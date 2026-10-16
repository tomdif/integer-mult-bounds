"""Bind the new lemmas to the exact retained target and moment certificate."""
from fractions import Fraction as Q
from pathlib import Path
import json
import sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
from crt_layers import need


def verify():
    ledger=json.loads((ROOT/'research/paired-terminal-refit/evidence/OUTER-LEDGER.json').read_text())
    row=ledger['rows']['struct_boundary_radix_union']
    C=Q('0.001722052684227397319529')
    epsilon=1-Q(1025,1024*10**104)
    kappa=C-Q(1,10**46)-Q(1,10**70)
    q=C-Q(2,10**104)
    a=C-Q(3,2*10**104)
    for key,expected in [('epsilon',epsilon),('kappa',kappa),('q',q),('a',a)]:
        need(Q(row[key]['rational'])==expected,'literal proof parameter equals source: '+key)
    need(Q(ledger['complex_lower_pinned']['rational'])==C,'complex endpoint')
    upper=Q(ledger['native_moment'][1]['rational'])
    need(upper<1,'retained certified moment enclosure')
    margins={'old_scan_exceeds_target':epsilon-(1-kappa),
             'ordinary_above_effective':Q('0.0017270071')-a,
             'moment_monotonicity_gap':C-a,
             'direct_induction_above_requested':a-q,
             'outer_main_absorption':epsilon*q-kappa,
             'global_router_absorption':Q('0.0017270071')-kappa,
             'retained_moment_gap':1-upper}
    need(all(v>0 for v in margins.values()),'strict proof margins')
    return dict(status='PASS_PROOF_TARGET_BINDINGS',parameters={k:str(v) for k,v in
                [('C',C),('epsilon',epsilon),('kappa',kappa),('q',q),('a',a)]},
                margins={k:str(v) for k,v in margins.items()},
                scope='Exact arithmetic and authenticated retained enclosure; no new native or analytic admission.')


if __name__=='__main__':print(json.dumps(verify(),indent=2))
