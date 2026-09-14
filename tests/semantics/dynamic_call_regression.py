#!/usr/bin/env python3
"""Existing call metadata, name/default timing and return owners across110."""
from pathlib import Path
import json
import function_scope as scope
ROOT = Path(__file__).resolve().parent
SELECTION = {
    'reference_return': ['ref-return-forward-reference', 'ref-return-forward-value',
                         'ref-return-typed-alias-coercion', 'ref-return-nested-call-line'],
    'named': ['named-hole-deferred-warning-before-type', 'named-contiguous-type-before-deferred-warning',
              'named-hole-uncoerced-string-reference-cache', 'named-deferred-cv-typed-return-line'],
    'call_unpack': ['unpack-reference-assignment-result', 'unpack-value-list-call',
                    'unpack-held-owner-after-later-call', 'unpack-nested-call-callee-type-line'],
}
CASES = {}
for suite, ids in SELECTION.items():
    cases = json.loads((ROOT / (suite + '_cases.json')).read_text())
    for name in ids:
        CASES[name] = cases[name].encode()
if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'dynamic-call-regression', Path(__file__)) else 1)
