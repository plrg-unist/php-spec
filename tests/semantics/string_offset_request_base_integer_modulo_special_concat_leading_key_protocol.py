#!/usr/bin/env python3
"""Exact integer modulo certificates retain Warning continuations."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_integer_modulo_special_concat_leading_key_cases as cases
import string_offset_request_base_integer_bitwise_special_concat_leading_key_protocol as prior

runner = prior.runner
arithmetic = prior.arithmetic
bitnot = prior.prior


def modulo(checks, tag, left, right, result):
    expression, origin = 'expression_' + tag, 'porigin_' + tag
    checks += [
        '$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')',
        expression + ' = NExprBinaryOpMod ' + expression + '_l ' + expression + '_r metadata_' + tag,
        '$pfshape(' + expression + ') = PFBINARY MODULO ' + expression + '_l ' + expression + '_r',
        '$parser_literal_at(' + expression + ', 14) = eps',
        '$compiled_read(S, ' + origin + ') = (PINT ' + result + ')',
        '$compiled_precision(S, (' + origin + ')) = (14)',
        '$long_range(' + left + r') /\ $long_range(' + right + r') /\ $long_range(' + result + ')',
        right + ' =/= 0',
        '$long_mod(' + left + ', ' + right + ') = IRESULT ' + result,
        '$compiled_special_concat_bytes(S, ' + origin + ') = ($decimal_integer(' + result + '))']
    for field, suffix, child in ((0, '_l', left), (1, '_r', right)):
        checks += [
            '$origin_child((' + origin + '), [PCFIELD ' + str(field) + ']) = (' + origin + suffix + ')',
            '$origin_node(S.SOURCES, ' + origin + suffix + ') = (' + expression + suffix + ')',
            '$compiled_read(S, ' + origin + suffix + ') = (PINT ' + child + ')',
            '$compiled_precision(S, (' + origin + suffix + ')) = (14)',
            '$compiled_special_concat_bytes(S, ' + origin + suffix + ') = ($decimal_integer(' + child + '))']


def authority(index):
    checks = ['$origin_child((porigin_key), [PCFIELD 0, PCFIELD 0]) = (porigin_modulo_root)',
              r'S.PRECISIONINI = $ptascii("17") /\ $precision_value(S) = 17']
    if index == 0:
        modulo(checks, 'modulo_root', '5', '2', '1')
        arithmetic.scalar(checks, 'modulo_root_l', 'NScalarInt (INTEGER 5)', 'PINT 5', '5')
        arithmetic.constant(checks, 'modulo_root_r', 'E_WARNING', '2')
    elif index == 1:
        modulo(checks, 'modulo_root', '$(-5)', '2', '$(-1)')
        bitnot.bitnot(checks, 'modulo_root_l', '4', '$(-5)')
        arithmetic.scalar(checks, 'modulo_root_l_child', 'NScalarInt (INTEGER 4)', 'PINT 4', '4')
        arithmetic.constant(checks, 'modulo_root_r', 'E_WARNING', '2')
    elif index == 2:
        arithmetic.binary(checks, 'modulo_root', 'NExprBinaryOpPlus', 'ADD', 'PINT 0', 'PBOOL false', 'PINT 0', 'NINT 0', 'NINT 0', 'NINT 0')
        modulo(checks, 'modulo_root_l', prior.MINIMUM, '$(-1)', '0')
        prior.minimum(checks, 'modulo_root_l_l')
        arithmetic.binary(checks, 'modulo_root_l_r', 'NExprBinaryOpMinus', 'SUBTRACT', 'PINT 0', 'PINT 1', 'PINT $(-1)', 'NINT 0', 'NINT 1', 'NINT $(-1)')
        arithmetic.scalar(checks, 'modulo_root_l_r_l', 'NScalarInt (INTEGER 0)', 'PINT 0', '0')
        arithmetic.scalar(checks, 'modulo_root_l_r_r', 'NScalarInt (INTEGER 1)', 'PINT 1', '1')
        arithmetic.constant(checks, 'modulo_root_r', 'false', '')
    else:
        bitnot.bitnot(checks, 'modulo_root', '3', '$(-4)')
        modulo(checks, 'modulo_root_child', '7', '4', '3')
        arithmetic.scalar(checks, 'modulo_root_child_l', 'NScalarInt (INTEGER 7)', 'PINT 7', '7')
        arithmetic.binary(checks, 'modulo_root_child_r', 'NExprBinaryOpPlus', 'ADD', 'PINT 2', 'PINT 2', 'PINT 4', 'NINT 2', 'NINT 2', 'NINT 4')
        arithmetic.constant(checks, 'modulo_root_child_r_l', 'E_WARNING', '2')
        arithmetic.constant(checks, 'modulo_root_child_r_r', 'E_WARNING', '2')
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
    watched = [Path(module.__file__) for module in (prior, prior.prior, arithmetic, bitnot, runner)] + [Path(__file__)]
    before = {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.cases = cases
    runner.OUTPUTS = cases.OUTPUTS
    runner.conditions = conditions
    passed = runner.main()
    assert before == {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = 'Four actual exact-PINT modulo source-state fixtures retain positive/negative dividend remainders, MIN modulo minus-one and computed nonzero divisors. Every own/child source, PINT read/range, matching precision, nonzero divisor and recursive certificate is explicit; early pure long_mod supplies IRESULT without later runtime helpers or coercion. Existing bitnot/arithmetic ancestors, current REQUEST owners, supplied throw, fixed bounds and budgets retain existing laws. Zero/error and non-PINT conversion routes remain outside this admission and retain their separate runtime obligations.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
