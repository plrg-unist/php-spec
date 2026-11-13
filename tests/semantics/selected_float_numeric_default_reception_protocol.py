#!/usr/bin/env python3
"""Selected FLOAT arithmetic preserves typed values and receive authority."""
import base64
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('selected_float_numeric_default_reception_cases.json')
SOURCES = {}
for row in json.loads(CATALOGUE.read_text()):
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
    SOURCES[row['id']] = row['source']

# Fresh first-VAL front preserves the whole five-default declaration; source0.
full = SOURCES['selected-float-numeric-precision-modes']
setup = full.index("set_error_handler('warningReceive216');")
start = full.index('$gotReceive216 = valueFirstReceive216(')
end = full.index('$xReceive216 = 1.5;', start)
source = full[:full.index('function referenceFirstReceive216')] + full[setup:end]
assert hashlib.sha256(source.encode()).hexdigest() == '5fbb98ba33e233c7d07398f44590ba5f2475af2000c4f6bcefdee609406d96a6'

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
    return constant('UnselectedReceive216')


yes = lambda: cast(constant('YesReceive216'))
no = lambda: cast(constant('NoReceive216'))
large = lambda: floating('7fe1ccf385ebc8a0')
computed_inf = lambda: binary('Mul', large(), integer(2))
computed_nan = lambda: binary('Minus', computed_inf(), computed_inf())
selected = [
    conditional(constant('YesReceive216'), negate(floating('401e000000000000')), unknown()),
    conditional(constant('NoReceive216'), unknown(), negate(floating('4016000000000000'))),
    binary('Coalesce', constant('NilReceive216'), binary('Div', integer(27), integer(2))),
    node('NExprTernary', binary('Div', floating('0000000000000000'), yes()), 'ABSENT', floating('3fe0000000000000')),
    node('NExprTernary', binary('Plus', floating('3ff8000000000000'), no()), 'ABSENT', unknown()),
]
arithmetic = [
    binary('Plus', selected[0], no()),
    binary('Mul', selected[1], binary('Plus', integer(1), yes())),
    binary('Plus', selected[2], no()),
    binary('Minus', selected[3], floating('3fe0000000000000')),
    binary('Minus', selected[4], floating('3fe0000000000000')),
]
patterns = [
    cast(arithmetic[0]), cast(arithmetic[1]), cast(arithmetic[2]),
    conditional(cast(arithmetic[3]), unknown(), cast(string('-9223372036854775808tail'))),
    conditional(cast(arithmetic[4]), cast(string('9' * 24)), unknown()),
]
contrasts = [
    ('floatnot','deferredFloatNotReceive216',cast(node('NExprBooleanNot',floating('3fe0000000000000'))),'(0)'),
    ('negative','deferredNegativeIndexReceive216',cast(dimension(string('10'),string('-1'))),'eps'),
    ('floatindex','deferredFloatIndexReceive216',cast(dimension(string('10'),string('1.0'))),'eps'),
    ('floatstring','deferredFloatStringReceive216',cast(string_cast(floating('3fe0000000000000'))),'eps'),
    ('computednegative','deferredComputedNegativeIndexReceive216',cast(dimension(string('10'),binary('Minus',integer(0),integer(1)))),'eps'),
    ('selectedfloat','deferredSelectedFloatStringReceive216',cast(string_cast(conditional(constant('YesReceive216'),floating('3fe0000000000000'),unknown()))),'eps'),
    ('nonfit','deferredComputedFloatNonfitReceive216',cast(computed_inf()),'eps'),
    ('zerodiv','deferredComputedFloatZeroDivReceive216',cast(binary('Div',floating('3ff0000000000000'),integer(0))),'eps'),
    ('computednan','deferredComputedFloatNanReceive216',cast(computed_nan()),'eps'),
    ('unarynonfit','deferredComputedFloatUnaryNonfitReceive216',cast(negate(cast(string('-9223372036854775808')))),'eps'),
    ('computednot','deferredComputedFloatNotReceive216',cast(node('NExprBooleanNot',binary('Div',yes(),integer(2)))),'(0)'),
    ('computednannot','deferredComputedFloatNanNotReceive216',cast(node('NExprBooleanNot',computed_nan())),'eps'),
    ('selectednonfit','deferredSelectedFloatArithmeticNonfitReceive216',cast(binary('Plus',conditional(constant('YesReceive216'),computed_inf(),unknown()),integer(0))),'eps'),
    ('coalescenonfit','deferredSelectedFloatCoalesceNonfitReceive216',cast(binary('Plus',binary('Coalesce',computed_inf(),unknown()),integer(0))),'eps'),
    ('selectednan','deferredSelectedFloatArithmeticNanReceive216',cast(binary('Minus',conditional(constant('YesReceive216'),computed_inf(),unknown()),conditional(constant('NoReceive216'),unknown(),computed_inf()))),'eps'),
]
checks = [
    r'n_bits = 4609434218613702656 /\ i = 1',
    '$function_at(S.FUNCTIONS, porigin) = (pfunction)',
    'plenv_source = pfunction.ENV',
    r'plenv_source.NAMESPACE = eps /\ plenv_source.CONSTANTS = [($ptascii("YesReceive216"), $ptascii("true")), ($ptascii("NoReceive216"), $ptascii("false")), ($ptascii("NilReceive216"), $ptascii("null"))]',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_a, psparam_b, psparam_c, psparam_d, psparam_e]',
    r'~psparam_a.REQUIRED /\ ~psparam_a.BYREF /\ psparam_b.BYREF /\ psparam_d.BYREF /\ psparam_e.BYREF',
]
for index, (letter, pattern, selection, operation, value, selected_bits, operation_bits, leaf_integer) in enumerate(zip(
    'abcde', patterns, selected, arithmetic,
    ('$(-7)', '$(-11)', '13', '$(-9223372036854775808)', '9223372036854775807'),
    ('c01e000000000000', 'c016000000000000', '402b000000000000', '3fe0000000000000', '3ff8000000000000'),
    ('c01e000000000000', 'c026000000000000', '402b000000000000', '0000000000000000', '3ff0000000000000'),
    ('$(-7)', '$(-5)', '13', '0', '1'),
)):
    checks.extend([
        f'psparam_{letter}.DEFAULT = PSDEFAULT expression_{letter} "int"',
        f'expression_{letter} = {pattern}',
        f'expression_selected_{letter} = {selection}',
        f'expression_numeric_{letter} = {operation}',
        f'$lossy_optional_integer_default_in(plenv_source, expression_{letter}) = ({value})',
        f'$lossy_optional_integer_default_in(plenv_source, expression_selected_{letter}) = eps',
        f'$lossy_optional_integer_selection_shape(expression_selected_{letter})',
        f'$lossy_optional_integer_cast_leaf(plenv_source, expression_selected_{letter}) = (expression_leaf_{letter})',
        f'$lossy_optional_integer_numeric(plenv_source, expression_selected_{letter}) = (NFLOAT $hex_bits("{selected_bits}", 0))',
        f'$lossy_optional_integer_numeric(plenv_source, expression_numeric_{letter}) = (NFLOAT $hex_bits("{operation_bits}", 0))',
        f'$lossy_optional_integer_default_in(plenv_source, NExprCastInt expression_selected_{letter} metadata_case_1) = ({leaf_integer})',
        f'$lossy_optional_integer_condition(plenv_source, expression_selected_{letter}) = (true)',
        f'$default_parameter_origin(S, porigin, {index}) = PORIGIN n_unit pcpath_{letter}',
        f'porigin_{letter} = PORIGIN n_unit (pcpath_{letter} ++ [PCFIELD 6])',
        f'$origin_node(S.SOURCES, porigin_{letter}) = (expression_{letter})',
        f'$default_at(pfunction.DEFAULTS, {index}) = ({{INDEX {index}, ORIGIN porigin_{letter}, KIND PDSTORED}})',
        f'$compiled_read(S, porigin_{letter}) = (PINT {value})',
    ])
checks.extend([
    '$lossy_optional_integer_header(S, pfunction, pfunction.SIGNATURE.PARAMETERS, 0)',
    'expression_a = NExprCastInt expression_numeric_a metadata_a',
    '$lossy_optional_integer_condition(plenv_source, expression_numeric_d) = (false)',
    '$lossy_optional_integer_condition(plenv_source, expression_numeric_e) = (true)',
    '$lossy_optional_integer_numeric($plempty(false), expression_selected_a) = eps',
    '~$lossy_optional_integer_header(S, pfunction[.ENV = $plempty(false)], pfunction.SIGNATURE.PARAMETERS, 0)',
    'plenv_yes_false = plenv_source[.CONSTANTS = [($ptascii("YesReceive216"), $ptascii("false")), ($ptascii("NoReceive216"), $ptascii("false")), ($ptascii("NilReceive216"), $ptascii("null"))]]',
    '$lossy_optional_integer_default_in(plenv_yes_false, expression_a) = eps',
    '$lossy_optional_integer_default_in(plenv_yes_false, expression_b) = ($(-5))',
    '~$lossy_optional_integer_header(S, pfunction[.ENV = plenv_yes_false], pfunction.SIGNATURE.PARAMETERS, 0)',
    'plenv_no_true = plenv_source[.CONSTANTS = [($ptascii("YesReceive216"), $ptascii("true")), ($ptascii("NoReceive216"), $ptascii("true")), ($ptascii("NilReceive216"), $ptascii("null"))]]',
    '$lossy_optional_integer_default_in(plenv_no_true, expression_c) = (14)',
    '~$lossy_optional_integer_header(S, pfunction[.ENV = plenv_no_true], pfunction.SIGNATURE.PARAMETERS, 0)',
    'expression_same = NExprUnaryMinus (NScalarInt (INTEGER 7) metadata_a) metadata_a',
    '$lossy_optional_integer_default_in(plenv_source, expression_same) = ($(-7))',
    '~$lossy_optional_integer_tail(S, pfunction, [psparam_a[.DEFAULT = PSDEFAULT expression_same "int"]], 0)',
    'pfunction.DEFAULTS = [pdefault_a, pdefault_b, pdefault_c, pdefault_d, pdefault_e]',
    '~$lossy_optional_integer_tail(S, pfunction[.DEFAULTS = [pdefault_a, pdefault_b[.KIND = PDDEFERRED], pdefault_c, pdefault_d, pdefault_e]], [psparam_b], 1)',
    'S_wrong_value = S[.POOLS = [{UNIT n_unit, CONSTANTS ([(PCONSTANT (pcpath_c ++ [PCFIELD 6]) (PINT 1))])}]]',
    '~$lossy_optional_integer_tail(S_wrong_value, pfunction, [psparam_c], 2)',
])
# Helper projection never substitutes for a genuine stored root in this same unit.
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
expr_yes, expr_no, expr_nil = map(constant, ('YesReceive216', 'NoReceive216', 'NilReceive216'))
expr_unknown = unknown()
half = binary('Div', integer(1), integer(2))
zero = binary('Minus', floating('3fe0000000000000'), floating('3fe0000000000000'))
fraction = conditional(expr_yes, half, expr_unknown)
# Selection preserves FLOAT tags/bits before arithmetic, truncation or truth.
for expression, bits, result in [
    (fraction, '3fe0000000000000', '0'),
    (conditional(expr_no, expr_unknown, floating('8000000000000000')), '8000000000000000', '0'),
    (conditional(half, 'ABSENT', expr_unknown), '3fe0000000000000', '0'),
    (conditional(zero, 'ABSENT', half), '3fe0000000000000', '0'),
    (binary('Coalesce', expr_nil, half), '3fe0000000000000', '0'),
    (binary('Coalesce', half, expr_unknown), '3fe0000000000000', '0'),
]:
    truth = str(bits != '8000000000000000').lower()
    checks.extend([
        f'$lossy_optional_integer_default_in(plenv_source, {expression}) = eps',
        f'$lossy_optional_integer_numeric(plenv_source, {expression}) = (NFLOAT $hex_bits("{bits}", 0))',
        f'$lossy_optional_integer_condition(plenv_source, {expression}) = ({truth})',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = ({result})',
        f'$lossy_optional_integer_string_in(plenv_source, {string_cast(expression)}) = eps',
    ])
for constructor, bits in [('NExprUnaryPlus', '3fe0000000000000'), ('NExprUnaryMinus', 'bfe0000000000000')]:
    expression = node(constructor, fraction)
    checks.extend([
        f'$lossy_optional_integer_numeric(plenv_source, {expression}) = (NFLOAT $hex_bits("{bits}", 0))',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = (0)',
    ])
# All four existing typed arithmetic operators compose on a selected FLOAT operand.
for kind, other, bits, result in [('Plus', integer(1), '3ff8000000000000', '1'),
                                  ('Minus', integer(1), 'bfe0000000000000', '0'),
                                  ('Mul', integer(3), '3ff8000000000000', '1'),
                                  ('Div', integer(2), '3fd0000000000000', '0')]:
    expression = binary(kind, fraction, other)
    checks.extend([
        f'$lossy_optional_integer_numeric(plenv_source, {expression}) = (NFLOAT $hex_bits("{bits}", 0))',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = ({result})',
    ])
inf = computed_inf()
# A null LEFT selects the RIGHT leaf; only a nonnull LEFT uses the inherited fit proof.
for expression, projected in [
    (conditional(expr_yes, inf, expr_unknown), '(NFLOAT $hex_bits("7ff0000000000000", 0))'),
    (binary('Coalesce', expr_nil, inf), '(NFLOAT $hex_bits("7ff0000000000000", 0))'),
    (binary('Coalesce', inf, expr_unknown), 'eps'),
]:
    checks.extend([
        f'$lossy_optional_integer_numeric(plenv_source, {expression}) = {projected}',
        f'$lossy_optional_integer_condition(plenv_source, {expression}) = (true)',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = eps',
    ])
selected_nan = conditional(expr_yes, computed_nan(), expr_unknown)
checks.extend([
    f'$lossy_optional_integer_numeric(plenv_source, {selected_nan}) = (NFLOAT n_nan)',
    '$pfcast_nan(PFLOAT n_nan)',
    f'$lossy_optional_integer_condition(plenv_source, {selected_nan}) = eps',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(selected_nan)}) = eps',
])
# Selected scalar types stay uncoerced; selected NINT leaves retain their own certificate.
selected_null_integer = binary('Coalesce', conditional(expr_yes, expr_nil, expr_unknown), integer(1))
for expression in [conditional(expr_yes, string('.5'), expr_unknown), conditional(expr_yes, expr_no, expr_unknown),
                   binary('Coalesce', expr_no, half), selected_null_integer,
                   conditional(expr_yes, integer(9223372036854775808), expr_unknown)]:
    numeric_result = '(NINT 1)' if expression == selected_null_integer else 'eps'
    checks.append(f'$lossy_optional_integer_numeric(plenv_source, {expression}) = {numeric_result}')
selected_int = conditional(expr_yes, integer(7), expr_unknown)
checks.extend([
    f'$lossy_optional_integer_default_in(plenv_source, {selected_int}) = (7)',
    f'$lossy_optional_integer_numeric(plenv_source, {selected_int}) = (NINT 7)',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(selected_int)}) = (7)',
    f'$lossy_optional_integer_numeric(plenv_source, {conditional(expr_yes, negate(integer(9223372036854775808)), expr_unknown)}) = (NINT $(-9223372036854775808))',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(dimension(string("10"), fraction))}) = eps',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(dimension(string("10"), cast(fraction)))}) = (1)',
])
# Fresh exact promoted prior source/helper forms keep their old namespace aliases.
checks.extend([
    'plenv_old213 = plenv_source[.CONSTANTS = [($ptascii("YesReceive213"), $ptascii("true")), ($ptascii("NoReceive213"), $ptascii("false")), ($ptascii("NilReceive213"), $ptascii("null"))]]',
    'plenv_old214 = plenv_source[.CONSTANTS = [($ptascii("YesReceive214"), $ptascii("true")), ($ptascii("NoReceive214"), $ptascii("false")), ($ptascii("NilReceive214"), $ptascii("null"))]]',
    'plenv_old215 = plenv_source[.CONSTANTS = [($ptascii("YesReceive215"), $ptascii("true")), ($ptascii("NoReceive215"), $ptascii("false")), ($ptascii("NilReceive215"), $ptascii("null"))]]',
])
for number in [213, 214]:
    old_literal = conditional(constant(f'YesReceive{number}'), floating('3fe0000000000000'), constant(f'UnselectedReceive{number}'))
    checks.append(f'$lossy_optional_integer_numeric(plenv_old{number}, {old_literal}) = (NFLOAT $hex_bits("3fe0000000000000", 0))')
    if number == 213:
        old_computed = conditional(constant('YesReceive213'), binary('Div', integer(5), integer(2)), constant('UnselectedReceive213'))
        checks.append(f'$lossy_optional_integer_numeric(plenv_old213, {old_computed}) = (NFLOAT $hex_bits("4004000000000000", 0))')
    else:
        for kind, bits in [('NExprUnaryPlus', '3fe0000000000000'), ('NExprUnaryMinus', 'bfe0000000000000')]:
            expression = node(kind, old_literal)
            checks.extend([
                f'$lossy_optional_integer_numeric(plenv_old214, {expression}) = (NFLOAT $hex_bits("{bits}", 0))',
                f'$lossy_optional_integer_default_in(plenv_old214, {cast(expression)}) = (0)',
            ])
old_yes, old_nil, old_unknown = map(constant, ('YesReceive215', 'NilReceive215', 'UnselectedReceive215'))
old_condition_d = conditional(binary('Coalesce', constant('null'), binary('Div', floating('0000000000000000'), cast(old_yes))), 'ABSENT', floating('0000000000000000'))
checks.append(f'$lossy_optional_integer_numeric(plenv_old215, {old_condition_d}) = (NFLOAT $hex_bits("0000000000000000", 0))')
for expression, bits in [(conditional(old_yes, half, old_unknown), '3fe0000000000000'),
                         (conditional(zero, 'ABSENT', half), '3fe0000000000000'),
                         (binary('Coalesce', old_nil, half), '3fe0000000000000'),
                         (binary('Coalesce', zero, old_unknown), '0000000000000000')]:
    checks.append(f'$lossy_optional_integer_numeric(plenv_old215, {expression}) = (NFLOAT $hex_bits("{bits}", 0))')
deep = half
for _ in range(8):
    deep = conditional(expr_yes, deep, expr_unknown)
checks.extend([
    f'$lossy_optional_integer_numeric(plenv_source, {deep}) = (NFLOAT $hex_bits("3fe0000000000000", 0))',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(binary("Mul", deep, integer(3)))}) = (1)',
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
    '$lookup(psymboltable_global.ENV, $ptascii("xReceive216")) = (n_global)',
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
    '$lookup(S_done.ENV, $ptascii("gotReceive216")) = (n_got)',
    'S_done.STORE[n_got] = DEFINED (PINT 13)',
    r'$call_descriptors_valid(S_done) /\ $heap_valid($heap_graph(S_done))',
])

CASES = {'selected-float-numeric-default-omitted-tail': {
    'source': source,
    'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z]',
    'checks': checks,
}}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
