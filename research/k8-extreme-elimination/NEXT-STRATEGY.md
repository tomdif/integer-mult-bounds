# Research target: synthesize a rank network instead of another lattice word

This is a proposed direction with an implemented small probe, **not a
paradigm-shifting discovery or an improved kappa**. The current complex supplier
still limits the reference assembly. Improving only its bit partner would not
raise that value.

## A larger search space already present in the bit contract

The original `upstream/build/sections/04-swap.tex`, finite-shear contract,
allows a finite reversible bit circuit whose full endpoint is any wire
permutation rho. Give each gate one arbitrary rational m-by-m matrix M, shared
by all its incident wires. Terminals also have matrices. The exact obligations
are

```
M_out(rho(w)) - M_in(w) = I_m   for every wire w,
s = sum_edges rank_Q(M_head - M_tail) < W*m.
```

These are the paper's existing conditions, not a new relaxation claimed valid
without proof. Matrices need not be projectors, symmetric, commuting, or
nested. Scratch wires count in W and obey the same arbitrary-input endpoint.
The unbatched recurrence has coefficient s/W; a strict inequality certifies
a positive interchange exponent saving under that original interface. It does
not by itself certify the current batched moment, outer assembly, or practical
runtime.

The research proposal is to synthesize the **circuit, final permutation and
matrix labels together**, using characteristic-dependent network coding as a
source of topologies. This leaves the fixed E8 word and its packing ceiling.
Small rank-one changes on random circuits are only a diagnostic starting point;
they do not exploit an actual coding construction.

## What is implemented

`rank_network/` builds 40 finite XOR circuits on 3, 4, 6, 8 or 12 wires, with
identity or cyclic endpoint and matrix size 2 or 3. Each circuit first mixes
with a deterministic random XOR word, then restores by Gaussian elimination;
the cyclic cases append a literal reversible rotation. Input matrices are
variables, so endpoints move coherently rather than being frozen to zero.

The C++ heuristic changes a gate or input matrix by u v^T, with integer entries
bounded by four in absolute value. Twelve million iterations evaluate
7,813,342 nonzero, in-range proposals. None lowers s below W*m. Exact rational
elimination in a separately implemented checker verifies all final circuits,
endpoints and rank sums. A positive control uses two nonsymmetric,
non-idempotent, noncommuting matrices; three corruption controls reject an
incorrect endpoint, deleted gate and false cost. This confirms the checker
supports the enlarged domain; it does not demonstrate an advantage in it.

## Structural seeds worth testing next

The relevant analogy is vector network coding: encode several symbols jointly
and optimize normalized block rank instead of repeating scalar codes.
Bukh and Cox's [fractional Haemers work](https://arxiv.org/abs/1802.00476)
provides exact block-matrix representations where fractionalization beats the
scalar rank bound. Das and Rai's
[characteristic-dependent multiple-unicast constructions](https://arxiv.org/abs/1610.08004)
provide another source of cross-field network patterns. These are established
results in their own models, not integer-multiplication suppliers. No numerical
improvement is transferred from either paper here.

A useful next witness must include all of the following:

1. A literal reversible circuit that routes every independent input, including
   dirty helpers, to a stated permutation.
2. Explicit rational gate matrices and every edge-rank certificate. A modular
   rank drop alone is insufficient.
3. A strict complete rank budget after making encoding/decoding reversible;
   discarded symbols and clean ancillas cannot be treated as free.
4. A corresponding complex supplier improvement or a separately proved way to
   change the limiting complex recurrence, followed by full outer pricing.

## Complex-side version: a distinct proof obligation

For the complex side, arbitrary rational address-shear labels do not directly
replace Fourier/Clifford frames. A possible extension is to allow a change of
representation mixing several register arrays. For a scalar gate G and block
representations D_before,D_after, its physical operation is

```
D_after * (G tensor I) * inverse(D_before).
```

This is an exact change-of-representation identity. Its usefulness depends on
factoring the displayed operation into permitted scalar work and fewer actual
recursive transforms. Cancellation of scalar coefficients alone does not make
that factorization cheap, and arbitrary dirty columns must still be preserved.
Any final representation must reduce to the required independent output
operators. Off-diagonal blocks left over at the end are an error.

The R464 witness is a concrete stress test for such a compiler: ordinary
per-register monotone frames reject it at two gates. A successful block
factorization would have to bypass that obstruction with a complete paid
operator identity. We have not constructed one. Simply descending and
reclimbing is already known to cost extra rank and is not this proposed gain.

The research threshold is a checked primitive or network that changes the
rank budget. Until then, the reference conditional kappa remains
`0.001675809683500501`.
