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
    'notice-owner':'reference-foreach-invalid-key-unset-receiver18',
    'scalar-warning':'reference-foreach-scalar-handler-retirement18',
}
PREFIX = r'''
dec $dupref_is_output(pevent) : bool
dec $dupref_output(pevent*) : ptbytes
def $dupref_output(eps) = eps
def $dupref_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $dupref_output(pevent*)
def $dupref_output(pevent :: pevent_tail*) = $dupref_output(pevent_tail*) -- if ~$dupref_is_output(pevent)
def $dupref_is_output(OUTPUT ptbytes) = true
def $dupref_is_output(pevent) = false -- otherwise
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


def prepare(directory, group):
    source = directory/'source.php'
    case = CASES[group]
    original = sources.CASES[case]
    source.write_bytes(original)
    sources.prepare(directory, source)
    initial = '$php_run(program_source,0,'+json.dumps(base64.b64encode(os.fsencode(source)).decode())+')'
    body = (physical_assertions(initial, sources.EXPECTED[case]) if group=='physical' else
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
