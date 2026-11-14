#!/usr/bin/env python3
"""Independent empty-byte, selected-source and actual-carrier controls."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import source_occurrences as occurrences
import string_offset_request_base_float_boolnot_special_concat_leading_key_review_state as helpers
import string_offset_request_base_runtime_compiled_primitive_special_concat_leading_key_review_state as compiled_review
import string_offset_request_base_runtime_coalesce_special_concat_leading_key_review_state as coalesce_review
import string_offset_request_base_runtime_null_bytes_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_null_bytes_special_concat_leading_key_protocol as source

runner = source.runner
CONTROLS = []


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    guards = ['pcode_peer_null_bytes = S_after.CODE[0]', 'pcode_peer_null_bytes.UNIT = 0',
              'ppool_peer_null_bytes = S_after.POOLS[0]', 'ppool_peer_null_bytes.UNIT = 0',
              'pcunit_peer_null_bytes = S_after.SOURCES[0]', 'pcunit_peer_null_bytes.ID = 0']

    def refused(state):
        return ['$string_read_runtime_bytes(' + state + ', porigin_key) = eps',
                '$string_read_request_base_saved(' + state + ', pstringread) = eps']

    def retained(state):
        return ['$string_read_runtime_value(' + state + ', porigin_operator) = (PNULL)',
                '$string_read_runtime_bytes(' + state + ', porigin_operator) = (eps)',
                '$string_read_runtime_bytes(' + state + ', porigin_key) = $string_read_runtime_bytes(S_after, porigin_key)',
                '$string_read_request_base_saved(' + state + ', pstringread) = $string_read_request_base_saved(S_after, pstringread)']

    emitted = ('operator', 'operator_0') + (('operator_0_0',) if index == 2 else ())
    nulls = (('operator_0_2', 'operator_1') if index == 2 else
             ('operator_1',) if index == 3 else ('operator_2',))
    floats = ('operator_0_0_0',) if index == 2 else ('operator_0_0',)
    for tag in (*emitted, *nulls, *floats):
        origin, target = 'porigin_' + tag, 'pcpath_peer_null_bytes_' + tag
        guards += [origin + ' = PORIGIN 0 ' + target]
        compiled = tag not in emitted
        mutations = [
            ('drop', 'S_after[.CODE[0] = pcode_peer_null_bytes[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_null_bytes.EXPRESSIONS, ' + target + ', eps)]]'),
            ('flip', 'S_after[.CODE[0] = pcode_peer_null_bytes[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_null_bytes.EXPRESSIONS, ' + target + ', (' + ('false' if compiled else 'true') + '))]]'),
            ('precision', 'S_after[.POOLS[0] = ppool_peer_null_bytes[.CONSTANTS = (PCCPRECISION ' + target + ' 17) :: ppool_peer_null_bytes.CONSTANTS]]'),
            ('source', 'S_after[.SOURCES[0] = pcunit_peer_null_bytes[.OCCURRENCES = (PCOCCURRENCE ' + target + ' (NExprVariable (BYTES "dW5hdXRo") eps)) :: pcunit_peer_null_bytes.OCCURRENCES]]'),
        ]
        if not compiled:
            mutations += [('line', 'S_after[.CODE[0] = pcode_peer_null_bytes[.EXPRESSIONS = (CODEEXPR ' + target + ' 0 false) :: pcode_peer_null_bytes.EXPRESSIONS]]')]
        for label, replacement in mutations:
            state = 'S_peer_null_bytes_' + tag + '_' + label
            guards += [state + ' = ' + replacement, *refused(state)]
        if tag in nulls:
            state = 'S_peer_null_bytes_' + tag + '_line'
            guards += [state + ' = S_after[.CODE[0] = pcode_peer_null_bytes[.EXPRESSIONS = (CODEEXPR ' + target + ' 0 true) :: pcode_peer_null_bytes.EXPRESSIONS]]',
                       '$compiled_read(' + state + ', ' + origin + ') = (PNULL)',
                       '$string_read_runtime_bytes(' + state + ', ' + origin + ') = (eps)', *retained(state)]

    for label, completion in (('budget', 'BUDGET'), ('pending', 'SOURCE_PENDING'),
                              ('unsupported', 'UNSUPPORTED "peer_null_bytes"'), ('exited', 'EXITED 0'),
                              ('thrown', 'THROWN "Error" ($ptascii("peer_null_bytes")) 5')):
        state = 'S_peer_null_bytes_' + label
        guards += [state + ' = S_after[.COMPLETION = ' + completion + '][.RESULT = KNOWN PNULL]',
                   '$string_read_runtime_value(' + state + ', porigin_operator) = eps',
                   '$string_read_runtime_bytes(' + state + ', porigin_operator) = eps', *refused(state),
                   '$string_read_runtime_bytes(' + state + ', porigin_' + nulls[0] + ') = (eps)']
    target = 'pcpath_peer_null_bytes_operator'
    guards += ['S_peer_null_bytes_pool = S_after[.POOLS[0] = ppool_peer_null_bytes[.CONSTANTS = (PCONSTANT ' + target + ' (PINT 99)) :: ppool_peer_null_bytes.CONSTANTS]]',
               '$compiled_read(S_peer_null_bytes_pool, porigin_operator) = eps', *retained('S_peer_null_bytes_pool'),
               *retained('S_after[.RESULT = KNOWN (PINT 99)][.TODO = [VALUE_COPY 11]][.BASE = BASE_VALUE (KNOWN (PINT 99))]'),
               *refused('S_after[.DECLARATIONS = eps]'), *refused('S_after[.POOLS = eps]'),
               '$stringify(S_after[.TODO = [VALUE_COPY 11]][.BASE = BASE_VALUE (KNOWN (PINT 99))], PNULL, 5) = S_after[.TODO = [VALUE_COPY 11]][.BASE = BASE_VALUE (KNOWN (PINT 99))][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING eps)]']

    if index != 1:
        tag = 'operator_0_1' if index == 2 else 'operator_2' if index == 3 else 'operator_1'
        target = 'pcpath_peer_null_bytes_skipped'
        guards += ['porigin_' + tag + ' = PORIGIN 0 ' + target]
        for label, replacement in (
                ('drop', 'S_after[.CODE[0] = pcode_peer_null_bytes[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_null_bytes.EXPRESSIONS, ' + target + ', eps)]]'),
                ('line', 'S_after[.CODE[0] = pcode_peer_null_bytes[.EXPRESSIONS = (CODEEXPR ' + target + ' 0 false) :: pcode_peer_null_bytes.EXPRESSIONS]]'),
                ('precision', 'S_after[.POOLS[0] = ppool_peer_null_bytes[.CONSTANTS = (PCCPRECISION ' + target + ' 17) :: ppool_peer_null_bytes.CONSTANTS]]'),
                ('pool', 'S_after[.CODE[0] = pcode_peer_null_bytes[.EXPRESSIONS = (CODEEXPR ' + target + ' 5 true) :: pcode_peer_null_bytes.EXPRESSIONS]][.POOLS[0] = ppool_peer_null_bytes[.CONSTANTS = (PCONSTANT ' + target + ' (PFLOAT 9221120237041090560)) :: ppool_peer_null_bytes.CONSTANTS]]')):
            state = 'S_peer_null_bytes_skipped_' + label
            guards += [state + ' = ' + replacement, *retained(state)]
        state = 'S_peer_null_bytes_skipped_source'
        guards += [state + ' = S_after[.SOURCES[0] = pcunit_peer_null_bytes[.OCCURRENCES = (PCOCCURRENCE ' + target + ' (NExprVariable (BYTES "dW5hdXRo") eps)) :: pcunit_peer_null_bytes.OCCURRENCES]]', *refused(state)]

    key = json.dumps(('1x', '-1x', '0x', '-4x')[index])
    guards += ['$string_read_request_base_saved(S_after, pstringread[.READ.INPUT = KNOWN (PSTRING ($ptascii(' + key + ')))][.READ.VALUE = PSTRING ($ptascii(' + key + '))]) = eps',
               '$string_read_request_base_saved(S_after, pstringread[.READ.OWNERS = BASE_VALUE (KNOWN pstringread.READ.BASE)]) = eps',
               'pstringread_peer_null_bytes_invalid = pstringread[.READ.INPUT = KNOWN (PSTRING_CARRIER (REQUEST_STRING (|S_after.STRINGDATA|)) ($ptascii(' + key + ')))][.READ.VALUE = PSTRING_CARRIER (REQUEST_STRING (|S_after.STRINGDATA|)) ($ptascii(' + key + '))]',
               '~$string_carrier_valid(S_after, pstringread_peer_null_bytes_invalid.READ.VALUE)',
               '$string_read_request_base_saved(S_after, pstringread_peer_null_bytes_invalid) = eps']
    if index == 0:
        for number, (name, fixture, original, target, node, expected, byte_result, compiled) in enumerate(CONTROLS):
            state, origin = 'S_peer_null_bytes_control_' + str(number), 'porigin_peer_null_bytes_control_' + str(number)
            normal, output = state + '_normal', 'eps' if expected is None else '(' + expected + ')'
            guards += [state + ' = $php_run(' + fixture + ', 0, ' + json.dumps(base64.b64encode(bytes(original)).decode()) + ')',
                       state + '.COMPLETION = BUDGET', origin + ' = PORIGIN 0 ' + occurrences.path_term(target),
                       '$origin_node(' + state + '.SOURCES, ' + origin + ') = (' + occurrences.node_term(node) + ')',
                       origin + ' = PORIGIN 0 pcpath_peer_null_bytes_control_' + str(number),
                       '$code_at(' + state + '.CODE, 0) = (pcode_peer_null_bytes_control_' + str(number) + ')',
                       '$code_expression(pcode_peer_null_bytes_control_' + str(number) + '.EXPRESSIONS, pcpath_peer_null_bytes_control_' + str(number) + ') = ((1, ' + str(compiled).lower() + '))',
                       normal + ' = ' + state + '[.COMPLETION = NORMAL]',
                       '$string_read_runtime_value(' + normal + ', ' + origin + ') = ' + output,
                       '$string_read_runtime_bytes(' + normal + ', ' + origin + ') = ' + byte_result,
                       '$string_read_runtime_bytes(' + normal + '[.RESULT = KNOWN PNULL], ' + origin + ') = ' + byte_result]
        # Execute the exact changed predicates from the two old review builders,
        # without replaying their accepted broad campaigns.
        saved = compiled_review.source.conditions
        try:
            compiled_review.source.conditions = lambda *args: ([], 0)
            affected, _ = compiled_review.conditions(None, None, 2)
        finally:
            compiled_review.source.conditions = saved
        exact = '$string_read_runtime_bytes(S_after, porigin_operator_0_0) = (eps)'
        assert affected.count(exact) == 1
        guards += [exact.replace('porigin_operator_0_0', 'porigin_operator')]
        control = next(row for row in CONTROLS if row[0] == 'null_result')
        name, fixture, original, target, node, expected, *_ = control
        saved = coalesce_review.source.conditions
        try:
            coalesce_review.source.conditions = lambda *args: ([], 0)
            coalesce_review.CONTROLS = [(name, fixture, original, target, node, expected, False)]
            affected, _ = coalesce_review.conditions(None, None, 0)
        finally:
            coalesce_review.source.conditions = saved
            coalesce_review.CONTROLS = []
        start = next(i for i, check in enumerate(affected) if check.startswith('S_peer_coalesce_control_0 = '))
        guards += affected[start:]
    return checks + guards, derived + len(guards)


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    prep = output.with_name(output.name + '-control-prep')
    prep.mkdir(parents=True)
    truth, false = '(!0.0)', '(!INF)'
    null = '(' + false + '?true:null)'
    raw = [
        ('full_false', null, 'PNULL', '(eps)', False),
        ('shorthand', '(' + false + '?:null)', 'PNULL', '(eps)', False),
        ('null_result', '(' + null + '??null)', 'PNULL', '(eps)', False),
        ('full_true', '(' + truth + '?null:(1/0))', 'PNULL', '(eps)', False),
        ('nested_null', '((' + null + '??null)?:null)', 'PNULL', '(eps)', False),
        ('typed_false', '(' + false + '?:false)', 'PBOOL false', '(eps)', False),
        ('typed_zero', '(' + false + '?true:0)', 'PINT 0', '($ptascii("0"))', False),
        ('float_zero', '(' + false + '?true:0.0)', 'PFLOAT 0', 'eps', False),
        ('float_inf', '(' + false + '?:INF)', 'PFLOAT 9218868437227405312', 'eps', False),
        ('raw_null', 'null', 'PNULL', '(eps)', True),
        ('raw_empty_string', "''", None, '(eps)', True),
        ('concat_empty', '(' + null + ".'')", None, '(eps)', False),
        ('concat_left', '(' + null + ".'1')", None, '($ptascii("1"))', False),
        ('concat_right', "('1'." + null + ')', None, '($ptascii("1"))', False),
        ('concat_both', '(' + null + '.' + null + ')', None, '(eps)', False),
    ]
    raw += [(name, expression, None, 'eps', False) for name, expression in (
        ('variable', '$missing'), ('quiet_null', '($missing??null)'),
        ('selected_variable', '(' + null + '??$missing)'),
        ('selected_divzero', '(' + false + '?true:(1/0))'),
        ('selected_nan', '(' + false + '?true:NAN)'),
        ('selected_string', '(' + false + "?true:'')"),
        ('cast_string', '(string)' + null), ('cast_array', '(array)' + null))]
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
    for name, expression, expected, byte_result, compiled in raw:
        target = [('INDEX', 0), ('FIELD', 0), ('FIELD', 1)]
        node = next(node for path, node in occurrences.expected(parsed[name]['ast']['program'][0], [('INDEX', 0)]) if path == target)
        CONTROLS.append((name, checked[name]['fixture'], paths[name], target, node, expected, byte_result, compiled))
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
    report['scope'] = ('Exact author histories plus independent emitted NULL empty-versus-missing BYTE controls; demanded source/CODE/positive-line/equal-precision and five nonnormal states refuse, while raw compiled NULL keeps its separate empty certificate. Skipped full-arm CODE/pools/precision stay undemanded but its exact source remains required. Stale RESULT and ignored pools cannot answer; nonempty TODO/BASE and pure stringify preserve full state. ' + str(len(CONTROLS)) + ' checked-source fixtures exercise NULL/full/shorthand/coalesce, raw compiled NULL, empty concat in both orientations, typed false/zero, FLOAT BYTE eps and unsupported location/string/cast/selected-failure boundaries. Only the corrected compiled-review emitted-NULL predicate and coalesce-review null_result control are selected from old builders; no old full suite is renewed. Real REQUEST key identity, owners, returning Warning, supplied Throwable, fixed bounds, cleanup and inherited budgets remain. Fixture source0/native0; no new source/native execution, formatter/compiler/API/owner change or held-boundary expansion.')
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
