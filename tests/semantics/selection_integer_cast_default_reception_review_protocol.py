#!/usr/bin/env python3
"""Selected-cast default authority, boundary controls and reference retirement."""
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
    node('NExprUnaryMinus', cast(ternary(integer(7), 'ABSENT', constant('UnselectedReceive198')))),
    cast(binary('Coalesce', constant('null'), ternary(constant('false'), 'ABSENT', string('-11tail')))),
    binary('Plus', integer(13), cast(binary('Coalesce',
            ternary(constant('true'), binary('Smaller', integer(1), integer(0)), constant('UnselectedReceive198')), constant('UnselectedReceive198')))),
    cast(ternary(constant('true'), node('NExprUnaryMinus', node('NScalarFloat', 'FLOAT "43e0000000000000"')), constant('UnselectedReceive198'))),
    cast(binary('Coalesce', ternary(constant('false'), constant('UnselectedReceive198'), constant('null')), string('999999999999999999999999'))),
]


CATALOGUE = Path(__file__).with_name('selection_integer_cast_default_reception_cases.json')
assert hashlib.sha256(CATALOGUE.read_bytes()).hexdigest() == '842a310ff4252e3174d800355f743a4196b859fbb0eb8526d69049a75c4addce'
row = next(row for row in json.loads(CATALOGUE.read_text()) if row['id'] == 'selection-integer-cast-precision-modes')
assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
source = row['source']
handler = source[:source.index('function valueFirstReceive198(')]
reference = source[source.index('function referenceReceive198('):source.index("set_error_handler('warningReceive198');")]
setup = source[source.index("set_error_handler('warningReceive198');"):source.index('$gotReceive198 = valueFirstReceive198(')]
start = source.index('$gotReceive198 = referenceReceive198(')
end = source.index('$xReceive198 = 1.5;', start)
# Exact five-default declaration and one leading named REF call, source0.
leading = handler + reference + setup + source[start:end]
assert hashlib.sha256(leading.encode()).hexdigest() == '998afea7b53858f27ff23d3c9f7272b992b1f2e92664642c21e7c4ec5f964fcc'

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
    'expression_a = NExprUnaryMinus expression_cast_a metadata_a',
    'plenv_alias = plenv_source[.CONSTANTS = [($ptascii("null"), $ptascii("false"))]]',
    '$lossy_optional_integer_default_in(plenv_alias, expression_b) = (0)',
    '$lossy_optional_integer_default_in(plenv_alias, expression_e) = (0)',
    '~$lossy_optional_integer_header(S, pfunction[.ENV = plenv_alias], pfunction.SIGNATURE.PARAMETERS, 0)',
    'plenv_true_alias = plenv_source[.CONSTANTS = [($ptascii("true"), $ptascii("false"))]]',
    '$lossy_optional_integer_default_in(plenv_true_alias, expression_c) = eps',
    '$lossy_optional_integer_default_in(plenv_true_alias, expression_d) = eps',
    'plenv_skipped = plenv_source[.CONSTANTS = [($ptascii("UnselectedReceive198"), $ptascii("UnresolvedReceive198"))]]',
    '$lossy_optional_integer_header(S, pfunction[.ENV = plenv_skipped], pfunction.SIGNATURE.PARAMETERS, 0)',
    'expression_same = NExprCastInt (NScalarString (BYTES "LTExdGFpbA==") metadata_a) metadata_a',
    '$lossy_optional_integer_default_in(plenv_source, expression_same) = ($(-11))',
    '~$lossy_optional_integer_tail(S, pfunction, [psparam_b[.DEFAULT = PSDEFAULT expression_same "int"]], 1)',
    'pfunction.DEFAULTS = [pdefault_a, pdefault_b, pdefault_c, pdefault_d, pdefault_e]',
    '~$lossy_optional_integer_tail(S, pfunction[.DEFAULTS = [pdefault_a, pdefault_b[.KIND = PDDEFERRED], pdefault_c, pdefault_d, pdefault_e]], [psparam_b], 1)',
    'S_wrong_type = S[.POOLS = [{UNIT n_unit, CONSTANTS ([(PCONSTANT (pcpath_c ++ [PCFIELD 6]) (PBOOL false))])}]]',
    '$compiled_read(S_wrong_type, porigin_c) = (PBOOL false)',
    '~$lossy_optional_integer_tail(S_wrong_type, pfunction, [psparam_c], 2)',
])

zero, one, two, seven, thirteen = map(integer, (0, 1, 2, 7, 13))
true, false, null = map(constant, ('true', 'false', 'null'))
unknown = constant('UnselectedReceive198')
large = node('NScalarFloat', 'FLOAT "43e0000000000000"')
minimum = node('NExprUnaryMinus', large)
negative_zero = node('NExprUnaryMinus', node('NScalarFloat', 'FLOAT "0000000000000000"'))
nan = node('NScalarFloat', 'FLOAT "7ff8000000000000"')
float_one = node('NScalarFloat', 'FLOAT "3ff0000000000000"')
saturated = string('999999999999999999999999')

# Falsy nonnull values stay on the left; failed classifications never rescue RHS.
for left, expected in [
    (false, '0'), (zero, '0'), (string(''), '0'), (string('0'), '0'),
    (negative_zero, '0'), (binary('Smaller', one, zero), '0'),
    (string('12tail'), '12'), (string('nonnumeric'), '0'),
]:
    checks.append(f'$lossy_optional_integer_default_in(plenv_source, {cast(binary("Coalesce", left, unknown))}) = ({expected})')
for left in [unknown, large, nan, binary('Concat', string('1'), string('2'))]:
    checks.append(f'$lossy_optional_integer_default_in(plenv_source, {cast(binary("Coalesce", left, thirteen))}) = eps')

# These four outcomes replace the affected old197 assertions without replay.
for expression in [
    ternary(true, true, false), ternary(one, true, unknown),
    binary('Coalesce', null, true), binary('Coalesce', true, false),
]:
    checks.append(f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = (1)')

for expression, expected in [
    (ternary(seven, 'ABSENT', unknown), '7'),
    (ternary(true, 'ABSENT', unknown), '1'),
    (ternary(false, 'ABSENT', string('-11tail')), '$(-11)'),
    (ternary(zero, 'ABSENT', string('nonnumeric')), '0'),
    (ternary(true, false, unknown), '0'),
    (ternary(false, unknown, null), '0'),
    (ternary(true, minimum, unknown), '$(-9223372036854775808)'),
    (binary('Coalesce', ternary(true, null, unknown), saturated), '9223372036854775807'),
    (ternary(true, binary('Coalesce', false, unknown), unknown), '0'),
    (ternary(true, logical_not(zero), unknown), '1'),
    (ternary(true, binary('Spaceship', one, two), unknown), '$(-1)'),
]:
    checks.append(f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = ({expected})')
for expression in [
    ternary(unknown, seven, seven), ternary(string('1'), seven, thirteen),
    ternary(float_one, seven, thirteen), ternary(true, unknown, seven),
    ternary(true, large, minimum),
    ternary(true, node('NExprUnaryMinus', minimum), unknown),
    ternary(true, nan, unknown),
    node('NExprUnaryMinus', ternary(true, large, unknown)),
]:
    checks.append(f'$lossy_optional_integer_default_in(plenv_source, {cast(expression)}) = eps')
checks.extend([
    f'$lossy_optional_integer_default_in(plenv_source, {ternary(true, false, unknown)}) = eps',
    f'$lossy_optional_integer_default_in(plenv_alias, {cast(binary("Coalesce", constant("null", qualified=True), thirteen))}) = (13)',
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
    '$lookup(S_done.ENV, $ptascii("gotReceive198")) = (n_got)',
    'S_done.STORE[n_got] = DEFINED (PINT 1)',
    r'$call_descriptors_valid(S_done) /\ $heap_valid($heap_graph(S_done))',
])

CASES = {'selection-cast-reference-leading': {
    'source': leading,
    'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 2 n_cell n_bits i z]',
    'checks': checks,
}}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
