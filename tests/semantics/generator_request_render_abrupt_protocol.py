#!/usr/bin/env python3
"""Reached C-root renderer rethrow, inner report/release and outer abandonment."""
import os

import generator_request_abrupt_protocol as fatal
import generator_request_render_abrupt_peer_sources as peer
import generator_request_render_abrupt_sources as author
from reference_yield_protocol import valid, reject

base = fatal.base
driver = fatal.driver
CASES = {
    'request-render-abrupt-root': peer.CASES['peer-request-render-throws-with-live-generator-cache'],
    'request-render-abrupt-inner-release': author.CASES['request-render-inner-release-before-bailout'],
    'request-render-abrupt-handler-parent': author.CASES['request-handler-render-throws'],
}
PREFIX = r'''
def $request_finally_phase(S,410) = $generator_request_report_abrupt(S)
def $request_finally_phase(S,411) = true
  -- if S.TODO = (GENERATOR_REQUEST_REPORT pgenfatal) :: (GENERATOR_REQUEST_REPORT pgenfatal_parent) :: ptask_tail*
  -- if pgenfatal.SOURCE = STRINGIFY_RESULT pgenfatal_parent.OBJECT porigin_method 0
  -- if pgenfatal.METHOD = eps
def $request_finally_phase(S,412) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.RECEIVER = (n)
  -- if $object_name(S,n) = $ptascii("InnerRenderRelease")
  -- if $trace_context_function(S,pcallcontext) = $ptascii("__destruct")
def $request_finally_phase(S,413) = ($request_finally_phase(S,412) /\ S.REPORTING = 0)
def $request_finally_phase(S,414) = true
  -- if S.TODO = (GENERATOR_REQUEST_BAILOUT pgenfatal) :: (GENERATOR_REQUEST_REPORT pgenfatal_parent) :: ptask_tail*
  -- if pgenfatal.SOURCE = STRINGIFY_RESULT pgenfatal_parent.OBJECT porigin_method 0
def $request_finally_phase(S,415) = true
  -- if $request_finally_phase(S,412)
  -- if S.RESULT = KNOWN (POBJECT n)
  -- if S.OBJECTS[n] = GENERATOR pgenerator
'''


def assertions(checked, path, directory, name):
    initial = ('$php_file_run(' + checked['fixture'] + ',0,'
               + driver.driver.byte_expr(os.fsencode(path)) + ','
               + driver.driver.byte_expr(os.fsencode(driver.ROOT)) + ')')
    release = name == 'request-render-abrupt-inner-release'
    handler = name == 'request-render-abrupt-handler-parent'
    checks = ['S_initial = ' + initial, '~S_initial.COMPILESTOP']
    checks += base.seek('S_lookup', 'S_initial', 303) + fatal.normal_valid('S_lookup')
    checks += fatal.lines(r'''
S_lookup.RESULT = KNOWN (POBJECT n_generator)
$heap_owners($heap_graph(S_lookup),HOBJECT n_generator) = 2
$heap_owners($heap_graph(S_lookup[.RESULT = KNOWN PNULL]),HOBJECT n_generator) = 1
$request_fatal_stderr(S_lookup.EVENTS) = eps
''')
    checks += base.seek('S_abrupt', 'S_lookup', 410) + fatal.normal_valid('S_abrupt')
    checks += fatal.lines(r'''
S_abrupt.TODO = (THROW_SEARCH n_inner) :: (STRINGIFY_RESULT n_parent porigin_method 0) :: (GENERATOR_REQUEST_REPORT pgenfatal_parent) :: ptask_parent_tail*
S_abrupt.CURRENT = eps /\ S_abrupt.FRAMES = eps
S_abrupt.ORIGIN = (porigin_method) /\ S_abrupt.EXCEPTIONHANDLER = eps
pgenfatal_parent.OBJECT = n_parent /\ pgenfatal_parent.METHOD = (porigin_method)
n_parent =/= n_inner
$throwable_live(S_abrupt,n_inner) /\ $throwable_live(S_abrupt,n_parent)
$heap_owners($heap_graph(S_abrupt),HOBJECT n_inner) = 1
$heap_owners($heap_graph(S_abrupt),HOBJECT n_parent) = 2
$generator_close_claims(ptask_parent_tail*) = [n_generator]
S_abrupt.OBJECTS[n_generator] = GENERATOR pgenerator
pgenerator.PHASE = GENERATOR_CLOSED /\ pgenerator.FRAME = eps
pgenerator.VALUE = (POBJECT n_payload)
$heap_owners($heap_graph(S_abrupt),HOBJECT n_generator) = 1
$heap_owners($heap_graph(S_abrupt),HOBJECT n_payload) = 1
$throwable_field(S_abrupt,n_inner,"previous") = PNULL
$throwable_field(S_abrupt,n_parent,"string") = PSTRING eps
$throwable_field(S_abrupt,n_inner,"trace") = PARRAY n_trace_inner
$entry_lookup(S_abrupt.ARRAYS[n_trace_inner].ITEMS,KINT 0) = (DIRECT (PARRAY n_frame_inner))
$entry_lookup(S_abrupt.ARRAYS[n_frame_inner].ITEMS,KSTRING $ptascii("function")) = (DIRECT (PSTRING $ptascii("__toString")))
$entry_lookup(S_abrupt.ARRAYS[n_frame_inner].ITEMS,KSTRING $ptascii("file")) = eps
$entry_lookup(S_abrupt.ARRAYS[n_frame_inner].ITEMS,KSTRING $ptascii("line")) = eps
$generator_request_fatal_selected(S_abrupt) = (pgenfatal_inner)
pgenfatal_inner.SOURCE = STRINGIFY_RESULT n_parent porigin_method 0
pgenfatal_inner.OBJECT = n_inner
pgenfatal_inner.METHOD = eps /\ pgenfatal_inner.REPORT = eps
S_abrupt_future = $call_after_origin(S_abrupt,THROW_SEARCH n_inner)
S_abrupt_future.TODO = (STRINGIFY_RESULT n_parent porigin_method 0) :: (GENERATOR_REQUEST_REPORT pgenfatal_parent) :: ptask_parent_tail*
$call_tasks_valid(S_abrupt_future,S_abrupt_future.TODO)
$request_fatal_stderr(S_abrupt.EVENTS) = eps
''')
    if not release and not handler:
        reject(checks, 'abrupt_consumer', 'S_abrupt[.TODO = (THROW_SEARCH n_inner) :: (STRINGIFY_RESULT n_parent porigin_method 0) :: (GENERATOR_REQUEST_REPORT pgenfatal_parent[.METHOD = eps]) :: ptask_parent_tail*]', 'S_abrupt')
    if handler:
        checks += fatal.lines(r'''
pgenfatal_parent.SOURCE = THROW_SEARCH n_parent
ptask_parent_tail* = (EXCEPTION_HANDLER_RESULT pexceptioncall) :: (GENERATOR_REQUEST_RESUME pgenclose) :: ptask_finish*
n_old = pexceptioncall.OBJECT
$throwable_field(S_abrupt,n_parent,"previous") = PNULL
$throwable_field(S_abrupt,n_parent,"trace") = PARRAY n_trace_parent
$entry_lookup(S_abrupt.ARRAYS[n_trace_parent].ITEMS,KINT 0) = (DIRECT (PARRAY n_frame_parent))
$entry_lookup(S_abrupt.ARRAYS[n_frame_parent].ITEMS,KSTRING $ptascii("args")) = (DIRECT (PARRAY n_args_parent))
$entry_lookup(S_abrupt.ARRAYS[n_args_parent].ITEMS,KINT 0) = (DIRECT (POBJECT n_old))
$heap_owners($heap_graph(S_abrupt),HOBJECT n_old) = 2
$generator_request_fatal_selected(S_abrupt[.EXCEPTIONHANDLER = (pexceptioncall.CALLBACK)]) = eps
''')
    else:
        checks += fatal.lines(r'''
pgenfatal_parent.SOURCE = GENERATOR_CLOSE_DONE pgenclose_original
pgenclose_original.PENDING = (n_parent)
ptask_parent_tail* = (GENERATOR_CLOSE_DONE pgenclose) :: ptask_finish*
pgenclose = pgenclose_original[.PENDING = eps]
''')
    checks += fatal.lines(r'''
S_inner_step = $drive_steps(S_abrupt,1)
S_inner_step.COMPLETION = NORMAL \/ S_inner_step.COMPLETION = BUDGET
S_inner = S_inner_step[.COMPLETION = NORMAL]
S_inner.TODO = (GENERATOR_REQUEST_REPORT pgenfatal_inner) :: (GENERATOR_REQUEST_REPORT pgenfatal_parent) :: ptask_parent_tail*
S_inner.ORIGIN = eps
S_inner.ALLOCATIONS = S_abrupt.ALLOCATIONS
$heap_graph(S_inner).NODES = $heap_graph(S_abrupt).NODES
$heap_graph(S_inner).EDGES = $heap_graph(S_abrupt).EDGES
$task_nodes(GENERATOR_REQUEST_REPORT pgenfatal_inner) = [HOBJECT n_inner]
$heap_owners($heap_graph(S_inner),HOBJECT n_inner) = 1
$heap_owners($heap_graph(S_inner),HOBJECT n_parent) = 1
$heap_owners($heap_graph(S_inner),HOBJECT n_generator) = 1
$heap_owners($heap_graph(S_inner),HOBJECT n_payload) = 1
$generator_request_report_valid(S_inner,pgenfatal_inner)
S_parent_view = $call_after_origin(S_inner,GENERATOR_REQUEST_REPORT pgenfatal_inner)
S_parent_view.TODO = (GENERATOR_REQUEST_REPORT pgenfatal_parent) :: ptask_parent_tail*
S_parent_view.ORIGIN = (porigin_method)
$generator_request_report_valid(S_parent_view,pgenfatal_parent)
$call_tasks_valid(S_parent_view,S_parent_view.TODO)
''')
    checks += fatal.normal_valid('S_inner')
    reject(checks, 'inner_source', 'S_inner[.TODO = (GENERATOR_REQUEST_REPORT pgenfatal_inner[.SOURCE = STRINGIFY_RESULT n_generator porigin_method 0]) :: (GENERATOR_REQUEST_REPORT pgenfatal_parent) :: ptask_parent_tail*]', 'S_inner')
    reject(checks, 'parent_method', 'S_inner[.TODO = (GENERATOR_REQUEST_REPORT pgenfatal_inner) :: (GENERATOR_REQUEST_REPORT pgenfatal_parent[.METHOD = eps]) :: ptask_parent_tail*]', 'S_inner')
    if handler:
        checks += ['$generator_request_resume_valid(S_inner,pgenclose)',
                   '$heap_owners($heap_graph(S_inner),HOBJECT n_old) = 2']
    previous = 'S_inner'
    if release:
        checks += base.seek('S_release', previous, 412) + fatal.normal_valid('S_release')
        checks += fatal.lines(r'''
S_release.CURRENT = (pcallcontext_release)
pcallcontext_release.RECEIVER = (n_inner)
S_release.FRAMES = pframe_release :: pframe_release_tail*
pframe_release.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: ptask_release_tail*
pdestructorcall.OBJECT = n_inner
~pdestructorcall.USER /\ pdestructorcall.CALLER = eps
pdestructorcall.FRAME = eps /\ pdestructorcall.OPERATION = eps
$generator_request_bailout_at(ptask_release_tail*) = (pgenfatal_releasing)
pgenfatal_releasing.SOURCE = pgenfatal_inner.SOURCE
$task_nodes(GENERATOR_REQUEST_BAILOUT pgenfatal_releasing) = eps
$heap_owners($heap_graph(S_release),HOBJECT n_parent) = 1
$heap_owners($heap_graph(S_release),HOBJECT n_generator) = 1
$heap_owners($heap_graph(S_release),HOBJECT n_payload) = 1
$request_fatal_stderr(S_release.EVENTS) =/= eps
ptbytes_reported = $request_fatal_stderr(S_release.EVENTS)
''')
        checks += base.seek('S_release_lookup', 'S_release', 415) + fatal.normal_valid('S_release_lookup')
        checks += fatal.lines(r'''
S_release_lookup.RESULT = KNOWN (POBJECT n_generator)
$heap_owners($heap_graph(S_release_lookup),HOBJECT n_generator) = 2
$heap_owners($heap_graph(S_release_lookup[.RESULT = KNOWN PNULL]),HOBJECT n_generator) = 1
$heap_owners($heap_graph(S_release_lookup),HOBJECT n_parent) = 1
''')
        checks += base.seek('S_masked', 'S_release_lookup', 413) + fatal.normal_valid('S_masked')
        checks += ['S_masked.REPORTING = 0',
                   '$request_fatal_stderr(S_masked.EVENTS) = ptbytes_reported']
        previous = 'S_masked'
    checks += base.seek('S_bailout', previous, 414) + fatal.normal_valid('S_bailout')
    checks += fatal.lines(r'''
S_bailout.TODO = (GENERATOR_REQUEST_BAILOUT pgenfatal_bailout) :: (GENERATOR_REQUEST_REPORT pgenfatal_parent) :: ptask_parent_tail*
pgenfatal_bailout.SOURCE = pgenfatal_inner.SOURCE
pgenfatal_bailout.OBJECT = n_inner
$generator_request_bailout_valid(S_bailout,pgenfatal_bailout)
$task_nodes(GENERATOR_REQUEST_BAILOUT pgenfatal_bailout) = eps
~((HOBJECT n_inner) <- S_bailout.ALLOCATIONS)
$objectprops_record_at(S_bailout.OBJECTPROPS,n_inner) = eps
$heap_owners($heap_graph(S_bailout),HOBJECT n_inner) = 0
(HOBJECT n_parent) <- S_bailout.ALLOCATIONS
$heap_owners($heap_graph(S_bailout),HOBJECT n_parent) = 1
$heap_owners($heap_graph(S_bailout),HOBJECT n_generator) = 1
$heap_owners($heap_graph(S_bailout),HOBJECT n_payload) = 1
$throwable_field(S_bailout,n_parent,"string") = PSTRING eps
$request_fatal_stderr(S_bailout.EVENTS) =/= eps
S_bailout_parent = $call_after_origin(S_bailout,GENERATOR_REQUEST_BAILOUT pgenfatal_bailout)
S_bailout_parent.TODO = (GENERATOR_REQUEST_REPORT pgenfatal_parent) :: ptask_parent_tail*
S_bailout_parent.ORIGIN = (porigin_method)
$call_tasks_valid(S_bailout_parent,S_bailout_parent.TODO)
''')
    if handler:
        checks += ['$heap_owners($heap_graph(S_bailout),HOBJECT n_old) = 2']
    checks += [f'S_stopped = $drive_steps({previous},0)',
               f'S_stopped = {previous}[.COMPLETION = BUDGET]',
               'S_resumed = $drive(S_stopped[.COMPLETION = NORMAL],4096)',
               f'S_direct = $drive({previous},4096)', 'S_resumed = S_direct',
               'S_resumed.COMPLETION = pgenfatal_bailout.FROZEN',
               'S_resumed.TODO = eps /\\ S_resumed.FRAMES = eps',
               'S_resumed.DESTRUCTION.PHASE = DESTRUCTION_DONE',
               'S_resumed.DESTRUCTION.CALLED = $destructor_all(0,|S_resumed.OBJECTS|)',
               '$close_outputs(S_resumed.EVENTS) = ' + driver.driver.byte_expr(CASES[name][1]),
               '$request_fatal_stderr(S_resumed.EVENTS) = $request_fatal_stderr(S_bailout.EVENTS)',
               '~((HOBJECT n_inner) <- S_resumed.ALLOCATIONS)',
               '$heap_owners($heap_graph(S_resumed),HOBJECT n_parent) = 1',
               '$heap_owners($heap_graph(S_resumed),HOBJECT n_generator) = 1',
               '$heap_owners($heap_graph(S_resumed),HOBJECT n_payload) = 1',
               'S_resumed.DESTRUCTION.ABANDONED = [pdestructioncleanup_fatal]',
               'pdestructioncleanup_fatal.SOURCE = DESTRUCTOR_FATAL pdestructionfatal',
               'pdestructionfatal.FRAME.TODO = S_bailout.TODO',
               '$eager_fatal_nodes(pdestructionfatal) = $tasks_nodes(S_bailout.TODO)']
    if handler:
        checks += ['$heap_owners($heap_graph(S_resumed),HOBJECT n_old) = 2']
    checks += valid('S_resumed')
    return checks


def main():
    process = driver.driver.process
    driver.driver.process = lambda argv, path, seconds, root: process(argv, path, min(seconds, 120), root)
    base.CASES = CASES
    driver.CASES = CASES
    driver.NATIVE_ERROR_PREFIXES = {
        'request-render-abrupt-root': b'Fatal error: Uncaught Exception: render',
        'request-render-abrupt-inner-release': b'Fatal error: Uncaught InnerRenderRelease: render',
        'request-render-abrupt-handler-parent': b'Fatal error: Uncaught Exception: render-handler',
    }
    driver.PREFIX += base.PREFIX + fatal.PREFIX + PREFIX
    driver.assertions = assertions
    driver.source.WATCHED += peer.EXTRA_WATCHED + [
        'tests/semantics/reference_yield_protocol.py',
        'tests/semantics/generator_request_finally_protocol.py',
        'tests/semantics/generator_request_abrupt_protocol.py',
        'tests/semantics/generator_request_render_abrupt_sources.py',
        'tests/semantics/generator_request_render_abrupt_protocol.py',
    ]
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())
