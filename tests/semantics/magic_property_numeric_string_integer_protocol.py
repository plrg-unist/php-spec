#!/usr/bin/env python3
"""Reached MAGIC_GET numeric-string-to-int warning producers, handler mutation and cleanup."""
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
CASES = {group: 'review-property-magic-numeric-string-integer-'+group+'43' for group in (
    'reference-kept', 'value', 'owned', 'source-conflict', 'handler-throw', 'strict-getter')}
CASES['reference-quiet'] = CASES['reference-kept']
CASES['reference-handled'] = CASES['reference-kept']
CASES['reference-resume'] = CASES['reference-kept']
CASES['reference-zero'] = CASES['reference-kept']
CASES['reference-prefix'] = CASES['reference-kept']
F75 = 4620130267728707584
F7 = 4619567317775286272
FNEGZERO = 9223372036854775808
MESSAGE = '$ptascii('+json.dumps('Implicit conversion from float-string " 7.50e0 " to int loses precision')+')'
PREFIX = integer.PREFIX + r'''
def $integer_get_phase(S, 7, n) = true
  -- if S.TODO = (PROPERTY_GET_STRING_LONG ppropertystringlong) :: ptask_tail*
  -- if ppropertystringlong.GET.OBJECT = n
  -- if S.DESTRUCTION.OPERATIONS = eps
def $integer_get_phase(S, 8, n) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = PROPERTY_GET_STRING_LONG ppropertystringlong
  -- if ppropertystringlong.GET.OBJECT = n
def $integer_get_phase(S, 9, n) = true
  -- if S.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = PROPERTY_GET_STRING_LONG ppropertystringlong
  -- if ppropertystringlong.GET.OBJECT = n
  -- if S.CURRENT = eps /\ S.DESTRUCTION.OPERATIONS = eps
def $integer_get_phase(S, 10, n) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: ptask :: ptask_tail*
  -- if $source_operand_marker(ptask) = PROPERTY_GET_STRING_LONG ppropertystringlong
  -- if ppropertystringlong.GET.OBJECT = n
  -- if S.CURRENT = eps /\ S.DESTRUCTION.OPERATIONS = eps
'''
QUIET_PHASE = r'''
def $integer_get_phase(S, 11, n) = true
  -- if S.TODO = (PROPERTY_GET_STRING_LONG ppropertystringlong) :: ptask_tail*
  -- if ppropertystringlong.GET.OBJECT = n
  -- if S.CURRENT = eps /\ S.DESTRUCTION.OPERATIONS = eps
  -- if S_global = $global_table_view(S)
  -- if $trace_slot(S_global, S_global.ENV, $ptascii("warnings")) = PINT 1
'''
QUIET_VALUE_PHASE = r'''
def $integer_get_phase(S, 12, n) = true
  -- if S.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_tail*
  -- if ppropertyget.OBJECT = n
  -- if S.RESULT = REFERENCE n_cell
  -- if S.STORE[n_cell] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("7.0")))
  -- if S.CURRENT = eps /\ S.DESTRUCTION.OPERATIONS = eps
def $integer_get_phase(S, 13, n) = true
  -- if S.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_tail*
  -- if ppropertyget.OBJECT = n
  -- if S.RESULT = REFERENCE n_cell
  -- if S.STORE[n_cell] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("-0.0")))
  -- if S.CURRENT = eps /\ S.DESTRUCTION.OPERATIONS = eps
def $integer_get_phase(S, 14, n) = true
  -- if S.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_tail*
  -- if ppropertyget.OBJECT = n
  -- if S.RESULT = REFERENCE n_cell
  -- if S.STORE[n_cell] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("7.5suffix")))
  -- if S.CURRENT = eps /\ S.DESTRUCTION.OPERATIONS = eps
'''
DROP_PHASE = r'''
def $integer_get_phase(S, 15, n) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: (PROPERTY_GET_DROP ppropertyget pvalue) :: ptask_tail*
  -- if ppropertyget.OBJECT = n
  -- if S.CURRENT = eps /\ S.DESTRUCTION.OPERATIONS = eps
'''


def string(text):
    return 'PSTRING_CARRIER INTERNED_STRING ($ptascii('+json.dumps(text)+'))'


def budget(parent, raw_next):
    return [f'$drive_steps({parent}, 0) = {parent}[.COMPLETION = BUDGET]',
        f'$drive_steps({parent}, 1) = $gc_transition_owners({parent}, $destruction_transition_owners({parent}, $sensitive_trace_freeze($source_exception_transition({parent}, $throwable_transition({parent}, {raw_next})))))[.COMPLETION = BUDGET]']


def start(run, source, group, eval_checks):
    line = next(i for i,row in enumerate(source.splitlines(),1)
        if b' = $reader->value;' in row or b' = magic_numeric_string_integer_owned_factory43()->value;' in row)
    kept = group in ('reference-kept', 'owned', 'source-conflict')
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
        'ppropertydesc_get.TYPE = [(PTBRANCH ([PTBUILTIN "int"]))]',
        '$objectprops_at(S_return.OBJECTPROPS, n_reader) = (ppropertyslot_all*)',
        '$property_slot_at(ppropertyslot_all*, ppropertyget.NAME) = (ppropertyslot_get)',
        'ppropertyslot_get.STATE = PROP_UNSET',
        'S_global = $global_table_view(S_return)',
        '$lookup(S_global.ENV, $ptascii("cell")) = (n_cell)',
        'pvalue_raw = '+('PINT 7' if constrained else string('7.0') if group=='strict-getter' else 'PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii(" 7.50e0 "))'), 'S_return.STORE[n_cell] = DEFINED pvalue_raw',
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
            '$propref_class(S_return, ppropertydesc_get.TYPE, pvalue_raw, false) = PROP_EXACT',
            '$propref_label(S_return, pproptypesource_first) = $ptascii("property MagicNumericStringIntegerSource43::$slot of type string|int")']
    else:
        checks += ['$propref_at(S_return.PROPREFS, n_cell) = eps',
            '$property_get_unconstrained(S_return, S_return.RESULT)']
    return checks


def dispatch(state='S_return', descriptor='ppropertyget', tail='ptask_return_tail*', suffix='', handler=True, constrained=False):
    out, record = 'S_dispatch'+suffix, 'ppropertystringlong'+suffix
    selected = 'pvalue_long'+suffix
    event = f'DIAGNOSTIC "Deprecated" ({MESSAGE}) {descriptor}.LINE'
    checks = [f'$property_get_string_long_ready({state}, {descriptor})',
        f'S_read_string{suffix} = $quiet_operand({state}, {state}.RESULT)',
        f'S_read_string{suffix}.RESULT = KNOWN pvalue_string{suffix}',
        f'pvalue_string{suffix} = PSTRING_CARRIER (REQUEST_STRING {1 if suffix=="_handled" else 0}) ($ptascii(" 7.50e0 "))',
        f'$string_carrier_valid({state}, pvalue_string{suffix})',
        f'$typed_number(pvalue_string{suffix}) = (NFLOAT {F75})',
        f'$typed_conversion_at({state}, ppropertydesc_get.TYPE, pvalue_string{suffix}, false) = TYPEINTEGER pvalue_string{suffix}',
        f'$reporting_lossy_value(PSTRING ($ptascii(" 7.50e0 "))) = ((7, {MESSAGE}))',
        f'{selected} = PINT 7',
        f'{record} = {{GET {descriptor}, INPUT {state}.RESULT, STRING pvalue_string{suffix}, INTEGER 7, SOURCES '+('([pproptypesource_first])' if constrained else 'eps')+f', OWNER (|{state}.FRAMES|), TAIL {tail}}}',
        f'{out} = $property_get_complete({state}, {descriptor}, {state}.RESULT)']
    produced = f'{state}[.ERRORFATALTRACE = eps]'
    if handler:
        callback, call = 'pvalue_handler'+suffix, 'perrorcall'+suffix
        checks += [f'{state}.ERRORHANDLER.CALLBACK = ({callback})',
            f'$error_handler_eligible({state}, 8192)',
            f'{call} = {{SITE {descriptor}.SITE, LEVEL 8192, MESSAGE ({MESSAGE}), LINE {descriptor}.LINE, EVENT ({event}), CALLBACK {callback}, TARGET eps, RESUME PROPERTY_GET_STRING_LONG {record}}}',
            f'{out} = {produced}[.TODO = (ERROR_HANDLER_INVOKE {call}) :: {tail}][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
            f'$error_call_valid({out}, {call})',
            f'$call_sourcefile({out}.FILES, {descriptor}.SITE) = ptbytes_file{suffix}',
            f'$error_handler_values({out}, {call}) = [PINT 8192, PSTRING ({MESSAGE}), PSTRING ptbytes_file{suffix}, PINT {descriptor}.LINE]']
    else:
        checks += [f'~$error_handler_eligible({state}, 8192)', f'{state}.REPORTING = 0',
            f'{out} = {produced}[.TODO = (PROPERTY_GET_STRING_LONG {record}) :: {tail}][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
            f'{out}.EVENTS = {state}.EVENTS']
    return checks + [f'{out}.STORE = {state}.STORE', f'{out}.PROPREFS = {state}.PROPREFS',
        f'{out}.OBJECTPROPS = {state}.OBJECTPROPS', f'{out}.FRAMES = {state}.FRAMES', f'{out}.HELD = {state}.HELD',
        f'$property_get_string_long_valid({out}, {record})', f'{out}.STRINGDATA = {state}.STRINGDATA',
        f'$property_get_carriers({out}.TODO, n_reader, {descriptor}.SITE) = 1',
        f'$task_nodes(PROPERTY_GET_STRING_LONG {record}) = [HOBJECT n_reader] ++ $operand_nodes({state}.RESULT)',
        f'~$property_get_guard_task(PROPERTY_GET_STRING_LONG {record}, n_reader, {descriptor}.NAME)',
        *budget(state,out)]


def callback(parent='S_dispatch', suffix='', changed='handler-kept43', constrained=False):
    result, resumed = 'S_handler_result'+suffix, 'S_long'+suffix
    record, call = 'ppropertystringlong'+suffix, 'perrorcall'+suffix
    checks = [*integer.seek(parent,result,9),
        f'{result}.TODO = (ERROR_HANDLER_RESULT perrorcall_done{suffix}) :: {record}.TAIL',
        f'perrorcall_done{suffix}.RESUME = PROPERTY_GET_STRING_LONG {record}',
        f'perrorcall_done{suffix}.TARGET = (pcalltarget_handler{suffix})',
        f'{result}.RESULT = KNOWN (PBOOL true)', f'{result}.ERRORHANDLER.CALLBACK = eps',
        f'{result}.STORE[n_cell] = DEFINED (PINT 42)' if constrained else f'{result}.STORE[n_cell] = DEFINED ({string(changed)})',
        f'S_handler_global{suffix} = $global_table_view({result})',
        f'$trace_slot(S_handler_global{suffix}, S_handler_global{suffix}.ENV, $ptascii("warnings")) = PINT 1',
        f'$property_get_string_long_valid({result}, {record})',
        *integer.seek(result,resumed,7),
        f'{resumed}.TODO = (PROPERTY_GET_STRING_LONG {record}) :: {record}.TAIL',
        f'{resumed}.ERRORHANDLER.CALLBACK = ({call}.CALLBACK)',
        f'{resumed}.STORE[n_cell] = DEFINED (PINT 42)' if constrained else f'{resumed}.STORE[n_cell] = DEFINED ({string(changed)})',
        f'$property_get_string_long_valid({resumed}, {record})']
    if constrained:
        checks += [f'{resumed}.PROPREFS = S_return.PROPREFS',
            f'$propref_at({resumed}.PROPREFS, n_cell) = (ppropref)', f'$proprefs_valid({resumed})',
            f'$typed_conversion_at({resumed}, ppropertydesc_get.TYPE, PINT 42, true) = TYPEVALUE (PINT 42)']
    return checks


def commit(state='S_long', suffix='', ref=True):
    record, selected = 'ppropertystringlong'+suffix, 'pvalue_long'+suffix
    committed, finished = 'S_committed'+suffix, 'S_finished'+suffix
    change = f'.STORE[n_cell] = DEFINED {selected}][.RESULT = REFERENCE n_cell' if ref else f'.RESULT = KNOWN {selected}'
    operand = 'REFERENCE n_cell' if ref else f'KNOWN {selected}'
    return [f'{committed} = $property_get_string_long_commit({state}, {record})',
        f'{committed} = {state}[{change}]', f'{committed}.STRINGDATA = {state}.STRINGDATA',
        f'{finished} = $property_get_string_long_finish({state}, {record})',
        f'{finished} = {committed}[.TODO = (PROPERTY_GET_COPY {record}.GET ({operand})) :: {record}.TAIL][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        *budget(state,finished)]


def guards(state='S_long', suffix=''):
    record = 'ppropertystringlong'+suffix
    checks=[]
    for label, field, value in [
        ('known','INPUT','KNOWN (PINT 7)'),
        ('known_string','INPUT','KNOWN ('+string('8.5')+')'),
        ('float','STRING',f'PFLOAT {F75}'),
        ('integral','STRING',string('7.0')),
        ('prefix','STRING',string('7.5suffix')),
        ('range','STRING',string('1e309')),
        ('carrier','STRING','PSTRING_CARRIER (REQUEST_STRING (|'+state+'.STRINGDATA|)) ($ptascii(" 7.50e0 "))'),
        ('integer','INTEGER','8'),
        ('owner','OWNER',f'$(|{state}.FRAMES| + 1)'),
        ('tail','TAIL','eps'),
        ('line','GET',f'{record}.GET[.LINE = $({record}.GET.LINE + 1)]')]:
        checks += [f'ppropertystringlong_bad_{label} = {record}[.{field} = {value}]',
            f'S_bad_{label} = {state}[.TODO = (PROPERTY_GET_STRING_LONG ppropertystringlong_bad_{label}) :: {record}.TAIL]',
            f'~$property_get_string_long_valid(S_bad_{label}, ppropertystringlong_bad_{label})']
    return checks + [f'~$property_get_string_long_valid({state}[.ORIGIN = ({record}.GET.METHOD)], {record})',
        f'S_bad_parameter = {state}[.PARAMETERBACKINGS = [{{FUNCTION {record}.GET.METHOD, INDEX 0, CELL n_cell, LINE {record}.GET.LINE, VALUE ($ptascii("string"))}}]]',
        f'~$property_get_string_long_valid(S_bad_parameter, {record})',
        f'S_grown = {state}[.STRINGDATA = {state}.STRINGDATA ++ [($ptascii("unrelated43"))]]',
        f'$property_get_string_long_valid(S_grown, {record})',
        f'$property_get_string_long_finish(S_grown, {record}) = S_grown[.STORE[n_cell] = DEFINED (PINT 7)][.TODO = (PROPERTY_GET_COPY {record}.GET (REFERENCE n_cell)) :: {record}.TAIL][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]']

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



def constructed_exclusions():
    # Direct-helper authority controls; generic range clones remain at the timed-out cut.
    quiet='PSTRING ($ptascii("7.0"))'
    return ['$property_get_verify(S_return, ppropertyget, S_return.RESULT) = S_return[.COMPLETION = UNSUPPORTED "magic getter property type coercion"]',
        f'$property_get_verify_value(S_return, ppropertyget, ppropertydesc_get, {quiet}, TYPEINTEGER ({quiet})) = S_return[.COMPLETION = UNSUPPORTED "magic getter property type coercion"]',
        f'S_quiet_control = S_return[.RESULT = KNOWN ({quiet})]',
        'ppropertydesc_wrong_type = ppropertydesc_get[.TYPE = [(PTBRANCH ([PTBUILTIN "float"]))]]',
        f'$property_get_verify_value(S_quiet_control, ppropertyget, ppropertydesc_wrong_type, {quiet}, TYPEINTEGER ({quiet})) = S_quiet_control[.COMPLETION = UNSUPPORTED "magic getter property type coercion"]',
        f'$property_get_verify_value(S_quiet_control, ppropertyget, ppropertydesc_get, {quiet}, TYPEVALUE (PINT 7)) = S_quiet_control[.COMPLETION = UNSUPPORTED "magic getter property type coercion"]',
        'S_invalid_carrier = S_return[.RESULT = KNOWN (PSTRING_CARRIER (REQUEST_STRING (|S_return.STRINGDATA|)) ($ptascii("7.0")))]',
        '$property_get_verify(S_invalid_carrier, ppropertyget, S_invalid_carrier.RESULT) = S_invalid_carrier[.COMPLETION = UNSUPPORTED "magic getter property type coercion"]',
        '$property_get_complete(S_return, ppropertyget, KNOWN (PINT 7)) = S_return[.TODO = (PROPERTY_GET_COPY ppropertyget (REFERENCE n_cell)) :: ptask_return_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]']

def exact_source_first():
    return ['$property_get_verify(S_exact_return, ppropertyget_exact, S_exact_return.RESULT) = S_exact_return',
        'S_exact_completed = $property_get_complete(S_exact_return, ppropertyget_exact, S_exact_return.RESULT)',
        'S_exact_completed = S_exact_return[.TODO = (PROPERTY_GET_COPY ppropertyget_exact (REFERENCE n_cell)) :: ptask_exact_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        *budget('S_exact_return','S_exact_completed'),
        '$propref_descriptor(S_exact_return, pproptypesource_first) = (ppropertydesc_source)',
        'S_exact_global = $global_table_view(S_exact_return)',
        '$trace_slot(S_exact_global, S_exact_global.ENV, $ptascii("holder")) = POBJECT n_holder',
        '$objectprops_at(S_exact_return.OBJECTPROPS, n_holder) = (ppropertyslot_source_all*)',
        '$property_slot_at(ppropertyslot_source_all*, $ptascii("slot")) = (ppropertyslot_source)',
        'ppropertyslot_source.STATE = PROP_VALUE (ALIAS n_cell)',
        *integer.seek('S_exact_return','S_copy_exact',2),
        'S_copy_exact.TODO = (PROPERTY_GET_COPY ppropertyget_exact (REFERENCE n_cell)) :: ptask_copy_exact_tail*',
        'S_copy_exact.PROPREFS = S_exact_return.PROPREFS',
        'S_copy_exact.OBJECTPROPS = S_exact_return.OBJECTPROPS',
        *get.step('S_copy_exact','S_receiving_exact'), *integer.seek('S_receiving_exact','S_received_exact',5),
        'S_received_exact.TODO = ptask_copy_exact_tail*', 'S_received_exact.RESULT = KNOWN (PINT 7)',
        'S_received_exact.STORE[n_cell] = DEFINED (PINT 7)',
        'S_received_exact.PROPREFS = S_exact_return.PROPREFS',
        *integer.seek('S_received_exact','S_before_second',0,'0'),
        '$property_get_plan(S_before_second) = (ppropertyget)',
        'ppropertyget.OBJECT = n_reader', 'ppropertyget.SITE =/= ppropertyget_exact.SITE',
        'S_before_second.STORE[n_cell] = DEFINED (PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii(" 7.50e0 ")))',
        *integer.seek('S_before_second','S_return',1),
        'S_return.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_return_tail*',
        'S_return.RESULT = REFERENCE n_cell', 'pvalue_raw = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii(" 7.50e0 "))',
        'S_return.STORE[n_cell] = DEFINED pvalue_raw', 'S_return.PROPREFS = S_exact_return.PROPREFS',
        '$property_get_propref(S_return, ppropertyget, n_cell)',
        '$propref_class(S_return, ppropertydesc_get.TYPE, pvalue_raw, false) = PROP_POSSIBLE',
        '$heap_owners($heap_graph(S_return), HOBJECT n_reader) = 1',
        '$typed_conversion_at(S_return, ppropertydesc_source.TYPE, pvalue_raw, true) = TYPEVALUE pvalue_raw',
        '$typed_conversion_at(S_return, ppropertydesc_source.TYPE, PINT 42, true) = TYPEVALUE (PINT 42)']


def kept(source, expected):
    checks = [*dispatch(handler=False), *integer.seek('S_dispatch','S_long',7),
        'S_long = S_dispatch', *commit(ref=True), *guards(),
        *integer.seek('S_long','S_copy',2),
        'S_copy.TODO = (PROPERTY_GET_COPY ppropertyget (REFERENCE n_cell)) :: ptask_copy_tail*',
        'S_copy.STORE[n_cell] = DEFINED pvalue_long',
        '$heap_owners($heap_graph(S_copy), HOBJECT n_reader) = 1',
        *get.step('S_copy','S_receiving'), *integer.seek('S_receiving','S_received',5),
        'S_received.TODO = ptask_copy_tail*', 'S_received.RESULT = KNOWN pvalue_long',
        *kept_finish('S_received',expected)]
    return checks

def handled_start(run, eval_checks):
    return ['S_initial = '+run, '~S_initial.COMPILESTOP', *eval_checks,
        *integer.seek('S_resumed','S_before_first',0,'0'),
        '$property_get_plan(S_before_first) = (ppropertyget_first)',
        'n_reader = ppropertyget_first.OBJECT',
        '$property_get_history(S_before_first, ppropertyget_first)',
        '$heap_owners($heap_graph(S_before_first), HOBJECT n_reader) = 1']


def handled():
    # The first masked conversion is driven, rather than replaying its checked metadata.
    return [*integer.seek('S_before_first','S_first_return',1),
        *integer.seek('S_first_return','S_before_handled',0,'0'),
        '$property_get_plan(S_before_handled) = (ppropertyget)',
        'ppropertyget.OBJECT = n_reader', 'ppropertyget.SITE =/= ppropertyget_first.SITE',
        'S_before_handled.REPORTING = 0',
        *integer.seek('S_before_handled','S_return',1),
        'S_return.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_return_tail*',
        'S_return.RESULT = REFERENCE n_cell',
        'S_return.STORE[n_cell] = DEFINED (PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii(" 7.50e0 ")))',
        '$property_desc_at($property_layout(S_return, ppropertyget.CLASS, |S_return.CLASSES|), ppropertyget.NAME) = (ppropertydesc_get)',
        '$property_get_unconstrained(S_return, S_return.RESULT)',
        '$heap_owners($heap_graph(S_return), HOBJECT n_reader) = 2',
        *dispatch('S_return','ppropertyget','ptask_return_tail*','_handled'),
        *constructed_exclusions()]


def resumed(expected):
    prefix = cross.invoke.byte_expr(expected.split('handled|',1)[0].encode())
    return [*integer.seek('S_before_first','S_long_handled',11),
        'S_long_handled.TODO = (PROPERTY_GET_STRING_LONG ppropertystringlong_handled) :: ptask_handled_tail*',
        'ppropertyget_handled = ppropertystringlong_handled.GET',
        'ppropertyget_handled.OBJECT = n_reader', 'ppropertyget_handled.SITE =/= ppropertyget_first.SITE',
        'ppropertystringlong_handled.INPUT = REFERENCE n_cell',
        'ppropertystringlong_handled.STRING = PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii(" 7.50e0 "))',
        'ppropertystringlong_handled.INTEGER = 7', 'ppropertystringlong_handled.SOURCES = eps',
        'ppropertystringlong_handled.TAIL = ptask_handled_tail*',
        'ppropertystringlong_handled.OWNER = |S_long_handled.FRAMES|',
        '$property_get_string_long_valid(S_long_handled, ppropertystringlong_handled)',
        'S_long_handled.STORE[n_cell] = DEFINED ('+string('handler-kept43')+')',
        'S_long_handled.ERRORHANDLER.CALLBACK = ('+string('magic_numeric_string_integer_kept_handler43')+')',
        'S_long_handled.REPORTING = 0',
        '$heap_owners($heap_graph(S_long_handled), HOBJECT n_reader) = 2',
        '$get_test_output(S_long_handled.EVENTS) = '+prefix,
        'pvalue_long_handled = PINT 7', *commit('S_long_handled','_handled'),
        *integer.seek('S_long_handled','S_copy_handled',2),
        'S_copy_handled.TODO = (PROPERTY_GET_COPY ppropertyget_handled (REFERENCE n_cell)) :: ptask_copy_handled_tail*',
        'S_copy_handled.STORE[n_cell] = DEFINED (PINT 7)',
        *get.step('S_copy_handled','S_receiving_handled'), *integer.seek('S_receiving_handled','S_received_handled',5),
        'S_received_handled.TODO = ptask_copy_handled_tail*', 'S_received_handled.RESULT = KNOWN (PINT 7)',
        'S_received_handled.STORE[n_cell] = DEFINED (PINT 7)',
        '$heap_owners($heap_graph(S_received_handled), HOBJECT n_reader) = 1',
        '$heap_owners($heap_graph(S_received_handled), HCELL n_cell) = 2',
        'S_received_handled.ERRORHANDLER.CALLBACK = S_long_handled.ERRORHANDLER.CALLBACK',
        '$get_test_output(S_received_handled.EVENTS) = '+prefix,
        '$trace_slot($global_table_view(S_received_handled), $global_table_view(S_received_handled).ENV, $ptascii("warnings")) = PINT 1']


def kept_finish(parent, expected):
    return [*get.finish(parent,expected),
        '$trace_slot(S_done, S_done.ENV, $ptascii("masked")) = PINT 7',
        '$trace_slot(S_done, S_done.ENV, $ptascii("handled")) = PINT 7',
        '$trace_slot(S_done, S_done.ENV, $ptascii("exact")) = PINT 7',
        '$trace_slot(S_done, S_done.ENV, $ptascii("zero")) = PINT 0',
        '$trace_slot(S_done, S_done.ENV, $ptascii("alias")) = '+string('after-kept43'),
        '$trace_slot(S_done, S_done.ENV, $ptascii("gets")) = PINT 5',
        '$trace_slot(S_done, S_done.ENV, $ptascii("drops")) = PINT 1',
        '$trace_slot(S_done, S_done.ENV, $ptascii("warnings")) = PINT 1']


def quiet_return(phase, raw):
    return [*integer.seek('S_before_first','S_return',phase),
        'S_return.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_return_tail*',
        'ppropertyget.OBJECT = n_reader', 'ppropertyget.SITE =/= ppropertyget_first.SITE',
        'S_return.RESULT = REFERENCE n_cell',
        'pvalue_raw = '+string(raw), 'S_return.STORE[n_cell] = DEFINED pvalue_raw',
        'S_return.BASE = BASE_VALUE (KNOWN PNULL)', 'S_return.ORIGIN = (ppropertyget.SITE)',
        '$property_get_valid(S_return, ppropertyget, true)', '$property_get_tail_valid(S_return, ppropertyget)',
        'S_return.ERRORHANDLER.CALLBACK = eps',
        '$heap_owners($heap_graph(S_return), HOBJECT n_reader) = 2',
        '$trace_slot($global_table_view(S_return), $global_table_view(S_return).ENV, $ptascii("warnings")) = PINT 1']


def quiet_kept(expected, zero=False):
    raw, bits, i, phase, marker = ('-0.0',FNEGZERO,0,13,'zero|') if zero else ('7.0',F7,7,12,'exact|')
    prefix = cross.invoke.byte_expr(expected.split(marker,1)[0].encode())
    return [*quiet_return(phase,raw),
        f'$typed_number(pvalue_raw) = (NFLOAT {bits})',
        '~$property_get_string_long_ready(S_return, ppropertyget)',
        f'$float_long({bits}, true) = ({i}, eps)',
        'S_verified = $property_get_verify(S_return, ppropertyget, S_return.RESULT)',
        f'S_verified = S_return[.STORE[n_cell] = DEFINED (PINT {i})][.RESULT = REFERENCE n_cell]',
        '$property_get_verify(S_verified, ppropertyget, S_verified.RESULT) = S_verified',
        'S_completed = $property_get_complete(S_return, ppropertyget, S_return.RESULT)',
        'S_completed = S_verified[.TODO = (PROPERTY_GET_COPY ppropertyget (REFERENCE n_cell)) :: ptask_return_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        *budget('S_return','S_completed'),
        *integer.seek('S_return','S_copy',2),
        'S_copy.TODO = (PROPERTY_GET_COPY ppropertyget (REFERENCE n_cell)) :: ptask_copy_tail*',
        f'S_copy.STORE[n_cell] = DEFINED (PINT {i})',
        *get.step('S_copy','S_receiving'), *integer.seek('S_receiving','S_received',5),
        'S_received.TODO = ptask_copy_tail*', f'S_received.RESULT = KNOWN (PINT {i})',
        f'S_received.STORE[n_cell] = DEFINED (PINT {i})',
        'S_received.STRINGDATA = S_return.STRINGDATA',
        '$heap_owners($heap_graph(S_received), HOBJECT n_reader) = 1',
        '$heap_owners($heap_graph(S_received), HCELL n_cell) = 2',
        '$trace_slot($global_table_view(S_received), $global_table_view(S_received).ENV, $ptascii("warnings")) = PINT 1',
        '$get_test_output(S_received.EVENTS) = '+prefix]


def prefix_read(expected):
    message = cross.invoke.byte_expr(expected.split('prefix=',1)[1].split('/prior=',1)[0].encode())
    return [*quiet_return(14,'7.5suffix'),
        '~$property_get_string_long_ready(S_return, ppropertyget)',
        '$typed_number(pvalue_raw) = eps',
        'S_verified = $property_get_verify(S_return, ppropertyget, S_return.RESULT)',
        'S_verified = S_return[.COMPLETION = THROWN "TypeError" ('+message+') ppropertyget.LINE]',
        'S_completed = $property_get_complete(S_return, ppropertyget, S_return.RESULT)',
        'S_completed = S_verified[.TODO = (PROPERTY_GET_COPY ppropertyget (REFERENCE n_cell)) :: ptask_return_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        *budget('S_return','S_completed'),
        *integer.seek('S_return','S_error_copy',6),
        'S_error_copy.TODO = (THROW_SEARCH n_type_error) :: (PROPERTY_GET_COPY ppropertyget (REFERENCE n_cell)) :: ptask_error_tail*',
        'S_error_copy.STORE[n_cell] = DEFINED pvalue_raw',
        '$get_test_message(S_error_copy, n_type_error, '+message+')',
        '$throwable_previous_id(S_error_copy, n_type_error) = eps',
        *integer.seek('S_error_copy','S_error_materialized',15),
        'S_error_materialized.TODO = (THROW_SEARCH n_type_error) :: (PROPERTY_GET_DROP ppropertyget pvalue_raw) :: ptask_error_tail*',
        *get.step('S_error_materialized','S_error_dropped'),
        'S_error_dropped.TODO = (THROW_SEARCH n_type_error) :: ptask_error_tail*',
        'S_error_dropped.STORE[n_cell] = DEFINED pvalue_raw',
        '$get_test_message(S_error_dropped, n_type_error, '+message+')',
        '$throwable_previous_id(S_error_dropped, n_type_error) = eps',
        '$heap_owners($heap_graph(S_error_dropped), HOBJECT n_reader) = 1',
        '$heap_owners($heap_graph(S_error_dropped), HCELL n_cell) = 2']


def ordinary(group, expected):
    owned = group=='owned'
    changed = 'handler-owned43' if owned else 'handler-value43'
    checks = [*dispatch(), *callback(changed=changed), *commit(ref=owned)]
    if owned:
        checks += [*integer.seek('S_long','S_copy',2),
            'S_copy.TODO = (PROPERTY_GET_COPY ppropertyget (REFERENCE n_cell)) :: (PROPERTY_GET_BASE ppropertyget) :: ptask_base_tail*',
            'S_copy.STORE[n_cell] = DEFINED pvalue_long',
            *integer.seek('S_copy','S_base',3),
            'S_base.RESULT = KNOWN pvalue_long', 'S_base.STORE[n_cell] = DEFINED pvalue_long',
            '$heap_owners($heap_graph(S_base), HOBJECT n_reader) = 1',
            '$heap_owners($heap_graph(S_base), HCELL n_cell) = 1',
            *reader('S_base'), 'pdestructionoperation_reader.SOURCE = PROPERTY_GET_BASE ppropertyget',
            'pdestructionoperation_reader.VALUE = KNOWN pvalue_long',
            'S_reader_dtor.STORE[n_cell] = DEFINED pvalue_long']
    else:
        checks += [*reader('S_long'),
            '$get_test_frame_copy(S_reader_dtor.FRAMES) = ((ppropertyget, KNOWN pvalue_long))',
            'S_reader_dtor.STORE[n_cell] = DEFINED ('+string(changed)+')']
    checks += [*get.finish('S_reader_dtor',expected), '$weakref_get(S_done, n_weak) = PNULL',
        '$trace_slot(S_done, S_done.ENV, $ptascii("value")) = pvalue_long',
        '$trace_slot(S_done, S_done.ENV, $ptascii("cell")) = PBOOL '+str(owned).lower(),
        '$trace_slot(S_done, S_done.ENV, $ptascii("warnings")) = PINT 1']
    return checks


def conflict(expected):
    message = cross.invoke.byte_expr(expected.split('caught=',1)[1].split('/prior=',1)[0].encode())
    return [*exact_source_first(), *dispatch(constrained=True), *callback(changed='handler-source43',constrained=True),
        '$property_get_string_long_commit(S_long, ppropertystringlong) = S_long[.COMPLETION = THROWN "TypeError" ('+message+') ppropertyget.LINE]',
        'S_finished = $property_get_string_long_finish(S_long, ppropertystringlong)',
        'S_finished = S_long[.TODO = (PROPERTY_GET_COPY ppropertyget (REFERENCE n_cell)) :: ptask_return_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)][.COMPLETION = THROWN "TypeError" ('+message+') ppropertyget.LINE]',
        *budget('S_long','S_finished'),
        'ppropertystringlong_bad_source = ppropertystringlong[.SOURCES = eps]',
        '~$property_get_string_long_valid(S_long[.TODO = (PROPERTY_GET_STRING_LONG ppropertystringlong_bad_source) :: ptask_return_tail*], ppropertystringlong_bad_source)',
        *integer.seek('S_long','S_reader_dtor',4),
        'S_reader_dtor.CURRENT = (pcallcontext_reader)',
        '$destructor_context_call(pcallcontext_reader, S_reader_dtor.CURRENT, S_reader_dtor.FRAMES) = (pdestructorcall_reader)',
        'pdestructorcall_reader.OPERATION = (pdestructionoperation_reader)',
        'pdestructionoperation_reader.PENDING = (n_type_error)',
        '$get_test_message(S_reader_dtor, n_type_error, '+message+')',
        'S_reader_dtor.STORE[n_cell] = DEFINED (PINT 42)',
        '$propref_at(S_reader_dtor.PROPREFS, n_cell) = (ppropref)',
        *integer.seek('S_reader_dtor','S_error_copy',6),
        'S_error_copy.TODO = (THROW_SEARCH n_type_error) :: (PROPERTY_GET_COPY ppropertyget (REFERENCE n_cell)) :: ptask_error_tail*',
        'S_error_copy.STORE[n_cell] = DEFINED ('+string('repaired-source43')+')',
        '$propref_at(S_error_copy.PROPREFS, n_cell) = eps',
        '$get_test_message(S_error_copy, n_type_error, '+message+')',
        '$throwable_previous_id(S_error_copy, n_type_error) = eps',
        *get.finish('S_error_copy',expected), '$lookup(S_done.ENV, $ptascii("value")) = eps',
        '$trace_slot(S_done, S_done.ENV, $ptascii("alias")) = '+string('repaired-source43')]


def throwing(expected):
    return [*dispatch(), *integer.seek('S_dispatch','S_throw',10),
        'S_throw.TODO = (THROW_SEARCH n_warning) :: (ERROR_HANDLER_RESULT perrorcall_throw) :: ptask_return_tail*',
        'perrorcall_throw.RESUME = PROPERTY_GET_STRING_LONG ppropertystringlong',
        '$get_test_message(S_throw, n_warning, $ptascii("warning43"))',
        'S_throw.STORE[n_cell] = DEFINED ('+string('handler-throw43')+')',
        'S_discard_input = S_throw[.TODO = (THROW_SEARCH n_warning) :: ptask_return_tail*]',
        'S_abrupt = $property_get_string_long_abrupt(S_discard_input, ppropertystringlong)',
        'S_abrupt = S_discard_input[.TODO = (THROW_SEARCH n_warning) :: (PROPERTY_GET_COPY ppropertyget (REFERENCE n_cell)) :: ptask_return_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        '$error_read_discard(S_discard_input, PROPERTY_GET_STRING_LONG ppropertystringlong) = S_abrupt',
        'S_wrapper_abrupt = S_abrupt[.ERRORHANDLER.CALLBACK = (perrorcall_throw.CALLBACK)]',
        '$return_discard(S_discard_input, ERROR_HANDLER_RESULT perrorcall_throw) = S_wrapper_abrupt',
        *budget('S_throw','S_wrapper_abrupt'),
        *reader('S_throw','(n_warning)'),
        'S_reader_dtor.STORE[n_cell] = DEFINED ('+string('handler-throw43')+')',
        '$get_test_frame_copy(S_reader_dtor.FRAMES) = ((ppropertyget, REFERENCE n_cell))',
        '$get_test_message(S_reader_dtor, n_warning, $ptascii("warning43"))',
        *integer.seek('S_reader_dtor','S_error_copy',6),
        'S_error_copy.TODO = (THROW_SEARCH n_cleanup) :: (PROPERTY_GET_COPY ppropertyget (REFERENCE n_cell)) :: ptask_error_tail*',
        '$get_test_message(S_error_copy, n_cleanup, $ptascii("cleanup43"))',
        '$throwable_previous_id(S_error_copy, n_cleanup) = (n_warning)',
        '$throwable_previous_id(S_error_copy, n_warning) = eps',
        'S_error_copy.STORE[n_cell] = DEFINED ('+string('repaired-throw43')+')',
        *get.finish('S_error_copy',expected), '$lookup(S_done.ENV, $ptascii("value")) = eps',
        '$weakref_get(S_done, n_weak) = PNULL']


def strict(expected):
    message = cross.invoke.byte_expr(expected.split('caught=',1)[1].split('/prior=',1)[0].encode())
    return ['~$property_get_string_long_ready(S_return, ppropertyget)',
        '$typed_conversion_at(S_return, ppropertydesc_get.TYPE, pvalue_raw, true) = TYPEREJECT',
        'S_verified = $property_get_verify(S_return, ppropertyget, S_return.RESULT)',
        'S_verified = S_return[.COMPLETION = THROWN "TypeError" ('+message+') ppropertyget.LINE]',
        'S_finished = $property_get_complete(S_return, ppropertyget, S_return.RESULT)',
        'S_finished = S_verified[.TODO = (PROPERTY_GET_COPY ppropertyget (REFERENCE n_cell)) :: ptask_return_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        *budget('S_return','S_finished'), *reader('S_return','(n_type_error)'),
        'S_reader_dtor.STORE[n_cell] = DEFINED pvalue_raw',
        '$get_test_message(S_reader_dtor, n_type_error, '+message+')',
        *integer.seek('S_reader_dtor','S_error_copy',6),
        'S_error_copy.STORE[n_cell] = DEFINED ('+string('repaired-strict43')+')',
        '$throwable_previous_id(S_error_copy, n_type_error) = eps',
        *get.finish('S_error_copy',expected),
        '$trace_slot(S_done, S_done.ENV, $ptascii("warnings")) = PINT 0', '$weakref_get(S_done, n_weak) = PNULL']


def body(run, source, expected, group, eval_checks=()):
    if group=='reference-handled': return handled_start(run,eval_checks)+handled()
    if group=='reference-resume': return handled_start(run,eval_checks)+resumed(expected)
    if group in ('reference-quiet','reference-zero'): return handled_start(run,eval_checks)+quiet_kept(expected,group=='reference-zero')
    if group=='reference-prefix': return handled_start(run,eval_checks)+prefix_read(expected)
    checks=start(run,source,'reference-kept' if group in ('reference-quiet','reference-handled') else group,eval_checks)
    if group=='source-conflict':
        checks=[row.replace('S_return','S_exact_return').replace('ppropertyget','ppropertyget_exact').replace('ptask_return_tail*','ptask_exact_tail*').replace('pvalue_raw','pvalue_exact') for row in checks]
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
    out = Path(tempfile.mkdtemp(prefix='magic-property-numeric-string-integer-', dir=ROOT/'.tools'))
    report = {'before': before, 'profile': cross.invoke.types.PROFILE, 'passed': False,
        'native_evaluations': 0, 'model_evaluations': 0, 'state_assertions_evaluated': 0,
        'runner_mode': 'SL', 'numeric_cap_seconds': 120, 'case': CASES[args.group], 'jobs': 1}
    print(out, flush=True)
    try:
        original = sources.CASES[CASES[args.group]]
        source = out/'source.php'; source.write_bytes(original)
        sources.prepare(out, source)
        eval_checks = integer.prepare_eval(out, 'weak-getter' if args.group in ('reference-kept', 'reference-quiet', 'reference-handled', 'reference-resume', 'reference-zero', 'reference-prefix') else args.group)
        run = '$php_run(program_source,0,'+json.dumps(base64.b64encode(os.fsencode(source)).decode())+')'
        clauses = ['program_source = '+(out/'program.watsup').read_text().strip(), *body(run, original, sources.EXPECTED[CASES[args.group]], args.group, eval_checks)]
        fixture = out/'protocol.watsup'
        fixture.write_text(PREFIX+(QUIET_PHASE if args.group=='reference-resume' else '')+(QUIET_VALUE_PHASE if args.group in ('reference-quiet','reference-zero','reference-prefix') else '')+(DROP_PHASE if args.group=='reference-prefix' else '')+'dec $body() : bool\ndef $body() = true\n'+
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
