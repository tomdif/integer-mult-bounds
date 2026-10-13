# U10 circuit with T37 whole owners

This composition verifies the conditional exponent saving

**κ = 0.001662039077758742**

by combining [rohanarun's PR987 U10 circuit](https://github.com/CrocSwap/integer-mult-bounds/pull/987)
with [jon314159's PR942 T37 owner schedule](https://github.com/CrocSwap/integer-mult-bounds/pull/942).
The U10 rewrites extend NewBArch's PR869 triangle-hybrid deliveries.
The new contribution here is their complete T37 composition and verification;
the two circuit rewrites and owner schedule are credited to their authors.

The value exceeds PR942's `0.001661960547713947` by `7.8530044795 × 10⁻⁸`
(about **0.004725%**), and PR987's proposed U10/T21 value by
`2.773328974 × 10⁻⁹`. It also exceeds this branch's earlier rounding refinement.
This is a small construction-based improvement, not a major geometric breakthrough.

The completed 15-stage run has status
`PASS_U10_T37_STRICT_WITH_SOURCE_BOUND_ANCESTRY`. See [the result](evidence/RESULT.json),
[exact assembly](evidence/ASSEMBLY.json), [final source binding](evidence/FINAL-BINDING.json)
and [validation record](VALIDATION.json). Both moment engines, all 47 outer
inequalities, 12 recipe mutants, 95 endpoint mutants, 15 controller mutants,
69 admission mutants, 12 bit mutants and 11 payload mutants passed their
required outcomes; independent owner and parent controls also passed.

## Why the composition works

The two extra deliveries replace eight rank-4 transitions with four rank-3
and four rank-5 transitions per invocation. The local paid profile becomes

`{1:2548, 2:338, 3:450, 4:154, 5:76, 8:8}`.

Its rank mass stays 5634. All 504 helper widths, start/end frames, source
encoding, ports, and centre interface stay fixed, so T37's physical hosting
can be rechecked with the same 167832 whole-helper roles and 333 invocations.
The returned idle profile is still `{1:6, 48:11086}`. The new global profile is
333 copies of the local profile plus those idle children.

The native complex moment uses width 73 and live stock 33152. Its certified
lower endpoint is `0.001664806050471515144350`. The bit supplier and surcharge
stay unchanged at `0.001733427039589844234749`, so the complex side still binds.
The final κ uses the original `10⁻¹⁸` grid, with seven bootstrap steps and all
47 strict outer inequalities. The complex prefix charge remains 1024 bits,
the bit charge remains 512 bits, and the physical row coefficient remains
17495 below its retained limit 20161.

## Reproduce

Python 3.11+, the repository's scientific dependencies, and its native build
dependencies are required. Start from completed PR799 and PR942 runs; their
source bindings and complete ancestry are rechecked, not assumed from labels.

```sh
python -B research/complex-u10-t37/verify.py \
  --work /absolute/path/to/new-u10-t37-run \
  --baseline799 /absolute/path/to/completed-frontier799-run \
  --u8-run /absolute/path/to/completed-t37-run
```

The new output must be outside the checkout. By default the driver rebuilds U10 native
programs, verifies the recipe and its mutation controls, recounts local
geometry and all owner roles, emits the controller and finite invoice, and
runs discovery followed by a separately frozen strict replay. It also runs
the two exact moment engines, all-replica fixed-U10 arithmetic bound, original
admission/bit/payload controls, and a final source-to-output binding.

For a completed U10 native replay, `--native-from /absolute/path/to/native`
explicitly reuses it after checking its eight successful stages, mutation
controls, literal word, every frozen native artifact and the complete
mathematical phase review. Only the phase review's elapsed-runtime field is
excluded from semantic comparison. The reused tree is copied byte for byte,
its complete inventory is recorded, and `RESULT.json` discloses the reuse.

PR987 was a draft with unfinished global verification at the cited source
commit. Only its three specified local-recipe files are imported here. This
package does not treat its draft claim or incomplete package manifest as
verification. The original builder and local auditors are the byte-identical
copies already pinned by the PR890/PR942 dependency closure.

## Source edits and scope

`SOURCE-PINS.json` pins the composition's executable sources and nominated
inputs. `vendor/pr987/UPSTREAM.json` pins PR987 commit
`36b76ed29fb30bce784a9b5d81eca0abc9f1f442`. PR942's immutable package is checked
through its existing manifest and predecessor dependency closure.

`prepare.py` records and re-derives every generated adapter. The T37 parent
builder reads the new local profile. The arithmetic checker reads that same
profile. Final binding expects the new rate, κ and U10 native-control inventory.
`nominate_provider.py` replaces the inherited U8 artifact references with the
checked U10 artifacts before discovery freezes the plan; it verifies the
unchanged ports, centres and complete helper-width vector. The original
provider-binding guards then require those new references to match exactly.
The runtime ownership, invoice, moment and assembly algorithms remain the
original T37 adaptations. There is no skipped or relaxed mathematical check.
Inherited receipt status names and descriptive text are retained from those
unchanged algorithms; the bound profiles, program hashes, and top-level
`RESULT.json` identify the U10/T37 composition.

The bound remains conditional on the inherited all-size/compiler,
common-label and physical-realization, precision/tape, analytic-transfer,
and bit H1–H5 assumptions. It is not an unconditional theorem, proof-assistant
formalization, or claim of a practical multiplication speedup.

Prepared with OpenAI Codex assistance. Apache-2.0. See `NOTICE.md` and the
original upstream notices for attribution.
