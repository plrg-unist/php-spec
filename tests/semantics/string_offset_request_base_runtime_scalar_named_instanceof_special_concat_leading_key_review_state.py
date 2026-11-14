#!/usr/bin/env python3
"""Independent scalar instanceof source, target and full-state controls."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import source_occurrences as occurrences
import string_offset_request_base_float_boolnot_special_concat_leading_key_review_state as helpers
import string_offset_request_base_runtime_scalar_named_instanceof_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_scalar_named_instanceof_special_concat_leading_key_protocol as source

runner = source.runner
CONTROLS = []


def links(tree, tag='operator'):
    yield tag, tree
    kind = tree[0]
    if kind in ('FLOAT', 'STRING', 'COMPILED'):
        return
    if kind == 'TERNARY':
        children = ((0, tree[1]), (1 if tree[-1] else 2, tree[2]))
    else:
        children = enumerate(tree[2:3] if kind == 'CAST' else tree[1:3] if kind in ('IDENTICAL', 'ADD') else tree[1:2])
    for index, child in children:
        yield from links(child, tag + '_' + str(index))


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    guards = ['pcode_peer_instanceof = S_after.CODE[0]', 'ppool_peer_instanceof = S_after.POOLS[0]',
              'pcunit_peer_instanceof = S_after.SOURCES[0]']
    for tag, tree in links(source.TREES[index]):
        if tree[0] != 'INSTANCEOF':
            continue
        origin, target = 'porigin_' + tag, 'pcpath_peer_instanceof_' + tag
        child, name_origin = origin + '_0', origin + '_name'
        child_value = source.value([], tag + '_0', tree[1])[0]
        requested = '$ptascii(' + json.dumps(tree[2]) + ')'
        guards += [origin + ' = PORIGIN 0 ' + target,
                   child + ' = PORIGIN 0 ' + target + '_child',
                   name_origin + ' = PORIGIN 0 ' + target + '_name']

        def refused(state):
            return ['$string_read_runtime_value(' + state + ', ' + origin + ') = eps',
                    '$string_read_runtime_value(' + state + ', porigin_operator) = eps',
                    '$string_read_runtime_bytes(' + state + ', porigin_key) = eps',
                    '$string_read_request_base_saved(' + state + ', pstringread) = eps']

        mutations = [
            ('drop', 'S_after[.CODE[0] = pcode_peer_instanceof[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_instanceof.EXPRESSIONS, ' + target + ', eps)]]'),
            ('flip', 'S_after[.CODE[0] = pcode_peer_instanceof[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_instanceof.EXPRESSIONS, ' + target + ', (true))]]'),
            ('line', 'S_after[.CODE[0] = pcode_peer_instanceof[.EXPRESSIONS = (CODEEXPR ' + target + ' 0 false) :: pcode_peer_instanceof.EXPRESSIONS]]'),
            ('names_missing', 'S_after[.CODE[0] = pcode_peer_instanceof[.NAMES = eps]]'),
            ('target', 'S_after[.CODE[0] = pcode_peer_instanceof[.NAMES = (CODENAME ' + target + ' ($ptascii("Other")) eps) :: pcode_peer_instanceof.NAMES]]'),
            ('fallback', 'S_after[.CODE[0] = pcode_peer_instanceof[.NAMES = (CODENAME ' + target + ' (' + requested + ') ($ptascii("Other"))) :: pcode_peer_instanceof.NAMES]]'),
            ('context', 'S_after[.CONSTCONTEXT = ({ORIGIN ' + origin + ', LINE 5, FACTS eps})]'),
        ]
        for suffix in ('', '_child', '_name'):
            mutations += [('source' + suffix, 'S_after[.SOURCES[0] = pcunit_peer_instanceof[.OCCURRENCES = (PCOCCURRENCE ' + target + suffix + ' (NExprVariable (BYTES "dW5hdXRo") eps)) :: pcunit_peer_instanceof.OCCURRENCES]]')]
        for suffix in ('', '_child'):
            mutations += [('precision' + suffix, 'S_after[.POOLS[0] = ppool_peer_instanceof[.CONSTANTS = (PCCPRECISION ' + target + suffix + ' 17) :: ppool_peer_instanceof.CONSTANTS]]')]
        for label, completion in (('budget', 'BUDGET'), ('pending', 'SOURCE_PENDING'),
                                  ('unsupported', 'UNSUPPORTED "peer_instanceof"'), ('exited', 'EXITED 0'),
                                  ('thrown', 'THROWN "Error" ($ptascii("peer_instanceof")) 5')):
            mutations += [(label, 'S_after[.COMPLETION = ' + completion + '][.RESULT = KNOWN (PBOOL false)]')]
        for label, replacement in mutations:
            state = 'S_peer_instanceof_' + tag + '_' + label
            guards += [state + ' = ' + replacement, *refused(state)]

        # Coherent root/name/CODE substitutions isolate the lexical target gates.
        for number, (constructor, text) in enumerate((('NName', 'SeLf'), ('NName', 'PaReNt'), ('NName', 'StAtIc'),
                                                     ('NName', 'A\\B'), ('NName', ''), ('NName', '1Bad'), ('NName', 'A\0B'),
                                                     ('NNameFullyQualified', 'stdClass'), ('NNameRelative', 'stdClass'))):
            name = constructor + ' (BYTES ' + json.dumps(base64.b64encode(text.encode()).decode()) + ') eps'
            node = 'NExprInstanceof expression_' + tag + '_0 (' + name + ') eps'
            state = 'S_peer_instanceof_' + tag + '_lexical_' + str(number)
            guards += [state + ' = S_after[.SOURCES[0] = pcunit_peer_instanceof[.OCCURRENCES = (PCOCCURRENCE ' + target + ' (' + node + ')) :: (PCOCCURRENCE ' + target + '_name (' + name + ')) :: pcunit_peer_instanceof.OCCURRENCES]][.CODE[0] = pcode_peer_instanceof[.NAMES = (CODENAME ' + target + ' (' + str(list(text.encode())) + ') eps) :: pcode_peer_instanceof.NAMES]]',
                       *refused(state)]

        whole = 'S_peer_instanceof_' + tag + '_whole'
        ignored = 'S_peer_instanceof_' + tag + '_ignored_pool'
        guards += [whole + ' = S_after[.RESULT = KNOWN (PINT 99)][.TODO = [VALUE_COPY 11]][.BASE = BASE_VALUE (KNOWN (PINT 99))]',
                   '$resolve_at(' + whole + ', KNOWN (' + child_value + '), 5) = ' + whole + '[.RESULT = KNOWN (' + child_value + ')]',
                   '~$class_instanceof(' + whole + '[.RESULT = KNOWN (' + child_value + ')], ' + child_value + ', ' + requested + ')',
                   '$string_read_runtime_value(' + whole + ', ' + origin + ') = (PBOOL false)',
                   ignored + ' = S_after[.POOLS[0] = ppool_peer_instanceof[.CONSTANTS = (PCONSTANT ' + target + ' (PBOOL true)) :: ppool_peer_instanceof.CONSTANTS]]',
                   '$compiled_read(' + ignored + ', ' + origin + ') = eps',
                   '$string_read_runtime_value(' + ignored + ', ' + origin + ') = (PBOOL false)',
                   '$string_read_runtime_bytes(' + ignored + ', porigin_key) = $string_read_runtime_bytes(S_after, porigin_key)']
    if index == 0:
        for number, (name, fixture, original, target, node, accepted) in enumerate(CONTROLS):
            state, origin = 'S_peer_instanceof_control_' + str(number), 'porigin_peer_instanceof_control_' + str(number)
            normal = state + '_normal'
            expected = '(PBOOL false)' if accepted else 'eps'
            guards += [state + ' = $php_run(' + fixture + ', 0, ' + json.dumps(base64.b64encode(bytes(original)).decode()) + ')',
                       state + '.COMPLETION = BUDGET', origin + ' = PORIGIN 0 ' + occurrences.path_term(target),
                       '$origin_node(' + state + '.SOURCES, ' + origin + ') = (' + occurrences.node_term(node) + ')',
                       '$compiled_read(' + state + ', ' + origin + ') = eps',
                       '$string_read_runtime_value(' + state + ', ' + origin + ') = eps',
                       normal + ' = ' + state + '[.COMPLETION = NORMAL]',
                       '$string_read_runtime_value(' + normal + ', ' + origin + ') = ' + expected,
                       '$string_read_runtime_bytes(' + normal + ', ' + origin + ') = ' + ('(eps)' if accepted else 'eps'),
                       '$string_read_runtime_value(' + normal + '[.RESULT = KNOWN (PBOOL true)], ' + origin + ') = ' + expected]
        for bits in (9221120237041090560, 18444492273895866368, 9221120237041090561, 9218868437227405313):
            guards += ['$pfcast_nan(PFLOAT ' + str(bits) + ')']
        for bits in (0, 9223372036854775808, 1, 9218868437227405312, 18442240474082181120):
            guards += ['~$pfcast_nan(PFLOAT ' + str(bits) + ')']
    return checks + guards, derived + len(guards)


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    prep = output.with_name(output.name + '-control-prep')
    prep.mkdir(parents=True)
    true, false = '(!0.0)', '(!INF)'
    operand = lambda text: '(' + true + '?' + text + ':(1/0))'
    raw = [(name, '<?php $x=(' + expression + ') instanceof MissingStringReadTarget;', accepted)
           for name, expression, accepted in (
               ('null', operand('null'), True), ('minimum', operand('PHP_INT_MIN'), True),
               ('maximum', operand('PHP_INT_MAX'), True), ('negative_zero', operand('-0.0'), True),
               ('finite_float', operand('1.5'), True), ('positive_infinity', operand('INF'), True),
               ('empty_string', operand('""'), True), ('raw_string', operand('"object"'), True),
               ('cast_empty_string', '(string)' + false, True),
               ('nul_string', operand('"a\\0b"'), False), ('array', operand('[1]'), False),
               ('object', operand('new stdClass'), False), ('allocated_string', '"a" . (string)' + true, False),
               ('nan_arithmetic', '((float)' + false + ') * INF', False),
           )]
    raw += [(name, '<?php ' + prefix + '$x=' + ('$left' if name == 'dynamic' else true) + ' instanceof ' + target + ';', accepted)
            for name, prefix, target, accepted in (
                ('fully_qualified', '', '\\stdClass', False), ('qualified', '', 'Other\\Target', False),
                ('relative', '', 'namespace\\Target', False), ('namespaced', 'namespace Ns;', 'Target', False),
                ('renamed_import', 'namespace Ns;use stdClass as Alias;', 'Alias', False),
                ('identity_import', 'namespace Ns;use stdClass;', 'stdClass', True),
                ('dynamic', '$left=' + true + ';', '$target', False), ('case_preserved', '', 'StDcLaSs', True),
            )]
    paths = {name: prep / (name + '.php') for name, *_ in raw}
    for name, program, _ in raw:
        paths[name].write_bytes((program + '\n').encode())
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
    for name, program, accepted in raw:
        targets = [(path, node) for index, statement in enumerate(parsed[name]['ast']['program'])
                   for path, node in occurrences.expected(statement, [('INDEX', index)]) if node['node'] == 'Expr_Instanceof']
        target, node = min(targets, key=lambda item: len(item[0]))
        CONTROLS.append((name, checked[name]['fixture'], paths[name], target, node, accepted))
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
    report['scope'] = 'Exact current author prefixes plus independent root/both-child SOURCE, emitted CODE/line/read/precision, same raw/compiled target without fallback, coherent keyword/invalid/qualified/FQN/relative target refusals, cached nonnormal and CONSTCONTEXT controls, ignored unselected pool and full resolve_at/class_instanceof state preservation. Twenty-two fresh checked-source source0 controls cover NULL, signed64 boundaries, signed zero, finite/infinite FLOAT, canonical INTERNED STRING, NUL/array/object/allocated-string/NaN refusal, namespace/renamed-import/dynamic mismatches and the admitted same-byte identity import/case-preserved name. Explicit NaN classifications retain the nonNaN fence; no fresh native observations, old replay, compiler/formatter/owner changes or exact held-boundary expansion.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
