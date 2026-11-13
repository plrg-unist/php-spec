#!/usr/bin/env python3
"""Computed FLOAT truth retains typed domains, source authority and receive ownership."""
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
    literal = f'$(-{abs(value)})' if value < 0 else str(value)
    return node('NScalarInt', f'INTEGER {literal}')


def string(value):
    data = value.encode() if isinstance(value, str) else value
    return node('NScalarString', f'BYTES "{base64.b64encode(data).decode()}"')


def constant(name, qualified=False):
    kind = 'NNameFullyQualified' if qualified else 'NName'
    return node('NExprConstFetch', node(kind, f'BYTES "{base64.b64encode(name.encode()).decode()}"'))


def binary(kind, left, right):
    return node('NExprBinaryOp' + kind, left, right)


def ternary(condition, selected, alternative):
    return node('NExprTernary', condition, selected, alternative)


def dimension(base, index):
    return node('NExprArrayDimFetch', base, index)


def cast(child):
    return node('NExprCastInt', child)


def float_cast(child):
    return node('NExprCastDouble', child)


def string_cast(child):
    return node('NExprCastString', child)


def floating(bits):
    return node('NScalarFloat', f'FLOAT "{bits}"')


def unknown():
    return constant('UnselectedReceive215')


def negate(child):
    return node('NExprUnaryMinus', child)


yes_cast = lambda: cast(constant('YesReceive215'))
no_cast = lambda: cast(constant('NoReceive215'))
large = lambda: floating('7fe1ccf385ebc8a0')
computed_inf = lambda: binary('Mul', large(), integer(2))
computed_nan = lambda: binary('Minus', computed_inf(), computed_inf())
conditions = [
    negate(binary('Minus', binary('Div', yes_cast(), integer(2)), floating('3fe0000000000000'))),
    node('NExprCastBool', binary('Plus', floating('3fe0000000000000'), no_cast())),
    negate(binary('Mul', floating('0000000000000001'), yes_cast())),
    node('NExprTernary', binary('Coalesce', constant('null'), binary('Div', floating('0000000000000000'), yes_cast())), 'ABSENT', floating('0000000000000000')),
    binary('Mul', large(), binary('Plus', integer(2), no_cast())),
]
patterns = [
    negate(ternary(conditions[0], unknown(), integer(7))),
    cast(ternary(conditions[1], string('-11tail'), unknown())),
    cast(ternary(conditions[2], string('13tail'), unknown())),
    ternary(conditions[3], unknown(), cast(string('-9223372036854775808tail'))),
    ternary(conditions[4], cast(string('9' * 24)), unknown()),
]
contrasts = [
    ('floatnot','deferredFloatNotReceive215',cast(node('NExprBooleanNot',floating('3fe0000000000000'))),'(0)'),
    ('negative','deferredNegativeIndexReceive215',cast(dimension(string('10'),string('-1'))),'eps'),
    ('floatindex','deferredFloatIndexReceive215',cast(dimension(string('10'),string('1.0'))),'eps'),
    ('floatstring','deferredFloatStringReceive215',cast(string_cast(floating('3fe0000000000000'))),'eps'),
    ('computednegative','deferredComputedNegativeIndexReceive215',cast(dimension(string('10'),binary('Minus',integer(0),integer(1)))),'eps'),
    ('selectedfloat','deferredSelectedFloatStringReceive215',cast(string_cast(ternary(constant('YesReceive215'),floating('3fe0000000000000'),unknown()))),'eps'),
    ('nonfit','deferredComputedFloatNonfitReceive215',cast(computed_inf()),'eps'),
    ('zerodiv','deferredComputedFloatZeroDivReceive215',cast(binary('Div',floating('3ff0000000000000'),integer(0))),'eps'),
    ('computednan','deferredComputedFloatNanReceive215',cast(computed_nan()),'eps'),
    ('unarynonfit','deferredComputedFloatUnaryNonfitReceive215',cast(negate(cast(string('-9223372036854775808')))),'eps'),
    ('computednot','deferredComputedFloatNotReceive215',cast(node('NExprBooleanNot',binary('Div',yes_cast(),integer(2)))),'(0)'),
    ('computednannot','deferredComputedFloatNanNotReceive215',cast(node('NExprBooleanNot',computed_nan())),'eps'),
]

CATALOGUE = Path(__file__).with_name('computed_float_truth_default_reception_cases.json')
assert hashlib.sha256(CATALOGUE.read_bytes()).hexdigest() == 'ebf6b3c8f7dc20808a611e11a7b58c18f28e50ad4d2d31ba6405861c48dae2df'
row = next(row for row in json.loads(CATALOGUE.read_text()) if row['id'] == 'computed-float-truth-precision-modes')
assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
source = row['source']
handler = source[:source.index('function valueFirstReceive215(')]
reference = source[source.index('function referenceReceive215('):source.index("set_error_handler('warningReceive215');")]
setup = source[source.index("set_error_handler('warningReceive215');"):source.index('$gotReceive215 = valueFirstReceive215(')]
start = source.index('$gotReceive215 = referenceReceive215(')
end = source.index('$xReceive215 = 1.5;', start)
leading = handler + reference + setup + source[start:end]
assert hashlib.sha256(leading.encode()).hexdigest() == 'ff16d17f5e3d2131c101bee193c7c244d96735eaf1e1c4edbd15c850d49b8e30'

checks = [
    r'n_bits = 4609434218613702656 /\ i = 1',
    '$function_at(S.FUNCTIONS, porigin) = (pfunction)',
    'plenv_source = pfunction.ENV',
    r'plenv_source.NAMESPACE = eps /\ plenv_source.CONSTANTS = [($ptascii("YesReceive215"), $ptascii("true")), ($ptascii("NoReceive215"), $ptascii("false")), ($ptascii("NilReceive215"), $ptascii("null"))]',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_a, psparam_b, psparam_c, psparam_d, psparam_e]',
    '$lossy_optional_integer_mode(pfunction.SIGNATURE.PARAMETERS, true)',
    '~$lossy_optional_integer_mode(pfunction.SIGNATURE.PARAMETERS, false)',
    'S.CURRENT = (pcallcontext)',
    r'pcallcontext.ARGC = 3 /\ pcallcontext.HOLES = [0, 1] /\ pcallcontext.NAMED = eps',
]
for index,(letter,pattern,condition,value) in enumerate(zip('abcde',patterns,conditions,('$(-7)','$(-11)','13','$(-9223372036854775808)','9223372036854775807'))):
    checks.extend([
        rf'~psparam_{letter}.REQUIRED /\ ~psparam_{letter}.VARIADIC /\ $ptmasks(psparam_{letter}.TYPE) = ["int"]',
        f'psparam_{letter}.DEFAULT = PSDEFAULT expression_{letter} "int"',
        f'expression_{letter} = {pattern}',
        f'$lossy_optional_integer_default_in(plenv_source, expression_{letter}) = ({value})',
        f'expression_condition_{letter} = {condition}',
        f'$lossy_optional_integer_condition(plenv_source, expression_condition_{letter}) = ({str(letter not in "ad").lower()})',
        f'$default_parameter_origin(S, porigin, {index}) = PORIGIN n_unit pcpath_{letter}',
        f'porigin_{letter} = PORIGIN n_unit (pcpath_{letter} ++ [PCFIELD 6])',
        f'$origin_node(S.SOURCES, porigin_{letter}) = (expression_{letter})',
        f'$default_at(pfunction.DEFAULTS, {index}) = ({{INDEX {index}, ORIGIN porigin_{letter}, KIND PDSTORED}})',
        f'$compiled_read(S, porigin_{letter}) = (PINT {value})',
    ])
for suffix,function_name,pattern,projection in contrasts:
    checks.extend([
        f'$call_target(S, $ptascii("{function_name}"), eps) = (pfunction_{suffix})',
        f'pfunction_{suffix}.ORIGIN = PORIGIN n_unit pcpath_{suffix}_function',
        f'pfunction_{suffix}.ORIGIN =/= porigin',
        f'pfunction_{suffix}.SIGNATURE.PARAMETERS = [psparam_{suffix}]',
        rf'~psparam_{suffix}.REQUIRED /\ ~psparam_{suffix}.BYREF /\ ~psparam_{suffix}.VARIADIC /\ $ptmasks(psparam_{suffix}.TYPE) = ["int"]',
        f'psparam_{suffix}.DEFAULT = PSDEFAULT expression_{suffix} "deferred"',
        f'expression_{suffix} = {pattern}',
        f'$default_parameter_origin(S, pfunction_{suffix}.ORIGIN, 0) = PORIGIN n_unit pcpath_{suffix}',
        f'porigin_{suffix} = PORIGIN n_unit (pcpath_{suffix} ++ [PCFIELD 6])',
        f'$origin_node(S.SOURCES, porigin_{suffix}) = (expression_{suffix})',
        f'pfunction_{suffix}.DEFAULTS = [{{INDEX 0, ORIGIN porigin_{suffix}, KIND PDDEFERRED}}]',
        f'$compiled_read(S, porigin_{suffix}) = eps',
        f'$lossy_optional_integer_default_in(pfunction_{suffix}.ENV, expression_{suffix}) = {projection}',
        f'~$lossy_optional_integer_header(S, pfunction_{suffix}, pfunction_{suffix}.SIGNATURE.PARAMETERS, 0)',
        f'~$lossy_optional_integer_tail(S, pfunction_{suffix}, [psparam_{suffix}[.DEFAULT = PSDEFAULT expression_{suffix} "int"]], 0)',
        f'pcallcontext.FUNCTION =/= pfunction_{suffix}.ORIGIN',
        f'~$lossy_optional_integer_tail(S, pfunction_{suffix}[.DEFAULTS = [{{INDEX 0, ORIGIN porigin_{suffix}, KIND PDSTORED}}]], [psparam_{suffix}[.DEFAULT = PSDEFAULT expression_{suffix} "int"]], 0)',
    ])

checks.extend([
    '$lossy_optional_integer_header(S, pfunction, pfunction.SIGNATURE.PARAMETERS, 0)',
    'expression_a = NExprUnaryMinus expression_choice_a metadata_a',
    'expression_choice_a = NExprTernary expression_condition_a expression_unused_a expression_seven_a metadata_choice_a',
    'expression_b = NExprCastInt expression_choice_b metadata_b',
    'expression_choice_b = NExprTernary expression_condition_b expression_minus_eleven_b expression_unused_b metadata_choice_b',
    'expression_condition_b = NExprCastBool expression_numeric_b metadata_bool_b',
    'expression_c = NExprCastInt expression_choice_c metadata_c',
    'expression_choice_c = NExprTernary expression_condition_c expression_thirteen_c expression_unused_c metadata_choice_c',
    'expression_d = NExprTernary expression_condition_d expression_unused_d expression_minimum_d metadata_d',
    'expression_e = NExprTernary expression_condition_e expression_maximum_e expression_unused_e metadata_e',
    '$lossy_optional_integer_numeric(plenv_source, expression_condition_a) = (NFLOAT $hex_bits("8000000000000000", 0))',
    '$lossy_optional_integer_numeric(plenv_source, expression_numeric_b) = (NFLOAT $hex_bits("3fe0000000000000", 0))',
    '$lossy_optional_integer_numeric(plenv_source, expression_condition_c) = (NFLOAT $hex_bits("8000000000000001", 0))',
    '$lossy_optional_integer_numeric(plenv_source, expression_condition_d) = eps',
    '$lossy_optional_integer_numeric(plenv_source, expression_condition_e) = (NFLOAT $hex_bits("7ff0000000000000", 0))',
    'plenv_alias = plenv_source[.CONSTANTS = [($ptascii("YesReceive215"), $ptascii("false")), ($ptascii("NoReceive215"), $ptascii("false")), ($ptascii("NilReceive215"), $ptascii("null"))]]',
    '$lossy_optional_integer_default_in(plenv_alias, expression_a) = eps',
    '$lossy_optional_integer_condition(plenv_alias, expression_condition_a) = (true)',
    '$lossy_optional_integer_condition(plenv_alias, expression_condition_c) = (false)',
    '$lossy_optional_integer_numeric(plenv_alias, expression_condition_c) = (NFLOAT $hex_bits("8000000000000000", 0))',
    '~$lossy_optional_integer_header(S, pfunction[.ENV = plenv_alias], pfunction.SIGNATURE.PARAMETERS, 0)',
    '$lossy_optional_integer_condition($plempty(false), expression_condition_a) = eps',
    '$lossy_optional_integer_default_in($plempty(false), expression_b) = eps',
    'plenv_no_alias = plenv_source[.CONSTANTS = [($ptascii("YesReceive215"), $ptascii("true")), ($ptascii("NoReceive215"), $ptascii("true")), ($ptascii("NilReceive215"), $ptascii("null"))]]',
    '$lossy_optional_integer_numeric(plenv_no_alias, expression_numeric_b) = (NFLOAT $hex_bits("3ff8000000000000", 0))',
    'expression_same = NExprUnaryMinus (NScalarInt (INTEGER 7) metadata_a) metadata_a',
    '$lossy_optional_integer_default_in(plenv_source, expression_same) = ($(-7))',
    '~$lossy_optional_integer_tail(S, pfunction, [psparam_a[.DEFAULT = PSDEFAULT expression_same "int"]], 0)',
    'pfunction.DEFAULTS = [pdefault_a, pdefault_b, pdefault_c, pdefault_d, pdefault_e]',
    '~$lossy_optional_integer_tail(S, pfunction[.DEFAULTS = [pdefault_a, pdefault_b[.KIND = PDDEFERRED], pdefault_c, pdefault_d, pdefault_e]], [psparam_b], 1)',
    '~$lossy_optional_integer_tail(S, pfunction[.DEFAULTS = [pdefault_a[.ORIGIN = porigin_b], pdefault_b, pdefault_c, pdefault_d, pdefault_e]], [psparam_a], 0)',
    'S_no_pool = S[.POOLS = eps]',
    '$origin_node(S_no_pool.SOURCES, porigin_a) = (expression_a)',
    '$compiled_read(S_no_pool, porigin_a) = eps',
    '~$lossy_optional_integer_header(S_no_pool, pfunction, pfunction.SIGNATURE.PARAMETERS, 0)',
    'S_wrong_type = S[.POOLS = [{UNIT n_unit, CONSTANTS ([(PCONSTANT (pcpath_c ++ [PCFIELD 6]) (PBOOL true))])}]]',
    '$compiled_read(S_wrong_type, porigin_c) = (PBOOL true)',
    '~$lossy_optional_integer_tail(S_wrong_type, pfunction, [psparam_c], 2)',
    'S_wrong_value = S[.POOLS = [{UNIT n_unit, CONSTANTS ([(PCONSTANT (pcpath_c ++ [PCFIELD 6]) (PINT 14))])}]]',
    '$compiled_read(S_wrong_value, porigin_c) = (PINT 14)',
    '~$lossy_optional_integer_tail(S_wrong_value, pfunction, [psparam_c], 2)',
])

fixed_metadata = 'metadata_a'
expr_yes, expr_no, expr_nil = map(constant, ('YesReceive215', 'NoReceive215', 'NilReceive215'))
expr_unknown = unknown()
half = binary('Div', integer(1), integer(2))
zero = binary('Minus', floating('3fe0000000000000'), floating('3fe0000000000000'))
inf = binary('Mul', large(), integer(2))

# Binary64 truth uses the FLOAT tag without requiring an integer fit.
for expression, bits, truth in [
    (zero, '0000000000000000', False),
    (negate(zero), '8000000000000000', False),
    (half, '3fe0000000000000', True),
    (negate(binary('Div', integer(5), integer(2))), 'c004000000000000', True),
    (binary('Mul', floating('0000000000000001'), integer(1)), '0000000000000001', True),
    (negate(binary('Mul', floating('0000000000000001'), integer(1))), '8000000000000001', True),
    (binary('Mul', floating('0000000000000001'), floating('3fe0000000000000')), '0000000000000000', False),
    (binary('Plus', floating('8000000000000000'), floating('8000000000000000')), '8000000000000000', False),
    (inf, '7ff0000000000000', True),
    (negate(inf), 'fff0000000000000', True),
    (binary('Plus', integer(9223372036854775807), integer(1)), '43e0000000000000', True),
]:
    boolean = str(truth).lower()
    opposite = str(not truth).lower()
    checks.extend([
        f'$lossy_optional_integer_default_in(plenv_source, {expression}) = eps',
        f'$lossy_optional_integer_float_literal({expression}) = eps',
        f'$lossy_optional_integer_numeric(plenv_source, {expression}) = (NFLOAT $hex_bits("{bits}", 0))',
        f'$lossy_optional_integer_condition(plenv_source, {expression}) = ({boolean})',
        f'$lossy_optional_integer_condition(plenv_source, {node("NExprCastBool", expression)}) = ({boolean})',
        f'$lossy_optional_integer_condition(plenv_source, {node("NExprBooleanNot", expression)}) = ({opposite})',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(node("NExprCastBool", expression))}) = ({int(truth)})',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(node("NExprBooleanNot", expression))}) = ({int(not truth)})',
        f'$lossy_optional_integer_default_in(plenv_source, {ternary(expression, integer(7), integer(-11))}) = ({"7" if truth else "$(-11)"})',
        f'$lossy_optional_integer_string_in(plenv_source, {string_cast(expression)}) = eps',
    ])
checks.extend([
    f'$lossy_optional_integer_default_in(plenv_source, {cast(inf)}) = eps',
    f'$lossy_optional_integer_string_in(plenv_source, {dimension(string("019"), half)}) = eps',
    f'$lossy_optional_integer_string_in(plenv_source, {string_cast(node("NExprCastBool", half))}) = ([49])',
    f'$lossy_optional_integer_string_in(plenv_source, {string_cast(node("NExprBooleanNot", half))}) = (eps)',
])

# Selection truth retains the selected leaf; Numeric does not project selections.
for expression, truth in [
    (ternary(expr_yes, half, expr_unknown), True),
    (node('NExprTernary', half, 'ABSENT', expr_unknown), True),
    (binary('Coalesce', expr_nil, half), True),
    (binary('Coalesce', expr_no, expr_unknown), False),
    (ternary(zero, expr_unknown, half), True),
    (node('NExprTernary', zero, 'ABSENT', integer(0)), False),
]:
    checks.extend([
        f'$lossy_optional_integer_selection_shape({expression})',
        f'$lossy_optional_integer_condition(plenv_source, {expression}) = ({str(truth).lower()})',
    ])
selected = ternary(expr_yes, half, expr_unknown)
checks.extend([
    f'$lossy_optional_integer_numeric(plenv_source, {selected}) = eps',
    f'$lossy_optional_integer_default_in(plenv_source, {selected}) = eps',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(selected)}) = (0)',
    f'$lossy_optional_integer_string_in(plenv_source, {string_cast(selected)}) = eps',
])
for kind, left, right, truth in [
    ('BooleanAnd', zero, expr_unknown, False),
    ('LogicalAnd', zero, expr_unknown, False),
    ('BooleanOr', half, expr_unknown, True),
    ('LogicalOr', inf, expr_unknown, True),
    ('LogicalXor', zero, half, True),
    ('LogicalXor', half, inf, False),
]:
    expression = binary(kind, left, right)
    checks.extend([
        f'$lossy_optional_integer_condition(plenv_source, {expression}) = ({str(truth).lower()})',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = ({int(truth)})',
    ])
for expression in [binary('BooleanAnd', half, expr_unknown), binary('BooleanOr', zero, expr_unknown), binary('LogicalXor', expr_unknown, zero)]:
    checks.append(f'$lossy_optional_integer_condition(plenv_source, {expression}) = eps')

# NaN is numerically representable but fails the existing quiet-truth guard.
nan = binary('Minus', inf, inf)
checks.extend([
    f'$lossy_optional_integer_numeric(plenv_source, {nan}) = (NFLOAT n_nan)',
    '$pfcast_nan(PFLOAT n_nan)',
    '$number_bool(NFLOAT n_nan) = (true, true)',
])
for expression in [nan, node('NExprBooleanNot', nan), node('NExprCastBool', nan), ternary(nan, integer(7), integer(7))]:
    checks.append(f'$lossy_optional_integer_condition(plenv_source, {expression}) = eps')
for expression in [
    binary('Div', floating('3ff0000000000000'), integer(0)),
    binary('Div', floating('3ff0000000000000'), floating('8000000000000000')),
    binary('Plus', expr_yes, floating('3fe0000000000000')),
    binary('Mul', string('2'), integer(1)),
    binary('Pow', integer(2), integer(63)),
    integer(9223372036854775808),
    node('NExprVariable', 'BYTES "eA=="'), node('NExprArray', 'SEQUENCE eps'),
]:
    checks.extend([
        f'$lossy_optional_integer_numeric(plenv_source, {expression}) = eps',
        f'$lossy_optional_integer_condition(plenv_source, {expression}) = eps',
    ])
checks.extend([
    f'$lossy_optional_integer_condition(plenv_source, {string("0.0")}) = (true)',
    f'$lossy_optional_integer_condition(plenv_source, {float_cast(string("0.0"))}) = (false)',
    f'$lossy_optional_integer_numeric(plenv_source, {expr_yes}) = eps',
    f'$lossy_optional_integer_condition(plenv_source, {expr_yes}) = (true)',
    f'$lossy_optional_integer_condition(plenv_source, {expr_nil}) = (false)',
    f'$lossy_optional_integer_numeric(plenv_source, {binary("Plus", integer(1), integer(1))}) = (NINT 2)',
    f'$lossy_optional_integer_condition(plenv_source, {binary("Plus", integer(1), integer(1))}) = (true)',
    f'$lossy_optional_integer_condition(plenv_source, {negate(integer(9223372036854775808))}) = (true)',
    f'$lossy_optional_integer_condition(plenv_source, {binary("Div", cast(constant("true", True)), integer(2))}) = (true)',
    f'$lossy_optional_integer_condition(plenv_source, {binary("Div", cast(constant("YesReceive215", True)), integer(2))}) = eps',
])

# Fresh exact formulas cover older scalar/arithmetic/unary truth RHS promotions.
for expression, truth in [
    (binary('Plus', floating('3fe0000000000000'), integer(0)), True),
    (binary('Plus', floating('3fe0000000000000'), floating('3fe0000000000000')), True),
    (binary('Div', integer(5), integer(2)), True),
    (binary('Div', integer(-5), integer(2)), True),
    (binary('Plus', floating('3ff8000000000000'), integer(1)), True),
    (binary('Minus', negate(floating('401c000000000000')), floating('3fe0000000000000')), True),
    (binary('Mul', floating('3ff8000000000000'), integer(2)), True),
    (binary('Div', floating('4018000000000000'), integer(3)), True),
    (binary('Minus', cast(string('-9223372036854775808')), integer(1)), True),
    (node('NExprUnaryPlus', binary('Div', integer(5), integer(2))), True),
    (negate(negate(binary('Div', integer(5), integer(2)))), True),
    (negate(binary('Mul', floating('3ff8000000000000'), integer(2))), True),
    (node('NExprUnaryPlus', binary('Div', integer(0), floating('bfe0000000000000'))), False),
    (negate(binary('Div', integer(0), floating('bfe0000000000000'))), False),
    (negate(binary('Mul', floating('0000000000000001'), floating('3fe0000000000000'))), False),
    (negate(negate(cast(string('-9223372036854775808')))), True),
]:
    checks.append(f'$lossy_optional_integer_condition(plenv_source, {expression}) = ({str(truth).lower()})')
deep = half
for _ in range(8):
    deep = node('NExprCastBool', node('NExprBooleanNot', node('NExprBooleanNot', deep)))
checks.extend([
    f'$lossy_optional_integer_condition(plenv_source, {deep}) = (true)',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(deep)}) = (1)',
    f'$lossy_optional_integer_default_in(plenv_source, {ternary(deep, integer(7), expr_unknown)}) = (7)',
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
    r'S.STORE[n_cell] = DEFINED (PFLOAT 4615063718147915776) /\ n_cell <- S.REFCELLS',
    '$heap_owners($heap_graph(S), HCELL n_cell) = 2',
    r'$lookup(S.ENV, psparam_d.NAME) = eps /\ $lookup(S.ENV, psparam_e.NAME) = eps',
    'S.GLOBALTABLE = (psymboltable_global)',
    '$lookup(psymboltable_global.ENV, $ptascii("xReceive215")) = (n_cell)',
    '$lookup(psymboltable_global.ENV, $ptascii("countReceive215")) = (n_count)',
    'S.STORE[n_count] = DEFINED (PINT 1)',
    '$lossy_mixed_parameter_source_valid(S, LOSSY_MIXED_PARAMETER_RECEIVE porigin 2 n_cell n_bits i z)',
    '$call_task_valid(S, LOSSY_MIXED_PARAMETER_RECEIVE porigin 2 n_cell n_bits i z)',
    '$task_nodes(LOSSY_MIXED_PARAMETER_RECEIVE porigin 2 n_cell n_bits i z) = eps',
    '~$lossy_mixed_parameter_source_valid(S, LOSSY_MIXED_PARAMETER_RECEIVE porigin 2 n_a n_bits i z)',
    '~$lossy_mixed_parameter_source_valid(S, LOSSY_MIXED_PARAMETER_RECEIVE porigin 2 n_cell n_bits 2 z)',
    '~$lossy_mixed_parameter_source_valid(S, LOSSY_MIXED_PARAMETER_RECEIVE porigin 2 n_cell n_bits i $(z + 1))',
    '~$lossy_mixed_parameter_source_valid(S[.ORIGIN = (porigin_a)], LOSSY_MIXED_PARAMETER_RECEIVE porigin 2 n_cell n_bits i z)',
    r'$call_descriptors_valid(S) /\ $heap_valid($heap_graph(S))',
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
    r'S_body.EVENTS = S.EVENTS /\ S_body.STORE[n_count] = DEFINED (PINT 1)',
    r'$call_descriptors_valid(S_body) /\ $heap_valid($heap_graph(S_body))',
    'S_done = $drive_steps(S_body, 2000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    r'~((HCELL n_a) <- S_done.ALLOCATIONS) /\ ~((HCELL n_b) <- S_done.ALLOCATIONS) /\ ~((HCELL n_d) <- S_done.ALLOCATIONS) /\ ~((HCELL n_e) <- S_done.ALLOCATIONS)',
    r'S_done.STORE[n_cell] = DEFINED (PINT 1) /\ $heap_owners($heap_graph(S_done), HCELL n_cell) = 1',
    'S_done.STORE[n_count] = DEFINED (PINT 1)',
    '$lookup(S_done.ENV, $ptascii("gotReceive215")) = (n_got)',
    'S_done.STORE[n_got] = DEFINED (PINT 1)',
    r'$call_descriptors_valid(S_done) /\ $heap_valid($heap_graph(S_done))',
])

CASES = {'computed-float-truth-reference-leading': {
    'source': leading,
    'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 2 n_cell n_bits i z]',
    'checks': checks,
}}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
