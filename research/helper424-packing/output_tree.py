# SPDX-License-Identifier: Apache-2.0
"""Bounded binary-tree synthesis for a declared scalar terminal row.

Every subtree retains one source row. The extracted row is never a source,
so its unit column is preserved. Frame unions and restoration endpoints are
charged at each merge. Floating costs only select a tree; exact word audits
and the full supplier decide acceptance.
"""
from collections import defaultdict
from fractions import Fraction as Q

def terminal_frames(w,pm,aud):
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
 return cur

def synthesize(w,alpha,h,normal,pm,aud):
 assert alpha[h]==1
 cur=terminal_frames(w,pm,aud);regs=sorted(alpha);n=len(regs);hi=regs.index(h);full=pm.basis([1<<i for i in range(9)]);E=pm.basis([x for x in range(1,512)if(normal&x).bit_count()%2==0]);ends={r:pm.basis(w['helper_final'].get(str(r),full))for r in regs};ends[h]=E
 frames={mask:pm.basis([x for i,r in enumerate(regs)if mask>>i&1 for x in cur[r]])for mask in range(1,1<<n)}
 costs=[d**(1-.0017214)for d in range(10)];costs[0]=0;dp={};choices=0
 for size in range(1,n+1):
  for mask,F in frames.items():
   if mask.bit_count()!=size:continue
   for i,r in enumerate(regs):
    if not(mask>>i&1)or(mask>>hi&1 and i!=hi):continue
    if size==1:dp[mask,i]=(0.,[]);continue
    if str(r)in w['helper_final']:continue
    best=None;A=(mask-1)&mask
    while A:
     B=mask^A
     if A>>i&1 and (A,i)in dp:
      ca,ga=dp[A,i];FA=frames[A];FB=frames[B]
      for j,s in enumerate(regs):
       if (B,j)not in dp or not pm.contained(F,ends[s]):continue
       cb,gb=dp[B,j];score=ca+cb+costs[len(F)-len(FA)]+costs[len(F)-len(FB)]+costs[len(ends[s])-len(F)];choices+=1
       if best is None or score<best[0]-1e-12:
        q=alpha[s]/alpha[r];best=(score,ga+gb+[['add',r,s,q.numerator,q.denominator,list(F)]])
     A=(A-1)&mask
    if best is not None:dp[mask,i]=best
 mask=(1<<n)-1;score,gates=dp[mask,hi];assert pm.contained(frames[mask],E);score+=costs[len(E)-len(frames[mask])]
 # Independent scalar row and column checks on the actual synthesized gates.
 rows={r:{r:Q(1)}for r in regs}
 for g in gates:aud.apply(g,rows)
 assert rows[h]==alpha and all(rows[r].get(h,0)==(1 if r==h else 0)for r in regs)
 return gates,dict(subsets=(1<<n)-1,states=len(dp),merge_choices=choices,terminal_frame=list(E),floating_tree_cost=score)
