#!/usr/bin/env python3
"""Cold scalar defaults retain cache publication, formal initialization and errors."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('deferred_float_default_type_error_reception_cases.json')
ROWS = json.loads(CATALOGUE.read_text())
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
SOURCE = next(row['source'] for row in ROWS if row['id'] == 'deferred-inf-default-type-error-precision')
FIT_SOURCE = next(row['source'] for row in ROWS if row['id'] == 'fitting-float-default-boundary-control')
INF = '9218868437227405312'
FLOAT = '4609434218613702656'


def stage(task, name):
    return (f'S.TODO = [{task} porigin 0]' if task == 'TYPE_RECEIVE' else f'S.TODO = [{task} porigin 1]') + (
        ' -- if $function_at(S.FUNCTIONS,porigin) = (pfunction)'
        f' -- if pfunction.NAME = $ptascii("{name}")')


authority = [
    'S.CURRENT = (pcallcontext)',
    r'pcallcontext.FUNCTION = porigin /\ pcallcontext.TARGET = porigin',
    r'pcallcontext.CACHE = eps /\ pcallcontext.WRAPPER = eps /\ pcallcontext.INSTANCE = eps',
    r'pcallcontext.RECEIVER = eps /\ pcallcontext.LEXICAL_CLASS = eps /\ pcallcontext.CALLED_CLASS = eps',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_first,psparam_later]',
    r'psparam_first.REQUIRED /\ psparam_first.BYREF /\ $ptmasks(psparam_first.TYPE) = ["int"]',
    r'~psparam_later.REQUIRED /\ ~psparam_later.BYREF /\ ~psparam_later.VARIADIC',
    '$ptmasks(psparam_later.TYPE) = ["int"]',
    'psparam_later.DEFAULT = PSDEFAULT expression_default "deferred"',
    'expression_default = NExprConstFetch name_default metadata_default',
    '$pnresolve(pfunction.ENV,PLCONSTANT,name_default) = PNRESOLVED pnreference',
    r'pnreference.RESOLVED = $ptascii("INF") /\ pnreference.FALLBACK = eps',
    '$default_parameter_origin(S,porigin,1) = PORIGIN n_unit pcpath_parameter',
    'porigin_default = PORIGIN n_unit (pcpath_parameter ++ [PCFIELD 6])',
    '$origin_node(S.SOURCES,porigin_default) = (expression_default)',
    'pfunction.DEFAULTS = [{INDEX 1,ORIGIN porigin_default,KIND PDDEFERRED}]',
    r'$pool_value(S.POOLS,porigin_default) = eps /\ $compiled_read(S,porigin_default) = eps',
    '$lossy_optional_integer_default_in(pfunction.ENV,expression_default) = eps',
    f'$lossy_optional_integer_deferred_value(pfunction.ENV,expression_default) = (PFLOAT {INF})',
    f'$typed_weak(["int"],PFLOAT {INF}) = TYPEREJECT',
    '$lossy_optional_integer_quiet_shape(expression_default)',
    '$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,porigin_default)',
    '$default_cache_owner(S) = (CACHE_SHARED)',
    '$default_current_cache(S,porigin_default) = eps',
    '$default_caches_valid(S,S.DEFAULTCACHE)',
    '$lossy_optional_integer_deferred(S,pfunction,1)',
    '$lossy_optional_integer_header(S,pfunction,pfunction.SIGNATURE.PARAMETERS,0)',
    '~$lossy_optional_integer_deferred(S,pfunction,0)',
    '~$lossy_optional_integer_deferred(S,pfunction,2)',
]
cold = authority + [
    r'pcallcontext.ARGC = 1 /\ pcallcontext.HOLES = eps /\ pcallcontext.NAMED = eps',
    '$lookup(S.ENV,psparam_first.NAME) = (n_cell)',
    fr'S.STORE[n_cell] = DEFINED (PFLOAT {FLOAT}) /\ n_cell <- S.REFCELLS',
    '$heap_owners($heap_graph(S),HCELL n_cell) = 2',
    '$lookup(S.ENV,psparam_later.NAME) = eps',
    'S.GLOBALTABLE = (psymboltable_global)',
    '$lookup(psymboltable_global.ENV,$ptascii("xFuture222")) = (n_cell)',
    'z = $default_parameter_line(S,porigin,0)',
    f'$lossy_mixed_parameter_ready(S,0,n_cell,{FLOAT})',
    '$lossy_mixed_parameter_metadata(S,porigin,0,z)',
    f'$lossy_mixed_parameter_capture(S) = (LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell {FLOAT} 1 z)',
    r'$call_descriptors_valid(S) /\ $heap_valid($heap_graph(S))',
    f'pdefaultcache_good = {{ORIGIN porigin_default,VALUE PFLOAT {INF},CLASS PVSCALAR}}',
    'S_warm = S[.DEFAULTCACHE = S.DEFAULTCACHE ++ [pdefaultcache_good]]',
    '$default_caches_valid(S_warm,S_warm.DEFAULTCACHE)',
    '$lossy_optional_integer_deferred(S_warm,pfunction,1)',
]
for value in ['PINT 0', 'PBOOL false', 'PFLOAT 18442240474082181120', 'PFLOAT 9221120237041090560']:
    cold.append('~$lossy_optional_integer_deferred(S[.DEFAULTCACHE = S.DEFAULTCACHE ++ '
                f'[pdefaultcache_good[.VALUE = {value}]]],pfunction,1)')
cold += [
    '~$lossy_optional_integer_deferred(S_warm[.DEFAULTCACHE = S_warm.DEFAULTCACHE ++ [pdefaultcache_good]],pfunction,1)',
    '~$lossy_optional_integer_deferred(S[.DEFAULTCACHE = S.DEFAULTCACHE ++ [pdefaultcache_good[.CLASS = PVSTRING true]]],pfunction,1)',
    '~$lossy_optional_integer_deferred(S[.CURRENT = eps],pfunction,1)',
    '~$lossy_optional_integer_deferred(S[.CURRENT = (pcallcontext[.CACHE = (CACHE_SHARED)])],pfunction,1)',
    '~$lossy_optional_integer_deferred(S[.CURRENT = (pcallcontext[.CACHE = (CACHE_PRIVATE 0)])],pfunction,1)',
    '~$lossy_optional_integer_deferred(S[.CURRENT = (pcallcontext[.CACHE = (CACHE_CALL 0)])],pfunction,1)',
    '~$lossy_optional_integer_deferred(S[.SOURCES = eps],pfunction,1)',
    '~$lossy_optional_integer_deferred(S[.FUNCTIONS = eps],pfunction,1)',
    'S.CODE = [pcode]',
    '~$lossy_optional_integer_deferred(S[.CODE = [pcode[.NAMES = eps]]],pfunction,1)',
    'S_budget = $drive_steps(S,0)',
    r'S_budget.COMPLETION = BUDGET /\ S_budget.DEFAULTCACHE = S.DEFAULTCACHE /\ S_budget.STORE = S.STORE',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'S_done = $drive_steps(S,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    f'$default_cache_at(S_done.DEFAULTCACHE,porigin_default) = ({{ORIGIN porigin_default,VALUE PFLOAT {INF},CLASS PVSCALAR}})',
    '$lookup(S_done.ENV,$ptascii("xFuture222")) = (n_cell)',
    'S_done.STORE[n_cell] = DEFINED (PINT 1)',
    r'$call_descriptors_valid(S_done) /\ $heap_valid($heap_graph(S_done)) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
]
bind = authority + [
    f'S.RESULT = KNOWN (PFLOAT {INF})',
    '$lookup(S.ENV,psparam_first.NAME) = (n_cell)',
    'S.STORE[n_cell] = DEFINED (PINT 1)',
    '$lookup(S.ENV,psparam_later.NAME) = eps',
    f'$parameter_default_error_candidate(S,pfunction,1,PFLOAT {INF})',
    'PhpStep: S ~> S_throw',
    'S_throw.COMPLETION = THROWN "TypeError" preqbytes z',
    'z = $default_parameter_line(S,porigin,1)',
    r'S_throw.CURRENT = $parameter_receive_end(S).CURRENT /\ S_throw.FRAMES = S.FRAMES',
    f'$default_cache_at(S_throw.DEFAULTCACHE,porigin_default) = ({{ORIGIN porigin_default,VALUE PFLOAT {INF},CLASS PVSCALAR}})',
    '$lookup(S_throw.ENV,psparam_later.NAME) = (n_later)',
    f'S_throw.STORE[n_later] = DEFINED (PFLOAT {INF})',
    '(HCELL n_later) <- S_throw.ALLOCATIONS',
    'S_throw.CONSTCONTEXT = eps',
    'S_done = $drive_steps(S_throw,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    f'$default_cache_at(S_done.DEFAULTCACHE,porigin_default) = ({{ORIGIN porigin_default,VALUE PFLOAT {INF},CLASS PVSCALAR}})',
    '~((HCELL n_later) <- S_done.ALLOCATIONS)',
    '$heap_owners($heap_graph(S_done),HCELL n_later) = 0',
    '$lookup(S_done.ENV,$ptascii("xFuture222")) = (n_cell)',
    'S_done.STORE[n_cell] = DEFINED (PINT 1)',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done)',
]
fit = [
    'pfunction.SIGNATURE.PARAMETERS = [psparam_first,psparam_later]',
    'psparam_later.DEFAULT = PSDEFAULT expression_default "deferred"',
    '$lossy_optional_integer_default_in(pfunction.ENV,expression_default) = eps',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_default) = (NFLOAT 14114281232179134464)',
    '$typed_weak(["int"],PFLOAT 14114281232179134464) = TYPEINTEGER (PFLOAT 14114281232179134464)',
    '$lossy_optional_integer_deferred_value(pfunction.ENV,expression_default) = eps',
    '~$lossy_optional_integer_deferred(S,pfunction,1)',
    '~$lossy_optional_integer_header(S,pfunction,pfunction.SIGNATURE.PARAMETERS,0)',
    '$lossy_mixed_parameter_capture(S) = eps',
    'S_blocked = $drive_steps(S,30)',
    'S_blocked.COMPLETION = UNSUPPORTED "error-handler ingress requires a producer continuation"',
    'S_blocked.DEFAULTCACHE = S.DEFAULTCACHE',
]
CASES = {
    'deferred-error-cold-reference': {'source': SOURCE, 'stage': stage('TYPE_RECEIVE', 'referenceFutureDefault222'), 'checks': cold},
    'deferred-error-bind-before-throw': {'source': SOURCE, 'stage': stage('DEFAULT_BIND', 'referenceFutureDefault222'), 'checks': bind},
    'deferred-error-fitting-control': {'source': FIT_SOURCE, 'stage': stage('TYPE_RECEIVE', 'fitDefault222'), 'checks': fit},
}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
