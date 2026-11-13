#!/usr/bin/env python3
"""Arithmetic NaN VALUE requires genuine numeric child VALUE, never NaN BYTE."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_nan_child_arithmetic_special_concat_leading_key_cases as cases
import string_offset_request_base_arithmetic_nan_special_concat_leading_key_protocol as prior

runner, arithmetic, unary, floats, nan = prior.runner, prior.arithmetic, prior.unary, prior.floats, prior.nan
BITS = 'n_nan_child_arithmetic_bits'
VALUE = ('PFLOAT ' + BITS, 'NFLOAT ' + BITS, None)


def producer(checks, tag, operation, left, right):
    expression, origin = 'expression_' + tag, 'porigin_' + tag
    shape = {'ADD': 'Plus', 'SUBTRACT': 'Minus', 'MULTIPLY': 'Mul', 'DIVIDE': 'Div'}[operation]
    checks += ['$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')',
               expression + ' = NExprBinaryOp' + shape + ' ' + expression + '_l ' + expression + '_r metadata_' + tag,
               '$pfshape(' + expression + ') = PFBINARY ' + operation + ' ' + expression + '_l ' + expression + '_r',
               '$parser_literal_at(' + expression + ', 14) = eps',
               '$compiled_read(S, ' + origin + ') = (' + VALUE[0] + ')',
               '$compiled_precision(S, (' + origin + ')) = (14)',
               '$binary_apply(S, ' + operation + ', ' + left[0] + ', ' + right[0] + ', 0) = S[.RESULT = KNOWN (' + VALUE[0] + ')]',
               '$(' + BITS + ' < 18446744073709551616)',
               '$fparts_nan($float_decode(' + BITS + '))',
               '$compiled_comparison_number(S, ' + origin + ') = (' + VALUE[1] + ')',
               '$compiled_special_concat_bytes(S, ' + origin + ') = eps']
    for field, suffix, (value, number, payload) in ((0, '_l', left), (1, '_r', right)):
        checks += ['$origin_child((' + origin + '), [PCFIELD ' + str(field) + ']) = (' + origin + suffix + ')',
                   '$origin_node(S.SOURCES, ' + origin + suffix + ') = (' + expression + suffix + ')',
                   '$compiled_read(S, ' + origin + suffix + ') = (' + value + ')',
                   '$compiled_precision(S, (' + origin + suffix + ')) = (14)',
                   '$compiled_comparison_number(S, ' + origin + suffix + ') = (' + number + ')',
                   '$coerce_number(' + value + ') = COERCED (' + number + ') false']
        if payload is None:
            checks += ['$compiled_special_concat_bytes(S, ' + origin + suffix + ') = eps',
                       '$(' + value[7:] + ' < 18446744073709551616)',
                       '$fparts_nan($float_decode(' + value[7:] + '))']
        else:
            checks += ['$compiled_order_number(' + value + ') = (' + number + ')',
                       '$compiled_special_concat_bytes(S, ' + origin + suffix + ') = ($ptascii(' + json.dumps(payload) + '))']


def authority(index):
    operation = ('ADD', 'DIVIDE', 'MULTIPLY', 'SUBTRACT')[index]
    left = floats.POSITIVE if index == 1 else prior.CONSTANT
    right = (('PINT 1', 'NINT 1', '1'), prior.CONSTANT, prior.CONSTANT, prior.VALUE)[index]
    checks = []
    if index == 3:
        checks += ['$number_binary(SUBTRACT, ' + floats.POSITIVE[1] + ', ' + floats.POSITIVE[1] + ') = NUM (' + prior.VALUE[1] + ')']
    checks += ['$number_binary(' + operation + ', ' + left[1] + ', ' + right[1] + ') = NUM (' + VALUE[1] + ')',
               '$origin_child((porigin_key), [PCFIELD 0, PCFIELD 0]) = (porigin_nan_child_arithmetic_root)',
               r'S.PRECISIONINI = $ptascii("17") /\ $precision_value(S) = 17']
    if index == 0:
        prior.comparison(checks, 'nan_child_arithmetic_root', 'NOTIDENTICAL', VALUE, prior.CONSTANT, 'PBOOL true', '1')
        tag = 'nan_child_arithmetic_root_l'
        nan.nan(checks, 'nan_child_arithmetic_root_r')
    elif index == 1:
        unary.unary(checks, 'nan_child_arithmetic_root', 'NEGATIVE', 'PINT 1', 'NINT 1', 'PINT $(-1)', '-1', '1')
        prior.comparison(checks, 'nan_child_arithmetic_root_child', 'SPACESHIP', VALUE,
                         ('PFLOAT 4609434218613702656', 'NFLOAT 4609434218613702656', '1.5'), 'PINT 1', '1')
        tag = 'nan_child_arithmetic_root_child_l'
        prior.prior.scalar(checks, 'nan_child_arithmetic_root_child_r', '4609434218613702656', '1.5')
    elif index == 2:
        arithmetic.binary(checks, 'nan_child_arithmetic_root', 'NExprBinaryOpPlus', 'ADD',
                          'PBOOL false', 'PBOOL false', 'PINT 0', 'NINT 0', 'NINT 0', 'NINT 0')
        prior.comparison(checks, 'nan_child_arithmetic_root_l', 'IDENTICAL', VALUE, prior.CONSTANT, 'PBOOL false', '')
        tag = 'nan_child_arithmetic_root_l_l'
        nan.nan(checks, 'nan_child_arithmetic_root_l_r')
        arithmetic.constant(checks, 'nan_child_arithmetic_root_r', 'false', '')
    else:
        unary.unary(checks, 'nan_child_arithmetic_root', 'NEGATIVE', 'PINT 4', 'NINT 4', 'PINT $(-4)', '-4', '4')
        arithmetic.binary(checks, 'nan_child_arithmetic_root_child', 'NExprBinaryOpMul', 'MULTIPLY',
                          'PBOOL true', 'PINT 4', 'PINT 4', 'NINT 1', 'NINT 4', 'NINT 4')
        prior.comparison(checks, 'nan_child_arithmetic_root_child_l', 'NOTEQUAL', VALUE,
                         ('PSTRING ($ptascii("NAN"))', '', 'NAN'), 'PBOOL true', '1')
        tag = 'nan_child_arithmetic_root_child_l_l'
        prior.strings.string(checks, 'nan_child_arithmetic_root_child_l_r', b'NAN')
        arithmetic.binary(checks, 'nan_child_arithmetic_root_child_r', 'NExprBinaryOpPlus', 'ADD',
                          'PINT 2', 'PINT 2', 'PINT 4', 'NINT 2', 'NINT 2', 'NINT 4')
        arithmetic.constant(checks, 'nan_child_arithmetic_root_child_r_l', 'E_WARNING', '2')
        arithmetic.constant(checks, 'nan_child_arithmetic_root_child_r_r', 'E_WARNING', '2')
    producer(checks, tag, operation, left, right)
    if index == 1:
        floats.constant(checks, tag + '_l')
    else:
        nan.nan(checks, tag + '_l')
    if index == 0:
        arithmetic.scalar(checks, tag + '_r', 'NScalarInt (INTEGER 1)', 'PINT 1', '1')
    elif index < 3:
        nan.nan(checks, tag + '_r')
    else:
        prior.producer(checks, tag + '_r', 'SUBTRACT', floats.POSITIVE, floats.POSITIVE)
        floats.constant(checks, tag + '_r_l')
        floats.constant(checks, tag + '_r_r')
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
    watched = [Path(module.__file__) for module in (prior, prior.prior, nan, prior.strings, floats, arithmetic, unary, runner)] + [Path(__file__)]
    before = {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.cases, runner.OUTPUTS, runner.conditions = cases, cases.OUTPUTS, conditions
    passed = runner.main()
    assert before == {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = 'Four authentic-source arithmetic fixtures require at least one genuine NaN child VALUE, exact own/child sources and reads, three compile14 precisions despite live17 and the full quiet binary result. Valid ordered numeric partners retain BYTE; genuine NaN children and results retain BYTE EPS. ConstFetch and computed arithmetic NaN sources remain distinct per occurrence. Exact pure result bits bind before dependent strict/unordered comparisons and quiet Boolean/integer ancestors. REQUEST owners, supplied throw, fixed bounds and budgets retain their laws. NaN BYTE, coercive/owning children, wider producers/ownership and held Source47 remain separate.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
