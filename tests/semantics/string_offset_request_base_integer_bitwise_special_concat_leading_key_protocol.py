#!/usr/bin/env python3
"""Exact integer AND/OR/XOR certificates retain Warning continuations."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_integer_bitwise_special_concat_leading_key_cases as cases
import string_offset_request_base_integer_bitnot_special_concat_leading_key_protocol as prior

runner = prior.runner
arithmetic = prior.arithmetic
MAXIMUM = '9223372036854775807'
MINIMUM = '$(-9223372036854775808)'
NEGATIVE_MAXIMUM = '$(-9223372036854775807)'


def bitwise(checks, tag, operation, left, right, result):
    expression, origin = 'expression_' + tag, 'porigin_' + tag
    shape, helper = {'BITAND': ('NExprBinaryOpBitwiseAnd', 'long_and'),
                     'BITOR': ('NExprBinaryOpBitwiseOr', 'long_or'),
                     'BITXOR': ('NExprBinaryOpBitwiseXor', 'long_xor')}[operation]
    checks += [
        '$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')',
        expression + ' = ' + shape + ' ' + expression + '_l ' + expression + '_r metadata_' + tag,
        '$pfshape(' + expression + ') = PFBINARY ' + operation + ' ' + expression + '_l ' + expression + '_r',
        '$parser_literal_at(' + expression + ', 14) = eps',
        '$compiled_read(S, ' + origin + ') = (PINT ' + result + ')',
        '$compiled_precision(S, (' + origin + ')) = (14)',
        '$long_range(' + left + r') /\ $long_range(' + right + r') /\ $long_range(' + result + ')',
        '$' + helper + '(' + left + ', ' + right + ') = ' + result,
        '$compiled_special_concat_bytes(S, ' + origin + ') = ($decimal_integer(' + result + '))']
    for field, suffix, child in ((0, '_l', left), (1, '_r', right)):
        checks += [
            '$origin_child((' + origin + '), [PCFIELD ' + str(field) + ']) = (' + origin + suffix + ')',
            '$origin_node(S.SOURCES, ' + origin + suffix + ') = (' + expression + suffix + ')',
            '$compiled_read(S, ' + origin + suffix + ') = (PINT ' + child + ')',
            '$compiled_precision(S, (' + origin + suffix + ')) = (14)',
            '$compiled_special_concat_bytes(S, ' + origin + suffix + ') = ($decimal_integer(' + child + '))']


def minimum(checks, tag):
    arithmetic.binary(checks, tag, 'NExprBinaryOpMinus', 'SUBTRACT', 'PINT ' + NEGATIVE_MAXIMUM, 'PINT 1', 'PINT ' + MINIMUM, 'NINT ' + NEGATIVE_MAXIMUM, 'NINT 1', 'NINT ' + MINIMUM)
    arithmetic.binary(checks, tag + '_l', 'NExprBinaryOpMinus', 'SUBTRACT', 'PINT 0', 'PINT ' + MAXIMUM, 'PINT ' + NEGATIVE_MAXIMUM, 'NINT 0', 'NINT ' + MAXIMUM, 'NINT ' + NEGATIVE_MAXIMUM)
    arithmetic.scalar(checks, tag + '_l_l', 'NScalarInt (INTEGER 0)', 'PINT 0', '0')
    arithmetic.scalar(checks, tag + '_l_r', 'NScalarInt (INTEGER ' + MAXIMUM + ')', 'PINT ' + MAXIMUM, MAXIMUM)
    arithmetic.scalar(checks, tag + '_r', 'NScalarInt (INTEGER 1)', 'PINT 1', '1')


def authority(index):
    checks = ['$origin_child((porigin_key), [PCFIELD 0, PCFIELD 0]) = (porigin_bitwise_root)',
              r'S.PRECISIONINI = $ptascii("17") /\ $precision_value(S) = 17']
    if index == 0:
        bitwise(checks, 'bitwise_root', 'BITAND', '$(-1)', '1', '1')
        bitwise(checks, 'bitwise_root_l', 'BITOR', MINIMUM, MAXIMUM, '$(-1)')
        minimum(checks, 'bitwise_root_l_l')
        arithmetic.scalar(checks, 'bitwise_root_l_r', 'NScalarInt (INTEGER ' + MAXIMUM + ')', 'PINT ' + MAXIMUM, MAXIMUM)
        arithmetic.scalar(checks, 'bitwise_root_r', 'NScalarInt (INTEGER 1)', 'PINT 1', '1')
    elif index == 1:
        bitwise(checks, 'bitwise_root', 'BITXOR', MINIMUM, MAXIMUM, '$(-1)')
        minimum(checks, 'bitwise_root_l')
        arithmetic.scalar(checks, 'bitwise_root_r', 'NScalarInt (INTEGER ' + MAXIMUM + ')', 'PINT ' + MAXIMUM, MAXIMUM)
    elif index == 2:
        arithmetic.binary(checks, 'bitwise_root', 'NExprBinaryOpPlus', 'ADD', 'PINT 0', 'PBOOL false', 'PINT 0', 'NINT 0', 'NINT 0', 'NINT 0')
        bitwise(checks, 'bitwise_root_l', 'BITAND', '2', '1', '0')
        arithmetic.constant(checks, 'bitwise_root_l_l', 'E_WARNING', '2')
        arithmetic.binary(checks, 'bitwise_root_l_r', 'NExprBinaryOpPlus', 'ADD', 'PBOOL true', 'PBOOL false', 'PINT 1', 'NINT 1', 'NINT 0', 'NINT 1')
        arithmetic.constant(checks, 'bitwise_root_l_r_l', 'true', '1')
        arithmetic.constant(checks, 'bitwise_root_l_r_r', 'false', '')
        arithmetic.constant(checks, 'bitwise_root_r', 'false', '')
    else:
        prior.bitnot(checks, 'bitwise_root', '3', '$(-4)')
        bitwise(checks, 'bitwise_root_child', 'BITOR', '1', '2', '3')
        arithmetic.scalar(checks, 'bitwise_root_child_l', 'NScalarInt (INTEGER 1)', 'PINT 1', '1')
        arithmetic.constant(checks, 'bitwise_root_child_r', 'E_WARNING', '2')
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
    watched = [Path(module.__file__) for module in (prior, prior.prior, arithmetic, runner)] + [Path(__file__)]
    before = {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.cases = cases
    runner.OUTPUTS = cases.OUTPUTS
    runner.conditions = conditions
    passed = runner.main()
    assert before == {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = 'Four actual exact-PINT binary bitwise source-state fixtures retain AND/OR/XOR, signed64 endpoint composition and explicit arithmetic-produced PINT children. Every own/child source, PINT read, range, matching precision and recursive certificate is explicit; early pure long_and/or/xor supply results without later runtime helpers or coercion. Existing bitnot/arithmetic ancestors, current REQUEST owners, supplied throw, fixed bounds and budgets retain existing laws. String-byte, non-PINT and wider owning/coercion histories remain follow-up core work.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
