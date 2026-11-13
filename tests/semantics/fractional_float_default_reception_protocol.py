#!/usr/bin/env python3
"""Raw default formals survive own precision callbacks and throwing retry."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('fractional_float_default_reception_cases.json')
PRIOR = Path(__file__).with_name('quiet_fitting_float_default_reception_cases.json')
SOURCES = {}
for path in (CATALOGUE, PRIOR):
    for row in json.loads(path.read_text()):
        assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
        SOURCES[row['id']] = row['source']

TASK = 'LOSSY_DEFAULT_PARAMETER_RECEIVE porigin 1 n_cell n_bits i z'
INGRESS = 'S.TODO = [ERROR_HANDLER_INVOKE perrorcall] -- if perrorcall.RESUME = ' + TASK
AUTHORITY = [
    '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
    'S.CURRENT = (pcallcontext)',
    r'pcallcontext.FUNCTION = porigin /\ pcallcontext.TARGET = porigin',
    r'pcallcontext.CACHE = eps /\ pcallcontext.WRAPPER = eps /\ pcallcontext.INSTANCE = eps',
    r'pcallcontext.DEFAULTRECEIVE = eps /\ S.CONSTCONTEXT = eps',
    '$parameter_receive_owner(S.CURRENT) = eps',
    'S.PARAMETERRECEIVES = [preceivebirth]',
    r'~preceivebirth.ACTIVE /\ preceivebirth.FUNCTION = porigin /\ preceivebirth.CACHE_OWNER = (CACHE_SHARED)',
    'preceivebirth.ORIGIN = $default_parameter_origin(S,porigin,1)',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_first,psparam_later]',
    'psparam_later.DEFAULT = PSDEFAULT expression_default "deferred"',
    '$default_parameter_origin(S,porigin,1) = PORIGIN n_unit pcpath_parameter',
    'porigin_default = PORIGIN n_unit (pcpath_parameter ++ [PCFIELD 6])',
    '$default_at(pfunction.DEFAULTS,1) = ({INDEX 1,ORIGIN porigin_default,KIND PDDEFERRED})',
    '$origin_node(S.SOURCES,porigin_default) = (expression_default)',
    '$lossy_optional_integer_deferred_value(pfunction.ENV,expression_default) = (PFLOAT 4609434218613702656)',
    '$default_cache_owner(S) = (CACHE_SHARED)',
    '$default_current_cache(S,porigin_default) = ({ORIGIN porigin_default,VALUE PFLOAT 4609434218613702656,CLASS PVSCALAR})',
    r'n_bits = 4609434218613702656 /\ i = 1',
    '$lossy_parameter_snapshot(n_bits) = ((i,ptbytes))',
    'z = $default_parameter_line(S,porigin,1)',
    'S.ORIGIN = ($default_parameter_origin(S,porigin,1))',
    '$lookup(S.ENV,psparam_later.NAME) = (n_cell)',
    'S.STORE[n_cell] = DEFINED (PFLOAT n_bits)',
    r'(HCELL n_cell) <- S.ALLOCATIONS /\ ~(n_cell <- S.REFCELLS)',
    '$heap_owners($heap_graph(S),HCELL n_cell) = 1',
    '$lossy_default_parameter_context(S,pfunction,1,n_bits,z)',
    '$lossy_parameter_ready(S,n_cell,n_bits)',
    '$lossy_default_parameter_source_valid(S,' + TASK + ')',
    '$task_nodes(' + TASK + ') = eps',
    '~$lossy_default_parameter_source_valid(S,LOSSY_DEFAULT_PARAMETER_RECEIVE porigin 1 n_cell n_bits 2 z)',
    '~$lossy_default_parameter_source_valid(S,LOSSY_DEFAULT_PARAMETER_RECEIVE porigin 1 n_cell n_bits i $(z + 100))',
    '~$lossy_default_parameter_source_valid(S[.SOURCES = eps],' + TASK + ')',
    '~$lossy_default_parameter_source_valid(S[.FUNCTIONS = eps],' + TASK + ')',
    'pdefaultcache_good = {ORIGIN porigin_default,VALUE PFLOAT n_bits,CLASS PVSCALAR}',
    'S_wrong_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_good[.VALUE = PINT 1])]',
    '$default_caches_valid(S_wrong_tag,S_wrong_tag.DEFAULTCACHE)',
    '~$lossy_default_parameter_source_valid(S_wrong_tag,' + TASK + ')',
    'S_wrong_bits = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_good[.VALUE = PFLOAT 4612811918334230528])]',
    '~$lossy_default_parameter_source_valid(S_wrong_bits,' + TASK + ')',
    '~$lossy_parameter_ready(S[.STORE[n_cell] = DEFINED (PINT 1)],n_cell,n_bits)',
    '~$lossy_parameter_ready(S[.REFCELLS = S.REFCELLS ++ [n_cell]],n_cell,n_bits)',
    r'$call_descriptors_valid(S) /\ $heap_valid($heap_graph(S)) /\ $default_caches_valid(S,S.DEFAULTCACHE)',
]


def ingress_checks(function, variable, counter, before_bits, final_count):
    return AUTHORITY + [
        f'pfunction.NAME = $ptascii("{function}")',
        r'~psparam_first.BYREF /\ ~psparam_later.BYREF',
        '$lookup(S.ENV,psparam_first.NAME) = (n_first)',
        'S.STORE[n_first] = DEFINED (PINT 1)',
        'perrorcall.SITE = $default_parameter_origin(S,porigin,1)',
        r'perrorcall.LEVEL = 8192 /\ perrorcall.LINE = z /\ perrorcall.MESSAGE = ptbytes',
        'perrorcall.EVENT = DIAGNOSTIC "Deprecated" ptbytes z',
        '$error_call_valid(S,perrorcall)',
        '$call_task_valid(S,ERROR_HANDLER_INVOKE perrorcall)',
        '~$error_call_valid(S,perrorcall[.MESSAGE = $ptascii("forged")])',
        '~$error_call_valid(S,perrorcall[.LEVEL = 2])',
        '~$error_call_valid(S,perrorcall[.SITE = $default_parameter_origin(S,porigin,0)])',
        'S.GLOBALTABLE = (psymboltable_global)',
        f'$lookup(psymboltable_global.ENV,$ptascii("{variable}")) = (n_global)',
        f'S.STORE[n_global] = DEFINED (PFLOAT {before_bits})',
        f'$lookup(psymboltable_global.ENV,$ptascii("{counter}")) = (n_count)',
        'S.STORE[n_count] = DEFINED (PINT 1)',
        'S_budget = $drive_steps(S,0)',
        r'S_budget.COMPLETION = BUDGET /\ S_budget.STORE = S.STORE /\ S_budget.DEFAULTCACHE = S.DEFAULTCACHE',
        '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
        'S_done = $drive_steps(S,3000)',
        r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
        '$default_cache_at(S_done.DEFAULTCACHE,porigin_default) = (pdefaultcache_good)',
        f'$lookup(S_done.ENV,$ptascii("{variable}")) = (n_global)',
        'S_done.STORE[n_global] = DEFINED (PFLOAT 4616752568008179712)',
        f'$lookup(S_done.ENV,$ptascii("{counter}")) = (n_count)',
        f'S_done.STORE[n_count] = DEFINED (PINT {final_count})',
        '~((HCELL n_cell) <- S_done.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_done),HCELL n_cell) = 0',
        r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
    ]


reference = AUTHORITY + [
    'pfunction.NAME = $ptascii("fractionalReference224")',
    r'psparam_first.BYREF /\ psparam_later.BYREF',
    '$call_task_valid(S,' + TASK + ')',
    '~$lossy_default_parameter_candidate(S,pfunction,1,PFLOAT n_bits)',
    '$lossy_default_parameter_source_valid(S[.ERRORHANDLER.CALLBACK = eps],' + TASK + ')',
    '$lookup(S.ENV,psparam_first.NAME) = (n_first)',
    r'n_first <- S.REFCELLS /\ $heap_owners($heap_graph(S),HCELL n_first) = 2',
    'S.STORE[n_first] = DEFINED (PFLOAT 4615063718147915776)',
    'S.GLOBALTABLE = (psymboltable_global)',
    '$lookup(psymboltable_global.ENV,$ptascii("xReference224")) = (n_first)',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'PhpStep: S ~> S_body',
    'S_body.TODO = $call_receive_body(S,pfunction)',
    'S_body.STORE[n_cell] = DEFINED (PINT 1)',
    'S_body.STORE[n_first] = S.STORE[n_first]',
    r'S_body.DEFAULTCACHE = S.DEFAULTCACHE /\ S_body.EVENTS = S.EVENTS',
    r'~(n_cell <- S_body.REFCELLS) /\ $heap_owners($heap_graph(S_body),HCELL n_cell) = 1',
    'S_done = $drive_steps(S_body,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_default) = (pdefaultcache_good)',
    '$lookup(S_done.ENV,$ptascii("xReference224")) = (n_first)',
    'S_done.STORE[n_first] = DEFINED (PINT 2)',
    '$lookup(S_done.ENV,$ptascii("laterReference224")) = (n_supplied)',
    'S_done.STORE[n_supplied] = DEFINED (PINT 9)',
    '~((HCELL n_cell) <- S_done.ALLOCATIONS)',
    '$heap_owners($heap_graph(S_done),HCELL n_cell) = 0',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
]
CASES = {
    'fractional-default-own-ingress': {
        'source': SOURCES['fractional-float-default-precision-control'],
        'stage': INGRESS,
        'checks': ingress_checks('fractionalFloatDefault223', 'xFraction223', 'countFraction223', '4615063718147915776', 2),
    },
    'fractional-default-reference-resume': {
        'source': SOURCES['fractional-float-default-reference-cold-warm'],
        'stage': 'S.TODO = [' + TASK + ']',
        'checks': reference,
    },
    'fractional-default-own-throw-retry': {
        'source': SOURCES['fractional-float-default-handler-throw-retry'],
        'stage': INGRESS,
        'checks': ingress_checks('fractionalThrow224', 'xThrow224', 'countThrow224', '4616752568008179712', 4),
    },
}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE, PRIOR), runner_flags=('--sl',))
