"""Translate the frozen CSV and certificate to Lean, rejecting any lossy row encoding."""
import argparse
import csv
import hashlib
import json
from itertools import combinations
from pathlib import Path


SHA256 = "fb842702e78a9db71687822d7e4950729c28a7a0d17c3e67c8357d8f7da6157a"
FIELDS = ("Docker", "applicationType", "authenticationType", "hibernateCache",
          "clusteredHttpSession", "websocket", "databaseType", "devDatabaseType",
          "prodDatabaseType", "buildTool", "searchEngine", "enableSocialSignIn",
          "useSass", "enableTranslation")
PAIRS = tuple(combinations(range(len(FIELDS)), 2))
HERE = Path(__file__).resolve().parent


def require(test, message):
    if not test:
        raise ValueError(message)


def labels(values):
    return {(i, j, values[i], values[j]) for i, j in PAIRS}


def export(csv_path, plan_path, bound_path, output):
    with csv_path.open("rb") as f:
        require(hashlib.file_digest(f, "sha256").hexdigest() == SHA256, "Unknown CSV")
    csv.field_size_limit(2**27)
    with csv_path.open(newline="", encoding="utf-8") as f:
        data = [(r["JHipsterRegister"] + "/" + r["Docker"], tuple(r[k] for k in FIELDS))
                for r in csv.DictReader(f)]
    require(len(data) == len(dict(data)) == len({v for _,v in data}) == 26256, "Duplicate row")
    universe = set()
    for _, values in data:
        universe.update(labels(values))
    cert = json.loads(bound_path.read_text(encoding="utf-8"))
    rare = sorted({tuple(item) for item, weight in cert["weights"] if weight == cert["scale"]})
    ordinary = sorted(universe.difference(rare))
    require(len(rare) == len(cert["weights"]) == 365 and len(ordinary) == 396
            and len(universe) == 761, "Invalid partition")
    lookup = {v: i for i, v in enumerate(ordinary + rare)}
    encoded = {}
    for key, values in data:
        expected = {lookup[t] for t in labels(values)}
        positions = sorted(i-396 for i in expected if i >= 396)
        require(len(positions) <= 21, "Row has more than 21 special items")
        mask = sum(1 << i for i in expected if i < 396)
        slots = sum(s << (9*j) for j,s in enumerate(positions + [511]*(21-len(positions))))
        # Decode every single item independently. In particular, no truncation,
        # missing item, or added item can be concealed by the 21-slot representation.
        recovered = {j for j in range(396) if (mask >> j) & 1}
        for j in range(21):
            slot = (slots >> (9*j)) & 511
            if slot < 365:
                recovered.add(396 + slot)
        require(recovered == expected, "Round trip failed for " + key)
        encoded[key] = (mask, slots)
    plan = json.loads(plan_path.read_text(encoding="utf-8"))["sample"]
    require(len(plan) == len(set(plan)) == 12 and set(plan) <= encoded.keys(), "Invalid plan")
    score = len(set.union(*(labels(dict(data)[k]) for k in plan)))
    def lit(row):
        return f"(0x{row[0]:x},0x{row[1]:x})"
    # The first 12 are precisely the chosen row IDs. Every other row occurs once.
    others = [row for key,row in encoded.items() if key not in set(plan)]
    output.mkdir(parents=True, exist_ok=True)
    with (output / "CensusData.lean").open("w", encoding="utf-8", newline="\n") as out:
        out.write("import Budget\nnamespace TestBudget\n")
        out.write("def chosen : List Row := [" + ",\n".join(lit(encoded[k]) for k in plan) + "]\n")
        blocks = []
        for start in range(0, len(others), 96):
            name = "block" + str(start // 96)
            blocks.append(name)
            out.write(f"def {name} : Array Row := #[")
            out.write(",\n".join(lit(r) for r in others[start:start+96]) + "]\n")
        out.write("def otherRows : Array (Array Row) := #[" + ",".join(blocks) + "]\n")
        out.write("def inCensus (r : Row) : Prop := r ∈ chosen ∨ ∃ b ∈ otherRows, r ∈ b\n")
        out.write("end TestBudget\n")
    (output / "CensusResult.lean").write_text(f"""import CensusData
set_option maxRecDepth 1000000
set_option maxHeartbeats 0
namespace TestBudget
theorem chosen_score : score chosen = {score} := by decide +kernel
theorem certified_interval :
    (∃ s : Finset Row, s.card ≤ 12 ∧ (∀ r ∈ s, inCensus r) ∧ (covered s).card = {score}) ∧
    (∀ s : Finset Row, s.card ≤ 12 → (∀ r ∈ s, inCensus r) → (covered s).card ≤ 648) := by
  constructor
  · refine ⟨chosen.toFinset, ?_, ?_, (score_eq chosen).symm.trans chosen_score⟩
    · exact (List.toFinset_card_le chosen).trans (by decide)
    · intro r hr
      exact Or.inl (List.mem_toFinset.mp hr)
  · exact fun s hs _ => budget_upper s hs
end TestBudget
#print axioms TestBudget.certified_interval
""", encoding="utf-8", newline="\n")
    print(f"Lossless census: {len(data)} rows, {len(universe)} items, witness {score}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", type=Path)
    parser.add_argument("plan", type=Path)
    parser.add_argument("certificate", type=Path)
    parser.add_argument("--output", type=Path, default=HERE)
    args = parser.parse_args()
    export(args.csv, args.plan, args.certificate, args.output)
