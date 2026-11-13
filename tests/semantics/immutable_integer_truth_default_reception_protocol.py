#!/usr/bin/env python3
"""NINT truth defaults retain raw source, cache and saved receive authority."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('immutable_integer_truth_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']


def authority(function):
    return [
        '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
        f'pfunction.NAME = $ptascii("{function}")',
        'S.CURRENT = (pcallcontext)',
        r'pcallcontext.FUNCTION = porigin /\ pcallcontext.TARGET = porigin',
        '$default_cache_owner(S) = (CACHE_SHARED)',
        '$lossy_optional_integer_header(S,pfunction,pfunction.SIGNATURE.PARAMETERS,0)',
        r'$heap_valid($heap_graph(S)) /\ $call_descriptors_valid(S) /\ $default_caches_valid(S,S.DEFAULTCACHE)',
    ]


def default(index, label, value):
    return [
        f'pfunction.SIGNATURE.PARAMETERS[{index}] = psparam_{label}',
        f'psparam_{label}.DEFAULT = PSDEFAULT expression_{label} "deferred"',
        f'$default_parameter_origin(S,porigin,{index}) = PORIGIN n_unit pcpath_{label}',
        f'porigin_{label} = PORIGIN n_unit (pcpath_{label} ++ [PCFIELD 6])',
        f'$default_at(pfunction.DEFAULTS,{index}) = ({{INDEX {index},ORIGIN porigin_{label},KIND PDDEFERRED}})',
        f'$origin_node(S.SOURCES,porigin_{label}) = (expression_{label})',
        rf'$pool_value(S.POOLS,porigin_{label}) = eps /\ $compiled_read(S,porigin_{label}) = eps',
        f'$lossy_optional_integer_default_in(pfunction.ENV,expression_{label}) = ({value})',
        f'$lossy_optional_integer_deferred_value(pfunction.ENV,expression_{label}) = (PINT {value})',
        f'$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,porigin_{label})',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
    ]


cold = authority('truthDefaults226')
for index, label, value in [(1, 'zero', 17), (2, 'negative', 19), (3, 'not', 23)]:
    cold += default(index, label, value)
    cold.append(f'$default_current_cache(S,porigin_{label}) = eps')
cold += [
    r'pcallcontext.ARGC = 1 /\ pcallcontext.HOLES = eps',
    'S.RESULT = KNOWN (PINT 17)',
    'expression_zero = NExprTernary expression_condition expression_yes expression_no metadata_zero',
    '$lossy_optional_integer_default_in(pfunction.ENV,expression_condition) = eps',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_condition) = (NINT 0)',
    '$lossy_optional_integer_condition(pfunction.ENV,expression_condition) = (false)',
    '$lookup(S.ENV,psparam_zero.NAME) = eps',
    'psparam_zero.BYREF',
    'pfunction.SIGNATURE.PARAMETERS[0] = psparam_first',
    '$lookup(S.ENV,psparam_first.NAME) = (n_first)',
    r'S.STORE[n_first] = DEFINED (PINT 1) /\ n_first <- S.REFCELLS',
    'pdefaultcache_zero = {ORIGIN porigin_zero,VALUE PINT 17,CLASS PVSCALAR}',
    'S_wrong = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_zero[.VALUE = PINT 18])]',
    '~$lossy_optional_integer_deferred(S_wrong,pfunction,1)',
    'plenv_wrong = pfunction.ENV[.NAMESPACE = $ptascii("Unknown226")]',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,porigin_zero)',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'PhpStep: S ~> S_zero',
    'S_zero.TODO = [TYPE_RECEIVE porigin 2]',
    '$lookup(S_zero.ENV,psparam_zero.NAME) = (n_zero)',
    'S_zero.STORE[n_zero] = DEFINED (PINT 17)',
    r'~(n_zero <- S_zero.REFCELLS) /\ $heap_owners($heap_graph(S_zero),HCELL n_zero) = 1',
    '$default_current_cache(S_zero,porigin_zero) = (pdefaultcache_zero)',
    'S_zero.EVENTS = S.EVENTS',
    'S_done = $drive_steps(S_zero,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_zero) = (pdefaultcache_zero)',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_negative) = ({ORIGIN porigin_negative,VALUE PINT 19,CLASS PVSCALAR})',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_not) = ({ORIGIN porigin_not,VALUE PINT 23,CLASS PVSCALAR})',
    r'~((HCELL n_zero) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_zero) = 0',
    '$lookup(S_done.ENV,$ptascii("xTruth226")) = (n_first)',
    'S_done.STORE[n_first] = DEFINED (PINT 2)',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
]

named = authority('lazyDefaults226')
for index, label, value in [(1, 'or', 29), (2, 'and', 31), (3, 'cast', 41)]:
    named += default(index, label, value)
    named += [
        f'$default_current_cache(S,porigin_{label}) = ({{ORIGIN porigin_{label},VALUE PINT {value},CLASS PVSCALAR}})',
        f'$lookup(S.ENV,psparam_{label}.NAME) = (n_{label})',
        f'S.STORE[n_{label}] = DEFINED (PINT {value})',
    ]
named += [
    r'pcallcontext.ARGC = 5 /\ pcallcontext.HOLES = [1,2,3]',
    r'n_bits = 4609434218613702656 /\ i = 1',
    'z = $default_parameter_line(S,porigin,0)',
    'pfunction.SIGNATURE.PARAMETERS[0] = psparam_first',
    '~psparam_first.BYREF',
    '$lookup(S.ENV,psparam_first.NAME) = (n_cell)',
    'S.STORE[n_cell] = DEFINED (PFLOAT n_bits)',
    r'~(n_cell <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_cell) = 1',
    'S.GLOBALTABLE = (psymboltable_global)',
    '$lookup(psymboltable_global.ENV,$ptascii("xLazy226")) = (n_global)',
    r'n_global =/= n_cell /\ S.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    '$lossy_mixed_parameter_source_valid(S,LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z)',
    '$lossy_mixed_parameter_ready(S,0,n_cell,n_bits)',
    '$call_task_valid(S,LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z)',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'PhpStep: S ~> S_first',
    r'S_first.TODO = [TYPE_RECEIVE porigin 1] /\ S_first.STORE[n_cell] = DEFINED (PINT 1)',
    r'S_first.DEFAULTCACHE = S.DEFAULTCACHE /\ S_first.STORE[n_global] = S.STORE[n_global]',
    'S_done = $drive_steps(S_first,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    'S_done.DEFAULTCACHE = S.DEFAULTCACHE',
    '$lookup(S_done.ENV,$ptascii("xLazy226")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    r'~((HCELL n_cell) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_cell) = 0',
    r'~((HCELL n_or) <- S_done.ALLOCATIONS) /\ ~((HCELL n_and) <- S_done.ALLOCATIONS) /\ ~((HCELL n_cast) <- S_done.ALLOCATIONS)',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
]

CASES = {
    'immutable-integer-truth-cold-bind': {'source': ROWS['immutable-integer-truth-default-cold-warm']['source'], 'stage': 'S.TODO = [DEFAULT_BIND porigin 1]', 'checks': cold},
    'immutable-integer-truth-lazy-named': {'source': ROWS['immutable-integer-truth-default-lazy-named']['source'], 'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z]', 'checks': named},
}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
