# Quantified dirty-control and repair proof

This successor makes the intermediate invariant in
`refit-proof-closure/ROUTER.md` section 3 explicit and formalizes its arithmetic
and permutation implications. It changes neither that package nor the raw
algorithm. In particular, it does not identify a counterexample to its stated
entry guard. The distinction below is necessary when applying that guard
inside the two-call construction.

## 1. Exact statement and source interpretation

Use complete binary fields in the physical order `(u,t,y,b)`, followed by an
untouched record. The three compact fields have equal width H. Let G,K>=1,
B=2^G, M=2^(K-1), and 1<=r with rG<=H. The active target
positions j_0<...<j_(r-1) in y have disjoint intervals `[j_i,j_i+K)`.
Sources s_i are distinct positions of y outside the set of targets. A source
may lie inside any guard. Gaps between guards and all inactive compact digits
may be arbitrary. For the density statement suppose M>=4B.

Write u_i,t_i for the low r base-B digits of u,t, and

    e_i = bit(y,j_i),
    h_i = floor(y/2^(j_i+1)) mod M.

The entry good predicate is exactly

    0 <= u_i,t_i <= B-2,
    2B <= h_i < M-2B                 for every i.

Let S be the actual 22-instruction word from `SparseWord.operations`, with
12 ordinary equal-H exchanges and ten controlled rotations. Let T XOR each
bit s_i into j_i, restoring every other coordinate. Then:

1. S equals T on every good address, for arbitrary dirty compact fields.
2. S and T preserve the good and bad sets. S is a permutation on all
   addresses, even where the guarded arithmetic interpretation fails.
3. At a current address z, the selective correction
   `z` if good, otherwise `T(S^-1(z))`, is a permutation and, after S,
   equals T everywhere. Its bad keys fill precisely the bad holes.
4. The bad fraction is exactly `1-a^r`, where
   `a=((B-1)/B)^2*(M-4B)/M`, and is at most `r*(2/B+4B/M)`.

The finite source-binding test compares the retained operation list with an
independent literal transcription. The written interpretation below binds
its general integer offsets to the formal expressions. Lean checks the
quantified expressions and repair implication; it does not parse or certify
the Python program, a tape interpreter, or the ordinary interchange supplier.

## 2. One F word and the maximum transient control

Fix one active guard and temporarily write `y=2h+e`. With read-only control
bit z, the source executes

    y1 = (y + 2zt) mod (2M),
    t1 = (t + (y1 mod 2)) mod B,
    y2 = (y1 + z(1-2t1)) mod (2M),
    t2 = (t1 - ((y2 mod 2 + z) mod 2)) mod B.

The last expression is the selected bit of `y2 XOR z`, exactly the source's
`original_compact` offset. Each late load/unload uses two ordinary exchanges
with b. Swapping, adding to the back, and swapping back performs the intended
front addition and restores an arbitrary dirty b. The `shuttle` theorem is
polymorphic in the additive type, so it also applies modulo the whole field.

`guardBounds` proves every intermediate y value belongs to `[0,2M)` and
`t+e` belongs to `[0,B)`. Thus the modular reductions do not change the
displayed signed arithmetic. In particular `y1 mod 2=e`, and

    y2 = 2h+e+z(1-2e) = 2h+(e+z mod 2),
    t2 = t.

This is `flipCorrect`, including all four modular operations. It only needs
`z` to be a bit. **It imposes no upper restriction on the compact digit
whose parity supplies z.** This is the sharpened intermediate invariant.

The complete late-source routine is `F; load x into u; F; unload x`, where
x is the selected source bit. At entry `u<=B-2`, so `u+x<=B-1`; loading may
reach B-1, as `loadedControl` explicitly allows. The second F still satisfies
`flipCorrect`. Both calls restore t. Their target parities compose as

    ((e + u mod 2) mod 2 + (u+x) mod 2) mod 2 = (e+x) mod 2.

`parityCancellation` proves this identity for all integers; `pairedFlipCorrect`
joins it to both exact F calls. Subtracting x restores u. Applying the original
entry predicate to the temporarily loaded u would be an invalid proof step;
it is unnecessary for the actual algorithm.

## 3. Packing, source stability, and arbitrary spectators

Partition y into the disjoint active K-bit guards and intervening untouched
bit fields. Partition u,t into the active G-bit digits and untouched high
digits. This is a mixed-radix representation; its radices need not be equal.
`packBounds` proves that valid digits encode an integer strictly below the
product of their radices. `packedNoWrap` therefore removes a whole-field
modular reduction when the resulting digits remain valid.

`packedUpdates` is the exact identity taking a sum of signed digit offsets
to the packed updated digits. In each F stage, section 2 supplies valid
updated guard and scratch digits. During the u load, `loadedControl` does
the same. Combining these statements proves that simultaneous additions
cause no carry into another guard, gap, or inactive high digit. It also
justifies unpacking the low target bits at the following load. The last
unload returns each t_i and u_i to its original range. Unequal guard gaps
require no extra assumption.

A completed F changes only the e_i bits: every h_i and every outside bit
is fixed. The source set avoids the targets, so all selected source bits
can be expressed as a function of the h_i and the untouched outside bits.
`sourcePreserved` proves this for an arbitrary such function, using the
actual quotient `(2h+e)/2=h`. Sources in another active guard are therefore
unchanged at both completed F boundaries and both source loads. They need
not be unchanged at every intermediate rotation, where they are not read
as source controls.

The compact fields, outside y bits, and following record are restored
pointwise. Consequently this is an address identity for arbitrary payload,
including correlated dirty coefficients; it is not a statement about an
average input or a special zero-filled reservoir.

## 4. Why selective repair is valid

Each raw rotation targets a field absent from its control list. For each
fixed control fibre it is addition in a finite additive group, with inverse
subtraction. `controlledAdd` constructs that equivalence, including its two
inverse proofs. Ordinary exchanges are equivalences too. Hence S is a
bijection independently of any guard. Its inverse reverses the instruction
order and evaluates each offset at that inverse step's current controls.

T is an involution: its sources and targets are disjoint. It only toggles
target low bits, which do not appear in the good predicate, so it preserves
goodness in both directions. Given these facts and S=T on good addresses,
`rawPreservesGood` derives the corresponding two-sided invariance for S.
The reverse implication uses injectivity: a bad address cannot enter a
good slot already occupied by the image of a good address.

`repairEquals` proves that the selective postprocessing equals `T ∘ S^-1`
on **all current addresses**, including good ones. `repairCorrect` gives
`repair(S(x))=T(x)`. `repairBijective` proves that correction is bijective
and preserves goodness, so its restriction is a bijection of the bad set.
This proves the exact key/hole correspondence used by sequential sorting
and reinsertion, rather than assuming it from finite examples.

Two explicit three-point counterexamples show why a forward raw map cannot
replace its inverse, and why agreement on good addresses without T-invariance
does not suffice. These are distinct from the arithmetic guard counterexamples.

## 5. Density and the physical cost implication

For one guard, the complete address rectangle gives independent ranges of
sizes B, B, M and 2 for u_i,t_i,h_i,e_i. Exactly
`(B-1)^2*(M-4B)*2` choices are good. All other coordinates are unrestricted.
Disjoint guards and compact digits therefore give the exact good fraction
`a^r`. Source values may be correlated with the guard bits; no source value
enters the good predicate or this counting argument.

`singleGuardDensity`, `productFailure`, and `allGuardDensity` prove

    1-a^r <= r(2/B+4B/M).

For the actual router, `G=4 ceil(log2 p)+6`, `K=128G`. Thus
`B>=64p^4` and `M=2^(128G-1)>=4B^2`. If r<=p,
`exceptionalDensity` proves the explicit bound `3/(64p^3)`.
For the stated n=O(p) interface, r<=ceil(n/K)<=p eventually; alternatively
r<=c p gives the same asymptotic estimate with constant c.

Retain the earlier physical implementation contract: rotations have linear
scan cost after polynomial descriptor preparation; the 12 ordinary H-bit
exchanges use B1; the actual final `ell=ceil(log2 p)^2` bits are an untouched
complete suffix. Let R include this full suffix fibre. Then R grows faster
than every fixed polynomial in p, and polynomial address/offset/key work per
prefix record is absorbed by its R payload bits. This is why this proof does
not silently price Python integer arithmetic at unit cost.

Extraction/reinsertion scans cost O(V). Stable binary radix sorting uses
O(p) passes on the bad records. Each has an O(p)-bit prefix key in addition
to its R-bit payload, and R eventually exceeds that key size. Its movement
cost is therefore `O(p * V_bad)=O(V/p^2)`. Scratch is O(V), and reuse of the
two radix buckets needs a fixed tape inventory. This justifies the repair
part of the earlier `O(V(H+1)^tau)`-up-to-logarithms sparse-word bound.

The physical B1 theorem, encoded descriptor scans, markers, parking locality,
and their primitive cost bounds remain the credited written implementation
dependencies. They are not axioms of Guard.lean and are not newly formalized
here. The earlier support planner supplies disjoint guards and suffix placement;
this package addresses its algebraic word and repair, not the whole planner.

## 6. Evidence and downstream status

The fresh Lean build checks 18 theorems and the `controlledAdd` equivalence
construction using only standard Lean axioms (`propext`, `Classical.choice`,
`Quot.sound`, where needed). Four false statements must fail after a valid
import. `KERNEL.json` binds the source, dependency revisions and build log.

The Python checks execute the unchanged retained word on all 69,632 addresses
in two nonbinary compact layouts and 3,072 constructed states with uneven
gaps, cross-guard sources and dirty inactive digits. They compare the complete
receipt, including five explicit counterexamples. They supplement the
quantified proof and do not execute an entire physical recursive caller.

The outer candidate in `fine-prime-transform-assembly` still depends on its
named B and C primitive proofs. This package strengthens one of C's support
routing dependencies without changing its saving or the selected frontier.
It is not an independent review of that chain, nor a full formalization of
integer multiplication.
