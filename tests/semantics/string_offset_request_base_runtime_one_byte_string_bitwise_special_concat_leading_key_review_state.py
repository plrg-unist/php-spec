#!/usr/bin/env python3
"""Independent string bitwise types, single-byte allocation and NUL bounds."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import source_occurrences as occurrences
import string_offset_request_base_float_boolnot_special_concat_leading_key_review_state as helpers
import string_offset_request_base_runtime_one_byte_string_bitwise_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_one_byte_string_bitwise_special_concat_leading_key_protocol as source

runner = source.runner
CONTROLS = []


def carrier(payload):
    return 'PSTRING_CARRIER INTERNED_STRING (' + payload + ')'


def links(tree, tag='operator'):
    yield tag, tree
    kind = tree[0]
    if kind in ('FLOAT', 'STRING'):
        return
    if kind == 'TERNARY':
        children = ((0, tree[1]), (1 if tree[-1] else 2, tree[2]))
    else:
        children = enumerate(tree[2:4] if kind == 'STRING_BINARY' else tree[2:3] if kind == 'CAST' else
                             tree[1:3] if kind == 'IDENTICAL' else tree[1:2])
    for index, child in children:
        yield from links(child, tag + '_' + str(index))


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    guards = ['pcode_peer_string_bits = S_after.CODE[0]', 'ppool_peer_string_bits = S_after.POOLS[0]',
              'pcunit_peer_string_bits = S_after.SOURCES[0]']
    for tag, tree in links(source.TREES[index]):
        kind = tree[0]
        if kind not in ('STRING_BINARY', 'STRING_NOT', 'TERNARY', 'STRING'):
            continue
        origin, target = 'porigin_' + tag, 'pcpath_peer_string_bits_' + tag
        guards += [origin + ' = PORIGIN 0 ' + target]
        mutations = [('drop', 'S_after[.CODE[0] = pcode_peer_string_bits[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_string_bits.EXPRESSIONS, ' + target + ', eps)]]'),
                     ('flip', 'S_after[.CODE[0] = pcode_peer_string_bits[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_string_bits.EXPRESSIONS, ' + target + ', (' + str(kind != 'STRING').lower() + '))]]'),
                     ('precision', 'S_after[.POOLS[0] = ppool_peer_string_bits[.CONSTANTS = (PCCPRECISION ' + target + ' 17) :: ppool_peer_string_bits.CONSTANTS]]'),
                     ('source', 'S_after[.SOURCES[0] = pcunit_peer_string_bits[.OCCURRENCES = (PCOCCURRENCE ' + target + ' (NExprVariable (BYTES "dW5hdXRo") eps)) :: pcunit_peer_string_bits.OCCURRENCES]]')]
        if kind == 'STRING':
            mutations += [('pool', 'S_after[.POOLS[0] = ppool_peer_string_bits[.CONSTANTS = (PCONSTANT ' + target + ' (PSTRING ($ptascii("wrong")))) :: ppool_peer_string_bits.CONSTANTS]]'),
                          ('request', 'S_after[.POOLS[0] = ppool_peer_string_bits[.CONSTANTS = (PCONSTANT ' + target + ' (PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii(' + json.dumps(tree[1]) + ')))) :: ppool_peer_string_bits.CONSTANTS]]')]
        else:
            mutations += [('line', 'S_after[.CODE[0] = pcode_peer_string_bits[.EXPRESSIONS = (CODEEXPR ' + target + ' 0 false) :: pcode_peer_string_bits.EXPRESSIONS]]')]
        for label, replacement in mutations:
            state = 'S_peer_string_bits_' + tag + '_' + label
            guards += [state + ' = ' + replacement,
                       '$string_read_runtime_value(' + state + ', porigin_operator) = eps',
                       '$string_read_runtime_bytes(' + state + ', porigin_key) = eps',
                       '$string_read_request_base_saved(' + state + ', pstringread) = eps']
        if kind not in ('STRING_BINARY', 'STRING_NOT'):
            continue
        result = carrier(str(tree[-1]))
        for label, completion in (('budget', 'BUDGET'), ('pending', 'SOURCE_PENDING'),
                                  ('unsupported', 'UNSUPPORTED "peer_string_bits"'), ('exited', 'EXITED 0'),
                                  ('thrown', 'THROWN "Error" ($ptascii("peer_string_bits")) 5')):
            state = 'S_peer_string_bits_' + tag + '_' + label
            guards += [state + ' = S_after[.COMPLETION = ' + completion + '][.RESULT = KNOWN (' + result + ')]',
                       '$string_read_runtime_value(' + state + ', ' + origin + ') = eps',
                       '$string_read_runtime_bytes(' + state + ', ' + origin + ') = eps']
        whole = 'S_peer_string_bits_' + tag + '_whole'
        children = tree[2:4] if kind == 'STRING_BINARY' else tree[1:2]
        values = [source.value([], tag + '_' + str(i), child)[0] for i, child in enumerate(children)]
        operation = ('$binary_apply(' + whole + ', ' + tree[1] + ', ' + ', '.join(values) + ', 5)' if kind == 'STRING_BINARY'
                     else '$bitnot_value(' + whole + ', ' + values[0] + ', 5)')
        guards += [whole + ' = S_after[.RESULT = KNOWN (PINT 99)][.TODO = [VALUE_COPY 11]][.BASE = BASE_VALUE (KNOWN (PINT 99))]',
                   operation + ' = ' + whole + '[.RESULT = KNOWN (' + result + ')]',
                   '$string_read_runtime_value(' + whole + ', ' + origin + ') = (' + result + ')']
    if index == 0:
        for number, (name, fixture, original, target, node, expected) in enumerate(CONTROLS):
            state, origin = 'S_peer_string_bits_control_' + str(number), 'porigin_peer_string_bits_control_' + str(number)
            normal, result = state + '_normal', 'eps' if expected is None else '(' + expected + ')'
            guards += [state + ' = $php_run(' + fixture + ', 0, ' + json.dumps(base64.b64encode(bytes(original)).decode()) + ')',
                       state + '.COMPLETION = BUDGET', origin + ' = PORIGIN 0 ' + occurrences.path_term(target),
                       '$origin_node(' + state + '.SOURCES, ' + origin + ') = (' + occurrences.node_term(node) + ')',
                       origin + ' = PORIGIN 0 pcpath_peer_string_bits_control_' + str(number),
                       '$code_at(' + state + '.CODE, 0) = (pcode_peer_string_bits_control_' + str(number) + ')',
                       '$code_expression(pcode_peer_string_bits_control_' + str(number) + '.EXPRESSIONS, pcpath_peer_string_bits_control_' + str(number) + ') = ((1, false))',
                       '$compiled_read(' + state + ', ' + origin + ') = eps',
                       '$string_read_runtime_value(' + state + ', ' + origin + ') = eps',
                       normal + ' = ' + state + '[.COMPLETION = NORMAL]',
                       '$string_read_runtime_value(' + normal + ', ' + origin + ') = ' + result,
                       '$string_read_runtime_bytes(' + normal + ', ' + origin + ') = ' + ('eps' if expected is None else '($echo_value(' + expected + '))'),
                       '$string_read_runtime_value(' + normal + '[.RESULT = KNOWN (PINT 99)], ' + origin + ') = ' + result]
            if name in ('not_nul_result', 'xor_nul_result'):
                operation = ('$bitnot_value(' + normal + ', ' + carrier('[255]') + ', 1)' if name == 'not_nul_result' else
                             '$binary_apply(' + normal + ', BITXOR, ' + carrier('[49]') + ', ' + carrier('[49]') + ', 1)')
                guards += [operation + ' = ' + normal + '[.RESULT = KNOWN (' + carrier('[0]') + ')]',
                           '$c_string([0]) = eps']
    return checks + guards, derived + len(guards)


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    prep = output.with_name(output.name + '-control-prep')
    prep.mkdir(parents=True)
    selected = lambda text: '((!0.0)?' + json.dumps(text) + ':(1/0))'
    one, zero = '(+(!0.0))', '(+(!INF))'
    raw = [('affected_both_string_bits', selected('1') + '&' + selected('3'), carrier('[49]')),
           ('affected_string_bitnot', '~' + selected('1'), carrier('[206]')),
           ('or', selected('0') + '|"0"', carrier('[48]')),
           ('xor', selected('p') + '^"C"', carrier('[51]')),
           ('and_reverse', '"3"&' + selected('1'), carrier('[49]')),
           ('or_reverse', '"0"|' + selected('0'), carrier('[48]')),
           ('xor_reverse', '"C"^' + selected('p'), carrier('[51]')),
           ('double_not', '~~' + selected('1'), carrier('[49]')),
           ('nested_binary', '(' + selected('p') + '^"C")&"3"', carrier('[51]')),
           ('not_nul_result', '~((!0.0)?"\\xFF":(1/0))', None),
           ('xor_nul_result', selected('1') + '^"1"', None),
           ('and_nul_result', selected('p') + '&"\\x0F"', None),
           ('and_multibyte', selected('ab') + '&"c"', None),
           ('xor_multibyte', selected('ab') + '^"c"', None),
           ('or_multibyte', selected('ab') + '|"c"', None),
           ('not_multibyte', '~' + selected('ab'), None),
           ('and_empty', selected('') + '&"1"', None),
           ('or_empty', selected('') + '|"1"', None),
           ('xor_empty', selected('') + '^"1"', None),
           ('not_empty', '~' + selected(''), None),
           ('nul_input', '((!0.0)?"\\0":(1/0))|"1"', None),
           ('mixed_integer', selected('3') + '&' + one, 'PINT 1'),
           ('mixed_float', selected('3') + '|(1.0+' + zero + ')', 'PINT 3'),
           ('numeric_shift', selected('3') + '<<"1"', 'PINT 6'),
           ('nonnumeric_mixed', selected('p') + '&' + one, None),
           ('concat_producer', '(' + selected('1') + '."")&"3"', None),
           ('string_cast_parent', '(string)(~' + selected('1') + ')', carrier('[206]'))]
    paths = {name: prep / (name + '.php') for name, *_ in raw}
    for name, expression, _ in raw:
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
    for name, expression, expected in raw:
        target = [('INDEX', 0), ('FIELD', 0), ('FIELD', 1)]
        node = next(node for path, node in occurrences.expected(parsed[name]['ast']['program'][0], [('INDEX', 0)]) if path == target)
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
    assert report['mode'] == 'fixture SL'
    report['scope'] = 'Exact new author histories plus independent bitwise/selected-arm/literal SOURCE/CODE/precision/line/raw-pool/REQUEST-header mutations, cached nonnormal results and whole-state RESULT/TODO/BASE preservation. Twenty-seven fresh checked-source controls include exact two affected old expressions, all three string binary operators and NOT, reversed/nested typed operations, nonNUL high byte206, immutable NUL results refused despite pure lower operations, empty/multibyte allocations including one-byte truncated outputs, selected NUL input, preserved mixed integer/FLOAT and shift dispatch, nonnumeric mixed failure, wider CONCAT refusal and STRING-cast composition. Fixture source0/native0; no accepted old campaign/native replay, formatter/compiler/owner changes or held-boundary expansion.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
