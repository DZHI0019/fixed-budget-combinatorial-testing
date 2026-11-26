"""Check that a saved integer-search run excludes the threshold on all representatives."""
import argparse
import re
from pathlib import Path


def check(top, log, target):
    expected = {}
    for line in top.read_text(encoding="utf8").splitlines():
        values = tuple(map(int, line.split()))
        if values[0] >= target:
            if len(values) != 13 or sum(values[1:]) != 12 or values in expected:
                raise ValueError("Malformed surviving histogram")
            expected[values] = None
    seen = set()
    total = 0
    for line in log.read_text(encoding="utf-8-sig").splitlines():
        match = re.fullmatch(r"([0-9 ]+) => (False|True) nodes ([0-9]+)", line)
        if match is None:
            raise ValueError(f"Malformed output line: {line}")
        key = tuple(map(int, match[1].split()))
        if key not in expected or key in seen or match[2] != "False":
            raise ValueError(f"Missing exclusion or repeated histogram: {line}")
        seen.add(key)
        total += int(match[3])
    if seen != expected.keys():
        raise ValueError(f"Incomplete search, {len(seen)}/{len(expected)} representatives")
    print(f"PASS: all {len(seen)} representatives exclude {target}, "
          f"{total:,} complete column prefixes visited. Upper bound {target-1}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("top", type=Path)
    parser.add_argument("log", type=Path)
    parser.add_argument("target", type=int)
    args = parser.parse_args()
    check(args.top, args.log, args.target)
