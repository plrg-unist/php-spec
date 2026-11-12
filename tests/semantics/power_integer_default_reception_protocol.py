#!/usr/bin/env python3
"""Integer power defaults retain source authority and ordered omitted insertion."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('power_integer_default_reception_cases.json')
SOURCES = {}
for row in json.loads(CATALOGUE.read_text()):
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
    SOURCES[row['id']] = row['source']

checks = [
    r'n_bits = 4609434218613702656 /\ i = 1',
    '$function_at(S.FUNCTIONS, porigin) = (pfunction)',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_a, psparam_b, psparam_c, psparam_d, psparam_e]',
    r'~psparam_a.REQUIRED /\ ~psparam_a.BYREF /\ psparam_b.BYREF /\ psparam_d.BYREF /\ psparam_e.BYREF',
    'psparam_a.DEFAULT = PSDEFAULT expression_a "int"',
    'expression_a = NExprBinaryOpPlus (NExprUnaryMinus expression_a_power metadata_a_minus) (NScalarInt (INTEGER 1) metadata_a_one) metadata_a_sum',
    'expression_a_power = NExprBinaryOpPow (NExprBinaryOpPlus (NScalarInt (INTEGER 1) metadata_base_left) (NScalarInt (INTEGER 1) metadata_base_right) metadata_base_sum) (NScalarInt (INTEGER 3) metadata_three) metadata_a_power',
    '$psnumber(expression_a_power) = PSNONNUMERIC',
    '$lossy_optional_integer_default(expression_a_power) = (8)',
    '$lossy_optional_integer_default(expression_a) = ($(-7))',
    'psparam_b.DEFAULT = PSDEFAULT expression_b "int"',
    'expression_b = NExprBinaryOpPlus (NExprBinaryOpMinus expression_negative_power expression_square metadata_b_difference) expression_zero_power metadata_b_sum',
    'expression_negative_power = NExprBinaryOpPow (NExprUnaryMinus (NScalarInt (INTEGER 2) metadata_negative_two) metadata_negative) (NScalarInt (INTEGER 3) metadata_b_three) metadata_negative_power',
    'expression_square = NExprBinaryOpPow (NScalarInt (INTEGER 2) metadata_square_two) (NScalarInt (INTEGER 2) metadata_square_count) metadata_square',
    'expression_zero_power = NExprBinaryOpPow (NScalarInt (INTEGER 0) metadata_zero_base) (NScalarInt (INTEGER 0) metadata_zero_exponent) metadata_zero_power',
    r'$lossy_optional_integer_default(expression_negative_power) = ($(-8)) /\ $lossy_optional_integer_default(expression_square) = (4) /\ $lossy_optional_integer_default(expression_zero_power) = (1)',
    'psparam_c.DEFAULT = PSDEFAULT expression_c "int"',
    'expression_c = NExprBinaryOpPlus (NExprBinaryOpPlus expression_huge_power expression_nested_power metadata_c_prefix) expression_eight metadata_c_sum',
    'expression_huge_power = NExprBinaryOpPow (NScalarInt (INTEGER 1) metadata_huge_one) (NScalarInt (INTEGER 9223372036854775807) metadata_huge_exponent) metadata_huge_power',
    'expression_nested_power = NExprBinaryOpPow (NScalarInt (INTEGER 2) metadata_nested_two) (NExprBinaryOpPlus (NScalarInt (INTEGER 1) metadata_count_left) (NScalarInt (INTEGER 1) metadata_count_right) metadata_count_sum) metadata_nested_power',
    'expression_eight = NExprBinaryOpPow (NScalarInt (INTEGER 2) metadata_eight_two) (NScalarInt (INTEGER 3) metadata_eight_three) metadata_eight',
    r'$lossy_optional_integer_default(expression_huge_power) = (1) /\ $lossy_optional_integer_default(expression_nested_power) = (4) /\ $lossy_optional_integer_default(expression_eight) = (8)',
    'psparam_d.DEFAULT = PSDEFAULT expression_d "int"',
    'expression_d = NExprBinaryOpPow (NExprUnaryMinus (NScalarInt (INTEGER 2) metadata_min_two) metadata_min_minus) (NScalarInt (INTEGER 63) metadata_min_count) metadata_min_power',
    'psparam_e.DEFAULT = PSDEFAULT expression_e "int"',
    'expression_e = NExprBitwiseNot (NExprBinaryOpPow (NExprUnaryMinus (NScalarInt (INTEGER 2) metadata_max_two) metadata_max_minus) (NScalarInt (INTEGER 63) metadata_max_count) metadata_max_power) metadata_max_not',
]
for index, letter, integer in [
    (0, 'a', '$(-7)'), (1, 'b', '$(-11)'), (2, 'c', '13'),
    (3, 'd', '$(-9223372036854775808)'), (4, 'e', '9223372036854775807'),
]:
    checks.extend([
        f'$lossy_optional_integer_default(expression_{letter}) = ({integer})',
        f'$default_parameter_origin(S, porigin, {index}) = PORIGIN n_unit pcpath_{letter}',
        f'porigin_{letter} = PORIGIN n_unit (pcpath_{letter} ++ [PCFIELD 6])',
        f'$origin_node(S.SOURCES, porigin_{letter}) = (expression_{letter})',
        f'$default_at(pfunction.DEFAULTS, {index}) = ({{INDEX {index}, ORIGIN porigin_{letter}, KIND PDSTORED}})',
        f'$compiled_read(S, porigin_{letter}) = (PINT {integer})',
    ])
checks.extend([
    '$lossy_optional_integer_header(S, pfunction, pfunction.SIGNATURE.PARAMETERS, 0)',
    'expression_same = NExprUnaryMinus (NScalarInt (INTEGER 7) metadata_a_one) metadata_a_one',
    '$lossy_optional_integer_default(expression_same) = ($(-7))',
    '~$lossy_optional_integer_tail(S, pfunction, [psparam_a[.DEFAULT = PSDEFAULT expression_same "int"]], 0)',
    'S_wrong_value = S[.POOLS = [{UNIT n_unit, CONSTANTS ([(PCONSTANT (pcpath_a ++ [PCFIELD 6]) (PINT 7))])}]]',
    '$compiled_read(S_wrong_value, porigin_a) = (PINT 7)',
    '~$lossy_optional_integer_tail(S_wrong_value, pfunction, [psparam_a], 0)',
    '~$lossy_optional_integer_tail(S, pfunction, [psparam_a[.DEFAULT = PSDEFAULT expression_a "float"]], 0)',
    '$lossy_optional_integer_default(NExprBinaryOpPow expression_d (NScalarInt (INTEGER 0) metadata_a_one) metadata_a_one) = (1)',
    '$lossy_optional_integer_default(NExprBinaryOpPow expression_d (NScalarInt (INTEGER 1) metadata_a_one) metadata_a_one) = ($(-9223372036854775808))',
    '$lossy_optional_integer_default(NExprBinaryOpPow (NExprUnaryMinus (NScalarInt (INTEGER 1) metadata_a_one) metadata_a_one) (NScalarInt (INTEGER 9223372036854775807) metadata_a_one) metadata_a_one) = ($(-1))',
    'expression_over = NExprBinaryOpPow (NScalarInt (INTEGER 2) metadata_a_one) (NScalarInt (INTEGER 63) metadata_a_one) metadata_a_one',
    '$lossy_optional_integer_default(expression_over) = eps',
    '$lossy_optional_integer_default(NExprBinaryOpPow expression_d (NScalarInt (INTEGER 2) metadata_a_one) metadata_a_one) = eps',
    'expression_negative_exponent = NExprBinaryOpPow (NScalarInt (INTEGER 2) metadata_a_one) (NExprUnaryMinus (NScalarInt (INTEGER 1) metadata_a_one) metadata_a_one) metadata_a_one',
    '$lossy_optional_integer_default(expression_negative_exponent) = eps',
    '$lossy_optional_integer_default(NExprBinaryOpPow (NScalarInt (INTEGER 0) metadata_a_one) (NExprUnaryMinus (NScalarInt (INTEGER 1) metadata_a_one) metadata_a_one) metadata_a_one) = eps',
    '$lossy_optional_integer_default(NExprBinaryOpPow expression_over (NScalarInt (INTEGER 0) metadata_a_one) metadata_a_one) = eps',
    '$lossy_optional_integer_default(NExprBinaryOpPow (NExprConstFetch (NName (BYTES "Wg==") metadata_a_one) metadata_a_one) (NScalarInt (INTEGER 0) metadata_a_one) metadata_a_one) = eps',
    '$lossy_optional_integer_default(NExprBinaryOpPow (NScalarInt (INTEGER 0) metadata_a_one) (NExprConstFetch (NName (BYTES "Wg==") metadata_a_one) metadata_a_one) metadata_a_one) = eps',
    '$lossy_optional_integer_default(NExprBinaryOpPow (NScalarFloat (FLOAT "0000000000000000") metadata_a_one) (NScalarInt (INTEGER 0) metadata_a_one) metadata_a_one) = eps',
    '$lossy_optional_integer_default(NExprBinaryOpPow (NScalarInt (INTEGER 1) metadata_a_one) (NScalarFloat (FLOAT "0000000000000000") metadata_a_one) metadata_a_one) = eps',
    '$lossy_optional_integer_default(NExprBinaryOpPow (NScalarInt (INTEGER 9223372036854775808) metadata_a_one) (NScalarInt (INTEGER 0) metadata_a_one) metadata_a_one) = eps',
    '$lossy_optional_integer_default(NExprBinaryOpPow (NScalarInt (INTEGER 1) metadata_a_one) (NScalarInt (INTEGER 9223372036854775808) metadata_a_one) metadata_a_one) = eps',
    '$lossy_optional_integer_default(NExprBinaryOpMinus expression_over expression_over metadata_a_one) = eps',
    '$lossy_optional_integer_default(NExprBinaryOpMul expression_negative_exponent (NScalarInt (INTEGER 2) metadata_a_one) metadata_a_one) = eps',
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
    '$lookup(psymboltable_global.ENV, $ptascii("xReceive192")) = (n_global)',
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

CASES = {'power-default-omitted-tail': {
    'source': SOURCES['power-precision-modes'],
    'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z]',
    'checks': checks,
}}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE))
