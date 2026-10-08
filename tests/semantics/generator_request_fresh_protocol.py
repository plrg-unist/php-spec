#!/usr/bin/env python3
"""Reached fresh STORE frames, transferred owners and immediate CV handlers."""
import os

import generator_request_finally_protocol as base
import generator_request_fresh_sources as author
import generator_request_fresh_peer_sources as peer
from reference_yield_protocol import valid, reject

driver = base.driver
CASES = {
    'fresh-pure-request-activation': author.CASES['fresh-pure-request-activation'],
    'fresh-self-reference-becomes-borrowed-store-bucket': author.CASES['fresh-self-reference-becomes-borrowed-store-bucket'],
    'fresh-closure-owner-survives-frame-retirement': author.CASES['fresh-closure-owner-survives-frame-retirement'],
    'peer-fresh-store-handler-precedes-later-parameter-release': peer.CASES['peer-fresh-store-handler-precedes-later-parameter-release'],
}
PREFIX = r'''
def $request_finally_phase(S,60) = true
  -- if S.TODO = [DESTRUCTOR_STORE]
  -- if $destructor_handle(S,S.DESTRUCTION.INDEX,0) = (n)
  -- if S.OBJECTS[n] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_FRESH
  -- if $generator_request_store_ready(S,n)
def $request_finally_phase(S,61) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin
  -- if $object_name(S,n) = $ptascii("First349")
  -- if $trace_context_function(S,pcallcontext) = $ptascii("__destruct")
  -- if $close_outputs(S.EVENTS) = $ptascii("C|")
def $request_finally_phase(S,62) = true
  -- if S.TODO = (GENERATOR_CLOSE_DONE pgenclose) :: ptask*
  -- if S.OBJECTS[pgenclose.OBJECT] = GENERATOR pgenerator
  -- if $generator_request_fresh_closed(pgenerator)
def $request_finally_phase(S,63) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $trace_context_function(S,pcallcontext) = $ptascii("caught349")
  -- if $exception_context_call(S,pcallcontext) = (pexceptioncall)
def $request_finally_phase(S,64) = true
  -- if S.DESTRUCTION.RETIRED = [(n_generator,n_handle)]
  -- if S.OBJECTS[n_generator] = GENERATOR pgenerator
  -- if $generator_request_fresh_closed(pgenerator)
  -- if $heap_owners($heap_graph(S),HOBJECT n_generator) = 0
'''


def assertions(checked, path, directory, name):
    initial = ('$php_file_run(' + checked['fixture'] + ',0,'
               + driver.driver.byte_expr(os.fsencode(path)) + ','
               + driver.driver.byte_expr(os.fsencode(driver.ROOT)) + ')')
    checks = ['S_initial = ' + initial, '~S_initial.COMPILESTOP']
    checks += base.seek('S_store', 'S_initial', 60) + valid('S_store')
    checks += r'''
$destructor_handle(S_store,S_store.DESTRUCTION.INDEX,0) = (n_generator)
n_handle = S_store.DESTRUCTION.INDEX
S_store.OBJECTS[n_generator] = GENERATOR pgenerator_store
pgenerator_store.PHASE = GENERATOR_FRESH
pgenerator_store.FRAME = (pframe_store)
pframe_store.CONTEXT = (pcallcontext_store)
$generator_record_valid(S_store,pgenerator_store)
$generator_destructor_pending(S_store,HOBJECT n_generator)
$generator_request_store_ready(S_store,n_generator)
~(n_generator <- S_store.DESTRUCTION.CALLED)
$heap_owners($heap_graph(S_store),HOBJECT n_generator) = 1
$close_outputs(S_store.EVENTS) = $ptascii("C|")
S_queued_budget = $drive_steps(S_store,1)
S_queued_budget.COMPLETION = BUDGET
S_queued = S_queued_budget[.COMPLETION = NORMAL]
S_queued.TODO = [GENERATOR_CLOSE_RELEASE pgenrelease, GENERATOR_CLOSE_DONE pgenclose, DESTRUCTOR_STORE]
pgenclose.OBJECT = n_generator /\ pgenclose.STORE = (n_handle)
pgenclose.SITE = pgenerator_store.FUNCTION /\ pgenclose.CONTEXT = pcallcontext_store
pgenclose.STAGE = CLOSE_FINISHED /\ pgenclose.FRAME = eps /\ pgenclose.NEXT = 0
pgenclose.CALLER = eps /\ pgenclose.CALLSITE = eps /\ pgenclose.PENDING = eps
S_queued.OBJECTS[n_generator] = GENERATOR pgenerator_closed
$generator_request_fresh_closed(pgenerator_closed)
$generator_close_done_site(S_queued,pgenerator_closed,pgenclose)
$generator_close_done_valid(S_queued,pgenclose)
S_queued.DESTRUCTION.INDEX = $(n_handle + 1)
n_generator <- S_queued.DESTRUCTION.CALLED
$heap_owners($heap_graph(S_queued),HOBJECT n_generator) = 2
$generator_close_claims(S_queued.TODO) = [n_generator]
pgenrelease.JOBS = $destruction_values($destruction_nodes_delete($generator_close_frame_nodes(S_store,pframe_store),$generator_closed_closure(pgenerator_closed)))
$close_outputs(S_queued.EVENTS) = $ptascii("C|")
'''.strip().splitlines()
    checks += valid('S_queued')
    if name == 'fresh-pure-request-activation':
        checks += ['~$destructor_classes(S_store.CLASSES)', 'S_store.FIBERSEQ = 1',
                   '$generator_request_fresh_any(S_store,S_store.ALLOCATIONS)',
                   'pgenrelease.JOBS = eps',
                   'pgenerator_store.FUNCTION = PORIGIN n_unit pcpath_function',
                   'porigin_unexecuted_yield = PORIGIN n_unit (pcpath_function ++ [PCFIELD 5, PCINDEX 1, PCFIELD 0, PCINDEX 0, PCFIELD 0])',
                   '$generator_close_site(S_queued,pgenerator_closed,porigin_unexecuted_yield)']
        for suffix, marker in [
            ('unexecuted_yield_site', 'pgenclose[.SITE = porigin_unexecuted_yield]'),
            ('wrong_handle', 'pgenclose[.STORE = ($(n_handle + 1))]'),
            ('missing_store', 'pgenclose[.STORE = eps]'),
            ('wrong_next', 'pgenclose[.NEXT = 1]'),
        ]:
            reject(checks, suffix, f'S_queued[.TODO = [GENERATOR_CLOSE_RELEASE pgenrelease, GENERATOR_CLOSE_DONE {marker}, DESTRUCTOR_STORE]]', 'S_queued')
        reject(checks, 'unprocessed_handle', 'S_queued[.DESTRUCTION.INDEX = n_handle]', 'S_queued')
        reject(checks, 'missing_called', 'S_queued[.DESTRUCTION.CALLED = $request_called_drop(S_queued.DESTRUCTION.CALLED,n_generator)]', 'S_queued')
        reject(checks, 'duplicate_claim', 'S_queued[.TODO = [GENERATOR_CLOSE_RELEASE pgenrelease, GENERATOR_CLOSE_DONE pgenclose, GENERATOR_CLOSE_DONE pgenclose, DESTRUCTOR_STORE]]', 'S_queued', same_heap=False)
    elif name == 'fresh-self-reference-becomes-borrowed-store-bucket':
        checks += ['$generator_frame_scope(S_store,pframe_store) = S_frame',
                   '$lookup(S_frame.ENV,$ptascii("self")) = (n_self)',
                   'n_self <- S_store.REFCELLS',
                   'S_store.STORE[n_self] = DEFINED (POBJECT n_generator)',
                   '$heap_owners($heap_graph(S_store),HCELL n_self) = 1',
                   'pgenrelease.JOBS = [DESTRUCTION_VALUE (HCELL n_self)]']
        checks += base.seek('S_done', 'S_queued', 62) + valid('S_done')
        checks += ['$heap_owners($heap_graph(S_done),HOBJECT n_generator) = 1',
                   '~((HCELL n_self) <- S_done.ALLOCATIONS)']
        checks += base.seek('S_retired', 'S_done', 64) + valid('S_retired')
        checks += ['S_retired.DESTRUCTION.RETIRED = [(n_generator,n_handle)]',
                   '(HOBJECT n_generator) <- S_retired.ALLOCATIONS',
                   '$generator_request_retired_state_valid(S_retired)',
                   'S_globals = $global_table_view(S_retired)',
                   '$trace_slot(S_globals,S_globals.ENV,$ptascii("w")) = POBJECT n_weak',
                   '$weakref_get(S_retired,n_weak) = POBJECT n_generator']
    elif name == 'fresh-closure-owner-survives-frame-retirement':
        checks += ['pgenerator_store.CLOSURE = (n_closure)',
                   '$heap_owners($heap_graph(S_store),HOBJECT n_closure) = 1',
                   '$heap_owners($heap_graph(S_queued),HOBJECT n_closure) = 1',
                   '~((HOBJECT n_closure) <- $destruction_job_nodes(pgenrelease.JOBS))',
                   '$generator_closed_closure(pgenerator_closed) = [HOBJECT n_closure]']
    else:
        checks += ['$generator_frame_scope(S_store,pframe_store) = S_frame',
                   '$trace_slot(S_frame,S_frame.ENV,$ptascii("second")) = POBJECT n_second']
        checks += base.seek('S_destructor', 'S_queued', 61) + valid('S_destructor')
        checks += ['S_destructor.FRAMES = [pframe_destructor]',
                   'pframe_destructor.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: ptask_destructor_tail*',
                   '$generator_request_tail_task(DESTRUCTOR_RESULT pdestructorcall)',
                   '$generator_request_store_tail(pframe_destructor.TODO)',
                   'S_destructor.OBJECTS[n_generator] = GENERATOR pgenerator_closed',
                   '$generator_request_fresh_closed(pgenerator_closed)',
                   '$heap_owners($heap_graph(S_destructor),HOBJECT n_generator) = 2',
                   '$heap_owners($heap_graph(S_destructor),HOBJECT n_second) = 1']
        checks += base.seek('S_handler', 'S_destructor', 63) + valid('S_handler')
        checks += ['S_handler.FRAMES = [pframe_handler]',
                   'pframe_handler.CONTEXT = eps',
                   'pframe_handler.TODO = (EXCEPTION_HANDLER_RESULT pexceptioncall) :: (DESTRUCTOR_RESULT pdestructorcall) :: ptask_handler_tail*',
                   '$exception_result_valid(S_handler,pexceptioncall)',
                   '$destructor_call_tail(pframe_handler.TODO,pdestructorcall) = (ptask_handler_tail*)',
                   '$destructor_call_pending_valid(S_handler,pdestructorcall)',
                   'S_handler.OBJECTS[n_generator] = GENERATOR pgenerator_closed',
                   '$generator_request_fresh_closed(pgenerator_closed)',
                   '$heap_owners($heap_graph(S_handler),HOBJECT n_generator) = 2',
                   '$heap_owners($heap_graph(S_handler),HOBJECT n_second) = 1',
                   '(HOBJECT n_second) <- S_handler.ALLOCATIONS',
                   '~(n_second <- S_handler.DESTRUCTION.CALLED)',
                   'S_handler.DESTRUCTION.CALLS = pdestructorcall :: pdestructorcall_tail*',
                   r'~pdestructorcall.USER /\ pdestructorcall.CALLER = eps',
                   r'pdestructorcall.FRAME = eps /\ pdestructorcall.OPERATION = eps',
                   '$close_outputs(S_handler.EVENTS) = $ptascii("C|A")']
        checks += ['pdestructorcall_user = pdestructorcall[.USER = true]',
                   '$destructor_call_tail((EXCEPTION_HANDLER_RESULT pexceptioncall) :: (DESTRUCTOR_RESULT pdestructorcall_user) :: ptask_handler_tail*,pdestructorcall) = eps',
                   '$destructor_call_tail((EXCEPTION_HANDLER_RESULT pexceptioncall) :: (DESTRUCTOR_RESULT pdestructorcall_user) :: ptask_handler_tail*,pdestructorcall_user) = eps',
                   '~$generator_request_tail_task(DESTRUCTOR_RESULT pdestructorcall_user)']
        reject(checks, 'handler_user',
               'S_handler[.FRAMES = [pframe_handler[.TODO = (EXCEPTION_HANDLER_RESULT pexceptioncall) :: (DESTRUCTOR_RESULT pdestructorcall_user) :: ptask_handler_tail*]]]',
               'S_handler')
        reject(checks, 'handler_wrong_throwable',
               'S_handler[.FRAMES = [pframe_handler[.TODO = (EXCEPTION_HANDLER_RESULT (pexceptioncall[.OBJECT = n_second])) :: (DESTRUCTOR_RESULT pdestructorcall) :: ptask_handler_tail*]]]',
               'S_handler', same_heap=False)
    base.finish(checks, 'S_queued', name)
    if name == 'fresh-self-reference-becomes-borrowed-store-bucket':
        checks += ['S_resumed.DESTRUCTION.RETIRED = eps',
                   '~((HOBJECT n_generator) <- S_resumed.ALLOCATIONS)',
                   '$weakref_get(S_resumed,n_weak) = PNULL']
    else:
        checks += ['S_resumed.OBJECTS[n_generator] = GENERATOR pgenerator_closed',
                   '(HOBJECT n_generator) <- S_resumed.ALLOCATIONS',
                   '$heap_owners($heap_graph(S_resumed),HOBJECT n_generator) = 1']
    return checks


def main():
    base.CASES = CASES
    driver.CASES = CASES
    driver.PREFIX += base.PREFIX + PREFIX
    driver.assertions = assertions
    driver.source.WATCHED = author.driver.WATCHED + [
        'spec/semantics/222-exception-handlers.watsup',
        'spec/semantics/270-eager-destructors.watsup',
        'spec/semantics/296-weak-references.watsup',
        'spec/semantics/328-generator-reference-yields.watsup',
        'spec/semantics/340-generator-request-finally.watsup',
        'spec/semantics/349-generator-request-fresh.watsup',
        'tests/semantics/generator_request_fresh_sources.py',
        'tests/semantics/generator_request_fresh_peer_sources.py',
        'tests/semantics/generator_request_finally_protocol.py',
        'tests/semantics/generator_request_fresh_protocol.py',
        'tests/semantics/reference_yield_protocol.py',
    ]
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())
