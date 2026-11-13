#!/usr/bin/env python3
"""Integer and byte identity string casts preserve defaults and borrowed cells."""
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


patterns = [
    node('NExprUnaryMinus', ternary(string_cast(string_cast(integer(0))), constant('UnselectedReceive209'), integer(7))),
    cast(ternary(string_cast(binary('Concat', string_cast(node('NExprUnaryPlus', integer(0))), string('.0'))),
                 string_cast(binary('Concat', string_cast(node('NExprUnaryMinus', integer(11))), string('tail'))), constant('UnselectedReceive209'))),
    cast(ternary(node('NExprCastDouble', ternary(constant('true'),
                                               binary('Concat', string_cast(node('NExprUnaryMinus', integer(0))), string('.5tail')), constant('UnselectedReceive209'))),
                 binary('Concat', string_cast(node('NExprUnaryPlus', integer(1))), string('3tail')), constant('UnselectedReceive209'))),
    ternary(node('NExprCastDouble', binary('Coalesce', constant('null'), string_cast(node('NExprUnaryMinus', integer(0))))),
            constant('UnselectedReceive209'), cast(string('-9223372036854775808tail'))),
    cast(ternary(constant('true'), binary('Concat', string_cast(string_cast(node('NExprUnaryPlus', integer(9)))), string('9' * 23)), constant('UnselectedReceive209'))),
]

contrasts = [
    ('floatnot', 'deferredFloatNotReceive209', cast(node('NExprBooleanNot', node('NScalarFloat', 'FLOAT "3fe0000000000000"'))), '(0)'),
    ('negative', 'deferredNegativeIndexReceive209', cast(dimension(string('10'), string('-1'))), 'eps'),
    ('floatindex', 'deferredFloatIndexReceive209', cast(dimension(string('10'), string('1.0'))), 'eps'),
    ('floatstring', 'deferredFloatStringReceive209', cast(string_cast(node('NScalarFloat', 'FLOAT "3fe0000000000000"'))), 'eps'),
]

CATALOGUE = Path(__file__).with_name('integer_string_cast_default_reception_cases.json')
assert hashlib.sha256(CATALOGUE.read_bytes()).hexdigest() == '59659fd51bcd2710c69a1517f01561bde442706895693ba68dee8ecc332606ba'
row = next(row for row in json.loads(CATALOGUE.read_text()) if row['id'] == 'integer-string-cast-precision-modes')
assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
source = row['source']
handler = source[:source.index('function valueFirstReceive209(')]
reference = source[source.index('function referenceReceive209('):source.index("set_error_handler('warningReceive209');")]
setup = source[source.index("set_error_handler('warningReceive209');"):source.index('$gotReceive209 = valueFirstReceive209(')]
start = source.index('$gotReceive209 = referenceReceive209(')
end = source.index('$xReceive209 = 1.5;', start)
leading = handler + reference + setup + source[start:end]
assert hashlib.sha256(leading.encode()).hexdigest() == '43879898ecff58ede6ed0a31c5af967fe677b00fc4633a389f56ccd31a8686dd'

checks = [
    r'n_bits = 4609434218613702656 /\ i = 1',
    '$function_at(S.FUNCTIONS, porigin) = (pfunction)',
    'plenv_source = pfunction.ENV',
    r'plenv_source.NAMESPACE = eps /\ plenv_source.CONSTANTS = eps',
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
    'plenv_alias = plenv_source[.CONSTANTS = [($ptascii("true"), $ptascii("false"))]]',
    '$lossy_optional_integer_default_in(plenv_alias, expression_c) = eps',
    '$lossy_optional_integer_default_in(plenv_alias, expression_e) = eps',
    '~$lossy_optional_integer_header(S, pfunction[.ENV = plenv_alias], pfunction.SIGNATURE.PARAMETERS, 0)',
    'plenv_null_alias = plenv_source[.CONSTANTS = [($ptascii("null"), $ptascii("true"))]]',
    '$lossy_optional_integer_default_in(plenv_null_alias, expression_d) = eps',
    '~$lossy_optional_integer_header(S, pfunction[.ENV = plenv_null_alias], pfunction.SIGNATURE.PARAMETERS, 0)',
    'expression_a = NExprUnaryMinus expression_select_a metadata_a',
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
unknown = constant('UnselectedReceive209')

# Integer formatting covers the signed range without float or ENV conversion.
for value, expected in [(0, '0'), (1, '1'), (-1, '-1'), (100, '100'),
                        (9223372036854775807, '9223372036854775807'),
                        (-9223372036854775808, '-9223372036854775808')]:
    expression = string_cast(integer(value))
    literal = str(value) if value >= 0 else f'$({value})'
    checks.extend([
        f'$lossy_optional_integer_string({expression}) = ($ptascii("{expected}"))',
        f'$lossy_optional_integer_condition(plenv_source, {expression}) = ({str(value != 0).lower()})',
        f'$lossy_optional_integer_default_in(plenv_source, {expression}) = eps',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = ({literal})',
        f'$lossy_optional_integer_condition(plenv_source, {float_cast(expression)}) = ({str(value != 0).lower()})',
    ])
for child, expected in [(node('NExprUnaryPlus', integer(0)), '0'),
                        (node('NExprUnaryMinus', integer(0)), '0'),
                        (node('NExprUnaryPlus', integer(9)), '9'),
                        (node('NExprUnaryMinus', integer(11)), '-11'),
                        (node('NExprUnaryMinus', node('NExprUnaryMinus', integer(1))), '1')]:
    checks.append(f'$lossy_optional_integer_string({string_cast(child)}) = ($ptascii("{expected}"))')
# Identity preserves arbitrary bytes, including empty, NUL and UTF-8 payloads.
for data, truth, result in [(b'', 'false', '0'), (b'0', 'false', '0'),
                            (b'0.0', 'true', '0'), (b'\0', 'true', '0'),
                            (b'\xc3\xa9', 'true', '0'), (b'\xff', 'true', '0'),
                            (b'-11tail', 'true', '$(-11)')]:
    expression = string_cast(string(data))
    expected = '[' + ', '.join(map(str, data)) + ']' if data else 'eps'
    checks.extend([
        f'$lossy_optional_integer_string({expression}) = ({expected})',
        f'$lossy_optional_integer_condition(plenv_source, {expression}) = ({truth})',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = ({result})',
    ])
for child, expected in [
    (binary('Concat', string('0'), string('.0')), [48,46,48]),
    (node('NExprBitwiseNot', string(b'\xcf')), [48]),
    (binary('BitwiseAnd', string('0'), string(b'\xff')), [48]),
    (binary('BitwiseOr', string('0'), string(b'\0x')), [48,120]),
    (binary('BitwiseXor', string('0'), string(b'\0')), [48]),
    (dimension(string('x0'), integer(1)), [48]),
    (dimension(string('x0'), string('1tail')), [48]),
    (string_cast(node('NExprUnaryPlus', integer(9))), [57]),
]:
    data = '[' + ', '.join(map(str, expected)) + ']'
    checks.append(f'$lossy_optional_integer_string({string_cast(child)}) = ({data})')
zero = string_cast(string_cast(integer(0)))
fraction_zero = string_cast(binary('Concat', string_cast(integer(0)), string('.0')))
checks.extend([
    f'$lossy_optional_integer_condition(plenv_source, {zero}) = (false)',
    f'$lossy_optional_integer_condition(plenv_source, {fraction_zero}) = (true)',
    f'$lossy_optional_integer_condition(plenv_source, {float_cast(fraction_zero)}) = (false)',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(ternary(fraction_zero, string_cast(integer(-11)), unknown))}) = ($(-11))',
    f'$lossy_optional_integer_string({dimension(string_cast(integer(10)), string_cast(integer(1)))}) = ([48])',
    f'$lossy_optional_integer_default_in(plenv_alias, {cast(ternary(constant("true", qualified=True), string_cast(integer(9)), unknown))}) = (9)',
])
# Bool/null require declaration ENV; float string casts stay precision-deferred.
for child, byte_result, truth, integer_result in [
    (unknown, None, None, None),
    (constant('true'), '[49]', 'true', '1'),
    (constant('false'), 'eps', 'false', '0'),
    (constant('null'), 'eps', 'false', '0'),
    (constant('true', qualified=True), '[49]', 'true', '1'),
    (node('NScalarFloat', 'FLOAT "0000000000000000"'), None, None, None),
    (node('NScalarFloat', 'FLOAT "3fe0000000000000"'), None, None, None),
    (node('NScalarFloat', 'FLOAT "7ff8000000000000"'), None, None, None),
    (integer(9223372036854775808), None, None, None),
    (integer(-9223372036854775809), None, None, None),
    (node('NExprUnaryMinus', integer(-9223372036854775808)), None, None, None),
    (cast(string('1')), '[49]', 'true', '1'),
    (binary('Plus', integer(0), integer(1)), '[49]', 'true', '1'),
    (ternary(constant('true'), string('1'), unknown), None, None, None),
    (node('NExprVariable', 'BYTES "aW5kZXg="'), None, None, None),
    (node('NExprArray', 'SEQUENCE eps'), None, None, None),
]:
    expression = string_cast(child)
    projected = 'eps' if byte_result is None else f'({byte_result})'
    condition = 'eps' if truth is None else f'({truth})'
    converted = 'eps' if integer_result is None else f'({integer_result})'
    checks.extend([
        f'$lossy_optional_integer_string({expression}) = {projected}',
        f'$lossy_optional_integer_condition(plenv_source, {expression}) = {condition}',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = {converted}',
    ])
# Corrected old CONCAT204 author/peer inputs give the same eight formulas.
# Recheck them once here, together with the other 23 affected peer formulas.
old_concat = string_cast(constant('UnselectedReceive204'))
for expression in [binary('Concat', string(''), old_concat), binary('Concat', old_concat, string(''))]:
    checks.extend([
        f'$lossy_optional_integer_string({expression}) = eps',
        f'$lossy_optional_integer_condition(plenv_source, {expression}) = eps',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = eps',
        f'$lossy_optional_integer_condition(plenv_source, {float_cast(expression)}) = eps',
    ])
old_not = node('NExprBitwiseNot', string_cast(constant('UnselectedReceive205')))
checks.extend([
    f'$lossy_optional_integer_string({old_not}) = eps',
    f'$lossy_optional_integer_condition(plenv_source, {old_not}) = eps',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(old_not)}) = eps',
])
old_bitwise = string_cast(constant('UnselectedReceive206'))
for kind in ('BitwiseAnd', 'BitwiseOr', 'BitwiseXor'):
    for first, second in [(string(''), old_bitwise), (old_bitwise, string(''))]:
        expression = binary(kind, first, second)
        checks.extend([
            f'$lossy_optional_integer_string({expression}) = eps',
            f'$lossy_optional_integer_condition(plenv_source, {expression}) = eps',
            f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = eps',
        ])
checks.extend([
    f'$lossy_optional_integer_string({dimension(string_cast(constant("UnselectedReceive207")), integer(0))}) = eps',
    f'$lossy_optional_integer_string({dimension(string_cast(constant("UnselectedReceive208")), string("0"))}) = eps',
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
    '$lookup(psymboltable_global.ENV, $ptascii("xReceive209")) = (n_cell)',
    '$lookup(psymboltable_global.ENV, $ptascii("countReceive209")) = (n_count)',
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
    '$lookup(S_done.ENV, $ptascii("gotReceive209")) = (n_got)',
    'S_done.STORE[n_got] = DEFINED (PINT 1)',
    r'$call_descriptors_valid(S_done) /\ $heap_valid($heap_graph(S_done))',
])

CASES = {'integer-string-cast-reference-leading': {
    'source': leading,
    'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 2 n_cell n_bits i z]',
    'checks': checks,
}}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
