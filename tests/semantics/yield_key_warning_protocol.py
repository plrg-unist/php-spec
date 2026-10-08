#!/usr/bin/env python3
"""Source-reached partial YIELD caches, warning owners and real resumers."""
import os

import generator_force_close_protocol as driver
import yield_key_warning_review as source

CASES = {
    'normal-reference-owner': source.CASES['key-warning-owns-value-during-reference-overwrite'],
    'direct-throw-cache-owner': source.CASES['key-warning-throw-retains-new-value-and-arrow-owner'],
    'delegated-key-child-catch': source.CASES['key-warning-delegated-child-catch-precedes-parent'],
    'delegated-value-child-catch': source.CASES['value-warning-delegated-child-catch-suppresses-key-warning'],
}
WATCHED = driver.source.WATCHED + [
    'spec/semantics/207-error-handler-runtime.watsup',
    'spec/semantics/296-weak-references.watsup',
    'spec/semantics/310-generator-fiber-close.watsup',
    'spec/semantics/311-arrow-generators.watsup',
    'spec/semantics/321-yield-key-warning.watsup',
    'tests/semantics/yield_key_warning_review.py',
    'tests/semantics/yield_key_warning_protocol.py',
]
PREFIX = r'''
dec $yield_key_phase(pstate,nat) : bool
def $yield_key_phase(S,0) = true
  -- if S.TODO = (GENERATOR_YIELD_KEY n porigin z) :: ptask*
def $yield_key_phase(S,1) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask*
  -- if perrorcall.RESUME = ERROR_READ_RESULT perrorread
def $yield_key_phase(S,2) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $error_context_current_call(S,pcallcontext) = (perrorcall)
def $yield_key_phase(S,3) = true
  -- if S.TODO = (CATCH_BIND porigin n_index n) :: ptask*
def $yield_key_phase(S,4) = true
  -- if S.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask*
  -- if S.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_PAUSED
  -- if pgenerator.VALUE = (PINT 12)
def $yield_key_phase(S,5) = true
  -- if $yield_key_phase(S,2)
  -- if S.GLOBALTABLE = (psymboltable)
  -- if $trace_slot(S,psymboltable.ENV,$ptascii("value")) = PNULL
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE expression*) metadata)) :: ptask*
def $yield_key_phase(S,n) = false -- otherwise
dec $yield_key_seek(pstate,nat,nat) : pstate
def $yield_key_seek(S,n_phase,n) = S -- if $yield_key_phase(S,n_phase)
def $yield_key_seek(S,n_phase,n) = S
  -- if ~$yield_key_phase(S,n_phase)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $yield_key_seek(S,n_phase,0) = S -- if ~$yield_key_phase(S,n_phase)
def $yield_key_seek(S,n_phase,n) = $yield_key_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_phase,$nabs($(n - 1)))
  -- if ~$yield_key_phase(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
dec $yield_key_output(pevent) : bool
def $yield_key_output(OUTPUT ptbytes) = true
def $yield_key_output(pevent) = false -- otherwise
dec $yield_key_outputs(pevent*) : ptbytes
def $yield_key_outputs(eps) = eps
def $yield_key_outputs((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $yield_key_outputs(pevent*)
def $yield_key_outputs(pevent :: pevent_tail*) = $yield_key_outputs(pevent_tail*)
  -- if ~$yield_key_output(pevent)
'''


def seek(state, previous, phase):
    return [f'{state}_found = $yield_key_seek({previous},{phase},4096)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$yield_key_phase({state},{phase})']


def valid(state):
    return driver.valid(state) + [f'$generator_state_valid({state})',
                                 f'$call_entry_check({state}) = {state}']


def reject(checks, label, expression):
    state = 'S_bad_' + label
    checks += [f'{state} = {expression}',
               f'$heap_graph({state}) = $heap_graph(S_key)',
               f'$heap_valid($heap_graph({state}))',
               f'~$call_descriptors_valid({state})',
               f'$call_entry_check({state}).COMPLETION = UNSUPPORTED "invalid compiled function descriptor"']


def assertions(checked, path, directory, name):
    initial = ('$php_file_run(' + checked['fixture'] + ',0,'
               + driver.driver.byte_expr(os.fsencode(path)) + ','
               + driver.driver.byte_expr(os.fsencode(driver.ROOT)) + ')')
    checks = ['S_initial = ' + initial, '~S_initial.COMPILESTOP']
    value_warning = name == 'delegated-value-child-catch'
    if not value_warning:
        checks += seek('S_key', 'S_initial', 0) + valid('S_key')
        checks += r'''
S_key.TODO = (GENERATOR_YIELD_KEY n_generator porigin_yield z_opcode) :: ptask_key_tail*
S_key.CURRENT = (pcallcontext_generator)
S_key.OBJECTS[n_generator] = GENERATOR pgenerator_key
pgenerator_key.PHASE = GENERATOR_RUNNING
pgenerator_key.FRAME = eps /\ pgenerator_key.RETURN = eps /\ pgenerator_key.DELEGATE = eps
pgenerator_key.KEY = eps
$generator_yield_key_operand(S_key,porigin_yield) = (S_key.RESULT)
S_key.BASE = BASE_VALUE (KNOWN PNULL)
$generator_yield_key_read_valid(S_key,n_generator,porigin_yield,z_opcode)
$generator_yield_key_node_valid(S_key,n_generator)
$generator_yield_key_task_ids(GENERATOR_YIELD_KEY n_generator porigin_yield z_opcode) = [n_generator]
$generator_id_count($generator_yield_key_tasks_ids(S_key.TODO) ++ $generator_yield_key_frames_ids(S_key.FRAMES),n_generator) = 1
'''.strip().splitlines()
        if name == 'direct-throw-cache-owner':
            # All changes here preserve the genuine source, caller and heap.
            reject(checks, 'input', 'S_key[.RESULT = KNOWN (PINT 17)]')
            reject(checks, 'base', 'S_key[.BASE = BASE_VALUE (KNOWN (PINT 17))]')
            reject(checks, 'line', 'S_key[.TODO = (GENERATOR_YIELD_KEY n_generator porigin_yield $(z_opcode + 1)) :: ptask_key_tail*]')
            reject(checks, 'preset_key', '$generator_set(S_key,n_generator,pgenerator_key[.KEY = (PINT 17)])')
            reject(checks, 'duplicate', 'S_key[.TODO = (GENERATOR_YIELD_KEY n_generator porigin_yield z_opcode) :: (GENERATOR_YIELD_KEY n_generator porigin_yield z_opcode) :: ptask_key_tail*]')
            reject(checks, 'hidden', 'S_key[.TODO = (CHOOSE ([GENERATOR_YIELD_KEY n_generator porigin_yield z_opcode]) eps z_opcode) :: ptask_key_tail*]')
            reject(checks, 'lost', 'S_key[.TODO = ptask_key_tail*]')
        previous = 'S_key'
    else:
        previous = 'S_initial'
    checks += seek('S_warning', previous, 1) + valid('S_warning')
    checks += r'''
S_warning.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warning_tail*
perrorcall.RESUME = ERROR_READ_RESULT perrorread
$error_read_valid(S_warning,perrorread)
$error_call_valid(S_warning,perrorcall)
perrorread.RESULT = KNOWN PNULL
perrorread.BASE = BASE_VALUE (KNOWN PNULL)
'''.strip().splitlines()
    if value_warning:
        checks += ['S_warning.CURRENT = (pcallcontext_generator)',
                   '$generator_context_operation(S_warning,pcallcontext_generator) = (pgeneratorop)',
                   'n_generator = pgeneratorop.OBJECT',
                   'S_warning.OBJECTS[n_generator] = GENERATOR pgenerator_key',
                   'perrorread.ORIGINAL = GENERATOR_YIELD_STORE porigin_yield (poperand_key)',
                   'perrorread.NAME = $ptascii("missingValue")',
                   'pgenerator_key.VALUE = eps /\\ pgenerator_key.KEY = eps']
    else:
        checks += ['perrorread.ORIGINAL = GENERATOR_YIELD_KEY n_generator porigin_yield z_opcode',
                   'perrorread.TASK = perrorread.ORIGINAL',
                   'perrorread.NAME = $ptascii("missingKey")',
                   '$task_nodes(perrorcall.RESUME) = eps',
                   'S_warning.OBJECTS[n_generator] = GENERATOR pgenerator_key']
    if name in ['normal-reference-owner', 'direct-throw-cache-owner']:
        checks += ['pgenerator_key.VALUE = (POBJECT n_payload)',
                   'pgenerator_key.CLOSURE = (n_closure)',
                   'S_warning.GLOBALTABLE = (psymboltable_global)',
                   '$trace_slot(S_warning,psymboltable_global.ENV,$ptascii("weak")) = POBJECT n_weak',
                   '$weakref_get(S_warning,n_weak) = POBJECT n_payload',
                   '$heap_owners($heap_graph(S_warning),HOBJECT n_payload) = '
                   + ('2' if name == 'normal-reference-owner' else '1')]
        if name == 'direct-throw-cache-owner':
            checks += ['$trace_slot(S_warning,psymboltable_global.ENV,$ptascii("weakArrow")) = POBJECT n_weak_closure',
                       '$weakref_get(S_warning,n_weak_closure) = POBJECT n_closure']
    else:
        checks += ['pgenerator_key.CLOSURE = eps']
        if not value_warning:
            checks += ['pgenerator_key.VALUE = (PINT 6)']
    checks += seek('S_callback', 'S_warning', 2) + valid('S_callback')
    checks += ['S_callback.CURRENT = (pcallcontext_handler)',
               '$error_context_current_call(S_callback,pcallcontext_handler) = (perrorcall_entered)',
               'perrorcall_entered.RESUME = perrorcall.RESUME',
               'S_callback.ERRORHANDLER.CALLBACK = eps']
    if name == 'normal-reference-owner':
        checks += seek('S_cleared', 'S_callback', 5) + valid('S_cleared')
        checks += ['S_cleared.OBJECTS[n_generator] = GENERATOR pgenerator_cleared',
                   'pgenerator_cleared.VALUE = (POBJECT n_payload)',
                   'pgenerator_cleared.KEY = eps',
                   '$heap_owners($heap_graph(S_cleared),HOBJECT n_payload) = 1',
                   '$weakref_get(S_cleared,n_weak) = POBJECT n_payload']
        previous = 'S_cleared'
    else:
        checks += seek('S_catch', 'S_callback', 3) + valid('S_catch')
        checks += ['S_catch.TODO = (CATCH_BIND porigin_catch n_catch n_throwable) :: ptask_catch_tail*',
                   'S_catch.OBJECTS[n_generator] = GENERATOR pgenerator_catch',
                   'pgenerator_catch.KEY = (PNULL)',
                   '$throwable_field(S_catch,n_throwable,"previous") = PNULL',
                   'S_catch.ERRORHANDLER.CALLBACK = (perrorcall.CALLBACK)']
        if name == 'direct-throw-cache-owner':
            checks += ['S_catch.CURRENT = eps', 'pgenerator_catch.PHASE = GENERATOR_CLOSED',
                       'pgenerator_catch.FRAME = eps',
                       'pgenerator_catch.VALUE = (POBJECT n_payload)',
                       '$trace_slot(S_catch,S_catch.ENV,$ptascii("error")) = POBJECT n_throwable',
                       '$heap_owners($heap_graph(S_catch),HOBJECT n_payload) = 1',
                       '$heap_owners($heap_graph(S_catch),HOBJECT n_closure) = 1',
                       '$weakref_get(S_catch,n_weak) = POBJECT n_payload',
                       '$weakref_get(S_catch,n_weak_closure) = POBJECT n_closure']
            previous = 'S_catch'
        else:
            checks += ['pgenerator_catch.PHASE = GENERATOR_RUNNING',
                       'pgenerator_catch.VALUE = (' + ('PNULL' if value_warning else 'PINT 6') + ')',
                       'S_catch.CURRENT = (pcallcontext_child)',
                       '$trace_context_function(S_catch,pcallcontext_child) = $ptascii("leaf321")',
                       'S_catch.FRAMES = pframe_resumer :: pframe_resumer_tail*',
                       'pframe_resumer.TODO = (GENERATOR_RESUME pgeneratorop_child) :: (GENERATOR_FROM_RESULT n_parent porigin_from n_generator) :: ptask_resumer_tail*',
                       '$generator_from_operation_tasks(S_catch,pgeneratorop_child,pframe_resumer.TODO,pframe_resumer.CONTEXT)']
            checks += seek('S_paused', 'S_catch', 4) + valid('S_paused')
            checks += ['S_paused.TODO = (GENERATOR_RESUME pgeneratorop_child) :: ptask_paused_tail*',
                       'S_paused.OBJECTS[n_generator] = GENERATOR pgenerator_paused',
                       'pgenerator_paused.VALUE = (PINT 12)',
                       'pgenerator_paused.KEY = (PINT 0)', 'pgenerator_paused.INDEX = 0']
            previous = 'S_paused'
    checks += [f'S_zero = $drive_steps({previous},0)',
               f'S_zero = {previous}[.COMPLETION = BUDGET]',
               'S_resumed = $drive(S_zero[.COMPLETION = NORMAL],4096)',
               f'S_direct = $drive({previous},4096)', 'S_resumed = S_direct',
               'S_resumed.COMPLETION = NORMAL', 'S_resumed.TODO = eps',
               'S_resumed.FRAMES = eps',
               '$yield_key_outputs(S_resumed.EVENTS) = ' + driver.driver.byte_expr(CASES[name][1])]
    checks += valid('S_resumed')
    if name in ['normal-reference-owner', 'direct-throw-cache-owner']:
        checks += ['$weakref_get(S_resumed,n_weak) = PNULL',
                   '~((HOBJECT n_payload) <- S_resumed.ALLOCATIONS)',
                   '~((HOBJECT n_closure) <- S_resumed.ALLOCATIONS)']
        if name == 'direct-throw-cache-owner':
            checks += ['$weakref_get(S_resumed,n_weak_closure) = PNULL']
    return checks


def main():
    driver.CASES = CASES
    driver.source.WATCHED = WATCHED
    driver.PREFIX = PREFIX
    driver.assertions = assertions
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())
