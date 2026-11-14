#!/usr/bin/env python3
"""Exact literal string carriers supply typed VALUE to quiet emitted parents."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_runtime_literal_string_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_float_power_special_concat_leading_key_protocol as prior

runner, integers = prior.runner, prior.integers
ZERO, ONE = prior.prior.ZERO, prior.prior.ONE
TREES = (
    ('POSITIVE', ('ADD', ('STRING', '1', '1'), ZERO, 1), 1),
    ('BITNOT', ('SUBTRACT', ('STRING', '0', '0'), ZERO, 0), -1),
    ('POSITIVE', ('IDENTICAL', ('STRING', '01', '1'), ONE, False), 0),
    ('BITNOT', ('MULTIPLY', ('STRING', '3', '3'), ONE, 3), -4),
)
base_value = prior.value


def value(checks, tag, tree):
    if tree[0] != 'STRING':
        return base_value(checks, tag, tree)
    origin, expression = 'porigin_' + tag, 'expression_' + tag
    payload = '$ptascii(' + json.dumps(tree[1]) + ')'
    raw = 'PSTRING (' + payload + ')'
    result = 'PSTRING_CARRIER INTERNED_STRING (' + payload + ')'
    checks += ['$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')',
               expression + ' = NScalarString (BYTES text_' + tag + ') metadata_' + tag,
               '$base64(text_' + tag + ') = ' + payload,
               '$startup_bytes(' + payload + ')', '$c_string(' + payload + ') = ' + payload,
               '$compiled_precision(S, (' + origin + ')) = (14)',
               '$compiled_read(S, ' + origin + ') = (' + raw + ')',
               '$compiled_identity_value(S, ' + origin + ') = (' + raw + ')',
               '$compiled_string_value(S, ' + origin + ', ' + raw + ') = ' + result,
               '$string_carrier_valid(S, ' + result + ')',
               '$string_read_runtime_value(S, ' + origin + ') = (' + result + ')',
               '$string_read_runtime_bytes(S, ' + origin + ') = (' + payload + ')']
    return result, tree[2]


module = prior
while module is not integers:
    module.value = value
    module = module.prior
integers.value, integers.TREES = value, TREES


def conditions(program, path, index):
    checks, derived = prior.conditions(program, path, index)
    at = checks.index('$string_read_plan(S_found) = eps')
    checks[at] = '$string_read_plan(S_found) = $string_read_plan(S_found[.COMPLETION = NORMAL])'
    return checks, derived


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
    report['scope'] = 'Four emitted ADD/SUBTRACT/MULTIPLY and strict-identity trees consume only exact actual NScalarString bytes, captured precision and raw PSTRING compiler reads/identity mapped to validated nonNUL INTERNED carriers. Genuine deferred FLOAT NOT supplies the other quiet integer operand; original typed numeric coercions and full-state operations preserve exact PINT/PBOOL results and REQUEST keys1/-1/0/-4. Captured14/live17 precision, returning Warning, supplied Throwable, bounds, owners, cleanup and budget rejoining retain existing laws. Raw PSTRING or REQUEST forgeries, warningful/nonnumeric arithmetic, STRING-result BYTE, FLOAT BYTE, casts, formatter/compiler/owner bodies and exact held boundaries gain no new authority. Saved native originals reused once; fixture source0/native0.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
