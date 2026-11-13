#!/usr/bin/env python3
"""NaN strict identity uses genuine VALUE facts without operand conversion."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_nan_identity_special_concat_leading_key_cases as cases
import string_offset_request_base_numeric_comparison_special_concat_leading_key_protocol as prior
import string_offset_request_base_nan_comparison_special_concat_leading_key_protocol as nan
import string_offset_request_base_string_bitwise_special_concat_leading_key_protocol as strings

runner, arithmetic, unary = prior.runner, prior.arithmetic, prior.unary
NOTNUMBER = ('PFLOAT ' + nan.NAN, None)


def identity(checks, tag, operation, left, right, result):
    expression, origin = 'expression_' + tag, 'porigin_' + tag
    shape = 'Identical' if operation == 'IDENTICAL' else 'NotIdentical'
    value, text = 'PBOOL ' + str(result).lower(), '1' if result else ''
    checks += [
        '$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')',
        expression + ' = NExprBinaryOp' + shape + ' ' + expression + '_l ' + expression + '_r metadata_' + tag,
        '$pfshape(' + expression + ') = PFBINARY ' + operation + ' ' + expression + '_l ' + expression + '_r',
        '$parser_literal_at(' + expression + ', 14) = eps',
        '$compiled_read(S, ' + origin + ') = (' + value + ')',
        '$compiled_precision(S, (' + origin + ')) = (14)',
        '$strict_identical(' + left[0] + ', ' + right[0] + ') = false',
        '$echo_value(' + value + ') = $ptascii(' + json.dumps(text) + ')',
        '$compiled_special_concat_bytes(S, ' + origin + ') = ($ptascii(' + json.dumps(text) + '))']
    for field, suffix, (child, payload) in ((0, '_l', left), (1, '_r', right)):
        checks += [
            '$origin_child((' + origin + '), [PCFIELD ' + str(field) + ']) = (' + origin + suffix + ')',
            '$origin_node(S.SOURCES, ' + origin + suffix + ') = (' + expression + suffix + ')',
            '$compiled_read(S, ' + origin + suffix + ') = (' + child + ')',
            '$compiled_precision(S, (' + origin + suffix + ')) = (14)']
        if payload is None:
            nan.nan(checks, tag + suffix)
            checks += ['$compiled_comparison_number(S, ' + origin + suffix + ') = (NFLOAT ' + nan.NAN + ')',
                       '$(' + nan.NAN + ' < 18446744073709551616)',
                       '$fparts_nan($float_decode(' + nan.NAN + '))',
                       '$compiled_special_concat_bytes(S, ' + origin + suffix + ') = eps',
                       '$parser_literal_text_at(' + child + ', 14) = eps',
                       '$number_text(NFLOAT ' + nan.NAN + ', 14) = ($ptascii("NAN"), true)']
        else:
            checks += ['$compiled_special_concat_bytes(S, ' + origin + suffix + ') = ($ptascii(' + json.dumps(payload) + '))']
            if child.startswith('PSTRING '):
                strings.string(checks, tag + suffix, payload.encode())
                checks += ['$compiled_comparison_number(S, ' + origin + suffix + ') = eps']
            else:
                prior.scalar(checks, tag + suffix, '4609434218613702656', payload)
                checks += ['$compiled_comparison_number(S, ' + origin + suffix + ') = (NFLOAT 4609434218613702656)',
                           '$compiled_order_number(' + child + ') = (NFLOAT 4609434218613702656)',
                           '$number_text(NFLOAT 4609434218613702656, 14) = ($ptascii("1.5"), false)']


def authority(index):
    checks = ['$origin_child((porigin_key), [PCFIELD 0, PCFIELD 0]) = (porigin_nan_identity_root)',
              r'S.PRECISIONINI = $ptascii("17") /\ $precision_value(S) = 17']
    if index == 0:
        identity(checks, 'nan_identity_root', 'NOTIDENTICAL', NOTNUMBER, NOTNUMBER, True)
    elif index == 1:
        unary.unary(checks, 'nan_identity_root', 'NEGATIVE', 'PBOOL true', 'NINT 1', 'PINT $(-1)', '-1', '1')
        identity(checks, 'nan_identity_root_child', 'NOTIDENTICAL', NOTNUMBER, ('PFLOAT 4609434218613702656', '1.5'), True)
    elif index == 2:
        arithmetic.binary(checks, 'nan_identity_root', 'NExprBinaryOpPlus', 'ADD', 'PBOOL false', 'PBOOL false', 'PINT 0', 'NINT 0', 'NINT 0', 'NINT 0')
        identity(checks, 'nan_identity_root_l', 'IDENTICAL', NOTNUMBER, NOTNUMBER, False)
        arithmetic.constant(checks, 'nan_identity_root_r', 'false', '')
    else:
        unary.unary(checks, 'nan_identity_root', 'NEGATIVE', 'PINT 4', 'NINT 4', 'PINT $(-4)', '-4', '4')
        arithmetic.binary(checks, 'nan_identity_root_child', 'NExprBinaryOpMul', 'MULTIPLY', 'PBOOL true', 'PINT 4', 'PINT 4', 'NINT 1', 'NINT 4', 'NINT 4')
        identity(checks, 'nan_identity_root_child_l', 'NOTIDENTICAL', ('PSTRING ($ptascii("NAN"))', 'NAN'), NOTNUMBER, True)
        arithmetic.binary(checks, 'nan_identity_root_child_r', 'NExprBinaryOpPlus', 'ADD', 'PINT 2', 'PINT 2', 'PINT 4', 'NINT 2', 'NINT 2', 'NINT 4')
        arithmetic.constant(checks, 'nan_identity_root_child_r_l', 'E_WARNING', '2')
        arithmetic.constant(checks, 'nan_identity_root_child_r_r', 'E_WARNING', '2')
        checks += ['$type_bytes(PSTRING ($ptascii("NAN"))) =/= $type_bytes(PFLOAT ' + nan.NAN + ')']
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
    watched = [Path(module.__file__) for module in (prior, nan, strings, strings.prior, arithmetic, unary, runner)] + [Path(__file__)]
    before = {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.cases, runner.OUTPUTS, runner.conditions = cases, cases.OUTPUTS, conditions
    passed = runner.main()
    assert before == {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = 'Four authentic strict NaN identity fixtures retain actual parent/child sources and reads, three matching compile14 precisions despite live17 and genuine valid64 ConstFetch NaN VALUE with BYTE absent/format notice true. Existing strict_identical is false even for two equal NaN bit patterns; NOTIDENTICAL returns true without operand conversion. Quiet numeric or exact raw PSTRING partners retain their BYTE proof, including distinct raw bytes NAN versus NaN FLOAT. Unary/arithmetic ancestors receive Boolean/integer outputs only. Existing REQUEST owners, saved throw, fixed bounds and budgets retain their laws. No arithmetic NaN producer, literal NaN value provenance, runtime carrier/owning or held Source47 expansion.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
