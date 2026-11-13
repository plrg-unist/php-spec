#!/usr/bin/env python3
"""Selected scalar FLOAT casts retain proper descendants and source authority."""
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
    return constant('UnselectedReceive219')


def negate(child):
    return node('NExprUnaryMinus', child)


yes = lambda: cast(constant('YesReceive219'))
no = lambda: cast(constant('NoReceive219'))
large = lambda: floating('7fe1ccf385ebc8a0')
computed_inf = lambda: binary('Mul', large(), integer(2))
computed_nan = lambda: binary('Minus', computed_inf(), computed_inf())
children=[ternary(constant('YesReceive219'),string('-7.5tail'),unknown()),node('NExprTernary',constant('NoReceive219'),'ABSENT',string('-5.5tail')),binary('Coalesce',constant('NilReceive219'),ternary(constant('NoReceive219'),unknown(),constant('YesReceive219'))),binary('Coalesce',constant('NoReceive219'),unknown()),node('NExprTernary',constant('YesReceive219'),'ABSENT',unknown())]
floating_casts=[float_cast(child) for child in children]
operands=[floating_casts[0],binary('Mul',floating_casts[1],integer(2)),binary('Plus',floating_casts[2],floating('4029000000000000')),floating_casts[3],floating_casts[4]]
patterns=[cast(operands[0]),cast(operands[1]),cast(operands[2]),ternary(cast(operands[3]),unknown(),cast(string('-9223372036854775808tail'))),ternary(cast(operands[4]),cast(string('9'*24)),unknown())]


contrasts = [
    ('floatnot','deferredFloatNotReceive219',cast(node('NExprBooleanNot',floating('3fe0000000000000'))),'(0)'),
    ('negative','deferredNegativeIndexReceive219',cast(dimension(string('10'),string('-1'))),'eps'),
    ('floatindex','deferredFloatIndexReceive219',cast(dimension(string('10'),string('1.0'))),'eps'),
    ('floatstring','deferredFloatStringReceive219',cast(string_cast(floating('3fe0000000000000'))),'eps'),
    ('computednegative','deferredComputedNegativeIndexReceive219',cast(dimension(string('10'),binary('Minus',integer(0),integer(1)))),'eps'),
    ('selectedfloat','deferredSelectedFloatStringReceive219',cast(string_cast(ternary(constant('YesReceive219'),floating('3fe0000000000000'),unknown()))),'eps'),
    ('nonfit','deferredComputedFloatNonfitReceive219',cast(computed_inf()),'eps'),
    ('zerodiv','deferredComputedFloatZeroDivReceive219',cast(binary('Div',floating('3ff0000000000000'),integer(0))),'eps'),
    ('computednan','deferredComputedFloatNanReceive219',cast(computed_nan()),'eps'),
    ('unarynonfit','deferredComputedFloatUnaryNonfitReceive219',cast(negate(cast(string('-9223372036854775808')))),'eps'),
    ('computednot','deferredComputedFloatNotReceive219',cast(node('NExprBooleanNot',binary('Div',yes(),integer(2)))),'(0)'),
    ('computednannot','deferredComputedFloatNanNotReceive219',cast(node('NExprBooleanNot',computed_nan())),'eps'),
    ('selectednonfit','deferredSelectedFloatArithmeticNonfitReceive219',cast(binary('Plus',ternary(constant('YesReceive219'),computed_inf(),unknown()),integer(0))),'eps'),
    ('coalescenonfit','deferredSelectedFloatCoalesceNonfitReceive219',cast(binary('Plus',binary('Coalesce',computed_inf(),unknown()),integer(0))),'eps'),
    ('selectednan','deferredSelectedFloatArithmeticNanReceive219',cast(binary('Minus',ternary(constant('YesReceive219'),computed_inf(),unknown()),ternary(constant('NoReceive219'),unknown(),computed_inf()))),'eps'),
    ('floatcastnan','deferredNumericFloatCastNanReceive219',cast(float_cast(computed_nan())),'eps'),
    ('floatcastnonfit','deferredNumericFloatCastNonfitReceive219',cast(float_cast(cast(string('9223372036854775807')))),'eps'),
    ('scalarfloatnonfit','deferredScalarFloatCastNonfitReceive219',cast(float_cast(string('1e999'))),'eps'),
    ('selectedscalarfloatnonfit','deferredSelectedScalarFloatCastNonfitReceive219',cast(float_cast(ternary(constant('YesReceive219'),string('1e999'),unknown()))),'eps'),
]

CATALOGUE = Path(__file__).with_name('selected_scalar_float_cast_default_reception_cases.json')
assert hashlib.sha256(CATALOGUE.read_bytes()).hexdigest() == 'ab3b081598b30ab56abe3b31203dcfdddf37035fcce08c4628b312887e7a4066'
row = next(row for row in json.loads(CATALOGUE.read_text()) if row['id'] == 'selected-scalar-float-cast-precision-modes')
assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
source = row['source']
handler = source[:source.index('function valueFirstReceive219(')]
reference = source[source.index('function referenceReceive219('):source.index("set_error_handler('warningReceive219');")]
setup = source[source.index("set_error_handler('warningReceive219');"):source.index('$gotReceive219 = valueFirstReceive219(')]
start = source.index('$gotReceive219 = referenceReceive219(')
end = source.index('$xReceive219 = 1.5;', start)
leading = handler + reference + setup + source[start:end]
assert hashlib.sha256(leading.encode()).hexdigest() == '773a565bd35c84390e18a0cb2f68481ea47de4579ded99aadd6d5112805e4c6b'


checks = [
    r'n_bits = 4609434218613702656 /\ i = 1',
    '$function_at(S.FUNCTIONS, porigin) = (pfunction)',
    'plenv_source = pfunction.ENV',
    r'plenv_source.NAMESPACE = eps /\ plenv_source.CONSTANTS = [($ptascii("YesReceive219"), $ptascii("true")), ($ptascii("NoReceive219"), $ptascii("false")), ($ptascii("NilReceive219"), $ptascii("null"))]',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_a, psparam_b, psparam_c, psparam_d, psparam_e]',
    '$lossy_optional_integer_mode(pfunction.SIGNATURE.PARAMETERS, true)',
    '~$lossy_optional_integer_mode(pfunction.SIGNATURE.PARAMETERS, false)',
    'S.CURRENT = (pcallcontext)',
    r'pcallcontext.ARGC = 3 /\ pcallcontext.HOLES = [0, 1] /\ pcallcontext.NAMED = eps',
]


for index,(letter,pattern,child,floating_cast,operand,value,bits,operand_bits) in enumerate(zip('abcde',patterns,children,floating_casts,operands,('$(-7)','$(-11)','13','$(-9223372036854775808)','9223372036854775807'),('c01e000000000000','c016000000000000','3ff0000000000000','0000000000000000','3ff0000000000000'),('c01e000000000000','c026000000000000','402b000000000000','0000000000000000','3ff0000000000000'))):
    checks.extend([
        rf'~psparam_{letter}.REQUIRED /\ ~psparam_{letter}.VARIADIC /\ $ptmasks(psparam_{letter}.TYPE) = ["int"]',
        f'psparam_{letter}.DEFAULT = PSDEFAULT expression_{letter} "int"',
        f'expression_{letter} = {pattern}',
        f'$lossy_optional_integer_default_in(plenv_source,expression_{letter}) = ({value})',
        f'expression_child_{letter} = {child}',
        f'expression_float_cast_{letter} = {floating_cast}',
        f'expression_operand_{letter} = {operand}',
        f'expression_float_cast_{letter} = NExprCastDouble expression_child_{letter} metadata_cast_{letter}',
        f'$lossy_optional_integer_selection_shape(expression_child_{letter})',
        f'$lossy_optional_integer_default_in(plenv_source,expression_child_{letter}) = eps',
        f'$lossy_optional_integer_numeric(plenv_source,expression_child_{letter}) = eps',
        f'$lossy_optional_integer_string_in(plenv_source,expression_child_{letter}) = eps',
        f'$lossy_optional_integer_default_in(plenv_source,expression_float_cast_{letter}) = eps',
        f'$lossy_optional_integer_numeric(plenv_source,expression_float_cast_{letter}) = (NFLOAT $hex_bits("{bits}",0))',
        f'$lossy_optional_integer_numeric(plenv_source,expression_operand_{letter}) = (NFLOAT $hex_bits("{operand_bits}",0))',
        f'$lossy_optional_integer_cast_leaf(plenv_source,expression_child_{letter}) = (expression_leaf_{letter})',
        f'$lossy_optional_integer_numeric(plenv_source,NExprCastDouble expression_leaf_{letter} metadata_cast_{letter}) = (NFLOAT $hex_bits("{bits}",0))',
        f'$lossy_optional_integer_condition(plenv_source,expression_float_cast_{letter}) = ({str(letter!="d").lower()})',
        f'$default_parameter_origin(S,porigin,{index}) = PORIGIN n_unit pcpath_{letter}',
        f'porigin_{letter} = PORIGIN n_unit (pcpath_{letter} ++ [PCFIELD 6])',
        f'$origin_node(S.SOURCES,porigin_{letter}) = (expression_{letter})',
        f'$default_at(pfunction.DEFAULTS,{index}) = ({{INDEX {index},ORIGIN porigin_{letter},KIND PDSTORED}})',
        f'$compiled_read(S,porigin_{letter}) = (PINT {value})',
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
    '$lossy_optional_integer_header(S, pfunction, pfunction.SIGNATURE.PARAMETERS, 0)',
    'plenv_alias = plenv_source[.CONSTANTS = [($ptascii("YesReceive219"), $ptascii("false")), ($ptascii("NoReceive219"), $ptascii("false")), ($ptascii("NilReceive219"), $ptascii("null"))]]',
    '$lossy_optional_integer_default_in(plenv_alias, expression_a) = eps',
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


fixed_metadata = 'metadata_a'
expr_yes, expr_no, expr_nil = map(constant, ('YesReceive219','NoReceive219','NilReceive219'))
expr_unknown = unknown()
half = binary('Div',integer(1),integer(2))
checks.extend([
    'plenv_no_true=plenv_source[.CONSTANTS=[($ptascii("YesReceive219"),$ptascii("true")),($ptascii("NoReceive219"),$ptascii("true")),($ptascii("NilReceive219"),$ptascii("null"))]]',
    '$lossy_optional_integer_default_in(plenv_no_true,expression_b) = (2)',
    '$lossy_optional_integer_default_in(plenv_no_true,expression_c) = eps',
    '$lossy_optional_integer_default_in(plenv_no_true,expression_d) = eps',
    '~$lossy_optional_integer_header(S,pfunction[.ENV=plenv_no_true],pfunction.SIGNATURE.PARAMETERS,0)',
    'plenv_nil_false=plenv_source[.CONSTANTS=[($ptascii("YesReceive219"),$ptascii("true")),($ptascii("NoReceive219"),$ptascii("false")),($ptascii("NilReceive219"),$ptascii("false"))]]',
    '$lossy_optional_integer_default_in(plenv_nil_false,expression_c) = (12)',
    '~$lossy_optional_integer_header(S,pfunction[.ENV=plenv_nil_false],pfunction.SIGNATURE.PARAMETERS,0)',
    '$lossy_optional_integer_numeric($plempty(false),expression_float_cast_a) = eps',
    '~$lossy_optional_integer_header(S,pfunction[.ENV=$plempty(false)],pfunction.SIGNATURE.PARAMETERS,0)',
    '$lossy_optional_integer_string_in(plenv_source,expression_leaf_a) = ($ptascii("-7.5tail"))',
    '$lossy_optional_integer_special(plenv_source,expression_leaf_c) = (PBOOL true)',
    '$lossy_optional_integer_special(plenv_source,expression_leaf_d) = (PBOOL false)',
])

# Raw BOOL/string selections stay outside Numeric; NULL selection can choose an integer.
selected_null_integer = binary('Coalesce',ternary(expr_yes,expr_nil,expr_unknown),integer(1))
for child, bits, result in [
    (ternary(expr_yes,string('12.5tail'),expr_unknown),'4029000000000000','12'),
    (ternary(expr_no,expr_unknown,string('0.0')),'0000000000000000','0'),
    (ternary(expr_yes,expr_no,expr_unknown),'0000000000000000','0'),
    (ternary(expr_yes,expr_nil,expr_unknown),'0000000000000000','0'),
    (node('NExprTernary',expr_no,'ABSENT',string('-2.5tail')),'c004000000000000','$(-2)'),
    (node('NExprTernary',expr_yes,'ABSENT',expr_unknown),'3ff0000000000000','1'),
    (binary('Coalesce',expr_nil,string('.5')),'3fe0000000000000','0'),
    (binary('Coalesce',expr_no,expr_unknown),'0000000000000000','0'),
    (binary('Coalesce',string('-0.0tail'),expr_unknown),'8000000000000000','0'),
    (ternary(expr_yes,string('5e-324'),expr_unknown),'0000000000000001','0'),
    (ternary(expr_no,expr_unknown,string('-5e-324')),'8000000000000001','0'),
    (ternary(expr_yes,string('NAN'),expr_unknown),'0000000000000000','0'),
    (ternary(expr_yes,node('NExprCastBool',half),expr_unknown),'3ff0000000000000','1'),
    (selected_null_integer,'3ff0000000000000','1'),
]:
    expression = float_cast(child)
    truth = str(bits not in ['0000000000000000','8000000000000000']).lower()
    raw_numeric = '(NINT 1)' if child == selected_null_integer else 'eps'
    checks.extend([
        f'$lossy_optional_integer_numeric(plenv_source,{child}) = {raw_numeric}',
        f'$lossy_optional_integer_string_in(plenv_source,{child}) = eps',
        f'$lossy_optional_integer_numeric(plenv_source,{expression}) = (NFLOAT $hex_bits("{bits}",0))',
        f'$lossy_optional_integer_default_in(plenv_source,{cast(expression)}) = ({result})',
        f'$lossy_optional_integer_default_in(plenv_source,{expression}) = eps',
        f'$lossy_optional_integer_condition(plenv_source,{expression}) = ({truth})',
        f'$lossy_optional_integer_string_in(plenv_source,{string_cast(expression)}) = eps',
    ])

# Already typed selections remain on the existing Numeric route.
for child, number, bits in [
    (ternary(expr_yes,integer(7),expr_unknown),'NINT 7','401c000000000000'),
    (ternary(expr_yes,half,expr_unknown),'NFLOAT $hex_bits("3fe0000000000000",0)','3fe0000000000000'),
    (binary('Coalesce',expr_nil,half),'NFLOAT $hex_bits("3fe0000000000000",0)','3fe0000000000000'),
]:
    checks.extend([
        f'$lossy_optional_integer_numeric(plenv_source,{child}) = ({number})',
        f'$lossy_optional_integer_numeric(plenv_source,{float_cast(child)}) = (NFLOAT $hex_bits("{bits}",0))',
    ])
selected_nan=ternary(expr_yes,computed_nan(),expr_unknown)
checks.extend([
    f'$lossy_optional_integer_numeric(plenv_source,{selected_nan}) = (NFLOAT n_nan)',
    '$pfcast_nan(PFLOAT n_nan)',
    f'$lossy_optional_integer_numeric(plenv_source,{float_cast(selected_nan)}) = eps',
    f'$lossy_optional_integer_default_in(plenv_source,{cast(float_cast(selected_nan))}) = eps',
    f'$lossy_optional_integer_condition(plenv_source,{float_cast(selected_nan)}) = eps',
])
# A left STRING overflow can be selected before FLOAT conversion; a nonfit left FLOAT cannot.
for child, result in [
    (ternary(expr_yes,string('1e999'),expr_unknown),'(NFLOAT $hex_bits("7ff0000000000000",0))'),
    (binary('Coalesce',string('1e999'),expr_unknown),'(NFLOAT $hex_bits("7ff0000000000000",0))'),
    (binary('Coalesce',computed_inf(),expr_unknown),'eps'),
    (binary('Coalesce',expr_nil,computed_inf()),'(NFLOAT $hex_bits("7ff0000000000000",0))'),
]:
    expression=float_cast(child)
    checks.extend([
        f'$lossy_optional_integer_numeric(plenv_source,{expression}) = {result}',
        f'$lossy_optional_integer_condition(plenv_source,{expression}) = (true)',
        f'$lossy_optional_integer_default_in(plenv_source,{cast(expression)}) = eps',
    ])
for child in [ternary(expr_unknown,string('1'),string('1')),ternary(expr_yes,expr_unknown,string('1')),
              ternary(expr_yes,node('NExprArray','SEQUENCE eps'),expr_unknown),binary('Coalesce',expr_unknown,string('1')),
              ternary(expr_yes,string_cast(floating('3fe0000000000000')),expr_unknown)]:
    checks.append(f'$lossy_optional_integer_numeric(plenv_source,{float_cast(child)}) = eps')
selected=ternary(expr_yes,string('.5tail'),expr_unknown)
for kind,bits,result in [('Plus','4004000000000000','2'),('Minus','bff8000000000000','$(-1)'),('Mul','3ff0000000000000','1'),('Div','3fd0000000000000','0')]:
    expression=binary(kind,float_cast(selected),integer(2))
    checks.extend([f'$lossy_optional_integer_numeric(plenv_source,{expression}) = (NFLOAT $hex_bits("{bits}",0))',
                   f'$lossy_optional_integer_default_in(plenv_source,{cast(expression)}) = ({result})'])
checks.extend([
    f'$lossy_optional_integer_default_in(plenv_source,{cast(dimension(string("019"),float_cast(selected)))}) = eps',
    f'$lossy_optional_integer_string_in(plenv_source,{dimension(string("019"),float_cast(selected))}) = eps',
    f'$lossy_optional_integer_default_in(plenv_source,{cast(dimension(string("019"),cast(float_cast(selected))))}) = (0)',
    f'$lossy_optional_integer_numeric(plenv_source,{binary("Plus",selected,integer(1))}) = eps',
])

# Fresh exact prior formulas retain their own declaration-ENV aliases, source0.
checks.extend([
    'plenv_old217=plenv_source[.CONSTANTS=[($ptascii("YesReceive217"),$ptascii("true")),($ptascii("NoReceive217"),$ptascii("false")),($ptascii("NilReceive217"),$ptascii("null"))]]',
    'plenv_old218=plenv_source[.CONSTANTS=[($ptascii("YesReceive218"),$ptascii("true")),($ptascii("NoReceive218"),$ptascii("false")),($ptascii("NilReceive218"),$ptascii("null"))]]',
])
for suffix, env, alternatives in [('217','plenv_old217',[(ternary(constant('YesReceive217'),string('0.0'),constant('UnselectedReceive217')),'0000000000000000')]),
                                   ('218','plenv_old218',[(ternary(constant('YesReceive218'),string('.5tail'),constant('UnselectedReceive218')),'3fe0000000000000'),(ternary(constant('YesReceive218'),constant('NoReceive218'),constant('UnselectedReceive218')),'0000000000000000'),(binary('Coalesce',constant('NilReceive218'),string('0.0')),'0000000000000000')])]:
    for child,bits in alternatives:
        expression=float_cast(child)
        checks.extend([f'$lossy_optional_integer_numeric({env},{expression}) = (NFLOAT $hex_bits("{bits}",0))',
                       f'$lossy_optional_integer_default_in({env},{cast(expression)}) = (0)'])
for child,bits in [(ternary(constant('YesReceive218'),string('0.0'),constant('UnselectedReceive218')),'0000000000000000'),(ternary(constant('YesReceive218'),constant('NoReceive218'),constant('UnselectedReceive218')),'0000000000000000'),(binary('Coalesce',constant('NilReceive218'),string('.5')),'3fe0000000000000')]:
    checks.append(f'$lossy_optional_integer_numeric(plenv_old218,{float_cast(child)}) = (NFLOAT $hex_bits("{bits}",0))')

# Eight proper selected descendants are traversed under one explicit FLOAT cast.
deep=string('.5tail')
for _ in range(8): deep=ternary(expr_yes,deep,expr_unknown)
checks.extend([f'$lossy_optional_integer_numeric(plenv_source,{float_cast(deep)}) = (NFLOAT $hex_bits("3fe0000000000000",0))',
               f'$lossy_optional_integer_default_in(plenv_source,{cast(float_cast(deep))}) = (0)'])

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
    '$lookup(psymboltable_global.ENV, $ptascii("xReceive219")) = (n_cell)',
    '$lookup(psymboltable_global.ENV, $ptascii("countReceive219")) = (n_count)',
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
    '$lookup(S_done.ENV, $ptascii("gotReceive219")) = (n_got)',
    'S_done.STORE[n_got] = DEFINED (PINT 1)',
    r'$call_descriptors_valid(S_done) /\ $heap_valid($heap_graph(S_done))',
])

CASES = {'selected-scalar-float-cast-reference-leading': {
    'source': leading,
    'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 2 n_cell n_bits i z]',
    'checks': checks,
}}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
