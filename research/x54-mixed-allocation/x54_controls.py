"""Reject missing or corrupted X54 operations on both final providers."""
import argparse,copy,contextlib,io,tempfile
from pathlib import Path
from common import P,ROOT,read,dump,load

def check(out):
    checker=load(ROOT/'research/gauge44-slots/independent/audit_local.py','x54_control_audit')
    rejected=[]
    with tempfile.TemporaryDirectory(prefix='x54-controls-')as tmp:
        d=Path(tmp)
        def audit(word):
            dump(d/'WORD.json.gz',word)
            with contextlib.redirect_stdout(io.StringIO()):checker.run(d/'WORD.json.gz',d/'AUDIT.json',ROOT)
        def index(word,section,gate):
            found=[i for i,g in enumerate(word[section])if g[:5]==gate]
            assert len(found)==1,(section,gate,found)
            return found[0]
        def drop_cleanup(word,gate):
            i=index(word,'cleanup',gate);word['cleanup'].pop(i)
            word['early_cleanup']=[[j-(j>i),fr]for j,fr in word['early_cleanup']if j!=i]
        for pid,name in [('demote3','THREE-WORD.json.gz'),('demote4','FOUR-WORD.json.gz')]:
            word=read(P/'data'/name);audit(word)
            for control in ['drop_full_restore','drop_early_restore','flip_donation','drop_preread']:
                bad=copy.deepcopy(word)
                if control=='drop_full_restore':drop_cleanup(bad,['add',335,54,-1,1])
                if control=='drop_early_restore':drop_cleanup(bad,['add',367,589,-1,1])
                if control=='flip_donation':bad['B'][index(bad,'B',['add',367,589,1,1])][3]=-1
                if control=='drop_preread':bad['B'].pop(index(bad,'B',['add',219,589,-1,1]))
                try:audit(bad)
                except RuntimeError as error:rejected.append(dict(provider=pid,control=control,reason=str(error)))
                else:raise AssertionError('Accepted X54 mutation: '+pid+' '+control)
    assert len(rejected)==8
    dump(out,dict(status='PASS_X54_BOTH_PROVIDERS_CONTROLS',rejected=rejected))
    return rejected
if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    assert not a.out.exists();print('PASS',len(check(a.out)),'X54 controls')
