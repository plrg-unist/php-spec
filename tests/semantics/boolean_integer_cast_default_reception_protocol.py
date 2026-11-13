#!/usr/bin/env python3
"""Boolean-producing integer casts retain exact omitted-default ownership."""
import base64
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('boolean_integer_cast_default_reception_cases.json')
SOURCES = {}
for row in json.loads(CATALOGUE.read_text()):
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
    SOURCES[row['id']] = row['source']

# Fresh first-VAL front preserves the whole five-default declaration; source0.
full = SOURCES['boolean-integer-cast-precision-modes']
setup = full.index("set_error_handler('warningReceive197');")
start = full.index('$gotReceive197 = valueFirstReceive197(')
end = full.index('$xReceive197 = 1.5;', start)
source = full[:full.index('function referenceFirstReceive197')] + full[setup:end]
assert hashlib.sha256(source.encode()).hexdigest() == '162df57df0640d3eb9a3c850c3a5c8e327386e88f90a3d5111fc3cbcb4bed9cd'

metadata_index = 0
def node(constructor, *children):
    global metadata_index
    metadata_index += 1
    return constructor + ''.join(f' ({child})' for child in children) + f' metadata_case_{metadata_index}'


def integer(value):
    return node('NScalarInt', f'INTEGER {value}')


def constant(name, qualified=False):
    payload = base64.b64encode(name.encode()).decode()
    return node('NExprConstFetch', node('NNameFullyQualified' if qualified else 'NName', f'BYTES "{payload}"'))


def cast(child):
    return node('NExprCastInt', child)


def add(left, right):
    return node('NExprBinaryOpPlus', left, right)


def binary(constructor, left, right):
    return node('NExprBinaryOp' + constructor, left, right)


def logical_not(child):
    return node('NExprBooleanNot', child)


def minimum():
    return binary('Pow', node('NExprUnaryMinus', integer(2)), integer(63))


predicates = ['Equal', 'NotEqual', 'Identical', 'NotIdentical', 'Smaller',
              'SmallerOrEqual', 'Greater', 'GreaterOrEqual']
terms = [cast(binary(constructor, integer(left), integer(right)))
         for constructor, left, right in zip(predicates,
             [1, 1, 1, 1, 1, 1, 2, 2], [1, 2, 1, 2, 2, 1, 1, 2])]
terms += [cast(binary('LogicalXor', constant('true'), constant('false'))),
          cast(binary('LogicalOr', constant('true'), constant('false'))),
          cast(binary('LogicalAnd', constant('true'), constant('true'))),
          cast(binary('BooleanOr', constant('true'), constant('UnselectedReceive197'))),
          cast(binary('BooleanOr', constant('false'), constant('true')))]
expression_thirteen = terms[0]
for term in terms[1:]:
    expression_thirteen = add(expression_thirteen, term)
patterns = [
    binary('Minus', cast(logical_not(integer(0))), integer(8)),
    node('NExprUnaryMinus', add(cast(binary('BooleanOr', constant('false'),
         binary('BooleanAnd', constant('TrUe'), logical_not(integer(0))))), integer(10))),
    expression_thirteen,
    add(add(minimum(), cast(binary('BooleanAnd', constant('false'), constant('UnselectedReceive197')))),
        cast(binary('LogicalAnd', constant('false'), constant('UnselectedReceive197')))),
    binary('Minus', binary('Minus', node('NExprBitwiseNot', minimum()), cast(logical_not(integer(1)))),
           cast(binary('Smaller', integer(2), integer(1)))),
]
checks = [
    r'n_bits = 4609434218613702656 /\ i = 1',
    '$function_at(S.FUNCTIONS, porigin) = (pfunction)',
    'plenv_source = pfunction.ENV',
    r'plenv_source.NAMESPACE = eps /\ plenv_source.CONSTANTS = eps',
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
checks.extend([
    '$lossy_optional_integer_header(S, pfunction, pfunction.SIGNATURE.PARAMETERS, 0)',
    'expression_a = NExprBinaryOpMinus expression_cast_a expression_eight metadata_a',
    'expression_cast_a = NExprCastInt expression_not_a metadata_cast_a',
    'expression_not_a = NExprBooleanNot expression_zero metadata_not_a',
    'expression_one = NScalarInt (INTEGER 1) metadata_a',
    'expression_two = NScalarInt (INTEGER 2) metadata_a',
    'expression_seven = NScalarInt (INTEGER 7) metadata_a',
    'expression_big = NScalarInt (INTEGER 9223372036854775808) metadata_a',
    'expression_unknown = NExprConstFetch (NName (BYTES "VW5rbm93blJlY2VpdmUxOTc=") metadata_a) metadata_a',
    '$lossy_optional_integer_boolean_shape(expression_not_a)',
    '~$lossy_optional_integer_boolean_shape(expression_seven)',
    '~$lossy_optional_integer_boolean_shape(NExprBinaryOpSpaceship expression_one expression_two metadata_a)',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt expression_seven metadata_a) = (7)',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt (NExprBinaryOpSpaceship expression_one expression_two metadata_a) metadata_a) = ($(-1))',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt (NExprBooleanNot expression_seven metadata_a) metadata_a) = (0)',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt (NExprBooleanNot expression_unknown metadata_a) metadata_a) = eps',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt (NExprBooleanNot expression_big metadata_a) metadata_a) = eps',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt (NExprBinaryOpEqual expression_one expression_one metadata_a) metadata_a) = (1)',
])
for left, expected in [('expression_zero', [0,1,0,1,1,1,0,0]),
                       ('expression_one', [1,0,1,0,0,1,0,1]),
                       ('expression_two', [0,1,0,1,0,0,1,1])]:
    for constructor, value in zip(predicates, expected):
        checks.append(f'$lossy_optional_integer_default_in(plenv_source, NExprCastInt (NExprBinaryOp{constructor} {left} expression_one metadata_a) metadata_a) = ({value})')
for constructor in ['Equal', 'Smaller']:
    for left, right in [('expression_unknown', 'expression_one'), ('expression_one', 'expression_unknown'),
                        ('expression_big', 'expression_one'), ('expression_one', 'expression_big')]:
        checks.append(f'$lossy_optional_integer_default_in(plenv_source, NExprCastInt (NExprBinaryOp{constructor} {left} {right} metadata_a) metadata_a) = eps')
for constructor, decisive, reached in [('BooleanAnd', 'expression_zero', 'expression_one'),
                                     ('LogicalAnd', 'expression_zero', 'expression_one'),
                                     ('BooleanOr', 'expression_one', 'expression_zero'),
                                     ('LogicalOr', 'expression_one', 'expression_zero')]:
    value = 1 if constructor.endswith('Or') else 0
    checks.extend([
        f'$lossy_optional_integer_default_in(plenv_source, NExprCastInt (NExprBinaryOp{constructor} {decisive} expression_unknown metadata_a) metadata_a) = ({value})',
        f'$lossy_optional_integer_default_in(plenv_source, NExprCastInt (NExprBinaryOp{constructor} {reached} expression_unknown metadata_a) metadata_a) = eps',
        f'$lossy_optional_integer_default_in(plenv_source, NExprCastInt (NExprBinaryOp{constructor} expression_unknown {decisive} metadata_a) metadata_a) = eps',
    ])
checks.extend([
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt (NExprBinaryOpLogicalXor expression_one expression_zero metadata_a) metadata_a) = (1)',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt (NExprBinaryOpLogicalXor expression_one expression_one metadata_a) metadata_a) = (0)',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt (NExprBinaryOpLogicalXor expression_one expression_unknown metadata_a) metadata_a) = eps',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt (NExprBinaryOpLogicalXor expression_unknown expression_one metadata_a) metadata_a) = eps',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt (NExprTernary expression_one (NExprConstFetch (NName (BYTES "dHJ1ZQ==") metadata_a) metadata_a) expression_unknown metadata_a) metadata_a) = (1)',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt (NExprBinaryOpCoalesce (NExprConstFetch (NName (BYTES "bnVsbA==") metadata_a) metadata_a) (NExprConstFetch (NName (BYTES "dHJ1ZQ==") metadata_a) metadata_a) metadata_a) metadata_a) = (1)',
    'plenv_alias = plenv_source[.CONSTANTS = [($ptascii("TrUe"), $ptascii("false"))]]',
    '$lossy_optional_integer_default_in(plenv_alias, expression_b) = ($(-10))',
    '~$lossy_optional_integer_header(S, pfunction[.ENV = plenv_alias], pfunction.SIGNATURE.PARAMETERS, 0)',
    'expression_same = NExprUnaryMinus expression_seven metadata_a',
    '$lossy_optional_integer_default_in(plenv_source, expression_same) = ($(-7))',
    '~$lossy_optional_integer_tail(S, pfunction, [psparam_a[.DEFAULT = PSDEFAULT expression_same "int"]], 0)',
    'S_wrong_value = S[.POOLS = [{UNIT n_unit, CONSTANTS ([(PCONSTANT (pcpath_a ++ [PCFIELD 6]) (PINT 7))])}]]',
    '$compiled_read(S_wrong_value, porigin_a) = (PINT 7)',
    '~$lossy_optional_integer_tail(S_wrong_value, pfunction, [psparam_a], 0)',
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
    '$lookup(psymboltable_global.ENV, $ptascii("xReceive197")) = (n_global)',
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
])

CASES = {'boolean-cast-default-omitted-tail': {
    'source': source,
    'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z]',
    'checks': checks,
}}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
