#!/usr/bin/env python3
"""Exact integer shift certificates retain Warning continuations."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_integer_shift_special_concat_leading_key_cases as cases
import string_offset_request_base_integer_modulo_special_concat_leading_key_protocol as prior
import string_offset_request_base_identity_special_concat_leading_key_protocol as identity

runner = prior.runner
arithmetic = prior.arithmetic
bitnot = prior.bitnot
integers = prior.prior


def shift(checks, tag, operation, left, right, result):
    expression, origin = 'expression_' + tag, 'porigin_' + tag
    shape, helper = ('NExprBinaryOpShiftLeft', 'long_shl') if operation == 'SHIFTLEFT' else ('NExprBinaryOpShiftRight', 'long_shr')
    checks += [
        '$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')',
        expression + ' = ' + shape + ' ' + expression + '_l ' + expression + '_r metadata_' + tag,
        '$pfshape(' + expression + ') = PFBINARY ' + operation + ' ' + expression + '_l ' + expression + '_r',
        '$parser_literal_at(' + expression + ', 14) = eps',
        '$compiled_read(S, ' + origin + ') = (PINT ' + result + ')',
        '$compiled_precision(S, (' + origin + ')) = (14)',
        '$long_range(' + left + r') /\ $long_range(' + right + r') /\ $long_range(' + result + ')',
        '$(' + right + ' >= 0)',
        '$' + helper + '(' + left + ', ' + right + ') = IRESULT ' + result,
        '$compiled_special_concat_bytes(S, ' + origin + ') = ($decimal_integer(' + result + '))']
    for field, suffix, child in ((0, '_l', left), (1, '_r', right)):
        checks += [
            '$origin_child((' + origin + '), [PCFIELD ' + str(field) + ']) = (' + origin + suffix + ')',
            '$origin_node(S.SOURCES, ' + origin + suffix + ') = (' + expression + suffix + ')',
            '$compiled_read(S, ' + origin + suffix + ') = (PINT ' + child + ')',
            '$compiled_precision(S, (' + origin + suffix + ')) = (14)',
            '$compiled_special_concat_bytes(S, ' + origin + suffix + ') = ($decimal_integer(' + child + '))']


def authority(index):
    checks = ['$origin_child((porigin_key), [PCFIELD 0, PCFIELD 0]) = (porigin_shift_root)',
              r'S.PRECISIONINI = $ptascii("17") /\ $precision_value(S) = 17']
    if index == 0:
        identity.identity(checks, 'shift_root', 'IDENTICAL', 'PINT ' + integers.MINIMUM, 'PINT ' + integers.MINIMUM, True, '-9223372036854775808', '-9223372036854775808')
        shift(checks, 'shift_root_l', 'SHIFTLEFT', '1', '63', integers.MINIMUM)
        arithmetic.scalar(checks, 'shift_root_l_l', 'NScalarInt (INTEGER 1)', 'PINT 1', '1')
        arithmetic.scalar(checks, 'shift_root_l_r', 'NScalarInt (INTEGER 63)', 'PINT 63', '63')
        integers.minimum(checks, 'shift_root_r')
    elif index == 1:
        shift(checks, 'shift_root', 'SHIFTRIGHT', integers.MINIMUM, '63', '$(-1)')
        integers.minimum(checks, 'shift_root_l')
        arithmetic.scalar(checks, 'shift_root_r', 'NScalarInt (INTEGER 63)', 'PINT 63', '63')
    elif index == 2:
        arithmetic.binary(checks, 'shift_root', 'NExprBinaryOpPlus', 'ADD', 'PINT 0', 'PBOOL false', 'PINT 0', 'NINT 0', 'NINT 0', 'NINT 0')
        shift(checks, 'shift_root_l', 'SHIFTLEFT', '1', '64', '0')
        arithmetic.scalar(checks, 'shift_root_l_l', 'NScalarInt (INTEGER 1)', 'PINT 1', '1')
        arithmetic.scalar(checks, 'shift_root_l_r', 'NScalarInt (INTEGER 64)', 'PINT 64', '64')
        arithmetic.constant(checks, 'shift_root_r', 'false', '')
    else:
        bitnot.bitnot(checks, 'shift_root', '3', '$(-4)')
        shift(checks, 'shift_root_child', 'SHIFTRIGHT', '7', '1', '3')
        arithmetic.scalar(checks, 'shift_root_child_l', 'NScalarInt (INTEGER 7)', 'PINT 7', '7')
        arithmetic.binary(checks, 'shift_root_child_r', 'NExprBinaryOpPlus', 'ADD', 'PBOOL true', 'PBOOL false', 'PINT 1', 'NINT 1', 'NINT 0', 'NINT 1')
        arithmetic.constant(checks, 'shift_root_child_r_l', 'true', '1')
        arithmetic.constant(checks, 'shift_root_child_r_r', 'false', '')
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
    watched = [Path(module.__file__) for module in (prior, prior.prior, arithmetic, bitnot, identity, runner)] + [Path(__file__)]
    before = {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.cases = cases
    runner.OUTPUTS = cases.OUTPUTS
    runner.conditions = conditions
    passed = runner.main()
    assert before == {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = 'Four actual exact-PINT shift source-state fixtures retain unsigned left wrap to signed MIN under strict identity, arithmetic right sign extension, width-count zero and typed arithmetic shift counts. Every own/child source, PINT read/range, matching precision, nonnegative count and recursive certificate is explicit; early pure long_shl/long_shr supply IRESULT without later runtime helpers or coercion. Existing identity/bitnot/arithmetic ancestors, current REQUEST owners, supplied throw, fixed bounds and budgets retain existing laws. Negative-count/error and non-PINT conversion routes retain separate core obligations.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
