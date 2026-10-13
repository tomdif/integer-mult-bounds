#!/usr/bin/env python3
"""Exact comparison inside the two original fixed-factor scheduling classes.

Independent of search.py. Each active row is written once per factor; each
other wire may be added at most once during that row's contiguous write.
Thomas DiFiore / OpenAI Codex, Apache-2.0. No unrestricted optimum is claimed.
"""
import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def target_rows(ops, n):
    rows = [[int(i == j) for j in range(n)] for i in range(n)]
    for d, s in ops:
        rows[d] = [a + b for a, b in zip(rows[d], rows[s])]
    return rows


def solve(rows, target):
    """Return unique F2 row coefficients, or fail if this state is singular."""
    basis = {}
    for i, row in enumerate(rows):
        v = sum((x % 2) << j for j, x in enumerate(row))
        label = 1 << i
        while v:
            p = v.bit_length() - 1
            if p not in basis:
                basis[p] = (v, label)
                break
            w, t = basis[p]
            v ^= w
            label ^= t
        if not v:
            raise ValueError('singular state; this solver does not certify it')
    v = sum((x % 2) << j for j, x in enumerate(target))
    label = 0
    while v:
        p = v.bit_length() - 1
        w, t = basis[p]
        v ^= w
        label ^= t
    return label


def optimize(ops, n):
    target = target_rows(ops, n)
    identity = [[int(i == j) for j in range(n)] for i in range(n)]
    active = [i for i in range(n) if target[i] != identity[i]]
    count = 1 << len(active)
    infinity = 1000000
    costs = [infinity] * count
    paths = [[] for _ in range(count)]
    costs[0] = 0
    edges = 0
    for mask in range(count):
        done = {d for k, d in enumerate(active) if mask >> k & 1}
        rows = [target[i] if i in done else identity[i] for i in range(n)]
        for k, d in enumerate(active):
            if d in done:
                continue
            delta = [a - b for a, b in zip(target[d], identity[d])]
            coeff = solve(rows, delta)
            if coeff >> d & 1:
                continue
            donors = [s for s in range(n) if coeff >> s & 1]
            if [sum(rows[s][j] for s in donors) for j in range(n)] != delta:
                continue
            edges += 1
            nxt = mask | (1 << k)
            value = costs[mask] + len(donors)
            if value < costs[nxt]:
                costs[nxt] = value
                paths[nxt] = paths[mask] + [[d, s] for s in donors]
    if costs[-1] == infinity or target_rows(paths[-1], n) != target:
        raise ValueError('factor class has no certified realization')
    return {'active_rows': active, 'states': count, 'feasible_edges': edges,
            'minimum': costs[-1], 'operations': paths[-1], 'distances': costs}


def run():
    c = json.loads((HERE / 'CANDIDATE.json').read_text())
    old = c['baseline_ops']
    factors = [optimize(old[:17], 12), optimize(old[17:], 12)]
    combined = factors[0]['operations'] + factors[1]['operations']
    if target_rows(combined, 12) != target_rows(old, 12):
        raise ValueError('factor composition changed')
    return {'scope': 'fixed two-factor, destination-once, distinct-donor scheduling only',
            'original_factor_lengths': [17, 24], 'factors': factors,
            'combined_minimum': sum(f['minimum'] for f in factors),
            'broader_search_witness_length': len(c['candidate_ops'])}


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--write-certificate', action='store_true')
    args = p.parse_args()
    result = run()
    path = HERE / 'FACTOR-COMPARISON.json'
    if args.write_certificate:
        path.write_text(json.dumps(result, indent=2) + '\n')
    elif result != json.loads(path.read_text()):
        raise ValueError('fixed-factor comparison changed')
    print('PASS_FACTOR_COMPARISON', [x['minimum'] for x in result['factors']],
          'sum', result['combined_minimum'], 'whole-block witness', result['broader_search_witness_length'])
