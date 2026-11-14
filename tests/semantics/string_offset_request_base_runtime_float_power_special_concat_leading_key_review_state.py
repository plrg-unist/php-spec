#!/usr/bin/env python3
"""Independent completed FLOAT POWER bits, authority and normal-state bounds."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import source_occurrences as occurrences
import string_offset_request_base_float_boolnot_special_concat_leading_key_review_state as helpers
import string_offset_request_base_runtime_float_power_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_float_power_special_concat_leading_key_protocol as source

runner = source.runner
CONTROLS = []


def power_node(tree, tag='operator'):
    if tree[0] == 'FLOAT_POWER':
        return tag, tree
    children = [child for child in tree[1:] if isinstance(child, tuple)]
    for index, child in enumerate(children):
        found = power_node(child, tag + '_' + str(index))
        if found is not None:
            return found
    return None


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    tag, tree = power_node(source.TREES[index])
    origin = 'porigin_' + tag
    result = 'PFLOAT ' + str(tree[-1])
    guards = ['pcode_peer_power_float = S_after.CODE[0]', 'pcode_peer_power_float.UNIT = 0',
              'ppool_peer_power_float = S_after.POOLS[0]', 'ppool_peer_power_float.UNIT = 0',
              'pcunit_peer_power_float = S_after.SOURCES[0]', 'pcunit_peer_power_float.ID = 0']

    def refused(state):
        return ['$string_read_runtime_value(' + state + ', ' + origin + ') = eps',
                '$string_read_runtime_bytes(' + state + ', porigin_key) = eps',
                '$string_read_request_base_saved(' + state + ', pstringread) = eps']

    for suffix, child in (('', tree), ('_0', tree[1]), ('_1', tree[2])):
        target = 'pcpath_peer_power_float' + suffix
        guards.append('porigin_' + tag + suffix + ' = PORIGIN 0 ' + target)
        leaf = child[0] == 'FLOAT'
        mutations = [
            ('drop', 'S_after[.CODE[0] = pcode_peer_power_float[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_power_float.EXPRESSIONS, ' + target + ', eps)]]'),
            ('flip', 'S_after[.CODE[0] = pcode_peer_power_float[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_power_float.EXPRESSIONS, ' + target + ', (' + str(not leaf).lower() + '))]]'),
            ('precision', 'S_after[.POOLS[0] = ppool_peer_power_float[.CONSTANTS = (PCCPRECISION ' + target + ' 17) :: ppool_peer_power_float.CONSTANTS]]'),
            ('source', 'S_after[.SOURCES[0] = pcunit_peer_power_float[.OCCURRENCES = (PCOCCURRENCE ' + target + ' (NExprVariable (BYTES "dW5hdXRo") eps)) :: pcunit_peer_power_float.OCCURRENCES]]'),
        ]
        if not leaf:
            mutations.append(('line', 'S_after[.CODE[0] = pcode_peer_power_float[.EXPRESSIONS = (CODEEXPR ' + target + ' 0 false) :: pcode_peer_power_float.EXPRESSIONS]]'))
        for label, replacement in mutations:
            state = 'S_peer_power_float' + suffix + '_' + label
            guards += [state + ' = ' + replacement, *refused(state)]
    left = source.value([], tag + '_0', tree[1])[0]
    right = source.value([], tag + '_1', tree[2])[0]
    guards += ['S_peer_power_float_whole = S_after[.RESULT = KNOWN PNULL][.TODO = [VALUE_COPY 11]][.BASE = BASE_VALUE (KNOWN (PINT 99))]',
               '$binary_apply(S_peer_power_float_whole, POWER, ' + left + ', ' + right + ', 5) = S_peer_power_float_whole[.RESULT = KNOWN (' + result + ')]',
               '$string_read_runtime_value(S_peer_power_float_whole, ' + origin + ') = (' + result + ')',
               '$string_read_runtime_value(S_after[.RESULT = KNOWN (PFLOAT 4602678819172646912)], ' + origin + ') = (' + result + ')',
               'S_peer_power_float_pool = S_after[.POOLS[0] = ppool_peer_power_float[.CONSTANTS = (PCONSTANT pcpath_peer_power_float (PFLOAT 4602678819172646912)) :: ppool_peer_power_float.CONSTANTS]]',
               '$compiled_read(S_peer_power_float_pool, ' + origin + ') = eps',
               '$string_read_runtime_value(S_peer_power_float_pool, ' + origin + ') = (' + result + ')',
               '$string_read_runtime_bytes(S_peer_power_float_pool, ' + origin + ') = eps']
    for label, completion in (('budget', 'BUDGET'), ('pending', 'SOURCE_PENDING'),
                              ('unsupported', 'UNSUPPORTED "peer_power_float"'), ('exited', 'EXITED 0'),
                              ('thrown', 'THROWN "Error" ($ptascii("peer_power_float")) 5')):
        state = 'S_peer_power_float_' + label
        guards += [state + ' = S_after[.COMPLETION = ' + completion + '][.RESULT = KNOWN (' + result + ')]', *refused(state)]
    if index == 0:
        for number, (name, fixture, original, target, node, expected, left, right) in enumerate(CONTROLS):
            state, control = 'S_peer_power_float_control_' + str(number), 'porigin_peer_power_float_control_' + str(number)
            normal = state + '_normal'
            value = 'eps' if expected is None else '(' + expected + ')'
            guards += [state + ' = $php_run(' + fixture + ', 0, ' + json.dumps(base64.b64encode(bytes(original)).decode()) + ')',
                       state + '.COMPLETION = BUDGET', control + ' = PORIGIN 0 ' + occurrences.path_term(target),
                       '$origin_node(' + state + '.SOURCES, ' + control + ') = (' + occurrences.node_term(node) + ')',
                       control + ' = PORIGIN 0 pcpath_peer_power_float_control_' + str(number),
                       '$code_at(' + state + '.CODE, 0) = (pcode_peer_power_float_control_' + str(number) + ')',
                       '$code_expression(pcode_peer_power_float_control_' + str(number) + '.EXPRESSIONS, pcpath_peer_power_float_control_' + str(number) + ') = ((1, false))',
                       '$compiled_read(' + state + ', ' + control + ') = eps',
                       '$string_read_runtime_value(' + state + ', ' + control + ') = eps',
                       normal + ' = ' + state + '[.COMPLETION = NORMAL]',
                       '$string_read_runtime_value(' + normal + ', ' + control + ') = ' + value,
                       '$string_read_runtime_bytes(' + normal + ', ' + control + ') = ' + ('($ptascii("1"))' if expected == 'PINT 1' else 'eps'),
                       '$string_read_runtime_value(' + normal + '[.RESULT = KNOWN (PFLOAT 4602678819172646912)], ' + control + ') = ' + value]
            for side, child_value in enumerate((left, right)):
                if child_value is not None:
                    child = control + '_' + str(side)
                    guards += ['$origin_child((' + control + '), [PCFIELD ' + str(side) + ']) = (' + child + ')',
                               '$string_read_runtime_value(' + normal + ', ' + child + ') = (' + child_value + ')']
            if name == 'overflow':
                guards += ['$string_read_runtime_value(' + state + ', ' + control + '_0) = (PINT 2)',
                           '$string_read_runtime_value(' + state + ', ' + control + '_1) = (PINT 63)',
                           '$binary_apply(' + state + ', POWER, PINT 2, PINT 63, 1) = ' + state + '[.RESULT = KNOWN (PFLOAT 4890909195324358656)]']
                for completion in ('SOURCE_PENDING', 'UNSUPPORTED "peer_power_float_control"', 'EXITED 0', 'THROWN "Error" ($ptascii("peer_power_float_control")) 1'):
                    guards += ['$string_read_runtime_value(' + state + '[.COMPLETION = ' + completion + '][.RESULT = KNOWN (PFLOAT 4890909195324358656)], ' + control + ') = eps']
            if name.startswith('deprecated_'):
                negative = name == 'deprecated_negative_zero'
                base, bits = ('9223372036854775808', '18442240474082181120') if negative else ('0', '9218868437227405312')
                suppressed = normal + '_suppressed'
                guards += ['$power_prepare(NFLOAT ' + base + ', NINT $(-1)) = POWERDONE (NFLOAT ' + bits + ') true',
                           suppressed + ' = ' + normal + '[.REPORTING = 0]',
                           '$binary_apply(' + suppressed + ', POWER, PFLOAT ' + base + ', PINT $(-1), 1) = ' + suppressed + '[.RESULT = KNOWN (PFLOAT ' + bits + ')]',
                           '$string_read_runtime_value(' + suppressed + ', ' + control + ') = eps']
            if name == 'general_float_base':
                guards += ['$power_prepare(NFLOAT 4611686018427387904, NINT 1) = POWERGENERAL 4607182418800017408 4611686018427387904 4607182418800017408 0 false']
            if name == 'nan_result':
                guards += ['$power_prepare(NFLOAT 13835058055282163712, NFLOAT 4602678819172646912) = POWERDONE (NFLOAT n_peer_power_nan) false',
                           '$number_bool(NFLOAT n_peer_power_nan) = (true, true)']
            if name == 'nan_child':
                guards += ['$power_prepare(NFLOAT 9221120237041090560, NINT 0) = POWERDONE (NFLOAT 4607182418800017408) false',
                           '$origin_child((' + control + '), [PCFIELD 0]) = (porigin_peer_power_nan_child)',
                           '$string_read_runtime_value(' + normal + ', porigin_peer_power_nan_child) = eps']
    return checks + guards, derived + len(guards)


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    prep = output.with_name(output.name + '-control-prep')
    prep.mkdir(parents=True)
    one, zero = '(+(!0.0))', '(+(!INF))'
    two = '(' + one + '+' + one + ')'
    true, null = '((!0.0)?true:(1/0))', '((!INF)?true:null)'
    floating, negative_zero = '((!0.0)?2.0:(1/0))', '(-((float)' + zero + '))'
    raw = [(name, '(' + left + '**' + right + ')', expected, left_value, right_value) for name, left, right, expected, left_value, right_value in (
        ('float_null', floating, null, 'PFLOAT 4607182418800017408', 'PFLOAT 4611686018427387904', 'PNULL'),
        ('bool_float_zero', true, '0.0', 'PFLOAT 4607182418800017408', 'PBOOL true', 'PFLOAT 0'),
        ('negative_zero', negative_zero, true, 'PFLOAT 9223372036854775808', 'PFLOAT 9223372036854775808', 'PBOOL true'),
        ('negative_zero_even', negative_zero, '(2+' + zero + ')', 'PFLOAT 0', 'PFLOAT 9223372036854775808', 'PINT 2'),
        ('negative_infinity_odd', '(-INF)', '(3+' + zero + ')', 'PFLOAT 18442240474082181120', 'PFLOAT 18442240474082181120', 'PINT 3'),
        ('negative_infinity_negative', '(-INF)', '(-' + one + ')', 'PFLOAT 9223372036854775808', 'PFLOAT 18442240474082181120', 'PINT $(-1)'),
        ('infinity_negative', 'INF', '(-' + one + ')', 'PFLOAT 0', 'PFLOAT 9218868437227405312', 'PINT $(-1)'),
        ('overflow', two, '(63+' + zero + ')', 'PFLOAT 4890909195324358656', 'PINT 2', 'PINT 63'),
        ('tiny_exponent', floating, '1.0e-30', 'PFLOAT 4607182418800017408', 'PFLOAT 4611686018427387904', None),
        ('huge_exponent', '((!0.0)?0.5:(1/0))', '1.0e300', 'PFLOAT 0', 'PFLOAT 4602678819172646912', None),
        ('exact_integer', one, one, 'PINT 1', 'PINT 1', 'PINT 1'),
        ('general_float_base', floating, one, None, 'PFLOAT 4611686018427387904', 'PINT 1'),
        ('general_negative_int', one, '(-' + one + ')', None, 'PINT 1', 'PINT $(-1)'),
        ('deprecated_positive_zero', '(+((float)' + zero + '))', '(-' + one + ')', None, 'PFLOAT 0', 'PINT $(-1)'),
        ('deprecated_negative_zero', negative_zero, '(-' + one + ')', None, 'PFLOAT 9223372036854775808', 'PINT $(-1)'),
        ('nan_result', '(-' + floating + ')', '0.5', None, 'PFLOAT 13835058055282163712', 'PFLOAT 4602678819172646912'),
        ('nan_child', 'NAN', zero, None, None, 'PINT 0'),
        ('string_base', "('1'.(!INF))", '0.0', None, None, 'PFLOAT 0'),
        ('array_base', '[]', one, None, None, 'PINT 1'),
        ('variable_base', '$missing', '0.0', None, None, 'PFLOAT 0'))]
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
        assert node['node'] == 'Expr_BinaryOp_Pow'
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
    report['scope'] = ('Exact author histories plus independent demanded POWER/child source, CODE, line and equal-precision controls, stale result/pool and whole-state original typed binary application with nonempty TODO/BASE. Twenty checked-source fixtures distinguish exact signed zero/infinity, finite integer-overflow FLOAT, tiny/huge exponent specials and existing PINT results from GENERAL, NaN input/result, suppressed positive/negative-zero Deprecated and unauthenticated string/array/variable operands. Both certified integer children and exact overflow full-state binary equality survive a raw BUDGET view while the new FLOAT POWER receipt still refuses; all five nonnormal completions remain refused. FLOAT BYTE stays eps. Numeric/power/formatter/compiler/owner bodies and exact held boundaries remain unchanged; fixture source0/native0, no old campaign or native replay.')
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
