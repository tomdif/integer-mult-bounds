# From the two physical primitives to exact integer recovery

This is a written composition theorem. Its two lower-level inputs are the
ordinary binary interchange theorem and the current terminal-refit complex
layer theorem, with their exact interfaces below. They are the written
constructions in the preceding packages, not conclusions obtained from an
outer exponent ledger. CORE.md and PRECISION.md supply the analytic and
numerical joins that were explicitly open in those packages.

No claim of a kernel-verified whole machine, an independent review, or a
practical input threshold is made. The finite checker tests the new seams;
it cannot certify the quantifiers in this written argument. The dependency
inventory must be read with the theorem, rather than calling a passing
certificate an unconditional multiplication proof.

## 1. Exact primitive inputs and parameter choice

**B.** An exchange of two equal e-bit binary address fields in a complete
rectangle of V bits, with arbitrary complete intervening and exterior
spectators, costs O(V(e+1)^(1-a1) polylog p), on fixed tapes, with linear
visited space and restored work, where a1=0.0017270071. The source is
recursive-refit-realization/PROOF section 2, using the selected bit recursive
closure and the physical PR2899 caller. It constructs B from elementary
digit operations and the strict bit moment, without assuming the complex
primitive below. The support and full-address router follows by
refit-proof-closure/ROUTER, with cost O(V(k+1)^(1-a1) polylog p) for k moved
binary positions. This is a coordinate router, not a CRT permutation.

**C.** On h=O(p^eta) named bits with fixed eta<1 in a complete Theta(p)-bit
address rectangle, apply H0^tensor-h, H0=[[1,1],[1,-1]]/2, to arbitrary
bounded complex data. All spectators are complete and restored; owned work
is cleared. Cost is O(V h^(1-q) polylog p), fixed tapes and O(V) visited
space. Requested precision is any fixed multiple of p. The exact native
grid adds C0*h bits, C0=2^210000, before one final rounding. The source is
refit-physical-dispatch/PROOF plus recursive-refit-realization's deferred
reservation, monomial/height join and refit-proof-closure's weighted
induction. It reduces to B and the pinned finite native identities. Its
actual recurrence uses W=66304, m=73 and the current histogram, including
all rank-48 terminal suppliers. It is not a recursive call to itself at
the same width, nor one call per spectator row.

The construction makes a finite, input-independent expansion of the row tape
inventory to W|O(73,2)|. The exponent calculation does not claim this is the
optimized 66804-tape invoice. A fixed number this large is allowed by the
model and contributes only constants.

Use the exact values in paired-terminal-refit/evidence/OUTER-LEDGER:

    C = 0.001722052684227397319529,
    q = C-2*10^-104,        a_eff=C-(3/2)*10^-104,
    delta=(1025/1024)*10^-104,
    epsilon=1-delta,       beta=1-3delta,
    xi=epsilon*(1+q)-3/32+10^-104,
    kappa=C-10^-46-10^-70.

In particular a1>a_eff>q>kappa, beta<epsilon<1 and 1/2<xi<epsilon.
For n-bit input let b=ceil(log2 n), p=6b, and choose d to be the largest
power of two <=floor(b^epsilon). This is Theta(p^epsilon). Set T to the
power of two in [4n/b,8n/b), and choose d dyadic target sides t_i in
{r/2,r}, r=2^ceil(log2(T)/d), whose product is T. Eventually

    Tp=Theta(n), log2 r=Theta(p^(1-epsilon)), S<T<2^b.

The harmless change from floor(b^epsilon) to a power of two changes fixed
comparison constants, not any exponent or strict gap. It is essential for
the balanced CRT tree: every nonempty level has exactly d/2 target axes.

## 2. Prime choice, input layout and initialization

Choose distinct primes s_i in

    (1-1/(2p^2))*t_i < s_i <= (1-1/(4p^2))*t_i.

Trudgian's effective prime-number theorem, applied to the interval endpoints,
gives eventually at least t_i/(8p^2 log t_i) primes in each interval. The
error/main-term ratio is at most
O(p^2(log t_i)^(1/4) exp(-c sqrt(log t_i)))=o(1), because epsilon<1 is fixed.
That count exceeds d. The two dyadic-size intervals are disjoint. Trial
division of all candidates costs at most O(d r^(3/2) poly(p))=2^o(p)=o(n).
It uses no improved multiplication theorem. Thus

    1/(4p^2)<theta_i=t_i/s_i-1<=1/p^2,
    T/2<S=product_i s_i<T.

This is the fine-prime argument credited to Boukhalfa. The strict tiny
exponent delta means an enormous but finite eventual threshold; no numerical
claim about a practical cutoff follows.

Prepare q_digits=ceil(n/b) radix-2^b digits and zero-pad to S. Since S>T/2
>=2n/b, S>=2q_digits-1 eventually, so the ordinary coefficient convolution
has no cyclic wrap. Store a_j*2^(-b-2), of magnitude below 1/4. Throughout,
use the complete padded dyadic box T; invalid source coordinates are zero.
V denotes its actual O(p)-bit word volume, hence V=Theta(n).

Converting the ordinary mixed-radix stream to its padded box is a monotone
insertion of zeros, using a mixed-radix odometer and a maintained invalid
coordinate count. Update only coordinates changed by a carry. The sum of
carry depths is O(T), since each radix is at least two; each update uses
O(p) bits of arithmetic/head travel. There is no d-element descriptor scan
per coefficient. Logical axis i has mixed-radix place product_(j<i)s_j;
axis zero is fastest in this ordinary stream. The later control-first
physical order is supplied by the paid binary-field router. Inverse
extraction uses the same counter. For q-image
embedding/extraction within an active group, g membership tests on h-bit
coordinates cost O(g h^2 polylog p)=o(p), since

    beta+2(1-epsilon)<1.

Alternatively the exact nearest-image remainder counter in source07 updates
only changed coordinates. All embeddings are monotone on the selected
image and preserve each complete spectator block. Both valid-prefix padding
and q-image embedding are paid scans, with volume always at most T.

## 3. The dyadic Fourier subroutine does not use outer CRT

For any r_axes in [d/2,d] chosen axes, retain the synthetic chirp convolution
of source06/source08. Choose one of their longest target axes as the ring
coefficient field; all other active axes have side length that field or half
of it. The independent pointwise polynomial product multiplies O(rp)-bit
packed integers with the established O(N log N) multiplier, at total cost

    O(V log(rp))=O(V p^(1-epsilon) polylog p).

This is an established shorter-record subroutine, not the multiplier being
constructed. The ring arithmetic, signed packing, extraction and exact
normalization identities are those in source06. Even using its time bound
as a space bound, a short product visits O(rp log(rp))=o(V) cells: the
remaining complete axes supply far more than log(rp) records. Its scratch
is reused between products. No separate linear-space theorem for that
published subroutine is required.

Each DIF level consists of H0 on one bit in each still-active axis followed
by the combined monomial twiddle. Different-axis butterflies commute; their
twiddles depend on disjoint axis addresses and may be combined after the
whole layer. Use C with its deferred reservations for that *complete* H0
layer. There are O(log r)=O(p/d) levels. The initial and final binary position
orders are routed using B; repeated per-axis prefix-slot moves from the old
layout are not retained. The complete-layer cost is therefore

    O(V[p^(1-a_eff)+(p/d)d^(1-q)] polylog p)
     =O(V[p^(1-a_eff)+p^(1-epsilon q)] polylog p).        (1)

The combined ring twiddle is one cyclic monomial on a complete r-coefficient
record. Its exponent is computed from the current address descriptor in
polynomial time in p, absorbed by r, which exceeds every polynomial in p.
The record rotation, sign and normalization are sequential O(rp) operations.
Thus there is one O(V polylog p) twiddle cost per level, already below (1).
Bit reversal uses the paid coordinate router. The layer's selected widths
are Theta(d) except possibly a last subset of the two axis-length classes;
a smaller layer only reduces its cost, and direct identity layers are skipped.

Global chirps/twists are separable phases. For a quadratic one-axis phase,
successive values and their ratios are updated using two O(p)-bit products;
the ratio itself progresses by a fixed unit root. A nested odometer caches
outer products, updating only carried coordinates. The total is O(1)
amortized products/head resets per scalar record. Root evaluation is paid
once per descriptor/fibre, whose size is superpolynomial. There are at most
T=2^O(p) updates, so a larger fixed multiple of p absorbs the accumulated
root/rounding drift. This explicitly replaces the old O(Vd) chirp generation
scan in source08. Pointwise arithmetic uses the established shorter multiplier.

Synthetic transform truncation, the three normalized transforms, endpoint
phases and the exact T/r convolution scale lose at most 2^O(p) in absolute
error. Increasing the fixed working precision supplies any desired 2^-C'p
error, while preserving (1). Every layer has complete long spectator fields,
including the ring coefficient field, so B and C have their required suffix
and stock. No Gaussian source transform or CRT map is called by this path.

## 4. Assemble the source transform on any d/2 or more axes

Partition the chosen axes into groups of sizes between g and 2g, where
g=floor(p^beta). This is possible eventually because r_axes/g tends to
infinity; distribute the final remainder among the preceding groups. Leave
all other axes as complete spectators. CORE and PRECISION apply uniformly
to the actual source/target lengths and group sizes.

For each active source axis define the exact infinite-periodized Gaussian
maps S_i,T_i, the nearest selector C_i, D_i=diag(exp(a beta_j^2)) and
N_i=C_i T_i D_i as in source07. The sharp row-gap argument in the predecessor
proves N_i invertible at fine theta; it does not use the old hypothesis
theta>p/alpha^4. The exact identity

    T_i P_(s_i) F_(s_i)=P_(t_i) F_(t_i) S_i,
    D_i N_i^-1 C_i T_i=I                              (2)

is the resampling identity and elementary left-inverse calculation. The
first equality is Theorem 4.2 of Harvey--van der Hoeven and is valid before
any quantitative inverse or numerical-routine hypotheses are imposed.

Let Z=2^ceil(100 log2 p). Broad expansion S_i/Z and compression
D_i N_i^-1 C_i/Z are contractions eventually, by the proved row/inverse
bounds. CORE computes their square target completions on the intended
embedded subspace; holes are included in the numerical error bound.
PRECISION specifies the actual rounded core matrices, phases, pages and errors.
The full periodic maps differ from the banded references by exponentially
small row/column errors, and the resolvent bound gives the corresponding
inverse error. Therefore these procedures approximate the exact factors
in (2), not a separate unrelated banded identity.

Tensor (2) over the active axes. Apply the grouped expansion, the permuted
dyadic Fourier via section 3's chirp convolution, and the grouped compression.
Finally multiply by Z^(2*r_axes). Its binary shift is O(d log p)=o(p).
The resulting exact map has coefficients

    (F_J^- x)(k)=1/S_J sum_j x(j)
                     exp[-2 pi i sum_(i in J)t_i k_i j_i/s_i],

where S_J=product_(i in J)s_i. Conjugating the entire procedure supplies
F_J^+. These are contractions. All numerical calls have a fixed margin
inside their bounded-input domain after the stated normalizations. Extra
working bits for (5) of PRECISION, source scales and all error accumulation
are O(p). P can be any sufficiently large fixed multiple of p.

No whole source axis is invoked separately for each fixed coarse label.
Each dense compiled H call acts on the entire complete stream and restores
borrowed coarse coordinates before the next coefficient scan. Consequently
coarse-label-dependent local matrices coexist with the physical primitive's
stock and restoration contract. Polynomial coefficient pages are regenerated
per complete coarse block and the fixed tapes are reused. Ancestor buffers
are parked by the already proved primitive contract; the outer schedule
uses a constant number of input/output streams and polynomial setup storage.
Visited space is O(V) and the tape inventory is independent of p,n,d,g.

## 5. Every cost row, including the repaired faces

The following powers multiply V; fixed logarithms are displayed only as
polylog(p). They follow from the constructions, not just from evaluating
an existing ledger.

| Operation | Power of p |
|---|---:|
| Synthetic transform layers | 1-epsilon*q |
| Full-address routing | 1-a_eff |
| Dense Gaussian groups | epsilon-q*beta |
| Group support routing | epsilon-a_eff*beta |
| Group scans and normalizers | epsilon-beta |
| Boundary products/solves | epsilon-xi+29/32 |
| Sparse union movement | epsilon+1/2-xi |
| Packed polynomial products | 1-epsilon |
| Direct variable-coefficient faces | epsilon+beta-30 |

The boundary row uses W=O(sqrt(p)polylog p) and tau-1=29/16. The last row
replaces the source's smaller p^2 online-face allowance with the proved
p^50 routine; it remains below -28. Costs of sparse keys and explicit
metadata are included there. The group scans count d/g groups, not d axes.

Put sigma=min_rows(1-kappa-power). The exact checker proves sigma>0 for
the pinned rationals. Define rho=sigma/2. Each fixed power of log p is
eventually at most p^(sigma/2), so the source transform just constructed
obeys contract T from refit-proof-closure/CRT:

    time O(V p^(1-kappa-rho) polylog p), accuracy 2^-P,
    fixed tapes, O(V) space, complete restored spectators.

The redundant polylog allowance is harmless. The proof applies to every set
of d/2 named axes and to all d axes, with constants uniform in the choice.
The dependency graph is B -> C -> dyadic convolution + grouped Gaussian
maps -> source transform -> CRT. It is acyclic. In particular, no fast
outer integer product is assumed to construct its own source transform.

## 6. Logarithmic CRT and its full error budget

Use the algebraic factorization proved in refit-proof-closure/CRT. At a
binary-tree node I=L union R, recover a_L=Phi_L^-1(x) from the unchanged
left controls, then shift each right coordinate by

    delta_i(x)=sum_(j in L) mu_i P_j a_j mod s_i,
    P_i=product_(j<i)s_j, mu_i=P_i^-1 mod s_i.

All nodes on a level commute, and, because d is a power of two, their union
of targets has exactly d/2 axes. Route controls before targets once, apply

    Shift_delta=S_J F_J^+ diag(exp[-2pi i sum t_i k_i delta_i/s_i]) F_J^-,

then restore the order. Both the frequency multipliers t_i and the final
S_J scale are required. The same phases with opposite sign, in reversed
tree-level order, give the inverse. Each conditional phase has the proved
O(1)-amortized odometer implementation; polynomial control setup is charged
per whole target fibre. Thus there are O(log d) source-transform calls,
coordinate routes and phase scans, absorbed by the strict gap sigma.

For an explicit precision target let e=2^(-10b). Require error <=e for a
*whole* CRT map and for each completed source transform, on inputs of
supremum norm <=1/2. At each of the at most log2 d CRT levels allocate
internal transform/phase error <=e/[20 S_J(1+log2 d)]. Exact F_J^+/F_J^-
are contractions, the diagonal has modulus one, and its approximate
coefficients have the stated uniform error. The sandwich error is then
<=e/(1+log2 d) after S_J. Completed shifts are permutations, so errors
add over levels. Since S_J<=S<2^b and log d=O(log p), this tolerance requires
only an additional b+O(log p) bits. Phase generation's length-dependent
drift was paid in section 3. All intermediate normalized transform inputs
remain below 1/2 when the original input is below 1/4 (or below 1/8 on the
inverse path). They are not supplied arbitrary integer payloads.

## 7. Three transforms, inverse CRT, then integer rounding

Let a,c be the two normalized ordinary coefficient streams, each <1/4,
and let u=Phi a, v=Phi c denote their exact CRT permutations. The implemented
CRT arrays have errors <=e. Applying the two approximate source transforms
introduces at most another e, so their errors relative to exact F^-u,F^-v
are <=2e each. Their norms are below .26 eventually. Multiply pointwise
with scalar error <=e. The error in that product is at most

    2e*.26 + (1/4)*2e + e < 3e.

Apply the opposite source transform, a contraction with its own error <=e.
The error is then <4e, and the exact result is (u*v)/S^2. This identity
holds with the retained frequency multipliers t_i: the geometric sum over
each unit t_i gives exactly the usual cyclic convolution.

Multiply by S exactly to obtain wtilde, with

    ||wtilde-(u*v)/S||_infinity <4S e.

The exact target has norm <1/16, so wtilde remains inside 1/8 eventually.
**Apply the approximate inverse CRT now**, before any integer rounding.
It adds at most e; the exact inverse permutation propagates the existing
error unchanged. The error in ordinary coefficient order is <(4S+1)e.

Finally multiply exactly by 2^(2b+4) S and round the real part. Since S<2^b,

    final error < 2^(2b+4) S(4S+1)e
                <=80*2^(4b)*2^(-10b)
                 =80*2^(-6b)<1/4                       (b>=2).

The true values are the integer coefficients of the original product.
Unique nearest-integer rounding therefore recovers every one exactly;
the imaginary residual has the same error bound and is discarded.
Project invalid padded addresses to zero at completed source boundaries
and remove padding in the inverse CRT extraction. Their exact values are
zero, so these projections do not increase the error.

Each coefficient is <S*2^(2b)<2^(3b). Exact radix-2^b carry propagation
uses O(b)-bit carries, O(V) time, and returns the full 2n-bit product after
one stream reversal. The two S scalings are different normalizations and
both are retained. Fixed component widths enlarged by O(b) suffice for
all exact shifts/products and rounding. Their known shorter-integer cost
is O(V polylog p). Multiplying by S does not invoke the new theorem.

## 8. Result and logical scope

Under the two explicitly cited physical primitive theorems B and C, the
construction above is a deterministic fixed-multitape integer multiplier
with linear visited space and

    time O(n (log n)^(1-kappa)),
    kappa=0.001722052684227397319529-10^-46-10^-70.

Proof: V=Theta(n), p=Theta(log n), the row slack pays all polylogarithms
and the logarithmic CRT layers, section 7 proves exact output, and the
fixed tape/space invariants are preserved at every call. Choose one fixed
cutoff beyond the finitely many eventual inequalities. Below it use the
ordinary multiplier; that finite range is absorbed into the constant.

CORE, PRECISION and this note discharge the outer cyclic/core, reference
rounding, capped-circuit composition, source-transform contract T and final
recovery obligations, as written mathematics relative to B and C. Whether
the full result is established consequently depends on the correctness of
those earlier constructive proofs and their finite operator certificates;
their source hashes or successful tests do not by themselves establish
them. DEPENDENCIES records this distinction explicitly. This package does
not change the repository's selected frontier or rewrite the historical
conditional claims in immutable predecessor packages.
