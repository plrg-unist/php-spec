#!/usr/bin/env python3
"""Independent reached assertions for the interface/helper Source119 original."""
import base64
import json


def term(data):
    return '$base64(' + json.dumps(base64.b64encode(data).decode()) + ')'


PREFIX = r'''
dec $s119r_running(pstate) : pstate
def $s119r_running(S) = S[.COMPLETION = NORMAL] -- if S.COMPLETION = BUDGET
def $s119r_running(S) = S -- otherwise
dec $s119r_front(pstate, bool) : bool
def $s119r_front(S, b_known) = true
  -- if S.TODO = (DYNAMIC_NEW_CLASS z z_fetch) :: ptask_tail*
  -- if S.ORIGIN = (porigin)
  -- if S_read = $resolve_at($s119r_running(S),S.RESULT,z_fetch)
  -- if S_read.COMPLETION = NORMAL
  -- if S_read.RESULT = KNOWN pvalue
  -- if $dynamic_new_value_name(S_read,porigin,pvalue) = (ptbytes)
  -- if $ptlc(ptbytes) = $ptascii("i119r")
  -- if $dynamic_new_known(S_read,ptbytes) = b_known
def $s119r_front(S, b_known) = false -- otherwise
dec $s119r_seek(pstate, bool, nat) : pstate
def $s119r_seek(S, b_known, 0) = S
def $s119r_seek(S, b_known, n) = S
  -- if $(n > 0)
  -- if $s119r_front(S,b_known) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $s119r_seek(S, b_known, n) = $s119r_seek($drive_steps($s119r_running(S),1),b_known,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$s119r_front(S,b_known)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
dec $s119r_marker(ptask*) : bool
def $s119r_marker(eps) = false
def $s119r_marker(ptask :: ptask_tail*) = ($dynamic_new_marker(ptask) \/ $s119r_marker(ptask_tail*))
dec $s119r_output_item(pevent) : ptbytes
def $s119r_output_item(OUTPUT ptbytes) = ptbytes
def $s119r_output_item(pevent) = eps -- otherwise
dec $s119r_output(pevent*) : ptbytes
def $s119r_output(eps) = eps
def $s119r_output(pevent :: pevent_tail*) = $s119r_output_item(pevent) ++ $s119r_output(pevent_tail*)
'''


def assertions(main_fixture, source_path, outer_response, dependency_response,
               expected_bytes):
    source_identity = json.dumps(base64.b64encode(str(source_path).encode()).decode())
    return [
        'S_wait0 = $php_run(' + main_fixture + ',5000,' + source_identity + ')',
        'S_wait0.COMPLETION = SOURCE_PENDING',
        'S_wait0.EVALCONTEXTS = pevalcontext_outer :: eps',
        'pevalcontext_outer.UNIT = 1',
        '$eval_response_valid(S_wait0,' + outer_response + ')',
        'S_body0 = $eval_resume(S_wait0,' + outer_response + ')',
        'S_found = $s119r_seek(S_body0,false,5000)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S_front = $s119r_running(S_found)',
        '$s119r_front(S_front,false)',
        'S_front.TODO = (DYNAMIC_NEW_CLASS z_new z_fetch) :: ptask_tail*',
        'S_front.ORIGIN = (porigin_new)',
        '$dynamic_new_site(S_front,porigin_new,z_new,z_fetch)',
        'z_new = 4',
        'z_fetch = 4',
        'S_read = $resolve_at(S_front,S_front.RESULT,z_fetch)',
        'S_read.COMPLETION = NORMAL',
        'S_read.RESULT = KNOWN pvalue_raw',
        '$string_bytes(pvalue_raw) = (' + term(b'\\i119r') + ')',
        '$string_carrier_valid(S_read,pvalue_raw)',
        '$value_nodes(pvalue_raw) = eps',
        '$lookup(S_front.ENV,$ptascii("selector")) = (n_alias)',
        'S_front.STORE[n_alias] = DEFINED pvalue_raw',
        'n_alias <- S_front.REFCELLS',
        '(HCELL n_alias) <- S_front.ALLOCATIONS',
        'S_front.FRAMES = pframe_helper :: pframe_link :: eps',
        'S_caller = $constant_frame_scope(S_front,pframe_helper,[pframe_link])',
        '$lookup(S_caller.ENV,$ptascii("name")) = (n_alias)',
        '$lookup(S_caller.ENV,$ptascii("alias")) = (n_alias)',
        'pframe_link.TODO = (AUTO_RESULT pautoloadcall_J pautoloadentry_J poperand_J) :: ptask_link*',
        'pautoloadcall_J.MODE = AUTO_LOOKUP',
        'pautoloadcall_J.NAME = $ptascii("J119R")',
        'pautoloadcall_J.RESUME = AUTO_INTERFACE porigin_I $ptascii("J119R")',
        'S_saved = $constant_frame_scope(S_front,pframe_link,eps)',
        '$autoload_selected_valid(S_saved,pautoloadcall_J,pautoloadentry_J)',
        '$class_at(S_front.CLASSES,porigin_I) = (pclassdesc_I)',
        'pclassdesc_I.KIND = "interface"',
        'pclassdesc_I.NAME = $ptascii("I119R")',
        '$class_named(S_front.CLASSNAMES,$ptascii("i119r")) = eps',
        '$autoload_interface_kind($origin_node(S_front.SOURCES,porigin_I)) = ("interface")',
        '$autoload_trait_kind($origin_node(S_front.SOURCES,porigin_I)) = eps',
        '$autoload_new_unlinked_call(S_saved,pautoloadcall_J,$ptascii("i119r"))',
        '$autoload_new_unlinked_frames(S_front,S_front.FRAMES,$ptascii("i119r"))',
        '$autoload_pending(S_read,$ptascii("i119r"))',
        '~$autoload_new_pending(S_read,$ptascii("i119r"))',
        '$autoload_new_pending(S_read,$ptascii("Unrelated119R"))',
        '~$autoload_new_unlinked_call(S_saved,pautoloadcall_J,$ptascii("Unrelated119R"))',
        '~$s119r_marker(S_front.TODO)',
        'pautoloadcall_wrong = pautoloadcall_J[.RESUME = AUTO_INTERFACE porigin_new $ptascii("J119R")]',
        '~$autoload_selected_valid(S_saved,pautoloadcall_wrong,pautoloadentry_J)',
        '~$autoload_new_unlinked_call(S_saved,pautoloadcall_wrong,$ptascii("i119r"))',
        '$call_descriptors_valid(S_front)',
        'S_budget = $drive_steps(S_front,0)',
        'S_budget = S_front[.COMPLETION = BUDGET]',
        'S_resume = $s119r_running(S_budget)',
        'S_resume = S_front',
        'PhpStep: S_resume ~> S_raw',
        'S_raw.COMPLETION = THROWN "Error" (' + term(b'Class "\\i119r" not found') + ') z_fetch',
        'S_raw.TODO = S_front.TODO',
        '~$s119r_marker(S_raw.TODO)',
        'S_raw.FRAMES = S_front.FRAMES',
        'S_raw.AUTOLOAD = S_front.AUTOLOAD',
        'S_raw.CLASSNAMES = S_front.CLASSNAMES',
        'S_raw.EVENTS = S_front.EVENTS',
        'S_waitJ = $drive_steps(S_raw,5000)',
        'S_waitJ.COMPLETION = SOURCE_PENDING',
        'S_waitJ.EVALCONTEXTS = pevalcontext_J :: pevalcontext_outer2 :: eps',
        'pevalcontext_J.UNIT = 2',
        'pevalcontext_outer2.UNIT = 1',
        '$eval_response_valid(S_waitJ,' + dependency_response + ')',
        'S_bodyJ = $eval_resume(S_waitJ,' + dependency_response + ')',
        'S_pub_found = $s119r_seek(S_bodyJ,true,5000)',
        r'S_pub_found.COMPLETION = NORMAL \/ S_pub_found.COMPLETION = BUDGET',
        'S_pub = $s119r_running(S_pub_found)',
        '$s119r_front(S_pub,true)',
        'S_pub.FRAMES = eps',
        'S_pub.TODO = (DYNAMIC_NEW_CLASS z_pub z_pub_fetch) :: ptask_pub*',
        'S_pub.ORIGIN = (porigin_pub)',
        'z_pub = 29',
        'z_pub_fetch = 29',
        'S_pub_read = $resolve_at(S_pub,S_pub.RESULT,z_pub_fetch)',
        'S_pub_read.RESULT = KNOWN pvalue_pub',
        '$string_bytes(pvalue_pub) = (' + term(b'\\i119r') + ')',
        '$class_named(S_pub.CLASSNAMES,$ptascii("i119r")) = (porigin_I)',
        '$dynamic_new_known(S_pub_read,$ptascii("i119r"))',
        '~$autoload_new_pending(S_pub_read,$ptascii("i119r"))',
        '~$s119r_marker(S_pub.TODO)',
        '$call_descriptors_valid(S_pub)',
        'S_pub_budget = $drive_steps(S_pub,0)',
        'S_pub_budget = S_pub[.COMPLETION = BUDGET]',
        'S_pub_resume = $s119r_running(S_pub_budget)',
        'S_pub_resume = S_pub',
        'PhpStep: S_pub_resume ~> S_pub_error',
        'S_pub_error.COMPLETION = THROWN "Error" ($ptascii("Cannot instantiate interface I119R")) z_pub_fetch',
        'S_pub_error.TODO = (DYNAMIC_NEW_FINISH pdynamicnew_pub) :: ptask_pub*',
        'pdynamicnew_pub.SITE = porigin_pub',
        'pdynamicnew_pub.SOURCE = pvalue_pub',
        'pdynamicnew_pub.CLASS = $ptascii("i119r")',
        '$dynamic_new_valid(S_pub_error,pdynamicnew_pub)',
        '$call_task_valid(S_pub_error,DYNAMIC_NEW_FINISH pdynamicnew_pub)',
        '$task_nodes(DYNAMIC_NEW_FINISH pdynamicnew_pub) = eps',
        'S_pub_error.AUTOLOAD = S_pub.AUTOLOAD',
        'S_pub_error.EVENTS = S_pub.EVENTS',
        '$call_descriptors_valid(S_pub_error)',
        'S_finish = $drive_steps(S_pub_error,5000)',
        'S_finish.COMPLETION = NORMAL',
        'S_finish.EXITSTATUS = 0',
        'S_finish.TODO = eps',
        'S_finish.FRAMES = eps',
        '$s119r_output(S_finish.EVENTS) = ' + term(expected_bytes),
        '$call_descriptors_valid(S_finish)',
    ]
