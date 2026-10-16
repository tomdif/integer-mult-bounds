# Whole-machine Lean formalization: unfinished

The exact whole-machine proposition is now recorded in
[`Target.lean`](Target.lean), including the original exponent saving
`0.001722052684227397319529 - 10^-46 - 10^-70`, exact binary multiplication,
a fixed finite transition table, and linear **visited** space. There is no
theorem proving `WholeMachine.Target.Complete` in this package.

This successor to
[`multiplication-proof-completion`](../multiplication-proof-completion/README.md)
formalizes supporting parts of its written argument. It does not promote the
written theorem to a formally verified multiplication result.

## What is proved

| File | Checked content | Remaining instantiation |
|---|---|---|
| `Target.lean` | Literal head-local tape semantics; run concatenation; first-halting-time reduction; visited-region composition; unvisited cells cannot change; binary value bound | A multiplier transition table satisfying `Complete` |
| `Composition.lean` | An actual finite-table sequential compiler; one charged handoff; exact run and visited-region identities; composition from arbitrary halting witnesses | Concrete primitive and outer programs, including loops, reusable scratch and recursion |
| `BoundedCalls.lean` | Exact propagated-error sum; first-failure induction; `s=E+4`, `R=Q+s+2E+clog₂(m)+3`; restored-scale and rounding bounds | The actual Gaussian interval envelopes and stage implementations |
| `Intervals.lean` | Invertible prefixes and inverse prefixes imply interval bound `K²`; singular augmented Horner intervals have bound `1+lL` | Bounds for the actual Gaussian matrices, capped circuits and tensor layout |
| `Parameters.lean` | Exact rational parameter order, guard inequalities and all nine cost powers, with common slack `10^-47` | Operation counts for the actual programs |
| `Asymptotics.lean` | Every fixed real power of `log p` is absorbed by the strict cost gap; the stated real guard envelope is `o(p)` | Integer sizing, computable envelopes, concrete running-time estimates |
| `RecoveryPipeline.lean` | Bounded-domain approximate CRT/Fourier/product/inverse-CRT assembly; error `(4S+1)e`; exact coordinate rounding via the predecessor's recovery lemma | Actual transform contracts and exact convolution identities |
| `ProofCounterexamples.lean` | A completed identity with an out-of-domain internal call; a finite machine that erases its output but has visited four cells | These refute shortcuts; neither constructs a multiplier |

The numerical results are universally quantified proofs, not finite fixtures.
Their displayed operator, contraction, approximation and exact-identity
hypotheses remain hypotheses. They are not supplied by reading the prose proof
or by the machine-composition theorems.

`Composition.sequence` combines control states by finite disjoint union and
preserves the same tapes and alphabet. Its handoff reads and rewrites the
scanned symbols without moving any head. `compose_halting_runs` proves both
the transition bound and the visited-region inclusion. Its cardinality bound
alone is insufficient to prove linear space over a growing number of stages:
the actual algorithm still needs a reusable-region invariant.

## Verification

The project pins Lean 4.32.2 and mathlib commit
`905b95818eb32af7874a58b427f50c1711a5e96c`. The verifier creates a fresh project
from captured source bytes, checks every dependency's source revision and
tracked cleanliness, builds `Audit`, audits all declarations in the package's
namespace, and runs the official `leanchecker --fresh --verbose Audit`.
Only `propext`, `Classical.choice`, and `Quot.sound` are allowed. The source
and compiled artifact hashes are retained with the result.

Five negative controls must fail mathematically: wrong κ; completed-map
normalization used as a call-domain bound; omitted restore-scale precision;
erased tape confused with unvisited tape; and an uncharged handoff.

```sh
python3.12 research/whole-machine-lean/verify_kernel.py \
  --lake /ABS/lean-4.32.2/bin/lake \
  --packages /ABS/pinned-mathlib-packages \
  --work /ABS/FRESH-WORK-DIRECTORY \
  --out /ABS/NEW-RESULT.json \
  --independent /ABS/lean4lean
```

`--independent` records a separate raw Lean4Lean replay. Failure or toolchain
incompatibility is recorded as failure, never silently replaced by official
checking. This harness does not perform the separate reviewed-challenge
strict acceptance workflow. Its `strict_acceptance` and
`whole_machine_proved` fields are always false. See `VALIDATION.md` for the
actual outcomes; a scoped passing receipt does not establish `Complete`.

## Open next questions

1. **Instantiate the selected BIT and complex suppliers as machines.** This
   is needed before their local algebra can imply time or visited-space
   bounds. Start with the `TapeStack.lean` instruction semantics in
   `machine-transfer-verification`, then encode the pinned native words and
   prove whole-call simulations. Current blockers are all-size dispatch,
   recursion, common labels, exact root-grid arithmetic and actual costs.
2. **Formalize the Gaussian construction and source transforms.** Start by
   proving the row/inverse bounds in `fine-prime-halo-closure`, then instantiate
   the prefix and interval hypotheses in `scaled_schedule`. Prime supply,
   capped circuits, coefficient generation, finite cores, boundary solves and
   physical hosting still require formal developments.
3. **Connect exact transform algebra to recovery and tape output.** Supply
   the pipeline's `hscaled` and `hexact`, prove no cyclic wrap, implement
   integer rounding and the sequential carry pass, and relate the returned
   cells to `Target.output`.
4. **Prove the total resource invariant.** Derive the nine cost rows from
   actual runs, bind record volume to input length, and prove a common linear
   visited region across reusable stages and parked recursive ancestors.
5. **Complete independent acceptance.** A compatible, qualifying Lean4Lean
   checker and the reviewed exact-theorem challenge are needed in addition
   to official checking. Neither a failed replay nor this partial package
   satisfies that requirement.

## External comparison and attribution

The independent project
[`platypii/integer-mult-bounds-lean`](https://github.com/platypii/integer-mult-bounds-lean/tree/de074bf95a2211efefcac642ec66a952e127ad9c)
was inspected at `de074bf95a2211efefcac642ec66a952e127ad9c`.
Its public `MathlibTM2.mulInTime` states saving `2^-34` and its public
`MulInTime` statement has no linear-space conjunct. Its sharper-bound work
plan explicitly leaves the selected suppliers and Gaussian machinery open.
It is useful prior work, but it does not prove this branch's target. Its full
proof was not rebuilt here, and no theorem from it is imported into this
package. The explicit finite-table model was informed by its `Machine.lean`
and by this repository's retained head-local tape model; the new model adds
the visited-space target and the original exact κ.

The bounded-call construction comes from
`multiplication-proof-completion/PROOF.md` §2; the numerical assembly comes
from §6. `Recovery.lean` is copied unchanged from
`fine-prime-transform-assembly` into the fresh build. Earlier source and
contributor attribution remains in those immutable packages. New work by
Thomas DiFiore with substantial OpenAI Codex assistance. No independent
reviewer or subagent participated. Apache-2.0, as in this repository.
