#!/usr/bin/env python3
"""Independent weak NaN equality, scalar dispatch and legacy-budget controls."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import source_occurrences as occurrences
import string_offset_request_base_float_boolnot_special_concat_leading_key_review_state as helpers
import string_offset_request_base_runtime_nan_equality_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_nan_equality_special_concat_leading_key_protocol as source

runner = source.runner
CONTROLS = []
FOLDED = {'same_nan', 'different_nan', 'negative_nan', 'finite_nan', 'nan_integer',
          'integer_nan', 'nan_null', 'string_nan', 'fqn_namespace',
          'mixed_numeric', 'mixed_numeric_neq'}


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
        children = tree[2:3] if tree[0] == 'CAST' else tree[1:3] if tree[0] in ('IDENTICAL', 'NOTIDENTICAL', 'EQUAL', 'NOTEQUAL', 'ADD', 'COALESCE') else tree[1:2]
    for index, child in enumerate(children):
        yield from links(child, tag + '_' + str(index))


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    guards = ['pcode_peer_nan_equality = S_after.CODE[0]', 'ppool_peer_nan_equality = S_after.POOLS[0]',
              'pcunit_peer_nan_equality = S_after.SOURCES[0]']
    for tag, tree in links(source.TREES[index]):
        if tree[0] not in ('EQUAL', 'NOTEQUAL') or not any(child[0] == 'NAN' for child in tree[1:3]):
            continue
        origin, target = 'porigin_' + tag, 'pcpath_peer_nan_equality'
        value = source.value([], tag, tree)[0]
        children = [source.value([], tag + '_' + str(i), child)[0] for i, child in enumerate(tree[1:3])]
        paused = 'S_peer_nan_equality_budget'
        guards += [origin + ' = PORIGIN 0 ' + target,
                   '$compiled_read(S_after, ' + origin + ') = eps',
                   '$compiled_identity_value(S_after, ' + origin + ') = eps',
                   '$string_read_runtime_value(S_after, ' + origin + ') = (' + value + ')',
                   '$string_read_runtime_bytes(S_after, ' + origin + ') = ($echo_value(' + value + '))',
                   '$strict_identical(' + value + ', PINT 0) = false',
                   paused + ' = S_after[.COMPLETION = BUDGET][.RESULT = KNOWN (' + value + ')][.TODO = eps]',
                   '$binary_apply(' + paused + ', ' + tree[0] + ', ' + children[0] + ', ' + children[1] + ', 5) = ' + paused + '[.RESULT = KNOWN (' + value + ')]',
                   '$string_read_runtime_value(' + paused + ', ' + origin + ') = eps']
        for i, child in enumerate(tree[1:3]):
            if child[0] == 'NAN':
                guards += ['$string_read_runtime_value(S_after, porigin_' + tag + '_' + str(i) + ') = eps',
                           '$string_read_runtime_bytes(S_after, porigin_' + tag + '_' + str(i) + ') = eps',
                           '$number_bool(' + children[i].replace('PFLOAT', 'NFLOAT', 1) + ') = (true, true)',
                           '$truth_value(S_after, ' + children[i] + ', 5) =/= S_after[.RESULT = KNOWN (PBOOL true)]']
        if index >= 2:
            continue
        mutations = [('line', 'S_after[.CODE[0] = pcode_peer_nan_equality[.EXPRESSIONS = (CODEEXPR ' + target + ' 0 false) :: pcode_peer_nan_equality.EXPRESSIONS]]')]
        for suffix in ('', '_0', '_1'):
            child_path = target + suffix
            guards += ['porigin_' + tag + suffix + ' = PORIGIN 0 ' + child_path]
            mutations += [('drop' + suffix, 'S_after[.CODE[0] = pcode_peer_nan_equality[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_nan_equality.EXPRESSIONS, ' + child_path + ', eps)]]'),
                          ('source' + suffix, 'S_after[.SOURCES[0] = pcunit_peer_nan_equality[.OCCURRENCES = (PCOCCURRENCE ' + child_path + ' (NExprVariable (BYTES "dW5hdXRo") eps)) :: pcunit_peer_nan_equality.OCCURRENCES]]'),
                          ('precision' + suffix, 'S_after[.POOLS[0] = ppool_peer_nan_equality[.CONSTANTS = (PCCPRECISION ' + child_path + ' 17) :: ppool_peer_nan_equality.CONSTANTS]]')]
        mutations += [('flip', 'S_after[.CODE[0] = pcode_peer_nan_equality[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_nan_equality.EXPRESSIONS, ' + target + ', (true))]]')]
        for label, completion in (('pending', 'SOURCE_PENDING'), ('throw', 'THROWN "Error" ($ptascii("peer_nan_equality")) 5')):
            mutations += [(label, 'S_after[.COMPLETION = ' + completion + '][.RESULT = KNOWN (' + value + ')][.TODO = eps]')]
        for label, replacement in mutations:
            state = 'S_peer_nan_equality_' + label
            guards += [state + ' = ' + replacement,
                       '$string_read_runtime_value(' + state + ', ' + origin + ') = eps']
        guards += ['$string_read_runtime_bytes(S_peer_nan_equality_drop, porigin_key) = eps',
                   '$string_read_request_base_saved(S_peer_nan_equality_drop, pstringread) = eps']
        for label, replacement in (
            ('live_precision', 'S_after[.PRECISIONINI = $ptascii("19")][.PRECISIONMODIFIED = true]'),
            ('cached_other', 'S_after[.RESULT = KNOWN (PINT 77)]'),
        ):
            state = 'S_peer_nan_equality_' + label
            guards += [state + ' = ' + replacement,
                       '$string_read_runtime_value(' + state + ', ' + origin + ') = (' + value + ')']
        if index == 0:
            guards += ['$strict_identical(' + children[0] + ', ' + children[1] + ') = false',
                       '$scalar_order(S_after, ' + children[0] + ', ' + children[1] + ') = 0',
                       '$binary_apply(S_after, IDENTICAL, ' + children[0] + ', ' + children[1] + ', 5) = S_after[.RESULT = KNOWN (PBOOL false)]']
            leaf_tag = next(name for name, subtree in links(tree, tag) if subtree[:2] == ('NAN', 'CONSTANT'))
            leaf_origin, leaf_path = 'porigin_' + leaf_tag, 'pcpath_peer_nan_equality_leaf'
            guards += [leaf_origin + ' = PORIGIN 0 ' + leaf_path]
            for label, bits in (('quiet', 9221120237041090560), ('negative', 18444492273895866368),
                                ('payload', 9221120237041090561), ('signaling', 9218868437227405313)):
                state, raw_value = 'S_peer_nan_equality_' + label, 'PFLOAT ' + str(bits)
                guards += [state + ' = S_after[.POOLS[0] = ppool_peer_nan_equality[.CONSTANTS = (PCONSTANT ' + leaf_path + ' (' + raw_value + ')) :: ppool_peer_nan_equality.CONSTANTS]]',
                           '$compiled_identity_value(' + state + ', ' + leaf_origin + ') = (' + raw_value + ')',
                           '$pfcast_nan(' + raw_value + ')',
                           '$strict_identical(' + raw_value + ', ' + raw_value + ') = false',
                           '$string_read_runtime_value(' + state + ', ' + origin + ') = (' + value + ')']
            guards += ['S_peer_nan_equality_invalid = S_after[.POOLS[0] = ppool_peer_nan_equality[.CONSTANTS = (PCONSTANT ' + leaf_path + ' (PFLOAT 18446744073709551616)) :: ppool_peer_nan_equality.CONSTANTS]]',
                       '$compiled_identity_value(S_peer_nan_equality_invalid, ' + leaf_origin + ') = eps',
                       '$string_read_runtime_value(S_peer_nan_equality_invalid, ' + origin + ') = eps']
    if index == 0:
        for number, (name, fixture, original, target, node, normal_result, budget_result) in enumerate(CONTROLS):
            state, origin = 'S_peer_nan_equality_control_' + str(number), 'porigin_peer_nan_equality_control_' + str(number)
            normal = state + '_normal'
            outcome = lambda result: 'eps' if result is None else '(PBOOL ' + str(result).lower() + ')'
            guards += [state + ' = $php_run(' + fixture + ', 0, ' + json.dumps(base64.b64encode(bytes(original)).decode()) + ')',
                       state + '.COMPLETION = BUDGET', origin + ' = PORIGIN 0 ' + occurrences.path_term(target),
                       '$origin_node(' + state + '.SOURCES, ' + origin + ') = (' + occurrences.node_term(node) + ')',
                       '$string_read_runtime_value(' + state + ', ' + origin + ') = ' + outcome(budget_result),
                       normal + ' = ' + state + '[.COMPLETION = NORMAL]',
                       '$string_read_runtime_value(' + normal + ', ' + origin + ') = ' + outcome(normal_result),
                       '$string_read_runtime_value(' + state + '[.RESULT = KNOWN (PBOOL false)], ' + origin + ') = ' + outcome(budget_result)]
            if normal_result is not None:
                guards += ['$string_read_runtime_bytes(' + normal + ', ' + origin + ') = ($echo_value(PBOOL ' + str(normal_result).lower() + '))']
            if name in FOLDED:
                folded = '(PBOOL ' + str(normal_result).lower() + ')'
                guards += ['$compiled_read(' + state + ', ' + origin + ') = ' + folded,
                           '$compiled_identity_value(' + state + ', ' + origin + ') = ' + folded]
            if name in ('mixed_numeric', 'mixed_numeric_neq'):
                guards += ['$strict_identical(PINT 1, PFLOAT 4607182418800017408) = false',
                           '$scalar_order(' + normal + ', PINT 1, PFLOAT 4607182418800017408) = 0']
            if name in ('nan_bool', 'nan_not_bool'):
                left, right, bits = origin + '_left', origin + '_right', 'n_peer_nan_equality_control_' + str(number)
                operation = 'EQUAL' if name == 'nan_bool' else 'NOTEQUAL'
                guards += ['$compiled_read(' + state + ', ' + origin + ') = eps',
                           '$origin_child((' + origin + '), [PCFIELD 0]) = (' + left + ')',
                           '$origin_child((' + origin + '), [PCFIELD 1]) = (' + right + ')',
                           '$string_read_runtime_instanceof_operand(' + state + ', ' + left + ') = (PFLOAT ' + bits + ')',
                           '$pfcast_nan(PFLOAT ' + bits + ')',
                           '$string_read_runtime_instanceof_operand(' + state + ', ' + right + ') = (PBOOL true)',
                           '$binary_apply(' + state + ', ' + operation + ', PFLOAT ' + bits + ', PBOOL true, 1) = ' + state + '[.RESULT = KNOWN (PBOOL ' + str(normal_result).lower() + ')]']
    return checks + guards, derived + len(guards)


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    prep = output.with_name(output.name + '-control-prep')
    prep.mkdir(parents=True)
    emitted = '(((!INF) ? true : null) ?? NAN)'
    raw = [
        ('same_nan', '', 'NAN==NAN', False, False),
        ('different_nan', '', 'NAN!=NAN', True, True),
        ('negative_nan', '', 'NAN==(-NAN)', False, False),
        ('finite_nan', '', '1.0==NAN', False, False),
        ('nan_integer', '', 'NAN==0', False, False),
        ('integer_nan', '', '0==NAN', False, False),
        ('nan_bool', '', 'NAN==(!0.0)', True, None),
        ('nan_not_bool', '', 'NAN!=(!0.0)', False, None),
        ('nan_null', '', 'NAN==null', False, False),
        ('string_nan', '', '""==NAN', False, False),
        ('recursive_nan', '', emitted + '==NAN', False, None),
        ('reversed_recursive', '', 'NAN!=(' + emitted + ' ?? (1/0))', True, None),
        ('arithmetic_cast', '', '(((float)(!INF))-NAN)==((float)NAN)', False, None),
        ('emitted_false', '', emitted + '==false', False, None),
        ('emitted_null', '', emitted + '==null', False, None),
        ('emitted_numeric_string', '', emitted + '=="0"', False, None),
        ('emitted_nan_string', '', emitted + '=="NAN"', False, None),
        ('reversed_emitted_string', '', '"NAN"==' + emitted, False, None),
        ('emitted_bool_neq', '', emitted + '!=true', False, None),
        ('warningful', '', '(!NAN)==false', None, None),
        ('alias', '', '((double)NAN)==NAN', None, None),
        ('zero_division', '', '(NAN/((float)(!INF)))==NAN', None, None),
        ('quiet_variable', '$left=NAN;', '$left==NAN', None, None),
        ('late_namespace', 'namespace Ns;', 'NAN==\\NAN', None, None),
        ('fqn_namespace', 'namespace Ns;', '\\NAN==\\NAN', False, False),
        ('mixed_numeric', '', '1==1.0', True, True),
        ('mixed_numeric_neq', '', '1!=1.0', False, False),
        ('legacy_boolean', '', '(!0.0)==(!INF)', False, False),
        ('legacy_integer', '', '(!0.0)==(+(!0.0))', True, True),
        ('legacy_reversed', '', '(+(!0.0))!=(!0.0)', False, False),
    ]
    paths = {name: prep / (name + '.php') for name, *_ in raw}
    for name, prefix, expression, normal_result, budget_result in raw:
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
    for name, prefix, expression, normal_result, budget_result in raw:
        target, node = next((path, node) for index, statement in enumerate(parsed[name]['ast']['program'])
                            for path, node in occurrences.expected(statement, [('INDEX', index)])
                            if node['node'] in ('Expr_BinaryOp_Equal', 'Expr_BinaryOp_NotEqual'))
        CONTROLS.append((name, checked[name]['fixture'], paths[name], target, node, normal_result, budget_result))
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
    report['scope'] = 'Three source-reached histories and one compiled-state root fixture independently check quiet NaN EQUAL/NOTEQUAL through exact source/CODE/read/precision and unchanged whole binary_apply. NaN==true differs from strict identity; generic NaN truth remains refused. Thirty fresh checked-source source0 controls distinguish eleven authenticated folded Boolean BUDGET positives, eleven genuine emitted NORMAL-only scalar comparisons, five unsupported producers and three legacy nonNaN BUDGET positives. Genuine emitted false/null/numeric-string/NAN-string/reversed-string partners exercise comparison-specific dispatch; mixed integer/float controls distinguish weak from strict equality. Direct NaN/Boolean controls retain both operands and lower binary_apply at BUDGET while the new emitted certificate refuses. Quiet/signed/payload/signaling substitutions target an actual selected NAN ConstFetch in the recursive operand; malformed64 bits refuse. Fourth uses the genuine checked Program/php_run0 compiled state only, with no callback/owner/bounds/resumption credit. General NaN VALUE/BYTE/truth, compiler33/numerics, legacy arms, owners/lifetimes and all exact holds remain unchanged. Source0/native0; saved native observations reused without execution.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
