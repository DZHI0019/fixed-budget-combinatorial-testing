# Testing a label-free three-way tie-break retrospectively

Each candidate contains twelve configurations. The common rule first prefers more distinct observed two-field value assignments, then more distinct three-field value assignments, then the smaller seed. For each unordered choice of three different fields, a value triple counts once regardless of the number of chosen rows displaying it. The final score sums these counts over field triples.

The candidate pools contain the nine previous JHipster 642-pair plans (seeds 17, 19, 101, 107, 109, 311, 313, 417, 419) and the three previously generated pair-optimized plans for each of four external projects (seeds 261126–261128). All candidates in each project's pool have the same two-field score. The comparison optimizes the tie-break only over the declared pool. No historical outcome enters the selection script. We had already seen outcomes for these projects when formulating the secondary objective; this is retrospective exploration. The first JHipster plan and the original four external plans remain the baseline selections.

| Project | Fixed pair score | Triple coverage, baseline → tie-break | Historically failed/reported configurations | Distinct archived fault labels or test signatures |
|---|---:|---:|---:|---:|
| JHipster 3.6.1 | 642 | 3,575 → 3,588 | 8 → 6 | 6 → 4 |
| ATM | 82 | 224 → 229 | 12 → 12 | 2 → 1 |
| MinePump | 60 | 140 → 143 | 1 → 2 | 3 → 3 |
| companies | 140 | 559 → 559 | 1 → 1 | 2 → 2 |
| sudoku | 54 | 114 → 117 | 3 → 3 | 1 → 1 |

JHipster counts named BUG categories; the other projects count distinct archived test descriptions. JHipster's failed-build count includes environmental issues. Counts from different projects represent different outcome measures.

JHipster gives a concrete counterexample to a monotonicity claim on this finite archive. Two lists have equal length and achieve the same maximal pair coverage. The list with more triple coverage detects fewer archived defect categories. ATM gives a second example for archived test signatures. These comparisons do not measure expected performance on new versions.

## Reproduction

Run the commands from the repository root after generating the transfer inputs. Supply the original JHipster CSV, its earlier frozen plan with field definitions, and the four-project transfer directory (settings.json, frozen.json, score.py, read_source.py and labels). The first command uses only configuration fields and seed metadata. The second command validates the lock digest before reading outcome data. Archive evidence files were generated using Python 3.12.

~~~sh
python lower/tiebreak/choose.py jhipster.csv lower/plan642.json lower/tiebreak/jhipster-candidates.json transfer/settings.json transfer/frozen.json locked.json
python lower/tiebreak/evaluate.py locked.json jhipster.csv transfer outcomes.json
~~~

Selection lock SHA-256: af204b06492ac22e2a2839814fe80741f2c0f7a0f4418503834a81db435fc98d. The lock contains all candidates' configurations and both scores; outcomes.json includes outcomes for every candidate, including the ones not selected.
