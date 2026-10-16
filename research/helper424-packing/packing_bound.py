# SPDX-License-Identifier: Apache-2.0
"""Exact fixed-inventory LP certificate, extending the round-one packing check.

Floating arithmetic chooses a basis and nominates a root interval. Rational
balances, every reduced cost and directed elementary-series bounds certify it.
No owner feasibility follows from this relaxation.
"""
import argparse, gzip, hashlib, importlib.util, itertools, json
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
import numpy as np
import sympy as sp
from scipy.optimize import linprog, brentq

P=Path(__file__).resolve().parent
def read(p):
    b=p.read_bytes(); return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def need(c,m):
    if not c: raise ValueError(m)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--predecessor',type=Path,required=True);ap.add_argument('--bounds',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--words',type=Path);a=ap.parse_args()
    need(__debug__,'no Python optimization')
    prior=P/'vendor/round1'
    need(all(sha(prior/n)==h for n,h in read(prior/'MANIFEST.json').items()),'round1 manifest')
    template=read(a.predecessor/'allocation/vendor/TEMPLATE.json.gz')
    capacity={r['child']:r['rank'] for r in template['idle_children']}
    counts=Counter(capacity.values());caps=sorted(counts)
    words=a.words or prior/'data';word=read(words/'WORD-base.json.gz');inventory={int(k):v for k,v in word['report']['width_inventory'].items()};local={int(k):v for k,v in word['report']['local_profile'].items()};widths=sorted(inventory)
    patterns=[]
    for c in caps:
        for ns in itertools.product(*(range(c//w+1)for w in widths)):
            used=sum(w*n for w,n in zip(widths,ns))
            if used<=c:patterns.append((c,ns,c-used))
    A=sp.Matrix([[int(c==k)for c,ns,r in patterns]for k in caps]+[[ns[j]for c,ns,r in patterns]for j in range(len(widths))]);b=sp.Matrix([112*counts[c]for c in caps]+[9*inventory[w]for w in widths])
    alpha=float(read(prior/'CLAIM.json')['kappa_decimal']);cost=np.array([r**(1-alpha)if r else 0 for c,ns,r in patterns]);af=np.array(A).astype(float)
    lp=linprog(cost,A_eq=af,b_eq=np.array(b).astype(float).ravel(),bounds=(0,None),method='highs');need(lp.success,'LP nominee')
    basis=[i for i,x in enumerate(lp.x)if x>1e-7];need(A[:,basis].rank()==len(basis),'independent support')
    reduced=cost-af.T@lp.eqlin.marginals
    for i in np.argsort(abs(reduced)):
        if len(basis)==A.rows:break
        i=int(i)
        if i not in basis and A[:,basis+[i]].rank()>len(basis):basis.append(i)
    B=A[:,basis];x=B.inv()*b;need(all(v>=0 for v in x)and B*x==b,'exact primal')
    ranks=sorted({r for c,ns,r in patterns if r});C=sp.Matrix([[int(patterns[i][2]==r)for r in ranks]for i in basis]);Y=B.T.inv()*C
    idle=Counter()
    for i,n in zip(basis,x):
        if patterns[i][2]:idle[patterns[i][2]]+=Q(n)
    H=Counter({r:Q(9*n)for r,n in local.items()});H.update(idle)
    root=brentq(lambda z:sum(float(n)*(r/73)**(1-z)for r,n in H.items())/896-1,0,.01,xtol=1e-15)
    spec=importlib.util.spec_from_file_location('credited_bounds',a.bounds);bounds=importlib.util.module_from_spec(spec);spec.loader.exec_module(bounds)
    # A wide rational bracket surrounds the floating nominee, then bisect exactly.
    lo=Q(str(root))-Q(1,10**13);hi=Q(str(root))+Q(1,10**13)
    need(bounds.moment(H,lo,896)[1]<1<bounds.moment(H,hi,896)[0],'initial root bracket')
    while hi-lo>Q(1,10**25):
        mid=(lo+hi)/2;v=bounds.moment(H,mid,896)
        if v[1]<1:lo=mid
        elif v[0]>1:hi=mid
        else:raise ValueError('insufficient exact moment precision')
    # Certify a decimal bracket with explicit directed endpoint signs.
    lower=Q((lo*10**24).__floor__(),10**24);upper=lower+Q(1,10**24)
    need(bounds.moment(H,lower,896)[1]<1<bounds.moment(H,upper,896)[0],'24-digit root bracket')
    values={r:(bounds.moment({r:73},lower,1)[0],bounds.moment({r:73},upper,1)[1])for r in ranks}
    tight=[];minimum=None
    for i,(c,ns,r)in enumerate(patterns):
        coeff=sp.Matrix([[int(k==r)for k in ranks]])-A[:,i].T*Y
        if not any(coeff):tight.append(i);continue
        slack=sum(Q(v)*values[k][0 if v>0 else 1]for v,k in zip(coeff,ranks));need(slack>0,f'reduced cost {i}')
        minimum=slack if minimum is None else min(minimum,slack)
    need(all(n==0 or i in tight for i,n in zip(basis,x)),'complementary slackness')
    actual={int(r):Q(n,74)for r,n in read(prior/'allocation/PROFILE.json').items()}
    out=dict(status='PASS_EXACT_FIXED_INVENTORY_PACKING_BOUND',patterns=len(patterns),tight_patterns=len(tight),root_lower=str(lower),root_upper=str(upper),floating_root=root,source_word_sha256=sha(words/'WORD-base.json.gz'),per_call_inventory=inventory,per_call_local_profile=local,per_replica_idle={r:str(n)for r,n in idle.items()},per_replica_full_profile={r:str(n)for r,n in H.items()},actual_profile_attains_optimum=actual==dict(H),primal=[dict(capacity=patterns[i][0],counts=list(patterns[i][1]),idle=patterns[i][2],multiplicity=str(n))for i,n in zip(basis,x)],dual_rank_basis=ranks,dual_coefficients=[[str(z)for z in Y.row(j)]for j in range(Y.rows)],minimum_strict_slack_lower=str(minimum),scope='Fractional nonchronological packing of exactly the supplied word inventory and profile. Feasibility and complete release are separate obligations.')
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({k:out[k]for k in ['status','root_lower','root_upper','floating_root','per_replica_idle','actual_profile_attains_optimum']},indent=2))
if __name__=='__main__':main()
