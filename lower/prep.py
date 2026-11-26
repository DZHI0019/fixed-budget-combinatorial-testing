"""Translate categorical configurations and their pair masks into the searcher's input."""
import argparse
import csv
import hashlib
import itertools
import json
from pathlib import Path
import struct

ap = argparse.ArgumentParser()
ap.add_argument("data", type=Path)
ap.add_argument("plan", type=Path)
ap.add_argument("output", type=Path)
args = ap.parse_args()
plan = json.loads(args.plan.read_text(encoding="utf-8"))
assert hashlib.sha256(args.data.read_bytes()).hexdigest() == plan["sha256"]
csv.field_size_limit(2**27)
with args.data.open(encoding="utf-8", newline="") as stream:
    rows = [(r["JHipsterRegister"]+"/"+r["Docker"], tuple(r[k] for k in plan["fields"]))
            for r in csv.DictReader(stream)]
n = len(plan["fields"])
values = [sorted({r[i] for _,r in rows}) for i in range(n)]
digits = [{value:i for i,value in enumerate(v)} for v in values]
encoded = [(key, tuple(d[v] for d,v in zip(digits,r))) for key,r in rows]
pairs = list(itertools.combinations(range(n),2))
items = sorted({(i,j,r[i],r[j]) for key,r in encoded for i,j in pairs})
codes = {v:j for j,v in enumerate(items)}
assert len(items)==761 and max(map(len,values))<=16 and n==14
names = [key for key,r in encoded]
with args.output.open("wb") as out:
    out.write(struct.pack("<I",len(rows)))
    for key,r in encoded:
        out.write(struct.pack("<Q",sum(x<<(4*i) for i,x in enumerate(r))))
        bits = sum(1<<codes[i,j,r[i],r[j]] for i,j in pairs)
        out.write(bits.to_bytes(96,"little"))
    for s in plan["sample"]:
        out.write(struct.pack("<i",names.index(s)))
args.output.with_suffix(".ids").write_text("\n".join(names),encoding="utf-8")
