#!/usr/bin/env python3
"""Finite helper provenance follows actual frame positions before native reporting."""
import argparse
import base64
import json
import os
from pathlib import Path
import re
import tempfile
import time

from recorded_worker import Worker
import output_deprecation_warning_review_state as runner
import output_call_contour_sources as sources
import output_object_conversion_review_sources as support

ROOT = support.ROOT
PREFIX = r'''
dec $cc_last(pframe*) : pframe?
def $cc_last([pframe]) = (pframe)
def $cc_last(pframe :: pframe_tail*) = $cc_last(pframe_tail*)
  -- if pframe_tail* =/= eps
def $cc_last(eps) = eps
dec $cc_phase(pstate, nat) : bool
def $cc_phase(S, 0) = true
  -- if S.TODO = (ORDINARY_CTOR_RECEIVE pordinaryinternal) :: ptask_tail*
  -- if pordinaryinternal.INDEX = 3
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = pcallcontext.FUNCTION
  -- if $cc_last(S.FRAMES) = (pframe)
  -- if pframe.TODO = (STRINGIFY_RESULT n porigin z) :: (OB_USER_OBJECT_STRING pobobjectreturn) :: ptask_native*
def $cc_phase(S, 1) = true
  -- if S.TODO = (ORDINARY_CTOR_RECEIVE pordinaryinternal) :: ptask_tail*
  -- if pordinaryinternal.INDEX = 3
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = pcallcontext.FUNCTION
  -- if $cc_last(S.FRAMES) = (pframe)
  -- if pframe.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: ptask_native*
def $cc_phase(S, 2) = true
  -- if S.TODO = [THROW_SEARCH n]
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = pcallcontext.FUNCTION
  -- if $ob_object_call_pending(S[.COMPLETION = NORMAL])

def $cc_phase(S, 3) = true
  -- if S.TODO = (CATCH_BIND porigin n_index n) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = pcallcontext.FUNCTION
def $cc_phase(S, 4) = true
  -- if S.TODO = [RETURN_UNWIND poperand porigin?]
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = pcallcontext.FUNCTION
def $cc_phase(S, 5) = true
  -- if S.TODO = (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: (OUTPUT_FINAL_OBJECT_CV pobobjectreturn) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $cc_phase(S, 6) = true
  -- if S.TODO = (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: (DESTRUCTOR_C_RETURN pdestructorcall) :: (DESTRUCTOR_RESULT pdestructorcall) :: (OUTPUT_FINAL_OBJECT_LOCAL_THROW pobobjectreturn pdestructorcall pobobjectsource eps) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $cc_phase(S, 7) = true
  -- if S.TODO = [OUTPUT_FINAL_DEACTIVATE pobdeactivate]
  -- if pobdeactivate.INDEX = 0

def $cc_phase(S, n) = false -- otherwise
dec $cc_seek(pstate, nat, nat) : pstate
def $cc_seek(S, n_phase, n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $cc_seek(S, n_phase, n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $cc_phase(S, n_phase)
def $cc_seek(S, n_phase, 0) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$cc_phase(S, n_phase)
def $cc_seek(S, n_phase, n) = $cc_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_phase, $nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$cc_phase(S, n_phase) /\ $(n > 0)
'''


WALK = r"""
dec $cc_all(bool*) : bool
def $cc_all(eps) = true
def $cc_all(b :: bool*) = (b /\ $cc_all(bool*))
dec $cc_walk(pstate, porigin, pobctorbirth, pobsourcecontour, nat) : (pstate, bool*)
def $cc_walk(S, porigin, pobctorbirth, pobsourcecontour, 0) = (S, [b])
  -- if $ob_object_call_fold(S) = ((S_native, pfunction_current, pobsourcecontour_current))
  -- if b = ($ob_object_native_source(S_native) = (OBJECT_CALL_UNWIND porigin pobctorbirth pobsourcecontour) /\ pobsourcecontour.CURSOR = |pobsourcecontour.CALLS| /\ pobsourcecontour_current.CALLS = eps)
def $cc_walk(S, porigin, pobctorbirth, pobsourcecontour, n) = (S_final, [b_budget, b_step, b_frame, b_owner, b_public, b_refuse] ++ bool_tail*)
  -- if $(n > 0)
  -- if S_exit_found = $cc_seek(S, 2, 512)
  -- if S_exit_found.COMPLETION = NORMAL \/ S_exit_found.COMPLETION = BUDGET
  -- if S_exit = S_exit_found[.COMPLETION = NORMAL]
  -- if S_exit.TODO = [THROW_SEARCH pobctorbirth.OBJECT]
  -- if S_exit.CURRENT = (pcallcontext)
  -- if S_exit.FRAMES = pframe_call :: pframe_tail*
  -- if $ob_object_call_active(S_exit) = ((S_native, pfunction_producer, pobsourcecontour))
  -- if S_raw = $restore_frame_raw(S_exit)
  -- if S_wrong_pending = S_exit[.TODO = [THROW_SEARCH 0]]
  -- if S_no_pop = S_raw[.FRAMES = S_exit.FRAMES]
  -- if S_skip_pop = S_raw[.FRAMES = eps]
  -- if S_wrong_origin = S_raw[.ORIGIN = eps]
  -- if S_budget = $drive_steps(S_exit, 0)
  -- if S_one_found = $drive_steps(S_exit, 1)
  -- if S_one_found.COMPLETION = BUDGET
  -- if S_one = S_one_found[.COMPLETION = NORMAL]
  -- if $ob_object_call_fold(S_one) = ((S_native_next, pfunction_next, pobsourcecontour_active))
  -- if $ob_object_source_call($ob_object_native_source(S_native_next)) = (pobsourcecontour_next)
  -- if S_one.DESTRUCTION.FRAMES = pdestructionframe :: pdestructionframe_tail*
  -- if b_budget = (S_budget.COMPLETION = BUDGET /\ S_budget.CURRENT = S_exit.CURRENT /\ S_budget.FRAMES = S_exit.FRAMES /\ S_budget.TODO = S_exit.TODO /\ S_budget.ALLOCATIONS = S_exit.ALLOCATIONS /\ S_budget.GC = S_exit.GC /\ S_budget.EVENTS = S_exit.EVENTS)
  -- if b_step = (pobsourcecontour_next.NATIVE = pobsourcecontour.NATIVE /\ pobsourcecontour_next.CALLS = pobsourcecontour.CALLS /\ pobsourcecontour_next.CURSOR = $(pobsourcecontour.CURSOR + 1) /\ |S_one.FRAMES| = $(|S_exit.FRAMES| - 1) /\ S_one.CURRENT = pframe_call.CONTEXT /\ S_one.ORIGIN = pframe_call.ORIGIN /\ S_one.EVENTS = [OUTPUT ([80])])
  -- if b_frame = (pdestructionframe.FUNCTION = pcallcontext.FUNCTION /\ pdestructionframe.CALLER = pframe_call.CONTEXT /\ pdestructionframe.ORIGIN = pframe_call.ORIGIN /\ pdestructionframe.PENDING = (pobctorbirth.OBJECT))
  -- if b_owner = ($heap_count(HOBJECT pobctorbirth.OBJECT, $machine_roots(S_exit)) = 1 /\ $heap_count(HOBJECT pobctorbirth.OBJECT, $machine_roots(S_one)) = 1)
  -- if b_public = ($call_descriptors_valid(S_one) /\ $heap_valid($heap_graph(S_one)) /\ $output_state_valid(S_one) /\ $destruction_state_valid(S_one))
  -- if b_refuse = ($destructor_frame_restore(S_wrong_pending, S_raw) = S_raw /\ $destructor_frame_restore(S_exit, S_no_pop) = S_no_pop /\ $destructor_frame_restore(S_exit, S_skip_pop) = S_skip_pop /\ $destructor_frame_restore(S_exit, S_wrong_origin) = S_wrong_origin)
  -- if (S_final, bool_tail*) = $cc_walk(S_one, porigin, pobctorbirth, pobsourcecontour_next, $nabs($(n - 1)))
"""
PREFIX += WALK


def public(state):
    return (f'$call_descriptors_valid({state}) /\\ $heap_valid($heap_graph({state})) /\\ '
            f'$output_state_valid({state}) /\\ $destruction_state_valid({state})')




def reach_ctor(fixture, path, local):
    return [
        'S_initial = $php_file_run(' + fixture + ', 0, ' + runner.bytes_expr(os.fsencode(path)) + ', ' + runner.bytes_expr(os.fsencode(path.parent)) + ')',
        f'S_found = $cc_seek(S_initial, {int(local)}, 1024)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', f'$cc_phase(S, {int(local)})',
        'S.TODO = (ORDINARY_CTOR_RECEIVE pordinaryinternal) :: ptask_tail*',
        'pctorcall_source = pordinaryinternal.SOURCE', 'pctorcall = pordinaryinternal.CALL',
        'pordinaryinternal.VALUES = [pvalue_message, PINT z_code, PNULL]',
        'n_exception = pctorcall.RECEIVER', 'S.CURRENT = (pcallcontext_leaf)',
        'S.FRAMES = pframe_first :: pframe_tail*',
        '$function_at(S.FUNCTIONS, pcallcontext_leaf.FUNCTION) = (pfunction_leaf)',
    ]



def reach_throw(fixture, path, local):
    bindings = reach_ctor(fixture, path, local) + [
        'S_done_found = $drive_steps(S, 1)', 'S_done_found.COMPLETION = BUDGET',
        'S_done = S_done_found[.COMPLETION = NORMAL]',
        '$ob_object_call_context(S_done) = ((S_native_born, pfunction_leaf, pobsourcecontour))',
        '$ob_object_native_source(S_native_born) = (OBJECT_CALL_NEW porigin_throw pobctorbirth pobsourcecontour)',
        'pobctorbirth.OBJECT = n_exception',
        'S_throw_found = $drive_steps(S_done, 1)', 'S_throw_found.COMPLETION = BUDGET',
        'S_throw = S_throw_found[.COMPLETION = NORMAL]',
        'S_throw.TODO = (THROW_VALUE porigin_throw z_throw) :: ptask_throw*',
        'S_active_found = $drive_steps(S_throw, 1)', 'S_active_found.COMPLETION = BUDGET',
        'S_active = S_active_found[.COMPLETION = NORMAL]',
        'S_active.TODO = (THROW_SEARCH n_exception) :: ptask_unwind*',
        '$ob_object_call_active(S_active) = ((S_native_active, pfunction_leaf, pobsourcecontour))',
        '$ob_object_native_source(S_native_active) = (OBJECT_CALL_THROW porigin_throw pobctorbirth pobsourcecontour)',
        'S_native_active.CURRENT = (pcallcontext_native)',
        'S_native_active.FRAMES = [pframe_native]',
        '$function_at($all_functions(S), pobsourcecontour.NATIVE) = (pfunction_native)',
    ]
    if local:
        bindings += [
            'pframe_native.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: (OUTPUT_FINAL_OBJECT_LOCAL_THROW pobobjectreturn pdestructorcall pobobjectsource_active eps) :: ptask_native*',
            'pdestructorcall.FRAME = (pdestructionframe_outer)', 'pdestructionframe_outer.PENDING = (n_old)',
        ]
    else:
        bindings += [
            'pframe_native.TODO = (STRINGIFY_RESULT n_object porigin_site 0) :: (OB_USER_OBJECT_STRING pobobjectreturn) :: ptask_native*',
            '$lookup(S_native_active.ENV, $ptascii("d")) = (n_cell)',
            'S.STORE[n_cell] = DEFINED (POBJECT n_local)',
        ]
    return bindings


def roots(state, local):
    result = (f'$heap_count(HOBJECT pobobjectreturn.OBJECT, $machine_roots({state})) = 2 /\\ '
              f'$heap_count(HOBJECT n_exception, $machine_roots({state})) = 1')
    if local:
        result += (f' /\\ $heap_count(HOBJECT pdestructorcall.OBJECT, $machine_roots({state})) = 2'
                   f' /\\ $heap_count(HOBJECT n_old, $machine_roots({state})) = 1')
    return result


def transport_assertions(fixture, path, local):
    bindings = reach_throw(fixture, path, local) + [
        'S_active.FRAMES = pframe_first_active :: pframe_active_tail*',
        'pframe_first_active.CONTEXT = (pcallcontext_caller)',
        'pframe_first_active.LOCALS = (psymboltable_caller)',
        'S_name = S_active[.FRAMES = pframe_first_active[.CONTEXT = (pcallcontext_caller[.NAME = $ptascii("wrong")])] :: pframe_active_tail*]',
        'S_cvs = S_active[.FRAMES = pframe_first_active[.LOCALS = (psymboltable_caller[.CVS = eps])] :: pframe_active_tail*]',
        'S_held = S_active[.FRAMES = pframe_first_active[.HELD = [HOBJECT n_exception]] :: pframe_active_tail*]',
        'S_tasks = S_active[.FRAMES = pframe_first_active[.TODO = pframe_first_active.TODO ++ [THROW_SEARCH n_exception]] :: pframe_active_tail*]',
        'pobsourcecontour_skip = pobsourcecontour[.CURSOR = 1]',
        'pobsourcecontour_native = pobsourcecontour[.NATIVE = pfunction_leaf.ORIGIN]',
        'S_skip = $ob_object_call_capture(S_active, (OBJECT_CALL_THROW porigin_throw pobctorbirth pobsourcecontour_skip))',
        'S_wrong_native = $ob_object_call_capture(S_active, (OBJECT_CALL_THROW porigin_throw pobctorbirth pobsourcecontour_native))',
        'S_early_unwind = $ob_object_call_capture(S_active, (OBJECT_CALL_UNWIND porigin_throw pobctorbirth pobsourcecontour))',
        '(S_arrived, bool_walk*) = $cc_walk(S_active, porigin_throw, pobctorbirth, pobsourcecontour, |pobsourcecontour.CALLS|)',
        '$ob_object_call_fold(S_arrived) = ((S_arrived, pfunction_native, pobsourcecontour_empty))',
        '$ob_object_native_source(S_arrived) = (OBJECT_CALL_UNWIND porigin_throw pobctorbirth pobsourcecontour_final)',
    ]
    checks = [
        ('actual leaf constructor keeps selected receiver and normalized immutable birth', r'pctorcall_source.RECEIVER = n_exception /\ pctorcall_source.MODE = CTOR_NEW /\ pctorcall.MODE = CTOR_NEW /\ pctorcall_source.SITE = pctorcall.SITE /\ $ctor_selected(S, pctorcall_source) /\ pobctorbirth.SITE = pctorcall.SITE /\ $string_bytes(pvalue_message) = (pobctorbirth.MESSAGE) /\ pobctorbirth.CODE = z_code /\ pobctorbirth.LINE = pctorcall.LINE /\ $ob_object_ctor_fact_live(S_done, pobctorbirth)'),
        ('nonempty immutable contour authenticates every selected edge and original native consumer', r'pobsourcecontour.CURSOR = 0 /\ $(|pobsourcecontour.CALLS| > 1) /\ pobsourcecontour.NATIVE = pfunction_native.ORIGIN /\ $ob_object_call_functions(S, pfunction_native, pobsourcecontour.CALLS) = (pfunction_leaf) /\ $ob_object_ctor_fact_source(S, pfunction_leaf, porigin_throw, pobctorbirth) /\ pfunction_leaf.ORIGIN =/= pfunction_native.ORIGIN'),
        ('helper capture remains nonowning and has no early native authority', r'$ob_object_source_thrown((OBJECT_CALL_THROW porigin_throw pobctorbirth pobsourcecontour)) = eps /\ S_active.EVENTS = [OUTPUT ([80])] /\ ' + roots('S_active', local)),
        ('wrong intermediate name CV table and continuation owners are refused', r'$ob_object_call_context(S_name) = eps /\ $ob_object_call_context(S_cvs) = eps /\ $ob_object_call_context(S_held) = eps /\ $ob_object_call_context(S_tasks) = eps'),
        ('skipped cursor and wrong original native origin cannot borrow the active suffix', r'$ob_object_call_active(S_skip) = eps /\ $ob_object_call_active(S_wrong_native) = eps /\ ~$ob_object_call_pending(S_early_unwind) /\ $ob_object_source_thrown((OBJECT_CALL_UNWIND porigin_throw pobctorbirth pobsourcecontour)) = eps'),
        ('every actual edge has exactly one budgeted VM restore and preserves its own cleanup frame', r'$cc_all(bool_walk*) /\ |bool_walk*| = $(6 * |pobsourcecontour.CALLS| + 1)'),
        ('arrival exhausts the contour at the original native caller before C0 reporting', r'pobsourcecontour_final.NATIVE = pobsourcecontour.NATIVE /\ pobsourcecontour_final.CALLS = pobsourcecontour.CALLS /\ pobsourcecontour_final.CURSOR = |pobsourcecontour.CALLS| /\ pobsourcecontour_empty.CALLS = eps /\ S_arrived.CURRENT = (pcallcontext_native) /\ S_arrived.CURRENT =/= eps /\ S_arrived.EVENTS = [OUTPUT ([80])] /\ ' + roots('S_arrived', local)),
    ]
    if local:
        bindings += ['pobsourcecontour.CALLS = [pobsourcecall_0, pobsourcecall_1, pobsourcecall_2]']
        checks += [('recursion uses real frame positions rather than distinct origins or contexts', r'|S.FRAMES| = 4 /\ S.CURRENT = pframe_first.CONTEXT /\ pobsourcecall_0 = pobsourcecall_1 /\ pobsourcecall_0.FUNCTION = pobsourcecall_2.FUNCTION')]
    if not local:
        checks += [('native caller retains its ordinary D local through all helper edges', r'$object_name(S_active, n_local) = $ptascii("D") /\ $heap_owners($heap_graph(S_active), HOBJECT n_local) = 1 /\ $heap_owners($heap_graph(S_arrived), HOBJECT n_local) = 1 /\ ~(n_local <- S_arrived.DESTRUCTION.CALLED)')]
    return bindings, checks


def fatal(path, local):
    if local:
        message, line, frames = 'F', 14, [f'#0 {path}(12): recur()', f'#1 {path}(12): recur()', f'#2 {path}(8): recur()', '#3 [internal function]: T->__destruct()', '#4 {main}']
    else:
        message, line, frames = 'E', 16, [f'#0 {path}(13): leaf()', f'#1 {path}(9): middle()', '#2 [internal function]: T->__toString()', '#3 {main}']
    return (f'Fatal error: Uncaught Exception: {message} in {path}:{line}\nStack trace:\n' + '\n'.join(frames) + f'\n  thrown in {path} on line {line}\n').encode()


def clearing_assertions(fixture, path, local, stage):
    bindings = reach_throw(fixture, path, local) + [
        'S_exit_found = $cc_seek(S_active, 2, 512)',
        r'S_exit_found.COMPLETION = NORMAL \/ S_exit_found.COMPLETION = BUDGET',
        'S_exit = S_exit_found[.COMPLETION = NORMAL]',
        'S_exit.FRAMES = pframe_depart :: pframe_remaining*',
        'S_one_found = $drive_steps(S_exit, 1)', 'S_one_found.COMPLETION = BUDGET',
        'S_one = S_one_found[.COMPLETION = NORMAL]',
        '$ob_object_call_fold(S_one) = ((S_native_one, pfunction_middle, pobsourcecontour_remaining))',
        '$ob_object_native_source(S_native_one) = (OBJECT_CALL_THROW porigin_throw pobctorbirth pobsourcecontour_one)',
        f'S_clear_found = $cc_seek(S_one, {3 if stage == "catch" else 4}, 512)',
        r'S_clear_found.COMPLETION = NORMAL \/ S_clear_found.COMPLETION = BUDGET',
        'S_clear = S_clear_found[.COMPLETION = NORMAL]',
        '$ob_object_native_source(S_clear) = eps',
        'S_clear.CURRENT = (pcallcontext_middle)',
    ]
    checks = [
        ('one real edge is consumed before the intermediate override', r'pobsourcecontour_one.CALLS = pobsourcecontour.CALLS /\ pobsourcecontour_one.NATIVE = pobsourcecontour.NATIVE /\ pobsourcecontour_one.CURSOR = 1 /\ $(pobsourcecontour_one.CURSOR < |pobsourcecontour_one.CALLS|) /\ |S_one.FRAMES| = $(|S_exit.FRAMES| - 1) /\ S_one.CURRENT = pframe_depart.CONTEXT /\ S_one.EVENTS = [OUTPUT ([80])]'),
        ('intermediate cleanup and clearing preserve real C owners and public validity', public('S_clear')),
    ]
    if stage == 'catch':
        bindings += ['S_clear.TODO = (CATCH_BIND porigin_try n_index n_exception) :: ptask_catch*']
        checks += [('intermediate catch clears the remaining contour with E still owned', r'pcallcontext_middle.FUNCTION =/= pfunction_leaf.ORIGIN /\ (HOBJECT n_exception) <- S_clear.ALLOCATIONS /\ $task_nodes(CATCH_BIND porigin_try n_index n_exception) = [HOBJECT n_exception] /\ S_clear.EVENTS = [OUTPUT ([80])] /\ ' + roots('S_clear', local) + r' /\ $heap_owners($heap_graph(S_clear), HOBJECT n_local) = 1')]
    else:
        bindings += [
            'S_clear.TODO = [RETURN_UNWIND (KNOWN pvalue_return) porigin_return?]',
            'S_normal_found = $drive_steps(S_clear, 1)', 'S_normal_found.COMPLETION = BUDGET',
            'S_normal = S_normal_found[.COMPLETION = NORMAL]',
        ]
        owner = roots('S_clear', local).replace('$heap_count(HOBJECT n_exception, $machine_roots(S_clear)) = 1', '$heap_count(HOBJECT n_exception, $machine_roots(S_clear)) = 0')
        checks += [('recursive finally consumes F and the whole outstanding contour', r'pcallcontext_middle.FUNCTION = pfunction_leaf.ORIGIN /\ ~((HOBJECT n_exception) <- S_clear.ALLOCATIONS) /\ $string_bytes(pvalue_return) = ($ptascii("H")) /\ S_clear.EVENTS = [OUTPUT ([80])] /\ ' + owner), ('later normal restore cannot regain stale exceptional authority', r'$ob_object_native_source(S_normal) = eps /\ $heap_count(HOBJECT n_exception, $machine_roots(S_normal)) = 0 /\ S_normal.EVENTS = [OUTPUT ([80])]')]
    return bindings, checks


def report_assertions(fixture, path, local):
    bindings, transport_checks = transport_assertions(fixture, path, local)
    bindings += [
        f'S_exit_found = $cc_seek(S_arrived, {6 if local else 5}, 512)',
        r'S_exit_found.COMPLETION = NORMAL \/ S_exit_found.COMPLETION = BUDGET',
        'S_exit = S_exit_found[.COMPLETION = NORMAL]',
        'S_exit.TODO = (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: ptask_return*',
        'pobsourcecontour_early = pobsourcecontour_final[.CURSOR = 0]',
        'pobsourcecall_mid = pobsourcecontour_final.CALLS[1]',
        'pobsourcecall_wrong = pobsourcecall_mid[.SITE = porigin_throw]',
        'pobsourcecontour_foreign = pobsourcecontour_final[.CALLS = pobsourcecontour_final.CALLS[0:1] ++ [pobsourcecall_wrong] ++ pobsourcecontour_final.CALLS[2:$nabs($(|pobsourcecontour_final.CALLS| - 2))]]',
        'pobobjectsource_final = OBJECT_CALL_UNWIND porigin_throw pobctorbirth pobsourcecontour_final',
        'pobobjectsource_early = OBJECT_CALL_UNWIND porigin_throw pobctorbirth pobsourcecontour_early',
        'pobobjectsource_foreign = OBJECT_CALL_UNWIND porigin_throw pobctorbirth pobsourcecontour_foreign',
    ]
    if local:
        bindings += ['ptask_return* = [DESTRUCTOR_C_RETURN pdestructorcall, DESTRUCTOR_RESULT pdestructorcall, OUTPUT_FINAL_OBJECT_LOCAL_THROW pobobjectreturn pdestructorcall pobobjectsource_final eps] ++ ptask_native*']
        ready = '$ob_object_final_local_ready(S_exit, pobobjectreturn, pdestructorcall, porigin_throw, n_exception, pdestructionframe, ptask_return*)'
    else:
        bindings += [
            'pobobjectreturn_final = pobobjectreturn[.SOURCE = (pobobjectsource_final)]',
            'ptask_return* = (OUTPUT_FINAL_OBJECT_CV pobobjectreturn_final) :: ptask_native*',
        ]
        ready = '$ob_object_final_cv_ready(S_exit, pobobjectreturn_final, pdestructionframe, n_exception)'
    bindings += [
        'S_report_found = $drive_steps(S_exit, 1)', 'S_report_found.COMPLETION = BUDGET',
        'S_report = S_report_found[.COMPLETION = NORMAL]',
        'S_report.TODO = [OUTPUT_FINAL_PENDING pobdeactivate n_exception true]',
        'S_deactivate_found = $cc_seek(S_report, 7, 512)',
        r'S_deactivate_found.COMPLETION = NORMAL \/ S_deactivate_found.COMPLETION = BUDGET',
        'S_deactivate = S_deactivate_found[.COMPLETION = NORMAL]',
    ]
    if local:
        bindings += [
            'S_report.DESTRUCTION.ABANDONED = [pdestructioncleanup_local, pdestructioncleanup_outer]',
            'pdestructioncleanup_early = pdestructioncleanup_outer[.SOURCE = OUTPUT_FINAL_OBJECT_LOCAL_THROW pobobjectreturn pdestructorcall pobobjectsource_early (pobdeactivate)]',
            'pdestructioncleanup_foreign = pdestructioncleanup_outer[.SOURCE = OUTPUT_FINAL_OBJECT_LOCAL_THROW pobobjectreturn pdestructorcall pobobjectsource_foreign (pobdeactivate)]',
            'S_early = S_deactivate[.DESTRUCTION.ABANDONED = [pdestructioncleanup_local, pdestructioncleanup_early]]',
            'S_foreign = S_deactivate[.DESTRUCTION.ABANDONED = [pdestructioncleanup_local, pdestructioncleanup_foreign]]',
        ]
    else:
        bindings += [
            'S_report.DESTRUCTION.ABANDONED = [pdestructioncleanup_outer]',
            'pobobjectreturn_early = pobobjectreturn[.SOURCE = (pobobjectsource_early)]',
            'pobobjectreturn_foreign = pobobjectreturn[.SOURCE = (pobobjectsource_foreign)]',
            'pdestructioncleanup_early = pdestructioncleanup_outer[.SOURCE = OUTPUT_FINAL_OBJECT_THROW pobobjectreturn_early pobdeactivate porigin_throw n_exception]',
            'pdestructioncleanup_foreign = pdestructioncleanup_outer[.SOURCE = OUTPUT_FINAL_OBJECT_THROW pobobjectreturn_foreign pobdeactivate porigin_throw n_exception]',
            'S_early = S_deactivate[.DESTRUCTION.ABANDONED = [pdestructioncleanup_early]]',
            'S_foreign = S_deactivate[.DESTRUCTION.ABANDONED = [pdestructioncleanup_foreign]]',
        ]
    warning = '' if local else ', WARNING ($ptascii("missing")) 4'
    events = '[OUTPUT ([80])' + warning + ', STDERR ' + runner.bytes_expr(fatal(path, local)) + ']'
    retired = roots('S_deactivate', local).replace('$heap_count(HOBJECT n_exception, $machine_roots(S_deactivate)) = 1', '$heap_count(HOBJECT n_exception, $machine_roots(S_deactivate)) = 0')
    checks = [
        ('only the original native cleanup frame reports the exhausted contour', ready + r' /\ pdestructionframe.FUNCTION = pfunction_native.ORIGIN /\ pdestructionframe.FUNCTION =/= pfunction_leaf.ORIGIN /\ S_exit.CURRENT = eps /\ S_exit.FRAMES = eps /\ S_exit.ORIGIN = eps'),
        ('complete helper contour trace reports after native cleanup with retained owners', 'S_report.EVENTS = ' + events + r' /\ S_report.EXITSTATUS = 255 /\ $throwable_field(S_report, n_exception, "previous") = PNULL /\ ' + roots('S_report', local)),
        ('retired Throwable owns no contour reference or real C guard', r'~((HOBJECT n_exception) <- S_deactivate.ALLOCATIONS) /\ $eager_cleanup_valid(S_deactivate, pdestructioncleanup_outer) /\ S_deactivate.EVENTS = S_report.EVENTS /\ ' + retired),
        ('retired receipts reject a false exhausted tag and a foreign middle call edge', r'~$eager_cleanup_valid(S_early, pdestructioncleanup_early) /\ ~$eager_cleanup_valid(S_foreign, pdestructioncleanup_foreign) /\ $task_nodes(pdestructioncleanup_outer.SOURCE) = eps /\ $eager_abandoned_owner(pdestructioncleanup_outer.SOURCE) = [HOBJECT pobobjectreturn.OBJECT, HOBJECT pobobjectreturn.OBJECT]'),
    ]
    return bindings, transport_checks + checks


def assertions(fixture, path, local, stage):
    if stage == 'transport':
        return transport_assertions(fixture, path, local)
    if stage == 'report':
        return report_assertions(fixture, path, local)
    return clearing_assertions(fixture, path, local, stage)


def render(bindings, checks):
    return (PREFIX + '\ndec $main() : bool*\ndef $main() = [' +
            ', '.join('(' + check + ')' for _, check in checks) + ']\n' +
            ''.join('  -- if ' + binding + '\n' for binding in bindings))


def fingerprint():
    return {name: support.common.sha(ROOT / name) for name in (
        'spec/semantics/30-storage.watsup', 'spec/semantics/456-output-object-returns.watsup',
        'spec/semantics/257-request-destructors.watsup', 'spec/semantics/modules.json',
        'tests/semantics/output_call_contour_sources.py', 'tests/semantics/output_call_contour_review_state.py',
        'tests/semantics/_build/default/numeric_runner.exe', '_build/default/adapter/main.exe', '.tools/php/bin/php')}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--stage', choices=('transport', 'report', 'catch', 'normal'), default='transport')
    parser.add_argument('--native-root', type=Path, help='Frozen source/path reference; never execute the oracle.')
    parser.add_argument('--select', choices=('cv', 'local', 'all'), default='all')
    args = parser.parse_args()
    out = args.output or Path(tempfile.mkdtemp(prefix='output-call-contour-review-'))
    out.mkdir(parents=True, exist_ok=True)
    report = {'revision': support.subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD']).decode().strip(),
              'before': fingerprint(), 'profile': support.common.PROFILE, 'native_agreement_credit': 0,
              'cap_seconds': 300, 'stage': args.stage, 'records': [], 'passed': False}
    directory = out
    try:
        modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
        cases = list(sources.CASES.items())
        selected = range(2) if args.stage in ('transport', 'report') else [2 if args.stage == 'catch' else 3]
        for index in selected:
            name, source = cases[index]
            local = bool(index % 2)
            short = 'local' if local else 'cv'
            if args.select not in ('all', short):
                continue
            directory = out / short
            directory.mkdir()
            frozen = args.native_root is not None
            native_case = ('native-01', 'native-03', 'native-control-01', 'native-control-03')[index]
            path = args.native_root / native_case / 'source.php' if frozen else directory / 'source.php'
            if frozen:
                assert path.read_bytes() == source
            else:
                path.write_bytes(source)
            frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], directory / 'frontend')
            try:
                parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source).decode()})
            finally:
                frontend.close()
            adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
            try:
                checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            finally:
                adapter.close()
            bindings, checks = assertions(checked['fixture'], path, local, args.stage)
            fixture = directory / 'state.watsup'
            fixture.write_text(render(bindings, checks))
            record = {'case': name, 'fixture_sha256': support.common.sha(fixture), 'checks': [label for label, _ in checks], 'passed': False}
            report['records'].append(record)
            started = time.monotonic()
            result = support.common.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl', *[str(ROOT / module) for module in modules], str(fixture)], directory, 'state', 300)
            record['seconds'] = round(time.monotonic() - started, 3)
            rendered = result.stdout.decode('ascii')
            values = re.findall(r'\b(?:true|false)\b', rendered)
            record.update(exit_status=result.returncode, results=dict(zip(record['checks'], [value == 'true' for value in values])))
            assert not re.sub(r'true|false|[\[\](),;\s]', '', rendered), rendered
            assert result.returncode == 0 and not result.stderr and values == ['true'] * len(checks), (result.returncode, result.stdout, result.stderr)
            record['passed'] = True
            (directory / 'report.json').write_text(json.dumps(record, indent=2) + '\n')
            print(short, True, flush=True)
        assert report['records'], 'no fixture selected'
        report['passed'] = True
    except BaseException as error:
        if isinstance(error, support.subprocess.TimeoutExpired):
            (directory / 'state.stdout').write_bytes(error.stdout or b'')
            (directory / 'state.stderr').write_bytes(error.stderr or b'')
            (directory / 'state.timeout').write_text(str(error.timeout) + '\n')
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        report['after'] = fingerprint()
        report['stable'] = report['before'] == report['after']
        report['passed'] = report['passed'] and report['stable']
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(out / 'report.json', report['passed'], flush=True)


if __name__ == '__main__':
    main()
