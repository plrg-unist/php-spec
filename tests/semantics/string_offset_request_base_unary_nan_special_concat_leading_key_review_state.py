#!/usr/bin/env python3
"""Independent unary NaN VALUE, exact result and recursive provenance checks."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_unary_nan_special_concat_leading_key_cases as cases
import string_offset_request_base_unary_nan_special_concat_leading_key_protocol as source
import string_offset_request_base_arithmetic_nan_special_concat_leading_key_review_state as prior

runner, numeric, NAN, INF = prior.runner, prior.numeric, prior.NAN, prior.INF
PRODUCERS = {
    'positive': ('+NAN', ('POSITIVE',), False),
    'negative': ('-NAN', ('NEGATIVE',), False),
    'computed-positive': ('+(INF - INF)', ('POSITIVE',), True),
    'computed-negative': ('-(INF - INF)', ('NEGATIVE',), True),
    'nested-negative': ('-(-NAN)', ('NEGATIVE', 'NEGATIVE'), False),
    'nested-mixed': ('+(-(+(-(INF - INF))))', ('POSITIVE', 'NEGATIVE', 'POSITIVE', 'NEGATIVE'), True)}
PARTNERS = {'number': ('1.5', 'PFLOAT 4609434218613702656'),
            'nan': ('NAN', 'PFLOAT ' + NAN), 'text': ("'NAN'", 'PSTRING ($ptascii("NAN"))'),
            'true': ('true', 'PBOOL true'), 'null': ('null', 'PNULL')}
ROWS = {operation.lower() + '-' + str(reverse):
        ('positive' if index % 2 else 'negative', operation, 'number', reverse)
        for index, operation in enumerate(numeric.OPERATORS) for reverse in (False, True)}
ROWS |= {operation.lower() + '-' + producer + '-' + str(reverse): (producer, operation, 'nan', reverse)
         for producer in PRODUCERS for operation in ('IDENTICAL', 'NOTIDENTICAL') for reverse in (False, True)}
ROWS |= {operation.lower() + '-text-' + str(reverse): ('computed-negative', operation, 'text', reverse)
         for operation in ('NOTEQUAL', 'SPACESHIP') for reverse in (False, True)}
ROWS |= {'strict-' + partner + '-' + str(reverse): ('nested-mixed', 'NOTIDENTICAL', partner, reverse)
         for partner in ('true', 'null') for reverse in (False, True)}
CONTROLS = {}
for name, (producer, operation, partner, reverse) in ROWS.items():
    operands = (PARTNERS[partner][0], PRODUCERS[producer][0]) if reverse else (PRODUCERS[producer][0], PARTNERS[partner][0])
    CONTROLS[name] = ('<?php $x = ((' + operands[0] + ' ' + prior.OPERATORS[operation] + ' ' + operands[1] + ") . null) . 'x';\n").encode()
for name, expression in {'nan-child-binary': 'NAN + 1', 'unary-child-binary': '(+NAN) + 1',
                         'unary-over-nan-binary': '+((INF - INF) + 1)', 'unary-coercive-child': '+(INF * false)',
                         'float-not': '!NAN', 'signed-float-not': '+(!NAN)',
                         'string-nan': "+'NAN'", 'variable': '+$missing'}.items():
    CONTROLS[name] = ('<?php $x = (((' + expression + ") === NAN) . null) . 'x';\n").encode()


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    tag = ('unary_nan_root_l', 'unary_nan_root_child_l',
           'unary_nan_root_l_l', 'unary_nan_root_child_l_l')[index]
    origin, bits = 'porigin_' + tag, source.BITS
    child, child_bits = origin + '_child', NAN if index < 2 else source.prior.BITS
    operation = 'POSITIVE' if index in (0, 3) else 'NEGATIVE'
    guards = [origin + ' = PORIGIN n_unary_review pcpath_unary_review',
              child + ' = PORIGIN n_unary_review pcpath_unary_review_child',
              '$compiled_read(S_after, ' + origin + ') = (PFLOAT ' + bits + ')',
              '$compiled_comparison_number(S_after, ' + origin + ') = (NFLOAT ' + bits + ')',
              '$compiled_special_concat_bytes(S_after, ' + origin + ') = eps']
    for label, replacement in (('drop', 'eps'), ('sign', '(PFLOAT $float_neg(' + bits + '))'),
                               ('invalid', '(PFLOAT 18446744073709551616)'), ('finite', '(PFLOAT 4607182418800017408)'),
                               ('raw', '(PSTRING ($ptascii("NAN")))'), ('carrier', '(PSTRING_CARRIER INTERNED_STRING ($ptascii("NAN")))'),
                               ('array', '(PARRAY 0)'), ('object', '(POBJECT 0)')):
        state = 'S_unary_review_' + label
        guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + origin + ', ' + replacement + ')]',
                   '$compiled_comparison_number(' + state + ', ' + origin + ') = eps',
                   '$compiled_special_concat_bytes(' + state + ', porigin_key) = eps']
    for label, replacement in (('drop', 'eps'), ('invalid', '(PFLOAT 18446744073709551616)'),
                               ('finite', '(PFLOAT 4607182418800017408)'), ('int', '(PINT 0)'),
                               ('bool', '(PBOOL false)'), ('null', '(PNULL)'),
                               ('raw', '(PSTRING ($ptascii("NAN")))'), ('carrier', '(PSTRING_CARRIER INTERNED_STRING ($ptascii("NAN")))')):
        state = 'S_unary_review_child_' + label
        guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + child + ', ' + replacement + ')]',
                   '$compiled_comparison_number(' + state + ', ' + origin + ') = eps',
                   '$compiled_special_concat_bytes(' + state + ', porigin_key) = eps']
    for number, node in enumerate((origin, child)):
        state = 'S_unary_review_precision_' + str(number)
        guards += [state + ' = S_after[.POOLS = $float_review_precision(S_after.POOLS, ' + node + ', 17)]',
                   '$compiled_precision(' + state + ', (' + node + ')) = (17)',
                   '$compiled_comparison_number(' + state + ', ' + origin + ') = eps',
                   '$compiled_special_concat_bytes(' + state + ', porigin_key) = eps']
    precision = 'S_after.POOLS'
    for node in (origin, child) + ((child + '_l', child + '_r') if index >= 2 else ()):
        precision = '$float_review_precision(' + precision + ', ' + node + ', 17)'
    guards += ['S_unary_review_all_precision = S_after[.POOLS = ' + precision + ']',
               '$compiled_comparison_number(S_unary_review_all_precision, ' + origin + ') = (NFLOAT ' + bits + ')',
               '$compiled_special_concat_bytes(S_unary_review_all_precision, porigin_key) = eps',
               'S_unary_review_source = S_after[.SOURCES = [{ID n_unary_review, AST (PROGRAM eps), OCCURRENCES ([(PCOCCURRENCE pcpath_unary_review (NExprVariable (BYTES "dW5hdXRo") eps))])}]]',
               '$compiled_read(S_unary_review_source, ' + origin + ') = (PFLOAT ' + bits + ')',
               '$compiled_comparison_number(S_unary_review_source, ' + origin + ') = eps',
               'S_unary_review_child_source = S_after[.SOURCES = [{ID n_unary_review, AST (PROGRAM eps), OCCURRENCES ([(PCOCCURRENCE pcpath_unary_review expression_' + tag + '), (PCOCCURRENCE pcpath_unary_review_child (NExprVariable (BYTES "dW5hdXRo") eps))])}]]',
               '$compiled_comparison_number(S_unary_review_child_source, ' + origin + ') = eps',
               'S_unary_review_no_code = S_after[.CODE = eps]',
               '$compiled_comparison_number(S_unary_review_no_code, ' + origin + ') = eps',
               'S_unary_review_live = S_after[.PRECISIONINI = $ptascii("9")][.PRECISIONMODIFIED = true]',
               '$compiled_comparison_number(S_unary_review_live, ' + origin + ') = (NFLOAT ' + bits + ')',
               '$compiled_special_concat_bytes(S_unary_review_live, porigin_key) = ($ptascii(' + json.dumps(('1x', '-1x', '0x', '-4x')[index]) + '))']
    if index < 2:
        for label, alternative in (('sign', '$float_neg(' + NAN + ')'), ('payload', '9221120237041090561')):
            state, result = 'S_unary_review_coherent_' + label, 'n_unary_review_' + label
            guards += [state + '_pure = $unary_apply(S_after, ' + operation + ', PFLOAT ' + alternative + ', 0)',
                       state + '_pure.RESULT = KNOWN (PFLOAT ' + result + ')',
                       state + '_pure = S_after[.RESULT = KNOWN (PFLOAT ' + result + ')]',
                       state + ' = S_after[.POOLS = $special_review_pools($special_review_pools(S_after.POOLS, ' + child + ', (PFLOAT ' + alternative + ')), ' + origin + ', (PFLOAT ' + result + '))]',
                       '$compiled_comparison_number(' + state + ', ' + child + ') = (NFLOAT ' + alternative + ')',
                       '$compiled_special_concat_bytes(' + state + ', ' + child + ') = eps',
                       '$compiled_comparison_number(' + state + ', ' + origin + ') = (NFLOAT ' + result + ')',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps',
                       '$compiled_special_concat_bytes(' + state + ', porigin_key) = ($ptascii(' + json.dumps(('1x', '-1x')[index]) + '))']
        finite = 'NScalarFloat (FLOAT "3ff0000000000000") eps'
        outer = ('NExprUnaryPlus' if operation == 'POSITIVE' else 'NExprUnaryMinus') + ' (' + finite + ') metadata_' + tag
        guards += ['S_unary_review_finite_source = S_after[.SOURCES = [{ID n_unary_review, AST (PROGRAM eps), OCCURRENCES ([(PCOCCURRENCE pcpath_unary_review (' + outer + ')), (PCOCCURRENCE pcpath_unary_review_child (' + finite + '))])}]]',
                   '$compiled_read(S_unary_review_finite_source, ' + child + ') = (PFLOAT ' + child_bits + ')',
                   '$compiled_special_concat_bytes(S_unary_review_finite_source, ' + child + ') = ($ptascii("1"))',
                   '$compiled_comparison_number(S_unary_review_finite_source, ' + child + ') = eps',
                   '$compiled_comparison_number(S_unary_review_finite_source, ' + origin + ') = eps']
    return checks + guards, derived + len(guards)


def compiler_conditions(checked, paths):
    checks, certified = [], set()
    for index, name in enumerate(checked):
        state, origin = 'S_unary_control_' + str(index), 'porigin_unary_control_' + str(index)
        binary = origin + '_binary'
        checks += [state + ' = $php_run(' + checked[name]['fixture'] + ', 0, ' + json.dumps(base64.b64encode(bytes(paths[name])).decode()) + ')',
                   state + '.COMPLETION = BUDGET',
                   '$special_review_concat_path(' + state + '.SOURCES[0].OCCURRENCES) = (pcpath_unary_control_' + str(index) + ')',
                   origin + ' = PORIGIN 0 pcpath_unary_control_' + str(index),
                   '$origin_child((' + origin + '), [PCFIELD 0, PCFIELD 0]) = (' + binary + ')']
        if name not in ROWS:
            checks += ['$origin_child((' + binary + '), [PCFIELD 0]) = (' + binary + '_producer)',
                       '$compiled_comparison_number(' + state + ', ' + binary + '_producer) = eps',
                       '$compiled_special_concat_bytes(' + state + ', ' + binary + ') = eps',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
            continue
        producer, operation, partner, reverse = ROWS[name]
        result = 1 if operation == 'SPACESHIP' else operation in ('NOTEQUAL', 'NOTIDENTICAL')
        text, value = numeric.text(result), numeric.value(result)
        own = binary + '_producer'
        checks += ['$compiled_read(' + state + ', ' + binary + ') = (' + value + ')',
                   '$compiled_special_concat_bytes(' + state + ', ' + binary + ') = ($ptascii(' + json.dumps(text) + '))',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = ($ptascii(' + json.dumps(text + 'x') + '))',
                   '$compiled_string_value(' + state + ', ' + origin + ', PSTRING ($ptascii(' + json.dumps(text + 'x') + '))) = PSTRING_CARRIER INTERNED_STRING ($ptascii(' + json.dumps(text + 'x') + '))',
                   '$origin_child((' + binary + '), [PCFIELD ' + str(1 if reverse else 0) + ']) = (' + own + ')',
                   '$origin_child((' + binary + '), [PCFIELD ' + str(0 if reverse else 1) + ']) = (' + binary + '_partner)',
                   '$compiled_read(' + state + ', ' + binary + '_partner) = (' + PARTNERS[partner][1] + ')']
        # Inspect each distinct chain once; every occurrence retains VALUE/BYTE.
        if producer in certified:
            bits = 'n_unary_control_' + str(index) + '_value'
            checks += ['$compiled_read(' + state + ', ' + own + ') = (PFLOAT ' + bits + ')',
                       '$fparts_nan($float_decode(' + bits + '))',
                       '$compiled_comparison_number(' + state + ', ' + own + ') = (NFLOAT ' + bits + ')',
                       '$compiled_special_concat_bytes(' + state + ', ' + own + ') = eps']
            continue
        certified.add(producer)
        for level, unary in enumerate(PRODUCERS[producer][1]):
            child, expression = own + '_child', 'expression_unary_control_' + str(index) + '_' + str(level)
            bits, child_bits = 'n_unary_control_' + str(index) + '_' + str(level), 'n_unary_control_' + str(index) + '_' + str(level + 1)
            checks += ['$origin_node(' + state + '.SOURCES, ' + own + ') = (' + expression + ')',
                       '$pfshape(' + expression + ') = PFUNARY ' + unary + ' ' + expression + '_child',
                       '$origin_child((' + own + '), [PCFIELD 0]) = (' + child + ')',
                       '$origin_node(' + state + '.SOURCES, ' + child + ') = (' + expression + '_child)',
                       '$compiled_read(' + state + ', ' + own + ') = (PFLOAT ' + bits + ')',
                       '$compiled_read(' + state + ', ' + child + ') = (PFLOAT ' + child_bits + ')',
                       '$compiled_precision(' + state + ', (' + own + ')) = (14)',
                       '$compiled_precision(' + state + ', (' + child + ')) = (14)',
                       '$fparts_nan($float_decode(' + bits + '))',
                       '$compiled_comparison_number(' + state + ', ' + own + ') = (NFLOAT ' + bits + ')',
                       '$compiled_comparison_number(' + state + ', ' + child + ') = (NFLOAT ' + child_bits + ')',
                       '$compiled_special_concat_bytes(' + state + ', ' + own + ') = eps',
                       '$compiled_special_concat_bytes(' + state + ', ' + child + ') = eps',
                       '$unary_apply(' + state + ', ' + unary + ', PFLOAT ' + child_bits + ', 0) = ' + state + '[.RESULT = KNOWN (PFLOAT ' + bits + ')]']
            own = child
        checks += [('$number_binary(SUBTRACT, NFLOAT ' + INF + ', NFLOAT ' + INF + ') = NUM (NFLOAT ' + child_bits + ')')
                   if PRODUCERS[producer][2] else child_bits + ' = ' + NAN]
    return checks


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    watched = [Path(module.__file__) for module in (source, source.prior, source.prior.prior, source.floats, source.arithmetic, source.unary, prior, numeric, runner)] + [Path(__file__)]
    before = {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.cases, runner.conditions = cases, conditions
    runner.compiler_conditions, runner.CONTROLS = compiler_conditions, CONTROLS
    passed = runner.main(expected_outputs=cases.OUTPUTS)
    assert before == {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = 'Four authentic unary-NaN fixtures retain exact author prefixes and add independent own/child read/type/valid64, signed-result, source/code and both precision guards. Coherent signed/payload ConstFetch NaNs bind the exact pure unary result before dependent checks; no canonical result payload is assumed. A coherent finite-source NaN read retains literal BYTE but fails genuine child VALUE. Matching every unary/producer precision retains VALUE while the unchanged parent refuses BYTE; live precision preserves the key. Fresh compiler tables cover both signs, finite nested chains, admitted arithmetic children, seven weak operators/both orientations, strict comparisons, raw-string and quiet scalar partners. NaN BYTE, FLOAT NOT, arithmetic with NaN children, coercive/uncertified producers, owners/lifetimes and held Source47 remain separate. Source/native originals are reused once; fixture/compiler conditions carry source0 without renewing prior campaigns.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
