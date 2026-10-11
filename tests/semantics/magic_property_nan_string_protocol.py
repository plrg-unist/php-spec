#!/usr/bin/env python3
"""Reached MAGIC_GET NaN warning producers, handler mutation and cleanup."""
import argparse
import base64
import json
import os
from pathlib import Path
import tempfile

import dynamic_property_warning_sources as sources
import magic_property_get_protocol as get
import magic_property_integer_protocol as integer

cross, ROOT = sources.cross, sources.ROOT
CASES = {group: 'review-property-magic-nan-string-'+group+'41' for group in (
    'reference-kept', 'value', 'owned', 'source-conflict', 'handler-throw', 'strict-getter')}
NAN = 18444492273895866368
MESSAGE = '$ptascii("unexpected NAN value was coerced to string")'
PREFIX = integer.PREFIX + r'''
def $integer_get_phase(S, 7, n) = true
  -- if S.TODO = (PROPERTY_GET_NAN ppropertynan) :: ptask_tail*
  -- if ppropertynan.GET.OBJECT = n
  -- if S.DESTRUCTION.OPERATIONS = eps
def $integer_get_phase(S, 8, n) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = PROPERTY_GET_NAN ppropertynan
  -- if ppropertynan.GET.OBJECT = n
def $integer_get_phase(S, 9, n) = true
  -- if S.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = PROPERTY_GET_NAN ppropertynan
  -- if ppropertynan.GET.OBJECT = n
  -- if S.CURRENT = eps /\ S.DESTRUCTION.OPERATIONS = eps
def $integer_get_phase(S, 10, n) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: ptask :: ptask_tail*
  -- if $source_operand_marker(ptask) = PROPERTY_GET_NAN ppropertynan
  -- if ppropertynan.GET.OBJECT = n
  -- if S.CURRENT = eps /\ S.DESTRUCTION.OPERATIONS = eps
'''


def string(text):
    return 'PSTRING_CARRIER INTERNED_STRING ($ptascii('+json.dumps(text)+'))'


def budget(parent, raw_next):
    return [f'$drive_steps({parent}, 0) = {parent}[.COMPLETION = BUDGET]',
        f'$drive_steps({parent}, 1) = $gc_transition_owners({parent}, $destruction_transition_owners({parent}, $sensitive_trace_freeze($source_exception_transition({parent}, $throwable_transition({parent}, {raw_next})))))[.COMPLETION = BUDGET]']


def start(run, source, group, eval_checks):
    line = next(i for i,row in enumerate(source.splitlines(),1)
        if b' = $reader->value;' in row or b' = magic_nan_string_owned_factory41()->value;' in row)
    kept = group in ('reference-kept', 'owned')
    constrained = group == 'source-conflict'
    checks = ['S_initial = '+run, '~S_initial.COMPILESTOP', *eval_checks,
        *integer.seek('S_resumed' if eval_checks else 'S_initial','S_before',0,'0'),
        '$property_get_plan(S_before) = (ppropertyget)', 'n_reader = ppropertyget.OBJECT',
        f'ppropertyget.LINE = {line}', '$property_get_history(S_before, ppropertyget)',
        '$heap_owners($heap_graph(S_before), HOBJECT n_reader) = 1',
        *get.step('S_before','S_pending'),
        '$heap_owners($heap_graph(S_pending), HOBJECT n_reader) = 2',
        f'$property_get_base_count(S_pending.TODO, n_reader, ppropertyget.SITE) = {int(group == "owned")}',
        *integer.seek('S_pending','S_return',1),
        'S_return.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_return_tail*',
        'S_return.ORIGIN = (ppropertyget.SITE)', 'S_return.BASE = BASE_VALUE (KNOWN PNULL)',
        '$property_get_valid(S_return, ppropertyget, true)', '$property_get_tail_valid(S_return, ppropertyget)',
        '$property_get_method(S_return, n_reader) = (pmethoddesc_get)',
        f'pmethoddesc_get.FUNCTION.CODE.STRICT = {str(group == "strict-getter").lower()}',
        'ppropertyget.SITE = PORIGIN n_caller pcpath_caller',
        '$code_at(S_return.CODE, n_caller) = (pcode_caller)',
        f'pcode_caller.STRICT = {str(group == "reference-kept").lower()}',
        '$property_desc_at($property_layout(S_return, ppropertyget.CLASS, |S_return.CLASSES|), ppropertyget.NAME) = (ppropertydesc_get)',
        'ppropertyget.DECL = (ppropertydesc_get.ORIGIN)', 'ppropertydesc_get.READONLY',
        'ppropertydesc_get.TYPE = [(PTBRANCH ([PTBUILTIN "string"]))]',
        '$objectprops_at(S_return.OBJECTPROPS, n_reader) = (ppropertyslot_all*)',
        '$property_slot_at(ppropertyslot_all*, ppropertyget.NAME) = (ppropertyslot_get)',
        'ppropertyslot_get.STATE = PROP_UNSET',
        'S_global = $global_table_view(S_return)',
        '$lookup(S_global.ENV, $ptascii("cell")) = (n_cell)',
        f'pvalue_raw = PFLOAT {NAN}', 'S_return.STORE[n_cell] = DEFINED pvalue_raw',
        'S_return.RESULT = '+('KNOWN pvalue_raw' if group == 'value' else 'REFERENCE n_cell'),
        '$call_reference_operand_valid(S_return, S_return.RESULT)',
        '$parameter_backing_at(S_return.PARAMETERBACKINGS, n_cell) = eps',
        f'$heap_owners($heap_graph(S_return), HOBJECT n_reader) = {2 if kept else 1}',
        f'$heap_owners($heap_graph(S_return), HCELL n_cell) = {4 if constrained else 3 if group in ("reference-kept", "strict-getter") else 1 if group == "value" else 2}',
        '$trace_slot(S_global, S_global.ENV, $ptascii("warnings")) = PINT 0']
    if constrained:
        checks += ['$propref_at(S_return.PROPREFS, n_cell) = (ppropref)',
            'ppropref.SOURCES = [pproptypesource_first]', '$proprefs_valid(S_return)',
            '$property_get_propref(S_return, ppropertyget, n_cell)',
            '$propref_class(S_return, ppropertydesc_get.TYPE, pvalue_raw, false) = PROP_POSSIBLE',
            '$propref_label(S_return, pproptypesource_first) = $ptascii("property MagicNaNStringSource41::$slot of type string|float")']
    else:
        checks += ['$propref_at(S_return.PROPREFS, n_cell) = eps',
            '$property_get_unconstrained(S_return, S_return.RESULT)']
    return checks


def dispatch(state='S_return', descriptor='ppropertyget', tail='ptask_return_tail*', suffix='', handler=True, constrained=False):
    out, nan = 'S_dispatch'+suffix, 'ppropertynan'+suffix
    selected = 'pvalue_nan'+suffix
    event = f'DIAGNOSTIC "Warning" ({MESSAGE}) {descriptor}.LINE'
    checks = [f'$property_get_nan_ready({state}, {descriptor})',
        f'$typed_conversion_at({state}, ppropertydesc_get.TYPE, pvalue_raw, false) = TYPESTRING pvalue_raw',
        f'$float_decode({NAN}) = NOTNUMBER {NAN}',
        f'{selected} = PSTRING_CARRIER (REQUEST_STRING (|{state}.STRINGDATA|)) ($ptascii("NAN"))',
        f'{nan} = {{GET {descriptor}, INPUT {state}.RESULT, FLOAT {NAN}, STRING {selected}, SOURCES '+('([pproptypesource_first])' if constrained else 'eps')+f', OWNER (|{state}.FRAMES|), TAIL {tail}}}',
        f'{out} = $property_get_complete({state}, {descriptor}, {state}.RESULT)']
    produced = f'{state}[.STRINGDATA = {state}.STRINGDATA ++ [($ptascii("NAN"))]][.ERRORFATALTRACE = eps]'
    if handler:
        callback, call = 'pvalue_handler'+suffix, 'perrorcall'+suffix
        checks += [f'{state}.ERRORHANDLER.CALLBACK = ({callback})',
            f'$error_handler_eligible({state}, 2)',
            f'{call} = {{SITE {descriptor}.SITE, LEVEL 2, MESSAGE ({MESSAGE}), LINE {descriptor}.LINE, EVENT ({event}), CALLBACK {callback}, TARGET eps, RESUME PROPERTY_GET_NAN {nan}}}',
            f'{out} = {produced}[.TODO = (ERROR_HANDLER_INVOKE {call}) :: {tail}][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
            f'$error_call_valid({out}, {call})',
            f'$call_sourcefile({out}.FILES, {descriptor}.SITE) = ptbytes_file{suffix}',
            f'$error_handler_values({out}, {call}) = [PINT 2, PSTRING ({MESSAGE}), PSTRING ptbytes_file{suffix}, PINT {descriptor}.LINE]']
    else:
        checks += [f'~$error_handler_eligible({state}, 2)', f'{state}.REPORTING = 0',
            f'{out} = {produced}[.TODO = (PROPERTY_GET_NAN {nan}) :: {tail}][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
            f'{out}.EVENTS = {state}.EVENTS']
    return checks + [f'{out}.STORE = {state}.STORE', f'{out}.PROPREFS = {state}.PROPREFS',
        f'{out}.OBJECTPROPS = {state}.OBJECTPROPS', f'{out}.FRAMES = {state}.FRAMES', f'{out}.HELD = {state}.HELD',
        f'$property_get_nan_valid({out}, {nan})', f'$string_carrier_valid({out}, {selected})',
        f'$property_get_carriers({out}.TODO, n_reader, {descriptor}.SITE) = 1',
        f'$task_nodes(PROPERTY_GET_NAN {nan}) = [HOBJECT n_reader] ++ $operand_nodes({state}.RESULT)',
        f'~$property_get_guard_task(PROPERTY_GET_NAN {nan}, n_reader, {descriptor}.NAME)',
        *budget(state,out)]


def callback(parent='S_dispatch', suffix='', changed='handler-kept41', constrained=False):
    result, resumed = 'S_handler_result'+suffix, 'S_nan'+suffix
    nan, call = 'ppropertynan'+suffix, 'perrorcall'+suffix
    checks = [*integer.seek(parent,result,9),
        f'{result}.TODO = (ERROR_HANDLER_RESULT perrorcall_done{suffix}) :: {nan}.TAIL',
        f'perrorcall_done{suffix}.RESUME = PROPERTY_GET_NAN {nan}',
        f'perrorcall_done{suffix}.TARGET = (pcalltarget_handler{suffix})',
        f'{result}.RESULT = KNOWN (PBOOL true)', f'{result}.ERRORHANDLER.CALLBACK = eps',
        f'{result}.STORE[n_cell] = DEFINED ({string(changed)})',
        f'S_handler_global{suffix} = $global_table_view({result})',
        f'$trace_slot(S_handler_global{suffix}, S_handler_global{suffix}.ENV, $ptascii("warnings")) = PINT 1',
        f'$property_get_nan_valid({result}, {nan})',
        *integer.seek(result,resumed,7),
        f'{resumed}.TODO = (PROPERTY_GET_NAN {nan}) :: {nan}.TAIL',
        f'{resumed}.ERRORHANDLER.CALLBACK = ({call}.CALLBACK)',
        f'{resumed}.STORE[n_cell] = DEFINED ({string(changed)})',
        f'$property_get_nan_valid({resumed}, {nan})',
        f'$string_carrier_valid({resumed}, {nan}.STRING)']
    if constrained:
        checks += [f'{resumed}.PROPREFS = S_return.PROPREFS',
            f'$propref_at({resumed}.PROPREFS, n_cell) = (ppropref)', f'$proprefs_valid({resumed})',
            f'$typed_conversion_at({resumed}, ppropertydesc_get.TYPE, {string(changed)}, true) = TYPEVALUE ({string(changed)})']
    return checks


def commit(state='S_nan', suffix='', ref=True):
    nan, selected = 'ppropertynan'+suffix, 'pvalue_nan'+suffix
    committed, finished = 'S_committed'+suffix, 'S_finished'+suffix
    change = f'.STORE[n_cell] = DEFINED {selected}][.RESULT = REFERENCE n_cell' if ref else f'.RESULT = KNOWN {selected}'
    operand = 'REFERENCE n_cell' if ref else f'KNOWN {selected}'
    return [f'{committed} = $property_get_nan_commit({state}, {nan})',
        f'{committed} = {state}[{change}]', f'{committed}.STRINGDATA = {state}.STRINGDATA',
        f'{finished} = $property_get_nan_finish({state}, {nan})',
        f'{finished} = {committed}[.TODO = (PROPERTY_GET_COPY {nan}.GET ({operand})) :: {nan}.TAIL][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        *budget(state,finished)]


def guards(state='S_nan', suffix=''):
    nan = 'ppropertynan'+suffix
    checks=[]
    for label, update in [('known','INPUT KNOWN (PINT 7)'), ('known_float','INPUT KNOWN (PFLOAT 0)'),
                          ('bits','FLOAT 18446744073709551616'), ('finite','FLOAT 0'),
                          ('plain','STRING PSTRING ($ptascii("NAN"))'),
                          ('index',f'STRING PSTRING_CARRIER (REQUEST_STRING (|{state}.STRINGDATA|)) ($ptascii("NAN"))'),
                          ('bytes','STRING PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("X"))'),
                          ('owner',f'OWNER $(|{state}.FRAMES| + 1)'), ('tail','TAIL eps'),
                          ('line',f'GET {nan}.GET[.LINE = $({nan}.GET.LINE + 1)]')]:
        checks += [f'ppropertynan_bad_{label} = {nan}[.{update.split(" ",1)[0]} = {update.split(" ",1)[1]}]',
            f'S_bad_{label} = {state}[.TODO = (PROPERTY_GET_NAN ppropertynan_bad_{label}) :: {nan}.TAIL]',
            f'~$property_get_nan_valid(S_bad_{label}, ppropertynan_bad_{label})']
    checks += [f'~$property_get_nan_valid({state}[.ORIGIN = ({nan}.GET.METHOD)], {nan})',
        f'S_bad_parameter = {state}[.PARAMETERBACKINGS = [{{FUNCTION {nan}.GET.METHOD, INDEX 0, CELL n_cell, LINE {nan}.GET.LINE, VALUE ($ptascii("float"))}}]]',
        f'~$property_get_nan_valid(S_bad_parameter, {nan})',
        f'S_growth = {state}[.STRINGDATA = {state}.STRINGDATA ++ [($ptascii("unrelated41"))]]',
        f'$property_get_nan_valid(S_growth, {nan})', f'$string_carrier_valid(S_growth, {nan}.STRING)',
        f'S_growth_finished = $property_get_nan_finish(S_growth, {nan})',
        f'S_growth_finished = S_finished{suffix}[.STRINGDATA = S_growth.STRINGDATA]']
    return checks


def reader(parent, pending='eps', label=''):
    state='S_reader_dtor'+label
    return [*integer.seek(parent,state,4),
        f'{state}.CURRENT = (pcallcontext_reader{label})',
        f'$destructor_context_call(pcallcontext_reader{label}, {state}.CURRENT, {state}.FRAMES) = (pdestructorcall_reader{label})',
        f'pdestructorcall_reader{label}.OBJECT = n_reader',
        f'pdestructorcall_reader{label}.OPERATION = (pdestructionoperation_reader{label})',
        f'pdestructionoperation_reader{label}.PENDING = {pending}',
        f'$destructor_call_pending_valid({state}, pdestructorcall_reader{label})',
        f'$eager_operation_source_guard({state}, pdestructionoperation_reader{label})',
        f'S_reader_global{label} = $global_table_view({state})',
        f'$trace_slot(S_reader_global{label}, S_reader_global{label}.ENV, $ptascii("weak")) = POBJECT n_weak',
        f'$weakref_get({state}, n_weak) = POBJECT n_reader']


def kept(source, expected):
    checks = [*dispatch(handler=False), *integer.seek('S_dispatch','S_nan',7),
        'S_nan = S_dispatch', *commit(ref=True), *guards(),
        *integer.seek('S_nan','S_copy',2),
        'S_copy.TODO = (PROPERTY_GET_COPY ppropertyget (REFERENCE n_cell)) :: ptask_copy_tail*',
        'S_copy.STORE[n_cell] = DEFINED pvalue_nan',
        '$heap_owners($heap_graph(S_copy), HOBJECT n_reader) = 1',
        *get.step('S_copy','S_receiving'), *integer.seek('S_receiving','S_received',5),
        'S_received.TODO = ptask_copy_tail*', 'S_received.RESULT = KNOWN pvalue_nan',
        *integer.seek('S_received','S_before_handled',0,'0'),
        '$property_get_plan(S_before_handled) = (ppropertyget_handled)',
        'ppropertyget_handled.OBJECT = n_reader', 'ppropertyget_handled.SITE =/= ppropertyget.SITE',
        'S_before_handled.REPORTING = 0',
        *integer.seek('S_before_handled','S_return_handled',1),
        'S_return_handled.TODO = (PROPERTY_GET_RESULT ppropertyget_handled) :: ptask_handled_tail*',
        'S_return_handled.STORE[n_cell] = DEFINED pvalue_raw', 'S_return_handled.RESULT = REFERENCE n_cell',
        *dispatch('S_return_handled','ppropertyget_handled','ptask_handled_tail*','_handled'),
        *callback('S_dispatch_handled','_handled'), *commit('S_nan_handled','_handled'),
        *get.finish('S_nan_handled',expected),
        '$trace_slot(S_done, S_done.ENV, $ptascii("masked")) = pvalue_nan',
        '$trace_slot(S_done, S_done.ENV, $ptascii("handled")) = pvalue_nan_handled',
        '$trace_slot(S_done, S_done.ENV, $ptascii("alias")) = '+string('after-kept41'),
        '$trace_slot(S_done, S_done.ENV, $ptascii("gets")) = PINT 2',
        '$trace_slot(S_done, S_done.ENV, $ptascii("drops")) = PINT 1',
        '$trace_slot(S_done, S_done.ENV, $ptascii("warnings")) = PINT 1']
    return checks


def ordinary(group, expected):
    owned = group=='owned'
    changed = 'handler-owned41' if owned else 'handler-value41'
    checks = [*dispatch(), *callback(changed=changed), *commit(ref=owned)]
    if owned:
        checks += [*integer.seek('S_nan','S_copy',2),
            'S_copy.TODO = (PROPERTY_GET_COPY ppropertyget (REFERENCE n_cell)) :: (PROPERTY_GET_BASE ppropertyget) :: ptask_base_tail*',
            'S_copy.STORE[n_cell] = DEFINED pvalue_nan',
            *integer.seek('S_copy','S_base',3),
            'S_base.RESULT = KNOWN pvalue_nan', 'S_base.STORE[n_cell] = DEFINED pvalue_nan',
            '$heap_owners($heap_graph(S_base), HOBJECT n_reader) = 1',
            '$heap_owners($heap_graph(S_base), HCELL n_cell) = 1',
            *reader('S_base'), 'pdestructionoperation_reader.SOURCE = PROPERTY_GET_BASE ppropertyget',
            'pdestructionoperation_reader.VALUE = KNOWN pvalue_nan',
            'S_reader_dtor.STORE[n_cell] = DEFINED pvalue_nan']
    else:
        checks += [*reader('S_nan'),
            '$get_test_frame_copy(S_reader_dtor.FRAMES) = ((ppropertyget, KNOWN pvalue_nan))',
            'S_reader_dtor.STORE[n_cell] = DEFINED ('+string(changed)+')']
    checks += [*get.finish('S_reader_dtor',expected), '$weakref_get(S_done, n_weak) = PNULL',
        '$trace_slot(S_done, S_done.ENV, $ptascii("value")) = pvalue_nan',
        '$trace_slot(S_done, S_done.ENV, $ptascii("cell")) = PBOOL '+str(owned).lower(),
        '$trace_slot(S_done, S_done.ENV, $ptascii("warnings")) = PINT 1']
    return checks


def conflict(expected):
    message = cross.invoke.byte_expr(expected.split('caught=',1)[1].split('/prior=',1)[0].encode())
    return [*dispatch(constrained=True), *callback(changed='handler-source41',constrained=True),
        '$property_get_nan_commit(S_nan, ppropertynan) = S_nan[.COMPLETION = THROWN "TypeError" ('+message+') ppropertyget.LINE]',
        'S_finished = $property_get_nan_finish(S_nan, ppropertynan)',
        'S_finished = S_nan[.TODO = (PROPERTY_GET_COPY ppropertyget (REFERENCE n_cell)) :: ptask_return_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)][.COMPLETION = THROWN "TypeError" ('+message+') ppropertyget.LINE]',
        *budget('S_nan','S_finished'),
        'ppropertynan_bad_source = ppropertynan[.SOURCES = eps]',
        '~$property_get_nan_valid(S_nan[.TODO = (PROPERTY_GET_NAN ppropertynan_bad_source) :: ptask_return_tail*], ppropertynan_bad_source)',
        *integer.seek('S_nan','S_reader_dtor',4),
        'S_reader_dtor.CURRENT = (pcallcontext_reader)',
        '$destructor_context_call(pcallcontext_reader, S_reader_dtor.CURRENT, S_reader_dtor.FRAMES) = (pdestructorcall_reader)',
        'pdestructorcall_reader.OPERATION = (pdestructionoperation_reader)',
        'pdestructionoperation_reader.PENDING = (n_type_error)',
        '$get_test_message(S_reader_dtor, n_type_error, '+message+')',
        'S_reader_dtor.STORE[n_cell] = DEFINED ('+string('handler-source41')+')',
        '$propref_at(S_reader_dtor.PROPREFS, n_cell) = (ppropref)',
        *integer.seek('S_reader_dtor','S_error_copy',6),
        'S_error_copy.TODO = (THROW_SEARCH n_type_error) :: (PROPERTY_GET_COPY ppropertyget (REFERENCE n_cell)) :: ptask_error_tail*',
        'S_error_copy.STORE[n_cell] = DEFINED ('+string('repaired-source41')+')',
        '$propref_at(S_error_copy.PROPREFS, n_cell) = eps',
        '$get_test_message(S_error_copy, n_type_error, '+message+')',
        '$throwable_previous_id(S_error_copy, n_type_error) = eps',
        *get.finish('S_error_copy',expected), '$lookup(S_done.ENV, $ptascii("value")) = eps',
        '$trace_slot(S_done, S_done.ENV, $ptascii("alias")) = '+string('repaired-source41')]


def throwing(expected):
    return [*dispatch(), *integer.seek('S_dispatch','S_throw',10),
        'S_throw.TODO = (THROW_SEARCH n_warning) :: (ERROR_HANDLER_RESULT perrorcall_throw) :: ptask_return_tail*',
        'perrorcall_throw.RESUME = PROPERTY_GET_NAN ppropertynan',
        '$get_test_message(S_throw, n_warning, $ptascii("warning41"))',
        'S_throw.STORE[n_cell] = DEFINED ('+string('handler-throw41')+')',
        'S_discard_input = S_throw[.TODO = (THROW_SEARCH n_warning) :: ptask_return_tail*]',
        'S_abrupt = $property_get_nan_abrupt(S_discard_input, ppropertynan)',
        'S_abrupt = S_discard_input[.STORE[n_cell] = DEFINED pvalue_nan][.TODO = (THROW_SEARCH n_warning) :: (PROPERTY_GET_COPY ppropertyget (REFERENCE n_cell)) :: ptask_return_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        '$error_read_discard(S_discard_input, PROPERTY_GET_NAN ppropertynan) = S_abrupt',
        'S_wrapper_abrupt = S_abrupt[.ERRORHANDLER.CALLBACK = (perrorcall_throw.CALLBACK)]',
        '$return_discard(S_discard_input, ERROR_HANDLER_RESULT perrorcall_throw) = S_wrapper_abrupt',
        *budget('S_throw','S_wrapper_abrupt'),
        *reader('S_throw','(n_warning)'),
        'S_reader_dtor.STORE[n_cell] = DEFINED pvalue_nan',
        '$get_test_frame_copy(S_reader_dtor.FRAMES) = ((ppropertyget, REFERENCE n_cell))',
        '$get_test_message(S_reader_dtor, n_warning, $ptascii("warning41"))',
        *integer.seek('S_reader_dtor','S_error_copy',6),
        'S_error_copy.TODO = (THROW_SEARCH n_cleanup) :: (PROPERTY_GET_COPY ppropertyget (REFERENCE n_cell)) :: ptask_error_tail*',
        '$get_test_message(S_error_copy, n_cleanup, $ptascii("cleanup41"))',
        '$throwable_previous_id(S_error_copy, n_cleanup) = (n_warning)',
        '$throwable_previous_id(S_error_copy, n_warning) = eps',
        'S_error_copy.STORE[n_cell] = DEFINED ('+string('repaired-throw41')+')',
        *get.finish('S_error_copy',expected), '$lookup(S_done.ENV, $ptascii("value")) = eps',
        '$weakref_get(S_done, n_weak) = PNULL']


def strict(expected):
    message = cross.invoke.byte_expr(expected.split('caught=',1)[1].split('/prior=',1)[0].encode())
    return ['~$property_get_nan_ready(S_return, ppropertyget)',
        '$typed_conversion_at(S_return, ppropertydesc_get.TYPE, pvalue_raw, true) = TYPEREJECT',
        'S_verified = $property_get_verify(S_return, ppropertyget, S_return.RESULT)',
        'S_verified = S_return[.COMPLETION = THROWN "TypeError" ('+message+') ppropertyget.LINE]',
        'S_finished = $property_get_complete(S_return, ppropertyget, S_return.RESULT)',
        'S_finished = S_verified[.TODO = (PROPERTY_GET_COPY ppropertyget (REFERENCE n_cell)) :: ptask_return_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        *budget('S_return','S_finished'), *reader('S_return','(n_type_error)'),
        'S_reader_dtor.STORE[n_cell] = DEFINED pvalue_raw',
        '$get_test_message(S_reader_dtor, n_type_error, '+message+')',
        *integer.seek('S_reader_dtor','S_error_copy',6),
        'S_error_copy.STORE[n_cell] = DEFINED ('+string('repaired-strict41')+')',
        '$throwable_previous_id(S_error_copy, n_type_error) = eps',
        *get.finish('S_error_copy',expected),
        '$trace_slot(S_done, S_done.ENV, $ptascii("warnings")) = PINT 0', '$weakref_get(S_done, n_weak) = PNULL']


def body(run, source, expected, group, eval_checks=()):
    checks=start(run,source,group,eval_checks)
    if group=='reference-kept': return checks+kept(source,expected)
    if group in ('value','owned'): return checks+ordinary(group,expected)
    if group=='source-conflict': return checks+conflict(expected)
    if group=='handler-throw': return checks+throwing(expected)
    return checks+strict(expected)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group', choices=list(CASES), required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    before = cross.snapshot(None)
    out = Path(tempfile.mkdtemp(prefix='magic-property-nan-string-', dir=ROOT/'.tools'))
    report = {'before': before, 'profile': cross.invoke.types.PROFILE, 'passed': False,
        'native_evaluations': 0, 'model_evaluations': 0, 'state_assertions_evaluated': 0,
        'runner_mode': 'SL', 'numeric_cap_seconds': 120, 'case': CASES[args.group], 'jobs': 1}
    print(out, flush=True)
    try:
        original = sources.CASES[CASES[args.group]]
        source = out/'source.php'; source.write_bytes(original)
        sources.prepare(out, source)
        eval_checks = integer.prepare_eval(out, 'weak-getter' if args.group == 'reference-kept' else args.group)
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
