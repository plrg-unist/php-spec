#!/usr/bin/env python3
"""Explicit Boolean casts retain stored-default authority and omitted owners."""
import base64
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('boolean_cast_default_reception_cases.json')
SOURCES = {}
for row in json.loads(CATALOGUE.read_text()):
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
    SOURCES[row['id']] = row['source']

# Fresh first-VAL front preserves the whole five-default declaration; source0.
full = SOURCES['boolean-cast-precision-modes']
setup = full.index("set_error_handler('warningReceive200');")
start = full.index('$gotReceive200 = valueFirstReceive200(')
end = full.index('$xReceive200 = 1.5;', start)
source = full[:full.index('function referenceFirstReceive200')] + full[setup:end]
assert hashlib.sha256(source.encode()).hexdigest() == '4c34e2a45e21e917676211560d20a0201a5c15024ca36dcb08ac56cf3b98593a'

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
    add(node('NExprUnaryMinus', integer(7)), cast(boolean(string('0')))),
    add(node('NExprUnaryMinus', integer(12)), cast(boolean(string('00')))),
    add(integer(12), cast(boolean(node('NExprUnaryMinus', floating('3fe0000000000000'))))),
    conditional(boolean(node('NExprUnaryPlus', node('NExprUnaryMinus', floating('0000000000000000')))),
                constant('UnselectedReceive200'), cast(node('NExprUnaryMinus', floating('43e0000000000000')))),
    cast(conditional(boolean(node('NExprUnaryPlus', floating('7ff0000000000000'))),
                     string('999999999999999999999999'), constant('UnselectedReceive200'))),
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
    'expression_a = NExprBinaryOpPlus expression_negative_seven expression_cast_a metadata_a',
    'expression_cast_a = NExprCastInt expression_bool_a metadata_cast_a',
    'expression_bool_a = NExprCastBool expression_zero_string metadata_bool_a',
    '$lossy_optional_integer_boolean_shape(expression_bool_a)',
    '$lossy_optional_integer_condition(plenv_source, expression_bool_a) = (false)',
    '$lossy_optional_integer_default_in(plenv_source, expression_bool_a) = eps',
    'expression_c = NExprBinaryOpPlus expression_twelve expression_cast_c metadata_c',
    'expression_cast_c = NExprCastInt expression_bool_c metadata_cast_c',
    'expression_bool_c = NExprCastBool expression_negative_fraction metadata_bool_c',
    '$lossy_optional_integer_condition(plenv_source, expression_bool_c) = (true)',
    'expression_d = NExprTernary expression_bool_d expression_unknown_d expression_minimum_cast metadata_d',
    '$lossy_optional_integer_condition(plenv_source, expression_bool_d) = (false)',
    'expression_e = NExprCastInt expression_select_e metadata_e',
    'expression_select_e = NExprTernary expression_bool_e expression_string_e expression_unknown_e metadata_select_e',
    '$lossy_optional_integer_condition(plenv_source, expression_bool_e) = (true)',
    '$lossy_optional_integer_cast_leaf(plenv_source, expression_select_e) = (expression_string_e)',
    '$call_target(S, $ptascii("deferredFloatNotReceive200"), eps) = (pfunction_not)',
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
    'expression_same = NExprUnaryMinus (NScalarInt (INTEGER 7) metadata_a) metadata_a',
    '$lossy_optional_integer_default_in(plenv_source, expression_same) = ($(-7))',
    '~$lossy_optional_integer_tail(S, pfunction, [psparam_a[.DEFAULT = PSDEFAULT expression_same "int"]], 0)',
    'pfunction.DEFAULTS = [pdefault_a, pdefault_b, pdefault_c, pdefault_d, pdefault_e]',
    '~$lossy_optional_integer_tail(S, pfunction[.DEFAULTS = [pdefault_a, pdefault_b[.KIND = PDDEFERRED], pdefault_c, pdefault_d, pdefault_e]], [psparam_b], 1)',
    'S_wrong_value = S[.POOLS = [{UNIT n_unit, CONSTANTS ([(PCONSTANT (pcpath_b ++ [PCFIELD 6]) (PINT 11))])}]]',
    '$compiled_read(S_wrong_value, porigin_b) = (PINT 11)',
    '~$lossy_optional_integer_tail(S_wrong_value, pfunction, [psparam_b], 1)',
])
# Scalar truth is inherited without making a Boolean a direct integer default.
for value, truth in [
    (constant('null'), 'false'), (constant('false'), 'false'),
    (constant('true'), 'true'), (integer(0), 'false'), (integer(7), 'true'),
    (string(''), 'false'), (string('0'), 'false'), (string('00'), 'true'),
    (string('\0'), 'true'), (floating('8000000000000000'), 'false'),
    (floating('bfe0000000000000'), 'true'), (floating('43e0000000000000'), 'true'),
    (floating('7ff0000000000000'), 'true'),
]:
    converted = boolean(value)
    checks.extend([
        f'$lossy_optional_integer_condition(plenv_source, {converted}) = ({truth})',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(converted)}) = ({1 if truth == "true" else 0})',
    ])
checks.extend([
    f'$lossy_optional_integer_condition(plenv_source, {boolean(integer(1))}) = (true)',
    f'$lossy_optional_integer_default_in(plenv_source, {boolean(integer(1))}) = eps',
    f'$lossy_optional_integer_condition(plenv_source, {boolean(boolean(string("0")))}) = (false)',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(boolean(binary("BooleanAnd", string("00"), floating("3fe0000000000000"))))}) = (1)',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(node("NExprBooleanNot", boolean(floating("3fe0000000000000"))))}) = (0)',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(floating("7ff0000000000000"))}) = eps',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(floating("43e0000000000000"))}) = eps',
])
for value in [
    floating('7ff8000000000000'), floating('fff8000000000000'),
    constant('UnselectedReceive200'), binary('Concat', string('0'), string('0')),
    node('NExprArray', 'SEQUENCE eps'),
]:
    converted = boolean(value)
    checks.extend([
        f'$lossy_optional_integer_condition(plenv_source, {converted}) = eps',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(converted)}) = eps',
    ])
converted = boolean(conditional(constant('true'), constant('false'), constant('true')))
checks.extend([
    f'$lossy_optional_integer_condition(plenv_source, {converted}) = (false)',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(converted)}) = (0)',
])
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
    '$lookup(psymboltable_global.ENV, $ptascii("xReceive200")) = (n_global)',
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
    '$lookup(S_done.ENV, $ptascii("gotReceive200")) = (n_got)',
    'S_done.STORE[n_got] = DEFINED (PINT 13)',
    r'$call_descriptors_valid(S_done) /\ $heap_valid($heap_graph(S_done))',
])

CASES = {'boolean-cast-default-omitted-tail': {
    'source': source,
    'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z]',
    'checks': checks,
}}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
