#!/usr/bin/env python3
"""Boolean-to-integer defaults retain raw caches and private reception."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('deferred_boolean_int_cast_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

checks = [
    'S.CURRENT = (pcallcontext)',
    'pcallcontext.FUNCTION = porigin',
    '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
    'pfunction.ENV.NAMESPACE = $ptascii("BoolIntWrapper260")',
    'pfunction.ENV.CONSTANTS = [($ptascii("Base260"),$ptascii("E_WARNING")),($ptascii("One260"),$ptascii("E_ERROR"))]',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_first,psparam_integer,psparam_last]',
    r'pcallcontext.ARGC = 1 /\ pcallcontext.HOLES = eps',
    r'pcallcontext.CACHE = eps /\ pcallcontext.DEFAULTRECEIVE = eps /\ S.CONSTCONTEXT = eps',
    r'psparam_first.REQUIRED /\ ~psparam_first.BYREF /\ psparam_integer.BYREF /\ ~psparam_last.BYREF',
    '$default_cache_owner(S) = (CACHE_SHARED)',
    '$lossy_optional_integer_header(S,pfunction,pfunction.SIGNATURE.PARAMETERS,0)',
    'S.CODE = [pcode]',
    'psparam_integer.DEFAULT = PSDEFAULT expression_integer "deferred"',
    '$default_parameter_origin(S,porigin,1) = PORIGIN n_unit pcpath_parameter',
    'pcpath_integer = pcpath_parameter ++ [PCFIELD 6]',
    'porigin_integer = PORIGIN n_unit pcpath_integer',
    'porigin_bool = PORIGIN n_unit (pcpath_integer ++ [PCFIELD 0])',
    'porigin_child = PORIGIN n_unit (pcpath_integer ++ [PCFIELD 0,PCFIELD 0])',
    '$default_at(pfunction.DEFAULTS,1) = ({INDEX 1,ORIGIN porigin_integer,KIND PDDEFERRED})',
    '$origin_node(S.SOURCES,porigin_integer) = (expression_integer)',
    'expression_integer = NExprCastInt expression_bool metadata_integer',
    '$plstyle(metadata_integer) = 1',
    '$origin_node(S.SOURCES,porigin_bool) = (expression_bool)',
    'expression_bool = NExprCastBool expression_child metadata_bool',
    '$plstyle(metadata_bool) = 1',
    '$origin_node(S.SOURCES,porigin_child) = (expression_child)',
    '$code_expression(pcode.EXPRESSIONS,pcpath_integer) = ((z_integer,false))',
    '$code_expression(pcode.EXPRESSIONS,pcpath_integer ++ [PCFIELD 0]) = ((z_bool,false))',
    r'$pool_value(S.POOLS,porigin_integer) = eps /\ $compiled_read(S,porigin_integer) = eps',
    '$compiled_redirect(S,porigin_integer) = eps',
    '~$lossy_optional_integer_phase_safe(S,pfunction.ENV,porigin_integer)',
    '~$lossy_optional_integer_phase_safe(S,pfunction.ENV,porigin_bool)',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_child) = (PINT $(-3))',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_bool) = (PBOOL true)',
    '$coerce_number(PBOOL true) = COERCED (NINT 1) false',
    '$coerce_number(PBOOL false) = COERCED (NINT 0) false',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_integer) = (PINT 1)',
    '$lossy_optional_integer_deferred(S,pfunction,1)',
    'pdefaultcache_integer = {ORIGIN porigin_integer,VALUE PINT 1,CLASS PVSCALAR}',
    '$default_current_cache(S,porigin_integer) = (pdefaultcache_integer)',
    '$lookup(S.ENV,psparam_first.NAME) = (n_first)',
    'S.STORE[n_first] = DEFINED (PINT 2)',
    '$lookup(S.ENV,psparam_integer.NAME) = (n_integer)',
    'S.STORE[n_integer] = DEFINED (PINT 1)',
    r'~(n_integer <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_integer) = 1',
    '$lookup(S.ENV,psparam_last.NAME) = (n_last)',
    'S.STORE[n_last] = DEFINED (PINT 7)',
    'S_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_integer[.VALUE = PBOOL true])]',
    '$default_caches_valid(S_tag,S_tag.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_tag,pfunction,1)',
    'S_value = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_integer[.VALUE = PINT 0])]',
    '$default_caches_valid(S_value,S_value.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_value,pfunction,1)',
    'S_code = S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR pcpath_integer z_integer true)] ++ pcode.EXPRESSIONS)]]]',
    '$lossy_optional_integer_deferred_value_at(S_code,pfunction.ENV,porigin_bool) = (PBOOL true)',
    '$lossy_optional_integer_deferred_value_at(S_code,pfunction.ENV,porigin_integer) = eps',
    '$pool_at(S.POOLS,n_unit) = (ppool)',
    'S_pool = S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT pcpath_integer (PINT 1))] ++ ppool.CONSTANTS)]]]',
    '$lossy_optional_integer_deferred_value_at(S_pool,pfunction.ENV,porigin_integer) = eps',
    'plenv_wrong = pfunction.ENV[.CONSTANTS = [($ptascii("Base260"),$ptascii("E_ERROR")),($ptascii("One260"),$ptascii("E_ERROR"))]]',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,porigin_integer)',
    '$cast_apply(S,CASTINT,PBOOL true,z_integer) = S[.RESULT = KNOWN (PINT 1)]',
    '$cast_apply(S,CASTINT,PBOOL false,z_integer) = S[.RESULT = KNOWN (PINT 0)]',
    'S_suppressed = S[.REPORTING = 0]',
    '$cast_apply(S_suppressed,CASTINT,PBOOL true,z_integer) = S_suppressed[.RESULT = KNOWN (PINT 1)]',
    '$lossy_optional_integer_deferred_value_at(S_suppressed,pfunction.ENV,porigin_integer) = (PINT 1)',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$lossy_optional_integer_deferred_value_at(S_budget,pfunction.ENV,porigin_integer) = (PINT 1)',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    r'$heap_valid($heap_graph(S)) /\ $call_descriptors_valid(S) /\ $default_caches_valid(S,S.DEFAULTCACHE)',
    'S_done = $drive_steps(S,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_integer) = (pdefaultcache_integer)',
    r'~((HCELL n_integer) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_integer) = 0',
    r'~((HCELL n_first) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_first) = 0',
    r'~((HCELL n_last) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_last) = 0',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
]

CASES = {'deferred-boolean-int-cast-wrapper-private-cache': {
    'source': ROWS['deferred-boolean-int-cast-wrapper-alias-named-reentry']['source'],
    'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.FUNCTION = porigin '
              '-- if pcallcontext.ARGC = 1 -- if $function_at(S.FUNCTIONS,porigin) = (pfunction) '
              '-- if pfunction.ENV.NAMESPACE = $ptascii("BoolIntWrapper260") '
              '-- if |pfunction.SIGNATURE.PARAMETERS| = 3 '
              '-- if S.TODO = $function_tasks(S,pfunction)'),
    'checks': checks,
}}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__),CATALOGUE), runner_flags=('--sl',))
