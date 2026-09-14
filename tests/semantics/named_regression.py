#!/usr/bin/env python3
"""Adjacent positional call behavior after named binding and hole preflight."""
from pathlib import Path
import json
import function_scope as scope
ROOT = Path(__file__).resolve().parent
SELECTION = {
    'typed_function_cases.json': ['weak-reference-alias'],
    'typed_runtime_cases.json': ['typed-default-ref-fresh-cache', 'first-type-before-missing'],
    'reference_return_cases.json': ['ref-return-forward-reference', 'unused-typed-refreturn-global-coercion'],
    'call_reference_cases.json': ['acquire-dim-existing-alias', 'acquire-argument-line-nested'],
    'suppression_cases.json': ['silence-nested-call-error', 'silence-folded-append-once'],
    'variadic_cases.json': ['variadic-fixed-tail-shared-coercion', 'variadic-tail-singleton-after-cleanup', 'optional-prefix-empty-tail'],
}
CASES = {name: json.loads((ROOT / filename).read_text())[name].encode()
         for filename, names in SELECTION.items() for name in names}
if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'named-regression', Path(__file__)) else 1)
