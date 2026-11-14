#!/usr/bin/env python3
"""Independent strict-integer runtime source, type and boundary controls."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import source_occurrences as occurrences
import string_offset_request_base_float_boolnot_special_concat_leading_key_review_state as prior
import string_offset_request_base_runtime_integer_binary_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_integer_binary_special_concat_leading_key_protocol as source

runner = source.runner
OPERATORS = {'MODULO', 'BITAND', 'BITOR', 'BITXOR', 'SHIFTLEFT', 'SHIFTRIGHT'}
RESULTS = (1, -1, 0, -4)
CONTROLS = []


def integer(value):
    return '$(' + str(value) + ')' if value < 0 else str(value)


def operators(tree, tag='operator'):
    if tree[0] == 'FLOAT':
        return
    if tree[0] in OPERATORS:
        yield tag
    binary = tree[0] in OPERATORS | {'ADD', 'SUBTRACT', 'MULTIPLY'}
    for index, child in enumerate(tree[1:3] if binary else tree[1:2]):
        yield from operators(child, tag + '_' + str(index))


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    guards = ['pcode_peer_integer = S_after.CODE[0]', 'pcode_peer_integer.UNIT = 0',
              'ppool_peer_integer = S_after.POOLS[0]', 'ppool_peer_integer.UNIT = 0',
              'pcunit_peer_integer = S_after.SOURCES[0]', 'pcunit_peer_integer.ID = 0']
    for tag in ('key', 'runtime_concat', *operators(source.TREES[index])):
        origin, target = 'porigin_' + tag, 'pcpath_peer_' + tag
        guards.append(origin + ' = PORIGIN 0 ' + target)
        mutations = (
            ('drop', 'S_after[.CODE[0] = pcode_peer_integer[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_integer.EXPRESSIONS, ' + target + ', eps)]]'),
            ('fold', 'S_after[.CODE[0] = pcode_peer_integer[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_integer.EXPRESSIONS, ' + target + ', (true))]]'),
            ('precision', 'S_after[.POOLS[0] = ppool_peer_integer[.CONSTANTS = (PCCPRECISION ' + target + ' 17) :: ppool_peer_integer.CONSTANTS]]'),
            ('source', 'S_after[.SOURCES[0] = pcunit_peer_integer[.OCCURRENCES = (PCOCCURRENCE ' + target + ' (NExprVariable (BYTES "dW5hdXRo") eps)) :: pcunit_peer_integer.OCCURRENCES]]'),
        )
        for label, value in mutations:
            state = 'S_peer_' + tag + '_' + label
            guards += [state + ' = ' + value,
                       '$string_read_runtime_value(' + state + ', porigin_operator) = ' +
                       ('(PINT ' + integer(RESULTS[index]) + ')' if tag in ('key', 'runtime_concat') else 'eps'),
                       '$string_read_runtime_bytes(' + state + ', porigin_key) = eps',
                       '$string_read_request_base_saved(' + state + ', pstringread) = eps']
        if tag in ('key', 'runtime_concat'):
            continue
        for child_index in (0, 1):
            child, child_path = origin + '_peer_child_' + str(child_index), target + '_child_' + str(child_index)
            state = 'S_peer_' + tag + '_child_precision_' + str(child_index)
            guards += ['$origin_child((' + origin + '), [PCFIELD ' + str(child_index) + ']) = (' + child + ')',
                       child + ' = PORIGIN 0 ' + child_path,
                       state + ' = S_after[.POOLS[0] = ppool_peer_integer[.CONSTANTS = (PCCPRECISION ' + child_path + ' 17) :: ppool_peer_integer.CONSTANTS]]',
                       '$compiled_precision(' + state + ', (' + child + ')) = (17)',
                       '$string_read_runtime_value(' + state + ', ' + origin + ') = eps',
                       '$string_read_runtime_bytes(' + state + ', porigin_key) = eps']
    guards += ['S_peer_integer_budget = S_after[.COMPLETION = BUDGET][.RESULT = KNOWN (PINT 99)]',
               '$string_read_runtime_value(S_peer_integer_budget, porigin_operator) = (PINT ' + integer(RESULTS[index]) + ')',
               '$string_read_runtime_bytes(S_peer_integer_budget, porigin_key) = ($ptascii(' + json.dumps(str(RESULTS[index]) + 'x') + '))']
    if index == 0:
        for number, control in enumerate(CONTROLS):
            name, fixture, path, target, node, result, op, left, right = control
            state, origin = 'S_peer_boundary_' + str(number), 'porigin_peer_boundary_' + str(number)
            guards += [state + ' = $php_run(' + fixture + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
                       state + '.COMPLETION = BUDGET', origin + ' = PORIGIN 0 ' + occurrences.path_term(target),
                       '$origin_node(' + state + '.SOURCES, ' + origin + ') = (' + occurrences.node_term(node) + ')',
                       origin + ' = PORIGIN 0 pcpath_peer_boundary_' + str(number),
                       '$code_at(' + state + '.CODE, 0) = (pcode_peer_boundary_' + str(number) + ')',
                       '$code_expression(pcode_peer_boundary_' + str(number) + '.EXPRESSIONS, pcpath_peer_boundary_' + str(number) + ') = ((1, false))',
                       '$compiled_read(' + state + ', ' + origin + ') = eps',
                       '$compiled_precision(' + state + ', (' + origin + ')) = (14)',
                       '$origin_child((' + origin + '), [PCFIELD 1]) = (' + origin + '_right)']
            expected = 'eps' if result is None else '(PINT ' + integer(result) + ')'
            guards += ['$string_read_runtime_value(' + state + ', ' + origin + ') = ' + expected,
                       '$string_read_runtime_bytes(' + state + ', ' + origin + ') = ' +
                       ('eps' if result is None else '($ptascii(' + json.dumps(str(result)) + '))')]
            if name in ('bool', 'float', 'compiled'):
                value = {'bool': 'PBOOL true', 'float': 'PFLOAT 0', 'compiled': 'PINT 1'}[name]
                guards += ['$compiled_read(' + state + ', ' + origin + '_right) = ' +
                           ('(PINT 1)' if name == 'compiled' else '(PFLOAT 0)' if name == 'float' else 'eps'),
                           '$string_read_runtime_value(' + state + ', ' + origin + '_right) = ' +
                           ('eps' if name == 'compiled' else '(' + value + ')'),
                           '$integer_coerce(' + state + ', ' + value + ', 1) = ' + state + '[.RESULT = KNOWN (PINT ' + str(right) + ')]',
                           '$binary_apply(' + state + ', ' + op + ', PINT 1, ' + value + ', 1) = ' + state + '[.RESULT = KNOWN (PINT ' + str({'bool': 1, 'float': 1, 'compiled': 0}[name]) + ')]']
                if name == 'compiled':
                    guards += ['$compiled_identity_value(' + state + ', ' + origin + '_right) = (PINT 1)']
            if name == 'zero_mod':
                kernel = 'INTZERO'
            elif name.startswith('negative_'):
                kernel = 'NEGSHIFT'
            else:
                kernel = 'IRESULT ' + integer(result if result is not None else {'bool': 1, 'float': 1, 'compiled': 0}[name])
            guards += ['$integer_binary(' + op + ', ' + integer(left) + ', ' + integer(right) + ') = ' + kernel]
            if result is not None:
                budget = state + '_result99'
                guards += [budget + ' = ' + state + '[.RESULT = KNOWN (PINT 99)]',
                           '$binary_apply(' + budget + ', ' + op + ', PINT ' + integer(left) + ', PINT ' + integer(right) + ', 1) = ' + budget + '[.RESULT = KNOWN (PINT ' + integer(result) + ')]',
                           '$string_read_runtime_value(' + budget + ', ' + origin + ') = ' + expected]
    return checks + guards, derived + len(guards)


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    prep = output.with_name(output.name + '-control-prep')
    prep.mkdir(parents=True)
    one, zero, negative = '(+(!0.0))', '(+(!INF))', '(-(!0.0))'
    two = '((!0.0)+(!0.0))'
    eight = '(' + two + '*(' + two + '*' + two + '))'
    count64 = '(' + eight + '*' + eight + ')'
    count63 = '(' + count64 + '-' + one + ')'
    minimum = '(' + one + ' << (+' + count63 + '))'
    raw = (
        ('bool', '(' + one + ' & (!0.0))', 'Expr_BinaryOp_BitwiseAnd', None, 'BITAND', 1, 1),
        ('float', '(' + one + ' | 0.0)', 'Expr_BinaryOp_BitwiseOr', None, 'BITOR', 1, 0),
        ('compiled', '(' + one + ' ^ 1)', 'Expr_BinaryOp_BitwiseXor', None, 'BITXOR', 1, 1),
        ('zero_mod', '(' + one + ' % ' + zero + ')', 'Expr_BinaryOp_Mod', None, 'MODULO', 1, 0),
        ('negative_left', '(' + one + ' << ' + negative + ')', 'Expr_BinaryOp_ShiftLeft', None, 'SHIFTLEFT', 1, -1),
        ('negative_right', '(' + one + ' >> ' + negative + ')', 'Expr_BinaryOp_ShiftRight', None, 'SHIFTRIGHT', 1, -1),
        ('count64_left', '(' + one + ' << (+' + count64 + '))', 'Expr_BinaryOp_ShiftLeft', 0, 'SHIFTLEFT', 1, 64),
        ('count64_right', '(' + negative + ' >> (+' + count64 + '))', 'Expr_BinaryOp_ShiftRight', -1, 'SHIFTRIGHT', -1, 64),
        ('signed_wrap', minimum, 'Expr_BinaryOp_ShiftLeft', -9223372036854775808, 'SHIFTLEFT', 1, 63),
        ('minimum_mod', '((+' + minimum + ') % ' + negative + ')', 'Expr_BinaryOp_Mod', 0, 'MODULO', -9223372036854775808, -1),
        ('wrapped_zero', '((+' + minimum + ') << ' + one + ')', 'Expr_BinaryOp_ShiftLeft', 0, 'SHIFTLEFT', -9223372036854775808, 1),
        ('signed_mod', '(' + negative + ' % (+' + two + '))', 'Expr_BinaryOp_Mod', -1, 'MODULO', -1, 2),
    )
    paths = {row[0]: prep / (row[0] + '.php') for row in raw}
    for name, expression, *_ in raw:
        paths[name].write_bytes(('<?php $x=' + expression + ';\n').encode())
    root = runner.ROOT
    profile = json.loads((root / 'tests/semantics/profile.json').read_bytes())
    flags = [part for key, value in profile.items() for part in ('-d', key + '=' + value)]
    frontend = runner.Worker([str(root / '.tools/php/bin/php'), '-n', *flags, '-d', 'extension=' + str(root / '.tools/php-file.so'), str(root / 'frontend/worker.php')], prep / 'frontend')
    try:
        parsed = {name: frontend.request({'op': 'parse', 'source': base64.b64encode(path.read_bytes()).decode()}) for name, path in paths.items()}
        assert all(row['accepted'] for row in parsed.values())
    finally:
        frontend.close()
    adapter = runner.Worker([str(root / '_build/default/adapter/main.exe'), str(root)], prep / 'adapter')
    try:
        checked = {name: adapter.request({'op': 'check', 'ast': row['ast'], 'fixture': True}) for name, row in parsed.items()}
        assert all(row['ok'] for row in checked.values())
    finally:
        adapter.close()
    for name, expression, kind, result, op, left, right in raw:
        targets = [(path, node) for index, statement in enumerate(parsed[name]['ast']['program'])
                   for path, node in occurrences.expected(statement, [('INDEX', index)]) if node['node'] == kind]
        target, node = min(targets, key=lambda item: len(item[0]))
        CONTROLS.append((name, checked[name]['fixture'], paths[name], target, node, result, op, left, right))
    watched = {Path(module.__file__).resolve() for module in tuple(sys.modules.values()) if getattr(module, '__file__', None)
               and Path(module.__file__).resolve().parent == Path(__file__).resolve().parent} | set(paths.values())
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.PREFIX += prior.HELPERS
    runner.cases, runner.OUTPUTS, runner.conditions = cases, tuple(cases.OUTPUTS.values()), conditions
    passed = runner.main()
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = ('Exact author prefixes plus independent emitted-source/CODE/read/precision and BUDGET RESULT99 controls for all six strict-PINT integer operators. Twelve genuine checked-source compiler states distinguish quiet BOOL/FLOAT and compiled-PINT leaf refusal, invalid MOD/shift refusal, count64, signed shift wrapping/saturation and MIN%-1. These add source0/native0; no387/compiler/schema/owner changes, broader coercions or accepted native/source replay.')
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
