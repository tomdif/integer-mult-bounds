# Helper 424 extraction after PR2908

**Full release status: `PASS_RELEASE`.** The verified conditional exponent saving is

`κ = 0.001720675131040831119055 - 10^-46 - 10^-70`.

This is 0.264238577% above the requested [PR2745](https://github.com/CrocSwap/integer-mult-bounds/pull/2745), and 0.016088930% above [PR2908](https://github.com/CrocSwap/integer-mult-bounds/pull/2908). It is a conditional exponent saving, not a measured runtime improvement. No unconditional multiplication theorem or global optimality is claimed.

The construction extends Jeremy Diviney's PR2908 paired input/output extraction: retain its restored helper408 and extract helper424 as a second restored helper. Both providers have local profile `{1:2410, 2:638, 3:262, 4:128, 5:26, 8:8}` and inventory `{4:26, 5:2, 7:62, 8:88, 9:230}`. The additional private cleanup buffer is fully charged: **74 buffers, 66,796 physical families**.

## Exact construction and complete cost

For the PR2908 non-target operator M, the new output row and column are

```
alpha = e_424^T + (1/2)e_16^T + e_44^T
y = 2 e_16
E = ker(dot(52, -)) over F2
  = span(256,128,64,36,20,8,2,1)
```

The three terminal gates are `424 += 16/2`, `424 += 44`, `16 -= 2*424`, all at E. The 24 input gates and all coefficients are in `data/TRANSFORM-{base,extra}.json`; the two transforms agree. Exact rational free-operator algebra derives `v=M^-1 y`, `u=alpha M`, and `u v=1`. Their support avoids existing restored helpers, nonzero entrants and operator-correction sources. The derived input change S satisfies `S e_424=v` and `u S=e_424^T`; output change T satisfies `T y=e_424` and `e_424^T T=alpha`. Therefore `T M S` restores both the row and column of helper424. Full target maps and both orientations are separately replayed.

The compensation changes by right multiplication `C S`, and inverse-reverse cleanup is regenerated with both helpers408/424 protected. Relative to PR2908, the per-call local delta is **3 H1 - 2 H2** and width424 changes **9 to 8**. This local delta alone does not establish a higher bound.

The literal T74 allocation uses 666 calls and 271,728 helper roles. Starting with PR2908's fill, the bounded repair makes 409 same-call width exchanges and 571 whole-role relocations. `allocation/MOVES.json` preserves the discovery trace. Every final window, family distinction, capacity and compact prefix is rechecked with the predecessor's independent integer owner engine. The complete paid histogram is

```
{1:1622227, 2:424908, 3:180642, 4:85248, 5:25607,
 6:112, 7:28, 8:5328, 16:2, 24:1, 32:50, 48:26841}.
```

Its rank mass is exactly `65088*74 = 4,816,512`, with 66,304 live families. `MOMENT424.json` brackets the complex root strictly between `0.001720675131040831119055` and `0.001720675131040831119056` using directed rational logarithm/exponential bounds. This uses the credited PR2857 bound implementation; NumPy and floating arithmetic only nominate the owner repair, never certify its moment.

## Verification and reproduction

The complete admission and release passed on 2026-10-16. The [release receipt](evidence/RELEASE-RECEIPT.json), [finite supplier result](evidence/SUPPLIER-RESULT.json), [exact outer ledger](evidence/OUTER-LEDGER.json), and [final claim and comparisons](CLAIM.json) are saved here. All 63 strict outer inequalities, 17 outer rejection controls and 19 retained evidence replays passed. The supplier checks include 119 admission controls, 12 bit controls, 15 controller controls, eight independent owner controls and six geometry controls. The measured prefix is 1,452 bits within the charged 2,048 bits. The final generator also regenerated the verified source manifest and all three admission adapters byte for byte.

The older supplier-only outer witness reports `0.001717719493825701`; the headline above comes from the separately verified modern outer ledger. These are different layers of the same release. Inherited prose in the generated upstream `OUTER-CLAIM.json` mentions historical precision parameters; the actual frozen specification, exact ledger and release receipt use the 24-digit endpoint recorded here.

The exact local replay checks all 632 arbitrary inputs in forward and dual orientations. Its four semantic controls reject a wrong input scale, wrong output cancellation, stale compensation and omission of the new private buffer. Both changed providers pass all five native stages. Saved-owner checks independently reject a missing role and an omitted paid child.

The complete source has an explicit second derivation stage after the preserved PR2908 stage. All retained native, physical, stock, prefix, owner and outer predicates remain. The private-buffer count and namespace endpoints are changed to the actual new ABI; dimension73 and the dimension72 symplectic stock factor remain fixed. Adapter diffs are in `evidence/`.

The first admission attempt was rejected by the private-namespace check: its declared interval still ended at `live+489`. The corrected interval is `[live+416, live+490)` and the coefficient interval is `[live+490, live+492)`. The inherited independent context display also had stale `live+490` total stock; it now uses actual `live+492`. The failed log is retained as `evidence/FIRST-ADMISSION-FAILURE.log`. The candidate words, owners and native receipts did not change in this repair.

Environment: CPython3.12.13, NumPy1.26.4, SciPy1.15.3, SymPy1.14.0, mpmath1.3.0, gmpy2 2.3.2, psutil7.2.2 on macOS. Exact versions and source identities are in the receipts. Run from this worktree with the environment at `/Users/thomasdifiore/beat2745-work/venv/bin/python`, or an equivalent environment.

The following driver exports pinned Git sources into fresh external directories. It requires the Git objects for PR2894, PR2833 and PR2908, which are available in this repository's shared object database. It does not fetch or publish anything.

```sh
python -B research/beat2745-investigation/reproduce_candidate.py \
  --repo . --work /absolute/fresh-helper424-replay
```

By default, the four bootstrap native chains and parent admission are rebuilt. `--retained /absolute/authenticated-preparation` explicitly reuses prior source-bound native and parent evidence. The recorded candidate run reuses this session's **freshly completed** PR2894 bootstrap, and freshly runs both changed providers. The individual complete recipe stages were executed; the new convenience driver was additionally preflighted with `--dry-run` rather than claiming a second full run of that wrapper.

For the quick saved-owner/moment replay, first use `--dry-run` to export the predecessor into a fresh directory, then:

```sh
python -B research/beat2745-investigation/check_saved_candidate.py \
  --predecessor /absolute/preflight-directory/pr2908 \
  --bounds-package /absolute/preflight-directory/pr2894
```

The complete local run directories and logs are retained under `/Users/thomasdifiore/beat2745-work/`. No selected result has been changed and no PR or discussion message has been published.

## Sources, credit, and scope

- PR2745: `4f485de05544884fa0f2edf6063bb9259decad30`, the user's requested comparison.
- Jeremy Kothe, PR2894: `18d03c447886895ef9abf888398178e0428533ca`, and PR2833: `e9307b48d7d1b690939935ecef0f8e524e6d92f4`.
- Jeremy Diviney, PR2908: `51309592971e3b5be935599eed2a95404dc7781e`: paired input/output extraction, first helper408, local checker, literal owner fill and complete admission adapters. This session applies that method to helper424; it does not claim the extraction method itself.
- Yiyang Lu / Lyy-iiis: PR2857 shared kernels, exact moment bounds, native and integration tooling; Dugongue: PR2863 packing and earlier block-norm work; Philippe Van Velzen: PR2853 and earlier helper work; Marius-Paul Dumitrean: PR2843/2802 lineage; Tekalign and all retained owner, native, compiler and outer authors. Original notices remain in exported source packages.

Prepared for Thomas DiFiore with substantial OpenAI Codex assistance, without delegated agents. No independent human review, formal-kernel theorem proof, global priority or latest-record claim is made. The inherited all-size/compiler, bit-supplier, precision/tape and analytic-transfer hypotheses remain.

Earlier session checks are retained separately. A full cold reproduction of PR2894 passed in 665.33 seconds. `check_packing.py` independently reconstructs an exact 1,163-pattern packing certificate with 11 tight patterns, agreeing with Discussion2612's prior reported result. `check_kernel.py` independently replays the six existing quartets: the restricted 24-helper target-response matrix has rank18 and exactly the six already-used cancellation directions. These are fixed-model screens, not barriers to the subsequent two-sided extraction. The bounded symmetric screen reproduced helper408, accepted helper424 in both providers, and rejected the analogous helper440 triple for lack of a containing terminal hyperplane.

## Open next questions

1. Can the new inventory be packed more tightly? The current fill is feasible and fully priced, but no optimum is claimed. Compare its exact relaxation with the actual fill before expanding any search.
2. Does another paired extraction survive after helpers408/424? The analogous helper440 triple fails the terminal-frame test; a different row/column combination is needed. Require exact two-sided identities, all dirty restoration, an additional charged buffer, actual owners and full admission before claiming another gain.
