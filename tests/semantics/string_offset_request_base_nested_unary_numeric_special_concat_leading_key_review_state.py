#!/usr/bin/env python3
"""Independent numeric unary-chain authority and retained-base continuations."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_nested_unary_numeric_special_concat_leading_key_cases as cases
import string_offset_request_base_unary_numeric_special_concat_leading_key_review_state as prior

runner = prior.runner
base_conditions = prior.conditions
STRING_CONTROL = 'mixed-numeric-string-unary-special'
BINARY_CONTROL = 'mixed-binary-unary-special'


def conditions(program, path, index):
    checks, derived = base_conditions(program, path, index)
    old_node = 'NExprUnaryPlus' if index in (0, 2) else 'NExprUnaryMinus'
    node = 'NExprUnaryMinus' if index in (0, 2) else 'NExprUnaryPlus'
    old_unary = 'POSITIVE' if index in (0, 2) else 'NEGATIVE'
    unary = 'NEGATIVE' if index in (0, 2) else 'POSITIVE'
    checks = [check.replace(old_node + ' expression_literal metadata_unary', node + ' expression_literal metadata_unary')
              .replace('PFUNARY ' + old_unary + ' expression_literal', 'PFUNARY ' + unary + ' expression_literal')
              .replace('$unary_apply(S, ' + old_unary + ', pvalue_literal, 0)', '$unary_apply(S, ' + unary + ', pvalue_literal, 0)')
              .replace('porigin_literal', 'porigin_child_unary').replace('expression_literal', 'expression_child_unary')
              .replace('pvalue_literal', 'pvalue_child_unary').replace('metadata_literal', 'metadata_child_unary')
              .replace('S_drop_literal', 'S_drop_child_unary') for check in checks]
    child_node = 'NExprUnaryPlus' if index == 2 else 'NExprUnaryMinus'
    child_unary = 'POSITIVE' if index == 2 else 'NEGATIVE'
    child_expression = 'expression_terminal' if index < 2 else 'expression_inner'
    if index < 2:
        old = 'expression_child_unary = NScalarInt (INTEGER 1) metadata_child_unary'
        value = 'PINT $(-1)'
        old_value = 'PINT 1'
    else:
        old = 'expression_child_unary = NScalarFloat (FLOAT text_literal) metadata_child_unary'
        old_value = 'PFLOAT ' + str(4607182418800017453 if index == 2 else 4616189618054758411)
        value = 'PFLOAT ' + str(13830554455654793261 if index == 2 else 13839561654909534219)
    replacements = {
        old: 'expression_child_unary = ' + child_node + ' ' + child_expression + ' metadata_child_unary',
        '$parser_literal_at(expression_child_unary, 14) = (pvalue_child_unary)': '$parser_literal_at(expression_child_unary, 14) = eps',
        'pvalue_child_unary = ' + old_value: 'pvalue_child_unary = ' + value,
        '$compiled_special_concat_bytes(S_drop_child_unary, porigin_key) = ($ptascii("' + ('-4x' if index == 3 else '-1x' if index == 1 else '1x') + '"))': '$compiled_special_concat_bytes(S_drop_child_unary, porigin_key) = eps',
        '$string_read_request_base_saved(S_drop_child_unary, pstringread) = (' + ('$(-4)' if index == 3 else '$(-1)' if index == 1 else '1') + ')': '$string_read_request_base_saved(S_drop_child_unary, pstringread) = eps'}
    for old, new in replacements.items():
        assert checks.count(old) == 1, old
        checks[checks.index(old)] = new
    extra = [
        '$pfshape(expression_child_unary) = PFUNARY ' + child_unary + ' ' + child_expression,
        '$compiled_precision(S, (porigin_child_unary)) = (14)',
        '$compiled_special_concat_bytes(S, porigin_child_unary) = ($ptascii("' + ('-4' if index == 3 else '-1') + '"))']
    if index < 2:
        extra += runner.lines(r'''
$origin_child((porigin_child_unary), [PCFIELD 0]) = (porigin_terminal)
$origin_node(S.SOURCES, porigin_terminal) = (expression_terminal)
expression_terminal = NScalarInt (INTEGER 1) metadata_terminal
$parser_literal_at(expression_terminal, 14) = (PINT 1)
$compiled_read(S, porigin_terminal) = (PINT 1)
$unary_apply(S, NEGATIVE, PINT 1, 0) = S[.RESULT = KNOWN pvalue_child_unary]
''')
    else:
        inner_node = 'NExprUnaryMinus' if index == 2 else 'NExprUnaryPlus'
        inner_unary = 'NEGATIVE' if index == 2 else 'POSITIVE'
        bits = 4607182418800017453 if index == 2 else 4616189618054758411
        inner_bits = 13830554455654793261 if index == 2 else bits
        extra += [
            '$origin_child((porigin_child_unary), [PCFIELD 0]) = (porigin_inner_unary)',
            '$origin_node(S.SOURCES, porigin_inner_unary) = (expression_inner)',
            'expression_inner = ' + inner_node + ' expression_terminal metadata_inner_unary',
            '$pfshape(expression_inner) = PFUNARY ' + inner_unary + ' expression_terminal',
            '$compiled_precision(S, (porigin_inner_unary)) = (14)',
            '$compiled_read(S, porigin_inner_unary) = (PFLOAT ' + str(inner_bits) + ')',
            '$origin_child((porigin_inner_unary), [PCFIELD 0]) = (porigin_terminal)',
            '$origin_node(S.SOURCES, porigin_terminal) = (expression_terminal)',
            'expression_terminal = NScalarFloat (FLOAT text_terminal) metadata_terminal',
            '$parser_literal_at(expression_terminal, 14) = (PFLOAT ' + str(bits) + ')',
            '$compiled_read(S, porigin_terminal) = (PFLOAT ' + str(bits) + ')',
            '$unary_apply(S, ' + inner_unary + ', PFLOAT ' + str(bits) + ', 0) = S[.RESULT = KNOWN (PFLOAT ' + str(inner_bits) + ')]',
            '$unary_apply(S, ' + child_unary + ', PFLOAT ' + str(inner_bits) + ', 0) = S[.RESULT = KNOWN pvalue_child_unary]']
    at = next(i for i, check in enumerate(checks) if check.startswith('S_drop_unary = '))
    checks[at:at] = extra
    key = '-4x' if index == 3 else '-1x' if index == 1 else '1x'
    term = '$(-4)' if index == 3 else '$(-1)' if index == 1 else '1'
    extra = runner.lines(r'''
S_wrong_child_unary = S_after[.POOLS = $special_review_pools(S_after.POOLS, porigin_child_unary, (PINT 2))]
$compiled_read(S_wrong_child_unary, porigin_child_unary) = (PINT 2)
$compiled_special_concat_bytes(S_wrong_child_unary, porigin_key) = eps
$string_read_request_base_saved(S_wrong_child_unary, pstringread) = eps
S_child_precision = S_after[.POOLS = $float_review_precision(S_after.POOLS, porigin_child_unary, 17)]
$compiled_precision(S_child_precision, (porigin_unary)) = (14)
$compiled_precision(S_child_precision, (porigin_child_unary)) = (17)
$compiled_special_concat_bytes(S_child_precision, porigin_key) = eps
$string_read_request_base_saved(S_child_precision, pstringread) = eps
S_drop_terminal = S_after[.POOLS = $special_review_pools(S_after.POOLS, porigin_terminal, eps)]
$compiled_read(S_drop_terminal, porigin_terminal) = eps
''') + [
        '$compiled_read(S_drop_child_unary, porigin_unary) = (pvalue_unary)',
        '$compiled_special_concat_bytes(S_drop_terminal, porigin_key) = ($ptascii("' + key + '"))',
        '$string_read_request_base_saved(S_drop_terminal, pstringread) = (' + term + ')']
    if index >= 2:
        extra += runner.lines(r'''
S_drop_inner_unary = S_after[.POOLS = $special_review_pools(S_after.POOLS, porigin_inner_unary, eps)]
$compiled_read(S_drop_inner_unary, porigin_inner_unary) = eps
$compiled_special_concat_bytes(S_drop_inner_unary, porigin_key) = eps
$string_read_request_base_saved(S_drop_inner_unary, pstringread) = eps
S_wrong_inner_unary = S_after[.POOLS = $special_review_pools(S_after.POOLS, porigin_inner_unary, (PINT 2))]
$compiled_special_concat_bytes(S_wrong_inner_unary, porigin_key) = eps
$string_read_request_base_saved(S_wrong_inner_unary, pstringread) = eps
S_inner_precision = S_after[.POOLS = $float_review_precision(S_after.POOLS, porigin_inner_unary, 17)]
$compiled_precision(S_inner_precision, (porigin_unary)) = (14)
$compiled_precision(S_inner_precision, (porigin_child_unary)) = (14)
$compiled_precision(S_inner_precision, (porigin_inner_unary)) = (17)
$compiled_special_concat_bytes(S_inner_precision, porigin_key) = eps
$string_read_request_base_saved(S_inner_precision, pstringread) = eps
''')
    checks += extra
    return checks, derived + len(extra)


def compiler_conditions(checked, paths):
    assert list(checked) == [STRING_CONTROL, BINARY_CONTROL]
    checks = prior.floating.compiler_conditions({STRING_CONTROL: checked[STRING_CONTROL]}, paths)
    checks += ['S_binary = $php_run(' + checked[BINARY_CONTROL]['fixture'] + ', 0, ' + json.dumps(base64.b64encode(bytes(paths[BINARY_CONTROL])).decode()) + ')']
    return checks + runner.lines(r'''
S_binary.COMPLETION = BUDGET
S_binary.SOURCES[0].ID = 0
$special_review_concat_path(S_binary.SOURCES[0].OCCURRENCES) = (pcpath_binary)
porigin_binary = PORIGIN 0 pcpath_binary
$compiled_read(S_binary, porigin_binary) = (PSTRING ($ptascii("1x")))
$compiled_special_concat_bytes(S_binary, porigin_binary) = eps
$compiled_string_value(S_binary, porigin_binary, PSTRING ($ptascii("1x"))) = PSTRING ($ptascii("1x"))
$origin_child((porigin_binary), [PCFIELD 0, PCFIELD 0]) = (porigin_binary_unary)
$origin_node(S_binary.SOURCES, porigin_binary_unary) = (NExprUnaryPlus expression_binary metadata_binary_unary)
$compiled_read(S_binary, porigin_binary_unary) = (PFLOAT 4607182418800017408)
$compiled_special_concat_bytes(S_binary, porigin_binary_unary) = eps
$origin_child((porigin_binary_unary), [PCFIELD 0]) = (porigin_binary_child)
$origin_node(S_binary.SOURCES, porigin_binary_child) = (expression_binary)
expression_binary = NExprBinaryOpPlus expression_left expression_right metadata_binary
$parser_literal_at(expression_binary, 14) = eps
$compiled_read(S_binary, porigin_binary_child) = (PFLOAT 4607182418800017408)
$unary_apply(S_binary, POSITIVE, PFLOAT 4607182418800017408, 0) = S_binary[.RESULT = KNOWN (PFLOAT 4607182418800017408)]
$compiled_special_concat_bytes(S_binary, porigin_binary_child) = eps
''')


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    watched = [Path(__file__), Path(prior.__file__), Path(prior.prior.__file__), Path(prior.floating.__file__)]
    before = {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.cases = cases
    runner.conditions = conditions
    runner.compiler_conditions = compiler_conditions
    runner.CONTROLS = {STRING_CONTROL: runner.CONTROLS[STRING_CONTROL], BINARY_CONTROL: b"<?php $x = (+(1+0.0) . false) . 'x';\n"}
    passed = runner.main(expected_outputs=cases.OUTPUTS)
    assert before == {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = 'Four fresh nested numeric-unary CONCAT source-state fixtures, all intermediate own facts/precision, unchanged terminal literal authority and genuine numeric-string/binary-child compiler refusals. Prior source/native/state/compiler cuts retain their identities without replay.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
