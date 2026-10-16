"""Reject violations that could otherwise invalidate the recursive argument."""
import copy
from fractions import Fraction as Q
from common import inputs, need
from complex_core import audit, local, height_theorem, scalar_charge
from deferred import phase, schedule


def rejected(fn,name):
    try:fn()
    except (ValueError,KeyError):return name
    raise ValueError('negative control accepted: '+name)


def run():
    data=inputs();out=[];key='base/providers/gauge44/LOCAL-PROGRAMS.json.gz'
    bad=copy.deepcopy(data)
    bad[key]['forward']=[e for e in bad[key]['forward'] if not(e[0]=='zero_buffer' and e[1]=='alloc')]
    out.append(rejected(lambda:local(bad,'gauge44','forward'),'private buffer used before allocation'))
    bad=copy.deepcopy(data)
    events=bad[key]['forward'];j=next(i for i,e in enumerate(events) if e[0]=='zero_buffer' and e[1]=='alloc')
    events.insert(j+1,copy.deepcopy(next(e for e in events if e[0]=='climb')))
    out.append(rejected(lambda:local(bad,'gauge44','forward'),'recursive child observes cleanup buffer'))
    bad=copy.deepcopy(data)
    child=next(e for e in bad[key]['forward'] if e[0]=='climb');child[-1]+=1
    out.append(rejected(lambda:local(bad,'gauge44','forward'),'wrong directed child rank'))
    bad=copy.deepcopy(data)
    event=next(e for e in bad[key]['forward'] if e[0]=='warp');event[2]=100000
    out.append(rejected(lambda:local(bad,'gauge44','forward'),'unbound rank-zero warp'))
    bad=copy.deepcopy(data)
    bad['hosted/GLOBAL-TEMPLATE.json.gz']['execution_schedule'].pop(0)
    out.append(rejected(lambda:audit(bad),'missing chronological dispatch'))
    out.append(rejected(lambda:scalar_charge(['scale',['L',0],1,3]),'nondyadic coefficient'))
    # A tiny final coefficient may nevertheless have a large Horner numerator.
    charge,b,k=scalar_charge(['add',['L',0],['L',1],7,8])
    need((charge,b,k)==(4,3,3),'pre-division Horner scratch is charged')
    out.append('Horner scratch charged despite coefficient below one')
    row=phase(512,512)
    need((row['row_chunks']-1)*row['K']<2644*row['depth'],'one less row chunk cannot hold certified stock')
    out.append('under-reserved complete row field')
    steps=schedule(4096,4096)
    done=[pair for step in steps for pair in step.get('active',step.get('direct',()))]
    need(sum(b-a for a,b in done)==4096 and steps[0]['reserved']>0,'nonempty deferred suffix is completed')
    need(sum(b-a for a,b in steps[0]['active'])<4096,'dropping deferred axes changes endpoint domain')
    out.append('dropped deferred selected axes')
    # C^2=X. An erroneously preprocessed reserved bit and its later phase
    # produce X rather than C, already visible on delta_0.
    Cdelta=(complex(.5,.5),complex(.5,-.5))
    need(Cdelta!=(0,1),'double processing a reserved C bit is not harmless')
    out.append('double processing reserved selected axes')
    return {'controls':out,'count':len(out),'assertions_required':False}
