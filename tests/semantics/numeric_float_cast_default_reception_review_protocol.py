#!/usr/bin/env python3
"""Typed FLOAT casts retain numeric bits, truth partitions and source receive authority."""
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
    return constant('UnselectedReceive217')




def negate(child):
    return node('NExprUnaryMinus', child)


yes = lambda: cast(constant('YesReceive217'))
no = lambda: cast(constant('NoReceive217'))
large = lambda: floating('7fe1ccf385ebc8a0')
computed_inf = lambda: binary('Mul', large(), integer(2))
computed_nan = lambda: binary('Minus', computed_inf(), computed_inf())
children = [
    binary('Plus', negate(integer(15)), no()),
    binary('Coalesce', constant('NilReceive217'), ternary(constant('YesReceive217'), binary('Div', negate(integer(23)), integer(2)), unknown())),
    node('NExprTernary', binary('Plus', floating('402b000000000000'), no()), 'ABSENT', unknown()),
    ternary(constant('NoReceive217'), unknown(), cast(string('-9223372036854775808tail'))),
    binary('Minus', integer(9223372036854775807), no()),
]
floating_casts = [float_cast(child) for child in children]
operands = [binary('Div', floating_casts[0], integer(2)),floating_casts[1],floating_casts[2],floating_casts[3],binary('Minus', binary('Minus', floating_casts[4], cast(string('9223372036854774784'))), integer(1024))]
patterns = [cast(operands[0]),cast(operands[1]),cast(operands[2]),cast(operands[3]),ternary(cast(operands[4]),unknown(),cast(string('9'*24)))]


contrasts = [
    ('floatnot','deferredFloatNotReceive217',cast(node('NExprBooleanNot',floating('3fe0000000000000'))),'(0)'),
    ('negative','deferredNegativeIndexReceive217',cast(dimension(string('10'),string('-1'))),'eps'),
    ('floatindex','deferredFloatIndexReceive217',cast(dimension(string('10'),string('1.0'))),'eps'),
    ('floatstring','deferredFloatStringReceive217',cast(string_cast(floating('3fe0000000000000'))),'eps'),
    ('computednegative','deferredComputedNegativeIndexReceive217',cast(dimension(string('10'),binary('Minus',integer(0),integer(1)))),'eps'),
    ('selectedfloat','deferredSelectedFloatStringReceive217',cast(string_cast(ternary(constant('YesReceive217'),floating('3fe0000000000000'),unknown()))),'eps'),
    ('nonfit','deferredComputedFloatNonfitReceive217',cast(computed_inf()),'eps'),
    ('zerodiv','deferredComputedFloatZeroDivReceive217',cast(binary('Div',floating('3ff0000000000000'),integer(0))),'eps'),
    ('computednan','deferredComputedFloatNanReceive217',cast(computed_nan()),'eps'),
    ('unarynonfit','deferredComputedFloatUnaryNonfitReceive217',cast(negate(cast(string('-9223372036854775808')))),'eps'),
    ('computednot','deferredComputedFloatNotReceive217',cast(node('NExprBooleanNot',binary('Div',yes(),integer(2)))),'(0)'),
    ('computednannot','deferredComputedFloatNanNotReceive217',cast(node('NExprBooleanNot',computed_nan())),'eps'),
    ('selectednonfit','deferredSelectedFloatArithmeticNonfitReceive217',cast(binary('Plus',ternary(constant('YesReceive217'),computed_inf(),unknown()),integer(0))),'eps'),
    ('coalescenonfit','deferredSelectedFloatCoalesceNonfitReceive217',cast(binary('Plus',binary('Coalesce',computed_inf(),unknown()),integer(0))),'eps'),
    ('selectednan','deferredSelectedFloatArithmeticNanReceive217',cast(binary('Minus',ternary(constant('YesReceive217'),computed_inf(),unknown()),ternary(constant('NoReceive217'),unknown(),computed_inf()))),'eps'),
    ('floatcastnan','deferredNumericFloatCastNanReceive217',cast(float_cast(computed_nan())),'eps'),
    ('floatcastnonfit','deferredNumericFloatCastNonfitReceive217',cast(float_cast(cast(string('9223372036854775807')))),'eps'),
]

CATALOGUE = Path(__file__).with_name('numeric_float_cast_default_reception_cases.json')
assert hashlib.sha256(CATALOGUE.read_bytes()).hexdigest() == '397a893fe79790e6595ba90cce059c6b5feabc393295be0b231c84a67249b36b'
row = next(row for row in json.loads(CATALOGUE.read_text()) if row['id'] == 'numeric-float-cast-precision-modes')
assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
source = row['source']
handler = source[:source.index('function valueFirstReceive217(')]
reference = source[source.index('function referenceReceive217('):source.index("set_error_handler('warningReceive217');")]
setup = source[source.index("set_error_handler('warningReceive217');"):source.index('$gotReceive217 = valueFirstReceive217(')]
start = source.index('$gotReceive217 = referenceReceive217(')
end = source.index('$xReceive217 = 1.5;', start)
leading = handler + reference + setup + source[start:end]
assert hashlib.sha256(leading.encode()).hexdigest() == '0bcb555592932d6fb012e3d4f959eeb803eec91b41ab352d9ef320b29bf7f59b'


checks = [
    r'n_bits = 4609434218613702656 /\ i = 1',
    '$function_at(S.FUNCTIONS, porigin) = (pfunction)',
    'plenv_source = pfunction.ENV',
    r'plenv_source.NAMESPACE = eps /\ plenv_source.CONSTANTS = [($ptascii("YesReceive217"), $ptascii("true")), ($ptascii("NoReceive217"), $ptascii("false")), ($ptascii("NilReceive217"), $ptascii("null"))]',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_a, psparam_b, psparam_c, psparam_d, psparam_e]',
    '$lossy_optional_integer_mode(pfunction.SIGNATURE.PARAMETERS, true)',
    '~$lossy_optional_integer_mode(pfunction.SIGNATURE.PARAMETERS, false)',
    'S.CURRENT = (pcallcontext)',
    r'pcallcontext.ARGC = 3 /\ pcallcontext.HOLES = [0, 1] /\ pcallcontext.NAMED = eps',
]


for index,(letter,pattern,child,floating_cast,operand,value,number,bits,operand_bits) in enumerate(zip('abcde',patterns,children,floating_casts,operands,('$(-7)','$(-11)','13','$(-9223372036854775808)','9223372036854775807'),('NINT $(-15)','NFLOAT $hex_bits("c027000000000000", 0)','NFLOAT $hex_bits("402b000000000000", 0)','NINT $(-9223372036854775808)','NINT 9223372036854775807'),('c02e000000000000','c027000000000000','402b000000000000','c3e0000000000000','43e0000000000000'),('c01e000000000000','c027000000000000','402b000000000000','c3e0000000000000','0000000000000000'))):
    checks.extend([
        rf'~psparam_{letter}.REQUIRED /\ ~psparam_{letter}.VARIADIC /\ $ptmasks(psparam_{letter}.TYPE) = ["int"]',
        f'psparam_{letter}.DEFAULT = PSDEFAULT expression_{letter} "int"',
        f'expression_{letter} = {pattern}',
        f'$lossy_optional_integer_default_in(plenv_source, expression_{letter}) = ({value})',
        f'expression_child_{letter} = {child}',
        f'expression_float_cast_{letter} = {floating_cast}',
        f'expression_operand_{letter} = {operand}',
        f'$lossy_optional_integer_numeric(plenv_source, expression_child_{letter}) = ({number})',
        f'$num_float({number}) = $hex_bits("{bits}", 0)',
        f'$lossy_optional_integer_numeric(plenv_source, expression_float_cast_{letter}) = (NFLOAT $hex_bits("{bits}", 0))',
        f'$lossy_optional_integer_numeric(plenv_source, expression_operand_{letter}) = (NFLOAT $hex_bits("{operand_bits}", 0))',
        f'$lossy_optional_integer_condition(plenv_source, expression_float_cast_{letter}) = (true)',
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
    'plenv_alias = plenv_source[.CONSTANTS = [($ptascii("YesReceive217"), $ptascii("false")), ($ptascii("NoReceive217"), $ptascii("false")), ($ptascii("NilReceive217"), $ptascii("null"))]]',
    '$lossy_optional_integer_default_in(plenv_alias, expression_a) = ($(-7))',
    '$lossy_optional_integer_default_in(plenv_alias, expression_b) = eps',
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
expr_yes,expr_no,expr_nil = map(constant,('YesReceive217','NoReceive217','NilReceive217'))
expr_unknown = unknown()
half = binary('Div',integer(1),integer(2))

# Typed INT conversion rounds once; typed FLOAT conversion keeps its exact bits.
for child,bits,result in [
    (integer(0),'0000000000000000',0),
    (integer(1),'3ff0000000000000',1),
    (integer(9007199254740993),'4340000000000000',9007199254740992),
    (integer(-9007199254740993),'c340000000000000',-9007199254740992),
    (integer(-9223372036854775808),'c3e0000000000000',-9223372036854775808),
    (floating('8000000000000000'),'8000000000000000',0),
    (floating('0000000000000001'),'0000000000000001',0),
    (floating('8000000000000001'),'8000000000000001',0),
    (floating('3fd0000000000000'),'3fd0000000000000',0),
    (ternary(expr_yes,half,expr_unknown),'3fe0000000000000',0),
]:
    expression=float_cast(child);value=str(result) if result>=0 else f'$({result})';truth=str(bits not in ['0000000000000000','8000000000000000']).lower()
    checks.extend([
        f'$lossy_optional_integer_default_in(plenv_source, {expression}) = eps',
        f'$lossy_optional_integer_numeric(plenv_source, {expression}) = (NFLOAT $hex_bits("{bits}", 0))',
        f'$lossy_optional_integer_condition(plenv_source, {expression}) = ({truth})',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = ({value})',
        f'$lossy_optional_integer_string_in(plenv_source, {string_cast(expression)}) = eps',
    ])
maximum= float_cast(integer(9223372036854775807))
inf=float_cast(computed_inf())
for expression,bits in [(maximum,'43e0000000000000'),(inf,'7ff0000000000000'),(float_cast(negate(computed_inf())),'fff0000000000000')]:
    checks.extend([
        f'$lossy_optional_integer_numeric(plenv_source, {expression}) = (NFLOAT $hex_bits("{bits}", 0))',
        f'$lossy_optional_integer_condition(plenv_source, {expression}) = (true)',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = eps',
    ])
# The source MAX boundary depends on FLOAT rounding before the two subtractions.
checks.extend([
    '$lossy_optional_integer_numeric(plenv_source, expression_float_cast_e) = (NFLOAT $hex_bits("43e0000000000000", 0))',
    '$lossy_optional_integer_numeric(plenv_source, expression_operand_e) = (NFLOAT 0)',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt expression_operand_e metadata_a) = (0)',
    'plenv_no_true = plenv_source[.CONSTANTS = [($ptascii("YesReceive217"),$ptascii("true")),($ptascii("NoReceive217"),$ptascii("true")),($ptascii("NilReceive217"),$ptascii("null"))]]',
    '$lossy_optional_integer_default_in(plenv_no_true, expression_c) = (14)',
    '~$lossy_optional_integer_header(S,pfunction[.ENV = plenv_no_true],pfunction.SIGNATURE.PARAMETERS,0)',
])

# Explicit scalar FLOAT casts now project values; raw selected STRING keeps its old truth-only path.
for child,truth,bits,value in [(string('0.0'),False,'0000000000000000',0),(string('0.25tail'),True,'3fd0000000000000',0),(string('1e999'),True,'7ff0000000000000',None),(expr_yes,True,'3ff0000000000000',1),(expr_no,False,'0000000000000000',0),(expr_nil,False,'0000000000000000',0),(ternary(expr_yes,string('0.0'),expr_unknown),False,None,None),(node('NExprCastBool',half),True,'3ff0000000000000',1)]:
    expression=float_cast(child)
    numeric_result=f'(NFLOAT $hex_bits("{bits}", 0))' if bits is not None else 'eps'
    integer_result=f'({value})' if value is not None else 'eps'
    checks.extend([
        f'$lossy_optional_integer_numeric(plenv_source, {expression}) = {numeric_result}',
        f'$lossy_optional_integer_condition(plenv_source, {expression}) = ({str(truth).lower()})',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = {integer_result}',
    ])
checks.extend([
    f'$lossy_optional_integer_numeric(plenv_source, {float_cast(cast(expr_yes))}) = (NFLOAT $hex_bits("3ff0000000000000",0))',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(node("NExprCastBool",float_cast(string("0.0"))))}) = (0)',
    f'$lossy_optional_integer_condition(plenv_source, {string("0.0")}) = (true)',
])

# Static/default cast eligibility rejects NaN; runtime FLOAT identity remains unchanged.
nan=computed_nan()
checks.extend([
    f'$lossy_optional_integer_numeric(plenv_source,{nan}) = (NFLOAT n_nan)',
    '$pfcast_nan(PFLOAT n_nan)',
    '$cast_value(S,CASTFLOAT,PFLOAT n_nan,z) = S[.RESULT = KNOWN (PFLOAT n_nan)]',
])
for child in [nan,floating('7ff8000000000000'),ternary(expr_yes,nan,expr_unknown),float_cast(nan)]:
    expression=float_cast(child)
    checks.extend([
        f'$lossy_optional_integer_numeric(plenv_source,{expression}) = eps',
        f'$lossy_optional_integer_condition(plenv_source,{expression}) = eps',
        f'$lossy_optional_integer_default_in(plenv_source,{cast(expression)}) = eps',
    ])
for child in [integer(9223372036854775808),expr_unknown,node('NExprVariable','BYTES "eA=="'),node('NExprArray','SEQUENCE eps'),binary('Div',integer(1),integer(0))]:
    expression=float_cast(child)
    checks.extend([
        f'$lossy_optional_integer_numeric(plenv_source,{expression}) = eps',
        f'$lossy_optional_integer_condition(plenv_source,{expression}) = eps',
    ])
# The inherited nonnull-left coalesce fit bound remains separate from its quiet truth.
left_inf=binary('Coalesce',computed_inf(),expr_unknown)
checks.extend([
    f'$lossy_optional_integer_numeric(plenv_source,{float_cast(left_inf)}) = eps',
    f'$lossy_optional_integer_condition(plenv_source,{float_cast(left_inf)}) = (true)',
    f'$lossy_optional_integer_numeric(plenv_source,{float_cast(binary("Coalesce",expr_nil,computed_inf()))}) = (NFLOAT $hex_bits("7ff0000000000000",0))',
    f'$lossy_optional_integer_string_in(plenv_source,{dimension(string("019"),float_cast(integer(1)))}) = eps',
    f'$lossy_optional_integer_default_in(plenv_source,{cast(dimension(string("019"),cast(float_cast(integer(1)))))}) = (1)',
])
# Exact two older promoted formulas are covered freshly at this cut.
checks.extend([
    f'$lossy_optional_integer_numeric(plenv_source,{float_cast(integer(1))}) = (NFLOAT $hex_bits("3ff0000000000000",0))',
    f'$lossy_optional_integer_default_in(plenv_source,{cast(float_cast(floating("3fd0000000000000")))}) = (0)',
])
deep=half
for _ in range(8):
    deep=float_cast(binary('Plus',deep,floating('0000000000000000')))
checks.extend([
    f'$lossy_optional_integer_numeric(plenv_source,{deep}) = (NFLOAT $hex_bits("3fe0000000000000",0))',
    f'$lossy_optional_integer_default_in(plenv_source,{cast(deep)}) = (0)',
    f'$lossy_optional_integer_condition(plenv_source,{deep}) = (true)',
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
    '$lookup(psymboltable_global.ENV, $ptascii("xReceive217")) = (n_cell)',
    '$lookup(psymboltable_global.ENV, $ptascii("countReceive217")) = (n_count)',
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
    '$lookup(S_done.ENV, $ptascii("gotReceive217")) = (n_got)',
    'S_done.STORE[n_got] = DEFINED (PINT 1)',
    r'$call_descriptors_valid(S_done) /\ $heap_valid($heap_graph(S_done))',
])

CASES = {'numeric-float-cast-reference-leading': {
    'source': leading,
    'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 2 n_cell n_bits i z]',
    'checks': checks,
}}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
