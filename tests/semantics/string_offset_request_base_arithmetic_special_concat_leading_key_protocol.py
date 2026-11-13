#!/usr/bin/env python3
"""Bare quiet arithmetic CONCAT keys retain actual Warning continuations."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_arithmetic_special_concat_leading_key_cases as cases
import string_offset_request_base_integer_special_concat_leading_key_protocol as runner

base_conditions = runner.conditions
base_outputs = runner.OUTPUTS

def binary(checks, tag, node, operation, left, right, result, left_number, right_number, result_number):
    expr, origin = 'expression_' + tag, 'porigin_' + tag
    checks += [
        '$origin_node(S.SOURCES, ' + origin + ') = (' + expr + ')',
        expr + ' = ' + node + ' ' + expr + '_l ' + expr + '_r metadata_' + tag,
        '$pfshape(' + expr + ') = PFBINARY ' + operation + ' ' + expr + '_l ' + expr + '_r',
        '$compiled_read(S, ' + origin + ') = (' + result + ')',
        '$compiled_precision(S, (' + origin + ')) = (14)',
        '$parser_literal_at(' + expr + ', 14) = eps',
        '$compiled_special_concat_bytes(S, ' + origin + ') = ($ptascii("' + str_value(result) + '"))',
        '$origin_child((' + origin + '), [PCFIELD 0]) = (' + origin + '_l)',
        '$origin_child((' + origin + '), [PCFIELD 1]) = (' + origin + '_r)',
        '$origin_node(S.SOURCES, ' + origin + '_l) = (' + expr + '_l)',
        '$origin_node(S.SOURCES, ' + origin + '_r) = (' + expr + '_r)',
        '$compiled_read(S, ' + origin + '_l) = (' + left + ')',
        '$compiled_read(S, ' + origin + '_r) = (' + right + ')',
        '$compiled_precision(S, (' + origin + '_l)) = (14)',
        '$compiled_precision(S, (' + origin + '_r)) = (14)',
        '$coerce_number(' + left + ') = COERCED (' + left_number + ') false',
        '$coerce_number(' + right + ') = COERCED (' + right_number + ') false',
        '$number_binary(' + operation + ', ' + left_number + ', ' + right_number + ') = NUM (' + result_number + ')',
        '$number_value(' + result_number + ') = ' + result,
        '$binary_apply(S, ' + operation + ', ' + left + ', ' + right + ', 0) = S[.RESULT = KNOWN (' + result + ')]',
        '$parser_literal_text_at(' + result + ', 14) = ($ptascii("' + str_value(result) + '"))']

def str_value(result):
    return {'PFLOAT 4607182418800017453': '1', 'PINT $(-1)': '-1', 'PINT 0': '0', 'PINT 1': '1', 'PINT 2': '2', 'PINT 4': '4'}[result]

def scalar(checks, tag, source, value, text):
    checks += ['expression_' + tag + ' = ' + source + ' metadata_' + tag,
               '$parser_literal_at(expression_' + tag + ', 14) = (' + value + ')',
               '$compiled_special_concat_bytes(S, porigin_' + tag + ') = ($ptascii(' + json.dumps(text) + '))']

def constant(checks, tag, spelling, text):
    checks += ['expression_' + tag + ' = NExprConstFetch name_' + tag + ' metadata_' + tag,
               '$ptast(name_' + tag + ') = PTNAME PTPLAIN ($ptascii(' + json.dumps(spelling) + '))',
               '$parser_literal_at(expression_' + tag + ', 14) = eps',
               '$compiled_special_concat_bytes(S, porigin_' + tag + ') = ($ptascii(' + json.dumps(text) + '))']

def authority(index):
    checks = ['$origin_child((porigin_key), [PCFIELD 0, PCFIELD 0]) = (porigin_arith)',
              r'S.PRECISIONINI = $ptascii("17") /\ $precision_value(S) = 17']
    if index == 0:
        binary(checks, 'arith', 'NExprBinaryOpPlus', 'ADD', 'PFLOAT 4607182418800017453', 'PFLOAT 0', 'PFLOAT 4607182418800017453', 'NFLOAT 4607182418800017453', 'NFLOAT 0', 'NFLOAT 4607182418800017453')
        scalar(checks, 'arith_l', 'NScalarFloat (FLOAT text_arith_l)', 'PFLOAT 4607182418800017453', '1')
        scalar(checks, 'arith_r', 'NScalarFloat (FLOAT text_arith_r)', 'PFLOAT 0', '0')
        checks += ['$parser_literal_text_at(PFLOAT 4607182418800017453, 17) = (n_live_text*)', 'n_live_text* =/= $ptascii("1")']
    elif index == 1:
        binary(checks, 'arith', 'NExprBinaryOpMinus', 'SUBTRACT', 'PINT 0', 'PINT 1', 'PINT $(-1)', 'NINT 0', 'NINT 1', 'NINT $(-1)')
        scalar(checks, 'arith_l', 'NScalarInt (INTEGER 0)', 'PINT 0', '0')
        constant(checks, 'arith_r', 'E_ERROR', '1')
    elif index == 2:
        binary(checks, 'arith', 'NExprBinaryOpMinus', 'SUBTRACT', 'PINT 2', 'PINT 1', 'PINT 1', 'NINT 2', 'NINT 1', 'NINT 1')
        binary(checks, 'arith_l', 'NExprBinaryOpDiv', 'DIVIDE', 'PINT 6', 'PSTRING ($ptascii("3"))', 'PINT 2', 'NINT 6', 'NINT 3', 'NINT 2')
        scalar(checks, 'arith_l_l', 'NScalarInt (INTEGER 6)', 'PINT 6', '6')
        checks += [
            'expression_arith_l_r = NExprBinaryOpConcat expression_three expression_empty metadata_numeric_concat',
            '$origin_child((porigin_arith_l_r), [PCFIELD 0]) = (porigin_three)',
            '$origin_child((porigin_arith_l_r), [PCFIELD 1]) = (porigin_empty)',
            '$origin_node(S.SOURCES, porigin_three) = (NScalarString (BYTES text_three) metadata_three)',
            '$origin_node(S.SOURCES, porigin_empty) = (NScalarString (BYTES text_empty) metadata_empty)',
            '$base64(text_three) = $ptascii("3") /\\ $base64(text_empty) = eps',
            '$compiled_special_concat_bytes(S, porigin_three) = ($ptascii("3"))',
            '$compiled_special_concat_bytes(S, porigin_empty) = ($ptascii(""))',
            '$compiled_precision(S, (porigin_arith_l_r)) = (14)',
            '$compiled_special_concat_bytes(S, porigin_arith_l_r) = ($ptascii("3"))',
            '$parser_literal_at(expression_arith_l_r, 14) = (PSTRING ($ptascii("3")))']
        binary(checks, 'arith_r', 'NExprBinaryOpPlus', 'ADD', 'PBOOL true', 'PBOOL false', 'PINT 1', 'NINT 1', 'NINT 0', 'NINT 1')
        constant(checks, 'arith_r_l', 'true', '1')
        constant(checks, 'arith_r_r', 'false', '')
    else:
        binary(checks, 'arith', 'NExprBinaryOpMul', 'MULTIPLY', 'PINT 2', 'PINT 2', 'PINT 4', 'NINT 2', 'NINT 2', 'NINT 4')
        scalar(checks, 'arith_l', 'NScalarInt (INTEGER 2)', 'PINT 2', '2')
        constant(checks, 'arith_r', 'E_WARNING', '2')
    return checks

def conditions(program, path, index):
    route = (0, 0, 1, 2)[index]
    checks, derived = base_conditions(program, path, route)
    old_integer, integer = (3 if route == 2 else 1), (1, -1, 1, 4)[index]
    term = str(integer) if integer >= 0 else '$(' + str(integer) + ')'
    old_key, key = str(old_integer) + 'x', str(integer) + 'x'
    replacements = {
        '"' + old_key + '"': '"' + key + '"',
        'STRING_LEADING ' + str(old_integer): 'STRING_LEADING ' + term,
        'STRING_BOUNDS ' + str(old_integer): 'STRING_BOUNDS ' + term,
        '"Uninitialized string offset ' + str(old_integer) + '"':
            '"Uninitialized string offset ' + str(integer) + '"',
        '$string_read_request_base_saved(S, pstringread) = (' + str(old_integer) + ')':
            '$string_read_request_base_saved(S, pstringread) = (' + term + ')',
        '$compiled_read(S, porigin_inner) = (PSTRING ($ptascii("' + str(old_integer) + '")))':
            '$compiled_read(S, porigin_inner) = (PSTRING ($ptascii("' + str(integer) + '")))',
        runner.prior.watbytes(('Illegal string offset "' + old_key + '"').encode()):
            runner.prior.watbytes(('Illegal string offset "' + key + '"').encode()),
        runner.prior.watbytes(('2|Illegal string offset "' + old_key + '"|5;').encode()):
            runner.prior.watbytes(('2|Illegal string offset "' + key + '"|5;').encode()),
        runner.prior.watbytes(base_outputs[route]): runner.prior.watbytes(cases.OUTPUTS[index])}
    if index == 1:
        replacements['$ptascii("b")'] = '$ptascii("c")'
    for old, new in replacements.items():
        checks = [check.replace(old, new) for check in checks]
    at = checks.index('$origin_child((porigin_key), [PCFIELD 0, PCFIELD 0]) = (porigin_integer)')
    assert checks[at + 1].startswith('$origin_node(S.SOURCES, porigin_integer) = (NScalarInt ')
    checks[at:at + 4] = authority(index)
    return checks, derived


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    watched = [Path(__file__), Path(runner.__file__)]
    before = {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.cases = cases
    runner.OUTPUTS = cases.OUTPUTS
    runner.conditions = conditions
    passed = runner.main()
    assert before == {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = 'Four fresh bare ADD/SUB/MUL/DIV plus bool/null CONCAT source-state fixtures authenticate every actual arithmetic node/child, own facts, BOTH quiet coercions, NUM results and exact pure application/quiet formatting at compile14/live17. Certified numeric CONCAT operands use original literal bytes without descendant own-read assumptions. Saved indices, borrowed owners, supplied throw, fixed later bounds and budgets retain existing laws. Older source/native/state/compiler cuts remain historical without replay.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
