#!/usr/bin/env python3
"""Independent canonical FLOAT-cast NaN identity and descent controls."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import source_occurrences as occurrences
import string_offset_request_base_float_boolnot_special_concat_leading_key_review_state as helpers
import string_offset_request_base_runtime_float_cast_nan_instanceof_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_float_cast_nan_instanceof_special_concat_leading_key_protocol as source

runner = source.runner
CONTROLS = []


def links(tree, tag='operator'):
    yield tag, tree
    if tree[0] == 'NAN':
        children = tree[2:] if tree[1] in ('CASTFLOAT', 'POWER') else tree[3:] if tree[1] in ('EMITTED', 'UNARY') else ()
    elif tree[0] in ('FLOAT', 'STRING', 'COMPILED'):
        children = ()
    else:
        children = tree[2:3] if tree[0] == 'CAST' else tree[1:3] if tree[0] in ('IDENTICAL', 'ADD') else tree[1:2]
    for index, child in enumerate(children):
        yield from links(child, tag + '_' + str(index))


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    guards = ['pcode_peer_cast_nan = S_after.CODE[0]', 'ppool_peer_cast_nan = S_after.POOLS[0]',
              'pcunit_peer_cast_nan = S_after.SOURCES[0]']
    for tag, tree in links(source.TREES[index]):
        if tree[:2] != ('NAN', 'CASTFLOAT'):
            continue
        origin, target = 'porigin_' + tag, 'pcpath_peer_cast_nan'
        value = source.value([], tag, tree)[0]
        child_value = source.value([], tag + '_0', tree[2])[0]
        guards += [origin + ' = PORIGIN 0 ' + target,
                   '$origin_node(S_after.SOURCES, ' + origin + ') = (NExprCastDouble expression_peer_cast_child metadata_peer_cast)',
                   '$pplist_meta_kind(metadata_peer_cast) = 2',
                   '$compiled_read(S_after, ' + origin + ') = eps',
                   '$compiled_identity_value(S_after, ' + origin + ') = eps',
                   value.removeprefix('PFLOAT ') + ' = ' + child_value.removeprefix('PFLOAT '),
                   '$string_read_runtime_instanceof_operand(S_after, ' + origin + ') = (' + value + ')',
                   '$cast_apply(S_after, CASTFLOAT, ' + child_value + ', 5) = S_after[.RESULT = KNOWN (' + value + ')]',
                   '$string_read_runtime_value(S_after, ' + origin + ') = eps',
                   '$string_read_runtime_bytes(S_after, ' + origin + ') = eps',
                   '$number_bool(' + value.replace('PFLOAT', 'NFLOAT', 1) + ') = (true, true)',
                   '$truth_value(S_after, ' + value + ', 5) =/= S_after[.RESULT = KNOWN (PBOOL true)]',
                   'S_peer_cast_nan_paused = S_after[.COMPLETION = BUDGET][.RESULT = KNOWN (' + value + ')]',
                   '$cast_apply(S_peer_cast_nan_paused, CASTFLOAT, ' + child_value + ', 5) = S_peer_cast_nan_paused',
                   '$string_read_runtime_instanceof_operand(S_peer_cast_nan_paused, ' + origin + ') = eps',
                   '$string_read_runtime_bytes(S_peer_cast_nan_paused, porigin_key) = eps']
        mutations = [
            ('drop', 'S_after[.CODE[0] = pcode_peer_cast_nan[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_cast_nan.EXPRESSIONS, ' + target + ', eps)]]'),
            ('flip', 'S_after[.CODE[0] = pcode_peer_cast_nan[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_cast_nan.EXPRESSIONS, ' + target + ', (true))]]'),
            ('line', 'S_after[.CODE[0] = pcode_peer_cast_nan[.EXPRESSIONS = (CODEEXPR ' + target + ' 0 false) :: pcode_peer_cast_nan.EXPRESSIONS]]'),
            ('child_drop', 'S_after[.CODE[0] = pcode_peer_cast_nan[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_cast_nan.EXPRESSIONS, ' + target + '_0, eps)]]'),
        ]
        for label, metadata in (('alias', '([(Mkind 1)])'), ('missing_kind', 'eps'), ('wrong_kind', '([(Mkind 3)])')):
            mutations += [(label, 'S_after[.SOURCES[0] = pcunit_peer_cast_nan[.OCCURRENCES = (PCOCCURRENCE ' + target + ' (NExprCastDouble expression_peer_cast_child ' + metadata + ')) :: pcunit_peer_cast_nan.OCCURRENCES]]')]
        for suffix in ('', '_0'):
            child_path = target + suffix
            guards += ['porigin_' + tag + suffix + ' = PORIGIN 0 ' + child_path]
            mutations += [('precision' + suffix, 'S_after[.POOLS[0] = ppool_peer_cast_nan[.CONSTANTS = (PCCPRECISION ' + child_path + ' 17) :: ppool_peer_cast_nan.CONSTANTS]]'),
                          ('source' + suffix, 'S_after[.SOURCES[0] = pcunit_peer_cast_nan[.OCCURRENCES = (PCOCCURRENCE ' + child_path + ' (NExprVariable (BYTES "dW5hdXRo") eps)) :: pcunit_peer_cast_nan.OCCURRENCES]]')]
        for label, completion in (('pending', 'SOURCE_PENDING'), ('throw', 'THROWN "Error" ($ptascii("peer_cast")) 5')):
            mutations += [(label, 'S_after[.COMPLETION = ' + completion + '][.RESULT = KNOWN (' + value + ')]')]
        for label, replacement in mutations:
            state = 'S_peer_cast_nan_' + label
            guards += [state + ' = ' + replacement,
                       '$string_read_runtime_instanceof_operand(' + state + ', ' + origin + ') = eps',
                       '$string_read_runtime_bytes(' + state + ', porigin_key) = eps',
                       '$string_read_request_base_saved(' + state + ', pstringread) = eps']
        guards += ['S_peer_cast_nan_live_precision = S_after[.PRECISIONINI = $ptascii("17")][.PRECISIONMODIFIED = true]',
                   '$string_read_runtime_instanceof_operand(S_peer_cast_nan_live_precision, ' + origin + ') = (' + value + ')']
        if index == 0:
            guards += ['S_peer_cast_nan_equal_precision = S_after[.POOLS[0] = ppool_peer_cast_nan[.CONSTANTS = (PCCPRECISION ' + target + ' 17) :: (PCCPRECISION ' + target + '_0 17) :: ppool_peer_cast_nan.CONSTANTS]]',
                       '$string_read_runtime_instanceof_operand(S_peer_cast_nan_equal_precision, ' + origin + ') = (' + value + ')']
    if index == 0:
        for number, (name, fixture, original, target, node, accepted, nan) in enumerate(CONTROLS):
            state, origin = 'S_peer_cast_control_' + str(number), 'porigin_peer_cast_control_' + str(number)
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
    emitted = '((float)NAN)'
    raw = [
        ('nested_cast', '', '(float)' + emitted, 'stdClass', True, True),
        ('arithmetic_child', '', '(float)(1.0+NAN)', 'stdClass', True, True),
        ('unary_child', '', '(float)(-NAN)', 'stdClass', True, True),
        ('power_child', '', '(float)(NAN**((float)(!0.0)))', 'stdClass', True, True),
        ('arithmetic_parent', '', '1.0+' + emitted, 'stdClass', True, True),
        ('unary_parent', '', '-' + emitted, 'stdClass', True, True),
        ('power_parent', '', '2.0**' + emitted, 'stdClass', True, True),
        ('quiet_string', '', '(float)("2"*NAN)', 'stdClass', True, True),
        ('alias', '', '(double)NAN', 'stdClass', False, True),
        ('nested_alias', '', '(float)((double)NAN)', 'stdClass', False, True),
        ('leading_string', '', '(float)("2junk"*NAN)', 'stdClass', False, True),
        ('bad_string', '', '(float)("no"*NAN)', 'stdClass', False, True),
        ('zero_division', '', '(float)(NAN/((float)(!INF)))', 'stdClass', False, True),
        ('boolnot', '', '(float)(!NAN)', 'stdClass', False, False),
        ('int_cast', '', '(float)((int)NAN)', 'stdClass', False, False),
        ('general_plan', '', '(float)(2.0**(((float)(!0.0))/2.0))', 'stdClass', False, False),
        ('deprecated_plan', '', '(float)(0.0**(-((float)(!0.0))))', 'stdClass', False, False),
        ('late_namespace_nan', 'namespace Ns;', '(float)NAN', 'namespace\\Missing', False, True),
        ('fqn_namespace_nan', 'namespace Ns;', '(float)\\NAN', 'namespace\\Missing', True, True),
        ('finite_fallback', '', '(float)((float)(!INF))', 'stdClass', True, False),
        ('integer_fallback', '', '(float)1', 'stdClass', True, False),
        ('dynamic_child', '$left=NAN;', '(float)$left', 'stdClass', False, True),
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
    report['scope'] = 'Four current histories independently check canonical FLOAT-cast NaN root/child source, exact child/result bits, kind2 versus alias/missing/wrong kind, false CODE/read-eps/positive line, both captured precisions and whole quiet cast state. Pending/throw/cached-paused-NaN refuse; live precision changes preserve captured authority and matching alternate captured precision passes for the compiled child. Twenty-two fresh checked-source source0 controls cover nested casts, arithmetic/unary/POWER children and parents, quiet versus leading/bad strings, division zero, general/deprecated plans, alias-child descent, warningful truth/int casts, dynamic and late namespace operands, FQN and finite/integer fallbacks. General VALUE/BYTE, warningful truth, compiler/numeric/formatter/owners/lifetimes and every exact hold are unchanged; fixture source0/native0.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
