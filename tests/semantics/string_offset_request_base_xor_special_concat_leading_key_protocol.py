#!/usr/bin/env python3
"""Quiet non-float XOR certificates retain actual Warning continuations."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_xor_special_concat_leading_key_cases as cases
import string_offset_request_base_identity_special_concat_leading_key_protocol as prior

runner = prior.runner
arithmetic = prior.arithmetic


def xor(checks, tag, left, right, left_truth, right_truth, left_text, right_text):
    expression, origin = 'expression_' + tag, 'porigin_' + tag
    result = left_truth != right_truth
    value, text = ('PBOOL true', '1') if result else ('PBOOL false', '')
    checks += [
        '$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')',
        expression + ' = NExprBinaryOpLogicalXor ' + expression + '_l ' + expression + '_r metadata_' + tag,
        '$pfshape(' + expression + ') = PFBINARY LOGICALXOR ' + expression + '_l ' + expression + '_r',
        '$parser_literal_at(' + expression + ', 14) = eps',
        '$compiled_read(S, ' + origin + ') = (' + value + ')',
        '$compiled_precision(S, (' + origin + ')) = (14)',
        '$truth(S, ' + left + ') = ' + str(left_truth).lower(),
        '$truth(S, ' + right + ') = ' + str(right_truth).lower(),
        '$binary_apply(S, LOGICALXOR, ' + left + ', ' + right + ', 0) = S[.RESULT = KNOWN (' + value + ')]',
        '$compiled_special_concat_bytes(S, ' + origin + ') = ($ptascii(' + json.dumps(text) + '))']
    for field, suffix, child, child_text in ((0, '_l', left, left_text), (1, '_r', right, right_text)):
        checks += [
            '$origin_child((' + origin + '), [PCFIELD ' + str(field) + ']) = (' + origin + suffix + ')',
            '$origin_node(S.SOURCES, ' + origin + suffix + ') = (' + expression + suffix + ')',
            '$compiled_read(S, ' + origin + suffix + ') = (' + child + ')',
            '$compiled_precision(S, (' + origin + suffix + ')) = (14)',
            '$compiled_special_concat_bytes(S, ' + origin + suffix + ') = ($ptascii(' + json.dumps(child_text) + '))']


def authority(index):
    checks = ['$origin_child((porigin_key), [PCFIELD 0, PCFIELD 0]) = (porigin_xor_root)',
              r'S.PRECISIONINI = $ptascii("17") /\ $precision_value(S) = 17']
    if index == 0:
        xor(checks, 'xor_root', 'PINT 0', 'PSTRING ($ptascii("1tail"))', False, True, '0', '1tail')
        arithmetic.scalar(checks, 'xor_root_l', 'NScalarInt (INTEGER 0)', 'PINT 0', '0')
        arithmetic.scalar(checks, 'xor_root_r', 'NScalarString (BYTES text_xor_text)', 'PSTRING ($ptascii("1tail"))', '1tail')
        checks += ['$coerce_number(PSTRING ($ptascii("1tail"))) = COERCED (NINT 1) true']
    elif index == 1:
        prior.prior.prior.unary(checks, 'xor_root', 'NEGATIVE', 'PBOOL true', 'NINT 1', 'PINT $(-1)', '-1', '1')
        xor(checks, 'xor_root_child', 'PBOOL true', 'PNULL', True, False, '1', '')
        arithmetic.constant(checks, 'xor_root_child_l', 'true', '1')
        arithmetic.constant(checks, 'xor_root_child_r', 'null', '')
    elif index == 2:
        arithmetic.binary(checks, 'xor_root', 'NExprBinaryOpPlus', 'ADD', 'PBOOL false', 'PBOOL false', 'PINT 0', 'NINT 0', 'NINT 0', 'NINT 0')
        xor(checks, 'xor_root_l', 'PINT 1', 'PBOOL true', True, True, '1', '1')
        arithmetic.scalar(checks, 'xor_root_l_l', 'NScalarInt (INTEGER 1)', 'PINT 1', '1')
        arithmetic.constant(checks, 'xor_root_l_r', 'true', '1')
        arithmetic.constant(checks, 'xor_root_r', 'false', '')
    else:
        prior.prior.prior.unary(checks, 'xor_root', 'NEGATIVE', 'PINT 4', 'NINT 4', 'PINT $(-4)', '-4', '4')
        arithmetic.binary(checks, 'xor_root_child', 'NExprBinaryOpMul', 'MULTIPLY', 'PBOOL true', 'PINT 4', 'PINT 4', 'NINT 1', 'NINT 4', 'NINT 4')
        xor(checks, 'xor_root_child_l', 'PSTRING ($ptascii("0"))', 'PBOOL true', False, True, '0', '1')
        prior.prior.strings.concat(checks, 'xor_root_child_l_l', '0', 'false', 'PBOOL false', '')
        prior.identity(checks, 'xor_root_child_l_r', 'IDENTICAL', 'PINT 1', 'PINT 1', True, '1', '1')
        arithmetic.scalar(checks, 'xor_root_child_l_r_l', 'NScalarInt (INTEGER 1)', 'PINT 1', '1')
        arithmetic.scalar(checks, 'xor_root_child_l_r_r', 'NScalarInt (INTEGER 1)', 'PINT 1', '1')
        arithmetic.binary(checks, 'xor_root_child_r', 'NExprBinaryOpPlus', 'ADD', 'PINT 2', 'PINT 2', 'PINT 4', 'NINT 2', 'NINT 2', 'NINT 4')
        arithmetic.constant(checks, 'xor_root_child_r_l', 'E_WARNING', '2')
        arithmetic.constant(checks, 'xor_root_child_r_r', 'E_WARNING', '2')
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
    report['scope'] = 'Four actual non-float XOR source-state fixtures retain int/bool/null/string truth, including truthy leading-number text without numeric coercion, a zero-string CONCAT and a recursively certified strict identity. Every own source/read/precision and both child certificates are explicit. Unary/arithmetic ancestors, current REQUEST owners, supplied throw, fixed bounds and budgets retain their existing laws. Float/owning/uncertified children and other operators remain follow-up work.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
