#!/usr/bin/env python3
"""Computed FLOAT integer casts preserve numeric types, source authority and receive ownership."""
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
    cast(binary('Minus', node('NExprUnaryMinus', floating('401c000000000000')), binary('Div', cast(constant('YesReceive213')), integer(2)))),
    cast(binary('Mul', node('NExprUnaryMinus', floating('4016000000000000')), binary('Plus', integer(1), cast(constant('YesReceive213'))))),
    cast(binary('Plus', floating('402a000000000000'), binary('Div', ternary(constant('NoReceive213'), constant('UnselectedReceive213'), integer(1)), integer(2)))),
    ternary(cast(binary('Div', cast(constant('YesReceive213')), integer(2))), constant('UnselectedReceive213'), cast(string('-9223372036854775808tail'))),
    ternary(cast(binary('Div', binary('Plus', integer(3), cast(constant('NoReceive213'))), integer(2))), cast(string('9' * 24)), constant('UnselectedReceive213')),
]

contrasts = [
    ('floatnot', 'deferredFloatNotReceive213', cast(node('NExprBooleanNot', node('NScalarFloat', 'FLOAT "3fe0000000000000"'))), '(0)'),
    ('negative', 'deferredNegativeIndexReceive213', cast(dimension(string('10'), string('-1'))), 'eps'),
    ('floatindex', 'deferredFloatIndexReceive213', cast(dimension(string('10'), string('1.0'))), 'eps'),
    ('floatstring', 'deferredFloatStringReceive213', cast(string_cast(node('NScalarFloat', 'FLOAT "3fe0000000000000"'))), 'eps'),
    ('computednegative', 'deferredComputedNegativeIndexReceive213', cast(dimension(string('10'), binary('Minus', integer(0), integer(1)))), 'eps'),
    ('selectedfloat', 'deferredSelectedFloatStringReceive213', cast(string_cast(ternary(constant('YesReceive213'), floating('3fe0000000000000'), constant('UnselectedReceive213')))), 'eps'),
    ('nonfit', 'deferredComputedFloatNonfitReceive213', cast(binary('Mul', floating('7fe1ccf385ebc8a0'), integer(2))), 'eps'),
    ('zerodiv', 'deferredComputedFloatZeroDivReceive213', cast(binary('Div', floating('3ff0000000000000'), integer(0))), 'eps'),
    ('computednan', 'deferredComputedFloatNanReceive213', cast(binary('Minus', binary('Mul', floating('7fe1ccf385ebc8a0'), integer(2)), binary('Mul', floating('7fe1ccf385ebc8a0'), integer(2)))), 'eps'),
]

CATALOGUE = Path(__file__).with_name('computed_float_integer_cast_default_reception_cases.json')
assert hashlib.sha256(CATALOGUE.read_bytes()).hexdigest() == '6b79068194d6f5d1c7e9648827d7677138c1848be2a6460d3413933b933041ea'
row = next(row for row in json.loads(CATALOGUE.read_text()) if row['id'] == 'computed-float-integer-cast-precision-modes')
assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
source = row['source']
handler = source[:source.index('function valueFirstReceive213(')]
reference = source[source.index('function referenceReceive213('):source.index("set_error_handler('warningReceive213');")]
setup = source[source.index("set_error_handler('warningReceive213');"):source.index('$gotReceive213 = valueFirstReceive213(')]
start = source.index('$gotReceive213 = referenceReceive213(')
end = source.index('$xReceive213 = 1.5;', start)
leading = handler + reference + setup + source[start:end]
assert hashlib.sha256(leading.encode()).hexdigest() == '8db521b687a1cf58b6e3574801be848a7b901fb1b1152ed58a79f56774784934'

checks = [
    r'n_bits = 4609434218613702656 /\ i = 1',
    '$function_at(S.FUNCTIONS, porigin) = (pfunction)',
    'plenv_source = pfunction.ENV',
    r'plenv_source.NAMESPACE = eps /\ plenv_source.CONSTANTS = [($ptascii("YesReceive213"), $ptascii("true")), ($ptascii("NoReceive213"), $ptascii("false")), ($ptascii("NilReceive213"), $ptascii("null"))]',
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
    'plenv_alias = plenv_source[.CONSTANTS = [($ptascii("YesReceive213"), $ptascii("false")), ($ptascii("NoReceive213"), $ptascii("false")), ($ptascii("NilReceive213"), $ptascii("null"))]]',
    '$lossy_optional_integer_default_in(plenv_alias, expression_a) = ($(-7))',
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
unknown = constant('UnselectedReceive213')
yes, no, nil = map(constant, ('YesReceive213', 'NoReceive213', 'NilReceive213'))

# Exact source-root children remain FLOAT until the explicit integer cast.
checks.extend([
    'expression_numeric_a = NExprBinaryOpMinus expression_negative_seven_a expression_fraction_a metadata_numeric_a',
    'expression_b = NExprCastInt expression_numeric_b metadata_b',
    'expression_c = NExprCastInt expression_numeric_c metadata_c',
    'expression_d = NExprTernary expression_int_d expression_unused_d expression_minimum_d metadata_d',
    'expression_int_d = NExprCastInt expression_numeric_d metadata_int_d',
    'expression_e = NExprTernary expression_int_e expression_maximum_e expression_unused_e metadata_e',
    'expression_int_e = NExprCastInt expression_numeric_e metadata_int_e',
])
for letter, bits in [('a', 'c01e000000000000'), ('b', 'c026000000000000'),
                     ('c', '402b000000000000'), ('d', '3fe0000000000000'),
                     ('e', '3ff8000000000000')]:
    checks.extend([
        f'$lossy_optional_integer_default_in(plenv_source, expression_numeric_{letter}) = eps',
        f'$lossy_optional_integer_numeric(plenv_source, expression_numeric_{letter}) = (NFLOAT $hex_bits("{bits}", 0))',
    ])
checks.extend([
    '$lossy_optional_integer_default_in(plenv_source, expression_int_d) = (0)',
    '$lossy_optional_integer_default_in(plenv_source, expression_int_e) = (1)',
    '$lossy_optional_integer_condition(plenv_source, expression_int_d) = (false)',
    '$lossy_optional_integer_condition(plenv_source, expression_int_e) = (true)',
    '$lossy_optional_integer_numeric(plenv_source, expression_a) = (NINT $(-7))',
    '$lossy_optional_integer_numeric($plempty(false), expression_numeric_a) = eps',
    '$lossy_optional_integer_numeric(plenv_alias, expression_numeric_a) = (NFLOAT $hex_bits("c01c000000000000", 0))',
    'plenv_no_alias = plenv_source[.CONSTANTS = [($ptascii("YesReceive213"), $ptascii("true")), ($ptascii("NoReceive213"), $ptascii("true")), ($ptascii("NilReceive213"), $ptascii("null"))]]',
    '$lossy_optional_integer_default_in(plenv_no_alias, expression_c) = eps',
    '~$lossy_optional_integer_header(S, pfunction[.ENV = plenv_no_alias], pfunction.SIGNATURE.PARAMETERS, 0)',
])

# Known binary64 bits distinguish result type and rounding from integer arithmetic.
for expression, bits, value in [
    (binary('Div', integer(5), integer(2)), '4004000000000000', 2),
    (binary('Div', integer(-5), integer(2)), 'c004000000000000', -2),
    (binary('Plus', floating('401f000000000000'), floating('0000000000000000')), '401f000000000000', 7),
    (binary('Minus', floating('0000000000000000'), floating('3fe0000000000000')), 'bfe0000000000000', 0),
    (binary('Mul', floating('3fe0000000000000'), integer(3)), '3ff8000000000000', 1),
    (binary('Div', floating('400c000000000000'), integer(1)), '400c000000000000', 3),
    (binary('Div', integer(0), node('NExprUnaryMinus', floating('3fe0000000000000'))), '8000000000000000', 0),
    (binary('Plus', floating('0000000000000001'), floating('0000000000000001')), '0000000000000002', 0),
    (binary('Plus', floating('3ff0000000000000'), floating('3ca0000000000000')), '3ff0000000000000', 1),
    (binary('Minus', integer(-9223372036854775808), integer(1)), 'c3e0000000000000', -9223372036854775808),
    (binary('Div', binary('Plus', integer(9223372036854775807), integer(1)), integer(2)), '43d0000000000000', 4611686018427387904),
    (binary('Div', binary('Plus', integer(9223372036854775807), integer(1025)), integer(2)), '43d0000000000001', 4611686018427388928),
    (binary('Div', binary('Mul', integer(4611686018427387904), integer(3)), integer(2)), '43d8000000000000', 6917529027641081856),
    (binary('Plus', floating('43dfffffffffffff'), floating('0000000000000000')), '43dfffffffffffff', 9223372036854774784),
]:
    integer_value = str(value) if value >= 0 else f'$({value})'
    checks.extend([
        f'$lossy_optional_integer_default_in(plenv_source, {expression}) = eps',
        f'$lossy_optional_integer_numeric(plenv_source, {expression}) = (NFLOAT $hex_bits("{bits}", 0))',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = ({integer_value})',
    ])

# Existing integer certificates and signed FLOAT literals preserve their distinct tags.
for expression, value in [
    (integer(3), 3), (binary('Div', integer(6), integer(2)), 3),
    (binary('Plus', integer(1), integer(2)), 3),
    (cast(yes), 1), (cast(nil), 0), (cast(string('1tail')), 1),
    (cast(floating('401f000000000000')), 7),
]:
    checks.extend([
        f'$lossy_optional_integer_default_in(plenv_source, {expression}) = ({value})',
        f'$lossy_optional_integer_numeric(plenv_source, {expression}) = (NINT {value})',
    ])
for expression, bits, value in [
    (floating('401f000000000000'), '401f000000000000', 7),
    (node('NExprUnaryMinus', floating('401f000000000000')), 'c01f000000000000', -7),
    (floating('0000000000000000'), '0000000000000000', 0),
    (floating('8000000000000000'), '8000000000000000', 0),
    (floating('0000000000000001'), '0000000000000001', 0),
]:
    result = str(value) if value >= 0 else f'$({value})'
    checks.extend([
        f'$lossy_optional_integer_float_literal({expression}) = ($hex_bits("{bits}", 0))',
        f'$lossy_optional_integer_numeric(plenv_source, {expression}) = (NFLOAT $hex_bits("{bits}", 0))',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = ({result})',
    ])

# Overflow is computed as FLOAT; only its final fitting, non-NaN cast can be borrowed.
overflow = binary('Plus', integer(9223372036854775807), integer(1025))
checks.extend([
    f'$lossy_optional_integer_numeric(plenv_source, {overflow}) = (NFLOAT $hex_bits("43e0000000000001", 0))',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(overflow)}) = eps',
])
nonfit = binary('Mul', floating('7fe1ccf385ebc8a0'), integer(2))
nan = binary('Minus', nonfit, nonfit)
checks.extend([
    f'$lossy_optional_integer_numeric(plenv_source, {nonfit}) = (NFLOAT $hex_bits("7ff0000000000000", 0))',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(nonfit)}) = eps',
    f'$lossy_optional_integer_numeric(plenv_source, {nan}) = (NFLOAT n_computed_nan)',
    '$pfcast_nan(PFLOAT n_computed_nan)',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(nan)}) = eps',
])

# Raw scalar coercion, other numeric operators, and zero divisors are not this proof.
for expression in [
    yes, no, nil, string('1'), unknown,
    integer(9223372036854775808), integer(-9223372036854775809),
    binary('Plus', yes, integer(1)), binary('Plus', string('1'), integer(1)),
    binary('Div', floating('3ff0000000000000'), integer(0)),
    binary('Div', floating('3ff0000000000000'), floating('8000000000000000')),
    binary('Mod', floating('4004000000000000'), integer(2)),
    binary('Pow', floating('4000000000000000'), integer(2)),
    node('NExprUnaryMinus', binary('Div', integer(5), integer(2))),
    node('NExprCastDouble', integer(1)),
    ternary(yes, floating('3fe0000000000000'), unknown),
    node('NExprVariable', 'BYTES "eA=="'), node('NExprArray', 'SEQUENCE eps'),
]:
    checks.append(f'$lossy_optional_integer_numeric(plenv_source, {expression}) = eps')

# No bare computed-FLOAT truth, byte conversion or DIM key is admitted incidentally.
computed = binary('Div', integer(5), integer(2))
checks.extend([
    f'$lossy_optional_integer_condition(plenv_source, {computed}) = eps',
    f'$lossy_optional_integer_string_in(plenv_source, {string_cast(computed)}) = eps',
    f'$lossy_optional_integer_string_in(plenv_source, {dimension(string("019"), computed)}) = eps',
    f'$lossy_optional_integer_string_in(plenv_source, {dimension(string("019"), cast(computed))}) = ([57])',
    f'$lossy_optional_integer_numeric(plenv_source, {ternary(yes, computed, unknown)}) = eps',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(ternary(yes, computed, unknown))}) = (2)',
])

# The one promoted old196 input remains exact under the old empty-ENV wrapper.
old196 = cast(binary('Plus', floating('401f000000000000'), floating('0000000000000000')))
checks.append(f'$lossy_optional_integer_default_in($plempty(false), {old196}) = (7)')

# Nested typed arithmetic keeps every intermediate binary64 result.
deep = floating('3fe0000000000000')
for _ in range(8):
    deep = binary('Plus', deep, floating('3fe0000000000000'))
checks.extend([
    f'$lossy_optional_integer_numeric(plenv_source, {deep}) = (NFLOAT $hex_bits("4012000000000000", 0))',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(deep)}) = (4)',
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
    '$lookup(psymboltable_global.ENV, $ptascii("xReceive213")) = (n_cell)',
    '$lookup(psymboltable_global.ENV, $ptascii("countReceive213")) = (n_count)',
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
    '$lookup(S_done.ENV, $ptascii("gotReceive213")) = (n_got)',
    'S_done.STORE[n_got] = DEFINED (PINT 1)',
    r'$call_descriptors_valid(S_done) /\ $heap_valid($heap_graph(S_done))',
])

CASES = {'computed-float-integer-cast-reference-leading': {
    'source': leading,
    'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 2 n_cell n_bits i z]',
    'checks': checks,
}}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
