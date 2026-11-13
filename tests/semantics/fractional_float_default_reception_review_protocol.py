#!/usr/bin/env python3
"""Independent named-hole and registry-reentry default continuation checks."""
import hashlib
import json
from pathlib import Path


def authority(function_name, index):
    task = f'LOSSY_DEFAULT_PARAMETER_RECEIVE porigin {index} n_cell n_bits i z'
    return [
        f'ptask_resume = {task}',
        '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
        f'pfunction.NAME = $ptascii("{function_name}")',
        'S.CURRENT = (pcallcontext)',
        r'pcallcontext.FUNCTION = porigin /\ pcallcontext.TARGET = porigin',
        r'pcallcontext.CACHE = eps /\ pcallcontext.WRAPPER = eps /\ pcallcontext.INSTANCE = eps',
        r'pcallcontext.DEFAULTRECEIVE = eps /\ S.CONSTCONTEXT = eps',
        '$parameter_receive_owner(S.CURRENT) = eps',
        f'pfunction.SIGNATURE.PARAMETERS[{index}] = psparam_later',
        r'~psparam_later.REQUIRED /\ $ptmasks(psparam_later.TYPE) = ["int"]',
        'psparam_later.DEFAULT = PSDEFAULT expression_default "deferred"',
        f'$default_parameter_origin(S,porigin,{index}) = PORIGIN n_unit pcpath_parameter',
        'porigin_default = PORIGIN n_unit (pcpath_parameter ++ [PCFIELD 6])',
        f'$default_at(pfunction.DEFAULTS,{index}) = ({{INDEX {index},ORIGIN porigin_default,KIND PDDEFERRED}})',
        '$origin_node(S.SOURCES,porigin_default) = (expression_default)',
        r'$pool_value(S.POOLS,porigin_default) = eps /\ $compiled_read(S,porigin_default) = eps',
        '$lossy_optional_integer_default_in(pfunction.ENV,expression_default) = eps',
        '$lossy_optional_integer_deferred_value(pfunction.ENV,expression_default) = (PFLOAT 4609434218613702656)',
        r'n_bits = 4609434218613702656 /\ i = 1',
        '$lossy_parameter_snapshot(n_bits) = ((i,ptbytes))',
        f'z = $default_parameter_line(S,porigin,{index})',
        f'S.ORIGIN = ($default_parameter_origin(S,porigin,{index}))',
        '$default_cache_owner(S) = (CACHE_SHARED)',
        'pdefaultcache_good = {ORIGIN porigin_default,VALUE PFLOAT n_bits,CLASS PVSCALAR}',
        '$default_current_cache(S,porigin_default) = (pdefaultcache_good)',
        '$lookup(S.ENV,psparam_later.NAME) = (n_cell)',
        'S.STORE[n_cell] = DEFINED (PFLOAT n_bits)',
        r'(HCELL n_cell) <- S.ALLOCATIONS /\ ~(n_cell <- S.REFCELLS)',
        '$heap_owners($heap_graph(S),HCELL n_cell) = 1',
        '$lossy_parameter_ready(S,n_cell,n_bits)',
        '$lossy_default_parameter_source_valid(S,ptask_resume)',
        '$call_task_valid(S,ptask_resume)',
        '$task_nodes(ptask_resume) = eps',
        f'~$lossy_default_parameter_candidate(S,pfunction,{index},PFLOAT n_bits)',
        r'$heap_valid($heap_graph(S)) /\ $call_descriptors_valid(S) /\ $default_caches_valid(S,S.DEFAULTCACHE)',
    ]


def malformed(index):
    return [
        f'~$lossy_default_parameter_source_valid(S,LOSSY_DEFAULT_PARAMETER_RECEIVE porigin {index} n_cell n_bits 2 z)',
        f'~$lossy_default_parameter_source_valid(S,LOSSY_DEFAULT_PARAMETER_RECEIVE porigin {index} n_cell 4615063718147915776 3 z)',
        f'~$lossy_default_parameter_source_valid(S,LOSSY_DEFAULT_PARAMETER_RECEIVE porigin {index} n_cell n_bits i $(z + 100))',
        '~$lossy_default_parameter_source_valid(S,LOSSY_DEFAULT_PARAMETER_RECEIVE porigin 100 n_cell n_bits i z)',
        '~$lossy_default_parameter_source_valid(S[.ORIGIN = (porigin_default)],ptask_resume)',
        '~$lossy_default_parameter_source_valid(S[.SOURCES = eps],ptask_resume)',
        '~$lossy_default_parameter_source_valid(S[.FUNCTIONS = eps],ptask_resume)',
        '~$lossy_default_parameter_source_valid(S[.ENV = eps],ptask_resume)',
        'S.CODE = [pcode]',
        '~$lossy_default_parameter_source_valid(S[.CODE = ([pcode[.NAMES = eps]])],ptask_resume)',
        'S_unknown = S[.CURRENT = (pcallcontext[.CACHE = (CACHE_SHARED)])]',
        '$default_cache_owner(S_unknown) = eps',
        '~$lossy_default_parameter_source_valid(S_unknown,ptask_resume)',
        'S_wrong_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_good[.VALUE = PINT 1])]',
        '$default_caches_valid(S_wrong_tag,S_wrong_tag.DEFAULTCACHE)',
        '~$lossy_default_parameter_source_valid(S_wrong_tag,ptask_resume)',
        'S_wrong_bits = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_good[.VALUE = PFLOAT 4615063718147915776])]',
        '~$lossy_default_parameter_source_valid(S_wrong_bits,ptask_resume)',
        'S_wrong_class = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_good[.CLASS = PVSTRING false])]',
        '~$lossy_default_parameter_source_valid(S_wrong_class,ptask_resume)',
        'S_duplicate = S[.DEFAULTCACHE = (S.DEFAULTCACHE ++ [pdefaultcache_good])]',
        '~$default_caches_valid(S_duplicate,S_duplicate.DEFAULTCACHE)',
        '~$lossy_default_parameter_source_valid(S_duplicate,ptask_resume)',
        'S_changed = $write_name(S,psparam_later.NAME,PFLOAT 4615063718147915776)',
        '$lossy_default_parameter_source_valid(S_changed,ptask_resume)',
        '~$lossy_parameter_ready(S_changed,n_cell,n_bits)',
        'PhpStep: S_changed ~> S_refused',
        'S_refused = S_changed[.COMPLETION = UNSUPPORTED "lossy deferred default receive continuation"]',
        'S_marked = $reference_cell(S,n_cell)',
        '$lossy_default_parameter_source_valid(S_marked,ptask_resume)',
        '~$lossy_parameter_ready(S_marked,n_cell,n_bits)',
        'PhpStep: S_marked ~> S_marked_refused',
        'S_marked_refused = S_marked[.COMPLETION = UNSUPPORTED "lossy deferred default receive continuation"]',
        'S_cleared = S[.ERRORHANDLER.CALLBACK = eps]',
        '~$error_handler_eligible(S_cleared,8192)',
        '$lossy_default_parameter_source_valid(S_cleared,ptask_resume)',
        '$call_task_valid(S_cleared,ptask_resume)',
        'PhpStep: S_cleared ~> S_cleared_bound',
        'S_cleared_bound.STORE[n_cell] = DEFINED (PINT 1)',
        r'S_cleared_bound.DEFAULTCACHE = S.DEFAULTCACHE /\ S_cleared_bound.EVENTS = S.EVENTS',
    ]


def finish():
    return [
        'S_budget = $drive_steps(S,0)',
        'S_budget = S[.COMPLETION = BUDGET]',
        '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
        'PhpStep: S ~> S_bound',
        'S_bound.STORE[n_cell] = DEFINED (PINT 1)',
        r'S_bound.DEFAULTCACHE = S.DEFAULTCACHE /\ S_bound.EVENTS = S.EVENTS',
        r'S_bound.CURRENT = S.CURRENT /\ S_bound.FRAMES = S.FRAMES',
        'S_bound.ORIGIN = (porigin)',
        r'S_bound.RESULT = KNOWN PNULL /\ S_bound.BASE = BASE_VALUE (KNOWN PNULL)',
        r'~(n_cell <- S_bound.REFCELLS) /\ $heap_owners($heap_graph(S_bound),HCELL n_cell) = 1',
        'S_done = $drive_steps(S_bound,3000)',
        r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
        '$default_cache_at(S_done.DEFAULTCACHE,porigin_default) = (pdefaultcache_good)',
        '~((HCELL n_cell) <- S_done.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_done),HCELL n_cell) = 0',
        r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
    ]


named = authority('fractionalNamed224', 1) + [
    r'pcallcontext.ARGC = 3 /\ pcallcontext.HOLES = [1]',
    '~psparam_later.BYREF',
    'pfunction.SIGNATURE.PARAMETERS[0] = psparam_first',
    'pfunction.SIGNATURE.PARAMETERS[2] = psparam_last',
    '$lookup(S.ENV,psparam_first.NAME) = (n_first)',
    'S.STORE[n_first] = DEFINED (PINT 1)',
    '$lookup(S.ENV,psparam_last.NAME) = (n_last)',
    'S.STORE[n_last] = DEFINED (PINT 8)',
    'S.GLOBALTABLE = (psymboltable_global)',
    '$lookup(psymboltable_global.ENV,$ptascii("xNamed224")) = (n_global)',
    'S.STORE[n_global] = DEFINED (PFLOAT 4616752568008179712)',
    '$lookup(psymboltable_global.ENV,$ptascii("countNamed224")) = (n_count)',
    'S.STORE[n_count] = DEFINED (PINT 2)',
] + malformed(1) + finish() + [
    'S_bound.TODO = [TYPE_RECEIVE porigin 2]',
    r'S_bound.STORE[n_first] = S.STORE[n_first] /\ S_bound.STORE[n_last] = S.STORE[n_last]',
    '$lookup(S_done.ENV,$ptascii("xNamed224")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4616752568008179712)',
    '$lookup(S_done.ENV,$ptascii("countNamed224")) = (n_count)',
    'S_done.STORE[n_count] = DEFINED (PINT 2)',
]

reentry = authority('registryFractional224', 0) + [
    r'pcallcontext.ARGC = 0 /\ pcallcontext.HOLES = eps',
    'psparam_later.BYREF',
    'S.FRAMES = [pframe]',
    'pframe.CONTEXT = eps',
    'S.ERRORHANDLER.CALLBACK = (PSTRING_CARRIER INTERNED_STRING $ptascii("registryReplacementWarning224"))',
    '$error_handler_eligible(S,8192)',
    'S.GLOBALTABLE = (psymboltable_global)',
    '$lookup(psymboltable_global.ENV,$ptascii("outerCount224")) = (n_outer)',
    'S.STORE[n_outer] = DEFINED (PINT 1)',
    '$lookup(psymboltable_global.ENV,$ptascii("replacementCount224")) = (n_replacement)',
    'S.STORE[n_replacement] = DEFINED (PINT 1)',
] + malformed(0) + finish() + [
    'S_bound.TODO = $call_receive_body(S,pfunction)',
    'S_bound.ERRORHANDLER = S.ERRORHANDLER',
    'S_done.ERRORHANDLER = S.ERRORHANDLER',
    '$lookup(S_done.ENV,$ptascii("outerCount224")) = (n_outer)',
    'S_done.STORE[n_outer] = DEFINED (PINT 1)',
    '$lookup(S_done.ENV,$ptascii("replacementCount224")) = (n_replacement)',
    'S_done.STORE[n_replacement] = DEFINED (PINT 2)',
]

CATALOGUE = Path(__file__).with_name('fractional_float_default_reception_cases.json')
rows = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in rows.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
CASES = {
    'fractional-default-named-hole-resume': {
        'source': rows['fractional-float-default-named-hole']['source'],
        'stage': 'S.TODO = [LOSSY_DEFAULT_PARAMETER_RECEIVE porigin 1 n_cell n_bits i z]',
        'checks': named,
    },
    'fractional-default-registry-reentry-resume': {
        'source': rows['fractional-float-default-registry-reentry']['source'],
        'stage': ('S.TODO = [LOSSY_DEFAULT_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z] '
                  '-- if S.FRAMES = pframe :: pframe_tail* -- if pframe.CONTEXT = eps'),
        'checks': reentry,
    },
}

if __name__ == '__main__':
    import closure_call_protocol as protocol
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
