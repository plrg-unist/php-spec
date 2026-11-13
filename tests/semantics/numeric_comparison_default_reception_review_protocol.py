#!/usr/bin/env python3
"""Typed numeric comparisons preserve tags, unordered results and receive authority."""
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
    return constant('UnselectedReceive220')


def negate(child):
    return node('NExprUnaryMinus', child)


yes = lambda: cast(constant('YesReceive220'))
no = lambda: cast(constant('NoReceive220'))
large = lambda: floating('7fe1ccf385ebc8a0')
computed_inf = lambda: binary('Mul', large(), integer(2))
computed_nan = lambda: binary('Minus', computed_inf(), computed_inf())
# Each syntactic occurrence receives distinct metadata before binding actual source nodes.
def maximum():
    return binary('Minus',cast(string('9223372036854775807tail')),cast(constant('NoReceive220')))

def actual_nan():
    return binary('Minus',binary('Mul',large(),binary('Plus',integer(2),cast(constant('NoReceive220')))),binary('Mul',large(),integer(2)))

comparison_a_less=binary('Smaller',integer(7),binary('Plus',float_cast(constant('YesReceive220')),floating('401a000000000000')))
comparison_a_le=binary('SmallerOrEqual',integer(7),binary('Plus',float_cast(constant('YesReceive220')),floating('401a000000000000')))
condition_a=binary('BooleanAnd',comparison_a_less,comparison_a_le)
comparison_b_equal=binary('Equal',maximum(),float_cast(maximum()))
comparison_b_identity=binary('NotIdentical',maximum(),float_cast(maximum()))
spaceship_b=binary('Spaceship',maximum(),float_cast(maximum()))
condition_b=binary('BooleanAnd',binary('BooleanAnd',comparison_b_equal,comparison_b_identity),binary('Identical',spaceship_b,integer(0)))
comparison_c_zero=binary('Identical',float_cast(constant('NoReceive220')),negate(floating('0000000000000000')))
comparison_c_identity=binary('Identical',cast(constant('YesReceive220')),float_cast(constant('YesReceive220')))
condition_c=binary('BooleanAnd',comparison_c_zero,node('NExprBooleanNot',comparison_c_identity))
comparison_d_greater=binary('Greater',actual_nan(),integer(0))
comparison_d_ge=binary('GreaterOrEqual',actual_nan(),integer(0))
condition_d=binary('BooleanOr',comparison_d_greater,comparison_d_ge)
condition_e=binary('NotEqual',actual_nan(),float_cast(constant('NilReceive220')))
conditions=[condition_a,condition_b,condition_c,condition_d,condition_e]
patterns=[negate(ternary(condition_a,integer(7),unknown())),ternary(condition_b,cast(string('-11tail')),unknown()),ternary(condition_c,cast(string('13tail')),unknown()),ternary(condition_d,unknown(),cast(string('-9223372036854775808tail'))),ternary(condition_e,cast(string('9'*24)),unknown())]

contrasts = [
    ('floatnot','deferredFloatNotReceive220',cast(node('NExprBooleanNot',floating('3fe0000000000000'))),'(0)'),
    ('negative','deferredNegativeIndexReceive220',cast(dimension(string('10'),string('-1'))),'eps'),
    ('floatindex','deferredFloatIndexReceive220',cast(dimension(string('10'),string('1.0'))),'eps'),
    ('floatstring','deferredFloatStringReceive220',cast(string_cast(floating('3fe0000000000000'))),'eps'),
    ('computednegative','deferredComputedNegativeIndexReceive220',cast(dimension(string('10'),binary('Minus',integer(0),integer(1)))),'eps'),
    ('selectedfloat','deferredSelectedFloatStringReceive220',cast(string_cast(ternary(constant('YesReceive220'),floating('3fe0000000000000'),unknown()))),'eps'),
    ('nonfit','deferredComputedFloatNonfitReceive220',cast(computed_inf()),'eps'),
    ('zerodiv','deferredComputedFloatZeroDivReceive220',cast(binary('Div',floating('3ff0000000000000'),integer(0))),'eps'),
    ('computednan','deferredComputedFloatNanReceive220',cast(computed_nan()),'eps'),
    ('unarynonfit','deferredComputedFloatUnaryNonfitReceive220',cast(negate(cast(string('-9223372036854775808')))),'eps'),
    ('computednot','deferredComputedFloatNotReceive220',cast(node('NExprBooleanNot',binary('Div',yes(),integer(2)))),'(0)'),
    ('computednannot','deferredComputedFloatNanNotReceive220',cast(node('NExprBooleanNot',computed_nan())),'eps'),
    ('selectednonfit','deferredSelectedFloatArithmeticNonfitReceive220',cast(binary('Plus',ternary(constant('YesReceive220'),computed_inf(),unknown()),integer(0))),'eps'),
    ('coalescenonfit','deferredSelectedFloatCoalesceNonfitReceive220',cast(binary('Plus',binary('Coalesce',computed_inf(),unknown()),integer(0))),'eps'),
    ('selectednan','deferredSelectedFloatArithmeticNanReceive220',cast(binary('Minus',ternary(constant('YesReceive220'),computed_inf(),unknown()),ternary(constant('NoReceive220'),unknown(),computed_inf()))),'eps'),
    ('floatcastnan','deferredNumericFloatCastNanReceive220',cast(float_cast(computed_nan())),'eps'),
    ('floatcastnonfit','deferredNumericFloatCastNonfitReceive220',cast(float_cast(cast(string('9223372036854775807')))),'eps'),
    ('scalarfloatnonfit','deferredScalarFloatCastNonfitReceive220',cast(float_cast(string('1e999'))),'eps'),
    ('selectedscalarfloatnonfit','deferredSelectedScalarFloatCastNonfitReceive220',cast(float_cast(ternary(constant('YesReceive220'),string('1e999'),unknown()))),'eps'),
]

CATALOGUE = Path(__file__).with_name('numeric_comparison_default_reception_cases.json')
assert hashlib.sha256(CATALOGUE.read_bytes()).hexdigest() == '22ddeca36823c846f29f148ddc64d1a6db30891f3dc880e7c0b796a07374d8b4'
row = next(row for row in json.loads(CATALOGUE.read_text()) if row['id'] == 'numeric-comparison-precision-modes')
assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
source = row['source']
handler = source[:source.index('function valueFirstReceive220(')]
reference = source[source.index('function referenceReceive220('):source.index("set_error_handler('warningReceive220');")]
setup = source[source.index("set_error_handler('warningReceive220');"):source.index('$gotReceive220 = valueFirstReceive220(')]
start = source.index('$gotReceive220 = referenceReceive220(')
end = source.index('$xReceive220 = 1.5;', start)
leading = handler + reference + setup + source[start:end]
assert hashlib.sha256(leading.encode()).hexdigest() == 'e43af3eb01e8c7d6763ba6cae34a9b336e5aeadf86e16239924ee1a98ff97932'


checks=[
    r'n_bits = 4609434218613702656 /\ i = 1',
    '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
    'plenv_source=pfunction.ENV',
    r'plenv_source.NAMESPACE = eps /\ plenv_source.CONSTANTS = [($ptascii("YesReceive220"),$ptascii("true")),($ptascii("NoReceive220"),$ptascii("false")),($ptascii("NilReceive220"),$ptascii("null"))]',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_a,psparam_b,psparam_c,psparam_d,psparam_e]',
    '$lossy_optional_integer_mode(pfunction.SIGNATURE.PARAMETERS,true)',
    '~$lossy_optional_integer_mode(pfunction.SIGNATURE.PARAMETERS,false)',
    'S.CURRENT = (pcallcontext)',
    r'pcallcontext.ARGC = 3 /\ pcallcontext.HOLES = [0,1] /\ pcallcontext.NAMED = eps',
]
for index,(letter,pattern,condition,value) in enumerate(zip('abcde',patterns,conditions,('$(-7)','$(-11)','13','$(-9223372036854775808)','9223372036854775807'))):
    checks.extend([
        rf'~psparam_{letter}.REQUIRED /\ ~psparam_{letter}.VARIADIC /\ $ptmasks(psparam_{letter}.TYPE) = ["int"]',
        f'psparam_{letter}.DEFAULT = PSDEFAULT expression_{letter} "int"',
        f'expression_{letter} = {pattern}',
        f'expression_condition_{letter} = {condition}',
        f'$lossy_optional_integer_default_in(plenv_source,expression_condition_{letter}) = eps',
        f'$lossy_optional_integer_numeric(plenv_source,expression_condition_{letter}) = eps',
        f'$lossy_optional_integer_default_in(plenv_source,expression_{letter}) = ({value})',
        f'$lossy_optional_integer_condition(plenv_source,expression_condition_{letter}) = ({str(letter != "d").lower()})',
        f'$default_parameter_origin(S,porigin,{index}) = PORIGIN n_unit pcpath_{letter}',
        f'porigin_{letter} = PORIGIN n_unit (pcpath_{letter} ++ [PCFIELD 6])',
        f'$origin_node(S.SOURCES,porigin_{letter}) = (expression_{letter})',
        f'$default_at(pfunction.DEFAULTS,{index}) = ({{INDEX {index},ORIGIN porigin_{letter},KIND PDSTORED}})',
        f'$compiled_read(S,porigin_{letter}) = (PINT {value})',
    ])
checks.extend([
    f'expression_less_a = {comparison_a_less}',
    'expression_less_a = NExprBinaryOpSmaller expression_left_a expression_right_a metadata_less_a',
    '$lossy_optional_integer_numeric(plenv_source,expression_left_a) = (NINT 7)',
    '$lossy_optional_integer_numeric(plenv_source,expression_right_a) = (NFLOAT $hex_bits("401e000000000000",0))',
    f'expression_equal_b = {comparison_b_equal}',
    'expression_equal_b = NExprBinaryOpEqual expression_int_b expression_float_b metadata_equal_b',
    '$lossy_optional_integer_numeric(plenv_source,expression_int_b) = (NINT 9223372036854775807)',
    '$lossy_optional_integer_numeric(plenv_source,expression_float_b) = (NFLOAT $hex_bits("43e0000000000000",0))',
    f'expression_spaceship_b = {spaceship_b}',
    '$lossy_optional_integer_default_in(plenv_source,expression_spaceship_b) = (0)',
    '$lossy_optional_integer_numeric(plenv_source,expression_spaceship_b) = (NINT 0)',
    f'expression_zero_c = {comparison_c_zero}',
    'expression_zero_c = NExprBinaryOpIdentical expression_pluszero_c expression_minuszero_c metadata_zero_c',
    '$lossy_optional_integer_numeric(plenv_source,expression_pluszero_c) = (NFLOAT 0)',
    '$lossy_optional_integer_numeric(plenv_source,expression_minuszero_c) = (NFLOAT $hex_bits("8000000000000000",0))',
    f'expression_identity_c = {comparison_c_identity}',
    'expression_identity_c = NExprBinaryOpIdentical expression_int_c expression_float_c metadata_identity_c',
    '$lossy_optional_integer_numeric(plenv_source,expression_int_c) = (NINT 1)',
    '$lossy_optional_integer_numeric(plenv_source,expression_float_c) = (NFLOAT $hex_bits("3ff0000000000000",0))',
    f'expression_greater_d = {comparison_d_greater}',
    'expression_greater_d = NExprBinaryOpGreater expression_nan_d expression_zero_d metadata_greater_d',
    '$lossy_optional_integer_numeric(plenv_source,expression_nan_d) = (NFLOAT n_nan_d)',
    '$pfcast_nan(PFLOAT n_nan_d)',
    '$lossy_optional_integer_condition(plenv_source,expression_nan_d) = eps',
    f'expression_condition_e = {condition_e}',
    'expression_condition_e = NExprBinaryOpNotEqual expression_nan_e expression_float_e metadata_ne_e',
    '$lossy_optional_integer_numeric(plenv_source,expression_nan_e) = (NFLOAT n_nan_e)',
    '$pfcast_nan(PFLOAT n_nan_e)',
    '$lossy_optional_integer_numeric(plenv_source,expression_float_e) = (NFLOAT 0)',
])
for suffix,function_name,pattern,projection in contrasts:
    checks.extend([
        f'$call_target(S,$ptascii("{function_name}"),eps) = (pfunction_{suffix})',
        f'pfunction_{suffix}.ORIGIN = PORIGIN n_unit pcpath_{suffix}_function',
        f'pfunction_{suffix}.ORIGIN =/= porigin',
        f'pfunction_{suffix}.SIGNATURE.PARAMETERS = [psparam_{suffix}]',
        rf'~psparam_{suffix}.REQUIRED /\ ~psparam_{suffix}.BYREF /\ ~psparam_{suffix}.VARIADIC /\ $ptmasks(psparam_{suffix}.TYPE) = ["int"]',
        f'psparam_{suffix}.DEFAULT = PSDEFAULT expression_{suffix} "deferred"',
        f'expression_{suffix} = {pattern}',
        f'$default_parameter_origin(S,pfunction_{suffix}.ORIGIN,0) = PORIGIN n_unit pcpath_{suffix}',
        f'porigin_{suffix} = PORIGIN n_unit (pcpath_{suffix} ++ [PCFIELD 6])',
        f'$origin_node(S.SOURCES,porigin_{suffix}) = (expression_{suffix})',
        f'pfunction_{suffix}.DEFAULTS = [{{INDEX 0,ORIGIN porigin_{suffix},KIND PDDEFERRED}}]',
        f'$compiled_read(S,porigin_{suffix}) = eps',
        f'$lossy_optional_integer_default_in(pfunction_{suffix}.ENV,expression_{suffix}) = {projection}',
        f'~$lossy_optional_integer_header(S,pfunction_{suffix},pfunction_{suffix}.SIGNATURE.PARAMETERS,0)',
        f'~$lossy_optional_integer_tail(S,pfunction_{suffix},[psparam_{suffix}[.DEFAULT = PSDEFAULT expression_{suffix} "int"]],0)',
        f'pcallcontext.FUNCTION =/= pfunction_{suffix}.ORIGIN',
        f'~$lossy_optional_integer_tail(S,pfunction_{suffix}[.DEFAULTS=[{{INDEX 0,ORIGIN porigin_{suffix},KIND PDSTORED}}]],[psparam_{suffix}[.DEFAULT=PSDEFAULT expression_{suffix} "int"]],0)',
    ])
checks.extend([
    '$lossy_optional_integer_header(S, pfunction, pfunction.SIGNATURE.PARAMETERS, 0)',
    'plenv_alias = plenv_source[.CONSTANTS = [($ptascii("YesReceive220"), $ptascii("false")), ($ptascii("NoReceive220"), $ptascii("false")), ($ptascii("NilReceive220"), $ptascii("null"))]]',
    '$lossy_optional_integer_default_in(plenv_alias, expression_a) = eps',
    '$lossy_optional_integer_default_in(plenv_alias, expression_b) = ($(-11))',
    '~$lossy_optional_integer_header(S, pfunction[.ENV = plenv_alias], pfunction.SIGNATURE.PARAMETERS, 0)',
    'expression_a = NExprUnaryMinus expression_branch_a metadata_a',
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


fixed_metadata='metadata_a'
expr_yes,expr_no,expr_nil=map(constant,('YesReceive220','NoReceive220','NilReceive220'))
expr_unknown=unknown()
checks.extend([
    'plenv_no_true=plenv_source[.CONSTANTS=[($ptascii("YesReceive220"),$ptascii("true")),($ptascii("NoReceive220"),$ptascii("true")),($ptascii("NilReceive220"),$ptascii("null"))]]',
    '$lossy_optional_integer_default_in(plenv_no_true,expression_b) = ($(-11))',
    '$lossy_optional_integer_default_in(plenv_no_true,expression_c) = eps',
    '~$lossy_optional_integer_header(S,pfunction[.ENV=plenv_no_true],pfunction.SIGNATURE.PARAMETERS,0)',
    '$lossy_optional_integer_default_in($plempty(false),expression_a) = eps',
    '~$lossy_optional_integer_header(S,pfunction[.ENV=$plempty(false)],pfunction.SIGNATURE.PARAMETERS,0)',
])

# Expected outcomes are fixed independently of the pure comparison kernels.
# Equal, NotEqual, Identical, NotIdentical, Smaller, SmallerOrEqual, Greater, GreaterOrEqual.
for left,right,results,order in [
    (integer(1),floating('3ff0000000000000'),(True,False,False,True,False,True,False,True),0),
    (integer(7),floating('401e000000000000'),(False,True,False,True,True,True,False,False),-1),
    (floating('401e000000000000'),integer(7),(False,True,False,True,False,False,True,True),1),
    (floating('0000000000000000'),floating('8000000000000000'),(True,False,True,False,False,True,False,True),0),
    (floating('7ff8000000000000'),integer(0),(False,True,False,True,False,False,False,False),1),
    (integer(0),floating('fff8000000000001'),(False,True,False,True,False,False,False,False),1),
    (floating('7ff8000000000000'),floating('fff8000000000001'),(False,True,False,True,False,False,False,False),1),
    (floating('7ff0000000000000'),floating('7ff0000000000000'),(True,False,True,False,False,True,False,True),0),
    (integer(9223372036854775807),floating('43e0000000000000'),(True,False,False,True,False,True,False,True),0),
]:
    for kind,value in zip(['Equal','NotEqual','Identical','NotIdentical','Smaller','SmallerOrEqual','Greater','GreaterOrEqual'],results):
        expression=binary(kind,left,right)
        checks.extend([
            f'$lossy_optional_integer_condition(plenv_source,{expression}) = ({str(value).lower()})',
            f'$lossy_optional_integer_default_in(plenv_source,{cast(expression)}) = ({int(value)})',
        ])
    spaceship=binary('Spaceship',left,right)
    result=f'$({order})' if order<0 else str(order)
    checks.extend([
        f'$lossy_optional_integer_default_in(plenv_source,{spaceship}) = ({result})',
        f'$lossy_optional_integer_numeric(plenv_source,{spaceship}) = (NINT {result})',
    ])

# Comparisons admit only existing typed Numeric operands, not raw scalar coercions.
for child in [string('1'),expr_yes,expr_no,expr_nil,node('NExprVariable','BYTES "eA=="'),node('NExprArray','SEQUENCE eps'),integer(9223372036854775808)]:
    for kind in ['Equal','Spaceship']:
        expression=binary(kind,integer(1),child)
        checks.append(f'$lossy_optional_integer_default_in(plenv_source,{cast(expression)}) = eps')
# The existing whole-expression INTMIN certificate remains valid before operand typing.
minimum=node('NExprUnaryMinus',integer(9223372036854775808))
checks.extend([
    f'$lossy_optional_integer_numeric(plenv_source,{minimum}) = (NINT $(-9223372036854775808))',
    f'$lossy_optional_integer_condition(plenv_source,{binary("Smaller",minimum,floating("0000000000000000"))}) = (true)',
])
selected_float=ternary(expr_yes,floating('3fe0000000000000'),expr_unknown)
selected_string=ternary(expr_yes,string('.5tail'),expr_unknown)
checks.extend([
    f'$lossy_optional_integer_condition(plenv_source,{binary("Equal",selected_float,floating("3fe0000000000000"))}) = (true)',
    f'$lossy_optional_integer_condition(plenv_source,{binary("Equal",selected_string,floating("3fe0000000000000"))}) = eps',
    f'$lossy_optional_integer_condition(plenv_source,{binary("Equal",float_cast(selected_string),floating("3fe0000000000000"))}) = (true)',
    f'$lossy_optional_integer_default_in(plenv_source,{binary("Equal",integer(1),floating("3ff0000000000000"))}) = eps',
    f'$lossy_optional_integer_numeric(plenv_source,{binary("Equal",integer(1),floating("3ff0000000000000"))}) = eps',
])
# Quiet comparison results compose through existing Boolean, selection and cast paths.
comparison=binary('Equal',floating('7ff8000000000000'),integer(0))
unequal=binary('NotEqual',floating('7ff8000000000000'),integer(0))
checks.extend([
    f'$lossy_optional_integer_condition(plenv_source,{binary("BooleanAnd",comparison,expr_unknown)}) = (false)',
    f'$lossy_optional_integer_condition(plenv_source,{binary("LogicalOr",unequal,expr_unknown)}) = (true)',
    f'$lossy_optional_integer_default_in(plenv_source,{ternary(unequal,integer(13),expr_unknown)}) = (13)',
    f'$lossy_optional_integer_numeric(plenv_source,{float_cast(comparison)}) = (NFLOAT 0)',
    f'$lossy_optional_integer_string_in(plenv_source,{string_cast(unequal)}) = ($ptascii("1"))',
    f'$lossy_optional_integer_numeric(plenv_source,{float_cast(floating("7ff8000000000000"))}) = eps',
    f'$lossy_optional_integer_condition(plenv_source,{binary("Equal",float_cast(floating("7ff8000000000000")),integer(0))}) = eps',
    f'$lossy_optional_integer_condition(plenv_source,{floating("7ff8000000000000")}) = eps',
    f'$lossy_optional_integer_default_in(plenv_source,{cast(floating("7ff8000000000000"))}) = eps',
    f'$lossy_optional_integer_string_in(plenv_source,{string_cast(floating("3fe0000000000000"))}) = eps',
    f'$lossy_optional_integer_default_in(plenv_source,{cast(dimension(string("019"),floating("3fe0000000000000")))}) = eps',
])
# Exact old197 promoted helper input is freshly exercised under its empty ENV.
old197=binary('Equal',integer(1),floating('3ff0000000000000'))
checks.extend([
    f'$lossy_optional_integer_default_in($plempty(false),{cast(old197)}) = (1)',
    f'$lossy_optional_integer_condition($plempty(false),{old197}) = (true)',
])
# Eight proper numeric-comparison descendants preserve bounded INT result tags.
deep=floating('3fe0000000000000')
for _ in range(8):deep=binary('Spaceship',float_cast(deep),integer(0))
checks.extend([
    f'$lossy_optional_integer_default_in(plenv_source,{deep}) = (1)',
    f'$lossy_optional_integer_numeric(plenv_source,{deep}) = (NINT 1)',
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
    '$lookup(psymboltable_global.ENV, $ptascii("xReceive220")) = (n_cell)',
    '$lookup(psymboltable_global.ENV, $ptascii("countReceive220")) = (n_count)',
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
    '$lookup(S_done.ENV, $ptascii("gotReceive220")) = (n_got)',
    'S_done.STORE[n_got] = DEFINED (PINT 1)',
    r'$call_descriptors_valid(S_done) /\ $heap_valid($heap_graph(S_done))',
])

CASES = {'numeric-comparison-reference-leading': {
    'source': leading,
    'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 2 n_cell n_bits i z]',
    'checks': checks,
}}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
