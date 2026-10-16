# Completed multiplication proof and bounded-call correction

[PROOF.md](PROOF.md) assembles the written fixed-multitape theorem at

```
kappa = 0.001722052684227397319529 - 10^-46 - 10^-70,
time O(n (log n)^(1-kappa)), visited space O(n).
```

The new correction is substantive: a completed Gaussian map being a
contraction does **not** ensure that intermediate Hadamard calls receive
bounded inputs. Section 2 proves and inserts uniform dyadic rescaling
around every Gaussian group, including accuracy lost when the scale is
restored. It costs two scans per group and o(p) extra precision bits.
An exact counterexample rejects the uncorrected inference.

The document substitutes the preceding constructive proofs for the
ordinary-interchange, router, complex-layer and source-transform interfaces,
then carries their costs and errors through CRT and exact recovery. It is
the top-level proof document for this branch. Immutable predecessor notes
retain their historical scope.

This is a **completed written argument, not a whole-machine formal proof
or an independently reviewed result**. The new checks validate the rescaling
seam and exact parameter arithmetic. Earlier Lean files prove specific guard,
recursion and recovery implications, not this entire theorem. The selected
repository result is unchanged.

## Reproduce

With Python 3.12, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/multiplication-proof-completion
```

Normal and optimized runs reproduce [RESULT.json](RESULT.json), including
bounded calls through amplifying identity circuits, perturbed arithmetic,
the error envelope and rejecting controls. They do not execute the
asymptotic multiplier. [VALIDATION.md](VALIDATION.md) records actual checks.

## Open next questions

Independent mathematical review should begin with the quantified theorem,
the call-domain induction in section 2, and the dependency substitutions
in section 3. Formalizing the whole machine additionally requires tape
semantics and analytic matrix constructions. Neither independent review
nor full formalization is represented by a passing finite test.

## Credit

Thomas DiFiore, with substantial OpenAI Codex assistance; no subagents.
Apache-2.0. Retain Douglas Colkitt's reduction lineage, the credited BIT
contributors, Vlado Vojdanovski's PR1673 circuits and schedules, IdeaOuter
and the PR1758 fractional-shift lineage, Chafik Boukhalfa's PR1786 fine
primes, Jeremy Kothe and LeverRank's outer scheduling, and Mason Hale,
Jeremy Diviney and the credited native-supplier predecessors. Source pins
and retained notices are in [SOURCES.json](SOURCES.json).
