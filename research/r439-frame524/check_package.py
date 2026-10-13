#!/usr/bin/env python3
"""Relocation and corruption controls. Thomas DiFiore / OpenAI Codex, Apache-2.0."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def main():
    with tempfile.TemporaryDirectory(prefix='frame524 relocation ') as tmp:
        root = Path(tmp)
        pkg = root / 'research/r439-frame524'
        shutil.copytree(HERE, pkg)
        pins = json.loads((HERE / 'SOURCES.json').read_text())
        for path in pins['execution_inputs']:
            dst = root / path
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / path, dst)
        cmd = [sys.executable, '-I', '-O', '-B', str(pkg / 'verify.py')]

        def call(expected, extra=()):
            result = subprocess.run(cmd + list(extra), capture_output=True, text=True, cwd=root)
            if expected == 'PASS':
                if result.returncode or 'PASS_R439_FRAME524' not in result.stdout:
                    raise RuntimeError(result.stdout + result.stderr)
            elif result.returncode == 0 or expected not in result.stderr:
                raise RuntimeError('corruption was not rejected as expected: ' + expected + result.stderr)

        call('PASS')
        tests = [
            (pkg / 'CANDIDATE.json', lambda d: d['candidate_ops'].pop(), 'frozen gate count'),
            (pkg / 'CANDIDATE.json', lambda d: d['candidate_ops'][0].reverse(), 'circuit F2 map changed'),
            (pkg / 'CERTIFICATE.json', lambda d: d.update(saved_with_cleanup=31), 'certificate mismatch'),
            (pkg / 'FACTOR-COMPARISON.json', lambda d: d['factors'][0]['distances'].__setitem__(1, 9999),
             'factor lower-bound edge'),
        ]
        for path, change, message in tests:
            saved = path.read_bytes()
            obj = json.loads(saved)
            change(obj)
            path.write_text(json.dumps(obj))
            try:
                call(message)
            finally:
                path.write_bytes(saved)
        source = root / next(iter(pins['execution_inputs']))
        original = source.read_bytes()
        source.write_bytes(original + b'corruption')
        try:
            call('source hash mismatch')
        finally:
            source.write_bytes(original)
        existing = root / 'already exists'
        existing.mkdir()
        marker = existing / 'user-work'
        marker.write_text('preserve me')
        call('FileExistsError', ['--output', str(existing)])
        if marker.read_text() != 'preserve me':
            raise RuntimeError('existing output changed')
        print('PASS_FRAME524_PACKAGE relocated_optimized=1 corruptions=5 preserved_output=1')


if __name__ == '__main__':
    main()
