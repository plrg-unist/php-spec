#!/usr/bin/env python3
"""Independent float truth, active operands and genuine skipped-code checks."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_float_logical_special_concat_leading_key_cases as cases
import string_offset_request_base_float_logical_special_concat_leading_key_protocol as source
import string_offset_request_base_numeric_comparison_special_concat_leading_key_review_state as numeric

runner = numeric.runner
HELPERS = r'''
dec $logical_review_unused(ppool*, porigin, pvalue) : ppool*
def $logical_review_unused(eps, porigin, pvalue) = eps
def $logical_review_unused(ppool :: ppool_tail*, PORIGIN n pcpath, pvalue) = ppool[.CONSTANTS = (PCONSTANT pcpath pvalue) :: ppool.CONSTANTS] :: ppool_tail*
  -- if ppool.UNIT = n
def $logical_review_unused(ppool :: ppool_tail*, PORIGIN n pcpath, pvalue) = ppool :: $logical_review_unused(ppool_tail*, PORIGIN n pcpath, pvalue)
  -- if ppool.UNIT =/= n
'''
FORMS = {'BooleanAnd': ('&&', False), 'LogicalAnd': ('and', False),
         'BooleanOr': ('||', True), 'LogicalOr': ('or', True), 'Xor': ('xor', None)}
VALUES = {
    'zero': ('0.0', '0', False), 'negative-zero': ('-0.0', '9223372036854775808', False),
    'one': ('1.5', '4609434218613702656', True), 'negative': ('-2.5', '13836183955189006336', True),
    'infinity': ('1e309', '9218868437227405312', True), 'negative-infinity': ('-1e309', '18442240474082181120', True),
    'subnormal': ('5e-324', '1', True), 'missing': ('$missing', None, None), 'nan': ('NAN', None, None)}
ROWS = {form + '-' + left + '-' + right: (form, left, right)
        for form in FORMS for left in ('zero', 'one') for right in ('zero', 'one')}
for form in FORMS:
    ROWS[form + '-signed-zero'] = form, 'negative-zero', 'subnormal'
    ROWS[form + '-infinite'] = form, 'negative-infinity', 'zero'
ROWS.update({
    'xor-infinities': ('Xor', 'infinity', 'negative-infinity'),
    'xor-subnormal': ('Xor', 'subnormal', 'zero'),
    'xor-negative': ('Xor', 'negative', 'one'),
    'or-dead-variable': ('BooleanOr', 'one', 'missing'),
    'and-dead-variable': ('LogicalAnd', 'zero', 'missing'),
    'or-dead-nan': ('LogicalOr', 'one', 'nan'),
    'and-dead-nan': ('BooleanAnd', 'zero', 'nan')})
CONTROLS = {name: ("<?php $x = ((" + VALUES[left][0] + ' ' + FORMS[form][0] + ' ' + VALUES[right][0] + ") . null) . 'x';\n").encode()
            for name, (form, left, right) in ROWS.items()} | {
    'live-variable': b"<?php $x = ((1.5 && $missing) . null) . 'x';\n",
    'live-array': b"<?php $x = ((0.0 || []) . null) . 'x';\n",
    'xor-array': b"<?php $x = ((1.5 xor []) . null) . 'x';\n",
    'direct-not': b"<?php $x = ((!0.0) . null) . 'x';\n",
    'composed-not': b"<?php $x = ((!(1.5-1.5)) . null) . 'x';\n",
    'nan-xor': b"<?php $x = ((NAN xor false) . null) . 'x';\n"}
NODES = (
    (('logical_root_child', False, True, False), ('logical_root_child_l', True, False, True)),
    (('logical_root_child_l', None, True, False),),
    (('logical_root_l', False, False, None),),
    (('logical_root_child_l', False, True, True), ('logical_root_child_l_l', False, True, True),
     ('logical_root_child_l_l_r', True, True, None), ('logical_root_child_l_r', True, False, True)))


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    guards = []
    for tag, b_or, left_truth, right_truth in NODES[index]:
        origin, expression, stem = 'porigin_' + tag, 'expression_' + tag, 'S_peer_' + tag
        skipped = b_or is not None and left_truth == b_or
        own = left_truth != right_truth if b_or is None else b_or if skipped else right_truth
        rendered = '1' if own else ''
        guards += [origin + ' = PORIGIN n_' + tag + ' pcpath_' + tag,
                   origin + '_l = PORIGIN n_' + tag + ' pcpath_' + tag + '_l',
                   origin + '_r = PORIGIN n_' + tag + ' pcpath_' + tag + '_r']
        for label, value in (('drop', 'eps'), ('wrong', '(PBOOL ' + str(not own).lower() + ')'), ('type', '(PINT ' + str(int(own)) + ')')):
            state = stem + '_' + label
            guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + origin + ', ' + value + ')]',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps',
                       '$string_read_request_base_saved(' + state + ', pstringread) = eps']
        for field, suffix in enumerate(('_l', '_r')):
            child = origin + suffix
            if field == 0 or not skipped:
                state = stem + '_drop' + suffix
                guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + child + ', eps)]',
                           '$compiled_read(' + state + ', ' + child + ') = eps',
                           '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
                state = stem + '_precision' + suffix
                guards += [state + ' = S_after[.POOLS = $float_review_precision(S_after.POOLS, ' + child + ', 17)]',
                           '$compiled_precision(' + state + ', (' + child + ')) = (17)',
                           '$compiled_precision(' + state + ', (' + origin + ')) = (14)',
                           '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
            else:
                state = stem + '_unused'
                guards += [state + ' = S_after[.POOLS = $float_review_precision($logical_review_unused(S_after.POOLS, ' + child + ', PFLOAT 9221120237041090560), ' + child + ', 17)]',
                           '$pool_value(' + state + '.POOLS, ' + child + ') = (PFLOAT 9221120237041090560)',
                           '$compiled_read(' + state + ', ' + child + ') = eps',
                           '$compiled_precision(' + state + ', (' + child + ')) = (17)',
                           '$compiled_precision(' + state + ', (' + origin + ')) = (14)',
                           '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = ($ptascii(' + json.dumps(rendered) + '))']
            other = 'expression_peer_' + tag
            if field == 0:
                guards += [other + ' = NExprVariable (BYTES "dW5hdXRo") metadata_' + tag]
            left, right = (other, expression + '_r') if field == 0 else (expression + '_l', other)
            state = stem + '_source' + suffix
            guards += [state + ' = S_after[.SOURCES = [{ID n_' + tag + ', AST (PROGRAM eps), OCCURRENCES ([(PCOCCURRENCE pcpath_' + tag + ' ' + expression + '), (PCOCCURRENCE pcpath_' + tag + '_l ' + left + '), (PCOCCURRENCE pcpath_' + tag + '_r ' + right + ')])}]]',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
        guards += [stem + '_precision = S_after[.POOLS = $float_review_precision(S_after.POOLS, ' + origin + ', 17)]',
                   '$compiled_precision(' + stem + '_precision, (' + origin + ')) = (17)',
                   '$compiled_special_concat_bytes(' + stem + '_precision, ' + origin + ') = eps']
    guards += numeric.prior.unary_guards([], ('1x', '-1x', '0x', '-4x')[index])
    return checks + guards, derived + len(guards)


def compiler_conditions(checked, paths):
    checks = []
    for index, name in enumerate(CONTROLS):
        state, origin = 'S_logical_control_' + str(index), 'porigin_logical_control_' + str(index)
        binary = origin + '_binary'
        checks += [state + ' = $php_run(' + checked[name]['fixture'] + ', 0, ' + json.dumps(base64.b64encode(bytes(paths[name])).decode()) + ')',
                   state + '.COMPLETION = BUDGET',
                   '$special_review_concat_path(' + state + '.SOURCES[0].OCCURRENCES) = (pcpath_logical_control_' + str(index) + ')',
                   origin + ' = PORIGIN 0 pcpath_logical_control_' + str(index),
                   '$origin_child((' + origin + '), [PCFIELD 0, PCFIELD 0]) = (' + binary + ')']
        if name not in ROWS:
            checks += ['$compiled_special_concat_bytes(' + state + ', ' + binary + ') = eps',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
            if name in ('direct-not', 'composed-not'):
                checks += ['$compiled_read(' + state + ', ' + binary + ') = eps']
            continue
        form, left_name, right_name = ROWS[name]
        b_or, left, right = FORMS[form][1], VALUES[left_name], VALUES[right_name]
        skipped = b_or is not None and left[2] == b_or
        result = left[2] != right[2] if b_or is None else b_or if skipped else right[2]
        rendered = '1' if result else ''
        checks += ['$compiled_read(' + state + ', ' + binary + ') = (PBOOL ' + str(result).lower() + ')',
                   '$compiled_precision(' + state + ', (' + binary + ')) = (14)',
                   '$compiled_special_concat_bytes(' + state + ', ' + binary + ') = ($ptascii(' + json.dumps(rendered) + '))',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = ($ptascii(' + json.dumps(rendered + 'x') + '))',
                   '$compiled_string_value(' + state + ', ' + origin + ', PSTRING ($ptascii(' + json.dumps(rendered + 'x') + '))) = PSTRING_CARRIER INTERNED_STRING ($ptascii(' + json.dumps(rendered + 'x') + '))']
        for field, value in enumerate((left, right)):
            child = binary + '_' + str(field)
            checks += ['$origin_child((' + binary + '), [PCFIELD ' + str(field) + ']) = (' + child + ')']
            if field == 1 and skipped:
                checks += [child + ' = PORIGIN n_logical_dead_' + str(index) + ' pcpath_logical_dead_' + str(index),
                           '$code_at(' + state + '.CODE, n_logical_dead_' + str(index) + ') = (pcode_logical_dead_' + str(index) + ')',
                           '$code_expression(pcode_logical_dead_' + str(index) + '.EXPRESSIONS, pcpath_logical_dead_' + str(index) + ') = eps',
                           '$compiled_read(' + state + ', ' + child + ') = eps',
                           '$compiled_precision(' + state + ', (' + child + ')) = $source_precision(' + state + ', (' + child + '))']
            else:
                checks += ['$compiled_read(' + state + ', ' + child + ') = (PFLOAT ' + value[1] + ')',
                           '$compiled_precision(' + state + ', (' + child + ')) = (14)',
                           '$compiled_special_concat_bytes(' + state + ', ' + child + ') =/= eps',
                           '$compiled_order_number(PFLOAT ' + value[1] + ') = (NFLOAT ' + value[1] + ')',
                           '$number_bool(NFLOAT ' + value[1] + ') = (' + str(value[2]).lower() + ', false)']
        if name == 'Xor-one-zero':
            child = binary + '_0'
            for label, bits in (('nan', '9221120237041090560'), ('invalid', '18446744073709551616')):
                changed = state + '_' + label
                checks += [changed + ' = ' + state + '[.POOLS = $special_review_pools(' + state + '.POOLS, ' + child + ', (PFLOAT ' + bits + '))]',
                           '$compiled_special_concat_bytes(' + changed + ', ' + child + ') =/= eps',
                           '$compiled_read(' + changed + ', ' + binary + ') = (PBOOL true)',
                           '$compiled_order_number(PFLOAT ' + bits + ') = eps',
                           '$compiled_special_concat_bytes(' + changed + ', ' + binary + ') = eps']
    return checks


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    watched = [Path(module.__file__) for module in (source, source.prior, source.logical, source.xor, source.boolnot, source.arithmetic, source.unary, numeric, numeric.prior, runner)] + [Path(__file__)]
    before = {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.HELPERS += HELPERS
    runner.cases, runner.conditions = cases, conditions
    runner.compiler_conditions, runner.CONTROLS = compiler_conditions, CONTROLS
    passed = runner.main(expected_outputs=cases.OUTPUTS)
    assert before == {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = 'Four authentic-source-seeded fixtures add own-result/type, evaluated missing-read, actual source and precision fences for every logical node. Genuine raw NaN pool entries at skipped RHSs are asserted through pool_value while compiled_read stays absent; conflicting RHS precision does not affect admission. Independent compiler tables cover all five forms, signed zero, negative/infinite/subnormal truth, active versus skipped operands, undefined/NaN skipped syntax, and direct/composed !FLOAT, active array/variable and NaN XOR refusals. Same-byte NaN/invalid64bit pool values retain cached XORtrue but fail the quiet FLOAT gate. No result-insensitive changed-left-value refusal is claimed. Author recipes remain exact prefixes, native4 are reused once, and owners/saved throw/fixed bounds/budgets retain their laws. Seven old selectors and six pool predicates have separate affected cuts; no old full replay or unique aggregate. Fixture/compiler conditions carry source0 and no NaN Boolean/string conversion or new ownership claim.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
