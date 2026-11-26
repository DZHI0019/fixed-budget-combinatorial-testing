"""Join archived outcomes only after validating the selection lock."""
import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

LOCK="af204b06492ac22e2a2839814fe80741f2c0f7a0f4418503834a81db435fc98d"
p=argparse.ArgumentParser(description=__doc__)
for name in ("locked","csv","transfer","output"):p.add_argument(name,type=Path)
a=p.parse_args()
raw=a.locked.read_bytes()
if hashlib.sha256(raw).hexdigest()!=LOCK:raise ValueError("The lock changed")
rankings=json.loads(raw)
csv.field_size_limit(2**27)
with a.csv.open(encoding="utf8",newline="") as f:
    archival={r["JHipsterRegister"]+"/"+r["Docker"]:(r["Build"],r["Bug"]) for r in csv.DictReader(f)}
sys.path.insert(0,str(a.transfer.resolve()))
from score import labels
data=json.loads((a.transfer/"settings.json").read_text(encoding="utf8"))
answer={}
for project,case in rankings.items():
    outcomes={}
    if project!="JHipster":
        reports,_,_=labels(project,data[project],a.transfer)
    for row in case["ranking"]:
        if project=="JHipster":
            records=[archival[k] for k in row["ids"]]
            descriptions=sorted({bug for _,bug in records if bug.startswith("BUG:")})
            reported=sum(build=="KO" for build,_ in records)
        else:
            descriptions=sorted({s for k in row["ids"] for s in reports.get(k,())})
            reported=sum(bool(reports.get(k)) for k in row["ids"])
        outcomes[row["seed"]]=dict(reported_configurations=reported,archived_signatures=descriptions,
                                   signature_count=len(descriptions),triples=row["triples"],pairs=row["pairs"])
    before=outcomes[case["original"]]; after=outcomes[case["winner"]]
    answer[project]=dict(original=before,tiebreak=after,all_candidates=outcomes)
    print(project,"reported configurations",before["reported_configurations"],"->",after["reported_configurations"],
          "signatures",before["signature_count"],"->",after["signature_count"])
a.output.write_bytes((json.dumps(answer,indent=2,sort_keys=True)+"\n").encode("utf8"))
