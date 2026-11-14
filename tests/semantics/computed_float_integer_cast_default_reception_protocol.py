#!/usr/bin/env python3
"""Explicit integer casts of computed floats retain typed arithmetic and receive authority."""
import base64
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('computed_float_integer_cast_default_reception_cases.json')
SOURCES = {}
for row in json.loads(CATALOGUE.read_text()):
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
    SOURCES[row['id']] = row['source']

# Fresh first-VAL front preserves the whole five-default declaration; source0.
full = SOURCES['computed-float-integer-cast-precision-modes']
setup = full.index("set_error_handler('warningReceive213');")
start = full.index('$gotReceive213 = valueFirstReceive213(')
end = full.index('$xReceive213 = 1.5;', start)
source = full[:full.index('function referenceFirstReceive213')] + full[setup:end]
assert hashlib.sha256(source.encode()).hexdigest() == '56b6fdda3661b80352787d77e916c1cbc32edc21032103c148cb1a4101e84443'

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


def boolean(child):
    return node('NExprCastBool', child)


def cast(child):
    return node('NExprCastInt', child)


def binary(constructor, left, right):
    return node('NExprBinaryOp' + constructor, left, right)


def conditional(cond, yes, no):
    return node('NExprTernary', cond, yes, no)


def float_cast(child):
    return node('NExprCastDouble', child)


def dimension(base, selector):
    return node('NExprArrayDimFetch', base, selector)


def string_cast(child):
    return node('NExprCastString', child)


patterns = [
    cast(binary('Minus', node('NExprUnaryMinus', floating('401c000000000000')), binary('Div', cast(constant('YesReceive213')), integer(2)))),
    cast(binary('Mul', node('NExprUnaryMinus', floating('4016000000000000')), binary('Plus', integer(1), cast(constant('YesReceive213'))))),
    cast(binary('Plus', floating('402a000000000000'), binary('Div', conditional(constant('NoReceive213'), constant('UnselectedReceive213'), integer(1)), integer(2)))),
    conditional(cast(binary('Div', cast(constant('YesReceive213')), integer(2))), constant('UnselectedReceive213'), cast(string('-9223372036854775808tail'))),
    conditional(cast(binary('Div', binary('Plus', integer(3), cast(constant('NoReceive213'))), integer(2))), cast(string('9' * 24)), constant('UnselectedReceive213')),
]

checks = [
    r'n_bits = 4609434218613702656 /\ i = 1',
    '$function_at(S.FUNCTIONS, porigin) = (pfunction)',
    'plenv_source = pfunction.ENV',
    r'plenv_source.NAMESPACE = eps /\ plenv_source.CONSTANTS = [($ptascii("YesReceive213"), $ptascii("true")), ($ptascii("NoReceive213"), $ptascii("false")), ($ptascii("NilReceive213"), $ptascii("null"))]',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_a, psparam_b, psparam_c, psparam_d, psparam_e]',
    r'~psparam_a.REQUIRED /\ ~psparam_a.BYREF /\ psparam_b.BYREF /\ psparam_d.BYREF /\ psparam_e.BYREF',
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
fixed_metadata = 'metadata_a'
checks.extend([
    '$lossy_optional_integer_header(S, pfunction, pfunction.SIGNATURE.PARAMETERS, 0)',
    'expression_a = NExprCastInt expression_numeric_a metadata_a',
    'expression_b = NExprCastInt expression_numeric_b metadata_b',
    'expression_c = NExprCastInt expression_numeric_c metadata_c',
    'expression_d = NExprTernary (NExprCastInt expression_numeric_d metadata_cast_d) expression_unknown_d expression_minimum metadata_d',
    'expression_e = NExprTernary (NExprCastInt expression_numeric_e metadata_cast_e) expression_maximum expression_unknown_e metadata_e',
])
for letter, bits in [('a', 'c01e000000000000'), ('b', 'c026000000000000'), ('c', '402b000000000000'), ('d', '3fe0000000000000'), ('e', '3ff8000000000000')]:
    checks.extend([
        f'$lossy_optional_integer_default_in(plenv_source, expression_numeric_{letter}) = eps',
        f'$lossy_optional_integer_float_literal(expression_numeric_{letter}) = eps',
        f'$lossy_optional_integer_numeric(plenv_source, expression_numeric_{letter}) = (NFLOAT $hex_bits("{bits}", 0))',
        f'$lossy_optional_integer_condition(plenv_source, expression_numeric_{letter}) = (true)',
        f'$lossy_optional_integer_string_in(plenv_source, NExprCastString expression_numeric_{letter} metadata_a) = eps',
    ])
checks.extend([
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt expression_numeric_d metadata_a) = (0)',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt expression_numeric_e metadata_a) = (1)',
    '~$lossy_optional_integer_header(S, pfunction[.ENV = $plempty(false)], pfunction.SIGNATURE.PARAMETERS, 0)',
    'plenv_yes_false = plenv_source[.CONSTANTS = [($ptascii("YesReceive213"), $ptascii("false")), ($ptascii("NoReceive213"), $ptascii("false")), ($ptascii("NilReceive213"), $ptascii("null"))]]',
    '$lossy_optional_integer_default_in(plenv_yes_false, expression_a) = ($(-7))',
    '$lossy_optional_integer_default_in(plenv_yes_false, expression_b) = ($(-5))',
    '~$lossy_optional_integer_header(S, pfunction[.ENV = plenv_yes_false], pfunction.SIGNATURE.PARAMETERS, 0)',
    'plenv_no_true = plenv_source[.CONSTANTS = [($ptascii("YesReceive213"), $ptascii("true")), ($ptascii("NoReceive213"), $ptascii("true")), ($ptascii("NilReceive213"), $ptascii("null"))]]',
    '$lossy_optional_integer_default_in(plenv_no_true, expression_c) = eps',
    '~$lossy_optional_integer_header(S, pfunction[.ENV = plenv_no_true], pfunction.SIGNATURE.PARAMETERS, 0)',
    'expression_same = NExprUnaryMinus (NScalarInt (INTEGER 7) metadata_a) metadata_a',
    '~$lossy_optional_integer_tail(S, pfunction, [psparam_a[.DEFAULT = PSDEFAULT expression_same "int"]], 0)',
    'pfunction.DEFAULTS = [pdefault_a, pdefault_b, pdefault_c, pdefault_d, pdefault_e]',
    '~$lossy_optional_integer_tail(S, pfunction[.DEFAULTS = [pdefault_a, pdefault_b[.KIND = PDDEFERRED], pdefault_c, pdefault_d, pdefault_e]], [psparam_b], 1)',
    'S_wrong_value = S[.POOLS = [{UNIT n_unit, CONSTANTS ([(PCONSTANT (pcpath_c ++ [PCFIELD 6]) (PINT 1))])}]]',
    '~$lossy_optional_integer_tail(S_wrong_value, pfunction, [psparam_c], 2)',
])
true, false, null = map(constant, ('true', 'false', 'null'))
yes, no, nil = map(constant, ('YesReceive213', 'NoReceive213', 'NilReceive213'))
unknown = constant('UnselectedReceive213')
# Typed arithmetic preserves binary64 result bits before the explicit truncating cast.
for expression, bits, result in [
    (binary('Div', integer(5), integer(2)), '4004000000000000', '2'),
    (binary('Div', integer(-5), integer(2)), 'c004000000000000', '$(-2)'),
    (binary('Plus', floating('3ff8000000000000'), integer(1)), '4004000000000000', '2'),
    (binary('Minus', node('NExprUnaryMinus', floating('401c000000000000')), floating('3fe0000000000000')), 'c01e000000000000', '$(-7)'),
    (binary('Mul', floating('3ff8000000000000'), integer(2)), '4008000000000000', '3'),
    (binary('Div', floating('4018000000000000'), integer(3)), '4000000000000000', '2'),
    (binary('Plus', floating('8000000000000000'), floating('8000000000000000')), '8000000000000000', '0'),
    (binary('Mul', floating('0000000000000001'), floating('3fe0000000000000')), '0000000000000000', '0'),
    (binary('Minus', cast(string('-9223372036854775808')), integer(1)), 'c3e0000000000000', '$(-9223372036854775808)'),
]:
    checks.extend([
        f'$lossy_optional_integer_numeric(plenv_source, {expression}) = (NFLOAT $hex_bits("{bits}", 0))',
        f'$lossy_optional_integer_default_in(plenv_source, {expression}) = eps',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = ({result})',
        f'$lossy_optional_integer_condition(plenv_source, {expression}) = ({"false" if bits in ["0000000000000000", "8000000000000000"] else "true"})',
        f'$lossy_optional_integer_string_in(plenv_source, {string_cast(expression)}) = eps',
    ])
# Old literal FLOAT casts keep their exact branch and the same explicit-cast guards.
for bits, result in [('0000000000000000', '0'), ('8000000000000000', '0'), ('3fe0000000000000', '0'), ('bfe0000000000000', '0'), ('401f000000000000', '7'), ('c3e0000000000000', '$(-9223372036854775808)')]:
    expression = floating(bits)
    checks.extend([
        f'$lossy_optional_integer_float_literal({expression}) = ($hex_bits("{bits}", 0))',
        f'$lossy_optional_integer_numeric(plenv_source, {expression}) = (NFLOAT $hex_bits("{bits}", 0))',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = ({result})',
    ])
for expression, value in [(integer(7), '7'), (binary('Plus', integer(1), integer(2)), '3'), (binary('Div', integer(6), integer(3)), '2'), (cast(yes), '1')]:
    checks.extend([
        f'$lossy_optional_integer_numeric(plenv_source, {expression}) = (NINT {value})',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = ({value})',
    ])
# Bare scalar leaves, opaque operators, unknown syntax and invalid INT stay outside Numeric.
for expression in [true, false, null, yes, no, nil, string('1'), string('1tail'),
                   integer(9223372036854775808), node('NExprVariable', 'BYTES "eA=="'),
                   node('NExprArray', 'SEQUENCE eps'), unknown,
                   binary('Plus', yes, integer(1)), binary('Mul', string('2'), integer(3)),
                   binary('Mod', floating('3ff8000000000000'), integer(1)),
                   conditional(yes, floating('3fe0000000000000'), unknown)]:
    result = ('(NINT 2)' if expression.startswith('NExprBinaryOpPlus ')
              else '(NINT 6)' if expression.startswith('NExprBinaryOpMul ')
              else '(NFLOAT $hex_bits("3fe0000000000000", 0))' if expression.startswith('NExprTernary ') else 'eps')
    checks.append(f'$lossy_optional_integer_numeric(plenv_source, {expression}) = {result}')
for expression in [binary('Div', integer(1), integer(0)), binary('Div', floating('3ff0000000000000'), floating('8000000000000000'))]:
    checks.extend([
        f'$lossy_optional_integer_numeric(plenv_source, {expression}) = eps',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = eps',
    ])
# Computed infinity/NaN/nonfitting results remain typed numbers but never quiet stored casts.
for expression in [binary('Plus', integer(9223372036854775807), integer(1)),
                   binary('Div', cast(string('-9223372036854775808')), integer(-1)),
                   binary('Mul', floating('7fe1ccf385ebc8a0'), integer(2)),
                   binary('Minus', floating('7ff0000000000000'), floating('7ff0000000000000'))]:
    checks.extend([
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = eps',
        f'$lossy_optional_integer_string_in(plenv_source, {string_cast(expression)}) = eps',
    ])
# Composition uses the existing explicit CASTINT path, not a raw FLOAT truth/string shortcut.
fraction = binary('Div', integer(1), integer(2))
checks.extend([
    f'$lossy_optional_integer_condition(plenv_source, {cast(fraction)}) = (false)',
    f'$lossy_optional_integer_condition(plenv_source, {string_cast(cast(fraction))}) = (false)',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(conditional(yes, binary("Div", integer(5), integer(2)), unknown))}) = (2)',
    f'$lossy_optional_integer_string_in(plenv_source, {string_cast(cast(binary("Div", integer(5), integer(2))))}) = ([50])',
    f'$lossy_optional_integer_string_in(plenv_source, {dimension(string("09"), cast(fraction))}) = ([48])',
])
# The one promoted old196 helper input keeps its exact literal bits and operator.
old196 = cast(binary('Plus', floating('401f000000000000'), floating('0000000000000000')))
checks.append(f'$lossy_optional_integer_default_in(plenv_source, {old196}) = (7)')
deep = binary('Div', integer(1), integer(2))
for _ in range(8):
    deep = binary('Plus', deep, integer(0))
checks.extend([
    f'$lossy_optional_integer_numeric(plenv_source, {deep}) = (NFLOAT $hex_bits("3fe0000000000000", 0))',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(deep)}) = (0)',
])
# Every contrast remains genuinely deferred in this same source unit.
fixed_metadata = None
for suffix, function, pattern, projected in [
    ('floatnot', 'deferredFloatNotReceive213', cast(node('NExprBooleanNot', floating('3fe0000000000000'))), '(0)'),
    ('negative', 'deferredNegativeIndexReceive213', cast(dimension(string('10'), string('-1'))), 'eps'),
    ('floatindex', 'deferredFloatIndexReceive213', cast(dimension(string('10'), string('1.0'))), 'eps'),
    ('floatstring', 'deferredFloatStringReceive213', cast(string_cast(floating('3fe0000000000000'))), 'eps'),
    ('computednegative', 'deferredComputedNegativeIndexReceive213', cast(dimension(string('10'), binary('Minus', integer(0), integer(1)))), 'eps'),
    ('selectedfloat', 'deferredSelectedFloatStringReceive213', cast(string_cast(conditional(constant('YesReceive213'), floating('3fe0000000000000'), constant('UnselectedReceive213')))), 'eps'),
    ('nonfit', 'deferredComputedFloatNonfitReceive213', cast(binary('Mul', floating('7fe1ccf385ebc8a0'), integer(2))), 'eps'),
    ('zerodiv', 'deferredComputedFloatZeroDivReceive213', cast(binary('Div', floating('3ff0000000000000'), integer(0))), 'eps'),
    ('nan', 'deferredComputedFloatNanReceive213', cast(binary('Minus', binary('Mul', floating('7fe1ccf385ebc8a0'), integer(2)), binary('Mul', floating('7fe1ccf385ebc8a0'), integer(2)))), 'eps'),
]:
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
    '$lookup(psymboltable_global.ENV, $ptascii("xReceive213")) = (n_global)',
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
    '$lookup(S_done.ENV, $ptascii("gotReceive213")) = (n_got)',
    'S_done.STORE[n_got] = DEFINED (PINT 13)',
    r'$call_descriptors_valid(S_done) /\ $heap_valid($heap_graph(S_done))',
])

CASES = {'computed-float-integer-cast-default-omitted-tail': {
    'source': source,
    'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z]',
    'checks': checks,
}}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
