#!/usr/bin/env python3
"""Owned factory-result receiver and getter RV detachment before FREE_OP1."""
import argparse
import base64
import json
import os
from pathlib import Path
import tempfile

import dynamic_property_warning_sources as sources
import magic_property_get_protocol as get

cross, ROOT = sources.cross, sources.ROOT
CASES = {
    'reference': 'review-property-magic-owned-reference28',
    'readonly': 'review-property-magic-owned-readonly28',
    'initial-reject': 'review-property-magic-owned-initial-reject28',
    'getter-throw': 'review-property-magic-owned-throw28',
    'returned-throw': 'review-property-magic-owned-returned-throw28',
    'discarded': 'review-property-magic-owned-discarded28',
    'value': 'review-property-magic-owned-value28',
}
PREFIX = get.PREFIX.split('dec $get_test_copy', 1)[0] + r'''
dec $owned_test_message(pstate, nat, ptbytes) : bool
def $owned_test_message(S, n, ptbytes) = ($string_bytes($throwable_field(S, n, "message")) = (ptbytes))
dec $owned_test_reader(pstate, nat) : pdestructorcall?
def $owned_test_reader(S, n) = (pdestructorcall)
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OBJECT = n /\ pdestructorcall.OPERATION =/= eps
def $owned_test_reader(S, n) = eps -- otherwise
dec $owned_test_phase(pstate, nat, nat) : bool
def $owned_test_phase(S, 0, n) = ($property_get_plan(S) =/= eps)
def $owned_test_phase(S, 1, n) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = PROPERTY_GET_TARGET n porigin
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (PROPERTY_GET_RESULT ppropertyget) :: (PROPERTY_GET_BASE ppropertyget) :: ptask_tail*
  -- if S.DESTRUCTION.OPERATIONS = eps
def $owned_test_phase(S, 2, n) = true
  -- if S.TODO = (PROPERTY_GET_RESULT ppropertyget) :: (PROPERTY_GET_BASE ppropertyget) :: ptask_tail*
  -- if ppropertyget.OBJECT = n
def $owned_test_phase(S, 3, n) = true
  -- if S.TODO = (PROPERTY_GET_COPY ppropertyget poperand) :: (PROPERTY_GET_BASE ppropertyget) :: ptask_tail*
  -- if ppropertyget.OBJECT = n /\ S.DESTRUCTION.OPERATIONS = eps
def $owned_test_phase(S, 4, n) = true
  -- if S.TODO = (PROPERTY_GET_BASE ppropertyget) :: ptask_tail*
  -- if ppropertyget.OBJECT = n /\ S.DESTRUCTION.OPERATIONS = eps
  -- if S.RESULT = KNOWN pvalue
def $owned_test_phase(S, 5, n) = ($owned_test_reader(S, n) =/= eps)
def $owned_test_phase(S, 6, n) = true
  -- if $owned_test_reader(S, n) = (pdestructorcall)
  -- if pdestructorcall.OPERATION = (pdestructionoperation)
  -- if S.DESTRUCTION.OPERATIONS = [pdestructionoperation]
  -- if S_global = $global_table_view(S)
  -- if $lookup(S_global.ENV, $ptascii("returnCell")) = eps
def $owned_test_phase(S, 7, n) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: (PROPERTY_GET_RESULT ppropertyget) :: (PROPERTY_GET_BASE ppropertyget) :: ptask_tail*
  -- if ppropertyget.OBJECT = n
def $owned_test_phase(S, 8, n) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: (PROPERTY_GET_COPY ppropertyget poperand) :: (PROPERTY_GET_BASE ppropertyget) :: ptask_tail*
  -- if ppropertyget.OBJECT = n /\ S.DESTRUCTION.OPERATIONS = eps
def $owned_test_phase(S, 9, n) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: (PROPERTY_GET_BASE ppropertyget) :: (PROPERTY_GET_DROP ppropertyget pvalue) :: ptask_tail*
  -- if ppropertyget.OBJECT = n /\ S.DESTRUCTION.OPERATIONS = eps
def $owned_test_phase(S, 10, n) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: (PROPERTY_GET_DROP ppropertyget pvalue) :: ptask_tail*
  -- if ppropertyget.OBJECT = n /\ S.DESTRUCTION.OPERATIONS = eps
def $owned_test_phase(S, 11, n) = true
  -- if S.TODO = (PROPERTY_PREP (NIdentifier (BYTES text) metadata_name) z) :: (DIM_FETCH z) :: ptask_tail*
  -- if S.RESULT = KNOWN (POBJECT n_object)
  -- if $objectprops_at(S.OBJECTPROPS, n_object) = (ppropertyslot_all*)
  -- if $property_slot_at(ppropertyslot_all*, $base64(text)) = (ppropertyslot)
  -- if ppropertyslot.STATE = PROP_INITIAL
def $owned_test_phase(S, 12, n) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: ptask_tail*
  -- if S.CURRENT = eps
  -- if $object_name(S, n_error) = $ptascii("Error")
  -- if S_global = $global_table_view(S)
  -- if $trace_slot(S_global, S_global.ENV, $ptascii("initialWeak")) = POBJECT n_weak
  -- if $weakref_get(S, n_weak) = PNULL
def $owned_test_phase(S, 13, n) = true
  -- if $owned_test_reader(S, n) = (pdestructorcall)
  -- if pdestructorcall.OPERATION = (pdestructionoperation)
  -- if S.DESTRUCTION.OPERATIONS = [pdestructionoperation]
  -- if $lookup(S.ENV, $ptascii("new")) = eps
  -- if S_global = $global_table_view(S)
  -- if $trace_slot(S_global, S_global.ENV, $ptascii("returnCell")) = POBJECT n_new
  -- if $trace_slot(S, S.ENV, $ptascii("newWeak")) = POBJECT n_new_weak
  -- if $weakref_get(S, n_new_weak) = POBJECT n_new
def $owned_test_phase(S, 14, n) = true
  -- if S.TODO = DISCARD :: ptask_tail*
  -- if S.RESULT = KNOWN (POBJECT n_old)
  -- if S.CURRENT = eps
  -- if S.DESTRUCTION.OPERATIONS = eps
def $owned_test_phase(S, 15, n) = (S.DESTRUCTION.OPERATIONS = eps)
def $owned_test_phase(S, 16, n) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OBJECT = n /\ pdestructorcall.PENDING =/= eps
def $owned_test_phase(S, 17, n) = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*
  -- if pdestructionoperation.SOURCE = PROPERTY_GET_BASE ppropertyget
  -- if ppropertyget.OBJECT = n /\ pdestructionoperation.PENDING =/= eps
def $owned_test_phase(S, 18, n) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.DESTRUCTION.OPERATIONS = eps
  -- if $owned_test_message(S, n_error, $ptascii("C"))
def $owned_test_phase(S, 19, n) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.DESTRUCTION.OPERATIONS = eps
  -- if $owned_test_message(S, n_error, $ptascii("B"))
def $owned_test_phase(S, 20, n) = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (PROPERTY_GET_DROP ppropertyget PNULL) :: ptask_tail*
  -- if ppropertyget.OBJECT = n /\ S.CURRENT = eps
  -- if pdestructionoperation.SOURCE = THROW_SEARCH n_source
  -- if pdestructionoperation.PENDING = (n_pending)
def $owned_test_phase(S, n_phase, n) = false -- otherwise
dec $owned_test_seek(pstate, nat, nat, nat) : pstate
def $owned_test_seek(S, n_phase, n_object, n) = S -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $owned_test_seek(S, n_phase, n_object, n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $owned_test_phase(S, n_phase, n_object)
def $owned_test_seek(S, n_phase, n_object, 0) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$owned_test_phase(S, n_phase, n_object)
def $owned_test_seek(S, n_phase, n_object, n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$owned_test_phase(S, n_phase, n_object)
  -- if $(n > 0) /\ S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps
def $owned_test_seek(S, n_phase, n_object, n) = $owned_test_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_phase, n_object, $nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$owned_test_phase(S, n_phase, n_object)
  -- if $(n > 0)
  -- if S.TODO =/= eps \/ S.CURRENT =/= eps \/ S.FRAMES =/= eps
'''


def seek(parent, state, phase, object_id='n_reader'):
    return [f'{state}_found = $owned_test_seek({parent}, {phase}, {object_id}, 2048)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = {state}_found[.COMPLETION = NORMAL]',
        f'$owned_test_phase({state}, {phase}, {object_id})', *get.valid(state)]


def start(source, weak='readerWeak', parent='S_initial'):
    line = next(i for i, row in enumerate(source.splitlines(), 1)
        if b'$result = owned_' in row or row.strip() == b'owned_discard_factory28()->missing;')
    return [*seek(parent, 'S_before', 0, '0'),
        '$property_get_plan(S_before) = (ppropertyget)', 'n_reader = ppropertyget.OBJECT',
        f'ppropertyget.LINE = {line}', '$property_get_owned_source(S_before, ppropertyget)',
        '$property_get_history(S_before, ppropertyget)', 'S_before.RESULT = KNOWN (POBJECT n_reader)',
        '$lookup(S_before.ENV, $ptascii("reader")) = eps',
        f'$trace_slot(S_before, S_before.ENV, $ptascii("{weak}")) = POBJECT n_reader_weak',
        '$weakref_get(S_before, n_reader_weak) = POBJECT n_reader',
        '$heap_owners($heap_graph(S_before), HOBJECT n_reader) = 1',
        '$property_get_base_count(S_before.TODO, n_reader, ppropertyget.SITE) = 0',
        *get.step('S_before', 'S_pending'),
        'S_pending.TODO = ptask_call :: (PROPERTY_GET_RESULT ppropertyget) :: (PROPERTY_GET_BASE ppropertyget) :: ptask_read_tail*',
        'pcalltarget_get = PROPERTY_GET_TARGET n_reader ppropertyget.METHOD',
        'ptask_call = CALL_ARGS pcalltarget_get eps 1 ([KNOWN (PSTRING ppropertyget.NAME)]) (ppropertyget.SITE) ppropertyget.LINE',
        '$property_get_pending_call(S_pending, pcalltarget_get, ppropertyget.SITE)',
        '$call_task_valid(S_pending, ptask_call)', '$property_get_tail_valid(S_pending, ppropertyget)',
        '$task_nodes(PROPERTY_GET_RESULT ppropertyget) = [HOBJECT n_reader]',
        '$task_nodes(PROPERTY_GET_BASE ppropertyget) = [HOBJECT n_reader]',
        '$heap_owners($heap_graph(S_pending), HOBJECT n_reader) = 2',
        '$target_nodes(pcalltarget_get) = eps', '$target_instance(pcalltarget_get) = eps']


def getter():
    return [*seek('S_pending', 'S_getter', 1), 'S_getter.CURRENT = (pcallcontext_get)',
        'pcallcontext_get.TARGET = pcalltarget_get', 'S_getter.FRAMES = pframe_get :: pframe_get_tail*',
        'pframe_get.TODO = (PROPERTY_GET_RESULT ppropertyget) :: (PROPERTY_GET_BASE ppropertyget) :: ptask_get_tail*',
        '$property_get_frame(S_getter, pcallcontext_get, pframe_get)',
        '$property_get_context(S_getter, pcallcontext_get)', '$call_receiver_roots(pcallcontext_get) = eps',
        '$heap_owners($heap_graph(S_getter), HOBJECT n_reader) = 2',
        '$reference_callback_used(S_getter, pcallcontext_get) = (true)', '$reference_return_used(S_getter)',
        '$property_get_guard_frames(S_getter.FRAMES, n_reader, ppropertyget.NAME)']


def returned(reference=True):
    clauses = [*seek('S_getter', 'S_return', 2),
        'S_return.TODO = (PROPERTY_GET_RESULT ppropertyget) :: (PROPERTY_GET_BASE ppropertyget) :: ptask_return_tail*',
        '$heap_owners($heap_graph(S_return), HOBJECT n_reader) = 2',
        'S_return_global = $global_table_view(S_return)',
        '$lookup(S_return_global.ENV, $ptascii("returnCell")) = (n_return_cell)',
        '$property_get_valid(S_return, ppropertyget, true)', '$property_get_tail_valid(S_return, ppropertyget)']
    if reference:
        clauses += ['S_return.RESULT = REFERENCE n_return_cell',
            '$heap_owners($heap_graph(S_return), HCELL n_return_cell) = 2',
            '$task_nodes(PROPERTY_GET_COPY ppropertyget (REFERENCE n_return_cell)) = [HCELL n_return_cell]',
            '$propref_at(S_return.PROPREFS, n_return_cell) = eps',
            '$parameter_backing_at(S_return.PARAMETERBACKINGS, n_return_cell) = eps']
    return clauses


def detach(reference=True, value='POBJECT n_old'):
    clauses = [*seek('S_return', 'S_copy', 3),
        'S_copy.TODO = (PROPERTY_GET_COPY ppropertyget poperand_copy) :: (PROPERTY_GET_BASE ppropertyget) :: ptask_copy_tail*',
        'S_copy.RESULT = KNOWN PNULL', 'S_copy.BASE = BASE_VALUE (KNOWN PNULL)',
        '$heap_owners($heap_graph(S_copy), HOBJECT n_reader) = 1',
        '$property_get_base_count(S_copy.TODO, n_reader, ppropertyget.SITE) = 1',
        '$weakref_get(S_copy, n_reader_weak) = POBJECT n_reader',
        '~$property_get_guard_tasks(S_copy.TODO, n_reader, ppropertyget.NAME)',
        *seek('S_copy', 'S_base', 4),
        'S_base.TODO = (PROPERTY_GET_BASE ppropertyget) :: ptask_base_tail*',
        'ptask_base_tail* = ptask_copy_tail*', f'S_base.RESULT = KNOWN ({value})',
        '$heap_owners($heap_graph(S_base), HOBJECT n_reader) = 1',
        '$property_get_carriers(S_base.TODO, n_reader, ppropertyget.SITE) = 0',
        '$property_get_base_valid(S_base, ppropertyget)', '$call_task_valid(S_base, PROPERTY_GET_BASE ppropertyget)']
    if reference:
        clauses += ['poperand_copy = REFERENCE n_return_cell',
            '$heap_owners($heap_graph(S_base), HCELL n_return_cell) = 1',
            'S_base.STORE[n_return_cell] = DEFINED ('+value+')']
    else:
        clauses += ['poperand_copy = KNOWN ('+value+')', '$task_nodes(PROPERTY_GET_COPY ppropertyget poperand_copy) = $value_nodes('+value+')']
    return clauses


def reader(parent='S_base', pending=None, source='PROPERTY_GET_BASE ppropertyget', value='POBJECT n_old'):
    return [*seek(parent, 'S_reader_dtor', 5),
        '$owned_test_reader(S_reader_dtor, n_reader) = (pdestructorcall_reader)',
        'pdestructorcall_reader.OPERATION = (pdestructionoperation_reader)',
        '$destructor_call_pending_valid(S_reader_dtor, pdestructorcall_reader)',
        'pdestructionoperation_reader.SOURCE = '+source,
        'pdestructionoperation_reader.PENDING = '+('eps' if pending is None else '('+pending+')'),
        f'pdestructionoperation_reader.VALUE = KNOWN ({value})',
        'S_reader_dtor.RESULT = KNOWN PNULL', 'S_reader_dtor.BASE = BASE_VALUE (KNOWN PNULL)',
        '$weakref_get(S_reader_dtor, n_reader_weak) = POBJECT n_reader',
        '(HOBJECT n_reader) <- S_reader_dtor.ALLOCATIONS', '~$instance_storage_freeing(S_reader_dtor, n_reader)',
        '$eager_operation_source_guard(S_reader_dtor, pdestructionoperation_reader)',
        '~$property_get_guard_frames(S_reader_dtor.FRAMES, n_reader, ppropertyget.NAME)']


def received(parent, value='POBJECT n_old'):
    return [*seek(parent, 'S_received', 15), 'S_received.TODO = ptask_base_tail*',
        f'S_received.RESULT = KNOWN ({value})', '$weakref_get(S_received, n_reader_weak) = PNULL',
        '~((HOBJECT n_reader) <- S_received.ALLOCATIONS)']


def admission():
    clauses = ['S_before.TODO = (PROPERTY_PREP phpType20_name z_get) :: (DIM_FETCH z_get) :: ptask_before_tail*',
        '$origin_node(S_before.SOURCES, ppropertyget.SITE) = (NExprPropertyFetch expression_factory phpType20_name metadata_get)',
        'expression_factory = NExprFuncCall name (SEQUENCE eps) metadata_call',
        'ppropertyget.SITE = PORIGIN n_unit pcpath_get',
        '$code_at(S_before.CODE, n_unit) = (pcode_get)',
        '$code_name(pcode_get.NAMES, pcpath_get ++ [PCFIELD 0]) = ((ptbytes_factory, eps))',
        '$call_target(S_before, ptbytes_factory, eps) = (pfunction_factory)', '~pfunction_factory.SIGNATURE.BYREF',
        '$source_emission_noarg_call(S_before, n_unit, pcpath_get ++ [PCFIELD 0], expression_factory) = (z_factory)',
        # Constructed selected-function mode corruption, not a source image claim.
        'S_ref_factory = S_pending[.FUNCTIONS = pfunction_factory[.SIGNATURE.BYREF = true] :: S_pending.FUNCTIONS]',
        '$call_target(S_ref_factory, ptbytes_factory, eps) = (pfunction_factory[.SIGNATURE.BYREF = true])',
        '$source_emission_noarg_call(S_ref_factory, n_unit, pcpath_get ++ [PCFIELD 0], expression_factory) = (z_factory)',
        '~$property_get_owned_source(S_ref_factory, ppropertyget)',
        '$property_get_plan(S_before[.RESULT = REFERENCE n_return_cell]) = eps',
        '$property_get_plan(S_before[.BASE = BASE_VALUE (KNOWN (POBJECT n_reader))]) = eps',
        '$property_get_plan(S_before[.TODO = S_before.TODO ++ [PROPERTY_GET_BASE ppropertyget]]) = eps',
        'S_missing_base = S_pending[.TODO = ptask_call :: (PROPERTY_GET_RESULT ppropertyget) :: ptask_read_tail*]',
        '~$property_get_tail_valid(S_missing_base, ppropertyget)', '~$call_descriptors_valid(S_missing_base)',
        'S_duplicate_base = S_pending[.TODO = S_pending.TODO ++ [PROPERTY_GET_BASE ppropertyget]]',
        '$property_get_base_count(S_duplicate_base.TODO, n_reader, ppropertyget.SITE) = 2',
        '~$call_descriptors_valid(S_duplicate_base)',
        'S_wrong_pair = S_pending[.TODO = ptask_call :: (PROPERTY_GET_RESULT ppropertyget) :: (PROPERTY_GET_BASE ppropertyget[.NAME = $ptascii("forged28")]) :: ptask_read_tail*]',
        '~$property_get_tail_valid(S_wrong_pair, ppropertyget)', '~$call_descriptors_valid(S_wrong_pair)',
        '~$call_descriptors_valid(S_pending[.TODO = ptask_call :: (PROPERTY_GET_BASE ppropertyget) :: (PROPERTY_GET_RESULT ppropertyget) :: ptask_read_tail*])']
    for field in ('.NAME = $ptascii("forged28")', '.LINE = 999', '.SITE = ppropertyget.METHOD',
                  '.METHOD = ppropertyget.SITE', '.CLASS = ppropertyget.SITE', '.OBJECT = |S_pending.OBJECTS|', '.DECL = (ppropertyget.METHOD)'):
        clauses += [f'~$property_get_history(S_pending, ppropertyget[{field}])',
            f'~$call_task_valid(S_pending, PROPERTY_GET_BASE ppropertyget[{field}])']
    # Preserve the actual original BASE when retargeting to a same-class instance.
    clauses += ['S_second = $destruction_store_new($new_class(S_pending, $object_name(S_pending, n_reader), ppropertyget.LINE))',
        'S_second.RESULT = KNOWN (POBJECT n_second)', 'n_second =/= n_reader',
        'S_second.OBJECTS[n_second] = INSTANCE ppropertyget.CLASS',
        'ppropertyget_second = ppropertyget[.OBJECT = n_second]',
        '$property_get_history(S_second, ppropertyget_second)',
        'S_wrong_instance = S_second[.TODO = (CALL_ARGS (PROPERTY_GET_TARGET n_second ppropertyget.METHOD) eps 1 ([KNOWN (PSTRING ppropertyget.NAME)]) (ppropertyget.SITE) ppropertyget.LINE) :: (PROPERTY_GET_RESULT ppropertyget_second) :: (PROPERTY_GET_BASE ppropertyget) :: ptask_read_tail*]',
        '~$property_get_tail_valid(S_wrong_instance, ppropertyget_second)',
        '~$property_get_pending_call(S_wrong_instance, PROPERTY_GET_TARGET n_second ppropertyget.METHOD, ppropertyget.SITE)',
        '~$call_descriptors_valid(S_wrong_instance)']
    return clauses


def saved_admission():
    clauses = ['S_saved_missing = S_getter[.FRAMES = pframe_get[.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_get_tail*] :: pframe_get_tail*]',
        '~$property_get_frame(S_saved_missing, pcallcontext_get, S_saved_missing.FRAMES[0])',
        '~$call_descriptors_valid(S_saved_missing)',
        'S_saved_duplicate = S_getter[.FRAMES = pframe_get[.TODO = pframe_get.TODO ++ [PROPERTY_GET_BASE ppropertyget]] :: pframe_get_tail*]',
        '~$call_descriptors_valid(S_saved_duplicate)',
        'S_saved_wrong = S_getter[.FRAMES = pframe_get[.TODO = (PROPERTY_GET_RESULT ppropertyget) :: (PROPERTY_GET_BASE ppropertyget[.LINE = 999]) :: ptask_get_tail*] :: pframe_get_tail*]',
        '~$call_descriptors_valid(S_saved_wrong)',
        'pcallcontext_ordinary = pcallcontext_get[.TARGET = METHOD_TARGET n_reader ppropertyget.METHOD]',
        '~$call_descriptors_valid(S_getter[.CURRENT = (pcallcontext_ordinary)])',
        '~$call_descriptors_valid(S_getter[.CURRENT = (pcallcontext_get[.LINE = 999])])']
    return clauses


def shared_receiver():
    return ['S_shared_created = $destruction_store_new($write_name(S_base, $ptascii("keptReader28"), POBJECT n_reader))',
        'S_shared = S_shared_created[.RESULT = S_base.RESULT][.BASE = S_base.BASE]',
        *get.valid('S_shared'), '$heap_owners($heap_graph(S_shared), HOBJECT n_reader) = 2',
        *get.step('S_shared', 'S_shared_step'), *seek('S_shared_step', 'S_shared_done', 15),
        'S_shared_done.TODO = ptask_base_tail*', 'S_shared_done.RESULT = S_base.RESULT',
        '$heap_owners($heap_graph(S_shared_done), HOBJECT n_reader) = 1',
        '$weakref_get(S_shared_done, n_reader_weak) = POBJECT n_reader',
        '$trace_slot(S_shared_done, S_shared_done.ENV, $ptascii("readerDrops")) = PINT 0']


def reference(expected):
    return [*returned(), *admission(), *saved_admission(),
        'S_return.STORE[n_return_cell] = DEFINED (POBJECT n_old)',
        '$trace_slot(S_return_global, S_return_global.ENV, $ptascii("oldWeak")) = POBJECT n_old_weak',
        '$heap_owners($heap_graph(S_return), HOBJECT n_old) = 1',
        '$property_get_verify(S_return, ppropertyget, S_return.RESULT) = S_return',
        *detach(), '$heap_owners($heap_graph(S_base), HOBJECT n_old) = 2', *shared_receiver(),
        *reader(), '$heap_owners($heap_graph(S_reader_dtor), HCELL n_return_cell) = 1',
        *seek('S_reader_dtor', 'S_rebound', 13), 'S_rebound_global = $global_table_view(S_rebound)',
        '$trace_slot(S_rebound_global, S_rebound_global.ENV, $ptascii("returnCell")) = POBJECT n_new',
        'n_new =/= n_old', '$heap_owners($heap_graph(S_rebound), HOBJECT n_new) = 1',
        '$heap_owners($heap_graph(S_rebound), HCELL n_return_cell) = 1',
        '$heap_owners($heap_graph(S_rebound), HOBJECT n_old) = 1',
        '$weakref_get(S_rebound, n_old_weak) = POBJECT n_old',
        '$trace_slot(S_rebound, S_rebound.ENV, $ptascii("newWeak")) = POBJECT n_new_weak',
        *seek('S_rebound', 'S_dropped', 6), '~((HCELL n_return_cell) <- S_dropped.ALLOCATIONS)',
        '~((HOBJECT n_new) <- S_dropped.ALLOCATIONS)', '$weakref_get(S_dropped, n_new_weak) = PNULL',
        '$weakref_get(S_dropped, n_old_weak) = POBJECT n_old',
        '$heap_owners($heap_graph(S_dropped), HOBJECT n_old) = 1',
        *received('S_dropped'), *get.finish('S_received', expected),
        '$weakref_get(S_done, n_old_weak) = PNULL', '$weakref_get(S_done, n_new_weak) = PNULL']


def readonly(expected):
    return [*returned(), 'S_return.STORE[n_return_cell] = DEFINED (PINT 7)',
        'ppropertyget.DECL = (ppropertyid)', '$property_get_verify(S_return, ppropertyget, S_return.RESULT) = S_return',
        *detach(value='PINT 7'), *reader(value='PINT 7'), *received('S_reader_dtor', 'PINT 7'),
        'S_received.STORE[n_return_cell] = DEFINED pvalue_changed',
        '$string_bytes(pvalue_changed) = ($ptascii("changed"))',
        '$propref_at(S_received.PROPREFS, n_return_cell) = eps', *get.finish('S_received', expected)]


def pending_reader(parent, error):
    return [*seek(parent, 'S_pending_copy', 8),
        'S_pending_copy.TODO = (THROW_SEARCH '+error+') :: (PROPERTY_GET_COPY ppropertyget poperand_copy) :: (PROPERTY_GET_BASE ppropertyget) :: ptask_pending_tail*',
        'S_pending_copy.RESULT = KNOWN PNULL', 'S_pending_copy.BASE = BASE_VALUE (KNOWN PNULL)',
        '$heap_owners($heap_graph(S_pending_copy), HOBJECT n_reader) = 1',
        *seek('S_pending_copy', 'S_pending_base', 9),
        'S_pending_base.TODO = (THROW_SEARCH '+error+') :: (PROPERTY_GET_BASE ppropertyget) :: (PROPERTY_GET_DROP ppropertyget pvalue_pending) :: ptask_pending_tail*',
        'S_pending_base.RESULT = KNOWN PNULL', 'S_pending_base.BASE = BASE_VALUE (KNOWN PNULL)',
        '$call_task_valid(S_pending_base, PROPERTY_GET_BASE ppropertyget)',
        '$call_task_valid(S_pending_base, PROPERTY_GET_DROP ppropertyget pvalue_pending)',
        *reader('S_pending_base', error, 'THROW_SEARCH '+error, 'PNULL')]


def getter_throw(expected):
    return [*seek('S_getter', 'S_getter_error', 7),
        'S_getter_error.TODO = (THROW_SEARCH n_getter_error) :: (PROPERTY_GET_RESULT ppropertyget) :: (PROPERTY_GET_BASE ppropertyget) :: ptask_error_tail*',
        '$owned_test_message(S_getter_error, n_getter_error, $ptascii("H"))',
        *pending_reader('S_getter_error', 'n_getter_error'), 'poperand_copy = KNOWN PNULL', 'pvalue_pending = PNULL',
        *seek('S_reader_dtor', 'S_chained_exit', 20),
        'S_chained_exit.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_chained) :: (PROPERTY_GET_DROP ppropertyget PNULL) :: ptask_chained_exit_tail*',
        'pdestructionoperation_chained.SOURCE = THROW_SEARCH n_getter_error',
        'pdestructionoperation_chained.PENDING = (n_reader_error)',
        'S_chained_exit.DESTRUCTION.OPERATIONS = [pdestructionoperation_chained]',
        '$throwable_previous_id(S_chained_exit, n_reader_error) = (n_getter_error)',
        'S_chained_projection = $call_after_origin(S_chained_exit, DESTRUCTOR_OPERATION_EXIT pdestructionoperation_chained)',
        'S_chained_projection.DESTRUCTION.OPERATIONS = eps',
        '$property_get_projected_drop(S_chained_projection, S_chained_projection.TODO, ppropertyget, PNULL)',
        '$call_task_valid(S_chained_projection, PROPERTY_GET_DROP ppropertyget PNULL)',
        '~$call_task_valid(S_chained_projection[.TODO = [PROPERTY_GET_DROP ppropertyget PNULL]], PROPERTY_GET_DROP ppropertyget PNULL)',
        '~$property_get_projected_drop(S_chained_projection[.ALLOCATIONS = $destruction_node_delete(S_chained_projection.ALLOCATIONS, HOBJECT n_getter_error)], S_chained_projection.TODO, ppropertyget, PNULL)',
        '~$property_get_projected_drop(S_chained_projection[.ALLOCATIONS = $destruction_node_delete(S_chained_projection.ALLOCATIONS, HOBJECT n_reader_error)], S_chained_projection.TODO, ppropertyget, PNULL)',
        *seek('S_chained_exit', 'S_chained', 19),
        'S_chained.TODO = (THROW_SEARCH n_reader_error) :: ptask_chained_tail*',
        '$throwable_previous_id(S_chained, n_reader_error) = (n_getter_error)',
        *get.finish('S_chained', expected), '$weakref_get(S_done, n_reader_weak) = PNULL',
        '$lookup(S_done.ENV, $ptascii("result")) = eps']


def returned_throw(expected):
    clauses = [*returned(), 'ppropertyget.DECL = eps',
        'S_return.STORE[n_return_cell] = DEFINED (POBJECT n_old)',
        '$trace_slot(S_return_global, S_return_global.ENV, $ptascii("leafWeak")) = POBJECT n_leaf_weak',
        *detach(), *reader(), *seek('S_reader_dtor', 'S_dropped', 6),
        '~((HCELL n_return_cell) <- S_dropped.ALLOCATIONS)', '$weakref_get(S_dropped, n_leaf_weak) = POBJECT n_old',
        '$heap_owners($heap_graph(S_dropped), HOBJECT n_old) = 1',
        *seek('S_dropped', 'S_reader_pending', 17),
        'S_reader_pending.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_pending) :: ptask_exit_tail*',
        'pdestructionoperation_pending.SOURCE = PROPERTY_GET_BASE ppropertyget',
        'pdestructionoperation_pending.PENDING = (n_reader_error)',
        'pdestructionoperation_pending.VALUE = KNOWN (POBJECT n_old)',
        '$owned_test_message(S_reader_pending, n_reader_error, $ptascii("B"))',
        '$throwable_previous_id(S_reader_pending, n_reader_error) = eps',
        '~((HOBJECT n_reader) <- S_reader_pending.ALLOCATIONS)',
        'S_reader_pending.DESTRUCTION.OPERATIONS = [pdestructionoperation_pending]',
        'S_finish_scope = S_reader_pending[.DESTRUCTION.OPERATIONS = eps]',
        'S_transfer = $destructor_pending_finish(S_finish_scope, pdestructionoperation_pending, n_reader_error, ptask_exit_tail*)',
        'S_transfer.TODO = (THROW_SEARCH n_reader_error) :: (PROPERTY_GET_DROP ppropertyget (POBJECT n_old)) :: ptask_exit_tail*',
        'S_transfer.RESULT = KNOWN PNULL', 'S_transfer.BASE = BASE_VALUE (KNOWN PNULL)',
        '$heap_owners($heap_graph(S_transfer), HOBJECT n_old) = 1',
        *get.step('S_reader_pending', 'S_drop'), 'S_drop = S_transfer',
        '$call_task_valid(S_drop, PROPERTY_GET_DROP ppropertyget (POBJECT n_old))']
    for i, update in enumerate(('.SOURCE = PROPERTY_GET_RESULT ppropertyget', '.PENDING = eps', '.VALUE = REFERENCE n_return_cell')):
        clauses += [f'pdestructionoperation_bad{i} = pdestructionoperation_pending[{update}]',
            f'S_bad_finish{i} = S_finish_scope[.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_bad{i}) :: ptask_exit_tail*]',
            f'S_bad_finished{i} = $destructor_pending_finish(S_bad_finish{i}, pdestructionoperation_bad{i}, n_reader_error, ptask_exit_tail*)',
            f'S_bad_finished{i}.TODO = (THROW_SEARCH n_reader_error) :: ptask_exit_tail*']
    clauses += [
        'S_wrong_tail_finish = $destructor_pending_finish(S_finish_scope, pdestructionoperation_pending, n_reader_error, [DISCARD])',
        'S_wrong_tail_finish.TODO = (THROW_SEARCH n_reader_error) :: [DISCARD]',
        *seek('S_drop', 'S_leaf_dtor', 16, 'n_old'), 'S_leaf_dtor.CURRENT = (pcallcontext_leaf)',
        '$destructor_context_call(pcallcontext_leaf, S_leaf_dtor.CURRENT, S_leaf_dtor.FRAMES) = (pdestructorcall_leaf)',
        'pdestructorcall_leaf.OPERATION = (pdestructionoperation_leaf)',
        'pdestructionoperation_leaf.PENDING = (n_reader_error)',
        'pdestructionoperation_leaf.SOURCE = THROW_SEARCH n_reader_error',
        '$destructor_call_pending_valid(S_leaf_dtor, pdestructorcall_leaf)',
        '$weakref_get(S_leaf_dtor, n_leaf_weak) = POBJECT n_old',
        '(HOBJECT n_old) <- S_leaf_dtor.ALLOCATIONS', '~$instance_storage_freeing(S_leaf_dtor, n_old)',
        *seek('S_leaf_dtor', 'S_chained', 18), 'S_chained.TODO = (THROW_SEARCH n_leaf_error) :: ptask_chained_tail*',
        '$throwable_previous_id(S_chained, n_leaf_error) = (n_reader_error)',
        *get.finish('S_chained', expected), '$weakref_get(S_done, n_leaf_weak) = PNULL',
        '$lookup(S_done.ENV, $ptascii("returnCell")) = eps', '$lookup(S_done.ENV, $ptascii("result")) = eps']
    return clauses


def discarded(expected):
    return [*returned(), 'S_return.STORE[n_return_cell] = DEFINED (POBJECT n_old)',
        '$trace_slot(S_return_global, S_return_global.ENV, $ptascii("leafWeak")) = POBJECT n_leaf_weak',
        '~$reference_call_used(S_getter, ppropertyget.SITE)', *detach(), *reader(),
        *seek('S_reader_dtor', 'S_dropped', 6), '~((HCELL n_return_cell) <- S_dropped.ALLOCATIONS)',
        '$weakref_get(S_dropped, n_leaf_weak) = POBJECT n_old',
        'ptask_base_tail* = (ORIGIN_RETURN porigin_restore?) :: ptask_discard_tail*',
        *seek('S_dropped', 'S_received', 14), 'S_received.TODO = ptask_discard_tail*',
        'S_received.ORIGIN = porigin_restore?',
        '$heap_owners($heap_graph(S_received), HOBJECT n_old) = 1',
        '$weakref_get(S_received, n_reader_weak) = PNULL',
        *get.finish('S_received', expected), '$weakref_get(S_done, n_leaf_weak) = PNULL']


def value(expected):
    return [*returned(False), 'S_return.RESULT = KNOWN (POBJECT n_old)',
        '$trace_slot(S_return_global, S_return_global.ENV, $ptascii("oldWeak")) = POBJECT n_old_weak',
        '$heap_owners($heap_graph(S_return), HOBJECT n_old) = 2',
        *detach(False), *reader(), *received('S_reader_dtor'),
        'S_received.STORE[n_return_cell] = DEFINED (PINT 19)',
        '$heap_owners($heap_graph(S_received), HOBJECT n_old) = 1',
        '$weakref_get(S_received, n_old_weak) = POBJECT n_old',
        *get.finish('S_received', expected), '$weakref_get(S_done, n_old_weak) = PNULL']


def initial_reject(run, source, expected):
    return ['S_initial = '+run, '~S_initial.COMPILESTOP', *seek('S_initial', 'S_initial_read', 11, '0'),
        'S_initial_read.RESULT = KNOWN (POBJECT n_initial_reader)',
        '$property_get_needed(S_initial_read, n_initial_reader, $ptascii("value")) = false',
        '$property_get_plan(S_initial_read) = eps',
        '$trace_slot(S_initial_read, S_initial_read.ENV, $ptascii("initialCalls")) = PINT 0',
        *seek('S_initial_read', 'S_initial_error', 12, '0'),
        '$trace_slot(S_initial_error, S_initial_error.ENV, $ptascii("initialCalls")) = PINT 0',
        '$trace_slot(S_initial_error, S_initial_error.ENV, $ptascii("initialDrops")) = PINT 1',
        *start(source, 'rejectWeak', 'S_initial_error'), *getter(), *returned(),
        'S_return.STORE[n_return_cell] = DEFINED pvalue_bad',
        '$string_bytes(pvalue_bad) = ($ptascii("bad"))',
        'ppropertyget.DECL = (ppropertyid)',
        'S_checked = $property_get_complete(S_return, ppropertyget, S_return.RESULT)',
        'S_checked.TODO = (PROPERTY_GET_COPY ppropertyget (REFERENCE n_return_cell)) :: (PROPERTY_GET_BASE ppropertyget) :: ptask_return_tail*',
        '$throwable_pending(S_checked.COMPLETION)',
        'S_materialized = $throwable_transition(S_return, S_checked)',
        'S_materialized.COMPLETION = THROWING n_type_error',
        'S_materialized.TODO = S_checked.TODO',
        'S_bad_copy = S_checked[.TODO = (PROPERTY_GET_COPY ppropertyget (KNOWN PNULL)) :: (PROPERTY_GET_BASE ppropertyget) :: ptask_return_tail*]',
        'S_bad_continuation = $throwable_same_frame_continuation(S_return, S_bad_copy, (PROPERTY_GET_BASE ppropertyget) :: ptask_return_tail*)',
        'S_bad_continuation.TODO = (PROPERTY_GET_BASE ppropertyget) :: ptask_return_tail*',
        *pending_reader('S_return', 'n_type_error'),
        'poperand_copy = REFERENCE n_return_cell', 'pvalue_pending = pvalue_bad',
        'S_reader_dtor.FRAMES = pframe_cleanup :: pframe_cleanup_tail*',
        'pframe_cleanup.TODO = (DESTRUCTOR_RESULT pdestructorcall_reader) :: ptask_cleanup_tail*',
        'S_cleanup_scope = $constant_frame_scope(S_reader_dtor, pframe_cleanup, pframe_cleanup_tail*)',
        'S_cleanup_saved = $destructor_saved_frame_scope(S_cleanup_scope, pframe_cleanup)',
        'S_cleanup_after_call = $call_after_origin(S_cleanup_saved, DESTRUCTOR_RESULT pdestructorcall_reader)',
        'S_cleanup_after_exit = $call_after_origin(S_cleanup_after_call, DESTRUCTOR_OPERATION_EXIT pdestructionoperation_reader)',
        'S_cleanup_after_exit.DESTRUCTION.OPERATIONS = eps',
        '$property_get_projected_drop(S_cleanup_after_exit, S_cleanup_after_exit.TODO, ppropertyget, pvalue_pending)',
        '$call_task_valid(S_cleanup_after_exit, PROPERTY_GET_DROP ppropertyget pvalue_pending)',
        '~$property_get_projected_drop(S_cleanup_after_call, S_cleanup_after_call.TODO, ppropertyget, pvalue_pending)',
        '~$property_get_projected_drop(S_cleanup_after_exit, S_cleanup_after_exit.TODO, ppropertyget, PINT 99)',
        '~$property_get_projected_drop(S_cleanup_after_exit, S_cleanup_after_exit.TODO, ppropertyget[.LINE = 999], pvalue_pending)',
        '~$property_get_projected_drop(S_cleanup_after_exit, DISCARD :: S_cleanup_after_exit.TODO, ppropertyget, pvalue_pending)',
        '~$property_get_projected_drop(S_cleanup_after_exit, [PROPERTY_GET_DROP ppropertyget pvalue_pending], ppropertyget, pvalue_pending)',
        '~$call_task_valid(S_cleanup_after_exit[.TODO = [PROPERTY_GET_DROP ppropertyget pvalue_pending]], PROPERTY_GET_DROP ppropertyget pvalue_pending)',
        '~$property_get_projected_drop(S_cleanup_after_exit, [(DESTRUCTOR_OPERATION_EXIT pdestructionoperation_reader[.SOURCE = PROPERTY_GET_RESULT ppropertyget]), PROPERTY_GET_DROP ppropertyget pvalue_pending], ppropertyget, pvalue_pending)',
        '~$property_get_projected_drop(S_cleanup_after_exit, [(DESTRUCTOR_OPERATION_EXIT pdestructionoperation_reader[.PENDING = eps]), PROPERTY_GET_DROP ppropertyget pvalue_pending], ppropertyget, pvalue_pending)',
        '~$property_get_projected_drop(S_cleanup_after_exit[.RESULT = KNOWN (PINT 99)], S_cleanup_after_exit.TODO, ppropertyget, pvalue_pending)',
        '~$property_get_projected_drop(S_cleanup_after_exit, [(DESTRUCTOR_OPERATION_EXIT pdestructionoperation_reader[.VALUE = KNOWN (PINT 99)]), PROPERTY_GET_DROP ppropertyget pvalue_pending], ppropertyget, pvalue_pending)',
        '~$property_get_projected_drop(S_cleanup_after_exit[.BASE = BASE_VALUE (KNOWN (POBJECT n_reader))], S_cleanup_after_exit.TODO, ppropertyget, pvalue_pending)',
        '~$property_get_projected_drop(S_cleanup_after_exit[.ORIGIN = eps], S_cleanup_after_exit.TODO, ppropertyget, pvalue_pending)',
        '$object_name(S_reader_dtor, n_type_error) = $ptascii("TypeError")',
        'S_reader_dtor.STORE[n_return_cell] = DEFINED pvalue_bad',
        *get.finish('S_reader_dtor', expected), 'S_done.STORE[n_return_cell] = DEFINED (PINT 7)',
        '$weakref_get(S_done, n_reader_weak) = PNULL', '$lookup(S_done.ENV, $ptascii("result")) = eps']


def body(run, source, expected, group):
    if group == 'initial-reject':
        return initial_reject(run, source, expected)
    clauses = ['S_initial = '+run, '~S_initial.COMPILESTOP', *start(source), *getter()]
    return clauses + globals()[group.replace('-', '_')](expected)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group', choices=list(CASES), required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    before = cross.snapshot(None)
    out = Path(tempfile.mkdtemp(prefix='magic-property-owned-', dir=ROOT/'.tools'))
    report = {'before':before, 'profile':cross.invoke.types.PROFILE, 'passed':False,
        'native_evaluations':0, 'model_evaluations':0, 'state_assertions_evaluated':0,
        'runner_mode':'SL', 'numeric_cap_seconds':120, 'case':CASES[args.group], 'jobs':1}
    print(out, flush=True)
    try:
        original = sources.CASES[CASES[args.group]]
        source = out/'source.php'; source.write_bytes(original)
        sources.prepare(out, source)
        run = '$php_run(program_source,0,'+json.dumps(base64.b64encode(os.fsencode(source)).decode())+')'
        clauses = ['program_source = '+(out/'program.watsup').read_text().strip(),
            *body(run, original, sources.EXPECTED[CASES[args.group]], args.group)]
        fixture = out/'protocol.watsup'
        fixture.write_text(PREFIX+'dec $body() : bool\ndef $body() = true\n'+
            ''.join('  -- if '+clause+'\n' for clause in clauses)+'\ndec $main() : bool\ndef $main() = $body()\n')
        (out/'assertions.json').write_text(json.dumps(clauses, indent=2)+'\n')
        report.update(source_sha256=cross.invoke.sha(source), fixture_sha256=cross.invoke.sha(fixture), assertions=len(clauses))
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
