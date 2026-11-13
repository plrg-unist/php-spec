#!/usr/bin/env python3
"""String binary bitwise lengths, byte values and selected-reference retirement."""
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
    node('NExprUnaryMinus', ternary(binary('BitwiseAnd', string('0'), string(b'\xffsuffix')), constant('UnselectedReceive206'), integer(7))),
    cast(ternary(binary('BitwiseOr', string('0.0'), string(b'\0')),
                 binary('Concat', binary('BitwiseOr', string('-1'), string(b'\0')),
                        binary('BitwiseXor', string('1tail'), string(b'\0' * 5))), constant('UnselectedReceive206'))),
    cast(ternary(float_cast(ternary(constant('true'), binary('BitwiseAnd', string('0.5tail'), string(b'\xff' * 7)), constant('UnselectedReceive206'))),
                 binary('BitwiseOr', string('13tail'), string(b'\0' * 2)), constant('UnselectedReceive206'))),
    ternary(float_cast(coalesce(constant('null'), binary('BitwiseXor', bitnot(string('-0.0')), string(b'\xff' * 4)))),
            constant('UnselectedReceive206'), cast(binary('BitwiseAnd', string('-9223372036854775808tail'), string(b'\xff' * 24)))),
    cast(ternary(constant('true'), binary('BitwiseXor', string('999999999999999999999999'), string(b'\0' * 24)), constant('UnselectedReceive206'))),
]
contrast = cast(node('NExprBooleanNot', floating('3fe0000000000000')))


CATALOGUE = Path(__file__).with_name('bitwise_string_default_reception_cases.json')
assert hashlib.sha256(CATALOGUE.read_bytes()).hexdigest() == '899673dff32ea5e832780597273dca482888df9ab84f40d74b88799236659888'
row = next(row for row in json.loads(CATALOGUE.read_text()) if row['id'] == 'bitwise-string-precision-modes')
assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
source = row['source']
handler = source[:source.index('function valueFirstReceive206(')]
reference = source[source.index('function referenceReceive206('):source.index("set_error_handler('warningReceive206');")]
setup = source[source.index("set_error_handler('warningReceive206');"):source.index('$gotReceive206 = valueFirstReceive206(')]
start = source.index('$gotReceive206 = referenceReceive206(')
end = source.index('$xReceive206 = 1.5;', start)
leading = handler + reference + setup + source[start:end]
assert hashlib.sha256(leading.encode()).hexdigest() == '9de119bfd937f322b8bc09171389e7665389a1ff68d57162a05fe3305ab7bb85'

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
    '$call_target(S, $ptascii("deferredFloatNotReceive206"), eps) = (pfunction_contrast)',
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

# Original roots distinguish byte lengths, selected syntax and cast context.
checks.extend([
    'expression_select_a = NExprTernary expression_and_a expression_unused_a expression_seven_a metadata_select_a',
    '$lossy_optional_integer_string(expression_and_a) = ([48])',
    '$lossy_optional_integer_condition(plenv_source, expression_and_a) = (false)',
    'expression_b = NExprCastInt expression_select_b metadata_b',
    'expression_select_b = NExprTernary expression_or_b expression_string_b expression_unused_b metadata_select_b',
    '$lossy_optional_integer_string(expression_or_b) = ([48, 46, 48])',
    '$lossy_optional_integer_leaf_truth(plenv_source, expression_or_b) = ((expression_or_b, true))',
    '$lossy_optional_integer_float_truth(expression_or_b, true) = false',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt expression_or_b metadata_b) = (0)',
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
unknown = constant('UnselectedReceive206')
nan = floating('7ff8000000000000')
operators = ('BitwiseAnd', 'BitwiseOr', 'BitwiseXor')

# Expected byte lists are explicit; both orders exercise length asymmetry.
examples = [
    (b'', b'0', ([], [48], []), ('false', 'false', 'false')),
    (b'\xf0\0\xff', b'\x0f\xff', ([0, 0], [255, 255, 255], [255, 255]), ('true', 'true', 'true')),
    (b'0.0', b'\xff', ([48], [255, 46, 48], [207]), ('false', 'true', 'true')),
    (b'13tail', b'\0\0', ([0, 0], [49, 51, 116, 97, 105, 108], [49, 51]), ('true', 'true', 'true')),
]
for left, right, results, truths in examples:
    for kind, expected, truth in zip(operators, results, truths):
        for first, second in ((left, right), (right, left)):
            expression = binary(kind, string(first), string(second))
            data = '[' + ', '.join(map(str, expected)) + ']' if expected else 'eps'
            checks.extend([
                f'$lossy_optional_integer_string({expression}) = ({data})',
                f'$lossy_optional_integer_condition(plenv_source, {expression}) = ({truth})',
            ])
for kind in operators:
    expression = binary(kind, string(''), string(''))
    checks.extend([
        f'$lossy_optional_integer_string({expression}) = (eps)',
        f'$lossy_optional_integer_condition(plenv_source, {expression}) = (false)',
    ])
zeros = [
    binary('BitwiseAnd', string('0.0'), string(b'\xff' * 3)),
    binary('BitwiseOr', string('0.0'), string(b'\0')),
    binary('BitwiseXor', string('0.0'), string(b'\0' * 3)),
]
for expression in zeros:
    checks.extend([
        f'$lossy_optional_integer_leaf_truth(plenv_source, {expression}) = (({expression}, true))',
        f'$lossy_optional_integer_default_in(plenv_source, {expression}) = eps',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = (0)',
        f'$lossy_optional_integer_condition(plenv_source, {float_cast(expression)}) = (false)',
        f'$lossy_optional_integer_condition(plenv_source, {float_cast(node("NExprCastBool", expression))}) = (true)',
    ])
for selected, leaf, truth in [
    (ternary(true, zeros[0], unknown), zeros[0], 'true'),
    (ternary(zeros[1], 'ABSENT', unknown), zeros[1], 'true'),
    (coalesce(null, zeros[2]), zeros[2], 'true'),
]:
    checks.extend([
        f'$lossy_optional_integer_leaf_truth(plenv_source, {selected}) = (({leaf}, {truth}))',
        f'$lossy_optional_integer_condition(plenv_source, {float_cast(selected)}) = (false)',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(selected)}) = (0)',
    ])
for kind in operators:
    empty = binary(kind, string(''), string(''))
    selected = coalesce(empty, unknown)
    checks.extend([
        f'$lossy_optional_integer_leaf_truth(plenv_source, {selected}) = (({empty}, false))',
        f'$lossy_optional_integer_condition(plenv_source, {float_cast(selected)}) = (false)',
    ])
# Unknown and other-type children cannot be ignored even beside an empty string.
for child in [unknown, integer(0), false, nan,
              node('NExprCastString', unknown), ternary(true, string('0'), unknown)]:
    for kind in operators:
        for first, second in ((string(''), child), (child, string(''))):
            expression = binary(kind, first, second)
            checks.extend([
                f'$lossy_optional_integer_string({expression}) = eps',
                f'$lossy_optional_integer_condition(plenv_source, {expression}) = eps',
                f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = eps',
            ])
# Long bitwise results remain numeric, with no byte certificate or coercion change.
for kind, value in zip(operators, (1, 3, 2)):
    expression = binary(kind, integer(1), integer(3))
    checks.extend([
        f'$lossy_optional_integer_string({expression}) = eps',
        f'$lossy_optional_integer_default_in(plenv_source, {expression}) = ({value})',
        f'$lossy_optional_integer_condition(plenv_source, {expression}) = (true)',
    ])
composite = binary('BitwiseXor', bitnot(string('-0.0')), string(b'\xff' * 4))
infinite = binary('BitwiseOr', string('1e999'), string(b'\0'))
fraction = binary('BitwiseXor', string('0.5tail'), string(b'\0' * 7))
checks.extend([
    f'$lossy_optional_integer_string({composite}) = ([45, 48, 46, 48])',
    f'$lossy_optional_integer_condition(plenv_source, {float_cast(composite)}) = (false)',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(infinite)}) = (0)',
    f'$lossy_optional_integer_condition(plenv_alias, {float_cast(ternary(constant("true"), zeros[0], fraction))}) = (true)',
    f'$lossy_optional_integer_condition(plenv_alias, {float_cast(ternary(constant("true", qualified=True), zeros[0], fraction))}) = (false)',
])
# Recursion descends through the AST even when OR copies an unchanged suffix.
deep = string('0')
for _ in range(24):
    deep = binary('BitwiseOr', deep, string(''))
checks.extend([
    f'$lossy_optional_integer_string({deep}) = ([48])',
    f'$lossy_optional_integer_condition(plenv_source, {deep}) = (false)',
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
    '$lookup(S_done.ENV, $ptascii("gotReceive206")) = (n_got)',
    'S_done.STORE[n_got] = DEFINED (PINT 1)',
    r'$call_descriptors_valid(S_done) /\ $heap_valid($heap_graph(S_done))',
])

CASES = {'bitwise-string-reference-leading': {
    'source': leading,
    'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 2 n_cell n_bits i z]',
    'checks': checks,
}}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
