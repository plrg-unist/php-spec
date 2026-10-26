#!/usr/bin/env python3
"""Selected string identity, live primitive offsets, and fixed bounds completion."""
import base64
import json

import string_offset_read_warning_cases as cases
import list_missing_warning_protocol as shared
from array_literal_float_array_cv_state_review import driven, seek
from array_literal_float_wrapped_mixed_cv_state_review import empty_biases

HELPERS = shared.HELPERS + r'''
def $list_warning_task(STRING_READ_RESULT pstringread) = true
def $list_warning_frontier(S, 10) = ($string_read_plan(S) =/= eps)
def $list_warning_frontier(S, 11) = true
  -- if S.TODO = (STRING_READ_RESULT pstringread) :: ptask_tail*
  -- if pstringread.PHASE = STRING_CAST
def $list_warning_frontier(S, 12) = true
  -- if S.TODO = (STRING_READ_RESULT pstringread) :: ptask_tail*
  -- if pstringread.PHASE = STRING_BOUNDS i
def $list_warning_frontier(S, 13) = true
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = STRING_READ_RESULT pstringread
def $list_warning_frontier(S, 15) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask_tail*
  -- if $base64(text) = $ptascii("R:")
'''


def dispatch(start, desc, result):
    return [
        f'PhpStep: {start} ~> {result}',
        f'{result}.TODO = (ERROR_HANDLER_INVOKE perrorcall_{result}) :: ptask_{result}*',
        f'perrorcall_{result}.RESUME = STRING_READ_RESULT {desc}',
        f'perrorcall_{result}.LEVEL = 2', f'perrorcall_{result}.LINE = {desc}.READ.LINE',
        f'perrorcall_{result}.MESSAGE = $string_read_message({desc})',
        f'perrorcall_{result}.EVENT = DIAGNOSTIC "Warning" perrorcall_{result}.MESSAGE {desc}.READ.LINE',
        f'$error_call_valid({result}, perrorcall_{result})',
        f'~$error_call_valid({result}, perrorcall_{result}[.LEVEL = 8192])',
        f'~$error_call_valid({result}, perrorcall_{result}[.LINE = $({desc}.READ.LINE + 1)])',
        f'~$error_call_valid({result}, perrorcall_{result}[.MESSAGE = eps])',
        f'~$error_call_valid({result}, perrorcall_{result}[.SITE = PORIGIN (|{start}.SOURCES|) eps])',
        f'~$error_call_valid({result}, perrorcall_{result}[.EVENT = DIAGNOSTIC "Notice" perrorcall_{result}.MESSAGE {desc}.READ.LINE])',
        f'$task_nodes(STRING_READ_RESULT {desc}) = eps',
        f'$task_nodes(ERROR_HANDLER_INVOKE perrorcall_{result}) = eps',
        f'{result}.STORE = {start}.STORE', f'{result}.ARRAYS = {start}.ARRAYS',
        f'{result}.ALLOCATIONS = {start}.ALLOCATIONS', f'{result}.STRINGDATA = {start}.STRINGDATA',
        f'$heap_valid($heap_graph({result}))', f'$call_descriptors_valid({result})',
    ] + empty_biases(result)


def source_checks(state, desc):
    return [
        f'$string_read_source({state}, {desc})', f'$string_read_ready({state}, {desc})',
        f'$string_read_provider_ready({state}, {desc})',
        f'{desc}.READ.PHASE = KEY_NULL', f'{desc}.READ.KEY = KSTRING eps', f'{desc}.READ.NAME = eps',
        f'~{desc}.READ.GLOBAL', f'{desc}.READ.MODE = KEY_R',
        f'~$string_read_source({state}[.ORIGIN = eps], {desc})',
        f'~$string_read_source({state}[.SOURCES = eps], {desc})',
        f'~$string_read_source({state}[.CODE = eps], {desc})',
        f'~$string_read_source({state}, {desc}[.READ.LINE = $({desc}.READ.LINE + 1)])',
        f'~$string_read_source({state}, {desc}[.READ.GLOBAL = true])',
        f'~$string_read_source({state}, {desc}[.READ.MODE = KEY_IS])',
        f'~$string_read_source({state}, {desc}[.READ.KEY = KINT 0])',
        f'~$string_read_source({state}, {desc}[.KEYCELL = eps])',
        f'~$string_read_source({state}, {desc}[.KEYCELL = (|{state}.STORE|)])',
        f'$heap_valid($heap_graph({state}))', f'$call_descriptors_valid({state})',
    ]


def finish(start, stdout):
    return seek(start, 15, 'S_read') + [
        '$heap_valid($heap_graph(S_read))', '$call_descriptors_valid(S_read)',
        '$drive_steps(S_read, 0) = S_read[.COMPLETION = BUDGET]',
        'S_split = $drive_steps(S_read, 1)', 'S_split.COMPLETION = BUDGET',
        'S_done = $drive_steps(S_split[.COMPLETION = NORMAL], 3000)',
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '$heap_valid($heap_graph(S_done))', '$call_descriptors_valid(S_done)',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        'S_done.POOLS = S_read.POOLS',
    ] + empty_biases('S_done')


def conditions(name, program, path, stdout):
    runtime = name.endswith('runtime-carriers')
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ] + seek('S_initial', 10, 'S') + [
        '$string_read_plan(S) = (pstringread)', 'pstringread.PHASE = STRING_CAST',
        f'pstringread.READ.LINE = {11 if runtime else 9}',
        'pstringread.READ.VALUE = PFLOAT 4609434218613702656',
        '$lookup(S.ENV, $ptascii("s")) = (n_s)',
        '$lookup(S.ENV, $ptascii("key")) = (n_key)', 'n_key =/= n_s',
        'pstringread.BASECELL = (n_s)', 'pstringread.KEYCELL = (n_key)',
        'S.STORE[n_s] = DEFINED pstringread.READ.BASE',
        'pstringread.READ.BASE = PSTRING_CARRIER pstringidentity ($ptascii("abcd"))',
        '$string_carrier_valid(S, pstringread.READ.BASE)',
        '$heap_owners($heap_graph(S), HCELL n_s) = 1',
        '$heap_owners($heap_graph(S), HCELL n_key) = 1',
        '$string_read_plan(S[.STORE[n_key] = DEFINED (PINT 2)]) = eps',
        '$string_read_plan(S[.REFCELLS = n_key :: S.REFCELLS]) = eps',
        '$string_read_plan(S[.REFCELLS = n_s :: S.REFCELLS]) = eps',
        '$string_read_plan(S[.RESULT = KNOWN PNULL]) = eps',
        '$string_read_plan(S[.ORIGIN = eps]) = eps',
        '$string_read_offset(PNULL) = (0)', '$string_read_offset(PBOOL true) = (1)',
        '$string_read_offset(PBOOL false) = (0)',
    ] + source_checks('S', 'pstringread')
    if runtime:
        checks += ['pstringidentity = REQUEST_STRING n_identity', 'S.STRINGDATA[n_identity] = $ptascii("abcd")']
    else:
        checks += ['pstringidentity = INTERNED_STRING']
    checks += dispatch('S', 'pstringread', 'S_dispatch') + driven('S', 'S_dispatch', 'S_driven')
    checks += seek('S_driven', 13, 'S_entered') + [
        'S_entered.ERRORHANDLER.CALLBACK = eps',
        'S_entered.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_entered*',
        'perrorcall_entered.RESUME = STRING_READ_RESULT pstringread',
        '$task_nodes(perrorcall_entered.RESUME) = eps',
        '$heap_owners($heap_graph(S_entered), HCELL n_s) = 1',
        '$heap_owners($heap_graph(S_entered), HCELL n_key) = 1',
    ] + seek('S_entered', 11, 'S_resume') + source_checks('S_resume', 'pstringread') + [
        'S_resume.TODO = (STRING_READ_RESULT pstringread) :: ptask_after*',
        '$task_nodes(STRING_READ_RESULT pstringread) = eps',
        'S_bad_key = S_resume[.REFCELLS = n_key :: S_resume.REFCELLS]',
        '$heap_valid($heap_graph(S_bad_key))', '$call_descriptors_valid(S_bad_key)',
        '$string_read_source(S_bad_key, pstringread)',
        '~$string_read_ready(S_bad_key, pstringread)',
        '$string_read_key_current(S_bad_key, pstringread) = eps',
        '$string_read_resume(S_bad_key, pstringread).COMPLETION = UNSUPPORTED "string offset changed key locator after callback"',
        '$error_read_discard(S_bad_key, STRING_READ_RESULT pstringread).COMPLETION = UNSUPPORTED "string offset changed key locator after callback"',
        'PhpStep: S_resume ~> S_value',
        'S_value.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("d")))' if runtime else
        'S_value.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("c")))',
        'S_value.STORE = S_resume.STORE', 'S_value.ARRAYS = S_resume.ARRAYS',
        'S_value.STRINGDATA = S_resume.STRINGDATA', 'S_value.BASE = BASE_VALUE (KNOWN PNULL)',
    ]
    if not runtime:
        checks += [
            'S_resume.STORE[n_s] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("XY")))',
            'S_resume.STORE[n_key] = DEFINED (PINT 2)', '$string_read_key_current(S_resume, pstringread) = (PINT 2)',
            '$string_read_provider_ready(S_resume[.ENV = eps], pstringread)',
        ] + finish('S_value', stdout) + [
            '$lookup(S_read.ENV, $ptascii("s")) = (n_s)',
            'S_read.STORE[n_s] = DEFINED (PSTRING ($ptascii("ZY")))',
            '$lookup(S_read.ENV, $ptascii("copy")) = (n_copy)',
            'S_read.STORE[n_copy] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("XY")))',
            '~((HCELL n_s) <- S_done.ALLOCATIONS)', '~((HCELL n_key) <- S_done.ALLOCATIONS)',
            '~((HCELL n_copy) <- S_done.ALLOCATIONS)',
        ]
        return checks
    checks += [
        'S_resume.STORE[n_s] = S.STORE[n_s]',
        '$string_read_key_current(S_resume, pstringread) = (PFLOAT 13833706975393952563)',
        '$string_read_offset(PFLOAT 13833706975393952563) = ($(-1))',
        '~$string_read_provider_ready(S_resume[.ENV = eps], pstringread)',
    ] + driven('S_resume', 'S_value', 'S_value_driven') + seek('S_value_driven', 10, 'S_tmp') + [
        '$string_read_plan(S_tmp) = (pstringread_tmp)',
        'pstringread_tmp.PHASE = STRING_CAST', 'pstringread_tmp.READ.LINE = 13',
        'pstringread_tmp.BASECELL = eps', 'pstringread_tmp.KEYCELL = (n_key)',
        'pstringread_tmp.READ.OWNERS = BASE_VALUE (KNOWN pstringread_tmp.READ.BASE)',
        'pstringread_tmp.READ.BASE = PSTRING_CARRIER (REQUEST_STRING n_tmp_identity) ($ptascii("ABCD"))',
        'n_tmp_identity =/= n_identity',
        '$string_read_provider_ready(S_tmp[.ENV = eps], pstringread_tmp)',
    ] + source_checks('S_tmp', 'pstringread_tmp') + dispatch('S_tmp', 'pstringread_tmp', 'S_tmp_dispatch')
    checks += driven('S_tmp', 'S_tmp_dispatch', 'S_tmp_driven') + seek('S_tmp_driven', 11, 'S_tmp_resume') + [
        '$string_read_source(S_tmp_resume, pstringread_tmp)', '$string_read_ready(S_tmp_resume, pstringread_tmp)',
        'S_tmp_resume.STORE[n_key] = DEFINED (PINT 9)',
        '$string_read_key_current(S_tmp_resume, pstringread_tmp) = (PINT 9)',
        '$lookup(S_tmp_resume.ENV, $ptascii("head")) = (n_head)',
        'S_tmp_resume.STORE[n_head] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("XY")))',
        'PhpStep: S_tmp_resume ~> S_bounds_dispatch',
        'S_bounds_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall_bounds) :: ptask_bounds*',
        'perrorcall_bounds.RESUME = STRING_READ_RESULT pstringread_bounds',
        'pstringread_bounds = pstringread_tmp[.PHASE = STRING_BOUNDS 9]',
        'perrorcall_bounds.MESSAGE = $ptascii("Uninitialized string offset 9")',
        'perrorcall_bounds.LINE = 13', '$error_call_valid(S_bounds_dispatch, perrorcall_bounds)',
        '$task_nodes(perrorcall_bounds.RESUME) = eps',
        'S_bounds_dispatch.STRINGDATA = S_tmp_resume.STRINGDATA',
    ] + driven('S_tmp_resume', 'S_bounds_dispatch', 'S_bounds_driven') + seek('S_bounds_driven', 12, 'S_bounds_resume') + [
        '$string_read_source(S_bounds_resume, pstringread_bounds)', '$string_read_ready(S_bounds_resume, pstringread_bounds)',
        'S_bounds_resume.STORE[n_key] = DEFINED (PINT 0)',
        'S_bounds_resume.STORE[n_head] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("z")))',
        '$string_read_ready(S_bounds_resume[.ENV = eps], pstringread_bounds)',
        '$error_read_discard(S_bounds_resume, STRING_READ_RESULT pstringread_bounds) = S_bounds_resume',
        'PhpStep: S_bounds_resume ~> S_empty',
        'S_empty.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING eps)',
        'S_empty.STORE = S_bounds_resume.STORE', 'S_empty.STRINGDATA = S_bounds_resume.STRINGDATA',
    ] + finish('S_empty', stdout) + [
        'S_read.STORE[n_s] = DEFINED (PSTRING_CARRIER (REQUEST_STRING n_identity) ($ptascii("abcd")))',
        '~((HCELL n_s) <- S_done.ALLOCATIONS)', '~((HCELL n_key) <- S_done.ALLOCATIONS)',
        '~((HCELL n_head) <- S_done.ALLOCATIONS)',
    ]
    return checks


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(cases, conditions, HELPERS) else 1)
