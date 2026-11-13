#!/usr/bin/env python3
"""Ternary truth preserves selected values, stored-default authority and owners."""
import base64
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('ternary_truth_default_reception_cases.json')
SOURCES = {}
for row in json.loads(CATALOGUE.read_text()):
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
    SOURCES[row['id']] = row['source']

# Fresh first-VAL front preserves the whole five-default declaration; source0.
full = SOURCES['ternary-truth-precision-modes']
setup = full.index("set_error_handler('warningReceive201');")
start = full.index('$gotReceive201 = valueFirstReceive201(')
end = full.index('$xReceive201 = 1.5;', start)
source = full[:full.index('function referenceFirstReceive201')] + full[setup:end]
assert hashlib.sha256(source.encode()).hexdigest() == 'afbc22bd47424f17e67132b75203d515bc2ecc809dafe22d6c76e60c3449d5ce'

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


nested = string('0')
for _ in range(8):
    nested = conditional(nested, constant('true'), constant('false'))
patterns = [
    node('NExprUnaryMinus', conditional(nested, constant('UnselectedReceive201'), integer(7))),
    cast(conditional(conditional(constant('false'), constant('UnselectedReceive201'), string('00')),
                     string('-11tail'), constant('UnselectedReceive201'))),
    cast(conditional(conditional(constant('true'), string('13tail'), constant('UnselectedReceive201')),
                     'ABSENT', constant('UnselectedReceive201'))),
    conditional(conditional(constant('true'), node('NExprUnaryMinus', floating('0000000000000000')),
                            constant('UnselectedReceive201')), constant('UnselectedReceive201'),
                cast(node('NExprUnaryMinus', floating('43e0000000000000')))),
    cast(conditional(conditional(constant('false'), constant('UnselectedReceive201'), node('NExprUnaryPlus', floating('7ff0000000000000'))),
                     string('999999999999999999999999'), constant('UnselectedReceive201'))),
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
    'expression_select_a = NExprTernary expression_depth expression_unknown expression_seven metadata_select_a',
    '$lossy_optional_integer_ternary_shape(expression_depth)',
    '$lossy_optional_integer_condition(plenv_source, expression_depth) = (false)',
    'expression_b = NExprCastInt expression_select_b metadata_b',
    'expression_select_b = NExprTernary expression_string_condition expression_string_b expression_unknown_b metadata_select_b',
    '$lossy_optional_integer_condition(plenv_source, expression_string_condition) = (true)',
    '$lossy_optional_integer_cast_leaf(plenv_source, expression_select_b) = (expression_string_b)',
    'expression_c = NExprCastInt expression_short_c metadata_c',
    'expression_short_c = NExprTernary expression_condition_c ABSENT expression_unknown_c metadata_short_c',
    'expression_condition_c = NExprTernary expression_true_c expression_string_c expression_unknown_inner metadata_condition_c',
    '$lossy_optional_integer_condition(plenv_source, expression_condition_c) = (true)',
    '$lossy_optional_integer_cast_leaf(plenv_source, expression_short_c) = (expression_string_c)',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt expression_string_c metadata_c) = (13)',
    'expression_d = NExprTernary expression_float_condition expression_unknown_d expression_minimum_cast metadata_d',
    '$lossy_optional_integer_condition(plenv_source, expression_float_condition) = (false)',
    'expression_e = NExprCastInt expression_select_e metadata_e',
    'expression_select_e = NExprTernary expression_inf_condition expression_string_e expression_unknown_e metadata_select_e',
    '$lossy_optional_integer_condition(plenv_source, expression_inf_condition) = (true)',
    '$call_target(S, $ptascii("deferredFloatNotReceive201"), eps) = (pfunction_not)',
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
    'plenv_alias = plenv_source[.CONSTANTS = [($ptascii("true"), $ptascii("false"))]]',
    '$lossy_optional_integer_default_in(plenv_alias, expression_c) = eps',
    '~$lossy_optional_integer_header(S, pfunction[.ENV = plenv_alias], pfunction.SIGNATURE.PARAMETERS, 0)',
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
unknown = constant('UnselectedReceive201')
for expression, truth in [
    (conditional(true, false, unknown), 'false'),
    (conditional(false, unknown, true), 'true'),
    (conditional(true, null, unknown), 'false'),
    (conditional(true, string('00'), unknown), 'true'),
    (conditional(false, unknown, string('0')), 'false'),
    (conditional(true, floating('8000000000000000'), unknown), 'false'),
    (conditional(true, floating('7ff0000000000000'), unknown), 'true'),
    (conditional(true, integer(7), unknown), 'true'),
    (conditional(false, unknown, integer(0)), 'false'),
    (conditional(string('12tail'), 'ABSENT', unknown), 'true'),
    (conditional(string('0'), 'ABSENT', false), 'false'),
    (conditional(floating('3fe0000000000000'), 'ABSENT', unknown), 'true'),
]:
    checks.append(f'$lossy_optional_integer_condition(plenv_source, {expression}) = ({truth})')
# The four old200 changes are checked here without replaying those actors.
for expression, truth, integer_value in [
    (conditional(true, false, true), 'false', 0),
    (conditional(true, string('12tail'), unknown), 'true', 1),
]:
    converted = boolean(expression)
    checks.extend([
        f'$lossy_optional_integer_condition(plenv_source, {converted}) = ({truth})',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(converted)}) = ({integer_value})',
    ])
for expression in [
    conditional(unknown, true, true), conditional(unknown, true, false),
    conditional(true, unknown, false), conditional(false, true, unknown),
    conditional(floating('7ff8000000000000'), true, false),
    conditional(true, floating('7ff8000000000000'), false),
]:
    checks.append(f'$lossy_optional_integer_condition(plenv_source, {expression}) = eps')
checks.extend([
    f'~$lossy_optional_integer_boolean_shape({conditional(true, false, true)})',
    f'$lossy_optional_integer_default_in(plenv_source, {conditional(true, false, true)}) = eps',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(conditional(true, string("12tail"), unknown))}) = (12)',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(conditional(conditional(true, string("12tail"), unknown), "ABSENT", unknown))}) = (12)',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(conditional(true, integer(7), unknown))}) = (7)',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(conditional(true, floating("43e0000000000000"), integer(7)))}) = eps',
    f'~$lossy_optional_integer_ternary_shape({binary("Coalesce", integer(0), unknown)})',
    f'$lossy_optional_integer_condition(plenv_source, {binary("Coalesce", integer(0), unknown)}) = (false)',
    f'$lossy_optional_integer_condition(plenv_source, {binary("Coalesce", false, unknown)}) = eps',
    f'$lossy_optional_integer_condition(plenv_source, {boolean(binary("Coalesce", false, unknown))}) = eps',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(binary("Coalesce", false, unknown))}) = (0)',
    f'$lossy_optional_integer_condition(plenv_alias, {conditional(constant("true", qualified=True), string("00"), unknown)}) = (true)',
])
# A deeper finite condition checks the selected-branch recursion without new source credit.
deep = string('0')
for _ in range(24):
    deep = conditional(deep, true, false)
checks.append(f'$lossy_optional_integer_condition(plenv_source, {deep}) = (false)')
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
    '$lookup(psymboltable_global.ENV, $ptascii("xReceive201")) = (n_global)',
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
    '$lookup(S_done.ENV, $ptascii("gotReceive201")) = (n_got)',
    'S_done.STORE[n_got] = DEFINED (PINT 13)',
    r'$call_descriptors_valid(S_done) /\ $heap_valid($heap_graph(S_done))',
])

CASES = {'ternary-truth-default-omitted-tail': {
    'source': source,
    'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z]',
    'checks': checks,
}}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
