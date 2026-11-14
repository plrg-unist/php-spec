#!/usr/bin/env python3
"""Quiet primitive casts retain exact typed VALUE and existing key owners."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_runtime_scalar_cast_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_float_unary_special_concat_leading_key_protocol as prior

runner, integers = prior.runner, prior.integers
TREES = (
    ('CAST', 'CASTINT', ('NOT', ('FLOAT', 0), True), 'PINT 1'),
    ('CAST', 'CASTINT', ('FLOAT_UNARY', 'NEGATIVE', ('FLOAT_BINARY', 'ADD', prior.prior.FLOAT_ONE_HALF, prior.INTEGER_ZERO, 4609434218613702656), 13832806255468478464), 'PINT $(-1)'),
    ('POSITIVE', ('CAST', 'CASTBOOL', prior.INTEGER_ZERO, 'PBOOL false'), 0),
    ('BITNOT', ('ADD', ('IDENTICAL', ('CAST', 'CASTFLOAT', ('NOT', ('FLOAT', 0), True), 'PFLOAT 4607182418800017408'), prior.prior.FLOAT_ONE, True),
               ('ADD', prior.ONE, prior.ONE, 2), 3), -4),
)
base_value = prior.value


def value(checks, tag, tree):
    if tree[0] != 'CAST':
        return base_value(checks, tag, tree)
    origin, expression = 'porigin_' + tag, 'expression_' + tag
    checks += ['$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')']
    integers.emitted(checks, tag)
    operator, result = tree[1], tree[-1]
    checks += ['$pfshape(' + expression + ') = PFCAST ' + operator + ' ' + expression + '_0',
               '$origin_child((' + origin + '), [PCFIELD 0]) = (porigin_' + tag + '_0)']
    child = value(checks, tag + '_0', tree[2])[0]
    checks += ['S.COMPLETION = NORMAL',
               '$string_read_runtime_cast_quiet(' + operator + ', ' + child + ')',
               '$cast_apply(S, ' + operator + ', ' + child + ', 5) = S[.RESULT = KNOWN (' + result + ')]']
    if operator == 'CASTINT' and child.startswith('PFLOAT '):
        checks += ['$float_long(' + child.removeprefix('PFLOAT ') + ', false) = (' + result.removeprefix('PINT ') + ', eps)']
    if result.startswith('PFLOAT '):
        checks += ['$string_read_runtime_bytes(S, ' + origin + ') = eps']
        number = None
    else:
        checks += ['$string_read_runtime_bytes(S, ' + origin + ') = ($echo_value(' + result + '))']
        number = result.removeprefix('PINT ') if result.startswith('PINT ') else '1' if result == 'PBOOL true' else '0'
    checks += ['$string_read_runtime_value(S, ' + origin + ') = (' + result + ')']
    return result, number


prior.value, prior.prior.value, integers.value, integers.TREES = value, value, value, TREES
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
    report['scope'] = 'Four actual emitted primitive CASTINT/CASTBOOL/CASTFLOAT trees retain NORMAL/source/CODEfalse/read-eps/equal captured precision, recursively certified PFLOAT/PBOOL/PINT operands, explicit signed64 PINT bounds, quiet FLOAT-to-INT notices and exact full-state cast_apply. Fitting fractional -1.5 truncates quietly; strict identity preserves FLOAT1 versus PINT1. FLOAT VALUE retains BYTE eps while Boolean/integer ancestors retain real REQUEST keys1/-1/0/-4, captured14/live17 precision, Warning owners, supplied Throwable identity, fixed bounds/cleanup and inherited budget rejoining. No CASTSTRING, formatter, compiler, schema, API or owner expansion. Saved native originals are reused once; fixture source0/native0.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
