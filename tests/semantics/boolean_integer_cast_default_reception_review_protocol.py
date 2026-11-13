#!/usr/bin/env python3
"""Boolean-cast default authority, boundary controls and reference retirement."""
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


def minimum():
    return binary('Pow', node('NExprUnaryMinus', integer(2)), integer(63))


def maximum():
    return node('NExprBitwiseNot', minimum())


terms = [
    cast(binary(kind, integer(left), integer(right)))
    for kind, left, right in [
        ('Equal', 1, 1), ('NotEqual', 1, 2), ('Identical', 1, 1),
        ('NotIdentical', 1, 2), ('Smaller', 1, 2), ('SmallerOrEqual', 1, 1),
        ('Greater', 2, 1), ('GreaterOrEqual', 2, 2),
    ]
] + [
    cast(binary('LogicalXor', constant('true'), constant('false'))),
    cast(binary('LogicalOr', constant('true'), constant('false'))),
    cast(binary('LogicalAnd', constant('true'), constant('true'))),
    cast(binary('BooleanOr', constant('true'), constant('UnselectedReceive197'))),
    cast(binary('BooleanOr', constant('false'), constant('true'))),
]
sum_terms = terms[0]
for term in terms[1:]:
    sum_terms = binary('Plus', sum_terms, term)
patterns = [
    binary('Minus', cast(logical_not(integer(0))), integer(8)),
    node('NExprUnaryMinus', binary('Plus',
         cast(binary('BooleanOr', constant('false'),
                     binary('BooleanAnd', constant('TrUe'), logical_not(integer(0))))), integer(10))),
    sum_terms,
    binary('Plus', binary('Plus', minimum(),
           cast(binary('BooleanAnd', constant('false'), constant('UnselectedReceive197')))),
           cast(binary('LogicalAnd', constant('false'), constant('UnselectedReceive197')))),
    binary('Minus', binary('Minus', maximum(), cast(logical_not(integer(1)))),
           cast(binary('Smaller', integer(2), integer(1)))),
]

CATALOGUE = Path(__file__).with_name('boolean_integer_cast_default_reception_cases.json')
assert hashlib.sha256(CATALOGUE.read_bytes()).hexdigest() == '1ed67136035f29b6589c63b5a12b775b6238a755d4e454bbe01db9bd79794250'
row = next(row for row in json.loads(CATALOGUE.read_text()) if row['id'] == 'boolean-integer-cast-precision-modes')
assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
source = row['source']
handler = source[:source.index('function valueFirstReceive197(')]
reference = source[source.index('function referenceReceive197('):source.index("set_error_handler('warningReceive197');")]
setup = source[source.index("set_error_handler('warningReceive197');"):source.index('$gotReceive197 = valueFirstReceive197(')]
start = source.index('$gotReceive197 = referenceReceive197(')
end = source.index('$xReceive197 = 1.5;', start)
# Exact five-default declaration and one leading named REF call, source0.
leading = handler + reference + setup + source[start:end]
assert hashlib.sha256(leading.encode()).hexdigest() == '153bbf2450507e83730b4ec141bf0759ea25ae88bb6011fb543f1be8ee92672e'

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
float_one = node('NScalarFloat', 'FLOAT "3ff0000000000000"')
string_zero = node('NScalarString', 'BYTES "MA=="')
checks.extend([
    '$lossy_optional_integer_header(S, pfunction, pfunction.SIGNATURE.PARAMETERS, 0)',
    'expression_a = NExprBinaryOpMinus expression_cast_a expression_eight metadata_a',
    'plenv_alias = plenv_source[.CONSTANTS = [($ptascii("TrUe"), $ptascii("false"))]]',
    '$lossy_optional_integer_default_in(plenv_alias, expression_b) = ($(-10))',
    '$lossy_optional_integer_default(expression_b) = ($(-11))',
    '~$lossy_optional_integer_header(S, pfunction[.ENV = plenv_alias], pfunction.SIGNATURE.PARAMETERS, 0)',
    'plenv_unknown = plenv_source[.CONSTANTS = [($ptascii("TrUe"), $ptascii("UnresolvedReceive197"))]]',
    '$lossy_optional_integer_default_in(plenv_unknown, expression_b) = eps',
    'plenv_skipped = plenv_source[.CONSTANTS = [($ptascii("UnselectedReceive197"), $ptascii("UnresolvedReceive197"))]]',
    '$lossy_optional_integer_header(S, pfunction[.ENV = plenv_skipped], pfunction.SIGNATURE.PARAMETERS, 0)',
    'expression_same = NExprBinaryOpPlus expression_a (NScalarInt (INTEGER 0) metadata_a) metadata_a',
    '$lossy_optional_integer_default_in(plenv_source, expression_same) = ($(-7))',
    '~$lossy_optional_integer_tail(S, pfunction, [psparam_a[.DEFAULT = PSDEFAULT expression_same "int"]], 0)',
    'pfunction.DEFAULTS = [pdefault_a, pdefault_b, pdefault_c, pdefault_d, pdefault_e]',
    '~$lossy_optional_integer_tail(S, pfunction[.DEFAULTS = [pdefault_a, pdefault_b[.KIND = PDDEFERRED], pdefault_c, pdefault_d, pdefault_e]], [psparam_b], 1)',
    'S_wrong_value = S[.POOLS = [{UNIT n_unit, CONSTANTS ([(PCONSTANT (pcpath_b ++ [PCFIELD 6]) (PINT $(-10)))])}]]',
    '$compiled_read(S_wrong_value, porigin_b) = (PINT $(-10))',
    '~$lossy_optional_integer_tail(S_wrong_value, pfunction, [psparam_b], 1)',
])

# Equal long boundaries exercise both Boolean results without floating coercion.
for kind, expected in [
    ('Equal', 1), ('NotEqual', 0), ('Identical', 1), ('NotIdentical', 0),
    ('Smaller', 0), ('SmallerOrEqual', 1), ('Greater', 0), ('GreaterOrEqual', 1),
]:
    checks.append(f'$lossy_optional_integer_default_in(plenv_source, {cast(binary(kind, minimum(), minimum()))}) = ({expected})')
for kind, expected in [
    ('Equal', 0), ('NotEqual', 1), ('Identical', 0), ('NotIdentical', 1),
    ('Smaller', 1), ('SmallerOrEqual', 1), ('Greater', 0), ('GreaterOrEqual', 0),
]:
    checks.append(f'$lossy_optional_integer_default_in(plenv_source, {cast(binary(kind, minimum(), maximum()))}) = ({expected})')

for kind in ('BooleanOr', 'LogicalOr', 'BooleanAnd', 'LogicalAnd'):
    is_or = kind.endswith('Or')
    decisive, needed = ('true', 'false') if is_or else ('false', 'true')
    checks.extend([
        f'$lossy_optional_integer_default_in(plenv_source, {cast(binary(kind, constant(decisive), constant("UnselectedReceive197")))}) = ({1 if is_or else 0})',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(binary(kind, constant(needed), constant("UnselectedReceive197")))}) = eps',
        f'$lossy_optional_integer_default_in(plenv_source, {cast(binary(kind, constant("UnselectedReceive197"), constant(decisive)))}) = eps',
    ])
checks.extend([
    f'$lossy_optional_integer_default_in(plenv_source, {cast(binary("LogicalXor", constant("false"), constant("UnselectedReceive197")))}) = eps',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(binary("LogicalXor", constant("UnselectedReceive197"), constant("true")))}) = eps',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(binary("LogicalAnd", integer(7), node("NExprUnaryMinus", integer(1))))}) = (1)',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(integer(7))}) = (7)',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(binary("Spaceship", minimum(), maximum()))}) = ($(-1))',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(binary("Equal", integer(1), integer(1)))}) = (1)',
    f'$lossy_optional_integer_default_in(plenv_alias, {cast(logical_not(constant("TrUe", qualified=True)))}) = (0)',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(binary("Equal", integer(9223372036854775808), integer(9223372036854775808)))}) = eps',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(binary("Equal", integer(1), float_one))}) = eps',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(logical_not(string_zero))}) = eps',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(node("NExprTernary", constant("true"), constant("true"), constant("false")))}) = eps',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(binary("Coalesce", constant("true"), constant("false")))}) = eps',
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
    '$lookup(S_done.ENV, $ptascii("gotReceive197")) = (n_got)',
    'S_done.STORE[n_got] = DEFINED (PINT 1)',
    r'$call_descriptors_valid(S_done) /\ $heap_valid($heap_graph(S_done))',
])

CASES = {'boolean-cast-reference-leading': {
    'source': leading,
    'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 2 n_cell n_bits i z]',
    'checks': checks,
}}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
