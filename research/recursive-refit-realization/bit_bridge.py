"""Retune the completed p=1 ordinary caller without changing its primitives.

The code and written machine argument belong to PR2753/2809/2899. This
module selects a stronger, certified rational point and proves stock fit
without reusing the predecessor's parameter-specific cutoff.
"""
from fractions import Fraction as Q
import json
from pathlib import Path
import sys

from common import ROOT, module, need, ordinary_sources

C = Q(173, 100000)
SAVING = C * (1 - C)


def arithmetic():
    directory = ROOT / "research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/vendor/e8-r740-replica32/code/engines"
    first = module("refit_first_moment", directory / "moment.py")
    second = module("refit_second_moment", directory / "base_two_moment.py")
    expected = json.loads((ROOT / "research/e8-bit-p111-tuned/tune/EXPECTED.json").read_text())
    h = {int(k): v for k, v in expected["nine"]["profile"].items()}
    need(h == {1:381024, 2:400416, 3:22752, 4:26880,
               5:29376, 6:17376, 7:26784, 42:288}, "selected BIT profile")
    fallback = 32 * 64**2 * sum(h.values())
    a = first.moment(h, 64, 28416, C, True)
    b = second.moment(64, 28416, h.items(), C)
    bad = second.moment(64, 28416, [(1, fallback)], C)
    b = tuple(x+y/10**16 for x, y in zip(b, bad))
    need(max(a[0], b[0]) <= min(a[1], b[1]), "two independent enclosures intersect")
    upper = max(a[1], b[1])
    linear = (Q(sum(r*n for r, n in h.items()), 64*28416)
              + Q(fallback, 10**16*64*28416))
    need(linear < Q(199,200) and upper < Q(99999,100000), "strict induction margins")
    # A proposed larger point must be rejected by a lower enclosure.
    too_large = Q(174,100000)
    lo = second.moment(64,28416,h.items(),too_large)[0]
    lo += second.moment(64,28416,[(1,fallback)],too_large)[0]/10**16
    need(lo > 1, "reject inadmissible c=0.00174")
    # Quantified stock fit: for x=log2(e)>=32,
    # 2k/e <= 26992(1+x)/2^(3x/4)+2/2^x < 1.
    # Both terms decrease on x>=32 (ln 2 > 1/2 suffices).
    fit = Q(26992*33, 2**24) + Q(2,2**32)
    need(C < Q(1,4) and fit < 1, "all-width borrowing envelope")
    need(2**22-1 >= 64, "fitted body is non-leaf above 2^32")
    need(2**17 * 42**28 < 64**28 and Q(28*4097,17) == 6748,
         "lcm stock logarithm coefficient")
    ledger = json.loads((ROOT / "research/paired-terminal-refit/evidence/OUTER-LEDGER.json").read_text())
    row = ledger["rows"]["struct_boundary_radix_union"]
    target = Q(row["kappa"]["rational"])
    effective = Q(row["a"]["rational"])
    need(SAVING > effective > target, "ordinary rate supplies the outer effective router")
    return {"c":str(C), "ordinary_saving":str(SAVING),
            "linear_moment":str(linear), "fractional_upper":str(upper),
            "slack_lower":str(1-upper), "induction_constants":[200,100000],
            "fallback_count":fallback, "uniform_fit_from":2**32,
            "fit_ratio_at_cutoff":str(fit), "target_margin":str(SAVING-target),
            "effective_router_margin":str(SAVING-effective),
            "rejected_point":str(too_large),
            "scope":"Exact parameter theorem; predecessor physical implementation arguments remain credited dependencies."}


def physical_setup():
    ordinary_sources()
    from encoded import Profile, atom_width, select
    from cardinal_counts import Count
    from scratch_pool import ScratchPool
    from session import sealed_constructors
    from check_support import no_decode
    from check_setup import decode
    profile = Profile(numerator=C.numerator, denominator=C.denominator)
    need((profile.dimension,profile.child_rank,profile.row_factor)==(64,42,269241600),
         "retuned production profile keeps the selected caller")
    pool = ScratchPool(64)
    roots = []
    for value in (1,2,64,10000):
        original = Count.literal(value)
        with no_decode(), sealed_constructors(), pool.install():
            width = atom_width(original, profile.numerator, profile.denominator)
            observed = decode(width)  # independent observer, never passed to runtime
            need((observed-1)**100000 < value**173 <= observed**100000,
                 "retuned encoded ceiling-power oracle")
            roots.append([value,observed])
            width.close()
            pool.empty()
        original.close()
    # Exercise the identical encoded selector with reduced stock. This is a
    # machine-interface test, not a selected GL64 payload execution.
    reduced = Profile(numerator=173, denominator=100000,
                      dimension=2, child_rank=1, row_factor=6)
    value=512
    original=Count.literal(value)
    with no_decode(), sealed_constructors(), pool.install():
        plan=select(original,3,reduced)
        observed={k:v if k=='fits' else decode(v) for k,v in plan.items()}
        cursor=value;depth=0
        while cursor>=2:cursor//=2;depth+=1
        w=observed['width'];stock=(6*(9-1)*(9-3)*3**(4*(w-1)))**depth
        rows=1;k=0
        while rows<stock:rows*=3;k+=1
        need((observed['stock'],observed['rows'],observed['borrowed'])==(stock,rows,k),
             "retuned selector preserves exact stock and borrowing")
        need((observed['body'],observed['remainder'])==divmod(value-k,w),
             "retuned body decomposition")
        for key,item in plan.items():
            if key!='fits':item.close()
        pool.empty()
    original.close()
    return {"production_profile":profile.__dict__,"encoded_roots":roots,
            "reduced_q3_plan":observed,"peak_setup_leases":pool.peak,
            "scope":"Actual encoded parameter path under no-decoder/no-constructor guards; reduced stock test."}


def make_ordinary(*args, **kwargs):
    """Construct B1 at the proved point; call in a cold predecessor namespace."""
    ordinary_sources()
    from encoded import Profile
    from ordinary import Ordinary
    need("profile" not in kwargs, "the certified profile cannot be overridden")
    return Ordinary(*args, profile=Profile(numerator=173,denominator=100000), **kwargs)


if __name__ == "__main__":
    print(json.dumps({"arithmetic":arithmetic(),"physical_setup":physical_setup()},indent=2))
    print("PASS_REFIT_ORDINARY_BRIDGE")
