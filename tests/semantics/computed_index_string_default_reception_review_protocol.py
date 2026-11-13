#!/usr/bin/env python3
"""Computed integer DIM selectors preserve declaration authority and receive ownership."""
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
    node('NExprUnaryMinus', ternary(dimension(string('10'), cast(string_cast(constant('YesReceive211')))), constant('UnselectedReceive211'), integer(7))),
    cast(ternary(binary('Concat', dimension(string('10'), binary('Plus', integer(1), integer(0))), string('.0')),
                 string_cast(binary('Concat', binary('Concat', string_cast(binary('Minus', node('NExprUnaryMinus', integer(10)), integer(1))), string_cast(constant('false', qualified=True))), string('tail'))), constant('UnselectedReceive211'))),
    cast(ternary(float_cast(ternary(constant('true'),
                                   binary('Concat', dimension(string('10'), ternary(constant('NoReceive211'), constant('UnselectedReceive211'), binary('Plus', integer(0), integer(1)))), string('.5tail')), constant('UnselectedReceive211'))),
                 binary('Concat', dimension(string('01'), binary('Div', integer(2), integer(2))), string('3tail')), constant('UnselectedReceive211'))),
    ternary(float_cast(binary('Coalesce', constant('null'), binary('Concat', dimension(string('10'), binary('Coalesce', constant('NilReceive211'), binary('Minus', integer(2), integer(1)))), string('.0')))),
            constant('UnselectedReceive211'), cast(string('-9223372036854775808tail'))),
    cast(ternary(constant('true'), binary('Concat', dimension(string('09'), ternary(constant('YesReceive211'), binary('Mod', integer(3), integer(2)), constant('UnselectedReceive211'))), string('9' * 23)), constant('UnselectedReceive211'))),
]

contrasts = [
    ('floatnot', 'deferredFloatNotReceive211', cast(node('NExprBooleanNot', node('NScalarFloat', 'FLOAT "3fe0000000000000"'))), '(0)'),
    ('negative', 'deferredNegativeIndexReceive211', cast(dimension(string('10'), string('-1'))), 'eps'),
    ('floatindex', 'deferredFloatIndexReceive211', cast(dimension(string('10'), string('1.0'))), 'eps'),
    ('floatstring', 'deferredFloatStringReceive211', cast(string_cast(node('NScalarFloat', 'FLOAT "3fe0000000000000"'))), 'eps'),
    ('computednegative', 'deferredComputedNegativeIndexReceive211', cast(dimension(string('10'), binary('Minus', integer(0), integer(1)))), 'eps'),
]

CATALOGUE = Path(__file__).with_name('computed_index_string_default_reception_cases.json')
assert hashlib.sha256(CATALOGUE.read_bytes()).hexdigest() == 'e0d741f7b00598cf15d1845e3082809a94f3f8d6a69ef7752faa325842ebc024'
row = next(row for row in json.loads(CATALOGUE.read_text()) if row['id'] == 'computed-index-string-precision-modes')
assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
source = row['source']
handler = source[:source.index('function valueFirstReceive211(')]
reference = source[source.index('function referenceReceive211('):source.index("set_error_handler('warningReceive211');")]
setup = source[source.index("set_error_handler('warningReceive211');"):source.index('$gotReceive211 = valueFirstReceive211(')]
start = source.index('$gotReceive211 = referenceReceive211(')
end = source.index('$xReceive211 = 1.5;', start)
leading = handler + reference + setup + source[start:end]
assert hashlib.sha256(leading.encode()).hexdigest() == 'bf17933afc9aa84d75ba877384a1a7a542c5bd26b4c07dad00d598c9dfc849b5'

checks = [
    r'n_bits = 4609434218613702656 /\ i = 1',
    '$function_at(S.FUNCTIONS, porigin) = (pfunction)',
    'plenv_source = pfunction.ENV',
    r'plenv_source.NAMESPACE = eps /\ plenv_source.CONSTANTS = [($ptascii("YesReceive211"), $ptascii("true")), ($ptascii("NoReceive211"), $ptascii("false")), ($ptascii("NilReceive211"), $ptascii("null"))]',
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
    'plenv_alias = plenv_source[.CONSTANTS = [($ptascii("YesReceive211"), $ptascii("false")), ($ptascii("NoReceive211"), $ptascii("false")), ($ptascii("NilReceive211"), $ptascii("null"))]]',
    '$lossy_optional_integer_default_in(plenv_alias, expression_a) = eps',
    '$lossy_optional_integer_default_in(plenv_alias, expression_e) = eps',
    '~$lossy_optional_integer_header(S, pfunction[.ENV = plenv_alias], pfunction.SIGNATURE.PARAMETERS, 0)',
    'plenv_null_alias = plenv_source[.CONSTANTS = [($ptascii("YesReceive211"), $ptascii("true")), ($ptascii("NoReceive211"), $ptascii("false")), ($ptascii("NilReceive211"), $ptascii("true"))]]',
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
unknown = constant('UnselectedReceive211')
yes, no, nil = map(constant, ('YesReceive211', 'NoReceive211', 'NilReceive211'))

# The source key is already a genuine integer; only the old DIM recognizer refused it.
checks.extend([
    'expression_a = NExprUnaryMinus expression_select_a metadata_a',
    'expression_select_a = NExprTernary expression_dim_a expression_unused_a expression_seven_a metadata_select_a',
    'expression_dim_a = NExprArrayDimFetch expression_base_a expression_key_a metadata_dim_a',
    '$psnumber(expression_key_a) = PSNONNUMERIC',
    '$lossy_optional_integer_default_in(plenv_source, expression_key_a) = (1)',
    '$lossy_optional_integer_default_in($plempty(false), expression_key_a) = eps',
    '$lossy_optional_integer_string_in(plenv_source, expression_dim_a) = ([48])',
    '$lossy_optional_integer_string(expression_dim_a) = eps',
    'expression_d = NExprTernary expression_float_d expression_unused_d expression_minimum_d metadata_d',
    'expression_float_d = NExprCastDouble expression_coalesce_d metadata_float_d',
    'expression_coalesce_d = NExprBinaryOpCoalesce expression_null_d expression_zero_d metadata_coalesce_d',
    '$lossy_optional_integer_leaf_truth(plenv_source, expression_coalesce_d) = ((expression_zero_d, true))',
    '$lossy_optional_integer_string_in(plenv_source, expression_zero_d) = ($ptascii("0.0"))',
    '$lossy_optional_integer_float_truth_in(plenv_source, expression_zero_d, true) = false',
    '$lossy_optional_integer_condition(plenv_source, expression_float_d) = (false)',
    'plenv_no_alias = plenv_source[.CONSTANTS = [($ptascii("YesReceive211"), $ptascii("true")), ($ptascii("NoReceive211"), $ptascii("true")), ($ptascii("NilReceive211"), $ptascii("null"))]]',
    '$lossy_optional_integer_default_in(plenv_no_alias, expression_c) = eps',
    '~$lossy_optional_integer_header(S, pfunction[.ENV = plenv_no_alias], pfunction.SIGNATURE.PARAMETERS, 0)',
    'plenv_fqn_alias = plenv_source[.CONSTANTS = plenv_source.CONSTANTS ++ [($ptascii("false"), $ptascii("true"))]]',
    '$lossy_optional_integer_default_in(plenv_fqn_alias, expression_b) = ($(-11))',
])

# Arithmetic, comparison results, explicit casts and selected INT values stay typed.
for key, value in [
    (binary('Plus', integer(0), integer(1)), 1),
    (binary('Minus', integer(2), integer(1)), 1),
    (binary('Mul', integer(1), integer(1)), 1),
    (binary('Pow', integer(2), integer(0)), 1),
    (binary('Div', integer(2), integer(2)), 1),
    (binary('Mod', integer(3), integer(2)), 1),
    (binary('ShiftLeft', integer(1), integer(0)), 1),
    (binary('ShiftRight', integer(2), integer(1)), 1),
    (binary('BitwiseAnd', integer(3), integer(1)), 1),
    (binary('BitwiseOr', integer(0), integer(1)), 1),
    (binary('BitwiseXor', integer(3), integer(2)), 1),
    (binary('Spaceship', integer(2), integer(1)), 1),
    (cast(string('1tail')), 1),
    (cast(no), 0),
    (cast(node('NScalarFloat', 'FLOAT "3fe0000000000000"')), 0),
    (cast(node('NExprBooleanNot', no)), 1),
    (ternary(yes, integer(1), unknown), 1),
    (binary('Coalesce', nil, binary('Minus', integer(2), integer(1))), 1),
    (cast(ternary(yes, string('1tail'), unknown)), 1),
    (binary('Plus', integer(0), integer(0)), 0),
]:
    expression = dimension(string('09'), key)
    truth = 'true' if value else 'false'
    byte, result = (57, 9) if value else (48, 0)
    checks.extend([
        f'$psnumber({key}) = PSNONNUMERIC',
        f'$lossy_optional_integer_default_in(plenv_source, {key}) = ({value})',
        f'$lossy_optional_integer_string_in(plenv_source, {expression}) = ([{byte}])',
        f'$lossy_optional_integer_condition(plenv_source, {expression}) = ({truth})',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = ({result})',
        f'$lossy_optional_integer_default_in(plenv_source, {expression}) = eps',
    ])

# Nested computed DIM can itself supply a typed integer index after an explicit cast.
key = binary('Plus', integer(0), integer(1))
for _ in range(8):
    key = cast(dimension(string('x1'), key))
checks.extend([
    f'$lossy_optional_integer_default_in(plenv_source, {key}) = (1)',
    f'$lossy_optional_integer_string_in(plenv_source, {dimension(string("09"), key)}) = ([57])',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(dimension(string("09"), key))}) = (9)',
])

# All certified byte producers preserve empty, NUL, high bytes and byte offsets.
for base, key, expected in [
    (binary('Concat', string('x'), string('9')), binary('Plus', integer(0), integer(1)), 57),
    (node('NExprBitwiseNot', string(b'\xff\xcf')), cast(no), 0),
    (binary('BitwiseAnd', string(b'\xff0'), string(b'\0\xff')), binary('Minus', integer(2), integer(1)), 48),
    (binary('BitwiseOr', string('0'), string(b'\0x')), binary('Mod', integer(3), integer(2)), 120),
    (binary('BitwiseXor', string(b'\0\xff'), string('0')), cast(no), 48),
    (string_cast(binary('Plus', integer(10), integer(9))), binary('Div', integer(2), integer(2)), 57),
    (dimension(string('x9'), binary('Plus', integer(0), integer(1))), cast(no), 57),
    (string(b'0\0\xc3\xa9\xff'), binary('Plus', integer(1), integer(1)), 195),
    (string(b'0\0\xc3\xa9\xff'), binary('Plus', integer(2), integer(1)), 169),
    (string(b'0\0\xc3\xa9\xff'), binary('Plus', integer(3), integer(1)), 255),
]:
    checks.append(f'$lossy_optional_integer_string_in(plenv_source, {dimension(base, key)}) = ([{expected}])')

# Literal and numeric-string keys retain their original independent certificate arm.
for key in [integer(1), string('01tail'), string('+1'), string(b'1\0tail'), string(' 1 ')]:
    checks.append(f'$lossy_optional_integer_string_in(plenv_source, {dimension(string("09"), key)}) = ([57])')

# These key kinds, exceptional computations and invalid bounds never gain bytes.
for key in [
    'ABSENT', yes, no, nil, unknown,
    node('NScalarFloat', 'FLOAT "3ff0000000000000"'),
    node('NScalarFloat', 'FLOAT "7ff8000000000000"'),
    node('NExprCastDouble', integer(1)),
    node('NExprBooleanNot', no),
    binary('Div', integer(5), integer(2)),
    binary('Div', integer(0), integer(0)),
    binary('Plus', integer(9223372036854775807), integer(1)),
    node('NExprUnaryMinus', integer(-9223372036854775808)),
    integer(9223372036854775808),
    binary('Minus', integer(0), integer(1)),
    binary('Plus', integer(1), integer(1)),
    ternary(yes, node('NScalarFloat', 'FLOAT "3ff0000000000000"'), unknown),
    ternary(yes, string('1'), unknown),
    cast(node('NScalarFloat', 'FLOAT "7ff8000000000000"')),
    string('-1'), string('1.0'), string('1e0'), string('bad'), string(''),
    node('NExprVariable', 'BYTES "aW5kZXg="'), node('NExprArray', 'SEQUENCE eps'),
]:
    expression = dimension(string('09'), key)
    checks.extend([
        f'$lossy_optional_integer_string_in(plenv_source, {expression}) = eps',
        f'$lossy_optional_integer_condition(plenv_source, {expression}) = eps',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = eps',
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
    '$lookup(psymboltable_global.ENV, $ptascii("xReceive211")) = (n_cell)',
    '$lookup(psymboltable_global.ENV, $ptascii("countReceive211")) = (n_count)',
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
    '$lookup(S_done.ENV, $ptascii("gotReceive211")) = (n_got)',
    'S_done.STORE[n_got] = DEFINED (PINT 1)',
    r'$call_descriptors_valid(S_done) /\ $heap_valid($heap_graph(S_done))',
])

CASES = {'computed-index-string-reference-leading': {
    'source': leading,
    'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 2 n_cell n_bits i z]',
    'checks': checks,
}}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
