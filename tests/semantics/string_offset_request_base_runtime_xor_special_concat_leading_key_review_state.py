#!/usr/bin/env python3
"""Independent XOR truth, NORMAL-state and emitted authority controls."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import source_occurrences as occurrences
import string_offset_request_base_float_boolnot_special_concat_leading_key_review_state as prior
import string_offset_request_base_runtime_xor_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_xor_special_concat_leading_key_protocol as source

runner = source.runner
KEYS = ('1x', '-1x', '0x', '-4x')
CONTROLS = []


def xor_links(tree, tag='operator'):
    if tree[0] == 'FLOAT':
        return
    if tree[0] == 'LOGICALXOR':
        yield tag, False
        yield tag + '_0', tree[1][0] == 'FLOAT'
        yield tag + '_1', tree[2][0] == 'FLOAT'
    children = tree[1:3] if tree[0] in ('LOGICALXOR', 'ADD') else tree[1:2]
    for index, child in enumerate(children):
        yield from xor_links(child, tag + '_' + str(index))


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    guards = ['pcode_peer_xor = S_after.CODE[0]', 'pcode_peer_xor.UNIT = 0',
              'ppool_peer_xor = S_after.POOLS[0]', 'ppool_peer_xor.UNIT = 0',
              'pcunit_peer_xor = S_after.SOURCES[0]', 'pcunit_peer_xor.ID = 0']
    for tag, leaf in dict(xor_links(source.TREES[index])).items():
        origin, target = 'porigin_' + tag, 'pcpath_peer_xor_' + tag
        guards.append(origin + ' = PORIGIN 0 ' + target)
        mutations = (
            ('drop', 'S_after[.CODE[0] = pcode_peer_xor[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_xor.EXPRESSIONS, ' + target + ', eps)]]'),
            ('flip', 'S_after[.CODE[0] = pcode_peer_xor[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_xor.EXPRESSIONS, ' + target + ', (' + str(not leaf).lower() + '))]]'),
            ('line', 'S_after[.CODE[0] = pcode_peer_xor[.EXPRESSIONS = (CODEEXPR ' + target + ' 0 false) :: pcode_peer_xor.EXPRESSIONS]]'),
            ('precision', 'S_after[.POOLS[0] = ppool_peer_xor[.CONSTANTS = (PCCPRECISION ' + target + ' 17) :: ppool_peer_xor.CONSTANTS]]'),
            ('source', 'S_after[.SOURCES[0] = pcunit_peer_xor[.OCCURRENCES = (PCOCCURRENCE ' + target + ' (NExprVariable (BYTES "dW5hdXRo") eps)) :: pcunit_peer_xor.OCCURRENCES]]'),
        )
        for label, replacement in mutations:
            state = 'S_peer_xor_' + tag + '_' + label
            guards += [state + ' = ' + replacement,
                       '$string_read_runtime_value(' + state + ', porigin_operator) = eps',
                       '$string_read_runtime_bytes(' + state + ', porigin_key) = eps',
                       '$string_read_request_base_saved(' + state + ', pstringread) = eps']
    for label, completion in (('budget', 'BUDGET'), ('unsupported', 'UNSUPPORTED "peer_xor"'),
                              ('pending', 'SOURCE_PENDING'), ('exited', 'EXITED 0')):
        state = 'S_peer_xor_' + label
        guards += [state + ' = S_after[.COMPLETION = ' + completion + '][.RESULT = KNOWN (PBOOL true)]',
                   '$string_read_runtime_value(' + state + ', porigin_operator) = eps',
                   '$string_read_runtime_bytes(' + state + ', porigin_key) = eps',
                   '$string_read_request_base_saved(' + state + ', pstringread) = eps']
    guards += ['S_peer_xor_stale = S_after[.RESULT = KNOWN (PSTRING ($ptascii("stale")))]',
               '$string_read_runtime_bytes(S_peer_xor_stale, porigin_key) = ($ptascii(' + json.dumps(KEYS[index]) + '))']
    if index == 1:
        guards += ['porigin_operator_0_0 = PORIGIN 0 pcpath_peer_xor_float']
        for label, value in (('nan', 'PFLOAT 9221120237041090560'),
                             ('negative_nan', 'PFLOAT 18444492273895866368'),
                             ('payload_nan', 'PFLOAT 9221120237041090561'),
                             ('invalid', 'PFLOAT 18446744073709551616'),
                             ('integer', 'PINT 0'), ('boolean', 'PBOOL false'),
                             ('null', 'PNULL'), ('string', 'PSTRING ($ptascii("0"))')):
            state = 'S_peer_xor_leaf_' + label
            guards += [state + ' = S_after[.POOLS[0] = ppool_peer_xor[.CONSTANTS = (PCONSTANT pcpath_peer_xor_float (' + value + ')) :: ppool_peer_xor.CONSTANTS]]',
                       '$compiled_read(' + state + ', porigin_operator_0_0) = (' + value + ')',
                       '$string_read_runtime_value(' + state + ', porigin_operator) = eps',
                       '$string_read_request_base_saved(' + state + ', pstringread) = eps']
        guards += ['S_peer_xor_signed_zero = S_after[.POOLS[0] = ppool_peer_xor[.CONSTANTS = (PCONSTANT pcpath_peer_xor_float (PFLOAT 9223372036854775808)) :: ppool_peer_xor.CONSTANTS]]',
                   '$string_read_runtime_value(S_peer_xor_signed_zero, porigin_operator_0_0) = (PFLOAT 9223372036854775808)',
                   '$string_read_runtime_value(S_peer_xor_signed_zero, porigin_operator_0) = (PBOOL true)',
                   '$string_read_runtime_bytes(S_peer_xor_signed_zero, porigin_key) = ($ptascii("-1x"))',
                   '$string_read_request_base_saved(S_peer_xor_signed_zero, pstringread) = ($(-1))']
    if index == 0:
        guards += ['$string_read_runtime_value(S_peer_xor_budget, porigin_operator_0) = (PBOOL true)',
                   '$string_read_runtime_value(S_peer_xor_budget, porigin_operator_1) = (PBOOL false)']
        for left in ('false', 'true'):
            for right in ('false', 'true'):
                result = str(left != right).lower()
                operands = 'PBOOL ' + left + ', PBOOL ' + right + ', 5'
                guards += ['$binary_apply(S_after, LOGICALXOR, ' + operands + ') = S_after[.RESULT = KNOWN (PBOOL ' + result + ')]',
                           '$binary_apply(S_peer_xor_budget, LOGICALXOR, ' + operands + ') = S_peer_xor_budget[.RESULT = KNOWN (PBOOL ' + left + ')]']
        for number, (name, fixture, control, target, node, result) in enumerate(CONTROLS):
            state, origin = 'S_peer_xor_control_' + str(number), 'porigin_peer_xor_control_' + str(number)
            expected = 'eps' if result is None else '(' + result + ')'
            guards += [state + '_budget = $php_run(' + fixture + ', 0, ' + json.dumps(base64.b64encode(bytes(control)).decode()) + ')',
                       state + '_budget.COMPLETION = BUDGET',
                       origin + ' = PORIGIN 0 ' + occurrences.path_term(target),
                       '$string_read_runtime_value(' + state + '_budget, ' + origin + ') = eps',
                       state + ' = ' + state + '_budget[.COMPLETION = NORMAL]',
                       '$origin_node(' + state + '.SOURCES, ' + origin + ') = (' + occurrences.node_term(node) + ')',
                       origin + ' = PORIGIN 0 pcpath_peer_xor_control_' + str(number),
                       '$code_at(' + state + '.CODE, 0) = (pcode_peer_xor_control_' + str(number) + ')',
                       '$code_expression(pcode_peer_xor_control_' + str(number) + '.EXPRESSIONS, pcpath_peer_xor_control_' + str(number) + ') = ((1, false))',
                       '$compiled_read(' + state + ', ' + origin + ') = eps',
                       '$compiled_precision(' + state + ', (' + origin + ')) = (14)',
                       '$string_read_runtime_value(' + state + ', ' + origin + ') = ' + expected,
                       state + '_stale = ' + state + '[.RESULT = KNOWN (PBOOL true)]',
                       '$string_read_runtime_value(' + state + '_stale, ' + origin + ') = ' + expected]
    return checks + guards, derived + len(guards)


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    prep = output.with_name(output.name + '-control-prep')
    prep.mkdir(parents=True)
    one, zero = '(!0.0)', '(!INF)'
    two = '(' + one + '+' + one + ')'
    raw = (
        ('false_false', zero + ' xor ' + zero, 'PBOOL false'),
        ('false_true', zero + ' xor ' + one, 'PBOOL true'),
        ('true_false', one + ' xor ' + zero, 'PBOOL true'),
        ('true_true', one + ' xor ' + one, 'PBOOL false'),
        ('float_zero_integer', '0.0 xor (+' + one + ')', 'PBOOL true'),
        ('integer_zero_signed_zero', '(+' + zero + ') xor (-0.0)', 'PBOOL false'),
        ('infinity_integer', 'INF xor (+' + zero + ')', 'PBOOL true'),
        ('integer_float', two + ' xor 0.0', 'PBOOL true'),
        ('integer_bool', two + ' xor ' + one, 'PBOOL false'),
        ('bool_integer', one + ' xor ' + two, 'PBOOL false'),
        ('negative_integer_float', '(-(+' + one + ')) xor 0.0', 'PBOOL true'),
        ('nested_xor', '(' + one + ' xor ' + zero + ') xor ' + one, 'PBOOL false'),
        ('nested_not', '!(' + one + ' xor ' + zero + ')', 'PBOOL false'),
        ('nested_greater', '(' + one + ' xor ' + zero + ')>(+' + zero + ')', 'PBOOL true'),
        ('nested_spaceship', '(' + one + ' xor ' + zero + ')<=>' + two, 'PINT 0'),
        ('compiled_integer', '1 xor ' + one, None),
        ('compiled_boolean', 'true xor ' + one, None),
        ('null', 'null xor ' + one, None),
        ('string', "'1' xor " + zero, None),
        ('array', '[] xor ' + one, None),
        ('object', '(new stdClass()) xor ' + zero, None),
        ('nan_left', 'NAN xor ' + one, None),
        ('nan_right', one + ' xor NAN', None),
        ('runtime_float', '(0.0+(+' + zero + ')) xor ' + one, 'PBOOL true'),
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
                   if node['node'] in ('Expr_BinaryOp_LogicalXor', 'Expr_BooleanNot', 'Expr_BinaryOp_Greater', 'Expr_BinaryOp_Spaceship')]
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
    report['scope'] = ('Exact author prefixes plus independent own/both-child source/CODE/line/precision, typed/invalid/NaN leaf and stale-result controls. Every XOR tree refuses BUDGET/Unsupported/source-pending/exited certificates, including the RHSfalse coincidence where the unchanged51 binary_apply returns only left truth. Twenty-four checked-source compiled states retain BUDGET refusal before explicitly derived NORMAL fixture states check16 admitted truth/type/nesting results and8 refused wider leaves/producers; no live state is normalized. All four Boolean truth pairs, signed zero/infinity, both mixed-type directions and nested XOR/NOT/greater/spaceship remain distinct. Signed-zero substitution retains the compiler-pool trust boundary. Fixture source0/native0; no51/compiler/schema/API/387/kernel/owner changes or source/native replay.')
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
