#!/usr/bin/env python3
"""Folded quiet FLOAT logical facts preserve evaluated and dead RHS domains."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_float_logical_special_concat_leading_key_cases as cases
import string_offset_request_base_nan_comparison_special_concat_leading_key_protocol as prior
import string_offset_request_base_short_circuit_special_concat_leading_key_protocol as logical
import string_offset_request_base_xor_special_concat_leading_key_protocol as xor
import string_offset_request_base_boolnot_special_concat_leading_key_protocol as boolnot

runner, arithmetic, unary = prior.runner, prior.arithmetic, prior.unary
HALF3 = prior.HALF3


def scalar(checks, tag, bits, text, truth):
    prior.prior.scalar(checks, tag, bits, text)
    checks += ['$(' + bits + ' < 18446744073709551616)',
               '~$fparts_nan($float_decode(' + bits + '))',
               '$compiled_order_number(PFLOAT ' + bits + ') = (NFLOAT ' + bits + ')',
               '$number_bool(NFLOAT ' + bits + ') = (' + str(truth).lower() + ', false)']


def short(checks, tag, form, left, left_truth, right=None):
    logical.short(checks, tag, form, left, left_truth, right)
    if left_truth == form.endswith('Or'):
        checks[-8:-5] = [
            'expression_' + tag + '_r = NExprVariable (BYTES text_' + tag + '_dead) metadata_' + tag + '_dead',
            '$base64(text_' + tag + '_dead) = $ptascii("missing")']


def authority(index):
    checks = ['$origin_child((porigin_key), [PCFIELD 0, PCFIELD 0]) = (porigin_logical_root)',
              r'S.PRECISIONINI = $ptascii("17") /\ $precision_value(S) = 17']
    half3 = 'PFLOAT ' + HALF3
    if index == 0:
        boolnot.boolnot(checks, 'logical_root', 'PBOOL false', False)
        short(checks, 'logical_root_child', 'BooleanAnd', 'PBOOL true', True, ('PFLOAT 0', False))
        short(checks, 'logical_root_child_l', 'BooleanOr', 'PFLOAT 0', False, (half3, True))
        scalar(checks, 'logical_root_child_l_l', '0', '0', False)
        scalar(checks, 'logical_root_child_l_r', HALF3, '1.5', True)
        scalar(checks, 'logical_root_child_r', '0', '0', False)
    elif index == 1:
        unary.unary(checks, 'logical_root', 'NEGATIVE', 'PINT 1', 'NINT 1', 'PINT $(-1)', '-1', '1')
        arithmetic.binary(checks, 'logical_root_child', 'NExprBinaryOpPlus', 'ADD', 'PBOOL true', 'PBOOL false', 'PINT 1', 'NINT 1', 'NINT 0', 'NINT 1')
        xor.xor(checks, 'logical_root_child_l', half3, 'PFLOAT 0', True, False, '1.5', '0')
        scalar(checks, 'logical_root_child_l_l', HALF3, '1.5', True)
        scalar(checks, 'logical_root_child_l_r', '0', '0', False)
        arithmetic.constant(checks, 'logical_root_child_r', 'false', '')
    elif index == 2:
        arithmetic.binary(checks, 'logical_root', 'NExprBinaryOpPlus', 'ADD', 'PBOOL false', 'PBOOL false', 'PINT 0', 'NINT 0', 'NINT 0', 'NINT 0')
        short(checks, 'logical_root_l', 'LogicalAnd', 'PFLOAT 0', False)
        scalar(checks, 'logical_root_l_l', '0', '0', False)
        arithmetic.constant(checks, 'logical_root_r', 'false', '')
    else:
        unary.unary(checks, 'logical_root', 'NEGATIVE', 'PINT 4', 'NINT 4', 'PINT $(-4)', '-4', '4')
        arithmetic.binary(checks, 'logical_root_child', 'NExprBinaryOpMul', 'MULTIPLY', 'PBOOL true', 'PINT 4', 'PINT 4', 'NINT 1', 'NINT 4', 'NINT 4')
        short(checks, 'logical_root_child_l', 'BooleanAnd', 'PBOOL true', True, ('PBOOL true', True))
        short(checks, 'logical_root_child_l_l', 'BooleanAnd', half3, True, ('PBOOL true', True))
        scalar(checks, 'logical_root_child_l_l_l', HALF3, '1.5', True)
        short(checks, 'logical_root_child_l_l_r', 'LogicalOr', half3, True)
        scalar(checks, 'logical_root_child_l_l_r_l', HALF3, '1.5', True)
        short(checks, 'logical_root_child_l_r', 'BooleanOr', 'PFLOAT 0', False, (half3, True))
        scalar(checks, 'logical_root_child_l_r_l', '0', '0', False)
        scalar(checks, 'logical_root_child_l_r_r', HALF3, '1.5', True)
        arithmetic.binary(checks, 'logical_root_child_r', 'NExprBinaryOpPlus', 'ADD', 'PINT 2', 'PINT 2', 'PINT 4', 'NINT 2', 'NINT 2', 'NINT 4')
        arithmetic.constant(checks, 'logical_root_child_r_l', 'E_WARNING', '2')
        arithmetic.constant(checks, 'logical_root_child_r_r', 'E_WARNING', '2')
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
    watched = [Path(module.__file__) for module in (prior, prior.prior, logical, xor, boolnot, arithmetic, unary, runner)] + [Path(__file__)]
    before = {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.cases, runner.OUTPUTS, runner.conditions = cases, cases.OUTPUTS, conditions
    passed = runner.main()
    assert before == {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = 'Four actual quiet FLOAT logical fixtures cover XOR and Boolean/Logical AND/OR, including finite0/1.5 evaluated truth and decisive keyword branches with missing RHS unexecuted. Every evaluated child has actual source/read/recursive BYTE and matching precision; float bits are valid64/nonNaN with number_bool pendingflagfalse. Dead RHS has authentic source and no compiled read/BYTE certificate. Existing NOT receives a Boolean result only: target !FLOAT remains unfolded and outside this certificate. Existing unary/arithmetic ancestors, REQUEST owners, saved throw, fixed bounds and budgets retain their laws. NaN Boolean diagnostics, owning/uncertified inputs and wider producers remain separate core work; Source47 stays held.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
