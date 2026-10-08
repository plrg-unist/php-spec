#!/usr/bin/env python3
"""Reached fatal rendering, exception release and retained request-close pins."""
import os

import generator_request_finally_protocol as base
import generator_request_abrupt_sources as author
import generator_request_abrupt_peer_sources as peer
from reference_yield_protocol import valid, reject

driver = base.driver
SELECTED = {
    'request-fatal-report-bailout': peer.UNSUPPORTED['peer-request-fatal-abandons-cache-and-later-destructor'],
    'request-fatal-custom-render': peer.UNSUPPORTED['peer-request-fatal-render-retains-generator-and-cache'],
    'request-fatal-handler-custom-render': author.UNSUPPORTED['request-handler-fatal-render-retains-original-exception'],
    'request-fatal-exception-release': author.UNSUPPORTED['request-fatal-releases-exception-before-bailout'],
}
CASES = {name: (row[0], row[1], row[3]) for name, row in SELECTED.items()}
NATIVE_ERROR_PREFIXES = {
    'request-fatal-report-bailout': peer.NATIVE_ERROR_PREFIXES['peer-request-fatal-abandons-cache-and-later-destructor'],
    'request-fatal-custom-render': peer.NATIVE_ERROR_PREFIXES['peer-request-fatal-render-retains-generator-and-cache'],
    'request-fatal-handler-custom-render': author.NATIVE_ERROR_PREFIXES['request-handler-fatal-render-retains-original-exception'],
    'request-fatal-exception-release': author.NATIVE_ERROR_PREFIXES['request-fatal-releases-exception-before-bailout'],
}
PREFIX = r'''
def $request_finally_phase(S,300) = true
  -- if S.TODO = (GENERATOR_REQUEST_REPORT pgenfatal) :: ptask_tail*
  -- if pgenfatal.METHOD = eps
def $request_finally_phase(S,301) = true
  -- if S.TODO = (CALL_ARGS (METHOD_TARGET n porigin) eps 0 eps (porigin) 0) :: (STRINGIFY_RESULT n porigin 0) :: (GENERATOR_REQUEST_REPORT pgenfatal) :: ptask_tail*
def $request_finally_phase(S,302) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $trace_context_function(S,pcallcontext) = $ptascii("__toString")
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if $generator_request_report_at(pframe.TODO) =/= eps
def $request_finally_phase(S,303) = true
  -- if $request_finally_phase(S,302)
  -- if S.RESULT = KNOWN (POBJECT n)
  -- if S.OBJECTS[n] = GENERATOR pgenerator
def $request_finally_phase(S,310) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.RECEIVER = (n)
  -- if $object_name(S,n) = $ptascii("ReleaseRequestException")
  -- if $trace_context_function(S,pcallcontext) = $ptascii("__destruct")
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if $generator_request_bailout_at(pframe.TODO) =/= eps
def $request_finally_phase(S,311) = ($request_finally_phase(S,310) /\ S.REPORTING = 0)
def $request_finally_phase(S,320) = true
  -- if S.TODO = (GENERATOR_REQUEST_BAILOUT pgenfatal) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
dec $request_fatal_stderr_event(pevent) : bool
dec $request_fatal_stderr(pevent*) : preqbytes
def $request_fatal_stderr(eps) = eps
def $request_fatal_stderr((STDERR ptbytes) :: pevent_tail*) = ptbytes ++ $request_fatal_stderr(pevent_tail*)
def $request_fatal_stderr(pevent :: pevent_tail*) = $request_fatal_stderr(pevent_tail*)
  -- if ~$request_fatal_stderr_event(pevent)
def $request_fatal_stderr_event(STDERR ptbytes) = true
def $request_fatal_stderr_event(pevent) = false -- otherwise
'''


def lines(value):
    return value.strip().splitlines()


def normal_valid(state):
    return driver.valid(state) + [f"$scope_codes_valid({state},{state}.CODE)"]


def assertions(checked, path, directory, name):
    initial = ('$php_file_run(' + checked['fixture'] + ',0,'
               + driver.driver.byte_expr(os.fsencode(path)) + ','
               + driver.driver.byte_expr(os.fsencode(driver.ROOT)) + ')')
    checks = ['S_initial = ' + initial, '~S_initial.COMPILESTOP']
    custom = name in ['request-fatal-custom-render', 'request-fatal-handler-custom-render']
    handler = name == 'request-fatal-handler-custom-render'
    release = name == 'request-fatal-exception-release'
    checks += base.seek('S_report', 'S_initial', 300) + normal_valid('S_report')
    checks += lines(r'''
S_report.TODO = (GENERATOR_REQUEST_REPORT pgenfatal_report) :: ptask_report_tail*
$generator_request_report_valid(S_report,pgenfatal_report)
n_exception = pgenfatal_report.OBJECT
pgenfatal_report.METHOD = eps /\ pgenfatal_report.TEXT = eps
pgenfatal_report.REPORT = eps /\ pgenfatal_report.FROZEN = NORMAL
$task_nodes(GENERATOR_REQUEST_REPORT pgenfatal_report) = [HOBJECT n_exception]
$heap_owners($heap_graph(S_report),HOBJECT n_exception) = 1
$generator_close_claims(ptask_report_tail*) = [n_generator]
S_report.OBJECTS[n_generator] = GENERATOR pgenerator_report
pgenerator_report.PHASE = GENERATOR_CLOSED /\ pgenerator_report.FRAME = eps
pgenerator_report.VALUE = (POBJECT n_payload)
(HOBJECT n_payload) <- S_report.ALLOCATIONS
$heap_owners($heap_graph(S_report),HOBJECT n_generator) = 1
$heap_owners($heap_graph(S_report),HOBJECT n_payload) = 1
$request_fatal_stderr(S_report.EVENTS) = eps
''')
    if handler:
        checks += lines(r'''
pgenfatal_report.SOURCE = THROW_SEARCH n_exception
ptask_report_tail* = (EXCEPTION_HANDLER_RESULT pexceptioncall_report) :: (GENERATOR_REQUEST_RESUME pgenclose_report) :: ptask_finish*
pexceptioncall_report.OBJECT = n_old
n_old =/= n_exception
$throwable_live(S_report,n_old)
$throwable_field(S_report,n_exception,"trace") = PARRAY n_trace
$entry_lookup(S_report.ARRAYS[n_trace].ITEMS,KINT 0) = (DIRECT (PARRAY n_trace_frame))
$entry_lookup(S_report.ARRAYS[n_trace_frame].ITEMS,KSTRING $ptascii("args")) = (DIRECT (PARRAY n_trace_args))
$entry_lookup(S_report.ARRAYS[n_trace_args].ITEMS,KINT 0) = (DIRECT (POBJECT n_old))
$heap_owners($heap_graph(S_report),HOBJECT n_old) = 2
$throwable_field(S_report,n_exception,"previous") = PNULL
pgenfatal_report.HANDLERS = S_report.EXCEPTIONHANDLERS
$generator_request_resume_valid(S_report,pgenclose_report)
''')
    else:
        checks += lines(r'''
pgenfatal_report.SOURCE = GENERATOR_CLOSE_DONE pgenclose_original
pgenclose_original.PENDING = (n_exception)
ptask_report_tail* = (GENERATOR_CLOSE_DONE pgenclose_report) :: ptask_finish*
pgenclose_report = pgenclose_original[.PENDING = eps]
$generator_close_done_valid(S_report,pgenclose_report)
''')
    if release:
        checks += lines(r'''
$throwable_field(S_report,n_exception,"trace") = PARRAY n_release_trace
$entry_lookup(S_report.ARRAYS[n_release_trace].ITEMS,KINT 0) = (DIRECT (PARRAY n_release_trace_frame))
$entry_lookup(S_report.ARRAYS[n_release_trace_frame].ITEMS,KSTRING $ptascii("function")) = (DIRECT (PSTRING $ptascii("requestReleaseFatal")))
$entry_lookup(S_report.ARRAYS[n_release_trace_frame].ITEMS,KSTRING $ptascii("file")) = eps
$entry_lookup(S_report.ARRAYS[n_release_trace_frame].ITEMS,KSTRING $ptascii("line")) = eps
''')
    wrong_source = ('GENERATOR_CLOSE_DONE pgenclose_report' if handler else 'THROW_SEARCH n_exception')
    reject(checks, 'source', 'S_report[.TODO = (GENERATOR_REQUEST_REPORT pgenfatal_report[.SOURCE = '
           + wrong_source + ']) :: ptask_report_tail*]', 'S_report')
    reject(checks, 'report_object', 'S_report[.TODO = (GENERATOR_REQUEST_REPORT pgenfatal_report[.OBJECT = n_generator]) :: ptask_report_tail*]', 'S_report', same_heap=False)
    previous = 'S_report'
    if custom:
        checks += base.seek('S_string', previous, 301) + normal_valid('S_string')
        checks += lines(r'''
S_string.TODO = (CALL_ARGS (METHOD_TARGET n_exception porigin_method) eps 0 eps (porigin_method) 0) :: (STRINGIFY_RESULT n_exception porigin_method 0) :: (GENERATOR_REQUEST_REPORT pgenfatal_string) :: ptask_string_tail*
pgenfatal_string = pgenfatal_report[.METHOD = (porigin_method)]
$terminal_string_site(S_string,porigin_method,0)
$generator_request_report_valid(S_string,pgenfatal_string)
$heap_owners($heap_graph(S_string),HOBJECT n_generator) = 1
$heap_owners($heap_graph(S_string),HOBJECT n_payload) = 1
''')
        checks += base.seek('S_renderer', 'S_string', 302) + normal_valid('S_renderer')
        checks += lines(r'''
S_renderer.FRAMES = pframe_renderer :: pframe_renderer_tail*
pframe_renderer.TODO = (STRINGIFY_RESULT n_exception porigin_method 0) :: (GENERATOR_REQUEST_REPORT pgenfatal_string) :: ptask_string_tail*
$heap_owners($heap_graph(S_renderer),HOBJECT n_generator) = 1
$heap_owners($heap_graph(S_renderer),HOBJECT n_payload) = 1
$request_fatal_stderr(S_renderer.EVENTS) = eps
''')
        if name == 'request-fatal-custom-render':
            reject(checks, 'renderer_method', 'S_renderer[.FRAMES = pframe_renderer[.TODO = (STRINGIFY_RESULT n_exception porigin_method 0) :: (GENERATOR_REQUEST_REPORT pgenfatal_string[.METHOD = eps]) :: ptask_string_tail*] :: pframe_renderer_tail*]', 'S_renderer')
        checks += base.seek('S_lookup', 'S_renderer', 303) + normal_valid('S_lookup')
        checks += lines(r'''
S_lookup.RESULT = KNOWN (POBJECT n_generator)
$heap_owners($heap_graph(S_lookup),HOBJECT n_generator) = 2
$heap_owners($heap_graph(S_lookup[.RESULT = KNOWN PNULL]),HOBJECT n_generator) = 1
(HOBJECT n_payload) <- S_lookup.ALLOCATIONS
$heap_owners($heap_graph(S_lookup),HOBJECT n_payload) = 1
$request_fatal_stderr(S_lookup.EVENTS) = eps
''')
        if handler:
            checks += lines(r'''
S_lookup.EXCEPTIONHANDLER =/= eps
S_lookup.EXCEPTIONHANDLERS =/= pgenfatal_string.HANDLERS
$throwable_live(S_lookup,n_old)
$heap_owners($heap_graph(S_lookup),HOBJECT n_old) = 2
$throwable_field(S_lookup,n_exception,"previous") = PNULL
''')
        previous = 'S_lookup'
    if release:
        checks += base.seek('S_exception_dtor', previous, 310) + normal_valid('S_exception_dtor')
        checks += lines(r'''
S_exception_dtor.FRAMES = pframe_exception :: pframe_exception_tail*
pframe_exception.TODO = (DESTRUCTOR_RESULT pdestructorcall_exception) :: ptask_exception_tail*
pdestructorcall_exception.OBJECT = n_exception
~pdestructorcall_exception.USER /\ pdestructorcall_exception.CALLER = eps
pdestructorcall_exception.FRAME = eps /\ pdestructorcall_exception.OPERATION = eps
$generator_request_bailout_at(ptask_exception_tail*) = (pgenfatal_released)
$task_nodes(GENERATOR_REQUEST_BAILOUT pgenfatal_released) = eps
$heap_owners($heap_graph(S_exception_dtor),HOBJECT n_generator) = 1
$heap_owners($heap_graph(S_exception_dtor),HOBJECT n_payload) = 1
$request_fatal_stderr(S_exception_dtor.EVENTS) =/= eps
ptbytes_reported = $request_fatal_stderr(S_exception_dtor.EVENTS)
$throwable_field(S_exception_dtor,n_exception,"message") = PSTRING $ptascii("new")
''')
        checks += base.seek('S_mutated', 'S_exception_dtor', 311) + normal_valid('S_mutated')
        checks += lines(r'''
S_mutated.REPORTING = 0
$throwable_field(S_mutated,n_exception,"message") = PSTRING $ptascii("later")
$request_fatal_stderr(S_mutated.EVENTS) = ptbytes_reported
$generator_request_report_frozen(S_mutated,pgenfatal_released) = pgenfatal_released.FROZEN
''')
        previous = 'S_mutated'
    checks += base.seek('S_bailout', previous, 320) + normal_valid('S_bailout')
    checks += lines(r'''
S_bailout.TODO = (GENERATOR_REQUEST_BAILOUT pgenfatal_bailout) :: ptask_bailout_tail*
$generator_request_bailout_valid(S_bailout,pgenfatal_bailout)
pgenfatal_bailout.SOURCE = pgenfatal_report.SOURCE
pgenfatal_bailout.HANDLERS = pgenfatal_report.HANDLERS
$task_nodes(GENERATOR_REQUEST_BAILOUT pgenfatal_bailout) = eps
~((HOBJECT n_exception) <- S_bailout.ALLOCATIONS)
$objectprops_record_at(S_bailout.OBJECTPROPS,n_exception) = eps
$heap_owners($heap_graph(S_bailout),HOBJECT n_exception) = 0
$heap_owners($heap_graph(S_bailout),HOBJECT n_generator) = 1
$heap_owners($heap_graph(S_bailout),HOBJECT n_payload) = 1
$request_fatal_stderr(S_bailout.EVENTS) =/= eps
$generator_request_report_frozen(S_bailout,pgenfatal_bailout) = pgenfatal_bailout.FROZEN
''')
    if handler:
        checks += ['~((HARRAY n_trace) <- S_bailout.ALLOCATIONS)',
                   '~((HARRAY n_trace_args) <- S_bailout.ALLOCATIONS)',
                   '$throwable_live(S_bailout,n_old)',
                   '$heap_owners($heap_graph(S_bailout),HOBJECT n_old) = 1',
                   '$generator_request_resume_valid(S_bailout,pgenclose_report)']
    if handler:
        checks += ['pgenfatal_bailout.REPORT = (pobjectprops_bailout)',
                   'n_beyond = |S_bailout.OBJECTS|']
        reject(checks, 'bailout_bounds', 'S_bailout[.TODO = (GENERATOR_REQUEST_BAILOUT pgenfatal_bailout[.OBJECT = n_beyond][.SOURCE = THROW_SEARCH n_beyond][.REPORT = (pobjectprops_bailout[.OBJECT = n_beyond])]) :: ptask_bailout_tail*]', 'S_bailout')
    reject(checks, 'frozen_report', 'S_bailout[.TODO = (GENERATOR_REQUEST_BAILOUT pgenfatal_bailout[.FROZEN = REQUESTFATAL $ptascii("Exception") $ptascii("forged") 0]) :: ptask_bailout_tail*]', 'S_bailout')
    checks += [f'S_stopped = $drive_steps({previous},0)',
               f'S_stopped = {previous}[.COMPLETION = BUDGET]',
               'S_resumed = $drive(S_stopped[.COMPLETION = NORMAL],4096)',
               f'S_direct = $drive({previous},4096)', 'S_resumed = S_direct',
               'S_resumed.COMPLETION = pgenfatal_bailout.FROZEN',
               'S_resumed.TODO = eps', 'S_resumed.FRAMES = eps',
               'S_resumed.DESTRUCTION.PHASE = DESTRUCTION_DONE',
               'S_resumed.DESTRUCTION.CALLED = $destructor_all(0,|S_resumed.OBJECTS|)',
               '$close_outputs(S_resumed.EVENTS) = ' + driver.driver.byte_expr(CASES[name][1]),
               '$request_fatal_stderr(S_resumed.EVENTS) = $request_fatal_stderr(S_bailout.EVENTS)',
               '~((HOBJECT n_exception) <- S_resumed.ALLOCATIONS)',
               '(HOBJECT n_generator) <- S_resumed.ALLOCATIONS',
               '(HOBJECT n_payload) <- S_resumed.ALLOCATIONS',
               '$heap_owners($heap_graph(S_resumed),HOBJECT n_generator) = 1',
               '$heap_owners($heap_graph(S_resumed),HOBJECT n_payload) = 1',
               'S_resumed.DESTRUCTION.ABANDONED = [pdestructioncleanup_fatal]',
               'pdestructioncleanup_fatal.SOURCE = DESTRUCTOR_FATAL pdestructionfatal',
               'pdestructionfatal.FRAME.TODO = S_bailout.TODO',
               '$eager_fatal_nodes(pdestructionfatal) = $tasks_nodes(S_bailout.TODO)']
    checks += valid('S_resumed')
    return checks


def main():
    base.CASES = CASES
    driver.CASES = CASES
    driver.NATIVE_ERROR_PREFIXES = NATIVE_ERROR_PREFIXES
    driver.PREFIX += base.PREFIX + PREFIX
    driver.assertions = assertions
    driver.source.WATCHED += [
        'spec/semantics/152-throwable-runtime.watsup',
        'spec/semantics/168-user-string-runtime.watsup',
        'spec/semantics/176-throwable-subclass-storage.watsup',
        'spec/semantics/222-exception-handlers.watsup',
        'spec/semantics/231-shutdown-functions.watsup',
        'spec/semantics/257-request-destructors.watsup',
        'spec/semantics/270-eager-destructors.watsup',
        'spec/semantics/296-weak-references.watsup',
        'spec/semantics/328-generator-reference-yields.watsup',
        'spec/semantics/340-generator-request-finally.watsup',
        'spec/semantics/349-generator-request-fresh.watsup',
        'spec/semantics/355-generator-storage-pin.watsup',
        'spec/semantics/360-generator-request-delegation.watsup',
        'spec/semantics/363-generator-request-abrupt.watsup',
        'tests/semantics/reference_yield_protocol.py',
        'tests/semantics/generator_request_finally_protocol.py',
        'tests/semantics/generator_request_abrupt_sources.py',
        'tests/semantics/generator_request_abrupt_peer_sources.py',
        'tests/semantics/generator_request_abrupt_protocol.py',
    ]
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())
