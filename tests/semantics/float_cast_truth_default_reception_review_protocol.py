#!/usr/bin/env python3
"""Float-cast conversion context, certified leaves and reference retirement."""
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
    return node('NScalarString', f'BYTES "{base64.b64encode(value.encode()).decode()}"')


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
    node('NExprUnaryMinus', ternary(float_cast(string('0.0')), constant('UnselectedReceive203'), integer(7))),
    cast(ternary(float_cast(string('0.5tail')), string('-11tail'), constant('UnselectedReceive203'))),
    cast(ternary(float_cast(ternary(constant('true'), string('1e999'), constant('UnselectedReceive203'))), string('13tail'), constant('UnselectedReceive203'))),
    ternary(float_cast(coalesce(constant('null'), node('NExprUnaryMinus', floating('0000000000000000')))),
            constant('UnselectedReceive203'), cast(node('NExprUnaryMinus', floating('43e0000000000000')))),
    ternary(float_cast(node('NExprCastBool', ternary(constant('true'), constant('true'), constant('UnselectedReceive203')))),
            cast(string('999999999999999999999999')), constant('UnselectedReceive203')),
]
contrast = cast(node('NExprBooleanNot', floating('3fe0000000000000')))


CATALOGUE = Path(__file__).with_name('float_cast_truth_default_reception_cases.json')
assert hashlib.sha256(CATALOGUE.read_bytes()).hexdigest() == 'd54eaef30252f49d7a4a925c9a9878719c525fdd5ed55f1a4be1a5f638200f06'
row = next(row for row in json.loads(CATALOGUE.read_text()) if row['id'] == 'float-cast-truth-precision-modes')
assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
source = row['source']
handler = source[:source.index('function valueFirstReceive203(')]
reference = source[source.index('function referenceReceive203('):source.index("set_error_handler('warningReceive203');")]
setup = source[source.index("set_error_handler('warningReceive203');"):source.index('$gotReceive203 = valueFirstReceive203(')]
start = source.index('$gotReceive203 = referenceReceive203(')
end = source.index('$xReceive203 = 1.5;', start)
leading = handler + reference + setup + source[start:end]
assert hashlib.sha256(leading.encode()).hexdigest() == '4640516fef5b3ca97154a1ae5b5c74eec94e3182b8449f33c07e6a7987551b08'

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
    '$call_target(S, $ptascii("deferredFloatNotReceive203"), eps) = (pfunction_contrast)',
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

# Original roots retain raw input truth, cast truth and numeric value distinctions.
checks.extend([
    'expression_select_a = NExprTernary expression_float_a expression_unused_a expression_seven_a metadata_select_a',
    'expression_float_a = NExprCastDouble expression_string_a metadata_float_a',
    '$lossy_optional_integer_leaf_truth(plenv_source, expression_string_a) = ((expression_string_a, true))',
    '$lossy_optional_integer_float_truth(expression_string_a, true) = false',
    '$lossy_optional_integer_condition(plenv_source, expression_float_a) = (false)',
    '$lossy_optional_integer_leaf_truth(plenv_source, expression_float_a) = ((expression_float_a, false))',
    'expression_b = NExprCastInt expression_select_b metadata_b',
    'expression_select_b = NExprTernary expression_float_b expression_string_b expression_unused_b metadata_select_b',
    'expression_float_b = NExprCastDouble expression_fraction_b metadata_float_b',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt expression_fraction_b metadata_b) = (0)',
    '$lossy_optional_integer_float_truth(expression_fraction_b, true) = true',
    '$lossy_optional_integer_condition(plenv_source, expression_float_b) = (true)',
    'expression_c = NExprCastInt expression_select_c metadata_c',
    'expression_select_c = NExprTernary expression_float_c expression_string_c expression_unused_c metadata_select_c',
    'expression_float_c = NExprCastDouble expression_inner_c metadata_float_c',
    'expression_inner_c = NExprTernary expression_true_c expression_overflow_c expression_unused_inner_c metadata_inner_c',
    '$lossy_optional_integer_leaf_truth(plenv_source, expression_inner_c) = ((expression_overflow_c, true))',
    '$lossy_optional_integer_condition(plenv_source, expression_float_c) = (true)',
    '$lossy_optional_integer_cast_leaf(plenv_source, expression_select_c) = (expression_string_c)',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt expression_string_c metadata_c) = (13)',
    'expression_d = NExprTernary expression_float_d expression_unused_d expression_minimum_d metadata_d',
    'expression_float_d = NExprCastDouble expression_coalesce_d metadata_float_d',
    'expression_coalesce_d = NExprBinaryOpCoalesce expression_null_d expression_zero_d metadata_coalesce_d',
    '$lossy_optional_integer_leaf_truth(plenv_source, expression_coalesce_d) = ((expression_zero_d, false))',
    '$lossy_optional_integer_float_literal(expression_zero_d) = (9223372036854775808)',
    '$lossy_optional_integer_leaf_truth(plenv_source, expression_float_d) = ((expression_float_d, false))',
    '$lossy_optional_integer_special(plenv_source, expression_float_d) = eps',
    'expression_e = NExprTernary expression_float_e expression_maximum_e expression_unused_e metadata_e',
    'expression_float_e = NExprCastDouble expression_boolean_e metadata_float_e',
    '$lossy_optional_integer_leaf_truth(plenv_source, expression_boolean_e) = ((expression_boolean_e, true))',
    '$lossy_optional_integer_float_truth(expression_boolean_e, true) = true',
    '$lossy_optional_integer_condition(plenv_source, expression_float_e) = (true)',
])

true, false, null = map(constant, ('true', 'false', 'null'))
unknown = constant('UnselectedReceive203')
zero, seven = map(integer, (0, 7))
nan = floating('7ff8000000000000')
fraction = floating('3fd0000000000000')
infinity = floating('7ff0000000000000')

# Only raw strings need new numeric parsing; their original byte truth can differ.
for text, truth in [
    ('00', 'false'), (' 0', 'false'), ('-0.0tail', 'false'),
    ('word', 'false'), ('NaN', 'false'), ('\0', 'false'),
    ('0.25suffix', 'true'), ('-.25suffix', 'true'),
    ('+1e999stuff', 'true'), ('1e-999', 'false'),
    ('0.5\0ignored', 'true'), ('3e-323', 'true'),
]:
    leaf = string(text); expression = float_cast(leaf)
    checks.extend([
        f'$lossy_optional_integer_leaf_truth(plenv_source, {leaf}) = (({leaf}, true))',
        f'$lossy_optional_integer_float_truth({leaf}, true) = {truth}',
        f'$lossy_optional_integer_condition(plenv_source, {expression}) = ({truth})',
        f'$lossy_optional_integer_leaf_truth(plenv_source, {expression}) = (({expression}, {truth}))',
    ])
for leaf, truth in [
    (null, 'false'), (false, 'false'), (true, 'true'), (zero, 'false'),
    (node('NExprUnaryMinus', integer(9223372036854775807)), 'true'),
    (floating('0000000000000000'), 'false'), (floating('8000000000000000'), 'false'),
    (fraction, 'true'), (infinity, 'true'),
    (node('NExprCastBool', string('0.0')), 'true'),
    (cast(string('0.25suffix')), 'false'),
]:
    expression = float_cast(leaf)
    checks.extend([
        f'$lossy_optional_integer_float_truth({leaf}, {truth}) = {truth}',
        f'$lossy_optional_integer_condition(plenv_source, {expression}) = ({truth})',
        f'$lossy_optional_integer_condition(plenv_source, {float_cast(expression)}) = ({truth})',
    ])
for child, truth in [
    (ternary(true, string('0.0'), unknown), 'false'),
    (ternary(string('0.0'), 'ABSENT', unknown), 'false'),
    (coalesce(string('word'), unknown), 'false'),
    (coalesce(null, string('0.25suffix')), 'true'),
    (ternary(false, nan, string('0.25suffix')), 'true'),
]:
    checks.append(f'$lossy_optional_integer_condition(plenv_source, {float_cast(child)}) = ({truth})')
for child in [
    unknown, nan, floating('fff8000000000000'),
    node('NExprCastBool', nan), coalesce(unknown, seven),
    ternary(unknown, string('0.0'), string('0.0')),
    ternary(true, nan, seven),
    binary('Concat', string('0'), integer(0)),
    node('NExprArray', 'SEQUENCE eps'),
]:
    checks.extend([
        f'$lossy_optional_integer_condition(plenv_source, {float_cast(child)}) = eps',
        f'$lossy_optional_integer_leaf_truth(plenv_source, {float_cast(child)}) = eps',
    ])
converted_zero = float_cast(null)
checks.extend([
    f'$lossy_optional_integer_special(plenv_source, {converted_zero}) = eps',
    f'$lossy_optional_integer_condition(plenv_source, {coalesce(converted_zero, unknown)}) = (false)',
    f'$lossy_optional_integer_condition(plenv_alias, {float_cast(constant("true"))}) = (false)',
    f'$lossy_optional_integer_condition(plenv_alias, {float_cast(constant("true", qualified=True))}) = (true)',
    f'$lossy_optional_integer_condition(plenv_null_alias, {float_cast(constant("null", qualified=True))}) = (false)',
    f'$lossy_optional_integer_default_in(plenv_source, {float_cast(seven)}) = eps',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(float_cast(fraction))}) = (0)',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(float_cast(infinity))}) = eps',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(node("NExprCastBool", float_cast(string("0.0"))))}) = (0)',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(node("NExprCastBool", float_cast(string("0.25suffix"))))}) = (1)',
])
# Cached truth must descend once through nested numeric casts and selected strings.
deep = string('0.0')
for _ in range(24):
    deep = float_cast(deep)
checks.append(f'$lossy_optional_integer_condition(plenv_source, {deep}) = (false)')
leaf = string('0.0'); deep = leaf
for _ in range(24):
    deep = ternary(deep, 'ABSENT', unknown)
checks.extend([
    f'$lossy_optional_integer_leaf_truth(plenv_source, {deep}) = (({leaf}, true))',
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
    '$lookup(S_done.ENV, $ptascii("gotReceive203")) = (n_got)',
    'S_done.STORE[n_got] = DEFINED (PINT 1)',
    r'$call_descriptors_valid(S_done) /\ $heap_valid($heap_graph(S_done))',
])

CASES = {'float-cast-truth-reference-leading': {
    'source': leading,
    'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 2 n_cell n_bits i z]',
    'checks': checks,
}}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
