#!/usr/bin/env python3
"""Genuine post-report stdClass and ordinary child storage before bailout."""
import os

import generator_request_abrupt_protocol as fatal
import generator_request_child_storage_peer_sources as peer
from reference_yield_protocol import valid, reject

base = fatal.base
driver = fatal.driver
NAME = 'request-fatal-std-child-storage'
CASES = {NAME: peer.CASES['peer-request-fatal-std-child-before-bailout']}
PREFIX = r'''
def $request_finally_phase(S,400) = true
  -- if S.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask_tail*
  -- if S.OBJECTS[pinstancestorage.OBJECT] = STDINSTANCE
def $request_finally_phase(S,401) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.RECEIVER = (n)
  -- if $object_name(S,n) = $ptascii("LeafPostReport363")
  -- if $trace_context_function(S,pcallcontext) = $ptascii("__destruct")
def $request_finally_phase(S,402) = true
  -- if $request_finally_phase(S,401)
  -- if S.RESULT = KNOWN (POBJECT n)
  -- if S.OBJECTS[n] = GENERATOR pgenerator
def $request_finally_phase(S,403) = true
  -- if S.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask_tail*
  -- if $object_name(S,pinstancestorage.OBJECT) = $ptascii("LeafPostReport363")
'''


def assertions(checked, path, directory, name):
    initial = ('$php_file_run(' + checked['fixture'] + ',0,'
               + driver.driver.byte_expr(os.fsencode(path)) + ','
               + driver.driver.byte_expr(os.fsencode(driver.ROOT)) + ')')
    checks = ['S_initial = ' + initial, '~S_initial.COMPILESTOP']
    checks += base.seek('S_report', 'S_initial', 300) + fatal.normal_valid('S_report')
    checks += fatal.lines(r'''
S_report.TODO = (GENERATOR_REQUEST_REPORT pgenfatal_report) :: ptask_report_tail*
pgenfatal_report.SOURCE = THROW_SEARCH n_exception
n_exception = pgenfatal_report.OBJECT
ptask_report_tail* = (EXCEPTION_HANDLER_RESULT pexceptioncall) :: (GENERATOR_REQUEST_RESUME pgenclose) :: ptask_finish*
n_old = pexceptioncall.OBJECT
n_old =/= n_exception
n_generator = pgenclose.OBJECT
S_report.OBJECTS[n_generator] = GENERATOR pgenerator
pgenerator.PHASE = GENERATOR_CLOSED /\ pgenerator.FRAME = eps
pgenerator.VALUE = (POBJECT n_payload)
$heap_owners($heap_graph(S_report),HOBJECT n_generator) = 1
$heap_owners($heap_graph(S_report),HOBJECT n_payload) = 1
''')
    checks += base.seek('S_storage', 'S_report', 400)
    checks += fatal.lines(r'''
S_storage.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask_storage_tail*
ptask_storage_tail* = (DESTRUCTOR_RELEASE pdestructionrelease) :: (GENERATOR_REQUEST_BAILOUT pgenfatal_bailout) :: ptask_report_tail*
n_std = pinstancestorage.OBJECT
~pinstancestorage.USER /\ pinstancestorage.CALLER = eps
pinstancestorage.ORIGIN = eps /\ pinstancestorage.CONSTCONTEXT = eps
pinstancestorage.NEXT = 0
$instance_storage_valid(S_storage,pinstancestorage)
$object_table_at(S_storage.OBJECTTABLES,n_std) = (n_table)
$entry_lookup(S_storage.ARRAYS[n_table].ITEMS,KSTRING $ptascii("leaf")) = (DIRECT (POBJECT n_leaf))
$heap_owners($heap_graph(S_storage),HOBJECT n_std) = 1
$heap_owners($heap_graph(S_storage),HARRAY n_table) = 1
$heap_owners($heap_graph(S_storage),HOBJECT n_leaf) = 1
$heap_owners($heap_graph(S_storage),HOBJECT n_generator) = 1
$heap_owners($heap_graph(S_storage),HOBJECT n_payload) = 1
~((HOBJECT n_exception) <- S_storage.ALLOCATIONS)
$throwable_live(S_storage,n_old)
$heap_owners($heap_graph(S_storage),HOBJECT n_old) = 1
$task_nodes(GENERATOR_REQUEST_BAILOUT pgenfatal_bailout) = eps
$request_fatal_stderr(S_storage.EVENTS) =/= eps
$generator_request_bailout_tail(S_storage.TODO,pgenfatal_bailout) = (ptask_report_tail*)
$generator_request_bailout_at(S_storage.TODO) = (pgenfatal_bailout)
$generator_request_bailout_valid(S_storage,pgenfatal_bailout)
$generator_request_resume_valid(S_storage,pgenclose)
''')
    checks += fatal.normal_valid('S_storage')
    checks += fatal.lines(r'''
~$generator_request_tail_task(INSTANCE_STORAGE_STEP pinstancestorage[.USER = true])
$generator_request_bailout_tail((INSTANCE_STORAGE_STEP pinstancestorage[.USER = true]) :: ptask_storage_tail*,pgenfatal_bailout) = eps
$generator_request_bailout_at((INSTANCE_STORAGE_STEP pinstancestorage[.USER = true]) :: ptask_storage_tail*) = eps
~$generator_request_resume_plain((INSTANCE_STORAGE_STEP pinstancestorage[.USER = true]) :: ptask_storage_tail*,pgenclose)
''')
    reject(checks, 'storage_user', 'S_storage[.TODO = (INSTANCE_STORAGE_STEP pinstancestorage[.USER = true]) :: ptask_storage_tail*]', 'S_storage')
    reject(checks, 'storage_handle', 'S_storage[.TODO = (INSTANCE_STORAGE_STEP pinstancestorage[.HANDLE = 0]) :: ptask_storage_tail*]', 'S_storage')
    checks += ['S_transfer_step = $drive_steps(S_storage,1)',
               'S_transfer_step.COMPLETION = NORMAL \\/ S_transfer_step.COMPLETION = BUDGET',
               'S_transferred = S_transfer_step[.COMPLETION = NORMAL]']
    checks += fatal.normal_valid('S_transferred')
    checks += fatal.lines(r'''
S_transferred.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_table) :: (INSTANCE_STORAGE_STEP pinstancestorage_after) :: ptask_storage_tail*
pdestructionrelease_table.JOBS = [DESTRUCTION_VALUE (HARRAY n_table)]
pinstancestorage_after = pinstancestorage[.NEXT = |pinstancestorage.SLOTS|]
$object_table_at(S_transferred.OBJECTTABLES,n_std) = eps
$heap_owners($heap_graph(S_transferred),HOBJECT n_std) = 1
$heap_owners($heap_graph(S_transferred),HARRAY n_table) = 1
$heap_owners($heap_graph(S_transferred),HOBJECT n_leaf) = 1
''')
    checks += base.seek('S_leaf', 'S_transferred', 401) + fatal.normal_valid('S_leaf')
    checks += fatal.lines(r'''
S_leaf.CURRENT = (pcallcontext_leaf)
pcallcontext_leaf.RECEIVER = (n_leaf)
S_leaf.FRAMES = pframe_leaf :: pframe_leaf_tail*
pframe_leaf.TODO = (DESTRUCTOR_RESULT pdestructorcall_leaf) :: ptask_leaf_tail*
pdestructorcall_leaf.OBJECT = n_leaf
~pdestructorcall_leaf.USER /\ pdestructorcall_leaf.CALLER = eps
pdestructorcall_leaf.FRAME = eps /\ pdestructorcall_leaf.OPERATION = eps
$heap_owners($heap_graph(S_leaf),HOBJECT n_std) = 1
$heap_owners($heap_graph(S_leaf),HOBJECT n_generator) = 1
$heap_owners($heap_graph(S_leaf),HOBJECT n_payload) = 1
$request_fatal_stderr(S_leaf.EVENTS) = $request_fatal_stderr(S_storage.EVENTS)
''')
    checks += base.seek('S_lookup', 'S_leaf', 402) + fatal.normal_valid('S_lookup')
    checks += fatal.lines(r'''
S_lookup.RESULT = KNOWN (POBJECT n_generator)
$heap_owners($heap_graph(S_lookup),HOBJECT n_generator) = 2
$heap_owners($heap_graph(S_lookup[.RESULT = KNOWN PNULL]),HOBJECT n_generator) = 1
$heap_owners($heap_graph(S_lookup),HOBJECT n_payload) = 1
''')
    checks += base.seek('S_leaf_storage', 'S_lookup', 403) + fatal.normal_valid('S_leaf_storage')
    checks += fatal.lines(r'''
S_leaf_storage.TODO = (INSTANCE_STORAGE_STEP pinstancestorage_leaf) :: ptask_leaf_storage_tail*
pinstancestorage_leaf.OBJECT = n_leaf
~pinstancestorage_leaf.USER /\ pinstancestorage_leaf.CALLER = eps
$instance_storage_valid(S_leaf_storage,pinstancestorage_leaf)
$instance_storage_all(S_leaf_storage) = [pinstancestorage_leaf,pinstancestorage_after]
$heap_owners($heap_graph(S_leaf_storage),HOBJECT n_leaf) = 1
$heap_owners($heap_graph(S_leaf_storage),HOBJECT n_std) = 1
$heap_owners($heap_graph(S_leaf_storage),HOBJECT n_generator) = 1
$generator_request_bailout_at(S_leaf_storage.TODO) = (pgenfatal_bailout)
$generator_request_bailout_valid(S_leaf_storage,pgenfatal_bailout)
$generator_request_resume_valid(S_leaf_storage,pgenclose)
''')
    checks += base.seek('S_bailout', 'S_leaf_storage', 320) + fatal.normal_valid('S_bailout')
    checks += fatal.lines(r'''
S_bailout.TODO = (GENERATOR_REQUEST_BAILOUT pgenfatal_bailout) :: ptask_report_tail*
~((HOBJECT n_exception) <- S_bailout.ALLOCATIONS)
~((HOBJECT n_std) <- S_bailout.ALLOCATIONS)
~((HOBJECT n_leaf) <- S_bailout.ALLOCATIONS)
~((HARRAY n_table) <- S_bailout.ALLOCATIONS)
$heap_owners($heap_graph(S_bailout),HOBJECT n_generator) = 1
$heap_owners($heap_graph(S_bailout),HOBJECT n_payload) = 1
$heap_owners($heap_graph(S_bailout),HOBJECT n_old) = 1
''')
    checks += [
        'S_stopped = $drive_steps(S_storage,0)',
        'S_stopped = S_storage[.COMPLETION = BUDGET]',
        'S_resumed = $drive(S_stopped[.COMPLETION = NORMAL],4096)',
        'S_direct = $drive(S_storage,4096)',
        'S_resumed = S_direct',
        'S_resumed.COMPLETION = pgenfatal_bailout.FROZEN',
        'S_resumed.TODO = eps /\\ S_resumed.FRAMES = eps',
        'S_resumed.DESTRUCTION.PHASE = DESTRUCTION_DONE',
        'S_resumed.DESTRUCTION.CALLED = $destructor_all(0,|S_resumed.OBJECTS|)',
        '$close_outputs(S_resumed.EVENTS) = ' + driver.driver.byte_expr(CASES[name][1]),
        '$request_fatal_stderr(S_resumed.EVENTS) = $request_fatal_stderr(S_storage.EVENTS)',
        '$heap_owners($heap_graph(S_resumed),HOBJECT n_generator) = 1',
        '$heap_owners($heap_graph(S_resumed),HOBJECT n_payload) = 1',
        '$heap_owners($heap_graph(S_resumed),HOBJECT n_old) = 1',
    ]
    checks += valid('S_resumed')
    return checks


def main():
    process = driver.driver.process
    driver.driver.process = lambda argv, path, seconds, root: process(argv, path, min(seconds, 120), root)
    base.CASES = CASES
    driver.CASES = CASES
    driver.NATIVE_ERROR_PREFIXES = {NAME: b'Fatal error: Uncaught ChildExceptionPostReport363: handler'}
    driver.PREFIX += base.PREFIX + fatal.PREFIX + PREFIX
    driver.assertions = assertions
    driver.source.WATCHED += [
        'spec/semantics/152-throwable-runtime.watsup',
        'spec/semantics/168-user-string-runtime.watsup',
        'spec/semantics/176-throwable-subclass-storage.watsup',
        'spec/semantics/222-exception-handlers.watsup',
        'spec/semantics/231-shutdown-functions.watsup',
        'spec/semantics/270-eager-destructors.watsup',
        'spec/semantics/296-weak-references.watsup',
        'spec/semantics/340-generator-request-finally.watsup',
        'spec/semantics/355-generator-storage-pin.watsup',
        'spec/semantics/359-instance-storage-pin.watsup',
        'spec/semantics/360-generator-request-delegation.watsup',
        'spec/semantics/363-generator-request-abrupt.watsup',
        'tests/semantics/reference_yield_protocol.py',
        'tests/semantics/generator_request_finally_protocol.py',
        'tests/semantics/generator_request_abrupt_protocol.py',
        'tests/semantics/generator_request_child_storage_peer_sources.py',
        'tests/semantics/generator_request_child_storage_protocol.py',
    ]
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())
