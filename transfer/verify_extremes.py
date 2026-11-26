"""Validate the finite endpoint certificates using plain Python, without the search or optimizer."""
import argparse
import csv
import hashlib
import itertools
import json
from pathlib import Path


HERE=Path(__file__).resolve().parent
EXPECTED={"ATM":(11,12), "MinePump":(0,8),"companies":(0,6),"sudoku":(1,4)}
LOCK="7078551c818e0ce90d43b6b8d616874bfa27e560dad92a56fb78431c45154243"
SIX=[
    ("CUT_NO_MANAGER","TOTAL_WALKER",1,1), ("CUT_NO_MANAGER","TOTAL_REDUCER",1,1),
    ("CUT_NO_DEPARTMENT","TOTAL_REDUCER",1,1), ("CUT_NO_DEPARTMENT","TOTAL_WALKER",1,1),
    ("CUT_WHATEVER","TOTAL_REDUCER",1,1), ("TOTAL_REDUCER","TOTAL_WALKER",0,0)]


def check(ok,message):
    if not ok:
        raise ValueError(message)


def read_json(name):
    return json.loads((HERE/name).read_bytes())


def parse_reports(path, options):
    # Independent reader: consume one complete named setting at a time.
    schema=sorted(set.union(*(set(x.lower() for x in v) for v in options.values())),
                  key=len,reverse=True)
    ids={frozenset(x.lower() for x in v):k for k,v in options.items()}
    out={}
    with path.open(encoding="utf-8-sig",newline="") as stream:
        for row in csv.DictReader(stream):
            remaining=row["configuration"].replace(" ","").lower()
            states={}
            while remaining:
                matches=[n for n in schema if remaining.startswith(n+":")]
                check(len(matches)==1,"unknown feature in label")
                name,=matches
                check(name not in states,"duplicate feature in label")
                rest=remaining[len(name)+1:]
                val=next(x for x in ["true","false"] if rest.startswith(x))
                states[name]=val=="true"
                remaining=rest[len(val):]
            check(set(states)==set(schema),"incomplete feature vector")
            key=ids[frozenset(n for n,v in states.items() if v)]
            out.setdefault(key,set()).add(row["description"].strip())
    return out


def run():
    raw=read_json("settings.json")
    witnesses=read_json("extreme-plans.json")
    lock=(HERE/"frozen.json").read_bytes().replace(b"\r\n",b"\n")
    check(hashlib.sha256(lock).hexdigest()==LOCK,"unexpected frozen selection")
    frozen=json.loads(lock)["frozen"]
    results=read_json("results.json")
    numeric={}
    for project,p in frozen.items():
        source=raw[project]
        cov={}
        options=[f for f in sorted(set.union(*(set(x) for x in source.values())))
                 if not all(f in v for v in source.values())]
        for k,v in source.items():
            cov[k]={(a,b,int(a in v),int(b in v)) for a,b in itertools.combinations(options,2)}
        universe=set.union(*cov.values())
        path=next(x for x in (HERE/"labels").glob("*.csv") if x.stem.lower()==project.lower())
        reported=set(parse_reports(path,source))
        encode=lambda k:sum(1<<i for i,f in enumerate(options) if f in source[k])
        ex=witnesses[project]
        numeric[project]={"rows":sorted(encode(k) for k in source),
                          "reported":sorted(encode(k) for k in reported),
                          "features":options,
                          "minRows":[encode(k) for k in ex["min"]["ids"]],
                          "maxRows":[encode(k) for k in ex["max"]["ids"]]}
        test=[(ex[tag],n) for tag,n in zip(["min","max"],EXPECTED[project])]
        test.append((p["plan"],results[project]["chosen"]["historical_failure_report_configs"]))
        test.append((p["greedy"],results[project]["greedy"]["historical_failure_report_configs"]))
        for plan,n in test:
            ids=set(plan["ids"])
            check(len(ids)==len(plan["ids"])==12 and ids<=set(source),"invalid plan")
            check(set.union(*(cov[k] for k in ids))==universe,"incomplete pair coverage")
            check(len(ids & reported)==n,"wrong failure count")
        n=len(reported)
        if project=="ATM":
            check(len(source)-n==1,"ATM lower limit")
        elif project=="MinePump":
            check(n==8,"MinePump upper limit")
            triple=read_json("minepump-threeway.json")
            numeric[project]["tripleRows"]=[encode(k) for k in triple["ids"]]
            check(len(set(triple["ids"]))==12,"invalid three-way plan")
            for a,b,c in itertools.combinations(options,3):
                observed={tuple(int(f in source[k]) for f in (a,b,c)) for k in triple["ids"]}
                check(len(observed)==8,"missing triple setting")
            key={"highWaterSensor":True,"lowWaterSensor":False,"methaneAlarm":False}
            check(reported=={k for k,v in source.items() if all((f in v)==x for f,x in key.items())},
                  "three-way failure block differs")
        elif project=="companies":
            s=[{k for k,its in cov.items() if demand in its} for demand in SIX]
            check(all(s) and all(not group & reported for group in s),"unsafe pass support")
            check(all(not a&b for a,b in itertools.combinations(s,2)),"packing supports intersect")
        elif project=="sudoku":
            target=("EXTENDEDSUDOKU","GENERATOR",1,1)
            support={k for k,its in cov.items() if target in its}
            check(support and support<=reported and n==4,"Sudoku endpoints")
        print(f'{project}: {len(universe)} feasible pairs, exact failure-count endpoints {EXPECTED[project]}')
    return numeric


if __name__=="__main__":
    run()
