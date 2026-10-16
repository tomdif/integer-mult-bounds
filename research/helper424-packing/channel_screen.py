# SPDX-License-Identifier: Apache-2.0
"""Exact clean row/column spaces for every terminal binary hyperplane.

This screens the unchanged word and zero-entry input contract only. It does
not rule out changed frames, changed words, or a different extraction contract.
Credits: PR2908 two-sided criterion and inherited free-operator engine.
"""
import argparse,gzip,json,sys,time
from pathlib import Path
from collections import defaultdict
from fractions import Fraction as Q

def nz(d):return {k:v for k,v in d.items()if v}
def add(d,s,c):
    for k,v in s.items():
        z=d.get(k,Q(0))+c*v
        if z:d[k]=z
        else:d.pop(k,None)
def dependencies(rows):
    """Exact left kernel of labelled sparse rows, with an elimination witness."""
    basis={};out=[]
    for r,raw in rows.items():
        v=dict(raw);comb={r:Q(1)}
        while v:
            k=min(v);q=v[k]
            if k not in basis:
                basis[k]=({j:c/q for j,c in v.items()},{j:c/q for j,c in comb.items()});break
            old,oldcomb=basis[k];add(v,old,-q);add(comb,oldcomb,-q)
        if not v:out.append(comb)
    # Verify every returned relation against the original rows.
    for comb in out:
        z={}
        for r,c in comb.items():add(z,rows[r],c)
        assert not z
    assert len(out)+len(basis)==len(rows)
    return out
def restrict(vectors,allowed):
    combs=dependencies({i:{r:c for r,c in v.items()if r not in allowed}for i,v in enumerate(vectors)})
    out=[]
    for comb in combs:
        v={}
        for i,c in comb.items():add(v,vectors[i],c)
        assert set(v)<=allowed;out.append(v)
    return out
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--predecessor',type=Path,required=True);ap.add_argument('--word',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    if not __debug__:raise RuntimeError('Assertions required')
    sys.path.insert(0,str(a.predecessor/'vendor'));import audit_local as aud;import preload_move as pm
    w=json.loads(gzip.decompress(a.word.read_bytes()));live=sorted(set(range(704))-set(w['removed'])-set(range(112,224)))
    protected=set(map(int,w['helper_final']))|set(map(int,w['start_extra']))|{c['source']for c in w['initial_corrections']};H={r for r in live if r>=224 and r not in protected}
    program=[g for g in w['A'][w['prelude_events']:]if g[0]=='warp'or not 112<=g[1]<224];by=defaultdict(list)
    for op,rec in enumerate(w['warps'],1):by[rec[0]].append(['warp',rec[1],op])
    for i in range(len(w['B'])+1):
        program+=by[i]
        if i<len(w['B'])and not 112<=w['B'][i][1]<224:program.append(w['B'][i])
    program+=w['restore']
    M={r:{(r,()):Q(1)}for r in live};N={r:{(r,()):Q(1)}for r in live}
    for g in program:aud.walg_apply(g,M,False,10**6)
    for g in reversed(program):aud.walg_apply(aud.invert_item(g,()),N,False,10**6)
    print('operators',sum(map(len,M.values())),sum(map(len,N.values())),flush=True)
    L=dependencies({r:{key:c for key,c in row.items()if key[0]not in H or key[1]}for r,row in M.items()})
    cols={c:{}for c in live}
    for r,row in N.items():
        for(c,ops),v in row.items():
            if r not in H or ops:cols[c][r,ops]=v
    R=dependencies(cols)
    print('clean spaces',len(L),len(R),flush=True)
    cur=[(p,)for p in w['ports']]+[()]*(704-112)
    for r,E in w['start_extra'].items():cur[int(r)]=pm.basis(E)
    for g in w['A']:
        if g[0]=='warp':cur[g[1]]=pm.basis(g[4])
        else:
            for r in aud.registers(g):cur[r]=pm.basis(g[-1])
    by=defaultdict(list)
    for rec in w['warps']:by[rec[0]].append(rec)
    for i in range(len(w['B'])+1):
        for rec in by[i]:cur[rec[1]]=pm.basis(rec[4])
        if i<len(w['B']):
            for r in aud.registers(w['B'][i]):cur[r]=pm.basis(w['B'][i][-1])
    for g in w['restore']:
        for r in aud.registers(g):cur[r]=pm.basis(g[-1])
    results=[];candidates=[]
    for normal in range(1,512):
        allowed={r for r in live if all((normal&x).bit_count()%2==0 for x in cur[r])}
        left=restrict(L,allowed);right=restrict(R,allowed);pairs=[]
        for i,alpha in enumerate(left):
            for j,y in enumerate(right):
                z=sum(c*y.get(r,0)for r,c in alpha.items())
                if z:pairs.append((i,j,z))
        results.append(dict(normal=normal,allowed=len(allowed),left_dimension=len(left),right_dimension=len(right),nonzero_basis_pairings=len(pairs)))
        for i,j,z in pairs:
            alpha,y=left[i],right[j];helpers=sorted(H&allowed&set(alpha))
            candidate=dict(normal=normal,alpha={r:str(c/z)for r,c in alpha.items()},y={r:str(c)for r,c in y.items()},helpers=helpers)
            candidates.append(candidate)
            print('candidate',candidate,flush=True)
    out=dict(status='PASS_EXACT_TERMINAL_HYPERPLANE_SCREEN',clean_left_dimension=len(L),clean_right_dimension=len(R),hyperplanes=results,candidates=candidates,clean_left=[{r:str(c)for r,c in v.items()}for v in L],clean_right=[{r:str(c)for r,c in v.items()}for v in R],scope='Unchanged supplied word, zero-entry unprotected helper inputs, scalar input and output combinations, and a single terminal hyperplane. No statement about changed frames or words.')
    a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(out['status'],len(candidates),'nonzero basis pairings',flush=True)
if __name__=='__main__':main()
