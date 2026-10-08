#!/usr/bin/env python3
"""A real delegated reference cache, warning reinjection and ordered close."""
import os

import generator_force_close_protocol as driver
import reference_yield_delegation_review as source

CASES = source.CASES
WATCHED = driver.source.WATCHED + [
    'spec/semantics/97-call-reference-acquisition.watsup',
    'spec/semantics/99-reference-returns.watsup',
    'spec/semantics/118-arrows.watsup',
    'spec/semantics/207-error-handler-runtime.watsup',
    'spec/semantics/270-eager-destructors.watsup',
    'spec/semantics/311-arrow-generators.watsup',
    'spec/semantics/321-yield-key-warning.watsup',
    'spec/semantics/328-generator-reference-yields.watsup',
    'tests/semantics/reference_yield_delegation_review.py',
    'tests/semantics/reference_yield_delegation_protocol.py',
]
PREFIX = r'''
dec $reference_delegation_phase(pstate,nat) : bool
def $reference_delegation_phase(S,0) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask*
  -- if perrorcall.RESUME = ERROR_READ_RESULT perrorread
  -- if perrorread.ORIGINAL = GENERATOR_YIELD_KEY n porigin z
def $reference_delegation_phase(S,1) = true
  -- if S.TODO = (CATCH_BIND porigin n_index n) :: ptask*
  -- if S.CURRENT = (pcallcontext)
  -- if $trace_context_function(S,pcallcontext) = $ptascii("leaf")
def $reference_delegation_phase(S,2) = true
  -- if S.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask*
  -- if S.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_PAUSED
  -- if pgenerator.REFCELL = (n_cell)
  -- if S.STORE[n_cell] = DEFINED (PINT 12)
def $reference_delegation_phase(S,3) = true
  -- if S.TODO = (STMT (NStmtUnset (SEQUENCE expression*) metadata)) :: ptask*
  -- if $close_outputs(S.EVENTS) = $ptascii("A|W|C1|12|15|")
def $reference_delegation_phase(S,4) = $close_body_named(S,"leaf")
def $reference_delegation_phase(S,5) = $close_body_named(S,"parent328")
def $reference_delegation_phase(S,n) = false -- otherwise
dec $reference_delegation_seek(pstate,nat,nat) : pstate
def $reference_delegation_seek(S,n_phase,n) = S
  -- if $reference_delegation_phase(S,n_phase)
def $reference_delegation_seek(S,n_phase,n) = S
  -- if ~$reference_delegation_phase(S,n_phase)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $reference_delegation_seek(S,n_phase,0) = S
  -- if ~$reference_delegation_phase(S,n_phase)
def $reference_delegation_seek(S,n_phase,n) = $reference_delegation_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_phase,$nabs($(n - 1)))
  -- if ~$reference_delegation_phase(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
'''


def seek(state, previous, phase):
    return [f'{state}_found = $reference_delegation_seek({previous},{phase},4096)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$reference_delegation_phase({state},{phase})']


def valid(state):
    return driver.valid(state) + [f'$generator_state_valid({state})',
                                 f'$call_entry_check({state}) = {state}']


def cache(state, record):
    return [f'{record}.VALUE = eps', f'{record}.REFCELL = (n_cell)',
            f'n_cell <- {state}.REFCELLS', f'(HCELL n_cell) <- {state}.ALLOCATIONS',
            f'H_{state} = $heap_graph({state})',
            f'H_{state}_uncached = $heap_graph($generator_set({state},n_child,{record}[.REFCELL = eps]))',
            f'$heap_owners(H_{state},HCELL n_cell) = $($heap_owners(H_{state}_uncached,HCELL n_cell) + 1)']


def assertions(checked, path, directory, name):
    initial = ('$php_file_run(' + checked['fixture'] + ',0,'
               + driver.driver.byte_expr(os.fsencode(path)) + ','
               + driver.driver.byte_expr(os.fsencode(driver.ROOT)) + ')')
    checks = ['S_initial = ' + initial, '~S_initial.COMPILESTOP']
    checks += seek('S_key', 'S_initial', 0) + valid('S_key')
    checks += r'''
S_key.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_key*
perrorcall.RESUME = ERROR_READ_RESULT perrorread
perrorread.ORIGINAL = GENERATOR_YIELD_KEY n_child porigin_key z
$error_call_valid(S_key,perrorcall)
S_key.OBJECTS[n_child] = GENERATOR pgenerator_key
pgenerator_key.PHASE = GENERATOR_RUNNING /\ pgenerator_key.FRAME = eps
pgenerator_key.KEY = eps /\ pgenerator_key.BORROWED = eps
pgenerator_key.REFCELL = (n_cell)
S_key.STORE[n_cell] = DEFINED (PINT 7)
S_key.GLOBALTABLE = (psymboltable_global)
$lookup(psymboltable_global.ENV,$ptascii("value")) = (n_cell)
$lookup(S_key.ENV,$ptascii("value")) = (n_cell)
$trace_slot(S_key,psymboltable_global.ENV,$ptascii("error")) = POBJECT n_throwable
S_key.FRAMES = pframe_resumer :: pframe_resumer_tail*
pframe_resumer.TODO = (GENERATOR_RESUME pgeneratorop_child) :: (GENERATOR_FROM_RESULT n_parent porigin_from n_child) :: ptask_resumer*
pgeneratorop_child.OBJECT = n_child
$generator_from_operation_tasks(S_key,pgeneratorop_child,pframe_resumer.TODO,pframe_resumer.CONTEXT)
pframe_resumer.LOCALS = (psymboltable_parent)
$lookup(psymboltable_parent.ENV,$ptascii("value")) = (n_cell)
S_key.OBJECTS[n_parent] = GENERATOR pgenerator_parent
pgenerator_parent.DELEGATE = (pgeneratorfrom_parent)
pgeneratorfrom_parent.INPUT = (POBJECT n_child)
$generator_cached_value(S_key,n_child,false) = PINT 7
'''.strip().splitlines()
    checks += cache('S_key', 'pgenerator_key')
    checks += seek('S_catch', 'S_key', 1) + valid('S_catch')
    checks += r'''
S_catch.TODO = (CATCH_BIND porigin_catch n_index n_throwable) :: ptask_catch*
S_catch.CURRENT = (pcallcontext_catch)
$trace_context_function(S_catch,pcallcontext_catch) = $ptascii("leaf")
S_catch.OBJECTS[n_child] = GENERATOR pgenerator_catch
pgenerator_catch.PHASE = GENERATOR_RUNNING /\ pgenerator_catch.FRAME = eps
pgenerator_catch.KEY = (PNULL) /\ pgenerator_catch.BORROWED = eps
S_catch.STORE[n_cell] = DEFINED (PINT 7)
$generator_yield_warning_throw(S_catch,n_throwable) = S_catch
$throwable_field(S_catch,n_throwable,"previous") = PNULL
'''.strip().splitlines()
    checks += cache('S_catch', 'pgenerator_catch')
    checks += seek('S_paused', 'S_catch', 2) + valid('S_paused')
    checks += r'''
S_paused.TODO = (GENERATOR_RESUME pgeneratorop_child) :: ptask_paused*
S_paused.OBJECTS[n_child] = GENERATOR pgenerator_paused
pgenerator_paused.KEY = (PINT 0) /\ pgenerator_paused.INDEX = 0
pgenerator_paused.BORROWED = eps
S_paused.STORE[n_cell] = DEFINED (PINT 12)
$generator_cached_value(S_paused,n_child,false) = PINT 12
'''.strip().splitlines()
    checks += cache('S_paused', 'pgenerator_paused')
    checks += seek('S_unset', 'S_paused', 3) + valid('S_unset')
    checks += r'''
$trace_slot(S_unset,S_unset.ENV,$ptascii("generator")) = POBJECT n_parent
$lookup(S_unset.ENV,$ptascii("value")) = (n_cell)
S_unset.STORE[n_cell] = DEFINED (PINT 15)
$generator_cached_value(S_unset,n_parent,false) = PINT 15
S_unset.OBJECTS[n_child] = GENERATOR pgenerator_unset
pgenerator_unset.KEY = (PINT 0)
'''.strip().splitlines()
    checks += cache('S_unset', 'pgenerator_unset')
    checks += seek('S_leaf', 'S_unset', 4) + valid('S_leaf')
    checks += r'''
$generator_close_saved(S_leaf,S_leaf.CURRENT,S_leaf.FRAMES) = (pgenclose_leaf)
pgenclose_leaf.OBJECT = n_child
pgenclose_leaf.STAGE = CLOSE_BODY porigin_leaf
S_leaf.OBJECTS[n_child] = GENERATOR pgenerator_leaf
pgenerator_leaf.PHASE = GENERATOR_RUNNING /\ pgenerator_leaf.FRAME = eps
$lookup(S_leaf.ENV,$ptascii("value")) = (n_cell)
S_leaf.STORE[n_cell] = DEFINED (PINT 15)
'''.strip().splitlines()
    checks += cache('S_leaf', 'pgenerator_leaf')
    checks += seek('S_parent', 'S_leaf', 5) + valid('S_parent')
    checks += r'''
$generator_close_saved(S_parent,S_parent.CURRENT,S_parent.FRAMES) = (pgenclose_parent)
pgenclose_parent.OBJECT = n_parent
pgenclose_parent.STAGE = CLOSE_BODY porigin_parent
~((HOBJECT n_child) <- S_parent.ALLOCATIONS)
$lookup(S_parent.ENV,$ptascii("value")) = (n_cell)
S_parent.STORE[n_cell] = DEFINED (PINT 15)
$close_outputs(S_parent.EVENTS) = $ptascii("A|W|C1|12|15|F|")
'''.strip().splitlines()
    checks += ['S_stopped = $drive_steps(S_parent,0)',
               'S_stopped = S_parent[.COMPLETION = BUDGET]',
               'S_resumed = $drive(S_stopped[.COMPLETION = NORMAL],4096)',
               'S_direct = $drive(S_parent,4096)', 'S_resumed = S_direct',
               'S_resumed.COMPLETION = NORMAL', 'S_resumed.TODO = eps',
               'S_resumed.FRAMES = eps', 'S_resumed.ITERATORS = eps',
               '$close_outputs_only(S_resumed.EVENTS)',
               '$close_outputs(S_resumed.EVENTS) = ' + driver.driver.byte_expr(CASES[name][1]),
               '~((HOBJECT n_child) <- S_resumed.ALLOCATIONS)',
               '~((HOBJECT n_parent) <- S_resumed.ALLOCATIONS)',
               '$lookup(S_resumed.ENV,$ptascii("value")) = (n_cell)',
               'S_resumed.STORE[n_cell] = DEFINED (PINT 15)',
               '$heap_owners($heap_graph(S_resumed),HCELL n_cell) = 1']
    checks += valid('S_resumed')
    return checks


def main():
    driver.CASES = CASES
    driver.PREFIX += PREFIX
    driver.assertions = assertions
    driver.source.WATCHED = WATCHED
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())
