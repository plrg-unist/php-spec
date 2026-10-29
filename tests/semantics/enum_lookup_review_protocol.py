#!/usr/bin/env python3
"""Source-reached captured enum lookup tables, retained history and caller strictness."""
import base64
from enum_core_review_protocol import PREFIX as CASE_PREFIX, term


_FRONTS = {
    'lazy-table-retired-owners': r'''
dec $ef_front(pstate,nat) : bool
def $ef_front(S,0) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_ENUM porigin ptbytes "from"
  -- if pconfigcall.OWNER = (n)
def $ef_front(S,1) = true
  -- if S.TODO = (CLASS_CONST_BIND porigin) :: ptask_tail*
  -- if $enum_case_origin(S,porigin)
def $ef_front(S,2) = true
  -- if S.TODO = (CLASS_CONST_TABLE_UPDATE porigin z) :: ptask_tail*
  -- if $class_at(S.CLASSES,porigin) = (pclassdesc)
  -- if pclassdesc.KIND = "enum"
def $ef_front(S,n_phase) = false -- otherwise
dec $ef_seek(pstate,nat,nat) : pstate
def $ef_seek(S,n_phase,0) = S
def $ef_seek(S,n_phase,n) = S
  -- if $(n > 0)
  -- if $ef_front(S,n_phase) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $ef_seek(S,n_phase,n) = $ef_seek($drive_steps($enumr_running(S),1),n_phase,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$ef_front(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
''',
    'ordinary-case-alias': r'''
dec $alias_front(pstate) : bool
def $alias_front(S) = true
  -- if S.TODO = (CLASS_CONST_BIND porigin) :: ptask_tail*
  -- if $class_constant_origin(S.CLASSES,porigin) = (pclassconstantdesc)
  -- if ~$enum_case_origin(S,porigin)
  -- if $class_at(S.CLASSES,pclassconstantdesc.OWNER) = (pclassdesc)
  -- if pclassdesc.KIND = "enum"
def $alias_front(S) = false -- otherwise
dec $alias_seek(pstate,nat) : pstate
def $alias_seek(S,0) = S
def $alias_seek(S,n) = S
  -- if $(n > 0)
  -- if $alias_front(S) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $alias_seek(S,n) = $alias_seek($drive_steps($enumr_running(S),1),$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$alias_front(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
''',
    'inherited-deferred-alias': r'''
dec $alias_front(pstate) : bool
def $alias_front(S) = true
  -- if S.TODO = (CLASS_CONST_BIND porigin) :: ptask_tail*
  -- if $class_constant_origin(S.CLASSES,porigin) = (pclassconstantdesc)
  -- if ~$enum_case_origin(S,porigin)
  -- if pclassconstantdesc.NAME = $ptascii("Alias")
def $alias_front(S) = false -- otherwise
dec $alias_seek(pstate,nat) : pstate
def $alias_seek(S,0) = S
def $alias_seek(S,n) = S
  -- if $(n > 0)
  -- if $alias_front(S) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $alias_seek(S,n) = $alias_seek($drive_steps($enumr_running(S),1),$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$alias_front(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
''',
    'callable-caller-strictness-prefix': r'''
dec $strict_front(pstate, nat, ptbytes) : bool
def $strict_front(S,n_unit,ptbytes_expected) = true
  -- if n_unit <- [0,1]
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_ENUM porigin_enum ptbytes_name "from"
  -- if pconfigcall.OWNER = (n_owner)
  -- if pconfigcall.SITE = PORIGIN n_unit pcpath
def $strict_front(S,2,ptbytes_expected) = ($enumr_output(S.EVENTS) = ptbytes_expected)
def $strict_front(S,n_unit,ptbytes_expected) = false -- otherwise
dec $strict_seek(pstate, nat, ptbytes, nat) : pstate
def $strict_seek(S,n_unit,ptbytes_expected,0) = S
def $strict_seek(S,n_unit,ptbytes_expected,n) = S
  -- if $(n > 0)
  -- if $strict_front(S,n_unit,ptbytes_expected) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET /\ ~$throwable_pending(S.COMPLETION))
def $strict_seek(S,n_unit,ptbytes_expected,n) = $strict_seek($drive_steps($enumr_running(S),1),n_unit,ptbytes_expected,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$strict_front(S,n_unit,ptbytes_expected)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET \/ $throwable_pending(S.COMPLETION)
''',
    'owned-stringable-multiline': r'''
dec $ostr_front(pstate,nat) : bool
def $ostr_front(S,0) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_ENUM porigin ptbytes "from"
  -- if pconfigcall.OWNER = (n_owner)
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN (POBJECT n_object))]
def $ostr_front(S,1) = true
  -- if S.TODO = (ENUM_FROM_STRING_RESULT pconfigcall n_object porigin_child z_child z_call) :: ptask_tail*
def $ostr_front(S,2) = true
  -- if S.TODO = (CLASS_CONST_UPDATE porigin z) :: ptask_tail*
  -- if $enumr_output(S.EVENTS) = $ptascii("READY|CAST|DROP|")
def $ostr_front(S,3) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $stringify_context_kind(S,pcallcontext)
def $ostr_front(S,n_phase) = false -- otherwise
dec $ostr_seek(pstate,nat,nat) : pstate
def $ostr_seek(S,n_phase,0) = S
def $ostr_seek(S,n_phase,n) = S
  -- if $(n > 0)
  -- if $ostr_front(S,n_phase) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $ostr_seek(S,n_phase,n) = $ostr_seek($drive_steps($enumr_running(S),1),n_phase,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$ostr_front(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
''',
    'enum-case-conditional-choice': r'''
dec $cc_front(pstate) : bool
def $cc_front(S) = true
  -- if S.TODO = (CLASS_CONST_BIND porigin) :: ptask_tail*
  -- if ~$enum_case_origin(S,porigin)
  -- if $class_constant_origin(S.CLASSES,porigin) = (pclassconstantdesc)
  -- if $class_at(S.CLASSES,pclassconstantdesc.OWNER) = (pclassdesc)
  -- if pclassdesc.KIND = "enum"
def $cc_front(S) = false -- otherwise
dec $cc_seek(pstate,nat) : pstate
dec $cc_case_event(pclassconstantevent,porigin) : bool
def $cc_case_event(pclassconstantevent,porigin) = true
  -- if $constant_callable_cache_event(pclassconstantevent) = ((porigin,n_prefix))
def $cc_case_event(pclassconstantevent,porigin) = false -- otherwise
dec $cc_without_cache(pclassconstantevent*,porigin) : pclassconstantevent*
def $cc_without_cache(eps,porigin) = eps
def $cc_without_cache(pclassconstantevent :: pclassconstantevent_tail*,porigin) = $cc_without_cache(pclassconstantevent_tail*,porigin)
  -- if $constant_callable_cache_event(pclassconstantevent) = ((porigin,n_prefix))
def $cc_without_cache(pclassconstantevent :: pclassconstantevent_tail*,porigin) = pclassconstantevent :: $cc_without_cache(pclassconstantevent_tail*,porigin)
  -- if ~$cc_case_event(pclassconstantevent,porigin)
def $cc_seek(S,0) = S
def $cc_seek(S,n) = S
  -- if $(n > 0)
  -- if $cc_front(S) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $cc_seek(S,n) = $cc_seek($drive_steps($enumr_running(S),1),$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$cc_front(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
''',
}

_FRONTS['array-target-rebound'] = r'''
dec $earr_front(pstate,nat) : bool
def $earr_front(S,0) = true
  -- if S.TODO = (CALL_DYNAMIC porigin z_init z_call) :: ptask_tail*
def $earr_front(S,1) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.OWNER = eps
  -- if pconfigcall.SELECTION = (n_nonce)
  -- if $enum_kind(pconfigcall.KIND)
def $earr_front(S,2) = true
  -- if S.TODO = (ENUM_FROM_FETCH pconfigcall pvalue_key) :: ptask_tail*
  -- if pconfigcall.OWNER = eps
  -- if pconfigcall.SELECTION = (n_nonce)
def $earr_front(S,n) = false -- otherwise
dec $earr_seek(pstate,nat,nat) : pstate
def $earr_seek(S,n_stage,0) = S
def $earr_seek(S,n_stage,n) = S
  -- if $(n > 0)
  -- if $earr_front(S,n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $earr_seek(S,n_stage,n) = $earr_seek($drive_steps($enumr_running(S),1),n_stage,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$earr_front(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
dec $earr_record(pselectedcall*,nat,pselectedcall) : pselectedcall*
def $earr_record(eps,n,pselectedcall) = eps
def $earr_record(pselectedcall_head :: pselectedcall_tail*,n,pselectedcall) = pselectedcall :: pselectedcall_tail*
  -- if pselectedcall_head.NONCE = n
def $earr_record(pselectedcall_head :: pselectedcall_tail*,n,pselectedcall) = pselectedcall_head :: $earr_record(pselectedcall_tail*,n,pselectedcall)
  -- if pselectedcall_head.NONCE =/= n
dec $earr_matches(pclassconstantevent,nat) : bool
def $earr_matches(CCCACHE_ENUM porigin porigin_site n_prefix n,n) = true
def $earr_matches(CCUPDATE_ENUM porigin porigin_root porigin_site n_prefix n,n) = true
def $earr_matches(pclassconstantevent,n) = false -- otherwise
dec $earr_nonce(pclassconstantevent*,nat,nat) : pclassconstantevent*
def $earr_nonce(eps,n_old,n_new) = eps
def $earr_nonce((CCCACHE_ENUM porigin porigin_site n_prefix n_old) :: pclassconstantevent_tail*,n_old,n_new) = (CCCACHE_ENUM porigin porigin_site n_prefix n_new) :: $earr_nonce(pclassconstantevent_tail*,n_old,n_new)
def $earr_nonce((CCUPDATE_ENUM porigin porigin_root porigin_site n_prefix n_old) :: pclassconstantevent_tail*,n_old,n_new) = (CCUPDATE_ENUM porigin porigin_root porigin_site n_prefix n_new) :: $earr_nonce(pclassconstantevent_tail*,n_old,n_new)
def $earr_nonce(pclassconstantevent :: pclassconstantevent_tail*,n_old,n_new) = pclassconstantevent :: $earr_nonce(pclassconstantevent_tail*,n_old,n_new)
  -- if ~$earr_matches(pclassconstantevent,n_old)
'''

_FRONTS['array-stringable-target-rebound'] = r'''
dec $ostr_front(pstate,nat) : bool
def $ostr_front(S,0) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_ENUM porigin ptbytes "from"
  -- if pconfigcall.OWNER = eps
  -- if pconfigcall.SELECTION = (n_nonce)
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN (POBJECT n_object))]
def $ostr_front(S,1) = true
  -- if S.TODO = (ENUM_FROM_STRING_RESULT pconfigcall n_object porigin_child z_child z_call) :: ptask_tail*
def $ostr_front(S,2) = true
  -- if S.TODO = (CLASS_CONST_UPDATE porigin z) :: ptask_tail*
  -- if $enumr_output(S.EVENTS) = $ptascii("READY|CAST|DROP|")
def $ostr_front(S,3) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $stringify_context_kind(S,pcallcontext)
def $ostr_front(S,n_phase) = false -- otherwise
dec $ostr_seek(pstate,nat,nat) : pstate
def $ostr_seek(S,n_phase,0) = S
def $ostr_seek(S,n_phase,n) = S
  -- if $(n > 0)
  -- if $ostr_front(S,n_phase) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $ostr_seek(S,n_phase,n) = $ostr_seek($drive_steps($enumr_running(S),1),n_phase,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$ostr_front(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def prefix(case_id):
    return CASE_PREFIX + _FRONTS[case_id]


def assertions(case_id, main_fixture, source_path, expected_bytes,
               file_snapshot=None, factory_fixture=None):
    if case_id == 'callable-caller-strictness-prefix':
        return _strict(main_fixture, source_path, expected_bytes, file_snapshot, factory_fixture)
    return {
        'lazy-table-retired-owners': _table,
        'enum-case-conditional-choice': _conditional,
        'array-target-rebound': _array_selected,
        'array-stringable-target-rebound': _array_stringable,
        'owned-stringable-multiline': _stringable,
        'ordinary-case-alias': _alias,
        'inherited-deferred-alias': _inherited,
    }[case_id](main_fixture, source_path, expected_bytes)


def _table(main_fixture, source_path, expected_bytes):
    assert expected_bytes == b'READY|One:Two:null|dead|same|'
    checks = [
        'S_initial = $php_file_run(' + main_fixture + ',0,' + term(str(source_path).encode()) + ',' + term(str(source_path.parent).encode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_config_found = $ef_seek(S_initial,0,3000)',
        'S_config_found.COMPLETION = NORMAL \\/ S_config_found.COMPLETION = BUDGET',
        'S_config = $enumr_running(S_config_found)',
        'S_config.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
        'pconfigcall.KIND = INTRINSIC_ENUM porigin_enum ($ptascii("ReviewOwnedLookup")) "from"',
        'pconfigcall.OWNER = (n_closure)',
        'pconfigcall.SELECTION = (n_nonce)',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_raw)]',
        '$string_bytes(pvalue_raw) = ($ptascii("1"))',
        'S_config.SELECTEDCALLS[n_nonce] = pselectedcall',
        'S_converted_found = $drive_steps(S_config,1)',
        'S_converted_found.COMPLETION = BUDGET',
        'S_converted = $enumr_running(S_converted_found)',
        'S_converted.TODO = (ENUM_FROM_CONVERT pconfigcall pvalue_raw) :: ptask_tail*',
        'S_converted.RESULT = KNOWN (PINT 1)',
        'S_queue_found = $drive_steps(S_converted,1)',
        'S_queue_found.COMPLETION = BUDGET',
        'S_queue = $enumr_running(S_queue_found)',
        'S_queue.TODO = (CLASS_CONST_UPDATE porigin_case z) :: ptask_queue*',
        'S_bind_found = $ef_seek(S_queue,1,100)',
        'S_bind_found.COMPLETION = NORMAL \\/ S_bind_found.COMPLETION = BUDGET',
        'S_bind = $enumr_running(S_bind_found)',
        'S_bind.TODO = (CLASS_CONST_BIND porigin_case_first) :: ptask_bind*',
        'S_bind.CLASSCONSTANTINIT = pclassconstantcontext :: eps',
        'pclassconstantcontext.DECL = porigin_case_first',
        'pclassconstantcontext.SELECTION = CLASS_CONST_UPDATE_SELECT porigin_enum',
        'S_cached_found = $drive_steps(S_bind,1)',
        'S_cached_found.COMPLETION = BUDGET',
        'S_cached = $enumr_running(S_cached_found)',
        '$default_cache_at(S_cached.CLASSCONSTANTCACHE,porigin_case_first) = (pdefaultcache)',
        'n_event = $nabs($( |S_cached.CLASSCONSTANTHISTORY| - 1))',
        'S_cached.CLASSCONSTANTHISTORY[n_event] = CCCACHE_ENUM porigin_case_first pconfigcall.SITE n_prefix n_nonce',
        'n_absent = |S_cached.SELECTEDCALLS|',
        'S_bad_nonce = S_cached[.CLASSCONSTANTHISTORY[n_event] = CCCACHE_ENUM porigin_case_first pconfigcall.SITE n_prefix n_absent]',
        'S_plain = S_cached[.CLASSCONSTANTHISTORY[n_event] = CCCACHE porigin_case_first pconfigcall.SITE n_prefix]',
        'S_wrong_case = S_cached[.CLASSCONSTANTHISTORY[n_event] = CCCACHE_ENUM porigin_enum pconfigcall.SITE n_prefix n_nonce]',
        'S_wrong_owner = S_cached[.SELECTEDCALLS[n_nonce] = pselectedcall[.OWNER = eps]]',
        'pconfigcall_bad = pconfigcall[.OWNER = eps][.SELECTION = eps]',
        'S_blocked = S_bind[.TODO = (ENUM_FROM_FETCH pconfigcall_bad (PINT 1)) :: S_bind.TODO]',
        'S_table_found = $ef_seek(S_cached,2,100)',
        'S_table_found.COMPLETION = NORMAL \\/ S_table_found.COMPLETION = BUDGET',
        'S_table = $enumr_running(S_table_found)',
        'S_table.TODO = (CLASS_CONST_TABLE_UPDATE porigin_enum z) :: (ENUM_FROM_FETCH pconfigcall (PINT 1)) :: ptask_table*',
        'n_table_prefix = |S_table.DECLARATIONS|',
        'S_after_found = $drive_steps(S_table,1)',
        'S_after_found.COMPLETION = BUDGET',
        'S_after = $enumr_running(S_after_found)',
        'S_after.TODO = (ENUM_FROM_FETCH pconfigcall (PINT 1)) :: ptask_table*',
        'n_table_event = $nabs($( |S_after.CLASSCONSTANTHISTORY| - 1))',
        'S_after.CLASSCONSTANTHISTORY[n_table_event] = CCUPDATE_ENUM porigin_enum porigin_enum pconfigcall.SITE n_table_prefix n_nonce',
        'n_absent_table = |S_after.SELECTEDCALLS|',
        'S_bad_table_nonce = S_after[.CLASSCONSTANTHISTORY[n_table_event] = CCUPDATE_ENUM porigin_enum porigin_enum pconfigcall.SITE n_table_prefix n_absent_table]',
        'S_bad_table_root = S_after[.CLASSCONSTANTHISTORY[n_table_event] = CCUPDATE_ENUM porigin_enum porigin_case_first pconfigcall.SITE n_table_prefix n_nonce]',
        'S_plain_table = S_after[.CLASSCONSTANTHISTORY[n_table_event] = CCUPDATE porigin_enum porigin_enum pconfigcall.SITE n_table_prefix]',
        'S_bad_table_owner = S_after[.SELECTEDCALLS[n_nonce] = pselectedcall[.OWNER = eps]]',
        'S_wrong_key = S_table[.TODO = (CLASS_CONST_TABLE_UPDATE porigin_enum z) :: (ENUM_FROM_FETCH pconfigcall (PINT 2)) :: ptask_table*]',
        'S_wrong_line = S_table[.TODO = (CLASS_CONST_TABLE_UPDATE porigin_enum $(z + 1)) :: (ENUM_FROM_FETCH pconfigcall (PINT 1)) :: ptask_table*]',
        'S_gap = S_table[.TODO = (CLASS_CONST_TABLE_UPDATE porigin_enum z) :: DISCARD :: (ENUM_FROM_FETCH pconfigcall (PINT 1)) :: ptask_table*]',
        'S_finish = $drive_steps(S_after,5000)',
    ]
    return checks + [
        '$call_descriptors_valid(S_table)',
        '$class_constant_history_valid(S_table)',
        '$class_constant_table_task(S_table,porigin_enum,z,S_table.TODO)',
        '$class_constant_update_site(S_table,pconfigcall.SITE,porigin_enum)',
        '$enum_backing_issue(S_table,porigin_enum) = METHOD_OK',
        '~$class_constant_table_done(S_table,porigin_enum)',
        '$call_descriptors_valid(S_after)',
        '$class_constant_history_valid(S_after)',
        '$class_constant_table_done(S_after,porigin_enum)',
        '$call_tasks_valid(S_after,S_after.TODO)',
        'S_after.CLASSCONSTANTCACHE = S_table.CLASSCONSTANTCACHE',
        'S_after.SELECTEDCALLS = S_table.SELECTEDCALLS',
        '~$class_constant_history_valid(S_bad_table_nonce)',
        '~$class_constant_history_valid(S_bad_table_root)',
        '~$class_constant_history_valid(S_plain_table)',
        '~$class_constant_history_valid(S_bad_table_owner)',
        '$enum_owned_from_table_context(S_wrong_key,porigin_enum,porigin_enum,pconfigcall.SITE) = eps',
        '~$call_task_valid(S_wrong_line,CLASS_CONST_TABLE_UPDATE porigin_enum $(z + 1))',
        '$enum_owned_from_table_context(S_gap,porigin_enum,porigin_enum,pconfigcall.SITE) = eps',
        'S_finish.COMPLETION = NORMAL',
        '~((HOBJECT n_closure) <- S_finish.ALLOCATIONS)',
        '$selected_entry_source_valid(S_finish,pselectedcall)',
        '$class_constant_history_valid(S_finish)',
        '$call_descriptors_valid(S_finish)',
        '$enumr_output(S_finish.EVENTS) = $ptascii("READY|One:Two:null|dead|same|")',
    ]


def _alias(main_fixture, source_path, expected_bytes):
    checks = [
        'S_initial = $php_file_run(' + main_fixture + ',0,' + term(str(source_path).encode()) + ',' + term(str(source_path.parent).encode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $alias_seek(S_initial,3000)',
        'S_found.COMPLETION = NORMAL \\/ S_found.COMPLETION = BUDGET',
        'S_bind = $enumr_running(S_found)',
        'S_bind.TODO = (CLASS_CONST_BIND porigin_alias) :: ptask_tail*',
        '$class_constant_origin(S_bind.CLASSES,porigin_alias) = (pclassconstantdesc)',
        'pclassconstantdesc.NAME = $base64("QWxpYXM=")',
        'S_bind.CLASSCONSTANTINIT = pclassconstantcontext :: eps',
        'pclassconstantcontext.DECL = porigin_alias',
        'pclassconstantcontext.SELECTION = CLASS_CONST_UPDATE_SELECT porigin_enum',
        '$enum_from_future(S_bind.TODO) = (pconfigcall)',
        'pconfigcall.KIND = INTRINSIC_ENUM porigin_enum ($ptascii("ReviewFromConstants")) "from"',
        'pconfigcall.OWNER = (n_closure)',
        'pconfigcall.SELECTION = (n_nonce)',
        'pclassconstantcontext.ORIGIN = (porigin_trigger)',
        'n_prefix = |S_bind.DECLARATIONS|',
        '$enum_from_update_context(S_bind,pclassconstantcontext,porigin_alias) = (pconfigcall)',
        'n_event = |S_bind.CLASSCONSTANTHISTORY|',
        'S_zero = $drive_steps(S_bind,0)',
        'S_bound_found = $drive_steps(S_bind,1)',
        'S_bound_found.COMPLETION = BUDGET',
        'S_bound = $enumr_running(S_bound_found)',
        'S_bound.CLASSCONSTANTHISTORY[n_event] = CCCACHE_ENUM porigin_alias porigin_trigger n_prefix n_nonce',
        'S_bound.SELECTEDCALLS[n_nonce] = pselectedcall',
        'n_absent = |S_bound.SELECTEDCALLS|',
        'S_wrong_nonce = S_bound[.CLASSCONSTANTHISTORY[n_event] = CCCACHE_ENUM porigin_alias porigin_trigger n_prefix n_absent]',
        'S_wrong_decl = S_bound[.CLASSCONSTANTHISTORY[n_event] = CCCACHE_ENUM porigin_enum porigin_trigger n_prefix n_nonce]',
        'S_wrong_site = S_bound[.CLASSCONSTANTHISTORY[n_event] = CCCACHE_ENUM porigin_alias porigin_alias n_prefix n_nonce]',
        'S_plain = S_bound[.CLASSCONSTANTHISTORY[n_event] = CCCACHE porigin_alias porigin_trigger n_prefix]',
        'S_finish = $drive_steps(S_bound,5000)',
        'S_bind.CONSTCONTEXT = (pconstantcontext)',
        'pconstantcontext.FACTS = [pconstantfact]',
        'pconstantfact.VALUE = eps',
        'pconstantfact.CLASS = PVENUMCASE n_case porigin_case',
        'S_bind.OBJECTS[n_case] = ENUMCASE porigin_case',
    ]
    return checks + [
        '$constant_fact_value_valid(pconstantfact)',
        '$constant_fact_truth(pconstantfact) = (true)',
        'pconstantfact.VALUE = eps',
        '~$constant_fact_value_valid(pconstantfact[.VALUE = (POBJECT n_case)])',
        '$constant_context_valid(S_bind)',
        '~$enum_case_origin(S_bind,porigin_alias)',
        '~pclassconstantdesc.FOLDED',
        'pclassconstantdesc <- $class_constant_update_order(S_bind,porigin_enum,|S_bind.CLASSES|)',
        '$call_descriptors_valid(S_bind)',
        '$class_constant_context_site(S_bind,pclassconstantcontext)',
        '$class_constant_selection_valid(S_bind,pclassconstantcontext)',
        '$config_invoke_valid(S_bind[.ORIGIN = (pconfigcall.SITE)],pconfigcall)',
        '$enumr_output(S_bind.EVENTS) = $base64("Q0FQfA==")',
        'S_zero = S_bind[.COMPLETION = BUDGET]',
        '$enumr_running(S_zero) = S_bind',
        '$class_constant_cache_event(S_bind,pclassconstantcontext,porigin_alias,porigin_trigger,n_prefix) = CCCACHE_ENUM porigin_alias porigin_trigger n_prefix n_nonce',
        '$class_constant_history_valid(S_bound)',
        '$call_descriptors_valid(S_bound)',
        'S_bound.SELECTEDCALLS = S_bind.SELECTEDCALLS',
        '$selected_entry_source_valid(S_bound,pselectedcall)',
        '~$class_constant_history_valid(S_wrong_nonce)',
        '~$class_constant_history_valid(S_wrong_decl)',
        '~$class_constant_history_valid(S_wrong_site)',
        '~$class_constant_history_valid(S_plain)',
        'S_finish.COMPLETION = NORMAL',
        '$enumr_output(S_finish.EVENTS) = ' + term(expected_bytes),
        '$call_descriptors_valid(S_finish)',
        '$class_constant_history_valid(S_finish)',
    ]


def _inherited(main_fixture, source_path, expected_bytes):
    checks = [
        'S_initial = $php_file_run(' + main_fixture + ',0,' + term(str(source_path).encode()) + ',' + term(str(source_path.parent).encode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $alias_seek(S_initial,3000)',
        'S_found.COMPLETION = NORMAL \\/ S_found.COMPLETION = BUDGET',
        'S_bind = $enumr_running(S_found)',
        'S_bind.TODO = (CLASS_CONST_BIND porigin_alias) :: ptask_tail*',
        '$class_constant_origin(S_bind.CLASSES,porigin_alias) = (pclassconstantdesc)',
        'pclassconstantdesc.NAME = $base64("QWxpYXM=")',
        'S_bind.CLASSCONSTANTINIT = pclassconstantcontext :: eps',
        'pclassconstantcontext.DECL = porigin_alias',
        'pclassconstantcontext.SELECTION = CLASS_CONST_UPDATE_SELECT porigin_enum',
        '$enum_from_future(S_bind.TODO) = (pconfigcall)',
        'pconfigcall.KIND = INTRINSIC_ENUM porigin_enum ($ptascii("ReviewInheritedLookup")) "from"',
        'pconfigcall.OWNER = (n_closure)',
        'pconfigcall.SELECTION = (n_nonce)',
        'pclassconstantcontext.ORIGIN = (porigin_trigger)',
        'n_prefix = |S_bind.DECLARATIONS|',
        '$class_at(S_bind.CLASSES,pclassconstantdesc.OWNER) = (pclassdesc_declaring)',
        '$class_at(S_bind.CLASSES,porigin_enum) = (pclassdesc_selected)',
        '$enum_from_update_context(S_bind,pclassconstantcontext,porigin_alias) = (pconfigcall)',
        'n_event = |S_bind.CLASSCONSTANTHISTORY|',
        'S_zero = $drive_steps(S_bind,0)',
        'S_bound_found = $drive_steps(S_bind,1)',
        'S_bound_found.COMPLETION = BUDGET',
        'S_bound = $enumr_running(S_bound_found)',
        'S_bound.CLASSCONSTANTHISTORY[n_event] = CCCACHE_ENUM porigin_alias porigin_trigger n_prefix n_nonce',
        'S_bound.SELECTEDCALLS[n_nonce] = pselectedcall',
        'n_absent = |S_bound.SELECTEDCALLS|',
        'S_wrong_nonce = S_bound[.CLASSCONSTANTHISTORY[n_event] = CCCACHE_ENUM porigin_alias porigin_trigger n_prefix n_absent]',
        'S_wrong_decl = S_bound[.CLASSCONSTANTHISTORY[n_event] = CCCACHE_ENUM porigin_enum porigin_trigger n_prefix n_nonce]',
        'S_wrong_site = S_bound[.CLASSCONSTANTHISTORY[n_event] = CCCACHE_ENUM porigin_alias porigin_alias n_prefix n_nonce]',
        'S_plain = S_bound[.CLASSCONSTANTHISTORY[n_event] = CCCACHE porigin_alias porigin_trigger n_prefix]',
        'S_finish = $drive_steps(S_bound,5000)',
        'S_bind.CONSTCONTEXT = (pconstantcontext)',
        'pconstantcontext.FACTS = [pconstantfact]',
        'pconstantfact.VALUE = eps',
        'pconstantfact.CLASS = PVENUMCASE n_case porigin_case',
        'S_bind.OBJECTS[n_case] = ENUMCASE porigin_case',
        'pclassconstantcontext_wrong = pclassconstantcontext[.SELECTION = CLASS_CONST_UPDATE_SELECT pclassconstantdesc.OWNER]',
        'S_wrong_selected_root = S_bound[.SELECTEDCALLS[n_nonce] = pselectedcall[.KIND = INTRINSIC_ENUM pclassconstantdesc.OWNER pclassconstantdesc.OWNERNAME "from"]]',
    ]
    return checks + [
        'pclassdesc_declaring.KIND = "interface"',
        'pclassdesc_selected.KIND = "enum"',
        'pclassconstantdesc.OWNER =/= porigin_enum',
        'pclassconstantdesc <- $class_constant_layout(S_bind,porigin_enum,|S_bind.CLASSES|)',
        '$enum_from_update_context(S_bind,pclassconstantcontext_wrong,porigin_alias) = eps',
        '~$class_constant_history_valid(S_wrong_selected_root)',
        '$constant_fact_value_valid(pconstantfact)',
        '$constant_fact_truth(pconstantfact) = (true)',
        'pconstantfact.VALUE = eps',
        '~$constant_fact_value_valid(pconstantfact[.VALUE = (POBJECT n_case)])',
        '$constant_context_valid(S_bind)',
        '~$enum_case_origin(S_bind,porigin_alias)',
        '~pclassconstantdesc.FOLDED',
        'pclassconstantdesc <- $class_constant_update_order(S_bind,porigin_enum,|S_bind.CLASSES|)',
        '$call_descriptors_valid(S_bind)',
        '$class_constant_context_site(S_bind,pclassconstantcontext)',
        '$class_constant_selection_valid(S_bind,pclassconstantcontext)',
        '$config_invoke_valid(S_bind[.ORIGIN = (pconfigcall.SITE)],pconfigcall)',
        '$enumr_output(S_bind.EVENTS) = $base64("Q09MRHw=")',
        'S_zero = S_bind[.COMPLETION = BUDGET]',
        '$enumr_running(S_zero) = S_bind',
        '$class_constant_cache_event(S_bind,pclassconstantcontext,porigin_alias,porigin_trigger,n_prefix) = CCCACHE_ENUM porigin_alias porigin_trigger n_prefix n_nonce',
        '$class_constant_history_valid(S_bound)',
        '$call_descriptors_valid(S_bound)',
        'S_bound.SELECTEDCALLS = S_bind.SELECTEDCALLS',
        '$selected_entry_source_valid(S_bound,pselectedcall)',
        '~$class_constant_history_valid(S_wrong_nonce)',
        '~$class_constant_history_valid(S_wrong_decl)',
        '~$class_constant_history_valid(S_wrong_site)',
        '~$class_constant_history_valid(S_plain)',
        'S_finish.COMPLETION = NORMAL',
        '$enumr_output(S_finish.EVENTS) = ' + term(expected_bytes),
        '$call_descriptors_valid(S_finish)',
        '$class_constant_history_valid(S_finish)',
    ]


def _strict(main_fixture, source_path, expected_bytes, file_snapshot, factory_fixture):
    entry, = file_snapshot['entries']
    opened = '(FILE_OPENED 0 ' + ' '.join(term(base64.b64decode(entry[key]))
        for key in ('caller', 'requested', 'resolved', 'opened', 'source')) + ')'
    accepted = '(SOURCE_ACCEPT 1 ' + term(base64.b64decode(entry['source'])) + ' ' + factory_fixture + ')'
    expected = expected_bytes.split(b'A:', 1)[0]
    assert expected == b'W:One|S:ReviewCallableEnum::from(): Argument #1 ($value) must be of type string, int given|'
    checks = [
        'S_open = $php_file_run(' + main_fixture + ',5000,' + term(str(source_path).encode()) + ',' + term(base64.b64decode(file_snapshot['cwd'])) + ')',
        'S_open.COMPLETION = SOURCE_PENDING',
        '$file_open_response_valid(S_open,' + opened + ')',
        'S_parse = $file_open_continue(S_open,' + opened + ')',
        'S_parse.COMPLETION = SOURCE_PENDING',
        '$file_parse_response_valid(S_parse,' + accepted + ')',
        'S_seed = $file_parse_resume(S_parse,' + accepted + ')',
        'S_seed.COMPLETION = NORMAL',
        'S_weak_found = $strict_seek(S_seed,0,$base64("VzpPbmV8UzpSZXZpZXdDYWxsYWJsZUVudW06OmZyb20oKTogQXJndW1lbnQgIzEgKCR2YWx1ZSkgbXVzdCBiZSBvZiB0eXBlIHN0cmluZywgaW50IGdpdmVufA=="),3000)',
        'S_weak_found.COMPLETION = NORMAL \\/ S_weak_found.COMPLETION = BUDGET',
        'S_weak = $enumr_running(S_weak_found)',
        '$strict_front(S_weak,0,$base64("VzpPbmV8UzpSZXZpZXdDYWxsYWJsZUVudW06OmZyb20oKTogQXJndW1lbnQgIzEgKCR2YWx1ZSkgbXVzdCBiZSBvZiB0eXBlIHN0cmluZywgaW50IGdpdmVufA=="))',
        'S_weak.TODO = (CONFIG_INVOKE pconfigcall_weak) :: ptask_weak*',
        'pconfigcall_weak.KIND = INTRINSIC_ENUM porigin_enum ptbytes_name "from"',
        'pconfigcall_weak.OWNER = (n_closure)',
        'pconfigcall_weak.SELECTION = (n_weak_nonce)',
        'pconfigcall_weak.SITE = PORIGIN 0 pcpath_weak',
        'pconfigcall_weak.SENT = [NAMED_SENT (KNOWN (PINT 1))]',
        '$code_at(S_weak.CODE,0) = (pcode_weak)',
        '$code_at(S_weak.CODE,1) = (pcode_strict)',
        'S_strict_found = $strict_seek(S_weak,1,$base64("VzpPbmV8UzpSZXZpZXdDYWxsYWJsZUVudW06OmZyb20oKTogQXJndW1lbnQgIzEgKCR2YWx1ZSkgbXVzdCBiZSBvZiB0eXBlIHN0cmluZywgaW50IGdpdmVufA=="),3000)',
        'S_strict_found.COMPLETION = NORMAL \\/ S_strict_found.COMPLETION = BUDGET',
        'S_strict = $enumr_running(S_strict_found)',
        '$strict_front(S_strict,1,$base64("VzpPbmV8UzpSZXZpZXdDYWxsYWJsZUVudW06OmZyb20oKTogQXJndW1lbnQgIzEgKCR2YWx1ZSkgbXVzdCBiZSBvZiB0eXBlIHN0cmluZywgaW50IGdpdmVufA=="))',
        'S_strict.TODO = (CONFIG_INVOKE pconfigcall_strict) :: ptask_strict*',
        'pconfigcall_strict.KIND = pconfigcall_weak.KIND',
        'pconfigcall_strict.OWNER = (n_closure)',
        'pconfigcall_strict.SELECTION = (n_strict_nonce)',
        'pconfigcall_strict.SITE = PORIGIN 1 pcpath_strict',
        'pconfigcall_strict.SENT = [NAMED_SENT (KNOWN (PINT 1))]',
        'S_strict.SELECTEDCALLS[n_weak_nonce] = pselectedcall_weak',
        'S_strict.SELECTEDCALLS[n_strict_nonce] = pselectedcall_strict',
        'S_prefix_found = $strict_seek(S_strict,2,$base64("VzpPbmV8UzpSZXZpZXdDYWxsYWJsZUVudW06OmZyb20oKTogQXJndW1lbnQgIzEgKCR2YWx1ZSkgbXVzdCBiZSBvZiB0eXBlIHN0cmluZywgaW50IGdpdmVufA=="),3000)',
        'S_prefix_found.COMPLETION = NORMAL \\/ S_prefix_found.COMPLETION = BUDGET',
        'S_prefix = $enumr_running(S_prefix_found)',
        '$strict_front(S_prefix,2,$base64("VzpPbmV8UzpSZXZpZXdDYWxsYWJsZUVudW06OmZyb20oKTogQXJndW1lbnQgIzEgKCR2YWx1ZSkgbXVzdCBiZSBvZiB0eXBlIHN0cmluZywgaW50IGdpdmVufA=="))',
    ]
    return checks + [
        '~pcode_weak.STRICT',
        'pcode_strict.STRICT',
        '~$config_strict(S_weak,pconfigcall_weak)',
        '$config_strict(S_strict,pconfigcall_strict)',
        'S_weak.OBJECTS[n_closure] = S_strict.OBJECTS[n_closure]',
        '$enum_closure_valid(S_weak,n_closure,pconfigcall_weak.KIND)',
        '$call_descriptors_valid(S_weak)',
        '$config_selected_valid(S_weak,pconfigcall_weak)',
        '$config_invoke_valid(S_weak,pconfigcall_weak)',
        '$enum_from_convertible($enum_from_parse(S_weak,pconfigcall_weak,PINT 1))',
        '~$class_constant_table_done(S_weak,porigin_enum)',
        '$call_descriptors_valid(S_strict)',
        '$config_selected_valid(S_strict,pconfigcall_strict)',
        '$config_invoke_valid(S_strict,pconfigcall_strict)',
        '$enum_from_parse(S_strict,pconfigcall_strict,PINT 1) = TYPEREJECT',
        '$class_constant_table_done(S_strict,porigin_enum)',
        'n_weak_nonce =/= n_strict_nonce',
        'pselectedcall_weak.SITE = pconfigcall_weak.SITE',
        'pselectedcall_strict.SITE = pconfigcall_strict.SITE',
        'pselectedcall_weak.OWNER = (n_closure)',
        'pselectedcall_strict.OWNER = (n_closure)',
        'S_prefix.COMPLETION = NORMAL',
        '$call_descriptors_valid(S_prefix)',
        '$call_descriptors_local_valid(S_prefix)',
        '$call_tasks_valid(S_prefix,S_prefix.TODO)',
        '$call_frames_valid(S_prefix,S_prefix.FRAMES)',
        '$class_constant_state_valid(S_prefix)',
        '$class_constant_history_valid(S_prefix)',
        '$enumr_output(S_prefix.EVENTS) = $base64("VzpPbmV8UzpSZXZpZXdDYWxsYWJsZUVudW06OmZyb20oKTogQXJndW1lbnQgIzEgKCR2YWx1ZSkgbXVzdCBiZSBvZiB0eXBlIHN0cmluZywgaW50IGdpdmVufA==")',
    ]


def _stringable(main_fixture, source_path, expected_bytes):
    assert expected_bytes == b'READY|CAST|DROP|V:Only|'
    checks = [
        'S_initial = $php_file_run(' + main_fixture + ',0,' + term(str(source_path).encode()) + ',' + term(str(source_path.parent).encode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_config_found = $ostr_seek(S_initial,0,3000)',
        'S_config_found.COMPLETION = NORMAL \\/ S_config_found.COMPLETION = BUDGET',
        'S_config = $enumr_running(S_config_found)',
        'S_config.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
        'pconfigcall.KIND = INTRINSIC_ENUM porigin_enum ($ptascii("ReviewOwnedTextLookup")) "from"',
        'pconfigcall.OWNER = (n_closure)',
        'pconfigcall.SELECTION = (n_nonce)',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN (POBJECT n_text))]',
        '$config_string_source(S_config,pconfigcall) = ((porigin_child,z_child))',
        'z_call = pconfigcall.LINE',
        'S_dead = S_config[.ALLOCATIONS = $destruction_node_delete(S_config.ALLOCATIONS,HOBJECT n_text)]',
        'S_dead_owner = S_config[.ALLOCATIONS = $destruction_node_delete(S_config.ALLOCATIONS,HOBJECT n_closure)]',
        'n_absent = |S_config.SELECTEDCALLS|',
        'S_cast_found = $ostr_seek(S_config,3,3000)',
        'S_cast_found.COMPLETION = NORMAL \\/ S_cast_found.COMPLETION = BUDGET',
        'S_cast = $enumr_running(S_cast_found)',
        'S_cast.CURRENT = (pcallcontext)',
        'pcallcontext.RECEIVER = (n_text)',
        'S_result_found = $ostr_seek(S_cast,1,3000)',
        'S_result_found.COMPLETION = NORMAL \\/ S_result_found.COMPLETION = BUDGET',
        'S_result = $enumr_running(S_result_found)',
        'S_result.TODO = (ENUM_FROM_STRING_RESULT pconfigcall n_text porigin_child z_child z_call) :: ptask_result*',
        'S_result.RESULT = KNOWN pvalue_text',
        '$string_bytes(pvalue_text) = ($ptascii("1"))',
        'S_zero = $drive_steps(S_result,0)',
        'S_retire_found = $drive_steps(S_result,1)',
        'S_retire_found.COMPLETION = BUDGET',
        'S_retire = $enumr_running(S_retire_found)',
        'S_queue_found = $ostr_seek(S_retire,2,3000)',
        'S_queue_found.COMPLETION = NORMAL \\/ S_queue_found.COMPLETION = BUDGET',
        'S_queue = $enumr_running(S_queue_found)',
        '$enum_from_future(S_queue.TODO) = (pconfigcall_parsed)',
        'pconfigcall_parsed = pconfigcall[.SENT = [NAMED_SENT (KNOWN pvalue_text)]]',
        'S_finish = $drive_steps(S_queue,5000)',
        'z_child =/= z_call',
    ]
    return checks + [
        '$call_descriptors_valid(S_config)',
        '$config_selected_valid(S_config,pconfigcall)',
        '$enum_string_site_valid(S_config,pconfigcall,n_text,porigin_child,z_child,z_call)',
        '~$enum_string_site_valid(S_config,pconfigcall,n_text,pconfigcall.SITE,z_child,z_call)',
        '~$enum_string_site_valid(S_config,pconfigcall,n_text,porigin_child,$(z_child + 1),z_call)',
        '~$enum_string_site_valid(S_config,pconfigcall,n_text,porigin_child,z_child,$(z_call + 1))',
        '~$enum_string_site_valid(S_config,pconfigcall,n_closure,porigin_child,z_child,z_call)',
        '~$enum_string_site_valid(S_config,pconfigcall[.SELECTION = (n_absent)],n_text,porigin_child,z_child,z_call)',
        '~$enum_string_site_valid(S_config,pconfigcall[.KIND = INTRINSIC_ENUM porigin_enum ($ptascii("ReviewOwnedTextLookup")) "tryFrom"],n_text,porigin_child,z_child,z_call)',
        '~$enum_string_site_valid(S_dead,pconfigcall,n_text,porigin_child,z_child,z_call)',
        '~$enum_string_site_valid(S_dead_owner,pconfigcall,n_text,porigin_child,z_child,z_call)',
        '$call_descriptors_valid(S_cast)',
        '$call_frames_valid(S_cast,S_cast.FRAMES)',
        '$call_current_valid(S_cast)',
        '(HOBJECT n_text) <- S_cast.ALLOCATIONS',
        '(HOBJECT n_closure) <- S_cast.ALLOCATIONS',
        '$call_descriptors_valid(S_result)',
        '$enum_string_site_valid(S_result,pconfigcall,n_text,porigin_child,z_child,z_call)',
        '(HOBJECT n_text) <- S_result.ALLOCATIONS',
        '(HOBJECT n_closure) <- S_result.ALLOCATIONS',
        '(HOBJECT n_text) <- $task_nodes(ENUM_FROM_STRING_RESULT pconfigcall n_text porigin_child z_child z_call)',
        '(HOBJECT n_closure) <- $task_nodes(ENUM_FROM_STRING_RESULT pconfigcall n_text porigin_child z_child z_call)',
        '$method_string(pvalue_text)',
        '$enumr_output(S_result.EVENTS) = $ptascii("READY|CAST|")',
        'S_result.CLASSCONSTANTCACHE = eps',
        'S_zero = S_result[.COMPLETION = BUDGET]',
        '$enumr_running(S_zero) = S_result',
        '$call_descriptors_valid(S_queue)',
        '~((HOBJECT n_text) <- S_queue.ALLOCATIONS)',
        '(HOBJECT n_closure) <- S_queue.ALLOCATIONS',
        'S_queue.CLASSCONSTANTCACHE = eps',
        'pconfigcall_parsed.SELECTION = (n_nonce)',
        '$enum_from_fetch_valid(S_queue,pconfigcall_parsed,pvalue_text)',
        '$enumr_output(S_queue.EVENTS) = $ptascii("READY|CAST|DROP|")',
        'S_finish.COMPLETION = NORMAL',
        '$enumr_output(S_finish.EVENTS) = $ptascii("READY|CAST|DROP|V:Only|")',
        '$call_descriptors_valid(S_finish)',
        '$class_constant_history_valid(S_finish)',
    ]


def _conditional(main_fixture, source_path, expected_bytes):
    assert expected_bytes == b'COLD|selected|distinct|'
    checks = [
        'S_initial = $php_file_run(' + main_fixture + ',0,' + term(str(source_path).encode()) + ',' + term(str(source_path.parent).encode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $cc_seek(S_initial,3000)',
        'S_found.COMPLETION = NORMAL \\/ S_found.COMPLETION = BUDGET',
        'S_bind = $enumr_running(S_found)',
        'S_bind.TODO = (CLASS_CONST_BIND porigin_decl) :: ptask_tail*',
        '$class_constant_origin(S_bind.CLASSES,porigin_decl) = (pclassconstantdesc)',
        'S_bind.CONSTCONTEXT = (pconstantcontext)',
        '$origin_node(S_bind.SOURCES,pclassconstantdesc.INITIALIZER) = (NExprTernary expression_condition expression_true expression_false metadata)',
        'porigin_condition = $constant_child(pclassconstantdesc.INITIALIZER,[PCFIELD 0])',
        'porigin_true = $constant_child(pclassconstantdesc.INITIALIZER,[PCFIELD 1])',
        'porigin_false = $constant_child(pclassconstantdesc.INITIALIZER,[PCFIELD 2])',
        '$constant_fact_at(pconstantcontext.FACTS,porigin_condition) = (pconstantfact_condition)',
        'pconstantfact_condition.CLASS = PVENUMCASE n_case porigin_case',
        '$constant_fact_at(pconstantcontext.FACTS,porigin_true) = (pconstantfact_selected)',
        'pvalueclass = $constant_class(S_bind,pclassconstantdesc.INITIALIZER)',
        '$constant_callable_alias(S_bind,porigin_condition,pclassconstantdesc.OWNER,|S_bind.DECLARATIONS|) = (pclassconstantdesc_condition)',
        '$constant_callable_alias_class(S_bind,pclassconstantdesc_condition) = (pvalueclass_condition)',
        '$default_cache_at(S_bind.CLASSCONSTANTCACHE,pclassconstantdesc_condition.ORIGIN) = (pdefaultcache_condition)',
        'n_prefix = |S_bind.DECLARATIONS|',
        '$constant_callable_alias(S_bind,porigin_true,pclassconstantdesc.OWNER,n_prefix) = (pclassconstantdesc_left)',
        '$constant_callable_alias_class(S_bind,pclassconstantdesc_left) = (pvalueclass_left)',
        'pvalueclass_left = pvalueclass',
        '$constant_callable_alias(S_bind,porigin_false,pclassconstantdesc.OWNER,n_prefix) = (pclassconstantdesc_right)',
        '$constant_callable_alias_class(S_bind,pclassconstantdesc_right) = (pvalueclass_right)',
        '$default_cache_at(S_bind.CLASSCONSTANTCACHE,pclassconstantdesc_right.ORIGIN) = (pdefaultcache_right)',
        '$constant_fact_at(pconstantcontext.FACTS,pclassconstantdesc.INITIALIZER) = (pconstantfact_root)',
        'S_wrong_class = S_bind[.RESULT = KNOWN pdefaultcache_right.VALUE][.CONSTCONTEXT = (pconstantcontext[.FACTS = $constant_fact_put(pconstantcontext.FACTS,pconstantfact_root[.CLASS = pvalueclass_right])])]',
        'pconstantfact_false = pconstantfact_condition[.VALUE = (PBOOL false)][.CLASS = PVSCALAR]',
        'pconstantfact_wrong_arm = pconstantfact_selected[.ORIGIN = porigin_false][.CLASS = pvalueclass_right]',
        'pconstantfact_wrong_root = pconstantfact_root[.CLASS = pvalueclass_right]',
        'S_false_facts = S_bind[.RESULT = KNOWN pdefaultcache_right.VALUE][.CONSTCONTEXT = (pconstantcontext[.FACTS = [pconstantfact_false,pconstantfact_wrong_arm,pconstantfact_wrong_root]])]',
        'S_reject = $drive_steps(S_false_facts,1)',
        'S_bound_found = $drive_steps(S_bind,1)',
        'S_bound_found.COMPLETION = BUDGET',
        'S_bound = $enumr_running(S_bound_found)',
        '$default_cache_at(S_bound.CLASSCONSTANTCACHE,porigin_decl) = (pdefaultcache_alias)',
        '$constant_callable_cache_prefix(S_bound.CLASSCONSTANTHISTORY,porigin_case) = (n_case_prefix)',
        '$(n_case_prefix > 0)',
        'n_early = $nabs($(n_case_prefix - 1))',
        'S_no_history = S_bound[.CLASSCONSTANTHISTORY = $cc_without_cache(S_bound.CLASSCONSTANTHISTORY,porigin_case)]',
        'S_finish = $drive_steps(S_bound,5000)',
    ]
    return checks + [
        '$call_descriptors_valid(S_bind)',
        'pclassconstantdesc_condition.OWNER =/= pclassconstantdesc.OWNER',
        '$enum_case_alias_valid(S_bind,porigin_condition,pclassconstantdesc.OWNER,pvalueclass_condition,n_prefix)',
        '$enum_case_condition_truth(S_bind,porigin_condition,pclassconstantdesc.OWNER,n_prefix) = (true)',
        '~$constant_callable_foldable(pvalueclass_condition)',
        '$constant_value_class_valid(S_bind,pdefaultcache_right.VALUE,pvalueclass_right)',
        '$enum_case_alias_valid(S_bind,porigin_false,pclassconstantdesc.OWNER,pvalueclass_right,n_prefix)',
        '$constant_callable_flow(S_bind,porigin_false,pclassconstantdesc.OWNER,pvalueclass_right,n_prefix,eps)',
        'pvalueclass_left =/= pvalueclass_right',
        '$constant_callable_flow(S_bind,porigin_true,pclassconstantdesc.OWNER,pvalueclass_left,n_prefix,eps)',
        '$constant_callable_flow(S_bind,pclassconstantdesc.INITIALIZER,pclassconstantdesc.OWNER,pvalueclass_left,n_prefix,eps)',
        '~$constant_callable_flow(S_bind,pclassconstantdesc.INITIALIZER,pclassconstantdesc.OWNER,pvalueclass_right,n_prefix,eps)',
        '~$enum_case_alias_valid(S_bind,porigin_condition,pclassconstantdesc.OWNER,pvalueclass_right,n_prefix)',
        '~$enum_case_alias_valid(S_bind,porigin_false,pclassconstantdesc.OWNER,pvalueclass_left,n_prefix)',
        '$constant_value_class_valid(S_wrong_class,pdefaultcache_right.VALUE,pvalueclass_right)',
        '~$constant_callable_cache_valid(S_wrong_class,pclassconstantdesc,pvalueclass_right,n_prefix)',
        '$constant_context_valid(S_false_facts)',
        '$constant_value_class_valid(S_false_facts,pdefaultcache_right.VALUE,pvalueclass_right)',
        '$constant_recorded_truth(S_false_facts,porigin_condition) = (false)',
        '$enum_case_condition_truth(S_false_facts,porigin_condition,pclassconstantdesc.OWNER,n_prefix) = (true)',
        '~$constant_callable_cache_valid(S_false_facts,pclassconstantdesc,pvalueclass_right,n_prefix)',
        'S_reject.COMPLETION = UNSUPPORTED "uncertified class constant Closure transfer"',
        'S_bound.CONSTCONTEXT = eps',
        'pdefaultcache_alias.CLASS = pvalueclass_left',
        '$constant_value_class_valid(S_bound,pdefaultcache_alias.VALUE,pvalueclass_left)',
        '$constant_callable_cache_valid(S_bound,pclassconstantdesc,pvalueclass_left,n_prefix)',
        '$enum_case_alias_valid(S_bound,porigin_condition,pclassconstantdesc.OWNER,pvalueclass_condition,n_prefix)',
        '$call_descriptors_valid(S_bound)',
        '$class_constant_history_valid(S_bound)',
        '~$enum_case_alias_valid(S_no_history,porigin_condition,pclassconstantdesc.OWNER,pvalueclass_condition,n_prefix)',
        '~$constant_callable_cache_valid(S_no_history,pclassconstantdesc,pvalueclass_left,n_prefix)',
        '~$enum_case_alias_valid(S_bound,porigin_condition,pclassconstantdesc.OWNER,pvalueclass_condition,n_early)',
        'S_finish.COMPLETION = NORMAL',
        '$enumr_output(S_finish.EVENTS) = $ptascii("COLD|selected|distinct|")',
        '$call_descriptors_valid(S_finish)',
        '$class_constant_history_valid(S_finish)',
    ]


def _array_selected(main_fixture, source_path, expected_bytes):
    assert expected_bytes == b'ARG|selected|rebound|'
    checks=[
        'S_initial = $php_file_run('+main_fixture+',0,'+term(str(source_path).encode())+','+term(str(source_path.parent).encode())+')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $earr_seek(S_initial,0,3000)',
        'S_lookup = $enumr_running(S_found)',
        'S_lookup.TODO = (CALL_DYNAMIC porigin_site z_init z_call) :: ptask_tail*',
        'S_pre = $resolve_at(S_lookup,S_lookup.RESULT,z_init)',
        'S_pre.RESULT = KNOWN (PARRAY n_array)',
        '$array_enum_candidate(S_pre,n_array) = ((pintrinsic,ptbytes_class,ptbytes_method))',
        'pintrinsic = INTRINSIC_ENUM porigin_class ptbytes_canonical "from"',
        'S_pre.ARRAYS[n_array] = parray_source',
        'pvalue_forged_carrier = PSTRING_CARRIER (REQUEST_STRING (|S_pre.STRINGDATA|)) ptbytes_class',
        'parray_forged_carrier = parray_source[.ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_forged_carrier), ENTRY (KINT 1) (DIRECT (PSTRING ptbytes_method))]]',
        'n_after = $nabs($(n_array + 1))',
        'n_remaining = $nabs($(|S_pre.ARRAYS| - n_array - 1))',
        'S_carrier = S_pre[.ARRAYS = S_pre.ARRAYS[0:n_array] ++ [parray_forged_carrier] ++ S_pre.ARRAYS[n_after:n_remaining]]',
        'S_selected_found = $drive_steps(S_lookup,1)',
        'S_selected_found.COMPLETION = BUDGET',
        'S_selected = $enumr_running(S_selected_found)',
        'S_selected.TODO = (CONFIG_ARGS pconfigcall_selected) :: ptask_selected_tail*',
        'pconfigcall_selected.SELECTION = (n_nonce)',
        'S_selected.SELECTEDCALLS[n_nonce] = pselectedcall',
        '$intrinsic_argument(S_selected,porigin_site,0) = ((expression_arg,false,preqbytes_arg?,porigin_arg,z_arg))',
        '$class_named(S_selected.CLASSNAMES,$ptlc($ptascii("ReviewReboundCallableEnum"))) = (porigin_other)',
        '$enum_generated_kind(S_selected,porigin_other,$ptascii("from")) = (pintrinsic_other)',
        'pselectedcall_other = pselectedcall[.KIND = pintrinsic_other][.ORIGINAL = $ptascii("ReviewReboundCallableEnum")]',
        'S_wrong_record = S_selected[.SELECTEDCALLS = $earr_record(S_selected.SELECTEDCALLS,n_nonce,pselectedcall_other)]',
        'S_invoke_found = $earr_seek(S_selected,1,3000)',
        'S_invoke = $enumr_running(S_invoke_found)',
        'S_invoke.TODO = (CONFIG_INVOKE pconfigcall_invoke) :: ptask_invoke_tail*',
        'pconfigcall_invoke.KIND = pintrinsic',
        'pconfigcall_invoke.SELECTION = (n_nonce)',
        'S_budget0 = $drive_steps(S_invoke,0)',
        'S_table_found = $earr_seek(S_invoke,2,3000)',
        'S_table = $enumr_running(S_table_found)',
        'S_table.TODO = (ENUM_FROM_FETCH pconfigcall_fetch pvalue_key) :: ptask_fetch_tail*',
        'pconfigcall_fetch.KIND = pintrinsic',
        'pconfigcall_fetch.SELECTION = (n_nonce)',
        'S_second_found = $earr_seek($drive_steps(S_table,1),0,3000)',
        'S_second_lookup = $enumr_running(S_second_found)',
        'S_second_lookup.TODO = (CALL_DYNAMIC porigin_second z_second_init z_second_call) :: ptask_second_tail*',
        'S_second = $resolve_at(S_second_lookup,S_second_lookup.RESULT,z_second_init)',
        'S_second.RESULT = KNOWN (PARRAY n_second)',
        '$array_enum_candidate(S_second,n_second) = ((pintrinsic_second,ptbytes_second_class,ptbytes_second_method))',
        'S_finish = $drive_steps(S_second_lookup,5000)',
        'n_later = S_finish.SELECTSEQ',
        'pselectedcall_later = pselectedcall_other[.NONCE = n_later]',
        'S_later = S_finish[.SELECTSEQ = $(n_later + 1)][.SELECTEDCALLS = S_finish.SELECTEDCALLS ++ [pselectedcall_later]]',
        'S_wrong_history = S_later[.CLASSCONSTANTHISTORY = $earr_nonce(S_later.CLASSCONSTANTHISTORY,n_nonce,n_later)]',
    ]
    return checks + [
        '$call_descriptors_valid(S_lookup)',
        '$array_resolve(S_pre,n_array,ARRAY_DISPATCH) = ARRAYENUM pintrinsic ptbytes_class ptbytes_method',
        '$array_resolve(S_pre,n_array,ARRAY_ADMISSION) = ARRAYADMITTED',
        'ptbytes_class = $ptascii("\\\\rEvIeWsElEcTeDcAlLaBlEeNuM")',
        'ptbytes_method = $ptascii("fRoM")',
        '~$string_carrier_valid(S_carrier,pvalue_forged_carrier)',
        '$array_enum_candidate(S_carrier,n_array) = eps',
        '$call_descriptors_valid(S_selected)',
        '$selected_entry_source_valid(S_selected,pselectedcall)',
        '$selected_log_valid(S_selected,S_selected.SELECTEDCALLS,0)',
        'pconfigcall_selected.OWNER = eps /\\ pselectedcall.OWNER = eps',
        'pselectedcall.ORIGINAL = ptbytes_class',
        'pselectedcall.LOOKUP = ptbytes_method',
        'pconfigcall_selected.KIND = pintrinsic /\\ pselectedcall.KIND = pintrinsic',
        '$config_selected_valid(S_selected,pconfigcall_selected)',
        '$selected_entry_source_valid(S_wrong_record,pselectedcall_other)',
        '~$config_selected_valid(S_wrong_record,pconfigcall_selected)',
        '~$config_selected_valid(S_selected,pconfigcall_selected[.KIND = pintrinsic_other])',
        '~$config_selected_valid(S_selected,pconfigcall_selected[.SELECTION = (S_selected.SELECTSEQ)])',
        '~$config_selected_valid(S_selected,pconfigcall_selected[.LINE = $(z_call + 1)])',
        '~$selected_entry_source_valid(S_selected,pselectedcall[.ORIGINAL = $ptascii("ReviewReboundCallableEnum")])',
        '~$selected_entry_source_valid(S_selected,pselectedcall[.LOOKUP = $ptascii("cases")])',
        '~$selected_entry_source_valid(S_selected,pselectedcall[.SITE = porigin_arg][.LINE = z_arg])',
        '$enumr_output(S_invoke.EVENTS) = $ptascii("ARG|")',
        'pconfigcall_invoke.KIND = pintrinsic',
        '$config_invoke_valid(S_invoke,pconfigcall_invoke)',
        '$call_descriptors_valid(S_invoke)',
        'S_budget0.COMPLETION = BUDGET /\\ S_budget0.TODO = S_invoke.TODO /\\ S_budget0.SELECTEDCALLS = S_invoke.SELECTEDCALLS',
        '$enum_from_fetch_valid(S_table,pconfigcall_fetch,pvalue_key)',
        '$class_constant_table_done(S_table,porigin_class)',
        '$class_constant_history_valid(S_table)',
        '$call_descriptors_valid(S_table)',
        'pintrinsic_second = pintrinsic_other /\\ pintrinsic_second =/= pintrinsic',
        '$call_descriptors_valid(S_second_lookup)',
        'S_finish.COMPLETION = NORMAL',
        '$enumr_output(S_finish.EVENTS) = $ptascii("ARG|selected|rebound|")',
        '$call_descriptors_valid(S_finish)',
        '$class_constant_history_valid(S_finish)',
        '$selected_entry_source_valid(S_later,pselectedcall_later)',
        '$selected_log_valid(S_later,S_later.SELECTEDCALLS,0)',
        '$class_constant_history_valid(S_later)',
        '~$class_constant_history_valid(S_wrong_history)',
    ]


def _array_stringable(main_fixture, source_path, expected_bytes):
    assert expected_bytes == b'READY|CAST|DROP|selected|rebound|'
    checks = [
        'S_initial = $php_file_run(' + main_fixture + ',0,' + term(str(source_path).encode()) + ',' + term(str(source_path.parent).encode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_config_found = $ostr_seek(S_initial,0,3000)',
        'S_config_found.COMPLETION = NORMAL \\/ S_config_found.COMPLETION = BUDGET',
        'S_config = $enumr_running(S_config_found)',
        'S_config.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
        'pconfigcall.KIND = INTRINSIC_ENUM porigin_enum ($ptascii("ReviewArrayStringableSelected")) "from"',
        'pconfigcall.OWNER = eps',
        'pconfigcall.SELECTION = (n_nonce)',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN (POBJECT n_text))]',
        '$config_string_source(S_config,pconfigcall) = ((porigin_child,z_child))',
        'z_call = pconfigcall.LINE',
        'S_dead = S_config[.ALLOCATIONS = $destruction_node_delete(S_config.ALLOCATIONS,HOBJECT n_text)]',
        'n_absent = |S_config.SELECTEDCALLS|',
        'S_cast_found = $ostr_seek(S_config,3,3000)',
        'S_cast_found.COMPLETION = NORMAL \\/ S_cast_found.COMPLETION = BUDGET',
        'S_cast = $enumr_running(S_cast_found)',
        'S_cast.CURRENT = (pcallcontext)',
        'pcallcontext.RECEIVER = (n_text)',
        'S_result_found = $ostr_seek(S_cast,1,3000)',
        'S_result_found.COMPLETION = NORMAL \\/ S_result_found.COMPLETION = BUDGET',
        'S_result = $enumr_running(S_result_found)',
        'S_result.TODO = (ENUM_FROM_STRING_RESULT pconfigcall n_text porigin_child z_child z_call) :: ptask_result*',
        'S_result.RESULT = KNOWN pvalue_text',
        '$string_bytes(pvalue_text) = ($ptascii("01"))',
        'S_zero = $drive_steps(S_result,0)',
        'S_retire_found = $drive_steps(S_result,1)',
        'S_retire_found.COMPLETION = BUDGET',
        'S_retire = $enumr_running(S_retire_found)',
        'S_queue_found = $ostr_seek(S_retire,2,3000)',
        'S_queue_found.COMPLETION = NORMAL \\/ S_queue_found.COMPLETION = BUDGET',
        'S_queue = $enumr_running(S_queue_found)',
        '$enum_from_future(S_queue.TODO) = (pconfigcall_parsed)',
        'pconfigcall_parsed = pconfigcall[.SENT = [NAMED_SENT (KNOWN pvalue_text)]]',
        'S_finish = $drive_steps(S_queue,5000)',
        'z_child =/= z_call',
    ]
    return checks + [
        '$call_descriptors_valid(S_config)',
        'pconfigcall.OWNER = eps',
        '$config_selected_valid(S_config,pconfigcall)',
        '$enum_string_site_valid(S_config,pconfigcall,n_text,porigin_child,z_child,z_call)',
        '~$enum_string_site_valid(S_config,pconfigcall,n_text,pconfigcall.SITE,z_child,z_call)',
        '~$enum_string_site_valid(S_config,pconfigcall,n_text,porigin_child,$(z_child + 1),z_call)',
        '~$enum_string_site_valid(S_config,pconfigcall,n_text,porigin_child,z_child,$(z_call + 1))',
        '~$enum_string_site_valid(S_config,pconfigcall[.SELECTION = (n_absent)],n_text,porigin_child,z_child,z_call)',
        '~$enum_string_site_valid(S_config,pconfigcall[.KIND = INTRINSIC_ENUM porigin_enum ($ptascii("ReviewArrayStringableSelected")) "tryFrom"],n_text,porigin_child,z_child,z_call)',
        '~$enum_string_site_valid(S_dead,pconfigcall,n_text,porigin_child,z_child,z_call)',
        '$call_descriptors_valid(S_cast)',
        '$call_frames_valid(S_cast,S_cast.FRAMES)',
        '(HOBJECT n_text) <- S_cast.ALLOCATIONS',
        '$call_descriptors_valid(S_result)',
        '$enum_string_site_valid(S_result,pconfigcall,n_text,porigin_child,z_child,z_call)',
        '(HOBJECT n_text) <- S_result.ALLOCATIONS',
        '(HOBJECT n_text) <- $task_nodes(ENUM_FROM_STRING_RESULT pconfigcall n_text porigin_child z_child z_call)',
        '$enumr_output(S_result.EVENTS) = $ptascii("READY|CAST|")',
        'S_result.CLASSCONSTANTCACHE = eps',
        'S_zero = S_result[.COMPLETION = BUDGET]',
        '$call_descriptors_valid(S_queue)',
        '~((HOBJECT n_text) <- S_queue.ALLOCATIONS)',
        'S_queue.CLASSCONSTANTCACHE = eps',
        'pconfigcall_parsed.SELECTION = (n_nonce)',
        '$enum_from_fetch_valid(S_queue,pconfigcall_parsed,pvalue_text)',
        '$task_nodes(ENUM_FROM_FETCH pconfigcall_parsed pvalue_text) = eps',
        '$enumr_output(S_queue.EVENTS) = $ptascii("READY|CAST|DROP|")',
        'S_finish.COMPLETION = NORMAL',
        '$enumr_output(S_finish.EVENTS) = $ptascii("READY|CAST|DROP|selected|rebound|")',
        '$call_descriptors_valid(S_finish)',
        '$class_constant_history_valid(S_finish)',
    ]
