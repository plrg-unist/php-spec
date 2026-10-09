#!/usr/bin/env python3
"""Reached report-release child fatal, real free_obj pins and notification order."""
import os

import generator_request_abrupt_protocol as fatal
import generator_request_instance_child_sources as source
from reference_yield_protocol import valid, reject

base = fatal.base
driver = fatal.driver
CASES = source.CASES
PREFIX = r'''
def $request_finally_phase(S,700) = true
  -- if S.TODO = (GENERATOR_REQUEST_REPORT pgenfatal) :: ptask_tail*
  -- if $object_name(S,pgenfatal.OBJECT) = $ptascii("RequestPinException21")
def $request_finally_phase(S,701) = true
  -- if S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_tail*
  -- if pdestructionrelease.JOBS = (DESTRUCTION_VALUE (HOBJECT n)) :: pdestructionjob*
  -- if $object_name(S,n) = $ptascii("RequestPinParent21")
def $request_finally_phase(S,702) = true
  -- if S.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask_tail*
  -- if $object_name(S,pinstancestorage.OBJECT) = $ptascii("RequestPinParent21")
  -- if pinstancestorage.NEXT = 0
def $request_finally_phase(S,703) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.RECEIVER = (n)
  -- if $object_name(S,n) = $ptascii("RequestPinLeaf21")
  -- if $close_outputs(S.EVENTS) = $ptascii("C|FHL1:1:1:1")
def $request_finally_phase(S,704) = true
  -- if S.TODO = (THROW_SEARCH n) :: (DESTRUCTOR_RESULT pdestructorcall) :: ptask_tail*
  -- if $object_name(S,pdestructorcall.OBJECT) = $ptascii("RequestPinLeaf21")
def $request_finally_phase(S,705) = true
  -- if S.TODO = (GENERATOR_REQUEST_BAILOUT pgenfatal) :: (DESTRUCTOR_RESULT pdestructorcall) :: ptask_tail*
dec $child_bailout_tasks(ptask*,pgenfatal,ptask*) : ptask*
def $child_bailout_tasks(eps,pgenfatal,ptask_replacement*) = eps
def $child_bailout_tasks((GENERATOR_REQUEST_BAILOUT pgenfatal) :: ptask_tail*,pgenfatal,ptask_replacement*) = ptask_replacement* ++ ptask_tail*
def $child_bailout_tasks(ptask :: ptask_tail*,pgenfatal,ptask_replacement*) = ptask :: $child_bailout_tasks(ptask_tail*,pgenfatal,ptask_replacement*)
  -- if ptask =/= GENERATOR_REQUEST_BAILOUT pgenfatal
dec $child_pin_tasks(ptask*,pinstancestorage,ptask*) : ptask*
def $child_pin_tasks(eps,pinstancestorage,ptask_replacement*) = eps
def $child_pin_tasks((INSTANCE_STORAGE_STEP pinstancestorage) :: ptask_tail*,pinstancestorage,ptask_replacement*) = ptask_replacement* ++ ptask_tail*
def $child_pin_tasks(ptask :: ptask_tail*,pinstancestorage,ptask_replacement*) = ptask :: $child_pin_tasks(ptask_tail*,pinstancestorage,ptask_replacement*)
  -- if ptask =/= INSTANCE_STORAGE_STEP pinstancestorage
dec $child_handle_tasks(ptask*,pdestructionrelease,ptask*) : ptask*
def $child_handle_tasks(eps,pdestructionrelease,ptask_replacement*) = eps
def $child_handle_tasks((DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_tail*,pdestructionrelease,ptask_replacement*) = ptask_replacement* ++ ptask_tail*
def $child_handle_tasks(ptask :: ptask_tail*,pdestructionrelease,ptask_replacement*) = ptask :: $child_handle_tasks(ptask_tail*,pdestructionrelease,ptask_replacement*)
  -- if ptask =/= DESTRUCTOR_RELEASE pdestructionrelease
'''


def one(checks, previous, state):
    checks += [f'{state}_found = $drive_steps({previous},1)',
               f'{state}_found.COMPLETION = BUDGET',
               f'{state} = {state}_found[.COMPLETION = NORMAL]']
    checks += fatal.normal_valid(state)


def terminal_reject(checks, label, expression, original, same_heap=True):
    state = 'S_bad_' + label
    relation = '=' if same_heap else '=/='
    checks += [f'{state} = {expression}', f'$heap_graph({state}) {relation} $heap_graph({original})',
               f'$heap_valid($heap_graph({state}))', f'~$call_descriptors_valid({state})',
               f'$call_entry_check({state}) = {state}']


def assertions(checked, path, directory, name, source=source):
    byte_expr = driver.driver.byte_expr
    first = byte_expr(source.FIRST_FATAL.replace(b'{file}', os.fsencode(path)))
    both = byte_expr((source.FIRST_FATAL + source.SECOND_FATAL).replace(b'{file}', os.fsencode(path)))
    cached_leaf = byte_expr(source.SECOND_FATAL.split(b'\n  thrown')[0].removeprefix(b'Fatal error: Uncaught ').replace(b'{file}', os.fsencode(path)))
    initial = ('$php_file_run(' + checked['fixture'] + ',0,'
               + byte_expr(os.fsencode(path)) + ',' + byte_expr(os.fsencode(driver.ROOT)) + ')')
    checks = ['S_initial = ' + initial, '~S_initial.COMPILESTOP']
    checks += base.seek('S_first', 'S_initial', 700) + fatal.normal_valid('S_first')
    checks += fatal.lines(r'''
S_first.TODO = (GENERATOR_REQUEST_REPORT pgenfatal_first) :: ptask_first_tail*
pgenfatal_first.SOURCE = THROW_SEARCH pgenfatal_first.OBJECT
ptask_first_tail* = (EXCEPTION_HANDLER_RESULT pexceptioncall) :: (GENERATOR_REQUEST_RESUME pgenclose) :: ptask_finish*
n_reported = pgenfatal_first.OBJECT
n_original = pexceptioncall.OBJECT
n_generator = pgenclose.OBJECT
S_first.OBJECTS[n_generator] = GENERATOR pgenerator
pgenerator.PHASE = GENERATOR_CLOSED /\ pgenerator.FRAME = eps
pgenerator.VALUE = (POBJECT n_payload)
S_first.EXCEPTIONHANDLER = eps
$generator_request_report_valid(S_first,pgenfatal_first)
$throwable_field(S_first,n_reported,"message") = PSTRING $ptascii("handler")
$throwable_field(S_first,n_original,"message") = PSTRING $ptascii("new")
$request_fatal_stderr(S_first.EVENTS) = eps
''')
    checks += base.seek('S_release', 'S_first', 701) + fatal.normal_valid('S_release')
    checks += fatal.lines(r'''
S_release.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_parent) :: ptask_release_tail*
pdestructionrelease_parent.JOBS = (DESTRUCTION_VALUE (HOBJECT n_parent)) :: pdestructionjob_parent*
$trace_slot(S_release,S_release.ENV,$ptascii("wb")) = POBJECT n_weak_parent
$trace_slot(S_release,S_release.ENV,$ptascii("wl")) = POBJECT n_weak_leaf
$trace_slot(S_release,S_release.ENV,$ptascii("wg")) = POBJECT n_weak_generator
$trace_slot(S_release,S_release.ENV,$ptascii("wp")) = POBJECT n_weak_payload
$weakref_get(S_release,n_weak_parent) = POBJECT n_parent
$weakref_get(S_release,n_weak_leaf) = POBJECT n_leaf
$weakref_get(S_release,n_weak_generator) = POBJECT n_generator
$weakref_get(S_release,n_weak_payload) = POBJECT n_payload
$heap_owners($heap_graph(S_release),HOBJECT n_parent) = 1
$generator_request_bailout_at(ptask_release_tail*) = (pgenfatal_old)
pgenfatal_old.SOURCE = pgenfatal_first.SOURCE /\ pgenfatal_old.OBJECT = n_reported
pgenfatal_old.FROZEN = REQUESTFATAL ($ptascii("RequestPinException21")) ($ptascii("handler")) 7
$generator_request_bailout_valid(S_release,pgenfatal_old)
''')
    checks += ['$request_fatal_stderr(S_release.EVENTS) = ' + first]
    checks += base.seek('S_pinned', 'S_release', 702) + fatal.normal_valid('S_pinned')
    checks += fatal.lines(r'''
S_pinned.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask_pin_tail*
pinstancestorage.OBJECT = n_parent /\ pinstancestorage.NEXT = 0
$instance_storage_valid(S_pinned,pinstancestorage)
|pinstancestorage.SLOTS| = 1
$property_slot_at(pinstancestorage.SLOTS,$ptascii("leaf")) = (ppropertyslot_leaf)
ppropertyslot_leaf.DECL =/= eps
ppropertyslot_leaf.STATE = PROP_VALUE (DIRECT (POBJECT n_leaf))
$property_slot_nodes([ppropertyslot_leaf]) = [HOBJECT n_leaf]
$task_nodes(INSTANCE_STORAGE_STEP pinstancestorage) = [HOBJECT n_parent]
$heap_owners($heap_graph(S_pinned),HOBJECT n_parent) = 1
(HOBJECT n_parent) <- S_pinned.ALLOCATIONS
$destructor_handle(S_pinned,pinstancestorage.HANDLE,0) = eps
$weakref_get(S_pinned,n_weak_parent) = PNULL
S_pinned.OBJECTS[n_weak_parent] = WEAKREFERENCE (n_parent)
$node_children(S_pinned,HOBJECT n_weak_parent) = eps
$weakref_get(S_pinned,n_weak_leaf) = POBJECT n_leaf
''')
    checks += base.seek('S_leaf', 'S_pinned', 703) + fatal.normal_valid('S_leaf')
    checks += fatal.lines(r'''
S_leaf.CURRENT = (pcallcontext_leaf)
pcallcontext_leaf.RECEIVER = (n_leaf)
$destructor_context_call(pcallcontext_leaf,S_leaf.CURRENT,S_leaf.FRAMES) = (pdestructorcall)
~pdestructorcall.USER /\ pdestructorcall.CALLER = eps /\ pdestructorcall.ORIGIN = eps
$instance_storage_for(S_leaf,n_parent) = (pinstancestorage[.NEXT = 1])
$node_children(S_leaf,HOBJECT n_parent) = eps
$heap_owners($heap_graph(S_leaf),HOBJECT n_parent) = 1
$heap_owners($heap_graph(S_leaf),HOBJECT n_leaf) = 2
$weakref_get(S_leaf,n_weak_parent) = PNULL
$weakref_get(S_leaf,n_weak_leaf) = POBJECT n_leaf
''')
    checks += base.seek('S_abrupt', 'S_leaf', 704) + fatal.normal_valid('S_abrupt')
    checks += fatal.lines(r'''
S_abrupt.TODO = (THROW_SEARCH n_exception) :: (DESTRUCTOR_RESULT pdestructorcall) :: (DESTRUCTOR_RELEASE pdestructionrelease_leaf) :: (INSTANCE_STORAGE_STEP pinstancestorage[.NEXT = 1]) :: ptask_parent_tail*
ptask_abrupt_tail* = (DESTRUCTOR_RESULT pdestructorcall) :: (DESTRUCTOR_RELEASE pdestructionrelease_leaf) :: (INSTANCE_STORAGE_STEP pinstancestorage[.NEXT = 1]) :: ptask_parent_tail*
S_abrupt.CURRENT = eps /\ S_abrupt.FRAMES = eps /\ S_abrupt.ORIGIN = eps /\ S_abrupt.CONSTCONTEXT = eps
S_abrupt.EXCEPTIONHANDLER = eps
pdestructorcall.OBJECT = n_leaf /\ pdestructorcall.CONSTCONTEXT = eps
pdestructorcall.FRAME = eps /\ pdestructorcall.OPERATION = eps /\ pdestructorcall.PENDING = eps
pdestructorcall.RELEASE = (pdestructionrelease_leaf_original)
pdestructionrelease_leaf_original.JOBS = [DESTRUCTION_VALUE (HOBJECT n_leaf)]
pdestructionrelease_leaf = pdestructionrelease_leaf_original[.JOBS = eps]
pdestructionjob_parent* = [DESTRUCTION_HANDLE n_reported]
pdestructionrelease_reported = pdestructionrelease_parent[.JOBS = pdestructionjob_parent*]
ptask_parent_tail* = (DESTRUCTOR_RELEASE pdestructionrelease_reported) :: (GENERATOR_REQUEST_BAILOUT pgenfatal_old) :: ptask_reported_tail*
$destructor_result_valid(S_abrupt,pdestructorcall)
$instance_storage_valid(S_abrupt,pinstancestorage[.NEXT = 1])
$generator_request_release_abrupt(S_abrupt) /\ $shutdown_render_throw_pending(S_abrupt)
$eager_bailout_source(S_abrupt) = eps
$generator_request_bailout_at(ptask_parent_tail*) = (pgenfatal_old)
~$generator_request_bailout_valid(S_abrupt,pgenfatal_old)
S_throw_future = $call_after_origin(S_abrupt,THROW_SEARCH n_exception)
S_throw_future = S_abrupt[.TODO = ptask_abrupt_tail*]
S_throw_future.DESTRUCTION.CALLS = S_abrupt.DESTRUCTION.CALLS
S_throw_future.DESTRUCTION.RELEASES = S_abrupt.DESTRUCTION.RELEASES
$generator_request_bailout_valid(S_throw_future,pgenfatal_old)
$call_tasks_valid(S_abrupt,S_abrupt.TODO)
$heap_graph(S_throw_future).NODES = $heap_graph(S_abrupt).NODES
$heap_graph(S_throw_future).EDGES = $heap_graph(S_abrupt).EDGES
$heap_owners($heap_graph(S_throw_future),HOBJECT n_leaf) = 1
$heap_owners($heap_graph(S_throw_future),HOBJECT n_parent) = 1
$throwable_live(S_abrupt,n_exception)
$throwable_field(S_abrupt,n_exception,"message") = PSTRING $ptascii("leaf")
$throwable_field(S_abrupt,n_exception,"previous") = PNULL
$generator_request_fatal_selected(S_abrupt) = (pgenfatal_new)
pgenfatal_new.SOURCE = DESTRUCTOR_RESULT pdestructorcall /\ pgenfatal_new.OBJECT = n_exception
pgenfatal_new.METHOD = eps /\ pgenfatal_new.TEXT = eps /\ pgenfatal_new.REPORT = eps /\ pgenfatal_new.FROZEN = NORMAL
$heap_owners($heap_graph(S_abrupt),HOBJECT n_exception) = 1
$heap_owners($heap_graph(S_abrupt),HOBJECT n_leaf) = 1
$heap_owners($heap_graph(S_abrupt),HOBJECT n_parent) = 1
$heap_owners($heap_graph(S_abrupt),HOBJECT n_generator) = 1
$heap_owners($heap_graph(S_abrupt),HOBJECT n_payload) = 1
$weakref_get(S_abrupt,n_weak_parent) = PNULL
$weakref_get(S_abrupt,n_weak_leaf) = POBJECT n_leaf
$weakref_get(S_abrupt,n_weak_generator) = POBJECT n_generator
$weakref_get(S_abrupt,n_weak_payload) = POBJECT n_payload
''')
    checks += ['$request_fatal_stderr(S_abrupt.EVENTS) = ' + first,
               'S_dead = S_abrupt[.ALLOCATIONS = $destruction_node_delete(S_abrupt.ALLOCATIONS,HOBJECT n_exception)]',
               '~$throwable_live(S_dead,n_exception)',
               '$generator_request_fatal_selected(S_dead) = eps',
               '~$heap_valid($heap_graph(S_dead))',
               'S_live_handler = S_abrupt[.EXCEPTIONHANDLER = (PSTRING $ptascii("requestPinHandler21"))]',
               '$generator_request_fatal_selected(S_live_handler) = eps']
    checks += fatal.normal_valid('S_live_handler')
    checks += ['S_live_handler_refused = $drive_steps(S_live_handler,1)',
               'S_live_handler_refused.COMPLETION = UNSUPPORTED "Generator request fatal exception-release throw"']
    for label, field in [('line', '.LINE = 1'), ('user', '.USER = true'),
                         ('caller', '.CALLER = (pcallcontext_leaf)'),
                         ('origin', '.ORIGIN = (pcallcontext_leaf.FUNCTION)')]:
        call = 'pdestructorcall_' + label
        checks += [f'{call} = pdestructorcall[{field}]',
                   f'S_{label} = S_abrupt[.TODO = (THROW_SEARCH n_exception) :: (DESTRUCTOR_RESULT {call}) :: (DESTRUCTOR_RELEASE pdestructionrelease_leaf) :: (INSTANCE_STORAGE_STEP pinstancestorage[.NEXT = 1]) :: ptask_parent_tail*][.DESTRUCTION.CALLS = [{call}]]',
                   f'~$destructor_result_valid(S_{label},{call})',
                   f'$generator_request_fatal_selected(S_{label}) = eps']
        reject(checks, 'child_' + label, 'S_' + label, 'S_abrupt')
        if label in ['user', 'caller', 'origin']:
            checks += [f'$call_after_origin(S_{label},THROW_SEARCH n_exception) = S_{label}']
    checks += ['S_current = S_abrupt[.CURRENT = (pcallcontext_leaf)]',
               '$generator_request_fatal_selected(S_current) = eps',
               '~$call_descriptors_valid(S_current)']
    for label, tail, same_heap in [
        ('no_pin', '(DESTRUCTOR_RESULT pdestructorcall) :: (DESTRUCTOR_RELEASE pdestructionrelease_leaf) :: ptask_parent_tail*', False),
        ('duplicate_pin', '(DESTRUCTOR_RESULT pdestructorcall) :: (DESTRUCTOR_RELEASE pdestructionrelease_leaf) :: (INSTANCE_STORAGE_STEP pinstancestorage[.NEXT = 1]) :: (INSTANCE_STORAGE_STEP pinstancestorage[.NEXT = 1]) :: ptask_parent_tail*', False),
        ('no_release', '(DESTRUCTOR_RESULT pdestructorcall) :: (INSTANCE_STORAGE_STEP pinstancestorage[.NEXT = 1]) :: ptask_parent_tail*', True),
        ('duplicate_release', '(DESTRUCTOR_RESULT pdestructorcall) :: (DESTRUCTOR_RELEASE pdestructionrelease_leaf) :: (DESTRUCTOR_RELEASE pdestructionrelease_leaf) :: (INSTANCE_STORAGE_STEP pinstancestorage[.NEXT = 1]) :: ptask_parent_tail*', True),
    ]:
        checks += [f'S_{label} = S_abrupt[.TODO = (THROW_SEARCH n_exception) :: {tail}]',
                   f'$generator_request_fatal_selected(S_{label}) = eps']
        reject(checks, 'child_' + label, 'S_' + label, 'S_abrupt', same_heap=same_heap)
    checks += ['$weakref_get(S_no_pin,n_weak_parent) = POBJECT n_parent',
               '$heap_owners($heap_graph(S_no_pin),HOBJECT n_parent) = 0',
               '$node_children(S_no_pin,HOBJECT n_weak_parent) = eps']
    for label, replacement in [
        ('no_bailout', 'eps'),
        ('duplicate_bailout', '[GENERATOR_REQUEST_BAILOUT pgenfatal_old, GENERATOR_REQUEST_BAILOUT pgenfatal_old]'),
        ('frozen', '[GENERATOR_REQUEST_BAILOUT pgenfatal_old[.FROZEN = REQUESTFATAL ($ptascii("RequestPinException21")) ($ptascii("changed")) 7]]'),
        ('frozen_line', '[GENERATOR_REQUEST_BAILOUT pgenfatal_old[.FROZEN = REQUESTFATAL ($ptascii("RequestPinException21")) ($ptascii("handler")) 4]]'),
        ('snapshot', '[GENERATOR_REQUEST_BAILOUT pgenfatal_old[.REPORT = eps]]'),
        ('old_source', '[GENERATOR_REQUEST_BAILOUT pgenfatal_old[.SOURCE = THROW_SEARCH n_original]]'),
    ]:
        checks += [f'S_{label} = S_abrupt[.TODO = $child_bailout_tasks(S_abrupt.TODO,pgenfatal_old,{replacement})]',
                   f'$generator_request_fatal_selected(S_{label}) = eps']
        if label != 'no_bailout':
            reject(checks, 'child_' + label, 'S_' + label, 'S_abrupt')
    checks += ['$call_after_origin(S_no_bailout,THROW_SEARCH n_exception) = S_no_bailout',
               '$destructor_result_valid(S_no_bailout,pdestructorcall)',
               '$eager_bailout_source(S_no_bailout) = (DESTRUCTOR_RESULT pdestructorcall)']
    one(checks, 'S_abrupt', 'S_report')
    checks += fatal.lines(r'''
S_report.TODO = (GENERATOR_REQUEST_REPORT pgenfatal_new) :: ptask_abrupt_tail*
S_report.DESTRUCTION.CALLS = S_abrupt.DESTRUCTION.CALLS
S_report.DESTRUCTION.RELEASES = S_abrupt.DESTRUCTION.RELEASES
S_report.DESTRUCTION.ABANDONED = S_abrupt.DESTRUCTION.ABANDONED
pdestructorcall <- S_report.DESTRUCTION.CALLS
$destructor_call_live(S_report,pdestructorcall)
S_report.OBJECTPROPS = S_abrupt.OBJECTPROPS
S_report.ALLOCATIONS = S_abrupt.ALLOCATIONS
$generator_request_report_valid(S_report,pgenfatal_new)
$destructor_call_tail(S_report.TODO,pdestructorcall) = ((DESTRUCTOR_RELEASE pdestructionrelease_leaf) :: (INSTANCE_STORAGE_STEP pinstancestorage[.NEXT = 1]) :: ptask_parent_tail*)
$heap_graph(S_report).NODES = $heap_graph(S_abrupt).NODES
$heap_graph(S_report).EDGES = $heap_graph(S_abrupt).EDGES
$generator_request_fatal_receiver(pgenfatal_new.SOURCE) = [HOBJECT n_leaf]
$task_nodes(GENERATOR_REQUEST_REPORT pgenfatal_new) = [HOBJECT n_exception,HOBJECT n_leaf]
$heap_owners($heap_graph(S_report),HOBJECT n_leaf) = 2
$task_nodes(GENERATOR_REQUEST_BAILOUT pgenfatal_old) = eps
S_future = $call_after_origin(S_report,GENERATOR_REQUEST_REPORT pgenfatal_new)
S_future = S_report[.TODO = ptask_abrupt_tail*]
$heap_graph(S_future).NODES = $heap_graph(S_report).NODES
$heap_graph(S_future).EDGES = $heap_graph(S_report).EDGES
$heap_owners($heap_graph(S_future),HOBJECT n_leaf) = 1
$heap_owners($heap_graph(S_future),HOBJECT n_parent) = 1
$heap_owners($heap_graph(S_future),HOBJECT n_generator) = 1
$heap_owners($heap_graph(S_future),HOBJECT n_payload) = 1
$heap_owners($heap_graph(S_report),HOBJECT n_exception) = 1
$heap_owners($heap_graph(S_future),HOBJECT n_exception) = 0
''')
    for label, field, same_heap in [('new_source', '.SOURCE = DESTRUCTOR_RESULT pdestructorcall_line', True),
                                    ('new_throw_source', '.SOURCE = THROW_SEARCH n_exception', False),
                                    ('new_owner', '.OBJECT = n_leaf', False)]:
        checks += [f'pgenfatal_{label} = pgenfatal_new[{field}]']
        if label == 'new_owner':
            checks += [f'$destructor_call_tail((GENERATOR_REQUEST_REPORT pgenfatal_{label}) :: ptask_abrupt_tail*,pdestructorcall) = ((DESTRUCTOR_RELEASE pdestructionrelease_leaf) :: (INSTANCE_STORAGE_STEP pinstancestorage[.NEXT = 1]) :: ptask_parent_tail*)',
                       f'~$generator_request_report_valid(S_report[.TODO = (GENERATOR_REQUEST_REPORT pgenfatal_{label}) :: ptask_abrupt_tail*],pgenfatal_{label})']
        else:
            checks += [f'$destructor_call_tail((GENERATOR_REQUEST_REPORT pgenfatal_{label}) :: ptask_abrupt_tail*,pdestructorcall) = eps']
        reject(checks, label, f'S_report[.TODO = (GENERATOR_REQUEST_REPORT pgenfatal_{label}) :: ptask_abrupt_tail*]', 'S_report', same_heap=same_heap)
    checks += ['$generator_request_fatal_receiver(DESTRUCTOR_RESULT pdestructorcall_user) = eps',
               'S_duplicate_report = S_report[.TODO = (GENERATOR_REQUEST_REPORT pgenfatal_new) :: S_report.TODO]',
               '$heap_owners($heap_graph(S_duplicate_report),HOBJECT n_leaf) = 3',
               '~$generator_request_report_valid(S_duplicate_report,pgenfatal_new)']
    reject(checks, 'duplicate_report', 'S_duplicate_report', 'S_report', same_heap=False)
    checks += ['$destructor_call_tail((GENERATOR_REQUEST_REPORT pgenfatal_new) :: (DESTRUCTOR_RESULT pdestructorcall_user) :: ptask_parent_tail*,pdestructorcall_user) = eps',
               '$destructor_call_tail((GENERATOR_REQUEST_BAILOUT pgenfatal_new) :: (DESTRUCTOR_RESULT pdestructorcall_caller) :: ptask_parent_tail*,pdestructorcall_caller) = eps',
               '$destructor_call_tail((GENERATOR_REQUEST_REPORT pgenfatal_new) :: ptask_abrupt_tail*,pdestructorcall_line) = eps']
    reject(checks, 'different_result', 'S_report[.TODO = (GENERATOR_REQUEST_REPORT pgenfatal_new) :: (DESTRUCTOR_RESULT pdestructorcall_line) :: (DESTRUCTOR_RELEASE pdestructionrelease_leaf) :: (INSTANCE_STORAGE_STEP pinstancestorage[.NEXT = 1]) :: ptask_parent_tail*]', 'S_report')
    one(checks, 'S_report', 'S_second_release')
    checks += ['ptbytes_leaf_report = ' + cached_leaf]
    checks += fatal.lines(r'''
S_second_release.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_new) :: (GENERATOR_REQUEST_BAILOUT pgenfatal_bailout) :: ptask_abrupt_tail*
pdestructionrelease_new.JOBS = [DESTRUCTION_VALUE (HOBJECT n_exception)]
pgenfatal_bailout.SOURCE = pgenfatal_new.SOURCE /\ pgenfatal_bailout.OBJECT = n_exception
$task_nodes(GENERATOR_REQUEST_BAILOUT pgenfatal_bailout) = [HOBJECT n_leaf]
pgenfatal_bailout.FROZEN = REQUESTFATAL ($ptascii("Exception")) ($ptascii("leaf")) 4
$generator_request_bailout_valid(S_second_release,pgenfatal_bailout)
S_second_release.DESTRUCTION.CALLS = S_abrupt.DESTRUCTION.CALLS
$objectprops_at(S_report.OBJECTPROPS,n_exception) = (ppropertyslot_exception*)
$throwable_field(S_report,n_exception,"string") = PSTRING eps
$generator_request_report_text(S_report,pgenfatal_new) = ptbytes_leaf_report
S_second_release.OBJECTPROPS = $objectprops_set(S_report.OBJECTPROPS,n_exception,$property_slot_set(ppropertyslot_exception*,$throwable_key("Exception","string"),PROP_VALUE (DIRECT (PSTRING ptbytes_leaf_report))))
$throwable_field(S_second_release,n_exception,"string") = PSTRING ptbytes_leaf_report
''')
    checks += ['$request_fatal_stderr(S_second_release.EVENTS) = ' + both]
    checks += base.seek('S_bailout', 'S_second_release', 705) + fatal.normal_valid('S_bailout')
    checks += fatal.lines(r'''
S_bailout.TODO = (GENERATOR_REQUEST_BAILOUT pgenfatal_bailout) :: ptask_abrupt_tail*
S_bailout.DESTRUCTION.CALLS = S_abrupt.DESTRUCTION.CALLS
S_bailout.DESTRUCTION.RELEASES = S_abrupt.DESTRUCTION.RELEASES
S_bailout.OBJECTPROPS = $objectprops_prune(S_second_release.OBJECTPROPS,$destruction_node_delete(S_second_release.ALLOCATIONS,HOBJECT n_exception))
$objectprops_at(S_bailout.OBJECTPROPS,n_exception) = eps
$objectprops_at(S_bailout.OBJECTPROPS,n_parent) = $objectprops_at(S_second_release.OBJECTPROPS,n_parent)
$objectprops_at(S_bailout.OBJECTPROPS,n_leaf) = $objectprops_at(S_second_release.OBJECTPROPS,n_leaf)
~((HOBJECT n_exception) <- S_bailout.ALLOCATIONS)
$heap_owners($heap_graph(S_bailout),HOBJECT n_exception) = 0
$heap_owners($heap_graph(S_bailout),HOBJECT n_leaf) = 2
$heap_owners($heap_graph(S_bailout),HOBJECT n_parent) = 1
$heap_owners($heap_graph(S_bailout),HOBJECT n_generator) = 1
$heap_owners($heap_graph(S_bailout),HOBJECT n_payload) = 1
$generator_request_bailout_valid(S_bailout,pgenfatal_bailout)
$destructor_call_tail(S_bailout.TODO,pdestructorcall) = ((DESTRUCTOR_RELEASE pdestructionrelease_leaf) :: (INSTANCE_STORAGE_STEP pinstancestorage[.NEXT = 1]) :: ptask_parent_tail*)
S_stopped = $drive_steps(S_bailout,0)
S_stopped = S_bailout[.COMPLETION = BUDGET]
S_resumed = $drive(S_stopped[.COMPLETION = NORMAL],4096)
S_direct = $drive(S_bailout,4096)
S_resumed = S_direct
S_resumed.COMPLETION = pgenfatal_bailout.FROZEN
S_resumed.TODO = eps /\ S_resumed.FRAMES = eps
S_resumed.DESTRUCTION.PHASE = DESTRUCTION_DONE
S_resumed.DESTRUCTION.CALLED = $destructor_all(0,|S_resumed.OBJECTS|)
S_resumed.DESTRUCTION.ABANDONED = [pdestructioncleanup_fatal]
pdestructioncleanup_fatal.SOURCE = DESTRUCTOR_FATAL pdestructionfatal
pdestructionfatal.FRAME.TODO = S_bailout.TODO
pdestructionfatal.FRAME.CONTEXT = eps /\ pdestructionfatal.FRAME.LOCALS = eps
pdestructionfatal.DESTRUCTION = S_bailout.DESTRUCTION
pdestructionfatal.COMPLETION = pgenfatal_bailout.FROZEN
pdestructionfatal.FROZEN = pgenfatal_bailout.FROZEN
(HOBJECT n_parent) <- $eager_fatal_nodes(pdestructionfatal)
(HOBJECT n_leaf) <- $eager_fatal_nodes(pdestructionfatal)
(HOBJECT n_generator) <- $eager_fatal_nodes(pdestructionfatal)
~((HOBJECT n_exception) <- $eager_fatal_nodes(pdestructionfatal))
$heap_owners($heap_graph(S_resumed),HOBJECT n_parent) = 1
$heap_owners($heap_graph(S_resumed),HOBJECT n_leaf) = 2
$heap_owners($heap_graph(S_resumed),HOBJECT n_generator) = 1
$heap_owners($heap_graph(S_resumed),HOBJECT n_payload) = 1
$weakref_get(S_resumed,n_weak_parent) = PNULL
$weakref_get(S_resumed,n_weak_leaf) = POBJECT n_leaf
$weakref_get(S_resumed,n_weak_generator) = POBJECT n_generator
$weakref_get(S_resumed,n_weak_payload) = POBJECT n_payload
$instance_storage_abandoned(S_resumed.DESTRUCTION.ABANDONED) = [pinstancestorage[.NEXT = 1]]
$instance_storage_all(S_resumed) = [pinstancestorage[.NEXT = 1]]
$instance_storage_for(S_resumed,n_parent) = (pinstancestorage[.NEXT = 1])
$instance_storage_state_valid(S_resumed)
$gc_handle_all(S_resumed,n_parent) = 0
$instance_storage_count($instance_storage_abandoned(S_resumed.DESTRUCTION.ABANDONED),n_parent) = 1
$gc_retired_valid(S_resumed,n_parent)
~((HOBJECT n_reported) <- S_resumed.ALLOCATIONS)
$heap_owners($heap_graph(S_resumed),HOBJECT n_reported) = 0
(GC_RETIRED n_reported) <- S_resumed.GC.BUFFER
S_resumed.GC = S_bailout.GC
$gc_handle_tasks(S_resumed,S_resumed.TODO,n_reported) = 0
$gc_handle_frames(S_resumed,S_resumed.FRAMES,n_reported) = 0
$gc_handle_fatal(DESTRUCTOR_FATAL pdestructionfatal,n_reported) = 1
$gc_handle_abandoned(S_resumed.DESTRUCTION.ABANDONED,n_reported) = 1
$gc_handle_all(S_resumed,n_reported) = 1
$gc_retired_valid(S_resumed,n_reported)
$gc_handle_fatal(DESTRUCTOR_RESULT pdestructorcall,n_reported) = 0
$gc_handle_fatal(DESTRUCTOR_FATAL pdestructionfatal[.DESTRUCTION = S_resumed.DESTRUCTION],n_reported) = 1
$gc_handle_fatal_frames([pdestructionfatal.FRAME],n_reported) = 1
S_history = $eager_fatal_history(S_resumed,pdestructionfatal)
S_history.TODO = S_bailout.TODO
S_history.CURRENT = S_bailout.CURRENT /\ S_history.FRAMES = S_bailout.FRAMES
S_history.DESTRUCTION = S_bailout.DESTRUCTION
$instance_storage_abandoned(S_history.DESTRUCTION.ABANDONED) = eps
$instance_storage_all(S_history) = [pinstancestorage[.NEXT = 1]]
$gc_handle_all(S_history,n_parent) = 1
$gc_retired_valid(S_history,n_parent)
S_history.GC = S_bailout.GC
$gc_handle_tasks(S_history,S_history.TODO,n_reported) = 1
$gc_handle_abandoned(S_history.DESTRUCTION.ABANDONED,n_reported) = 0
$gc_handle_all(S_history,n_reported) = 1
$gc_retired_valid(S_history,n_reported)
$gc_state_valid(S_history)
$generator_request_bailout_valid(S_history,pgenfatal_bailout)
''')
    checks += ['$request_fatal_stderr(S_resumed.EVENTS) = ' + both,
               '$close_outputs(S_resumed.EVENTS) = ' + byte_expr(source.CASES[name][1])]
    checks += valid('S_resumed')
    for label, replacement, count in [
        ('missing', 'eps', 0),
        ('duplicate', '[DESTRUCTOR_RELEASE pdestructionrelease_reported,DESTRUCTOR_RELEASE pdestructionrelease_reported]', 2),
        ('user', '[DESTRUCTOR_RELEASE pdestructionrelease_reported[.USER = true]]', 1),
    ]:
        fatal_record = 'pdestructionfatal_handle_' + label
        state = 'S_final_handle_' + label
        checks += [f'{fatal_record} = pdestructionfatal[.FRAME.TODO = $child_handle_tasks(pdestructionfatal.FRAME.TODO,pdestructionrelease_reported,{replacement})]',
                   f'{state} = S_resumed[.DESTRUCTION.ABANDONED = [pdestructioncleanup_fatal[.SOURCE = DESTRUCTOR_FATAL {fatal_record}]]]',
                   f'$gc_handle_abandoned({state}.DESTRUCTION.ABANDONED,n_reported) = {count}',
                   f'$gc_handle_all({state},n_reported) = {count}',
                   f'{"" if count == 1 else "~"}$gc_retired_valid({state},n_reported)']
        if label == 'user':
            checks += [f'~$eager_fatal_valid({state},pdestructioncleanup_fatal[.SOURCE = DESTRUCTOR_FATAL {fatal_record}],{fatal_record})']
        terminal_reject(checks, 'final_handle_' + label, state, 'S_resumed')
    checks += fatal.lines(r'''
S_history_handle_duplicate = S_history[.DESTRUCTION.ABANDONED = [pdestructioncleanup_fatal]]
$gc_handle_tasks(S_history_handle_duplicate,S_history_handle_duplicate.TODO,n_reported) = 1
$gc_handle_abandoned(S_history_handle_duplicate.DESTRUCTION.ABANDONED,n_reported) = 1
$gc_handle_all(S_history_handle_duplicate,n_reported) = 2
~$gc_retired_valid(S_history_handle_duplicate,n_reported)
''')
    reject(checks, 'history_handle_duplicate', 'S_history_handle_duplicate', 'S_history', same_heap=False)
    for label, replacement in [
        ('missing', 'eps'),
        ('duplicate', '[INSTANCE_STORAGE_STEP pinstancestorage[.NEXT = 1],INSTANCE_STORAGE_STEP pinstancestorage[.NEXT = 1]]'),
        ('handle', '[INSTANCE_STORAGE_STEP pinstancestorage[.NEXT = 1][.HANDLE = 0]]'),
        ('next', '[INSTANCE_STORAGE_STEP pinstancestorage[.NEXT = 2]]'),
    ]:
        fatal_record = 'pdestructionfatal_' + label
        state = 'S_final_' + label
        checks += [f'{fatal_record} = pdestructionfatal[.FRAME.TODO = $child_pin_tasks(pdestructionfatal.FRAME.TODO,pinstancestorage[.NEXT = 1],{replacement})]',
                   f'{state} = S_resumed[.DESTRUCTION.ABANDONED = [pdestructioncleanup_fatal[.SOURCE = DESTRUCTOR_FATAL {fatal_record}]]]',
                   f'~$gc_retired_valid({state},n_parent)']
        if label == 'missing':
            checks += [f'$instance_storage_for({state},n_parent) = eps',
                       f'$weakref_get({state},n_weak_parent) = POBJECT n_parent',
                       f'$heap_owners($heap_graph({state}),HOBJECT n_parent) = 0']
        elif label == 'duplicate':
            checks += [f'$instance_storage_count($instance_storage_abandoned({state}.DESTRUCTION.ABANDONED),n_parent) = 2',
                       f'~$instance_storage_state_valid({state})',
                       f'$heap_owners($heap_graph({state}),HOBJECT n_parent) = 2']
        else:
            field = '.HANDLE = 0' if label == 'handle' else '.NEXT = 2'
            pin = 'pinstancestorage[.NEXT = 1]' if label == 'handle' else 'pinstancestorage'
            checks += [f'$instance_storage_for({state},n_parent) = ({pin}[{field}])',
                       f'~$instance_storage_basic({state},{pin}[{field}])']
        terminal_reject(checks, 'final_pin_' + label, state, 'S_resumed', same_heap=label in ['handle', 'next'])
    checks += fatal.lines(r'''
S_final_released = S_resumed[.DESTRUCTION.ABANDONED = [pdestructioncleanup_fatal[.RELEASED = true]]]
$instance_storage_abandoned(S_final_released.DESTRUCTION.ABANDONED) = eps
$instance_storage_for(S_final_released,n_parent) = eps
~$gc_retired_valid(S_final_released,n_parent)
$gc_handle_abandoned(S_final_released.DESTRUCTION.ABANDONED,n_reported) = 0
~$gc_retired_valid(S_final_released,n_reported)
$weakref_get(S_final_released,n_weak_parent) = POBJECT n_parent
S_final_active_duplicate = S_resumed[.TODO = [INSTANCE_STORAGE_STEP pinstancestorage[.NEXT = 1]]]
$gc_handle_all(S_final_active_duplicate,n_parent) = 1
$instance_storage_count($instance_storage_abandoned(S_final_active_duplicate.DESTRUCTION.ABANDONED),n_parent) = 1
~$instance_storage_state_valid(S_final_active_duplicate)
~$gc_retired_valid(S_final_active_duplicate,n_parent)
$instance_storage_abandoned([pdestructioncleanup_fatal[.SOURCE = DESTRUCTOR_RESULT pdestructorcall]]) = eps
''')
    terminal_reject(checks, 'final_released', 'S_final_released', 'S_resumed')
    terminal_reject(checks, 'final_active_duplicate', 'S_final_active_duplicate', 'S_resumed', same_heap=False)
    return checks


def main():
    process = driver.driver.process
    driver.driver.process = lambda argv, path, seconds, root: process(argv, path, min(seconds, 120), root)
    base.CASES = CASES
    driver.CASES = CASES
    driver.NATIVE_ERROR_PREFIXES = source.NATIVE_ERROR_PREFIXES
    driver.PREFIX += base.PREFIX + fatal.PREFIX + PREFIX
    driver.assertions = assertions
    driver.source.WATCHED += source.EXTRA_WATCHED + [
        'tests/semantics/reference_yield_protocol.py',
        'tests/semantics/generator_request_finally_protocol.py',
        'tests/semantics/generator_request_abrupt_protocol.py',
        'tests/semantics/generator_request_instance_child_protocol.py',
    ]
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())
