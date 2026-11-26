# Independent checks of the finite upper-bound computation

The source under audit represents a 12-row plan by the multiplicities of its twelve database types and then by the values of additional fields in those rows. The starting certificate marks 365 interactions and every row includes at most 21 marks. For any plan, subtracting its actual coverage from 648 gives the sum of three nonnegative numbers:

1. The sum over selected rows of 21 minus the number of marks in that row.
2. The total excess multiplicity of marked interactions (all occurrences after their respective first occurrence).
3. The total number of feasible unmarked interactions missed.

Restricting terms 2 and 3 to a subset of pairs gives a valid lower bound on that deficit. A smaller deficit is a necessary condition for any putative better plan.

## Histogram calculations

The independently written `audit_hist.py` generates all 1,352,078 multisets of 12 members drawn from 12 database types using combinations with replacement. It computes the histogram bound for every multiset, without early rejection of prefixes. By comparison the primary program uses recursive composition generation and prunes partial compositions. The following checks passed against the primary representative file.

| Target | Surviving histograms | Represented orbits |
|---:|---:|---:|
| 643 | 267 | 29 |
| 644 | 192 | 21 |
| 645 | 138 | 15 |

The audit also checks equality of the complete configuration set before and after each of the 12 claimed renamings. The objective counts field/value pairs, so these bijective renamings preserve the underlying optimization problem, even if the original fixed mark set changes.

## Projection searches

For a fixed database multiset, rows are indistinguishable within equal prefixes. Sorting the next field within each such group preserves a representative of every feasible assignment. At a search node the minimum per-row slack among compatible data rows lower-bounds the eventual contribution of part 1 above. This slack is used for a pruning test rather than charged again each time another field is chosen.

The new interactions introduced with field f and a previously fixed field all belong to f's own stage. Each repeated mark is charged once for every occurrence after its first. An unmarked interaction absent both from the prefix and from every viable completion must remain absent. For future columns the primary implementation reserves valid lower bounds from the fixed fields' marginal counts. These future bounds are over different unordered field pairs from the current-stage interactions. The reserve is restored on descent before a new reserve is computed.

The separate `audit_projection.py` tests the actual compiled search on 36 generated restricted instances. One true CSV row survives per database type, so the given histogram uniquely specifies the entire multiset, including possible repetitions. A direct evaluation of the above identity gives the **exact** projected feasibility threshold. All 72 solver answers at the threshold and one above it matched this independent oracle. Tests include the eight-field projected search, the complete eleven-field order, and shorter partial projections.

The restricted cases test code paths and boundary conventions. The claim on the complete input still depends on the primary exhaustive enumeration and the absence of survivors at the reported target.

Run the histogram audit with Python 3.11 or newer and NumPy. Run the projection tests using a primary verifier executable compiled for the host OS.

~~~sh
python audit_hist.py jhipster.csv plan642.json bound.json 643 proofrun/top.txt
python audit_projection.py jhipster.csv plan642.json bound.json proofrun/instance.dat proofrun/Fast.exe
~~~
