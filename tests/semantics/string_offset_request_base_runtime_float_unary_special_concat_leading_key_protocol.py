#!/usr/bin/env python3
"""Quiet FLOAT signs retain exact VALUE bits and no BYTE receipt."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_runtime_float_unary_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_float_arithmetic_special_concat_leading_key_protocol as prior

runner, integers = prior.runner, prior.integers
ONE, INTEGER_ZERO = prior.ONE, prior.INTEGER_ZERO
FLOAT_NEGATIVE_ZERO = ('FLOAT', 9223372036854775808)
FLOAT_INFINITY = ('FLOAT', 9218868437227405312)
FLOAT_NEGATIVE_INFINITY = ('FLOAT', 18442240474082181120)
TREES = (
    ('NOT', ('FLOAT_UNARY', 'NEGATIVE', ('FLOAT_BINARY', 'ADD', INTEGER_ZERO, FLOAT_NEGATIVE_ZERO, 0), 9223372036854775808), True),
    ('NEGATIVE', ('IDENTICAL', ('FLOAT_UNARY', 'POSITIVE', ('FLOAT_BINARY', 'SUBTRACT', ONE, prior.FLOAT_ONE, 0), 0), FLOAT_NEGATIVE_ZERO, True), -1),
    ('POSITIVE', ('IDENTICAL', ('FLOAT_UNARY', 'POSITIVE', ('FLOAT_BINARY', 'MULTIPLY', ONE, prior.FLOAT_ONE_HALF, 4609434218613702656), 4609434218613702656), ONE, False), 0),
    ('BITNOT', ('ADD', ('IDENTICAL', ('FLOAT_UNARY', 'POSITIVE', ('FLOAT_UNARY', 'NEGATIVE', ('FLOAT_BINARY', 'ADD', FLOAT_INFINITY, INTEGER_ZERO, 9218868437227405312), 18442240474082181120), 18442240474082181120), FLOAT_NEGATIVE_INFINITY, True),
               ('ADD', ONE, ONE, 2), 3), -4),
)
base_value = prior.value


def value(checks, tag, tree):
    kind = tree[0]
    if kind != 'FLOAT_UNARY':
        return base_value(checks, tag, tree)
    origin, expression = 'porigin_' + tag, 'expression_' + tag
    checks += ['$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')']
    integers.emitted(checks, tag)
    operator = tree[1]
    checks += ['$pfshape(' + expression + ') = PFUNARY ' + operator + ' ' + expression + '_0',
               '$origin_child((' + origin + '), [PCFIELD 0]) = (porigin_' + tag + '_0)']
    child = value(checks, tag + '_0', tree[2])[0]
    result = 'PFLOAT ' + str(tree[-1])
    truth = str(tree[-1] not in (0, 9223372036854775808)).lower()
    checks += ['S.COMPLETION = NORMAL',
               '$coerce_number(' + child + ') = COERCED (' + prior.numeric(child) + ') false',
               '$unary_apply(S, ' + operator + ', ' + child + ', 5) = S[.RESULT = KNOWN (' + result + ')]',
               '$number_bool(' + prior.numeric(result) + ') = (' + truth + ', false)',
               '$string_read_runtime_bytes(S, ' + origin + ') = eps']
    checks += ['$string_read_runtime_value(S, ' + origin + ') = (' + result + ')']
    return result, None


prior.value, integers.value, integers.TREES = value, value, TREES
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
    report['scope'] = 'Four final actual emitted POSITIVE/NEGATIVE FLOAT-result trees retain exact NORMAL/source/CODEfalse/read-eps/equal captured precision, recursive typed operands, quiet coercions, unchanged full-state unary_apply and nonNaN result truth. Signed zero, fractional1.5, negative infinity and nested signs preserve exact VALUE bits with BYTE eps. Existing typed NOT/identity and integer ancestors retain real REQUEST keys1/-1/0/-4, captured14/live17 precision, Warning owners, same supplied Throwable, fixed bounds/cleanup and inherited guarded-frontier budget rejoining. Earlier deep MIN and three-identity key timeouts remain separate zero-agreement cost limits; their source is not credited by these fixtures. No primitive/compiler/schema/API/kernel/owner expansion, runtime FLOAT BYTE or NaN truth; saved natives retain six-original-once provenance and fixture source0/native0.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
