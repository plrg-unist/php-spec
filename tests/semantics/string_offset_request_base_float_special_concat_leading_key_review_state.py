#!/usr/bin/env python3
"""Independent float/special CONCAT precision, pool and borrowed-owner checks."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_float_special_concat_leading_key_cases as cases
import string_offset_request_base_integer_special_concat_leading_key_review_state as prior

runner = prior.runner
base_compiler_conditions = runner.compiler_conditions
runner.HELPERS += r'''
dec $float_review_precision(ppool*, porigin, int) : ppool*
def $float_review_precision(eps, porigin, z) = eps
def $float_review_precision(ppool :: ppool_tail*, PORIGIN n pcpath, z) = ppool[.CONSTANTS = (PCCPRECISION pcpath z) :: ppool.CONSTANTS] :: ppool_tail*
  -- if ppool.UNIT = n
def $float_review_precision(ppool :: ppool_tail*, PORIGIN n pcpath, z) = ppool :: $float_review_precision(ppool_tail*, PORIGIN n pcpath, z)
  -- if ppool.UNIT =/= n
'''


def conditions(program, path, index):
    checks, derived = prior.conditions(program, path, index)
    integer = 3 if index == 2 else 1
    bits = 4613937818241073175 if index == 2 else 4607182418800017453
    old_node = 'NScalarInt (INTEGER ' + str(integer) + ') metadata_integer'
    new_node = 'NScalarFloat (FLOAT text_numeric) metadata_numeric'
    checks = [check.replace(old_node, new_node).replace('porigin_integer', 'porigin_float') for check in checks]
    old = '$compiled_read(S, porigin_float) = (PINT ' + str(integer) + ')'
    checks[checks.index(old)] = '$compiled_read(S, porigin_float) = (PFLOAT ' + str(bits) + ')'
    old = '$parser_literal_at(' + new_node + ', 14) = (PINT ' + str(integer) + ')'
    checks[checks.index(old)] = '$parser_literal_at(' + new_node + ', 14) = (PFLOAT ' + str(bits) + ')'
    at = checks.index('$compiled_special_concat_bytes(S, porigin_float) = ($ptascii("' + str(integer) + '"))') + 1
    checks[at:at] = [
        r'S.PRECISIONINI = $ptascii("17") /\ $precision_value(S) = 17',
        '$compiled_precision(S, (porigin_float)) = (14)',
        '$parser_literal_text_at(PFLOAT ' + str(bits) + ', 14) = ($ptascii("' + str(integer) + '"))',
        '$parser_literal_text_at(PFLOAT ' + str(bits) + ', 17) =/= ($ptascii("' + str(integer) + '"))']
    key = str(integer) + 'x'
    extra = runner.lines(r'''
S_live_precision = S_after[.PRECISIONINI = $ptascii("9")][.PRECISIONMODIFIED = true]
$precision_value(S_live_precision) = 9
$compiled_precision(S_live_precision, (porigin_float)) = (14)
S_no_precision = S_after[.POOLS = eps][.DECLARATIONS = eps]
$compiled_precision(S_no_precision, (porigin_float)) = eps
$compiled_special_concat_bytes(S_no_precision, porigin_float) = eps
$string_read_request_base_saved(S_no_precision, pstringread) = eps
S_wrong_precision = S_after[.POOLS = $float_review_precision(S_after.POOLS, porigin_float, 17)]
$compiled_precision(S_wrong_precision, (porigin_float)) = (17)
$compiled_special_concat_bytes(S_wrong_precision, porigin_key) = eps
$string_read_request_base_saved(S_wrong_precision, pstringread) = eps
S_float_fact = S_after[.POOLS = $special_review_pools(S_after.POOLS, porigin_special, (PFLOAT 4607182418800017408))]
$compiled_read(S_float_fact, porigin_special) = (PFLOAT 4607182418800017408)
$compiled_special_concat_bytes(S_float_fact, porigin_key) = eps
$string_read_request_base_saved(S_float_fact, pstringread) = eps
$parser_literal_text_at(PFLOAT 9221120237041090560, 14) = eps
''') + [
        '$compiled_special_concat_bytes(S_live_precision, porigin_key) = ($ptascii("' + key + '"))',
        '$string_read_request_base_saved(S_live_precision, pstringread) = (' + str(integer) + ')',
        '$compiled_read(S_wrong_precision, porigin_key) = (PSTRING ($ptascii("' + key + '")))',
        '$compiled_string_value(S_wrong_precision, porigin_key, PSTRING ($ptascii("' + key + '"))) = PSTRING ($ptascii("' + key + '"))']
    checks += extra
    return checks, derived + len(extra)


def compiler_conditions(checked, paths):
    assert list(checked) == ['mixed-leading-numeric-string-unary-special']
    return base_compiler_conditions(checked, paths) + runner.lines(r'''
$origin_child((porigin_control_0), [PCFIELD 0, PCFIELD 0]) = (porigin_unary)
$origin_node(S_control_0.SOURCES, porigin_unary) = (NExprUnaryPlus expression_nested metadata_unary)
$compiled_read(S_control_0, porigin_unary) = eps
$compiled_special_concat_bytes(S_control_0, porigin_unary) = eps
$parser_literal_at(expression_nested, 14) = eps
$origin_child((porigin_unary), [PCFIELD 0]) = (porigin_inner_unary)
$origin_node(S_control_0.SOURCES, porigin_inner_unary) = (NExprUnaryPlus expression_string metadata_inner_unary)
$compiled_read(S_control_0, porigin_inner_unary) = eps
$compiled_special_concat_bytes(S_control_0, porigin_inner_unary) = eps
$origin_child((porigin_inner_unary), [PCFIELD 0]) = (porigin_string)
$origin_node(S_control_0.SOURCES, porigin_string) = (expression_string)
expression_string = NScalarString (BYTES text_numeric) metadata_string
$base64(text_numeric) = $ptascii("1.0tail")
$parser_literal_at(expression_string, 14) = (PSTRING ($ptascii("1.0tail")))
$coerce_number(PSTRING ($ptascii("1.0tail"))) = COERCED (NFLOAT 4607182418800017408) true
''')


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    own_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    prior_hash = hashlib.sha256(Path(prior.__file__).read_bytes()).hexdigest()
    runner.cases = cases
    runner.conditions = conditions
    runner.compiler_conditions = compiler_conditions
    runner.CONTROLS = {'mixed-leading-numeric-string-unary-special': runner.CONTROLS['mixed-leading-numeric-string-unary-special']}
    passed = runner.main()
    assert hashlib.sha256(Path(__file__).read_bytes()).hexdigest() == own_hash
    assert hashlib.sha256(Path(prior.__file__).read_bytes()).hexdigest() == prior_hash
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'][str(Path(__file__).resolve())] = own_hash
    report['inputs'][str(Path(prior.__file__).resolve())] = prior_hash
    report['scope'] = 'Three new rounded float/special source-state fixtures and only the affected warningful numeric-string unary compiler exclusion; prior integer, special, numeric, source and native campaigns retain their original cuts without replay.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
