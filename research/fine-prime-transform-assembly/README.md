# Fine-prime transform assembly and exact recovery

**Written outer composition theorem, relative to the two preceding physical
primitive proofs.** This completes the outer proof candidate left open by
`refit-physical-dispatch` and `fine-prime-halo-closure`. It does not turn the
finite certificate into a formal verification of the entire multiplier.

[TRANSFER.md](TRANSFER.md) joins the constructed source transform to the
logarithmic CRT layout and exact integer recovery, at

```
kappa = 0.001722052684227397319529 - 10^-46 - 10^-70.
```

[CORE.md](CORE.md) removes the terminal cyclic-prefix premise: fast solves
use finite cores and whole separator pivots, while actual wrapped input
faces use the explicitly priced polynomial inverse. The face proof applies
to varying coefficients. [PRECISION.md](PRECISION.md) binds capped circuits
and Schur pages to the same rational matrix, accounts for setup underflow,
and proves the sufficient online guard. The final coefficient error is
at most `80*2^(-6b)<1/4`, with inverse CRT performed before rounding.

Read [DEPENDENCIES.md](DEPENDENCIES.md) for the exact logical boundary. The
ordinary bit interchange and terminal-refit complex layer remain lower-level
written theorem dependencies. Their correctness, and this new composition,
require mathematical scrutiny. No independent human review, executable
all-size fast multiplier, practical cutoff, or whole-machine formal proof
is claimed; the selected repository frontier is unchanged.

## Reproduce

With Python 3.12, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/fine-prime-transform-assembly
```

The registered normal and optimized runs check the entire deterministic
[RESULT.json](RESULT.json), source pins and authenticated retained notes.
The tests include 1,920 exact variable-coefficient tensor outputs, 4,752
counted halo copies, whole-group Schur identities, eight exact cyclotomic
Fourier/CRT recovery cases, and eight rejecting controls. Some recovery
cases inject dyadic errors at every completed interface. These are exact
finite tests, not an implementation of the full fast Gaussian compiler.

[Recovery.lean](Recovery.lean) kernel-checks five general error/rounding
implications. [KERNEL.json](KERNEL.json) records the fresh build and three
false-statement controls. A separate fresh replay uses:

```sh
python3.12 -I -B research/fine-prime-transform-assembly/verify_kernel.py \
  --lake /path/to/lean-4.32.2/bin/lake \
  --packages /path/to/pinned/mathlib/packages \
  --work /fresh/temporary/directory --out /fresh/receipt.json
```

The dependency revisions are fixed by `lean/lake-manifest.json`. The final
Lean theorem assumes the approximation-error premise proved in the written
assembly; it does not formalize the source transform or its machine cost.

## Open next questions

Independently audit the complete dependency chain, beginning with the two
physical primitive contracts, CORE section 5's prefix geometry, and
PRECISION sections 3--5's circuit/page composition. A full formalization
would require analytic matrix lemmas and tape semantics. This is a review
and formalization task; a new finite endpoint search would not resolve it.

## Credit

Thomas DiFiore, with substantial OpenAI Codex assistance; no subagents.
Apache-2.0. Retain Douglas Colkitt's supplier/reduction lineage, Vlado
Vojdanovski's PR1673 constructions, IdeaOuter and the PR1758 fractional-shift
lineage, Chafik Boukhalfa's PR1786 fine-prime mechanism, Jeremy Kothe and
LeverRank's outer scheduling lineage, and Mason Hale/Jeremy Diviney's
immediate finite-supplier predecessors. Ten unmodified proof/notice files
are source-manifest-bound in [REFERENCES.json](REFERENCES.json); their
inclusion is attribution and review support, not independent validation.
