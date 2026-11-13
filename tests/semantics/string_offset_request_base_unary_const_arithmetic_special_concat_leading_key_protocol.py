#!/usr/bin/env python3
"""Certified unary constant/arithmetic keys retain actual Warning histories."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_unary_const_arithmetic_special_concat_leading_key_cases as cases
import string_offset_request_base_arithmetic_special_concat_leading_key_protocol as arithmetic

runner = arithmetic.runner
base_conditions = runner.conditions
base_outputs = runner.OUTPUTS


def authority(index):
    operation = ('POSITIVE', 'NEGATIVE', 'POSITIVE', 'NEGATIVE')[index]
    node = 'NExprUnaryPlus' if operation == 'POSITIVE' else 'NExprUnaryMinus'
    child = ('PINT 1', 'PFLOAT 4607182418800017453', 'PINT 1', 'PINT 4')[index]
    number = ('NINT 1', 'NFLOAT 4607182418800017453', 'NINT 1', 'NINT 4')[index]
    result = ('PINT 1', 'PFLOAT 13830554455654793261', 'PINT 1', 'PINT $(-4)')[index]
    child_text, text = ('1', '1', '1', '4')[index], ('1', '-1', '1', '-4')[index]
    checks = [
        '$origin_child((porigin_key), [PCFIELD 0, PCFIELD 0]) = (porigin_unary)',
        r'S.PRECISIONINI = $ptascii("17") /\ $precision_value(S) = 17',
        '$origin_node(S.SOURCES, porigin_unary) = (expression_unary)',
        'expression_unary = ' + node + ' expression_arith metadata_unary',
        '$pfshape(expression_unary) = PFUNARY ' + operation + ' expression_arith',
        '$origin_child((porigin_unary), [PCFIELD 0]) = (porigin_arith)',
        '$origin_node(S.SOURCES, porigin_arith) = (expression_arith)',
        '$parser_literal_at(expression_arith, 14) = eps',
        '$compiled_read(S, porigin_arith) = (' + child + ')',
        '$compiled_precision(S, (porigin_arith)) = (14)',
        '$compiled_special_concat_bytes(S, porigin_arith) = ($ptascii("' + child_text + '"))',
        '$coerce_number(' + child + ') = COERCED (' + number + ') false',
        '$compiled_read(S, porigin_unary) = (' + result + ')',
        '$compiled_precision(S, (porigin_unary)) = (14)',
        '$unary_apply(S, ' + operation + ', ' + child + ', 0) = S[.RESULT = KNOWN (' + result + ')]',
        '$parser_literal_text_at(' + result + ', 14) = ($ptascii("' + text + '"))',
        '$compiled_special_concat_bytes(S, porigin_unary) = ($ptascii("' + text + '"))']
    if index == 0:
        arithmetic.constant(checks, 'arith', 'E_ERROR', '1')
    else:
        checks += arithmetic.authority((0, 0, 2, 3)[index])[2:]
    if index == 1:
        checks += ['$parser_literal_text_at(' + result + ', 17) = (n_unary_live_text*)',
                   'n_unary_live_text* =/= $ptascii("-1")']
    return checks


def conditions(program, path, index):
    route = (0, 0, 1, 2)[index]
    checks, derived = base_conditions(program, path, route)
    old_integer, integer = (3 if route == 2 else 1), (1, -1, 1, -4)[index]
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
    report['scope'] = 'Four fresh unary plus/minus source-state fixtures authenticate their exact nonliteral integer-constant or quiet arithmetic child, recursive certificate, own numeric facts and shared compiled precision. Existing pure unary application and quiet formatting preserve compile14/live17, negative selection, marked supplied throw, fixed negative later bounds and borrowed-owner/budget laws. Native originals are reused once; earlier campaigns retain their recorded cuts.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
