#!/usr/bin/env python3
"""Binary default roots preserve exact values, source syntax and receive order."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('binary_integer_default_reception_cases.json')
SOURCES = {}
for row in json.loads(CATALOGUE.read_text()):
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
    SOURCES[row['id']] = row['source']

# Retain fresh setup and the final opposite-mode call, omitting all earlier
# invocations and their histories. This selected source has source credit0.
opposite = SOURCES['binary-precision-modes']
setup_end = opposite.index('$xReceive187 = 1.5;\n$countReceive187 = 0;\n')
selected = opposite.index('$xReceive187 = 1.5;\n$countReceive187 = 0;\n$gotReceive187 = referenceFirstReceive187(')
opposite = opposite[:setup_end] + opposite[selected:]
assert hashlib.sha256(opposite.encode()).hexdigest() == '5ffbdd895c68de4801aa1499208eba6e4bca2c43856115a634a12ded4f45ea5d'

CASES = {
    'binary-integer-default-omitted-tail': {
        'source': SOURCES['binary-precision-modes'],
        'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z]',
        'checks': [
            r'n_bits = 4609434218613702656 /\ i = 1',
            '$function_at(S.FUNCTIONS, porigin) = (pfunction)',
            'pfunction.SIGNATURE.PARAMETERS = [psparam_a, psparam_b, psparam_c, psparam_d, psparam_e]',
            r'~psparam_a.REQUIRED /\ ~psparam_a.BYREF /\ psparam_b.BYREF /\ psparam_d.BYREF /\ psparam_e.BYREF',
            'psparam_a.DEFAULT = PSDEFAULT expression_a "int"',
            'expression_a = NExprBinaryOpPlus (NExprUnaryMinus (NScalarInt (INTEGER 3) metadata_left_int) metadata_left) (NExprUnaryMinus (NScalarInt (INTEGER 4) metadata_right_int) metadata_right) metadata_plus',
            '$psnumber(expression_a) = PSNONNUMERIC',
            '$lossy_optional_integer_default(expression_a) = ($(-7))',
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
            'expression_same = NExprUnaryMinus (NScalarInt (INTEGER 7) metadata_left_int) metadata_left',
            '$lossy_optional_integer_default(expression_same) = ($(-7))',
            '~$lossy_optional_integer_tail(S, pfunction, [psparam_a[.DEFAULT = PSDEFAULT expression_same "int"]], 0)',
            'S_wrong_value = S[.POOLS = [{UNIT n_unit, CONSTANTS ([(PCONSTANT pcpath_default (PINT 7))])}]]',
            '$compiled_read(S_wrong_value, porigin_default) = (PINT 7)',
            '~$lossy_optional_integer_tail(S_wrong_value, pfunction, [psparam_a], 0)',
            '$lossy_optional_integer_default(NScalarInt (INTEGER 7) metadata_left_int) = (7)',
            '$lossy_optional_integer_default(NExprBinaryOpPlus (NScalarInt (INTEGER 9223372036854775807) metadata_left_int) (NScalarInt (INTEGER 1) metadata_right_int) metadata_plus) = eps',
            '$lossy_optional_integer_default(NExprBinaryOpMinus (NExprUnaryMinus (NScalarInt (INTEGER 9223372036854775807) metadata_left_int) metadata_left) (NScalarInt (INTEGER 2) metadata_right_int) metadata_plus) = eps',
            '$lossy_optional_integer_default(NExprBinaryOpPlus expression_a (NScalarInt (INTEGER 1) metadata_right_int) metadata_plus) = ($(-6))',
            '$lossy_optional_integer_default(NExprUnaryPlus expression_a metadata_plus) = ($(-7))',
            '$lossy_optional_integer_default(NExprBinaryOpMul (NScalarInt (INTEGER 3) metadata_left_int) (NScalarInt (INTEGER 4) metadata_right_int) metadata_plus) = (12)',
            '$lossy_optional_integer_default(NExprBinaryOpPlus (NScalarFloat (FLOAT "3ff8000000000000") metadata_left_int) (NScalarInt (INTEGER 1) metadata_right_int) metadata_plus) = eps',
            '$lossy_optional_integer_default(NExprConstFetch (NName (BYTES "Wg==") metadata_left_int) metadata_plus) = eps',
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
            '$lookup(psymboltable_global.ENV, $ptascii("xReceive187")) = (n_global)',
            'S.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
            'PhpStep: S ~> S_after_0',
            r'S_after_0.TODO = [TYPE_RECEIVE porigin 1] /\ S_after_0.STORE[n_cell] = DEFINED (PINT 1)',
        ],
    },
    'binary-integer-default-opposite-modes': {
        'source': opposite,
        'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 2 n_cell n_bits i z]',
        'checks': [
            r'n_bits = 4609434218613702656 /\ i = 1',
            '$function_at(S.FUNCTIONS, porigin) = (pfunction)',
            'pfunction.SIGNATURE.PARAMETERS = [psparam_a, psparam_b, psparam_c, psparam_d, psparam_e]',
            r'psparam_a.BYREF /\ ~psparam_b.BYREF /\ ~psparam_c.BYREF /\ ~psparam_d.BYREF /\ ~psparam_e.BYREF',
            '$lossy_optional_integer_header(S, pfunction, pfunction.SIGNATURE.PARAMETERS, 0)',
            'S.CURRENT = (pcallcontext)',
            r'pcallcontext.ARGC = 3 /\ pcallcontext.HOLES = [1]',
            '$lookup(S.ENV, psparam_a.NAME) = (n_a)',
            '$lookup(S.ENV, psparam_b.NAME) = (n_b)',
            '$lookup(S.ENV, psparam_c.NAME) = (n_cell)',
            r'$lookup(S.ENV, psparam_d.NAME) = eps /\ $lookup(S.ENV, psparam_e.NAME) = eps',
            r'S.STORE[n_a] = DEFINED (PFLOAT 4616752568008179712) /\ n_a <- S.REFCELLS /\ $heap_owners($heap_graph(S), HCELL n_a) = 2',
            r'S.STORE[n_b] = DEFINED (PINT $(-11)) /\ ~(n_b <- S.REFCELLS) /\ $heap_owners($heap_graph(S), HCELL n_b) = 1',
            r'S.STORE[n_cell] = DEFINED (PFLOAT n_bits) /\ ~(n_cell <- S.REFCELLS) /\ $heap_owners($heap_graph(S), HCELL n_cell) = 1',
            '$lossy_mixed_parameter_source_valid(S, LOSSY_MIXED_PARAMETER_RECEIVE porigin 2 n_cell n_bits i z)',
            '$lossy_mixed_parameter_ready(S, 2, n_cell, n_bits)',
            '$lossy_parameter_ready(S, n_cell, n_bits)',
            '$task_nodes(LOSSY_MIXED_PARAMETER_RECEIVE porigin 2 n_cell n_bits i z) = eps',
            'PhpStep: S ~> S_after_2',
            r'S_after_2.TODO = [TYPE_RECEIVE porigin 3] /\ S_after_2.STORE[n_cell] = DEFINED (PINT 1)',
        ],
    },
}

# Each remaining formal takes its actual TYPE_RECEIVE then DEFAULT_RECEIVE.
for name, defaults in [
    ('binary-integer-default-omitted-tail', [(1, 'b', '$(-11)'), (2, 'c', '13'), (3, 'd', '$(-9223372036854775808)'), (4, 'e', '9223372036854775807')]),
    ('binary-integer-default-opposite-modes', [(3, 'd', '$(-9223372036854775808)'), (4, 'e', '9223372036854775807')]),
]:
    checks = CASES[name]['checks']
    for index, letter, integer in defaults:
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
        '$call_descriptors_valid(S_after_4) /\\ $heap_valid($heap_graph(S_after_4))',
    ])

CASES['binary-integer-default-omitted-tail']['checks'].append(
    'S_after_4.STORE[n_global] = S.STORE[n_global] /\\ S_after_4.STORE[n_cell] = DEFINED (PINT 1)')
CASES['binary-integer-default-opposite-modes']['checks'].append(
    'S_after_4.STORE[n_a] = S.STORE[n_a] /\\ S_after_4.STORE[n_b] = S.STORE[n_b] /\\ S_after_4.STORE[n_cell] = DEFINED (PINT 1)')

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE))
