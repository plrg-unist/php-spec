#!/usr/bin/env python3
"""Reached array child retirement and a genuine shared-array release control."""
import os
import re

import generator_request_instance_child_protocol as child
import generator_request_array_child_sources as source
from reference_yield_protocol import reject

driver = child.driver
CASES = source.CASES


def names(text):
    return re.sub(r'(RequestPin|requestPin)(\w*)21',
                  lambda match: match[1].replace('Pin', 'ArrayPin') + match[2] + '23', text)


def assertions(checked, path, directory, name):
    if name == 'request-fatal-shared-array-child':
        return shared_assertions(checked, path)
    checks = [names(check) for check in child.assertions(checked, path, directory, name, source)]
    slot = checks.index('ppropertyslot_leaf.STATE = PROP_VALUE (DIRECT (POBJECT n_leaf))')
    checks[slot:slot + 2] = child.fatal.lines(r'''
ppropertyslot_leaf.STATE = PROP_VALUE (DIRECT (PARRAY n_array))
$property_slot_nodes([ppropertyslot_leaf]) = [HARRAY n_array]
(HARRAY n_array) <- S_pinned.ALLOCATIONS
S_pinned.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_leaf))]
$node_children(S_pinned,HARRAY n_array) = [HOBJECT n_leaf]
$heap_owners($heap_graph(S_pinned),HARRAY n_array) = 1
$heap_owners($heap_graph(S_pinned),HOBJECT n_leaf) = 1
''')
    leaf = checks.index('S_leaf_found = $request_finally_seek(S_pinned,703,4096)')
    checks[leaf] = 'S_leaf_found = $request_finally_seek(S_retired,703,4096)'
    transfer = child.fatal.lines(r'''
S_array_found = $drive_steps(S_pinned,1)
S_array_found.COMPLETION = BUDGET
S_array = S_array_found[.COMPLETION = NORMAL]
S_array.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_array) :: (INSTANCE_STORAGE_STEP pinstancestorage[.NEXT = 1]) :: ptask_pin_tail*
pdestructionrelease_array.JOBS = [DESTRUCTION_VALUE (HARRAY n_array)]
$destructor_release_valid(S_array,pdestructionrelease_array)
$objectprops_at(S_array.OBJECTPROPS,n_parent) = (ppropertyslot_array*)
$property_slot_at(ppropertyslot_array*,$ptascii("leaf")) = (ppropertyslot_leaf[.STATE = PROP_UNSET])
S_array.ARRAYS[n_array] = S_pinned.ARRAYS[n_array]
$heap_owners($heap_graph(S_array),HARRAY n_array) = 1
$heap_owners($heap_graph(S_array),HOBJECT n_leaf) = 1
S_retired_found = $drive_steps(S_array,1)
S_retired_found.COMPLETION = BUDGET
S_retired = S_retired_found[.COMPLETION = NORMAL]
pdestructionrelease_referent = pdestructionrelease_array[.JOBS = [DESTRUCTION_VALUE (HOBJECT n_leaf)]]
S_retired.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_referent) :: (INSTANCE_STORAGE_STEP pinstancestorage[.NEXT = 1]) :: ptask_pin_tail*
$destructor_release_valid(S_retired,pdestructionrelease_referent)
~((HARRAY n_array) <- S_retired.ALLOCATIONS)
S_retired.ARRAYS[n_array] = S_pinned.ARRAYS[n_array]
$heap_owners($heap_graph(S_retired),HARRAY n_array) = 0
~((HEDGE (HARRAY n_array) (HOBJECT n_leaf)) <- $heap_graph(S_retired).EDGES)
$heap_owners($heap_graph(S_retired),HOBJECT n_leaf) = 1
$destruction_free_job(HARRAY n_array) = eps
$gc_slot_find(S_retired.GC.BUFFER,HARRAY n_array,0) = eps
''') + child.fatal.normal_valid('S_array') + child.fatal.normal_valid('S_retired')
    checks[leaf:leaf] = transfer
    abrupt = checks.index('$generator_request_fatal_selected(S_abrupt) = (pgenfatal_new)')
    checks[abrupt:abrupt] = child.fatal.lines(r'''
pdestructionrelease_leaf_original = pdestructionrelease_referent
~((HARRAY n_array) <- S_abrupt.ALLOCATIONS)
S_abrupt.ARRAYS[n_array] = S_pinned.ARRAYS[n_array]
$heap_owners($heap_graph(S_abrupt),HARRAY n_array) = 0
~((HEDGE (HARRAY n_array) (HOBJECT n_leaf)) <- $heap_graph(S_abrupt).EDGES)
$generator_request_release_slot(S_abrupt,ppropertyslot_leaf,n_leaf)
''')
    report = checks.index('S_report.TODO = (GENERATOR_REQUEST_REPORT pgenfatal_new) :: ptask_abrupt_tail*')
    controls = []
    for label, array in [
        ('empty', 'S_report.ARRAYS[n_array][.ITEMS = eps]'),
        ('scalar', 'S_report.ARRAYS[n_array][.ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 1))]]'),
        ('object', 'S_report.ARRAYS[n_array][.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_parent))]]'),
        ('duplicate', '$array_insert(S_report.ARRAYS[n_array],KINT 1,DIRECT (POBJECT n_leaf))'),
        ('reference', 'S_report.ARRAYS[n_array][.ITEMS = [ENTRY (KINT 0) (ALIAS 0)]]'),
        ('nested', 'S_report.ARRAYS[n_array][.ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_array))]]'),
    ]:
        state = 'S_array_' + label
        controls += [f'{state} = S_report[.ARRAYS = $array_replace(S_report.ARRAYS,n_array,{array})]',
                     f'~$generator_request_release_slot({state},ppropertyslot_leaf,n_leaf)',
                     f'~$generator_request_report_valid({state},pgenfatal_new)',
                     f'{state}_throw = S_abrupt[.ARRAYS = {state}.ARRAYS]',
                     f'$call_descriptors_valid({state}_throw)',
                     f'$generator_request_fatal_selected({state}_throw) = eps']
        reject(controls, 'retired_array_' + label, state, 'S_report')
    controls += child.fatal.lines(r'''
parray_primitive = $array_insert(S_report.ARRAYS[n_array],KINT 1,DIRECT (PINT 7))
S_array_primitive = S_report[.ARRAYS = $array_replace(S_report.ARRAYS,n_array,parray_primitive)]
$entries_nodes(parray_primitive.ITEMS) = [HOBJECT n_leaf]
$heap_graph(S_array_primitive) = $heap_graph(S_report)
$generator_request_release_slot(S_array_primitive,ppropertyslot_leaf,n_leaf)
$generator_request_report_valid(S_array_primitive,pgenfatal_new)
$call_descriptors_valid(S_array_primitive)
n_array_beyond = |S_report.ARRAYS|
''')
    for label, state in [
        ('live', 'S_report[.ALLOCATIONS = S_report.ALLOCATIONS ++ [HARRAY n_array]]'),
        ('bounds', 'S_report[.TODO = $child_pin_tasks(S_report.TODO,pinstancestorage[.NEXT = 1],[INSTANCE_STORAGE_STEP pinstancestorage[.NEXT = 1][.SLOTS = [ppropertyslot_leaf[.STATE = PROP_VALUE (DIRECT (PARRAY n_array_beyond))]]]])]'),
        ('slot', 'S_report[.TODO = $child_pin_tasks(S_report.TODO,pinstancestorage[.NEXT = 1],[INSTANCE_STORAGE_STEP pinstancestorage[.NEXT = 1][.SLOTS = [ppropertyslot_leaf[.STATE = PROP_UNSET]]]])]'),
    ]:
        bad = 'S_array_' + label
        controls += [f'{bad} = {state}', f'~$generator_request_report_valid({bad},pgenfatal_new)']
        reject(controls, 'retired_array_' + label, bad, 'S_report', same_heap=label != 'live')
    controls += child.fatal.lines(r'''
S_array_restored = S_report[.OBJECTPROPS = $objectprops_set(S_report.OBJECTPROPS,n_parent,[ppropertyslot_leaf])]
~$instance_storage_basic(S_array_restored,pinstancestorage[.NEXT = 1])
~$generator_request_report_valid(S_array_restored,pgenfatal_new)
~$call_descriptors_valid(S_array_restored)
~$heap_valid($heap_graph(S_array_restored))
S_array_restored_checked = $call_entry_check(S_array_restored)
S_array_restored_checked.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"
''')
    checks[report:report] = controls
    for state in ['S_report', 'S_bailout', 'S_resumed', 'S_history']:
        checks += [f'~((HARRAY n_array) <- {state}.ALLOCATIONS)',
                   f'{state}.ARRAYS[n_array] = S_pinned.ARRAYS[n_array]',
                   f'$heap_owners($heap_graph({state}),HARRAY n_array) = 0',
                   f'~((HEDGE (HARRAY n_array) (HOBJECT n_leaf)) <- $heap_graph({state}).EDGES)',
                   f'$gc_slot_find({state}.GC.BUFFER,HARRAY n_array,0) = eps']
    return checks


def shared_assertions(checked, path):
    byte_expr = driver.driver.byte_expr
    initial = ('$php_file_run(' + checked['fixture'] + ',0,'
               + byte_expr(os.fsencode(path)) + ',' + byte_expr(os.fsencode(driver.ROOT)) + ')')
    checks = ['S_initial = ' + initial, '~S_initial.COMPILESTOP']
    checks += child.base.seek('S_pinned', 'S_initial', 702) + child.fatal.normal_valid('S_pinned')
    checks += child.fatal.lines(r'''
S_pinned.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask_pin_tail*
pinstancestorage.NEXT = 0 /\ |pinstancestorage.SLOTS| = 1
n_parent = pinstancestorage.OBJECT
$object_name(S_pinned,n_parent) = $ptascii("RequestArrayPinParent23")
$property_slot_at(pinstancestorage.SLOTS,$ptascii("leaf")) = (ppropertyslot_leaf)
ppropertyslot_leaf.DECL =/= eps
ppropertyslot_leaf.STATE = PROP_VALUE (DIRECT (PARRAY n_array))
$objectprops_at(S_pinned.OBJECTPROPS,n_parent) = (ppropertyslot_pinned*)
$property_slot_at(ppropertyslot_pinned*,$ptascii("leaf")) = (ppropertyslot_leaf)
S_pinned.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_leaf))]
(HARRAY n_array) <- S_pinned.ALLOCATIONS
$node_children(S_pinned,HARRAY n_array) = [HOBJECT n_leaf]
$heap_owners($heap_graph(S_pinned),HARRAY n_array) = 2
$heap_owners($heap_graph(S_pinned),HOBJECT n_leaf) = 1
~(n_leaf <- S_pinned.DESTRUCTION.CALLED)
~$generator_request_release_slot(S_pinned,ppropertyslot_leaf,n_leaf)
$trace_slot(S_pinned,S_pinned.ENV,$ptascii("wb")) = POBJECT n_weak_parent
$trace_slot(S_pinned,S_pinned.ENV,$ptascii("wl")) = POBJECT n_weak_leaf
$weakref_get(S_pinned,n_weak_parent) = PNULL
$weakref_get(S_pinned,n_weak_leaf) = POBJECT n_leaf
S_array_found = $drive_steps(S_pinned,1)
S_array_found.COMPLETION = BUDGET
S_array = S_array_found[.COMPLETION = NORMAL]
S_array.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_array) :: (INSTANCE_STORAGE_STEP pinstancestorage[.NEXT = 1]) :: ptask_pin_tail*
pdestructionrelease_array.JOBS = [DESTRUCTION_VALUE (HARRAY n_array)]
$destructor_release_valid(S_array,pdestructionrelease_array)
$heap_owners($heap_graph(S_array),HARRAY n_array) = 2
S_retained_found = $drive_steps(S_array,1)
S_retained_found.COMPLETION = BUDGET
S_retained = S_retained_found[.COMPLETION = NORMAL]
S_retained.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_array[.JOBS = eps]) :: (INSTANCE_STORAGE_STEP pinstancestorage[.NEXT = 1]) :: ptask_pin_tail*
(HARRAY n_array) <- S_retained.ALLOCATIONS
S_retained.ARRAYS[n_array] = S_pinned.ARRAYS[n_array]
$heap_owners($heap_graph(S_retained),HARRAY n_array) = 1
$heap_owners($heap_graph(S_retained),HOBJECT n_leaf) = 1
(HEDGE (HARRAY n_array) (HOBJECT n_leaf)) <- $heap_graph(S_retained).EDGES
~(n_leaf <- S_retained.DESTRUCTION.CALLED)
~$generator_request_release_slot(S_retained,ppropertyslot_leaf,n_leaf)
$close_outputs(S_retained.EVENTS) = $ptascii("C|FH")
$generator_request_fatal_selected(S_retained) = eps
S_resumed = $drive_steps(S_retained,4096)
S_resumed.COMPLETION = REQUESTFATAL ($ptascii("RequestArrayPinException23")) ($ptascii("handler")) 7
$close_outputs(S_resumed.EVENTS) = $ptascii("C|FH")
(HARRAY n_array) <- S_resumed.ALLOCATIONS
S_resumed.ARRAYS[n_array] = S_pinned.ARRAYS[n_array]
$heap_owners($heap_graph(S_resumed),HARRAY n_array) = 1
$heap_owners($heap_graph(S_resumed),HOBJECT n_leaf) = 1
(HEDGE (HARRAY n_array) (HOBJECT n_leaf)) <- $heap_graph(S_resumed).EDGES
~((HOBJECT n_parent) <- S_resumed.ALLOCATIONS)
$heap_owners($heap_graph(S_resumed),HOBJECT n_parent) = 0
$weakref_get(S_resumed,n_weak_parent) = PNULL
$weakref_get(S_resumed,n_weak_leaf) = POBJECT n_leaf
n_leaf <- S_resumed.DESTRUCTION.CALLED
~$generator_request_release_slot(S_resumed,ppropertyslot_leaf,n_leaf)
$call_descriptors_valid(S_resumed)
$heap_valid($heap_graph(S_resumed))
S_piece = $drive_steps(S_retained,1)
S_piece.COMPLETION = BUDGET
S_piece.COMPLETION =/= S_resumed.COMPLETION
S_replayed = $drive_steps(S_piece[.COMPLETION = NORMAL],4096)
S_replayed = S_resumed
''')
    checks += child.fatal.normal_valid('S_array') + child.fatal.normal_valid('S_retained')
    checks += ['$request_fatal_stderr(S_resumed.EVENTS) = ' + byte_expr(source.FIRST_FATAL.replace(b'{file}', os.fsencode(path)))]
    return checks


def main():
    process = driver.driver.process
    driver.driver.process = lambda argv, path, seconds, root: process(argv, path, min(seconds, 120), root)
    driver.CASES = CASES
    driver.NATIVE_ERROR_PREFIXES = source.NATIVE_ERROR_PREFIXES
    driver.PREFIX += child.base.PREFIX + child.fatal.PREFIX + names(child.PREFIX)
    driver.assertions = assertions
    driver.source.WATCHED += source.EXTRA_WATCHED + [
        'tests/semantics/reference_yield_protocol.py',
        'tests/semantics/generator_request_finally_protocol.py',
        'tests/semantics/generator_request_abrupt_protocol.py',
        'tests/semantics/generator_request_instance_child_protocol.py',
        'tests/semantics/generator_request_array_child_protocol.py',
    ]
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())
