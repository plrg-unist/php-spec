#!/usr/bin/env python3
"""Value-preserving cast selections retain exact omitted-default ownership."""
import base64
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('selection_integer_cast_default_reception_cases.json')
SOURCES = {}
for row in json.loads(CATALOGUE.read_text()):
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
    SOURCES[row['id']] = row['source']

# Fresh first-VAL front preserves the whole five-default declaration; source0.
full = SOURCES['selection-integer-cast-precision-modes']
setup = full.index("set_error_handler('warningReceive198');")
start = full.index('$gotReceive198 = valueFirstReceive198(')
end = full.index('$xReceive198 = 1.5;', start)
source = full[:full.index('function referenceFirstReceive198')] + full[setup:end]
assert hashlib.sha256(source.encode()).hexdigest() == '5de103a729e4936af3cdf5e6f8434d9c09e55a997e6e0edeb9e8f6f9dcd339f9'

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


def binary(constructor, left, right):
    return node('NExprBinaryOp' + constructor, left, right)


def conditional(cond, yes, no):
    return node('NExprTernary', cond, yes, no)


patterns = [
    node('NExprUnaryMinus', cast(conditional(integer(7), 'ABSENT', constant('UnselectedReceive198')))),
    cast(binary('Coalesce', constant('null'), conditional(constant('false'), 'ABSENT', string('-11tail')))),
    add(integer(13), cast(binary('Coalesce',
        conditional(constant('true'), binary('Smaller', integer(1), integer(0)), constant('UnselectedReceive198')),
        constant('UnselectedReceive198')))),
    cast(conditional(constant('true'), node('NExprUnaryMinus', node('NScalarFloat', 'FLOAT "43e0000000000000"')),
                     constant('UnselectedReceive198'))),
    cast(binary('Coalesce', conditional(constant('false'), constant('UnselectedReceive198'), constant('null')),
                string('999999999999999999999999'))),
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
    'expression_a = NExprUnaryMinus expression_cast_a metadata_a',
    'expression_cast_a = NExprCastInt expression_short_a metadata_cast_a',
    'expression_short_a = NExprTernary expression_seven ABSENT expression_unknown metadata_short_a',
    '$lossy_optional_integer_selection_shape(expression_short_a)',
    '~$lossy_optional_integer_selection_shape(expression_seven)',
    '$lossy_optional_integer_cast_leaf(plenv_source, expression_short_a) = (expression_seven)',
    '$lossy_optional_integer_default_in(plenv_source, expression_short_a) = (7)',
    '$lossy_optional_integer_default_in(plenv_source, expression_cast_a) = (7)',
    'expression_b = NExprCastInt expression_coalesce_b metadata_b',
    'expression_coalesce_b = NExprBinaryOpCoalesce expression_null expression_short_b metadata_coalesce_b',
    'expression_short_b = NExprTernary expression_false ABSENT expression_string_b metadata_short_b',
    '$lossy_optional_integer_special(plenv_source, expression_null) = (PNULL)',
    '$lossy_optional_integer_cast_leaf(plenv_source, expression_coalesce_b) = (expression_string_b)',
    'expression_c = NExprBinaryOpPlus expression_thirteen expression_cast_c metadata_c',
    'expression_cast_c = NExprCastInt expression_coalesce_c metadata_cast_c',
    'expression_coalesce_c = NExprBinaryOpCoalesce expression_select_c expression_unknown_right metadata_coalesce_c',
    'expression_select_c = NExprTernary expression_true expression_false_comparison expression_unknown_left metadata_select_c',
    '$lossy_optional_integer_condition(plenv_source, expression_false_comparison) = (false)',
    '$lossy_optional_integer_cast_leaf(plenv_source, expression_coalesce_c) = (expression_false_comparison)',
    '$lossy_optional_integer_default_in(plenv_source, expression_false_comparison) = eps',
    '$lossy_optional_integer_default_in(plenv_source, expression_cast_c) = (0)',
    'expression_d = NExprCastInt expression_select_d metadata_d',
    'expression_select_d = NExprTernary expression_true_d expression_negative_float expression_unknown_d metadata_select_d',
    'expression_negative_float = NExprUnaryMinus expression_positive_float metadata_negative_float',
    '$lossy_optional_integer_cast_leaf(plenv_source, expression_select_d) = (expression_negative_float)',
    '$lossy_optional_integer_float_literal(expression_positive_float) = ($hex_bits("43e0000000000000", 0))',
    '$lossy_optional_integer_float_literal(expression_negative_float) = ($hex_bits("c3e0000000000000", 0))',
    'expression_e = NExprCastInt expression_coalesce_e metadata_e',
    'expression_coalesce_e = NExprBinaryOpCoalesce expression_select_e expression_string_e metadata_coalesce_e',
    '$lossy_optional_integer_cast_leaf(plenv_source, expression_coalesce_e) = (expression_string_e)',
    'expression_zero = NScalarInt (INTEGER 0) metadata_a',
    'expression_one = NScalarInt (INTEGER 1) metadata_a',
    '$lossy_optional_integer_cast_leaf(plenv_source, NExprTernary expression_unknown expression_seven expression_zero metadata_a) = eps',
    '$lossy_optional_integer_cast_leaf(plenv_source, NExprBinaryOpCoalesce expression_unknown expression_seven metadata_a) = eps',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt (NExprTernary expression_true expression_positive_float expression_seven metadata_a) metadata_a) = eps',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt (NExprBinaryOpCoalesce expression_positive_float expression_seven metadata_a) metadata_a) = eps',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt (NExprTernary expression_false expression_unknown expression_null metadata_a) metadata_a) = (0)',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt (NExprTernary expression_one expression_true expression_unknown metadata_a) metadata_a) = (1)',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt (NExprTernary expression_true expression_true expression_false metadata_a) metadata_a) = (1)',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt (NExprBinaryOpCoalesce expression_null expression_true metadata_a) metadata_a) = (1)',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt (NExprBinaryOpCoalesce expression_true expression_false metadata_a) metadata_a) = (1)',
])
for left in ['expression_false', 'expression_zero', 'NScalarString (BYTES "") metadata_a']:
    checks.append(f'$lossy_optional_integer_default_in(plenv_source, NExprCastInt (NExprBinaryOpCoalesce ({left}) expression_unknown metadata_a) metadata_a) = (0)')
for cond in ['NScalarString (BYTES "MQ==") metadata_a', 'NScalarFloat (FLOAT "3ff0000000000000") metadata_a']:
    checks.append(f'$lossy_optional_integer_default_in(plenv_source, NExprCastInt (NExprTernary ({cond}) expression_seven expression_zero metadata_a) metadata_a) = (7)')
checks.extend([
    'expression_inf_string = NScalarString (BYTES "MWU5OTk=") metadata_a',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt (NExprTernary expression_true expression_inf_string expression_unknown metadata_a) metadata_a) = (0)',
    'plenv_alias = plenv_source[.CONSTANTS = [($ptascii("true"), $ptascii("false"))]]',
    '$lossy_optional_integer_default_in(plenv_alias, expression_d) = eps',
    '~$lossy_optional_integer_header(S, pfunction[.ENV = plenv_alias], pfunction.SIGNATURE.PARAMETERS, 0)',
    'expression_same = NExprUnaryMinus expression_seven metadata_a',
    '$lossy_optional_integer_default_in(plenv_source, expression_same) = ($(-7))',
    '~$lossy_optional_integer_tail(S, pfunction, [psparam_a[.DEFAULT = PSDEFAULT expression_same "int"]], 0)',
    'S_wrong_value = S[.POOLS = [{UNIT n_unit, CONSTANTS ([(PCONSTANT (pcpath_b ++ [PCFIELD 6]) (PINT 11))])}]]',
    '$compiled_read(S_wrong_value, porigin_b) = (PINT 11)',
    '~$lossy_optional_integer_tail(S_wrong_value, pfunction, [psparam_b], 1)',
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
    '$lookup(psymboltable_global.ENV, $ptascii("xReceive198")) = (n_global)',
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

CASES = {'selection-cast-default-omitted-tail': {
    'source': source,
    'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z]',
    'checks': checks,
}}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
