"""Enumerate every composition, then independently verify the database orbit reduction."""
import argparse
import collections
import csv
import hashlib
import itertools
import json
import math
import sys
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("csv",type=Path)
ap.add_argument("spec",type=Path)
ap.add_argument("certificate",type=Path)
ap.add_argument("target",type=int)
ap.add_argument("representatives",type=Path)
ap.add_argument("--numpy-path")
arg=ap.parse_args()
if arg.numpy_path:
    sys.path.insert(0,arg.numpy_path)
import numpy as np

plan=json.loads(arg.spec.read_text())
if hashlib.sha256(arg.csv.read_bytes()).hexdigest()!=plan["sha256"]:
    raise ValueError("Incorrect raw data")
csv.field_size_limit(2**27)
with arg.csv.open(encoding="utf8",newline="") as f:
    data=[tuple(r[c] for c in plan["fields"]) for r in csv.DictReader(f)]
K=(6,7,8)
dbs=sorted(set(r[6:9] for r in data))
marks={tuple(label) for label,w in json.loads(arg.certificate.read_text())["weights"]}
cells={pair:{(r[pair[0]],r[pair[1]]) for r in data} for pair in itertools.combinations(range(14),2)}
rowmax={db:0 for db in dbs}
for r in data:
    n=sum((i,j,r[i],r[j]) in marks for i,j in cells)
    rowmax[r[6:9]]=max(rowmax[r[6:9]],n)
assert len(marks)==365 and sum(map(len,cells.values()))==761 and max(rowmax.values())==21

# Create identity tests per slice before summing equal slices. Each composition
# is evaluated without branch pruning. The reduction below holds for all
# histograms, including those rejected by the reference recursion.
terms=collections.defaultdict(lambda:np.zeros(13,np.int16))
counts=np.arange(13,dtype=np.int16)
for (i,j), observed in cells.items():
    if i in K and j in K:
        for a,b in observed:
            sets=tuple(z for z,db in enumerate(dbs) if (db[i-6],db[j-6])==(a,b))
            terms[sets]+=np.maximum(0,counts-1) if (i,j,a,b) in marks else counts==0
    elif i in K or j in K:
        pos,k=(0,i) if i in K else (1,j)
        for x in {p[pos] for p in observed}:
            group={v for v in observed if v[pos]==x}
            special=sum((i,j,*p) in marks for p in group)
            sets=tuple(z for z,db in enumerate(dbs) if db[k-6]==x)
            if special==len(group): terms[sets]+=np.maximum(0,counts-special)
            if special==0: terms[sets]+=np.maximum(0,len(group)-counts)
for i,v in enumerate(dbs):
    terms[i,]+=(21-rowmax[v])*counts
survive={}
tested=0
it=itertools.combinations_with_replacement(range(12),12)
while True:
    raw=list(itertools.islice(it,16384))
    if not raw:break
    raw=np.asarray(raw,dtype=np.int8)
    # columns are identical class labels; raw repeats give the unique multisets.
    h=np.stack([(raw==k).sum(axis=1,dtype=np.int8) for k in range(12)],axis=1)
    budget=np.full(len(raw),648,dtype=np.int16)
    for g,t in terms.items():
        if np.any(t):
            budget-=t[h[:,g].sum(axis=1,dtype=np.int16)]
    for i in np.flatnonzero(budget>=arg.target):
        survive[tuple(map(int,h[i]))]=int(budget[i])
    tested+=len(raw)
assert tested==math.comb(23,11)
data_set=set(data)
alphabet=("mariadb","mysql","postgresql")
syms=[]
for perm in itertools.permutations(alphabet):
    for flip in range(2):
        mapping=dict(zip(alphabet,perm))
        if flip:mapping.update({"InMemory":"DiskBased","DiskBased":"InMemory"})
        def image(r):
            v=list(r)
            for i in (7,8): v[i]=mapping.get(v[i],v[i])
            return tuple(v)
        if {image(r) for r in data_set}!=data_set:continue
        syms.append([dbs.index((c,mapping.get(d,d),mapping.get(p,p))) for c,d,p in dbs])
def orbit(h):
    # Send the multiplicity at position j to position permutation[j].
    reps=[]
    for s in syms:
        v=[0]*12
        for j,x in enumerate(h):v[s[j]]=x
        reps.append(tuple(v))
    return min(reps)
all_orbits={orbit(h) for h in survive}
published={}
for line in arg.representatives.read_text().splitlines():
    b,*h=map(int,line.split())
    if b<arg.target:continue
    h=tuple(h)
    if h not in survive or survive[h]!=b:raise ValueError("Incorrect representative bound")
    published[orbit(h)]=h
if published.keys()!=all_orbits:raise ValueError("Missing or extra orbit")
print(f"PASS: {tested:,} raw histograms; {len(survive)} survivors at {arg.target}; "
      f"{len(syms)} feasible-data symmetries; {len(all_orbits)} represented orbits")
