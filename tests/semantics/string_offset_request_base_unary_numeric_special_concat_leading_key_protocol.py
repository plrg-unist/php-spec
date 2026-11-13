#!/usr/bin/env python3
"""Signed immediate numeric CONCAT keys retain real Warning continuation history."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_unary_numeric_special_concat_leading_key_cases as cases
import string_offset_request_base_integer_special_concat_leading_key_protocol as runner

base_conditions = runner.conditions


def conditions(program, path, index):
    prior_index = (0, 0, 1, 2)[index]
    checks, derived = base_conditions(program, path, prior_index)
    old_integer = 3 if prior_index == 2 else 1
    integer = (1, -1, 1, -4)[index]
    term = str(integer) if integer >= 0 else '$(' + str(integer) + ')'
    old_key, key = str(old_integer) + 'x', str(integer) + 'x'
    old_output = runner.prior.OUTPUTS[prior_index]
    replacements = {
        '"' + old_key + '"': '"' + key + '"',
        'STRING_LEADING ' + str(old_integer): 'STRING_LEADING ' + term,
        'STRING_BOUNDS ' + str(old_integer): 'STRING_BOUNDS ' + term,
        '"Uninitialized string offset ' + str(old_integer) + '"':
            '"Uninitialized string offset ' + str(integer) + '"',
        '$string_read_request_base_saved(S, pstringread) = (' + str(old_integer) + ')':
            '$string_read_request_base_saved(S, pstringread) = (' + term + ')',
        runner.prior.watbytes(('Illegal string offset "' + old_key + '"').encode()):
            runner.prior.watbytes(('Illegal string offset "' + key + '"').encode()),
        runner.prior.watbytes(('2|Illegal string offset "' + old_key + '"|5;').encode()):
            runner.prior.watbytes(('2|Illegal string offset "' + key + '"|5;').encode()),
        runner.prior.watbytes(old_output): runner.prior.watbytes(cases.OUTPUTS[index])}
    if index == 1:
        replacements['$ptascii("b")'] = '$ptascii("c")'
    for old, new in replacements.items():
        checks = [check.replace(old, new) for check in checks]
    old = '$origin_child((porigin_key), [PCFIELD 0, PCFIELD 0]) = (porigin_integer)'
    at = checks.index(old)
    unary = 'POSITIVE' if index in (0, 2) else 'NEGATIVE'
    node = 'NExprUnaryPlus' if index in (0, 2) else 'NExprUnaryMinus'
    extra = [
        '$origin_child((porigin_key), [PCFIELD 0, PCFIELD 0]) = (porigin_unary)',
        '$origin_node(S.SOURCES, porigin_unary) = (expression_unary)',
        'expression_unary = ' + node + ' expression_literal metadata_unary',
        '$pfshape(expression_unary) = PFUNARY ' + unary + ' expression_literal',
        '$origin_child((porigin_unary), [PCFIELD 0]) = (porigin_literal)',
        '$origin_node(S.SOURCES, porigin_literal) = (expression_literal)',
        '$compiled_precision(S, (porigin_unary)) = (14)',
        '$compiled_precision(S, (porigin_literal)) = (14)',
        'S.PRECISIONINI = $ptascii("17") /\\ $precision_value(S) = 17',
        '$parser_literal_at(expression_literal, 14) = (pvalue_literal)',
        '$compiled_read(S, porigin_literal) = (pvalue_literal)',
        '$compiled_read(S, porigin_unary) = (pvalue_unary)',
        '$unary_apply(S, ' + unary + ', pvalue_literal, 0) = S[.RESULT = KNOWN pvalue_unary]',
        '$parser_literal_at(expression_unary, 14) = eps',
        '$parser_literal_text_at(pvalue_unary, 14) = ($ptascii("' + str(integer) + '"))',
        '$compiled_special_concat_bytes(S, porigin_unary) = ($ptascii("' + str(integer) + '"))']
    if index < 2:
        extra += ['expression_literal = NScalarInt (INTEGER 1) metadata_literal',
                  'pvalue_literal = PINT 1', 'pvalue_unary = PINT ' + term]
    else:
        extra += ['expression_literal = NScalarFloat (FLOAT text_literal) metadata_literal',
                  'pvalue_literal = PFLOAT n_bits_literal',
                  'pvalue_unary = PFLOAT n_bits_unary',
                  '$parser_literal_text_at(pvalue_unary, 17) = (n_live_text*)',
                  'n_live_text* =/= $ptascii("' + str(integer) + '")']
    checks[at:at + 4] = extra
    return checks, derived


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    own_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    runner.cases = cases
    runner.OUTPUTS = cases.OUTPUTS
    runner.conditions = conditions
    passed = runner.main()
    assert hashlib.sha256(Path(__file__).read_bytes()).hexdigest() == own_hash
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'][str(Path(__file__).resolve())] = own_hash
    report['scope'] = 'Four fresh immediate signed int/float plus resolved bool/null CONCAT source-state fixtures at compile14/live17. Negative normal selection and genuine negative bounds preserve the existing borrowed-owner, fixed-index and supplied-throw laws. Older source/native/state and compiler-control cuts retain their identities without replay.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
