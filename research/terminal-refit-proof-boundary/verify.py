#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check source-bound patch premises; optionally rebuild the scoped Lean proof.

Thomas DiFiore with OpenAI Codex assistance. Kernel harness conventions follow
Gareth Davidson's common-label tensor audit. No full supplier theorem is claimed.
"""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def source_check():
    pins = read(HERE / 'SOURCES.json')
    repo = HERE.parents[1]
    for path, digest in pins['inputs'].items():
        need(sha(repo / path) == digest, 'changed source: ' + path)
    for path, digest in pins['proof_files'].items():
        need(sha(HERE / path) == digest, 'changed proof source: ' + path)
    need((HERE / 'lean/LemmaG/Stream.lean').read_bytes() ==
         (repo / 'research/e8-lemma-g-lean/LemmaG/Stream.lean').read_bytes(),
         'changed common-label semantics')
    package = repo / 'research/paired-terminal-refit'
    manifest = read(package / 'MANIFEST.json')
    need({f.relative_to(package).as_posix(): sha(f) for f in package.rglob('*')
          if f.is_file() and f != package / 'MANIFEST.json'} == manifest,
         'released research package integrity')
    cases = []
    for tag in ['base', 'extra']:
        patch = read(package / f'data/PATCH-{tag}.json')
        parent = read(package / f'vendor/pr2917/data/WORD-{tag}.json.gz')
        word = read(package / f'data/WORD-{tag}.json.gz')
        restored = list(parent['restore'])
        need(len(patch['edits']) == 4, 'four declared edits')
        for edit in patch['edits']:
            i, old, new = edit['index'], edit['old'], edit['new']
            need(restored[i:i+len(old)] == old, 'literal old block')
            need(len(old) == len(new) and len(old) in (2, 3), 'block extent')
            a, b = old[-2:]
            need(a[0] == b[0] == 'add' and a[1] == b[1], 'same destination')
            d, s, t = a[1], a[2], b[2]
            need(s != d and t != d, 'source separation required by Lean theorem')
            need(new[-2][:-1] == b[:-1] and new[-1][:-1] == a[:-1],
                 'same two scalar additions, reversed')
            if len(old) == 3:
                need(old[0][0] == 'scale' and old[0][1] == d and
                     old[0][:-1] == new[0][:-1], 'unchanged preceding scale')
            restored[i:i+len(old)] = new
            cases.append(dict(provider=tag, destination=d, sources=[s, t],
                              coefficients=[a[3:5], b[3:5]],
                              preceding_scale=old[0][2:4] if len(old) == 3 else None))
        need(restored == word['restore'], 'all literal edits accounted for')
        for key in parent.keys() | word.keys():
            if key not in {'restore', 'cleanup', 'report'}:
                need(parent.get(key) == word.get(key), 'unchanged interface: ' + key)
        need([c['destination'] for c in cases if c['provider'] == tag] ==
             [408, 424, 428, 412], 'exact four helpers')
    return dict(status='PASS_LITERAL_REFIT_PREMISES', cases=cases,
                kernel_checked=False,
                boundary='Literal patch premises only. Full frame/native/cleanup admission is retained from the authenticated release; native recipes are not imported into Lean.')


def kernel(args, result):
    lake = args.lake.resolve()
    version = subprocess.check_output([str(lake.with_name('lean')), '--version'], text=True)
    need('4.32.2' in version, 'expected Lean 4.32.2')
    work = args.work.resolve()
    need(not work.exists(), 'kernel work directory must be fresh')
    shutil.copytree(HERE / 'lean', work)
    (work / '.lake').mkdir()
    packages = args.packages.resolve()
    dependencies = read(work / 'lake-manifest.json')['packages']
    for dep in dependencies:
        path = packages / dep['name']
        head = subprocess.check_output(['git', '-C', str(path), 'rev-parse', 'HEAD'], text=True).strip()
        need(head == dep['rev'], 'dependency revision: ' + dep['name'])
        need(subprocess.run(['git', '-C', str(path), 'diff', '--quiet', 'HEAD', '--']).returncode == 0,
             'modified dependency: ' + dep['name'])
    (work / '.lake/packages').symlink_to(packages, target_is_directory=True)
    env = dict(os.environ, PATH=str(lake.parent) + os.pathsep + os.environ.get('PATH', ''))
    build = subprocess.run([str(lake), 'build'], cwd=work, env=env, capture_output=True, text=True)
    output = build.stdout + build.stderr
    (work / 'BUILD.log').write_text(output)
    need(build.returncode == 0, 'Lean build failed: ' + str(work / 'BUILD.log'))
    targets = ['adds_commute', 'scale_then_adds_commute', 'replace_program']
    reports = re.findall(r"'TerminalRefit\.([^']+)' depends on axioms:\s*\[([^\]]*)\]", output)
    axioms = {name: sorted(x.strip() for x in raw.split(',') if x.strip()) for name, raw in reports}
    need(set(axioms) == set(targets), 'missing kernel axiom report')
    need(all(set(xs) <= {'propext', 'Classical.choice', 'Quot.sound'} for xs in axioms.values()),
         'unexpected proof axiom')
    # These claims are mathematically false; each must fail after valid imports.
    controls = {
        'self_reading_adds': '''import Refit
open LemmaG
example :
  (Event.add 0 1 1 : Event Nat Unit Nat).scal
    ((Event.add 0 0 1 : Event Nat Unit Nat).scal (fun _ => (1 : Nat))) 0 =
  (Event.add 0 0 1 : Event Nat Unit Nat).scal
    ((Event.add 0 1 1 : Event Nat Unit Nat).scal (fun _ => (1 : Nat))) 0 := by
  simp [Event.scal, Event.phys]
''',
        'different_shadow': '''import Refit
open LemmaG
example : (Event.scale 0 2 : Event Nat Unit Nat).scal (fun _ => (1 : Nat)) 0 = 1 := by
  simp [Event.scal, Event.phys]
'''}
    for name, code in controls.items():
        path = work / (name + '.lean')
        path.write_text(code)
        rejected = subprocess.run([str(lake), 'env', 'lean', path.name], cwd=work,
                                  env=env, capture_output=True, text=True)
        log = rejected.stdout + rejected.stderr
        (work / (name + '.log')).write_text(log)
        need(rejected.returncode != 0 and 'unsolved goals' in log and 'Unknown' not in log,
             'control did not reject its mathematical claim: ' + name)
    result.update(kernel_checked=True, status='PASS_SCOPED_LEAN_REFIT_PROOF',
                  lean_version=version.strip(), axioms=axioms,
                  rejected_controls=sorted(controls), build_log_sha256=sha(work / 'BUILD.log'),
                  lean_sources={str(f.relative_to(HERE / 'lean')): sha(f)
                                for f in (HERE / 'lean').rglob('*') if f.is_file()},
                  dependencies={d['name']: d['rev'] for d in dependencies})
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lake', type=Path)
    parser.add_argument('--packages', type=Path)
    parser.add_argument('--work', type=Path)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    result = source_check()
    if args.lake:
        need(args.packages is not None and args.work is not None, 'kernel mode needs --packages and --work')
        result = kernel(args, result)
    if args.out:
        with args.out.open('x') as stream:
            json.dump(result, stream, indent=2, sort_keys=True)
            stream.write('\n')
    print(result['status'], 'kernel_checked=' + str(result['kernel_checked']))


if __name__ == '__main__':
    main()
