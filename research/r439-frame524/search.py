#!/usr/bin/env python3
"""Seeded positive integer row-factor search. Thomas DiFiore / OpenAI Codex, Apache-2.0."""
import argparse
import gzip
import json
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = ROOT / 'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz'


def matrix(ops, n):
    rows = [[int(i == j) for j in range(n)] for i in range(n)]
    for a, b in ops:
        rows[a] = [x + y for x, y in zip(rows[a], rows[b])]
    return rows


def search(trials, seed):
    w = json.load(gzip.open(WORD, 'rt'))
    block = w['B'][449:490]
    if any(g[0] != 524 or len(g[2]) != 1 for g in block):
        raise ValueError('unexpected block')
    wires = sorted({r for _, a, ss in block for r in [a, *ss]})
    n = len(wires)
    old = [(wires.index(a), wires.index(ss[0])) for _, a, ss in block]
    target = matrix(old, n)
    reverse = matrix(list(reversed(old)), n)
    identity = [[int(i == j) for j in range(n)] for i in range(n)]
    rng = random.Random(seed)
    best = old
    completed = 0
    histogram = {}
    improvements = []
    # Positive row subtraction traverses a broader class than destination-once
    # scheduling: the same row can be changed repeatedly and used in between.
    for trial in range(trials):
        rows = [r[:] for r in target]
        inverse_ops = []
        greed = (0.0, 0.3, 1.0, 3.0, 10.0)[trial % 5]
        while rows != identity and len(inverse_ops) < 60:
            candidates = []
            for a in range(n):
                for b in range(n):
                    if a != b and all(x >= y for x, y in zip(rows[a], rows[b])):
                        # Always leave a nonzero row (unimodularity implies this).
                        score = rng.random() + greed * sum(rows[b]) / sum(rows[a])
                        candidates.append((score, a, b))
            if not candidates:
                break
            _, a, b = max(candidates)
            rows[a] = [x - y for x, y in zip(rows[a], rows[b])]
            inverse_ops.append((a, b))
        if rows != identity:
            continue
        completed += 1
        ops = list(reversed(inverse_ops))
        histogram[len(ops)] = histogram.get(len(ops), 0) + 1
        rev = matrix(list(reversed(ops)), n)
        dominated = all(a <= b for ra, rb in zip(rev, reverse) for a, b in zip(ra, rb))
        if dominated and len(ops) < len(best):
            best = ops
            improvements.append({'trial': trial, 'gates': len(best)})
            print('improvement', improvements[-1], flush=True)
    return {'schema': 1, 'seed': seed, 'trials': trials, 'completed': completed,
            'completed_length_histogram': dict(sorted(histogram.items())),
            'frame': 524, 'slice': [449, 490], 'wires': wires,
            'baseline_ops': old, 'candidate_ops': best,
            'forward_integer_matrix': target,
            'baseline_reverse_positive_matrix': reverse,
            'candidate_reverse_positive_matrix': matrix(list(reversed(best)), n),
            'improvements': improvements, 'scope': 'sampled positive integer factorizations; no optimality claim'}


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--trials', type=int, default=12000)
    p.add_argument('--seed', type=int, default=13)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    result = search(args.trials, args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print('completed', result['completed'], 'best', len(result['candidate_ops']))
