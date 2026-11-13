#!/usr/bin/env python3
"""Declaration-context scalar casts preserve lexical imports and receive ownership."""
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
    node('NExprUnaryMinus', ternary(string_cast(constant('NoReceive210')), constant('UnselectedReceive210'), integer(7))),
    cast(ternary(string_cast(binary('Concat', string_cast(constant('NoReceive210')), string('0.0'))),
                 string_cast(binary('Concat', binary('Concat', string_cast(binary('Minus', node('NExprUnaryMinus', integer(10)), integer(1))), string_cast(constant('false', qualified=True))), string('tail'))), constant('UnselectedReceive210'))),
    cast(ternary(node('NExprCastDouble', ternary(constant('true'),
                                               binary('Concat', string_cast(node('NExprBooleanNot', constant('NoReceive210'))), string('.5tail')), constant('UnselectedReceive210'))),
                 binary('Concat', string_cast(constant('YesReceive210')), string('3tail')), constant('UnselectedReceive210'))),
    ternary(node('NExprCastDouble', binary('Coalesce', constant('null'), binary('Concat', string_cast(constant('NilReceive210')), string('0.0')))),
            constant('UnselectedReceive210'), cast(string('-9223372036854775808tail'))),
    cast(ternary(constant('true'), binary('Concat', string_cast(ternary(constant('YesReceive210'), integer(9), constant('UnselectedReceive210'))), string('9' * 23)), constant('UnselectedReceive210'))),
]

contrasts = [
    ('floatnot', 'deferredFloatNotReceive210', cast(node('NExprBooleanNot', node('NScalarFloat', 'FLOAT "3fe0000000000000"'))), '(0)'),
    ('negative', 'deferredNegativeIndexReceive210', cast(dimension(string('10'), string('-1'))), 'eps'),
    ('floatindex', 'deferredFloatIndexReceive210', cast(dimension(string('10'), string('1.0'))), 'eps'),
    ('floatstring', 'deferredFloatStringReceive210', cast(string_cast(node('NScalarFloat', 'FLOAT "3fe0000000000000"'))), 'eps'),
]

CATALOGUE = Path(__file__).with_name('contextual_string_cast_default_reception_cases.json')
assert hashlib.sha256(CATALOGUE.read_bytes()).hexdigest() == '2ebd690227827b198221eff8cd08445975ad739f729354b6f4aa5e148b443999'
row = next(row for row in json.loads(CATALOGUE.read_text()) if row['id'] == 'contextual-string-cast-precision-modes')
assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
source = row['source']
handler = source[:source.index('function valueFirstReceive210(')]
reference = source[source.index('function referenceReceive210('):source.index("set_error_handler('warningReceive210');")]
setup = source[source.index("set_error_handler('warningReceive210');"):source.index('$gotReceive210 = valueFirstReceive210(')]
start = source.index('$gotReceive210 = referenceReceive210(')
end = source.index('$xReceive210 = 1.5;', start)
leading = handler + reference + setup + source[start:end]
assert hashlib.sha256(leading.encode()).hexdigest() == 'aa09f017bad01271bb94946ebb08a1777477c2e59b406402f54c7efc20d44858'

checks = [
    r'n_bits = 4609434218613702656 /\ i = 1',
    '$function_at(S.FUNCTIONS, porigin) = (pfunction)',
    'plenv_source = pfunction.ENV',
    r'plenv_source.NAMESPACE = eps /\ plenv_source.CONSTANTS = [($ptascii("YesReceive210"), $ptascii("true")), ($ptascii("NoReceive210"), $ptascii("false")), ($ptascii("NilReceive210"), $ptascii("null"))]',
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
    'plenv_alias = plenv_source[.CONSTANTS = [($ptascii("YesReceive210"), $ptascii("false")), ($ptascii("NoReceive210"), $ptascii("false")), ($ptascii("NilReceive210"), $ptascii("null"))]]',
    '$lossy_optional_integer_default_in(plenv_alias, expression_c) = (3)',
    '$lossy_optional_integer_default_in(plenv_alias, expression_e) = eps',
    '~$lossy_optional_integer_header(S, pfunction[.ENV = plenv_alias], pfunction.SIGNATURE.PARAMETERS, 0)',
    'plenv_null_alias = plenv_source[.CONSTANTS = [($ptascii("YesReceive210"), $ptascii("true")), ($ptascii("NoReceive210"), $ptascii("false")), ($ptascii("NilReceive210"), $ptascii("true"))]]',
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
unknown = constant('UnselectedReceive210')

# Prove actual declaration ENV is needed for the original float-zero leaf.
checks.extend([
    'expression_d = NExprTernary expression_float_d expression_unused_d expression_minimum_d metadata_d',
    'expression_float_d = NExprCastDouble expression_coalesce_d metadata_float_d',
    'expression_coalesce_d = NExprBinaryOpCoalesce expression_null_d expression_zero_d metadata_coalesce_d',
    '$lossy_optional_integer_leaf_truth(plenv_source, expression_coalesce_d) = ((expression_zero_d, true))',
    '$lossy_optional_integer_string_in(plenv_source, expression_zero_d) = ($ptascii("0.0"))',
    '$lossy_optional_integer_string(expression_zero_d) = eps',
    '$lossy_optional_integer_float_truth_in(plenv_source, expression_zero_d, true) = false',
    '$lossy_optional_integer_float_truth(expression_zero_d, true) = true',
    '$lossy_optional_integer_condition(plenv_source, expression_float_d) = (false)',
    'plenv_no_alias = plenv_source[.CONSTANTS = [($ptascii("YesReceive210"), $ptascii("true")), ($ptascii("NoReceive210"), $ptascii("true")), ($ptascii("NilReceive210"), $ptascii("null"))]]',
    '$lossy_optional_integer_default_in(plenv_no_alias, expression_a) = eps',
    '~$lossy_optional_integer_header(S, pfunction[.ENV = plenv_no_alias], pfunction.SIGNATURE.PARAMETERS, 0)',
    'plenv_fqn_alias = plenv_source[.CONSTANTS = plenv_source.CONSTANTS ++ [($ptascii("false"), $ptascii("true"))]]',
    '$lossy_optional_integer_default_in(plenv_fqn_alias, expression_b) = ($(-11))',
])
# Alias operands project through real ENV; the old wrapper keeps its empty ENV.
for name, data, truth, value in [('YesReceive210', '[49]', 'true', '1'),
                                ('NoReceive210', 'eps', 'false', '0'),
                                ('NilReceive210', 'eps', 'false', '0')]:
    expression = string_cast(constant(name))
    checks.extend([
        f'$lossy_optional_integer_string_in(plenv_source, {expression}) = ({data})',
        f'$lossy_optional_integer_string({expression}) = eps',
        f'$lossy_optional_integer_condition(plenv_source, {expression}) = ({truth})',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = ({value})',
        f'$lossy_optional_integer_string_in(plenv_source, {string_cast(constant(name, qualified=True))}) = eps',
    ])
checks.extend([
    f'$lossy_optional_integer_string_in(plenv_fqn_alias, {string_cast(constant("false", qualified=True))}) = (eps)',
    f'$lossy_optional_integer_string_in(plenv_fqn_alias, {string_cast(constant("false"))}) = ([49])',
])
yes, no, nil = map(constant, ('YesReceive210', 'NoReceive210', 'NilReceive210'))
# Typed Boolean shapes never grant integer or arbitrary truth-string authority.
for child, truth in [
    (node('NExprBooleanNot', no), 'true'),
    (binary('BooleanAnd', yes, no), 'false'),
    (binary('BooleanOr', yes, unknown), 'true'),
    (binary('BooleanAnd', no, unknown), 'false'),
    (binary('LogicalXor', yes, no), 'true'),
    (node('NExprCastBool', integer(2)), 'true'),
    (binary('Equal', integer(1), integer(1)), 'true'),
    (binary('Smaller', integer(2), integer(1)), 'false'),
]:
    expression = string_cast(child)
    data, value = ('[49]', '1') if truth == 'true' else ('eps', '0')
    checks.extend([
        f'$lossy_optional_integer_boolean_shape({child})',
        f'$lossy_optional_integer_default_in(plenv_source, {child}) = eps',
        f'$lossy_optional_integer_condition(plenv_source, {child}) = ({truth})',
        f'$lossy_optional_integer_string_in(plenv_source, {expression}) = ({data})',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = ({value})',
    ])
# Existing PINT certificates admit computed and selected integer cast children.
for child, text, value in [
    (binary('Minus', node('NExprUnaryMinus', integer(10)), integer(1)), '-11', '$(-11)'),
    (binary('Div', integer(6), integer(2)), '3', '3'),
    (binary('Mod', integer(-9), integer(4)), '-1', '$(-1)'),
    (cast(string('1tail')), '1', '1'),
    (binary('Spaceship', integer(1), integer(2)), '-1', '$(-1)'),
    (ternary(yes, integer(9), unknown), '9', '9'),
    (binary('Coalesce', nil, integer(5)), '5', '5'),
]:
    expression = string_cast(child)
    checks.extend([
        f'$lossy_optional_integer_default_in(plenv_source, {child}) = ({value})',
        f'$lossy_optional_integer_string_in(plenv_source, {expression}) = ($ptascii("{text}"))',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = ({value})',
    ])
checks.append(f'$lossy_optional_integer_string_in(plenv_alias, {string_cast(ternary(yes, integer(9), unknown))}) = eps')
# Both byte operands and both DIM operands retain ENV through recursion.
for expression, data in [
    (binary('Concat', string_cast(no), string('0.0')), [48,46,48]),
    (node('NExprBitwiseNot', string_cast(yes)), [206]),
    (binary('BitwiseAnd', string(b'\xff'), string_cast(yes)), [49]),
    (binary('BitwiseOr', string_cast(no), string('0.0')), [48,46,48]),
    (binary('BitwiseXor', string_cast(yes), string(b'\0')), [49]),
    (dimension(binary('Concat', string_cast(no), string('x0')), string_cast(yes)), [48]),
    (string_cast(binary('Concat', string_cast(nil), string('0.0'))), [48,46,48]),
]:
    expected = '[' + ', '.join(map(str, data)) + ']'
    checks.extend([
        f'$lossy_optional_integer_string_in(plenv_source, {expression}) = ({expected})',
        f'$lossy_optional_integer_string({expression}) = eps',
    ])
# Fresh checks of all eighteen promoted old209 peer assertions; inputs unchanged.
for child, data, truth, value in [
    (constant('true'), '[49]', 'true', '1'),
    (constant('false'), 'eps', 'false', '0'),
    (constant('null'), 'eps', 'false', '0'),
    (constant('true', qualified=True), '[49]', 'true', '1'),
    (cast(string('1')), '[49]', 'true', '1'),
    (binary('Plus', integer(0), integer(1)), '[49]', 'true', '1'),
]:
    expression = string_cast(child)
    checks.extend([
        f'$lossy_optional_integer_string({expression}) = ({data})',
        f'$lossy_optional_integer_condition(plenv_source, {expression}) = ({truth})',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = ({value})',
    ])
# Precision/warning/unknown domains remain separate from scalar certificates.
nan = node('NScalarFloat', 'FLOAT "7ff8000000000000"')
fraction = node('NScalarFloat', 'FLOAT "3fe0000000000000"')
for child in [
    node('NExprBooleanNot', nan), node('NExprCastBool', nan), fraction,
    string_cast(fraction), binary('Plus', fraction, integer(0)),
    node('NExprCastDouble', string('1')), binary('Div', integer(5), integer(2)),
    binary('Plus', integer(9223372036854775807), integer(1)),
    ternary(constant('true'), fraction, unknown),
    ternary(constant('true'), string('1'), unknown), unknown,
    node('NExprVariable', 'BYTES "aW5kZXg="'), node('NExprArray', 'SEQUENCE eps'),
]:
    expression = string_cast(child)
    promoted = child.startswith('NExprTernary ') and 'NScalarString' in child
    projected, truth, result = ('([49])', '(true)', '(1)') if promoted else ('eps', 'eps', 'eps')
    checks.extend([
        f'$lossy_optional_integer_string_in(plenv_source, {expression}) = {projected}',
        f'$lossy_optional_integer_condition(plenv_source, {expression}) = {truth}',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = {result}',
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
    '$lookup(psymboltable_global.ENV, $ptascii("xReceive210")) = (n_cell)',
    '$lookup(psymboltable_global.ENV, $ptascii("countReceive210")) = (n_count)',
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
    '$lookup(S_done.ENV, $ptascii("gotReceive210")) = (n_got)',
    'S_done.STORE[n_got] = DEFINED (PINT 1)',
    r'$call_descriptors_valid(S_done) /\ $heap_valid($heap_graph(S_done))',
])

CASES = {'contextual-string-cast-reference-leading': {
    'source': leading,
    'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 2 n_cell n_bits i z]',
    'checks': checks,
}}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
