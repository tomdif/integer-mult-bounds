"""Positive controls for the reorder bounds and independent ceiling engines."""
import reschedule_eliminated as S
from eliminate_register import *
import importlib.util
import math
from fractions import Fraction as Q

# A valid word must pass the necessary bounds for its literal A and B starts.
w=H.load(str(ROOT/'research/x54-mixed-allocation/data/THREE-WORD.json.gz'));ii=inline(w,True)
starts=[F.basis(tuple(f))for f in ii['_start_frames']];ends=[F.basis(tuple(f))for f in ii['_final_frames']]
cur=list(starts)
for e in w['A']:
 for r in H.regs(e):cur[r]=F.basis(tuple(e[-1]))
pa=S.bounds(w['A'],starts,cur)
assert all(F.leq(F.basis(tuple(e[-1])),pa[3][i])for i,e in enumerate(w['A']))
B=w['B']+[w['cleanup'][i][:-1]+[U]for i,U in w['early_cleanup']]
pb=S.bounds(B,cur,ends)
assert all(F.leq(F.basis(tuple(e[-1])),pb[3][i])for i,e in enumerate(B))

# Two commuting additions: only one order respects the source endpoint cap.
gates=[['add',0,2,1,1,[]],['add',0,1,1,1,[]]]
s=[(),(1,),(2,)];e=[(2,1),(1,),(2,1)];prep=S.bounds(gates,s,e)
out,cur,receipt=S.schedule(gates,s,e,{},0,prep)
assert receipt['order']==[1,0] and receipt['added_frame_precedences']>=1

def load(path,name):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
eng=ROOT/'research/complex-k492-owner-repair/vendor/multicold/engines'
M=load(eng/'moment.py','independent_mercator');N=load(eng/'base_two_moment.py','independent_atanh')
c=json.loads((W/'GEOMETRY-CEILINGS.json').read_text());local={int(r):Q(n)for r,n in c['local'].items()};mass=sum(r*n for r,n in local.items());idle=Q(7232)-mass
receipts=[]
for z in c['results']:
 R=z['idle_cap'];profile={r:9*n for r,n in local.items()};profile[R]=9*idle/R
 scale=math.lcm(*(n.denominator for n in profile.values()))
 integer_profile={r:int(n*scale)for r,n in profile.items()}
 assert all(Q(integer_profile[r],scale)==n for r,n in profile.items())
 lo,hi=map(Q,z['complex_bracket']);bounds=[]
 for label,a in [('lower',lo),('upper',hi)]:
  first=M.moment(integer_profile,73,896*scale,a,False);second=N.moment(73,896*scale,list(integer_profile.items()),a)
  assert (first[1]<1 and second[1]<1)if label=='lower'else(first[0]>1 and second[0]>1)
  bounds.append(dict(endpoint=label,mercator=[str(x-1)for x in first],atanh=[str(x-1)for x in second]))
 receipts.append(dict(cap=R,integer_replica_scale=scale,bounds=bounds))
result=dict(status='PASS_POSITIVE_REORDER_CONTROLS_AND_TWO_INDEPENDENT_CEILING_ENGINES',baseline_A_gates=len(w['A']),baseline_B_tail_gates=len(B),toy_order=receipt,ceilings=receipts)
(W/'CONTROLS.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'])
