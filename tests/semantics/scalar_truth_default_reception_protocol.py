#!/usr/bin/env python3
"""Literal scalar truth retains exact omitted-default authority and ownership."""
import base64
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('scalar_truth_default_reception_cases.json')
SOURCES = {}
for row in json.loads(CATALOGUE.read_text()):
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
    SOURCES[row['id']] = row['source']

# Fresh first-VAL front preserves the whole five-default declaration; source0.
full = SOURCES['scalar-truth-precision-modes']
setup = full.index("set_error_handler('warningReceive199');")
start = full.index('$gotReceive199 = valueFirstReceive199(')
end = full.index('$xReceive199 = 1.5;', start)
source = full[:full.index('function referenceFirstReceive199')] + full[setup:end]
assert hashlib.sha256(source.encode()).hexdigest() == '81c82e89563626fea8c802285253070aa719490439169338806f9c237d580ed8'

metadata_index = 0
fixed_metadata = None
def node(constructor, *children):
    global metadata_index
    metadata_index += 1
    metadata = fixed_metadata or f'metadata_case_{metadata_index}'
    return constructor + ''.join(f' ({child})' for child in children) + ' ' + metadata


def integer(value):
    return node('NScalarInt', f'INTEGER {value}')


def constant(name, qualified=False):
    payload = base64.b64encode(name.encode()).decode()
    return node('NExprConstFetch', node('NNameFullyQualified' if qualified else 'NName', f'BYTES "{payload}"'))


def string(value):
    return node('NScalarString', f'BYTES "{base64.b64encode(value.encode()).decode()}"')


def floating(bits):
    return node('NScalarFloat', f'FLOAT "{bits}"')


def cast(child):
    return node('NExprCastInt', child)


def add(left, right):
    return node('NExprBinaryOpPlus', left, right)


def binary(constructor, left, right):
    return node('NExprBinaryOp' + constructor, left, right)


def conditional(cond, yes, no):
    return node('NExprTernary', cond, yes, no)


patterns = [
    node('NExprUnaryMinus', conditional(string('0'), constant('UnselectedReceive199'), integer(7))),
    cast(conditional(string(''), 'ABSENT', string('-11tail'))),
    binary('Plus', integer(13), cast(binary('LogicalXor',
        binary('BooleanAnd', string('00'), string('\0')),
        binary('BooleanAnd', node('NExprBooleanNot', string('0')),
                node('NExprUnaryMinus', node('NScalarFloat', 'FLOAT "3fe0000000000000"')))))),
    conditional(node('NExprUnaryPlus', node('NExprUnaryMinus', node('NScalarFloat', 'FLOAT "0000000000000000"'))),
            constant('UnselectedReceive199'), cast(conditional(string('1'), node('NExprUnaryMinus', node('NScalarFloat', 'FLOAT "43e0000000000000"')), constant('UnselectedReceive199')))),
    cast(conditional(binary('BooleanAnd', node('NExprUnaryPlus', node('NScalarFloat', 'FLOAT "7ff0000000000000"')),
                  binary('BooleanOr', node('NExprUnaryMinus', node('NScalarFloat', 'FLOAT "3fe0000000000000"')), string('0'))),
                 string('999999999999999999999999'), constant('UnselectedReceive199'))),
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
fixed_metadata = 'metadata_a'
checks.extend([
    '$lossy_optional_integer_header(S, pfunction, pfunction.SIGNATURE.PARAMETERS, 0)',
    'expression_a = NExprUnaryMinus expression_select_a metadata_a',
    'expression_select_a = NExprTernary expression_string_zero expression_unknown expression_seven metadata_select_a',
    '$lossy_optional_integer_condition(plenv_source, expression_string_zero) = (false)',
    '$lossy_optional_integer_cast_leaf(plenv_source, expression_select_a) = (expression_seven)',
    'expression_b = NExprCastInt expression_short_b metadata_b',
    'expression_short_b = NExprTernary expression_empty ABSENT expression_string_b metadata_short_b',
    '$lossy_optional_integer_cast_leaf(plenv_source, expression_short_b) = (expression_string_b)',
    'expression_c = NExprBinaryOpPlus expression_thirteen expression_cast_c metadata_c',
    'expression_cast_c = NExprCastInt expression_xor metadata_cast_c',
    '$lossy_optional_integer_condition(plenv_source, expression_xor) = (false)',
    'expression_d = NExprTernary expression_signed_zero expression_unknown_d expression_cast_d metadata_d',
    '$lossy_optional_integer_float_literal(expression_signed_zero) = ($hex_bits("8000000000000000", 0))',
    '$lossy_optional_integer_condition(plenv_source, expression_signed_zero) = (false)',
    'expression_e = NExprCastInt expression_select_e metadata_e',
    'expression_select_e = NExprTernary expression_inf_and expression_string_e expression_unknown_e metadata_select_e',
    '$lossy_optional_integer_condition(plenv_source, expression_inf_and) = (true)',
    '$lossy_optional_integer_cast_leaf(plenv_source, expression_select_e) = (expression_string_e)',
    'plenv_alias = plenv_source[.CONSTANTS = [($ptascii("true"), $ptascii("false"))]]',
    '$lossy_optional_integer_header(S, pfunction[.ENV = plenv_alias], pfunction.SIGNATURE.PARAMETERS, 0)',
    'expression_same = NExprUnaryMinus expression_seven metadata_a',
    '$lossy_optional_integer_default_in(plenv_source, expression_same) = ($(-7))',
    '~$lossy_optional_integer_tail(S, pfunction, [psparam_a[.DEFAULT = PSDEFAULT expression_same "int"]], 0)',
    'pfunction.DEFAULTS = [pdefault_a, pdefault_b, pdefault_c, pdefault_d, pdefault_e]',
    '~$lossy_optional_integer_tail(S, pfunction[.DEFAULTS = [pdefault_a, pdefault_b[.KIND = PDDEFERRED], pdefault_c, pdefault_d, pdefault_e]], [psparam_b], 1)',
    'S_wrong_value = S[.POOLS = [{UNIT n_unit, CONSTANTS ([(PCONSTANT (pcpath_b ++ [PCFIELD 6]) (PINT 11))])}]]',
    '$compiled_read(S_wrong_value, porigin_b) = (PINT 11)',
    '~$lossy_optional_integer_tail(S_wrong_value, pfunction, [psparam_b], 1)',
])
# Byte truth is exact, including decoded NUL and multi-byte zero spellings.
for value, expected in [('', 'false'), ('0', 'false'), ('00', 'true'), ('\0', 'true'), ('0\0', 'true'), ('0.0', 'true')]:
    checks.append(f'$lossy_optional_integer_condition(plenv_source, {string(value)}) = ({expected})')
for bits, expected in [
    ('0000000000000000', 'false'), ('8000000000000000', 'false'),
    ('0000000000000001', 'true'), ('8000000000000001', 'true'),
    ('3fe0000000000000', 'true'), ('bfe0000000000000', 'true'),
    ('7ff0000000000000', 'true'), ('fff0000000000000', 'true'),
]:
    value = floating(bits)
    checks.append(f'$lossy_optional_integer_condition(plenv_source, {value}) = ({expected})')
for bits in ['7ff8000000000000', 'fff8000000000000']:
    checks.append(f'$lossy_optional_integer_condition(plenv_source, {floating(bits)}) = eps')
# Cover the affected old193/197/198 expectations without replaying old actors.
for cond in [string('1'), node('NScalarFloat', 'FLOAT "3ff0000000000000"')]:
    checks.append(f'$lossy_optional_integer_default_in(plenv_source, {cast(conditional(cond, integer(7), integer(0)))}) = (7)')
checks.append(f'$lossy_optional_integer_default_in(plenv_source, {cast(node("NExprBooleanNot", string("0")))}) = (1)')
for value in [
    binary('Concat', string(''), string('0')),
    binary('Plus', node('NScalarFloat', 'FLOAT "3fe0000000000000"'), integer(0)),
    constant('UnselectedReceive199'), node('NExprArray', 'SEQUENCE eps'),
]:
    checks.append(f'$lossy_optional_integer_condition(plenv_source, {value}) = eps')
checks.extend([
    f'$lossy_optional_integer_default_in(plenv_source, {cast(conditional(string("1"), floating("43e0000000000000"), integer(7)))}) = eps',
    f'$lossy_optional_integer_default_in(plenv_source, {cast(conditional(string("0"), constant("UnselectedReceive199"), string("12tail")))}) = (12)',
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
    '$lookup(psymboltable_global.ENV, $ptascii("xReceive199")) = (n_global)',
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
    'S_done = $drive_steps(S_after_4, 2000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    r'~((HCELL n_cell) <- S_done.ALLOCATIONS) /\ ~((HCELL n_b) <- S_done.ALLOCATIONS) /\ ~((HCELL n_c) <- S_done.ALLOCATIONS) /\ ~((HCELL n_d) <- S_done.ALLOCATIONS) /\ ~((HCELL n_e) <- S_done.ALLOCATIONS)',
    'S_done.STORE[n_global] = S.STORE[n_global]',
    '$lookup(S_done.ENV, $ptascii("gotReceive199")) = (n_got)',
    'S_done.STORE[n_got] = DEFINED (PINT 13)',
    r'$call_descriptors_valid(S_done) /\ $heap_valid($heap_graph(S_done))',
])

CASES = {'scalar-truth-default-omitted-tail': {
    'source': source,
    'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z]',
    'checks': checks,
}}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
