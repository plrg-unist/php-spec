#!/usr/bin/env python3
"""Independent lexical/numeric string order and exact byte/read provenance."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_string_comparison_special_concat_leading_key_cases as cases
import string_offset_request_base_string_comparison_special_concat_leading_key_protocol as source
import string_offset_request_base_numeric_comparison_special_concat_leading_key_review_state as numeric

runner = numeric.runner
raw = source.strings.bytes_term
PAIRS = {
    'lex-less': (b'a', b'z', -1), 'lex-equal': (b'key', b'key', 0), 'lex-greater': (b'z', b'a', 1),
    'numeric-equal': (b'02', b'2', 0), 'leading-text': (b'2tail', b'10tail', 1)}
ROWS = {operation.lower() + '-' + pair: (operation, left, right, order)
        for operation in numeric.OPERATORS for pair, (left, right, order) in PAIRS.items()}
for name, left, right, order in (
        ('numeric-order', b'2', b'10', -1), ('numeric-reverse', b'10', b'2', 1),
        ('signed-zero', b'-0', b'+0.0', 0), ('numeric-whitespace', b' 2 ', b'2', 0),
        ('round53', b'9007199254740993', b'9007199254740992.0', 0),
        ('max-overflow', b'9223372036854775807', b'9223372036854775808', -1),
        ('min-overflow', b'-9223372036854775808', b'-9223372036854775809', 1),
        ('same-rounded', b'9223372036854775808', b'9223372036854775809', -1),
        ('negative-rounded', b'-9223372036854775810', b'-9223372036854775809', 1),
        ('infinite-fallback', b'1e309', b'2e309', -1),
        ('negative-infinite', b'-1e309', b'-2e309', -1),
        ('prefix20-decimal', b'18446744073709551616.0', b'18446744073709551616.00', -1),
        ('empty-zero', b'', b'0', -1), ('nul-prefix', b'\0a', b'\0b', -1),
        ('nul-numeric', b'2\0a', b'10\0a', 1), ('high-byte', b'\xff', b'\x01', 1)):
    ROWS[name] = 'SPACESHIP', left, right, order


def literal(data):
    return '"' + ''.join('\\x' + format(value, '02x') for value in data) + '"'


CONTROLS = {name: ("<?php $x = ((" + literal(left) + ' ' + numeric.OPERATORS[operation] + ' ' + literal(right) + ") . null) . 'x';\n").encode()
            for name, (operation, left, right, order) in ROWS.items()} | {
    'mixed-int': b"<?php $x = (('02' == 2) . null) . 'x';\n",
    'mixed-float': b"<?php $x = (('2' == 2.0) . null) . 'x';\n",
    'mixed-bool': b"<?php $x = (('0' == false) . null) . 'x';\n",
    'mixed-null': b"<?php $x = (('' == null) . null) . 'x';\n",
    'owning-array': b"<?php $x = (('a' < []) . null) . 'x';\n"}
DATA = ((b'9223372036854775808', b'9223372036854775809'), (b'a', b'z'),
        (b'02', b'2'), (b'2tail', b'10tail'))
SAME_RESULT = ((b'0', b'9223372036854775810'), (b'b', b'y'), (b'2', b'02'), (b'3tail', b'0tail'))


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    tag = ('string_root', 'string_root', 'string_root_l', 'string_root_child_l')[index]
    origin, expression = 'porigin_' + tag, 'expression_' + tag
    guards = [origin + ' = PORIGIN n_string pcpath_string',
              origin + '_l = PORIGIN n_string pcpath_string_l',
              origin + '_r = PORIGIN n_string pcpath_string_r']
    wrong, wrong_type = (('PBOOL false', 'PINT 1'), ('PINT 0', 'PBOOL false'),
                         ('PBOOL true', 'PINT 0'), ('PBOOL false', 'PINT 1'))[index]
    for label, replacement in (('drop', 'eps'), ('wrong', '(' + wrong + ')'), ('type', '(' + wrong_type + ')')):
        state = 'S_string_' + label
        guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + origin + ', ' + replacement + ')]',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps',
                   '$string_read_request_base_saved(' + state + ', pstringread) = eps']
    for field, suffix in enumerate(('_l', '_r')):
        child, value, changed_value = origin + suffix, raw(DATA[index][field]), raw(SAME_RESULT[index][field])
        state = 'S_string_drop' + suffix
        guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + child + ', eps)]',
                   '$compiled_read(' + state + ', ' + child + ') = eps',
                   '$compiled_special_concat_bytes(' + state + ', ' + child + ') = (' + value + ')',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
        state = 'S_string_bytes' + suffix
        left, right = (changed_value, raw(DATA[index][1])) if field == 0 else (raw(DATA[index][0]), changed_value)
        order = ('$(-1)', '$(-1)', '0', '1')[index]
        guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + child + ', (PSTRING ' + changed_value + '))]',
                   '$compiled_read(' + state + ', ' + child + ') = (PSTRING ' + changed_value + ')',
                   '$compiled_special_concat_bytes(' + state + ', ' + child + ') = (' + value + ')',
                   '$string_order(' + left + ', ' + right + ') = ' + order,
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
        state = 'S_string_carrier' + suffix
        guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + child + ', (PSTRING_CARRIER INTERNED_STRING ' + value + '))]',
                   '$compiled_read(' + state + ', ' + child + ') = (PSTRING_CARRIER INTERNED_STRING ' + value + ')',
                   '$string_plain(PSTRING_CARRIER INTERNED_STRING ' + value + ') = PSTRING ' + value,
                   '$compiled_special_concat_bytes(' + state + ', ' + child + ') = (' + value + ')',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
        state = 'S_string_precision' + suffix
        guards += [state + ' = S_after[.POOLS = $float_review_precision(S_after.POOLS, ' + child + ', 17)]',
                   '$compiled_precision(' + state + ', (' + origin + ')) = (14)',
                   '$compiled_precision(' + state + ', (' + child + ')) = (17)',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
        other = 'expression_string_other'
        if field == 0:
            guards += [other + ' = NExprVariable (BYTES "dW5hdXRo") metadata_' + tag]
        left_source, right_source = (other, expression + '_r') if field == 0 else (expression + '_l', other)
        state = 'S_string_source' + suffix
        guards += [state + ' = S_after[.SOURCES = [{ID n_string, AST (PROGRAM eps), OCCURRENCES ([(PCOCCURRENCE pcpath_string ' + expression + '), (PCOCCURRENCE pcpath_string_l ' + left_source + '), (PCOCCURRENCE pcpath_string_r ' + right_source + ')])}]]',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
    guards += ['S_string_precision = S_after[.POOLS = $float_review_precision(S_after.POOLS, ' + origin + ', 17)]',
               '$compiled_precision(S_string_precision, (' + origin + ')) = (17)',
               '$compiled_precision(S_string_precision, (' + origin + '_l)) = (14)',
               '$compiled_precision(S_string_precision, (' + origin + '_r)) = (14)',
               '$compiled_special_concat_bytes(S_string_precision, ' + origin + ') = eps']
    if index == 2:
        guards += ['S_string_integer = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + origin + '_l, (PINT 2))]',
                   '$compiled_special_concat_bytes(S_string_integer, ' + origin + '_l) = ($ptascii("02"))',
                   '$binary_apply(S_string_integer, NOTEQUAL, PINT 2, PSTRING ($ptascii("2")), 0) = S_string_integer[.RESULT = KNOWN (PBOOL false)]',
                   '$compiled_special_concat_bytes(S_string_integer, ' + origin + ') = ($ptascii(""))']
    guards += numeric.prior.unary_guards([], ('1x', '-1x', '0x', '-4x')[index])
    return checks + guards, derived + len(guards)


def result(operation, order):
    return {'LESS': order < 0, 'LESSEQUAL': order <= 0, 'GREATER': order > 0,
            'GREATEREQUAL': order >= 0, 'EQUAL': order == 0, 'NOTEQUAL': order != 0,
            'SPACESHIP': order}[operation]


def compiler_conditions(checked, paths):
    checks = []
    for index, name in enumerate(CONTROLS):
        state, origin = 'S_string_control_' + str(index), 'porigin_string_control_' + str(index)
        binary = origin + '_binary'
        checks += [state + ' = $php_run(' + checked[name]['fixture'] + ', 0, ' + json.dumps(base64.b64encode(bytes(paths[name])).decode()) + ')',
                   state + '.COMPLETION = BUDGET',
                   '$special_review_concat_path(' + state + '.SOURCES[0].OCCURRENCES) = (pcpath_string_control_' + str(index) + ')',
                   origin + ' = PORIGIN 0 pcpath_string_control_' + str(index),
                   '$origin_child((' + origin + '), [PCFIELD 0, PCFIELD 0]) = (' + binary + ')']
        if name not in ROWS:
            if name in ('mixed-int', 'mixed-float', 'mixed-bool', 'mixed-null'):
                checks += ['$compiled_read(' + state + ', ' + binary + ') = (PBOOL true)',
                           '$compiled_special_concat_bytes(' + state + ', ' + binary + ') = ($ptascii("1"))',
                           '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = ($ptascii("1x"))',
                           '$compiled_string_value(' + state + ', ' + origin + ', PSTRING ($ptascii("1x"))) = PSTRING_CARRIER INTERNED_STRING ($ptascii("1x"))']
            else:
                checks += ['$compiled_special_concat_bytes(' + state + ', ' + binary + ') = eps',
                           '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
            continue
        operation, left, right, order = ROWS[name]
        answer = result(operation, order)
        rendered = numeric.text(answer)
        signed = str(order) if order >= 0 else '$(' + str(order) + ')'
        checks += ['$string_order(' + raw(left) + ', ' + raw(right) + ') = ' + signed,
                   '$compiled_read(' + state + ', ' + binary + ') = (' + numeric.value(answer) + ')',
                   '$compiled_precision(' + state + ', (' + binary + ')) = (14)',
                   '$compiled_special_concat_bytes(' + state + ', ' + binary + ') = ($ptascii(' + json.dumps(rendered) + '))',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = ($ptascii(' + json.dumps(rendered + 'x') + '))',
                   '$compiled_string_value(' + state + ', ' + origin + ', PSTRING ($ptascii(' + json.dumps(rendered + 'x') + '))) = PSTRING_CARRIER INTERNED_STRING ($ptascii(' + json.dumps(rendered + 'x') + '))']
        for field, data in enumerate((left, right)):
            child = binary + '_' + str(field)
            checks += ['$origin_child((' + binary + '), [PCFIELD ' + str(field) + ']) = (' + child + ')',
                       '$compiled_read(' + state + ', ' + child + ') = (PSTRING ' + raw(data) + ')',
                       '$compiled_precision(' + state + ', (' + child + ')) = (14)',
                       '$compiled_special_concat_bytes(' + state + ', ' + child + ') = (' + raw(data) + ')']
    return checks


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    watched = [Path(module.__file__) for module in (source, source.prior, source.strings, source.arithmetic, source.unary, numeric, numeric.prior, runner)] + [Path(__file__)]
    before = {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.cases, runner.conditions = cases, conditions
    runner.compiler_conditions, runner.CONTROLS = compiler_conditions, CONTROLS
    passed = runner.main(expected_outputs=cases.OUTPUTS)
    assert before == {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = 'Four authentic-source-seeded raw-string fixtures add own-result/type, missing reads, same-order changed-string read/BYTE mismatches, per-side runtime carriers, actual source and three precision refusals. The quiet same-result mixed INT/STRING context now checks the separately reviewed number/string admission. Independent fixed-order compiler tables cover all seven operators, numeric equality versus lexical order, normalized spaceship, signs/whitespace, binary NUL/high bytes, above2**53 rounding, integer-overflow provenance on both signs and same-sign infinities. Twenty-digit integer-prefix overflow with decimal suffix retains lexical fallback. The two mixed INT/FLOAT compiler selectors now check ordered-number/raw-string admission; Boolean/null controls now check their separately reviewed priority comparison admission; arrays remain refused. Author recipes are exact prefixes; existing52 order body is reused, accepted00 overflow shortcut is only in the new post/prepared cut, and earlier native4/pre502 old00 identities remain. Owner, saved throw, fixed bounds and budgets retain their laws. The original raw-string cut required no older promotions; these later mixed promotions retain separate cuts without old full replay or cross-campaign unique sum; fixture/compiler conditions carry source0, with no raw-carrier ownership or general coercion claim.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
