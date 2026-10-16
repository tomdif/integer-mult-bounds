# Broad forward conditioning, including finite physical prefixes

This instantiates the broad norm premise for whole periodic matrices and finite
line sections using the credited bilateral/finite Gaussian LDU argument. The
additions are an explicit extension to every b>0, both row and column norms,
and a precise physical-prefix Schur hypothesis. It remains
a written analytic proof, not a formalized matrix theorem or the complete
source-transform compiler. Credit: Vojdanovski's `BILATERAL-LDU.md` and
`FORWARD-SMALL-A-AUDIT.md`, with Boukhalfa's fine-prime parameters.

## 1. Finite factors and bounds for any positive b

Let rho=1+theta in (1,2], let q_i have successive gaps at least one, and suppose
beta_i=rho i-q_i lies in [-1/2,1/2]. On a finite principal interval [l,u] set

    G_ij = exp(-b ((rho j-q_i)^2-beta_j^2)),    b>0,
    x_i = exp(2b rho q_i),
    e_i = exp(-b rho^2 i^2+b beta_i^2),
    C_i(l) = product(l<=k<i)(1-x_k/x_i).

Finite Newton elimination of the Vandermonde matrix gives G=L C U, with

    L_ij=G_ij product(l<=k<j)(1-x_k/x_i)/C_j(l),        i>=j,
    U_ij=(e_j/e_i) h_(j-i)(x_l,...,x_i),               j>=i,

and h the complete homogeneous symmetric polynomial. The finite-origin row
diagonal in the Vandermonde form is `exp(-b q_i^2) x_i^l`, with powers j-l.
Using unshifted powers at a nonzero origin would give different factors.
The inverse formulas are

    Uinv_ij=(-1)^(j-i)(e_j/e_i) e_(j-i)(x_l,...,x_(j-1)),
    Linv_ij=(-1)^(i-j) exp(E_ij) C_i(l)/(C_j(l) D_ij),
    D_ij=product(j<k<=i)(1-x_j/x_k),
    E_ij=b[-beta_i^2+beta_j^2-rho^2(i-j)+2rho sum(j<k<=i)beta_k].

Here e_h is the elementary symmetric polynomial. The identities are ordinary
finite Newton interpolation/triangular inversion; the checker compares them
with exact rational matrices at translated origins, including b<1 instances.
Their mathematical use is the finite identities, not those samples.

Put `c_b=product(m>=1)(1-exp(-2b rho m))`. Positive q gaps imply
`c_b<=C_i(l),D_ij<=1`. Comparing homogeneous coefficients with the generating
product of variables 1,r^-1,r^-2,..., r=exp(2b rho), gives
`h_h(x_l,...,x_i)/x_i^h <= c_b^-1`. Comparing an h-subset with the largest
h nodes gives the same c_b^-1 bound for its normalized elementary polynomial;
the deficits form a partition. These comparisons require b>0, not b>=1.

Consequently L_ij and U_ij are at most c_b^-1 G_ij in magnitude. From the two
inverse formulas, using |beta|<=1/2,

    |Linv_ij| <= c_b^-2 exp(b/4) exp(-b rho theta(i-j)),
    |Uinv_ij| <= c_b^-1 exp(b/4) exp(-b rho theta(j-i)).

For example the upper exponent after replacing its elementary polynomial by
its largest-node product is
`b[beta_j^2-beta_i^2-rho^2(j-i)-2rho sum(i<=k<j)beta_k]`, at most
`b/4-b rho theta(j-i)`. The lower expression gives the identical decay.
The bounds depend on index distance, so they bound **both** row and column
sums by the same geometric series, uniformly in l,u. Since ||C^-1||<=c_b^-1,

    max(||G^-1||_1,||G^-1||_infinity,||G^-1||_2)
      <= c_b^-4 exp(b/2)/(1-exp(-b rho theta))^2.

The positive factors themselves have summable row/column envelopes because
`G_ij <= exp(b/4) exp(-b(rho |j-i|-1/2)^2)`.

For q_i=floor(rho i+1/2) with rational rho=t/s, pass l to minus infinity.
Products converge absolutely; each factor entry has the uniform bounds above.
Dominated convergence gives G=LCU, while products of triangular inverse factors
at a fixed entry use only finitely many indices. The factors are invariant under
simultaneous translation by s. Periodization is an algebra homomorphism by
absolute summability and has norm at most one in both induced row and column
norms: for columns, shift row indices along with each translated column.
Thus the same inverse estimate holds for the periodic normalized Gaussian.
No operator-norm convergence of finite sections is required.

## 2. Fine-prime parameters

For the broad forward map set

    a=pi alpha^2,   b=pi/(alpha^2 rho^2),
    alpha=ceil(sqrt((4/pi) log(16p))),
    1/(4p^2)<=theta<=1/p^2.

Expanding the nonnegative product logarithm and using exp(x)-1>=x gives

    log(c_b^-1)
      = sum(k>=1) 1/[k(exp(2b rho k)-1)]
      <= pi^2/(12b rho),
    c_b^-4 <= exp(a rho/3).

Also `1-exp(-b rho theta) >= b rho theta/2` eventually. For the actual square
selected-target block K, including its Gaussian diagonal normalization,

    ||K^-1||_(1,infinity,2)
      <= alpha exp(3b/4) c_b^-4/(1-exp(-b rho theta))^2
      = O(alpha^5 rho^2 theta^-2 exp(a rho/3)).

Eventually a<=5 log(16p) and rho<=6/5, so exp(a rho/3)<=(16p)^2. Together with
theta^-2<=16p^4 and alpha^5=O((log p)^(5/2)), this is O(p^6 polylog p), hence
at most p^7 for all sufficiently large p after absorbing the fixed constants.

For a contiguous interior of an original target phase cell, write q_j=j+c
and target coordinate k=q_j. The broad block is
`K_(k,i)=alpha^-1 exp[-(pi/alpha^2)(i-k/rho-c)^2]`. Its normalized Gaussian
description uses q'_k=k+rho c and beta'_k=theta k-rho c=beta_j. Thus q' has gap
one and |beta'|<=1/2. The finite proof above permits these nonintegral q' values;
it gives the same bound. Contiguous selected-source prefixes instead use the
original increasing q sequence, whose gaps are at least one.

## 3. Holes, truncation and the actual prefix geometry

Complete the broad forward map with identity columns at target holes. After
moving selected rows/columns first, the square completion is

    H_aug = [[alpha^-1 N_b D_b^-1, 0], [R,I]],
    D_b=diag(exp(b beta_j^2)).

The Gaussian lattice-sum bound, with both source/target spacings bounded below,
gives uniform O(1) row and column norms for the original broad map and R after
the alpha^-1 factor. The inverse of this block triangular matrix has blocks
`alpha D_b N_b^-1`, 0, `-R alpha D_b N_b^-1`, I. Thus its inverse has
O(p^6 polylog p) norms in all three senses. A contiguous physical target section
on the lifted line has the same block form with a contiguous selected-source
section and a subset of holes. The same bounds hold uniformly, independent of
its length. A proper principal section of the *periodic* matrix is not silently
identified with this finite line section: wraparound entries may remain.

Band truncation and reference rounding must have induced row/column error
eta=poly(p)2^-Cp (or any stronger stated bound), uniformly in period. The
Gaussian tail gives such a truncation error at W=O(sqrt(p) polylog p); the
coefficient generator must supply the rounding part. Since ||H_aug^-1|| eta
tends to zero, the resolvent identity/Neumann series preserves the bound,
with a fixed factor two, on all these principal sections simultaneously.
The truncated map has bandwidth W in physical order.

For an elimination in which the eliminated set is a contiguous physical prefix
and future interiors separated from each other and that prefix by boundary
groups of at least W vertices, require additionally that each proper cyclic
section used below is isolated across its cut by an omitted gap wider than W.
The truncated eliminated matrix is then
a direct sum of the sections just bounded. This assertion uses the actual
carving order; it is not true for arbitrary interleaved elimination sets.
Its inverse has the same O(p^6 polylog p) bound. A surviving Schur block obeys

    ||S|| <= ||H_BB|| + ||H_BI|| ||H_II^-1|| ||H_IB||
           = O(p^6 polylog p).

For its inverse use its embedding as a principal block of the inverse of the
corresponding contiguous completed physical section. The block-inverse identity
gives the same O(p^6 polylog p) bound. This covers completed Schur maps and
physical prefixes satisfying that geometry. The conservative p^10 umbrella
is valid eventually for these broad matrices. It has not yet been bound to
every terminal cyclic prefix of the actual outer schedule.

More explicitly, a leading boundary section includes the original physical
interval through its last boundary group, together with the immediately adjacent
eliminated interior at each exposed end. Only these adjacent/intervening interiors
couple to its boundary rows; all other eliminated interiors form disconnected
blocks. Eliminate those included interiors in this extended physical section to
obtain the leading Schur section exactly. At a period cut the extension is a
cyclic interval, represented on the lifted line when its omitted gap is wider
than W; the full-period case uses the periodic inverse directly. This explains which contiguous-section bound is used
when a prefix ends next to an eliminated interior.

The proof requires actual reference rounding bounds and the stated prefix
geometry. It does not prove stability of arbitrary structured generators or
an arbitrary elimination order, and supplies no fast tensor layout by itself.
Those claims must not be inferred from this conditioning estimate. In particular,
if a proper cyclic prefix leaves a smaller omitted gap, cross-cut band entries
survive and need a separate inverse argument or a different boundary schedule.
The global periodic inverse bound alone does not bound inverses of all its
principal submatrices. That terminal-cut join remains open here.
