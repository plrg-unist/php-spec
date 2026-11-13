#!/usr/bin/env python3
"""Scalar truth default authority, boundary controls and reference retirement."""
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
    return node('NScalarInt', f'INTEGER {value}')


def constant(name, qualified=False):
    kind = 'NNameFullyQualified' if qualified else 'NName'
    return node('NExprConstFetch', node(kind, f'BYTES "{base64.b64encode(name.encode()).decode()}"'))


def binary(kind, left, right):
    return node('NExprBinaryOp' + kind, left, right)


def cast(child):
    return node('NExprCastInt', child)


def logical_not(child):
    return node('NExprBooleanNot', child)


def string(value):
    return node('NScalarString', f'BYTES "{base64.b64encode(value.encode()).decode()}"')


def ternary(condition, selected, alternative):
    return node('NExprTernary', condition, selected, alternative)


patterns = [
    node('NExprUnaryMinus', ternary(string('0'), constant('UnselectedReceive199'), integer(7))),
    cast(ternary(string(''), 'ABSENT', string('-11tail'))),
    binary('Plus', integer(13), cast(binary('LogicalXor',
        binary('BooleanAnd', string('00'), string('\0')),
        binary('BooleanAnd', node('NExprBooleanNot', string('0')),
                node('NExprUnaryMinus', node('NScalarFloat', 'FLOAT "3fe0000000000000"')))))),
    ternary(node('NExprUnaryPlus', node('NExprUnaryMinus', node('NScalarFloat', 'FLOAT "0000000000000000"'))),
            constant('UnselectedReceive199'), cast(ternary(string('1'), node('NExprUnaryMinus', node('NScalarFloat', 'FLOAT "43e0000000000000"')), constant('UnselectedReceive199')))),
    cast(ternary(binary('BooleanAnd', node('NExprUnaryPlus', node('NScalarFloat', 'FLOAT "7ff0000000000000"')),
                  binary('BooleanOr', node('NExprUnaryMinus', node('NScalarFloat', 'FLOAT "3fe0000000000000"')), string('0'))),
                 string('999999999999999999999999'), constant('UnselectedReceive199'))),
]


CATALOGUE = Path(__file__).with_name('scalar_truth_default_reception_cases.json')
assert hashlib.sha256(CATALOGUE.read_bytes()).hexdigest() == 'cbef3eacef90a99f2179b1878a7b491cea0575f3ca824dd4f28cafb7ab3e2e4b'
row = next(row for row in json.loads(CATALOGUE.read_text()) if row['id'] == 'scalar-truth-precision-modes')
assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
source = row['source']
handler = source[:source.index('function valueFirstReceive199(')]
reference = source[source.index('function referenceReceive199('):source.index("set_error_handler('warningReceive199');")]
setup = source[source.index("set_error_handler('warningReceive199');"):source.index('$gotReceive199 = valueFirstReceive199(')]
start = source.index('$gotReceive199 = referenceReceive199(')
end = source.index('$xReceive199 = 1.5;', start)
# Exact five-default declaration and one leading named REF call, source0.
leading = handler + reference + setup + source[start:end]
assert hashlib.sha256(leading.encode()).hexdigest() == '36ff5ad0d6b224ceb34de0452bb7dddbf42fddc8adb8e098f4314881e3627c71'

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
fixed_metadata = 'metadata_a'
checks.extend([
    '$lossy_optional_integer_header(S, pfunction, pfunction.SIGNATURE.PARAMETERS, 0)',
    'expression_a = NExprUnaryMinus expression_select_a metadata_a',
    'plenv_alias = plenv_source[.CONSTANTS = [($ptascii("true"), $ptascii("false"))]]',
    '$lossy_optional_integer_header(S, pfunction[.ENV = plenv_alias], pfunction.SIGNATURE.PARAMETERS, 0)',
    'expression_same = NExprUnaryMinus (NScalarInt (INTEGER 7) metadata_a) metadata_a',
    '$lossy_optional_integer_default_in(plenv_source, expression_same) = ($(-7))',
    '~$lossy_optional_integer_tail(S, pfunction, [psparam_a[.DEFAULT = PSDEFAULT expression_same "int"]], 0)',
    'pfunction.DEFAULTS = [pdefault_a, pdefault_b, pdefault_c, pdefault_d, pdefault_e]',
    '~$lossy_optional_integer_tail(S, pfunction[.DEFAULTS = [pdefault_a[.KIND = PDDEFERRED], pdefault_b, pdefault_c, pdefault_d, pdefault_e]], [psparam_a], 0)',
    'S_no_pool = S[.POOLS = eps]',
    '$origin_node(S_no_pool.SOURCES, porigin_a) = (expression_a)',
    '$compiled_read(S_no_pool, porigin_a) = eps',
    '~$lossy_optional_integer_header(S_no_pool, pfunction, pfunction.SIGNATURE.PARAMETERS, 0)',
    'S_wrong_type = S[.POOLS = [{UNIT n_unit, CONSTANTS ([(PCONSTANT (pcpath_c ++ [PCFIELD 6]) (PBOOL false))])}]]',
    '$compiled_read(S_wrong_type, porigin_c) = (PBOOL false)',
    '~$lossy_optional_integer_tail(S_wrong_type, pfunction, [psparam_c], 2)',
])


def floating(bits):
    return node('NScalarFloat', f'FLOAT "{bits}"')


zero, one, seven, thirteen = map(integer, (0, 1, 7, 13))
true, false = map(constant, ('true', 'false'))
unknown = constant('UnselectedReceive199')
fraction = node('NExprUnaryMinus', floating('3fe0000000000000'))
large = floating('43e0000000000000')
nan = floating('7ff8000000000000')

# Raw bytes use PHP truth, independently of numeric spelling or constant imports.
for value, expected in [
    ('', 'false'), ('0', 'false'), ('00', 'true'), ('0.0', 'true'),
    (' 0', 'true'), ('0 ', 'true'), ('\0', 'true'), ('0\0', 'true'),
    ('false', 'true'), ('null', 'true'),
]:
    checks.append(f'$lossy_optional_integer_condition(plenv_source, {string(value)}) = ({expected})')
binary_string = node('NScalarString', 'BYTES "/w=="')
checks.extend([
    f'$lossy_optional_integer_condition(plenv_source, {binary_string}) = (true)',
    f'$lossy_optional_integer_condition(plenv_alias, {string("true")}) = (true)',
    f'$lossy_optional_integer_condition(plenv_alias, {constant("true")}) = (false)',
])
for bits, expected in [
    ('0000000000000000', 'false'), ('8000000000000000', 'false'),
    ('0000000000000001', 'true'), ('8000000000000001', 'true'),
    ('3ff0000000000000', 'true'), ('bfe0000000000000', 'true'),
    ('43e0000000000000', 'true'), ('7fefffffffffffff', 'true'),
    ('7ff0000000000000', 'true'), ('fff0000000000000', 'true'),
]:
    checks.append(f'$lossy_optional_integer_condition(plenv_source, {floating(bits)}) = ({expected})')
for bits in ('7ff8000000000000', 'fff8000000000000', '7ff0000000000001'):
    checks.append(f'$lossy_optional_integer_condition(plenv_source, {floating(bits)}) = eps')
checks.extend([
    f'$lossy_optional_integer_condition(plenv_source, {fraction}) = (true)',
    f'$lossy_optional_integer_condition(plenv_source, {cast(fraction)}) = (false)',
    f'$lossy_optional_integer_condition(plenv_source, {node("NExprUnaryPlus", node("NExprUnaryMinus", floating("0000000000000000")))}) = (false)',
])

# Value-preserving shorthand and later cast eligibility remain separate from truth.
for expression, expected in [
    (ternary(string('12tail'), 'ABSENT', unknown), '12'),
    (ternary(fraction, 'ABSENT', unknown), '0'),
    (ternary(large, seven, unknown), '7'),
    (ternary(string('0'), unknown, string('-11tail')), '$(-11)'),
    (ternary(floating('8000000000000000'), unknown, thirteen), '13'),
]:
    checks.append(f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = ({expected})')
checks.extend([
    f'$lossy_optional_integer_default_in(plenv_source, {cast(large)}) = eps',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(ternary(large, "ABSENT", thirteen))}) = eps',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(ternary(nan, seven, thirteen))}) = eps',
])
for kind, left, right, expected in [
    ('BooleanAnd', string('0'), unknown, 'false'),
    ('LogicalAnd', floating('8000000000000000'), unknown, 'false'),
    ('BooleanOr', floating('7ff0000000000000'), unknown, 'true'),
    ('LogicalOr', string('00'), nan, 'true'),
]:
    checks.append(f'$lossy_optional_integer_condition(plenv_source, {binary(kind, left, right)}) = ({expected})')
for expression in [
    binary('BooleanAnd', string('00'), unknown),
    binary('LogicalOr', string('0'), unknown),
    binary('LogicalXor', string('0'), unknown),
    binary('LogicalXor', unknown, string('00')),
    binary('BooleanOr', nan, true),
    binary('Concat', string('0'), string('0')),
    binary('Plus', floating('3fe0000000000000'), floating('3fe0000000000000')),
    node('NExprArray', 'SEQUENCE eps'),
]:
    checks.append(f'$lossy_optional_integer_condition(plenv_source, {expression}) = eps')
checks.append(f'$lossy_optional_integer_condition(plenv_source, {node("NExprCastBool", one)}) = (true)')

# Freshly check all seven affected old193/197/198 outcomes without old actors.
for cond in (string('1'), floating('3ff0000000000000')):
    for alternative in (zero, thirteen):
        checks.append(f'$lossy_optional_integer_default_in(plenv_source, {cast(ternary(cond, seven, alternative))}) = (7)')
checks.extend([
    f'$lossy_optional_integer_condition(plenv_source, {string("0")}) = (false)',
    f'$lossy_optional_integer_condition(plenv_source, {floating("0000000000000000")}) = (false)',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(logical_not(string("0")))}) = (1)',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(logical_not(floating("3ff0000000000000")))}) = (0)',
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
    r'$lookup(S.ENV, psparam_d.NAME) = eps /\ $lookup(S.ENV, psparam_e.NAME) = eps',
    r'S.STORE[n_cell] = DEFINED (PFLOAT 4615063718147915776) /\ n_cell <- S.REFCELLS',
    '$heap_owners($heap_graph(S), HCELL n_cell) = 2',
    '$lossy_mixed_parameter_source_valid(S, LOSSY_MIXED_PARAMETER_RECEIVE porigin 2 n_cell n_bits i z)',
    '$task_nodes(LOSSY_MIXED_PARAMETER_RECEIVE porigin 2 n_cell n_bits i z) = eps',
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
    r'S_body.EVENTS = S.EVENTS /\ $call_descriptors_valid(S_body) /\ $heap_valid($heap_graph(S_body))',
    'S_done = $drive_steps(S_body, 2000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    r'~((HCELL n_a) <- S_done.ALLOCATIONS) /\ ~((HCELL n_b) <- S_done.ALLOCATIONS) /\ ~((HCELL n_d) <- S_done.ALLOCATIONS) /\ ~((HCELL n_e) <- S_done.ALLOCATIONS)',
    r'S_done.STORE[n_cell] = DEFINED (PINT 1) /\ $heap_owners($heap_graph(S_done), HCELL n_cell) = 1',
    '$lookup(S_done.ENV, $ptascii("gotReceive199")) = (n_got)',
    'S_done.STORE[n_got] = DEFINED (PINT 1)',
    r'$call_descriptors_valid(S_done) /\ $heap_valid($heap_graph(S_done))',
])

CASES = {'scalar-truth-reference-leading': {
    'source': leading,
    'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 2 n_cell n_bits i z]',
    'checks': checks,
}}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
