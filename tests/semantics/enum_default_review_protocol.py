#!/usr/bin/env python3
"""Reach enum parameter-default cache identity, provenance and ownership."""
import base64
import json
from enum_core_review_protocol import PREFIX as CASE_PREFIX, term


PREFIX = CASE_PREFIX + r'''
dec $enumd_front(pstate) : bool
def $enumd_front(S) = true
  -- if S.DEFAULTCACHE = pdefaultcache :: pdefaultcache_tail*
  -- if pdefaultcache.CLASS = PVENUMCASE n_case porigin_case
  -- if S.CURRENT = (pcallcontext)
  -- if $function_at($all_functions(S),pcallcontext.FUNCTION) = (pfunction)
  -- if pfunction.NAME = $ptascii("reviewEnumDefault")
  -- if $lookup(S.ENV,$ptascii("value")) = (n_cell)
  -- if S.STORE[n_cell] = DEFINED (POBJECT n_case)
def $enumd_front(S) = false -- otherwise
dec $enumd_seek(pstate, nat) : pstate
def $enumd_seek(S, 0) = S
def $enumd_seek(S, n) = S
  -- if $(n > 0)
  -- if $enumd_front(S) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET /\ ~$throwable_pending(S.COMPLETION))
def $enumd_seek(S, n) = $enumd_seek($drive_steps($enumr_running(S),1),$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$enumd_front(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET \/ $throwable_pending(S.COMPLETION)
'''


def assertions(case_id, main_fixture, source_path, expected_bytes):
    if case_id != 'enum-type-default-reference':
        raise ValueError(case_id)
    return ['S_initial = $php_run(' + main_fixture + ',0,' +
            json.dumps(base64.b64encode(str(source_path).encode()).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', 'S_cached_found = $enumd_seek(S_initial,3000)',
        r'S_cached_found.COMPLETION = NORMAL \/ S_cached_found.COMPLETION = BUDGET',
        'S_cached = $enumr_running(S_cached_found)', '$enumd_front(S_cached)',
        '$call_descriptors_valid(S_cached)',
        'S_cached.DEFAULTCACHE = pdefaultcache :: pdefaultcache_tail*',
        'pdefaultcache.CLASS = PVENUMCASE n_case porigin_case',
        'pdefaultcache.VALUE = POBJECT n_case',
        'S_cached.CURRENT = (pcallcontext)',
        '$function_at($all_functions(S_cached),pcallcontext.FUNCTION) = (pfunction)',
        '$default_at(pfunction.DEFAULTS,0) = (pdefault)',
        'pdefault.KIND = PDDEFERRED', 'pdefault.ORIGIN = pdefaultcache.ORIGIN',
        'pdefaultcache.ORIGIN = $constant_child($default_parameter_origin(S_cached,pfunction.ORIGIN,0),[PCFIELD 6])',
        'pdefaultcache.ORIGIN =/= porigin_case',
        '$enum_case_object(S_cached,n_case) = (pclassconstantdesc_case)',
        'pclassconstantdesc_case.ORIGIN = porigin_case',
        '$constant_value_class_valid(S_cached,pdefaultcache.VALUE,pdefaultcache.CLASS)',
        '$default_cacheable(pdefaultcache.CLASS)', '~$default_cacheable(PVOBJECT)',
        '$default_caches_valid(S_cached,S_cached.DEFAULTCACHE)',
        '(HOBJECT n_case) <- $default_cache_roots(S_cached.DEFAULTCACHE)',
        '(HOBJECT n_case) <- $class_constant_roots(S_cached.CLASSCONSTANTCACHE)',
        'S_bad = S_cached[.DEFAULTCACHE = pdefaultcache[.CLASS = PVENUMCASE n_case pfunction.ORIGIN] :: pdefaultcache_tail*]',
        '~$default_caches_valid(S_bad,S_bad.DEFAULTCACHE)', '~$call_descriptors_valid(S_bad)',
        'S_zero = $drive_steps(S_cached,0)', 'S_zero = S_cached[.COMPLETION = BUDGET]',
        'S_one = $enumr_running($drive_steps($enumr_running(S_zero),1))',
        '$enum_case_object(S_one,n_case) = (pclassconstantdesc_case)',
        'S_one.DEFAULTCACHE = S_cached.DEFAULTCACHE',
        'S_finish = $drive_steps(S_one,5000)',
        'S_finish.COMPLETION = NORMAL', 'S_finish.EXITSTATUS = 0', 'S_finish.TODO = eps',
        '$enumr_output(S_finish.EVENTS) = ' + term(expected_bytes),
        '(HOBJECT n_case) <- $default_cache_roots(S_finish.DEFAULTCACHE)',
        '$call_descriptors_valid(S_finish)']
