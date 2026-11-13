#!/usr/bin/env python3
"""Exact integer-result power certificates retain Warning continuations."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_integer_power_special_concat_leading_key_cases as cases
import string_offset_request_base_short_circuit_special_concat_leading_key_protocol as prior
import string_offset_request_base_integer_shift_special_concat_leading_key_protocol as shift

runner = prior.runner
arithmetic = prior.arithmetic
unary = prior.unary
integers = shift.integers


def power(checks, tag, left, right, result):
    expression, origin = 'expression_' + tag, 'porigin_' + tag
    checks += [
        '$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')',
        expression + ' = NExprBinaryOpPow ' + expression + '_l ' + expression + '_r metadata_' + tag,
        '$pfshape(' + expression + ') = PFBINARY POWER ' + expression + '_l ' + expression + '_r',
        '$parser_literal_at(' + expression + ', 14) = eps',
        '$compiled_read(S, ' + origin + ') = (PINT ' + result + ')',
        '$compiled_precision(S, (' + origin + ')) = (14)',
        '$long_range(' + left + r') /\ $long_range(' + right + r') /\ $long_range(' + result + ')',
        '$(' + right + ' >= 0)',
        '$power_prepare(NINT ' + left + ', NINT ' + right + ') = POWERDONE (NINT ' + result + ') false',
        '$compiled_special_concat_bytes(S, ' + origin + ') = ($decimal_integer(' + result + '))']
    for field, suffix, child in ((0, '_l', left), (1, '_r', right)):
        checks += [
            '$origin_child((' + origin + '), [PCFIELD ' + str(field) + ']) = (' + origin + suffix + ')',
            '$origin_node(S.SOURCES, ' + origin + suffix + ') = (' + expression + suffix + ')',
            '$compiled_read(S, ' + origin + suffix + ') = (PINT ' + child + ')',
            '$compiled_precision(S, (' + origin + suffix + ')) = (14)',
            '$compiled_special_concat_bytes(S, ' + origin + suffix + ') = ($decimal_integer(' + child + '))']


def authority(index):
    checks = ['$origin_child((porigin_key), [PCFIELD 0, PCFIELD 0]) = (porigin_power_root)',
              r'S.PRECISIONINI = $ptascii("17") /\ $precision_value(S) = 17']
    if index == 0:
        power(checks, 'power_root', '0', '0', '1')
        arithmetic.scalar(checks, 'power_root_l', 'NScalarInt (INTEGER 0)', 'PINT 0', '0')
        arithmetic.scalar(checks, 'power_root_r', 'NScalarInt (INTEGER 0)', 'PINT 0', '0')
    elif index == 1:
        shift.shift(checks, 'power_root', 'SHIFTRIGHT', integers.MINIMUM, '63', '$(-1)')
        power(checks, 'power_root_l', integers.MINIMUM, '1', integers.MINIMUM)
        integers.minimum(checks, 'power_root_l_l')
        arithmetic.scalar(checks, 'power_root_l_r', 'NScalarInt (INTEGER 1)', 'PINT 1', '1')
        arithmetic.scalar(checks, 'power_root_r', 'NScalarInt (INTEGER 63)', 'PINT 63', '63')
    elif index == 2:
        arithmetic.binary(checks, 'power_root', 'NExprBinaryOpPlus', 'ADD', 'PINT 0', 'PBOOL false', 'PINT 0', 'NINT 0', 'NINT 0', 'NINT 0')
        power(checks, 'power_root_l', '0', '2', '0')
        arithmetic.scalar(checks, 'power_root_l_l', 'NScalarInt (INTEGER 0)', 'PINT 0', '0')
        arithmetic.constant(checks, 'power_root_l_r', 'E_WARNING', '2')
        arithmetic.constant(checks, 'power_root_r', 'false', '')
    else:
        unary.unary(checks, 'power_root', 'NEGATIVE', 'PINT 4', 'NINT 4', 'PINT $(-4)', '-4', '4')
        power(checks, 'power_root_child', '2', '2', '4')
        arithmetic.constant(checks, 'power_root_child_l', 'E_WARNING', '2')
        arithmetic.binary(checks, 'power_root_child_r', 'NExprBinaryOpPlus', 'ADD', 'PBOOL true', 'PBOOL true', 'PINT 2', 'NINT 1', 'NINT 1', 'NINT 2')
        arithmetic.constant(checks, 'power_root_child_r_l', 'true', '1')
        arithmetic.constant(checks, 'power_root_child_r_r', 'true', '1')
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
    watched = [Path(module.__file__) for module in (prior, prior.prior, shift, arithmetic, unary, runner)] + [Path(__file__)]
    before = {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.cases = cases
    runner.OUTPUTS = cases.OUTPUTS
    runner.conditions = conditions
    passed = runner.main()
    assert before == {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = 'Four actual exact-PINT integer-result power source-state fixtures retain zero exponent including0**0, safe MIN**1 under existing right shift, zero base with positive exponent and arithmetic-produced exponent2 under unaryminus. Both actual child sources/reads/certificates, all signed64 ranges, three matching precisions, nonnegative exponent and early power_prepare POWERDONE(NINT own)false are explicit. No floating result, general libm, runtime conversion or later power helper is used. Existing arithmetic/unary/shift ancestors, REQUEST owners, supplied throw, fixed bounds and budgets retain prior laws; negative exponents, overflow-to-float and mixed numeric paths remain separate core obligations.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
