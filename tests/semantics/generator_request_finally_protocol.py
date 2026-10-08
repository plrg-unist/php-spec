#!/usr/bin/env python3
"""Normal request-close frontiers; fatal continuations are checked by363."""
import os

import generator_force_close_protocol as driver
import generator_request_finally_sources as author
import generator_request_finally_peer_sources as peer
from reference_yield_protocol import valid, reject

CASES = {
    'request-global-reference-finally': author.CASES['reference-terminal-active-finally-required'],
    'request-store-cache-retained': peer.CASES['peer-request-store-close-retains-cache'],
    'request-handler-before-cache': peer.CASES['peer-request-handler-before-cache-retirement'],
}
PREFIX = r'''
dec $request_called_drop(nat*,nat) : nat*
def $request_called_drop(eps,n) = eps
def $request_called_drop(n :: nat_tail*,n) = $request_called_drop(nat_tail*,n)
def $request_called_drop(n_head :: nat_tail*,n) = n_head :: $request_called_drop(nat_tail*,n) -- if n_head =/= n
dec $request_finally_phase(pstate,nat) : bool
def $request_finally_phase(S,0) = true
  -- if S.TODO = (EMIT z) :: ptask*
  -- if S.RESULT = KNOWN (PSTRING ($ptascii("|")))
  -- if $close_outputs(S.EVENTS) = $ptascii("C|7")
def $request_finally_phase(S,1) = (S.TODO = [DESTRUCTOR_GLOBALS])
def $request_finally_phase(S,2) = true
  -- if S.TODO = [DESTRUCTOR_RELEASE pdestructionrelease, DESTRUCTOR_GLOBALS]
  -- if pdestructionrelease.JOBS = (DESTRUCTION_VALUE (HOBJECT n)) :: pdestructionjob*
  -- if $generator_destructor_request_ready(S,pdestructionrelease,HOBJECT n)
def $request_finally_phase(S,3) = true
  -- if S.TODO = (GENERATOR_CLOSE_ENTER pgenclose) :: ptask*
  -- if pgenclose.STORE = eps
def $request_finally_phase(S,4) = true
  -- if $generator_close_saved(S,S.CURRENT,S.FRAMES) = (pgenclose)
  -- if pgenclose.STAGE = CLOSE_BODY porigin
def $request_finally_phase(S,5) = true
  -- if S.TODO = (GENERATOR_CLOSE_DONE pgenclose) :: ptask*
  -- if pgenclose.STAGE = CLOSE_FINISHED
  -- if pgenclose.PENDING = eps
def $request_finally_phase(S,10) = true
  -- if S.TODO = [DESTRUCTOR_STORE]
  -- if $destructor_handle(S,S.DESTRUCTION.INDEX,0) = (n)
  -- if $generator_request_store_ready(S,n)
def $request_finally_phase(S,11) = true
  -- if S.TODO = (GENERATOR_CLOSE_ENTER pgenclose) :: ptask*
  -- if pgenclose.STORE = (n_handle)
def $request_finally_phase(S,20) = true
  -- if S.TODO = (GENERATOR_CLOSE_DONE pgenclose) :: ptask*
  -- if $generator_request_done_pending(S,pgenclose)
def $request_finally_phase(S,21) = true
  -- if S.TODO = (THROW_SEARCH n) :: (GENERATOR_REQUEST_RESUME pgenclose) :: ptask*
  -- if $exception_dispatch_ready(S)
def $request_finally_phase(S,22) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $trace_context_function(S,pcallcontext) = $ptascii("caught340")
  -- if $exception_context_call(S,pcallcontext) = (pexceptioncall)
def $request_finally_phase(S,23) = true
  -- if S.TODO = (GENERATOR_REQUEST_RESUME pgenclose) :: ptask*
def $request_finally_phase(S,n) = false -- otherwise
dec $request_finally_finished(pstate) : bool
def $request_finally_finished(S) = (S.TODO = eps /\ S.FRAMES = eps /\ S.DESTRUCTION.PHASE = DESTRUCTION_DONE)
dec $request_finally_seek(pstate,nat,nat) : pstate
def $request_finally_seek(S,n_phase,n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $request_finally_seek(S,n_phase,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $request_finally_phase(S[.COMPLETION = NORMAL],n_phase)
def $request_finally_seek(S,n_phase,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$request_finally_phase(S[.COMPLETION = NORMAL],n_phase)
  -- if n = 0 \/ $request_finally_finished(S)
def $request_finally_seek(S,n_phase,n) = $request_finally_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_phase,$nabs($(n - 1)))
  -- if ~$request_finally_phase(S[.COMPLETION = NORMAL],n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
  -- if ~$request_finally_finished(S)
'''


def seek(state, previous, phase):
    return [f'{state}_found = $request_finally_seek({previous},{phase},4096)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$request_finally_phase({state},{phase})']


def finish(checks, previous, name):
    checks += [f'S_stopped = $drive_steps({previous},0)',
               f'S_stopped = {previous}[.COMPLETION = BUDGET]',
               'S_resumed = $drive(S_stopped[.COMPLETION = NORMAL],4096)',
               f'S_direct = $drive({previous},4096)', 'S_resumed = S_direct',
               'S_resumed.COMPLETION = NORMAL', 'S_resumed.TODO = eps',
               'S_resumed.FRAMES = eps', 'S_resumed.DESTRUCTION.PHASE = DESTRUCTION_DONE',
               '$generator_close_claims(S_resumed.TODO) = eps',
               '$close_outputs_only(S_resumed.EVENTS)',
               '$close_outputs(S_resumed.EVENTS) = ' + driver.driver.byte_expr(CASES[name][1])]
    checks += valid('S_resumed')


def assertions(checked, path, directory, name):
    initial = ('$php_file_run(' + checked['fixture'] + ',0,'
               + driver.driver.byte_expr(os.fsencode(path)) + ','
               + driver.driver.byte_expr(os.fsencode(driver.ROOT)) + ')')
    checks = ['S_initial = ' + initial, '~S_initial.COMPILESTOP']
    if name == 'request-global-reference-finally':
        checks += seek('S_terminal', 'S_initial', 0) + valid('S_terminal')
        checks += r'''
$trace_slot(S_terminal,S_terminal.ENV,$ptascii("generator")) = POBJECT n_generator
$lookup(S_terminal.ENV,$ptascii("value")) = (n_cell)
S_terminal.OBJECTS[n_generator] = GENERATOR pgenerator_terminal
pgenerator_terminal.REFCELL = (n_cell) /\ pgenerator_terminal.VALUE = eps
pgenerator_terminal.FRAME = (pframe_terminal)
$getclass_live_object(S_terminal,n_generator)
~$getclass_live_object(S_terminal[.ALLOCATIONS = $destruction_node_delete(S_terminal.ALLOCATIONS,HOBJECT n_generator)],n_generator)
~$getclass_live_object(S_terminal,|S_terminal.OBJECTS|)
pframe_terminal.ORIGIN = (porigin_terminal)
|$generator_close_regions(S_terminal,porigin_terminal)| = 1
$generator_finalizer_frame(S_terminal,pgenerator_terminal.FRAME)
'''.strip().splitlines()
        checks += seek('S_globals', 'S_terminal', 1) + valid('S_globals')
        checks += ['$heap_owners($heap_graph(S_globals),HOBJECT n_generator) = 1',
                   'S_globals.SHUTDOWN.PHASE = SHUTDOWN_DONE',
                   'S_globals.DESTRUCTION.PHASE = DESTRUCTION_GLOBALS']
        checks += seek('S_release', 'S_globals', 2) + valid('S_release')
        checks += r'''
S_release.TODO = [DESTRUCTOR_RELEASE pdestructionrelease, DESTRUCTOR_GLOBALS]
pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_generator)]
~pdestructionrelease.USER
$lookup(S_release.ENV,$ptascii("generator")) = eps
$heap_owners($heap_graph(S_release),HOBJECT n_generator) = 1
S_unheld = $destructor_release_replace(S_release,pdestructionrelease[.JOBS = eps])
$heap_owners($heap_graph(S_unheld),HOBJECT n_generator) = 0
'''.strip().splitlines()
        checks += seek('S_queued', 'S_release', 3) + valid('S_queued')
        checks += ['S_queued.TODO = (GENERATOR_CLOSE_ENTER pgenclose_queued) :: ptask_queued*',
                   'pgenclose_queued.OBJECT = n_generator', 'pgenclose_queued.STORE = eps',
                   '$generator_close_enter_valid(S_queued,pgenclose_queued)']
        reject(checks, 'invented_store', 'S_queued[.TODO = (GENERATOR_CLOSE_ENTER pgenclose_queued[.STORE = (1)]) :: ptask_queued*]', 'S_queued')
        checks += seek('S_body', 'S_queued', 4) + valid('S_body')
        checks += ['$generator_close_saved(S_body,S_body.CURRENT,S_body.FRAMES) = (pgenclose_body)',
                   'pgenclose_body.NEXT = 1', 'pgenclose_body.STORE = eps',
                   'S_body.OBJECTS[n_generator] = GENERATOR pgenerator_body',
                   'pgenerator_body.PHASE = GENERATOR_RUNNING',
                   r'pgenerator_body.FRAME = eps /\ pgenerator_body.REFCELL = (n_cell)']
        checks += seek('S_closed', 'S_body', 5) + valid('S_closed')
        checks += ['S_closed.OBJECTS[n_generator] = GENERATOR pgenerator_closed',
                   'pgenerator_closed.PHASE = GENERATOR_CLOSED',
                   'pgenerator_closed.REFCELL = (n_cell)',
                   'S_closed.STORE[n_cell] = DEFINED (PINT 7)']
        finish(checks, 'S_closed', name)
        checks += ['~((HOBJECT n_generator) <- S_resumed.ALLOCATIONS)',
                   '~$getclass_live_object(S_resumed,n_generator)',
                   'S_resumed.STORE[n_cell] = DEFINED (PINT 7)',
                   '$heap_owners($heap_graph(S_resumed),HCELL n_cell) = 1']
    elif name == 'request-store-cache-retained':
        checks += seek('S_store', 'S_initial', 10) + valid('S_store')
        checks += r'''
$trace_slot(S_store,S_store.ENV,$ptascii("g")) = POBJECT n_generator
$destructor_handle(S_store,S_store.DESTRUCTION.INDEX,0) = (n_generator)
n_handle = S_store.DESTRUCTION.INDEX
~(n_generator <- S_store.DESTRUCTION.CALLED)
S_store.OBJECTS[n_generator] = GENERATOR pgenerator_store
pgenerator_store.VALUE = (POBJECT n_payload)
pgenerator_store.REFCELL = eps
$heap_owners($heap_graph(S_store),HOBJECT n_generator) = 1
$heap_owners($heap_graph(S_store),HOBJECT n_payload) = 1
'''.strip().splitlines()
        checks += seek('S_queued', 'S_store', 11) + valid('S_queued')
        checks += r'''
S_queued.TODO = (GENERATOR_CLOSE_ENTER pgenclose_queued) :: ptask_queued*
pgenclose_queued.OBJECT = n_generator /\ pgenclose_queued.STORE = (n_handle)
S_queued.DESTRUCTION.INDEX = $(n_handle + 1)
n_generator <- S_queued.DESTRUCTION.CALLED
$heap_owners($heap_graph(S_queued),HOBJECT n_generator) = 2
$heap_owners($heap_graph(S_queued),HOBJECT n_payload) = 1
$generator_close_enter_valid(S_queued,pgenclose_queued)
'''.strip().splitlines()
        reject(checks, 'erased_store', 'S_queued[.TODO = (GENERATOR_CLOSE_ENTER pgenclose_queued[.STORE = eps]) :: ptask_queued*]', 'S_queued')
        reject(checks, 'wrong_handle', 'S_queued[.TODO = (GENERATOR_CLOSE_ENTER pgenclose_queued[.STORE = ($(n_handle + 1))]) :: ptask_queued*]', 'S_queued')
        reject(checks, 'missing_called', 'S_queued[.DESTRUCTION.CALLED = $request_called_drop(S_queued.DESTRUCTION.CALLED,n_generator)]', 'S_queued')
        checks += seek('S_closed', 'S_queued', 5) + valid('S_closed')
        checks += ['S_closed.OBJECTS[n_generator] = GENERATOR pgenerator_closed',
                   r'pgenerator_closed.PHASE = GENERATOR_CLOSED /\ pgenerator_closed.FRAME = eps',
                   'pgenerator_closed.VALUE = (POBJECT n_payload)',
                   '$heap_owners($heap_graph(S_closed),HOBJECT n_payload) = 1']
        finish(checks, 'S_closed', name)
        checks += ['(HOBJECT n_generator) <- S_resumed.ALLOCATIONS',
                   '(HOBJECT n_payload) <- S_resumed.ALLOCATIONS',
                   'n_payload <- S_resumed.DESTRUCTION.CALLED',
                   '$heap_owners($heap_graph(S_resumed),HOBJECT n_generator) = 1',
                   '$heap_owners($heap_graph(S_resumed),HOBJECT n_payload) = 1']
    else:
        checks += seek('S_pending', 'S_initial', 20) + valid('S_pending')
        checks += r'''
S_pending.TODO = (GENERATOR_CLOSE_DONE pgenclose_pending) :: ptask_pending*
pgenclose_pending.PENDING = (n_exception)
n_generator = pgenclose_pending.OBJECT
S_pending.OBJECTS[n_generator] = GENERATOR pgenerator_pending
pgenerator_pending.PHASE = GENERATOR_CLOSED /\ pgenerator_pending.FRAME = eps
S_pending.DESTRUCTION.OPERATIONS = eps /\ S_pending.DESTRUCTION.FRAMES = eps
$heap_owners($heap_graph(S_pending),HOBJECT n_generator) = 1
$throwable_field(S_pending,n_exception,"message") = PSTRING $ptascii("new")
'''.strip().splitlines()
        checks += seek('S_transfer', 'S_pending', 21) + valid('S_transfer')
        checks += r'''
S_transfer.TODO = (THROW_SEARCH n_exception) :: (GENERATOR_REQUEST_RESUME pgenclose_transfer) :: ptask_transfer*
pgenclose_transfer.OBJECT = n_generator /\ pgenclose_transfer.PENDING = eps
$generator_close_claims(S_transfer.TODO) = [n_generator]
H_pending = $heap_graph(S_pending)
H_transfer = $heap_graph(S_transfer)
H_transfer.NODES = H_pending.NODES /\ H_transfer.EDGES = H_pending.EDGES
$heap_owners(H_transfer,HOBJECT n_generator) = 1
$heap_owners(H_transfer,HOBJECT n_exception) = $heap_owners(H_pending,HOBJECT n_exception)
$generator_request_resume_valid(S_transfer,pgenclose_transfer)
'''.strip().splitlines()
        reject(checks, 'reordered_resume', 'S_transfer[.TODO = (GENERATOR_REQUEST_RESUME pgenclose_transfer) :: (THROW_SEARCH n_exception) :: ptask_transfer*]', 'S_transfer', same_heap=False)
        checks += ['$heap_owners($heap_graph(S_bad_reordered_resume),HOBJECT n_generator) = 1',
                   '$heap_owners($heap_graph(S_bad_reordered_resume),HOBJECT n_exception) = $heap_owners(H_transfer,HOBJECT n_exception)']
        reject(checks, 'duplicate_resume', 'S_transfer[.TODO = (THROW_SEARCH n_exception) :: (GENERATOR_REQUEST_RESUME pgenclose_transfer) :: (GENERATOR_REQUEST_RESUME pgenclose_transfer) :: ptask_transfer*]', 'S_transfer', same_heap=False)
        checks += ['pgenerator_pending.VALUE = (POBJECT n_payload)',
                   '$heap_owners($heap_graph(S_transfer),HOBJECT n_payload) = 1']
        checks += seek('S_handler', 'S_transfer', 22) + valid('S_handler')
        checks += ['S_handler.OBJECTS[n_generator] = GENERATOR pgenerator_pending',
                   '(HOBJECT n_payload) <- S_handler.ALLOCATIONS',
                   '~(n_payload <- S_handler.DESTRUCTION.CALLED)',
                   '$heap_owners($heap_graph(S_handler),HOBJECT n_payload) = 1']
        checks += seek('S_resume', 'S_handler', 23) + valid('S_resume')
        checks += ['S_resume.TODO = (GENERATOR_REQUEST_RESUME pgenclose_resume) :: ptask_resume*',
                   '$generator_request_resume_valid(S_resume,pgenclose_resume)',
                   '$heap_owners($heap_graph(S_resume),HOBJECT n_generator) = 1',
                   '$heap_owners($heap_graph(S_resume),HOBJECT n_payload) = 1',
                   '$close_outputs(S_resume.EVENTS) = $ptascii("C|FH1|")']
        finish(checks, 'S_resume', name)
        checks += ['~((HOBJECT n_generator) <- S_resumed.ALLOCATIONS)',
                   '~((HOBJECT n_payload) <- S_resumed.ALLOCATIONS)']
    return checks


def main():
    driver.CASES = CASES
    driver.NATIVE_ERROR_PREFIXES = {}
    driver.PREFIX += PREFIX
    driver.assertions = assertions
    driver.source.WATCHED = author.WATCHED + [
        'tests/semantics/generator_force_close_protocol.py',
        'tests/semantics/reference_yield_protocol.py',
        'tests/semantics/generator_request_finally_protocol.py',
    ]
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())
