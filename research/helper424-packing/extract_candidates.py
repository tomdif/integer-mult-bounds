# SPDX-License-Identifier: Apache-2.0
"""Derive newly screened helper400/416 channels after helper408/424.
Extends Jeremy Diviney's PR2908 extraction, using its exact auditor and frame
accounting. No native or supplier admission is inferred from this generator.
"""
import argparse,copy,gzip,json,sys,subprocess
from pathlib import Path
from collections import defaultdict
from fractions import Fraction as Q

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--predecessor',type=Path,required=True);ap.add_argument('--words',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();out=a.out;out.mkdir(parents=True,exist_ok=False)
    sys.path.insert(0,str(a.predecessor/'vendor'));import audit_local as aud;import preload_move as pm
    for tag in ['base','extra']:
        w=json.loads(gzip.decompress((a.words/f'WORD-{tag}.json.gz').read_bytes()))
        for h,normal,alpha in [(400,127,{400:Q(1),412:Q(-2),414:Q(2)}),(416,76,{416:Q(1),428:Q(-2),430:Q(2)}),(547,486,{561:Q(1),547:Q(1),560:Q(1),546:Q(1),559:Q(-1),549:Q(-1),558:Q(-1),548:Q(-1)}),(570,504,{579:Q(-1),568:Q(-1),577:Q(1),570:Q(1),578:Q(-1),569:Q(-1),576:Q(1),571:Q(1)})]:
            parent=copy.deepcopy(w);live=set(range(704))-set(w['removed'])-set(range(112,224))
            program=[g for g in w['A'][w['prelude_events']:]if g[0]=='warp'or not 112<=g[1]<224];by=defaultdict(list)
            for op,rec in enumerate(w['warps'],1):by[rec[0]].append(['warp',rec[1],op])
            for i in range(len(w['B'])+1):
                program+=by[i]
                if i<len(w['B'])and not 112<=w['B'][i][1]<224:program.append(w['B'][i])
            program+=w['restore']
            M={r:{(r,()):Q(1)}for r in live}
            for g in program:aud.walg_apply(g,M,False,10**6)
            u=defaultdict(Q)
            for r,c in alpha.items():
                for key,d in M[r].items():u[key]+=c*d
            u={key:c for key,c in u.items()if c}
            protected=set(map(int,w['helper_final']))|set(map(int,w['start_extra']))|{c['source']for c in w['initial_corrections']};H={r for r in live if r>=224 and r not in protected}
            assert all(r in H and not op for r,op in u);u={r:c for(r,op),c in u.items()}
            V={r:{}for r in live};V[h][('v',())]=Q(1)
            for g in reversed(program):aud.walg_apply(aud.invert_item(g,()),V,False,10**6)
            assert all(r in H and all(not op for var,op in row)for r,row in V.items()if row)
            v={r:row['v',()]for r,row in V.items()if row};assert sum(u.get(r,0)*c for r,c in v.items())==1
            pivot=h if v.get(h) else min(v)
            before=[]
            if pivot!=h:
                before=[['add',h,pivot,1,1,[]],['add',pivot,h,-1,1,[]],['add',h,pivot,1,1,[]],['scale',pivot,-1,1,[]]]
            for r,c in sorted(u.items()):
                if r!=pivot:before.append(['add',pivot,r,(-c).numerator,c.denominator,[]])
            before.append(['scale',pivot,v[pivot].numerator,v[pivot].denominator,[]])
            for r,c in sorted(v.items()):
                if r!=pivot:
                    d=c/v[pivot];before.append(['add',r,pivot,d.numerator,d.denominator,[]])
            E=list(pm.basis([x for x in range(1,512)if(normal&x).bit_count()%2==0]));after=[['add',h,r,c.numerator,c.denominator,E]for r,c in sorted(alpha.items())if r!=h]
            n=w['prelude_events'];w['A']=w['A'][:n]+before+w['A'][n:];w['restore']+=after;w['helper_final'][str(h)]=E
            C=defaultdict(dict)
            for g in w['compensation']:C[g[2]][g[1]]=C[g[2]].get(g[1],Q(0))+Q(g[3],g[4])
            for g in reversed(before):
                if g[0]=='scale':C[g[1]]={t:c*Q(g[2],g[3])for t,c in C[g[1]].items()}
                else:
                    d,sr=g[1:3];c=Q(g[3],g[4])
                    for target,b in C[d].items():C[sr][target]=C[sr].get(target,Q(0))+c*b
            w['compensation']=[['add',t,r,c.numerator,c.denominator,[]]for r,col in sorted(C.items())for t,c in sorted(col.items())if c];assert not any(g[2]==h for g in w['compensation'])
            profile,inventory=pm.frame_report(w);w['report']['local_profile']=profile;w['report']['width_inventory']=inventory
            z=copy.deepcopy(w);z['A']=z['A'][n:];w['cleanup']=pm.derive_cleanup(z,set(map(int,w['helper_final'])))
            transform=dict(helper=h,normal=normal,before=before,after=after,profile=profile,inventory=inventory,u={r:str(c)for r,c in u.items()},v={r:str(c)for r,c in v.items()})
            stage=out/str(h);stage.mkdir(exist_ok=True)
            for name,value in [(f'PARENT-{tag}.json.gz',parent),(f'WORD-{tag}.json.gz',w)]:
                (stage/name).write_bytes(gzip.compress(json.dumps(value,separators=(',',':')).encode(),mtime=0))
            (stage/f'TRANSFORM-{tag}.json').write_text(json.dumps(transform,indent=2)+'\n')
            subprocess.run([sys.executable,'-B',str(a.predecessor/'vendor/audit_local.py'),'--word',str(stage/f'WORD-{tag}.json.gz'),'--output',str(stage/f'AUDIT-{tag}.json')],check=True,stdout=(stage/f'AUDIT-{tag}.log').open('w'),stderr=subprocess.STDOUT)
            print('PASS_LOCAL',tag,h,len(before),profile,inventory,flush=True)
if __name__=='__main__':main()
