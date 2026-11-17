#!/usr/bin/env python3
"""Independent nullness, selected NaN and ordinary coalesce task controls."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import source_occurrences as occurrences
import string_offset_request_base_float_boolnot_special_concat_leading_key_review_state as helpers
import string_offset_request_base_runtime_null_left_nan_coalesce_instanceof_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_null_left_nan_coalesce_instanceof_special_concat_leading_key_protocol as source

runner = source.runner
CONTROLS = []


def links(tree, tag='operator'):
    yield tag, tree
    if tree[:2] == ('NAN', 'NULLCOALESCE'):
        yield from links(tree[2], tag + '_0')
        yield from links(tree[3], tag + '_1')
        return
    if tree[:2] == ('NAN', 'SHORTHAND'):
        yield from links(tree[2], tag + '_0')
        yield from links(tree[3], tag + '_2')
        return
    if tree[0] == 'NAN':
        children = tree[2:] if tree[1] in ('COALESCE', 'CASTFLOAT', 'POWER') else tree[3:] if tree[1] in ('EMITTED', 'UNARY') else ()
    elif tree[0] in ('FLOAT', 'STRING', 'COMPILED'):
        children = ()
    else:
        children = tree[2:3] if tree[0] == 'CAST' else tree[1:3] if tree[0] in ('IDENTICAL', 'ADD', 'COALESCE') else tree[1:2]
    for index, child in enumerate(children):
        yield from links(child, tag + '_' + str(index))


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    guards = ['pcode_peer_null_nan = S_after.CODE[0]', 'ppool_peer_null_nan = S_after.POOLS[0]',
              'pcunit_peer_null_nan = S_after.SOURCES[0]']
    for tag, tree in links(source.TREES[index]):
        if tree[:2] != ('NAN', 'NULLCOALESCE'):
            continue
        origin, target = 'porigin_' + tag, 'pcpath_peer_null_nan'
        value = source.value([], tag, tree)[0]
        right = 'expression_' + tag + '_1'
        transition = 'S_peer_null_nan_transition'
        guards += [origin + ' = PORIGIN 0 ' + target,
                   '$compiled_read(S_after, ' + origin + ') = eps',
                   '$compiled_identity_value(S_after, ' + origin + ') = eps',
                   '$string_read_runtime_instanceof_operand(S_after, ' + origin + ') = (' + value + ')',
                   '$string_read_runtime_value(S_after, ' + origin + ') = eps',
                   '$string_read_runtime_bytes(S_after, ' + origin + ') = eps',
                   '$number_bool(' + value.replace('PFLOAT', 'NFLOAT', 1) + ') = (true, true)',
                   '$truth_value(S_after, ' + value + ', 5) =/= S_after[.RESULT = KNOWN (PBOOL true)]',
                   transition + ' = S_after[.ORIGIN = (' + origin + ')][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN (PINT 77))][.TODO = [VALUE_COPY 9]]',
                   '$coalesce_result(' + transition + ', ' + right + ', 5, 5) = ' + transition + '[.TODO = [$at_task((porigin_' + tag + '_1), EVAL ' + right + '), VALUE_COPY 5, VALUE_COPY 9]][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
                   '$coalesce_result(' + transition + '[.RESULT = KNOWN (PBOOL false)], ' + right + ', 5, 5) = ' + transition + '[.RESULT = KNOWN (PBOOL false)][.BASE = BASE_VALUE (KNOWN PNULL)]',
                   '$coalesce_result(' + transition + '[.RESULT = KNOWN (PINT 0)], ' + right + ', 5, 5) = ' + transition + '[.RESULT = KNOWN (PINT 0)][.BASE = BASE_VALUE (KNOWN PNULL)]']
        if index >= 2:
            continue
        mutations = [
            ('drop', 'S_after[.CODE[0] = pcode_peer_null_nan[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_null_nan.EXPRESSIONS, ' + target + ', eps)]]'),
            ('flip', 'S_after[.CODE[0] = pcode_peer_null_nan[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_null_nan.EXPRESSIONS, ' + target + ', (true))]]'),
            ('line', 'S_after[.CODE[0] = pcode_peer_null_nan[.EXPRESSIONS = (CODEEXPR ' + target + ' 0 false) :: pcode_peer_null_nan.EXPRESSIONS]]'),
            ('left_code', 'S_after[.CODE[0] = pcode_peer_null_nan[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_null_nan.EXPRESSIONS, ' + target + '_0, eps)]]'),
            ('right_code', 'S_after[.CODE[0] = pcode_peer_null_nan[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_null_nan.EXPRESSIONS, ' + target + '_1, eps)]]'),
        ]
        for suffix in ('', '_0', '_1'):
            child_path = target + suffix
            guards += ['porigin_' + tag + suffix + ' = PORIGIN 0 ' + child_path]
            mutations += [('source' + suffix, 'S_after[.SOURCES[0] = pcunit_peer_null_nan[.OCCURRENCES = (PCOCCURRENCE ' + child_path + ' (NExprVariable (BYTES "dW5hdXRo") eps)) :: pcunit_peer_null_nan.OCCURRENCES]]'),
                          ('precision' + suffix, 'S_after[.POOLS[0] = ppool_peer_null_nan[.CONSTANTS = (PCCPRECISION ' + child_path + ' 17) :: ppool_peer_null_nan.CONSTANTS]]')]
        for label, completion in (('budget', 'BUDGET'), ('pending', 'SOURCE_PENDING'), ('throw', 'THROWN "Error" ($ptascii("peer_null_nan")) 5')):
            mutations += [(label, 'S_after[.COMPLETION = ' + completion + '][.RESULT = KNOWN (' + value + ')][.TODO = eps]')]
        for label, replacement in mutations:
            state = 'S_peer_null_nan_' + label
            guards += [state + ' = ' + replacement,
                       '$string_read_runtime_instanceof_operand(' + state + ', ' + origin + ') = eps']
        guards += ['$string_read_runtime_bytes(S_peer_null_nan_drop, porigin_key) = eps',
                   '$string_read_request_base_saved(S_peer_null_nan_drop, pstringread) = eps']
        for label, replacement in (
            ('live_precision', 'S_after[.PRECISIONINI = $ptascii("19")][.PRECISIONMODIFIED = true]'),
            ('cached_other', 'S_after[.RESULT = KNOWN (PINT 77)]'),
        ):
            state = 'S_peer_null_nan_' + label
            guards += [state + ' = ' + replacement,
                       '$string_read_runtime_instanceof_operand(' + state + ', ' + origin + ') = (' + value + ')']
    if index == 0:
        for number, (name, fixture, original, target, node, expected) in enumerate(CONTROLS):
            state, origin = 'S_peer_null_control_' + str(number), 'porigin_peer_null_control_' + str(number)
            normal, child = state + '_normal', origin + '_child'
            guards += [state + ' = $php_run(' + fixture + ', 0, ' + json.dumps(base64.b64encode(bytes(original)).decode()) + ')',
                       state + '.COMPLETION = BUDGET', origin + ' = PORIGIN 0 ' + occurrences.path_term(target),
                       '$origin_node(' + state + '.SOURCES, ' + origin + ') = (' + occurrences.node_term(node) + ')',
                       '$string_read_runtime_value(' + state + ', ' + origin + ') = eps',
                       normal + ' = ' + state + '[.COMPLETION = NORMAL]',
                       '$string_read_runtime_value(' + normal + ', ' + origin + ') = ' + ('eps' if expected is None else '(PBOOL false)'),
                       '$string_read_runtime_bytes(' + normal + ', ' + origin + ') = ' + ('eps' if expected is None else '(eps)'),
                       '$origin_child((' + origin + '), [PCFIELD 0]) = (' + child + ')']
            if expected == 'NAN':
                value = 'PFLOAT n_peer_null_control_' + str(number)
                guards += ['$string_read_runtime_value(' + normal + ', ' + child + ') = eps',
                           '$string_read_runtime_bytes(' + normal + ', ' + child + ') = eps',
                           '$string_read_runtime_instanceof_operand(' + normal + ', ' + child + ') = (' + value + ')',
                           '$pfcast_nan(' + value + ')']
            else:
                guards += ['$string_read_runtime_instanceof_operand(' + normal + ', ' + child + ') = ' + ('eps' if expected is None else '(' + expected + ')')]
    return checks + guards, derived + len(guards)


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    prep = output.with_name(output.name + '-control-prep')
    prep.mkdir(parents=True)
    left = '((!INF) ? true : null)'
    emitted = '(' + left + ' ?? NAN)'
    raw = [
        ('raw_null', '', 'null ?? NAN', 'stdClass', 'NAN'),
        ('selected_arithmetic', '', left + ' ?? (1.0+NAN)', 'stdClass', 'NAN'),
        ('selected_unary', '', left + ' ?? (-NAN)', 'stdClass', 'NAN'),
        ('selected_nested', '', left + ' ?? (null ?? NAN)', 'stdClass', 'NAN'),
        ('nested_left', '', '(' + left + ' ?? null) ?? NAN', 'stdClass', 'NAN'),
        ('coalesce_parent', '', emitted + ' ?? (1/0)', 'stdClass', 'NAN'),
        ('full_parent', '', '(!0.0) ? ' + emitted + ' : (1/0)', 'stdClass', 'NAN'),
        ('shorthand_parent', '', '(!INF) ?: ' + emitted, 'stdClass', 'NAN'),
        ('arithmetic_parent', '', '1.0+' + emitted, 'stdClass', 'NAN'),
        ('unary_parent', '', '-' + emitted, 'stdClass', 'NAN'),
        ('power_parent', '', '2.0**' + emitted, 'stdClass', 'NAN'),
        ('cast_parent', '', '(float)' + emitted, 'stdClass', 'NAN'),
        ('false_left', '', '(!INF) ?? NAN', 'stdClass', 'PBOOL false'),
        ('zero_left', '', '0.0 ?? NAN', 'stdClass', 'PFLOAT 0'),
        ('null_finite', '', left + ' ?? 7.5', 'stdClass', 'PFLOAT 4620130267728707584'),
        ('null_null', '', left + ' ?? null', 'stdClass', 'PNULL'),
        ('quiet_variable', '$left=null;', '$left ?? NAN', 'stdClass', None),
        ('selected_alias', '', left + ' ?? ((double)NAN)', 'stdClass', None),
        ('selected_zero_division', '', left + ' ?? (NAN/((float)(!INF)))', 'stdClass', None),
        ('selected_warningful', '', left + ' ?? (!NAN)', 'stdClass', None),
        ('warningful_left', '', '((!NAN) ? true : null) ?? NAN', 'stdClass', None),
        ('late_namespace_nan', 'namespace Ns;', '((!\\INF) ? true : null) ?? NAN', 'namespace\\Missing', None),
        ('fqn_namespace_nan', 'namespace Ns;', '((!\\INF) ? true : null) ?? \\NAN', 'namespace\\Missing', 'NAN'),
    ]
    paths = {name: prep / (name + '.php') for name, *_ in raw}
    for name, prefix, operand, target, expected in raw:
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
    for name, prefix, operand, target_name, expected in raw:
        target, node = next((path, node) for index, statement in enumerate(parsed[name]['ast']['program'])
                            for path, node in occurrences.expected(statement, [('INDEX', index)]) if node['node'] == 'Expr_Instanceof')
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
    report['scope'] = 'Four histories independently retain ordinary null-left coalesce, selected recursive NaN bits and exact module66 AT(RHS EVAL)/VALUE_COPY/tail/RESULT/BASE; false and integer-zero skip RHS by nullness. Root/both-child source, CODE/read/line/precision and nonnormal counterfacts concentrate on the first two histories; live precision19 and unrelated cached RESULT preserve captured authority. Twenty-three fresh checked-source source0 controls cover selected arithmetic/unary/nested NaNs, nested/full/shorthand/coalesce/arithmetic/unary/POWER/cast parents, false/zero/finite/null selections, quiet-CV and alias/zero-division/warningful refusals, and FQN versus late namespace. General VALUE/BYTE/NaN truth, compiler/numerics, owners/lifetimes and exact holds remain unchanged; native0/source0.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
