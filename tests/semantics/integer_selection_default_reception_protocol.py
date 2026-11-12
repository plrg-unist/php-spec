#!/usr/bin/env python3
"""Integer selection defaults retain source authority and ordered omitted insertion."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('integer_selection_default_reception_cases.json')
SOURCES = {}
for row in json.loads(CATALOGUE.read_text()):
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
    SOURCES[row['id']] = row['source']

checks = [
    r'n_bits = 4609434218613702656 /\ i = 1',
    '$function_at(S.FUNCTIONS, porigin) = (pfunction)',
    'plenv_source = pfunction.ENV',
    'plenv_source.CONSTANTS = eps',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_a, psparam_b, psparam_c, psparam_d, psparam_e]',
    r'~psparam_a.REQUIRED /\ ~psparam_a.BYREF /\ psparam_b.BYREF /\ psparam_d.BYREF /\ psparam_e.BYREF',
    'psparam_a.DEFAULT = PSDEFAULT expression_a "int"',
    'expression_a = NExprTernary expression_a_condition expression_a_true expression_unknown metadata_a',
    'expression_a_condition = NExprConstFetch (NName (BYTES "VHJVZQ==") metadata_true_name) metadata_true',
    'expression_a_true = NExprUnaryMinus (NScalarInt (INTEGER 7) metadata_seven) metadata_negative_seven',
    'expression_unknown = NExprConstFetch (NName (BYTES "VW5zZWxlY3RlZFJlY2VpdmUxOTM=") metadata_unknown_name) metadata_unknown',
    '$lossy_optional_integer_special(plenv_source, expression_a_condition) = (PBOOL true)',
    '$lossy_optional_integer_condition(plenv_source, expression_a_condition) = (true)',
    '$lossy_optional_integer_default_in(plenv_source, expression_unknown) = eps',
    'psparam_b.DEFAULT = PSDEFAULT expression_b "int"',
    'expression_b = NExprTernary expression_null expression_unknown_b expression_shorthand metadata_b',
    'expression_null = NExprConstFetch (NName (BYTES "bnVsbA==") metadata_null_name) metadata_null',
    'expression_unknown_b = NExprConstFetch name_unknown_b metadata_unknown_b',
    'expression_shorthand = NExprTernary (NScalarInt (INTEGER 0) metadata_shorthand_zero) ABSENT (NExprUnaryMinus (NScalarInt (INTEGER 11) metadata_eleven) metadata_negative_eleven) metadata_shorthand',
    '$lossy_optional_integer_special(plenv_source, expression_null) = (PNULL)',
    '$lossy_optional_integer_condition(plenv_source, expression_null) = (false)',
    '$lossy_optional_integer_default_in(plenv_source, expression_shorthand) = ($(-11))',
    'psparam_c.DEFAULT = PSDEFAULT expression_c "int"',
    'expression_c = NExprTernary expression_coalesce_zero expression_unknown_c expression_coalesce_null metadata_c',
    'expression_coalesce_zero = NExprBinaryOpCoalesce (NScalarInt (INTEGER 0) metadata_coalesce_zero) expression_unknown_zero metadata_coalesce_zero_parent',
    'expression_coalesce_null = NExprBinaryOpCoalesce (NExprConstFetch (NName (BYTES "bnVsbA==") metadata_c_null_name) metadata_c_null) (NScalarInt (INTEGER 13) metadata_thirteen) metadata_coalesce_null',
    'expression_unknown_c = NExprConstFetch name_unknown_c metadata_unknown_c',
    'expression_unknown_zero = NExprConstFetch name_unknown_zero metadata_unknown_zero',
    '$lossy_optional_integer_default_in(plenv_source, expression_coalesce_zero) = (0)',
    '$lossy_optional_integer_condition(plenv_source, expression_coalesce_zero) = (false)',
    '$lossy_optional_integer_default_in(plenv_source, expression_coalesce_null) = (13)',
    'psparam_d.DEFAULT = PSDEFAULT expression_d "int"',
    'expression_d = NExprTernary expression_min ABSENT expression_unknown_d metadata_d',
    'expression_min = NExprBinaryOpPow (NExprUnaryMinus (NScalarInt (INTEGER 2) metadata_min_two) metadata_min_minus) (NScalarInt (INTEGER 63) metadata_min_count) metadata_min_power',
    'expression_unknown_d = NExprConstFetch name_unknown_d metadata_unknown_d',
    '$lossy_optional_integer_condition(plenv_source, expression_min) = (true)',
    'psparam_e.DEFAULT = PSDEFAULT expression_e "int"',
    'expression_e = NExprTernary expression_false expression_unknown_e (NExprBitwiseNot expression_max_min metadata_max_not) metadata_e',
    'expression_false = NExprConstFetch (NNameFullyQualified (BYTES "RmFMc0U=") metadata_false_name) metadata_false',
    'expression_max_min = NExprBinaryOpPow (NExprUnaryMinus (NScalarInt (INTEGER 2) metadata_max_two) metadata_max_minus) (NScalarInt (INTEGER 63) metadata_max_count) metadata_max_power',
    'expression_unknown_e = NExprConstFetch name_unknown_e metadata_unknown_e',
    '$lossy_optional_integer_special(plenv_source, expression_false) = (PBOOL false)',
    '$lossy_optional_integer_condition(plenv_source, expression_false) = (false)',
]
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
    ])
checks.extend([
    '$lossy_optional_integer_header(S, pfunction, pfunction.SIGNATURE.PARAMETERS, 0)',
    'expression_same = NExprTernary expression_a_condition expression_a_true (NScalarInt (INTEGER 99) metadata_seven) metadata_a',
    '$lossy_optional_integer_default_in(plenv_source, expression_same) = ($(-7))',
    '~$lossy_optional_integer_tail(S, pfunction, [psparam_a[.DEFAULT = PSDEFAULT expression_same "int"]], 0)',
    'S_wrong_value = S[.POOLS = [{UNIT n_unit, CONSTANTS ([(PCONSTANT (pcpath_a ++ [PCFIELD 6]) (PINT 7))])}]]',
    '$compiled_read(S_wrong_value, porigin_a) = (PINT 7)',
    '~$lossy_optional_integer_tail(S_wrong_value, pfunction, [psparam_a], 0)',
    '~$lossy_optional_integer_tail(S, pfunction, [psparam_a[.DEFAULT = PSDEFAULT expression_a "float"]], 0)',
    'expression_zero = NScalarInt (INTEGER 0) metadata_seven',
    'expression_one = NScalarInt (INTEGER 1) metadata_seven',
    '$lossy_optional_integer_condition(plenv_source, expression_zero) = (false)',
    '$lossy_optional_integer_condition(plenv_source, expression_a_true) = (true)',
    '$lossy_optional_integer_default_in(plenv_source, NExprTernary expression_zero ABSENT expression_one metadata_a) = (1)',
    '$lossy_optional_integer_default_in(plenv_source, NExprTernary expression_one ABSENT expression_unknown metadata_a) = (1)',
    '$lossy_optional_integer_default_in(plenv_source, NExprBinaryOpCoalesce expression_zero expression_unknown metadata_a) = (0)',
    '$lossy_optional_integer_default_in(plenv_source, NExprBinaryOpCoalesce expression_null expression_one metadata_a) = (1)',
    '$lossy_optional_integer_default_in(plenv_source, NExprBinaryOpCoalesce expression_false expression_one metadata_a) = eps',
    '$lossy_optional_integer_default_in(plenv_source, NExprTernary expression_false ABSENT expression_one metadata_a) = (1)',
    '$lossy_optional_integer_default_in(plenv_source, NExprTernary expression_null ABSENT expression_one metadata_a) = (1)',
    '$lossy_optional_integer_default_in(plenv_source, NExprTernary expression_a_condition ABSENT expression_one metadata_a) = eps',
    '$lossy_optional_integer_default_in(plenv_source, NExprTernary expression_unknown expression_one expression_one metadata_a) = eps',
    '$lossy_optional_integer_default_in(plenv_source, NExprTernary expression_a_condition expression_unknown expression_one metadata_a) = eps',
    '$lossy_optional_integer_default_in(plenv_source, NExprTernary expression_false expression_one expression_unknown metadata_a) = eps',
    '$lossy_optional_integer_default_in(plenv_source, NExprBinaryOpCoalesce expression_unknown expression_one metadata_a) = eps',
    '$lossy_optional_integer_default_in(plenv_source, NExprBinaryOpCoalesce expression_null expression_unknown metadata_a) = eps',
    'expression_over = NExprBinaryOpPow (NScalarInt (INTEGER 2) metadata_seven) (NScalarInt (INTEGER 63) metadata_seven) metadata_a',
    '$lossy_optional_integer_default_in(plenv_source, NExprTernary expression_a_condition expression_one expression_over metadata_a) = (1)',
    '$lossy_optional_integer_default_in(plenv_source, NExprTernary expression_a_condition expression_over expression_one metadata_a) = eps',
    '$lossy_optional_integer_default_in(plenv_source, NExprTernary expression_over expression_one expression_one metadata_a) = eps',
    '$lossy_optional_integer_default_in(plenv_source, NExprBinaryOpCoalesce expression_over expression_one metadata_a) = eps',
    '$lossy_optional_integer_special(plenv_source, NExprConstFetch (NNameFullyQualified (BYTES "TlVMTA==") metadata_seven) metadata_a) = (PNULL)',
    'plenv_relative = plenv_source[.NAMESPACE = $ptascii("Scope")]',
    '$lossy_optional_integer_special(plenv_relative, NExprConstFetch (NNameRelative (BYTES "bnVsbA==") metadata_seven) metadata_a) = eps',
    '$lossy_optional_integer_special(plenv_source, NExprConstFetch (NNameFullyQualified (BYTES "U2NvcGVcbnVsbA==") metadata_seven) metadata_a) = eps',
    '$lossy_optional_integer_special(plenv_source, NExprConstFetch (NName (BYTES "U2NvcGVcbnVsbA==") metadata_seven) metadata_a) = eps',
    '$lossy_optional_integer_condition(plenv_source, NExprConstFetch (NName (BYTES "UEhQX0lOVF9NQVg=") metadata_seven) metadata_a) = eps',
    '$lossy_optional_integer_condition(plenv_source, NScalarFloat (FLOAT "0000000000000000") metadata_seven) = eps',
    '$lossy_optional_integer_condition(plenv_source, NScalarString (BYTES "MA==") metadata_seven) = eps',
    '$lossy_optional_integer_condition(plenv_source, NScalarInt (INTEGER 9223372036854775808) metadata_seven) = eps',
    '$lossy_optional_integer_default_in(plenv_source, NExprTernary expression_a_condition expression_false expression_one metadata_a) = eps',
    '$lossy_optional_integer_default_in(plenv_source, NExprBinaryOpCoalesce (NScalarInt (INTEGER 9223372036854775808) metadata_seven) expression_one metadata_a) = eps',
    'plenv_alias = plenv_source[.CONSTANTS = [($ptascii("TrUe"), $ptascii("false")), ($ptascii("null"), $ptascii("true"))]]',
    'expression_alias_choice = NExprTernary expression_a_condition expression_a_true (NScalarInt (INTEGER 13) metadata_seven) metadata_a',
    '$lossy_optional_integer_default_in(plenv_source, expression_alias_choice) = ($(-7))',
    '$lossy_optional_integer_default_in(plenv_alias, expression_alias_choice) = (13)',
    '$lossy_optional_integer_special(plenv_alias, expression_a_condition) = (PBOOL false)',
    '$lossy_optional_integer_special(plenv_alias, expression_null) = (PBOOL true)',
    '$lossy_optional_integer_default_in(plenv_alias, expression_a) = eps',
    '$lossy_optional_integer_default_in(plenv_alias, expression_b) = eps',
    '~$lossy_optional_integer_header(S, pfunction[.ENV = plenv_alias], pfunction.SIGNATURE.PARAMETERS, 0)',
    '$lossy_optional_integer_default(NExprBinaryOpPow (NScalarInt (INTEGER 2) metadata_seven) (NScalarInt (INTEGER 3) metadata_seven) metadata_a) = (8)',
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
    '$lookup(psymboltable_global.ENV, $ptascii("xReceive193")) = (n_global)',
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

CASES = {'integer-selection-default-omitted-tail': {
    'source': SOURCES['integer-selection-precision-modes'],
    'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z]',
    'checks': checks,
}}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE))
