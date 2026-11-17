#!/usr/bin/env python3
"""Independent nonnull NaN coalesce selection and skipped-RHS controls."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import source_occurrences as occurrences
import string_offset_request_base_float_boolnot_special_concat_leading_key_review_state as helpers
import string_offset_request_base_runtime_nonnull_nan_coalesce_instanceof_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_nonnull_nan_coalesce_instanceof_special_concat_leading_key_protocol as source

runner = source.runner
CONTROLS = []


def links(tree, tag='operator'):
    yield tag, tree
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
    guards = ['pcode_peer_coalesce_nan = S_after.CODE[0]', 'ppool_peer_coalesce_nan = S_after.POOLS[0]',
              'pcunit_peer_coalesce_nan = S_after.SOURCES[0]']
    for tag, tree in links(source.TREES[index]):
        if tree[:2] != ('NAN', 'COALESCE'):
            continue
        origin, target = 'porigin_' + tag, 'pcpath_peer_coalesce_nan'
        value = source.value([], tag, tree)[0]
        left = source.value([], tag + '_0', tree[2])[0]
        guards += [origin + ' = PORIGIN 0 ' + target,
                   '$origin_node(S_after.SOURCES, ' + origin + ') = (NExprBinaryOpCoalesce expression_peer_coalesce_left expression_peer_coalesce_right metadata_peer_coalesce)',
                   '~$coalesce_quiet_operand(expression_peer_coalesce_left)',
                   '$compiled_read(S_after, ' + origin + ') = eps',
                   '$compiled_identity_value(S_after, ' + origin + ') = eps',
                   value.removeprefix('PFLOAT ') + ' = ' + left.removeprefix('PFLOAT '),
                   '$string_read_runtime_instanceof_operand(S_after, ' + origin + ') = (' + value + ')',
                   '$coalesce_result(S_after[.RESULT = KNOWN (' + left + ')], expression_peer_coalesce_right, 5, 5) = S_after[.RESULT = KNOWN (' + value + ')][.BASE = BASE_VALUE (KNOWN PNULL)]',
                   '$string_read_runtime_value(S_after, ' + origin + ') = eps',
                   '$string_read_runtime_bytes(S_after, ' + origin + ') = eps',
                   '$number_bool(' + value.replace('PFLOAT', 'NFLOAT', 1) + ') = (true, true)',
                   '$truth_value(S_after, ' + value + ', 5) =/= S_after[.RESULT = KNOWN (PBOOL true)]',
                   'S_peer_coalesce_nan_paused = S_after[.COMPLETION = BUDGET][.RESULT = KNOWN (' + value + ')][.TODO = eps][.BASE = BASE_VALUE (KNOWN PNULL)]',
                   '$coalesce_result(S_peer_coalesce_nan_paused, expression_peer_coalesce_right, 5, 5) = S_peer_coalesce_nan_paused',
                   '$string_read_runtime_instanceof_operand(S_peer_coalesce_nan_paused, ' + origin + ') = eps',
                   '$string_read_runtime_bytes(S_peer_coalesce_nan_paused, porigin_key) = eps']
        mutations = [
            ('drop', 'S_after[.CODE[0] = pcode_peer_coalesce_nan[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_coalesce_nan.EXPRESSIONS, ' + target + ', eps)]]'),
            ('flip', 'S_after[.CODE[0] = pcode_peer_coalesce_nan[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_coalesce_nan.EXPRESSIONS, ' + target + ', (true))]]'),
            ('line', 'S_after[.CODE[0] = pcode_peer_coalesce_nan[.EXPRESSIONS = (CODEEXPR ' + target + ' 0 false) :: pcode_peer_coalesce_nan.EXPRESSIONS]]'),
            ('left_drop', 'S_after[.CODE[0] = pcode_peer_coalesce_nan[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_coalesce_nan.EXPRESSIONS, ' + target + '_0, eps)]]'),
        ]
        for suffix in ('', '_0', '_1'):
            child_path = target + suffix
            guards += ['porigin_' + tag + suffix + ' = PORIGIN 0 ' + child_path]
            mutations += [('source' + suffix, 'S_after[.SOURCES[0] = pcunit_peer_coalesce_nan[.OCCURRENCES = (PCOCCURRENCE ' + child_path + ' (NExprVariable (BYTES "dW5hdXRo") eps)) :: pcunit_peer_coalesce_nan.OCCURRENCES]]')]
            if suffix != '_1':
                mutations += [('precision' + suffix, 'S_after[.POOLS[0] = ppool_peer_coalesce_nan[.CONSTANTS = (PCCPRECISION ' + child_path + ' 17) :: ppool_peer_coalesce_nan.CONSTANTS]]')]
        for label, completion in (('pending', 'SOURCE_PENDING'), ('throw', 'THROWN "Error" ($ptascii("peer_coalesce")) 5')):
            mutations += [(label, 'S_after[.COMPLETION = ' + completion + '][.RESULT = KNOWN (' + value + ')][.TODO = eps][.BASE = BASE_VALUE (KNOWN PNULL)]')]
        for label, replacement in mutations:
            state = 'S_peer_coalesce_nan_' + label
            guards += [state + ' = ' + replacement,
                       '$string_read_runtime_instanceof_operand(' + state + ', ' + origin + ') = eps',
                       '$string_read_runtime_bytes(' + state + ', porigin_key) = eps',
                       '$string_read_request_base_saved(' + state + ', pstringread) = eps']
        for label, replacement in (
            ('right_drop', 'S_after[.CODE[0] = pcode_peer_coalesce_nan[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_coalesce_nan.EXPRESSIONS, ' + target + '_1, eps)]]'),
            ('right_precision', 'S_after[.POOLS[0] = ppool_peer_coalesce_nan[.CONSTANTS = (PCCPRECISION ' + target + '_1 17) :: ppool_peer_coalesce_nan.CONSTANTS]]'),
            ('live_precision', 'S_after[.PRECISIONINI = $ptascii("17")][.PRECISIONMODIFIED = true]'),
            ('cached_other', 'S_after[.RESULT = KNOWN (PINT 77)]'),
        ):
            state = 'S_peer_coalesce_nan_' + label
            guards += [state + ' = ' + replacement,
                       '$string_read_runtime_instanceof_operand(' + state + ', ' + origin + ') = (' + value + ')']
        if index == 0:
            guards += ['S_peer_coalesce_nan_equal_precision = S_after[.POOLS[0] = ppool_peer_coalesce_nan[.CONSTANTS = (PCCPRECISION ' + target + ' 17) :: (PCCPRECISION ' + target + '_0 17) :: ppool_peer_coalesce_nan.CONSTANTS]]',
                       '$string_read_runtime_instanceof_operand(S_peer_coalesce_nan_equal_precision, ' + origin + ') = (' + value + ')']
    if index == 0:
        for number, (name, fixture, original, target, node, accepted, nan) in enumerate(CONTROLS):
            state, origin = 'S_peer_coalesce_control_' + str(number), 'porigin_peer_coalesce_control_' + str(number)
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
    return checks + guards, derived + len(guards)


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    prep = output.with_name(output.name + '-control-prep')
    prep.mkdir(parents=True)
    emitted = '(NAN ?? (1/0))'
    raw = [
        ('nested_left', '', emitted + ' ?? missing_nan_default()', 'stdClass', True, True),
        ('cast_left', '', '((float)NAN) ?? missing_nan_default()', 'stdClass', True, True),
        ('arithmetic_left', '', '(1.0+NAN) ?? ($side=9)', 'stdClass', True, True),
        ('arithmetic_parent', '', '1.0+' + emitted, 'stdClass', True, True),
        ('unary_parent', '', '-' + emitted, 'stdClass', True, True),
        ('power_parent', '', '2.0**' + emitted, 'stdClass', True, True),
        ('cast_parent', '', '(float)' + emitted, 'stdClass', True, True),
        ('null_left_nan', '', 'null ?? NAN', 'stdClass', False, True),
        ('null_left_cast_nan', '', 'null ?? ((float)NAN)', 'stdClass', False, True),
        ('quiet_variable', '$left=NAN;', '$left ?? (1/0)', 'stdClass', False, True),
        ('alias_left', '', '((double)NAN) ?? 1', 'stdClass', False, True),
        ('leading_string', '', '("2junk"*NAN) ?? 1', 'stdClass', False, True),
        ('bad_string', '', '("no"*NAN) ?? 1', 'stdClass', False, True),
        ('zero_division', '', '(NAN/((float)(!INF))) ?? 1', 'stdClass', False, True),
        ('boolnot', '', '(!NAN) ?? 1', 'stdClass', False, False),
        ('int_cast', '', '((int)NAN) ?? 1', 'stdClass', False, False),
        ('general_plan', '', '(2.0**(((float)(!0.0))/2.0)) ?? 1', 'stdClass', False, False),
        ('late_namespace_nan', 'namespace Ns;', 'NAN ?? (1/0)', 'namespace\\Missing', False, True),
        ('fqn_namespace_nan', 'namespace Ns;', '\\NAN ?? (1/0)', 'namespace\\Missing', True, True),
        ('false_fallback', '', 'false ?? NAN', 'stdClass', True, False),
        ('zero_fallback', '', '0.0 ?? NAN', 'stdClass', True, False),
        ('null_integer_fallback', '', 'null ?? 1', 'stdClass', True, False),
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
    report['scope'] = 'Four histories independently check exact nonnull NaN-left coalesce source/root/left CODE/read/positive-line/captured-precision and child/result bits under NORMAL. Both source children remain required; dropped RHS CODE or altered RHS precision retain the selected value, while full coalesce_result proves unchanged TODO and canonical BASE. Cached paused NaNs satisfying the lower fixed-state result still refuse; pending/throw/source/precision counterfacts refuse, and live precision/cached-other changes preserve exact selected bits. Twenty-two fresh checked-source source0 controls cover nested coalesce, cast/arithmetic lefts, arithmetic/unary/POWER/cast parents, skipped undefined-call/assignment RHS, null-left and quiet-CV refusal, alias/leading/bad-string/zero-division/warningful truth/int/GENERAL boundaries, FQN versus late namespace, and genuine false/zero/null-to-integer fallbacks. General VALUE/BYTE/truth/compiler/numeric/formatter/owners/lifetimes and every exact hold are unchanged; fixture source0/native0.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
