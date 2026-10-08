#!/usr/bin/env python3
"""One genuine fresh STORE/typed-slot composition, with ordered source detach."""
import os

import generator_request_finally_protocol as base
import generator_fresh_typed_slot_join_sources as source
from reference_yield_protocol import valid

driver = base.driver
CASES = source.CASES
PREFIX = r'''
def $request_finally_phase(S,80) = true
  -- if S.TODO = [DESTRUCTOR_STORE]
  -- if $destructor_handle(S,S.DESTRUCTION.INDEX,0) = (n)
  -- if S.OBJECTS[n] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_FRESH
  -- if $generator_request_store_ready(S,n)
def $request_finally_phase(S,81) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin
  -- if $object_name(S,n) = $ptascii("FreshTypedChild349")
  -- if $trace_context_function(S,pcallcontext) = $ptascii("__destruct")
  -- if $close_outputs(S.EVENTS) = $ptascii("C|")
def $request_finally_phase(S,82) = true
  -- if S.TODO = (GENERATOR_CLOSE_RELEASE pgenrelease) :: ptask*
  -- if pgenrelease.JOBS = (DESTRUCTION_PROP_SOURCE pproptypesource n_cell) :: pdestructionjob*
'''


def assertions(checked, path, directory, name):
    initial = ('$php_file_run(' + checked['fixture'] + ',0,'
               + driver.driver.byte_expr(os.fsencode(path)) + ','
               + driver.driver.byte_expr(os.fsencode(driver.ROOT)) + ')')
    checks = ['S_initial = ' + initial, '~S_initial.COMPILESTOP']
    checks += base.seek('S_store', 'S_initial', 80) + valid('S_store')
    checks += [
        '$destructor_handle(S_store,S_store.DESTRUCTION.INDEX,0) = (n_generator)',
        'n_handle = S_store.DESTRUCTION.INDEX',
    ]
    checks += base.seek('S_child', 'S_store', 81) + valid('S_child')
    checks += r'''
S_child.CURRENT = (pcallcontext_child)
$destructor_context_call(pcallcontext_child,S_child.CURRENT,S_child.FRAMES) = (pdestructorcall)
~pdestructorcall.USER /\ pdestructorcall.CALLER = eps
pdestructorcall.FRAME = eps /\ pdestructorcall.OPERATION = eps
S_child.PROPREFS = [{CELL n_cell, SOURCES ([pproptypesource])}]
pproptypesource = OBJECT_PROP_SOURCE n_holder $ptascii("number") ppropertyid
~((HOBJECT n_holder) <- S_child.ALLOCATIONS)
$propref_source_valid(S_child,n_cell,pproptypesource)
$property_generator_source_count(S_child,n_cell,pproptypesource) = 1
S_child.OBJECTS[n_generator] = GENERATOR pgenerator_closed
$generator_request_fresh_closed(pgenerator_closed)
$heap_owners($heap_graph(S_child),HOBJECT n_generator) = 2
'''.strip().splitlines()
    checks += base.seek('S_slot', 'S_child', 82) + valid('S_slot')
    checks += r'''
S_slot.TODO = [GENERATOR_CLOSE_RELEASE pgenrelease, GENERATOR_CLOSE_DONE pgenclose, DESTRUCTOR_STORE]
pgenrelease.JOBS = (DESTRUCTION_PROP_SOURCE pproptypesource n_cell) :: pdestructionjob_tail*
(DESTRUCTION_HANDLE n_holder) <- pdestructionjob_tail*
pgenclose.OBJECT = n_generator
pgenclose.STORE = (n_handle)
pgenclose.SITE = pgenerator_closed.FUNCTION
pgenclose.STAGE = CLOSE_FINISHED /\ pgenclose.NEXT = 0 /\ pgenclose.FRAME = eps
$generator_close_done_valid(S_slot,pgenclose)
$propref_source_valid(S_slot,n_cell,pproptypesource)
$property_generator_source_count(S_slot,n_cell,pproptypesource) = 1
$close_outputs(S_slot.EVENTS) = $ptascii("C|A|type|")
S_detached_budget = $drive_steps(S_slot,1)
S_detached_budget.COMPLETION = BUDGET
S_detached = S_detached_budget[.COMPLETION = NORMAL]
S_detached.TODO = [GENERATOR_CLOSE_RELEASE pgenrelease[.JOBS = (DESTRUCTION_VALUE (HCELL n_cell)) :: pdestructionjob_tail*], GENERATOR_CLOSE_DONE pgenclose, DESTRUCTOR_STORE]
S_detached.PROPREFS = eps
~$propref_source_valid(S_detached,n_cell,pproptypesource)
$heap_owners($heap_graph(S_detached),HCELL n_cell) = $heap_owners($heap_graph(S_slot),HCELL n_cell)
'''.strip().splitlines()
    checks += valid('S_detached')
    base.finish(checks, 'S_slot', name)
    checks += ['S_resumed.PROPREFS = eps']
    return checks


def main():
    base.CASES = CASES
    driver.CASES = CASES
    driver.PREFIX += base.PREFIX + PREFIX
    driver.assertions = assertions
    driver.source.WATCHED += [
        'spec/semantics/222-exception-handlers.watsup',
        'spec/semantics/303-generator-force-close.watsup',
        'spec/semantics/340-generator-request-finally.watsup',
        'spec/semantics/346-typed-property-slot-retirement.watsup',
        'spec/semantics/349-generator-request-fresh.watsup',
        'tests/semantics/generator_request_finally_protocol.py',
        'tests/semantics/reference_yield_protocol.py',
        'tests/semantics/generator_fresh_typed_slot_join_sources.py',
        'tests/semantics/generator_fresh_typed_slot_join_protocol.py',
    ]
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())
