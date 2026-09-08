#!/usr/bin/env python3
"""Reject malformed flat-wire structure independently of PHP syntax checking."""
import json
import sys
from validate import ROOT, Worker
import wire


def main():
    malformed = {
        "empty table": {"wire": wire.TAG, "root": 0, "values": []},
        "boolean root": {"wire": wire.TAG, "root": False, "values": [[0, 1]]},
        "boolean row kind": {"wire": wire.TAG, "root": 0, "values": [[False, 1]]},
        "self cycle": {"wire": wire.TAG, "root": 0, "values": [[1, [0]]]},
        "back reference": {"wire": wire.TAG, "root": 0, "values": [[1, [1]], [1, [0]]]},
        "out of range": {"wire": wire.TAG, "root": 0, "values": [[1, [1]]]},
        "duplicate key": {"wire": wire.TAG, "root": 0, "values": [[2, [["x", 1], ["x", 2]]], [0, 1], [0, 2]]},
        "numeric object key": {"wire": wire.TAG, "root": 0, "values": [[2, [[1, 1]]], [0, 1]]},
        "container scalar": {"wire": wire.TAG, "root": 0, "values": [[0, []]]},
        "unknown kind": {"wire": wire.TAG, "root": 0, "values": [[3, 1]]},
        "row arity": {"wire": wire.TAG, "root": 0, "values": [[0, 1, 2]]},
    }
    frontend = Worker([str(ROOT / ".tools/php/bin/php"), "-n", str(ROOT / "frontend/worker.php")])
    adapter = Worker([str(ROOT / "_build/default/adapter/main.exe"), str(ROOT)])
    results = []
    try:
        for name, value in malformed.items():
            try:
                wire.inflate(value)
                rejected = False
            except (ValueError, TypeError, IndexError):
                rejected = True
            results.append({"case": name, "endpoint": "Python", "passed": rejected})
            for endpoint, worker in (("PHP", frontend), ("OCaml", adapter)):
                response = worker.call(**value)
                results.append({"case": name, "endpoint": endpoint, "passed": response.get("ok") is False, "response": response})
    finally:
        frontend.close()
        adapter.close()
    report = {"total": len(results), "passed": sum(result["passed"] for result in results), "cases": results}
    (ROOT / "coverage/wire-negative.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"total": report["total"], "passed": report["passed"], "failures": [result for result in results if not result["passed"]]}))
    return int(report["total"] != report["passed"])


if __name__ == "__main__":
    raise SystemExit(main())
