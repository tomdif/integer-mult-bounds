# Exact replacement and a restricted-class lower bound

Number the wires in the order
`[8,12,31,37,40,45,73,78,81,86,105,110]`.
Each instruction is the elementary addition `x_d += x_s`, at frame 524.
`CANDIDATE.json` gives the original and new ordered lists and their exact
integer matrices. The verifier computes these matrices by evolving one basis
column at a time; it imports no search code.

## Scalar map, cleanup and frames

The two forward integer matrices are equal. Reduction modulo two proves
equality of the local bit maps for arbitrary inputs, including every value
left by the preceding part of the word. The replacement changes no instruction
outside this contiguous B block except the mandatory cleanup: C is regenerated
as the literal reverse of all z-destination gates in A followed by B, at the
full frame. This is exactly the original interface's H4 requirement.

The unchanged checker proves all H1–H5 hypotheses and U/J/K/U-inverse
conclusions separately, as well as the complete dirty-column endpoint.
Keeping the old cleanup happens to preserve the F2 endpoint, but violates H4;
this distinction is an explicit positive endpoint/negative interface control.

Every wire's sequence of distinct frames is unchanged. The COPY locations and
ranks are unchanged. Exact record interpretation therefore recovers the same
MOVE/COPY rank histogram and rank mass. The B block loses 15 ADDs and its
literal reversed cleanup loses another 15, giving 30 in total.

## Positive bounds

Let P be the forward nonnegative integer matrix and Q the matrix obtained by
executing the additions in reverse order with positive coefficients. The
certified relationships are `P_new = P_old` and `Q_new <= Q_old` entrywise.
Every intermediate row is nondecreasing during a positive addition program.
Thus equality/dominance of endpoint matrices controls every internal prefix
for any incoming nonnegative vector of row bounds. The surrounding unchanged
positive operations preserve this order.

Rather than rely only on that argument, Python and C++ independently replay
the complete ADD/COPY/ERASE streams in both directions. They obtain
`F=49347`, `B_old=1113070`, and `B_new=1057866`. The inherited payload formula
`64 F^3 B^2` gives
`8606440250798375406443864832 < 2^104`, with bit length 93.
These are cancellation-free local prefix bounds; no new hosted cost theorem
is inferred from them.

## Why the original two-factor scheduling class needs 27 ADDs

Split the original 41-operation word after its first 17 operations. Keep
the resulting two exact positive integer matrices fixed. In each factor's
class, each nonidentity destination row is written in one contiguous group;
other wires may be used repeatedly in that group. No wire permutation,
extra wire, negative coefficient, or interleaving of factor boundaries is
allowed. Identity rows remain unwritten. This class includes the original
factor programs.

A state S identifies the rows already written. Their current values are the
corresponding target rows; all other rows are unit vectors. To finish row d,
the donor multiset must sum over the integers to `target[d] - e_d`. The two
factor matrices are unit triangular after a permutation; this property and
an ordering are checked. Consequently every mixed state matrix is invertible
over both the integers and F2. There is at most one integer coefficient vector.

The generator finds subsets by F2 elimination and then checks their full
integer sums. The verifier instead performs integer triangular
back-substitution: a positive edge exists exactly when the solved coefficient
of d is zero and all other coefficients are nonnegative. In every feasible
state it separately verifies that those coefficients are already zero or one:
allowing repeated donors adds **no edges**. Thus the generator covers the
broader positive class. Edge cost is the sum of coefficients. The two methods
agree on all **32 + 2048 states** and
**72 + 9536 feasible edges**.

`FACTOR-COMPARISON.json` contains a distance value D(S) at every state.
The verifier checks `D(empty)=0` and, for every legal edge S→T of cost w,
`D(T)-D(S) <= w`. Summing this inequality along any complete schedule proves
its cost is at least D(full). Explicit legal programs attain D(full) equal
to **12** and **15**, respectively. Their concatenation therefore gives the
exact class minimum **27**.

The new whole-block circuit uses 26 ADDs, so it is outside that restricted
two-factor class. No lower bound of 26 for unrestricted positive circuits or
general XOR circuits is established. PR891's different whole-block
destination-once obstruction is credited as motivation, not imported as a
dependency of this proof.
