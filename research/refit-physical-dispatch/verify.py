"""Read-only exact checks; meaningful mutations remain active under python -O."""
import argparse
from collections import Counter
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import native as n
import charts
import rows


def bindings():
    manifest=json.loads((HERE/'SOURCES.json').read_text());count=0
    for item in manifest['files']:
        if item['usage']=='input':
            n.need(sha256((n.ROOT/item['path']).read_bytes()).hexdigest()==item['sha256'],'changed source '+item['path']);count+=1
    return count


def rejected(action,name):
    try:action()
    except (ValueError,KeyError):return name
    raise ValueError('accepted mutation '+name)


def row_checks():
    m=rows.m;cases=0;stream=sha256()
    for width,max_n in ((2,4),(3,2),(5,1)):
        for length in range(max_n+1):
            for payload in product(m.BIT,repeat=width*length):
                tape=m.Tape.marked(payload);clock=m.Tape.marked();roles=[m.Tape.marked() for _ in range(width)]
                actions=rows.make_clock(tape,clock,width)+rows.split(tape,roles,clock)
                n.need([r.bits() for r in roles]==[payload[i*length:(i+1)*length] for i in range(width)],'complete ordered packets')
                actions+=rows.join(roles,tape)+rows.erase(clock)
                n.need(tape.bits()==payload and clock.bits()==() and all(r.bits()==() for r in roles),'row movement and clearing')
                n.need(actions<=20*len(payload)+20*width,'linear controller-action envelope')
                n.need(all(min(r.visits,default=0)>=-1 for r in [tape,clock]+roles),'local row traces')
                stream.update(n.canonical([width,length,payload,actions]));cases+=1
    nested=[];boundary_count=0
    for width in (2,3,5):
        for depth in range(4):
            for length in (0,1,2):
                a=rows.recursive_fixture(width,depth,length,(),-7)
                b=rows.recursive_fixture(width,depth,length,tuple(m.SYMBOLS[i%4] for i in range(257)),11)
                n.need(a['trace']==b['trace'] and a['nonchild_actions']==b['nonchild_actions'] and
                       a['parking_trace_sha256']==b['parking_trace_sha256'],'trace independent of ancestor bytes and stack offset')
                boundary_count+=a['boundaries']+b['boundaries']
                nested.extend({k:v for k,v in item.items() if k!='trace'} for item in (a,b))
    controls=[]
    controls.append(rejected(lambda:rows.make_clock(m.Tape.marked('010'),m.Tape.marked(),2),'incomplete_row_division'))
    def bad_order():
        tape=m.Tape.marked('001011');clock=m.Tape.marked();roles=[m.Tape.marked() for _ in range(3)]
        rows.make_clock(tape,clock,3);rows.split(tape,roles,clock);rows.join(list(reversed(roles)),tape)
        n.need(tape.bits()==tuple('001011'),'wrong scatter order changes real bits')
    controls.append(rejected(bad_order,'reversed_physical_scatter'))
    return dict(exhaustive_round_trips=cases,round_trip_sha256=stream.hexdigest(),nested_runs=nested,
                nested_boundaries=boundary_count,rejection_controls=controls,
                scope='Literal row/call/return movement; complement leaf, not a numerical complex transform.')


def native_checks(data,programs):
    results={};controls=[];inputs={};outputs={}
    for index,(key,program) in enumerate(programs.items()):
        provider,direction=key;live=n.fixture(index);inputs[key]=live
        out,receipt=n.execute(program,live);expected=n.reference(data,provider,direction,live)
        n.need(out==expected,'whole native endpoint '+str(key));outputs[key]=expected
        n.need(dict(Counter(op[3] for op in program if op[1]=='child'))=={1:2408,2:644,3:280,4:110,5:26,8:8},'actual positive child profile')
        results['/'.join(key)]=receipt|dict(native_events=22353,lowered_primitives=len(program),
            input_sha256=sha256(n.canonical([v.digest() for v in live])).hexdigest(),
            output_sha256=sha256(n.canonical([v.digest() for v in out])).hexdigest(),
            program_sha256=sha256(n.canonical(program)).hexdigest(),
            complete_addresses=512,live_roles=632,endpoint='independent original convolution formula')
    key=('extra','forward');program=programs[key];word=n.source(data,key[0],'LOCAL-PROGRAMS.json.gz')[key[1]]
    def wrong_endpoint(changed,omit=None):
        out,_=n.execute(changed,inputs[key],omit=omit)
        n.need(out==outputs[key],'mutated numerical endpoint')
    first_warp=next(i for i,op in enumerate(program) if word[op[0]][0]=='warp')
    controls.append(rejected(lambda:wrong_endpoint(program,first_warp),'omitted_actual_warp'))
    first_wrapper=next(i for i,op in enumerate(program) if word[op[0]][:2]==['residual_adapter','pre'])
    changed=list(program);op=changed[first_wrapper];changed[first_wrapper]=op[:-1]+(False,)
    controls.append(rejected(lambda:wrong_endpoint(changed),'wrong_residual_inverse'))
    free=next(i for i,op in enumerate(program) if op[1]=='free')
    controls.append(rejected(lambda:wrong_endpoint(program,free),'missing_private_buffer_release'))
    return dict(whole_invocations=results,rejection_controls=controls,
                scope='Exact dense Gaussian dyadics at f=1; not bit-microtransition timing or an all-input proof.')


def phase_controls(data):
    controls=[];identity=[[int(i==j) for j in range(8)] for i in range(8)]
    n.need(charts.scalar_shadow(data)==identity,'whole global scalar identity')
    recipe=data['hosted/GLOBAL-TEMPLATE.json.gz']['recipe']
    for index,event in enumerate(recipe):
        if event['kind']=='bridge':
            n.need(charts.scalar_shadow(data,index)!=identity,'omitted bridge witness');controls.append('omitted_bridge_'+str(index))
    # A translation in a zero-rank slot is not an identity permutation.
    ph=data['base/work/complex-nine-native/DATA-PHASES.json'];mask=ph['recipes'][0]['idle_children'][0]['translation_after']
    n.need(mask!=0 and charts.phase_polynomial([(2,mask)])!=((0,)*73,(0,)*73),'zero-rank translation witness')
    controls.append('omitted_zero_rank_translation')
    # Physical and pulled-back masks differ for an actual stage/port.
    record=next(r for r in ph['recipes'] if any(charts.linear(charts.rho(r['q'],s),a['entry_X'])!=a['entry_X']
                for s,a in enumerate(r['stage_alignment'])))
    controls.append('untransported_common_view_translation')
    return controls


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write-result',type=Path);args=ap.parse_args()
    result=dict(source_files=bindings());data=n.inputs()
    programs={(a,b):n.compile_native(data,a,b) for a in ('extra','gauge44') for b in ('forward','backward')}
    result['native']=native_checks(data,programs)
    result['global']=charts.audit(data,programs)
    result['phases']=charts.phase_audit(data)
    result['global_controls']=phase_controls(data)
    result['rows']=row_checks()
    result['status']='PASS_SCOPED_REFIT_DISPATCH'
    result['scope']='Constructive written dispatcher composition with credited primitive/algebra dependencies; finite component executions. Outer source-transform contract T and full machine formalization are not proved.'
    text=json.dumps(result,sort_keys=True,indent=2)+'\n'
    if args.write_result:
        with args.write_result.open('x') as out:out.write(text)
    else:
        expected=json.loads((HERE/'RESULT.json').read_text());n.need(json.loads(text)==expected,'complete deterministic receipt')
    print(text,end='')


if __name__=='__main__':main()
