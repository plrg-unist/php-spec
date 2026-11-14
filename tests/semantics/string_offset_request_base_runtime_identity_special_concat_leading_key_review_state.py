#!/usr/bin/env python3
"""Independent typed identity, emitted authority and stale-result controls."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import source_occurrences as occurrences
import string_offset_request_base_float_boolnot_special_concat_leading_key_review_state as prior
import string_offset_request_base_runtime_identity_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_identity_special_concat_leading_key_protocol as source

runner = source.runner
KEYS = ('1x', '-1x', '0x', '-4x')
CONTROLS = []


def identities(tree, tag='operator'):
    if tree[0] == 'FLOAT':
        return
    if tree[0] in ('IDENTICAL', 'NOTIDENTICAL'):
        yield tag, False
        yield tag + '_0', tree[1][0] == 'FLOAT'
        yield tag + '_1', tree[2][0] == 'FLOAT'
    children = tree[1:3] if tree[0] in ('IDENTICAL', 'NOTIDENTICAL', 'ADD') else tree[1:2]
    for index, child in enumerate(children):
        yield from identities(child, tag + '_' + str(index))


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    guards = ['pcode_peer_identity = S_after.CODE[0]', 'pcode_peer_identity.UNIT = 0',
              'ppool_peer_identity = S_after.POOLS[0]', 'ppool_peer_identity.UNIT = 0',
              'pcunit_peer_identity = S_after.SOURCES[0]', 'pcunit_peer_identity.ID = 0']
    for tag, leaf in dict(identities(source.TREES[index])).items():
        origin, target = 'porigin_' + tag, 'pcpath_peer_identity_' + tag
        guards.append(origin + ' = PORIGIN 0 ' + target)
        mutations = (
            ('drop', 'S_after[.CODE[0] = pcode_peer_identity[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_identity.EXPRESSIONS, ' + target + ', eps)]]'),
            ('flip', 'S_after[.CODE[0] = pcode_peer_identity[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_identity.EXPRESSIONS, ' + target + ', (' + str(not leaf).lower() + '))]]'),
            ('line', 'S_after[.CODE[0] = pcode_peer_identity[.EXPRESSIONS = (CODEEXPR ' + target + ' 0 false) :: pcode_peer_identity.EXPRESSIONS]]'),
            ('precision', 'S_after[.POOLS[0] = ppool_peer_identity[.CONSTANTS = (PCCPRECISION ' + target + ' 17) :: ppool_peer_identity.CONSTANTS]]'),
            ('source', 'S_after[.SOURCES[0] = pcunit_peer_identity[.OCCURRENCES = (PCOCCURRENCE ' + target + ' (NExprVariable (BYTES "dW5hdXRo") eps)) :: pcunit_peer_identity.OCCURRENCES]]'),
        )
        for label, replacement in mutations:
            state = 'S_peer_identity_' + tag + '_' + label
            guards += [state + ' = ' + replacement,
                       '$string_read_runtime_value(' + state + ', porigin_operator) = eps',
                       '$string_read_runtime_bytes(' + state + ', porigin_key) = eps',
                       '$string_read_request_base_saved(' + state + ', pstringread) = eps']
    guards += ['S_peer_identity_budget = S_after[.COMPLETION = BUDGET][.RESULT = KNOWN (PBOOL false)]',
               '$string_read_runtime_bytes(S_peer_identity_budget, porigin_key) = ($ptascii(' + json.dumps(KEYS[index]) + '))']
    if index == 2:
        guards += ['porigin_operator_0_0 = PORIGIN 0 pcpath_peer_identity_float']
        for label, value in (('nan', 'PFLOAT 9221120237041090560'),
                             ('negative_nan', 'PFLOAT 18444492273895866368'),
                             ('payload_nan', 'PFLOAT 9221120237041090561'),
                             ('invalid', 'PFLOAT 18446744073709551616'),
                             ('integer', 'PINT 0'), ('boolean', 'PBOOL false'),
                             ('null', 'PNULL'), ('string', 'PSTRING ($ptascii("0"))')):
            state = 'S_peer_identity_leaf_' + label
            guards += [state + ' = S_after[.POOLS[0] = ppool_peer_identity[.CONSTANTS = (PCONSTANT pcpath_peer_identity_float (' + value + ')) :: ppool_peer_identity.CONSTANTS]]',
                       '$compiled_read(' + state + ', porigin_operator_0_0) = (' + value + ')',
                       '$string_read_runtime_value(' + state + ', porigin_operator) = eps',
                       '$string_read_request_base_saved(' + state + ', pstringread) = eps']
        guards += ['S_peer_identity_signed_zero = S_after[.POOLS[0] = ppool_peer_identity[.CONSTANTS = (PCONSTANT pcpath_peer_identity_float (PFLOAT 9223372036854775808)) :: ppool_peer_identity.CONSTANTS]]',
                   '$string_read_runtime_value(S_peer_identity_signed_zero, porigin_operator_0_0) = (PFLOAT 9223372036854775808)',
                   '$string_read_runtime_value(S_peer_identity_signed_zero, porigin_operator_0) = (PBOOL false)',
                   '$string_read_runtime_bytes(S_peer_identity_signed_zero, porigin_key) = ($ptascii("0x"))',
                   '$string_read_request_base_saved(S_peer_identity_signed_zero, pstringread) = (0)']
    if index == 0:
        guards += ['$echo_value(PBOOL true) = $echo_value(PINT 1)',
                   '$strict_identical(PBOOL true, PINT 1) = false',
                   '$truth(S_after, PBOOL false) = $truth(S_after, PINT 0)',
                   '$strict_identical(PBOOL false, PINT 0) = false',
                   '$strict_identical(PFLOAT 0, PFLOAT 9223372036854775808) = true',
                   '$strict_identical(PFLOAT 9218868437227405312, PFLOAT 18442240474082181120) = false',
                   '$binary_apply(S_peer_identity_budget, IDENTICAL, PBOOL true, PINT 1, 5) = S_peer_identity_budget[.RESULT = KNOWN (PBOOL false)]',
                   '$binary_apply(S_peer_identity_budget, NOTIDENTICAL, PBOOL true, PINT 1, 5) = S_peer_identity_budget[.RESULT = KNOWN (PBOOL true)]']
        for number, (name, fixture, control, target, node, result) in enumerate(CONTROLS):
            state, origin = 'S_peer_identity_control_' + str(number), 'porigin_peer_identity_control_' + str(number)
            guards += [state + ' = $php_run(' + fixture + ', 0, ' + json.dumps(base64.b64encode(bytes(control)).decode()) + ')',
                       state + '.COMPLETION = BUDGET',
                       origin + ' = PORIGIN 0 ' + occurrences.path_term(target),
                       '$origin_node(' + state + '.SOURCES, ' + origin + ') = (' + occurrences.node_term(node) + ')',
                       origin + ' = PORIGIN 0 pcpath_peer_identity_control_' + str(number),
                       '$code_at(' + state + '.CODE, 0) = (pcode_peer_identity_control_' + str(number) + ')',
                       '$code_expression(pcode_peer_identity_control_' + str(number) + '.EXPRESSIONS, pcpath_peer_identity_control_' + str(number) + ') = ((1, false))',
                       '$compiled_read(' + state + ', ' + origin + ') = eps',
                       '$compiled_precision(' + state + ', (' + origin + ')) = (14)',
                       '$string_read_runtime_value(' + state + ', ' + origin + ') = ' + ('eps' if result is None else '(PBOOL ' + str(result).lower() + ')'),
                       state + '_stale = ' + state + '[.RESULT = KNOWN (PBOOL true)]',
                       '$string_read_runtime_value(' + state + '_stale, ' + origin + ') = ' + ('eps' if result is None else '(PBOOL ' + str(result).lower() + ')')]
    return checks + guards, derived + len(guards)


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    prep = output.with_name(output.name + '-control-prep')
    prep.mkdir(parents=True)
    one, zero = '(!0.0)', '(!INF)'
    raw = (
        ('bool_difference', one + '===' + zero, False),
        ('bool_integer', one + '===(+' + one + ')', False),
        ('integer_bool', '(+' + one + ')!==' + one, True),
        ('nested_not', '!(' + one + '===(+' + one + '))', True),
        ('nested_identity', '(' + one + '===(+' + one + '))===(' + zero + '===' + one + ')', True),
        ('compiled_integer', '1===' + one, None),
        ('compiled_boolean', 'true===' + one, None),
        ('null', 'null===' + one, None),
        ('string', "'1'===" + one, False),
        ('array', '[]===' + one, None),
        ('object', '(new stdClass())===' + one, None),
        ('nan', 'NAN===' + one, None),
        ('negative_nan', '(-NAN)!==' + one, None),
        ('runtime_float', '(0.0+(+' + zero + '))===' + one, None),
    )
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
    for name, expression, result in raw:
        targets = [(path, node) for index, statement in enumerate(parsed[name]['ast']['program'])
                   for path, node in occurrences.expected(statement, [('INDEX', index)])
                   if node['node'] in ('Expr_BinaryOp_Identical', 'Expr_BinaryOp_NotIdentical', 'Expr_BooleanNot')]
        target, node = min(targets, key=lambda item: len(item[0]))
        CONTROLS.append((name, checked[name]['fixture'], paths[name], target, node, result))
    watched = {Path(module.__file__).resolve() for module in tuple(sys.modules.values()) if getattr(module, '__file__', None)
               and Path(module.__file__).resolve().parent == Path(__file__).resolve().parent} | set(paths.values())
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.PREFIX += prior.HELPERS
    runner.cases, runner.OUTPUTS, runner.conditions = cases, tuple(cases.OUTPUTS.values()), conditions
    passed = runner.main()
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = ('Exact author prefixes plus independent own/both-child source/CODE/line/precision, malformed/NaN/typed-leaf and stale BUDGET Boolean-result controls. Fourteen genuine checked-source states distinguish equal string bytes or truth from strict scalar identity, reverse operand types and nested NOT/identity; compiled PINT/PBOOL, NULL/array/object, NaN and runtime FLOAT producers retain refusal; the exact literal-string comparison is admitted. Signed-zero PFLOAT substitution stays admitted at the existing compiler-output boundary. Fixture source0/native0; no compiler/schema/API/387/kernel/owner changes or source/native replay.')
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
