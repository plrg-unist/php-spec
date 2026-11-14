#!/usr/bin/env python3
"""Independent compiled type, source, precision and BYTE disjointness controls."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import source_occurrences as occurrences
import string_offset_request_base_float_boolnot_special_concat_leading_key_review_state as helpers
import string_offset_request_base_runtime_compiled_primitive_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_compiled_primitive_special_concat_leading_key_protocol as source

runner = source.runner
CONTROLS = []


def links(tree, tag='operator'):
    yield tag, tree
    kind = tree[0]
    if kind in ('FLOAT', 'COMPILED'):
        return
    if kind in ('TERNARY', 'SHORTHAND'):
        children = [(0, tree[1])]
        if kind == 'TERNARY' or not tree[-1]:
            children.append((1 if kind == 'TERNARY' and tree[-1] else 2, tree[2]))
    else:
        children = enumerate(tree[1:3] if kind == 'IDENTICAL' else tree[1:2])
    for index, child in children:
        yield from links(child, tag + '_' + str(index))


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    guards = ['pcode_peer_primitive = S_after.CODE[0]', 'pcode_peer_primitive.UNIT = 0',
              'ppool_peer_primitive = S_after.POOLS[0]', 'ppool_peer_primitive.UNIT = 0',
              'pcunit_peer_primitive = S_after.SOURCES[0]', 'pcunit_peer_primitive.ID = 0']

    def refused(state):
        return ['$string_read_runtime_value(' + state + ', porigin_operator) = eps',
                '$string_read_runtime_bytes(' + state + ', porigin_key) = eps',
                '$string_read_request_base_saved(' + state + ', pstringread) = eps']

    for tag, tree in links(source.TREES[index]):
        origin = 'porigin_' + tag
        result = source.value([], tag, tree)[0]
        if tree[0] != 'COMPILED':
            if result == 'PNULL':
                guards += ['$compiled_read(S_after, ' + origin + ') = eps',
                           '$string_read_runtime_bytes(S_after, ' + origin + ') = (eps)']
            continue
        target = 'pcpath_peer_primitive_' + tag
        guards.append(origin + ' = PORIGIN 0 ' + target)
        mutations = [
            ('drop', 'S_after[.CODE[0] = pcode_peer_primitive[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_primitive.EXPRESSIONS, ' + target + ', eps)]]'),
            ('flip', 'S_after[.CODE[0] = pcode_peer_primitive[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_primitive.EXPRESSIONS, ' + target + ', (false))]]'),
            ('source', 'S_after[.SOURCES[0] = pcunit_peer_primitive[.OCCURRENCES = (PCOCCURRENCE ' + target + ' (NExprVariable (BYTES "dW5hdXRo") eps)) :: pcunit_peer_primitive.OCCURRENCES]]'),
            ('pools', 'S_after[.POOLS = eps]'),
            ('precision_missing', 'S_after[.DECLARATIONS = eps]'),
        ]
        for label, replacement in mutations:
            state = 'S_peer_primitive_' + tag + '_' + label
            guards.append(state + ' = ' + replacement)
            if label == 'flip' and not isinstance(tree[2], str):
                guards += ['$compiled_read(' + state + ', ' + origin + ') = eps',
                           '$string_read_runtime_value(' + state + ', ' + origin + ') = (' + result + ')',
                           '$string_read_runtime_bytes(' + state + ', ' + origin + ') = ($echo_value(' + result + '))',
                           '$string_read_runtime_value(' + state + ', porigin_operator) = $string_read_runtime_value(S_after, porigin_operator)',
                           '$string_read_runtime_bytes(' + state + ', porigin_key) = $string_read_runtime_bytes(S_after, porigin_key)',
                           '$string_read_request_base_saved(' + state + ', pstringread) = $string_read_request_base_saved(S_after, pstringread)']
            else:
                guards += ['$string_read_runtime_value(' + state + ', ' + origin + ') = eps', *refused(state)]
        for number, payload in enumerate(('PSTRING ($ptascii("1"))', 'PINT 9223372036854775808', 'PINT $(-9223372036854775809)')):
            state = 'S_peer_primitive_' + tag + '_pool_' + str(number)
            guards += [state + ' = S_after[.POOLS[0] = ppool_peer_primitive[.CONSTANTS = (PCONSTANT ' + target + ' (' + payload + ')) :: ppool_peer_primitive.CONSTANTS]]',
                       '$compiled_read(' + state + ', ' + origin + ') = (' + payload + ')',
                       '$string_read_runtime_value(' + state + ', ' + origin + ') = eps', *refused(state)]
        state = 'S_peer_primitive_' + tag + '_precision'
        guards += [state + ' = S_after[.POOLS[0] = ppool_peer_primitive[.CONSTANTS = (PCCPRECISION ' + target + ' 17) :: ppool_peer_primitive.CONSTANTS]]',
                   '$compiled_precision(' + state + ', (' + origin + ')) = (17)',
                   '$string_read_runtime_value(' + state + ', ' + origin + ') = (' + result + ')', *refused(state),
                   '$string_read_runtime_bytes(S_after, ' + origin + ') = ($echo_value(' + result + '))',
                   '$string_read_runtime_value(S_after[.RESULT = KNOWN (PINT 99)], ' + origin + ') = (' + result + ')',
                   '$string_read_runtime_bytes(S_after[.RESULT = KNOWN (PINT 99)], porigin_key) = $string_read_runtime_bytes(S_after, porigin_key)']
        for label, completion in (('budget', 'BUDGET'), ('pending', 'SOURCE_PENDING'),
                                  ('unsupported', 'UNSUPPORTED "peer_primitive"'), ('exited', 'EXITED 0'),
                                  ('thrown', 'THROWN "Error" ($ptascii("peer_primitive")) 5')):
            state = 'S_peer_primitive_' + tag + '_' + label
            guards += [state + ' = S_after[.COMPLETION = ' + completion + ']',
                       '$string_read_runtime_value(' + state + ', ' + origin + ') = (' + result + ')', *refused(state)]
    root_result = source.value([], 'operator', source.TREES[index])[0]
    guards += ['porigin_operator = PORIGIN 0 pcpath_peer_primitive_root',
               'S_peer_primitive_line = S_after[.CODE[0] = pcode_peer_primitive[.EXPRESSIONS = (CODEEXPR pcpath_peer_primitive_root 0 false) :: pcode_peer_primitive.EXPRESSIONS]]',
               *refused('S_peer_primitive_line'),
               'S_peer_primitive_ignored_pool = S_after[.POOLS[0] = ppool_peer_primitive[.CONSTANTS = (PCONSTANT pcpath_peer_primitive_root (PINT 99)) :: ppool_peer_primitive.CONSTANTS]]',
               '$compiled_read(S_peer_primitive_ignored_pool, porigin_operator) = eps',
               '$string_read_runtime_value(S_peer_primitive_ignored_pool, porigin_operator) = (' + root_result + ')',
               '$string_read_runtime_bytes(S_peer_primitive_ignored_pool, porigin_key) = $string_read_runtime_bytes(S_after, porigin_key)']
    if index == 0:
        for number, (name, fixture, original, target, node, pool_value, expected, emitted) in enumerate(CONTROLS):
            state, origin = 'S_peer_primitive_control_' + str(number), 'porigin_peer_primitive_control_' + str(number)
            target_name, pool = 'pcpath_peer_primitive_control_' + str(number), 'ppool_peer_primitive_control_' + str(number)
            output = 'eps' if expected is None else '(' + expected + ')'
            guards += [state + ' = $php_run(' + fixture + ', 0, ' + json.dumps(base64.b64encode(bytes(original)).decode()) + ')',
                       state + '.COMPLETION = BUDGET', origin + ' = PORIGIN 0 ' + occurrences.path_term(target),
                       '$origin_node(' + state + '.SOURCES, ' + origin + ') = (' + occurrences.node_term(node) + ')',
                       origin + ' = PORIGIN 0 ' + target_name,
                       '$code_at(' + state + '.CODE, 0) = (pcode_peer_primitive_control_' + str(number) + ')',
                       '$code_expression(pcode_peer_primitive_control_' + str(number) + '.EXPRESSIONS, ' + target_name + ') = ((1, ' + str(not emitted).lower() + '))',
                       '$compiled_read(' + state + ', ' + origin + ') = ' + ('eps' if emitted else '(' + pool_value + ')'),
                       '$compiled_precision(' + state + ', (' + origin + ')) = (14)',
                       '$string_read_runtime_value(' + state + ', ' + origin + ') = ' + ('eps' if emitted else output),
                       '$string_read_runtime_value(' + state + '[.COMPLETION = NORMAL], ' + origin + ') = ' + output,
                       '$string_read_runtime_bytes(' + state + '[.COMPLETION = NORMAL], ' + origin + ') = ' + ('eps' if emitted else '($echo_value(' + pool_value + '))')]
            if name not in ('raw_float', 'raw_string', 'raw_int'):
                continue
            guards.append(pool + ' = ' + state + '.POOLS[0]')
            payloads = ['PBOOL true', 'PBOOL false', 'PNULL', 'PINT 2', 'PINT 9223372036854775808', 'PINT $(-9223372036854775809)']
            if name != 'raw_int':
                payloads.append('PINT 1')
            for mutation, payload in enumerate(payloads):
                changed = state + '_pool_' + str(mutation)
                invalid_range = '922337203685477580' in payload
                guards += [changed + ' = ' + state + '[.POOLS[0] = ' + pool + '[.CONSTANTS = (PCONSTANT ' + target_name + ' (' + payload + ')) :: ' + pool + '.CONSTANTS]]',
                           '$compiled_read(' + changed + ', ' + origin + ') = (' + payload + ')',
                           '$string_read_runtime_value(' + changed + ', ' + origin + ') = eps',
                           '$string_read_runtime_bytes(' + changed + ', ' + origin + ') = ' + ('eps' if invalid_range else '($echo_value(' + pool_value + '))')]
                if not invalid_range:
                    guards.append('$compiled_identity_value(' + changed + ', ' + origin + ') = (' + payload + ')')
    return checks + guards, derived + len(guards)


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    prep = output.with_name(output.name + '-control-prep')
    prep.mkdir(parents=True)
    raw = [('true', 'true', 'PBOOL true'), ('false', 'false', 'PBOOL false'), ('null', 'null', 'PNULL'),
           ('named_int', 'E_WARNING', 'PINT 2'), ('minimum', 'PHP_INT_MIN', 'PINT $(-9223372036854775808)'),
           ('maximum', '9223372036854775807', 'PINT 9223372036854775807'), ('zero', '0', 'PINT 0'),
           ('negative_fold', '-1', 'PINT $(-1)'), ('binary_fold', '1+2', 'PINT 3'), ('raw_int', '1', 'PINT 1'),
           ('raw_float', '1.0', 'PFLOAT 4607182418800017408'), ('raw_string', "'1'", 'PSTRING ($ptascii("1"))'),
           ('full_null', '(!0.0)?null:(1/0)', 'PNULL'), ('shorthand_null', '(!INF)?:null', 'PNULL')]
    paths = {name: prep / (name + '.php') for name, *_ in raw}
    for name, expression, _ in raw:
        paths[name].write_bytes(('<?php echo (' + expression + ');\n').encode())
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
                   for path, node in occurrences.expected(statement, [('INDEX', index)]) if node['node'].startswith(('Expr_', 'Scalar_'))]
        target, node = min(targets, key=lambda item: len(item[0]))
        CONTROLS.append((name, checked[name]['fixture'], paths[name], target, node, expected,
                         'PSTRING_CARRIER INTERNED_STRING ($ptascii("1"))' if name == 'raw_string' else expected, name.endswith('_null')))
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
    report['scope'] = ('Exact new author prefixes plus independent compiled-child CODE/source/pool/range and missing/mismatched precision controls. Flipping genuine folded integer CODE to emitted retains its valid recursive VALUE/BYTE; raw Boolean/NULL names refuse that flip. Compiled facts survive stale RESULT and five nonnormal completions while the emitted full/shorthand parents refuse. Compiled BOOL/INT BYTE uses the existing compiled route; emitted BOOL/INT keeps read-eps and parent zero-line/ignored-pool fences. Fourteen checked-source compiler controls cover raw/name/folded Boolean, NULL and signed64 integers, raw FLOAT/string/INT type/value substitutions and both NULL parent forms. Raw counterfeits refuse new VALUE while preserving historical compiled BYTE; nonliteral identities keep the existing compiler-output trust boundary. Compiled NULL BYTE is (eps), emitted NULL BYTE is eps. Actual REQUEST owners, supplied Throwable, bounds, cleanup and exact budgets retain the new author selection. Fixture source0/native0; no native/source replay or compiler/numeric/formatter/owner/held-boundary expansion.')
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
