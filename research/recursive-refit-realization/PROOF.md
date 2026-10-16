# Recursive realization of the paired terminal refit

This is a source-bound **written composition proof**, with explicit primitive
premises. It is not a kernel proof of a Turing-machine multiplication theorem.
The new results are a stronger ordinary-call parameter, the actual refit's
complete recursive height ledger, a compact-to-binary executable handoff, and
a quantitatively sufficient deferred-row controller. The six Lean theorems
verify the stated all-width arithmetic implications. They do not postulate or
verify the implementation premises below.

## 1. Statement and the precise remaining boundary

Use the exact paired-terminal-refit source admitted in the previous complete
replay: dimension 73, 66,304 live families, 666 whole native invocations,
408 helper roles per invocation, eight private centres and 82 private zero
buffers. The input member hashes in INPUTS.json identify that execution.
Do not substitute PR2287's old R480/T16 word, 144 calls or 14,336 live rows.

Let p>=2 be global coefficient precision. Let 1<=h<=p be the number of selected
bits, on a globally complete binary address rectangle of O(p) bits. Each
selected bit has a disjoint K-bit neighbourhood, at the same relative offset,
where G=4 ceil(log2 p)+6 and K=128G. An original axis of length
Theta(p^(1-epsilon)), for any fixed epsilon<1, eventually has room for this
neighbourhood. Coefficient values may be correlated arbitrarily with every
coordinate and every live family. Complete fields need not contain zeros.
Records are long enough to absorb each fixed polynomial in p; equivalently
use the credited untouched-suffix construction, keeping that suffix outside
the whole call's support and temporary fields. Write V for logical bit volume.

The composition proves, **given the following source-level implementation
contracts**, an exact C tensor on the h selected bits and then a normalized
H0 tensor, with time

    O(V h^(1-q) polylog(p)),

fixed tape count, visited space O(V)+F_qradix, restored spectators and empty
owned work. Here q is the exact saving called `q` in parameters.py, strictly
below 0.001722052684227397319529. The radix in the bit construction is a
different, fixed, source-admissible odd prime Q>2^80.

The implementation contracts are:

1. The PR2753 source endpoint/root-coupling/local-cost argument and PR2809
   fixed-role refinement, completed by PR2899's two-call ordinary wrapper.
   Section 2 specializes these arguments to c=173/100000; it does not infer
   them from small tests. The unchanged nested sources are in vendor/pr2899.tar.
2. The sequential compact rotation/repair and monomial lowering of PR2250,
   with its separately charged polynomial descriptor work; and the
   support-exposure construction in vendor/support. Section 3 supplies its
   ordinary primitive and exact current monomial catalogue. The sparse
   support router itself has not been joined to the physical C0 interpreter
   by this package. Its fixed-tape realization remains a written dependency.
3. Exact native unary recipes, extended common-label semantics, owner charts
   and whole-call hosting identities in the pinned complete native admission.
   Those finite sources passed the earlier full replay. The generic tensor
   implication uses unary products/inverses and common-label scalar gates,
   never a tensor power of a sum-of-operators identity.

Under these contracts, complex-child correctness, recursion termination,
precision, complete row stock and the stated time/space estimates are derived
below. Thus there is no assumed completed complex child inside its own proof.
Proving a literal end-to-end machine theorem still requires the source-level
refinement/dependency boundary to be discharged, and the outer analytic
FFT/gauge/prime-padding/integer-recovery argument is entirely separate.

## 2. A sufficient ordinary primitive without a bootstrap assumption

The current PR589 BIT histogram is

    H={1:381024,2:400416,3:22752,4:26880,
       5:29376,6:17376,7:26784,42:288}, Wb=28416, mb=64.

Include the bad-class envelope F=32*64^2*sum(H)=118606528512 with density
at most 10^-16. Define

    mu_x = sum_r (H_r/Wb)(r/64)^x + (10^-16 F/Wb)(1/64)^x.

At c=173/100000, two independent directed rational engines enclose mu_(1-c).
They establish mu_1<199/200 and mu_(1-c)<99999/100000, with a lower bound
on the latter slack of approximately 0.000011199673410191. The c=0.00174
control has a lower enclosure above one and is rejected.

The inherited baseline caller, using only elementary digit interchanges,
therefore satisfies

    T(n,w)/V <= 200 C n + 100000 C n^(1-c) w.

Indeed each linear recursive term consumes at most 199/200 of the first
summand and each fractional term at most 99999/100000 of the second.
The remaining Cn+C n^(1-c)w pays C(n+w) for n>=1. Increase C once to cover
the n<64 leaves; handle n=0 by its empty/identity branch. Floors only shrink
child widths. The bad term is a maximum over j<=floor(n/64), bounded by the
same increasing inductive envelope. This is a strong induction, not a fit
to measured execution times.

PR2899's encoded selector already accepts fixed numerator and denominator
parameters. We set them to 173 and 100000, retaining dimension 64, maximum
rank 42 and M=lcm(28416,28425)=269241600. No primitive or source word changes.
The retuned selector computes the least w with w^100000>=e^173 by encoded
bisection. Its fixed powers, comparisons, countdowns and saturation rule
are the predecessor's. Changing two fixed integers does not introduce a
numerical width into finite control. Root coupling e<=w^(1/c) still bounds
the inherited history/preparation terms by fixed polynomials in w. Complete
high cubes absorb those polynomials as in the baseline argument.

The old cutoff 311311 was proved for c=17/10000 and is not reused. Set

    Kb=M |GL64(F_Q)| Q^(4096(w-1)), S=Kb^Db(e),
    Db(e)=0 (e<64), otherwise 1+Db(42 floor(e/64)).

Since Q>2^80>M, log_Q Kb<4097w. Also 2^17*42^28<64^28 and
(28/17)*4097=6748, so

    log_Q S < 6748 w (1+log2 e).

For e>=2^32, w<=2 e^c<=2 e^(1/4). With k=ceil(log_Q S) and x=log2 e,

    2k/e <= 26992(1+x)/2^(3x/4) + 2/2^x < 1.

Both terms decrease for x>=32: for the first, its logarithmic derivative is
1/(1+x)-(3/4)ln2<0, already using ln2>1/2. The exact value at 32 is below
one. Also floor((e-k)/w)>e^(3/4)/4-1>=2^22-1>=64. Hence every width above
this explicit conservative cutoff uses a fitted non-leaf body. Smaller
widths are a finite elementary fallback, absorbed into the fixed constant.

The unchanged chronological wrapper D-=H; F_I; D+=H; F_I; D=-D; D+=H
requires the unweighted ROOT and returns the ordinary chunk interchange.
Each F_I separately restores its padded row ordinal; padding is less than
two and is removed before the next arithmetic step. The same stock is reused.
Thus

    Tordinary(e)/V = O(n+n^(1-c)w+k+w)
                  = O(e^(1-c+c^2)),
    a1=c(1-c)=17270071/10^10=0.0017270071.

The binary rectangular completion changes volume by less than the fixed Q^2.
This a1 exceeds the current outer ledger's effective bit saving and the
headline saving. C0 uses elementary primitives; B1 uses C0; the complex
caller uses B1. No C1 or iterative bootstrap is required for this bound.

## 3. Bind the actual compact call and current monomials

compact_bridge.py replaces PR2250's reached `compact.ordinary` function with
the PR2899 binary engine. For equal fields with b bits, it supplies exactly

    width=b, prefixes=2^before, gap=2^between,
    suffix=record_bits*2^after.

The record suffix is part of the last field multiplicity. It is not dropped
or treated as a single bit. A sequential copy places the upper payload on
one persistent borrowed input port. The binary engine returns a distinct
owned result. Another sequential copy returns it to the upper representation;
the binary output is consumed before reuse. Counts use a fixed sixteen-role
pool, suspended while the binary engine uses its own pool. The owned input,
count bodies and markers are explicitly erased at final return. Each copy,
rewind and erasure costs O(V); no address-dependent seek occurs.

The upper PR2250 simulator still represents descriptors as Python integers.
Their polynomial arithmetic is a written refinement premise, not a unit-cost
claim. The join tests the actual ordinary call seam, both source orders, and
a separate fitted reduced body reaching two completed C0 roots. It does not
execute the selected enormous GL64 rectangle. Its small compact tests reach
B1's elementary branch; the fitted test is explicitly a dimension-two fixture.
The fixture's `source_restored` field refers to the source address coordinate
of the completed shear. The upper payload tape is consumed and replaced by
the returned tape, as required by the compact API.

For a native monomial

    |x> -> i^(p0+q(x)) |M x XOR b>,

PR2250's binary elimination yields a finite row-add/flip word. Its f-column
version uses compact simultaneous selected-bit XOR, and applies the phase
f*p0+sum_j q(x_j) before the affine word. The inverse reverses the affine
word and evaluates the negative phase on recovered input columns. Offsets
repeat in each column; a role-scalar coefficient is unchanged, not raised
to the f-th power. Raw quadratic rows follow the native strict-upper convention.

complex_core.py checks all 3,780 distinct monomials in both providers' child,
endpoint, helper-wrapper and warp catalogues: 1,935,360 complete column
checks of forward/inverse affine maps and phase convention, with at most
59 binary gates. It additionally executes an actual newly present rank-zero
warp on full Gaussian records and its inverse. Existing native admission
supplies the exact unary frame identities; the present check supplies their
binding to this compiler, not a replacement native producer.

The literal `warp` has a matching signed rank-zero recipe and contributes
no child or numerical height. A `zero_buffer alloc` creates a distinct Z
role and clears it; `free` clears before release. Clear is valid ordinary
linear scratch semantics, without the BIT transported-source erasure rule.
All 82 such roles are confined to cleanup, and no recursive child is invoked
while one is live. Copies, ADDs and SCALEs only read allocated roles. The
eight C roles are initialized before reading. These are checked in both
22,353-event directions of both current providers.

## 4. Whole-call semantics and the complete recursive invoice

For each current native call and common cover element d, gather its 632
distinct owner packets. Use the literal owner chart to identify the physical
cover class, retaining all unused rows, compact coordinates and spectators.
Apply the common-view monomials, run the entire local word with the exact
centre and Z lifetimes, undo that view, and scatter every completed owner.
No later call begins before this whole invocation has finished. The owner
families are distinct within each call; the pinned hosting audit supplies
the disjoint pending-axis pieces and untouched chronological windows.

At a relabel use its actual right monomial, a single child on rf consecutive
selected slots, and its actual left monomial. At a wrapper use the declared
entrance and terminal maps, in their stored direction. All recipes act on
the full function space. The common-label invariant transports every scalar
gate on arbitrary correlated arrays, so exact unary lifting closes the
f-column endpoint. The helper's unit scalar row/column gives the whole-call
hosting endpoint, including dirty inputs.

The 2,222-event global schedule has 666 local calls, 666 bridges, 740 idle
sweeps, 74 terminal translations, 74 exchanges and the two final global
events. At every original idle deadline, perform the positive remaining
child if present and then the original translation, even when rank is zero.
There are 165,760 original idle slots, 57,181 positive idle children and
20,032 zero-rank slots with nonzero translations. Omitting the last class
changes a delta record's address. The terminal Y translation stays before
the signed exchange; the cover correction stays after the complete global
word. The prior native/global admission checks their unary identities and
common labels. Tensor lifting preserves that order and those identities.

The new independent ledger reconstructs, per cover element,

    H={1:1620396,2:428904,3:191980,4:73260,5:24951,
       6:167,7:45,8:5328,24:1,32:207,48:26958}.

There are 2,372,197 children, rank mass 4,816,512, 14,887,098 local events
and 149,184 bridge ADDs. Finite source bindings and counts are not an
all-size payload execution. The all-size implication is the induction here.

At width e, first execute the fewer than 73 remainder axes and retain them
as completed spectators. Every positive child has width rf with
f=floor(e/73), 1<=r<=48, hence rf<e. A direct leaf executes elementary C
kernels. Strong induction on e proves exact endpoints and spectator/work
restoration once the named monomial/scalar/parking primitives are supplied.

## 5. Complete rows and deferred reservoirs

Let

    Gamma=|O(73,2)|=2^1296 product_(i=1)^36 (2^(2i)-1),
    L=66304 Gamma, ceil(log2 L)=2644,
    D(e)=0 (e<73), otherwise 1+D(48 floor(e/73)).

The odd orthogonal group fixes the all-one vector and restricts to the
72-dimensional symplectic group; its ordered-basis count gives this Gamma.
Since 73^2>2*48^2, D(e)<=2 ceil(log2(max(2,e))). At a phase with h remaining
selected chunks reserve

    q0=ceil(2644 D(h)/K), qF=ceil(2hG/K), qB=ceil(hG/K).

The first q0 chunks form the row field, the next qF supply two hG-bit front
fields, and the last qB supply one hG-bit back field. These regions are
disjoint. Extra bits are spectators. For h<=p and ell=ceil(log2 p),

    2644 D(h) <= 5288 ell <= 11*128*(4ell+6)=11K,

so q0<=11. Further,

    R(h)=q0+qF+qB <= 11+ceil(h/64)+ceil(h/128)
                     <= 3h/128+13 <= h/16  (h>=512).

The exact last inequality and the all-width row capacity are kernel checked.
At h<512 finish directly, so no reservation is attempted. deferred.py uses
interval descriptors to finish every original selected bit exactly once;
it does not allocate an h-element list for the proof's large-width cases.

Do not preprocess the reserved selected bits. They are arbitrary dirty
coordinates during this phase. Expose the active chunks, pad the row range
once to a multiple of L^D(h), and run the core only on unreserved selected
bits. Since 2^(q0 K)>=L^D(h), padding is below two. Decode each node's rows
as [66304] x [Gamma] x [U]. A child receives the *whole* U range, so its
volume is v=V/L and its required L^D(child) divides U. Nothing from a compact
field is consumed as row stock. Completed siblings reuse the restored rows.

At a completed core endpoint the row coordinate is fixed; padded zero rows
are again zero and are deleted before inverse exposure. Only then start the
next deferred phase on its R(h) selected chunks. Thus padding never compounds
across phases. Completed phases act on disjoint original selected bits.

Unlike the older support notes' externally stocked bit primitive, B1 here
borrows inside each equal-chunk call and restores before returning. No
additional complex-level BIT row factor is needed. This is justified only
because Section 2 supplies the completed ordinary interface with arbitrary
complete spectators, including nonbinary preceding row multiplicities.

Support exposure uses the credited coordinate permutation supported on the
union of the source neighbourhoods and destination chunks, at most 2hK
positions. The support-router's reservoirs and optional short-record suffix
must stay in the working prefix and outside any grouped suffix. All coarse
labels remain complete; a fixed-coarse-label microbox is not a valid input.
Complete every deferred phase and restore exposure before the next diagonal
table scan. If the address is too short for these reservoirs or the untouched
suffix, its length is O(h polylog(p)); the retained full-span router then has
the same O(V h^tau polylog(p)) bound. In the intended regime h=O(p^eta),
fixed eta<1, and address length Theta(p), the O(h log^2 p) support reservoirs
fit eventually. This removes the old preliminary
d^(1-spacing) scan and the resulting epsilon*(1+spacing)<1 restriction.
It does not remove the explicit support-router implementation premise.

## 6. Common-grid height: actual events to all recursion depths

Prove the ideal algorithm over Q[i] first. An incoming array has height t
when its entries lie in 2^-(p+t) Z[i] and have absolute value at most 2^t.
A completed C tensor on u bits has dyadic denominator dividing 2^u and
absolute row sum at most 2^u. Its *returned* height is at most t+u;
its internal scratch guard does not accumulate after it returns.

For a dyadic coefficient a/2^k, binary Horner prefixes have magnitude below
2^b times the source magnitude, b=bitlength(|a|). Charge max(b,k), and one
additional bit for an ADD into an existing target. This covers intermediate
numerators *before* division; merely charging |a/2^k| would be wrong. The
largest actual b and k are both three. Copy/clear and unit-phase monomials
increase neither height nor denominator. The reconstructed scalar-prefix
charge including all bridges is Hscalar=25,101,614 per cover element.

Put

    s=Gamma*4,816,512, E=2^100000, B=s+E, C0=2^210000.

The exact check gives Gamma*Hscalar+32*73<E. The small remainder kernels,
C-pair arithmetic scratch and normalizations fit the explicit 32*73 slack
per internal node; a direct leaf has additional height at most 8e. Only one
child is unfinished under depth-first evaluation. All previous children
have returned endpoints, whose total width is at most s floor(e/73).
Therefore the maximum additional coefficient height satisfies

    A(e)<=8e at a leaf,
    A(e)<=A(48 floor(e/73))+s floor(e/73)+E otherwise.

Because 2B(73-48)>=s+E and B>=4, strong induction gives A(e)<=2Be.
`heightBound` verifies this for every natural width, not just tested widths.
The W denominator belongs in the time recurrence and **not** in s.

Before an unfinished deferred phase, the completed phases contribute only
their completed widths. These plus the active width do not exceed the
original h. Consequently all phases together, including normalization,
have height at most (2B+18)h<C0 h. `deferredHeight` verifies this implication.
Do not add a fresh C0h guard once per child or once per phase.

Choose Delta=ceil(C0h) once at the root. Store real and imaginary components
on the grid 2^-(p+Delta), with p+Delta fractional and Delta+3 integer/sign
bits. A height-t numerator is divisible by 2^(Delta-t). Before division by
2^k the corresponding height charge guarantees t+k<=Delta, so discarded
bits are zero. Headroom bounds every signed temporary. Thus fixed-grid
execution simulates the ideal algorithm exactly. There is no rounding at
a child return, phase return, buffer allocation or ordinary-call boundary.
Bit routines may temporarily rearrange arbitrary encoding bits; interpret
them as coefficients only after their completed return.

For h<=p this word width is O(p), with a large fixed constant. For h=o(p),
Delta=o(p) as well. The final normalized H0 tensor preserves the unit disk.
Truncate toward zero only after it completes: each real/imaginary error is
less than 2^-p, and the complex error is at most sqrt(2)*2^-p.

## 7. Time, fixed tapes and visited storage

Let mu_x=sum_r (H_r/66304)(r/73)^x. parameters.py independently encloses
the complex moment at the pinned endpoint with an upper bound below one.
Use b=C-10^-104, sigma=1-b, the outer effective a=(q+b)/2, tau=1-a,
and stop=10^-110. Section 2 supplies a strictly faster ordinary primitive,
so using exponent tau is valid. Stop complex recursion below
max(73,h^stop), with h fixed for the current phase. The exact rational-power
comparison has fixed exponents and polynomial descriptor complexity.

The Gamma cover copies cancel against each child's volume V/(66304 Gamma).
All source selection/replacement scans, scalar passes, parking and bounded
remainders cost O(Vnode). Fixed monomial words and complete compact calls
cost O(Vnode ((e log p)^tau+1)). Polynomial control preparation is paid by
the long record in every packet, including after row splits. There is no
per-bit random lookup and no child per individual unused row.

The strict weighted-tree estimate gives leaf cost
O(V h^(sigma+stop*(1-sigma))) and internal cost
O(V h^chi polylog p), where

    chi=tau+(1-stop)*max(sigma-tau,0).

The checked exact inequalities place both below 1-q. Include exposure at
O(V h^tau polylog p), a single padding/removal and the bounded direct tail.
Since successive phase widths are at most h/16, their powers sum as a
geometric series. This proves O(V h^(1-q) polylog p) under the stated
primitive contracts. The positive outer gap epsilon*q-kappa can absorb
these logarithms; that arithmetic does not prove the outer reduction itself.

A fixed set of canonical roles suffices for 66,304 families, 632 local owner
copies, eight centres, 82 Z buffers, scalar scratch, selection/replacement
and monomial scratch, and encoded descriptors. Scalar coefficients and
monomial words are finite source data; they do not add tapes with recursion
depth. Supply independent fixed banks for B1, completed and empty before
each complex child. A conservative W+1024 complex packet/control-role
allowance covers the stated local roles: at most 32 coefficient-word
temporaries (b,k<=3), eight payload selection/replacement streams, the
compact stream/key/two-bucket inventory and fixed control work. Ordinary
backend roles are separate and may depend on the fixed prime Q.

Park the inactive parent roles and program counter at a delimited stack
top, move the active whole packet to child I/O, and reuse the fixed roles.
At return retain the result on a distinct port, clear child-owned work,
restore the parent in reverse order and commit the result. No child reads
buried ancestor data; every primitive is local to its own delimited regions.
The credited parking codec has linear cost in current parked bits, including
empty-role delimiters. A constant source number of such boundaries per node
contributes O(Vnode), with source constants permitted to include Gamma.

At depth j the active volume is V/L^j. All live parent payload, duplicated
packets and metadata are O(V/L^j), with long-record absorption as above.
Summing the active stack gives O(V)/(1-1/L). A reusable tape visits only the
largest dense prefix used for its role; count erased cells as well as live
ones. Fixed tape count bounds those maxima by a constant times the same
geometric sum. The support/ordinary routines contribute their own O(V)+F_Q
space while active, and release it before complex descent. Deferred phases
run sequentially with removed padding. Hence visited space is O(V)+F_Q,
uniform in ancestor contents and stack offset, under the locality premises.

## 8. What this proves and what it does not

The current refit's all-width numerical guard and stock/reservation arithmetic
are now explicit, source-bound and partly kernel checked. Its actual compact
ordinary seam is executable against the physical predecessor. The old coarse
bit saving and old R480 ledger are no longer silently substituted for it.

This package does **not** establish an unconditional multiplication theorem.
It does not emit or kernel-verify the complete complex fixed-role dispatcher,
prove the upper Python descriptor model's physical correspondence, or execute
the sparse support router through the same physical backend. Those are the
remaining implementation/refinement obligations. The exact finite native
admission and credited source-level primitive proofs remain dependencies,
with no claim of independent human review. The FFT/convolution, conditioning,
prime-padding and exact recovery proofs remain outside this package.
