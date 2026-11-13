#!/usr/bin/env python3
"""Quiet completed-power FLOAT bytes retain actual source, children and precision."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_power_float_special_concat_leading_key_cases as cases
import string_offset_request_base_power_nan_special_concat_leading_key_protocol as prior

runner, arithmetic, unary, floats, nan = prior.runner, prior.arithmetic, prior.unary, prior.floats, prior.nan
BITS = 'n_power_float_bits'
VALUE = ('PFLOAT ' + BITS, 'NFLOAT ' + BITS)
ONE = ('PINT 1', 'NINT 1', '1')
TWO = ('PINT 2', 'NINT 2', '2')


def comparison(checks, tag, operation, left, right, result, text):
    expression, origin = 'expression_' + tag, 'porigin_' + tag
    order_left, order_right = (right, left) if operation == 'GREATER' else (left, right)
    checks += ['$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')',
               expression + ' = NExprBinaryOp' + ('Spaceship' if operation == 'SPACESHIP' else 'Greater') + ' ' + expression + '_l ' + expression + '_r metadata_' + tag,
               '$pfshape(' + expression + ') = PFBINARY ' + operation + ' ' + expression + '_l ' + expression + '_r',
               '$parser_literal_at(' + expression + ', 14) = eps',
               '$compiled_read(S, ' + origin + ') = (' + result + ')',
               '$compiled_precision(S, (' + origin + ')) = (14)',
               '$compiled_special_concat_bytes(S, ' + origin + ') = ($ptascii(' + json.dumps(text) + '))',
               '$comparison_value(' + operation + ', $scalar_plain_order(S, ' + order_left[0] + ', ' + order_right[0] + ')) = ' + result]
    for field, suffix, value in ((0, '_l', left), (1, '_r', right)):
        checks += ['$origin_child((' + origin + '), [PCFIELD ' + str(field) + ']) = (' + origin + suffix + ')',
                   '$origin_node(S.SOURCES, ' + origin + suffix + ') = (' + expression + suffix + ')',
                   '$compiled_read(S, ' + origin + suffix + ') = (' + value[0] + ')',
                   '$compiled_precision(S, (' + origin + suffix + ')) = (14)',
                   '$compiled_comparison_number(S, ' + origin + suffix + ') = (' + value[1] + ')']


def producer(checks, tag, left, right):
    expression, origin = 'expression_' + tag, 'porigin_' + tag
    checks += ['$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')',
               expression + ' = NExprBinaryOpPow ' + expression + '_l ' + expression + '_r metadata_' + tag,
               '$pfshape(' + expression + ') = PFBINARY POWER ' + expression + '_l ' + expression + '_r',
               '$parser_literal_at(' + expression + ', 14) = eps',
               '$compiled_read(S, ' + origin + ') = (' + VALUE[0] + ')',
               '$compiled_precision(S, (' + origin + ')) = (14)',
               '$power_prepare(' + left[1] + ', ' + right[1] + ') = POWERDONE (' + VALUE[1] + ') false',
               '$binary_apply(S, POWER, ' + left[0] + ', ' + right[0] + ', 0) = S[.RESULT = KNOWN (' + VALUE[0] + ')]',
               '$(' + BITS + ' < 18446744073709551616)',
               '~$fparts_nan($float_decode(' + BITS + '))',
               '$number_text(' + VALUE[1] + ', 14) = (n_power_float_text*, false)',
               '$parser_literal_text_at(' + VALUE[0] + ', 14) = (n_power_float_text*)',
               '$compiled_comparison_number(S, ' + origin + ') = (' + VALUE[1] + ')',
               '$compiled_special_concat_bytes(S, ' + origin + ') = (n_power_float_text*)']
    for field, suffix, (value, number, payload) in ((0, '_l', left), (1, '_r', right)):
        checks += ['$origin_child((' + origin + '), [PCFIELD ' + str(field) + ']) = (' + origin + suffix + ')',
                   '$origin_node(S.SOURCES, ' + origin + suffix + ') = (' + expression + suffix + ')',
                   '$compiled_read(S, ' + origin + suffix + ') = (' + value + ')',
                   '$compiled_precision(S, (' + origin + suffix + ')) = (14)',
                   '$compiled_identity_value(S, ' + origin + suffix + ') = (' + value + ')',
                   '$coerce_number(' + value + ') = COERCED (' + number + ') false',
                   '$compiled_special_concat_bytes(S, ' + origin + suffix + ') = ' + ('eps' if payload is None else '($ptascii(' + json.dumps(payload) + '))')]


def authority(index):
    left = (prior.prior.CONSTANT, ('PINT 3000001', 'NINT 3000001', '3000001'), floats.POSITIVE, floats.POSITIVE)[index]
    right = (('PBOOL false', 'NINT 0', ''), ('PINT 3', 'NINT 3', '3'), ('PINT $(-2)', 'NINT $(-2)', '-2'), TWO)[index]
    checks = ['$power_prepare(' + left[1] + ', ' + right[1] + ') = POWERDONE (' + VALUE[1] + ') false',
              '$number_text(' + VALUE[1] + ', 14) = (n_power_float_text*, false)',
              '$origin_child((porigin_key), [PCFIELD 0, PCFIELD 0]) = (porigin_power_float_root)',
              r'S.PRECISIONINI = $ptascii("17") /\ $precision_value(S) = 17']
    if index in (0, 2):
        tag = 'power_float_root'
        checks += ['n_power_float_text* = $ptascii(' + json.dumps('1' if index == 0 else '0') + ')']
    elif index == 1:
        comparison(checks, 'power_float_root', 'SPACESHIP', VALUE, floats.POSITIVE, 'PINT $(-1)', '-1')
        tag = 'power_float_root_l'
        floats.constant(checks, 'power_float_root_r')
        checks += ['$number_text(' + VALUE[1] + ', 17) = (n_power_float_live_text*, false)',
                   'n_power_float_live_text* =/= n_power_float_text*']
    else:
        unary.unary(checks, 'power_float_root', 'NEGATIVE', 'PINT 4', 'NINT 4', 'PINT $(-4)', '-4', '4')
        arithmetic.binary(checks, 'power_float_root_child', 'NExprBinaryOpMul', 'MULTIPLY',
                          'PBOOL true', 'PINT 4', 'PINT 4', 'NINT 1', 'NINT 4', 'NINT 4')
        comparison(checks, 'power_float_root_child_l', 'GREATER', VALUE, ONE, 'PBOOL true', '1')
        tag = 'power_float_root_child_l_l'
        arithmetic.constant(checks, 'power_float_root_child_l_r', 'E_ERROR', '1')
        arithmetic.binary(checks, 'power_float_root_child_r', 'NExprBinaryOpPlus', 'ADD',
                          'PINT 2', 'PINT 2', 'PINT 4', 'NINT 2', 'NINT 2', 'NINT 4')
        arithmetic.constant(checks, 'power_float_root_child_r_l', 'E_WARNING', '2')
        arithmetic.constant(checks, 'power_float_root_child_r_r', 'E_WARNING', '2')
        checks += ['n_power_float_text* = $ptascii("INF")']
    producer(checks, tag, left, right)
    if index == 0:
        nan.nan(checks, tag + '_l')
        arithmetic.constant(checks, tag + '_r', 'false', '')
    else:
        if index == 1:
            checks += ['expression_' + tag + '_l = NExprBinaryOpPlus expression_' + tag + '_l_l expression_' + tag + '_l_r metadata_' + tag + '_l',
                       '$origin_child((porigin_' + tag + '_l), [PCFIELD 0]) = (porigin_' + tag + '_l_l)',
                       '$origin_child((porigin_' + tag + '_l), [PCFIELD 1]) = (porigin_' + tag + '_l_r)']
            for suffix, value in (('_l_l', 'PINT 1'), ('_l_r', 'PINT 3000000')):
                checks += ['$origin_node(S.SOURCES, porigin_' + tag + suffix + ') = (expression_' + tag + suffix + ')',
                           '$compiled_read(S, porigin_' + tag + suffix + ') = (' + value + ')',
                           '$compiled_precision(S, (porigin_' + tag + suffix + ')) = (14)']
            arithmetic.constant(checks, tag + '_l_l', 'E_ERROR', '1')
            arithmetic.scalar(checks, tag + '_l_r', 'NScalarInt (INTEGER 3000000)', 'PINT 3000000', '3000000')
            arithmetic.scalar(checks, tag + '_r', 'NScalarInt (INTEGER 3)', 'PINT 3', '3')
        else:
            floats.constant(checks, tag + '_l')
            if index == 2:
                unary.unary(checks, tag + '_r', 'NEGATIVE', 'PINT 2', 'NINT 2', 'PINT $(-2)', '-2', '2')
                arithmetic.constant(checks, tag + '_r_child', 'E_WARNING', '2')
            else:
                arithmetic.constant(checks, tag + '_r', 'E_WARNING', '2')
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
    watched = [Path(module.__file__) for module in (prior, prior.prior, prior.prior.prior, prior.strings, prior.strings.prior, nan, floats, arithmetic, unary, runner)] + [Path(__file__)]
    before = {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.cases, runner.OUTPUTS, runner.conditions = cases, cases.OUTPUTS, conditions
    passed = runner.main()
    assert before == {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = 'Four authentic-source completed POWER non-NaN FLOAT fixtures retain actual own/child source and reads, three capture precisions, genuine child scalar VALUE, quiet conversions and POWERDONE with a false diagnostic flag before exact full binary_apply and quiet output at captured14 despite live17. NAN-to-zero exponent, finite final-multiply integer overflow, INF-to-negative exponent and INF-positive exponent stay distinct; the overflow formatter distinguishes14/17. Existing REQUEST owners, supplied throw, fixed bounds and budgets retain their laws. POWERGENERAL/log-exp, Deprecated power, NaN BYTE, wider producers/owners and held Source47 remain separate. Fixtures carry source0 and saved native observations are reused once.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
