#!/usr/bin/env python3
"""Reach individual enum API initialization, retry, aliases and cache authority."""
import base64
import json
from enum_core_review_protocol import PREFIX as CASE_PREFIX, term


PREFIX = CASE_PREFIX + r'''
dec $enumq_marker(ptask*) : (pconfigcall, porigin)?
def $enumq_marker(eps) = eps
def $enumq_marker((ENUM_QUERY_RESULT pconfigcall porigin) :: ptask_tail*) = ((pconfigcall,porigin))
def $enumq_marker(ptask :: ptask_tail*) = $enumq_marker(ptask_tail*) -- if ~$enum_query_result_task(ptask)
dec $enumq_without_marker(ptask*) : ptask*
def $enumq_without_marker(eps) = eps
def $enumq_without_marker((ENUM_QUERY_RESULT pconfigcall porigin) :: ptask_tail*) = ptask_tail*
def $enumq_without_marker(ptask :: ptask_tail*) = ptask :: $enumq_without_marker(ptask_tail*) -- if ~$enum_query_result_task(ptask)
dec $enumq_front(pstate, nat) : bool
def $enumq_front(S, 0) = true
  -- if $enumq_marker(S.TODO) = ((pconfigcall,porigin))
  -- if $enum_query_initializing(S.CLASSCONSTANTINIT,pconfigcall,porigin)
def $enumq_front(S, 1) = true
  -- if S.TODO = (ENUM_QUERY_RESULT pconfigcall porigin) :: ptask*
def $enumq_front(S, n) = true
  -- if n <- [2,3]
  -- if $enumq_marker(S.TODO) = ((pconfigcall,porigin))
  -- if $enum_query_initializing(S.CLASSCONSTANTINIT,pconfigcall,porigin)
  -- if (n = 2 /\ pconfigcall.LINE = 5) \/ (n = 3 /\ pconfigcall.LINE = 8)
def $enumq_front(S, n) = false -- otherwise
dec $enumq_seek(pstate, nat, nat) : pstate
def $enumq_seek(S, n_phase, 0) = S
def $enumq_seek(S, n_phase, n) = S
  -- if $(n > 0)
  -- if $enumq_front(S,n_phase) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET /\ ~$throwable_pending(S.COMPLETION))
def $enumq_seek(S, n_phase, n) = $enumq_seek($drive_steps($enumr_running(S),1),n_phase,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$enumq_front(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET \/ $throwable_pending(S.COMPLETION)
dec $enumq_unrelated_node(pcnode) : bool
def $enumq_unrelated_node(NExprFuncCall name (SEQUENCE ([NArg ABSENT (NScalarString (BYTES text) metadata_string) (BOOLEAN false) (BOOLEAN false) metadata_arg])) metadata) = ($base64(text) = $ptascii("REVIEW_UNRELATED_QUERY"))
def $enumq_unrelated_node(pcnode) = false -- otherwise
dec $enumq_unrelated(nat, pcoccurrence*) : porigin?
def $enumq_unrelated(n, (PCOCCURRENCE pcpath pcnode) :: pcoccurrence_tail*) = (PORIGIN n pcpath)
  -- if $enumq_unrelated_node(pcnode)
def $enumq_unrelated(n, (PCOCCURRENCE pcpath pcnode) :: pcoccurrence_tail*) = $enumq_unrelated(n,pcoccurrence_tail*)
  -- if ~$enumq_unrelated_node(pcnode)
def $enumq_unrelated(n, eps) = eps
dec $enumq_cache_event(pclassconstantevent, porigin) : bool
def $enumq_cache_event(CCCACHE porigin porigin_trigger n, porigin) = true
def $enumq_cache_event(pclassconstantevent, porigin) = false -- otherwise
dec $enumq_bad_history(pclassconstantevent*, porigin, porigin) : pclassconstantevent*
def $enumq_bad_history(eps, porigin, porigin_bad) = eps
def $enumq_bad_history((CCCACHE porigin porigin_old n) :: pclassconstantevent*, porigin, porigin_bad) = (CCCACHE porigin porigin_bad n) :: pclassconstantevent*
def $enumq_bad_history(pclassconstantevent :: pclassconstantevent_tail*, porigin, porigin_bad) = pclassconstantevent :: $enumq_bad_history(pclassconstantevent_tail*,porigin,porigin_bad)
  -- if ~$enumq_cache_event(pclassconstantevent,porigin)
'''


def reach(label, prior, phase):
    return [label + '_found = $enumq_seek(' + prior + ',' + str(phase) + ',4000)',
            label + r'_found.COMPLETION = NORMAL \/ ' + label + '_found.COMPLETION = BUDGET',
            label + ' = $enumr_running(' + label + '_found)',
            '$enumq_front(' + label + ',' + str(phase) + ')',
            '$call_descriptors_valid(' + label + ')']


def assertions(case_id, main_fixture, source_path, expected_bytes):
    if case_id not in ('defined-initializer-retry', 'aliased-query-cache'):
        raise ValueError(case_id)
    retry = case_id == 'defined-initializer-retry'
    checks = ['S_initial = $php_run(' + main_fixture + ',0,' +
              json.dumps(base64.b64encode(str(source_path).encode()).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', *reach('S_pending', 'S_initial', 0),
        '$enumq_marker(S_pending.TODO) = ((pconfigcall_query,porigin_decl))',
        'pconfigcall_query.KIND = INTRINSIC_DEFINED',
        '$class_constant_origin(S_pending.CLASSES,porigin_decl) = (pclassconstantdesc_decl)',
        'porigin_owner = pclassconstantdesc_decl.OWNER',
        '$class_at(S_pending.CLASSES,porigin_owner) = (pclassdesc_owner)',
        'pclassdesc_owner.KIND = "enum"',
        '$enum_query_call_valid(S_pending,pconfigcall_query,porigin_decl)',
        '~$enum_query_result_valid(S_pending,pconfigcall_query,porigin_decl)',
        '~$enum_query_result_valid(S_pending[.TODO = (ENUM_QUERY_RESULT pconfigcall_query porigin_decl) :: S_pending.TODO],pconfigcall_query,porigin_decl)',
        '$call_task_valid(S_pending,ENUM_QUERY_RESULT pconfigcall_query porigin_decl)',
        '$enum_query_initializing(S_pending.CLASSCONSTANTINIT,pconfigcall_query,porigin_decl)',
        'S_pending.CLASSCONSTANTINIT = pclassconstantcontext_query :: eps',
        'pclassconstantcontext_query.DECL = porigin_decl',
        'pclassconstantcontext_query.SELECTION = CLASS_CONST_CALL pconfigcall_query',
        '$class_constant_selection_valid(S_pending,pclassconstantcontext_query)',
        '~$class_constant_selection_valid(S_pending,pclassconstantcontext_query[.LINE = $(pclassconstantcontext_query.LINE + 1)])',
        '$default_cache_at(S_pending.CLASSCONSTANTCACHE,porigin_decl) = eps',
        'pconfigcall_bad = pconfigcall_query[.SENT = [NAMED_SENT (KNOWN (PSTRING $ptascii("DifferentReviewEnum::Only")))]]',
        '~$enum_query_call_valid(S_pending,pconfigcall_bad,porigin_decl)',
        '~$enum_query_result_valid(S_pending,pconfigcall_bad,porigin_decl)',
        '~$enum_query_call_valid(S_pending,pconfigcall_query,porigin_owner)',
        'S_no_marker = S_pending[.TODO = $enumq_without_marker(S_pending.TODO)]',
        '~$enum_query_marker(S_no_marker,pconfigcall_query,porigin_decl,S_no_marker.TODO)',
        '~$class_constant_selection_valid(S_no_marker,pclassconstantcontext_query)',
        'S_zero = $drive_steps(S_pending,0)',
        'S_zero = S_pending[.COMPLETION = BUDGET]']
    prior = '$drive_steps($enumr_running(S_zero),1)'
    if retry:
        checks += ['$call_task_valid(S_pending,ENUM_CASE_INIT porigin_decl)',
            '~$enum_case_init_valid(S_pending,porigin_decl)',
            '~$call_task_valid(S_pending[.CONSTCONTEXT = eps],ENUM_CASE_INIT porigin_decl)',
            '~$call_task_valid(S_pending[.ORIGIN = (porigin_owner)],ENUM_CASE_INIT porigin_decl)',
            *reach('S_retry', prior, 2),
            '$enumq_marker(S_retry.TODO) = ((pconfigcall_retry,porigin_decl))',
            'pconfigcall_retry.SITE =/= pconfigcall_query.SITE',
            '$default_cache_at(S_retry.CLASSCONSTANTCACHE,porigin_decl) = eps',
            'S_retry.CLASSCONSTANTHISTORY = S_pending.CLASSCONSTANTHISTORY',
            *reach('S_success', '$drive_steps(S_retry,1)', 3),
            '$enumq_marker(S_success.TODO) = ((pconfigcall_success,porigin_decl))',
            '$default_cache_at(S_success.CLASSCONSTANTCACHE,porigin_decl) = eps',
            'S_success.CLASSCONSTANTHISTORY = S_pending.CLASSCONSTANTHISTORY']
        prior = '$drive_steps(S_success,1)'
    checks += [*reach('S_cached', prior, 1),
        'S_cached.TODO = (ENUM_QUERY_RESULT pconfigcall_cached porigin_decl) :: ptask_cached*',
        'pconfigcall_cached.KIND = INTRINSIC_DEFINED',
        'S_cached.CLASSCONSTANTINIT = eps', 'S_cached.CONSTCONTEXT = eps',
        '$enum_query_result_valid(S_cached,pconfigcall_cached,porigin_decl)',
        'S_cached.RESULT = KNOWN (POBJECT n_case)',
        '$default_cache_at(S_cached.CLASSCONSTANTCACHE,porigin_decl) = (pdefaultcache_decl)',
        'pdefaultcache_decl.VALUE = POBJECT n_case',
        'pdefaultcache_decl.CLASS = PVENUMCASE n_case porigin_case',
        '$enum_case_object(S_cached,n_case) = (pclassconstantdesc_case)',
        'pclassconstantdesc_case.ORIGIN = porigin_case',
        'pclassconstantdesc_case.OWNER = porigin_owner',
        '$default_cache_at(S_cached.CLASSCONSTANTCACHE,porigin_case) = (pdefaultcache_case)',
        'pdefaultcache_case.VALUE = POBJECT n_case',
        '(HOBJECT n_case) <- $class_constant_roots(S_cached.CLASSCONSTANTCACHE)',
        '$class_constant_state_valid(S_cached)',
        '$class_constant_cache_trigger(S_cached,porigin_decl,pconfigcall_cached.SITE,|S_cached.DECLARATIONS|)',
        '~$enum_query_result_valid(S_cached[.RESULT = KNOWN PNULL],pconfigcall_cached,porigin_decl)',
        '~$enum_query_result_valid(S_cached[.TODO = ptask_cached*],pconfigcall_cached,porigin_decl)',
        'S_one = $enumr_running($drive_steps(S_cached,1))',
        'S_one.RESULT = KNOWN (PBOOL true)',
        'S_one.TODO = ptask_cached*',
        'S_one.CLASSCONSTANTCACHE = S_cached.CLASSCONSTANTCACHE',
        '$call_descriptors_valid(S_one)']
    if retry:
        checks += ['porigin_decl = porigin_case',
            '~$class_constant_table_done(S_cached,porigin_owner)',
            '$location_slot(S_cached,PROPERTY n_case $ptascii("value")) = DEFINED (PINT 13)']
    else:
        checks += ['porigin_decl =/= porigin_case',
            'pclassconstantdesc_decl.NAME = $ptascii("Alias")',
            'S_cached.SOURCES = [pcunit_source]',
            '$enumq_unrelated(pcunit_source.ID,pcunit_source.OCCURRENCES) = (porigin_unrelated)',
            '~$class_constant_cache_trigger(S_cached,porigin_decl,porigin_unrelated,|S_cached.DECLARATIONS|)',
            'S_bad_history = S_cached[.CLASSCONSTANTHISTORY = $enumq_bad_history(S_cached.CLASSCONSTANTHISTORY,porigin_decl,porigin_unrelated)]',
            '~$class_constant_state_valid(S_bad_history)']
    return checks + ['S_finish = $drive_steps(S_one,5000)',
        'S_finish.COMPLETION = NORMAL', 'S_finish.EXITSTATUS = 0', 'S_finish.TODO = eps',
        '$enumr_output(S_finish.EVENTS) = ' + term(expected_bytes),
        '(HOBJECT n_case) <- $class_constant_roots(S_finish.CLASSCONSTANTCACHE)',
        '$call_descriptors_valid(S_finish)']
