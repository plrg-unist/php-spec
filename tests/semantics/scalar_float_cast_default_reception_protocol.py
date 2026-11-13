#!/usr/bin/env python3
"""Explicit scalar FLOAT casts preserve types and receive authority."""
import base64
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('scalar_float_cast_default_reception_cases.json')
SOURCES = {}
for row in json.loads(CATALOGUE.read_text()):
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
    SOURCES[row['id']] = row['source']

# Fresh first-VAL front preserves the whole five-default declaration; source0.
full = SOURCES['scalar-float-cast-precision-modes']
setup = full.index("set_error_handler('warningReceive218');")
start = full.index('$gotReceive218 = valueFirstReceive218(')
end = full.index('$xReceive218 = 1.5;', start)
source = full[:full.index('function referenceFirstReceive218')] + full[setup:end]
assert hashlib.sha256(source.encode()).hexdigest() == 'e68c5a36a3b5d921cd68ef0591b30bd5f3c080d62f9b3620a2463b062a86d62d'

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
    return constant('UnselectedReceive218')


yes = lambda: cast(constant('YesReceive218'))
no = lambda: cast(constant('NoReceive218'))
large = lambda: floating('7fe1ccf385ebc8a0')
computed_inf = lambda: binary('Mul', large(), integer(2))
computed_nan = lambda: binary('Minus', computed_inf(), computed_inf())
def float_cast(child):
    return node('NExprCastDouble', child)




children = [
    binary('Concat',string_cast(constant('YesReceive218')),string('.5tail')),
    binary('Concat',node('NExprBitwiseNot',string(bytes((207,207)))),string_cast(constant('NoReceive218'))),
    node('NExprBooleanNot',constant('NoReceive218')),
    constant('NilReceive218'),constant('YesReceive218'),
]
floating_casts=[float_cast(child) for child in children]
false_cast=float_cast(constant('NoReceive218'))
operands=[binary('Minus',floating_casts[0],floating('4022000000000000')),binary('Minus',floating_casts[1],floating('4027000000000000')),binary('Minus',binary('Plus',floating_casts[2],floating('4029000000000000')),false_cast),floating_casts[3],floating_casts[4]]
patterns=[cast(operands[0]),cast(operands[1]),cast(operands[2]),conditional(cast(operands[3]),unknown(),cast(string('-9223372036854775808tail'))),conditional(cast(operands[4]),cast(string('9'*24)),unknown())]


contrasts = [
    ('floatnot','deferredFloatNotReceive218',cast(node('NExprBooleanNot',floating('3fe0000000000000'))),'(0)'),
    ('negative','deferredNegativeIndexReceive218',cast(dimension(string('10'),string('-1'))),'eps'),
    ('floatindex','deferredFloatIndexReceive218',cast(dimension(string('10'),string('1.0'))),'eps'),
    ('floatstring','deferredFloatStringReceive218',cast(string_cast(floating('3fe0000000000000'))),'eps'),
    ('computednegative','deferredComputedNegativeIndexReceive218',cast(dimension(string('10'),binary('Minus',integer(0),integer(1)))),'eps'),
    ('selectedfloat','deferredSelectedFloatStringReceive218',cast(string_cast(conditional(constant('YesReceive218'),floating('3fe0000000000000'),unknown()))),'eps'),
    ('nonfit','deferredComputedFloatNonfitReceive218',cast(computed_inf()),'eps'),
    ('zerodiv','deferredComputedFloatZeroDivReceive218',cast(binary('Div',floating('3ff0000000000000'),integer(0))),'eps'),
    ('computednan','deferredComputedFloatNanReceive218',cast(computed_nan()),'eps'),
    ('unarynonfit','deferredComputedFloatUnaryNonfitReceive218',cast(negate(cast(string('-9223372036854775808')))),'eps'),
    ('computednot','deferredComputedFloatNotReceive218',cast(node('NExprBooleanNot',binary('Div',yes(),integer(2)))),'(0)'),
    ('computednannot','deferredComputedFloatNanNotReceive218',cast(node('NExprBooleanNot',computed_nan())),'eps'),
    ('selectednonfit','deferredSelectedFloatArithmeticNonfitReceive218',cast(binary('Plus',conditional(constant('YesReceive218'),computed_inf(),unknown()),integer(0))),'eps'),
    ('coalescenonfit','deferredSelectedFloatCoalesceNonfitReceive218',cast(binary('Plus',binary('Coalesce',computed_inf(),unknown()),integer(0))),'eps'),
    ('selectednan','deferredSelectedFloatArithmeticNanReceive218',cast(binary('Minus',conditional(constant('YesReceive218'),computed_inf(),unknown()),conditional(constant('NoReceive218'),unknown(),computed_inf()))),'eps'),
    ('floatcastnan','deferredNumericFloatCastNanReceive218',cast(float_cast(computed_nan())),'eps'),
    ('floatcastnonfit','deferredNumericFloatCastNonfitReceive218',cast(float_cast(cast(string('9223372036854775807')))),'eps'),
    ('scalarfloatnonfit','deferredScalarFloatCastNonfitReceive218',cast(float_cast(string('1e999'))),'eps'),
]

checks = [
    r'n_bits = 4609434218613702656 /\ i = 1',
    '$function_at(S.FUNCTIONS, porigin) = (pfunction)',
    'plenv_source = pfunction.ENV',
    r'plenv_source.NAMESPACE = eps /\ plenv_source.CONSTANTS = [($ptascii("YesReceive218"), $ptascii("true")), ($ptascii("NoReceive218"), $ptascii("false")), ($ptascii("NilReceive218"), $ptascii("null"))]',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_a, psparam_b, psparam_c, psparam_d, psparam_e]',
    r'~psparam_a.REQUIRED /\ ~psparam_a.BYREF /\ psparam_b.BYREF /\ psparam_d.BYREF /\ psparam_e.BYREF',
]
for index, (letter, pattern, child, floating_cast, operand, value, bits, operand_bits) in enumerate(zip(
    'abcde', patterns, children, floating_casts, operands,
    ('$(-7)', '$(-11)', '13', '$(-9223372036854775808)', '9223372036854775807'),
    ('3ff8000000000000', '0000000000000000', '3ff0000000000000', '0000000000000000', '3ff0000000000000'),
    ('c01e000000000000', 'c027000000000000', '402b000000000000', '0000000000000000', '3ff0000000000000'),
)):
    checks.extend([
        f'psparam_{letter}.DEFAULT = PSDEFAULT expression_{letter} "int"',
        f'expression_{letter} = {pattern}',
        f'expression_child_{letter} = {child}',
        f'expression_float_cast_{letter} = {floating_cast}',
        f'expression_operand_{letter} = {operand}',
        f'$lossy_optional_integer_numeric(plenv_source, expression_child_{letter}) = eps',
        f'$lossy_optional_integer_numeric(plenv_source, expression_float_cast_{letter}) = (NFLOAT $hex_bits("{bits}", 0))',
        f'$lossy_optional_integer_numeric(plenv_source, expression_operand_{letter}) = (NFLOAT $hex_bits("{operand_bits}", 0))',
        f'$lossy_optional_integer_condition(plenv_source, expression_float_cast_{letter}) = ({str(letter not in "bd").lower()})',
        f'$lossy_optional_integer_default_in(plenv_source, expression_{letter}) = ({value})',
        f'$default_parameter_origin(S, porigin, {index}) = PORIGIN n_unit pcpath_{letter}',
        f'porigin_{letter} = PORIGIN n_unit (pcpath_{letter} ++ [PCFIELD 6])',
        f'$origin_node(S.SOURCES, porigin_{letter}) = (expression_{letter})',
        f'$default_at(pfunction.DEFAULTS, {index}) = ({{INDEX {index}, ORIGIN porigin_{letter}, KIND PDSTORED}})',
        f'$compiled_read(S, porigin_{letter}) = (PINT {value})',
    ])
checks.extend([
    '$lossy_optional_integer_header(S, pfunction, pfunction.SIGNATURE.PARAMETERS, 0)',
    'expression_a = NExprCastInt expression_operand_a metadata_a',
    '$lossy_optional_integer_string_in(plenv_source, expression_child_a) = ($ptascii("1.5tail"))',
    '$lossy_optional_integer_string_in(plenv_source, expression_child_b) = ($ptascii("00"))',
    '$lossy_optional_integer_condition(plenv_source, expression_child_b) = (true)',
    '$lossy_optional_integer_boolean_shape(expression_child_c)',
    '$lossy_optional_integer_special(plenv_source, expression_child_d) = (PNULL)',
    '$lossy_optional_integer_special(plenv_source, expression_child_e) = (PBOOL true)',
    f'expression_false_cast = {false_cast}',
    '$lossy_optional_integer_numeric(plenv_source, expression_false_cast) = (NFLOAT $hex_bits("0000000000000000", 0))',
    '$lossy_optional_integer_numeric($plempty(false), expression_float_cast_a) = eps',
    '~$lossy_optional_integer_header(S, pfunction[.ENV = $plempty(false)], pfunction.SIGNATURE.PARAMETERS, 0)',
    'plenv_yes_false = plenv_source[.CONSTANTS = [($ptascii("YesReceive218"), $ptascii("false")), ($ptascii("NoReceive218"), $ptascii("false")), ($ptascii("NilReceive218"), $ptascii("null"))]]',
    '$lossy_optional_integer_default_in(plenv_yes_false, expression_a) = ($(-8))',
    '$lossy_optional_integer_default_in(plenv_yes_false, expression_e) = eps',
    '~$lossy_optional_integer_header(S, pfunction[.ENV = plenv_yes_false], pfunction.SIGNATURE.PARAMETERS, 0)',
    'plenv_no_true = plenv_source[.CONSTANTS = [($ptascii("YesReceive218"), $ptascii("true")), ($ptascii("NoReceive218"), $ptascii("true")), ($ptascii("NilReceive218"), $ptascii("null"))]]',
    '$lossy_optional_integer_default_in(plenv_no_true, expression_b) = ($(-10))',
    '$lossy_optional_integer_default_in(plenv_no_true, expression_c) = (11)',
    '~$lossy_optional_integer_header(S, pfunction[.ENV = plenv_no_true], pfunction.SIGNATURE.PARAMETERS, 0)',
    'plenv_nil_true = plenv_source[.CONSTANTS = [($ptascii("YesReceive218"), $ptascii("true")), ($ptascii("NoReceive218"), $ptascii("false")), ($ptascii("NilReceive218"), $ptascii("true"))]]',
    '$lossy_optional_integer_default_in(plenv_nil_true, expression_d) = eps',
    '~$lossy_optional_integer_header(S, pfunction[.ENV = plenv_nil_true], pfunction.SIGNATURE.PARAMETERS, 0)',
    'expression_same = NExprUnaryMinus (NScalarInt (INTEGER 7) metadata_a) metadata_a',
    '$lossy_optional_integer_default_in(plenv_source, expression_same) = ($(-7))',
    '~$lossy_optional_integer_tail(S, pfunction, [psparam_a[.DEFAULT = PSDEFAULT expression_same "int"]], 0)',
    'pfunction.DEFAULTS = [pdefault_a, pdefault_b, pdefault_c, pdefault_d, pdefault_e]',
    '~$lossy_optional_integer_tail(S, pfunction[.DEFAULTS = [pdefault_a, pdefault_b[.KIND = PDDEFERRED], pdefault_c, pdefault_d, pdefault_e]], [psparam_b], 1)',
    'S_wrong_value = S[.POOLS = [{UNIT n_unit, CONSTANTS ([(PCONSTANT (pcpath_c ++ [PCFIELD 6]) (PINT 1))])}]]',
    '~$lossy_optional_integer_tail(S_wrong_value, pfunction, [psparam_c], 2)',
])
# Helper values cannot substitute for source/deferred/PINT authority.
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
expr_yes, expr_no, expr_nil = map(constant, ('YesReceive218', 'NoReceive218', 'NilReceive218'))
expr_unknown = unknown()
half = binary('Div', integer(1), integer(2))
# Byte parsing preserves FLOAT values before integer truncation or Boolean truth.
for value, bits, result, truth in [
    ('', '0000000000000000', '(0)', False),
    ('0', '0000000000000000', '(0)', False),
    ('00', '0000000000000000', '(0)', False),
    ('0.0', '0000000000000000', '(0)', False),
    ('word', '0000000000000000', '(0)', False),
    ('NAN', '0000000000000000', '(0)', False),
    (b'\0', '0000000000000000', '(0)', False),
    ('.5tail', '3fe0000000000000', '(0)', True),
    ('-.5tail', 'bfe0000000000000', '(0)', True),
    ('-0.0tail', '8000000000000000', '(0)', False),
    ('5e-324tail', '0000000000000001', '(0)', True),
    ('1e999', '7ff0000000000000', 'eps', True),
]:
    child = string(value);expression = float_cast(child)
    checks.extend([
        f'$lossy_optional_integer_numeric(plenv_source, {child}) = eps',
        f'$lossy_optional_integer_numeric(plenv_source, {expression}) = (NFLOAT $hex_bits("{bits}", 0))',
        f'$lossy_optional_integer_condition(plenv_source, {expression}) = ({str(truth).lower()})',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = {result}',
        f'$lossy_optional_integer_string_in(plenv_source, {string_cast(expression)}) = eps',
    ])
# Constant specials and quiet Boolean-shaped children remain distinct input domains.
for child, truth in [(expr_yes, True), (expr_no, False), (expr_nil, False),
                     (node('NExprBooleanNot', expr_no), True),
                     (node('NExprCastBool', half), True),
                     (node('NExprCastBool', string('00')), True),
                     (binary('BooleanAnd', expr_no, expr_unknown), False),
                     (binary('BooleanOr', expr_yes, expr_unknown), True)]:
    expression = float_cast(child)
    bits = '3ff0000000000000' if truth else '0000000000000000'
    checks.extend([
        f'$lossy_optional_integer_numeric(plenv_source, {child}) = eps',
        f'$lossy_optional_integer_numeric(plenv_source, {expression}) = (NFLOAT $hex_bits("{bits}", 0))',
        f'$lossy_optional_integer_condition(plenv_source, {expression}) = ({str(truth).lower()})',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = ({int(truth)})',
    ])
# Existing typed numeric casts keep their tags, rounding and final fit bounds.
for child, bits, result in [(integer(1), '3ff0000000000000', '(1)'),
                            (floating('8000000000000000'), '8000000000000000', '(0)'),
                            (integer(9223372036854775807), '43e0000000000000', 'eps')]:
    checks.extend([
        f'$lossy_optional_integer_numeric(plenv_source, {float_cast(child)}) = (NFLOAT $hex_bits("{bits}", 0))',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(float_cast(child))}) = {result}',
    ])
# Bare values, raw selected scalar producers and arithmetic implicit coercion stay out.
for child, truth in [(conditional(expr_yes, string('.5tail'), expr_unknown), True),
                     (conditional(expr_yes, expr_no, expr_unknown), False),
                     (binary('Coalesce', expr_nil, string('0.0')), False)]:
    checks.extend([
        f'$lossy_optional_integer_numeric(plenv_source, {float_cast(child)}) = eps',
        f'$lossy_optional_integer_condition(plenv_source, {float_cast(child)}) = ({str(truth).lower()})',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(float_cast(child))}) = eps',
    ])
for child in [expr_unknown, node('NExprArray', 'SEQUENCE eps'), binary('Plus', string('1'), integer(1)),
              binary('Plus', expr_yes, integer(1)), node('NExprCastBool', computed_nan())]:
    checks.append(f'$lossy_optional_integer_numeric(plenv_source, {float_cast(child)}) = eps')
for child in [computed_nan(), floating('7ff8000000000000')]:
    checks.extend([
        f'$lossy_optional_integer_numeric(plenv_source, {float_cast(child)}) = eps',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(float_cast(child))}) = eps',
    ])
# A selected byte leaf becomes eligible through the existing explicit byte CASTSTRING wrapper.
selected_bytes = string_cast(conditional(expr_yes, string('13.5tail'), expr_unknown))
checks.extend([
    f'$lossy_optional_integer_numeric(plenv_source, {float_cast(selected_bytes)}) = (NFLOAT $hex_bits("402b000000000000", 0))',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(float_cast(selected_bytes))}) = (13)',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(dimension(string("10"), float_cast(string(".5"))))}) = eps',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(dimension(string("10"), cast(float_cast(string(".5")))))}) = (1)',
    f'$lossy_optional_integer_numeric(plenv_source, {float_cast(constant("true", qualified=True))}) = (NFLOAT $hex_bits("3ff0000000000000", 0))',
])
# Fresh exact36 prior RHS inputs, with old217 alias targets retained; source0.
checks.append('plenv_old217 = plenv_source[.CONSTANTS = [($ptascii("YesReceive217"), $ptascii("true")), ($ptascii("NoReceive217"), $ptascii("false")), ($ptascii("NilReceive217"), $ptascii("null"))]]')
checks.extend([
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt (NExprCastDouble (NExprBitwiseNot (NScalarString (BYTES "z9HP") metadata_a) metadata_a) metadata_a) metadata_a) = (0)',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt (NExprCastDouble (NExprBitwiseNot (NScalarString (BYTES "z9HKi56Wkw==") metadata_a) metadata_a) metadata_a) metadata_a) = (0)',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt (NExprCastDouble (NExprBinaryOpBitwiseOr (NScalarString (BYTES "MC4w") metadata_a) (NScalarString (BYTES "AA==") metadata_a) metadata_a) metadata_a) metadata_a) = (0)',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt (NExprCastDouble (NExprBinaryOpConcat (NScalarString (BYTES "MA==") metadata_a) (NScalarString (BYTES "LjA=") metadata_a) metadata_a) metadata_a) metadata_a) = (0)',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt (NExprCastDouble (NExprBinaryOpConcat (NScalarString (BYTES "MC4=") metadata_a) (NScalarString (BYTES "NXRhaWw=") metadata_a) metadata_a) metadata_a) metadata_a) = (0)',
    '$lossy_optional_integer_numeric(plenv_old217, NExprCastDouble (NScalarString (BYTES "MC4w") metadata_a) metadata_a) = (NFLOAT $hex_bits("0000000000000000", 0))',
    '$lossy_optional_integer_default_in(plenv_old217, NExprCastInt (NExprCastDouble (NScalarString (BYTES "MC4w") metadata_a) metadata_a) metadata_a) = (0)',
    '$lossy_optional_integer_numeric(plenv_old217, NExprCastDouble (NScalarString (BYTES "LjV0YWls") metadata_a) metadata_a) = (NFLOAT $hex_bits("3fe0000000000000", 0))',
    '$lossy_optional_integer_default_in(plenv_old217, NExprCastInt (NExprCastDouble (NScalarString (BYTES "LjV0YWls") metadata_a) metadata_a) metadata_a) = (0)',
    '$lossy_optional_integer_numeric(plenv_old217, NExprCastDouble (NScalarString (BYTES "eA==") metadata_a) metadata_a) = (NFLOAT $hex_bits("0000000000000000", 0))',
    '$lossy_optional_integer_default_in(plenv_old217, NExprCastInt (NExprCastDouble (NScalarString (BYTES "eA==") metadata_a) metadata_a) metadata_a) = (0)',
    '$lossy_optional_integer_numeric(plenv_old217, NExprCastDouble (NExprConstFetch (NName (BYTES "dHJ1ZQ==") metadata_a) metadata_a) metadata_a) = (NFLOAT $hex_bits("3ff0000000000000", 0))',
    '$lossy_optional_integer_default_in(plenv_old217, NExprCastInt (NExprCastDouble (NExprConstFetch (NName (BYTES "dHJ1ZQ==") metadata_a) metadata_a) metadata_a) metadata_a) = (1)',
    '$lossy_optional_integer_numeric(plenv_old217, NExprCastDouble (NExprConstFetch (NName (BYTES "ZmFsc2U=") metadata_a) metadata_a) metadata_a) = (NFLOAT $hex_bits("0000000000000000", 0))',
    '$lossy_optional_integer_default_in(plenv_old217, NExprCastInt (NExprCastDouble (NExprConstFetch (NName (BYTES "ZmFsc2U=") metadata_a) metadata_a) metadata_a) metadata_a) = (0)',
    '$lossy_optional_integer_numeric(plenv_old217, NExprCastDouble (NExprConstFetch (NName (BYTES "bnVsbA==") metadata_a) metadata_a) metadata_a) = (NFLOAT $hex_bits("0000000000000000", 0))',
    '$lossy_optional_integer_default_in(plenv_old217, NExprCastInt (NExprCastDouble (NExprConstFetch (NName (BYTES "bnVsbA==") metadata_a) metadata_a) metadata_a) metadata_a) = (0)',
    '$lossy_optional_integer_numeric(plenv_old217, NExprCastDouble (NExprConstFetch (NName (BYTES "WWVzUmVjZWl2ZTIxNw==") metadata_a) metadata_a) metadata_a) = (NFLOAT $hex_bits("3ff0000000000000", 0))',
    '$lossy_optional_integer_default_in(plenv_old217, NExprCastInt (NExprCastDouble (NExprConstFetch (NName (BYTES "WWVzUmVjZWl2ZTIxNw==") metadata_a) metadata_a) metadata_a) metadata_a) = (1)',
    '$lossy_optional_integer_numeric(plenv_old217, NExprCastDouble (NExprConstFetch (NName (BYTES "Tm9SZWNlaXZlMjE3") metadata_a) metadata_a) metadata_a) = (NFLOAT $hex_bits("0000000000000000", 0))',
    '$lossy_optional_integer_default_in(plenv_old217, NExprCastInt (NExprCastDouble (NExprConstFetch (NName (BYTES "Tm9SZWNlaXZlMjE3") metadata_a) metadata_a) metadata_a) metadata_a) = (0)',
    '$lossy_optional_integer_numeric(plenv_old217, NExprCastDouble (NExprConstFetch (NName (BYTES "TmlsUmVjZWl2ZTIxNw==") metadata_a) metadata_a) metadata_a) = (NFLOAT $hex_bits("0000000000000000", 0))',
    '$lossy_optional_integer_default_in(plenv_old217, NExprCastInt (NExprCastDouble (NExprConstFetch (NName (BYTES "TmlsUmVjZWl2ZTIxNw==") metadata_a) metadata_a) metadata_a) metadata_a) = (0)',
    '$lossy_optional_integer_numeric(plenv_old217, NExprCastDouble (NScalarString (BYTES "MC4w") metadata_a) metadata_a) = (NFLOAT $hex_bits("0000000000000000", 0))',
    '$lossy_optional_integer_default_in(plenv_old217, NExprCastInt (NExprCastDouble (NScalarString (BYTES "MC4w") metadata_a) metadata_a) metadata_a) = (0)',
    '$lossy_optional_integer_numeric(plenv_old217, NExprCastDouble (NScalarString (BYTES "MC4yNXRhaWw=") metadata_a) metadata_a) = (NFLOAT $hex_bits("3fd0000000000000", 0))',
    '$lossy_optional_integer_default_in(plenv_old217, NExprCastInt (NExprCastDouble (NScalarString (BYTES "MC4yNXRhaWw=") metadata_a) metadata_a) metadata_a) = (0)',
    '$lossy_optional_integer_numeric(plenv_old217, NExprCastDouble (NScalarString (BYTES "MWU5OTk=") metadata_a) metadata_a) = (NFLOAT $hex_bits("7ff0000000000000", 0))',
    '$lossy_optional_integer_numeric(plenv_old217, NExprCastDouble (NExprConstFetch (NName (BYTES "WWVzUmVjZWl2ZTIxNw==") metadata_a) metadata_a) metadata_a) = (NFLOAT $hex_bits("3ff0000000000000", 0))',
    '$lossy_optional_integer_default_in(plenv_old217, NExprCastInt (NExprCastDouble (NExprConstFetch (NName (BYTES "WWVzUmVjZWl2ZTIxNw==") metadata_a) metadata_a) metadata_a) metadata_a) = (1)',
    '$lossy_optional_integer_numeric(plenv_old217, NExprCastDouble (NExprConstFetch (NName (BYTES "Tm9SZWNlaXZlMjE3") metadata_a) metadata_a) metadata_a) = (NFLOAT $hex_bits("0000000000000000", 0))',
    '$lossy_optional_integer_default_in(plenv_old217, NExprCastInt (NExprCastDouble (NExprConstFetch (NName (BYTES "Tm9SZWNlaXZlMjE3") metadata_a) metadata_a) metadata_a) metadata_a) = (0)',
    '$lossy_optional_integer_numeric(plenv_old217, NExprCastDouble (NExprConstFetch (NName (BYTES "TmlsUmVjZWl2ZTIxNw==") metadata_a) metadata_a) metadata_a) = (NFLOAT $hex_bits("0000000000000000", 0))',
    '$lossy_optional_integer_default_in(plenv_old217, NExprCastInt (NExprCastDouble (NExprConstFetch (NName (BYTES "TmlsUmVjZWl2ZTIxNw==") metadata_a) metadata_a) metadata_a) metadata_a) = (0)',
    '$lossy_optional_integer_numeric(plenv_old217, NExprCastDouble (NExprCastBool (NExprBinaryOpDiv (NScalarInt (INTEGER 1) metadata_a) (NScalarInt (INTEGER 2) metadata_a) metadata_a) metadata_a) metadata_a) = (NFLOAT $hex_bits("3ff0000000000000", 0))',
    '$lossy_optional_integer_default_in(plenv_old217, NExprCastInt (NExprCastDouble (NExprCastBool (NExprBinaryOpDiv (NScalarInt (INTEGER 1) metadata_a) (NScalarInt (INTEGER 2) metadata_a) metadata_a) metadata_a) metadata_a) metadata_a) = (1)',
])
deep = float_cast(string('.5tail'))
for _ in range(8):
    deep = float_cast(node('NExprCastBool', deep))
checks.extend([
    f'$lossy_optional_integer_numeric(plenv_source, {deep}) = (NFLOAT $hex_bits("3ff0000000000000", 0))',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(deep)}) = (1)',
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
    '$lookup(psymboltable_global.ENV, $ptascii("xReceive218")) = (n_global)',
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
    '$lookup(S_done.ENV, $ptascii("gotReceive218")) = (n_got)',
    'S_done.STORE[n_got] = DEFINED (PINT 13)',
    r'$call_descriptors_valid(S_done) /\ $heap_valid($heap_graph(S_done))',
])

CASES = {'scalar-float-cast-default-omitted-tail': {
    'source': source,
    'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z]',
    'checks': checks,
}}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
