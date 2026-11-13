#!/usr/bin/env python3
"""Independent signed modulo, nonzero-divisor and certificate checks."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_integer_modulo_special_concat_leading_key_cases as cases
import string_offset_request_base_integer_modulo_special_concat_leading_key_protocol as source
import string_offset_request_base_bool_null_unary_special_concat_leading_key_review_state as prior

runner = prior.runner
MINIMUM, MAXIMUM = -9223372036854775808, 9223372036854775807
INTEGERS = {'positive': (5, 2, 1), 'negative-left': (-5, 2, -1),
            'negative-right': (5, -2, 1), 'both-negative': (-5, -2, -1),
            'minimum-minus-one': (MINIMUM, -1, 0), 'minimum-maximum': (MINIMUM, MAXIMUM, -1),
            'maximum-minimum': (MAXIMUM, MINIMUM, MAXIMUM), 'zero-one': (0, 1, 0)}


def term(number):
    return str(number) if number >= 0 else '$(' + str(number) + ')'


def integer_source(number):
    return '((0 - 9223372036854775807) - 1)' if number == MINIMUM else str(number)


CONTROLS = {name: ("<?php $x = ((" + integer_source(left) + ' % ' + integer_source(right) + ") . null) . 'x';\n").encode()
            for name, (left, right, result) in INTEGERS.items()} | {
    'float-left': b"<?php $x = ((5.0 % 2) . null) . 'x';\n",
    'float-right': b"<?php $x = ((5 % 2.0) . null) . 'x';\n",
    'numeric-string': b"<?php $x = (('5' % 2) . null) . 'x';\n",
    'boolean-left': b"<?php $x = ((true % 2) . null) . 'x';\n",
    'null-left': b"<?php $x = ((null % 2) . null) . 'x';\n",
    'zero-divisor': b"<?php $x = ((1 % 0) . null) . 'x';\n",
    'fractional-float': b"<?php $x = ((5.5 % 2) . null) . 'x';\n",
    'leading-string': b"<?php $x = (('5tail' % 2) . null) . 'x';\n",
    'nan-left': b"<?php $x = ((NAN % 2) . null) . 'x';\n",
    'array-left': b"<?php $x = (([] % 2) . null) . 'x';\n",
    'same-result-shift': b"<?php $x = ((0 << 1) . null) . 'x';\n"}


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    tag = ('modulo_root', 'modulo_root', 'modulo_root_l', 'modulo_root_child')[index]
    origin, expression = 'porigin_' + tag, 'expression_' + tag
    guards = [origin + ' = PORIGIN n_modulo pcpath_modulo',
              origin + '_l = PORIGIN n_modulo pcpath_modulo_l',
              origin + '_r = PORIGIN n_modulo pcpath_modulo_r']
    for suffix, value in (('drop', 'eps'), ('wrong', '(PINT 99)'), ('type', '(PFLOAT 0)')):
        state = 'S_modulo_' + suffix
        guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + origin + ', ' + value + ')]',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps',
                   '$string_read_request_base_saved(' + state + ', pstringread) = eps']
    mutants = (('4', '5'), ('$(-4)', '5'), ('0', '3'), ('8', '7'))[index]
    for suffix, number in zip(('_l', '_r'), mutants):
        child = origin + suffix
        for operation, value in (('drop', 'eps'), ('wrong', '(PINT ' + number + ')')):
            state = 'S_modulo_child' + suffix + '_' + operation
            guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + child + ', ' + value + ')]',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps',
                       '$string_read_request_base_saved(' + state + ', pstringread) = eps']
        state = 'S_modulo_precision' + suffix
        guards += [state + ' = S_after[.POOLS = $float_review_precision(S_after.POOLS, ' + child + ', 17)]',
                   '$compiled_precision(' + state + ', (' + origin + ')) = (14)',
                   '$compiled_precision(' + state + ', (' + child + ')) = (17)',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
        left = 'expression_modulo_other' if suffix == '_l' else expression + '_l'
        right = 'expression_modulo_other' if suffix == '_r' else expression + '_r'
        if suffix == '_l':
            guards += ['expression_modulo_other = NExprVariable (BYTES "dW5hdXRo") metadata_' + tag]
        state = 'S_modulo_source' + suffix
        guards += [state + ' = S_after[.SOURCES = [{ID n_modulo, AST (PROGRAM eps), OCCURRENCES ([(PCOCCURRENCE pcpath_modulo ' + expression + '), (PCOCCURRENCE pcpath_modulo_l ' + left + '), (PCOCCURRENCE pcpath_modulo_r ' + right + ')])}]]',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
    guards += ['S_modulo_precision = S_after[.POOLS = $float_review_precision(S_after.POOLS, ' + origin + ', 17)]',
               '$compiled_precision(S_modulo_precision, (' + origin + ')) = (17)',
               '$compiled_precision(S_modulo_precision, (' + origin + '_l)) = (14)',
               '$compiled_precision(S_modulo_precision, (' + origin + '_r)) = (14)',
               '$compiled_special_concat_bytes(S_modulo_precision, ' + origin + ') = eps']
    guards += prior.unary_guards([], ('1x', '-1x', '0x', '-4x')[index])
    return checks + guards, derived + len(guards)


def compiler_conditions(checked, paths):
    checks = []
    numeric = {'float-left': ('PFLOAT 4617315517961601024', 'PINT 2', '5', '2', 1),
               'float-right': ('PINT 5', 'PFLOAT 4611686018427387904', '5', '2', 1),
               'numeric-string': ('PSTRING ($ptascii("5"))', 'PINT 2', '5', '2', 1),
               'boolean-left': ('PBOOL true', 'PINT 2', '1', '2', 1),
               'null-left': ('PNULL', 'PINT 2', '', '2', 0),
               'same-result-shift': ('PINT 0', 'PINT 1', '0', '1', 0)}
    for index, name in enumerate(CONTROLS):
        state, origin = 'S_modulo_control_' + str(index), 'porigin_modulo_control_' + str(index)
        binary = origin + '_binary'
        checks += [state + ' = $php_run(' + checked[name]['fixture'] + ', 0, ' + json.dumps(base64.b64encode(bytes(paths[name])).decode()) + ')',
                   state + '.COMPLETION = BUDGET',
                   '$special_review_concat_path(' + state + '.SOURCES[0].OCCURRENCES) = (pcpath_modulo_control_' + str(index) + ')',
                   origin + ' = PORIGIN 0 pcpath_modulo_control_' + str(index),
                   '$origin_child((' + origin + '), [PCFIELD 0, PCFIELD 0]) = (' + binary + ')']
        if name in INTEGERS:
            left, right, result = INTEGERS[name]
            scalars = ('PINT ' + term(left), 'PINT ' + term(right), str(left), str(right), result)
            checks += ['$compiled_read(' + state + ', ' + binary + ') = (PINT ' + term(result) + ')',
                       '$long_mod(' + term(left) + ', ' + term(right) + ') = IRESULT ' + term(result),
                       '$compiled_special_concat_bytes(' + state + ', ' + binary + ') = ($ptascii(' + json.dumps(str(result)) + '))',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = ($ptascii(' + json.dumps(str(result) + 'x') + '))',
                       '$compiled_string_value(' + state + ', ' + origin + ', PSTRING ($ptascii(' + json.dumps(str(result) + 'x') + '))) = PSTRING_CARRIER INTERNED_STRING ($ptascii(' + json.dumps(str(result) + 'x') + '))']
        else:
            scalars = numeric.get(name)
            checks += ['$compiled_special_concat_bytes(' + state + ', ' + binary + ') = eps',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
            checks += ['$compiled_read(' + state + ', ' + binary + ') = ' + ('(PINT ' + term(scalars[4]) + ')' if scalars else 'eps')]
        if scalars:
            for field, value, text in ((0, scalars[0], scalars[2]), (1, scalars[1], scalars[3])):
                child = binary + '_' + str(field)
                checks += ['$origin_child((' + binary + '), [PCFIELD ' + str(field) + ']) = (' + child + ')',
                           '$compiled_read(' + state + ', ' + child + ') = (' + value + ')',
                           '$compiled_precision(' + state + ', (' + child + ')) = (14)',
                           '$compiled_special_concat_bytes(' + state + ', ' + child + ') = ($ptascii(' + json.dumps(text) + '))']
        if name == 'positive':
            for field, number, bits in ((0, 5, 4617315517961601024), (1, 2, 4611686018427387904)):
                changed, child = state + '_float_' + str(field), binary + '_' + str(field)
                checks += [changed + ' = ' + state + '[.POOLS = $special_review_pools(' + state + '.POOLS, ' + child + ', (PFLOAT ' + str(bits) + '))]',
                           '$compiled_read(' + changed + ', ' + child + ') = (PFLOAT ' + str(bits) + ')',
                           '$compiled_special_concat_bytes(' + changed + ', ' + child + ') = ($ptascii(' + json.dumps(str(number)) + '))',
                           '$compiled_read(' + changed + ', ' + binary + ') = (PINT 1)',
                           '$float_long(' + str(bits) + ', true) = (' + str(number) + ', eps)',
                           '$compiled_special_concat_bytes(' + changed + ', ' + binary + ') = eps']
        if name == 'zero-one':
            for field in (0, 1):
                child = binary + '_' + str(field)
                for label, number in (('below', MINIMUM - 1), ('above', MAXIMUM + 1)):
                    changed = state + '_range_' + str(field) + '_' + label
                    left, right = (number, 1) if field == 0 else (0, number)
                    checks += [changed + ' = ' + state + '[.POOLS = $special_review_pools(' + state + '.POOLS, ' + child + ', (PINT ' + term(number) + '))]',
                               '$compiled_read(' + changed + ', ' + child + ') = (PINT ' + term(number) + ')',
                               '$compiled_read(' + changed + ', ' + binary + ') = (PINT 0)',
                               '$compiled_special_concat_bytes(' + changed + ', ' + child + ') = ($ptascii(' + json.dumps(str(field)) + '))',
                               '~$long_range(' + term(number) + ')',
                               '$long_mod(' + term(left) + ', ' + term(right) + ') = IRESULT 0',
                               '$compiled_special_concat_bytes(' + changed + ', ' + binary + ') = eps']
            changed, child = state + '_zero', binary + '_1'
            checks += [changed + ' = ' + state + '[.POOLS = $special_review_pools(' + state + '.POOLS, ' + child + ', (PINT 0))]',
                       '$compiled_read(' + changed + ', ' + child + ') = (PINT 0)',
                       '$compiled_special_concat_bytes(' + changed + ', ' + child + ') = ($ptascii("1"))',
                       '$compiled_read(' + changed + ', ' + binary + ') = (PINT 0)',
                       '$long_mod(0, 0) = INTZERO',
                       '$compiled_special_concat_bytes(' + changed + ', ' + binary + ') = eps']
    return checks


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    watched = [Path(module.__file__) for module in (source, source.prior, source.prior.prior, source.arithmetic, source.bitnot, prior, prior.source, prior.prior, prior.strings, runner)] + [Path(__file__)]
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
    report['scope'] = 'Four authentic-source-seeded integer modulo fixtures add own-result/type, both child read/source and all precision refusals. Explicit signed remainder tuples avoid host negative-modulo convention and cover MIN modulo minus-one. Per-side quiet float pools and valid-output0 range mutations isolate PINT/input-range admission. A forged cached0 with actual divisor0 refuses because the pure helper returns INTZERO; real zero-divisor compiler input has no own constant fact. Mixed/fractional/leading-string/NaN/array and same-result shift refusals carry zero source credit and do not validate runtime zero/error/coercion behavior. Original native4 are reused once; owners, supplied throw, fixed bounds and budgets retain their laws.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
