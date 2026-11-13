#!/usr/bin/env python3
"""Quiet scalar cast dispatch and exact omitted-default ownership."""
import base64
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('scalar_integer_cast_default_reception_cases.json')
SOURCES = {}
for row in json.loads(CATALOGUE.read_text()):
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
    SOURCES[row['id']] = row['source']

# Fresh first-VAL front preserves the whole five-default declaration; source0.
full = SOURCES['scalar-integer-cast-precision-modes']
setup = full.index("set_error_handler('warningReceive196');")
start = full.index('$gotReceive196 = valueFirstReceive196(')
end = full.index('$xReceive196 = 1.5;', start)
source = full[:full.index('function referenceFirstReceive196')] + full[setup:end]
assert hashlib.sha256(source.encode()).hexdigest() == 'cc838d6cf14f13f60145d1cc13c63a414924e3c538e11fb658623ae193ce252d'

metadata_index = 0
def node(constructor, *children):
    global metadata_index
    metadata_index += 1
    return constructor + ''.join(f' ({child})' for child in children) + f' metadata_case_{metadata_index}'


def integer(value):
    return node('NScalarInt', f'INTEGER {value}')


def constant(name, qualified=False):
    payload = base64.b64encode(name.encode()).decode()
    return node('NExprConstFetch', node('NNameFullyQualified' if qualified else 'NName', f'BYTES "{payload}"'))


def string(value):
    return node('NScalarString', f'BYTES "{base64.b64encode(value.encode()).decode()}"')


def cast(child):
    return node('NExprCastInt', child)


def add(left, right):
    return node('NExprBinaryOpPlus', left, right)


patterns = [
    cast(node('NExprUnaryMinus', node('NExprUnaryPlus', node('NScalarFloat', 'FLOAT "401f000000000000"')))),
    cast(string('-11tail')),
    add(add(add(add(cast(constant('TrUe')), cast(constant('FaLsE', True))), cast(constant('null'))),
            cast(string('12'))), cast(string('nonnumeric'))),
    cast(node('NExprBinaryOpPow', node('NExprUnaryMinus', integer(2)), integer(63))),
    cast(string('999999999999999999999999')),
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
checks.extend([
    '$lossy_optional_integer_header(S, pfunction, pfunction.SIGNATURE.PARAMETERS, 0)',
    'expression_a = NExprCastInt expression_signed metadata_a',
    'expression_signed = NExprUnaryMinus expression_positive metadata_negative',
    'expression_positive = NExprUnaryPlus expression_float metadata_positive',
    'expression_float = NScalarFloat (FLOAT "401f000000000000") metadata_float',
    '$lossy_optional_integer_float_literal(expression_float) = ($hex_bits("401f000000000000", 0))',
    '$lossy_optional_integer_float_literal(expression_positive) = ($hex_bits("401f000000000000", 0))',
    '$lossy_optional_integer_float_literal(expression_signed) = ($hex_bits("c01f000000000000", 0))',
    '$float_long($hex_bits("c01f000000000000", 0), false) = ($(-7), eps)',
    'expression_c = NExprBinaryOpPlus expression_c_twelve expression_cast_nonnumeric metadata_c',
    'expression_c_twelve = NExprBinaryOpPlus expression_c_null expression_cast_twelve metadata_c_twelve',
    'expression_c_null = NExprBinaryOpPlus expression_c_bool expression_cast_null metadata_c_null',
    'expression_c_bool = NExprBinaryOpPlus expression_cast_true expression_cast_false metadata_c_bool',
    '$lossy_optional_integer_default_in(plenv_source, expression_cast_true) = (1)',
    '$lossy_optional_integer_default_in(plenv_source, expression_cast_false) = (0)',
    '$lossy_optional_integer_default_in(plenv_source, expression_cast_null) = (0)',
    '$lossy_optional_integer_default_in(plenv_source, expression_cast_twelve) = (12)',
    '$lossy_optional_integer_default_in(plenv_source, expression_cast_nonnumeric) = (0)',
    'expression_d = NExprCastInt expression_min metadata_d',
    '$lossy_optional_integer_default_in(plenv_source, expression_min) = ($(-9223372036854775808))',
    '$lossy_optional_integer_float_literal(expression_min) = eps',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt expression_d metadata_a) = ($(-9223372036854775808))',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt expression_e metadata_a) = (9223372036854775807)',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt (NScalarInt (INTEGER 0) metadata_a) metadata_a) = (0)',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt (NExprBinaryOpSpaceship (NScalarInt (INTEGER 1) metadata_a) (NScalarInt (INTEGER 2) metadata_a) metadata_a) metadata_a) = ($(-1))',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt (NScalarFloat (FLOAT "3ff8000000000000") metadata_a) metadata_a) = (1)',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt (NExprUnaryMinus (NScalarFloat (FLOAT "3ff8000000000000") metadata_a) metadata_a) metadata_a) = ($(-1))',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt (NScalarFloat (FLOAT "8000000000000000") metadata_a) metadata_a) = (0)',
    '$lossy_optional_integer_default_in(plenv_source, expression_float) = eps',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt (NScalarInt (INTEGER 9223372036854775808) metadata_a) metadata_a) = eps',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt (NExprBinaryOpPow (NScalarInt (INTEGER 2) metadata_a) (NScalarInt (INTEGER 63) metadata_a) metadata_a) metadata_a) = eps',
])
for value, expected in [('', '0'), (' \t12', '12'), ('12.75', '12')]:
    payload = base64.b64encode(value.encode()).decode()
    checks.append(f'$lossy_optional_integer_default_in(plenv_source, NExprCastInt (NScalarString (BYTES "{payload}") metadata_a) metadata_a) = ({expected})')
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
    '$lookup(psymboltable_global.ENV, $ptascii("xReceive196")) = (n_global)',
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
])

CASES = {'scalar-cast-default-omitted-tail': {
    'source': source,
    'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z]',
    'checks': checks,
}}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
