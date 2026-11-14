#!/usr/bin/env python3
"""Independent exact-division source, result-type and stale-state controls."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import source_occurrences as occurrences
import string_offset_request_base_float_boolnot_special_concat_leading_key_review_state as prior
import string_offset_request_base_runtime_integer_division_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_integer_division_special_concat_leading_key_protocol as source

runner = source.runner
RESULTS = (1, -1, 0, -4)
CONTROLS = []


def integer(value):
    return '$(' + str(value) + ')' if value < 0 else str(value)


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    guards = ['pcode_peer_div = S_after.CODE[0]', 'pcode_peer_div.UNIT = 0',
              'ppool_peer_div = S_after.POOLS[0]', 'ppool_peer_div.UNIT = 0',
              'pcunit_peer_div = S_after.SOURCES[0]', 'pcunit_peer_div.ID = 0']
    for tag in ('key', 'runtime_concat', 'operator', 'operator_0', 'operator_1'):
        origin, target = 'porigin_' + tag, 'pcpath_peer_div_' + tag
        guards.append(origin + ' = PORIGIN 0 ' + target)
        mutations = (
            ('drop', 'S_after[.CODE[0] = pcode_peer_div[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_div.EXPRESSIONS, ' + target + ', eps)]]'),
            ('fold', 'S_after[.CODE[0] = pcode_peer_div[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_div.EXPRESSIONS, ' + target + ', (true))]]'),
            ('precision', 'S_after[.POOLS[0] = ppool_peer_div[.CONSTANTS = (PCCPRECISION ' + target + ' 17) :: ppool_peer_div.CONSTANTS]]'),
            ('source', 'S_after[.SOURCES[0] = pcunit_peer_div[.OCCURRENCES = (PCOCCURRENCE ' + target + ' (NExprVariable (BYTES "dW5hdXRo") eps)) :: pcunit_peer_div.OCCURRENCES]]'),
        )
        for label, value in mutations:
            state = 'S_peer_div_' + tag + '_' + label
            guards += [state + ' = ' + value,
                       '$string_read_runtime_value(' + state + ', porigin_operator) = ' +
                       ('(PINT ' + integer(RESULTS[index]) + ')' if tag in ('key', 'runtime_concat') else 'eps'),
                       '$string_read_runtime_bytes(' + state + ', porigin_key) = eps',
                       '$string_read_request_base_saved(' + state + ', pstringread) = eps']
    guards += ['S_peer_div_budget = S_after[.COMPLETION = BUDGET][.RESULT = KNOWN (PINT 99)]',
               '$string_read_runtime_value(S_peer_div_budget, porigin_operator) = (PINT ' + integer(RESULTS[index]) + ')',
               '$string_read_runtime_bytes(S_peer_div_budget, porigin_key) = ($ptascii(' + json.dumps(str(RESULTS[index]) + 'x') + '))']
    if index == 0:
        for number, control in enumerate(CONTROLS):
            name, fixture, path, target, node, result, left, right, left_number, right_number, kernel, output = control
            state, origin = 'S_peer_div_control_' + str(number), 'porigin_peer_div_control_' + str(number)
            actual_left = 'PSTRING_CARRIER INTERNED_STRING ($ptascii("1"))' if name == 'string' else left
            guards += [state + ' = $php_run(' + fixture + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
                       state + '.COMPLETION = BUDGET', origin + ' = PORIGIN 0 ' + occurrences.path_term(target),
                       '$origin_node(' + state + '.SOURCES, ' + origin + ') = (' + occurrences.node_term(node) + ')',
                       origin + ' = PORIGIN 0 pcpath_peer_div_control_' + str(number),
                       '$code_at(' + state + '.CODE, 0) = (pcode_peer_div_control_' + str(number) + ')',
                       '$code_expression(pcode_peer_div_control_' + str(number) + '.EXPRESSIONS, pcpath_peer_div_control_' + str(number) + ') = ((1, false))',
                       '$compiled_read(' + state + ', ' + origin + ') = eps',
                       '$compiled_precision(' + state + ', (' + origin + ')) = (14)',
                       '$coerce_number(' + actual_left + ') = COERCED (' + left_number + ') false',
                       '$coerce_number(' + right + ') = COERCED (' + right_number + ') false',
                       '$number_binary(DIVIDE, ' + left_number + ', ' + right_number + ') = ' + kernel,
                       '$string_read_runtime_value(' + state + ', ' + origin + ') = ' +
                       ('eps' if result is None else '(PINT ' + integer(result) + ')'),
                       '$string_read_runtime_bytes(' + state + ', ' + origin + ') = ' +
                       ('eps' if result is None else '($ptascii(' + json.dumps(str(result)) + '))'),
                       state + '_result99 = ' + state + '[.RESULT = KNOWN (PINT 99)]',
                       '$binary_apply(' + state + '_result99, DIVIDE, ' + actual_left + ', ' + right + ', 1) = ' +
                       state + '_result99' + ('' if name == 'zero' else '[.RESULT = KNOWN (' + output + ')]'),
                       '$string_read_runtime_value(' + state + '_result99, ' + origin + ') = ' +
                       ('eps' if result is None else '(PINT ' + integer(result) + ')')]
            if name == 'zero':
                normal = state + '_normal'
                guards += [normal + ' = ' + state + '_result99[.COMPLETION = NORMAL]',
                           '$binary_apply(' + normal + ', DIVIDE, PBOOL true, PBOOL false, 1) = ' + normal + '[.COMPLETION = THROWN "DivisionByZeroError" ($ptascii("Division by zero")) 1]',
                           '$string_read_runtime_value(' + normal + ', ' + origin + ') = eps']
            if name in ('float', 'compiled', 'null', 'string'):
                child = origin + '_left'
                guards += ['$origin_child((' + origin + '), [PCFIELD 0]) = (' + child + ')',
                           '$compiled_read(' + state + ', ' + child + ') = (' + left + ')',
                           '$string_read_runtime_value(' + state + ', ' + child + ') = ' +
                           ('(PFLOAT 0)' if name == 'float' else '(' + actual_left + ')' if name == 'string' else 'eps')]
    return checks + guards, derived + len(guards)


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    prep = output.with_name(output.name + '-control-prep')
    prep.mkdir(parents=True)
    one, zero, two = '(!0.0)', '(!INF)', '((!0.0)+(!0.0))'
    eight = '(' + two + '*(' + two + '*' + two + '))'
    count63 = '((' + eight + '*' + eight + ')-' + one + ')'
    minimum = '((+' + one + ') << (+' + count63 + '))'
    min_value, min_number = 'PINT $(-9223372036854775808)', 'NINT $(-9223372036854775808)'
    raw = (
        ('zero', one + '/' + zero, None, 'PBOOL true', 'PBOOL false', 'NINT 1', 'NINT 0', 'DIVZERO', None),
        ('fraction', one + '/' + two, None, 'PBOOL true', 'PINT 2', 'NINT 1', 'NINT 2', 'NUM (NFLOAT 4602678819172646912)', 'PFLOAT 4602678819172646912'),
        ('overflow', minimum + '/(-' + one + ')', None, min_value, 'PINT $(-1)', min_number, 'NINT $(-1)', 'NUM (NFLOAT 4890909195324358656)', 'PFLOAT 4890909195324358656'),
        ('float', '0.0/' + one, None, 'PFLOAT 0', 'PBOOL true', 'NFLOAT 0', 'NINT 1', 'NUM (NFLOAT 0)', 'PFLOAT 0'),
        ('compiled', '1/' + one, None, 'PINT 1', 'PBOOL true', 'NINT 1', 'NINT 1', 'NUM (NINT 1)', 'PINT 1'),
        ('null', 'null/' + one, None, 'PNULL', 'PBOOL true', 'NINT 0', 'NINT 1', 'NUM (NINT 0)', 'PINT 0'),
        ('string', "'1'/" + one, 1, 'PSTRING ($ptascii("1"))', 'PBOOL true', 'NINT 1', 'NINT 1', 'NUM (NINT 1)', 'PINT 1'),
        ('minimum', minimum + '/' + one, -9223372036854775808, min_value, 'PBOOL true', min_number, 'NINT 1', 'NUM (' + min_number + ')', min_value),
        ('minimum_identity', minimum + '/' + minimum, 1, min_value, min_value, min_number, min_number, 'NUM (NINT 1)', 'PINT 1'),
        ('integer_zero', '(-' + zero + ')/' + one, 0, 'PINT 0', 'PBOOL true', 'NINT 0', 'NINT 1', 'NUM (NINT 0)', 'PINT 0'),
    )
    paths = {row[0]: prep / (row[0] + '.php') for row in raw}
    for name, expression, *_ in raw:
        paths[name].write_bytes(('<?php $x=(' + expression + ');\n').encode())
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
    for name, expression, result, left, right, left_number, right_number, kernel, value in raw:
        targets = [(path, node) for index, statement in enumerate(parsed[name]['ast']['program'])
                   for path, node in occurrences.expected(statement, [('INDEX', index)]) if node['node'] == 'Expr_BinaryOp_Div']
        target, node = min(targets, key=lambda item: len(item[0]))
        CONTROLS.append((name, checked[name]['fixture'], paths[name], target, node, result, left, right, left_number, right_number, kernel, value))
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
    report['scope'] = ('Exact author prefixes plus independent emitted-source/CODE/precision and BUDGET RESULT99 controls. Ten genuine checked-source states cover stale nonnormal zero-divisor refusal, fractional/MIN-overflow FLOAT, FLOAT/compiled-PINT/NULL leaf refusal, literal-INTERNED string division, exact MIN identity and integer zero. Pure numeric results remain distinct from NORMAL-gated throw no-ops; source0/native0, no compiler/schema/API/owner/387 change or accepted replay.')
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
