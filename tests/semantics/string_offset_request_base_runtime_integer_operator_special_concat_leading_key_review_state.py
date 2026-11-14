#!/usr/bin/env python3
"""Independent integer operator authority, type and completion controls."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import source_occurrences as occurrences
import string_offset_request_base_float_boolnot_special_concat_leading_key_review_state as prior
import string_offset_request_base_runtime_integer_operator_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_integer_operator_special_concat_leading_key_protocol as source

runner = source.runner
RESULTS, KEYS = ('1', '$(-1)', '0', '$(-4)'), ('1x', '-1x', '0x', '-4x')
CONTROLS = []


def nodes(tree, tag='operator'):
    yield tag, tree[0] == 'FLOAT'
    if tree[0] != 'FLOAT':
        for index, child in enumerate(tree[1:3] if tree[0] in ('ADD', 'SUBTRACT', 'MULTIPLY') else tree[1:2]):
            yield from nodes(child, tag + '_' + str(index))


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    guards = ['pcode_peer_op = S_after.CODE[0]', 'pcode_peer_op.UNIT = 0',
              'ppool_peer_op = S_after.POOLS[0]', 'ppool_peer_op.UNIT = 0',
              'pcunit_peer_op = S_after.SOURCES[0]', 'pcunit_peer_op.ID = 0',
              '$string_read_runtime_value(S_after, porigin_operator) = (PINT ' + RESULTS[index] + ')',
              '$string_read_runtime_bytes(S_after, porigin_key) = ($ptascii(' + json.dumps(KEYS[index]) + '))']
    for tag, leaf in [('key', False), ('runtime_concat', False), *nodes(source.TREES[index])]:
        origin, target = 'porigin_' + tag, 'pcpath_peer_' + tag
        guards.append(origin + ' = PORIGIN 0 ' + target)
        states = [
            ('drop', 'S_after[.CODE[0] = pcode_peer_op[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_op.EXPRESSIONS, ' + target + ', eps)]]'),
            ('flip', 'S_after[.CODE[0] = pcode_peer_op[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_op.EXPRESSIONS, ' + target + ', (' + str(not leaf).lower() + '))]]'),
            ('precision', 'S_after[.POOLS[0] = ppool_peer_op[.CONSTANTS = (PCCPRECISION ' + target + ' 17) :: ppool_peer_op.CONSTANTS]]'),
            ('source', 'S_after[.SOURCES[0] = pcunit_peer_op[.OCCURRENCES = (PCOCCURRENCE ' + target + ' (NExprVariable (BYTES "dW5hdXRo") eps)) :: pcunit_peer_op.OCCURRENCES]]')]
        for label, value in states:
            state = 'S_peer_' + tag + '_' + label
            guards += [state + ' = ' + value,
                       ('$compiled_precision(' + state + ', (' + origin + ')) = (17)' if label == 'precision' else
                        '$compiled_read(' + state + ', ' + origin + ') = eps') if label != 'source' else
                       '$string_read_runtime_value(' + state + ', porigin_operator) = ' +
                       ('(PINT ' + RESULTS[index] + ')' if tag in ('key', 'runtime_concat') else 'eps'),
                       '$string_read_runtime_bytes(' + state + ', porigin_key) = eps',
                       '$string_read_request_base_saved(' + state + ', pstringread) = eps']
    if index == 2:
        guards += ['porigin_operator_0_0_0 = PORIGIN 0 pcpath_peer_inf']
        for label, value in (('nan', 'PFLOAT 9221120237041090560'), ('negative_nan', 'PFLOAT 18444492273895866368'),
                             ('payload_nan', 'PFLOAT 9221120237041090561'), ('invalid', 'PFLOAT 18446744073709551616'),
                             ('integer', 'PINT 0'), ('boolean', 'PBOOL false'), ('null', 'PNULL')):
            state = 'S_peer_op_' + label
            guards += [state + ' = S_after[.POOLS[0] = ppool_peer_op[.CONSTANTS = (PCONSTANT pcpath_peer_inf (' + value + ')) :: ppool_peer_op.CONSTANTS]]',
                       '$compiled_read(' + state + ', porigin_operator_0_0_0) = (' + value + ')']
            if 'nan' in label:
                guards += ['$compiled_identity_value(' + state + ', porigin_operator_0_0_0) = (' + value + ')',
                           '$number_bool(NFLOAT ' + value.split()[1] + ') = (true, true)']
            guards += ['$string_read_runtime_value(' + state + ', porigin_operator) = eps',
                       '$string_read_request_base_saved(' + state + ', pstringread) = eps']
    if index == 3:
        guards += [
            'S_peer_bit_budget = S_after[.COMPLETION = BUDGET][.RESULT = KNOWN (PINT 99)]',
            '$long_not(3) = $(-4)',
            '$bitnot_apply(S_peer_bit_budget, PINT 3, 5) = S_peer_bit_budget',
            '$bitnot_value(S_peer_bit_budget, PINT 3, 5) = S_peer_bit_budget[.RESULT = KNOWN (PINT $(-4))]',
            '$string_read_runtime_value(S_peer_bit_budget, porigin_operator_0) = (PINT 3)',
            '$string_read_runtime_value(S_peer_bit_budget, porigin_operator) = (PINT $(-4))',
            '$string_read_runtime_bytes(S_peer_bit_budget, porigin_key) = ($ptascii("-4x"))']
    if index == 0:
        for number, (name, fixture, control, target, node) in enumerate(CONTROLS):
            state, origin, child = 'S_peer_control_' + str(number), 'porigin_peer_control_' + str(number), 'porigin_peer_control_child_' + str(number)
            guards += [state + ' = $php_run(' + fixture + ', 0, ' + json.dumps(base64.b64encode(bytes(control)).decode()) + ')',
                       state + '.COMPLETION = BUDGET', origin + ' = PORIGIN 0 ' + occurrences.path_term(target),
                       '$origin_node(' + state + '.SOURCES, ' + origin + ') = (' + occurrences.node_term(node) + ')',
                       origin + ' = PORIGIN 0 pcpath_peer_control_' + str(number),
                       '$code_at(' + state + '.CODE, 0) = (pcode_peer_control_' + str(number) + ')',
                       '$code_expression(pcode_peer_control_' + str(number) + '.EXPRESSIONS, pcpath_peer_control_' + str(number) + ') = ((1, false))',
                       '$compiled_read(' + state + ', ' + origin + ') = eps',
                       '$origin_child((' + origin + '), [PCFIELD 0]) = (' + child + ')']
            if name == 'float':
                guards += ['$string_read_runtime_value(' + state + ', ' + child + ') = (PFLOAT 0)',
                           '$coerce_number(PFLOAT 0) = COERCED (NFLOAT 0) false',
                           '$binary_apply(' + state + ', ADD, PFLOAT 0, PINT 0, 1) = ' + state + '[.RESULT = KNOWN (PFLOAT 0)]']
            elif name == 'bool':
                guards += ['$string_read_runtime_value(' + state + ', ' + child + ') = (PBOOL true)',
                           '$coerce_number(PBOOL true) = COERCED (NINT 1) false']
            else:
                guards += ['$string_read_runtime_value(' + state + ', ' + child + ') = (PINT 4294967296)',
                           '$origin_child((' + origin + '), [PCFIELD 1]) = (' + child + '_r)',
                           '$string_read_runtime_value(' + state + ', ' + child + '_r) = (PINT 2147483648)',
                           '$binary_apply(' + state + ', MULTIPLY, PINT 4294967296, PINT 2147483648, 1) = ' + state + '[.RESULT = KNOWN (PFLOAT 4890909195324358656)]']
            guards += ['$string_read_runtime_value(' + state + ', ' + origin + ') = eps',
                       '$string_read_runtime_bytes(' + state + ', ' + origin + ') = eps']
    return checks + guards, derived + len(guards)


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    prep = output.with_name(output.name + '-control-prep')
    prep.mkdir(parents=True)
    factor = '((!0.0)+(!0.0))'
    factors = [factor] * 63
    while len(factors) > 1:
        factors = ['(' + factors[i] + '*' + factors[i + 1] + ')' if i + 1 < len(factors) else factors[i]
                   for i in range(0, len(factors), 2)]
    raw = {'float': (b"<?php $x=((0.0+(+(!INF))).null).'x';\n", 'Expr_BinaryOp_Plus'),
           'bool': (b"<?php $x=((~(!0.0)).false).'x';\n", 'Expr_BitwiseNot'),
           'overflow': (("<?php $x=((" + factors[0] + ").false).'x';\n").encode(), 'Expr_BinaryOp_Mul')}
    paths = {name: prep / (name + '.php') for name in raw}
    for name, path in paths.items():
        path.write_bytes(raw[name][0])
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
    for name, row in parsed.items():
        targets = [(path, node) for index, statement in enumerate(row['ast']['program'])
                   for path, node in occurrences.expected(statement, [('INDEX', index)]) if node['node'] == raw[name][1]]
        target, node = min(targets, key=lambda item: len(item[0]))
        CONTROLS.append((name, checked[name]['fixture'], paths[name], target, node))
    watched = {Path(module.__file__).resolve() for module in tuple(sys.modules.values()) if getattr(module, '__file__', None)
               and Path(module.__file__).resolve().parent == Path(__file__).resolve().parent} | set(paths.values())
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.PREFIX += prior.HELPERS
    runner.cases, runner.OUTPUTS, runner.conditions = cases, tuple(cases.OUTPUTS.values()), conditions
    passed = runner.main()
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = ('Four actual integer-operator histories retain exact author prefixes and add per-node source/CODE/precision '
                       'and typed-leaf controls. A source-reached budget state with RESULT99 distinguishes pure bitnot_value '
                       'from its NORMAL wrapper. Three separately parsed/checked compiler controls reject runtime FLOAT '
                       'arithmetic, BOOL BITNOT despite numeric coercion, and genuine 2^63 FLOAT overflow. These controls '
                       'add source0/native0; no compiled-PINT base, FLOAT formatter, owner/compiler/schema changes or '
                       'accepted source/native replay is claimed.')
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
