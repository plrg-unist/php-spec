#!/usr/bin/env python3
"""Independent FLOAT VALUE, source authority, type and abrupt-state controls."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import source_occurrences as occurrences
import string_offset_request_base_float_boolnot_special_concat_leading_key_review_state as helpers
import string_offset_request_base_runtime_float_arithmetic_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_float_arithmetic_special_concat_leading_key_protocol as source

runner = source.runner
KEYS = ('1x', '-1x', '0x', '-4x')
CONTROLS = []


def links(tree, tag='operator'):
    yield tag, tree
    if tree[0] == 'FLOAT':
        return
    children = (tree[2:4] if tree[0] == 'FLOAT_BINARY' else
                tree[1:3] if tree[0] in ('ADD', 'SUBTRACT', 'MULTIPLY', 'DIVIDE', 'IDENTICAL') else tree[1:2])
    for index, child in enumerate(children):
        yield from links(child, tag + '_' + str(index))


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    guards = ['pcode_peer_float = S_after.CODE[0]', 'pcode_peer_float.UNIT = 0',
              'ppool_peer_float = S_after.POOLS[0]', 'ppool_peer_float.UNIT = 0',
              'pcunit_peer_float = S_after.SOURCES[0]', 'pcunit_peer_float.ID = 0']
    for tag, tree in links(source.TREES[index]):
        origin, target = 'porigin_' + tag, 'pcpath_peer_float_' + tag
        guards.append(origin + ' = PORIGIN 0 ' + target)
        leaf = tree[0] == 'FLOAT'
        mutations = [
            ('drop', 'S_after[.CODE[0] = pcode_peer_float[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_float.EXPRESSIONS, ' + target + ', eps)]]'),
            ('flip', 'S_after[.CODE[0] = pcode_peer_float[.EXPRESSIONS = $float_not_review_expressions(pcode_peer_float.EXPRESSIONS, ' + target + ', (' + str(not leaf).lower() + '))]]'),
            ('precision', 'S_after[.POOLS[0] = ppool_peer_float[.CONSTANTS = (PCCPRECISION ' + target + ' 17) :: ppool_peer_float.CONSTANTS]]'),
            ('source', 'S_after[.SOURCES[0] = pcunit_peer_float[.OCCURRENCES = (PCOCCURRENCE ' + target + ' (NExprVariable (BYTES "dW5hdXRo") eps)) :: pcunit_peer_float.OCCURRENCES]]'),
        ]
        if not leaf:
            mutations.append(('line', 'S_after[.CODE[0] = pcode_peer_float[.EXPRESSIONS = (CODEEXPR ' + target + ' 0 false) :: pcode_peer_float.EXPRESSIONS]]'))
        for label, replacement in mutations:
            state = 'S_peer_float_' + tag + '_' + label
            guards += [state + ' = ' + replacement,
                       '$string_read_runtime_value(' + state + ', porigin_operator) = eps',
                       '$string_read_runtime_bytes(' + state + ', porigin_key) = eps',
                       '$string_read_request_base_saved(' + state + ', pstringread) = eps']
        if tree[0] == 'FLOAT_BINARY':
            result = 'PFLOAT ' + str(tree[-1])
            state = 'S_peer_float_' + tag + '_pool'
            guards += [state + ' = S_after[.POOLS[0] = ppool_peer_float[.CONSTANTS = (PCONSTANT ' + target + ' (PFLOAT 4611686018427387904)) :: ppool_peer_float.CONSTANTS]]',
                       '$compiled_read(' + state + ', ' + origin + ') = eps',
                       '$string_read_runtime_value(' + state + ', ' + origin + ') = (' + result + ')',
                       '$string_read_runtime_bytes(' + state + ', ' + origin + ') = eps',
                       '$string_read_request_base_saved(' + state + ', pstringread) = (' + source.integers.integer((1, -1, 0, -4)[index]) + ')']
            for label, completion in (('budget', 'BUDGET'), ('pending', 'SOURCE_PENDING'),
                                      ('unsupported', 'UNSUPPORTED "peer_float"'), ('exited', 'EXITED 0'),
                                      ('thrown', 'THROWN "Error" ($ptascii("peer_float")) 5')):
                state = 'S_peer_float_' + tag + '_' + label
                guards += [state + ' = S_after[.COMPLETION = ' + completion + '][.RESULT = KNOWN (' + result + ')]',
                           '$string_read_runtime_value(' + state + ', ' + origin + ') = eps',
                           '$string_read_runtime_bytes(' + state + ', porigin_key) = eps',
                           '$string_read_request_base_saved(' + state + ', pstringread) = eps']
            guards += ['$string_read_runtime_value(S_after[.RESULT = KNOWN (PFLOAT 4611686018427387904)], ' + origin + ') = (' + result + ')']
    if index == 2:
        guards += ['porigin_operator_0_0_1 = PORIGIN 0 pcpath_peer_float_leaf']
        for label, value in (('nan', 'PFLOAT 9221120237041090560'), ('negative_nan', 'PFLOAT 18444492273895866368'),
                             ('payload_nan', 'PFLOAT 9221120237041090561'), ('invalid', 'PFLOAT 18446744073709551616'),
                             ('integer', 'PINT 1'), ('boolean', 'PBOOL true'), ('null', 'PNULL'),
                             ('string', 'PSTRING ($ptascii("1.5"))')):
            state = 'S_peer_float_leaf_' + label
            guards += [state + ' = S_after[.POOLS[0] = ppool_peer_float[.CONSTANTS = (PCONSTANT pcpath_peer_float_leaf (' + value + ')) :: ppool_peer_float.CONSTANTS]]',
                       '$compiled_read(' + state + ', porigin_operator_0_0_1) = (' + value + ')',
                       '$string_read_runtime_value(' + state + ', porigin_operator_0_0) = eps',
                       '$string_read_request_base_saved(' + state + ', pstringread) = eps']
    if index == 0:
        for number, (name, fixture, original, target, node, expected) in enumerate(CONTROLS):
            state, origin = 'S_peer_float_control_' + str(number), 'porigin_peer_float_control_' + str(number)
            normal = state + '_normal'
            value = 'eps' if expected is None else '(' + expected + ')'
            guards += [state + ' = $php_run(' + fixture + ', 0, ' + json.dumps(base64.b64encode(bytes(original)).decode()) + ')',
                       state + '.COMPLETION = BUDGET', origin + ' = PORIGIN 0 ' + occurrences.path_term(target),
                       '$origin_node(' + state + '.SOURCES, ' + origin + ') = (' + occurrences.node_term(node) + ')',
                       origin + ' = PORIGIN 0 pcpath_peer_float_control_' + str(number),
                       '$code_at(' + state + '.CODE, 0) = (pcode_peer_float_control_' + str(number) + ')',
                       '$code_expression(pcode_peer_float_control_' + str(number) + '.EXPRESSIONS, pcpath_peer_float_control_' + str(number) + ') = ((1, false))',
                       '$compiled_read(' + state + ', ' + origin + ') = eps',
                       '$compiled_precision(' + state + ', (' + origin + ')) = (14)',
                       '$string_read_runtime_value(' + state + ', ' + origin + ') = ' + ('(PINT 1)' if name == 'exact_integer' else 'eps'),
                       normal + ' = ' + state + '[.COMPLETION = NORMAL]',
                       '$string_read_runtime_value(' + normal + ', ' + origin + ') = ' + value,
                       '$string_read_runtime_bytes(' + normal + ', ' + origin + ') = ' +
                       ('($echo_value(' + expected + '))' if expected is not None and not expected.startswith('PFLOAT ') else 'eps'),
                       '$string_read_runtime_value(' + normal + '[.RESULT = KNOWN (PFLOAT 4611686018427387904)], ' + origin + ') = ' + value]
            if name in ('positive_zero_divisor', 'negative_zero_divisor'):
                divisor = '0' if name == 'positive_zero_divisor' else '9223372036854775808'
                guards += ['$number_binary(DIVIDE, NINT 1, NFLOAT ' + divisor + ') = DIVZERO',
                           '$binary_apply(' + normal + ', DIVIDE, PBOOL true, PFLOAT ' + divisor + ', 1) = ' + normal + '[.COMPLETION = THROWN "DivisionByZeroError" ($ptascii("Division by zero")) 1]',
                           '$binary_apply(' + state + ', DIVIDE, PBOOL true, PFLOAT ' + divisor + ', 1) = ' + state]
            if name == 'warning_string':
                guards += ['$coerce_number(PSTRING ($ptascii("1x"))) = COERCED (NINT 1) true',
                           '$number_binary(ADD, NINT 1, NFLOAT 0) = NUM (NFLOAT 4607182418800017408)',
                           'S_peer_float_warning = $binary_apply(' + normal + ', ADD, PSTRING ($ptascii("1x")), PFLOAT 0, 1)',
                           'S_peer_float_warning =/= ' + normal + '[.RESULT = KNOWN (PFLOAT 4607182418800017408)]']
    return checks + guards, derived + len(guards)


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    prep = output.with_name(output.name + '-control-prep')
    prep.mkdir(parents=True)
    one, zero = '(+(!0.0))', '(+(!INF))'
    two = '(' + one + '+' + one + ')'
    runtime_float = '(0.0+' + zero + ')'
    runtime_inf = '(INF+' + zero + ')'
    count63 = '((' + two + '*' + two + '*' + two + '*' + two + '*' + two + '*' + two + ')-' + one + ')'
    minimum = '(' + one + ' << ' + count63 + ')'
    raw = [
        ('fraction', one + '/' + two, 'PFLOAT 4602678819172646912'),
        ('float_left', '1.0/' + one, 'PFLOAT 4607182418800017408'),
        ('negative_zero', '(-0.0)*' + one, 'PFLOAT 9223372036854775808'),
        ('infinity', runtime_inf, 'PFLOAT 9218868437227405312'),
        ('overflow_add', minimum + '+(' + minimum + ')', 'PFLOAT 14118784831806504960'),
        ('overflow_div', minimum + '/(-' + one + ')', 'PFLOAT 4890909195324358656'),
        ('exact_integer', one + '/' + one, 'PINT 1'),
        ('numeric_equal', '(' + runtime_float + '==' + zero + ')', 'PBOOL true'),
        ('numeric_order', '(' + runtime_float + '<=1.0)', 'PBOOL true'),
        ('spaceship', '(' + runtime_float + '<=>1.0)', 'PINT $(-1)'),
        ('xor_truth', '(' + runtime_float + ' xor (!0.0))', 'PBOOL true'),
        ('short_truth', '(' + runtime_float + ' || (!0.0))', 'PBOOL true'),
        ('positive_zero_divisor', one + '/' + runtime_float, None),
        ('negative_zero_divisor', one + '/((-0.0)*' + one + ')', None),
        ('nan_add', '(-INF)+' + runtime_inf, None),
        ('nan_subtract', 'INF-' + runtime_inf, None),
        ('nan_multiply', 'INF*' + zero, None),
        ('nan_divide', 'INF/' + runtime_inf, None),
        ('nan_child', 'NAN+' + one, None),
        ('warning_string', "'1x'+" + runtime_float, None),
        ('quiet_string', "'1'+" + runtime_float, None),
        ('null_child', 'null+' + runtime_float, None),
        ('compiled_integer', '1+' + runtime_float, None),
        ('variable_child', '$missing+' + runtime_float, None),
        ('runtime_float_sign', '-(' + runtime_float + ')', 'PFLOAT 9223372036854775808'),
        ('runtime_power', '1.0**' + one, None),
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
    kinds = ('Expr_BinaryOp_Plus', 'Expr_BinaryOp_Minus', 'Expr_BinaryOp_Mul', 'Expr_BinaryOp_Div',
             'Expr_BinaryOp_Equal', 'Expr_BinaryOp_SmallerOrEqual', 'Expr_BinaryOp_Spaceship',
             'Expr_BinaryOp_LogicalXor', 'Expr_BinaryOp_BooleanOr', 'Expr_UnaryMinus', 'Expr_BinaryOp_Pow')
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
    report['scope'] = ('Exact author prefixes plus independent recursive SOURCE/CODE/line/precision, stale RESULT and actual nonnormal-completion refusals. Runtime FLOAT pool injection without CODE folding is ignored; forged NaN/invalid/type leaves refuse the arithmetic value and saved key. Twenty-six genuine checked-source controls retain original BUDGET states before explicitly derived NORMAL fixtures cover fractional and overflow FLOAT, signed zero, infinity, equality/order/spaceship/XOR/OR consumers, exact PINT division, both zero divisors, all four NaN-producing arithmetic forms, NaN children, warningful/quiet strings, NULL/compiled-PINT/variable leaves, quiet runtime FLOAT sign and wider POWER refusal. Full-state numeric results remain distinct from quiet coercions and NORMAL-gated throws. Each runtime FLOAT VALUE has BYTE eps. Fixture source0/native0; no source/native replay, live-state normalization, primitive/compiler/schema/API/kernel/owner change or held-boundary expansion.')
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
