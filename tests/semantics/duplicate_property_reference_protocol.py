#!/usr/bin/env python3
"""Reached physical foreach selection and staged CV cleanup ownership."""
import argparse
import base64
import json
import os
from pathlib import Path
import tempfile

import dynamic_property_warning_sources as sources

ROOT = sources.ROOT
cross = sources.cross
CASES = {
    'physical':'duplicate-reference-foreach-escaped-first18',
    'binding':'duplicate-reference-foreach-binding-observation18',
    'pending-binding':'duplicate-reference-foreach-binding-throw18',
    'receiver-cleanup':'reference-foreach-receiver-cleanup-rebind18',
    'notice-owner':'reference-foreach-invalid-key-unset-receiver-key-observer18',
    'scalar-warning':'reference-foreach-scalar-handler-retirement18',
    'binding-gc':'duplicate-reference-foreach-binding-gc18',
    'container':'review-container-mutate-selected19',
    'container-throw':'review-container-first-throw19',
    'descendants':'review-descendant-order19',
    'descendants-throw':'review-descendant-two-throws19',
    'descendants-guard':'review-descendant-order19',
    'typed-slot':'review-typed-slot-two-sources-throw19',
    'typed-slot-fiber':'review-typed-slot-fiber19',
}
PREFIX = r'''
dec $dupref_is_output(pevent) : bool
dec $dupref_output(pevent*) : ptbytes
def $dupref_output(eps) = eps
def $dupref_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $dupref_output(pevent*)
def $dupref_output(pevent :: pevent_tail*) = $dupref_output(pevent_tail*) -- if ~$dupref_is_output(pevent)
def $dupref_is_output(OUTPUT ptbytes) = true
def $dupref_is_output(pevent) = false -- otherwise
dec $dupref_descendant_phase(pstate, ptbytes) : bool
def $dupref_descendant_phase(S, ptbytes) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OPERATION = (pdestructionoperation)
  -- if pdestructionoperation.SOURCE = FOREACH_BIND_RELEASE pforeachbind
  -- if pforeachbind.VALUE = POBJECT n_previous
  -- if $destructor_method(S, n_previous) = eps
  -- if $dupref_output(S.EVENTS) = ptbytes
def $dupref_descendant_phase(S, ptbytes) = false -- otherwise
dec $dupref_phase(pstate, nat) : bool
def $dupref_phase(S, 0) = true
  -- if S.TODO = (FOREACH_NEXT n (HCELL n_receiver) statement porigin? z) :: ptask_tail*
  -- if S.STORE[n_receiver] = DEFINED (POBJECT n_object)
  -- if $iterator_lookup(S.ITERATORS, n) = (OBJECTITER n n_object 0 true)
  -- if $objectprops_at(S.OBJECTPROPS, n_object) = ([{DECL eps, NAME $ptascii("x"), STATE PROP_VALUE (DIRECT (PINT 2))}, {DECL eps, NAME $ptascii("x"), STATE PROP_VALUE (DIRECT (PINT 7))}])
def $dupref_phase(S, 1) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (LIST_STORE (NExprVariable phpType32 metadata) (REFERENCE n_cell) true z) :: ptask_tail*
  -- if $cv_name(phpType32) = ($ptascii("value"))
  -- if $lookup(S.ENV, $ptascii("object")) = (n_cv)
  -- if S.STORE[n_cv] = DEFINED (POBJECT n_object)
  -- if $objectprops_at(S.OBJECTPROPS, n_object) = ([{DECL eps, NAME $ptascii("x"), STATE PROP_VALUE (ALIAS n_cell)}, {DECL eps, NAME $ptascii("x"), STATE PROP_VALUE (DIRECT (PINT 7))}])
def $dupref_phase(S, 2) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (LIST_STORE (NExprVariable phpType32 metadata) (REFERENCE n_cell) true z) :: ptask_tail*
  -- if $cv_name(phpType32) = ($ptascii("value"))
  -- if $lookup(S.ENV, $ptascii("object")) = (n_cv)
  -- if S.STORE[n_cv] = DEFINED (POBJECT n_object)
  -- if $objectprops_at(S.OBJECTPROPS, n_object) = ([{DECL eps, NAME $ptascii("x"), STATE PROP_VALUE (ALIAS n_first)}, {DECL eps, NAME $ptascii("x"), STATE PROP_VALUE (ALIAS n_cell)}])
  -- if n_first =/= n_cell
def $dupref_phase(S, 3) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if $dupref_output(S.EVENTS) = $ptascii("warning|2/7|2/9|x=12|x=9|12/12|")
  -- if $lookup(S.ENV, $ptascii("object")) = (n_cv)
  -- if S.STORE[n_cv] = DEFINED (POBJECT n_object)
  -- if $objectprops_at(S.OBJECTPROPS, n_object) = ([{DECL eps, NAME $ptascii("x"), STATE PROP_VALUE (ALIAS n_first)}, {DECL eps, NAME $ptascii("x"), STATE PROP_UNSET}])
def $dupref_phase(S, 4) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (FOREACH_BIND_RELEASE pforeachbind) :: ptask_tail*
def $dupref_phase(S, 5) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_operation_for(S) = eps
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OPERATION = (pdestructionoperation)
  -- if pdestructionoperation.SOURCE = FOREACH_BIND_RELEASE pforeachbind
  -- if $dupref_output(S.EVENTS) = $ptascii("warning|old|")
  -- if $objectprops_at(S.OBJECTPROPS, pforeachbind.OBJECT) = ([{DECL eps, NAME $ptascii("x"), STATE PROP_UNSET}, {DECL eps, NAME $ptascii("x"), STATE PROP_UNSET}])
def $dupref_phase(S, 6) = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (FOREACH_BIND_COMMIT pforeachbind) :: ptask_tail*
  -- if pdestructionoperation.SOURCE = FOREACH_BIND_RELEASE pforeachbind
def $dupref_phase(S, 7) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_operation_for(S) = eps
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OPERATION = (pdestructionoperation)
  -- if pdestructionoperation.SOURCE = FOREACH_BIND_RELEASE pforeachbind
  -- if $dupref_output(S.EVENTS) = $ptascii("old|receiver-drop|")
  -- if ~((HOBJECT pforeachbind.OBJECT) <- S.ALLOCATIONS)
def $dupref_phase(S, 8) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (LIST_STORE (NExprVariable phpType32 metadata) (REFERENCE n_cell) true z) :: ptask_tail*
  -- if $cv_name(phpType32) = ($ptascii("value"))
  -- if $dupref_output(S.EVENTS) = $ptascii("old|receiver-drop|x=1|")
def $dupref_phase(S, 9) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.TARGET = eps
  -- if perrorcall.RESUME = OBJECT_FOREACH_KEY pobjectforeach
def $dupref_phase(S, 10) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.TARGET = eps
  -- if perrorcall.RESUME = FOREACH_SCALAR_END n n_cell porigin pvalue z
def $dupref_phase(S, 11) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (FOREACH_SCALAR_END n n_cell porigin pvalue z) :: ptask_tail*
def $dupref_phase(S, 12) = true
  -- if S.TODO = (GC_TRACE pgccall) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OPERATION = (pdestructionoperation)
  -- if pdestructionoperation.SOURCE = FOREACH_BIND_RELEASE pforeachbind
def $dupref_phase(S, 13) = true
  -- if S.TODO = (FOREACH_BIND_RELEASE pforeachbind) :: ptask_tail*
  -- if pforeachbind.VALUE = PARRAY n_array
def $dupref_phase(S, 14) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OPERATION = (pdestructionoperation)
  -- if pdestructionoperation.SOURCE = FOREACH_BIND_RELEASE pforeachbind
  -- if pforeachbind.VALUE = PARRAY n_array
  -- if $dupref_output(S.EVENTS) = $ptascii("A|")
def $dupref_phase(S, 15) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OPERATION = (pdestructionoperation)
  -- if pdestructionoperation.SOURCE = FOREACH_BIND_RELEASE pforeachbind
  -- if pforeachbind.VALUE = PARRAY n_array
  -- if $dupref_output(S.EVENTS) = $ptascii("A|B|")
def $dupref_phase(S, 16) = true
  -- if S.TODO = (FOREACH_BIND_RELEASE pforeachbind) :: ptask_tail*
  -- if pforeachbind.VALUE = POBJECT n_previous
  -- if $destructor_method(S, n_previous) = eps
def $dupref_phase(S, 17) = $dupref_descendant_phase(S, $ptascii("B|"))
def $dupref_phase(S, 18) = $dupref_descendant_phase(S, $ptascii("B|A|"))
def $dupref_phase(S, 19) = $dupref_descendant_phase(S, $ptascii("A|"))
def $dupref_phase(S, 20) = $dupref_descendant_phase(S, $ptascii("A|B|"))
def $dupref_phase(S, 21) = $dupref_descendant_phase(S, $ptascii("A|"))
def $dupref_phase(S, 22) = true
  -- if S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask*
  -- if pdestructionrelease.JOBS = (DESTRUCTION_PROP_SOURCE pproptypesource n_cell) :: pdestructionjob*
def $dupref_phase(S, 24) = true
  -- if S.ACTIVEFIBER = eps /\ S.CURRENT = eps /\ S.FRAMES = eps
  -- if $dupref_output(S.EVENTS) = $ptascii("A|")
  -- if $lookup(S.ENV, $ptascii("fiber")) = (n_cv)
  -- if S.STORE[n_cv] = DEFINED (POBJECT n_fiber)
  -- if $fiber_at(S, n_fiber) = (pfiber)
  -- if pfiber.STATUS = FIBER_SUSPENDED
def $dupref_phase(S, 27) = $dupref_descendant_phase(S, $ptascii("A|B|type|"))
def $dupref_phase(S, n) = false -- otherwise
dec $dupref_seek(pstate, nat, nat) : pstate
def $dupref_seek(S, n_phase, n) = S -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $dupref_seek(S, n_phase, n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $dupref_phase(S, n_phase)
def $dupref_seek(S, n_phase, 0) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$dupref_phase(S, n_phase)
def $dupref_seek(S, n_phase, n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$dupref_phase(S, n_phase)
  -- if $(n > 0) /\ S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps
def $dupref_seek(S, n_phase, n) = $dupref_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_phase, $nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$dupref_phase(S, n_phase)
  -- if $(n > 0)
  -- if S.TODO =/= eps \/ S.CURRENT =/= eps \/ S.FRAMES =/= eps
'''


def valid(state):
    return [f'$call_descriptors_valid({state})', f'$heap_valid($heap_graph({state}))']


def seek(parent, state, phase):
    return [f'{state}_found = $dupref_seek({parent}, {phase}, 2048)',
            fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$dupref_phase({state}, {phase})', *valid(state)]


def physical_assertions(initial, expected):
    return ['S_initial = '+initial, '~S_initial.COMPILESTOP',
        *seek('S_initial', 'S_before', 0),
        'S_before.TODO = (FOREACH_NEXT n_iterator (HCELL n_receiver) statement porigin_foreach? z_foreach) :: ptask_before_tail*',
        'S_before.STORE[n_receiver] = DEFINED (POBJECT n_object)',
        'n_receiver <- S_before.REFCELLS',
        '$heap_owners($heap_graph(S_before), HCELL n_receiver) = 2',
        '$task_nodes(FOREACH_NEXT n_iterator (HCELL n_receiver) statement porigin_foreach? z_foreach) = [HCELL n_receiver]',
        'ptask_owner_bad = FOREACH_NEXT n_iterator (HOBJECT n_object) statement porigin_foreach? z_foreach',
        'S_owner_bad = S_before[.TODO = ptask_owner_bad :: ptask_before_tail*]',
        '$heap_valid($heap_graph(S_owner_bad))',
        '~$goto_marker_valid(S_owner_bad, ptask_owner_bad)',
        '~$call_descriptors_valid(S_owner_bad)',
        'S_owner_rejected = $drive(S_owner_bad, 0)',
        'S_owner_rejected.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"',
        'statement = NStmtForeach expression_iterable phpType5 (BOOLEAN true) expression_value phpType23 (BOOLEAN false) metadata_foreach',
        '$objectprops_at(S_before.OBJECTPROPS, n_object) = (ppropertyslot_before*)',
        '$property_next(S_before, n_object, ppropertyslot_before*, 0, 0) = ($ptascii("x"), DIRECT (PINT 2), 1)',
        '$property_duplicate_table(S_before, n_object)',
        '$property_foreach_selected_slot(S_before, n_object, 1, $ptascii("x")) = (ppropertyslot_first)',
        'ppropertyslot_first.STATE = PROP_VALUE (DIRECT (PINT 2))',
        '$property_foreach_selected_slot(S_before, n_object, 0, $ptascii("x")) = eps',
        '$property_foreach_selected_slot(S_before, n_object, 3, $ptascii("x")) = eps',
        '$property_foreach_selected_slot(S_before, n_object, 1, $ptascii("y")) = eps',
        *seek('S_before', 'S_first', 1),
        'S_first.TODO = (LIST_STORE expression_value (REFERENCE n_first) true z_value) :: ptask_first_tail*',
        'S_first.STORE[n_first] = DEFINED (PINT 2)',
        'n_first <- S_first.REFCELLS',
        '$iterator_lookup(S_first.ITERATORS, n_iterator) = (OBJECTITER n_iterator n_object 1 true)',
        '$heap_owners($heap_graph(S_first), HCELL n_first) = 2',
        '$task_nodes(LIST_STORE expression_value (REFERENCE n_first) true z_value) = [HCELL n_first]',
        'S_zero = $drive(S_first, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S_first',
        'S_one_found = $drive_steps(S_first, 1)', 'S_one_found.COMPLETION = BUDGET',
        'S_one = S_one_found[.COMPLETION = NORMAL]', *valid('S_one'),
        '$lookup(S_one.ENV, $ptascii("value")) = (n_first)',
        '$heap_owners($heap_graph(S_one), HCELL n_first) = 2',
        *seek('S_one', 'S_second', 2),
        'S_second.TODO = (LIST_STORE expression_value (REFERENCE n_second) true z_value) :: ptask_second_tail*',
        'n_second =/= n_first', 'S_second.STORE[n_second] = DEFINED (PINT 7)',
        'S_second.STORE[n_first] = DEFINED (PINT 2)',
        '$lookup(S_second.ENV, $ptascii("first")) = (n_first)',
        '$lookup(S_second.ENV, $ptascii("value")) = (n_first)',
        '$iterator_lookup(S_second.ITERATORS, n_iterator) = (OBJECTITER n_iterator n_object 2 true)',
        '$heap_owners($heap_graph(S_second), HCELL n_second) = 2',
        '$heap_owners($heap_graph(S_second), HCELL n_first) = 3',
        *seek('S_second', 'S_deleted', 3),
        '$lookup(S_deleted.ENV, $ptascii("first")) = (n_first)',
        'S_deleted.STORE[n_first] = DEFINED (PINT 12)',
        '$objectprops_at(S_deleted.OBJECTPROPS, n_object) = (ppropertyslot_deleted*)',
        '$property_slot_at(ppropertyslot_deleted*, $ptascii("x")) = (ppropertyslot_visible)',
        'ppropertyslot_visible.STATE = PROP_VALUE (ALIAS n_first)',
        '$heap_owners($heap_graph(S_deleted), HCELL n_first) = 2',
        '~$heap_member(HCELL n_second, S_deleted.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_deleted), HCELL n_second) = 0',
        'S_done = $drive(S_deleted, 2048)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        'S_done.ITERATORS = eps', 'S_done.DESTRUCTION.OPERATIONS = eps',
        '$dupref_output(S_done.EVENTS) = $ptascii('+json.dumps(expected)+')',
        *valid('S_done')]


def binding_assertions(initial, expected, pending):
    clauses = ['S_initial = '+initial, '~S_initial.COMPILESTOP',
        *seek('S_initial', 'S_release', 4),
        'S_release.TODO = (FOREACH_BIND_RELEASE pforeachbind) :: ptask_release_tail*',
        'pforeachbind.NAME = $ptascii("value")', 'pforeachbind.KEY = $ptascii("x")',
        'pforeachbind.POSITION = 1', 'pforeachbind.VALUE = POBJECT n_previous',
        'S_release.STORE[pforeachbind.OLD] = DEFINED (POBJECT n_previous)',
        'S_release.STORE[pforeachbind.NEW] = DEFINED (PINT 2)',
        '$lookup(S_release.ENV, pforeachbind.NAME) = (pforeachbind.OLD)',
        '~(pforeachbind.OLD <- S_release.REFCELLS)',
        'pforeachbind.NEW <- S_release.REFCELLS',
        '$foreach_bind_capture(S_release, pforeachbind.NAME, pforeachbind.NEW, pforeachbind.LINE) = (pforeachbind)',
        '$call_task_valid(S_release, FOREACH_BIND_RELEASE pforeachbind)',
        '~$foreach_released_cell(S_release, pforeachbind.OLD)',
        '$node_children(S_release, HCELL pforeachbind.OLD) = [HOBJECT n_previous]',
        '$task_nodes(FOREACH_BIND_RELEASE pforeachbind) = [HCELL pforeachbind.NEW]',
        '$task_nodes(FOREACH_BIND_COMMIT pforeachbind) = [HCELL pforeachbind.NEW]',
        '$heap_owners($heap_graph(S_release), HCELL pforeachbind.NEW) = 2',
        'S_release_zero = $drive(S_release, 0)', 'S_release_zero.COMPLETION = BUDGET',
        'S_release_zero[.COMPLETION = NORMAL] = S_release']
    for label, change in [('line', '[.LINE = $(pforeachbind.LINE + 1)]'),
                          ('cell', '[.NEW = n_receiver_cell]')]:
        if label=='cell':
            clauses += ['$lookup(S_release.ENV, $ptascii("object")) = (n_receiver_cell)',
                        'n_receiver_cell =/= pforeachbind.NEW', 'n_receiver_cell <- S_release.REFCELLS']
        clauses += [f'pforeachbind_bad_{label} = pforeachbind'+change,
            f'S_bad_{label} = S_release[.TODO = (FOREACH_BIND_RELEASE pforeachbind_bad_{label}) :: ptask_release_tail*]',
            f'$heap_valid($heap_graph(S_bad_{label}))',
            f'~$call_task_valid(S_bad_{label}, FOREACH_BIND_RELEASE pforeachbind_bad_{label})',
            f'~$call_descriptors_valid(S_bad_{label})',
            f'S_rejected_{label} = $drive(S_bad_{label}, 0)',
            f'S_rejected_{label}.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"']
    clauses += [*seek('S_release', 'S_cleanup', 5),
        'S_cleanup.CURRENT = (pcallcontext_cleanup)',
        '$destructor_context_call(pcallcontext_cleanup, S_cleanup.CURRENT, S_cleanup.FRAMES) = (pdestructorcall)',
        'pdestructorcall.OPERATION = (pdestructionoperation_cleanup)',
        'pdestructionoperation_cleanup.SOURCE = FOREACH_BIND_RELEASE pforeachbind',
        'pdestructorcall.OBJECT = n_previous',
        '$foreach_released_cell(S_cleanup, pforeachbind.OLD)',
        '$node_children(S_cleanup, HCELL pforeachbind.OLD) = eps',
        'S_cleanup.STORE[pforeachbind.OLD] = DEFINED (POBJECT n_previous)',
        '(HOBJECT n_previous) <- S_cleanup.ALLOCATIONS',
        'S_cleanup.STORE[pforeachbind.NEW] = DEFINED (PINT 2)',
        '$heap_owners($heap_graph(S_cleanup), HCELL pforeachbind.NEW) = 1',
        'S_read = $global_read_name(S_cleanup, pforeachbind.NAME, pforeachbind.LINE)',
        'S_read.COMPLETION = NORMAL', 'S_read.RESULT = KNOWN (POBJECT n_previous)',
        '$foreach_released_cell(S_read, pforeachbind.OLD)',
        '$foreach_bind_scope(S_cleanup, pforeachbind, S_cleanup.FRAMES) = (S_caller)',
        '$lookup(S_caller.ENV, pforeachbind.NAME) = (pforeachbind.OLD)',
        *seek('S_cleanup', 'S_finish', 6),
        'S_finish.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (FOREACH_BIND_COMMIT pforeachbind) :: ptask_finish_tail*',
        'pdestructionoperation.SOURCE = FOREACH_BIND_RELEASE pforeachbind',
        '$call_task_valid(S_finish, DESTRUCTOR_OPERATION_EXIT pdestructionoperation)',
        '$foreach_bind_operation_source_valid(S_finish, pdestructionoperation, pforeachbind)',
        '$eager_operation_source_valid(S_finish, pdestructionoperation)',
        '$foreach_released_cell(S_finish, pforeachbind.OLD)',
        '$node_children(S_finish, HCELL pforeachbind.OLD) = eps',
        '$heap_owners($heap_graph(S_finish), HCELL pforeachbind.NEW) = 1']
    if pending:
        clauses += ['pdestructionoperation.PENDING = (n_pending)',
            '$throwable_live(S_finish, n_pending)',
            '$heap_owners($heap_graph(S_finish), HOBJECT n_pending) = 1']
    else:
        clauses += ['pdestructionoperation.PENDING = eps']
    clauses += ['S_one_found = $drive_steps(S_finish, 1)',
        'S_one_found.COMPLETION = BUDGET', 'S_one = S_one_found[.COMPLETION = NORMAL]',
        *valid('S_one'),
        '$lookup(S_one.ENV, pforeachbind.NAME) = (pforeachbind.NEW)',
        'S_one.STORE[pforeachbind.OLD] = UNDEFINED',
        'S_one.STORE[pforeachbind.NEW] = DEFINED (PINT 2)',
        '~$foreach_released_cell(S_one, pforeachbind.OLD)',
        '$heap_owners($heap_graph(S_one), HCELL pforeachbind.NEW) = 1',
        'S_one.DESTRUCTION.OPERATIONS = eps',
        '$dupref_output(S_one.EVENTS) = $ptascii("warning|old|")']
    if pending:
        clauses += ['S_one.TODO = (THROW_SEARCH n_pending) :: ptask_finish_tail*',
            '$heap_owners($heap_graph(S_one), HOBJECT n_pending) = 1']
    else:
        clauses += ['S_one.TODO = ptask_finish_tail*']
    return clauses+['S_done = $drive(S_one, 2048)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        'S_done.ITERATORS = eps', 'S_done.DESTRUCTION.OPERATIONS = eps',
        '$dupref_output(S_done.EVENTS) = $ptascii('+json.dumps(expected)+')', *valid('S_done')]


def receiver_cleanup_assertions(initial, expected):
    return ['S_initial = '+initial, '~S_initial.COMPILESTOP',
        *seek('S_initial', 'S_release', 4),
        'S_release.TODO = (FOREACH_BIND_RELEASE pforeachbind) :: ptask_release_tail*',
        '$foreach_bind_capture(S_release, pforeachbind.NAME, pforeachbind.NEW, pforeachbind.LINE) = (pforeachbind)',
        'pforeachbind.OWNER = HCELL n_receiver',
        '$lookup(S_release.ENV, $ptascii("object")) = (n_receiver)',
        'n_receiver <- S_release.REFCELLS',
        'S_release.STORE[n_receiver] = DEFINED (POBJECT pforeachbind.OBJECT)',
        'S_release.STORE[pforeachbind.OLD] = DEFINED (POBJECT n_previous)',
        'S_release.STORE[pforeachbind.NEW] = DEFINED (PINT 1)',
        '$heap_owners($heap_graph(S_release), HCELL pforeachbind.NEW) = 2',
        *seek('S_release', 'S_cleanup', 7),
        'S_cleanup.CURRENT = (pcallcontext_cleanup)',
        '$destructor_context_call(pcallcontext_cleanup, S_cleanup.CURRENT, S_cleanup.FRAMES) = (pdestructorcall)',
        'pdestructorcall.OPERATION = (pdestructionoperation_cleanup)',
        'pdestructionoperation_cleanup.SOURCE = FOREACH_BIND_RELEASE pforeachbind',
        'pdestructorcall.OBJECT = n_previous',
        '$foreach_released_cell(S_cleanup, pforeachbind.OLD)',
        '$node_children(S_cleanup, HCELL pforeachbind.OLD) = eps',
        'S_cleanup.STORE[pforeachbind.OLD] = DEFINED (POBJECT n_previous)',
        'S_cleanup.STORE[n_receiver] = DEFINED (POBJECT n_next_receiver)',
        'n_next_receiver =/= pforeachbind.OBJECT',
        '(HOBJECT n_next_receiver) <- S_cleanup.ALLOCATIONS',
        '~((HOBJECT pforeachbind.OBJECT) <- S_cleanup.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_cleanup), HOBJECT pforeachbind.OBJECT) = 0',
        'S_cleanup.STORE[pforeachbind.NEW] = DEFINED (PINT 1)',
        '$heap_owners($heap_graph(S_cleanup), HCELL pforeachbind.NEW) = 1',
        '$task_nodes(FOREACH_BIND_COMMIT pforeachbind) = [HCELL pforeachbind.NEW]',
        '$foreach_bind_scope(S_cleanup, pforeachbind, S_cleanup.FRAMES) = (S_caller)',
        '$lookup(S_caller.ENV, pforeachbind.NAME) = (pforeachbind.OLD)',
        *seek('S_cleanup', 'S_finish', 6),
        'S_finish.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (FOREACH_BIND_COMMIT pforeachbind) :: ptask_finish_tail*',
        'pdestructionoperation.SOURCE = FOREACH_BIND_RELEASE pforeachbind',
        'pdestructionoperation.PENDING = eps',
        '$foreach_bind_operation_source_valid(S_finish, pdestructionoperation, pforeachbind)',
        '$eager_operation_source_valid(S_finish, pdestructionoperation)',
        'S_one_found = $drive_steps(S_finish, 1)',
        'S_one_found.COMPLETION = BUDGET', 'S_one = S_one_found[.COMPLETION = NORMAL]',
        *valid('S_one'),
        '$lookup(S_one.ENV, pforeachbind.NAME) = (pforeachbind.NEW)',
        'S_one.STORE[pforeachbind.OLD] = UNDEFINED',
        'S_one.STORE[pforeachbind.NEW] = DEFINED (PINT 1)',
        '$heap_owners($heap_graph(S_one), HCELL pforeachbind.NEW) = 1',
        '~$foreach_released_cell(S_one, pforeachbind.OLD)',
        'S_one.TODO = ptask_finish_tail*',
        '$dupref_output(S_one.EVENTS) = $ptascii("old|receiver-drop|")',
        *seek('S_one', 'S_next', 8),
        'S_next.TODO = (LIST_STORE expression_value (REFERENCE n_next_cell) true z_value) :: ptask_next_tail*',
        '$lookup(S_next.ENV, $ptascii("object")) = (n_receiver)',
        'S_next.STORE[n_receiver] = DEFINED (POBJECT n_next_receiver)',
        '$iterator_lookup(S_next.ITERATORS, pforeachbind.ITERATOR) = (OBJECTITER pforeachbind.ITERATOR n_next_receiver 1 true)',
        'S_next.STORE[pforeachbind.NEW] = DEFINED (PINT 1)',
        '$heap_owners($heap_graph(S_next), HCELL pforeachbind.NEW) = 1',
        'S_next.STORE[n_next_cell] = DEFINED (PINT 3)',
        '$heap_owners($heap_graph(S_next), HCELL n_next_cell) = 2',
        'n_next_cell =/= pforeachbind.NEW',
        'S_done = $drive(S_next, 2048)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        'S_done.ITERATORS = eps', 'S_done.DESTRUCTION.OPERATIONS = eps',
        '$dupref_output(S_done.EVENTS) = $ptascii('+json.dumps(expected)+')', *valid('S_done')]


def notice_owner_assertions(initial):
    return ['S_initial = '+initial, '~S_initial.COMPILESTOP',
        *seek('S_initial', 'S_notice', 9),
        'S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_notice_tail*',
        'perrorcall.RESUME = OBJECT_FOREACH_KEY pobjectforeach',
        'pobjectforeach.REF',
        'pobjectforeach.OWNER = HCELL n_receiver',
        '$lookup(S_notice.ENV, $ptascii("object")) = (n_receiver)',
        'n_receiver <- S_notice.REFCELLS',
        'S_notice.STORE[n_receiver] = DEFINED (POBJECT pobjectforeach.OBJECT)',
        '$task_nodes(perrorcall.RESUME) = [HCELL n_receiver]',
        '$object_foreach_owner_valid(S_notice, pobjectforeach)',
        '$error_call_valid(S_notice, perrorcall)',
        '$dupref_output(S_notice.EVENTS) = eps',
        'S_notice_zero = $drive(S_notice, 0)',
        'S_notice_zero.COMPLETION = BUDGET',
        'S_notice_zero[.COMPLETION = NORMAL] = S_notice',
        'pobjectforeach_bad = pobjectforeach[.OWNER = HOBJECT pobjectforeach.OBJECT]',
        'perrorcall_bad = perrorcall[.RESUME = OBJECT_FOREACH_KEY pobjectforeach_bad]',
        'S_bad = S_notice[.TODO = (ERROR_HANDLER_INVOKE perrorcall_bad) :: ptask_notice_tail*]',
        '$heap_valid($heap_graph(S_bad))',
        '~$object_foreach_owner_valid(S_bad, pobjectforeach_bad)',
        '~$error_call_valid(S_bad, perrorcall_bad)',
        '~$call_descriptors_valid(S_bad)',
        'S_rejected = $drive(S_bad, 0)',
        'S_rejected.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"']


def scalar_warning_assertions(initial, expected):
    return ['S_initial = '+initial, '~S_initial.COMPILESTOP',
        *seek('S_initial', 'S_notice', 10),
        'S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_notice_tail*',
        'perrorcall.RESUME = FOREACH_SCALAR_END n_iterator n_receiver porigin (PINT 7) z',
        '$lookup(S_notice.ENV, $ptascii("object")) = (n_receiver)',
        'n_receiver <- S_notice.REFCELLS',
        'S_notice.STORE[n_receiver] = DEFINED (PINT 7)',
        '$heap_owners($heap_graph(S_notice), HCELL n_receiver) = 2',
        '$iterator_lookup(S_notice.ITERATORS, n_iterator) = (OBJECTITER n_iterator n_previous 1 true)',
        '~((HOBJECT n_previous) <- S_notice.ALLOCATIONS)',
        '$task_nodes(perrorcall.RESUME) = [HCELL n_receiver]',
        '$error_task_iterator(perrorcall.RESUME) = [n_iterator]',
        '$foreach_scalar_valid(S_notice, n_iterator, n_receiver, porigin, PINT 7, z)',
        '$error_call_valid(S_notice, perrorcall)',
        'perrorcall.LEVEL = 2',
        'perrorcall.MESSAGE = $ptascii("foreach() argument must be of type array|object, int given")',
        '$dupref_output(S_notice.EVENTS) = $ptascii("x=1|receiver-drop|")',
        'S_notice_zero = $drive(S_notice, 0)',
        'S_notice_zero.COMPLETION = BUDGET',
        'S_notice_zero[.COMPLETION = NORMAL] = S_notice',
        'ptask_bad = FOREACH_SCALAR_END n_iterator n_receiver porigin (PINT 8) z',
        '$foreach_scalar_valid(S_notice, n_iterator, n_receiver, porigin, PINT 8, z)',
        'perrorcall_bad = perrorcall[.RESUME = ptask_bad]',
        'S_bad = S_notice[.TODO = (ERROR_HANDLER_INVOKE perrorcall_bad) :: ptask_notice_tail*]',
        '$heap_valid($heap_graph(S_bad))',
        '~$error_call_valid(S_bad, perrorcall_bad)',
        '~$call_descriptors_valid(S_bad)',
        'S_rejected = $drive(S_bad, 0)',
        'S_rejected.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"',
        *seek('S_notice', 'S_end', 11),
        'S_end.TODO = (FOREACH_SCALAR_END n_iterator n_receiver porigin (PINT 7) z) :: ptask_end_tail*',
        '$lookup(S_end.ENV, $ptascii("object")) = eps',
        'S_end.STORE[n_receiver] = DEFINED (POBJECT n_replacement)',
        'n_replacement =/= n_previous',
        '(HOBJECT n_replacement) <- S_end.ALLOCATIONS',
        '$heap_owners($heap_graph(S_end), HCELL n_receiver) = 1',
        '$heap_owners($heap_graph(S_end), HOBJECT n_replacement) = 1',
        '$task_nodes(FOREACH_SCALAR_END n_iterator n_receiver porigin (PINT 7) z) = [HCELL n_receiver]',
        '$foreach_scalar_valid(S_end, n_iterator, n_receiver, porigin, PINT 7, z)',
        '$iterator_lookup(S_end.ITERATORS, n_iterator) = (OBJECTITER n_iterator n_previous 1 true)',
        '$dupref_output(S_end.EVENTS) = $ptascii("x=1|receiver-drop|level|captured|")',
        'S_discarded = $error_read_discard(S_end, FOREACH_SCALAR_END n_iterator n_receiver porigin (PINT 7) z)',
        'S_discarded.ITERATORS = eps',
        'S_discarded.STORE = S_end.STORE',
        'S_end_zero = $drive(S_end, 0)',
        'S_end_zero.COMPLETION = BUDGET',
        'S_end_zero[.COMPLETION = NORMAL] = S_end',
        'S_one_found = $drive_steps(S_end, 1)',
        'S_one_found.COMPLETION = BUDGET',
        'S_one = S_one_found[.COMPLETION = NORMAL]', *valid('S_one'),
        'S_one.ITERATORS = eps',
        'S_done = $drive(S_one, 2048)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        'S_done.ITERATORS = eps', 'S_done.DESTRUCTION.OPERATIONS = eps',
        '$lookup(S_done.ENV, $ptascii("object")) = eps',
        '$dupref_output(S_done.EVENTS) = $ptascii('+json.dumps(expected)+')', *valid('S_done')]


def binding_gc_assertions(initial, expected):
    return ['S_initial = '+initial, '~S_initial.COMPILESTOP',
        *seek('S_initial', 'S_release', 4),
        'S_release.TODO = (FOREACH_BIND_RELEASE pforeachbind) :: ptask_release_tail*',
        'pforeachbind.VALUE = POBJECT n_previous',
        'pforeachbind.NAME = $ptascii("value")',
        '$node_children(S_release, HCELL pforeachbind.OLD) = [HOBJECT n_previous]',
        *seek('S_release', 'S_gc', 12),
        'S_gc.TODO = (GC_TRACE pgccall) :: ptask_gc_tail*',
        'S_gc.GC.ACTIVE = (pgccall)',
        '$gc_trace_valid(S_gc, pgccall)',
        'S_gc.FRAMES = [pframe_saved]',
        '$foreach_bind_scope(S_gc, pforeachbind, S_gc.FRAMES) = (S_caller)',
        '$foreach_bind_body_valid(S_caller, pforeachbind)',
        '$foreach_bind_address_valid(S_caller, pforeachbind)',
        '$foreach_bind_operation_queued(pframe_saved.TODO, pforeachbind)',
        '$foreach_bind_pending_frames(S_gc, pforeachbind.OLD, S_gc.FRAMES)',
        '~$foreach_bind_pending_tasks(S_gc, pforeachbind.OLD, S_gc.TODO)',
        '$foreach_released_cell(S_gc, pforeachbind.OLD)',
        'S_gc.STORE[pforeachbind.OLD] = DEFINED (POBJECT n_previous)',
        '$node_children(S_gc, HCELL pforeachbind.OLD) = eps',
        'S_gc.STORE[pforeachbind.NEW] = DEFINED (PINT 2)',
        '$heap_owners($heap_graph(S_gc), HCELL pforeachbind.NEW) = 1',
        '(HCELL pforeachbind.NEW) <- $frames_roots(S_gc.FRAMES)',
        '~((HCELL pforeachbind.NEW) <- $tasks_nodes(S_gc.TODO))',
        '$task_nodes(FOREACH_BIND_COMMIT pforeachbind) = [HCELL pforeachbind.NEW]',
        '$task_nodes(GC_TRACE pgccall) = eps',
        'S_read = $global_read_name(S_gc, pforeachbind.NAME, pforeachbind.LINE)',
        'S_read.COMPLETION = NORMAL', 'S_read.RESULT = KNOWN (POBJECT n_previous)',
        'pfibervm = $fiber_vm(S_gc)',
        '$foreach_bind_pending_vm(S_gc, pforeachbind.OLD, pfibervm)',
        '(HCELL pforeachbind.NEW) <- $fiber_vm_nodes(pfibervm)',
        'pfibervm.FRAMES = S_gc.FRAMES',
        'pfibervm.DESTRUCTOROPERATIONS = S_gc.DESTRUCTION.OPERATIONS',
        'S_restored = $fiber_vm_restore(S_gc, pfibervm)',
        '$foreach_released_cell(S_restored, pforeachbind.OLD)',
        '$node_children(S_restored, HCELL pforeachbind.OLD) = eps',
        '$heap_owners($heap_graph(S_restored), HCELL pforeachbind.NEW) = 1',
        'pforeachbind_bad = pforeachbind[.LINE = $(pforeachbind.LINE + 1)]',
        '~$foreach_bind_body_valid(S_caller, pforeachbind_bad)',
        '~$call_task_valid(S_caller, FOREACH_BIND_COMMIT pforeachbind_bad)',
        'S_zero = $drive(S_gc, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S_gc',
        'S_one_found = $drive_steps(S_gc, 1)', 'S_one_found.COMPLETION = BUDGET',
        'S_one = S_one_found[.COMPLETION = NORMAL]', *valid('S_one'),
        '$foreach_released_cell(S_one, pforeachbind.OLD)',
        '$node_children(S_one, HCELL pforeachbind.OLD) = eps',
        '$heap_owners($heap_graph(S_one), HCELL pforeachbind.NEW) = 1',
        *seek('S_one', 'S_finish', 6),
        'S_finish.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (FOREACH_BIND_COMMIT pforeachbind) :: ptask_finish_tail*',
        'pdestructionoperation.SOURCE = FOREACH_BIND_RELEASE pforeachbind',
        'pdestructionoperation.PENDING = eps',
        '$foreach_bind_operation_source_valid(S_finish, pdestructionoperation, pforeachbind)',
        '$dupref_output(S_finish.EVENTS) = $ptascii("warning|old|0|")',
        'S_commit_found = $drive_steps(S_finish, 1)', 'S_commit_found.COMPLETION = BUDGET',
        'S_commit = S_commit_found[.COMPLETION = NORMAL]', *valid('S_commit'),
        '$lookup(S_commit.ENV, pforeachbind.NAME) = (pforeachbind.NEW)',
        'S_commit.STORE[pforeachbind.OLD] = UNDEFINED',
        '~$foreach_released_cell(S_commit, pforeachbind.OLD)',
        'S_done = $drive(S_commit, 2048)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        'S_done.ITERATORS = eps', 'S_done.DESTRUCTION.OPERATIONS = eps',
        'S_done.GC.ACTIVE = eps', 'S_done.GC.PLAN = eps',
        '$dupref_output(S_done.EVENTS) = $ptascii('+json.dumps(expected)+')', *valid('S_done')]


def container_assertions(initial, expected, pending, descendants=False):
    payload = 'POBJECT n_previous' if descendants else 'PARRAY n_array'
    node = 'HOBJECT n_previous' if descendants else 'HARRAY n_array'
    phase_first, phase_second = ((19, 20) if pending else (17, 18)) if descendants else (14, 15)
    markers = 'B|A|' if descendants and not pending else 'A|B|'
    final_value = '2' if pending or descendants else '9'
    final_pending = 'n_final' if descendants else 'n_pending'
    clauses = ['S_initial = '+initial, '~S_initial.COMPILESTOP',
        *seek('S_initial', 'S_release', 16 if descendants else 13),
        'S_release.TODO = (FOREACH_BIND_RELEASE pforeachbind) :: ptask_release_tail*',
        'pforeachbind.VALUE = '+payload,
        'pforeachbind.NAME = $ptascii("value")', 'pforeachbind.KEY = $ptascii("x")',
        'S_release.STORE[pforeachbind.OLD] = DEFINED ('+payload+')',
        '~(pforeachbind.OLD <- S_release.REFCELLS)',
        '$node_children(S_release, HCELL pforeachbind.OLD) = ['+node+']',
        '('+node+') <- S_release.ALLOCATIONS',
        '$heap_owners($heap_graph(S_release), '+node+') = 1']
    if descendants:
        clauses += ['$destructor_method(S_release, n_previous) = eps',
            '$objectprops_at(S_release.OBJECTPROPS, n_previous) = ([ppropertyslot_parent_first, ppropertyslot_parent_second])']
        if pending:
            clauses += ['ppropertyslot_parent_first.DECL =/= eps /\\ ppropertyslot_parent_second.DECL =/= eps',
                'ppropertyslot_parent_first.STATE = PROP_VALUE (DIRECT (POBJECT n_first))',
                'ppropertyslot_parent_second.STATE = PROP_VALUE (DIRECT (POBJECT n_second))']
        else:
            clauses += ['ppropertyslot_parent_first.DECL =/= eps /\\ ppropertyslot_parent_second.DECL = eps',
                'ppropertyslot_parent_first.STATE = PROP_VALUE (DIRECT (POBJECT n_second))',
                'ppropertyslot_parent_second.STATE = PROP_VALUE (DIRECT (POBJECT n_first))',
                '$property_slot_nodes([ppropertyslot_parent_first, ppropertyslot_parent_second]) = [HOBJECT n_second, HOBJECT n_first]']
        clauses += ['$property_release_nodes([ppropertyslot_parent_first, ppropertyslot_parent_second]) = [HOBJECT n_first, HOBJECT n_second]']
    else:
        clauses += ['S_release.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_first)), ENTRY (KINT 1) (DIRECT (POBJECT n_second))]']
    clauses += [
        'n_first =/= n_second',
        '$heap_owners($heap_graph(S_release), HOBJECT n_first) = 1',
        '$heap_owners($heap_graph(S_release), HOBJECT n_second) = 1',
        'S_release.STORE[pforeachbind.NEW] = DEFINED (PINT 2)',
        '$heap_owners($heap_graph(S_release), HCELL pforeachbind.NEW) = 2',
        '$foreach_bind_capture(S_release, pforeachbind.NAME, pforeachbind.NEW, pforeachbind.LINE) = (pforeachbind)',
        '$call_task_valid(S_release, FOREACH_BIND_RELEASE pforeachbind)',
        'S_wrapper = S_release[.REFCELLS = pforeachbind.OLD :: S_release.REFCELLS]',
        '$heap_valid($heap_graph(S_wrapper))',
        '$foreach_bind_capture(S_wrapper, pforeachbind.NAME, pforeachbind.NEW, pforeachbind.LINE) = eps',
        '~$call_task_valid(S_wrapper, FOREACH_BIND_RELEASE pforeachbind)',
        'S_zero = $drive(S_release, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S_release',
        *seek('S_release', 'S_first', phase_first),
        'S_first.CURRENT = (pcallcontext_first)',
        '$destructor_context_call(pcallcontext_first, S_first.CURRENT, S_first.FRAMES) = (pdestructorcall_first)',
        'pdestructorcall_first.OBJECT = n_first',
        'pdestructorcall_first.OPERATION = (pdestructionoperation_first)',
        'pdestructionoperation_first.SOURCE = FOREACH_BIND_RELEASE pforeachbind',
        'pdestructorcall_first.PENDING = eps',
        'n_first <- S_first.DESTRUCTION.CALLED',
        '~(n_second <- S_first.DESTRUCTION.CALLED)',
        '$heap_owners($heap_graph(S_first), HOBJECT n_first) = 2',
        '$heap_owners($heap_graph(S_first), HOBJECT n_second) = 1',
        '~(('+node+') <- S_first.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_first), '+node+') = 0',
        'S_first.STORE[pforeachbind.OLD] = DEFINED ('+payload+')',
        '$foreach_released_cell(S_first, pforeachbind.OLD)',
        '$foreach_released_container_cell(S_first, pforeachbind.OLD)',
        '$node_children(S_first, HCELL pforeachbind.OLD) = eps',
        'S_first.STORE[pforeachbind.NEW] = DEFINED (PINT 2)',
        '$heap_owners($heap_graph(S_first), HCELL pforeachbind.NEW) = 2',
        '$foreach_bind_scope(S_first, pforeachbind, S_first.FRAMES) = (S_caller)',
        '$lookup(S_caller.ENV, pforeachbind.NAME) = (pforeachbind.OLD)',
        '$foreach_bind_body_valid(S_caller, pforeachbind)',
        '$foreach_bind_address_valid(S_caller, pforeachbind)',
        '~$foreach_bind_payload_kind(S_caller, '+('POBJECT (|S_caller.OBJECTS|)' if descendants else 'PARRAY (|S_caller.ARRAYS|)')+')']
    if descendants:
        clauses += ['~(n_previous <- S_first.DESTRUCTION.CALLED)',
            'S_live = S_caller[.ALLOCATIONS = (HOBJECT n_previous) :: S_caller.ALLOCATIONS]',
            '$foreach_released_cell(S_live, pforeachbind.OLD)',
            '~$foreach_released_container_cell(S_live, pforeachbind.OLD)',
            'S_live_read = $read_name(S_live, pforeachbind.NAME, pforeachbind.LINE)',
            'S_live_read.COMPLETION = NORMAL',
            'S_live_read.RESULT = KNOWN (POBJECT n_previous)']
    for label, expression in [
            ('read', '$read_name(S_caller, pforeachbind.NAME, pforeachbind.LINE)'),
            ('global_read', '$global_read_name(S_first, pforeachbind.NAME, pforeachbind.LINE)'),
            ('quiet', '$quiet_name(S_caller, pforeachbind.NAME)'),
            ('global_quiet', '$global_quiet_name(S_first, pforeachbind.NAME)'),
            ('location', '$location_name(S_caller, pforeachbind.NAME)'),
            ('find', '$find_name(S_caller, pforeachbind.NAME, pforeachbind.LINE, false)'),
            ('snapshot', '$globals_snapshot(S_first)')]:
        clauses += [f'S_guard_{label} = '+expression,
            f'S_guard_{label}.COMPLETION = UNSUPPORTED "released foreach container payload read"',
            f'S_guard_{label}.STORE = S_first.STORE /\\ S_guard_{label}.ALLOCATIONS = S_first.ALLOCATIONS']
    clauses += [*seek('S_first', 'S_second', phase_second),
        'S_second.CURRENT = (pcallcontext_second)',
        '$destructor_context_call(pcallcontext_second, S_second.CURRENT, S_second.FRAMES) = (pdestructorcall_second)',
        'pdestructorcall_second.OBJECT = n_second',
        'pdestructorcall_second.OPERATION = (pdestructionoperation_second)',
        'pdestructionoperation_second.SOURCE = FOREACH_BIND_RELEASE pforeachbind',
        '~((HOBJECT n_first) <- S_second.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_second), HOBJECT n_first) = 0',
        '$heap_owners($heap_graph(S_second), HOBJECT n_second) = 2',
        'S_second.STORE[pforeachbind.OLD] = DEFINED ('+payload+')',
        '$node_children(S_second, HCELL pforeachbind.OLD) = eps',
        'S_second.STORE[pforeachbind.NEW] = DEFINED (PINT 2)',
        '$heap_owners($heap_graph(S_second), HCELL pforeachbind.NEW) = '+('1' if pending else '2')]
    if pending:
        clauses += ['pdestructorcall_second.PENDING = (n_pending)',
            'pdestructionoperation_second.PENDING = (n_pending)',
            '$throwable_live(S_second, n_pending)',
            '$heap_owners($heap_graph(S_second), HOBJECT n_pending) = 1',
            '$objectprops_at(S_second.OBJECTPROPS, pforeachbind.OBJECT) = (ppropertyslot_second*)',
            '$property_slot_at(ppropertyslot_second*, $ptascii("x")) = (ppropertyslot_unset)',
            'ppropertyslot_unset.STATE = PROP_UNSET']
    else:
        clauses += ['pdestructorcall_second.PENDING = eps',
                    'pdestructionoperation_second.PENDING = eps']
    clauses += [*seek('S_second', 'S_finish', 6),
        'S_finish.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (FOREACH_BIND_COMMIT pforeachbind) :: ptask_finish_tail*',
        'pdestructionoperation.SOURCE = FOREACH_BIND_RELEASE pforeachbind',
        '$foreach_bind_operation_source_valid(S_finish, pdestructionoperation, pforeachbind)',
        '$eager_operation_source_valid(S_finish, pdestructionoperation)',
        'S_finish.STORE[pforeachbind.OLD] = DEFINED ('+payload+')',
        '$node_children(S_finish, HCELL pforeachbind.OLD) = eps',
        '~((HOBJECT n_second) <- S_finish.ALLOCATIONS)',
        '$dupref_output(S_finish.EVENTS) = $ptascii('+json.dumps(markers)+')',
        'S_finish.STORE[pforeachbind.NEW] = DEFINED (PINT '+final_value+')',
        '$heap_owners($heap_graph(S_finish), HCELL pforeachbind.NEW) = '+('1' if pending else '2'),
        'pdestructionoperation.PENDING = '+('('+final_pending+')' if pending else 'eps')]
    if pending and descendants:
        clauses += ['n_final =/= n_pending',
            '$throwable_previous_id(S_finish, n_final) = (n_pending)',
            '$heap_owners($heap_graph(S_finish), HOBJECT n_final) = 1',
            '$heap_owners($heap_graph(S_finish), HOBJECT n_pending) = 1']
    clauses += ['S_one_found = $drive_steps(S_finish, 1)',
        'S_one_found.COMPLETION = BUDGET', 'S_one = S_one_found[.COMPLETION = NORMAL]',
        *valid('S_one'),
        '$lookup(S_one.ENV, pforeachbind.NAME) = (pforeachbind.NEW)',
        'S_one.STORE[pforeachbind.OLD] = UNDEFINED',
        '~$foreach_released_cell(S_one, pforeachbind.OLD)',
        'S_one.STORE[pforeachbind.NEW] = DEFINED (PINT '+final_value+')',
        '$heap_owners($heap_graph(S_one), HCELL pforeachbind.NEW) = '+('1' if pending else '2'),
        'S_one.DESTRUCTION.OPERATIONS = eps']
    if pending:
        clauses += ['S_one.TODO = (THROW_SEARCH '+final_pending+') :: ptask_finish_tail*',
            '$heap_owners($heap_graph(S_one), HOBJECT '+final_pending+') = 1']
    else:
        clauses += ['S_one.TODO = ptask_finish_tail*']
    return clauses+['S_done = $drive(S_one, 2048)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        'S_done.ITERATORS = eps', 'S_done.DESTRUCTION.OPERATIONS = eps',
        '$dupref_output(S_done.EVENTS) = $ptascii('+json.dumps(expected)+')', *valid('S_done')]


def descendant_guard_assertions(initial):
    return ['S_initial = '+initial, '~S_initial.COMPILESTOP',
        *seek('S_initial', 'S_release', 16),
        'S_release.TODO = (FOREACH_BIND_RELEASE pforeachbind) :: ptask_release_tail*',
        'pforeachbind.VALUE = POBJECT n_previous',
        'S_release.PROPREFS = eps',
        'S_bound = $scope_bind_name(S_release[.CELL = pforeachbind.NEW], eps, pforeachbind.NAME, pforeachbind.LINE)',
        'S_bound.COMPLETION = NORMAL',
        'pnode_retired* = $destruction_release_walk($heap_graph(S_bound), $destruction_values([HCELL pforeachbind.OLD]), eps)',
        '(HOBJECT n_previous) <- pnode_retired*',
        '~$foreach_bind_retired_types(S_release.PROPREFS, pnode_retired*)',
        '$foreach_bind_children(S_release, pforeachbind.NAME, pforeachbind.NEW, pforeachbind.LINE, HOBJECT n_previous)',
        '$foreach_bind_capture(S_release, pforeachbind.NAME, pforeachbind.NEW, pforeachbind.LINE) = (pforeachbind)']


def typed_slot_assertions(initial, expected):
    return ['S_initial = '+initial, '~S_initial.COMPILESTOP',
        *seek('S_initial', 'S_release', 16),
        'S_release.TODO = (FOREACH_BIND_RELEASE pforeachbind) :: ptask_release_tail*',
        'pforeachbind.VALUE = POBJECT n_previous',
        'S_release.PROPREFS = [{CELL n_cell, SOURCES ([pproptypesource_second, pproptypesource_first])}]',
        'pproptypesource_first = OBJECT_PROP_SOURCE n_previous $ptascii("first") ppropertyid_first',
        'pproptypesource_second = OBJECT_PROP_SOURCE n_previous $ptascii("second") ppropertyid_second',
        'pproptypesource_first =/= pproptypesource_second',
        '$heap_owners($heap_graph(S_release), HCELL n_cell) = 3',
        '$foreach_bind_capture(S_release, pforeachbind.NAME, pforeachbind.NEW, pforeachbind.LINE) = (pforeachbind)',
        *seek('S_release', 'S_child', 21),
        'S_child.CURRENT = (pcallcontext)',
        '$destructor_context_call(pcallcontext, S_child.CURRENT, S_child.FRAMES) = (pdestructorcall)',
        'pdestructorcall.RELEASE = (pdestructionrelease_saved)',
        'pdestructorcall.OPERATION = (pdestructionoperation)',
        'pdestructionoperation.SOURCE = FOREACH_BIND_RELEASE pforeachbind',
        'S_child.DESTRUCTION.RELEASES = pdestructionrelease :: pdestructionrelease_tail*',
        'pdestructionrelease.JOBS = (DESTRUCTION_PROP_SOURCE pproptypesource_first n_cell) :: pdestructionjob_tail*',
        '(DESTRUCTION_PROP_SOURCE pproptypesource_second n_cell) <- pdestructionjob_tail*',
        '(DESTRUCTION_HANDLE n_previous) <- pdestructionjob_tail*',
        '(DESTRUCTION_PROP_SOURCE pproptypesource_first n_cell) <- pdestructionrelease_saved.JOBS',
        '$property_release_owners(pdestructionrelease, S_child.TODO, S_child.FRAMES) = 1',
        '$gc_release_metadata_valid(S_child, pdestructionrelease)',
        '$destructor_jobs_valid(S_child, pdestructionrelease.JOBS)',
        '$propref_source_valid(S_child, n_cell, pproptypesource_first)',
        '$propref_source_valid(S_child, n_cell, pproptypesource_second)',
        '$heap_owners($heap_graph(S_child), HCELL n_cell) = 3',
        '~((HOBJECT n_previous) <- S_child.ALLOCATIONS)',
        'S_child.STORE[pforeachbind.OLD] = DEFINED (POBJECT n_previous)',
        '$node_children(S_child, HCELL pforeachbind.OLD) = eps',
        'S_stale = S_child[.DESTRUCTION.RELEASES = eps]',
        'S_stale.DESTRUCTION.CALLS = S_child.DESTRUCTION.CALLS',
        '~$propref_source_queued(S_stale, n_cell, pproptypesource_first)',
        '~$proprefs_valid(S_stale)',
        'S_duplicate = S_child[.DESTRUCTION.RELEASES = pdestructionrelease :: S_child.DESTRUCTION.RELEASES]',
        '~$propref_source_queued(S_duplicate, n_cell, pproptypesource_first)',
        '~$destructor_jobs_valid(S_duplicate, pdestructionrelease.JOBS)',
        'S_owner_duplicate = S_child[.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: S_child.TODO]',
        '$property_release_owners(pdestructionrelease, S_owner_duplicate.TODO, S_owner_duplicate.FRAMES) = 2',
        '~$propref_source_queued(S_owner_duplicate, n_cell, pproptypesource_first)',
        '~$destructor_jobs_valid(S_owner_duplicate, pdestructionrelease.JOBS)',
        '~$destructor_jobs_valid(S_child, (DESTRUCTION_PROP_SOURCE pproptypesource_first n_cell) :: pdestructionrelease.JOBS)',
        '~$destructor_jobs_valid(S_child, [DESTRUCTION_PROP_SOURCE pproptypesource_first n_cell])',
        '~$destructor_jobs_valid(S_child, (DESTRUCTION_PROP_SOURCE (CLASS_PROP_SOURCE ppropertyid_first) n_cell) :: pdestructionjob_tail*)',
        '~$destructor_jobs_valid(S_child, (DESTRUCTION_PROP_SOURCE pproptypesource_first (|S_child.STORE|)) :: pdestructionjob_tail*)',
        'n_handle = S_child.DESTRUCTION.HANDLES[n_previous]',
        'S_free = S_child[.DESTRUCTION.FREE = n_handle :: S_child.DESTRUCTION.FREE]',
        '~$property_retired_source_valid(S_free, n_cell, pproptypesource_first)',
        '~$propref_source_queued(S_free, n_cell, pproptypesource_first)',
        *seek('S_child', 'S_first', 22),
        'S_first.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_first) :: ptask_first_tail*',
        'pdestructionrelease_first.JOBS = (DESTRUCTION_PROP_SOURCE pproptypesource_first n_cell) :: pdestructionjob_first_tail*',
        'S_first.DESTRUCTION.OPERATIONS = pdestructionoperation_first :: pdestructionoperation_tail*',
        'pdestructionoperation_first.PENDING = (n_pending)',
        '$throwable_live(S_first, n_pending)',
        'S_two_todo = S_first[.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_first) :: S_first.TODO]',
        '~$propref_source_queued(S_two_todo, n_cell, pproptypesource_first)',
        'S_zero = $drive_steps(S_first, 0)',
        'S_zero.COMPLETION = BUDGET',
        'S_zero.TODO = S_first.TODO /\\ S_zero.PROPREFS = S_first.PROPREFS',
        'S_one_found = $drive_steps(S_first, 1)',
        'S_one_found.COMPLETION = BUDGET',
        'S_one = S_one_found[.COMPLETION = NORMAL]', *valid('S_one'),
        'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_one) :: ptask_first_tail*',
        'pdestructionrelease_one.JOBS = (DESTRUCTION_VALUE (HCELL n_cell)) :: pdestructionjob_first_tail*',
        'S_one.PROPREFS = [{CELL n_cell, SOURCES ([pproptypesource_second])}]',
        '~$propref_source_valid(S_one, n_cell, pproptypesource_first)',
        '$propref_source_valid(S_one, n_cell, pproptypesource_second)',
        '$heap_owners($heap_graph(S_one), HCELL n_cell) = 3',
        'S_value_found = $drive_steps(S_one, 1)',
        'S_value_found.COMPLETION = BUDGET',
        'S_value = S_value_found[.COMPLETION = NORMAL]', *valid('S_value'),
        '$heap_owners($heap_graph(S_value), HCELL n_cell) = 2',
        *seek('S_value', 'S_second_child', 27),
        'S_second_child.CURRENT = (pcallcontext_second)',
        '$destructor_context_call(pcallcontext_second, S_second_child.CURRENT, S_second_child.FRAMES) = (pdestructorcall_second)',
        'pdestructorcall_second.PENDING = (n_pending)',
        'S_second_child.PROPREFS = [{CELL n_cell, SOURCES ([pproptypesource_second])}]',
        '$propref_source_valid(S_second_child, n_cell, pproptypesource_second)',
        'S_second_child.STORE[n_cell] = DEFINED (PINT 7)',
        *seek('S_second_child', 'S_second', 22),
        'S_second.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_second) :: ptask_second_tail*',
        'pdestructionrelease_second.JOBS = (DESTRUCTION_PROP_SOURCE pproptypesource_second n_cell) :: pdestructionjob_second_tail*',
        'S_second.DESTRUCTION.OPERATIONS = pdestructionoperation_second :: pdestructionoperation_tail*',
        'pdestructionoperation_second.PENDING = (n_final)',
        'n_final =/= n_pending',
        '$throwable_previous_id(S_second, n_final) = (n_pending)',
        'S_detached_found = $drive_steps(S_second, 1)',
        'S_detached_found.COMPLETION = BUDGET',
        'S_detached = S_detached_found[.COMPLETION = NORMAL]', *valid('S_detached'),
        'S_detached.PROPREFS = eps',
        '$heap_owners($heap_graph(S_detached), HCELL n_cell) = 2',
        '~$propref_source_valid(S_detached, n_cell, pproptypesource_second)',
        'S_forged = S_detached[.PROPREFS = S_second.PROPREFS]',
        '~$proprefs_valid(S_forged)',
        *seek('S_detached', 'S_finish', 6),
        'S_finish.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_finish) :: (FOREACH_BIND_COMMIT pforeachbind) :: ptask_finish_tail*',
        'pdestructionoperation_finish.PENDING = (n_final)',
        'S_finish.PROPREFS = eps',
        '$heap_owners($heap_graph(S_finish), HCELL n_cell) = 1',
        'S_bound_found = $drive_steps(S_finish, 1)',
        'S_bound_found.COMPLETION = BUDGET',
        'S_bound = S_bound_found[.COMPLETION = NORMAL]', *valid('S_bound'),
        '$lookup(S_bound.ENV, pforeachbind.NAME) = (pforeachbind.NEW)',
        'S_bound.STORE[pforeachbind.NEW] = DEFINED (PINT 2)',
        'S_bound.TODO = (THROW_SEARCH n_final) :: ptask_finish_tail*',
        'S_done = $drive(S_bound, 2048)',
        'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.FRAMES = eps',
        '$dupref_output(S_done.EVENTS) = $ptascii('+json.dumps(expected)+')', *valid('S_done')]


def typed_slot_fiber_assertions(initial, expected):
    return ['S_initial = '+initial, '~S_initial.COMPILESTOP',
        *seek('S_initial', 'S_parked', 24),
        '$lookup(S_parked.ENV, $ptascii("fiber")) = (n_cv)',
        'S_parked.STORE[n_cv] = DEFINED (POBJECT n_fiber)',
        '$fiber_at(S_parked, n_fiber) = (pfiber)',
        'pfiber.STATUS = FIBER_SUSPENDED /\\ pfiber.VM = (pfibervm)',
        'S_parked.DESTRUCTION.RELEASES = eps',
        'pfibervm.DESTRUCTORRELEASES = pdestructionrelease :: pdestructionrelease_tail*',
        'pdestructionrelease.JOBS = (DESTRUCTION_PROP_SOURCE pproptypesource n_cell) :: pdestructionjob_tail*',
        'pproptypesource = OBJECT_PROP_SOURCE n_previous $ptascii("number") ppropertyid',
        '(DESTRUCTION_HANDLE n_previous) <- pdestructionjob_tail*',
        '$property_release_owners(pdestructionrelease, pfibervm.TODO, pfibervm.FRAMES) = 1',
        '$propref_source_valid(S_parked, n_cell, pproptypesource)',
        '$propref_source_queued(S_parked, n_cell, pproptypesource)',
        '~((HOBJECT n_previous) <- S_parked.ALLOCATIONS)',
        'S_vm = $fiber_vm_restore(S_parked, pfibervm)[.ACTIVEFIBER = (n_fiber)]',
        '$property_source_queues($property_release_queues(S_vm), n_cell, pproptypesource) = 1',
        '$propref_source_valid(S_vm, n_cell, pproptypesource)',
        '$heap_valid($heap_graph(S_vm))',
        'pfibervm_bad = pfibervm[.DESTRUCTORRELEASES = eps]',
        'S_stale = $fiber_put(S_parked, n_fiber, pfiber[.VM = (pfibervm_bad)])',
        'pfibervm_bad.DESTRUCTORCALLS = pfibervm.DESTRUCTORCALLS',
        '~$propref_source_valid(S_stale, n_cell, pproptypesource)',
        '~$proprefs_valid(S_stale)',
        'pfibervm_duplicate = pfibervm[.DESTRUCTORRELEASES = pdestructionrelease :: pfibervm.DESTRUCTORRELEASES]',
        'S_duplicate = $fiber_put(S_parked, n_fiber, pfiber[.VM = (pfibervm_duplicate)])',
        '~$propref_source_queued(S_duplicate, n_cell, pproptypesource)',
        'S_two_vms = S_parked[.OBJECTS = S_parked.OBJECTS ++ [FIBER pfiber]][.ALLOCATIONS = S_parked.ALLOCATIONS ++ [HOBJECT (|S_parked.OBJECTS|)]]',
        '$property_source_queues($property_release_queues(S_two_vms), n_cell, pproptypesource) = 2',
        '~$propref_source_queued(S_two_vms, n_cell, pproptypesource)',
        'S_zero = $drive_steps(S_parked, 0)',
        'S_zero.COMPLETION = BUDGET /\\ S_zero.OBJECTS = S_parked.OBJECTS /\\ S_zero.PROPREFS = S_parked.PROPREFS',
        *seek('S_parked', 'S_slot', 22),
        'S_slot.ACTIVEFIBER = (n_fiber)',
        '$dupref_output(S_slot.EVENTS) = $ptascii("A|type|back|")',
        'S_slot.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_slot) :: ptask_slot_tail*',
        'pdestructionrelease_slot.JOBS = (DESTRUCTION_PROP_SOURCE pproptypesource n_cell) :: pdestructionjob_slot_tail*',
        '$propref_source_valid(S_slot, n_cell, pproptypesource)',
        'S_one_found = $drive_steps(S_slot, 1)',
        'S_one_found.COMPLETION = BUDGET',
        'S_one = S_one_found[.COMPLETION = NORMAL]', *valid('S_one'),
        'S_one.PROPREFS = eps',
        'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_one) :: ptask_slot_tail*',
        'pdestructionrelease_one.JOBS = (DESTRUCTION_VALUE (HCELL n_cell)) :: pdestructionjob_slot_tail*',
        '~$propref_source_valid(S_one, n_cell, pproptypesource)',
        '$heap_owners($heap_graph(S_one), HCELL n_cell) = $heap_owners($heap_graph(S_slot), HCELL n_cell)',
        'S_done = $drive(S_one, 2048)',
        'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.ACTIVEFIBER = eps',
        'S_done.PROPREFS = eps',
        '$dupref_output(S_done.EVENTS) = $ptascii('+json.dumps(expected)+')', *valid('S_done')]


def prepare(directory, group):
    source = directory/'source.php'
    case = CASES[group]
    original = sources.CASES[case]
    source.write_bytes(original)
    sources.prepare(directory, source)
    initial = '$php_run(program_source,0,'+json.dumps(base64.b64encode(os.fsencode(source)).decode())+')'
    body = (physical_assertions(initial, sources.EXPECTED[case]) if group=='physical' else
            typed_slot_assertions(initial, sources.EXPECTED[case]) if group=='typed-slot' else
            typed_slot_fiber_assertions(initial, sources.EXPECTED[case]) if group=='typed-slot-fiber' else
            container_assertions(initial, sources.EXPECTED[case], group=='container-throw') if group.startswith('container') else
            descendant_guard_assertions(initial) if group=='descendants-guard' else
            container_assertions(initial, sources.EXPECTED[case], group=='descendants-throw', True) if group.startswith('descendants') else
            binding_gc_assertions(initial, sources.EXPECTED[case]) if group=='binding-gc' else
            scalar_warning_assertions(initial, sources.EXPECTED[case]) if group=='scalar-warning' else
            notice_owner_assertions(initial) if group=='notice-owner' else
            receiver_cleanup_assertions(initial, sources.EXPECTED[case]) if group=='receiver-cleanup' else
            binding_assertions(initial, sources.EXPECTED[case], group=='pending-binding'))
    clauses = ['program_source = '+(directory/'program.watsup').read_text().strip(), *body]
    fixture = directory/'protocol.watsup'
    fixture.write_text(PREFIX+'dec $body() : bool\ndef $body() = true\n'+
                      ''.join('  -- if '+clause+'\n' for clause in clauses)+
                      '\ndec $main() : bool\ndef $main() = $body()\n')
    (directory/'assertions.json').write_text(json.dumps(clauses, indent=2)+'\n')
    assert source.read_bytes() == original
    return source, original, fixture, clauses


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group', choices=list(CASES), required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    before = cross.snapshot(None)
    out = Path(tempfile.mkdtemp(prefix='duplicate-property-reference-', dir=ROOT/'.tools'))
    report = {'before':before, 'profile':cross.invoke.types.PROFILE, 'passed':False,
              'native_evaluations':0, 'model_evaluations':0, 'state_assertions_evaluated':0,
              'runner_mode':'SL', 'numeric_cap_seconds':120, 'case':CASES[args.group], 'jobs':1}
    print(out, flush=True)
    try:
        source, original, fixture, clauses = prepare(out, args.group)
        report.update(source_sha256=cross.invoke.sha(source), fixture_sha256=cross.invoke.sha(fixture),
                      assertions=len(clauses))
        if not args.prepare_only:
            modules = json.loads((ROOT/'spec/semantics/modules.json').read_text())
            result = cross.invoke.process([str(ROOT/'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
                *[str(ROOT/module) for module in modules], str(fixture)], out/'numeric', 120, ROOT)
            assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
            report['state_assertions_evaluated'] = len(clauses)
        assert source.read_bytes() == original and cross.snapshot(None) == before
        report['passed'] = True
    except BaseException as error:
        report['failure'] = {'type':type(error).__name__, 'message':str(error)}
        raise
    finally:
        report['after'] = cross.snapshot(None)
        (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
        print(out/'report.json', report['passed'], flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()
