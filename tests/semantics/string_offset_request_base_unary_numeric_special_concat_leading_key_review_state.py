#!/usr/bin/env python3
"""Independent signed numeric CONCAT facts, precision and borrowed-owner checks."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_unary_numeric_special_concat_leading_key_cases as cases
import string_offset_request_base_float_special_concat_leading_key_review_state as floating

prior = floating.prior
runner = prior.runner
base_conditions = prior.conditions


def conditions(program, path, index):
    prior_index = (0, 0, 1, 2)[index]
    checks, derived = base_conditions(program, path, prior_index)
    old_integer = 3 if prior_index == 2 else 1
    integer = (1, -1, 1, -4)[index]
    term = str(integer) if integer >= 0 else '$(' + str(integer) + ')'
    key = str(integer) + 'x'
    old_output = runner.prior.cases.OUTPUTS[prior_index]
    replacements = {
        '$ptascii("' + str(old_integer) + 'x")': '$ptascii("' + key + '")',
        '$ptascii("Uninitialized string offset ' + str(old_integer) + '")':
            '$ptascii("Uninitialized string offset ' + str(integer) + '")',
        'STRING_LEADING ' + str(old_integer): 'STRING_LEADING ' + term,
        'STRING_BOUNDS ' + str(old_integer): 'STRING_BOUNDS ' + term,
        '$string_read_request_base_saved(S, pstringread) = (' + str(old_integer) + ')':
            '$string_read_request_base_saved(S, pstringread) = (' + term + ')',
        '$compiled_read(S, porigin_inner) = (PSTRING ($ptascii("' + str(old_integer) + '")))':
            '$compiled_read(S, porigin_inner) = (PSTRING ($ptascii("' + str(integer) + '")))',
        '[' + ','.join(map(str, old_output)) + ']': '[' + ','.join(map(str, cases.OUTPUTS[index])) + ']'}
    if index == 1:
        replacements['$ptascii("b")'] = '$ptascii("c")'
    for old, new in replacements.items():
        checks = [check.replace(old, new) for check in checks]
    old_node = 'NScalarInt (INTEGER ' + str(old_integer) + ') metadata_integer'
    old = 'expression_11 = ' + old_node
    assert checks.count(old) == 1
    checks[checks.index(old)] = 'expression_11 = expression_unary'
    old_checks = [
        '$origin_child((porigin_key), [PCFIELD 0, PCFIELD 0]) = (porigin_integer)',
        '$origin_node(S.SOURCES, porigin_integer) = (' + old_node + ')',
        '$compiled_read(S, porigin_integer) = (PINT ' + str(old_integer) + ')',
        '$parser_literal_at(' + old_node + ', 14) = (PINT ' + str(old_integer) + ')',
        '$compiled_special_concat_bytes(S, porigin_integer) = ($ptascii("' + str(old_integer) + '"))']
    at = checks.index(old_checks[0])
    assert checks[at:at + len(old_checks)] == old_checks
    unary = 'POSITIVE' if index in (0, 2) else 'NEGATIVE'
    node = 'NExprUnaryPlus' if index in (0, 2) else 'NExprUnaryMinus'
    extra = [
        '$origin_child((porigin_key), [PCFIELD 0, PCFIELD 0]) = (porigin_unary)',
        '$origin_node(S.SOURCES, porigin_unary) = (expression_unary)',
        'expression_unary = ' + node + ' expression_literal metadata_unary',
        '$pfshape(expression_unary) = PFUNARY ' + unary + ' expression_literal',
        '$origin_child((porigin_unary), [PCFIELD 0]) = (porigin_literal)',
        '$origin_node(S.SOURCES, porigin_literal) = (expression_literal)',
        '$parser_literal_at(expression_unary, 14) = eps',
        '$parser_literal_at(expression_literal, 14) = (pvalue_literal)',
        '$compiled_read(S, porigin_literal) = (pvalue_literal)',
        '$compiled_read(S, porigin_unary) = (pvalue_unary)',
        '$compiled_precision(S, (porigin_unary)) = (14)',
        'S.PRECISIONINI = $ptascii("17") /\\ $precision_value(S) = 17',
        '$unary_apply(S, ' + unary + ', pvalue_literal, 0) = S[.RESULT = KNOWN pvalue_unary]',
        '$parser_literal_text_at(pvalue_unary, 14) = ($ptascii("' + str(integer) + '"))',
        '$compiled_special_concat_bytes(S, porigin_unary) = ($ptascii("' + str(integer) + '"))']
    if index < 2:
        extra += ['expression_literal = NScalarInt (INTEGER 1) metadata_literal',
                  'pvalue_literal = PINT 1', 'pvalue_unary = PINT ' + term]
    else:
        literal_bits = 4607182418800017453 if index == 2 else 4616189618054758411
        result_bits = literal_bits if index == 2 else 13839561654909534219
        extra += ['expression_literal = NScalarFloat (FLOAT text_literal) metadata_literal',
                  'pvalue_literal = PFLOAT ' + str(literal_bits),
                  'pvalue_unary = PFLOAT ' + str(result_bits),
                  '$parser_literal_text_at(pvalue_unary, 17) =/= ($ptascii("' + str(integer) + '"))']
    checks[at:at + len(old_checks)] = extra
    extra = runner.lines(r'''
S_drop_unary = S_after[.POOLS = $special_review_pools(S_after.POOLS, porigin_unary, eps)]
$compiled_read(S_drop_unary, porigin_unary) = eps
$compiled_special_concat_bytes(S_drop_unary, porigin_unary) = eps
$compiled_special_concat_bytes(S_drop_unary, porigin_key) = eps
$string_read_request_base_saved(S_drop_unary, pstringread) = eps
S_wrong_unary = S_after[.POOLS = $special_review_pools(S_after.POOLS, porigin_unary, (PINT 2))]
$compiled_read(S_wrong_unary, porigin_unary) = (PINT 2)
$compiled_special_concat_bytes(S_wrong_unary, porigin_unary) = eps
$compiled_special_concat_bytes(S_wrong_unary, porigin_key) = eps
$string_read_request_base_saved(S_wrong_unary, pstringread) = eps
S_drop_literal = S_after[.POOLS = $special_review_pools(S_after.POOLS, porigin_literal, eps)]
$compiled_read(S_drop_literal, porigin_literal) = eps
S_live_precision = S_after[.PRECISIONINI = $ptascii("9")][.PRECISIONMODIFIED = true]
$precision_value(S_live_precision) = 9
$compiled_precision(S_live_precision, (porigin_unary)) = (14)
S_no_precision = S_after[.DECLARATIONS = eps]
$compiled_read(S_no_precision, porigin_unary) = (pvalue_unary)
$compiled_precision(S_no_precision, (porigin_unary)) = eps
$compiled_special_concat_bytes(S_no_precision, porigin_unary) = eps
$string_read_request_base_saved(S_no_precision, pstringread) = eps
''') + [
        '$compiled_read(S_drop_unary, porigin_key) = (PSTRING ($ptascii("' + key + '")))',
        '$compiled_string_value(S_drop_unary, porigin_key, PSTRING ($ptascii("' + key + '"))) = PSTRING ($ptascii("' + key + '"))',
        '$compiled_special_concat_bytes(S_drop_literal, porigin_key) = ($ptascii("' + key + '"))',
        '$string_read_request_base_saved(S_drop_literal, pstringread) = (' + term + ')',
        '$compiled_special_concat_bytes(S_live_precision, porigin_key) = ($ptascii("' + key + '"))',
        '$string_read_request_base_saved(S_live_precision, pstringread) = (' + term + ')']
    if index >= 2:
        extra += runner.lines(r'''
S_wrong_precision = S_after[.POOLS = $float_review_precision(S_after.POOLS, porigin_unary, 17)]
$compiled_read(S_wrong_precision, porigin_unary) = (pvalue_unary)
$compiled_precision(S_wrong_precision, (porigin_key)) = (14)
$compiled_precision(S_wrong_precision, (porigin_unary)) = (17)
$compiled_special_concat_bytes(S_wrong_precision, porigin_key) = eps
$string_read_request_base_saved(S_wrong_precision, pstringread) = eps
''')
    checks += extra
    return checks, derived + len(extra)


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    watched = [Path(__file__), Path(prior.__file__), Path(floating.__file__)]
    before = {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.cases = cases
    runner.conditions = conditions
    runner.compiler_conditions = floating.compiler_conditions
    runner.CONTROLS = {'mixed-nested-unary-special': runner.CONTROLS['mixed-nested-unary-special']}
    passed = runner.main(expected_outputs=cases.OUTPUTS)
    assert before == {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = 'Four fresh signed int/float plus special CONCAT source-state fixtures, independently checked unary facts/precision and a genuine nested-unary compiler refusal. Old source/native/state and compiler-name selections retain their recorded cuts without replay.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
