#!/usr/bin/env python3
"""Independent selected/skipped authority and quiet AND/OR truth controls."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import source_occurrences as occurrences
import string_offset_request_base_float_boolnot_special_concat_leading_key_review_state as helpers
import string_offset_request_base_runtime_short_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_short_special_concat_leading_key_protocol as source

runner = source.runner
KEYS = ('1x', '-1x', '0x', '-4x')
CONTROLS = []


def links(tree, tag='operator'):
    yield tag, tree[0] == 'FLOAT', True
    if tree[0] == 'FLOAT':
        return
    if tree[0] == 'SHORT':
        yield from links(tree[2], tag + '_0')
        if tree[3] is None:
            yield tag + '_1', False, False
        else:
            yield from links(tree[3], tag + '_1')
    else:
        for index, child in enumerate(tree[1:3] if tree[0] == 'ADD' else tree[1:2]):
            yield from links(child, tag + '_' + str(index))


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    guards = ['pcode_peer_short = S_after.CODE[0]', 'pcode_peer_short.UNIT = 0',
              'ppool_peer_short = S_after.POOLS[0]', 'ppool_peer_short.UNIT = 0',
              'pcunit_peer_short = S_after.SOURCES[0]', 'pcunit_peer_short.ID = 0']
    for tag, leaf, evaluated in links(source.TREES[index]):
        origin, target = 'porigin_' + tag, 'pcpath_peer_short_' + tag
        guards.append(origin + ' = PORIGIN 0 ' + target)
        mutations = [
            ('drop', 'S_after[.CODE[0] = pcode_peer_short[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_short.EXPRESSIONS, ' + target + ', eps)]]'),
            ('flip', 'S_after[.CODE[0] = pcode_peer_short[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_short.EXPRESSIONS, ' + target + ', (' + str(not leaf).lower() + '))]]'),
            ('precision', 'S_after[.POOLS[0] = ppool_peer_short[.CONSTANTS = (PCCPRECISION ' + target + ' 17) :: ppool_peer_short.CONSTANTS]]'),
            ('source', 'S_after[.SOURCES[0] = pcunit_peer_short[.OCCURRENCES = (PCOCCURRENCE ' + target + ' (NExprVariable (BYTES "dW5hdXRo") eps)) :: pcunit_peer_short.OCCURRENCES]]'),
        ]
        if not leaf:
            mutations.append(('line', 'S_after[.CODE[0] = pcode_peer_short[.EXPRESSIONS = (CODEEXPR ' + target + ' 0 false) :: pcode_peer_short.EXPRESSIONS]]'))
        for label, replacement in mutations:
            state = 'S_peer_short_' + tag + '_' + label
            expected = 'eps' if evaluated or label == 'source' else '($ptascii(' + json.dumps(KEYS[index]) + '))'
            saved = 'eps' if evaluated or label == 'source' else '(' + source.prior.prior.integer((1, -1, 0, -4)[index]) + ')'
            guards += [state + ' = ' + replacement,
                       '$string_read_runtime_bytes(' + state + ', porigin_key) = ' + expected,
                       '$string_read_request_base_saved(' + state + ', pstringread) = ' + saved]
    for label, completion in (('budget', 'BUDGET'), ('unsupported', 'UNSUPPORTED "peer_short"'),
                              ('pending', 'SOURCE_PENDING'), ('exited', 'EXITED 0')):
        state = 'S_peer_short_' + label
        guards += [state + ' = S_after[.COMPLETION = ' + completion + '][.RESULT = KNOWN (PBOOL true)]',
                   '$string_read_runtime_value(' + state + ', porigin_operator) = eps',
                   '$string_read_runtime_bytes(' + state + ', porigin_key) = eps',
                   '$string_read_request_base_saved(' + state + ', pstringread) = eps']
    guards += ['S_peer_short_stale = S_after[.RESULT = KNOWN (PSTRING ($ptascii("stale")))]',
               '$string_read_runtime_bytes(S_peer_short_stale, porigin_key) = ($ptascii(' + json.dumps(KEYS[index]) + '))']
    if index == 1:
        guards += ['porigin_operator_0_1 = PORIGIN 0 pcpath_peer_short_float']
        for label, value in (('nan', 'PFLOAT 9221120237041090560'),
                             ('negative_nan', 'PFLOAT 18444492273895866368'),
                             ('payload_nan', 'PFLOAT 9221120237041090561'),
                             ('invalid', 'PFLOAT 18446744073709551616'),
                             ('integer', 'PINT 0'), ('boolean', 'PBOOL false'),
                             ('null', 'PNULL'), ('string', 'PSTRING ($ptascii("0"))')):
            state = 'S_peer_short_leaf_' + label
            guards += [state + ' = S_after[.POOLS[0] = ppool_peer_short[.CONSTANTS = (PCONSTANT pcpath_peer_short_float (' + value + ')) :: ppool_peer_short.CONSTANTS]]',
                       '$compiled_read(' + state + ', porigin_operator_0_1) = (' + value + ')',
                       '$string_read_runtime_bytes(' + state + ', porigin_key) = eps',
                       '$string_read_request_base_saved(' + state + ', pstringread) = eps']
        guards += ['S_peer_short_signed_zero = S_after[.POOLS[0] = ppool_peer_short[.CONSTANTS = (PCONSTANT pcpath_peer_short_float (PFLOAT 9223372036854775808)) :: ppool_peer_short.CONSTANTS]]',
                   '$string_read_runtime_value(S_peer_short_signed_zero, porigin_operator_0_1) = (PFLOAT 9223372036854775808)',
                   '$string_read_runtime_value(S_peer_short_signed_zero, porigin_operator_0) = (PBOOL false)',
                   '$string_read_runtime_bytes(S_peer_short_signed_zero, porigin_key) = ($ptascii("0x"))',
                   '$string_read_request_base_saved(S_peer_short_signed_zero, pstringread) = eps']
    if index == 0:
        for number, (name, fixture, control, target, node, result) in enumerate(CONTROLS):
            state, origin = 'S_peer_short_control_' + str(number), 'porigin_peer_short_control_' + str(number)
            expected = 'eps' if result is None else '(' + result + ')'
            folded = name in ('compiled_boolean', 'nan_left')
            guards += [state + '_budget = $php_run(' + fixture + ', 0, ' + json.dumps(base64.b64encode(bytes(control)).decode()) + ')',
                       state + '_budget.COMPLETION = BUDGET',
                       origin + ' = PORIGIN 0 ' + occurrences.path_term(target),
                       '$string_read_runtime_value(' + state + '_budget, ' + origin + ') = eps',
                       state + ' = ' + state + '_budget[.COMPLETION = NORMAL]',
                       '$origin_node(' + state + '.SOURCES, ' + origin + ') = (' + occurrences.node_term(node) + ')',
                       origin + ' = PORIGIN 0 pcpath_peer_short_control_' + str(number),
                       '$code_at(' + state + '.CODE, 0) = (pcode_peer_short_control_' + str(number) + ')',
                       '$code_expression(pcode_peer_short_control_' + str(number) + '.EXPRESSIONS, pcpath_peer_short_control_' + str(number) + ') = ((1, ' + str(folded).lower() + '))',
                       '$compiled_read(' + state + ', ' + origin + ') = ' + ('(PBOOL true)' if folded else 'eps'),
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
    raw = []
    for operator in ('&&', '||', 'and', 'or'):
        for left in (False, True):
            for right in (False, True):
                result = left or right if operator in ('||', 'or') else left and right
                raw.append(('truth_' + str(len(raw)), (one if left else zero) + ' ' + operator + ' ' + (one if right else zero), 'PBOOL ' + str(result).lower()))
    raw += [
        ('float_zero_integer', '0.0 || (+' + one + ')', 'PBOOL true'),
        ('integer_signed_zero', '(+' + zero + ') && (-0.0)', 'PBOOL false'),
        ('infinity_integer', 'INF && (+' + zero + ')', 'PBOOL false'),
        ('integer_float', two + ' && 0.0', 'PBOOL false'),
        ('integer_bool', two + ' || ' + zero, 'PBOOL true'),
        ('bool_integer', one + ' and ' + two, 'PBOOL true'),
        ('nested_not', '!(' + zero + ' or (' + one + ' && ' + zero + '))', 'PBOOL true'),
        ('nested_add', '(' + one + ' && ' + one + ')+(+' + zero + ')', 'PINT 1'),
    ]
    for name, right in (('nan', 'NAN'), ('variable', '$missing'), ('object', '(new stdClass())'), ('division', '(1/0)')):
        raw += [('skip_or_' + name, one + ' || ' + right, 'PBOOL true'),
                ('skip_and_' + name, zero + ' && ' + right, 'PBOOL false'),
                ('demand_or_' + name, zero + ' || ' + right, None),
                ('demand_and_' + name, one + ' && ' + right, None)]
    raw += [('nan_left', 'NAN || ' + one, None),
            ('runtime_float', '(0.0+(+' + zero + ')) && ' + one, None),
            ('compiled_integer', '1 && ' + one, None),
            ('compiled_boolean', 'true || ' + zero, None)]
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
    kinds = ('Expr_BinaryOp_BooleanAnd', 'Expr_BinaryOp_BooleanOr', 'Expr_BinaryOp_LogicalAnd',
             'Expr_BinaryOp_LogicalOr', 'Expr_BooleanNot', 'Expr_BinaryOp_Plus')
    for name, expression, result in raw:
        targets = [(path, node) for index, statement in enumerate(parsed[name]['ast']['program'])
                   for path, node in occurrences.expected(statement, [('INDEX', index)]) if node['node'] in kinds]
        target, node = min(targets, key=lambda item: len(item[0]))
        CONTROLS.append((name, checked[name]['fixture'], paths[name], target, node, result))
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
    report['scope'] = ('Exact author prefixes plus independent evaluated/skipped SOURCE/CODE/line/precision, completion, stale-result and typed/NaN leaf controls. Skipped right CODE and precision are irrelevant while its actual SOURCE remains required; demanded right authority is required. Forty-four checked-source compiled states retain actual BUDGET refusal before explicitly derived NORMAL fixture states check all four truth pairs for all four spellings, mixed PFLOAT/PBOOL/PINT directions, nesting, ignored NaN/variable/object/division RHSs and demanded refusals. Folded NaN-left and literal-Boolean controls retain actual PBOOL pools and refuse runtime certification. No live runtime state is normalized. Signed-zero substitution changes selected truth and refuses the old saved key at the existing compiler-pool boundary. Fixture source0/native0 and no source/native replay or 50/51/compiler/387/kernel/owner change.')
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
