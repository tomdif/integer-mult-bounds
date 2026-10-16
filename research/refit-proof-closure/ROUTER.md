# Constructive support routing through the ordinary binary caller

This is a written composition proof, a generated coordinate-routing plan,
and a physical primitive join. The retained ordinary binary interchange
contract is supplied by PR2753/2809/2899, retuned and source-bound in
`../recursive-refit-realization/PROOF.md` section 2. We do not claim to have
kernel-verified those source arguments or the whole tape machine.

The sparse shear and exceptional-set argument retain Vlado Vojdanovski's
PR1673 construction. This successor supplies explicit reservoir placement,
an actual fixed-capacity sparse interpreter, and a suffix procedure that
also handles full-span routing. It does not use a fast computed-key sort of
the complete input. That distinction is essential for CRT; see CRT.md.

## 1. Contract and suffix

Let pi be a permutation of n=O(p) binary coordinate positions, moving k
positions, on a complete address rectangle with arbitrary coefficient bits.
An ordinary exchange of two equal E-bit fields, including arbitrary complete
spectators, costs O(V(E+1)^tau), restores spectators and clears its owned work.
Here tau=1-0.0017270071 is sufficient. Elementary single-bit exchanges and
single-bit XOR shears have O(V) scan implementations in source02/source04.

Put G=4 ceil(log2 p)+6, K=128G, ell=ceil(log2 p)^2. When n<=2ell, use at
most n elementary bit-position exchanges; their cost is O(V polylog p).
Otherwise settle the final ell coordinate positions first. For each final
position j, exchange its currently held bit with the bit whose required
destination is j. A previously settled position is never disturbed because
its required source already has that unique destination. This uses at most
ell elementary exchanges. Keep the source-to-current-position table on a
descriptor tape, including each performed exchange.

After this step the residual coordinate permutation fixes the actual final
ell positions pointwise and acts only on the prefix of length N=n-ell.
Its support is at most k+2ell: each preliminary transposition changes at most
two destinations. The following construction never uses the suffix as a
reservoir. Every prefix record therefore contains its full 2^ell suffix
fibre, longer than every fixed polynomial in p. No input padding is used.

This argument works even when every original position is moved. It replaces
the appeal to an unspecified full-span fallback in the retained support note.
For small k its O(ell) preliminary passes are still within the claimed
O(V(k+1)^tau polylog p) bound.

## 2. Two matchings and three disjoint reservoirs

Every cycle c_0,...,c_(m-1) factors into the involutions j -> -j and
j -> 1-j, executed in that order. Their composite is j -> j+1. Applying
this to the disjoint cycles gives two matchings of coordinate positions.
Each transposition (a,b) uses the three simultaneous XOR stages

    b ^= a;  a ^= b;  b ^= a.

Within one matching all endpoints are distinct, so every stage has disjoint
source and target sets. The sparse routine below can therefore execute the
stage in classes without modifying another class's controls.

Let k' be the prefix support size and choose, **before any field placement**,

    H = min(k',ceil(N/K)) G.

If 9H>N or N<4H+K, the prefix has O(G) positions: since K=128G,
H<=N/128+G, the first inequality implies N<(1152/119)G and the second
implies N<(132*32/31)G. Use the elementary matching exchanges in this branch.
Otherwise reserve the three disjoint length-3H intervals starting at
0,3H,6H. An edge has only two endpoints, so it avoids at least one of these
three reservoirs. Assign the edge to the first avoided reservoir.

For class c, exchange its 3H reservoir with [0,3H), unless it is already
there, then exchange [2H,3H) with [N-H,N). These are disjoint equal-field
exchanges. The chosen reservoir now occupies the front u,t fields of H bits
each and the back b field of H bits. The intervening field y has N-3H bits.
Because every edge in the class avoided the reservoir, both endpoints are
now in y. Compute their positions after both exchanges. Keep this placement
through all three XOR stages and undo both exchanges at class completion.

Color a stage's targets by their current y position modulo K. All guards
[j,j+K) within a color are disjoint. Targets in the last K positions of y
use the elementary single-bit XOR; there are at most K per stage. A color
contains at most min(k',ceil(N/K)) active targets, so its r active control
digits fit rG<=H. Thus the reservoir size is not circularly chosen from a
coloring that changes when the reservoir moves.

## 3. Sparse shear, including inactive dirty digits

Use the retained four-update F word on active target positions j_i, with
base B=2^G digits u_i,t_i and z_i=u_i mod 2. It adds 2z_i t_i 2^j_i to y,
loads the selected y bits into t, adds z_i(1-2t_i)2^j_i to y, and unloads
the original selected bits from t. Every later-to-earlier load is shuttled
through the back b field by two ordinary equal-H exchanges. All controls
precede their rotation target at the moment of use.

Good addresses have u_i,t_i != B-1 and

    2B <= (y >> (j_i+1)) mod 2^(K-1) < 2^(K-1)-2B.

If the initial target bit is e, the two additions change its guard by
2z_i t_i + z_i(1-2(t_i+e)) = z_i(1-2e). This flips exactly its low bit
when z_i=1, and restores all higher guard bits. The last unload restores t.
The displayed margins contain each intermediate displacement. No equality
between consecutive gaps is used. Inactive high digits of u,t,b can be
arbitrary: on good addresses no active digit overflows into them.

Execute F; load the source bits into u; F; unload the source bits. A completed
F fixes every non-target bit, so a source inside a guard has the same value
at both loads. The toggling controls differ by precisely that source bit.
The completed good-address map is the desired simultaneous XOR shear T,
with all compact fields and other bits restored.

The raw word S is a bijection on all addresses, since every step is an
ordinary swap or a modular controlled rotation. The ideal T preserves the
good predicate and is a bijection there. Since S=T on the good set, both
good and bad sets are invariant under S. For a current bad address z, route
its record under T(S^-1(z)); use current controls when evaluating the raw
inverse. Sorting these bad records by their corrected keys and reinserting
them into the bad holes gives T on the entire rectangle.

The bad density is at most r(2/B+8B/2^K)=O(p^-3). Its keys have O(p) bits.
Ordinary stable binary radix sorting takes O(p) record passes, so its total
payload movement is O(V/p^2); extraction and reinsertion take O(V).
The long untouched suffix absorbs the fixed polynomial descriptor and key
computation for each prefix record, including inverse evaluation. Counting,
copying, rewinding and work erasure use the same sequential stream rules as
PR2250. Their heads stop at their own delimiters, never at an ancestor's.

## 4. Time, space and the actual join

There are two matchings, three reservoir classes, three XOR stages, O(K)
colors per stage and a constant number of equal-H interchanges in each
sparse word. All other passes have linear payload charge plus polynomial
descriptor work per enlarged record. Hence

    O(V K (H+1)^tau + V polylog p)
      = O(V(k+1)^tau polylog p).

The equality uses k'<=k+2ell and H<=k'G. It also gives the full-address
bound O(V(n+1)^tau polylog p). Setup is polynomial in p and is dominated
when the bulk branch uses its complete suffix. Small addresses use the
elementary branch. The record layout is restored after every completed
class and the final permutation is exactly pi, with arbitrary payload.

The tape inventory is constant: the complete payload streams, the compact
sort's two buckets, a fixed descriptor workspace, and the separately fixed
B1 inventory. Iterations reuse these tapes. The number of stored descriptor
bits is polynomial in p and, in the bulk branch, dominated by V. Payload
scratch and all B1 calls occupy O(V)+F_Q visited cells. At a completed call
all owned scratch is cleared and all heads return to their marked origins.
These are composition arguments from the stated primitive contracts; a
complete new microtransition table is not emitted by this package.

`coordinate_router.py` constructs exactly this plan. Its verifier propagates
independent formal bit variables, so a verified finite plan is checked on
all its 2^n addresses, not on sampled addresses. It also validates every
generated sparse call against the actual `SparseWord` domain. The reported
4,096-bit instance is a symbolic endpoint check, not a 2^4096-record tape run.

`sparse_router.py` implements the uneven target lists and inactive high
digits in the retained sequential compact interpreter. Exhaustive address
checks cover both good and bad classes and sources inside guards. Its
256-record physical fixture routes unique eight-bit payloads through all
12 ordinary calls of the PR2899 binary backend, with numeric decoder and
dynamic word-construction shortcuts disabled and work explicitly closed.
Those reduced binary calls use the elementary branch; the predecessor's
all-width B1 proof, not this fixture, supplies the asymptotic rate.

The omitted-repair and stale-inverse controls fail on actual payload.
Omitted reservoir exchanges and omitted sparse calls fail on the complete
symbolic plan. The same checks must pass with Python assertions disabled.
