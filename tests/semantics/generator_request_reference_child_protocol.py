#!/usr/bin/env python3
"""Reached reference-cell child release and nonowning retired-store evidence."""
import re

import generator_request_instance_child_protocol as child
import generator_request_reference_child_sources as source
from reference_yield_protocol import reject

driver = child.driver
CASES = source.CASES


def names(text):
    return re.sub(r'(RequestPin|requestPin)(\w*)21',
                  lambda match: match[1].replace('Pin', 'RefPin') + match[2] + '22', text)


def assertions(checked, path, directory, name):
    checks = [names(check) for check in child.assertions(checked, path, directory, name, source)]
    slot = checks.index('ppropertyslot_leaf.STATE = PROP_VALUE (DIRECT (POBJECT n_leaf))')
    checks[slot:slot + 2] = child.fatal.lines(r'''
ppropertyslot_leaf.STATE = PROP_VALUE (ALIAS n_cell)
$property_slot_nodes([ppropertyslot_leaf]) = [HCELL n_cell]
(HCELL n_cell) <- S_pinned.ALLOCATIONS /\ n_cell <- S_pinned.REFCELLS
S_pinned.STORE[n_cell] = DEFINED (POBJECT n_leaf)
$heap_owners($heap_graph(S_pinned),HCELL n_cell) = 1
$heap_owners($heap_graph(S_pinned),HOBJECT n_leaf) = 1
''')
    leaf = checks.index('S_leaf_found = $request_finally_seek(S_pinned,703,4096)')
    checks[leaf] = 'S_leaf_found = $request_finally_seek(S_retired,703,4096)'
    transfer = child.fatal.lines(r'''
S_cell_found = $drive_steps(S_pinned,1)
S_cell_found.COMPLETION = BUDGET
S_cell = S_cell_found[.COMPLETION = NORMAL]
S_cell.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_cell) :: (INSTANCE_STORAGE_STEP pinstancestorage[.NEXT = 1]) :: ptask_pin_tail*
pdestructionrelease_cell.JOBS = [DESTRUCTION_VALUE (HCELL n_cell)]
$destructor_release_valid(S_cell,pdestructionrelease_cell)
$objectprops_at(S_cell.OBJECTPROPS,n_parent) = (ppropertyslot_cell*)
$property_slot_at(ppropertyslot_cell*,$ptascii("leaf")) = (ppropertyslot_leaf[.STATE = PROP_UNSET])
S_cell.STORE[n_cell] = S_pinned.STORE[n_cell]
$heap_owners($heap_graph(S_cell),HCELL n_cell) = 1
$heap_owners($heap_graph(S_cell),HOBJECT n_leaf) = 1
S_retired_found = $drive_steps(S_cell,1)
S_retired_found.COMPLETION = BUDGET
S_retired = S_retired_found[.COMPLETION = NORMAL]
pdestructionrelease_referent = pdestructionrelease_cell[.JOBS = [DESTRUCTION_VALUE (HOBJECT n_leaf)]]
S_retired.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_referent) :: (INSTANCE_STORAGE_STEP pinstancestorage[.NEXT = 1]) :: ptask_pin_tail*
$destructor_release_valid(S_retired,pdestructionrelease_referent)
~((HCELL n_cell) <- S_retired.ALLOCATIONS)
S_retired.STORE[n_cell] = S_pinned.STORE[n_cell]
$heap_owners($heap_graph(S_retired),HCELL n_cell) = 0
~((HEDGE (HCELL n_cell) (HOBJECT n_leaf)) <- $heap_graph(S_retired).EDGES)
$heap_owners($heap_graph(S_retired),HOBJECT n_leaf) = 1
''') + child.fatal.normal_valid('S_cell') + child.fatal.normal_valid('S_retired')
    checks[leaf:leaf] = transfer
    abrupt = checks.index('$generator_request_fatal_selected(S_abrupt) = (pgenfatal_new)')
    checks[abrupt:abrupt] = child.fatal.lines(r'''
pdestructionrelease_leaf_original = pdestructionrelease_referent
~((HCELL n_cell) <- S_abrupt.ALLOCATIONS)
n_cell <- S_abrupt.REFCELLS
S_abrupt.STORE[n_cell] = S_pinned.STORE[n_cell]
$heap_owners($heap_graph(S_abrupt),HCELL n_cell) = 0
~((HEDGE (HCELL n_cell) (HOBJECT n_leaf)) <- $heap_graph(S_abrupt).EDGES)
$generator_request_release_slot(S_abrupt,ppropertyslot_leaf,n_leaf)
''')
    report = checks.index('S_report.TODO = (GENERATOR_REQUEST_REPORT pgenfatal_new) :: ptask_abrupt_tail*')
    controls = []
    for label, field in [
        ('marker', '.REFCELLS = $request_called_drop(S_report.REFCELLS,n_cell)'),
        ('undefined', '.STORE = $set_cell(S_report.STORE,n_cell,UNDEFINED)'),
        ('scalar', '.STORE = $set_cell(S_report.STORE,n_cell,DEFINED (PINT 1))'),
        ('object', '.STORE = $set_cell(S_report.STORE,n_cell,DEFINED (POBJECT n_parent))'),
    ]:
        state = 'S_cell_' + label
        controls += [f'{state} = S_report[{field}]',
                     f'~$generator_request_release_slot({state},ppropertyslot_leaf,n_leaf)',
                     f'~$generator_request_report_valid({state},pgenfatal_new)',
                     f'{state}_throw = S_abrupt[{field.replace("S_report", "S_abrupt")}]',
                     f'$call_descriptors_valid({state}_throw)',
                     f'$generator_request_fatal_selected({state}_throw) = eps']
        reject(controls, 'reference_cell_' + label, state, 'S_report')
    controls += ['n_cell_beyond = |S_report.STORE|']
    for label, state in [
        ('live', 'S_report[.ALLOCATIONS = S_report.ALLOCATIONS ++ [HCELL n_cell]]'),
        ('bounds', 'S_report[.TODO = $child_pin_tasks(S_report.TODO,pinstancestorage[.NEXT = 1],[INSTANCE_STORAGE_STEP pinstancestorage[.NEXT = 1][.SLOTS = [ppropertyslot_leaf[.STATE = PROP_VALUE (ALIAS n_cell_beyond)]]]])]'),
        ('slot', 'S_report[.TODO = $child_pin_tasks(S_report.TODO,pinstancestorage[.NEXT = 1],[INSTANCE_STORAGE_STEP pinstancestorage[.NEXT = 1][.SLOTS = [ppropertyslot_leaf[.STATE = PROP_UNSET]]]])]'),
    ]:
        bad = 'S_cell_' + label
        controls += [f'{bad} = {state}', f'~$generator_request_report_valid({bad},pgenfatal_new)']
        reject(controls, 'reference_cell_' + label, bad, 'S_report', same_heap=label != 'live')
    controls += child.fatal.lines(r'''
S_cell_restored = S_report[.OBJECTPROPS = $objectprops_set(S_report.OBJECTPROPS,n_parent,[ppropertyslot_leaf])]
~$instance_storage_basic(S_cell_restored,pinstancestorage[.NEXT = 1])
~$generator_request_report_valid(S_cell_restored,pgenfatal_new)
~$call_descriptors_valid(S_cell_restored)
~$heap_valid($heap_graph(S_cell_restored))
S_cell_restored_checked = $call_entry_check(S_cell_restored)
S_cell_restored_checked.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"
''')
    checks[report:report] = controls
    for state in ['S_report', 'S_bailout', 'S_resumed', 'S_history']:
        checks += [f'~((HCELL n_cell) <- {state}.ALLOCATIONS)',
                   f'{state}.STORE[n_cell] = S_pinned.STORE[n_cell]',
                   f'$heap_owners($heap_graph({state}),HCELL n_cell) = 0',
                   f'~((HEDGE (HCELL n_cell) (HOBJECT n_leaf)) <- $heap_graph({state}).EDGES)']
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
        'tests/semantics/generator_request_reference_child_protocol.py',
    ]
    return driver.main()


if __name__ == '__main__':
    raise SystemExit(main())
