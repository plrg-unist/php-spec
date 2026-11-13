#!/usr/bin/env python3
"""Independent recursive unary authority, nonliteral kinds and retained owners."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_unary_const_arithmetic_special_concat_leading_key_cases as cases
import string_offset_request_base_arithmetic_special_concat_leading_key_review_state as arithmetic
import string_offset_request_base_integer_const_special_concat_leading_key_review_state as constants
import string_offset_request_base_nested_unary_numeric_special_concat_leading_key_review_state as nested

prior = arithmetic.prior
runner = arithmetic.runner
CONST_CONTROL = 'unary-integer-constant-null'
CONTROLS = dict(arithmetic.CONTROLS) | {
    CONST_CONTROL: constants.CONTROLS['unary-integer-constant'],
    'unary-boolean-constant': b"<?php $x = (+true . false) . 'x';\n",
    'unary-numeric-concat': b"<?php $x = (+('1'.'') . false) . 'x';\n"}


def conditions(program, path, index):
    route = (0, 0, 1, 2)[index]
    checks, derived = prior.conditions(program, path, route)
    old_integer, integer = (3 if route == 2 else 1), (1, -1, 1, -4)[index]
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
    checks[checks.index(old)] = 'expression_11 = expression_unary_root'
    old_checks = [
        '$origin_child((porigin_key), [PCFIELD 0, PCFIELD 0]) = (porigin_integer)',
        '$origin_node(S.SOURCES, porigin_integer) = (' + old_node + ')',
        '$compiled_read(S, porigin_integer) = (PINT ' + str(old_integer) + ')',
        '$parser_literal_at(' + old_node + ', 14) = (PINT ' + str(old_integer) + ')',
        '$compiled_special_concat_bytes(S, porigin_integer) = ($ptascii("' + str(old_integer) + '"))']
    at = checks.index(old_checks[0])
    assert checks[at:at + len(old_checks)] == old_checks

    leaf = lambda n: ('NScalarInt (INTEGER ' + str(n) + ')', 'PINT ' + str(n), 'NINT ' + str(n), str(n))
    const = lambda name, value, number, text: ('NExprConstFetch name_' + name, value, number, text)
    numeric_concat = ('CONCAT', 'PSTRING ($ptascii("3"))', 'NINT 3', '3',
        ('NScalarString (BYTES text_three)', 'PSTRING ($ptascii("3"))', 'NINT 3', '3'),
        ('NScalarString (BYTES text_empty)', 'PSTRING eps', None, ''))
    graphs = (
        ('POSITIVE', 'PINT 1', 'NINT 1', '1', const('error', 'PINT 1', 'NINT 1', '1')),
        ('NEGATIVE', 'PFLOAT 13830554455654793261', 'NFLOAT 13830554455654793261', '-1',
            ('ADD', 'PFLOAT 4607182418800017453', 'NFLOAT 4607182418800017453', '1',
                ('NScalarFloat (FLOAT text_float_one)', 'PFLOAT 4607182418800017453', 'NFLOAT 4607182418800017453', '1'),
                ('NScalarFloat (FLOAT text_float_zero)', 'PFLOAT 0', 'NFLOAT 0', '0'))),
        ('POSITIVE', 'PINT 1', 'NINT 1', '1',
            ('SUBTRACT', 'PINT 1', 'NINT 1', '1',
                ('DIVIDE', 'PINT 2', 'NINT 2', '2', leaf(6), numeric_concat),
                ('ADD', 'PINT 1', 'NINT 1', '1', const('true', 'PBOOL true', 'NINT 1', '1'), const('false', 'PBOOL false', 'NINT 0', '')))),
        ('NEGATIVE', 'PINT $(-4)', 'NINT $(-4)', '-4',
            ('MULTIPLY', 'PINT 4', 'NINT 4', '4', leaf(2), const('warning', 'PINT 2', 'NINT 2', '2'))))
    asts = {'ADD': 'NExprBinaryOpPlus', 'SUBTRACT': 'NExprBinaryOpMinus',
        'MULTIPLY': 'NExprBinaryOpMul', 'DIVIDE': 'NExprBinaryOpDiv', 'CONCAT': 'NExprBinaryOpConcat',
        'POSITIVE': 'NExprUnaryPlus', 'NEGATIVE': 'NExprUnaryMinus'}
    operations = []

    def authority(node, suffix, own_fact=True):
        shape, value, number, text = node[:4]
        origin, expression = 'porigin_unary_' + suffix, 'expression_unary_' + suffix
        extra = ['$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')']
        if own_fact:
            extra += ['$compiled_read(S, ' + origin + ') = (' + value + ')',
                '$compiled_precision(S, (' + origin + ')) = (14)']
        if len(node) == 4:
            extra += [expression + ' = ' + shape + ' metadata_unary_' + suffix,
                '$parser_literal_at(' + expression + ', 14) = ' + ('eps' if shape.startswith('NExprConstFetch') else '(' + value + ')')]
        else:
            children = [suffix + '_child'] if len(node) == 5 else [suffix + '_left', suffix + '_right']
            extra += [expression + ' = ' + asts[shape] + ' ' + ' '.join('expression_unary_' + child for child in children) + ' metadata_unary_' + suffix]
            for field, (child, child_node) in enumerate(zip(children, node[4:])):
                extra += ['$origin_child((' + origin + '), [PCFIELD ' + str(field) + ']) = (porigin_unary_' + child + ')']
                extra += authority(child_node, child, shape != 'CONCAT')
            if shape != 'CONCAT':
                operations.append(suffix)
                if len(node) == 5:
                    extra += ['$pfshape(' + expression + ') = PFUNARY ' + shape + ' expression_unary_' + children[0],
                        '$parser_literal_at(expression_unary_' + children[0] + ', 14) = eps',
                        '$unary_apply(S, ' + shape + ', ' + node[4][1] + ', 0) = S[.RESULT = KNOWN (' + value + ')]']
                else:
                    extra += ['$pfshape(' + expression + ') = PFBINARY ' + shape + ' expression_unary_' + children[0] + ' expression_unary_' + children[1],
                        '$coerce_number(' + node[4][1] + ') = COERCED (' + node[4][2] + ') false',
                        '$coerce_number(' + node[5][1] + ') = COERCED (' + node[5][2] + ') false',
                        '$number_binary(' + shape + ', ' + node[4][2] + ', ' + node[5][2] + ') = NUM (' + number + ')',
                        '$binary_apply(S, ' + shape + ', ' + node[4][1] + ', ' + node[5][1] + ', 0) = S[.RESULT = KNOWN (' + value + ')]']
                extra += ['$parser_literal_text_at(' + value + ', 14) = ($ptascii(' + json.dumps(text) + '))']
        return extra + ['$compiled_special_concat_bytes(S, ' + origin + ') = ($ptascii(' + json.dumps(text) + '))']

    extra = ['$origin_child((porigin_key), [PCFIELD 0, PCFIELD 0]) = (porigin_unary_root)',
        'porigin_unary_root = PORIGIN n_unary_unit pcpath_unary_root',
        r'S.PRECISIONINI = $ptascii("17") /\ $precision_value(S) = 17'] + authority(graphs[index], 'root')
    checks[at:at + len(old_checks)] = extra
    guards = []
    for suffix in operations:
        origin = 'porigin_unary_' + suffix
        guards += ['S_drop_unary_' + suffix + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + origin + ', eps)]',
            '$compiled_read(S_drop_unary_' + suffix + ', ' + origin + ') = eps',
            '$compiled_special_concat_bytes(S_drop_unary_' + suffix + ', porigin_key) = eps',
            '$string_read_request_base_saved(S_drop_unary_' + suffix + ', pstringread) = eps',
            'S_wrong_unary_' + suffix + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + origin + ', (PINT 99))]',
            '$compiled_special_concat_bytes(S_wrong_unary_' + suffix + ', porigin_key) = eps',
            '$string_read_request_base_saved(S_wrong_unary_' + suffix + ', pstringread) = eps']
    guards += runner.lines(r'''
S_drop_unary_child = S_after[.POOLS = $special_review_pools(S_after.POOLS, porigin_unary_root_child, eps)]
$compiled_read(S_drop_unary_child, porigin_unary_root_child) = eps
$compiled_special_concat_bytes(S_drop_unary_child, porigin_unary_root) = eps
$string_read_request_base_saved(S_drop_unary_child, pstringread) = eps
S_child_precision = S_after[.POOLS = $float_review_precision(S_after.POOLS, porigin_unary_root_child, 17)]
$compiled_precision(S_child_precision, (porigin_unary_root)) = (14)
$compiled_precision(S_child_precision, (porigin_unary_root_child)) = (17)
$compiled_special_concat_bytes(S_child_precision, porigin_key) = eps
$string_read_request_base_saved(S_child_precision, pstringread) = eps
S_root_precision = S_after[.POOLS = $float_review_precision(S_after.POOLS, porigin_unary_root, 17)]
$compiled_precision(S_root_precision, (porigin_unary_root)) = (17)
$compiled_precision(S_root_precision, (porigin_unary_root_child)) = (14)
$compiled_special_concat_bytes(S_root_precision, porigin_key) = eps
$string_read_request_base_saved(S_root_precision, pstringread) = eps
S_no_child = S_after[.SOURCES = [{ID n_unary_unit, AST (PROGRAM eps), OCCURRENCES ([(PCOCCURRENCE pcpath_unary_root expression_unary_root)])}]]
$compiled_read(S_no_child, porigin_unary_root_child) = pvalue_child?
$compiled_read(S_after, porigin_unary_root_child) = pvalue_child?
$origin_node(S_no_child.SOURCES, porigin_unary_root) = (expression_unary_root)
$compiled_special_concat_bytes(S_no_child, porigin_unary_root) = eps
expression_wrong_kind = NExprVariable (BYTES "dW5hdXRo") metadata_unary_root
S_wrong_kind = S_after[.SOURCES = [{ID n_unary_unit, AST (PROGRAM eps), OCCURRENCES ([(PCOCCURRENCE pcpath_unary_root expression_wrong_kind)])}]]
$compiled_read(S_wrong_kind, porigin_unary_root) = pvalue_root?
$compiled_read(S_after, porigin_unary_root) = pvalue_root?
$compiled_special_concat_bytes(S_wrong_kind, porigin_unary_root) = eps
S_live_precision = S_after[.PRECISIONINI = $ptascii("9")][.PRECISIONMODIFIED = true]
$precision_value(S_live_precision) = 9
''') + ['$compiled_special_concat_bytes(S_live_precision, porigin_key) = ($ptascii("' + key + '"))',
        '$string_read_request_base_saved(S_live_precision, pstringread) = (' + term + ')']
    if index == 0:
        guards += runner.lines(r'''
S_boolean = S_after[.POOLS = $special_review_pools(S_after.POOLS, porigin_unary_root_child, (PBOOL true))]
$compiled_special_concat_bytes(S_boolean, porigin_unary_root_child) = ($ptascii("1"))
$compiled_read(S_boolean, porigin_unary_root) = (PINT 1)
$unary_apply(S_boolean, POSITIVE, PBOOL true, 0) = S_boolean[.RESULT = KNOWN (PINT 1)]
$compiled_special_concat_bytes(S_boolean, porigin_unary_root) = ($ptascii("1"))
$string_read_request_base_saved(S_boolean, pstringread) = (1)
''')
    if index == 1:
        guards += runner.lines(r'''
$parser_literal_text_at(PFLOAT 13830554455654793261, 17) =/= ($ptascii("-1"))
''')
    checks += guards
    return checks, derived + len(guards)


def compiler_conditions(checked, paths):
    checks = arithmetic.compiler_conditions({name: value for name, value in checked.items() if name in arithmetic.CONTROLS}, paths)
    if 'outer-unary-arithmetic' in checked:
        checks += nested.compiler_conditions({nested.BINARY_CONTROL: checked['outer-unary-arithmetic']}, {nested.BINARY_CONTROL: paths['outer-unary-arithmetic']})
    if CONST_CONTROL in checked:
        checks += constants.compiler_conditions({'unary-integer-constant': checked[CONST_CONTROL]}, {'unary-integer-constant': paths[CONST_CONTROL]})
    for index, name in enumerate(('unary-boolean-constant', 'unary-numeric-concat')):
        if name not in checked:
            continue
        state, origin, child = 'S_kind_' + str(index), 'porigin_kind_' + str(index), 'porigin_kind_child_' + str(index)
        checks += [state + ' = $php_run(' + checked[name]['fixture'] + ', 0, ' + json.dumps(base64.b64encode(bytes(paths[name])).decode()) + ')',
            state + '.COMPLETION = BUDGET',
            '$special_review_concat_path(' + state + '.SOURCES[0].OCCURRENCES) = (pcpath_kind_' + str(index) + ')',
            origin + ' = PORIGIN 0 pcpath_kind_' + str(index),
            '$compiled_read(' + state + ', ' + origin + ') = (PSTRING ($ptascii("1x")))',
            '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = ' + ('($ptascii("1x"))' if index == 0 else 'eps'),
            '$compiled_string_value(' + state + ', ' + origin + ', PSTRING ($ptascii("1x"))) = ' + ('PSTRING_CARRIER INTERNED_STRING' if index == 0 else 'PSTRING') + ' ($ptascii("1x"))',
            '$origin_child((' + origin + '), [PCFIELD 0, PCFIELD 0]) = (' + child + ')',
            '$compiled_read(' + state + ', ' + child + ') = (PINT 1)',
            '$compiled_special_concat_bytes(' + state + ', ' + child + ') = ' + ('($ptascii("1"))' if index == 0 else 'eps')]
    return checks


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    watched = [Path(__file__), Path(arithmetic.__file__), Path(constants.__file__), Path(nested.__file__), Path(prior.__file__), Path(arithmetic.floating.__file__)]
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
    report['scope'] = 'Four actual unary PINT-constant/arithmetic source-state fixtures authenticate every actual child, own fact, shared compiled precision, pure result and recursive certificate. Missing/wrong facts, absent source children and wrong source kinds remain refused; certified Boolean children now join the admitted domain. Compile14/live17, borrowed owners, supplied throw, fixed negative bounds and budgets retain their existing laws. Current compiler controls admit certified arithmetic, integer-constant and Boolean children while retaining warningful, nonarithmetic, assigning, array and numeric-CONCAT refusals. Historical cuts retain their identities without replay.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
