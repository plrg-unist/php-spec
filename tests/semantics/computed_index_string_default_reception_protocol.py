#!/usr/bin/env python3
"""Computed integer string selectors retain declaration environments and receive authority."""
import base64
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('computed_index_string_default_reception_cases.json')
SOURCES = {}
for row in json.loads(CATALOGUE.read_text()):
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
    SOURCES[row['id']] = row['source']

# Fresh first-VAL front preserves the whole five-default declaration; source0.
full = SOURCES['computed-index-string-precision-modes']
setup = full.index("set_error_handler('warningReceive211');")
start = full.index('$gotReceive211 = valueFirstReceive211(')
end = full.index('$xReceive211 = 1.5;', start)
source = full[:full.index('function referenceFirstReceive211')] + full[setup:end]
assert hashlib.sha256(source.encode()).hexdigest() == 'd26439aa672fd6171c1e6ebcb13d6d410b5cf09097d7d6ce9952ebe4d0ea3db2'

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


def dimension(base, selector):
    return node('NExprArrayDimFetch', base, selector)


def string_cast(child):
    return node('NExprCastString', child)


patterns = [
    node('NExprUnaryMinus', conditional(dimension(string('10'), cast(string_cast(constant('YesReceive211')))), constant('UnselectedReceive211'), integer(7))),
    cast(conditional(binary('Concat', dimension(string('10'), binary('Plus', integer(1), integer(0))), string('.0')), string_cast(binary('Concat', binary('Concat', string_cast(binary('Minus', node('NExprUnaryMinus', integer(10)), integer(1))), string_cast(constant('false', qualified=True))), string('tail'))), constant('UnselectedReceive211'))),
    cast(conditional(float_cast(conditional(constant('true'), binary('Concat', dimension(string('10'), conditional(constant('NoReceive211'), constant('UnselectedReceive211'), binary('Plus', integer(0), integer(1)))), string('.5tail')), constant('UnselectedReceive211'))), binary('Concat', dimension(string('01'), binary('Div', integer(2), integer(2))), string('3tail')), constant('UnselectedReceive211'))),
    conditional(float_cast(binary('Coalesce', constant('null'), binary('Concat', dimension(string('10'), binary('Coalesce', constant('NilReceive211'), binary('Minus', integer(2), integer(1)))), string('.0')))), constant('UnselectedReceive211'), cast(string('-9223372036854775808tail'))),
    cast(conditional(constant('true'), binary('Concat', dimension(string('09'), conditional(constant('YesReceive211'), binary('Mod', integer(3), integer(2)), constant('UnselectedReceive211'))), string('9' * 23)), constant('UnselectedReceive211'))),
]

checks = [
    r'n_bits = 4609434218613702656 /\ i = 1',
    '$function_at(S.FUNCTIONS, porigin) = (pfunction)',
    'plenv_source = pfunction.ENV',
    r'plenv_source.NAMESPACE = eps /\ plenv_source.CONSTANTS = [($ptascii("YesReceive211"), $ptascii("true")), ($ptascii("NoReceive211"), $ptascii("false")), ($ptascii("NilReceive211"), $ptascii("null"))]',
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
    'expression_a = NExprUnaryMinus (NExprTernary (NExprArrayDimFetch expression_base_a expression_key_a metadata_dim_a) expression_unknown_a expression_seven metadata_select_a) metadata_a',
    '$lossy_optional_integer_default_in(plenv_source, expression_key_a) = (1)',
    '$lossy_optional_integer_string_in(plenv_source, expression_key_a) = eps',
    '$lossy_optional_integer_default(expression_key_a) = eps',
    '$lossy_optional_integer_default(expression_b) = ($(-11))',
    '$lossy_optional_integer_default(expression_c) = eps',
    '$lossy_optional_integer_default(expression_d) = eps',
    '$lossy_optional_integer_default(expression_e) = eps',
    'plenv_yes_false = plenv_source[.CONSTANTS = [($ptascii("YesReceive211"), $ptascii("false")), ($ptascii("NoReceive211"), $ptascii("false")), ($ptascii("NilReceive211"), $ptascii("null"))]]',
    '$lossy_optional_integer_default_in(plenv_yes_false, expression_a) = eps',
    '$lossy_optional_integer_default_in(plenv_yes_false, expression_e) = eps',
    '~$lossy_optional_integer_header(S, pfunction[.ENV = plenv_yes_false], pfunction.SIGNATURE.PARAMETERS, 0)',
    'plenv_no_true = plenv_source[.CONSTANTS = [($ptascii("YesReceive211"), $ptascii("true")), ($ptascii("NoReceive211"), $ptascii("true")), ($ptascii("NilReceive211"), $ptascii("null"))]]',
    '$lossy_optional_integer_default_in(plenv_no_true, expression_c) = eps',
    '~$lossy_optional_integer_header(S, pfunction[.ENV = plenv_no_true], pfunction.SIGNATURE.PARAMETERS, 0)',
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
yes, no, nil = map(constant, ('YesReceive211', 'NoReceive211', 'NilReceive211'))
unknown = constant('UnselectedReceive211')
# The selector's type is PINT, not a numeric-looking CASTSTRING projection.
for key, index in [
    (binary('Plus', integer(0), integer(1)), 1),
    (binary('Plus', integer(0), integer(0)), 0),
    (binary('Minus', integer(2), integer(1)), 1),
    (binary('Mul', integer(1), integer(1)), 1),
    (binary('Div', integer(2), integer(2)), 1),
    (binary('Mod', integer(3), integer(2)), 1),
    (binary('BitwiseAnd', integer(3), integer(1)), 1),
    (binary('ShiftRight', integer(2), integer(1)), 1),
    (cast(string('1tail')), 1),
    (cast(floating('3fe0000000000000')), 0),
    (cast(true), 1), (cast(false), 0), (cast(null), 0),
    (conditional(yes, integer(1), unknown), 1),
    (binary('Coalesce', nil, integer(1)), 1),
    (conditional(string('0.0'), integer(1), unknown), 1),
    (conditional(float_cast(string('0.0')), unknown, integer(0)), 0),
    (cast(string_cast(integer(1))), 1),
]:
    expression = dimension(string('019'), key)
    byte = 48 + index
    truth = 'true' if index else 'false'
    checks.extend([
        f'$lossy_optional_integer_default_in(plenv_source, {key}) = ({index})',
        f'$lossy_optional_integer_string_in(plenv_source, {key}) = eps',
        f'$lossy_optional_integer_string_in(plenv_source, {expression}) = ([{byte}])',
        f'$lossy_optional_integer_condition(plenv_source, {expression}) = ({truth})',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = ({index})',
    ])
for data, expected, truth in [(b'0', 48, 'false'), (b'\0', 0, 'true'), (b'\xff', 255, 'true'), (b'\xc3\xa9', 195, 'true')]:
    expression = dimension(string(data), binary('Plus', integer(0), integer(0)))
    checks.extend([
        f'$lossy_optional_integer_string({expression}) = ([{expected}])',
        f'$lossy_optional_integer_condition(plenv_source, {expression}) = ({truth})',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = (0)',
        f'$lossy_optional_integer_condition(plenv_source, {float_cast(expression)}) = (false)',
    ])
# Raw bool/null/float keys are distinct from explicit quiet int casts.
for key in [true, false, null, floating('0000000000000000'), floating('3ff0000000000000'),
            string('bad'), string('1.0'), string('-1'), string('9223372036854775808'),
            integer(-1), integer(2), integer(9223372036854775808),
            binary('Minus', integer(0), integer(1)), binary('Div', integer(5), integer(2)),
            binary('Plus', integer(9223372036854775807), integer(1)),
            cast(floating('7ff8000000000000')), cast(floating('7ff0000000000000')),
            conditional(true, floating('3ff0000000000000'), unknown),
            conditional(unknown, integer(1), integer(0)),
            node('NExprVariable', 'BYTES "aW5kZXg="'), node('NExprArray', 'SEQUENCE eps'), 'ABSENT']:
    expression = dimension(string('09'), key)
    checks.extend([
        f'$lossy_optional_integer_string_in(plenv_source, {expression}) = eps',
        f'$lossy_optional_integer_condition(plenv_source, {expression}) = eps',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = eps',
    ])
# Existing numeric-string key grammar and byte operators still compose.
for key in [string('01tail'), string('+1'), string(b'1\0tail')]:
    expression = dimension(string('09'), key)
    checks.append(f'$lossy_optional_integer_string_in(plenv_source, {expression}) = ([57])')
for base in [string_cast(integer(19)), binary('Concat', string('1'), string('9')),
             node('NExprBitwiseNot', string(b'\xff\xc6'))]:
    expression = dimension(base, binary('Plus', integer(0), integer(1)))
    checks.append(f'$lossy_optional_integer_string_in(plenv_source, {expression}) = ([57])')
# Preserve every promoted old207/208 helper input without replaying its campaign.
for base, key, byte, integer_value in [
    (string('09'), binary('Plus', integer(0), integer(1)), 57, 9),
    (string('09'), cast(string('1')), 57, 9),
    (string('x'), binary('Plus', integer(0), integer(0)), 120, 0),
]:
    expression = dimension(base, key)
    checks.extend([
        f'$lossy_optional_integer_string({expression}) = ([{byte}])',
        f'$lossy_optional_integer_condition($plempty(false), {expression}) = (true)',
        f'$lossy_optional_integer_default_in($plempty(false), {cast(expression)}) = ({integer_value})',
    ])
deep_key = binary('Plus', integer(0), integer(1))
for _ in range(16):
    deep_key = cast(dimension(string('01'), deep_key))
deep = dimension(string('09'), deep_key)
checks.extend([
    f'$lossy_optional_integer_default_in(plenv_source, {deep_key}) = (1)',
    f'$lossy_optional_integer_string_in(plenv_source, {deep}) = ([57])',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(deep)}) = (9)',
])
# All five contrasts are genuine compiler-deferred defaults in this source unit.
fixed_metadata = None
for suffix, function, pattern, projected in [
    ('floatnot', 'deferredFloatNotReceive211', cast(node('NExprBooleanNot', floating('3fe0000000000000'))), '(0)'),
    ('negative', 'deferredNegativeIndexReceive211', cast(dimension(string('10'), string('-1'))), 'eps'),
    ('floatindex', 'deferredFloatIndexReceive211', cast(dimension(string('10'), string('1.0'))), 'eps'),
    ('floatstring', 'deferredFloatStringReceive211', cast(string_cast(floating('3fe0000000000000'))), 'eps'),
    ('computednegative', 'deferredComputedNegativeIndexReceive211', cast(dimension(string('10'), binary('Minus', integer(0), integer(1)))), 'eps'),
]:
    checks.extend([
        f'$call_target(S, $ptascii("{function}"), eps) = (pfunction_{suffix})',
        f'pfunction_{suffix}.SIGNATURE.PARAMETERS = [psparam_{suffix}]',
        f'psparam_{suffix}.DEFAULT = PSDEFAULT expression_{suffix} "deferred"',
        f'expression_{suffix} = {pattern}',
        f'$lossy_optional_integer_default_in(pfunction_{suffix}.ENV, expression_{suffix}) = {projected}',
        f'$default_parameter_origin(S, pfunction_{suffix}.ORIGIN, 0) = PORIGIN n_unit_{suffix} pcpath_{suffix}',
        f'porigin_{suffix} = PORIGIN n_unit_{suffix} (pcpath_{suffix} ++ [PCFIELD 6])',
        f'$origin_node(S.SOURCES, porigin_{suffix}) = (expression_{suffix})',
        f'$default_at(pfunction_{suffix}.DEFAULTS, 0) = ({{INDEX 0, ORIGIN porigin_{suffix}, KIND PDDEFERRED}})',
        f'$compiled_read(S, porigin_{suffix}) = eps',
        f'~$lossy_optional_integer_header(S, pfunction_{suffix}, pfunction_{suffix}.SIGNATURE.PARAMETERS, 0)',
        f'~$lossy_optional_integer_tail(S, pfunction_{suffix}, [psparam_{suffix}[.DEFAULT = PSDEFAULT expression_{suffix} "int"]], 0)',
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
    '$lookup(psymboltable_global.ENV, $ptascii("xReceive211")) = (n_global)',
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
    '$lookup(S_done.ENV, $ptascii("gotReceive211")) = (n_got)',
    'S_done.STORE[n_got] = DEFINED (PINT 13)',
    r'$call_descriptors_valid(S_done) /\ $heap_valid($heap_graph(S_done))',
])

CASES = {'computed-index-string-default-omitted-tail': {
    'source': source,
    'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z]',
    'checks': checks,
}}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
