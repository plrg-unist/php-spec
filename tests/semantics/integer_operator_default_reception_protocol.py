#!/usr/bin/env python3
"""Integer-only operator trees preserve exact default authority and ordered insertion."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('integer_operator_default_reception_cases.json')
SOURCES = {}
for row in json.loads(CATALOGUE.read_text()):
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
    SOURCES[row['id']] = row['source']

CASES = {
    'integer-operator-default-omitted-tail': {
        'source': SOURCES['integer-operator-precision-modes'],
        'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z]',
        'checks': [
            r'n_bits = 4609434218613702656 /\ i = 1',
            '$function_at(S.FUNCTIONS, porigin) = (pfunction)',
            'pfunction.SIGNATURE.PARAMETERS = [psparam_a, psparam_b, psparam_c, psparam_d, psparam_e]',
            r'~psparam_a.REQUIRED /\ ~psparam_a.BYREF /\ psparam_b.BYREF /\ psparam_d.BYREF /\ psparam_e.BYREF',
            'psparam_a.DEFAULT = PSDEFAULT expression_a "int"',
            'expression_a = NExprBitwiseNot (NExprBinaryOpShiftLeft (NScalarInt (INTEGER 3) metadata_three) (NScalarInt (INTEGER 1) metadata_one) metadata_shift) metadata_not',
            '$psnumber(expression_a) = PSNONNUMERIC',
            '$lossy_optional_integer_default(expression_a) = ($(-7))',
            'psparam_b.DEFAULT = PSDEFAULT expression_b "int"',
            'psparam_c.DEFAULT = PSDEFAULT expression_c "int"',
            r'$lossy_optional_integer_default(expression_b) = ($(-11)) /\ $lossy_optional_integer_default(expression_c) = (13)',
            '$default_parameter_origin(S, porigin, 0) = PORIGIN n_unit pcpath_parameter',
            'pcpath_default = pcpath_parameter ++ [PCFIELD 6]',
            'porigin_default = PORIGIN n_unit pcpath_default',
            '$origin_node(S.SOURCES, porigin_default) = (expression_a)',
            '$default_at(pfunction.DEFAULTS, 0) = ({INDEX 0, ORIGIN porigin_default, KIND PDSTORED})',
            '$compiled_read(S, porigin_default) = (PINT $(-7))',
            'psparam_d.DEFAULT = PSDEFAULT expression_d "int"',
            'psparam_e.DEFAULT = PSDEFAULT expression_e "int"',
            r'$lossy_optional_integer_default(expression_d) = ($(-9223372036854775808)) /\ $lossy_optional_integer_default(expression_e) = (9223372036854775807)',
            '$default_parameter_origin(S, porigin, 3) = PORIGIN n_unit pcpath_d',
            '$default_parameter_origin(S, porigin, 4) = PORIGIN n_unit pcpath_e',
            'porigin_d = PORIGIN n_unit (pcpath_d ++ [PCFIELD 6])',
            'porigin_e = PORIGIN n_unit (pcpath_e ++ [PCFIELD 6])',
            r'$origin_node(S.SOURCES, porigin_d) = (expression_d) /\ $origin_node(S.SOURCES, porigin_e) = (expression_e)',
            r'$compiled_read(S, porigin_d) = (PINT $(-9223372036854775808)) /\ $compiled_read(S, porigin_e) = (PINT 9223372036854775807)',
            '$lossy_optional_integer_header(S, pfunction, pfunction.SIGNATURE.PARAMETERS, 0)',
            'expression_same = NExprUnaryMinus (NScalarInt (INTEGER 7) metadata_one) metadata_one',
            '$lossy_optional_integer_default(expression_same) = ($(-7))',
            '~$lossy_optional_integer_tail(S, pfunction, [psparam_a[.DEFAULT = PSDEFAULT expression_same "int"]], 0)',
            'S_wrong_value = S[.POOLS = [{UNIT n_unit, CONSTANTS ([(PCONSTANT pcpath_default (PINT 7))])}]]',
            '$compiled_read(S_wrong_value, porigin_default) = (PINT 7)',
            '~$lossy_optional_integer_tail(S_wrong_value, pfunction, [psparam_a], 0)',
            '~$lossy_optional_integer_tail(S, pfunction, [psparam_a[.DEFAULT = PSDEFAULT expression_a "float"]], 0)',
            '$lossy_optional_integer_default(NExprBinaryOpMod (NScalarInt (INTEGER 12) metadata_one) (NScalarInt (INTEGER 3) metadata_one) metadata_one) = (0)',
            '$lossy_optional_integer_default(NExprBinaryOpMod (NExprUnaryMinus (NScalarInt (INTEGER 35) metadata_one) metadata_one) (NScalarInt (INTEGER 21) metadata_one) metadata_one) = ($(-14))',
            '$lossy_optional_integer_default(NExprBinaryOpMod (NScalarInt (INTEGER 35) metadata_one) (NExprUnaryMinus (NScalarInt (INTEGER 21) metadata_one) metadata_one) metadata_one) = (14)',
            '$lossy_optional_integer_default(NExprBinaryOpMod expression_d (NExprUnaryMinus (NScalarInt (INTEGER 1) metadata_one) metadata_one) metadata_one) = (0)',
            '$lossy_optional_integer_default(NExprBinaryOpMod (NScalarInt (INTEGER 12) metadata_one) (NScalarInt (INTEGER 0) metadata_one) metadata_one) = eps',
            '$lossy_optional_integer_default(NExprBinaryOpShiftLeft (NScalarInt (INTEGER 1) metadata_one) (NScalarInt (INTEGER 63) metadata_one) metadata_one) = ($(-9223372036854775808))',
            '$lossy_optional_integer_default(NExprBinaryOpShiftLeft (NScalarInt (INTEGER 9223372036854775807) metadata_one) (NScalarInt (INTEGER 1) metadata_one) metadata_one) = ($(-2))',
            '$lossy_optional_integer_default(NExprBinaryOpShiftLeft (NScalarInt (INTEGER 1) metadata_one) (NScalarInt (INTEGER 64) metadata_one) metadata_one) = (0)',
            '$lossy_optional_integer_default(NExprBinaryOpShiftLeft (NScalarInt (INTEGER 1) metadata_one) (NScalarInt (INTEGER 9223372036854775807) metadata_one) metadata_one) = (0)',
            '$lossy_optional_integer_default(NExprBinaryOpShiftRight (NExprUnaryMinus (NScalarInt (INTEGER 3) metadata_one) metadata_one) (NScalarInt (INTEGER 1) metadata_one) metadata_one) = ($(-2))',
            '$lossy_optional_integer_default(NExprBinaryOpShiftRight (NExprUnaryMinus (NScalarInt (INTEGER 3) metadata_one) metadata_one) (NScalarInt (INTEGER 64) metadata_one) metadata_one) = ($(-1))',
            '$lossy_optional_integer_default(NExprBinaryOpShiftRight (NScalarInt (INTEGER 3) metadata_one) (NScalarInt (INTEGER 64) metadata_one) metadata_one) = (0)',
            '$lossy_optional_integer_default(NExprBinaryOpShiftLeft (NScalarInt (INTEGER 1) metadata_one) (NExprUnaryMinus (NScalarInt (INTEGER 1) metadata_one) metadata_one) metadata_one) = eps',
            '$lossy_optional_integer_default(NExprBinaryOpShiftRight (NScalarInt (INTEGER 1) metadata_one) (NExprUnaryMinus (NScalarInt (INTEGER 1) metadata_one) metadata_one) metadata_one) = eps',
            '$lossy_optional_integer_default(NExprBinaryOpBitwiseAnd (NScalarInt (INTEGER 11) metadata_one) (NScalarInt (INTEGER 6) metadata_one) metadata_one) = (2)',
            '$lossy_optional_integer_default(NExprBinaryOpBitwiseOr (NScalarInt (INTEGER 11) metadata_one) (NScalarInt (INTEGER 6) metadata_one) metadata_one) = (15)',
            '$lossy_optional_integer_default(NExprBinaryOpBitwiseXor (NScalarInt (INTEGER 11) metadata_one) (NScalarInt (INTEGER 6) metadata_one) metadata_one) = (13)',
            '$lossy_optional_integer_default(NExprBitwiseNot (NScalarInt (INTEGER 0) metadata_one) metadata_one) = ($(-1))',
            '$lossy_optional_integer_default(NExprBitwiseNot expression_d metadata_one) = (9223372036854775807)',
            '$lossy_optional_integer_default(NExprBitwiseNot (NScalarInt (INTEGER 9223372036854775807) metadata_one) metadata_one) = ($(-9223372036854775808))',
            '$lossy_optional_integer_default(NExprBinaryOpShiftLeft (NScalarInt (INTEGER 9223372036854775808) metadata_one) (NScalarInt (INTEGER 0) metadata_one) metadata_one) = eps',
            '$lossy_optional_integer_default(NExprBinaryOpBitwiseAnd (NScalarInt (INTEGER 9223372036854775808) metadata_one) (NScalarInt (INTEGER 0) metadata_one) metadata_one) = eps',
            '$lossy_optional_integer_default(NExprBinaryOpMod (NScalarInt (INTEGER 9223372036854775808) metadata_one) (NScalarInt (INTEGER 1) metadata_one) metadata_one) = eps',
            '$lossy_optional_integer_default(NScalarInt (INTEGER 9223372036854775808) metadata_one) = (9223372036854775808)',
            'expression_over = NExprBinaryOpPlus (NScalarInt (INTEGER 9223372036854775807) metadata_one) (NScalarInt (INTEGER 1) metadata_one) metadata_one',
            '$lossy_optional_integer_default(NExprBinaryOpBitwiseAnd (NScalarInt (INTEGER 0) metadata_one) expression_over metadata_one) = eps',
            '$lossy_optional_integer_default(NExprBinaryOpMod expression_over (NScalarInt (INTEGER 2) metadata_one) metadata_one) = eps',
            '$lossy_optional_integer_default(NExprBinaryOpBitwiseAnd (NScalarInt (INTEGER 0) metadata_one) (NExprConstFetch (NName (BYTES "Wg==") metadata_one) metadata_one) metadata_one) = eps',
            '$lossy_optional_integer_default(NExprBinaryOpMod (NScalarFloat (FLOAT "3ff8000000000000") metadata_one) (NScalarInt (INTEGER 2) metadata_one) metadata_one) = eps',
            '$lossy_optional_integer_default(NExprBinaryOpBitwiseXor (NScalarInt (INTEGER 0) metadata_one) (NScalarFloat (FLOAT "3ff8000000000000") metadata_one) metadata_one) = eps',
            '$lossy_optional_integer_default(NExprBitwiseNot (NScalarFloat (FLOAT "0000000000000000") metadata_one) metadata_one) = eps',
            '$lossy_optional_integer_default(NExprBinaryOpPow (NScalarInt (INTEGER 2) metadata_one) (NScalarInt (INTEGER 3) metadata_one) metadata_one) = eps',
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
            '$lookup(psymboltable_global.ENV, $ptascii("xReceive191")) = (n_global)',
            'S.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
            'PhpStep: S ~> S_after_0',
            r'S_after_0.TODO = [TYPE_RECEIVE porigin 1] /\ S_after_0.STORE[n_cell] = DEFINED (PINT 1)',
        ],
    },
}

# All four omitted defaults take their real TYPE_RECEIVE and DEFAULT_RECEIVE.
checks = CASES['integer-operator-default-omitted-tail']['checks']
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

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE))
