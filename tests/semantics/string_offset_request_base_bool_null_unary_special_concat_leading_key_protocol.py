#!/usr/bin/env python3
"""Boolean/null unary certificates preserve saved-key callback histories."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_bool_null_unary_special_concat_leading_key_cases as cases
import string_offset_request_base_arithmetic_special_concat_leading_key_protocol as arithmetic

runner = arithmetic.runner
base_conditions = runner.conditions
base_outputs = runner.OUTPUTS


def unary(checks, tag, operation, child, number, result, text, child_text):
    expression, origin = 'expression_' + tag, 'porigin_' + tag
    checks += [
        '$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')',
        expression + ' = ' + ('NExprUnaryPlus' if operation == 'POSITIVE' else 'NExprUnaryMinus') + ' ' + expression + '_child metadata_' + tag,
        '$pfshape(' + expression + ') = PFUNARY ' + operation + ' ' + expression + '_child',
        '$origin_child((' + origin + '), [PCFIELD 0]) = (' + origin + '_child)',
        '$origin_node(S.SOURCES, ' + origin + '_child) = (' + expression + '_child)',
        '$parser_literal_at(' + expression + '_child, 14) = eps',
        '$compiled_read(S, ' + origin + '_child) = (' + child + ')',
        '$compiled_precision(S, (' + origin + '_child)) = (14)',
        '$compiled_special_concat_bytes(S, ' + origin + '_child) = ($ptascii(' + json.dumps(child_text) + '))',
        '$coerce_number(' + child + ') = COERCED (' + number + ') false',
        '$compiled_read(S, ' + origin + ') = (' + result + ')',
        '$compiled_precision(S, (' + origin + ')) = (14)',
        '$unary_apply(S, ' + operation + ', ' + child + ', 0) = S[.RESULT = KNOWN (' + result + ')]',
        '$parser_literal_text_at(' + result + ', 14) = ($ptascii(' + json.dumps(text) + '))',
        '$compiled_special_concat_bytes(S, ' + origin + ') = ($ptascii(' + json.dumps(text) + '))']


def authority(index):
    checks = ['$origin_child((porigin_key), [PCFIELD 0, PCFIELD 0]) = (porigin_bool_unary)',
              r'S.PRECISIONINI = $ptascii("17") /\ $precision_value(S) = 17']
    if index < 3:
        operation = 'NEGATIVE' if index == 1 else 'POSITIVE'
        child, number, child_text = ('PNULL', 'NINT 0', '') if index == 2 else ('PBOOL true', 'NINT 1', '1')
        result, text = ('PINT 1', '1') if index == 0 else ('PINT $(-1)', '-1') if index == 1 else ('PINT 0', '0')
        unary(checks, 'bool_unary', operation, child, number, result, text, child_text)
        arithmetic.constant(checks, 'bool_unary_child', 'null' if index == 2 else 'true', child_text)
        checks += ['$type_bytes(' + child + ') = $ptascii("' + ('null' if index == 2 else 'bool') + '")']
    else:
        unary(checks, 'bool_unary', 'NEGATIVE', 'PINT 4', 'NINT 4', 'PINT $(-4)', '-4', '4')
        arithmetic.binary(checks, 'bool_unary_child', 'NExprBinaryOpPlus', 'ADD', 'PINT 0', 'PINT 4', 'PINT 4', 'NINT 0', 'NINT 4', 'NINT 4')
        unary(checks, 'bool_unary_child_l', 'POSITIVE', 'PNULL', 'NINT 0', 'PINT 0', '0', '')
        arithmetic.constant(checks, 'bool_unary_child_l_child', 'null', '')
        arithmetic.binary(checks, 'bool_unary_child_r', 'NExprBinaryOpPlus', 'ADD', 'PINT 0', 'PINT 4', 'PINT 4', 'NINT 0', 'NINT 4', 'NINT 4')
        unary(checks, 'bool_unary_child_r_l', 'NEGATIVE', 'PBOOL false', 'NINT 0', 'PINT 0', '0', '')
        arithmetic.constant(checks, 'bool_unary_child_r_l_child', 'false', '')
        arithmetic.binary(checks, 'bool_unary_child_r_r', 'NExprBinaryOpMul', 'MULTIPLY', 'PINT 2', 'PINT 2', 'PINT 4', 'NINT 2', 'NINT 2', 'NINT 4')
        arithmetic.scalar(checks, 'bool_unary_child_r_r_l', 'NScalarInt (INTEGER 2)', 'PINT 2', '2')
        arithmetic.constant(checks, 'bool_unary_child_r_r_r', 'E_WARNING', '2')
    return checks


def conditions(program, path, index):
    route = (0, 0, 1, 2)[index]
    checks, derived = base_conditions(program, path, route)
    old_integer, integer = (3 if route == 2 else 1), (1, -1, 0, -4)[index]
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
        replacements['$compiled_read(S, porigin_special) = (PNULL)'] = '$compiled_read(S, porigin_special) = (PBOOL false)'
    for old, new in replacements.items():
        checks = [check.replace(old, new) for check in checks]
    at = checks.index('$origin_child((porigin_key), [PCFIELD 0, PCFIELD 0]) = (porigin_integer)')
    assert checks[at + 1].startswith('$origin_node(S.SOURCES, porigin_integer) = (NScalarInt ')
    checks[at:at + 4] = authority(index)
    return checks, derived


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    watched = [Path(__file__), Path(arithmetic.__file__), Path(runner.__file__)]
    before = {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.cases = cases
    runner.OUTPUTS = cases.OUTPUTS
    runner.conditions = conditions
    passed = runner.main()
    assert before == {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = 'Four fresh Boolean/null unary source-state fixtures authenticate exact child kinds, recursive certificates, own facts and matching compiled precision. Quiet coercions and pure unary/ADD/MUL results preserve true/false/null typing, signed/zero indices, nested arithmetic, supplied throw, fixed negative bounds and borrowed owners/budgets. Original native observations are reused once; earlier campaigns retain separate cuts.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
