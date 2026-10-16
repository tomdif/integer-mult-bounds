# Finite cores, whole separator pivots, and variable-coefficient faces

This note supplies the missing cyclic-boundary join in the fine-prime halo
supplement. It uses finite principal cores for the fast path and a polynomial
inverse on the separately copied faces. It never solves a nearly complete
proper principal section of a cyclic matrix. This is a modification of the
algorithm, not a proof that those cyclic sections are well conditioned.

The core/first-face layout and the finite-core interpretation are due to
Vlado Vojdanovski's PR1673 (PHASE-LAYOUT-AUDIT and the phase assembly audit).
Chafik Boukhalfa's PR1786 supplies the enlarged scales. The new joins here
are the variable-coefficient polynomial comparison, the explicit prohibition
on cutting a separator pivot, and the resulting finite-line stability proof.

## 1. Reference operators and scales

Let p tend to infinity. All constants below are fixed independently of p,
the period and the input data. An actual target axis has dyadic length t,
with log(t)=Theta(p^(1-epsilon)), epsilon<1. In particular t exceeds every
fixed power of p eventually. Its source length is s, rho=t/s=1+theta,
1/(4p^2)<theta<=1/p^2. The nearest image is

    q_j=floor(rho*j+1/2),    beta_j=rho*j-q_j.

Extend q_(j+s)=q_j+t and beta_(j+s)=beta_j to the lifted integer line.
There is at most one source at each target position; unused target positions
are holes. All holes are assigned to the boundary in the carving below.

There are two square target-grid reference matrices. For expansion, add
identity columns at the holes to the broad Gaussian map

    K_(k,j)=alpha^-1 sum_(m in Z) exp[-(pi/alpha^2)(j+ms-k/rho)^2],

placing source column j at physical target column q_j. For compression, put
the normalized narrow Gaussian N=C T D on the selected rows/columns and the
identity on holes; here D_j=exp(a beta_j^2), a=pi alpha^2. Thus the second
completion is E N C+(I-EC). Both definitions fix the coefficients across the
true period cut; they are not constant-coefficient convolution matrices.

Take alpha=ceil(sqrt((4/pi)log(16p))). Truncate Gaussian entries outside
physical band W=C_W ceil(sqrt(p) log p), choosing the fixed C_W for the
desired constant multiple of p accuracy. Truncate each lifted Gaussian
summand by the distance of its physical row and column *before* periodizing;
then set the narrow diagonal exactly one. Thus a retained band entry has
only its unique nearby lift, with remote periodic aliases deleted. Call
these banded references H. Gaussian tails give, in both induced
row and column norm, error at most poly(p) exp(-c W^2/log p).
This is below 2^-Cp for any prescribed fixed C, eventually, with this W.
The broad and narrow estimates proved in ../fine-prime-halo-closure give

    ||H||_2, ||H^-1||_2 <= p^10,

both on the whole periodic axis and on every finite lifted physical interval.
The broad estimates also hold in 1- and infinity-norm. For the narrow map,
row gap and bandwidth give the spectral bound as in NARROW.md. Sections on
the lifted line have diagonal one and retain their row gap. The Gaussian
tail perturbation preserves all these statements uniformly in interval size.
Larger fixed thresholds absorb constants. Coefficient rounding is treated
separately in PRECISION.md; it is not silently included in this definition.

Set

    L=2^ceil(128 log2 p),   A=ceil(p^48),
    gamma=2^-ceil(log2(p^20)),   J=2p^42,
    P_J(H)=gamma sum_(j=0)^(J-1)(I-gamma H*H)^j H*.

Eventually L divides every t and 4A<L<t/2. The predecessor proves

    ||P_J(H)-H^-1||_2 <= e_p := p^10 exp(-p^2),
    bandwidth(P_J(H)) <= (2J-1)W < A.

The same estimate holds for the inverse of each finite core section. On an
arbitrary smaller halo section only the polynomial is used: invertibility
of that halo section is unnecessary.

## 2. Core locality is an operator comparison

Partition the physical target axis into length-L intervals I. R_I restricts
to I and E_I extends by zero. Let R_I^deep select coordinates at distance
at least A from the complement of I. Expansion uses H_I=R_I H E_I; compression
uses its inverse H_I^-1. Since I is shorter than t/2, H_I is exactly the lifted
finite-line section, even for the first and last cores of the period.

Expand P_J into words in H and H*. A nonzero term contributing to an output
at x follows at most 2J-1 edges, each of physical length at most W. If x is
deep in I, every vertex in that path belongs to I. Therefore, as maps from
the entire periodic input space,

    R_I^deep P_J(H) = R_I^deep E_I P_J(H_I) R_I.

Consequently

    ||R_I^deep(H^-1-E_I H_I^-1 R_I)||_2 <= 2 e_p.       (1)

This uses two inverse approximation estimates and an exact finite-path
identity, not a supposition that an inverse is exactly banded. The forward
version is exact for distance W. Inputs outside I are not assumed zero.

For g axes, keep the dense-core output only where every coordinate is deep.
Apply the telescoping identity for a difference of tensor products to (1).
With K=p^10, each core restriction has error at most

    2g e_p (K+2e_p)^(g-1)

in spectral norm. Converting from bounded scalar inputs, or collecting all
cores, loses at most exp(O(p)): the entire addressed data rectangle has
2^O(p) scalar positions. Since g=O(p^beta), beta<1, the tensor factor has
logarithm O(g log p)=o(p). Thus the retained deep outputs have error
exp(-p^2+O(p)), below 2^-Cp for every fixed C. No dense output near a core
edge is used as an input for a correction.

## 3. The sparse faces do not require translation invariance

Partition the discarded outputs by their first boundary axis j and low/high
side. The output intervals are

    i<j: [A,L-A),  i=j: [0,A) or [L-A,L),  i>j: [0,L).

Their necessary input rectangles are respectively

    i<j: [0,L),  i=j: [-A,2A) or [L-2A,L+A),
    i>j: [-A,L+A).

Indices outside a core are copied from the actual neighboring core, including
periodic wrap. The layout, enumeration, radix gather and inverse merge of
HALO-THEOREM depend only on these intervals. They do not use translation
invariance of the numerical coefficients. The copy count is exactly

    M=6A V/L^g sum_(j=0)^(g-1)L^j(L+2A)^(g-1-j)
     =3V[(1+2A/L)^g-1]=O(VgA/L).                        (2)

Process one such rectangle at a time. On each axis apply the polynomial
P_J of its actual lifted finite section, then crop A sites from each end.
For a forward map apply H and crop in the same fashion. Path locality says
that every retained output equals the global polynomial on that axis. Maps
on distinct tensor factors commute, so earlier crops leave every input
needed on the remaining axes. At the end the rectangle equals the required
restriction of tensor_i P_J(H_i). Its error against tensor_i H_i^-1 is at
most g e_p(K+e_p)^(g-1), with the same harmless exp(O(p)) conversion.

This establishes the variable-coefficient replacement for the numerical
convolution step of HALO-THEOREM. Only its movement and counting argument is
reused verbatim. It would be incorrect to reuse its convolution algorithm
for these varying Gaussian coefficients.

The predecessor's explicit Horner routine performs at most O(p^44 polylog p)
bit operations per input bit, including schoolbook scalar multiplication;
we retain the ample p^50 bound. Its section norm is at most ||H||_2<=p^10.
Thus I-gamma H_section*H_section has spectrum in [0,1], even if the section
is singular. Each partial Horner sum has polynomial magnitude. Rounded
arithmetic loses only polynomial factors in the error, including its J
iterations. Sections have polynomial length; their coefficient pages can
be generated in polynomial time and reused over complete right-hand sides.

Sequentially exposing one polynomial-length axis temporarily pads only that
axis by less than two; the padding is removed before exposing the next.
There is no simultaneous 2^g padding. The fixed collection of radix bucket,
input, output and Horner work tapes is reused. Keys have O(p) bits, so the
ordinary sparse radix sorting and metadata arithmetic fit below p^50.
The one dense copy-enumeration scan remains O(V polylog p) per group.
Across d/g groups, the incremental cost from (2) is

    O(V d g A p^50/L)=O(V p^(epsilon+beta-30))=o(V).

## 4. Carving finite cores into capped dyadic interiors

On each length-L line, first separate the original phase cells, holes and
the two endpoints. Reserve at least W sites at each phase-cell/endpoint
boundary. Inside a remaining constant-offset run, repeatedly choose a dyadic
interior of size at most B=2^floor(xi log2 p), leaving a W-site separator
after it. Choose the largest power of two no larger than min(B,R-W) when
the current remainder R>4W; otherwise declare the remainder boundary.
Merge adjacent boundary pieces. Since B>4W eventually, all chosen interiors
are longer than W. Runs of full-size interiors contribute O(L/B) separators;
the geometrically shrinking final remainders contribute O(log B) per phase
cell or clipped end. Thus

    |boundary|/L=O((W/B) polylog p),

since phase cells have length Theta(p^2), B<p^2 and L>=B. All separator
groups have O(W) sites; merged short phase cells cause only a fixed increase
in that bound because phase cells are much longer than W eventually.

Write the core matrix in interior/boundary order as M=[[A,B0],[C0,D]].
Different interior blocks do not couple. A is a direct sum of capped
dyadic blocks, and S=D-C0 A^-1 B0 couples only identical or neighboring
separator groups. The endpoints of this finite core are ordinary line
endpoints. There is no cyclic wrap block in S.

## 5. Stable boundary pivots must end at whole groups

Let the ordered separator groups be J_0,...,J_m, with intervening interiors
I_1,...,I_m (empty endpoint interiors may be included). Use exactly these
groups as the block pivots. Do not replace them by arbitrary fixed-width
chunks that can end inside a separator.

The leading Schur section on J_0 union ... union J_k is obtained by taking
the finite physical prefix through the end of the immediately following
interior I_(k+1), and eliminating all interiors in that prefix. Other future
interiors have no edge to the selected boundary rows, so eliminating them
does not change this section. At k=m use the whole core. The prefix is
contiguous; no unselected tail of J_k is included. This proves the identity,
including the extension past J_k that is necessary to include its coupling
to I_(k+1).

Both this prefix and its interior direct sum have polynomial norm and inverse
norm by the finite-line estimates. The block inverse identity gives

    ||S_lead^-1|| <= ||M_prefix^-1|| <= p^O(1),
    ||S_lead|| <= ||M_prefix|| + ||M_prefix||^2 ||A_prefix^-1||
               <= p^O(1).                              (3)

The next block pivot is a Schur complement of S_lead. Its inverse is the
corresponding principal block of S_lead^-1. Its norm follows from the same
Schur formula. These estimates are uniform in the number of cells. They
also survive exponentially accurate coefficient perturbations, as proved
in PRECISION.md. The special argument about a nearly full cyclic prefix
from the predecessor is therefore unnecessary for this schedule.

There are only L=poly(p) scalar positions on a core. For completeness,
polynomial pivot bounds imply polynomial *solve-prefix* bounds here. The
unit lower and upper block factors have O(L^2) entries, each polynomially
bounded by (3). For every completed leading block,

    L_lead^-1=U_lead S_lead^-1,
    U_lead^-1=S_lead^-1 L_lead.

Hence their norms and those of their inverses are polynomial in p. An
unfinished forward/backward substitution consists of such a prefix solve,
one block product and a subtraction. This bounds all its intermediates by
a fixed polynomial times its input norm. Summing the polynomially many
rounding errors loses only polynomial factors, so O(log p) extra guard
bits suffice. This avoids multiplying a pivot-condition bound L times.

Apply each O(W)-square factor to batches of between W and 2W right-hand
sides with the explicit Strassen formula. Its depth is O(log W), its
integer encoders have bounded coefficients, and its recursion has cost
O(W^log2(7)) including scans/rewinds by depth-first evaluation. The sum of
live child arrays is geometric and each recursion level's additions have
the same geometric bound. Absolute error amplification is W^O(1), by
induction on that fixed formula. Since 7^16<2^45, the usable exponent is
tau=45/16. Padding one matrix block or the final RHS batch is a constant
factor and creates no tensor axes.

The online boundary cost per axis is consequently

    O((V/B) W^(tau-1) polylog p).

Original coupling blocks B0,C0 involve only O(W)-sized endpoint slabs and
have the same or smaller cost. Shortening/merging separator groups changes
only constants. The complete spectator payload supplies superpolynomially
many RHS records for every prefix; in particular the last active axis still
has d-g complete spectator axes. Polynomial factor setup and incomplete
batches are therefore amortized. All factor pages and workspace fit O(V).

## 6. Exact stage order and the union schedule

The inverse core map executes, in chronological order,

    diag(A^-1,I), E_-C0, diag(I,S^-1),
    diag(A,I), E_-B0, diag(A^-1,I).

Direct block multiplication gives M^-1. Reverse the order and invert each
factor for M. The two sparse windows use only the boundary plus the interior
sites incident to the ORIGINAL B0,C0; they never use a dense A^-1 B0 as a
supposedly sparse block. Scatter the union before every dense interior stage.

Apply the retained radix-distributed union schedule to each sparse window.
An axis factor changes membership only inside its own complete E_i line,
so the set of flagged axes is invariant. Processing the r-th flag on the
shrinking stream S_r and undoing its order by the retained LIFO indicators
executes every nonidentity axis factor exactly once. Operators on different
axes commute. The incidence identity is

    sum_r |S_r|=sum_x |flags(x)|=sum_i |U_i|
               =O(V g W polylog(p)/B).

Every round touches only S_r, including the rewind, variable-row transpose
and untranspose. Its bit cost is O(|S_r| polylog p) in bit-volume units.
Headers of O(g log L)=o(p) bits fit the record. No scan of the entire union
is made once per axis. Across groups, movement is
O(V d W/B polylog p), and arithmetic is O(V d W^(tau-1)/B polylog p).

This completes the finite-core and face composition. Its remaining use of
the dense capped circuit is discharged in PRECISION.md. It has not proved
a statement about arbitrary cyclic principal inverses, and does not need one.
