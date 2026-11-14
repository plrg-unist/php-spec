#!/usr/bin/env python3
"""Independent integer POWER results, normal-state demand and type boundaries."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import source_occurrences as occurrences
import string_offset_request_base_float_boolnot_special_concat_leading_key_review_state as helpers
import string_offset_request_base_runtime_integer_power_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_integer_power_special_concat_leading_key_protocol as source

runner = source.runner
CONTROLS = []


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    guards = ['pcode_peer_power = S_after.CODE[0]', 'pcode_peer_power.UNIT = 0',
              'ppool_peer_power = S_after.POOLS[0]', 'ppool_peer_power.UNIT = 0',
              'pcunit_peer_power = S_after.SOURCES[0]', 'pcunit_peer_power.ID = 0']

    def refused(state):
        return ['$string_read_runtime_value(' + state + ', porigin_operator) = eps',
                '$string_read_runtime_bytes(' + state + ', porigin_key) = eps',
                '$string_read_request_base_saved(' + state + ', pstringread) = eps']

    for tag in ('operator_0', 'operator_0_0', 'operator_0_1'):
        target = 'pcpath_peer_power_' + tag
        guards.append('porigin_' + tag + ' = PORIGIN 0 ' + target)
        for label, replacement in (
                ('drop', 'S_after[.CODE[0] = pcode_peer_power[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_power.EXPRESSIONS, ' + target + ', eps)]]'),
                ('flip', 'S_after[.CODE[0] = pcode_peer_power[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_power.EXPRESSIONS, ' + target + ', (true))]]'),
                ('line', 'S_after[.CODE[0] = pcode_peer_power[.EXPRESSIONS = (CODEEXPR ' + target + ' 0 false) :: pcode_peer_power.EXPRESSIONS]]'),
                ('precision', 'S_after[.POOLS[0] = ppool_peer_power[.CONSTANTS = (PCCPRECISION ' + target + ' 17) :: ppool_peer_power.CONSTANTS]]'),
                ('source', 'S_after[.SOURCES[0] = pcunit_peer_power[.OCCURRENCES = (PCOCCURRENCE ' + target + ' (NExprVariable (BYTES "dW5hdXRo") eps)) :: pcunit_peer_power.OCCURRENCES]]')):
            state = 'S_peer_power_' + tag + '_' + label
            guards += [state + ' = ' + replacement, *refused(state)]
    tree = source.TREES[index][1]
    left, left_number = source.value([], 'operator_0_0', tree[1])
    right, right_number = source.value([], 'operator_0_1', tree[2])
    result = 'PINT ' + source.integers.integer(tree[-1])
    state = 'S_peer_power_whole'
    guards += [state + ' = S_after[.RESULT = KNOWN PNULL][.TODO = [VALUE_COPY 11]][.BASE = BASE_VALUE (KNOWN (PINT 99))]',
               '$coerce_number(' + left + ') = COERCED (NINT ' + left_number + ') false',
               '$coerce_number(' + right + ') = COERCED (NINT ' + right_number + ') false',
               '$binary_apply(' + state + ', POWER, ' + left + ', ' + right + ', 5) = ' + state + '[.RESULT = KNOWN (' + result + ')]',
               '$string_read_runtime_value(' + state + ', porigin_operator_0) = (' + result + ')',
               '$string_read_runtime_value(S_after[.RESULT = KNOWN (PINT 99)], porigin_operator_0) = (' + result + ')',
               'S_peer_power_pool = S_after[.POOLS[0] = ppool_peer_power[.CONSTANTS = (PCONSTANT pcpath_peer_power_operator_0 (PINT 99)) :: ppool_peer_power.CONSTANTS]]',
               '$compiled_read(S_peer_power_pool, porigin_operator_0) = eps',
               '$string_read_runtime_value(S_peer_power_pool, porigin_operator_0) = (' + result + ')']
    for label, completion in (('budget', 'BUDGET'), ('pending', 'SOURCE_PENDING'),
                              ('unsupported', 'UNSUPPORTED "peer_power"'), ('exited', 'EXITED 0'),
                              ('thrown', 'THROWN "Error" ($ptascii("peer_power")) 5')):
        state = 'S_peer_power_' + label
        guards += [state + ' = S_after[.COMPLETION = ' + completion + '][.RESULT = KNOWN (PINT 99)]', *refused(state)]
    if index == 0:
        for number, (name, fixture, original, target, node, expected, left, right) in enumerate(CONTROLS):
            state, origin = 'S_peer_power_control_' + str(number), 'porigin_peer_power_control_' + str(number)
            normal = state + '_normal'
            result = 'eps' if expected is None else '(PINT ' + source.integers.integer(expected) + ')'
            byte_result = 'eps' if expected is None else '($ptascii(' + json.dumps(str(expected)) + '))'
            guards += [state + ' = $php_run(' + fixture + ', 0, ' + json.dumps(base64.b64encode(bytes(original)).decode()) + ')',
                       state + '.COMPLETION = BUDGET', origin + ' = PORIGIN 0 ' + occurrences.path_term(target),
                       '$origin_node(' + state + '.SOURCES, ' + origin + ') = (' + occurrences.node_term(node) + ')',
                       origin + ' = PORIGIN 0 pcpath_peer_power_control_' + str(number),
                       '$code_at(' + state + '.CODE, 0) = (pcode_peer_power_control_' + str(number) + ')',
                       '$code_expression(pcode_peer_power_control_' + str(number) + '.EXPRESSIONS, pcpath_peer_power_control_' + str(number) + ') = ((1, false))',
                       '$compiled_read(' + state + ', ' + origin + ') = eps',
                       '$string_read_runtime_value(' + state + ', ' + origin + ') = eps',
                       normal + ' = ' + state + '[.COMPLETION = NORMAL]',
                       '$string_read_runtime_value(' + normal + ', ' + origin + ') = ' + result,
                       '$string_read_runtime_bytes(' + normal + ', ' + origin + ') = ' + byte_result,
                       '$string_read_runtime_value(' + normal + '[.RESULT = KNOWN (PINT 99)], ' + origin + ') = ' + result]
            for side, value in enumerate((left, right)):
                if value is not None:
                    child = origin + '_' + str(side)
                    guards += ['$origin_child((' + origin + '), [PCFIELD ' + str(side) + ']) = (' + child + ')',
                               '$string_read_runtime_value(' + normal + ', ' + child + ') = (' + value + ')']
            if name == 'one':
                guards += ['$string_read_runtime_value(' + state + ', ' + origin + '_0) = (PINT 1)',
                           '$string_read_runtime_value(' + state + ', ' + origin + '_1) = (PINT 1)',
                           '$binary_apply(' + state + ', POWER, PINT 1, PINT 1, 1) = ' + state + '[.RESULT = KNOWN (PINT 1)]']
                for completion in ('SOURCE_PENDING', 'UNSUPPORTED "peer_control"', 'EXITED 0', 'THROWN "Error" ($ptascii("peer_control")) 1'):
                    guards += ['$string_read_runtime_value(' + state + '[.COMPLETION = ' + completion + '][.RESULT = KNOWN (PINT 1)], ' + origin + ') = eps']
            if name == 'deprecated_zero':
                suppressed = normal + '_suppressed'
                guards += ['$power_prepare(NINT 0, NINT $(-1)) = POWERDONE (NFLOAT 9218868437227405312) true',
                           suppressed + ' = ' + normal + '[.REPORTING = 0]',
                           '$binary_apply(' + suppressed + ', POWER, PINT 0, PINT $(-1), 1) = ' + suppressed + '[.RESULT = KNOWN (PFLOAT 9218868437227405312)]',
                           '$string_read_runtime_value(' + suppressed + ', ' + origin + ') = eps']
    return checks + guards, derived + len(guards)


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    prep = output.with_name(output.name + '-control-prep')
    prep.mkdir(parents=True)
    one, zero = '(+(!0.0))', '(+(!INF))'
    two, three = '(' + one + '+' + one + ')', '(' + one + '+(' + one + '+' + one + '))'
    true, false, null = '((!0.0)?true:(1/0))', '((!0.0)?false:(1/0))', '((!INF)?true:null)'
    floating = '((!0.0)?1.0:(1/0))'
    raw = [(name, '(' + left + '**' + right + ')', expected, left_value, right_value) for name, left, right, expected, left_value, right_value in (
        ('one', one, one, 1, 'PINT 1', 'PINT 1'), ('zero_zero', zero, zero, 1, 'PINT 0', 'PINT 0'),
        ('zero_one', zero, one, 0, 'PINT 0', 'PINT 1'), ('three_one', three, one, 3, 'PINT 3', 'PINT 1'),
        ('minus_one_odd', '(-' + one + ')', '(3+' + zero + ')', -1, 'PINT $(-1)', 'PINT 3'),
        ('even_power', '(-' + two + ')', '(2+' + zero + ')', 4, 'PINT $(-2)', 'PINT 2'),
        ('minimum', '(-' + two + ')', '(63+' + zero + ')', -9223372036854775808, 'PINT $(-2)', 'PINT 63'),
        ('max_exp_one', one, 'PHP_INT_MAX', 1, 'PINT 1', 'PINT 9223372036854775807'),
        ('max_exp_zero', zero, 'PHP_INT_MAX', 0, 'PINT 0', 'PINT 9223372036854775807'),
        ('true_null', true, null, 1, 'PBOOL true', 'PNULL'), ('false_true', false, true, 0, 'PBOOL false', 'PBOOL true'),
        ('null_false', null, false, 1, 'PNULL', 'PBOOL false'),
        ('overflow', two, '(63+' + zero + ')', None, 'PINT 2', 'PINT 63'),
        ('negative_exponent', one, '(-' + one + ')', None, 'PINT 1', 'PINT $(-1)'),
        ('deprecated_zero', zero, '(-' + one + ')', None, 'PINT 0', 'PINT $(-1)'),
        ('float_base', floating, one, None, 'PFLOAT 4607182418800017408', 'PINT 1'),
        ('float_exponent', one, floating, None, 'PINT 1', 'PFLOAT 4607182418800017408'),
        ('string_base', "('1'.(!INF))", one, None, None, 'PINT 1'),
        ('array_base', '[]', one, None, None, 'PINT 1'))]
    paths = {name: prep / (name + '.php') for name, *_ in raw}
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
    for name, expression, expected, left, right in raw:
        target = [('INDEX', 0), ('FIELD', 0), ('FIELD', 1)]
        node = next(node for path, node in occurrences.expected(parsed[name]['ast']['program'][0], [('INDEX', 0)]) if path == target)
        CONTROLS.append((name, checked[name]['fixture'], paths[name], target, node, expected, left, right))
    watched = {Path(module.__file__).resolve() for module in tuple(sys.modules.values()) if getattr(module, '__file__', None)
               and Path(module.__file__).resolve().parent == Path(__file__).resolve().parent} | set(paths.values())
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.PREFIX += helpers.HELPERS
    runner.cases, runner.OUTPUTS, runner.conditions = cases, tuple(cases.OUTPUTS.values()), conditions
    passed = runner.main()
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    assert report['mode'] == 'fixture SL'
    report['scope'] = ('Exact author histories plus independent demanded POWER/child source, CODE, line and equal-precision guards, stale result/pool and whole-state original typed binary application with nonempty TODO/BASE. ' + str(len(CONTROLS)) + ' checked-source fixtures cover zero/Boolean/null coercions, iterative signed powers, fitting MIN versus overflow, maximal exponents on zero/one, negative-exponent promotion, FLOAT/string/array refusal and suppressed Deprecated. Both certified PINT children and full-state binary equality survive a raw BUDGET view while the new POWER receipt still refuses; all five nonnormal completions stay refused. FLOAT BYTE and numeric/power/formatter/compiler/owner bodies remain unchanged. Actual REQUEST Warning/Throwable/bounds/owners/cleanup/budgets remain; SL fixtures source0/native0 and no accepted old campaign replay or held-boundary change.')
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
