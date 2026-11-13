#!/usr/bin/env python3
"""NaN comparison value facts retain quiet operands and Warning histories."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_nan_comparison_special_concat_leading_key_cases as cases
import string_offset_request_base_numeric_comparison_special_concat_leading_key_protocol as prior

runner = prior.runner
arithmetic, unary = prior.arithmetic, prior.unary
NAN = '9221120237041090560'
HALF3 = prior.HALF3


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
            '$compiled_precision(S, (' + origin + suffix + ')) = (14)']
        if child_text is None:
            checks += ['$compiled_special_concat_bytes(S, ' + origin + suffix + ') = eps',
                       '$parser_literal_text_at(' + value + ', 14) = eps',
                       '$number_text(' + number + ', 14) = ($ptascii("NAN"), true)']
        else:
            checks += ['$compiled_special_concat_bytes(S, ' + origin + suffix + ') = ($ptascii(' + json.dumps(child_text) + '))']
        if value.startswith('PINT '):
            checks += ['$long_range(' + value[5:] + ')']
        else:
            checks += ['$(' + value[7:] + ' < 18446744073709551616)',
                       ('' if child_text is None else '~') + '$fparts_nan($float_decode(' + value[7:] + '))']


def nan(checks, tag):
    checks += [
        'expression_' + tag + ' = NExprConstFetch name_' + tag + ' metadata_' + tag,
        '$ptast(name_' + tag + ') = PTNAME PTPLAIN ($ptascii("NAN"))',
        '$parser_literal_at(expression_' + tag + ', 14) = eps']


def authority(index):
    checks = ['$origin_child((porigin_key), [PCFIELD 0, PCFIELD 0]) = (porigin_nan_root)',
              r'S.PRECISIONINI = $ptascii("17") /\ $precision_value(S) = 17']
    half3 = ('PFLOAT ' + HALF3, 'NFLOAT ' + HALF3, '1.5')
    notnumber = ('PFLOAT ' + NAN, 'NFLOAT ' + NAN, None)
    if index == 0:
        arithmetic.binary(checks, 'nan_root', 'NExprBinaryOpPlus', 'ADD', 'PBOOL false', 'PBOOL true', 'PINT 1', 'NINT 0', 'NINT 1', 'NINT 1')
        comparison(checks, 'nan_root_l', 'GREATER', notnumber, half3, 'PBOOL false', '')
        nan(checks, 'nan_root_l_l')
        prior.scalar(checks, 'nan_root_l_r', HALF3, '1.5')
        arithmetic.constant(checks, 'nan_root_r', 'true', '1')
    elif index == 1:
        unary.unary(checks, 'nan_root', 'NEGATIVE', 'PINT 1', 'NINT 1', 'PINT $(-1)', '-1', '1')
        comparison(checks, 'nan_root_child', 'SPACESHIP', half3, notnumber, 'PINT 1', '1')
        prior.scalar(checks, 'nan_root_child_l', HALF3, '1.5')
        nan(checks, 'nan_root_child_r')
    elif index == 2:
        arithmetic.binary(checks, 'nan_root', 'NExprBinaryOpPlus', 'ADD', 'PBOOL false', 'PBOOL false', 'PINT 0', 'NINT 0', 'NINT 0', 'NINT 0')
        comparison(checks, 'nan_root_l', 'EQUAL', notnumber, notnumber, 'PBOOL false', '')
        nan(checks, 'nan_root_l_l')
        nan(checks, 'nan_root_l_r')
        arithmetic.constant(checks, 'nan_root_r', 'false', '')
    else:
        unary.unary(checks, 'nan_root', 'NEGATIVE', 'PINT 4', 'NINT 4', 'PINT $(-4)', '-4', '4')
        arithmetic.binary(checks, 'nan_root_child', 'NExprBinaryOpPlus', 'ADD', 'PBOOL false', 'PINT 4', 'PINT 4', 'NINT 0', 'NINT 4', 'NINT 4')
        comparison(checks, 'nan_root_child_l', 'GREATEREQUAL', notnumber, notnumber, 'PBOOL false', '')
        nan(checks, 'nan_root_child_l_l')
        nan(checks, 'nan_root_child_l_r')
        arithmetic.binary(checks, 'nan_root_child_r', 'NExprBinaryOpPlus', 'ADD', 'PINT 2', 'PINT 2', 'PINT 4', 'NINT 2', 'NINT 2', 'NINT 4')
        arithmetic.constant(checks, 'nan_root_child_r_l', 'E_WARNING', '2')
        arithmetic.constant(checks, 'nan_root_child_r_r', 'E_WARNING', '2')
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
    report['scope'] = 'Four actual NAN ConstFetch comparison fixtures retain valid64bit PFLOAT NaN own reads and actual source children at compile14/live17. NAN quiet-byte certificates stay EPS because formatting has a pending notice. Comparisons themselves preserve typed BOOL or spaceship PINT results with reversed greater operands and no operand formatting/Boolean conversion. NonNaN child certificates and all arithmetic/unary ancestors, REQUEST owners, supplied throw, fixed bounds and budgets remain explicit. Wider NaN producers and weak/coercive comparisons remain separate; Source47 lowprecision DEFINE-name NaN is untouched.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
