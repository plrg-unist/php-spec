#!/usr/bin/env python3
"""Runtime float-NOT keys retain real carriers and existing Warning histories."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_float_boolnot_special_concat_leading_key_cases as cases
import string_offset_request_base_boolnot_special_concat_leading_key_protocol as prior

runner = prior.runner
BITS = (0, 9223372036854775808, 9218868437227405312, 4613937818241073152)
KEYS = ('1x', '-1x', '0x', '-4x')


def authority(index):
    truth = index >= 2
    boolean = str(truth).lower()
    value = 'PFLOAT ' + str(BITS[index])
    checks = [
        '$origin_child((porigin_key), [PCFIELD 0]) = (porigin_float_concat)',
        '$origin_node(S.SOURCES, porigin_float_concat) = (expression_1)',
        'expression_1 = NExprBinaryOpConcat expression_prefix expression_float_not metadata_float_concat',
        '$origin_child((porigin_float_concat), [PCFIELD 0]) = (porigin_float_prefix)',
        '$origin_child((porigin_float_concat), [PCFIELD 1]) = (porigin_float_not)',
        '$origin_node(S.SOURCES, porigin_float_prefix) = (expression_prefix)',
        '$origin_node(S.SOURCES, porigin_float_not) = (expression_float_not)',
        'expression_float_not = NExprBooleanNot expression_float_child metadata_float_not',
        '$origin_child((porigin_float_not), [PCFIELD 0]) = (porigin_float_child)',
        '$origin_node(S.SOURCES, porigin_float_child) = (expression_float_child)',
        '$compiled_read(S, porigin_float_child) = (' + value + ')',
        '$compiled_identity_value(S, porigin_float_child) = (' + value + ')',
        '$number_bool(NFLOAT ' + str(BITS[index]) + ') = (' + boolean + ', false)',
        '$truth_value(S, ' + value + ', 5) = S[.RESULT = KNOWN (PBOOL ' + boolean + ')]',
        '$string_read_runtime_bytes(S, porigin_float_not) = ($echo_value(PBOOL ' + str(not truth).lower() + '))',
        r'S.PRECISIONINI = $ptascii("17") /\ $precision_value(S) = 17']
    for tag in ('key', 'float_concat', 'float_not'):
        checks += ['porigin_' + tag + ' = PORIGIN n_runtime_unit pcpath_runtime_' + tag,
                   '$code_at(S.CODE, n_runtime_unit) = (pcode_runtime)',
                   '$code_expression(pcode_runtime.EXPRESSIONS, pcpath_runtime_' + tag + ') = ((5, false))',
                   '$compiled_read(S, porigin_' + tag + ') = eps',
                   '$compiled_precision(S, (porigin_' + tag + ')) = (14)',
                   '$compiled_special_concat_bytes(S, porigin_' + tag + ') = eps']
    checks += ['$compiled_precision(S, (porigin_float_child)) = (14)',
               '$string_read_runtime_bytes(S, porigin_key) = ($ptascii(' + json.dumps(KEYS[index]) + '))']
    if index == 0:
        checks += ['expression_float_child = NScalarFloat (FLOAT text_float_child) metadata_float_child',
                   '$hex_bits(text_float_child, 0) = 0']
    elif index == 1:
        checks += ['expression_float_child = NExprUnaryMinus expression_float_zero metadata_float_child',
                   '$origin_child((porigin_float_child), [PCFIELD 0]) = (porigin_float_zero)',
                   '$compiled_read(S, porigin_float_zero) = (PFLOAT 0)',
                   '$unary_apply(S, NEGATIVE, PFLOAT 0, 5) = S[.RESULT = KNOWN (' + value + ')]']
    elif index == 2:
        checks += ['expression_float_child = NExprConstFetch name_float_inf metadata_float_child',
                   '$ptast(name_float_inf) = PTNAME PTPLAIN ($ptascii("INF"))']
    else:
        checks += ['expression_float_child = NExprBinaryOpPlus expression_float_left expression_float_right metadata_float_child',
                   '$origin_child((porigin_float_child), [PCFIELD 0]) = (porigin_float_left)',
                   '$origin_child((porigin_float_child), [PCFIELD 1]) = (porigin_float_right)',
                   '$compiled_read(S, porigin_float_left) = (PFLOAT 4607182418800017408)',
                   '$compiled_read(S, porigin_float_right) = (PFLOAT 4611686018427387904)',
                   '$binary_apply(S, ADD, PFLOAT 4607182418800017408, PFLOAT 4611686018427387904, 5) = S[.RESULT = KNOWN (' + value + ')]']
    return checks


def conditions(program, path, index):
    checks, derived = prior.conditions(program, path, index)
    old = prior.authority(index)
    at = checks.index(old[0])
    assert checks[at:at + len(old)] == old
    checks[at:at + len(old)] = authority(index)
    at = checks.index('$origin_child((porigin_key), [PCFIELD 0, PCFIELD 1]) = (porigin_special)')
    del checks[at:at + 4]
    key = KEYS[index]
    replacements = {
        'pstringread.READ.VALUE = PSTRING_CARRIER INTERNED_STRING ($ptascii(' + json.dumps(key) + '))':
            'pstringread.READ.VALUE = PSTRING_CARRIER (REQUEST_STRING n_runtime_key_identity) ($ptascii(' + json.dumps(key) + '))',
        '$compiled_special_concat_bytes(S, porigin_key) = ($ptascii(' + json.dumps(key) + '))':
            '$string_read_runtime_bytes(S, porigin_key) = ($ptascii(' + json.dumps(key) + '))',
        '$compiled_read(S, porigin_key) = (PSTRING ($ptascii(' + json.dumps(key) + ')))':
            '$compiled_read(S, porigin_key) = eps',
        '$compiled_string_value(S, porigin_key, PSTRING ($ptascii(' + json.dumps(key) + '))) = pstringread.READ.VALUE':
            '$compiled_string_value(S, porigin_key, PSTRING ($ptascii(' + json.dumps(key) + '))) = PSTRING ($ptascii(' + json.dumps(key) + '))'}
    for old, new in replacements.items():
        assert old in checks, old
        checks[checks.index(old)] = new
    checks += ['$string_carrier_valid(S, pstringread.READ.VALUE)',
               'S.STRINGDATA[n_runtime_key_identity] = $ptascii(' + json.dumps(key) + ')',
               'n_runtime_key_identity =/= n_base_identity',
               '$string_read_runtime_bytes(S_no_code, porigin_key) = eps',
               '$string_read_runtime_bytes(S_no_pools, porigin_key) = eps',
               '$string_read_runtime_bytes(S_no_source, porigin_key) = eps']
    return checks, derived + 6


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    watched = [Path(module.__file__) for module in (prior, prior.prior, prior.strings, prior.arithmetic, runner)] + [Path(__file__)]
    before = {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.cases, runner.OUTPUTS, runner.conditions = cases, tuple(cases.OUTPUTS.values()), conditions
    passed = runner.main()
    assert before == {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = 'Four original-source runtime FLOAT NOT/CONCAT fixtures keep actual false CODE descriptors, absent own compiled reads, genuine scalar child values, quiet full-state truth and real REQUEST key carriers. Existing return, negative index, supplied throw and bounds histories retain source/owner/cleanup/budget guards. Compiler BYTE and INTERNED normalization remain absent at runtime roots. Fixtures add source0 and reuse native originals once.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
