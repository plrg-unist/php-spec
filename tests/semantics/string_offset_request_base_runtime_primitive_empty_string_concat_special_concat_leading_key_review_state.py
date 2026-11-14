#!/usr/bin/env python3
"""Independent primitive CONCAT conversions, constness and immutable headers."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import source_occurrences as occurrences
import string_offset_request_base_float_boolnot_special_concat_leading_key_review_state as helpers
import string_offset_request_base_runtime_primitive_empty_string_concat_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_primitive_empty_string_concat_special_concat_leading_key_protocol as source

runner = source.runner
CONTROLS = []


def carrier(text):
    return 'PSTRING_CARRIER INTERNED_STRING ($ptascii(' + json.dumps(text) + '))'


def links(tree, tag='operator'):
    yield tag, tree
    kind = tree[0]
    if kind in ('FLOAT', 'STRING'):
        return
    if kind == 'TERNARY':
        children = ((0, tree[1]), (1 if tree[-1] else 2, tree[2]))
    else:
        children = enumerate(tree[2:3] if kind == 'CAST' else tree[1:3] if kind in ('STRING_CONCAT', 'MIXED_CONCAT', 'IDENTICAL') else tree[1:2])
    for index, child in children:
        yield from links(child, tag + '_' + str(index))


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    guards = ['pcode_peer_primitive_concat = S_after.CODE[0]', 'ppool_peer_primitive_concat = S_after.POOLS[0]',
              'pcunit_peer_primitive_concat = S_after.SOURCES[0]']
    for tag, tree in links(source.TREES[index]):
        kind = tree[0]
        if kind not in ('STRING_CONCAT', 'MIXED_CONCAT', 'CAST', 'TERNARY', 'STRING'):
            continue
        origin, target = 'porigin_' + tag, 'pcpath_peer_primitive_concat_' + tag
        guards += [origin + ' = PORIGIN 0 ' + target]
        mutations = [('drop', 'S_after[.CODE[0] = pcode_peer_primitive_concat[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_primitive_concat.EXPRESSIONS, ' + target + ', eps)]]'),
                     ('flip', 'S_after[.CODE[0] = pcode_peer_primitive_concat[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_primitive_concat.EXPRESSIONS, ' + target + ', (' + str(kind != 'STRING').lower() + '))]]'),
                     ('precision', 'S_after[.POOLS[0] = ppool_peer_primitive_concat[.CONSTANTS = (PCCPRECISION ' + target + ' 17) :: ppool_peer_primitive_concat.CONSTANTS]]'),
                     ('source', 'S_after[.SOURCES[0] = pcunit_peer_primitive_concat[.OCCURRENCES = (PCOCCURRENCE ' + target + ' (NExprVariable (BYTES "dW5hdXRo") eps)) :: pcunit_peer_primitive_concat.OCCURRENCES]]')]
        if kind == 'STRING':
            mutations += [('pool', 'S_after[.POOLS[0] = ppool_peer_primitive_concat[.CONSTANTS = (PCONSTANT ' + target + ' (PSTRING ($ptascii("wrong")))) :: ppool_peer_primitive_concat.CONSTANTS]]'),
                          ('request', 'S_after[.POOLS[0] = ppool_peer_primitive_concat[.CONSTANTS = (PCONSTANT ' + target + ' (PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii(' + json.dumps(tree[1]) + ')))) :: ppool_peer_primitive_concat.CONSTANTS]]')]
        else:
            mutations += [('line', 'S_after[.CODE[0] = pcode_peer_primitive_concat[.EXPRESSIONS = (CODEEXPR ' + target + ' 0 false) :: pcode_peer_primitive_concat.EXPRESSIONS]]')]
        for label, replacement in mutations:
            state = 'S_peer_primitive_concat_' + tag + '_' + label
            guards += [state + ' = ' + replacement,
                       '$string_read_runtime_value(' + state + ', porigin_operator) = eps',
                       '$string_read_runtime_bytes(' + state + ', porigin_key) = eps',
                       '$string_read_request_base_saved(' + state + ', pstringread) = eps']
        if kind not in ('STRING_CONCAT', 'MIXED_CONCAT'):
            continue
        result, payload = 'PSTRING_CARRIER INTERNED_STRING (' + str(tree[-1]) + ')', str(tree[-1])
        context = 'S_peer_primitive_concat_' + tag + '_context'
        guards += [context + ' = S_after[.CONSTCONTEXT = ({ORIGIN ' + origin + ', LINE 5, FACTS eps})]',
                   '$string_read_runtime_value(' + context + ', ' + origin + ') = eps',
                   '$string_read_runtime_value(' + context + ', porigin_operator) = eps',
                   '$string_read_runtime_bytes(' + context + ', ' + origin + ') = (' + payload + ')',
                   '$string_read_runtime_bytes(' + context + ', porigin_key) = eps']
        for label, completion in (('budget', 'BUDGET'), ('pending', 'SOURCE_PENDING'),
                                  ('unsupported', 'UNSUPPORTED "peer_primitive_concat"'), ('exited', 'EXITED 0'),
                                  ('thrown', 'THROWN "Error" ($ptascii("peer_primitive_concat")) 5')):
            state = 'S_peer_primitive_concat_' + tag + '_' + label
            guards += [state + ' = S_after[.COMPLETION = ' + completion + '][.RESULT = KNOWN (' + result + ')]',
                       '$string_read_runtime_value(' + state + ', ' + origin + ') = eps']
        whole = 'S_peer_primitive_concat_' + tag + '_whole'
        values = [source.value([], tag + '_' + str(i), child)[0] for i, child in enumerate(tree[1:3])]
        flags = ['$concat_constant(' + whole + ', (porigin_' + tag + '_' + str(i) + '))' for i in range(2)]
        guards += [whole + ' = S_after[.RESULT = KNOWN (PINT 99)][.TODO = [VALUE_COPY 11]][.BASE = BASE_VALUE (KNOWN (PINT 99))]']
        state, strings = whole, []
        for child_index, original in enumerate(values):
            converted = ('PSTRING_CARRIER INTERNED_STRING (' + str(tree[3][child_index]) + ')'
                         if kind == 'MIXED_CONCAT' else original)
            prepared, after = 'pvalue_prepared_' + tag + '_' + str(child_index), whole + '_' + str(child_index)
            guards += ['$string_read_runtime_cast_quiet(CASTSTRING, ' + original + ')',
                       '(' + state + ', KNOWN ' + prepared + ') = $concat_operand(' + state + ', KNOWN (' + original + '), ' + flags[child_index] + ', 5)',
                       after + ' = $stringify(' + state + ', ' + prepared + ', 5)',
                       after + ' = ' + whole + '[.RESULT = KNOWN (' + converted + ')]']
            state = after
            strings.append(converted)
        guards += ['$string_concat(' + state + ', ' + ', '.join(strings + flags) + ') = ' + whole + '[.RESULT = KNOWN (' + result + ')]',
                   '$string_read_runtime_value(' + whole + ', ' + origin + ') = (' + result + ')']
    if index == 0:
        for number, (name, fixture, original, target, node, expected, byte_result) in enumerate(CONTROLS):
            state, origin = 'S_peer_primitive_concat_control_' + str(number), 'porigin_peer_primitive_concat_control_' + str(number)
            normal, result = state + '_normal', 'eps' if expected is None else '(' + expected + ')'
            guards += [state + ' = $php_run(' + fixture + ', 0, ' + json.dumps(base64.b64encode(bytes(original)).decode()) + ')',
                       state + '.COMPLETION = BUDGET', origin + ' = PORIGIN 0 ' + occurrences.path_term(target),
                       '$origin_node(' + state + '.SOURCES, ' + origin + ') = (' + occurrences.node_term(node) + ')',
                       origin + ' = PORIGIN 0 pcpath_peer_primitive_concat_control_' + str(number),
                       '$code_at(' + state + '.CODE, 0) = (pcode_peer_primitive_concat_control_' + str(number) + ')',
                       '$code_expression(pcode_peer_primitive_concat_control_' + str(number) + '.EXPRESSIONS, pcpath_peer_primitive_concat_control_' + str(number) + ') = ((1, false))',
                       '$compiled_read(' + state + ', ' + origin + ') = eps',
                       '$string_read_runtime_value(' + state + ', ' + origin + ') = eps',
                       normal + ' = ' + state + '[.COMPLETION = NORMAL]',
                       '$string_read_runtime_value(' + normal + ', ' + origin + ') = ' + result,
                       '$string_read_runtime_bytes(' + normal + ', ' + origin + ') = ' + ('eps' if byte_result is None else '(' + byte_result + ')'),
                       '$string_read_runtime_value(' + normal + '[.RESULT = KNOWN (PINT 99)], ' + origin + ') = ' + result]
            if name in ('constant_empty_left', 'constant_empty_right', 'both_nonempty'):
                left, right, flags = ((carrier(''), carrier('1'), 'true, false') if name == 'constant_empty_left' else
                                      (carrier('1'), carrier(''), 'false, true') if name == 'constant_empty_right' else
                                      (carrier('1'), carrier('9'), 'false, true'))
                allocated = normal + '_allocated'
                guards += [allocated + ' = $string_concat(' + normal + ', ' + left + ', ' + right + ', ' + flags + ')',
                           '$(|' + allocated + '.STRINGDATA| = |' + normal + '.STRINGDATA| + 1)',
                           allocated + '.STRINGDATA[|' + normal + '.STRINGDATA|] = ' + byte_result]
    return checks + guards, derived + len(guards)


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    prep = output.with_name(output.name + '-control-prep')
    prep.mkdir(parents=True)
    false, true, null = '(!INF)', '(!0.0)', '((!INF)?true:null)'
    raw = [('false_true', false + '.' + true, carrier('1'), '$ptascii("1")'),
           ('true_false', true + '.' + false, carrier('1'), '$ptascii("1")'),
           ('false_null', false + '.' + null, carrier(''), 'eps'),
           ('null_false', null + '.' + false, carrier(''), 'eps'),
           ('zero_false', '0 . ' + false, carrier('0'), '$ptascii("0")'),
           ('nine_false', '9 . ' + false, carrier('9'), '$ptascii("9")'),
           ('false_nine', false + ' . 9', carrier('9'), '$ptascii("9")'),
           ('nested_primitive', '(' + false + '.(+(!0.0)+2)).' + false, carrier('3'), '$ptascii("3")'),
           ('constant_empty_left', '"".' + true, None, '$ptascii("1")'),
           ('constant_empty_right', true + '.""', None, '$ptascii("1")'),
           ('both_nonempty', true + ' . 9', None, '$ptascii("19")'),
           ('raw_nul_survivor', false + '."a\\0b"', None, '[97, 0, 98]'),
           ('selected_nul_survivor', false + '.((!0.0)?"a\\0b":(1/0))', None, None),
           ('integer_parent', '(int)(' + false + '."003")', 'PINT 3', '$ptascii("3")'),
           ('bitwise_parent', '(' + false + '.' + true + ')&"3"', carrier('1'), '$ptascii("1")'),
           ('empty_coalesce', '((' + false + '.' + null + ')??"fallback")', carrier(''), 'eps'),
           ('empty_truth', '((' + false + '.' + null + ')?"bad":"good")', carrier('good'), '$ptascii("good")'),
           ('negative_integer', '(-1).' + false, carrier('-1'), '$ptascii("-1")'),
           ('two_digit_integer', '10 . ' + false, carrier('10'), '$ptascii("10")'),
           ('float_parent', '(int)(' + false + ' . 0.0)', None, None)]
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
    for name, expression, expected, byte_result in raw:
        target = [('INDEX', 0), ('FIELD', 0), ('FIELD', 1)]
        node = next(node for path, node in occurrences.expected(parsed[name]['ast']['program'][0], [('INDEX', 0)]) if path == target)
        CONTROLS.append((name, checked[name]['fixture'], paths[name], target, node, expected, byte_result))
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
    report['scope'] = 'Fresh four primitive CONCAT histories plus independent original-child source/CODE/line/precision/pool/header mutations, nonnormal cached results and sequential prepare/stringify/final whole-state preservation. Twenty fresh source0 controls cover NULL/BOOL/digits0/9, left/right/both-empty and nested computed3, const-empty slowpath reuse remaining conservatively refused, both-nonempty allocation, NUL carrier bounds, typed INT/bitwise/truth/coalesce parents and actual compiled negative/two-digit integer survivors; dynamic wider integers and FLOAT remain refused. Known both-STRING behavior remains pointwise; no old campaign/native replay or formatter/owner/held-boundary expansion.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
