"""Extract a literal frame-contamination path for the R464 compiled trace."""
from eliminate_register import *
from reschedule_eliminated import meet_many,join_many
from collections import deque
input_path=Path(os.environ.get('R464_INPUT',W/'R464-SCALAR-ONLY.json.gz'))
output_path=Path(os.environ.get('OBSTRUCTION_OUT',W/'R464-OBSTRUCTION.json'))
z=H.load(str(input_path));iw=inline(z,True)
starts=[F.basis(tuple(f))for f in iw['_start_frames']];ends=[F.basis(tuple(f))for f in iw['_final_frames']]
requirements={r:[dict(kind='final',cap_register=r,frame=list(ends[r]))]for r in range(len(starts))}
b=z['B']+[z['cleanup'][i]for i,U in z['early_cleanup']]
for i,e in enumerate(b):
 for r in H.regs(e):
  for s in H.regs(e):requirements[r].append(dict(kind='B_or_tail',event=i,cap_register=s,frame=list(ends[s])))
for r,f in zip(z['centers'],z['center_frames']):requirements[r].append(dict(kind='cut',frame=f))
for t in range(112):requirements[112+t].append(dict(kind='cut',frame=z.get('target_levels',{}).get(str(t),[])))
A=z['A'];pred=[];history={};L=[]
for i,e in enumerate(A):
 rr=H.regs(e);p={j for r in rr for j in history.get(r,[])if not F.commute(A[j],e)};pred.append(p)
 L.append(join_many([*(starts[r]for r in rr),*(L[j]for j in p)]))
 for r in rr:history.setdefault(r,[]).append(i)
bad=None
for i,e in enumerate(A):
 for r in H.regs(e):
  for cap in requirements[r]:
   U=tuple(cap['frame'])
   if not F.leq(L[i],U):bad=(i,r,cap);break
  if bad:break
 if bad:break
assert bad
i,r,cap=bad;todo=deque([(i,[i])]);seen={i};found=None
while todo and found is None:
 j,path=todo.popleft()
 for root in H.regs(A[j]):
  for vector in starts[root]:
   if vector not in F.span(tuple(cap['frame'])):found=(root,vector,list(reversed(path)));break
  if found:break
 if found:break
 for k in sorted(pred[j]):
  if k not in seen:seen.add(k);todo.append((k,path+[k]))
assert found
root,vector,path=found
witness=dict(status='FRAME_OBSTRUCTION_FOR_FIXED_COMMUTATION_TRACE',word_content_sha256=__import__('hashlib').sha256(gzip.decompress(input_path.read_bytes())).hexdigest(),initial_register=root,initial_vector=vector,A_gate_path=path,last_register=r,boundary=cap,
 scope='Fixed A/B/cut phases, monotone common ADD/scale frames, these compiled gate multisets, and permutations preserving the original order of each noncommuting gate pair. Alternative algebraic factorizations and different interfaces are outside scope.')
output_path.write_text(json.dumps(witness,indent=2)+'\n')
print('WITNESS',witness,flush=True)
