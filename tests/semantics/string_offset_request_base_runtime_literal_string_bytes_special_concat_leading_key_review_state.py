#!/usr/bin/env python3
"""Independent selected STRING bytes, empty payloads and demanded-arm authority."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import source_occurrences as occurrences
import string_offset_request_base_float_boolnot_special_concat_leading_key_review_state as helpers
import string_offset_request_base_runtime_literal_string_bytes_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_literal_string_bytes_special_concat_leading_key_protocol as source

runner = source.runner
CONTROLS = []


def carrier(text):
    return 'PSTRING_CARRIER INTERNED_STRING ($ptascii(' + json.dumps(text) + '))'


def links(tree, tag='operator'):
    yield tag, tree
    kind = tree[0]
    if kind in ('FLOAT', 'STRING', 'NULL_TERNARY'):
        return
    if kind == 'TERNARY':
        children = ((0, tree[1]), (1 if tree[-1] else 2, tree[2]))
    elif kind == 'SHORTHAND':
        children = [(0, tree[1])] + ([] if tree[-1] else [(2, tree[2])])
    elif kind == 'COALESCE':
        children = [(0, tree[1])] + ([] if tree[2] is None else [(1, tree[2])])
    else:
        children = ((0, tree[1]),)
    for index, child in children:
        yield from links(child, tag + '_' + str(index))


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    expected = ('1', '-1', '0', '-4')[index]
    guards = ['pcode_peer_string_bytes = S_after.CODE[0]', 'ppool_peer_string_bytes = S_after.POOLS[0]',
              'pcunit_peer_string_bytes = S_after.SOURCES[0]']
    for tag, tree in links(source.TREES[index]):
        if tree[0] not in ('SHORTHAND', 'COALESCE', 'TERNARY', 'STRING'):
            continue
        origin, target = 'porigin_' + tag, 'pcpath_peer_string_bytes_' + tag
        guards += [origin + ' = PORIGIN 0 ' + target]
        mutations = [('drop', 'S_after[.CODE[0] = pcode_peer_string_bytes[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_string_bytes.EXPRESSIONS, ' + target + ', eps)]]'),
                     ('flip', 'S_after[.CODE[0] = pcode_peer_string_bytes[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_string_bytes.EXPRESSIONS, ' + target + ', (' + str(tree[0] != 'STRING').lower() + '))]]'),
                     ('precision', 'S_after[.POOLS[0] = ppool_peer_string_bytes[.CONSTANTS = (PCCPRECISION ' + target + ' 17) :: ppool_peer_string_bytes.CONSTANTS]]'),
                     ('source', 'S_after[.SOURCES[0] = pcunit_peer_string_bytes[.OCCURRENCES = (PCOCCURRENCE ' + target + ' (NExprVariable (BYTES "dW5hdXRo") eps)) :: pcunit_peer_string_bytes.OCCURRENCES]]')]
        if tree[0] == 'STRING':
            mutations += [('pool', 'S_after[.POOLS[0] = ppool_peer_string_bytes[.CONSTANTS = (PCONSTANT ' + target + ' (PSTRING ($ptascii("other")))) :: ppool_peer_string_bytes.CONSTANTS]]'),
                          ('request_pool', 'S_after[.POOLS[0] = ppool_peer_string_bytes[.CONSTANTS = (PCONSTANT ' + target + ' (PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii(' + json.dumps(tree[1]) + ')))) :: ppool_peer_string_bytes.CONSTANTS]]')]
        else:
            mutations += [('line', 'S_after[.CODE[0] = pcode_peer_string_bytes[.EXPRESSIONS = (CODEEXPR ' + target + ' 0 false) :: pcode_peer_string_bytes.EXPRESSIONS]]')]
        for label, replacement in mutations:
            state = 'S_peer_string_bytes_' + tag + '_' + label
            guards += [state + ' = ' + replacement,
                       '$string_read_runtime_value(' + state + ', porigin_operator) = eps',
                       '$string_read_runtime_bytes(' + state + ', porigin_operator) = eps',
                       '$string_read_runtime_bytes(' + state + ', porigin_key) = eps',
                       '$string_read_request_base_saved(' + state + ', pstringread) = eps']
    for completion in ('BUDGET', 'SOURCE_PENDING', 'UNSUPPORTED "peer_string_bytes"', 'EXITED 0', 'THROWN "Error" ($ptascii("peer_string_bytes")) 5'):
        guards += ['$string_read_runtime_bytes(S_after[.COMPLETION = ' + completion + '], porigin_operator) = eps']
    guards += ['S_peer_string_bytes_whole = S_after[.RESULT = KNOWN (PINT 99)][.TODO = [VALUE_COPY 11]][.BASE = BASE_VALUE (KNOWN (PINT 99))]',
               '$string_read_runtime_value(S_peer_string_bytes_whole, porigin_operator) = (' + carrier(expected) + ')',
               '$string_read_runtime_bytes(S_peer_string_bytes_whole, porigin_operator) = ($ptascii(' + json.dumps(expected) + '))']
    if index == 0:
        for tag in ('operator_2', 'operator_0_2'):
            target, state = 'pcpath_peer_string_bytes_dead_' + tag, 'S_peer_string_bytes_dead_' + tag
            guards += ['porigin_' + tag + ' = PORIGIN 0 ' + target,
                       state + ' = S_after[.CODE[0] = pcode_peer_string_bytes[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_string_bytes.EXPRESSIONS, ' + target + ', eps)]]',
                       '$string_read_runtime_value(' + state + ', porigin_operator) = (' + carrier('1') + ')',
                       '$string_read_runtime_bytes(' + state + ', porigin_operator) = ($ptascii("1"))',
                       state + '_source = S_after[.SOURCES[0] = pcunit_peer_string_bytes[.OCCURRENCES = (PCOCCURRENCE ' + target + ' (NExprVariable (BYTES "dW5hdXRo") eps)) :: pcunit_peer_string_bytes.OCCURRENCES]]',
                       '$string_read_runtime_value(' + state + '_source, porigin_operator) = eps',
                       '$string_read_runtime_bytes(' + state + '_source, porigin_operator) = eps']
        for number, (name, fixture, original, target, node, value, byte_result, folded) in enumerate(CONTROLS):
            state, origin = 'S_peer_string_bytes_control_' + str(number), 'porigin_peer_string_bytes_control_' + str(number)
            normal, result = state + '_normal', 'eps' if value is None else '(' + value + ')'
            read = '(PSTRING ($ptascii("a") ++ [0] ++ $ptascii("b")))' if folded else 'eps'
            guards += [state + ' = $php_run(' + fixture + ', 0, ' + json.dumps(base64.b64encode(bytes(original)).decode()) + ')',
                       state + '.COMPLETION = BUDGET', origin + ' = PORIGIN 0 ' + occurrences.path_term(target),
                       '$origin_node(' + state + '.SOURCES, ' + origin + ') = (' + occurrences.node_term(node) + ')',
                       origin + ' = PORIGIN 0 pcpath_peer_string_bytes_control_' + str(number),
                       '$code_at(' + state + '.CODE, 0) = (pcode_peer_string_bytes_control_' + str(number) + ')',
                       '$code_expression(pcode_peer_string_bytes_control_' + str(number) + '.EXPRESSIONS, pcpath_peer_string_bytes_control_' + str(number) + ') = ((1, ' + str(folded).lower() + '))',
                       '$compiled_read(' + state + ', ' + origin + ') = ' + read,
                       '$string_read_runtime_value(' + state + ', ' + origin + ') = eps',
                       '$string_read_runtime_bytes(' + state + ', ' + origin + ') = ' + (byte_result if folded else 'eps'),
                       normal + ' = ' + state + '[.COMPLETION = NORMAL]',
                       '$string_read_runtime_value(' + normal + ', ' + origin + ') = ' + result,
                       '$string_read_runtime_bytes(' + normal + ', ' + origin + ') = ' + byte_result,
                       '$string_read_runtime_bytes(' + normal + '[.RESULT = KNOWN (PINT 99)], ' + origin + ') = ' + byte_result]
            if folded:
                guards += ['$string_carrier_valid(' + normal + ', PSTRING_CARRIER INTERNED_STRING ($ptascii("a") ++ [0] ++ $ptascii("b")))']
    return checks + guards, derived + len(guards)


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    prep = output.with_name(output.name + '-control-prep')
    prep.mkdir(parents=True)

    def selected(text):
        return "((!0.0) ? '" + text + "' : (1/0))"

    raw = [('affected_selected_string', "((!0.0)?'1':(1/0))", carrier('1'), '($ptascii("1"))', False)]
    raw += [('cast_child_' + str(i), selected(text), carrier(text), '($ptascii(' + json.dumps(text) + '))', False)
            for i, text in enumerate(('1tail', 'junk', '0', '3.0tail'))]
    raw += [('empty_full', selected(''), carrier(''), '(eps)', False),
            ('nonnumeric_full', selected('hello'), carrier('hello'), '($ptascii("hello"))', False),
            ('zero_shorthand', '(' + selected('0') + " ?: 'fallback')", carrier('fallback'), '($ptascii("fallback"))', False),
            ('truthy_double_zero', '(' + selected('00') + ' ?: (1/0))', carrier('00'), '($ptascii("00"))', False),
            ('empty_coalesce', '(' + selected('') + ' ?? (1/0))', carrier(''), '(eps)', False),
            ('zero_coalesce', '(' + selected('0') + ' ?? (1/0))', carrier('0'), '($ptascii("0"))', False),
            ('null_coalesce', "(((!INF)?true:null) ?? 'x')", carrier('x'), '($ptascii("x"))', False),
            ('false_full', "((+(!INF))?(1/0):'selected')", carrier('selected'), '($ptascii("selected"))', False),
            ('selected_nul', '((!0.0)?"a\\0b":(1/0))', None, 'eps', False),
            ('raw_nul', '"a\\0b"', None, '($ptascii("a") ++ [0] ++ $ptascii("b"))', True),
            ('emitted_float', '(1.0+(+(!INF)))', 'PFLOAT 4607182418800017408', 'eps', False)]
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
    for name, expression, value, byte_result, folded in raw:
        target = [('INDEX', 0), ('FIELD', 0), ('FIELD', 1)]
        node = next(node for path, node in occurrences.expected(parsed[name]['ast']['program'][0], [('INDEX', 0)]) if path == target)
        CONTROLS.append((name, checked[name]['fixture'], paths[name], target, node, value, byte_result, folded))
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
    assert report['mode'] == 'fixture SL'
    report['scope'] = ('Exact author histories plus independent demanded selector/literal SOURCE/CODE/precision/line/raw-pool and REQUEST-header forgeries, nonnormal completions and whole-state RESULT/TODO/BASE preservation. Two skipped divide-zero arms retain BYTE when their CODE is absent but refuse forged SOURCE. Sixteen fresh checked-source controls include exact affected selected-string and four prior CAST child expressions, empty Some(eps), nonnumeric bytes, zero/double-zero truth, empty/zero/null coalesce, false full selection, selected-NUL refusal versus unchanged raw compiled-NUL BYTE and emitted FLOAT BYTEeps. Compiled and emitted BYTE remain disjoint; fixture source0/native0 with no old campaign/native replay, formatter/compiler/owner body or held-boundary expansion.')
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
