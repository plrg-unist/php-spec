#!/usr/bin/env python3
"""Integer comparisons preserve exact defaults, long domains and omitted cells."""
import base64
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('comparison_integer_default_reception_cases.json')
SOURCES = {}
for row in json.loads(CATALOGUE.read_text()):
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
    SOURCES[row['id']] = row['source']

# A fresh first call retains its complete five-default declaration; source credit0.
full = SOURCES['comparison-integer-precision-modes']
setup = full.index("set_error_handler('warningReceive195');")
first_call = full.index('$gotReceive195 = valueFirstReceive195(')
end = full.index('$xReceive195 = 1.5;', first_call)
source = full[:full.index('function referenceFirstReceive195')] + full[setup:end]
assert hashlib.sha256(source.encode()).hexdigest() == 'c4e95f5e610e8dda2cca7dc284f7327ee1c1824b0f130ca45f304d98ab31ac45'

# Distinct occurrence metadata avoids accidental equality between separate leaves.
metadata_index = 0
def node(constructor, *children):
    global metadata_index
    metadata_index += 1
    return constructor + ''.join(f' ({child})' for child in children) + f' metadata_case_{metadata_index}'


def integer(value):
    return node('NScalarInt', f'INTEGER {value}')


def constant(name):
    payload = base64.b64encode(name.encode()).decode()
    return node('NExprConstFetch', node('NName', f'BYTES "{payload}"'))


def minimum():
    return node('NExprBinaryOpPow', node('NExprUnaryMinus', integer(2)), integer(63))


def maximum():
    return node('NExprBitwiseNot', minimum())


patterns = [
    node('NExprTernary',
         node('NExprBinaryOpBooleanAnd',
              node('NExprBinaryOpEqual', node('NExprTernary', constant('TrUe'), integer(3), integer(5)),
                   node('NExprBinaryOpPlus', integer(1), integer(2))),
              node('NExprBinaryOpIdentical', integer(4), node('NExprBinaryOpMul', integer(2), integer(2)))),
         node('NExprBinaryOpPlus', node('NExprUnaryMinus', integer(8)), node('NExprBinaryOpSpaceship', integer(3), integer(2))),
         constant('UnselectedReceive195')),
    node('NExprTernary',
         node('NExprBinaryOpLogicalAnd',
              node('NExprBinaryOpNotEqual', node('NExprUnaryMinus', integer(3)), integer(3)),
              node('NExprBinaryOpNotIdentical', integer(2), integer(3))),
         node('NExprBinaryOpPlus', node('NExprUnaryMinus', integer(11)), node('NExprBinaryOpSpaceship', integer(3), integer(3))),
         constant('UnselectedReceive195')),
    node('NExprTernary', node('NExprBinaryOpSmaller', minimum(), maximum()),
         node('NExprBinaryOpPlus', integer(14), node('NExprBinaryOpSpaceship', integer(2), integer(3))),
         constant('UnselectedReceive195')),
    node('NExprTernary', node('NExprBinaryOpSmallerOrEqual', minimum(), integer(0)),
         minimum(), constant('UnselectedReceive195')),
    node('NExprTernary',
         node('NExprBinaryOpBooleanOr', node('NExprBinaryOpGreater', integer(0), integer(1)),
              node('NExprBinaryOpGreaterOrEqual', maximum(), integer(0))),
         maximum(), constant('UnselectedReceive195')),
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
    'expression_a = NExprTernary expression_condition_a expression_value_a expression_unknown metadata_a',
    'expression_condition_a = NExprBinaryOpBooleanAnd (NExprBinaryOpEqual expression_choice_source expression_sum metadata_equal) expression_identity metadata_and',
    'expression_choice_source = NExprTernary expression_true expression_three expression_five metadata_choice',
    'expression_d = NExprTernary (NExprBinaryOpSmallerOrEqual expression_min expression_zero_d metadata_condition_d) expression_min_d expression_unknown_d metadata_d',
    'expression_e = NExprTernary expression_condition_e expression_max expression_unknown_e metadata_e',
    'expression_zero = NScalarInt (INTEGER 0) metadata_a',
    'expression_one = NScalarInt (INTEGER 1) metadata_a',
    'expression_two = NScalarInt (INTEGER 2) metadata_a',
    'expression_big = NScalarInt (INTEGER 9223372036854775808) metadata_a',
])
predicates = [
    'NExprBinaryOpEqual', 'NExprBinaryOpNotEqual', 'NExprBinaryOpIdentical',
    'NExprBinaryOpNotIdentical', 'NExprBinaryOpSmaller', 'NExprBinaryOpSmallerOrEqual',
    'NExprBinaryOpGreater', 'NExprBinaryOpGreaterOrEqual',
]
less = ('false', 'true', 'false', 'true', 'true', 'true', 'false', 'false')
equal = ('true', 'false', 'true', 'false', 'false', 'true', 'false', 'true')
greater = ('false', 'true', 'false', 'true', 'false', 'false', 'true', 'true')
for left, right, expected, order in [
    ('expression_zero', 'expression_one', less, '$(-1)'),
    ('expression_one', 'expression_one', equal, '0'),
    ('expression_two', 'expression_one', greater, '1'),
    ('expression_min', 'expression_max', less, '$(-1)'),
    ('expression_max', 'expression_min', greater, '1'),
]:
    for constructor, result in zip(predicates, expected):
        checks.append(f'$lossy_optional_integer_condition(plenv_source, {constructor} {left} {right} metadata_a) = ({result})')
    checks.append(f'$lossy_optional_integer_default_in(plenv_source, NExprBinaryOpSpaceship {left} {right} metadata_a) = ({order})')
for constructor in predicates:
    checks.append(f'$lossy_optional_integer_default_in(plenv_source, {constructor} expression_one expression_one metadata_a) = eps')
for constructor in [predicates[0], predicates[1], predicates[4], predicates[6], 'NExprBinaryOpSpaceship']:
    helper = 'default_in' if constructor == 'NExprBinaryOpSpaceship' else 'condition'
    for left, right in [('expression_unknown', 'expression_one'), ('expression_one', 'expression_unknown'),
                        ('expression_big', 'expression_one'), ('expression_one', 'expression_big')]:
        checks.append(f'$lossy_optional_integer_{helper}(plenv_source, {constructor} {left} {right} metadata_a) = eps')
checks.extend([
    'plenv_alias = plenv_source[.CONSTANTS = [($ptascii("TrUe"), $ptascii("false"))]]',
    'expression_choice = NExprTernary expression_true expression_zero expression_two metadata_a',
])
for constructor, rhs, actual, alias in zip(
    predicates, ['expression_zero'] * 4 + ['expression_one'] * 4,
    ['true', 'false', 'true', 'false', 'true', 'true', 'false', 'false'],
    ['false', 'true', 'false', 'true', 'false', 'false', 'true', 'true'],
):
    checks.extend([
        f'$lossy_optional_integer_condition(plenv_source, {constructor} expression_choice {rhs} metadata_a) = ({actual})',
        f'$lossy_optional_integer_condition(plenv_alias, {constructor} expression_choice {rhs} metadata_a) = ({alias})',
    ])
checks.extend([
    '$lossy_optional_integer_default_in(plenv_source, NExprBinaryOpSpaceship expression_choice expression_one metadata_a) = ($(-1))',
    '$lossy_optional_integer_default_in(plenv_alias, NExprBinaryOpSpaceship expression_choice expression_one metadata_a) = (1)',
    '$lossy_optional_integer_default_in(plenv_alias, expression_a) = eps',
    '~$lossy_optional_integer_header(S, pfunction[.ENV = plenv_alias], pfunction.SIGNATURE.PARAMETERS, 0)',
    'expression_same = NExprTernary expression_condition_a expression_value_a expression_one metadata_a',
    '$lossy_optional_integer_default_in(plenv_source, expression_same) = ($(-7))',
    '~$lossy_optional_integer_tail(S, pfunction, [psparam_a[.DEFAULT = PSDEFAULT expression_same "int"]], 0)',
    'S_wrong_value = S[.POOLS = [{UNIT n_unit, CONSTANTS ([(PCONSTANT (pcpath_a ++ [PCFIELD 6]) (PINT 7))])}]]',
    '$compiled_read(S_wrong_value, porigin_a) = (PINT 7)',
    '~$lossy_optional_integer_tail(S_wrong_value, pfunction, [psparam_a], 0)',
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
    '$lookup(psymboltable_global.ENV, $ptascii("xReceive195")) = (n_global)',
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

CASES = {'comparison-default-omitted-tail': {
    'source': source,
    'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z]',
    'checks': checks,
}}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
