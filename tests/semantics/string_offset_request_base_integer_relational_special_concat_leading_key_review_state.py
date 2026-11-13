#!/usr/bin/env python3
"""Independent integer relational order, type, range and certificate checks."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_integer_relational_special_concat_leading_key_cases as cases
import string_offset_request_base_integer_relational_special_concat_leading_key_protocol as source
import string_offset_request_base_bool_null_unary_special_concat_leading_key_review_state as prior

runner = prior.runner
OPERATORS = {'less': ('<', lambda left, right: left < right),
             'lessequal': ('<=', lambda left, right: left <= right),
             'greater': ('>', lambda left, right: left > right),
             'greaterequal': ('>=', lambda left, right: left >= right)}
ORDER_CASES = {name + '-' + str(index): (symbol, left, 0, compare(left, 0))
               for name, (symbol, compare) in OPERATORS.items() for index, left in enumerate((-1, 0, 1))}
CONTROLS = {name: ("<?php $x = ((" + str(left) + ' ' + symbol + " 0) . null) . 'x';\n").encode()
            for name, (symbol, left, right, result) in ORDER_CASES.items()} | {
    'float-left': b"<?php $x = ((0.0 < 1) . null) . 'x';\n",
    'float-right': b"<?php $x = ((0 < 1.0) . null) . 'x';\n",
    'string-left': b"<?php $x = (('0' < 1) . null) . 'x';\n",
    'boolean-right': b"<?php $x = ((0 < true) . null) . 'x';\n",
    'null-left': b"<?php $x = ((null < 1) . null) . 'x';\n",
    'array-left': b"<?php $x = (([] < 1) . null) . 'x';\n",
    'loose-equal': b"<?php $x = ((0 == 0) . null) . 'x';\n",
    'spaceship': b"<?php $x = ((0 <=> 1) . null) . 'x';\n"}


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    tag = ('relational_root', 'relational_root_child', 'relational_root_l', 'relational_root_child_l')[index]
    origin, expression = 'porigin_' + tag, 'expression_' + tag
    guards = [origin + ' = PORIGIN n_relational pcpath_relational',
              origin + '_l = PORIGIN n_relational pcpath_relational_l',
              origin + '_r = PORIGIN n_relational pcpath_relational_r']
    wrong = 'PBOOL true' if index == 2 else 'PBOOL false'
    for suffix, value in (('drop', 'eps'), ('wrong', '(' + wrong + ')'), ('type', '(PINT 1)')):
        state = 'S_relational_' + suffix
        guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + origin + ', ' + value + ')]',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps',
                   '$string_read_request_base_saved(' + state + ', pstringread) = eps']
    mutants = (('9223372036854775807', '$(-9223372036854775808)'), ('3', '1'), ('3', '0'), ('0', '3'))[index]
    for suffix, value in zip(('_l', '_r'), mutants):
        child = origin + suffix
        for operation, replacement in (('drop', 'eps'), ('wrong', '(PINT ' + value + ')')):
            state = 'S_relational_child' + suffix + '_' + operation
            guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + child + ', ' + replacement + ')]',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps',
                       '$string_read_request_base_saved(' + state + ', pstringread) = eps']
        state = 'S_relational_precision' + suffix
        guards += [state + ' = S_after[.POOLS = $float_review_precision(S_after.POOLS, ' + child + ', 17)]',
                   '$compiled_precision(' + state + ', (' + origin + ')) = (14)',
                   '$compiled_precision(' + state + ', (' + child + ')) = (17)',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
        left = 'expression_relational_other' if suffix == '_l' else expression + '_l'
        right = 'expression_relational_other' if suffix == '_r' else expression + '_r'
        state = 'S_relational_source' + suffix
        if suffix == '_l':
            guards += ['expression_relational_other = NExprVariable (BYTES "dW5hdXRo") metadata_' + tag]
        guards += [state + ' = S_after[.SOURCES = [{ID n_relational, AST (PROGRAM eps), OCCURRENCES ([(PCOCCURRENCE pcpath_relational ' + expression + '), (PCOCCURRENCE pcpath_relational_l ' + left + '), (PCOCCURRENCE pcpath_relational_r ' + right + ')])}]]',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
    guards += ['S_relational_precision = S_after[.POOLS = $float_review_precision(S_after.POOLS, ' + origin + ', 17)]',
               '$compiled_precision(S_relational_precision, (' + origin + ')) = (17)',
               '$compiled_precision(S_relational_precision, (' + origin + '_l)) = (14)',
               '$compiled_precision(S_relational_precision, (' + origin + '_r)) = (14)',
               '$compiled_special_concat_bytes(S_relational_precision, ' + origin + ') = eps']
    if index in (2, 3):
        suffix, operation = ('_l', 'GREATER') if index == 2 else ('_r', 'GREATEREQUAL')
        child = origin + suffix
        result = 'false' if index == 2 else 'true'
        for number, value in enumerate(('PFLOAT 4607182418800017408', 'PSTRING ($ptascii("1"))', 'PBOOL true', 'PINT $(-9223372036854775809)')):
            state = 'S_relational_scalar_' + str(number)
            left, right = (value, 'PINT 2') if index == 2 else ('PINT 2', value)
            guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + child + ', (' + value + '))]',
                       '$compiled_read(' + state + ', ' + child + ') = (' + value + ')',
                       '$compiled_special_concat_bytes(' + state + ', ' + child + ') = ($ptascii("1"))',
                       '$compiled_read(' + state + ', ' + origin + ') = (PBOOL ' + result + ')']
            if number < 3:
                guards += ['$binary_apply(' + state + ', ' + operation + ', ' + left + ', ' + right + ', 0) = ' + state + '[.RESULT = KNOWN (PBOOL ' + result + ')]']
            else:
                guards += ['~$long_range($(-9223372036854775809))',
                           '$comparison_value(' + operation + ', $compare_int(' + (right + ', ' + left).replace('PINT ', '') + ')) = PBOOL ' + result]
            if number == 0:
                guards += ['$compiled_special_concat_bytes(' + state + ', ' + origin + ') = ($ptascii(' + json.dumps('1' if result == 'true' else '') + '))']
            else:
                guards += ['$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
    if index == 2:
        guards += ['expression_relational_opcode = NExprBinaryOpEqual ' + expression + '_l ' + expression + '_r metadata_' + tag,
                   'S_relational_opcode = S_after[.SOURCES = [{ID n_relational, AST (PROGRAM eps), OCCURRENCES ([(PCOCCURRENCE pcpath_relational expression_relational_opcode), (PCOCCURRENCE pcpath_relational_l ' + expression + '_l), (PCOCCURRENCE pcpath_relational_r ' + expression + '_r)])}]]',
                   '$compiled_read(S_relational_opcode, ' + origin + ') = (PBOOL false)',
                   '$compiled_special_concat_bytes(S_relational_opcode, ' + origin + '_l) = ($ptascii("1"))',
                   '$compiled_special_concat_bytes(S_relational_opcode, ' + origin + '_r) = ($ptascii("2"))',
                   '$binary_apply(S_relational_opcode, EQUAL, PINT 1, PINT 2, 0) = S_relational_opcode[.RESULT = KNOWN (PBOOL false)]',
                   '$compiled_special_concat_bytes(S_relational_opcode, ' + origin + ') = ($ptascii(""))']
    guards += prior.unary_guards([], ('1x', '-1x', '0x', '-4x')[index])
    return checks + guards, derived + len(guards)


def compiler_conditions(checked, paths):
    checks = []
    scalar_cases = {'float-left': ('PFLOAT 0', 'PINT 1', '0', '1'),
                    'float-right': ('PINT 0', 'PFLOAT 4607182418800017408', '0', '1'),
                    'string-left': ('PSTRING ($ptascii("0"))', 'PINT 1', '0', '1'),
                    'boolean-right': ('PINT 0', 'PBOOL true', '0', '1'),
                    'null-left': ('PNULL', 'PINT 1', '', '1')}
    for index, name in enumerate(CONTROLS):
        state, origin = 'S_relational_control_' + str(index), 'porigin_relational_control_' + str(index)
        binary = origin + '_binary'
        checks += [state + ' = $php_run(' + checked[name]['fixture'] + ', 0, ' + json.dumps(base64.b64encode(bytes(paths[name])).decode()) + ')',
                   state + '.COMPLETION = BUDGET',
                   '$special_review_concat_path(' + state + '.SOURCES[0].OCCURRENCES) = (pcpath_relational_control_' + str(index) + ')',
                   origin + ' = PORIGIN 0 pcpath_relational_control_' + str(index),
                   '$origin_child((' + origin + '), [PCFIELD 0, PCFIELD 0]) = (' + binary + ')']
        if name in ORDER_CASES:
            symbol, left, right, result = ORDER_CASES[name]
            value, text = ('PBOOL true', '1') if result else ('PBOOL false', '')
            term = str(left) if left >= 0 else '$(' + str(left) + ')'
            scalars = ('PINT ' + term, 'PINT 0', str(left), '0')
            checks += ['$compiled_read(' + state + ', ' + binary + ') = (' + value + ')',
                       '$compiled_special_concat_bytes(' + state + ', ' + binary + ') = ($ptascii(' + json.dumps(text) + '))',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = ($ptascii(' + json.dumps(text + 'x') + '))',
                       '$compiled_string_value(' + state + ', ' + origin + ', PSTRING ($ptascii(' + json.dumps(text + 'x') + '))) = PSTRING_CARRIER INTERNED_STRING ($ptascii(' + json.dumps(text + 'x') + '))']
        else:
            scalars = scalar_cases.get(name)
            value = 'PINT $(-1)' if name == 'spaceship' else 'PBOOL false' if name == 'array-left' else 'PBOOL true'
            checks += ['$compiled_read(' + state + ', ' + binary + ') = (' + value + ')']
            if name in ('loose-equal', 'spaceship', 'float-left', 'float-right'):
                text = '-1' if name == 'spaceship' else '1'
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
    report['scope'] = 'Four authentic-source-seeded integer relational fixtures add own-result/type, both child read/source and three precision refusals. Both literal-child sides preserve correct generic comparison results and byte certificates while string/bool and out-of-range PINT pools retain type/range refusals. The two per-side quiet-float mutations now check reviewed numeric comparison admission. The same-result exact-PINT EQUAL source now certifies Boolean false as empty bytes. Compiler controls distinguish less/equal/greater integer orders for all four operators, including greater argument reversal, from float/string/bool/null/array refusals. Former exact-PINT EQUAL and SPACESHIP refusals retain reviewed integer admission; the two float comparison selectors now check typed numeric admission. Native4 are reused once; owners, supplied throw, fixed bounds and budgets retain their laws. Derived/compiler conditions carry zero source credit.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
