#!/usr/bin/env python3
"""Computed FLOAT truth preserves source defaults and receive authority."""
import base64
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('computed_float_truth_default_reception_cases.json')
SOURCES = {}
for row in json.loads(CATALOGUE.read_text()):
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
    SOURCES[row['id']] = row['source']

# Fresh first-VAL front preserves the whole five-default declaration; source0.
full = SOURCES['computed-float-truth-precision-modes']
setup = full.index("set_error_handler('warningReceive215');")
start = full.index('$gotReceive215 = valueFirstReceive215(')
end = full.index('$xReceive215 = 1.5;', start)
source = full[:full.index('function referenceFirstReceive215')] + full[setup:end]
assert hashlib.sha256(source.encode()).hexdigest() == 'e084f5fa7e9b06199c6b8b8d943d4ef0ee6b9e92a36928e63dae73e84459c9be'

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


def cast(child):
    return node('NExprCastInt', child)


def binary(constructor, left, right):
    return node('NExprBinaryOp' + constructor, left, right)


def conditional(cond, yes, no):
    return node('NExprTernary', cond, yes, no)


def dimension(base, selector):
    return node('NExprArrayDimFetch', base, selector)


def string_cast(child):
    return node('NExprCastString', child)


def negate(child):
    return node('NExprUnaryMinus', child)


def unknown():
    return constant('UnselectedReceive215')


yes = lambda: cast(constant('YesReceive215'))
no = lambda: cast(constant('NoReceive215'))
large = lambda: floating('7fe1ccf385ebc8a0')
computed_inf = lambda: binary('Mul', large(), integer(2))
computed_nan = lambda: binary('Minus', computed_inf(), computed_inf())
conditions = [
    negate(binary('Minus', binary('Div', yes(), integer(2)), floating('3fe0000000000000'))),
    node('NExprCastBool', binary('Plus', floating('3fe0000000000000'), no())),
    negate(binary('Mul', floating('0000000000000001'), yes())),
    node('NExprTernary', binary('Coalesce', constant('null'), binary('Div', floating('0000000000000000'), yes())), 'ABSENT', floating('0000000000000000')),
    binary('Mul', large(), binary('Plus', integer(2), no())),
]
patterns = [
    negate(conditional(conditions[0], unknown(), integer(7))),
    cast(conditional(conditions[1], string('-11tail'), unknown())),
    cast(conditional(conditions[2], string('13tail'), unknown())),
    conditional(conditions[3], unknown(), cast(string('-9223372036854775808tail'))),
    conditional(conditions[4], cast(string('9' * 24)), unknown()),
]
contrasts = [
    ('floatnot','deferredFloatNotReceive215',cast(node('NExprBooleanNot',floating('3fe0000000000000'))),'(0)'),
    ('negative','deferredNegativeIndexReceive215',cast(dimension(string('10'),string('-1'))),'eps'),
    ('floatindex','deferredFloatIndexReceive215',cast(dimension(string('10'),string('1.0'))),'eps'),
    ('floatstring','deferredFloatStringReceive215',cast(string_cast(floating('3fe0000000000000'))),'eps'),
    ('computednegative','deferredComputedNegativeIndexReceive215',cast(dimension(string('10'),binary('Minus',integer(0),integer(1)))),'eps'),
    ('selectedfloat','deferredSelectedFloatStringReceive215',cast(string_cast(conditional(constant('YesReceive215'),floating('3fe0000000000000'),unknown()))),'eps'),
    ('nonfit','deferredComputedFloatNonfitReceive215',cast(computed_inf()),'eps'),
    ('zerodiv','deferredComputedFloatZeroDivReceive215',cast(binary('Div',floating('3ff0000000000000'),integer(0))),'eps'),
    ('computednan','deferredComputedFloatNanReceive215',cast(computed_nan()),'eps'),
    ('unarynonfit','deferredComputedFloatUnaryNonfitReceive215',cast(negate(cast(string('-9223372036854775808')))),'eps'),
    ('computednot','deferredComputedFloatNotReceive215',cast(node('NExprBooleanNot',binary('Div',yes(),integer(2)))),'(0)'),
    ('computednannot','deferredComputedFloatNanNotReceive215',cast(node('NExprBooleanNot',computed_nan())),'eps'),
]

checks = [
    r'n_bits = 4609434218613702656 /\ i = 1',
    '$function_at(S.FUNCTIONS, porigin) = (pfunction)',
    'plenv_source = pfunction.ENV',
    r'plenv_source.NAMESPACE = eps /\ plenv_source.CONSTANTS = [($ptascii("YesReceive215"), $ptascii("true")), ($ptascii("NoReceive215"), $ptascii("false")), ($ptascii("NilReceive215"), $ptascii("null"))]',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_a, psparam_b, psparam_c, psparam_d, psparam_e]',
    r'~psparam_a.REQUIRED /\ ~psparam_a.BYREF /\ psparam_b.BYREF /\ psparam_d.BYREF /\ psparam_e.BYREF',
]
for index, (letter, pattern, condition, value) in enumerate(zip(
    'abcde', patterns, conditions, ('$(-7)', '$(-11)', '13', '$(-9223372036854775808)', '9223372036854775807'),
)):
    checks.extend([
        f'psparam_{letter}.DEFAULT = PSDEFAULT expression_{letter} "int"',
        f'expression_{letter} = {pattern}',
        f'expression_condition_{letter} = {condition}',
        f'$lossy_optional_integer_condition(plenv_source, expression_condition_{letter}) = ({str(letter not in "ad").lower()})',
        f'$lossy_optional_integer_default_in(plenv_source, expression_{letter}) = ({value})',
        f'$default_parameter_origin(S, porigin, {index}) = PORIGIN n_unit pcpath_{letter}',
        f'porigin_{letter} = PORIGIN n_unit (pcpath_{letter} ++ [PCFIELD 6])',
        f'$origin_node(S.SOURCES, porigin_{letter}) = (expression_{letter})',
        f'$default_at(pfunction.DEFAULTS, {index}) = ({{INDEX {index}, ORIGIN porigin_{letter}, KIND PDSTORED}})',
        f'$compiled_read(S, porigin_{letter}) = (PINT {value})',
    ])
checks.extend([
    '$lossy_optional_integer_header(S, pfunction, pfunction.SIGNATURE.PARAMETERS, 0)',
    'expression_a = NExprUnaryMinus expression_choice_a metadata_a',
    'expression_condition_b = NExprCastBool expression_numeric_b metadata_bool_b',
    '$lossy_optional_integer_numeric(plenv_source, expression_condition_a) = (NFLOAT $hex_bits("8000000000000000", 0))',
    '$lossy_optional_integer_numeric(plenv_source, expression_numeric_b) = (NFLOAT $hex_bits("3fe0000000000000", 0))',
    '$lossy_optional_integer_numeric(plenv_source, expression_condition_c) = (NFLOAT $hex_bits("8000000000000001", 0))',
    '$lossy_optional_integer_numeric(plenv_source, expression_condition_d) = eps',
    '$lossy_optional_integer_selection_shape(expression_condition_d)',
    '$lossy_optional_integer_numeric(plenv_source, expression_condition_e) = (NFLOAT $hex_bits("7ff0000000000000", 0))',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt expression_condition_e metadata_a) = eps',
    '$lossy_optional_integer_string_in(plenv_source, NExprCastString expression_condition_e metadata_a) = eps',
    '$lossy_optional_integer_condition($plempty(false), expression_condition_a) = eps',
    '~$lossy_optional_integer_header(S, pfunction[.ENV = $plempty(false)], pfunction.SIGNATURE.PARAMETERS, 0)',
    'plenv_yes_false = plenv_source[.CONSTANTS = [($ptascii("YesReceive215"), $ptascii("false")), ($ptascii("NoReceive215"), $ptascii("false")), ($ptascii("NilReceive215"), $ptascii("null"))]]',
    '$lossy_optional_integer_condition(plenv_yes_false, expression_condition_a) = (true)',
    '$lossy_optional_integer_default_in(plenv_yes_false, expression_a) = eps',
    '$lossy_optional_integer_condition(plenv_yes_false, expression_condition_c) = (false)',
    '~$lossy_optional_integer_header(S, pfunction[.ENV = plenv_yes_false], pfunction.SIGNATURE.PARAMETERS, 0)',
    'expression_same = NExprUnaryMinus (NScalarInt (INTEGER 7) metadata_a) metadata_a',
    '$lossy_optional_integer_default_in(plenv_source, expression_same) = ($(-7))',
    '~$lossy_optional_integer_tail(S, pfunction, [psparam_a[.DEFAULT = PSDEFAULT expression_same "int"]], 0)',
    'pfunction.DEFAULTS = [pdefault_a, pdefault_b, pdefault_c, pdefault_d, pdefault_e]',
    '~$lossy_optional_integer_tail(S, pfunction[.DEFAULTS = [pdefault_a, pdefault_b[.KIND = PDDEFERRED], pdefault_c, pdefault_d, pdefault_e]], [psparam_b], 1)',
    'S_wrong_value = S[.POOLS = [{UNIT n_unit, CONSTANTS ([(PCONSTANT (pcpath_c ++ [PCFIELD 6]) (PINT 1))])}]]',
    '~$lossy_optional_integer_tail(S_wrong_value, pfunction, [psparam_c], 2)',
])
# Preserve the compiler-deferred contrasts, including helper-only BOOL_NOT success.
for suffix, function, pattern, projected in contrasts:
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
        f'~$lossy_optional_integer_tail(S, pfunction_{suffix}[.DEFAULTS = [{{INDEX 0, ORIGIN porigin_{suffix}, KIND PDSTORED}}]], [psparam_{suffix}[.DEFAULT = PSDEFAULT expression_{suffix} "int"]], 0)',
    ])
fixed_metadata = 'metadata_a'
expr_unknown = unknown()
# Fresh coverage of the exact ten old source operands whose condition RHS changes.
checks.extend([
    'plenv_old213 = plenv_source[.CONSTANTS = [($ptascii("YesReceive213"), $ptascii("true")), ($ptascii("NoReceive213"), $ptascii("false")), ($ptascii("NilReceive213"), $ptascii("null"))]]',
    'plenv_old214 = plenv_source[.CONSTANTS = [($ptascii("YesReceive214"), $ptascii("true")), ($ptascii("NoReceive214"), $ptascii("false")), ($ptascii("NilReceive214"), $ptascii("null"))]]',
])
yes213, no213, unknown213 = map(constant, ('YesReceive213', 'NoReceive213', 'UnselectedReceive213'))
yes214, no214 = map(constant, ('YesReceive214', 'NoReceive214'))
old_sources = [
    ('plenv_old213', binary('Minus', negate(floating('401c000000000000')), binary('Div', cast(yes213), integer(2))), 'c01e000000000000'),
    ('plenv_old213', binary('Mul', negate(floating('4016000000000000')), binary('Plus', integer(1), cast(yes213))), 'c026000000000000'),
    ('plenv_old213', binary('Plus', floating('402a000000000000'), binary('Div', conditional(no213, unknown213, integer(1)), integer(2))), '402b000000000000'),
    ('plenv_old213', binary('Div', cast(yes213), integer(2)), '3fe0000000000000'),
    ('plenv_old213', binary('Div', binary('Plus', integer(3), cast(no213)), integer(2)), '3ff8000000000000'),
    ('plenv_old214', negate(binary('Plus', cast(yes214), binary('Div', integer(13), integer(2)))), 'c01e000000000000'),
    ('plenv_old214', negate(binary('Plus', binary('Div', integer(21), integer(2)), cast(yes214))), 'c027000000000000'),
    ('plenv_old214', node('NExprUnaryPlus', binary('Div', binary('Plus', integer(27), cast(no214)), integer(2))), '402b000000000000'),
    ('plenv_old214', negate(binary('Div', cast(yes214), integer(2))), 'bfe0000000000000'),
    ('plenv_old214', node('NExprUnaryPlus', binary('Plus', binary('Div', integer(3), integer(2)), cast(no214))), '3ff8000000000000'),
]
for env, expression, bits in old_sources:
    checks.extend([
        f'$lossy_optional_integer_numeric({env}, {expression}) = (NFLOAT $hex_bits("{bits}", 0))',
        f'$lossy_optional_integer_condition({env}, {expression}) = (true)',
    ])
# Exact old arithmetic/sign table inputs retain typed bits and now quiet FLOAT truth.
for expression, bits in [
    (binary('Div', integer(5), integer(2)), '4004000000000000'),
    (binary('Div', integer(-5), integer(2)), 'c004000000000000'),
    (binary('Plus', floating('3ff8000000000000'), integer(1)), '4004000000000000'),
    (binary('Minus', negate(floating('401c000000000000')), floating('3fe0000000000000')), 'c01e000000000000'),
    (binary('Mul', floating('3ff8000000000000'), integer(2)), '4008000000000000'),
    (binary('Div', floating('4018000000000000'), integer(3)), '4000000000000000'),
    (binary('Plus', floating('8000000000000000'), floating('8000000000000000')), '8000000000000000'),
    (binary('Mul', floating('0000000000000001'), floating('3fe0000000000000')), '0000000000000000'),
    (binary('Minus', cast(string('-9223372036854775808')), integer(1)), 'c3e0000000000000'),
    (negate(binary('Div', integer(5), integer(2))), 'c004000000000000'),
    (node('NExprUnaryPlus', binary('Div', integer(5), integer(2))), '4004000000000000'),
    (negate(negate(binary('Div', integer(5), integer(2)))), '4004000000000000'),
    (negate(binary('Mul', floating('3ff8000000000000'), integer(2))), 'c008000000000000'),
    (node('NExprUnaryPlus', binary('Div', integer(0), floating('bfe0000000000000'))), '8000000000000000'),
    (negate(binary('Div', integer(0), floating('bfe0000000000000'))), '0000000000000000'),
    (negate(binary('Mul', floating('0000000000000001'), floating('3fe0000000000000'))), '8000000000000000'),
    (negate(negate(cast(string('-9223372036854775808')))), 'c3e0000000000000'),
    (binary('Plus', floating('3fe0000000000000'), integer(0)), '3fe0000000000000'),
    (binary('Plus', floating('3fe0000000000000'), floating('3fe0000000000000')), '3ff0000000000000'),
]:
    checks.extend([
        f'$lossy_optional_integer_numeric(plenv_source, {expression}) = (NFLOAT $hex_bits("{bits}", 0))',
        f'$lossy_optional_integer_condition(plenv_source, {expression}) = ({str(bits not in ["0000000000000000", "8000000000000000"]).lower()})',
    ])
half = binary('Div', integer(1), integer(2))
zero = binary('Minus', floating('3fe0000000000000'), floating('3fe0000000000000'))
inf = computed_inf()
# Truth remains separate from truncation, formatting, raw arithmetic coercion and key grammar.
for expression, truth, integer_result in [(half, True, '(0)'), (zero, False, '(0)'), (inf, True, 'eps'), (negate(inf), True, 'eps')]:
    checks.extend([
        f'$lossy_optional_integer_condition(plenv_source, {expression}) = ({str(truth).lower()})',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = {integer_result}',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(node("NExprCastBool", expression))}) = ({int(truth)})',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(node("NExprBooleanNot", expression))}) = ({int(not truth)})',
        f'$lossy_optional_integer_string_in(plenv_source, {string_cast(expression)}) = eps',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(dimension(string("10"), expression))}) = eps',
    ])
for expression in [computed_nan(), binary('Div', integer(1), integer(0)), binary('Div', floating('3ff0000000000000'), integer(0)),
                   binary('Plus', constant('true'), integer(1)), binary('Plus', string('1'), integer(1)),
                   binary('Pow', integer(2), integer(63))]:
    checks.extend([
        f'$lossy_optional_integer_condition(plenv_source, {expression}) = eps',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(node("NExprCastBool", expression))}) = eps',
    ])
# Selection truth takes its existing route; raw selected FLOAT operands remain outside Numeric.
for expression, truth in [
    (conditional(constant('YesReceive215'), half, expr_unknown), True),
    (conditional(zero, 'ABSENT', half), True),
    (binary('Coalesce', constant('NilReceive215'), half), True),
    (binary('Coalesce', zero, expr_unknown), False),
]:
    checks.extend([
        f'$lossy_optional_integer_selection_shape({expression})',
        f'$lossy_optional_integer_numeric(plenv_source, {expression}) = eps',
        f'$lossy_optional_integer_condition(plenv_source, {expression}) = ({str(truth).lower()})',
    ])
deep = half
for _ in range(8):
    deep = node('NExprCastBool', node('NExprBooleanNot', node('NExprBooleanNot', deep)))
checks.extend([
    f'$lossy_optional_integer_condition(plenv_source, {deep}) = (true)',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(deep)}) = (1)',
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
    '$lookup(psymboltable_global.ENV, $ptascii("xReceive215")) = (n_global)',
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
    '$lookup(S_done.ENV, $ptascii("gotReceive215")) = (n_got)',
    'S_done.STORE[n_got] = DEFINED (PINT 13)',
    r'$call_descriptors_valid(S_done) /\ $heap_valid($heap_graph(S_done))',
])

CASES = {'computed-float-truth-default-omitted-tail': {
    'source': source,
    'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z]',
    'checks': checks,
}}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
