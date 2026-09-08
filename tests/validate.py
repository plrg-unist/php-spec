#!/usr/bin/env python3
"""Independent syntax differential and checked-AST round-trip validation."""
import argparse
import base64
import collections
import copy
import json
import select
import subprocess
import tempfile
from pathlib import Path
from corpus import ROOT, inputs

IGNORED_META = {"startLine", "endLine", "startFilePos", "endFilePos", "startTokenPos",
                "endTokenPos", "kind", "rawValue", "docLabel", "docIndentation", "hasLeadingNewline"}


def normalize(value):
    if isinstance(value, list):
        return [normalize(item) for item in value]
    if isinstance(value, dict):
        if "comment" in value:
            return {"comment": value["comment"][:2]}
        return {key: normalize({name: item for name, item in child.items() if name not in IGNORED_META})
                if key == "meta" else normalize(child) for key, child in value.items()}
    return value


class Worker:
    def __init__(self, command):
        self.process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=tempfile.TemporaryFile())

    def call(self, **request):
        self.process.stdin.write(json.dumps(request, separators=(",", ":")).encode() + b"\n")
        self.process.stdin.flush()
        ready, _, _ = select.select([self.process.stdout], [], [], 60)
        if not ready:
            raise TimeoutError("worker response timeout")
        line = self.process.stdout.readline()
        if not line:
            raise RuntimeError("worker exited " + str(self.process.poll()))
        return json.loads(line)

    def close(self):
        self.process.stdin.close()
        try:
            self.process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            self.process.kill()


def require(response, stage):
    if not response.get("ok"):
        raise ValueError(stage + ": " + json.dumps(response))
    return response


def node_tags(value):
    if isinstance(value, list):
        for item in value:
            yield from node_tags(item)
    elif isinstance(value, dict):
        if "node" in value:
            yield value["node"]
        for child in value.values():
            yield from node_tags(child)


def lint(source, ini):
    with tempfile.NamedTemporaryFile(suffix=".php") as fixture:
        fixture.write(source)
        fixture.flush()
        command = [str(ROOT / ".tools/php/bin/php"), "-n"]
        for key, value in ini.items():
            command.extend(["-d", key + "=" + value])
        result = subprocess.run(command + ["-l", fixture.name], capture_output=True, timeout=30)
        return {"accepted": result.returncode == 0,
                "diagnostic_b64": base64.b64encode(result.stdout + result.stderr).decode()}


def validate(record, frontend, adapter, elaborate=False):
    source = record["source_b64"]
    oracle = require(frontend.call(op="oracle", source=source), "oracle")
    parsed = require(frontend.call(op="parse", source=source), "frontend")
    result = {"oracle": oracle["accepted"], "frontend": parsed["accepted"]}
    if "expected" in record and oracle["accepted"] != (record["expected"] == "accept"):
        return {**result, "status": "fixture_expectation_failure"}
    if oracle["accepted"] != parsed["accepted"]:
        compiled = lint(base64.b64decode(source), record.get("ini", {}))
        result.update(lint=compiled, oracle_detail=oracle, frontend_detail=parsed)
        result["status"] = "compile_phase_difference" if oracle["accepted"] and not compiled["accepted"] else "acceptance_mismatch"
        return result
    if not oracle["accepted"]:
        return {**result, "status": "parser_rejection", "oracle_detail": oracle, "frontend_detail": parsed}
    ast = parsed["ast"]
    first = require(adapter.call(op="elaborate" if elaborate else "check", ast=ast), "adapter")
    if first["ast"] != ast:
        raise ValueError("forward/reverse transport changed original AST")
    printed = require(frontend.call(op="print", ast=first["ast"]), "fresh reconstruction")
    if printed["ast"] != first["ast"]:
        raise ValueError("fresh node reconstruction changed checked AST")
    out_oracle = require(frontend.call(op="oracle", source=printed["source"]), "output oracle")
    if not out_oracle["accepted"]:
        raise ValueError("canonical output rejected: " + json.dumps(out_oracle))
    reparsed = require(frontend.call(op="parse", source=printed["source"]), "reparse")
    if not reparsed["accepted"]:
        raise ValueError("canonical output rejected by frontend")
    second = require(adapter.call(op="check", ast=reparsed["ast"]), "second adapter")
    reprinted = require(frontend.call(op="print", ast=second["ast"]), "second fresh reconstruction")
    if printed["source"] != reprinted["source"]:
        raise ValueError("canonical printing is not idempotent")
    if normalize(ast) != normalize(second["ast"]):
        return {**result, "status": "ast_roundtrip_failure", "original": ast, "reparsed": second["ast"], "printed": printed["source"]}
    return {**result, "status": "pass", "nodes": sorted(set(node_tags(ast)))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", action="store_true")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--match", default="")
    parser.add_argument("--output", type=Path, default=ROOT / "coverage/results-targeted.jsonl")
    parser.add_argument("--elaborate", action="store_true")
    args = parser.parse_args()
    workers = {}
    adapter = Worker([str(ROOT / "_build/default/adapter/main.exe"), str(ROOT)])
    counts, node_witnesses = collections.Counter(), {}
    records = inputs()
    seen = 0
    try:
        with args.output.open("w") as output:
            for record in records:
                if not args.corpus and record["origin"] != "targeted":
                    continue
                if args.match not in record["id"]:
                    continue
                if args.limit and seen >= args.limit:
                    break
                seen += 1
                identity = {key: value for key, value in record.items() if key != "source_b64"}
                if record["status"] != "source":
                    result = identity
                else:
                    ini = {"short_open_tag": "0", **record.get("ini", {})}
                    profile = tuple(sorted(ini.items()))
                    if profile not in workers:
                        command = [str(ROOT / ".tools/php/bin/php"), "-n"]
                        for key, value in profile:
                            command.extend(["-d", key + "=" + value])
                        workers[profile] = Worker(command + [str(ROOT / "frontend/worker.php")])
                    try:
                        result = {**identity, **validate(record, workers[profile], adapter, args.elaborate)}
                    except Exception as error:
                        result = {**identity, "status": "failure", "error": str(error)}
                        # A malformed response must never shift later request/response pairs.
                        workers.pop(profile).close()
                counts[result["status"]] += 1
                for node in result.get("nodes", []):
                    if len(node_witnesses.setdefault(node, [])) < 3:
                        node_witnesses[node].append(record["id"])
                output.write(json.dumps(result, separators=(",", ":")) + "\n")
                output.flush()
                if seen % 100 == 0 or result["status"] not in {"pass", "parser_rejection"}:
                    print(json.dumps({"seen": seen, "id": record["id"], "status": result["status"], "counts": counts}), flush=True)
    finally:
        adapter.close()
        for worker in workers.values():
            worker.close()
    summary = {"tested": seen, "counts": counts, "nodes": node_witnesses}
    args.output.with_suffix(".summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, sort_keys=True))
    return int(any(counts[key] for key in {"failure", "acceptance_mismatch", "ast_roundtrip_failure", "fixture_expectation_failure", "missing_fixture", "invalid_container"}))


if __name__ == "__main__":
    raise SystemExit(main())
