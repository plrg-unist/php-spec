#!/usr/bin/env python3
"""Independent immutable string casts, typed inputs and allocation refusals."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import source_occurrences as occurrences
import string_offset_request_base_float_boolnot_special_concat_leading_key_review_state as helpers
import string_offset_request_base_runtime_interned_string_cast_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_interned_string_cast_special_concat_leading_key_protocol as source

runner = source.runner
CONTROLS = []


def carrier(text):
    return 'PSTRING_CARRIER INTERNED_STRING ($ptascii(' + json.dumps(text) + '))'


def links(tree, tag='operator'):
    yield tag, tree
    kind = tree[0]
    if kind in ('FLOAT', 'STRING', 'NULL_TERNARY'):
        return
    children = tree[2:3] if kind == 'CAST' else tree[1:3] if kind == 'ADD' else tree[1:2]
    for index, child in enumerate(children):
        yield from links(child, tag + '_' + str(index))


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    guards = ['pcode_peer_interned_cast = S_after.CODE[0]', 'ppool_peer_interned_cast = S_after.POOLS[0]',
              'pcunit_peer_interned_cast = S_after.SOURCES[0]']
    nodes = dict(links(source.TREES[index]))
    casts = {tag: tree for tag, tree in nodes.items() if tree[0] == 'CAST'}
    demanded = dict(casts)
    demanded.update({tag + '_0': nodes[tag + '_0'] for tag in casts})
    for tag in demanded:
        origin, target = 'porigin_' + tag, 'pcpath_peer_interned_cast_' + tag
        guards += [origin + ' = PORIGIN 0 ' + target]
        mutations = [('drop', 'S_after[.CODE[0] = pcode_peer_interned_cast[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_interned_cast.EXPRESSIONS, ' + target + ', eps)]]'),
                     ('flip', 'S_after[.CODE[0] = pcode_peer_interned_cast[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_interned_cast.EXPRESSIONS, ' + target + ', (true))]]'),
                     ('line', 'S_after[.CODE[0] = pcode_peer_interned_cast[.EXPRESSIONS = (CODEEXPR ' + target + ' 0 false) :: pcode_peer_interned_cast.EXPRESSIONS]]'),
                     ('precision', 'S_after[.POOLS[0] = ppool_peer_interned_cast[.CONSTANTS = (PCCPRECISION ' + target + ' 17) :: ppool_peer_interned_cast.CONSTANTS]]'),
                     ('source', 'S_after[.SOURCES[0] = pcunit_peer_interned_cast[.OCCURRENCES = (PCOCCURRENCE ' + target + ' (NExprVariable (BYTES "dW5hdXRo") eps)) :: pcunit_peer_interned_cast.OCCURRENCES]]')]
        for label, replacement in mutations:
            state = 'S_peer_interned_cast_' + tag + '_' + label
            guards += [state + ' = ' + replacement,
                       '$string_read_runtime_value(' + state + ', porigin_operator) = eps',
                       '$string_read_runtime_bytes(' + state + ', porigin_key) = eps',
                       '$string_read_request_base_saved(' + state + ', pstringread) = eps']
    for tag, tree in casts.items():
        origin, expected = 'porigin_' + tag, tree[-1]
        for label, completion in (('budget', 'BUDGET'), ('pending', 'SOURCE_PENDING'),
                                  ('unsupported', 'UNSUPPORTED "peer_interned_cast"'), ('exited', 'EXITED 0'),
                                  ('thrown', 'THROWN "Error" ($ptascii("peer_interned_cast")) 5')):
            state = 'S_peer_interned_cast_' + tag + '_' + label
            guards += [state + ' = S_after[.COMPLETION = ' + completion + '][.RESULT = KNOWN (' + expected + ')]',
                       '$cast_apply(' + state + ', ' + tree[1] + ', PBOOL true, 5) = ' + state,
                       '$string_read_runtime_value(' + state + ', ' + origin + ') = eps']
        if tree[1] == 'CASTSTRING':
            child = source.value([], tag + '_0', tree[2])[0]
            whole = 'S_peer_interned_cast_' + tag + '_whole'
            guards += [whole + ' = S_after[.RESULT = KNOWN (PINT 99)][.TODO = [VALUE_COPY 11]][.BASE = BASE_VALUE (KNOWN (PINT 99))]',
                       '$cast_apply(' + whole + ', CASTSTRING, ' + child + ', 5) = ' + whole + '[.RESULT = KNOWN (' + expected + ')]',
                       '$string_read_runtime_value(' + whole + ', ' + origin + ') = (' + expected + ')']
    if index == 0:
        for value, text in (('PNULL', ''), ('PBOOL false', ''), ('PBOOL true', '1'), ('PINT 0', '0'), ('PINT 9', '9'),
                            (carrier(''), ''), (carrier('0'), '0'), (carrier('00'), '00'), (carrier('nonnumeric'), 'nonnumeric')):
            guards += ['$string_read_runtime_cast_quiet(CASTSTRING, ' + value + ')',
                       '$cast_apply(S_after, CASTSTRING, ' + value + ', 5) = S_after[.RESULT = KNOWN (' + carrier(text) + ')]']
        for value in ('PINT $(-1)', 'PINT 10', 'PINT $(-9223372036854775808)', 'PINT 9223372036854775807',
                      'PINT 9223372036854775808', 'PFLOAT 0', 'PFLOAT 9223372036854775808',
                      'PFLOAT 9218868437227405312', 'PFLOAT 9221120237041090560', 'PUNDEFINED', 'PARRAY 0', 'POBJECT 0',
                      'PSTRING ($ptascii("1"))', 'PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("1"))',
                      'PSTRING_CARRIER INTERNED_STRING ([256])', 'PSTRING_CARRIER INTERNED_STRING ($ptascii("a") ++ [0] ++ $ptascii("b"))'):
            guards += ['~$string_read_runtime_cast_quiet(CASTSTRING, ' + value + ')']
        for value, text in (('PINT $(-1)', '-1'), ('PINT 10', '10')):
            guards += ['$cast_apply(S_after, CASTSTRING, ' + value + ', 5) =/= S_after[.RESULT = KNOWN (' + carrier(text) + ')]']
        for operator in ('CASTARRAY', 'CASTOBJECT'):
            guards += ['~$string_read_runtime_cast_quiet(' + operator + ', PBOOL true)',
                       '~$string_read_runtime_cast_quiet(' + operator + ', ' + carrier('1') + ')']
        for number, (name, fixture, original, target, node, expected) in enumerate(CONTROLS):
            state, origin = 'S_peer_interned_cast_control_' + str(number), 'porigin_peer_interned_cast_control_' + str(number)
            normal, result = state + '_normal', 'eps' if expected is None else '(' + expected + ')'
            guards += [state + ' = $php_run(' + fixture + ', 0, ' + json.dumps(base64.b64encode(bytes(original)).decode()) + ')',
                       state + '.COMPLETION = BUDGET', origin + ' = PORIGIN 0 ' + occurrences.path_term(target),
                       '$origin_node(' + state + '.SOURCES, ' + origin + ') = (' + occurrences.node_term(node) + ')',
                       origin + ' = PORIGIN 0 pcpath_peer_interned_cast_control_' + str(number),
                       '$code_at(' + state + '.CODE, 0) = (pcode_peer_interned_cast_control_' + str(number) + ')',
                       '$code_expression(pcode_peer_interned_cast_control_' + str(number) + '.EXPRESSIONS, pcpath_peer_interned_cast_control_' + str(number) + ') = ((1, false))',
                       '$compiled_precision(' + state + ', (' + origin + ')) = (14)',
                       '$compiled_read(' + state + ', ' + origin + ') = eps',
                       '$string_read_runtime_value(' + state + ', ' + origin + ') = eps',
                       normal + ' = ' + state + '[.COMPLETION = NORMAL]',
                       '$string_read_runtime_value(' + normal + ', ' + origin + ') = ' + result,
                       '$string_read_runtime_bytes(' + normal + ', ' + origin + ') = ' + ('eps' if expected is None else '($echo_value(' + expected + '))'),
                       '$string_read_runtime_value(' + normal + '[.RESULT = KNOWN (PINT 99)], ' + origin + ') = ' + result]
            if name == 'identity':
                leaf = occurrences.path_term(target + [('FIELD', 0), ('FIELD', 1)])
                pool = 'ppool_peer_interned_cast_identity'
                guards += [pool + ' = ' + normal + '.POOLS[0]']
                for label, forged in (('raw', 'PSTRING ($ptascii("other"))'),
                                      ('request', 'PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("nonnumeric"))')):
                    bad = normal + '_' + label
                    guards += [bad + ' = ' + normal + '[.POOLS[0] = ' + pool + '[.CONSTANTS = (PCONSTANT ' + leaf + ' (' + forged + ')) :: ' + pool + '.CONSTANTS]]',
                               '$string_read_runtime_value(' + bad + ', ' + origin + ') = eps',
                               '$string_read_runtime_bytes(' + bad + ', ' + origin + ') = eps']
    return checks + guards, derived + len(guards)


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    prep = output.with_name(output.name + '-control-prep')
    prep.mkdir(parents=True)
    zero, one = '(+(!INF))', '(+(!0.0))'
    selected = lambda text: "((!0.0)?'" + text + "':(1/0))"
    raw = [('affected_scalar', '(string)(!0.0)', carrier('1')),
           ('affected_null', '(string)null', carrier('')),
           ('affected_literal', '(string)' + selected('1'), carrier('1')),
           ('zero', '(string)' + zero, carrier('0')),
           ('nine', '(string)(9+' + zero + ')', carrier('9')),
           ('ten_allocates', '(string)(10+' + zero + ')', None),
           ('negative_allocates', '(string)(-' + one + ')', None),
           ('max_allocates', '(string)(9223372036854775807+' + zero + ')', None),
           ('float_refused', '(string)(1.0+' + zero + ')', None),
           ('identity', '(string)' + selected('nonnumeric'), carrier('nonnumeric')),
           ('empty_identity', '(string)' + selected(''), carrier('')),
           ('zero_identity', '(string)' + selected('0'), carrier('0')),
           ('double_zero_identity', '(string)' + selected('00'), carrier('00')),
           ('nul_refused', '(string)((!0.0)?"a\\0b":(1/0))', None),
           ('undefined_refused', '(string)$missing', None),
           ('array_refused', '(string)((array)(!0.0))', None),
           ('object_refused', '(string)((object)(!0.0))', None),
           ('zero_boolean', '(bool)((string)' + zero + ')', 'PBOOL false'),
           ('empty_shorthand', '((string)(!INF) ?: (string)' + one + ')', carrier('1')),
           ('empty_coalesce', '((string)(!INF) ?? (1/0))', carrier('')),
           ('nested_identity', '(string)((string)' + selected('01') + ')', carrier('01')),
           ('zero_condition', '(((string)' + zero + ")?'no':'yes')", carrier('yes')),
           ('other_cast_refused', '(array)((string)(!0.0))', None)]
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
    report['scope'] = 'Exact new author histories plus independent demanded CAST/child SOURCE/CODE/line/precision mutations, nonnormal cached-result forgeries and whole-state RESULT/TODO/BASE preservation. Twenty-three fresh checked-source controls include the three affected scalar/NULL/literal STRING casts, immutable digit0/9, allocated -1/10/INTMAX, FLOAT/raw/REQUEST/undefined/array/object/NUL refusals, nonnumeric/empty/zero/double-zero identities, falsey zero truth, empty shorthand versus nonnull coalesce and nested identity. Helper controls retain real typed NULL/BOOL/digit/INTERNED inputs and forbid malformed bytes/other casts. Fixture source0/native0; no accepted old campaign/native replay, formatter/compiler/owner change or held-boundary expansion.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
