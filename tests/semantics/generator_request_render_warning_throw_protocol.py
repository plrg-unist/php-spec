#!/usr/bin/env python3
"""Reached warning throw, restored-handler redispatch and original fatal report."""
import os

import generator_request_abrupt_protocol as fatal
import generator_request_render_warning_throw_sources as source
from reference_yield_protocol import valid, reject

base = fatal.base
driver = fatal.driver
CASES = source.CASES
PREFIX = r'''
def $request_finally_phase(S,600) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ERROR_HANDLER_RESULT perrorcall) :: (GENERATOR_REQUEST_REPORT pgenfatal) :: ptask_tail*
  -- if perrorcall.RESUME = GENERATOR_REQUEST_RENDER_RETURN pgenfatal n_inner true
def $request_finally_phase(S,601) = true
  -- if S.TODO = (EXCEPTION_HANDLER_INVOKE pexceptioncall) :: (ERROR_HANDLER_RESULT perrorcall) :: (GENERATOR_REQUEST_REPORT pgenfatal) :: ptask_tail*
def $request_finally_phase(S,602) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $trace_context_function(S,pcallcontext) = $ptascii("handledWarningThrow")
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (EXCEPTION_HANDLER_RESULT pexceptioncall) :: ptask_tail*
  -- if $throwable_field(S,pexceptioncall.OBJECT,"message") = PSTRING $ptascii("warning")
def $request_finally_phase(S,603) = true
  -- if S.TODO = (EXCEPTION_HANDLER_CLEAN pexceptioncall false) :: (ERROR_HANDLER_RESULT perrorcall) :: (GENERATOR_REQUEST_REPORT pgenfatal) :: ptask_tail*
def $request_finally_phase(S,604) = true
  -- if S.TODO = (ERROR_HANDLER_RESULT perrorcall) :: (GENERATOR_REQUEST_REPORT pgenfatal) :: ptask_tail*
def $request_finally_phase(S,605) = true
  -- if S.TODO = (GENERATOR_REQUEST_RENDER_RETURN pgenfatal n_inner true) :: (GENERATOR_REQUEST_REPORT pgenfatal) :: ptask_tail*
def $request_finally_phase(S,606) = true
  -- if S.TODO = (GENERATOR_REQUEST_REPORT pgenfatal) :: ptask_tail*
  -- if S.RESULT = KNOWN (PSTRING ptbytes)
def $request_finally_phase(S,607) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.RECEIVER = (n)
  -- if $object_name(S,n) = $ptascii("RenderWarningThrowParent")
  -- if $trace_context_function(S,pcallcontext) = $ptascii("__destruct")
def $request_finally_phase(S,608) = true
  -- if S.TODO = (GENERATOR_REQUEST_BAILOUT pgenfatal) :: ptask_tail*
'''


def assertions(checked, path, directory, name):
    initial = ('$php_file_run(' + checked['fixture'] + ',0,'
               + driver.driver.byte_expr(os.fsencode(path)) + ','
               + driver.driver.byte_expr(os.fsencode(driver.ROOT)) + ')')
    checks = ['S_initial = ' + initial, '~S_initial.COMPILESTOP']
    checks += base.seek('S_abrupt', 'S_initial', 600) + fatal.normal_valid('S_abrupt')
    checks += fatal.lines(r'''
S_abrupt.TODO = (THROW_SEARCH n_warning) :: (ERROR_HANDLER_RESULT perrorcall) :: (GENERATOR_REQUEST_REPORT pgenfatal) :: ptask_parent_tail*
perrorcall.RESUME = GENERATOR_REQUEST_RENDER_RETURN pgenfatal n_inner true
pgenfatal.METHOD = (porigin_method)
S_abrupt.ORIGIN = (porigin_method)
perrorcall.SITE = porigin_method /\ perrorcall.LEVEL = 2 /\ perrorcall.LINE = 0
perrorcall.MESSAGE = $generator_request_render_warning(S_abrupt,pgenfatal)
perrorcall.EVENT = DIAGNOSTIC_INTERNAL "Warning" perrorcall.MESSAGE 0
$error_entered_call_valid(S_abrupt,perrorcall)
$error_handler_values(S_abrupt,perrorcall) = [PINT 2,PSTRING perrorcall.MESSAGE,PSTRING ($ptascii("Unknown")),PINT 0]
S_abrupt.ERRORHANDLER.CALLBACK = eps
S_abrupt.EXCEPTIONHANDLER = (pvalue_callback)
$exception_task_scope(S_abrupt) /\ $shutdown_render_throw_pending(S_abrupt)
$exception_dispatch_ready(S_abrupt)
$generator_request_fatal_selected(S_abrupt) = eps
$generator_request_render_return_valid(S_abrupt,pgenfatal,n_inner,true)
pgenfatal.SOURCE = GENERATOR_CLOSE_DONE pgenclose_original
pgenclose_original.PENDING = (pgenfatal.OBJECT)
ptask_parent_tail* = (GENERATOR_CLOSE_DONE pgenclose) :: ptask_finish*
pgenclose = pgenclose_original[.PENDING = eps]
n_parent = pgenfatal.OBJECT
$generator_close_claims(ptask_parent_tail*) = [n_generator]
S_abrupt.OBJECTS[n_generator] = GENERATOR pgenerator
pgenerator.PHASE = GENERATOR_CLOSED /\ pgenerator.FRAME = eps
pgenerator.VALUE = (POBJECT n_payload)
~((HOBJECT n_inner) <- S_abrupt.ALLOCATIONS)
$heap_owners($heap_graph(S_abrupt),HOBJECT n_inner) = 0
$heap_owners($heap_graph(S_abrupt),HOBJECT n_warning) = 1
$heap_owners($heap_graph(S_abrupt),HOBJECT n_parent) = 1
$heap_owners($heap_graph(S_abrupt),HOBJECT n_generator) = 1
$heap_owners($heap_graph(S_abrupt),HOBJECT n_payload) = 1
$throwable_field(S_abrupt,n_warning,"message") = PSTRING $ptascii("warning")
$throwable_field(S_abrupt,n_warning,"previous") = PNULL
$throwable_field(S_abrupt,n_parent,"string") = PSTRING eps
$request_fatal_stderr(S_abrupt.EVENTS) = eps
perrorcall_wrong_line = perrorcall[.LINE = 1][.EVENT = DIAGNOSTIC_INTERNAL "Warning" perrorcall.MESSAGE 1]
S_wrong_line = S_abrupt[.TODO = (THROW_SEARCH n_warning) :: (ERROR_HANDLER_RESULT perrorcall_wrong_line) :: (GENERATOR_REQUEST_REPORT pgenfatal) :: ptask_parent_tail*]
~$error_entered_call_valid(S_wrong_line,perrorcall_wrong_line)
~$exception_dispatch_ready(S_wrong_line)
''')
    reject(checks, 'warning_line', 'S_wrong_line', 'S_abrupt')
    checks += fatal.lines(r'''
S_abrupt.OBJECTS[n_parent] = INSTANCE porigin_class
$effective_method(S_abrupt,porigin_class,$ptascii("__destruct"),|S_abrupt.CLASSES|) = (pmethoddesc_wrong)
perrorcall_wrong_site = perrorcall[.SITE = pmethoddesc_wrong.FUNCTION.ORIGIN]
S_wrong_site = S_abrupt[.TODO = (THROW_SEARCH n_warning) :: (ERROR_HANDLER_RESULT perrorcall_wrong_site) :: (GENERATOR_REQUEST_REPORT pgenfatal) :: ptask_parent_tail*]
~$error_entered_call_valid(S_wrong_site,perrorcall_wrong_site)
~$exception_dispatch_ready(S_wrong_site)
pgenfatal_wrong_source = pgenfatal[.SOURCE = THROW_SEARCH n_parent]
perrorcall_wrong_source = perrorcall[.RESUME = GENERATOR_REQUEST_RENDER_RETURN pgenfatal_wrong_source n_inner true]
S_wrong_source = S_abrupt[.TODO = (THROW_SEARCH n_warning) :: (ERROR_HANDLER_RESULT perrorcall_wrong_source) :: (GENERATOR_REQUEST_REPORT pgenfatal_wrong_source) :: ptask_parent_tail*]
~$generator_request_report_valid(S_wrong_source,pgenfatal_wrong_source)
~$exception_dispatch_ready(S_wrong_source)
''')
    reject(checks, 'warning_site', 'S_wrong_site', 'S_abrupt')
    reject(checks, 'report_source', 'S_wrong_source', 'S_abrupt')
    checks += ['S_no_handler = S_abrupt[.EXCEPTIONHANDLER = eps]',
               '~$exception_dispatch_ready(S_no_handler)',
               '$generator_request_render_abrupt(S_no_handler)',
               'S_refused = $drive_steps(S_no_handler,1)',
               'S_refused.COMPLETION = UNSUPPORTED "Generator request fatal renderer handler or warning exception"']
    checks += fatal.normal_valid('S_no_handler')
    checks += base.seek('S_invoke', 'S_abrupt', 601) + fatal.normal_valid('S_invoke')
    checks += fatal.lines(r'''
S_invoke.TODO = (EXCEPTION_HANDLER_INVOKE pexceptioncall) :: (ERROR_HANDLER_RESULT perrorcall) :: (GENERATOR_REQUEST_REPORT pgenfatal) :: ptask_parent_tail*
pexceptioncall.OBJECT = n_warning /\ pexceptioncall.CALLBACK = pvalue_callback
pexceptioncall.ORIGIN = (porigin_method)
$exception_invoke_valid(S_invoke,pexceptioncall)
S_invoke.EXCEPTIONHANDLER = eps
S_invoke.EXCEPTIONHANDLERS = (pvalue_callback) :: S_abrupt.EXCEPTIONHANDLERS
$heap_owners($heap_graph(S_invoke),HOBJECT n_warning) = 1
$heap_owners($heap_graph(S_invoke),HOBJECT n_parent) = 1
$heap_owners($heap_graph(S_invoke),HOBJECT n_generator) = 1
$heap_owners($heap_graph(S_invoke),HOBJECT n_payload) = 1
$heap_graph(S_invoke).NODES = $heap_graph(S_abrupt).NODES
$heap_graph(S_invoke).EDGES = $heap_graph(S_abrupt).EDGES
pexceptioncall_wrong = pexceptioncall[.ORIGIN = eps]
S_wrong_origin = S_invoke[.TODO = (EXCEPTION_HANDLER_INVOKE pexceptioncall_wrong) :: (ERROR_HANDLER_RESULT perrorcall) :: (GENERATOR_REQUEST_REPORT pgenfatal) :: ptask_parent_tail*]
$exception_invoke_valid(S_wrong_origin,pexceptioncall_wrong)
~$generator_request_render_return_valid(S_wrong_origin,pgenfatal,n_inner,true)
''')
    reject(checks, 'handler_origin', 'S_wrong_origin', 'S_invoke')
    checks += base.seek('S_handler', 'S_invoke', 602) + fatal.normal_valid('S_handler')
    checks += fatal.lines(r'''
S_handler.FRAMES = pframe_handler :: pframe_handler_tail*
pframe_handler.TODO = (EXCEPTION_HANDLER_RESULT pexceptioncall_entered) :: (ERROR_HANDLER_RESULT perrorcall) :: (GENERATOR_REQUEST_REPORT pgenfatal) :: ptask_parent_tail*
pexceptioncall_entered.OBJECT = n_warning /\ pexceptioncall_entered.ORIGIN = (porigin_method)
pexceptioncall_entered.SENT = (KNOWN (POBJECT n_warning)) /\ pexceptioncall_entered.RECEIVED = (KNOWN (POBJECT n_warning))
S_handler.CURRENT = (pcallcontext_handler)
pcallcontext_handler.ARGC = 1 /\ pcallcontext_handler.EXTRA = eps
pframe_handler.CONTEXT = eps /\ pframe_handler.ORIGIN = eps
S_handler.EXCEPTIONHANDLER = eps /\ S_handler.ERRORHANDLER.CALLBACK = eps
$heap_owners($heap_graph(S_handler),HOBJECT n_warning) = 2
$heap_owners($heap_graph(S_handler),HOBJECT n_parent) = 1
$heap_owners($heap_graph(S_handler),HOBJECT n_generator) = 1
$heap_owners($heap_graph(S_handler),HOBJECT n_payload) = 1
''')
    checks += base.seek('S_cleanup', 'S_handler', 603) + fatal.normal_valid('S_cleanup')
    checks += ['$exception_cleanup_valid(S_cleanup,pexceptioncall_entered,false)',
               r'S_cleanup.EXCEPTIONHANDLER = eps /\ S_cleanup.ERRORHANDLER.CALLBACK = eps',
               '$heap_owners($heap_graph(S_cleanup),HOBJECT n_warning) = 1']
    checks += base.seek('S_warning_return', 'S_cleanup', 604) + fatal.normal_valid('S_warning_return')
    checks += fatal.lines(r'''
S_warning_return.TODO = (ERROR_HANDLER_RESULT perrorcall) :: (GENERATOR_REQUEST_REPORT pgenfatal) :: ptask_parent_tail*
S_warning_return.ORIGIN = (porigin_method)
S_warning_return.RESULT = KNOWN PNULL /\ S_warning_return.BASE = BASE_VALUE (KNOWN PNULL)
S_warning_return.EXCEPTIONHANDLER = (pvalue_callback)
S_warning_return.EXCEPTIONHANDLERS = S_abrupt.EXCEPTIONHANDLERS
S_warning_return.ERRORHANDLER.CALLBACK = eps
~((HOBJECT n_warning) <- S_warning_return.ALLOCATIONS)
~((HOBJECT n_inner) <- S_warning_return.ALLOCATIONS)
$heap_owners($heap_graph(S_warning_return),HOBJECT n_parent) = 1
$heap_owners($heap_graph(S_warning_return),HOBJECT n_generator) = 1
$heap_owners($heap_graph(S_warning_return),HOBJECT n_payload) = 1
''')
    checks += base.seek('S_warned', 'S_warning_return', 605) + fatal.normal_valid('S_warned')
    checks += fatal.lines(r'''
S_warned.TODO = (GENERATOR_REQUEST_RENDER_RETURN pgenfatal n_inner true) :: (GENERATOR_REQUEST_REPORT pgenfatal) :: ptask_parent_tail*
S_warned.ERRORHANDLER.CALLBACK = (perrorcall.CALLBACK)
S_warned.EXCEPTIONHANDLER = (pvalue_callback)
~((DIAGNOSTIC_INTERNAL "Warning" perrorcall.MESSAGE 0) <- S_warned.EVENTS)
$throwable_field(S_warned,n_parent,"string") = PSTRING eps
''')
    checks += base.seek('S_report', 'S_warned', 606) + fatal.normal_valid('S_report')
    checks += ['S_report.RESULT = KNOWN (PSTRING eps)',
               '$generator_request_report_valid(S_report,pgenfatal)']
    checks += base.seek('S_dtor', 'S_report', 607) + fatal.normal_valid('S_dtor')
    checks += ['$heap_owners($heap_graph(S_dtor),HOBJECT n_parent) = 2',
               '$heap_owners($heap_graph(S_dtor),HOBJECT n_generator) = 1',
               '$heap_owners($heap_graph(S_dtor),HOBJECT n_payload) = 1',
               '$request_fatal_stderr(S_dtor.EVENTS) = '
               + driver.driver.byte_expr(b'Fatal error: Uncaught \n  thrown in '
                                         + os.fsencode(path) + b' on line 7\n')]
    checks += base.seek('S_bailout', 'S_dtor', 608) + fatal.normal_valid('S_bailout')
    checks += fatal.lines(r'''
S_bailout.TODO = (GENERATOR_REQUEST_BAILOUT pgenfatal_bailout) :: ptask_parent_tail*
pgenfatal_bailout.OBJECT = n_parent /\ pgenfatal_bailout.SOURCE = pgenfatal.SOURCE
pgenfatal_bailout.TEXT = (eps)
~((HOBJECT n_parent) <- S_bailout.ALLOCATIONS)
~((HOBJECT n_warning) <- S_bailout.ALLOCATIONS)
~((HOBJECT n_inner) <- S_bailout.ALLOCATIONS)
$heap_owners($heap_graph(S_bailout),HOBJECT n_generator) = 1
$heap_owners($heap_graph(S_bailout),HOBJECT n_payload) = 1
S_stopped = $drive_steps(S_abrupt,0)
S_stopped = S_abrupt[.COMPLETION = BUDGET]
S_resumed = $drive(S_stopped[.COMPLETION = NORMAL],4096)
S_direct = $drive(S_abrupt,4096)
S_resumed = S_direct
S_resumed.COMPLETION = pgenfatal_bailout.FROZEN
S_resumed.TODO = eps /\ S_resumed.FRAMES = eps
S_resumed.DESTRUCTION.PHASE = DESTRUCTION_DONE
S_resumed.DESTRUCTION.CALLED = $destructor_all(0,|S_resumed.OBJECTS|)
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
        'request-render-warning-handler-throws': b'Fatal error: Uncaught \n  thrown in {file} on line 7\n',
    }
    driver.PREFIX += base.PREFIX + fatal.PREFIX + PREFIX
    driver.assertions = assertions
    driver.source.WATCHED += source.previous.EXTRA_WATCHED + [
        'tests/semantics/reference_yield_protocol.py',
        'tests/semantics/generator_request_finally_protocol.py',
        'tests/semantics/generator_request_abrupt_protocol.py',
        'tests/semantics/generator_request_render_warning_throw_sources.py',
        'tests/semantics/generator_request_render_warning_throw_protocol.py',
    ]
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())
