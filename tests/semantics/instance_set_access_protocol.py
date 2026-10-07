#!/usr/bin/env python3
"""Source-reached instance setter permissions and compound callback ownership."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[2]
OWN = ROOT / '.tools'
import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker
from instance_set_access_sources import CASES, EXPECTED

PREFIX = r'''
dec $compound_review_output(pevent*) : ptbytes
dec $compound_review_is_output(pevent) : bool
def $compound_review_output(eps) = eps
def $compound_review_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $compound_review_output(pevent*)
def $compound_review_output(pevent :: pevent_tail*) = $compound_review_output(pevent_tail*) -- if ~$compound_review_is_output(pevent)
def $compound_review_is_output(OUTPUT ptbytes) = true
def $compound_review_is_output(pevent) = false -- otherwise
dec $compound_review_phase(pstate,nat) : bool
def $compound_review_phase(S,0) = true
  -- if S.TODO = (COMPOUND_STRING_PREP plocation pvalue_left pvalue_right porigin_site z) :: ptask_tail*
def $compound_review_phase(S,1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (STRINGIFY_RESULT n porigin_site z) :: (COMPOUND_STRING_LEFT plocation pvalue_right porigin_site z) :: ptask_tail*
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin_method
def $compound_review_phase(S,2) = true
  -- if $compound_review_phase(S,1)
  -- if S_global = $global_table_view(S)
  -- if $lookup(S_global.ENV,$ptascii("value")) = eps
def $compound_review_phase(S,3) = true
  -- if S.TODO = (STRINGIFY_RESULT n porigin_site z) :: (COMPOUND_STRING_LEFT plocation pvalue_right porigin_site z) :: ptask_tail*
  -- if S.RESULT = KNOWN (PSTRING ptbytes)
def $compound_review_phase(S,4) = true
  -- if S.TODO = (COMPOUND_STRING_RIGHT plocation ptbytes_left porigin_site z) :: ptask_tail*
def $compound_review_phase(S,5) = true
  -- if S.CURRENT = (pcallcontext_new)
  -- if S.FRAMES = pframe_new :: pframe_middle :: pframe_old :: pframe_tail*
  -- if pframe_new.TODO = (STRINGIFY_RESULT n porigin_site z) :: (COMPOUND_STRING_LEFT plocation pvalue_right porigin_site z) :: ptask_new_tail*
  -- if pframe_old.TODO = (STRINGIFY_RESULT n porigin_site z) :: (COMPOUND_STRING_LEFT plocation pvalue_right porigin_site z) :: ptask_old_tail*
  -- if pframe_middle.CONTEXT = (pcallcontext_old)
  -- if pcallcontext_new.TARGET = METHOD_TARGET n porigin_method
  -- if pcallcontext_old.TARGET = METHOD_TARGET n porigin_method
  -- if pcallcontext_new.CALLSITE = (porigin_site)
  -- if pcallcontext_old.CALLSITE = (porigin_site)
def $compound_review_phase(S,n) = false -- otherwise
dec $compound_review_terminal(pstate) : bool
def $compound_review_terminal(S) = (S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
dec $compound_review_seek(pstate,nat,nat) : pstate
def $compound_review_seek(S,n_phase,n) = S -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $compound_review_seek(S,n_phase,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $compound_review_phase(S,n_phase)
def $compound_review_seek(S,n_phase,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$compound_review_phase(S,n_phase)
  -- if n = 0 \/ $compound_review_terminal(S)
def $compound_review_seek(S,n_phase,n) = $compound_review_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_phase,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$compound_review_phase(S,n_phase) /\ ~$compound_review_terminal(S) /\ $(n > 0)
'''


def valid(state):
    return [f'$call_descriptors_valid({state})', f'$heap_valid($heap_graph({state}))']


def seek(parent, state, phase):
    return [f'{state}_found = $compound_review_seek({parent},{phase},2048)',
            fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$compound_review_phase({state},{phase})', *valid(state)]


def reject(name, expression, predicate):
    state = 'S_bad_' + name
    return [f'{state} = {expression}', f'$heap_valid($heap_graph({state}))',
            f'~$call_descriptors_valid({state})', '~' + predicate.replace('STATE', state)]


def completed(state, expected):
    return [f'S_done = $drive_steps({state},2048)',
            r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
            '$compound_review_output(S_done.EVENTS) = ' + cross.invoke.byte_expr(expected), *valid('S_done')]


def private(initial, expected):
    prep = 'COMPOUND_STRING_PREP (PROPERTY n_owner ptbytes_key) (POBJECT n_box) pvalue_right porigin_site z'
    checks = ['S_initial = ' + initial, '~S_initial.COMPILESTOP', *seek('S_initial','S_ready',0),
        'S_ready.TODO = (' + prep + ') :: ptask_tail*',
        'pvalue_right = PSTRING $ptascii("x")', 'S_ready.CURRENT = (pcallcontext_owner)',
        '$class_named(S_ready.CLASSNAMES,$ptascii("owner")) = (porigin_owner)',
        '$class_named(S_ready.CLASSNAMES,$ptascii("box")) = (porigin_box)',
        'pcallcontext_owner.LEXICAL_CLASS = (porigin_owner)',
        'S_ready.OBJECTS[n_owner] = INSTANCE porigin_owner',
        '$location_slot(S_ready,PROPERTY n_owner ptbytes_key) = DEFINED (POBJECT n_box)',
        '$compound_string_source(S_ready,PROPERTY n_owner ptbytes_key,porigin_site,z)',
        '$property_resolve(S_ready,n_owner,$ptascii("value")) = PROPERTY_ACCESS ptbytes_key']
    for name, task in [
        ('left', 'COMPOUND_STRING_PREP (PROPERTY n_owner ptbytes_key) PNULL pvalue_right porigin_site z'),
        ('literal', 'COMPOUND_STRING_PREP (PROPERTY n_owner ptbytes_key) (POBJECT n_box) (PSTRING $ptascii("wrong")) porigin_site z'),
        ('line', 'COMPOUND_STRING_PREP (PROPERTY n_owner ptbytes_key) (POBJECT n_box) pvalue_right porigin_site $(z + 1)'),
        ('place', 'COMPOUND_STRING_PREP (ROOT 0) (POBJECT n_box) pvalue_right porigin_site z')]:
        checks += reject(name, 'S_ready[.TODO = (' + task + ') :: ptask_tail*]', '$call_task_valid(STATE,' + task + ')')
    checks += [*seek('S_ready','S_body',1), 'S_body.CURRENT = (pcallcontext_box)',
        'S_body.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (STRINGIFY_RESULT n_box porigin_site z) :: (COMPOUND_STRING_LEFT (PROPERTY n_owner ptbytes_key) pvalue_right porigin_site z) :: ptask_body_tail*',
        'pcallcontext_box.LEXICAL_CLASS = (porigin_box)', 'pcallcontext_box.CALLSITE = (porigin_site)',
        'S_owner = $constant_frame_scope(S_body,pframe,pframe_tail*)',
        'S_owner.CURRENT = (pcallcontext_owner)',
        '$property_resolve(S_owner,n_owner,$ptascii("value")) = PROPERTY_ACCESS ptbytes_key',
        '~($property_resolve(S_body,n_owner,$ptascii("value")) = PROPERTY_ACCESS ptbytes_key)',
        '$stringify_context_frame_valid(S_owner,pcallcontext_box,pframe)']
    checks += reject('consumer',
        'S_body[.FRAMES = pframe[.TODO = (STRINGIFY_RESULT n_box porigin_site z) :: DISCARD :: ptask_body_tail*] :: pframe_tail*]',
        '$stringify_chain_valid(STATE,STATE.CURRENT,STATE.FRAMES)')
    checks += [*seek('S_body','S_returned',3),
        '$stringify_result_valid(S_returned,n_box,porigin_site,z)',
        '$compound_string_place_nodes(PROPERTY n_owner ptbytes_key) = [HOBJECT n_owner]',
        *seek('S_returned','S_store',4),
        'S_store.TODO = (COMPOUND_STRING_RIGHT (PROPERTY n_owner ptbytes_key) ptbytes_left porigin_site z) :: ptask_store_tail*',
        'ptbytes_left = $ptascii("box")', *completed('S_store',expected),
        '~((HOBJECT n_box) <- S_done.ALLOCATIONS)']
    return checks


def cells(initial, expected, alias):
    checks = ['S_initial = ' + initial, '~S_initial.COMPILESTOP', *seek('S_initial','S_ready',0),
        'S_ready.TODO = (COMPOUND_STRING_PREP (ROOT n_cell) (POBJECT n_box) pvalue_right porigin_site z) :: ptask_tail*',
        '(HCELL n_cell) <- S_ready.ALLOCATIONS',
        '$compound_string_place_nodes(ROOT n_cell) = eps']
    if not alias:
        checks += ['n_cell_fresh = |S_ready.STORE|',
            'S_bad_cell_place = S_ready[.STORE = S_ready.STORE ++ [DEFINED (POBJECT n_box)]][.ALLOCATIONS = S_ready.ALLOCATIONS ++ [HCELL n_cell_fresh]][.TODO = (COMPOUND_STRING_PREP (ROOT n_cell_fresh) (POBJECT n_box) pvalue_right porigin_site z) :: ptask_tail*]',
            '$heap_valid($heap_graph(S_bad_cell_place))',
            '$heap_owners($heap_graph(S_bad_cell_place),HCELL n_cell_fresh) = 0',
            '$location_slot(S_bad_cell_place,ROOT n_cell_fresh) = DEFINED (POBJECT n_box)',
            'S_bad_cell_place.ORIGIN = (porigin_site)',
            '$compound_string_source(S_bad_cell_place,ROOT n_cell_fresh,porigin_site,z)',
            '$user_string_value(S_bad_cell_place,POBJECT n_box)',
            '$heap_subset($value_nodes(POBJECT n_box),S_bad_cell_place.ALLOCATIONS)',
            '$compound_string_right_value(S_bad_cell_place,porigin_site,pvalue_right)',
            '$task_nodes(COMPOUND_STRING_PREP (ROOT n_cell_fresh) (POBJECT n_box) pvalue_right porigin_site z) = $task_nodes(COMPOUND_STRING_PREP (ROOT n_cell) (POBJECT n_box) pvalue_right porigin_site z)',
            '~$compound_string_initial_place(S_bad_cell_place,ROOT n_cell_fresh,porigin_site)',
            '~$call_task_valid(S_bad_cell_place,COMPOUND_STRING_PREP (ROOT n_cell_fresh) (POBJECT n_box) pvalue_right porigin_site z)',
            '~$call_descriptors_valid(S_bad_cell_place)']
    checks += [*seek('S_ready','S_body',2), 'S_body.CURRENT = (pcallcontext_box)',
        'S_body.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (STRINGIFY_RESULT n_box porigin_site z) :: (COMPOUND_STRING_LEFT (ROOT n_cell) pvalue_right porigin_site z) :: ptask_body_tail*',
        'S_owner = $constant_frame_scope(S_body,pframe,pframe_tail*)',
        '$lookup(S_owner.ENV,$ptascii("value")) = eps',
        '$task_nodes(COMPOUND_STRING_LEFT (ROOT n_cell) pvalue_right porigin_site z) = eps']
    if alias:
        checks += ['S_global = $global_table_view(S_body)',
            '$lookup(S_global.ENV,$ptascii("owner")) = (n_owner_cell)',
            'S_body.STORE[n_owner_cell] = DEFINED (POBJECT n_owner)',
            '$objectprops_record_at(S_body.OBJECTPROPS,n_owner) = (pobjectprops)',
            '$property_slot_at(pobjectprops.SLOTS,$ptascii("value")) = (ppropertyslot)',
            'ppropertyslot.STATE = PROP_VALUE (ALIAS n_cell)',
            '(HCELL n_cell) <- S_body.ALLOCATIONS',
            '$heap_owners($heap_graph(S_body),HCELL n_cell) = 1']
    else:
        checks += ['~((HCELL n_cell) <- S_body.ALLOCATIONS)',
            '$heap_owners($heap_graph(S_body),HCELL n_cell) = 0']
    checks += reject('cell_consumer',
        'S_body[.FRAMES = pframe[.TODO = (STRINGIFY_RESULT n_box porigin_site z) :: DISCARD :: ptask_body_tail*] :: pframe_tail*]',
        '$stringify_chain_valid(STATE,STATE.CURRENT,STATE.FRAMES)')
    checks += [*completed('S_body',expected), '~((HOBJECT n_box) <- S_done.ALLOCATIONS)']
    if alias:
        checks += ['$lookup(S_done.ENV,$ptascii("value")) = eps',
                   'S_done.STORE[n_cell] = DEFINED (PSTRING $ptascii("boxx"))']
    else:
        checks += ['$lookup(S_done.ENV,$ptascii("value")) = (n_result)',
                   'S_done.STORE[n_result] = DEFINED (PSTRING $ptascii("boxx"))']
    return checks


def alias(initial, expected):
    return cells(initial, expected, True)


def cv(initial, expected):
    return cells(initial, expected, False)


def recursive(initial, expected):
    return ['S_initial = ' + initial, '~S_initial.COMPILESTOP',
        *seek('S_initial','S_inner',5),
        'S_inner.CURRENT = (pcallcontext_new)',
        'S_inner.FRAMES = pframe_new :: pframe_middle :: pframe_old :: pframe_tail*',
        'pframe_new.TODO = (STRINGIFY_RESULT n_box porigin_site z) :: (COMPOUND_STRING_LEFT (PROPERTY n_owner ptbytes_key) pvalue_right porigin_site z) :: ptask_new_tail*',
        'pframe_old.TODO = (STRINGIFY_RESULT n_box porigin_site z) :: (COMPOUND_STRING_LEFT (PROPERTY n_owner ptbytes_key) pvalue_right porigin_site z) :: ptask_old_tail*',
        'pframe_middle.CONTEXT = (pcallcontext_old)',
        'pcallcontext_new.TARGET = METHOD_TARGET n_box porigin_method',
        'pcallcontext_old.TARGET = METHOD_TARGET n_box porigin_method',
        'pcallcontext_new.CALLSITE = (porigin_site)',
        'pcallcontext_old.CALLSITE = (porigin_site)',
        r'pcallcontext_new.LINE = z /\ pcallcontext_old.LINE = z',
        'S_new_owner = $constant_frame_scope(S_inner,pframe_new,pframe_middle :: pframe_old :: pframe_tail*)',
        'S_old_owner = $constant_frame_scope(S_inner,pframe_old,pframe_tail*)',
        '$stringify_context_frame_valid(S_new_owner,pcallcontext_new,pframe_new)',
        '$stringify_context_frame_valid(S_old_owner,pcallcontext_old,pframe_old)',
        '$compound_string_source(S_old_owner,PROPERTY n_owner ptbytes_key,porigin_site,z)',
        'pframe_bad = pframe_old[.TODO = (STRINGIFY_RESULT n_box porigin_site z) :: DISCARD :: ptask_old_tail*]',
        'S_bad_consumer = S_inner[.FRAMES = pframe_new :: pframe_middle :: pframe_bad :: pframe_tail*]',
        '$heap_valid($heap_graph(S_bad_consumer))',
        '$stringify_selected(S_bad_consumer,METHOD_TARGET n_box porigin_method,porigin_site)',
        '~$stringify_context_frame_valid(S_old_owner,pcallcontext_old,pframe_bad)',
        '~$stringify_chain_valid(S_bad_consumer,S_bad_consumer.CURRENT,S_bad_consumer.FRAMES)',
        '~$call_descriptors_valid(S_bad_consumer)',
        *completed('S_inner',expected),
        '~((HOBJECT n_box) <- S_done.ALLOCATIONS)']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


PREFIX += r'''
dec $review_instance_phase(pstate,nat) : bool
def $review_instance_phase(S,0) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.LEXICAL_CLASS =/= pcallcontext.CALLED_CLASS
  -- if S.TODO = (ASSIGN_ARRAY pbase z b) :: ptask_tail*
  -- if S.RESULT = KNOWN (PINT 9)
def $review_instance_phase(S,1) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (ASSIGN_ARRAY pbase z b) :: ptask_tail*
  -- if S.RESULT = KNOWN (PINT 2)
def $review_instance_phase(S,2) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (ASSIGN_ARRAY pbase z b) :: ptask_tail*
  -- if S.RESULT = KNOWN (PINT 3)
def $review_instance_phase(S,3) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (UPDATE_PREP INCREMENT b z) :: ptask_tail*
def $review_instance_phase(S,n) = false -- otherwise
dec $review_instance_terminal(pstate) : bool
def $review_instance_terminal(S) = (S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
dec $review_instance_seek(pstate,nat,nat) : pstate
def $review_instance_seek(S,n_phase,n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $review_instance_seek(S,n_phase,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $review_instance_phase(S,n_phase)
def $review_instance_seek(S,n_phase,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$review_instance_phase(S,n_phase)
  -- if n = 0 \/ $review_instance_terminal(S)
def $review_instance_seek(S,n_phase,n) = $review_instance_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_phase,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$review_instance_phase(S,n_phase) /\ ~$review_instance_terminal(S) /\ $(n > 0)
'''

def primitive_seek(parent, state, phase, valid):
    return [f'{state}_found = $review_instance_seek({parent},{phase},2048)',
            fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$review_instance_phase({state},{phase})', *valid(state)]

def permission_primitive(initial, expected, valid, completed):
    return ['S_initial = ' + initial, '~S_initial.COMPILESTOP',
        *primitive_seek('S_initial', 'S_store', 0, valid),
        'S_store.CURRENT = (pcallcontext)',
        'S_store.TODO = (ASSIGN_ARRAY pbase z b) :: ptask_tail*',
        'pbase = BASE_PROPERTY_PENDING (BASE_VALUE (VARIABLE ptbytes_cv z_cv)) (KNOWN (PSTRING ptbytes_name)) z_receiver',
        r'ptbytes_cv = $ptascii("target") /\ ptbytes_name = $ptascii("x")',
        '$lookup(S_store.ENV,$ptascii("target")) = (n_target_cell)',
        'S_store.STORE[n_target_cell] = DEFINED (POBJECT n_target)',
        'S_store.OBJECTS[n_target] = INSTANCE porigin_owner',
        '$class_named(S_store.CLASSNAMES,$ptascii("unrelated")) = (porigin_called)',
        'porigin_owner =/= porigin_called',
        'pcallcontext.LEXICAL_CLASS = (porigin_owner)',
        'pcallcontext.CALLED_CLASS = (porigin_called)',
        'pcallcontext.RECEIVER = (n_receiver)',
        'n_receiver =/= n_target',
        'S_store.OBJECTS[n_receiver] = INSTANCE porigin_called',
        '$property_instance_set_desc(S_store,n_target,$ptascii("x")) = (ppropertydesc)',
        'ppropertydesc.SETVISIBILITY = (PROPERTY_PRIVATE)',
        '$property_resolve(S_store,n_target,$ptascii("x")) = PROPERTY_ACCESS $ptascii("x")',
        '$location_slot(S_store,PROPERTY n_target $ptascii("x")) = DEFINED (PINT 1)',
        '$class_static_set_allowed(S_store,ppropertydesc)',
        '~$property_set_denied(S_store,n_target,$ptascii("x"))',
        '$($heap_owners($heap_graph(S_store),HOBJECT n_target) > 0)',
        'pbase_wrong = BASE_PROPERTY_PENDING (BASE_VALUE (VARIABLE $ptascii("wrong") z_cv)) (KNOWN (PSTRING ptbytes_name)) z_receiver',
        'S_bad_name = S_store[.TODO = (ASSIGN_ARRAY pbase_wrong z b) :: ptask_tail*]',
        '$heap_valid($heap_graph(S_bad_name))',
        '~$property_pending_assign_valid(S_bad_name,pbase_wrong,z,b)',
        '~$call_descriptors_valid(S_bad_name)',
        'pbase_line = BASE_PROPERTY_PENDING (BASE_VALUE (VARIABLE ptbytes_cv $(z_cv + 1))) (KNOWN (PSTRING ptbytes_name)) z_receiver',
        'S_bad_line = S_store[.TODO = (ASSIGN_ARRAY pbase_line z b) :: ptask_tail*]',
        '$heap_valid($heap_graph(S_bad_line))',
        '~$property_pending_assign_valid(S_bad_line,pbase_line,z,b)',
        '~$call_descriptors_valid(S_bad_line)',
        'S_bad_scope = S_store[.CURRENT = (pcallcontext[.LEXICAL_CLASS = (porigin_called)])]',
        '$heap_valid($heap_graph(S_bad_scope))',
        '~$call_current_valid(S_bad_scope)',
        '~$call_descriptors_valid(S_bad_scope)',
        '$property_set_denied(S_bad_scope,n_target,$ptascii("x"))',
        '$class_static_set_message(S_bad_scope,ppropertydesc,$ptascii("modify")) = $ptascii("Cannot modify private(set) property Owner::$x from scope Unrelated")',
        'S_written_found = $drive_steps(S_store,1)',
        r'S_written_found.COMPLETION = NORMAL \/ S_written_found.COMPLETION = BUDGET',
        'S_written = S_written_found[.COMPLETION = NORMAL]',
        '$location_slot(S_written,PROPERTY n_target $ptascii("x")) = DEFINED (PINT 9)',
        *valid('S_written'), *completed('S_written', expected)]

def interiors_primitive(initial, expected, valid, completed):
    return ['S_initial = ' + initial, '~S_initial.COMPILESTOP',
        *primitive_seek('S_initial', 'S_raw', 1, valid),
        '$lookup(S_raw.ENV,$ptascii("o")) = (n_holder_cell)',
        'S_raw.STORE[n_holder_cell] = DEFINED (POBJECT n_holder)',
        '$objectprops_record_at(S_raw.OBJECTPROPS,n_holder) = (pobjectprops)',
        '$property_slot_at(pobjectprops.SLOTS,$ptascii("box")) = (ppropertyslot)',
        'ppropertyslot.STATE = PROP_VALUE (DIRECT (POBJECT n_raw))',
        '$property_instance_set_desc(S_raw,n_holder,$ptascii("box")) = (ppropertydesc)',
        '$property_set_denied(S_raw,n_holder,$ptascii("box"))',
        '$property_instance_raw_object(S_raw,n_holder,$ptascii("box"))',
        'S_raw_read = $property_receiver_fetch(S_raw,BASE_PROPERTY (POBJECT n_holder) $ptascii("box"),PPW,1)',
        'S_raw_read.COMPLETION = NORMAL',
        'S_raw_read.RESULT = KNOWN (POBJECT n_raw)',
        'S_whole = $property_store_key(S_raw,n_holder,$ptascii("box"),POBJECT n_raw,1)',
        'S_whole.COMPLETION = THROWN "Error" $ptascii("Cannot modify private(set) property Holder::$box from global scope") 1',
        'S_whole.OBJECTPROPS = S_raw.OBJECTPROPS',
        'S_ref = $reference_acquire(S_raw,BASE_PROPERTY (POBJECT n_holder) $ptascii("box"),1)',
        'S_ref.COMPLETION = THROWN "Error" $ptascii("Cannot assign by reference to overloaded object") 1',
        r'S_ref.PROPREFS = S_raw.PROPREFS /\ S_ref.STORE = S_raw.STORE',
        *primitive_seek('S_raw', 'S_alias', 2, valid),
        '$objectprops_record_at(S_alias.OBJECTPROPS,n_holder) = (pobjectprops_alias)',
        '$property_slot_at(pobjectprops_alias.SLOTS,$ptascii("box")) = (ppropertyslot_alias)',
        'ppropertyslot_alias.STATE = PROP_VALUE (ALIAS n_alias)',
        'S_alias.STORE[n_alias] = DEFINED (POBJECT n_aliased_object)',
        '$propref_at(S_alias.PROPREFS,n_alias) = (ppropref)',
        '$propref_source_present(S_alias.PROPREFS,n_alias,OBJECT_PROP_SOURCE n_holder $ptascii("box") ppropertydesc.ORIGIN)',
        '~$property_instance_raw_object(S_alias,n_holder,$ptascii("box"))',
        'S_alias_read = $property_receiver_fetch(S_alias,BASE_PROPERTY (POBJECT n_holder) $ptascii("box"),PPW,1)',
        'S_alias_read.COMPLETION = THROWN "Error" $ptascii("Cannot indirectly modify private(set) property Holder::$box from global scope") 1',
        r'S_alias_read.OBJECTPROPS = S_alias.OBJECTPROPS /\ S_alias_read.STORE = S_alias.STORE',
        '$($heap_owners($heap_graph(S_alias),HCELL n_alias) > 0)',
        '$($heap_owners($heap_graph(S_alias),HOBJECT n_aliased_object) > 0)',
        *completed('S_alias', expected)]

def increment_primitive(initial, expected, valid, completed):
    return ['S_initial = ' + initial, '~S_initial.COMPILESTOP',
        *primitive_seek('S_initial', 'S_update', 3, valid),
        'S_update.TODO = (UPDATE_PREP INCREMENT b z) :: ptask_tail*',
        '$lookup(S_update.ENV,$ptascii("o")) = (n_holder_cell)',
        'S_update.STORE[n_holder_cell] = DEFINED (POBJECT n_holder)',
        '$location_slot(S_update,PROPERTY n_holder $ptascii("box")) = DEFINED (POBJECT n_box)',
        '$property_set_denied(S_update,n_holder,$ptascii("box"))',
        'S_acquired = $rw_base(S_update,S_update.BASE,STRINGINCDEC,z)',
        'S_acquired.COMPLETION = NORMAL',
        'S_acquired.LOCATION = PROPERTY n_holder $ptascii("box")',
        'S_error = $throwable_materialize($update_acquired(S_acquired,INCREMENT,b,z))',
        'S_error.COMPLETION = THROWING n_error',
        '$object_name(S_error,n_error) = $ptascii("Error")',
        '$throwable_field(S_error,n_error,"message") = PSTRING $ptascii("Cannot modify private(set) property Holder::$box from global scope")',
        '$throwable_previous_id(S_error,n_error) = (n_previous)',
        'n_previous =/= n_error',
        '$object_name(S_error,n_previous) = $ptascii("TypeError")',
        '$throwable_field(S_error,n_previous,"message") = PSTRING $ptascii("Cannot increment Box")',
        '$throwable_previous_id(S_error,n_previous) = eps',
        '$heap_valid($heap_graph(S_error))',
        '$heap_owners($heap_graph(S_error),HOBJECT n_previous) = 1',
        '$location_slot(S_error,PROPERTY n_holder $ptascii("box")) = DEFINED (POBJECT n_box)',
        *completed('S_update', expected)]

def permission(initial, expected):
    return permission_primitive(initial, expected, valid, completed)

def interiors(initial, expected):
    return interiors_primitive(initial, expected, valid, completed)

def increment(initial, expected):
    return increment_primitive(initial, expected, valid, completed)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--freeze', type=Path)
    parser.add_argument('--group', choices=['permission','interiors','increment','private','alias','cv','recursive'], required=True)
    parser.add_argument('--elaborate-only', action='store_true')
    args = parser.parse_args()
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    names = {'permission':'setter-rebound-closure-lexical-authority',
             'interiors':'setter-object-interior-raw-versus-alias',
             'increment':'setter-object-increment-previous',
             'private':'setter-concat-private-reader-scope',
             'alias':'setter-concat-alias-destination-core',
             'cv':'setter-concat-global-destination-unset',
             'recursive':'setter-concat-recursive-same-consumer'}
    name = names[args.group]
    original_bytes = CASES[name]
    expected = EXPECTED[name]
    before = cross.snapshot(args.freeze)
    out = Path(tempfile.mkdtemp(prefix='instance-protocol-' + args.group + '-', dir=OWN))
    source = out/'source.php'; source.write_bytes(original_bytes)
    source_before = sha(source)
    report = {'passed':False,'before':before,'source':str(source),'source_sha256':source_before,
              'profile':cross.invoke.types.PROFILE,'mode':'unused' if args.elaborate_only else 'source-reached',
              'group':args.group,'runner_mode':'AL'}
    print(out,flush=True)
    frontend = adapter = None
    try:
        frontend = Worker([str(ROOT/'.tools/php/bin/php'),'-n',*cross.invoke.types.FLAGS,'-d',
            'extension='+str(ROOT/'.tools/php-file.so'),str(ROOT/'frontend/worker.php')],out/'frontend')
        adapter = Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)],out/'adapter')
        parsed = frontend.request({'op':'parse','source':base64.b64encode(source.read_bytes()).decode()})
        assert parsed['accepted'] is True
        checked = adapter.request({'op':'check','ast':parsed['ast'],'fixture':True})
        assert checked['ok'] is True
        initial = '$php_run(program_source,0,'+json.dumps(base64.b64encode(os.fsencode(source)).decode())+')'
        clauses = ['program_source = '+checked['fixture'],*globals()[args.group](initial,expected)]
        (out/'assertions.json').write_text(json.dumps(clauses,indent=2)+'\n')
        fixture = out/'protocol.watsup'
        fixture.write_text(PREFIX+'dec $body() : bool\ndef $body() = true\n'+''.join('  -- if '+c+'\n' for c in clauses)+'\ndec $main() : bool\ndef $main() = '+('true' if args.elaborate_only else '$body()')+'\n')
        modules = json.loads((ROOT/'spec/semantics/modules.json').read_text())
        result = cross.invoke.process([str(ROOT/'tests/semantics/_build/default/numeric_runner.exe'),
            *[str(ROOT/p) for p in modules],str(fixture)],out/'numeric',120,ROOT)
        assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
        report.update(passed=True,assertions=len(clauses),fixture_sha256=sha(fixture),
            state_assertions_evaluated=0 if args.elaborate_only else len(clauses),
            unused_body_assertions=len(clauses) if args.elaborate_only else 0)
    except BaseException as error:
        report['failure'] = {'type':type(error).__name__,'message':str(error)}
        raise
    finally:
        if adapter: adapter.close()
        if frontend: frontend.close()
        report['after'] = cross.snapshot(args.freeze)
        report['source_unchanged'] = source_before == sha(source)
        report['passed'] = report['passed'] and report['before'] == report['after'] and report['source_unchanged']
        (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
        print(out/'report.json',report['passed'],flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()
