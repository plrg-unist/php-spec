#!/usr/bin/env python3
"""Independent Boolean priority, NULL/string exceptions and typed boundaries."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_bool_null_comparison_special_concat_leading_key_cases as cases
import string_offset_request_base_bool_null_comparison_special_concat_leading_key_protocol as source
import string_offset_request_base_numeric_comparison_special_concat_leading_key_review_state as numeric
import string_offset_request_base_string_comparison_special_concat_leading_key_review_state as strings

runner, raw = numeric.runner, source.strings.bytes_term
VALUES = {name: (php, value, None) for name, (php, value, number, _, _) in numeric.NUMBERS.items()}
VALUES |= {'false': ('false', 'PBOOL false', None), 'true': ('true', 'PBOOL true', None), 'null': ('null', 'PNULL', None)}
for name, data in (('s0', b'0'), ('empty', b''), ('nul', b'\0'), ('text', b'text'), ('high', b'\xff')):
    VALUES[name] = strings.literal(data), 'PSTRING ' + raw(data), data
VALUES['subnormal'] = '5e-324', 'PFLOAT 1', None
VALUES['nested-nan'] = '(NAN < 1)', 'PBOOL false', None
VALUES['nested-logical'] = '(1.5 && 1)', 'PBOOL true', None
ROWS = {operation.lower() + '-' + str(pair) + '-' + str(reverse):
        (operation, right if reverse else left, left if reverse else right, -order if reverse else order)
        for operation in numeric.OPERATORS for pair, (left, right, order) in enumerate(
            (('false', 's0', 0), ('null', 's0', -1), ('true', 's0', 1)))
        for reverse in (False, True)}
for name, left, right, order in (
        ('null-empty', 'null', 'empty', 0), ('empty-null', 'empty', 'null', 0),
        ('false-empty', 'false', 'empty', 0), ('false-nul', 'false', 'nul', -1),
        ('null-nul', 'null', 'nul', -1), ('true-text', 'true', 'text', 0),
        ('high-false', 'high', 'false', 1), ('true-false', 'true', 'false', 1),
        ('false-null', 'false', 'null', 0), ('true-null', 'true', 'null', 1),
        ('null-zero', 'null', 'i0', 0), ('null-negative', 'null', 'imin', -1),
        ('negative-zero-null', 'fn0', 'null', 0), ('false-infinity', 'false', 'finf', -1),
        ('infinity-true', 'finf', 'true', 0), ('null-subnormal', 'null', 'subnormal', -1),
        ('nested-nan-bool', 'nested-nan', 'false', 0), ('nested-logical-bool', 'nested-logical', 'true', 0)):
    ROWS[name] = 'SPACESHIP', left, right, order
CONTROLS = {name: ("<?php $x = ((" + VALUES[left][0] + ' ' + numeric.OPERATORS[operation] + ' ' + VALUES[right][0] + ") . null) . 'x';\n").encode()
            for name, (operation, left, right, order) in ROWS.items()} | {
    'no-priority': b"<?php $x = ((1.0000000000000002 > '1.0000000000000001x') . null) . 'x';\n",
    'nan-bool': b"<?php $x = ((NAN == true) . null) . 'x';\n",
    'bool-nan': b"<?php $x = ((false < NAN) . null) . 'x';\n",
    'array-bool': b"<?php $x = (([] == false) . null) . 'x';\n",
    'null-object': b"<?php $x = ((null == new stdClass()) . null) . 'x';\n",
    'variable': b"<?php $x = (($missing == false) . null) . 'x';\n",
    'not-float': b"<?php $x = ((!1.5) . null) . 'x';\n"}
PAYLOADS = ((b'', b'0'), (b'', b'0'), (b'1', b'text'), (b'0', b''))


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    tag = ('bool_root', 'bool_root', 'bool_root_l', 'bool_root_child_l')[index]
    origin, expression = 'porigin_' + tag, 'expression_' + tag
    guards = [origin + ' = PORIGIN n_priority pcpath_priority', origin + '_l = PORIGIN n_priority pcpath_priority_l',
              origin + '_r = PORIGIN n_priority pcpath_priority_r']
    wrong, wrong_type = (('PBOOL false', 'PINT 1'), ('PINT 0', 'PFLOAT 13830554455654793216'),
                         ('PBOOL true', 'PSTRING ($ptascii(""))'), ('PBOOL false', 'PINT 1'))[index]
    for label, replacement in (('drop', 'eps'), ('wrong', '(' + wrong + ')'), ('type', '(' + wrong_type + ')')):
        state = 'S_priority_' + label
        guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + origin + ', ' + replacement + ')]',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps',
                   '$string_read_request_base_saved(' + state + ', pstringread) = eps']
    for field, suffix in enumerate(('_l', '_r')):
        child = origin + suffix
        state = 'S_priority_drop' + suffix
        guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + child + ', eps)]',
                   '$compiled_read(' + state + ', ' + child + ') = eps',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
        state = 'S_priority_precision' + suffix
        guards += [state + ' = S_after[.POOLS = $float_review_precision(S_after.POOLS, ' + child + ', 17)]',
                   '$compiled_precision(' + state + ', (' + origin + ')) = (14)',
                   '$compiled_precision(' + state + ', (' + child + ')) = (17)',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
        state = 'S_priority_carrier' + suffix
        guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + child + ', (PSTRING_CARRIER INTERNED_STRING ' + raw(PAYLOADS[index][field]) + '))]',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
        if field == 0:
            guards += ['expression_priority_other = NExprVariable (BYTES "dW5hdXRo") metadata_' + tag]
        left, right = ('expression_priority_other', expression + '_r') if field == 0 else (expression + '_l', 'expression_priority_other')
        state = 'S_priority_source' + suffix
        guards += [state + ' = S_after[.SOURCES = [{ID n_priority, AST (PROGRAM eps), OCCURRENCES ([(PCOCCURRENCE pcpath_priority ' + expression + '), (PCOCCURRENCE pcpath_priority_l ' + left + '), (PCOCCURRENCE pcpath_priority_r ' + right + ')])}]]',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
    guards += ['S_priority_root_source = S_after[.SOURCES = [{ID n_priority, AST (PROGRAM eps), OCCURRENCES ([(PCOCCURRENCE pcpath_priority expression_priority_other), (PCOCCURRENCE pcpath_priority_l ' + expression + '_l), (PCOCCURRENCE pcpath_priority_r ' + expression + '_r)])}]]',
               '$compiled_special_concat_bytes(S_priority_root_source, ' + origin + ') = eps',
               'S_priority_precision = S_after[.POOLS = $float_review_precision(S_after.POOLS, ' + origin + ', 17)]',
               '$compiled_precision(S_priority_precision, (' + origin + ')) = (17)',
               '$compiled_precision(S_priority_precision, (' + origin + '_l)) = (14)',
               '$compiled_precision(S_priority_precision, (' + origin + '_r)) = (14)',
               '$compiled_special_concat_bytes(S_priority_precision, ' + origin + ') = eps',
               'S_priority_live = S_after[.PRECISIONINI = $ptascii("9")][.PRECISIONMODIFIED = true]',
               '$precision_value(S_priority_live) = 9',
               '$compiled_special_concat_bytes(S_priority_live, porigin_key) = ($ptascii("' + ('1x', '-1x', '0x', '-4x')[index] + '"))']
    if index < 3:
        original, changed = PAYLOADS[index][1], (b'', b'other', b'other')[index]
        guards += ['S_priority_bytes = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + origin + '_r, (PSTRING ' + raw(changed) + '))]',
                   '$compiled_special_concat_bytes(S_priority_bytes, ' + origin + '_r) = (' + raw(original) + ')',
                   '$scalar_plain_order(S_priority_bytes, ' + ('PBOOL false', 'PNULL', 'PBOOL true')[index] + ', PSTRING ' + raw(changed) + ') = ' + ('0', '$(-1)', '0')[index],
                   '$compiled_special_concat_bytes(S_priority_bytes, ' + origin + ') = eps']
    else:
        for label, value in (('nan', 'PFLOAT 9221120237041090560'), ('bits', 'PFLOAT 18446744073709551616'), ('range', 'PINT 9223372036854775808')):
            state = 'S_priority_' + label
            guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + origin + '_l, (' + value + '))]',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + '_l) = ($ptascii("0"))',
                       '$compiled_order_number(' + value + ') = eps',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
        guards += ['S_priority_signedzero = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + origin + '_l, (PFLOAT 9223372036854775808))]',
                   '$compiled_special_concat_bytes(S_priority_signedzero, ' + origin + '_l) = ($ptascii("0"))',
                   '$scalar_plain_order(S_priority_signedzero, PFLOAT 9223372036854775808, PNULL) = 0',
                   '$compiled_special_concat_bytes(S_priority_signedzero, ' + origin + ') = ($ptascii("1"))']
    return checks + guards, derived + len(guards)


def compiler_conditions(checked, paths):
    checks = []
    for index, name in enumerate(CONTROLS):
        state, origin = 'S_priority_control_' + str(index), 'porigin_priority_control_' + str(index)
        binary = origin + '_binary'
        checks += [state + ' = $php_run(' + checked[name]['fixture'] + ', 0, ' + json.dumps(base64.b64encode(bytes(paths[name])).decode()) + ')',
                   state + '.COMPLETION = BUDGET',
                   '$special_review_concat_path(' + state + '.SOURCES[0].OCCURRENCES) = (pcpath_priority_control_' + str(index) + ')',
                   origin + ' = PORIGIN 0 pcpath_priority_control_' + str(index),
                   '$origin_child((' + origin + '), [PCFIELD 0, PCFIELD 0]) = (' + binary + ')']
        if name not in ROWS:
            if name == 'no-priority':
                data = raw(b'1.0000000000000001x')
                checks += ['$compiled_read(' + state + ', ' + binary + ') = (PBOOL false)',
                           '$compiled_special_concat_bytes(' + state + ', ' + binary + ') = ($ptascii(""))',
                           state + '_live = ' + state + '[.PRECISIONINI = $ptascii("17")][.PRECISIONMODIFIED = true]',
                           state + '_wrong = ' + state + '_live[.POOLS = $special_review_pools(' + state + '_live.POOLS, ' + binary + ', (PBOOL true))]',
                           '$compiled_precision(' + state + '_wrong, (' + binary + ')) = (14)',
                           '$scalar_plain_order(' + state + '_wrong, PFLOAT 4607182418800017409, PSTRING ' + data + ') = 1',
                           '$number_string_precision_order(NFLOAT 4607182418800017409, ' + data + ', 14) = $(-1)',
                           '$compiled_special_concat_bytes(' + state + '_wrong, ' + binary + ') = eps']
            elif name in ('nan-bool', 'bool-nan'):
                checks += ['$compiled_read(' + state + ', ' + binary + ') = (PBOOL true)',
                           '$compiled_special_concat_bytes(' + state + ', ' + binary + ') = ($ptascii("1"))',
                           '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = ($ptascii("1x"))',
                           '$compiled_string_value(' + state + ', ' + origin + ', PSTRING ($ptascii("1x"))) = PSTRING_CARRIER INTERNED_STRING ($ptascii("1x"))']
            else:
                checks += ['$compiled_special_concat_bytes(' + state + ', ' + binary + ') = eps',
                           '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
            continue
        operation, left, right, order = ROWS[name]
        answer = strings.result(operation, order)
        rendered, value = numeric.text(answer), numeric.value(answer)
        checks += ['$compiled_read(' + state + ', ' + binary + ') = (' + value + ')',
                   '$compiled_precision(' + state + ', (' + binary + ')) = (14)',
                   '$compiled_special_concat_bytes(' + state + ', ' + binary + ') = ($ptascii(' + json.dumps(rendered) + '))',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = ($ptascii(' + json.dumps(rendered + 'x') + '))',
                   '$compiled_string_value(' + state + ', ' + origin + ', PSTRING ($ptascii(' + json.dumps(rendered + 'x') + '))) = PSTRING_CARRIER INTERNED_STRING ($ptascii(' + json.dumps(rendered + 'x') + '))']
        for field, label in enumerate((left, right)):
            child, child_value, data = binary + '_' + str(field), VALUES[label][1], VALUES[label][2]
            checks += ['$origin_child((' + binary + '), [PCFIELD ' + str(field) + ']) = (' + child + ')',
                       '$compiled_read(' + state + ', ' + child + ') = (' + child_value + ')',
                       '$compiled_precision(' + state + ', (' + child + ')) = (14)',
                       '$compiled_special_concat_bytes(' + state + ', ' + child + ') ' + ('= (' + raw(data) + ')' if data is not None else '=/= eps')]
    return checks


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    watched = [Path(module.__file__) for module in (source, source.prior, source.strings, source.arithmetic, source.unary, numeric, strings, runner)] + [Path(__file__)]
    before = {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.cases, runner.conditions = cases, conditions
    runner.compiler_conditions, runner.CONTROLS = compiler_conditions, CONTROLS
    passed = runner.main(expected_outputs=cases.OUTPUTS)
    assert before == {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = 'Four authentic-source-seeded BOOL/NULL-priority fixtures add own-result/type with equal-rendering wrong types, missing child reads, actual source and three precision controls, same-order changed raw string payloads, carriers and quiet numeric range/nonNaN/valid64 boundaries. A signed-zero numeric replacement remains admitted without requiring numeric value/literal-byte equality. Independent fixed-order tables cover all seven operators in both orientations, NULL/nonempty-string exceptions versus Boolean truth, empty/string0/NUL/high bytes, numbers, infinities, subnormal truth and already-certified nested Boolean results. A forged live17 non-priority result on a compile14 mixed comparison refuses, isolating the priority gate that prevents live-formatting leakage. Former direct NaN ConstFetch/Boolean selectors check their separate VALUE comparison admission; arrays, objects, variables and unary FLOAT NOT stay outside. A certified Boolean result of a NaN comparison remains distinct from a NaN operand. Exact author prefixes/native4-once remain, affected controls retain separate cuts and fixture/compiler conditions carry source0, without old full/source/native/author replay or ownership expansion.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
