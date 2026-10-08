#!/usr/bin/env python3
"""Reached throwing renderer-handler report, release and parent abandonment."""
import os

import generator_request_abrupt_protocol as fatal
import generator_request_render_handler_throw_peer_sources as peer
from reference_yield_protocol import valid, reject

base = fatal.base
driver = fatal.driver
SELECTED = {
    'request-render-handler-throws': peer.UNSUPPORTED['peer-request-render-handler-throws'],
    'request-render-handler-throw-release': peer.UNSUPPORTED['peer-request-render-handler-throw-release-before-bailout'],
}
CASES = {name: (row[0], row[1], row[3]) for name, row in SELECTED.items()}
PREFIX = r'''
def $request_finally_phase(S,500) = true
  -- if S.TODO = (THROW_SEARCH n) :: (EXCEPTION_HANDLER_RESULT pexceptioncall) :: (GENERATOR_REQUEST_RENDER_RETURN pgenfatal n_old false) :: (GENERATOR_REQUEST_REPORT pgenfatal) :: ptask_tail*
def $request_finally_phase(S,501) = true
  -- if S.TODO = (GENERATOR_REQUEST_REPORT pgenfatal_new) :: (EXCEPTION_HANDLER_RESULT pexceptioncall) :: (GENERATOR_REQUEST_RENDER_RETURN pgenfatal_parent n_old false) :: (GENERATOR_REQUEST_REPORT pgenfatal_parent) :: ptask_tail*
  -- if pgenfatal_new.METHOD = eps
def $request_finally_phase(S,502) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.RECEIVER = (n)
  -- if $object_name(S,n) <- [$ptascii("RenderHandlerAbort"),$ptascii("RenderHandlerRelease")]
  -- if $trace_context_function(S,pcallcontext) = $ptascii("__toString")
def $request_finally_phase(S,503) = true
  -- if $request_finally_phase(S,502)
  -- if S.RESULT = KNOWN (POBJECT n)
  -- if S.OBJECTS[n] = GENERATOR pgenerator
def $request_finally_phase(S,504) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.RECEIVER = (n)
  -- if $object_name(S,n) = $ptascii("RenderHandlerRelease")
  -- if $trace_context_function(S,pcallcontext) = $ptascii("__destruct")
def $request_finally_phase(S,505) = ($request_finally_phase(S,504) /\ S.REPORTING = 0)
def $request_finally_phase(S,506) = true
  -- if S.TODO = (GENERATOR_REQUEST_BAILOUT pgenfatal_new) :: (EXCEPTION_HANDLER_RESULT pexceptioncall) :: (GENERATOR_REQUEST_RENDER_RETURN pgenfatal_parent n_old false) :: (GENERATOR_REQUEST_REPORT pgenfatal_parent) :: ptask_tail*
'''


def assertions(checked, path, directory, name):
    initial = ('$php_file_run(' + checked['fixture'] + ',0,'
               + driver.driver.byte_expr(os.fsencode(path)) + ','
               + driver.driver.byte_expr(os.fsencode(driver.ROOT)) + ')')
    release = name == 'request-render-handler-throw-release'
    checks = ['S_initial = ' + initial, '~S_initial.COMPILESTOP']
    checks += base.seek('S_abrupt', 'S_initial', 500) + fatal.normal_valid('S_abrupt')
    checks += fatal.lines(r'''
S_abrupt.TODO = (THROW_SEARCH n_new) :: (EXCEPTION_HANDLER_RESULT pexceptioncall) :: (GENERATOR_REQUEST_RENDER_RETURN pgenfatal_parent n_old false) :: (GENERATOR_REQUEST_REPORT pgenfatal_parent) :: ptask_parent_tail*
S_abrupt.CURRENT = eps /\ S_abrupt.FRAMES = eps /\ S_abrupt.ORIGIN = eps
S_abrupt.EXCEPTIONHANDLER = eps
S_abrupt.EXCEPTIONHANDLERS = (pexceptioncall.CALLBACK) :: (pvalue?)*
pexceptioncall.OBJECT = n_old /\ pexceptioncall.ORIGIN = pgenfatal_parent.METHOD
$exception_result_valid(S_abrupt,pexceptioncall)
$generator_request_render_handler_abrupt(S_abrupt)
$shutdown_render_throw_pending(S_abrupt)
pgenfatal_parent.METHOD = (porigin_parent)
pgenfatal_parent.SOURCE = GENERATOR_CLOSE_DONE pgenclose_original
pgenclose_original.PENDING = (pgenfatal_parent.OBJECT)
ptask_parent_tail* = (GENERATOR_CLOSE_DONE pgenclose) :: ptask_finish*
pgenclose = pgenclose_original[.PENDING = eps]
n_parent = pgenfatal_parent.OBJECT
n_new =/= n_old /\ n_new =/= n_parent
$generator_close_claims(ptask_parent_tail*) = [n_generator]
S_abrupt.OBJECTS[n_generator] = GENERATOR pgenerator
pgenerator.PHASE = GENERATOR_CLOSED /\ pgenerator.FRAME = eps
pgenerator.VALUE = (POBJECT n_payload)
$heap_owners($heap_graph(S_abrupt),HOBJECT n_new) = 1
$heap_owners($heap_graph(S_abrupt),HOBJECT n_old) = 2
$heap_owners($heap_graph(S_abrupt),HOBJECT n_parent) = 1
$heap_owners($heap_graph(S_abrupt),HOBJECT n_generator) = 1
$heap_owners($heap_graph(S_abrupt),HOBJECT n_payload) = 1
$throwable_field(S_abrupt,n_new,"previous") = PNULL
$throwable_field(S_abrupt,n_new,"trace") = PARRAY n_trace
$entry_lookup(S_abrupt.ARRAYS[n_trace].ITEMS,KINT 0) = (DIRECT (PARRAY n_trace_frame))
$entry_lookup(S_abrupt.ARRAYS[n_trace_frame].ITEMS,KSTRING $ptascii("file")) = eps
$entry_lookup(S_abrupt.ARRAYS[n_trace_frame].ITEMS,KSTRING $ptascii("line")) = eps
$entry_lookup(S_abrupt.ARRAYS[n_trace_frame].ITEMS,KSTRING $ptascii("args")) = (DIRECT (PARRAY n_trace_args))
$entry_lookup(S_abrupt.ARRAYS[n_trace_args].ITEMS,KINT 0) = (DIRECT (POBJECT n_old))
$generator_request_fatal_selected(S_abrupt) = (pgenfatal_new)
pgenfatal_new.SOURCE = THROW_SEARCH n_new
pgenfatal_new.OBJECT = n_new /\ pgenfatal_new.METHOD = eps
pgenfatal_new.HANDLERS = S_abrupt.EXCEPTIONHANDLERS
$request_fatal_stderr(S_abrupt.EVENTS) = eps
''')
    if not release:
        checks += fatal.lines(r'''
pexceptioncall_wrong = pexceptioncall[.ORIGIN = eps]
S_wrong_handler_origin = S_abrupt[.TODO = (THROW_SEARCH n_new) :: (EXCEPTION_HANDLER_RESULT pexceptioncall_wrong) :: (GENERATOR_REQUEST_RENDER_RETURN pgenfatal_parent n_old false) :: (GENERATOR_REQUEST_REPORT pgenfatal_parent) :: ptask_parent_tail*]
$exception_result_valid(S_wrong_handler_origin,pexceptioncall_wrong)
~$generator_request_render_handler_abrupt(S_wrong_handler_origin)
$generator_request_fatal_selected(S_wrong_handler_origin) = eps
''')
        reject(checks, 'handler_origin', 'S_wrong_handler_origin', 'S_abrupt')
    checks += base.seek('S_report', 'S_abrupt', 501) + fatal.normal_valid('S_report')
    checks += fatal.lines(r'''
S_report.TODO = (GENERATOR_REQUEST_REPORT pgenfatal_new) :: (EXCEPTION_HANDLER_RESULT pexceptioncall) :: (GENERATOR_REQUEST_RENDER_RETURN pgenfatal_parent n_old false) :: (GENERATOR_REQUEST_REPORT pgenfatal_parent) :: ptask_parent_tail*
$generator_request_report_valid(S_report,pgenfatal_new)
$task_nodes(GENERATOR_REQUEST_REPORT pgenfatal_new) = [HOBJECT n_new]
$task_nodes(GENERATOR_REQUEST_RENDER_RETURN pgenfatal_parent n_old false) = eps
$generator_request_render_at(S_report.TODO) = ((pgenfatal_parent,n_old,false,ptask_parent_tail*))
$generator_request_render_return_valid(S_report,pgenfatal_parent,n_old,false)
$generator_request_report_valid(S_report,pgenfatal_parent)
S_parent_future = $call_after_origin(S_report,GENERATOR_REQUEST_REPORT pgenfatal_new)
$call_tasks_valid(S_parent_future,(EXCEPTION_HANDLER_RESULT pexceptioncall) :: (GENERATOR_REQUEST_RENDER_RETURN pgenfatal_parent n_old false) :: (GENERATOR_REQUEST_REPORT pgenfatal_parent) :: ptask_parent_tail*)
$heap_owners($heap_graph(S_report),HOBJECT n_new) = 1
$heap_owners($heap_graph(S_report),HOBJECT n_old) = 2
$heap_owners($heap_graph(S_report),HOBJECT n_parent) = 1
$heap_owners($heap_graph(S_report),HOBJECT n_generator) = 1
$heap_owners($heap_graph(S_report),HOBJECT n_payload) = 1
$request_fatal_stderr(S_report.EVENTS) = eps
''')
    if not release:
        reject(checks, 'report_source', 'S_report[.TODO = (GENERATOR_REQUEST_REPORT pgenfatal_new[.SOURCE = THROW_SEARCH n_old]) :: (EXCEPTION_HANDLER_RESULT pexceptioncall) :: (GENERATOR_REQUEST_RENDER_RETURN pgenfatal_parent n_old false) :: (GENERATOR_REQUEST_REPORT pgenfatal_parent) :: ptask_parent_tail*]', 'S_report')
    checks += base.seek('S_renderer', 'S_report', 502) + fatal.normal_valid('S_renderer')
    checks += fatal.lines(r'''
S_renderer.CURRENT = (pcallcontext_renderer)
pcallcontext_renderer.RECEIVER = (n_new)
S_renderer.FRAMES = pframe_renderer :: pframe_renderer_tail*
pframe_renderer.TODO = (STRINGIFY_RESULT n_new porigin_new 0) :: (GENERATOR_REQUEST_REPORT pgenfatal_render) :: (EXCEPTION_HANDLER_RESULT pexceptioncall) :: (GENERATOR_REQUEST_RENDER_RETURN pgenfatal_parent n_old false) :: (GENERATOR_REQUEST_REPORT pgenfatal_parent) :: ptask_parent_tail*
pgenfatal_render = pgenfatal_new[.METHOD = (porigin_new)]
$terminal_string_frame_match(S_renderer,S_renderer.CURRENT,pframe_renderer,porigin_new)
$call_context_roots(S_renderer.CURRENT) = [HOBJECT n_new]
$task_nodes(STRINGIFY_RESULT n_new porigin_new 0) = [HOBJECT n_new]
$task_nodes(GENERATOR_REQUEST_REPORT pgenfatal_render) = [HOBJECT n_new]
$heap_owners($heap_graph(S_renderer),HOBJECT n_new) = 3
$heap_owners($heap_graph(S_renderer),HOBJECT n_old) = 2
$heap_owners($heap_graph(S_renderer),HOBJECT n_parent) = 1
$heap_owners($heap_graph(S_renderer),HOBJECT n_generator) = 1
$heap_owners($heap_graph(S_renderer),HOBJECT n_payload) = 1
$request_fatal_stderr(S_renderer.EVENTS) = eps
''')
    checks += base.seek('S_lookup', 'S_renderer', 503) + fatal.normal_valid('S_lookup')
    checks += fatal.lines(r'''
S_lookup.RESULT = KNOWN (POBJECT n_generator)
$heap_owners($heap_graph(S_lookup),HOBJECT n_generator) = 2
$heap_owners($heap_graph(S_lookup[.RESULT = KNOWN PNULL]),HOBJECT n_generator) = 1
$heap_owners($heap_graph(S_lookup),HOBJECT n_parent) = 1
$heap_owners($heap_graph(S_lookup),HOBJECT n_old) = 2
''')
    previous = 'S_lookup'
    if release:
        checks += base.seek('S_release', previous, 504) + fatal.normal_valid('S_release')
        checks += fatal.lines(r'''
S_release.CURRENT = (pcallcontext_release)
pcallcontext_release.RECEIVER = (n_new)
S_release.FRAMES = pframe_release :: pframe_release_tail*
pframe_release.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: ptask_release_tail*
pdestructorcall.OBJECT = n_new
~pdestructorcall.USER /\ pdestructorcall.CALLER = eps /\ pdestructorcall.ORIGIN = eps
pdestructorcall.FRAME = eps /\ pdestructorcall.OPERATION = eps
$generator_request_bailout_at(ptask_release_tail*) = (pgenfatal_releasing)
pgenfatal_releasing.OBJECT = n_new /\ pgenfatal_releasing.SOURCE = THROW_SEARCH n_new
$heap_owners($heap_graph(S_release),HOBJECT n_new) = 2
$heap_owners($heap_graph(S_release),HOBJECT n_old) = 2
$heap_owners($heap_graph(S_release),HOBJECT n_parent) = 1
$heap_owners($heap_graph(S_release),HOBJECT n_generator) = 1
$heap_owners($heap_graph(S_release),HOBJECT n_payload) = 1
ptbytes_reported = $request_fatal_stderr(S_release.EVENTS)
ptbytes_reported =/= eps
''')
        checks += base.seek('S_masked', 'S_release', 505) + fatal.normal_valid('S_masked')
        checks += ['S_masked.REPORTING = 0',
                   '$request_fatal_stderr(S_masked.EVENTS) = ptbytes_reported']
        previous = 'S_masked'
    checks += base.seek('S_bailout', previous, 506) + fatal.normal_valid('S_bailout')
    checks += fatal.lines(r'''
S_bailout.TODO = (GENERATOR_REQUEST_BAILOUT pgenfatal_bailout) :: (EXCEPTION_HANDLER_RESULT pexceptioncall) :: (GENERATOR_REQUEST_RENDER_RETURN pgenfatal_parent n_old false) :: (GENERATOR_REQUEST_REPORT pgenfatal_parent) :: ptask_parent_tail*
pgenfatal_bailout.OBJECT = n_new /\ pgenfatal_bailout.SOURCE = THROW_SEARCH n_new
pgenfatal_bailout.METHOD = (porigin_new)
$generator_request_bailout_valid(S_bailout,pgenfatal_bailout)
$task_nodes(GENERATOR_REQUEST_BAILOUT pgenfatal_bailout) = eps
~((HOBJECT n_new) <- S_bailout.ALLOCATIONS)
~((HARRAY n_trace) <- S_bailout.ALLOCATIONS)
~((HARRAY n_trace_args) <- S_bailout.ALLOCATIONS)
$heap_owners($heap_graph(S_bailout),HOBJECT n_new) = 0
$heap_owners($heap_graph(S_bailout),HOBJECT n_old) = 1
$heap_owners($heap_graph(S_bailout),HOBJECT n_parent) = 1
$heap_owners($heap_graph(S_bailout),HOBJECT n_generator) = 1
$heap_owners($heap_graph(S_bailout),HOBJECT n_payload) = 1
$throwable_field(S_bailout,n_parent,"string") = PSTRING eps
$request_fatal_stderr(S_bailout.EVENTS) =/= eps
S_bailout_future = $call_after_origin(S_bailout,GENERATOR_REQUEST_BAILOUT pgenfatal_bailout)
S_bailout_future.TODO = (EXCEPTION_HANDLER_RESULT pexceptioncall) :: (GENERATOR_REQUEST_RENDER_RETURN pgenfatal_parent n_old false) :: (GENERATOR_REQUEST_REPORT pgenfatal_parent) :: ptask_parent_tail*
$call_tasks_valid(S_bailout_future,S_bailout_future.TODO)
''')
    replay_start = 'S_bailout' if release else 'S_report'
    checks += [
        f'S_stopped = $drive_steps({replay_start},0)',
        f'S_stopped = {replay_start}[.COMPLETION = BUDGET]',
        'S_resumed = $drive(S_stopped[.COMPLETION = NORMAL],4096)',
        f'S_direct = $drive({replay_start},4096)',
    ]
    checks += fatal.lines(r'''
S_resumed = S_direct
S_resumed.COMPLETION = pgenfatal_bailout.FROZEN
S_resumed.TODO = eps /\ S_resumed.FRAMES = eps
S_resumed.DESTRUCTION.PHASE = DESTRUCTION_DONE
S_resumed.DESTRUCTION.CALLED = $destructor_all(0,|S_resumed.OBJECTS|)
~((HOBJECT n_new) <- S_resumed.ALLOCATIONS)
$heap_owners($heap_graph(S_resumed),HOBJECT n_old) = 1
$heap_owners($heap_graph(S_resumed),HOBJECT n_parent) = 1
$heap_owners($heap_graph(S_resumed),HOBJECT n_generator) = 1
$heap_owners($heap_graph(S_resumed),HOBJECT n_payload) = 1
S_resumed.DESTRUCTION.ABANDONED = [pdestructioncleanup_fatal]
pdestructioncleanup_fatal.SOURCE = DESTRUCTOR_FATAL pdestructionfatal
pdestructionfatal.FRAME.TODO = S_bailout.TODO
''')
    checks += ['$close_outputs(S_resumed.EVENTS) = ' + driver.driver.byte_expr(CASES[name][1])]
    checks += valid('S_resumed')
    return checks


def main():
    process = driver.driver.process
    driver.driver.process = lambda argv, path, seconds, root: process(argv, path, min(seconds, 120), root)
    base.CASES = CASES
    driver.CASES = CASES
    driver.NATIVE_ERROR_PREFIXES = {
        'request-render-handler-throws': b'Fatal error: Uncaught RenderHandlerAbort: handler',
        'request-render-handler-throw-release': b'Fatal error: Uncaught RenderHandlerRelease: handler-release',
    }
    driver.PREFIX += base.PREFIX + fatal.PREFIX + PREFIX
    driver.assertions = assertions
    driver.source.WATCHED += peer.EXTRA_WATCHED + [
        'tests/semantics/reference_yield_protocol.py',
        'tests/semantics/generator_request_finally_protocol.py',
        'tests/semantics/generator_request_abrupt_protocol.py',
        'tests/semantics/generator_request_render_handler_throw_protocol.py',
    ]
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())
