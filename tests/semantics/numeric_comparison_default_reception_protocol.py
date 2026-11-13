#!/usr/bin/env python3
"""Typed numeric comparisons preserve tags, quiet results and receive authority."""
import base64
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('numeric_comparison_default_reception_cases.json')
SOURCES = {}
for row in json.loads(CATALOGUE.read_text()):
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
    SOURCES[row['id']] = row['source']

# Fresh first-VAL front preserves the whole five-default declaration; source0.
full = SOURCES['numeric-comparison-precision-modes']
setup = full.index("set_error_handler('warningReceive220');")
start = full.index('$gotReceive220 = valueFirstReceive220(')
end = full.index('$xReceive220 = 1.5;', start)
source = full[:full.index('function referenceFirstReceive220')] + full[setup:end]
assert hashlib.sha256(source.encode()).hexdigest() == 'c38f85224636c4416c5f8f31a2e36da3d682a71757379066f223148ca5d222e6'

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
    return constant('UnselectedReceive220')


yes = lambda: cast(constant('YesReceive220'))
no = lambda: cast(constant('NoReceive220'))
large = lambda: floating('7fe1ccf385ebc8a0')
computed_inf = lambda: binary('Mul', large(), integer(2))
computed_nan = lambda: binary('Minus', computed_inf(), computed_inf())
def float_cast(child):
    return node('NExprCastDouble', child)






compare = binary
ternary = conditional

# Each syntactic occurrence receives distinct metadata before binding actual source nodes.
def maximum():
    return compare('Minus',cast(string('9223372036854775807tail')),cast(constant('NoReceive220')))

def actual_nan():
    return compare('Minus',compare('Mul',large(),compare('Plus',integer(2),cast(constant('NoReceive220')))),compare('Mul',large(),integer(2)))

comparison_a_less=compare('Smaller',integer(7),compare('Plus',float_cast(constant('YesReceive220')),floating('401a000000000000')))
comparison_a_le=compare('SmallerOrEqual',integer(7),compare('Plus',float_cast(constant('YesReceive220')),floating('401a000000000000')))
condition_a=compare('BooleanAnd',comparison_a_less,comparison_a_le)
comparison_b_equal=compare('Equal',maximum(),float_cast(maximum()))
comparison_b_identity=compare('NotIdentical',maximum(),float_cast(maximum()))
spaceship_b=compare('Spaceship',maximum(),float_cast(maximum()))
condition_b=compare('BooleanAnd',compare('BooleanAnd',comparison_b_equal,comparison_b_identity),compare('Identical',spaceship_b,integer(0)))
comparison_c_zero=compare('Identical',float_cast(constant('NoReceive220')),negate(floating('0000000000000000')))
comparison_c_identity=compare('Identical',cast(constant('YesReceive220')),float_cast(constant('YesReceive220')))
condition_c=compare('BooleanAnd',comparison_c_zero,node('NExprBooleanNot',comparison_c_identity))
comparison_d_greater=compare('Greater',actual_nan(),integer(0))
comparison_d_ge=compare('GreaterOrEqual',actual_nan(),integer(0))
condition_d=compare('BooleanOr',comparison_d_greater,comparison_d_ge)
condition_e=compare('NotEqual',actual_nan(),float_cast(constant('NilReceive220')))
conditions=[condition_a,condition_b,condition_c,condition_d,condition_e]
patterns=[negate(ternary(condition_a,integer(7),unknown())),ternary(condition_b,cast(string('-11tail')),unknown()),ternary(condition_c,cast(string('13tail')),unknown()),ternary(condition_d,unknown(),cast(string('-9223372036854775808tail'))),ternary(condition_e,cast(string('9'*24)),unknown())]

contrasts = [
    ('floatnot','deferredFloatNotReceive220',cast(node('NExprBooleanNot',floating('3fe0000000000000'))),'(0)'),
    ('negative','deferredNegativeIndexReceive220',cast(dimension(string('10'),string('-1'))),'eps'),
    ('floatindex','deferredFloatIndexReceive220',cast(dimension(string('10'),string('1.0'))),'eps'),
    ('floatstring','deferredFloatStringReceive220',cast(string_cast(floating('3fe0000000000000'))),'eps'),
    ('computednegative','deferredComputedNegativeIndexReceive220',cast(dimension(string('10'),compare('Minus',integer(0),integer(1)))),'eps'),
    ('selectedfloat','deferredSelectedFloatStringReceive220',cast(string_cast(ternary(constant('YesReceive220'),floating('3fe0000000000000'),unknown()))),'eps'),
    ('nonfit','deferredComputedFloatNonfitReceive220',cast(computed_inf()),'eps'),
    ('zerodiv','deferredComputedFloatZeroDivReceive220',cast(compare('Div',floating('3ff0000000000000'),integer(0))),'eps'),
    ('computednan','deferredComputedFloatNanReceive220',cast(computed_nan()),'eps'),
    ('unarynonfit','deferredComputedFloatUnaryNonfitReceive220',cast(negate(cast(string('-9223372036854775808')))),'eps'),
    ('computednot','deferredComputedFloatNotReceive220',cast(node('NExprBooleanNot',compare('Div',yes(),integer(2)))),'(0)'),
    ('computednannot','deferredComputedFloatNanNotReceive220',cast(node('NExprBooleanNot',computed_nan())),'eps'),
    ('selectednonfit','deferredSelectedFloatArithmeticNonfitReceive220',cast(compare('Plus',ternary(constant('YesReceive220'),computed_inf(),unknown()),integer(0))),'eps'),
    ('coalescenonfit','deferredSelectedFloatCoalesceNonfitReceive220',cast(compare('Plus',compare('Coalesce',computed_inf(),unknown()),integer(0))),'eps'),
    ('selectednan','deferredSelectedFloatArithmeticNanReceive220',cast(compare('Minus',ternary(constant('YesReceive220'),computed_inf(),unknown()),ternary(constant('NoReceive220'),unknown(),computed_inf()))),'eps'),
    ('floatcastnan','deferredNumericFloatCastNanReceive220',cast(float_cast(computed_nan())),'eps'),
    ('floatcastnonfit','deferredNumericFloatCastNonfitReceive220',cast(float_cast(cast(string('9223372036854775807')))),'eps'),
    ('scalarfloatnonfit','deferredScalarFloatCastNonfitReceive220',cast(float_cast(string('1e999'))),'eps'),
    ('selectedscalarfloatnonfit','deferredSelectedScalarFloatCastNonfitReceive220',cast(float_cast(ternary(constant('YesReceive220'),string('1e999'),unknown()))),'eps'),
]

checks = [
    r'n_bits = 4609434218613702656 /\ i = 1',
    '$function_at(S.FUNCTIONS, porigin) = (pfunction)',
    'plenv_source = pfunction.ENV',
    r'plenv_source.NAMESPACE = eps /\ plenv_source.CONSTANTS = [($ptascii("YesReceive220"), $ptascii("true")), ($ptascii("NoReceive220"), $ptascii("false")), ($ptascii("NilReceive220"), $ptascii("null"))]',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_a, psparam_b, psparam_c, psparam_d, psparam_e]',
    r'~psparam_a.REQUIRED /\ ~psparam_a.BYREF /\ psparam_b.BYREF /\ psparam_d.BYREF /\ psparam_e.BYREF',
]
for index,(letter,pattern,condition,value,truth) in enumerate(zip(
    'abcde',patterns,conditions,
    ('$(-7)','$(-11)','13','$(-9223372036854775808)','9223372036854775807'),
    (True,True,True,False,True),
)):
    checks.extend([
        f'psparam_{letter}.DEFAULT = PSDEFAULT expression_{letter} "int"',
        f'expression_{letter} = {pattern}',
        f'expression_condition_{letter} = {condition}',
        f'$lossy_optional_integer_condition(plenv_source,expression_condition_{letter}) = ({str(truth).lower()})',
        f'$lossy_optional_integer_default_in(plenv_source,expression_{letter}) = ({value})',
        f'$lossy_optional_integer_numeric(plenv_source,expression_{letter}) = (NINT {value})',
        f'$default_parameter_origin(S,porigin,{index}) = PORIGIN n_unit pcpath_{letter}',
        f'porigin_{letter} = PORIGIN n_unit (pcpath_{letter} ++ [PCFIELD 6])',
        f'$origin_node(S.SOURCES,porigin_{letter}) = (expression_{letter})',
        f'$default_at(pfunction.DEFAULTS,{index}) = ({{INDEX {index},ORIGIN porigin_{letter},KIND PDSTORED}})',
        f'$compiled_read(S,porigin_{letter}) = (PINT {value})',
    ])
checks.extend([
    '$lossy_optional_integer_header(S,pfunction,pfunction.SIGNATURE.PARAMETERS,0)',
    'expression_a = NExprUnaryMinus expression_child_a metadata_a',
    '$lossy_optional_integer_default_in($plempty(false),expression_a) = eps',
    '~$lossy_optional_integer_header(S,pfunction[.ENV = $plempty(false)],pfunction.SIGNATURE.PARAMETERS,0)',
    'plenv_yes_false = plenv_source[.CONSTANTS = [($ptascii("YesReceive220"),$ptascii("false")),($ptascii("NoReceive220"),$ptascii("false")),($ptascii("NilReceive220"),$ptascii("null"))]]',
    '$lossy_optional_integer_default_in(plenv_yes_false,expression_a) = eps',
    '~$lossy_optional_integer_header(S,pfunction[.ENV = plenv_yes_false],pfunction.SIGNATURE.PARAMETERS,0)',
    'plenv_no_true = plenv_source[.CONSTANTS = [($ptascii("YesReceive220"),$ptascii("true")),($ptascii("NoReceive220"),$ptascii("true")),($ptascii("NilReceive220"),$ptascii("null"))]]',
    '$lossy_optional_integer_default_in(plenv_no_true,expression_c) = eps',
    '~$lossy_optional_integer_header(S,pfunction[.ENV = plenv_no_true],pfunction.SIGNATURE.PARAMETERS,0)',
    'expression_same = NExprUnaryMinus (NScalarInt (INTEGER 7) metadata_a) metadata_a',
    '$lossy_optional_integer_default_in(plenv_source,expression_same) = ($(-7))',
    '~$lossy_optional_integer_tail(S,pfunction,[psparam_a[.DEFAULT = PSDEFAULT expression_same "int"]],0)',
    'pfunction.DEFAULTS = [pdefault_a,pdefault_b,pdefault_c,pdefault_d,pdefault_e]',
    '~$lossy_optional_integer_tail(S,pfunction[.DEFAULTS = [pdefault_a,pdefault_b[.KIND = PDDEFERRED],pdefault_c,pdefault_d,pdefault_e]],[psparam_b],1)',
    'S_wrong_value = S[.POOLS = [{UNIT n_unit,CONSTANTS ([(PCONSTANT (pcpath_c ++ [PCFIELD 6]) (PINT 1))])}]]',
    '~$lossy_optional_integer_tail(S_wrong_value,pfunction,[psparam_c],2)',
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
# Every contrast keeps its authentic deferred kind and absent root PINT.
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
# Hardcoded typed matrices distinguish loose equality, identity and unordered order.
matrices = [
    (integer(1),floating('3ff0000000000000'),0,[True,False,False,True,False,True,False,True]),
    (floating('0000000000000000'),floating('8000000000000000'),0,[True,False,True,False,False,True,False,True]),
    (integer(9223372036854775807),floating('43e0000000000000'),0,[True,False,False,True,False,True,False,True]),
    (floating('7ff8000000000001'),integer(0),1,[False,True,False,True,False,False,False,False]),
    (integer(0),floating('7ff8000000000001'),1,[False,True,False,True,False,False,False,False]),
    (floating('fff0000000000000'),floating('7ff0000000000000'),-1,[False,True,False,True,True,True,False,False]),
    (floating('3ff8000000000000'),integer(2),-1,[False,True,False,True,True,True,False,False]),
]
operators=['Equal','NotEqual','Identical','NotIdentical','Smaller','SmallerOrEqual','Greater','GreaterOrEqual']
for left,right,order,truths in matrices:
    for operator,truth in zip(operators,truths):
        expression=binary(operator,left,right)
        checks.extend([
            f'$lossy_optional_integer_condition(plenv_source,{expression}) = ({str(truth).lower()})',
            f'$lossy_optional_integer_default_in(plenv_source,{cast(expression)}) = ({int(truth)})',
        ])
    expression=binary('Spaceship',left,right)
    result=str(order) if order>=0 else f'$({order})'
    checks.extend([
        f'$lossy_optional_integer_default_in(plenv_source,{expression}) = ({result})',
        f'$lossy_optional_integer_numeric(plenv_source,{expression}) = (NINT {result})',
    ])
# Quiet NaN comparison does not admit NaN truth or casts, nor implicit scalar operands.
expr_nan=floating('7ff8000000000001')
checks.extend([
    f'$lossy_optional_integer_numeric(plenv_source,{expr_nan}) = (NFLOAT $hex_bits("7ff8000000000001",0))',
    f'$lossy_optional_integer_condition(plenv_source,{expr_nan}) = eps',
    f'$lossy_optional_integer_default_in(plenv_source,{cast(expr_nan)}) = eps',
    f'$lossy_optional_integer_numeric(plenv_source,{float_cast(expr_nan)}) = eps',
])
for operand in [string('1'),constant('YesReceive220'),constant('NilReceive220'),unknown(),integer(9223372036854775808),node('NExprArray','SEQUENCE eps')]:
    for operator in ['Equal','Identical','Smaller','Greater']:
        expression=binary(operator,operand,integer(1))
        checks.extend([
            f'$lossy_optional_integer_condition(plenv_source,{expression}) = eps',
            f'$lossy_optional_integer_default_in(plenv_source,{cast(expression)}) = eps',
        ])
    checks.append(f'$lossy_optional_integer_default_in(plenv_source,{binary("Spaceship",operand,integer(1))}) = eps')
# Exact old197 input is freshly covered; its source/stage/count remain unchanged.
checks.append('$lossy_optional_integer_default_in(plenv_source, NExprCastInt (NExprBinaryOpEqual (NScalarInt (INTEGER 1) metadata_a) (NScalarFloat (FLOAT "3ff0000000000000") metadata_a) metadata_a) metadata_a) = (1)')
expr_boolean=binary('Equal',integer(1),floating('3ff0000000000000'))
checks.extend([
    f'$lossy_optional_integer_default_in(plenv_source,{expr_boolean}) = eps',
    f'$lossy_optional_integer_numeric(plenv_source,{expr_boolean}) = eps',
    f'$lossy_optional_integer_numeric(plenv_source,{float_cast(expr_boolean)}) = (NFLOAT $hex_bits("3ff0000000000000",0))',
    f'$lossy_optional_integer_string_in(plenv_source,{string_cast(expr_boolean)}) = ([49])',
])
deep=floating('3fe0000000000000')
for _ in range(8):
    deep=binary('Spaceship',deep,floating('3fe0000000000000'))
checks.extend([
    f'$lossy_optional_integer_default_in(plenv_source,{deep}) = ($(-1))',
    f'$lossy_optional_integer_numeric(plenv_source,{deep}) = (NINT $(-1))',
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
    '$lookup(psymboltable_global.ENV, $ptascii("xReceive220")) = (n_global)',
    'S.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    'S_capture = S[.TODO = [TYPE_RECEIVE porigin 0]]',
    '$lossy_mixed_parameter_capture(S_capture) = (LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z)',
    '$lossy_mixed_parameter_capture(S_capture[.STORE = $set_cell(S_capture.STORE,n_cell,DEFINED (PINT 1))]) = eps',
    '$lossy_mixed_parameter_capture(S_capture[.STORE = $set_cell(S_capture.STORE,n_cell,DEFINED (PBOOL true))]) = eps',
    '$lossy_mixed_parameter_capture(S_capture[.STORE = $set_cell(S_capture.STORE,n_cell,DEFINED PNULL)]) = eps',
    '$lossy_mixed_parameter_capture(S_capture[.STORE = $set_cell(S_capture.STORE,n_cell,DEFINED (PSTRING ($ptascii("1.5"))))]) = eps',
    '$lossy_mixed_parameter_capture(S_capture[.STORE = $set_cell(S_capture.STORE,n_cell,UNDEFINED)]) = eps',
    '$lossy_mixed_parameter_capture(S_capture[.TODO = [TYPE_RECEIVE porigin 5]]) = eps',
    '$lossy_mixed_parameter_capture(S_capture[.ALLOCATIONS = eps]) = eps',
    '$lossy_mixed_parameter_capture(S_capture[.STORE = $set_cell(S_capture.STORE,n_cell,DEFINED (PFLOAT $hex_bits("7ff0000000000000",0)))]) = eps',
    '$lossy_mixed_parameter_capture(S_capture[.STORE = $set_cell(S_capture.STORE,n_cell,DEFINED (PFLOAT $hex_bits("7ff8000000000000",0)))]) = eps',
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
    '$lookup(S_done.ENV, $ptascii("gotReceive220")) = (n_got)',
    'S_done.STORE[n_got] = DEFINED (PINT 13)',
    r'$call_descriptors_valid(S_done) /\ $heap_valid($heap_graph(S_done))',
])

CASES = {'numeric-comparison-default-omitted-tail': {
    'source': source,
    'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z]',
    'checks': checks,
}}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
