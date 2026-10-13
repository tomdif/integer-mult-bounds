"""Exact checker of the upstream rational matrix-label bit contract.

Uses Fraction elimination, not the C++ search's small-determinant routine.
No claim about the complex supplier or fully priced outer kappa is inferred.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import json,copy,hashlib,gzip
P=Path(__file__).resolve().parent

def rank(a):
 a=[[Q(x)for x in row]for row in a];r=0
 for c in range(len(a[0])):
  p=next((i for i in range(r,len(a))if a[i][c]),None)
  if p is None:continue
  a[r],a[p]=a[p],a[r];d=a[r][c];a[r]=[x/d for x in a[r]]
  for i in range(r+1,len(a)):
   if a[i][c]:
    q=a[i][c];a[i]=[x-q*y for x,y in zip(a[i],a[r])]
  r+=1
 return r

def check(c,labels,outputs,claimed=None):
 W,m=c['W'],c['m'];rows=[1<<i for i in range(W)]
 assert len(labels)==W+len(c['gates']) and len(outputs)==W
 assert all(len(a)==m and all(len(row)==m for row in a)for a in labels+outputs)
 for t,s in c['gates']:
  assert 0<=t<W and 0<=s<W and t!=s
  rows[t]^=rows[s]
 assert sorted(c['rho'])==list(range(W))
 assert all(rows[c['rho'][w]]==1<<w for w in range(W)),'Not the stated scalar permutation'
 for w in range(W):
  assert all(outputs[c['rho'][w]][i][j]-labels[w][i][j]==int(i==j)for i in range(m)for j in range(m)),'Endpoint contract fails'
 def difference(a,b):return [[b[i][j]-a[i][j]for j in range(m)]for i in range(m)]
 hist=Counter();last=[labels[w]for w in range(W)]
 for k,(t,s)in enumerate(c['gates']):
  for r in [t,s]:hist[rank(difference(last[r],labels[W+k]))]+=1;last[r]=labels[W+k]
 for r in range(W):hist[rank(difference(last[r],outputs[r]))]+=1
 cost=sum(r*n for r,n in hist.items())
 if claimed is not None:assert cost==claimed,'Claimed edge cost differs'
 return dict(cost=cost,budget=W*m,strict_rank_saving=cost<W*m,histogram=dict(sorted(hist.items())))

def outputs(c,labels):
 m=c['m'];out=[None]*c['W']
 for w in range(c['W']):out[c['rho'][w]]=[[labels[w][i][j]+int(i==j)for j in range(m)]for i in range(m)]
 return out

if __name__=='__main__':
 cases=json.loads((P/'CASES.json').read_text());rp=P/'RESULT.txt';raw=(rp.read_text()if rp.exists()else gzip.decompress((P/'RESULT.txt.gz').read_bytes()).decode()).split();it=iter(raw);results=[]
 for i,c in enumerate(cases):
  idx,best,proposals,accepted=[int(next(it))for _ in range(4)];assert idx==i
  mats=[[int(next(it))for _ in range(9)]for _ in range(c['vertices'])]
  labels=[[[a[3*r+s]for s in range(c['m'])]for r in range(c['m'])]for a in mats]
  r=check(c,labels,outputs(c,labels),best);r.update(case=i,W=c['W'],m=c['m'],routing=c['routing'],seed=c['seed'],proposed=proposals,accepted=accepted);results.append(r)
 assert next(it,None)is None
 # Positive control: permit truly non-projector, noncommuting labels.
 c=cases[0];m=2;labels=[[[0,0],[0,0]]for _ in range(c['vertices'])]
 A=[[1,1],[0,1]];B=[[1,0],[1,1]];labels[c['W']]=A;labels[c['W']+1]=B
 mm=lambda a,b:[[sum(a[i][k]*b[k][j]for k in range(m))for j in range(m)]for i in range(m)]
 assert mm(A,A)!=A and mm(B,B)!=B and mm(A,B)!=mm(B,A)
 control=check(c,labels,outputs(c,labels));rejected=[]
 for name in ['bad_endpoint','missing_gate','false_cost']:
  d=copy.deepcopy(c);ll=copy.deepcopy(labels);oo=outputs(d,ll);claim=control['cost']
  if name=='bad_endpoint':oo[0][0][0]+=1
  elif name=='missing_gate':d['gates'].pop(0);ll.pop(d['W'])
  else:claim-=1
  try:check(d,ll,oo,claim)
  except AssertionError:rejected.append(name)
  else:raise AssertionError('Corruption accepted')
 result=dict(status='EXACT_MATRIX_LABEL_SEARCH_SCREEN',scope='Forty prescribed XOR circuits, m=2 or 3, bounded integer matrices and heuristic rank-one moves; not exhaustive and not a new supplier.',cases=len(cases),proposals=sum(r['proposed']for r in results),scheduled=sum(c['steps']*c['restarts']for c in cases),strict_savings=sum(r['strict_rank_saving']for r in results),results=results,nonprojector_noncommuting_control=control,controls_rejected=rejected)
 assert json.loads(json.dumps(result))==json.loads((P/'CHECK.json').read_text()),'Rebuilt matrix-label receipt differs'
 print(result['status'],'cases',len(cases),'strict savings',result['strict_savings'],'proposals',result['proposals'])
