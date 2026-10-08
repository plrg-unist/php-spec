#!/usr/bin/env python3
"""Real delayed-CV retirement and non-finalizing request cache release."""
import os

import generator_force_close_protocol as driver
import reference_yield_prepare as author
import reference_yield_terminal_review as terminal

CASES = {
    'delayed-cv-terminal-reference-cache': author.CASES['readonly-reference-fetch-precedes-old-cache-release'],
    'notice-terminal-value-cache': author.CASES['handler-retval-retirement-keeps-key-and-notice-ingress'],
    'terminal-active-finally-refused': (
        terminal.UNSUPPORTED['reference-terminal-active-finally-required'][0],
        terminal.UNSUPPORTED['reference-terminal-active-finally-required'][1], 0),
}
WATCHED = driver.source.WATCHED + [
    'spec/semantics/97-call-reference-acquisition.watsup',
    'spec/semantics/99-reference-returns.watsup',
    'spec/semantics/118-arrows.watsup',
    'spec/semantics/207-error-handler-runtime.watsup',
    'spec/semantics/270-eager-destructors.watsup',
    'spec/semantics/311-arrow-generators.watsup',
    'spec/semantics/321-yield-key-warning.watsup',
    'spec/semantics/328-generator-reference-yields.watsup',
    'tests/semantics/reference_yield_prepare.py',
    'tests/semantics/reference_yield_terminal_review.py',
    'tests/semantics/reference_yield_terminal_protocol.py',
]
PREFIX = r'''
dec $reference_terminal_phase(pstate,nat) : bool
def $reference_terminal_phase(S,0) = true
  -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask*
  -- if pdestructorcall.OPERATION = (pdestructionoperation)
  -- if pdestructionoperation.SOURCE = GENERATOR_YIELD_DONE porigin poperand?
  -- if pdestructionoperation.VALUE = VARIABLE n_name* z
def $reference_terminal_phase(S,1) = true
  -- if S.TODO = [DESTRUCTOR_RELEASE pdestructionrelease, DESTRUCTOR_GLOBALS]
  -- if ~pdestructionrelease.USER
  -- if pdestructionrelease.JOBS = (DESTRUCTION_VALUE (HOBJECT n)) :: pdestructionjob*
  -- if S.OBJECTS[n] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_PAUSED
def $reference_terminal_phase(S,2) = true
  -- if S.TODO = (GENERATOR_CLOSE_ENTER pgenclose) :: ptask*
  -- if pgenclose.STAGE = CLOSE_QUEUED
def $reference_terminal_phase(S,3) = true
  -- if S.TODO = (GENERATOR_CLOSE_DONE pgenclose) :: ptask*
  -- if pgenclose.STAGE = CLOSE_FINISHED
def $reference_terminal_phase(S,n) = false -- otherwise
dec $reference_terminal_seek(pstate,nat,nat) : pstate
def $reference_terminal_seek(S,n_phase,n) = S
  -- if $reference_terminal_phase(S,n_phase)
def $reference_terminal_seek(S,n_phase,n) = S
  -- if ~$reference_terminal_phase(S,n_phase)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $reference_terminal_seek(S,n_phase,0) = S
  -- if ~$reference_terminal_phase(S,n_phase)
def $reference_terminal_seek(S,n_phase,n) = $reference_terminal_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_phase,$nabs($(n - 1)))
  -- if ~$reference_terminal_phase(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
'''


def seek(state, previous, phase):
    return [f'{state}_found = $reference_terminal_seek({previous},{phase},4096)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$reference_terminal_phase({state},{phase})']


def valid(state):
    return driver.valid(state) + [f'$generator_state_valid({state})',
                                 f'$call_entry_check({state}) = {state}']


def assertions(checked, path, directory, name):
    initial = ('$php_file_run(' + checked['fixture'] + ',0,'
               + driver.driver.byte_expr(os.fsencode(path)) + ','
               + driver.driver.byte_expr(os.fsencode(driver.ROOT)) + ')')
    checks = ['S_initial = ' + initial, '~S_initial.COMPILESTOP']
    previous = 'S_initial'
    if name == 'delayed-cv-terminal-reference-cache':
        checks += seek('S_operation', previous, 0) + valid('S_operation')
        checks += r'''
S_operation.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_operation*
pdestructorcall.OPERATION = (pdestructionoperation)
pdestructionoperation.SOURCE = GENERATOR_YIELD_DONE porigin_yield eps
pdestructionoperation.VALUE = VARIABLE n_name* z
n_name* = $ptascii("next")
$destructor_operation_valid(S_operation,pdestructionoperation)
~$destructor_return_operand_valid(S_operation,pdestructionoperation.VALUE)
$eager_operation_value_valid(S_operation,pdestructionoperation)
$generator_yield_delayed_value_valid(S_operation,pdestructionoperation)
~$eager_operation_value_valid(S_operation,pdestructionoperation[.VALUE = VARIABLE ($ptascii("other")) z])
~$eager_operation_value_valid(S_operation,pdestructionoperation[.VALUE = VARIABLE n_name* $(z + 1)])
$trace_slot(S_operation,S_operation.ENV,$ptascii("next")) = PINT 2
$close_outputs(S_operation.EVENTS) = $ptascii("1|E|")
'''.strip().splitlines()
        previous = 'S_operation'
    checks += seek('S_request', previous, 1) + valid('S_request')
    checks += r'''
S_request.TODO = [DESTRUCTOR_RELEASE pdestructionrelease, DESTRUCTOR_GLOBALS]
S_request.DESTRUCTION.RELEASES = pdestructionrelease :: pdestructionrelease_tail*
S_request.DESTRUCTION.PHASE = DESTRUCTION_GLOBALS
S_request.CURRENT = eps /\ S_request.ORIGIN = eps /\ S_request.FRAMES = eps
S_request.ACTIVEFIBER = eps /\ ~pdestructionrelease.USER
$destructor_release_valid(S_request,pdestructionrelease)
pdestructionrelease.JOBS = (DESTRUCTION_VALUE (HOBJECT n_generator)) :: pdestructionjob_tail*
$heap_owners($heap_graph(S_request),HOBJECT n_generator) = 1
S_unheld = $destructor_release_replace(S_request,pdestructionrelease[.JOBS = pdestructionjob_tail*])
$heap_owners($heap_graph(S_unheld),HOBJECT n_generator) = 0
S_request.OBJECTS[n_generator] = GENERATOR pgenerator_request
pgenerator_request.PHASE = GENERATOR_PAUSED /\ pgenerator_request.DELEGATE = eps
pgenerator_request.FRAME = (pframe_request)
pframe_request.ORIGIN = (porigin_request)
$generator_record_valid(S_request,pgenerator_request)
$generator_close_site(S_request,pgenerator_request,porigin_request)
$generator_close_frame_valid(S_request,pgenerator_request,pframe_request)
S_frame = $generator_frame_scope(S_request,pframe_request)
~$reference_returning(S_frame)
$call_task_valid(S_frame,RETURN_NULL)
'''.strip().splitlines()
    if name == 'terminal-active-finally-refused':
        checks += ['$generator_finalizer_frame(S_request,pgenerator_request.FRAME)',
                   '$generator_close_regions(S_request,porigin_request) =/= eps',
                   '~$generator_destructor_request_ready(S_request,pdestructionrelease,HOBJECT n_generator)',
                   'S_rejected = $drive_steps(S_request,1)',
                   'S_rejected.COMPLETION = UNSUPPORTED "Generator force-close at request end"',
                   '$close_outputs(S_request.EVENTS) = $ptascii("C|7|")',
                   '$close_outputs(S_rejected.EVENTS) = $close_outputs(S_request.EVENTS)']
        return checks
    checks += ['~$generator_finalizer_frame(S_request,pgenerator_request.FRAME)',
               '$generator_close_regions(S_request,porigin_request) = eps',
               '$generator_destructor_request_ready(S_request,pdestructionrelease,HOBJECT n_generator)',
               '$close_outputs(S_request.EVENTS) = ' + driver.driver.byte_expr(CASES[name][1]),
               'S_bad_site = $generator_set(S_request,n_generator,pgenerator_request[.FRAME = (pframe_request[.ORIGIN = $origin_child((porigin_request),[PCFIELD 1])])])',
               '$heap_graph(S_bad_site) = $heap_graph(S_request)',
               '$heap_valid($heap_graph(S_bad_site))',
               '~$generator_destructor_request_ready(S_bad_site,pdestructionrelease,HOBJECT n_generator)',
               '~$call_descriptors_valid(S_bad_site)',
               '$call_entry_check(S_bad_site).COMPLETION = UNSUPPORTED "invalid compiled function descriptor"']
    if name == 'delayed-cv-terminal-reference-cache':
        checks += ['$lookup(S_frame.ENV,$ptascii("next")) = (n_cell)',
                   r'pgenerator_request.VALUE = eps /\ pgenerator_request.REFCELL = (n_cell)',
                   'pgenerator_request.KEY = (PINT 1)',
                   'S_request.STORE[n_cell] = DEFINED (PINT 2)']
    else:
        checks += [r'pgenerator_request.VALUE = (PINT 5) /\ pgenerator_request.REFCELL = eps',
                   'pgenerator_request.KEY = (PNULL)']
    checks += seek('S_queued', 'S_request', 2) + valid('S_queued')
    checks += r'''
S_queued.TODO = (GENERATOR_CLOSE_ENTER pgenclose_queued) :: ptask_queued*
pgenclose_queued.OBJECT = n_generator
pgenclose_queued.FRAME = (pframe_queued)
pgenclose_queued.CALLER = eps /\ pgenclose_queued.CALLSITE = eps
pgenclose_queued.PENDING = eps /\ pgenclose_queued.NEXT = 0
S_queued.OBJECTS[n_generator] = GENERATOR pgenerator_queued
pgenerator_queued.PHASE = GENERATOR_CLOSING /\ pgenerator_queued.FRAME = eps
S_queued.DESTRUCTION.PHASE = DESTRUCTION_GLOBALS
$generator_close_regions(S_queued,pgenclose_queued.SITE) = eps
$generator_close_enter_valid(S_queued,pgenclose_queued)
'''.strip().splitlines()
    checks += seek('S_closed', 'S_queued', 3) + valid('S_closed')
    checks += r'''
S_closed.TODO = (GENERATOR_CLOSE_DONE pgenclose_closed) :: ptask_closed*
pgenclose_closed.OBJECT = n_generator
pgenclose_closed.FRAME = eps /\ pgenclose_closed.PENDING = eps
S_closed.OBJECTS[n_generator] = GENERATOR pgenerator_closed
pgenerator_closed.PHASE = GENERATOR_CLOSED /\ pgenerator_closed.FRAME = eps
pgenerator_closed.BORROWED = eps /\ pgenerator_closed.DELEGATE = eps
$generator_close_done_valid(S_closed,pgenclose_closed)
$close_outputs(S_closed.EVENTS) = $close_outputs(S_request.EVENTS)
'''.strip().splitlines()
    if name == 'delayed-cv-terminal-reference-cache':
        checks += [r'pgenerator_closed.REFCELL = (n_cell) /\ pgenerator_closed.VALUE = eps',
                   'S_closed.STORE[n_cell] = DEFINED (PINT 2)',
                   '(HCELL n_cell) <- S_closed.ALLOCATIONS',
                   '$heap_owners($heap_graph(S_closed),HCELL n_cell) = 1']
    else:
        checks += [r'pgenerator_closed.VALUE = (PINT 5) /\ pgenerator_closed.REFCELL = eps']
    checks += ['S_stopped = $drive_steps(S_closed,0)',
               'S_stopped = S_closed[.COMPLETION = BUDGET]',
               'S_resumed = $drive(S_stopped[.COMPLETION = NORMAL],4096)',
               'S_direct = $drive(S_closed,4096)', 'S_resumed = S_direct',
               'S_resumed.COMPLETION = NORMAL', 'S_resumed.TODO = eps',
               'S_resumed.FRAMES = eps', 'S_resumed.ITERATORS = eps',
               'S_resumed.DESTRUCTION.PHASE = DESTRUCTION_DONE',
               '~((HOBJECT n_generator) <- S_resumed.ALLOCATIONS)',
               '$close_outputs_only(S_resumed.EVENTS)',
               '$close_outputs(S_resumed.EVENTS) = ' + driver.driver.byte_expr(CASES[name][1])]
    checks += valid('S_resumed')
    if name == 'delayed-cv-terminal-reference-cache':
        checks += ['~((HCELL n_cell) <- S_resumed.ALLOCATIONS)']
    return checks


def main():
    driver.CASES = CASES
    driver.PREFIX += PREFIX
    driver.assertions = assertions
    driver.source.WATCHED = WATCHED
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())
