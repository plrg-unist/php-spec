#!/usr/bin/env python3
"""Authentic warm and reentered defaults keep FLOAT caches and integer formals."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('quiet_fitting_float_default_reception_cases.json')
SOURCES = {}
for row in json.loads(CATALOGUE.read_text()):
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
    SOURCES[row['id']] = row['source']

ZERO = '9223372036854775808'
LARGE = '4890909195324358655'
STAGE = (
    'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z]'
    ' -- if $function_at(S.FUNCTIONS,porigin) = (pfunction)'
    ' -- if pfunction.NAME = $ptascii("exactFloatDefaults223")'
    ' -- if pfunction.DEFAULTS = [pdefault_zero,pdefault_large]'
    ' -- if $default_current_cache(S,pdefault_zero.ORIGIN) = (pdefaultcache_zero)'
    f' -- if pdefaultcache_zero.VALUE = PFLOAT {ZERO}'
)
CHECKS = [
    r'n_bits = 4609434218613702656 /\ i = 1',
    'S.CURRENT = (pcallcontext)',
    r'pcallcontext.FUNCTION = porigin /\ pcallcontext.TARGET = porigin',
    r'pcallcontext.ARGC = 1 /\ pcallcontext.HOLES = eps /\ pcallcontext.NAMED = eps',
    r'pcallcontext.CACHE = eps /\ pcallcontext.WRAPPER = eps /\ pcallcontext.INSTANCE = eps',
    '$default_cache_owner(S) = (CACHE_SHARED)',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_first,psparam_zero,psparam_large]',
    r'psparam_first.REQUIRED /\ ~psparam_first.BYREF /\ psparam_zero.BYREF',
    'psparam_zero.DEFAULT = PSDEFAULT expression_zero "deferred"',
    'psparam_large.DEFAULT = PSDEFAULT expression_large "deferred"',
    r'pdefault_zero.INDEX = 1 /\ pdefault_zero.KIND = PDDEFERRED',
    r'pdefault_large.INDEX = 2 /\ pdefault_large.KIND = PDDEFERRED',
    '$default_parameter_origin(S,porigin,1) = PORIGIN n_unit pcpath_zero',
    'pdefault_zero.ORIGIN = PORIGIN n_unit (pcpath_zero ++ [PCFIELD 6])',
    '$origin_node(S.SOURCES,pdefault_zero.ORIGIN) = (expression_zero)',
    '$origin_node(S.SOURCES,pdefault_large.ORIGIN) = (expression_large)',
    f'$lossy_optional_integer_deferred_value(pfunction.ENV,expression_zero) = (PFLOAT {ZERO})',
    f'$lossy_optional_integer_deferred_value(pfunction.ENV,expression_large) = (PFLOAT {LARGE})',
    f'$float_long({ZERO},true) = (0,eps)',
    f'$float_long({LARGE},true) = (9223372036854774784,eps)',
    f'$default_cache_at(S.DEFAULTCACHE,pdefault_zero.ORIGIN) = ({{ORIGIN pdefault_zero.ORIGIN,VALUE PFLOAT {ZERO},CLASS PVSCALAR}})',
    f'$default_cache_at(S.DEFAULTCACHE,pdefault_large.ORIGIN) = ({{ORIGIN pdefault_large.ORIGIN,VALUE PFLOAT {LARGE},CLASS PVSCALAR}})',
    '$lossy_optional_integer_deferred(S,pfunction,1)',
    '$lossy_optional_integer_deferred(S,pfunction,2)',
    '$lossy_optional_integer_header(S,pfunction,pfunction.SIGNATURE.PARAMETERS,0)',
    '$lookup(S.ENV,psparam_first.NAME) = (n_cell)',
    'S.STORE[n_cell] = DEFINED (PFLOAT n_bits)',
    r'~(n_cell <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_cell) = 1',
    r'$lookup(S.ENV,psparam_zero.NAME) = eps /\ $lookup(S.ENV,psparam_large.NAME) = eps',
    'S.GLOBALTABLE = (psymboltable_global)',
    '$lookup(psymboltable_global.ENV,$ptascii("xExact223")) = (n_global)',
    'S.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    '$lossy_mixed_parameter_source_valid(S,LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z)',
    '$lossy_mixed_parameter_ready(S,0,n_cell,n_bits)',
    '$task_nodes(LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z) = eps',
    r'$call_descriptors_valid(S) /\ $heap_valid($heap_graph(S)) /\ $default_caches_valid(S,S.DEFAULTCACHE)',
    'S_budget = $drive_steps(S,0)',
    r'S_budget.COMPLETION = BUDGET /\ S_budget.DEFAULTCACHE = S.DEFAULTCACHE /\ S_budget.STORE = S.STORE',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'PhpStep: S ~> S_first',
    'S_first.TODO = [TYPE_RECEIVE porigin 1]',
    'S_first.STORE[n_cell] = DEFINED (PINT 1)',
    'PhpStep: S_first ~> S_zero_receive',
    'S_zero_receive.TODO = [DEFAULT_RECEIVE porigin 1]',
    'PhpStep: S_zero_receive ~> S_zero',
    'S_zero.TODO = [TYPE_RECEIVE porigin 2]',
    '$lookup(S_zero.ENV,psparam_zero.NAME) = (n_zero)',
    'S_zero.STORE[n_zero] = DEFINED (PINT 0)',
    r'~(n_zero <- S_zero.REFCELLS) /\ $heap_owners($heap_graph(S_zero),HCELL n_zero) = 1',
    r'S_zero.DEFAULTCACHE = S.DEFAULTCACHE /\ S_zero.EVENTS = S.EVENTS',
    'PhpStep: S_zero ~> S_large_receive',
    'S_large_receive.TODO = [DEFAULT_RECEIVE porigin 2]',
    'PhpStep: S_large_receive ~> S_body',
    'S_body.TODO = $call_receive_body(S_large_receive,pfunction)',
    '$lookup(S_body.ENV,psparam_large.NAME) = (n_large)',
    'S_body.STORE[n_large] = DEFINED (PINT 9223372036854774784)',
    r'S_body.DEFAULTCACHE = S.DEFAULTCACHE /\ S_body.EVENTS = S.EVENTS',
    r'$call_descriptors_valid(S_body) /\ $heap_valid($heap_graph(S_body))',
    'S_done = $drive_steps(S_body,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_zero.ORIGIN) = ({{ORIGIN pdefault_zero.ORIGIN,VALUE PFLOAT {ZERO},CLASS PVSCALAR}})',
    f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_large.ORIGIN) = ({{ORIGIN pdefault_large.ORIGIN,VALUE PFLOAT {LARGE},CLASS PVSCALAR}})',
    '$lookup(S_done.ENV,$ptascii("rExact223")) = (n_result)',
    'S_done.STORE[n_result] = DEFINED (PINT 9223372036854774784)',
    '$lookup(S_done.ENV,$ptascii("xExact223")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
]
CASES = {
    'quiet-fitting-float-warm-receive': {
        'source': SOURCES['quiet-fitting-float-default-cold-warm'],
        'stage': STAGE,
        'checks': CHECKS,
    },
    'quiet-fitting-float-reentered-receive': {
        'source': SOURCES['quiet-fitting-float-default-handler-reentry'],
        'stage': STAGE + (
            ' -- if S.GLOBALTABLE = (psymboltable_global)'
            ' -- if $lookup(psymboltable_global.ENV,$ptascii("rExact223")) = eps'
        ),
        'checks': CHECKS,
    },
}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
