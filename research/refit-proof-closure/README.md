# Refit proof progress: support routing, weighted induction and CRT

**Partial proof completion; the full multiplication theorem remains unproved
by this package.** This continues the explicit request to finish the proof of
the paired-terminal refit's conditional saving
`0.001722052684227397319529 - 10^-46 - 10^-70`. It does not change that saving,
the selected frontier, or the immutable predecessor packages.

Three concrete additions replace previously missing arguments:

* [ROUTER.md](ROUTER.md) gives an explicit support/full-address routing plan,
  with fixed reservoirs, current-position coloring and an untouched long
  suffix. The sparse shear is connected to the actual retained binary backend.
  The all-size cost is a written composition using that backend's source proof.
* [RECURRENCE.md](RECURRENCE.md) proves the actual histogram's time bound
  directly down to constant-width leaves. An input-dependent stopping exponent
  is unnecessary. The generic weighted strong induction is checked in Lean.
* [CRT.md](CRT.md) identifies the retained `Vd` scan cost, which exceeds the
  claimed budget, and proves a logarithmic block factorization that can replace
  it. Its conditional implementation uses retained-label Fourier sandwiches,
  including the frequency units and final normalization. Its required uniform
  source-transform contract is stated explicitly, not asserted as proved.

The CRT map is not a permutation of binary coordinate positions; the two
routing results have different domains. The repaired CRT is a numerical map
on zero-padded valid coefficient arrays. Its inverse must precede final integer
rounding. These distinctions prevent two otherwise tempting incorrect joins.

## Evidence and reproduction

The standard-library checks cover 3,588 complete CRT addresses and their
intermediate blocks, 4,599 exact cyclotomic Fourier sandwich entries, 2,310
conditional phases, 16 generated coordinate plans up to 4,096 address bits,
and 133,376 exhaustive sparse addresses including bad classes and inactive
dirty digits. Another 4,000 deterministic sampled/constructed states exercise
unequal gaps, base-eight controls and inactive high digits.
Formal bit variables check each generated plan on all its possible addresses;
this does not execute its exponentially large payload. A separate 256-record
payload fixture reaches all 12 ordinary calls through the binary backend,
with decoding shortcuts disabled and work cleared. Those small calls take
the elementary branch; they do not measure the asymptotic saving.

Eleven Python rejection controls cover chronology, transformed controls,
Fourier labels, normalization, reservoir placement, repair and sparse domains.
Normal and optimized verification must agree. [Closure.lean](Closure.lean)
contains five scoped algebraic/arithmetic theorems, with only the standard
Lean axioms; three false-statement controls must fail. The Fourier construction,
physical tape semantics and full multiplication theorem are not formalized.

From the repository root, using Python 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/refit-proof-closure
```

The registered runner authenticates inputs and uses fresh bytecode namespaces
for both normal and `-O` commands. [SOURCES.json](SOURCES.json) pins all 85
predecessor inputs; [evidence](evidence) records the scoped checks. A fresh
kernel replay requires the exact dependencies in `lean/lake-manifest.json`:

```sh
python3.12 -B research/refit-proof-closure/verify_kernel.py \
  --lake /path/to/lean-4.32.2/bin/lake \
  --packages /path/to/cached/.lake/packages \
  --work /absolute/fresh/work --out /absolute/fresh/KERNEL.json
```

[KERNEL.json](KERNEL.json) records the executed replay. No `sorry`, admitted
machine theorem, or custom mathematical axiom is used. A passing receipt
establishes only its stated scope.

## Open next questions

1. **Complete physical complex dispatch.** Bind the actual 2,222-event global
   caller, owner selection/scatter, cover enumeration, recursive parking and
   every native opcode to permanent tape roles. The first step is one whole
   current native invocation with its real owner charts and return boundary.
   The source-bound event/height ledger and new routing plan do not yet supply
   that whole-program refinement. Without it, the recurrence remains an
   implication whose node-cost premise must be established.
2. **Uniform fine-prime source transform.** Prove contract T in CRT.md from
   the actual fine-prime, gauge-free and union-schedule routines, uniformly on
   d/2 target axes with complete spectator rows and O(p) working precision.
   Extract the source-transform call graph before introducing the outer CRT,
   then charge every Gaussian, halo, diagonal and synthetic-transform pass.
   This is needed both by the original outer reduction and by the new CRT
   implementation; small dense FFT tests cannot establish it. The revised
   power-of-two choice of d and inverse-before-rounding order must be included
   in a complete integration replay and exact recovery proof.

These are substantive remaining obligations. The result is not being labeled
an unconditional or fully formalized multiplication theorem.

## Credit

Prepared for Thomas DiFiore with substantial OpenAI Codex assistance, without
subagents. Apache-2.0. Retain the full supplier credit in
[the paired-terminal refit](../paired-terminal-refit/README.md) and
[recursive realization](../recursive-refit-realization/README.md).
Vlado Vojdanovski supplied the sparse support/shear and deferred-layout
lineage; Jose Manuel supplied the compact interpreter and physical ordinary
interfaces; David Arias and Nick Petalas supplied their caller/wrapper
predecessors. Douglas Colkitt supplied the retained CRT and Fourier assembly.
The Gaussian reduction retains David Harvey and Joris van der Hoeven's work.
The new CRT block factorization, routing plan and direct induction do not
reattribute any of those results. No independent human review is claimed.
