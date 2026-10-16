# Four terminal-frame refits on PR2917

**Complete release: `PASS_RELEASE`.** The verified conditional exponent saving is

`κ = 0.001722052684227397319529 - 10^-46 - 10^-70`.

This is **0.080058877%** above the previous local helper408/424 result, **0.344509001%** above the user's requested [PR2745](https://github.com/CrocSwap/integer-mult-bounds/pull/2745), and **0.026954001%** above [Mason Hale's PR2917](https://github.com/CrocSwap/integer-mult-bounds/pull/2917) at `224bd5e56041c40078ff6b5fa7393733a215de5c`. Exact comparisons are in `COMPARISONS.json`. These percentages describe the exponent-saving parameter, not measured runtime.

The immediate predecessor is retained byte for byte in `vendor/pr2917/`, with its original manifest and attribution. This package adds four legal terminal-frame refits to its ten extracted helpers. Its six frame-assisted directions, nine-stage composition, literal owner allocation and original integration belong to Mason Hale. Jeremy Diviney's PR2908 supplies the paired-extraction method and immediate ancestor. No selected result is changed.

## The change and its complete cost

For helpers408,424,428 and412, the parent executes two additions to the same destination in a rank8 frame. Their sources are different from the destination, so the additions commute. One source and the destination already share a rank7 frame. Execute that addition first in this smaller frame, then the other addition in the original rank8 frame. For428 and412, the preceding sign scale also executes in the register's existing rank7 frame; its coefficient and position are unchanged.

The declared pairs are:

| Helper | First source in common rank7 frame | Other source | Rank8 normal |
| ---: | ---: | ---: | ---: |
| 408 | 105 | 42 | 52 |
| 424 | 44 | 16 | 52 |
| 428 | 430 | 416 | 76 |
| 412 | 414 | 400 | 127 |

The entire terminal scalar operator is exactly unchanged. Final endpoint frames remain rank8, and compensation, arbitrary-input contract, all helper widths, existing extractions and literal allocation remain unchanged. This is not a rank7 endpoint extraction and does not contradict the fixed-endpoint obstruction in PR2918.

Each refit replaces two paid rank-one steps by one rank-two step. Thus the complete per-call profile changes by **`-8 H1 + 4 H2`** to

```
{1:2408, 2:644, 3:280, 4:110, 5:26, 8:8}.
```

The fixed inventory remains `{4:26, 5:2, 7:62, 8:96, 9:222}`. Inverse-reverse cleanup is regenerated from the actual new word. The unchanged physical invoice still charges **82 private zero buffers** and **66,804 physical families**:

`66,304 live + 408 helpers + 8 centres + 82 buffers + 2 scratch`.

All 666 calls and 271,728 helper roles are retained. The complete paid profile is

```
{1:1620396, 2:428904, 3:191980, 4:73260, 5:24951,
 6:167, 7:45, 8:5328, 24:1, 32:207, 48:26958}.
```

Its rank mass is exactly `65088*74 = 4,816,512`. The saved independent owner check rederives every role's window, physical-family distinction, capacity, offset and compact prefix. `MOMENT.json` brackets the complex root strictly between `0.001722052684227397319529` and `0.001722052684227397319530` using PR2857's directed rational logarithm/exponential bounds. Floating arithmetic only nominates the bracket.

## Verification and reproduction

`terminal_refit.py` authenticates each complete old gate block, applies only the declared commuting changes, rederives frames and cleanup, and compares the entire terminal scalar operator independently. The inherited local auditor checks all 632 arbitrary inputs in forward and dual orientations for both providers. Four controls reject a wrong coefficient, a noncommuting order, an understated paid profile and an illegal smaller frame. The saved-owner replay separately rejects a missing role and an omitted paid child.

`build.py` preserves PR2917's complete reconstruction and local review, then appends this refit as a separate source-bound stage. Source adapters change only the new source identity and file count. The 82-buffer block-norm checker is unchanged. Both final providers pass fresh five-stage native runs. The complete [release receipt](evidence/RELEASE-RECEIPT.json), [supplier result](evidence/SUPPLIER-RESULT.json) and [outer ledger](evidence/OUTER-LEDGER.json) also pass: 63 strict outer inequalities, 17 outer rejection controls and 19 retained exact replays. Supplier checks reject 119 admission, 12 bit, 15 controller, eight independent-owner and six geometry mutants. The measured prefix is 1,456 bits within the charged 2,048 bits. The headline uses the modern outer ledger; the separately recorded supplier-only outer witness has a different kappa.

Run from a repository containing the exact PR2894, PR2833 and PR2908 Git objects:

```sh
python3.12 -B research/paired-terminal-refit/reproduce.py \
  --repo . --work /absolute/fresh-terminal-refit-run
```

The PR2917 source is vendored and authenticated at manifest `55c46ddf2e3edc87dfe1ba3320947466d36980d457eb37f6cd6fba341dae0192`. The driver makes no network requests. Default execution rebuilds the retained bootstrap; `--retained /absolute/authenticated-preparation` explicitly reuses its complete source/cache/parent receipts. The recorded run reuses the preceding session's independently cold-replayed PR2894 bootstrap and freshly runs both changed providers. Reused evidence is not described as freshly rerun.

The complete single-command replay also passed in a separate detached checkout: [replay result](evidence/CLEAN-REPLAY-RESULT.json), [commands](evidence/CLEAN-REPLAY-RECIPE.json), [stage receipts](evidence/CLEAN-REPLAY-STAGES.json), and [code/data identity](evidence/CLEAN-REPLAY-INPUTS.json). Every stage exited zero; fresh native runs and complete admission reproduced the same exact kappa and 645-file source identity. This replay used the explicit `--retained` option described above.

Environment: CPython3.12.13, NumPy1.26.4, SciPy1.15.3, SymPy1.14.0, mpmath1.3.0, gmpy2 2.3.2, psutil7.2.2 on macOS. Exact versions, commands and identities are in the receipts. A dry run only checks the pinned export and writes the full recipe.

## Credit and scope

Mason Hale/PR2917; Jeremy Diviney/PR2908; Jeremy Kothe/PR2894 and2833; Yiyang Lu/PR2857; Dugongue's packing; Marius-Paul Dumitrean's retired-helper work; Philippe Van Velzen's cost work; Tekalign's owner/admission checks; icekylinx's free-operator auditor; and all retained native, compiler and outer authors. Their notices remain unchanged in the vendored package. This terminal-frame refinement was prepared for Thomas DiFiore with substantial OpenAI Codex assistance, without delegated agents.

The earlier [four-helper branch](../helper424-packing/README.md) separately passed full release at κ≈0.001721778811275. This package transfers its frame-staging idea to PR2917, which appeared during the session. No claim of global priority, packing optimality, independent human review, formal-kernel proof or unconditional multiplication theorem is made. All inherited all-size/compiler, whole-call hosting, precision/tape, exact-recovery, bit-supplier and analytic-transfer assumptions remain. This package is prepared for the user-authorized research-branch push. The selected result is unchanged; local-only notes inside immutable predecessors describe their historical state.

## Open next questions

1. Improve the unchanged literal PR2917 allocation. Start with its actual chronological windows and compare a certified packing relaxation; the paid local saving is already fully accounted for here.
2. Explore different frame-staged output trees or earlier scalar contracts on remaining directions. A legal local identity alone is insufficient: require the complete native, owner, stock, prefix and outer checks before another bound.
