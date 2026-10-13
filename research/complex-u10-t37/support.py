# SPDX-License-Identifier: Apache-2.0
"""I/O and source binding for the PR987-U10 / PR942-T37 composition."""
import gzip
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

if not __debug__:
    raise RuntimeError('Assertions are required; do not use -O')
P = Path(__file__).resolve().parent
ROOT = P.parents[1]
T37 = ROOT/'research/complex-t37-owners'
T21 = ROOT/'research/complex-t21-owners'
# Upstream same-package loaders expect their common module to remain importable
# when an imported function later loads a sibling module.
if str(T37) not in sys.path:
    sys.path.append(str(T37))


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, indent=2)+'\n')


def load(path, name):
    prior = sys.modules.pop('common', None)
    sys.path.insert(0, str(path.parent))
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.pop(0)
        sys.modules.pop('common', None)
        if prior is not None:
            sys.modules['common'] = prior


def validate():
    pins = read(P/'SOURCE-PINS.json')
    for name, digest in pins.items():
        path = (P/name).resolve()
        assert not Path(name).is_absolute() and path.is_relative_to(P)
        assert sha(path) == digest, 'Composition source drift: '+name
    upstream = load(T37/'package.py', 'u10_upstream_package').validate()
    return dict(composition_source_pins_sha256=sha(P/'SOURCE-PINS.json'),
                upstream=upstream)
