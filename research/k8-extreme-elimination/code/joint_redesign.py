"""Combine dynamic helper deletion, global rescheduling, and free helper ends."""
import dynamic_elimination as D
import eliminate_register as E
from eliminate_register import *
from reschedule_eliminated import transform,OrderRejected
from unlock_interfaces import refit

def trial_joint(row):
    hs=row['helpers'];rec=dict(helpers=hs,attempts=[]);t=time.monotonic()
    signal.signal(signal.SIGALRM,H._alarm);signal.alarm(90)
    try:
        w=E.base
        for h in sorted(hs,reverse=True):w,_=D.eliminate_dynamic(w,h)
        cold=copy.deepcopy(w);cold['start_extra']={};cold['helper_final']={}
        oldmass=sum(int(k)*v for k,v in E.base['report']['local_profile'].items())
        for mode in range(4):
            try:
                z,order=transform(cold,mode)
                z['start_extra']=copy.deepcopy(w['start_extra'])
                word,detail=refit(z,True)
                profile={int(k):v for k,v in word['report']['local_profile'].items()};mass=sum(k*v for k,v in profile.items())
                delta=48*(E.C.profile_cost(profile)-E.oldcost)+(oldmass-mass)*E.C.c[48]
                attempt=dict(mode=mode,status='frame_solution',**detail,profile=profile,relaxed_cost_delta48=delta,width_inventory=word['report']['width_inventory'])
                ok,a,ident=audit(word);attempt.update(exact_audit_pass=ok,exact_audit=a,identity=ident)
                if ok:
                    name='h-'+'-'.join(map(str,hs))+f'-{mode}';path=W/'joint'/(name+'.json.gz');path.write_bytes(gzip.compress(json.dumps(word,sort_keys=True,separators=(',',':')).encode(),mtime=0));attempt['word']=str(path)
                rec['attempts'].append(attempt)
            except (OrderRejected,Rejected,F.Infeasible,ValueError)as e:
                rec['attempts'].append(dict(mode=mode,status=type(e).__name__,reason=str(e)[:450]))
                if 'necessary_'in str(e)and"'A'"in str(e):break
        rec['status']='completed'
    except H.Timeout:rec['status']='timeout'
    finally:signal.alarm(0)
    rec['seconds']=round(time.monotonic()-t,3);return rec

if __name__=='__main__':
    rows=json.loads((W/'dynamic/RESULTS.json').read_text());rows=[r for r in rows if'compilation'in r]
    rows=sorted(rows,key=lambda r:(-len(r['helpers']),r['helpers']));out=W/'joint';out.mkdir(exist_ok=True);results=[]
    print('CASES',len(rows),flush=True)
    with mp.get_context('fork').Pool(3,initializer=D.init_dynamic,maxtasksperchild=30)as pool:
        for r in pool.imap_unordered(trial_joint,rows,chunksize=1):
            results.append(r)
            if any(a.get('exact_audit_pass')for a in r['attempts']):print('NOMINATION',r,flush=True)
            if len(results)%10==0:print('PROGRESS',len(results),dict(Counter(a['status']for x in results for a in x['attempts'])),flush=True)
            (out/'RESULTS.json').write_text(json.dumps(results,indent=2)+'\n')
    print('DONE',len(results),flush=True)
