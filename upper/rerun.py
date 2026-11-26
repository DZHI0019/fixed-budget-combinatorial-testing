"""Rebuild and replay the complete upper bound directly from original data."""
import argparse
import concurrent.futures
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from prepare import prepare
from check_run import check


HERE = Path(__file__).resolve().parent
DEFAULT = "10,3,11,1,2,4,5,12,0,9,13"
HARDEST = "10,11,3,1,2,4,5,12,0,9,13"


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("csv", type=Path)
    cli.add_argument("bound", type=Path)
    cli.add_argument("output", type=Path, help="Write the new run log here")
    cli.add_argument("--csc", type=Path, help="Windows .NET Framework csc.exe (default: .NET 10 SDK)")
    cli.add_argument("--jobs", type=int, default=2)
    args = cli.parse_args()
    with tempfile.TemporaryDirectory(dir=args.output.resolve().parent) as folder:
        tmp = Path(folder)
        prepare(args.csv, args.bound, 643, tmp)
        if args.csc:
            exe = tmp / "Join.exe"
            subprocess.run([str(args.csc.resolve()), "/nologo", "/optimize+", "/out:"+str(exe),
                            str(HERE/"Join.cs")], check=True)
            run = [str(exe)]
        else:
            shutil.copyfile(HERE/"Join.cs", tmp/"Join.cs")
            (tmp/"Upper.csproj").write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup>'
                '<OutputType>Exe</OutputType><TargetFramework>net10.0</TargetFramework>'
                '</PropertyGroup></Project>', encoding="utf-8")
            subprocess.run(["dotnet","build","-c","Release",str(tmp/"Upper.csproj")],check=True)
            run = ["dotnet", str(tmp/"bin/Release/net10.0/Upper.dll")]
        top = tmp / "top.txt"
        reps = top.read_text().splitlines()
        if len(reps) != 29 or sum(s.startswith("648 ") for s in reps)!=1:
            raise ValueError("Unexpected representative census")
        def evaluate(pair):
            i, row = pair
            part = tmp / f"group{i}.txt"
            part.write_text(row+"\n", encoding="ascii")
            order = HARDEST if row.startswith("648 ") else DEFAULT
            out = subprocess.run([*run,"643",order,part.name],cwd=tmp,
                                 capture_output=True,text=True,check=True)
            if len(out.stdout.splitlines()) != 1:
                raise ValueError(out.stdout)
            return i, out.stdout.strip()
        ordered = sorted(enumerate(reps),key=lambda x: (-int(x[1].split()[0]),x[0]))
        with concurrent.futures.ThreadPoolExecutor(max_workers=max(1,args.jobs)) as pool:
            futures = [pool.submit(evaluate, pair) for pair in ordered]
            result = {}
            for future in concurrent.futures.as_completed(futures):
                i, line = future.result()
                result[i] = line
                print(f"checked {len(result)}/{len(reps)}",flush=True)
        args.output.write_text("".join(result[i]+"\n" for i in range(len(reps))),encoding="utf-8")
        check(top, args.output, 643)


if __name__=="__main__":
    main()
