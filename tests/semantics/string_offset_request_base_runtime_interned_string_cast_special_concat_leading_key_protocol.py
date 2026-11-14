#!/usr/bin/env python3
"""Immutable string casts preserve original typed inputs and complete state."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_runtime_interned_string_cast_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_literal_string_bytes_special_concat_leading_key_protocol as prior

runner, integers = prior.runner, prior.integers
TRUTH = ('NOT', ('FLOAT', 0), True)
FALSE = ('NOT', ('FLOAT', 9218868437227405312), False)
ONE = ('POSITIVE', TRUTH, 1)
THREE = ('ADD', ONE, ('ADD', ONE, ONE, 2), 3)


def interned(text):
    return 'PSTRING_CARRIER INTERNED_STRING ($ptascii(' + json.dumps(text) + '))'


TREES = (
    ('CAST', 'CASTSTRING', TRUTH, interned('1')),
    ('BITNOT', ('CAST', 'CASTINT', ('CAST', 'CASTSTRING', FALSE, interned('')), 'PINT 0'), -1),
    ('CAST', 'CASTINT', ('CAST', 'CASTSTRING', ('NULL_TERNARY',), interned('')), 'PINT 0'),
    ('BITNOT', ('CAST', 'CASTINT', ('CAST', 'CASTSTRING', ('CAST', 'CASTSTRING', ('POSITIVE', THREE, 3), interned('3')), interned('3')), 'PINT 3'), -4),
)
integers.TREES = TREES
value, conditions = prior.value, prior.conditions


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    watched = {Path(module.__file__).resolve() for module in tuple(sys.modules.values())
               if getattr(module, '__file__', None)
               and Path(module.__file__).resolve().parent == Path(__file__).resolve().parent}
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.cases, runner.OUTPUTS, runner.conditions = cases, tuple(cases.OUTPUTS.values()), conditions
    passed = runner.main()
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = 'Four emitted CASTSTRING trees consume exact NULL/BOOL/digit-PINT0..9 and certified nonNUL INTERNED STRING inputs through existing NORMAL/source/CODEfalse/read-eps/positive-line/equal captured precision and exact whole-state cast_apply. Quiet immutable empty/one/digit results and identity casts retain their actual INTERNED headers and bytes without allocating a REQUEST string. BOOL false and selected NULL remain distinct typed inputs before empty strings cast explicitly to integer zero; computed3 and nested STRING identity preserve the bounds key. Existing REQUEST keys1/-1/0/-4, Warning/Throwable/bounds, ownership, cleanup and budget rejoining remain. Wider integer/FLOAT/REQUEST/raw/NUL inputs, other casts, formatter/compiler/owner bodies and exact holds gain no authority; native originals reused once and fixture source0/native0.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
