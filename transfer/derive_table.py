"""Reconstruct the formal empirical-table certificate directly from frozen configuration IDs."""
from pathlib import Path
import argparse
import hashlib
import json

EXPECTED = "7078551c818e0ce90d43b6b8d616874bfa27e560dad92a56fb78431c45154243"
DATA = [("ATM",80,82,12,12),("MinePump",64,60,1,2),
        ("companies",192,140,1,2),("sudoku",20,54,3,2)]


def render(directory):
    labels = (directory/"frozen.json").read_text(encoding="utf-8").encode("utf-8")
    if hashlib.sha256(labels).hexdigest() != EXPECTED:
        raise ValueError("Unexpected frozen input")
    frozen = json.loads(labels)["frozen"]
    settings = json.loads((directory/"settings.json").read_text(encoding="utf-8"))
    lines = ["import Transfer", "namespace Transfer.Table", "set_option maxHeartbeats 0",
             "set_option maxRecDepth 100000",
             "def requests (s masks : List Nat) : Nat :=",
             "  ((masks.map fun m => ((s.map fun r => r &&& m).eraseDups).length)).sum"]
    for name,n,p,h1,h2 in DATA:
        record = frozen[name]
        for ref in ["plan","greedy"]:
            ids = record[ref]["ids"]
            masks = [sum(1 << i for i,f in enumerate(record["features"]) if f in settings[name][k])
                     for k in ids]
            lines.append(f"def {name}_{ref} : List Nat := {masks}")
        lines += [
            f"theorem {name}_table :",
            f"  {name}.rows.length = {n} ∧ requests {name}.rows {name}.pairs = {p} ∧",
            f"  legal12 {name}.rows {name}_plan = true ∧ legal12 {name}.rows {name}_greedy = true ∧",
            f"  full {name}.rows {name}_plan {name}.pairs = true ∧ full {name}.rows {name}_greedy {name}.pairs = true ∧",
            f"  hits {name}_plan {name}.reported = {h1} ∧ hits {name}_greedy {name}.reported = {h2} := by decide +kernel",
            f"#print axioms {name}_table"]
    def total(ref):
        return " + ".join(f"hits {n}_{ref} {n}.reported" for n,*_ in DATA)
    lines += [
        "theorem aggregate_detection :", f"  {total('plan')} = 17 ∧",
        f"  {total('greedy')} = 18 := by decide +kernel",
        "theorem threeway_assignment_count : requests MinePump.rows MinePump.triples = 160 := by decide +kernel",
        "#print axioms aggregate_detection", "#print axioms threeway_assignment_count",
        "end Transfer.Table"]
    return "\n".join(lines)+"\n"


if __name__=="__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("transfer",type=Path)
    cli.add_argument("output",type=Path)
    args = cli.parse_args()
    args.output.write_text(render(args.transfer),encoding="utf-8",newline="\n")
