#!/usr/bin/env python3
"""Reached cache release, real destructor carrier and exception replacement."""
import os

import generator_force_close_protocol as driver
import yield_key_warning_protocol as key
import yield_key_warning_review as source

CASES = {
    'normal-cache-release': source.CASES['key-warning-owns-value-during-reference-overwrite'],
    'throwing-cache-release': source.CASES['cached-value-destructor-throw-after-key-warning'],
    'pending-cache-release': source.CASES['cached-value-destructor-replaces-force-close-finally-throw'],
}
WATCHED = key.WATCHED + ['tests/semantics/yield_key_release_protocol.py']
PREFIX = key.PREFIX + r'''
dec $key_release_phase(pstate) : bool
def $key_release_phase(S) = true
  -- if S.TODO = (GENERATOR_CLOSE_RELEASE pgenrelease) :: ptask*
  -- if pgenrelease.JOBS = (DESTRUCTION_VALUE (HOBJECT n)) :: pdestructionjob*
  -- if $destructor_uncalled_node(S,HOBJECT n)
  -- if $object_name(S,n) = $ptascii("Payload321")
def $key_release_phase(S) = false -- otherwise
dec $key_release_seek(pstate,nat) : pstate
def $key_release_seek(S,n) = S -- if $key_release_phase(S)
def $key_release_seek(S,n) = S
  -- if ~$key_release_phase(S)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $key_release_seek(S,0) = S -- if ~$key_release_phase(S)
def $key_release_seek(S,n) = $key_release_seek($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))
  -- if ~$key_release_phase(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
'''


def assertions(checked, path, directory, name):
    initial = ('$php_file_run(' + checked['fixture'] + ',0,'
               + driver.driver.byte_expr(os.fsencode(path)) + ','
               + driver.driver.byte_expr(os.fsencode(driver.ROOT)) + ')')
    checks = ['S_initial = ' + initial, '~S_initial.COMPILESTOP',
              'S_release_found = $key_release_seek(S_initial,4096)',
              r'S_release_found.COMPLETION = NORMAL \/ S_release_found.COMPLETION = BUDGET',
              'S_release = S_release_found[.COMPLETION = NORMAL]',
              '$key_release_phase(S_release)'] + key.valid('S_release')
    checks += r'''
S_release.TODO = (GENERATOR_CLOSE_RELEASE pgenrelease) :: ptask_release_tail*
pgenrelease.JOBS = (DESTRUCTION_VALUE (HOBJECT n_payload)) :: pdestructionjob_tail*
S_release.CURRENT = eps /\ S_release.ACTIVEFIBER = eps
$destructor_operational(S_release) /\ $destructor_user_source(S_release)
$destructor_operation_for(S_release) = (pdestructionoperation)
S_release.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail*
$destructor_operation_valid(S_release,pdestructionoperation)
pdestructionoperation.PENDING = eps
$generator_close_destructor_ready(S_release,pgenrelease)
S_unheld = S_release[.TODO = (GENERATOR_CLOSE_RELEASE pgenrelease[.JOBS = pdestructionjob_tail*]) :: ptask_release_tail*]
$heap_owners($heap_graph(S_release),HOBJECT n_payload) = 1
$heap_owners($heap_graph(S_unheld),HOBJECT n_payload) = 0
$trace_slot(S_release,S_release.ENV,$ptascii("weak")) = POBJECT n_weak
$weakref_get(S_release,n_weak) = POBJECT n_payload
'''.strip().splitlines()
    if name == 'pending-cache-release':
        checks += ['$trace_slot(S_release,S_release.ENV,$ptascii("original")) = POBJECT n_original',
                   'pgenrelease.PENDING = (n_original)',
                   '$throwable_field(S_release,n_original,"previous") = PNULL']
    else:
        checks += ['pgenrelease.PENDING = eps']
    if name == 'normal-cache-release':
        # Borrowed registry removal preserves every real heap owner. These
        # controls test the handoff helper, not public admission of that edit.
        checks += r'''
S_no_carrier = S_release[.DESTRUCTION.OPERATIONS = eps]
$heap_graph(S_no_carrier) = $heap_graph(S_release)
~$generator_close_destructor_ready(S_no_carrier,pgenrelease)
$generator_close_release(S_no_carrier,pgenrelease).COMPLETION = UNSUPPORTED "ordinary destructor release before request stage"
~$generator_close_destructor_tasks(S_release,[CHOOSE ([DESTRUCTOR_OPERATION_EXIT pdestructionoperation]) eps 0],pgenrelease.PENDING,pdestructionoperation.PENDING,DESTRUCTOR_OPERATION_EXIT pdestructionoperation)
~$generator_close_destructor_ready(S_release[.TODO = [GENERATOR_CLOSE_RELEASE pgenrelease]],pgenrelease)
'''.strip().splitlines()
    checks += r'''
S_handoff_found = $drive_steps(S_release,1)
S_handoff_found.COMPLETION = NORMAL \/ S_handoff_found.COMPLETION = BUDGET
S_handoff = S_handoff_found[.COMPLETION = NORMAL]
S_handoff.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (GENERATOR_CLOSE_RELEASE pgenrelease_after) :: ptask_handoff_tail*
pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_payload)]
pgenrelease_after.JOBS = pdestructionjob_tail*
pgenrelease_after.VALUE = pgenrelease.VALUE /\ pgenrelease_after.BASE = pgenrelease.BASE
S_handoff.DESTRUCTION.RELEASES = pdestructionrelease :: S_release.DESTRUCTION.RELEASES
S_handoff.CURRENT = S_release.CURRENT /\ S_handoff.ORIGIN = S_release.ORIGIN
S_handoff.CONSTCONTEXT = S_release.CONSTCONTEXT
$heap_owners($heap_graph(S_handoff),HOBJECT n_payload) = 1
$weakref_get(S_handoff,n_weak) = POBJECT n_payload
$destructor_operation_for(S_handoff) = (pdestructionoperation_after)
pdestructionoperation_after.PENDING = pgenrelease_after.PENDING
'''.strip().splitlines()
    checks += key.valid('S_handoff')
    if name == 'pending-cache-release':
        checks += ['pgenrelease_after.PENDING = (n_original)']
    else:
        checks += ['pgenrelease_after.PENDING = eps']
    if name != 'normal-cache-release':
        checks += key.seek('S_catch', 'S_handoff', 3) + key.valid('S_catch')
        checks += ['S_catch.TODO = (CATCH_BIND porigin_catch n_catch n_throwable) :: ptask_catch_tail*',
                   'S_catch.CURRENT = eps',
                   '$trace_slot(S_catch,S_catch.ENV,$ptascii("replacement")) = POBJECT n_throwable',
                   '$weakref_get(S_catch,n_weak) = PNULL']
        if name == 'pending-cache-release':
            checks += ['$throwable_field(S_catch,n_throwable,"previous") = POBJECT n_original',
                       '$throwable_field(S_catch,n_original,"previous") = PNULL']
        else:
            checks += ['$throwable_field(S_catch,n_throwable,"previous") = PNULL']
        previous = 'S_catch'
    else:
        previous = 'S_handoff'
    checks += [f'S_zero = $drive_steps({previous},0)',
               f'S_zero = {previous}[.COMPLETION = BUDGET]',
               'S_resumed = $drive(S_zero[.COMPLETION = NORMAL],4096)',
               f'S_direct = $drive({previous},4096)', 'S_resumed = S_direct',
               r'S_resumed.COMPLETION = NORMAL /\ S_resumed.TODO = eps /\ S_resumed.FRAMES = eps',
               '$yield_key_outputs(S_resumed.EVENTS) = ' + driver.driver.byte_expr(CASES[name][1]),
               '$weakref_get(S_resumed,n_weak) = PNULL',
               '~((HOBJECT n_payload) <- S_resumed.ALLOCATIONS)']
    checks += key.valid('S_resumed')
    return checks


def main():
    driver.CASES = CASES
    driver.source.WATCHED = WATCHED
    driver.PREFIX = PREFIX
    driver.assertions = assertions
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())
