#!/usr/bin/env python3
"""Nonfloat logical certificates distinguish live and skipped source operands."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_short_circuit_special_concat_leading_key_cases as cases
import string_offset_request_base_integer_equality_special_concat_leading_key_protocol as prior
import string_offset_request_base_bool_null_unary_special_concat_leading_key_protocol as unary

runner = prior.runner
arithmetic = prior.arithmetic


def short(checks, tag, form, left, left_truth, right=None):
    expression, origin = 'expression_' + tag, 'porigin_' + tag
    b_or = form.endswith('Or')
    skipped = left_truth == b_or
    result = b_or if skipped else right[1]
    value, text = ('PBOOL true', '1') if result else ('PBOOL false', '')
    checks += [
        '$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')',
        expression + ' = NExprBinaryOp' + form + ' ' + expression + '_l ' + expression + '_r metadata_' + tag,
        '$pfshape(' + expression + ') = PFSHORT ' + str(b_or).lower() + ' ' + expression + '_l ' + expression + '_r',
        '$parser_literal_at(' + expression + ', 14) = eps',
        '$compiled_read(S, ' + origin + ') = (' + value + ')',
        '$compiled_precision(S, (' + origin + ')) = (14)',
        '$origin_child((' + origin + '), [PCFIELD 0]) = (' + origin + '_l)',
        '$origin_child((' + origin + '), [PCFIELD 1]) = (' + origin + '_r)',
        '$origin_node(S.SOURCES, ' + origin + '_l) = (' + expression + '_l)',
        '$origin_node(S.SOURCES, ' + origin + '_r) = (' + expression + '_r)',
        '$compiled_read(S, ' + origin + '_l) = (' + left + ')',
        '$compiled_precision(S, (' + origin + '_l)) = (14)',
        '$compiled_special_concat_bytes(S, ' + origin + '_l) = ($echo_value(' + left + '))',
        '$truth(S, ' + left + ') = ' + str(left_truth).lower(),
        '$compiled_special_concat_bytes(S, ' + origin + ') = ($ptascii(' + json.dumps(text) + '))']
    if skipped:
        name = 'string_key_short_and_never' if form == 'LogicalAnd' else 'string_key_short_or_never'
        checks += [
            expression + '_r = NExprFuncCall (NName (BYTES text_' + tag + '_dead) metadata_' + tag + '_name) (SEQUENCE eps) metadata_' + tag + '_call',
            '$base64(text_' + tag + '_dead) = $ptascii(' + json.dumps(name) + ')',
            '$pfshape(' + expression + '_r) = PFSTOP',
            origin + '_r = PORIGIN n_' + tag + '_dead pcpath_' + tag + '_dead',
            '$code_at(S.CODE, n_' + tag + '_dead) = (pcode_' + tag + '_dead)',
            '$code_expression(pcode_' + tag + '_dead.EXPRESSIONS, pcpath_' + tag + '_dead) = eps',
            '$compiled_read(S, ' + origin + '_r) = eps',
            '$compiled_special_concat_bytes(S, ' + origin + '_r) = eps']
    else:
        checks += [
            '$compiled_read(S, ' + origin + '_r) = (' + right[0] + ')',
            '$compiled_precision(S, (' + origin + '_r)) = (14)',
            '$compiled_special_concat_bytes(S, ' + origin + '_r) = ($echo_value(' + right[0] + '))',
            '$truth(S, ' + right[0] + ') = ' + str(right[1]).lower()]


def authority(index):
    checks = ['$origin_child((porigin_key), [PCFIELD 0, PCFIELD 0]) = (porigin_short_root)',
              r'S.PRECISIONINI = $ptascii("17") /\ $precision_value(S) = 17']
    if index == 0:
        short(checks, 'short_root', 'BooleanOr', 'PBOOL false', False, ('PSTRING ($ptascii("1tail"))', True))
        arithmetic.constant(checks, 'short_root_l', 'false', '')
        arithmetic.scalar(checks, 'short_root_r', 'NScalarString (BYTES text_short_root_r)', 'PSTRING ($ptascii("1tail"))', '1tail')
    elif index == 1:
        unary.unary(checks, 'short_root', 'NEGATIVE', 'PBOOL true', 'NINT 1', 'PINT $(-1)', '-1', '1')
        short(checks, 'short_root_child', 'BooleanAnd', 'PBOOL true', True, ('PINT 2', True))
        arithmetic.constant(checks, 'short_root_child_l', 'true', '1')
        arithmetic.constant(checks, 'short_root_child_r', 'E_WARNING', '2')
    elif index == 2:
        arithmetic.binary(checks, 'short_root', 'NExprBinaryOpPlus', 'ADD', 'PBOOL false', 'PBOOL false', 'PINT 0', 'NINT 0', 'NINT 0', 'NINT 0')
        short(checks, 'short_root_l', 'LogicalAnd', 'PBOOL false', False)
        arithmetic.constant(checks, 'short_root_l_l', 'false', '')
        arithmetic.constant(checks, 'short_root_r', 'false', '')
    else:
        unary.unary(checks, 'short_root', 'NEGATIVE', 'PINT 4', 'NINT 4', 'PINT $(-4)', '-4', '4')
        arithmetic.binary(checks, 'short_root_child', 'NExprBinaryOpMul', 'MULTIPLY', 'PBOOL true', 'PINT 4', 'PINT 4', 'NINT 1', 'NINT 4', 'NINT 4')
        short(checks, 'short_root_child_l', 'LogicalOr', 'PBOOL true', True)
        arithmetic.constant(checks, 'short_root_child_l_l', 'true', '1')
        arithmetic.binary(checks, 'short_root_child_r', 'NExprBinaryOpPlus', 'ADD', 'PINT 2', 'PINT 2', 'PINT 4', 'NINT 2', 'NINT 2', 'NINT 4')
        arithmetic.constant(checks, 'short_root_child_r_l', 'E_WARNING', '2')
        arithmetic.constant(checks, 'short_root_child_r_r', 'E_WARNING', '2')
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
    report['scope'] = 'Four actual nonfloat short-circuit source-state fixtures cover Boolean and Logical AND/OR with both ordinary compilation paths. A decisive left operand skips an undefined right call: its source remains authentic while no executable code/read/certificate is required. A nondecisive left operand has an actual right source/read/certificate and matching precision; only evaluated scalar operands use quiet truth. Root own Boolean values, source occurrences, existing unary/arithmetic ancestors, REQUEST owners, saved throw, fixed bounds and budgets retain existing laws. Float truth diagnostics and nonconstant evaluated operands retain separate core obligations.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
