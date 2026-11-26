"""Create compact local inputs from the published challenge archive without executing its contents."""
import argparse
import hashlib
import json
import re
import tarfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
PIN = "eb6d88977219f1b090ab340b45b6bb3f10d30ce1"
SOURCE = f"https://codeload.github.com/fischerJF/challenge/tar.gz/{PIN}"
CENSUS = {"ATM": 80, "BankAccount": 144, "Chess": 7, "companies": 192, "GPL": 73,
          "MinePump": 64, "Paycard": 6, "sudoku": 20}
CONFIG = re.compile(r"workspace_IncLing/Tools/All_valid_conf/([^/]+)/products/(\d+)/(\d+)\.config")


def unpack(path, output):
    configurations = {project: {} for project in CENSUS}
    hashes = {}
    with tarfile.open(path, "r|gz") as archive:
        for member in archive:
            if not member.isfile():
                continue
            root, _, rel = member.name.partition("/")
            if not root.endswith(PIN):
                raise ValueError("unexpected archive revision")
            match = CONFIG.fullmatch(rel)
            if match and match.group(1) in CENSUS:
                project, index, repeated = match.groups()
                if index != repeated or index in configurations[project]:
                    raise ValueError(rel)
                raw = archive.extractfile(member).read()
                features = sorted(x.strip() for x in raw.decode("utf-8-sig").splitlines() if x.strip())
                if len(features) != len(set(features)):
                    raise ValueError(rel)
                configurations[project][index] = features
            elif rel.startswith("failuresFound/") and rel.lower().endswith(".csv"):
                name = rel.rsplit("/", 1)[1]
                if name[:-4].casefold() not in {x.casefold() for x in CENSUS}:
                    continue
                raw = archive.extractfile(member).read()
                (output/"labels").mkdir(exist_ok=True)
                (output/"labels"/name).write_bytes(raw)
            else:
                continue
            hashes[rel] = hashlib.sha256(raw).hexdigest()
    for name, obj in [("settings.json", configurations), ("source-files.json", hashes)]:
        (output / name).write_text(json.dumps(obj, sort_keys=True, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path, help=SOURCE)
    parser.add_argument("--output", type=Path, default=HERE)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    unpack(args.archive, args.output)
