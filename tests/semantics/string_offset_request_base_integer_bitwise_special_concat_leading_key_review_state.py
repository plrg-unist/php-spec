#!/usr/bin/env python3
"""Independent integer bitwise dispatch, type, range and source checks."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_integer_bitwise_special_concat_leading_key_cases as cases
import string_offset_request_base_integer_bitwise_special_concat_leading_key_protocol as source
import string_offset_request_base_bool_null_unary_special_concat_leading_key_review_state as prior

runner = prior.runner
MINIMUM, MAXIMUM = -9223372036854775808, 9223372036854775807
OPERATORS = {'and': ('&', lambda left, right: left & right),
             'or': ('|', lambda left, right: left | right),
             'xor': ('^', lambda left, right: left ^ right)}
PAIRS = {'overlap': (6, 3), 'endpoints': (MINIMUM, MAXIMUM), 'negative': (-1, 5)}
INTEGERS = {name + '-' + pair: (symbol, left, right, apply(left, right))
            for name, (symbol, apply) in OPERATORS.items() for pair, (left, right) in PAIRS.items()} | {
    'and-zero': ('&', 0, 0, 0)}


def term(number):
    return str(number) if number >= 0 else '$(' + str(number) + ')'


def integer_source(number):
    return '((0 - 9223372036854775807) - 1)' if number == MINIMUM else str(number)


CONTROLS = {name: ("<?php $x = ((" + integer_source(left) + ' ' + symbol + ' ' + integer_source(right) + ") . null) . 'x';\n").encode()
            for name, (symbol, left, right, result) in INTEGERS.items()} | {
    'float-left': b"<?php $x = ((6.0 | 3) . null) . 'x';\n",
    'float-right': b"<?php $x = ((6 | 3.0) . null) . 'x';\n",
    'numeric-string': b"<?php $x = (('6' | 3) . null) . 'x';\n",
    'boolean-left': b"<?php $x = ((true | 2) . null) . 'x';\n",
    'null-left': b"<?php $x = ((null | 2) . null) . 'x';\n",
    'string-bytes': b"<?php $x = (('1' | '2') . null) . 'x';\n",
    'fractional-float': b"<?php $x = ((1.5 | 2) . null) . 'x';\n",
    'nan-left': b"<?php $x = ((NAN | 2) . null) . 'x';\n",
    'array-left': b"<?php $x = (([] | 2) . null) . 'x';\n",
    'other-shift': b"<?php $x = ((6 << 1) . null) . 'x';\n"}


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    tag = ('bitwise_root', 'bitwise_root', 'bitwise_root_l', 'bitwise_root_child')[index]
    origin, expression = 'porigin_' + tag, 'expression_' + tag
    guards = [origin + ' = PORIGIN n_bitwise pcpath_bitwise',
              origin + '_l = PORIGIN n_bitwise pcpath_bitwise_l',
              origin + '_r = PORIGIN n_bitwise pcpath_bitwise_r']
    for suffix, value in (('drop', 'eps'), ('wrong', '(PINT 99)'), ('type', '(PBOOL true)')):
        state = 'S_bitwise_' + suffix
        guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + origin + ', ' + value + ')]',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps',
                   '$string_read_request_base_saved(' + state + ', pstringread) = eps']
    mutants = (('0', '0'), ('0', '0'), ('1', '2'), ('0', '0'))[index]
    for suffix, number in zip(('_l', '_r'), mutants):
        child = origin + suffix
        for operation, value in (('drop', 'eps'), ('wrong', '(PINT ' + number + ')')):
            state = 'S_bitwise_child' + suffix + '_' + operation
            guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + child + ', ' + value + ')]',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps',
                       '$string_read_request_base_saved(' + state + ', pstringread) = eps']
        state = 'S_bitwise_precision' + suffix
        guards += [state + ' = S_after[.POOLS = $float_review_precision(S_after.POOLS, ' + child + ', 17)]',
                   '$compiled_precision(' + state + ', (' + origin + ')) = (14)',
                   '$compiled_precision(' + state + ', (' + child + ')) = (17)',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
        left = 'expression_bitwise_other' if suffix == '_l' else expression + '_l'
        right = 'expression_bitwise_other' if suffix == '_r' else expression + '_r'
        if suffix == '_l':
            guards += ['expression_bitwise_other = NExprVariable (BYTES "dW5hdXRo") metadata_' + tag]
        state = 'S_bitwise_source' + suffix
        guards += [state + ' = S_after[.SOURCES = [{ID n_bitwise, AST (PROGRAM eps), OCCURRENCES ([(PCOCCURRENCE pcpath_bitwise ' + expression + '), (PCOCCURRENCE pcpath_bitwise_l ' + left + '), (PCOCCURRENCE pcpath_bitwise_r ' + right + ')])}]]',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
    guards += ['S_bitwise_precision = S_after[.POOLS = $float_review_precision(S_after.POOLS, ' + origin + ', 17)]',
               '$compiled_precision(S_bitwise_precision, (' + origin + ')) = (17)',
               '$compiled_precision(S_bitwise_precision, (' + origin + '_l)) = (14)',
               '$compiled_precision(S_bitwise_precision, (' + origin + '_r)) = (14)',
               '$compiled_special_concat_bytes(S_bitwise_precision, ' + origin + ') = eps']
    guards += prior.unary_guards([], ('1x', '-1x', '0x', '-4x')[index])
    return checks + guards, derived + len(guards)


def compiler_conditions(checked, paths):
    checks = []
    numeric = {'float-left': ('PFLOAT 4618441417868443648', 'PINT 3', '6', '3', 7),
               'float-right': ('PINT 6', 'PFLOAT 4613937818241073152', '6', '3', 7),
               'numeric-string': ('PSTRING ($ptascii("6"))', 'PINT 3', '6', '3', 7),
               'boolean-left': ('PBOOL true', 'PINT 2', '1', '2', 3),
               'null-left': ('PNULL', 'PINT 2', '', '2', 2),
               'other-shift': ('PINT 6', 'PINT 1', '6', '1', 12)}
    for index, name in enumerate(CONTROLS):
        state, origin = 'S_bitwise_control_' + str(index), 'porigin_bitwise_control_' + str(index)
        binary = origin + '_binary'
        checks += [state + ' = $php_run(' + checked[name]['fixture'] + ', 0, ' + json.dumps(base64.b64encode(bytes(paths[name])).decode()) + ')',
                   state + '.COMPLETION = BUDGET',
                   '$special_review_concat_path(' + state + '.SOURCES[0].OCCURRENCES) = (pcpath_bitwise_control_' + str(index) + ')',
                   origin + ' = PORIGIN 0 pcpath_bitwise_control_' + str(index),
                   '$origin_child((' + origin + '), [PCFIELD 0, PCFIELD 0]) = (' + binary + ')']
        if name in INTEGERS:
            symbol, left, right, result = INTEGERS[name]
            scalars = ('PINT ' + term(left), 'PINT ' + term(right), str(left), str(right), result)
            checks += ['$compiled_read(' + state + ', ' + binary + ') = (PINT ' + term(result) + ')',
                       '$compiled_special_concat_bytes(' + state + ', ' + binary + ') = ($ptascii(' + json.dumps(str(result)) + '))',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = ($ptascii(' + json.dumps(str(result) + 'x') + '))',
                       '$compiled_string_value(' + state + ', ' + origin + ', PSTRING ($ptascii(' + json.dumps(str(result) + 'x') + '))) = PSTRING_CARRIER INTERNED_STRING ($ptascii(' + json.dumps(str(result) + 'x') + '))']
        else:
            scalars = numeric.get(name)
            if name == 'other-shift':
                checks += ['$compiled_special_concat_bytes(' + state + ', ' + binary + ') = ($ptascii("12"))',
                           '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = ($ptascii("12x"))',
                           '$compiled_string_value(' + state + ', ' + origin + ', PSTRING ($ptascii("12x"))) = PSTRING_CARRIER INTERNED_STRING ($ptascii("12x"))']
            elif name == 'string-bytes':
                checks += ['$compiled_special_concat_bytes(' + state + ', ' + binary + ') = ($ptascii("3"))',
                           '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = ($ptascii("3x"))',
                           '$compiled_string_value(' + state + ', ' + origin + ', PSTRING ($ptascii("3x"))) = PSTRING_CARRIER INTERNED_STRING ($ptascii("3x"))']
            else:
                checks += ['$compiled_special_concat_bytes(' + state + ', ' + binary + ') = eps',
                           '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
            if scalars:
                checks += ['$compiled_read(' + state + ', ' + binary + ') = (PINT ' + term(scalars[4]) + ')']
            elif name == 'string-bytes':
                checks += ['$compiled_read(' + state + ', ' + binary + ') = (pvalue_bitwise_bytes)',
                           '$string_plain(pvalue_bitwise_bytes) = PSTRING ($ptascii("3"))']
            else:
                checks += ['$compiled_read(' + state + ', ' + binary + ') = eps']
        if scalars:
            for field, value, text in ((0, scalars[0], scalars[2]), (1, scalars[1], scalars[3])):
                child = binary + '_' + str(field)
                checks += ['$origin_child((' + binary + '), [PCFIELD ' + str(field) + ']) = (' + child + ')',
                           '$compiled_read(' + state + ', ' + child + ') = (' + value + ')',
                           '$compiled_precision(' + state + ', (' + child + ')) = (14)',
                           '$compiled_special_concat_bytes(' + state + ', ' + child + ') = ($ptascii(' + json.dumps(text) + '))']
        if name == 'or-overlap':
            for field, number, bits in ((0, 6, 4618441417868443648), (1, 3, 4613937818241073152)):
                changed, child = state + '_float_' + str(field), binary + '_' + str(field)
                checks += [changed + ' = ' + state + '[.POOLS = $special_review_pools(' + state + '.POOLS, ' + child + ', (PFLOAT ' + str(bits) + '))]',
                           '$compiled_read(' + changed + ', ' + child + ') = (PFLOAT ' + str(bits) + ')',
                           '$compiled_special_concat_bytes(' + changed + ', ' + child + ') = ($ptascii(' + json.dumps(str(number)) + '))',
                           '$compiled_read(' + changed + ', ' + binary + ') = (PINT 7)',
                           '$float_long(' + str(bits) + ', true) = (' + str(number) + ', eps)',
                           '$compiled_special_concat_bytes(' + changed + ', ' + binary + ') = eps']
        if name == 'and-zero':
            for field in (0, 1):
                child = binary + '_' + str(field)
                for label, number in (('below', MINIMUM - 1), ('above', MAXIMUM + 1)):
                    changed = state + '_range_' + str(field) + '_' + label
                    left, right = (number, 0) if field == 0 else (0, number)
                    checks += [changed + ' = ' + state + '[.POOLS = $special_review_pools(' + state + '.POOLS, ' + child + ', (PINT ' + term(number) + '))]',
                               '$compiled_read(' + changed + ', ' + child + ') = (PINT ' + term(number) + ')',
                               '$compiled_read(' + changed + ', ' + binary + ') = (PINT 0)',
                               '$compiled_special_concat_bytes(' + changed + ', ' + child + ') = ($ptascii("0"))',
                               '~$long_range(' + term(number) + ')',
                               '$long_and(' + term(left) + ', ' + term(right) + ') = 0',
                               '$compiled_special_concat_bytes(' + changed + ', ' + binary + ') = eps']
    return checks


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    watched = [Path(module.__file__) for module in (source, source.prior, source.prior.prior, source.arithmetic, prior, prior.source, prior.prior, prior.strings, runner)] + [Path(__file__)]
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
    report['scope'] = 'Four authentic-source-seeded integer AND/OR/XOR fixtures add own-result/type, both child read/source and all precision refusals. Independent overlapping6/3 compiler controls distinguish AND2/OR7/XOR5; signed endpoints and negative masks retain exact integer results. Per-side literal float mutations retain quiet conversion/output7 but refuse integer admission. AND0 annihilates coherent out-of-range values one side at a time, isolating input range checks while output0 stays valid; no independent result-range isolation is claimed. Mixed/float/bool/null/array controls remain separate. The former two-string OR refusal now checks the reviewed exact-PSTRING admission. The former shift refusal now checks the reviewed exact-PINT shift admission. Original native4 are reused once; owners, supplied throw, fixed bounds and budgets retain their laws. Derived/compiler conditions carry zero source credit.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
