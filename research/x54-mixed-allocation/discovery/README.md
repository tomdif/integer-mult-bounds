# Bounded follow-up searches

These searches did not improve the composed X54 mixed witness. They use Marius-Paul Dumitrean's unchanged PR1186 exact-frame toolkit at `9254a3cc610a72e9c4600da089d5cdbcab996b9c`. Its notice and source are in `../vendor/pr1186`. `SUMMARY.json` pins both input words and the cost endpoint. These are discrete circuit/frame screens, not an exhaustive search over constructions or an impossibility proof.

| Search | Recorded work | Result |
|---|---:|---|
| Single-source fusion with reader repairs | 2,238 candidates, 2,850 evaluations | 969 candidates returned a priced repair; no saving |
| Commuting event reordering | 700 retained trials out of 14,720 planned | 680 certified, 20 infeasible, no saving; search intentionally stopped |
| One donation shared across several targets | 215 candidates | All certified; no saving |
| Two donated sources shared across a target batch | 30 candidates | All certified; no saving |
| One-helper entrance demotion | 372 trials | All certified; no saving after crediting one idle rank-one axis |
| Proper subsets of the known fourth group | Six pairs and four triples | All certified ties after idle credit |

The first four searches use D3 only. The single-helper search covers all 31 codimension-one subspaces of eight specified rank-five entrances in D3 and four in D4. It is not a census of every helper. Its certified optimum applies to each fixed scalar order and nominated interface under the toolkit's frame constraints and integer cost endpoint. Native/global admission is not inferred for any search candidate.

For a shared donation, targets reading `a_t*A + c_t*H` with common `a_t/c_t=q` can instead read `c_t*(H+q*A)`. The search inserts one donation and one restoration for the entire batch, checking source stability and target-read dependencies before frame pricing. There were 169 two-target and 46 three-target candidates. The paired search donates two sources into one holder serving the same target batch. Both families tied on these words.

The known full four-helper change is a positive control: demoting helpers 627, 629, 630 and 631 together to `[68,34,24,1]` returns D4's profile and saves 7,452 integer cost units relative to D3 plus four idle rank-one children. Each tested proper subset merely adds one H1 per changed helper. Thus the two spare rank-one children do not yield a gain through these tested partial changes. This is not a general obstruction to using that spare capacity differently.

The repair tool retains the best priced repair, not every evaluation's timeout/failure/certification status; absent results are not infeasibility certificates. Its built-in 40-option cap was nonbinding here (at most four repair options were generated). The interrupted retiming census retains only the 700 persisted results. A worker-recycling stall in the one-helper search was resolved by changing the process pool and resuming from its 120 saved results; all 372 unique cases completed.

`records/` contains the original compressed results and logs. `INDEX.json` records decompressed hashes; `scripts/` preserves the final discovery scripts. The replay wrapper changes only the historical checkout path, materializes a fresh workspace, and records those adaptations. The `retiming` option replays only the 700 retained cases. Other suite choices are `repair`, `shared`, `pairs`, `single` and `partial-group`:

```sh
python -B research/x54-mixed-allocation/discovery/reproduce.py --suite partial-group --work /absolute/new/search-output
```

Use Python 3.11+, NumPy, SciPy and SymPy on a Unix system. Discovery invokes optimizers; the separate finite-construction verifier does not. Timing and failure details may differ across environments. No new geometry, physical packing or improved κ is claimed from these negative experiments. Prepared for Thomas DiFiore with substantial OpenAI Codex assistance; credit to PR1186 and its retained frame/circuit/engine lineage.
