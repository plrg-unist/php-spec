#!/usr/bin/env python3
"""Unary computed FLOAT casts preserve numeric types, source authority and receive ownership."""
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


patterns = [
    cast(node('NExprUnaryMinus', binary('Plus', cast(constant('YesReceive214')), binary('Div', integer(13), integer(2))))),
    cast(node('NExprUnaryMinus', binary('Plus', binary('Div', integer(21), integer(2)), cast(constant('YesReceive214'))))),
    cast(node('NExprUnaryPlus', binary('Div', binary('Plus', integer(27), cast(constant('NoReceive214'))), integer(2)))),
    ternary(cast(node('NExprUnaryMinus', binary('Div', cast(constant('YesReceive214')), integer(2)))), constant('UnselectedReceive214'), cast(string('-9223372036854775808tail'))),
    ternary(cast(node('NExprUnaryPlus', binary('Plus', binary('Div', integer(3), integer(2)), cast(constant('NoReceive214'))))), cast(string('9' * 24)), constant('UnselectedReceive214')),
]

contrasts = [
    ('floatnot', 'deferredFloatNotReceive214', cast(node('NExprBooleanNot', node('NScalarFloat', 'FLOAT "3fe0000000000000"'))), '(0)'),
    ('negative', 'deferredNegativeIndexReceive214', cast(dimension(string('10'), string('-1'))), 'eps'),
    ('floatindex', 'deferredFloatIndexReceive214', cast(dimension(string('10'), string('1.0'))), 'eps'),
    ('floatstring', 'deferredFloatStringReceive214', cast(string_cast(node('NScalarFloat', 'FLOAT "3fe0000000000000"'))), 'eps'),
    ('computednegative', 'deferredComputedNegativeIndexReceive214', cast(dimension(string('10'), binary('Minus', integer(0), integer(1)))), 'eps'),
    ('selectedfloat', 'deferredSelectedFloatStringReceive214', cast(string_cast(ternary(constant('YesReceive214'), floating('3fe0000000000000'), constant('UnselectedReceive214')))), 'eps'),
    ('nonfit', 'deferredComputedFloatNonfitReceive214', cast(binary('Mul', floating('7fe1ccf385ebc8a0'), integer(2))), 'eps'),
    ('zerodiv', 'deferredComputedFloatZeroDivReceive214', cast(binary('Div', floating('3ff0000000000000'), integer(0))), 'eps'),
    ('computednan', 'deferredComputedFloatNanReceive214', cast(binary('Minus', binary('Mul', floating('7fe1ccf385ebc8a0'), integer(2)), binary('Mul', floating('7fe1ccf385ebc8a0'), integer(2)))), 'eps'),
    ('unarynonfit', 'deferredComputedFloatUnaryNonfitReceive214', cast(node('NExprUnaryMinus', cast(string('-9223372036854775808')))), 'eps'),
]

CATALOGUE = Path(__file__).with_name('unary_computed_float_integer_cast_default_reception_cases.json')
assert hashlib.sha256(CATALOGUE.read_bytes()).hexdigest() == '2189bdf33ca900bb8debc021cbae3ec35aaf3b752167cb38e9356d9ef87007f0'
row = next(row for row in json.loads(CATALOGUE.read_text()) if row['id'] == 'unary-computed-float-integer-cast-precision-modes')
assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
source = row['source']
handler = source[:source.index('function valueFirstReceive214(')]
reference = source[source.index('function referenceReceive214('):source.index("set_error_handler('warningReceive214');")]
setup = source[source.index("set_error_handler('warningReceive214');"):source.index('$gotReceive214 = valueFirstReceive214(')]
start = source.index('$gotReceive214 = referenceReceive214(')
end = source.index('$xReceive214 = 1.5;', start)
leading = handler + reference + setup + source[start:end]
assert hashlib.sha256(leading.encode()).hexdigest() == 'f99b1d0a82d5ca946dd40980c534b274d2280afdc27a53c5dd9fb02f029399e9'

checks = [
    r'n_bits = 4609434218613702656 /\ i = 1',
    '$function_at(S.FUNCTIONS, porigin) = (pfunction)',
    'plenv_source = pfunction.ENV',
    r'plenv_source.NAMESPACE = eps /\ plenv_source.CONSTANTS = [($ptascii("YesReceive214"), $ptascii("true")), ($ptascii("NoReceive214"), $ptascii("false")), ($ptascii("NilReceive214"), $ptascii("null"))]',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_a, psparam_b, psparam_c, psparam_d, psparam_e]',
    r'$lossy_optional_integer_mode(pfunction.SIGNATURE.PARAMETERS, true) /\ ~$lossy_optional_integer_mode(pfunction.SIGNATURE.PARAMETERS, false)',
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
checks.extend([
    '$lossy_optional_integer_header(S, pfunction, pfunction.SIGNATURE.PARAMETERS, 0)',
    'plenv_alias = plenv_source[.CONSTANTS = [($ptascii("YesReceive214"), $ptascii("false")), ($ptascii("NoReceive214"), $ptascii("false")), ($ptascii("NilReceive214"), $ptascii("null"))]]',
    '$lossy_optional_integer_default_in(plenv_alias, expression_a) = ($(-6))',
    '$lossy_optional_integer_default_in(plenv_alias, expression_b) = ($(-10))',
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

# These are genuine compiler-deferred declarations in this same source unit.
for suffix, function_name, expression, projection in contrasts:
    checks.extend([
        f'$call_target(S, $ptascii("{function_name}"), eps) = (pfunction_{suffix})',
        f'pfunction_{suffix}.ORIGIN = PORIGIN n_unit pcpath_{suffix}_function',
        f'pfunction_{suffix}.ORIGIN =/= porigin',
        f'pfunction_{suffix}.SIGNATURE.PARAMETERS = [psparam_{suffix}]',
        f'psparam_{suffix}.DEFAULT = PSDEFAULT expression_{suffix} "deferred"',
        f'expression_{suffix} = {expression}',
        f'$default_parameter_origin(S, pfunction_{suffix}.ORIGIN, 0) = PORIGIN n_unit pcpath_{suffix}',
        f'porigin_{suffix} = PORIGIN n_unit (pcpath_{suffix} ++ [PCFIELD 6])',
        f'$origin_node(S.SOURCES, porigin_{suffix}) = (expression_{suffix})',
        f'pfunction_{suffix}.DEFAULTS = [{{INDEX 0, ORIGIN porigin_{suffix}, KIND PDDEFERRED}}]',
        f'$compiled_read(S, porigin_{suffix}) = eps',
        f'$lossy_optional_integer_default_in(pfunction_{suffix}.ENV, expression_{suffix}) = {projection}',
        f'~$lossy_optional_integer_header(S, pfunction_{suffix}, pfunction_{suffix}.SIGNATURE.PARAMETERS, 0)',
        f'psparam_forged_{suffix} = psparam_{suffix}[.DEFAULT = PSDEFAULT expression_{suffix} "int"]',
        f'pfunction_forged_{suffix} = pfunction_{suffix}[.DEFAULTS = [{{INDEX 0, ORIGIN porigin_{suffix}, KIND PDSTORED}}]]',
        f'~$lossy_optional_integer_tail(S, pfunction_forged_{suffix}, [psparam_forged_{suffix}], 0)',
    ])

fixed_metadata = 'metadata_a'
unknown = constant('UnselectedReceive214')
yes, no, nil = map(constant, ('YesReceive214', 'NoReceive214', 'NilReceive214'))

# Exact source roots are CASTINT of generic unary expressions, not signed literals.
checks.extend([
    'expression_numeric_a = NExprUnaryMinus expression_arithmetic_a metadata_unary_a',
    'expression_arithmetic_a = NExprBinaryOpPlus expression_yes_int_a expression_fraction_a metadata_arithmetic_a',
    'expression_b = NExprCastInt expression_numeric_b metadata_b',
    'expression_c = NExprCastInt expression_numeric_c metadata_c',
    'expression_d = NExprTernary expression_int_d expression_unused_d expression_minimum_d metadata_d',
    'expression_int_d = NExprCastInt expression_numeric_d metadata_int_d',
    'expression_e = NExprTernary expression_int_e expression_maximum_e expression_unused_e metadata_e',
    'expression_int_e = NExprCastInt expression_numeric_e metadata_int_e',
    '$lossy_optional_integer_numeric(plenv_source, expression_arithmetic_a) = (NFLOAT $hex_bits("401e000000000000", 0))',
])
for letter, bits in [('a', 'c01e000000000000'), ('b', 'c027000000000000'),
                     ('c', '402b000000000000'), ('d', 'bfe0000000000000'),
                     ('e', '3ff8000000000000')]:
    checks.extend([
        f'$lossy_optional_integer_default_in(plenv_source, expression_numeric_{letter}) = eps',
        f'$lossy_optional_integer_float_literal(expression_numeric_{letter}) = eps',
        f'$lossy_optional_integer_numeric(plenv_source, expression_numeric_{letter}) = (NFLOAT $hex_bits("{bits}", 0))',
    ])
checks.extend([
    '$lossy_optional_integer_default_in(plenv_source, expression_int_d) = (0)',
    '$lossy_optional_integer_default_in(plenv_source, expression_int_e) = (1)',
    '$lossy_optional_integer_condition(plenv_source, expression_int_d) = (false)',
    '$lossy_optional_integer_condition(plenv_source, expression_int_e) = (true)',
    '$lossy_optional_integer_numeric($plempty(false), expression_numeric_a) = eps',
    '$lossy_optional_integer_numeric(plenv_alias, expression_numeric_a) = (NFLOAT $hex_bits("c01a000000000000", 0))',
    'plenv_no_alias = plenv_source[.CONSTANTS = [($ptascii("YesReceive214"), $ptascii("true")), ($ptascii("NoReceive214"), $ptascii("true")), ($ptascii("NilReceive214"), $ptascii("null"))]]',
    '$lossy_optional_integer_default_in(plenv_no_alias, expression_c) = (14)',
    '~$lossy_optional_integer_header(S, pfunction[.ENV = plenv_no_alias], pfunction.SIGNATURE.PARAMETERS, 0)',
])

# Both generic signs preserve FLOAT bits and truncate only at the explicit cast.
fraction = binary('Div', integer(5), integer(2))
negative_zero = binary('Div', integer(0), node('NExprUnaryMinus', floating('3fe0000000000000')))
for expression, bits, value in [
    (node('NExprUnaryMinus', fraction), 'c004000000000000', -2),
    (node('NExprUnaryPlus', fraction), '4004000000000000', 2),
    (node('NExprUnaryMinus', node('NExprUnaryMinus', fraction)), '4004000000000000', 2),
    (node('NExprUnaryPlus', node('NExprUnaryMinus', fraction)), 'c004000000000000', -2),
    (node('NExprUnaryMinus', negative_zero), '0000000000000000', 0),
    (node('NExprUnaryPlus', negative_zero), '8000000000000000', 0),
    (node('NExprUnaryMinus', binary('Mul', floating('0000000000000000'), integer(1))), '8000000000000000', 0),
    (node('NExprUnaryMinus', binary('Plus', floating('0000000000000001'), floating('0000000000000001'))), '8000000000000002', 0),
    (node('NExprUnaryPlus', binary('Plus', floating('3ff0000000000000'), floating('3ca0000000000000'))), '3ff0000000000000', 1),
    (node('NExprUnaryMinus', binary('Div', binary('Plus', integer(9223372036854775807), integer(1025)), integer(2))), 'c3d0000000000001', -4611686018427388928),
    (node('NExprUnaryPlus', binary('Minus', integer(-9223372036854775808), integer(1))), 'c3e0000000000000', -9223372036854775808),
]:
    result = str(value) if value >= 0 else f'$({value})'
    checks.extend([
        f'$lossy_optional_integer_default_in(plenv_source, {expression}) = eps',
        f'$lossy_optional_integer_float_literal({expression}) = eps',
        f'$lossy_optional_integer_numeric(plenv_source, {expression}) = (NFLOAT $hex_bits("{bits}", 0))',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = ({result})',
    ])
composed = binary('Plus', node('NExprUnaryMinus', fraction), floating('3ff8000000000000'))
checks.extend([
    f'$lossy_optional_integer_numeric(plenv_source, {composed}) = (NFLOAT $hex_bits("bff0000000000000", 0))',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(composed)}) = ($(-1))',
])

# Existing INT and signed-literal paths stay disjoint from generic unary recursion.
for expression, value in [
    (node('NExprUnaryPlus', binary('Plus', integer(1), integer(2))), 3),
    (node('NExprUnaryMinus', binary('Plus', integer(1), integer(2))), -3),
    (node('NExprUnaryMinus', binary('Plus', integer(0), integer(0))), 0),
    (node('NExprUnaryMinus', cast(yes)), -1),
    (node('NExprUnaryPlus', cast(no)), 0),
]:
    result = str(value) if value >= 0 else f'$({value})'
    checks.extend([
        f'$lossy_optional_integer_default_in(plenv_source, {expression}) = ({result})',
        f'$lossy_optional_integer_numeric(plenv_source, {expression}) = (NINT {result})',
    ])
for expression, bits, value in [
    (node('NExprUnaryMinus', floating('401f000000000000')), 'c01f000000000000', -7),
    (node('NExprUnaryPlus', floating('401f000000000000')), '401f000000000000', 7),
    (node('NExprUnaryMinus', node('NExprUnaryMinus', floating('8000000000000000'))), '8000000000000000', 0),
]:
    result = str(value) if value >= 0 else f'$({value})'
    checks.extend([
        f'$lossy_optional_integer_float_literal({expression}) = ($hex_bits("{bits}", 0))',
        f'$lossy_optional_integer_numeric(plenv_source, {expression}) = (NFLOAT $hex_bits("{bits}", 0))',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = ({result})',
    ])

# MIN negation promotes to FLOAT; the final fit guard rejects its first cast.
minimum = cast(string('-9223372036854775808'))
promoted = node('NExprUnaryMinus', minimum)
refitted = binary('Div', promoted, integer(2))
checks.extend([
    f'$lossy_optional_integer_numeric(plenv_source, {promoted}) = (NFLOAT $hex_bits("43e0000000000000", 0))',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(promoted)}) = eps',
    f'$lossy_optional_integer_numeric(plenv_source, {refitted}) = (NFLOAT $hex_bits("43d0000000000000", 0))',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(refitted)}) = (4611686018427387904)',
])
nonfit = binary('Mul', floating('7fe1ccf385ebc8a0'), integer(2))
nan = node('NExprUnaryMinus', binary('Minus', nonfit, nonfit))
checks.extend([
    f'$lossy_optional_integer_numeric(plenv_source, {nan}) = (NFLOAT n_unary_nan)',
    '$pfcast_nan(PFLOAT n_unary_nan)',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(nan)}) = eps',
])

# Whole-expression integer certificates take precedence over operand admission.
overrange_literal = integer(9223372036854775808)
# Untyped coercions, nonnumeric syntax and zero divisors do not gain authority.
for child in [
    yes, no, nil, string('1'), unknown,
    overrange_literal, integer(-9223372036854775809),
    binary('Div', floating('3ff0000000000000'), integer(0)),
    ternary(yes, floating('3fe0000000000000'), unknown),
    node('NExprVariable', 'BYTES "eA=="'), node('NExprArray', 'SEQUENCE eps'),
]:
    for constructor in ['NExprUnaryPlus', 'NExprUnaryMinus']:
        expression = node(constructor, child)
        whole_min = constructor == 'NExprUnaryMinus' and child == overrange_literal
        numeric_result = '(NINT $(-9223372036854775808))' if whole_min else 'eps'
        integer_result = '($(-9223372036854775808))' if whole_min else 'eps'
        checks.extend([
            f'$lossy_optional_integer_numeric(plenv_source, {expression}) = {numeric_result}',
            f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = {integer_result}',
        ])
checks.extend([
    f'$lossy_optional_integer_numeric(plenv_source, {overrange_literal}) = eps',
    f'$lossy_optional_integer_default_in(plenv_source, {node("NExprUnaryMinus", overrange_literal)}) = ($(-9223372036854775808))',
])

# Generic FLOAT signs still supply no raw truth, byte or DIM-key proof.
computed = node('NExprUnaryMinus', fraction)
checks.extend([
    f'$lossy_optional_integer_condition(plenv_source, {computed}) = (true)',
    f'$lossy_optional_integer_string_in(plenv_source, {string_cast(computed)}) = eps',
    f'$lossy_optional_integer_string_in(plenv_source, {dimension(string("019"), computed)}) = eps',
])

# Preserve the one promoted prior numeric input, with its exact DIV and unary sign.
checks.extend([
    f'$lossy_optional_integer_numeric(plenv_source, {computed}) = (NFLOAT $hex_bits("c004000000000000", 0))',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(computed)}) = ($(-2))',
])

deep = fraction
for _ in range(8):
    deep = node('NExprUnaryMinus', node('NExprUnaryPlus', deep))
checks.extend([
    f'$lossy_optional_integer_numeric(plenv_source, {deep}) = (NFLOAT $hex_bits("4004000000000000", 0))',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(deep)}) = (2)',
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
    '$lookup(psymboltable_global.ENV, $ptascii("xReceive214")) = (n_cell)',
    '$lookup(psymboltable_global.ENV, $ptascii("countReceive214")) = (n_count)',
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
    '$lookup(S_done.ENV, $ptascii("gotReceive214")) = (n_got)',
    'S_done.STORE[n_got] = DEFINED (PINT 1)',
    r'$call_descriptors_valid(S_done) /\ $heap_valid($heap_graph(S_done))',
])

CASES = {'unary-computed-float-integer-cast-reference-leading': {
    'source': leading,
    'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 2 n_cell n_bits i z]',
    'checks': checks,
}}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
