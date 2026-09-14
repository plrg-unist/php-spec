#!/usr/bin/env python3
"""Named-function static cells and shared call ownership across initial main-script statics."""
from pathlib import Path
import json
import function_scope as scope
ROOT = Path(__file__).resolve().parent
SELECTION = {
    'function_statics': ['static-reentry-inner-wins', 'static-binding-releases-prior-reference',
                         'static-bare-null-returned-alias', 'static-stored-array-null-distinct-cells',
                         'static-autoglobal-hidden-local-cv', 'static-globals-hidden-local-cv',
                         'static-saved-suppression-typed-initializer-error', 'static-bare-cv-current-parameter'],
    'dynamic_call': ['dynamic-reference-return', 'dynamic-successful-multiline-callee-type'],
    'named': ['named-hole-deferred-warning-before-type'],
    'call_unpack': ['unpack-held-owner-after-later-call'],
}
CASES = {}
for suite, ids in SELECTION.items():
    cases = json.loads((ROOT / (suite + '_cases.json')).read_text())
    for name in ids:
        CASES[name] = cases[name].encode()
if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'main-statics-regression', Path(__file__)) else 1)
