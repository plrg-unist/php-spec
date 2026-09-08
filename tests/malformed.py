#!/usr/bin/env python3
"""Cross-check strict value checking with actual typed fixture elaboration."""
import base64
import copy
import json
from validate import ROOT, Worker, require


def main():
    frontend = Worker([str(ROOT / ".tools/php/bin/php"), "-n", str(ROOT / "frontend/worker.php")])
    adapter = Worker([str(ROOT / "_build/default/adapter/main.exe"), str(ROOT)])
    cases = []
    try:
        ast = require(frontend.call(op="parse", source=base64.b64encode(b"<?php echo 1;").decode()), "parse")["ast"]
        checked = require(adapter.call(op="elaborate", ast=ast, fixture=True), "positive elaboration")
        expression = checked["fixture"]
        formal = {
            "unknown constructor": expression.replace("NStmtEcho", "NUnknown"),
            "wrong constructor category": "(PROGRAM ([(NScalarInt ((INTEGER (1))) ([]))]))",
            "wrong arity": "(PROGRAM ([]) ([]))",
            "missing arity": "PROGRAM",
            "wrong scalar payload": expression.replace("INTEGER (1)", 'INTEGER ("one")'),
            "wrong list payload": "(PROGRAM (true))",
            "wrong list element": "(PROGRAM ([true]))",
            "absent is not a list": "(PROGRAM ([(NStmtEcho (ABSENT) ([]))]))",
            "list is not an option": "(PROGRAM ([(NStmtReturn ((SEQUENCE ([]))) ([]))]))",
            "wrong metadata payload": expression.replace("MstartLine (1)", 'MstartLine ("one")'),
            "wrong metadata constructor": expression.replace("MstartLine", "Munknown"),
        }
        for name, fixture in formal.items():
            response = adapter.call(op="elaborate_fixture", fixture=fixture)
            cases.append({"name": "formal: " + name, "passed": response.get("ok") is False, "result": response})
        mutations = {}
        value = copy.deepcopy(ast); value["program"][0]["node"] = "Unknown"; mutations["unknown constructor"] = value
        value = copy.deepcopy(ast); value["program"][0]["fields"].append(None); mutations["wrong arity"] = value
        value = copy.deepcopy(ast); value["program"][0]["fields"][0] = None; mutations["absent is not a list"] = value
        value = copy.deepcopy(ast); value["program"][0]["fields"][0] = [True]; mutations["wrong list element"] = value
        value = copy.deepcopy(ast); value["program"] = [value["program"][0]["fields"][0][0]]; mutations["wrong constructor category"] = value
        value = copy.deepcopy(ast); value["program"][0]["fields"][0][0]["fields"][0] = {"bytes": "MQ=="}; mutations["wrong scalar payload"] = value
        value = copy.deepcopy(ast); value["program"][0]["meta"]["startLine"] = {"bytes": "MQ=="}; mutations["wrong metadata payload"] = value
        value = copy.deepcopy(ast); value["program"][0]["meta"]["unknown"] = True; mutations["wrong metadata constructor"] = value
        value = copy.deepcopy(ast); value["program"][0]["fields"][0][0]["fields"][0] = {"int": "9223372036854775808"}; mutations["integer overflow"] = value
        value = copy.deepcopy(ast); value["program"][0]["meta"]["rawValue"] = {"bytes": "!!!!"}; mutations["malformed base64"] = value
        value = copy.deepcopy(ast); value["program"][0]["extra"] = True; mutations["unknown transport key"] = value
        for name, value in mutations.items():
            response = adapter.call(op="check", ast=value)
            cases.append({"name": "transport: " + name, "passed": response.get("ok") is False, "result": response})
        # Change the actual checked value through transport, then reconstruct fresh nodes.
        value = copy.deepcopy(ast)
        value["program"][0]["fields"][0][0]["fields"][0] = {"int": "2"}
        changed = require(adapter.call(op="check", ast=value), "mutated check")
        printed = require(frontend.call(op="print", ast=changed["ast"]), "mutated print")
        cases.append({"name": "checked payload affects fresh output", "passed": b"echo 2;" in base64.b64decode(printed["source"])})
        cases.append({"name": "positive typed elaboration", "passed": checked["ast"] == ast})
    finally:
        frontend.close()
        adapter.close()
    result = {"total": len(cases), "passed": sum(case["passed"] for case in cases), "cases": cases}
    (ROOT / "coverage/malformed.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"total": result["total"], "passed": result["passed"], "failures": [case for case in cases if not case["passed"]]}))
    return int(result["total"] != result["passed"])


if __name__ == "__main__":
    raise SystemExit(main())
