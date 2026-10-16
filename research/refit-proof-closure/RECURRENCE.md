# Direct weighted induction to constant-width leaves

The previous proof's h-dependent stopping threshold is unnecessary once the
compact spacing is K=128G=O(log p). This note proves that simplification under
the same native dispatch and primitive implementation contracts. It does not
turn a cost recurrence into a physical implementation of its premises.

Let H be the actual terminal-refit histogram in `complex_core.py`, W=66304,
m=73, and

    C = 0.001722052684227397319529,
    q = C - 2*10^-104,
    a = C - (3/2)*10^-104,
    tau = 1-a.

The pinned directed rational moment enclosure establishes

    mu_C = sum_r (H_r/W)(r/73)^(1-C) < 1.

Every rank satisfies 1<=r<=48<73. Since a<C, tau>1-C and thus

    mu = sum_r (H_r/W)(r/73)^tau <= mu_C < 1.

The retuned ordinary primitive has saving a1=0.0017270071>a, so it supports
the slower exponent tau. Fix p for the root and absorb all its fixed
logarithmic factors into a multiplicative L(p)>=1. The source-bound node
cost has the form

    T(V,e) <= A V e^tau L(p)
               + Gamma sum_r H_r T(V/(W Gamma), r floor(e/73)),   e>=73.

This statement presupposes that each child receives its whole packet, that
all node work is local, that scalar passes and descriptor preparation are
charged, and that the copied row stock is restored. Those are implementation
obligations, not consequences of the inequality.

For e>=1 seek the bound T(V,e)<=B V e^tau L(p). In a nonleaf,

    Gamma sum_r H_r [B V/(W Gamma) (r floor(e/73))^tau L(p)]
        <= B V e^tau L(p) mu.

Choose B>=A/(1-mu). Then A+B mu<=B, so the desired bound is a supersolution.
Every child has strictly smaller width, since r floor(e/73)<=48 floor(e/73)<e.
For the finitely many leaves 1<=e<73, elementary execution costs O(Ve),
which is at most 73 times the same bound after increasing B once. Width zero
is a separate identity branch with O(V) copying if an owned output is needed.
Strong induction proves the bound for every width, including all floor cases.

The generic strong-induction step is `weightedClosure` in Closure.lean. Its
premises are printed in full and include the recurrence, child decrease,
nonnegative weights and supersolution. It does not assume a completed child
at the same width, and it introduces no new axiom for a machine or a moment.

Successive deferred phases retain at most 1/16 of the selected bits while
their width is at least 512. Since tau>0, their costs sum to at most

    B V h^tau L(p) / (1-16^-tau),

plus a fixed-size direct tail. Reservoir exposure has the same or smaller
exponent by ROUTER.md, and padding is removed between phases. Since a>q,
this is O(V h^(1-q) polylog p). For h=O(p^eta), eta>0 fixed, the strict gap
also absorbs any fixed logarithmic powers if an unadorned weaker exponent
is needed. The existing root-grid height proof remains valid: descending
farther only follows the all-width recurrence it already proves.

This eliminates a stopping-parameter side condition. The primitive rate,
full current-word semantics, actual dispatch locality and outer analytic
transfer still require their own proofs. The new induction does not supply
them by renaming its premises.
