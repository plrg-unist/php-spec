#!/usr/bin/env python3
"""Independent quiet arithmetic NaN VALUE and compiler-provenance checks."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_arithmetic_nan_special_concat_leading_key_cases as cases
import string_offset_request_base_arithmetic_nan_special_concat_leading_key_protocol as source
import string_offset_request_base_numeric_comparison_special_concat_leading_key_review_state as numeric

runner, INF, NAN = numeric.runner, source.floats.INF, source.nan.NAN
PRODUCERS = {
    'sub': ('(INF - INF)', 'SUBTRACT', 'NFLOAT ' + INF, 'NFLOAT ' + INF),
    'div': ('(INF / INF)', 'DIVIDE', 'NFLOAT ' + INF, 'NFLOAT ' + INF),
    'mul': ('(INF * 0)', 'MULTIPLY', 'NFLOAT ' + INF, 'NINT 0'),
    'add': ('(INF + -INF)', 'ADD', 'NFLOAT ' + INF, 'NFLOAT ' + source.floats.NINF)}
PARTNERS = {'number': ('1.5', 'PFLOAT 4609434218613702656'),
            'nan': ('NAN', 'PFLOAT ' + NAN), 'text': ("'NAN'", 'PSTRING ($ptascii("NAN"))')}
OPERATORS = numeric.OPERATORS | {'IDENTICAL': '===', 'NOTIDENTICAL': '!=='}
ROWS = {operation.lower() + '-sub-' + str(reverse): ('sub', operation, 'number', reverse)
        for operation in numeric.OPERATORS for reverse in (False, True)}
ROWS |= {operation.lower() + '-' + producer + '-' + str(reverse): (producer, operation, 'nan', reverse)
         for producer in PRODUCERS for operation in ('IDENTICAL', 'NOTIDENTICAL') for reverse in (False, True)}
ROWS |= {'space-' + producer + '-' + str(reverse): (producer, 'SPACESHIP', 'number', reverse)
         for producer in ('div', 'mul', 'add') for reverse in (False, True)}
ROWS |= {operation.lower() + '-text-' + str(reverse): ('add', operation, 'text', reverse)
         for operation in numeric.OPERATORS for reverse in (False, True)}
CONTROLS = {}
for name, (producer, operation, partner, reverse) in ROWS.items():
    left, right = (PARTNERS[partner][0], PRODUCERS[producer][0]) if reverse else (PRODUCERS[producer][0], PARTNERS[partner][0])
    CONTROLS[name] = ('<?php $x = ((' + left + ' ' + OPERATORS[operation] + ' ' + right + ") . null) . 'x';\n").encode()
for name, expression in {'nan-child': 'NAN + 1', 'right-nan': 'INF + NAN', 'both-nan': 'NAN - NAN',
                         'unary-nan': '-NAN', 'boolean-child': 'INF * false', 'null-child': 'INF * null',
                         'string-child': "INF * '0'", 'unary-computed': '-(INF - INF)'}.items():
    CONTROLS[name] = ('<?php $x = (((' + expression + ") === NAN) . null) . 'x';\n").encode()


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    tag = ('arithmetic_nan_root_l', 'arithmetic_nan_root_child_l',
           'arithmetic_nan_root_l_l', 'arithmetic_nan_root_child_l_l')[index]
    origin, bits = 'porigin_' + tag, source.BITS
    guards = [origin + ' = PORIGIN n_arithmetic_review pcpath_arithmetic_review',
              '$compiled_read(S_after, ' + origin + ') = (PFLOAT ' + bits + ')',
              '$compiled_comparison_number(S_after, ' + origin + ') = (NFLOAT ' + bits + ')',
              '$compiled_special_concat_bytes(S_after, ' + origin + ') = eps',
              '$float_neg(' + bits + ') =/= ' + bits,
              '$fparts_nan($float_decode($float_neg(' + bits + ')))']
    for label, replacement in (('drop', 'eps'), ('sign', '(PFLOAT $float_neg(' + bits + '))'),
                               ('invalid', '(PFLOAT 18446744073709551616)'),
                               ('finite', '(PFLOAT 4607182418800017408)'),
                               ('raw', '(PSTRING ($ptascii("NAN")))'),
                               ('carrier', '(PSTRING_CARRIER INTERNED_STRING ($ptascii("NAN")))'),
                               ('array', '(PARRAY 0)'), ('object', '(POBJECT 0)')):
        state = 'S_arithmetic_review_' + label
        guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + origin + ', ' + replacement + ')]',
                   '$compiled_comparison_number(' + state + ', ' + origin + ') = eps',
                   '$compiled_special_concat_bytes(' + state + ', porigin_key) = eps']
    for field, child in enumerate((origin + '_l', origin + '_r')):
        for label, replacement in (('drop', 'eps'), ('nan', '(PFLOAT ' + NAN + ')'),
                                   ('invalid', '(PFLOAT 18446744073709551616)'),
                                   ('range', '(PINT 9223372036854775808)'),
                                   ('bool', '(PBOOL false)'), ('null', '(PNULL)'),
                                   ('string', '(PSTRING ($ptascii("0")))')):
            state = 'S_arithmetic_review_child_' + str(field) + '_' + label
            admitted = index == 2 and field == 1 and label in ('bool', 'null', 'string')
            guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + child + ', ' + replacement + ')]',
                       '$compiled_comparison_number(' + state + ', ' + origin + ') = ' + ('(NFLOAT ' + bits + ')' if admitted else 'eps'),
                       '$compiled_special_concat_bytes(' + state + ', porigin_key) = ' + ('($ptascii("0x"))' if admitted else 'eps')]
            if admitted:
                guards += ['$compiled_identity_value(' + state + ', ' + child + ') = ' + replacement,
                           '$compiled_comparison_number(' + state + ', ' + child + ') = eps']
    for number, node in enumerate((origin, origin + '_l', origin + '_r')):
        state = 'S_arithmetic_review_precision_' + str(number)
        guards += [state + ' = S_after[.POOLS = $float_review_precision(S_after.POOLS, ' + node + ', 17)]',
                   '$compiled_precision(' + state + ', (' + node + ')) = (17)',
                   '$compiled_comparison_number(' + state + ', ' + origin + ') = eps',
                   '$compiled_special_concat_bytes(' + state + ', porigin_key) = eps']
    precision = 'S_after.POOLS'
    for node in (origin, origin + '_l', origin + '_r') + ((origin + '_r_child',) if index == 3 else ()):
        precision = '$float_review_precision(' + precision + ', ' + node + ', 17)'
    guards += ['S_arithmetic_review_all_precision = S_after[.POOLS = ' + precision + ']',
               '$compiled_comparison_number(S_arithmetic_review_all_precision, ' + origin + ') = (NFLOAT ' + bits + ')',
               '$compiled_special_concat_bytes(S_arithmetic_review_all_precision, porigin_key) = eps',
               'S_arithmetic_review_source = S_after[.SOURCES = [{ID n_arithmetic_review, AST (PROGRAM eps), OCCURRENCES ([(PCOCCURRENCE pcpath_arithmetic_review (NExprVariable (BYTES "dW5hdXRo") eps))])}]]',
               '$compiled_read(S_arithmetic_review_source, ' + origin + ') = (PFLOAT ' + bits + ')',
               '$compiled_comparison_number(S_arithmetic_review_source, ' + origin + ') = eps',
               'S_arithmetic_review_no_code = S_after[.CODE = eps]',
               '$compiled_comparison_number(S_arithmetic_review_no_code, ' + origin + ') = eps',
               'S_arithmetic_review_live = S_after[.PRECISIONINI = $ptascii("9")][.PRECISIONMODIFIED = true]',
               '$compiled_comparison_number(S_arithmetic_review_live, ' + origin + ') = (NFLOAT ' + bits + ')',
               '$compiled_special_concat_bytes(S_arithmetic_review_live, porigin_key) = ($ptascii(' + json.dumps(('1x', '-1x', '0x', '-4x')[index]) + '))']
    if index == 2:
        guards += ['$coerce_number(PBOOL false) = COERCED (NINT 0) false',
                   '$number_binary(MULTIPLY, NFLOAT ' + INF + ', NINT 0) = NUM (NFLOAT ' + bits + ')',
                   '$compiled_order_number(PBOOL false) = eps']
    return checks + guards, derived + len(guards)


def compiler_conditions(checked, paths):
    checks = []
    for index, name in enumerate(checked):
        state, origin = 'S_arithmetic_control_' + str(index), 'porigin_arithmetic_control_' + str(index)
        binary = origin + '_binary'
        checks += [state + ' = $php_run(' + checked[name]['fixture'] + ', 0, ' + json.dumps(base64.b64encode(bytes(paths[name])).decode()) + ')',
                   state + '.COMPLETION = BUDGET',
                   '$special_review_concat_path(' + state + '.SOURCES[0].OCCURRENCES) = (pcpath_arithmetic_control_' + str(index) + ')',
                   origin + ' = PORIGIN 0 pcpath_arithmetic_control_' + str(index),
                   '$origin_child((' + origin + '), [PCFIELD 0, PCFIELD 0]) = (' + binary + ')']
        if name not in ROWS:
            if name in ('nan-child', 'right-nan', 'both-nan', 'boolean-child', 'null-child', 'string-child'):
                bits = 'n_arithmetic_control_nan_child_' + str(index)
                checks += ['$origin_child((' + binary + '), [PCFIELD 0]) = (' + binary + '_producer)',
                           '$compiled_read(' + state + ', ' + binary + '_producer) = (PFLOAT ' + bits + ')',
                           '$fparts_nan($float_decode(' + bits + '))',
                           '$compiled_comparison_number(' + state + ', ' + binary + '_producer) = (NFLOAT ' + bits + ')',
                           '$compiled_special_concat_bytes(' + state + ', ' + binary + '_producer) = eps',
                           '$compiled_read(' + state + ', ' + binary + ') = (PBOOL false)',
                           '$compiled_special_concat_bytes(' + state + ', ' + binary + ') = ($ptascii(""))',
                           '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = ($ptascii("x"))',
                           '$compiled_string_value(' + state + ', ' + origin + ', PSTRING ($ptascii("x"))) = PSTRING_CARRIER INTERNED_STRING ($ptascii("x"))']
                continue
            if name in ('unary-nan', 'unary-computed'):
                bits = 'n_arithmetic_control_unary_' + str(index)
                checks += ['$origin_child((' + binary + '), [PCFIELD 0]) = (' + binary + '_producer)',
                           '$compiled_read(' + state + ', ' + binary + '_producer) = (PFLOAT ' + bits + ')',
                           '$fparts_nan($float_decode(' + bits + '))',
                           '$compiled_comparison_number(' + state + ', ' + binary + '_producer) = (NFLOAT ' + bits + ')',
                           '$compiled_special_concat_bytes(' + state + ', ' + binary + '_producer) = eps',
                           '$compiled_read(' + state + ', ' + binary + ') = (PBOOL false)',
                           '$compiled_special_concat_bytes(' + state + ', ' + binary + ') = ($ptascii(""))',
                           '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = ($ptascii("x"))',
                           '$compiled_string_value(' + state + ', ' + origin + ', PSTRING ($ptascii("x"))) = PSTRING_CARRIER INTERNED_STRING ($ptascii("x"))']
                continue
            checks += ['$origin_child((' + binary + '), [PCFIELD 0]) = (' + binary + '_producer)',
                       '$compiled_comparison_number(' + state + ', ' + binary + '_producer) = eps',
                       '$compiled_special_concat_bytes(' + state + ', ' + binary + ') = eps',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
            continue
        producer, operation, partner, reverse = ROWS[name]
        _, arithmetic, left_number, right_number = PRODUCERS[producer]
        bits = 'n_arithmetic_control_' + str(index)
        result = 1 if operation == 'SPACESHIP' else operation in ('NOTEQUAL', 'NOTIDENTICAL')
        text, value = numeric.text(result), numeric.value(result)
        checks += ['$number_binary(' + arithmetic + ', ' + left_number + ', ' + right_number + ') = NUM (NFLOAT ' + bits + ')',
                   '$fparts_nan($float_decode(' + bits + '))',
                   '$compiled_read(' + state + ', ' + binary + ') = (' + value + ')',
                   '$compiled_special_concat_bytes(' + state + ', ' + binary + ') = ($ptascii(' + json.dumps(text) + '))',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = ($ptascii(' + json.dumps(text + 'x') + '))',
                   '$compiled_string_value(' + state + ', ' + origin + ', PSTRING ($ptascii(' + json.dumps(text + 'x') + '))) = PSTRING_CARRIER INTERNED_STRING ($ptascii(' + json.dumps(text + 'x') + '))',
                   '$origin_child((' + binary + '), [PCFIELD ' + str(1 if reverse else 0) + ']) = (' + binary + '_producer)',
                   '$compiled_read(' + state + ', ' + binary + '_producer) = (PFLOAT ' + bits + ')',
                   '$compiled_comparison_number(' + state + ', ' + binary + '_producer) = (NFLOAT ' + bits + ')',
                   '$compiled_special_concat_bytes(' + state + ', ' + binary + '_producer) = eps',
                   '$origin_child((' + binary + '), [PCFIELD ' + str(0 if reverse else 1) + ']) = (' + binary + '_partner)',
                   '$compiled_read(' + state + ', ' + binary + '_partner) = (' + PARTNERS[partner][1] + ')',
                   '$compiled_precision(' + state + ', (' + binary + ')) = (14)',
                   '$compiled_precision(' + state + ', (' + binary + '_producer)) = (14)',
                   '$compiled_precision(' + state + ', (' + binary + '_partner)) = (14)']
    return checks


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    watched = [Path(module.__file__) for module in (source, source.prior, source.floats, source.nan, source.strings, source.arithmetic, source.unary, numeric, runner)] + [Path(__file__)]
    before = {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.cases, runner.conditions = cases, conditions
    runner.compiler_conditions, runner.CONTROLS = compiler_conditions, CONTROLS
    passed = runner.main(expected_outputs=cases.OUTPUTS)
    assert before == {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = 'Four authentic arithmetic-NaN fixtures add own read/type/valid64/exact signed-result bits, missing source/code, child reads/ranges and three precision controls. At the existing compiler-proof boundary, only the MULTIPLY right-child false/null/raw-zero mutations now admit their genuine scalar VALUE and unchanged quiet result bits; all other recorded malformed/sign-mismatch controls remain. Matching all producer precisions admits VALUE while its unchanged parent precision still refuses BYTE; live precision does not alter the compiled key. Independent compiler controls cover seven weak operators/both orientations, numeric/raw-string partners and strict comparisons. Three former quiet-coercive selectors now check separate scalar VALUE admission alongside the previously accepted NaN-child and unary selectors; this update does not renew the old fixture/compiler campaigns. Exact own pure arithmetic bits remain bound and NaN BYTE absent; source/native4 once and held boundaries retain their original cuts, with fixture/compiler source0.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
