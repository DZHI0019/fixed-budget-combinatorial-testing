"""Exact uniform-sampling comparison under the archived one-label-per-row classification."""
import argparse
from collections import Counter
import csv
from fractions import Fraction
import itertools
import json
import math
from pathlib import Path

p=argparse.ArgumentParser()
p.add_argument("csv",type=Path)
p.add_argument("plan",type=Path)
a=p.parse_args()
plan=json.loads(a.plan.read_text())
csv.field_size_limit(2**27)
with a.csv.open(encoding="utf8",newline="") as f:
    records={r["JHipsterRegister"]+"/"+r["Docker"]:(r["Build"],r["Bug"]) for r in csv.DictReader(f)}
hist=Counter(b for _,b in records.values() if b.startswith("BUG:"))
defects=sorted(hist)
N=len(records)
B=plan["budget"]
D=math.comb(N,B)
none=lambda ds:Fraction(math.comb(N-sum(hist[x] for x in ds),B),D)
expected=sum(1-none([x]) for x in hist)
all_six=sum((-1)**i*none(z) for i in range(len(defects)+1) for z in itertools.combinations(defects,i))
labels=Counter(records[k][1] for k in plan["sample"])
print("Historical population by defect",dict(hist))
print("Frozen plan Build counts:",dict(Counter(records[k][0] for k in plan["sample"])))
print("Frozen plan Bug counts:",dict(labels))
print("Uniform twelve configurations without replacement:", "expected defects",float(expected),
      "probability of hitting all six",float(all_six))
