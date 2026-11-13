#!/usr/bin/env python3
"""Independent binary64 order, integer rounding and typed comparison checks."""
import base64
import hashlib
import json
from pathlib import Path
import struct
import sys

import string_offset_request_base_numeric_comparison_special_concat_leading_key_cases as cases
import string_offset_request_base_numeric_comparison_special_concat_leading_key_protocol as source
import string_offset_request_base_bool_null_unary_special_concat_leading_key_review_state as prior

runner = prior.runner
MINIMUM, MAXIMUM = -9223372036854775808, 9223372036854775807
OPERATORS = {'LESS': '<', 'LESSEQUAL': '<=', 'GREATER': '>', 'GREATEREQUAL': '>=',
             'EQUAL': '==', 'NOTEQUAL': '!=', 'SPACESHIP': '<=>'}


def integer(value):
    code = str(value) if value >= 0 else '$(' + str(value) + ')'
    php = '((0 - 9223372036854775807) - 1)' if value == MINIMUM else str(value)
    return php, 'PINT ' + code, 'NINT ' + code, value, False


def floating(php):
    value = float(php)
    bits = struct.unpack('>Q', struct.pack('>d', value))[0]
    return php, 'PFLOAT ' + str(bits), 'NFLOAT ' + str(bits), value, True


NUMBERS = {name: integer(value) for name, value in {
    'i0': 0, 'i1': 1, 'i2': 2, 'imax': MAXIMUM, 'imin': MINIMUM,
    'i53next': 9007199254740993}.items()} | {name: floating(php) for name, php in {
    'f0': '0.0', 'fn0': '-0.0', 'f1': '1.0', 'f15': '1.5', 'f2': '2.0',
    'f25': '2.5', 'fnext': '1.0000000000000002', 'finf': '1e309', 'fninf': '-1e309',
    'f63': '9223372036854775808.0', 'f53': '9007199254740992.0'}.items()}
ROWS = {operation.lower() + '-' + left: (operation, left, 'i2')
        for operation in OPERATORS for left in ('f15', 'f2', 'f25')} | {
    operation.lower() + '-right-float': (operation, 'i2', 'f15') for operation in OPERATORS}
for name, operation, left, right in (
        ('zero-equal', 'EQUAL', 'fn0', 'f0'), ('zero-space', 'SPACESHIP', 'fn0', 'f0'),
        ('zero-less', 'LESS', 'fn0', 'i0'), ('zero-ge', 'GREATEREQUAL', 'i0', 'fn0'),
        ('max-equal', 'EQUAL', 'imax', 'f63'), ('max-space', 'SPACESHIP', 'imax', 'f63'),
        ('max-less', 'LESS', 'imax', 'f63'), ('max-greater', 'GREATER', 'imax', 'f63'),
        ('max-reverse', 'SPACESHIP', 'f63', 'imax'), ('min-equal', 'EQUAL', 'imin', 'fninf'),
        ('round53-equal', 'EQUAL', 'i53next', 'f53'), ('round53-space', 'SPACESHIP', 'i53next', 'f53'),
        ('round53-greater', 'GREATER', 'i53next', 'f53'),
        ('adjacent-equal', 'EQUAL', 'fnext', 'f1'), ('adjacent-ne', 'NOTEQUAL', 'fnext', 'f1'),
        ('adjacent-space', 'SPACESHIP', 'fnext', 'f1'), ('adjacent-greater', 'GREATER', 'fnext', 'f1'),
        ('adjacent-less', 'LESS', 'f1', 'fnext'), ('adjacent-le', 'LESSEQUAL', 'f1', 'fnext'),
        ('inf-greater', 'GREATER', 'finf', 'i2'), ('inf-ge', 'GREATEREQUAL', 'finf', 'i2'),
        ('inf-space', 'SPACESHIP', 'finf', 'i2'), ('inf-reverse', 'LESS', 'i2', 'finf'),
        ('ninf-less', 'LESS', 'fninf', 'i0'), ('infinities-space', 'SPACESHIP', 'fninf', 'finf'),
        ('inf-equal', 'EQUAL', 'finf', 'finf'), ('inf-same-space', 'SPACESHIP', 'finf', 'finf'),
        ('inf-same-ge', 'GREATEREQUAL', 'finf', 'finf')):
    ROWS[name] = operation, left, right
CONTROLS = {name: ("<?php $x = ((" + NUMBERS[left][0] + ' ' + OPERATORS[operation] + ' ' + NUMBERS[right][0] + ") . null) . 'x';\n").encode()
            for name, (operation, left, right) in ROWS.items()} | {
    'string-left': b"<?php $x = (('1.5' < 2.5) . null) . 'x';\n",
    'string-right': b"<?php $x = ((1.5 < '2.5') . null) . 'x';\n",
    'boolean-left': b"<?php $x = ((true < 1.5) . null) . 'x';\n",
    'null-left': b"<?php $x = ((null < 1.5) . null) . 'x';\n",
    'array-left': b"<?php $x = (([] < 1.5) . null) . 'x';\n",
    'nan-left': b"<?php $x = ((NAN < 1.5) . null) . 'x';\n",
    'nan-arithmetic': b"<?php $x = (((1e309 - 1e309) < 1.5) . null) . 'x';\n",
    'outside-op': b"<?php $x = ((0.0 xor 1) . null) . 'x';\n"}


def outcome(operation, left, right):
    # PHP converts the integer operand to binary64 in mixed numeric pairs.
    a, b = (float(left[3]), float(right[3])) if left[4] or right[4] else (left[3], right[3])
    order = (a > b) - (a < b)
    return {'LESS': order < 0, 'LESSEQUAL': order <= 0, 'GREATER': order > 0,
            'GREATEREQUAL': order >= 0, 'EQUAL': order == 0,
            'NOTEQUAL': order != 0, 'SPACESHIP': order}[operation]


def value(result):
    return 'PBOOL ' + str(result).lower() if isinstance(result, bool) else 'PINT ' + (str(result) if result >= 0 else '$(' + str(result) + ')')


def text(result):
    return ('1' if result else '') if isinstance(result, bool) else str(result)


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    tag = ('numeric_root', 'numeric_root', 'numeric_root_l', 'numeric_root_child_l')[index]
    origin, expression = 'porigin_' + tag, 'expression_' + tag
    guards = [origin + ' = PORIGIN n_numeric pcpath_numeric',
              origin + '_l = PORIGIN n_numeric pcpath_numeric_l',
              origin + '_r = PORIGIN n_numeric pcpath_numeric_r']
    wrong, wrong_type = (('PBOOL false', 'PINT 1'), ('PINT 0', 'PFLOAT 13830554455654793216'),
                         ('PBOOL true', 'PINT 0'), ('PBOOL false', 'PINT 1'))[index]
    for suffix, replacement in (('drop', 'eps'), ('wrong', '(' + wrong + ')'), ('type', '(' + wrong_type + ')')):
        state = 'S_numeric_' + suffix
        guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + origin + ', ' + replacement + ')]',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps',
                   '$string_read_request_base_saved(' + state + ', pstringread) = eps']
    mutants = (('PFLOAT 4613937818241073152', 'PINT 1'),
               ('PFLOAT 4613937818241073152', 'PFLOAT 4609434218613702656'),
               ('PFLOAT 4612811918334230528', 'PFLOAT 4612811918334230528'),
               ('PFLOAT 4602678819172646912', 'PINT 2'))[index]
    for suffix, replacement in zip(('_l', '_r'), mutants):
        child = origin + suffix
        for operation, changed_value in (('drop', 'eps'), ('wrong', '(' + replacement + ')')):
            state = 'S_numeric_child' + suffix + '_' + operation
            guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + child + ', ' + changed_value + ')]',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps',
                       '$string_read_request_base_saved(' + state + ', pstringread) = eps']
        state = 'S_numeric_precision' + suffix
        guards += [state + ' = S_after[.POOLS = $float_review_precision(S_after.POOLS, ' + child + ', 17)]',
                   '$compiled_precision(' + state + ', (' + origin + ')) = (14)',
                   '$compiled_precision(' + state + ', (' + child + ')) = (17)',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
        left = 'expression_numeric_other' if suffix == '_l' else expression + '_l'
        right = 'expression_numeric_other' if suffix == '_r' else expression + '_r'
        if suffix == '_l':
            guards += ['expression_numeric_other = NExprVariable (BYTES "dW5hdXRo") metadata_' + tag]
        state = 'S_numeric_source' + suffix
        guards += [state + ' = S_after[.SOURCES = [{ID n_numeric, AST (PROGRAM eps), OCCURRENCES ([(PCOCCURRENCE pcpath_numeric ' + expression + '), (PCOCCURRENCE pcpath_numeric_l ' + left + '), (PCOCCURRENCE pcpath_numeric_r ' + right + ')])}]]',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
    guards += ['S_numeric_precision = S_after[.POOLS = $float_review_precision(S_after.POOLS, ' + origin + ', 17)]',
               '$compiled_precision(S_numeric_precision, (' + origin + ')) = (17)',
               '$compiled_precision(S_numeric_precision, (' + origin + '_l)) = (14)',
               '$compiled_precision(S_numeric_precision, (' + origin + '_r)) = (14)',
               '$compiled_special_concat_bytes(S_numeric_precision, ' + origin + ') = eps']
    guards += prior.unary_guards([], ('1x', '-1x', '0x', '-4x')[index])
    return checks + guards, derived + len(guards)


def compiler_conditions(checked, paths):
    checks = []
    for index, name in enumerate(CONTROLS):
        state, origin = 'S_numeric_control_' + str(index), 'porigin_numeric_control_' + str(index)
        binary = origin + '_binary'
        checks += [state + ' = $php_run(' + checked[name]['fixture'] + ', 0, ' + json.dumps(base64.b64encode(bytes(paths[name])).decode()) + ')',
                   state + '.COMPLETION = BUDGET',
                   '$special_review_concat_path(' + state + '.SOURCES[0].OCCURRENCES) = (pcpath_numeric_control_' + str(index) + ')',
                   origin + ' = PORIGIN 0 pcpath_numeric_control_' + str(index),
                   '$origin_child((' + origin + '), [PCFIELD 0, PCFIELD 0]) = (' + binary + ')']
        if name in ROWS:
            operation, left_name, right_name = ROWS[name]
            left, right = NUMBERS[left_name], NUMBERS[right_name]
            result = outcome(operation, left, right)
            rendered = text(result)
            checks += ['$compiled_read(' + state + ', ' + binary + ') = (' + value(result) + ')',
                       '$compiled_special_concat_bytes(' + state + ', ' + binary + ') = ($ptascii(' + json.dumps(rendered) + '))',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = ($ptascii(' + json.dumps(rendered + 'x') + '))',
                       '$compiled_string_value(' + state + ', ' + origin + ', PSTRING ($ptascii(' + json.dumps(rendered + 'x') + '))) = PSTRING_CARRIER INTERNED_STRING ($ptascii(' + json.dumps(rendered + 'x') + '))']
            for field, number in ((0, left), (1, right)):
                child = binary + '_' + str(field)
                checks += ['$origin_child((' + binary + '), [PCFIELD ' + str(field) + ']) = (' + child + ')',
                           '$compiled_read(' + state + ', ' + child + ') = (' + number[1] + ')',
                           '$compiled_precision(' + state + ', (' + child + ')) = (14)',
                           '$compiled_special_concat_bytes(' + state + ', ' + child + ') =/= eps',
                           '$compiled_order_number(' + number[1] + ') = (' + number[2] + ')']
        elif name in ('nan-left', 'outside-op', 'string-left', 'string-right', 'boolean-left', 'null-left', 'nan-arithmetic'):
            result = name not in ('nan-left', 'boolean-left', 'nan-arithmetic')
            rendered = text(result)
            checks += ['$compiled_read(' + state + ', ' + binary + ') = (' + value(result) + ')',
                       '$compiled_special_concat_bytes(' + state + ', ' + binary + ') = ($ptascii(' + json.dumps(rendered) + '))',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = ($ptascii(' + json.dumps(rendered + 'x') + '))',
                       '$compiled_string_value(' + state + ', ' + origin + ', PSTRING ($ptascii(' + json.dumps(rendered + 'x') + '))) = PSTRING_CARRIER INTERNED_STRING ($ptascii(' + json.dumps(rendered + 'x') + '))']
        else:
            result = name in ('string-left', 'string-right', 'null-left', 'outside-op')
            checks += ['$compiled_read(' + state + ', ' + binary + ') = (' + value(result) + ')',
                       '$compiled_special_concat_bytes(' + state + ', ' + binary + ') = eps',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
        if name == 'less-f15':
            child, changed = binary + '_0', state + '_string'
            checks += [changed + ' = ' + state + '[.POOLS = $special_review_pools(' + state + '.POOLS, ' + child + ', (PSTRING ($ptascii("1.5"))))]',
                       '$compiled_read(' + changed + ', ' + child + ') = (PSTRING ($ptascii("1.5")))',
                       '$compiled_special_concat_bytes(' + changed + ', ' + child + ') = ($ptascii("1.5"))',
                       '$coerce_number(PSTRING ($ptascii("1.5"))) = COERCED (NFLOAT 4609434218613702656) false',
                       '$compiled_order_number(PSTRING ($ptascii("1.5"))) = eps',
                       '$compiled_read(' + changed + ', ' + binary + ') = (PBOOL true)',
                       '$compiled_special_concat_bytes(' + changed + ', ' + binary + ') = ($ptascii("1"))']
        if name == 'spaceship-f25':
            for field in (0, 1):
                changed, child = state + '_nan_' + str(field), binary + '_' + str(field)
                other = right[2] if field == 0 else left[2]
                args = 'NFLOAT 9221120237041090560, ' + other if field == 0 else other + ', NFLOAT 9221120237041090560'
                checks += [changed + ' = ' + state + '[.POOLS = $special_review_pools(' + state + '.POOLS, ' + child + ', (PFLOAT 9221120237041090560))]',
                           '$compiled_read(' + changed + ', ' + child + ') = (PFLOAT 9221120237041090560)',
                           '$compiled_special_concat_bytes(' + changed + ', ' + child + ') =/= eps',
                           '$compiled_read(' + changed + ', ' + binary + ') = (PINT 1)',
                           '$num_compare(' + args + ') = 1',
                           '$compiled_order_number(PFLOAT 9221120237041090560) = eps',
                           '$compiled_special_concat_bytes(' + changed + ', ' + binary + ') = eps']
            changed, child = state + '_invalid_bits', binary + '_0'
            checks += [changed + ' = ' + state + '[.POOLS = $special_review_pools(' + state + '.POOLS, ' + child + ', (PFLOAT 18446744073709551616))]',
                       '$compiled_read(' + changed + ', ' + child + ') = (PFLOAT 18446744073709551616)',
                       '$compiled_special_concat_bytes(' + changed + ', ' + child + ') =/= eps',
                       '$compiled_order_number(PFLOAT 18446744073709551616) = eps',
                       '$compiled_special_concat_bytes(' + changed + ', ' + binary + ') = eps']
    return checks


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    watched = [Path(module.__file__) for module in (source, source.prior, source.prior.prior, source.arithmetic, source.unary, prior, prior.source, prior.prior, prior.strings, runner)] + [Path(__file__)]
    before = {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.cases = cases
    runner.conditions = conditions
    runner.compiler_conditions = compiler_conditions
    runner.CONTROLS = CONTROLS
    passed = runner.main(expected_outputs=cases.OUTPUTS)
    assert before == {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = 'Four authentic-source-seeded nonNaN numeric fixtures add own-result/type, missing/outcome-changing child reads, both child sources and three precision refusals. Independent binary64 reference order explicitly float-casts integer operands in mixed pairs; tables distinguish all seven operators, signed zeros, infinities, adjacent binary64 values, MAX rounding to2**63 and integers above2**53. The quiet numeric-string mutation preserves bytes/coercion/order and numeric projection still refuses strings; the separate mixed number/string certificate now admits this exact-byte context. NaN pool mutations preserve forward unordered+1 and cached spaceship1 with existing child-byte authority but remain excluded; invalid64bit floats also refuse. The former NAN ConstFetch, finite XOR, string and Boolean/null selectors check their separately reviewed typed-value, logical and comparison admissions; the existing arithmetic-NaN selector now uses its separate exact quiet-producer VALUE proof, while owning comparisons remain outside this numeric slice, with no NaN Boolean/string conversion claim. Five historical compiler selectors and eight mutations are promoted separately; source/native4 are reused once, author prefixes remain exact, and owners/throw/fixed bounds/budgets keep their laws. No cross-campaign unique sum or new coercion/ownership claim; fixture/compiler conditions carry source0.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
