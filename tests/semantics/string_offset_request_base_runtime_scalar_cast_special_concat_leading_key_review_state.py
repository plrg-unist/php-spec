#!/usr/bin/env python3
"""Independent primitive cast types, quiet notices and source authority."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import source_occurrences as occurrences
import string_offset_request_base_float_boolnot_special_concat_leading_key_review_state as helpers
import string_offset_request_base_runtime_scalar_cast_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_scalar_cast_special_concat_leading_key_protocol as source

runner = source.runner
CONTROLS = []


def links(tree, tag='operator'):
    yield tag, tree
    kind = tree[0]
    if kind == 'FLOAT':
        return
    children = (tree[2:3] if kind in ('CAST', 'FLOAT_UNARY') else tree[2:4] if kind == 'FLOAT_BINARY' else
                tree[1:3] if kind in ('ADD', 'SUBTRACT', 'MULTIPLY', 'DIVIDE', 'IDENTICAL') else tree[1:2])
    for index, child in enumerate(children):
        yield from links(child, tag + '_' + str(index))


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    guards = ['pcode_peer_cast = S_after.CODE[0]', 'pcode_peer_cast.UNIT = 0',
              'ppool_peer_cast = S_after.POOLS[0]', 'ppool_peer_cast.UNIT = 0',
              'pcunit_peer_cast = S_after.SOURCES[0]', 'pcunit_peer_cast.ID = 0']
    nodes = dict(links(source.TREES[index]))
    demanded = {tag: tree for tag, tree in nodes.items() if tree[0] == 'CAST'}
    demanded.update({tag + '_0': nodes[tag + '_0'] for tag in tuple(demanded)})
    for tag, tree in demanded.items():
        origin, target = 'porigin_' + tag, 'pcpath_peer_cast_' + tag
        guards.append(origin + ' = PORIGIN 0 ' + target)
        mutations = [
            ('drop', 'S_after[.CODE[0] = pcode_peer_cast[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_cast.EXPRESSIONS, ' + target + ', eps)]]'),
            ('flip', 'S_after[.CODE[0] = pcode_peer_cast[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_cast.EXPRESSIONS, ' + target + ', (true))]]'),
            ('line', 'S_after[.CODE[0] = pcode_peer_cast[.EXPRESSIONS = (CODEEXPR ' + target + ' 0 false) :: pcode_peer_cast.EXPRESSIONS]]'),
            ('precision', 'S_after[.POOLS[0] = ppool_peer_cast[.CONSTANTS = (PCCPRECISION ' + target + ' 17) :: ppool_peer_cast.CONSTANTS]]'),
            ('source', 'S_after[.SOURCES[0] = pcunit_peer_cast[.OCCURRENCES = (PCOCCURRENCE ' + target + ' (NExprVariable (BYTES "dW5hdXRo") eps)) :: pcunit_peer_cast.OCCURRENCES]]'),
        ]
        for label, replacement in mutations:
            state = 'S_peer_cast_' + tag + '_' + label
            guards += [state + ' = ' + replacement,
                       '$string_read_runtime_value(' + state + ', porigin_operator) = eps',
                       '$string_read_runtime_bytes(' + state + ', porigin_key) = eps',
                       '$string_read_request_base_saved(' + state + ', pstringread) = eps']
        if tree[0] == 'CAST':
            result = tree[-1]
            state = 'S_peer_cast_' + tag + '_pool'
            guards += [state + ' = S_after[.POOLS[0] = ppool_peer_cast[.CONSTANTS = (PCONSTANT ' + target + ' (PINT 99)) :: ppool_peer_cast.CONSTANTS]]',
                       '$compiled_read(' + state + ', ' + origin + ') = eps',
                       '$string_read_runtime_value(' + state + ', ' + origin + ') = (' + result + ')',
                       '$string_read_runtime_value(S_after[.RESULT = KNOWN (PINT 99)], ' + origin + ') = (' + result + ')',
                       '$string_read_runtime_value(S_after[.POOLS = eps], ' + origin + ') = eps']
            for label, completion in (('budget', 'BUDGET'), ('pending', 'SOURCE_PENDING'),
                                      ('unsupported', 'UNSUPPORTED "peer_cast"'), ('exited', 'EXITED 0'),
                                      ('thrown', 'THROWN "Error" ($ptascii("peer_cast")) 5')):
                state = 'S_peer_cast_' + tag + '_' + label
                guards += [state + ' = S_after[.COMPLETION = ' + completion + '][.RESULT = KNOWN (' + result + ')]',
                           '$cast_apply(' + state + ', ' + tree[1] + ', PBOOL true, 5) = ' + state,
                           '$string_read_runtime_value(' + state + ', ' + origin + ') = eps',
                           '$string_read_runtime_bytes(' + state + ', porigin_key) = eps',
                           '$string_read_request_base_saved(' + state + ', pstringread) = eps']
    if index == 1:
        guards += ['porigin_operator_0_0_0 = PORIGIN 0 pcpath_peer_cast_leaf']
        for label, value in (('nan', 'PFLOAT 9221120237041090560'), ('negative_nan', 'PFLOAT 18444492273895866368'),
                             ('payload_nan', 'PFLOAT 9221120237041090561'), ('invalid', 'PFLOAT 18446744073709551616'),
                             ('integer', 'PINT 1'), ('boolean', 'PBOOL true'), ('null', 'PNULL'),
                             ('string', 'PSTRING ($ptascii("1.5"))'), ('array', 'PARRAY 0'), ('object', 'POBJECT 0')):
            state = 'S_peer_cast_leaf_' + label
            guards += [state + ' = S_after[.POOLS[0] = ppool_peer_cast[.CONSTANTS = (PCONSTANT pcpath_peer_cast_leaf (' + value + ')) :: ppool_peer_cast.CONSTANTS]]',
                       '$compiled_read(' + state + ', porigin_operator_0_0_0) = (' + value + ')',
                       '$string_read_runtime_value(' + state + ', porigin_operator) = eps',
                       '$string_read_request_base_saved(' + state + ', pstringread) = eps']
    if index == 0:
        for value in ('PUNDEFINED', 'PSTRING ($ptascii("1"))',
                      'PARRAY 0', 'POBJECT 0', 'PINT 9223372036854775808', 'PINT $(-9223372036854775809)'):
            for operator in ('CASTBOOL', 'CASTINT', 'CASTFLOAT'):
                guards += ['~$string_read_runtime_cast_quiet(' + operator + ', ' + value + ')']
        for operator in ('CASTBOOL', 'CASTINT', 'CASTFLOAT'):
            guards += ['$string_read_runtime_cast_quiet(' + operator + ', PNULL)',
                       '$string_read_runtime_cast_quiet(' + operator + ', PSTRING_CARRIER INTERNED_STRING ($ptascii("1")))']
        for operator in ('CASTSTRING', 'CASTARRAY', 'CASTOBJECT'):
            guards += ['~$string_read_runtime_cast_quiet(' + operator + ', PBOOL true)']
        for number, (name, fixture, original, target, node, expected) in enumerate(CONTROLS):
            state, origin = 'S_peer_cast_control_' + str(number), 'porigin_peer_cast_control_' + str(number)
            normal, output = state + '_normal', 'eps' if expected is None else '(' + expected + ')'
            guards += [state + ' = $php_run(' + fixture + ', 0, ' + json.dumps(base64.b64encode(bytes(original)).decode()) + ')',
                       state + '.COMPLETION = BUDGET', origin + ' = PORIGIN 0 ' + occurrences.path_term(target),
                       '$origin_node(' + state + '.SOURCES, ' + origin + ') = (' + occurrences.node_term(node) + ')',
                       origin + ' = PORIGIN 0 pcpath_peer_cast_control_' + str(number),
                       '$code_at(' + state + '.CODE, 0) = (pcode_peer_cast_control_' + str(number) + ')',
                       '$code_expression(pcode_peer_cast_control_' + str(number) + '.EXPRESSIONS, pcpath_peer_cast_control_' + str(number) + ') = ((1, false))',
                       '$compiled_read(' + state + ', ' + origin + ') = eps',
                       '$compiled_precision(' + state + ', (' + origin + ')) = (14)',
                       '$string_read_runtime_value(' + state + ', ' + origin + ') = eps',
                       normal + ' = ' + state + '[.COMPLETION = NORMAL]',
                       '$string_read_runtime_value(' + normal + ', ' + origin + ') = ' + output,
                       '$string_read_runtime_bytes(' + normal + ', ' + origin + ') = ' +
                       ('($echo_value(' + expected + '))' if expected is not None and not expected.startswith('PFLOAT ') else 'eps'),
                       '$string_read_runtime_value(' + normal + '[.RESULT = KNOWN (PINT 99)], ' + origin + ') = ' + output]
            if name == 'int_infinity':
                suppressed = normal + '_suppressed'
                guards += ['$float_long(9218868437227405312, false) = (0, [RANGEWARNING])',
                           '~$string_read_runtime_cast_quiet(CASTINT, PFLOAT 9218868437227405312)',
                           '$cast_apply(' + normal + ', CASTINT, PFLOAT 9218868437227405312, 1) =/= ' + normal + '[.RESULT = KNOWN (PINT 0)]',
                           suppressed + ' = ' + normal + '[.REPORTING = 0]',
                           '$cast_apply(' + suppressed + ', CASTINT, PFLOAT 9218868437227405312, 1) = ' + suppressed + '[.RESULT = KNOWN (PINT 0)]',
                           '$string_read_runtime_value(' + suppressed + ', ' + origin + ') = eps']
    return checks + guards, derived + len(guards)


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    prep = output.with_name(output.name + '-control-prep')
    prep.mkdir(parents=True)
    truth, false = '(!0.0)', '(!INF)'
    one, zero = '(+' + truth + ')', '(+' + false + ')'
    fraction, negative_zero = '(1.5+' + zero + ')', '-(0.0+' + zero + ')'
    infinity = '(INF+' + zero + ')'
    raw = []
    for cast, prefix in (('bool', 'PBOOL true'), ('int', 'PINT 1'), ('float', 'PFLOAT 4607182418800017408')):
        for kind, child in (('bool', truth), ('int', one), ('float', fraction)):
            result = 'PFLOAT 4609434218613702656' if cast == kind == 'float' else prefix
            raw.append((cast + '_' + kind, '(' + cast + ')' + child, result))
    raw += [
        ('bool_zero', '(bool)' + zero, 'PBOOL false'),
        ('int_fraction_negative', '(int)(-' + fraction + ')', 'PINT $(-1)'),
        ('int_negative_zero', '(int)(' + negative_zero + ')', 'PINT 0'),
        ('bool_negative_zero', '(bool)(' + negative_zero + ')', 'PBOOL false'),
        ('float_negative_zero', '(float)(' + negative_zero + ')', 'PFLOAT 9223372036854775808'),
        ('bool_infinity', '(bool)' + infinity, 'PBOOL true'),
        ('float_infinity', '(float)' + infinity, 'PFLOAT 9218868437227405312'),
        ('int_infinity', '(int)' + infinity, None),
        ('int_negative_infinity', '(int)(-' + infinity + ')', None),
        ('int_upper_limit', '(int)(9223372036854775808.0+' + zero + ')', None),
        ('int_lower_limit', '(int)(-9223372036854775808.0+' + zero + ')', 'PINT $(-9223372036854775808)'),
        ('int_upper_adjacent', '(int)(9223372036854774784.0+' + zero + ')', 'PINT 9223372036854774784'),
        ('int_below_lower', '(int)(-9223372036854777856.0+' + zero + ')', None),
        ('nested_float_int', '(float)((int)' + fraction + ')', 'PFLOAT 4607182418800017408'),
        ('nested_bool_float', '(bool)((float)' + zero + ')', 'PBOOL false'),
        ('nested_int_bool', '(int)((bool)' + fraction + ')', 'PINT 1'),
        ('nan_bool', '(bool)(NAN+' + one + ')', None),
        ('nan_int', '(int)(NAN+' + one + ')', None),
        ('nan_float', '(float)(NAN+' + one + ')', None),
        ('quiet_string', "(int)('1.5'." + false + ')', None),
        ('warning_string', "(float)('1.5x'." + false + ')', None),
        ('variable', '(int)$missing', None),
        ('string_cast', '(string)' + truth, None),
        ('array_cast', '(array)' + truth, None),
    ]
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
    kinds = ('Expr_Cast_Bool', 'Expr_Cast_Int', 'Expr_Cast_Double', 'Expr_Cast_String', 'Expr_Cast_Array')
    for name, expression, expected in raw:
        targets = [(path, node) for index, statement in enumerate(parsed[name]['ast']['program'])
                   for path, node in occurrences.expected(statement, [('INDEX', index)]) if node['node'] in kinds]
        target, node = min(targets, key=lambda item: len(item[0]))
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
    report['scope'] = ('Exact author prefixes plus independent demanded cast/child source, CODE/line/precision, missing pools, ignored own nonfolded pools, stale RESULT and five nonnormal completion refusals. Genuine NaN/invalid/forged type and owning leaf substitutions refuse. Thirty-three checked-source controls retain their actual BUDGET state before explicitly derived NORMAL fixtures check all nine BOOL/INT/FLOAT combinations, signed zero, fractions, infinities, adjacent signed64 float limits, nested casts and excluded nonliteral string/variable/array producers. Exact canonical INTERNED strings now pass all three primitive cast helpers; raw PSTRING and REQUEST inputs stay refused. Suppressed infinity-to-int full-state equality still refuses the pure quiet certificate through its RANGEWARNING guard. Runtime FLOAT VALUE retains BYTE eps. Existing REQUEST owners, supplied Throwable, bounds, cleanup and budget rejoining are inherited unchanged. These fixtures add source0/native0, with no source/native replay, live-state normalization, formatter/compiler/schema/API/kernel/owner changes or held-boundary expansion.')
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
