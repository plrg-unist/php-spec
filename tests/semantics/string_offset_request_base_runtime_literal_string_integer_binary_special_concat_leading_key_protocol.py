#!/usr/bin/env python3
"""Quiet integer conversion consumes original certified literal string values."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_runtime_literal_string_integer_binary_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_literal_string_cast_special_concat_leading_key_protocol as prior

runner, integers = prior.runner, prior.integers
ZERO, ONE = prior.prior.ZERO, prior.prior.ONE
THREE = ('ADD', ONE, ('ADD', ONE, ONE, 2), 3)


def selected(text, number):
    return ('TERNARY', prior.TRUTH, ('STRING', text, number), True)


TREES = (
    ('SHIFTRIGHT', ('BITOR', selected('3.0', '3'), ZERO, 3), selected('1e0', '1'), 1),
    ('BITNOT', ('BITXOR', ('POSITIVE', ('BITAND', selected('-1', '$(-1)'), ZERO, 0), 0), ZERO, 0), -1),
    ('SHIFTLEFT', ('TERNARY', ZERO, ('STRING', '-0.0', '0'), False), ONE, 0),
    ('BITNOT', ('BITOR', ('POSITIVE', ('MODULO', selected('9223372036854775808', '9223372036854775807'), selected('2', '2'), 1), 1), THREE, 3), -4),
)
base_value = prior.value


def value(checks, tag, tree):
    result, number = base_value(checks, tag, tree)
    if result.startswith('PSTRING_CARRIER INTERNED_STRING '):
        payload = result.removeprefix('PSTRING_CARRIER INTERNED_STRING ')
        checks += ['$string_long(' + payload + ') = STRINT ' + number + ' eps',
                   '$long_range(' + number + ')',
                   '$string_read_runtime_integer_quiet(' + result + ')']
    return result, number


module = prior
while module is not integers:
    module.value = value
    module = module.prior
integers.value, integers.TREES = value, TREES
conditions = prior.conditions


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
    report['scope'] = 'Four emitted MOD/BW/shift trees consume certified nonNUL literal-INTERNED STRING values through exact intrinsic STRINT i eps, signed64 bounds and existing ordered full-state integer_coerce/original typed binary_apply. Integral decimal/exponent strings, negative zero and quiet positive-boundary saturation retain actual operands. Full ternaries select both arms; selected STRING BYTE stays eps and exact PINT parents preserve REQUEST keys1/-1/0/-4, Warning/Throwable/bounds, ownership, cleanup and budget rejoining. Leading/precision-loss/nonfinite notice vectors, raw PSTRING/REQUEST/NUL, both-STRING bytewise dispatch and STRING BITNOT remain outside. No numeric/compiler/formatter/owner body or held-boundary change; saved native originals reused once and fixture source0/native0.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
