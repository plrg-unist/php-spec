#!/usr/bin/env python3
"""Non-NaN numeric comparison certificates retain Warning histories."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_numeric_comparison_special_concat_leading_key_cases as cases
import string_offset_request_base_string_bitwise_special_concat_leading_key_protocol as prior
import string_offset_request_base_arithmetic_special_concat_leading_key_protocol as arithmetic
import string_offset_request_base_bool_null_unary_special_concat_leading_key_protocol as unary

runner = prior.runner
HALF3, HALF5 = '$float_round(0, 3, 2)', '$float_round(0, 5, 2)'


def comparison(checks, tag, operation, left, right, result, text):
    expression, origin = 'expression_' + tag, 'porigin_' + tag
    shape = {'LESS': 'Smaller', 'LESSEQUAL': 'SmallerOrEqual', 'GREATER': 'Greater',
             'GREATEREQUAL': 'GreaterOrEqual', 'EQUAL': 'Equal', 'NOTEQUAL': 'NotEqual',
             'SPACESHIP': 'Spaceship'}[operation]
    ordered = (right[1], left[1]) if operation in ('GREATER', 'GREATEREQUAL') else (left[1], right[1])
    checks += [
        '$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')',
        expression + ' = NExprBinaryOp' + shape + ' ' + expression + '_l ' + expression + '_r metadata_' + tag,
        '$pfshape(' + expression + ') = PFBINARY ' + operation + ' ' + expression + '_l ' + expression + '_r',
        '$parser_literal_at(' + expression + ', 14) = eps',
        '$compiled_read(S, ' + origin + ') = (' + result + ')',
        '$compiled_precision(S, (' + origin + ')) = (14)',
        '$comparison_value(' + operation + ', $num_compare(' + ordered[0] + ', ' + ordered[1] + ')) = ' + result,
        '$echo_value(' + result + ') = $ptascii(' + json.dumps(text) + ')',
        '$compiled_special_concat_bytes(S, ' + origin + ') = ($ptascii(' + json.dumps(text) + '))']
    for field, suffix, (value, number, child_text) in ((0, '_l', left), (1, '_r', right)):
        checks += [
            '$origin_child((' + origin + '), [PCFIELD ' + str(field) + ']) = (' + origin + suffix + ')',
            '$origin_node(S.SOURCES, ' + origin + suffix + ') = (' + expression + suffix + ')',
            '$compiled_read(S, ' + origin + suffix + ') = (' + value + ')',
            '$compiled_precision(S, (' + origin + suffix + ')) = (14)',
            '$compiled_special_concat_bytes(S, ' + origin + suffix + ') = ($ptascii(' + json.dumps(child_text) + '))',
            '$coerce_number(' + value + ') = COERCED (' + number + ') false',
            '$number_bool(' + number + ') = (b_' + tag + suffix + ', false)']
        if value.startswith('PINT '):
            checks += ['$long_range(' + value[5:] + ')']
        else:
            checks += ['$(' + value[7:] + ' < 18446744073709551616)',
                       '~$fparts_nan($float_decode(' + value[7:] + '))']


def scalar(checks, tag, bits, text):
    arithmetic.scalar(checks, tag, 'NScalarFloat (FLOAT text_' + tag + ')', 'PFLOAT ' + bits, text)
    checks += ['$hex_bits(text_' + tag + ', 0) = ' + bits]


def authority(index):
    checks = ['$origin_child((porigin_key), [PCFIELD 0, PCFIELD 0]) = (porigin_numeric_root)',
              r'S.PRECISIONINI = $ptascii("17") /\ $precision_value(S) = 17']
    half3, half5 = ('PFLOAT ' + HALF3, 'NFLOAT ' + HALF3, '1.5'), ('PFLOAT ' + HALF5, 'NFLOAT ' + HALF5, '2.5')
    if index == 0:
        comparison(checks, 'numeric_root', 'LESS', half3, ('PINT 2', 'NINT 2', '2'), 'PBOOL true', '1')
        scalar(checks, 'numeric_root_l', HALF3, '1.5')
        arithmetic.constant(checks, 'numeric_root_r', 'E_WARNING', '2')
    elif index == 1:
        comparison(checks, 'numeric_root', 'SPACESHIP', half3, half5, 'PINT $(-1)', '-1')
        scalar(checks, 'numeric_root_l', HALF3, '1.5')
        scalar(checks, 'numeric_root_r', HALF5, '2.5')
    elif index == 2:
        arithmetic.binary(checks, 'numeric_root', 'NExprBinaryOpPlus', 'ADD', 'PBOOL false', 'PBOOL false', 'PINT 0', 'NINT 0', 'NINT 0', 'NINT 0')
        comparison(checks, 'numeric_root_l', 'NOTEQUAL', half3, half3, 'PBOOL false', '')
        scalar(checks, 'numeric_root_l_l', HALF3, '1.5')
        scalar(checks, 'numeric_root_l_r', HALF3, '1.5')
        arithmetic.constant(checks, 'numeric_root_r', 'false', '')
    else:
        unary.unary(checks, 'numeric_root', 'NEGATIVE', 'PINT 4', 'NINT 4', 'PINT $(-4)', '-4', '4')
        arithmetic.binary(checks, 'numeric_root_child', 'NExprBinaryOpMul', 'MULTIPLY', 'PBOOL true', 'PINT 4', 'PINT 4', 'NINT 1', 'NINT 4', 'NINT 4')
        comparison(checks, 'numeric_root_child_l', 'GREATEREQUAL', half3, ('PINT 1', 'NINT 1', '1'), 'PBOOL true', '1')
        scalar(checks, 'numeric_root_child_l_l', HALF3, '1.5')
        arithmetic.scalar(checks, 'numeric_root_child_l_r', 'NScalarInt (INTEGER 1)', 'PINT 1', '1')
        arithmetic.binary(checks, 'numeric_root_child_r', 'NExprBinaryOpPlus', 'ADD', 'PINT 2', 'PINT 2', 'PINT 4', 'NINT 2', 'NINT 2', 'NINT 4')
        arithmetic.constant(checks, 'numeric_root_child_r_l', 'E_WARNING', '2')
        arithmetic.constant(checks, 'numeric_root_child_r_r', 'E_WARNING', '2')
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
    watched = [Path(module.__file__) for module in (prior, prior.prior, arithmetic, unary, runner)] + [Path(__file__)]
    before = {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.cases = cases
    runner.OUTPUTS = cases.OUTPUTS
    runner.conditions = conditions
    passed = runner.main()
    assert before == {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = 'Four actual non-NaN numeric comparison source-state fixtures use exact fractions1.5/2.5 and integer counterparts, preserving Boolean versus spaceship integer results. Own/child source occurrences, reads, recursive certificates and three precisions are explicit; typed numeric conversions, signed64 integer ranges, valid64bit non-NaN float bits and early num_compare establish quiet numeric order. Independent final-fixture comparison_value uses reversed operands for greater operators, without imposing a later-helper production dependency. Existing arithmetic/unary ancestors, REQUEST owners, supplied throw, fixed bounds and budgets retain prior laws. NaN, nonnumeric weak comparisons and wider histories remain separate core obligations.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
