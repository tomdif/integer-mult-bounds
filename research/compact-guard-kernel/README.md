# Kernel proof of compact guards and exceptional-address repair

[Guard.lean](Guard.lean) proves the dirty-control arithmetic, packed bounds,
exceptional-set estimate, and selective repair used by the support router in
the terminal-refit proof chain. It contains 18 theorems and a controlled-addition
equivalence, checked with standard Lean axioms only. [PROOF.md](PROOF.md) binds
those statements to the retained 22-instruction word and its written tape-cost
contract.

The important intermediate invariant is that a source load may raise a
control digit to B-1. The second F word is still valid because it reads that
digit's parity; it does not increment it. Scratch digits retain the stricter
overflow restriction. Both calls restore dirty work, and sources inside other
guards remain valid. This sharpens the proof without changing the entry guard
or the algorithm.

The repair proof derives bad-set invariance from the raw and ideal permutations.
It proves that `T ∘ S^-1` sends each bad record to exactly one bad slot, and
that selective repair realizes T on every input. The density bound is at most
`r(2/B+4B/M)`, hence `3/(64p^3)` when `r<=p`, `B>=64p^4`, `M>=4B^2`.

Source-bound finite checks cover all **69,632 addresses** in two layouts,
**3,072** states with unequal gaps and cross-guard sources, and five explicit
counterexamples to weakened premises. Four false Lean statements are also
required to fail. These checks do not execute a new physical recursive caller.

This is a scoped formal result inside the B/C dependency chain of
[the outer candidate](../fine-prime-transform-assembly/DEPENDENCIES.md).
The whole multiplier, ordinary interchange machine, native dispatch, and
analytic transform are not formalized by this package. No new kappa,
selected-frontier change, or independent review is claimed.

## Reproduce

From the repository root, using Python 3.12 and its standard library:

```sh
python3.12 -B scripts/research_package.py --package research/compact-guard-kernel
```

The registered normal and optimized runs use fresh bytecode namespaces and
compare the complete [RESULT.json](RESULT.json). Sources are authenticated
before imports. They also authenticate the retained kernel receipt against
the current Lean source; they do not launch a Lean build implicitly.

For a fresh Lean 4.32.2 build with the exact cached dependencies listed in
`lean/lake-manifest.json`:

```sh
python3.12 -B research/compact-guard-kernel/verify_kernel.py \
  --lake /path/to/lean-4.32.2/bin/lake \
  --packages /path/to/cached/.lake/packages \
  --work /absolute/new/work --out /absolute/new/KERNEL.json
```

The new work directory must not exist. [KERNEL.json](KERNEL.json) records the
actual fresh build, dependency revisions, source and log hashes, all axiom
reports and the four mathematical rejection controls. The pinned input files
and source provenance are in [SOURCES.json](SOURCES.json).

## Open next questions

The remaining machine refinement would connect this address-level word and
the sequential repair loops to the encoded tape semantics, with measured
descriptor work and delimiter locality. A concrete next step is to formalize
one complete controlled rotation and stable radix pass, then compose their
contracts with this repair theorem. The current kernel does not model tape
states or costs.

The larger proof candidate also needs independent mathematical review of B,
C and the outer composition together. A feasible first review compares the
exact interfaces in the linked dependency inventory with their implementations;
finite tests and the present scoped kernel proof do not supply that review.
Structured questions and the upstream/overlap checkpoint are in [TASK.json](TASK.json).

## Credit

Prepared for Thomas DiFiore with substantial OpenAI Codex assistance, without
subagents or independent human review. Apache-2.0. Douglas Colkitt supplied
the retained dirty compact word and original guard/repair method. Vlado
Vojdanovski's PR1673 lineage supplied the sparse support construction; Jose
Manuel supplied the sequential compact interpreter and ordinary/compact
integration lineage. The prior fork packages retain the terminal-refit and
ordinary-supplier contributors. This package credits those algorithms and
adds the stated formal implications and source-bound checks.
