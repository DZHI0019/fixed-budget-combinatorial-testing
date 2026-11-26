"""Smallest interaction strength at which complete coverage must include a reported failure."""
from collections import Counter
import json
import itertools
from read_source import HERE
from score import labels


def classify(fields, raw, failing):
    for strength in range(1,len(fields)+1):
        witnesses = []
        interactions = 0
        for names in itertools.combinations(fields,strength):
            patterns = {}
            for key,features in raw.items():
                values = tuple(int(f in features) for f in names)
                patterns.setdefault(values, []).append(key)
            interactions += len(patterns)
            for values,keys in patterns.items():
                if all(k in failing for k in keys):
                    witnesses.append(dict(fields=names,values=values,support=keys))
        if witnesses:
            return dict(strength=strength,interactions=interactions,
                        solely_reported_interactions=len(witnesses),one=witnesses[0])
    return {}


if __name__ == "__main__":
    f=json.loads((HERE/'frozen.json').read_text())['frozen']
    raw=json.loads((HERE/'settings.json').read_text())
    out={}
    for project,p in f.items():
        fail=labels(project,raw[project],HERE)[0]
        out[project]=classify(p['features'],raw[project],set(fail))
        print(project,out[project]['strength'],out[project]['solely_reported_interactions'],
              out[project]['one']['fields'],out[project]['one']['values'])
    (HERE/'thresholds.json').write_text(json.dumps(out,sort_keys=True,indent=2)+'\n')
