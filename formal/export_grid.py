"""Extract column supports from the complete released test matrix; check every cell in transit."""
import argparse
from pathlib import Path
from verify_grid import read_blocks


def item(rows):
    columns = []
    for col in range(103):
        masks = [0]*6
        for i, row in enumerate(rows):
            masks[row[col]] |= 1 << i
        columns.append("#[" + ",".join(hex(x) for x in masks) + "]")
    return "#[" + ",\n".join(columns) + "]"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("matrix", type=Path)
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("GridData.lean"))
    args = parser.parse_args()
    seed, correction = read_blocks(args.matrix)
    assert [r[0] for r in seed[:6]] == list(range(6))
    text = "import Grid\nnamespace SixGrid\n"
    for name, block in [("seedTable",seed),("repairTable",correction)]:
        text += f"def {name} : Array (Array Nat) := " + item(block) + "\n"
    args.output.write_text(text+"end SixGrid\n", encoding="utf-8", newline="\n")
