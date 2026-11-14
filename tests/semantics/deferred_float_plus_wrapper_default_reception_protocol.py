#!/usr/bin/env python3
"""Emitted Plus composes a phase-certified child before private integer reception."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('deferred_float_plus_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

checks = [
    'S.CURRENT = (pcallcontext)',
    'pcallcontext.FUNCTION = porigin',
    '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
    'pfunction.ENV.NAMESPACE = $ptascii("PlusWrapper253")',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_first,psparam_zero,psparam_last]',
    r'pcallcontext.ARGC = 1 /\ pcallcontext.HOLES = eps',
    r'pcallcontext.CACHE = eps /\ pcallcontext.DEFAULTRECEIVE = eps /\ S.CONSTCONTEXT = eps',
    r'psparam_first.REQUIRED /\ ~psparam_first.BYREF /\ psparam_zero.BYREF /\ ~psparam_last.BYREF',
    '$default_cache_owner(S) = (CACHE_SHARED)',
    '$lossy_optional_integer_header(S,pfunction,pfunction.SIGNATURE.PARAMETERS,0)',
    'S.CODE = [pcode]',
    'psparam_zero.DEFAULT = PSDEFAULT expression_zero "deferred"',
    '$default_parameter_origin(S,porigin,1) = PORIGIN n_unit pcpath_parameter',
    'pcpath_zero = pcpath_parameter ++ [PCFIELD 6]',
    'porigin_zero = PORIGIN n_unit pcpath_zero',
    'porigin_child = PORIGIN n_unit (pcpath_zero ++ [PCFIELD 0])',
    '$default_at(pfunction.DEFAULTS,1) = ({INDEX 1,ORIGIN porigin_zero,KIND PDDEFERRED})',
    '$origin_node(S.SOURCES,porigin_zero) = (expression_zero)',
    'expression_zero = NExprUnaryPlus expression_child metadata_zero',
    '$origin_node(S.SOURCES,porigin_child) = (expression_child)',
    '$code_expression(pcode.EXPRESSIONS,pcpath_zero) = ((z_zero,false))',
    r'$pool_value(S.POOLS,porigin_zero) = eps /\ $compiled_read(S,porigin_zero) = eps',
    '$compiled_redirect(S,porigin_zero) = eps',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_zero) = (NFLOAT 9223372036854775808)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_child) = (NFLOAT 9223372036854775808)',
    '~$lossy_optional_integer_phase_safe(S,pfunction.ENV,porigin_zero)',
    '~$lossy_optional_integer_phase_safe(S,pfunction.ENV,porigin_child)',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_child) = (PFLOAT 0)',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_zero) = (PFLOAT 0)',
    '$lossy_optional_integer_deferred(S,pfunction,1)',
    'pdefaultcache_zero = {ORIGIN porigin_zero,VALUE PFLOAT 0,CLASS PVSCALAR}',
    '$default_current_cache(S,porigin_zero) = (pdefaultcache_zero)',
    '$lookup(S.ENV,psparam_first.NAME) = (n_first)',
    'S.STORE[n_first] = DEFINED (PINT 2)',
    '$lookup(S.ENV,psparam_zero.NAME) = (n_zero)',
    'S.STORE[n_zero] = DEFINED (PINT 0)',
    r'~(n_zero <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_zero) = 1',
    '$lookup(S.ENV,psparam_last.NAME) = (n_last)',
    'S.STORE[n_last] = DEFINED (PINT 7)',
    'S_sign = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_zero[.VALUE = PFLOAT 9223372036854775808])]',
    '$default_caches_valid(S_sign,S_sign.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_sign,pfunction,1)',
    'S_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_zero[.VALUE = PINT 0])]',
    '$default_caches_valid(S_tag,S_tag.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_tag,pfunction,1)',
    'S_code = S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR pcpath_zero z_zero true)] ++ pcode.EXPRESSIONS)]]]',
    '$lossy_optional_integer_deferred_value_at(S_code,pfunction.ENV,porigin_zero) = eps',
    '$lossy_optional_integer_deferred_value_at(S[.CODE = eps],pfunction.ENV,porigin_zero) = eps',
    '$lossy_optional_integer_deferred_value_at(S[.SOURCES = eps],pfunction.ENV,porigin_zero) = eps',
    'S_pool = S[.POOLS = [{UNIT n_unit,CONSTANTS ([(PCONSTANT pcpath_zero (PINT 0))])}]]',
    '$lossy_optional_integer_deferred_value_at(S_pool,pfunction.ENV,porigin_zero) = eps',
    r'$heap_valid($heap_graph(S)) /\ $call_descriptors_valid(S) /\ $default_caches_valid(S,S.DEFAULTCACHE)',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'S_done = $drive_steps(S,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_zero) = (pdefaultcache_zero)',
    r'~((HCELL n_zero) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_zero) = 0',
    r'~((HCELL n_first) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_first) = 0',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
]

CASES = {'deferred-plus-wrapper-private-cache': {
    'source': ROWS['deferred-float-plus-wrapper-alias-named-reentry']['source'],
    'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.FUNCTION = porigin '
              '-- if pcallcontext.ARGC = 1 -- if $function_at(S.FUNCTIONS,porigin) = (pfunction) '
              '-- if pfunction.ENV.NAMESPACE = $ptascii("PlusWrapper253") '
              '-- if |pfunction.SIGNATURE.PARAMETERS| = 3 '
              '-- if S.TODO = $function_tasks(S,pfunction)'),
    'checks': checks,
}}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__),CATALOGUE), runner_flags=('--sl',))
