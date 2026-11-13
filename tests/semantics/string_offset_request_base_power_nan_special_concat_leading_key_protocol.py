#!/usr/bin/env python3
"""Quiet prepared power NaN VALUE retains exact source and scalar children."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_power_nan_special_concat_leading_key_cases as cases
import string_offset_request_base_arithmetic_nan_special_concat_leading_key_protocol as prior

runner, arithmetic, unary, floats, nan, strings = prior.runner, prior.arithmetic, prior.unary, prior.floats, prior.nan, prior.strings
BITS = 'n_power_nan_bits'
VALUE = ('PFLOAT ' + BITS, 'NFLOAT ' + BITS, None)
HALF = ('PFLOAT 4602678819172646912', 'NFLOAT 4602678819172646912', '0.5')
TWO = ('PINT 2', 'NINT 2', '2')


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
               '$fparts_nan($float_decode(' + BITS + '))',
               '$compiled_comparison_number(S, ' + origin + ') = (' + VALUE[1] + ')',
               '$compiled_special_concat_bytes(S, ' + origin + ') = eps']
    for field, suffix, (value, number, payload) in ((0, '_l', left), (1, '_r', right)):
        checks += ['$origin_child((' + origin + '), [PCFIELD ' + str(field) + ']) = (' + origin + suffix + ')',
                   '$origin_node(S.SOURCES, ' + origin + suffix + ') = (' + expression + suffix + ')',
                   '$compiled_read(S, ' + origin + suffix + ') = (' + value + ')',
                   '$compiled_precision(S, (' + origin + suffix + ')) = (14)',
                   '$compiled_identity_value(S, ' + origin + suffix + ') = (' + value + ')',
                   '$coerce_number(' + value + ') = COERCED (' + number + ') false']
        checks += ['$compiled_special_concat_bytes(S, ' + origin + suffix + ') = ' + ('eps' if payload is None else '($ptascii(' + json.dumps(payload) + '))')]


def authority(index):
    left = ('PINT $(-2)', 'NINT $(-2)', '-2') if index == 1 else (TWO if index == 2 else prior.CONSTANT)
    right = (TWO, HALF, prior.CONSTANT, ('PSTRING ($ptascii("2"))', 'NINT 2', '2'))[index]
    checks = ['$power_prepare(' + left[1] + ', ' + right[1] + ') = POWERDONE (' + VALUE[1] + ') false',
              'S_power_nan_pure = $binary_apply(S, POWER, ' + left[0] + ', ' + right[0] + ', 0)',
              'S_power_nan_pure.RESULT = KNOWN (' + VALUE[0] + ')',
              'S_power_nan_pure = S[.RESULT = KNOWN (' + VALUE[0] + ')]',
              '$origin_child((porigin_key), [PCFIELD 0, PCFIELD 0]) = (porigin_power_nan_root)',
              r'S.PRECISIONINI = $ptascii("17") /\ $precision_value(S) = 17']
    if index == 0:
        prior.comparison(checks, 'power_nan_root', 'NOTIDENTICAL', VALUE, prior.CONSTANT, 'PBOOL true', '1')
        tag = 'power_nan_root_l'
        nan.nan(checks, 'power_nan_root_r')
    elif index == 1:
        unary.unary(checks, 'power_nan_root', 'NEGATIVE', 'PINT 1', 'NINT 1', 'PINT $(-1)', '-1', '1')
        prior.comparison(checks, 'power_nan_root_child', 'SPACESHIP', VALUE,
                         ('PFLOAT 4609434218613702656', 'NFLOAT 4609434218613702656', '1.5'), 'PINT 1', '1')
        tag = 'power_nan_root_child_l'
        prior.prior.scalar(checks, 'power_nan_root_child_r', '4609434218613702656', '1.5')
    elif index == 2:
        arithmetic.binary(checks, 'power_nan_root', 'NExprBinaryOpPlus', 'ADD',
                          'PBOOL false', 'PBOOL false', 'PINT 0', 'NINT 0', 'NINT 0', 'NINT 0')
        prior.comparison(checks, 'power_nan_root_l', 'IDENTICAL', VALUE, prior.CONSTANT, 'PBOOL false', '')
        tag = 'power_nan_root_l_l'
        nan.nan(checks, 'power_nan_root_l_r')
        arithmetic.constant(checks, 'power_nan_root_r', 'false', '')
    else:
        unary.unary(checks, 'power_nan_root', 'NEGATIVE', 'PINT 4', 'NINT 4', 'PINT $(-4)', '-4', '4')
        arithmetic.binary(checks, 'power_nan_root_child', 'NExprBinaryOpMul', 'MULTIPLY',
                          'PBOOL true', 'PINT 4', 'PINT 4', 'NINT 1', 'NINT 4', 'NINT 4')
        prior.comparison(checks, 'power_nan_root_child_l', 'NOTEQUAL', VALUE,
                         ('PSTRING ($ptascii("NAN"))', '', 'NAN'), 'PBOOL true', '1')
        tag = 'power_nan_root_child_l_l'
        strings.string(checks, 'power_nan_root_child_l_r', b'NAN')
        arithmetic.binary(checks, 'power_nan_root_child_r', 'NExprBinaryOpPlus', 'ADD',
                          'PINT 2', 'PINT 2', 'PINT 4', 'NINT 2', 'NINT 2', 'NINT 4')
        arithmetic.constant(checks, 'power_nan_root_child_r_l', 'E_WARNING', '2')
        arithmetic.constant(checks, 'power_nan_root_child_r_r', 'E_WARNING', '2')
    producer(checks, tag, left, right)
    if index == 1:
        unary.unary(checks, tag + '_l', 'NEGATIVE', 'PINT 2', 'NINT 2', 'PINT $(-2)', '-2', '2')
        arithmetic.constant(checks, tag + '_l_child', 'E_WARNING', '2')
        prior.prior.scalar(checks, tag + '_r', '4602678819172646912', '0.5')
    else:
        if index == 2:
            arithmetic.scalar(checks, tag + '_l', 'NScalarInt (INTEGER 2)', 'PINT 2', '2')
            nan.nan(checks, tag + '_r')
        else:
            nan.nan(checks, tag + '_l')
            if index == 0:
                arithmetic.scalar(checks, tag + '_r', 'NScalarInt (INTEGER 2)', 'PINT 2', '2')
            else:
                strings.string(checks, tag + '_r', b'2')
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
    watched = [Path(module.__file__) for module in (prior, prior.prior, nan, strings, floats, arithmetic, unary, runner)] + [Path(__file__)]
    before = {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.cases, runner.OUTPUTS, runner.conditions = cases, cases.OUTPUTS, conditions
    passed = runner.main()
    assert before == {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = 'Four authentic-source prepared POWER NaN fixtures retain actual own/child source and reads, three compile14 precisions despite live17, genuine scalar child identity VALUE and quiet coercions. Only POWERDONE NFLOAT with false diagnostic flag supplies exact NaN bits before the full quiet operation and dependent comparisons. NaN operands or a negative integer base with fractional exponent and a full numeric string exponent retain separate source facts. REQUEST owners, supplied throw, fixed bounds and budgets retain their laws. NaN BYTE, POWERGENERAL/log-exp, Deprecated power, nonNaN float-power BYTE, wider producers/ownership and held Source47 remain separate.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
