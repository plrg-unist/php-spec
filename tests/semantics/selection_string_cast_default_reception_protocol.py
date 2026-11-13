#!/usr/bin/env python3
"""Selected scalar string casts retain typed leaves and receive authority."""
import base64
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('selection_string_cast_default_reception_cases.json')
SOURCES = {}
for row in json.loads(CATALOGUE.read_text()):
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
    SOURCES[row['id']] = row['source']

# Fresh first-VAL front preserves the whole five-default declaration; source0.
full = SOURCES['selection-string-cast-precision-modes']
setup = full.index("set_error_handler('warningReceive212');")
start = full.index('$gotReceive212 = valueFirstReceive212(')
end = full.index('$xReceive212 = 1.5;', start)
source = full[:full.index('function referenceFirstReceive212')] + full[setup:end]
assert hashlib.sha256(source.encode()).hexdigest() == 'b76fa0afddbf3b842259d009ec739738e5ee28876300663331169821f46b4354'

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
    node('NExprUnaryMinus', conditional(string_cast(conditional(constant('YesReceive212'), binary('Coalesce', constant('NoReceive212'), constant('UnselectedReceive212')), constant('UnselectedReceive212'))), constant('UnselectedReceive212'), integer(7))),
    cast(conditional(string_cast(conditional(constant('YesReceive212'), string('0.0'), constant('UnselectedReceive212'))), string_cast(conditional(constant('NoReceive212'), constant('UnselectedReceive212'), binary('Concat', binary('Concat', string_cast(binary('Minus', node('NExprUnaryMinus', integer(10)), integer(1))), string_cast(constant('false', qualified=True))), string('tail')))), constant('UnselectedReceive212'))),
    cast(conditional(float_cast(conditional(constant('true'), string_cast(binary('Coalesce', constant('NilReceive212'), conditional(constant('NoReceive212'), 'ABSENT', string('.5tail')))), constant('UnselectedReceive212'))), binary('Concat', string_cast(conditional(constant('NoReceive212'), constant('UnselectedReceive212'), constant('YesReceive212'))), string('3tail')), constant('UnselectedReceive212'))),
    conditional(float_cast(binary('Coalesce', constant('null'), string_cast(conditional(binary('Concat', string_cast(conditional(constant('YesReceive212'), constant('NilReceive212'), constant('UnselectedReceive212'))), string('0.0')), 'ABSENT', constant('UnselectedReceive212'))))), constant('UnselectedReceive212'), cast(string('-9223372036854775808tail'))),
    cast(string_cast(conditional(constant('YesReceive212'), conditional(constant('NoReceive212'), 'ABSENT', string('9' * 24)), constant('UnselectedReceive212')))),
]

checks = [
    r'n_bits = 4609434218613702656 /\ i = 1',
    '$function_at(S.FUNCTIONS, porigin) = (pfunction)',
    'plenv_source = pfunction.ENV',
    r'plenv_source.NAMESPACE = eps /\ plenv_source.CONSTANTS = [($ptascii("YesReceive212"), $ptascii("true")), ($ptascii("NoReceive212"), $ptascii("false")), ($ptascii("NilReceive212"), $ptascii("null"))]',
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
    'expression_a = NExprUnaryMinus (NExprTernary (NExprCastString expression_selection_a metadata_cast_a) expression_unknown_a expression_seven metadata_select_a) metadata_a',
    '$lossy_optional_integer_selection_shape(expression_selection_a)',
    '$lossy_optional_integer_default_in(plenv_source, expression_selection_a) = eps',
    '$lossy_optional_integer_string_in(plenv_source, expression_selection_a) = eps',
    'expression_selection_a = NExprTernary expression_yes_a expression_coalesce_a expression_unknown_inner_a metadata_selection_a',
    'expression_coalesce_a = NExprBinaryOpCoalesce expression_no_a expression_unknown_coalesce_a metadata_coalesce_a',
    '$lossy_optional_integer_cast_leaf(plenv_source, expression_selection_a) = (expression_no_a)',
    '$lossy_optional_integer_special(plenv_source, expression_no_a) = (PBOOL false)',
    '$lossy_optional_integer_string_in(plenv_source, NExprCastString expression_selection_a metadata_cast_a) = (eps)',
    '~$lossy_optional_integer_header(S, pfunction[.ENV = $plempty(false)], pfunction.SIGNATURE.PARAMETERS, 0)',
    'plenv_yes_false = plenv_source[.CONSTANTS = [($ptascii("YesReceive212"), $ptascii("false")), ($ptascii("NoReceive212"), $ptascii("false")), ($ptascii("NilReceive212"), $ptascii("null"))]]',
    '$lossy_optional_integer_default_in(plenv_yes_false, expression_a) = eps',
    '~$lossy_optional_integer_header(S, pfunction[.ENV = plenv_yes_false], pfunction.SIGNATURE.PARAMETERS, 0)',
    'plenv_no_true = plenv_source[.CONSTANTS = [($ptascii("YesReceive212"), $ptascii("true")), ($ptascii("NoReceive212"), $ptascii("true")), ($ptascii("NilReceive212"), $ptascii("null"))]]',
    '$lossy_optional_integer_default_in(plenv_no_true, expression_a) = eps',
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
yes, no, nil = map(constant, ('YesReceive212', 'NoReceive212', 'NilReceive212'))
unknown = constant('UnselectedReceive212')
# Selected noninteger leaves keep their type until CASTSTRING formats that leaf.
for child, data, truth, numeric_truth, result in [
    (conditional(yes, string(''), unknown), b'', 'false', 'false', '0'),
    (conditional(yes, no, unknown), b'', 'false', 'false', '0'),
    (conditional(yes, nil, unknown), b'', 'false', 'false', '0'),
    (conditional(no, unknown, yes), b'1', 'true', 'true', '1'),
    (conditional(yes, string('0'), unknown), b'0', 'false', 'false', '0'),
    (conditional(yes, string('0.0'), unknown), b'0.0', 'true', 'false', '0'),
    (conditional(yes, string(b'\0'), unknown), b'\0', 'true', 'false', '0'),
    (conditional(no, unknown, string(b'\xff')), b'\xff', 'true', 'false', '0'),
    (conditional(yes, string('-11tail'), unknown), b'-11tail', 'true', 'true', '$(-11)'),
    (binary('Coalesce', nil, string('13tail')), b'13tail', 'true', 'true', '13'),
    (binary('Coalesce', no, unknown), b'', 'false', 'false', '0'),
    (binary('Coalesce', yes, unknown), b'1', 'true', 'true', '1'),
    (conditional(no, 'ABSENT', string('0.0')), b'0.0', 'true', 'false', '0'),
    (conditional(string('0.0'), 'ABSENT', unknown), b'0.0', 'true', 'false', '0'),
    (conditional(string(b'\0'), 'ABSENT', unknown), b'\0', 'true', 'false', '0'),
    (conditional(string('0.0'), string('-11tail'), unknown), b'-11tail', 'true', 'true', '$(-11)'),
    (conditional(float_cast(string('0.0')), unknown, string('13tail')), b'13tail', 'true', 'true', '13'),
]:
    expression = string_cast(child)
    expected = '[' + ', '.join(map(str, data)) + ']' if data else 'eps'
    checks.extend([
        f'$lossy_optional_integer_selection_shape({child})',
        f'$lossy_optional_integer_default_in(plenv_source, {child}) = eps',
        f'$lossy_optional_integer_string_in(plenv_source, {child}) = eps',
        f'$lossy_optional_integer_string_in(plenv_source, {expression}) = ({expected})',
        f'$lossy_optional_integer_condition(plenv_source, {expression}) = ({truth})',
        f'$lossy_optional_integer_condition(plenv_source, {float_cast(expression)}) = ({numeric_truth})',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = ({result})',
    ])
# Selected PINT children retain the original decimal formatter and its result type.
for child, value, text in [
    (conditional(yes, integer(-11), unknown), '$(-11)', '-11'),
    (binary('Coalesce', nil, integer(0)), '0', '0'),
    (conditional(integer(7), 'ABSENT', unknown), '7', '7'),
]:
    checks.extend([
        f'$lossy_optional_integer_default_in(plenv_source, {child}) = ({value})',
        f'$lossy_optional_integer_string_in(plenv_source, {string_cast(child)}) = ($ptascii("{text}"))',
    ])
# CASTSTRING admits these selected bytes without admitting raw selected byte producers.
for expression, data in [
    (binary('Concat', string_cast(conditional(yes, no, unknown)), string('0.0')), [48, 46, 48]),
    (node('NExprBitwiseNot', string_cast(conditional(no, unknown, yes))), [206]),
    (binary('BitwiseAnd', string(b'\xff'), string_cast(binary('Coalesce', yes, unknown))), [49]),
    (dimension(string_cast(conditional(yes, string('19'), unknown)), binary('Plus', integer(0), integer(1))), [57]),
    (dimension(string('09'), string_cast(conditional(yes, string('1'), unknown))), [57]),
]:
    expected = '[' + ', '.join(map(str, data)) + ']'
    checks.append(f'$lossy_optional_integer_string_in(plenv_source, {expression}) = ({expected})')
raw = conditional(yes, string('1'), unknown)
checks.extend([
    f'$lossy_optional_integer_string_in(plenv_source, {raw}) = eps',
    f'$lossy_optional_integer_string_in(plenv_source, {dimension(string("09"), raw)}) = eps',
    f'$lossy_optional_integer_string_in(plenv_source, {string_cast(binary("Concat", string_cast(conditional(yes, no, unknown)), string_cast(unknown)))}) = eps',
])
# Preserve both exact old209/210 selected-string input forms and promoted RHS checks.
for old_unknown in [constant('UnselectedReceive209'), constant('UnselectedReceive210')]:
    expression = string_cast(conditional(true, string('1'), old_unknown))
    checks.extend([
        f'$lossy_optional_integer_string_in(plenv_source, {expression}) = ([49])',
        f'$lossy_optional_integer_condition(plenv_source, {expression}) = (true)',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = (1)',
    ])
# Unselected unknown/FLOAT leaves stay unobserved; selected float formatting stays deferred.
for child in [conditional(yes, floating('3fe0000000000000'), unknown),
              binary('Coalesce', nil, floating('3fe0000000000000')),
              conditional(yes, floating('7ff8000000000000'), unknown),
              conditional(unknown, string('1'), string('0')),
              conditional(yes, unknown, string('1')),
              conditional(yes, node('NExprArray', 'SEQUENCE eps'), unknown),
              conditional(yes, node('NExprVariable', 'BYTES "eA=="'), unknown),
              conditional(yes, string_cast(floating('3fe0000000000000')), unknown)]:
    expression = string_cast(child)
    checks.extend([
        f'$lossy_optional_integer_string_in(plenv_source, {expression}) = eps',
        f'$lossy_optional_integer_condition(plenv_source, {expression}) = eps',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = eps',
    ])
deep = string('0.0')
for _ in range(16):
    deep = string_cast(conditional(yes, deep, unknown))
checks.extend([
    f'$lossy_optional_integer_string_in(plenv_source, {deep}) = ([48, 46, 48])',
    f'$lossy_optional_integer_condition(plenv_source, {deep}) = (true)',
    f'$lossy_optional_integer_condition(plenv_source, {float_cast(deep)}) = (false)',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(deep)}) = (0)',
])
# Every contrast remains genuinely deferred in this same source unit.
fixed_metadata = None
for suffix, function, pattern, projected in [
    ('floatnot', 'deferredFloatNotReceive212', cast(node('NExprBooleanNot', floating('3fe0000000000000'))), '(0)'),
    ('negative', 'deferredNegativeIndexReceive212', cast(dimension(string('10'), string('-1'))), 'eps'),
    ('floatindex', 'deferredFloatIndexReceive212', cast(dimension(string('10'), string('1.0'))), 'eps'),
    ('floatstring', 'deferredFloatStringReceive212', cast(string_cast(floating('3fe0000000000000'))), 'eps'),
    ('computednegative', 'deferredComputedNegativeIndexReceive212', cast(dimension(string('10'), binary('Minus', integer(0), integer(1)))), 'eps'),
    ('selectedfloat', 'deferredSelectedFloatStringReceive212', cast(string_cast(conditional(constant('YesReceive212'), floating('3fe0000000000000'), constant('UnselectedReceive212')))), 'eps'),
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
    '$lookup(psymboltable_global.ENV, $ptascii("xReceive212")) = (n_global)',
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
    '$lookup(S_done.ENV, $ptascii("gotReceive212")) = (n_got)',
    'S_done.STORE[n_got] = DEFINED (PINT 13)',
    r'$call_descriptors_valid(S_done) /\ $heap_valid($heap_graph(S_done))',
])

CASES = {'selection-string-cast-default-omitted-tail': {
    'source': source,
    'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z]',
    'checks': checks,
}}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
