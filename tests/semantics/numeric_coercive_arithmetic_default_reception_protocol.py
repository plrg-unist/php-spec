#!/usr/bin/env python3
"""Quiet arithmetic caches precede BYREF reception and throwing precision callbacks."""
import base64
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('numeric_coercive_arithmetic_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']


def authority(function, parameters, index):
    task = f'LOSSY_DEFAULT_PARAMETER_RECEIVE porigin {index} n_cell n_bits i z'
    return [
        '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
        f'pfunction.NAME = $ptascii("{function}")',
        f'pfunction.SIGNATURE.PARAMETERS = [{parameters}]',
        'S.CURRENT = (pcallcontext)',
        r'pcallcontext.FUNCTION = porigin /\ pcallcontext.TARGET = porigin',
        r'pcallcontext.ARGC = 1 /\ pcallcontext.HOLES = eps /\ pcallcontext.CACHE = eps',
        r'pcallcontext.DEFAULTRECEIVE = eps /\ S.CONSTCONTEXT = eps',
        '$parameter_receive_owner(S.CURRENT) = eps',
        '$default_cache_owner(S) = (CACHE_SHARED)',
        'psparam_later.DEFAULT = PSDEFAULT expression_later "deferred"',
        f'$default_parameter_origin(S,porigin,{index}) = PORIGIN n_unit pcpath_later',
        'porigin_later = PORIGIN n_unit (pcpath_later ++ [PCFIELD 6])',
        f'$default_at(pfunction.DEFAULTS,{index}) = ({{INDEX {index},ORIGIN porigin_later,KIND PDDEFERRED}})',
        '$origin_node(S.SOURCES,porigin_later) = (expression_later)',
        r'$pool_value(S.POOLS,porigin_later) = eps /\ $compiled_read(S,porigin_later) = eps',
        '$lossy_optional_integer_default_in(pfunction.ENV,expression_later) = eps',
        '$lossy_optional_integer_numeric(pfunction.ENV,expression_later) = (NFLOAT 4612811918334230528)',
        '$lossy_optional_integer_deferred_value(pfunction.ENV,expression_later) = (PFLOAT 4612811918334230528)',
        '$typed_weak(["int"],PFLOAT 4612811918334230528) = TYPEINTEGER (PFLOAT 4612811918334230528)',
        '$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,porigin_later)',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        'pdefaultcache_later = {ORIGIN porigin_later,VALUE PFLOAT 4612811918334230528,CLASS PVSCALAR}',
        '$default_current_cache(S,porigin_later) = (pdefaultcache_later)',
        r'n_bits = 4612811918334230528 /\ i = 2',
        '$lossy_parameter_snapshot(n_bits) = ((i,ptbytes))',
        f'z = $default_parameter_line(S,porigin,{index})',
        f'S.ORIGIN = ($default_parameter_origin(S,porigin,{index}))',
        '$lookup(S.ENV,psparam_later.NAME) = (n_cell)',
        'S.STORE[n_cell] = DEFINED (PFLOAT n_bits)',
        r'(HCELL n_cell) <- S.ALLOCATIONS /\ ~(n_cell <- S.REFCELLS)',
        '$heap_owners($heap_graph(S),HCELL n_cell) = 1',
        '$lookup(S.ENV,psparam_first.NAME) = (n_first)',
        r'S.STORE[n_first] = DEFINED (PINT 1) /\ ~(n_first <- S.REFCELLS)',
        f'$lossy_default_parameter_context(S,pfunction,{index},n_bits,z)',
        '$lossy_parameter_ready(S,n_cell,n_bits)',
        '$lossy_default_parameter_source_valid(S,' + task + ')',
        '$task_nodes(' + task + ') = eps',
        f'~$lossy_default_parameter_source_valid(S,LOSSY_DEFAULT_PARAMETER_RECEIVE porigin {index} n_cell n_bits 3 z)',
        f'~$lossy_default_parameter_source_valid(S,LOSSY_DEFAULT_PARAMETER_RECEIVE porigin {index} n_cell n_bits i $(z + 100))',
        '~$lossy_default_parameter_source_valid(S[.SOURCES = eps],' + task + ')',
        '~$lossy_default_parameter_source_valid(S[.FUNCTIONS = eps],' + task + ')',
        'S_wrong_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_later[.VALUE = PINT 2])]',
        '$default_caches_valid(S_wrong_tag,S_wrong_tag.DEFAULTCACHE)',
        '~$lossy_default_parameter_source_valid(S_wrong_tag,' + task + ')',
        'S_wrong_bits = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_later[.VALUE = PFLOAT 4609434218613702656])]',
        '~$lossy_default_parameter_source_valid(S_wrong_bits,' + task + ')',
        '~$lossy_parameter_ready(S[.STORE[n_cell] = DEFINED (PINT 2)],n_cell,n_bits)',
        '~$lossy_parameter_ready(S[.REFCELLS = S.REFCELLS ++ [n_cell]],n_cell,n_bits)',
        r'$call_descriptors_valid(S) /\ $heap_valid($heap_graph(S)) /\ $default_caches_valid(S,S.DEFAULTCACHE)',
        'S_budget = $drive_steps(S,0)',
        'S_budget = S[.COMPLETION = BUDGET]',
        '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    ]


cold = authority('arithmeticDefaults241', 'psparam_first,psparam_sum,psparam_difference,psparam_product,psparam_exact,psparam_later', 5)
cold.extend([
    r'~psparam_first.BYREF /\ ~psparam_sum.BYREF /\ ~psparam_difference.BYREF /\ ~psparam_product.BYREF /\ ~psparam_exact.BYREF /\ psparam_later.BYREF',
    '$call_task_valid(S,LOSSY_DEFAULT_PARAMETER_RECEIVE porigin 5 n_cell n_bits i z)',
    'expression_later = NExprBinaryOpDiv expression_total expression_string metadata_later',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_total) = (NINT 5)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_string) = eps',
    '$lossy_optional_integer_string_in(pfunction.ENV,expression_string) = ([50])',
    '$coerce_number(PSTRING ([50])) = COERCED (NINT 2) false',
    '$lossy_optional_integer_quiet_operand(pfunction.ENV,expression_total) = (NINT 5)',
    '$lossy_optional_integer_quiet_operand(pfunction.ENV,expression_string) = (NINT 2)',
    '$number_binary(DIVIDE,NINT 5,NINT 2) = NUM (NFLOAT 4612811918334230528)',
])
for index, label, value in [(1, 'sum', 3), (2, 'difference', 1), (3, 'product', 2), (4, 'exact', 2)]:
    cold.extend([
        f'psparam_{label}.DEFAULT = PSDEFAULT expression_{label} "deferred"',
        f'$default_parameter_origin(S,porigin,{index}) = PORIGIN n_unit pcpath_{label}',
        f'porigin_{label} = PORIGIN n_unit (pcpath_{label} ++ [PCFIELD 6])',
        f'$default_at(pfunction.DEFAULTS,{index}) = ({{INDEX {index},ORIGIN porigin_{label},KIND PDDEFERRED}})',
        f'$origin_node(S.SOURCES,porigin_{label}) = (expression_{label})',
        f'$lossy_optional_integer_numeric(pfunction.ENV,expression_{label}) = (NINT {value})',
        f'$lossy_optional_integer_deferred_value(pfunction.ENV,expression_{label}) = (PINT {value})',
        f'pdefaultcache_{label} = {{ORIGIN porigin_{label},VALUE PINT {value},CLASS PVSCALAR}}',
        f'$default_current_cache(S,porigin_{label}) = (pdefaultcache_{label})',
        f'$lookup(S.ENV,psparam_{label}.NAME) = (n_local_{label})',
        f'S.STORE[n_local_{label}] = DEFINED (PINT {value})',
    ])
cold.extend([
    'S.CODE = [pcode]',
    '~$lossy_default_parameter_source_valid(S[.CODE = ([pcode[.NAMES = eps]])],LOSSY_DEFAULT_PARAMETER_RECEIVE porigin 5 n_cell n_bits i z)',
    'plenv_wrong = pfunction.ENV[.CONSTANTS = ([($ptascii("E_WARNING"),$ptascii("E_ERROR"))])]',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,porigin_later)',
    'PhpStep: S ~> S_bound',
    'S_bound.TODO = $function_tasks(S,pfunction)',
    'S_bound.STORE[n_cell] = DEFINED (PINT 2)',
    r'S_bound.DEFAULTCACHE = S.DEFAULTCACHE /\ S_bound.EVENTS = S.EVENTS',
    'S_done = $drive_steps(S_bound,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_later) = (pdefaultcache_later)',
    r'~((HCELL n_cell) <- S_done.ALLOCATIONS) /\ ~((HCELL n_first) <- S_done.ALLOCATIONS)',
    '$heap_owners($heap_graph(S_done),HCELL n_cell) = 0',
    '$lookup(S_done.ENV,$ptascii("xArithmetic241")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
])
for label in ('sum', 'difference', 'product', 'exact'):
    cold.append(f'$default_cache_at(S_done.DEFAULTCACHE,porigin_{label}) = (pdefaultcache_{label})')

throwing = authority('arithmeticThrow241', 'psparam_first,psparam_later', 1)
throwing.extend([
    r'~psparam_first.BYREF /\ ~psparam_later.BYREF',
    'expression_later = NExprBinaryOpMinus expression_string expression_one metadata_later',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_string) = eps',
    '$lossy_optional_integer_string_in(pfunction.ENV,expression_string) = ([51,46,53])',
    '$coerce_number(PSTRING ([51,46,53])) = COERCED (NFLOAT 4615063718147915776) false',
    '$lossy_optional_integer_quiet_operand(pfunction.ENV,expression_string) = (NFLOAT 4615063718147915776)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_one) = (NINT 1)',
    '$number_binary(SUBTRACT,NFLOAT 4615063718147915776,NINT 1) = NUM (NFLOAT 4612811918334230528)',
    'perrorcall.SITE = $default_parameter_origin(S,porigin,1)',
    r'perrorcall.LEVEL = 8192 /\ perrorcall.LINE = z /\ perrorcall.MESSAGE = ptbytes',
    'perrorcall.EVENT = DIAGNOSTIC "Deprecated" ptbytes z',
    '$error_call_valid(S,perrorcall)',
    '$call_task_valid(S,ERROR_HANDLER_INVOKE perrorcall)',
    '~$error_call_valid(S,perrorcall[.LEVEL = 2])',
    '~$error_call_valid(S,perrorcall[.MESSAGE = $ptascii("forged")])',
    'S.GLOBALTABLE = (psymboltable_global)',
    '$lookup(psymboltable_global.ENV,$ptascii("countThrow241")) = (n_count)',
    'S.STORE[n_count] = DEFINED (PINT 1)',
    '$lookup(psymboltable_global.ENV,$ptascii("xThrow241")) = (n_global)',
    'S.STORE[n_global] = DEFINED (PFLOAT 4616752568008179712)',
    '$lookup(psymboltable_global.ENV,$ptascii("result241")) = (n_result)',
    'S.STORE[n_result] = DEFINED (PINT 99)',
    'S_done = $drive_steps(S,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_later) = (pdefaultcache_later)',
    '$lookup(S_done.ENV,$ptascii("countThrow241")) = (n_count)',
    'S_done.STORE[n_count] = DEFINED (PINT 4)',
    '$lookup(S_done.ENV,$ptascii("result241")) = (n_result)',
    'S_done.STORE[n_result] = DEFINED (PINT 2)',
    '$lookup(S_done.ENV,$ptascii("xThrow241")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4616752568008179712)',
    r'~((HCELL n_cell) <- S_done.ALLOCATIONS) /\ ~((HCELL n_first) <- S_done.ALLOCATIONS)',
    '$heap_owners($heap_graph(S_done),HCELL n_cell) = 0',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
])


def constant(name):
    text = base64.b64encode(name.encode()).decode()
    return f'NExprConstFetch (NName (BYTES "{text}") eps) eps'


def string(text):
    text = base64.b64encode(text.encode()).decode()
    return f'NScalarString (BYTES "{text}") eps'


def binary(operator, left, right):
    return f'NExprBinaryOp{operator} ({left}) ({right}) eps'


# Exactly nine changed old author formulas execute in these fresh fixtures.
for suffix in (213, 218):
    throwing.append(f'plenv_old{suffix} = $plempty(false)[.CONSTANTS = [($ptascii("YesReceive{suffix}"),$ptascii("true")),($ptascii("NoReceive{suffix}"),$ptascii("false")),($ptascii("NilReceive{suffix}"),$ptascii("null"))]]')
for expression, result in [(binary('Plus', constant('YesReceive213'), 'NScalarInt (INTEGER 1) eps'), 2),
                           (binary('Mul', string('2'), 'NScalarInt (INTEGER 3) eps'), 6)]:
    throwing.append(f'$lossy_optional_integer_numeric(plenv_old213,{expression}) = (NINT {result})')
for expression in [binary('Plus', constant('true'), 'NScalarInt (INTEGER 1) eps'),
                   binary('Plus', string('1'), 'NScalarInt (INTEGER 1) eps')]:
    throwing.extend([
        f'$lossy_optional_integer_condition($plempty(false),{expression}) = (true)',
        f'$lossy_optional_integer_default_in($plempty(false),NExprCastInt (NExprCastBool ({expression}) eps) eps) = (1)',
    ])
for expression in [binary('Plus', string('1'), 'NScalarInt (INTEGER 1) eps'),
                   binary('Plus', constant('YesReceive218'), 'NScalarInt (INTEGER 1) eps')]:
    throwing.append(f'$lossy_optional_integer_numeric(plenv_old218,NExprCastDouble ({expression}) eps) = (NFLOAT 4611686018427387904)')
throwing.append(f'$lossy_optional_integer_numeric($plempty(false),{binary("Plus",string("2"),constant("E_ERROR"))}) = (NINT 3)')

CASES = {
    'numeric-coercive-arithmetic-fractional-reference-resume': {
        'source': ROWS['numeric-coercive-arithmetic-default-cold-warm']['source'],
        'stage': 'S.TODO = [LOSSY_DEFAULT_PARAMETER_RECEIVE porigin 5 n_cell n_bits i z]',
        'checks': cold,
    },
    'numeric-coercive-arithmetic-fractional-throw-retry': {
        'source': ROWS['numeric-coercive-arithmetic-default-fractional-handler-throw-retry']['source'],
        'stage': 'S.TODO = [ERROR_HANDLER_INVOKE perrorcall] -- if perrorcall.RESUME = LOSSY_DEFAULT_PARAMETER_RECEIVE porigin 1 n_cell n_bits i z',
        'checks': throwing,
    },
}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
