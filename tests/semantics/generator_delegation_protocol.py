#!/usr/bin/env python3
"""Source-reached delegation graph, raw cache and natural unwind checks."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

from recorded_worker import Worker
import generator_delegation_review as source
import generator_effects_review_protocol as effects
import typed_static_invoke_set_protocol as driver

ROOT = source.ROOT
CASES = {
    'actual-property-ingress': source.CASES['generator-fiber-arrayaccess-value-read-and-property-aliases'],
    'actual-property-access-owner': source.CASES['generator-fiber-arrayaccess-value-read-and-property-aliases'],
    'array-alias': source.CASES['array-reference-live-cache'],
    'shared-child': source.CASES['generator-shared-parents-progress-and-return'],
    'nested-child': source.CASES['generator-nested-completed-leaf-cache'],
    'detached-retval': source.CASES['generator-detached-reference-retval'],
    'iterator-rebind-current': source.CASES['iterator-current-reference-rebind'],
    'iterator-rebind-key': source.CASES['iterator-current-reference-rebind'],
    'iterator-rebind-cache': source.CASES['iterator-current-reference-rebind'],
    'iterator-unused-stages': source.CASES['iterator-callback-order-and-null-return'],
    'iterator-scopes': source.CASES['iterator-inherited-private-generator-scope'],
    'iterator-nan-owner': source.CASES['iterator-valid-nan-reference-retained'],
    'shared-abort': source.CASES['generator-shared-abort-distinct-exception'],
    'delegated-finally': source.CASES['generator-injected-finally-send'],
}
PREFIX = r'''
dec $delegation_global_env(pstate) : pbinding*
def $delegation_global_env(S) = S.ENV -- if S.GLOBALTABLE = eps
def $delegation_global_env(S) = psymboltable.ENV -- if S.GLOBALTABLE = (psymboltable)
dec $delegation_phase(pstate,nat) : bool
def $delegation_phase(S,0) = true
  -- if S.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask*
  -- if S.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_DELEGATING
  -- if pgenerator.DELEGATE = (pgeneratorfrom)
  -- if pgeneratorfrom.INPUT = (PARRAY n)
  -- if pgeneratorfrom.CURRENT = (REFERENCE n_cell)
def $delegation_phase(S,1) = true
  -- if S.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask*
  -- if S.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_DELEGATING
  -- if pgenerator.DELEGATE = (pgeneratorfrom)
  -- if pgeneratorfrom.INPUT = (PARRAY n)
  -- if pgeneratorfrom.CURRENT = (KNOWN (PINT 6))
def $delegation_phase(S,2) = true
  -- if S.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask*
  -- if S.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_CLOSED
def $delegation_phase(S,10) = true
  -- if S.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask*
  -- if pgeneratorop.NAME = "current"
  -- if $trace_slot(S,$delegation_global_env(S),$ptascii("a")) = POBJECT n_a
  -- if $trace_slot(S,$delegation_global_env(S),$ptascii("b")) = POBJECT pgeneratorop.OBJECT
  -- if S.OBJECTS[n_a] = GENERATOR pgenerator_a
  -- if S.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator_b
  -- if pgenerator_a.PHASE = GENERATOR_DELEGATING /\ pgenerator_b.PHASE = GENERATOR_DELEGATING
def $delegation_phase(S,11) = true
  -- if S.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask*
  -- if pgeneratorop.NAME = "next"
  -- if S.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_DELEGATING
  -- if pgenerator.DELEGATE = (pgeneratorfrom)
  -- if pgeneratorfrom.INPUT = (POBJECT n_child)
  -- if S.OBJECTS[n_child] = GENERATOR pgenerator_child
  -- if pgenerator_child.VALUE = (PINT 2)
def $delegation_phase(S,12) = true
  -- if $trace_slot(S,$delegation_global_env(S),$ptascii("g")) = POBJECT n_outer
  -- if S.RESULT = KNOWN (PINT 2)
  -- if S.OBJECTS[n_outer] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_DELEGATING
  -- if pgenerator.DELEGATE = (pgeneratorfrom)
  -- if pgeneratorfrom.INPUT = (POBJECT n_middle)
  -- if S.OBJECTS[n_middle] = GENERATOR pgenerator_middle
  -- if pgenerator_middle.DELEGATE = (pgeneratorfrom_middle)
  -- if pgeneratorfrom_middle.INPUT = eps
  -- if pgenerator_middle.FRAME = (pframe_middle)
  -- if pframe_middle.TODO = (GENERATOR_FROM_COMPLETE n_middle porigin_middle n_leaf pvalue) :: ptask_middle*
def $delegation_phase(S,20) = true
  -- if $trace_slot(S,$delegation_global_env(S),$ptascii("g")) = POBJECT n_parent
  -- if S.RESULT = KNOWN PNULL
  -- if S.OBJECTS[n_parent] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_DELEGATING
  -- if pgenerator.FRAME = (pframe)
  -- if pframe.TODO = (GENERATOR_FROM_COMPLETE n porigin n_child pvalue) :: ptask_frame*
def $delegation_phase(S,30) = true
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (GENERATOR_FROM_CALLBACK n porigin "current") :: ptask*
  -- if S.TODO = (RETURN_REF_FETCH z) :: ptask_tail*
def $delegation_phase(S,31) = true
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (GENERATOR_FROM_CALLBACK n porigin "key") :: ptask*
  -- if $generator_from_callback_frame(S,pcallcontext,pframe)
def $delegation_phase(S,32) = true
  -- if S.TODO = (GENERATOR_FROM_CALLBACK n porigin "key") :: ptask*
  -- if S.OBJECTS[n] = GENERATOR pgenerator
  -- if pgenerator.DELEGATE = (pgeneratorfrom)
  -- if pgeneratorfrom.CURRENT = (REFERENCE n_cell)
  -- if S.RESULT = KNOWN (PINT 0)
def $delegation_phase(S,33) = true
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (GENERATOR_FROM_CALLBACK n porigin "rewind") :: ptask*
  -- if $generator_from_callback_frame(S,pcallcontext,pframe)
def $delegation_phase(S,34) = true
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (GENERATOR_FROM_CALLBACK n porigin "next") :: ptask*
  -- if $generator_from_callback_frame(S,pcallcontext,pframe)
def $delegation_phase(S,39) = true
  -- if S.TODO = (THROW_SEARCH n_throw) :: ptask*
  -- if S.OBJECTS[n_throw] = THROWABLE pthrowable
  -- if pthrowable.KIND = "Exception"
  -- if $throwable_field(S,n_throw,"message") = PSTRING $ptascii("E")
def $delegation_phase(S,40) = true
  -- if S.TODO = (GENERATOR_FROM_NEXT n porigin) :: ptask*
  -- if S.OBJECTS[n] = GENERATOR pgenerator
  -- if pgenerator.DELEGATE = (pgeneratorfrom)
  -- if pgeneratorfrom.INPUT = (POBJECT n_child)
  -- if S.OBJECTS[n_child] = GENERATOR pgenerator_child
  -- if pgenerator_child.PHASE = GENERATOR_CLOSED /\ pgenerator_child.RETURN = eps
def $delegation_phase(S,50) = true
  -- if S.TODO = (GENERATOR_RESUME pgeneratorop) :: (GENERATOR_FROM_RESULT n porigin n_child) :: ptask*
  -- if pgeneratorop.NAME = "throw"
  -- if S.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_PAUSED
  -- if pgenerator.VALUE = (PINT 2)
  -- if pgenerator.FRAME = (pframe)
  -- if $effects_pending(pframe.TODO) =/= eps
def $delegation_phase(S,60) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $trace_context_function(S,pcallcontext) = $ptascii("warning")
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask*
  -- if perrorcall.RESUME = GENERATOR_FROM_VALID n porigin (REFERENCE n_cell)
  -- if S.GLOBALTABLE = (psymboltable)
  -- if $lookup(psymboltable.ENV,$ptascii("nan")) = eps
  -- if S.STORE[n_cell] = DEFINED (PFLOAT 4607182418800017408)
def $delegation_phase(S,70) = true
  -- if S.TODO = (KEY_READ_BASE (BASE_PROPERTY (POBJECT n) ptbytes) KEY_R) :: ptask*
  -- if ptbytes = $ptascii("b")
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.RECEIVER = (n)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (GENERATOR_FROM_CALLBACK n_owner porigin "current") :: ptask_frame*
def $delegation_phase(S,71) = true
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (ACCESS_RESULT paccess) :: ptask_frame*
  -- if paccess.PHASE = ACCESS_CALL $ptascii("offsetGet")
dec $delegation_outputs_only(pevent*) : bool
def $delegation_outputs_only(eps) = true
def $delegation_outputs_only((OUTPUT ptbytes) :: pevent*) = $delegation_outputs_only(pevent*)
def $delegation_outputs_only(pevent*) = false -- otherwise
def $delegation_phase(S,n) = false -- otherwise
dec $delegation_seek(pstate,nat,nat) : pstate
def $delegation_seek(S,n_phase,n) = S -- if S.COMPILESTOP
def $delegation_seek(S,n_phase,n) = S
  -- if ~S.COMPILESTOP
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $delegation_seek(S,n_phase,n) = S
  -- if ~S.COMPILESTOP
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $delegation_phase(S,n_phase)
def $delegation_seek(S,n_phase,n) = S
  -- if ~S.COMPILESTOP
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$delegation_phase(S,n_phase)
  -- if n = 0 \/ (S.TODO = eps /\ S.FRAMES = eps)
def $delegation_seek(S,n_phase,n) = $delegation_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_phase,$nabs($(n - 1)))
  -- if ~S.COMPILESTOP
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$delegation_phase(S,n_phase)
  -- if $(n > 0)
  -- if S.TODO =/= eps \/ S.FRAMES =/= eps
'''


def seek(state, previous, phase):
    return [f'{state}_found = $delegation_seek({previous},{phase},4096)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]', f'$delegation_phase({state},{phase})']


def valid(state):
    # Public admission conjoins generator/delegation, task, frame and current checks.
    return [f'$call_descriptors_valid({state})', f'$heap_valid($heap_graph({state}))']


def reject(checks, name, expression, guard='generator_state_valid'):
    state = 'S_bad_' + name
    checks += [state + ' = ' + expression, f'$heap_valid($heap_graph({state}))', f'~${guard}({state})']


def assertions(checked, path, directory, name):
    initial = '$php_file_run(' + checked['fixture'] + ',0,' + driver.byte_expr(os.fsencode(path)) + ',' + driver.byte_expr(os.fsencode(directory)) + ')'
    checks = ['S_initial = ' + initial, '~S_initial.COMPILESTOP']
    if name == 'actual-property-ingress':
        checks += seek('S_base', 'S_initial', 70) + valid('S_base')
        checks += r'''
S_base.TODO = (KEY_READ_BASE (BASE_PROPERTY (POBJECT n_iterator) $ptascii("b")) KEY_R) :: ptask_base*
S_base.CURRENT = (pcallcontext_current)
pcallcontext_current.RECEIVER = (n_iterator)
S_base.FRAMES = pframe_current :: pframe_current_tail*
pframe_current.TODO = (GENERATOR_FROM_CALLBACK n_owner porigin_site "current") :: ptask_current*
$reference_callback_used(S_base,pcallcontext_current) = (true)
$trace_slot(S_base,$delegation_global_env(S_base),$ptascii("bag")) = POBJECT n_bag
S_base.ORIGIN = (porigin_property)
$origin_node(S_base.SOURCES,porigin_property) = (NExprPropertyFetch expression (NIdentifier (BYTES "Yg==") metadata_name) metadata)
$property_resolve(S_base,n_iterator,$ptascii("b")) = PROPERTY_ACCESS $ptascii("b")
S_probe = $quiet_base(S_base,BASE_PROPERTY (POBJECT n_iterator) $ptascii("b"),$(-1))
S_probe = S_base[.RESULT = KNOWN (POBJECT n_bag)]
$access_base(S_base,BASE_PROPERTY (POBJECT n_iterator) $ptascii("b"))
~$access_base(S_base,BASE_PROPERTY (POBJECT n_iterator) $ptascii("i"))
~$access_base(S_base,BASE_PROPERTY (POBJECT n_iterator) $ptascii("missing"))
$task_nodes(KEY_READ_BASE (BASE_PROPERTY (POBJECT n_iterator) $ptascii("b")) KEY_R) = [HOBJECT n_iterator]
S_base.RESULT = KNOWN PNULL
S_fetched_budget = $drive_steps(S_base,1)
S_fetched_budget.COMPLETION = BUDGET
S_fetched = S_fetched_budget[.COMPLETION = NORMAL]
S_fetched.RESULT = KNOWN (POBJECT n_bag)
$heap_owners($heap_graph(S_fetched),HOBJECT n_iterator) = $($heap_owners($heap_graph(S_base),HOBJECT n_iterator) - 1)
$heap_owners($heap_graph(S_fetched),HOBJECT n_bag) = $($heap_owners($heap_graph(S_base),HOBJECT n_bag) + 1)
'''.strip().splitlines()
        checks += valid('S_fetched')
        return checks
    elif name == 'actual-property-access-owner':
        checks += seek('S_access', 'S_initial', 71) + valid('S_access')
        checks += r'''
S_access.CURRENT = (pcallcontext_get)
S_access.FRAMES = pframe_access :: pframe_current :: pframe_tail*
pframe_access.TODO = (ACCESS_RESULT paccess) :: ptask_access*
pframe_current.TODO = (GENERATOR_FROM_CALLBACK n_owner porigin_site "current") :: ptask_current*
pframe_access.CONTEXT = (pcallcontext_current)
pcallcontext_current.RECEIVER = (n_iterator)
paccess.MODE = ACCESS_READ KEY_R
paccess.PHASE = ACCESS_CALL $ptascii("offsetGet")
paccess.BASE = BASE_VALUE (KNOWN (POBJECT n_bag))
paccess.INPUT = KNOWN (PSTRING $ptascii("k"))
paccess.OFFSET = PSTRING $ptascii("k")
paccess.OBJECT = (n_bag)
paccess.OUTER
paccess.LINE = 15
paccess.TARGET = paccess.SITE
paccess.TASK = KEY_READ_DIM paccess.INPUT 15 KEY_R
pcallcontext_get.RECEIVER = (n_bag)
$reference_callback_used(S_access,pcallcontext_get) = eps
$task_nodes(ACCESS_RESULT paccess) = [HOBJECT n_bag,HOBJECT n_bag,HOBJECT n_bag]
$access_frame(S_access,pcallcontext_get,pframe_access)
S_caller = S_access[.ORIGIN = pframe_access.ORIGIN][.TODO = pframe_access.TODO]
$access_valid(S_caller,paccess)
paccess_bad_base = paccess[.BASE = BASE_PROPERTY (POBJECT n_iterator) $ptascii("b")]
~$access_valid(S_caller,paccess_bad_base)
paccess_bad_key = paccess[.INPUT = KNOWN (PSTRING $ptascii("q"))][.OFFSET = PSTRING $ptascii("q")][.TASK = KEY_READ_DIM (KNOWN (PSTRING $ptascii("q"))) 15 KEY_R]
~$access_valid(S_caller,paccess_bad_key)
'''.strip().splitlines()
        reject(checks, 'access_base', 'S_access[.FRAMES = pframe_access[.TODO = (ACCESS_RESULT paccess_bad_base) :: ptask_access*] :: pframe_current :: pframe_tail*]', 'call_descriptors_valid')
        reject(checks, 'access_key', 'S_access[.FRAMES = pframe_access[.TODO = (ACCESS_RESULT paccess_bad_key) :: ptask_access*] :: pframe_current :: pframe_tail*]', 'call_descriptors_valid')
        previous = 'S_access'
    elif name == 'array-alias':
        checks += seek('S_first', 'S_initial', 0) + valid('S_first')
        checks += r'''
S_first.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask_first*
S_first.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator_first
pgenerator_first.DELEGATE = (pgeneratorfrom_first)
pgeneratorfrom_first.INPUT = (PARRAY n_array)
pgeneratorfrom_first.CURRENT = (REFERENCE n_cell)
pgeneratorfrom_first.POSITION = 1
pgenerator_first.KEY = (PINT 0)
pgenerator_first.VALUE = eps
pgenerator_first.FRAME = (pframe_first)
pframe_first.TODO = (GENERATOR_FROM_NEXT pgeneratorop.OBJECT pgeneratorfrom_first.SITE) :: ptask_frame*
S_first.STORE[n_cell] = DEFINED (PINT 4)
$heap_owners($heap_graph(S_first),HARRAY n_array) = 3
$heap_owners($heap_graph(S_first),HCELL n_cell) = 3
$generator_cached_value(S_first,pgeneratorop.OBJECT,false) = PINT 4
'''.strip().splitlines()
        reject(checks, 'array_cursor', '$generator_set(S_first,pgeneratorop.OBJECT,pgenerator_first[.DELEGATE = (pgeneratorfrom_first[.POSITION = $(S_first.ARRAYS[n_array].SERIAL + 1)])])')
        reject(checks, 'input_type', '$generator_set(S_first,pgeneratorop.OBJECT,pgenerator_first[.DELEGATE = (pgeneratorfrom_first[.INPUT = (PINT 1)])])')
        reject(checks, 'source_site', '$generator_set(S_first,pgeneratorop.OBJECT,pgenerator_first[.DELEGATE = (pgeneratorfrom_first[.SITE = pgenerator_first.FUNCTION])])')
        for label, todo in [('missing_claim', 'ptask_frame*'), ('duplicate_claim', '(GENERATOR_FROM_NEXT pgeneratorop.OBJECT pgeneratorfrom_first.SITE) :: pframe_first.TODO'), ('wrapped_claim', '(AT pgeneratorfrom_first.SITE (GENERATOR_FROM_NEXT pgeneratorop.OBJECT pgeneratorfrom_first.SITE)) :: ptask_frame*'), ('stranded_claim', 'DISCARD :: pframe_first.TODO')]:
            reject(checks, label, f'$generator_set(S_first,pgeneratorop.OBJECT,pgenerator_first[.FRAME = (pframe_first[.TODO = {todo}])])')
        checks += seek('S_second', 'S_first', 1) + valid('S_second')
        checks += r'''
S_second.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator_second
pgenerator_second.DELEGATE = (pgeneratorfrom_second)
pgeneratorfrom_second.INPUT = (PARRAY n_array)
pgeneratorfrom_second.CURRENT = (KNOWN (PINT 6))
pgeneratorfrom_second.POSITION = 2
S_second.STORE[n_cell] = DEFINED (PINT 9)
$heap_owners($heap_graph(S_second),HARRAY n_array) = 2
$generator_cached_value(S_second,pgeneratorop.OBJECT,false) = PINT 6
'''.strip().splitlines()
        checks += seek('S_closed', 'S_second', 2) + valid('S_closed')
        checks += r'''
S_closed.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator_closed
pgenerator_closed.FRAME = eps
pgenerator_closed.RETURN = (PNULL)
pgenerator_closed.DELEGATE = (pgeneratorfrom_closed)
pgeneratorfrom_closed.INPUT = eps
~((HARRAY n_array) <- S_closed.ALLOCATIONS)
$heap_owners($heap_graph(S_closed),HCELL n_cell) = 2
'''.strip().splitlines()
        previous = 'S_closed'
    elif name == 'shared-child':
        checks += seek('S_shared', 'S_initial', 10) + valid('S_shared')
        checks += r'''
$trace_slot(S_shared,$delegation_global_env(S_shared),$ptascii("i")) = POBJECT n_child
$trace_slot(S_shared,$delegation_global_env(S_shared),$ptascii("a")) = POBJECT n_a
$trace_slot(S_shared,$delegation_global_env(S_shared),$ptascii("b")) = POBJECT n_b
S_shared.OBJECTS[n_a] = GENERATOR pgenerator_a
S_shared.OBJECTS[n_b] = GENERATOR pgenerator_b
pgenerator_a.DELEGATE = (pgeneratorfrom_a)
pgenerator_b.DELEGATE = (pgeneratorfrom_b)
pgeneratorfrom_a.INPUT = (POBJECT n_child)
pgeneratorfrom_b.INPUT = (POBJECT n_child)
pgenerator_a.FRAME = (pframe_a)
pgenerator_b.FRAME = (pframe_b)
pframe_a.TODO = (GENERATOR_FROM_NEXT n_a pgeneratorfrom_a.SITE) :: ptask_a*
pframe_b.TODO = (GENERATOR_FROM_NEXT n_b pgeneratorfrom_b.SITE) :: ptask_b*
$heap_owners($heap_graph(S_shared),HOBJECT n_child) = 5
$generator_cached_value(S_shared,n_a,false) = PINT 1
$generator_cached_value(S_shared,n_b,false) = PINT 1
'''.strip().splitlines()
        reject(checks, 'child_cycle', '$generator_set(S_shared,n_a,pgenerator_a[.DELEGATE = (pgeneratorfrom_a[.INPUT = (POBJECT n_a)])])')
        reject(checks, 'sibling_claim', '$generator_set(S_shared,n_a,pgenerator_a[.FRAME = (pframe_a[.TODO = (GENERATOR_FROM_NEXT n_b pgeneratorfrom_b.SITE) :: ptask_a*])])')
        checks += seek('S_advanced', 'S_shared', 11) + valid('S_advanced')
        checks += ['$generator_cached_value(S_advanced,n_a,false) = PINT 2', '$generator_cached_value(S_advanced,n_b,false) = PINT 2', '$heap_owners($heap_graph(S_advanced),HOBJECT n_child) = 5']
        previous = 'S_advanced'
    elif name == 'nested-child':
        checks += seek('S_nested', 'S_initial', 12) + valid('S_nested')
        checks += r'''
$trace_slot(S_nested,$delegation_global_env(S_nested),$ptascii("g")) = POBJECT n_outer
S_nested.OBJECTS[n_outer] = GENERATOR pgenerator_outer
pgenerator_outer.DELEGATE = (pgeneratorfrom_outer)
pgeneratorfrom_outer.INPUT = (POBJECT n_middle)
S_nested.OBJECTS[n_middle] = GENERATOR pgenerator_middle
pgenerator_middle.PHASE = GENERATOR_DELEGATING
pgenerator_middle.DELEGATE = (pgeneratorfrom_middle)
pgeneratorfrom_middle.INPUT = eps
pgeneratorfrom_middle.CURRENT = (KNOWN (PINT 2))
pgenerator_middle.FRAME = (pframe_middle)
pframe_middle.TODO = (GENERATOR_FROM_COMPLETE n_middle pgeneratorfrom_middle.SITE n_leaf (PINT 7)) :: ptask_middle*
S_nested.OBJECTS[n_leaf] = GENERATOR pgenerator_leaf
pgenerator_leaf.PHASE = GENERATOR_CLOSED
pgenerator_leaf.RETURN = (PINT 7)
$generator_cached_value(S_nested,n_outer,false) = PINT 2
$generator_cached_value(S_nested,n_outer,true) = PNULL
$generator_cache_present(S_nested,n_outer)
$heap_owners($heap_graph(S_nested),HOBJECT n_leaf) = 2
$heap_owners($heap_graph(S_nested),HOBJECT n_middle) = 3
$task_nodes(GENERATOR_FROM_COMPLETE n_middle pgeneratorfrom_middle.SITE n_leaf (PINT 7)) = eps
'''.strip().splitlines()
        reject(checks, 'nested_cycle', '$generator_set(S_nested,n_middle,pgenerator_middle[.DELEGATE = (pgeneratorfrom_middle[.INPUT = (POBJECT n_outer)])])')
        reject(checks, 'nested_return', '$generator_set(S_nested,n_middle,pgenerator_middle[.FRAME = (pframe_middle[.TODO = (GENERATOR_FROM_COMPLETE n_middle pgeneratorfrom_middle.SITE n_leaf (PINT 8)) :: ptask_middle*])])', 'call_descriptors_valid')
        previous = 'S_nested'
    elif name == 'detached-retval':
        checks += seek('S_detached', 'S_initial', 20) + valid('S_detached')
        checks += r'''
$trace_slot(S_detached,$delegation_global_env(S_detached),$ptascii("g")) = POBJECT n_parent
S_detached.OBJECTS[n_parent] = GENERATOR pgenerator_detached
pgenerator_detached.DELEGATE = (pgeneratorfrom_detached)
pgeneratorfrom_detached.INPUT = eps
pgeneratorfrom_detached.CURRENT = (KNOWN (PARRAY n_cache))
pgenerator_detached.FRAME = (pframe_detached)
pframe_detached.TODO = (GENERATOR_FROM_COMPLETE n_parent pgeneratorfrom_detached.SITE n_child (PARRAY n_return)) :: ptask_frame*
n_cache =/= n_return
~((HOBJECT n_child) <- S_detached.ALLOCATIONS)
$task_nodes(GENERATOR_FROM_COMPLETE n_parent pgeneratorfrom_detached.SITE n_child (PARRAY n_return)) = [HARRAY n_return]
$heap_owners($heap_graph(S_detached),HARRAY n_cache) = 1
$heap_owners($heap_graph(S_detached),HARRAY n_return) = 1
S_detached.ARRAYS[n_cache].ITEMS = [ENTRY (KINT 0) (ALIAS n_cell)]
S_detached.ARRAYS[n_return].ITEMS = [ENTRY (KINT 0) (ALIAS n_cell)]
$heap_owners($heap_graph(S_detached),HCELL n_cell) = 3
$generator_cached_value(S_detached,n_parent,true) = PNULL
$generator_cache_present(S_detached,n_parent)
'''.strip().splitlines()
        reject(checks, 'forged_return', '$generator_set(S_detached,n_parent,pgenerator_detached[.FRAME = (pframe_detached[.TODO = (GENERATOR_FROM_COMPLETE n_parent pgeneratorfrom_detached.SITE n_child (PARRAY n_cache)) :: ptask_frame*])])', 'call_descriptors_valid')
        reject(checks, 'forged_child', '$generator_set(S_detached,n_parent,pgenerator_detached[.FRAME = (pframe_detached[.TODO = (GENERATOR_FROM_COMPLETE n_parent pgeneratorfrom_detached.SITE n_parent (PARRAY n_return)) :: ptask_frame*])])', 'call_descriptors_valid')
        previous = 'S_detached'
    elif name in ['iterator-rebind-current', 'iterator-rebind-key', 'iterator-rebind-cache']:
        if name == 'iterator-rebind-current':
            checks += seek('S_current', 'S_initial', 30) + valid('S_current')
            checks += r'''
S_current.CURRENT = (pcallcontext_current)
S_current.FRAMES = pframe_current :: pframe_current_tail*
pframe_current.TODO = (GENERATOR_FROM_CALLBACK n_owner porigin_site "current") :: ptask_current*
$reference_callback_used(S_current,pcallcontext_current) = (true)
$reference_return_used(S_current)
~$reference_call_used(S_current,porigin_site)
pcallcontext_current.CALLSITE = (porigin_site)
pcallcontext_current.LINE = $generator_from_line(S_current,porigin_site)
pcallcontext_current.RECEIVER = (n_iterator)
$trace_context(S_current,S_current.ENV,S_current.CURRENT) = [ptraceframe_current]
ptraceframe_current.FUNCTION = $ptascii("current")
ptraceframe_current.CLASS = ($ptascii("It"))
ptraceframe_current.LINE = $generator_from_line(S_current,porigin_site)
ptraceframe_current.ARGS = eps
'''.strip().splitlines()
            reject(checks, 'callback_line', 'S_current[.CURRENT = (pcallcontext_current[.LINE = $(pcallcontext_current.LINE + 1)])]', 'call_descriptors_valid')
            reject(checks, 'callback_stage', 'S_current[.FRAMES = pframe_current[.TODO = (GENERATOR_FROM_CALLBACK n_owner porigin_site "next") :: ptask_current*] :: pframe_current_tail*]', 'call_descriptors_valid')
            reject(checks, 'callback_owner', 'S_current[.FRAMES = pframe_current[.TODO = (GENERATOR_FROM_CALLBACK n_iterator porigin_site "current") :: ptask_current*] :: pframe_current_tail*]', 'call_descriptors_valid')
            return checks
        else:
            if name == 'iterator-rebind-cache':
                checks += seek('S_current', 'S_initial', 30)
                checks += ['S_current.FRAMES = pframe_current :: pframe_current_tail*',
                           'pframe_current.TODO = (GENERATOR_FROM_CALLBACK n_owner porigin_site "current") :: ptask_current*',
                           'S_current.CURRENT = (pcallcontext_current)',
                           'pcallcontext_current.RECEIVER = (n_iterator)']
                checks += seek('S_key', 'S_current', 31)
            else:
                checks += seek('S_key', 'S_initial', 31)
            if name == 'iterator-rebind-key':
                checks += valid('S_key')
            checks += r'''
S_key.CURRENT = (pcallcontext_key)
S_key.FRAMES = pframe_key :: pframe_key_tail*
pframe_key.TODO = (GENERATOR_FROM_CALLBACK n_owner porigin_site "key") :: ptask_key*
S_key.OBJECTS[n_owner] = GENERATOR pgenerator_key
pgenerator_key.DELEGATE = (pgeneratorfrom_key)
pgeneratorfrom_key.INPUT = (POBJECT n_iterator)
pgeneratorfrom_key.CURRENT = (REFERENCE n_old)
S_key.STORE[n_old] = DEFINED (PINT 7)
$reference_callback_used(S_key,pcallcontext_key) = (true)
'''.strip().splitlines()
            if name == 'iterator-rebind-key':
                return checks
            if name == 'iterator-rebind-cache':
                checks += seek('S_cached', 'S_key', 32) + valid('S_cached')
                checks += r'''
S_cached.OBJECTS[n_owner] = GENERATOR pgenerator_cached
pgenerator_cached.DELEGATE = (pgeneratorfrom_cached)
pgeneratorfrom_cached.CURRENT = (REFERENCE n_old)
S_cached.GLOBALTABLE = (psymboltable_global)
$trace_slot(S_cached,psymboltable_global.ENV,$ptascii("replacement")) = PINT 9
$objectprops_at(S_cached.OBJECTPROPS,n_iterator) = (ppropertyslot*)
$property_slot_at(ppropertyslot*,$ptascii("v")) = (ppropertyslot_v)
ppropertyslot_v.STATE = PROP_VALUE (ALIAS n_new)
n_new =/= n_old
S_cached.STORE[n_old] = DEFINED (PINT 7)
S_cached.STORE[n_new] = DEFINED (PINT 9)
$generator_cached_value(S_cached,n_owner,false) = PINT 7
'''.strip().splitlines()
                previous = 'S_cached'
    elif name == 'iterator-unused-stages':
        checks += seek('S_rewind', 'S_initial', 33) + valid('S_rewind')
        checks += r'''
S_rewind.CURRENT = (pcallcontext_rewind)
pcallcontext_rewind.CALLSITE = (porigin_site)
$reference_call_used(S_rewind,porigin_site)
$reference_callback_used(S_rewind,pcallcontext_rewind) = (false)
~$reference_return_used(S_rewind)
'''.strip().splitlines()
        checks += seek('S_next', 'S_rewind', 34) + valid('S_next')
        checks += r'''
S_next.CURRENT = (pcallcontext_next)
pcallcontext_next.CALLSITE = (porigin_site)
$reference_call_used(S_next,porigin_site)
$reference_callback_used(S_next,pcallcontext_next) = (false)
~$reference_return_used(S_next)
'''.strip().splitlines()
        previous = 'S_next'
    elif name == 'iterator-scopes':
        checks += seek('S_scope', 'S_initial', 31) + valid('S_scope')
        checks += r'''
S_scope.CURRENT = (pcallcontext_key)
S_scope.FRAMES = pframe_owner :: pframe_owner_tail*
pframe_owner.TODO = (GENERATOR_FROM_CALLBACK n_owner porigin_site "key") :: ptask_owner*
pframe_owner.CONTEXT = (pcallcontext_owner)
$trace_context_class(S_scope,pcallcontext_key) = ($ptascii("It"))
pcallcontext_key.LEXICAL_CLASS = (porigin_it)
pcallcontext_key.CALLED_CLASS = (porigin_derived)
$class_at(S_scope.CLASSES,porigin_it) = (pclassdesc_it)
$class_at(S_scope.CLASSES,porigin_derived) = (pclassdesc_derived)
pclassdesc_it.NAME = $ptascii("It")
pclassdesc_derived.NAME = $ptascii("DerivedIt")
pcallcontext_owner.LEXICAL_CLASS = (porigin_owner)
pcallcontext_owner.CALLED_CLASS = (porigin_child)
$class_at(S_scope.CLASSES,porigin_owner) = (pclassdesc_owner)
$class_at(S_scope.CLASSES,porigin_child) = (pclassdesc_child)
pclassdesc_owner.NAME = $ptascii("Owner")
pclassdesc_child.NAME = $ptascii("Child")
pcallcontext_owner.RECEIVER = (n_creator)
(HOBJECT n_creator) <- S_scope.ALLOCATIONS
S_scope.GLOBALTABLE = (psymboltable_global)
$lookup(psymboltable_global.ENV,$ptascii("o")) = eps
$heap_owners($heap_graph(S_scope),HOBJECT n_creator) = 1
'''.strip().splitlines()
        previous = 'S_scope'
    elif name == 'iterator-nan-owner':
        checks += seek('S_warning', 'S_initial', 60) + valid('S_warning')
        checks += r'''
S_warning.CURRENT = (pcallcontext_warning)
S_warning.FRAMES = pframe_warning :: pframe_warning_tail*
pframe_warning.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_warning*
perrorcall.RESUME = GENERATOR_FROM_VALID n_owner porigin_site (REFERENCE n_old)
perrorcall.LEVEL = 2
perrorcall.MESSAGE = $ptascii("unexpected NAN value was coerced to bool")
perrorcall.LINE = $generator_from_line(S_warning,porigin_site)
$task_nodes(perrorcall.RESUME) = [HCELL n_old]
$heap_owners($heap_graph(S_warning),HCELL n_old) = 1
S_warning.STORE[n_old] = DEFINED (PFLOAT 4607182418800017408)
$generator_from_valid_decision(S_warning,REFERENCE n_old) = (true)
$generator_from_valid_decision(S_warning[.STORE[n_old] = DEFINED (PFLOAT 0)],REFERENCE n_old) = (false)
$reference_callback_used(S_warning,pcallcontext_warning) = eps
S_warning.OBJECTS[n_owner] = GENERATOR pgenerator_owner
pgenerator_owner.DELEGATE = (pgeneratorfrom_owner)
pgeneratorfrom_owner.INPUT = (POBJECT n_iterator)
$objectprops_at(S_warning.OBJECTPROPS,n_iterator) = (ppropertyslot*)
$property_slot_at(ppropertyslot*,$ptascii("v")) = (ppropertyslot_v)
ppropertyslot_v.STATE = PROP_VALUE (ALIAS n_new)
n_new =/= n_old
S_warning.STORE[n_new] = DEFINED (PBOOL false)
'''.strip().splitlines()
        for label, mutation in [('nan_line', '.LINE = $(perrorcall.LINE + 1)'), ('nan_message', '.MESSAGE = $ptascii("other")'), ('nan_level', '.LEVEL = 8'), ('nan_owner', '.RESUME = GENERATOR_FROM_VALID n_iterator porigin_site (REFERENCE n_old)'), ('nan_false', '.RESUME = GENERATOR_FROM_VALID n_owner porigin_site (KNOWN (PBOOL false))')]:
            reject(checks, label, f'S_warning[.FRAMES = pframe_warning[.TODO = (ERROR_HANDLER_RESULT perrorcall[{mutation}]) :: ptask_warning*] :: pframe_warning_tail*]', 'call_descriptors_valid')
        previous = 'S_warning'
    elif name == 'shared-abort':
        checks += seek('S_original', 'S_initial', 39) + valid('S_original')
        checks += ['S_original.TODO = (THROW_SEARCH n_original) :: ptask_original*',
                   'S_original.OBJECTS[n_original] = THROWABLE pthrowable_original',
                   'pthrowable_original.KIND = "Exception"']
        checks += seek('S_restored', 'S_original', 40) + valid('S_restored')
        checks += r'''
S_restored.TODO = (GENERATOR_FROM_NEXT n_parent porigin_site) :: ptask_parent*
S_restored.FRAMES = pframe_resumer :: pframe_resumer_tail*
pframe_resumer.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask_resumer*
pgeneratorop.OBJECT = n_parent
S_restored.OBJECTS[n_parent] = GENERATOR pgenerator_parent
pgenerator_parent.PHASE = GENERATOR_RUNNING
pgenerator_parent.FRAME = eps
S_restored.COMPLETION = NORMAL
S_throw_stop = $drive_steps(S_restored,1)
S_throw_stop.COMPLETION = BUDGET
S_throw = S_throw_stop[.COMPLETION = NORMAL]
S_throw.TODO = (THROW_SEARCH n_throw) :: ptask_parent*
$throwable_member(S_throw,n_throw)
n_throw =/= n_original
n_throw = |S_restored.OBJECTS|
S_throw.OBJECTS[n_throw] = THROWABLE pthrowable_closed
pthrowable_closed.KIND = "ClosedGeneratorException"
$throwable_field(S_throw,n_throw,"previous") = PNULL
S_throw.OBJECTS[n_parent] = GENERATOR pgenerator_throw
pgenerator_throw.DELEGATE = (pgeneratorfrom_throw)
pgeneratorfrom_throw.INPUT = eps
'''.strip().splitlines()
        checks += valid('S_throw')
        reject(checks, 'doubled_next', 'S_restored[.TODO = (GENERATOR_FROM_NEXT n_parent porigin_site) :: S_restored.TODO]', 'call_descriptors_valid')
        previous = 'S_throw'
    else:
        checks += seek('S_finally', 'S_initial', 50) + valid('S_finally')
        checks += r'''
S_finally.TODO = (GENERATOR_RESUME pgeneratorop_child) :: (GENERATOR_FROM_RESULT n_parent porigin_site n_child) :: ptask_parent*
pgeneratorop_child.OBJECT = n_child
pgeneratorop_child.ARGUMENTS = [POBJECT n_throw]
$generator_operation_trace(S_finally,pgeneratorop_child) = eps
S_finally.OBJECTS[n_child] = GENERATOR pgenerator_child
pgenerator_child.FRAME = (pframe_child)
$effects_pending(pframe_child.TODO) = (FINALLY_RESUME porigin_finally (n_throw))
$task_nodes(FINALLY_RESUME porigin_finally (n_throw)) = [HOBJECT n_throw]
S_finally.OBJECTS[n_parent] = GENERATOR pgenerator_parent
pgenerator_parent.PHASE = GENERATOR_RUNNING
pgenerator_parent.FRAME = eps
'''.strip().splitlines()
        reject(checks, 'forwarded_argument', 'S_finally[.TODO = (GENERATOR_RESUME pgeneratorop_child[.ARGUMENTS = [PINT 1]]) :: (GENERATOR_FROM_RESULT n_parent porigin_site n_child) :: ptask_parent*]', 'call_descriptors_valid')
        reject(checks, 'stranded_result', 'S_finally[.TODO = (GENERATOR_RESUME pgeneratorop_child) :: DISCARD :: (GENERATOR_FROM_RESULT n_parent porigin_site n_child) :: ptask_parent*]')
        previous = 'S_finally'
    checks += [f'S_stopped = $drive_steps({previous},0)', 'S_stopped.COMPLETION = BUDGET',
               f'S_stopped = {previous}[.COMPLETION = BUDGET]',
               'S_resumed = $drive(S_stopped[.COMPLETION = NORMAL],4096)',
               f'S_direct = $drive({previous},4096)', 'S_resumed = S_direct',
               'S_resumed.COMPLETION = NORMAL', 'S_resumed.TODO = eps', 'S_resumed.FRAMES = eps',
               'S_resumed.ITERATORS = eps', '$effects_outputs(S_resumed.EVENTS) = ' + driver.byte_expr(CASES[name][1])]
    checks += valid('S_resumed')
    if name == 'actual-property-access-owner':
        checks += ['$delegation_outputs_only(S_resumed.EVENTS)']
    if name == 'detached-retval':
        checks += ['~((HARRAY n_cache) <- S_resumed.ALLOCATIONS)', '~((HARRAY n_return) <- S_resumed.ALLOCATIONS)', '$heap_owners($heap_graph(S_resumed),HCELL n_cell) = 1']
    if name == 'iterator-nan-owner':
        checks += ['~((HCELL n_old) <- S_resumed.ALLOCATIONS)']
    return checks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['fixtures', 'prepare', 'check'], default='check')
    parser.add_argument('--select', help='Comma-separated exact case IDs')
    parser.add_argument('--sl', action='store_true', help='Use the existing strict SL fixture mode')
    args = parser.parse_args()
    names = args.select.split(',') if args.select else list(CASES)
    assert names and len(names) == len(set(names)) and all(n in CASES for n in names)
    out = Path(tempfile.mkdtemp(prefix='generator-delegation-protocol-', dir=ROOT / '.tools'))
    report = {'result': 'fail', 'mode': args.mode, 'backend': 'sl' if args.sl else 'al', 'records': [], 'assertions': 0,
              'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'profile': driver.types.PROFILE, 'environment': {'LC_ALL': 'C', 'TZ': 'UTC'}}
    print(out, flush=True)
    try:
        (out / 'candidate.diff').write_bytes(subprocess.check_output(['git', 'diff', 'HEAD'], cwd=ROOT))
        (out / 'case-fixture.py').write_bytes(Path(__file__).read_bytes())
        report['tools'] = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                           for path in [Path(__file__), ROOT / '.tools/php/bin/php', ROOT / '_build/default/adapter/main.exe']}
        if args.mode != 'fixtures':
            runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
            report['tools'][str(runner.relative_to(ROOT))] = hashlib.sha256(runner.read_bytes()).hexdigest()
        identity = source.run([str(driver.types.PHP), '-n', *driver.types.FLAGS, '-r',
                               'echo json_encode([PHP_VERSION,PHP_SAPI,PHP_INT_SIZE,PHP_ZTS,get_loaded_extensions(),ini_get_all(null,false)]);'], out / 'runtime', 10)
        assert identity.returncode == 0 and not identity.stderr
        report['runtime'] = json.loads(identity.stdout)
        assert report['runtime'][:4] == ['8.5.10', 'cli', 8, False]
        assert all(report['runtime'][5][key] == value for key, value in driver.types.PROFILE.items())
        for name in names:
            directory = out / name
            directory.mkdir()
            path = directory / 'source.php'
            path.write_bytes(CASES[name][0])
            row = {'id': name, 'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'evaluated': args.mode == 'check'}
            report['records'].append(row)
            native = source.run([str(driver.types.PHP), '-n', *driver.types.FLAGS, str(path)], directory / 'native', 10)
            row.update(native_exit=native.returncode, native_stdout=driver.b64(native.stdout), native_stderr=driver.b64(native.stderr))
            assert native.returncode == 0 and native.stdout == CASES[name][1] and not native.stderr
            frontend = Worker([str(driver.types.PHP), '-n', *driver.types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], directory / 'frontend')
            try:
                parsed = frontend.request({'op': 'parse', 'source': driver.b64(path.read_bytes())})
                assert parsed['accepted']
                adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
                try:
                    checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
                finally:
                    adapter.close()
            finally:
                frontend.close()
            checks = assertions(checked, path, directory, name)
            (directory / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
            fixture = directory / 'protocol.watsup'
            fixture.write_text(effects.PREFIX + PREFIX + '\ndec $body() : bool\ndef $body() = true\n' +
                               ''.join('  -- if ' + check + '\n' for check in checks) +
                               '\ndec $main() : bool\ndef $main() = ' + ('true' if args.mode == 'prepare' else '$body()') + '\n')
            row['assertions'] = len(checks)
            if args.mode != 'fixtures':
                if args.sl:
                    modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
                    result = driver.process([str(runner), '--sl', *[str(ROOT / module) for module in modules], str(fixture)],
                                            directory / 'numeric', 300, ROOT)
                    assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
                else:
                    driver.numeric(fixture, directory)
            report['assertions'] += len(checks) if args.mode == 'check' else 0
            row['passed'] = True
            print(name, args.mode, 'pass', flush=True)
        report['result'] = 'pass'
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(out / 'report.json', report['result'], flush=True)


if __name__ == '__main__':
    main()
