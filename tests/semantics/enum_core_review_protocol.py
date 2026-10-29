#!/usr/bin/env python3
"""Independent source-reached case identity, cache ownership and retry checks."""
import base64
import json


def term(data):
    return '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'


PREFIX = r'''
dec $enumr_running(pstate) : pstate
def $enumr_running(S) = S[.COMPLETION = NORMAL] -- if S.COMPLETION = BUDGET
def $enumr_running(S) = S -- otherwise
dec $enumr_output_item(pevent) : ptbytes
def $enumr_output_item(OUTPUT ptbytes) = ptbytes
def $enumr_output_item(pevent) = eps -- otherwise
dec $enumr_output(pevent*) : ptbytes
def $enumr_output(eps) = eps
def $enumr_output(pevent :: pevent_tail*) = $enumr_output_item(pevent) ++ $enumr_output(pevent_tail*)
dec $enumr_front(pstate, ptbytes, nat) : bool
def $enumr_front(S, ptbytes_owner, 0) = true
  -- if S.TODO = (ENUM_CASE_INIT porigin) :: ptask_tail*
  -- if $enum_case_descriptor(S,porigin) = (pclassconstantdesc)
  -- if pclassconstantdesc.OWNERNAME = ptbytes_owner
def $enumr_front(S, ptbytes_owner, 1) = true
  -- if S.TODO = (CLASS_CONST_TABLE_UPDATE porigin z) :: ptask_tail*
  -- if $class_at(S.CLASSES,porigin) = (pclassdesc)
  -- if pclassdesc.KIND = "enum" /\ pclassdesc.NAME = ptbytes_owner
def $enumr_front(S, ptbytes_owner, 2) = true
  -- if $lookup(S.ENV,$ptascii("value")) = eps
  -- if $enumr_output(S.EVENTS) = $ptascii("T|")
  -- if $class_named(S.CLASSNAMES,$ptlc(ptbytes_owner)) = (porigin)
def $enumr_front(S, ptbytes_owner, n_phase) = false -- otherwise
dec $enumr_seek(pstate, ptbytes, nat, nat) : pstate
def $enumr_seek(S, ptbytes_owner, n_phase, 0) = S
def $enumr_seek(S, ptbytes_owner, n_phase, n) = S
  -- if $(n > 0)
  -- if $enumr_front(S,ptbytes_owner,n_phase) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET /\ ~$throwable_pending(S.COMPLETION))
def $enumr_seek(S, ptbytes_owner, n_phase, n) = $enumr_seek($drive_steps($enumr_running(S),1),ptbytes_owner,n_phase,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$enumr_front(S,ptbytes_owner,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET \/ $throwable_pending(S.COMPLETION)
'''


def reach(label, prior, owner, phase):
    return [
        label + '_found = $enumr_seek(' + prior + ',' + term(owner) + ',' + str(phase) + ',2000)',
        label + r'_found.COMPLETION = NORMAL \/ ' + label + '_found.COMPLETION = BUDGET',
        label + ' = $enumr_running(' + label + '_found)',
        '$enumr_front(' + label + ',' + term(owner) + ',' + str(phase) + ')',
        '$call_descriptors_valid(' + label + ')',
    ]


def assertions(case_id, main_fixture, source_path, expected_bytes):
    if case_id not in ('identity-alias', 'deferred-backing-priority'):
        raise ValueError(case_id)
    identity = case_id == 'identity-alias'
    owner = b'ReviewUnit' if identity else b'ReviewDeferred'
    first = b'First' if identity else b'Good'
    checks = [
        'S_initial = $php_run(' + main_fixture + ',0,' + json.dumps(base64.b64encode(str(source_path).encode()).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        *reach('S_init', 'S_initial', owner, 0),
        'S_init.TODO = (ENUM_CASE_INIT porigin_case) :: (CLASS_CONST_BIND porigin_case) :: ptask_tail*',
        '$enum_case_descriptor(S_init,porigin_case) = (pclassconstantdesc_case)',
        'pclassconstantdesc_case.NAME = ' + term(first),
        'porigin_owner = pclassconstantdesc_case.OWNER',
        'porigin_owner =/= porigin_case',
        '$class_named(S_init.CLASSNAMES,$ptlc(' + term(owner) + ')) = (porigin_owner)',
        '$default_cache_at(S_init.CLASSCONSTANTCACHE,porigin_case) = eps',
        '$enum_case_init_valid(S_init,porigin_case)',
        '$call_task_valid(S_init,ENUM_CASE_INIT porigin_case)',
        '~$enum_case_init_valid(S_init,porigin_owner)',
        '~$enum_case_init_valid(S_init[.CLASSCONSTANTINIT = eps],porigin_case)',
        '~$enum_case_init_valid(S_init[.CONSTCONTEXT = eps],porigin_case)',
        '~$enum_case_init_valid(S_init[.TODO = (ENUM_CASE_INIT porigin_case) :: ptask_tail*],porigin_case)',
        'S_zero = $drive_steps(S_init,0)',
        'S_zero = S_init[.COMPLETION = BUDGET]',
        '$enumr_running(S_zero) = S_init',
        'PhpStep: S_init ~> S_raw_object',
        'S_raw_object.COMPLETION = NORMAL',
        'S_one = $drive_steps(S_init,1)',
        'S_one.COMPLETION = BUDGET',
        'S_object = $enumr_running(S_one)',
        'S_object.TODO = S_raw_object.TODO',
        'S_object.RESULT = S_raw_object.RESULT',
        'S_object.OBJECTS = S_raw_object.OBJECTS',
        'S_object.OBJECTPROPS = S_raw_object.OBJECTPROPS',
        'S_object.CLASSCONSTANTCACHE = S_raw_object.CLASSCONSTANTCACHE',
        'S_object.CLASSCONSTANTINIT = S_raw_object.CLASSCONSTANTINIT',
        'S_object.CONSTCONTEXT = S_raw_object.CONSTCONTEXT',
        'S_object.ORIGIN = S_raw_object.ORIGIN',
        'S_object.EVENTS = S_init.EVENTS',
        'S_object.COMPLETION = NORMAL',
        'S_object.RESULT = KNOWN (POBJECT n_case)',
        'n_case = |S_init.OBJECTS|',
        'S_object.OBJECTS[n_case] = ENUMCASE porigin_case',
        '$object_class_origin(S_object,n_case) = (porigin_owner)',
        '$objectprops_at(S_object.OBJECTPROPS,n_case) = (ppropertyslot*)',
        '$enum_case_slots_valid(S_object,n_case,pclassconstantdesc_case,ppropertyslot*)',
        'ppropertyslot_name = ppropertyslot*[0]',
        'ppropertyslot_wrong = ppropertyslot_name[.DECL = (ENUM_PROPERTY porigin_case $ptascii("name"))]',
        '~$enum_case_slots_valid(S_object,n_case,pclassconstantdesc_case,[ppropertyslot_wrong] ++ ppropertyslot*[1:$nabs($(|ppropertyslot*| - 1))])',
        '$location_slot(S_object,PROPERTY n_case $ptascii("name")) = DEFINED pvalue_name',
        '$string_bytes(pvalue_name) = (' + term(first) + ')',
        '$closure_live_object_valid(S_object,n_case)',
        '$constant_value_class_valid(S_object,POBJECT n_case,PVENUMCASE n_case porigin_case)',
        '~$constant_value_class_valid(S_object,POBJECT n_case,PVENUMCASE n_case porigin_owner)',
        '~$constant_value_class_valid(S_object,POBJECT n_case,PVENUMCASE $(n_case + 1) porigin_case)',
        '$enum_case_object(S_object[.OBJECTS[n_case] = ENUMCASE porigin_owner],n_case) = eps',
        'S_object.TODO = (CLASS_CONST_BIND porigin_case) :: ptask_tail*',
        '$call_task_valid(S_object,CLASS_CONST_BIND porigin_case)',
        'PhpStep: S_object ~> S_cached',
        'S_cached.COMPLETION = NORMAL',
        '$default_cache_at(S_cached.CLASSCONSTANTCACHE,porigin_case) = (pdefaultcache_case)',
        'pdefaultcache_case.VALUE = POBJECT n_case',
        'pdefaultcache_case.CLASS = PVENUMCASE n_case porigin_case',
        '(HOBJECT n_case) <- $class_constant_roots(S_cached.CLASSCONSTANTCACHE)',
        '(HOBJECT n_case) <- $machine_roots(S_cached)',
        '$class_constant_state_valid(S_cached)',
        '$call_descriptors_valid(S_cached)',
    ]
    if identity:
        checks += [
            *reach('S_retained', 'S_cached', owner, 2),
            '$default_cache_at(S_retained.CLASSCONSTANTCACHE,porigin_case) = (pdefaultcache_case)',
            '$lookup(S_retained.ENV,$ptascii("value")) = eps',
            '$lookup(S_retained.ENV,$ptascii("weak")) = (n_weak_cell)',
            'S_retained.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)',
            '$weakref_get(S_retained,n_weak) = POBJECT n_case',
            '(HOBJECT n_case) <- $class_constant_roots(S_retained.CLASSCONSTANTCACHE)',
            '(HOBJECT n_case) <- S_retained.ALLOCATIONS',
            '$closure_live_object_valid(S_retained,n_case)',
            'S_finish = $drive_steps(S_retained,5000)',
        ]
    else:
        checks += [
            '$enumr_output(S_init.EVENTS) = ' + term(b'D|N:Cannot instantiate enum ReviewDeferred|'),
            *reach('S_table', 'S_cached', owner, 1),
            'S_table.TODO = (CLASS_CONST_TABLE_UPDATE porigin_owner z_first) :: ptask_table*',
            '$class_constant_table_task(S_table,porigin_owner,z_first,S_table.TODO)',
            '~$class_constant_table_done(S_table,porigin_owner)',
            '$class_constant_lookup(S_table,porigin_owner,$ptascii("Bad"),|S_table.CLASSES|) = (pclassconstantdesc_bad)',
            '$default_cache_at(S_table.CLASSCONSTANTCACHE,pclassconstantdesc_bad.ORIGIN) = (pdefaultcache_bad)',
            'pdefaultcache_bad.VALUE = POBJECT n_bad',
            'n_bad =/= n_case',
            '$location_slot(S_table,PROPERTY n_bad $ptascii("value")) = DEFINED pvalue_bad',
            '$string_bytes(pvalue_bad) = ($ptascii("bad"))',
            '$enum_backing_issue(S_table,porigin_owner) = METHOD_FILEISSUE ptbytes_type z_bad porigin_bad',
            'porigin_bad = pclassconstantdesc_bad.ORIGIN',
            'ptbytes_type = $ptascii("Enum case type string does not match enum backing type int")',
            'PhpStep: S_table ~> S_error',
            'S_error.COMPLETION = THROWN "TypeError" ptbytes_type z_first',
            'S_error.CLASSCONSTANTCACHE = S_table.CLASSCONSTANTCACHE',
            'S_error.CLASSCONSTANTHISTORY = S_table.CLASSCONSTANTHISTORY',
            '~$class_constant_table_done(S_error,porigin_owner)',
            'S_resume = $drive_steps(S_error,1)',
            *reach('S_retry', 'S_resume', owner, 1),
            'S_retry.TODO = (CLASS_CONST_TABLE_UPDATE porigin_owner z_retry) :: ptask_retry*',
            'z_retry =/= z_first',
            'S_retry.CLASSCONSTANTCACHE = S_table.CLASSCONSTANTCACHE',
            'S_retry.CLASSCONSTANTHISTORY = S_table.CLASSCONSTANTHISTORY',
            '$default_cache_at(S_retry.CLASSCONSTANTCACHE,porigin_case) = (pdefaultcache_case)',
            '$default_cache_at(S_retry.CLASSCONSTANTCACHE,porigin_bad) = (pdefaultcache_bad)',
            '(HOBJECT n_case) <- $class_constant_roots(S_retry.CLASSCONSTANTCACHE)',
            '(HOBJECT n_bad) <- $class_constant_roots(S_retry.CLASSCONSTANTCACHE)',
            '~$class_constant_table_done(S_retry,porigin_owner)',
            'S_retry_zero = $drive_steps(S_retry,0)',
            'S_retry_zero = S_retry[.COMPLETION = BUDGET]',
            'S_finish = $drive_steps($enumr_running(S_retry_zero),5000)',
        ]
    return checks + [
        'S_finish.COMPLETION = NORMAL',
        'S_finish.EXITSTATUS = 0',
        'S_finish.TODO = eps',
        '$enumr_output(S_finish.EVENTS) = ' + term(expected_bytes),
        '$default_cache_at(S_finish.CLASSCONSTANTCACHE,porigin_case) = (pdefaultcache_case)',
        '$class_constant_state_valid(S_finish)',
        '$call_descriptors_valid(S_finish)',
    ]


def duplicate_assertions(main_fixture, source_path, expected_bytes):
    """Reject a second rooted live object for the same cached source case."""
    checks = assertions('identity-alias', main_fixture, source_path, expected_bytes)
    end = checks.index('$call_descriptors_valid(S_cached)') + 1
    return checks[:end] + [
        'n_duplicate = |S_cached.OBJECTS|',
        '~((HOBJECT n_duplicate) <- S_cached.ALLOCATIONS)',
        'S_duplicate = S_cached[.OBJECTS = S_cached.OBJECTS ++ [ENUMCASE porigin_case]][.OBJECTPROPS = S_cached.OBJECTPROPS ++ [{OBJECT n_duplicate, SLOTS ppropertyslot*, MATERIALIZED false}]][.ALLOCATIONS = S_cached.ALLOCATIONS ++ [HOBJECT n_duplicate]][.RESULT = KNOWN (POBJECT n_duplicate)]',
        'S_duplicate.CLASSCONSTANTCACHE = S_cached.CLASSCONSTANTCACHE',
        '$default_cache_at(S_duplicate.CLASSCONSTANTCACHE,porigin_case) = (pdefaultcache_case)',
        '(HOBJECT n_case) <- $class_constant_roots(S_duplicate.CLASSCONSTANTCACHE)',
        '(HOBJECT n_duplicate) <- $machine_roots(S_duplicate)',
        'S_duplicate.OBJECTS[n_duplicate] = ENUMCASE porigin_case',
        '$objectprops_at(S_duplicate.OBJECTPROPS,n_duplicate) = (ppropertyslot*)',
        '$enum_case_slots_valid(S_duplicate,n_duplicate,pclassconstantdesc_case,ppropertyslot*)',
        '$enum_case_object(S_duplicate,n_case) = eps',
        '$enum_case_object(S_duplicate,n_duplicate) = eps',
        '~$closure_live_object_valid(S_duplicate,n_case)',
        '~$closure_live_object_valid(S_duplicate,n_duplicate)',
        '~$constant_value_class_valid(S_duplicate,POBJECT n_case,PVENUMCASE n_case porigin_case)',
        '~$call_descriptors_valid(S_duplicate)',
        'S_stale = S_duplicate[.ALLOCATIONS = S_cached.ALLOCATIONS][.OBJECTPROPS = S_cached.OBJECTPROPS][.RESULT = S_cached.RESULT]',
        '$enum_case_object(S_stale,n_case) = (pclassconstantdesc_case)',
    ]
