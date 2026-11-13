#!/usr/bin/env python3
"""Numeric-string DIM selectors preserve compiler bytes and reception authority."""
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


patterns = [
    node('NExprUnaryMinus', ternary(dimension(string('10'), string('01tail')), constant('UnselectedReceive208'), integer(7))),
    cast(ternary(dimension(string(b'\0x'), string(' +0tail')), string('-11tail'), constant('UnselectedReceive208'))),
    cast(ternary(float_cast(ternary(constant('true'),
                                  binary('Concat', dimension(string('x0'), string('+1')), string('.5tail')), constant('UnselectedReceive208'))),
                 binary('Concat', dimension(string('x1'), string(b'1\0tail')), string('3tail')), constant('UnselectedReceive208'))),
    ternary(float_cast(binary('Coalesce', constant('null'), dimension(string('-0'), string(' \t1 ')))),
            constant('UnselectedReceive208'), cast(string('-9223372036854775808tail'))),
    cast(ternary(constant('true'), binary('Concat', dimension(string('x9'), string('0001')), string('9' * 23)), constant('UnselectedReceive208'))),
]
contrasts = [
    ('floatnot', 'deferredFloatNotReceive208', cast(node('NExprBooleanNot', node('NScalarFloat', 'FLOAT "3fe0000000000000"'))), '(0)'),
    ('negative', 'deferredNegativeIndexReceive208', cast(dimension(string('10'), string('-1'))), 'eps'),
    ('floatindex', 'deferredFloatIndexReceive208', cast(dimension(string('10'), string('1.0'))), 'eps'),
]

CATALOGUE = Path(__file__).with_name('string_selector_default_reception_cases.json')
assert hashlib.sha256(CATALOGUE.read_bytes()).hexdigest() == '8f54e0a7f990775fa5f6dfbd1cde2e587c43f6b0112965cc95a2550fffd06253'
row = next(row for row in json.loads(CATALOGUE.read_text()) if row['id'] == 'string-selector-precision-modes')
assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
source = row['source']
handler = source[:source.index('function valueFirstReceive208(')]
reference = source[source.index('function referenceReceive208('):source.index("set_error_handler('warningReceive208');")]
setup = source[source.index("set_error_handler('warningReceive208');"):source.index('$gotReceive208 = valueFirstReceive208(')]
start = source.index('$gotReceive208 = referenceReceive208(')
end = source.index('$xReceive208 = 1.5;', start)
leading = handler + reference + setup + source[start:end]
assert hashlib.sha256(leading.encode()).hexdigest() == 'ddae843f78effc44d22a314c421132c10d9c7d178594761ed9e7a1faf5b38ed1'

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
unknown = constant('UnselectedReceive208')

# The new selector path returns one byte, including NUL and each UTF-8 byte.
for index, byte, truth, integer_value in [
    (0, 48, 'false', 0), (1, 57, 'true', 9), (2, 0, 'true', 0),
    (3, 195, 'true', 0), (4, 169, 'true', 0), (5, 255, 'true', 0),
]:
    expression = dimension(string(b'09\0\xc3\xa9\xff'), string(str(index)))
    checks.extend([
        f'$lossy_optional_integer_string({expression}) = ([{byte}])',
        f'$lossy_optional_integer_condition(plenv_source, {expression}) = ({truth})',
        f'$lossy_optional_integer_default_in(plenv_source, {expression}) = eps',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = ({integer_value})',
        f'$lossy_optional_integer_condition(plenv_source, {float_cast(expression)}) = ({str(integer_value != 0).lower()})',
    ])
# Compiler allow_errors=1 accepts integer prefixes without runtime offset warnings.
# 0x1 is decimal prefix zero; float spellings are not converted to integer indices.
for selector, expected, truth, integer_value in [
    (b'0', 48, 'false', 0), (b'00', 48, 'false', 0), (b'-0', 48, 'false', 0),
    (b'+0', 48, 'false', 0), (b' 0 ', 48, 'false', 0), (b'0x1', 48, 'false', 0),
    (b'1tail', 57, 'true', 9), (b'01tail', 57, 'true', 9),
    (b'\t+1junk', 57, 'true', 9), (b'1\0tail', 57, 'true', 9),
    (b' 1\t', 57, 'true', 9), (b'1_0', 57, 'true', 9),
]:
    expression = dimension(string('09'), string(selector))
    checks.extend([
        f'$lossy_optional_integer_string({expression}) = ([{expected}])',
        f'$lossy_optional_integer_condition(plenv_source, {expression}) = ({truth})',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = ({integer_value})',
    ])
# Each side independently admits its existing recursive byte certificate.
for base, selector, expected in [
    (binary('Concat', string('a'), string('9')), string('01tail'), 57),
    (node('NExprBitwiseNot', string(b'\xff\xcf')), string('1'), 48),
    (binary('BitwiseAnd', string(b'\xff0'), string(b'\0\xff')), string('+1'), 48),
    (binary('BitwiseOr', string('0'), string(b'\0x')), string('1tail'), 120),
    (binary('BitwiseXor', string(b'\0\xff'), string('0')), string('-0'), 48),
    (dimension(string('ab'), integer(1)), string('0'), 98),
    (string('09'), binary('Concat', string('+'), string('1tail')), 57),
    (string('09'), node('NExprBitwiseNot', string(b'\xcf')), 48),
    (string('09'), binary('BitwiseAnd', string('1tail'), string(b'\xff' * 5)), 57),
    (string('09'), binary('BitwiseOr', string('1tail'), string(b'\0')), 57),
    (string('09'), binary('BitwiseXor', string('0'), string(b'\0')), 48),
    (string('09'), dimension(string('x1'), integer(1)), 57),
    (string('09'), dimension(string('01'), string('1')), 57),
]:
    checks.append(f'$lossy_optional_integer_string({dimension(base, selector)}) = ([{expected}])')
zero = dimension(string('x0'), string('1tail'))
nul = dimension(string(b'\0x'), string('0'))
checks.extend([
    f'$lossy_optional_integer_condition(plenv_source, {ternary(zero, unknown, integer(7))}) = (true)',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(ternary(nul, string("-11tail"), unknown))}) = ($(-11))',
    f'$lossy_optional_integer_leaf_truth(plenv_source, {binary("Coalesce", nul, unknown)}) = (({nul}, true))',
    f'$lossy_optional_integer_condition(plenv_source, {float_cast(binary("Coalesce", nul, unknown))}) = (false)',
    f'$lossy_optional_integer_default_in(plenv_alias, {cast(ternary(constant("true", qualified=True), dimension(string("x9"), string("1")), unknown))}) = (9)',
])

# "bad" and "1.0" recheck the six affected old207 refusal assertions here.
# The newly admitted old inputs "0"/"1tail" are tested positively above.
bad_selectors = [
    b'bad', b'1.0', b'', b'+', b'-', b'\0', b'\0 1', b'\xc2\xa01',
    b'-1', b' -1tail', b'2', b'02tail', b'1.', b'.0', b'1e0', b'1.0tail',
    b'1e-1', b'9223372036854775807', b'9223372036854775808',
    b'-9223372036854775808', b'-9223372036854775809',
]
for selector in bad_selectors:
    expression = dimension(string('09'), string(selector))
    checks.extend([
        f'$lossy_optional_integer_string({expression}) = eps',
        f'$lossy_optional_integer_condition(plenv_source, {expression}) = eps',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = eps',
    ])
# Unknown/coerced/selected children cannot supply either byte certificate.
for selector in ['ABSENT', node('NScalarFloat', 'FLOAT "3ff0000000000000"'),
                 constant('true'), cast(string('1')), unknown,
                 ternary(constant('true'), string('1'), unknown),
                 node('NExprVariable', 'BYTES "aW5kZXg="')]:
    expression = dimension(string('09'), selector)
    checks.extend([
        f'$lossy_optional_integer_string({expression}) = eps',
        f'$lossy_optional_integer_condition(plenv_source, {expression}) = eps',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = eps',
    ])
for base in [string(''), integer(9), constant('null'), unknown,
             node('NExprCastString', integer(9)), ternary(constant('true'), string('9'), unknown),
             dimension(string('09'), string('-1'))]:
    checks.append(f'$lossy_optional_integer_string({dimension(base, string("0"))}) = eps')

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
    '$lookup(psymboltable_global.ENV, $ptascii("xReceive208")) = (n_cell)',
    '$lookup(psymboltable_global.ENV, $ptascii("countReceive208")) = (n_count)',
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
    '$lookup(S_done.ENV, $ptascii("gotReceive208")) = (n_got)',
    'S_done.STORE[n_got] = DEFINED (PINT 1)',
    r'$call_descriptors_valid(S_done) /\ $heap_valid($heap_graph(S_done))',
])

CASES = {'string-selector-reference-leading': {
    'source': leading,
    'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 2 n_cell n_bits i z]',
    'checks': checks,
}}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
