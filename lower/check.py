"""Read the original dataset independently; score a list of twelve row indices."""
import argparse
import csv
import hashlib
import itertools
import json
from pathlib import Path

fields = "Docker applicationType authenticationType hibernateCache clusteredHttpSession websocket databaseType devDatabaseType prodDatabaseType buildTool searchEngine enableSocialSignIn useSass enableTranslation".split()
ap = argparse.ArgumentParser()
ap.add_argument("data", type=Path)
ap.add_argument("indices", type=Path)
ap.add_argument("output", type=Path)
a = ap.parse_args()
score, *indices = map(int, a.indices.read_text().split())
if len(indices) != 12 or len(set(indices)) != 12:
    raise ValueError("Expected 12 different indices")
csv.field_size_limit(2**27)
selected = {}
with a.data.open(encoding="utf-8", newline="") as f:
    for i,r in enumerate(csv.DictReader(f)):
        if i in indices:
            selected[i]=r
sample = [selected[i] for i in indices]
coverage = {(u,r[u],v,r[v]) for r in sample for u,v in itertools.combinations(fields,2)}
if len(coverage) != score:
    raise ValueError("Incorrect score")
out = {"sample":[r["JHipsterRegister"]+"/"+r["Docker"] for r in sample],
       "covered":score, "budget":12, "fields":fields, "feasible":761,
       "sha256":hashlib.sha256(a.data.read_bytes()).hexdigest()}
a.output.write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
print("Verified",score,"covered interactions in 12 configurations")
