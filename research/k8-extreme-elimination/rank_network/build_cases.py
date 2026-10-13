import random,json
from pathlib import Path
P=Path(__file__).resolve().parent
cases=[]
for W in [3,4,6,8,12]:
 for seed in range(2):
  rng=random.Random(20261013+W*101+seed);gates=[];rows=[1<<i for i in range(W)]
  def add(t,s):gates.append([t,s]);rows[t]^=rows[s]
  for _ in range(5*W):t,s=rng.sample(range(W),2);add(t,s)
  # Independently synthesize the inverse through Gaussian row elimination.
  for col in range(W):
   if not(rows[col]>>col&1):
    p=next(i for i in range(col+1,W)if rows[i]>>col&1)
    add(col,p);add(p,col);add(col,p)
   for r in range(W):
    if r!=col and rows[r]>>col&1:add(r,col)
  assert rows==[1<<i for i in range(W)]
  for routing in ['identity','cycle']:
   gg=[g[:]for g in gates];rr=rows[:]
   if routing=='cycle':
    for i in range(W-1):
     for t,s in [(i,i+1),(i+1,i),(i,i+1)]:gg.append([t,s]);rr[t]^=rr[s]
   inv=[r.bit_length()-1 for r in rr];assert len(set(inv))==W and all(r&(r-1)==0 for r in rr)
   rho=[inv.index(i)for i in range(W)];edges=[];last=list(range(W))
   for k,(t,s)in enumerate(gg):
    v=W+k
    for r in [t,s]:edges.append([last[r],v,0]);last[r]=v
   for r in range(W):edges.append([last[r],inv[r],1])
   for m in [2,3]:cases.append(dict(W=W,m=m,seed=seed,routing=routing,gates=gg,rho=rho,edges=edges,vertices=W+len(gg),steps=100000,restarts=3))
(P/'CASES.json').write_text(json.dumps(cases,separators=(',',':'))+'\n')
with(P/'SEARCH.txt').open('w')as f:
 print(len(cases),file=f)
 for c in cases:
  print(c['vertices'],c['m'],len(c['edges']),c['W'],c['steps'],c['restarts'],file=f)
  for e in c['edges']:print(*e,file=f)
print('CASES',len(cases),'scheduled proposals',sum(c['steps']*c['restarts']for c in cases))
