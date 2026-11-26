# Joint database-histogram and projected-column upper bounds

The data, objective and 365 marked interactions are those in the preceding JHipster experiment. The following procedure gives an exhaustive integer search for an upper bound on the number of distinct interactions covered by twelve rows. All row-indexed information comes from the frozen feature CSV. Neither the Build field nor fault labels enter this program.

## Exact loss identity

There are 396 unmarked interactions. Let r(x) be the number of marked interactions covered by one configuration x. Every configuration has r(x) at most 21. For any list of twelve configurations, let c(t) count the occurrences of interaction t. The slack below 648 equals the sum of the following nonnegative integer terms.

1. The twelve row terms, each equal to 21 minus r(x).
2. For each unmarked interaction, one if its count is zero, zero otherwise.
3. For each marked interaction, the number of occurrences beyond its first, max(0,c(t)-1).

Indeed, adding the marked counts over all twelve rows gives the total number of individual occurrences. Removing the extras gives the number of distinct marked interactions. Adding the covered unmarked interactions proves the identity.

## Exhaustive histogram reduction

The three fields databaseType, devDatabaseType and prodDatabaseType form twelve possible joint types. There are 1,352,078 weak compositions of twelve into twelve parts. For each type, its count times its smallest row slack is a lower bound on row losses. An interaction of two database fields has a known count, so its exact loss can be charged.

For a fixed value of a database field and a different non-database field, suppose that m rows have that value and there are k feasible interactions in the slice. If all k are unmarked, at least max(0,k-m) are missed. If all k are marked, at least max(0,m-k) redundant occurrences are unavoidable. Summing these losses uses disjoint interactions. The traversal discards a partial histogram as soon as its already determined losses exceed the budget. Partial grouping only processes terms whose classes have all been assigned.

Exchanging the names of three SQL products simultaneously in the development and production fields, and swapping the two embedded development modes, gives up to twelve relabelings. The preprocessor checks the image of every raw configuration under every relabeling before using it. Each accepted relabeling preserves the objective because it permutes rows and interaction labels bijectively. This only uses symmetry of the original problem. A particular artificial choice of marked interactions need not possess the symmetry. A single surviving representative therefore suffices in each orbit.

## Exhaustive search within each surviving histogram

Fix twelve positions in order of database type. Extend them one field at a time. An accepted prefix of an individual position must occur in at least one original configuration with that database type. Its smallest possible row slack is computed from all such completions. Identical database types allow positions to be sorted lexicographically by the fields assigned so far.

For the current field compare it with every earlier field, including all three database fields. A bit set tracks interactions seen so far. Each additional occurrence of a marked interaction costs one. An as-yet-unseen unmarked interaction whose value has no support in any remaining position costs one. At the end of the column the unmarked count is exact. The same pair of fields is charged only once. Row slack is a lower bound on the total slack in the final rows and is tested afresh on every level; it is never spent repeatedly.

The optimized version also reserves unavoidable losses for future pairs. If an already determined value occurs m times, has u unmarked feasible partners and w marked feasible partners in an unassigned field, it forces at least max(0,u-m) missed unmarked interactions. When u is zero it also forces max(0,m-w) extra marked occurrences. These reserves concern pairs not yet fully assigned and are replaced with exact counts after the appropriate column is assigned. Every pruning rule is necessary for meeting the target. Consequently a `False` result for all remaining histograms excludes that target even when only a subset of the eleven non-database fields was searched.

## Reproduction

Use Python 3.11+ and a C# compiler. First run the following with the original JHipster CSV and the old bound.json. The threshold used when generating input must be less than or equal to the threshold being tested.

~~~~
python prepare.py jhipster.csv bound.json 643 input
~~~~

Compile Join.cs with optimization, then run the program with working directory `input`. On Windows the framework compiler accepts `csc /optimize+ /out:Join.exe Join.cs`. For the projection excluding 645 or more, use the following.

~~~~
Join.exe 645 10,3,11,1,2,4,5,12
~~~~

For the stronger searches use all eleven non-database fields, in order `10,3,11,1,2,4,5,12,0,9,13`, and the desired threshold. Every line must be inspected. A `True` result on a projection indicates a candidate for further search; only a complete eleven-field witness rechecked against the original data certifies a feasible plan. Full enumeration is finite, with runtimes depending on the target and histogram. The proof consists of an integer exhaustive computation and the reductions above. A theorem prover has not checked the reductions or the search implementation.

## Completed exclusion at 643

The first stage retained 267 of the 1,352,078 histograms. The twelve data-validated relabelings reduced these to 29 representatives. The last representative has all three of its database fields distributed as recorded on the unique line of top.txt beginning with 648. We processed the first 28 with column order 10,3,11,1,2,4,5,12,0,9,13, traversing 128,035,123 completed column prefixes. We processed the last with the order 10,11,3,1,2,4,5,12,0,9,13, traversing 140,072,694. All 29 returned False. The merged log contains 268,107,817 completed column prefixes in total. The separately validated twelve-row plan covering 642 interactions attains the resulting upper bound. The exact maximum for this fixed dataset and objective is 642.

To reproduce the same prefix count, split top.txt on whether its first integer equals 648 (first28.txt excludes that line and last.txt contains it). Run both commands in the prepared input directory and concatenate the two output logs. Alternatively a single run on all 29 with one column order proves the same exclusion, and its prefix count can differ.

~~~~
Join.exe 643 10,3,11,1,2,4,5,12,0,9,13 first28.txt
Join.exe 643 10,11,3,1,2,4,5,12,0,9,13 last.txt
python check_run.py top.txt excludes643.log 643
~~~~
