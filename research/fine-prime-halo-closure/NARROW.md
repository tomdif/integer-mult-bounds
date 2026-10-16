# Uniform spectral bounds for the narrow Gaussian and its banded Schur sections

This discharges the p^10 norm premise for the **narrow** banded reference
matrix and the retained banded Schur/prefix geometries, provided the stated
reference rounding error is met. It does not apply this argument to the broad
forward Gaussian, which is not diagonally dominant. All bounds below are
independent of the physical period or the number of phase cells.

## 1. A banded row-gap lemma

Let A be a finite real or complex matrix with line/circular bandwidth b, maximum
absolute row sum at most M, and absolute row diagonal-dominance gap at least
delta>0. Thus `|a_ii|-sum(j!=i)|a_ij| >= delta`. Let D be its diagonal and
R=I-D^-1 A. Then

    ||R||_infinity <= q=1-delta/M < 1,
    ||D^-1||_infinity <= delta^-1,
    A^-1 = sum(k>=0) R^k D^-1.

Every row entry of R^k has magnitude at most q^k. Its bandwidth is at most kb,
so a column has at most 2kb+1 possibly nonzero entries, even on a circle (this
bound may exceed the dimension, which is harmless). Therefore

    ||A^-1||_1
      <= delta^-1 sum(k>=0)(2kb+1) q^k
      <= M/delta^2 + 2b M^2/delta^3.

The direct maximum-component argument gives the better row norm
`||A^-1||_infinity <= 1/delta`: for `Ax=y`, take an index maximizing |x_i|
and use `|y_i| >= delta |x_i|`. Interpolation of induced matrix norms yields

    ||A^-1||_2^2 <= M/delta^3 + 2b M^2/delta^4.

Likewise `||A||_1 <= (2b+1)M`, so `||A||_2^2 <= (2b+1)M^2`.
These are elementary finite-dimensional inequalities. They require no bound
on matrix dimension, inverse-entry decay from a Gaussian LDU, or normality.

Bandwidth cannot simply be omitted: set A=I-(1/2)u e_0^t, where u_0=0 and
u_i=1 otherwise. Its row gap is at least 1/2 and its row norm at most 3/2,
but A^-1 e_0 has squared length 1+(n-1)/4. Its spectral inverse norm is
unbounded with n. The checker retains this exact adverse family.

## 2. Scalar elimination preserves the gap and row bound

For an eliminated pivot k, its nonzero diagonal is guaranteed by the gap. For
each surviving row i, the Schur update and triangle inequalities give

    gap_i(new) >= gap_i(old) + |a_ik/a_kk| gap_k(old),
    row_sum_i(new) <= row_sum_i(old) - |a_ik/a_kk| gap_k(old).

The first follows by bounding the new diagonal below and all other entries
above; the second bounds every entry above. Thus any sequence of exact scalar
eliminations preserves gap delta and row bound M. Principal sections preserve
both as well. This is valid for signed/complex fill, not just positive entries.

Apply the lemma of section 1 to each resulting Schur matrix **in its retained
physical boundary ordering**. Its bandwidth hypothesis must still be checked.
Here that is the established carving geometry: interiors are intervals
separated by width-W boundaries; elimination connects only the two neighboring
O(W) endpoint groups. The physical boundary ordering therefore has bandwidth
O(W), even after a contiguous boundary prefix has been eliminated. Future
interiors are disjoint sections. The same reasoning covers a period cut using
the circular order. This is not a bandwidth claim for arbitrary elimination
orders on arbitrary banded matrices.

## 3. Actual fine-prime narrow row gap

Use the original source-grid coordinates, `rho=1+theta`,
`beta_i=rho i-q_i in [-1/2,1/2)`, with nearest-grid gaps q_i-q_(i-1) in {1,2}.
The normalized narrow Gaussian row at offset h has coefficient

    exp(-a ((rho h+beta_i)^2-beta_(i+h)^2)).

The diagonal is one before periodic aliases. For the two nearest offsets,
the grid-gap constraint implies the respective exponents are at least
`a(1+2theta-2beta_i)` and `a(1+2theta+2beta_i)`. Their sum is at most
`exp(-2a theta)+exp(-2a(1+theta))`, by convexity in beta on its interval.
For |h|>=2 the exponent is at least `a(h^2-|h|)`, whose entire two-sided tail
is at most `4 exp(-2a)` for a>=1. Hence

    off_diagonal_row_sum <= exp(-2a theta)+5 exp(-2a).

This is the credited sharp row estimate of Vojdanovski's
`LOG-A-PHASE-SCHUR-AUDIT.md`; the derivation above states the ingredients used.
Nonzero periodic diagonal aliases belong to its tail. Delete those aliases
and fix the reference diagonal to exactly one, as in the retained construction.

For the fine-prime choice `theta>=1/(4p^2)` and `a>=4 log(16p)`, a>=1 and

    1-exp(-2a theta) >= 1-exp(-1/(2p^2)) >= 1/(4p^2),
    5exp(-2a) <= 5/(16p)^8 <= 1/(8p^2),       p>=2.

Thus the unrounded narrow row gap is at least 1/(8p^2). Gaussian band truncation
only reduces the nonnegative off-diagonal sum. Require the actual reference
coefficient/weight-ratio perturbation to have row norm at most 1/(16p^2), and
keep its diagonal exactly one. The rounded banded H then has

    delta = 1/(16p^2),       M <= 2.

The high-precision positive-weight setup is necessary for that perturbation
premise. This lemma does not validate a generator that rounds the tiny absolute
weights to merely Cp bits; such underflow would invalidate the premise.

For the retained W=O(sqrt(p) polylog p), every needed physical Schur bandwidth
is eventually at most p. Sections 1 and 2 now give

    ||A||_2^2 <= 4(2p+1),
    ||A^-1||_2^2 <= 8192 p^6 + 524288 p^9 <= p^20,  p>=4.

The final inequality holds at p=4 and remains true after division by p^20,
since both terms decrease. The first bound is also below p^20. Therefore the
uniform `||A||_2, ||A^-1||_2 <= p^10` premise used by the halo proof is supplied
for the narrow reference, its principal sections, and these banded Schur
sections, at all sufficiently large p. The finite initial range has the
retained fallback. Direct sums preserve the same spectral bound.

The broad completed map and its Schur sections still need their own uniform
conditioning argument; strict narrow row dominance cannot be transferred to
them by analogy. Online setup accuracy, capped circuits and full transform
assembly remain explicit obligations of contract T.
