#!/usr/bin/env python3
"""Source-reached active-Fiber close claims and parked caller owners."""
import os

import generator_force_close_protocol as protocol
import generator_fiber_close_prepare as source

CASES = {name: source.CASES[case] for name, case in [
    ('active-claim', 'active-current-local'),
    ('resumed-claim', 'active-resumed-close'),
    ('caller-pending', 'active-caller-pending'),
    ('waiting-owner', 'waiting-main-argument-owner'),
]}
PREFIX = protocol.PREFIX + r'''
dec $fiber_close_phase(pstate,nat) : bool
def $fiber_close_phase(S,0) = true
  -- if S.TODO = (GENERATOR_CLOSE_ENTER pgenclose) :: ptask*
  -- if $trace_context_function(S,pgenclose.CONTEXT) = $ptascii("seq")
  -- if S.ACTIVEFIBER =/= eps
def $fiber_close_phase(S,1) = ($close_body_named(S,"seq") /\ S.ACTIVEFIBER =/= eps)
def $fiber_close_phase(S,2) = true
  -- if S.ACTIVEFIBER = eps
  -- if $lookup(S.ENV,$ptascii("f")) = (n_cell)
  -- if S.STORE[n_cell] = DEFINED (POBJECT n)
  -- if S.OBJECTS[n] = FIBER pfiber
  -- if pfiber.STATUS = FIBER_SUSPENDED
def $fiber_close_phase(S,3) = true
  -- if S.ACTIVEFIBER = (n_fiber)
  -- if $close_outputs(S.EVENTS) = [49,65]
  -- if S.FIBERCALLERS = [pfibercaller]
  -- if pfibercaller.VM.CURRENT = (pcallcontext)
  -- if $trace_context_function(S,pcallcontext) = $ptascii("hold")
def $fiber_close_phase(S,n_phase) = false -- otherwise
dec $fiber_close_seek(pstate,nat,nat) : pstate
def $fiber_close_seek(S,n_phase,n) = S -- if S.COMPILESTOP
def $fiber_close_seek(S,n_phase,n) = S
  -- if ~S.COMPILESTOP
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $fiber_close_seek(S,n_phase,n) = S
  -- if ~S.COMPILESTOP
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $fiber_close_phase(S,n_phase)
def $fiber_close_seek(S,n_phase,n) = S
  -- if ~S.COMPILESTOP
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$fiber_close_phase(S,n_phase)
  -- if n = 0 \/ (S.TODO = eps /\ S.FRAMES = eps)
def $fiber_close_seek(S,n_phase,n) = $fiber_close_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_phase,$nabs($(n - 1)))
  -- if ~S.COMPILESTOP
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$fiber_close_phase(S,n_phase)
  -- if $(n > 0)
  -- if S.TODO =/= eps \/ S.FRAMES =/= eps
'''


def seek(state, previous, phase):
    return [f'{state}_found = $fiber_close_seek({previous},{phase},4096)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$fiber_close_phase({state},{phase})']


def active(checks, state):
    checks += protocol.valid(state)
    checks += [f'{state}.ACTIVEFIBER = (n_fiber)',
               f'{state}.OBJECTS[n_fiber] = FIBER pfiber_live',
               'pfiber_live.STATUS = FIBER_RUNNING', 'pfiber_live.VM = eps',
               f'{state}.FIBERCALLERS = [pfibercaller_live]',
               'pfibercaller_live.OBJECT = n_fiber',
               'pfibercaller_live.PREVIOUS = eps',
               'pfibercaller_live.API.OBJECT = n_fiber',
               'pfibercaller_live.API.SEQUENCE = pfiber_live.SEQUENCE',
               f'$fiber_state_valid({state})']


def assertions(checked, path, directory, name):
    initial = '$php_file_run(' + checked['fixture'] + ',0,' + protocol.driver.byte_expr(os.fsencode(path)) + ',' + protocol.driver.byte_expr(os.fsencode(directory)) + ')'
    checks = ['S_initial = ' + initial, '~S_initial.COMPILESTOP']
    previous = 'S_initial'
    if name == 'resumed-claim':
        checks += seek('S_paused', previous, 2) + protocol.valid('S_paused')
        checks += r'''
S_paused.ACTIVEFIBER = eps
S_paused.FIBERCALLERS = eps
$lookup(S_paused.ENV,$ptascii("f")) = (n_fiber_cell)
S_paused.STORE[n_fiber_cell] = DEFINED (POBJECT n_fiber_paused)
S_paused.OBJECTS[n_fiber_paused] = FIBER pfiber_paused
pfiber_paused.STATUS = FIBER_SUSPENDED
pfiber_paused.VM = (pfibervm_paused)
pfibervm_paused.TODO = (FIBER_CONTINUE pfiberapi_paused) :: ptask_paused*
$lookup(pfibervm_paused.TABLE.ENV,$ptascii("g")) = (n_gen_cell)
S_paused.STORE[n_gen_cell] = DEFINED (POBJECT n_gen)
S_paused.OBJECTS[n_gen] = GENERATOR pgenerator_paused
pgenerator_paused.PHASE = GENERATOR_PAUSED
$($heap_owners($heap_graph(S_paused),HOBJECT n_gen) > 0)
$generator_close_claims(pfibervm_paused.TODO) = eps
$generator_close_frame_claims(pfibervm_paused.FRAMES) = eps
'''.strip().splitlines()
        previous = 'S_paused'
    if name in ['active-claim', 'resumed-claim']:
        checks += seek('S_queued', previous, 0)
        active(checks, 'S_queued')
        checks += r'''
S_queued.TODO = (GENERATOR_CLOSE_ENTER pgenclose_queued) :: ptask_queued*
pgenclose_queued.FRAME = (pframe_queued)
pgenclose_queued.STAGE = CLOSE_QUEUED
pgenclose_queued.NEXT = 0
S_queued.CURRENT = pgenclose_queued.CALLER
S_queued.ORIGIN = pgenclose_queued.CALLSITE
S_queued.OBJECTS[pgenclose_queued.OBJECT] = GENERATOR pgenerator_queued
pgenerator_queued.PHASE = GENERATOR_CLOSING
pgenerator_queued.FRAME = eps
$heap_owners($heap_graph(S_queued)[.ROOTS = $destruction_node_delete($machine_roots(S_queued),HOBJECT pgenclose_queued.OBJECT)],HOBJECT pgenclose_queued.OBJECT) = 0
$generator_close_claims(S_queued.TODO) = [pgenclose_queued.OBJECT]
'''.strip().splitlines()
        protocol.reject(checks, 'missing_active', 'S_queued[.ACTIVEFIBER = eps]')
        protocol.reject(checks, 'missing_callers', 'S_queued[.FIBERCALLERS = eps]')
        protocol.reject(checks, 'wrong_sequence', 'S_queued[.FIBERCALLERS = [pfibercaller_live[.API = pfibercaller_live.API[.SEQUENCE = S_queued.FIBERSEQ]]]]')
        protocol.reject(checks, 'external_owner', 'S_queued[.HELD = S_queued.HELD ++ [HOBJECT pgenclose_queued.OBJECT]]')
        protocol.reject(checks, 'duplicate_claim', 'S_queued[.TODO = (GENERATOR_CLOSE_ENTER pgenclose_queued) :: S_queued.TODO]')
        protocol.reject(checks, 'wrong_caller', 'S_queued[.TODO = (GENERATOR_CLOSE_ENTER pgenclose_queued[.CALLER = eps]) :: ptask_queued*]')
        if name == 'resumed-claim':
            checks += ['n_fiber = n_fiber_paused', 'pgenclose_queued.OBJECT = n_gen',
                       'pfibercaller_live.API.KIND = (INTRINSIC_FIBER_RESUME)',
                       '$(pfiber_live.SEQUENCE > pfiber_paused.SEQUENCE)']
        checks += seek('S_body', 'S_queued', 1) + protocol.valid('S_body') + protocol.body_binding('S_body')
        checks += ['S_body.ACTIVEFIBER = (n_fiber)',
                   'S_body.FIBERCALLERS = S_queued.FIBERCALLERS',
                   'pgenclose_body.OBJECT = pgenclose_queued.OBJECT',
                   '$generator_close_active(S_body)', '~$fiber_transfer_domain(S_body)',
                   '$generator_close_stages(S_body,S_body.CURRENT,S_body.TODO,S_body.FRAMES)']
        protocol.reject(checks, 'lost_active_body', 'S_body[.ACTIVEFIBER = eps]')
        protocol.reject(checks, 'ordinary_marker', 'S_body[.TODO = $close_ordinary_marker(S_body.TODO,porigin_finally)]')
        previous = 'S_body'
    elif name == 'caller-pending':
        checks += protocol.seek('S_body', previous, 70)
        active(checks, 'S_body')
        checks += protocol.body_binding('S_body')
        checks += ['pgenclose_body.PENDING = (n_old)', '$throwable_live(S_body,n_old)',
                   '$throwable_field(S_body,n_old,"message") = PSTRING $ptascii("old")',
                   '$throwable_field(S_body,n_old,"previous") = PNULL',
                   '$($heap_owners($heap_graph(S_body),HOBJECT n_old) > 0)']
        protocol.reject(checks, 'lost_pending_active', 'S_body[.ACTIVEFIBER = eps]')
        checks += protocol.seek('S_catch', 'S_body', 72) + protocol.valid('S_catch')
        checks += ['S_catch.ACTIVEFIBER = (n_fiber)',
                   'S_catch.TODO = (CATCH_BIND porigin_catch n_index n_new) :: ptask_catch*',
                   '$throwable_field(S_catch,n_new,"previous") = POBJECT n_old',
                   '$throwable_live(S_catch,n_old)',
                   '~((HOBJECT pgenclose_body.OBJECT) <- S_catch.ALLOCATIONS)']
        previous = 'S_catch'
    elif name == 'waiting-owner':
        checks += seek('S_waiting', previous, 3)
        active(checks, 'S_waiting')
        checks += r'''
pfibercaller_live.VM.CURRENT = (pcallcontext_hold)
$trace_context_function(S_waiting,pcallcontext_hold) = $ptascii("hold")
$lookup(pfibercaller_live.VM.TABLE.ENV,$ptascii("g")) = (n_gen_cell)
S_waiting.STORE[n_gen_cell] = DEFINED (POBJECT n_gen)
S_waiting.OBJECTS[n_gen] = GENERATOR pgenerator_waiting
pgenerator_waiting.PHASE = GENERATOR_PAUSED
$heap_owners($heap_graph(S_waiting),HOBJECT n_gen) = 1
(HCELL n_gen_cell) <- $fiber_vm_nodes(pfibercaller_live.VM)
$generator_close_claims(S_waiting.TODO) = eps
$generator_close_frame_claims(S_waiting.FRAMES) = eps
$lookup($fiber_globals(S_waiting).ENV,$ptascii("g")) = eps
'''.strip().splitlines()
        protocol.reject(checks, 'lost_waiting_caller', 'S_waiting[.FIBERCALLERS = eps]')
        previous = 'S_waiting'
    checks += [f'S_stopped = $drive_steps({previous},0)', 'S_stopped.COMPLETION = BUDGET',
               f'S_stopped = {previous}[.COMPLETION = BUDGET]',
               'S_resumed = $drive(S_stopped[.COMPLETION = NORMAL],4096)',
               f'S_direct = $drive({previous},4096)', 'S_resumed = S_direct',
               'S_resumed.COMPLETION = NORMAL', 'S_resumed.TODO = eps', 'S_resumed.FRAMES = eps',
               'S_resumed.ACTIVEFIBER = eps', 'S_resumed.FIBERCALLERS = eps',
               '$close_outputs_only(S_resumed.EVENTS)',
               '$close_outputs(S_resumed.EVENTS) = ' + protocol.driver.byte_expr(CASES[name][1])]
    checks += protocol.valid('S_resumed')
    if name in ['active-claim', 'resumed-claim', 'caller-pending']:
        checks += ['~((HOBJECT pgenclose_body.OBJECT) <- S_resumed.ALLOCATIONS)']
    else:
        checks += ['~((HOBJECT n_gen) <- S_resumed.ALLOCATIONS)']
    return checks


def main():
    protocol.CASES = CASES
    protocol.PREFIX = PREFIX
    protocol.assertions = assertions
    protocol.source.WATCHED = source.WATCHED + ['tests/semantics/generator_fiber_close_protocol.py']
    return protocol.main()


if __name__ == '__main__':
    raise SystemExit(main())
