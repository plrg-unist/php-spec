#!/usr/bin/env python3
"""Independent NULL cast types, source authority and full-state controls."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import source_occurrences as occurrences
import string_offset_request_base_float_boolnot_special_concat_leading_key_review_state as helpers
import string_offset_request_base_runtime_null_cast_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_null_cast_special_concat_leading_key_protocol as source

runner = source.runner
CONTROLS = []


def links(tree, tag='operator'):
    yield tag, tree
    kind = tree[0]
    if kind in ('FLOAT', 'COMPILED', 'NULL_TERNARY'):
        return
    if kind == 'SHORTHAND':
        children = [(0, tree[1])] + ([] if tree[-1] else [(2, tree[2])])
    elif kind == 'COALESCE':
        children = [(0, tree[1])] + ([] if tree[2] is None else [(1, tree[2])])
    else:
        children = enumerate(tree[2:3] if kind in ('CAST', 'FLOAT_UNARY') else tree[2:4] if kind == 'FLOAT_BINARY' else
                             tree[1:3] if kind in ('ADD', 'SUBTRACT', 'MULTIPLY', 'DIVIDE', 'IDENTICAL') else tree[1:2])
    for index, child in children:
        yield from links(child, tag + '_' + str(index))


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    guards = ['pcode_peer_null_cast = S_after.CODE[0]', 'pcode_peer_null_cast.UNIT = 0',
              'ppool_peer_null_cast = S_after.POOLS[0]', 'ppool_peer_null_cast.UNIT = 0',
              'pcunit_peer_null_cast = S_after.SOURCES[0]', 'pcunit_peer_null_cast.ID = 0']
    nodes = dict(links(source.TREES[index]))
    demanded = {tag: tree for tag, tree in nodes.items() if tree[0] == 'CAST'}
    demanded.update({tag + '_0': nodes[tag + '_0'] for tag in tuple(demanded)})

    def refused(state):
        return ['$string_read_runtime_value(' + state + ', porigin_operator) = eps',
                '$string_read_runtime_bytes(' + state + ', porigin_key) = eps',
                '$string_read_request_base_saved(' + state + ', pstringread) = eps']

    for tag, tree in demanded.items():
        origin, target = 'porigin_' + tag, 'pcpath_peer_null_cast_' + tag
        guards.append(origin + ' = PORIGIN 0 ' + target)
        compiled = tree[0] == 'COMPILED'
        mutations = [
            ('drop', 'S_after[.CODE[0] = pcode_peer_null_cast[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_null_cast.EXPRESSIONS, ' + target + ', eps)]]'),
            ('flip', 'S_after[.CODE[0] = pcode_peer_null_cast[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_null_cast.EXPRESSIONS, ' + target + ', (' + ('false' if compiled else 'true') + '))]]'),
            ('precision', 'S_after[.POOLS[0] = ppool_peer_null_cast[.CONSTANTS = (PCCPRECISION ' + target + ' 17) :: ppool_peer_null_cast.CONSTANTS]]'),
            ('source', 'S_after[.SOURCES[0] = pcunit_peer_null_cast[.OCCURRENCES = (PCOCCURRENCE ' + target + ' (NExprVariable (BYTES "dW5hdXRo") eps)) :: pcunit_peer_null_cast.OCCURRENCES]]'),
        ]
        if not compiled:
            mutations += [('line', 'S_after[.CODE[0] = pcode_peer_null_cast[.EXPRESSIONS = (CODEEXPR ' + target + ' 0 false) :: pcode_peer_null_cast.EXPRESSIONS]]')]
        for label, replacement in mutations:
            state = 'S_peer_null_cast_' + tag + '_' + label
            guards += [state + ' = ' + replacement, *refused(state)]
        if compiled:
            state = 'S_peer_null_cast_' + tag + '_line'
            guards += [state + ' = S_after[.CODE[0] = pcode_peer_null_cast[.EXPRESSIONS = (CODEEXPR ' + target + ' 0 true) :: pcode_peer_null_cast.EXPRESSIONS]]',
                       '$string_read_runtime_value(' + state + ', ' + origin + ') = (PNULL)',
                       '$string_read_runtime_value(' + state + ', porigin_operator) = $string_read_runtime_value(S_after, porigin_operator)',
                       '$string_read_runtime_bytes(' + state + ', porigin_key) = $string_read_runtime_bytes(S_after, porigin_key)',
                       '$string_read_request_base_saved(' + state + ', pstringread) = $string_read_request_base_saved(S_after, pstringread)']
        if tree[0] != 'CAST':
            continue
        result, child = tree[-1], source.value([], tag + '_0', tree[2])[0]
        state = 'S_peer_null_cast_' + tag + '_pool'
        guards += [state + ' = S_after[.POOLS[0] = ppool_peer_null_cast[.CONSTANTS = (PCONSTANT ' + target + ' (PINT 99)) :: ppool_peer_null_cast.CONSTANTS]]',
                   '$compiled_read(' + state + ', ' + origin + ') = eps',
                   '$string_read_runtime_value(' + state + ', ' + origin + ') = (' + result + ')',
                   '$string_read_runtime_value(S_after[.RESULT = KNOWN (PINT 99)], ' + origin + ') = (' + result + ')',
                   '$string_read_runtime_value(S_after[.POOLS = eps], ' + origin + ') = eps']
        state = 'S_peer_null_cast_' + tag + '_whole'
        guards += [state + ' = S_after[.RESULT = KNOWN (PINT 99)][.TODO = [VALUE_COPY 11]][.BASE = BASE_VALUE (KNOWN (PINT 99))]',
                   '$cast_apply(' + state + ', ' + tree[1] + ', ' + child + ', 5) = ' + state + '[.RESULT = KNOWN (' + result + ')]']
        for label, completion in (('budget', 'BUDGET'), ('pending', 'SOURCE_PENDING'),
                                  ('unsupported', 'UNSUPPORTED "peer_null_cast"'), ('exited', 'EXITED 0'),
                                  ('thrown', 'THROWN "Error" ($ptascii("peer_null_cast")) 5')):
            state = 'S_peer_null_cast_' + tag + '_' + label
            guards += [state + ' = S_after[.COMPLETION = ' + completion + '][.RESULT = KNOWN (' + result + ')]',
                       '$cast_apply(' + state + ', ' + tree[1] + ', PNULL, 5) = ' + state,
                       '$string_read_runtime_value(' + state + ', ' + origin + ') = eps', *refused(state)]
    if index == 0:
        for operator, result in (('CASTBOOL', 'PBOOL false'), ('CASTINT', 'PINT 0'), ('CASTFLOAT', 'PFLOAT 0')):
            guards += ['$string_read_runtime_cast_quiet(' + operator + ', PNULL)',
                       '$string_read_runtime_cast_quiet(' + operator + ', PSTRING_CARRIER INTERNED_STRING ($ptascii("0")))',
                       '$cast_apply(S_after, ' + operator + ', PNULL, 5) = S_after[.RESULT = KNOWN (' + result + ')]']
            for value in ('PUNDEFINED', 'PSTRING ($ptascii("0"))',
                          'PARRAY 0', 'POBJECT 0', 'PINT 9223372036854775808', 'PINT $(-9223372036854775809)'):
                guards += ['~$string_read_runtime_cast_quiet(' + operator + ', ' + value + ')']
        guards += ['$string_read_runtime_cast_quiet(CASTSTRING, PNULL)']
        for operator in ('CASTARRAY', 'CASTOBJECT'):
            guards += ['~$string_read_runtime_cast_quiet(' + operator + ', PNULL)']
        for number, (name, fixture, original, target, node, expected) in enumerate(CONTROLS):
            state, origin = 'S_peer_null_cast_control_' + str(number), 'porigin_peer_null_cast_control_' + str(number)
            normal, output = state + '_normal', 'eps' if expected is None else '(' + expected + ')'
            guards += [state + ' = $php_run(' + fixture + ', 0, ' + json.dumps(base64.b64encode(bytes(original)).decode()) + ')',
                       state + '.COMPLETION = BUDGET', origin + ' = PORIGIN 0 ' + occurrences.path_term(target),
                       '$origin_node(' + state + '.SOURCES, ' + origin + ') = (' + occurrences.node_term(node) + ')',
                       origin + ' = PORIGIN 0 pcpath_peer_null_cast_control_' + str(number),
                       '$code_at(' + state + '.CODE, 0) = (pcode_peer_null_cast_control_' + str(number) + ')',
                       '$code_expression(pcode_peer_null_cast_control_' + str(number) + '.EXPRESSIONS, pcpath_peer_null_cast_control_' + str(number) + ') = ((1, false))',
                       '$compiled_read(' + state + ', ' + origin + ') = eps',
                       '$compiled_precision(' + state + ', (' + origin + ')) = (14)',
                       '$string_read_runtime_value(' + state + ', ' + origin + ') = eps',
                       normal + ' = ' + state + '[.COMPLETION = NORMAL]',
                       '$string_read_runtime_value(' + normal + ', ' + origin + ') = ' + output,
                       '$string_read_runtime_bytes(' + normal + ', ' + origin + ') = ' +
                       ('($echo_value(' + expected + '))' if expected is not None and not expected.startswith('PFLOAT ') else 'eps'),
                       '$string_read_runtime_value(' + normal + '[.RESULT = KNOWN (PINT 99)], ' + origin + ') = ' + output]
    return checks + guards, derived + len(guards)


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    prep = output.with_name(output.name + '-control-prep')
    prep.mkdir(parents=True)
    truth, false = '(!0.0)', '(!INF)'
    one = '(+' + truth + ')'
    producers = (('raw', 'null'), ('full', '(' + false + '?true:null)'),
                 ('shorthand', '(' + false + '?:null)'), ('coalesce', '(null??null)'))
    results = {'bool': 'PBOOL false', 'int': 'PINT 0', 'float': 'PFLOAT 0'}
    raw = []
    for cast, result in results.items():
        for name, child in producers:
            raw.append((cast + '_' + name, '(' + cast + ')' + child, result))
        for inner in results:
            raw.append((cast + '_nested_' + inner, '(' + cast + ')((' + inner + ')null)', result))
        raw += [(cast + '_selected_true', '(' + cast + ')(' + truth + '?null:(1/0))', result),
                (cast + '_nonnull_false', '(' + cast + ')(false??(1/0))', result)]
    raw += [
        ('string_null', '(string)null', 'PSTRING_CARRIER INTERNED_STRING eps'), ('array_null', '(array)null', None), ('object_null', '(object)null', None),
        ('bool_variable', '(bool)$missing', None), ('int_variable', '(int)$missing', None), ('float_variable', '(float)$missing', None),
        ('selected_variable', '(bool)(null??$missing)', None),
        ('selected_divzero', '(int)(null??(1/0))', None),
        ('selected_nan', '(float)(null??(NAN+' + one + '))', None),
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
    kinds = ('Expr_Cast_Bool', 'Expr_Cast_Int', 'Expr_Cast_Double', 'Expr_Cast_String', 'Expr_Cast_Array', 'Expr_Cast_Object')
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
    report['scope'] = ('Exact author prefixes plus demanded cast/producer source, CODE, emitted positive-line and equal captured-precision refusals; raw compiled NULL retains its existing line and compiler-output authority. Ignored own pools/stale RESULT cannot forge answers; full cast_apply equality preserves nonempty TODO/nondefault BASE and five nonnormal states remain unchanged/refuse certificates. ' + str(len(CONTROLS)) + ' checked-source controls retain actual BUDGET before derived NORMAL fixtures for all three primitive casts of raw/full/shorthand/coalesce NULL, nested casts, emitted NULL-to-empty-INTERNED STRING and exact false/int0/float+0. FLOAT BYTE stays eps. Undefined/location, selected failures, raw/REQUEST STRING, ARRAY/OBJECT and range/type boundaries refuse. Exact canonical INTERNED strings now pass all three primitive cast helpers. The exact three corrected old PNULL helper positives are included, while its FLOAT-forged-PNULL control and old33/1792 evidence remain unchanged and unrenewed. REQUEST owners, supplied Throwable, fixed bounds, cleanup and inherited budget rejoining remain included. Fixture source0/native0; no compiler/cast/numeric/formatter/API/owner or held-boundary expansion.')
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
