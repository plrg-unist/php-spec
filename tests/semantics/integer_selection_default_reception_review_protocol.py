#!/usr/bin/env python3
"""Selection environments, named holes and omitted reference-cell cleanup."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('integer_selection_default_reception_cases.json')
SOURCES = {}
for row in json.loads(CATALOGUE.read_text()):
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
    SOURCES[row['id']] = row['source']

# Retain fresh setup and the leading REF call. Removed calls and their histories
# have no source credit in this independently derived fixture.
source = SOURCES['integer-selection-precision-modes']
start = source.index('$gotReceive193 = referenceReceive193(')
end = source.index('$xReceive193 = 1.5;', start)
leading = source[:source.index('$gotReceive193 = valueFirstReceive193(')] + source[start:end]
assert hashlib.sha256(leading.encode()).hexdigest() == '475d36aec4f042e239eb43310c0463693df502788273bfdbf50236c4d0ff3412'

checks = [
    r'n_bits = 4609434218613702656 /\ i = 1',
    '$function_at(S.FUNCTIONS, porigin) = (pfunction)',
    'plenv_source = pfunction.ENV',
    'plenv_source.CONSTANTS = eps',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_a, psparam_b, psparam_c, psparam_d, psparam_e]',
    r'$lossy_optional_integer_mode(pfunction.SIGNATURE.PARAMETERS, true) /\ ~$lossy_optional_integer_mode(pfunction.SIGNATURE.PARAMETERS, false)',
    'psparam_a.DEFAULT = PSDEFAULT expression_a "int"',
    'expression_a = NExprTernary expression_true expression_minus_seven expression_unknown metadata_a',
    'expression_true = NExprConstFetch (NName (BYTES "VHJVZQ==") metadata_true_name) metadata_true',
    'expression_minus_seven = NExprUnaryMinus (NScalarInt (INTEGER 7) metadata_seven) metadata_minus',
    'expression_unknown = NExprConstFetch name_unknown metadata_unknown',
    'psparam_b.DEFAULT = PSDEFAULT expression_b "int"',
    'expression_b = NExprTernary expression_null expression_unknown_b expression_shorthand metadata_b',
    'expression_null = NExprConstFetch (NName (BYTES "bnVsbA==") metadata_null_name) metadata_null',
    'expression_unknown_b = NExprConstFetch name_unknown_b metadata_unknown_b',
    'expression_shorthand = NExprTernary (NScalarInt (INTEGER 0) metadata_zero) ABSENT (NExprUnaryMinus (NScalarInt (INTEGER 11) metadata_eleven) metadata_minus_eleven) metadata_shorthand',
    'psparam_c.DEFAULT = PSDEFAULT expression_c "int"',
    'expression_c = NExprTernary expression_coalesce_zero expression_unknown_c expression_coalesce_null metadata_c',
    'expression_coalesce_zero = NExprBinaryOpCoalesce (NScalarInt (INTEGER 0) metadata_zero_left) expression_unknown_zero metadata_coalesce_zero',
    'expression_coalesce_null = NExprBinaryOpCoalesce (NExprConstFetch (NName (BYTES "bnVsbA==") metadata_null_rhs_name) metadata_null_rhs) (NScalarInt (INTEGER 13) metadata_thirteen) metadata_coalesce_null',
    'expression_unknown_c = NExprConstFetch name_unknown_c metadata_unknown_c',
    'expression_unknown_zero = NExprConstFetch name_unknown_zero metadata_unknown_zero',
    'psparam_d.DEFAULT = PSDEFAULT expression_d "int"',
    'expression_d = NExprTernary expression_min ABSENT expression_unknown_d metadata_d',
    'expression_min = NExprBinaryOpPow (NExprUnaryMinus (NScalarInt (INTEGER 2) metadata_two) metadata_minus_two) (NScalarInt (INTEGER 63) metadata_sixty_three) metadata_min',
    'expression_unknown_d = NExprConstFetch name_unknown_d metadata_unknown_d',
    'psparam_e.DEFAULT = PSDEFAULT expression_e "int"',
    'expression_e = NExprTernary expression_false expression_unknown_e (NExprBitwiseNot expression_min_e metadata_not) metadata_e',
    'expression_false = NExprConstFetch (NNameFullyQualified (BYTES "RmFMc0U=") metadata_false_name) metadata_false',
    'expression_min_e = NExprBinaryOpPow (NExprUnaryMinus (NScalarInt (INTEGER 2) metadata_e_two) metadata_e_minus) (NScalarInt (INTEGER 63) metadata_e_count) metadata_e_min',
    'expression_unknown_e = NExprConstFetch name_unknown_e metadata_unknown_e',
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
    'pfunction.DEFAULTS = [pdefault_a, pdefault_b, pdefault_c, pdefault_d, pdefault_e]',
    '~$lossy_optional_integer_tail(S, pfunction[.DEFAULTS = [pdefault_a[.INDEX = 1], pdefault_b, pdefault_c, pdefault_d, pdefault_e]], [psparam_a], 0)',
    '~$lossy_optional_integer_tail(S, pfunction[.DEFAULTS = [pdefault_a[.KIND = PDDEFERRED], pdefault_b, pdefault_c, pdefault_d, pdefault_e]], [psparam_a], 0)',
    'expression_same = NExprTernary expression_true expression_minus_seven (NScalarInt (INTEGER 13) metadata_thirteen) metadata_a',
    '$lossy_optional_integer_default_in(plenv_source, expression_same) = ($(-7))',
    '~$lossy_optional_integer_tail(S, pfunction, [psparam_a[.DEFAULT = PSDEFAULT expression_same "int"]], 0)',
    'S_wrong_value = S[.POOLS = [{UNIT n_unit, CONSTANTS ([(PCONSTANT (pcpath_a ++ [PCFIELD 6]) (PINT 7))])}]]',
    '$compiled_read(S_wrong_value, porigin_a) = (PINT 7)',
    '~$lossy_optional_integer_tail(S_wrong_value, pfunction, [psparam_a], 0)',
    'plenv_alias = plenv_source[.CONSTANTS = [($ptascii("TrUe"), $ptascii("false")), ($ptascii("FaLsE"), $ptascii("true"))]]',
    '$lossy_optional_integer_special(plenv_alias, expression_true) = (PBOOL false)',
    '$lossy_optional_integer_special(plenv_alias, expression_false) = (PBOOL false)',
    '$lossy_optional_integer_default_in(plenv_alias, expression_same) = (13)',
    '$lossy_optional_integer_default_in(plenv_alias, expression_a) = eps',
    '~$lossy_optional_integer_header(S, pfunction[.ENV = plenv_alias], pfunction.SIGNATURE.PARAMETERS, 0)',
    'expression_choice = NExprTernary expression_true (NScalarInt (INTEGER 2) metadata_two) (NScalarInt (INTEGER 3) metadata_seven) metadata_a',
    '$lossy_optional_integer_default_in(plenv_source, expression_choice) = (2)',
    '$lossy_optional_integer_default_in(plenv_alias, expression_choice) = (3)',
    '$lossy_optional_integer_default(expression_choice) = (2)',
])

# Every old recursive constructor must preserve the real declaration ENV.
one = '(NScalarInt (INTEGER 1) metadata_seven)'
two = '(NScalarInt (INTEGER 2) metadata_seven)'
four = '(NScalarInt (INTEGER 4) metadata_seven)'
twice = f'(NExprBinaryOpMul expression_choice {two} metadata_a)'
for expression, ordinary, aliased in [
    (f'NExprBinaryOpPlus expression_choice {one} metadata_a', 3, 4),
    (f'NExprBinaryOpMinus expression_choice {one} metadata_a', 1, 2),
    (f'NExprBinaryOpMul expression_choice {two} metadata_a', 4, 6),
    (f'NExprBinaryOpDiv {twice} {two} metadata_a', 2, 3),
    (f'NExprBinaryOpPow expression_choice {two} metadata_a', 4, 9),
    (f'NExprBinaryOpMod expression_choice {two} metadata_a', 0, 1),
    (f'NExprBinaryOpShiftLeft expression_choice {one} metadata_a', 4, 6),
    (f'NExprBinaryOpShiftRight {twice} {one} metadata_a', 2, 3),
    (f'NExprBinaryOpBitwiseAnd expression_choice {one} metadata_a', 0, 1),
    (f'NExprBinaryOpBitwiseOr expression_choice {four} metadata_a', 6, 7),
    (f'NExprBinaryOpBitwiseXor expression_choice {one} metadata_a', 3, 2),
    ('NExprBitwiseNot expression_choice metadata_a', '$(-3)', '$(-4)'),
    ('NExprUnaryPlus expression_choice metadata_a', 2, 3),
    ('NExprUnaryMinus expression_choice metadata_a', '$(-2)', '$(-3)'),
]:
    checks.extend([
        f'$lossy_optional_integer_default_in(plenv_source, {expression}) = ({ordinary})',
        f'$lossy_optional_integer_default_in(plenv_alias, {expression}) = ({aliased})',
    ])
checks.extend([
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
    '$lookup(S_done.ENV, $ptascii("gotReceive193")) = (n_got)',
    'S_done.STORE[n_got] = DEFINED (PINT 1)',
    r'$call_descriptors_valid(S_done) /\ $heap_valid($heap_graph(S_done))',
])

CASES = {'integer-selection-reference-leading': {
    'source': leading,
    'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 2 n_cell n_bits i z]',
    'checks': checks,
}}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE))
