#!/usr/bin/env python3
"""Independent genuine NaN-child VALUE and exact arithmetic-result checks."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_nan_child_arithmetic_special_concat_leading_key_cases as cases
import string_offset_request_base_nan_child_arithmetic_special_concat_leading_key_protocol as source
import string_offset_request_base_arithmetic_nan_special_concat_leading_key_review_state as prior

runner, numeric, NAN = prior.runner, prior.numeric, prior.NAN
PRODUCERS = {'add': ('NAN + 1', 'ADD'), 'div': ('INF / NAN', 'DIVIDE'),
             'mul': ('NAN * NAN', 'MULTIPLY'), 'sub': ('NAN - (INF - INF)', 'SUBTRACT'),
             'nested': ('(NAN + 1) * (INF / NAN)', 'MULTIPLY'),
             'signed': ('(+NAN) - (-NAN)', 'SUBTRACT')}
PARTNERS = {'number': ('1.5', 'PFLOAT 4609434218613702656'),
            'nan': ('NAN', 'PFLOAT ' + NAN), 'text': ("'NAN'", 'PSTRING ($ptascii("NAN"))')}
ROWS = {operation.lower() + '-' + str(reverse):
        (('add', 'div', 'mul', 'sub')[index % 4], operation, 'number', reverse)
        for index, operation in enumerate(numeric.OPERATORS) for reverse in (False, True)}
ROWS |= {operation.lower() + '-' + producer + '-' + str(reverse): (producer, operation, 'nan', reverse)
         for producer in PRODUCERS for operation in ('IDENTICAL', 'NOTIDENTICAL') for reverse in (False, True)}
ROWS |= {operation.lower() + '-text-' + str(reverse): ('nested', operation, 'text', reverse)
         for operation in ('NOTEQUAL', 'SPACESHIP') for reverse in (False, True)}
CONTROLS = {}
for name, (producer, operation, partner, reverse) in ROWS.items():
    operands = (PARTNERS[partner][0], PRODUCERS[producer][0]) if reverse else (PRODUCERS[producer][0], PARTNERS[partner][0])
    CONTROLS[name] = ('<?php $x = ((' + operands[0] + ' ' + prior.OPERATORS[operation] + ' ' + operands[1] + ") . null) . 'x';\n").encode()
for name, expression in {'boolean-child': 'NAN + false', 'null-child': 'NAN + null',
                         'string-child': "NAN + '1'", 'warning-child': "NAN + '1x'", 'zero-divisor': 'NAN / 0',
                         'power': 'NAN ** 2', 'modulo': 'NAN % 1', 'float-not': '!NAN',
                         'array-child': '+[NAN]', 'variable-child': 'NAN + $missing'}.items():
    CONTROLS[name] = ('<?php $x = (((' + expression + ") === NAN) . null) . 'x';\n").encode()
STALE = {'stale-' + name: row for name, row in prior.PRODUCERS.items()}
for name, (expression, _, _, _) in STALE.items():
    CONTROLS[name] = ('<?php $x = ((' + expression + " !== NAN) . null) . 'x';\n").encode()


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    tag = ('nan_child_arithmetic_root_l', 'nan_child_arithmetic_root_child_l',
           'nan_child_arithmetic_root_l_l', 'nan_child_arithmetic_root_child_l_l')[index]
    origin, bits = 'porigin_' + tag, source.BITS
    guards = [origin + ' = PORIGIN n_nan_child_review pcpath_nan_child_review']
    for label, replacement in (('drop', 'eps'), ('sign', '(PFLOAT $float_neg(' + bits + '))'),
                               ('invalid', '(PFLOAT 18446744073709551616)'), ('finite', '(PFLOAT 4607182418800017408)'),
                               ('raw', '(PSTRING ($ptascii("NAN")))'), ('array', '(PARRAY 0)'), ('object', '(POBJECT 0)')):
        state = 'S_nan_child_review_' + label
        guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + origin + ', ' + replacement + ')]',
                   '$compiled_comparison_number(' + state + ', ' + origin + ') = eps',
                   '$compiled_special_concat_bytes(' + state + ', porigin_key) = eps']
    for field, suffix in enumerate(('_l', '_r')):
        child = origin + suffix
        guards += [child + ' = PORIGIN n_nan_child_review pcpath_nan_child_review_' + str(field)]
        for label, replacement in (('drop', 'eps'), ('invalid', '(PFLOAT 18446744073709551616)'),
                                   ('range', '(PINT 9223372036854775808)'), ('bool', '(PBOOL true)'), ('null', '(PNULL)'),
                                   ('raw', '(PSTRING ($ptascii("1")))'), ('carrier', '(PSTRING_CARRIER INTERNED_STRING ($ptascii("1")))')):
            state = 'S_nan_child_review_child_' + str(field) + '_' + label
            admitted = ((index == 0 and field == 1 and label in ('bool', 'null', 'raw'))
                        or (index == 1 and field == 0 and label in ('bool', 'null'))
                        or (index == 2 and label in ('bool', 'null')))
            guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + child + ', ' + replacement + ')]',
                       '$compiled_comparison_number(' + state + ', ' + origin + ') = ' + ('(NFLOAT ' + bits + ')' if admitted else 'eps'),
                       '$compiled_special_concat_bytes(' + state + ', porigin_key) = ' + ('($ptascii(' + json.dumps(('1x', '-1x', '0x', '-4x')[index]) + '))' if admitted else 'eps')]
            if admitted:
                guards += ['$compiled_identity_value(' + state + ', ' + child + ') = ' + replacement,
                           '$compiled_comparison_number(' + state + ', ' + child + ') = eps']
        state = 'S_nan_child_review_source_' + str(field)
        guards += [state + ' = S_after[.SOURCES = [{ID n_nan_child_review, AST (PROGRAM eps), OCCURRENCES ([(PCOCCURRENCE pcpath_nan_child_review expression_' + tag + '), (PCOCCURRENCE pcpath_nan_child_review_' + str(field) + ' (NExprVariable (BYTES "dW5hdXRo") eps))])}]]',
                   '$compiled_comparison_number(' + state + ', ' + origin + ') = eps']
    for number, node in enumerate((origin, origin + '_l', origin + '_r')):
        state = 'S_nan_child_review_precision_' + str(number)
        guards += [state + ' = S_after[.POOLS = $float_review_precision(S_after.POOLS, ' + node + ', 17)]',
                   '$compiled_precision(' + state + ', (' + node + ')) = (17)',
                   '$compiled_comparison_number(' + state + ', ' + origin + ') = eps',
                   '$compiled_special_concat_bytes(' + state + ', porigin_key) = eps']
    precision = 'S_after.POOLS'
    for node in (origin, origin + '_l', origin + '_r') + ((origin + '_r_l', origin + '_r_r') if index == 3 else ()):
        precision = '$float_review_precision(' + precision + ', ' + node + ', 17)'
    guards += ['S_nan_child_review_all_precision = S_after[.POOLS = ' + precision + ']',
               '$compiled_comparison_number(S_nan_child_review_all_precision, ' + origin + ') = (NFLOAT ' + bits + ')',
               '$compiled_special_concat_bytes(S_nan_child_review_all_precision, porigin_key) = eps',
               'S_nan_child_review_source = S_after[.SOURCES = [{ID n_nan_child_review, AST (PROGRAM eps), OCCURRENCES ([(PCOCCURRENCE pcpath_nan_child_review (NExprVariable (BYTES "dW5hdXRo") eps))])}]]',
               '$compiled_read(S_nan_child_review_source, ' + origin + ') = (PFLOAT ' + bits + ')',
               '$compiled_comparison_number(S_nan_child_review_source, ' + origin + ') = eps',
               'S_nan_child_review_no_code = S_after[.CODE = eps]',
               '$compiled_comparison_number(S_nan_child_review_no_code, ' + origin + ') = eps',
               'S_nan_child_review_live = S_after[.PRECISIONINI = $ptascii("9")][.PRECISIONMODIFIED = true]',
               '$compiled_comparison_number(S_nan_child_review_live, ' + origin + ') = (NFLOAT ' + bits + ')',
               '$compiled_special_concat_bytes(S_nan_child_review_live, porigin_key) = ($ptascii(' + json.dumps(('1x', '-1x', '0x', '-4x')[index]) + '))']
    child = origin + ('_r' if index == 1 else '_l')
    left = source.floats.POSITIVE[0] if index == 1 else 'PFLOAT ' + NAN
    right = ('PINT 1', 'PFLOAT ' + NAN, 'PFLOAT ' + NAN, source.prior.VALUE[0])[index]
    operation = ('ADD', 'DIVIDE', 'MULTIPLY', 'SUBTRACT')[index]
    if index == 0:
        finite = 'NScalarFloat (FLOAT "3ff0000000000000") eps'
        guards += ['S_nan_child_review_finite_source = S_after[.SOURCES = [{ID n_nan_child_review, AST (PROGRAM eps), OCCURRENCES ([(PCOCCURRENCE pcpath_nan_child_review (NExprBinaryOpPlus (' + finite + ') expression_' + tag + '_r metadata_' + tag + ')), (PCOCCURRENCE pcpath_nan_child_review_0 (' + finite + ')), (PCOCCURRENCE pcpath_nan_child_review_1 expression_' + tag + '_r)])}]]',
                   '$compiled_read(S_nan_child_review_finite_source, ' + child + ') = (PFLOAT ' + NAN + ')',
                   '$compiled_special_concat_bytes(S_nan_child_review_finite_source, ' + child + ') = ($ptascii("1"))',
                   '$compiled_comparison_number(S_nan_child_review_finite_source, ' + child + ') = eps',
                   '$compiled_comparison_number(S_nan_child_review_finite_source, ' + origin + ') = eps']
    for label, alternative in (('sign', '$float_neg(' + NAN + ')'), ('payload', '9221120237041090561')):
        state, result = 'S_nan_child_review_coherent_' + label, 'n_nan_child_review_' + label
        a, b = (left, 'PFLOAT ' + alternative) if index == 1 else ('PFLOAT ' + alternative, right)
        guards += [state + '_pure = $binary_apply(S_after, ' + operation + ', ' + a + ', ' + b + ', 0)',
                   state + '_pure.RESULT = KNOWN (PFLOAT ' + result + ')',
                   state + '_pure = S_after[.RESULT = KNOWN (PFLOAT ' + result + ')]',
                   state + ' = S_after[.POOLS = $special_review_pools($special_review_pools(S_after.POOLS, ' + child + ', (PFLOAT ' + alternative + ')), ' + origin + ', (PFLOAT ' + result + '))]',
                   '$compiled_comparison_number(' + state + ', ' + child + ') = (NFLOAT ' + alternative + ')',
                   '$compiled_special_concat_bytes(' + state + ', ' + child + ') = eps',
                   '$compiled_comparison_number(' + state + ', ' + origin + ') = (NFLOAT ' + result + ')',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps',
                   '$compiled_special_concat_bytes(' + state + ', porigin_key) = ($ptascii(' + json.dumps(('1x', '-1x', '0x', '-4x')[index]) + '))']
    return checks + guards, derived + len(guards)


def compiler_conditions(checked, paths):
    checks, certified = [], set()
    for index, name in enumerate(checked):
        state, origin = 'S_nan_child_control_' + str(index), 'porigin_nan_child_control_' + str(index)
        binary, own = origin + '_binary', origin + '_producer'
        checks += [state + ' = $php_run(' + checked[name]['fixture'] + ', 0, ' + json.dumps(base64.b64encode(bytes(paths[name])).decode()) + ')',
                   state + '.COMPLETION = BUDGET',
                   '$special_review_concat_path(' + state + '.SOURCES[0].OCCURRENCES) = (pcpath_nan_child_control_' + str(index) + ')',
                   origin + ' = PORIGIN 0 pcpath_nan_child_control_' + str(index),
                   '$origin_child((' + origin + '), [PCFIELD 0, PCFIELD 0]) = (' + binary + ')']
        if name not in ROWS:
            checks += ['$origin_child((' + binary + '), [PCFIELD 0]) = (' + own + ')']
            if name in ('boolean-child', 'null-child', 'string-child', 'power'):
                bits = 'n_nan_child_coercive_' + str(index)
                checks += ['$compiled_read(' + state + ', ' + own + ') = (PFLOAT ' + bits + ')',
                           '$fparts_nan($float_decode(' + bits + '))',
                           '$compiled_comparison_number(' + state + ', ' + own + ') = (NFLOAT ' + bits + ')',
                           '$compiled_special_concat_bytes(' + state + ', ' + own + ') = eps',
                           '$compiled_read(' + state + ', ' + binary + ') = (PBOOL false)',
                           '$compiled_special_concat_bytes(' + state + ', ' + binary + ') = ($ptascii(""))',
                           '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = ($ptascii("x"))',
                           '$compiled_string_value(' + state + ', ' + origin + ', PSTRING ($ptascii("x"))) = PSTRING_CARRIER INTERNED_STRING ($ptascii("x"))']
                continue
            if name not in STALE:
                checks += ['$compiled_comparison_number(' + state + ', ' + own + ') = eps',
                           '$compiled_special_concat_bytes(' + state + ', ' + binary + ') = eps',
                           '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
                continue
            _, operation, left, right = STALE[name]
            bits, changed_bits = 'n_nan_child_old_' + str(index), 'n_nan_child_new_' + str(index)
            changed, coherent = state + '_stale', state + '_coherent'
            checks += ['$number_binary(' + operation + ', ' + left + ', ' + right + ') = NUM (NFLOAT ' + bits + ')',
                       '$compiled_read(' + state + ', ' + own + ') = (PFLOAT ' + bits + ')',
                       '$origin_child((' + own + '), [PCFIELD 0]) = (' + own + '_child)',
                       changed + ' = ' + state + '[.POOLS = $special_review_pools(' + state + '.POOLS, ' + own + '_child, (PFLOAT ' + NAN + '))]',
                       '$compiled_comparison_number(' + changed + ', ' + own + '_child) = (NFLOAT ' + NAN + ')',
                       '$number_binary(' + operation + ', NFLOAT ' + NAN + ', ' + right + ') = NUM (NFLOAT ' + changed_bits + ')',
                       changed_bits + ' =/= ' + bits,
                       '$compiled_comparison_number(' + changed + ', ' + own + ') = eps',
                       '$compiled_special_concat_bytes(' + changed + ', ' + origin + ') = eps',
                       coherent + ' = ' + changed + '[.POOLS = $special_review_pools(' + changed + '.POOLS, ' + own + ', (PFLOAT ' + changed_bits + '))]',
                       '$compiled_comparison_number(' + coherent + ', ' + own + ') = (NFLOAT ' + changed_bits + ')',
                       '$compiled_special_concat_bytes(' + coherent + ', ' + own + ') = eps',
                       '$compiled_special_concat_bytes(' + coherent + ', ' + origin + ') = ($ptascii("1x"))']
            continue
        producer, operation, partner, reverse = ROWS[name]
        result = 1 if operation == 'SPACESHIP' else operation in ('NOTEQUAL', 'NOTIDENTICAL')
        text, value, bits = numeric.text(result), numeric.value(result), 'n_nan_child_control_' + str(index)
        checks += ['$compiled_read(' + state + ', ' + binary + ') = (' + value + ')',
                   '$compiled_special_concat_bytes(' + state + ', ' + binary + ') = ($ptascii(' + json.dumps(text) + '))',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = ($ptascii(' + json.dumps(text + 'x') + '))',
                   '$compiled_string_value(' + state + ', ' + origin + ', PSTRING ($ptascii(' + json.dumps(text + 'x') + '))) = PSTRING_CARRIER INTERNED_STRING ($ptascii(' + json.dumps(text + 'x') + '))',
                   '$origin_child((' + binary + '), [PCFIELD ' + str(1 if reverse else 0) + ']) = (' + own + ')',
                   '$origin_child((' + binary + '), [PCFIELD ' + str(0 if reverse else 1) + ']) = (' + binary + '_partner)',
                   '$compiled_read(' + state + ', ' + binary + '_partner) = (' + PARTNERS[partner][1] + ')',
                   '$compiled_read(' + state + ', ' + own + ') = (PFLOAT ' + bits + ')',
                   '$fparts_nan($float_decode(' + bits + '))',
                   '$compiled_comparison_number(' + state + ', ' + own + ') = (NFLOAT ' + bits + ')',
                   '$compiled_special_concat_bytes(' + state + ', ' + own + ') = eps']
        if producer in certified:
            continue
        certified.add(producer)
        expression, operation = 'expression_nan_child_' + str(index), PRODUCERS[producer][1]
        checks += ['$origin_node(' + state + '.SOURCES, ' + own + ') = (' + expression + ')',
                   '$pfshape(' + expression + ') = PFBINARY ' + operation + ' ' + expression + '_l ' + expression + '_r',
                   '$compiled_precision(' + state + ', (' + own + ')) = (14)']
        for field, suffix in enumerate(('_l', '_r')):
            child, value, number = own + suffix, 'pvalue_nan_child_' + str(index) + suffix, 'pnumber_nan_child_' + str(index) + suffix
            checks += ['$origin_child((' + own + '), [PCFIELD ' + str(field) + ']) = (' + child + ')',
                       '$origin_node(' + state + '.SOURCES, ' + child + ') = (' + expression + suffix + ')',
                       '$compiled_precision(' + state + ', (' + child + ')) = (14)',
                       '$compiled_read(' + state + ', ' + child + ') = (' + value + ')',
                       '$compiled_comparison_number(' + state + ', ' + child + ') = (' + number + ')',
                       '$coerce_number(' + value + ') = COERCED ' + number + ' false']
        checks += ['$compiled_order_number(pvalue_nan_child_' + str(index) + r'_l) = eps \/ $compiled_order_number(pvalue_nan_child_' + str(index) + '_r) = eps',
                   '$number_binary(' + operation + ', pnumber_nan_child_' + str(index) + '_l, pnumber_nan_child_' + str(index) + '_r) = NUM (NFLOAT ' + bits + ')',
                   '$binary_apply(' + state + ', ' + operation + ', pvalue_nan_child_' + str(index) + '_l, pvalue_nan_child_' + str(index) + '_r, 0) = ' + state + '[.RESULT = KNOWN (PFLOAT ' + bits + ')]']
    return checks


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    watched = [Path(module.__file__) for module in (source, source.prior, source.prior.prior, source.floats, source.nan, source.arithmetic, source.unary, prior, numeric, runner)] + [Path(__file__)]
    before = {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.cases, runner.conditions = cases, conditions
    runner.compiler_conditions, runner.CONTROLS = compiler_conditions, CONTROLS
    passed = runner.main(expected_outputs=cases.OUTPUTS)
    assert before == {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = 'Four authentic NaN-child arithmetic fixtures retain source, own/child reads, exact quiet result bits, three matching capture precisions and genuine child VALUE. Only pointwise same-result bool/null and exact raw-one child mutations now admit through scalar identity VALUE at the existing compiler-proof boundary; other malformed/range/source/code and sign-mismatch controls remain. Signed/payload child changes recompute the own bits before checking admission. Compiler tables cover four operations, both orientations, seven weak/two strict comparisons, raw-string partners, nested/unary-NaN children and the three reviewed quiet-coercive selectors. The former power selector now checks separate quiet POWERDONE NaN VALUE admission. Four stale-result controls retain old sign refusals and coherent child+own admissions. Prior campaigns retain their original cuts; NaN BYTE, owning children, other operators, FLOAT NOT and exact held lanes remain partial. Source/native observations are reused once; fixture/compiler evidence carries source0.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
