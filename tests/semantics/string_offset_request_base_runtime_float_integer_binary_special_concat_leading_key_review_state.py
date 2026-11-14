#!/usr/bin/env python3
"""Independent integral FLOAT operands, intrinsic notices and state authority."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import source_occurrences as occurrences
import string_offset_request_base_float_boolnot_special_concat_leading_key_review_state as helpers
import string_offset_request_base_runtime_float_integer_binary_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_float_integer_binary_special_concat_leading_key_protocol as source

runner = source.runner
CONTROLS = []


def links(tree, tag='operator'):
    if tree[0] in source.prior.INTEGER_OPS:
        yield tag, tree
    if tree[0] in (*source.prior.INTEGER_OPS, 'ADD', 'SUBTRACT', 'MULTIPLY', 'DIVIDE'):
        for index, child in enumerate(tree[1:3]):
            yield from links(child, tag + '_' + str(index))
    elif tree[0] in ('BITNOT', 'POSITIVE', 'NEGATIVE'):
        yield from links(tree[1], tag + '_0')


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    guards = ['pcode_peer_float_integer = S_after.CODE[0]', 'pcode_peer_float_integer.UNIT = 0',
              'ppool_peer_float_integer = S_after.POOLS[0]', 'ppool_peer_float_integer.UNIT = 0',
              'pcunit_peer_float_integer = S_after.SOURCES[0]', 'pcunit_peer_float_integer.ID = 0']

    def refused(state):
        return ['$string_read_runtime_value(' + state + ', porigin_operator) = eps',
                '$string_read_runtime_bytes(' + state + ', porigin_key) = eps',
                '$string_read_request_base_saved(' + state + ', pstringread) = eps']

    nodes = [(tag, tree) for tag, tree in links(source.TREES[index])
             if any(source.value([], tag + '_' + str(i), child)[0].startswith('PFLOAT ')
                    for i, child in enumerate(tree[1:3]))]
    demanded = sorted({child for tag, _ in nodes for child in (tag, tag + '_0', tag + '_1')})
    for tag in demanded:
        origin, target = 'porigin_' + tag, 'pcpath_peer_float_integer_' + tag
        guards.append(origin + ' = PORIGIN 0 ' + target)
        for label, replacement in (
                ('drop', 'S_after[.CODE[0] = pcode_peer_float_integer[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_float_integer.EXPRESSIONS, ' + target + ', eps)]]'),
                ('flip', 'S_after[.CODE[0] = pcode_peer_float_integer[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_float_integer.EXPRESSIONS, ' + target + ', (true))]]'),
                ('line', 'S_after[.CODE[0] = pcode_peer_float_integer[.EXPRESSIONS = (CODEEXPR ' + target + ' 0 false) :: pcode_peer_float_integer.EXPRESSIONS]]'),
                ('precision', 'S_after[.POOLS[0] = ppool_peer_float_integer[.CONSTANTS = (PCCPRECISION ' + target + ' 17) :: ppool_peer_float_integer.CONSTANTS]]'),
                ('source', 'S_after[.SOURCES[0] = pcunit_peer_float_integer[.OCCURRENCES = (PCOCCURRENCE ' + target + ' (NExprVariable (BYTES "dW5hdXRo") eps)) :: pcunit_peer_float_integer.OCCURRENCES]]')):
            state = 'S_peer_float_integer_' + tag + '_' + label
            guards += [state + ' = ' + replacement, *refused(state)]
    for tag, tree in nodes:
        origin, target = 'porigin_' + tag, 'pcpath_peer_float_integer_' + tag
        result, _ = source.value([], tag, tree)
        left, number_left = source.value([], tag + '_0', tree[1])
        right, number_right = source.value([], tag + '_1', tree[2])
        state = 'S_peer_float_integer_' + tag + '_whole'
        guards += [state + ' = S_after[.RESULT = KNOWN PNULL][.TODO = [VALUE_COPY 11]][.BASE = BASE_VALUE (KNOWN (PINT 99))]',
                   '$integer_coerce(' + state + ', ' + left + ', 5) = ' + state + '[.RESULT = KNOWN (PINT ' + number_left + ')]',
                   '$integer_coerce(' + state + '[.RESULT = KNOWN (PINT ' + number_left + ')], ' + right + ', 5) = ' + state + '[.RESULT = KNOWN (PINT ' + number_right + ')]',
                   '$binary_apply(' + state + ', ' + tree[0] + ', ' + left + ', ' + right + ', 5) = ' + state + '[.RESULT = KNOWN (' + result + ')]',
                   '$string_read_runtime_value(' + state + ', ' + origin + ') = (' + result + ')',
                   '$string_read_runtime_value(S_after[.RESULT = KNOWN (PINT 99)], ' + origin + ') = (' + result + ')',
                   'S_peer_float_integer_' + tag + '_pool = S_after[.POOLS[0] = ppool_peer_float_integer[.CONSTANTS = (PCONSTANT ' + target + ' (PINT 99)) :: ppool_peer_float_integer.CONSTANTS]]',
                   '$compiled_read(S_peer_float_integer_' + tag + '_pool, ' + origin + ') = eps',
                   '$string_read_runtime_value(S_peer_float_integer_' + tag + '_pool, ' + origin + ') = (' + result + ')']
    for label, completion in (('budget', 'BUDGET'), ('pending', 'SOURCE_PENDING'),
                              ('unsupported', 'UNSUPPORTED "peer_float_integer"'), ('exited', 'EXITED 0'),
                              ('thrown', 'THROWN "Error" ($ptascii("peer_float_integer")) 5')):
        state = 'S_peer_float_integer_' + label
        guards += [state + ' = S_after[.COMPLETION = ' + completion + '][.RESULT = KNOWN (PINT 99)]', *refused(state)]
    if index == 0:
        for value in ('PFLOAT 18446744073709551616', 'PINT 9223372036854775808', 'PINT $(-9223372036854775809)',
                      'PSTRING ($ptascii("1"))', 'PARRAY 0', 'POBJECT 0'):
            guards += ['~$string_read_runtime_integer_quiet(' + value + ')']
        for number, (name, fixture, original, target, node, expected, compatibility, side, bits) in enumerate(CONTROLS):
            state, origin = 'S_peer_float_integer_control_' + str(number), 'porigin_peer_float_integer_control_' + str(number)
            normal = state + '_normal'
            result = 'eps' if expected is None else '(PINT ' + source.integers.integer(expected) + ')'
            byte_result = 'eps' if expected is None else '($ptascii(' + json.dumps(str(expected)) + '))'
            guards += [state + ' = $php_run(' + fixture + ', 0, ' + json.dumps(base64.b64encode(bytes(original)).decode()) + ')',
                       state + '.COMPLETION = BUDGET', origin + ' = PORIGIN 0 ' + occurrences.path_term(target),
                       '$origin_node(' + state + '.SOURCES, ' + origin + ') = (' + occurrences.node_term(node) + ')',
                       origin + ' = PORIGIN 0 pcpath_peer_float_integer_control_' + str(number),
                       '$code_at(' + state + '.CODE, 0) = (pcode_peer_float_integer_control_' + str(number) + ')',
                       '$code_expression(pcode_peer_float_integer_control_' + str(number) + '.EXPRESSIONS, pcpath_peer_float_integer_control_' + str(number) + ') = ((1, false))',
                       '$compiled_read(' + state + ', ' + origin + ') = eps',
                       normal + ' = ' + state + '[.COMPLETION = NORMAL]',
                       '$string_read_runtime_value(' + normal + ', ' + origin + ') = ' + result,
                       '$string_read_runtime_bytes(' + normal + ', ' + origin + ') = ' + byte_result,
                       '$string_read_runtime_value(' + normal + '[.RESULT = KNOWN (PINT 99)], ' + origin + ') = ' + result,
                       '$string_read_runtime_value(' + state + '[.RESULT = KNOWN (PINT 99)], ' + origin + ') = ' + (result if compatibility else 'eps')]
            if bits is not None:
                child = origin + '_float'
                guards += ['$origin_child((' + origin + '), [PCFIELD ' + str(side) + ']) = (' + child + ')',
                           '$string_read_runtime_value(' + normal + ', ' + child + ') = (PFLOAT ' + str(bits) + ')',
                           '$string_read_runtime_bytes(' + normal + ', ' + child + ') = eps']
            if name in ('left_fraction', 'left_infinity'):
                suppressed, converted = normal + '_suppressed', '1' if name == 'left_fraction' else '0'
                guards += ['~$string_read_runtime_integer_quiet(PFLOAT ' + str(bits) + ')',
                           suppressed + ' = ' + normal + '[.REPORTING = 0]',
                           '$integer_coerce(' + suppressed + ', PFLOAT ' + str(bits) + ', 1) = ' + suppressed + '[.RESULT = KNOWN (PINT ' + converted + ')]',
                           '$binary_apply(' + suppressed + ', BITOR, PFLOAT ' + str(bits) + ', PINT 1, 1) = ' + suppressed + '[.RESULT = KNOWN (PINT 1)]',
                           '$string_read_runtime_value(' + suppressed + ', ' + origin + ') = eps']
            if compatibility:
                for completion in ('SOURCE_PENDING', 'UNSUPPORTED "peer_control"', 'EXITED 0', 'THROWN "Error" ($ptascii("peer_control")) 1'):
                    guards += ['$string_read_runtime_value(' + state + '[.COMPLETION = ' + completion + '][.RESULT = KNOWN (PINT 99)], ' + origin + ') = ' + result]
    return checks + guards, derived + len(guards)


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    prep = output.with_name(output.name + '-control-prep')
    prep.mkdir(parents=True)
    one = '(+(!0.0))'
    floating = lambda literal: '((!0.0)?(' + literal + '):(1/0))'
    raw = []
    for name, symbol, expected in (('mod', '%', 0), ('and', '&', 1), ('or', '|', 1), ('xor', '^', 0), ('left', '<<', 2), ('right', '>>', 0)):
        raw += [('left_float_' + name, '(' + floating('1.0') + symbol + one + ')', expected, False, 0, 4607182418800017408),
                ('right_float_' + name, '(' + one + symbol + floating('1.0') + ')', expected, False, 1, 4607182418800017408),
                ('pure_int_' + name, '(' + one + symbol + one + ')', expected, True, None, None)]
    raw += [(name, '(' + floating(literal) + '|' + one + ')', expected, False, 0, bits) for name, literal, expected, bits in (
        ('positive_zero', '0.0', 1, 0), ('negative_zero', '-0.0', 1, 9223372036854775808),
        ('minimum', '-9223372036854775808.0', -9223372036854775807, 14114281232179134464),
        ('upper_adjacent', '9223372036854774784.0', 9223372036854774785, 4890909195324358655),
        ('left_fraction', '1.5', None, 4609434218613702656), ('subnormal', '5.0E-324', None, 1),
        ('left_infinity', 'INF', None, 9218868437227405312),
        ('upper_limit', '9223372036854775808.0', None, 4890909195324358656),
        ('below_lower', '-9223372036854777856.0', None, 14114281232179134465),
        ('nan', 'NAN', None, None))]
    raw += [('right_fraction', '(' + one + '|' + floating('-1.5') + ')', None, False, 1, 13832806255468478464),
            ('right_infinity', '(' + one + '|' + floating('-INF') + ')', None, False, 1, 18442240474082181120),
            ('count64', '(' + one + '<<' + floating('64.0') + ')', 0, False, 1, 4634204016564240384),
            ('zero_mod', '(' + one + '%' + floating('-0.0') + ')', None, False, 1, 9223372036854775808),
            ('negative_left', '(' + one + '<<' + floating('-1.0') + ')', None, False, 1, 13830554455654793216),
            ('negative_right', '(' + one + '>>' + floating('-1.0') + ')', None, False, 1, 13830554455654793216)]
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
    for name, expression, expected, compatibility, side, bits in raw:
        target = [('INDEX', 0), ('FIELD', 0), ('FIELD', 1)]
        node = next(node for path, node in occurrences.expected(parsed[name]['ast']['program'][0], [('INDEX', 0)]) if path == target)
        CONTROLS.append((name, checked[name]['fixture'], paths[name], target, node, expected, compatibility, side, bits))
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
    report['scope'] = ('Exact author histories plus independent demanded integral-FLOAT parent/child source, CODE, line and equal-precision controls, stale result/pool and typed sequential full-state coercion/binary checks with nonempty TODO/BASE. ' + str(len(CONTROLS)) + ' checked-source fixtures cover each operand side for all six operators, signed zero, adjacent signed64 limits, fractional/subnormal/nonfinite refusal, MOD0/negative shifts/count64 and six pure-PINT completion controls. Suppressed fractional/infinity conversions demonstrate why full-state quietness alone is insufficient; intrinsic notice guards still refuse. Malformed bits and excluded type/range inputs refuse; emitted FLOAT BYTE stays eps. Actual REQUEST Warning/Throwable/bounds/owners/cleanup/budgets remain. SL fixtures source0/native0; original failures/unrun and all accepted historical campaigns retain separate cuts, with no source/native replay or compiler/numeric/formatter/API/owner/held-boundary change.')
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
