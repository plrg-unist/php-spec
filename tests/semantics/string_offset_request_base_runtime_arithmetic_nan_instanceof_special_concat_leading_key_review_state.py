#!/usr/bin/env python3
"""Independent emitted-NaN receipts, proper descent and paused-state fences."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import source_occurrences as occurrences
import string_offset_request_base_float_boolnot_special_concat_leading_key_review_state as helpers
import string_offset_request_base_runtime_arithmetic_nan_instanceof_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_arithmetic_nan_instanceof_special_concat_leading_key_protocol as source

runner = source.runner
CONTROLS = []


def links(tree, tag='operator'):
    yield tag, tree
    if tree[0] == 'NAN':
        children = tree[3:] if tree[1] == 'EMITTED' else ()
    elif tree[0] in ('FLOAT', 'STRING', 'COMPILED'):
        children = ()
    else:
        children = tree[2:3] if tree[0] == 'CAST' else tree[1:3] if tree[0] in ('IDENTICAL', 'ADD') else tree[1:2]
    for index, child in enumerate(children):
        yield from links(child, tag + '_' + str(index))


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    guards = ['pcode_peer_arith_nan = S_after.CODE[0]', 'ppool_peer_arith_nan = S_after.POOLS[0]',
              'pcunit_peer_arith_nan = S_after.SOURCES[0]']
    for tag, tree in links(source.TREES[index]):
        if tree[:2] != ('NAN', 'EMITTED'):
            continue
        origin, target = 'porigin_' + tag, 'pcpath_peer_arith_nan'
        value = 'PFLOAT n_compiled_nan_' + tag
        left = source.value([], tag + '_0', tree[3])[0]
        right = source.value([], tag + '_1', tree[4])[0]
        guards += [origin + ' = PORIGIN 0 ' + target,
                   '$compiled_read(S_after, ' + origin + ') = eps',
                   '$compiled_identity_value(S_after, ' + origin + ') = eps',
                   '$string_read_runtime_instanceof_operand(S_after, ' + origin + ') = (' + value + ')',
                   '$string_read_runtime_value(S_after, ' + origin + ') = eps',
                   '$string_read_runtime_bytes(S_after, ' + origin + ') = eps',
                   'S_peer_arith_nan_paused = S_after[.COMPLETION = BUDGET][.RESULT = KNOWN (' + value + ')]',
                   '$binary_apply(S_peer_arith_nan_paused, ' + tree[2] + ', ' + left + ', ' + right + ', 5) = S_peer_arith_nan_paused',
                   '$string_read_runtime_instanceof_operand(S_peer_arith_nan_paused, ' + origin + ') = eps',
                   '$string_read_runtime_bytes(S_peer_arith_nan_paused, porigin_key) = eps']
        mutations = [
            ('drop', 'S_after[.CODE[0] = pcode_peer_arith_nan[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_arith_nan.EXPRESSIONS, ' + target + ', eps)]]'),
            ('flip', 'S_after[.CODE[0] = pcode_peer_arith_nan[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_arith_nan.EXPRESSIONS, ' + target + ', (true))]]'),
            ('line', 'S_after[.CODE[0] = pcode_peer_arith_nan[.EXPRESSIONS = (CODEEXPR ' + target + ' 0 false) :: pcode_peer_arith_nan.EXPRESSIONS]]'),
        ]
        for suffix in ('', '_0', '_1'):
            child_path = target + suffix
            guards += ['porigin_' + tag + suffix + ' = PORIGIN 0 ' + child_path]
            mutations += [('precision' + suffix, 'S_after[.POOLS[0] = ppool_peer_arith_nan[.CONSTANTS = (PCCPRECISION ' + child_path + ' 17) :: ppool_peer_arith_nan.CONSTANTS]]')]
            if suffix:
                mutations += [('source' + suffix, 'S_after[.SOURCES[0] = pcunit_peer_arith_nan[.OCCURRENCES = (PCOCCURRENCE ' + child_path + ' (NExprVariable (BYTES "dW5hdXRo") eps)) :: pcunit_peer_arith_nan.OCCURRENCES]]')]
        for suffix, flag in (('_0', '(true)'), ('_1', '(false)')):
            mutations += [('child_code' + suffix, 'S_after[.CODE[0] = pcode_peer_arith_nan[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_arith_nan.EXPRESSIONS, ' + target + suffix + ', ' + flag + ')]]')]
        for label, replacement in mutations:
            state = 'S_peer_arith_nan_' + label
            guards += [state + ' = ' + replacement,
                       '$string_read_runtime_instanceof_operand(' + state + ', ' + origin + ') = eps',
                       '$string_read_runtime_bytes(' + state + ', porigin_key) = eps',
                       '$string_read_request_base_saved(' + state + ', pstringread) = eps']
        guards += ['S_peer_arith_nan_live_precision = S_after[.PRECISIONINI = $ptascii("17")][.PRECISIONMODIFIED = true]',
                   '$string_read_runtime_instanceof_operand(S_peer_arith_nan_live_precision, ' + origin + ') = (' + value + ')']
    if index == 0:
        for number, (name, fixture, original, target, node, accepted, nan) in enumerate(CONTROLS):
            state, origin = 'S_peer_arith_control_' + str(number), 'porigin_peer_arith_control_' + str(number)
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
            if name == 'compiled_bridge':
                bridge, child_path = state + '_bridge', 'pcpath_peer_arith_bridge'
                guards += [child + ' = PORIGIN 0 ' + child_path,
                           '$compiled_read(' + normal + ', ' + child + ') = (PFLOAT n_peer_arith_bridge)',
                           'pcode_peer_arith_bridge = ' + normal + '.CODE[0]',
                           bridge + ' = ' + normal + '[.CODE[0] = pcode_peer_arith_bridge[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_arith_bridge.EXPRESSIONS, ' + child_path + ', (false))]]',
                           '$compiled_read(' + bridge + ', ' + child + ') = eps',
                           '$compiled_identity_value(' + bridge + ', ' + child + ') = eps',
                           '$string_read_runtime_instanceof_operand(' + bridge + ', ' + child + ') = (PFLOAT n_peer_arith_bridge)',
                           '$string_read_runtime_value(' + bridge + ', ' + child + ') = eps',
                           '$string_read_runtime_value(' + bridge + ', ' + origin + ') = (PBOOL false)']
    return checks + guards, derived + len(guards)


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    prep = output.with_name(output.name + '-control-prep')
    prep.mkdir(parents=True)
    emitted = '(((float)(!INF))*INF)'
    raw = [
        ('old_emitted', '', emitted, 'stdClass', True, True),
        ('recursive_left', '', emitted + '+1.0', 'stdClass', True, True),
        ('recursive_right', '', '1.0+' + emitted, 'stdClass', True, True),
        ('quiet_string', '', '"0"*' + emitted, 'stdClass', True, True),
        ('quiet_bool', '', 'false+' + emitted, 'stdClass', True, True),
        ('quiet_null', '', 'null-' + emitted, 'stdClass', True, True),
        ('leading_string', '', '"0junk"*' + emitted, 'stdClass', False, True),
        ('bad_string', '', '"no"*' + emitted, 'stdClass', False, True),
        ('zero_division', '', emitted + '/((float)(!INF))', 'stdClass', False, True),
        ('emitted_power', '', '(-1.0)**(((float)(!0.0))/2)', 'stdClass', False, True),
        ('emitted_unary', '', '+' + emitted, 'stdClass', True, True),
        ('late_namespace_inf', 'namespace Ns;', emitted, 'namespace\\Missing', False, True),
        ('fqn_namespace_inf', 'namespace Ns;', '((float)(!\\INF))*\\INF', 'namespace\\Missing', True, True),
        ('finite_fallback', '', '((float)(!INF))+1.0', 'stdClass', True, False),
        ('compiled_bridge', '', 'INF-INF', 'stdClass', True, True),
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
    watched.add(Path(__file__).with_name('string_offset_request_base_runtime_compiled_nan_instanceof_special_concat_leading_key_review_state.py'))
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.PREFIX += helpers.HELPERS
    runner.cases, runner.OUTPUTS, runner.conditions = cases, tuple(cases.OUTPUTS.values()), conditions
    passed = runner.main()
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = 'Current four histories add independent emitted-NaN missing/flipped CODE, root/both-child source/precision and line fences, live-versus-captured precision and explicit cached-paused-NaN counterexamples. Lower binary_apply can retain the paused cached result while the operand certificate refuses it. Fifteen checked-source source0 controls cover proper left/right recursive NaNs, quiet string/BOOL/NULL operands, warningful/bad strings, zero division, emitted POWER and late namespace fallback refusal, genuine FQN namespace and finite fallback. The later unary operand certificate promotes the emitted-unary control. Fresh emitted and compiled-INF-INF false-CODE bridge controls validate only the two affected old compiled-NaN expectation promotions without historical replay. General VALUE/BYTE/truth/compiler/formatter/owner and exact held boundaries stay unchanged; native originals reused once, fixture source0/native0.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
