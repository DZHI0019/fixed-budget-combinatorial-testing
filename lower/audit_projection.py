"""Check the upper-bound executable against exact finite oracle cases by restriction."""
import argparse
import collections
import csv
import itertools
import json
import random
import shutil
import subprocess
import tempfile
from pathlib import Path

ap=argparse.ArgumentParser()
ap.add_argument("data",type=Path)
ap.add_argument("plan",type=Path)
ap.add_argument("marks",type=Path)
ap.add_argument("instance",type=Path)
ap.add_argument("executable",type=Path)
a=ap.parse_args()
solver=a.executable.resolve()
plan=json.loads(a.plan.read_text())
marks={tuple(x) for x,w in json.loads(a.marks.read_text())["weights"]}
fields=plan["fields"]
pairs=tuple(itertools.combinations(range(14),2))
csv.field_size_limit(2**27)
with a.data.open(encoding="utf8",newline="") as f:
    rows=[tuple(r[k] for k in fields) for r in csv.DictReader(f)]
vals=[sorted({r[i] for r in rows}) for i in range(14)]
universe={(i,j,r[i],r[j]) for r in rows for i,j in pairs}
bydb=collections.defaultdict(list)
for r in rows:bydb[r[6:9]].append(r)
dbtypes=sorted(bydb)
rng=random.Random(40139)
tested=0
with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as temp:
    d=Path(temp)
    shutil.copyfile(a.instance,d/"instance.dat")
    # Every test case supplies its only histogram. No preprocessing cutoff applies.
    (d/"threshold.txt").write_text("-1000\n")
    for exp in range(36):
        pick=[rng.choice(bydb[v]) for v in dbtypes]
        nums=[[vals[i].index(r[i]) for i in range(14)] for r in pick]
        costs=[21-sum((i,j,r[i],r[j]) in marks for i,j in pairs) for r in pick]
        # Exactly one valid row per class. Thus the class histogram forces a
        # single multiset of rows, making the relaxed projection test exact.
        (d/"types.dat").write_text("".join(" ".join(map(str,(g,costs[g],*nums[g])))+"\n" for g in range(12)))
        hist=collections.Counter(rng.choices(range(12),k=12)) if exp%2 else dict.fromkeys(range(12),1)
        mult=[hist.get(g,0) for g in range(12)]
        actual=[r for g,r in enumerate(pick) for _ in range(mult[g])]
        line=" ".join(map(str,[648,*mult]))
        (d/"top.txt").write_text(line+"\n")
        if exp%3==0:order=[10,3,11,1,2,4,5,12]
        elif exp%3==1:order=[10,3,11,1,2,4,5,12,0,9,13]
        else:order=rng.sample([0,1,2,3,4,5,9,10,11,12,13],rng.randint(2,5))
        kept={6,7,8,*order}
        sub={k for k in universe if k[0] in kept and k[1] in kept}
        hits=collections.Counter((i,j,r[i],r[j]) for r in actual for i,j in pairs if i in kept and j in kept)
        loss=sum(n*c for n,c in zip(mult,costs))+sum(not hits[k] for k in sub-marks)+sum(max(0,hits[k]-1) for k in sub&marks)
        exact=648-loss
        for threshold,answer in [(exact,"True"),(exact+1,"False")]:
            proc=subprocess.run([str(solver),str(threshold),",".join(map(str,order))],
                                cwd=d,text=True,check=True,capture_output=True,timeout=30)
            if ("=> "+answer+" nodes ") not in proc.stdout:raise ValueError((exp,exact,proc.stdout))
            tested+=1
print(f"PASS: {tested} projected-threshold answers on 36 independent exact restricted instances; both sides of every threshold checked.")
