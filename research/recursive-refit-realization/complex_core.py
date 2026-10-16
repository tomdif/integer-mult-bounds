"""Read the current literal caller, including warps and private zero buffers.

This independently reconstructs the new word's height/child ledger and binds
its complete monomial catalogue to Jose Manuel's compact compiler. It does
not turn a finite check into an all-size physical theorem; see PROOF.md.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import json
import sys

from common import HERE, ROOT, canonical, digest, inputs, module, need
from deferred import GAMMA, W, L

PROFILE={1:1620396,2:428904,3:191980,4:73260,5:24951,
         6:167,7:45,8:5328,24:1,32:207,48:26958}


def scalar_charge(op):
    c=Q(op[-2],op[-1]);b=abs(c.numerator).bit_length();k=c.denominator.bit_length()-1
    need(c.denominator==1<<k and c!=0,"nonzero dyadic scalar")
    # An ADD needs one further magnitude bit. Horner scratch precedes the
    # denominator shift, so max(b,k) is charged, not log2(abs(c)).
    return max(b,k)+(op[0]=='add'),b,k


def local(data,provider,direction):
    prefix='base/providers/'+provider+'/'
    word=data[prefix+'CANONICAL-WORD.json.gz']
    events=data[prefix+'LOCAL-PROGRAMS.json.gz'][direction]
    recipes=data[prefix+'CLIFFORD-RECIPES.json']
    wrappers=data[prefix+'RESIDUAL-ADAPTERS.json']['recipes']
    directed={(r['old'],r['new']):r for r in recipes['children']}
    warps={(r['sign'],r['op'],r['old'],r['new']):r for r in recipes['warps']}
    roles={('L',i) for i in range(632)};centres=set();buffers=set();allocated=set()
    children=Counter();tags=Counter();height=peak=maximum_numerator=maximum_shift=0
    charge_stream=sha256();coefficients=set()
    for index,event in enumerate(events):
        tag=event[0];tags[tag]+=1
        need(not buffers or tag in ('scalar','warp','zero_buffer'),
             "no recursive child observes cleanup buffers")
        if tag in ('climb','center'):
            old,new,rank=event[-3:]
            need((old,new) in directed and directed[old,new]['rank']==rank
                 and 0<rank<=48,"actual directed proper-width child")
            children[rank]+=1
        elif tag=='warp':
            _,role,op,old,new=event
            key=(1 if op>0 else -1,abs(op),old,new)
            need(tuple(role) in roles and key in warps and warps[key]['rank']==0
                 and warps[key]['right'] is None,"actual height-neutral warp")
        elif tag=='zero_buffer':
            _,way,z=event
            need(z in word['zero_buffers'],"declared private buffer")
            if way=='alloc':
                need(z not in allocated,"unique private buffer allocation")
                allocated.add(z);buffers.add(z);roles.add(('Z',z));peak=max(peak,len(buffers))
            else:
                need(way=='free' and z in buffers,"matching private buffer release")
                buffers.remove(z);roles.remove(('Z',z))
        elif tag=='scalar':
            op=event[1];kind=op[0];target=tuple(op[1])
            if target[0]=='C' and target not in roles:
                need(kind in ('clear','copy') and 0<=target[1]<8,
                     "centre initialized before reading")
                roles.add(target);centres.add(target[1])
            need(target in roles,"allocated scalar target")
            if kind in ('copy','add'):
                need(tuple(op[2]) in roles and tuple(op[2])!=target,"distinct live scalar source")
            if kind in ('add','scale'):
                charge,b,k=scalar_charge(op);height+=charge
                maximum_numerator=max(maximum_numerator,b);maximum_shift=max(maximum_shift,k)
                coefficients.add(Q(op[-2],op[-1]))
            else:need(kind in ('copy','clear'),"closed scalar alphabet")
        elif tag=='residual_adapter':
            _,way,role,entrance,*terminal=event
            end=terminal[0] if terminal else 1
            key=f'{entrance}:{end}' if terminal else str(entrance)
            need(way in ('pre','post') and key in wrappers
                 and wrappers[key]['rank']==len(word['frames'][end])-len(word['frames'][entrance]),
                 "actual entrance/terminal wrapper")
        elif tag=='adapter':
            need(event[1] in ('old_to_new','new_to_old'),"endpoint adapter direction")
        else:need(tag=='phase',"complete local event alphabet")
        charge_stream.update(canonical([index,height,sum(r*n for r,n in children.items())])+b'\n')
    need(not buffers and allocated==set(word['zero_buffers']) and len(allocated)==82,
         "all private buffers returned")
    need(centres==set(range(8)),"eight initialized centres")
    need(dict(children)=={1:2408,2:644,3:280,4:110,5:26,8:8},"new paid local profile")
    return dict(events=len(events),tags=dict(sorted(tags.items())),children=dict(sorted(children.items())),
                scalar_height=height,zero_buffer_peak=peak,max_numerator_bits=maximum_numerator,
                max_division_shift=maximum_shift,prefix_sha256=charge_stream.hexdigest(),
                program_sha256=digest(canonical(events))),coefficients


def audit(data):
    template=data['hosted/GLOBAL-TEMPLATE.json.gz']
    invoice=data['audit/PREFIX-AND-INVOICE.json']
    phases=data['base/work/complex-nine-native/DATA-PHASES.json']
    need((template['m'],template['live'],template['physical'])==(73,W,66804),"refit dimensions")
    need(template['cover']=='all matrices d in O(73,2), in lexicographic row order',"complete cover")
    local_rows={};coefficients=set()
    for provider in ('extra','gauge44'):
        prefix='base/providers/'+provider+'/'
        need(template['local_providers'][provider]['local_programs']==data[prefix+'LOCAL-PROGRAMS.json.gz'],
             "embedded and native words agree")
        for direction in ('forward','backward'):
            row,cs=local(data,provider,direction);local_rows[provider+'/'+direction]=row;coefficients|=cs
    calls={(c['stage'],c['replica']):c for c in template['calls']}
    idle={(z['replica'],z['child'],z['port']):z for z in template['idle_children']}
    need(len(calls)==len(template['calls'])==666 and len(idle)==len(template['idle_children']),"unique calls and idle children")
    seen_calls=set();seen_idle=set();deadlines=set();profile=Counter();event_counts=Counter()
    height=local_events=bridge_adds=zero_rank_translations=0;chronology=sha256()
    for position,event in enumerate(template['execution_schedule']):
        kind=event['kind'];event_counts[kind]+=1
        if kind=='local_cover_sweep':
            key=(event['stage'],event['replica']);call=calls[key]
            need(key not in seen_calls and call['time']==event['time']
                 and call['provider_id']==event['provider_id'],"exact chronological native dispatch")
            seen_calls.add(key)
            need(len(call['owners'])==632 and len({z[0] for z in call['owners']})==632,
                 "distinct owner packets within a whole call")
            row=local_rows[call['provider_id']+'/'+call['orientation']]
            need(call['local_program_sha256']==row['program_sha256'],"called program digest")
            profile.update(row['children']);height+=row['scalar_height'];local_events+=row['events']
        elif kind=='idle_cover_sweep':
            for child in event['child_indices']:
                for port in range(112):
                    key=(event['replica'],child,port)
                    need(key not in deadlines,"one original idle deadline")
                    deadlines.add(key)
                    original=phases['recipes'][port]['idle_children'][child]
                    if key in idle:
                        z=idle[key]
                        need(z['rank']>0 and z['rank']+z['pending_offset']==len(original['orthogonal_axes']),
                             "actual idle suffix")
                        profile[z['rank']]+=1;seen_idle.add(key)
                    elif original['translation_after']:
                        zero_rank_translations+=1
        elif kind=='bridge':
            need(event['coefficient'] in (-1,1),"unit signed global bridge")
            bridge_adds+=224;height+=224
        elif kind=='bank_padding_cover_sweep':
            need(not template['bank_padding']['children'],"no uncounted bank padding")
        else:
            need(kind in ('terminal_Y_translations','terminal','translate_every_live_family'),
                 "complete caller alphabet")
        chronology.update(canonical([position,kind,height,sum(r*n for r,n in profile.items())])+b'\n')
    need(seen_calls==set(calls) and seen_idle==set(idle),"complete actual recursive dispatch")
    need(dict(profile)==PROFILE and sum(r*n for r,n in profile.items())==4816512,
         "actual unnormalized refit rank mass")
    need(invoice['selected_local_paid_profile']=={str(k):v for k,v in sorted(
         sum((Counter(local_rows[c['provider_id']+'/'+c['orientation']]['children']) for c in calls.values()),Counter()).items())},
         "fresh ledger agrees with finite invoice")
    return dict(local=local_rows,caller_events=len(template['execution_schedule']),
                caller_event_counts=dict(sorted(event_counts.items())),local_events_per_cover=local_events,
                bridge_adds_per_cover=bridge_adds,original_idle_deadlines=len(deadlines),
                positive_idle_children=len(idle),zero_rank_nonzero_translations=zero_rank_translations,
                child_profile=dict(sorted(profile.items())),children_per_cover=sum(profile.values()),
                unnormalized_rank_mass=4816512,scalar_height_per_cover=height,
                caller_prefix_sha256=chronology.hexdigest()),coefficients


def height_theorem(ledger):
    s=GAMMA*ledger['unnormalized_rank_mass'];E=1<<100000;B=s+E;C0=1<<210000
    charge=GAMMA*ledger['scalar_height_per_cover']+32*73
    need(charge<E,"actual scalar scratch and remainder charge fits E")
    need(8<=2*B and 2*B*(73-48)>=s+E,"all-width unfinished-child induction")
    need(2*B+18<C0,"all deferred phases and final normalization fit root grid")
    return dict(rank_mass=ledger['unnormalized_rank_mass'],full_cover_mass_bits=s.bit_length(),
                scalar_charge_bits=charge.bit_length(),E_exponent=100000,C0_exponent=210000,
                recurrence='A(e) <= A(48 floor(e/73)) + Gamma*4816512*floor(e/73) + E',
                conclusion='A(e)<=2*(Gamma*4816512+E)*e; total deferred-layer guard<C0*h',
                grid='one root grid 2^-(p+ceil(C0*h)), no child or phase rounding',
                space='O(V)+F_q on fixed tapes, by child volume V/(66304*Gamma) and local parking')


def monomials(data):
    directory=ROOT/'research/selected-complex-compact-adapters'
    sys.path.insert(0,str(directory))
    compiler=module('monomial',directory/'monomial.py')
    checker=module('check_monomials',directory/'check_monomials.py')
    old=module('refit_clifford',ROOT/'research/complex-k492-owner-repair/vendor/multicold/vendor/pr558/vendor/pr552/complex-global/vendor531/vendor/clifford/clifford_exact.py')
    unique={}
    for provider in ('extra','gauge44'):
        for filename in ('CLIFFORD-RECIPES.json','RESIDUAL-ADAPTERS.json'):
            for recipe in checker.recipes(data['base/providers/'+provider+'/'+filename]):
                unique[canonical(recipe)]=recipe
    checks=0;maximum=0;digestor=sha256()
    for key,recipe in sorted(unique.items()):
        need(len(recipe['matrix_rows'])==9,"local recipe dimension")
        word=compiler.binary_word(recipe);maximum=max(maximum,len(word))
        for x in range(512):
            mapped=checker.word_address(word,x)
            need(mapped==old.mv(recipe['matrix_rows'],x)^recipe['offset'],"compiled affine endpoint")
            need(checker.word_address(tuple(reversed(word)),mapped)==x,"compiled inverse order")
            need(compiler.column_phase(recipe,x)==old.qvalue(recipe['quadratic_rows'],recipe['linear_Z4'],x,9),
                 "exact source phase convention")
            checks+=1
        digestor.update(key+b'\n')
    # Exercise a newly present, actual rank-zero warp on complete Gaussian records.
    warp=data['base/providers/gauge44/CLIFFORD-RECIPES.json']['warps'][0]
    physical=checker.physical_case(warp['left'],1,1,1,0,old)
    return dict(unique_monomials=len(unique),complete_column_checks=checks,
                maximum_binary_gates=maximum,catalogue_sha256=digestor.hexdigest(),
                actual_warp={k:warp[k] for k in ('op','sign','old','new')},physical_warp=physical)


def run():
    data=inputs();ledger,coefficients=audit(data)
    return dict(ledger=ledger,height=height_theorem(ledger),monomial_binding=monomials(data),
                distinct_scalar_coefficients=len(coefficients))


if __name__=='__main__':
    print(json.dumps(run(),indent=2));print('PASS_REFIT_COMPLEX_RECURSIVE_LEDGER')
