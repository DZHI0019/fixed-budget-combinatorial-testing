"""Join frozen feature-only plans to published failure reports, using project-specific complete feature vectors."""
import csv
import hashlib
import json
import math
import re
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

from read_source import HERE


FROZEN_LF = "7078551c818e0ce90d43b6b8d616874bfa27e560dad92a56fb78431c45154243"
PAPER_FO = {"ATM":80, "companies":6, "MinePump":24, "sudoku":4}
ASSIGNMENT = re.compile(r"([a-z_0-9]+):(true|false)", re.IGNORECASE)


def labels(project, raw, data_dir):
    canonical = {frozenset(f.casefold() for f in fields): key for key,fields in raw.items()}
    field_names = frozenset.union(*canonical)
    by_config = defaultdict(set)
    lines = unknown = 0
    f = next(p for p in (data_dir/"labels").glob("*.csv") if p.stem.casefold() == project.casefold())
    with f.open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            source = row["configuration"]
            pairs = ASSIGNMENT.findall(source)
            if ASSIGNMENT.sub("",source).strip():
                raise ValueError((project,source))
            mapping = {k.casefold(): v.casefold()=="true" for k,v in pairs}
            if not mapping or field_names != mapping.keys() or len(pairs)!=len(mapping):
                raise ValueError((project,source,field_names))
            feat = frozenset(k for k,v in mapping.items() if v)
            lines += 1
            if feat not in canonical:
                unknown += 1
                continue
            by_config[canonical[feat]].add(row["description"].strip())
    return by_config, lines, unknown


def any_prob(population, successes, sample=12):
    return 1 - Fraction(math.comb(population-successes,sample), math.comb(population,sample))


def evaluate(data_dir=HERE):
    frozen = (data_dir/"frozen.json").read_bytes()
    if hashlib.sha256(frozen.replace(b"\r\n", b"\n")).hexdigest() != FROZEN_LF:
        raise ValueError("selection lock differs")
    data = json.loads(frozen)
    settings = json.loads((data_dir/"settings.json").read_text())
    result = {}
    for project, p in data["frozen"].items():
        by_config,lines,unknown = labels(project,settings[project],data_dir)
        def outcome(plan):
            keys = set(plan["ids"]) & by_config.keys()
            return dict(historical_failure_report_configs=len(keys),historical_test_signatures=
                        sorted({t for k in keys for t in by_config[k]}),matched_ids=sorted(keys))
        count = len(by_config)
        result[project] = dict(population=p["n"],report_rows=lines,paper_report_count=PAPER_FO[project],
            report_rows_outside_population=unknown,distinct_reported_failing_configs=count,
            all_test_signatures=sorted({t for ts in by_config.values() for t in ts}),
            pairs=p["feasible_pairs"],selected_pairs=p["plan"]["covered"],greedy_pairs=p["greedy"]["covered"],
            random_expected_pairs=p["uniform_expected_pairs"],
            chosen=outcome(p["plan"]),greedy=outcome(p["greedy"]),
            optimizer_seeds={r["seed"]:outcome(r["plan"]) for r in p["runs"]},
            random_expected_reported_configurations=float(Fraction(12*count,p["n"])),
            random_probability_at_least_one_report=float(any_prob(p["n"],count)))
    return result


if __name__ == "__main__":
    results = evaluate()
    (HERE/"results.json").write_text(json.dumps(results,indent=2,sort_keys=True)+"\n",encoding="utf-8")
