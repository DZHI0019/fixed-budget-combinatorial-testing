# A 642-pair test plan

The selection in `plan642.json` consists of twelve configurations in JHipster 3.6.1. It covers 642 distinct feasible two-field assignments under the field definitions of the earlier experiment. The witness alone suffices to establish the lower bound. A proof of optimality requires a separate upper bound.

The search uses only categorical settings and maintains the original budget. A proposal transfers a field, or a group of related fields such as the three database settings, between two configurations. Looking the resulting rows up in the input dictionary enforces all empirical feasibility constraints. Simulated annealing accepts some temporary losses. At the end of a round, a coordinate pass exhaustively tries all configurations at each of the twelve positions.

## Reproduce

The original data are pinned in the [JHipster 3.6.1 dataset](https://github.com/xdevroey/jhipster-dataset/blob/5e6103044c968561ad3f68d07f4f70982b7a718b/v3.6.1/test/jhipster3.6.1-testresults.csv). Save the file as `jhipster.csv`. The SHA-256 digest is recorded in `plan642.json`.

The following commands use Python 3.11+ and the .NET 10 SDK. The search was run using .NET 10.0.11 with SDK 10.0.400. `start641.json` is the frozen plan from the first round of this project.

~~~sh
python prep.py jhipster.csv start641.json rows.bin
dotnet run --project LowerSearch.csproj --configuration Release -- rows.bin result.txt 17 70 160000
python check.py jhipster.csv result.txt reproduced.json
~~~

To check the supplied index witness without installing .NET or running any search, use:

~~~sh
python check.py jhipster.csv best17.txt verified.json
~~~

The verifier reads the original CSV independently and forms literal sets of (field, value, field, value) tuples. The 12 IDs in `verified.json` and their union count can be compared directly with `plan642.json`. Neither the proposal score nor this independent verification uses any failure labels.

## Historical outcome check

After freezing this particular plan, `python historical_baseline.py jhipster.csv plan642.json` reads its archived build and bug columns. It gives eight failed builds. Six have six different study fault labels; two are marked as environmental issues. There are six named fault labels in the entire data set. For a uniformly sampled set of 12 rows drawn without replacement, the exact expected number of named fault labels is about 2.7352, and the probability of seeing all six is about 0.0008304. The calculation uses inclusion–exclusion and integer binomial coefficients. These quantities describe the uniform baseline. Other plans scoring 642 covered different numbers of historical fault labels.
