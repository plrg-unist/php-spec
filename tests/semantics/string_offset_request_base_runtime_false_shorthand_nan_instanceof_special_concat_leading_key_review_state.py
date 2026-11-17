#!/usr/bin/env python3
"""Independent quiet false shorthand and selected NaN fallback controls."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import source_occurrences as occurrences
import string_offset_request_base_float_boolnot_special_concat_leading_key_review_state as helpers
import string_offset_request_base_runtime_false_shorthand_nan_instanceof_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_false_shorthand_nan_instanceof_special_concat_leading_key_protocol as source

runner = source.runner
CONTROLS = []


def links(tree, tag='operator'):
    yield tag, tree
    if tree[:2] == ('NAN', 'SHORTHAND'):
        yield from links(tree[2], tag + '_0')
        yield from links(tree[3], tag + '_2')
        return
    if tree[0] == 'NAN':
        children = tree[2:] if tree[1] in ('COALESCE', 'CASTFLOAT', 'POWER') else tree[3:] if tree[1] in ('EMITTED', 'UNARY') else ()
    elif tree[0] in ('FLOAT', 'STRING', 'COMPILED'):
        children = ()
    else:
        children = tree[2:3] if tree[0] == 'CAST' else tree[1:3] if tree[0] in ('IDENTICAL', 'ADD') else tree[1:2]
    for index, child in enumerate(children):
        yield from links(child, tag + '_' + str(index))


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    guards = ['pcode_peer_ternary_nan = S_after.CODE[0]', 'ppool_peer_ternary_nan = S_after.POOLS[0]',
              'pcunit_peer_ternary_nan = S_after.SOURCES[0]']
    for tag, tree in links(source.TREES[index]):
        if tree[:2] != ('NAN', 'SHORTHAND'):
            continue
        origin, target = 'porigin_' + tag, 'pcpath_peer_ternary_nan'
        selected = '_2'
        value = source.value([], tag, tree)[0]
        guards += [origin + ' = PORIGIN 0 ' + target,
                   '$origin_child((' + origin + '), [PCFIELD 1]) = (porigin_peer_shorthand_absent)',
                   '$origin_node(S_after.SOURCES, porigin_peer_shorthand_absent) = eps',
                   '$string_read_runtime_instanceof_operand(S_after, ' + origin + ') = (' + value + ')',
                   '$string_read_runtime_value(S_after, ' + origin + ') = eps',
                   '$string_read_runtime_bytes(S_after, ' + origin + ') = eps',
                   '$number_bool(' + value.replace('PFLOAT', 'NFLOAT', 1) + ') = (true, true)',
                   '$truth_value(S_after, ' + value + ', 5) =/= S_after[.RESULT = KNOWN (PBOOL true)]',
                   'S_peer_ternary_nan_paused = S_after[.COMPLETION = BUDGET][.RESULT = KNOWN (' + value + ')][.TODO = eps]',
                   '$string_read_runtime_instanceof_operand(S_peer_ternary_nan_paused, ' + origin + ') = eps']
        if index >= 2:
            continue
        mutations = [
            ('drop', 'S_after[.CODE[0] = pcode_peer_ternary_nan[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_ternary_nan.EXPRESSIONS, ' + target + ', eps)]]'),
            ('flip', 'S_after[.CODE[0] = pcode_peer_ternary_nan[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_ternary_nan.EXPRESSIONS, ' + target + ', (true))]]'),
            ('line', 'S_after[.CODE[0] = pcode_peer_ternary_nan[.EXPRESSIONS = (CODEEXPR ' + target + ' 0 false) :: pcode_peer_ternary_nan.EXPRESSIONS]]'),
            ('condition_code', 'S_after[.CODE[0] = pcode_peer_ternary_nan[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_ternary_nan.EXPRESSIONS, ' + target + '_0, eps)]]'),
            ('selected_code', 'S_after[.CODE[0] = pcode_peer_ternary_nan[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_ternary_nan.EXPRESSIONS, ' + target + selected + ', eps)]]'),
        ]
        for suffix in ('', '_0', '_2'):
            child_path = target + suffix
            guards += ['porigin_' + tag + suffix + ' = PORIGIN 0 ' + child_path]
            mutations += [('source' + suffix, 'S_after[.SOURCES[0] = pcunit_peer_ternary_nan[.OCCURRENCES = (PCOCCURRENCE ' + child_path + ' (NExprVariable (BYTES "dW5hdXRo") eps)) :: pcunit_peer_ternary_nan.OCCURRENCES]]')]
            mutations += [('precision' + suffix, 'S_after[.POOLS[0] = ppool_peer_ternary_nan[.CONSTANTS = (PCCPRECISION ' + child_path + ' 17) :: ppool_peer_ternary_nan.CONSTANTS]]')]
        for label, completion in (('pending', 'SOURCE_PENDING'), ('throw', 'THROWN "Error" ($ptascii("peer_ternary")) 5')):
            mutations += [(label, 'S_after[.COMPLETION = ' + completion + '][.RESULT = KNOWN (' + value + ')][.TODO = eps]')]
        for label, replacement in mutations:
            state = 'S_peer_ternary_nan_' + label
            guards += [state + ' = ' + replacement,
                       '$string_read_runtime_instanceof_operand(' + state + ', ' + origin + ') = eps']
        guards += ['$string_read_runtime_bytes(S_peer_ternary_nan_drop, porigin_key) = eps',
                   '$string_read_request_base_saved(S_peer_ternary_nan_drop, pstringread) = eps']
        for label, replacement in (
            ('live_precision', 'S_after[.PRECISIONINI = $ptascii("19")][.PRECISIONMODIFIED = true]'),
            ('cached_other', 'S_after[.RESULT = KNOWN (PINT 77)]'),
        ):
            state = 'S_peer_ternary_nan_' + label
            guards += [state + ' = ' + replacement,
                       '$string_read_runtime_instanceof_operand(' + state + ', ' + origin + ') = (' + value + ')']
    if index == 0:
        for number, (name, fixture, original, target, node, accepted, nan) in enumerate(CONTROLS):
            state, origin = 'S_peer_ternary_control_' + str(number), 'porigin_peer_ternary_control_' + str(number)
            normal, child = state + '_normal', origin + '_child'
            guards += [state + ' = $php_run(' + fixture + ', 0, ' + json.dumps(base64.b64encode(bytes(original)).decode()) + ')',
                       state + '.COMPLETION = BUDGET', origin + ' = PORIGIN 0 ' + occurrences.path_term(target),
                       '$origin_node(' + state + '.SOURCES, ' + origin + ') = (' + occurrences.node_term(node) + ')',
                       '$string_read_runtime_value(' + state + ', ' + origin + ') = eps',
                       normal + ' = ' + state + '[.COMPLETION = NORMAL]',
                       '$string_read_runtime_value(' + normal + ', ' + origin + ') = ' + ('(PBOOL false)' if accepted else 'eps'),
                       '$string_read_runtime_bytes(' + normal + ', ' + origin + ') = ' + ('(eps)' if accepted else 'eps')]
            if nan:
                guards += ['$origin_child((' + origin + '), [PCFIELD 0]) = (' + child + ')',
                           '$string_read_runtime_value(' + normal + ', ' + child + ') = eps',
                           '$string_read_runtime_bytes(' + normal + ', ' + child + ') = eps']
                if accepted:
                    value = 'PFLOAT n_peer_shorthand_nan_control_' + str(number)
                    guards += ['$string_read_runtime_instanceof_operand(' + normal + ', ' + child + ') = (' + value + ')',
                               '$pfcast_nan(' + value + ')']
                else:
                    guards += ['$string_read_runtime_instanceof_operand(' + normal + ', ' + child + ') = eps']
            else:
                value = 'PBOOL true' if name == 'true_condition' else 'PFLOAT 4620130267728707584'
                guards += ['$origin_child((' + origin + '), [PCFIELD 0]) = (' + child + ')',
                           '$string_read_runtime_instanceof_operand(' + normal + ', ' + child + ') = (' + value + ')']
    return checks + guards, derived + len(guards)


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    prep = output.with_name(output.name + '-control-prep')
    prep.mkdir(parents=True)
    emitted = '((!INF) ?: NAN)'
    raw = [
        ('nested_fallback', '', '(!INF) ?: ' + emitted, 'stdClass', True, True),
        ('full_parent', '', '(!0.0) ? ' + emitted + ' : (1/0)', 'stdClass', True, True),
        ('coalesce_parent', '', emitted + ' ?? (1/0)', 'stdClass', True, True),
        ('arithmetic_parent', '', '1.0+' + emitted, 'stdClass', True, True),
        ('unary_parent', '', '-' + emitted, 'stdClass', True, True),
        ('power_parent', '', '2.0**' + emitted, 'stdClass', True, True),
        ('cast_parent', '', '(float)' + emitted, 'stdClass', True, True),
        ('zero_string_condition', '', '"0" ?: NAN', 'stdClass', True, True),
        ('null_condition', '', 'null ?: NAN', 'stdClass', True, True),
        ('empty_string_condition', '', '"" ?: NAN', 'stdClass', True, True),
        ('true_condition', '', '(!0.0) ?: NAN', 'stdClass', True, False),
        ('nan_condition', '', 'NAN ?: 1', 'stdClass', False, True),
        ('warningful_condition', '', '(!NAN) ?: NAN', 'stdClass', False, True),
        ('quiet_cv_condition', '$condition=false;', '$condition ?: NAN', 'stdClass', False, True),
        ('selected_alias_cast', '', '(!INF) ?: ((double)NAN)', 'stdClass', False, True),
        ('selected_zero_division', '', '(!INF) ?: (NAN/((float)(!INF)))', 'stdClass', False, True),
        ('late_namespace_nan', 'namespace Ns;', '(!\\INF) ?: NAN', 'namespace\\Missing', False, True),
        ('fqn_namespace_nan', 'namespace Ns;', '(!\\INF) ?: \\NAN', 'namespace\\Missing', True, True),
        ('selected_finite', '', '(!INF) ?: 7.5', 'stdClass', True, False),
    ]
    paths = {name: prep / (name + '.php') for name, *_ in raw}
    for name, prefix, operand, target, accepted, nan in raw:
        paths[name].write_bytes(('<?php ' + prefix + '$x=(' + operand + ') instanceof ' + target + ';\n').encode())
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
    for name, prefix, operand, target_name, accepted, nan in raw:
        target, node = next((path, node) for index, statement in enumerate(parsed[name]['ast']['program'])
                            for path, node in occurrences.expected(statement, [('INDEX', index)]) if node['node'] == 'Expr_Instanceof')
        CONTROLS.append((name, checked[name]['fixture'], paths[name], target, node, accepted, nan))
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
    report['scope'] = 'Four actual histories preserve quiet FALSE shorthand selection, exact ABSENT true arm, selected NaN bits, module51 line0/fallback tasks and whole-state TODO/RESULT/BASE with original owners, throws and bounds. Independent root/condition/fallback SOURCE, CODE, line, precision and normality counterfacts concentrate on first two histories; changed live precision19 and cached-other results preserve captured authority. Nineteen fresh checked-source source0 controls cover nested fallbacks, full/coalesce/arithmetic/unary/POWER/cast parents, null/empty/zero-string false conditions, genuine true/finite selection, NaN/warningful/CV conditions, selected alias/zero-division refusal and namespace authority. General VALUE/BYTE/NaN truth, compiler/numerics, owners/lifetimes and exact holds remain unchanged; native0/source0.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
