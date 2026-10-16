"""Construct a fixed-reservoir coordinate-routing plan.

Plans contain paid equal-chunk exchanges and repaired sparse XOR shears.
The verifier runs the ideal endpoints on independent formal bit variables;
this is not a payload execution of the enormous address rectangle.
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from crt_layers import need


def matchings(permutation):
    seen = set()
    first, second = [], []
    for start in range(len(permutation)):
        if start in seen:
            continue
        cycle, i = [], start
        while i not in seen:
            seen.add(i)
            cycle.append(i)
            i = permutation[i]
        m = len(cycle)
        for j in range(m):
            a, b = (-j) % m, (1-j) % m
            if j < a:
                first.append((cycle[j], cycle[a]))
            if j < b:
                second.append((cycle[j], cycle[b]))
    return first, second


def swap_position(pos, left, right, width):
    if left <= pos < left+width:
        return pos+right-left
    if right <= pos < right+width:
        return pos+left-right
    return pos


def plan_prefix(permutation, G, K):
    n = len(permutation)
    need(sorted(permutation) == list(range(n)), 'coordinate permutation')
    need(G >= 1 and K >= 128*G, 'uniform reservoir spacing')
    moved = sum(i != j for i, j in enumerate(permutation))
    if moved == 0:
        return []
    H = min(moved, (n+K-1)//K)*G
    # The asymptotic short branch has only O(log p) bits.
    if 9*H > n or n < 4*H+K:
        return [('swap', a, b, 1) for matching in matchings(permutation) for a,b in matching]
    operations = []
    for matching in matchings(permutation):
        classes = [[], [], []]
        for a, b in matching:
            for c in range(3):
                if all(not 3*c*H <= x < 3*(c+1)*H for x in (a,b)):
                    classes[c].append((a,b))
                    break
            else:
                raise ValueError('an edge must avoid a reservoir')
        for c, edges in enumerate(classes):
            if not edges:
                continue
            placements = ([] if c == 0 else [('swap', 0, 3*c*H, 3*H)])
            placements.append(('swap', 2*H, n-H, H))
            operations.extend(placements)
            def placed(x):
                for _, a,b,w in placements:
                    x = swap_position(x,a,b,w)
                return x
            edges = [(placed(a),placed(b)) for a,b in edges]
            need(all(2*H <= x < n-H for edge in edges for x in edge), 'edges avoid placed controls')
            for reverse in (False, True, False):
                colors = {}
                for a,b in edges:
                    source,target = (b,a) if reverse else (a,b)
                    if target-2*H+K > n-3*H:
                        operations.append(('xor', source, target))
                    else:
                        colors.setdefault((target-2*H) % K, []).append((source,target))
                for color in sorted(colors):
                    pairs = sorted(colors[color], key=lambda pair:pair[1])
                    need(len(pairs)*G <= H, 'active digits fit preselected reservoir')
                    operations.append(('sparse', H, G, K,
                                       tuple(t-2*H for _,t in pairs),
                                       tuple(s-2*H for s,_ in pairs)))
            operations.extend(reversed(placements))
    return operations


def plan(permutation, G, K, suffix_bits):
    n = len(permutation)
    need(0 <= suffix_bits <= n, 'suffix inside address')
    need(sorted(permutation) == list(range(n)), 'coordinate permutation')
    inverse = [0]*n
    for i,j in enumerate(permutation):
        inverse[j] = i
    # Map original source to its current position; settle the final suffix.
    current = list(range(n))
    occupant = list(range(n))
    operations = []
    for target in range(n-suffix_bits,n):
        source = inverse[target]
        old = current[source]
        if old != target:
            operations.append(('swap',old,target,1))
            displaced = occupant[target]
            current[source],current[displaced] = target,old
            occupant[target],occupant[old] = source,displaced
    residual = [0]*(n-suffix_bits)
    for source, position in enumerate(current):
        if position < len(residual):
            residual[position] = permutation[source]
        else:
            need(position == permutation[source], 'settled suffix is fixed')
    operations.extend(('prefix',n-suffix_bits,op) for op in plan_prefix(residual,G,K))
    return operations


def endpoint(labels, operation):
    if operation[0] == 'prefix':
        _,length,op = operation
        prefix = labels[:length]
        endpoint(prefix,op)
        labels[:length] = prefix
    elif operation[0] == 'swap':
        _,a,b,w = operation
        need(a+w <= b or b+w <= a, 'ordinary fields are disjoint')
        labels[a:a+w],labels[b:b+w] = labels[b:b+w],labels[a:a+w]
    elif operation[0] == 'xor':
        _,s,t = operation
        labels[t] ^= labels[s]
    elif operation[0] == 'sparse':
        _,H,G,K,targets,sources = operation
        need(len(targets)*G <= H, 'sparse digit capacity')
        need(all(a+K <= b for a,b in zip(targets,targets[1:])), 'sparse disjoint guards')
        need(not set(targets)&set(sources), 'current source and target separation')
        for s,t in zip(sources,targets):
            labels[2*H+t] ^= labels[2*H+s]
    else:
        raise ValueError('unknown coordinate-router operation')


def verify():
    import random
    from sparse_router import SparseWord, compact
    cases=[]
    rejected=set()
    for n,G,K,suffix in [(17,1,128,4),(1024,1,128,16),(2048,2,256,25),(4096,2,256,25)]:
        for kind in ('cycle','reverse','shuffle','sparse'):
            permutation = list(range(n))
            if kind == 'cycle':
                permutation = permutation[1:]+permutation[:1]
            elif kind == 'reverse':
                permutation.reverse()
            elif kind == 'shuffle':
                random.Random(2745+n).shuffle(permutation)
            else:
                for a,b in [(0,n-1),(n//3,n//2),(n//4,n-2)]:
                    permutation[a],permutation[b] = permutation[b],permutation[a]
            ops = plan(permutation,G,K,suffix)
            labels = [1<<i for i in range(n)]
            for op in ops:
                if op[0]=='prefix' and op[2][0]=='sparse':
                    _,length,(_,H,Gc,Kc,targets,sources)=op
                    SparseWord(targets,sources,Kc,Gc).validate(
                        compact.Layout((('u',H),('t',H),('y',length-3*H),('b',H)),1))
                endpoint(labels,op)
            need(all(labels[permutation[i]] == 1<<i for i in range(n)), 'all-address linear endpoint')
            if n==1024 and kind=='shuffle':
                for name,tag in [('omit_actual_sparse_call','sparse'),('omit_actual_reservoir_exchange','swap')]:
                    index=next(i for i,op in enumerate(ops) if op[0]=='prefix' and op[2][0]==tag)
                    wrong=[1<<i for i in range(n)]
                    for i,op in enumerate(ops):
                        if i!=index:endpoint(wrong,op)
                    need(any(wrong[permutation[i]]!=1<<i for i in range(n)),name+' must fail')
                    rejected.add(name)
            sparse = sum(op[0]=='prefix' and op[2][0]=='sparse' for op in ops)
            cases.append(dict(bits=n,kind=kind,operations=len(ops),sparse_shears=sparse,suffix_bits=suffix))
    need(any(c['sparse_shears'] for c in cases), 'bulk route actually reached')
    # Removing the middle XOR stage from a transposition must fail.
    labels=[1,2]
    endpoint(labels,('xor',0,1));endpoint(labels,('xor',0,1))
    need(labels != [2,1], 'missing-middle-XOR rejection')
    rejected.add('omit_middle_matching_XOR')
    return dict(status='PASS_COORDINATE_ROUTER_PLAN',cases=cases,
                rejecting_controls=sorted(rejected),
                scope='Exact formal-bit endpoint checks of constructed plans; sparse raw/repair payload seam checked separately.')


if __name__ == '__main__':
    import json
    print(json.dumps(verify(),indent=2))
