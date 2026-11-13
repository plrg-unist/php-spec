#!/usr/bin/env python3
"""Independent arithmetic facts, quietness guards and borrowed-base continuations."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_arithmetic_special_concat_leading_key_cases as cases
import string_offset_request_base_float_special_concat_leading_key_review_state as floating

prior = floating.prior
runner = prior.runner
CONTROLS = {
    'outer-unary-arithmetic': b"<?php $x = (+(1+0.0) . false) . 'x';\n",
    'unary-integer-constant': b"<?php $x = (+E_ERROR . false) . 'x';\n",
    'warningful-arithmetic-left': b"<?php $x = (('1tail'+0) . null) . 'x';\n",
    'warningful-arithmetic-right': b"<?php $x = ((0+'1tail') . null) . 'x';\n",
    'zero-division': b"<?php $x = ((1/0) . null) . 'x';\n",
    'nonarithmetic-binary': b"<?php $x = ((1%2) . null) . 'x';\n",
    'assignment-arithmetic': b"<?php $x = ((($a=1)+0) . null) . 'x';\n",
    'array-arithmetic': b"<?php $x = (([1]+[2]) . null) . 'x';\n"}


def conditions(program, path, index):
    route = (0, 0, 1, 2)[index]
    checks, derived = prior.conditions(program, path, route)
    old_integer, integer = (3 if route == 2 else 1), (1, -1, 1, 4)[index]
    term = str(integer) if integer >= 0 else '$(' + str(integer) + ')'
    key = str(integer) + 'x'
    replacements = {
        '$ptascii("' + str(old_integer) + 'x")': '$ptascii("' + key + '")',
        '$ptascii("Uninitialized string offset ' + str(old_integer) + '")':
            '$ptascii("Uninitialized string offset ' + str(integer) + '")',
        'STRING_LEADING ' + str(old_integer): 'STRING_LEADING ' + term,
        'STRING_BOUNDS ' + str(old_integer): 'STRING_BOUNDS ' + term,
        '$string_read_request_base_saved(S, pstringread) = (' + str(old_integer) + ')':
            '$string_read_request_base_saved(S, pstringread) = (' + term + ')',
        '$compiled_read(S, porigin_inner) = (PSTRING ($ptascii("' + str(old_integer) + '")))':
            '$compiled_read(S, porigin_inner) = (PSTRING ($ptascii("' + str(integer) + '")))',
        '[' + ','.join(map(str, prior.cases.OUTPUTS[route])) + ']':
            '[' + ','.join(map(str, cases.OUTPUTS[index])) + ']'}
    if index == 1:
        replacements['$ptascii("b")'] = '$ptascii("c")'
    for old, new in replacements.items():
        checks = [check.replace(old, new) for check in checks]
    old_node = 'NScalarInt (INTEGER ' + str(old_integer) + ') metadata_integer'
    old = 'expression_11 = ' + old_node
    assert checks.count(old) == 1
    checks[checks.index(old)] = 'expression_11 = expression_arithmetic_root'
    old_checks = [
        '$origin_child((porigin_key), [PCFIELD 0, PCFIELD 0]) = (porigin_integer)',
        '$origin_node(S.SOURCES, porigin_integer) = (' + old_node + ')',
        '$compiled_read(S, porigin_integer) = (PINT ' + str(old_integer) + ')',
        '$parser_literal_at(' + old_node + ', 14) = (PINT ' + str(old_integer) + ')',
        '$compiled_special_concat_bytes(S, porigin_integer) = ($ptascii("' + str(old_integer) + '"))']
    at = checks.index(old_checks[0])
    assert checks[at:at + len(old_checks)] == old_checks

    # A leaf is (AST, value, number, text); a binary node adds two children.
    integer_leaf = lambda n: ('NScalarInt (INTEGER ' + str(n) + ')', 'PINT ' + str(n), 'NINT ' + str(n), str(n))
    const_leaf = lambda name, value, number, text: ('NExprConstFetch name_' + name, value, number, text)
    float_one = ('NScalarFloat (FLOAT text_float_one)', 'PFLOAT 4607182418800017453', 'NFLOAT 4607182418800017453', '1')
    float_zero = ('NScalarFloat (FLOAT text_float_zero)', 'PFLOAT 0', 'NFLOAT 0', '0')
    numeric_concat = ('CONCAT', 'PSTRING ($ptascii("3"))', 'NINT 3', '3',
        ('NScalarString (BYTES text_three)', 'PSTRING ($ptascii("3"))', 'NINT 3', '3'),
        ('NScalarString (BYTES text_empty)', 'PSTRING eps', None, ''))
    graphs = (
        ('ADD', float_one[1], float_one[2], '1', float_one, float_zero),
        ('SUBTRACT', 'PINT $(-1)', 'NINT $(-1)', '-1', integer_leaf(0), const_leaf('error', 'PINT 1', 'NINT 1', '1')),
        ('SUBTRACT', 'PINT 1', 'NINT 1', '1',
            ('DIVIDE', 'PINT 2', 'NINT 2', '2', integer_leaf(6), numeric_concat),
            ('ADD', 'PINT 1', 'NINT 1', '1', const_leaf('true', 'PBOOL true', 'NINT 1', '1'), const_leaf('false', 'PBOOL false', 'NINT 0', ''))),
        ('MULTIPLY', 'PINT 4', 'NINT 4', '4', integer_leaf(2), const_leaf('warning', 'PINT 2', 'NINT 2', '2')))
    asts = {'ADD': 'NExprBinaryOpPlus', 'SUBTRACT': 'NExprBinaryOpMinus',
            'MULTIPLY': 'NExprBinaryOpMul', 'DIVIDE': 'NExprBinaryOpDiv', 'CONCAT': 'NExprBinaryOpConcat'}
    binary_nodes = []

    def authority(node, suffix):
        shape, value, number, text = node[:4]
        origin, expression = 'porigin_arithmetic_' + suffix, 'expression_arithmetic_' + suffix
        extra = ['$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')',
                 '$compiled_read(S, ' + origin + ') = (' + value + ')',
                 '$compiled_precision(S, (' + origin + ')) = (14)']
        if len(node) == 4:
            extra += [expression + ' = ' + shape + ' metadata_arithmetic_' + suffix]
            if not shape.startswith('NExprConstFetch'):
                extra += ['$parser_literal_at(' + expression + ', 14) = (' + value + ')']
            else:
                extra += ['$parser_literal_at(' + expression + ', 14) = eps']
        else:
            left, right = suffix + '_left', suffix + '_right'
            extra += [expression + ' = ' + asts[shape] + ' expression_arithmetic_' + left + ' expression_arithmetic_' + right + ' metadata_arithmetic_' + suffix,
                '$origin_child((' + origin + '), [PCFIELD 0]) = (porigin_arithmetic_' + left + ')',
                '$origin_child((' + origin + '), [PCFIELD 1]) = (porigin_arithmetic_' + right + ')']
            extra += authority(node[4], left) + authority(node[5], right)
            if shape != 'CONCAT':
                extra += ['$pfshape(' + expression + ') = PFBINARY ' + shape + ' expression_arithmetic_' + left + ' expression_arithmetic_' + right,
                    '$coerce_number(' + node[4][1] + ') = COERCED (' + node[4][2] + ') false',
                    '$coerce_number(' + node[5][1] + ') = COERCED (' + node[5][2] + ') false',
                    '$number_binary(' + shape + ', ' + node[4][2] + ', ' + node[5][2] + ') = NUM (' + number + ')',
                    '$binary_apply(S, ' + shape + ', ' + node[4][1] + ', ' + node[5][1] + ', 0) = S[.RESULT = KNOWN (' + value + ')]',
                    '$parser_literal_text_at(' + value + ', 14) = ($ptascii(' + json.dumps(text) + '))']
                binary_nodes.append(suffix)
        return extra + ['$compiled_special_concat_bytes(S, ' + origin + ') = ($ptascii(' + json.dumps(text) + '))']

    extra = ['$origin_child((porigin_key), [PCFIELD 0, PCFIELD 0]) = (porigin_arithmetic_root)',
             'porigin_arithmetic_root = PORIGIN n_arithmetic_unit pcpath_arithmetic_root',
             r'S.PRECISIONINI = $ptascii("17") /\ $precision_value(S) = 17'] + authority(graphs[index], 'root')
    if index == 0:
        extra += ['$parser_literal_text_at(PFLOAT 4607182418800017453, 17) =/= ($ptascii("1"))']
    checks[at:at + len(old_checks)] = extra

    guards = []
    for suffix in binary_nodes:
        origin = 'porigin_arithmetic_' + suffix
        for child in ('', '_left', '_right'):
            state = 'S_drop_arithmetic_' + suffix + child
            target = origin + child
            guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + target + ', eps)]',
                '$compiled_read(' + state + ', ' + target + ') = eps',
                '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps',
                '$compiled_special_concat_bytes(' + state + ', porigin_key) = eps',
                '$string_read_request_base_saved(' + state + ', pstringread) = eps']
        state = 'S_wrong_arithmetic_' + suffix
        guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + origin + ', (PINT 99))]',
            '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps',
            '$string_read_request_base_saved(' + state + ', pstringread) = eps']
    guards += runner.lines(r'''
S_live_precision = S_after[.PRECISIONINI = $ptascii("9")][.PRECISIONMODIFIED = true]
$precision_value(S_live_precision) = 9
$compiled_precision(S_live_precision, (porigin_arithmetic_root)) = (14)
S_no_children = S_after[.SOURCES = [{ID n_arithmetic_unit, AST (PROGRAM eps), OCCURRENCES ([(PCOCCURRENCE pcpath_arithmetic_root expression_arithmetic_root)])}]]
$compiled_read(S_no_children, porigin_arithmetic_root) = pvalue_root?
$compiled_read(S_after, porigin_arithmetic_root) = pvalue_root?
$origin_node(S_no_children.SOURCES, porigin_arithmetic_root) = (expression_arithmetic_root)
$compiled_special_concat_bytes(S_no_children, porigin_arithmetic_root) = eps
''') + ['$compiled_special_concat_bytes(S_live_precision, porigin_key) = ($ptascii("' + key + '"))',
        '$string_read_request_base_saved(S_live_precision, pstringread) = (' + term + ')']
    if index == 0:
        guards += runner.lines(r'''
S_wrong_precision = S_after[.POOLS = $float_review_precision(S_after.POOLS, porigin_arithmetic_root, 17)]
$compiled_precision(S_wrong_precision, (porigin_arithmetic_root)) = (17)
$compiled_special_concat_bytes(S_wrong_precision, porigin_key) = eps
$string_read_request_base_saved(S_wrong_precision, pstringread) = eps
''')
    if index == 1:
        guards += runner.lines(r'''
S_hostile = S_after[.COMPLETION = UNSUPPORTED "missing source line"][.RESULT = KNOWN (PINT $(-1))]
$binary_apply(S_hostile, ADD, PSTRING ($ptascii("-1tail")), PINT 0, 0) = S_hostile
$binary_apply(S_hostile, ADD, PINT 0, PSTRING ($ptascii("-1tail")), 0) = S_hostile
$binary_apply(S_hostile, DIVIDE, PINT 1, PINT 0, 0) = S_hostile
$coerce_number(PSTRING ($ptascii("-1tail"))) = COERCED (NINT $(-1)) true
$number_binary(DIVIDE, NINT 1, NINT 0) = DIVZERO
''')
        for side in ('left', 'right', 'divzero'):
            state = 'S_hostile_' + side
            left_value = 'PINT 0' if side == 'right' else 'PINT 1' if side == 'divzero' else 'PSTRING ($ptascii("-1tail"))'
            right_value = 'PSTRING ($ptascii("-1tail"))' if side == 'right' else 'PINT 0'
            left_ast = 'NScalarInt (INTEGER ' + ('1' if side == 'divzero' else '0') + ') metadata_arithmetic_root_left' if side != 'left' else 'NScalarString (BYTES "LTF0YWls") metadata_arithmetic_root_left'
            right_ast = 'NScalarString (BYTES "LTF0YWls") metadata_arithmetic_root_right' if side == 'right' else 'NScalarInt (INTEGER 0) metadata_arithmetic_root_right'
            ast = 'NExprBinaryOpDiv' if side == 'divzero' else 'NExprBinaryOpPlus'
            guards += ['expression_hostile_left_' + side + ' = ' + left_ast,
                'expression_hostile_right_' + side + ' = ' + right_ast,
                '$origin_child((porigin_arithmetic_root), [PCFIELD 0]) = (PORIGIN n_arithmetic_unit pcpath_hostile_left_' + side + ')',
                '$origin_child((porigin_arithmetic_root), [PCFIELD 1]) = (PORIGIN n_arithmetic_unit pcpath_hostile_right_' + side + ')',
                'expression_hostile_' + side + ' = ' + ast + ' expression_hostile_left_' + side + ' expression_hostile_right_' + side + ' metadata_arithmetic_root',
                state + ' = S_hostile[.POOLS = $special_review_pools($special_review_pools(S_hostile.POOLS, porigin_arithmetic_root_left, (' + left_value + ')), porigin_arithmetic_root_right, (' + right_value + '))][.SOURCES = [{ID n_arithmetic_unit, AST (PROGRAM eps), OCCURRENCES ([(PCOCCURRENCE pcpath_arithmetic_root expression_hostile_' + side + '), (PCOCCURRENCE pcpath_hostile_left_' + side + ' expression_hostile_left_' + side + '), (PCOCCURRENCE pcpath_hostile_right_' + side + ' expression_hostile_right_' + side + ')])}]]',
                '$compiled_read(' + state + ', porigin_arithmetic_root) = (PINT $(-1))',
                '$compiled_read(' + state + ', porigin_arithmetic_root_left) = (' + left_value + ')',
                '$compiled_read(' + state + ', porigin_arithmetic_root_right) = (' + right_value + ')',
                '$binary_apply(' + state + ', ' + ('DIVIDE' if side == 'divzero' else 'ADD') + ', ' + left_value + ', ' + right_value + ', 0) = ' + state,
                '$compiled_special_concat_bytes(' + state + ', porigin_arithmetic_root) = eps']
    checks += guards
    return checks, derived + len(guards)


def compiler_conditions(checked, paths):
    checks = []
    for index, (name, value) in enumerate(checked.items()):
        state, origin = 'S_compiler_' + str(index), 'porigin_compiler_' + str(index)
        path, child = 'pcpath_compiler_' + str(index), 'porigin_compiler_child_' + str(index)
        expression = 'expression_compiler_' + str(index)
        checks += [state + ' = $php_run(' + value['fixture'] + ', 0, ' + json.dumps(base64.b64encode(bytes(paths[name])).decode()) + ')',
            state + '.COMPLETION = BUDGET',
            '$special_review_concat_path(' + state + '.SOURCES[0].OCCURRENCES) = (' + path + ')',
            origin + ' = PORIGIN 0 ' + path,
            '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps',
            '$origin_child((' + origin + '), [PCFIELD 0, PCFIELD 0]) = (' + child + ')',
            '$origin_node(' + state + '.SOURCES, ' + child + ') = (' + expression + ')',
            '$compiled_special_concat_bytes(' + state + ', ' + child + ') = eps']
        if index < 2:
            checks += ['$compiled_read(' + state + ', ' + origin + ') = (PSTRING ($ptascii("1x")))',
                '$compiled_string_value(' + state + ', ' + origin + ', PSTRING ($ptascii("1x"))) = PSTRING ($ptascii("1x"))',
                expression + ' = NExprUnaryPlus expression_compiler_inner_' + str(index) + ' metadata_compiler_unary_' + str(index),
                '$origin_child((' + child + '), [PCFIELD 0]) = (porigin_compiler_inner_' + str(index) + ')',
                '$origin_node(' + state + '.SOURCES, porigin_compiler_inner_' + str(index) + ') = (expression_compiler_inner_' + str(index) + ')',
                '$compiled_read(' + state + ', porigin_compiler_inner_' + str(index) + ') = (' + ('PFLOAT 4607182418800017408' if index == 0 else 'PINT 1') + ')',
                '$compiled_special_concat_bytes(' + state + ', porigin_compiler_inner_' + str(index) + ') = ($ptascii("1"))']
            if index == 0:
                checks += runner.lines(r'''
expression_compiler_inner_0 = NExprBinaryOpPlus expression_compiler_left expression_compiler_right metadata_compiler_binary
$origin_child((porigin_compiler_inner_0), [PCFIELD 0]) = (porigin_compiler_left)
$origin_child((porigin_compiler_inner_0), [PCFIELD 1]) = (porigin_compiler_right)
$origin_node(S_compiler_0.SOURCES, porigin_compiler_left) = (expression_compiler_left)
$origin_node(S_compiler_0.SOURCES, porigin_compiler_right) = (expression_compiler_right)
expression_compiler_left = NScalarInt (INTEGER 1) metadata_compiler_left
expression_compiler_right = NScalarFloat (FLOAT text_compiler_zero) metadata_compiler_right
$compiled_read(S_compiler_0, porigin_compiler_left) = (PINT 1)
$compiled_read(S_compiler_0, porigin_compiler_right) = (PFLOAT 0)
$compiled_precision(S_compiler_0, (porigin_compiler_inner_0)) = (14)
$coerce_number(PINT 1) = COERCED (NINT 1) false
$coerce_number(PFLOAT 0) = COERCED (NFLOAT 0) false
$number_binary(ADD, NINT 1, NFLOAT 0) = NUM (NFLOAT 4607182418800017408)
$binary_apply(S_compiler_0, ADD, PINT 1, PFLOAT 0, 0) = S_compiler_0[.RESULT = KNOWN (PFLOAT 4607182418800017408)]
''')
            else:
                checks += ['expression_compiler_inner_1 = NExprConstFetch name_compiler_constant metadata_compiler_constant']
        elif name == 'nonarithmetic-binary':
            checks += ['$compiled_read(' + state + ', ' + origin + ') = (PSTRING ($ptascii("1x")))',
                '$compiled_read(' + state + ', ' + child + ') = (PINT 1)']
        else:
            checks += ['$compiled_read(' + state + ', ' + origin + ') = eps']
    return checks


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    watched = [Path(__file__), Path(prior.__file__), Path(floating.__file__),
        Path(__file__).with_name('string_offset_request_base_nested_unary_numeric_special_concat_leading_key_review_state.py')]
    before = {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.cases = cases
    runner.conditions = conditions
    runner.compiler_conditions = compiler_conditions
    runner.CONTROLS = CONTROLS
    passed = runner.main(expected_outputs=cases.OUTPUTS)
    assert before == {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = 'Four actual arithmetic CONCAT source-state fixtures authenticate every ADD/SUB/MUL/DIV node, actual children, own facts, quiet coercions, NUM results, pure application and compile14/live17 formatting, including numeric CONCAT operands. Missing facts/children, wrong roots and left/right warning or DIV0 state-equality traps remain refused. Borrowed owners, supplied throw, genuine later bounds and budgets retain their existing laws. Current compiler controls admit the bare inner 1+0.0 while retaining outer unary/root and unary ConstFetch refusals; no historical95/41 or older source/native/state campaign is replayed.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
