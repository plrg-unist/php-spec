#!/usr/bin/env python3
"""Independent selected-arm, typed-value and full-ternary authority controls."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import source_occurrences as occurrences
import string_offset_request_base_float_boolnot_special_concat_leading_key_review_state as helpers
import string_offset_request_base_runtime_full_ternary_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_full_ternary_special_concat_leading_key_protocol as source

runner = source.runner
CONTROLS = []


def links(tree, tag='operator'):
    yield tag, tree
    kind = tree[0]
    if kind == 'FLOAT':
        return
    if kind == 'TERNARY':
        yield from links(tree[1], tag + '_0')
        yield from links(tree[2], tag + ('_1' if tree[-1] else '_2'))
        return
    children = (tree[2:3] if kind in ('CAST', 'FLOAT_UNARY') else tree[2:4] if kind == 'FLOAT_BINARY' else
                tree[1:3] if kind in ('ADD', 'SUBTRACT', 'MULTIPLY', 'DIVIDE', 'IDENTICAL') else tree[1:2])
    for index, child in enumerate(children):
        yield from links(child, tag + '_' + str(index))


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    guards = ['pcode_peer_ternary = S_after.CODE[0]', 'pcode_peer_ternary.UNIT = 0',
              'ppool_peer_ternary = S_after.POOLS[0]', 'ppool_peer_ternary.UNIT = 0',
              'pcunit_peer_ternary = S_after.SOURCES[0]', 'pcunit_peer_ternary.ID = 0']

    def refused(state):
        return ['$string_read_runtime_value(' + state + ', porigin_operator) = eps',
                '$string_read_runtime_bytes(' + state + ', porigin_key) = eps',
                '$string_read_request_base_saved(' + state + ', pstringread) = eps']

    for tag, tree in links(source.TREES[index]):
        if tree[0] != 'TERNARY':
            continue
        origin = 'porigin_' + tag
        result = source.value([], tag, tree)[0]
        selected, skipped = ('1', '2') if tree[-1] else ('2', '1')
        for demanded in (tag, tag + '_0', tag + '_' + selected):
            target = 'pcpath_peer_ternary_' + demanded
            guards.append('porigin_' + demanded + ' = PORIGIN 0 ' + target)
            mutations = [
                ('drop', 'S_after[.CODE[0] = pcode_peer_ternary[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_ternary.EXPRESSIONS, ' + target + ', eps)]]'),
                ('flip', 'S_after[.CODE[0] = pcode_peer_ternary[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_ternary.EXPRESSIONS, ' + target + ', (true))]]'),
                ('line', 'S_after[.CODE[0] = pcode_peer_ternary[.EXPRESSIONS = (CODEEXPR ' + target + ' 0 false) :: pcode_peer_ternary.EXPRESSIONS]]'),
                ('precision', 'S_after[.POOLS[0] = ppool_peer_ternary[.CONSTANTS = (PCCPRECISION ' + target + ' 17) :: ppool_peer_ternary.CONSTANTS]]'),
                ('source', 'S_after[.SOURCES[0] = pcunit_peer_ternary[.OCCURRENCES = (PCOCCURRENCE ' + target + ' (NExprVariable (BYTES "dW5hdXRo") eps)) :: pcunit_peer_ternary.OCCURRENCES]]'),
            ]
            for label, replacement in mutations:
                state = 'S_peer_ternary_' + demanded + '_' + label
                guards += [state + ' = ' + replacement, *refused(state)]
        target = 'pcpath_peer_ternary_' + tag
        state = 'S_peer_ternary_' + tag + '_pool'
        guards += [state + ' = S_after[.POOLS[0] = ppool_peer_ternary[.CONSTANTS = (PCONSTANT ' + target + ' (PINT 99)) :: ppool_peer_ternary.CONSTANTS]]',
                   '$compiled_read(' + state + ', ' + origin + ') = eps',
                   '$string_read_runtime_value(' + state + ', ' + origin + ') = (' + result + ')',
                   '$string_read_runtime_value(S_after[.RESULT = KNOWN (PINT 99)], ' + origin + ') = (' + result + ')',
                   '$string_read_runtime_value(S_after[.POOLS = eps], ' + origin + ') = eps']
        skip_origin, skip_path = 'porigin_' + tag + '_' + skipped, 'pcpath_peer_ternary_' + tag + '_skipped'
        guards.append(skip_origin + ' = PORIGIN 0 ' + skip_path)
        mutations = [
            ('drop', 'S_after[.CODE[0] = pcode_peer_ternary[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_ternary.EXPRESSIONS, ' + skip_path + ', eps)]]'),
            ('line', 'S_after[.CODE[0] = pcode_peer_ternary[.EXPRESSIONS = (CODEEXPR ' + skip_path + ' 0 false) :: pcode_peer_ternary.EXPRESSIONS]]'),
            ('precision', 'S_after[.POOLS[0] = ppool_peer_ternary[.CONSTANTS = (PCCPRECISION ' + skip_path + ' 17) :: ppool_peer_ternary.CONSTANTS]]'),
            ('pool', 'S_after[.CODE[0] = pcode_peer_ternary[.EXPRESSIONS = (CODEEXPR ' + skip_path + ' 5 true) :: pcode_peer_ternary.EXPRESSIONS]][.POOLS[0] = ppool_peer_ternary[.CONSTANTS = (PCONSTANT ' + skip_path + ' (PFLOAT 9221120237041090560)) :: ppool_peer_ternary.CONSTANTS]]'),
        ]
        for label, replacement in mutations:
            state = 'S_peer_ternary_' + tag + '_skipped_' + label
            guards += [state + ' = ' + replacement,
                       '$string_read_runtime_value(' + state + ', ' + origin + ') = (' + result + ')',
                       '$string_read_runtime_bytes(' + state + ', porigin_key) = $string_read_runtime_bytes(S_after, porigin_key)',
                       '$string_read_request_base_saved(' + state + ', pstringread) = $string_read_request_base_saved(S_after, pstringread)']
        state = 'S_peer_ternary_' + tag + '_skipped_source'
        guards += [state + ' = S_after[.SOURCES[0] = pcunit_peer_ternary[.OCCURRENCES = (PCOCCURRENCE ' + skip_path + ' (NExprVariable (BYTES "dW5hdXRo") eps)) :: pcunit_peer_ternary.OCCURRENCES]]', *refused(state)]
        for label, completion in (('budget', 'BUDGET'), ('pending', 'SOURCE_PENDING'),
                                  ('unsupported', 'UNSUPPORTED "peer_ternary"'), ('exited', 'EXITED 0'),
                                  ('thrown', 'THROWN "Error" ($ptascii("peer_ternary")) 5')):
            state = 'S_peer_ternary_' + tag + '_' + label
            guards += [state + ' = S_after[.COMPLETION = ' + completion + '][.RESULT = KNOWN (' + result + ')]',
                       '$string_read_runtime_value(' + state + ', ' + origin + ') = eps', *refused(state)]
    if index == 0:
        for number, (name, fixture, original, target, node, expected) in enumerate(CONTROLS):
            state, origin = 'S_peer_ternary_control_' + str(number), 'porigin_peer_ternary_control_' + str(number)
            normal, output = state + '_normal', 'eps' if expected is None else '(' + expected + ')'
            guards += [state + ' = $php_run(' + fixture + ', 0, ' + json.dumps(base64.b64encode(bytes(original)).decode()) + ')',
                       state + '.COMPLETION = BUDGET', origin + ' = PORIGIN 0 ' + occurrences.path_term(target),
                       '$origin_node(' + state + '.SOURCES, ' + origin + ') = (' + occurrences.node_term(node) + ')',
                       origin + ' = PORIGIN 0 pcpath_peer_ternary_control_' + str(number),
                       '$code_at(' + state + '.CODE, 0) = (pcode_peer_ternary_control_' + str(number) + ')',
                       '$code_expression(pcode_peer_ternary_control_' + str(number) + '.EXPRESSIONS, pcpath_peer_ternary_control_' + str(number) + ') = ((1, false))',
                       '$compiled_read(' + state + ', ' + origin + ') = eps',
                       '$compiled_precision(' + state + ', (' + origin + ')) = (14)',
                       '$string_read_runtime_value(' + state + ', ' + origin + ') = eps',
                       normal + ' = ' + state + '[.COMPLETION = NORMAL]',
                       '$string_read_runtime_value(' + normal + ', ' + origin + ') = ' + output,
                       '$string_read_runtime_bytes(' + normal + ', ' + origin + ') = ' +
                       ('($echo_value(' + expected + '))' if expected is not None and not expected.startswith('PFLOAT ') else 'eps'),
                       '$string_read_runtime_value(' + normal + '[.RESULT = KNOWN (PINT 99)], ' + origin + ') = ' + output]
    return checks + guards, derived + len(guards)


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    prep = output.with_name(output.name + '-control-prep')
    prep.mkdir(parents=True)
    truth, false = '(!0.0)', '(!INF)'
    one, zero = '(+' + truth + ')', '(+' + false + ')'
    fraction, negative_zero = '(1.5+' + zero + ')', '-(0.0+' + zero + ')'
    infinity = '(INF+' + zero + ')'
    raw = []
    for name, condition, decision in (
            ('bool_true', truth, True), ('bool_false', false, False),
            ('int_true', one, True), ('int_negative', '-'+one, True), ('int_false', zero, False),
            ('float_true', fraction, True), ('float_zero', '(0.0+' + zero + ')', False),
            ('float_negative_zero', negative_zero, False), ('float_infinity', infinity, True),
            ('float_negative_infinity', '-' + infinity, True)):
        raw.append((name, condition + '?' + (one + ':(1/0)' if decision else '(1/0):' + one), 'PINT 1'))
    for name, selected, expected in (
            ('bool_true', truth, 'PBOOL true'), ('bool_false', false, 'PBOOL false'),
            ('float_fraction', fraction, 'PFLOAT 4609434218613702656'),
            ('float_negative_zero', negative_zero, 'PFLOAT 9223372036854775808'),
            ('float_infinity', infinity, 'PFLOAT 9218868437227405312'),
            ('nested', '(' + false + '?(1/0):' + one + ')', 'PINT 1')):
        raw += [('selected_true_' + name, truth + '?' + selected + ':(1/0)', expected),
                ('selected_false_' + name, false + '?(1/0):' + selected, expected)]
    raw += [
        ('nested_condition', '(' + truth + '?' + false + ':(1/0))?(1/0):' + one, 'PINT 1'),
        ('skipped_variable', truth + '?' + one + ':$missing', 'PINT 1'),
        ('skipped_nan', false + '?(NAN+' + one + '):' + one, 'PINT 1'),
        ('selected_variable', truth + '?$missing:' + one, None),
        ('selected_divzero', false + '?' + one + ':(1/0)', None),
        ('selected_nan', truth + '?(NAN+' + one + '):' + one, None),
        ('condition_variable', '$missing?' + one + ':' + zero, None),
        ('condition_nan', '(NAN+' + one + ')?' + one + ':' + zero, None),
        ('condition_string', "('1'." + false + ')?' + one + ':' + zero, None),
        ('shorthand_true', truth + '?:' + one, None),
        ('shorthand_false', false + '?:' + one, None),
    ]
    paths = {name: prep / (name + '.php') for name, *_ in raw}
    for name, expression, _ in raw:
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
    for name, expression, expected in raw:
        targets = [(path, node) for index, statement in enumerate(parsed[name]['ast']['program'])
                   for path, node in occurrences.expected(statement, [('INDEX', index)]) if node['node'] == 'Expr_Ternary']
        target, node = min(targets, key=lambda item: len(item[0]))
        CONTROLS.append((name, checked[name]['fixture'], paths[name], target, node, expected))
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
    report['scope'] = ('Exact author prefixes plus independent demanded parent/condition/selected source, CODE/line/precision and missing-pool refusals; own ignored pools and stale RESULT cannot forge answers. Skipped CODE/line/precision/NaN-pool changes preserve the authentic selected value, bytes and saved key, while mismatched skipped SOURCE refuses. Five nonnormal completions cannot use a stale selected RESULT. Thirty-three checked-source controls preserve actual BUDGET states before explicitly derived NORMAL fixtures test Boolean/integer/float truth, signed zero, infinities, typed selected values and nested full ternaries; skipped variable/NaN arms are not demanded, while selected variable/divzero/NaN, warningful or unsupported conditions and shorthand refuse. Exact module51 tasks, REQUEST owners, supplied Throwable, bounds, cleanup and budget rejoining retain the author evidence. Fixture source0/native0; no source/native replay or compiler/formatter/API/kernel/owner/held-boundary expansion.')
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
