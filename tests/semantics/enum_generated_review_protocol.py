#!/usr/bin/env python3
"""Independent reached warning and parsed Stringable enum-call protocols."""
import base64
import json
from enum_core_review_protocol import PREFIX as CASE_PREFIX, term


PREFIX = CASE_PREFIX + r'''
dec $enumg_front(pstate, nat) : bool
def $enumg_front(S, 0) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = ENUM_FROM_LOSSY pconfigcall pvalue i
def $enumg_front(S, 1) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = ENUM_FROM_NULL pconfigcall
def $enumg_front(S, 2) = true
  -- if S.TODO = (ENUM_FROM_STRING_RESULT pconfigcall n_object porigin_child z_child z_call) :: ptask_tail*
def $enumg_front(S, 3) = true
  -- if S.TODO = (CLASS_CONST_TABLE_UPDATE porigin z) :: (ENUM_FROM_FETCH pconfigcall pvalue) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_ENUM porigin ptbytes text_method
def $enumg_front(S, 4) = true
  -- if S.TODO = (ENUM_FROM_FETCH pconfigcall pvalue_key) :: ptask_tail*
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue)]
  -- if $string_bytes(pvalue) = ($ptascii("01"))
def $enumg_front(S, n_phase) = false -- otherwise
dec $enumg_seek(pstate, nat, nat) : pstate
def $enumg_seek(S, n_phase, 0) = S
def $enumg_seek(S, n_phase, n) = S
  -- if $(n > 0)
  -- if $enumg_front(S,n_phase) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET /\ ~$throwable_pending(S.COMPLETION))
def $enumg_seek(S, n_phase, n) = $enumg_seek($drive_steps($enumr_running(S),1),n_phase,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$enumg_front(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET \/ $throwable_pending(S.COMPLETION)
'''


def reach(label, previous, phase):
    return [label + '_found = $enumg_seek(' + previous + ',' + str(phase) + ',3000)',
            label + r'_found.COMPLETION = NORMAL \/ ' + label + '_found.COMPLETION = BUDGET',
            label + ' = $enumr_running(' + label + '_found)',
            '$enumg_front(' + label + ',' + str(phase) + ')',
            '$call_descriptors_valid(' + label + ')']


def assertions(case_id, main_fixture, source_path, expected_bytes):
    if case_id not in ('weak-parser-order', 'parsed-argument-trace'):
        raise ValueError(case_id)
    weak = case_id == 'weak-parser-order'
    checks = ['S_initial = $php_run(' + main_fixture + ',0,' +
              json.dumps(base64.b64encode(str(source_path).encode()).decode()) + ')',
              'S_initial.COMPLETION = BUDGET']
    if weak:
        checks += [*reach('S_lossy', 'S_initial', 0),
            'S_lossy.TODO = (ERROR_HANDLER_INVOKE perrorcall_lossy) :: ptask_lossy*',
            'perrorcall_lossy.RESUME = ENUM_FROM_LOSSY pconfigcall_lossy pvalue_lossy i_lossy',
            'pvalue_lossy = PFLOAT 4609434218613702656',
            'i_lossy = 1',
            'pconfigcall_lossy.SENT = [NAMED_SENT (KNOWN pvalue_lossy)]',
            '~$config_strict(S_lossy,pconfigcall_lossy)',
            '$enum_from_lossy_valid(S_lossy,pconfigcall_lossy,pvalue_lossy,i_lossy)',
            '$error_call_valid(S_lossy,perrorcall_lossy)',
            'perrorcall_lossy.LEVEL = 8192',
            '~$enum_from_lossy_valid(S_lossy,pconfigcall_lossy,pvalue_lossy,$(i_lossy + 1))',
            '~$error_call_valid(S_lossy,perrorcall_lossy[.LEVEL = 8])',
            '~$error_call_valid(S_lossy,perrorcall_lossy[.MESSAGE = $ptascii("wrong")])',
            'S_lossy_zero = $drive_steps(S_lossy,0)',
            'S_lossy_zero = S_lossy[.COMPLETION = BUDGET]',
            *reach('S_null', '$drive_steps($enumr_running(S_lossy_zero),1)', 1),
            'S_null.TODO = (ERROR_HANDLER_INVOKE perrorcall_null) :: ptask_null*',
            'perrorcall_null.RESUME = ENUM_FROM_NULL pconfigcall_null',
            'pconfigcall_null.SENT = [NAMED_SENT (KNOWN PNULL)]',
            '$enum_from_null_valid(S_null,pconfigcall_null)',
            '$error_call_valid(S_null,perrorcall_null)',
            'perrorcall_null.LEVEL = 8192',
            '~$error_call_valid(S_null,perrorcall_null[.LINE = $(perrorcall_null.LINE + 1)])',
            '~$error_call_valid(S_null,perrorcall_null[.EVENT = DIAGNOSTIC "Warning" perrorcall_null.MESSAGE perrorcall_null.LINE])']
        prior = '$drive_steps(S_null,1)'
    else:
        prior = 'S_initial'
    checks += [*reach('S_string', prior, 2),
        'S_string.TODO = (ENUM_FROM_STRING_RESULT pconfigcall_raw n_original porigin_child z_child z_call) :: ptask_string*',
        'pconfigcall_raw.SENT = [NAMED_SENT (KNOWN (POBJECT n_original))]',
        '$enum_string_site_valid(S_string,pconfigcall_raw,n_original,porigin_child,z_child,z_call)',
        '$call_task_valid(S_string,ENUM_FROM_STRING_RESULT pconfigcall_raw n_original porigin_child z_child z_call)',
        '(HOBJECT n_original) <- $machine_roots(S_string)',
        '(HOBJECT n_original) <- S_string.ALLOCATIONS',
        'S_string.RESULT = KNOWN pvalue_text',
        '$string_bytes(pvalue_text) = ($ptascii("01"))',
        '$value_nodes(pvalue_text) = eps',
        '~$enum_string_site_valid(S_string,pconfigcall_raw,$(n_original + 1),porigin_child,z_child,z_call)',
        '~$enum_string_site_valid(S_string,pconfigcall_raw,n_original,porigin_child,$(z_child + 1),z_call)',
        '~$enum_string_site_valid(S_string,pconfigcall_raw[.SENT = [NAMED_SENT (KNOWN pvalue_text)]],n_original,porigin_child,z_child,z_call)',
        'S_string_zero = $drive_steps(S_string,0)',
        'S_string_zero = S_string[.COMPLETION = BUDGET]',
        'S_string_after = $drive_steps($enumr_running(S_string_zero),1)']
    checks += reach('S_parsed', 'S_string_after', 4 if weak else 3)
    checks += ['S_parsed.TODO = ' + ('' if weak else '(CLASS_CONST_TABLE_UPDATE porigin_owner z_update) :: ') + '(ENUM_FROM_FETCH pconfigcall_parsed pvalue_key) :: ptask_parsed*',
        'pconfigcall_parsed = pconfigcall_raw[.SENT = [NAMED_SENT (KNOWN pvalue_text)]]',
        'pvalue_key = pvalue_text',
        '$enum_from_fetch_valid(S_parsed,pconfigcall_parsed,pvalue_key)',
        '~$enum_from_fetch_valid(S_parsed,pconfigcall_parsed,PSTRING $ptascii("wrong"))',
        '~((HOBJECT n_original) <- S_parsed.ALLOCATIONS)',
        '~((HOBJECT n_original) <- $machine_roots(S_parsed))']
    if not weak:
        checks += ['$lookup(S_parsed.ENV,$ptascii("weak")) = (n_weak_cell)',
            'S_parsed.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)',
            '$weakref_get(S_parsed,n_weak) = PNULL',
            '$class_constant_table_task(S_parsed,porigin_owner,z_update,S_parsed.TODO)',
            '~$class_constant_table_done(S_parsed,porigin_owner)',
            '$enum_backing_issue(S_parsed,porigin_owner) = METHOD_FILEISSUE ptbytes_type z_bad porigin_bad',
            'ptbytes_type = $ptascii("Enum case type int does not match enum backing type string")']
    return checks + ['S_finish = $drive_steps(S_parsed,5000)',
        'S_finish.COMPLETION = NORMAL', 'S_finish.EXITSTATUS = 0',
        'S_finish.TODO = eps', '$enumr_output(S_finish.EVENTS) = ' + term(expected_bytes),
        '$call_descriptors_valid(S_finish)']
