#!/usr/bin/env python3
"""Integer operator provenance, supplied authority and omitted-reference cells."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('integer_operator_default_reception_cases.json')
SOURCES = {}
for row in json.loads(CATALOGUE.read_text()):
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
    SOURCES[row['id']] = row['source']

# Keep fresh setup and only the leading REF call; the removed calls and their
# histories have no source credit in this independently derived fixture.
source = SOURCES['integer-operator-precision-modes']
start = source.index('$gotReceive191 = referenceReceive191(')
end = source.index('$xReceive191 = 1.5;', start)
leading = source[:source.index('$gotReceive191 = valueFirstReceive191(')] + source[start:end]
assert hashlib.sha256(leading.encode()).hexdigest() == '9fa8bd0ac69e831c2420b9becaaacf6d0513c4bd8bee2be9a142d6a3afa5f2e0'

CASES = {
    'integer-operator-default-reference-leading': {
        'source': leading,
        'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 2 n_cell n_bits i z]',
        'checks': [
            r'n_bits = 4609434218613702656 /\ i = 1',
            '$function_at(S.FUNCTIONS, porigin) = (pfunction)',
            'pfunction.SIGNATURE.PARAMETERS = [psparam_a, psparam_b, psparam_c, psparam_d, psparam_e]',
            r'$lossy_optional_integer_mode(pfunction.SIGNATURE.PARAMETERS, true) /\ ~$lossy_optional_integer_mode(pfunction.SIGNATURE.PARAMETERS, false)',
            'psparam_a.DEFAULT = PSDEFAULT expression_a "int"',
            'expression_a = NExprBitwiseNot expression_shift metadata_not',
            'expression_shift = NExprBinaryOpShiftLeft (NScalarInt (INTEGER 3) metadata_three) (NScalarInt (INTEGER 1) metadata_one) metadata_shift',
            '$psnumber(expression_shift) = PSNONNUMERIC',
            '$lossy_optional_integer_default(expression_shift) = (6)',
            '$psnumber(expression_a) = PSNONNUMERIC',
            '$lossy_optional_integer_default(expression_a) = ($(-7))',
            '$default_parameter_origin(S, porigin, 0) = PORIGIN n_unit pcpath_parameter',
            'pcpath_default = pcpath_parameter ++ [PCFIELD 6]',
            'porigin_default = PORIGIN n_unit pcpath_default',
            '$origin_node(S.SOURCES, porigin_default) = (expression_a)',
            '$default_at(pfunction.DEFAULTS, 0) = ({INDEX 0, ORIGIN porigin_default, KIND PDSTORED})',
            '$compiled_read(S, porigin_default) = (PINT $(-7))',
            'pfunction.DEFAULTS = [pdefault_a, pdefault_b, pdefault_c, pdefault_d, pdefault_e]',
            '~$lossy_optional_integer_tail(S, pfunction[.DEFAULTS = [pdefault_a[.INDEX = 1], pdefault_b, pdefault_c, pdefault_d, pdefault_e]], [psparam_a], 0)',
            '~$lossy_optional_integer_tail(S, pfunction[.DEFAULTS = [pdefault_a[.KIND = PDDEFERRED], pdefault_b, pdefault_c, pdefault_d, pdefault_e]], [psparam_a], 0)',
            '$lossy_optional_integer_header(S, pfunction, pfunction.SIGNATURE.PARAMETERS, 0)',
            'psparam_b.DEFAULT = PSDEFAULT expression_b "int"',
            'expression_b = NExprBinaryOpPlus (NExprUnaryPlus (NScalarInt (INTEGER 3) metadata_b_three) metadata_b_plus) expression_mod metadata_b_sum',
            'expression_mod = NExprBinaryOpMod (NExprUnaryMinus (NScalarInt (INTEGER 35) metadata_thirty_five) metadata_b_minus) (NScalarInt (INTEGER 21) metadata_twenty_one) metadata_mod',
            '$lossy_optional_integer_default(expression_mod) = ($(-14))',
            '$lossy_optional_integer_default(expression_b) = ($(-11))',
            'psparam_c.DEFAULT = PSDEFAULT expression_c "int"',
            'expression_c = NExprBinaryOpPlus expression_xor expression_right_sum metadata_c_sum',
            'expression_xor = NExprBinaryOpBitwiseXor expression_or expression_and metadata_xor',
            'expression_or = NExprBinaryOpBitwiseOr (NScalarInt (INTEGER 11) metadata_eleven) (NScalarInt (INTEGER 6) metadata_or_six) metadata_or',
            'expression_and = NExprBinaryOpBitwiseAnd (NScalarInt (INTEGER 6) metadata_and_six) (NScalarInt (INTEGER 2) metadata_and_two) metadata_and',
            'expression_right_sum = NExprBinaryOpPlus expression_right (NScalarInt (INTEGER 2) metadata_right_two) metadata_right_sum',
            'expression_right = NExprBinaryOpShiftRight (NExprUnaryMinus (NScalarInt (INTEGER 3) metadata_right_three) metadata_right_minus) (NScalarInt (INTEGER 1) metadata_right_count) metadata_right',
            '$lossy_optional_integer_default(expression_or) = (15)',
            '$lossy_optional_integer_default(expression_and) = (2)',
            '$lossy_optional_integer_default(expression_xor) = (13)',
            '$lossy_optional_integer_default(expression_right) = ($(-2))',
            '$lossy_optional_integer_default(expression_right_sum) = (0)',
            '$lossy_optional_integer_default(expression_c) = (13)',
            'psparam_d.DEFAULT = PSDEFAULT expression_d "int"',
            'expression_d = NExprBinaryOpPlus expression_min_shift expression_min_mod metadata_d_sum',
            'expression_min_shift = NExprBinaryOpShiftLeft (NScalarInt (INTEGER 1) metadata_min_one) (NScalarInt (INTEGER 63) metadata_min_sixty_three) metadata_min_shift',
            'expression_min_mod = NExprBinaryOpMod (NExprBinaryOpShiftLeft (NScalarInt (INTEGER 1) metadata_min_mod_one) (NScalarInt (INTEGER 63) metadata_min_mod_sixty_three) metadata_min_mod_shift) (NExprUnaryMinus (NScalarInt (INTEGER 1) metadata_negative_one) metadata_minus_one) metadata_min_mod',
            '$lossy_optional_integer_default(expression_min_shift) = ($(-9223372036854775808))',
            '$lossy_optional_integer_default(expression_min_mod) = (0)',
            '$lossy_optional_integer_default(expression_d) = ($(-9223372036854775808))',
            'psparam_e.DEFAULT = PSDEFAULT expression_e "int"',
            'expression_e = NExprBitwiseNot (NExprBinaryOpShiftLeft (NScalarInt (INTEGER 1) metadata_max_one) (NScalarInt (INTEGER 63) metadata_max_sixty_three) metadata_max_shift) metadata_max_not',
            '$lossy_optional_integer_default(expression_e) = (9223372036854775807)',
            '$lossy_optional_integer_default(NExprUnaryMinus expression_d metadata_minus_one) = eps',
            '$lossy_optional_integer_default(NExprUnaryMinus (NExprUnaryMinus expression_d metadata_minus_one) metadata_minus_one) = eps',
            'expression_same = NExprBitwiseNot (NExprBinaryOpShiftLeft (NScalarInt (INTEGER 6) metadata_three) (NScalarInt (INTEGER 0) metadata_one) metadata_shift) metadata_not',
            '$lossy_optional_integer_default(expression_same) = ($(-7))',
            '~$lossy_optional_integer_tail(S, pfunction, [psparam_a[.DEFAULT = PSDEFAULT expression_same "int"]], 0)',
            'S_wrong_value = S[.POOLS = [{UNIT n_unit, CONSTANTS ([(PCONSTANT pcpath_default (PINT 7))])}]]',
            '$compiled_read(S_wrong_value, porigin_default) = (PINT 7)',
            '~$lossy_optional_integer_tail(S_wrong_value, pfunction, [psparam_a], 0)',
            'S.CURRENT = (pcallcontext)',
            r'pcallcontext.ARGC = 3 /\ pcallcontext.HOLES = [0, 1] /\ pcallcontext.NAMED = eps',
            'pcallcontext.CALLSITE = (porigin_call)',
            '$named_call_valid(S, porigin, (porigin_call))',
            '$named_call_shape(S, porigin, (porigin_call)) = {SLOTS ([NAMED_HOLE, NAMED_HOLE, NAMED_SENT (KNOWN PNULL)]), NAMED eps}',
            '$lookup(S.ENV, psparam_a.NAME) = (n_a)',
            '$lookup(S.ENV, psparam_b.NAME) = (n_b)',
            '$lookup(S.ENV, psparam_c.NAME) = (n_cell)',
            r'S.STORE[n_a] = DEFINED (PINT $(-7)) /\ S.STORE[n_b] = DEFINED (PINT $(-11))',
            r'~(n_a <- S.REFCELLS) /\ ~(n_b <- S.REFCELLS)',
            r'$heap_owners($heap_graph(S), HCELL n_a) = 1 /\ $heap_owners($heap_graph(S), HCELL n_b) = 1',
            r'$lookup(S.ENV, psparam_d.NAME) = eps /\ $lookup(S.ENV, psparam_e.NAME) = eps',
            'S.STORE[n_cell] = DEFINED (PFLOAT 4615063718147915776)',
            r'n_cell <- S.REFCELLS /\ $heap_owners($heap_graph(S), HCELL n_cell) = 2',
            '$lossy_mixed_parameter_source_valid(S, LOSSY_MIXED_PARAMETER_RECEIVE porigin 2 n_cell n_bits i z)',
            '$task_nodes(LOSSY_MIXED_PARAMETER_RECEIVE porigin 2 n_cell n_bits i z) = eps',
            'z_hole = $default_parameter_line(S, porigin, 0)',
            'ptask_hole = LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_a n_bits i z_hole',
            'S_hole = S[.STORE[n_a] = DEFINED (PFLOAT n_bits)][.REFCELLS = n_a :: S.REFCELLS][.ORIGIN = ($default_parameter_origin(S, porigin, 0))][.TODO = [ptask_hole]]',
            '$lossy_positional_reference_parameter_ready(S_hole, 0, n_a)',
            '$typed_receive_valid(S_hole[.TODO = [TYPE_RECEIVE porigin 0]][.ORIGIN = (porigin)], porigin, 0)',
            '~$lossy_mixed_parameter_source_valid(S_hole, ptask_hole)',
            'PhpStep: S ~> S_next',
            r'S_next.TODO = [TYPE_RECEIVE porigin 3] /\ S_next.STORE[n_cell] = DEFINED (PINT 1)',
            'PhpStep: S_next ~> S_default_d',
            'S_default_d.TODO = [DEFAULT_RECEIVE porigin 3]',
            'PhpStep: S_default_d ~> S_d',
            'S_d.TODO = [TYPE_RECEIVE porigin 4]',
            'PhpStep: S_d ~> S_default_e',
            'S_default_e.TODO = [DEFAULT_RECEIVE porigin 4]',
            'PhpStep: S_default_e ~> S_body',
            'S_body.TODO = $call_receive_body(S_default_e, pfunction)',
            '$lookup(S_body.ENV, psparam_d.NAME) = (n_d)',
            '$lookup(S_body.ENV, psparam_e.NAME) = (n_e)',
            r'S_body.STORE[n_d] = DEFINED (PINT $(-9223372036854775808)) /\ S_body.STORE[n_e] = DEFINED (PINT 9223372036854775807)',
            r'~(n_d <- S_body.REFCELLS) /\ ~(n_e <- S_body.REFCELLS)',
            r'$heap_owners($heap_graph(S_body), HCELL n_d) = 1 /\ $heap_owners($heap_graph(S_body), HCELL n_e) = 1',
            r'S_body.EVENTS = S.EVENTS /\ $call_descriptors_valid(S_body) /\ $heap_valid($heap_graph(S_body))',
            'S_done = $drive_steps(S_body, 2000)',
            r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
            r'~((HCELL n_a) <- S_done.ALLOCATIONS) /\ ~((HCELL n_b) <- S_done.ALLOCATIONS) /\ ~((HCELL n_d) <- S_done.ALLOCATIONS) /\ ~((HCELL n_e) <- S_done.ALLOCATIONS)',
            r'S_done.STORE[n_cell] = DEFINED (PINT 1) /\ $heap_owners($heap_graph(S_done), HCELL n_cell) = 1',
            '$lookup(S_done.ENV, $ptascii("gotReceive191")) = (n_got)',
            'S_done.STORE[n_got] = DEFINED (PINT 1)',
            r'$call_descriptors_valid(S_done) /\ $heap_valid($heap_graph(S_done))',
        ],
    },
}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE))
