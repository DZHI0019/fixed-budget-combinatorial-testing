"""Find a label-free three-way coverage plan for the MinePump configuration population."""
from itertools import combinations
import json
from freeze import HERE, sample, union


def main():
    project = "MinePump"
    f = json.loads((HERE/"frozen.json").read_text())["frozen"][project]
    raw = json.loads((HERE/"settings.json").read_text())[project]
    ids = sorted(raw)
    triples = list(combinations(f["features"],3))
    masks = []
    for key in ids:
        z = raw[key]
        masks.append(sum(1 << (8*i + 4*(a in z)+2*(b in z)+(c in z))
                         for i,(a,b,c) in enumerate(triples)))
    target = union(masks,range(len(ids))).bit_count()
    for seed in range(261126,261200):
        chosen,_ = sample(masks,seed,target)
        if union(masks,chosen).bit_count() == target:
            out = {"project":project,"seed":seed,"ids":sorted(ids[i] for i in chosen),
                   "covered_triples":target,"features":f["features"]}
            print(out)
            (HERE/"minepump-threeway.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
            return
    raise RuntimeError("full coverage not found")


if __name__ == "__main__":
    main()
