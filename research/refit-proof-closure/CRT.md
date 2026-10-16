# A logarithmic CRT layout, with its transform dependency exposed

This note proves a new algebraic factorization and a conditional implementation
bound. It repairs a specific missing cost row in the proposed outer assembly.
It does **not** prove the fast source-transform contract in section 4. Calling
that contract an FFT, or checking its exponents, does not discharge it.

The source CRT map is Douglas Colkitt's retained triangular map in
`upstream/build/sections/08-assembly.tex`, equations defining `P_i`, `mu_i`
and `b_i`. The normalized Fourier convention and retained frequency labels
come from section 07, `lem:chirp-permutation`. The factorization below is new
in this successor; no upstream file or previous certificate is changed.

## 1. The cost that cannot be silently dropped

The retained implementation makes d controlled rotations, each costing O(V),
in addition to its axis exchanges. `docs/nonadjacent-axis-audit.md` explicitly
retains this O(Vd) row. At the terminal-refit parameter point

    epsilon = 1 - (1025/1024) 10^-104,
    kappa = 0.001722052684227397319529 - 10^-46 - 10^-70,

epsilon > 1-kappa. Consequently this implementation does not establish the
desired O(V p^(1-kappa)) bound. This is a failure of that charged algorithm,
not a lower bound for CRT conversion or a disproof of the target theorem.
`oldScanExceedsTarget` checks the exact inequality in Lean.

The support router alone cannot remove the row. It permutes binary coordinate
positions. With source moduli (3,5), the valid input digits (1,0) map to
(1,2), changing the Hamming weight of their binary encoding from one to two.
A permutation of binary positions preserves Hamming weight. Thus calling
CRT a coordinate permutation would change the primitive's contract.

## 2. Exact factorization for every valid address

Index the pairwise coprime moduli by 0,...,d-1. Put

    P_i = product_(j<i) s_j,
    mu_i = P_i^-1 mod s_i,
    c_ij = mu_i P_j mod s_i  (j<i).

For a contiguous index interval I define

    Phi_I(a)_i = a_i + sum_(j in I, j<i) c_ij a_j mod s_i.

This is a bijection: recover the original a_i in increasing order, subtracting
the already recovered earlier digits. All intermediates have polynomially
many bits in p when sum log(s_i)=O(p), so this inverse is a polynomial-time
*descriptor* calculation. We do not charge it once per scalar coefficient.

Split I into consecutive left and right intervals L,R. For x on L, define

    delta_i(x) = sum_(j in L) c_ij (Phi_L^-1(x))_j mod s_i,  i in R,
    C_I(x,y) = (x, (y_i+delta_i(x) mod s_i)_(i in R)).

Then, on the full product of the valid coordinate ranges,

    Phi_I = C_I composed with (Phi_L tensor Phi_R).                 (1)

Indeed the parallel factor produces x=Phi_L(a_L) and y=Phi_R(a_R).
Substituting Phi_L^-1(x)=a_L supplies exactly the missing terms j in L
in every right output. The left outputs are unchanged. This proves (1)
without assuming linearity of the mixed-radix inverse across different
moduli. Using the transformed left digits directly is generally false.

Apply (1) bottom up on a binary interval tree. At each level, disjoint nodes
have disjoint controls and targets. Their C_I maps commute, and the completed
level consists of simultaneous cyclic shifts of all its target coordinates,
with offsets depending only on its control coordinates. There are
ceil(log2 d) levels. The inverse uses the reverse levels and negated offsets;
the controls are unchanged during the level being inverted.

`crt_layers.py` emits these levels, including a short final interval for
nonpowers of two. The exact oracle in `check_crt.py` independently forms the
ordinary integer k=sum a_i P_i and computes mu_i k mod s_i. It checks every
intermediate interval invariant, endpoint and inverse on the stated finite
boxes. These tests are evidence for the implementation; equation (1) is the
all-size proof. The abstract cancellation in (1) is also kernel checked as
`blockFactorization`, and each level's inverse as `conditionalShiftInverse`.

## 3. Execute one level without one scan per target

Let J be the target axes at this level and S_J=product_(i in J) s_i. The
retained source transform has a nontrivial frequency labeling:

    (F_J^- z)(k) = 1/S_J sum_j z(j) exp(-2 pi i sum_i t_i k_i j_i/s_i),
    (F_J^+ z)(k) = 1/S_J sum_j z(j) exp(+2 pi i sum_i t_i k_i j_i/s_i).

Here gcd(t_i,s_i)=1. Both transforms have infinity operator norm at most one,
and F_J^+ F_J^- = I/S_J. For fixed controls x, define the diagonal

    D_x(k) = exp(-2 pi i sum_(i in J) t_i k_i delta_i(x)/s_i).

If Shift_delta sends the input at j to output j+delta, the exact identity is

    Shift_delta = S_J F_J^+ D_x F_J^-.                             (2)

To prove it, the coefficient from input j to output y before the S_J scale
is the product of sums

    1/s_i^2 sum_(k=0)^(s_i-1)
        exp(2 pi i t_i k (y_i-j_i-delta_i)/s_i).

Each sum is 1/s_i when y_i=j_i+delta_i modulo s_i and zero otherwise,
by the finite geometric-series identity and the fact that t_i is a unit.
Tensoring and applying S_J proves (2). The retained frequency permutation
is therefore paid algebraically, with no separate address permutation.
The conjugated opposite-sign source transform is the required F_J^+.

Two normalizations matter: omitting S_J returns Shift_delta/S_J; omitting
t_i from D_x implements a different shift. The exact cyclotomic checker
rejects both errors, including composites for which t_i remains a unit.
`normalizedSandwichScale` checks only the final scalar cancellation, not the
Fourier or transcendental construction.

## 4. The precise fast-transform contract needed by (2)

For the *cost* implication, choose d to be the largest power of two at most
floor(p^epsilon). This remains Theta(p^epsilon); prime lengths, axis widths,
padding ratios and all strict exponent inequalities retain their powers.
The fixed comparison constants and finite cutoff must be adjusted. Each
nonempty binary-tree level then has exactly d/2 target axes. This avoids
invoking a many-axis fast bound on a root with just one target axis when
d is just above a power of two. The algebra for arbitrary d remains valid.

Required contract T: on any such set of d/2 named source axes, with all
other complete axes as arbitrary spectators, the retained forward and
opposite source-transform procedures compute F_J^-/F_J^+ to error 2^-P,
with P any sufficiently large fixed multiple of p, in

    O(V p^(1-kappa-rho) polylog(p)),  rho>0 fixed,

fixed tape count, linear visited space, restored spectators and cleared
owned work. V includes the actual O(p)-bit coefficient words. Padding is
the near-one source/target padding, not one factor two per axis. This must
hold uniformly for the actual fine-prime/gauge-free parameters. Contract T
is a named remaining analytic and implementation obligation in this package.

The intended call graph is acyclic: section 08's `source transform` uses
Gaussian expansion, the chirp convolution over dyadic axes, compression and
normalization. That chirp convolution uses the synthetic transforms and
established short integer products. It does **not** call the outer CRT map.
The source-transform proof can therefore be extracted and verified before
using it to implement (2). An unspecified fast *integer multiplier* would
not be an adequate substitute for this independently constructed contract.

First route all controls before all targets by the completed binary-position
router, carrying axis identities and widths. One full-address permutation
and its inverse suffice per level. Apply F_J^- with all controls as complete
spectators, the diagonal below, then F_J^+ and the exact S_J scale. These
are globally completed calls; the diagonal is evaluated only after temporary
spectator borrowing has been restored.

### Conditional phase generation is paid

For each fixed control tuple, recover the original digits of every left
block and compute all delta_i and roots

    w_i = exp(-2 pi i t_i delta_i/s_i).

This is a fixed polynomial in p per *whole target tensor fibre*. Every target
axis has superpolynomial length exp(Theta(p^(1-epsilon))), so the setup is
absorbed by that fibre. The collection of O(d) roots and running products
has polynomial size and uses a fixed number of tapes, not one tape per axis.

Enumerate target coordinates by a mixed-radix odometer. Retain the powers
w_i^k_i and prefix products on two aligned stack-like tapes. Updating the
innermost digit and emitting the product takes O(1) multiplications of
O(p)-bit scalars; carrying j levels costs O(j) such operations and head
travel O(jp). Across a complete fibre the number of level-j carries is at
most its cardinality divided by the product of the j fastest radices.
Since every radix is at least two, their sum, with the j factor, is O(the
fibre cardinality). Returning over a cached O(p)-bit scalar is charged.
Known quasilinear integer multiplication therefore gives O(V polylog(p))
for the whole diagonal. There is no descriptor scan of d axes per record.

Finite-precision repeated root multiplication is not treated as exact.
There are at most S_J<2^O(p) updates in a fibre, so a working precision
P+C p bounds the total drift by 2^-P for a sufficiently large fixed C.
Products of numbers with modulus 1+O(2^(-P-Cp)) amplify by at most two
beyond a fixed cutoff. The same allowance covers root evaluation and
prefix-product rounding. All online words still have O(p) bits.

### Error and recovery

If both normalized transforms and the diagonal introduce at most eta
absolute error on the bounded inputs, the exact contractions and unitary
diagonal bound the error of the three-factor composition by O(eta).
The final S_J scale makes it O(S_J eta). Taking the internal precision
larger by O(p) gives any desired 2^-Cp error at the completed shift.
The exact completed map is a permutation, hence a contraction; errors add
over O(log p) completed levels. Start with norm below 1/4 as in source08;
the total error can be made smaller than 1/100, so every next normalized
source-transform input stays inside its required 1/2 disk bound.

Use this approximate CRT map on the two normalized input coefficient arrays.
After the source convolution's first S scale, apply the inverse approximate
CRT **before** integer rounding, to the still bounded array w. Only then
multiply by 2^(2b+4)S and round. Retaining the old order, which rounded first
and supplied arbitrary integer payload to an approximate numerical routine,
would require a different argument. These extra errors are at most
poly(p)2^-Cp before the final factor 2^O(p); a larger fixed C keeps their
contribution below 1/4. The separately proved original chain must supply its
remaining error below 1/4. Unique-integer rounding and exact carries follow.
Invalid padded source coordinates are zero and are cleared at completed
source-transform boundaries. This is a numerical map on that subspace,
not a general bit-record interchange primitive.

There are O(log p) layers, O(1) transforms and full-address routes per layer,
and linear or quasilinear-in-record work otherwise. Under T and the router
bound, their strict gaps absorb these additional logarithms. Thus the new
CRT no longer contributes Vd. This proves the stated conditional repair;
it does not establish T by assumption or upgrade the headline to an
unconditional multiplication theorem.
