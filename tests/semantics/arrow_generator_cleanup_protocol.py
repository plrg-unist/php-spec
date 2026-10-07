#!/usr/bin/env python3
"""Reached Arrow cleanup with the current collection and clone fields."""
import arrow_generator_integration_protocol as integration
import generator_force_close_protocol as driver

CASES = integration.CASES
WATCHED = integration.WATCHED + [
    'spec/semantics/270-eager-destructors.watsup',
    'spec/semantics/300-readonly-clone-lifecycle.watsup',
    'spec/semantics/301-cycle-collection.watsup',
    'tests/semantics/arrow_generator_cleanup_protocol.py',
]
PREFIX = integration.PREFIX + r'''
def $arrow_integration_phase(S,3) = true
  -- if S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask*
  -- if pdestructionrelease.JOBS = (DESTRUCTION_HANDLE n) :: pdestructionjob*
'''


def cleanup_fields(state):
    return [f'$gc_state_valid({state})',
            f'{state}.CLONES = eps /\\ {state}.CLONEMAKERS = eps']


def assertions(checked, path, directory, name):
    # Reuse the frozen fixture's checked child preparation and startup only.
    # Its remaining143 checks are neither emitted nor renewed by this cut.
    checks = integration.assertions(checked, path, directory, name)[:5]
    checks += ['psourceresponse = SOURCE_ACCEPT n_unit pevalcontext.BYTES $arrow_integration_child()',
               'S_entry = $eval_resume(S_wait,psourceresponse)', 'S_entry.COMPLETION = NORMAL']
    checks += integration.seek('S_retired', 'S_entry', 0) + cleanup_fields('S_retired')
    checks += ['S_retired.ACTIVEFIBER = (n_fiber)',
               'S_retired.CURRENT = (pcallcontext_destructor)',
               '$destructor_context_call(pcallcontext_destructor,S_retired.CURRENT,S_retired.FRAMES) = (pdestructorcall)',
               'n_source = pdestructorcall.OBJECT']
    checks += integration.seek('S_handle', 'S_retired', 3) + driver.valid('S_handle')
    checks += ['$gc_state_valid(S_handle)']
    checks += r'''
S_handle.ACTIVEFIBER = (n_fiber)
S_handle.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_handle_tail*
pdestructionrelease.JOBS = (DESTRUCTION_HANDLE n_source) :: pdestructionjob_tail*
S_handle.DESTRUCTION.RELEASES = pdestructionrelease :: pdestructionrelease_tail*
~((HOBJECT n_source) <- S_handle.ALLOCATIONS)
$destructor_release_valid(S_handle,pdestructionrelease)
$gc_handle_all(S_handle,n_source) = 1
$gc_retired_valid(S_handle,n_source)
S_handle_bad = S_handle[.TODO = (DESTRUCTOR_RELEASE pdestructionrelease[.JOBS = pdestructionjob_tail*]) :: ptask_handle_tail*][.DESTRUCTION.RELEASES = pdestructionrelease[.JOBS = pdestructionjob_tail*] :: pdestructionrelease_tail*]
$heap_graph(S_handle_bad) = $heap_graph(S_handle)
$heap_valid($heap_graph(S_handle_bad))
$gc_handle_all(S_handle_bad,n_source) = 0
~$gc_retired_valid(S_handle_bad,n_source)
'''.strip().splitlines()
    # Removing a HANDLE tests its physical-storage obligation. Public rejection
    # is not claimed unless this original also has a GC_RETIRED buffer slot.
    checks += integration.seek('S_paused', 'S_handle', 1) + cleanup_fields('S_paused')
    checks += ['S_paused.ACTIVEFIBER = (n_fiber)',
               'S_paused.TODO = (GENERATOR_RESUME pgeneratorop_arrow) :: ptask_paused*',
               'S_paused.OBJECTS[pgeneratorop_arrow.OBJECT] = GENERATOR pgenerator_paused',
               'pgenerator_paused.CLOSURE = (n_closure)',
               '$heap_owners($heap_graph(S_paused),HOBJECT n_closure) = 1']
    checks += integration.seek('S_close', 'S_paused', 2) + cleanup_fields('S_close')
    checks += ['S_close.ACTIVEFIBER = (n_fiber)',
               'S_close.TODO = (GENERATOR_CLOSE_ENTER pgenclose) :: ptask_close*',
               'pgenclose.CONTEXT.INSTANCE = (n_closure)',
               '$generator_close_enter_valid(S_close,pgenclose)',
               'S_zero = $drive_steps(S_close,0)', 'S_zero.COMPLETION = BUDGET',
               'S_zero.TODO = S_close.TODO', 'S_zero.FRAMES = S_close.FRAMES',
               'S_resumed = $drive(S_zero[.COMPLETION = NORMAL],4096)',
               'S_direct = $drive(S_close,4096)', 'S_resumed = S_direct',
               'S_resumed.COMPLETION = NORMAL', 'S_resumed.TODO = eps',
               'S_resumed.ACTIVEFIBER = eps',
               '$arrow_integration_outputs(S_resumed.EVENTS) = '
               + driver.driver.byte_expr(CASES[name][1])]
    checks += driver.valid('S_resumed') + cleanup_fields('S_resumed')
    checks += ['$call_entry_check(S_resumed) = S_resumed']
    return checks


def main():
    driver.CASES = CASES
    driver.source.WATCHED = WATCHED
    driver.PREFIX = PREFIX
    driver.assertions = assertions
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())
