#!/usr/bin/env python3
"""Independent quiet coercion, genuine scalar VALUE and arithmetic NaN checks."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_coercive_arithmetic_nan_special_concat_leading_key_cases as cases
import string_offset_request_base_coercive_arithmetic_nan_special_concat_leading_key_protocol as source
import string_offset_request_base_arithmetic_nan_special_concat_leading_key_review_state as prior

runner, numeric, NAN = prior.runner, prior.numeric, prior.NAN
PRODUCERS = {
    'mul': ('INF * false', 'MULTIPLY'), 'div': ("INF / '1e999'", 'DIVIDE'),
    'sub': ("INF - '1e999'", 'SUBTRACT'), 'add': ("'1e999' + -INF", 'ADD'),
    'mul-null': ('INF * null', 'MULTIPLY'), 'mul-string': ("INF * '0'", 'MULTIPLY'),
    'nan-bool': ('NAN + false', 'ADD'), 'nan-null': ('NAN - null', 'SUBTRACT'),
    'nan-string': ("NAN * '1'", 'MULTIPLY'), 'bool-nan': ('true + NAN', 'ADD'),
    'null-nan': ('null - NAN', 'SUBTRACT'), 'string-nan': ("'1e999' / NAN", 'DIVIDE'),
    'nested': ("(INF * false) + (NAN * '1')", 'ADD')}
ROWS = {operation.lower() + '-' + str(reverse):
        (('mul', 'div', 'sub', 'add')[index % 4], operation, 'number', reverse)
        for index, operation in enumerate(numeric.OPERATORS) for reverse in (False, True)}
ROWS |= {operation.lower() + '-' + producer + '-' + str(reverse): (producer, operation, 'nan', reverse)
         for producer in ('mul', 'div', 'sub', 'add')
         for operation in ('IDENTICAL', 'NOTIDENTICAL') for reverse in (False, True)}
ROWS |= {'strict-' + producer: (producer, 'NOTIDENTICAL', 'nan', bool(index % 2))
         for index, producer in enumerate(PRODUCERS) if producer not in ('mul', 'div', 'sub', 'add')}
ROWS |= {operation.lower() + '-text-' + str(reverse): ('nan-string', operation, 'text', reverse)
         for operation in ('NOTEQUAL', 'SPACESHIP') for reverse in (False, True)}
CONTROLS = {}
for name, (producer, operation, partner, reverse) in ROWS.items():
    operands = (prior.PARTNERS[partner][0], PRODUCERS[producer][0]) if reverse else (PRODUCERS[producer][0], prior.PARTNERS[partner][0])
    CONTROLS[name] = ('<?php $x = ((' + operands[0] + ' ' + prior.OPERATORS[operation] + ' ' + operands[1] + ") . null) . 'x';\n").encode()
for name, expression in {'warning-child': "NAN + '1x'", 'nonnumeric-child': "NAN + 'x'",
                         'zero-divisor': 'NAN / false', 'array-child': 'NAN + []',
                         'variable-child': 'NAN + $missing', 'power': "NAN ** '2'",
                         'modulo': 'NAN % 1', 'float-not': '!NAN', 'string-nan': "+'NAN'"}.items():
    CONTROLS[name] = ('<?php $x = (((' + expression + ") === NAN) . null) . 'x';\n").encode()


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    tag = ('coercive_arithmetic_nan_root_l', 'coercive_arithmetic_nan_root_child_l',
           'coercive_arithmetic_nan_root_l_l', 'coercive_arithmetic_nan_root_child_l_l')[index]
    origin, bits = 'porigin_' + tag, source.BITS
    guards = [origin + ' = PORIGIN n_coercive_review pcpath_coercive_review']
    for label, replacement in (('drop', 'eps'), ('sign', '(PFLOAT $float_neg(' + bits + '))'),
                               ('invalid', '(PFLOAT 18446744073709551616)'), ('finite', '(PFLOAT 4607182418800017408)'),
                               ('raw', '(PSTRING ($ptascii("NAN")))'),
                               ('carrier', '(PSTRING_CARRIER INTERNED_STRING ($ptascii("NAN")))'),
                               ('array', '(PARRAY 0)'), ('object', '(POBJECT 0)')):
        state = 'S_coercive_review_' + label
        guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + origin + ', ' + replacement + ')]',
                   '$compiled_comparison_number(' + state + ', ' + origin + ') = eps',
                   '$compiled_special_concat_bytes(' + state + ', porigin_key) = eps']
    for field, suffix in enumerate(('_l', '_r')):
        child = origin + suffix
        guards += [child + ' = PORIGIN n_coercive_review pcpath_coercive_review_' + str(field)]
        for label, replacement in (('drop', 'eps'), ('invalid', '(PFLOAT 18446744073709551616)'),
                                   ('range', '(PINT 9223372036854775808)'), ('raw', '(PSTRING ($ptascii("wrong")))'),
                                   ('carrier', '(PSTRING_CARRIER INTERNED_STRING ($ptascii("1e999")))'),
                                   ('array', '(PARRAY 0)'), ('object', '(POBJECT 0)')):
            state = 'S_coercive_review_child_' + str(field) + '_' + label
            guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + child + ', ' + replacement + ')]',
                       '$compiled_comparison_number(' + state + ', ' + origin + ') = eps',
                       '$compiled_special_concat_bytes(' + state + ', porigin_key) = eps']
        state = 'S_coercive_review_source_' + str(field)
        guards += [state + ' = S_after[.SOURCES = [{ID n_coercive_review, AST (PROGRAM eps), OCCURRENCES ([(PCOCCURRENCE pcpath_coercive_review expression_' + tag + '), (PCOCCURRENCE pcpath_coercive_review_' + str(field) + ' (NExprVariable (BYTES "dW5hdXRo") eps))])}]]',
                   '$compiled_comparison_number(' + state + ', ' + origin + ') = eps']
    for number, node in enumerate((origin, origin + '_l', origin + '_r')):
        state = 'S_coercive_review_precision_' + str(number)
        guards += [state + ' = S_after[.POOLS = $float_review_precision(S_after.POOLS, ' + node + ', 17)]',
                   '$compiled_precision(' + state + ', (' + node + ')) = (17)',
                   '$compiled_comparison_number(' + state + ', ' + origin + ') = eps',
                   '$compiled_special_concat_bytes(' + state + ', porigin_key) = eps']
    precision = 'S_after.POOLS'
    for node in (origin, origin + '_l', origin + '_r') + ((origin + '_r_child',) if index == 3 else ()):
        precision = '$float_review_precision(' + precision + ', ' + node + ', 17)'
    guards += ['S_coercive_review_all_precision = S_after[.POOLS = ' + precision + ']',
               '$compiled_comparison_number(S_coercive_review_all_precision, ' + origin + ') = (NFLOAT ' + bits + ')',
               '$compiled_special_concat_bytes(S_coercive_review_all_precision, porigin_key) = eps',
               'S_coercive_review_source = S_after[.SOURCES = [{ID n_coercive_review, AST (PROGRAM eps), OCCURRENCES ([(PCOCCURRENCE pcpath_coercive_review (NExprVariable (BYTES "dW5hdXRo") eps))])}]]',
               '$compiled_read(S_coercive_review_source, ' + origin + ') = (PFLOAT ' + bits + ')',
               '$compiled_comparison_number(S_coercive_review_source, ' + origin + ') = eps',
               'S_coercive_review_no_code = S_after[.CODE = eps]',
               '$compiled_comparison_number(S_coercive_review_no_code, ' + origin + ') = eps',
               'S_coercive_review_live = S_after[.PRECISIONINI = $ptascii("9")][.PRECISIONMODIFIED = true]',
               '$compiled_comparison_number(S_coercive_review_live, ' + origin + ') = (NFLOAT ' + bits + ')',
               '$compiled_special_concat_bytes(S_coercive_review_live, porigin_key) = ($ptascii(' + json.dumps(('1x', '-1x', '0x', '-4x')[index]) + '))']
    if index == 0:
        guards += ['S_coercive_review_same_zero = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + origin + '_r, (PNULL))]',
                   '$compiled_identity_value(S_coercive_review_same_zero, ' + origin + '_r) = (PNULL)',
                   '$compiled_comparison_number(S_coercive_review_same_zero, ' + origin + ') = (NFLOAT ' + bits + ')',
                   '$compiled_special_concat_bytes(S_coercive_review_same_zero, porigin_key) = ($ptascii("1x"))']
    return checks + guards, derived + len(guards)


def compiler_conditions(checked, paths):
    checks, certified = [], set()
    for index, name in enumerate(checked):
        state, origin = 'S_coercive_control_' + str(index), 'porigin_coercive_control_' + str(index)
        binary, own = origin + '_binary', origin + '_producer'
        checks += [state + ' = $php_run(' + checked[name]['fixture'] + ', 0, ' + json.dumps(base64.b64encode(bytes(paths[name])).decode()) + ')',
                   state + '.COMPLETION = BUDGET',
                   '$special_review_concat_path(' + state + '.SOURCES[0].OCCURRENCES) = (pcpath_coercive_control_' + str(index) + ')',
                   origin + ' = PORIGIN 0 pcpath_coercive_control_' + str(index),
                   '$origin_child((' + origin + '), [PCFIELD 0, PCFIELD 0]) = (' + binary + ')']
        if name not in ROWS:
            checks += ['$origin_child((' + binary + '), [PCFIELD 0]) = (' + own + ')',
                       '$compiled_comparison_number(' + state + ', ' + own + ') = eps',
                       '$compiled_special_concat_bytes(' + state + ', ' + binary + ') = eps',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
            continue
        producer, operation, partner, reverse = ROWS[name]
        result = 1 if operation == 'SPACESHIP' else operation in ('NOTEQUAL', 'NOTIDENTICAL')
        text, value, bits = numeric.text(result), numeric.value(result), 'n_coercive_control_' + str(index)
        checks += ['$compiled_read(' + state + ', ' + binary + ') = (' + value + ')',
                   '$compiled_special_concat_bytes(' + state + ', ' + binary + ') = ($ptascii(' + json.dumps(text) + '))',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = ($ptascii(' + json.dumps(text + 'x') + '))',
                   '$compiled_string_value(' + state + ', ' + origin + ', PSTRING ($ptascii(' + json.dumps(text + 'x') + '))) = PSTRING_CARRIER INTERNED_STRING ($ptascii(' + json.dumps(text + 'x') + '))',
                   '$origin_child((' + binary + '), [PCFIELD ' + str(1 if reverse else 0) + ']) = (' + own + ')',
                   '$origin_child((' + binary + '), [PCFIELD ' + str(0 if reverse else 1) + ']) = (' + binary + '_partner)',
                   '$compiled_read(' + state + ', ' + binary + '_partner) = (' + prior.PARTNERS[partner][1] + ')',
                   '$compiled_read(' + state + ', ' + own + ') = (PFLOAT ' + bits + ')',
                   '$fparts_nan($float_decode(' + bits + '))',
                   '$compiled_comparison_number(' + state + ', ' + own + ') = (NFLOAT ' + bits + ')',
                   '$compiled_special_concat_bytes(' + state + ', ' + own + ') = eps']
        if producer in certified:
            continue
        certified.add(producer)
        expression, operation = 'expression_coercive_' + str(index), PRODUCERS[producer][1]
        checks += ['$origin_node(' + state + '.SOURCES, ' + own + ') = (' + expression + ')',
                   '$pfshape(' + expression + ') = PFBINARY ' + operation + ' ' + expression + '_l ' + expression + '_r',
                   '$compiled_precision(' + state + ', (' + own + ')) = (14)']
        for field, suffix in enumerate(('_l', '_r')):
            child, value, number = own + suffix, 'pvalue_coercive_' + str(index) + suffix, 'pnumber_coercive_' + str(index) + suffix
            checks += ['$origin_child((' + own + '), [PCFIELD ' + str(field) + ']) = (' + child + ')',
                       '$origin_node(' + state + '.SOURCES, ' + child + ') = (' + expression + suffix + ')',
                       '$compiled_precision(' + state + ', (' + child + ')) = (14)',
                       '$compiled_read(' + state + ', ' + child + ') = (' + value + ')',
                       '$compiled_identity_value(' + state + ', ' + child + ') = (' + value + ')',
                       '$coerce_number(' + value + ') = COERCED ' + number + ' false']
        if producer != 'nested':
            checks += ['$compiled_comparison_number(' + state + ', ' + own + r'_l) = eps \/ $compiled_comparison_number(' + state + ', ' + own + '_r) = eps']
        checks += ['$number_binary(' + operation + ', pnumber_coercive_' + str(index) + '_l, pnumber_coercive_' + str(index) + '_r) = NUM (NFLOAT ' + bits + ')',
                   '$binary_apply(' + state + ', ' + operation + ', pvalue_coercive_' + str(index) + '_l, pvalue_coercive_' + str(index) + '_r, 0) = ' + state + '[.RESULT = KNOWN (PFLOAT ' + bits + ')]']
        if producer == 'nan-bool':
            for label, alternative in (('sign', '$float_neg(' + NAN + ')'), ('payload', '9221120237041090561')):
                changed, result = state + '_' + label, 'n_coercive_' + label
                checks += [changed + '_pure = $binary_apply(' + state + ', ADD, PFLOAT ' + alternative + ', PBOOL false, 0)',
                           changed + '_pure.RESULT = KNOWN (PFLOAT ' + result + ')',
                           changed + '_pure = ' + state + '[.RESULT = KNOWN (PFLOAT ' + result + ')]',
                           result + ' =/= ' + bits,
                           changed + ' = ' + state + '[.POOLS = $special_review_pools(' + state + '.POOLS, ' + own + '_l, (PFLOAT ' + alternative + '))]',
                           '$compiled_comparison_number(' + changed + ', ' + own + ') = eps',
                           changed + '_coherent = ' + changed + '[.POOLS = $special_review_pools(' + changed + '.POOLS, ' + own + ', (PFLOAT ' + result + '))]',
                           '$compiled_identity_value(' + changed + '_coherent, ' + own + '_l) = (PFLOAT ' + alternative + ')',
                           '$compiled_comparison_number(' + changed + '_coherent, ' + own + ') = (NFLOAT ' + result + ')',
                           '$compiled_special_concat_bytes(' + changed + '_coherent, ' + own + ') = eps',
                           '$compiled_special_concat_bytes(' + changed + '_coherent, ' + origin + ') = ($ptascii("1x"))']
            finite = 'NScalarFloat (FLOAT "3ff0000000000000") eps'
            checks += [own + ' = PORIGIN n_coercive_finite pcpath_coercive_finite',
                       own + '_l = PORIGIN n_coercive_finite pcpath_coercive_finite_l',
                       own + '_r = PORIGIN n_coercive_finite pcpath_coercive_finite_r',
                       state + '_finite = ' + state + '[.SOURCES = [{ID n_coercive_finite, AST (PROGRAM eps), OCCURRENCES ([(PCOCCURRENCE pcpath_coercive_finite (NExprBinaryOpPlus (' + finite + ') ' + expression + '_r eps)), (PCOCCURRENCE pcpath_coercive_finite_l (' + finite + ')), (PCOCCURRENCE pcpath_coercive_finite_r ' + expression + '_r)])}]]',
                       '$compiled_special_concat_bytes(' + state + '_finite, ' + own + '_l) = ($ptascii("1"))',
                       '$compiled_identity_value(' + state + '_finite, ' + own + '_l) = eps',
                       '$compiled_comparison_number(' + state + '_finite, ' + own + ') = eps']
    return checks


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    watched = [Path(module.__file__) for module in (source, source.prior, source.prior.prior,
               source.nan, source.strings, source.floats, source.arithmetic, source.unary, prior, numeric, runner)] + [Path(__file__)]
    before = {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.cases, runner.conditions = cases, conditions
    runner.compiler_conditions, runner.CONTROLS = compiler_conditions, CONTROLS
    passed = runner.main(expected_outputs=cases.OUTPUTS)
    assert before == {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = 'Four authentic coercive-arithmetic NaN fixtures preserve actual own/child sources, reads, genuine scalar VALUE and quiet exact arithmetic at three matching compile precisions. Independent malformed, missing, range, owner/carrier, source/code and precision controls retain refusals; a quiet false-to-null same-result mutation admits at the existing compiler-proof boundary. Fresh compiler-only tables cover four operators, BOOL/NULL/full numeric strings, both NaN/scalar orientations, numeric and raw-string comparisons, strict comparisons and nested composition; warningful/nonnumeric, zero-divisor, owning/variable and other-operator controls refuse. NaN BYTE, FLOAT NOT, wider producers/lifetimes and held Source47 remain separate. Saved source/native observations are reused once; fixture/compiler conditions carry source0.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
