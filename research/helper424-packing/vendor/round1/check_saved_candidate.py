# SPDX-License-Identifier: Apache-2.0
"""Verify shipped helper408+424 owners and exact moment; no solver is used.
The separate native and complete-release receipts carry the admission scope.
"""
import argparse,gzip,hashlib,importlib.util,json
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
from sources import authenticate
HERE=Path(__file__).resolve().parent

def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def load(name,p):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def main():
 if not __debug__:raise RuntimeError('Assertions must be enabled')
 ap=argparse.ArgumentParser();ap.add_argument('--predecessor',type=Path,required=True);ap.add_argument('--bounds-package',type=Path,default=HERE.parent/'shared-kernel-packing');a=ap.parse_args();q=a.predecessor
 authenticate(a.bounds_package)
 pins=read(HERE/'DATA-PINS.json')
 assert all(hashlib.sha256((HERE/p).read_bytes()).hexdigest()==h for p,h in pins.items())
 upstream_pins=read(q/'MANIFEST.json')
 assert hashlib.sha256((q/'MANIFEST.json').read_bytes()).hexdigest()=='9dba3fe371602ec023a54e26c0fd66f69eb7a74be86aab89923529083c14b36f'
 assert all(hashlib.sha256((q/p).read_bytes()).hexdigest()==h for p,h in upstream_pins.items())
 owner=load('independent_owners',q/'allocation/vendor/independent_owners.py')
 bounds=load('credited_bounds',a.bounds_package/'vendor/pr2857/audit_relaxation.py')
 providers={}
 for tag,pid in [('base','gauge44'),('extra','extra')]:
  w=read(HERE/f'data/WORD-{tag}.json.gz');hs=sorted(set(range(224,704))-set(w['removed']))
  assert len(w['helper_final'])==74 and {'408','424'}<=set(w['helper_final'])
  providers[pid]={'widths':[len(w['helper_final'].get(str(h),[0]*9))-len(w['start_extra'].get(str(h),[]))for h in hs],'actual_paid_profile':{int(r):n for r,n in w['report']['local_profile'].items()}}
 b=HERE/'allocation';order=read(b/'ORDER.json');fill=read(b/'FILL.json.gz');dispatch={(s,r):pid for s,r,pid in read(b/'DISPATCH.json')}
 result,_,_=owner.check(74,order,fill,dispatch,read(b/'PROFILE.json'),read(q/'allocation/vendor/PLAN.json.gz'),read(q/'allocation/vendor/TEMPLATE.json.gz'),providers)
 mom=read(HERE/'MOMENT424.json');H={int(r):n for r,n in result['profile'].items()};lo,hi=Q(mom['lower']),Q(mom['upper'])
 assert H=={int(r):n for r,n in mom['profile'].items()}
 assert bounds.moment(H,lo,66304)[1]<1<bounds.moment(H,hi,66304)[0]
 target=lo-Q(1,10**46)-Q(1,10**70);prior=Q(read(q/'CLAIM.json')['kappa'])
 assert target>prior
 # Removing one helper role and understating the global bill must both fail.
 rejected=[]
 for name,badfill,badprofile in [('missing role',{**fill,'rows':fill['rows'][:-1]},H),('omitted paid child',fill,{**H,1:H[1]-1})]:
  try:owner.check(74,order,badfill,dispatch,badprofile,read(q/'allocation/vendor/PLAN.json.gz'),read(q/'allocation/vendor/TEMPLATE.json.gz'),providers)
  except ValueError:rejected.append(name)
  else:raise ValueError('bad construction accepted')
 print(json.dumps(dict(status='PASS_SAVED_CANDIDATE_OWNERS_AND_EXACT_MOMENT',roles=result['roles'],physical_families=66304+408+8+74+2,target=str(target),gain_over_pr2908=str(target-prior),controls=rejected)))
if __name__=='__main__':main()
