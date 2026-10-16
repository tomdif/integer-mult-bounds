"""Current global owner/phase binding, with explicit 73-column charts.

Port charts follow Gareth Davidson's selected1094 chart audit; the rho
involution follows the retained nine-stage construction. Current dimensions,
helper widths, chronology and phase deadlines are checked afresh.
"""
from collections import Counter, defaultdict
from functools import lru_cache
from hashlib import sha256
from native import canonical, need, source


def linear(columns,value):
    out=0
    for i,c in enumerate(columns):
        if value>>i&1:out^=c
    return out


@lru_cache(None)
def port_basis(q):
    missing=next(j for j in range(9) if not (q>>j&1));v=q^(1<<missing)
    order=list(range(73));order[0],order[missing]=order[missing],order[0]
    return tuple((1<<j)^(v if v>>j&1 else 0) for j in order)


@lru_cache(None)
def rho(q,stage):
    if not stage:return tuple(1<<i for i in range(73))
    b=port_basis(q);shift=9+8*(stage-1);out=[]
    for j in range(73):
        x=1<<j;local=x&511;fresh=x>>shift&255
        y=x&~(511|(255<<shift));y|=q if (local&q).bit_count()%2 else 0
        for k in range(8):
            if fresh>>k&1:y^=b[k+1]
            if (local&b[k+1]).bit_count()%2:y^=1<<(shift+k)
        out.append(y)
    return tuple(out)


@lru_cache(None)
def check_chart(columns):
    need(len(columns)==73 and all(0<x<1<<73 for x in columns),'complete chart')
    need(all((a&b).bit_count()%2==int(i==j) for i,a in enumerate(columns)
             for j,b in enumerate(columns)),'orthogonal chart')
    return sha256(canonical(columns)).hexdigest()


def owner_chart(data,call,role):
    family,route=call['owners'][role]
    c=source(data,call['provider_id'],'CANONICAL-WORD.json.gz')
    if role<224:
        port=role%112;need(route==[1,call['stage'],port],'actual data route')
        need(family==896*call['replica']+224*call['pair']+role,'data family')
        return rho(c['ports'][port],call['stage'])
    port=family%112;kind,child,offset,*tail=route
    width=len(c['frames'][c['final'][role]])-len(c['frames'][c['start'][role]])
    pending=data['base/work/complex-nine-native/DATA-PHASES.json']['recipes'][port]['idle_children'][child]['orthogonal_axes']
    need(0<=offset and offset+width<=len(pending),'complete pending slice')
    b=port_basis(c['ports'][port]);active=tuple(pending[offset:offset+width]);positions=[b.index(x) for x in active]
    spectators=[i for i in range(73) if i not in positions][:9-width]
    need(route==([3,child,offset] if width==9 else [4,child,offset,width,spectators]),'actual residual spectators')
    order=positions+spectators+[i for i in range(73) if i not in positions and i not in spectators]
    columns=tuple(b[j] for j in order)
    need(columns[:width]==active,'ordered axes, including their phase convention')
    return columns


def phase_polynomial(terms):
    """Z/4 coefficients of sum c*parity(vector & z), all 2**73 z at once."""
    diagonal=[0]*73;cross=[0]*73
    for coefficient,vector in terms:
        for i in range(73):
            if vector>>i&1:
                diagonal[i]=(diagonal[i]+coefficient)%4
                if coefficient%2:cross[i]^=vector&~((1<<(i+1))-1)
    return tuple(diagonal),tuple(cross)


def phase_audit(data):
    t=data['hosted/GLOBAL-TEMPLATE.json.gz'];ph=data['base/work/complex-nine-native/DATA-PHASES.json']
    idle={}
    for event in t['execution_schedule']:
        if event['kind']=='idle_cover_sweep':
            for child in event['child_indices']:
                levels=(event['from_level'],event['to_level'])
                need(child not in idle or idle[child]==levels,'unambiguous original idle levels');idle[child]=levels
    checks=0;stream=sha256()
    def check(terms,mask):
        nonlocal checks
        want=(tuple(2*((mask>>i)&1) for i in range(73)),(0,)*73)
        actual=phase_polynomial(terms);need(actual==want,'exact all-frequency phase polynomial')
        stream.update(canonical([actual,mask])+b'\n');checks+=1
    for record in ph['recipes']:
        q=record['q']
        def label(level):return [q] if level==-1 else [1<<i for i in range(9+8*level)]
        for stage,alignment in enumerate(record['stage_alignment']):
            columns=rho(q,stage);prefix=[1<<i for i in range(9,9+8*stage)]
            before=[linear(columns,x) for x in [q]+prefix]
            after=[linear(columns,x) for x in [1<<i for i in range(9)]+prefix]
            need(alignment['entry_X']==alignment['entry_Y'] and alignment['exit_X']==alignment['exit_Y'],'both data sides')
            check([(1,x) for x in label(stage-1)]+[(-1,x) for x in before],alignment['entry_X'])
            check([(1,x) for x in label(stage)]+[(-1,x) for x in after],alignment['exit_X'])
        for child,(before,after) in idle.items():
            r=record['idle_children'][child]
            check([(1,x) for x in label(after)]+[(-1,x) for x in label(before)+r['orthogonal_axes']],r['translation_after'])
        need(record['terminal_Y_translation']==q,'terminal C_q squared translation')
    return dict(polynomial_identities=checks,frequencies_per_identity='2^73 (coefficient comparison)',
                phase_identity_sha256=stream.hexdigest(),coordinate_order='translate in physical g coordinates, then pull back by d^-1')


def scalar_shadow(data,omit=None):
    recipe=data['hosted/GLOBAL-TEMPLATE.json.gz']['recipe']
    matrix=[[int(i==j) for j in range(8)] for i in range(8)]
    for index,event in enumerate(recipe):
        if index==omit:continue
        kind=event['kind']
        if kind=='local':
            x,y=2*event['pair'],2*event['pair']+1
            if event['reverse']:matrix[x]=[a-b for a,b in zip(matrix[x],matrix[y])]
            else:matrix[y]=[a+b for a,b in zip(matrix[y],matrix[x])]
        elif kind=='bridge':
            x,y,c=2*event['dst'],2*event['src'],event['coefficient']
            matrix[x]=[a+c*b for a,b in zip(matrix[x],matrix[y])]
            matrix[y+1]=[a-c*b for a,b in zip(matrix[y+1],matrix[x+1])]
        elif kind=='terminal':
            for pair in range(4):
                x,y=2*pair,2*pair+1;matrix[x],matrix[y]=matrix[y],[-a for a in matrix[x]]
        else:raise ValueError('closed global scalar alphabet')
    return matrix


def audit(data,programs):
    t=data['hosted/GLOBAL-TEMPLATE.json.gz'];ph=data['base/work/complex-nine-native/DATA-PHASES.json']
    need((t['m'],t['live'],t['physical'])==(73,66304,66804),'current inventory')
    calls={(c['stage'],c['replica']):c for c in t['calls']}
    need(len(calls)==666,'whole-call domain')
    levels={(rep,pair):-1 for rep in range(74) for pair in range(4)}
    last={};windows={};positions={};kinds=Counter();dispatch=[]
    for index,event in enumerate(t['execution_schedule']):
        kind=event['kind'];kinds[kind]+=1
        if kind=='local_cover_sweep':
            key=event['stage'],event['replica'];c=calls[key];pair=c['pair'];rep=c['replica']
            need(levels[rep,pair]==c['stage']-1,'native input level')
            need(event['provider_id']==c['provider_id'] and event['time']==c['time'],'native source dispatch')
            need(c['local_program_sha256']==sha256(canonical(source(data,c['provider_id'],'LOCAL-PROGRAMS.json.gz')[c['orientation']])).hexdigest(),'native digest')
            need(c['window']==dict(local_axes=list(range(9)),prefix_axes=list(range(9,9+8*c['stage']))),'complete common prefix')
            levels[rep,pair]=c['stage'];last[rep,pair]=index;positions[key]=index
        elif kind=='idle_cover_sweep':
            rep,pair=event['replica'],event['pair'];need(levels[rep,pair]==event['from_level'],'idle input level')
            levels[rep,pair]=event['to_level']
            for side,child in enumerate(event['child_indices']):windows[rep,child]=(last.get((rep,pair),-1),index,pair,side)
        elif kind=='bridge':
            rep=event['replica'];need(levels[rep,event['src']]==levels[rep,event['dst']],'bridge common label')
            last[rep,event['src']]=last[rep,event['dst']]=index
        elif kind in ('terminal','terminal_Y_translations'):
            need(all(levels[event['replica'],pair]==8 for pair in range(4)),'terminal levels')
        else:need(kind in ('bank_padding_cover_sweep','translate_every_live_family'),'global alphabet')
        dispatch.append([index,kind,event])
    used=defaultdict(set);chartstream=sha256();widths=Counter();chartset=set()
    for key,c in calls.items():
        need(len(c['owners'])==632 and len({f for f,_ in c['owners']})==632,'whole-call owner nonaliasing')
        for role,(family,route) in enumerate(c['owners']):
            need(0<=family<66304,'live owner')
            cols=owner_chart(data,c,role);chart=check_chart(cols);chartset.add(chart)
            chartstream.update(canonical([*key,role,family,chart])+b'\n')
            if role<224:continue
            owner_rep,sub=divmod(family,896);pair,sub=divmod(sub,224);side,port=divmod(sub,112)
            typ,child,offset=route[:3];width=9 if typ==3 else route[3]
            before,deadline,w_pair,w_side=windows[owner_rep,child]
            need(before<positions[key]<deadline and (pair,side)==(w_pair,w_side),'untouched whole-call owner window')
            cells=set(range(offset,offset+width));slot=(owner_rep,child,port)
            need(not used[slot]&cells,'no overlapping hosted pieces');used[slot]|=cells;widths[width]+=1
    idle={(z['replica'],z['child'],z['port']):z for z in t['idle_children']};seen=set();zero=0;deadline_count=0;phasehash=sha256();paid=Counter()
    for c in calls.values():paid.update(op[3] for op in programs[c['provider_id'],c['orientation']] if op[1]=='child')
    for event in t['execution_schedule']:
        if event['kind']!='idle_cover_sweep':continue
        for side,child in enumerate(event['child_indices']):
            for port in range(112):
                key=(event['replica'],child,port);old=ph['recipes'][port]['idle_children'][child];taken=used[key]
                need(taken==set(range(len(taken))),'hosted prefix tiling')
                rank=len(old['orthogonal_axes'])-len(taken);family=896*event['replica']+224*event['pair']+112*side+port
                if rank:
                    z=idle[key];seen.add(key);need((z['family'],z['rank'],z['pending_offset'])==(family,rank,len(taken)),'positive idle binding');paid[rank]+=1
                else:
                    need(key not in idle,'no zero-rank recursive call');zero+=bool(old['translation_after'])
                # This directive is retained even when rank is zero.
                phasehash.update(canonical([family,child,rank,len(taken),old['translation_after']])+b'\n');deadline_count+=1
    need(seen==set(idle),'all idle callees');need(zero==20032 and deadline_count==165760,'all zero-rank phase deadlines')
    need(not t['bank_padding']['children'],'empty bank tail')
    need(dict(paid)=={1:1620396,2:428904,3:191980,4:73260,5:24951,6:167,7:45,8:5328,24:1,32:207,48:26958},'current full histogram')
    return dict(global_events=len(dispatch),kinds=dict(sorted(kinds.items())),native_calls=len(calls),
                owner_occurrences=len(calls)*632,helper_widths=dict(sorted(widths.items())),unique_charts=len(chartset),
                chart_stream_sha256=chartstream.hexdigest(),phase_stream_sha256=phasehash.hexdigest(),
                original_idle_deadlines=deadline_count,zero_rank_nonzero_translations=zero,
                paid_profile=dict(sorted(paid.items())),global_dispatch_sha256=sha256(canonical(dispatch)).hexdigest())
