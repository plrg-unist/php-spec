#!/usr/bin/env python3
"""Map real Bison reductions to source witnesses using an optional trace build."""
import argparse
import base64
import json
import os
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from corpus import ROOT, inputs


def inventory():
    with tempfile.TemporaryDirectory() as temporary:
        xml = Path(temporary) / "grammar.xml"
        subprocess.run(["bison", "--xml=" + str(xml), "-o", temporary + "/parser.c",
                        str(ROOT / "vendor/php-src/Zend/zend_language_parser.y")], check=True)
        grammar = ET.parse(xml).getroot()
    return [{"rule": int(rule.attrib["number"]), "lhs": rule.findtext("lhs"),
             "rhs": [item.text for item in rule.findall("rhs/symbol")],
             "synthetic": rule.findtext("lhs").startswith(("@", "$")),
             "witnesses": []} for rule in grammar.findall("grammar/rules/rule")]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    output = ROOT / "coverage/grammar.json"
    rules = json.loads(output.read_text())["productions"] if args.resume else inventory()
    index = {rule["rule"]: rule for rule in rules}
    scanner_path = ROOT / "coverage/scanner.json"
    scanner = json.loads(scanner_path.read_text())
    if not args.resume:
        for entry in scanner["rules"]:
            entry["witnesses"] = []
            entry.pop("rejection_witnesses", None)
            entry.pop("lint_witnesses", None)
    scanner_index = {rule["line"]: rule for rule in scanner["rules"]}
    php = ROOT / ".tools/php-coverage-build/sapi/cli/php"
    env = {**os.environ, "LD_PRELOAD": str(ROOT / ".tools/trace-enable.so")}
    seen, accepted, rejected, crashes = 0, 0, 0, []
    records = inputs()
    if not args.corpus:
        records = (record for record in records if record["origin"] == "targeted")
    with tempfile.TemporaryDirectory() as temporary:
        source = Path(temporary) / "source.php"
        for record in records:
            if record["status"] != "source":
                continue
            if args.limit and seen >= args.limit:
                break
            source.write_bytes(base64.b64decode(record["source_b64"]))
            command = [str(php), "-n", "-d", "short_open_tag=0", "-d", "display_errors=stderr", "-d", "extension=" + str(ROOT / ".tools/php-file.so")]
            for key, value in record.get("ini", {}).items():
                if key == "zend.script_encoding":
                    continue
                command.extend(["-d", key + "=" + value])
            command.extend([str(ROOT / "tests/trace-runner.php"), str(source), json.dumps(record.get("ini", {}))])
            seen += 1
            try:
                result = subprocess.run(command, env=env, capture_output=True, timeout=30)
            except subprocess.TimeoutExpired:
                crashes.append({"id": record["id"], "status": "timeout"})
                continue
            if result.returncode:
                crashes.append({"id": record["id"], "status": "crash", "exit": result.returncode})
                continue
            trace = result.stderr.split(b"SOURCE_BEGIN\n")[-1].split(b"SOURCE_END\n")[0]
            for number in set(re.findall(rb"LEX_RULE:(\d+)", trace)):
                entry = scanner_index[int(number)]
                witnesses = entry.setdefault("witnesses" if result.stdout == b"accept" else "rejection_witnesses", [])
                if len(witnesses) < 3 and record["id"] not in witnesses:
                    witnesses.append(record["id"])
                entry["status"] = "rule_action_observed"
            reductions = set(re.findall(rb"Reducing stack by rule (\d+) \(line (\d+)\)", trace))
            if result.stdout != b"accept":
                for number, line in reductions:
                    entry = index[int(number)]
                    witnesses = entry.setdefault("rejection_witnesses", [])
                    entry["line"] = int(line)
                    if len(witnesses) < 3 and record["id"] not in witnesses:
                        witnesses.append(record["id"])
                rejected += 1
                continue
            accepted += 1
            for number, line in reductions:
                entry = index[int(number)]
                entry["line"] = int(line)
                if len(entry["witnesses"]) < 3 and record["id"] not in entry["witnesses"]:
                    entry["witnesses"].append(record["id"])
            if seen % 100 == 0:
                print(json.dumps({"seen": seen, "covered": sum(bool(rule["witnesses"]) for rule in rules)}), flush=True)
                save(output, rules, seen, accepted, rejected, crashes)
    dispositions(rules)
    save(output, rules, seen, accepted, rejected, crashes)
    # TOKEN_* string scanning starts in INITIAL. CLI file scanning alone exercises
    # the separate SHEBANG state; lint is recorded as a distinct observation.
    for name in ("shebang", "blocks"):
        source = ROOT / ("tests/fixtures/" + name + ".php")
        result = subprocess.run([str(php), "-n", "-l", str(source)], env=env, capture_output=True, timeout=30)
        if result.returncode:
            raise RuntimeError("coverage lint witness failed: " + name)
        for number in set(re.findall(rb"LEX_RULE:(\d+)", result.stderr)):
            entry = scanner_index[int(number)]
            witnesses = entry.setdefault("lint_witnesses", [])
            identifier = str(source.relative_to(ROOT))
            if len(witnesses) < 3 and identifier not in witnesses:
                witnesses.append(identifier)
            entry["status"] = "rule_action_observed"
    prologue = scanner_index[1396]
    prologue.update(status="shared_rule_prologue", witnesses=["tests/fixtures/blocks.php"],
                    reason="re2c <!*> action computes yyleng before every scanner rule; observed action markers witness this mandatory prologue.")
    scanner_path.write_text(json.dumps(scanner, indent=2) + "\n")
    print(json.dumps({"seen": seen, "accepted": accepted, "rejected": rejected,
                      "covered": sum(bool(rule["witnesses"]) for rule in rules),
                      "uncovered": [rule["rule"] for rule in rules if not rule["witnesses"]], "crashes": crashes}))


def save(path, rules, seen, accepted, rejected, crashes):
    path.write_text(json.dumps({"authority": "vendor/php-src/Zend/zend_language_parser.y",
                               "method": "Bison debug reductions during native file-mode parser-only oracle on accepted source",
                               "last_run": {"seen": seen, "accepted": accepted, "rejected": rejected, "crashes": crashes},
                               "productions": rules}, indent=2) + "\n")


def dispositions(rules):
    reasons = {
        0: ("synthetic_accept", "Bison augmented start rule accepts successful end-of-input without a debug reduction; every accepted trace witnesses this boundary."),
        71: ("lexically_unreachable_in_valid_source", "scanner.l:1564-1576 returns T_ENUM only before whitespace/comments and another identifier character; extends/implements return T_STRING. In identifier/semi_reserved or trait-alias positions valid continuations require punctuation, so enum there lexes as T_STRING. Enum declarations have separately witnessed productions."),
        149: ("parser_static_rejection", "inner_statement __halt_compiler triggers CompileError and YYERROR in parser.y:503-505; outermost top_statement is separately witnessed."),
        200: ("parser_static_rejection", "zend_add_anonymous_class_modifier in zend_compile.c:1003-1020 rejects abstract, final, and repeated readonly. Readonly is the sole permitted modifier, so this repeated-modifier production cannot succeed."),
    }
    for rule in rules:
        if rule["rule"] in reasons:
            rule["status"], rule["reason"] = reasons[rule["rule"]]
        else:
            rule["status"] = "accepted_source_witness" if rule["witnesses"] else "missing_witness"


if __name__ == "__main__":
    main()
