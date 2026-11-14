#!/usr/bin/env python3
"""Independent literal-byte authority, carrier type and quiet parent controls."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import source_occurrences as occurrences
import string_offset_request_base_float_boolnot_special_concat_leading_key_review_state as helpers
import string_offset_request_base_runtime_literal_string_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_literal_string_special_concat_leading_key_protocol as source

runner = source.runner
CONTROLS = []


def carrier(text):
    return 'PSTRING_CARRIER INTERNED_STRING ($ptascii(' + json.dumps(text) + '))'


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    tree = source.TREES[index][1]
    text = tree[1][1]
    value = carrier(text)
    other = '0' + text if text != '01' else '1'
    guards = ['pcode_peer_literal = S_after.CODE[0]', 'ppool_peer_literal = S_after.POOLS[0]',
              'pcunit_peer_literal = S_after.SOURCES[0]',
              'porigin_operator_0_0 = PORIGIN 0 pcpath_peer_literal']

    def refused(state):
        return ['$string_read_runtime_value(' + state + ', porigin_operator_0_0) = eps',
                '$string_read_runtime_value(' + state + ', porigin_operator) = eps',
                '$string_read_runtime_bytes(' + state + ', porigin_key) = eps',
                '$string_read_request_base_saved(' + state + ', pstringread) = eps']

    for label, flag in (('drop', 'eps'), ('flip', '(false)')):
        state = 'S_peer_literal_' + label
        guards += [state + ' = S_after[.CODE[0] = pcode_peer_literal[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_literal.EXPRESSIONS, pcpath_peer_literal, ' + flag + ')]]', *refused(state)]
    for label, raw in (('same_numeric_bytes', 'PSTRING ($ptascii(' + json.dumps(other) + '))'),
                       ('interned_pool', value), ('request_pool', 'PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii(' + json.dumps(text) + '))'),
                       ('integer_pool', 'PINT ' + tree[1][2]), ('boolean_pool', 'PBOOL true'),
                       ('null_pool', 'PNULL'),
                       ('invalid_byte_pool', 'PSTRING ([256])')):
        state = 'S_peer_literal_' + label
        guards += [state + ' = S_after[.POOLS[0] = ppool_peer_literal[.CONSTANTS = (PCONSTANT pcpath_peer_literal (' + raw + ')) :: ppool_peer_literal.CONSTANTS]]', *refused(state)]
    guards += ['S_peer_literal_float_pool = S_after[.POOLS[0] = ppool_peer_literal[.CONSTANTS = (PCONSTANT pcpath_peer_literal (PFLOAT 4607182418800017408)) :: ppool_peer_literal.CONSTANTS]]',
               '$compiled_read(S_peer_literal_float_pool, porigin_operator_0_0) = (PFLOAT 4607182418800017408)',
               '$compiled_identity_value(S_peer_literal_float_pool, porigin_operator_0_0) = (PFLOAT 4607182418800017408)',
               '$string_read_runtime_value(S_peer_literal_float_pool, porigin_operator_0_0) = (PFLOAT 4607182418800017408)',
               '$string_read_runtime_bytes(S_peer_literal_float_pool, porigin_operator_0_0) = ($ptascii(' + json.dumps(text) + '))']
    replacement = 'NScalarString (BYTES ' + json.dumps(base64.b64encode(other.encode()).decode()) + ') eps'
    for label, node in (('same_numeric_source', replacement), ('foreign_source', 'NExprVariable (BYTES "dW5hdXRo") eps')):
        state = 'S_peer_literal_' + label
        guards += [state + ' = S_after[.SOURCES[0] = pcunit_peer_literal[.OCCURRENCES = (PCOCCURRENCE pcpath_peer_literal (' + node + ')) :: pcunit_peer_literal.OCCURRENCES]]', *refused(state)]
    guards += ['S_peer_literal_precision = S_after[.POOLS[0] = ppool_peer_literal[.CONSTANTS = (PCCPRECISION pcpath_peer_literal 17) :: ppool_peer_literal.CONSTANTS]]',
               '$compiled_precision(S_peer_literal_precision, (porigin_operator_0_0)) = (17)',
               '$string_read_runtime_value(S_peer_literal_precision, porigin_operator_0_0) = (' + value + ')',
               '$string_read_runtime_value(S_peer_literal_precision, porigin_operator) = eps',
               '$string_read_request_base_saved(S_peer_literal_precision, pstringread) = eps',
               'S_peer_literal_whole = S_after[.RESULT = KNOWN PNULL][.TODO = [VALUE_COPY 11]][.BASE = BASE_VALUE (KNOWN (PINT 99))]',
               '$string_read_runtime_value(S_peer_literal_whole, porigin_operator_0_0) = (' + value + ')']
    right = source.value([], 'operator_0_1', tree[2])[0]
    result = source.value([], 'operator_0', tree)[0]
    guards += ['$binary_apply(S_peer_literal_whole, ' + tree[0] + ', ' + value + ', ' + right + ', 5) = S_peer_literal_whole[.RESULT = KNOWN (' + result + ')]']
    for completion in ('BUDGET', 'SOURCE_PENDING', 'UNSUPPORTED "peer_literal"', 'EXITED 0', 'THROWN "Error" ($ptascii("peer_literal")) 5'):
        guards += ['$string_read_runtime_value(S_after[.COMPLETION = ' + completion + '], porigin_operator_0_0) = (' + value + ')']
    if index == 0:
        for number, (name, fixture, original, target, node, expected, byte_result, folded) in enumerate(CONTROLS):
            state, origin = 'S_peer_literal_control_' + str(number), 'porigin_peer_literal_control_' + str(number)
            normal = state + '_normal'
            result = 'eps' if expected is None else '(' + expected + ')'
            guards += [state + ' = $php_run(' + fixture + ', 0, ' + json.dumps(base64.b64encode(bytes(original)).decode()) + ')',
                       state + '.COMPLETION = BUDGET', origin + ' = PORIGIN 0 ' + occurrences.path_term(target),
                       '$origin_node(' + state + '.SOURCES, ' + origin + ') = (' + occurrences.node_term(node) + ')',
                       origin + ' = PORIGIN 0 pcpath_peer_literal_control_' + str(number),
                       '$code_at(' + state + '.CODE, 0) = (pcode_peer_literal_control_' + str(number) + ')',
                       '$code_expression(pcode_peer_literal_control_' + str(number) + '.EXPRESSIONS, pcpath_peer_literal_control_' + str(number) + ') = ((1, ' + str(folded).lower() + '))',
                       normal + ' = ' + state + '[.COMPLETION = NORMAL]',
                       '$string_read_runtime_value(' + normal + ', ' + origin + ') = ' + result,
                       '$string_read_runtime_bytes(' + normal + ', ' + origin + ') = ' + byte_result,
                       '$string_read_runtime_value(' + normal + '[.RESULT = KNOWN (PINT 99)], ' + origin + ') = ' + result]
            if folded or name in ('affected_identity', 'affected_equality', 'affected_order', 'affected_division'):
                guards += ['$string_read_runtime_value(' + state + ', ' + origin + ') = ' + result]
            if name in ('affected_xor', 'affected_float_arithmetic'):
                guards += ['$string_read_runtime_value(' + state + ', ' + origin + ') = eps']
            if name == 'affected_raw_string':
                guards += ['$compiled_read(' + state + ', ' + origin + ') = (PSTRING ($ptascii("1")))',
                           '$compiled_identity_value(' + state + ', ' + origin + ') = (PSTRING ($ptascii("1")))']
            if name == 'affected_division':
                guards += ['$origin_child((' + origin + '), [PCFIELD 0]) = (porigin_peer_literal_div_left)',
                           '$origin_child((' + origin + '), [PCFIELD 1]) = (porigin_peer_literal_div_right)',
                           '$compiled_read(' + normal + ', porigin_peer_literal_div_left) = (PSTRING ($ptascii("1")))',
                           '$string_read_runtime_value(' + normal + ', porigin_peer_literal_div_left) = (' + carrier('1') + ')',
                           '$string_read_runtime_value(' + normal + ', porigin_peer_literal_div_right) = (PBOOL true)',
                           '$binary_apply(' + normal + ', DIVIDE, ' + carrier('1') + ', PBOOL true, 1) = ' + normal + '[.RESULT = KNOWN (PINT 1)]']
            if name == 'nul_literal':
                payload = '($ptascii("a") ++ [0] ++ $ptascii("b"))'
                guards += ['$compiled_read(' + normal + ', ' + origin + ') = (PSTRING ' + payload + ')',
                           '$compiled_identity_value(' + normal + ', ' + origin + ') = (PSTRING ' + payload + ')',
                           '$compiled_string_value(' + normal + ', ' + origin + ', PSTRING ' + payload + ') = PSTRING_CARRIER INTERNED_STRING ' + payload,
                           '$string_carrier_valid(' + normal + ', PSTRING_CARRIER INTERNED_STRING ' + payload + ')']
            if name == 'leading_arithmetic':
                suppressed = normal + '_suppressed'
                guards += ['$coerce_number(' + carrier('1x') + ') = COERCED (NINT 1) true',
                           suppressed + ' = ' + normal + '[.REPORTING = 0]',
                           '$binary_apply(' + suppressed + ', ADD, ' + carrier('1x') + ', PINT 0, 1) = ' + suppressed + '[.RESULT = KNOWN (PINT 1)]',
                           '$string_read_runtime_value(' + suppressed + ', ' + origin + ') = eps']
    return checks + guards, derived + len(guards)


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    prep = output.with_name(output.name + '-control-prep')
    prep.mkdir(parents=True)
    one, zero = '(+(!0.0))', '(+(!INF))'
    true, false = '(!0.0)', '(!INF)'
    runtime_float = '(0.0+' + zero + ')'
    raw = [
        ('affected_raw_string', "'1'", carrier('1'), '($ptascii("1"))', True),
        ('affected_identity', "'1'===" + true, 'PBOOL false', '(eps)', False),
        ('affected_equality', "'1'==" + true, 'PBOOL true', '($ptascii("1"))', False),
        ('affected_order', "'1'>" + false, 'PBOOL true', '($ptascii("1"))', False),
        ('affected_xor', "'1' xor " + false, 'PBOOL true', '($ptascii("1"))', False),
        ('affected_division', "'1'/" + true, 'PINT 1', '($ptascii("1"))', False),
        ('affected_float_arithmetic', "'1'+" + runtime_float, 'PFLOAT 4607182418800017408', 'eps', False),
        ('empty_literal', "''", carrier(''), '(eps)', True),
        ('double_zero_literal', "'00'", carrier('00'), '($ptascii("00"))', True),
        ('nul_literal', '"a\\0b"', None, '($ptascii("a") ++ [0] ++ $ptascii("b"))', True),
        ('leading_arithmetic', "'1x'+" + zero, None, 'eps', False),
        ('nonnumeric_arithmetic', "'foo'+" + zero, None, 'eps', False),
        ('selected_string', "((!0.0)?'1':(1/0))", carrier('1'), 'eps', False),
        ('string_cast', "(int)((!0.0)?'1':(1/0))", 'PINT 1', '($ptascii("1"))', False),
        ('string_integer_binary', "'1'&" + one, None, 'eps', False),
        ('string_power', "'2'**" + zero, 'PINT 1', '($ptascii("1"))', False),
        ('zero_truth', "!((!0.0)?'0':(1/0))", 'PBOOL true', '($ptascii("1"))', False),
    ]
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
    for name, expression, expected, byte_result, folded in raw:
        target = [('INDEX', 0), ('FIELD', 0), ('FIELD', 1)]
        node = next(node for path, node in occurrences.expected(parsed[name]['ast']['program'][0], [('INDEX', 0)]) if path == target)
        CONTROLS.append((name, checked[name]['fixture'], paths[name], target, node, expected, byte_result, folded))
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
    report['scope'] = ('Exact author histories plus independent literal source/pool/decoded-byte/header authority, including same-numeric different-byte forgeries and nonraw pool types. A forged PFLOAT pool retains its prior compiled VALUE and actual literal BYTE without gaining INTERNED VALUE. Literal precision17 preserves its bytes but refuses a parent captured14; compiled-leaf values preserve existing completion behavior and whole-state typed parents retain nonempty TODO/BASE. Seventeen checked-source controls include fresh copies of the seven affected old literal-string controls, nonNUL empty/zero strings, NUL refusal despite valid raw/interned/unchanged BYTE facts, quiet FLOAT arithmetic with BYTEeps, selected STRING VALUE without BYTE, selected STRING CASTINT and existing integer-binary refusals, quiet POWER and exact zero-string truth. Suppressed leading-number conversion stays refused despite a matching quiet full-state numeric result. Fixture source0/native0; no old campaign/native replay, owner/formatter/compiler/numeric body change or held-boundary expansion.')
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
