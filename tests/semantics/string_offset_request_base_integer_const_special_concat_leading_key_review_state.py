#!/usr/bin/env python3
"""Independent resolved integer constant facts and retained-base continuations."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_integer_const_special_concat_leading_key_cases as cases
import string_offset_request_base_integer_special_concat_leading_key_review_state as prior

runner = prior.runner
CONTROLS = {
    'namespace-fallback-integer-constant': b"<?php namespace Local; $x = (E_ERROR . null) . 'x';\n",
    'unary-integer-constant': b"<?php $x = (+E_ERROR . null) . 'x';\n",
    'float-constant': b"<?php $x = (\\INF . null) . 'x';\n"}


def conditions(program, path, index):
    route = (0, 0, 1, 2)[index]
    checks, derived = prior.conditions(program, path, route)
    old_integer, integer = (3 if route == 2 else 1), (1, 2, 1, 4)[index]
    old_key, key = str(old_integer) + 'x', str(integer) + 'x'
    old_output = prior.cases.OUTPUTS[route]
    replacements = {
        '$ptascii("' + old_key + '")': '$ptascii("' + key + '")',
        '$ptascii("Uninitialized string offset ' + str(old_integer) + '")':
            '$ptascii("Uninitialized string offset ' + str(integer) + '")',
        'STRING_LEADING ' + str(old_integer): 'STRING_LEADING ' + str(integer),
        'STRING_BOUNDS ' + str(old_integer): 'STRING_BOUNDS ' + str(integer),
        '$string_read_request_base_saved(S, pstringread) = (' + str(old_integer) + ')':
            '$string_read_request_base_saved(S, pstringread) = (' + str(integer) + ')',
        '$compiled_read(S, porigin_inner) = (PSTRING ($ptascii("' + str(old_integer) + '")))':
            '$compiled_read(S, porigin_inner) = (PSTRING ($ptascii("' + str(integer) + '")))',
        '[' + ','.join(map(str, old_output)) + ']': '[' + ','.join(map(str, cases.OUTPUTS[index])) + ']'}
    if index == 1:
        replacements['$ptascii("b")'] = '$ptascii("c")'
    for old, new in replacements.items():
        checks = [check.replace(old, new) for check in checks]
    old_node = 'NScalarInt (INTEGER ' + str(old_integer) + ') metadata_integer'
    new_node = 'NExprConstFetch name_integer metadata_integer'
    checks = [check.replace(old_node, new_node).replace('porigin_integer', 'porigin_constant') for check in checks]
    replacements = {
        '$compiled_read(S, porigin_constant) = (PINT ' + str(old_integer) + ')':
            '$compiled_read(S, porigin_constant) = (PINT ' + str(integer) + ')',
        '$parser_literal_at(' + new_node + ', 14) = (PINT ' + str(old_integer) + ')':
            '$parser_literal_at(' + new_node + ', 14) = eps',
        '$compiled_special_concat_bytes(S, porigin_constant) = ($ptascii("' + str(old_integer) + '"))':
            '$compiled_special_concat_bytes(S, porigin_constant) = ($ptascii("' + str(integer) + '"))'}
    for old, new in replacements.items():
        assert checks.count(old) == 1, old
        checks[checks.index(old)] = new
    spelling = ('E_ERROR', 'Leaf', 'E_ERROR', 'E_PARSE')[index]
    qualifier = 'PTFULL' if index == 2 else 'PTPLAIN'
    checks += [
        '$ptast(name_integer) = PTNAME ' + qualifier + ' ($ptascii("' + spelling + '"))',
        r'S.PRECISIONINI = $ptascii("17") /\ $precision_value(S) = 17',
        '$compiled_precision(S, (porigin_constant)) = (14)']
    # Compiled values are internal compiler-proved inputs, not a public API for
    # forged pools. These guards check the newly admitted type and dependencies.
    guards = runner.lines(r'''
S_drop_constant = S_after[.POOLS = $special_review_pools(S_after.POOLS, porigin_constant, eps)]
$compiled_read(S_drop_constant, porigin_constant) = eps
$compiled_special_concat_bytes(S_drop_constant, porigin_constant) = eps
$compiled_special_concat_bytes(S_drop_constant, porigin_key) = eps
$string_read_request_base_saved(S_drop_constant, pstringread) = eps
S_float_constant = S_after[.POOLS = $special_review_pools(S_after.POOLS, porigin_constant, (PFLOAT 4607182418800017408))]
$compiled_read(S_float_constant, porigin_constant) = (PFLOAT 4607182418800017408)
$compiled_special_concat_bytes(S_float_constant, porigin_constant) = eps
$compiled_special_concat_bytes(S_float_constant, porigin_key) = eps
$string_read_request_base_saved(S_float_constant, pstringread) = eps
S_constant_no_code = S_after[.CODE = eps]
$compiled_read(S_constant_no_code, porigin_constant) = eps
$compiled_special_concat_bytes(S_constant_no_code, porigin_constant) = eps
S_constant_live_precision = S_after[.PRECISIONINI = $ptascii("9")][.PRECISIONMODIFIED = true]
$precision_value(S_constant_live_precision) = 9
''') + [
        'S_wrong_constant = S_after[.POOLS = $special_review_pools(S_after.POOLS, porigin_constant, (PINT ' + str(integer + 1) + '))]',
        '$compiled_special_concat_bytes(S_wrong_constant, porigin_constant) = ($ptascii("' + str(integer + 1) + '"))',
        '$compiled_special_concat_bytes(S_wrong_constant, porigin_key) = eps',
        '$string_read_request_base_saved(S_wrong_constant, pstringread) = eps',
        '$compiled_special_concat_bytes(S_constant_live_precision, porigin_constant) = ($ptascii("' + str(integer) + '"))',
        '$compiled_special_concat_bytes(S_constant_live_precision, porigin_key) = ($ptascii("' + key + '"))',
        '$string_read_request_base_saved(S_constant_live_precision, pstringread) = (' + str(integer) + ')']
    checks += guards
    return checks, derived + len(guards)


def compiler_conditions(checked, paths):
    checks = []
    for index, (name, value) in enumerate(checked.items()):
        state, origin = 'S_bound_' + str(index), 'porigin_bound_' + str(index)
        path, child = 'pcpath_bound_' + str(index), 'porigin_bound_child_' + str(index)
        expression = 'expression_bound_' + str(index)
        key = 'INFx' if index == 2 else '1x'
        checks += [
            state + ' = $php_run(' + value['fixture'] + ', 0, ' + json.dumps(base64.b64encode(bytes(paths[name])).decode()) + ')',
            state + '.COMPLETION = BUDGET',
            '$special_review_concat_path(' + state + '.SOURCES[0].OCCURRENCES) = (' + path + ')',
            origin + ' = PORIGIN 0 ' + path,
            '$compiled_read(' + state + ', ' + origin + ') = ' + ('eps' if index == 0 else '(PSTRING ($ptascii("' + key + '")))'),
            '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps',
            '$compiled_string_value(' + state + ', ' + origin + ', PSTRING ($ptascii("' + key + '"))) = PSTRING ($ptascii("' + key + '"))',
            '$origin_child((' + origin + '), [PCFIELD 0, PCFIELD 0]) = (' + child + ')',
            '$origin_node(' + state + '.SOURCES, ' + child + ') = (' + expression + ')',
            '$compiled_special_concat_bytes(' + state + ', ' + child + ') = eps']
        if index == 1:
            checks += [
                expression + ' = NExprUnaryPlus expression_unary_bound metadata_unary_bound',
                '$compiled_read(' + state + ', ' + child + ') = (PINT 1)',
                '$origin_child((' + child + '), [PCFIELD 0]) = (porigin_unary_constant_bound)',
                '$origin_node(' + state + '.SOURCES, porigin_unary_constant_bound) = (expression_unary_bound)',
                'expression_unary_bound = NExprConstFetch name_unary_bound metadata_constant_bound',
                '$compiled_read(' + state + ', porigin_unary_constant_bound) = (PINT 1)',
                '$compiled_special_concat_bytes(' + state + ', porigin_unary_constant_bound) = ($ptascii("1"))']
        else:
            checks += [
                expression + ' = NExprConstFetch name_bound_' + str(index) + ' metadata_bound_' + str(index),
                '$compiled_read(' + state + ', ' + child + ') = ' + ('eps' if index == 0 else '(PFLOAT 9218868437227405312)')]
    return checks


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    watched = [Path(__file__), Path(prior.__file__)]
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
    report['scope'] = 'Four actual global/imported/fully qualified PINT ConstFetch source-state fixtures check own facts, type/root dependencies, live precision independence, borrowed owners, supplied throw, genuine later bounds and budgets. Compiler-only controls retain late namespace fallback, unary ConstFetch and floating ConstFetch limits. The internal compiler-proof boundary is unchanged; arbitrary forged pools are not validated. Older source/native/state/compiler cuts retain their identities without replay.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
