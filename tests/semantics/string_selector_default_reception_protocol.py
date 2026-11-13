#!/usr/bin/env python3
"""Numeric-string selectors preserve quiet compiler DIM folding and default authority."""
import base64
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('string_selector_default_reception_cases.json')
SOURCES = {}
for row in json.loads(CATALOGUE.read_text()):
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
    SOURCES[row['id']] = row['source']

# Fresh first-VAL front preserves the whole five-default declaration; source0.
full = SOURCES['string-selector-precision-modes']
setup = full.index("set_error_handler('warningReceive208');")
start = full.index('$gotReceive208 = valueFirstReceive208(')
end = full.index('$xReceive208 = 1.5;', start)
source = full[:full.index('function referenceFirstReceive208')] + full[setup:end]
assert hashlib.sha256(source.encode()).hexdigest() == 'af788286c11034406a674718ebf88fda5e02233e31f3a43a6f1c1fc196738ea0'

metadata_index = 0
fixed_metadata = None
def node(constructor, *children):
    global metadata_index
    metadata_index += 1
    metadata = fixed_metadata or f'metadata_case_{metadata_index}'
    return constructor + ''.join(f' ({child})' for child in children) + ' ' + metadata


def integer(value):
    literal = str(value) if value >= 0 else f'$({value})'
    return node('NScalarInt', f'INTEGER {literal}')


def constant(name):
    payload = base64.b64encode(name.encode()).decode()
    return node('NExprConstFetch', node('NName', f'BYTES "{payload}"'))


def string(value):
    payload = value if isinstance(value, bytes) else value.encode()
    return node('NScalarString', f'BYTES "{base64.b64encode(payload).decode()}"')


def floating(bits):
    return node('NScalarFloat', f'FLOAT "{bits}"')


def cast(child):
    return node('NExprCastInt', child)


def binary(constructor, left, right):
    return node('NExprBinaryOp' + constructor, left, right)


def conditional(cond, yes, no):
    return node('NExprTernary', cond, yes, no)


def float_cast(child):
    return node('NExprCastDouble', child)


def dimension(base, selector):
    return node('NExprArrayDimFetch', base, selector)


patterns = [
    node('NExprUnaryMinus', conditional(dimension(string('10'), string('01tail')), constant('UnselectedReceive208'), integer(7))),
    cast(conditional(dimension(string(b'\0x'), string(' +0tail')), string('-11tail'), constant('UnselectedReceive208'))),
    cast(conditional(float_cast(conditional(constant('true'), binary('Concat', dimension(string('x0'), string('+1')), string('.5tail')), constant('UnselectedReceive208'))), binary('Concat', dimension(string('x1'), string(b'1\0tail')), string('3tail')), constant('UnselectedReceive208'))),
    conditional(float_cast(binary('Coalesce', constant('null'), dimension(string('-0'), string(' \t1 ')))), constant('UnselectedReceive208'), cast(string('-9223372036854775808tail'))),
    cast(conditional(constant('true'), binary('Concat', dimension(string('x9'), string('0001')), string('9' * 23)), constant('UnselectedReceive208'))),
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
    '$lossy_optional_integer_string(expression_concat_b) = ([0])',
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
    '$lossy_optional_integer_leaf_truth(plenv_source, expression_coalesce_d) = ((expression_zero_d, false))',
    '$lossy_optional_integer_condition(plenv_source, expression_float_d) = (false)',
    '$lossy_optional_integer_special(plenv_source, expression_float_d) = eps',
    '$call_target(S, $ptascii("deferredFloatNotReceive208"), eps) = (pfunction_not)',
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
unknown = constant('UnselectedReceive208')
# Integer numeric strings fold without runtime offset diagnostics, even with tails.
for value, selector, expected, truth, integer_value, numeric_truth in [
    (b'10', '01tail', b'0', 'false', '0', 'false'),
    (b'\0x', ' +0tail', b'\0', 'true', '0', 'false'),
    (b'v9', '0001', b'9', 'true', '9', 'true'),
    (b'\xc3\xa9', ' +0', b'\xc3', 'true', '0', 'false'),
    (b'\xc3\xa9', b'1\0tail', b'\xa9', 'true', '0', 'false'),
    (b'\xff', '0x1', b'\xff', 'true', '0', 'false'),
]:
    expression = dimension(string(value), string(selector))
    expected_bytes = '[' + ', '.join(map(str, expected)) + ']'
    checks.extend([
        f'$lossy_optional_integer_string({expression}) = ({expected_bytes})',
        f'$lossy_optional_integer_condition(plenv_source, {expression}) = ({truth})',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = ({integer_value})',
        f'$lossy_optional_integer_condition(plenv_source, {float_cast(expression)}) = ({numeric_truth})',
        f'$lossy_optional_integer_default_in(plenv_source, {expression}) = eps',
    ])
for selector in [integer(0), node('NExprUnaryMinus', integer(0)), node('NExprUnaryPlus', integer(0)),
                 string('0'), string('-0'), string('+0'), string('00000')]:
    expression = dimension(string(b'\0'), selector)
    checks.append(f'$lossy_optional_integer_string({expression}) = ([0])')
# Floats, nonnumeric text, out-of-bounds offsets and dynamic syntax stay outside.
for selector in [integer(-1), node('NExprUnaryMinus', integer(1)), integer(1),
                 integer(9223372036854775807), integer(9223372036854775808),
                 floating('0000000000000000'), floating('3ff0000000000000'),
                 string('bad'), string('1.0'), string('1e0'), string('1.0tail'), string(''),
                 string('-1'), string('9223372036854775808'), string(b'\0'),
                 true, false, null, unknown, 'ABSENT',
                 binary('Plus', integer(0), integer(0)),
                 node('NExprVariable', 'BYTES "aQ=="')]:
    expression = dimension(string('x'), selector)
    checks.extend([
        f'$lossy_optional_integer_string({expression}) = eps',
        f'$lossy_optional_integer_condition(plenv_source, {expression}) = eps',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = eps',
    ])
for base in [string(''), integer(0), true, false, null, unknown,
             conditional(true, string('x'), unknown), node('NExprVariable', 'BYTES "eA=="')]:
    expression = dimension(base, integer(0))
    checks.extend([
        f'$lossy_optional_integer_string({expression}) = eps',
        f'$lossy_optional_integer_condition(plenv_source, {expression}) = eps',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = eps',
    ])
# Existing certified byte producers compose before and after DIM.
for base in [binary('Concat', string('x'), string('0')),
             binary('BitwiseOr', string('x0'), string(b'\0\0')),
             binary('BitwiseAnd', string('x0'), string(b'\xff\xff')),
             binary('BitwiseXor', string('x0'), string(b'\0\0')),
             node('NExprBitwiseNot', string(bytes(255 - n for n in b'x0')))]:
    expression = dimension(base, string('+1tail'))
    checks.extend([
        f'$lossy_optional_integer_string({expression}) = ([48])',
        f'$lossy_optional_integer_condition(plenv_source, {expression}) = (false)',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = (0)',
    ])
raw_zero = dimension(binary('Concat', string('x'), string('0')), string('01'))
for selected in [conditional(true, raw_zero, unknown), conditional(raw_zero, 'ABSENT', raw_zero), binary('Coalesce', null, raw_zero)]:
    checks.extend([
        f'$lossy_optional_integer_leaf_truth(plenv_source, {selected}) = (({raw_zero}, false))',
        f'$lossy_optional_integer_condition(plenv_source, {float_cast(selected)}) = (false)',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(selected)}) = (0)',
    ])
deep = dimension(string('1'), integer(0))
for _ in range(16):
    deep = dimension(deep, string('+0tail'))
checks.extend([
    f'$lossy_optional_integer_string({deep}) = ([49])',
    f'$lossy_optional_integer_condition(plenv_source, {deep}) = (true)',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(deep)}) = (1)',
    '$call_target(S, $ptascii("deferredNegativeIndexReceive208"), eps) = (pfunction_negative)',
    'pfunction_negative.SIGNATURE.PARAMETERS = [psparam_negative]',
    'psparam_negative.DEFAULT = PSDEFAULT expression_negative "deferred"',
    'expression_negative = NExprCastInt (NExprArrayDimFetch (NScalarString (BYTES "MTA=") metadata_negative_base) (NScalarString (BYTES "LTE=") metadata_negative_index) metadata_negative_dim) metadata_negative_cast',
    '$lossy_optional_integer_default_in(pfunction_negative.ENV, expression_negative) = eps',
    '$default_parameter_origin(S, pfunction_negative.ORIGIN, 0) = PORIGIN n_unit_negative pcpath_negative',
    'porigin_negative = PORIGIN n_unit_negative (pcpath_negative ++ [PCFIELD 6])',
    '$origin_node(S.SOURCES, porigin_negative) = (expression_negative)',
    '$default_at(pfunction_negative.DEFAULTS, 0) = ({INDEX 0, ORIGIN porigin_negative, KIND PDDEFERRED})',
    '$compiled_read(S, porigin_negative) = eps',
    '~$lossy_optional_integer_header(S, pfunction_negative, pfunction_negative.SIGNATURE.PARAMETERS, 0)',
    '~$lossy_optional_integer_tail(S, pfunction_negative, [psparam_negative[.DEFAULT = PSDEFAULT expression_negative "int"]], 0)',
])
# The invalid-selector loop freshly checks the three corrected old207 refusals.
for selector in [string('1'), binary('Concat', string('0'), string('1tail')),
                 node('NExprBitwiseNot', string(bytes(255 - n for n in b'1'))),
                 binary('BitwiseOr', string('1'), string(b'\0')),
                 dimension(string('01'), integer(1))]:
    checks.append(f'$lossy_optional_integer_string({dimension(string("09"), selector)}) = ([57])')
checks.extend([
    '$call_target(S, $ptascii("deferredFloatIndexReceive208"), eps) = (pfunction_floatindex)',
    'pfunction_floatindex.SIGNATURE.PARAMETERS = [psparam_floatindex]',
    'psparam_floatindex.DEFAULT = PSDEFAULT expression_floatindex "deferred"',
    'expression_floatindex = NExprCastInt (NExprArrayDimFetch (NScalarString (BYTES "MTA=") metadata_floatindex_base) (NScalarString (BYTES "MS4w") metadata_floatindex_index) metadata_floatindex_dim) metadata_floatindex_cast',
    '$lossy_optional_integer_default_in(pfunction_floatindex.ENV, expression_floatindex) = eps',
    '$default_parameter_origin(S, pfunction_floatindex.ORIGIN, 0) = PORIGIN n_unit_floatindex pcpath_floatindex',
    'porigin_floatindex = PORIGIN n_unit_floatindex (pcpath_floatindex ++ [PCFIELD 6])',
    '$origin_node(S.SOURCES, porigin_floatindex) = (expression_floatindex)',
    '$default_at(pfunction_floatindex.DEFAULTS, 0) = ({INDEX 0, ORIGIN porigin_floatindex, KIND PDDEFERRED})',
    '$compiled_read(S, porigin_floatindex) = eps',
    '~$lossy_optional_integer_header(S, pfunction_floatindex, pfunction_floatindex.SIGNATURE.PARAMETERS, 0)',
    '~$lossy_optional_integer_tail(S, pfunction_floatindex, [psparam_floatindex[.DEFAULT = PSDEFAULT expression_floatindex "int"]], 0)',
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
    '$lookup(psymboltable_global.ENV, $ptascii("xReceive208")) = (n_global)',
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
    '$lookup(S_done.ENV, $ptascii("gotReceive208")) = (n_got)',
    'S_done.STORE[n_got] = DEFINED (PINT 13)',
    r'$call_descriptors_valid(S_done) /\ $heap_valid($heap_graph(S_done))',
])

CASES = {'string-selector-default-omitted-tail': {
    'source': source,
    'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z]',
    'checks': checks,
}}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
