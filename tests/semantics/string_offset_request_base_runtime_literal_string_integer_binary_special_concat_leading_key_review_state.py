#!/usr/bin/env python3
"""Independent quiet string integer conversions and original typed dispatch."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import source_occurrences as occurrences
import string_offset_request_base_float_boolnot_special_concat_leading_key_review_state as helpers
import string_offset_request_base_runtime_literal_string_integer_binary_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_literal_string_integer_binary_special_concat_leading_key_protocol as source

runner = source.runner
CONTROLS = []
BINARY = ('ADD', 'MODULO', 'BITAND', 'BITOR', 'BITXOR', 'SHIFTLEFT', 'SHIFTRIGHT')


def carrier(text):
    return 'PSTRING_CARRIER INTERNED_STRING ($ptascii(' + json.dumps(text) + '))'


def links(tree, tag='operator'):
    yield tag, tree
    if tree[0] in ('FLOAT', 'STRING'):
        return
    if tree[0] == 'TERNARY':
        children = ((0, tree[1]), (1 if tree[-1] else 2, tree[2]))
    elif tree[0] in BINARY:
        children = enumerate(tree[1:3])
    else:
        children = ((0, tree[1]),)
    for index, child in children:
        yield from links(child, tag + '_' + str(index))


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    guards = ['pcode_peer_string_integer = S_after.CODE[0]', 'ppool_peer_string_integer = S_after.POOLS[0]',
              'pcunit_peer_string_integer = S_after.SOURCES[0]']
    for tag, tree in links(source.TREES[index]):
        if tree[0] not in (*BINARY, 'TERNARY', 'STRING'):
            continue
        origin, target = 'porigin_' + tag, 'pcpath_peer_string_integer_' + tag
        guards += [origin + ' = PORIGIN 0 ' + target]
        mutations = [('drop', 'S_after[.CODE[0] = pcode_peer_string_integer[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_string_integer.EXPRESSIONS, ' + target + ', eps)]]'),
                     ('flip', 'S_after[.CODE[0] = pcode_peer_string_integer[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_string_integer.EXPRESSIONS, ' + target + ', (' + str(tree[0] != 'STRING').lower() + '))]]'),
                     ('precision', 'S_after[.POOLS[0] = ppool_peer_string_integer[.CONSTANTS = (PCCPRECISION ' + target + ' 17) :: ppool_peer_string_integer.CONSTANTS]]'),
                     ('source', 'S_after[.SOURCES[0] = pcunit_peer_string_integer[.OCCURRENCES = (PCOCCURRENCE ' + target + ' (NExprVariable (BYTES "dW5hdXRo") eps)) :: pcunit_peer_string_integer.OCCURRENCES]]')]
        if tree[0] == 'STRING':
            mutations += [('pool', 'S_after[.POOLS[0] = ppool_peer_string_integer[.CONSTANTS = (PCONSTANT ' + target + ' (PSTRING ($ptascii("other")))) :: ppool_peer_string_integer.CONSTANTS]]')]
        else:
            mutations += [('line', 'S_after[.CODE[0] = pcode_peer_string_integer[.EXPRESSIONS = (CODEEXPR ' + target + ' 0 false) :: pcode_peer_string_integer.EXPRESSIONS]]')]
        for label, replacement in mutations:
            state = 'S_peer_string_integer_' + tag + '_' + label
            guards += [state + ' = ' + replacement,
                       '$string_read_runtime_value(' + state + ', porigin_operator) = eps',
                       '$string_read_runtime_bytes(' + state + ', porigin_key) = eps',
                       '$string_read_request_base_saved(' + state + ', pstringread) = eps']
    for completion in ('BUDGET', 'SOURCE_PENDING', 'UNSUPPORTED "peer_string_integer"', 'EXITED 0', 'THROWN "Error" ($ptascii("peer_string_integer")) 5'):
        guards += ['$string_read_runtime_value(S_after[.COMPLETION = ' + completion + '], porigin_operator) = eps']
    guards += ['$string_read_runtime_value(S_after[.RESULT = KNOWN (PINT 99)][.TODO = [VALUE_COPY 11]][.BASE = BASE_VALUE (KNOWN (PINT 99))], porigin_operator) = (PINT ' + ('1', '$(-1)', '0', '$(-4)')[index] + ')']
    if index == 0:
        for text, number in (('0', '0'), ('-0.0', '0'), ('00', '0'), ('1', '1'), ('1.0', '1'), ('1e0', '1'),
                             (' -1 ', '$(-1)'), ('9223372036854775808', '9223372036854775807'),
                             ('-9223372036854775809', '$(-9223372036854775808)')):
            guards += ['$string_long($ptascii(' + json.dumps(text) + ')) = STRINT ' + number + ' eps',
                       '$string_read_runtime_integer_quiet(' + carrier(text) + ')']
        for text in ('', 'junk', '1tail', '1.5', '1.5tail', '1e999', '18446744073709551616'):
            guards += ['~$string_read_runtime_integer_quiet(' + carrier(text) + ')']
        for value in ('PSTRING ($ptascii("1"))', 'PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("1"))',
                      'PSTRING_CARRIER INTERNED_STRING ([256])', 'PSTRING_CARRIER INTERNED_STRING ($ptascii("1") ++ [0])'):
            guards += ['~$string_read_runtime_integer_quiet(' + value + ')']
        guards += ['$byte_operator(BITAND, ' + carrier('1') + ', ' + carrier('3') + ')',
                   '$binary_apply(S_after, BITAND, ' + carrier('1') + ', ' + carrier('3') + ', 5) = S_after[.RESULT = KNOWN (' + carrier('1') + ')]',
                   '$bitnot_value(S_after, ' + carrier('1') + ', 5) = S_after[.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([206]))]']
        for number, (name, fixture, original, target, node, expected) in enumerate(CONTROLS):
            state, origin = 'S_peer_string_integer_control_' + str(number), 'porigin_peer_string_integer_control_' + str(number)
            normal, result = state + '_normal', 'eps' if expected is None else '(' + expected + ')'
            byte_result = 'eps' if expected is None else '($echo_value(' + expected + '))'
            guards += [state + ' = $php_run(' + fixture + ', 0, ' + json.dumps(base64.b64encode(bytes(original)).decode()) + ')',
                       state + '.COMPLETION = BUDGET', origin + ' = PORIGIN 0 ' + occurrences.path_term(target),
                       '$origin_node(' + state + '.SOURCES, ' + origin + ') = (' + occurrences.node_term(node) + ')',
                       origin + ' = PORIGIN 0 pcpath_peer_string_integer_control_' + str(number),
                       '$code_at(' + state + '.CODE, 0) = (pcode_peer_string_integer_control_' + str(number) + ')',
                       '$code_expression(pcode_peer_string_integer_control_' + str(number) + '.EXPRESSIONS, pcpath_peer_string_integer_control_' + str(number) + ') = ((1, false))',
                       '$compiled_read(' + state + ', ' + origin + ') = eps',
                       '$string_read_runtime_value(' + state + ', ' + origin + ') = eps',
                       normal + ' = ' + state + '[.COMPLETION = NORMAL]',
                       '$string_read_runtime_value(' + normal + ', ' + origin + ') = ' + result,
                       '$string_read_runtime_bytes(' + normal + ', ' + origin + ') = ' + byte_result,
                       '$string_read_runtime_value(' + normal + '[.RESULT = KNOWN (PINT 99)], ' + origin + ') = ' + result]
            if name in ('fractional_noise', 'leading_noise', 'nonfinite_noise'):
                text = {'fractional_noise': '1.5', 'leading_noise': '1tail', 'nonfinite_noise': '1e999'}[name]
                integer = '0' if name == 'nonfinite_noise' else '1'
                suppressed = normal + '_suppressed'
                guards += [suppressed + ' = ' + normal + '[.REPORTING = 0]',
                           '$integer_coerce(' + suppressed + ', ' + carrier(text) + ', 1) = ' + suppressed + '[.RESULT = KNOWN (PINT ' + integer + ')]',
                           '$string_read_runtime_value(' + suppressed + ', ' + origin + ') = eps']
    return checks + guards, derived + len(guards)


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    prep = output.with_name(output.name + '-control-prep')
    prep.mkdir(parents=True)

    def selected(text):
        return '((!0.0)?' + json.dumps(text) + ':(1/0))'

    one, zero = '(+(!0.0))', '(+(!INF))'
    raw = [('affected_literal_string', "'1'&" + one, 'PINT 1'),
           ('affected_cast_string', '"1"&' + one, 'PINT 1'),
           ('negative_zero', selected('-0.0') + '>>' + one, 'PINT 0'),
           ('upper_saturation', selected('9223372036854775808') + '&' + one, 'PINT 1'),
           ('lower_saturation', selected('-9223372036854775809') + '>>' + one, 'PINT $(-4611686018427387904)'),
           ('both_string_modulo', selected('5') + '%' + selected('2'), 'PINT 1'),
           ('fractional_noise', selected('1.5') + '&' + one, None),
           ('leading_noise', selected('1tail') + '|' + zero, None),
           ('nonfinite_noise', selected('1e999') + '&' + one, None),
           ('nonnumeric_error', selected('junk') + '%' + one, None),
           ('both_string_bits', selected('1') + '&' + selected('3'), None),
           ('string_bitnot', '~' + selected('1'), None),
           ('zero_divisor', selected('1') + '%' + zero, None),
           ('negative_shift', selected('1') + '<<(-' + one + ')', None),
           ('mixed_integral_float', selected('1') + '&(1.0+' + zero + ')', 'PINT 1'),
           ('nul_string', '((!0.0)?"1\\0":(1/0))&' + one, None)]
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
    report['scope'] = ('Exact author histories plus independent recursive operator/selected-ternary/literal source, CODE, precision, line and raw-pool authority; nonnormal completions and stale RESULT/TODO/BASE remain distinct. Sixteen fresh checked-source controls include exact single/double-quoted affected controls, negative zero, both quiet saturation boundaries, both-STRING modulo, mixed integral FLOAT, intrinsic fractional/leading/nonfinite notices even under reporting0, nonnumeric/zero-divisor/negative-shift failures, bytewise STRING and STRING BITNOT type distinctions, and NUL refusal. Quiet helpers retain canonical nonNUL INTERNED headers and exact STRINT i eps; raw PSTRING, REQUEST and malformed bytes refuse. Selected STRING BYTE remains eps. Fixture source0/native0; no old campaign/native replay, numeric/compiler/formatter/owner body or held-boundary change.')
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
