"""Fresh, source-pinned scoped Lean checks; never a whole-machine receipt.

Cached dependency oleans are independently replayed by the official checker.
An optional Lean4Lean run is recorded separately, including incompatibility or
failure. This script does not implement the user's reviewed strict-acceptance
challenge workflow and never reports strict acceptance.
"""
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import re
import signal
import subprocess
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RECOVERY = ROOT / 'research/fine-prime-transform-assembly/Recovery.lean'


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    h = sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def run(argv, cwd, env, log, timeout=900):
    """Stop the entire child process group on timeout, interruption or >24GiB."""
    start = time.monotonic()
    peak = 0
    reason = None
    with log.open('w') as output:
        child = subprocess.Popen(argv, cwd=cwd, env=env, stdout=output,
                                 stderr=subprocess.STDOUT, start_new_session=True)
        try:
            while child.poll() is None:
                rows = subprocess.check_output(['ps', '-axo', 'pgid=,rss='], text=True)
                rss = sum(int(parts[1]) for line in rows.splitlines()
                          if len(parts := line.split()) == 2 and int(parts[0]) == child.pid)
                peak = max(peak, rss)
                if rss > 24 * 1024 * 1024:
                    reason = 'RSS_LIMIT_24_GIB'
                    break
                if time.monotonic() - start > timeout:
                    reason = 'TIMEOUT'
                    break
                time.sleep(0.2)
        finally:
            if child.poll() is None:
                os.killpg(child.pid, signal.SIGTERM)
                try:
                    child.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(child.pid, signal.SIGKILL)
                    child.wait()
    return {'argv': [str(x) for x in argv], 'returncode': child.returncode,
            'stopped': reason, 'peak_rss_kib': peak,
            'elapsed_seconds': round(time.monotonic() - start, 3),
            'log_sha256': digest(log)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('lake', 'packages', 'work', 'out'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--independent', type=Path)
    args = parser.parse_args()
    lake, packages, work = args.lake.resolve(), args.packages.resolve(), args.work.resolve()
    need(not work.exists(), 'fresh work directory required')
    need(not args.out.exists(), 'fresh output required')
    source_manifest = (HERE / 'SOURCES.json').read_bytes()
    source_pins = json.loads(source_manifest)['inputs']
    pinned_bytes = {}
    for relative, expected in source_pins.items():
        pinned_bytes[relative] = (ROOT / relative).read_bytes()
        need(sha256(pinned_bytes[relative]).hexdigest() == expected, 'source pin mismatch: ' + relative)
    version = subprocess.check_output([str(lake.with_name('lean')), '--version'], text=True).strip()
    need('version 4.32.2' in version, 'Lean 4.32.2 required')
    manifest = json.loads((HERE / 'lean/lake-manifest.json').read_text())
    for dep in manifest['packages']:
        path = packages / dep['name']
        head = subprocess.check_output(['git', '-C', str(path), 'rev-parse', 'HEAD'], text=True).strip()
        need(head == dep['rev'], 'dependency revision mismatch: ' + dep['name'])
        need(subprocess.run(['git', '-C', str(path), 'diff', '--quiet', 'HEAD', '--']).returncode == 0,
             'modified dependency: ' + dep['name'])
    work.mkdir()
    for relative, data in pinned_bytes.items():
        source = ROOT / relative
        if source.parent == HERE / 'lean' or (source.parent == HERE and source.suffix == '.lean'):
            (work / source.name).write_bytes(data)
    (work / 'Recovery.lean').write_bytes(pinned_bytes[str(RECOVERY.relative_to(ROOT))])
    (work / 'SOURCE-MANIFEST.json').write_bytes(source_manifest)
    (work / '.lake').mkdir()
    (work / '.lake/packages').symlink_to(packages, target_is_directory=True)
    env = dict(os.environ, PATH=str(lake.parent) + os.pathsep + os.environ.get('PATH', ''))
    build = run([str(lake), 'build', 'Audit'], work, env, work / 'BUILD.log')
    need(build['returncode'] == 0 and not build['stopped'], 'build failed: ' + str(work / 'BUILD.log'))
    build_text = (work / 'BUILD.log').read_text()
    match = re.search(r'SCOPED_AXIOM_AUDIT declarations=(\d+) theorems=(\d+)', build_text)
    need(match is not None, 'missing exhaustive declaration audit')
    reports = re.findall(r"'([^']+)' depends on axioms:\s*\[([^\]]*)\]", build_text)
    axioms = {name: sorted(x.strip() for x in raw.split(',') if x.strip()) for name, raw in reports}
    need('WholeMachine.BoundedCalls.scaled_schedule' in axioms, 'missing rescaling theorem audit')
    need(all(set(xs) <= {'propext', 'Classical.choice', 'Quot.sound'} for xs in axioms.values()),
         'unapproved axiom')
    official = run([str(lake), 'env', str(lake.with_name('leanchecker')), '--fresh', '--verbose', 'Audit'],
                   work, env, work / 'OFFICIAL-FRESH.log', timeout=1200)
    need(official['returncode'] == 0 and not official['stopped'],
         'official fresh replay failed: ' + str(work / 'OFFICIAL-FRESH.log'))
    need('replaying Audit with --fresh' in (work / 'OFFICIAL-FRESH.log').read_text(), 'wrong replay target')
    controls = {
        'wrong_kappa': 'example : WholeMachine.Parameters.kappa = (1/100 : ℚ) := by\n'
                       '  norm_num [WholeMachine.Parameters.kappa, WholeMachine.Parameters.C]\n',
        'completed_map_bounds_calls': 'example : ‖WholeMachine.Counterexamples.D ((1/2 : ℝ), 0)‖ ≤ 1 := by\n'
                                     '  norm_num [WholeMachine.Counterexamples.D, Prod.norm_def]\n',
        'omit_restore_precision': 'example : (2:ℝ)^4 * ((2:ℝ)^3)⁻¹ ≤ ((2:ℝ)^0)⁻¹ := by norm_num\n',
        'erase_visited_history': 'example : (WholeMachine.Target.visited WholeMachine.Counterexamples.eraser\n'
                                '  WholeMachine.Counterexamples.emptyInput 3).card = 0 := by decide\n',
        'omit_handoff': 'open WholeMachine.Target WholeMachine.Composition\n'
                        'def stop : Program 0 1 0 := ⟨0, fun _ _ => none⟩\n'
                        'example : (run (sequence stop stop) (left (input stop [] [])) 0).state =\n'
                        '  (right (restart stop (input stop [] [])) : Configuration 0 2 0).state := by decide\n'
    }
    rejected = {}
    for name, code in controls.items():
        source = work / (name + '.lean')
        source.write_text('import Audit\n' + code)
        log = work / (name + '.log')
        result = run([str(lake), 'env', 'lean', '-j1', '-M8192', source.name], work, env, log, timeout=180)
        message = log.read_text()
        need(result['returncode'] != 0 and not result['stopped'], 'false control accepted: ' + name)
        mathematical_rejection = 'unsolved goals' in message or (
            'Tactic `decide` proved that the proposition' in message and 'is false' in message)
        need(mathematical_rejection and
             not any(term in message for term in ('Unknown', 'unknown module', 'failed to synthesize', 'unexpected token')),
             'control did not fail mathematically: ' + name)
        rejected[name] = result
    independent = {'status': 'NOT_RUN', 'accepted': False}
    if args.independent:
        executable = args.independent.resolve()
        need(executable.is_file(), 'missing independent checker')
        independent = run([str(lake), 'env', str(executable), '--fresh', 'Audit'], work, env,
                          work / 'INDEPENDENT.log', timeout=1200)
        independent['executable_sha256'] = digest(executable)
        independent['accepted'] = False  # No reviewed strict challenge in this harness.
        independent['status'] = 'RAW_REPLAY_SUCCEEDED' if independent['returncode'] == 0 else 'RAW_REPLAY_FAILED'
    result = {
        'status': 'PASS_SCOPED_LEAN_PROGRESS', 'whole_machine_proved': False,
        'target': 'WholeMachine.Target.Complete', 'strict_acceptance': False,
        'lean': version, 'platform': platform.platform(),
        'audit': {'declarations': int(match[1]), 'theorems_including_generated': int(match[2]),
                  'printed_roots': axioms},
        'build': build, 'official_fresh_replay': official, 'independent': independent,
        'rejected_controls': rejected,
        'tool_sha256': {name: digest(lake.with_name(name)) for name in ('lean', 'lake', 'leanchecker')},
        'dependencies': {dep['name']: dep['rev'] for dep in manifest['packages']},
        'source_manifest_sha256': sha256(source_manifest).hexdigest(),
        'local_source_sha256': {p.name: digest(p) for p in sorted(work.glob('*.lean'))
                                if p.stem not in controls},
        'local_olean_sha256': {str(p.relative_to(work)): digest(p)
                              for p in sorted((work / '.lake/build/lib/lean').glob('*.olean*'))},
        'scope': 'Finite tape composition, visited-space semantics, numerical schedules and recovery implications; '
                 'no multiplier program or proof of Target.Complete.'
    }
    with args.out.open('x') as stream:
        json.dump(result, stream, sort_keys=True, indent=2)
        stream.write('\n')
    print(json.dumps({'status': result['status'], 'audit': result['audit']['declarations'],
                      'whole_machine_proved': False, 'strict_acceptance': False,
                      'independent': independent['status']}, sort_keys=True))


if __name__ == '__main__':
    main()
