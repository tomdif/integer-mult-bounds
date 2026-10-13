# X54 on the tighter mixed T37 allocation

This package constructs the conditional finite witness **κ = 0.001675809683500501** by composing the X54 local operation with PR1193's 125/208 mixed allocation and PR1195's source-holder fusions. It changes both local scalar circuits by `+2 H3 -4 H4 +2 H5`. Every ordered helper width and interface is preserved, so the exact owner map remains available.

The value exceeds our earlier PR1148 value, 0.001675560947524449, by 0.0148449375%. During this run, Rohan Arun posted the same construction/value in [PR1218](https://github.com/CrocSwap/integer-mult-bounds/pull/1218), and Jeremy Diviney updated [PR1193](https://github.com/CrocSwap/integer-mult-bounds/pull/1193) to the same composition. This is an independent checked reproduction, not a new community record or a priority claim. PR1207 supplied the X54/fusion composition idea and mapped recipe; PR1193 supplied the exact tighter allocation.

The local profiles are `{1:2358,2:504,3:410,4:130,5:82,8:8}` and `{1:2350,2:512,3:414,4:126,5:82,8:8}`. Across 333 calls and 159,840 whole-helper roles, idle remains `{1:2,48:11374}`. CLAIM.json gives exact endpoints; PROOF.md explains the composition.

## Reproduce

Use Python 3.11+, NumPy/SciPy/SymPy, a C++ compiler and Boost headers, with a new directory outside the checkout:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 CPLUS_INCLUDE_PATH=/path/to/boost python -B research/x54-mixed-allocation/verify.py --work /absolute/new/output
```

No optimizer or network runs during verification. The wrapper rebuilds the original fusions, applies the pinned X54 scalar recipe and literal frame assignments, reconstructs D4 and the owners, and freshly replays both providers and full global admission. A completed cold PR799 replay can be supplied with `--ancestry799 /path/to/completed/replay`; all consumed bindings and mandatory coverage are rechecked. Otherwise that ancestry is rebuilt cold.

Expected final marker: `PASS_X54_MIXED_ALLOCATION_COMPLETE_ADMISSION 0.001675809683500501`. Checks include all 704 columns in both orientations for each provider, every native phase edge, eight X54 mutations, twenty fusion mutations, eleven entrance controls, eight flow controls, eight independent owner controls, 114 admission mutations, 23 controller mutations, twelve bit-supplier mutations, two exact moment engines and 47 strict outer inequalities. Repository-wide hosted CI is separate.

The complete replay passed locally, including fresh five-stage native replays of both final words, strict global admission and a newly completed cold ancestor replay. Receipts are in `evidence/replay/`; `evidence/INDEX.json` preserves original hashes for compressed receipts. `evidence/VERIFIED-MANIFEST.json` pins the package at the time of that run. Subsequent changes add documentation, discovery records, and a separate check; all previously verified proof code and frozen construction inputs remain identical. CLAIM.json's status and comparison metadata are updated to report the completed run.

The additional unchanged PR1049 checker verifies all eight coded cells, all 24 leaver conditions, the exact scalar map and frames of each final word; all fourteen semantic mutation controls reject. Replay it separately:

```sh
python -B research/x54-mixed-allocation/check_leavers.py --out /absolute/new/leaver-checks.json
```

See `discovery/README.md` for the unsuccessful local circuit and entrance searches. These are bounded negative experiments, not impossibility or optimality claims.

All-size compilation, common-label/mutable-source realization, whole-call hosting, precision/tape and recovery, analytic transfer, PR559 recurrence correction and PR589 bit H1–H5 assumptions remain. This is an incremental conditional construction, not an unconditional theorem or runtime claim. See NOTICE.md and the retained source pins for attribution.
