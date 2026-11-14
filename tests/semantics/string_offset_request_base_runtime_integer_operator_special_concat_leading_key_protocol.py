#!/usr/bin/env python3
"""Actual emitted integer operators retain quiet values and Warning histories."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_runtime_integer_operator_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_unary_integer_special_concat_leading_key_protocol as prior

runner = prior.runner
ZERO = ('NOT', ('FLOAT', 0), True)
INF = ('NOT', ('FLOAT', 9218868437227405312), False)
TREES = (
    ('ADD', ZERO, ('POSITIVE', INF, 0), 1),
    ('SUBTRACT', ('POSITIVE', INF, 0), ZERO, -1),
    ('MULTIPLY', ('POSITIVE', INF, 0), ('NEGATIVE', ZERO, -1), 0),
    ('BITNOT', ('ADD', ZERO, ('ADD', ZERO, ZERO, 2), 3), -4),
)


def integer(value):
    return '$(' + str(value) + ')' if value < 0 else str(value)


def emitted(checks, tag):
    origin, path = 'porigin_' + tag, 'pcpath_' + tag
    checks += [origin + ' = PORIGIN n_runtime_unit ' + path,
               '$code_at(S.CODE, n_runtime_unit) = (pcode_runtime)',
               '$code_expression(pcode_runtime.EXPRESSIONS, ' + path + ') = ((5, false))',
               '$compiled_read(S, ' + origin + ') = eps',
               '$compiled_precision(S, (' + origin + ')) = (14)',
               '$compiled_special_concat_bytes(S, ' + origin + ') = eps']


def value(checks, tag, tree):
    kind = tree[0]
    origin, expression = 'porigin_' + tag, 'expression_' + tag
    checks += ['$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')']
    if kind == 'FLOAT':
        bits = str(tree[1])
        result = 'PFLOAT ' + bits
        checks += ['$compiled_read(S, ' + origin + ') = (' + result + ')',
                   '$compiled_identity_value(S, ' + origin + ') = (' + result + ')',
                   '$compiled_precision(S, (' + origin + ')) = (14)',
                   '$string_read_runtime_value(S, ' + origin + ') = (' + result + ')']
        if tree[1] == 0:
            checks += [expression + ' = NScalarFloat (FLOAT text_' + tag + ') metadata_' + tag,
                       '$hex_bits(text_' + tag + ', 0) = 0']
        else:
            assert tree[1] == 9218868437227405312
            checks += [expression + ' = NExprConstFetch name_' + tag + ' metadata_' + tag,
                       '$ptast(name_' + tag + ') = PTNAME PTPLAIN ($ptascii("INF"))']
        return result, None
    emitted(checks, tag)
    binary = kind in ('ADD', 'SUBTRACT', 'MULTIPLY')
    children = tree[1:3] if binary else tree[1:2]
    shape = ('PFBINARY ' + kind if binary else
             'PFUNARY ' + kind if kind in ('POSITIVE', 'NEGATIVE') else
             'PFNOT' if kind == 'NOT' else 'PFBITNOT')
    checks += ['$pfshape(' + expression + ') = ' + shape + ' ' + ' '.join(expression + '_' + str(i) for i in range(len(children)))]
    values = []
    for index, child in enumerate(children):
        child_tag = tag + '_' + str(index)
        checks += ['$origin_child((' + origin + '), [PCFIELD ' + str(index) + ']) = (porigin_' + child_tag + ')']
        values.append(value(checks, child_tag, child))
    if kind == 'NOT':
        result = 'PBOOL ' + str(tree[-1]).lower()
        number = '1' if tree[-1] else '0'
        truth = str(not tree[-1]).lower()
        assert tree[1][0] == 'FLOAT'
        checks += ['$number_bool(NFLOAT ' + str(tree[1][1]) + ') = (' + truth + ', false)',
                   '$truth_value(S, ' + values[0][0] + ', 5) = S[.RESULT = KNOWN (PBOOL ' + truth + ')]']
    else:
        number = integer(tree[-1])
        result = 'PINT ' + number
        checks += ['$long_range(' + number + ')']
        if binary:
            for child, numeric in values:
                checks += ['$coerce_number(' + child + ') = COERCED (NINT ' + numeric + ') false',
                           '$long_range(' + numeric + ')']
            checks += ['$number_binary(' + kind + ', NINT ' + values[0][1] + ', NINT ' + values[1][1] + ') = NUM (NINT ' + number + ')',
                       '$binary_apply(S, ' + kind + ', ' + values[0][0] + ', ' + values[1][0] + ', 5) = S[.RESULT = KNOWN (' + result + ')]']
        elif kind == 'BITNOT':
            assert values[0][0].startswith('PINT ')
            checks += ['$long_not(' + values[0][1] + ') = ' + number,
                       '$bitnot_value(S, ' + values[0][0] + ', 5) = S[.RESULT = KNOWN (' + result + ')]']
        else:
            checks += ['$coerce_number(' + values[0][0] + ') = COERCED (NINT ' + values[0][1] + ') false',
                       '$unary_apply(S, ' + kind + ', ' + values[0][0] + ', 5) = S[.RESULT = KNOWN (' + result + ')]']
    checks += ['$string_read_runtime_value(S, ' + origin + ') = (' + result + ')',
               '$string_read_runtime_bytes(S, ' + origin + ') = ($echo_value(' + result + '))']
    return result, number


def authority(index):
    checks = ['$origin_child((porigin_key), [PCFIELD 0]) = (porigin_runtime_concat)',
              '$origin_node(S.SOURCES, porigin_runtime_concat) = (expression_1)',
              'expression_1 = NExprBinaryOpConcat expression_runtime_left expression_runtime_right metadata_runtime_concat',
              '$origin_child((porigin_runtime_concat), [PCFIELD 0]) = (porigin_runtime_left)',
              '$origin_child((porigin_runtime_concat), [PCFIELD 1]) = (porigin_runtime_right)',
              '$origin_node(S.SOURCES, porigin_runtime_left) = (expression_runtime_left)',
              '$origin_node(S.SOURCES, porigin_runtime_right) = (expression_runtime_right)',
              'porigin_operator = porigin_runtime_left',
              r'S.PRECISIONINI = $ptascii("17") /\ $precision_value(S) = 17']
    for tag in ('key', 'runtime_concat'):
        emitted(checks, tag)
    value(checks, 'operator', TREES[index])
    checks += ['$compiled_read(S, porigin_runtime_right) = (' + ('PNULL' if index == 0 else 'PBOOL false') + ')',
               '$compiled_precision(S, (porigin_runtime_right)) = (14)',
               '$string_read_runtime_bytes(S, porigin_runtime_right) = (eps)',
               '$string_read_runtime_bytes(S, porigin_key) = ($ptascii(' + json.dumps(prior.prior.KEYS[index]) + '))']
    return checks


def conditions(program, path, index):
    checks, derived = prior.conditions(program, path, index)
    old = prior.authority(index)
    at = checks.index(old[0])
    assert checks[at:at + len(old)] == old
    checks[at:at + len(old)] = authority(index)
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
    report['scope'] = 'Four source-reached emitted ADD/SUB/MUL and PINT-only BITNOT trees retain actual own/child source, false CODE/read-eps/equal captured precision, typed BOOL/PINT children, quiet fitting NINT conversions and exact fitting PINT whole-state results/decimal BYTE. BITNOT uses pure bitnot_value with an independent long_not result; compiled PINT leaves and runtime FLOAT formatting gain no authority. Real REQUEST keys preserve returning/negative/supplied-throw/bounds owners, cleanup and budgets. Native originals are reused once; fixture source0.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
