#!/usr/bin/env python3
"""Existing dynamic/named/unpacked calls, cached defaults and returned owners across112."""
from pathlib import Path
import json
import function_scope as scope
ROOT = Path(__file__).resolve().parent
SELECTION = {
    'dynamic_call': ['dynamic-callee-before-arguments', 'dynamic-reference-return',
                     'dynamic-hole-float-cache-fresh-reference', 'dynamic-saved-suppression-hole-type-error',
                     'dynamic-successful-multiline-callee-type', 'dynamic-reference-result-unpack'],
    'named': ['named-hole-deferred-warning-before-type', 'named-hole-uncoerced-string-reference-cache',
              'named-deferred-cv-typed-return-line'],
    'call_unpack': ['unpack-reference-assignment-result', 'unpack-held-owner-after-later-call',
                    'unpack-nested-call-callee-type-line'],
}
CASES = {}
for suite, ids in SELECTION.items():
    cases = json.loads((ROOT / (suite + '_cases.json')).read_text())
    for name in ids:
        CASES[name] = cases[name].encode()
if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'function-statics-regression', Path(__file__)) else 1)
