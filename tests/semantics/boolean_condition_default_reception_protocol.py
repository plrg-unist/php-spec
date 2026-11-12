#!/usr/bin/env python3
"""Boolean condition defaults preserve indexed source authority and omitted cells."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('boolean_condition_default_reception_cases.json')
SOURCES = {}
for row in json.loads(CATALOGUE.read_text()):
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
    SOURCES[row['id']] = row['source']

checks = [
    r'n_bits = 4609434218613702656 /\ i = 1',
    '$function_at(S.FUNCTIONS, porigin) = (pfunction)',
    'plenv_source = pfunction.ENV',
    r'plenv_source.NAMESPACE = eps /\ plenv_source.CONSTANTS = eps',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_a, psparam_b, psparam_c, psparam_d, psparam_e]',
    r'~psparam_a.REQUIRED /\ ~psparam_a.BYREF /\ psparam_b.BYREF /\ psparam_d.BYREF /\ psparam_e.BYREF',
]
for letter in 'abcde':
    checks.extend([
        f'psparam_{letter}.DEFAULT = PSDEFAULT expression_{letter} "int"',
        f'expression_{letter} = NExprTernary expression_condition_{letter} phpType5_{letter} expression_false_{letter} metadata_{letter}',
    ])
checks.extend([
    'expression_condition_a = NExprBinaryOpBooleanAnd (NExprBooleanNot (NScalarInt (INTEGER 0) metadata_zero_a) metadata_not_a) expression_true metadata_and_a',
    'expression_true = NExprConstFetch (NName (BYTES "VHJVZQ==") metadata_true_name) metadata_true',
    'expression_false_a = NExprConstFetch name_unknown metadata_unknown',
    'expression_condition_b = NExprBinaryOpBooleanOr expression_and_b expression_or_b metadata_or_b',
    'expression_and_b = NExprBinaryOpLogicalAnd expression_null expression_unknown_b metadata_and_b',
    'expression_null = NExprConstFetch (NName (BYTES "bnVsbA==") metadata_null_name) metadata_null',
    'expression_or_b = NExprBinaryOpLogicalOr (NExprBooleanNot expression_false metadata_not_b) expression_unknown_or_b metadata_logical_or_b',
    'expression_false = NExprConstFetch (NName (BYTES "ZmFsc2U=") metadata_false_name) metadata_false',
    'expression_condition_c = NExprBinaryOpLogicalXor expression_xor_c expression_or_c metadata_xor_c',
    'expression_xor_c = NExprBinaryOpLogicalXor expression_negative_three expression_null_c metadata_xor_left',
    'expression_negative_three = NExprUnaryMinus (NScalarInt (INTEGER 3) metadata_three) metadata_negative_three',
    'expression_or_c = NExprBinaryOpBooleanOr expression_bool_false_c (NScalarInt (INTEGER 0) metadata_zero_c) metadata_or_c',
    'expression_condition_d = NExprBinaryOpBooleanAnd (NScalarInt (INTEGER 0) metadata_zero_d) expression_unknown_d metadata_and_d',
    'expression_condition_e = NExprBinaryOpBooleanAnd expression_or_e (NExprBooleanNot expression_and_e metadata_not_e) metadata_and_parent_e',
    'expression_or_e = NExprBinaryOpLogicalOr expression_true_e expression_unknown_e metadata_or_e',
    'expression_and_e = NExprBinaryOpLogicalAnd (NScalarInt (INTEGER 0) metadata_zero_e) expression_false_and_e metadata_and_e',
    '$lossy_optional_integer_condition(plenv_source, expression_condition_a) = (true)',
    '$lossy_optional_integer_condition(plenv_source, expression_condition_b) = (true)',
    '$lossy_optional_integer_condition(plenv_source, expression_condition_c) = (true)',
    '$lossy_optional_integer_condition(plenv_source, expression_condition_d) = (false)',
    '$lossy_optional_integer_condition(plenv_source, expression_condition_e) = (true)',
])
for index, letter, integer in [
    (0, 'a', '$(-7)'), (1, 'b', '$(-11)'), (2, 'c', '13'),
    (3, 'd', '$(-9223372036854775808)'), (4, 'e', '9223372036854775807'),
]:
    checks.extend([
        f'$lossy_optional_integer_default_in(plenv_source, expression_{letter}) = ({integer})',
        f'$default_parameter_origin(S, porigin, {index}) = PORIGIN n_unit pcpath_{letter}',
        f'porigin_{letter} = PORIGIN n_unit (pcpath_{letter} ++ [PCFIELD 6])',
        f'$origin_node(S.SOURCES, porigin_{letter}) = (expression_{letter})',
        f'$default_at(pfunction.DEFAULTS, {index}) = ({{INDEX {index}, ORIGIN porigin_{letter}, KIND PDSTORED}})',
        f'$compiled_read(S, porigin_{letter}) = (PINT {integer})',
        f'$lossy_optional_integer_default_in(plenv_source, expression_condition_{letter}) = eps',
    ])
checks.extend([
    '$lossy_optional_integer_header(S, pfunction, pfunction.SIGNATURE.PARAMETERS, 0)',
    'expression_same = NExprTernary expression_condition_a phpType5_a (NScalarInt (INTEGER 99) metadata_a) metadata_a',
    '$lossy_optional_integer_default_in(plenv_source, expression_same) = ($(-7))',
    '~$lossy_optional_integer_tail(S, pfunction, [psparam_a[.DEFAULT = PSDEFAULT expression_same "int"]], 0)',
    'S_wrong_value = S[.POOLS = [{UNIT n_unit, CONSTANTS ([(PCONSTANT (pcpath_a ++ [PCFIELD 6]) (PINT 7))])}]]',
    '$compiled_read(S_wrong_value, porigin_a) = (PINT 7)',
    '~$lossy_optional_integer_tail(S_wrong_value, pfunction, [psparam_a], 0)',
    'expression_zero = NScalarInt (INTEGER 0) metadata_a',
    'expression_one = NScalarInt (INTEGER 1) metadata_a',
    '$lossy_optional_integer_condition(plenv_source, NExprBooleanNot expression_false_a metadata_a) = eps',
])
for constructor, decisive, reached, result in [
    ('NExprBinaryOpBooleanAnd', 'expression_zero', 'expression_one', 'false'),
    ('NExprBinaryOpLogicalAnd', 'expression_zero', 'expression_one', 'false'),
    ('NExprBinaryOpBooleanOr', 'expression_one', 'expression_zero', 'true'),
    ('NExprBinaryOpLogicalOr', 'expression_one', 'expression_zero', 'true'),
]:
    checks.extend([
        f'$lossy_optional_integer_condition(plenv_source, {constructor} {decisive} expression_false_a metadata_a) = ({result})',
        f'$lossy_optional_integer_condition(plenv_source, {constructor} {reached} expression_zero metadata_a) = (false)',
        f'$lossy_optional_integer_condition(plenv_source, {constructor} {reached} expression_one metadata_a) = (true)',
        f'$lossy_optional_integer_condition(plenv_source, {constructor} {reached} expression_false_a metadata_a) = eps',
        f'$lossy_optional_integer_condition(plenv_source, {constructor} expression_false_a {decisive} metadata_a) = eps',
    ])
checks.extend([
    '$lossy_optional_integer_condition(plenv_source, NExprBooleanNot expression_zero metadata_a) = (true)',
    '$lossy_optional_integer_condition(plenv_source, NExprBooleanNot expression_one metadata_a) = (false)',
    '$lossy_optional_integer_condition(plenv_source, NExprBinaryOpLogicalXor expression_one expression_one metadata_a) = (false)',
    '$lossy_optional_integer_condition(plenv_source, NExprBinaryOpLogicalXor expression_one expression_zero metadata_a) = (true)',
    '$lossy_optional_integer_condition(plenv_source, NExprBinaryOpLogicalXor expression_zero expression_zero metadata_a) = (false)',
    '$lossy_optional_integer_condition(plenv_source, NExprBinaryOpLogicalXor expression_one expression_false_a metadata_a) = eps',
    '$lossy_optional_integer_condition(plenv_source, NExprBinaryOpLogicalXor expression_false_a expression_one metadata_a) = eps',
    '$lossy_optional_integer_default_in(plenv_source, NExprBooleanNot expression_zero metadata_a) = eps',
    '$lossy_optional_integer_default_in(plenv_source, NExprTernary expression_condition_a ABSENT expression_one metadata_a) = eps',
    '$lossy_optional_integer_default_in(plenv_source, NExprTernary expression_condition_d ABSENT expression_one metadata_a) = (1)',
    '$lossy_optional_integer_default_in(plenv_source, NExprBinaryOpCoalesce expression_condition_a expression_one metadata_a) = eps',
    '$lossy_optional_integer_default_in(plenv_source, NExprTernary expression_condition_a expression_true expression_one metadata_a) = eps',
    'expression_over = NExprBinaryOpPow (NScalarInt (INTEGER 2) metadata_a) (NScalarInt (INTEGER 63) metadata_a) metadata_a',
    '$lossy_optional_integer_condition(plenv_source, NExprBooleanNot expression_over metadata_a) = eps',
    '$lossy_optional_integer_condition(plenv_source, NExprBinaryOpBooleanAnd expression_one expression_over metadata_a) = eps',
    'plenv_alias = plenv_source[.CONSTANTS = [($ptascii("TrUe"), $ptascii("false")), ($ptascii("null"), $ptascii("true"))]]',
    '$lossy_optional_integer_condition(plenv_alias, expression_condition_a) = (false)',
    '$lossy_optional_integer_default_in(plenv_alias, expression_a) = eps',
    '~$lossy_optional_integer_header(S, pfunction[.ENV = plenv_alias], pfunction.SIGNATURE.PARAMETERS, 0)',
    '$lossy_optional_integer_condition(plenv_source, NExprBooleanNot expression_true metadata_a) = (false)',
    '$lossy_optional_integer_condition(plenv_alias, NExprBooleanNot expression_true metadata_a) = (true)',
    '$lossy_optional_integer_condition(plenv_alias, NExprBooleanNot (NExprConstFetch (NNameFullyQualified (BYTES "VHJVZQ==") metadata_true_name) metadata_true) metadata_a) = (false)',
])
for constructor, rhs in [
    ('NExprBinaryOpBooleanAnd', 'expression_one'),
    ('NExprBinaryOpLogicalAnd', 'expression_one'),
    ('NExprBinaryOpBooleanOr', 'expression_zero'),
    ('NExprBinaryOpLogicalOr', 'expression_zero'),
    ('NExprBinaryOpLogicalXor', 'expression_zero'),
]:
    checks.extend([
        f'$lossy_optional_integer_condition(plenv_source, {constructor} expression_true {rhs} metadata_a) = (true)',
        f'$lossy_optional_integer_condition(plenv_alias, {constructor} expression_true {rhs} metadata_a) = (false)',
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
    '$lookup(psymboltable_global.ENV, $ptascii("xReceive194")) = (n_global)',
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

CASES = {'boolean-condition-default-omitted-tail': {
    'source': SOURCES['boolean-condition-precision-modes'],
    'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z]',
    'checks': checks,
}}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE))
