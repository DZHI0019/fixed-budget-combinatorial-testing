"""Rank a fixed pool of test plans using configuration values only."""
import argparse
import csv
import hashlib
import itertools
import json
from pathlib import Path


def scores(settings, plans):
    pairs = tuple(itertools.combinations(range(len(next(iter(settings.values())))), 2))
    triples = tuple(itertools.combinations(range(len(next(iter(settings.values())))), 3))
    ranked = []
    for seed, ids in plans:
        rows = [settings[key] for key in ids]
        if len(set(ids)) != 12:
            raise ValueError("Expected twelve distinct configurations")
        pair_score = sum(len({(r[i],r[j]) for r in rows}) for i,j in pairs)
        triple_score = sum(len({(r[i],r[j],r[k]) for r in rows}) for i,j,k in triples)
        ranked.append(dict(seed=seed, pairs=pair_score, triples=triple_score, ids=sorted(ids)))
    # Primary objective is unchanged, then all field triples carry equal weight.
    return sorted(ranked, key=lambda e: (-e["pairs"],-e["triples"],e["seed"]))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    for name in ("csv","spec","pool","settings","frozen","output"):
        ap.add_argument(name, type=Path)
    a=ap.parse_args()
    p=json.loads(a.spec.read_text(encoding="utf8"))
    if hashlib.sha256(a.csv.read_bytes()).hexdigest()!=p["sha256"]:
        raise ValueError("Incorrect JHipster data")
    csv.field_size_limit(2**27)
    with a.csv.open(encoding="utf8",newline="") as f:
        data={r["JHipsterRegister"]+"/"+r["Docker"]:tuple(r[k] for k in p["fields"]) for r in csv.DictReader(f)}
    pool=json.loads(a.pool.read_text(encoding="utf8"))
    rows=scores(data, [(x["seed"],x["ids"]) for x in pool])
    if {r["pairs"] for r in rows}!={642}:raise ValueError("Unexpected JHipster first objective")
    results={"JHipster":dict(original=17,winner=rows[0]["seed"],ranking=rows)}
    features=json.loads(a.settings.read_text(encoding="utf8"))
    frozen=json.loads(a.frozen.read_text(encoding="utf8"))["frozen"]
    for name, original in frozen.items():
        bits={k:tuple(f in choices for f in original["features"]) for k,choices in features[name].items()}
        rows=scores(bits,[(x["seed"],x["plan"]["ids"]) for x in original["runs"]])
        if rows[0]["pairs"]!=original["feasible_pairs"]:raise ValueError("Pairwise goal not reached")
        results[name]=dict(original=original["chosen_seed"],winner=rows[0]["seed"],ranking=rows)
    raw=(json.dumps(results,ensure_ascii=False,sort_keys=True,indent=2)+"\n").encode("utf8")
    a.output.write_bytes(raw)
    print("Frozen SHA256",hashlib.sha256(raw).hexdigest())
    for k,v in results.items():print(k,[(x["seed"],x["pairs"],x["triples"]) for x in v["ranking"]])


if __name__=="__main__":main()
