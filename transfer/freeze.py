"""Choose twelve configurations using features alone. No label reader is imported."""
import itertools
import json
import math
import operator
import random
from functools import reduce
from pathlib import Path

from read_source import CENSUS, HERE


BUDGET = 12
SEEDS = [261126, 261127, 261128]


def union(masks, indices):
    return reduce(operator.or_, (masks[i] for i in indices), 0)


def sample(masks, seed, reachable):
    rng = random.Random(seed)
    best, best_score = [], 0
    greedy = []
    def pick(partial):
        covered = union(masks, partial)
        unavailable = set(partial)
        scores = [(mask & ~covered).bit_count() if i not in unavailable else -1
                  for i, mask in enumerate(masks)]
        top = max(scores)
        return rng.choice([i for i, score in enumerate(scores) if score == top])
    for restart in range(100):
        plan = [] if restart % 5 == 0 else rng.sample(best, rng.randint(6,9))
        while len(plan) < BUDGET:
            plan.append(pick(plan))
        if not greedy:
            greedy = plan.copy()
        for _ in range(5):
            before = union(masks,plan).bit_count()
            order = list(range(BUDGET))
            rng.shuffle(order)
            for slot in order:
                plan[slot] = pick(plan[:slot]+plan[slot+1:])
            score = union(masks,plan).bit_count()
            if score > best_score:
                best, best_score = plan.copy(), score
            if before == score:
                break
        # Further rounds cannot improve on attaining every feasible interaction.
        # Ties retain their first witness, so early stopping preserves this plan.
        if best_score == reachable:
            break
    return best, greedy


def prepare(raw):
    sets = [set(f) for f in raw.values()]
    names = sorted(set.union(*sets) - set.intersection(*sets))
    rows = sorted((tuple(int(name in features) for name in names), key)
                  for key,features in raw.items())
    pairs = list(itertools.combinations(range(len(names)), 2))
    masks = [sum(1 << (4*p + 2*x[i] + x[j]) for p, (i,j) in enumerate(pairs)) for x,_ in rows]
    n = len(rows)
    all_pairs = union(masks, range(n))
    counts = [sum((mask >> bit) & 1 for mask in masks) for bit in range(all_pairs.bit_length())
              if (all_pairs >> bit) & 1]
    expected = sum(1 - math.comb(n-c,BUDGET)/math.comb(n,BUDGET) for c in counts)
    def encode(plan):
        assert len(plan) == len(set(plan)) == BUDGET
        return dict(ids=sorted(rows[i][1] for i in plan), covered=union(masks,plan).bit_count())
    options = []
    for seed in SEEDS:
        optimized,greedy = sample(masks,seed,len(counts))
        options.append({"seed":seed, "plan":encode(optimized), "greedy":encode(greedy)})
    best = max(options,key=lambda d:d["plan"]["covered"])
    return dict(n=n,features=names,feasible_pairs=len(counts),uniform_expected_pairs=expected,
                chosen_seed=best["seed"],plan=best["plan"],greedy=options[0]["greedy"],runs=options)


if __name__ == "__main__":
    settings = json.loads((HERE/"settings.json").read_text())
    frozen, exclusions = {}, {}
    for project, count in CENSUS.items():
        raw = settings[project]
        unique = len({tuple(f) for f in raw.values()})
        if count < BUDGET or unique != count or len(raw) != count:
            exclusions[project] = dict(paper=count,raw=len(raw),distinct=unique)
            continue
        frozen[project] = prepare(raw)
    (HERE/"frozen.json").write_text(json.dumps(dict(frozen=frozen,exclusions=exclusions),
                                               indent=2,sort_keys=True)+"\n",encoding="utf8")
