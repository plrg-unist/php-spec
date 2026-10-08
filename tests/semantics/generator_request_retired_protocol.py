#!/usr/bin/env python3
"""Real bare store decrements, borrowed buckets and ordinary reacquisition free."""
import os

import generator_request_finally_protocol as base
import generator_request_finally_peer_sources as peer
from reference_yield_protocol import valid, reject

driver = base.driver
CASES = {
    'request-store-retired-reacquisition': peer.CASES['peer-request-store-reacquisition-later-release-frees-bucket'],
    'request-store-retired-handler-resume': peer.CASES['peer-request-handler-resume-keeps-zero-owner-bucket'],
}
PREFIX = r'''
def $request_finally_phase(S,50) = true
  -- if S.DESTRUCTION.RETIRED = [(n_generator,n_handle)]
  -- if $heap_owners($heap_graph(S),HOBJECT n_generator) = 0
def $request_finally_phase(S,51) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $trace_context_function(S,pcallcontext) = $ptascii("__destruct")
  -- if $lookup(S.ENV,$ptascii("h")) = (n_cell)
  -- if S.STORE[n_cell] = DEFINED (POBJECT n_generator)
  -- if S.OBJECTS[n_generator] = GENERATOR pgenerator
  -- if S.DESTRUCTION.RETIRED = eps
def $request_finally_phase(S,52) = true
  -- if S_globals = $global_table_view(S)
  -- if $trace_slot(S_globals,S_globals.ENV,$ptascii("w")) = POBJECT n_weak
  -- if S.OBJECTS[n_weak] = WEAKREFERENCE (n_generator)
  -- if ~((HOBJECT n_generator) <- S.ALLOCATIONS)
  -- if S.OBJECTS[n_generator] = GENERATOR pgenerator
  -- if pgenerator.VALUE = (POBJECT n_payload)
  -- if ~((HOBJECT n_payload) <- S.ALLOCATIONS)
'''


def assertions(checked, path, directory, name):
    initial = ('$php_file_run(' + checked['fixture'] + ',0,'
               + driver.driver.byte_expr(os.fsencode(path)) + ','
               + driver.driver.byte_expr(os.fsencode(driver.ROOT)) + ')')
    checks = ['S_initial = ' + initial, '~S_initial.COMPILESTOP']
    checks += base.seek('S_store', 'S_initial', 10) + valid('S_store')
    checks += r'''
S_globals = $global_table_view(S_store)
$trace_slot(S_globals,S_globals.ENV,$ptascii("w")) = POBJECT n_weak
$weakref_get(S_store,n_weak) = POBJECT n_generator
$destructor_handle(S_store,S_store.DESTRUCTION.INDEX,0) = (n_generator)
n_handle = S_store.DESTRUCTION.INDEX
S_store.OBJECTS[n_generator] = GENERATOR pgenerator_store
pgenerator_store.VALUE = (POBJECT n_payload)
$heap_owners($heap_graph(S_store),HOBJECT n_generator) = 1
$heap_owners($heap_graph(S_store),HOBJECT n_payload) = 1
S_store.DESTRUCTION.RETIRED = eps
'''.strip().splitlines()
    checks += base.seek('S_queued', 'S_store', 11) + valid('S_queued')
    checks += ['$heap_owners($heap_graph(S_queued),HOBJECT n_generator) = 2']
    if name == 'request-store-retired-handler-resume':
        checks += base.seek('S_pending', 'S_queued', 20) + valid('S_pending')
        checks += ['S_pending.TODO = (GENERATOR_CLOSE_DONE pgenclose_pending) :: ptask_pending*',
                   'pgenclose_pending.PENDING = (n_exception)',
                   'pgenclose_pending.STORE = (n_handle)']
        checks += base.seek('S_transfer', 'S_pending', 21) + valid('S_transfer')
        checks += ['$generator_close_claims(S_transfer.TODO) = [n_generator]',
                   '$heap_owners($heap_graph(S_transfer),HOBJECT n_generator) = 1',
                   '$heap_owners($heap_graph(S_transfer),HOBJECT n_payload) = 1']
        checks += base.seek('S_closed', 'S_transfer', 23) + valid('S_closed')
        checks += ['S_closed.TODO = (GENERATOR_REQUEST_RESUME pgenclose_closed) :: ptask_closed*',
                   'pgenclose_closed.STORE = (n_handle)',
                   '$generator_request_resume_valid(S_closed,pgenclose_closed)',
                   '$close_outputs(S_closed.EVENTS) = $ptascii("C|FH")']
    else:
        checks += base.seek('S_closed', 'S_queued', 5) + valid('S_closed')
        checks += ['S_closed.TODO = (GENERATOR_CLOSE_DONE pgenclose_closed) :: ptask_closed*',
                   'pgenclose_closed.STORE = (n_handle)',
                   '$close_outputs(S_closed.EVENTS) = $ptascii("C|F")']
    checks += r'''
S_closed.OBJECTS[n_generator] = GENERATOR pgenerator_closed
pgenerator_closed.PHASE = GENERATOR_CLOSED /\ pgenerator_closed.FRAME = eps
pgenerator_closed.VALUE = (POBJECT n_payload)
$heap_owners($heap_graph(S_closed),HOBJECT n_generator) = 1
$heap_owners($heap_graph(S_closed),HOBJECT n_payload) = 1
S_dropped = S_closed[.TODO = ptask_closed*]
$heap_owners($heap_graph(S_dropped),HOBJECT n_generator) = 0
S_retired_budget = $drive_steps(S_closed,1)
S_retired_budget.COMPLETION = BUDGET
S_retired = S_retired_budget[.COMPLETION = NORMAL]
$request_finally_phase(S_retired,50)
S_retired.DESTRUCTION.RETIRED = [(n_generator,n_handle)]
S_retired.OBJECTS[n_generator] = GENERATOR pgenerator_closed
(HOBJECT n_generator) <- S_retired.ALLOCATIONS
$heap_owners($heap_graph(S_retired),HOBJECT n_generator) = 0
$heap_owners($heap_graph(S_retired),HOBJECT n_payload) = 1
$heap_graph(S_retired) = $heap_graph(S_dropped)
$weakref_get(S_retired,n_weak) = POBJECT n_generator
(HOBJECT n_generator) <- $gc_prune_nodes(S_retired)
(HOBJECT n_payload) <- $generator_request_retired_keep(S_retired)
$generator_request_retired_state_valid(S_retired)
S_erased = S_retired[.DESTRUCTION.RETIRED = eps]
$heap_graph(S_erased) = $heap_graph(S_retired)
~((HOBJECT n_generator) <- $gc_prune_nodes(S_erased))
'''.strip().splitlines()
    checks += valid('S_retired')
    for suffix, expression in [
        ('wrong_handle', 'S_retired[.DESTRUCTION.RETIRED = [(n_generator,$(n_handle + 1))]]'),
        ('unprocessed_index', 'S_retired[.DESTRUCTION.INDEX = n_handle]'),
        ('missing_called', 'S_retired[.DESTRUCTION.CALLED = $request_called_drop(S_retired.DESTRUCTION.CALLED,n_generator)]'),
        ('wrong_phase', 'S_retired[.DESTRUCTION.PHASE = DESTRUCTION_GLOBALS]'),
        ('duplicate_bucket', 'S_retired[.DESTRUCTION.RETIRED = [(n_generator,n_handle),(n_generator,n_handle)]]'),
    ]:
        reject(checks, suffix, expression, 'S_retired')
        checks += [f'~$generator_request_retired_state_valid(S_bad_{suffix})']
    reject(checks, 'invented_owner', 'S_retired[.HELD = [HOBJECT n_generator]]', 'S_retired', same_heap=False)
    checks += ['~$generator_request_retired_state_valid(S_bad_invented_owner)',
               '$heap_owners($heap_graph(S_bad_invented_owner),HOBJECT n_generator) = 1']
    checks += base.seek('S_acquired', 'S_retired', 51) + valid('S_acquired')
    checks += ['S_acquired.DESTRUCTION.RETIRED = eps',
               '$( $heap_owners($heap_graph(S_acquired),HOBJECT n_generator) > 0 )',
               '$weakref_get(S_acquired,n_weak) = POBJECT n_generator',
               'S_acquired.OBJECTS[n_generator] = GENERATOR pgenerator_closed',
               '(HOBJECT n_payload) <- S_acquired.ALLOCATIONS',
               'n_payload <- S_acquired.DESTRUCTION.CALLED']
    checks += base.seek('S_freed', 'S_acquired', 52) + valid('S_freed')
    checks += ['S_freed.DESTRUCTION.RETIRED = eps',
               '$weakref_get(S_freed,n_weak) = PNULL',
               '~((HOBJECT n_payload) <- S_freed.ALLOCATIONS)']
    base.finish(checks, 'S_retired', name)
    checks += ['S_resumed.DESTRUCTION.RETIRED = eps',
               '$weakref_get(S_resumed,n_weak) = PNULL',
               '~((HOBJECT n_generator) <- S_resumed.ALLOCATIONS)',
               '~((HOBJECT n_payload) <- S_resumed.ALLOCATIONS)']
    return checks


def main():
    base.CASES = CASES
    driver.CASES = CASES
    driver.PREFIX += base.PREFIX + PREFIX
    driver.assertions = assertions
    driver.source.WATCHED = base.author.WATCHED + [
        'spec/semantics/296-weak-references.watsup',
        'spec/semantics/325-detached-collector-roots.watsup',
        'tests/semantics/generator_force_close_protocol.py',
        'tests/semantics/reference_yield_protocol.py',
        'tests/semantics/generator_request_finally_protocol.py',
        'tests/semantics/generator_request_retired_protocol.py',
    ]
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())
