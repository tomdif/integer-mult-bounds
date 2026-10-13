"""Jointly delete helpers and redesign their entrance/exit frame geometry.

Nominate maximal subspaces of the old entrances that fit the rewritten word.
Also try releasing all helper exit caps to FULL. All actual frame assignments
and local recursive costs are recomputed. Relaxed idle48 pricing is only a
search screen and never a physical packing or an admitted kappa.
"""
import dynamic_elimination as D
import eliminate_register as E
from eliminate_register import *
from reschedule_eliminated import meet_many

def refit(word,full_ends):
    z=copy.deepcopy(word);old=dict(z['start_extra']);z['start_extra']={}
    if full_ends:z['helper_final']={}
    # This first pass reads only propagated interval endpoints, not solutions.
    # Restoring the actual domain enumerator is mandatory before optimization.
    original_domain=F.Graph._domain
    F.Graph._domain=lambda self,k:sorted(set([self.lower[k],self.upper[k]]))
    try:g=F.Graph(inline(z,True),check_literal=False,tail_mutable=True,cut_equality=True)
    finally:F.Graph._domain=original_domain
    changes=[]
    for key,f in old.items():
        r=int(key);chain=g.chains[r];first=chain[1];new=meet_many([tuple(f),g.upper[first]])
        if new:z['start_extra'][key]=list(new)
        if F.basis(tuple(f))!=new:changes.append(dict(helper=r,before=f,after=list(new)))
    caps,comp=cone_caps(z)
    if any(e[2]in set(map(int,z['start_extra']))|set(map(int,z['helper_final']))for e in comp):raise Rejected('residual_compensation')
    g=F.Graph(inline(z,True),check_literal=False,tail_mutable=True,caps=caps,cut_equality=True)
    r=F.optimal_frames(inline(z,True),E.C,check_literal=False,graph=g)
    return write_back(z,g,r['assign']),dict(entrance_changes=changes,all_helper_ends_full=full_ends,optimal_frames_certified=r['certified'])

def trial_interfaces(row):
    hs=row['helpers'];rec=dict(helpers=hs,attempts=[]);t=time.monotonic()
    signal.signal(signal.SIGALRM,H._alarm);signal.alarm(90)
    try:
        w=E.base
        for h in sorted(hs,reverse=True):w,_=D.eliminate_dynamic(w,h)
        oldprofile={int(k):v for k,v in E.base['report']['local_profile'].items()};oldmass=sum(k*v for k,v in oldprofile.items())
        for full in [False,True]:
            try:
                z,detail=refit(w,full);profile={int(k):v for k,v in z['report']['local_profile'].items()};mass=sum(k*v for k,v in profile.items())
                delta=E.C.profile_cost(profile)-E.oldcost;relaxed=48*delta+(oldmass-mass)*E.C.c[48]
                attempt=dict(status='frame_solution',**detail,profile=profile,local_mass=mass,relaxed_cost_delta48=relaxed,width_inventory=z['report']['width_inventory'])
                if relaxed<0:
                    ok,a,ident=audit(z);attempt.update(exact_audit_pass=ok,exact_audit=a,identity=ident)
                    if ok:
                        name='h-'+'-'.join(map(str,hs))+('-full'if full else'-oldends');path=W/'interfaces'/(name+'.json.gz');path.write_bytes(gzip.compress(json.dumps(z,sort_keys=True,separators=(',',':')).encode(),mtime=0));attempt['word']=str(path)
                rec['attempts'].append(attempt)
            except (Rejected,F.Infeasible,ValueError)as e:rec['attempts'].append(dict(all_helper_ends_full=full,status=type(e).__name__,reason=str(e)[:300]))
        rec['status']='completed'
    except H.Timeout:rec['status']='timeout'
    finally:signal.alarm(0)
    rec['seconds']=round(time.monotonic()-t,3);return rec

if __name__=='__main__':
    rows=json.loads((W/'dynamic/RESULTS.json').read_text());rows=[r for r in rows if'compilation'in r]
    rows=sorted(rows,key=lambda r:(-len(r['helpers']),r['helpers']));out=W/'interfaces';out.mkdir(exist_ok=True);results=[]
    print('CASES',len(rows),'variants per case 2',flush=True)
    with mp.get_context('fork').Pool(3,initializer=D.init_dynamic,maxtasksperchild=30)as pool:
        for r in pool.imap_unordered(trial_interfaces,rows,chunksize=1):
            results.append(r)
            if any(a.get('exact_audit_pass')for a in r['attempts']):print('NOMINATION',r,flush=True)
            if len(results)%10==0:print('PROGRESS',len(results),dict(Counter(a['status']for x in results for a in x['attempts'])),flush=True)
            (out/'RESULTS.json').write_text(json.dumps(results,indent=2)+'\n')
    print('DONE',len(results),flush=True)
