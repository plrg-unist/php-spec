#!/usr/bin/env python3
"""Independent exact integer comparison, result typing and boundary checks."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_integer_equality_special_concat_leading_key_cases as cases
import string_offset_request_base_integer_equality_special_concat_leading_key_protocol as source
import string_offset_request_base_bool_null_unary_special_concat_leading_key_review_state as prior

runner = prior.runner
MINIMUM, MAXIMUM = -9223372036854775808, 9223372036854775807
INTEGERS = {}
for label, symbol in (('equal', '=='), ('notequal', '!='), ('spaceship', '<=>')):
    for name, left, right in (('negative', 0, 1), ('zero', 0, 0), ('positive', 1, 0),
                              ('minmax', MINIMUM, MAXIMUM), ('maxmin', MAXIMUM, MINIMUM),
                              ('minsame', MINIMUM, MINIMUM)):
        result = left == right if symbol == '==' else left != right if symbol == '!=' else (left > right) - (left < right)
        INTEGERS[label + '-' + name] = symbol, left, right, result


def term(number):
    return str(number) if number >= 0 else '$(' + str(number) + ')'


def integer_source(number):
    return '((0 - 9223372036854775807) - 1)' if number == MINIMUM else str(number)


def result_value(result):
    return 'PBOOL ' + str(result).lower() if isinstance(result, bool) else 'PINT ' + term(result)


def result_text(result):
    return ('1' if result else '') if isinstance(result, bool) else str(result)


CONTROLS = {name: ("<?php $x = ((" + integer_source(left) + ' ' + symbol + ' ' + integer_source(right) + ") . null) . 'x';\n").encode()
            for name, (symbol, left, right, result) in INTEGERS.items()} | {
    'float-left': b"<?php $x = ((0.0 == 0) . null) . 'x';\n",
    'float-right': b"<?php $x = ((0 == 0.0) . null) . 'x';\n",
    'string-left': b"<?php $x = (('0' == 0) . null) . 'x';\n",
    'boolean-right': b"<?php $x = ((0 == false) . null) . 'x';\n",
    'null-left': b"<?php $x = ((null == 0) . null) . 'x';\n",
    'array-left': b"<?php $x = (([] == 0) . null) . 'x';\n",
    'float-spaceship': b"<?php $x = ((0 <=> 0.0) . null) . 'x';\n",
    'mixed-notequal': b"<?php $x = ((1 != true) . null) . 'x';\n",
    'same-result-power': b"<?php $x = ((0 ** 1) . null) . 'x';\n"}


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    tag = ('equality_root', 'equality_root', 'equality_root_l', 'equality_root_child_l')[index]
    origin, expression = 'porigin_' + tag, 'expression_' + tag
    guards = [origin + ' = PORIGIN n_equality pcpath_equality',
              origin + '_l = PORIGIN n_equality pcpath_equality_l',
              origin + '_r = PORIGIN n_equality pcpath_equality_r']
    wrong, wrong_type = (('PBOOL false', 'PINT 1'), ('PINT 0', 'PBOOL true'),
                         ('PBOOL true', 'PINT 0'), ('PBOOL false', 'PINT 1'))[index]
    for suffix, value in (('drop', 'eps'), ('wrong', '(' + wrong + ')'), ('type', '(' + wrong_type + ')')):
        state = 'S_equality_' + suffix
        guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + origin + ', ' + value + ')]',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps',
                   '$string_read_request_base_saved(' + state + ', pstringread) = eps']
    mutants = (('PINT 1', 'PINT 1'), ('PINT 3', 'PINT 0'),
               ('PINT 1', 'PINT 1'), ('PINT 1', 'PINT 2'))[index]
    for suffix, value in zip(('_l', '_r'), mutants):
        child = origin + suffix
        for operation, replacement in (('drop', 'eps'), ('wrong', '(' + value + ')')):
            state = 'S_equality_child' + suffix + '_' + operation
            guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + child + ', ' + replacement + ')]',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps',
                       '$string_read_request_base_saved(' + state + ', pstringread) = eps']
        state = 'S_equality_precision' + suffix
        guards += [state + ' = S_after[.POOLS = $float_review_precision(S_after.POOLS, ' + child + ', 17)]',
                   '$compiled_precision(' + state + ', (' + origin + ')) = (14)',
                   '$compiled_precision(' + state + ', (' + child + ')) = (17)',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
        left = 'expression_equality_other' if suffix == '_l' else expression + '_l'
        right = 'expression_equality_other' if suffix == '_r' else expression + '_r'
        if suffix == '_l':
            guards += ['expression_equality_other = NExprVariable (BYTES "dW5hdXRo") metadata_' + tag]
        state = 'S_equality_source' + suffix
        guards += [state + ' = S_after[.SOURCES = [{ID n_equality, AST (PROGRAM eps), OCCURRENCES ([(PCOCCURRENCE pcpath_equality ' + expression + '), (PCOCCURRENCE pcpath_equality_l ' + left + '), (PCOCCURRENCE pcpath_equality_r ' + right + ')])}]]',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
    guards += ['S_equality_precision = S_after[.POOLS = $float_review_precision(S_after.POOLS, ' + origin + ', 17)]',
               '$compiled_precision(S_equality_precision, (' + origin + ')) = (17)',
               '$compiled_precision(S_equality_precision, (' + origin + '_l)) = (14)',
               '$compiled_precision(S_equality_precision, (' + origin + '_r)) = (14)',
               '$compiled_special_concat_bytes(S_equality_precision, ' + origin + ') = eps']
    guards += prior.unary_guards([], ('1x', '-1x', '0x', '-4x')[index])
    return checks + guards, derived + len(guards)


def compiler_conditions(checked, paths):
    checks = []
    scalar_cases = {'float-left': ('PFLOAT 0', 'PINT 0', '0', '0', True),
                    'float-right': ('PINT 0', 'PFLOAT 0', '0', '0', True),
                    'string-left': ('PSTRING ($ptascii("0"))', 'PINT 0', '0', '0', True),
                    'boolean-right': ('PINT 0', 'PBOOL false', '0', '', True),
                    'null-left': ('PNULL', 'PINT 0', '', '0', True),
                    'float-spaceship': ('PINT 0', 'PFLOAT 0', '0', '0', 0),
                    'mixed-notequal': ('PINT 1', 'PBOOL true', '1', '1', False),
                    'same-result-power': ('PINT 0', 'PINT 1', '0', '1', 0)}
    for index, name in enumerate(CONTROLS):
        state, origin = 'S_equality_control_' + str(index), 'porigin_equality_control_' + str(index)
        binary = origin + '_binary'
        checks += [state + ' = $php_run(' + checked[name]['fixture'] + ', 0, ' + json.dumps(base64.b64encode(bytes(paths[name])).decode()) + ')',
                   state + '.COMPLETION = BUDGET',
                   '$special_review_concat_path(' + state + '.SOURCES[0].OCCURRENCES) = (pcpath_equality_control_' + str(index) + ')',
                   origin + ' = PORIGIN 0 pcpath_equality_control_' + str(index),
                   '$origin_child((' + origin + '), [PCFIELD 0, PCFIELD 0]) = (' + binary + ')']
        if name in INTEGERS:
            symbol, left, right, result = INTEGERS[name]
            value, text = result_value(result), result_text(result)
            scalars = 'PINT ' + term(left), 'PINT ' + term(right), str(left), str(right), result
            checks += ['$compiled_read(' + state + ', ' + binary + ') = (' + value + ')',
                       '$echo_value(' + value + ') = $ptascii(' + json.dumps(text) + ')',
                       '$compiled_special_concat_bytes(' + state + ', ' + binary + ') = ($ptascii(' + json.dumps(text) + '))',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = ($ptascii(' + json.dumps(text + 'x') + '))',
                       '$compiled_string_value(' + state + ', ' + origin + ', PSTRING ($ptascii(' + json.dumps(text + 'x') + '))) = PSTRING_CARRIER INTERNED_STRING ($ptascii(' + json.dumps(text + 'x') + '))']
        else:
            scalars = scalar_cases.get(name)
            value = result_value(scalars[4]) if scalars else 'PBOOL false'
            checks += ['$compiled_read(' + state + ', ' + binary + ') = (' + value + ')']
            if name in ('same-result-power', 'float-spaceship'):
                checks += ['$compiled_special_concat_bytes(' + state + ', ' + binary + ') = ($ptascii("0"))',
                           '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = ($ptascii("0x"))',
                           '$compiled_string_value(' + state + ', ' + origin + ', PSTRING ($ptascii("0x"))) = PSTRING_CARRIER INTERNED_STRING ($ptascii("0x"))']
            elif name in ('float-left', 'float-right', 'string-left'):
                checks += ['$compiled_special_concat_bytes(' + state + ', ' + binary + ') = ($ptascii("1"))',
                           '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = ($ptascii("1x"))',
                           '$compiled_string_value(' + state + ', ' + origin + ', PSTRING ($ptascii("1x"))) = PSTRING_CARRIER INTERNED_STRING ($ptascii("1x"))']
            else:
                checks += ['$compiled_special_concat_bytes(' + state + ', ' + binary + ') = eps',
                           '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
        if scalars:
            for field, value, text in ((0, scalars[0], scalars[2]), (1, scalars[1], scalars[3])):
                child = binary + '_' + str(field)
                checks += ['$origin_child((' + binary + '), [PCFIELD ' + str(field) + ']) = (' + child + ')',
                           '$compiled_read(' + state + ', ' + child + ') = (' + value + ')',
                           '$compiled_precision(' + state + ', (' + child + ')) = (14)',
                           '$compiled_special_concat_bytes(' + state + ', ' + child + ') = ($ptascii(' + json.dumps(text) + '))']
        if name in ('equal-zero', 'notequal-zero', 'spaceship-zero'):
            operation = {'==': 'EQUAL', '!=': 'NOTEQUAL', '<=>': 'SPACESHIP'}[INTEGERS[name][0]]
            value = result_value(INTEGERS[name][3])
            for field in (0, 1):
                changed, child = state + '_float_' + str(field), binary + '_' + str(field)
                left, right = ('PFLOAT 0', 'PINT 0') if field == 0 else ('PINT 0', 'PFLOAT 0')
                checks += [changed + ' = ' + state + '[.POOLS = $special_review_pools(' + state + '.POOLS, ' + child + ', (PFLOAT 0))]',
                           '$compiled_read(' + changed + ', ' + child + ') = (PFLOAT 0)',
                           '$compiled_special_concat_bytes(' + changed + ', ' + child + ') = ($ptascii("0"))',
                           '$compiled_read(' + changed + ', ' + binary + ') = (' + value + ')',
                           '$comparison_value(' + operation + ', $scalar_plain_order(' + changed + ', ' + left + ', ' + right + ')) = ' + value,
                           '$compiled_special_concat_bytes(' + changed + ', ' + binary + ') = ($ptascii(' + json.dumps(result_text(INTEGERS[name][3])) + '))']
        ranges = []
        if name in ('equal-positive', 'notequal-positive'):
            ranges = [(field, number) for field in (0, 1) for number in (MINIMUM - 1, MAXIMUM + 1)]
        elif name == 'spaceship-negative':
            ranges = [(0, MINIMUM - 1), (1, MAXIMUM + 1)]
        elif name == 'spaceship-positive':
            ranges = [(0, MAXIMUM + 1), (1, MINIMUM - 1)]
        for serial, (field, number) in enumerate(ranges):
            symbol, left, right, result = INTEGERS[name]
            operation = {'==': 'EQUAL', '!=': 'NOTEQUAL', '<=>': 'SPACESHIP'}[symbol]
            changed, child = state + '_range_' + str(serial), binary + '_' + str(field)
            actual = left if field == 0 else right
            left, right = (number, right) if field == 0 else (left, number)
            value = result_value(result)
            checks += [changed + ' = ' + state + '[.POOLS = $special_review_pools(' + state + '.POOLS, ' + child + ', (PINT ' + term(number) + '))]',
                       '$compiled_read(' + changed + ', ' + child + ') = (PINT ' + term(number) + ')',
                       '$compiled_special_concat_bytes(' + changed + ', ' + child + ') = ($ptascii(' + json.dumps(str(actual)) + '))',
                       '$compiled_read(' + changed + ', ' + binary + ') = (' + value + ')',
                       '~$long_range(' + term(number) + ')',
                       '$comparison_value(' + operation + ', $compare_int(' + term(left) + ', ' + term(right) + ')) = ' + value,
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
    report['scope'] = 'Four authentic-source-seeded exact integer equality/spaceship fixtures add own-result/type, missing/outcome-changing child reads, both child sources and three precision refusals. Independent integer-order compiler tables include signed endpoints and Boolean false empty bytes versus spaceship zero decimal0. Per-side quiet floats retain correct numeric results and literal byte certificates and now pass the reviewed numeric comparison certificate; out-of-range input mutations retain unequal Boolean results or directional spaceship signs. No independent result-range isolation is claimed. Former float-left/right/spaceship selectors now check reviewed typed numeric admission. The string-left selector now checks the separate ordered-number/raw-string admission; Boolean/null and owning comparisons stay outside, with no general runtime coercion or ownership claim. The former exact-PINT power refusal now checks zero-result admission. Five historical compiler selectors and one relational-derived mutation are promoted separately; original native4 are reused once, author recipes remain exact prefixes, and owners/throw/bounds/budgets keep their laws.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
