#!/usr/bin/env python3
"""Independent nullness, typed selection, compiler and state controls."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import source_occurrences as occurrences
import string_offset_request_base_float_boolnot_special_concat_leading_key_review_state as helpers
import string_offset_request_base_runtime_coalesce_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_coalesce_special_concat_leading_key_protocol as source

runner = source.runner
CONTROLS = []


def links(tree, tag='operator'):
    yield tag, tree
    kind = tree[0]
    if kind in ('FLOAT', 'COMPILED', 'NULL_TERNARY'):
        return
    if kind == 'COALESCE':
        children = [tree[1]] + ([] if tree[2] is None else [tree[2]])
    else:
        children = (tree[2:3] if kind in ('CAST', 'FLOAT_UNARY') else tree[2:4] if kind == 'FLOAT_BINARY' else
                    tree[1:3] if kind in ('ADD', 'SUBTRACT', 'MULTIPLY', 'DIVIDE', 'IDENTICAL') else tree[1:2])
    for index, child in enumerate(children):
        yield from links(child, tag + '_' + str(index))


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    guards = ['pcode_peer_coalesce = S_after.CODE[0]', 'pcode_peer_coalesce.UNIT = 0',
              'ppool_peer_coalesce = S_after.POOLS[0]', 'ppool_peer_coalesce.UNIT = 0',
              'pcunit_peer_coalesce = S_after.SOURCES[0]', 'pcunit_peer_coalesce.ID = 0']

    def refused(state):
        return ['$string_read_runtime_value(' + state + ', porigin_operator) = eps',
                '$string_read_runtime_bytes(' + state + ', porigin_key) = eps',
                '$string_read_request_base_saved(' + state + ', pstringread) = eps']

    for tag, tree in links(source.TREES[index]):
        if tree[0] != 'COALESCE':
            continue
        origin, expression = 'porigin_' + tag, 'expression_' + tag
        result = source.value([], tag, tree)[0]
        left = source.value([], tag + '_0', tree[1])[0]
        demanded = (tag, tag + '_0') + ((tag + '_1',) if left == 'PNULL' else ())
        for child in demanded:
            target = 'pcpath_peer_coalesce_' + child
            guards.append('porigin_' + child + ' = PORIGIN 0 ' + target)
            mutations = [
                ('drop', 'S_after[.CODE[0] = pcode_peer_coalesce[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_coalesce.EXPRESSIONS, ' + target + ', eps)]]'),
                ('flip', 'S_after[.CODE[0] = pcode_peer_coalesce[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_coalesce.EXPRESSIONS, ' + target + ', (true))]]'),
                ('line', 'S_after[.CODE[0] = pcode_peer_coalesce[.EXPRESSIONS = (CODEEXPR ' + target + ' 0 false) :: pcode_peer_coalesce.EXPRESSIONS]]'),
                ('precision', 'S_after[.POOLS[0] = ppool_peer_coalesce[.CONSTANTS = (PCCPRECISION ' + target + ' 17) :: ppool_peer_coalesce.CONSTANTS]]'),
                ('source', 'S_after[.SOURCES[0] = pcunit_peer_coalesce[.OCCURRENCES = (PCOCCURRENCE ' + target + ' (NExprVariable (BYTES "dW5hdXRo") eps)) :: pcunit_peer_coalesce.OCCURRENCES]]'),
            ]
            for label, replacement in mutations:
                state = 'S_peer_coalesce_' + child + '_' + label
                guards += [state + ' = ' + replacement, *refused(state)]
        target = 'pcpath_peer_coalesce_' + tag
        state = 'S_peer_coalesce_' + tag + '_pool'
        guards += [state + ' = S_after[.POOLS[0] = ppool_peer_coalesce[.CONSTANTS = (PCONSTANT ' + target + ' (PINT 99)) :: ppool_peer_coalesce.CONSTANTS]]',
                   '$compiled_read(' + state + ', ' + origin + ') = eps',
                   '$string_read_runtime_value(' + state + ', ' + origin + ') = (' + result + ')',
                   '$string_read_runtime_value(S_after[.RESULT = KNOWN (PINT 99)], ' + origin + ') = (' + result + ')',
                   '$string_read_runtime_value(S_after[.POOLS = eps], ' + origin + ') = eps']
        select = 'S_peer_coalesce_' + tag + '_select'
        guards += [select + ' = S_after[.ORIGIN = (' + origin + ')][.RESULT = KNOWN (' + left + ')][.BASE = BASE_VALUE (KNOWN (PINT 99))][.TODO = [VALUE_COPY 11]]',
                   '$coalesce_result(' + select + ', ' + expression + '_1, 5, 5) = ' + select +
                   ('[.TODO = [$at_task((porigin_' + tag + '_1), EVAL ' + expression + '_1), VALUE_COPY 5] ++ ' + select + '.TODO][.RESULT = KNOWN PNULL]' if left == 'PNULL' else '') +
                   '[.BASE = BASE_VALUE (KNOWN PNULL)]']
        if left != 'PNULL':
            skip_path = 'pcpath_peer_coalesce_' + tag + '_skipped'
            guards.append('porigin_' + tag + '_1 = PORIGIN 0 ' + skip_path)
            mutations = [
                ('drop', 'S_after[.CODE[0] = pcode_peer_coalesce[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_coalesce.EXPRESSIONS, ' + skip_path + ', eps)]]'),
                ('line', 'S_after[.CODE[0] = pcode_peer_coalesce[.EXPRESSIONS = (CODEEXPR ' + skip_path + ' 0 false) :: pcode_peer_coalesce.EXPRESSIONS]]'),
                ('precision', 'S_after[.POOLS[0] = ppool_peer_coalesce[.CONSTANTS = (PCCPRECISION ' + skip_path + ' 17) :: ppool_peer_coalesce.CONSTANTS]]'),
                ('pool', 'S_after[.CODE[0] = pcode_peer_coalesce[.EXPRESSIONS = (CODEEXPR ' + skip_path + ' 5 true) :: pcode_peer_coalesce.EXPRESSIONS]][.POOLS[0] = ppool_peer_coalesce[.CONSTANTS = (PCONSTANT ' + skip_path + ' (PFLOAT 9221120237041090560)) :: ppool_peer_coalesce.CONSTANTS]]'),
            ]
            for label, replacement in mutations:
                state = 'S_peer_coalesce_' + tag + '_skipped_' + label
                guards += [state + ' = ' + replacement,
                           '$string_read_runtime_value(' + state + ', ' + origin + ') = (' + result + ')',
                           '$string_read_runtime_bytes(' + state + ', porigin_key) = $string_read_runtime_bytes(S_after, porigin_key)',
                           '$string_read_request_base_saved(' + state + ', pstringread) = $string_read_request_base_saved(S_after, pstringread)']
            state = 'S_peer_coalesce_' + tag + '_skipped_source'
            guards += [state + ' = S_after[.SOURCES[0] = pcunit_peer_coalesce[.OCCURRENCES = (PCOCCURRENCE ' + skip_path + ' (NExprVariable (BYTES "dW5hdXRo") eps)) :: pcunit_peer_coalesce.OCCURRENCES]]', *refused(state)]
        for label, completion in (('budget', 'BUDGET'), ('pending', 'SOURCE_PENDING'),
                                  ('unsupported', 'UNSUPPORTED "peer_coalesce"'), ('exited', 'EXITED 0'),
                                  ('thrown', 'THROWN "Error" ($ptascii("peer_coalesce")) 5')):
            state = 'S_peer_coalesce_' + tag + '_' + label
            guards += [state + ' = S_after[.COMPLETION = ' + completion + '][.RESULT = KNOWN (' + result + ')]',
                       '$string_read_runtime_value(' + state + ', ' + origin + ') = eps', *refused(state)]
    if index == 0:
        for number, (name, fixture, original, target, node, expected, quiet) in enumerate(CONTROLS):
            state, origin = 'S_peer_coalesce_control_' + str(number), 'porigin_peer_coalesce_control_' + str(number)
            normal, output = state + '_normal', 'eps' if expected is None else '(' + expected + ')'
            expression = occurrences.node_term(node['fields'][0])
            guards += [state + ' = $php_run(' + fixture + ', 0, ' + json.dumps(base64.b64encode(bytes(original)).decode()) + ')',
                       state + '.COMPLETION = BUDGET', origin + ' = PORIGIN 0 ' + occurrences.path_term(target),
                       '$origin_node(' + state + '.SOURCES, ' + origin + ') = (' + occurrences.node_term(node) + ')',
                       ('$coalesce_quiet_operand(' if quiet else '~$coalesce_quiet_operand(') + expression + ')',
                       '$coalesce_mode(' + expression + ') = ' + ('PPIS' if quiet else 'PPR'),
                       origin + ' = PORIGIN 0 pcpath_peer_coalesce_control_' + str(number),
                       '$code_at(' + state + '.CODE, 0) = (pcode_peer_coalesce_control_' + str(number) + ')',
                       '$code_expression(pcode_peer_coalesce_control_' + str(number) + '.EXPRESSIONS, pcpath_peer_coalesce_control_' + str(number) + ') = ((1, false))',
                       '$compiled_read(' + state + ', ' + origin + ') = eps',
                       '$compiled_precision(' + state + ', (' + origin + ')) = (14)',
                       '$string_read_runtime_value(' + state + ', ' + origin + ') = eps',
                       normal + ' = ' + state + '[.COMPLETION = NORMAL]',
                       '$string_read_runtime_value(' + normal + ', ' + origin + ') = ' + output,
                       '$string_read_runtime_bytes(' + normal + ', ' + origin + ') = ' +
                       ('($echo_value(' + expected + '))' if expected is not None and expected != 'PNULL' and not expected.startswith('PFLOAT ') else 'eps'),
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
    null = '(' + false + '?true:null)'
    raw = []
    for name, left, expected in (
            ('bool_true', truth, 'PBOOL true'), ('bool_false', false, 'PBOOL false'),
            ('int_one', one, 'PINT 1'), ('int_negative', '-' + one, 'PINT $(-1)'), ('int_zero', zero, 'PINT 0'),
            ('float_fraction', fraction, 'PFLOAT 4609434218613702656'), ('float_zero', '(0.0+' + zero + ')', 'PFLOAT 0'),
            ('float_negative_zero', negative_zero, 'PFLOAT 9223372036854775808'),
            ('float_infinity', infinity, 'PFLOAT 9218868437227405312'),
            ('float_negative_infinity', '-' + infinity, 'PFLOAT 18442240474082181120')):
        raw += [(name, left + '??(1/0)', expected, False),
                ('fallback_' + name, null + '??' + left, expected, False)]
    raw += [
        ('compiled_false', 'false??(1/0)', 'PBOOL false', False),
        ('compiled_zero', '0??(1/0)', 'PINT 0', False),
        ('compiled_null', 'null??' + one, 'PINT 1', False),
        ('null_result', null + '??null', 'PNULL', False),
        ('nested_left', '(' + null + '??' + false + ')??(1/0)', 'PBOOL false', False),
        ('nested_fallback', null + '??(' + null + '??' + zero + ')', 'PINT 0', False),
        ('skipped_variable', false + '??$missing', 'PBOOL false', False),
        ('skipped_nan', zero + '??(NAN+' + one + ')', 'PINT 0', False),
        ('skipped_string', false + "??('1'." + false + ')', 'PBOOL false', False),
        ('selected_variable', null + '??$missing', None, False),
        ('selected_divzero', null + '??(1/0)', None, False),
        ('selected_nan', null + '??(NAN+' + one + ')', None, False),
        ('selected_string', null + "??('1'." + false + ')', None, False),
        ('left_nan', '(NAN+' + one + ')??' + one, None, False),
        ('left_string', "('1'." + false + ')??' + one, None, False),
        ('quiet_variable', '$missing??' + one, None, True),
        ('quiet_dimension', '$missing[0]??' + one, None, True),
        ('quiet_property', '$missing->x??' + one, None, True),
        ('quiet_nullsafe', '$missing?->x??' + one, None, True),
        ('quiet_static_property', 'Missing::$x??' + one, None, True),
    ]
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
    for name, expression, expected, quiet in raw:
        targets = [(path, node) for index, statement in enumerate(parsed[name]['ast']['program'])
                   for path, node in occurrences.expected(statement, [('INDEX', index)]) if node['node'] == 'Expr_BinaryOp_Coalesce']
        target, node = min(targets, key=lambda item: len(item[0]))
        CONTROLS.append((name, checked[name]['fixture'], paths[name], target, node, expected, quiet))
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
    report['scope'] = ('Exact author prefixes plus independent demanded parent/left/selected-fallback source/CODE/line/precision and missing-pool refusals. Ignored own pools and stale RESULT cannot forge answers; five nonnormal completions refuse. Nonnull left values ignore fallback CODE/line/precision/NaN pools but require authentic fallback SOURCE. Full module66 state equality retains original nonnull type and TODO or schedules exact fallback AT(EVAL)/VALUE_COPY while clearing RESULT/BASE. ' + str(len(CONTROLS)) + ' checked-source controls retain actual BUDGET states before explicitly derived NORMAL fixtures distinguish false/zero/signed-zero/infinity from NULL, typed fallbacks and nested coalesces. Skipped variable/NaN/string values are not demanded; demanded failures and each of the five quiet-location compiler modes refuse. Emitted FLOAT/NULL retain BYTE eps. REQUEST owners, supplied Throwable, fixed bounds, cleanup and inherited budget rejoining remain included. Fixture source0/native0; no source/native replay or compiler/formatter/API/owner/held-boundary expansion.')
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
