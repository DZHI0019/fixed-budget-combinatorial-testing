"""Build the selected standalone modules with pinned Lean and a prebuilt mathlib checkout."""
import argparse
import os
from pathlib import Path
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lean-bin", required=True, type=Path)
    parser.add_argument("--mathlib", required=True, type=Path)
    parser.add_argument("modules", nargs="*", default=["Budget", "CensusData", "CensusResult"])
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    bin_dir = args.lean_bin.resolve()
    mathlib = args.mathlib.resolve()
    search = [root, mathlib/".lake/build/lib/lean", *(mathlib/".lake/packages").glob("*/.lake/build/lib/lean")]
    env = dict(os.environ, PATH=str(bin_dir) + os.pathsep + os.environ["PATH"],
               LEAN_PATH=os.pathsep.join(map(str, search)))
    lean = bin_dir / ("lean.exe" if os.name == "nt" else "lean")
    subprocess.run([str(lean), "--version"], check=True, env=env)
    for name in args.modules:
        print("Checking", name, flush=True)
        subprocess.run([str(lean), "-s", "65536", "-o", name+".olean", name+".lean"],
                       cwd=root, env=env, check=True)


if __name__ == "__main__":
    main()
