"""Exact scalar verification of the 16-deletion circuit; geometry is rejected."""
import dynamic_elimination as D
from eliminate_register import *
import importlib.util,hashlib
source=ROOT/'research/x54-mixed-allocation/vendor/pr1049/verify.py'
s=importlib.util.spec_from_file_location('unchanged_pr1049_endpoint',source);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
rows=json.loads((W/'dynamic/RESULTS.json').read_text());row=next(r for r in rows if len(r['helpers'])==16 and'compilation'in r)
word=H.load(str(ROOT/'research/x54-mixed-allocation/data/THREE-WORD.json.gz'));steps=[]
for h in sorted(row['helpers'],reverse=True):word,r=D.eliminate_dynamic(word,h);steps.append(r)
assert word['report']['R']==464
receipt=m.endpoint(word)
scalar_source=ROOT/'research/gauge44-slots/independent/audit_local.py'
sp=importlib.util.spec_from_file_location('retained_full_scalar_replay',scalar_source);scalar=importlib.util.module_from_spec(sp);sp.loader.exec_module(scalar)
n=224+word['report']['R'];ident=lambda:[{j:Q(1)}for j in range(n)]
main=word['A']+word['cut']+word['B'];raw_rows=ident()
for event in main:scalar.apply(event,raw_rows)
dirt=[{}for _ in range(n)]
for y in range(112,224):dirt[y]={k:c for k,c in raw_rows[y].items()if k>=224}
for event in word['precondition']:scalar.apply(event,dirt)
compensation=[['add',y,k,-c.numerator,c.denominator,[]]for y in range(112,224)for k,c in sorted(dirt[y].items())]
residual=set(map(int,word['start_extra']))|set(map(int,word['helper_final']))
assert not any(event[2]in residual for event in compensation)
_,_,tail,cleanup=m.parts(word)
program=word['precondition']+compensation+main+tail+cleanup
for dual in [False,True]:
 actual=ident();expected=ident()
 for event in program:scalar.apply(event,actual,dual)
 for t in range(112):expected[t if dual else 112+t][112+t if dual else t]=Q(-1 if dual else 1)
 assert actual==expected,('full exact scalar replay',dual)
(W/'R464-COMPENSATION.json.gz').write_bytes(gzip.compress(json.dumps(compensation,sort_keys=True,separators=(',',':')).encode(),mtime=0))
receipt.update(full_forward_and_dual_columns=n,compensation_gates=len(compensation),full_scalar_source_sha256=hashlib.sha256(scalar_source.read_bytes()).hexdigest())
for name in ['local_profile','local_rank_mass','width_inventory']:word['report'].pop(name,None)
word['report'].update(status='SCALAR_MAP_ONLY_FRAMES_UNASSIGNED',scope='Exact scalar construction only; fails geometric admission and has no recursive price.')
raw=json.dumps(word,sort_keys=True,separators=(',',':')).encode()
(W/'R464-SCALAR-ONLY.json.gz').write_bytes(gzip.compress(raw,mtime=0))
checks=[]
for label,edit in [('drop_add',0),('flip_add',1)]:
 bad=copy.deepcopy(word);i=next(i for i,e in enumerate(bad['B'])if e[0]=='add'and 112<=e[1]<224)
 if edit==0:bad['B'].pop(i)
 else:bad['B'][i][3]*=-1
 try:m.endpoint(bad)
 except m.AuditError as e:checks.append(dict(name=label,reason=str(e)))
 else:raise AssertionError('Scalar corruption accepted')
assert len(checks)==2
try:F.Graph(inline(word,True),check_literal=False,tail_mutable=True,cut_equality=True)
except F.Infeasible as e:failure=str(e)
else:raise AssertionError('Expected geometric rejection was not reproduced')
result=dict(status='EXACT_R464_SCALAR_MAP_ONLY_GEOMETRY_REJECTED',removed_helpers=row['helpers'],R=464,endpoint=receipt,controls=checks,geometric_failure=failure,source_checker_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),word_content_sha256=hashlib.sha256(raw).hexdigest(),steps=steps,scope='No valid frame assignment, native supplier, whole-owner packing or improved kappa is claimed.')
(W/'R464-RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
print(result['status'],receipt,'controls',len(checks),flush=True)
