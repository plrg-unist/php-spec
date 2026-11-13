#!/usr/bin/env python3
"""Strict scalar identity certificates retain actual Warning continuations."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_identity_special_concat_leading_key_cases as cases
import string_offset_request_base_boolnot_special_concat_leading_key_protocol as prior

runner = prior.runner
arithmetic = prior.arithmetic


def identity(checks, tag, operation, left, right, result, left_text, right_text):
    expression, origin = 'expression_' + tag, 'porigin_' + tag
    value, text = ('PBOOL true', '1') if result else ('PBOOL false', '')
    identical = result if operation == 'IDENTICAL' else not result
    checks += [
        '$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')',
        expression + ' = ' + ('NExprBinaryOpIdentical' if operation == 'IDENTICAL' else 'NExprBinaryOpNotIdentical') + ' ' + expression + '_l ' + expression + '_r metadata_' + tag,
        '$pfshape(' + expression + ') = PFBINARY ' + operation + ' ' + expression + '_l ' + expression + '_r',
        '$parser_literal_at(' + expression + ', 14) = eps',
        '$compiled_read(S, ' + origin + ') = (' + value + ')',
        '$compiled_precision(S, (' + origin + ')) = (14)',
        '$strict_identical(' + left + ', ' + right + ') = ' + str(identical).lower(),
        '$compiled_special_concat_bytes(S, ' + origin + ') = ($ptascii(' + json.dumps(text) + '))']
    for field, suffix, child, child_text in ((0, '_l', left, left_text), (1, '_r', right, right_text)):
        checks += [
            '$origin_child((' + origin + '), [PCFIELD ' + str(field) + ']) = (' + origin + suffix + ')',
            '$origin_node(S.SOURCES, ' + origin + suffix + ') = (' + expression + suffix + ')',
            '$compiled_read(S, ' + origin + suffix + ') = (' + child + ')',
            '$compiled_precision(S, (' + origin + suffix + ')) = (14)',
            '$compiled_special_concat_bytes(S, ' + origin + suffix + ') = ($ptascii(' + json.dumps(child_text) + '))']


def float_unary(checks, tag, operation, result, text):
    expression, origin = 'expression_' + tag, 'porigin_' + tag
    checks += [
        expression + ' = ' + ('NExprUnaryPlus' if operation == 'POSITIVE' else 'NExprUnaryMinus') + ' ' + expression + '_child metadata_' + tag,
        '$origin_child((' + origin + '), [PCFIELD 0]) = (' + origin + '_child)',
        '$origin_node(S.SOURCES, ' + origin + '_child) = (' + expression + '_child)',
        '$compiled_read(S, ' + origin + '_child) = (PFLOAT 0)',
        '$compiled_precision(S, (' + origin + '_child)) = (14)',
        '$parser_literal_at(' + expression + '_child, 14) = (PFLOAT 0)',
        '$unary_apply(S, ' + operation + ', PFLOAT 0, 0) = S[.RESULT = KNOWN (' + result + ')]',
        '$compiled_special_concat_bytes(S, ' + origin + ') = ($ptascii(' + json.dumps(text) + '))']
    payload = 'text_float_' + tag
    arithmetic.scalar(checks, tag + '_child', 'NScalarFloat (FLOAT ' + payload + ')', 'PFLOAT 0', '0')
    checks += ['$hex_bits(' + payload + ', 0) = 0']


def authority(index):
    checks = ['$origin_child((porigin_key), [PCFIELD 0, PCFIELD 0]) = (porigin_identity_root)',
              r'S.PRECISIONINI = $ptascii("17") /\ $precision_value(S) = 17']
    if index == 0:
        prior.boolnot(checks, 'identity_root', 'PBOOL false', False)
        identity(checks, 'identity_root_child', 'IDENTICAL', 'PSTRING ($ptascii("0"))', 'PINT 0', False, '0', '0')
        arithmetic.scalar(checks, 'identity_root_child_l', 'NScalarString (BYTES text_identity_zero)', 'PSTRING ($ptascii("0"))', '0')
        arithmetic.scalar(checks, 'identity_root_child_r', 'NScalarInt (INTEGER 0)', 'PINT 0', '0')
    elif index == 1:
        prior.prior.unary(checks, 'identity_root', 'NEGATIVE', 'PBOOL true', 'NINT 1', 'PINT $(-1)', '-1', '1')
        identity(checks, 'identity_root_child', 'NOTIDENTICAL', 'PINT 0', 'PBOOL false', True, '0', '')
        arithmetic.scalar(checks, 'identity_root_child_l', 'NScalarInt (INTEGER 0)', 'PINT 0', '0')
        arithmetic.constant(checks, 'identity_root_child_r', 'false', '')
    elif index == 2:
        arithmetic.binary(checks, 'identity_root', 'NExprBinaryOpPlus', 'ADD', 'PBOOL false', 'PBOOL false', 'PINT 0', 'NINT 0', 'NINT 0', 'NINT 0')
        identity(checks, 'identity_root_l', 'IDENTICAL', 'PINT 1', 'PBOOL true', False, '1', '1')
        arithmetic.scalar(checks, 'identity_root_l_l', 'NScalarInt (INTEGER 1)', 'PINT 1', '1')
        arithmetic.constant(checks, 'identity_root_l_r', 'true', '1')
        arithmetic.constant(checks, 'identity_root_r', 'false', '')
    else:
        prior.prior.unary(checks, 'identity_root', 'NEGATIVE', 'PINT 4', 'NINT 4', 'PINT $(-4)', '-4', '4')
        arithmetic.binary(checks, 'identity_root_child', 'NExprBinaryOpMul', 'MULTIPLY', 'PBOOL true', 'PINT 4', 'PINT 4', 'NINT 1', 'NINT 4', 'NINT 4')
        identity(checks, 'identity_root_child_l', 'IDENTICAL', 'PFLOAT 0', 'PFLOAT 9223372036854775808', True, '0', '-0')
        float_unary(checks, 'identity_root_child_l_l', 'POSITIVE', 'PFLOAT 0', '0')
        float_unary(checks, 'identity_root_child_l_r', 'NEGATIVE', 'PFLOAT 9223372036854775808', '-0')
        arithmetic.binary(checks, 'identity_root_child_r', 'NExprBinaryOpPlus', 'ADD', 'PINT 2', 'PINT 2', 'PINT 4', 'NINT 2', 'NINT 2', 'NINT 4')
        arithmetic.constant(checks, 'identity_root_child_r_l', 'E_WARNING', '2')
        arithmetic.constant(checks, 'identity_root_child_r_r', 'E_WARNING', '2')
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
    report['scope'] = 'Four actual strict scalar identity source-state fixtures keep original operand types and float bits. Typed string/int/bool differences and signed float zero use the existing strict predicate, with no weak or text coercion. Every own source/read/precision and child certificate is checked, including literal facts established by the prelaw frontiers. Boolean-not/unary/arithmetic ancestors, current REQUEST owners, supplied throw, fixed bounds and budgets retain their existing laws.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
