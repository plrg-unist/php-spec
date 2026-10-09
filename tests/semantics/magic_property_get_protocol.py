#!/usr/bin/env python3
"""Source-reached implicit getter receiver, raw RV and exceptional cleanup."""
import argparse
import base64
import json
import os
from pathlib import Path
import tempfile

import dynamic_property_warning_sources as sources

cross, ROOT = sources.cross, sources.ROOT
CASES = {
    'reference': 'review-property-magic-get-reference-global26',
    'readonly': 'review-property-magic-get-readonly-global26',
    'type-error': 'review-property-magic-get-type-error-global26',
    'initial': 'review-property-magic-get-initial26',
    'value': 'review-property-magic-get-value-global26',
    'getter-throw': 'review-property-magic-get-throw-global26',
    'returned-throw': 'review-property-magic-get-returned-throw-global26',
    'discarded': 'review-property-magic-get-discarded26',
}
PREFIX = r'''
dec $get_test_output(pevent*) : ptbytes
dec $get_test_is_output(pevent) : bool
def $get_test_output(eps) = eps
def $get_test_output((OUTPUT ptbytes) :: pevent_tail*) = ptbytes ++ $get_test_output(pevent_tail*)
def $get_test_output(pevent :: pevent_tail*) = $get_test_output(pevent_tail*) -- if ~$get_test_is_output(pevent)
def $get_test_is_output(OUTPUT ptbytes) = true
def $get_test_is_output(pevent) = false -- otherwise
dec $get_test_copy(ptask*) : (ppropertyget, poperand)?
dec $get_test_is_copy(ptask) : bool
def $get_test_is_copy(PROPERTY_GET_COPY ppropertyget poperand) = true
def $get_test_is_copy(ptask) = false -- otherwise
def $get_test_copy((PROPERTY_GET_COPY ppropertyget poperand) :: ptask_tail*) = ((ppropertyget, poperand))
def $get_test_copy(ptask :: ptask_tail*) = $get_test_copy(ptask_tail*)
  -- if ~$get_test_is_copy(ptask)
def $get_test_copy(eps) = eps
dec $get_test_frame_copy(pframe*) : (ppropertyget, poperand)?
def $get_test_frame_copy(pframe :: pframe_tail*) = $get_test_copy(pframe.TODO)
  -- if $get_test_copy(pframe.TODO) =/= eps
def $get_test_frame_copy(pframe :: pframe_tail*) = $get_test_frame_copy(pframe_tail*)
  -- if $get_test_copy(pframe.TODO) = eps
def $get_test_frame_copy(eps) = eps
dec $get_test_message(pstate, nat, ptbytes) : bool
def $get_test_message(S, n, ptbytes) = ($string_bytes($throwable_field(S, n, "message")) = (ptbytes))
dec $get_test_reader_destructor(pstate) : bool
def $get_test_reader_destructor(S) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OPERATION =/= eps
  -- if $get_test_frame_copy(S.FRAMES) = ((ppropertyget, poperand))
  -- if pdestructorcall.OBJECT = ppropertyget.OBJECT
def $get_test_reader_destructor(S) = false -- otherwise
dec $get_test_phase(pstate, nat) : bool
def $get_test_phase(S, 0) = ($property_get_plan(S) =/= eps)
def $get_test_phase(S, 1) = true
  -- if S.TODO = (CALL_ARGS (PROPERTY_GET_TARGET n porigin_method) eps 1 poperand* porigin_site? z) :: (PROPERTY_GET_RESULT ppropertyget) :: ptask_tail*
def $get_test_phase(S, 2) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = PROPERTY_GET_TARGET n porigin
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_tail*
  -- if S_global = $global_table_view(S)
  -- if $lookup(S_global.ENV, $ptascii("reader")) = eps
  -- if S.DESTRUCTION.OPERATIONS = eps
def $get_test_phase(S, 3) = true
  -- if S.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_tail*
def $get_test_phase(S, 4) = $get_test_reader_destructor(S)
def $get_test_phase(S, 5) = true
  -- if S.TODO = (PROPERTY_GET_COPY ppropertyget poperand) :: ptask_tail*
def $get_test_phase(S, 6) = true
  -- if S.TODO = (THROW_SEARCH n) :: (PROPERTY_GET_COPY ppropertyget poperand) :: ptask_tail*
def $get_test_phase(S, 7) = true
  -- if S.TODO = (THROW_SEARCH n) :: (PROPERTY_GET_DROP ppropertyget pvalue) :: ptask_tail*
def $get_test_phase(S, 8) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
  -- if $object_name(S, pdestructorcall.OBJECT) = $ptascii("MagicGetReturnedLeaf26")
  -- if pdestructorcall.OPERATION = (pdestructionoperation)
  -- if pdestructionoperation.PENDING =/= eps
def $get_test_phase(S, 9) = true
  -- if S.TODO = (THROW_SEARCH n) :: ptask_tail*
  -- if $get_test_message(S, n, $ptascii("B"))
  -- if $throwable_previous_id(S, n) =/= eps
def $get_test_phase(S, 10) = true
  -- if S.TODO = (THROW_SEARCH n) :: ptask_tail*
  -- if $get_test_message(S, n, $ptascii("C"))
  -- if $throwable_previous_id(S, n) =/= eps
def $get_test_phase(S, 12) = true
  -- if $get_test_reader_destructor(S)
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OPERATION = (pdestructionoperation)
  -- if S.DESTRUCTION.OPERATIONS = [pdestructionoperation]
  -- if S_global = $global_table_view(S)
  -- if $lookup(S_global.ENV, $ptascii("return_cell")) = eps
def $get_test_phase(S, 13) = true
  -- if S.TODO = (PROPERTY_PREP (NIdentifier (BYTES text) metadata_name) z) :: (DIM_FETCH z) :: ptask_tail*
  -- if S_read = $quiet_operand(S, S.RESULT)
  -- if S_read.RESULT = KNOWN (POBJECT n)
  -- if $objectprops_at(S.OBJECTPROPS, n) = (ppropertyslot_all*)
  -- if $property_slot_at(ppropertyslot_all*, $base64(text)) = (ppropertyslot)
  -- if ppropertyslot.STATE = PROP_INITIAL
def $get_test_phase(S, 15) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = PROPERTY_GET_TARGET n porigin
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_tail*
def $get_test_phase(S, 16) = true
  -- if S.TODO = (THROW_SEARCH n) :: (PROPERTY_GET_RESULT ppropertyget) :: ptask_tail*
def $get_test_phase(S, 17) = true
  -- if S.TODO = (THROW_SEARCH n) :: ptask_tail*
  -- if $object_name(S, n) = $ptascii("Error")
  -- if S_global = $global_table_view(S)
  -- if $trace_slot(S_global, S_global.ENV, $ptascii("get_calls")) = PINT 0
def $get_test_phase(S, 18) = true
  -- if S.TODO = DISCARD :: ptask_tail*
  -- if S.RESULT = KNOWN (POBJECT n)
  -- if S.CURRENT = eps
def $get_test_phase(S, 19) = (S.DESTRUCTION.OPERATIONS = eps)
def $get_test_phase(S, n) = false -- otherwise
dec $get_test_seek(pstate, nat, nat) : pstate
def $get_test_seek(S, n_phase, n) = S -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $get_test_seek(S, n_phase, n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $get_test_phase(S, n_phase)
def $get_test_seek(S, n_phase, 0) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$get_test_phase(S, n_phase)
def $get_test_seek(S, n_phase, n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$get_test_phase(S, n_phase)
  -- if $(n > 0) /\ S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps
def $get_test_seek(S, n_phase, n) = $get_test_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_phase, $nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$get_test_phase(S, n_phase)
  -- if $(n > 0)
  -- if S.TODO =/= eps \/ S.CURRENT =/= eps \/ S.FRAMES =/= eps
'''


def valid(state):
    return [f'$call_descriptors_valid({state})', f'$heap_valid($heap_graph({state}))',
        f'$scope_codes_valid({state}, {state}.CODE)']


def seek(parent, state, phase):
    return [f'{state}_found = $get_test_seek({parent}, {phase}, 2048)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = {state}_found[.COMPLETION = NORMAL]',
        f'$get_test_phase({state}, {phase})', *valid(state)]


def step(parent, state):
    return [f'{state}_found = $drive_steps({parent}, 1)', f'{state}_found.COMPLETION = BUDGET',
        f'{state} = {state}_found[.COMPLETION = NORMAL]', *valid(state)]


def receive():
    return [*step('S_copy', 'S_receiving'), *seek('S_receiving', 'S_received', 19),
        'S_received.TODO = ptask_copy_tail*']


def finish(parent, expected):
    return [f'S_paused = $drive_steps({parent}, 0)', f'S_paused = {parent}[.COMPLETION = BUDGET]',
        'S_done = $drive(S_paused[.COMPLETION = NORMAL], 2048)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        '$get_test_output(S_done.EVENTS) = '+cross.invoke.byte_expr(expected.encode()), *valid('S_done')]


def start(run, source):
    line = next(i for i, item in enumerate(source.splitlines(), 1)
        if b'$result = $reader->' in item or item.strip() == b'$reader->missing;')
    return ['S_initial = '+run, '~S_initial.COMPILESTOP', *seek('S_initial', 'S_before', 0),
        '$property_get_plan(S_before) = (ppropertyget)',
        'n_reader = ppropertyget.OBJECT', f'ppropertyget.LINE = {line}',
        '$property_get_history(S_before, ppropertyget)', '$property_get_valid(S_before, ppropertyget, true)',
        '$lookup(S_before.ENV, $ptascii("reader")) = (n_reader_cell)',
        'S_before.STORE[n_reader_cell] = DEFINED (POBJECT n_reader)',
        '$property_get_carriers(S_before.TODO, n_reader, ppropertyget.SITE) = 0',
        '$heap_owners($heap_graph(S_before), HOBJECT n_reader) = 1',
        '$task_nodes(PROPERTY_GET_RESULT ppropertyget) = [HOBJECT n_reader]',
        *step('S_before', 'S_pending'),
        'S_pending.TODO = ptask_call :: (PROPERTY_GET_RESULT ppropertyget) :: ptask_read_tail*',
        'pcalltarget_get = PROPERTY_GET_TARGET n_reader ppropertyget.METHOD',
        'ptask_call = CALL_ARGS pcalltarget_get eps 1 ([KNOWN (PSTRING ppropertyget.NAME)]) (ppropertyget.SITE) ppropertyget.LINE',
        '$property_get_pending_call(S_pending, pcalltarget_get, ppropertyget.SITE)',
        '$call_task_valid(S_pending, ptask_call)',
        '$target_nodes(pcalltarget_get) = eps', '$target_instance(pcalltarget_get) = eps',
        '$heap_owners($heap_graph(S_pending), HOBJECT n_reader) = 2',
        '$target_function(S_pending, pcalltarget_get) = (pfunction_get)',
        '$ppmethod_get_signature(pfunction_get.SIGNATURE)']


def getter_body(parent='S_pending', keep_reader=False):
    checks = [*seek(parent, 'S_getter', 15 if keep_reader else 2),
        'S_getter.CURRENT = (pcallcontext_get)',
        'pcallcontext_get.TARGET = pcalltarget_get',
        'S_getter.FRAMES = pframe_get :: pframe_get_tail*',
        'pframe_get.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_get_tail*',
        '$property_get_frame(S_getter, pcallcontext_get, pframe_get)',
        '$property_get_context(S_getter, pcallcontext_get)',
        '$call_receiver_roots(pcallcontext_get) = eps',
        '$reference_callback_used(S_getter, pcallcontext_get) = (true)', '$reference_return_used(S_getter)',
        'S_getter_global = $global_table_view(S_getter)',
        '$property_get_guard_frames(S_getter.FRAMES, n_reader, ppropertyget.NAME)',
        'S_getter_scope = $constant_frame_scope(S_getter, pframe_get, pframe_get_tail*)',
        '$property_get_valid(S_getter_scope, ppropertyget, true)']
    if not keep_reader:
        checks += ['$lookup(S_getter_global.ENV, $ptascii("reader")) = eps',
            '$heap_owners($heap_graph(S_getter), HOBJECT n_reader) = 1',
            '$property_get_capture(S_getter_scope, ppropertyget) = false']
    return checks


def returned(reference=True):
    checks = [*seek('S_getter', 'S_return', 3),
        'S_return.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_return_tail*',
        '$heap_owners($heap_graph(S_return), HOBJECT n_reader) = 1',
        '$property_get_valid(S_return, ppropertyget, true)',
        '$property_get_guard_tasks(S_return.TODO, n_reader, ppropertyget.NAME)',
        '$property_get_method(S_return, n_reader) = (pmethoddesc_get)',
        'pmethoddesc_get.FUNCTION.ORIGIN = ppropertyget.METHOD',
        'S_return_global = $global_table_view(S_return)',
        '$lookup(S_return_global.ENV, $ptascii("reader")) = eps']
    if reference:
        checks += ['S_return.RESULT = REFERENCE n_return_cell',
            '$lookup(S_return_global.ENV, $ptascii("return_cell")) = (n_return_cell)',
            '$heap_owners($heap_graph(S_return), HCELL n_return_cell) = 2',
            '$task_nodes(PROPERTY_GET_COPY ppropertyget (REFERENCE n_return_cell)) = [HCELL n_return_cell]',
            '$propref_at(S_return.PROPREFS, n_return_cell) = eps',
            '$parameter_backing_at(S_return.PARAMETERBACKINGS, n_return_cell) = eps']
    return checks


def receiver_destructor(parent, pending=None):
    checks = [*seek(parent, 'S_reader_dtor', 4), 'S_reader_dtor.CURRENT = (pcallcontext_reader_dtor)',
        '$destructor_context_call(pcallcontext_reader_dtor, S_reader_dtor.CURRENT, S_reader_dtor.FRAMES) = (pdestructorcall_reader)',
        'pdestructorcall_reader.OBJECT = n_reader',
        'pdestructorcall_reader.OPERATION = (pdestructionoperation_reader)',
        '$destructor_call_pending_valid(S_reader_dtor, pdestructorcall_reader)',
        '$get_test_frame_copy(S_reader_dtor.FRAMES) = ((ppropertyget, poperand_rv))',
        '$property_get_valid(S_reader_dtor, ppropertyget, true)',
        '~$property_get_guard_tasks(S_reader_dtor.TODO, n_reader, ppropertyget.NAME)',
        '~$property_get_guard_frames(S_reader_dtor.FRAMES, n_reader, ppropertyget.NAME)',
        '(HOBJECT n_reader) <- S_reader_dtor.ALLOCATIONS', '~$instance_storage_freeing(S_reader_dtor, n_reader)',
        'S_reader_dtor_global = $global_table_view(S_reader_dtor)',
        '$trace_slot(S_reader_dtor_global, S_reader_dtor_global.ENV, $ptascii("reader_weak")) = POBJECT n_reader_weak',
        '$weakref_get(S_reader_dtor, n_reader_weak) = POBJECT n_reader']
    checks += ['pdestructionoperation_reader.PENDING = '+('eps' if pending is None else '('+pending+')')]
    return checks


def copied(parent='S_reader_dtor'):
    return [*seek(parent, 'S_copy', 5),
        'S_copy.TODO = (PROPERTY_GET_COPY ppropertyget poperand_copy) :: ptask_copy_tail*',
        'S_copy.RESULT = KNOWN PNULL', 'S_copy.BASE = BASE_VALUE (KNOWN PNULL)',
        '~((HOBJECT n_reader) <- S_copy.ALLOCATIONS)',
        '$weakref_get(S_copy, n_reader_weak) = PNULL',
        '$property_get_history(S_copy, ppropertyget)', '$property_get_valid(S_copy, ppropertyget, false)',
        '~$property_get_valid(S_copy, ppropertyget, true)',
        '~$property_get_guard_tasks(S_copy.TODO, n_reader, ppropertyget.NAME)',
        '$property_get_plan(S_copy) = eps']


def admission():
    checks = ['S_before.TODO = (PROPERTY_PREP phpType20_name z_get) :: (DIM_FETCH z_get) :: ptask_before_tail*',
        'S_before.ORIGIN = (ppropertyget.SITE)',
        '$origin_node(S_before.SOURCES, ppropertyget.SITE) = (NExprPropertyFetch (NExprVariable (BYTES text_reader) metadata_reader) phpType20_name metadata_get)',
        '$property_get_source(S_before, ppropertyget)',
        '$call_arguments_valid(S_pending, (ppropertyget.SITE), 1, eps, [KNOWN (PSTRING ppropertyget.NAME)], 0)',
        '~$call_arguments_valid(S_pending, (ppropertyget.SITE), 1, eps, [KNOWN (PSTRING $ptascii("forged26"))], 0)',
        '~$call_arguments_valid(S_pending, (ppropertyget.SITE), 1, eps, eps, 0)',
        'S_bad_base = S_before[.BASE = BASE_VALUE (KNOWN (POBJECT n_reader))]',
        '$property_get_plan(S_bad_base) = eps',
        'S_latent = S_before[.TODO = S_before.TODO ++ [PROPERTY_GET_RESULT ppropertyget]]',
        '$property_get_plan(S_latent) = eps',
        'S_duplicate_pending = S_pending[.TODO = S_pending.TODO ++ [PROPERTY_GET_RESULT ppropertyget]]',
        '$property_get_carriers(S_duplicate_pending.TODO, n_reader, ppropertyget.SITE) = 2',
        '~$call_descriptors_valid(S_duplicate_pending)',
        'S_missing_pending = S_pending[.TODO = ptask_call :: ptask_read_tail*]',
        '~$call_descriptors_valid(S_missing_pending)',
        '~$call_task_valid(S_pending, CALL_ARGS (METHOD_TARGET n_reader ppropertyget.METHOD) eps 1 ([KNOWN (PSTRING ppropertyget.NAME)]) (ppropertyget.SITE) ppropertyget.LINE)']
    for field in ('.NAME = $ptascii("forged26")', '.LINE = 999', '.SITE = ppropertyget.METHOD',
                  '.CLASS = ppropertyget.METHOD', '.METHOD = ppropertyget.SITE', '.OBJECT = |S_pending.OBJECTS|',
                  '.DECL = (ppropertyget.METHOD)'):
        checks += [f'~$property_get_history(S_pending, ppropertyget[{field}])',
            f'~$call_task_valid(S_pending, PROPERTY_GET_RESULT ppropertyget[{field}])']
    # Constructed same-class instance; actual source CV continues to name the original.
    checks += ['S_second = $destruction_store_new($new_class(S_pending, $object_name(S_pending, n_reader), ppropertyget.LINE))',
        'S_second.RESULT = KNOWN (POBJECT n_second)', 'n_second =/= n_reader',
        'S_second.OBJECTS[n_second] = INSTANCE ppropertyget.CLASS',
        '(HOBJECT n_second) <- S_second.ALLOCATIONS', '~$instance_storage_freeing(S_second, n_second)',
        '$heap_owners($heap_graph(S_second), HOBJECT n_second) = 1', '$heap_valid($heap_graph(S_second))',
        'ppropertyget_second = ppropertyget[.OBJECT = n_second]',
        '$property_get_history(S_second, ppropertyget_second)',
        'S_wrong_instance = S_second[.TODO = (CALL_ARGS (PROPERTY_GET_TARGET n_second ppropertyget.METHOD) eps 1 ([KNOWN (PSTRING ppropertyget.NAME)]) (ppropertyget.SITE) ppropertyget.LINE) :: (PROPERTY_GET_RESULT ppropertyget_second) :: ptask_read_tail*][.ORIGIN = (ppropertyget.SITE)][.BASE = BASE_VALUE (KNOWN PNULL)]',
        '$property_get_valid(S_wrong_instance, ppropertyget_second, true)',
        '$property_get_source(S_wrong_instance, ppropertyget_second)',
        '$trace_slot(S_wrong_instance, S_wrong_instance.ENV, $ptascii("reader")) = POBJECT n_reader',
        '~$property_get_capture(S_wrong_instance, ppropertyget_second)',
        '~$property_get_pending_call(S_wrong_instance, PROPERTY_GET_TARGET n_second ppropertyget.METHOD, ppropertyget.SITE)',
        'S_second_cv = S_wrong_instance[.STORE[n_reader_cell] = DEFINED (POBJECT n_second)]',
        '$property_get_capture(S_second_cv, ppropertyget_second)',
        '$property_get_pending_call(S_second_cv, PROPERTY_GET_TARGET n_second ppropertyget.METHOD, ppropertyget.SITE)']
    return checks


def saved_admission():
    checks = ['S_saved_duplicate = S_getter[.FRAMES = pframe_get[.TODO = (PROPERTY_GET_RESULT ppropertyget) :: pframe_get.TODO] :: pframe_get_tail*]',
        '~$call_descriptors_valid(S_saved_duplicate)',
        'S_saved_missing = S_getter[.FRAMES = pframe_get[.TODO = ptask_get_tail*] :: pframe_get_tail*]',
        '~$call_descriptors_valid(S_saved_missing)',
        'pcallcontext_ordinary = pcallcontext_get[.TARGET = METHOD_TARGET n_reader ppropertyget.METHOD]',
        '~$property_get_context(S_getter[.CURRENT = (pcallcontext_ordinary)], pcallcontext_ordinary)',
        '~$call_descriptors_valid(S_getter[.CURRENT = (pcallcontext_ordinary)])',
        '~$call_descriptors_valid(S_getter[.CURRENT = (pcallcontext_get[.LINE = 999])])']
    for field in ('.NAME = $ptascii("forged26")', '.LINE = 999', '.SITE = ppropertyget.METHOD',
                  '.METHOD = ppropertyget.SITE', '.OBJECT = |S_getter.OBJECTS|'):
        checks += [f'~$property_get_frame(S_getter, pcallcontext_get, pframe_get[.TODO = (PROPERTY_GET_RESULT ppropertyget[{field}]) :: ptask_get_tail*])',
            f'~$call_descriptors_valid(S_getter[.FRAMES = pframe_get[.TODO = (PROPERTY_GET_RESULT ppropertyget[{field}]) :: ptask_get_tail*] :: pframe_get_tail*])']
    checks += ['S_recursive = S_before[.FRAMES = pframe_get :: pframe_get_tail*]',
        '$trace_slot(S_recursive, S_recursive.ENV, $ptascii("reader")) = POBJECT n_reader',
        '$property_get_needed(S_recursive, n_reader, ppropertyget.NAME)',
        '$property_get_guard_frames(S_recursive.FRAMES, n_reader, ppropertyget.NAME)',
        '$property_get_pending(S_recursive)', '$property_get_plan(S_recursive) = eps',
        'S_return_duplicate = S_return[.TODO = (PROPERTY_GET_RESULT ppropertyget) :: S_return.TODO]',
        '~$call_descriptors_valid(S_return_duplicate)']
    return checks


def body(run, expected, group, source):
    if group == 'initial':
        return initial_body(run, expected, source)
    checks = start(run, source)
    if group == 'reference':
        checks += admission()
    checks += getter_body()
    if group == 'getter-throw':
        return checks + getter_throw(expected)
    checks += returned(group != 'value')
    if group == 'reference':
        checks += saved_admission()
    if group in ('readonly', 'type-error'):
        checks += typed(group == 'type-error', expected)
        return checks
    if group == 'value':
        checks += ['S_return.RESULT = KNOWN (POBJECT n_old)',
            '$trace_slot(S_return_global, S_return_global.ENV, $ptascii("return_cell")) = POBJECT n_old',
            '$heap_owners($heap_graph(S_return), HOBJECT n_old) = 2']
    else:
        checks += ['S_return.STORE[n_return_cell] = DEFINED (POBJECT n_old)',
            '$heap_owners($heap_graph(S_return), HOBJECT n_old) = 1']
    checks += ['$property_get_verify(S_return, ppropertyget, S_return.RESULT) = S_return',
        *receiver_destructor('S_return'), 'pdestructionoperation_reader.SOURCE = PROPERTY_GET_RESULT ppropertyget']
    if group == 'returned-throw':
        return checks + returned_throw(expected)
    if group == 'discarded':
        return checks + discarded(expected)
    checks += copied()
    if group == 'reference':
        checks += ['poperand_copy = REFERENCE n_return_cell',
            'S_copy.STORE[n_return_cell] = DEFINED (POBJECT n_new)', 'n_new =/= n_old',
            '~((HOBJECT n_old) <- S_copy.ALLOCATIONS)',
            '$trace_slot(S_copy, S_copy.ENV, $ptascii("old_weak")) = POBJECT n_old_weak',
            '$weakref_get(S_copy, n_old_weak) = PNULL',
            '$heap_owners($heap_graph(S_copy), HCELL n_return_cell) = 2',
            '$heap_owners($heap_graph(S_copy), HOBJECT n_new) = 1',
            *receive(), 'S_received.RESULT = KNOWN (POBJECT n_new)',
            'S_receiving.DESTRUCTION.OPERATIONS = pdestructionoperation_copy :: pdestructionoperation_copy_tail*',
            'pdestructionoperation_copy.SOURCE = PROPERTY_GET_COPY ppropertyget (REFERENCE n_return_cell)',
            'pdestructionoperation_copy.VALUE = KNOWN (POBJECT n_new)',
            'pdestructionoperation_copy.PENDING = eps',
            'S_receiving.RESULT = KNOWN PNULL',
            '$heap_owners($heap_graph(S_received), HCELL n_return_cell) = 1',
            '$task_nodes(PROPERTY_GET_COPY ppropertyget (REFERENCE n_return_cell)) = [HCELL n_return_cell]',
            'S_standalone_drop = S_copy[.TODO = [PROPERTY_GET_DROP ppropertyget (POBJECT n_new)]]',
            '~$property_get_drop_pending(S_standalone_drop)',
            '~$call_task_valid(S_standalone_drop, PROPERTY_GET_DROP ppropertyget (POBJECT n_new))',
            '~$call_descriptors_valid(S_standalone_drop)', *finish('S_received', expected)]
    else:
        checks += ['poperand_copy = KNOWN (POBJECT n_old)',
            '$trace_slot(S_copy, S_copy.ENV, $ptascii("return_cell")) = POBJECT n_new', 'n_new =/= n_old',
            '$heap_owners($heap_graph(S_copy), HOBJECT n_old) = 1',
            '$heap_owners($heap_graph(S_copy), HOBJECT n_new) = 1',
            *receive(), 'S_received.RESULT = KNOWN (POBJECT n_old)',
            *finish('S_received', expected)]
    return checks + ['~((HOBJECT n_old) <- S_done.ALLOCATIONS)', '~((HOBJECT n_new) <- S_done.ALLOCATIONS)']


def typed(reject, expected):
    checks = ['ppropertyget.DECL = (ppropertyid)',
        '$property_desc_at($property_layout(S_return, ppropertyget.CLASS, |S_return.CLASSES|), ppropertyget.NAME) = (ppropertydesc_get)',
        'ppropertydesc_get.TYPE =/= eps', 'ppropertydesc_get.READONLY',
        '$objectprops_at(S_return.OBJECTPROPS, n_reader) = (ppropertyslot_get_all*)',
        '$property_slot_at(ppropertyslot_get_all*, ppropertyget.NAME) = (ppropertyslot_get)',
        'ppropertyslot_get.STATE = PROP_UNSET',
        '~pmethoddesc_get.FUNCTION.CODE.STRICT',
        'S_payload = $quiet_operand(S_return, S_return.RESULT)', 'S_payload.RESULT = KNOWN pvalue_return',
        '$property_get_unconstrained(S_return, S_return.RESULT)']
    if not reject:
        checks += ['pvalue_return = PINT 7',
            '$typed_conversion_at(S_return, ppropertydesc_get.TYPE, pvalue_return, pmethoddesc_get.FUNCTION.CODE.STRICT) = TYPEVALUE pvalue_return',
            '$property_get_verify(S_return, ppropertyget, S_return.RESULT) = S_return',
            'S_coercion = S_return[.STORE[n_return_cell] = DEFINED (PSTRING ($ptascii("7.5")))]',
            '$typed_conversion_at(S_coercion, ppropertydesc_get.TYPE, PSTRING ($ptascii("7.5")), false) = TYPEINTEGER (PSTRING ($ptascii("7.5")))',
            '$typed_number(PSTRING ($ptascii("7.5"))) = (NFLOAT n_coercion)',
            'S_coercion_checked = $property_get_verify(S_coercion, ppropertyget, REFERENCE n_return_cell)',
            'S_coercion_checked.COMPLETION = UNSUPPORTED "magic getter property type coercion"',
            *receiver_destructor('S_return'), 'poperand_rv = REFERENCE n_return_cell',
            *copied(), 'poperand_copy = REFERENCE n_return_cell',
            'S_copy.STORE[n_return_cell] = DEFINED pvalue_changed',
            '$string_bytes(pvalue_changed) = ($ptascii("changed"))',
            '$typed_conversion_at(S_copy, ppropertydesc_get.TYPE, pvalue_changed, false) = TYPEREJECT',
            '$propref_at(S_copy.PROPREFS, n_return_cell) = eps',
            '$parameter_backing_at(S_copy.PARAMETERBACKINGS, n_return_cell) = eps',
            *receive(), 'S_received.RESULT = KNOWN pvalue_changed',
            *finish('S_received', expected),
            '$trace_slot(S_done, S_done.ENV, $ptascii("result")) = pvalue_result_done',
            '$string_bytes(pvalue_result_done) = ($ptascii("changed"))',
            '$trace_slot(S_done, S_done.ENV, $ptascii("return_cell")) = PINT 13']
    else:
        message = expected.split('caught=', 1)[1].split('|', 1)[0]
        checks += ['$string_bytes(pvalue_return) = ($ptascii("bad"))',
            '$typed_conversion_at(S_return, ppropertydesc_get.TYPE, pvalue_return, false) = TYPEREJECT',
            'S_verify = $property_get_verify(S_return, ppropertyget, S_return.RESULT)',
            'S_verify.COMPLETION = THROWN "TypeError" '+cross.invoke.byte_expr(message.encode())+' ppropertyget.LINE',
            'S_complete = $property_get_complete(S_return, ppropertyget, S_return.RESULT)',
            'S_complete.TODO = (PROPERTY_GET_COPY ppropertyget (REFERENCE n_return_cell)) :: ptask_return_tail*',
            'S_complete.RESULT = KNOWN PNULL', 'S_complete.BASE = BASE_VALUE (KNOWN PNULL)',
            '$throwable_same_frame_continuation(S_return, S_complete, ptask_return_tail*) = S_complete',
            'S_transition = $throwable_transition(S_return, S_complete)',
            'S_transition.COMPLETION = THROWING n_type_error',
            'S_transition.TODO = S_complete.TODO',
            '$get_test_message(S_transition, n_type_error, '+cross.invoke.byte_expr(message.encode())+')',
            'S_bad_descriptor_continuation = $throwable_same_frame_continuation(S_return, S_complete[.TODO = (PROPERTY_GET_COPY ppropertyget[.LINE = 999] (REFERENCE n_return_cell)) :: ptask_return_tail*], ptask_return_tail*)',
            'S_bad_descriptor_continuation.TODO = ptask_return_tail*',
            'S_bad_raw_continuation = $throwable_same_frame_continuation(S_return, S_complete[.TODO = (PROPERTY_GET_COPY ppropertyget (KNOWN PNULL)) :: ptask_return_tail*], ptask_return_tail*)',
            'S_bad_raw_continuation.TODO = ptask_return_tail*',
            'S_bad_tail_continuation = $throwable_same_frame_continuation(S_return, S_complete[.TODO = [PROPERTY_GET_COPY ppropertyget (REFERENCE n_return_cell)]], ptask_return_tail*)',
            'S_bad_tail_continuation.TODO = ptask_return_tail*',
            *receiver_destructor('S_return', 'n_type_error'),
            'poperand_rv = REFERENCE n_return_cell',
            '$get_test_message(S_reader_dtor, n_type_error, '+cross.invoke.byte_expr(message.encode())+')',
            'S_reader_dtor.STORE[n_return_cell] = DEFINED pvalue_return',
            *seek('S_reader_dtor', 'S_error_copy', 6),
            'S_error_copy.TODO = (THROW_SEARCH n_type_error) :: (PROPERTY_GET_COPY ppropertyget (REFERENCE n_return_cell)) :: ptask_error_tail*',
            'S_error_copy.RESULT = KNOWN PNULL', 'S_error_copy.BASE = BASE_VALUE (KNOWN PNULL)',
            'S_error_copy.STORE[n_return_cell] = DEFINED (PINT 7)',
            '~((HOBJECT n_reader) <- S_error_copy.ALLOCATIONS)',
            '$get_test_message(S_error_copy, n_type_error, '+cross.invoke.byte_expr(message.encode())+')',
            *finish('S_error_copy', expected),
            '$trace_slot(S_done, S_done.ENV, $ptascii("return_cell")) = PINT 7',
            '$lookup(S_done.ENV, $ptascii("result")) = eps']
    return checks


def getter_throw(expected):
    return [*seek('S_getter', 'S_getter_throw', 16),
        'S_getter_throw.TODO = (THROW_SEARCH n_getter_error) :: (PROPERTY_GET_RESULT ppropertyget) :: ptask_getter_throw_tail*',
        '$get_test_message(S_getter_throw, n_getter_error, $ptascii("H"))',
        '$heap_owners($heap_graph(S_getter_throw), HOBJECT n_reader) = 1',
        *receiver_destructor('S_getter_throw', 'n_getter_error'), 'poperand_rv = KNOWN PNULL',
        *seek('S_reader_dtor', 'S_chained', 9), 'S_chained.TODO = (THROW_SEARCH n_reader_error) :: ptask_chained_tail*',
        '$throwable_previous_id(S_chained, n_reader_error) = (n_getter_error)',
        '$get_test_message(S_chained, n_reader_error, $ptascii("B"))',
        *finish('S_chained', expected), '~((HOBJECT n_reader) <- S_done.ALLOCATIONS)']


def dropped_global():
    return [*seek('S_reader_dtor', 'S_dropped_global', 12),
        '$get_test_frame_copy(S_dropped_global.FRAMES) = ((ppropertyget, REFERENCE n_return_cell))',
        '$heap_owners($heap_graph(S_dropped_global), HCELL n_return_cell) = 1',
        '$heap_owners($heap_graph(S_dropped_global), HOBJECT n_old) = 1',
        'S_dropped_global_global = $global_table_view(S_dropped_global)',
        '$trace_slot(S_dropped_global_global, S_dropped_global_global.ENV, $ptascii("return_weak")) = POBJECT n_return_weak',
        '$weakref_get(S_dropped_global, n_return_weak) = POBJECT n_old']


def returned_throw(expected):
    return [*dropped_global(), *seek('S_dropped_global', 'S_pending_copy', 6),
        'S_pending_copy.TODO = (THROW_SEARCH n_reader_error) :: (PROPERTY_GET_COPY ppropertyget (REFERENCE n_return_cell)) :: ptask_pending_tail*',
        '$get_test_message(S_pending_copy, n_reader_error, $ptascii("B"))',
        'S_pending_copy.RESULT = KNOWN PNULL', 'S_pending_copy.BASE = BASE_VALUE (KNOWN PNULL)',
        '~((HOBJECT n_reader) <- S_pending_copy.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_pending_copy), HCELL n_return_cell) = 1',
        '$weakref_get(S_pending_copy, n_return_weak) = POBJECT n_old',
        'S_drop_pure = $return_discard(S_pending_copy[.TODO = (THROW_SEARCH n_reader_error) :: ptask_pending_tail*], PROPERTY_GET_COPY ppropertyget (REFERENCE n_return_cell))',
        'S_drop_pure.TODO = (THROW_SEARCH n_reader_error) :: (PROPERTY_GET_DROP ppropertyget (POBJECT n_old)) :: ptask_pending_tail*',
        'S_drop_pure.RESULT = KNOWN PNULL', 'S_drop_pure.BASE = BASE_VALUE (KNOWN PNULL)',
        *seek('S_pending_copy', 'S_drop', 7),
        'S_drop.TODO = (THROW_SEARCH n_reader_error) :: (PROPERTY_GET_DROP ppropertyget (POBJECT n_old)) :: ptask_drop_tail*',
        'S_drop.RESULT = KNOWN PNULL', 'S_drop.BASE = BASE_VALUE (KNOWN PNULL)',
        '~((HCELL n_return_cell) <- S_drop.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_drop), HOBJECT n_old) = 1',
        '$task_nodes(PROPERTY_GET_DROP ppropertyget (POBJECT n_old)) = [HOBJECT n_old]',
        '$call_task_valid(S_drop, PROPERTY_GET_DROP ppropertyget (POBJECT n_old))',
        *seek('S_drop', 'S_leaf_dtor', 8), 'S_leaf_dtor.CURRENT = (pcallcontext_leaf)',
        '$destructor_context_call(pcallcontext_leaf, S_leaf_dtor.CURRENT, S_leaf_dtor.FRAMES) = (pdestructorcall_leaf)',
        'pdestructorcall_leaf.OBJECT = n_old', 'pdestructorcall_leaf.OPERATION = (pdestructionoperation_leaf)',
        'pdestructionoperation_leaf.PENDING = (n_reader_error)',
        '$destructor_call_pending_valid(S_leaf_dtor, pdestructorcall_leaf)',
        '(HOBJECT n_old) <- S_leaf_dtor.ALLOCATIONS', '~$instance_storage_freeing(S_leaf_dtor, n_old)',
        '$weakref_get(S_leaf_dtor, n_return_weak) = POBJECT n_old',
        *seek('S_leaf_dtor', 'S_chained', 10), 'S_chained.TODO = (THROW_SEARCH n_leaf_error) :: ptask_chained_tail*',
        '$throwable_previous_id(S_chained, n_leaf_error) = (n_reader_error)',
        '$get_test_message(S_chained, n_leaf_error, $ptascii("C"))',
        *finish('S_chained', expected), '$weakref_get(S_done, n_return_weak) = PNULL',
        '~((HOBJECT n_old) <- S_done.ALLOCATIONS)', '~((HCELL n_return_cell) <- S_done.ALLOCATIONS)',
        '$lookup(S_done.ENV, $ptascii("result")) = eps', '$lookup(S_done.ENV, $ptascii("return_cell")) = eps']


def discarded(expected):
    return [*dropped_global(),
        '~$reference_call_used(S_getter, ppropertyget.SITE)', '$reference_return_used(S_getter)',
        *copied('S_dropped_global'), 'poperand_copy = REFERENCE n_return_cell',
        '$heap_owners($heap_graph(S_copy), HCELL n_return_cell) = 1',
        *seek('S_copy', 'S_received', 18), 'S_received.RESULT = KNOWN (POBJECT n_old)',
        '~((HCELL n_return_cell) <- S_received.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_received), HOBJECT n_old) = 1',
        '$weakref_get(S_received, n_return_weak) = POBJECT n_old',
        *finish('S_received', expected), '$weakref_get(S_done, n_return_weak) = PNULL',
        '~((HOBJECT n_old) <- S_done.ALLOCATIONS)', '$lookup(S_done.ENV, $ptascii("return_cell")) = eps']


def initial_body(run, expected, source):
    return ['S_initial = '+run, '~S_initial.COMPILESTOP', *seek('S_initial', 'S_initial_read', 13),
        'S_initial_read.TODO = (PROPERTY_PREP (NIdentifier (BYTES text_initial_name) metadata_initial_name) z_initial_read) :: (DIM_FETCH z_initial_read) :: ptask_initial_tail*',
        'S_initial_payload = $quiet_operand(S_initial_read, S_initial_read.RESULT)',
        'S_initial_payload.RESULT = KNOWN (POBJECT n_initial_reader)',
        '~$property_get_needed(S_initial_read, n_initial_reader, $base64(text_initial_name))',
        '$property_get_plan(S_initial_read) = eps',
        *seek('S_initial_read', 'S_initial_error', 17),
        'S_initial_error.TODO = (THROW_SEARCH n_initial_error) :: ptask_initial_error_tail*',
        '$trace_slot(S_initial_error, S_initial_error.ENV, $ptascii("get_calls")) = PINT 0',
        *seek('S_initial_error', 'S_before', 0), '$property_get_plan(S_before) = (ppropertyget)',
        'n_reader = ppropertyget.OBJECT', 'n_reader = n_initial_reader',
        '$property_get_needed(S_before, n_reader, ppropertyget.NAME)',
        '$objectprops_at(S_before.OBJECTPROPS, n_reader) = (ppropertyslot_initial_all*)',
        '$property_slot_at(ppropertyslot_initial_all*, ppropertyget.NAME) = (ppropertyslot_initial)',
        'ppropertyslot_initial.STATE = PROP_UNSET',
        *step('S_before', 'S_pending'),
        'pcalltarget_get = PROPERTY_GET_TARGET n_reader ppropertyget.METHOD',
        *getter_body(keep_reader=True),
        '$heap_owners($heap_graph(S_getter), HOBJECT n_reader) = 2',
        *seek('S_getter', 'S_return', 3), 'S_return.RESULT = REFERENCE n_return_cell',
        '$property_get_verify(S_return, ppropertyget, S_return.RESULT) = S_return',
        *seek('S_return', 'S_copy', 5),
        'S_copy.TODO = (PROPERTY_GET_COPY ppropertyget (REFERENCE n_return_cell)) :: ptask_copy_tail*',
        '$heap_owners($heap_graph(S_copy), HOBJECT n_reader) = 1',
        '$heap_owners($heap_graph(S_copy), HCELL n_return_cell) = 2',
        *receive(), 'S_received.RESULT = KNOWN (PINT 7)',
        *finish('S_received', expected),
        '$trace_slot(S_done, S_done.ENV, $ptascii("result")) = PINT 7',
        '$trace_slot(S_done, S_done.ENV, $ptascii("return_cell")) = PINT 17',
        '$trace_slot(S_done, S_done.ENV, $ptascii("get_calls")) = PINT 1']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group', choices=list(CASES), required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    before = cross.snapshot(None)
    out = Path(tempfile.mkdtemp(prefix='magic-property-get-', dir=ROOT/'.tools'))
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
            *body(run, sources.EXPECTED[CASES[args.group]], args.group, original)]
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
