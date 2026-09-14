#!/usr/bin/env python3
"""Explicit captures, source returns and frame/static behavior shared with arrows."""
from pathlib import Path
import json
import function_scope as scope
ROOT = Path(__file__).resolve().parent
SELECTION = {
    'closures': ['closure-capture-value-reset-and-reference',
                 'closure-captured-array-nested-reference',
                 'closure-instance-static-reentry', 'closure-self-capture-cycle',
                 'closure-multiline-capture-warning', 'closure-multiline-call-type',
                 'closure-object-callable-class-types', 'closure-reference-return-signature',
                 'closure-named-default-signature', 'closure-unpack-reference-signature'],
    'named': ['named-hole-deferred-warning-before-type'],
    'function_statics': ['static-saved-suppression-typed-initializer-error'],
}
CASES = {}
for suite, ids in SELECTION.items():
    cases = json.loads((ROOT / (suite + '_cases.json')).read_text())
    for name in ids:
        CASES[name] = cases[name].encode()
# This accepted explicit-closure source exposes the shared suppression owner guard.
CASES['closure-body-suppressed-reference-call'] = b'<?php function &r(){return 3;}$f=function(){return @r();};$f();'
if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'arrows-regression', Path(__file__)) else 1)
