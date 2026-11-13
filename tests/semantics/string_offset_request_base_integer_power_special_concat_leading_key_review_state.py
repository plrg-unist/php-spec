#!/usr/bin/env python3
"""Independent integer-power results, signed bounds and conversion refusals."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_integer_power_special_concat_leading_key_cases as cases
import string_offset_request_base_integer_power_special_concat_leading_key_protocol as source
import string_offset_request_base_bool_null_unary_special_concat_leading_key_review_state as prior

runner = prior.runner
MINIMUM, MAXIMUM = -9223372036854775808, 9223372036854775807
INTEGERS = {
    'zero-zero': (0, 0, 1), 'zero-positive': (0, 1, 0), 'one-zero': (1, 0, 1),
    'two-zero': (2, 0, 1), 'two-one': (2, 1, 2), 'two-square': (2, 2, 4),
    'negative-odd': (-2, 3, -8), 'negative-even': (-2, 4, 16),
    'largest-power': (2, 62, 4611686018427387904), 'minimum-power': (-2, 63, MINIMUM),
    'maximum-identity': (MAXIMUM, 1, MAXIMUM), 'minimum-identity': (MINIMUM, 1, MINIMUM),
    'one-huge': (1, MAXIMUM, 1), 'minus-one-huge': (-1, MAXIMUM, -1),
    'zero-huge': (0, MAXIMUM, 0)}


def term(number):
    return str(number) if number >= 0 else '$(' + str(number) + ')'


def integer_source(number):
    return '((0 - 9223372036854775807) - 1)' if number == MINIMUM else '(' + str(number) + ')'


CONTROLS = {name: ("<?php $x = ((" + integer_source(left) + ' ** ' + integer_source(right) + ") . null) . 'x';\n").encode()
            for name, (left, right, result) in INTEGERS.items()} | {
    'negative-exponent': b"<?php $x = ((2 ** (0 - 1)) . null) . 'x';\n",
    'zero-negative': b"<?php $x = ((0 ** (0 - 1)) . null) . 'x';\n",
    'overflow-power': b"<?php $x = ((2 ** 63) . null) . 'x';\n",
    'float-base': b"<?php $x = ((2.0 ** 2) . null) . 'x';\n",
    'float-exponent': b"<?php $x = ((2 ** 2.0) . null) . 'x';\n",
    'numeric-string': b"<?php $x = (('2' ** 2) . null) . 'x';\n",
    'boolean-base': b"<?php $x = ((true ** 2) . null) . 'x';\n",
    'null-base': b"<?php $x = ((null ** 2) . null) . 'x';\n",
    'array-base': b"<?php $x = (([] ** 2) . null) . 'x';\n",
    'fractional-base': b"<?php $x = ((2.5 ** 2) . null) . 'x';\n"}


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    tag = ('power_root', 'power_root_l', 'power_root_l', 'power_root_child')[index]
    origin, expression = 'porigin_' + tag, 'expression_' + tag
    guards = [origin + ' = PORIGIN n_power pcpath_power',
              origin + '_l = PORIGIN n_power pcpath_power_l',
              origin + '_r = PORIGIN n_power pcpath_power_r']
    for suffix, value in (('drop', 'eps'), ('wrong', '(PINT 99)'), ('type', '(PFLOAT 0)')):
        state = 'S_power_' + suffix
        guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + origin + ', ' + value + ')]',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps',
                   '$string_read_request_base_saved(' + state + ', pstringread) = eps']
    mutants = (('PFLOAT 0', 'PINT 1'), ('PINT 0', 'PINT 0'),
               ('PINT 1', 'PINT 0'), ('PINT 3', 'PINT 1'))[index]
    for suffix, value in zip(('_l', '_r'), mutants):
        child = origin + suffix
        for operation, replacement in (('drop', 'eps'), ('wrong', '(' + value + ')')):
            state = 'S_power_child' + suffix + '_' + operation
            guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + child + ', ' + replacement + ')]',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps',
                       '$string_read_request_base_saved(' + state + ', pstringread) = eps']
        state = 'S_power_precision' + suffix
        guards += [state + ' = S_after[.POOLS = $float_review_precision(S_after.POOLS, ' + child + ', 17)]',
                   '$compiled_precision(' + state + ', (' + origin + ')) = (14)',
                   '$compiled_precision(' + state + ', (' + child + ')) = (17)',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
        left = 'expression_power_other' if suffix == '_l' else expression + '_l'
        right = 'expression_power_other' if suffix == '_r' else expression + '_r'
        if suffix == '_l':
            guards += ['expression_power_other = NExprVariable (BYTES "dW5hdXRo") metadata_' + tag]
        state = 'S_power_source' + suffix
        guards += [state + ' = S_after[.SOURCES = [{ID n_power, AST (PROGRAM eps), OCCURRENCES ([(PCOCCURRENCE pcpath_power ' + expression + '), (PCOCCURRENCE pcpath_power_l ' + left + '), (PCOCCURRENCE pcpath_power_r ' + right + ')])}]]',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
    guards += ['S_power_precision = S_after[.POOLS = $float_review_precision(S_after.POOLS, ' + origin + ', 17)]',
               '$compiled_precision(S_power_precision, (' + origin + ')) = (17)',
               '$compiled_precision(S_power_precision, (' + origin + '_l)) = (14)',
               '$compiled_precision(S_power_precision, (' + origin + '_r)) = (14)',
               '$compiled_special_concat_bytes(S_power_precision, ' + origin + ') = eps']
    guards += prior.unary_guards([], ('1x', '-1x', '0x', '-4x')[index])
    return checks + guards, derived + len(guards)


def compiler_conditions(checked, paths):
    checks = []
    scalar_cases = {
        'negative-exponent': ('PINT 2', 'PINT $(-1)', '2', '-1', 'PFLOAT 4602678819172646912'),
        'zero-negative': ('PINT 0', 'PINT $(-1)', '0', '-1', None),
        'overflow-power': ('PINT 2', 'PINT 63', '2', '63', 'PFLOAT 4890909195324358656'),
        'float-base': ('PFLOAT 4611686018427387904', 'PINT 2', '2', '2', 'PFLOAT 4616189618054758400'),
        'float-exponent': ('PINT 2', 'PFLOAT 4611686018427387904', '2', '2', 'PFLOAT 4616189618054758400'),
        'numeric-string': ('PSTRING ($ptascii("2"))', 'PINT 2', '2', '2', 'PINT 4'),
        'boolean-base': ('PBOOL true', 'PINT 2', '1', '2', 'PINT 1'),
        'null-base': ('PNULL', 'PINT 2', '', '2', 'PINT 0'),
        'fractional-base': ('PFLOAT 4612811918334230528', 'PINT 2', '2.5', '2', 'PFLOAT 4618722892845154304')}
    for index, name in enumerate(CONTROLS):
        state, origin = 'S_power_control_' + str(index), 'porigin_power_control_' + str(index)
        binary = origin + '_binary'
        checks += [state + ' = $php_run(' + checked[name]['fixture'] + ', 0, ' + json.dumps(base64.b64encode(bytes(paths[name])).decode()) + ')',
                   state + '.COMPLETION = BUDGET',
                   '$special_review_concat_path(' + state + '.SOURCES[0].OCCURRENCES) = (pcpath_power_control_' + str(index) + ')',
                   origin + ' = PORIGIN 0 pcpath_power_control_' + str(index),
                   '$origin_child((' + origin + '), [PCFIELD 0, PCFIELD 0]) = (' + binary + ')']
        if name in INTEGERS:
            left, right, result = INTEGERS[name]
            scalars = 'PINT ' + term(left), 'PINT ' + term(right), str(left), str(right), 'PINT ' + term(result)
            checks += ['$compiled_read(' + state + ', ' + binary + ') = (PINT ' + term(result) + ')',
                       '$power_prepare(NINT ' + term(left) + ', NINT ' + term(right) + ') = POWERDONE (NINT ' + term(result) + ') false',
                       '$compiled_special_concat_bytes(' + state + ', ' + binary + ') = ($ptascii(' + json.dumps(str(result)) + '))',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = ($ptascii(' + json.dumps(str(result) + 'x') + '))',
                       '$compiled_string_value(' + state + ', ' + origin + ', PSTRING ($ptascii(' + json.dumps(str(result) + 'x') + '))) = PSTRING_CARRIER INTERNED_STRING ($ptascii(' + json.dumps(str(result) + 'x') + '))']
        else:
            scalars = scalar_cases.get(name)
            checks += ['$compiled_read(' + state + ', ' + binary + ') = ' + ('(' + scalars[4] + ')' if scalars and scalars[4] else 'eps')]
            if name in ('overflow-power', 'numeric-string', 'boolean-base', 'null-base'):
                text = {'overflow-power': '9.2233720368548E+18', 'numeric-string': '4', 'boolean-base': '1', 'null-base': '0'}[name]
                if name == 'overflow-power':
                    checks += ['$power_prepare(NINT 2, NINT 63) = POWERDONE (NFLOAT 4890909195324358656) false']
                else:
                    left = {'numeric-string': 2, 'boolean-base': 1, 'null-base': 0}[name]
                    checks += ['$power_prepare(NINT ' + str(left) + ', NINT 2) = POWERDONE (NINT ' + text + ') false']
                checks += ['$compiled_special_concat_bytes(' + state + ', ' + binary + ') = ($ptascii(' + json.dumps(text) + '))',
                           '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = ($ptascii(' + json.dumps(text + 'x') + '))',
                           '$compiled_string_value(' + state + ', ' + origin + ', PSTRING ($ptascii(' + json.dumps(text + 'x') + '))) = PSTRING_CARRIER INTERNED_STRING ($ptascii(' + json.dumps(text + 'x') + '))']
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
        if name == 'two-square':
            for field in (0, 1):
                changed, child = state + '_string_' + str(field), binary + '_' + str(field)
                checks += [changed + ' = ' + state + '[.POOLS = $special_review_pools(' + state + '.POOLS, ' + child + ', (PSTRING ($ptascii("2"))))]',
                           '$compiled_read(' + changed + ', ' + child + ') = (PSTRING ($ptascii("2")))',
                           '$compiled_special_concat_bytes(' + changed + ', ' + child + ') = ($ptascii("2"))',
                           '$compiled_read(' + changed + ', ' + binary + ') = (PINT 4)',
                           '$coerce_number(PSTRING ($ptascii("2"))) = COERCED (NINT 2) false',
                           '$compiled_identity_value(' + changed + ', ' + child + ') = (PSTRING ($ptascii("2")))',
                           '$compiled_special_concat_bytes(' + changed + ', ' + binary + ') = ($ptascii("4"))',
                           '$compiled_special_concat_bytes(' + changed + ', ' + origin + ') = ($ptascii("4x"))',
                           '$compiled_string_value(' + changed + ', ' + origin + ', PSTRING ($ptascii("4x"))) = PSTRING_CARRIER INTERNED_STRING ($ptascii("4x"))']
        ranges = [('base-below', 0, MINIMUM - 1), ('base-above', 0, MAXIMUM + 1)] if name == 'zero-zero' else [('exponent-above', 1, MAXIMUM + 1)] if name == 'zero-positive' else []
        for label, field, number in ranges:
            changed, child = state + '_range_' + label.replace('-', '_'), binary + '_' + str(field)
            left, right, result = INTEGERS[name]
            actual = left if field == 0 else right
            left, right = (number, right) if field == 0 else (left, number)
            checks += [changed + ' = ' + state + '[.POOLS = $special_review_pools(' + state + '.POOLS, ' + child + ', (PINT ' + term(number) + '))]',
                       '$compiled_read(' + changed + ', ' + child + ') = (PINT ' + term(number) + ')',
                       '$compiled_special_concat_bytes(' + changed + ', ' + child + ') = ($ptascii(' + json.dumps(str(actual)) + '))',
                       '$compiled_read(' + changed + ', ' + binary + ') = (PINT ' + term(result) + ')',
                       '~$long_range(' + term(number) + ')',
                       '$power_prepare(NINT ' + term(left) + ', NINT ' + term(right) + ') = POWERDONE (NINT ' + term(result) + ') false',
                       '$compiled_special_concat_bytes(' + changed + ', ' + binary + ') = eps']
        if name == 'zero-positive':
            changed, child = state + '_negative', binary + '_1'
            checks += [changed + ' = ' + state + '[.POOLS = $special_review_pools(' + state + '.POOLS, ' + child + ', (PINT $(-1)))]',
                       '$compiled_read(' + changed + ', ' + child + ') = (PINT $(-1))',
                       '$compiled_special_concat_bytes(' + changed + ', ' + child + ') = ($ptascii("1"))',
                       '$compiled_read(' + changed + ', ' + binary + ') = (PINT 0)',
                       '$power_prepare(NINT 0, NINT $(-1)) = POWERDONE (NFLOAT 9218868437227405312) true',
                       '$compiled_special_concat_bytes(' + changed + ', ' + binary + ') = eps']
    return checks


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    watched = [Path(module.__file__) for module in (source, source.prior, source.prior.prior, source.shift, source.arithmetic, source.unary, source.integers, prior, prior.source, prior.prior, prior.strings, runner)] + [Path(__file__)]
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
    report['scope'] = 'Four authentic-source-seeded integer-power fixtures add own-result/type, missing/typed or outcome-changing child reads, both child sources and three precision refusals. Zero exponent annihilates valid base-value changes, so no independent base-value rejection is claimed there. Compiler integer tables include0**0, signed parity, signed endpoints and huge exponents on0/1/minus1, with negative-exponent, float/array refusals. The separate completed-FLOAT BYTE slice promotes only the overflow-power selector; its fresh affected check does not renew the earlier full campaign. The separate coerced-PINT slice also promotes numeric-string/boolean-base/null-base and the two-square raw-string pool mutations. Those mutations retain literal byte authority and generic integer results; the old strict-PINT arm still refuses them while the new arm certifies their exact quiet result. Only fresh affected compiler checks are credited, with the authentic state recipes unchanged. Base ranges at exponent0 and positive exponent aboveMAX at base0 preserve own results but refuse; no independent result-range or nonnegative-versus-integer-plan conjunct isolation is claimed. A cached0 with negative exponent sees a floating warning plan and refuses. Compiler/derived checks are source0 and do not validate new runtime deprecation, conversion, error, libm or ownership routes. The historical power selector is promoted separately; native4 are reused once, author recipes stay exact prefixes, and owners/supplied throw/fixed bounds/budgets retain existing laws.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
