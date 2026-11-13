#!/usr/bin/env python3
"""Boolean cast default authority, boundary controls and reference retirement."""
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


def binary(kind, left, right):
    return node('NExprBinaryOp' + kind, left, right)


def cast(child):
    return node('NExprCastInt', child)


def logical_not(child):
    return node('NExprBooleanNot', child)


def string(value):
    return node('NScalarString', f'BYTES "{base64.b64encode(value.encode()).decode()}"')


def ternary(condition, selected, alternative):
    return node('NExprTernary', condition, selected, alternative)


def boolean_cast(child):
    return node('NExprCastBool', child)


patterns = [
    binary('Plus', node('NExprUnaryMinus', integer(7)), cast(boolean_cast(string('0')))),
    binary('Plus', node('NExprUnaryMinus', integer(12)), cast(boolean_cast(string('00')))),
    binary('Plus', integer(12), cast(boolean_cast(node('NExprUnaryMinus', node('NScalarFloat', 'FLOAT "3fe0000000000000"'))))),
    ternary(boolean_cast(node('NExprUnaryPlus', node('NExprUnaryMinus', node('NScalarFloat', 'FLOAT "0000000000000000"')))),
            constant('UnselectedReceive200'), cast(node('NExprUnaryMinus', node('NScalarFloat', 'FLOAT "43e0000000000000"')))),
    cast(ternary(boolean_cast(node('NExprUnaryPlus', node('NScalarFloat', 'FLOAT "7ff0000000000000"'))),
                 string('999999999999999999999999'), constant('UnselectedReceive200'))),
]
contrast = cast(node('NExprBooleanNot', node('NScalarFloat', 'FLOAT "3fe0000000000000"')))


CATALOGUE = Path(__file__).with_name('boolean_cast_default_reception_cases.json')
assert hashlib.sha256(CATALOGUE.read_bytes()).hexdigest() == 'e93bc22594aa218a968565ef65164b4b26b2f80235cc34d6591f9de89c03a629'
row = next(row for row in json.loads(CATALOGUE.read_text()) if row['id'] == 'boolean-cast-precision-modes')
assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
source = row['source']
handler = source[:source.index('function valueFirstReceive200(')]
reference = source[source.index('function referenceReceive200('):source.index("set_error_handler('warningReceive200');")]
setup = source[source.index("set_error_handler('warningReceive200');"):source.index('$gotReceive200 = valueFirstReceive200(')]
start = source.index('$gotReceive200 = referenceReceive200(')
end = source.index('$xReceive200 = 1.5;', start)
# Exact five-default declaration, unused deferred contrast and one leading REF call, source0.
leading = handler + reference + setup + source[start:end]
assert hashlib.sha256(leading.encode()).hexdigest() == '039352e19dd630d41878cbb329080142544814602a823a14de3c1e4d848f6094'

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
    'expression_a = NExprBinaryOpPlus expression_negative_seven expression_cast_a metadata_a',
    'plenv_alias = plenv_source[.CONSTANTS = [($ptascii("true"), $ptascii("false"))]]',
    '$lossy_optional_integer_header(S, pfunction[.ENV = plenv_alias], pfunction.SIGNATURE.PARAMETERS, 0)',
    '$call_target(S, $ptascii("deferredFloatNotReceive200"), eps) = (pfunction_contrast)',
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
    'S_wrong_type = S[.POOLS = [{UNIT n_unit, CONSTANTS ([(PCONSTANT (pcpath_c ++ [PCFIELD 6]) (PBOOL true))])}]]',
    '$compiled_read(S_wrong_type, porigin_c) = (PBOOL true)',
    '~$lossy_optional_integer_tail(S_wrong_type, pfunction, [psparam_c], 2)',
])


def floating(bits):
    return node('NScalarFloat', f'FLOAT "{bits}"')


one, seven, two = map(integer, (1, 7, 2))
unknown = constant('UnselectedReceive200')
fraction = node('NExprUnaryMinus', floating('3fe0000000000000'))
large = floating('43e0000000000000')
infinity = floating('7ff0000000000000')
nan = floating('7ff8000000000000')

# Explicit bool preserves PHP truth rather than performing an intermediate int cast.
for leaf, expected in [
    (constant('null'), 0), (string('0'), 0), (string('00'), 1),
    (string('nonnumeric'), 1), (fraction, 1),
    (floating('8000000000000000'), 0), (large, 1), (infinity, 1),
]:
    checks.append(f'$lossy_optional_integer_default_in(plenv_source, {cast(boolean_cast(leaf))}) = ({expected})')
checks.extend([
    f'$lossy_optional_integer_condition(plenv_source, {boolean_cast(one)}) = (true)',
    f'$lossy_optional_integer_default_in(plenv_source, {boolean_cast(one)}) = eps',
    f'$lossy_optional_integer_boolean_shape({boolean_cast(one)})',
    f'~$lossy_optional_integer_boolean_shape({cast(seven)})',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(seven)}) = (7)',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(binary("Spaceship", one, two))}) = ($(-1))',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(string("nonnumeric"))}) = (0)',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(fraction)}) = (0)',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(large)}) = eps',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(infinity)}) = eps',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(boolean_cast(boolean_cast(string("0"))))}) = (0)',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(boolean_cast(boolean_cast(seven)))}) = (1)',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(boolean_cast(cast(fraction)))}) = (0)',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(logical_not(boolean_cast(fraction)))}) = (0)',
    f'$lossy_optional_integer_default_in(plenv_alias, {cast(boolean_cast(constant("true")))}) = (0)',
    f'$lossy_optional_integer_default_in(plenv_alias, {cast(boolean_cast(constant("true", qualified=True)))}) = (1)',
    f'$lossy_optional_integer_default_in(plenv_alias, {cast(boolean_cast(string("true")))}) = (1)',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(binary("Coalesce", boolean_cast(string("0")), unknown))}) = (0)',
])
for expression, expected in [
    (binary('BooleanAnd', string('0'), unknown), 0),
    (binary('LogicalOr', string('00'), nan), 1),
    (ternary(boolean_cast(fraction), integer(13), unknown), 1),
    (binary('Coalesce', integer(0), unknown), 0),
]:
    checks.append(f'$lossy_optional_integer_default_in(plenv_source, {cast(boolean_cast(expression))}) = ({expected})')
for leaf in [
    nan, floating('fff8000000000000'), unknown,
    node('NExprArray', 'SEQUENCE eps'), binary('Concat', string('0'), string('0')),
    binary('LogicalXor', string('0'), unknown),
]:
    converted = boolean_cast(leaf)
    checks.extend([
        f'$lossy_optional_integer_condition(plenv_source, {converted}) = eps',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(converted)}) = eps',
    ])
converted_coalesce = boolean_cast(binary('Coalesce', boolean_cast(string('0')), unknown))
checks.extend([
    f'$lossy_optional_integer_condition(plenv_source, {converted_coalesce}) = (false)',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(converted_coalesce)}) = (0)',
])
converted = boolean_cast(ternary(constant('true'), string('12tail'), unknown))
checks.extend([
    f'$lossy_optional_integer_condition(plenv_source, {converted}) = (true)',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(converted)}) = (1)',
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
    '$lookup(S_done.ENV, $ptascii("gotReceive200")) = (n_got)',
    'S_done.STORE[n_got] = DEFINED (PINT 1)',
    r'$call_descriptors_valid(S_done) /\ $heap_valid($heap_graph(S_done))',
])

CASES = {'boolean-cast-reference-leading': {
    'source': leading,
    'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 2 n_cell n_bits i z]',
    'checks': checks,
}}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
