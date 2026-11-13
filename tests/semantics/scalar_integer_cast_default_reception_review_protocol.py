#!/usr/bin/env python3
"""Scalar-cast source authority, final signed bits and reference retirement."""
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


def negative(value):
    return node('NExprUnaryMinus', integer(value))


def minimum():
    return node('NExprBinaryOpPow', negative(2), integer(63))


def compare(constructor, left, right):
    return node('NExprBinaryOp' + constructor, left, right)


def string(value):
    return node('NScalarString', f'BYTES "{base64.b64encode(value.encode()).decode()}"')


def cast(child):
    return node('NExprCastInt', child)


def fully_qualified(name):
    return node('NExprConstFetch', node('NNameFullyQualified', f'BYTES "{base64.b64encode(name.encode()).decode()}"'))


patterns = [
    cast(node('NExprUnaryMinus', node('NExprUnaryPlus', node('NScalarFloat', 'FLOAT "401f000000000000"')))),
    cast(string('-11tail')),
    compare('Plus',
            compare('Plus',
                    compare('Plus', compare('Plus', cast(constant('TrUe')), cast(fully_qualified('FaLsE'))),
                            cast(constant('null'))), cast(string('12'))), cast(string('nonnumeric'))),
    cast(minimum()),
    cast(string('999999999999999999999999')),
]

CATALOGUE = Path(__file__).with_name('scalar_integer_cast_default_reception_cases.json')
rows = json.loads(CATALOGUE.read_text())
assert hashlib.sha256(CATALOGUE.read_bytes()).hexdigest() == '871237c0b2ee69809ac5f7210cf7a74cf0a918a0675673e98b2048b72f43d047'
row = next(row for row in rows if row['id'] == 'scalar-integer-cast-precision-modes')
assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
source = row['source']
handler = source[:source.index('function valueFirstReceive196(')]
reference = source[source.index('function referenceReceive196('):source.index("set_error_handler('warningReceive196');")]
setup = source[source.index("set_error_handler('warningReceive196');"):source.index('$gotReceive196 = valueFirstReceive196(')]
start = source.index('$gotReceive196 = referenceReceive196(')
end = source.index('$xReceive196 = 1.5;', start)
# Original five-default declaration, fresh setup and leading REF call only, source0.
leading = handler + reference + setup + source[start:end]
assert hashlib.sha256(leading.encode()).hexdigest() == 'f3622bafcf5984951005dd08b29ad851939e0a1eb049f4fd2afef15efc3c1e45'

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
    'expression_a = NExprCastInt expression_signed_a metadata_a',
    'expression_b = NExprCastInt expression_string_b metadata_b',
    'expression_c = NExprBinaryOpPlus expression_c_twelve expression_nonnumeric metadata_c',
    'expression_c_twelve = NExprBinaryOpPlus expression_c_null expression_twelve metadata_c_twelve',
    'expression_c_null = NExprBinaryOpPlus expression_c_bool expression_null metadata_c_null',
    'expression_c_bool = NExprBinaryOpPlus expression_bare_true expression_fqn_false metadata_c_bool',
    'expression_bare_true = NExprCastInt expression_true metadata_true_cast',
    'expression_true = NExprConstFetch (NName (BYTES "VHJVZQ==") metadata_true_name) metadata_true',
    'expression_e = NExprCastInt expression_string_e metadata_e',
    'plenv_alias = plenv_source[.CONSTANTS = [($ptascii("TrUe"), $ptascii("false"))]]',
    '$lossy_optional_integer_default_in(plenv_alias, expression_c) = (12)',
    '~$lossy_optional_integer_header(S, pfunction[.ENV = plenv_alias], pfunction.SIGNATURE.PARAMETERS, 0)',
    'plenv_false_alias = plenv_source[.CONSTANTS = [($ptascii("FaLsE"), $ptascii("true"))]]',
    '$lossy_optional_integer_default_in(plenv_false_alias, expression_fqn_false) = (0)',
    '$lossy_optional_integer_default_in(plenv_false_alias, expression_c) = (13)',
    'plenv_null_alias = plenv_source[.CONSTANTS = [($ptascii("null"), $ptascii("true"))]]',
    '$lossy_optional_integer_default_in(plenv_null_alias, expression_null) = (1)',
    '$lossy_optional_integer_default_in(plenv_null_alias, expression_c) = (14)',
    '~$lossy_optional_integer_header(S, pfunction[.ENV = plenv_null_alias], pfunction.SIGNATURE.PARAMETERS, 0)',
    'expression_same = NExprCastInt (NScalarString (BYTES "LTExZmlzaA==") metadata_a) metadata_a',
    '$lossy_optional_integer_default_in(plenv_source, expression_same) = ($(-11))',
    '~$lossy_optional_integer_tail(S, pfunction, [psparam_b[.DEFAULT = PSDEFAULT expression_same "int"]], 1)',
    'pfunction.DEFAULTS = [pdefault_a, pdefault_b, pdefault_c, pdefault_d, pdefault_e]',
    '~$lossy_optional_integer_tail(S, pfunction[.DEFAULTS = [pdefault_a, pdefault_b[.INDEX = 0], pdefault_c, pdefault_d, pdefault_e]], [psparam_b], 1)',
    '~$lossy_optional_integer_tail(S, pfunction[.DEFAULTS = [pdefault_a, pdefault_b[.ORIGIN = porigin_c], pdefault_c, pdefault_d, pdefault_e]], [psparam_b], 1)',
    '~$lossy_optional_integer_tail(S, pfunction[.DEFAULTS = [pdefault_a, pdefault_b[.KIND = PDDEFERRED], pdefault_c, pdefault_d, pdefault_e]], [psparam_b], 1)',
    'S_wrong_value = S[.POOLS = [{UNIT n_unit, CONSTANTS ([(PCONSTANT (pcpath_b ++ [PCFIELD 6]) (PINT 11))])}]]',
    '$compiled_read(S_wrong_value, porigin_b) = (PINT 11)',
    '~$lossy_optional_integer_tail(S_wrong_value, pfunction, [psparam_b], 1)',
    'expression_large = NScalarFloat (FLOAT "43e0000000000000") metadata_a',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt expression_large metadata_a) = eps',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt (NExprUnaryMinus expression_large metadata_a) metadata_a) = ($(-9223372036854775808))',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt (NExprUnaryPlus (NExprUnaryMinus expression_large metadata_a) metadata_a) metadata_a) = ($(-9223372036854775808))',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt (NExprUnaryMinus (NExprUnaryMinus expression_large metadata_a) metadata_a) metadata_a) = eps',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt (NScalarFloat (FLOAT "7ff0000000000000") metadata_a) metadata_a) = eps',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt (NScalarFloat (FLOAT "7ff8000000000000") metadata_a) metadata_a) = eps',
])
for text, expected in [('1e999', '0'), ('-999999999999999999999999', '$(-9223372036854775808)')]:
    payload = base64.b64encode(text.encode()).decode()
    checks.append(f'$lossy_optional_integer_default_in(plenv_source, NExprCastInt (NScalarString (BYTES "{payload}") metadata_a) metadata_a) = ({expected})')
checks.extend([
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt (NExprBinaryOpConcat expression_string_b (NScalarString (BYTES "") metadata_a) metadata_a) metadata_a) = eps',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt (NExprBinaryOpPlus (NScalarFloat (FLOAT "401f000000000000") metadata_a) (NScalarFloat (FLOAT "0000000000000000") metadata_a) metadata_a) metadata_a) = eps',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastInt (NExprBinaryOpEqual (NScalarInt (INTEGER 1) metadata_a) (NScalarInt (INTEGER 1) metadata_a) metadata_a) metadata_a) = (1)',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastBool expression_b metadata_a) = eps',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastDouble expression_b metadata_a) = eps',
    '$lossy_optional_integer_default_in(plenv_source, NExprCastString expression_b metadata_a) = eps',
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
    '$lookup(S_done.ENV, $ptascii("gotReceive196")) = (n_got)',
    'S_done.STORE[n_got] = DEFINED (PINT 1)',
    r'$call_descriptors_valid(S_done) /\ $heap_valid($heap_graph(S_done))',
])

CASES = {'scalar-cast-reference-leading': {
    'source': leading,
    'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 2 n_cell n_bits i z]',
    'checks': checks,
}}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
