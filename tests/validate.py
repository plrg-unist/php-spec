#!/usr/bin/env python3
"""Independent syntax differential and checked-AST round-trip validation."""
import argparse
import base64
import collections
import copy
import hashlib
import json
import os
import select
import re
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path
from corpus import ROOT, inputs

sys.setrecursionlimit(50000)
sys.path.insert(0, str(ROOT / "frontend"))
import wire

IGNORED_META = {"startLine", "endLine", "startFilePos", "endFilePos", "startTokenPos",
                "endTokenPos", "kind", "rawValue", "docLabel", "docIndentation", "hasLeadingNewline", "namespaceBraceLine", "statementTerminatorLine", "statementBodyLine", "parenthesizedConditional", "destructuringArrayKind", "listFirstHoleLine"}


def normalize(value):
    if isinstance(value, list):
        return [normalize(item) for item in value]
    if isinstance(value, dict):
        if "comment" in value:
            doc, encoded = value["comment"][:2]
            text = base64.b64decode(encoded).decode("latin1").replace("\r\n", "\n")
            first, separator, rest = text.partition("\n")
            if separator:
                lines = rest.split("\n")
                if all(re.match(r"^[ \t]*\*", line) for line in lines if line):
                    rest = "\n".join(re.sub(r"^[ \t]+(?=\*)", "", line) for line in lines)
                else:
                    rest = textwrap.dedent(rest)
                text = first + separator + rest
            return {"comment": [doc, base64.b64encode(text.encode("latin1")).decode()]}
        return {key: normalize({name: item for name, item in child.items() if name not in IGNORED_META})
                if key == "meta" else normalize({name: item for name, item in child.items() if name not in {"original", "bom", "source", "lexer"}})
                if key == "encoding" else normalize(child) for key, child in value.items()}
    return value


def structurally_equal(left, right):
    pending = [(left, right)]
    while pending:
        left, right = pending.pop()
        if type(left) is not type(right):
            return False
        if isinstance(left, dict):
            if left.keys() != right.keys():
                return False
            pending.extend((value, right[key]) for key, value in left.items())
        elif isinstance(left, list):
            if len(left) != len(right):
                return False
            pending.extend(zip(left, right))
        elif left != right:
            return False
    return True


class Worker:
    def __init__(self, command):
        environment = os.environ.copy()
        environment.pop("PHP_SPEC_SCRIPT_ENCODING", None)
        selected = []
        index = 0
        while index < len(command):
            if command[index] == "-d" and index + 1 < len(command) and command[index + 1].startswith("zend.script_encoding="):
                environment["PHP_SPEC_SCRIPT_ENCODING"] = command[index + 1].split("=", 1)[1]
                index += 2
            else:
                selected.append(command[index])
                index += 1
        command = selected
        if command[-1] == str(ROOT / "frontend/worker.php"):
            command = command[:-1] + ["-d", "extension=" + str(ROOT / ".tools/php-file.so"), command[-1]]
        self.errors = tempfile.TemporaryFile()
        self.process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=self.errors, env=environment)

    def call(self, **request):
        payload = wire.dumps(request)
        try:
            self.process.stdin.write(payload.encode() + b"\n")
            self.process.stdin.flush()
        except BrokenPipeError as error:
            raise RuntimeError(self.failure()) from error
        ready, _, _ = select.select([self.process.stdout], [], [], 60)
        if not ready:
            raise TimeoutError("worker response timeout")
        line = self.process.stdout.readline()
        if not line:
            raise RuntimeError(self.failure())
        return wire.loads(line)

    def failure(self):
        self.errors.seek(0)
        return "worker exited " + str(self.process.poll()) + ": " + self.errors.read()[-2000:].decode("utf-8", "replace")

    def close(self):
        try:
            self.process.stdin.close()
        except BrokenPipeError:
            pass
        try:
            self.process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait()
        self.process.stdout.close()
        self.errors.close()


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


def retained_comments(value):
    pending, comments = [value], {}
    while pending:
        current = pending.pop()
        if isinstance(current, dict):
            if "comment" in current:
                doc, text, _, _, token, *_ = current["comment"]
                comments[(token, doc, text)] = (doc, text)
            pending.extend(current.values())
        elif isinstance(current, list):
            pending.extend(current)
    return collections.Counter(comments.values())


def lint(source, ini):
    with tempfile.NamedTemporaryFile(suffix=".php") as fixture:
        fixture.write(source)
        fixture.flush()
        command = [str(ROOT / ".tools/php/bin/php"), "-n", "-d", "memory_limit=-1", "-d", "short_open_tag=0"]
        for key, value in ini.items():
            command.extend(["-d", key + "=" + value])
        result = subprocess.run(command + ["-l", fixture.name], capture_output=True, timeout=30)
        return {"accepted": True} if result.returncode == 0 else {
            "accepted": False, "diagnostic_b64": base64.b64encode(result.stdout + result.stderr).decode()}


def validate(record, frontend, adapter, elaborate=False, observations=None):
    source = record["source_b64"]
    oracle = require(frontend.call(op="oracle", source=source), "oracle")
    if observations is not None:
        observations.update(oracle=oracle["accepted"], oracle_detail=oracle)
    parsed = frontend.call(op="parse", source=source)
    frontend_detail = {key: value for key, value in parsed.items() if key not in {"ast", "token_comments"}}
    if observations is not None:
        observations.update(frontend=parsed.get("accepted"), frontend_detail=frontend_detail)
    parsed = require(parsed, "frontend")
    result = {"oracle": oracle["accepted"], "frontend": parsed["accepted"],
              "oracle_detail": oracle, "frontend_detail": frontend_detail}
    if "expected" in record and oracle["accepted"] != (record["expected"] == "accept"):
        return {**result, "status": "fixture_expectation_failure"}
    if oracle["accepted"] != parsed["accepted"]:
        compiled = lint(base64.b64decode(source), record.get("ini", {}))
        result.update(lint=compiled)
        result["status"] = "unreviewed_phase_difference" if oracle["accepted"] and not compiled["accepted"] else "acceptance_mismatch"
        return classify_phase_difference(record, result)
    if not oracle["accepted"]:
        return {**result, "status": "parser_rejection", "oracle_detail": oracle, "frontend_detail": parsed}
    ast = parsed["ast"]
    comments = retained_comments(ast)
    if "token_comments" in parsed:
        lexical = collections.Counter((comment["doc"], comment["text"]) for comment in parsed["token_comments"])
        if comments != lexical:
            raise ValueError("source comments missing or duplicated in AST: lexical=" + str(sum(lexical.values())) + ", retained=" + str(sum(comments.values())))
    if "retained_comments" in record and sum(comments.values()) != record["retained_comments"]:
        raise ValueError("hand-counted source comment retention failed")
    first = require(adapter.call(op="elaborate" if elaborate else "check", ast=ast), "adapter")
    if not structurally_equal(first["ast"], ast):
        raise ValueError("forward/reverse transport changed original AST")
    printed = require(frontend.call(op="print", ast=first["ast"]), "fresh reconstruction")
    if not structurally_equal(printed["ast"], first["ast"]):
        raise ValueError("fresh node reconstruction changed checked AST")
    out_oracle = require(frontend.call(op="oracle", source=printed["source"]), "output oracle")
    result.update(printed_oracle=out_oracle["accepted"], printed_oracle_detail=out_oracle)
    if observations is not None:
        observations.update(result, printed_source=printed["source"])
    if not out_oracle["accepted"]:
        raise ValueError("canonical output rejected: " + json.dumps(out_oracle))
    reparsed = frontend.call(op="parse", source=printed["source"])
    result.update(printed_frontend=reparsed.get("accepted"), printed_frontend_detail={key: value for key, value in reparsed.items() if key not in {"ast", "token_comments"}})
    if observations is not None:
        observations.update(result)
    reparsed = require(reparsed, "reparse")
    if not reparsed["accepted"]:
        raise ValueError("canonical output rejected by frontend")
    second = require(adapter.call(op="check", ast=reparsed["ast"]), "second adapter")
    if not structurally_equal(second["ast"], reparsed["ast"]):
        raise ValueError("second forward/reverse transport changed reparsed AST")
    reprinted = require(frontend.call(op="print", ast=second["ast"]), "second fresh reconstruction")
    if not structurally_equal(reprinted["ast"], second["ast"]):
        raise ValueError("second fresh node reconstruction changed checked AST")
    if printed["source"] != reprinted["source"]:
        raise ValueError("canonical printing is not idempotent")
    if not structurally_equal(normalize(ast), normalize(second["ast"])):
        return {**result, "status": "ast_roundtrip_failure", "original": ast, "reparsed": second["ast"], "printed": printed["source"]}
    return {**result, "status": "pass", "nodes": sorted(set(node_tags(ast)))}



def classify_phase_difference(record, result):
    if result['status'] != 'unreviewed_phase_difference' or result.get('lint', {}).get('accepted') is not False:
        return result
    entries = json.loads((ROOT / 'tests/phase-discrepancies.json').read_text())
    entry = next((entry for entry in entries if entry['id'] == record['id']), None)
    if entry is None or entry['sha256'] != record['sha256'] or entry['ini'] != record.get('ini', {}):
        return result
    diagnostic = base64.b64decode(result['lint']['diagnostic_b64']).decode('utf-8', 'replace')
    frontend_message = base64.b64decode(result['frontend_detail'].get('message', '')).decode('utf-8', 'replace')
    if frontend_message != entry['frontend_message'] or entry['lint_contains'] not in diagnostic:
        return result
    return {**result, 'raw_status': result['status'], 'status': 'compile_phase_difference',
            'disposition': entry['reason'], 'restriction': entry['restriction'], 'evidence': entry['evidence']}


def implementation_fingerprint():
    roots = ['frontend', 'adapter', 'spec', 'native', 'tests', 'scripts', 'bin', 'vendor/php-parser']
    paths = [path for root in roots for path in (ROOT / root).rglob('*')
             if path.is_file() and not {'__pycache__', '_build'}.intersection(path.relative_to(ROOT).parts)
             and path.suffix != '.pyc']
    paths += [ROOT / name for name in ['Makefile', 'dune-project', '.tools/php/bin/php',
              '.tools/php-file.so', '_build/default/adapter/main.exe', 'coverage/encoding-spellings.json',
              'coverage/semantics/comparison-phase-originals.json',
              'coverage/semantics/comparison-overflow-draft-disagreement.json']]
    # Dune bookkeeping is generated, but executed artifacts remain evidence
    # inputs. Syntax-only builds need not have built the semantic helper yet;
    # helper campaigns also require and fingerprint this binary directly.
    helper = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    if helper.exists():
        paths.append(helper)
    digest = hashlib.sha256()
    for path in sorted(set(paths)):
        digest.update(str(path.relative_to(ROOT)).encode() + b'\0')
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    return {'sha256': digest.hexdigest(), 'files': len(set(paths)), 'scope': roots + ['Makefile', 'dune-project', 'runtime binaries', 'encoding-spellings inventory', 'comparison oracle archives']}


def classify_documented_invalid(result):
    ledger = json.loads((ROOT / 'tests/invalid-discrepancies.json').read_text())
    entry = next((entry for entry in ledger if entry['id'] == result['id']), None)
    if entry is None or entry['sha256'] != result['sha256'] or result.get('lint', {}).get('accepted') is not False:
        return result
    diagnostic = base64.b64decode(result['lint']['diagnostic_b64']).decode('utf-8', 'replace')
    if entry['lint_contains'] not in diagnostic or entry['failure_prefix'] not in result['error']:
        return result
    return {**result, 'raw_status': result['status'], 'status': 'invalid_program_roundtrip_difference',
            'disposition': entry['reason'], 'evidence': entry['evidence']}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", action="store_true")
    parser.add_argument("--generated", action="store_true")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--match", default="")
    parser.add_argument("--output", type=Path, default=ROOT / "coverage/results-targeted.jsonl")
    parser.add_argument("--elaborate", action="store_true")
    parser.add_argument("--retry", type=Path, help="Rerun unresolved source IDs from a previous report")
    parser.add_argument("--lint-all", action="store_true", help="Classify compilation separately for every parser-accepted source")
    parser.add_argument("--shard", help="Zero-based deterministic shard i/n of eligible inputs")
    args = parser.parse_args()
    shard = None
    if args.shard:
        try:
            index, count = map(int, args.shard.split('/'))
            if not 0 <= index < count:
                raise ValueError()
            shard = {'index': index, 'count': count}
        except ValueError:
            parser.error('--shard must be i/n with 0 <= i < n')
    fingerprint = implementation_fingerprint()
    retry = None
    if args.retry:
        retry = {record["id"] for record in (json.loads(line) for line in args.retry.open())
                 if record["status"] not in {"pass", "parser_rejection", "compile_phase_difference", "non_source", "redirect_container"}}
    workers = {}
    adapter = Worker([str(ROOT / "_build/default/adapter/main.exe"), str(ROOT)])
    counts, node_witnesses = collections.Counter(), {}
    if args.generated:
        from generated import generated
        records = generated()
    else:
        records = inputs()
    seen, eligible = 0, 0
    try:
        with args.output.open("w") as output:
            for record in records:
                if not args.corpus and not args.generated and record["origin"] != "targeted":
                    continue
                if args.match not in record["id"]:
                    continue
                if retry is not None and record["id"] not in retry:
                    continue
                if args.limit and eligible >= args.limit:
                    break
                ordinal = eligible
                eligible += 1
                if shard and ordinal % shard['count'] != shard['index']:
                    continue
                seen += 1
                identity = {key: value for key, value in record.items() if key != "source_b64"}
                if shard:
                    identity['_ordinal'] = ordinal
                if record["status"] != "source":
                    result = identity
                else:
                    ini = {"short_open_tag": "0", **record.get("ini", {})}
                    profile = tuple(sorted(ini.items()))
                    if profile not in workers:
                        if len(workers) >= 16:
                            workers.pop(next(iter(workers))).close()
                        command = [str(ROOT / ".tools/php/bin/php"), "-n", "-d", "memory_limit=-1", "-d", "display_errors=stderr"]
                        for key, value in profile:
                            command.extend(["-d", key + "=" + value])
                        workers[profile] = Worker(command + [str(ROOT / "frontend/worker.php")])
                    try:
                        observations = {}
                        result = {**identity, **validate(record, workers[profile], adapter, args.elaborate, observations)}
                        if args.lint_all and result.get("oracle") and "lint" not in result:
                            result["lint"] = lint(base64.b64decode(record["source_b64"]), ini)
                    except Exception as error:
                        result = {**identity, **observations, "status": "failure", "error": str(error)}
                        if result.get("oracle"):
                            result["lint"] = lint(base64.b64decode(record["source_b64"]), ini)
                        result = classify_documented_invalid(result)
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
    final_fingerprint = implementation_fingerprint()
    stable = fingerprint == final_fingerprint
    summary = {"tested": seen, "counts": counts, "nodes": node_witnesses,
               "implementation": fingerprint, "stable_implementation": stable}
    if shard:
        summary.update(shard=shard, eligible_count=eligible)
    if not stable:
        summary["implementation_after"] = final_fingerprint
    args.output.with_suffix(".summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, sort_keys=True))
    return int(not stable or any(counts[key] for key in {"failure", "acceptance_mismatch", "unreviewed_phase_difference", "ast_roundtrip_failure", "fixture_expectation_failure", "missing_fixture", "invalid_container"}))


if __name__ == "__main__":
    raise SystemExit(main())
