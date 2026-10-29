#!/usr/bin/env python3
"""Source-reached enum cases Closure and nonowning selected-cache history."""
from enum_core_review_protocol import PREFIX as CASE_PREFIX, term


PREFIX = CASE_PREFIX + r'''

dec $fc_front(pstate,nat) : bool
def $fc_front(S,0) = true
  -- if S.TODO = (AUTO_SCOPED_SELECTED porigin poperand ptbytes z) :: ptask_tail*
  -- if $enum_autoload_capture_target(S,porigin,poperand,ptbytes,z) = (pintrinsic)
def $fc_front(S,1) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_ENUM porigin ptbytes "cases"
  -- if pconfigcall.OWNER = (n)
def $fc_front(S,2) = true
  -- if S.TODO = (ENUM_CASE_INIT porigin) :: ptask_tail*
def $fc_front(S,3) = true
  -- if S.TODO = (ENUM_CASES_VALUE pconfigcall porigin* pvalue*) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_ENUM porigin_class ptbytes "cases"
  -- if pconfigcall.OWNER = (n)
  -- if pvalue* = eps
def $fc_front(S,n) = false -- otherwise
dec $fc_seek(pstate,nat,nat) : pstate
def $fc_seek(S,n_phase,0) = S
def $fc_seek(S,n_phase,n) = S
  -- if $(n > 0)
  -- if $fc_front(S,n_phase) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $fc_seek(S,n_phase,n) = $fc_seek($drive_steps($enumr_running(S),1),n_phase,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$fc_front(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def assertions(case_id, main_fixture, source_path, expected_bytes, eval_response, eval_code):
    if case_id == 'same-site-retired-owners':
        return retired_assertions(main_fixture, source_path, expected_bytes, eval_response, eval_code)
    if case_id != 'fcc-first-use':
        raise ValueError(case_id)
    checks = [
    'S_wait = $php_file_run('+main_fixture+',5000,'+term(str(source_path).encode())+','+term(str(source_path.parent).encode())+')',
    'S_wait.COMPLETION = SOURCE_PENDING',
    '$eval_response_valid(S_wait,'+eval_response+')',
    'S_body = $eval_resume(S_wait,'+eval_response+')',
    'S_body.COMPLETION = NORMAL',
    'S_capture_found = $fc_seek(S_body,0,3000)',
    r'S_capture_found.COMPLETION = NORMAL \/ S_capture_found.COMPLETION = BUDGET',
    'S_capture = $enumr_running(S_capture_found)',
    'S_capture.TODO = (AUTO_SCOPED_SELECTED porigin_capture poperand_capture ptbytes_method z_capture) :: ptask_capture*',
    '$enum_autoload_capture_target(S_capture,porigin_capture,poperand_capture,ptbytes_method,z_capture) = (pintrinsic)',
    'S_captured_found = $drive_steps(S_capture,1)',
    'S_captured_found.COMPLETION = BUDGET',
    'S_captured = $enumr_running(S_captured_found)',
    'S_captured.TODO = ptask_capture*',
    'S_captured.RESULT = KNOWN (POBJECT n_closure)',
    'S_captured.OBJECTS[n_closure] = INTRINSICCLOSURE pintrinsic',
    'S_owned_found = $fc_seek(S_captured,1,3000)',
    r'S_owned_found.COMPLETION = NORMAL \/ S_owned_found.COMPLETION = BUDGET',
    'S_owned = $enumr_running(S_owned_found)',
    'S_owned.TODO = (CONFIG_ARGS pconfigcall) :: ptask_owned*',
    'pconfigcall.OWNER = (n_closure)',
    'pconfigcall.KIND = pintrinsic',
    'pconfigcall.SELECTION = (n_nonce)',
    'S_owned.SELECTEDCALLS[n_nonce] = pselectedcall',
    'pselectedcall.NONCE = n_nonce',
    'pselectedcall.OWNER = (n_closure)',
    'pselectedcall.SITE = pconfigcall.SITE',
    'pselectedcall.KIND = pintrinsic',
    'S_owned.SELECTSEQ = $(n_nonce + 1)',
    'S_init_found = $fc_seek(S_owned,2,3000)',
    r'S_init_found.COMPLETION = NORMAL \/ S_init_found.COMPLETION = BUDGET',
    'S_init = $enumr_running(S_init_found)',
    'S_init.TODO = (ENUM_CASE_INIT porigin_case) :: ptask_init*',
    'S_init.CLASSCONSTANTINIT = pclassconstantcontext :: eps',
    'pclassconstantcontext.DECL = porigin_case',
    'pclassconstantcontext.SELECTION = CLASS_CONST_CALL pconfigcall',
    'S_cached_found = $fc_seek(S_init,3,3000)',
    r'S_cached_found.COMPLETION = NORMAL \/ S_cached_found.COMPLETION = BUDGET',
    'S_cached = $enumr_running(S_cached_found)',
    'S_cached.TODO = (ENUM_CASES_VALUE pconfigcall porigin_remaining* eps) :: ptask_cached*',
    '$default_cache_at(S_cached.CLASSCONSTANTCACHE,porigin_case) = (pdefaultcache)',
    'pclassconstantevent = S_cached.CLASSCONSTANTHISTORY[$nabs($( |S_cached.CLASSCONSTANTHISTORY| - 1))]',
    'pclassconstantevent = CCCACHE_ENUM porigin_case pconfigcall.SITE n_prefix n_nonce',
    'n_event = $nabs($( |S_cached.CLASSCONSTANTHISTORY| - 1))',
    'n_absent = |S_cached.SELECTEDCALLS|',
    'S_bad_nonce = S_cached[.CLASSCONSTANTHISTORY[n_event] = CCCACHE_ENUM porigin_case pconfigcall.SITE n_prefix n_absent]',
    'S_bad_site = S_cached[.CLASSCONSTANTHISTORY[n_event] = CCCACHE_ENUM porigin_case porigin_capture n_prefix n_nonce]',
    'S_bad_prefix = S_cached[.CLASSCONSTANTHISTORY[n_event] = CCCACHE_ENUM porigin_case pconfigcall.SITE 0 n_nonce]',
    'S_plain = S_cached[.CLASSCONSTANTHISTORY[n_event] = CCCACHE porigin_case pconfigcall.SITE n_prefix]',
    'S_bad_owner = S_cached[.SELECTEDCALLS[n_nonce] = pselectedcall[.OWNER = eps]]',
    'S_bad_kind = S_cached[.SELECTEDCALLS[n_nonce] = pselectedcall[.KIND = INTRINSIC_INI_GET][.LOOKUP = $intrinsic_name(INTRINSIC_INI_GET)]]',
    'S_bad_lookup = S_cached[.SELECTEDCALLS[n_nonce] = pselectedcall[.LOOKUP = $ptascii("wrong")]]',
    'S_finish = $drive_steps(S_cached,5000)',
]
    return checks + [
        '$call_descriptors_valid(S_capture)',
        '$call_descriptors_valid(S_captured)',
        '$enum_closure_valid(S_captured,n_closure,pintrinsic)',
        '$call_descriptors_valid(S_owned)',
        '$config_selected_valid(S_owned,pconfigcall)',
        '$enum_cases_call_valid(S_owned,pconfigcall)',
        '$call_descriptors_valid(S_init)',
        '$class_constant_state_valid(S_init)',
        '$class_constant_selection_valid(S_init,pclassconstantcontext)',
        '$class_constant_context_site(S_init,pclassconstantcontext)',
        '$call_descriptors_valid(S_cached)',
        '$class_constant_state_valid(S_cached)',
        '$class_constant_history_valid(S_cached)',
        '$class_constant_caches_valid(S_cached,S_cached.CLASSCONSTANTCACHE)',
        '~$class_constant_cache_trigger(S_cached,porigin_case,pconfigcall.SITE,n_prefix)',
        '$selected_entry_source_valid(S_cached,pselectedcall)',
        '$selected_log_valid(S_cached,S_cached.SELECTEDCALLS,0)',
        '$selected_task_count(S_cached.TODO,n_nonce) = 1',
        '~$class_constant_history_valid(S_bad_nonce)',
        '~$class_constant_history_valid(S_bad_site)',
        '~$class_constant_history_valid(S_bad_prefix)',
        '~$class_constant_history_valid(S_plain)',
        '~$class_constant_history_valid(S_bad_owner)',
        '~$class_constant_history_valid(S_bad_kind)',
        '~$class_constant_history_valid(S_bad_lookup)',
        '$constant_value_class_valid(S_cached,pdefaultcache.VALUE,pdefaultcache.CLASS)',
        '$call_tasks_valid(S_cached,S_cached.TODO)',
        'S_finish.COMPLETION = NORMAL',
        '$enumr_output(S_finish.EVENTS) = '+term(expected_bytes),
        '$call_descriptors_valid(S_finish)',
    ]


def retired_assertions(main_fixture, source_path, expected_bytes, eval_response, eval_code):
    checks = [
    'S_wait = $php_file_run('+main_fixture+',5000,'+term(str(source_path).encode())+','+term(str(source_path.parent).encode())+')',
    'S_wait.COMPLETION = SOURCE_PENDING',
    '$enumr_output(S_wait.EVENTS) = '+term(b'One:Two:dead|'),
    'S_wait.EVALCONTEXTS = pevalcontext :: eps',
    'pevalcontext.UNIT = 1',
    'pevalcontext.BYTES = '+term(eval_code),
    'S_wait.SELECTEDCALLS = pselectedcall_first :: pselectedcall_second :: eps',
    'pselectedcall_first.NONCE = 0', 'pselectedcall_second.NONCE = 1',
    'pselectedcall_first.SITE = pselectedcall_second.SITE',
    'pselectedcall_first.DEPTH = pselectedcall_second.DEPTH',
    'pselectedcall_first.LINE = pselectedcall_second.LINE',
    'pselectedcall_first.OWNER = (n_first)', 'pselectedcall_second.OWNER = (n_second)',
    'pselectedcall_first.KIND = INTRINSIC_ENUM porigin_first ($ptascii("ReviewFirstCallable")) "cases"',
    'pselectedcall_second.KIND = INTRINSIC_ENUM porigin_second ($ptascii("ReviewSecondCallable")) "cases"',
    '$class_at(S_wait.CLASSES,porigin_first) = (pclassdesc_first)',
    '$class_at(S_wait.CLASSES,porigin_second) = (pclassdesc_second)',
    '$enum_case_origins(S_wait,pclassdesc_first.CONSTANTS) = [porigin_case_first]',
    '$enum_case_origins(S_wait,pclassdesc_second.CONSTANTS) = [porigin_case_second]',
    'n_event_first = $nabs($( |S_wait.CLASSCONSTANTHISTORY| - 2))',
    'n_event_second = $nabs($( |S_wait.CLASSCONSTANTHISTORY| - 1))',
    'S_wait.CLASSCONSTANTHISTORY[n_event_first] = CCCACHE_ENUM porigin_case_first pselectedcall_first.SITE n_prefix_first 0',
    'S_wait.CLASSCONSTANTHISTORY[n_event_second] = CCCACHE_ENUM porigin_case_second pselectedcall_second.SITE n_prefix_second 1',
    'S_bad_later = S_wait[.CLASSCONSTANTHISTORY[n_event_first] = CCCACHE_ENUM porigin_case_first pselectedcall_first.SITE n_prefix_first 1]',
    'pselectedcall_rebound = pselectedcall_first[.KIND = pselectedcall_second.KIND][.OWNER = pselectedcall_second.OWNER][.LOOKUP = pselectedcall_second.LOOKUP]',
    'S_rebound = S_wait[.SELECTEDCALLS[0] = pselectedcall_rebound]',
    'S_body = $eval_resume(S_wait,'+eval_response+')',
    'S_body.COMPLETION = NORMAL',
    'S_finish = $drive_steps(S_body,5000)',
]
    return checks + [
        '$call_descriptors_valid(S_wait)',
        '$class_constant_history_valid(S_wait)',
        '$class_constant_caches_valid(S_wait,S_wait.CLASSCONSTANTCACHE)',
        '$selected_log_valid(S_wait,S_wait.SELECTEDCALLS,0)',
        '~((HOBJECT n_first) <- S_wait.ALLOCATIONS)',
        '~((HOBJECT n_second) <- S_wait.ALLOCATIONS)',
        '~$enum_closure_valid(S_wait,n_first,pselectedcall_first.KIND)',
        '~$enum_closure_valid(S_wait,n_second,pselectedcall_second.KIND)',
        'S_wait.OBJECTS[n_first] = INTRINSICCLOSURE pselectedcall_first.KIND',
        'S_wait.OBJECTS[n_second] = INTRINSICCLOSURE pselectedcall_second.KIND',
        '$selected_entry_source_valid(S_wait,pselectedcall_first)',
        '$selected_entry_source_valid(S_wait,pselectedcall_second)',
        r'porigin_first =/= porigin_second /\ n_first =/= n_second',
        '~$class_constant_history_valid(S_bad_later)',
        '$selected_entry_source_valid(S_wait,pselectedcall_rebound)',
        '$selected_log_valid(S_rebound,S_rebound.SELECTEDCALLS,0)',
        '~$class_constant_history_valid(S_rebound)',
        '~$call_descriptors_valid(S_rebound)',
        '$eval_response_valid(S_wait,'+eval_response+')',
        '$call_descriptors_valid(S_body)',
        'S_finish.COMPLETION = NORMAL',
        '$enumr_output(S_finish.EVENTS) = '+term(expected_bytes),
        '$call_descriptors_valid(S_finish)',
    ]
