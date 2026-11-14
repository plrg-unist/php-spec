#!/usr/bin/env python3
"""Arithmetic defaults keep raw phase-aware caches through private int reception."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('deferred_float_arithmetic_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

checks = [
    'S.CURRENT = (pcallcontext)',
    'pcallcontext.FUNCTION = porigin',
    '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
    'pfunction.ENV.NAMESPACE = $ptascii("ArithmeticWrapper254")',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_first,psparam_add,psparam_sub,psparam_mul,psparam_div,psparam_last]',
    r'pcallcontext.ARGC = 1 /\ pcallcontext.HOLES = eps',
    r'pcallcontext.CACHE = eps /\ pcallcontext.DEFAULTRECEIVE = eps /\ S.CONSTCONTEXT = eps',
    r'psparam_first.REQUIRED /\ ~psparam_first.BYREF /\ psparam_add.BYREF /\ ~psparam_sub.BYREF /\ ~psparam_mul.BYREF /\ ~psparam_div.BYREF /\ ~psparam_last.BYREF',
    '$default_cache_owner(S) = (CACHE_SHARED)',
    '$lossy_optional_integer_header(S,pfunction,pfunction.SIGNATURE.PARAMETERS,0)',
    'S.CODE = [pcode]',
    'psparam_add.DEFAULT = PSDEFAULT expression_add "deferred"',
    '$default_parameter_origin(S,porigin,1) = PORIGIN n_unit pcpath_parameter',
    'pcpath_add = pcpath_parameter ++ [PCFIELD 6]',
    'porigin_add = PORIGIN n_unit pcpath_add',
    'porigin_left = PORIGIN n_unit (pcpath_add ++ [PCFIELD 0])',
    'porigin_right = PORIGIN n_unit (pcpath_add ++ [PCFIELD 1])',
    '$default_at(pfunction.DEFAULTS,1) = ({INDEX 1,ORIGIN porigin_add,KIND PDDEFERRED})',
    '$origin_node(S.SOURCES,porigin_add) = (expression_add)',
    '$pfshape(expression_add) = PFBINARY ADD expression_left expression_right',
    '$origin_node(S.SOURCES,porigin_left) = (expression_left)',
    '$origin_node(S.SOURCES,porigin_right) = (expression_right)',
    '$code_expression(pcode.EXPRESSIONS,pcpath_add) = ((z_add,false))',
    r'$pool_value(S.POOLS,porigin_add) = eps /\ $compiled_read(S,porigin_add) = eps',
    '$compiled_redirect(S,porigin_add) = eps',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_add) = (NFLOAT 0)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_left) = (NFLOAT 9223372036854775808)',
    '~$lossy_optional_integer_phase_safe(S,pfunction.ENV,porigin_add)',
    '~$lossy_optional_integer_phase_safe(S,pfunction.ENV,porigin_left)',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_left) = (PFLOAT 0)',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_right) = (PINT 0)',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_add) = (PFLOAT 0)',
    '$lossy_optional_integer_deferred(S,pfunction,1)',
    'pdefaultcache_add = {ORIGIN porigin_add,VALUE PFLOAT 0,CLASS PVSCALAR}',
    '$default_current_cache(S,porigin_add) = (pdefaultcache_add)',
    '$default_at(pfunction.DEFAULTS,2) = (pdefault_sub)',
    '$origin_node(S.SOURCES,pdefault_sub.ORIGIN) = (expression_sub)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_sub) = (NFLOAT 0)',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_sub.ORIGIN) = (PFLOAT 9223372036854775808)',
    '$default_current_cache(S,pdefault_sub.ORIGIN) = ({ORIGIN pdefault_sub.ORIGIN,VALUE PFLOAT 9223372036854775808,CLASS PVSCALAR})',
    '$default_at(pfunction.DEFAULTS,3) = (pdefault_mul)',
    '$default_current_cache(S,pdefault_mul.ORIGIN) = ({ORIGIN pdefault_mul.ORIGIN,VALUE PFLOAT 9223372036854775808,CLASS PVSCALAR})',
    '$default_at(pfunction.DEFAULTS,4) = (pdefault_div)',
    '$default_current_cache(S,pdefault_div.ORIGIN) = ({ORIGIN pdefault_div.ORIGIN,VALUE PFLOAT 9223372036854775808,CLASS PVSCALAR})',
    '$binary_apply(S,ADD,PFLOAT 0,PINT 0,z_add) = S[.RESULT = KNOWN (PFLOAT 0)]',
    '$binary_apply(S,SUBTRACT,PFLOAT 9223372036854775808,PINT 0,z_add) = S[.RESULT = KNOWN (PFLOAT 9223372036854775808)]',
    '$binary_apply(S,MULTIPLY,PFLOAT 0,PINT $(-1),z_add) = S[.RESULT = KNOWN (PFLOAT 9223372036854775808)]',
    '$binary_apply(S,DIVIDE,PFLOAT 0,PINT $(-1),z_add) = S[.RESULT = KNOWN (PFLOAT 9223372036854775808)]',
    '$number_binary(DIVIDE,NFLOAT 0,NINT 0) = DIVZERO',
    '$lookup(S.ENV,psparam_first.NAME) = (n_first)',
    'S.STORE[n_first] = DEFINED (PINT 2)',
    '$lookup(S.ENV,psparam_add.NAME) = (n_add)',
    'S.STORE[n_add] = DEFINED (PINT 0)',
    r'~(n_add <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_add) = 1',
    '$lookup(S.ENV,psparam_sub.NAME) = (n_sub)',
    'S.STORE[n_sub] = DEFINED (PINT 0)',
    'S_sign = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_add[.VALUE = PFLOAT 9223372036854775808])]',
    '$default_caches_valid(S_sign,S_sign.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_sign,pfunction,1)',
    'S_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_add[.VALUE = PINT 0])]',
    '$default_caches_valid(S_tag,S_tag.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_tag,pfunction,1)',
    'S_code = S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR pcpath_add z_add true)] ++ pcode.EXPRESSIONS)]]]',
    '$lossy_optional_integer_deferred_value_at(S_code,pfunction.ENV,porigin_add) = eps',
    '$lossy_optional_integer_deferred_value_at(S[.CODE = eps],pfunction.ENV,porigin_add) = eps',
    '$lossy_optional_integer_deferred_value_at(S[.SOURCES = eps],pfunction.ENV,porigin_add) = eps',
    'S_pool = S[.POOLS = [{UNIT n_unit,CONSTANTS ([(PCONSTANT pcpath_add (PINT 0))])}]]',
    '$lossy_optional_integer_deferred_value_at(S_pool,pfunction.ENV,porigin_add) = eps',
    r'$heap_valid($heap_graph(S)) /\ $call_descriptors_valid(S) /\ $default_caches_valid(S,S.DEFAULTCACHE)',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'S_done = $drive_steps(S,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_add) = (pdefaultcache_add)',
    r'~((HCELL n_add) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_add) = 0',
    r'~((HCELL n_first) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_first) = 0',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
]

CASES = {'deferred-arithmetic-wrapper-private-cache': {
    'source': ROWS['deferred-float-arithmetic-wrapper-alias-named-reentry']['source'],
    'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.FUNCTION = porigin '
              '-- if pcallcontext.ARGC = 1 -- if $function_at(S.FUNCTIONS,porigin) = (pfunction) '
              '-- if pfunction.ENV.NAMESPACE = $ptascii("ArithmeticWrapper254") '
              '-- if |pfunction.SIGNATURE.PARAMETERS| = 6 '
              '-- if S.TODO = $function_tasks(S,pfunction)'),
    'checks': checks,
}}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__),CATALOGUE), runner_flags=('--sl',))
