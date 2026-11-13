#!/usr/bin/env python3
"""Literal-string bitwise NOT preserves conversion context and authentic default ownership."""
import base64
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('bitnot_string_default_reception_cases.json')
SOURCES = {}
for row in json.loads(CATALOGUE.read_text()):
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
    SOURCES[row['id']] = row['source']

# Fresh first-VAL front preserves the whole five-default declaration; source0.
full = SOURCES['bitnot-string-precision-modes']
setup = full.index("set_error_handler('warningReceive205');")
start = full.index('$gotReceive205 = valueFirstReceive205(')
end = full.index('$xReceive205 = 1.5;', start)
source = full[:full.index('function referenceFirstReceive205')] + full[setup:end]
assert hashlib.sha256(source.encode()).hexdigest() == 'b7fae235366c8b02545ec932eeb7e5eaefd7b1626533fe2ea6ff9df1b52bab04'

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
    payload = value if isinstance(value, bytes) else value.encode()
    return node('NScalarString', f'BYTES "{base64.b64encode(payload).decode()}"')


def floating(bits):
    return node('NScalarFloat', f'FLOAT "{bits}"')


def boolean(child):
    return node('NExprCastBool', child)


def cast(child):
    return node('NExprCastInt', child)


def binary(constructor, left, right):
    return node('NExprBinaryOp' + constructor, left, right)


def conditional(cond, yes, no):
    return node('NExprTernary', cond, yes, no)


def float_cast(child):
    return node('NExprCastDouble', child)


def string_not_value(value):
    data = value if isinstance(value, bytes) else value.encode()
    return node('NExprBitwiseNot', string(bytes(255 - byte for byte in data)))


patterns = [
    node('NExprUnaryMinus', conditional(string_not_value('0'), constant('UnselectedReceive205'), integer(7))),
    cast(conditional(string_not_value('0.0'), string_not_value('-11tail'), constant('UnselectedReceive205'))),
    cast(conditional(float_cast(conditional(constant('true'), binary('Concat', string_not_value('0'), string('.5tail')), constant('UnselectedReceive205'))), string_not_value('13tail'), constant('UnselectedReceive205'))),
    conditional(float_cast(binary('Coalesce', constant('null'), string_not_value('-0.0'))), constant('UnselectedReceive205'), cast(string_not_value('-9223372036854775808tail'))),
    cast(conditional(constant('true'), string_not_value('999999999999999999999999'), constant('UnselectedReceive205'))),
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
    'expression_a = NExprUnaryMinus expression_select_a metadata_a',
    'expression_select_a = NExprTernary expression_concat_a expression_unknown_a expression_seven metadata_select_a',
    '$lossy_optional_integer_string(expression_concat_a) = ([48])',
    '$lossy_optional_integer_condition(plenv_source, expression_concat_a) = (false)',
    'expression_b = NExprCastInt expression_select_b metadata_b',
    'expression_select_b = NExprTernary expression_concat_b expression_string_b expression_unknown_b metadata_select_b',
    '$lossy_optional_integer_string(expression_concat_b) = ([48, 46, 48])',
    '$lossy_optional_integer_condition(plenv_source, expression_concat_b) = (true)',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt expression_concat_b metadata_b) = (0)',
    '$lossy_optional_integer_condition(plenv_source, NExprCastDouble expression_concat_b metadata_b) = (false)',
    '$lossy_optional_integer_string(expression_string_b) = ($ptascii("-11tail"))',
    'expression_c = NExprCastInt expression_select_c metadata_c',
    'expression_select_c = NExprTernary expression_float_c expression_string_c expression_unknown_c metadata_select_c',
    'expression_float_c = NExprCastDouble expression_inner_c metadata_float_c',
    'expression_inner_c = NExprTernary expression_true_c expression_fraction_c expression_unknown_inner_c metadata_inner_c',
    '$lossy_optional_integer_leaf_truth(plenv_source, expression_inner_c) = ((expression_fraction_c, true))',
    '$lossy_optional_integer_condition(plenv_source, expression_float_c) = (true)',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt expression_float_c metadata_c) = eps',
    'expression_d = NExprTernary expression_float_d expression_unknown_d expression_minimum_cast metadata_d',
    'expression_float_d = NExprCastDouble expression_coalesce_d metadata_float_d',
    'expression_coalesce_d = NExprBinaryOpCoalesce expression_null_d expression_zero_d metadata_coalesce_d',
    '$lossy_optional_integer_leaf_truth(plenv_source, expression_coalesce_d) = ((expression_zero_d, true))',
    '$lossy_optional_integer_condition(plenv_source, expression_float_d) = (false)',
    '$lossy_optional_integer_special(plenv_source, expression_float_d) = eps',
    '$call_target(S, $ptascii("deferredFloatNotReceive205"), eps) = (pfunction_not)',
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
    'plenv_true_alias = plenv_source[.CONSTANTS = [($ptascii("true"), $ptascii("false"))]]',
    '$lossy_optional_integer_default_in(plenv_true_alias, expression_e) = eps',
    '~$lossy_optional_integer_header(S, pfunction[.ENV = plenv_true_alias], pfunction.SIGNATURE.PARAMETERS, 0)',
    'expression_same = NExprUnaryMinus (NScalarInt (INTEGER 7) metadata_a) metadata_a',
    '$lossy_optional_integer_default_in(plenv_source, expression_same) = ($(-7))',
    '~$lossy_optional_integer_tail(S, pfunction, [psparam_a[.DEFAULT = PSDEFAULT expression_same "int"]], 0)',
    'pfunction.DEFAULTS = [pdefault_a, pdefault_b, pdefault_c, pdefault_d, pdefault_e]',
    '~$lossy_optional_integer_tail(S, pfunction[.DEFAULTS = [pdefault_a, pdefault_b[.KIND = PDDEFERRED], pdefault_c, pdefault_d, pdefault_e]], [psparam_b], 1)',
    'S_wrong_value = S[.POOLS = [{UNIT n_unit, CONSTANTS ([(PCONSTANT (pcpath_c ++ [PCFIELD 6]) (PINT 1))])}]]',
    '$compiled_read(S_wrong_value, porigin_c) = (PINT 1)',
    '~$lossy_optional_integer_tail(S_wrong_value, pfunction, [psparam_c], 2)',
])
true, false, null = map(constant, ('true', 'false', 'null'))
unknown = constant('UnselectedReceive205')
# Byte results distinguish raw truth, decimal-prefix casts and saturating integer conversion.
for left, right, raw, converted, integer_value in [
    ('', '', 'false', 'false', '0'), ('', '0', 'false', 'false', '0'),
    ('0', '.0', 'true', 'false', '0'), ('0', '.5tail', 'true', 'true', '0'),
    ('-1', '1tail', 'true', 'true', '$(-11)'),
    ('1e', '999', 'true', 'true', '0'),
    ('1e', '-999', 'true', 'false', '0'), ('5e', '-324', 'true', 'true', '0'),
    (b'13', b'\x00tail', 'true', 'true', '13'), (b'\xff', b'13', 'true', 'false', '0'),
    ('999999999999', '999999999999', 'true', 'true', '9223372036854775807'),
    ('-922337203685477580', '8tail', 'true', 'true', '$(-9223372036854775808)'),
]:
    data = (left.encode() if isinstance(left, str) else left) + (right.encode() if isinstance(right, str) else right)
    expression = string_not_value(data)
    bytes_value = '[' + ', '.join(map(str, data)) + ']' if data else 'eps'
    checks.extend([
        f'$lossy_optional_integer_string({expression}) = ({bytes_value})',
        f'$lossy_optional_integer_condition(plenv_source, {expression}) = ({raw})',
        f'$lossy_optional_integer_leaf_truth(plenv_source, {expression}) = (({expression}, {raw}))',
        f'$lossy_optional_integer_condition(plenv_source, {float_cast(expression)}) = ({converted})',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = ({integer_value})',
        f'$lossy_optional_integer_default_in(plenv_source, {expression}) = eps',
    ])
concat_zero = string_not_value('0.0')
checks.extend([
    f'$lossy_optional_integer_condition(plenv_source, {float_cast(boolean(concat_zero))}) = (true)',
    f'$lossy_optional_integer_condition(plenv_source, {float_cast(cast(concat_zero))}) = (false)',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(float_cast(concat_zero))}) = eps',
    f'$lossy_optional_integer_condition(plenv_source, {binary("Concat", string(".0"), string("0"))}) = (true)',
    f'$lossy_optional_integer_condition(plenv_source, {float_cast(binary("Concat", string(".0"), string("0")))}) = (false)',
])
for child in [
    unknown, null, false, integer(13), floating('3fe0000000000000'),
    node('NExprCastString', unknown), conditional(true, string('0'), string('0')),
    node('NExprArray', 'SEQUENCE eps'),
]:
    for expression in (binary('Concat', string(''), child), binary('Concat', child, string(''))):
        checks.extend([
            f'$lossy_optional_integer_string({expression}) = eps',
            f'$lossy_optional_integer_condition(plenv_source, {expression}) = eps',
            f'$lossy_optional_integer_condition(plenv_source, {float_cast(expression)}) = eps',
            f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = eps',
        ])
for selected in [
    conditional(true, concat_zero, unknown), conditional(concat_zero, 'ABSENT', unknown),
    binary('Coalesce', null, concat_zero), binary('Coalesce', concat_zero, unknown),
]:
    checks.extend([
        f'$lossy_optional_integer_leaf_truth(plenv_source, {selected}) = (({concat_zero}, true))',
        f'$lossy_optional_integer_condition(plenv_source, {float_cast(selected)}) = (false)',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(selected)}) = (0)',
    ])
# Existing integer-NOT and literal-CONCAT contexts stay separate from new string results.
checks.extend([
    f'$lossy_optional_integer_condition(plenv_source, {concat_zero}) = (true)',
    f'$lossy_optional_integer_condition(plenv_source, {float_cast(concat_zero)}) = (false)',
])
# Raw byte0xff, zero and ASCII0 distinguish string and integer NOT.
for expression, byte_result, truth in [
    (node('NExprBitwiseNot', string('0')), '[207]', 'true'),
    (node('NExprBitwiseNot', string(b'\xff')), '[0]', 'true'),
    (node('NExprBitwiseNot', string(b'\0')), '[255]', 'true'),
    (node('NExprBitwiseNot', node('NExprBitwiseNot', string('0'))), '[48]', 'false'),
]:
    checks.extend([
        f'$lossy_optional_integer_string({expression}) = ({byte_result})',
        f'$lossy_optional_integer_condition(plenv_source, {expression}) = ({truth})',
        f'$lossy_optional_integer_default_in(plenv_source, {expression}) = eps',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = (0)',
    ])
integer_not = node('NExprBitwiseNot', integer(0))
checks.extend([
    f'$lossy_optional_integer_string({integer_not}) = eps',
    f'$lossy_optional_integer_default_in(plenv_source, {integer_not}) = ($(-1))',
    f'$lossy_optional_integer_condition(plenv_source, {float_cast(integer_not)}) = (true)',
])
for child in [unknown, null, false, floating('3fe0000000000000'),
              conditional(true, string('0'), unknown), node('NExprCastString', unknown)]:
    expression = node('NExprBitwiseNot', child)
    checks.extend([
        f'$lossy_optional_integer_string({expression}) = eps',
        f'$lossy_optional_integer_condition(plenv_source, {expression}) = eps',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = eps',
    ])
deep = string('0')
for _ in range(24):
    deep = node('NExprBitwiseNot', deep)
checks.extend([
    f'$lossy_optional_integer_string({deep}) = ([48])',
    f'$lossy_optional_integer_condition(plenv_source, {deep}) = (false)',
    f'$lossy_optional_integer_condition(plenv_source, {float_cast(deep)}) = (false)',
])
deep = concat_zero
for _ in range(24):
    deep = conditional(deep, 'ABSENT', unknown)
checks.extend([
    f'$lossy_optional_integer_leaf_truth(plenv_source, {deep}) = (({concat_zero}, true))',
    f'$lossy_optional_integer_condition(plenv_source, {float_cast(deep)}) = (false)',
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
    '$lookup(psymboltable_global.ENV, $ptascii("xReceive205")) = (n_global)',
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
    '$lookup(S_done.ENV, $ptascii("gotReceive205")) = (n_got)',
    'S_done.STORE[n_got] = DEFINED (PINT 13)',
    r'$call_descriptors_valid(S_done) /\ $heap_valid($heap_graph(S_done))',
])

CASES = {'bitnot-string-default-omitted-tail': {
    'source': source,
    'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z]',
    'checks': checks,
}}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
