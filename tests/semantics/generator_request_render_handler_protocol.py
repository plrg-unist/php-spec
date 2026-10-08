#!/usr/bin/env python3
"""Reached request renderer handler, inner release and live warning continuation."""
import os

import generator_request_abrupt_protocol as fatal
import generator_request_render_handler_peer_sources as peer
import generator_request_render_handler_sources as author
from reference_yield_protocol import valid, reject

base = fatal.base
driver = fatal.driver
SELECTED = {
    'request-render-handler-normal': peer.UNSUPPORTED['peer-request-render-handler-returns'],
    'request-render-handler-inner-release': peer.UNSUPPORTED['peer-request-render-inner-dtor-before-handler-restore'],
    'request-render-handler-warning': author.UNSUPPORTED['request-render-warning-reads-live-cache'],
}
CASES = {name: (row[0], row[1], row[3]) for name, row in SELECTED.items()}
PREFIX = r'''
def $request_finally_phase(S,420) = $generator_request_render_dispatch_ready(S)
def $request_finally_phase(S,421) = true
  -- if S.TODO = (EXCEPTION_HANDLER_INVOKE pexceptioncall) :: (GENERATOR_REQUEST_RENDER_RETURN pgenfatal n false) :: (GENERATOR_REQUEST_REPORT pgenfatal) :: ptask_tail*
def $request_finally_phase(S,422) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $trace_context_function(S,pcallcontext) <- [$ptascii("handledRenderInner"),$ptascii("handledInnerRenderDtor"),$ptascii("handledWarningInner")]
def $request_finally_phase(S,423) = true
  -- if $request_finally_phase(S,422)
  -- if S.RESULT = KNOWN (POBJECT n)
  -- if S.OBJECTS[n] = GENERATOR pgenerator
def $request_finally_phase(S,424) = true
  -- if S.TODO = (GENERATOR_REQUEST_RENDER_RETURN pgenfatal n false) :: (GENERATOR_REQUEST_REPORT pgenfatal) :: ptask_tail*
def $request_finally_phase(S,425) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.RECEIVER = (n)
  -- if $object_name(S,n) = $ptascii("InnerHandledRender")
  -- if $trace_context_function(S,pcallcontext) = $ptascii("__destruct")
def $request_finally_phase(S,426) = true
  -- if $request_finally_phase(S,425)
  -- if S.RESULT = KNOWN (POBJECT n)
  -- if S.OBJECTS[n] = GENERATOR pgenerator
def $request_finally_phase(S,427) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $trace_context_function(S,pcallcontext) = $ptascii("handledRenderWarning")
def $request_finally_phase(S,428) = true
  -- if $request_finally_phase(S,427)
  -- if S.RESULT = KNOWN (POBJECT n)
  -- if $object_name(S,n) = $ptascii("RenderWarningException")
def $request_finally_phase(S,430) = true
  -- if S.TODO = (GENERATOR_REQUEST_RENDER_RETURN pgenfatal n true) :: (GENERATOR_REQUEST_REPORT pgenfatal) :: ptask_tail*
def $request_finally_phase(S,431) = true
  -- if S.TODO = (GENERATOR_REQUEST_REPORT pgenfatal) :: ptask_tail*
  -- if pgenfatal.METHOD =/= eps
  -- if S.RESULT = KNOWN (PSTRING ptbytes)
def $request_finally_phase(S,432) = true
  -- if S.TODO = (GENERATOR_REQUEST_BAILOUT pgenfatal) :: ptask_tail*
'''


def assertions(checked, path, directory, name):
    initial = ('$php_file_run(' + checked['fixture'] + ',0,'
               + driver.driver.byte_expr(os.fsencode(path)) + ','
               + driver.driver.byte_expr(os.fsencode(driver.ROOT)) + ')')
    release = name == 'request-render-handler-inner-release'
    warning = name == 'request-render-handler-warning'
    checks = ['S_initial = ' + initial, '~S_initial.COMPILESTOP']
    checks += base.seek('S_lookup', 'S_initial', 303) + fatal.normal_valid('S_lookup')
    checks += fatal.lines(r'''
S_lookup.RESULT = KNOWN (POBJECT n_generator)
$heap_owners($heap_graph(S_lookup),HOBJECT n_generator) = 2
''')
    checks += base.seek('S_abrupt', 'S_lookup', 420) + fatal.normal_valid('S_abrupt')
    checks += fatal.lines(r'''
S_abrupt.TODO = (THROW_SEARCH n_inner) :: (STRINGIFY_RESULT n_parent porigin_method 0) :: (GENERATOR_REQUEST_REPORT pgenfatal) :: ptask_parent_tail*
S_abrupt.EXCEPTIONHANDLER = (pvalue_callback)
pgenfatal.OBJECT = n_parent /\ pgenfatal.METHOD = (porigin_method)
pgenfatal.SOURCE = GENERATOR_CLOSE_DONE pgenclose_original
pgenclose_original.PENDING = (n_parent)
ptask_parent_tail* = (GENERATOR_CLOSE_DONE pgenclose) :: ptask_finish*
pgenclose = pgenclose_original[.PENDING = eps]
S_abrupt.OBJECTS[n_generator] = GENERATOR pgenerator
pgenerator.PHASE = GENERATOR_CLOSED /\ pgenerator.FRAME = eps
pgenerator.VALUE = (POBJECT n_payload)
$heap_owners($heap_graph(S_abrupt),HOBJECT n_inner) = 1
$heap_owners($heap_graph(S_abrupt),HOBJECT n_parent) = 2
$heap_owners($heap_graph(S_abrupt),HOBJECT n_generator) = 1
$heap_owners($heap_graph(S_abrupt),HOBJECT n_payload) = 1
$generator_request_fatal_selected(S_abrupt) = eps
$throwable_field(S_abrupt,n_parent,"string") = PSTRING eps
$request_fatal_stderr(S_abrupt.EVENTS) = eps
S_receiver_step = $drive_steps(S_abrupt,1)
S_receiver_step.COMPLETION = NORMAL \/ S_receiver_step.COMPLETION = BUDGET
S_receiver = S_receiver_step[.COMPLETION = NORMAL]
S_receiver.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (EXCEPTION_HANDLER_INVOKE pexceptioncall) :: (GENERATOR_REQUEST_RENDER_RETURN pgenfatal n_inner false) :: (GENERATOR_REQUEST_REPORT pgenfatal) :: ptask_parent_tail*
pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_parent)]
pdestructionoperation.SOURCE = THROW_SEARCH n_inner
pexceptioncall.OBJECT = n_inner /\ pexceptioncall.CALLBACK = pvalue_callback
pexceptioncall.ORIGIN = (porigin_method)
S_receiver.EXCEPTIONHANDLER = eps
S_receiver.EXCEPTIONHANDLERS = (pvalue_callback) :: S_abrupt.EXCEPTIONHANDLERS
$heap_owners($heap_graph(S_receiver),HOBJECT n_parent) = 2
$heap_owners($heap_graph(S_receiver),HOBJECT n_inner) = 1
$heap_owners($heap_graph(S_receiver),HOBJECT n_generator) = 1
$heap_owners($heap_graph(S_receiver),HOBJECT n_payload) = 1
$heap_graph(S_receiver).NODES = $heap_graph(S_abrupt).NODES
$heap_graph(S_receiver).EDGES = $heap_graph(S_abrupt).EDGES
''')
    checks += fatal.normal_valid('S_receiver')
    checks += base.seek('S_invoke', 'S_receiver', 421) + fatal.normal_valid('S_invoke')
    checks += fatal.lines(r'''
S_invoke.TODO = (EXCEPTION_HANDLER_INVOKE pexceptioncall) :: (GENERATOR_REQUEST_RENDER_RETURN pgenfatal n_inner false) :: (GENERATOR_REQUEST_REPORT pgenfatal) :: ptask_parent_tail*
$exception_invoke_valid(S_invoke,pexceptioncall)
$generator_request_render_return_valid(S_invoke,pgenfatal,n_inner,false)
$generator_request_report_valid(S_invoke,pgenfatal)
$task_nodes(GENERATOR_REQUEST_RENDER_RETURN pgenfatal n_inner false) = eps
$heap_owners($heap_graph(S_invoke),HOBJECT n_parent) = 1
$heap_owners($heap_graph(S_invoke),HOBJECT n_inner) = 1
S_without_borrow = S_invoke[.TODO = (EXCEPTION_HANDLER_INVOKE pexceptioncall) :: (GENERATOR_REQUEST_REPORT pgenfatal) :: ptask_parent_tail*]
$heap_graph(S_without_borrow) = $heap_graph(S_invoke)
''')
    if not release and not warning:
        checks += fatal.lines(r'''
pexceptioncall_wrong = pexceptioncall[.ORIGIN = eps]
S_wrong_origin = S_invoke[.TODO = (EXCEPTION_HANDLER_INVOKE pexceptioncall_wrong) :: (GENERATOR_REQUEST_RENDER_RETURN pgenfatal n_inner false) :: (GENERATOR_REQUEST_REPORT pgenfatal) :: ptask_parent_tail*]
$exception_invoke_valid(S_wrong_origin,pexceptioncall_wrong)
$generator_request_render_at(S_wrong_origin.TODO) = eps
~$call_descriptors_valid(S_wrong_origin)
$heap_graph(S_wrong_origin) = $heap_graph(S_invoke)
''')
    checks += base.seek('S_handler', 'S_invoke', 422) + fatal.normal_valid('S_handler')
    checks += fatal.lines(r'''
S_handler.FRAMES = pframe_handler :: pframe_handler_tail*
pframe_handler.TODO = (EXCEPTION_HANDLER_RESULT pexceptioncall_entered) :: (GENERATOR_REQUEST_RENDER_RETURN pgenfatal n_inner false) :: (GENERATOR_REQUEST_REPORT pgenfatal) :: ptask_parent_tail*
pframe_handler.CONTEXT = eps /\ pframe_handler.ORIGIN = eps
pexceptioncall_entered.OBJECT = n_inner /\ pexceptioncall_entered.ORIGIN = (porigin_method)
S_handler.EXCEPTIONHANDLER = eps
$heap_owners($heap_graph(S_handler),HOBJECT n_inner) = 2
$heap_owners($heap_graph(S_handler),HOBJECT n_parent) = 1
$heap_owners($heap_graph(S_handler),HOBJECT n_generator) = 1
$heap_owners($heap_graph(S_handler),HOBJECT n_payload) = 1
''')
    previous = 'S_handler'
    if not warning:
        checks += base.seek('S_handler_lookup', previous, 423) + fatal.normal_valid('S_handler_lookup')
        checks += fatal.lines(r'''
S_handler_lookup.RESULT = KNOWN (POBJECT n_generator)
$heap_owners($heap_graph(S_handler_lookup),HOBJECT n_generator) = 2
$heap_owners($heap_graph(S_handler_lookup[.RESULT = KNOWN PNULL]),HOBJECT n_generator) = 1
$heap_owners($heap_graph(S_handler_lookup),HOBJECT n_parent) = 1
''')
        previous = 'S_handler_lookup'
    if release:
        checks += base.seek('S_inner_dtor', previous, 425) + fatal.normal_valid('S_inner_dtor')
        checks += fatal.lines(r'''
S_inner_dtor.CURRENT = (pcallcontext_dtor)
pcallcontext_dtor.RECEIVER = (n_inner)
S_inner_dtor.FRAMES = pframe_dtor :: pframe_dtor_tail*
pframe_dtor.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: ptask_dtor_tail*
pdestructorcall.OBJECT = n_inner /\ ~pdestructorcall.USER
$heap_owners($heap_graph(S_inner_dtor),HOBJECT n_inner) = 2
S_inner_dtor.EXCEPTIONHANDLER = eps
S_inner_dtor.EXCEPTIONHANDLERS = (pvalue_callback) :: S_abrupt.EXCEPTIONHANDLERS
$heap_owners($heap_graph(S_inner_dtor),HOBJECT n_parent) = 1
$heap_owners($heap_graph(S_inner_dtor),HOBJECT n_generator) = 1
$heap_owners($heap_graph(S_inner_dtor),HOBJECT n_payload) = 1
$request_fatal_stderr(S_inner_dtor.EVENTS) = eps
''')
        checks += base.seek('S_inner_lookup', 'S_inner_dtor', 426) + fatal.normal_valid('S_inner_lookup')
        checks += ['S_inner_lookup.RESULT = KNOWN (POBJECT n_generator)',
                   '$heap_owners($heap_graph(S_inner_lookup),HOBJECT n_generator) = 2']
        previous = 'S_inner_lookup'
    checks += base.seek('S_return', previous, 424) + fatal.normal_valid('S_return')
    checks += fatal.lines(r'''
S_return.TODO = (GENERATOR_REQUEST_RENDER_RETURN pgenfatal n_inner false) :: (GENERATOR_REQUEST_REPORT pgenfatal) :: ptask_parent_tail*
S_return.ORIGIN = (porigin_method)
S_return.RESULT = KNOWN PNULL /\ S_return.BASE = BASE_VALUE (KNOWN PNULL)
S_return.EXCEPTIONHANDLER = (pvalue_callback)
S_return.EXCEPTIONHANDLERS = S_abrupt.EXCEPTIONHANDLERS
~((HOBJECT n_inner) <- S_return.ALLOCATIONS)
$heap_owners($heap_graph(S_return),HOBJECT n_inner) = 0
$heap_owners($heap_graph(S_return),HOBJECT n_parent) = 1
$heap_owners($heap_graph(S_return),HOBJECT n_generator) = 1
$heap_owners($heap_graph(S_return),HOBJECT n_payload) = 1
$request_fatal_stderr(S_return.EVENTS) = eps
S_parent_view = $call_after_origin(S_return,GENERATOR_REQUEST_RENDER_RETURN pgenfatal n_inner false)
S_parent_view.TODO = (GENERATOR_REQUEST_REPORT pgenfatal) :: ptask_parent_tail*
$call_tasks_valid(S_parent_view,S_parent_view.TODO)
''')
    if not release and not warning:
        checks += fatal.lines(r'''
n_beyond = |S_return.OBJECTS|
S_wrong_return_origin = S_return[.ORIGIN = eps]
$generator_request_render_view(S_wrong_return_origin,pgenfatal) = S_wrong_return_origin
~$generator_request_render_return_valid(S_wrong_return_origin,pgenfatal,n_inner,false)
S_wrong_return_result = S_return[.RESULT = KNOWN (POBJECT n_generator)]
~$generator_request_render_return_valid(S_wrong_return_result,pgenfatal,n_inner,false)
$heap_owners($heap_graph(S_wrong_return_result),HOBJECT n_generator) = 2
''')
        reject(checks, 'return_origin', 'S_wrong_return_origin', 'S_return')
        reject(checks, 'return_result', 'S_wrong_return_result', 'S_return', same_heap=False)
        reject(checks, 'return_object_bounds', 'S_return[.TODO = (GENERATOR_REQUEST_RENDER_RETURN pgenfatal n_beyond false) :: (GENERATOR_REQUEST_REPORT pgenfatal) :: ptask_parent_tail*]', 'S_return')
    previous = 'S_return'
    if warning:
        checks += base.seek('S_warning', previous, 427) + fatal.normal_valid('S_warning')
        checks += fatal.lines(r'''
S_warning.FRAMES = pframe_warning :: pframe_warning_tail*
pframe_warning.TODO = (ERROR_HANDLER_RESULT perrorcall) :: (GENERATOR_REQUEST_REPORT pgenfatal) :: ptask_parent_tail*
perrorcall.RESUME = GENERATOR_REQUEST_RENDER_RETURN pgenfatal n_inner true
S_warning_root = $constant_frame_scope(S_warning,pframe_warning,pframe_warning_tail*)
$error_entered_call_valid(S_warning_root,perrorcall)
$error_handler_file(S_warning_root,perrorcall) = $ptascii("Unknown")
$error_handler_values(S_warning_root,perrorcall) = [PINT 2,PSTRING perrorcall.MESSAGE,PSTRING ($ptascii("Unknown")),PINT 0]
S_warning.EXCEPTIONHANDLER = (pvalue_callback)
~((HOBJECT n_inner) <- S_warning.ALLOCATIONS)
$heap_owners($heap_graph(S_warning),HOBJECT n_parent) = 1
$heap_owners($heap_graph(S_warning),HOBJECT n_generator) = 1
$heap_owners($heap_graph(S_warning),HOBJECT n_payload) = 1
''')
        checks += base.seek('S_warning_lookup', 'S_warning', 428) + fatal.normal_valid('S_warning_lookup')
        checks += ['S_warning_lookup.RESULT = KNOWN (POBJECT n_parent)',
                   '$heap_owners($heap_graph(S_warning_lookup),HOBJECT n_parent) = 2']
        previous = 'S_warning_lookup'
    checks += base.seek('S_warned', previous, 430) + fatal.normal_valid('S_warned')
    checks += fatal.lines(r'''
S_warned.TODO = (GENERATOR_REQUEST_RENDER_RETURN pgenfatal n_inner true) :: (GENERATOR_REQUEST_REPORT pgenfatal) :: ptask_parent_tail*
$throwable_field(S_warned,n_parent,"string") = PSTRING ptbytes_cached
$heap_owners($heap_graph(S_warned),HOBJECT n_parent) = 1
$heap_owners($heap_graph(S_warned),HOBJECT n_generator) = 1
$heap_owners($heap_graph(S_warned),HOBJECT n_payload) = 1
''')
    if warning:
        checks += ['ptbytes_cached =/= eps', '$throwable_field(S_warned,n_parent,"message") = PSTRING ($ptascii("changed"))',
                   '$request_fatal_stderr(S_warned.EVENTS) = eps']
    else:
        checks += ['ptbytes_cached = eps', '$request_fatal_stderr(S_warned.EVENTS) =/= eps']
    checks += base.seek('S_report', 'S_warned', 431) + fatal.normal_valid('S_report')
    checks += ['S_report.RESULT = KNOWN (PSTRING ptbytes_cached)',
               '$generator_request_report_valid(S_report,pgenfatal)']
    checks += base.seek('S_bailout', 'S_report', 432) + fatal.normal_valid('S_bailout')
    checks += fatal.lines(r'''
S_bailout.TODO = (GENERATOR_REQUEST_BAILOUT pgenfatal_bailout) :: ptask_parent_tail*
pgenfatal_bailout.OBJECT = n_parent /\ pgenfatal_bailout.SOURCE = pgenfatal.SOURCE
pgenfatal_bailout.TEXT = (ptbytes_cached)
$generator_request_bailout_valid(S_bailout,pgenfatal_bailout)
~((HOBJECT n_inner) <- S_bailout.ALLOCATIONS)
~((HOBJECT n_parent) <- S_bailout.ALLOCATIONS)
$heap_owners($heap_graph(S_bailout),HOBJECT n_parent) = 0
$heap_owners($heap_graph(S_bailout),HOBJECT n_generator) = 1
$heap_owners($heap_graph(S_bailout),HOBJECT n_payload) = 1
$request_fatal_stderr(S_bailout.EVENTS) =/= eps
S_stopped = $drive_steps(S_return,0)
S_stopped = S_return[.COMPLETION = BUDGET]
S_resumed = $drive(S_stopped[.COMPLETION = NORMAL],4096)
S_direct = $drive(S_return,4096)
S_resumed = S_direct
S_resumed.COMPLETION = pgenfatal_bailout.FROZEN
S_resumed.TODO = eps /\ S_resumed.FRAMES = eps
S_resumed.DESTRUCTION.PHASE = DESTRUCTION_DONE
S_resumed.DESTRUCTION.CALLED = $destructor_all(0,|S_resumed.OBJECTS|)
~((HOBJECT n_parent) <- S_resumed.ALLOCATIONS)
~((HOBJECT n_inner) <- S_resumed.ALLOCATIONS)
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
        'request-render-handler-normal': b'Warning: RenderHandlerException::__toString() must return a string',
        'request-render-handler-inner-release': b'Warning: RenderInnerDtorException::__toString() must return a string',
        'request-render-handler-warning': b'Fatal error: Uncaught RenderWarningException: changed',
    }
    driver.PREFIX += base.PREFIX + fatal.PREFIX + PREFIX
    driver.assertions = assertions
    driver.source.WATCHED += peer.EXTRA_WATCHED + [
        'tests/semantics/reference_yield_protocol.py',
        'tests/semantics/generator_request_finally_protocol.py',
        'tests/semantics/generator_request_abrupt_protocol.py',
        'tests/semantics/generator_request_render_handler_sources.py',
        'tests/semantics/generator_request_render_handler_protocol.py',
    ]
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())
