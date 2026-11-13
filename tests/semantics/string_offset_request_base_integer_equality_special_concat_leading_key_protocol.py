#!/usr/bin/env python3
"""Exact integer equality/spaceship certificates retain Warning histories."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_integer_equality_special_concat_leading_key_cases as cases
import string_offset_request_base_integer_shift_special_concat_leading_key_protocol as prior
import string_offset_request_base_bool_null_unary_special_concat_leading_key_protocol as unary

runner = prior.runner
arithmetic = prior.arithmetic


def comparison(checks, tag, operation, left, right, result, text):
    expression, origin = 'expression_' + tag, 'porigin_' + tag
    shape = {'EQUAL': 'NExprBinaryOpEqual', 'NOTEQUAL': 'NExprBinaryOpNotEqual',
             'SPACESHIP': 'NExprBinaryOpSpaceship'}[operation]
    reference = ('PINT $compare_int(' + left + ', ' + right + ')') if operation == 'SPACESHIP' else ('PBOOL $(' + left + (' = ' if operation == 'EQUAL' else ' =/= ') + right + ')')
    checks += [
        '$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')',
        expression + ' = ' + shape + ' ' + expression + '_l ' + expression + '_r metadata_' + tag,
        '$pfshape(' + expression + ') = PFBINARY ' + operation + ' ' + expression + '_l ' + expression + '_r',
        '$parser_literal_at(' + expression + ', 14) = eps',
        '$compiled_read(S, ' + origin + ') = (' + result + ')',
        '$compiled_precision(S, (' + origin + ')) = (14)',
        '$long_range(' + left + r') /\ $long_range(' + right + ')',
        '$compiled_read(S, ' + origin + ') = (' + reference + ')',
        '$echo_value(' + result + ') = $ptascii(' + json.dumps(text) + ')',
        '$compiled_special_concat_bytes(S, ' + origin + ') = ($ptascii(' + json.dumps(text) + '))']
    for field, suffix, child in ((0, '_l', left), (1, '_r', right)):
        checks += [
            '$origin_child((' + origin + '), [PCFIELD ' + str(field) + ']) = (' + origin + suffix + ')',
            '$origin_node(S.SOURCES, ' + origin + suffix + ') = (' + expression + suffix + ')',
            '$compiled_read(S, ' + origin + suffix + ') = (PINT ' + child + ')',
            '$compiled_precision(S, (' + origin + suffix + ')) = (14)',
            '$compiled_special_concat_bytes(S, ' + origin + suffix + ') = ($decimal_integer(' + child + '))']


def authority(index):
    checks = ['$origin_child((porigin_key), [PCFIELD 0, PCFIELD 0]) = (porigin_equality_root)',
              r'S.PRECISIONINI = $ptascii("17") /\ $precision_value(S) = 17']
    if index == 0:
        comparison(checks, 'equality_root', 'EQUAL', '2', '2', 'PBOOL true', '1')
        arithmetic.binary(checks, 'equality_root_l', 'NExprBinaryOpPlus', 'ADD', 'PINT 2', 'PBOOL false', 'PINT 2', 'NINT 2', 'NINT 0', 'NINT 2')
        arithmetic.constant(checks, 'equality_root_l_l', 'E_WARNING', '2')
        arithmetic.constant(checks, 'equality_root_l_r', 'false', '')
        arithmetic.constant(checks, 'equality_root_r', 'E_WARNING', '2')
    elif index == 1:
        comparison(checks, 'equality_root', 'SPACESHIP', '0', '2', 'PINT $(-1)', '-1')
        arithmetic.scalar(checks, 'equality_root_l', 'NScalarInt (INTEGER 0)', 'PINT 0', '0')
        arithmetic.constant(checks, 'equality_root_r', 'E_WARNING', '2')
    elif index == 2:
        arithmetic.binary(checks, 'equality_root', 'NExprBinaryOpPlus', 'ADD', 'PBOOL false', 'PBOOL false', 'PINT 0', 'NINT 0', 'NINT 0', 'NINT 0')
        comparison(checks, 'equality_root_l', 'NOTEQUAL', '2', '2', 'PBOOL false', '')
        arithmetic.constant(checks, 'equality_root_l_l', 'E_WARNING', '2')
        arithmetic.constant(checks, 'equality_root_l_r', 'E_WARNING', '2')
        arithmetic.constant(checks, 'equality_root_r', 'false', '')
    else:
        unary.unary(checks, 'equality_root', 'NEGATIVE', 'PINT 4', 'NINT 4', 'PINT $(-4)', '-4', '4')
        arithmetic.binary(checks, 'equality_root_child', 'NExprBinaryOpMul', 'MULTIPLY', 'PBOOL true', 'PINT 4', 'PINT 4', 'NINT 1', 'NINT 4', 'NINT 4')
        comparison(checks, 'equality_root_child_l', 'NOTEQUAL', '2', '1', 'PBOOL true', '1')
        arithmetic.constant(checks, 'equality_root_child_l_l', 'E_WARNING', '2')
        arithmetic.scalar(checks, 'equality_root_child_l_r', 'NScalarInt (INTEGER 1)', 'PINT 1', '1')
        arithmetic.binary(checks, 'equality_root_child_r', 'NExprBinaryOpPlus', 'ADD', 'PINT 2', 'PINT 2', 'PINT 4', 'NINT 2', 'NINT 2', 'NINT 4')
        arithmetic.constant(checks, 'equality_root_child_r_l', 'E_WARNING', '2')
        arithmetic.constant(checks, 'equality_root_child_r_r', 'E_WARNING', '2')
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
    report['scope'] = 'Four actual exact-PINT EQUAL/NOTEQUAL/SPACESHIP source-state fixtures retain computed integer equality, negative integer order and Boolean false/true composition. Every own/child source, PINT read/range, matching precision and recursive certificate is explicit. Direct integer equality predicates and early compare_int preserve Boolean versus integer result types and echo bytes without weak coercion or later helpers. Existing unary/arithmetic ancestors, current REQUEST owners, supplied throw, fixed bounds and budgets retain existing laws; mixed comparisons retain separate core obligations.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
