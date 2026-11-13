#!/usr/bin/env python3
"""Independent mixed order, captured precision and exact string payload checks."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_number_string_comparison_special_concat_leading_key_cases as cases
import string_offset_request_base_number_string_comparison_special_concat_leading_key_protocol as source
import string_offset_request_base_numeric_comparison_special_concat_leading_key_review_state as numeric
import string_offset_request_base_string_comparison_special_concat_leading_key_review_state as strings

runner, raw = numeric.runner, source.strings.bytes_term
ROWS = {operation.lower() + '-' + str(pair) + '-' + str(reverse):
        (operation, number, data, reverse, -order if reverse else order)
        for operation in numeric.OPERATORS for pair, (number, data, order) in enumerate(
            (('i0', b'00', 0), ('i2', b'1', 1), ('i2', b'2tail', -1)))
        for reverse in (False, True)}
for name, number, data, order in (
        ('max-overflow', 'imax', b'9223372036854775808', 0),
        ('min-overflow', 'imin', b'-9223372036854775809', 0),
        ('round53', 'i53next', b'9007199254740992.0', 0),
        ('numeric-whitespace', 'i2', b' +02 ', 0),
        ('signed-zero', 'fn0', b'-0', 0), ('empty-zero', 'i0', b'', 1),
        ('nul-zero', 'i0', b'\0', 1), ('nul-leading', 'i2', b'2\0tail', -1),
        ('high-byte', 'i1', b'\xff', -1),
        ('infinite-numeric', 'finf', b'2e309', 0),
        ('infinite-text', 'finf', b'INF', 0),
        ('negative-infinite', 'fninf', b'-2e309', 0),
        ('negative-infinite-text', 'fninf', b'-INF', 0),
        ('adjacent-full', 'fnext', b'1.0000000000000001', 1),
        ('adjacent-reverse', 'f1', b'1.0000000000000002', -1)):
    ROWS[name] = 'SPACESHIP', number, data, False, order
ROWS['precision-number'] = 'GREATER', 'fnext', b'1.0000000000000001x', False, -1
ROWS['precision-string'] = 'GREATER', 'fnext', b'1.0000000000000001x', True, 1
CONTROLS = {}
for name, (operation, number, data, reverse, order) in ROWS.items():
    operands = (strings.literal(data), numeric.NUMBERS[number][0]) if reverse else (numeric.NUMBERS[number][0], strings.literal(data))
    CONTROLS[name] = ("<?php $x = ((" + operands[0] + ' ' + numeric.OPERATORS[operation] + ' ' + operands[1] + ") . null) . 'x';\n").encode()
CONTROLS |= {
    'nan-number': b"<?php $x = ((NAN < '2') . null) . 'x';\n",
    'nan-string': b"<?php $x = (('2' > NAN) . null) . 'x';\n",
    'arithmetic-nan': b"<?php $x = (((1e309-1e309) < '2') . null) . 'x';\n",
    'boolean': b"<?php $x = ((true > '1') . null) . 'x';\n",
    'null': b"<?php $x = ((null < '1') . null) . 'x';\n",
    'array': b"<?php $x = (([] < '1') . null) . 'x';\n",
    'not-float': b"<?php $x = ((!1.5) . null) . 'x';\n",
    'variable': b"<?php $x = (($missing < '1') . null) . 'x';\n"}
DATA = (b'9223372036854775808', b'2tail', b'1.0000000000000001x', b'2tail')
CHANGED = (b'9223372036854775809', b'3tail', b'1.0000000000000003x', b'3tail')
NUMBERS = ('NINT 9223372036854775807', 'NINT 10', 'NFLOAT 4607182418800017409', 'NINT 10')


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    tag = ('mixed_root', 'mixed_root', 'mixed_root_l', 'mixed_root_child_l')[index]
    origin, expression = 'porigin_' + tag, 'expression_' + tag
    guards = [origin + ' = PORIGIN n_mixed pcpath_mixed', origin + '_l = PORIGIN n_mixed pcpath_mixed_l',
              origin + '_r = PORIGIN n_mixed pcpath_mixed_r']
    wrong, wrong_type = (('PBOOL false', 'PINT 1'), ('PINT 0', 'PBOOL true'),
                         ('PBOOL true', 'PINT 0'), ('PBOOL false', 'PINT 1'))[index]
    for label, replacement in (('drop', 'eps'), ('wrong', '(' + wrong + ')'), ('type', '(' + wrong_type + ')')):
        state = 'S_mixed_' + label
        guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + origin + ', ' + replacement + ')]',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps',
                   '$string_read_request_base_saved(' + state + ', pstringread) = eps']
    for field, suffix in enumerate(('_l', '_r')):
        child = origin + suffix
        state = 'S_mixed_drop' + suffix
        guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + child + ', eps)]',
                   '$compiled_read(' + state + ', ' + child + ') = eps',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
        state = 'S_mixed_precision' + suffix
        guards += [state + ' = S_after[.POOLS = $float_review_precision(S_after.POOLS, ' + child + ', 17)]',
                   '$compiled_precision(' + state + ', (' + origin + ')) = (14)',
                   '$compiled_precision(' + state + ', (' + child + ')) = (17)',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
        if field == 0:
            guards += ['expression_mixed_other = NExprVariable (BYTES "dW5hdXRo") metadata_' + tag]
        left, right = ('expression_mixed_other', expression + '_r') if field == 0 else (expression + '_l', 'expression_mixed_other')
        state = 'S_mixed_source' + suffix
        guards += [state + ' = S_after[.SOURCES = [{ID n_mixed, AST (PROGRAM eps), OCCURRENCES ([(PCOCCURRENCE pcpath_mixed ' + expression + '), (PCOCCURRENCE pcpath_mixed_l ' + left + '), (PCOCCURRENCE pcpath_mixed_r ' + right + ')])}]]',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
    guards += ['S_mixed_root_source = S_after[.SOURCES = [{ID n_mixed, AST (PROGRAM eps), OCCURRENCES ([(PCOCCURRENCE pcpath_mixed expression_mixed_other), (PCOCCURRENCE pcpath_mixed_l ' + expression + '_l), (PCOCCURRENCE pcpath_mixed_r ' + expression + '_r)])}]]',
               '$compiled_special_concat_bytes(S_mixed_root_source, ' + origin + ') = eps',
               'S_mixed_precision = S_after[.POOLS = $float_review_precision(S_after.POOLS, ' + origin + ', 17)]',
               '$compiled_precision(S_mixed_precision, (' + origin + ')) = (17)',
               '$compiled_precision(S_mixed_precision, (' + origin + '_l)) = (14)',
               '$compiled_precision(S_mixed_precision, (' + origin + '_r)) = (14)',
               '$compiled_special_concat_bytes(S_mixed_precision, ' + origin + ') = eps']
    number, string = (origin + '_r', origin + '_l') if index == 3 else (origin + '_l', origin + '_r')
    for label, value in (('bytes', 'PSTRING ' + raw(CHANGED[index])),
                         ('carrier', 'PSTRING_CARRIER INTERNED_STRING ' + raw(DATA[index]))):
        state = 'S_mixed_string_' + label
        guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + string + ', (' + value + '))]',
                   '$compiled_read(' + state + ', ' + string + ') = (' + value + ')',
                   '$compiled_special_concat_bytes(' + state + ', ' + string + ') = (' + raw(DATA[index]) + ')',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
    guards += ['$number_string_precision_order(' + NUMBERS[index] + ', ' + raw(CHANGED[index]) + ', 14) = ' + ('0' if index == 0 else '$(-1)')]
    for label, value in (('bool', 'PBOOL true'), ('null', 'PNULL'), ('array', 'PARRAY 0'),
                         ('range', 'PINT 9223372036854775808'), ('nan', 'PFLOAT 9221120237041090560'),
                         ('bits', 'PFLOAT 18446744073709551616')):
        state = 'S_mixed_number_' + label
        guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + number + ', (' + value + '))]',
                   '$compiled_read(' + state + ', ' + number + ') = (' + value + ')',
                   '$compiled_order_number(' + value + ') = eps']
        if (label == 'bool' and index != 1) or (label == 'null' and index != 0):
            guards += ['$compiled_special_concat_bytes(' + state + ', ' + origin + ') = ($ptascii(' + json.dumps(('1', '-1', '', '1')[index]) + '))']
        else:
            guards += ['$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
    replacement = ('PINT 0', 'PINT 30', 'PFLOAT 4609434218613702656', 'PINT 40')[index]
    guards += ['S_mixed_number_value = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + number + ', (' + replacement + '))]',
               '$compiled_order_number(' + replacement + ') =/= eps',
               '$compiled_special_concat_bytes(S_mixed_number_value, ' + origin + ') = eps',
               'S_mixed_live = S_after[.PRECISIONINI = $ptascii("9")][.PRECISIONMODIFIED = true]',
               '$precision_value(S_mixed_live) = 9',
               '$compiled_special_concat_bytes(S_mixed_live, porigin_key) = ($ptascii("' + ('1x', '-1x', '0x', '-4x')[index] + '"))']
    if index == 2:
        guards += ['S_mixed_all17 = S_mixed_precision[.POOLS = $float_review_precision($float_review_precision(S_mixed_precision.POOLS, ' + number + ', 17), ' + string + ', 17)]',
                   '$compiled_precision(S_mixed_all17, (' + number + ')) = (17)',
                   '$compiled_precision(S_mixed_all17, (' + string + ')) = (17)',
                   '$compiled_read(S_mixed_all17, ' + origin + ') = (PBOOL false)',
                   '$compiled_special_concat_bytes(S_mixed_all17, ' + number + ') = ($ptascii("1.0000000000000002"))',
                   '$compiled_special_concat_bytes(S_mixed_all17, ' + origin + ') = eps']
    return checks + guards, derived + len(guards)


def compiler_conditions(checked, paths):
    checks = []
    for index, name in enumerate(CONTROLS):
        state, origin = 'S_mixed_control_' + str(index), 'porigin_mixed_control_' + str(index)
        binary = origin + '_binary'
        checks += [state + ' = $php_run(' + checked[name]['fixture'] + ', 0, ' + json.dumps(base64.b64encode(bytes(paths[name])).decode()) + ')',
                   state + '.COMPLETION = BUDGET',
                   '$special_review_concat_path(' + state + '.SOURCES[0].OCCURRENCES) = (pcpath_mixed_control_' + str(index) + ')',
                   origin + ' = PORIGIN 0 pcpath_mixed_control_' + str(index),
                   '$origin_child((' + origin + '), [PCFIELD 0, PCFIELD 0]) = (' + binary + ')']
        if name not in ROWS:
            if name in ('boolean', 'null', 'nan-number', 'nan-string'):
                answer = name == 'null'
                text, value = numeric.text(answer), numeric.value(answer)
                checks += ['$compiled_read(' + state + ', ' + binary + ') = (' + value + ')',
                           '$compiled_special_concat_bytes(' + state + ', ' + binary + ') = ($ptascii(' + json.dumps(text) + '))',
                           '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = ($ptascii(' + json.dumps(text + 'x') + '))',
                           '$compiled_string_value(' + state + ', ' + origin + ', PSTRING ($ptascii(' + json.dumps(text + 'x') + '))) = PSTRING_CARRIER INTERNED_STRING ($ptascii(' + json.dumps(text + 'x') + '))']
            else:
                checks += ['$compiled_special_concat_bytes(' + state + ', ' + binary + ') = eps',
                           '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
            continue
        operation, number, data, reverse, order = ROWS[name]
        answer = strings.result(operation, order)
        rendered, value = numeric.text(answer), numeric.value(answer)
        checks += ['$compiled_read(' + state + ', ' + binary + ') = (' + value + ')',
                   '$compiled_precision(' + state + ', (' + binary + ')) = (14)',
                   '$compiled_special_concat_bytes(' + state + ', ' + binary + ') = ($ptascii(' + json.dumps(rendered) + '))',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = ($ptascii(' + json.dumps(rendered + 'x') + '))',
                   '$compiled_string_value(' + state + ', ' + origin + ', PSTRING ($ptascii(' + json.dumps(rendered + 'x') + '))) = PSTRING_CARRIER INTERNED_STRING ($ptascii(' + json.dumps(rendered + 'x') + '))']
        for field in (0, 1):
            child, is_string = binary + '_' + str(field), reverse == (field == 0)
            child_value = 'PSTRING ' + raw(data) if is_string else numeric.NUMBERS[number][1]
            checks += ['$origin_child((' + binary + '), [PCFIELD ' + str(field) + ']) = (' + child + ')',
                       '$compiled_read(' + state + ', ' + child + ') = (' + child_value + ')',
                       '$compiled_precision(' + state + ', (' + child + ')) = (14)',
                       '$compiled_special_concat_bytes(' + state + ', ' + child + ') ' + ('= (' + raw(data) + ')' if is_string else '=/= eps')]
            if not is_string:
                checks += ['$compiled_order_number(' + child_value + ') = (' + numeric.NUMBERS[number][2] + ')']
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
    report['scope'] = 'Four authentic-source-seeded mixed ordered-number/raw-PSTRING fixtures add typed own-result, missing reads, exact string payload versus same-order changed bytes/carriers, numeric type/range/nonNaN/valid64, outcome-changing numeric values, actual source and three precision controls. Compiled numeric values need not equal literal byte text; no result-insensitive numeric-value refusal is claimed. A coherent compile17 mutation flips the precision-sensitive comparison while changing only live precision leaves the compile14 key intact. Independent fixed-order compiler tables distinguish all seven operators and both orientations, FULLNUM versus leading text, integer overflow conversion versus both-string provenance, rounding above2**53, adjacent binary64, signed zeros, infinities and binary bytes. Arrays, variables and unary FLOAT NOT remain outside this mixed slice. Former genuine NaN ConstFetch/string selectors now check their separate VALUE comparison admission; arithmetic NaN and malformed pool provenance remain refused. Later BOOL/NULL compiler selectors and six same-result pool contexts check their separate priority comparison admission; the two outcome-changing BOOL/NULL pools still refuse. Exact author recipe prefixes/native4-once are retained, all fixture/compiler conditions carry source0, and affected old controls retain separate cuts without old full/source/native/author replay or a cross-campaign unique sum.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
