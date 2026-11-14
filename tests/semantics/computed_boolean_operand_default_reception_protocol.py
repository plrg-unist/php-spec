#!/usr/bin/env python3
"""Computed Boolean operands retain raw caches through BYREF and throwing reception."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('computed_boolean_operand_default_reception_cases.json')
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


cold = authority('booleanDefaults242', 'psparam_first,psparam_comparison,psparam_negation,psparam_castPower,psparam_conjunction,psparam_later', 5)
cold.extend([
    r'~psparam_first.BYREF /\ ~psparam_comparison.BYREF /\ ~psparam_negation.BYREF /\ ~psparam_castPower.BYREF /\ ~psparam_conjunction.BYREF /\ psparam_later.BYREF',
    '$call_task_valid(S,LOSSY_DEFAULT_PARAMETER_RECEIVE porigin 5 n_cell n_bits i z)',
    'expression_later = NExprBinaryOpPlus expression_string expression_boolean metadata_later',
    'expression_boolean = NExprBinaryOpIdentical expression_one expression_two metadata_boolean',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_one) = (NINT 1)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_two) = (NINT 2)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_boolean) = eps',
    '$lossy_optional_integer_boolean_shape(expression_boolean)',
    '$lossy_optional_integer_condition(pfunction.ENV,expression_boolean) = (false)',
    '$coerce_number(PBOOL false) = COERCED (NINT 0) false',
    '$lossy_optional_integer_quiet_operand(pfunction.ENV,expression_boolean) = (NINT 0)',
    '$lossy_optional_integer_power_operand(pfunction.ENV,expression_boolean) = (NINT 0)',
    '$lossy_optional_integer_string_in(pfunction.ENV,expression_string) = ([50,46,53])',
    '$coerce_number(PSTRING ([50,46,53])) = COERCED (NFLOAT 4612811918334230528) false',
    '$number_binary(ADD,NFLOAT 4612811918334230528,NINT 0) = NUM (NFLOAT 4612811918334230528)',
])
for index, label, value in [(1, 'comparison', 2), (2, 'negation', 3), (3, 'castPower', 1), (4, 'conjunction', 2)]:
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
    '$lookup(S_done.ENV,$ptascii("xBooleanOperand242")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
])
for label in ('comparison', 'negation', 'castPower', 'conjunction'):
    cold.append(f'$default_cache_at(S_done.DEFAULTCACHE,porigin_{label}) = (pdefaultcache_{label})')

throwing = authority('booleanThrow242', 'psparam_first,psparam_later', 1)
throwing.extend([
    r'~psparam_first.BYREF /\ ~psparam_later.BYREF',
    'expression_later = NExprBinaryOpPlus expression_string expression_boolean metadata_later',
    'expression_boolean = NExprBinaryOpEqual expression_one_left expression_one_right metadata_boolean',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_boolean) = eps',
    '$lossy_optional_integer_boolean_shape(expression_boolean)',
    '$lossy_optional_integer_condition(pfunction.ENV,expression_boolean) = (true)',
    '$coerce_number(PBOOL true) = COERCED (NINT 1) false',
    '$lossy_optional_integer_quiet_operand(pfunction.ENV,expression_boolean) = (NINT 1)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_string) = eps',
    '$lossy_optional_integer_string_in(pfunction.ENV,expression_string) = ([49,46,53])',
    '$coerce_number(PSTRING ([49,46,53])) = COERCED (NFLOAT 4609434218613702656) false',
    '$number_binary(ADD,NFLOAT 4609434218613702656,NINT 1) = NUM (NFLOAT 4612811918334230528)',
    'perrorcall.SITE = $default_parameter_origin(S,porigin,1)',
    r'perrorcall.LEVEL = 8192 /\ perrorcall.LINE = z /\ perrorcall.MESSAGE = ptbytes',
    'perrorcall.EVENT = DIAGNOSTIC "Deprecated" ptbytes z',
    '$error_call_valid(S,perrorcall)',
    '$call_task_valid(S,ERROR_HANDLER_INVOKE perrorcall)',
    '~$error_call_valid(S,perrorcall[.LEVEL = 2])',
    '~$error_call_valid(S,perrorcall[.MESSAGE = $ptascii("forged")])',
    'S.GLOBALTABLE = (psymboltable_global)',
    '$lookup(psymboltable_global.ENV,$ptascii("countThrow242")) = (n_count)',
    'S.STORE[n_count] = DEFINED (PINT 1)',
    '$lookup(psymboltable_global.ENV,$ptascii("xThrow242")) = (n_global)',
    'S.STORE[n_global] = DEFINED (PFLOAT 4616752568008179712)',
    '$lookup(psymboltable_global.ENV,$ptascii("result242")) = (n_result)',
    'S.STORE[n_result] = DEFINED (PINT 99)',
    'S_done = $drive_steps(S,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_later) = (pdefaultcache_later)',
    '$lookup(S_done.ENV,$ptascii("countThrow242")) = (n_count)',
    'S_done.STORE[n_count] = DEFINED (PINT 4)',
    '$lookup(S_done.ENV,$ptascii("result242")) = (n_result)',
    'S_done.STORE[n_result] = DEFINED (PINT 2)',
    '$lookup(S_done.ENV,$ptascii("xThrow242")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4616752568008179712)',
    r'~((HCELL n_cell) <- S_done.ALLOCATIONS) /\ ~((HCELL n_first) <- S_done.ALLOCATIONS)',
    '$heap_owners($heap_graph(S_done),HCELL n_cell) = 0',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
])

CASES = {
    'computed-boolean-operand-fractional-reference-resume': {
        'source': ROWS['computed-boolean-operand-default-cold-warm']['source'],
        'stage': 'S.TODO = [LOSSY_DEFAULT_PARAMETER_RECEIVE porigin 5 n_cell n_bits i z]',
        'checks': cold,
    },
    'computed-boolean-operand-fractional-throw-retry': {
        'source': ROWS['computed-boolean-operand-default-fractional-handler-throw-retry']['source'],
        'stage': 'S.TODO = [ERROR_HANDLER_INVOKE perrorcall] -- if perrorcall.RESUME = LOSSY_DEFAULT_PARAMETER_RECEIVE porigin 1 n_cell n_bits i z',
        'checks': throwing,
    },
}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
