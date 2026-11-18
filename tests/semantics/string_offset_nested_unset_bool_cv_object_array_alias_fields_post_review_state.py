#!/usr/bin/env python3
"""Independent shared array ALIAS fields, continuations and hidden edges."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import string_offset_nested_unset_bool_cv_object_scalar_fields_post_review_state as prior
import string_offset_nested_unset_bool_cv_object_array_alias_fields_post_cases as cases
from string_offset_nested_unset_bool_cv_object_array_fields_post_review_state import TYPED_PROGRAM

INDEX = 0
PRELAW = False
PART = 'all'
FRONT = prior.front
PREFIX = prior.PREFIX

UPDATE_PROGRAM = '(PROGRAM ([(NStmtExpression ((NExprPreInc ((NExprVariable ((BYTES ("cGF5bG9hZA=="))) ([(MendFilePos (15)), (MendLine (1)), (MendTokenPos (2)), (MstartFilePos (8)), (MstartLine (1)), (MstartTokenPos (2))]))) ([(MendFilePos (15)), (MendLine (1)), (MendTokenPos (2)), (MstartFilePos (6)), (MstartLine (1)), (MstartTokenPos (1))]))) ([(MendFilePos (16)), (MendLine (1)), (MendTokenPos (3)), (MstartFilePos (6)), (MstartLine (1)), (MstartTokenPos (1))]))]))'


def fields():
    return '[' + ', '.join(prior.slot('$ptascii("' + name + '")', '',
        state='PROP_VALUE (ALIAS n_payload)') for name in ('left', 'right')) + ']'


def front(program, path):
    prior.INDEX, prior.cases = INDEX, cases
    checks = FRONT(program, path)
    old = prior.fields(7, 'true', 'old', 4609434218613702656)
    assert sum(check.count(old) for check in checks) == 2
    checks = [check.replace(old, fields()).replace(
        '$node_children(S_R, HOBJECT n_object) = eps',
        '$node_children(S_R, HOBJECT n_object) = [HCELL n_payload, HCELL n_payload]').replace(
        '$property_release_nodes(ppropertyslot_before*) = eps',
        '$property_release_nodes(ppropertyslot_before*) = [HCELL n_payload, HCELL n_payload]')
        for check in checks]
    checks += ['$lookup(S_R.ENV, $ptascii("payload")) = (n_payload)',
        'n_payload =/= n_key', 'n_payload =/= n_alias',
        '$call_reference_operand_valid(S_R, REFERENCE n_payload)',
        'S_R.STORE[n_payload] = DEFINED (PARRAY n_initial)',
        '$(n_initial < |S_R.ARRAYS|)', 'n_initial =/= n_array', 'n_initial =/= n_middle',
        'S_R.ARRAYS[n_initial].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 11)), ENTRY (KINT 1) (ALIAS n_field)]',
        '$lookup(S_R.ENV, $ptascii("outside")) = (n_outside)',
        'n_outside =/= n_payload', 'n_outside =/= n_alias', 'n_outside =/= n_key',
        'S_R.STORE[n_outside] = DEFINED (PARRAY n_initial)',
        '$lookup(S_R.ENV, $ptascii("fieldValue")) = (n_field)',
        'n_field =/= n_payload', 'n_field =/= n_outside',
        'n_field =/= n_alias', 'n_field =/= n_key',
        'S_R.STORE[n_field] = DEFINED (PINT 7)',
        '$literal_reference_plain_cell(S_R, n_field)',
        '$node_children(S_R, HCELL n_payload) = [HARRAY n_initial]',
        '$node_children(S_R, HCELL n_outside) = [HARRAY n_initial]',
        '$node_children(S_R, HARRAY n_initial) = [HCELL n_field]',
        '$node_children(S_R, HCELL n_field) = eps',
        '$heap_member(HCELL n_payload, $heap_prune(H_saved).NODES)',
        '$heap_member(HARRAY n_initial, $heap_prune(H_saved).NODES)',
        '$heap_member(HCELL n_field, $heap_prune(H_saved).NODES)',
        'n_payload_roots = $heap_count(HCELL n_payload, H_saved.ROOTS)',
        '$(n_payload_roots > 0)',
        '$heap_edge_owners(HCELL n_payload, H_saved.EDGES, [HOBJECT n_object]) = 2',
        '$heap_edge_owners(HCELL n_payload, H_saved.EDGES, H_saved.NODES) = 2',
        '$heap_owners(H_saved, HCELL n_payload) = $(n_payload_roots + 2)',
        '$heap_edge_owners(HARRAY n_initial, H_saved.EDGES, [HCELL n_payload]) = 1',
        '$heap_edge_owners(HARRAY n_initial, H_saved.EDGES, [HCELL n_outside]) = 1',
        '$heap_owners(H_saved, HARRAY n_initial) = 2',
        'n_field_roots = $heap_count(HCELL n_field, H_saved.ROOTS)',
        '$(n_field_roots > 0)',
        '$heap_edge_owners(HCELL n_field, H_saved.EDGES, [HARRAY n_initial]) = 1',
        '$heap_owners(H_saved, HCELL n_field) = $(n_field_roots + 1)',
        '~$literal_reference_plain_cell(S_R, n_payload)',
        '~$string_read_array_string_cell(S_R, n_payload)',
        '$propref_at(S_R.PROPREFS, n_payload) = eps',
        '$reference_coercion_at(S_R.REFCOERCIONS, n_payload) = eps',
        '$parameter_backing_at(S_R.PARAMETERBACKINGS, n_payload) = eps']
    return checks


def prelaw_conditions(program, path):
    checks = front(program, path)
    resume = 'STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key'
    checks += ['$string_unset_bool_cv_post_field_nodes(S_R, $heap_reach([HCELL n_payload], eps, H_saved.EDGES))',
        '$string_unset_bool_cv_post_array_entries(S_R, eps, [ENTRY (KINT 0) (ALIAS n_payload)])',
        '~$string_unset_bool_cv_post_object_fields(S_R, ppropertyslot_before*)',
        '~$string_unset_bool_cv_post_object(S_R, n_object)',
        '~$string_unset_bool_cv_post_nonempty_array(S_R, n_key)',
        '~$string_unset_bool_cv_post_cell(S_R, n_key_name*, z_key, n_key)',
        '~$string_unset_bool_cv_post_normal_cell(S_R, n_key_name*, z_key, n_key)',
        '$string_unset_cv_range_plan(S_R) = eps']
    if cases.FACTS[tuple(cases.CASES)[INDEX]]['throwing']:
        checks += ['$error_read_discard(S_R, ' + resume + ') = S_R[.COMPLETION = UNSUPPORTED "post-warning Boolean CV conversion"]',
            '$return_discard(S_cut, ERROR_HANDLER_RESULT perrorcall_entered) = S_R[.COMPLETION = UNSUPPORTED "post-warning Boolean CV conversion"]',
            'PhpStep: S_P ~> S_old',
            'S_old = S_R[.COMPLETION = UNSUPPORTED "post-warning Boolean CV conversion"]']
    else:
        checks += ['PhpStep: S_R ~> S_old',
            'S_old = S_R[.TODO = ptask_after*][.COMPLETION = UNSUPPORTED "post-warning Boolean CV conversion"]']
    checks += ['S_old.STORE = S_R.STORE', 'S_old.ARRAYS = S_R.ARRAYS',
        'S_old.OBJECTPROPS = S_R.OBJECTPROPS', 'S_old.OBJECTTABLES = S_R.OBJECTTABLES',
        'S_old.ALLOCATIONS = S_R.ALLOCATIONS', 'S_old.EVENTS = S_R.EVENTS']
    return checks, 0


def post_front(program, path):
    checks = front(program, path)
    resume = 'STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key'
    checks += ['$string_unset_bool_cv_post_object_fields(S_R, ppropertyslot_before*)',
        '$string_unset_bool_cv_post_object(S_R, n_object)',
        '$string_unset_bool_cv_post_nonempty_array(S_R, n_key)',
        '$string_unset_bool_cv_post_cell(S_R, n_key_name*, z_key, n_key)',
        '$string_unset_bool_cv_post_normal_cell(S_R, n_key_name*, z_key, n_key)',
        '$string_unset_bool_cv_post_discard_cell(S_R, n_key_name*, z_key, n_key)',
        '$string_unset_cv_range_plan(S_R) = eps']
    if cases.FACTS[tuple(cases.CASES)[INDEX]]['throwing']:
        checks += ['$error_read_discard(S_R, ' + resume + ') = S_R',
            '$return_discard(S_cut, ERROR_HANDLER_RESULT perrorcall_entered) = S_R',
            'PhpStep: S_P ~> S_next', 'S_next = S_R',
            'S_next.OBJECTS[n_exception] = S_P.OBJECTS[n_exception]',
            'S_public = $drive_steps(S_P, 1)',
            'S_public = S_next[.COMPLETION = BUDGET]']
    else:
        checks += ['PhpStep: S_R ~> S_next',
            'S_next = S_R[.TODO = ptask_after*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)][.LOCATION = NOWHERE][.COMPLETION = THROWN "Error" ($ptascii("Cannot use string offset as an array")) z]',
            'S_public = $drive_steps(S_R, 1)', 'S_public.COMPLETION = BUDGET',
            'S_public.TODO = (THROW_SEARCH n_error) :: ptask_after*',
            'S_public.OBJECTS[n_error] = THROWABLE pthrowable_error',
            'pthrowable_error.KIND = "Error"',
            '$throwable_field(S_public, n_error, "message") = PSTRING ($ptascii("Cannot use string offset as an array"))',
            '$throwable_field(S_public, n_error, "line") = PINT z',
            *prior.base.prior.seek.public('S_public')]
    checks += ['$heap_graph(S_next) = H_saved',
        'S_next.STORE = S_R.STORE', 'S_next.ARRAYS = S_R.ARRAYS',
        'S_next.OBJECTPROPS = S_R.OBJECTPROPS', 'S_next.OBJECTTABLES = S_R.OBJECTTABLES',
        'S_next.ALLOCATIONS = S_R.ALLOCATIONS', 'S_next.EVENTS = S_R.EVENTS',
        '$drive_steps(S_R, 0) = S_R[.COMPLETION = BUDGET]']
    return checks


def completed():
    name = tuple(cases.CASES)[INDEX]
    checks = [r'S_DONE.COMPLETION = NORMAL /\ S_DONE.TODO = eps /\ S_DONE.EXITSTATUS = 0',
        r'S_DONE.CURRENT = eps /\ S_DONE.FRAMES = eps /\ S_DONE.HELD = eps',
        'S_DONE.ERRORHANDLER = S_R.ERRORHANDLER',
        '$lookup(S_DONE.ENV, n_key_name*) = eps',
        '$lookup(S_DONE.ENV, $ptascii("payload")) = eps',
        '$lookup(S_DONE.ENV, $ptascii("fieldValue")) = eps',
        '$lookup(S_DONE.ENV, $ptascii("outside")) = eps',
        '$lookup(S_DONE.ENV, $ptascii("objectAlias")) = eps',
        '~((HCELL n_payload) <- S_DONE.ALLOCATIONS)',
        '~((HCELL n_field) <- S_DONE.ALLOCATIONS)',
        '~((HARRAY n_initial) <- S_DONE.ALLOCATIONS)',
        '~((HCELL n_alias) <- S_DONE.ALLOCATIONS)',
        '~((HOBJECT n_object) <- S_DONE.ALLOCATIONS)',
        '$weakref_get(S_DONE, n_wrapper) = PNULL',
        '$review_cv_outputs(S_DONE.EVENTS) = ' + prior.base.prior.seek.term(cases.OUTPUTS[name]),
        *prior.base.prior.seek.public('S_DONE')]
    if cases.FACTS[name]['throwing']:
        checks += ['S_DONE.OBJECTS[n_exception] = S_R.OBJECTS[n_exception]']
    return checks


def core(program, path):
    checks = post_front(program, path)
    name = tuple(cases.CASES)[INDEX]
    term = prior.base.prior.seek.term
    checks += ['S_C_found = $review_scalar_fields_seek($drive_steps(S_next, 1), ' + term(cases.CHANGED_OUTPUTS[name]) + ', false, 4000)',
        '$review_scalar_fields_at(S_C_found, ' + term(cases.CHANGED_OUTPUTS[name]) + ', false)',
        'S_C = $review_cv_running(S_C_found)', 'S_C.COMPLETION = NORMAL',
        '$lookup(S_C.ENV, $ptascii("payload")) = (n_payload)',
        '$lookup(S_C.ENV, $ptascii("fieldValue")) = (n_field)',
        '$call_reference_operand_valid(S_C, REFERENCE n_payload)',
        'S_C.STORE[n_payload] = DEFINED (PARRAY n_changed)', 'n_changed =/= n_initial',
        'S_C.ARRAYS[n_changed].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 19)), ENTRY (KINT 1) (ALIAS n_field)]',
        'S_C.ARRAYS[n_initial].ITEMS = S_R.ARRAYS[n_initial].ITEMS',
        'S_C.STORE[n_outside] = DEFINED (PARRAY n_initial)',
        'S_C.STORE[n_field] = DEFINED (PINT 9)',
        '$objectprops_at(S_C.OBJECTPROPS, n_object) = (' + fields() + ')',
        '$node_children(S_C, HOBJECT n_object) = [HCELL n_payload, HCELL n_payload]',
        '$node_children(S_C, HCELL n_payload) = [HARRAY n_changed]',
        '$node_children(S_C, HARRAY n_changed) = [HCELL n_field]',
        '$node_children(S_C, HARRAY n_initial) = [HCELL n_field]',
        'H_C = $heap_graph(S_C)', '$heap_valid(H_C)',
        '$heap_edge_owners(HCELL n_payload, H_C.EDGES, [HOBJECT n_object]) = 2',
        '$heap_owners(H_C, HARRAY n_changed) = 1', '$heap_owners(H_C, HARRAY n_initial) = 1',
        '$heap_edge_owners(HCELL n_field, H_C.EDGES, [HARRAY n_changed]) = 1',
        '$heap_edge_owners(HCELL n_field, H_C.EDGES, [HARRAY n_initial]) = 1',
        '$string_unset_bool_cv_post_object(S_C, n_object)',
        'S_B_found = $review_scalar_fields_seek($drive_steps(S_C, 1), ' + term(cases.REBOUND_OUTPUTS[name]) + ', false, 4000)',
        '$review_scalar_fields_at(S_B_found, ' + term(cases.REBOUND_OUTPUTS[name]) + ', false)',
        'S_B = $review_cv_running(S_B_found)', 'S_B.COMPLETION = NORMAL',
        '$lookup(S_B.ENV, n_key_name*) = (n_key)', 'S_B.ARRAYS[n_array] = parray_saved',
        'S_B.ARRAYS[n_middle] = S_R.ARRAYS[n_middle]',
        '$lookup(S_B.ENV, $ptascii("payload")) = eps',
        '$lookup(S_B.ENV, $ptascii("fieldValue")) = eps',
        '$call_reference_operand_valid(S_B, REFERENCE n_payload)',
        'S_B.STORE[n_payload] = DEFINED (PARRAY n_current)',
        'n_current =/= n_initial', 'n_current =/= n_changed',
        'S_B.ARRAYS[n_current].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 23)), ENTRY (KINT 1) (ALIAS n_field)]',
        'S_B.ARRAYS[n_initial].ITEMS = S_R.ARRAYS[n_initial].ITEMS',
        'S_B.STORE[n_outside] = DEFINED (PARRAY n_initial)',
        'S_B.STORE[n_field] = DEFINED (PINT 13)',
        '$literal_reference_plain_cell(S_B, n_field)',
        '$objectprops_at(S_B.OBJECTPROPS, n_object) = (' + fields() + ')',
        '$node_children(S_B, HOBJECT n_object) = [HCELL n_payload, HCELL n_payload]',
        '$node_children(S_B, HCELL n_payload) = [HARRAY n_current]',
        '~((HARRAY n_changed) <- S_B.ALLOCATIONS)',
        '$lookup(S_B.ENV, $ptascii("objectAlias")) = (n_alias)',
        'S_B.STORE[n_alias] = DEFINED (POBJECT n_after)', 'n_after =/= n_object',
        'S_B.OBJECTS[n_after] = STDINSTANCE',
        '$objectprops_at(S_B.OBJECTPROPS, n_after) = (eps)',
        '$weakref_get(S_B, n_wrapper) = POBJECT n_object',
        '$lookup(S_B.ENV, $ptascii("objectWeakAfter")) = (n_after_weak_cell)',
        'S_B.STORE[n_after_weak_cell] = DEFINED (POBJECT n_after_wrapper)',
        '$weakref_at(S_B, n_after_wrapper) = (WEAKREFERENCE (n_after))',
        '$weakref_get(S_B, n_after_wrapper) = POBJECT n_after',
        'H_B = $heap_graph(S_B)', '$heap_valid(H_B)',
        '$heap_count(HCELL n_payload, H_B.ROOTS) = 0',
        '$heap_edge_owners(HCELL n_payload, H_B.EDGES, [HOBJECT n_object]) = 2',
        '$heap_owners(H_B, HCELL n_payload) = 2',
        '$heap_owners(H_B, HARRAY n_current) = 1', '$heap_owners(H_B, HARRAY n_initial) = 1',
        '$heap_count(HCELL n_field, H_B.ROOTS) = 0', '$heap_owners(H_B, HCELL n_field) = 2',
        '$heap_edge_owners(HOBJECT n_object, H_B.EDGES, [HARRAY n_middle]) = 1',
        '$heap_edge_owners(HOBJECT n_after, H_B.EDGES, [HCELL n_alias]) = 1',
        '$heap_owners(H_B, HOBJECT n_object) = 1', '$heap_owners(H_B, HOBJECT n_after) = 1',
        '$string_unset_bool_cv_post_object(S_B, n_object)',
        'S_RET_found = $review_scalar_fields_seek($drive_steps(S_B, 1), ' + term(cases.RETAINED_OUTPUTS[name]) + ', true, 4000)',
        '$review_scalar_fields_at(S_RET_found, ' + term(cases.RETAINED_OUTPUTS[name]) + ', true)',
        'S_RET = $review_cv_running(S_RET_found)', 'S_RET.COMPLETION = NORMAL',
        '$lookup(S_RET.ENV, n_key_name*) = eps',
        '~((HOBJECT n_object) <- S_RET.ALLOCATIONS)',
        '~((HCELL n_payload) <- S_RET.ALLOCATIONS)',
        '~((HARRAY n_current) <- S_RET.ALLOCATIONS)',
        '$weakref_get(S_RET, n_wrapper) = PNULL',
        '$weakref_get(S_RET, n_after_wrapper) = POBJECT n_after',
        'S_RET.STORE[n_outside] = DEFINED (PARRAY n_initial)',
        'S_RET.ARRAYS[n_initial].ITEMS = S_R.ARRAYS[n_initial].ITEMS',
        'S_RET.STORE[n_field] = DEFINED (PINT 13)',
        'H_RET = $heap_graph(S_RET)', '$heap_valid(H_RET)',
        '$heap_member(HARRAY n_initial, $heap_prune(H_RET).NODES)',
        '$heap_member(HCELL n_field, $heap_prune(H_RET).NODES)',
        '$heap_owners(H_RET, HARRAY n_initial) = 1',
        '$heap_edge_owners(HARRAY n_initial, H_RET.EDGES, [HCELL n_outside]) = 1',
        '$heap_count(HCELL n_field, H_RET.ROOTS) = 0', '$heap_owners(H_RET, HCELL n_field) = 1',
        'S_OUT_found = $review_scalar_fields_seek($drive_steps(S_RET, 1), ' + term(cases.OUTSIDE_OUTPUTS[name]) + ', true, 4000)',
        '$review_scalar_fields_at(S_OUT_found, ' + term(cases.OUTSIDE_OUTPUTS[name]) + ', true)',
        'S_OUT = $review_cv_running(S_OUT_found)', 'S_OUT.COMPLETION = NORMAL',
        '$lookup(S_OUT.ENV, $ptascii("outside")) = eps',
        '~((HCELL n_outside) <- S_OUT.ALLOCATIONS)',
        '~((HARRAY n_initial) <- S_OUT.ALLOCATIONS)',
        '~((HCELL n_field) <- S_OUT.ALLOCATIONS)',
        '$weakref_get(S_OUT, n_wrapper) = PNULL',
        '$weakref_get(S_OUT, n_after_wrapper) = POBJECT n_after',
        *prior.base.prior.seek.public('S_OUT'),
        'S_DONE = $drive_steps(S_OUT, 4000)', *completed(),
        '~((HARRAY n_changed) <- S_DONE.ALLOCATIONS)',
        '~((HARRAY n_current) <- S_DONE.ALLOCATIONS)',
        '~((HOBJECT n_after) <- S_DONE.ALLOCATIONS)',
        '$weakref_get(S_DONE, n_after_wrapper) = PNULL']
    return checks


def guards(program, path):
    checks = front(program, path)
    reached = len(checks)
    checks += ['$string_unset_bool_cv_post_object_fields(S_R, ppropertyslot_before*)',
        '$string_unset_bool_cv_post_object(S_R, n_object)']
    for name in ('eps', '$ptascii("123")'):
        slot = prior.slot(name, '', state='PROP_VALUE (ALIAS n_payload)')
        state = 'S_R[.OBJECTPROPS = $objectprops_set(S_R.OBJECTPROPS, n_object, [' + slot + '])]'
        checks += ['$string_unset_bool_cv_post_object(' + state + ', n_object)']
    for slot in (
        prior.slot('$ptascii("bad")', '', '(porigin_site)', 'PROP_VALUE (ALIAS n_payload)'),
        prior.slot('[256]', '', state='PROP_VALUE (ALIAS n_payload)'),
        prior.slot('[0, 65]', '', state='PROP_VALUE (ALIAS n_payload)'),
        prior.slot('[65, 0, 66]', '', state='PROP_VALUE (ALIAS n_payload)'),
        prior.slot('$ptascii("bad")', '', state='PROP_UNSET'),
        prior.slot('$ptascii("bad")', '', state='PROP_INITIAL'),
        prior.slot('$ptascii("bad")', '', state='PROP_DEFERRED porigin_site'),
    ):
        state = 'S_R[.OBJECTPROPS = $objectprops_set(S_R.OBJECTPROPS, n_object, [' + slot + '])]'
        checks += ['~$string_unset_bool_cv_post_object(' + state + ', n_object)']
    duplicate = '[' + ', '.join(prior.slot('$ptascii("same")', '', state='PROP_VALUE (ALIAS n_payload)') for _ in range(2)) + ']'
    checks += ['S_duplicate = S_R[.OBJECTPROPS = $objectprops_set(S_R.OBJECTPROPS, n_object, ' + duplicate + ')]',
        '~$string_unset_bool_cv_post_object(S_duplicate, n_object)',
        '~$string_unset_bool_cv_post_object(S_R[.OBJECTTABLES = {OBJECT n_object, TABLE n_array} :: S_R.OBJECTTABLES], n_object)']
    for state in (
        'S_R[.REFCELLS = $literal_reference_delete(S_R.REFCELLS, n_payload)]',
        'S_R[.ALLOCATIONS = $destruction_node_delete(S_R.ALLOCATIONS, HCELL n_payload)]',
        'S_R[.PROPREFS = {CELL n_payload, SOURCES eps} :: S_R.PROPREFS]',
        'S_R[.REFCOERCIONS = {CELL n_payload, SITE porigin_site, LINE z, VALUE eps} :: S_R.REFCOERCIONS]',
        'S_R[.PARAMETERBACKINGS = {FUNCTION porigin_site, INDEX 0, CELL n_payload, LINE z, VALUE eps} :: S_R.PARAMETERBACKINGS]',
    ):
        checks += ['~$string_unset_bool_cv_post_object(' + state + ', n_object)']
    file = json.dumps(base64.b64encode(b'/derived-array-alias-field-flag.php').decode())
    if INDEX == 0:
        checks += ['S_flag = $php_run(' + UPDATE_PROGRAM + ', 0, ' + file + ')',
            'S_flag.COMPLETION = BUDGET', 'porigin_flag = PORIGIN 0 ([PCINDEX 0, PCFIELD 0])',
            'pupdatewarning_flag = {SITE porigin_flag, OP INCREMENT, POST false, NAME $ptascii("payload"), LINE 1, POINTER UPDATE_CELL n_payload, INPUT (PBOOL false), PENDING eps}',
            'pupdaterestore_flag = {WARNING pupdatewarning_flag, CELL n_payload, WRAPPER eps, VALUE (PARRAY n_initial), CALLER S_R.CURRENT, CONSTCONTEXT S_R.CONSTCONTEXT}',
            'S_hidden = S_R[.SOURCES = S_flag.SOURCES][.CODE = S_flag.CODE][.ORIGIN = (porigin_flag)][.ARRAYS[n_initial].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_object))]][.TODO = [UPDATE_WARNING_COMMIT pupdaterestore_flag]]',
            '$update_warning_source(S_hidden, pupdatewarning_flag)',
            '$update_restore_record_valid(S_hidden, pupdaterestore_flag)',
            '$update_released_cell(S_hidden, n_payload)',
            '~$update_released_cell(S_hidden[.CODE = eps], n_payload)',
            '~$update_released_cell(S_hidden[.SOURCES = eps], n_payload)',
            '$call_reference_operand_valid(S_hidden, REFERENCE n_payload)',
            'S_hidden.STORE[n_payload] = DEFINED (PARRAY n_initial)',
            '$node_children(S_hidden, HCELL n_payload) = eps',
            '$node_children(S_hidden, HARRAY n_initial) = [HOBJECT n_object]',
            'H_hidden = $heap_graph(S_hidden)', '$heap_valid(H_hidden)',
            '$heap_member(HARRAY n_initial, $heap_prune(H_hidden).NODES)',
            '$heap_edge_owners(HARRAY n_initial, H_hidden.EDGES, [HCELL n_outside]) = 1',
            'pnode_hidden* = $heap_reach([HCELL n_payload], eps, H_hidden.EDGES)',
            'pnode_hidden* = [HCELL n_payload]']
    else:
        checks += ['S_flag = $php_run(' + TYPED_PROGRAM + ', 0, ' + file + ')',
            'S_flag.COMPLETION = BUDGET',
            'porigin_flag_function = PORIGIN 0 ([PCINDEX 0])',
            '$function_at($all_functions(S_flag), porigin_flag_function) = (pfunction_flag)',
            'pfunction_flag.SIGNATURE.BYREF',
            'porigin_flag = PORIGIN 0 ([PCINDEX 0, PCFIELD 5, PCINDEX 0, PCFIELD 0, PCINDEX 0])',
            'pcallcontext_flag = {TARGET porigin_flag_function, CACHE eps, DEFAULTRECEIVE eps, WRAPPER eps, INSTANCE eps, RECEIVER eps, LEXICAL_CLASS eps, CALLED_CLASS eps, FUNCTION porigin_flag_function, NAME $ptascii("arrayFieldFlagTyped"), CALLSITE eps, LINE 1, PARAMS eps, ARGC 0, HOLES eps, EXTRA eps, NAMED eps}',
            'prefstringcv_flag = {SOURCE porigin_flag, LINE 1, CELL n_field, OBJECT n_object}',
            'pvalue_flag = PSTRING_CARRIER INTERNED_STRING ($ptascii("flag"))',
            'S_hidden = S_R[.SOURCES = S_flag.SOURCES][.CODE = S_flag.CODE][.FUNCTIONS = S_flag.FUNCTIONS][.CURRENT = (pcallcontext_flag)][.ORIGIN = (porigin_flag)][.STORE[n_field] = DEFINED (POBJECT n_object)][.TODO = [REF_CV_STRING_COPY prefstringcv_flag pvalue_flag, REF_CV_STRING_TEMP prefstringcv_flag]]',
            '$finally_return_pending(S_hidden)', '$reference_return_fetch_valid(S_hidden, 1)',
            '$typed_cv_string_copy_valid(S_hidden, prefstringcv_flag, pvalue_flag)',
            '$typed_cv_string_released_cell(S_hidden, n_field)',
            '~$typed_cv_string_released_cell(S_hidden[.CURRENT = eps], n_field)',
            '~$typed_cv_string_released_cell(S_hidden[.SOURCES = eps], n_field)',
            '$call_reference_operand_valid(S_hidden, REFERENCE n_field)',
            'S_hidden.STORE[n_payload] = DEFINED (PARRAY n_initial)',
            '$node_children(S_hidden, HCELL n_payload) = [HARRAY n_initial]',
            '$node_children(S_hidden, HCELL n_field) = eps',
            'H_hidden = $heap_graph(S_hidden)', '$heap_valid(H_hidden)',
            'pnode_hidden* = $heap_reach([HCELL n_payload], eps, H_hidden.EDGES)',
            '$heap_member(HCELL n_field, pnode_hidden*)']
    checks += ['$heap_member(HCELL n_payload, pnode_hidden*)',
        '~$heap_member(HOBJECT n_object, pnode_hidden*)',
        '$array_float_key_plain_nodes(pnode_hidden*)',
        '~$string_unset_bool_cv_post_field_nodes(S_hidden, pnode_hidden*)',
        '~$string_unset_bool_cv_post_object(S_hidden, n_object)',
        '~$string_unset_bool_cv_post_nonempty_array(S_hidden, n_key)',
        '~$foreach_released_cell(S_hidden, n_payload)']
    return checks, len(checks) - reached


def conditions(program, path):
    if PRELAW:
        return prelaw_conditions(program, path)
    if PART == 'guards':
        return guards(program, path)
    if PART == 'budget':
        return post_front(program, path) + ['S_DONE = $drive_steps(S_P, 3000)', *completed()], 0
    checks = core(program, path)
    if PART == 'all':
        extra, count = guards(program, path)
        checks += extra[-count:]
        return checks, count
    return checks, 0


if __name__ == '__main__':
    PRELAW = '--prelaw' in sys.argv
    if PRELAW:
        sys.argv.remove('--prelaw')
    if '--part' in sys.argv:
        at = sys.argv.index('--part')
        PART = sys.argv[at + 1]
        del sys.argv[at:at + 2]
    assert PART in ('all', 'core', 'budget', 'guards') and (not PRELAW or PART == 'all')
    at = sys.argv.index('--index')
    INDEX = int(sys.argv[at + 1])
    del sys.argv[at:at + 2]
    assert INDEX in (0, 1)
    watched = [Path(__file__), Path(prior.__file__), Path(prior.base.__file__),
        Path(prior.base.prior.__file__), Path(prior.base.prior.seek.__file__),
        Path(prior.base.prior.sl.__file__), Path(cases.__file__),
        Path(__file__).with_name('string_offset_nested_unset_bool_cv_object_array_fields_post_review_state.py'),
        *[prior.base.prior.runner.ROOT / path for path in cases.WATCHED]]
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner = prior.base.prior.runner
    runner.NAME = tuple(cases.CASES)[INDEX]
    runner.OUTPUT = cases.OUTPUTS[runner.NAME]
    runner.cases, runner.conditions = cases, conditions
    runner.PREFIX, runner.recorded = PREFIX, prior.base.prior.sl.recorded
    passed = runner.main()
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = Path(sys.argv[sys.argv.index('--output') + 1]) / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['mode'], report['raw_unset_steps'] = 'SL', 1
    report['part'] = 'prelaw-front' if PRELAW else PART
    report['source_bridge_credit'] = int(passed and not PRELAW and PART == 'budget')
    report['scope'] = ('Independent checked original prefix authenticates the shared property ARRAY cell, outside VALUE owner, embedded scalar REF and exact old Unsupported despite valid physical-root/singleton-array prerequisites; no observer-tail, source or native credit.' if PRELAW else
        'Independent checked original prefix and exact new step followed by complete direct S_P3000/NORMAL/native bytes/final retirement; unique checked-source bridge, public CLI UNRUN.' if PART == 'budget' else
        'Independent exact new step and C/B/R/O source ownership/retirement/native tail; complete direct budget is a separate required cut.' if PART == 'core' else
        'Reached source prefix plus property-domain and compiler-authenticated root UPDATE_ARRAY/typed-COPY descendant hidden-edge controls; source0/native0, no marked-foreach runtime claim.')
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
