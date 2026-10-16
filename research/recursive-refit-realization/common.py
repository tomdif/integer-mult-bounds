"""Source authentication for the recursive refit investigation (Apache-2.0)."""
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path
import sys
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
_temporary = None


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    # JSON object keys are strings. Normalize that serialization boundary
    # before sorting, while preserving value types (True is not integer 1).
    return json.dumps(json.loads(json.dumps(value)), sort_keys=True,
                      separators=(",", ":")).encode()


def digest(value):
    return sha256(value).hexdigest()


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


def inputs():
    data = {}
    for entry in json.loads((HERE / "INPUTS.json").read_text()):
        raw = (HERE / entry["path"]).read_bytes()
        need(digest(raw) == entry["sha256"], "changed refit input: " + entry["path"])
        name = entry["path"].removeprefix("inputs/")
        data[name] = json.loads(gzip.decompress(raw) if name.endswith(".gz") else raw)
    return data


def ordinary_sources():
    """Keep all predecessor files unchanged, including their nested checks."""
    global _temporary
    if _temporary is not None:
        return Path(_temporary.name)
    raw = (HERE / "vendor/pr2899.tar").read_bytes()
    need(digest(raw) == "fc4a2e07423835737c8fb3872664b16ff12aa4cf83b1e26e49878debef40c531",
         "pinned PR2899 Git export")
    _temporary = tempfile.TemporaryDirectory(prefix="refit-ordinary-")
    destination = Path(_temporary.name)
    with tarfile.open(HERE / "vendor/pr2899.tar") as archive:
        for item in archive.getmembers():
            path = Path(item.name)
            need(not path.is_absolute() and ".." not in path.parts
                 and (item.isfile() or item.isdir()), "regular archive members")
        archive.extractall(destination, filter="data")
    source = module("source", destination / "source.py")
    source.ROOT = ROOT
    source.activate()
    sys.path.insert(0, str(destination))
    return destination
