#!/usr/bin/env python3
"""Literal CONCAT bytes, conversion contexts and selected-reference retirement."""
import base64
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol


metadata_index = 0
fixed_metadata = None


def node(constructor, *children):
    global metadata_index
    metadata_index += 1
    metadata = fixed_metadata or f'metadata_peer_{metadata_index}'
    return constructor + ''.join(f' ({child})' for child in children) + ' ' + metadata


def integer(value):
    return node('NScalarInt', f'INTEGER {value}')


def constant(name, qualified=False):
    kind = 'NNameFullyQualified' if qualified else 'NName'
    return node('NExprConstFetch', node(kind, f'BYTES "{base64.b64encode(name.encode()).decode()}"'))


def string(value):
    data = value.encode() if isinstance(value, str) else value
    return node('NScalarString', f'BYTES "{base64.b64encode(data).decode()}"')


def floating(bits):
    return node('NScalarFloat', f'FLOAT "{bits}"')


def ternary(condition, selected, alternative):
    return node('NExprTernary', condition, selected, alternative)


def cast(child):
    return node('NExprCastInt', child)


def binary(kind, left, right):
    return node('NExprBinaryOp' + kind, left, right)


def coalesce(left, right):
    return binary('Coalesce', left, right)


def float_cast(child):
    return node('NExprCastDouble', child)


patterns = [
    node('NExprUnaryMinus', ternary(binary('Concat', string(''), string('0')), constant('UnselectedReceive204'), integer(7))),
    cast(ternary(binary('Concat', string('0'), string('.0')),
                 binary('Concat', string('-1'), binary('Concat', string('1'), string('tail'))), constant('UnselectedReceive204'))),
    cast(ternary(float_cast(ternary(constant('true'), binary('Concat', string('0'), string('.5tail')), constant('UnselectedReceive204'))),
                 binary('Concat', string('1'), string('3tail')), constant('UnselectedReceive204'))),
    ternary(float_cast(coalesce(constant('null'), binary('Concat', string('-0'), string('.0')))),
            constant('UnselectedReceive204'), cast(binary('Concat', string('-922337203685477580'), string('8tail')))),
    cast(ternary(constant('true'), binary('Concat', string('999999999999'), string('999999999999')), constant('UnselectedReceive204'))),
]
contrast = cast(node('NExprBooleanNot', floating('3fe0000000000000')))


CATALOGUE = Path(__file__).with_name('concat_string_default_reception_cases.json')
assert hashlib.sha256(CATALOGUE.read_bytes()).hexdigest() == 'a71dba2406fe60c4a3e18e25a00e0747578c02331d56b702025f15de20744ea6'
row = next(row for row in json.loads(CATALOGUE.read_text()) if row['id'] == 'concat-string-precision-modes')
assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
source = row['source']
handler = source[:source.index('function valueFirstReceive204(')]
reference = source[source.index('function referenceReceive204('):source.index("set_error_handler('warningReceive204');")]
setup = source[source.index("set_error_handler('warningReceive204');"):source.index('$gotReceive204 = valueFirstReceive204(')]
start = source.index('$gotReceive204 = referenceReceive204(')
end = source.index('$xReceive204 = 1.5;', start)
leading = handler + reference + setup + source[start:end]
assert hashlib.sha256(leading.encode()).hexdigest() == 'e908305be4e0fe3ec707f912feec49b6bb90bb449985832a1f0d9e3d489933d8'

checks = [
    r'n_bits = 4609434218613702656 /\ i = 1',
    '$function_at(S.FUNCTIONS, porigin) = (pfunction)',
    'plenv_source = pfunction.ENV',
    r'plenv_source.NAMESPACE = eps /\ plenv_source.CONSTANTS = eps',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_a, psparam_b, psparam_c, psparam_d, psparam_e]',
    r'$lossy_optional_integer_mode(pfunction.SIGNATURE.PARAMETERS, true) /\ ~$lossy_optional_integer_mode(pfunction.SIGNATURE.PARAMETERS, false)',
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
    'plenv_alias = plenv_source[.CONSTANTS = [($ptascii("true"), $ptascii("false"))]]',
    '$lossy_optional_integer_default_in(plenv_alias, expression_c) = eps',
    '$lossy_optional_integer_default_in(plenv_alias, expression_e) = eps',
    '~$lossy_optional_integer_header(S, pfunction[.ENV = plenv_alias], pfunction.SIGNATURE.PARAMETERS, 0)',
    'plenv_null_alias = plenv_source[.CONSTANTS = [($ptascii("null"), $ptascii("true"))]]',
    '$lossy_optional_integer_default_in(plenv_null_alias, expression_d) = eps',
    '~$lossy_optional_integer_header(S, pfunction[.ENV = plenv_null_alias], pfunction.SIGNATURE.PARAMETERS, 0)',
    '$call_target(S, $ptascii("deferredFloatNotReceive204"), eps) = (pfunction_contrast)',
    'pfunction_contrast.ORIGIN = PORIGIN n_unit pcpath_contrast_function',
    'pfunction_contrast.ORIGIN =/= porigin',
    'pfunction_contrast.SIGNATURE.PARAMETERS = [psparam_contrast]',
    r'~psparam_contrast.REQUIRED /\ ~psparam_contrast.BYREF /\ ~psparam_contrast.VARIADIC /\ $ptmasks(psparam_contrast.TYPE) = ["int"]',
    'psparam_contrast.DEFAULT = PSDEFAULT expression_contrast "deferred"',
    f'expression_contrast = {contrast}',
    '$default_parameter_origin(S, pfunction_contrast.ORIGIN, 0) = PORIGIN n_unit pcpath_contrast',
    'porigin_contrast = PORIGIN n_unit (pcpath_contrast ++ [PCFIELD 6])',
    '$origin_node(S.SOURCES, porigin_contrast) = (expression_contrast)',
    'pfunction_contrast.DEFAULTS = [{INDEX 0, ORIGIN porigin_contrast, KIND PDDEFERRED}]',
    '$compiled_read(S, porigin_contrast) = eps',
    '$lossy_optional_integer_default_in(pfunction_contrast.ENV, expression_contrast) = (0)',
    '~$lossy_optional_integer_header(S, pfunction_contrast, pfunction_contrast.SIGNATURE.PARAMETERS, 0)',
    'psparam_forged = psparam_contrast[.DEFAULT = PSDEFAULT expression_contrast "int"]',
    '~$lossy_optional_integer_tail(S, pfunction_contrast, [psparam_forged], 0)',
    'pfunction_forged = pfunction_contrast[.DEFAULTS = [{INDEX 0, ORIGIN porigin_contrast, KIND PDSTORED}]]',
    '~$lossy_optional_integer_tail(S, pfunction_forged, [psparam_forged], 0)',
    'expression_same = NExprUnaryMinus (NScalarInt (INTEGER 7) metadata_a) metadata_a',
    '$lossy_optional_integer_default_in(plenv_source, expression_same) = ($(-7))',
    '~$lossy_optional_integer_tail(S, pfunction, [psparam_a[.DEFAULT = PSDEFAULT expression_same "int"]], 0)',
    'pfunction.DEFAULTS = [pdefault_a, pdefault_b, pdefault_c, pdefault_d, pdefault_e]',
    '~$lossy_optional_integer_tail(S, pfunction[.DEFAULTS = [pdefault_a, pdefault_b[.KIND = PDDEFERRED], pdefault_c, pdefault_d, pdefault_e]], [psparam_b], 1)',
    'S_no_pool = S[.POOLS = eps]',
    '$origin_node(S_no_pool.SOURCES, porigin_a) = (expression_a)',
    '$compiled_read(S_no_pool, porigin_a) = eps',
    '~$lossy_optional_integer_header(S_no_pool, pfunction, pfunction.SIGNATURE.PARAMETERS, 0)',
    'S_wrong_type = S[.POOLS = [{UNIT n_unit, CONSTANTS ([(PCONSTANT (pcpath_c ++ [PCFIELD 6]) (PBOOL true))])}]]',
    '$compiled_read(S_wrong_type, porigin_c) = (PBOOL true)',
    '~$lossy_optional_integer_tail(S_wrong_type, pfunction, [psparam_c], 2)',
])

# Original selected syntax keeps bytes distinct from truth and numeric conversion.
checks.extend([
    'expression_select_a = NExprTernary expression_zero_a expression_unused_a expression_seven_a metadata_select_a',
    '$lossy_optional_integer_string(expression_zero_a) = ([48])',
    '$lossy_optional_integer_condition(plenv_source, expression_zero_a) = (false)',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt expression_zero_a metadata_a) = (0)',
    'expression_b = NExprCastInt expression_select_b metadata_b',
    'expression_select_b = NExprTernary expression_zero_b expression_string_b expression_unused_b metadata_select_b',
    '$lossy_optional_integer_string(expression_zero_b) = ([48, 46, 48])',
    '$lossy_optional_integer_leaf_truth(plenv_source, expression_zero_b) = ((expression_zero_b, true))',
    '$lossy_optional_integer_float_truth(expression_zero_b, true) = false',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt expression_zero_b metadata_b) = (0)',
    '$lossy_optional_integer_cast_leaf(plenv_source, expression_select_b) = (expression_string_b)',
    '$lossy_optional_integer_string(expression_string_b) = ([45, 49, 49, 116, 97, 105, 108])',
    'expression_c = NExprCastInt expression_select_c metadata_c',
    'expression_select_c = NExprTernary expression_float_c expression_string_c expression_unused_c metadata_select_c',
    'expression_float_c = NExprCastDouble expression_inner_c metadata_float_c',
    'expression_inner_c = NExprTernary expression_true_c expression_fraction_c expression_unused_inner_c metadata_inner_c',
    '$lossy_optional_integer_leaf_truth(plenv_source, expression_inner_c) = ((expression_fraction_c, true))',
    '$lossy_optional_integer_string(expression_fraction_c) = ([48, 46, 53, 116, 97, 105, 108])',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt expression_fraction_c metadata_c) = (0)',
    '$lossy_optional_integer_condition(plenv_source, expression_float_c) = (true)',
    '$lossy_optional_integer_cast_leaf(plenv_source, expression_select_c) = (expression_string_c)',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt expression_string_c metadata_c) = (13)',
    'expression_d = NExprTernary expression_float_d expression_unused_d expression_minimum_d metadata_d',
    'expression_float_d = NExprCastDouble expression_coalesce_d metadata_float_d',
    'expression_coalesce_d = NExprBinaryOpCoalesce expression_null_d expression_zero_d metadata_coalesce_d',
    '$lossy_optional_integer_leaf_truth(plenv_source, expression_coalesce_d) = ((expression_zero_d, true))',
    '$lossy_optional_integer_string(expression_zero_d) = ([45, 48, 46, 48])',
    '$lossy_optional_integer_float_truth(expression_zero_d, true) = false',
    '$lossy_optional_integer_leaf_truth(plenv_source, expression_float_d) = ((expression_float_d, false))',
    '$lossy_optional_integer_special(plenv_source, expression_float_d) = eps',
    'expression_e = NExprCastInt expression_select_e metadata_e',
    'expression_select_e = NExprTernary expression_true_e expression_maximum_e expression_unused_e metadata_select_e',
    '$lossy_optional_integer_cast_leaf(plenv_source, expression_select_e) = (expression_maximum_e)',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt expression_maximum_e metadata_e) = (9223372036854775807)',
])

true, false, null = map(constant, ('true', 'false', 'null'))
unknown = constant('UnselectedReceive204')
zero, seven = map(integer, (0, 7))
nan = floating('7ff8000000000000')

# These independently specified byte lists test order, emptiness and binary payloads.
for left, right, data, truth in [
    (b'', b'', [], 'false'), (b'', b'0', [48], 'false'),
    (b'0', b'', [48], 'false'), (b'0', b'0', [48, 48], 'true'),
    (b'0', b'.0', [48, 46, 48], 'true'),
    (b'\0', b'0', [0, 48], 'true'), (b'0', b'\0', [48, 0], 'true'),
    (b'\xff', b'\0', [255, 0], 'true'), (b'ab', b'cd', [97, 98, 99, 100], 'true'),
]:
    expression = binary('Concat', string(left), string(right))
    expected = '[' + ', '.join(map(str, data)) + ']' if data else 'eps'
    checks.extend([
        f'$lossy_optional_integer_string({expression}) = ({expected})',
        f'$lossy_optional_integer_condition(plenv_source, {expression}) = ({truth})',
        f'$lossy_optional_integer_leaf_truth(plenv_source, {expression}) = (({expression}, {truth}))',
    ])
for left, right, integer_result, float_truth in [
    ('0', '.0', '0', 'false'), ('0.', '5tail', '0', 'true'),
    ('-', '11tail', '$(-11)', 'true'), ('1e', '-999', '0', 'false'),
    ('+1e', '999junk', '9223372036854775807', 'true'),
    ('-.', '0tail', '0', 'false'), ('\0', '9', '0', 'false'),
    ('0.5\0', 'ignored', '0', 'true'),
    ('-922337203685477580', '9tail', '$(-9223372036854775808)', 'true'),
    ('922337203685477580', '7tail', '9223372036854775807', 'true'),
]:
    expression = binary('Concat', string(left), string(right))
    checks.extend([
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = ({integer_result})',
        f'$lossy_optional_integer_float_truth({expression}, true) = {float_truth}',
        f'$lossy_optional_integer_condition(plenv_source, {float_cast(expression)}) = ({float_truth})',
    ])

concat_zero = binary('Concat', string('0'), string('.0'))
concat_fraction = binary('Concat', string('0.'), string('5tail'))
for expression in [
    ternary(true, concat_zero, unknown),
    ternary(concat_zero, 'ABSENT', unknown),
    coalesce(concat_zero, unknown),
    coalesce(null, concat_zero),
    ternary(false, nan, concat_zero),
]:
    checks.extend([
        f'$lossy_optional_integer_leaf_truth(plenv_source, {expression}) = (({concat_zero}, true))',
        f'$lossy_optional_integer_condition(plenv_source, {float_cast(expression)}) = (false)',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = (0)',
    ])
boolean_zero = node('NExprCastBool', concat_zero)
integer_zero = cast(concat_fraction)
checks.extend([
    f'$lossy_optional_integer_condition(plenv_source, {boolean_zero}) = (true)',
    f'$lossy_optional_integer_condition(plenv_source, {float_cast(boolean_zero)}) = (true)',
    f'$lossy_optional_integer_condition(plenv_source, {float_cast(integer_zero)}) = (false)',
    f'$lossy_optional_integer_condition(plenv_source, {float_cast(float_cast(concat_zero))}) = (false)',
    f'$lossy_optional_integer_condition(plenv_source, {coalesce(float_cast(concat_zero), unknown)}) = (false)',
    f'$lossy_optional_integer_special(plenv_source, {concat_zero}) = eps',
    f'$lossy_optional_integer_string({cast(concat_zero)}) = eps',
    f'$lossy_optional_integer_string({float_cast(concat_zero)}) = eps',
    f'$lossy_optional_integer_condition(plenv_alias, {ternary(constant("true"), concat_fraction, concat_zero)}) = (true)',
    f'$lossy_optional_integer_condition(plenv_alias, {float_cast(ternary(constant("true"), concat_fraction, concat_zero))}) = (false)',
    f'$lossy_optional_integer_condition(plenv_alias, {float_cast(ternary(constant("true", qualified=True), concat_fraction, concat_zero))}) = (true)',
    f'$lossy_optional_integer_default_in(plenv_source, {float_cast(concat_fraction)}) = eps',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(float_cast(concat_fraction))}) = eps',
])
for child in [
    unknown, integer(1), null, true, nan,
    node('NExprCastString', integer(1)),
    ternary(true, string('0'), unknown),
]:
    for expression in [binary('Concat', string(''), child), binary('Concat', child, string(''))]:
        checks.extend([
            f'$lossy_optional_integer_string({expression}) = eps',
            f'$lossy_optional_integer_condition(plenv_source, {expression}) = eps',
            f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = eps',
            f'$lossy_optional_integer_condition(plenv_source, {float_cast(expression)}) = eps',
        ])
# Nested CONCAT descends through each child; selected shorthand retains one AST.
deep = string('0')
for _ in range(24):
    deep = binary('Concat', string(''), deep)
checks.extend([
    f'$lossy_optional_integer_string({deep}) = ([48])',
    f'$lossy_optional_integer_condition(plenv_source, {deep}) = (false)',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(deep)}) = (0)',
])
deep = concat_zero
for _ in range(24):
    deep = ternary(deep, 'ABSENT', unknown)
checks.extend([
    f'$lossy_optional_integer_leaf_truth(plenv_source, {deep}) = (({concat_zero}, true))',
    f'$lossy_optional_integer_condition(plenv_source, {float_cast(deep)}) = (false)',
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
    r'S.STORE[n_cell] = DEFINED (PFLOAT 4615063718147915776) /\ n_cell <- S.REFCELLS',
    '$heap_owners($heap_graph(S), HCELL n_cell) = 2',
    '$lossy_mixed_parameter_source_valid(S, LOSSY_MIXED_PARAMETER_RECEIVE porigin 2 n_cell n_bits i z)',
    '$task_nodes(LOSSY_MIXED_PARAMETER_RECEIVE porigin 2 n_cell n_bits i z) = eps',
    'S_budget = $drive_steps(S, 0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL], 1) = $drive_steps(S, 1)',
    'PhpStep: S ~> S_next',
    r'S_next.TODO = [TYPE_RECEIVE porigin 3] /\ S_next.STORE[n_cell] = DEFINED (PINT 1)',
    r'S_next.STORE[n_a] = S.STORE[n_a] /\ S_next.STORE[n_b] = S.STORE[n_b] /\ S_next.EVENTS = S.EVENTS',
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
    '$lookup(S_done.ENV, $ptascii("gotReceive204")) = (n_got)',
    'S_done.STORE[n_got] = DEFINED (PINT 1)',
    r'$call_descriptors_valid(S_done) /\ $heap_valid($heap_graph(S_done))',
])

CASES = {'concat-string-reference-leading': {
    'source': leading,
    'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 2 n_cell n_bits i z]',
    'checks': checks,
}}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
