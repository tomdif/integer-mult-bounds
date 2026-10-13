"""Compare the original and replacement words with the pinned cohort checkers.

Adapted from Ali Romman PR688 by Thomas DiFiore / OpenAI Codex. Apache-2.0.
"""
import json
import os
import shlex
import subprocess
import sys


def run(root, out):
    import hashlib
    from pathlib import Path
    pins = json.loads((Path(__file__).resolve().parent / 'SOURCES.json').read_text())
    for path, expected in pins['native_inputs'].items():
        if hashlib.sha256((root / path).read_bytes()).hexdigest() != expected:
            raise ValueError('Native source hash mismatch: ' + path)
    package = root / "research/e8-bit-carrier-skeleton"
    bit = package / "code/bit"
    checkers = bit / "checkers"
    python = [sys.executable, "-B"]
    compiler = shlex.split(os.environ.get("CXX", "c++"))
    include = os.environ.get("BOOST_INCLUDE", "/usr/include")
    flags = ["-O2", "-std=c++17", "-DHDIM=8", "-DNCOPY=9", "-DVPORTS=111", "-DRHELP=439",
             "-I" + str(package / "portable-include"), "-I" + str(checkers), "-I" + include]
    bindir = out / "bin"
    bindir.mkdir()

    def call(name, command):
        with (out / (name + ".log")).open("w") as log:
            subprocess.run(list(map(str, command)), check=True, stdout=log, stderr=subprocess.STDOUT)

    call("compile-legality", compiler + flags + ["-o", bindir / "legality", checkers / "legality_h.cpp"])
    for pairs in (2, 4, 5):
        call("compile-columns" + str(pairs), compiler + flags + ["-DKPAIRS=" + str(pairs), "-o",
             bindir / ("columns" + str(pairs)), checkers / "columns_k.cpp"])
    results = {}
    for name in ("baseline", "replacement"):
        base = out / name
        records, cin, cout = (base / item for item in ("records", "cin", "cout"))
        call(name + "-export", python + [bit / "export_records.py", out / (name + ".json.gz"), records])
        call(name + "-cohort", python + [bit / "regression/stage_cohort.py", records, records, cin, cout])
        call(name + "-legality", [bindir / "legality", cin, cout, cout / "legality.json"])
        legality = json.loads((cout / "legality.json").read_text())
        if legality["status"] != "PASS_INDEPENDENT_COHORT_LEGALITY_SOURCE_OWNERS_AND_LIFECYCLE":
            raise ValueError("Legality did not pass")
        results[name] = {"legality": legality, "stages": {}}
        for pairs in (2, 4, 5):
            receipt = cout / ("columns.json" if pairs == 2 else "columns" + str(pairs) + ".json")
            call(name + "-columns" + str(pairs), [bindir / ("columns" + str(pairs)),
                 cout / "COHORT249-RECORDS.bin", receipt])
            data = json.loads(receipt.read_text())
            expected_status = ("PASS_NEW_COHORT249_ALL_FIVE_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL" if pairs == 2
                               else "PASS_NEW_COHORT249_ALL_BRIDGED_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL")
            if data["status"] != expected_status:
                raise ValueError("Formal columns did not pass")
            expected = 6 * (pairs - 1)
            if (len(data["negative_controls"]) != expected
                    or not all(c["rejected"] for c in data["negative_controls"])):
                raise ValueError("A bridge control failed")
            if data["formal_columns_checked"] != 222 * pairs + 439:
                raise ValueError("Wrong formal column count")
            results[name]["stages"][str(2 * pairs + 1)] = {
                key: data[key] for key in ("formal_columns_checked", "local_scalar_additions", "local_raw_H",
                                          "payload_prefix_bits", "payload_prefix_upper", "signed_lift_prefix")}
    for stages in ("5", "9", "11"):
        old, new = (results[name]["stages"][stages] for name in ("baseline", "replacement"))
        if old["local_raw_H"] != new["local_raw_H"] or old["local_scalar_additions"] - new["local_scalar_additions"] != 30:
            raise ValueError("Paid profile or XOR saving differs")
        if int(new["payload_prefix_upper"]) > int(old["payload_prefix_upper"]):
            raise ValueError("Payload bound increased")
        for a, b in zip(old["signed_lift_prefix"], new["signed_lift_prefix"]):
            if a["reverse"] != b["reverse"] or int(b["cancellation_free_signed_row_l1_upper"]) > int(a["cancellation_free_signed_row_l1_upper"]):
                raise ValueError("Signed bound increased")
    return results


if __name__ == "__main__":
    import argparse
    import importlib.util
    from pathlib import Path
    here = Path(__file__).resolve().parent
    root = here.parents[1]
    spec = importlib.util.spec_from_file_location("local_verify", here / "verify.py")
    verifier = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(verifier)
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, required=True, help="new directory; never overwrite")
    p.add_argument("--write-receipt", action="store_true")
    args = p.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    cert = verifier.run(args.output.resolve(), False)
    result = run(root, args.output.resolve())
    for name, data in result.items():
        expected = cert["native_records"][name]
        for stage, receipt in data["stages"].items():
            if (receipt["local_scalar_additions"] != expected["adds"]
                    or dict(receipt["local_raw_H"]) != {int(k): v for k, v in expected["paid_histogram"].items()}
                    or receipt["payload_prefix_bits"] != expected["prefix"]["payload_bits"]
                    or receipt["payload_prefix_upper"] != expected["prefix"]["payload_upper"]):
                raise ValueError("C++ and Python accounting differ")
            for bound in receipt["signed_lift_prefix"]:
                key = "reverse" if bound["reverse"] else "forward"
                if int(bound["cancellation_free_signed_row_l1_upper"]) != expected["prefix"][key]:
                    raise ValueError("C++ and Python prefix differ")
    # Runtime and absolute input paths are descriptive, not mathematical evidence.
    def normalize(value):
        if isinstance(value, dict):
            return {k: normalize(v) for k, v in value.items()
                    if k not in ("seconds", "local_scalar_stream")}
        if isinstance(value, list):
            return [normalize(x) for x in value]
        if isinstance(value, str) and str(args.output.resolve()) in value:
            return value.replace(str(args.output.resolve()), "$OUTPUT")
        return value
    stable = normalize(result)
    receipt_path = here / "NATIVE.json"
    rendered = json.dumps(stable, sort_keys=True, indent=2) + "\n"
    if args.write_receipt:
        receipt_path.write_text(rendered)
    elif stable != json.loads(receipt_path.read_text()):
        raise ValueError("Native receipt mismatch")
    (args.output / "NATIVE.json").write_text(rendered)
    print("PASS_R439_FRAME524_NATIVE columns=883,1327,1549 bridge_controls=96")
