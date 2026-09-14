#!/usr/bin/env python3
"""Adjacent named and positional binding, typed aliases, caches and suppression."""
from pathlib import Path
import json
import function_scope as scope
ROOT = Path(__file__).resolve().parent
SELECTION = {
    'named_cases.json': ['named-known-reference-reorder', 'named-deferred-reference-reorder',
        'named-hole-deferred-warning-before-type', 'named-contiguous-type-before-deferred-warning',
        'named-hole-uncoerced-string-reference-cache', 'named-fixed-tail-shared-late-error',
        'named-only-extra-required-prefix', 'named-deferred-cv-typed-return-line'],
    'variadic_cases.json': ['variadic-fixed-tail-shared-coercion', 'variadic-tail-singleton-after-cleanup'],
    'reference_return_cases.json': ['ref-return-forward-reference'],
    'suppression_cases.json': ['silence-nested-call-error'],
}
CASES = {name: json.loads((ROOT / filename).read_text())[name].encode()
         for filename, names in SELECTION.items() for name in names}
if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'call-unpack-regression', Path(__file__)) else 1)
