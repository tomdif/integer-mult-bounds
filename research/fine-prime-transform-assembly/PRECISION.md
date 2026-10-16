# Coefficient construction, capped circuits and the online precision bound

The reference in CORE.md is an analytic, band-truncated Gaussian. This note
specifies how to construct its approximate core circuits and boundary pages.
It does not assume the original source's constant-width inverse routine works
at fine theta. Only the Gaussian identity from Harvey--van der Hoeven and
the finite-line estimates in the preceding package are used for that step.

Credit: the shallow circuit and tensor compiler are Vojdanovski's PR1673;
the fractional shifts and accretive extension are the PR1758 lineage credited
in GAUGEFREE-INTERIORS (including IdeaOuter); the distinction between setup
and online precision is Boukhalfa's PR1786. We give a slightly weaker but
sufficient prefix bound and explicitly join rational coefficient generation
to the finite-core Schur pages.

## 1. Setup numbers and avoiding underflow

Write a=pi alpha^2 and beta_j=rho j-q_j. Original narrow cell weights are

    w_j=exp[-a(1/4-beta_j^2)/theta].

For L_p=ceil(log2 p), eventually a<=16 L_p and theta>=1/(4p^2), so
-log w_j<=16p^2 L_p. At setup precision

    P_setup=Cp+64p^2 L_p

downward rounding has relative error at most
2^-P_setup exp(16p^2 L_p)<2^-Cp, using log 2>1/2. In particular every rounded
weight is positive. Absolute Cp-bit rounding alone does not have this property.
For two such relative approximations with error u<1/2, their quotient has
relative error at most 4u. On a distance-W band within a phase cell,
|log(w_j/w_k)|=O(aW+a theta W^2)=o(p). Thus multiplying an absolute Cp-bit
kernel error by that ratio still gives 2^(-(C-o(1))p) entry error. Only O(W)
entries occur per row/column. Gaussian tails and the omitted periodic aliases
are smaller. This proves the previously explicit reference-rounding premise
for that original implementation, in both induced row and column norm.

For the concrete compiler here it is simpler to generate *anchored* capped
blocks directly. All origins, beta values and rho are rational with O(p)
bits. A local window has polynomial length L, and we compute beta by integer
division/remainder, never by subtracting two inaccurate large reals. Exponential,
pi, square-root and trigonometric coefficients to any polynomial number of
bits can be generated in polynomial time by argument reduction and convergent
series; ordinary rational arithmetic suffices. Negative exponents beyond the
requested absolute precision may be truncated to zero with the stated bound.
The setup uses polynomial space/time and is paid once per complete coarse
block; L^g and the complete spectator payload dominate every such polynomial.

## 2. Shifted kernels and accretivity

In a constant-offset phase cell, write centered coordinates x=i-m, y=k-m,
lambda=1/rho, delta=(1-lambda)m-c and b0=pi/alpha^2. The broad block is

    alpha^-1 exp[-b0(x-lambda*y+delta)^2].

For s0=-delta(1-theta), expansion of the square gives

 (x-lambda*y+delta)^2-lambda(x-y-s0)^2
 = (1-lambda)x^2-lambda(1-lambda)y^2+delta^2-lambda s0^2
   +2(delta+lambda s0)x-2lambda(delta+s0)y.             (1)

The right side is a sum of row and column terms. Also |delta|<=1/2 at
a selected central anchor and 1-2|s0|>=theta. Its linear leftovers have
range O(b0 theta B), its quadratic terms O(b0 theta B^2).

For the narrow block, put beta_i=beta0+theta(i-m). Direct expansion gives

    N_ij=exp[a theta(i-m)^2] k(j-i) exp[-a theta(j-m)^2],
    k(h)=exp[-a rho h^2-2a beta0 h].                    (2)

This is the unit-diagonal shifted kernel with gamma0=a rho and
s0=-beta0/rho, so 1-2|s0|>=theta/rho>=theta/2. The broad kernel similarly
has gamma0=b0/rho, after absorbing its constant scale in the diagonals.
Truncation on physical distance inside one such cell is the same Toeplitz
band truncation on h. Holes and cell cuts have already been excluded from
these interiors.

For the unit-diagonal kernel k(h)=exp[-gamma0 h^2+2gamma0 s0 h], |s0|<1/2,
the symbol has

    Re sum_h k(h)e^(-i h omega) >=
       (1-exp[-gamma0(1-2|s0|)]) exp[-pi^2/(3gamma0)] =: mu,
    ||k||_1 <= 3+sqrt(2pi/gamma0) =: Lambda.             (3)

Here is the argument used from GAUGEFREE-INTERIORS. In Jacobi's triple product,
put q=exp(-gamma0), a_m=q^(2m-1-2|s0|), b_m=q^(2m-1+2|s0|).
The variable arguments are those of (1+a_m e^-iw)(1+b_m e^iw).
For 0<=w<=pi, f(z)=arg(1+z e^iw) increases on [0,1), and
a_(m+1)<=b_m<=a_m. Their total phase lies between -f(a_1) and zero by
telescoping. Multiplying the modulus by cos(f(a_1)) leaves at least
(1-a_1) times the three remaining positive products. Expansion of their
negative logarithms gives sum_(h>=1)1/[h(exp(hx)-1)]<=pi^2/(6x).
This yields (3); negative w follows by conjugation. Absolute convergence
justifies the products and the limit. Finally h^2-|h|>=h^2/2 for |h|>=2
gives the lattice-sum upper bound. Thus every finite Toeplitz section is
accretive: Re <Tx,x> >= mu ||x||_2^2, by integrating its symbol against
the squared trigonometric polynomial of x.

For the broad gamma0=Theta(1/log p), the exponential in (3) is a fixed
power of p and the first factor is Omega(p^-2/log p). For the narrow
gamma0=Theta(log p) it is Omega(p^-2 log p). Hence Lambda,mu^-1=p^O(1).
Band truncation and coefficient rounding of total l1 error <=mu/2 preserve
accretivity, with mu/2, and retain the diagonal exactly one.

## 3. A safe version of the accretive circuit bound

Let T be an N-by-N accretive Toeplitz matrix, N dyadic, with norms as above.
The recursive block-LU circuit in SHALLOW-TOEPLITZ acts on intervals [a,b).
Every node is T_[0,b)/T_[0,a). The quotient identity for Schur complements
proves this by induction. All leading principal blocks have inverse norm
at most mu^-1. Therefore every node M satisfies

    ||M^-1||<=mu^-1,   ||M||<=Lambda+Lambda^2/mu=:Lambda'.

For its partition [[A,B],[C,D]], the shears have bounds
||A^-1 B||,||C A^-1||<=mu^-1 Lambda'. This uses Lambda', not the possibly
smaller norm Lambda of the original T. Put K=2+Lambda+mu^-1; all these
quantities are at most K^4. No repeated growth of the descendant bound occurs.

The nilpotent-shift displacement has rank at most 2 at the root and increases
by at most one at each child. The shear ranks are at most twice the node
rank plus three. These statements follow by multiplying the block identity
Z_(2m)=[[Z,0],[e0 e_(m-1)^T,Z]] and the Schur projectors. Thus the shear
rank is O(log N), independently of coefficients or positivity.

For a shear matrix U, its Stein displacement E=U-ZUZ* has rank O(log N).
Choose orthonormal column generators g_j and h_j=E* g_j. Telescoping gives

    U=sum_j L(g_j) U(conj(h_j)),

where the factors are triangular Toeplitz, ||g_j||_2=1 and
||h_j||_2<=2||U||. Choose an integer R>=2||h_j||_1 and put
P=I+U(conj(h_j))/R. To add one generator term to a dirty target y, execute

    x<-P x;  y<-y+R L(g_j)x;
    x<-P^-1 x;  y<-y-R L(g_j)x.

This adds exactly L(g_j)U(conj(h_j))x and restores x. P is within 1/2
of I in both 1- and infinity-norm. The independent parity-split triangular
compiler has O(log^2 N) rounds: the even and odd children run in parallel,
with two dirty Toeplitz shears. A dirty Toeplitz shear is the sum of a
circulant and a negacyclic-circulant shear, each using unitary FFTs and a
diagonal on the existing two dirty vectors, in O(log N) rounds. No clean
data coordinate is introduced. The exact formulas are retained in the
credited source; their parity, displacement and telescoping identities are
algebraic and hold also for the rounded rational kernel above.

There are O(log N) generators, giving O(log^3 N) rounds per shear and
O(log^4 N) rounds for the complete recursion. All gate coefficients and
the intermediates inside one generator are poly(N,K). Partial completed
generator sums add their norms; they do not multiply them. Along a recursive
path there are O(log N) unfinished/ancestor stages, each bounded by
poly(N,K), while disjoint paths are a direct sum. The deliberately
conservative bound sufficient here is

    log(max prefix, suffix, inverse-prefix norm)
       =O(log^2 N + log N log K).                     (4)

We do not need the sharper O(log N log K+log N) claim in the retained text.
Since N<=B=poly(p) and K=poly(p), (4) costs only polylog(p) guard bits.
Reversing and inverting the gates computes T^-1 with the same bound.

To generate coefficients, first use a rational rounded Toeplitz kernel
with the proved accretivity margin. Compute Schur matrices by exact rational
arithmetic. Their numerators/denominators are ratios of minors of a
polynomial-size matrix with polynomial-bit entries, hence have polynomial
bitlength. Exact elimination selects independent Stein columns. Rational
orthogonalization and square-root approximation produce the bounded
generators; nonzero rational residuals are separated from zero by
2^-poly(p), so a polynomial number of setup bits suffices. This is a
terminating polynomial-time coefficient algorithm, not a floating-point
rank oracle. Only the final bounded approximations are put on data tapes.

## 4. Join the actual dense blocks to their Schur pages

For each capped block, approximate the anchored diagonals in (1) or (2)
and the banded shifted Toeplitz kernel at Cp+O(q_B+log p) bits, where

    q_B=O(a theta B^2 + a theta B + log p).

Choose rational approximations that keep the diagonal factors nonzero,
and the Toeplitz diagonal one. Form the resulting rational block Atilde
*exactly* from those factors. Approximate original off-interior band entries
at matching accuracy and set exact zeros outside the band. This defines a
single rational finite-core matrix Mtilde, not incompatible interior and
boundary approximations. Its row and column perturbation from H_core is
at most 2^(-(C-o(1))p), uniformly in the core. Exact interior Toeplitz
structure is preserved by the construction, not inferred from a general
entrywise rounding of H_core.

Compute Stilde=Dtilde-Ctilde Atilde^-1 Btilde for precisely this Mtilde.
The whole-separator leading sections in CORE.md are Schur complements of
finite prefixes of Mtilde. All these prefixes and their interior sums
are perturbations of the corresponding analytic sections by the same
norm bound. For ||H^-1|| eta<1/2, the resolvent identity yields

    ||Mtilde^-1||<=2||H^-1||,
    ||Mtilde^-1-H^-1||<=2||H^-1||^2 eta.

This applies simultaneously to every needed prefix. Their no-pivot block
factors and inverses have polynomial norm and polynomial bitlength. All
boundary pages are for this same Mtilde. Rounding their final coefficients
and executing the solves uses the polynomial prefix bounds of CORE.md.
The exact six-stage product is Mtilde^-1; its perturbation from H_core^-1
has just been bounded. Thus the dense circuit and the boundary solver are
bound to one actual matrix, rather than merely to nearby unrelated formulas.

## 5. Tensor compilation on complete rows

On a length-L core axis, put all its disjoint capped circuits in parallel,
with identity operations on boundary sites. Their depth is polylog(p), even
when blocks have different dyadic lengths or origins. Regard each layer as
one matching on all L wires; no alignment with a dyadic subinterval is needed.
For m=log2 L, the retained Beneš compiler routes any matching to adjacent
pairs in 2m-1 switch layers, using its even-cycle coloring recursion.
Every switch is (1/2) H diag(1,+/-1) H. Adjacent shears, diagonals, swaps
and FFT butterflies have a common word with six H factors and seven
diagonals, with polynomially bounded coefficients and inverses. For zero
shears it uses U(t)=U(t+c)U(-c), c=2B_gate+1, avoiding division by t.
Padding uses identity operations, never extra data coordinates.

For each global stage, tensor multiplication of these words gives one
simultaneous H call on one named bit of each of the g axes, interspersed
with separable diagonal scans. The selected bit positions are the same
across coarse labels. **Execute that H call on the entire complete tensor
stream**, not separately inside a core block. The primitive may temporarily
borrow complete high bits of those axes and restores them before a diagonal
table is read. The true axis widths are superpolynomially larger than log p;
each has room for the required K=128(4 ceil(log2 p)+6) neighborhood.

The two primitive theorems used here are explicitly identified in
TRANSFER.md. Their support cost is O(V(g+1)^(1-a_eff) polylog p) for the
O(g log p) positions used, and the completed complex call costs
O(V g^(1-q) polylog p), q<a_eff. The normalized supplier returns H/2 on
each bit. One exact shift by 2^g per completed call recovers the raw H in
the compiler words; all its O(g) extra bits are in the bound below.

Between calls, generate each coarse block's g coefficient tables in polynomial
time. Nested coordinate enumeration maintains suffix products. A carry of
depth k occurs at most L^-k times per record and costs O(kL) coefficient
record moves, so sum_(k>=1)kL/L^k=O(1). Diagonal application consequently
costs O(V polylog p), including table rewinds, on fixed tapes. Complete
L^g payloads pay for setup; identities need no special zero data.

## 6. Total data width and roundoff

Tensor products multiply norms and add their logarithms. By (4), the
matching compiler, local chirps and scalar rescalings, the logarithm of
every group prefix/suffix amplification is at most

    O(g polylog p + g a theta B^2)=o(p).                (5)

The strict conditions are beta<1 and beta+2xi-2<1. Larger polylog factors
from (4) do not change either condition. The complex primitive's exact
internal grid adds C0*g bits with C0=2^210000, a fixed constant from the
native height proof. Since beta<1, this too is o(p). For the main transform
with O(d) active bits the same argument uses epsilon<1. No child is rounded
inside that primitive; its final layer rounding is what is charged here.

There are at most exp(O(p)) scalar records and at most polynomially many
stages per record. Converting absolute scalar roundoffs to 2-norm and back
can therefore cost exp(O(p)); (5) and all local polynomial factors add only
o(p) bits. Telescoping over perturbed gates, or the usual inhomogeneous
roundoff recurrence, proves that increasing the fixed leading constant C
delivers any requested 2^-C' p error in supremum norm on bounded inputs.
Rounded coefficients and arithmetic cannot invalidate this estimate: if
the total gate perturbation times the ideal prefix/suffix envelope is <1/2,
the perturbed envelope is at most twice the ideal one (expand by the first
perturbed gate, or solve the corresponding Gronwall inequality). Both
fixed-point integer magnitude and fractional bits fit O(p).

At completed group boundaries divide each one-axis Gaussian map by the
dyadic Z=2^ceil(100 log2 p), combining g powers into one scan. The exact
completed map is then a contraction in supremum norm; polynomially bounded
D factors and narrow inverse row norms are included. Restoring all such
normalizers takes O(d log p)=o(p) bits and one scalar scan at the stated
source-transform endpoint. A small numerical error at holes is retained
through the invertible square completion, then projected to zero at the
completed source boundary. That projection is a contraction.

The large original weights occur only in polynomial-precision setup.
The online invariant is O(p)-bit data, fixed tapes, complete restored
spectators and linear visited space. This is the precision assertion needed
by the physical primitive and by the final exact recovery argument.
