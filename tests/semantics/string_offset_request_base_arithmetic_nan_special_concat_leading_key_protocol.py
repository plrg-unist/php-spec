#!/usr/bin/env python3
"""Quiet arithmetic NaN VALUE retains exact sources without NaN BYTE."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_arithmetic_nan_special_concat_leading_key_cases as cases
import string_offset_request_base_numeric_comparison_special_concat_leading_key_protocol as prior
import string_offset_request_base_float_const_special_concat_leading_key_protocol as floats
import string_offset_request_base_nan_comparison_special_concat_leading_key_protocol as nan
import string_offset_request_base_string_bitwise_special_concat_leading_key_protocol as strings

runner, arithmetic, unary = prior.runner, prior.arithmetic, prior.unary
BITS = 'n_arithmetic_nan_bits'
VALUE = ('PFLOAT ' + BITS, 'NFLOAT ' + BITS, None)
CONSTANT = ('PFLOAT ' + nan.NAN, 'NFLOAT ' + nan.NAN, None)


def comparison(checks, tag, operation, left, right, result, text):
    expression, origin = 'expression_' + tag, 'porigin_' + tag
    shape = {'IDENTICAL': 'Identical', 'NOTIDENTICAL': 'NotIdentical',
             'SPACESHIP': 'Spaceship', 'NOTEQUAL': 'NotEqual'}[operation]
    checks += ['$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')',
               expression + ' = NExprBinaryOp' + shape + ' ' + expression + '_l ' + expression + '_r metadata_' + tag,
               '$pfshape(' + expression + ') = PFBINARY ' + operation + ' ' + expression + '_l ' + expression + '_r',
               '$parser_literal_at(' + expression + ', 14) = eps',
               '$compiled_read(S, ' + origin + ') = (' + result + ')',
               '$compiled_precision(S, (' + origin + ')) = (14)',
               '$compiled_special_concat_bytes(S, ' + origin + ') = ($ptascii(' + json.dumps(text) + '))']
    if operation in ('IDENTICAL', 'NOTIDENTICAL'):
        checks += ['$strict_identical(' + left[0] + ', ' + right[0] + ') = false']
    else:
        checks += ['$comparison_value(' + operation + ', $scalar_plain_order(S, ' + left[0] + ', ' + right[0] + ')) = ' + result]
    for field, suffix, (value, number, payload) in ((0, '_l', left), (1, '_r', right)):
        checks += ['$origin_child((' + origin + '), [PCFIELD ' + str(field) + ']) = (' + origin + suffix + ')',
                   '$origin_node(S.SOURCES, ' + origin + suffix + ') = (' + expression + suffix + ')',
                   '$compiled_read(S, ' + origin + suffix + ') = (' + value + ')',
                   '$compiled_precision(S, (' + origin + suffix + ')) = (14)']
        if payload is None:
            checks += ['$compiled_comparison_number(S, ' + origin + suffix + ') = (' + number + ')',
                       '$compiled_special_concat_bytes(S, ' + origin + suffix + ') = eps',
                       '$parser_literal_text_at(' + value + ', 14) = eps',
                       '$number_text(' + number + ', 14) = ($ptascii("NAN"), true)']
        else:
            checks += ['$compiled_special_concat_bytes(S, ' + origin + suffix + ') = ($ptascii(' + json.dumps(payload) + '))']


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
                   '$compiled_order_number(' + value + ') = (' + number + ')',
                   '$coerce_number(' + value + ') = COERCED (' + number + ') false',
                   '$compiled_special_concat_bytes(S, ' + origin + suffix + ') = ($ptascii(' + json.dumps(payload) + '))']


def authority(index):
    operation = ('SUBTRACT', 'DIVIDE', 'MULTIPLY', 'ADD')[index]
    right = (floats.POSITIVE, floats.POSITIVE, ('PINT 0', 'NINT 0', '0'), floats.NEGATIVE)[index]
    checks = ['$number_binary(' + operation + ', ' + floats.POSITIVE[1] + ', ' + right[1] + ') = NUM (' + VALUE[1] + ')',
              '$origin_child((porigin_key), [PCFIELD 0, PCFIELD 0]) = (porigin_arithmetic_nan_root)',
              r'S.PRECISIONINI = $ptascii("17") /\ $precision_value(S) = 17']
    if index == 0:
        comparison(checks, 'arithmetic_nan_root', 'NOTIDENTICAL', VALUE, CONSTANT, 'PBOOL true', '1')
        tag = 'arithmetic_nan_root_l'
        nan.nan(checks, 'arithmetic_nan_root_r')
    elif index == 1:
        unary.unary(checks, 'arithmetic_nan_root', 'NEGATIVE', 'PINT 1', 'NINT 1', 'PINT $(-1)', '-1', '1')
        comparison(checks, 'arithmetic_nan_root_child', 'SPACESHIP', VALUE,
                   ('PFLOAT 4609434218613702656', 'NFLOAT 4609434218613702656', '1.5'), 'PINT 1', '1')
        tag = 'arithmetic_nan_root_child_l'
        prior.scalar(checks, 'arithmetic_nan_root_child_r', '4609434218613702656', '1.5')
    elif index == 2:
        arithmetic.binary(checks, 'arithmetic_nan_root', 'NExprBinaryOpPlus', 'ADD',
                          'PBOOL false', 'PBOOL false', 'PINT 0', 'NINT 0', 'NINT 0', 'NINT 0')
        comparison(checks, 'arithmetic_nan_root_l', 'IDENTICAL', VALUE, CONSTANT, 'PBOOL false', '')
        tag = 'arithmetic_nan_root_l_l'
        nan.nan(checks, 'arithmetic_nan_root_l_r')
        arithmetic.constant(checks, 'arithmetic_nan_root_r', 'false', '')
    else:
        unary.unary(checks, 'arithmetic_nan_root', 'NEGATIVE', 'PINT 4', 'NINT 4', 'PINT $(-4)', '-4', '4')
        arithmetic.binary(checks, 'arithmetic_nan_root_child', 'NExprBinaryOpMul', 'MULTIPLY',
                          'PBOOL true', 'PINT 4', 'PINT 4', 'NINT 1', 'NINT 4', 'NINT 4')
        comparison(checks, 'arithmetic_nan_root_child_l', 'NOTEQUAL', VALUE,
                   ('PSTRING ($ptascii("NAN"))', '', 'NAN'), 'PBOOL true', '1')
        tag = 'arithmetic_nan_root_child_l_l'
        strings.string(checks, 'arithmetic_nan_root_child_l_r', b'NAN')
        arithmetic.binary(checks, 'arithmetic_nan_root_child_r', 'NExprBinaryOpPlus', 'ADD',
                          'PINT 2', 'PINT 2', 'PINT 4', 'NINT 2', 'NINT 2', 'NINT 4')
        arithmetic.constant(checks, 'arithmetic_nan_root_child_r_l', 'E_WARNING', '2')
        arithmetic.constant(checks, 'arithmetic_nan_root_child_r_r', 'E_WARNING', '2')
    producer(checks, tag, operation, floats.POSITIVE, right)
    floats.constant(checks, tag + '_l')
    if index < 2:
        floats.constant(checks, tag + '_r')
    elif index == 2:
        arithmetic.scalar(checks, tag + '_r', 'NScalarInt (INTEGER 0)', 'PINT 0', '0')
    else:
        floats.negative(checks, tag + '_r')
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
    watched = [Path(module.__file__) for module in (prior, floats, nan, strings, arithmetic, unary, runner)] + [Path(__file__)]
    before = {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.cases, runner.OUTPUTS, runner.conditions = cases, cases.OUTPUTS, conditions
    passed = runner.main()
    assert before == {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = 'Four authentic-source arithmetic NaN fixtures retain actual ADD/SUBTRACT/MULTIPLY/DIVIDE sources, own and child reads and three compile14 precisions despite live17. Valid quiet nonNaN numeric children keep BYTE; exact pure arithmetic binds the NaN result bits before dependent predicates. Comparisons consume VALUE while NaN BYTE/formatting remains refused; strict types and unordered numeric/raw-string order keep quiet Boolean/integer ancestors. Existing REQUEST owners, supplied throw, fixed bounds and budgets remain. Arithmetic with NaN children, unary NaN VALUE, wider producers, carriers/owning forms and held Source47 remain separate.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
