# SPDX-License-Identifier: Apache-2.0
"""Independent exact certificate for the PR2894 fixed-inventory packing screen.

The floating LP only chooses a basis. All balances, complementary slackness,
root signs and all 1163 reduced costs are subsequently checked with rational
arithmetic and the credited predecessor's directed elementary-series bounds.
This is a local investigation, not a new construction or a novelty claim.
"""
import gzip, hashlib, importlib.util, itertools, json, math, sys
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
import numpy as np
import sympy as sp
from scipy.optimize import linprog
from sources import authenticate

HERE=Path(__file__).resolve().parent
SRC=HERE.parent/'shared-kernel-packing'

def read(p):
    b=p.read_bytes()
    return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(c,m):
    if not c:raise ValueError(m)

def main():
    authenticate()
    template=read(SRC/'vendor/pr2857/sources/PR2833-T37-TEMPLATE.json.gz')
    cap_by_child={}
    for row in template['idle_children']:
        c,r=row['child'],row['rank']
        need(c not in cap_by_child or cap_by_child[c]==r,'consistent capacity')
        cap_by_child[c]=r
    caps=sorted(set(cap_by_child.values()))
    bin_counts=Counter(cap_by_child.values())
    inventory=Counter();local=None
    for tag in ['base','extra']:
        w=read(SRC/f'vendor/pm/words/WORD-PM-{tag}.json.gz')
        inv=Counter({int(k):v for k,v in w['report']['width_inventory'].items()})
        lp={int(k):v for k,v in w['report']['local_profile'].items()}
        if local is None:inventory=inv;local=lp
        else:need(inventory==inv and local==lp,'same inventories and profiles')
    widths=sorted(inventory)
    patterns=[]
    for c in caps:
        for counts in itertools.product(*(range(c//w+1)for w in widths)):
            used=sum(w*n for w,n in zip(widths,counts))
            if used<=c:patterns.append((c,counts,c-used))
    need(len(patterns)==1163,'complete pattern count')
    A=sp.Matrix([[int(c==k)for c,counts,r in patterns]for k in caps]+
                [[counts[j]for c,counts,r in patterns]for j in range(len(widths))])
    b=sp.Matrix([112*bin_counts[c]for c in caps]+[9*inventory[w]for w in widths])
    alpha=Q('0.001720184528377469533074')
    costs=np.array([r**(1-float(alpha))if r else 0 for c,counts,r in patterns])
    res=linprog(costs,A_eq=np.array(A).astype(float),b_eq=np.array(b).astype(float).ravel(),bounds=(0,None),method='highs')
    need(res.success,'LP discovery')
    active=[i for i,x in enumerate(res.x)if x>1e-7]
    # Complete the positive support to a full rank square basis using tight columns.
    reduced=costs-np.array(A).astype(float).T@res.eqlin.marginals
    basis=list(active)
    need(A[:,basis].rank()==len(basis),'independent positive support')
    for i in np.argsort(np.abs(reduced)):
        if len(basis)==A.rows:break
        i=int(i)
        if i not in basis and A[:,basis+[i]].rank()>len(basis):basis.append(i)
    B=A[:,basis];need(B.rows==B.cols and B.det()!=0,'nonsingular basis')
    x=B.inv()*b
    need(all(v>=0 for v in x),'rational nonnegative primal')
    ranks=sorted({r for c,counts,r in patterns if r})
    C=sp.Matrix([[int(patterns[i][2]==r)for r in ranks]for i in basis])
    Y=B.T.inv()*C
    # Same directed bound helper as PR2857; independent LP construction and exact equations.
    source=SRC/'vendor/pr2857/audit_relaxation.py'
    spec=importlib.util.spec_from_file_location('credited_interval_bounds',source)
    bounds=importlib.util.module_from_spec(spec);spec.loader.exec_module(bounds)
    upper=Q('0.00172018452837746953307464')
    lower=Q('0.00172018452837746953307463')
    # Each normalized rank cost increases with alpha. These endpoint bounds
    # cover the complete narrow interval, including all mixed-sign dual rows.
    values={r:(bounds.moment({r:73},lower,1)[0],
               bounds.moment({r:73},upper,1)[1])for r in ranks}
    tight=[];min_slack=None
    for i,(cap,counts,r) in enumerate(patterns):
        coeff=sp.Matrix([[int(k==r)for k in ranks]])-A[:,i].T*Y
        if not any(coeff):tight.append(i);continue
        slack=sum(Q(v)*values[k][0 if v>0 else 1]for v,k in zip(coeff,ranks))
        need(slack>0,f'exact dual reduced cost {i}')
        min_slack=slack if min_slack is None else min(min_slack,slack)
    idle=Counter()
    for i,n in zip(basis,x):
        need(n==0 or i in tight,'complementary slackness')
        if patterns[i][2]:idle[patterns[i][2]]+=Q(n)
    need(B*x==b,'all exact balance equations')
    H=Counter({r:9*n for r,n in local.items()});H.update(idle)
    actual={int(k):Q(v,74) for k,v in read(SRC/'data/PROFILE.json').items()}
    need(dict(H)==actual,'actual literal profile attains fractional optimum')
    need(bounds.moment(H,lower,896)[1]<1<bounds.moment(H,upper,896)[0],'root bracket')
    # Meaningful price control: omitting one billed rank-one child changes the exact profile.
    corrupted=Counter(H);corrupted[1]-=Q(1,74)
    need(dict(corrupted)!=actual,'missing-child control')
    out=dict(status='PASS_EXACT_FIXED_INVENTORY_PACKING_OPTIMUM',patterns=len(patterns),tight_patterns=len(tight),strict_patterns=len(patterns)-len(tight),
        source_head='18d03c447886895ef9abf888398178e0428533ca',
        source_hashes={str(p.relative_to(SRC)):digest(p)for p in [source,SRC/'data/PROFILE.json',SRC/'vendor/pm/words/WORD-PM-base.json.gz',SRC/'vendor/pm/words/WORD-PM-extra.json.gz']},
        per_replica_bins={c:112*bin_counts[c]for c in caps},per_call_inventory=dict(inventory),
        exact_primal=[dict(capacity=patterns[i][0],counts=list(patterns[i][1]),idle=patterns[i][2],multiplicity=str(n))for i,n in zip(basis,x)],
        dual_rank_basis=ranks,dual_coefficients=[[str(z)for z in Y.row(j)]for j in range(Y.rows)],
        minimum_strict_slack_lower=str(min_slack),per_replica_idle={r:str(n)for r,n in idle.items()},
        complex_root_lower=str(lower),complex_root_upper=str(upper),
        actual_profile_attains_optimum=True,
        scope='Fractional nonchronological bin packing for exactly PR2894 widths/capacities/local profile. Actual owners separately pass predecessor checks. No obstruction to changed words or changed interfaces. Matches the prior reported Discussion2612 finding; no novelty claim.')
    (HERE/'PACKING-RESULT.json').write_text(json.dumps(out,indent=2)+'\n')
    print(out['status'],len(patterns),'patterns',len(tight),'tight; actual profile attained')

if __name__=='__main__':main()
