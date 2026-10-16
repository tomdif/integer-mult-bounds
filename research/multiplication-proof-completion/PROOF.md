# The assembled fixed-multitape multiplication theorem

This completes the written argument on this branch: one correction to the
outer assembly, followed by substitution of the preceding implementation
lemmas into its interfaces. These are mathematical dependencies, not a
claim that test receipts prove their quantified statements. The result is
not independently reviewed or fully formalized.

## 1. Statement and parameters

**Theorem.** There exist a deterministic finite-alphabet multitape Turing
machine, a finite number of tapes independent of the input, and constants
A,N such that, for every n>=N and two unsigned n-bit integers, the machine
returns their exact product in at most A n (log2 n)^(1-kappa) steps and
visits at most A n cells, where

    C = 0.001722052684227397319529,
    kappa = C-10^-46-10^-70.

Below N use school multiplication; that finite range is absorbed into the
constants, with log2 n replaced by log2(max(2,n)). This is an asymptotic
existence assertion, with no practical threshold or tape count asserted.

Fix the rational parameters

    delta = (1025/1024) 10^-104,
    epsilon = 1-delta, beta = 1-3delta,
    q = C-2*10^-104, a_eff = C-(3/2)*10^-104,
    xi = epsilon*(1+q)-3/32+10^-104,
    a1 = (173/100000)*(1-173/100000) = 0.0017270071.

They satisfy a1>a_eff>q>kappa>0, beta<epsilon<1,
beta+2(1-epsilon)<1, beta+2xi-2<1 and 1/2<xi<epsilon.
The BIT prime Q and native dimension 73 are also fixed independently of n.

Bounded input means a uniform supremum bound on complex coefficients.
Having O(p) bits of integer headroom alone does not give this condition.

## 2. Correction: bounded calls throughout a Gaussian group

### Counterexample to completed-map normalization alone

Let H0=[[1,1],[1,-1]]/2 and D=diag(2^k,2^-k). The chronological word

    D; H0; H0; 2D^-1

is the identity. Input (1/2,0) nevertheless becomes (2^(k-1),0) before
its first H0. For k>=2 the bounded-input supplier contract cannot be
invoked. Normalizing only the completed map does not fix this.

The wrapper below supersedes the assertion in the preceding TRANSFER
section 4 that its completed-map normalizations alone supply a fixed
margin at every numerical call.

### Uniform scaling lemma

Let A_1,...,A_m be ideal linear stages, m>=1. Rectangular stages, copying
and zero insertion are allowed. Use supremum operator norms on the live
coefficient arrays. Suppose integer E>=0 bounds every prefix by 2^E and
every contiguous subword by 2^(2E), including empty subwords. Let ||x||<=2.
For requested accuracy 2^-Q, Q>=0, set

    s=E+4, ell=ceil(log2 m), R=Q+s+2E+ell+3, eta=2^-R.

Scale x by 2^-s exactly, retaining s extra fractional bits. Execute every
stage with absolute error <=eta whenever its input has norm <=1. Restore
2^s exactly at the end. If needed, round to the output format with total
complex error <=2^(-Q-2). Every call is in domain, and the output error
is <2^-Q.

**Proof.** The ideal scaled boundary z_j=A_j...A_1(2^-s x) has norm <=1/8.
If the first j operations succeeded with errors r_i, their exact error is

    e_j=sum_(i=1)^j A_j...A_(i+1) r_i.

Hence ||e_j||<=m 2^(2E) eta<=2^(-Q-s-3)<=1/8. Induction starting from
the exact scaled input gives actual norm <=1/4 at every boundary. This
justifies the next operation's bounded-input premise; it does not assume
successful bounded calls to prove their domain condition. Restoring 2^s
gives error <=2^(-Q-3). The optional final rounding adds <=2^(-Q-2),
and the sum is <2^-Q.

The errors may include both coefficient approximation and arithmetic.
Allocate eta/2 to each. For a diagonal scan, coefficient error <=eta/2
suffices on input of norm <=1. For a raw H tensor on h bits, request the
normalized supplier at R+h+2 fractional bits before the exact 2^h shift;
the extra two bits cover real/imaginary conversion. Exact shifts and
signed component permutations introduce no rounding.

An invertible circuit's prefix and inverse-prefix bounds K imply interval
bounds K^2. Noninvertible stages require direct interval bounds, as below.

### Application to the actual group, including intermediate norms

Let g'=|J|, g<=g'<=2g, g=floor(p^beta). PRECISION section 3 bounds each
capped circuit's prefix, inverse-prefix and suffix logarithmic 2-norm by
O(log^2 p). Anchored Gaussian diagonals add
O(a theta B^2+a theta B+log p) per axis, with
a<=16 ceil(log2 p), theta<=p^-2 and B<=p^xi. The matching compiler adds
polylog(p). Completed switch routes are permutations, so its gate bound
is not multiplied again after every completed original layer.

Tensor products add these logarithms. The complete coarse-label layout
is a direct sum, taking their maximum. Within a coarse block, conversion
to supremum norm costs at most L^(g'/2), L=2^ceil(128 log2 p), adding
O(g' log p), rather than multiplying a full-input norm factor per block.

The six-stage core solve has polynomially bounded factors and inverses;
across g' axes it adds O(g' log p). Whole-separator boundary solves use
CORE section 5's bounded leading inverses, not a product of all individual
pivot bounds. In the first-face Horner algorithm, Q0=I-gamma H*H has
||Q0^j||_2<=1. A contiguous Horner interval on augmented state
(input,accumulator) has norm <=1+J gamma ||H||_2, polynomial in p.
Its tensor product and norm conversion add O(g' log p). Copying has
supremum norm one and the output faces are disjoint. Thus the actual
core/face schedules also have the required interval bounds.

One may consequently choose a uniform integer E(p,g') with

    E=O(g' polylog(p)+g' a theta B^2)=o(p).             (1)

For example, fix integers c,D large enough to dominate the proved circuit
bounds, and take the ceiling of

    c g' (1+ceil(log2 p))^D
       +16 c g' ceil(log2 p) p^(2xi-2).

All constants arise from finite words and effective elementary bounds.
Rational-power comparisons, or a larger rational-power majorant, compute
the envelope in polynomial control work; there is no search through all
coarse labels. Finitely many small-p exceptions are covered by the fixed
cutoff. Equation (1) uses beta<1 and beta+2xi-2<1.

Consider mathematical layers acting independently on all coarse blocks.
Serial physical execution does not lengthen a value's dependency path.
There are m=p^O(1) layers, including the direct face polynomial, so
ell=O(log p). The lemma gives R=Q+o(p), raw-H conversion costs g'=o(p)
bits, and the native internal guard C0 g'=o(p), C0=2^210000. Therefore
any Q that is a fixed multiple of p still requires O(p)-bit records.
Choose one larger fixed multiple of p dominating these local requests
for all sufficiently large p. If an incoming stored grid has more bits,
retain those plus s for the exact downscale, then round back at the group
return; this does not accumulate fractional width from group to group.
Increasing the primitive's precision parameter by a fixed factor changes
its logarithmic neighbourhood sizes only by a fixed additive constant,
which fits the same superpolynomial axis widths eventually.

Apply the wrapper to the whole complete coefficient stream before copying
core/face inputs. Its scale is uniform in data and coarse label and commutes
with the linear map, zero insertion and extraction. All input-derived work
carries that scale. Addresses and router control fields are not scaled.
The physical H call still sees complete coarse spectators and restores
borrowed coordinates before coefficient pages are read.

Include Z^-g' in the ideal group word, Z=2^ceil(100 log2 p); restore 2^s
only at group completion. The wrapper adds two O(V) scans per group,
O(V p^(epsilon-beta)) in total, already the group-scan cost row. Account
separately for the final Z^(2r_axes) source scale when choosing Q.
Completed group maps are contractions; their prescribed total error keeps
bounded starting inputs bounded at all group boundaries. The lemma allows
input norm 2, providing margin beyond the actual inputs, which are <1.

## 3. Substitute the physical primitive proofs

The earlier outer theorem has interfaces B and C. Their algorithms are
supplied by the following constructive lemmas, in dependency order.

### Ordinary interchange B and coordinate routing

[selected-bit-recursive-closure/PROOF](../selected-bit-recursive-closure/PROOF.md)
constructs F_A(H,D)=(A C_n D,C_n A^-1 H) on arbitrary complete preceding,
intervening and following fields. It proves full-ring good and fallback
elimination, frozen weight ancestry, elementary leaves, literal header
routes and whole-call hosting. Weights read older frozen fields only.
Children execute once on the whole high matrix cube, not once per lift.

[recursive-refit-realization/PROOF section 2](../recursive-refit-realization/PROOF.md)
retunes c to 173/100000. The complete good-plus-bad moments are
mu_(1-c)<99999/100000 and mu_1<199/200. Strong induction gives
O(V[n+n^(1-c)w]), w=ceil(e^c), with elementary n<64 leaves. Its stock
proof gives k<e/2 for e>=2^32. The chronological two-F wrapper removes
padding after each call and yields O(V(e+1)^(1-a1)) ordinary interchange,
a1=c(1-c). Fixed-odd-radix completion costs only a constant volume factor.
This construction never calls the complex supplier.

The inherited H1--H5 labels concern the selected finite scalar word's gate
directions, frames, literal inverse cleanup and target-to-target block.
They are checked finite hypotheses of its scalar-interface lemma, not
universal assertions about every possible network. The literal all-column
proof and the decoded-frame induction in
[selected-bit-local-ring-sweeps section 2](../selected-bit-local-ring-sweeps/PROOF.md)
transport those identities to arbitrary correlated dirty functions over
the complete local-ring packets. Section 5 of the recursive closure then
composes whole calls through the verified untouched hosting intervals.

[ROUTER](../refit-proof-closure/ROUTER.md) settles an untouched
polylogarithmic suffix, factors permutations into two matchings and assigns
edges to avoided disjoint reservoirs. The guarded dirty word S equals the
desired shear T on an invariant good set. Exceptional records sorted by
T S^-1 fill precisely the exceptional holes. Density O(p^-3) pays the
key sort; the complete suffix pays descriptors. The guard and repair
implications are also proved in
[compact-guard-kernel/PROOF](../compact-guard-kernel/PROOF.md).
This yields O(V(k+1)^(1-a1) polylog p) for k moved coordinate positions,
fixed tapes, linear visited space, restored spectators and empty work.
It does not assert that bound for arbitrary computed-key permutations.

### Complex layer C, recursion and internal precision

[refit-physical-dispatch/PROOF](../refit-physical-dispatch/PROOF.md)
implements the current dimension-73 native program on a fixed finite
inventory of W Gamma row tapes, W=66304, Gamma=|O(73,2)|. Unary-clock
split/merge is linear; owner selection is a fixed role. Every child retains
the complete unused U range. Actual charts select d sigma^-1, with
entry/exit translations in the correct common frame.

The finite native proof combines free-operator scalar identities on
independent dirty registers with exact unary monomial/frame identities.
Tensoring the latter preserves products and inverses. Evaluating the
former in these tensor operators preserves addition and unchanged role
scalars. No sum is illegitimately tensor-powered term by term. The earlier
complete native admission pins the actual four words, helper endpoints,
zero work and chronological hosting used here.

The global schedule retains rank-zero translations, completes each whole
invocation before the next and applies the cover correction after the
terminal signed exchange. Every child has r floor(e/73)<=48 floor(e/73)<e.
With the current histogram H,

    T(V,e)<=A V e^(1-a_eff) polylog p
             +Gamma sum_r H_r T(V/(W Gamma),r floor(e/73)).

The moment at 1-C is strictly below 1. Because a_eff<C, the moment at
1-a_eff is smaller still. Strong induction pays the node cost with this
slack, based on elementary finite leaves. There is no same-width assumed
child and no complex call in B.

Deferred reservations leave at most h/16 selected bits for the next phase.
Complete row stock suffices for descendants; padding is less than two and
is deleted at each completed phase. The exact height proof in
recursive-refit-realization section 6 charges returned children by endpoint
width, with only one unfinished child, giving the root guard C0 h.
The root grid executes all native arithmetic exactly, with no child
rounding. Completed normalization converts C to H0 with one final rounding.

Parking scans only local marked regions. Active volumes are
V,V/(W Gamma),..., giving O(V) visited space, with the ordinary inventory
reused between children. A complete long suffix pays descriptors and
remains outside support. Thus C supplies H0^(tensor h) in
O(V h^(1-q) polylog p) time and O(V) space, on bounded inputs at any
fixed multiple of p output bits, for h=O(p^eta), fixed eta<1.
Its h=d and h=g' uses meet that condition. Section 2 supplies its missing
domain condition inside Gaussian circuits. Synthetic normalized layers
are already contractions.

## 4. Analytic construction and acyclic reduction

Set b=ceil(log2 n), p=6b, and d to the largest power of two <=floor(b^epsilon).
Choose power-of-two T in [4n/b,8n/b), with d sides t_i in {r/2,r},
r=2^ceil(log2(T)/d). Then Tp=Theta(n), log2 r=Theta(p^(1-epsilon)).
Trudgian's effective prime theorem supplies distinct primes

    (1-1/(2p^2))t_i<s_i<=(1-1/(4p^2))t_i.

The prime-count error/main ratio is
O(p^2(log t_i)^(1/4) exp(-c sqrt(log t_i)))=o(1); eventually there are
more than d primes per interval. Trial division costs 2^o(p)=o(n).
For S=product s_i, T/2<S<T<2^b and 1/(4p^2)<theta_i<=1/p^2.

[NARROW](../fine-prime-halo-closure/NARROW.md) proves row dominance and
dimension-independent row/column inverse bounds. [BROAD](../fine-prime-halo-closure/BROAD.md)
uses finite Newton/Vandermonde factors and summable inverses, including
holes and periodic completion. Together they supply the p^10 norm/inverse
envelope to [CORE](../fine-prime-transform-assembly/CORE.md).

CORE uses finite length-L cores instead of a cyclic-prefix assumption.
Its explicit inverse polynomial has radius <A=p^48. Deep outputs agree
with the global polynomial; first-boundary-axis faces use original wrapped
inputs. Whole separator pivots are Schur complements of contiguous finite
prefixes including the adjacent eliminated interior. Those prefix inverses
bound substitution as well as the pivots. Boundary products use the explicit
seven-product algorithm, exponent 45/16>log2 7. Sparse movement pays each
actual face incidence once.

[PRECISION](../fine-prime-transform-assembly/PRECISION.md) constructs
anchored capped blocks and boundary pages from one rational matrix.
The shifted Gaussian symbol is accretive with inverse margin p^O(1).
Schur descendants, low displacement rank, triangular Toeplitz shears and
matching compilation give the shallow circuits and bounds of section 2.
Polynomial setup precision avoids underflow and is paid by complete coarse
payloads. The new rescaling wrapper supplements these constructions.

Harvey--van der Hoeven's exact Gaussian identity, Theorem 4.2, gives

    T_i P_s F_s=P_t F_t S_i,
    D_i(C_i T_i D_i)^-1 C_i T_i=I.

Its identity does not require the old large-theta numerical inverse routine.
Grouped normalized broad expansion and narrow compression surround a dyadic
Fourier transform. That transform uses synthetic chirp convolution,
normalized H0 layers, one combined monomial twiddle per level and the
independent O(N log N) multiplier on short O(rp)-bit packed records.
It calls neither outer CRT nor the new outer multiplier. Even its time
bound as a space bound is o(V), allowing reusable short-product scratch.

Twiddle descriptors are paid per superpolynomial ring record. Chirps and
conditional phases use nested odometers with O(1) amortized updates per
record. General complex phases have an explicit error budget: rounding
commutes only with signed coefficient permutations, not with arbitrary
unitaries. At most exp(O(p)) updates consume O(p) extra accuracy bits.

For any d/2 or more chosen axes J the resulting source transform is

    F_J^-(x)(k)=(1/S_J) sum_j x(j)
                    exp(-2pi i sum_(i in J) t_i k_i j_i/s_i).

Its conjugate is F_J^+; both are contractions. Restoring Gaussian scales
costs O(d log p)=o(p) bits. Divide local error allowances by that scale
and the polynomial number of groups. Section 2 then gives any requested
2^-P accuracy with O(p)-bit online records.

The published inputs are [Harvey--van der Hoeven](https://www.texmacs.org/joris/nlogn/nlogn.pdf),
Theorems 1.1 and 4.2, and [Trudgian](https://arxiv.org/html/1401.2689v2),
Theorem 2. Detailed phase, layout and error calculations are in
[TRANSFER sections 2--4](../fine-prime-transform-assembly/TRANSFER.md).
The dependency order is elementary streams -> B -> router -> C ->
dyadic Fourier plus Gaussian maps -> source Fourier -> CRT -> multiplication.

## 5. All costs and visited space

For actual O(p)-bit volume V=Theta(n), these powers multiply V:

| Operation | Power of p |
|---|---:|
| Synthetic layers | 1-epsilon*q |
| Full coordinate routes | 1-a_eff |
| Dense Gaussian groups | epsilon-q*beta |
| Group support routes | epsilon-a_eff*beta |
| Group scans, including the two new scans | epsilon-beta |
| Boundary arithmetic | epsilon-xi+29/32 |
| Sparse union movement | epsilon+1/2-xi |
| Short packed products | 1-epsilon |
| Variable-coefficient first faces | epsilon+beta-30 |

Exact substitution gives sigma=min_rows(1-kappa-power)>0. Each fixed
polylog(p) factor, including logarithmic CRT depth, is absorbed by this
strict positive gap. No limit sets epsilon equal to 1. Extra precision
changes only the fixed constant in V.

Dyadic padding changes volume by a constant factor. Core/face duplication
has bounded volume because g A/L tends to zero; polynomial setup storage
is absorbed by complete coarse payloads. The outer schedule uses finitely
many reusable streams. Each primitive has linear visited space, including
parked ancestors, and clears owned work between calls. Total visited space
is O(V).

## 6. CRT, exact recovery and conclusion

The block factorization in [CRT](../refit-proof-closure/CRT.md) converts
mixed-radix addresses to residues through a balanced tree. Every level
targets exactly d/2 axes; left controls are inverted before computing
their conditional shift. Each shift is

    S_J F_J^+ diag(exp(-2pi i sum_i t_i k_i delta_i/s_i)) F_J^-.

Retain the units t_i and scale S_J. There are O(log d) levels with paid
conditional-phase generation. Let e=2^(-10b); require each internal
transform/phase error <=e/[20 S_J(1+log2 d)]. This uses O(p) bits and
gives whole-CRT error <=e on the bounded arrays used here. Completed
shifts are permutations, so errors add across levels.

Split inputs into radix-2^b digits, divide by 2^(b+2), and zero-pad to S.
There is no cyclic wrap, since S>=2 ceil(n/b)-1; input norms are <1/4.
Apply CRT, two negative source transforms, pointwise multiplication, and
one positive transform. With error e per completed interface and product,
the forward errors are <=2e, product error <3e, and third-transform error
<4e. Its exact output is the normalized convolution divided by S^2.

Multiply by S, then apply inverse CRT **before rounding**. The exact
ordinary normalized convolution divided by S has norm <1/16; its error
after inverse CRT is <(4S+1)e. The inverse CRT input is therefore inside
1/8 eventually. Multiply exactly by 2^(2b+4)S. Total error is

    <2^(2b+4) S(4S+1)2^(-10b)
    <=80*2^(-6b)<1/4  (b>=2).

The true coefficients are integers, so unique nearest-integer rounding
recovers them. They are <2^(3b); an O(b)-bit sequential carry pass returns
the exact 2n-bit product. Hole projections occur only at completed source
boundaries and are contractions. Exact S products, shifts and carries
fit O(p)-bit records and the independent scalar-arithmetic cost allowance.

All algorithmic interfaces in this recovery are supplied by sections 2--5
and the cited constructive lemmas, with matching accuracy, cost, complete
spectator and storage contracts. Choose fixed N beyond their finitely many
eventual thresholds. Since V=Theta(n) and p=Theta(log n), section 5 gives
the time and space, and this section the exact output. This completes the
written proof.

## 7. Where the earlier assumptions are discharged

| Earlier obligation | Written resolution |
|---|---|
| BIT H1--H5 and mutable sources | Selected literal scalar identities, decoded-frame induction and guarded private lifetimes; section 3 above |
| All-size ordinary compiler | Full-ring good/fallback adapters, causal weights, elementary leaves, row stock, parking and strong induction in selected-bit-recursive-closure |
| Common labels and whole-call hosting | Complete low-packet separation on BIT; actual cover charts, whole native calls and untouched chronological windows on complex data |
| Complex dispatcher | Unary-clock packet movement, fixed roles, literal opcodes, local parking and proper children in refit-physical-dispatch |
| Cover recurrence/volume correction | Actual child volume V/(W Gamma), Gamma copies and the strict moment in section 3 |
| Precision and bounded supplier inputs | Exact root grid for C; one rational Gaussian reference matrix; the new scaling induction in section 2 |
| Fine-prime analytic/source transform | Finite-line norm bounds, finite cores, whole separators, actual variable-coefficient faces and capped circuits; section 4 |
| CRT and exact integer recovery | Acyclic source transform, logarithmic CRT tree, both S scales, inverse CRT before rounding; section 6 |

This table locates proofs; checking that a row exists is not a mathematical
verification of that proof. It does not replace the cited arguments.

## 8. Evidence and review boundary

The theorem is the mathematical claim of this manuscript. It is not inferred
from RESULT.json, native admission or a Lean theorem assuming an error bound.
Those are scoped evidence for finite algebra and local implications. The
whole argument, including tape constructions and analytic estimates, remains
subject to review. No independent review or whole-machine formalization is
claimed. Historical conditional packages and the selected frontier remain
unchanged.
