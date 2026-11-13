#!/usr/bin/env python3
"""Exact integer bitwise-NOT certificates retain Warning continuations."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_integer_bitnot_special_concat_leading_key_cases as cases
import string_offset_request_base_integer_relational_special_concat_leading_key_protocol as prior

runner = prior.runner
arithmetic = prior.arithmetic


def bitnot(checks, tag, child, result):
    expression, origin = 'expression_' + tag, 'porigin_' + tag
    checks += [
        '$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')',
        expression + ' = NExprBitwiseNot ' + expression + '_child metadata_' + tag,
        '$pfshape(' + expression + ') = PFBITNOT ' + expression + '_child',
        '$origin_child((' + origin + '), [PCFIELD 0]) = (' + origin + '_child)',
        '$origin_node(S.SOURCES, ' + origin + '_child) = (' + expression + '_child)',
        '$parser_literal_at(' + expression + ', 14) = eps',
        '$compiled_read(S, ' + origin + ') = (PINT ' + result + ')',
        '$compiled_read(S, ' + origin + '_child) = (PINT ' + child + ')',
        '$compiled_precision(S, (' + origin + ')) = (14)',
        '$compiled_precision(S, (' + origin + '_child)) = (14)',
        '$long_range(' + child + r') /\ $long_range(' + result + ')',
        '$long_not(' + child + ') = ' + result,
        '$compiled_special_concat_bytes(S, ' + origin + '_child) = ($decimal_integer(' + child + '))',
        '$compiled_special_concat_bytes(S, ' + origin + ') = ($decimal_integer(' + result + '))']


def authority(index):
    checks = ['$origin_child((porigin_key), [PCFIELD 0, PCFIELD 0]) = (porigin_bitnot_root)',
              r'S.PRECISIONINI = $ptascii("17") /\ $precision_value(S) = 17']
    if index == 0:
        minimum, maximum = '$(-9223372036854775808)', '9223372036854775807'
        negative_maximum = '$(-9223372036854775807)'
        prior.relational(checks, 'bitnot_root', 'GREATEREQUAL', maximum, maximum, True)
        bitnot(checks, 'bitnot_root_l', minimum, maximum)
        arithmetic.binary(checks, 'bitnot_root_l_child', 'NExprBinaryOpMinus', 'SUBTRACT', 'PINT ' + negative_maximum, 'PINT 1', 'PINT ' + minimum, 'NINT ' + negative_maximum, 'NINT 1', 'NINT ' + minimum)
        arithmetic.binary(checks, 'bitnot_root_l_child_l', 'NExprBinaryOpMinus', 'SUBTRACT', 'PINT 0', 'PINT ' + maximum, 'PINT ' + negative_maximum, 'NINT 0', 'NINT ' + maximum, 'NINT ' + negative_maximum)
        arithmetic.scalar(checks, 'bitnot_root_l_child_l_l', 'NScalarInt (INTEGER 0)', 'PINT 0', '0')
        arithmetic.scalar(checks, 'bitnot_root_l_child_l_r', 'NScalarInt (INTEGER ' + maximum + ')', 'PINT ' + maximum, maximum)
        arithmetic.scalar(checks, 'bitnot_root_l_child_r', 'NScalarInt (INTEGER 1)', 'PINT 1', '1')
        arithmetic.scalar(checks, 'bitnot_root_r', 'NScalarInt (INTEGER ' + maximum + ')', 'PINT ' + maximum, maximum)
    elif index == 1:
        bitnot(checks, 'bitnot_root', '0', '$(-1)')
        arithmetic.scalar(checks, 'bitnot_root_child', 'NScalarInt (INTEGER 0)', 'PINT 0', '0')
    elif index == 2:
        arithmetic.binary(checks, 'bitnot_root', 'NExprBinaryOpPlus', 'ADD', 'PINT 0', 'PBOOL false', 'PINT 0', 'NINT 0', 'NINT 0', 'NINT 0')
        bitnot(checks, 'bitnot_root_l', '$(-1)', '0')
        arithmetic.binary(checks, 'bitnot_root_l_child', 'NExprBinaryOpMinus', 'SUBTRACT', 'PINT 0', 'PINT 1', 'PINT $(-1)', 'NINT 0', 'NINT 1', 'NINT $(-1)')
        arithmetic.scalar(checks, 'bitnot_root_l_child_l', 'NScalarInt (INTEGER 0)', 'PINT 0', '0')
        arithmetic.scalar(checks, 'bitnot_root_l_child_r', 'NScalarInt (INTEGER 1)', 'PINT 1', '1')
        arithmetic.constant(checks, 'bitnot_root_r', 'false', '')
    else:
        bitnot(checks, 'bitnot_root', '3', '$(-4)')
        arithmetic.scalar(checks, 'bitnot_root_child', 'NScalarInt (INTEGER 3)', 'PINT 3', '3')
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
    report['scope'] = 'Four actual exact-PINT bitwise-NOT source-state fixtures retain signed64 MIN-to-MAX complement, zero-to-minus-one, minus-one-to-zero and three-to-minus-four. Every own/child source, PINT read, range, matching precision and recursive certificate is explicit; existing early pure long_not supplies the complement without a later runtime helper. Relational/arithmetic ancestors, current REQUEST owners, supplied throw, fixed bounds and budgets retain existing laws. Non-PINT bitwise operations and wider owning/coercion histories remain follow-up core work.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
