# Helper-basis resynthesis: scoped search, no new κ

This package changes the scalar factorization of PR1286's complex word and
then checks its complete local frame bill. It does not nominate an improved
bound. The separately reproduced PR1286 value is
**κ = 0.001676332167598458**, conditional on its inherited obligations.
That construction belongs to its credited authors; it is not a new result of
this search and is not a change to the maintainer-selected certificate.

A subsequent independent fresh replay of Rohan Arun's **PR1297**, pinned at
`4abf710a7f0d2a46f522f3f13c15769d003f9495`, passed with conditional
**κ = 0.001676854978651125**. Both native providers were rebuilt, and strict
global admission passed. `evidence/PR1297-*` binds that reproduction. The
basis-search input remains PR1286; the higher κ is credited to PR1297's
four-kernel composition, not to any word generated here.

## What was tested

For helper registers `h,d`, let `S = I + a E[d,h]`, with dyadic `a`. Conjugate
the scalar gates by `S`, simplify only commuting additions, and solve the
remaining native frame constraints. Selected helpers are untouched by A and
the central cut. The pair census uses identical entry and exit frames, 869
unordered pairs, both orientations, and coefficients `±1/2, ±1, ±2`.

All 10,428 permanent pair changes fail the fixed-order frame screen. Eleven
remove two scalar additions. Four scheduling priorities on each of those
eleven also produce no admitted word; a failed greedy schedule alone is not
a proof about every legal ordering.

Temporary changes conjugate a B prefix, insert the inverse at an explicit
seam, and restore the dirty helper coordinates at the end. Every internal undo
gate and every low-frame restoration participates in the frame bill. FULL
cleanup is permitted only on FULL-ended registers. No basis change is treated
as a free internal operation.

The additional families are a pair-prefix screen, joint disjoint shears on
four-helper blocks, and dense four-coordinate changes obtained by dyadic
Gaussian elimination of the correction matrices. Intermediate conjugations
need not be geometrically feasible. The final emitted word must be feasible.
Exact coverage, failures and costs are recorded in `RESULT.json`; the receipt
files retain the individual specifications. These are finite search domains,
not a universal obstruction to basis changes or new multiplication algorithms.

| Family | Distinct nonzero words within family | Frame-feasible, unchanged profile |
| --- | ---: | ---: |
| Permanent pair conjugation | 10,428 | 0 |
| Temporary pair basis | 1,012 | 644 |
| Joint pair changes on four helpers | 4,380 | 1,740 |
| Dense four-coordinate changes | 1,152 | 576 |

The temporary pair/block drivers also run one zero-shear control each, excluded
from this table. Duplicate emitted words within each temporary family are
removed. No claim is made that words are distinct across different families.
All 2,960 feasible nonzero words have the identical paid profile; endpoint
audits are performed on selected controls rather than independently repeated
for every search row.

## Concrete obstruction and positive control

In the permanent `h=593,d=594,a=1` rewrite, vector `2` from input register 8
propagates through four common-frame gates to target 171. That target's port
is 38, and `popcount(2 & 38)` is odd. Its required final hyperplane excludes
the vector. `evidence/GLOBAL-OBSTRUCTION.json` gives the literal path. The
counterexample applies to this emitted order.

Undoing that mixing at original B seam 1053 gives an exact nonzero positive
control. The independent auditor checks all 704 columns in both orientations,
the entry response, dirty restoration, frame chains and final cones. Its
profile is unchanged: `{1:2352,2:504,3:412,4:130,5:82,8:8}`. This control
establishes local admissibility; it has no fresh global owner admission.

`BLOCK-LEMMA.md` gives a separate structural observation: all 12 dense-screen
correction matrices are invertible, so an invertible coordinate change cannot
remove every dependency on the common source frame from any recipient. Each
recipient must still contain that frame at the seam. This does not establish
optimality of the complete paid profile or rule out coalescing later growth.

## Replay

From this checkout, with Python 3.11 and NumPy:

```sh
python -B research/complex-helper-basis-screen/verify.py --work /tmp/helper-basis-focused
```

The output path must not exist. The focused verifier binds sources, reruns
1,600 exact conjugation checks and 100 simplification checks, checks the
permanent word's full scalar endpoint, verifies the frame obstruction, and
rebuilds/audits the nonzero prefix control. Negative controls reject corrupted
conjugation, path, scalar coefficient and missing dirty restoration.

To rerun the search, use a new external output directory:

```sh
mkdir /tmp/helper-basis-search
export BASIS_WORK=/tmp/helper-basis-search
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
python -B research/complex-helper-basis-screen/code/basis_search.py census
python -B research/complex-helper-basis-screen/code/basis_search.py price --limit 10428
python -B research/complex-helper-basis-screen/code/prefix_search.py --pairs 92
python -B research/complex-helper-basis-screen/code/prefix_search.py --blocks
python -B research/complex-helper-basis-screen/code/dense_search.py
python -B research/complex-helper-basis-screen/code/reorder_search.py
```

Frame pricing uses the retained PR1186 objective at its documented nearby
endpoint. Cached component solutions are reused only when the cost table,
all frame domains and every objective factor are identical. Every assembled
assignment is checked for feasibility and independently recounted. The focused
verifier cross-checks the cached and original solvers. Equal full profiles
give the same recursive bill at every endpoint; no rounded-cost decrease is
being promoted to an exponent claim.

For a fixed prefix basis `S`, undoing it at any seam leaves the same complete
B scalar map, `B_original S^-1`. The prefix driver therefore also reuses its
exact scalar cone/compensation calculation across those seams. The gate order
and all frame constraints are still checked separately for each word.

The separate, unchanged PR1286 native/global replay is:

```sh
python -B research/global-mixed-k531-k543/verify.py --work /tmp/pr1286-fresh
```

Its fresh two-word native and strict-global receipts are retained under
`evidence/PR1286-*`. Both native reuse flags are false. Its package/compiler
requirements still apply. The focused verifier does not rerun that five-stage
native/global chain or discharge any inherited all-size theorem obligation.

For PR1297, use its pinned checkout and
`python -B research/global-mixed-four-cold-kernels/verify.py --work /tmp/pr1297-fresh`.
Its source manifest and claim are retained with the receipts. Both words passed
fresh native replay, 24 new kernel controls, 12 inherited kernel controls,
strict owner/controller admission and all 47 outer inequalities with the two
retained exact moment engines. The same inherited theorem conditions remain.

## Open next questions

1. Can a different scalar factorization remove the cross-port dependencies
   without restoring the original basis before their frames diverge? A useful
   next candidate must change the paid profile, rather than just gate count.
2. Can input/output interfaces be changed together so that the obstructing
   vector is legal, with a complete price for every interface conversion?
3. Can sharing between complete recursive calls reduce the central-path bill?
   These single-call helper changes do not test that mechanism.

Prepared for Thomas DiFiore with OpenAI Codex assistance. See `NOTICE.md` for
predecessor attribution and `SOURCE-PINS.json` for exact bindings.
