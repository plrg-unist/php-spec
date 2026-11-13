#!/usr/bin/env python3
"""Explicit scalar FLOAT casts retain byte and Boolean values with source authority."""
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
    return constant('UnselectedReceive218')




def negate(child):
    return node('NExprUnaryMinus', child)


yes = lambda: cast(constant('YesReceive218'))
no = lambda: cast(constant('NoReceive218'))
large = lambda: floating('7fe1ccf385ebc8a0')
computed_inf = lambda: binary('Mul', large(), integer(2))
computed_nan = lambda: binary('Minus', computed_inf(), computed_inf())
children = [
    binary('Concat',string_cast(constant('YesReceive218')),string('.5tail')),
    binary('Concat',node('NExprBitwiseNot',string(bytes((207,207)))),string_cast(constant('NoReceive218'))),
    node('NExprBooleanNot',constant('NoReceive218')),
    constant('NilReceive218'),constant('YesReceive218'),
]
floating_casts=[float_cast(child) for child in children]
false_cast=float_cast(constant('NoReceive218'))
operands=[binary('Minus',floating_casts[0],floating('4022000000000000')),binary('Minus',floating_casts[1],floating('4027000000000000')),binary('Minus',binary('Plus',floating_casts[2],floating('4029000000000000')),false_cast),floating_casts[3],floating_casts[4]]
patterns=[cast(operands[0]),cast(operands[1]),cast(operands[2]),ternary(cast(operands[3]),unknown(),cast(string('-9223372036854775808tail'))),ternary(cast(operands[4]),cast(string('9'*24)),unknown())]


contrasts = [
    ('floatnot','deferredFloatNotReceive218',cast(node('NExprBooleanNot',floating('3fe0000000000000'))),'(0)'),
    ('negative','deferredNegativeIndexReceive218',cast(dimension(string('10'),string('-1'))),'eps'),
    ('floatindex','deferredFloatIndexReceive218',cast(dimension(string('10'),string('1.0'))),'eps'),
    ('floatstring','deferredFloatStringReceive218',cast(string_cast(floating('3fe0000000000000'))),'eps'),
    ('computednegative','deferredComputedNegativeIndexReceive218',cast(dimension(string('10'),binary('Minus',integer(0),integer(1)))),'eps'),
    ('selectedfloat','deferredSelectedFloatStringReceive218',cast(string_cast(ternary(constant('YesReceive218'),floating('3fe0000000000000'),unknown()))),'eps'),
    ('nonfit','deferredComputedFloatNonfitReceive218',cast(computed_inf()),'eps'),
    ('zerodiv','deferredComputedFloatZeroDivReceive218',cast(binary('Div',floating('3ff0000000000000'),integer(0))),'eps'),
    ('computednan','deferredComputedFloatNanReceive218',cast(computed_nan()),'eps'),
    ('unarynonfit','deferredComputedFloatUnaryNonfitReceive218',cast(negate(cast(string('-9223372036854775808')))),'eps'),
    ('computednot','deferredComputedFloatNotReceive218',cast(node('NExprBooleanNot',binary('Div',yes(),integer(2)))),'(0)'),
    ('computednannot','deferredComputedFloatNanNotReceive218',cast(node('NExprBooleanNot',computed_nan())),'eps'),
    ('selectednonfit','deferredSelectedFloatArithmeticNonfitReceive218',cast(binary('Plus',ternary(constant('YesReceive218'),computed_inf(),unknown()),integer(0))),'eps'),
    ('coalescenonfit','deferredSelectedFloatCoalesceNonfitReceive218',cast(binary('Plus',binary('Coalesce',computed_inf(),unknown()),integer(0))),'eps'),
    ('selectednan','deferredSelectedFloatArithmeticNanReceive218',cast(binary('Minus',ternary(constant('YesReceive218'),computed_inf(),unknown()),ternary(constant('NoReceive218'),unknown(),computed_inf()))),'eps'),
    ('floatcastnan','deferredNumericFloatCastNanReceive218',cast(float_cast(computed_nan())),'eps'),
    ('floatcastnonfit','deferredNumericFloatCastNonfitReceive218',cast(float_cast(cast(string('9223372036854775807')))),'eps'),
    ('scalarfloatnonfit','deferredScalarFloatCastNonfitReceive218',cast(float_cast(string('1e999'))),'eps'),
]

CATALOGUE = Path(__file__).with_name('scalar_float_cast_default_reception_cases.json')
assert hashlib.sha256(CATALOGUE.read_bytes()).hexdigest() == '13834da5f36255a25d6c837e73c01cb404aa19cd58fd47ce8066634bf94ed630'
row = next(row for row in json.loads(CATALOGUE.read_text()) if row['id'] == 'scalar-float-cast-precision-modes')
assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
source = row['source']
handler = source[:source.index('function valueFirstReceive218(')]
reference = source[source.index('function referenceReceive218('):source.index("set_error_handler('warningReceive218');")]
setup = source[source.index("set_error_handler('warningReceive218');"):source.index('$gotReceive218 = valueFirstReceive218(')]
start = source.index('$gotReceive218 = referenceReceive218(')
end = source.index('$xReceive218 = 1.5;', start)
leading = handler + reference + setup + source[start:end]
assert hashlib.sha256(leading.encode()).hexdigest() == 'c9cc57873090e9515fe2cc5863c1123354750f8e34d110fd7e961b610de62b67'



checks = [
    r'n_bits = 4609434218613702656 /\ i = 1',
    '$function_at(S.FUNCTIONS, porigin) = (pfunction)',
    'plenv_source = pfunction.ENV',
    r'plenv_source.NAMESPACE = eps /\ plenv_source.CONSTANTS = [($ptascii("YesReceive218"), $ptascii("true")), ($ptascii("NoReceive218"), $ptascii("false")), ($ptascii("NilReceive218"), $ptascii("null"))]',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_a, psparam_b, psparam_c, psparam_d, psparam_e]',
    '$lossy_optional_integer_mode(pfunction.SIGNATURE.PARAMETERS, true)',
    '~$lossy_optional_integer_mode(pfunction.SIGNATURE.PARAMETERS, false)',
    'S.CURRENT = (pcallcontext)',
    r'pcallcontext.ARGC = 3 /\ pcallcontext.HOLES = [0, 1] /\ pcallcontext.NAMED = eps',
]




for index,(letter,pattern,child,floating_cast,operand,value,bits,operand_bits) in enumerate(zip('abcde',patterns,children,floating_casts,operands,('$(-7)','$(-11)','13','$(-9223372036854775808)','9223372036854775807'),('3ff8000000000000','0000000000000000','3ff0000000000000','0000000000000000','3ff0000000000000'),('c01e000000000000','c027000000000000','402b000000000000','0000000000000000','3ff0000000000000'))):
    checks.extend([
        rf'~psparam_{letter}.REQUIRED /\ ~psparam_{letter}.VARIADIC /\ $ptmasks(psparam_{letter}.TYPE) = ["int"]',
        f'psparam_{letter}.DEFAULT = PSDEFAULT expression_{letter} "int"',
        f'expression_{letter} = {pattern}',
        f'$lossy_optional_integer_default_in(plenv_source,expression_{letter}) = ({value})',
        f'expression_child_{letter} = {child}',
        f'expression_float_cast_{letter} = {floating_cast}',
        f'expression_operand_{letter} = {operand}',
        f'$lossy_optional_integer_numeric(plenv_source,expression_child_{letter}) = eps',
        f'$lossy_optional_integer_numeric(plenv_source,expression_float_cast_{letter}) = (NFLOAT $hex_bits("{bits}",0))',
        f'$lossy_optional_integer_numeric(plenv_source,expression_operand_{letter}) = (NFLOAT $hex_bits("{operand_bits}",0))',
        f'$lossy_optional_integer_condition(plenv_source,expression_float_cast_{letter}) = ({str(letter not in "bd").lower()})',
        f'$default_parameter_origin(S,porigin,{index}) = PORIGIN n_unit pcpath_{letter}',
        f'porigin_{letter} = PORIGIN n_unit (pcpath_{letter} ++ [PCFIELD 6])',
        f'$origin_node(S.SOURCES,porigin_{letter}) = (expression_{letter})',
        f'$default_at(pfunction.DEFAULTS,{index}) = ({{INDEX {index},ORIGIN porigin_{letter},KIND PDSTORED}})',
        f'$compiled_read(S,porigin_{letter}) = (PINT {value})',
    ])
checks.extend([
    '$lossy_optional_integer_string_in(plenv_source,expression_child_a) = ($ptascii("1.5tail"))',
    '$lossy_optional_integer_string_in(plenv_source,expression_child_b) = ($ptascii("00"))',
    '$lossy_optional_integer_boolean_shape(expression_child_c)',
    '$lossy_optional_integer_condition(plenv_source,expression_child_c) = (true)',
    '$lossy_optional_integer_special(plenv_source,expression_child_d) = (PNULL)',
    '$lossy_optional_integer_special(plenv_source,expression_child_e) = (PBOOL true)',
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
        f'~$lossy_optional_integer_tail(S,pfunction_{suffix}[.DEFAULTS = [{{INDEX 0,ORIGIN porigin_{suffix},KIND PDSTORED}}]],[psparam_{suffix}[.DEFAULT = PSDEFAULT expression_{suffix} "int"]],0)',
    ])




checks.extend([
    f'expression_false_cast = {false_cast}',
    '$lossy_optional_integer_numeric(plenv_source,expression_false_cast) = (NFLOAT 0)',
    '$lossy_optional_integer_condition(plenv_source,expression_false_cast) = (false)',
])




checks.extend([
    '$lossy_optional_integer_header(S, pfunction, pfunction.SIGNATURE.PARAMETERS, 0)',
    'plenv_alias = plenv_source[.CONSTANTS = [($ptascii("YesReceive218"), $ptascii("false")), ($ptascii("NoReceive218"), $ptascii("false")), ($ptascii("NilReceive218"), $ptascii("null"))]]',
    '$lossy_optional_integer_default_in(plenv_alias, expression_a) = ($(-8))',
    '$lossy_optional_integer_default_in(plenv_alias, expression_b) = ($(-11))',
    '~$lossy_optional_integer_header(S, pfunction[.ENV = plenv_alias], pfunction.SIGNATURE.PARAMETERS, 0)',
    'expression_a = NExprCastInt expression_operand_a metadata_a',
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
expr_yes,expr_no,expr_nil=map(constant,('YesReceive218','NoReceive218','NilReceive218'))
expr_unknown=unknown()
half=binary('Div',integer(1),integer(2))

# Explicit byte casts use the full permissive decimal-prefix FLOAT parser.
for child,bits,result in [
    (string(''),'0000000000000000','0'),(string('0.0'),'0000000000000000','0'),
    (string('.5tail'),'3fe0000000000000','0'),(string('0.25tail'),'3fd0000000000000','0'),
    (string('x'),'0000000000000000','0'),(string('NAN'),'0000000000000000','0'),
    (string('INF'),'0000000000000000','0'),(string('-0.0tail'),'8000000000000000','0'),
    (string('5e-324'),'0000000000000001','0'),(string('-5e-324'),'8000000000000001','0'),
    (string('1e999'),'7ff0000000000000',None),(string('-1e999'),'fff0000000000000',None),
    (binary('Concat',string('0'),string('.0')),'0000000000000000','0'),
    (binary('Concat',string('0.'),string('5tail')),'3fe0000000000000','0'),
    (node('NExprBitwiseNot',string(bytes((207,209,207)))),'0000000000000000','0'),
    (node('NExprBitwiseNot',string(bytes((207,209,202,139,158,150,147)))),'3fe0000000000000','0'),
    (binary('BitwiseOr',string('0.0'),string(bytes((0,)))),'0000000000000000','0'),
]:
    expression=float_cast(child);truth=str(bits not in ['0000000000000000','8000000000000000']).lower()
    checks.extend([
        f'$lossy_optional_integer_numeric(plenv_source,{child}) = eps',
        f'$lossy_optional_integer_numeric(plenv_source,{expression}) = (NFLOAT $hex_bits("{bits}",0))',
        f'$lossy_optional_integer_default_in(plenv_source,{cast(expression)}) = {"eps" if result is None else "("+result+")"}',
        f'$lossy_optional_integer_condition(plenv_source,{expression}) = ({truth})',
    ])

# Every Boolean/null form remains distinct from a raw integer Numeric certificate.
for child,result in [(constant('true'),1),(constant('false'),0),(constant('null'),0),(expr_yes,1),(expr_no,0),(expr_nil,0),
                     (node('NExprBooleanNot',expr_no),1),(node('NExprCastBool',half),1),
                     (binary('BooleanAnd',integer(0),expr_unknown),0),(binary('LogicalOr',integer(1),expr_unknown),1),
                     (binary('LogicalXor',integer(0),integer(1)),1),(binary('Identical',integer(1),integer(1)),1)]:
    expression=float_cast(child);bits='3ff0000000000000' if result else '0000000000000000'
    checks.extend([
        f'$lossy_optional_integer_numeric(plenv_source,{child}) = eps',
        f'$lossy_optional_integer_numeric(plenv_source,{expression}) = (NFLOAT $hex_bits("{bits}",0))',
        f'$lossy_optional_integer_default_in(plenv_source,{cast(expression)}) = ({result})',
        f'$lossy_optional_integer_condition(plenv_source,{expression}) = ({str(bool(result)).lower()})',
    ])
checks.extend([
    'plenv_no_true=plenv_source[.CONSTANTS=[($ptascii("YesReceive218"),$ptascii("true")),($ptascii("NoReceive218"),$ptascii("true")),($ptascii("NilReceive218"),$ptascii("null"))]]',
    '$lossy_optional_integer_default_in(plenv_no_true,expression_b) = ($(-10))',
    '$lossy_optional_integer_default_in(plenv_no_true,expression_c) = (11)',
    '~$lossy_optional_integer_header(S,pfunction[.ENV=plenv_no_true],pfunction.SIGNATURE.PARAMETERS,0)',
    '$lossy_optional_integer_numeric($plempty(false),expression_float_cast_a) = eps',
])

# The two scalar routes compose through existing arithmetic, with FLOAT tags preserved.
scalar=float_cast(binary('Concat',string_cast(expr_yes),string('.5tail')))
for expression,bits,result in [(binary('Plus',scalar,integer(1)),'4004000000000000','2'),
                               (binary('Minus',scalar,integer(2)),'bfe0000000000000','0'),
                               (binary('Mul',scalar,integer(2)),'4008000000000000','3'),
                               (binary('Div',scalar,integer(3)),'3fe0000000000000','0'),
                               (node('NExprUnaryMinus',scalar),'bff8000000000000','$(-1)')]:
    checks.extend([
        f'$lossy_optional_integer_numeric(plenv_source,{expression}) = (NFLOAT $hex_bits("{bits}",0))',
        f'$lossy_optional_integer_default_in(plenv_source,{cast(expression)}) = ({result})',
    ])
# Selected values need the explicit FLOAT cast; raw arithmetic, keys and formatting stay bounded.
for child,bits in [(ternary(expr_yes,string('0.0'),expr_unknown),'0000000000000000'),(ternary(expr_yes,expr_no,expr_unknown),'0000000000000000'),(binary('Coalesce',expr_nil,string('.5')),'3fe0000000000000'),(node('NExprVariable','BYTES "eA=="'),None),(node('NExprArray','SEQUENCE eps'),None)]:
    result=f'(NFLOAT $hex_bits("{bits}",0))' if bits is not None else 'eps'
    checks.append(f'$lossy_optional_integer_numeric(plenv_source,{float_cast(child)}) = {result}')
for expression in [binary('Plus',expr_yes,integer(1)),binary('Mul',string('2'),integer(2)),binary('BooleanAnd',integer(1),expr_unknown)]:
    checks.append(f'$lossy_optional_integer_numeric(plenv_source,{float_cast(expression)}) = eps')
checks.extend([
    f'$lossy_optional_integer_default_in(plenv_source,{scalar}) = eps',
    f'$lossy_optional_integer_string_in(plenv_source,{string_cast(scalar)}) = eps',
    f'$lossy_optional_integer_string_in(plenv_source,{dimension(string("019"),float_cast(expr_yes))}) = eps',
    f'$lossy_optional_integer_default_in(plenv_source,{cast(dimension(string("019"),cast(float_cast(expr_yes))))}) = (1)',
    f'$lossy_optional_integer_numeric(plenv_source,{float_cast(constant("true",True))}) = (NFLOAT $hex_bits("3ff0000000000000",0))',
    f'$lossy_optional_integer_numeric(plenv_source,{float_cast(constant("YesReceive218",True))}) = eps',
])
nan=computed_nan()
for expression in [float_cast(nan),float_cast(node('NExprCastBool',nan)),float_cast(node('NExprBooleanNot',nan))]:
    checks.append(f'$lossy_optional_integer_numeric(plenv_source,{expression}) = eps')
checks.extend([
    f'$lossy_optional_integer_numeric(plenv_source,{float_cast(node("NExprBooleanNot",floating("3fe0000000000000")))}) = (NFLOAT 0)',
    f'$lossy_optional_integer_numeric(plenv_source,{binary("Minus",float_cast(string("1e999")),computed_inf())}) = (NFLOAT n_nan)',
    '$pfcast_nan(PFLOAT n_nan)',
])
# Exact old217 local aliases are retained for the newly promoted scalar forms.
checks.append('plenv_old=plenv_source[.CONSTANTS=[($ptascii("YesReceive217"),$ptascii("true")),($ptascii("NoReceive217"),$ptascii("false")),($ptascii("NilReceive217"),$ptascii("null"))]]')
for child,result in [(constant('YesReceive217'),1),(constant('NoReceive217'),0),(constant('NilReceive217'),0)]:
    expression=float_cast(child);bits='3ff0000000000000' if result else '0000000000000000'
    checks.extend([f'$lossy_optional_integer_numeric(plenv_old,{expression}) = (NFLOAT $hex_bits("{bits}",0))',f'$lossy_optional_integer_default_in(plenv_old,{cast(expression)}) = ({result})'])
# Eight typed FLOAT-cast levels over a quiet Boolean leaf preserve the new value.
deep=float_cast(node('NExprBooleanNot',expr_no))
for _ in range(8):deep=float_cast(binary('Plus',deep,floating('0000000000000000')))
checks.extend([f'$lossy_optional_integer_numeric(plenv_source,{deep}) = (NFLOAT $hex_bits("3ff0000000000000",0))',f'$lossy_optional_integer_default_in(plenv_source,{cast(deep)}) = (1)'])


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
    '$lookup(psymboltable_global.ENV, $ptascii("xReceive218")) = (n_cell)',
    '$lookup(psymboltable_global.ENV, $ptascii("countReceive218")) = (n_count)',
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
    '$lookup(S_done.ENV, $ptascii("gotReceive218")) = (n_got)',
    'S_done.STORE[n_got] = DEFINED (PINT 1)',
    r'$call_descriptors_valid(S_done) /\ $heap_valid($heap_graph(S_done))',
])

CASES = {'scalar-float-cast-reference-leading': {
    'source': leading,
    'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 2 n_cell n_bits i z]',
    'checks': checks,
}}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
