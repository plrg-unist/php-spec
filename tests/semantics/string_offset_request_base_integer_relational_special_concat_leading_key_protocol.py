#!/usr/bin/env python3
"""Exact integer relational certificates retain actual Warning continuations."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_integer_relational_special_concat_leading_key_cases as cases
import string_offset_request_base_xor_special_concat_leading_key_protocol as prior
import string_offset_request_base_bool_null_unary_special_concat_leading_key_protocol as unary

runner = prior.runner
arithmetic = prior.arithmetic


def relational(checks, tag, operation, left, right, result):
    expression, origin = 'expression_' + tag, 'porigin_' + tag
    value, text = ('PBOOL true', '1') if result else ('PBOOL false', '')
    shape = {'LESS': 'NExprBinaryOpSmaller', 'LESSEQUAL': 'NExprBinaryOpSmallerOrEqual',
             'GREATER': 'NExprBinaryOpGreater', 'GREATEREQUAL': 'NExprBinaryOpGreaterOrEqual'}[operation]
    ordered = (right, left) if operation in ('GREATER', 'GREATEREQUAL') else (left, right)
    checks += [
        '$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')',
        expression + ' = ' + shape + ' ' + expression + '_l ' + expression + '_r metadata_' + tag,
        '$pfshape(' + expression + ') = PFBINARY ' + operation + ' ' + expression + '_l ' + expression + '_r',
        '$parser_literal_at(' + expression + ', 14) = eps',
        '$compiled_read(S, ' + origin + ') = (' + value + ')',
        '$compiled_precision(S, (' + origin + ')) = (14)',
        '$long_range(' + left + ') /\ $long_range(' + right + ')',
        '$comparison_value(' + operation + ', $compare_int(' + ', '.join(ordered) + ')) = ' + value,
        '$compiled_special_concat_bytes(S, ' + origin + ') = ($ptascii(' + json.dumps(text) + '))']
    for field, suffix, child in ((0, '_l', left), (1, '_r', right)):
        checks += [
            '$origin_child((' + origin + '), [PCFIELD ' + str(field) + ']) = (' + origin + suffix + ')',
            '$origin_node(S.SOURCES, ' + origin + suffix + ') = (' + expression + suffix + ')',
            '$compiled_read(S, ' + origin + suffix + ') = (PINT ' + child + ')',
            '$compiled_precision(S, (' + origin + suffix + ')) = (14)',
            '$compiled_special_concat_bytes(S, ' + origin + suffix + ') = ($decimal_integer(' + child + '))']


def authority(index):
    checks = ['$origin_child((porigin_key), [PCFIELD 0, PCFIELD 0]) = (porigin_relational_root)',
              r'S.PRECISIONINI = $ptascii("17") /\ $precision_value(S) = 17']
    if index == 0:
        minimum, maximum = '$(-9223372036854775808)', '9223372036854775807'
        negative_maximum = '$(-9223372036854775807)'
        relational(checks, 'relational_root', 'LESS', minimum, maximum, True)
        arithmetic.binary(checks, 'relational_root_l', 'NExprBinaryOpMinus', 'SUBTRACT', 'PINT ' + negative_maximum, 'PINT 1', 'PINT ' + minimum, 'NINT ' + negative_maximum, 'NINT 1', 'NINT ' + minimum)
        arithmetic.binary(checks, 'relational_root_l_l', 'NExprBinaryOpMinus', 'SUBTRACT', 'PINT 0', 'PINT ' + maximum, 'PINT ' + negative_maximum, 'NINT 0', 'NINT ' + maximum, 'NINT ' + negative_maximum)
        arithmetic.scalar(checks, 'relational_root_l_l_l', 'NScalarInt (INTEGER 0)', 'PINT 0', '0')
        arithmetic.scalar(checks, 'relational_root_l_l_r', 'NScalarInt (INTEGER ' + maximum + ')', 'PINT ' + maximum, maximum)
        arithmetic.scalar(checks, 'relational_root_l_r', 'NScalarInt (INTEGER 1)', 'PINT 1', '1')
        arithmetic.scalar(checks, 'relational_root_r', 'NScalarInt (INTEGER ' + maximum + ')', 'PINT ' + maximum, maximum)
    elif index == 1:
        unary.unary(checks, 'relational_root', 'NEGATIVE', 'PBOOL true', 'NINT 1', 'PINT $(-1)', '-1', '1')
        relational(checks, 'relational_root_child', 'LESSEQUAL', '2', '2', True)
        arithmetic.binary(checks, 'relational_root_child_l', 'NExprBinaryOpPlus', 'ADD', 'PINT 2', 'PBOOL false', 'PINT 2', 'NINT 2', 'NINT 0', 'NINT 2')
        arithmetic.constant(checks, 'relational_root_child_l_l', 'E_WARNING', '2')
        arithmetic.constant(checks, 'relational_root_child_l_r', 'false', '')
        arithmetic.constant(checks, 'relational_root_child_r', 'E_WARNING', '2')
    elif index == 2:
        arithmetic.binary(checks, 'relational_root', 'NExprBinaryOpPlus', 'ADD', 'PBOOL false', 'PBOOL false', 'PINT 0', 'NINT 0', 'NINT 0', 'NINT 0')
        relational(checks, 'relational_root_l', 'GREATER', '1', '2', False)
        arithmetic.scalar(checks, 'relational_root_l_l', 'NScalarInt (INTEGER 1)', 'PINT 1', '1')
        arithmetic.constant(checks, 'relational_root_l_r', 'E_WARNING', '2')
        arithmetic.constant(checks, 'relational_root_r', 'false', '')
    else:
        unary.unary(checks, 'relational_root', 'NEGATIVE', 'PINT 4', 'NINT 4', 'PINT $(-4)', '-4', '4')
        arithmetic.binary(checks, 'relational_root_child', 'NExprBinaryOpMul', 'MULTIPLY', 'PBOOL true', 'PINT 4', 'PINT 4', 'NINT 1', 'NINT 4', 'NINT 4')
        relational(checks, 'relational_root_child_l', 'GREATEREQUAL', '2', '1', True)
        arithmetic.constant(checks, 'relational_root_child_l_l', 'E_WARNING', '2')
        arithmetic.scalar(checks, 'relational_root_child_l_r', 'NScalarInt (INTEGER 1)', 'PINT 1', '1')
        arithmetic.binary(checks, 'relational_root_child_r', 'NExprBinaryOpPlus', 'ADD', 'PINT 2', 'PINT 2', 'PINT 4', 'NINT 2', 'NINT 2', 'NINT 4')
        arithmetic.constant(checks, 'relational_root_child_r_l', 'E_WARNING', '2')
        arithmetic.constant(checks, 'relational_root_child_r_r', 'E_WARNING', '2')
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
    report['scope'] = 'Four actual exact-PINT relational source-state fixtures retain all four operators, both signed64 boundaries, integer equality and greater-direction argument reversal. Every own source/read/precision, long-range condition and both recursive child certificates is explicit. Unary/arithmetic ancestors, current REQUEST owners, supplied throw, fixed bounds and budgets retain existing laws. Mixed/string/float/owning comparisons and other operators remain follow-up core work.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
