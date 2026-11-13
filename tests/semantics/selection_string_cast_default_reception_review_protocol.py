#!/usr/bin/env python3
"""Selected scalar CASTSTRING values preserve type, source authority and receive ownership."""
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
    node('NExprUnaryMinus', ternary(string_cast(ternary(constant('YesReceive212'), binary('Coalesce', constant('NoReceive212'), constant('UnselectedReceive212')), constant('UnselectedReceive212'))), constant('UnselectedReceive212'), integer(7))),
    cast(ternary(string_cast(ternary(constant('YesReceive212'), string('0.0'), constant('UnselectedReceive212'))),
                 string_cast(ternary(constant('NoReceive212'), constant('UnselectedReceive212'), binary('Concat', binary('Concat', string_cast(binary('Minus', node('NExprUnaryMinus', integer(10)), integer(1))), string_cast(constant('false', qualified=True))), string('tail')))), constant('UnselectedReceive212'))),
    cast(ternary(float_cast(ternary(constant('true'),
                                   string_cast(binary('Coalesce', constant('NilReceive212'), ternary(constant('NoReceive212'), 'ABSENT', string('.5tail')))), constant('UnselectedReceive212'))),
                 binary('Concat', string_cast(ternary(constant('NoReceive212'), constant('UnselectedReceive212'), constant('YesReceive212'))), string('3tail')), constant('UnselectedReceive212'))),
    ternary(float_cast(binary('Coalesce', constant('null'), string_cast(ternary(binary('Concat', string_cast(ternary(constant('YesReceive212'), constant('NilReceive212'), constant('UnselectedReceive212'))), string('0.0')), 'ABSENT', constant('UnselectedReceive212'))))),
            constant('UnselectedReceive212'), cast(string('-9223372036854775808tail'))),
    cast(string_cast(ternary(constant('YesReceive212'), ternary(constant('NoReceive212'), 'ABSENT', string('9' * 24)), constant('UnselectedReceive212')))),
]

contrasts = [
    ('floatnot', 'deferredFloatNotReceive212', cast(node('NExprBooleanNot', node('NScalarFloat', 'FLOAT "3fe0000000000000"'))), '(0)'),
    ('negative', 'deferredNegativeIndexReceive212', cast(dimension(string('10'), string('-1'))), 'eps'),
    ('floatindex', 'deferredFloatIndexReceive212', cast(dimension(string('10'), string('1.0'))), 'eps'),
    ('floatstring', 'deferredFloatStringReceive212', cast(string_cast(node('NScalarFloat', 'FLOAT "3fe0000000000000"'))), 'eps'),
    ('computednegative', 'deferredComputedNegativeIndexReceive212', cast(dimension(string('10'), binary('Minus', integer(0), integer(1)))), 'eps'),
    ('selectedfloat', 'deferredSelectedFloatStringReceive212', cast(string_cast(ternary(constant('YesReceive212'), node('NScalarFloat', 'FLOAT "3fe0000000000000"'), constant('UnselectedReceive212')))), 'eps'),
]

CATALOGUE = Path(__file__).with_name('selection_string_cast_default_reception_cases.json')
assert hashlib.sha256(CATALOGUE.read_bytes()).hexdigest() == 'fd9f39d6baf989b40c14c5c0ba5c9a0f99b978a7cb3d9e4f1d09cad3eef8b1b1'
row = next(row for row in json.loads(CATALOGUE.read_text()) if row['id'] == 'selection-string-cast-precision-modes')
assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
source = row['source']
handler = source[:source.index('function valueFirstReceive212(')]
reference = source[source.index('function referenceReceive212('):source.index("set_error_handler('warningReceive212');")]
setup = source[source.index("set_error_handler('warningReceive212');"):source.index('$gotReceive212 = valueFirstReceive212(')]
start = source.index('$gotReceive212 = referenceReceive212(')
end = source.index('$xReceive212 = 1.5;', start)
leading = handler + reference + setup + source[start:end]
assert hashlib.sha256(leading.encode()).hexdigest() == 'cac709646d79001e40b9da4759042c65875a495a53302b22381d4e6cda30bb6f'

checks = [
    r'n_bits = 4609434218613702656 /\ i = 1',
    '$function_at(S.FUNCTIONS, porigin) = (pfunction)',
    'plenv_source = pfunction.ENV',
    r'plenv_source.NAMESPACE = eps /\ plenv_source.CONSTANTS = [($ptascii("YesReceive212"), $ptascii("true")), ($ptascii("NoReceive212"), $ptascii("false")), ($ptascii("NilReceive212"), $ptascii("null"))]',
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
    'plenv_alias = plenv_source[.CONSTANTS = [($ptascii("YesReceive212"), $ptascii("false")), ($ptascii("NoReceive212"), $ptascii("false")), ($ptascii("NilReceive212"), $ptascii("null"))]]',
    '$lossy_optional_integer_default_in(plenv_alias, expression_a) = eps',
    '$lossy_optional_integer_default_in(plenv_alias, expression_e) = eps',
    '~$lossy_optional_integer_header(S, pfunction[.ENV = plenv_alias], pfunction.SIGNATURE.PARAMETERS, 0)',
    'plenv_null_alias = plenv_source[.CONSTANTS = [($ptascii("YesReceive212"), $ptascii("true")), ($ptascii("NoReceive212"), $ptascii("false")), ($ptascii("NilReceive212"), $ptascii("true"))]]',
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
unknown = constant('UnselectedReceive212')
yes, no, nil = map(constant, ('YesReceive212', 'NoReceive212', 'NilReceive212'))

# The existing selector chooses the false, non-null source leaf without stringifying it.
checks.extend([
    'expression_a = NExprUnaryMinus expression_select_a metadata_a',
    'expression_select_a = NExprTernary expression_string_a expression_unused_a expression_seven_a metadata_select_a',
    'expression_string_a = NExprCastString expression_child_a metadata_string_a',
    'expression_child_a = NExprTernary expression_yes_a expression_coalesce_a expression_unknown_a metadata_child_a',
    'expression_coalesce_a = NExprBinaryOpCoalesce expression_no_a expression_unknown_coalesce_a metadata_coalesce_a',
    '$lossy_optional_integer_selection_shape(expression_child_a)',
    '$lossy_optional_integer_default_in(plenv_source, expression_child_a) = eps',
    '$lossy_optional_integer_cast_leaf(plenv_source, expression_child_a) = (expression_no_a)',
    '$lossy_optional_integer_special(plenv_source, expression_no_a) = (PBOOL false)',
    '$lossy_optional_integer_string_in(plenv_source, expression_child_a) = eps',
    '$lossy_optional_integer_string_in(plenv_source, expression_string_a) = (eps)',
    '$lossy_optional_integer_string(expression_string_a) = eps',
    'expression_d = NExprTernary expression_float_d expression_unused_d expression_minimum_d metadata_d',
    '$lossy_optional_integer_condition(plenv_source, expression_float_d) = (false)',
    'plenv_no_alias = plenv_source[.CONSTANTS = [($ptascii("YesReceive212"), $ptascii("true")), ($ptascii("NoReceive212"), $ptascii("true")), ($ptascii("NilReceive212"), $ptascii("null"))]]',
    '$lossy_optional_integer_default_in(plenv_no_alias, expression_a) = eps',
    '$lossy_optional_integer_default_in(plenv_no_alias, expression_c) = eps',
    '~$lossy_optional_integer_header(S, pfunction[.ENV = plenv_no_alias], pfunction.SIGNATURE.PARAMETERS, 0)',
    'plenv_fqn_alias = plenv_source[.CONSTANTS = plenv_source.CONSTANTS ++ [($ptascii("false"), $ptascii("true"))]]',
    '$lossy_optional_integer_default_in(plenv_fqn_alias, expression_b) = ($(-11))',
])

# Selected non-INT scalars retain their own type and exact bytes.
for leaf, data, truth, numeric_truth, value in [
    (no, b'', 'false', 'false', '0'),
    (yes, b'1', 'true', 'true', '1'),
    (nil, b'', 'false', 'false', '0'),
    (string(''), b'', 'false', 'false', '0'),
    (string('0'), b'0', 'false', 'false', '0'),
    (string('0.0'), b'0.0', 'true', 'false', '0'),
    (string('01'), b'01', 'true', 'true', '1'),
    (string(b'\0'), b'\0', 'true', 'false', '0'),
    (string(b'\xff'), b'\xff', 'true', 'false', '0'),
    (string('13tail'), b'13tail', 'true', 'true', '13'),
    (string('9' * 24), b'9' * 24, 'true', 'true', '9223372036854775807'),
    (node('NExprBooleanNot', no), b'1', 'true', 'true', '1'),
    (node('NExprCastBool', string('0')), b'', 'false', 'false', '0'),
    (binary('Identical', integer(1), integer(1)), b'1', 'true', 'true', '1'),
    (binary('Concat', string('1'), string('3tail')), b'13tail', 'true', 'true', '13'),
    (node('NExprBitwiseNot', string(b'\xff')), b'\0', 'true', 'false', '0'),
    (dimension(string('09'), binary('Plus', integer(0), integer(1))), b'9', 'true', 'true', '9'),
]:
    selected = ternary(yes, leaf, unknown)
    expression = string_cast(selected)
    expected = '[' + ', '.join(map(str, data)) + ']' if data else 'eps'
    checks.extend([
        f'$lossy_optional_integer_selection_shape({selected})',
        f'$lossy_optional_integer_default_in(plenv_source, {selected}) = eps',
        f'$lossy_optional_integer_cast_leaf(plenv_source, {selected}) = ({leaf})',
        f'$lossy_optional_integer_string_in(plenv_source, {selected}) = eps',
        f'$lossy_optional_integer_string_in(plenv_source, {expression}) = ({expected})',
        f'$lossy_optional_integer_condition(plenv_source, {expression}) = ({truth})',
        f'$lossy_optional_integer_condition(plenv_source, {float_cast(expression)}) = ({numeric_truth})',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = ({value})',
        f'$lossy_optional_integer_default_in(plenv_source, {expression}) = eps',
    ])

# Existing selected INT formatting stays disjoint from the new non-INT cast case.
for leaf, value, data in [
    (integer(0), '0', b'0'), (integer(1), '1', b'1'),
    (node('NExprUnaryMinus', integer(11)), '$(-11)', b'-11'),
    (binary('Plus', integer(1), integer(2)), '3', b'3'),
    (cast(string('01')), '1', b'1'),
]:
    selected = ternary(yes, leaf, unknown)
    expected = '[' + ', '.join(map(str, data)) + ']'
    checks.extend([
        f'$lossy_optional_integer_default_in(plenv_source, {selected}) = ({value})',
        f'$lossy_optional_integer_string_in(plenv_source, {selected}) = eps',
        f'$lossy_optional_integer_string_in(plenv_source, {string_cast(selected)}) = ({expected})',
    ])

# Shorthand truth keeps the selected expression; coalesce distinguishes false/null.
zero, decimal_zero = string('0'), string('0.0')
right = string('1tail')
for selected, leaf, data, truth, value in [
    (ternary(zero, 'ABSENT', right), right, b'1tail', 'true', '1'),
    (ternary(decimal_zero, 'ABSENT', unknown), decimal_zero, b'0.0', 'true', '0'),
    (ternary(no, 'ABSENT', right), right, b'1tail', 'true', '1'),
    (ternary(yes, 'ABSENT', unknown), yes, b'1', 'true', '1'),
    (binary('Coalesce', no, unknown), no, b'', 'false', '0'),
    (binary('Coalesce', nil, decimal_zero), decimal_zero, b'0.0', 'true', '0'),
    (binary('Coalesce', ternary(yes, nil, unknown), ternary(no, 'ABSENT', right)), right, b'1tail', 'true', '1'),
]:
    expression = string_cast(selected)
    expected = '[' + ', '.join(map(str, data)) + ']' if data else 'eps'
    checks.extend([
        f'$lossy_optional_integer_default_in(plenv_source, {selected}) = eps',
        f'$lossy_optional_integer_cast_leaf(plenv_source, {selected}) = ({leaf})',
        f'$lossy_optional_integer_string_in(plenv_source, {selected}) = eps',
        f'$lossy_optional_integer_string_in(plenv_source, {expression}) = ({expected})',
        f'$lossy_optional_integer_condition(plenv_source, {expression}) = ({truth})',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = ({value})',
    ])

# Nested selected casts compose through existing byte identity without a depth cutoff.
deep = string('01')
for _ in range(8):
    deep = string_cast(ternary(yes, deep, unknown))
checks.extend([
    f'$lossy_optional_integer_string_in(plenv_source, {deep}) = ([48, 49])',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(deep)}) = (1)',
])

# Both promoted old peer inputs keep their original global-true and unknown names.
for suffix in ['209', '210']:
    expression = string_cast(ternary(constant('true'), string('1'), constant('UnselectedReceive' + suffix)))
    checks.extend([
        f'$lossy_optional_integer_string({expression}) = ([49])',
        f'$lossy_optional_integer_condition($plempty(false), {expression}) = (true)',
        f'$lossy_optional_integer_default_in($plempty(false), {cast(expression)}) = (1)',
    ])

# The old raw selected-STRING DIM key still refuses; an explicit CASTSTRING is typed.
raw_key = ternary(yes, string('1'), unknown)
checks.extend([
    f'$lossy_optional_integer_string_in(plenv_source, {raw_key}) = eps',
    f'$lossy_optional_integer_default_in(plenv_source, {raw_key}) = eps',
    f'$lossy_optional_integer_string_in(plenv_source, {dimension(string("09"), raw_key)}) = eps',
    f'$lossy_optional_integer_string_in(plenv_source, {dimension(string("09"), string_cast(raw_key))}) = ([57])',
])

# Selecting a FLOAT never authorizes precision-dependent string formatting.
for selected in [
    ternary(yes, node('NScalarFloat', 'FLOAT "3fe0000000000000"'), unknown),
    ternary(yes, node('NScalarFloat', 'FLOAT "7ff8000000000000"'), unknown),
    ternary(yes, node('NExprCastDouble', integer(1)), unknown),
    ternary(yes, binary('Div', integer(5), integer(2)), unknown),
    ternary(yes, binary('Plus', integer(9223372036854775807), integer(1)), unknown),
    ternary(yes, node('NExprBooleanNot', node('NScalarFloat', 'FLOAT "7ff8000000000000"')), unknown),
    ternary(yes, node('NExprArray', 'SEQUENCE eps'), unknown),
    ternary(yes, node('NExprVariable', 'BYTES "eA=="'), unknown),
    ternary(yes, unknown, string('1')),
    ternary(unknown, string('1'), string('0')),
    binary('Coalesce', unknown, string('1')),
]:
    expression = string_cast(selected)
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
    '$lookup(psymboltable_global.ENV, $ptascii("xReceive212")) = (n_cell)',
    '$lookup(psymboltable_global.ENV, $ptascii("countReceive212")) = (n_count)',
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
    '$lookup(S_done.ENV, $ptascii("gotReceive212")) = (n_got)',
    'S_done.STORE[n_got] = DEFINED (PINT 1)',
    r'$call_descriptors_valid(S_done) /\ $heap_valid($heap_graph(S_done))',
])

CASES = {'selection-string-cast-reference-leading': {
    'source': leading,
    'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 2 n_cell n_bits i z]',
    'checks': checks,
}}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
