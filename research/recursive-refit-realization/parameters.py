"""Exact strict inequalities for the new recursive core at the pinned target."""
from fractions import Fraction as Q
import json
from common import ROOT, module, need
from complex_core import PROFILE
from bit_bridge import SAVING


def run():
    ledger=json.loads((ROOT/'research/paired-terminal-refit/evidence/OUTER-LEDGER.json').read_text())
    row=ledger['rows']['struct_boundary_radix_union']
    C=Q(ledger['complex_lower_pinned']['rational'])
    q=Q(row['q']['rational']);a=Q(row['a']['rational'])
    b=C-Q(1,10**104);stop=Q(1,10**110)
    tau=1-a;sigma=1-b;lam=1-(q+a)/2;lamp=1-q
    directory=ROOT/'research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/vendor/e8-r740-replica32/code/engines'
    engine=module('refit_core_moment',directory/'base_two_moment.py')
    lo,hi=engine.moment(73,66304,PROFILE.items(),C)
    need(hi<1,"independent coarse-grid enclosure still resolves the pinned complex endpoint")
    chi=tau+(1-stop)*max(sigma-tau,0);leaf=sigma+stop*(1-sigma)
    margins={'B1_above_effective':SAVING-a,'q_positive':q,'sigma_moment_slack':1-hi,
             'lambda_above_tau':lam-tau,'lambda_above_sigma':lam-sigma,
             'lambda_above_internal':lam-chi,'lambdaPrime_above_lambda':lamp-lam,
             'lambdaPrime_above_leaf':lamp-leaf,'stop_positive':stop,'stop_below_one':1-stop,
             'outer_main_above_kappa':Q(row['epsilon']['rational'])*q-Q(row['kappa']['rational'])}
    need(all(v>0 for v in margins.values()),"strict recursive/outer interface margins")
    return {'complex_endpoint':str(C),'complex_moment_interval':[str(lo),str(hi)],
            'effective_bit_saving':str(a),'actual_B1_saving':str(SAVING),'q':str(q),
            'sigma':str(sigma),'tau':str(tau),'stop':str(stop),
            'lambda':str(lam),'lambdaPrime':str(lamp),'internal':str(chi),'leaf':str(leaf),
            'margins':{k:str(v) for k,v in margins.items()},
            'reservation_cost':'geometric deferred phases, no d^(1-c) preliminary scan',
            'conclusion':'O(V*h^(1-q)*polylog(p)) under the explicit primitive/realization contracts in PROOF.md',
            'not_proved':'outer FFT, gauge/conditioning, prime padding and exact integer recovery'}
