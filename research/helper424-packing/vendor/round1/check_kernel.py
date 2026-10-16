# SPDX-License-Identifier: Apache-2.0
"""Exact response-rank screen on the 24 helpers of the six staged quartets.

Replays the actual scalar/warp program, not its stored compensation. A warp is
an independent noncommuting symbol; adjacent inverse symbols cancel. All other
coefficients are exact rationals. This screens additional independent entry
cancellation directions in this fixed 24-input response map, not changed
circuits or larger entrance-frame ranks.
"""
import gzip, hashlib, json
from fractions import Fraction as F
from pathlib import Path
from sources import authenticate
HERE=Path(__file__).resolve().parent
SRC=HERE.parent/'shared-kernel-packing'
GROUPS=[[460,461,468,469],[462,463,470,471],[478,479,490,491],[480,481,492,493],[456,457,466,467],[458,459,464,465]]
HELPERS=sorted(sum(GROUPS,[]))
EXPECTED={457,458,460,462,478,480}

def need(x,s):
    if not x:raise ValueError(s)

def replay(w):
    rows=[{}for _ in range(704)]
    for q in HELPERS:rows[q][(q,())]=F(1)
    def step(g):
        if g[0]=='warp':
            r,op=g[1:3]
            rows[r]={(q,tail[1:] if tail and tail[0]==-op else (op,)+tail):c for (q,tail),c in rows[r].items()}
        elif g[0]=='add':
            t,s,num,den=g[1:5];need(t!=s,'self add');c=F(num,den)
            for k,a in list(rows[s].items()):
                b=rows[t].get(k,F(0))+c*a
                if b:rows[t][k]=b
                else:rows[t].pop(k,None)
        elif g[0]=='scale':
            r,num,den=g[1:4];c=F(num,den)
            rows[r]={k:c*a for k,a in rows[r].items()}
        else:raise ValueError('unknown operation')
    for g in w['A']+w['cut']:step(g)
    warps={}
    for op,g in enumerate(w['warps'],1):warps.setdefault(g[0],[]).append(['warp',g[1],op])
    for i in range(len(w['B'])+1):
        for g in warps.get(i,[]):step(g)
        if i<len(w['B']):step(w['B'][i])
    for g in w['restore']:step(g)
    output={}
    for t in range(112,224):
        for (q,op),c in rows[t].items():output.setdefault((t,op),{})[q]=c
    return [[d.get(q,F(0))for q in HELPERS]for _,d in sorted(output.items())]

def rref(M):
    M=[row[:]for row in M];piv=[];k=0
    for j in range(len(HELPERS)):
        i=next((i for i in range(k,len(M))if M[i][j]),None)
        if i is None:continue
        M[k],M[i]=M[i],M[k];z=M[k][j];M[k]=[v/z for v in M[k]]
        for i in range(len(M)):
            if i!=k and M[i][j]:
                z=M[i][j];M[i]=[a-z*b for a,b in zip(M[i],M[k])]
        piv.append(j);k+=1
    free=[j for j in range(len(HELPERS))if j not in piv];null=[]
    for j in free:
        v=[F(0)]*len(HELPERS);v[j]=F(1)
        for i,p in enumerate(piv):v[p]=-M[i][j]
        null.append(v)
    return piv,null

def main():
    authenticate()
    variants={}
    for tag in ['base','extra']:
        p=SRC/f'vendor/pm/words/WORD-PM-{tag}.json.gz';w=json.loads(gzip.decompress(p.read_bytes()))
        M=replay(w);piv,ns=rref(M)
        zeros={q for j,q in enumerate(HELPERS)if all(row[j]==0 for row in M)}
        need(len(piv)==18 and zeros==EXPECTED,'six existing directions exactly exhaust the 24-column kernel')
        need(len(ns)==6 and all(sum(v!=0 for v in col)==1 for col in ns),'coordinate kernel')
        # Perturb a zero response to a new independent formal output: the rank rises.
        bad=[row[:]for row in M]+[[F(int(q==457))for q in HELPERS]]
        need(len(rref(bad)[0])==19,'missing-response control')
        # Removing a pivot input drops the rank by one.
        bad=[row[:]for row in M]
        for row in bad:row[piv[0]]=F(0)
        need(len(rref(bad)[0])==17,'missing-pivot control')
        variants[tag]=dict(word_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),response_rows=len(M),rank=len(piv),nullity=len(ns),zero_columns=sorted(zeros),pivot_columns=[HELPERS[j]for j in piv],controls=['added independent response increases rank','deleted pivot column decreases rank'])
    result=dict(status='PASS_EXACT_SIX_QUARTET_RESPONSE_KERNEL',helpers=HELPERS,variants=variants,
        scope='The frozen PR2894 forward target-response map restricted to these 24 input helpers has rank18 and exactly six independent zero directions, already realized. An invertible change of helper basis alone cannot create a seventh. This does not rule out changed gates, extra carriers, enlarged helper sets, larger entrance frames or cheaper realizations of the existing directions.',
        credit='Jeremy Kothe PR2894, Yiyang Lu PR2857, Philippe Van Velzen PR2853, Dugongue PR2863, and retained word authors. Exact algebra independently implemented with OpenAI Codex assistance; no novelty claim.')
    (HERE/'KERNEL-RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['status'],'rank18/nullity6 in both words')
if __name__=='__main__':main()
