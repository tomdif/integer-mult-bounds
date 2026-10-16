"""Actual PR2250 ordinary-call seam joined to the PR2899 binary engine.

The upper compact simulator still represents layout descriptors by Python
integers. Its written polynomial descriptor charge is retained, not counted
as unit-cost machine arithmetic. Payload transfer below is sequential.
"""
from contextlib import contextmanager
import json
import sys
from unittest.mock import patch

from common import ROOT, module, need, ordinary_sources


class CompactBinary:
    def __init__(self,binary,compact,streams):
        from records import Tape
        from scratch_pool import ScratchPool
        from session import OuterScope
        self.binary,self.compact,self.streams=binary,compact,streams
        self.input=Tape();self.pool=ScratchPool(16);self.scope=OuterScope(self.pool)
        self.calls=[]

    def ordinary(self,source,layout,first,second):
        from cardinal_counts import Count
        from session import borrowed_count
        width=layout.width(first)
        need(width==layout.width(second) and first!=second,"equal distinct compact fields")
        names=layout.names
        left,right=sorted((names.index(first),names.index(second)))
        before=sum(w for _,w in layout.fields[:left])
        between=sum(w for _,w in layout.fields[left+1:right])
        after=sum(w for _,w in layout.fields[right+1:])
        need(len(source.data)==layout.records*layout.record_bits,"complete compact payload")
        source.rewind()
        for _ in range(len(source.data)):
            self.input.append(source.read(1)[0])
        source.finish();self.input.rewind()
        # The numerical values are computed from the upper descriptor, whose
        # arithmetic is explicitly charged in the written construction.
        with self.scope.installed():
            counts=[Count.literal(x) for x in (width,1<<before,1<<between,(1<<after)*layout.record_bits)]
            try:
                with self.scope.suspended():
                    returned=self.binary.run(self.input,*(borrowed_count(c) for c in counts))
                output=self.streams.Tape(source.meter)
                for _ in range(len(source.data)):
                    bit=returned.read();need(bit in (0,1),"complete binary return")
                    returned.step(1);output.write(bytes((bit,)))
                from words import BLANK
                need(returned.read()==BLANK,"exact binary return length")
                returned.clear();self.input.clear()
            finally:
                for count in counts:count.close()
            self.pool.empty()
        bill={'width':width,'volume':len(source.data),
              'prefix':1<<before,'gap':1<<between,'suffix':(1<<after)*layout.record_bits}
        self.calls.append(bill);source.meter.ordinary_calls.append(bill)
        source.erase();output.rewind()
        return output

    @contextmanager
    def installed(self):
        with patch.object(self.compact,'ordinary',self.ordinary):yield self

    def close(self):
        from session import erase_marker
        from words import BLANK
        self.pool.empty();self.input.clear();erase_marker(self.input)
        for tape in self.pool.tapes:erase_marker(tape)
        need(all(all(b==BLANK for b in t.cells) for t in (self.input,*self.pool.tapes)),
             "bridge-owned input and numerical work erased")


def run():
    ordinary_sources()
    from binary import Binary
    from check_engine import fixture_engine,toy_plan
    from encoded import Profile
    from check_support import no_decode
    from physical_words import PhysicalWord
    from words import Word
    directory=ROOT/'research/selected-complex-compact-adapters'
    sys.path.insert(0,str(directory))
    streams=module('streams',directory/'streams.py')
    compact=module('compact',directory/'compact.py')
    native=fixture_engine()
    native.profile=Profile(numerator=173,denominator=100000)
    bridge=CompactBinary(Binary(native),compact,streams)
    cases=[]
    def forbidden(*_args,**_kwargs):raise ValueError('forbidden numerical decoding/construction')
    # Exercise both chronological shuttles at the actual compact call site.
    for late in (False,True):
        fields=(('u',1),('t',1),('x',2),('y',2),('b',1))
        layout=compact.Layout(fields,8)
        raw=bytes(bit for i in range(layout.records) for bit in streams.bit_key(i,8))
        word=compact.Compact(1,1,1,0,'y' if late else 'x','x' if late else 'y',late)
        expected=bytearray(len(raw))
        for i in range(layout.records):
            state=layout.decode(i);state[word.target]^=state[word.source]
            at=layout.encode(state)*8;expected[at:at+8]=raw[i*8:i*8+8]
        start=len(bridge.calls)
        with bridge.installed(),no_decode(),patch.object(Word,'__init__',forbidden),patch.object(PhysicalWord,'inspect',forbidden):
            result=compact.execute(streams.Tape(streams.Meter(),raw),layout,word)
        need(result.data==expected,"complete joined compact shear, unique record per address")
        cases.append(dict(late_source=late,records=layout.records,
                          ordinary_calls=len(bridge.calls)-start,source_restored=True))
    bridge.close()
    # A separate declared reduced fitted body reaches two real C0 roots.
    # This tests the seam beyond B1's elementary branch without pretending
    # that a selected GL64 rectangle was materialized.
    class Fitted:
        q=2
        output=native.output
        @property
        def closed(self):return native.closed
        def run(self,payload,original,prefixes,gap,suffix):
            return native.execute_plan(payload,original,prefixes,gap,suffix,toy_plan)
        def finish(self,fitted):native.finish(fitted)
    fitted=CompactBinary(Binary(Fitted()),compact,streams)
    layout=compact.Layout((('a',5),('b',5)),1)
    raw=bytes(((i*13)^(i>>3)^0x53)&1 for i in range(1024))
    with no_decode(),patch.object(Word,'__init__',forbidden),patch.object(PhysicalWord,'inspect',forbidden):
        result=fitted.ordinary(streams.Tape(streams.Meter(),raw),layout,'a','b')
    need(result.data==bytes(raw[(i%32)*32+i//32] for i in range(1024)),"fitted compact-to-B1-to-C0 endpoint")
    need(native.runtime.completed_roots==2,"two actual completed C0 roots")
    fitted.close()
    return dict(compact_cases=cases,fitted_binary_bits=1024,fitted_C0_roots=2,
                production_profile=native.profile.__dict__,
                scope='Executable compact/B1 boundary with source preservation, sequential transfer and cleanup; reduced fixtures, not the selected large-prime payload.')


if __name__=='__main__':
    print(json.dumps(run(),indent=2));print('PASS_REFIT_COMPACT_BINARY_JOIN')
