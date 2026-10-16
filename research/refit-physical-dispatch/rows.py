"""Literal complete-row split/merge on four-symbol sequential tapes.

Only symbol observations and unit head movements occur in the controllers.
The width is a compile-time constant; no transition reads a Python position.
The inherited Tape stores sparse cells for simulation and records trace bounds.
"""
from hashlib import sha256
from native import ROOT, module, need, canonical

m = module('refit_parking_machine',ROOT/'research/recursive-parking-boundary/machine.py')


def rewind(tape):
    steps=1;tape.perform((None,-1))
    while tape.read()!=m.SEP:
        tape.perform((None,-1));steps+=1
    tape.perform((None,1));return steps+1


def make_clock(source,clock,width):
    """Copy the quotient of source length by a fixed width into unary clock.

    The residue 0..width-1 belongs to finite control. Entry source and clock
    are marked streams, clock empty, and source length divisible by width.
    """
    need(width>=2,'fixed positive row divisor');state=0;steps=0
    while True:
        symbol=source.read()
        if symbol==m.BLANK:break
        need(symbol in m.BIT,'complete bit stream')
        source.perform((None,1));state+=1;steps+=1
        if state==width:
            need(clock.read()==m.BLANK,'fresh clock work')
            clock.perform((m.ZERO,1));state=0;steps+=1
    need(state==0,'complete equal packets')
    return steps+rewind(source)+rewind(clock)


def split(source,roles,clock):
    """Move equal contiguous packets to the fixed role tapes, using the clock."""
    steps=0
    for target in roles:  # The finite compiler unrolls this role selection.
        while True:
            tick=clock.read()
            if tick==m.BLANK:break
            need(tick==m.ZERO and source.read() in m.BIT and target.read()==m.BLANK,
                 'split marked interfaces')
            bit=source.read();source.perform((m.BLANK,1));target.perform((bit,1))
            clock.perform((None,1));steps+=1
        steps+=rewind(clock)+rewind(target)
    need(source.read()==m.BLANK,'split consumes the complete stream')
    return steps+rewind(source)


def join(roles,destination):
    """Inverse packet movement; all role heads and destination head restored."""
    steps=0
    for source in roles:
        while True:
            symbol=source.read()
            if symbol==m.BLANK:break
            need(symbol in m.BIT and destination.read()==m.BLANK,'join marked interfaces')
            source.perform((m.BLANK,1));destination.perform((symbol,1));steps+=1
        steps+=rewind(source)
    return steps+rewind(destination)


def erase(tape):
    steps=0
    while tape.read()!=m.BLANK:
        need(tape.read() in m.BIT,'erase complete bit stream')
        tape.perform((m.BLANK,1));steps+=1
    return steps+rewind(tape)


def tables():
    directory=ROOT/'research/machine-transfer-verification/transfer-proof/tapes'
    push=m.parse_instruction_table((directory/'TapeStackPush.lean').read_text(),m.PUSH_MODES,('source',),2)
    pop=m.parse_instruction_table((directory/'TapeStack.lean').read_text(),m.POP_MODES,('park','temp','out'),3)
    need(all(v==m.reference_push(*k) for k,v in push.items()),'source push table')
    need(all(v==m.reference_pop(*k) for k,v in pop.items()),'source pop table')
    return push,pop


def recursive_fixture(width,depth,leaf_bits,ancestor,origin):
    """A real recursive split/call/merge, replacing the old abstract shims.

    The endpoint is bit complement. It tests the row and call controllers;
    numerical C kernels are tested separately and are not claimed here.
    The unary clock is itself an inactive role, hence parked across children.
    """
    push,pop=tables();calls=[];total=[0]
    payload=tuple(m.BIT[(i*i+i//3+7)%2] for i in range(width**depth*leaf_bits))
    work=m.Workspace([m.Tape.marked() for _ in range(width+1)],m.Tape.stack(ancestor,origin),
                     io=m.Tape.marked(payload))
    frame=work.parking.snapshot()
    def run(level):
        if level==0:m.flip_child(work);return
        row_roles=work.roles[:width];clock=work.roles[width]
        total[0]+=make_clock(work.io,clock,width)
        total[0]+=split(work.io,row_roles,clock)
        for active in range(width):
            before=[t.bits() for t in work.roles];entry=work.parking.head
            a=len(work.parking.visits);b=len(work.parking.writes)
            invoice=m.boundary(work,active,lambda _:run(level-1),push,pop)
            need(invoice['total']==m.invoice([len(x) for x in before],active),'actual boundary invoice')
            need(all(t.bits()==before[i] for i,t in enumerate(work.roles) if i!=active),'inactive role and descriptor restoration')
            need(work.roles[active].bits()==tuple(m.ONE if x==m.ZERO else m.ZERO for x in before[active]),'child endpoint')
            need(min(work.parking.visits[a:])>=entry-1 and min(work.parking.writes[b:])>=entry,'local stack trace')
            calls.append([level,active,len(before[active]),invoice['total']]);total[0]+=invoice['total']
        total[0]+=join(row_roles,work.io)+erase(clock)
    run(depth)
    need(work.io.bits()==tuple(m.ONE if x==m.ZERO else m.ZERO for x in payload),'recursive full endpoint')
    need(work.parking.snapshot()==frame and all(t.bits()==() for t in work.roles),'entire recursive frame restored')
    need(work.temporary.bits()==(),'temporary cleared')
    return dict(width=width,depth=depth,leaf_bits=leaf_bits,ancestor_length=len(ancestor),origin=origin,
                boundaries=len(calls),nonchild_actions=total[0],trace=calls,
                parking_trace_sha256=sha256(canonical([[x-origin for x in work.parking.visits],
                                                      [x-origin for x in work.parking.writes]])).hexdigest())
