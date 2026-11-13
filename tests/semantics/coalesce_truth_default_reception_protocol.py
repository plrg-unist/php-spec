#!/usr/bin/env python3
"""Coalesce truth keeps nullness, selected values and default ownership distinct."""
import base64
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('coalesce_truth_default_reception_cases.json')
SOURCES = {}
for row in json.loads(CATALOGUE.read_text()):
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
    SOURCES[row['id']] = row['source']

# Fresh first-VAL front preserves the whole five-default declaration; source0.
full = SOURCES['coalesce-truth-precision-modes']
setup = full.index("set_error_handler('warningReceive202');")
start = full.index('$gotReceive202 = valueFirstReceive202(')
end = full.index('$xReceive202 = 1.5;', start)
source = full[:full.index('function referenceFirstReceive202')] + full[setup:end]
assert hashlib.sha256(source.encode()).hexdigest() == '2ecf48a52c1c85f6a9a1c354e8c70c230be7266aa328966bc12325ef200c5769'

metadata_index = 0
fixed_metadata = None
def node(constructor, *children):
    global metadata_index
    metadata_index += 1
    metadata = fixed_metadata or f'metadata_case_{metadata_index}'
    return constructor + ''.join(f' ({child})' for child in children) + ' ' + metadata


def integer(value):
    return node('NScalarInt', f'INTEGER {value}')


def constant(name, qualified=False):
    payload = base64.b64encode(name.encode()).decode()
    return node('NExprConstFetch', node('NNameFullyQualified' if qualified else 'NName', f'BYTES "{payload}"'))


def string(value):
    return node('NScalarString', f'BYTES "{base64.b64encode(value.encode()).decode()}"')


def floating(bits):
    return node('NScalarFloat', f'FLOAT "{bits}"')


def boolean(child):
    return node('NExprCastBool', child)


def cast(child):
    return node('NExprCastInt', child)


def add(left, right):
    return node('NExprBinaryOpPlus', left, right)


def binary(constructor, left, right):
    return node('NExprBinaryOp' + constructor, left, right)


def conditional(cond, yes, no):
    return node('NExprTernary', cond, yes, no)


patterns = [
    node('NExprUnaryMinus', conditional(binary('Coalesce', constant('false'), constant('UnselectedReceive202')), constant('UnselectedReceive202'), integer(7))),
    cast(conditional(binary('Coalesce', constant('null'), conditional(constant('true'), string('0'), constant('UnselectedReceive202'))), 'ABSENT', string('-11tail'))),
    cast(conditional(binary('Coalesce', conditional(constant('false'), constant('UnselectedReceive202'), string('13tail')), constant('UnselectedReceive202')), 'ABSENT', constant('UnselectedReceive202'))),
    conditional(binary('Coalesce', conditional(constant('true'), constant('null'), constant('UnselectedReceive202')), constant('true')),
                cast(node('NExprUnaryMinus', floating('43e0000000000000'))), constant('UnselectedReceive202')),
    cast(conditional(binary('Coalesce', conditional(constant('false'), constant('UnselectedReceive202'), node('NExprUnaryPlus', floating('7ff0000000000000'))), constant('UnselectedReceive202')),
                     string('999999999999999999999999'), constant('UnselectedReceive202'))),
]

checks = [
    r'n_bits = 4609434218613702656 /\ i = 1',
    '$function_at(S.FUNCTIONS, porigin) = (pfunction)',
    'plenv_source = pfunction.ENV',
    r'plenv_source.NAMESPACE = eps /\ plenv_source.CONSTANTS = eps',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_a, psparam_b, psparam_c, psparam_d, psparam_e]',
    r'~psparam_a.REQUIRED /\ ~psparam_a.BYREF /\ psparam_b.BYREF /\ psparam_d.BYREF /\ psparam_e.BYREF',
]
for index, (letter, pattern, value) in enumerate(zip(
    'abcde', patterns, ('$(-7)', '$(-11)', '13', '$(-9223372036854775808)', '9223372036854775807'),
)):
    checks.extend([
        f'psparam_{letter}.DEFAULT = PSDEFAULT expression_{letter} "int"',
        f'expression_{letter} = {pattern}',
        f'$lossy_optional_integer_default_in(plenv_source, expression_{letter}) = ({value})',
        f'$default_parameter_origin(S, porigin, {index}) = PORIGIN n_unit pcpath_{letter}',
        f'porigin_{letter} = PORIGIN n_unit (pcpath_{letter} ++ [PCFIELD 6])',
        f'$origin_node(S.SOURCES, porigin_{letter}) = (expression_{letter})',
        f'$default_at(pfunction.DEFAULTS, {index}) = ({{INDEX {index}, ORIGIN porigin_{letter}, KIND PDSTORED}})',
        f'$compiled_read(S, porigin_{letter}) = (PINT {value})',
    ])
fixed_metadata = 'metadata_a'
checks.extend([
    '$lossy_optional_integer_header(S, pfunction, pfunction.SIGNATURE.PARAMETERS, 0)',
    'expression_a = NExprUnaryMinus expression_select_a metadata_a',
    'expression_select_a = NExprTernary expression_coalesce_a expression_unknown_a expression_seven metadata_select_a',
    'expression_coalesce_a = NExprBinaryOpCoalesce expression_false_a expression_unknown_rhs_a metadata_coalesce_a',
    '$lossy_optional_integer_leaf_truth(plenv_source, expression_coalesce_a) = ((expression_false_a, false))',
    '$lossy_optional_integer_special(plenv_source, expression_false_a) = (PBOOL false)',
    'expression_b = NExprCastInt expression_short_b metadata_b',
    'expression_short_b = NExprTernary expression_coalesce_b ABSENT expression_string_b metadata_short_b',
    'expression_coalesce_b = NExprBinaryOpCoalesce expression_null_b expression_select_b metadata_coalesce_b',
    'expression_select_b = NExprTernary expression_true_b expression_zero_string_b expression_unknown_b metadata_select_b',
    '$lossy_optional_integer_leaf_truth(plenv_source, expression_coalesce_b) = ((expression_zero_string_b, false))',
    '$lossy_optional_integer_special(plenv_source, expression_null_b) = (PNULL)',
    '$lossy_optional_integer_cast_leaf(plenv_source, expression_short_b) = (expression_string_b)',
    'expression_c = NExprCastInt expression_short_c metadata_c',
    'expression_short_c = NExprTernary expression_coalesce_c ABSENT expression_unknown_c metadata_short_c',
    'expression_coalesce_c = NExprBinaryOpCoalesce expression_select_c expression_unknown_rhs_c metadata_coalesce_c',
    'expression_select_c = NExprTernary expression_false_c expression_unknown_inner_c expression_string_c metadata_select_c',
    '$lossy_optional_integer_leaf_truth(plenv_source, expression_coalesce_c) = ((expression_string_c, true))',
    '$lossy_optional_integer_cast_leaf(plenv_source, expression_short_c) = (expression_string_c)',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt expression_string_c metadata_c) = (13)',
    'expression_d = NExprTernary expression_coalesce_d expression_minimum_cast expression_unknown_d metadata_d',
    'expression_coalesce_d = NExprBinaryOpCoalesce expression_select_d expression_true_rhs_d metadata_coalesce_d',
    'expression_select_d = NExprTernary expression_true_d expression_null_d expression_unknown_inner_d metadata_select_d',
    '$lossy_optional_integer_leaf_truth(plenv_source, expression_select_d) = ((expression_null_d, false))',
    '$lossy_optional_integer_leaf_truth(plenv_source, expression_coalesce_d) = ((expression_true_rhs_d, true))',
    'expression_e = NExprCastInt expression_select_e metadata_e',
    'expression_select_e = NExprTernary expression_coalesce_e expression_string_e expression_unknown_e metadata_select_e',
    'expression_coalesce_e = NExprBinaryOpCoalesce expression_inner_e expression_unknown_rhs_e metadata_coalesce_e',
    'expression_inner_e = NExprTernary expression_false_e expression_unknown_inner_e expression_inf_e metadata_inner_e',
    '$lossy_optional_integer_leaf_truth(plenv_source, expression_coalesce_e) = ((expression_inf_e, true))',
    '$lossy_optional_integer_float_literal(expression_inf_e) = ($hex_bits("7ff0000000000000", 0))',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt expression_inf_e metadata_e) = eps',
    '$call_target(S, $ptascii("deferredFloatNotReceive202"), eps) = (pfunction_not)',
    'pfunction_not.SIGNATURE.PARAMETERS = [psparam_not]',
    '$ptmasks(psparam_not.TYPE) = ["int"]',
    'psparam_not.DEFAULT = PSDEFAULT expression_not "deferred"',
    'expression_not = NExprCastInt (NExprBooleanNot (NScalarFloat (FLOAT "3fe0000000000000") metadata_not_float) metadata_not_bool) metadata_not_cast',
    '$lossy_optional_integer_default_in(pfunction_not.ENV, expression_not) = (0)',
    '$default_parameter_origin(S, pfunction_not.ORIGIN, 0) = PORIGIN n_unit_not pcpath_not',
    'porigin_not = PORIGIN n_unit_not (pcpath_not ++ [PCFIELD 6])',
    '$origin_node(S.SOURCES, porigin_not) = (expression_not)',
    '$default_at(pfunction_not.DEFAULTS, 0) = ({INDEX 0, ORIGIN porigin_not, KIND PDDEFERRED})',
    '$compiled_read(S, porigin_not) = eps',
    '~$lossy_optional_integer_header(S, pfunction_not, pfunction_not.SIGNATURE.PARAMETERS, 0)',
    '~$lossy_optional_integer_tail(S, pfunction_not, [psparam_not[.DEFAULT = PSDEFAULT expression_not "int"]], 0)',
    'plenv_null_alias = plenv_source[.CONSTANTS = [($ptascii("null"), $ptascii("false"))]]',
    '$lossy_optional_integer_default_in(plenv_null_alias, expression_d) = eps',
    '~$lossy_optional_integer_header(S, pfunction[.ENV = plenv_null_alias], pfunction.SIGNATURE.PARAMETERS, 0)',
    'expression_same = NExprUnaryMinus (NScalarInt (INTEGER 7) metadata_a) metadata_a',
    '$lossy_optional_integer_default_in(plenv_source, expression_same) = ($(-7))',
    '~$lossy_optional_integer_tail(S, pfunction, [psparam_a[.DEFAULT = PSDEFAULT expression_same "int"]], 0)',
    'pfunction.DEFAULTS = [pdefault_a, pdefault_b, pdefault_c, pdefault_d, pdefault_e]',
    '~$lossy_optional_integer_tail(S, pfunction[.DEFAULTS = [pdefault_a, pdefault_b[.KIND = PDDEFERRED], pdefault_c, pdefault_d, pdefault_e]], [psparam_b], 1)',
    'S_wrong_value = S[.POOLS = [{UNIT n_unit, CONSTANTS ([(PCONSTANT (pcpath_c ++ [PCFIELD 6]) (PINT 1))])}]]',
    '$compiled_read(S_wrong_value, porigin_c) = (PINT 1)',
    '~$lossy_optional_integer_tail(S_wrong_value, pfunction, [psparam_c], 2)',
])
true, false, null = map(constant, ('true', 'false', 'null'))
unknown = constant('UnselectedReceive202')
# Only null selects the coalesce RHS; falsy values retain their original leaf.
for leaf, truth in [
    (false, 'false'), (integer(0), 'false'), (string(''), 'false'),
    (string('0'), 'false'), (floating('8000000000000000'), 'false'),
    (string('13tail'), 'true'), (floating('7ff0000000000000'), 'true'),
    (boolean(null), 'false'), (cast(null), 'false'),
]:
    expression = binary('Coalesce', leaf, unknown)
    checks.extend([
        f'$lossy_optional_integer_leaf_truth(plenv_source, {expression}) = (({leaf}, {truth}))',
        f'$lossy_optional_integer_condition(plenv_source, {expression}) = ({truth})',
    ])
for expression, leaf, truth in [
    (binary('Coalesce', null, string('0')), string('0'), 'false'),
    (binary('Coalesce', conditional(true, null, false), integer(13)), integer(13), 'true'),
    (binary('Coalesce', conditional(true, false, null), unknown), false, 'false'),
    (conditional(string('13tail'), 'ABSENT', unknown), string('13tail'), 'true'),
    (conditional(string('0'), 'ABSENT', null), null, 'false'),
]:
    checks.extend([
        f'$lossy_optional_integer_leaf_truth(plenv_source, {expression}) = (({leaf}, {truth}))',
        f'$lossy_optional_integer_condition(plenv_source, {expression}) = ({truth})',
    ])
for expression in [
    binary('Coalesce', unknown, integer(13)),
    binary('Coalesce', floating('7ff8000000000000'), integer(13)),
    binary('Coalesce', null, floating('7ff8000000000000')),
    conditional(unknown, integer(13), integer(13)),
    conditional(true, floating('7ff8000000000000'), false),
]:
    checks.extend([
        f'$lossy_optional_integer_leaf_truth(plenv_source, {expression}) = eps',
        f'$lossy_optional_integer_condition(plenv_source, {expression}) = eps',
    ])
checks.extend([
    f'$lossy_optional_integer_condition(plenv_source, {binary("Coalesce", false, floating("7ff8000000000000"))}) = (false)',
    f'$lossy_optional_integer_condition(plenv_null_alias, {binary("Coalesce", constant("null", qualified=True), true)}) = (true)',
    f'$lossy_optional_integer_default_in(plenv_source, {binary("Coalesce", false, unknown)}) = eps',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(binary("Coalesce", false, unknown))}) = (0)',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(binary("Coalesce", floating("7ff0000000000000"), unknown))}) = eps',
    f'$lossy_optional_integer_condition(plenv_source, {binary("Coalesce", integer(0), unknown)}) = (false)',
    f'$lossy_optional_integer_selection_shape({conditional(true, integer(7), unknown)})',
    f'$lossy_optional_integer_selection_shape({binary("Coalesce", false, unknown)})',
    f'$lossy_optional_integer_condition(plenv_source, {boolean(binary("Coalesce", boolean(string("0")), unknown))}) = (false)',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(boolean(binary("Coalesce", boolean(string("0")), unknown)))}) = (0)',
    f'$lossy_optional_integer_condition(plenv_source, {binary("Coalesce", false, unknown)}) = (false)',
    f'$lossy_optional_integer_condition(plenv_source, {boolean(binary("Coalesce", false, unknown))}) = (false)',
])
# Cached certificates keep deep left-coalesce/true-shorthand recursion bounded.
deep = false
for _ in range(24):
    deep = binary('Coalesce', deep, unknown)
checks.append(f'$lossy_optional_integer_leaf_truth(plenv_source, {deep}) = (({false}, false))')
leaf = string('13tail');deep = leaf
for _ in range(24):
    deep = conditional(deep, 'ABSENT', unknown)
checks.append(f'$lossy_optional_integer_leaf_truth(plenv_source, {deep}) = (({leaf}, true))')
checks.extend([
    'S.CURRENT = (pcallcontext)',
    r'pcallcontext.ARGC = 1 /\ pcallcontext.HOLES = eps',
    '$lookup(S.ENV, psparam_a.NAME) = (n_cell)',
    r'$lookup(S.ENV, psparam_b.NAME) = eps /\ $lookup(S.ENV, psparam_c.NAME) = eps /\ $lookup(S.ENV, psparam_d.NAME) = eps /\ $lookup(S.ENV, psparam_e.NAME) = eps',
    r'S.STORE[n_cell] = DEFINED (PFLOAT n_bits) /\ ~(n_cell <- S.REFCELLS)',
    '$heap_owners($heap_graph(S), HCELL n_cell) = 1',
    '$lossy_mixed_parameter_source_valid(S, LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z)',
    '$lossy_mixed_parameter_ready(S, 0, n_cell, n_bits)',
    '$task_nodes(LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z) = eps',
    'S.GLOBALTABLE = (psymboltable_global)',
    '$lookup(psymboltable_global.ENV, $ptascii("xReceive202")) = (n_global)',
    'S.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    'PhpStep: S ~> S_after_0',
    r'S_after_0.TODO = [TYPE_RECEIVE porigin 1] /\ S_after_0.STORE[n_cell] = DEFINED (PINT 1)',
])
for index, letter, integer in [
    (1, 'b', '$(-11)'), (2, 'c', '13'),
    (3, 'd', '$(-9223372036854775808)'), (4, 'e', '9223372036854775807'),
]:
    checks.extend([
        f'PhpStep: S_after_{index - 1} ~> S_default_{index}',
        f'S_default_{index}.TODO = [DEFAULT_RECEIVE porigin {index}]',
        f'PhpStep: S_default_{index} ~> S_after_{index}',
        f'$lookup(S_after_{index}.ENV, psparam_{letter}.NAME) = (n_{letter})',
        f'S_after_{index}.STORE[n_{letter}] = DEFINED (PINT {integer}) /\\ ~(n_{letter} <- S_after_{index}.REFCELLS)',
        f'$heap_owners($heap_graph(S_after_{index}), HCELL n_{letter}) = 1',
    ])
    if index < 4:
        checks.append(f'S_after_{index}.TODO = [TYPE_RECEIVE porigin {index + 1}]')
checks.extend([
    'S_after_4.TODO = $call_receive_body(S_default_4, pfunction)',
    'S_after_4.EVENTS = S.EVENTS',
    r'$call_descriptors_valid(S_after_4) /\ $heap_valid($heap_graph(S_after_4))',
    r'S_after_4.STORE[n_global] = S.STORE[n_global] /\ S_after_4.STORE[n_cell] = DEFINED (PINT 1)',
    'S_done = $drive_steps(S_after_4, 2000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    r'~((HCELL n_cell) <- S_done.ALLOCATIONS) /\ ~((HCELL n_b) <- S_done.ALLOCATIONS) /\ ~((HCELL n_c) <- S_done.ALLOCATIONS) /\ ~((HCELL n_d) <- S_done.ALLOCATIONS) /\ ~((HCELL n_e) <- S_done.ALLOCATIONS)',
    'S_done.STORE[n_global] = S.STORE[n_global]',
    '$lookup(S_done.ENV, $ptascii("gotReceive202")) = (n_got)',
    'S_done.STORE[n_got] = DEFINED (PINT 13)',
    r'$call_descriptors_valid(S_done) /\ $heap_valid($heap_graph(S_done))',
])

CASES = {'coalesce-truth-default-omitted-tail': {
    'source': source,
    'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z]',
    'checks': checks,
}}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
