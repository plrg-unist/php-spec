#!/usr/bin/env python3
"""Quiet NaN/scalar comparisons use VALUE and true reverse order, never NaN BYTE."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_nan_scalar_comparison_special_concat_leading_key_cases as cases
import string_offset_request_base_numeric_comparison_special_concat_leading_key_protocol as prior
import string_offset_request_base_nan_comparison_special_concat_leading_key_protocol as nan
import string_offset_request_base_string_bitwise_special_concat_leading_key_protocol as strings

runner, arithmetic, unary = prior.runner, prior.arithmetic, prior.unary
VALUE = 'PFLOAT ' + nan.NAN


def comparison(checks, tag, operation, partner, payload, nan_left, result, text):
    expression, origin = 'expression_' + tag, 'porigin_' + tag
    shape = {'LESS': 'Smaller', 'LESSEQUAL': 'SmallerOrEqual', 'GREATER': 'Greater',
             'GREATEREQUAL': 'GreaterOrEqual', 'EQUAL': 'Equal', 'NOTEQUAL': 'NotEqual',
             'SPACESHIP': 'Spaceship'}[operation]
    left, right = (VALUE, partner) if nan_left else (partner, VALUE)
    ordered = (right, left) if operation in ('GREATER', 'GREATEREQUAL') else (left, right)
    checks += [
        '$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')',
        expression + ' = NExprBinaryOp' + shape + ' ' + expression + '_l ' + expression + '_r metadata_' + tag,
        '$pfshape(' + expression + ') = PFBINARY ' + operation + ' ' + expression + '_l ' + expression + '_r',
        '$parser_literal_at(' + expression + ', 14) = eps',
        '$compiled_read(S, ' + origin + ') = (' + result + ')',
        '$compiled_precision(S, (' + origin + ')) = (14)',
        '$comparison_value(' + operation + ', $scalar_plain_order(S, ' + ordered[0] + ', ' + ordered[1] + ')) = ' + result,
        '$echo_value(' + result + ') = $ptascii(' + json.dumps(text) + ')',
        '$compiled_special_concat_bytes(S, ' + origin + ') = ($ptascii(' + json.dumps(text) + '))']
    for field, suffix in ((0, '_l'), (1, '_r')):
        is_nan = nan_left == (field == 0)
        value = VALUE if is_nan else partner
        checks += [
            '$origin_child((' + origin + '), [PCFIELD ' + str(field) + ']) = (' + origin + suffix + ')',
            '$origin_node(S.SOURCES, ' + origin + suffix + ') = (' + expression + suffix + ')',
            '$compiled_read(S, ' + origin + suffix + ') = (' + value + ')',
            '$compiled_precision(S, (' + origin + suffix + ')) = (14)']
        if is_nan:
            nan.nan(checks, tag + suffix)
            checks += ['$compiled_comparison_number(S, ' + origin + suffix + ') = (NFLOAT ' + nan.NAN + ')',
                       '$(' + nan.NAN + ' < 18446744073709551616)',
                       '$fparts_nan($float_decode(' + nan.NAN + '))',
                       '$compiled_special_concat_bytes(S, ' + origin + suffix + ') = eps',
                       '$parser_literal_text_at(' + VALUE + ', 14) = eps',
                       '$number_text(NFLOAT ' + nan.NAN + ', 14) = ($ptascii("NAN"), true)']
        else:
            checks += ['$compiled_special_concat_bytes(S, ' + origin + suffix + ') = ($ptascii(' + json.dumps(payload) + '))']
            if partner.startswith('PSTRING '):
                strings.string(checks, tag + suffix, payload.encode())
            else:
                arithmetic.constant(checks, tag + suffix, 'null' if partner == 'PNULL' else 'true', payload)
                checks += ['$type_bytes(' + partner + ') <- [$ptascii("bool"), $ptascii("null")]']


def authority(index):
    checks = ['$origin_child((porigin_key), [PCFIELD 0, PCFIELD 0]) = (porigin_nan_scalar_root)',
              r'S.PRECISIONINI = $ptascii("17") /\ $precision_value(S) = 17']
    string = 'PSTRING ($ptascii("x"))'
    if index == 0:
        checks += ['$origin_node(S.SOURCES, porigin_nan_scalar_root) = (expression_nan_scalar_root)',
                   'expression_nan_scalar_root = NExprBooleanNot expression_nan_scalar_root_child metadata_nan_scalar_root',
                   '$origin_child((porigin_nan_scalar_root), [PCFIELD 0]) = (porigin_nan_scalar_root_child)',
                   '$origin_node(S.SOURCES, porigin_nan_scalar_root_child) = (expression_nan_scalar_root_child)',
                   '$compiled_read(S, porigin_nan_scalar_root) = (PBOOL true)',
                   '$compiled_precision(S, (porigin_nan_scalar_root)) = (14)',
                   '$compiled_read(S, porigin_nan_scalar_root_child) = (PBOOL false)',
                   '$compiled_precision(S, (porigin_nan_scalar_root_child)) = (14)',
                   '$parser_literal_at(expression_nan_scalar_root_child, 14) = eps',
                   '~$truth(S, PBOOL false)',
                   '$compiled_special_concat_bytes(S, porigin_nan_scalar_root) = ($ptascii("1"))']
        comparison(checks, 'nan_scalar_root_child', 'GREATER', string, 'x', True, 'PBOOL false', '')
        checks += ['$scalar_plain_order(S, ' + VALUE + ', ' + string + ') = 1',
                   '$scalar_plain_order(S, ' + string + ', ' + VALUE + ') = 1']
    elif index == 1:
        unary.unary(checks, 'nan_scalar_root', 'NEGATIVE', 'PINT 1', 'NINT 1', 'PINT $(-1)', '-1', '1')
        comparison(checks, 'nan_scalar_root_child', 'SPACESHIP', 'PNULL', '', True, 'PINT 1', '1')
        checks += ['$scalar_plain_order(S, ' + VALUE + ', PNULL) = 1',
                   '$scalar_plain_order(S, PNULL, ' + VALUE + ') = $(-1)']
    elif index == 2:
        arithmetic.binary(checks, 'nan_scalar_root', 'NExprBinaryOpPlus', 'ADD', 'PINT 0', 'PBOOL false', 'PINT 0', 'NINT 0', 'NINT 0', 'NINT 0')
        comparison(checks, 'nan_scalar_root_l', 'SPACESHIP', 'PBOOL true', '1', True, 'PINT 0', '0')
        arithmetic.constant(checks, 'nan_scalar_root_r', 'false', '')
        checks += ['$scalar_plain_order(S, ' + VALUE + ', PBOOL true) = 0',
                   '$scalar_plain_order(S, PBOOL true, ' + VALUE + ') = 0']
    else:
        unary.unary(checks, 'nan_scalar_root', 'NEGATIVE', 'PINT 4', 'NINT 4', 'PINT $(-4)', '-4', '4')
        arithmetic.binary(checks, 'nan_scalar_root_child', 'NExprBinaryOpMul', 'MULTIPLY', 'PBOOL true', 'PINT 4', 'PINT 4', 'NINT 1', 'NINT 4', 'NINT 4')
        comparison(checks, 'nan_scalar_root_child_l', 'NOTEQUAL', string, 'x', False, 'PBOOL true', '1')
        arithmetic.binary(checks, 'nan_scalar_root_child_r', 'NExprBinaryOpPlus', 'ADD', 'PINT 2', 'PINT 2', 'PINT 4', 'NINT 2', 'NINT 2', 'NINT 4')
        arithmetic.constant(checks, 'nan_scalar_root_child_r_l', 'E_WARNING', '2')
        arithmetic.constant(checks, 'nan_scalar_root_child_r_r', 'E_WARNING', '2')
        checks += ['$scalar_plain_order(S, ' + string + ', ' + VALUE + ') = 1',
                   '$scalar_plain_order(S, ' + VALUE + ', ' + string + ') = 1']
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
    watched = [Path(module.__file__) for module in (prior, nan, strings, strings.prior, arithmetic, unary, runner)] + [Path(__file__)]
    before = {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.cases, runner.OUTPUTS, runner.conditions = cases, cases.OUTPUTS, conditions
    passed = runner.main()
    assert before == {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = 'Four authentic NaN ConstFetch/scalar fixtures retain existing typed valid64 NaN VALUE facts with BYTE absent, actual own/child sources and reads, three matching compile14 precisions despite live17, and quiet BOOL/NULL or exact raw PSTRING partner BYTE. Existing52 scalar_plain_order preserves quiet TRUE equality and NULL order plus unordered string/NaN +1 in both directions; greater uses actual reverse, never sign negation. NOT sees an actual Boolean comparison result only, and arithmetic/unary ancestors see quiet Boolean/integer outputs. Existing REQUEST owners, supplied throw, fixed bounds and budgets retain their laws. No operand NaN string/Boolean conversion, new dispatcher, arithmetic NaN, strict identity, owning/carrier or held Source47 expansion.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
