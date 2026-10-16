# A fixed-tape dispatcher for the current terminal refit

This is a constructive written refinement, relative to the credited binary
interchange/compact routines and the pinned native algebraic certificates. It
closes the dispatcher premise left in `refit-proof-closure/RECURRENCE.md` by
specifying physical row selection, every opcode, recursive call boundaries,
and return. It is not a formalized Turing-machine theorem. The finite executions
below are evidence for particular components, not a proof of the quantifiers.
The outer source-transform contract T remains a separate open obligation.

## 1. Quantified interface and a finite expansion of the roles

Fix the refit's dimension 73, W=66304, and

    Gamma = |O(73,2)| = 2^1296 product(i=1..36)(2^(2i)-1),
    L = W Gamma.

The following machine has **L permanent row tapes**, plus 632 local packet
tapes, eight centre tapes, 82 zero-buffer tapes, a fixed descriptor/arithmetic
inventory, child I/O, parking and the fixed B1 work inventory. L is an absolute
constant, independent of precision, input length, recursion depth and selected
width. This expansion is allowed in the fixed-multitape model. It is neither
practical nor an improvement of the source's 66804 optimized workspace invoice.
It is the reason packet selection below needs no fast computed-key sort.

Enumerate all 73-by-73 binary matrices lexicographically and retain those
with D^t D=I. This is a terminating, input-independent compilation procedure.
It produces the finite group, its products/inverses, the right-multiplication
permutations of its indices, and constant role selectors. It may be compiled
into finite control; it is not an input-dependent array of tapes. An equally
valid implementation pays a fixed setup constant once. No materialization of
this table is claimed by the executable tests.

Use the original complete-row interface and deferred schedule of
`recursive-refit-realization/deferred.py`: the unused row range R at width e
is divisible by L^D(e), where D(e)=0 for e<73 and
D(e)=1+D(48 floor(e/73)) otherwise. At an internal call, decode the outer row
range as [W] x [Gamma] x [U], U=R/L. Every packet contains the **whole**
unused U range, compact fields, unselected bits and coefficient records.
Its logical volume is v=V/L, before counting copies or parked work. Children
retain complete rows; they are not invoked separately on each spectator row.

Global parameters p, K=128G and G=4 ceil(log2 p)+6 remain unchanged down the
recursion. The root selected width h is O(p^eta) for a fixed eta<1, and the
address rectangle has a complete untouched suffix of length at least
ceil(log2 p)^2 outside all selected neighbourhoods, row stock and compact work.
The earlier support router can expose such a suffix in the outer regime:
the total reserved support is O(h log p)=o(p), within Theta(p) address bits.
Alternatively the long-record hypothesis can be supplied directly. Treat
the suffix as part of each payload record throughout, including at leaves.
It absorbs any fixed polynomial descriptor cost per enlarged record. This
is an explicit interface condition, not a claim for arbitrary short records.

## 2. Row splitting and exact packet movement

Put the row coordinate outermost. Then each of the L owner packets is a
contiguous equal-length bit interval. Divisibility of the row range ensures
that interval boundaries are also complete-row boundaries. No field of a
coefficient or compact rectangle is split.

The input is a marked bit stream of N=Ln bits. With a residue state in
{0,...,L-1}, scan it without changing its bits and append one zero to an empty
clock tape after every L bits. Rewind input and clock to their left markers.
The clock contains n zeros. This uses O(N+n+1) unit moves; the counter belongs
to finite control because L is fixed. It never decodes the numerical value n.

For each of the L fixed target roles, advance input, that role, and the unary
clock together until the clock's right blank. Move the current input bit to
the empty role cell, erasing the input cell. Rewind the clock and target to
their marked origins, then select the next fixed role. At completion the
input is empty; rewind its erased region. A prefix induction proves that role
j contains exactly input interval [jn,(j+1)n), in the same order. All other
roles and every cell left of the markers are unchanged. The total charge is
O(N+Ln+L)=O(N+L), including every rewind and fixed dispatch transition.

Merge by visiting those roles in the same order, moving each stream into the
next blank cell of input, rewinding each emptied role, and finally rewinding
input. Erase the unary clock. This is the inverse movement and has the same
bound. Empty streams have O(L) cost; they do not justify a zero-cost claim.
`rows.py` executes these symbol tests and unit moves. Its recursive tests use
these actual routines where the predecessor used abstract split/merge shims.
The reported action counts exclude finite branch/dispatch expansion; adding
O(N+L) accounts for it and leaves the stated linear bound unchanged.

Internal calls have positive complete packets, hence N>=L and all this work
is O(V). The finite leaf routines do not need to split. Installing/removing
the fixed inventory's markers contributes a fixed constant, absorbed by the
positive-volume bound (and by the allowed fixed visited-space constant).

## 3. Owner selection and the common view

The original node input is now on the L row tapes, indexed (family,g). A
complete invocation has 632 distinct family owners. Its owner chart sigma
is the exact 73-column chart determined by its route:

* A data route [1,stage,port] uses the involution rho(stage,q), fixing q and
  exchanging its local eight-dimensional orthogonal complement with the
  stage's fresh eight axes. Stage zero is the identity.
* A helper route uses the retained orthogonal port basis. Place the exact
  ordered pending-axis slice first, then the recorded 9-width spectator
  columns, then the remaining columns in their original order. This is a
  complete orthogonal chart, including every spectator.

`charts.py` reconstructs all 420912 owner occurrences of the current 666
calls, checks their 10339 distinct charts, the actual helper widths, and their
untouched hosting windows. It does not reuse the old R480/T16 owner census.

For a common cover matrix d select the fixed role (family,g), where
g=d sigma^-1, and copy it sequentially to its local role. A fixed tape selector
costs one finite dispatch transition; a copy and its rewind cost O(v).
For each family the map d -> d sigma^-1 is a permutation of the entire cover.
Different owners in one invocation have distinct families. Thus different
d within a native sweep use disjoint complete owner packets, and gather and
scatter cannot overwrite another pending packet in that sweep.

For data, first apply the stored entrance translation X_(g a_in), and pull
back the packet by P_d^-1, columnwise on the 73 slots. The native program uses
the first nine slots; its common prefix is the declared spectator window.
After the complete program, apply P_d and the exit translation X_(g a_out).
Equivalently, translations inside the common view use d^-1 g a, **not the
unmodified physical mask a**. Helpers need only the common pullback/pushforward;
their entrance/exit monomials occur at their literal native positions.

Scatter the completed local packets to the same fixed row roles. Erase their
local copies and the zero-valued private centre/buffer streams before another
invocation. This final erase converts logical zero packets to marked-empty work
and is charged as another linear pass. Original rows were retained during
the whole call, so no partial update is visible to its caller. These copies
change working space by a fixed factor and do not change logical v.

All chart operators act on at most 73f selected positions. Gaussian elimination
of the fixed 73-by-73 binary matrix expresses its columnwise action as a fixed
number of simultaneous XOR/flip operations. The credited compact monomial
routine and the preceding support router perform these with arbitrary complete
spectators, restored work, and cost O(v(e+1)^tau polylog p). The unit phase is
computed once per enlarged record and applied to all its coefficients. Where
necessary, expose/retract the chosen slots with the preceding coordinate
router. The protected suffix is never part of their support.

## 4. Every native opcode and its scalar convention

`compile_native` lowers every actual event into the following closed alphabet.
The event index and provider/direction are part of the fixed program, rather
than a payload-dependent dispatch. Both providers have 22353 events in each
direction, lowered to 29305 primitives, including 3476 positive children.

| Native operation | Sequential implementation |
| --- | --- |
| phase marker | Stationary control transition; no numerical phase |
| scalar clear/copy/add/scale | Zero-fill, copy, or fixed dyadic arithmetic on aligned Gaussian components |
| warp | Its actual rank-zero monomial; no recursive child |
| climb or centre | Right monomial; one C^(tensor rf) child; left monomial |
| endpoint adapter | Stored monomial for old-to-new; its inverse for new-to-old; identity at frames 0 and 1 |
| residual pre/post | Inverse of the actual right/left monomial, using the full entrance:terminal key |
| zero-buffer alloc/free | Zero-fill private marked packet; at release erase the now-zero packet |

The scalar coefficient is **not** raised to f. A Gaussian monomial's constant
phase is multiplied by f modulo four, its quadratic phase is summed over the
f columns, and its affine displacement repeats in each column. These rules
follow by tensoring unary products/inverses and using linearity at scalar gates.
They apply to arbitrary arrays, including correlated dirty helper inputs.

Private centres use the literal copy/clear/gather word of their orientation.
The backward centre need not be an unmodified source copy. Zero buffers are
allocated only in the final cleanup section, contain the exact declared
zero input, and are freed after their last use. No positive child occurs while
one is allocated. Their physical roles exist permanently; allocation does not
create a tape. The retained finite algebra proves their final zeros. Clear and
free are therefore legal even though the global computation need not be
reversible on arbitrary private garbage.

All numerical arithmetic uses the one root dyadic grid of the previous height
proof, with guard Delta=ceil(2^210000 h). Fixed scalar numerators/denominators
are implemented by finite Horner additions, negation and binary shifts. C uses
((a+b)+i(a-b))/2 and ((a+b)-i(a-b))/2 on paired streams. Componentwise carry
scans, reversals/rewinds and clearing take O(p+Delta)=O(p) per coefficient.
The previous all-prefix height bound gives headroom and divisibility at each
division; children are never rounded. New copies, selectors, clocks and parking
do not increase numerical height. The original rank mass and scalar ledger
therefore remain valid. Leaves e<73 use at most 72 elementary C axes.

An exact dense reference executes all four whole native programs on arbitrary
deterministic Gaussian integer payloads at all 512 addresses. Its independent
oracle uses only C_q, C_all and the completed helper C tensors, not the child,
warp, endpoint or wrapper recipes. This is stronger than a count-only binding,
but is still a finite test, not all-input proof. The all-input algebra remains
the credited exact free-operator/native certificates and their tensor argument.

## 5. Global phases, idle calls and terminal order

The source data phase masks are in physical g coordinates. Their correctness
can be checked without evaluating 2^73 frequencies individually. For a vector
v the Fourier phase of C_v is parity(v dot z). Modulo four,

    parity(v dot z) = sum_i v_i z_i - 2 sum_(i<j) v_i v_j z_i z_j.

Every term of degree at least three vanishes modulo four. Thus comparing the
73 linear and 2628 quadratic coefficients proves equality on all frequencies.
A translation X_a has phase 2(a dot z), with no quadratic coefficients.
`phase_audit` applies this identity to every current data entry/exit and
original idle recipe. Equality at frequency zero fixes the scalar phase too.

Write A_s=C on the first 9+8s standard axes, and A_-1=C_q. The data labels
before stage s are X=A_(s-1), Y=A_(s-1) C_q^-1. At s=0 these are (C_q,I).
In native coordinates, the old source label is C_q and the old target output
label is C_all C_q^-1, with the declared prefix as a common spectator factor.
The verified entry and exit translations identify those routed labels with
the physical ones. Both data sides have the same respective alignment masks.

The literal event sequence first equalizes pair levels at idle deadlines and
then applies each signed bridge on common labels. The nine local scalar shears,
nine bridges and signed exchange have identity scalar shadow on eight data
registers; this small exact check is repeated independently. The same
common-label argument as for a native word composes their tensor lifts.

At each idle deadline, hosted pieces occupy a disjoint **prefix of the actual
ordered axes**. Invoke a child once on the remaining positive suffix, with
all spectators and U rows, then apply the recorded translation even if the
remaining rank is zero. This accounts for 165760 original deadlines and 20032
zero-rank cases with nonzero translations. Using ranks alone would lose them.

Apply X_(gq) to terminal Y **before** its signed exchange. Then apply the
all-live correction after the empty bank-padding tail. For each orthogonal g,

    delta_i(g) = (weight(row_i(g))-1)/2 mod 2,
    P_g C_all P_g^-1 = C_all X_delta(g).

To prove the second identity, expand the difference of the two weight phases
modulo four. Orthogonality makes its mixed quadratic coefficients zero and its
linear coefficients 2 delta_i. Its value at zero is zero. The final translation
therefore removes the defect. All these are unary identities and lift to every
f; the complete core returns C^(tensor 73f) on every original live row.

## 6. Recursive parking, return addresses and locality

At a positive child, all transient monomial/scalar scratch has already closed.
The active local packet has v bits. Keep every other occupied row, local packet,
centre and descriptor as a marked stream on a permanent role. Parent descriptors
include current width, row count/clock, layout, root-grid parameters and return
program point. They are parked like payload; none is left on work reused by the
child. The fixed program point can be encoded in a fixed-length marked record.

Apply the credited unequal-stream boundary: push inactive roles in fixed order,
move active to child I/O, run the child, move output back, and pop in reverse
order. If B is the fixed number of participating slots and P their total bit
length, the exact wrapper charge is

    5P - v + 9B - 2,

excluding the child and separately charged preparation. Here P=O(V) plus
polynomial descriptors, which the protected suffix absorbs. Zero/unused roles
are included in B, so their marker/dispatch overhead is not silently discarded.
Park the parent descriptor before constructing the child descriptor in cleared
work; erase the child descriptor on return before popping the parent. Shared
root parameters may be copied read-only, charging their polynomial bit length.

The child is the *same* machine on width rf <=48 floor(e/73)<e. All permanent
roles are empty at entry, except its explicit I/O and the parking stack, whose
top is its own boundary. Its row count U remains divisible by L^D(rf). It uses
its own local clock and markers and stops each scan at those markers. Induction
on width proves that it returns a length-preserving output, empty owned work,
the same parking top/contents, and a trace independent of buried ancestors.

This last property does not follow merely from endpoint restoration. Each new
primitive scans only its current marked region. The credited push/pop wrapper
reads no lower than the entry delimiter and writes no lower than the entry top.
The corresponding primitive contracts for B1/compact routines use their own
cleared work and never scan parking. Composition and induction therefore give
the same trace bounds for the complete dispatcher. There is no ancestor scan
or cost depending on the absolute stack height.

At node return, scatter every completed native/idle operation, merge all L row
roles, erase clocks/descriptors and scratch, and restore the input/output head.
Selected axes completed as a remainder are retained as spectators. The node's
logical layout, coefficient length, unused rows and compact fields are restored.

## 7. Cost, space and well-founded closure

An internal node executes a fixed finite number of row copies, scalar passes,
phase passes, monomial calls and wrappers. This number can contain W, Gamma and
the full program length; none depends on p or e. Their total cost is

    A V e^tau polylog(p),

where tau=1-(C-1.5*10^-104), C=0.001722052684227397319529. The earlier B1 saving
0.0017270071 is strictly larger, and the support/monomial costs obey this bound.
Every child retains exactly v=V/(W Gamma). Counting its actual rank with the
current histogram H, and looping over the finite cover, proves the concrete
node recurrence

    T(V,e) <= A V e^tau polylog(p)
               + Gamma sum_r H_r T(V/(W Gamma), r floor(e/73)).

There is no hidden call per spectator row. Descriptor and fixed-marker charges
are included in A; root setup is covered by the original fixed setup allowance.
The credited strict moment, together with the direct strong induction in
`refit-proof-closure/RECURRENCE.md`, now yields O(V e^tau polylog p). Its base
case is the finite elementary C routine, not a completed complex transform
assumed at its own width. The deferred widths shrink by at least 1/16 and sum
geometrically; this gives the claimed complex-layer bound at the weaker q.

At an unfinished child the parent occupies O(V), and active logical volumes
along a recursion chain are V,V/L,V/L^2,... . Their sum is O(V). The fixed
ordinary workspace is reused, and all descriptors fit the long-record charge.
Thus visited space is O(V)+F_Q on a fixed tape inventory. Large finite constants
are permitted but do not replace V in the normalized moment.

Root padding increases volume by less than two, once per deferred phase. It
pads complete rows, which are independent at the completed endpoint; the padded
zero rows return to zero and can be removed before the next phase. The earlier
single-pass normalization converts completed C into H0 with exact guarded
arithmetic. Truncation is performed only at the stated completed layer boundary.

This establishes a written dispatcher composition with explicit primitive and
finite-algebra dependencies. It does **not** discharge the outer uniform
fine-prime transform contract, its numerical error/recovery integration, or a
proof-assistant verification of the whole machine. Archive acceptance would
not validate these mathematical claims; independent review is still needed.
