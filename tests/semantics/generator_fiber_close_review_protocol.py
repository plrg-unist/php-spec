#!/usr/bin/env python3
"""Independent source-reached active, nested and parked Fiber close states."""
import os

import generator_force_close_protocol as driver
import generator_fiber_close_review as source

CASES = {name: source.CASES[case] for name, case in [
    ('queued-body', 'active-current'),
    ('nested-callers', 'nested-active-fibers'),
    ('parked-owner', 'parked-fiber-owner'),
    ('pending-chain', 'pending-throw-chain'),
]}
WATCHED = source.WATCHED + ['tests/semantics/generator_fiber_close_review_protocol.py']
PREFIX = driver.PREFIX + r'''
def $close_phase(S,310) = true
  -- if S.TODO = (GENERATOR_CLOSE_ENTER pgenclose) :: ptask*
  -- if $trace_context_function(S,pgenclose.CONTEXT) = $ptascii("seq")
  -- if S.ACTIVEFIBER =/= eps
def $close_phase(S,311) = ($close_body_named(S,"seq") /\ S.ACTIVEFIBER =/= eps)
def $close_phase(S,312) = true
  -- if $close_body_named(S,"seq")
  -- if S.ACTIVEFIBER =/= eps
  -- if $generator_close_saved(S,S.CURRENT,S.FRAMES) = (pgenclose)
  -- if pgenclose.PENDING = (n)
  -- if $throwable_field(S,n,"message") = PSTRING $ptascii("body")
def $close_phase(S,313) = true
  -- if S.TODO = (CATCH_BIND porigin n_index n) :: ptask*
  -- if S.ACTIVEFIBER =/= eps
  -- if $throwable_field(S,n,"message") = PSTRING $ptascii("close")
  -- if $throwable_field(S,n,"previous") = POBJECT n_old
  -- if $throwable_field(S,n_old,"message") = PSTRING $ptascii("body")
def $close_phase(S,314) = true
  -- if $close_body_named(S,"seq")
  -- if S.ACTIVEFIBER =/= eps
  -- if |S.FIBERCALLERS| = 2
def $close_phase(S,315) = true
  -- if S.ACTIVEFIBER =/= eps
  -- if $close_outputs(S.EVENTS) = $ptascii("6S|D|")
'''


def active(state):
    return driver.valid(state) + [
        f'{state}.ACTIVEFIBER = (n_fiber)',
        f'{state}.OBJECTS[n_fiber] = FIBER pfiber_live',
        'pfiber_live.STATUS = FIBER_RUNNING', 'pfiber_live.VM = eps',
        f'$generator_state_valid({state})', f'$fiber_state_valid({state})',
        f'$generator_close_state_valid({state})',
    ]


def assertions(checked, path, directory, name):
    initial = '$php_file_run(' + checked['fixture'] + ',0,' + driver.driver.byte_expr(os.fsencode(path)) + ',' + driver.driver.byte_expr(os.fsencode(directory)) + ')'
    checks = ['S_initial = ' + initial, '~S_initial.COMPILESTOP']
    previous = 'S_initial'
    if name in ['queued-body', 'parked-owner']:
        if name == 'parked-owner':
            checks += driver.seek('S_parked', previous, 315) + driver.valid('S_parked')
            checks += r'''
S_parked.ACTIVEFIBER = (n_drop)
S_parked.FIBERCALLERS = [pfibercaller_drop]
pfibercaller_drop.OBJECT = n_drop
pfibercaller_drop.PREVIOUS = eps
$lookup($fiber_globals(S_parked).ENV,$ptascii("g")) = eps
$lookup($fiber_globals(S_parked).ENV,$ptascii("keep")) = (n_keep_cell)
S_parked.STORE[n_keep_cell] = DEFINED (POBJECT n_keep)
S_parked.OBJECTS[n_keep] = FIBER pfiber_parked
pfiber_parked.STATUS = FIBER_SUSPENDED
pfiber_parked.VM = (pfibervm)
$lookup(pfibervm.TABLE.ENV,$ptascii("held")) = (n_held)
S_parked.STORE[n_held] = DEFINED (POBJECT n_generator)
S_parked.OBJECTS[n_generator] = GENERATOR pgenerator_parked
pgenerator_parked.PHASE = GENERATOR_PAUSED
$heap_owners($heap_graph(S_parked),HOBJECT n_generator) = 1
$heap_count(HCELL n_held,$fiber_vm_nodes(pfibervm)) = 1
$heap_count(HOBJECT n_generator,$fiber_vm_nodes(pfibervm)) = 0
$fiber_vm_valid(S_parked,pfibervm,(n_keep),eps)
~$fiber_vm_valid(S_parked,pfibervm[.GLOBAL = true],(n_keep),eps)
'''.strip().splitlines()
            previous = 'S_parked'
        checks += driver.seek('S_queued', previous, 310) + active('S_queued')
        checks += r'''
S_queued.TODO = (GENERATOR_CLOSE_ENTER pgenclose) :: ptask_queued*
n_close = pgenclose.OBJECT
S_queued.OBJECTS[n_close] = GENERATOR pgenerator_queued
pgenerator_queued.PHASE = GENERATOR_CLOSING
pgenerator_queued.FRAME = eps
pgenclose.STAGE = CLOSE_QUEUED
pgenclose.FRAME = (pframe_queued)
pgenclose.CALLER = S_queued.CURRENT
pgenclose.CALLSITE = S_queued.ORIGIN
pgenclose.CALLSITE = (porigin_caller)
$heap_owners($heap_graph(S_queued),HOBJECT n_close) = 1
$heap_count(HOBJECT n_close,$machine_roots(S_queued)) = 1
$generator_close_enter_valid(S_queued,pgenclose)
'''.strip().splitlines()
        if name == 'parked-owner':
            checks += ['n_close = n_generator', 'n_fiber = n_keep',
                       'S_queued.FIBERCALLERS = [pfibercaller_resume]',
                       'pfibercaller_resume.API.KIND = (INTRINSIC_FIBER_RESUME)']
        driver.reject(checks, 'queued_fiber', 'S_queued[.ACTIVEFIBER = eps]')
        driver.reject(checks, 'queued_claim', 'S_queued[.TODO = ptask_queued*]')
        driver.reject(checks, 'queued_double', 'S_queued[.TODO = (GENERATOR_CLOSE_ENTER pgenclose) :: S_queued.TODO]')
        driver.reject(checks, 'queued_site', 'S_queued[.TODO = (GENERATOR_CLOSE_ENTER pgenclose[.CALLSITE = eps]) :: ptask_queued*]')
        previous = 'S_queued'
    phase = 314 if name == 'nested-callers' else 312 if name == 'pending-chain' else 311
    checks += driver.seek('S_body', previous, phase) + active('S_body') + driver.body_binding('S_body')
    checks += r'''
$generator_close_saved(S_body,S_body.CURRENT,S_body.FRAMES) = (pgenclose_body)
$heap_owners($heap_graph(S_body),HOBJECT pgenclose_body.OBJECT) = 1
$generator_resume_ids(S_body.TODO) = eps
$generator_saved_ids(S_body.FRAMES) = [pgenclose_body.OBJECT]
~$fiber_transfer_domain(S_body)
'''.strip().splitlines()
    driver.reject(checks, 'body_active', 'S_body[.ACTIVEFIBER = eps]')
    driver.reject(checks, 'body_stage', 'S_body[.FRAMES = pframe_caller[.TODO = (GENERATOR_CLOSE_DONE pgenclose_body[.STAGE = CLOSE_QUEUED]) :: ptask_caller*] :: pframe_caller_tail*]')
    if name == 'nested-callers':
        checks += r'''
S_body.FIBERCALLERS = [pfibercaller_inner,pfibercaller_outer]
pfibercaller_inner.OBJECT = n_fiber
pfibercaller_inner.PREVIOUS = (n_outer)
pfibercaller_outer.OBJECT = n_outer
pfibercaller_outer.PREVIOUS = eps
S_body.OBJECTS[n_outer] = FIBER pfiber_outer
pfiber_outer.STATUS = FIBER_RUNNING
pfiber_outer.VM = eps
~pfibercaller_inner.VM.GLOBAL
pfibercaller_outer.VM.GLOBAL
$fiber_callers_valid(S_body,(n_fiber),S_body.FIBERCALLERS,eps)
~$fiber_callers_valid(S_body,(n_outer),S_body.FIBERCALLERS,eps)
'''.strip().splitlines()
        driver.reject(checks, 'nested_previous', 'S_body[.FIBERCALLERS = [pfibercaller_inner[.PREVIOUS = eps],pfibercaller_outer]]')
        driver.reject(checks, 'nested_duplicate', 'S_body[.FIBERCALLERS = [pfibercaller_inner[.PREVIOUS = (n_fiber)],pfibercaller_outer]]')
    if name == 'pending-chain':
        checks += r'''
pgenclose_body.PENDING = (n_old)
$throwable_live(S_body,n_old)
$throwable_field(S_body,n_old,"message") = PSTRING $ptascii("body")
$throwable_field(S_body,n_old,"previous") = PNULL
$heap_owners($heap_graph(S_body),HOBJECT n_old) = 1
'''.strip().splitlines()
        driver.reject(checks, 'pending_type', 'S_body[.FRAMES = pframe_caller[.TODO = (GENERATOR_CLOSE_DONE pgenclose_body[.PENDING = (n_fiber)]) :: ptask_caller*] :: pframe_caller_tail*]')
        checks += driver.seek('S_catch', 'S_body', 313) + driver.valid('S_catch')
        checks += r'''
S_catch.ACTIVEFIBER = (n_fiber)
S_catch.FIBERCALLERS = S_body.FIBERCALLERS
S_catch.TODO = (CATCH_BIND porigin_catch n_index n_new) :: ptask_catch*
$throwable_field(S_catch,n_new,"previous") = POBJECT n_old
$heap_owners($heap_graph(S_catch),HOBJECT n_old) = 1
~((HOBJECT pgenclose_body.OBJECT) <- S_catch.ALLOCATIONS)
'''.strip().splitlines()
        previous = 'S_catch'
    else:
        previous = 'S_body'
    checks += [f'S_stopped = $drive_steps({previous},0)', 'S_stopped.COMPLETION = BUDGET',
               f'S_stopped = {previous}[.COMPLETION = BUDGET]',
               'S_resumed = $drive(S_stopped[.COMPLETION = NORMAL],4096)',
               f'S_direct = $drive({previous},4096)', 'S_resumed = S_direct',
               'S_resumed.COMPLETION = NORMAL', 'S_resumed.TODO = eps', 'S_resumed.FRAMES = eps',
               'S_resumed.CURRENT = eps', 'S_resumed.ACTIVEFIBER = eps', 'S_resumed.FIBERCALLERS = eps',
               '$close_outputs_only(S_resumed.EVENTS)',
               '$close_outputs(S_resumed.EVENTS) = ' + driver.driver.byte_expr(CASES[name][1])]
    return checks + driver.valid('S_resumed')


def main():
    source.WATCHED = WATCHED
    driver.source = source
    driver.CASES = CASES
    driver.PREFIX = PREFIX
    driver.assertions = assertions
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())
