#!/usr/bin/env python3
"""Reached Stringable getter cast, original-owner release and pending commit."""
import argparse
import base64
import json
import os
from pathlib import Path
import tempfile

import dynamic_property_warning_sources as sources
import magic_property_get_protocol as get
import magic_property_integer_protocol as integer
import magic_property_scalar_boolean_protocol as boolean
import magic_property_nan_string_protocol as nan_string

cross, ROOT = sources.cross, sources.ROOT
CASES = {group: 'review-property-magic-stringable-string-' + original + '46' for group, original in (
    ('reference-entry', 'reference-kept'), ('reference-ready', 'reference-kept'),
    ('reference-copy', 'reference-kept'), ('reference-drop', 'reference-drop'),
    ('value', 'value'), ('owned', 'owned'), ('source-exact', 'source-conflict'),
    ('source-conflict', 'source-conflict'), ('destructor-throw', 'destructor-throw'),
    ('source-destructor-throw', 'source-destructor-throw'), ('cast-throw', 'cast-throw'),
    ('strict-getter', 'strict-getter'))}
PREFIX = boolean.PREFIX + r'''
def $integer_get_phase(S, 7, n) = true
  -- if S.TODO = (STRINGIFY_RESULT n_object porigin z) :: (PROPERTY_GET_STRING_RESULT ppropertygetstring) :: ptask_tail*
  -- if ppropertygetstring.GET.OBJECT = n
  -- if S.CURRENT = eps /\ S.DESTRUCTION.OPERATIONS = eps
def $integer_get_phase(S, 8, n) = true
  -- if S.TODO = (PROPERTY_GET_STRING_READY ppropertygetstring pvalue) :: ptask_tail*
  -- if ppropertygetstring.GET.OBJECT = n
  -- if S.CURRENT = eps /\ S.DESTRUCTION.OPERATIONS = eps
def $integer_get_phase(S, 9, n) = true
  -- if S.TODO = (PROPERTY_GET_STRING_COPY ppropertygetstring pvalue) :: ptask_tail*
  -- if ppropertygetstring.GET.OBJECT = n
  -- if S.CURRENT = eps /\ S.DESTRUCTION.OPERATIONS = eps
def $integer_get_phase(S, 10, n) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: (PROPERTY_GET_STRING_RESULT ppropertygetstring) :: ptask_tail*
  -- if ppropertygetstring.GET.OBJECT = n
  -- if S.CURRENT = eps /\ S.DESTRUCTION.OPERATIONS = eps
def $integer_get_phase(S, 11, n) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: (PROPERTY_GET_STRING_COPY ppropertygetstring pvalue) :: ptask_tail*
  -- if ppropertygetstring.GET.OBJECT = n
  -- if S.CURRENT = eps /\ S.DESTRUCTION.OPERATIONS = eps
dec $stringable_get_phase(pstate, nat) : bool
def $stringable_get_phase(S, 7) = $integer_get_phase(S, 7, ppropertygetstring.GET.OBJECT)
  -- if S.TODO = (STRINGIFY_RESULT n_object porigin z) :: (PROPERTY_GET_STRING_RESULT ppropertygetstring) :: ptask_tail*
def $stringable_get_phase(S, 10) = $integer_get_phase(S, 10, ppropertygetstring.GET.OBJECT)
  -- if S.TODO = (THROW_SEARCH n_error) :: (PROPERTY_GET_STRING_RESULT ppropertygetstring) :: ptask_tail*
def $stringable_get_phase(S, 11) = $integer_get_phase(S, 11, ppropertygetstring.GET.OBJECT)
  -- if S.TODO = (THROW_SEARCH n_error) :: (PROPERTY_GET_STRING_COPY ppropertygetstring pvalue) :: ptask_tail*
def $stringable_get_phase(S, n) = false -- otherwise
dec $stringable_get_seek(pstate, nat, nat) : pstate
def $stringable_get_seek(S, n_phase, n) = S -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $stringable_get_seek(S, n_phase, n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $stringable_get_phase(S, n_phase)
def $stringable_get_seek(S, n_phase, 0) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$stringable_get_phase(S, n_phase)
def $stringable_get_seek(S, n_phase, n) = $stringable_get_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_phase, $nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$stringable_get_phase(S, n_phase)
  -- if $(n > 0)
'''
SAVED = 'PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("value46"))'


def eval_group(group):
    return 'weak-getter' if group.startswith('reference-') and group != 'reference-drop' else group


def initial(run, eval_checks):
    return ['S_initial = ' + run, '~S_initial.COMPILESTOP', *eval_checks]


def seek_any(parent, state, phase):
    return [f'{state}_found = $stringable_get_seek({parent}, {phase}, 2048)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = {state}_found[.COMPLETION = NORMAL]', f'$stringable_get_phase({state}, {phase})']


def returned(run, source, group, eval_checks):
    line = next(i for i, row in enumerate(source.splitlines(), 1) if b' = $reader->value;' in row)
    return [*initial(run, eval_checks),
        *boolean.later('S_resumed' if eval_checks else 'S_initial', 'S_return', 'ppropertyget', 'ptask_return_tail*', 1),
        f'ppropertyget.LINE = {line}',
        '$property_desc_at($property_layout(S_return, ppropertyget.CLASS, |S_return.CLASSES|), ppropertyget.NAME) = (ppropertydesc_get)',
        'ppropertydesc_get.TYPE = [(PTBRANCH ([PTBUILTIN "string"]))]', 'ppropertydesc_get.READONLY',
        '$objectprops_at(S_return.OBJECTPROPS, n_reader) = (ppropertyslot_all*)',
        '$property_slot_at(ppropertyslot_all*, ppropertyget.NAME) = (ppropertyslot_get)', 'ppropertyslot_get.STATE = PROP_UNSET',
        'S_global = $global_table_view(S_return)', '$lookup(S_global.ENV, $ptascii("returnCell")) = (n_cell)',
        'S_return.RESULT = REFERENCE n_cell', 'S_return.STORE[n_cell] = DEFINED (POBJECT n_payload)',
        '$property_get_method(S_return, n_reader) = (pmethoddesc_get)',
        f'pmethoddesc_get.FUNCTION.CODE.STRICT = {str(group == "strict-getter").lower()}',
        'ppropertyget.SITE = PORIGIN n_caller pcpath_caller', '$code_at(S_return.CODE, n_caller) = (pcode_caller)',
        f'pcode_caller.STRICT = {str(group.startswith("reference-") and group != "reference-drop").lower()}',
        'S_return.STRINGDATA = eps']


def entry():
    return ['$property_get_string_capture(S_return, ppropertyget) = (ppropertygetstring)',
        'ppropertygetstring = {GET ppropertyget, INPUT REFERENCE n_cell, OBJECT n_payload, SOURCES eps, OWNER (|S_return.FRAMES|), CALLER S_return.CURRENT, TAIL ptask_return_tail*}',
        '$typed_conversion_at(S_return, ppropertydesc_get.TYPE, POBJECT n_payload, false) = TYPEDEPENDENT "user object string conversion"',
        'S_return.OBJECTS[n_payload] = INSTANCE porigin_payload',
        '$effective_method(S_return, porigin_payload, $ptascii("__toString"), |S_return.CLASSES|) = (pmethoddesc_cast)',
        'S_call = $property_get_complete(S_return, ppropertyget, S_return.RESULT)',
        'S_call = S_return[.TODO = (CALL_ARGS (METHOD_TARGET n_payload pmethoddesc_cast.FUNCTION.ORIGIN) eps 0 eps (ppropertyget.SITE) ppropertyget.LINE) :: (STRINGIFY_RESULT n_payload ppropertyget.SITE ppropertyget.LINE) :: (PROPERTY_GET_STRING_RESULT ppropertygetstring) :: ptask_return_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        '$property_get_string_valid(S_call, ppropertygetstring)',
        '$stringify_site_valid(S_call, ppropertyget.SITE, ppropertyget.LINE)',
        '$task_nodes(PROPERTY_GET_STRING_RESULT ppropertygetstring) = [HOBJECT n_reader, HCELL n_cell]',
        '$heap_owners($heap_graph(S_call), HOBJECT n_payload) = 3',
        '$heap_owners($heap_graph(S_call), HOBJECT n_reader) = 2',
        *nan_string.budget('S_return', 'S_call'),
        '$property_get_verify(S_return, ppropertyget, S_return.RESULT) = S_return[.COMPLETION = UNSUPPORTED "magic getter property type coercion"]',
        'S_nonactual = $property_get_complete(S_return, ppropertyget, KNOWN (PSTRING ($ptascii("independent46"))))',
        'S_nonactual = S_return[.TODO = (PROPERTY_GET_COPY ppropertyget (REFERENCE n_cell)) :: ptask_return_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]']


def cast_return(run, group, eval_checks):
    constrained = group.startswith('source-')
    return [*initial(run, eval_checks),
        *seek_any('S_resumed' if eval_checks else 'S_initial', 'S_cast', 7),
        'S_cast.TODO = (STRINGIFY_RESULT n_payload porigin_site z_site) :: (PROPERTY_GET_STRING_RESULT ppropertygetstring) :: ptask_return_tail*',
        'ppropertyget = ppropertygetstring.GET', 'n_reader = ppropertyget.OBJECT',
        'n_payload = ppropertygetstring.OBJECT', 'porigin_site = ppropertyget.SITE', 'z_site = ppropertyget.LINE',
        '$integer_get_phase(S_cast, 7, n_reader)', *get.valid('S_cast'),
        'ppropertygetstring.TAIL = ptask_return_tail*', 'ppropertygetstring.OWNER = |S_cast.FRAMES|',
        'ppropertygetstring.CALLER = S_cast.CURRENT',
        'S_global = $global_table_view(S_cast)', '$lookup(S_global.ENV, $ptascii("returnCell")) = (n_cell)',
        'ppropertygetstring.INPUT = ' + ('KNOWN (POBJECT n_payload)' if group == 'value' else 'REFERENCE n_cell'),
        'ppropertygetstring.SOURCES = ' + ('([pproptypesource_first])' if constrained else 'eps'),
        'S_cast.STORE[n_cell] = DEFINED (' + (nan_string.string('changed46') if constrained else 'POBJECT n_payload') + ')',
        'pvalue_saved = ' + SAVED, 'S_cast.RESULT = KNOWN pvalue_saved',
        'S_cast.STRINGDATA = [($ptascii("value46"))]', '$string_carrier_valid(S_cast, pvalue_saved)',
        '$property_get_string_valid(S_cast, ppropertygetstring)',
        '$heap_owners($heap_graph(S_cast), HOBJECT n_payload) = ' + str(3 if group == 'value' else 2),
        '$trace_slot(S_global, S_global.ENV, $ptascii("casts")) = PINT 1',
        '$trace_slot(S_global, S_global.ENV, $ptascii("readerDrops")) = PINT 0']


def ready():
    return ['S_ready_raw = S_cast[.TODO = (PROPERTY_GET_STRING_READY ppropertygetstring pvalue_saved) :: ptask_return_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        '$stringify_return_state(S_cast, PROPERTY_GET_STRING_RESULT ppropertygetstring, pvalue_saved, ptask_return_tail*) = S_ready_raw',
        *nan_string.budget('S_cast', 'S_ready_raw'), *integer.seek('S_cast', 'S_ready', 8),
        '$property_get_string_ready_valid(S_ready, ppropertygetstring, pvalue_saved)',
        '$task_nodes(PROPERTY_GET_STRING_READY ppropertygetstring pvalue_saved) = $task_nodes(PROPERTY_GET_STRING_RESULT ppropertygetstring)',
        'S_ready.STORE = S_cast.STORE', 'S_ready.STRINGDATA = S_cast.STRINGDATA',
        '$heap_owners($heap_graph(S_ready), HOBJECT n_payload) = 1',
        'S_release_raw = S_ready[.TODO = (PROPERTY_GET_STRING_COPY ppropertygetstring pvalue_saved) :: ptask_return_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        '$property_get_string_copy_valid(S_release_raw, ppropertygetstring, pvalue_saved)',
        *nan_string.budget('S_ready', 'S_release_raw')]


def guards():
    checks = ['ppropertyget.DECL = (ppropertyid)']
    for label, field, value in [('input', 'INPUT', 'KNOWN (PINT 7)'), ('cell', 'INPUT', 'REFERENCE (|S_ready.STORE|)'),
        ('object', 'OBJECT', '$(n_payload + 1)'), ('owner', 'OWNER', '$(|S_ready.FRAMES| + 1)'),
        ('tail', 'TAIL', 'eps'), ('line', 'GET', 'ppropertyget[.LINE = $(ppropertyget.LINE + 1)]'),
        ('source', 'SOURCES', '([OBJECT_PROP_SOURCE n_reader ppropertyget.NAME ppropertyid])')]:
        checks += [f'ppropertygetstring_bad_{label} = ppropertygetstring[.{field} = {value}]',
            f'S_bad_{label} = S_ready[.TODO = (PROPERTY_GET_STRING_READY ppropertygetstring_bad_{label} pvalue_saved) :: ptask_return_tail*]',
            f'~$property_get_string_ready_valid(S_bad_{label}, ppropertygetstring_bad_{label}, pvalue_saved)',
            f'S_copy_bad_{label} = S_release_raw[.TODO = (PROPERTY_GET_STRING_COPY ppropertygetstring_bad_{label} pvalue_saved) :: ptask_return_tail*]',
            f'~$property_get_string_copy_valid(S_copy_bad_{label}, ppropertygetstring_bad_{label}, pvalue_saved)']
    checks += ['~$property_get_string_ready_valid(S_ready[.ORIGIN = (ppropertyget.METHOD)], ppropertygetstring, pvalue_saved)',
        '~$property_get_string_ready_valid(S_ready[.RESULT = KNOWN pvalue_saved], ppropertygetstring, pvalue_saved)',
        '~$property_get_string_ready_valid(S_ready[.BASE = BASE_VALUE (REFERENCE n_cell)], ppropertygetstring, pvalue_saved)',
        'S_parameter = S_ready[.PARAMETERBACKINGS = [{FUNCTION ppropertyget.METHOD, INDEX 0, CELL n_cell, LINE ppropertyget.LINE, VALUE ($ptascii("string"))}]]',
        '~$property_get_string_ready_valid(S_parameter, ppropertygetstring, pvalue_saved)',
        'pvalue_forged = PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("value46"))',
        'S_forged = S_ready[.TODO = (PROPERTY_GET_STRING_READY ppropertygetstring pvalue_forged) :: ptask_return_tail*]',
        '~$property_get_string_ready_valid(S_forged, ppropertygetstring, pvalue_forged)',
        'pvalue_plain = PSTRING ($ptascii("value46"))',
        'S_plain = S_ready[.TODO = (PROPERTY_GET_STRING_READY ppropertygetstring pvalue_plain) :: ptask_return_tail*]',
        '$property_get_string_ready_valid(S_plain, ppropertygetstring, pvalue_plain)',
        'S_growth = S_ready[.STRINGDATA = S_ready.STRINGDATA ++ [($ptascii("unrelated46"))]]',
        '$property_get_string_ready_valid(S_growth, ppropertygetstring, pvalue_saved)',
        '~$property_get_string_copy_valid(S_release_raw[.RESULT = KNOWN pvalue_saved], ppropertygetstring, pvalue_saved)',
        '~$property_get_string_copy_valid(S_release_raw[.BASE = BASE_VALUE (REFERENCE n_cell)], ppropertygetstring, pvalue_saved)']
    return checks


def payload(parent):
    return [*integer.seek(parent, 'S_payload', 4, 'n_payload'),
        'S_payload.CURRENT = (pcallcontext_payload)',
        '$destructor_context_call(pcallcontext_payload, S_payload.CURRENT, S_payload.FRAMES) = (pdestructorcall_payload)',
        'pdestructorcall_payload.OPERATION = (pdestructionoperation_payload)',
        'pdestructionoperation_payload.SOURCE = PROPERTY_GET_STRING_READY ppropertygetstring pvalue_saved',
        'S_payload.STORE[n_cell] = DEFINED (POBJECT n_payload)',
        '$typed_cv_string_released_cell(S_payload, n_cell)', '$node_children(S_payload, HCELL n_cell) = eps']


def copied(parent):
    return [*integer.seek(parent, 'S_object_released', 9),
        'S_object_released.TODO = (PROPERTY_GET_STRING_COPY ppropertygetstring pvalue_saved) :: ptask_return_tail*',
        '$property_get_string_copy_valid(S_object_released, ppropertygetstring, pvalue_saved)',
        '~((HOBJECT n_payload) <- S_object_released.ALLOCATIONS)',
        'S_object_released.STORE[n_cell] = DEFINED (POBJECT n_payload)',
        '$get_test_output(S_object_released.EVENTS) = $ptascii("C|G|value|T|1/0|L|1|")']


def commit(state, byval=False):
    rv = 'KNOWN pvalue_saved' if byval else 'REFERENCE n_cell'
    written = state + '[.RESULT = KNOWN pvalue_saved]' if byval else state + '[.STORE = $set_cell(' + state + '.STORE, n_cell, DEFINED pvalue_saved)][.RESULT = REFERENCE n_cell]'
    return ['S_written = ' + written,
        f'$property_get_string_commit({state}, ppropertygetstring, pvalue_saved) = S_written',
        'S_finished = S_written[.TODO = (PROPERTY_GET_COPY ppropertyget (' + rv + ')) :: ptask_return_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        f'$property_get_string_finish({state}, ppropertygetstring, pvalue_saved) = S_finished',
        *nan_string.budget(state, 'S_finished')]


def receive(parent, value, cells=2):
    return [clause.replace('n_return_cell', 'n_cell') for clause in boolean.receive(parent, 'ppropertyget', 'ptask_copy_tail*', value, cells=cells)]


def ordinary(group):
    if group == 'owned':
        return [*integer.seek('S_cast', 'S_object_released', 9),
            'S_object_released.STORE[n_cell] = DEFINED (POBJECT n_payload)',
            '~((HOBJECT n_payload) <- S_object_released.ALLOCATIONS)', *commit('S_object_released'),
            *receive('S_object_released', 'pvalue_saved'),
            'ptask_copy_tail* = (PROPERTY_GET_BASE ppropertyget) :: ptask_base_tail*',
            *nan_string.reader('S_received'), 'S_reader_dtor.STORE[n_cell] = DEFINED pvalue_saved',
            'pdestructionoperation_reader.SOURCE = PROPERTY_GET_BASE ppropertyget',
            *integer.seek('S_reader_dtor', 'S_detached', 5),
            'S_detached.RESULT = KNOWN pvalue_saved', 'S_detached.STORE[n_cell] = DEFINED (' + nan_string.string('repair46') + ')',
            '$weakref_get(S_detached, n_weak) = PNULL']
    return [*nan_string.reader('S_cast'),
        'S_reader_dtor.STORE[n_cell] = DEFINED (' + ('POBJECT n_payload' if group == 'value' else 'pvalue_saved') + ')',
        '$get_test_frame_copy(S_reader_dtor.FRAMES) = ((ppropertyget, ' + ('KNOWN pvalue_saved' if group == 'value' else 'REFERENCE n_cell') + '))',
        *receive('S_reader_dtor', 'pvalue_saved' if group == 'value' else nan_string.string('repair46')),
        '$weakref_get(S_received, n_weak) = PNULL',
        'S_received.STORE[n_cell] = DEFINED (' + nan_string.string('repair46') + ')',
        '$get_test_output(S_received.EVENTS) = $ptascii(' + json.dumps('C|G|value|T|1/0|R|0/1|L|0|' if group == 'value' else 'C|G|value|T|1/0|L|1|R|1/1|') + ')']


def message(expected):
    return cross.invoke.byte_expr(expected.split('caught|', 1)[1].split('|1|', 1)[0].encode())


def conflict(expected):
    text = message(expected)
    return [*integer.seek('S_cast', 'S_object_released', 9),
        '~((HOBJECT n_payload) <- S_object_released.ALLOCATIONS)',
        'S_object_released.STORE[n_cell] = DEFINED (' + nan_string.string('changed46') + ')',
        'S_object_released.PROPREFS = S_cast.PROPREFS',
        '$typed_conversion_at(S_object_released, [(PTBRANCH ([PTBUILTIN "string"]))], ' + nan_string.string('changed46') + ', true) = TYPEVALUE (' + nan_string.string('changed46') + ')',
        'S_error = S_object_released[.COMPLETION = THROWN "TypeError" (' + text + ') ppropertyget.LINE]',
        '$property_get_string_commit(S_object_released, ppropertygetstring, pvalue_saved) = S_error',
        'S_finished = S_error[.TODO = (PROPERTY_GET_COPY ppropertyget (REFERENCE n_cell)) :: ptask_return_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        '$property_get_string_finish(S_object_released, ppropertygetstring, pvalue_saved) = S_finished',
        *nan_string.budget('S_object_released', 'S_finished'),
        *nan_string.reader('S_object_released', '(n_type_error)'), '$get_test_message(S_reader_dtor, n_type_error, ' + text + ')',
        'S_reader_dtor.STORE[n_cell] = DEFINED (' + nan_string.string('changed46') + ')',
        *integer.seek('S_reader_dtor', 'S_error_copy', 6),
        'S_error_copy.STORE[n_cell] = DEFINED (' + nan_string.string('repair46') + ')',
        '$propref_at(S_error_copy.PROPREFS, n_cell) = eps', '$get_test_message(S_error_copy, n_type_error, ' + text + ')']


def pending(run, group, expected, eval_checks):
    constrained = group == 'source-destructor-throw'
    text = message(expected) if constrained else None
    checks = [*initial(run, eval_checks),
        *seek_any('S_initial', 'S_throw', 11),
        'S_throw.TODO = (THROW_SEARCH n_payload_error) :: (PROPERTY_GET_STRING_COPY ppropertygetstring pvalue_saved) :: ptask_return_tail*',
        'ppropertyget = ppropertygetstring.GET', 'n_reader = ppropertyget.OBJECT', 'n_payload = ppropertygetstring.OBJECT',
        '$integer_get_phase(S_throw, 11, n_reader)', *get.valid('S_throw'),
        'S_global = $global_table_view(S_throw)', '$lookup(S_global.ENV, $ptascii("returnCell")) = (n_cell)',
        'pvalue_saved = ' + SAVED, 'ppropertygetstring.INPUT = REFERENCE n_cell',
        '$get_test_message(S_throw, n_payload_error, $ptascii(' + json.dumps('payload-source46' if constrained else 'payload46') + '))',
        '$throwable_previous_id(S_throw, n_payload_error) = eps',
        'S_throw.STORE[n_cell] = DEFINED (' + (nan_string.string('changed46') if constrained else 'POBJECT n_payload') + ')',
        '~((HOBJECT n_payload) <- S_throw.ALLOCATIONS)',
        'S_discard = S_throw[.TODO = (THROW_SEARCH n_payload_error) :: ptask_return_tail*]']
    checks += ['$throwable_live(S_throw, n_payload_error)',
        '$property_get_string_copy_abrupt(S_discard, ppropertygetstring[.OWNER = $(ppropertygetstring.OWNER + 1)], pvalue_saved) = S_discard[.COMPLETION = UNSUPPORTED "magic getter Stringable copy cleanup"]',
        '$property_get_string_copy_abrupt(S_discard, ppropertygetstring, PSTRING_CARRIER (REQUEST_STRING (|S_discard.STRINGDATA|)) ($ptascii("value46"))) = S_discard[.COMPLETION = UNSUPPORTED "magic getter Stringable copy cleanup"]']
    if not constrained:
        checks += ['~$throwable_live(S_discard, n_payload_error)']
    if constrained:
        checks += ['S_error = $throw_scalar(S_discard, "TypeError", ' + text + ', ppropertyget.LINE)',
            'S_new = $throwable_materialize(S_error)', 'S_new.COMPLETION = THROWING n_type_error',
            'S_linked = $throwable_previous(S_new, n_type_error, n_payload_error)',
            'S_abrupt = S_linked[.TODO = (THROW_SEARCH n_type_error) :: (PROPERTY_GET_COPY ppropertyget (REFERENCE n_cell)) :: ptask_return_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)][.COMPLETION = NORMAL]']
    else:
        checks += ['S_abrupt = S_discard[.STORE = $set_cell(S_discard.STORE, n_cell, DEFINED pvalue_saved)][.TODO = (THROW_SEARCH n_payload_error) :: (PROPERTY_GET_COPY ppropertyget (REFERENCE n_cell)) :: ptask_return_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]']
    checks += ['$property_get_string_copy_abrupt(S_discard, ppropertygetstring, pvalue_saved) = S_abrupt',
        '$return_discard(S_discard, PROPERTY_GET_STRING_COPY ppropertygetstring pvalue_saved) = S_abrupt',
        *nan_string.budget('S_throw', 'S_abrupt'),
        *nan_string.reader('S_throw', '(n_type_error)' if constrained else '(n_payload_error)'),
        'S_reader_dtor.STORE[n_cell] = DEFINED (' + (nan_string.string('changed46') if constrained else 'pvalue_saved') + ')',
        *integer.seek('S_reader_dtor', 'S_error_copy', 6),
        'S_error_copy.STORE[n_cell] = DEFINED (' + nan_string.string('repair46') + ')']
    if constrained:
        checks += ['$get_test_message(S_error_copy, n_type_error, ' + text + ')', '$throwable_previous_id(S_error_copy, n_type_error) = (n_payload_error)']
    else:
        checks += ['$get_test_message(S_error_copy, n_payload_error, $ptascii("payload46"))', '$throwable_previous_id(S_error_copy, n_payload_error) = eps']
    return checks


def cast_throw(run):
    return [*initial(run, ()), *seek_any('S_initial', 'S_throw', 10),
        'S_throw.TODO = (THROW_SEARCH n_cast_error) :: (PROPERTY_GET_STRING_RESULT ppropertygetstring) :: ptask_return_tail*',
        'ppropertyget = ppropertygetstring.GET', 'n_reader = ppropertyget.OBJECT', 'n_payload = ppropertygetstring.OBJECT',
        '$integer_get_phase(S_throw, 10, n_reader)', *get.valid('S_throw'),
        'S_global = $global_table_view(S_throw)', '$lookup(S_global.ENV, $ptascii("returnCell")) = (n_cell)',
        'ppropertygetstring.INPUT = REFERENCE n_cell', 'S_throw.STORE[n_cell] = DEFINED (POBJECT n_payload)',
        'S_throw.STRINGDATA = eps', '$get_test_message(S_throw, n_cast_error, $ptascii("cast46"))',
        'S_discard = S_throw[.TODO = (THROW_SEARCH n_cast_error) :: ptask_return_tail*]',
        'S_abrupt = S_discard[.TODO = (THROW_SEARCH n_cast_error) :: (PROPERTY_GET_COPY ppropertyget (REFERENCE n_cell)) :: ptask_return_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        '$property_get_string_abrupt(S_discard, ppropertygetstring) = S_abrupt',
        '$return_discard(S_discard, PROPERTY_GET_STRING_RESULT ppropertygetstring) = S_abrupt',
        *nan_string.budget('S_throw', 'S_abrupt'), *nan_string.reader('S_throw', '(n_cast_error)'),
        'S_reader_dtor.STORE[n_cell] = DEFINED (POBJECT n_payload)',
        *integer.seek('S_reader_dtor', 'S_error_copy', 6),
        'S_error_copy.TODO = (THROW_SEARCH n_cleanup_error) :: (PROPERTY_GET_COPY ppropertyget (REFERENCE n_cell)) :: ptask_error_tail*',
        '$get_test_message(S_error_copy, n_cleanup_error, $ptascii("cleanup46"))',
        '$throwable_previous_id(S_error_copy, n_cleanup_error) = (n_cast_error)',
        'S_error_copy.STORE[n_cell] = DEFINED (' + nan_string.string('repair46') + ')']


def body(run, source, expected, group, eval_checks=()):
    if group == 'cast-throw':
        return cast_throw(run)
    if group in ('destructor-throw', 'source-destructor-throw'):
        return pending(run, group, expected, eval_checks)
    if group == 'source-exact':
        return [*initial(run, eval_checks),
            *boolean.later('S_initial', 'S_exact', 'ppropertyget', 'ptask_return_tail*', 1),
            'S_global = $global_table_view(S_exact)', '$lookup(S_global.ENV, $ptascii("returnCell")) = (n_cell)',
            'S_exact.STORE[n_cell] = DEFINED (PSTRING ($ptascii("seed46")))',
            '$propref_at(S_exact.PROPREFS, n_cell) = (ppropref)', 'ppropref.SOURCES =/= eps',
            '$property_get_propref(S_exact, ppropertyget, n_cell)',
            '$property_get_verify(S_exact, ppropertyget, REFERENCE n_cell) = S_exact',
            '$property_get_string_capture(S_exact, ppropertyget) = eps',
            'S_finished = S_exact[.TODO = (PROPERTY_GET_COPY ppropertyget (REFERENCE n_cell)) :: ptask_return_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
            '$property_get_complete(S_exact, ppropertyget, S_exact.RESULT) = S_finished', *nan_string.budget('S_exact', 'S_finished')]
    if group in ('reference-entry', 'strict-getter'):
        checks = returned(run, source, group, eval_checks)
        if group == 'reference-entry':
            return checks + entry()
        text = message(expected)
        return checks + ['$property_get_string_capture(S_return, ppropertyget) = eps',
            'S_finished = S_return[.TODO = (PROPERTY_GET_COPY ppropertyget (REFERENCE n_cell)) :: ptask_return_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)][.COMPLETION = THROWN "TypeError" (' + text + ') ppropertyget.LINE]',
            '$property_get_complete(S_return, ppropertyget, S_return.RESULT) = S_finished',
            *nan_string.budget('S_return', 'S_finished'), *nan_string.reader('S_return', '(n_type_error)'),
            'S_reader_dtor.STORE[n_cell] = DEFINED (POBJECT n_payload)', '$get_test_message(S_reader_dtor, n_type_error, ' + text + ')',
            'S_reader_global = $global_table_view(S_reader_dtor)',
            '$trace_slot(S_reader_global, S_reader_global.ENV, $ptascii("casts")) = PINT 0']
    checks = cast_return(run, group, eval_checks)
    if group == 'reference-ready':
        return checks + ready() + guards()
    if group == 'reference-copy':
        return checks + payload('S_cast') + copied('S_payload') + commit('S_object_released') + receive('S_object_released', 'pvalue_saved')
    if group == 'source-conflict':
        return checks + conflict(expected)
    return checks + ordinary(group)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group', choices=list(CASES), required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    before = cross.snapshot(None)
    out = Path(tempfile.mkdtemp(prefix='magic-property-stringable-string-', dir=ROOT/'.tools'))
    report = {'before': before, 'profile': cross.invoke.types.PROFILE, 'passed': False,
        'native_evaluations': 0, 'model_evaluations': 0, 'state_assertions_evaluated': 0,
        'runner_mode': 'SL', 'numeric_cap_seconds': 120, 'case': CASES[args.group], 'jobs': 1}
    print(out, flush=True)
    try:
        original = sources.CASES[CASES[args.group]]
        source = out/'source.php'; source.write_bytes(original)
        sources.prepare(out, source)
        eval_checks = integer.prepare_eval(out, eval_group(args.group))
        run = '$php_run(program_source,0,'+json.dumps(base64.b64encode(os.fsencode(source)).decode())+')'
        clauses = ['program_source = '+(out/'program.watsup').read_text().strip(), *body(run, original, sources.EXPECTED[CASES[args.group]], args.group, eval_checks)]
        fixture = out/'protocol.watsup'
        fixture.write_text(PREFIX+'dec $body() : bool\ndef $body() = true\n'+
            ''.join('  -- if '+clause+'\n' for clause in clauses)+'\ndec $main() : bool\ndef $main() = $body()\n')
        (out/'assertions.json').write_text(json.dumps(clauses, indent=2)+'\n')
        report['state_assertions'] = len(clauses)
        if not args.prepare_only:
            runner = ROOT/'tests/semantics/_build/default/numeric_runner.exe'
            report['numeric_runner_sha256'] = cross.invoke.sha(runner)
            assert report['numeric_runner_sha256'] == 'b57a2ed7daf86de23993a29d079083377cfef6da133739a164dbfdb9f11fd7a0'
            result = cross.invoke.process([str(runner), '--sl', *[str(ROOT/module) for module in before['ordered_modules']], str(fixture)], out/'numeric', 120, ROOT)
            assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
            report['state_assertions_evaluated'] = len(clauses)
        assert source.read_bytes() == original and cross.snapshot(None) == before
        report['passed'] = True
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        report['after'] = cross.snapshot(None)
        (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
        print(out/'report.json', report['passed'], flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()
