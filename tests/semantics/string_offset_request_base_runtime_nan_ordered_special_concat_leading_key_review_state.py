#!/usr/bin/env python3
"""Independent typed NaN ordering, reversed dispatch and admission controls."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import source_occurrences as occurrences
import string_offset_request_base_float_boolnot_special_concat_leading_key_review_state as helpers
import string_offset_request_base_runtime_nan_ordered_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_nan_ordered_special_concat_leading_key_protocol as source

runner = source.runner
source_recorded = runner.recorded
OPERATORS = ('LESS', 'LESSEQUAL', 'GREATER', 'GREATEREQUAL', 'SPACESHIP')
CONTROLS = []
FOLDED = {'same_nan', 'finite_nan', 'nan_integer', 'nan_string', 'string_nan',
          'nan_null', 'null_nan', 'nan_true', 'false_nan', 'fqn_namespace'}


def recorded(command, stem, cap):
    return source_recorded(command, stem, 360)


def links(tree, tag='operator'):
    yield tag, tree
    if tree[:2] == ('NAN', 'SHORTHAND'):
        yield from links(tree[2], tag + '_0')
        yield from links(tree[3], tag + '_2')
        return
    if tree[0] == 'NAN':
        children = tree[2:] if tree[1] in ('NULLCOALESCE', 'COALESCE', 'CASTFLOAT', 'POWER') else tree[3:] if tree[1] in ('EMITTED', 'UNARY') else ()
    elif tree[0] in ('FLOAT', 'STRING', 'COMPILED', 'LITERAL_INT'):
        children = ()
    else:
        children = tree[2:3] if tree[0] == 'CAST' else tree[1:3] if tree[0] in (*OPERATORS, 'IDENTICAL', 'NOTIDENTICAL', 'EQUAL', 'NOTEQUAL', 'ADD', 'COALESCE') else tree[1:2]
    for index, child in enumerate(children):
        yield from links(child, tag + '_' + str(index))


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    guards = ['pcode_peer_nan_ordered = S_after.CODE[0]', 'ppool_peer_nan_ordered = S_after.POOLS[0]',
              'pcunit_peer_nan_ordered = S_after.SOURCES[0]']
    for tag, tree in links(source.TREES[index]):
        if tree[0] not in OPERATORS or not any(child[0] == 'NAN' for child in tree[1:3]):
            continue
        origin, target = 'porigin_' + tag, 'pcpath_peer_nan_ordered_' + tag
        value = source.value([], tag, tree)[0]
        children = [source.value([], tag + '_' + str(i), child)[0] for i, child in enumerate(tree[1:3])]
        prefix = 'S_peer_nan_ordered_' + tag
        paused = prefix + '_budget'
        guards += [origin + ' = PORIGIN 0 ' + target,
                   '$compiled_read(S_after, ' + origin + ') = eps',
                   '$compiled_identity_value(S_after, ' + origin + ') = eps',
                   '$string_read_runtime_value(S_after, ' + origin + ') = (' + value + ')',
                   '$string_read_runtime_bytes(S_after, ' + origin + ') = ($echo_value(' + value + '))',
                   '$strict_identical(' + value + ', ' + ('PBOOL true' if tree[0] == 'SPACESHIP' else 'PINT 0') + ') = false',
                   paused + ' = S_after[.COMPLETION = BUDGET][.RESULT = KNOWN (' + value + ')][.TODO = eps]',
                   '$binary_apply(' + paused + ', ' + tree[0] + ', ' + children[0] + ', ' + children[1] + ', 5) = ' + paused + '[.RESULT = KNOWN (' + value + ')]',
                   '$string_read_runtime_value(' + paused + ', ' + origin + ') = eps']
        for i, child in enumerate(tree[1:3]):
            if child[0] == 'NAN':
                guards += ['$string_read_runtime_value(S_after, porigin_' + tag + '_' + str(i) + ') = eps',
                           '$string_read_runtime_bytes(S_after, porigin_' + tag + '_' + str(i) + ') = eps',
                           '$number_bool(' + children[i].replace('PFLOAT', 'NFLOAT', 1) + ') = (true, true)',
                           '$truth_value(S_after, ' + children[i] + ', 5) =/= S_after[.RESULT = KNOWN (PBOOL true)]']
        forward = '-1' if children[0] in ('PBOOL false', 'PNULL') else '0' if 'PBOOL true' in children else '1'
        reverse = '-1' if children[1] in ('PBOOL false', 'PNULL') else '0' if 'PBOOL true' in children else '1'
        guards += ['$scalar_order(S_after, ' + children[0] + ', ' + children[1] + ') = ' + ('$(-1)' if forward == '-1' else forward),
                   '$scalar_order(S_after, ' + children[1] + ', ' + children[0] + ') = ' + ('$(-1)' if reverse == '-1' else reverse)]
        if index >= 2:
            continue
        mutations = [('line', 'S_after[.CODE[0] = pcode_peer_nan_ordered[.EXPRESSIONS = (CODEEXPR ' + target + ' 0 false) :: pcode_peer_nan_ordered.EXPRESSIONS]]')]
        for suffix in ('', '_0', '_1'):
            child_path = target + suffix
            guards += ['porigin_' + tag + suffix + ' = PORIGIN 0 ' + child_path]
            mutations += [('drop' + suffix, 'S_after[.CODE[0] = pcode_peer_nan_ordered[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_nan_ordered.EXPRESSIONS, ' + child_path + ', eps)]]'),
                          ('source' + suffix, 'S_after[.SOURCES[0] = pcunit_peer_nan_ordered[.OCCURRENCES = (PCOCCURRENCE ' + child_path + ' (NExprVariable (BYTES "dW5hdXRo") eps)) :: pcunit_peer_nan_ordered.OCCURRENCES]]'),
                          ('precision' + suffix, 'S_after[.POOLS[0] = ppool_peer_nan_ordered[.CONSTANTS = (PCCPRECISION ' + child_path + ' 17) :: ppool_peer_nan_ordered.CONSTANTS]]')]
        mutations += [('flip', 'S_after[.CODE[0] = pcode_peer_nan_ordered[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_nan_ordered.EXPRESSIONS, ' + target + ', (true))]]')]
        for label, completion in (('pending', 'SOURCE_PENDING'), ('throw', 'THROWN "Error" ($ptascii("peer_nan_ordered")) 5')):
            mutations += [(label, 'S_after[.COMPLETION = ' + completion + '][.RESULT = KNOWN (' + value + ')][.TODO = eps]')]
        for label, replacement in mutations:
            guards += [prefix + '_' + label + ' = ' + replacement,
                       '$string_read_runtime_value(' + prefix + '_' + label + ', ' + origin + ') = eps']
        guards += ['$string_read_runtime_bytes(' + prefix + '_drop, porigin_key) = eps',
                   '$string_read_request_base_saved(' + prefix + '_drop, pstringread) = eps']
        for label, replacement in (
            ('live_precision', 'S_after[.PRECISIONINI = $ptascii("19")][.PRECISIONMODIFIED = true]'),
            ('cached_other', 'S_after[.RESULT = KNOWN (PBOOL true)]'),
        ):
            guards += [prefix + '_' + label + ' = ' + replacement,
                       '$string_read_runtime_value(' + prefix + '_' + label + ', ' + origin + ') = (' + value + ')']
        if index == 0:
            leaf_tag = next(name for name, subtree in links(tree, tag) if subtree[:2] == ('NAN', 'CONSTANT'))
            leaf_origin, leaf_path = 'porigin_' + leaf_tag, 'pcpath_peer_nan_ordered_leaf'
            guards += [leaf_origin + ' = PORIGIN 0 ' + leaf_path]
            for label, bits in (('quiet', 9221120237041090560), ('negative', 18444492273895866368),
                                ('payload', 9221120237041090561), ('signaling', 9218868437227405313)):
                raw_value = 'PFLOAT ' + str(bits)
                guards += [prefix + '_' + label + ' = S_after[.POOLS[0] = ppool_peer_nan_ordered[.CONSTANTS = (PCONSTANT ' + leaf_path + ' (' + raw_value + ')) :: ppool_peer_nan_ordered.CONSTANTS]]',
                           '$compiled_identity_value(' + prefix + '_' + label + ', ' + leaf_origin + ') = (' + raw_value + ')',
                           '$pfcast_nan(' + raw_value + ')',
                           '$strict_identical(' + raw_value + ', ' + raw_value + ') = false',
                           '$string_read_runtime_value(' + prefix + '_' + label + ', ' + origin + ') = (' + value + ')']
            guards += [prefix + '_invalid = S_after[.POOLS[0] = ppool_peer_nan_ordered[.CONSTANTS = (PCONSTANT ' + leaf_path + ' (PFLOAT 18446744073709551616)) :: ppool_peer_nan_ordered.CONSTANTS]]',
                       '$compiled_identity_value(' + prefix + '_invalid, ' + leaf_origin + ') = eps',
                       '$string_read_runtime_value(' + prefix + '_invalid, ' + origin + ') = eps']
    if index == 0:
        for number, (name, fixture, original, target, node, result, budget) in enumerate(CONTROLS):
            state, origin = 'S_peer_nan_ordered_control_' + str(number), 'porigin_peer_nan_ordered_control_' + str(number)
            normal = state + '_normal'
            outcome = lambda value: 'eps' if value is None else '(' + value + ')'
            guards += [state + ' = $php_run(' + fixture + ', 0, ' + json.dumps(base64.b64encode(bytes(original)).decode()) + ')',
                       state + '.COMPLETION = BUDGET', origin + ' = PORIGIN 0 ' + occurrences.path_term(target),
                       '$origin_node(' + state + '.SOURCES, ' + origin + ') = (' + occurrences.node_term(node) + ')',
                       '$string_read_runtime_value(' + state + ', ' + origin + ') = ' + outcome(budget),
                       normal + ' = ' + state + '[.COMPLETION = NORMAL]',
                       '$string_read_runtime_value(' + normal + ', ' + origin + ') = ' + outcome(result),
                       '$string_read_runtime_value(' + state + '[.RESULT = KNOWN (PBOOL true)], ' + origin + ') = ' + outcome(budget)]
            if result is not None:
                guards += ['$string_read_runtime_bytes(' + normal + ', ' + origin + ') = ($echo_value(' + result + '))',
                           '$strict_identical(' + result + ', ' + ('PBOOL true' if result.startswith('PINT ') else 'PINT 0') + ') = false']
            if name in FOLDED:
                guards += ['$compiled_read(' + state + ', ' + origin + ') = (' + result + ')',
                           '$compiled_identity_value(' + state + ', ' + origin + ') = (' + result + ')']
            elif result is not None:
                guards += ['$compiled_read(' + state + ', ' + origin + ') = eps']
            if name in ('direct_nan_bool', 'direct_bool_nan'):
                left, right = origin + '_left', origin + '_right'
                bits = 'n_peer_nan_ordered_control_' + str(number)
                operands = ['PFLOAT ' + bits, 'PBOOL true'] if name == 'direct_nan_bool' else ['PBOOL false', 'PFLOAT ' + bits]
                operator = 'LESSEQUAL' if name == 'direct_nan_bool' else 'SPACESHIP'
                guards += ['$origin_child((' + origin + '), [PCFIELD 0]) = (' + left + ')',
                           '$origin_child((' + origin + '), [PCFIELD 1]) = (' + right + ')',
                           '$compiled_identity_value(' + state + ', ' + origin + ') = eps',
                           '$string_read_runtime_instanceof_operand(' + state + ', ' + left + ') = (' + operands[0] + ')',
                           '$string_read_runtime_instanceof_operand(' + state + ', ' + right + ') = (' + operands[1] + ')',
                           '$pfcast_nan(PFLOAT ' + bits + ')',
                           '$string_read_runtime_value(' + state + '[.RESULT = KNOWN (' + result + ')], ' + origin + ') = eps',
                           '$string_read_runtime_value(' + state + '[.RESULT = KNOWN (PINT 77)], ' + origin + ') = eps',
                           '$binary_apply(' + state + ', ' + operator + ', ' + operands[0] + ', ' + operands[1] + ', 1) = ' + state + '[.RESULT = KNOWN (' + result + ')]']
    return checks + guards, derived + len(guards)


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    prep = output.with_name(output.name + '-control-prep')
    prep.mkdir(parents=True)
    emitted = '(((!INF) ? true : null) ?? NAN)'
    raw = [
        ('same_nan', '', 'NAN<=>NAN', 'PINT 1', 'PINT 1'),
        ('finite_nan', '', '1.0<NAN', 'PBOOL false', 'PBOOL false'),
        ('nan_integer', '', 'NAN>0', 'PBOOL false', 'PBOOL false'),
        ('nan_string', '', 'NAN<=>"0"', 'PINT 1', 'PINT 1'),
        ('string_nan', '', '"NAN"<=>NAN', 'PINT 1', 'PINT 1'),
        ('nan_null', '', 'NAN<=>null', 'PINT 1', 'PINT 1'),
        ('null_nan', '', 'null<=>NAN', 'PINT $(-1)', 'PINT $(-1)'),
        ('nan_true', '', 'NAN<=>true', 'PINT 0', 'PINT 0'),
        ('false_nan', '', 'false<=>NAN', 'PINT $(-1)', 'PINT $(-1)'),
        ('fqn_namespace', 'namespace Ns;', '\\NAN<=>\\NAN', 'PINT 1', 'PINT 1'),
        ('emitted_spaceship', '', emitted + '<=>NAN', 'PINT 1', None),
        ('reversed_spaceship', '', 'NAN<=>(' + emitted + ' ?? (1/0))', 'PINT 1', None),
        ('emitted_less', '', emitted + '<NAN', 'PBOOL false', None),
        ('emitted_lessequal', '', emitted + '<=NAN', 'PBOOL false', None),
        ('emitted_greater', '', emitted + '>NAN', 'PBOOL false', None),
        ('emitted_greaterequal', '', emitted + '>=NAN', 'PBOOL false', None),
        ('emitted_true', '', emitted + '<true', 'PBOOL false', None),
        ('reversed_true', '', 'true>=' + emitted, 'PBOOL true', None),
        ('emitted_false', '', emitted + '>false', 'PBOOL true', None),
        ('reversed_false', '', 'false<' + emitted, 'PBOOL true', None),
        ('emitted_null', '', emitted + '<=null', 'PBOOL false', None),
        ('reversed_null', '', 'null<=' + emitted, 'PBOOL true', None),
        ('emitted_string', '', emitted + '>"0"', 'PBOOL false', None),
        ('reversed_string', '', '"NAN">=' + emitted, 'PBOOL false', None),
        ('direct_nan_bool', '', 'NAN<=(!0.0)', 'PBOOL true', None),
        ('direct_bool_nan', '', '(!INF)<=>NAN', 'PINT $(-1)', None),
        ('warningful', '', '(!NAN)<NAN', None, None),
        ('alias', '', '((double)NAN)<=>NAN', None, None),
        ('zero_division', '', '(NAN/((float)(!INF)))<=>NAN', None, None),
        ('quiet_variable', '$left=NAN;', '$left<=>NAN', None, None),
        ('late_namespace', 'namespace Ns;', 'NAN<=>\\NAN', None, None),
        ('legacy_boolean', '', '(!0.0)<(!INF)', 'PBOOL false', 'PBOOL false'),
        ('legacy_integer', '', '(+(!0.0))>(+(!INF))', 'PBOOL true', 'PBOOL true'),
    ]
    paths = {name: prep / (name + '.php') for name, *_ in raw}
    for name, prefix, expression, result, budget in raw:
        paths[name].write_bytes(('<?php ' + prefix + '$x=(' + expression + ');\n').encode())
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
    for name, prefix, expression, result, budget in raw:
        target, node = next((path, node) for index, statement in enumerate(parsed[name]['ast']['program'])
                            for path, node in occurrences.expected(statement, [('INDEX', index)])
                            if node['node'] in ('Expr_BinaryOp_Smaller', 'Expr_BinaryOp_SmallerOrEqual', 'Expr_BinaryOp_Greater', 'Expr_BinaryOp_GreaterOrEqual', 'Expr_BinaryOp_Spaceship'))
        CONTROLS.append((name, checked[name]['fixture'], paths[name], target, node, result, budget))
    watched = {Path(module.__file__).resolve() for module in tuple(sys.modules.values()) if getattr(module, '__file__', None)
               and Path(module.__file__).resolve().parent == Path(__file__).resolve().parent} | set(paths.values())
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.PREFIX += helpers.HELPERS
    runner.recorded = recorded
    runner.cases, runner.OUTPUTS, runner.conditions = cases, tuple(cases.OUTPUTS.values()), conditions
    passed = runner.main()
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = 'Independent typed ordered-NaN fixtures preserve PINT spaceship versus PBOOL, both comparison directions, reversed Greater and full-state binary_apply at actual source-reached origins. Exact source/CODE/read/line/precision and NORMAL-only guards are checked without general NaN VALUE/BYTE/truth authority. Thirty-three fresh checked-source controls separate ten authenticated folded BUDGET positives, sixteen emitted NORMAL-only comparisons, five unsupported producers and two legacy nonNaN BUDGET positives. Two direct compiled-NaN/emitted-Boolean controls authenticate both operands and quiet binary_apply at BUDGET while the new outer certificate refuses, isolating its NORMAL guard; the reversed spaceship retains exact PINT-1. NaN numeric/string unordered +1, quiet BOOL/NULL compatibility and signed/payload/signaling/invalid-bit substitutions remain distinct. Fourth uses only its actual checked Program/php_run0 compiled key, with source0/native0 and no callback/owner/bounds/resumption credit. Old ordered/BUDGET/compiler/numeric/kernel and all exact holds remain unchanged; native observations are reused once.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
