"""Screen joint two-source donations across a common multi-target batch."""
import os,sys,json,gzip,itertools,time
from collections import defaultdict
from pathlib import Path
W=Path(__file__).resolve().parent;os.environ['IMB_ROOT']='/Users/thomasdifiore/integer-mult-next-construction'
sys.path.insert(0,str(W/'research/exact-frame-toolkit'));import harness as C
cs=json.loads((W/'shared-donations/CANDIDATES.json').read_text());groups=defaultdict(list)
for c in cs:groups[(c['holder'],tuple(c['reads']))].append(c)
p=C.Pricer(str(W/'x54/demote3.json.gz'));out=W/'shared-pairs';out.mkdir(exist_ok=True);results=[];t=time.monotonic()
for candidates in groups.values():
    for a,b in itertools.combinations(candidates,2):
        if a['source']==b['source']or set(a['ed']['delete']).intersection(b['ed']['delete']):continue
        ed={key:a['ed'][key]+b['ed'][key]for key in ['delete','insert','tail','prepend']}
        r=p.price(ed,want_word=True,timeout=30);word=r.pop('word',None);r.update(holder=a['holder'],sources=[a['source'],b['source']],reads=a['reads'],ed=ed)
        if r.get('status')=='ok'and r.get('delta',0)<0:
            name=f'candidate-{len(results)}.json.gz';(out/name).write_bytes(gzip.compress(json.dumps(word,sort_keys=True,separators=(',',':')).encode(),mtime=0));r['word']=name
        results.append(r);print('RESULT',len(results),r['status'],r.get('delta'),flush=True)
(out/'RESULTS.json').write_text(json.dumps(results,indent=2)+'\n');print('DONE',len(results),'seconds',time.monotonic()-t,flush=True)
