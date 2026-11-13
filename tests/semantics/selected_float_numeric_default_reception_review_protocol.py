#!/usr/bin/env python3
"""Selected FLOAT numeric operands retain tags, casts, source authority and owners."""
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
    return constant('UnselectedReceive216')


def negate(child):
    return node('NExprUnaryMinus', child)


yes = lambda: cast(constant('YesReceive216'))
no = lambda: cast(constant('NoReceive216'))
large = lambda: floating('7fe1ccf385ebc8a0')
computed_inf = lambda: binary('Mul', large(), integer(2))
computed_nan = lambda: binary('Minus', computed_inf(), computed_inf())
selected = [
    ternary(constant('YesReceive216'), negate(floating('401e000000000000')), unknown()),
    ternary(constant('NoReceive216'), unknown(), negate(floating('4016000000000000'))),
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
    ternary(cast(arithmetic[3]), unknown(), cast(string('-9223372036854775808tail'))),
    ternary(cast(arithmetic[4]), cast(string('9' * 24)), unknown()),
]
contrasts = [
    ('floatnot','deferredFloatNotReceive216',cast(node('NExprBooleanNot',floating('3fe0000000000000'))),'(0)'),
    ('negative','deferredNegativeIndexReceive216',cast(dimension(string('10'),string('-1'))),'eps'),
    ('floatindex','deferredFloatIndexReceive216',cast(dimension(string('10'),string('1.0'))),'eps'),
    ('floatstring','deferredFloatStringReceive216',cast(string_cast(floating('3fe0000000000000'))),'eps'),
    ('computednegative','deferredComputedNegativeIndexReceive216',cast(dimension(string('10'),binary('Minus',integer(0),integer(1)))),'eps'),
    ('selectedfloat','deferredSelectedFloatStringReceive216',cast(string_cast(ternary(constant('YesReceive216'),floating('3fe0000000000000'),unknown()))),'eps'),
    ('nonfit','deferredComputedFloatNonfitReceive216',cast(computed_inf()),'eps'),
    ('zerodiv','deferredComputedFloatZeroDivReceive216',cast(binary('Div',floating('3ff0000000000000'),integer(0))),'eps'),
    ('computednan','deferredComputedFloatNanReceive216',cast(computed_nan()),'eps'),
    ('unarynonfit','deferredComputedFloatUnaryNonfitReceive216',cast(negate(cast(string('-9223372036854775808')))),'eps'),
    ('computednot','deferredComputedFloatNotReceive216',cast(node('NExprBooleanNot',binary('Div',yes(),integer(2)))),'(0)'),
    ('computednannot','deferredComputedFloatNanNotReceive216',cast(node('NExprBooleanNot',computed_nan())),'eps'),
    ('selectednonfit','deferredSelectedFloatArithmeticNonfitReceive216',cast(binary('Plus',ternary(constant('YesReceive216'),computed_inf(),unknown()),integer(0))),'eps'),
    ('coalescenonfit','deferredSelectedFloatCoalesceNonfitReceive216',cast(binary('Plus',binary('Coalesce',computed_inf(),unknown()),integer(0))),'eps'),
    ('selectednan','deferredSelectedFloatArithmeticNanReceive216',cast(binary('Minus',ternary(constant('YesReceive216'),computed_inf(),unknown()),ternary(constant('NoReceive216'),unknown(),computed_inf()))),'eps'),
]
CATALOGUE = Path(__file__).with_name('selected_float_numeric_default_reception_cases.json')
assert hashlib.sha256(CATALOGUE.read_bytes()).hexdigest() == 'a575ef184107c030dfcea2daafcc7bb0b9e5dd002a0266adb0416d99dac06afe'
row = next(row for row in json.loads(CATALOGUE.read_text()) if row['id'] == 'selected-float-numeric-precision-modes')
assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
source = row['source']
handler = source[:source.index('function valueFirstReceive216(')]
reference = source[source.index('function referenceReceive216('):source.index("set_error_handler('warningReceive216');")]
setup = source[source.index("set_error_handler('warningReceive216');"):source.index('$gotReceive216 = valueFirstReceive216(')]
start = source.index('$gotReceive216 = referenceReceive216(')
end = source.index('$xReceive216 = 1.5;', start)
leading = handler + reference + setup + source[start:end]
assert hashlib.sha256(leading.encode()).hexdigest() == '5270e3349a91bb92f33428c82036179b3628cdd426c9d1604ca686d814579b7b'

checks = [
    r'n_bits = 4609434218613702656 /\ i = 1',
    '$function_at(S.FUNCTIONS, porigin) = (pfunction)',
    'plenv_source = pfunction.ENV',
    r'plenv_source.NAMESPACE = eps /\ plenv_source.CONSTANTS = [($ptascii("YesReceive216"), $ptascii("true")), ($ptascii("NoReceive216"), $ptascii("false")), ($ptascii("NilReceive216"), $ptascii("null"))]',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_a, psparam_b, psparam_c, psparam_d, psparam_e]',
    '$lossy_optional_integer_mode(pfunction.SIGNATURE.PARAMETERS, true)',
    '~$lossy_optional_integer_mode(pfunction.SIGNATURE.PARAMETERS, false)',
    'S.CURRENT = (pcallcontext)',
    r'pcallcontext.ARGC = 3 /\ pcallcontext.HOLES = [0, 1] /\ pcallcontext.NAMED = eps',
]
for index,(letter,pattern,selection,operation,value,leaf_value,selected_bits,operation_bits) in enumerate(zip('abcde',patterns,selected,arithmetic,('$(-7)','$(-11)','13','$(-9223372036854775808)','9223372036854775807'),('$(-7)','$(-5)','13','0','1'),('c01e000000000000','c016000000000000','402b000000000000','3fe0000000000000','3ff8000000000000'),('c01e000000000000','c026000000000000','402b000000000000','0000000000000000','3ff0000000000000'))):
    checks.extend([
        rf'~psparam_{letter}.REQUIRED /\ ~psparam_{letter}.VARIADIC /\ $ptmasks(psparam_{letter}.TYPE) = ["int"]',
        f'psparam_{letter}.DEFAULT = PSDEFAULT expression_{letter} "int"',
        f'expression_{letter} = {pattern}',
        f'$lossy_optional_integer_default_in(plenv_source, expression_{letter}) = ({value})',
        f'expression_selected_{letter} = {selection}',
        f'expression_numeric_{letter} = {operation}',
        f'$lossy_optional_integer_selection_shape(expression_selected_{letter})',
        f'$lossy_optional_integer_default_in(plenv_source, expression_selected_{letter}) = eps',
        f'$lossy_optional_integer_numeric(plenv_source, expression_selected_{letter}) = (NFLOAT $hex_bits("{selected_bits}", 0))',
        f'$lossy_optional_integer_numeric(plenv_source, expression_numeric_{letter}) = (NFLOAT $hex_bits("{operation_bits}", 0))',
        f'$lossy_optional_integer_condition(plenv_source, expression_selected_{letter}) = (true)',
        f'$lossy_optional_integer_cast_leaf(plenv_source, expression_selected_{letter}) = (expression_leaf_{letter})',
        f'$lossy_optional_integer_default_in(plenv_source, NExprCastInt expression_selected_{letter} metadata_pre_1) = ({leaf_value})',
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
    ])
for letter,bits in [('a','c01e000000000000'),('b','c016000000000000'),('c','402b000000000000'),('d','3fe0000000000000'),('e','3ff8000000000000')]:
    checks.extend([
        f'$lossy_optional_integer_numeric(plenv_source, expression_leaf_{letter}) = (NFLOAT $hex_bits("{bits}", 0))',
        f'$lossy_optional_integer_numeric($plempty(false), expression_selected_{letter}) = eps',
    ])
checks.extend([
    '$lossy_optional_integer_header(S, pfunction, pfunction.SIGNATURE.PARAMETERS, 0)',
    'plenv_alias = plenv_source[.CONSTANTS = [($ptascii("YesReceive216"), $ptascii("false")), ($ptascii("NoReceive216"), $ptascii("false")), ($ptascii("NilReceive216"), $ptascii("null"))]]',
    '$lossy_optional_integer_default_in(plenv_alias, expression_a) = eps',
    '$lossy_optional_integer_default_in(plenv_alias, expression_b) = ($(-5))',
    '~$lossy_optional_integer_header(S, pfunction[.ENV = plenv_alias], pfunction.SIGNATURE.PARAMETERS, 0)',
    'expression_a = NExprCastInt expression_numeric_a metadata_a',
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
expr_yes, expr_no, expr_nil = map(constant, ('YesReceive216', 'NoReceive216', 'NilReceive216'))
expr_unknown = unknown()
half = binary('Div', integer(1), integer(2))
inf = computed_inf()

# FLOAT tags survive every admitted finite selection, including integral-valued FLOATs.
for expression, bits, result in [
    (ternary(expr_yes, floating('8000000000000000'), expr_unknown), '8000000000000000', 0),
    (ternary(expr_no, expr_unknown, floating('0000000000000001')), '0000000000000001', 0),
    (ternary(expr_yes, binary('Div', integer(5), integer(2)), expr_unknown), '4004000000000000', 2),
    (node('NExprTernary', floating('8000000000000000'), 'ABSENT', floating('bfe0000000000000')), 'bfe0000000000000', 0),
    (node('NExprTernary', half, 'ABSENT', expr_unknown), '3fe0000000000000', 0),
    (binary('Coalesce', expr_nil, floating('3ff0000000000000')), '3ff0000000000000', 1),
    (binary('Coalesce', floating('0000000000000000'), expr_unknown), '0000000000000000', 0),
    (binary('Coalesce', floating('c01e000000000000'), expr_unknown), 'c01e000000000000', -7),
]:
    value = str(result) if result >= 0 else f'$({result})'
    checks.extend([
        f'$lossy_optional_integer_default_in(plenv_source, {expression}) = eps',
        f'$lossy_optional_integer_float_literal({expression}) = eps',
        f'$lossy_optional_integer_numeric(plenv_source, {expression}) = (NFLOAT $hex_bits("{bits}", 0))',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = ({value})',
        f'$lossy_optional_integer_string_in(plenv_source, {string_cast(expression)}) = eps',
    ])

# Integer selections keep the old NINT path, never an equal-valued FLOAT projection.
for expression, result in [
    (ternary(expr_yes, integer(7), expr_unknown), 7),
    (node('NExprTernary', integer(1), 'ABSENT', expr_unknown), 1),
    (binary('Coalesce', expr_nil, integer(0)), 0),
]:
    checks.extend([
        f'$lossy_optional_integer_default_in(plenv_source, {expression}) = ({result})',
        f'$lossy_optional_integer_numeric(plenv_source, {expression}) = (NINT {result})',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = ({result})',
    ])
for child, result in [(expr_yes, 1), (expr_no, 0), (expr_nil, 0), (string('0.0'), 0)]:
    expression = ternary(expr_yes, child, expr_unknown)
    checks.extend([
        f'$lossy_optional_integer_numeric(plenv_source, {expression}) = eps',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = ({result})',
        f'$lossy_optional_integer_numeric(plenv_source, {binary("Plus", expression, integer(1))}) = eps',
    ])

# The old coalesce fit bound applies to nonnull LEFT leaves, not selected RIGHT leaves.
selected_inf = ternary(expr_yes, inf, expr_unknown)
right_inf = binary('Coalesce', expr_nil, inf)
left_inf = binary('Coalesce', inf, expr_unknown)
for expression in [selected_inf, right_inf]:
    checks.extend([
        f'$lossy_optional_integer_numeric(plenv_source, {expression}) = (NFLOAT $hex_bits("7ff0000000000000", 0))',
        f'$lossy_optional_integer_condition(plenv_source, {expression}) = (true)',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = eps',
    ])
checks.extend([
    f'$lossy_optional_integer_numeric(plenv_source, {left_inf}) = eps',
    f'$lossy_optional_integer_cast_leaf(plenv_source, {left_inf}) = eps',
    f'$lossy_optional_integer_condition(plenv_source, {left_inf}) = (true)',
    f'$lossy_optional_integer_numeric(plenv_source, {binary("Plus", left_inf, integer(0))}) = eps',
    f'$lossy_optional_integer_numeric(plenv_source, {binary("Plus", selected_inf, integer(0))}) = (NFLOAT $hex_bits("7ff0000000000000", 0))',
])
nan = binary('Minus', inf, inf)
for expression in [ternary(expr_yes, nan, expr_unknown), binary('Coalesce', expr_nil, nan), binary('Minus', selected_inf, right_inf)]:
    checks.extend([
        f'$lossy_optional_integer_numeric(plenv_source, {expression}) = (NFLOAT n_nan)',
        '$pfcast_nan(PFLOAT n_nan)',
        f'$lossy_optional_integer_condition(plenv_source, {expression}) = eps',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = eps',
    ])
for expression in [
    binary('Coalesce', nan, expr_unknown), ternary(expr_unknown, half, half),
    ternary(expr_yes, integer(9223372036854775808), expr_unknown),
    ternary(expr_yes, binary('Div', integer(1), integer(0)), expr_unknown),
]:
    checks.append(f'$lossy_optional_integer_numeric(plenv_source, {expression}) = eps')

# Numeric selection composes through arithmetic/signs while key/byte domains stay separate.
selected_half = ternary(expr_yes, half, expr_unknown)
for expression, bits, result in [
    (node('NExprUnaryPlus', selected_half), '3fe0000000000000', 0),
    (negate(selected_half), 'bfe0000000000000', 0),
    (binary('Plus', selected_half, floating('3fe0000000000000')), '3ff0000000000000', 1),
    (binary('Minus', selected_half, floating('3ff8000000000000')), 'bff0000000000000', -1),
    (binary('Mul', selected_half, integer(3)), '3ff8000000000000', 1),
    (binary('Div', selected_half, integer(2)), '3fd0000000000000', 0),
]:
    value = str(result) if result >= 0 else f'$({result})'
    checks.extend([
        f'$lossy_optional_integer_default_in(plenv_source, {expression}) = eps',
        f'$lossy_optional_integer_numeric(plenv_source, {expression}) = (NFLOAT $hex_bits("{bits}", 0))',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = ({value})',
    ])
checks.extend([
    f'$lossy_optional_integer_string_in(plenv_source, {dimension(string("019"), selected_half)}) = eps',
    f'$lossy_optional_integer_string_in(plenv_source, {string_cast(selected_half)}) = eps',
    f'$lossy_optional_integer_numeric(plenv_source, {ternary(expr_yes, string("0.5"), expr_unknown)}) = eps',
    f'$lossy_optional_integer_numeric(plenv_source, {binary("Plus", expr_yes, integer(1))}) = eps',
])
# Preserve the exact old selected-literal and selected-computed unary formulas freshly.
checks.extend([
    'plenv_old = plenv_source[.CONSTANTS = [($ptascii("YesReceive214"), $ptascii("true")), ($ptascii("NoReceive214"), $ptascii("false")), ($ptascii("NilReceive214"), $ptascii("null"))]]',
])
old_selected = ternary(constant('YesReceive214'), floating('3fe0000000000000'), constant('UnselectedReceive214'))
for expression,bits in [(old_selected,'3fe0000000000000'),(node('NExprUnaryPlus',old_selected),'3fe0000000000000'),(negate(old_selected),'bfe0000000000000')]:
    checks.extend([
        f'$lossy_optional_integer_numeric(plenv_old, {expression}) = (NFLOAT $hex_bits("{bits}", 0))',
        f'$lossy_optional_integer_default_in(plenv_old, {cast(expression)}) = (0)',
    ])
deep = half
for _ in range(8):
    deep = ternary(expr_yes, binary('Plus', deep, floating('0000000000000000')), expr_unknown)
checks.extend([
    f'$lossy_optional_integer_numeric(plenv_source, {deep}) = (NFLOAT $hex_bits("3fe0000000000000", 0))',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(deep)}) = (0)',
    f'$lossy_optional_integer_condition(plenv_source, {deep}) = (true)',
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
    '$lookup(psymboltable_global.ENV, $ptascii("xReceive216")) = (n_cell)',
    '$lookup(psymboltable_global.ENV, $ptascii("countReceive216")) = (n_count)',
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
    '$lookup(S_done.ENV, $ptascii("gotReceive216")) = (n_got)',
    'S_done.STORE[n_got] = DEFINED (PINT 1)',
    r'$call_descriptors_valid(S_done) /\ $heap_valid($heap_graph(S_done))',
])

CASES = {'selected-float-numeric-reference-leading': {
    'source': leading,
    'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 2 n_cell n_bits i z]',
    'checks': checks,
}}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
