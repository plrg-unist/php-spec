#!/usr/bin/env python3
"""Actual ordinary INSTANCE pin beneath the Generator request close carrier."""
import os

import generator_request_finally_protocol as base
import generator_request_delegation_instance_sources as source
from reference_yield_protocol import valid

driver = base.driver
CASES = source.CASES
PREFIX = r'''
def $request_finally_phase(S,200) = (S.TODO = [DESTRUCTOR_GLOBALS])
def $request_finally_phase(S,201) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin
  -- if $object_name(S,n) = $ptascii("ChildInputJoin360")
  -- if $trace_context_function(S,pcallcontext) = $ptascii("__destruct")
def $request_finally_phase(S,202) = true
  -- if S.TODO = (GENERATOR_CLOSE_ENTER pgenclose) :: ptask_tail*
  -- if $trace_context_function(S,pgenclose.CONTEXT) = $ptascii("outerInputJoin360")
def $request_finally_phase(S,203) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin
  -- if $object_name(S,n) = $ptascii("ChildInputJoin360")
  -- if S.RESULT = KNOWN (POBJECT n_outer)
  -- if S.OBJECTS[n_outer] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_CLOSING
'''


def assertions(checked, path, directory, name):
    initial = ('$php_file_run(' + checked['fixture'] + ',0,'
               + driver.driver.byte_expr(os.fsencode(path)) + ','
               + driver.driver.byte_expr(os.fsencode(driver.ROOT)) + ')')
    checks = ['S_initial = ' + initial, '~S_initial.COMPILESTOP']
    checks += base.seek('S_globals', 'S_initial', 200) + valid('S_globals')
    checks += r'''
$trace_slot(S_globals,S_globals.ENV,$ptascii("g")) = POBJECT n_outer
$trace_slot(S_globals,S_globals.ENV,$ptascii("wi")) = POBJECT n_wi
$trace_slot(S_globals,S_globals.ENV,$ptascii("wg")) = POBJECT n_wg
S_globals.OBJECTS[n_outer] = GENERATOR pgenerator_outer
pgenerator_outer.PHASE = GENERATOR_DELEGATING
pgenerator_outer.DELEGATE = (pgeneratorfrom_outer)
pgeneratorfrom_outer.INPUT = (POBJECT n_iterator)
pgeneratorfrom_outer.CURRENT = (KNOWN (PINT 7))
$heap_owners($heap_graph(S_globals),HOBJECT n_iterator) = 1
'''.strip().splitlines()
    checks += base.seek('S_child', 'S_globals', 201) + valid('S_child')
    checks += r'''
S_child.CURRENT = (pcallcontext_child)
pcallcontext_child.TARGET = METHOD_TARGET n_child porigin_child
S_child.FRAMES = [pframe_root]
S_root = $constant_frame_scope(S_child,pframe_root,eps)
$instance_storage_for(S_child,n_iterator) = (pinstancestorage)
$instance_storage_valid(S_root,pinstancestorage)
pinstancestorage.OBJECT = n_iterator
pinstancestorage.NEXT = 1 /\ |pinstancestorage.SLOTS| = 1
~pinstancestorage.USER
pinstancestorage.CALLER = eps /\ pinstancestorage.ORIGIN = eps /\ pinstancestorage.CONSTCONTEXT = eps
$heap_owners($heap_graph(S_child),HOBJECT n_iterator) = 1
$heap_owners($heap_graph(S_child),HOBJECT n_outer) = 1
pcallcontext_child.RECEIVER = (n_child)
$heap_owners($heap_graph(S_child),HOBJECT n_child) = 2
$heap_owners($heap_graph(S_child[.CURRENT = eps]),HOBJECT n_child) = 1
(HOBJECT n_iterator) <- S_child.ALLOCATIONS
$instance_storage_freeing(S_child,n_iterator)
$weakref_get(S_child,n_wi) = PNULL
$weakref_get(S_child,n_wg) = POBJECT n_outer
S_child.OBJECTS[n_outer] = GENERATOR pgenerator_closing
pgenerator_closing.PHASE = GENERATOR_CLOSING /\ pgenerator_closing.FRAME = eps
$generator_from_input_of(pgenerator_closing.DELEGATE) = eps
$generator_id_count($generator_close_frame_claims(S_child.FRAMES),n_outer) = 1
$close_outputs(S_child.EVENTS) = $ptascii("C|I")
'''.strip().splitlines()
    checks += base.seek('S_weak_result', 'S_child', 203) + valid('S_weak_result')
    checks += r'''
S_weak_result.RESULT = KNOWN (POBJECT n_outer)
$heap_owners($heap_graph(S_weak_result),HOBJECT n_outer) = 2
$heap_owners($heap_graph(S_weak_result[.RESULT = KNOWN PNULL]),HOBJECT n_outer) = 1
$instance_storage_for(S_weak_result,n_iterator) = (pinstancestorage)
$weakref_get(S_weak_result,n_wi) = PNULL
$weakref_get(S_weak_result,n_wg) = POBJECT n_outer
'''.strip().splitlines()
    checks += base.seek('S_enter', 'S_weak_result', 202) + valid('S_enter')
    checks += r'''
S_enter.TODO = (GENERATOR_CLOSE_ENTER pgenclose_outer) :: ptask_after*
pgenclose_outer.OBJECT = n_outer
$generator_close_enter_valid(S_enter,pgenclose_outer)
~((HOBJECT n_iterator) <- S_enter.ALLOCATIONS)
~((HOBJECT n_child) <- S_enter.ALLOCATIONS)
$instance_storage_for(S_enter,n_iterator) = eps
$heap_owners($heap_graph(S_enter),HOBJECT n_outer) = 1
$close_outputs(S_enter.EVENTS) = $ptascii("C|ID1:1")
'''.strip().splitlines()
    base.finish(checks, 'S_weak_result', name)
    checks += ['~((HOBJECT n_outer) <- S_resumed.ALLOCATIONS)',
               '$weakref_get(S_resumed,n_wg) = PNULL']
    return checks


def main():
    base.CASES = CASES
    driver.CASES = CASES
    driver.PREFIX += base.PREFIX + PREFIX
    driver.assertions = assertions
    driver.source.WATCHED += [
        'spec/semantics/222-exception-handlers.watsup',
        'spec/semantics/257-request-destructors.watsup',
        'spec/semantics/281-fibers.watsup',
        'spec/semantics/289-generator-delegation.watsup',
        'spec/semantics/296-weak-references.watsup',
        'spec/semantics/303-generator-force-close.watsup',
        'spec/semantics/340-generator-request-finally.watsup',
        'spec/semantics/355-generator-storage-pin.watsup',
        'spec/semantics/359-instance-storage-pin.watsup',
        'spec/semantics/360-generator-request-delegation.watsup',
        'tests/semantics/generator_request_finally_protocol.py',
        'tests/semantics/reference_yield_protocol.py',
        'tests/semantics/generator_request_delegation_instance_sources.py',
        'tests/semantics/generator_request_delegation_instance_protocol.py',
    ]
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())
