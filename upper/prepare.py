"""Build a complete list of remaining database histograms and finite projection inputs."""
import argparse
import collections
import csv
import hashlib
import itertools
import json
from pathlib import Path

FIELDS = ("Docker", "applicationType", "authenticationType", "hibernateCache",
          "clusteredHttpSession", "websocket", "databaseType", "devDatabaseType",
          "prodDatabaseType", "buildTool", "searchEngine", "enableSocialSignIn",
          "useSass", "enableTranslation")
DB = (6, 7, 8)
PAIRS = tuple(itertools.combinations(range(14), 2))
EXPECTED = "fb842702e78a9db71687822d7e4950729c28a7a0d17c3e67c8357d8f7da6157a"


def prepare(csv_path, weights_path, target, output):
    csv.field_size_limit(2**27)
    with csv_path.open("rb") as f:
        if hashlib.file_digest(f, "sha256").hexdigest() != EXPECTED:
            raise ValueError("Unrecognized original data")
    with csv_path.open(encoding="utf8", newline="") as f:
        rows = [tuple(r[c] for c in FIELDS) for r in csv.DictReader(f)]
    values = [sorted({r[i] for r in rows}) for i in range(14)]
    numbered = [tuple(values[i].index(v) for i, v in enumerate(r)) for r in rows]
    universe = {(i,j,r[i],r[j]) for r in numbered for i,j in PAIRS}
    cert = json.loads(weights_path.read_text(encoding="utf8"))
    marks = {(i,j,values[i].index(a),values[j].index(b))
             for (i,j,a,b),w in cert["weights"] if w == cert["scale"]}
    if len(universe)!=761 or len(marks)!=365 or not marks<=universe:
        raise ValueError("Invalid mark set")
    classes = sorted({r[6:9] for r in numbered})
    domains = [[set() for _ in FIELDS] for _ in classes]
    row_max = [0] * len(classes)
    output.mkdir(parents=True, exist_ok=True)
    with (output/"types.dat").open("w") as f:
        for r in numbered:
            g = classes.index(r[6:9])
            weight = sum((i,j,r[i],r[j]) in marks for i,j in PAIRS)
            for i,v in enumerate(r):
                domains[g][i].add(v)
            row_max[g] = max(row_max[g], weight)
            print(g, 21-weight, *r, file=f)
    if max(row_max)!=21:
        raise ValueError("Invalid row maximum")
    with (output/"instance.dat").open("w") as f:
        for alphabet in values:
            print(len(alphabet), file=f)
        for d in domains:
            for s in d:
                print(sum(1<<v for v in s), file=f)
        for i,j in PAIRS:
            for a,b in itertools.product(range(len(values[i])),range(len(values[j]))):
                label = (i,j,a,b)
                print(2 if label in marks else int(label in universe), file=f)
    # A group of database classes determines how many of the 12 rows enter a slice.
    # For each group, tabulate a lower bound on the deficit for each possible count.
    penalty = collections.defaultdict(lambda: [0]*13)
    for g,maximum in enumerate(row_max):
        penalty[(g,)] = [(21-maximum)*m for m in range(13)]
    for i,j in PAIRS:
        pairs = [(a,b) for ii,jj,a,b in universe if (ii,jj)==(i,j)]
        if i in DB and j in DB:
            for a,b in pairs:
                group=tuple(g for g,r in enumerate(classes) if r[i-6]==a and r[j-6]==b)
                for m in range(13):
                    penalty[group][m] += (max(0,m-1) if (i,j,a,b) in marks else int(m==0))
        elif (i in DB) != (j in DB):
            k = i if i in DB else j
            for value in range(len(values[k])):
                labels = [(i,j,a,b) for a,b in pairs if (a if i==k else b)==value]
                group = tuple(g for g,r in enumerate(classes) if r[k-6]==value)
                marked = sum(label in marks for label in labels)
                for m in range(13):
                    if marked==0: penalty[group][m] += max(0,len(labels)-m)
                    if marked==len(labels): penalty[group][m] += max(0,m-marked)
    due = [[] for _ in classes]
    for group,t in penalty.items():
        if any(t): due[max(group)].append((group,t))
    survive = []
    def traverse(h, left, loss):
        i = len(h)
        for c in (range(left+1) if i<11 else (left,)):
            hh=h+(c,)
            deficit=loss+sum(t[sum(hh[k] for k in g)] for g,t in due[i])
            if 648-deficit<target: continue
            if i==11: survive.append((648-deficit,hh))
            else: traverse(hh,left-c,deficit)
    traverse((),12,0)
    # Three SQL product names and two development-mode names can be permuted.
    # Check EVERY raw tuple, so that equivalence does not assume a model symmetry.
    moves = []
    data_set=set(rows)
    names=["mariadb","mysql","postgresql"]
    class_names = sorted({r[6:9] for r in rows})
    for perm,flip in itertools.product(itertools.permutations(names),(False,True)):
        mp=dict(zip(names,perm))
        if flip:mp.update({"DiskBased":"InMemory","InMemory":"DiskBased"})
        def transform(r):
            return r[:7]+(mp.get(r[7],r[7]),mp.get(r[8],r[8]))+r[9:]
        if all(transform(r) in data_set for r in rows):
            moves.append([class_names.index((a,mp.get(b,b),mp.get(c,c))) for a,b,c in class_names])
    # Choose a surviving representative in each orbit with the strongest initial upper bound.
    groups = {}
    for ub,h in survive:
        key=min(tuple(h[k] for k in move) for move in moves)
        groups[key]=min(groups.get(key,(ub,h)),(ub,h))
    with (output/"top.txt").open("w") as f:
        for ub,h in sorted(groups.values()): print(ub,*h,file=f)
    (output/"threshold.txt").write_text(str(target)+"\n",encoding="ascii")
    print(f"Database histograms allowing {target}: {len(survive)}; representatives: {len(groups)}.")

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("csv",type=Path)
    p.add_argument("weights",type=Path)
    p.add_argument("target",type=int)
    p.add_argument("output",type=Path)
    a=p.parse_args()
    prepare(a.csv,a.weights,a.target,a.output)
