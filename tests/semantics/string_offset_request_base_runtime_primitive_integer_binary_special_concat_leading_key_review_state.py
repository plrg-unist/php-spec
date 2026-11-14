#!/usr/bin/env python3
"""Independent primitive integer types, coercion state and error boundaries."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import source_occurrences as occurrences
import string_offset_request_base_float_boolnot_special_concat_leading_key_review_state as helpers
import string_offset_request_base_runtime_primitive_integer_binary_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_primitive_integer_binary_special_concat_leading_key_protocol as source

runner = source.runner
CONTROLS = []


def links(tree, tag='operator'):
    if tree[0] in source.INTEGER_OPS:
        yield tag, tree
    if tree[0] in (*source.INTEGER_OPS, 'ADD', 'SUBTRACT', 'MULTIPLY', 'DIVIDE'):
        for index, child in enumerate(tree[1:3]):
            yield from links(child, tag + '_' + str(index))
    elif tree[0] in ('BITNOT', 'POSITIVE', 'NEGATIVE'):
        yield from links(tree[1], tag + '_0')


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    guards = ['pcode_peer_primitive_integer = S_after.CODE[0]', 'pcode_peer_primitive_integer.UNIT = 0',
              'ppool_peer_primitive_integer = S_after.POOLS[0]', 'ppool_peer_primitive_integer.UNIT = 0',
              'pcunit_peer_primitive_integer = S_after.SOURCES[0]', 'pcunit_peer_primitive_integer.ID = 0']

    def refused(state):
        return ['$string_read_runtime_value(' + state + ', porigin_operator) = eps',
                '$string_read_runtime_bytes(' + state + ', porigin_key) = eps',
                '$string_read_request_base_saved(' + state + ', pstringread) = eps']

    # Target the new typed branch; pure-PINT compatibility has separate controls.
    nodes = [(tag, tree) for tag, tree in links(source.TREES[index])
             if any(source.value([], tag + '_' + str(i), child)[0] == 'PNULL' or
                    source.value([], tag + '_' + str(i), child)[0].startswith('PBOOL ')
                    for i, child in enumerate(tree[1:3]))]
    demanded = sorted({child for tag, _ in nodes for child in (tag, tag + '_0', tag + '_1')})
    for tag in demanded:
        origin, target = 'porigin_' + tag, 'pcpath_peer_primitive_integer_' + tag
        guards.append(origin + ' = PORIGIN 0 ' + target)
        for label, replacement in (
                ('drop', 'S_after[.CODE[0] = pcode_peer_primitive_integer[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_primitive_integer.EXPRESSIONS, ' + target + ', eps)]]'),
                ('flip', 'S_after[.CODE[0] = pcode_peer_primitive_integer[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_primitive_integer.EXPRESSIONS, ' + target + ', (true))]]'),
                ('line', 'S_after[.CODE[0] = pcode_peer_primitive_integer[.EXPRESSIONS = (CODEEXPR ' + target + ' 0 false) :: pcode_peer_primitive_integer.EXPRESSIONS]]'),
                ('precision', 'S_after[.POOLS[0] = ppool_peer_primitive_integer[.CONSTANTS = (PCCPRECISION ' + target + ' 17) :: ppool_peer_primitive_integer.CONSTANTS]]'),
                ('source', 'S_after[.SOURCES[0] = pcunit_peer_primitive_integer[.OCCURRENCES = (PCOCCURRENCE ' + target + ' (NExprVariable (BYTES "dW5hdXRo") eps)) :: pcunit_peer_primitive_integer.OCCURRENCES]]')):
            state = 'S_peer_primitive_integer_' + tag + '_' + label
            guards += [state + ' = ' + replacement, *refused(state)]
    for tag, tree in nodes:
        origin, target = 'porigin_' + tag, 'pcpath_peer_primitive_integer_' + tag
        result, _ = source.value([], tag, tree)
        left, number_left = source.value([], tag + '_0', tree[1])
        right, number_right = source.value([], tag + '_1', tree[2])
        state = 'S_peer_primitive_integer_' + tag + '_whole'
        guards += [state + ' = S_after[.RESULT = KNOWN PNULL][.TODO = [VALUE_COPY 11]][.BASE = BASE_VALUE (KNOWN (PINT 99))]',
                   '$integer_coerce(' + state + ', ' + left + ', 5) = ' + state + '[.RESULT = KNOWN (PINT ' + number_left + ')]',
                   '$integer_coerce(' + state + '[.RESULT = KNOWN (PINT ' + number_left + ')], ' + right + ', 5) = ' + state + '[.RESULT = KNOWN (PINT ' + number_right + ')]',
                   '$binary_apply(' + state + ', ' + tree[0] + ', ' + left + ', ' + right + ', 5) = ' + state + '[.RESULT = KNOWN (' + result + ')]',
                   '$string_read_runtime_value(' + state + ', ' + origin + ') = (' + result + ')',
                   '$string_read_runtime_value(S_after[.RESULT = KNOWN (PINT 99)], ' + origin + ') = (' + result + ')',
                   'S_peer_primitive_integer_' + tag + '_pool = S_after[.POOLS[0] = ppool_peer_primitive_integer[.CONSTANTS = (PCONSTANT ' + target + ' (PINT 99)) :: ppool_peer_primitive_integer.CONSTANTS]]',
                   '$compiled_read(S_peer_primitive_integer_' + tag + '_pool, ' + origin + ') = eps',
                   '$string_read_runtime_value(S_peer_primitive_integer_' + tag + '_pool, ' + origin + ') = (' + result + ')']
    for label, completion in (('budget', 'BUDGET'), ('pending', 'SOURCE_PENDING'),
                              ('unsupported', 'UNSUPPORTED "peer_primitive_integer"'), ('exited', 'EXITED 0'),
                              ('thrown', 'THROWN "Error" ($ptascii("peer_primitive_integer")) 5')):
        state = 'S_peer_primitive_integer_' + label
        guards += [state + ' = S_after[.COMPLETION = ' + completion + '][.RESULT = KNOWN (PINT ' + source.integers.integer((1, -1, 0, -4)[index]) + ')]', *refused(state)]
    guards += [*refused('S_after[.POOLS = eps]'), *refused('S_after[.DECLARATIONS = eps]'),
               '$string_read_request_base_saved(S_after, pstringread[.READ.OWNERS = BASE_VALUE (KNOWN pstringread.READ.BASE)]) = eps']
    if index == 0:
        guards += ['~$long_range(9223372036854775808)', '~$long_range($(-9223372036854775809))']
        for number, (name, fixture, original, target, node, expected, compatibility) in enumerate(CONTROLS):
            state, origin = 'S_peer_primitive_integer_control_' + str(number), 'porigin_peer_primitive_integer_control_' + str(number)
            normal = state + '_normal'
            result = 'eps' if expected is None else '(PINT ' + source.integers.integer(expected) + ')'
            byte_result = 'eps' if expected is None else '($ptascii(' + json.dumps(str(expected)) + '))'
            guards += [state + ' = $php_run(' + fixture + ', 0, ' + json.dumps(base64.b64encode(bytes(original)).decode()) + ')',
                       state + '.COMPLETION = BUDGET', origin + ' = PORIGIN 0 ' + occurrences.path_term(target),
                       '$origin_node(' + state + '.SOURCES, ' + origin + ') = (' + occurrences.node_term(node) + ')',
                       origin + ' = PORIGIN 0 pcpath_peer_primitive_integer_control_' + str(number),
                       '$code_at(' + state + '.CODE, 0) = (pcode_peer_primitive_integer_control_' + str(number) + ')',
                       '$code_expression(pcode_peer_primitive_integer_control_' + str(number) + '.EXPRESSIONS, pcpath_peer_primitive_integer_control_' + str(number) + ') = ((1, false))',
                       '$compiled_read(' + state + ', ' + origin + ') = eps',
                       normal + ' = ' + state + '[.COMPLETION = NORMAL]',
                       '$string_read_runtime_value(' + normal + ', ' + origin + ') = ' + result,
                       '$string_read_runtime_bytes(' + normal + ', ' + origin + ') = ' + byte_result,
                       '$string_read_runtime_value(' + normal + '[.RESULT = KNOWN (PINT 99)], ' + origin + ') = ' + result,
                       '$string_read_runtime_value(' + state + '[.RESULT = KNOWN (PINT 99)], ' + origin + ') = ' + (result if compatibility else 'eps')]
            if name.startswith(('left_null_', 'right_true_')):
                child, field, value = origin + '_child', 0 if name.startswith('left_null_') else 1, 'PNULL' if name.startswith('left_null_') else 'PBOOL true'
                guards += ['$origin_child((' + origin + '), [PCFIELD ' + str(field) + ']) = (' + child + ')',
                           '$compiled_read(' + state + ', ' + child + ') = (' + value + ')',
                           '$string_read_runtime_value(' + state + ', ' + child + ') = (' + value + ')']
            if name.startswith('float_'):
                child = origin + '_float'
                guards += ['$origin_child((' + origin + '), [PCFIELD 0]) = (' + child + ')',
                           '$string_read_runtime_value(' + normal + ', ' + child + ') = (PFLOAT 0)',
                           '$integer_coerce(' + normal + ', PFLOAT 0, 1) = ' + normal + '[.RESULT = KNOWN (PINT 0)]',
                           '$binary_apply(' + normal + ', ' + ('BITOR' if name == 'float_or' else 'MODULO') + ', PFLOAT 0, PINT 1, 1) = ' + normal + '[.RESULT = KNOWN (PINT ' + ('1' if name == 'float_or' else '0') + ')]']
            if compatibility:
                for completion in ('SOURCE_PENDING', 'UNSUPPORTED "peer_control"', 'EXITED 0', 'THROWN "Error" ($ptascii("peer_control")) 1'):
                    guards += ['$string_read_runtime_value(' + state + '[.COMPLETION = ' + completion + '][.RESULT = KNOWN (PINT 99)], ' + origin + ') = ' + result]
    return checks + guards, derived + len(guards)


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    prep = output.with_name(output.name + '-control-prep')
    prep.mkdir(parents=True)
    one, zero, negative = '(+(!0.0))', '(+(!INF))', '(-(!0.0))'
    ops = (('MODULO', '%', 0, 0, 0), ('BITAND', '&', 0, 1, 0), ('BITOR', '|', 1, 1, 1),
           ('BITXOR', '^', 1, 0, 1), ('SHIFTLEFT', '<<', 0, 2, 0), ('SHIFTRIGHT', '>>', 0, 0, 0))
    raw = []
    for name, symbol, null_result, true_result, false_result in ops:
        raw += [('left_null_' + name, '(null' + symbol + one + ')', null_result, False),
                ('right_true_' + name, '(' + one + symbol + 'true)', true_result, False),
                ('left_false_' + name, '(false' + symbol + one + ')', false_result, False),
                ('pure_int_' + name, '(' + one + symbol + one + ')', true_result, True)]
    raw += [(name, expression, None, False) for name, expression in (
        ('zero_mod_null', '(' + one + '%null)'), ('zero_mod_false', '((!0.0)%false)'),
        ('negative_left', '(true<<' + negative + ')'), ('negative_right', '(null>>' + negative + ')'),
        ('float_or', '(0.0|' + one + ')'), ('float_mod', '(0.0%' + one + ')'),
        ('string_or', "('0'|" + one + ')'), ('bool_not', '(~(!0.0))'),
        ('array_or', '([]|' + one + ')'), ('object_or', '((new stdClass)|' + one + ')'))]
    raw += [('minimum_mod', '(PHP_INT_MIN%(!0.0))', 0, False),
            ('bool_count64_left', '(true<<(64+' + zero + '))', 0, False),
            ('bool_count64_right', '(true>>(64+' + zero + '))', 0, False),
            ('minimum_or_true', '(PHP_INT_MIN|(!0.0))', -9223372036854775807, False),
            ('maximum_shift_true', '(PHP_INT_MAX<<(!0.0))', -2, False)]
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
    for name, expression, expected, compatibility in raw:
        target = [('INDEX', 0), ('FIELD', 0), ('FIELD', 1)]
        node = next(node for path, node in occurrences.expected(parsed[name]['ast']['program'][0], [('INDEX', 0)]) if path == target)
        CONTROLS.append((name, checked[name]['fixture'], paths[name], target, node, expected, compatibility))
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
    report['scope'] = ('Exact author histories plus independent demanded six-op parent/child source, CODE, positive-line and equal-precision controls; original typed sequential coercion/binary state retains nonempty TODO and BASE. New BOOL/NULL requires NORMAL even when raw compiled children and stale RESULT remain available, while six old pure-PINT operators retain five nonnormal completions. ' + str(len(CONTROLS)) + ' checked-source controls cover all six operators with raw NULL/true/false, pure-PINT compatibility, quiet FLOAT refusal, numeric strings, arrays/objects, unchanged Boolean BITNOT, MOD0/negative shifts, count64 and signed64 boundaries. Actual REQUEST owners, supplied Throwable, fixed bounds, cleanup and inherited budgets remain. Fixture source0/native0; original author binding failure/unrun cuts retain zero credit. No387/compiler/numeric/formatter/API/owner or held-boundary change and no accepted source/native replay.')
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
