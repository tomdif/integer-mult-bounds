#!/usr/bin/env python3
"""Exact call-domain/error seams, not a checker for the complete theorem.

Thomas DiFiore, substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def eye(n):
    return [[F(i == j) for j in range(n)] for i in range(n)]


def mm(a, b):
    return [[sum((x*y for x, y in zip(r, c)), F(0))
             for c in zip(*b)] for r in a]


def mv(a, x):
    return [sum((u*v for u, v in zip(r, x)), F(0)) for r in a]


def scale(a, c):
    return [[x*c for x in row] for row in a]


def norm(x):
    return max(map(abs, x), default=F(0))


def opnorm(a):
    return max(sum(map(abs, row)) for row in a)


def ceil_log2(x):
    need(x >= 1, 'positive logarithmic envelope')
    e = 0
    while 2**e < x:
        e += 1
    return e


def trunc(x, bits):
    # int(Fraction) truncates toward zero, including negative values.
    return F(int(x*2**bits), 2**bits)


def tensor(a, b):
    return [[a[i][j]*b[k][l] for j in range(len(a)) for l in range(len(b))]
            for i in range(len(a)) for k in range(len(b))]


def circuit(g, k, base):
    n = 2**g
    h = [[F(1)]]
    for _ in range(g):
        h = tensor(h, [[F(1), F(1)], [F(1), F(-1)]])
    weights = [F(base)**(k*(g-2*i.bit_count())) for i in range(n)]
    d = [[weights[i] if i == j else F(0) for j in range(n)] for i in range(n)]
    end = [[1/(2**g*weights[i]) if i == j else F(0)
            for j in range(n)] for i in range(n)]
    stages = [('diagonal', d), ('raw_h', h), ('raw_h', h), ('diagonal', end)]
    product = eye(n)
    for _, a in stages:
        product = mm(a, product)
    need(product == eye(n), 'independent exact completed identity')
    # Bound every actual interval independently, including prefixes.
    envelope = F(1)
    intervals = 0
    for start in range(len(stages)):
        product = eye(n)
        for _, a in stages[start:]:
            product = mm(a, product)
            envelope = max(envelope, opnorm(product))
            intervals += 1
    return stages, ceil_log2(envelope), intervals


def execute(stages, x, g, E, Q, adversarial):
    m = len(stages)
    s = E+4
    R = Q+s+2*E+ceil_log2(F(m))+3
    eta = F(1, 2**R)
    actual = [v/2**s for v in x]
    ideal = actual[:]
    max_call = F(0)
    max_error = F(0)
    raw_calls = 0
    for j, (kind, a) in enumerate(stages):
        need(norm(actual) <= F(1, 4), 'actual boundary is in domain')
        exact_step = mv(a, actual)
        if kind == 'raw_h':
            need(norm(actual) <= 1, 'bounded normalized supplier invocation')
            max_call = max(max_call, norm(actual))
            raw_calls += 1
            normalized = mv(scale(a, F(1, 2**g)), actual)
            computed = [trunc(v, R+g+2)*2**g for v in normalized]
        else:
            coefficient_bits = R+ceil_log2(F(len(x)))+2
            rounded = [[trunc(v, coefficient_bits) for v in row] for row in a]
            computed = [trunc(v, R+2) for v in mv(rounded, actual)]
        if adversarial:
            computed = [v+eta*F((-1)**(i+j), 4) for i, v in enumerate(computed)]
        need(norm([u-v for u, v in zip(computed, exact_step)]) <= eta,
             'local coefficient/arithmetic/adversarial error allowance')
        actual = computed
        ideal = mv(a, ideal)
        error = norm([u-v for u, v in zip(actual, ideal)])
        max_error = max(max_error, error)
        need(norm(ideal) <= F(1, 8), 'scaled ideal prefix bound')
        need(error <= (j+1)*2**(2*E)*eta, 'interval error envelope')
    restored = [v*2**s for v in actual]
    need(norm([u-v for u, v in zip(restored, x)]) <= F(1, 2**(Q+3)),
         'error after undoing global scale')
    output = [trunc(v, Q+2) for v in restored]
    need(norm([u-v for u, v in zip(output, x)]) < F(1, 2**Q),
         'requested final error')
    return dict(raw_calls=raw_calls, max_call_input=str(max_call),
                max_scaled_error=str(max_error), E=E, s=s, R=R,
                output=[str(v) for v in output])


def fixtures():
    rows = []
    interval_count = 0
    for g in (1, 2, 3):
        for k in (2, 5, 12):
            for base in (2, 3):
                stages, E, count = circuit(g, k, base)
                interval_count += count
                for seed in range(8):
                    x = [F(((7*i+5*seed)%17)-8, 8) for i in range(2**g)]
                    for adversarial in (False, True):
                        run = execute(stages, x, g, E, 18, adversarial)
                        rows.append(dict(g=g, k=k, base=base, seed=seed,
                                         adversarial=adversarial, **run))
    raw = json.dumps(rows, sort_keys=True).encode()
    return dict(circuits=18, intervals=interval_count, executions=len(rows),
                bounded_raw_h_calls=sum(r['raw_calls'] for r in rows),
                largest_envelope_bits=max(r['E'] for r in rows),
                all_calls_within_quarter_disk=True,
                receipt_sha256=sha256(raw).hexdigest(),
                scope='Exact real subspace fixtures, including rational coefficient rounding; general complex statement is proved in PROOF.md.')


def controls():
    # Completed identity does not bound its first supplied call.
    stages, E, _ = circuit(1, 2, 2)
    x = [F(1, 2), F(0)]
    unsafe = mv(stages[0][1], x)
    need(norm(unsafe) == 2, 'unscaled call-domain counterexample')
    # An omitted scale restoration changes even an exact endpoint.
    need([v/2**(E+4) for v in x] != x, 'missing undo has witness')
    # Merely requesting final accuracy before undoing a scale is insufficient.
    Q, s = 12, 14
    old_local_error = F(1, 2**(Q+2))
    need(2**s*old_local_error > F(1, 2**Q), 'missing undo precision guard')
    # Prefix bounds alone cannot control a local error's future amplification.
    a, b = F(1, 1024), F(1024)
    need(max(F(1), a, a*b) == 1 and b*F(1, 2**Q) > F(1, 2**Q),
         'missing interval bound')
    # General rotations do not commute with truncation.
    rotation = [[F(3, 5), F(-4, 5)], [F(4, 5), F(3, 5)]]
    y = [F(7, 16), F(1, 16)]
    left = [trunc(v, 2) for v in mv(rotation, y)]
    right = mv(rotation, [trunc(v, 2) for v in y])
    need(left != right, 'unitarity is not grid equivariance')
    # Dropping 2^g after each H0 call gives the wrong endpoint.
    wrong = x[:]
    for kind, a in stages:
        wrong = mv(scale(a, F(1, 2)) if kind == 'raw_h' else a, wrong)
    need(wrong != x, 'normalized and raw H distinguished')
    return dict(rejected=['completed_contraction_bounds_calls', 'omit_scale_restore',
                          'omit_accuracy_for_scale_restore', 'prefix_without_interval_bound',
                          'commute_rounding_with_arbitrary_unitary', 'omit_raw_h_scale'],
                unsafe_input=[str(v) for v in unsafe],
                unitary_left=[str(v) for v in left], unitary_right=[str(v) for v in right])


def parameters():
    C = F('0.001722052684227397319529')
    delta = F(1025, 1024*10**104)
    eps, beta = 1-delta, 1-3*delta
    q, a = C-F(2, 10**104), C-F(3, 2*10**104)
    xi = eps*(1+q)-F(3, 32)+F(1, 10**104)
    kappa = C-F(1, 10**46)-F(1, 10**70)
    a1 = F(173, 100000)*(1-F(173, 100000))
    ledger = json.loads((ROOT/'research/paired-terminal-refit/evidence/OUTER-LEDGER.json').read_text())
    source = ledger['rows']['struct_boundary_radix_union']
    for key, value in [('epsilon', eps), ('beta', beta), ('q', q), ('a', a), ('xi', xi), ('kappa', kappa)]:
        need(F(source[key]['rational']) == value, 'source parameter '+key)
    need(a1 > a > q > kappa > 0 and F(1, 2) < xi < eps < 1 and beta < eps,
         'primitive and parameter ordering')
    need(F(ledger['native_moment'][1]['rational']) < 1, 'retained finite strict moment')
    powers = dict(main=1-eps*q, full_route=1-a, dense=eps-q*beta,
                  group_route=eps-a*beta, group_scan_including_wrapper=eps-beta,
                  boundary=eps-xi+F(29, 32), union=eps+F(1, 2)-xi,
                  short_products=1-eps, faces=eps+beta-30)
    margins = {k: 1-kappa-v for k, v in powers.items()}
    guards = dict(compiled_log=1-beta, anchored_gauge=1-(beta+2*xi-2),
                  native_main=1-eps, membership=1-(beta+2*(1-eps)))
    need(all(v > 0 for v in [*margins.values(), *guards.values()]), 'all strict cost/guard margins')
    comparisons = json.loads((ROOT/'research/paired-terminal-refit/COMPARISONS.json').read_text())
    other = next(F(r['kappa']) for r in comparisons if r['baseline'] == 'PR2745')
    need(kappa > other, 'exact improvement over pinned PR2745 value')
    return dict(kappa=str(kappa), powers={k:str(v) for k,v in powers.items()},
                margins={k:str(v) for k,v in margins.items()},
                guard_margins={k:str(v) for k,v in guards.items()},
                sigma=str(min(margins.values())), beats_pinned_pr2745=True)


def authenticate():
    count = 0
    for source in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if source['usage'] == 'input':
            need(sha256((ROOT/source['path']).read_bytes()).hexdigest() == source['sha256'],
                 'source drift: '+source['path'])
            count += 1
    return count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-result', type=Path)
    args = parser.parse_args()
    result = dict(status='PASS_BOUNDED_CALL_COMPLETION_SEAMS', inputs=authenticate(),
                  fixtures=fixtures(), controls=controls(), parameters=parameters(),
                  scope='Finite exact interface/error fixtures and rational exponent arithmetic; not verification of the whole multiplication theorem.')
    raw = json.dumps(result, sort_keys=True, indent=2)+'\n'
    if args.write_result:
        with args.write_result.open('x') as output:
            output.write(raw)
    else:
        need(json.loads(raw) == json.loads((HERE/'RESULT.json').read_text()), 'entire deterministic receipt')
    print(result['status'], result['fixtures']['executions'], 'executions;',
          len(result['controls']['rejected']), 'rejecting controls;', result['inputs'], 'source pins')


if __name__ == '__main__':
    main()
