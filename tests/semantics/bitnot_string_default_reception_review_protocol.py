#!/usr/bin/env python3
"""Literal-byte string NOT, conversion contexts and selected-reference retirement."""
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


def bitnot(child):
    return node('NExprBitwiseNot', child)


patterns = [
    node('NExprUnaryMinus', ternary(bitnot(string(b'\xcf')), constant('UnselectedReceive205'), integer(7))),
    cast(ternary(bitnot(string(b'\xcf\xd1\xcf')),
                 bitnot(string(b'\xd2\xce\xce\x8b\x9e\x96\x93')), constant('UnselectedReceive205'))),
    cast(ternary(float_cast(ternary(constant('true'),
                                   binary('Concat', bitnot(string(b'\xcf')), string('.5tail')), constant('UnselectedReceive205'))),
                 bitnot(string(b'\xce\xcc\x8b\x9e\x96\x93')), constant('UnselectedReceive205'))),
    ternary(float_cast(coalesce(constant('null'), bitnot(string(b'\xd2\xcf\xd1\xcf')))),
            constant('UnselectedReceive205'),
            cast(bitnot(string(b'\xd2\xc6\xcd\xcd\xcc\xcc\xc8\xcd\xcf\xcc\xc9\xc7\xca\xcb\xc8\xc8\xca\xc7\xcf\xc7\x8b\x9e\x96\x93')))),
    cast(ternary(constant('true'), bitnot(string(b'\xc6' * 24)), constant('UnselectedReceive205'))),
]
contrast = cast(node('NExprBooleanNot', floating('3fe0000000000000')))


CATALOGUE = Path(__file__).with_name('bitnot_string_default_reception_cases.json')
assert hashlib.sha256(CATALOGUE.read_bytes()).hexdigest() == 'cdc7f6ac3a5e37efdff73b19df9d8b153cfcf1afb4bc4d94085f0e8e42dd06cc'
row = next(row for row in json.loads(CATALOGUE.read_text()) if row['id'] == 'bitnot-string-precision-modes')
assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
source = row['source']
handler = source[:source.index('function valueFirstReceive205(')]
reference = source[source.index('function referenceReceive205('):source.index("set_error_handler('warningReceive205');")]
setup = source[source.index("set_error_handler('warningReceive205');"):source.index('$gotReceive205 = valueFirstReceive205(')]
start = source.index('$gotReceive205 = referenceReceive205(')
end = source.index('$xReceive205 = 1.5;', start)
leading = handler + reference + setup + source[start:end]
assert hashlib.sha256(leading.encode()).hexdigest() == '082013ae1dc3b2fd1b357f529e89916ba3dc7e62b3b2f853d709ac97c8e94079'

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
    '$call_target(S, $ptascii("deferredFloatNotReceive205"), eps) = (pfunction_contrast)',
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

# Original source roots retain byte identity through selection and conversion.
checks.extend([
    'expression_select_a = NExprTernary expression_not_a expression_unused_a expression_seven_a metadata_select_a',
    'expression_not_a = NExprBitwiseNot expression_string_a metadata_not_a',
    '$lossy_optional_integer_string(expression_string_a) = ([207])',
    '$lossy_optional_integer_string(expression_not_a) = ([48])',
    '$lossy_optional_integer_condition(plenv_source, expression_not_a) = (false)',
    'expression_b = NExprCastInt expression_select_b metadata_b',
    'expression_select_b = NExprTernary expression_not_b expression_string_b expression_unused_b metadata_select_b',
    '$lossy_optional_integer_string(expression_not_b) = ([48, 46, 48])',
    '$lossy_optional_integer_leaf_truth(plenv_source, expression_not_b) = ((expression_not_b, true))',
    '$lossy_optional_integer_float_truth(expression_not_b, true) = false',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt expression_not_b metadata_b) = (0)',
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
unknown = constant('UnselectedReceive205')
nan = floating('7ff8000000000000')

# Explicit expected bytes distinguish complement from truth or numeric negation.
for data, expected, raw, integer_result, numeric_truth in [
    (b'', [], 'false', '0', 'false'),
    (b'\xff', [0], 'true', '0', 'false'),
    (b'\0', [255], 'true', '0', 'false'),
    (b'\xcf', [48], 'false', '0', 'false'),
    (b'\xce', [49], 'true', '1', 'true'),
    (b'\xcf\xd1\xcf', [48, 46, 48], 'true', '0', 'false'),
    (b'\xcf\xd1\xca\x8b\x9e\x96\x93', [48, 46, 53, 116, 97, 105, 108], 'true', '0', 'true'),
    (b'\xd2\xce\xce\x8b\x9e\x96\x93', [45, 49, 49, 116, 97, 105, 108], 'true', '$(-11)', 'true'),
]:
    expression = bitnot(string(data))
    bytes_value = '[' + ', '.join(map(str, expected)) + ']' if expected else 'eps'
    checks.extend([
        f'$lossy_optional_integer_string({expression}) = ({bytes_value})',
        f'$lossy_optional_integer_condition(plenv_source, {expression}) = ({raw})',
        f'$lossy_optional_integer_leaf_truth(plenv_source, {expression}) = (({expression}, {raw}))',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = ({integer_result})',
        f'$lossy_optional_integer_condition(plenv_source, {float_cast(expression)}) = ({numeric_truth})',
    ])
    double = bitnot(expression)
    original_bytes = '[' + ', '.join(map(str, data)) + ']' if data else 'eps'
    checks.append(f'$lossy_optional_integer_string({double}) = ({original_bytes})')

not_zero = bitnot(string(b'\xcf\xd1\xcf'))
not_fraction = bitnot(string(b'\xcf\xd1\xca\x8b\x9e\x96\x93'))
not_empty = bitnot(string(''))
checks.extend([
    f'$lossy_optional_integer_condition(plenv_source, {float_cast(node("NExprCastBool", not_zero))}) = (true)',
    f'$lossy_optional_integer_condition(plenv_source, {float_cast(cast(not_fraction))}) = (false)',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(float_cast(not_fraction))}) = (0)',
    f'$lossy_optional_integer_condition(plenv_source, {coalesce(not_empty, unknown)}) = (false)',
    f'$lossy_optional_integer_special(plenv_source, {not_empty}) = eps',
    f'$lossy_optional_integer_string({bitnot(binary("Concat", string(b"\xcf"), string(b"\xd1\xcf")))}) = ([48, 46, 48])',
    f'$lossy_optional_integer_string({binary("Concat", bitnot(string(b"\xcf")), string(".0"))}) = ([48, 46, 48])',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(bitnot(bitnot(string("1e999"))))}) = (0)',
])
for selected in [
    ternary(true, not_zero, unknown), ternary(not_zero, 'ABSENT', unknown),
    coalesce(null, not_zero), coalesce(not_zero, unknown),
    ternary(false, nan, not_zero),
]:
    checks.extend([
        f'$lossy_optional_integer_leaf_truth(plenv_source, {selected}) = (({not_zero}, true))',
        f'$lossy_optional_integer_condition(plenv_source, {float_cast(selected)}) = (false)',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(selected)}) = (0)',
    ])
for child in [unknown, null, true, floating('0000000000000000'), nan,
              node('NExprCastString', unknown), ternary(true, string('0'), unknown)]:
    expression = bitnot(child)
    checks.extend([
        f'$lossy_optional_integer_string({expression}) = eps',
        f'$lossy_optional_integer_condition(plenv_source, {expression}) = eps',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = eps',
    ])
# Existing integer NOT uses its long result, never a string-byte certificate.
for child in [integer(0), cast(string('0'))]:
    expression = bitnot(child)
    checks.extend([
        f'$lossy_optional_integer_string({expression}) = eps',
        f'$lossy_optional_integer_default_in(plenv_source, {expression}) = ($(-1))',
        f'$lossy_optional_integer_condition(plenv_source, {expression}) = (true)',
    ])
checks.extend([
    f'$lossy_optional_integer_condition(plenv_alias, {float_cast(ternary(constant("true"), not_fraction, not_zero))}) = (false)',
    f'$lossy_optional_integer_condition(plenv_alias, {float_cast(ternary(constant("true", qualified=True), not_fraction, not_zero))}) = (true)',
])
# Two complement parities and cached shorthand depth remain bounded cost controls.
deep = string('0')
for _ in range(24):
    deep = bitnot(deep)
checks.extend([
    f'$lossy_optional_integer_string({deep}) = ([48])',
    f'$lossy_optional_integer_condition(plenv_source, {deep}) = (false)',
    f'$lossy_optional_integer_string({bitnot(deep)}) = ([207])',
    f'$lossy_optional_integer_condition(plenv_source, {bitnot(deep)}) = (true)',
])
deep = not_zero
for _ in range(24):
    deep = ternary(deep, 'ABSENT', unknown)
checks.extend([
    f'$lossy_optional_integer_leaf_truth(plenv_source, {deep}) = (({not_zero}, true))',
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
    '$lookup(S_done.ENV, $ptascii("gotReceive205")) = (n_got)',
    'S_done.STORE[n_got] = DEFINED (PINT 1)',
    r'$call_descriptors_valid(S_done) /\ $heap_valid($heap_graph(S_done))',
])

CASES = {'bitnot-string-reference-leading': {
    'source': leading,
    'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 2 n_cell n_bits i z]',
    'checks': checks,
}}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
