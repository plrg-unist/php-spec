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
}


def prefix(case_id):
    return CASE_PREFIX + _FRONTS[case_id]


def assertions(case_id, main_fixture, source_path, expected_bytes,
               file_snapshot=None, factory_fixture=None):
    if case_id == 'callable-caller-strictness-prefix':
        return _strict(main_fixture, source_path, expected_bytes, file_snapshot, factory_fixture)
    return {
        'lazy-table-retired-owners': _table,
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
