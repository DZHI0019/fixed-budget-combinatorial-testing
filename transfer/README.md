# Pair coverage and historical failures in four independent software test subjects

Soma · Research assisted by GPT 6.2 · 2026-11-26 · Unreviewed

## Finding

In the 64-configuration MinePump benchmark, two plans of exactly 12 distinct configurations both cover every one of the 60 feasible assignments on pairs of options. One plan selects **zero** of the eight configurations with historical failure reports. Another selects **all eight**. Both are optimal for the pair-coverage objective, and both correspond to actual historical tests. Thus even exact optimization of pair coverage can leave fault detection completely undetermined on this subject.

Every recorded failing configuration has highWaterSensor enabled, lowWaterSensor disabled and methaneAlarm disabled, and all eight configurations with that triple have a report. Every pair assignment occurs in at least one configuration without a failure report. A three-way covering plan must therefore touch this historically failing subcube. The supplied **12-configuration** plan covers all 160 three-way assignments at the same budget. This is a retrospective guarantee tied to the named dataset, not evidence that the sensors cause failures in a deployed pump or a future release.

## Experiment

Ferreira et al. reported exhaustive execution of the eight small configurable systems in Dataset A. We fixed the selection rules in protocol.md and the 12-row plans in frozen.json before joining the files in failuresFound. The dataset's previously published aggregate event counts were known. All results are retrospective. The project names refer to benchmark software, not live production systems. The study includes no unseen release.

| Subject | Configs | Feasible pairs | Optimizer pairs / greedy pairs | Uniform expected pairs | Reported configurations in optimizer / greedy | Uniform expected reported configurations | Exact attainable endpoints at full pair coverage |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ATM | 80 | 82 | 82 / 82 | 78.09 | 12 / 12 | 11.85 | 11 and 12 |
| MinePump | 64 | 60 | 60 / 60 | 58.73 | 1 / 2 | 1.50 | 0 and 8 |
| Companies | 192 | 140 | 140 / 140 | 129.86 | 1 / 2 | 0.50 | 0 and 6 |
| Sudoku | 20 | 54 | 54 / 54 | 52.56 | 3 / 2 | 2.40 | 1 and 4 |

The fixed-budget optimizer and greedy both cover 100% of that subject's feasible pairs. Their historical reported-configuration totals across the four subjects are 17 and 18; random sampling without replacement has exact expectation 16.25. For a pair reachable in c out of n rows and a 12-row budget, the probability of covering it is 1 − choose(n−c,12)/choose(n,12). Summing these probabilities gives the random expected coverage. The reported endpoints were found in a separate outcome-aware retrospective optimization; none of these endpoint witnesses was used to score the label-free optimizer. For Companies, two of the three independently frozen optimizer seeds miss every historical report while covering every pair.

The endpoint proofs are short. ATM has only one configuration without a recorded failure. MinePump has eight configurations with failure reports. Sudoku has four. Any fully pair-covering Sudoku plan must include a reported configuration because EXTENDEDSUDOKU=1, GENERATOR=1 occurs only in reported configurations. For Companies, six pair assignments require six distinct configurations without reported failures: their supports are nonempty, pairwise disjoint, and contain only such configurations. Their identities and sufficient finite checks are in verify_extremes.py, and all extreme witnesses are listed in extreme-plans.json. Endpoints are minima and maxima, not assertions that all intermediate counts occur.

Twelve is the **global minimum** for full three-way coverage on this MinePump snapshot. Its 64 rows form the entire six-dimensional binary cube. Splitting a three-way covering suite on the highWaterSensor bit leaves two subsuites; each must cover the 40 possible pair assignments on the five other bits. A kernel-checked exhaustive search proves five rows cannot do so on either side. Thus even a suite allowing repeated rows needs at least 6 + 6 tests. The existing 12-row witness attains this bound. The abstract six-factor binary covering-array number was already known and appears in Table 1 of [Lawrence et al. (2011)](https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=51256).

In the source archive ATM has 81 CSV event rows and 79 distinct reported configurations; Companies has 16 event rows and 8 distinct reported configurations. The paper's summary gives 80 and 6 failure occurrences respectively. We report archive values after joining full feature vectors and do not force agreement. MinePump has 24 event rows on 8 configurations, Sudoku 4 rows on 4; these two event counts agree with the paper. No event row in any retained project is outside its settings population. Distinct failing configurations and named tests must not be interpreted as independently established root causes.

The predeclared census and budget filter excludes BankAccount (paper 144, archive 145 unique), GPL (73, archive 89 files / 71 unique), Chess (7, archive 8, below budget), and Paycard (6, below budget). This leaves four out of eight Dataset A subjects. Table-wide comparisons between testing methods already exist in this literature. This analysis does not claim priority for the general observation that pairwise coverage and real fault detection differ.

Sources: [Ferreira et al., SPLC 2020](https://splc2020.net/wp-content/uploads/2020/03/SPLC_2020_paper_1.pdf), [archived benchmark source at the version used](https://github.com/fischerJF/challenge/tree/eb6d88977219f1b090ab340b45b6bb3f10d30ce1), [Ferreira et al., 2021 comparative study](https://doi.org/10.1016/j.jss.2021.110990).

## Reproduction

The formal certificate is self-contained. Run Lean 4.30.0-rc2 with `lean formal/Transfer.lean`. The Python scripts require Python 3.11 or newer. To independently establish the link between that certificate and the published benchmark, download the [pinned archive](https://codeload.github.com/fischerJF/challenge/tar.gz/eb6d88977219f1b090ab340b45b6bb3f10d30ce1) as source.tar.gz. The scripts only read feature vectors and historical result files. Inside this directory run:

~~~text
python read_source.py source.tar.gz
python freeze.py
python score.py
python threshold.py
python minepump_threeway.py
python verify_extremes.py
python export_lean.py
lean formal/Transfer.lean
~~~

To replay the additional optimality proof in **PowerShell**, run the following in the formal subdirectory with Lean on your PATH. On Linux or macOS use `LEAN_PATH=. lean MinePumpMinimum.lean` for the last two lines.

~~~powershell
lean -o Transfer.olean Transfer.lean
$env:LEAN_PATH = (Get-Location).Path
lean MinePumpMinimum.lean
~~~

The archive used here has SHA-256 54f08ff354ca2c654cbd830246741dbc401a996ee0af1a7e40fe0b78d9bdc9de. frozen.json is locked with SHA-256 7078551c818e0ce90d43b6b8d616874bfa27e560dad92a56fb78431c45154243 using LF newlines. verify_extremes.py reads the underlying raw reports separately from score.py, recreates the realized pair universe, verifies every extremal plan, and checks the certificates bounding the possible counts. Optional find_extremes.py uses SciPy to search for endpoint witnesses; it is not required to reproduce the proof. Its published witnesses are fixed in extreme-plans.json. The empirical conclusions remain conditional on the authors' recorded outcomes being accurate.

Lean checks legality, full pair coverage and the hit count of each endpoint suite. Its universal bounds apply to arbitrary 12-row, legal, distinct, fully pair-covering suites as applicable. It also checks the same-budget full-three-way MinePump witness and proves detection for any suite covering every historical three-way assignment on that subject. Each integer-coded row represents the enabled subset in alphabetic feature order, with the first varying feature stored in the least-significant bit. Data extraction from the original archive and the published experiments themselves are outside the Lean kernel.

## Independent check of the empirical table

Running read_source.py on the pinned archive regenerates settings.json and the outcome inputs locally. From the transfer directory, use `python derive_table.py . formal/EmpiricalTable.lean` to reconstruct the table certificate. After building Transfer.olean as above, run `lean EmpiricalTable.lean` from the formal directory with LEAN_PATH set to that directory. This checks both sets of 12 test IDs as encoded by the helper, their coverage and the aggregate reported counts of 17 and 18.
