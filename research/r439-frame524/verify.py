"""Exact frame-524 replacement and native-word checks; no new rate claim.

Adapted from mtpsl PR691 by Thomas DiFiore with OpenAI Codex assistance. Apache-2.0.
Python 3.10+, standard library only. No assertions are used for acceptance.
"""
import argparse
from collections import Counter
import copy
import gzip
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
AUDITOR = "research/e8-bit-p111-tuned/code/xcheck_p.py"
EXPORTER = "research/e8-bit-carrier-skeleton/code/bit/export_records.py"


class Reject(Exception):
    pass


def need(condition, reason):
    if not condition:
        raise Reject(reason)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def matrix(ops, positive=False):
    # Each column is evolved separately; search.py evolves whole rows.
    cols = []
    for j in range(12):
        values = [int(i == j) for i in range(12)]
        for d, s in ops:
            need(type(d) is int and type(s) is int and 0 <= d < 12 and
                 0 <= s < 12 and d != s, "invalid circuit gate")
            values[d] = values[d] + values[s] if positive else values[d] ^ values[s]
        cols.append(values)
    return [list(r) for r in zip(*cols)]


def circuit_check(old, new):
    need(matrix(old) == matrix(new), "circuit F2 map changed")
    positive = {}
    for direction, a, b in (("forward", old, new), ("reverse", old[::-1], new[::-1])):
        before, after = matrix(a, True), matrix(b, True)
        need(all(y <= x for rr, ss in zip(before, after) for x, y in zip(rr, ss)),
             direction + " positive matrix increased")
        positive[direction] = {"original": before, "replacement": after}
    return positive


def cleanup(w):
    return [[1, d, list(ss)] for _, d, ss in reversed(w["A"] + w["B"])
            if not 111 <= d < 222]


def build(base, recipe):
    need((recipe["frame"], recipe["slice"]) == (524, [449, 490]), "unexpected circuit location")
    regs = recipe["wires"]
    need(regs == [8, 12, 31, 37, 40, 45, 73, 78, 81, 86, 105, 110], "unexpected registers")
    old = [[524, regs[d], [regs[s]]] for d, s in recipe["baseline_ops"]]
    need(base["B"][449:490] == old, "original gate slice mismatch")
    circuit_check(recipe["baseline_ops"], recipe["candidate_ops"])
    out = copy.deepcopy(base)
    out["B"][449:490] = [[524, regs[d], [regs[s]]] for d, s in recipe["candidate_ops"]]
    out["C"] = cleanup(out)
    return out


def paths(w):
    result = [[f] for f in w["start"]]
    for sec in ("D", "A", "B", "C"):
        for f, d, ss in w[sec]:
            for r in [d] + ss:
                if result[r][-1] != f:
                    result[r].append(f)
    for r, f in enumerate(w["final"]):
        if result[r][-1] != f:
            result[r].append(f)
    return result


def audit(w, module, geometry):
    # Geometry is unchanged; reuse the baseline's already checked exact spaces.
    obj = copy.copy(geometry)
    obj.w = w
    result = obj.full()
    h, c, _ = obj.interface()
    need(all(h.values()) and all(c.values()), "interface H1-H5 or decomposition failed")
    return result


def records_check(directory, word):
    """Independent set-valued interpreter of the actual exported instructions.

    This checks the scalar projection and literal MOVE/COPY/ERASE lifecycle,
    not the multistage formal-column or hosted-recursion contracts.
    """
    raw = (directory / "249-records.bin").read_bytes()
    need(len(raw) % 24 == 0, "truncated record")
    records = list(struct.iter_unpack("<6i", raw))
    dim = {int(k): v["dim"] for k, v in
           json.loads((directory / "frames.json").read_text())["frames"].items()}
    frames = list(word["start"]) + [None]
    values = [{i} for i in range(661)] + [set()]
    pths = [[f] for f in frames[:661]]
    hist, counts = Counter(), Counter()
    for op, a, b, c, d, e in records:
        counts[op] += 1
        if op == 0:
            need(0 <= a < 661 and frames[a] == b and dim[c] - dim[b] == d and d > 0,
                 "bad MOVE")
            need(set(word["frames"][b]) <= set(word["frames"][c]), "MOVE not nested")
            frames[a] = c
            pths[a].append(c)
            hist[d] += 1
        elif op == 1:
            need(0 <= a < 661 and 0 <= b <= 661 and a != b and c == 1
                 and frames[a] == frames[b] == d, "bad ADD frame")
            values[a] = values[a].symmetric_difference(values[b])
        elif op == 2:
            need(b == 661 and not values[b] and frames[b] is None and frames[a] == c,
                 "COPY lifecycle")
            need(d == 0 and e == dim[c], "COPY rank")
            values[b] = set(values[a])
            frames[b] = d
            hist[e] += 1
        elif op == 3:
            need(b == 661 and frames[a] == c and frames[b] == d == 0
                 and values[b] == values[a], "ERASE lifecycle")
            values[b] = set()
            frames[b] = None
        else:
            raise Reject("unknown record opcode")
    expected = [{i} if not 111 <= i < 222 else {i, i - 111} for i in range(661)]
    need(values[:661] == expected and not values[661], "record dirty-column endpoint")
    need(frames[:661] == word["final"] and frames[661] is None, "record frame endpoint")
    need(pths == paths(word), "record frame paths differ")
    return {"records": len(records), "adds": counts[1], "moves": counts[0],
            "copies": counts[2], "erasures": counts[3],
            "paid_histogram": dict(sorted(hist.items())),
            "rank_mass": sum(k * v for k, v in hist.items()),
            "records_sha256": sha(raw)}


def rejected(label, fn, exceptions):
    try:
        fn()
    except exceptions:
        return label
    raise Reject("negative control accepted: " + label)


def prefix_bounds(directory, word):
    records = list(struct.iter_unpack('<6i', (directory / '249-records.bin').read_bytes()))
    n = 2 * word['v'] + word['R']
    maxima = []
    for reverse in (False, True):
        weights = [1] * (n + 1)
        largest = 1
        opened = False
        for op, a, b, c, d, e in (reversed(records) if reverse else records):
            if op == 0:
                continue
            if op == 1:
                weights[a] += abs(c) * weights[b]
                largest = max(largest, weights[a])
            else:
                if reverse:
                    op = 5 - op
                if op == 2:
                    need(not opened, 'prefix COPY already open')
                    weights[b] = weights[a]
                    opened = True
                else:
                    need(opened, 'prefix ERASE without COPY')
                    weights[b] = 0
                    opened = False
        need(not opened, 'prefix copy left open')
        maxima.append(largest)
    f, b = maxima
    payload = 64 * f**3 * b**2
    need(payload < 2**104, 'payload exceeds inherited cap')
    return {'forward': f, 'reverse': b, 'payload_upper': str(payload), 'payload_bits': payload.bit_length()}


def factor_comparison(recipe):
    """Check the fixed-factor lower bounds without importing their DP solver.

    Unit-triangular integer back-substitution replaces its F2 elimination.
    Every legal edge obeys d(next)-d(state) <= edge cost; summing along any
    realization proves the lower bound, attained by the supplied witness.
    """
    cert = json.loads((HERE / 'FACTOR-COMPARISON.json').read_text())
    identity = [[int(i == j) for j in range(12)] for i in range(12)]
    summary = []
    for ops, proof in zip((recipe['baseline_ops'][:17], recipe['baseline_ops'][17:]), cert['factors']):
        target = matrix(ops, True)
        need(all(target[i][i] == 1 for i in range(12)), 'factor diagonal is not unit')
        # Dependency edges row i -> column j. Earlier coefficients are solved
        # before they contribute to later residual coordinates.
        remaining, order = set(range(12)), []
        while remaining:
            available = [j for j in sorted(remaining)
                         if not any(target[i][j] for i in remaining if i != j)]
            need(bool(available), 'factor is not permuted unit triangular')
            j = available[0]
            remaining.remove(j)
            order.append(j)
        active = [i for i in range(12) if target[i] != identity[i]]
        need(active == proof['active_rows'], 'active row receipt')
        count = 1 << len(active)
        dist = proof['distances']
        need(len(dist) == count == proof['states'] and dist[0] == 0, 'distance boundary')
        need(dist[-1] == proof['minimum'] == len(proof['operations']), 'factor witness cost')
        need(matrix(proof['operations'], True) == target, 'factor witness integer map')
        groups = [(d, list(gs)) for d, gs in itertools.groupby(proof['operations'], key=lambda g: g[0])]
        need(len(groups) == len(active) and sorted(d for d, _ in groups) == active,
             'factor witness must write each active destination once')
        need(all(len({g[1] for g in gs}) == len(gs) for _, gs in groups), 'factor witness repeats a donor')
        edges = 0
        for state in range(count):
            done = {d for k, d in enumerate(active) if state >> k & 1}
            rows = [target[i] if i in done else identity[i] for i in range(12)]
            for k, d in enumerate(active):
                if d in done:
                    continue
                residual = [a - b for a, b in zip(target[d], identity[d])]
                coeff = [0] * 12
                for j in order:
                    coeff[j] = residual[j]
                    for col in range(12):
                        residual[col] -= coeff[j] * rows[j][col]
                need(not any(residual), 'integer back-substitution residual')
                if coeff[d] != 0 or any(v < 0 for v in coeff):
                    continue
                # Enumerate the broader positive class, allowing donor
                # repetitions. Every feasible state happens to be 0/1.
                need(all(v <= 1 for v in coeff), 'positive edge requires repeated donor')
                edges += 1
                need(dist[state | (1 << k)] <= dist[state] + sum(coeff), 'factor lower-bound edge')
        need(edges == proof['feasible_edges'], 'factor edge census')
        summary.append({'states': count, 'feasible_edges': edges, 'minimum': proof['minimum'],
                        'nonnegative_edges_require_distinct_donors': True})
    need(len(cert['factors']) == 2 and cert['combined_minimum'] == sum(p['minimum'] for p in summary),
         'factor total')
    need(cert['combined_minimum'] == 27 and len(recipe['candidate_ops']) == 26, 'class gap')
    return summary


def run(output, write_certificate):
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    for path, digest in pins['execution_inputs'].items():
        need(sha((ROOT / path).read_bytes()) == digest, 'source hash mismatch: ' + path)
    base = json.loads(gzip.decompress((ROOT / WORD).read_bytes()))
    recipe = json.loads((HERE / 'CANDIDATE.json').read_text())
    original, replacement = recipe['baseline_ops'], recipe['candidate_ops']
    need(len(original) == 41 and len(replacement) == 26, 'frozen gate count')
    fixed_factors = factor_comparison(recipe)
    revised = build(base, recipe)
    positive = circuit_check(original, replacement)
    need(positive['forward']['original'] == positive['forward']['replacement'], 'forward integer map changed')
    need(matrix(replacement, True) == recipe['forward_integer_matrix'], 'candidate matrix receipt')
    need(matrix(original[::-1], True) == recipe['baseline_reverse_positive_matrix'], 'baseline reverse receipt')
    need(matrix(replacement[::-1], True) == recipe['candidate_reverse_positive_matrix'], 'candidate reverse receipt')
    need(paths(base) == paths(revised), 'physical frame path changed')
    spec = importlib.util.spec_from_file_location('predecessor_xcheck', ROOT / AUDITOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    geometry, labels, baseline, h, c, _ = module.check(base)
    need(all(h.values()) and all(c.values()), 'baseline interface failed')
    revised_audit = audit(revised, module, geometry)
    # Search evolves integer rows. This verifier evolves columns and then
    # separately tests every Boolean input with a packed scalar interpreter.
    for bits in range(4096):
        endings = []
        for gates in (original, replacement):
            value = bits
            for d, s in gates:
                value ^= ((value >> s) & 1) << d
            endings.append(value)
        need(endings[0] == endings[1], 'exhaustive twelve-bit map differs')
    evidence = {}
    for name, word in (('baseline', base), ('replacement', revised)):
        path = output / (name + '.json.gz')
        path.write_bytes(gzip.compress(canonical(word), mtime=0))
        directory = output / name / 'records'
        subprocess.run([sys.executable, '-I', '-B', str(ROOT / EXPORTER), str(path), str(directory)],
                       check=True, capture_output=True, text=True)
        evidence[name] = records_check(directory, word)
        evidence[name]['prefix'] = prefix_bounds(directory, word)
    a, b = evidence['baseline'], evidence['replacement']
    need(a['adds'] == 24305 and b['adds'] == 24275, 'native ADD count')
    for key in ('moves', 'copies', 'erasures', 'paid_histogram', 'rank_mass'):
        need(a[key] == b[key], 'native cost changed: ' + key)
    need(b['rank_mass'] == 5129 and b['copies'] == 9, 'native cost')
    need(a['prefix']['forward'] == 49347 and a['prefix']['reverse'] == 1113070, 'baseline prefix')
    need(b['prefix']['forward'] <= a['prefix']['forward'] and b['prefix']['reverse'] <= a['prefix']['reverse'],
         'complete prefix increased')
    controls = []
    fail = (Reject, module.Reject)
    controls.append(rejected('drop circuit gate', lambda: circuit_check(original, replacement[1:]), fail))
    wrong = copy.deepcopy(replacement)
    wrong[0].reverse()
    controls.append(rejected('reverse circuit operand', lambda: circuit_check(original, wrong), fail))
    inflated = replacement + [[0, 1], [0, 1]]
    need(matrix(inflated) == matrix(replacement), 'inflation must be F2-neutral')
    controls.append(rejected('F2-neutral integer inflation', lambda: circuit_check(original, inflated), fail))
    bad = copy.deepcopy(revised)
    bad['C'].pop()
    controls.append(rejected('dropped cleanup', lambda: audit(bad, module, geometry), fail))
    bad = copy.deepcopy(revised)
    bad['C'] = copy.deepcopy(base['C'])
    obj = copy.copy(geometry)
    obj.w = bad
    obj.full()  # Positive endpoint control; H4 must still reject stale cleanup.
    controls.append(rejected('nonliteral original cleanup', lambda: audit(bad, module, geometry), fail))
    bad = copy.deepcopy(revised)
    bad['B'][449][0] = 0
    controls.append(rejected('illegal lower frame', lambda: audit(bad, module, geometry), fail))
    bad = copy.deepcopy(revised)
    bad['D'][0][2].pop()
    controls.append(rejected('missing dirty compensation', lambda: audit(bad, module, geometry), fail))
    directory = output / 'replacement' / 'records'
    rawpath = directory / '249-records.bin'
    raw = rawpath.read_bytes()
    recs = list(struct.iter_unpack('<6i', raw))
    index = next(i for i, r in enumerate(recs) if r[0] == 1 and r[5] == 4 and r[4] == 524)
    rawpath.write_bytes(raw[:24*index] + raw[24*(index+1):])
    try:
        controls.append(rejected('dropped exported block ADD', lambda: records_check(directory, revised), fail))
    finally:
        rawpath.write_bytes(raw)
    index = next(i for i, r in enumerate(recs) if r[0] == 0)
    badmove = list(recs[index])
    badmove[1] = 661
    rawpath.write_bytes(raw[:24*index] + struct.pack('<6i', *badmove) + raw[24*(index+1):])
    try:
        controls.append(rejected('MOVE on temporary COPY register', lambda: records_check(directory, revised), fail))
    finally:
        rawpath.write_bytes(raw)
    cert = {'status': 'PASS_R439_FRAME524', 'old_gates': 41, 'new_gates': 26,
            'fixed_factor_class': fixed_factors,
            'saved_with_cleanup': 30, 'labels': labels, 'columns': revised_audit['columns'],
            'old_phase_gates': baseline['gates'], 'new_phase_gates': revised_audit['gates'],
            'boolean_inputs': 4096, 'positive_matrices': positive, 'native_records': evidence,
            'reconstructed_word_sha256': sha(canonical(revised)), 'controls_rejected': controls,
            'kappa_claim': 'none; unchanged paid profile; hosted recursion not replayed'}
    target = HERE / 'CERTIFICATE.json'
    if write_certificate:
        target.write_text(json.dumps(cert, indent=2, sort_keys=True) + '\n')
    else:
        need(canonical(cert) == canonical(json.loads(target.read_text())), 'certificate mismatch')
    print('PASS_R439_FRAME524 gates=41->26 native_adds=24305->24275 columns=661 rank_mass=5129 controls=9')
    print('prefix', b['prefix'])
    return cert


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, help='new directory for reconstructed words and records')
    p.add_argument('--write-certificate', action='store_true')
    args = p.parse_args()
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        run(args.output.resolve(), args.write_certificate)
    else:
        with tempfile.TemporaryDirectory(prefix='r439-frame524-') as temporary:
            run(Path(temporary), args.write_certificate)


if __name__ == '__main__':
    main()
