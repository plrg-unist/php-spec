#!/usr/bin/env python3
"""Native FINAL CV cleanup retains the real cast guard until null-C reporting."""
import argparse
import json
import os
import re
from pathlib import Path
import tempfile

from recorded_worker import Worker
import output_deprecation_warning_review_state as runner
import output_final_cast_locals_sources as sources
import output_object_conversion_review_sources as support

ROOT = support.ROOT
SOURCE = sources.CASES['fresh-throw-local-warning']
CAUGHT_SOURCE = sources.CASES['caught-fresh-normal']
FINALLY_SOURCE = SOURCE.replace(b"        throw new Exception('E');",
                               b"        try { throw new Exception('E'); } finally { return 'H'; }")
EMPTY_SOURCE = b"""<?php
echo 'P';
class T {
    function __toString() {
        if (false) { $unused = 1; }
        throw new Exception('E');
    }
}
function h($b,$p) { return new T; }
ob_start('h'); echo 'A';
"""
UNSTAGED_SOURCE = EMPTY_SOURCE.replace(b"        throw new Exception('E');",
                                     b"        try { throw new Exception('E'); } finally { return 'H'; }")
PREFIX = runner.PREFIX.split('dec $dp_phase', 1)[0] + r'''
dec $cl_cleanup(ptask*, pdestructionframe) : pobobjectreturn?
def $cl_cleanup((DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_tail*, pdestructionframe) = $cl_cleanup(ptask_tail*, pdestructionframe)
def $cl_cleanup((DESTRUCTOR_FRAME_EXIT pdestructionframe) :: (OUTPUT_FINAL_OBJECT_CV pobobjectreturn) :: ptask_tail*, pdestructionframe) = (pobobjectreturn)
  -- if ptask_tail* = pobobjectreturn.TAIL
def $cl_cleanup(ptask*, pdestructionframe) = eps -- otherwise
dec $cl_normal_site(ptask*) : pobobjectreturn?
def $cl_normal_site((OB_USER_OBJECT_NORMAL pobobjectreturn pdestructionframe) :: ptask_tail*) = $cl_normal_site(ptask_tail*)
def $cl_normal_site((STRINGIFY_RESULT n porigin z) :: (OB_USER_OBJECT_STRING pobobjectreturn) :: ptask_tail*) = (pobobjectreturn)
  -- if ptask_tail* = pobobjectreturn.TAIL
def $cl_normal_site(ptask*) = eps -- otherwise
dec $cl_normal_cleanup(ptask*, pdestructionframe) : pobobjectreturn?
def $cl_normal_cleanup((DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_tail*, pdestructionframe) = $cl_normal_cleanup(ptask_tail*, pdestructionframe)
def $cl_normal_cleanup((DESTRUCTOR_FRAME_EXIT pdestructionframe) :: ptask_tail*, pdestructionframe) = $cl_normal_site(ptask_tail*)
def $cl_normal_cleanup(ptask*, pdestructionframe) = eps -- otherwise
dec $dp_phase(pstate, nat) : bool
def $dp_phase(S, 0) = true
  -- if S.TODO = (THROW_VALUE porigin z) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = [pframe]
  -- if pframe.TODO = (STRINGIFY_RESULT n porigin_site 0) :: (OB_USER_OBJECT_STRING pobobjectreturn) :: ptask_native*
  -- if pobobjectreturn.INVOKE.CALL = OB_FINAL pobdrain
def $dp_phase(S, 1) = true
  -- if S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_tail*
  -- if S.DESTRUCTION.FRAMES = [pdestructionframe]
  -- if pdestructionframe.PENDING = (n)
  -- if $cl_cleanup(S.TODO, pdestructionframe) =/= eps
def $dp_phase(S, 2) = true
  -- if S.TODO = (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: (OUTPUT_FINAL_OBJECT_CV pobobjectreturn) :: ptask_native*
  -- if pdestructionframe.PENDING = (n)
def $dp_phase(S, 3) = true
  -- if S.TODO = [OUTPUT_FINAL_DEACTIVATE pobdeactivate]
  -- if pobdeactivate.INDEX = 0
def $dp_phase(S, 5) = true
  -- if S.TODO = [THROW_SEARCH n]
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = [pframe]
  -- if $ob_object_final_cv_method(S) =/= eps
def $dp_phase(S, 6) = true
  -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*
  -- if pdestructorcall.FRAME = (pdestructionframe)
  -- if pdestructionframe.PENDING = (n)
def $dp_phase(S, 7) = true
  -- if S.TODO = (CATCH_BIND porigin n_index n) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = [pframe]
  -- if pframe.TODO = (STRINGIFY_RESULT n_object porigin_site 0) :: (OB_USER_OBJECT_STRING pobobjectreturn) :: ptask_native*
  -- if pobobjectreturn.INVOKE.CALL = OB_FINAL pobdrain
def $dp_phase(S, 9) = true
  -- if S.TODO = [RETURN_UNWIND poperand porigin?]
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = [pframe]
  -- if pframe.TODO = (STRINGIFY_RESULT n_object porigin_site 0) :: (OB_USER_OBJECT_STRING pobobjectreturn) :: ptask_native*
  -- if pobobjectreturn.INVOKE.CALL = OB_FINAL pobdrain
def $dp_phase(S, n) = false -- otherwise
''' + 'dec $dp_seek' + runner.PREFIX.split('dec $dp_seek', 1)[1]


def expected_warning(path):
    return b'Warning: Undefined variable $missing in ' + os.fsencode(path) + b' on line 4\n'


def expected_fatal(path):
    name = os.fsencode(path)
    return (b'Fatal error: Uncaught Exception: E in ' + name + b':9\nStack trace:\n'
            b'#0 [internal function]: T->__toString()\n#1 {main}\n  thrown in ' + name + b' on line 9\n')


def fingerprint():
    inputs = support.fingerprint()
    for name in ('tests/semantics/output_final_cast_locals_sources.py',
                 'tests/semantics/output_final_cast_locals_review_state.py',
                 'tests/semantics/output_deprecation_warning_review_state.py',
                 'tests/semantics/_build/default/numeric_runner.exe'):
        inputs[name] = support.common.sha(ROOT / name)
    return inputs


def assertions(fixture, directory, path, finally_fixture, finally_path):
    bindings = [
        'S_initial = $php_file_run(' + fixture + ', 0, ' + runner.bytes_expr(os.fsencode(path)) + ', ' + runner.bytes_expr(os.fsencode(directory)) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $dp_seek(S_initial, 0, 1024)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]',
        'S.TODO = (THROW_VALUE porigin z) :: ptask_tail*',
        'porigin = PORIGIN n_unit pcpath_throw',
        'S.CURRENT = (pcallcontext)', 'S.FRAMES = [pframe]',
        'pframe.TODO = (STRINGIFY_RESULT n_object porigin_site 0) :: (OB_USER_OBJECT_STRING pobobjectreturn) :: ptask_native*',
        'n_object = pobobjectreturn.OBJECT',
        'pobobjectreturn.INVOKE.CALL = OB_FINAL pobdrain',
        'S.RESULT = KNOWN (POBJECT n_exception)',
        '$lookup(S.ENV, $ptascii("d")) = (n_cell)',
        'S.STORE[n_cell] = DEFINED (POBJECT n_local)',
        'S_capture_found = $drive_steps(S, 1)', 'S_capture_found.COMPLETION = BUDGET',
        'S_capture = S_capture_found[.COMPLETION = NORMAL]',
        'S_capture.FRAMES = [pframe_capture]',
        '$ob_object_source_new(pobobjectreturn.SOURCE) = ((porigin, pobctorbirth))',
        'pobctorbirth.OBJECT = n_exception',
        'pobobjectreturn_capture = pobobjectreturn[.SOURCE = (OBJECT_THROW_BIRTH porigin pobctorbirth)]',
        'S_context_found = $dp_seek(S_capture, 5, 256)',
        r'S_context_found.COMPLETION = NORMAL \/ S_context_found.COMPLETION = BUDGET',
        'S_context = S_context_found[.COMPLETION = NORMAL]',
        'S_context_extra = S_context[.CURRENT = (pcallcontext[.INSTANCE = (n_exception)])]',
        'S_context_receiver = S_context[.CURRENT = (pcallcontext[.RECEIVER = eps])]',
        'S_context_function = S_context[.CURRENT = (pcallcontext[.FUNCTION = porigin][.TARGET = METHOD_TARGET n_object porigin])]',
        'S_context_target = S_context[.CURRENT = (pcallcontext[.TARGET = METHOD_TARGET n_exception pcallcontext.FUNCTION][.RECEIVER = (n_exception)])]',
        'S_context_pending = S_context[.TODO = [THROW_SEARCH n_object]]',
        'S_context_header = S_context[.CURRENT = (pcallcontext[.CALLSITE = (porigin_site)][.LINE = 0])]',
        'pobobjectreturn_bad_source = pobobjectreturn_capture[.SOURCE = (OBJECT_THROW_BIRTH pcallcontext.FUNCTION pobctorbirth)]',
        'S_context_source = S_context[.FRAMES = [pframe_capture[.TODO = (STRINGIFY_RESULT n_object porigin_site 0) :: (OB_USER_OBJECT_STRING pobobjectreturn_bad_source) :: ptask_native*]]]',
        'S_context_stale = S_context[.ALLOCATIONS = $destruction_node_delete(S_context.ALLOCATIONS, HOBJECT n_exception)]',
        'S_stage_found = $dp_seek(S_context, 1, 256)',
        r'S_stage_found.COMPLETION = NORMAL \/ S_stage_found.COMPLETION = BUDGET',
        'S_stage = S_stage_found[.COMPLETION = NORMAL]',
        'S_stage.DESTRUCTION.FRAMES = [pdestructionframe]',
        '$cl_cleanup(S_stage.TODO, pdestructionframe) = (pobobjectreturn_capture)',
        'S_budget = $drive_steps(S_stage, 0)',
        'S_one_found = $drive_steps(S_budget[.COMPLETION = NORMAL], 1)',
        'S_one_found.COMPLETION = BUDGET', 'S_one = S_one_found[.COMPLETION = NORMAL]',
        'S_entry_found = $dp_seek(S_one, 6, 128)',
        r'S_entry_found.COMPLETION = NORMAL \/ S_entry_found.COMPLETION = BUDGET',
        'S_entry = S_entry_found[.COMPLETION = NORMAL]',
        'S_entry.TODO = (DESTRUCTOR_ENTER pdestructorcall_local) :: ptask_entry*',
        'S_entered_found = $drive_steps(S_entry, 1)', 'S_entered_found.COMPLETION = BUDGET',
        'S_entered = S_entered_found[.COMPLETION = NORMAL]',
        'S_entered.CURRENT = (pcallcontext_local)',
        '$trace_context(S_entered, S_entered.ENV, S_entered.CURRENT) = [ptraceframe_local]',
        'S_exit_found = $dp_seek(S_entered, 2, 512)',
        r'S_exit_found.COMPLETION = NORMAL \/ S_exit_found.COMPLETION = BUDGET',
        'S_exit = S_exit_found[.COMPLETION = NORMAL]',
        'S_exit.TODO = [DESTRUCTOR_FRAME_EXIT pdestructionframe, OUTPUT_FINAL_OBJECT_CV pobobjectreturn_capture, OUTPUT_DRAIN pobdrain]',
        'pobobjectreturn_source = pobobjectreturn_capture[.SOURCE = (OBJECT_THROW_BIRTH pcallcontext.FUNCTION pobctorbirth)]',
        'S_source = S_exit[.TODO = [DESTRUCTOR_FRAME_EXIT pdestructionframe, OUTPUT_FINAL_OBJECT_CV pobobjectreturn_source, OUTPUT_DRAIN pobdrain]]',
        'pobctorbirth_identity = pobctorbirth[.OBJECT = n_object]',
        'pobobjectreturn_identity = pobobjectreturn_capture[.SOURCE = (OBJECT_THROW_BIRTH porigin pobctorbirth_identity)]',
        'S_identity = S_exit[.TODO = [DESTRUCTOR_FRAME_EXIT pdestructionframe, OUTPUT_FINAL_OBJECT_CV pobobjectreturn_identity, OUTPUT_DRAIN pobdrain]]',
        'S_report_found = $drive_steps(S_exit, 1)', 'S_report_found.COMPLETION = BUDGET',
        'S_report = S_report_found[.COMPLETION = NORMAL]',
        'S_report.TODO = [OUTPUT_FINAL_PENDING pobdeactivate n_exception true]',
        'S_report.DESTRUCTION.ABANDONED = [pdestructioncleanup]',
        'S_release_found = $drive_steps(S_report, 1)', 'S_release_found.COMPLETION = BUDGET',
        'S_release = S_release_found[.COMPLETION = NORMAL]',
        'S_release.DESTRUCTION.OPERATIONS = [pdestructionoperation]',
        'S_deactivate_found = $dp_seek(S_release, 3, 512)',
        r'S_deactivate_found.COMPLETION = NORMAL \/ S_deactivate_found.COMPLETION = BUDGET',
        'S_deactivate = S_deactivate_found[.COMPLETION = NORMAL]',
        'S_done = $drive_steps(S_deactivate, 2048)',
    ]
    warning_events = '[OUTPUT ([80]), WARNING ($ptascii("missing")) 4]'
    fatal_events = '[OUTPUT ([80]), WARNING ($ptascii("missing")) 4, STDERR ' + runner.bytes_expr(expected_fatal(path)) + ']'
    components = [
        ('real method locals and pending birth', r'$object_name(S, n_object) = $ptascii("T") /\ $object_name(S, n_local) = $ptascii("D") /\ $ob_object_source_new(pobobjectreturn.SOURCE) = ((porigin, pobctorbirth)) /\ $heap_count(HOBJECT n_object, $machine_roots(S)) = 2 /\ $heap_owners($heap_graph(S), HOBJECT n_local) = 1 /\ $heap_count(HOBJECT n_exception, $machine_roots(S)) = 1'),
        ('nonowning direct-throw capture', r'pframe_capture.TODO = (STRINGIFY_RESULT n_object porigin_site 0) :: (OB_USER_OBJECT_STRING pobobjectreturn_capture) :: ptask_native* /\ $task_nodes(OB_USER_OBJECT_STRING pobobjectreturn_capture) = $task_nodes(OB_USER_OBJECT_STRING pobobjectreturn) /\ $heap_count(HOBJECT n_object, $machine_roots(S_capture)) = 2 /\ $heap_count(HOBJECT n_exception, $machine_roots(S_capture)) = 1'),
        ('exact external context and context-owner refusals', r'pcallcontext.INSTANCE = eps /\ pcallcontext.RECEIVER = (n_object) /\ $destructor_context_nodes(S_context.CURRENT) = [HOBJECT n_object] /\ $destructor_borrowed_context(S_context) = (pcallcontext) /\ $destructor_borrowed_context(S_context_extra) = eps /\ $destructor_borrowed_context(S_context_receiver) = eps'),
        ('saved consumer keeps current target pending birth and native authority', r'$ob_object_final_saved_context(S_context) = ((pcallcontext, pobobjectreturn_capture)) /\ $ob_object_final_saved_context(S_context_function) = eps /\ $ob_object_final_saved_context(S_context_target) = eps /\ $ob_object_final_saved_context(S_context_pending) = eps /\ $ob_object_final_saved_context(S_context_header) = eps /\ $ob_object_final_saved_context(S_context_source) = eps /\ $ob_object_final_saved_context(S_context_stale) = eps'),
        ('actual null caller before ordered CV release', r'S_stage.CURRENT = eps /\ S_stage.FRAMES = eps /\ S_stage.ORIGIN = eps /\ pdestructionframe.ORIGIN = eps /\ pdestructionframe.PENDING = (n_exception) /\ pdestructionframe.FUNCTION = pcallcontext.FUNCTION /\ S_stage.EVENTS = S.EVENTS /\ S_stage.OUTPUTBUFFERS = S.OUTPUTBUFFERS /\ ~(n_local <- S_stage.DESTRUCTION.CALLED)'),
        ('real receiver local and pending owners at cleanup', r'$task_nodes(OUTPUT_FINAL_OBJECT_CV pobobjectreturn_capture) = $ob_object_nodes(pobobjectreturn_capture) ++ [HOBJECT n_object] /\ $heap_count(HOBJECT n_object, $machine_roots(S_stage)) = 2 /\ $heap_owners($heap_graph(S_stage), HOBJECT n_local) = 1 /\ $heap_count(HOBJECT n_exception, $machine_roots(S_stage)) = 1 /\ ~(n_object <- S_stage.DESTRUCTION.CALLED)'),
        ('public cleanup validity', r'$call_descriptors_valid(S_stage) /\ $heap_valid($heap_graph(S_stage)) /\ $output_state_valid(S_stage) /\ $destruction_state_valid(S_stage) /\ ~$call_task_valid(S_stage[.DECLARATIONS = eps], OUTPUT_FINAL_OBJECT_CV pobobjectreturn_capture)'),
        ('zero-budget keeps actual cleanup owners', r'S_budget.COMPLETION = BUDGET /\ S_budget.TODO = S_stage.TODO /\ S_budget.DESTRUCTION = S_stage.DESTRUCTION /\ S_budget.ALLOCATIONS = S_stage.ALLOCATIONS /\ S_budget.GC = S_stage.GC /\ S_budget.EVENTS = S_stage.EVENTS'),
        ('one-budget starts local release without receiver decrement', r'S_one.OUTPUTBUFFERS = S_stage.OUTPUTBUFFERS /\ $heap_count(HOBJECT n_object, $machine_roots(S_one)) = 2 /\ $heap_count(HOBJECT n_exception, $machine_roots(S_one)) = 1 /\ ~(n_object <- S_one.DESTRUCTION.CALLED)'),
        ('genuine local destructor uses a null native caller', r'pdestructorcall_local.OBJECT = n_local /\ ~pdestructorcall_local.USER /\ pdestructorcall_local.CALLER = eps /\ pdestructorcall_local.ORIGIN = eps /\ pdestructorcall_local.SITE = eps /\ pcallcontext_local.CALLSITE = eps /\ pcallcontext_local.LINE = $(-1) /\ pcallcontext_local.RECEIVER = (n_local) /\ ptraceframe_local.FILE = eps /\ ptraceframe_local.LINE = $(-1) /\ ptraceframe_local.FUNCTION = $ptascii("__destruct") /\ ptraceframe_local.CLASS = ($ptascii("D")) /\ $heap_count(HOBJECT n_object, $machine_roots(S_entered)) = 2 /\ $heap_count(HOBJECT n_exception, $machine_roots(S_entered)) = 1'),
        ('warning precedes actual frame exit', 'S_exit.EVENTS = ' + warning_events + r' /\ n_unit = 0 /\ $call_sourcefile(S_exit.FILES, porigin) = ' + runner.bytes_expr(os.fsencode(path)) + r' /\ ~((HOBJECT n_local) <- S_exit.ALLOCATIONS) /\ n_local <- S_exit.DESTRUCTION.CALLED /\ S_exit.OUTPUTBUFFERS = S.OUTPUTBUFFERS /\ $heap_count(HOBJECT n_object, $machine_roots(S_exit)) = 2 /\ $heap_count(HOBJECT n_exception, $machine_roots(S_exit)) = 1'),
        ('genuine post-cleanup null-C report admission', r'$ob_object_final_cv_ready(S_exit, pobobjectreturn_capture, pdestructionframe, n_exception) /\ $call_descriptors_valid(S_exit) /\ $heap_valid($heap_graph(S_exit)) /\ $destruction_state_valid(S_exit)'),
        ('source identity and native-frame refusals', r'~$ob_object_final_cv_ready(S_source, pobobjectreturn_source, pdestructionframe, n_exception) /\ ~$ob_object_final_cv_ready(S_identity, pobobjectreturn_identity, pdestructionframe, n_exception) /\ ~$ob_object_final_cv_ready(S_exit[.FRAMES = [pframe]], pobobjectreturn_capture, pdestructionframe, n_exception) /\ ~$ob_object_final_cv_ready(S_exit[.EXCEPTIONHANDLER = (PSTRING $ptascii("h"))], pobobjectreturn_capture, pdestructionframe, n_exception)'),
        ('exact warning then internal fatal without receiver destructor', 'S_report.EVENTS = ' + fatal_events + r' /\ pobdeactivate.COMPLETION = REQUESTFATAL ($ptascii("Exception")) ($ptascii("E")) 9 /\ S_report.EXITSTATUS = 255 /\ S_report.DESTRUCTION.FRAMES = eps /\ $heap_count(HOBJECT n_object, $machine_roots(S_report)) = 2 /\ $heap_count(HOBJECT n_exception, $machine_roots(S_report)) = 1'),
        ('registered receipt owns only actual receiver pair', r'$eager_cleanup_valid(S_report, pdestructioncleanup) /\ $task_nodes(pdestructioncleanup.SOURCE) = eps /\ ~$call_task_valid(S_report, pdestructioncleanup.SOURCE) /\ $eager_abandoned_owner(pdestructioncleanup.SOURCE) = [HOBJECT n_object, HOBJECT n_object] /\ $call_descriptors_valid(S_report) /\ $heap_valid($heap_graph(S_report)) /\ $output_state_valid(S_report) /\ $destruction_state_valid(S_report)'),
        ('ordinary Throwable release keeps receiver owners', r'pdestructionoperation.SOURCE = OUTPUT_FINAL_PENDING pobdeactivate n_exception true /\ S_release.OUTPUTBUFFERS = S_report.OUTPUTBUFFERS /\ $heap_count(HOBJECT n_object, $machine_roots(S_release)) = 2'),
        ('retired Throwable cannot remain a borrowed owner', r'~((HOBJECT n_exception) <- S_deactivate.ALLOCATIONS) /\ $eager_cleanup_valid(S_deactivate, pdestructioncleanup) /\ $heap_count(HOBJECT n_exception, $machine_roots(S_deactivate)) = 0 /\ $heap_count(HOBJECT n_object, $machine_roots(S_deactivate)) = 2 /\ S_deactivate.EVENTS = S_report.EVENTS'),
        ('full fatal endpoint preserves abandoned cast pair', r'S_done.COMPLETION = pobdeactivate.COMPLETION /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.OUTPUTBUFFERS = eps /\ S_done.EXITSTATUS = 255 /\ S_done.EVENTS = S_report.EVENTS /\ S_done.DESTRUCTION.ABANDONED = [pdestructioncleanup] /\ $eager_cleanup_valid(S_done, pdestructioncleanup) /\ $heap_count(HOBJECT n_object, $machine_roots(S_done)) = 2 /\ $heap_count(HOBJECT n_exception, $machine_roots(S_done)) = 0'),
    ]
    bindings += [
        'S_control_initial = $php_file_run(' + finally_fixture + ', 0, ' + runner.bytes_expr(os.fsencode(finally_path)) + ', ' + runner.bytes_expr(os.fsencode(finally_path.parent)) + ')',
        'S_control_initial.COMPLETION = BUDGET',
        'S_control_found = $dp_seek(S_control_initial, 0, 1024)',
        r'S_control_found.COMPLETION = NORMAL \/ S_control_found.COMPLETION = BUDGET',
        'S_control = S_control_found[.COMPLETION = NORMAL]',
        'S_control.TODO = (THROW_VALUE porigin_control_throw z_control) :: ptask_control_tail*',
        'porigin_control_throw = PORIGIN n_unit_control pcpath_control_throw',
        'S_control.RESULT = KNOWN (POBJECT n_control_exception)',
        'S_control.CURRENT = (pcallcontext_control)',
        'S_control_capture_found = $drive_steps(S_control, 1)',
        'S_control_capture_found.COMPLETION = BUDGET',
        'S_control_capture = S_control_capture_found[.COMPLETION = NORMAL]',
        'S_control_capture.FRAMES = [pframe_control]',
        'pframe_control.TODO = (STRINGIFY_RESULT n_control_object porigin_control 0) :: (OB_USER_OBJECT_STRING pobobjectreturn_control_capture) :: ptask_control*',
        'S_return_found = $dp_seek(S_control_capture, 9, 512)',
        r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
        'S_return = S_return_found[.COMPLETION = NORMAL]',
        'S_normal_found = $drive_steps(S_return, 1)', 'S_normal_found.COMPLETION = BUDGET',
        'S_normal = S_normal_found[.COMPLETION = NORMAL]',
        'S_normal.DESTRUCTION.FRAMES = [pdestructionframe_normal]',
        'pdestructionframe_normal.VALUE = KNOWN pvalue_normal',
        '$cl_normal_cleanup(S_normal.TODO, pdestructionframe_normal) = (pobobjectreturn_normal)',
    ]
    components += [
        ('actual finally override follows captured throw', r'$ob_object_source_pending(pobobjectreturn_control_capture.SOURCE) = ((porigin_control_throw, n_control_exception)) /\ pdestructionframe_normal.FUNCTION = pcallcontext_control.FUNCTION /\ pdestructionframe_normal.PENDING = eps /\ $string_bytes(pvalue_normal) = ($ptascii("H"))'),
        ('normal restore clears borrowed freshness before local cleanup', r'pobobjectreturn_normal.SOURCE = eps /\ S_normal.CURRENT = eps /\ S_normal.FRAMES = eps /\ $heap_count(HOBJECT n_control_exception, $machine_roots(S_normal)) = 0 /\ ~((HOBJECT n_control_exception) <- S_normal.ALLOCATIONS) /\ $call_descriptors_valid(S_normal) /\ $heap_valid($heap_graph(S_normal))'),
    ]
    return bindings, components


def empty_assertions(fixture, directory, path):
    name = os.fsencode(path)
    fatal = (b'Fatal error: Uncaught Exception: E in ' + name + b':6\nStack trace:\n'
             b'#0 [internal function]: T->__toString()\n#1 {main}\n  thrown in ' + name + b' on line 6\n')
    bindings = [
        'S_initial = $php_file_run(' + fixture + ', 0, ' + runner.bytes_expr(name) + ', ' + runner.bytes_expr(os.fsencode(directory)) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $dp_seek(S_initial, 0, 1024)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]',
        'S.CURRENT = (pcallcontext)', 'S.FRAMES = [pframe]',
        'pframe.TODO = (STRINGIFY_RESULT n_object porigin_site 0) :: (OB_USER_OBJECT_STRING pobobjectreturn) :: ptask_native*',
        'pobobjectreturn.INVOKE.CALL = OB_FINAL pobdrain',
        'S.RESULT = KNOWN (POBJECT n_exception)',
        'S_capture_found = $drive_steps(S, 1)', 'S_capture_found.COMPLETION = BUDGET',
        'S_capture = S_capture_found[.COMPLETION = NORMAL]',
        'S_context_found = $dp_seek(S_capture, 5, 256)',
        r'S_context_found.COMPLETION = NORMAL \/ S_context_found.COMPLETION = BUDGET',
        'S_context = S_context_found[.COMPLETION = NORMAL]',
        'S_stage_found = $drive_steps(S_context, 1)', 'S_stage_found.COMPLETION = BUDGET',
        'S_stage = S_stage_found[.COMPLETION = NORMAL]',
        'S_stage.DESTRUCTION.FRAMES = [pdestructionframe]',
        'S_stage.TODO = [DESTRUCTOR_RELEASE pdestructionrelease, DESTRUCTOR_FRAME_EXIT pdestructionframe, OUTPUT_FINAL_OBJECT_CV pobobjectreturn_capture, OUTPUT_DRAIN pobdrain]',
        'S_budget = $drive_steps(S_stage, 0)',
        'S_exit_found = $drive_steps(S_budget[.COMPLETION = NORMAL], 1)', 'S_exit_found.COMPLETION = BUDGET',
        'S_exit = S_exit_found[.COMPLETION = NORMAL]',
        'S_report_found = $drive_steps(S_exit, 1)', 'S_report_found.COMPLETION = BUDGET',
        'S_report = S_report_found[.COMPLETION = NORMAL]',
        'S_report.TODO = [OUTPUT_FINAL_PENDING pobdeactivate n_exception true]',
        'S_report.DESTRUCTION.ABANDONED = [pdestructioncleanup]',
    ]
    components = [
        ('actual unused CV without a destructor class', r'S_context.CVS = [$ptascii("unused")] /\ S_context.ENV = eps /\ ~$destructor_classes(S_context.CLASSES) /\ $destructor_native_cv_cleanup(S_context) /\ $destructor_frame_nodes(S_context) = eps /\ $destructor_frame_staged(S_context)'),
        ('real empty-job native barrier and owners', r'pdestructionrelease.JOBS = eps /\ ~pdestructionrelease.USER /\ S_stage.CURRENT = eps /\ S_stage.ORIGIN = eps /\ pdestructionframe.PENDING = (n_exception) /\ pdestructionframe.ORIGIN = eps /\ $heap_count(HOBJECT n_object, $machine_roots(S_stage)) = 2 /\ $heap_count(HOBJECT n_exception, $machine_roots(S_stage)) = 1 /\ $call_descriptors_valid(S_stage) /\ $heap_valid($heap_graph(S_stage)) /\ $destruction_state_valid(S_stage) /\ S_budget.TODO = S_stage.TODO /\ S_exit.TODO = [DESTRUCTOR_FRAME_EXIT pdestructionframe, OUTPUT_FINAL_OBJECT_CV pobobjectreturn_capture, OUTPUT_DRAIN pobdrain]'),
        ('actual null-C report follows the empty barrier', 'S_report.EVENTS = [OUTPUT ([80]), STDERR ' + runner.bytes_expr(fatal) + r'] /\ pobdeactivate.COMPLETION = REQUESTFATAL ($ptascii("Exception")) ($ptascii("E")) 6 /\ S_report.EXITSTATUS = 255 /\ $eager_cleanup_valid(S_report, pdestructioncleanup) /\ $heap_count(HOBJECT n_object, $machine_roots(S_report)) = 2 /\ $heap_count(HOBJECT n_exception, $machine_roots(S_report)) = 1'),
    ]
    return bindings, components


def caught_assertions(fixture, directory, path):
    bindings = [
        'S_initial = $php_file_run(' + fixture + ', 0, ' + runner.bytes_expr(os.fsencode(path)) + ', ' + runner.bytes_expr(os.fsencode(directory)) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $dp_seek(S_initial, 0, 1024)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]',
        'S.TODO = (THROW_VALUE porigin z) :: ptask_tail*',
        'S.CURRENT = (pcallcontext)', 'S.RESULT = KNOWN (POBJECT n_exception)',
        'S_capture_found = $drive_steps(S, 1)', 'S_capture_found.COMPLETION = BUDGET',
        'S_capture = S_capture_found[.COMPLETION = NORMAL]',
        'S_capture.FRAMES = [pframe_capture]',
        'pframe_capture.TODO = (STRINGIFY_RESULT n_object porigin_site 0) :: (OB_USER_OBJECT_STRING pobobjectreturn_capture) :: ptask_native*',
        'S_catch_found = $dp_seek(S_capture, 7, 256)',
        r'S_catch_found.COMPLETION = NORMAL \/ S_catch_found.COMPLETION = BUDGET',
        'S_catch = S_catch_found[.COMPLETION = NORMAL]',
        'S_catch.CURRENT = (pcallcontext)', 'S_catch.FRAMES = [pframe_catch]',
        'S_catch.TODO = (CATCH_BIND porigin_try n_index n_exception) :: ptask_catch*',
        'pframe_catch.TODO = (STRINGIFY_RESULT n_object porigin_site 0) :: (OB_USER_OBJECT_STRING pobobjectreturn_catch) :: ptask_native*',
    ]
    components = [
        ('real fresh-throw capture before catch consumption', r'$ob_object_source_pending(pobobjectreturn_capture.SOURCE) = ((porigin, n_exception)) /\ $heap_count(HOBJECT n_exception, $machine_roots(S_capture)) = 1 /\ $heap_count(HOBJECT n_object, $machine_roots(S_capture)) = 2'),
        ('actual catch clears borrowed identity while retaining its Throwable', r'pobobjectreturn_catch = pobobjectreturn_capture[.SOURCE = eps] /\ $task_nodes(CATCH_BIND porigin_try n_index n_exception) = [HOBJECT n_exception] /\ $heap_count(HOBJECT n_exception, $machine_roots(S_catch)) = 1 /\ $heap_count(HOBJECT n_object, $machine_roots(S_catch)) = 2 /\ (HOBJECT n_exception) <- S_catch.ALLOCATIONS /\ $call_task_valid(S_catch, CATCH_BIND porigin_try n_index n_exception) /\ S_catch.EVENTS = [OUTPUT ([80])]'),
    ]
    return bindings, components


def unstaged_assertions(fixture, directory, path):
    bindings = [
        'S_initial = $php_file_run(' + fixture + ', 0, ' + runner.bytes_expr(os.fsencode(path)) + ', ' + runner.bytes_expr(os.fsencode(directory)) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $dp_seek(S_initial, 0, 1024)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]',
        'S.TODO = (THROW_VALUE porigin z) :: ptask_tail*',
        'S.RESULT = KNOWN (POBJECT n_exception)',
        'S_capture_found = $drive_steps(S, 1)', 'S_capture_found.COMPLETION = BUDGET',
        'S_capture = S_capture_found[.COMPLETION = NORMAL]',
        'S_capture.FRAMES = [pframe_capture]',
        'pframe_capture.TODO = (STRINGIFY_RESULT n_object porigin_site 0) :: (OB_USER_OBJECT_STRING pobobjectreturn_capture) :: ptask_native*',
        'S_return_found = $dp_seek(S_capture, 9, 512)',
        r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
        'S_return = S_return_found[.COMPLETION = NORMAL]',
        'S_return.TODO = [RETURN_UNWIND (KNOWN pvalue_return) porigin_return?]',
        'S_normal_found = $drive_steps(S_return, 1)', 'S_normal_found.COMPLETION = BUDGET',
        'S_normal = S_normal_found[.COMPLETION = NORMAL]',
        'S_normal.TODO = (OB_USER_OBJECT_RETURN pobobjectreturn_normal poperand_normal) :: ptask_normal*',
        'ptask_normal* = pobobjectreturn_normal.TAIL',
    ]
    components = [
        ('actual fresh throw reaches a real finally H override', r'$ob_object_source_pending(pobobjectreturn_capture.SOURCE) = ((porigin,n_exception)) /\ $string_bytes(pvalue_return) = ($ptascii("H")) /\ ~$destructor_classes(S_return.CLASSES) /\ S_return.ENV = eps'),
        ('unstaged native return clears retired borrowed identity', r'S_normal.CURRENT = eps /\ S_normal.FRAMES = eps /\ S_normal.DESTRUCTION.FRAMES = eps /\ poperand_normal = KNOWN pvalue_return /\ pobobjectreturn_normal = pobobjectreturn_capture[.SOURCE = eps][.RETURNED = (poperand_normal)] /\ $heap_count(HOBJECT n_exception,$machine_roots(S_normal)) = 0 /\ ~((HOBJECT n_exception) <- S_normal.ALLOCATIONS) /\ S_normal.RESULT = KNOWN PNULL /\ S_normal.EVENTS = [OUTPUT ([80])]'),
    ]
    return bindings, components


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    out = args.output or Path(tempfile.mkdtemp(prefix='output-final-cast-locals-review-', dir=ROOT / '.tools'))
    out.mkdir(parents=True, exist_ok=True)
    report = {'revision': support.subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD']).decode().strip(),
              'before': fingerprint(), 'profile': support.common.PROFILE,
              'source_case': 'fresh-throw-local-warning',
              'model_only_controls': ['finally-return', 'unused-cv', 'catch-consumption', 'unstaged-finally-return'],
              'records': [], 'passed': False, 'completed': False}
    print(out, flush=True)
    stage = 'native'
    stage_directory = out
    try:
        path = out / 'source.php'; path.write_bytes(SOURCE)
        native = support.common.run([str(ROOT / '.tools/php/bin/php'), '-n', *support.common.FLAGS, str(path)], out, 'native', 10)
        assert native.returncode == 255 and native.stdout == b'P'
        assert native.stderr == expected_warning(path) + expected_fatal(path)
        finally_path = out / 'finally.php'; finally_path.write_bytes(FINALLY_SOURCE)
        empty_path = out / 'empty.php'; empty_path.write_bytes(EMPTY_SOURCE)
        caught_path = out / 'caught.php'; caught_path.write_bytes(CAUGHT_SOURCE)
        unstaged_path = out / 'unstaged.php'; unstaged_path.write_bytes(UNSTAGED_SOURCE)
        frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d', 'extension=' + str(ROOT / '.tools/php-file.so'),
                           str(ROOT / 'frontend/worker.php')], out / 'frontend')
        try:
            parsed = frontend.request({'op': 'parse', 'source': support.base64.b64encode(SOURCE).decode()})
            finally_parsed = frontend.request({'op': 'parse', 'source': support.base64.b64encode(FINALLY_SOURCE).decode()})
            empty_parsed = frontend.request({'op': 'parse', 'source': support.base64.b64encode(EMPTY_SOURCE).decode()})
            caught_parsed = frontend.request({'op': 'parse', 'source': support.base64.b64encode(CAUGHT_SOURCE).decode()})
            unstaged_parsed = frontend.request({'op': 'parse', 'source': support.base64.b64encode(UNSTAGED_SOURCE).decode()})
        finally:
            frontend.close()
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        try:
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            finally_checked = adapter.request({'op': 'check', 'ast': finally_parsed['ast'], 'fixture': True})
            empty_checked = adapter.request({'op': 'check', 'ast': empty_parsed['ast'], 'fixture': True})
            caught_checked = adapter.request({'op': 'check', 'ast': caught_parsed['ast'], 'fixture': True})
            unstaged_checked = adapter.request({'op': 'check', 'ast': unstaged_parsed['ast'], 'fixture': True})
        finally:
            adapter.close()
        bindings, components = assertions(checked['fixture'], out, path, finally_checked['fixture'], finally_path)
        report.update(source_sha256=support.common.sha(path), finally_source_sha256=support.common.sha(finally_path),
                      empty_source_sha256=support.common.sha(empty_path), model_only_native_agreement_credit=0,
                      caught_source_sha256=support.common.sha(caught_path),
                      unstaged_source_sha256=support.common.sha(unstaged_path),
                      native_agreement_credit=0)
        modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
        binding_cut = next(index for index, binding in enumerate(bindings) if binding.startswith('S_control_initial ='))
        component_cut = next(index for index, (name, _) in enumerate(components) if name == 'actual finally override follows captured throw')
        selections = [('primary', bindings[:binding_cut], components[:component_cut]),
                      ('finally-return', bindings[binding_cut:], components[component_cut:])]
        selections.append(('unused-cv', *empty_assertions(empty_checked['fixture'], out, empty_path)))
        selections.append(('catch-consumption', *caught_assertions(caught_checked['fixture'], out, caught_path)))
        selections.append(('unstaged-finally-return', *unstaged_assertions(unstaged_checked['fixture'], out, unstaged_path)))
        for name, selected_bindings, selected_components in selections:
            stage_directory = out / name; stage_directory.mkdir()
            fixture = stage_directory / 'state.watsup'
            fixture.write_text(PREFIX + '\ndec $main() : bool*\ndef $main() = [' +
                               ', '.join('(' + check + ')' for _, check in selected_components) + ']\n' +
                               ''.join('  -- if ' + binding + '\n' for binding in selected_bindings))
            record = {'case': name, 'binding_premises': len(selected_bindings),
                      'components': [label for label, _ in selected_components],
                      'fixture_sha256': support.common.sha(fixture), 'passed': False}
            report['records'].append(record)
            stage = 'state'
            result = support.common.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
                                         *[str(ROOT / module) for module in modules], str(fixture)], stage_directory, 'state', 300)
            rendered = result.stdout.decode('ascii')
            values = re.findall(r'\b(?:true|false)\b', rendered)
            assert not re.sub(r'true|false|[\[\](),;\s]', '', rendered), rendered
            record['component_results'] = dict(zip(record['components'], [value == 'true' for value in values]))
            assert result.returncode == 0 and not result.stderr and values == ['true'] * len(selected_components), (result.returncode, result.stdout, result.stderr)
            record['passed'] = True
            print(name, True, flush=True)
        report.update(passed=True, completed=True)
    except BaseException as error:
        if isinstance(error, support.subprocess.TimeoutExpired):
            (stage_directory / (stage + '.stdout')).write_bytes(error.stdout or b'')
            (stage_directory / (stage + '.stderr')).write_bytes(error.stderr or b'')
            (stage_directory / (stage + '.timeout')).write_text(str(error.timeout) + '\n')
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        report['after'] = fingerprint()
        report['passed'] = report['passed'] and report['before'] == report['after']
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(out / 'report.json', report['passed'], flush=True)
    assert report['passed'] and report['completed']


if __name__ == '__main__':
    main()
