"""Discover witnesses for extremes using optional SciPy. The final checker uses only stdlib."""
import json
from itertools import combinations
from pathlib import Path
from read_source import HERE
from score import labels
import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp


def extremes():
    frozen = json.loads((HERE/'frozen.json').read_text())['frozen']
    settings = json.loads((HERE/'settings.json').read_text())
    witness = {}
    for project,p in frozen.items():
        raw = settings[project]
        ids = sorted(raw)
        failing = set(labels(project,raw,HERE)[0])
        pairs = list(combinations(p['features'],2))
        hits = [{(i,j,i in raw[k],j in raw[k]) for i,j in pairs} for k in ids]
        universe = sorted(set.union(*hits))
        mat = np.array([[1. if t in row else 0. for row in hits] for t in universe]+[[1.]*len(ids)])
        constr = LinearConstraint(mat,[1]*len(universe)+[12],[np.inf]*len(universe)+[12])
        change = np.array([int(k in failing) for k in ids])
        bounds = Bounds(0,1)
        output = {}
        for sign,extremum in [(1,"min"),(-1,"max")]:
            res = milp(sign*change,integrality=np.ones(len(ids)),bounds=bounds,constraints=constr,
                       options={'time_limit':35})
            if res.x is None:
                continue
            plan = [k for k,val in zip(ids,res.x) if val>.5]
            output[extremum] = {'ids':plan, 'failures':len(set(plan)&failing),
                                 'solver_status':int(res.status), 'solver_gap':res.mip_gap}
        witness[project] = output
        print(project, [(k,v['failures'],v['solver_status']) for k,v in output.items()], flush=True)
    (HERE/'extreme-plans.json').write_text(json.dumps(witness,indent=2,sort_keys=True)+'\n')


if __name__ == '__main__':
    extremes()
