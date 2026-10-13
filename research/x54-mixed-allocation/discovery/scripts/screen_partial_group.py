"""Test proper subsets of a four-helper entrance change, conditional on idle axes."""
import sys,os,json,copy,gzip,itertools
from pathlib import Path
W=Path(__file__).resolve().parent
os.environ['IMB_ROOT']='/Users/thomasdifiore/integer-mult-next-construction'
sys.path.insert(0,str(W/'research/exact-frame-toolkit'))
import frames as F,harness as H
from word import inline
from model import cone_caps
from writeback import write_back,audit
base=H.load(str(W/'x54/demote3.json.gz'));C=F.Costs(H.DEFAULT_B)
old={int(k):v for k,v in base['report']['local_profile'].items()}
out=W/'partial-group';out.mkdir(exist_ok=True);results=[]
for n in (2,3,4):
 for hs in itertools.combinations((627,629,630,631),n):
  w=copy.deepcopy(base)
  for h in hs:w['start_extra'][str(h)]=[68,34,24,1]
  caps,_=cone_caps(w);g=F.Graph(inline(w,True),check_literal=False,tail_mutable=True,caps=caps,cut_equality=True)
  r=F.optimal_frames(inline(w,True),C,check_literal=False,graph=g);z=write_back(w,g,r['assign'])
  profile={int(k):v for k,v in z['report']['local_profile'].items()};d=C.profile_cost(profile)-C.profile_cost(old)-n*C.c[1]
  rec=dict(helpers=hs,certified=r['certified'],delta_with_idle=d,profile=profile)
  if d<0 and r['certified']:
   path=out/('-'.join(map(str,hs))+'.json.gz');path.write_bytes(gzip.compress(json.dumps(z,sort_keys=True,separators=(',',':')).encode(),mtime=0));rec['word']=str(path)
  results.append(rec);print(rec,flush=True)
(out/'RESULTS.json').write_text(json.dumps(results,indent=2)+'\n')
