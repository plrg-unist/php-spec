#!/usr/bin/env python3
"""Independent FLOAT bitwise NOT, type priority and intrinsic notice guards."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import source_occurrences as occurrences
import string_offset_request_base_float_boolnot_special_concat_leading_key_review_state as helpers
import string_offset_request_base_runtime_float_bitnot_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_float_bitnot_special_concat_leading_key_protocol as source

runner = source.runner
CONTROLS = []


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    guards = ['pcode_peer_float_not = S_after.CODE[0]', 'pcode_peer_float_not.UNIT = 0',
              'ppool_peer_float_not = S_after.POOLS[0]', 'ppool_peer_float_not.UNIT = 0',
              'pcunit_peer_float_not = S_after.SOURCES[0]', 'pcunit_peer_float_not.ID = 0']

    def refused(state):
        return ['$string_read_runtime_value(' + state + ', porigin_operator) = eps',
                '$string_read_runtime_bytes(' + state + ', porigin_key) = eps',
                '$string_read_request_base_saved(' + state + ', pstringread) = eps']

    for tag in ('operator', 'operator_0'):
        target = 'pcpath_peer_float_not_' + tag
        guards.append('porigin_' + tag + ' = PORIGIN 0 ' + target)
        for label, replacement in (
                ('drop', 'S_after[.CODE[0] = pcode_peer_float_not[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_float_not.EXPRESSIONS, ' + target + ', eps)]]'),
                ('flip', 'S_after[.CODE[0] = pcode_peer_float_not[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_float_not.EXPRESSIONS, ' + target + ', (true))]]'),
                ('line', 'S_after[.CODE[0] = pcode_peer_float_not[.EXPRESSIONS = (CODEEXPR ' + target + ' 0 false) :: pcode_peer_float_not.EXPRESSIONS]]'),
                ('precision', 'S_after[.POOLS[0] = ppool_peer_float_not[.CONSTANTS = (PCCPRECISION ' + target + ' 17) :: ppool_peer_float_not.CONSTANTS]]'),
                ('source', 'S_after[.SOURCES[0] = pcunit_peer_float_not[.OCCURRENCES = (PCOCCURRENCE ' + target + ' (NExprVariable (BYTES "dW5hdXRo") eps)) :: pcunit_peer_float_not.OCCURRENCES]]')):
            state = 'S_peer_float_not_' + tag + '_' + label
            guards += [state + ' = ' + replacement, *refused(state)]
    child, child_number = source.value([], 'operator_0', source.TREES[index][1])
    result = 'PINT ' + source.integers.integer(source.TREES[index][-1])
    state = 'S_peer_float_not_whole'
    guards += [state + ' = S_after[.RESULT = KNOWN PNULL][.TODO = [VALUE_COPY 11]][.BASE = BASE_VALUE (KNOWN (PINT 99))]',
               '$integer_coerce(' + state + ', ' + child + ', 5) = ' + state + '[.RESULT = KNOWN (PINT ' + child_number + ')]',
               '$bitnot_value(' + state + ', ' + child + ', 5) = ' + state + '[.RESULT = KNOWN (' + result + ')]',
               '$string_read_runtime_value(' + state + ', porigin_operator) = (' + result + ')',
               '$string_read_runtime_value(S_after[.RESULT = KNOWN (PINT 99)], porigin_operator) = (' + result + ')',
               'S_peer_float_not_pool = S_after[.POOLS[0] = ppool_peer_float_not[.CONSTANTS = (PCONSTANT pcpath_peer_float_not_operator (PINT 99)) :: ppool_peer_float_not.CONSTANTS]]',
               '$compiled_read(S_peer_float_not_pool, porigin_operator) = eps',
               '$string_read_runtime_value(S_peer_float_not_pool, porigin_operator) = (' + result + ')']
    for label, completion in (('budget', 'BUDGET'), ('pending', 'SOURCE_PENDING'),
                              ('unsupported', 'UNSUPPORTED "peer_float_not"'), ('exited', 'EXITED 0'),
                              ('thrown', 'THROWN "Error" ($ptascii("peer_float_not")) 5')):
        state = 'S_peer_float_not_' + label
        guards += [state + ' = S_after[.COMPLETION = ' + completion + '][.RESULT = KNOWN (' + result + ')]', *refused(state)]
    if index == 0:
        for number, (name, fixture, original, target, node, expected, compatibility, child) in enumerate(CONTROLS):
            state, origin = 'S_peer_float_not_control_' + str(number), 'porigin_peer_float_not_control_' + str(number)
            normal = state + '_normal'
            result = 'eps' if expected is None else '(PINT ' + source.integers.integer(expected) + ')'
            byte_result = 'eps' if expected is None else '($ptascii(' + json.dumps(str(expected)) + '))'
            guards += [state + ' = $php_run(' + fixture + ', 0, ' + json.dumps(base64.b64encode(bytes(original)).decode()) + ')',
                       state + '.COMPLETION = BUDGET', origin + ' = PORIGIN 0 ' + occurrences.path_term(target),
                       '$origin_node(' + state + '.SOURCES, ' + origin + ') = (' + occurrences.node_term(node) + ')',
                       origin + ' = PORIGIN 0 pcpath_peer_float_not_control_' + str(number),
                       '$code_at(' + state + '.CODE, 0) = (pcode_peer_float_not_control_' + str(number) + ')',
                       '$code_expression(pcode_peer_float_not_control_' + str(number) + '.EXPRESSIONS, pcpath_peer_float_not_control_' + str(number) + ') = ((1, false))',
                       '$compiled_read(' + state + ', ' + origin + ') = eps',
                       normal + ' = ' + state + '[.COMPLETION = NORMAL]',
                       '$string_read_runtime_value(' + normal + ', ' + origin + ') = ' + result,
                       '$string_read_runtime_bytes(' + normal + ', ' + origin + ') = ' + byte_result,
                       '$string_read_runtime_value(' + normal + '[.RESULT = KNOWN (PINT 99)], ' + origin + ') = ' + result,
                       '$string_read_runtime_value(' + state + '[.RESULT = KNOWN (PINT 99)], ' + origin + ') = ' + (result if compatibility else 'eps')]
            if child is not None:
                child_origin = origin + '_child'
                guards += ['$origin_child((' + origin + '), [PCFIELD 0]) = (' + child_origin + ')',
                           '$string_read_runtime_value(' + normal + ', ' + child_origin + ') = (' + child + ')']
                if child.startswith('PFLOAT '):
                    guards += ['$string_read_runtime_bytes(' + normal + ', ' + child_origin + ') = eps']
            if name in ('fraction', 'infinity'):
                suppressed = normal + '_suppressed'
                converted, complemented = ('1', '$(-2)') if name == 'fraction' else ('0', '$(-1)')
                guards += [suppressed + ' = ' + normal + '[.REPORTING = 0]',
                           '$integer_coerce(' + suppressed + ', ' + child + ', 1) = ' + suppressed + '[.RESULT = KNOWN (PINT ' + converted + ')]',
                           '$bitnot_value(' + suppressed + ', ' + child + ', 1) = ' + suppressed + '[.RESULT = KNOWN (PINT ' + complemented + ')]',
                           '$string_read_runtime_value(' + suppressed + ', ' + origin + ') = eps']
            if compatibility:
                for completion in ('SOURCE_PENDING', 'UNSUPPORTED "peer_control"', 'EXITED 0', 'THROWN "Error" ($ptascii("peer_control")) 1'):
                    guards += ['$string_read_runtime_value(' + state + '[.COMPLETION = ' + completion + '][.RESULT = KNOWN (PINT 99)], ' + origin + ') = ' + result]
    return checks + guards, derived + len(guards)


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    prep = output.with_name(output.name + '-control-prep')
    prep.mkdir(parents=True)
    selected = lambda literal: '((!0.0)?(' + literal + '):(1/0))'
    raw = [(name, '(~' + selected(literal) + ')', expected, False, 'PFLOAT ' + str(bits) if bits is not None else None)
           for name, literal, expected, bits in (
               ('negative_two', '-2.0', 1, 13835058055282163712),
               ('positive_zero', '0.0', -1, 0), ('negative_zero', '-0.0', -1, 9223372036854775808),
               ('negative_one', '-1.0', 0, 13830554455654793216), ('three', '3.0', -4, 4613937818241073152),
               ('minimum', '-9223372036854775808.0', 9223372036854775807, 14114281232179134464),
               ('upper_adjacent', '9223372036854774784.0', -9223372036854774785, 4890909195324358655),
               ('fraction', '1.5', None, 4609434218613702656), ('negative_fraction', '-1.5', None, 13832806255468478464),
               ('subnormal', '5.0E-324', None, 1), ('infinity', 'INF', None, 9218868437227405312),
               ('negative_infinity', '-INF', None, 18442240474082181120), ('nan', 'NAN', None, None),
               ('upper_limit', '9223372036854775808.0', None, 4890909195324358656),
               ('below_lower', '-9223372036854777856.0', None, 14114281232179134465))]
    raw += [(name, '(~' + selected(literal) + ')', None, False, value) for name, literal, value in (
        ('true', 'true', 'PBOOL true'), ('false', 'false', 'PBOOL false'), ('null', 'null', 'PNULL'))]
    raw += [(name, '(~((int)' + selected(literal) + '))', expected, False, value) for name, literal, expected, value in (
        ('cast_true', 'true', -2, 'PINT 1'), ('cast_false', 'false', -1, 'PINT 0'), ('cast_null', 'null', -1, 'PINT 0'))]
    raw += [('pure_int', '(~(+(!0.0)))', -2, True, 'PINT 1'),
            ('pure_minimum', '(~(PHP_INT_MIN+(+(!INF))))', 9223372036854775807, True, 'PINT $(-9223372036854775808)'),
            ('string', "(~('1'.(!INF)))", None, False, None), ('array', '(~[])', None, False, None)]
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
    for name, expression, expected, compatibility, child in raw:
        target = [('INDEX', 0), ('FIELD', 0), ('FIELD', 1)]
        node = next(node for path, node in occurrences.expected(parsed[name]['ast']['program'][0], [('INDEX', 0)]) if path == target)
        CONTROLS.append((name, checked[name]['fixture'], paths[name], target, node, expected, compatibility, child))
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
    report['scope'] = ('Exact author histories plus independent BITNOT parent/child source, CODE, line, equal precision, stale result/pool and full-state original typed coercion/bitnot checks with nonempty TODO/BASE. ' + str(len(CONTROLS)) + ' checked-source fixtures cover signed zeros, integral limits, fractional/subnormal/nonfinite refusal, raw BOOL/NULL refusal versus explicit INT casts, string/array refusal and two old-PINT five-completion controls. Suppressed fractional/infinity conversions remain refused despite unchanged-state coercion and bitnot results. Emitted FLOAT BYTE stays eps; unchanged intrinsic integer predicate bounds are retained. Actual REQUEST Warning/Throwable/bounds/owners/cleanup/budgets remain. SL fixtures source0/native0; no source/native replay or old campaign renewal, no compiler/numeric/formatter/API/owner/held-boundary change.')
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
