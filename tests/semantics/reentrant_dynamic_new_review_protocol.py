#!/usr/bin/env python3
"""Independent assertions for the frozen interface/alias Source118 witness."""
import base64
import json


def term(data):
    return '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'


PREFIX = r'''
dec $s118r_running(pstate) : pstate
def $s118r_running(S) = S[.COMPLETION = NORMAL] -- if S.COMPLETION = BUDGET
def $s118r_running(S) = S -- otherwise
dec $s118r_front(pstate, nat) : bool
def $s118r_front(S, 1) = true
  -- if S.TODO = (AUTO_NEXT pautoloadcall) :: ptask_tail*
  -- if pautoloadcall.NAME = $ptascii("D118R")
def $s118r_front(S, 2) = true
  -- if S.TODO = (DYNAMIC_NEW_FINISH pdynamicnew) :: ptask_tail*
  -- if pdynamicnew.CLASS = $ptascii("D118R")
def $s118r_front(S, n) = false -- otherwise
dec $s118r_seek(pstate, nat, nat) : pstate
def $s118r_seek(S, 0, n_front) = S
def $s118r_seek(S, n, n_front) = S
  -- if $(n > 0)
  -- if $s118r_front(S, n_front) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $s118r_seek(S, n, n_front) = $s118r_seek($drive_steps($s118r_running(S), 1), $nabs($(n - 1)), n_front)
  -- if $(n > 0)
  -- if ~$s118r_front(S, n_front)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
dec $s118r_output_item(pevent) : ptbytes
def $s118r_output_item(OUTPUT ptbytes) = ptbytes
def $s118r_output_item(pevent) = eps -- otherwise
dec $s118r_output(pevent*) : ptbytes
def $s118r_output(eps) = eps
def $s118r_output(pevent :: pevent_tail*) = $s118r_output_item(pevent) ++ $s118r_output(pevent_tail*)
'''


def assertions(main_fixture, source_path, outer_response, interface_response,
               d_response, expected_bytes, temporary=False):
    source_identity = json.dumps(base64.b64encode(str(source_path).encode()).decode())
    selected_identity = '(REQUEST_STRING n_selected)' if temporary else 'INTERNED_STRING'
    prefix_bytes = 'D' if temporary else 'D118R'
    return [
        'S_wait0 = $php_run(' + main_fixture + ',5000,' + source_identity + ')',
        'S_wait0.COMPLETION = SOURCE_PENDING',
        'S_wait0.EVALCONTEXTS = pevalcontext_outer :: eps',
        'pevalcontext_outer.UNIT = 1',
        '$eval_response_valid(S_wait0,' + outer_response + ')',
        'S_body0 = $eval_resume(S_wait0,' + outer_response + ')',
        'S_lookup0 = $s118r_seek(S_body0,5000,1)',
        r'S_lookup0.COMPLETION = NORMAL \/ S_lookup0.COMPLETION = BUDGET',
        'S_lookup = $s118r_running(S_lookup0)',
        '$s118r_front(S_lookup,1)',
        'S_lookup.TODO = (AUTO_NEXT pautoloadcall_D) :: (DYNAMIC_NEW_FINISH pdynamicnew_D) :: ptask_lookup*',
        'pautoloadcall_D.MODE = AUTO_LOOKUP',
        'pautoloadcall_D.NAME = $ptascii("D118R")',
        'pautoloadcall_D.KEY = $ptascii("d118r")',
        'pautoloadcall_D.RESUME = AUTO_NEW $ptascii("D118R") eps z_D z_fetchD',
        'pautoloadcall_D.SITE = pdynamicnew_D.SITE',
        'pdynamicnew_D.SOURCE = pvalue_D',
        'pvalue_D = PSTRING_CARRIER ' + selected_identity + ' $ptascii("D118R")',
        '$string_carrier_valid(S_lookup,pvalue_D)',
        '$value_nodes(pvalue_D) = eps',
        '$task_nodes(DYNAMIC_NEW_FINISH pdynamicnew_D) = eps',
        'pdynamicnew_D.CLASS = $ptascii("D118R")',
        'pdynamicnew_D.LINE = z_D',
        'pdynamicnew_D.FETCHLINE = z_fetchD',
        'z_D = 13',
        'z_fetchD = 13',
        '$dynamic_new_valid(S_lookup,pdynamicnew_D)',
        '$autoload_call_valid(S_lookup,pautoloadcall_D)',
        '$call_task_valid(S_lookup,DYNAMIC_NEW_FINISH pdynamicnew_D)',
        '$lookup(S_lookup.ENV,$ptascii("selector118r")) = (n_alias)',
        '$lookup(S_lookup.ENV,$ptascii("name118r")) = (n_alias)',
        'S_lookup.STORE[n_alias] = DEFINED pvalue_prefix',
        '$string_bytes(pvalue_prefix) = ($ptascii("' + prefix_bytes + '"))',
        '$string_carrier_valid(S_lookup,pvalue_prefix)',
        'n_alias <- S_lookup.REFCELLS',
        '(HCELL n_alias) <- S_lookup.ALLOCATIONS',
        'S_absent = S_lookup[.TODO = (AUTO_NEXT pautoloadcall_D) :: ptask_lookup*]',
        '~$autoload_call_valid(S_absent,pautoloadcall_D)',
        'pdynamicnew_wrong = pdynamicnew_D[.CLASS = $ptascii("Missing118R")]',
        '~$dynamic_new_valid(S_lookup,pdynamicnew_wrong)',
        'S_wrong = S_lookup[.TODO = (AUTO_NEXT pautoloadcall_D) :: (DYNAMIC_NEW_FINISH pdynamicnew_wrong) :: ptask_lookup*]',
        '~$autoload_call_valid(S_wrong,pautoloadcall_D)',
        'pdynamicnew_line = pdynamicnew_D[.FETCHLINE = $(z_fetchD + 1)]',
        '~$dynamic_new_valid(S_lookup,pdynamicnew_line)',
        'S_line = S_lookup[.TODO = (AUTO_NEXT pautoloadcall_D) :: (DYNAMIC_NEW_FINISH pdynamicnew_line) :: ptask_lookup*]',
        '~$autoload_call_valid(S_line,pautoloadcall_D)',
        'pdynamicnew_source = pdynamicnew_D[.SOURCE = PSTRING $ptascii("Missing118R")]',
        '~$dynamic_new_valid(S_lookup,pdynamicnew_source)',
        '$call_descriptors_valid(S_lookup)',
        'S_budget0 = $drive_steps(S_lookup,0)',
        'S_budget0 = S_lookup[.COMPLETION = BUDGET]',
        'S_resume = $s118r_running(S_budget0)',
        'S_resume = S_lookup',
        'PhpStep: S_resume ~> S_selected',
        'S_selected.COMPLETION = NORMAL',
        'S_selected.TODO = (AUTO_ENTER pautoloadcall_selected pautoloadentry_D poperand_D) :: (DYNAMIC_NEW_FINISH pdynamicnew_D) :: ptask_lookup*',
        'pautoloadcall_selected.SITE = pautoloadcall_D.SITE',
        'pautoloadcall_selected.RESUME = pautoloadcall_D.RESUME',
        '$autoload_selected_valid(S_selected,pautoloadcall_selected,pautoloadentry_D)',
        'S_budget1 = $drive_steps(S_resume,1)',
        'S_budget1 = S_selected[.COMPLETION = BUDGET]',
        'S_waitD = $drive_steps($s118r_running(S_budget1),5000)',
        'S_waitD.COMPLETION = SOURCE_PENDING',
        'S_waitD.EVALCONTEXTS = pevalcontext_D :: pevalcontext_outer2 :: eps',
        'pevalcontext_D.UNIT = 2',
        'pevalcontext_outer2.UNIT = 1',
        '$eval_response_valid(S_waitD,' + d_response + ')',
        'S_waitD.FRAMES = pframe_D :: pframe_I :: eps',
        'pframe_D.TODO = (AUTO_RESULT pautoloadcall_entered pautoloadentry_entered poperand_entered) :: (DYNAMIC_NEW_FINISH pdynamicnew_D) :: ptask_entered*',
        'S_saved = $constant_frame_scope(S_waitD,pframe_D,[pframe_I])',
        '$autoload_selected_valid(S_saved,pautoloadcall_entered,pautoloadentry_entered)',
        '$dynamic_new_valid(S_saved,pdynamicnew_D)',
        '$dynamic_new_find(S_saved,S_saved.TODO,pdynamicnew_D.SITE) = (pdynamicnew_D)',
        '$new_source_name(S_saved,pdynamicnew_D.SITE) = ($ptascii("D118R"))',
        '$lookup(S_saved.ENV,$ptascii("selector118r")) = (n_alias)',
        '$lookup(S_saved.ENV,$ptascii("name118r")) = (n_alias)',
        'S_saved.STORE[n_alias] = DEFINED pvalue_changed',
        '$string_bytes(pvalue_changed) = ($ptascii("Missing118R"))',
        '$string_carrier_valid(S_saved,pvalue_changed)',
        'S_saved_wrong = S_saved[.TODO = (AUTO_RESULT pautoloadcall_entered pautoloadentry_entered poperand_entered) :: (DYNAMIC_NEW_FINISH pdynamicnew_wrong) :: ptask_entered*]',
        '~$autoload_selected_valid(S_saved_wrong,pautoloadcall_entered,pautoloadentry_entered)',
        'S_bodyD = $eval_resume(S_waitD,' + d_response + ')',
        'S_return0 = $s118r_seek(S_bodyD,5000,2)',
        r'S_return0.COMPLETION = NORMAL \/ S_return0.COMPLETION = BUDGET',
        'S_return = $s118r_running(S_return0)',
        '$s118r_front(S_return,2)',
        'S_return.TODO = (DYNAMIC_NEW_FINISH pdynamicnew_D) :: ptask_return*',
        'S_return.RESULT = KNOWN (POBJECT n_D)',
        '$getclass_live_object(S_return,n_D)',
        '$object_name(S_return,n_D) = $ptascii("D118R")',
        '$lookup(S_return.ENV,$ptascii("selector118r")) = (n_alias)',
        'S_return.STORE[n_alias] = DEFINED pvalue_changed',
        '$dynamic_new_valid(S_return,pdynamicnew_D)',
        '$dynamic_new_finish_result(S_return,pdynamicnew_D)',
        '$call_task_valid(S_return,DYNAMIC_NEW_FINISH pdynamicnew_D)',
        '$call_descriptors_valid(S_return)',
        'S_bad_finish = S_return[.TODO = (DYNAMIC_NEW_FINISH pdynamicnew_wrong) :: ptask_return*]',
        '~$call_task_valid(S_bad_finish,DYNAMIC_NEW_FINISH pdynamicnew_wrong)',
        'S_budget_return = $drive_steps(S_return,0)',
        'S_budget_return = S_return[.COMPLETION = BUDGET]',
        'S_return_resume = $s118r_running(S_budget_return)',
        'S_return_resume = S_return',
        'PhpStep: S_return_resume ~> S_finished_D',
        'S_finished_D = S_return[.TODO = ptask_return*]',
        'S_waitI = $drive_steps(S_finished_D,5000)',
        'S_waitI.COMPLETION = SOURCE_PENDING',
        'S_waitI.EVALCONTEXTS = pevalcontext_I :: pevalcontext_outer3 :: eps',
        'pevalcontext_I.UNIT = 3',
        'pevalcontext_outer3.UNIT = 1',
        '$eval_response_valid(S_waitI,' + interface_response + ')',
        'S_finish = $drive_steps($eval_resume(S_waitI,' + interface_response + '),5000)',
        'S_finish.COMPLETION = NORMAL',
        'S_finish.EXITSTATUS = 0',
        'S_finish.TODO = eps',
        'S_finish.FRAMES = eps',
        '$s118r_output(S_finish.EVENTS) = ' + term(expected_bytes),
        '$call_descriptors_valid(S_finish)',
    ]
