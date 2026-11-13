#!/usr/bin/env python3
"""Independent signed shifts, count boundaries and certificate checks."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_integer_shift_special_concat_leading_key_cases as cases
import string_offset_request_base_integer_shift_special_concat_leading_key_protocol as source
import string_offset_request_base_bool_null_unary_special_concat_leading_key_review_state as prior

runner = prior.runner
MINIMUM, MAXIMUM = -9223372036854775808, 9223372036854775807
INTEGERS = {
    'left-basic': ('<<', 6, 1, 12), 'left-zero': ('<<', 0, 1, 0),
    'left-identity': ('<<', MINIMUM, 0, MINIMUM), 'left-sign': ('<<', 1, 63, MINIMUM),
    'left-wrap': ('<<', MAXIMUM, 1, -2), 'left-min-wrap': ('<<', MINIMUM, 1, 0),
    'left-width': ('<<', 1, 64, 0), 'left-beyond': ('<<', -5, 65, 0),
    'left-huge': ('<<', 1, MAXIMUM, 0),
    'right-basic': ('>>', 7, 1, 3), 'right-identity': ('>>', MINIMUM, 0, MINIMUM),
    'right-negative': ('>>', -5, 1, -3), 'right-sign': ('>>', MINIMUM, 63, -1),
    'right-positive-sign': ('>>', MAXIMUM, 63, 0),
    'right-width-positive': ('>>', 5, 64, 0), 'right-width-negative': ('>>', -5, 64, -1),
    'right-beyond-negative': ('>>', -5, 65, -1), 'right-huge-negative': ('>>', -5, MAXIMUM, -1)}


def term(number):
    return str(number) if number >= 0 else '$(' + str(number) + ')'


def integer_source(number):
    return '((0 - 9223372036854775807) - 1)' if number == MINIMUM else str(number)


CONTROLS = {name: ("<?php $x = ((" + integer_source(left) + ' ' + symbol + ' ' + integer_source(right) + ") . null) . 'x';\n").encode()
            for name, (symbol, left, right, result) in INTEGERS.items()} | {
    'negative-count-left': b"<?php $x = ((1 << (0 - 1)) . null) . 'x';\n",
    'negative-count-right': b"<?php $x = ((1 >> (0 - 1)) . null) . 'x';\n",
    'float-left': b"<?php $x = ((6.0 << 1) . null) . 'x';\n",
    'float-count': b"<?php $x = ((6 << 1.0) . null) . 'x';\n",
    'numeric-string': b"<?php $x = (('6' << 1) . null) . 'x';\n",
    'boolean-count': b"<?php $x = ((1 << true) . null) . 'x';\n",
    'null-count': b"<?php $x = ((1 << null) . null) . 'x';\n",
    'fractional-value': b"<?php $x = ((6.5 << 1) . null) . 'x';\n",
    'fractional-count': b"<?php $x = ((6 << 1.5) . null) . 'x';\n",
    'nan-count': b"<?php $x = ((6 << NAN) . null) . 'x';\n",
    'array-left': b"<?php $x = (([] << 1) . null) . 'x';\n",
    'same-result-spaceship': b"<?php $x = ((0 <=> 0) . null) . 'x';\n"}


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    tag = ('shift_root_l', 'shift_root', 'shift_root_l', 'shift_root_child')[index]
    origin, expression = 'porigin_' + tag, 'expression_' + tag
    guards = [origin + ' = PORIGIN n_shift pcpath_shift',
              origin + '_l = PORIGIN n_shift pcpath_shift_l',
              origin + '_r = PORIGIN n_shift pcpath_shift_r']
    for suffix, value in (('drop', 'eps'), ('wrong', '(PINT 99)'), ('type', '(PFLOAT 0)')):
        state = 'S_shift_' + suffix
        guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + origin + ', ' + value + ')]',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps',
                   '$string_read_request_base_saved(' + state + ', pstringread) = eps']
    mutants = (('PINT 0', 'PINT 62'), ('PINT 0', 'PINT 0'),
               ('PFLOAT 4607182418800017408', 'PINT 63'), ('PINT 8', 'PINT 0'))[index]
    for suffix, value in zip(('_l', '_r'), mutants):
        child = origin + suffix
        for operation, replacement in (('drop', 'eps'), ('wrong', '(' + value + ')')):
            state = 'S_shift_child' + suffix + '_' + operation
            guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + child + ', ' + replacement + ')]',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps',
                       '$string_read_request_base_saved(' + state + ', pstringread) = eps']
        state = 'S_shift_precision' + suffix
        guards += [state + ' = S_after[.POOLS = $float_review_precision(S_after.POOLS, ' + child + ', 17)]',
                   '$compiled_precision(' + state + ', (' + origin + ')) = (14)',
                   '$compiled_precision(' + state + ', (' + child + ')) = (17)',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
        left = 'expression_shift_other' if suffix == '_l' else expression + '_l'
        right = 'expression_shift_other' if suffix == '_r' else expression + '_r'
        if suffix == '_l':
            guards += ['expression_shift_other = NExprVariable (BYTES "dW5hdXRo") metadata_' + tag]
        state = 'S_shift_source' + suffix
        guards += [state + ' = S_after[.SOURCES = [{ID n_shift, AST (PROGRAM eps), OCCURRENCES ([(PCOCCURRENCE pcpath_shift ' + expression + '), (PCOCCURRENCE pcpath_shift_l ' + left + '), (PCOCCURRENCE pcpath_shift_r ' + right + ')])}]]',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
    guards += ['S_shift_precision = S_after[.POOLS = $float_review_precision(S_after.POOLS, ' + origin + ', 17)]',
               '$compiled_precision(S_shift_precision, (' + origin + ')) = (17)',
               '$compiled_precision(S_shift_precision, (' + origin + '_l)) = (14)',
               '$compiled_precision(S_shift_precision, (' + origin + '_r)) = (14)',
               '$compiled_special_concat_bytes(S_shift_precision, ' + origin + ') = eps']
    guards += prior.unary_guards([], ('1x', '-1x', '0x', '-4x')[index])
    return checks + guards, derived + len(guards)


def compiler_conditions(checked, paths):
    checks = []
    numeric = {'float-left': ('PFLOAT 4618441417868443648', 'PINT 1', '6', '1', 12),
               'float-count': ('PINT 6', 'PFLOAT 4607182418800017408', '6', '1', 12),
               'numeric-string': ('PSTRING ($ptascii("6"))', 'PINT 1', '6', '1', 12),
               'boolean-count': ('PINT 1', 'PBOOL true', '1', '1', 2),
               'null-count': ('PINT 1', 'PNULL', '1', '', 1),
               'same-result-spaceship': ('PINT 0', 'PINT 0', '0', '0', 0)}
    for index, name in enumerate(CONTROLS):
        state, origin = 'S_shift_control_' + str(index), 'porigin_shift_control_' + str(index)
        binary = origin + '_binary'
        checks += [state + ' = $php_run(' + checked[name]['fixture'] + ', 0, ' + json.dumps(base64.b64encode(bytes(paths[name])).decode()) + ')',
                   state + '.COMPLETION = BUDGET',
                   '$special_review_concat_path(' + state + '.SOURCES[0].OCCURRENCES) = (pcpath_shift_control_' + str(index) + ')',
                   origin + ' = PORIGIN 0 pcpath_shift_control_' + str(index),
                   '$origin_child((' + origin + '), [PCFIELD 0, PCFIELD 0]) = (' + binary + ')']
        if name in INTEGERS:
            symbol, left, right, result = INTEGERS[name]
            helper = 'long_shl' if symbol == '<<' else 'long_shr'
            scalars = ('PINT ' + term(left), 'PINT ' + term(right), str(left), str(right), result)
            checks += ['$compiled_read(' + state + ', ' + binary + ') = (PINT ' + term(result) + ')',
                       '$' + helper + '(' + term(left) + ', ' + term(right) + ') = IRESULT ' + term(result),
                       '$compiled_special_concat_bytes(' + state + ', ' + binary + ') = ($ptascii(' + json.dumps(str(result)) + '))',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = ($ptascii(' + json.dumps(str(result) + 'x') + '))',
                       '$compiled_string_value(' + state + ', ' + origin + ', PSTRING ($ptascii(' + json.dumps(str(result) + 'x') + '))) = PSTRING_CARRIER INTERNED_STRING ($ptascii(' + json.dumps(str(result) + 'x') + '))']
        else:
            scalars = numeric.get(name)
            if name == 'same-result-spaceship':
                checks += ['$compiled_special_concat_bytes(' + state + ', ' + binary + ') = ($ptascii("0"))',
                           '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = ($ptascii("0x"))',
                           '$compiled_string_value(' + state + ', ' + origin + ', PSTRING ($ptascii("0x"))) = PSTRING_CARRIER INTERNED_STRING ($ptascii("0x"))']
            else:
                checks += ['$compiled_special_concat_bytes(' + state + ', ' + binary + ') = eps',
                           '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
            checks += ['$compiled_read(' + state + ', ' + binary + ') = ' + ('(PINT ' + term(scalars[4]) + ')' if scalars else 'eps')]
            if name.startswith('negative-count-'):
                helper = 'long_shl' if name.endswith('left') else 'long_shr'
                checks += ['$' + helper + '(1, $(-1)) = NEGSHIFT']
        if scalars:
            for field, value, text in ((0, scalars[0], scalars[2]), (1, scalars[1], scalars[3])):
                child = binary + '_' + str(field)
                checks += ['$origin_child((' + binary + '), [PCFIELD ' + str(field) + ']) = (' + child + ')',
                           '$compiled_read(' + state + ', ' + child + ') = (' + value + ')',
                           '$compiled_precision(' + state + ', (' + child + ')) = (14)',
                           '$compiled_special_concat_bytes(' + state + ', ' + child + ') = ($ptascii(' + json.dumps(text) + '))']
        if name == 'left-basic':
            for field, number, bits in ((0, 6, 4618441417868443648), (1, 1, 4607182418800017408)):
                changed, child = state + '_float_' + str(field), binary + '_' + str(field)
                checks += [changed + ' = ' + state + '[.POOLS = $special_review_pools(' + state + '.POOLS, ' + child + ', (PFLOAT ' + str(bits) + '))]',
                           '$compiled_read(' + changed + ', ' + child + ') = (PFLOAT ' + str(bits) + ')',
                           '$compiled_special_concat_bytes(' + changed + ', ' + child + ') = ($ptascii(' + json.dumps(str(number)) + '))',
                           '$compiled_read(' + changed + ', ' + binary + ') = (PINT 12)',
                           '$float_long(' + str(bits) + ', true) = (' + str(number) + ', eps)',
                           '$compiled_special_concat_bytes(' + changed + ', ' + binary + ') = eps']
        if name == 'left-width':
            for label, field, number in (('below-left', 0, MINIMUM - 1), ('above-left', 0, MAXIMUM + 1), ('above-count', 1, MAXIMUM + 1)):
                changed, child = state + '_range_' + label.replace('-', '_'), binary + '_' + str(field)
                left, right = (number, 64) if field == 0 else (1, number)
                checks += [changed + ' = ' + state + '[.POOLS = $special_review_pools(' + state + '.POOLS, ' + child + ', (PINT ' + term(number) + '))]',
                           '$compiled_read(' + changed + ', ' + child + ') = (PINT ' + term(number) + ')',
                           '$compiled_read(' + changed + ', ' + binary + ') = (PINT 0)',
                           '$compiled_special_concat_bytes(' + changed + ', ' + child + ') = ($ptascii(' + json.dumps('1' if field == 0 else '64') + '))',
                           '~$long_range(' + term(number) + ')',
                           '$long_shl(' + term(left) + ', ' + term(right) + ') = IRESULT 0',
                           '$compiled_special_concat_bytes(' + changed + ', ' + binary + ') = eps']
            changed, child = state + '_negative', binary + '_1'
            checks += [changed + ' = ' + state + '[.POOLS = $special_review_pools(' + state + '.POOLS, ' + child + ', (PINT $(-1)))]',
                       '$compiled_read(' + changed + ', ' + child + ') = (PINT $(-1))',
                       '$compiled_special_concat_bytes(' + changed + ', ' + child + ') = ($ptascii("64"))',
                       '$compiled_read(' + changed + ', ' + binary + ') = (PINT 0)',
                       '$long_shl(1, $(-1)) = NEGSHIFT',
                       '$compiled_special_concat_bytes(' + changed + ', ' + binary + ') = eps']
    return checks


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    watched = [Path(module.__file__) for module in (source, source.prior, source.prior.prior, source.arithmetic, source.bitnot, source.identity, prior, prior.source, prior.prior, prior.strings, runner)] + [Path(__file__)]
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
    report['scope'] = 'Four authentic-source-seeded shift fixtures add own-result/type, missing/typed child reads, value-changing reads where observable, both child sources and all precision refusals. Compiler tables cover both directions, count0/63/64/65/MAX, signed wrap and arithmetic right extension. Per-side quiet floats, invalid left ranges and positive count beyond signed64 preserve known results but remain refused; cached0 with negative count refuses via NEGSHIFT. Count64 annihilates valid left-value differences, so no independent value-coherence refusal or result-range isolation is claimed. Negative/error/coercion controls carry zero source credit and do not validate runtime error paths. The former exact-PINT spaceship refusal now checks decimal zero admission. Two promoted historical controls retain their separate reports; native4 are reused once and prior owner/throw/bounds/budget laws remain.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
