"""Complete deferred reservoir schedule for the actual 73-dimensional core.

The deferral and support exposure method is credited to the retained PR1673
supplier/support audits. This specializes the stock to the refit and the
self-borrowing B1, and supplies a uniform eleven-chunk row bound.
Only interval descriptors are stored; no list proportional to h is allocated.
"""
from math import prod
from common import need

GAMMA = (1 << 1296) * prod((1 << (2*i))-1 for i in range(1,37))
W = 66304
L = W * GAMMA
ROW_BITS = L.bit_length()


def depth(e):
    d = 0
    while e >= 73:
        e = 48*(e//73)
        d += 1
    return d


def ceildiv(a,b):
    return -(-a//b)


def take(ranges, count):
    """Split an ordered list of disjoint half-open original-axis intervals."""
    front=[];back=[]
    for a,b in ranges:
        size=min(count,b-a)
        if size:front.append((a,a+size))
        if a+size<b:back.append((a+size,b))
        count-=size
    need(count==0,"enough selected axes for a reservation")
    return tuple(front),tuple(back)


def volume(ranges):
    return sum(b-a for a,b in ranges)


def phase(h,p):
    need(type(h) is int and type(p) is int and 0<h<=p and p>=2,
         "positive width within global precision")
    logp=(p-1).bit_length()
    G=4*logp+6;K=128*G
    q0=ceildiv(ROW_BITS*depth(h),K)
    front=ceildiv(2*h*G,K);back=ceildiv(h*G,K)
    reserved=q0+front+back
    need(q0<=11,"uniform actual row reservation")
    if h>=512:
        need(16*reserved<=h,"deferred width contracts by sixteen")
        need(q0*K>=ROW_BITS*depth(h),"complete row stock capacity")
        need(front*K>=2*h*G and back*K>=h*G,"complete compact fields")
    return dict(h=h,G=G,K=K,row_chunks=q0,front_chunks=front,
                back_chunks=back,reserved=reserved,depth=depth(h))


def schedule(h,p):
    pending=((0,h),);out=[]
    while volume(pending)>=512:
        row=phase(volume(pending),p)
        left,rest=take(pending,row['row_chunks']+row['front_chunks'])
        active,right=take(rest,volume(rest)-row['back_chunks'])
        out.append(row|dict(active=active,deferred=left+right))
        pending=left+right
    out.append(dict(h=volume(pending),direct=pending))
    return out


def verify():
    need(ROW_BITS==2644 and 73**2>2*48**2,"actual stock and two-level contraction")
    need(2*ROW_BITS<=11*512,"eleven row chunks for h<=p")
    need(3*512+13*128<=512*8,"reservation at most h/16 from h=512")
    cases=0;max_phases=0;max_ranges=0
    widths=list(range(1,1025))+[2**j+offset for j in range(10,201,10) for offset in (-1,0,1)]
    for h in widths:
        p=max(2,h)
        steps=schedule(h,p)
        done=[]
        for item in steps:
            done.extend(item.get('active',item.get('direct',())))
            max_ranges=max(max_ranges,len(item.get('deferred',())))
        done.sort()
        need(done[0][0]==0 and done[-1][1]==h and
             all(a[1]==b[0] for a,b in zip(done,done[1:])),
             "every original selected bit finishes exactly once")
        need(steps[-1]['h']<512,"bounded direct tail")
        max_phases=max(max_phases,len(steps));cases+=1
    return dict(stock_bits=ROW_BITS,row_chunks_bound=11,tail_below=512,
                contraction='1/16',width_cases=cases,max_phases_tested=max_phases,
                maximum_interval_descriptors=max_ranges,
                row_stock='(66304*|O(73,2)|)^D(h)',
                bit_stock='B1 borrows and restores inside each compact interchange',
                scope='Exact interval controller and integer premises of the written all-width proof; no payload or support-router execution.')
