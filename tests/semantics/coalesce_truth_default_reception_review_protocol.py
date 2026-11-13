#!/usr/bin/env python3
"""Coalesce nullness, selected-leaf truth and real reference retirement."""
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


patterns = [
    node('NExprUnaryMinus', ternary(coalesce(constant('false'), constant('UnselectedReceive202')),
                                   constant('UnselectedReceive202'), integer(7))),
    cast(ternary(coalesce(constant('null'), ternary(constant('true'), string('0'), constant('UnselectedReceive202'))),
                 'ABSENT', string('-11tail'))),
    cast(ternary(coalesce(ternary(constant('false'), constant('UnselectedReceive202'), string('13tail')),
                           constant('UnselectedReceive202')), 'ABSENT', constant('UnselectedReceive202'))),
    ternary(coalesce(ternary(constant('true'), constant('null'), constant('UnselectedReceive202')), constant('true')),
            cast(node('NExprUnaryMinus', floating('43e0000000000000'))), constant('UnselectedReceive202')),
    cast(ternary(coalesce(ternary(constant('false'), constant('UnselectedReceive202'),
                                   node('NExprUnaryPlus', floating('7ff0000000000000'))), constant('UnselectedReceive202')),
                 string('999999999999999999999999'), constant('UnselectedReceive202'))),
]
contrast = cast(node('NExprBooleanNot', floating('3fe0000000000000')))


CATALOGUE = Path(__file__).with_name('coalesce_truth_default_reception_cases.json')
assert hashlib.sha256(CATALOGUE.read_bytes()).hexdigest() == 'b3384d7657f9cafadf7ea918bb114674a6d67bc03362774d13624ffe2e5d04db'
row = next(row for row in json.loads(CATALOGUE.read_text()) if row['id'] == 'coalesce-truth-precision-modes')
assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
source = row['source']
handler = source[:source.index('function valueFirstReceive202(')]
reference = source[source.index('function referenceReceive202('):source.index("set_error_handler('warningReceive202');")]
setup = source[source.index("set_error_handler('warningReceive202');"):source.index('$gotReceive202 = valueFirstReceive202(')]
start = source.index('$gotReceive202 = referenceReceive202(')
end = source.index('$xReceive202 = 1.5;', start)
leading = handler + reference + setup + source[start:end]
assert hashlib.sha256(leading.encode()).hexdigest() == '2975b980aaec7435fa0f03638c53936b807e4321306ee627330836e0eccb43ef'

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
    'plenv_alias = plenv_source[.CONSTANTS = [($ptascii("true"), $ptascii("null"))]]',
    '$lossy_optional_integer_default_in(plenv_alias, expression_b) = eps',
    '$lossy_optional_integer_default_in(plenv_alias, expression_d) = eps',
    '~$lossy_optional_integer_header(S, pfunction[.ENV = plenv_alias], pfunction.SIGNATURE.PARAMETERS, 0)',
    'plenv_false_alias = plenv_source[.CONSTANTS = [($ptascii("false"), $ptascii("null"))]]',
    '$lossy_optional_integer_default_in(plenv_false_alias, expression_a) = eps',
    '~$lossy_optional_integer_header(S, pfunction[.ENV = plenv_false_alias], pfunction.SIGNATURE.PARAMETERS, 0)',
    '$call_target(S, $ptascii("deferredFloatNotReceive202"), eps) = (pfunction_contrast)',
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

# Actual selected leaves distinguish nullness, truth and later cast eligibility.
checks.extend([
    'expression_c = NExprCastInt expression_short_c metadata_c',
    'expression_short_c = NExprTernary expression_coalesce_c ABSENT expression_unused_c metadata_short_c',
    'expression_coalesce_c = NExprBinaryOpCoalesce expression_select_c expression_unused_cc metadata_coalesce_c',
    'expression_select_c = NExprTernary expression_false_c expression_unused_select_c expression_string_c metadata_select_c',
    '$lossy_optional_integer_leaf_truth(plenv_source, expression_coalesce_c) = ((expression_string_c, true))',
    '$lossy_optional_integer_leaf_truth(plenv_source, expression_short_c) = ((expression_string_c, true))',
    '$lossy_optional_integer_cast_leaf(plenv_source, expression_short_c) = (expression_string_c)',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt expression_string_c metadata_c) = (13)',
    'expression_d = NExprTernary expression_coalesce_d expression_min_d expression_unused_d metadata_d',
    'expression_coalesce_d = NExprBinaryOpCoalesce expression_select_d expression_true_d metadata_coalesce_d',
    'expression_select_d = NExprTernary expression_condition_d expression_null_d expression_unused_select_d metadata_select_d',
    '$lossy_optional_integer_leaf_truth(plenv_source, expression_select_d) = ((expression_null_d, false))',
    '$lossy_optional_integer_special(plenv_source, expression_null_d) = (PNULL)',
    '$lossy_optional_integer_leaf_truth(plenv_source, expression_coalesce_d) = ((expression_true_d, true))',
    'expression_e = NExprCastInt expression_select_e metadata_e',
    'expression_select_e = NExprTernary expression_coalesce_e expression_string_e expression_unused_e metadata_select_e',
    'expression_coalesce_e = NExprBinaryOpCoalesce expression_inf_select expression_unused_ee metadata_coalesce_e',
    'expression_inf_select = NExprTernary expression_false_e expression_unused_inf expression_inf_e metadata_inf_select',
    '$lossy_optional_integer_leaf_truth(plenv_source, expression_coalesce_e) = ((expression_inf_e, true))',
    '$lossy_optional_integer_float_literal(expression_inf_e) = (9218868437227405312)',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt expression_inf_e metadata_e) = eps',
])

true, false, null = map(constant, ('true', 'false', 'null'))
unknown = constant('UnselectedReceive202')
seven, thirteen, zero = map(integer, (7, 13, 0))
string_thirteen = string('13tail')
nan = floating('7ff8000000000000')
infinity = floating('7ff0000000000000')
fraction = node('NExprUnaryMinus', floating('3fe0000000000000'))
large = floating('43e0000000000000')

# A known falsy value is nonnull and must retain its own original expression.
for leaf, truth in [
    (false, 'false'), (true, 'true'), (zero, 'false'), (seven, 'true'),
    (string(''), 'false'), (string('0'), 'false'), (string('00'), 'true'),
    (string_thirteen, 'true'), (floating('0000000000000000'), 'false'),
    (floating('8000000000000000'), 'false'), (fraction, 'true'),
    (infinity, 'true'), (large, 'true'),
    (node('NExprCastBool', null), 'false'),
    (node('NExprBooleanNot', null), 'true'), (cast(fraction), 'false'),
]:
    expression = coalesce(leaf, unknown)
    checks.extend([
        f'$lossy_optional_integer_leaf_truth(plenv_source, {expression}) = (({leaf}, {truth}))',
        f'$lossy_optional_integer_condition(plenv_source, {expression}) = ({truth})',
    ])
for selected, truth in [(false, 'false'), (null, 'false'), (string_thirteen, 'true'), (infinity, 'true')]:
    checks.append(f'$lossy_optional_integer_leaf_truth(plenv_source, {coalesce(null, selected)}) = (({selected}, {truth}))')
for left, selected, truth in [
    (ternary(true, null, unknown), seven, 'true'),
    (ternary(true, false, null), false, 'false'),
    (ternary(false, unknown, string_thirteen), string_thirteen, 'true'),
    (ternary(false, unknown, infinity), infinity, 'true'),
    (ternary(string_thirteen, 'ABSENT', unknown), string_thirteen, 'true'),
]:
    right = seven if selected == seven else unknown
    checks.append(f'$lossy_optional_integer_leaf_truth(plenv_source, {coalesce(left, right)}) = (({selected}, {truth}))')
for expression in [
    unknown, coalesce(unknown, true), coalesce(null, unknown),
    coalesce(nan, seven), coalesce(null, nan),
    ternary(unknown, true, true), ternary(true, nan, seven),
    coalesce(node('NExprArray', 'SEQUENCE eps'), false),
    coalesce(binary('Concat', string('0'), string('0')), false),
]:
    checks.extend([
        f'$lossy_optional_integer_leaf_truth(plenv_source, {expression}) = eps',
        f'$lossy_optional_integer_condition(plenv_source, {expression}) = eps',
    ])
checks.extend([
    f'$lossy_optional_integer_leaf_truth(plenv_source, {coalesce(false, nan)}) = (({false}, false))',
    f'$lossy_optional_integer_condition(plenv_source, {ternary(false, nan, zero)}) = (false)',
    f'$lossy_optional_integer_condition(plenv_source, {ternary(true, seven, nan)}) = (true)',
    f'$lossy_optional_integer_leaf_truth(plenv_alias, {coalesce(constant("true"), seven)}) = (({seven}, true))',
    f'$lossy_optional_integer_leaf_truth(plenv_false_alias, {coalesce(constant("false"), seven)}) = (({seven}, true))',
    f'$lossy_optional_integer_condition(plenv_alias, {coalesce(constant("true", qualified=True), unknown)}) = (true)',
    f'$lossy_optional_integer_selection_shape({ternary(true, seven, unknown)})',
    f'$lossy_optional_integer_selection_shape({coalesce(false, unknown)})',
    f'~$lossy_optional_integer_selection_shape({cast(seven)})',
    f'$lossy_optional_integer_default_in(plenv_source, {coalesce(false, unknown)}) = eps',
    f'$lossy_optional_integer_default_in(plenv_source, {coalesce(null, true)}) = eps',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(coalesce(false, unknown))}) = (0)',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(coalesce(infinity, seven))}) = eps',
    f'$lossy_optional_integer_condition(plenv_source, {coalesce(zero, unknown)}) = (false)',
    f'$lossy_optional_integer_default_in(plenv_source, {coalesce(zero, unknown)}) = (0)',
    f'$lossy_optional_integer_default_in(plenv_source, {ternary(true, seven, unknown)}) = (7)',
    f'$lossy_optional_integer_default_in(plenv_source, {ternary(true, false, unknown)}) = eps',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(ternary(string_thirteen, "ABSENT", unknown))}) = (13)',
])
# Fresh assertions cover the maintained Boolean-coalesce promotions, without replay.
converted = node('NExprCastBool', coalesce(node('NExprCastBool', string('0')), unknown))
checks.extend([
    f'$lossy_optional_integer_condition(plenv_source, {converted}) = (false)',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(converted)}) = (0)',
    f'$lossy_optional_integer_condition(plenv_source, {coalesce(false, unknown)}) = (false)',
    f'$lossy_optional_integer_condition(plenv_source, {node("NExprCastBool", coalesce(false, unknown))}) = (false)',
])
# Cached certificates must stay linear across repeated left and shorthand selection.
deep_left = false
for _ in range(24):
    deep_left = coalesce(deep_left, unknown)
checks.append(f'$lossy_optional_integer_leaf_truth(plenv_source, {deep_left}) = (({false}, false))')
deep_short = string_thirteen
for _ in range(24):
    deep_short = ternary(deep_short, 'ABSENT', unknown)
checks.append(f'$lossy_optional_integer_leaf_truth(plenv_source, {deep_short}) = (({string_thirteen}, true))')

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
    '$lookup(S_done.ENV, $ptascii("gotReceive202")) = (n_got)',
    'S_done.STORE[n_got] = DEFINED (PINT 1)',
    r'$call_descriptors_valid(S_done) /\ $heap_valid($heap_graph(S_done))',
])

CASES = {'coalesce-truth-reference-leading': {
    'source': leading,
    'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 2 n_cell n_bits i z]',
    'checks': checks,
}}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
