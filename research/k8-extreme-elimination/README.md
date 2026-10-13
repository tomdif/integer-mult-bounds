# Extreme helper elimination and a matrix-label research pivot

**No improved kappa.** The reference conditional value remains
`0.001675809683500501`, independently reproduced in
[x54-mixed-allocation](../x54-mixed-allocation/README.md). This package contains
an exact 464-helper scalar construction, a short obstruction to its geometric
admission, bounded searches, and a first experiment outside projector labels.
It does not supply a new recursive word or claim a record.

## A real scalar saving with an explicit geometric failure

Eliminating these 16 original helpers from the 480-helper THREE word succeeds:

```
461 462 463 464 465 466 467 468
469 470 471 478 479 480 481 482
```

The compiler tracks the missing coordinate as an exact linear combination of
the surviving coordinates. Reads substitute that relation; writes update it.
The general search also permits dyadic pivots into other eligible cold helpers.
This particular 16-deletion witness requires no pivots. It changes the raw
scalar gate count from 12,459 to 12,548, excluding its explicitly reconstructed
7,083 compensation additions. Helper count alone is not recursive cost.

The retained PR1049 checker verifies its endpoint, and the unchanged
`gauge44-slots/independent/audit_local.py` scalar interpreter verifies every
one of its **688 columns in both forward and dual orientations**, with the
actual dirty compensation included. Dropped and sign-flipped target additions
are rejected. Old paid-profile metadata has been removed from the artifact.

Even setting all helper entrances to zero and all helper exits to FULL cannot
admit this trace. A two-gate witness suffices (zero-based indices):

```
A[1384]: add helper 242, source 25, +1
B[1949]: add target 192, helper 242, -1/2
```

Source 25's frame contains vector 336. The first common-frame gate puts it in
helper 242's frame. Monotonicity retains it until the B read, which puts it in
target 192's frame. That target must end in the hyperplane perpendicular to
port 73, but `parity(336 & 73) = 1`. This is a literal contradiction under the
common-frame, monotone, A-before-B premises, independent of the choice of
helper entrance or end frames. Altered factorizations, ports, cuts, or paid
descents are outside this obstruction. It is not an impossibility theorem for
464-helper constructions.

The separate standard-library obstruction checker imports no generator,
scheduler or frame solver. It checks the word hash, source membership, actual
gates, mandatory edges and endpoint cap, rejecting three corruptions per
witness. A second witness retains the original warm entrances.

## Completed bounded searches

| Search | Cases or attempts | Result |
| --- | ---: | --- |
| Static deletion of every eligible cold FULL helper | 237 | 121 compiler rejections; 116 frame failures |
| Dyadic hole pivoting, singles and joint batches through all 237 eligible helpers | 468 | 273 compiler rejections; 195 frame failures |
| Reorder compiled cases, preserving noncommuting pairs | 195 cases, 231 attempts | No admitted order |
| Refit entrances, with existing or FULL helper ends | 195 cases, 390 attempts | No feasible frame bounds |
| Combine deletion, reordering and cold/FULL boundaries | 195 cases, 231 attempts | No admitted order |

There were 139 compiled singles, 44 pairs, nine groups of four, two groups of
eight and one group of sixteen. Compiled cases pass two modular scalar checks
per deletion; only R464 receives the full exact endpoint replay reported here.
Compiler limits are 60,000 emitted gates, relation support 256, and 60 seconds
per case. Reordering tries four deterministic priorities within retained phases.
Rejections and limits concern these algorithms and inputs, not all rewrites.
The archives retain every case, reason, compiler receipt and progress log.

## Why change the research target

Applying Douglas Colkitt's PR1240 relaxation to our fixed 125/208 mixture gives
these **optimistic upper bounds**, not achieved constructions:

| Largest idle rank | Kappa upper bound, approximately | Maximum relative gain over our reference |
| --- | ---: | ---: |
| 48 | 0.001675811521577451 | 0.000109683% |
| 51 | 0.001683679967213164 | 0.469641% |

These hold only for the fixed local profiles, coverage law, live families,
centre charge and stated idle-rank cap. Fractional packing and zero additional
overhead are granted. New words or coverage laws are outside their scope.
Two unchanged exact moment engines verify the brackets after denominators are
cleared by integer replication; fractional counts are never truncated.

[NEXT-STRATEGY.md](NEXT-STRATEGY.md) develops a different search space:
arbitrary rational matrix labels in the original bit contract, and block
operator factorizations as a separate complex-side question. The first 40
small XOR circuits, using 2-by-2 or 3-by-3 integer labels, give no strict rank
saving after 7,813,342 evaluated proposals (12,000,000 scheduled iterations).
This is an exploratory search, not evidence of general impossibility.

## Reproduce

From this checkout, Python 3.11+ with NumPy/SciPy/SymPy available:

```sh
python3 -B research/k8-extreme-elimination/verify.py --work /absolute/fresh/output
```

This verifies package and retained source bindings; freshly reconstructs R464,
compensation and both obstruction witnesses; repeats the exact forward/dual
scalar replay and controls; checks both ceiling engines and valid scheduling
controls; and independently recounts the matrix-label search witnesses. It
compares the frozen census totals but **does not rerun the full searches**.
No new native supplier, global owner admission or full repository suite is
claimed, because no geometric nomination survived.

To repeat the old-circuit searches in a fresh external directory, set
`EXTREME_WORK` to that directory and run, in order, the scripts
`eliminate_register.py`, `dynamic_elimination.py`, `reschedule_eliminated.py`,
`unlock_interfaces.py`, and `joint_redesign.py` under `code/`. These use three
local worker processes; output order and timings can differ. The matrix-label
search can be repeated by copying `rank_network/` to an external directory,
running `build_cases.py`, compiling `search.cpp` with C++17, and running the
binary with `SEARCH.txt` as stdin and `RESULT.txt` as stdout. Its verifier
compares the frozen receipt; different standard-library RNG behavior may
change the heuristic transcript without changing the checked contract.

Prepared for Thomas DiFiore with substantial OpenAI Codex assistance. See
[NOTICE.md](NOTICE.md) for source credit and limitations. No independent human
review or proof-assistant verification is claimed.
