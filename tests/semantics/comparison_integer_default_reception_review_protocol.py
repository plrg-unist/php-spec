#!/usr/bin/env python3
"""Right-child comparison environments and named reference-default retirement."""
import base64
import hashlib
import json
from pathlib import Path
import closure_call_protocol as protocol


metadata_index = 0


def node(constructor, *children):
    global metadata_index
    metadata_index += 1
    return constructor + ''.join(f' ({child})' for child in children) + f' metadata_peer_{metadata_index}'


def integer(value):
    return node('NScalarInt', f'INTEGER {value}')


def constant(name):
    return node('NExprConstFetch', node('NName', f'BYTES "{base64.b64encode(name.encode()).decode()}"'))


def unknown():
    return constant('UnselectedReceive195')


def negative(value):
    return node('NExprUnaryMinus', integer(value))


def minimum():
    return node('NExprBinaryOpPow', negative(2), integer(63))


def maximum():
    return node('NExprBitwiseNot', minimum())


def compare(constructor, left, right):
    return node('NExprBinaryOp' + constructor, left, right)


patterns = [
    node('NExprTernary',
         compare('BooleanAnd',
                 compare('Equal', node('NExprTernary', constant('TrUe'), integer(3), integer(5)),
                         compare('Plus', integer(1), integer(2))),
                 compare('Identical', integer(4), compare('Mul', integer(2), integer(2)))),
         compare('Plus', negative(8), compare('Spaceship', integer(3), integer(2))), unknown()),
    node('NExprTernary',
         compare('LogicalAnd', compare('NotEqual', negative(3), integer(3)),
                 compare('NotIdentical', integer(2), integer(3))),
         compare('Plus', negative(11), compare('Spaceship', integer(3), integer(3))), unknown()),
    node('NExprTernary', compare('Smaller', minimum(), maximum()),
         compare('Plus', integer(14), compare('Spaceship', integer(2), integer(3))), unknown()),
    node('NExprTernary', compare('SmallerOrEqual', minimum(), integer(0)), minimum(), unknown()),
    node('NExprTernary',
         compare('BooleanOr', compare('Greater', integer(0), integer(1)),
                 compare('GreaterOrEqual', maximum(), integer(0))), maximum(), unknown()),
]

CATALOGUE = Path(__file__).with_name('comparison_integer_default_reception_cases.json')
rows = json.loads(CATALOGUE.read_text())
assert hashlib.sha256(CATALOGUE.read_bytes()).hexdigest() == 'd416fe1160cb23d559a7d6e90141237652d25048743b73a058f0d5881605962a'
row = next(row for row in rows if row['id'] == 'comparison-integer-precision-modes')
assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
source = row['source']
handler = source[:source.index('function valueFirstReceive195(')]
reference = source[source.index('function referenceReceive195('):source.index("set_error_handler('warningReceive195');")]
setup = source[source.index("set_error_handler('warningReceive195');"):source.index('$gotReceive195 = valueFirstReceive195(')]
start = source.index('$gotReceive195 = referenceReceive195(')
end = source.index('$xReceive195 = 1.5;', start)
# Original five-default declaration, fresh setup and leading REF call only, source0.
leading = handler + reference + setup + source[start:end]
assert hashlib.sha256(leading.encode()).hexdigest() == 'a79bf896bd20b3367967915242e839ca215299c6ae5d9f59597c38b471ee6d0b'

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
    'expression_a = NExprTernary expression_condition_a expression_true_a expression_false_a metadata_a',
    'expression_condition_a = NExprBinaryOpBooleanAnd expression_equal_a expression_identity_a metadata_and_a',
    'expression_equal_a = NExprBinaryOpEqual expression_choice_a expression_sum_a metadata_equal_a',
    'expression_choice_a = NExprTernary expression_true expression_three expression_five metadata_choice_a',
    'expression_true = NExprConstFetch (NName (BYTES "VHJVZQ==") metadata_true_name) metadata_true',
    'expression_same = NExprTernary (NExprBooleanNot (NExprBooleanNot expression_condition_a metadata_a) metadata_a) expression_true_a expression_false_a metadata_a',
    '$lossy_optional_integer_default_in(plenv_source, expression_same) = ($(-7))',
    '~$lossy_optional_integer_tail(S, pfunction, [psparam_a[.DEFAULT = PSDEFAULT expression_same "int"]], 0)',
    'pfunction.DEFAULTS = [pdefault_a, pdefault_b, pdefault_c, pdefault_d, pdefault_e]',
    '~$lossy_optional_integer_tail(S, pfunction[.DEFAULTS = [pdefault_a[.INDEX = 1], pdefault_b, pdefault_c, pdefault_d, pdefault_e]], [psparam_a], 0)',
    '~$lossy_optional_integer_tail(S, pfunction[.DEFAULTS = [pdefault_a[.ORIGIN = porigin_b], pdefault_b, pdefault_c, pdefault_d, pdefault_e]], [psparam_a], 0)',
    '~$lossy_optional_integer_tail(S, pfunction[.DEFAULTS = [pdefault_a[.KIND = PDDEFERRED], pdefault_b, pdefault_c, pdefault_d, pdefault_e]], [psparam_a], 0)',
    'S_wrong_value = S[.POOLS = [{UNIT n_unit, CONSTANTS ([(PCONSTANT (pcpath_a ++ [PCFIELD 6]) (PINT 7))])}]]',
    '$compiled_read(S_wrong_value, porigin_a) = (PINT 7)',
    '~$lossy_optional_integer_tail(S_wrong_value, pfunction, [psparam_a], 0)',
    'plenv_alias = plenv_source[.CONSTANTS = [($ptascii("TrUe"), $ptascii("false"))]]',
    '$lossy_optional_integer_default_in(plenv_alias, expression_a) = eps',
    '~$lossy_optional_integer_header(S, pfunction[.ENV = plenv_alias], pfunction.SIGNATURE.PARAMETERS, 0)',
    'expression_zero = NScalarInt (INTEGER 0) metadata_a',
    'expression_one = NScalarInt (INTEGER 1) metadata_a',
    'expression_two = NScalarInt (INTEGER 2) metadata_a',
    'expression_equal_right = NExprTernary expression_true expression_one expression_two metadata_a',
    'expression_order_right = NExprTernary expression_true expression_zero expression_two metadata_a',
])
for constructor, right, actual, alias in [
    ('Equal', 'expression_equal_right', 'true', 'false'),
    ('Identical', 'expression_equal_right', 'true', 'false'),
    ('NotEqual', 'expression_equal_right', 'false', 'true'),
    ('NotIdentical', 'expression_equal_right', 'false', 'true'),
    ('Smaller', 'expression_order_right', 'false', 'true'),
    ('SmallerOrEqual', 'expression_order_right', 'false', 'true'),
    ('Greater', 'expression_order_right', 'true', 'false'),
    ('GreaterOrEqual', 'expression_order_right', 'true', 'false'),
]:
    expression = f'NExprBinaryOp{constructor} expression_one {right} metadata_a'
    checks.extend([
        f'$lossy_optional_integer_condition(plenv_source, {expression}) = ({actual})',
        f'$lossy_optional_integer_condition(plenv_alias, {expression}) = ({alias})',
    ])
checks.extend([
    '$lossy_optional_integer_default_in(plenv_source, NExprBinaryOpSpaceship expression_one expression_order_right metadata_a) = (1)',
    '$lossy_optional_integer_default_in(plenv_alias, NExprBinaryOpSpaceship expression_one expression_order_right metadata_a) = ($(-1))',
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
    'S.STORE[n_cell] = DEFINED (PFLOAT 4615063718147915776)',
    r'n_cell <- S.REFCELLS /\ $heap_owners($heap_graph(S), HCELL n_cell) = 2',
    '$lossy_mixed_parameter_source_valid(S, LOSSY_MIXED_PARAMETER_RECEIVE porigin 2 n_cell n_bits i z)',
    '$task_nodes(LOSSY_MIXED_PARAMETER_RECEIVE porigin 2 n_cell n_bits i z) = eps',
    'z_hole = $default_parameter_line(S, porigin, 0)',
    'ptask_hole = LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_a n_bits i z_hole',
    'S_hole = S[.STORE[n_a] = DEFINED (PFLOAT n_bits)][.REFCELLS = n_a :: S.REFCELLS][.ORIGIN = ($default_parameter_origin(S, porigin, 0))][.TODO = [ptask_hole]]',
    '$lossy_positional_reference_parameter_ready(S_hole, 0, n_a)',
    '$typed_receive_valid(S_hole[.TODO = [TYPE_RECEIVE porigin 0]][.ORIGIN = (porigin)], porigin, 0)',
    '~$lossy_mixed_parameter_source_valid(S_hole, ptask_hole)',
    'PhpStep: S ~> S_next',
    r'S_next.TODO = [TYPE_RECEIVE porigin 3] /\ S_next.STORE[n_cell] = DEFINED (PINT 1)',
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
    '$lookup(S_done.ENV, $ptascii("gotReceive195")) = (n_got)',
    'S_done.STORE[n_got] = DEFINED (PINT 1)',
    r'$call_descriptors_valid(S_done) /\ $heap_valid($heap_graph(S_done))',
])

CASES = {'comparison-reference-leading': {
    'source': leading,
    'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 2 n_cell n_bits i z]',
    'checks': checks,
}}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
