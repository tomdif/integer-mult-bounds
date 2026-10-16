# SPDX-License-Identifier: Apache-2.0
"""Exact word/owner/moment check of a saved four-channel allocation.
Credits the unchanged PR2908/PR2802 owner engine and PR2857 rational bounds.
Native realization and full outer release are separate mandatory checks.
"""
import argparse,copy,gzip,hashlib,importlib.util,json,sys
from pathlib import Path
from fractions import Fraction as Q
P=Path(__file__).resolve().parent
def rd(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def load(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 if not __debug__:raise RuntimeError('Assertions required')
 ap=argparse.ArgumentParser();ap.add_argument('--predecessor',type=Path,required=True);ap.add_argument('--words',type=Path,required=True);ap.add_argument('--allocation',type=Path,required=True);ap.add_argument('--bounds',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=False)
 pred=a.predecessor;assert sha(pred/'MANIFEST.json')=='9dba3fe371602ec023a54e26c0fd66f69eb7a74be86aab89923529083c14b36f';assert {f.relative_to(pred).as_posix():sha(f)for f in pred.rglob('*')if f.is_file()and f!=pred/'MANIFEST.json'}==rd(pred/'MANIFEST.json')
 assert sha(a.bounds)=='0e489823b37303ba383648e3fd21aca1b497abc74c297b5b131a3e4684cf5302'
 aud=load('four_channel_audit',pred/'vendor/audit_local.py');owner=load('independent_owner',pred/'allocation/vendor/independent_owners.py');bounds=load('credited_exact_bounds',a.bounds)
 files=[a.words/f'WORD-{tag}.json.gz'for tag in ['base','extra']]+[a.allocation/name for name in ['FILL.json.gz','ORDER.json','DISPATCH.json']];before={str(f):sha(f)for f in files}
 providers={}
 for tag,pid in [('base','gauge44'),('extra','extra')]:
  path=a.words/f'WORD-{tag}.json.gz';w=rd(path);aud.run(path,a.out/f'AUDIT-{tag}.json');report=rd(a.out/f'AUDIT-{tag}.json');assert report['independent_inputs']==632 and report['zero_buffers']==report['restored_cold']==76
  hs=sorted(set(range(224,704))-set(w['removed']));widths=[len(w['helper_final'].get(str(h),[0]*9))-len(w['start_extra'].get(str(h),[]))for h in hs];assert len(widths)==408
  providers[pid]=dict(widths=widths,actual_paid_profile={int(r):n for r,n in report['local_profile'].items()})
 order=rd(a.allocation/'ORDER.json');fill=rd(a.allocation/'FILL.json.gz');dispatch={(s,r):pid for s,r,pid in rd(a.allocation/'DISPATCH.json')};T=len(order)//9;plan=rd(pred/'allocation/vendor/PLAN.json.gz');template=rd(pred/'allocation/vendor/TEMPLATE.json.gz')
 result,win,last=owner.check(T,order,fill,dispatch,None,plan,template,providers);H={int(r):n for r,n in result['profile'].items()};assert sum(r*n for r,n in H.items())==65088*T
 rejected=[]
 try:owner.check(T,order,{**fill,'rows':fill['rows'][:-1]},dispatch,None,plan,template,providers)
 except ValueError as e:assert str(e)=='complete role count';rejected.append('missing role')
 else:raise AssertionError('accepted missing role')
 bad=dict(H);bad[1]-=1
 try:owner.check(T,order,fill,dispatch,bad,plan,template,providers)
 except ValueError as e:assert str(e)=='complete claimed profile';rejected.append('omitted paid child')
 else:raise AssertionError('accepted omitted child')
 low,high=0.,.01
 for _ in range(60):
  mid=(low+high)/2
  if sum(n*(r/73)**(1-mid)for r,n in H.items())/(896*T)<1:low=mid
  else:high=mid
 lo=Q(str(low))-Q(1,10**13);hi=Q(str(high))+Q(1,10**13);assert bounds.moment(H,lo,896*T)[1]<1<bounds.moment(H,hi,896*T)[0]
 while hi-lo>Q(1,10**25):
  mid=(lo+hi)/2;x=bounds.moment(H,mid,896*T)
  if x[1]<1:lo=mid
  elif x[0]>1:hi=mid
  else:raise AssertionError('insufficient rational precision')
 lower=Q((lo*10**24).__floor__(),10**24);upper=lower+Q(1,10**24);assert bounds.moment(H,lower,896*T)[1]<1<bounds.moment(H,upper,896*T)[0]
 target=lower-Q(1,10**46)-Q(1,10**70);prior=Q(rd(P/'vendor/round1/CLAIM.json')['kappa']);assert target>prior
 assert before=={str(f):sha(f)for f in files}
 result.update(status='PASS_EXACT_FOUR_CHANNEL_OWNERS_AND_MOMENT',physical=896*T+408+8+76+2,private_buffers=76,complex_lower=str(lower),complex_upper=str(upper),kappa=str(target),gain_over_round1=str(target-prior),controls=rejected,inputs_sha256=before,scope='Complete finite words, literal owners and rational complex moment. Full native/supplier/outer admission remains separate.')
 save(a.out/'RESULT.json',result);save(a.out/'PROFILE.json',H);save(a.out/'PROVIDERS.json',providers)
 print(result['status'],str(target),result['physical'],flush=True)
if __name__=='__main__':main()
