#!/usr/bin/env python3
"""Source-reached weak non-NaN float-to-string magic getters and string carriers."""
import argparse
import base64
import json
import os
from pathlib import Path
import tempfile

import dynamic_property_warning_sources as sources
import magic_property_get_protocol as get
import magic_property_integer_protocol as integer
import magic_property_float_protocol as floating
import magic_property_reference_protocol as reference
import magic_property_boolean_string_protocol as boolean_string
import magic_property_integer_string_protocol as integer_string

cross, ROOT = sources.cross, sources.ROOT
CASES = {
    'reference-kept': 'review-property-magic-float-string-reference-kept40',
    'reference-format': 'review-property-magic-float-string-reference-format40',
    'reference-drop': 'review-property-magic-float-string-reference-drop40',
    'value': 'review-property-magic-float-string-value40',
    'owned': 'review-property-magic-float-string-owned40',
    'source-conflict': 'review-property-magic-float-string-source-conflict40',
    'strict-getter': 'review-property-magic-float-string-strict-getter40',
}
# Fixed binary64 values and bytes are independent of the formatting algorithm.
DIGIT, ZERO, NEGATIVE_ZERO = 4619567317775286272, 0, 9223372036854775808
DECIMAL, PRECISION = 4591870180066957722, 4593560419846153055
INFINITY, NEGATIVE_INFINITY = 9218868437227405312, 18442240474082181120
RAW = {'reference-kept': DIGIT, 'reference-format': PRECISION, 'reference-drop': DECIMAL, 'value': DIGIT,
       'owned': NEGATIVE_ZERO, 'source-conflict': DECIMAL, 'strict-getter': DECIMAL}
BYTES = {DIGIT: '7', ZERO: '0', NEGATIVE_ZERO: '-0', DECIMAL: '0.1',
         PRECISION: '0.123457', INFINITY: 'INF', NEGATIVE_INFINITY: '-INF'}
PREFIX = integer.PREFIX


def value(bits, state='S_return'):
    return f'PSTRING_CARRIER (REQUEST_STRING (|{state}.STRINGDATA|)) ($ptascii("{BYTES[bits]}"))'


def start(run, source, group, eval_checks, exact=False):
    owned, constrained = group == 'owned', group == 'source-conflict'
    kept = group in ('reference-kept', 'reference-format', 'owned') or exact
    line = next(i for i, row in enumerate(source.splitlines(), 1)
        if b' = $reader->value;' in row or b' = magic_float_string_owned_factory40()->value;' in row)
    checks = ['S_initial = '+run, '~S_initial.COMPILESTOP', *eval_checks,
        *integer.seek('S_resumed' if eval_checks else 'S_initial', 'S_before', 0, '0'),
        '$property_get_plan(S_before) = (ppropertyget)', 'n_reader = ppropertyget.OBJECT',
        f'ppropertyget.LINE = {line}', '$property_get_history(S_before, ppropertyget)',
        '$property_get_valid(S_before, ppropertyget, true)',
        '$property_get_owned_source(S_before, ppropertyget)' if owned else '$property_get_source(S_before, ppropertyget)',
        '$heap_owners($heap_graph(S_before), HOBJECT n_reader) = 1',
        *get.step('S_before', 'S_pending'),
        '$heap_owners($heap_graph(S_pending), HOBJECT n_reader) = 2',
        f'$property_get_base_count(S_pending.TODO, n_reader, ppropertyget.SITE) = {int(owned)}',
        *integer.seek('S_pending', 'S_return', 1),
        'S_return.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_return_tail*',
        '$property_get_valid(S_return, ppropertyget, true)', '$property_get_tail_valid(S_return, ppropertyget)',
        '$property_get_method(S_return, n_reader) = (pmethoddesc_get)',
        'pmethoddesc_get.FUNCTION.ORIGIN = ppropertyget.METHOD',
        f'pmethoddesc_get.FUNCTION.CODE.STRICT = {str(group == "strict-getter").lower()}',
        'ppropertyget.SITE = PORIGIN n_caller pcpath_caller',
        '$code_at(S_return.CODE, n_caller) = (pcode_caller)',
        f'pcode_caller.STRICT = {str(group in ("reference-kept", "reference-format")).lower()}',
        '$property_desc_at($property_layout(S_return, ppropertyget.CLASS, |S_return.CLASSES|), ppropertyget.NAME) = (ppropertydesc_get)',
        'ppropertyget.DECL = (ppropertydesc_get.ORIGIN)', 'ppropertydesc_get.READONLY',
        'ppropertydesc_get.TYPE = [(PTBRANCH ([PTBUILTIN "string"]))]',
        '$objectprops_at(S_return.OBJECTPROPS, n_reader) = (ppropertyslot_all*)',
        '$property_slot_at(ppropertyslot_all*, ppropertyget.NAME) = (ppropertyslot_get)',
        'ppropertyslot_get.STATE = PROP_UNSET',
        'S_return_global = $global_table_view(S_return)',
        '$lookup(S_return_global.ENV, $ptascii("returnCell")) = (n_return_cell)',
        'S_return.STORE[n_return_cell] = DEFINED pvalue_raw',
        *(['pvalue_raw = PSTRING_CARRIER INTERNED_STRING ($ptascii("0.1"))', '$typed_string_value(pvalue_raw)'] if exact else [
            f'pvalue_raw = PFLOAT {RAW[group]}', '~$typed_string_value(pvalue_raw)',
            '$property_get_given(S_return, pvalue_raw) = $ptascii("float")']),
        'S_return.RESULT = '+('KNOWN pvalue_raw' if group == 'value' else 'REFERENCE n_return_cell'),
        '$parameter_backing_at(S_return.PARAMETERBACKINGS, n_return_cell) = eps',
        f'$heap_owners($heap_graph(S_return), HOBJECT n_reader) = {2 if kept else 1}',
        f'$heap_owners($heap_graph(S_return), HCELL n_return_cell) = {3 if constrained or group in ("reference-kept", "reference-format") else 1 if group == "value" else 2}']
    if constrained:
        checks += ['$propref_at(S_return.PROPREFS, n_return_cell) = (ppropref)',
            'ppropref.SOURCES = [pproptypesource_first]', '$proprefs_valid(S_return)',
            '$propref_unique_sources(ppropref.SOURCES)',
            '$propref_sources_valid(S_return, n_return_cell, ppropref.SOURCES)',
            '~$property_get_unconstrained(S_return, S_return.RESULT)',
            '$property_get_propref(S_return, ppropertyget, n_return_cell)', *reference.source_slot()]
    else:
        checks += ['$propref_at(S_return.PROPREFS, n_return_cell) = eps',
            '$property_get_unconstrained(S_return, S_return.RESULT)']
    return checks


def verify(bits, ref=True, state='S_return', descriptor='ppropertyget', tail='ptask_return_tail*', suffix='', cell_owners=2, precision=14):
    string = value(bits, state)
    produced = state + f'[.STRINGDATA = {state}.STRINGDATA ++ [($ptascii("{BYTES[bits]}"))]]'
    changed = f'.STORE[n_return_cell] = DEFINED ({string})' if ref else f'.RESULT = KNOWN ({string})'
    operand = 'REFERENCE n_return_cell' if ref else f'KNOWN ({string})'
    verified, completed = 'S_verified'+suffix, 'S_completed'+suffix
    return [f'$({bits} < 18446744073709551616)',
        f'~($float_decode({bits}) = NOTNUMBER {bits})',
        f'$precision_value({state}) = {precision}',
        f'$number_text(NFLOAT {bits}, {precision}) = ($ptascii("{BYTES[bits]}"), false)',
        f'$typed_conversion_at({state}, ppropertydesc_get.TYPE, PFLOAT {bits}, false) = TYPESTRING (PFLOAT {bits})',
        f'$stringify({state}, PFLOAT {bits}, {descriptor}.LINE) = {produced}[.RESULT = KNOWN ({string})]',
        f'{verified} = $property_get_verify({state}, {descriptor}, {state}.RESULT)',
        f'{verified} = {produced}[{changed}]',
        f'$string_carrier_valid({verified}, {string})',
        f'$property_get_verify({verified}, {descriptor}, {verified}.RESULT) = {verified}',
        f'$heap_owners($heap_graph({verified}), HCELL n_return_cell) = {cell_owners}',
        f'{completed} = $property_get_complete({state}, {descriptor}, {state}.RESULT)',
        f'{completed} = {verified}[.TODO = (PROPERTY_GET_COPY {descriptor} ({operand})) :: {tail}][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]']


def boundaries():
    # Constructed guards and selected old maintenance are separate from reached sources.
    checks = []
    for original, marker in [(f'PFLOAT {DIGIT}', f'TYPESTRING (PFLOAT {DECIMAL})'),
                             (f'PFLOAT {DECIMAL}', f'TYPESTRING (PFLOAT {DECIMAL})'),
                             (f'PFLOAT {DIGIT}', f'TYPEINTEGER (PFLOAT {DIGIT})')]:
        checks += [f'$property_get_verify_value(S_return, ppropertyget, ppropertydesc_get, {original}, {marker}) = S_return[.COMPLETION = UNSUPPORTED "magic getter property type coercion"]']
    checks += ['ppropertydesc_wrong = ppropertydesc_get[.TYPE = [(PTBRANCH ([PTBUILTIN "float"]))]]',
        f'$property_get_verify_value(S_return, ppropertyget, ppropertydesc_wrong, PFLOAT {DIGIT}, TYPESTRING (PFLOAT {DIGIT})) = S_return[.COMPLETION = UNSUPPORTED "magic getter property type coercion"]']
    for tag, original in [('null', 'PNULL'), ('range', 'PFLOAT 18446744073709551616'),
                          ('nan', 'PFLOAT 9221120237041090560'), ('negative_nan', 'PFLOAT 18444492273895866368')]:
        checks += [f'S_bad_{tag} = S_return[.RESULT = KNOWN ({original})]',
            f'$property_get_verify_value(S_bad_{tag}, ppropertyget, ppropertydesc_get, {original}, TYPESTRING ({original})) = S_bad_{tag}[.COMPLETION = UNSUPPORTED "magic getter property type coercion"]']
    checks += ['S_invalid_rv = S_return[.RESULT = REFERENCE (|S_return.STORE|)]',
        '~$call_reference_operand_valid(S_invalid_rv, S_invalid_rv.RESULT)',
        '$property_get_verify_value(S_invalid_rv, ppropertyget, ppropertydesc_get, pvalue_raw, TYPESTRING pvalue_raw) = S_invalid_rv[.COMPLETION = UNSUPPORTED "magic getter property type coercion"]',
        'S_backed = S_return[.PARAMETERBACKINGS = [{FUNCTION ppropertyget.METHOD, INDEX 0, CELL n_return_cell, LINE ppropertyget.LINE, VALUE ($ptascii("float"))}]]',
        '~$property_get_unconstrained(S_backed, S_backed.RESULT)',
        '$property_get_verify_value(S_backed, ppropertyget, ppropertydesc_get, pvalue_raw, TYPESTRING pvalue_raw) = S_backed[.COMPLETION = UNSUPPORTED "magic getter property type coercion"]',
        '$property_get_verify(S_backed, ppropertyget, S_backed.RESULT) = S_backed[.COMPLETION = UNSUPPORTED "magic getter typed reference sources"]']
    legacy = [clause.replace('S_bad_float', 'S_legacy_integer_string_float')
              for clause in integer_string.boundaries() if 'S_bad_float' in clause]
    assert len(legacy) == 2
    return checks + legacy


def kept(expected, formatting=False):
    bits, precision = (PRECISION, 6) if formatting else (DIGIT, 14)
    first = value(bits)
    checks = ['$precision_value(S_before) = 14', *verify(bits, cell_owners=3, precision=precision),
        *([] if formatting else boundaries()),
        '$drive_steps(S_return, 0) = S_return[.COMPLETION = BUDGET]',
        '$drive_steps(S_return, 1) = $gc_transition_owners(S_return, $destruction_transition_owners(S_return, $sensitive_trace_freeze($source_exception_transition(S_return, $throwable_transition(S_return, S_completed)))))[.COMPLETION = BUDGET]',
        *floating.copied('S_return', value=first, alive=True), *integer.receive(),
        f'S_received.RESULT = KNOWN ({first})',
        '$heap_owners($heap_graph(S_received), HCELL n_return_cell) = 2']
    parent, prior_descriptor = 'S_received', 'ppropertyget'
    reads = [('infinity', INFINITY, 6), ('negative_infinity', NEGATIVE_INFINITY, 6)] if formatting else [('zero', ZERO, 14), ('negative_zero', NEGATIVE_ZERO, 14)]
    for label, bits, precision in reads:
        before, returned, copy, receiving, received = (f'S_{name}_{label}' for name in ('before', 'return', 'copy', 'receiving', 'received'))
        descriptor, tail = 'ppropertyget_'+label, 'ptask_'+label+'_tail*'
        string = value(bits, returned)
        checks += [*integer.seek(parent, before, 0, '0'),
            f'$property_get_plan({before}) = ({descriptor})',
            f'{descriptor}.OBJECT = n_reader', f'{descriptor}.SITE =/= {prior_descriptor}.SITE',
            f'{before}.STORE[n_return_cell] = DEFINED (PFLOAT {bits})',
            f'$precision_value({before}) = {precision}',
            f'$propref_at({before}.PROPREFS, n_return_cell) = eps',
            f'$parameter_backing_at({before}.PARAMETERBACKINGS, n_return_cell) = eps',
            f'$objectprops_at({before}.OBJECTPROPS, n_reader) = (ppropertyslot_all*)',
            '$property_slot_at(ppropertyslot_all*, ppropertyget.NAME) = (ppropertyslot_get)',
            'ppropertyslot_get.STATE = PROP_UNSET',
            *integer.seek(before, returned, 1),
            f'{returned}.TODO = (PROPERTY_GET_RESULT {descriptor}) :: {tail}',
            f'{returned}.RESULT = REFERENCE n_return_cell',
            f'{returned}.STORE[n_return_cell] = DEFINED (PFLOAT {bits})',
            *verify(bits, state=returned, descriptor=descriptor, tail=tail, suffix='_'+label, cell_owners=3, precision=precision),
            *integer.seek(returned, copy, 2),
            f'{copy}.TODO = (PROPERTY_GET_COPY {descriptor} (REFERENCE n_return_cell)) :: ptask_copy_{label}_tail*',
            f'{copy}.STORE[n_return_cell] = DEFINED ({string})',
            *get.step(copy, receiving), *integer.seek(receiving, received, 5),
            f'{received}.TODO = ptask_copy_{label}_tail*', f'{received}.RESULT = KNOWN ({string})',
            f'{received}.STORE[n_return_cell] = DEFINED ({string})',
            f'$heap_owners($heap_graph({received}), HCELL n_return_cell) = 2']
        if label == 'negative_zero':
            checks += [f'$drive_steps({returned}, 0) = {returned}[.COMPLETION = BUDGET]',
                f'$drive_steps({returned}, 1) = $gc_transition_owners({returned}, $destruction_transition_owners({returned}, $sensitive_trace_freeze($source_exception_transition({returned}, $throwable_transition({returned}, S_completed_{label})))))[.COMPLETION = BUDGET]']
        parent, prior_descriptor = received, descriptor
    if formatting:
        return checks + [*get.finish(parent, expected),
            '$trace_slot(S_done, S_done.ENV, $ptascii("precision")) = '+first,
            '$trace_slot(S_done, S_done.ENV, $ptascii("infinity")) = '+value(INFINITY, 'S_return_infinity'),
            '$trace_slot(S_done, S_done.ENV, $ptascii("negativeInfinity")) = '+value(NEGATIVE_INFINITY, 'S_return_negative_infinity'),
            '$trace_slot(S_done, S_done.ENV, $ptascii("alias")) = '+value(NEGATIVE_INFINITY, 'S_return_negative_infinity'),
            '$precision_value(S_done) = 6',
            '$trace_slot(S_done, S_done.ENV, $ptascii("getCalls")) = PINT 3',
            '$trace_slot(S_done, S_done.ENV, $ptascii("drops")) = PINT 1']
    checks += [*integer.seek(parent, 'S_before_null', 0, '0'),
        '$property_get_plan(S_before_null) = (ppropertyget_null)',
        'ppropertyget_null.OBJECT = n_reader',
        *integer.seek('S_before_null', 'S_return_null', 1),
        'S_return_null.TODO = (PROPERTY_GET_RESULT ppropertyget_null) :: ptask_null_tail*',
        'S_return_null.RESULT = REFERENCE n_return_cell',
        'S_return_null.STORE[n_return_cell] = DEFINED pvalue_null', 'pvalue_null = PNULL',
        '$typed_conversion_at(S_return_null, ppropertydesc_get.TYPE, pvalue_null, false) = TYPEREJECT',
        *boolean_string.error_verify(expected, 'S_return_null', 'ppropertyget_null', 'ptask_null_tail*', 'null='),
        *get.finish('S_return_null', expected),
        'S_done.STORE[n_return_cell] = DEFINED PNULL',
        '$trace_slot(S_done, S_done.ENV, $ptascii("alias")) = PNULL',
        '$trace_slot(S_done, S_done.ENV, $ptascii("first")) = '+first,
        '$trace_slot(S_done, S_done.ENV, $ptascii("zero")) = '+value(ZERO, 'S_return_zero'),
        '$trace_slot(S_done, S_done.ENV, $ptascii("negativeZero")) = '+value(NEGATIVE_ZERO, 'S_return_negative_zero'),
        '$precision_value(S_done) = 14',
        '$trace_slot(S_done, S_done.ENV, $ptascii("getCalls")) = PINT 4']
    return checks


def drop(expected, group):
    ref, i = group == 'reference-drop', RAW[group]
    string = value(i)
    return [*verify(i, ref, cell_owners=2 if ref else 1), *integer.reader('S_return'),
        '$get_test_frame_copy(S_reader_dtor.FRAMES) = ((ppropertyget, poperand_rv))',
        'poperand_rv = '+('REFERENCE n_return_cell' if ref else f'KNOWN ({string})'),
        'S_reader_dtor.STORE[n_return_cell] = DEFINED '+(f'({string})' if ref else 'pvalue_raw'),
        'pdestructionoperation_reader.SOURCE = PROPERTY_GET_RESULT ppropertyget',
        f'$string_carrier_valid(S_reader_dtor, {string})',
        *floating.copied('S_reader_dtor', ref, string),
        'S_copy.STORE[n_return_cell] = DEFINED pvalue_changed',
        '$string_bytes(pvalue_changed) = ($ptascii("changed"))',
        '~((HOBJECT n_reader) <- S_copy.ALLOCATIONS)', *integer.receive(),
        'S_received.RESULT = '+('KNOWN pvalue_changed' if ref else f'KNOWN ({string})'),
        *get.finish('S_received', expected),
        '$trace_slot(S_done, S_done.ENV, $ptascii("read")) = '+('pvalue_changed' if ref else string),
        '$weakref_get(S_done, n_reader_weak) = PNULL']


def owned(expected):
    string = value(NEGATIVE_ZERO)
    return [*verify(NEGATIVE_ZERO), *floating.copied('S_return', value=string, alive=True),
        'ptask_copy_tail* = (PROPERTY_GET_BASE ppropertyget) :: ptask_base_tail*',
        *integer.seek('S_copy', 'S_base', 3), 'S_base.TODO = (PROPERTY_GET_BASE ppropertyget) :: ptask_base_tail*',
        f'S_base.RESULT = KNOWN ({string})', f'S_base.STORE[n_return_cell] = DEFINED ({string})',
        '$heap_owners($heap_graph(S_base), HCELL n_return_cell) = 1',
        '$heap_owners($heap_graph(S_base), HOBJECT n_reader) = 1',
        '$property_get_base_valid(S_base, ppropertyget)',
        *integer.reader('S_base'), 'pdestructionoperation_reader.SOURCE = PROPERTY_GET_BASE ppropertyget',
        f'pdestructionoperation_reader.VALUE = KNOWN ({string})',
        f'S_reader_dtor.STORE[n_return_cell] = DEFINED ({string})',
        *integer.seek('S_reader_dtor', 'S_received', 5), 'S_received.TODO = ptask_base_tail*',
        f'S_received.RESULT = KNOWN ({string})', 'S_received.STORE[n_return_cell] = DEFINED pvalue_changed',
        '$string_bytes(pvalue_changed) = ($ptascii("changed"))',
        '$weakref_get(S_received, n_reader_weak) = PNULL',
        *get.finish('S_received', expected), f'$trace_slot(S_done, S_done.ENV, $ptascii("read")) = {string}']


def rejected(expected, constrained=False):
    message = cross.invoke.byte_expr(expected.split('caught=', 1)[1].split('/prior=', 1)[0].encode())
    checks = ['$typed_conversion_at(S_return, ppropertydesc_get.TYPE, pvalue_raw, false) = TYPESTRING pvalue_raw']
    if constrained:
        string = value(DECIMAL)
        checks += ['$property_type_name(S_return, ppropertydesc_source) = $ptascii("string|float")',
            '$propref_class(S_return, ppropertydesc_get.TYPE, pvalue_raw, false) = PROP_POSSIBLE',
            '$typed_conversion_at(S_return, ppropertydesc_source.TYPE, pvalue_raw, true) = TYPEVALUE pvalue_raw',
            f'$typed_conversion_at(S_return[.STRINGDATA = S_return.STRINGDATA ++ [($ptascii("0.1"))]], ppropertydesc_source.TYPE, {string}, true) = TYPEVALUE ({string})',
            '$property_get_verify_value(S_return, ppropertyget, ppropertydesc_get, pvalue_raw, TYPESTRING pvalue_raw) = S_return[.COMPLETION = UNSUPPORTED "magic getter property type coercion"]',
            '$property_get_propref_possible(S_return, ppropertyget, ppropertydesc_get, PFLOAT 9221120237041090560, pproptypesource_first, TYPESTRING (PFLOAT 9221120237041090560)) = S_return[.COMPLETION = UNSUPPORTED "magic getter constrained reference coercion"]',
            '$property_get_propref_possible(S_return, ppropertyget, ppropertydesc_get, PFLOAT 18446744073709551616, pproptypesource_first, TYPESTRING (PFLOAT 18446744073709551616)) = S_return[.COMPLETION = UNSUPPORTED "magic getter constrained reference coercion"]']
    else:
        checks += ['$typed_conversion_at(S_return, ppropertydesc_get.TYPE, pvalue_raw, true) = TYPEREJECT']
    repaired = 'PSTRING_CARRIER INTERNED_STRING ($ptascii("'+('0.1' if constrained else 'repaired40')+'"))'
    return [*checks, *boolean_string.error_verify(expected), *integer.reader('S_return', '(n_type_error)'),
        '$get_test_frame_copy(S_reader_dtor.FRAMES) = ((ppropertyget, REFERENCE n_return_cell))',
        'S_reader_dtor.STORE[n_return_cell] = DEFINED pvalue_raw',
        '$propref_at(S_reader_dtor.PROPREFS, n_return_cell) = '+('(ppropref)' if constrained else 'eps'),
        '$get_test_message(S_reader_dtor, n_type_error, '+message+')',
        *integer.seek('S_reader_dtor', 'S_error_copy', 6),
        'S_error_copy.TODO = (THROW_SEARCH n_type_error) :: (PROPERTY_GET_COPY ppropertyget (REFERENCE n_return_cell)) :: ptask_error_tail*',
        f'S_error_copy.STORE[n_return_cell] = DEFINED ({repaired})',
        '$propref_at(S_error_copy.PROPREFS, n_return_cell) = eps',
        '$throwable_previous_id(S_error_copy, n_type_error) = eps',
        '$get_test_message(S_error_copy, n_type_error, '+message+')',
        '$weakref_get(S_error_copy, n_reader_weak) = PNULL',
        *get.finish('S_error_copy', expected), '$lookup(S_done.ENV, $ptascii("result")) = eps',
        f'S_done.STORE[n_return_cell] = DEFINED ({repaired})', '$propref_at(S_done.PROPREFS, n_return_cell) = eps']


def conflict_start(run, source, eval_checks):
    first = start(run, source, 'source-conflict', eval_checks, exact=True)
    for old, new in [('S_before', 'S_before_exact'), ('S_pending', 'S_pending_exact'),
                     ('S_return', 'S_return_exact'), ('ppropertyget', 'ppropertyget_exact'),
                     ('pvalue_raw', 'pvalue_exact'), ('ptask_return_tail', 'ptask_exact_tail')]:
        first = [clause.replace(old, new) for clause in first]
    second_line = next(i for i, row in enumerate(source.splitlines(), 1) if b'$result = $reader->value;' in row)
    return [*first,
        '$property_type_name(S_return_exact, ppropertydesc_source) = $ptascii("string|float")',
        '$propref_class(S_return_exact, ppropertydesc_get.TYPE, pvalue_exact, false) = PROP_EXACT',
        '$typed_conversion_at(S_return_exact, ppropertydesc_get.TYPE, pvalue_exact, false) = TYPEVALUE pvalue_exact',
        '$property_get_verify(S_return_exact, ppropertyget_exact, S_return_exact.RESULT) = S_return_exact',
        'S_completed_exact = $property_get_complete(S_return_exact, ppropertyget_exact, S_return_exact.RESULT)',
        'S_completed_exact = S_return_exact[.TODO = (PROPERTY_GET_COPY ppropertyget_exact (REFERENCE n_return_cell)) :: ptask_exact_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        *integer.seek('S_return_exact', 'S_copy_exact', 2),
        'S_copy_exact.TODO = (PROPERTY_GET_COPY ppropertyget_exact (REFERENCE n_return_cell)) :: ptask_copy_exact_tail*',
        'S_copy_exact.STORE[n_return_cell] = DEFINED pvalue_exact',
        'S_copy_exact.PROPREFS = S_return_exact.PROPREFS',
        'S_copy_exact.OBJECTPROPS = S_return_exact.OBJECTPROPS',
        *get.step('S_copy_exact', 'S_receiving_exact'), *integer.seek('S_receiving_exact', 'S_received_exact', 5),
        'S_received_exact.TODO = ptask_copy_exact_tail*', 'S_received_exact.RESULT = KNOWN pvalue_exact',
        'S_received_exact.STORE[n_return_cell] = DEFINED pvalue_exact',
        'S_received_exact.PROPREFS = S_return_exact.PROPREFS',
        'S_received_exact.OBJECTPROPS = S_return_exact.OBJECTPROPS',
        '$heap_owners($heap_graph(S_received_exact), HCELL n_return_cell) = 2',
        '$heap_owners($heap_graph(S_received_exact), HOBJECT n_reader) = 1',
        *integer.seek('S_received_exact', 'S_before', 0, '0'),
        '$property_get_plan(S_before) = (ppropertyget)', 'ppropertyget.OBJECT = n_reader',
        'ppropertyget.SITE =/= ppropertyget_exact.SITE', f'ppropertyget.LINE = {second_line}',
        '$property_get_history(S_before, ppropertyget)',
        '$trace_slot(S_before, S_before.ENV, $ptascii("first")) = pvalue_exact',
        '$trace_slot(S_before, S_before.ENV, $ptascii("getCalls")) = PINT 1',
        '$trace_slot(S_before, S_before.ENV, $ptascii("drops")) = PINT 0',
        'S_before.STORE[n_return_cell] = DEFINED (PFLOAT 4591870180066957722)',
        '$propref_at(S_before.PROPREFS, n_return_cell) = (ppropref)',
        *get.step('S_before', 'S_pending'), *integer.seek('S_pending', 'S_return', 1),
        'S_return.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_return_tail*',
        '$property_get_valid(S_return, ppropertyget, true)', '$property_get_tail_valid(S_return, ppropertyget)',
        'S_return.RESULT = REFERENCE n_return_cell', 'S_return.STORE[n_return_cell] = DEFINED pvalue_raw',
        'pvalue_raw = PFLOAT 4591870180066957722', '$property_get_given(S_return, pvalue_raw) = $ptascii("float")',
        '$propref_at(S_return.PROPREFS, n_return_cell) = (ppropref)', '$proprefs_valid(S_return)',
        '$propref_sources_valid(S_return, n_return_cell, ppropref.SOURCES)',
        '$property_get_propref(S_return, ppropertyget, n_return_cell)',
        '$parameter_backing_at(S_return.PARAMETERBACKINGS, n_return_cell) = eps',
        '$heap_owners($heap_graph(S_return), HCELL n_return_cell) = 3',
        '$heap_owners($heap_graph(S_return), HOBJECT n_reader) = 1', *reference.source_slot()]


def body(run, source, expected, group, eval_checks=()):
    checks = conflict_start(run, source, eval_checks) if group == 'source-conflict' else start(run, source, group, eval_checks)
    if group in ('reference-kept', 'reference-format'):
        return checks + kept(expected, group == 'reference-format')
    if group in ('reference-drop', 'value'):
        return checks + drop(expected, group)
    if group == 'owned':
        return checks + owned(expected)
    return checks + rejected(expected, group == 'source-conflict')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group', choices=list(CASES), required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    before = cross.snapshot(None)
    out = Path(tempfile.mkdtemp(prefix='magic-property-float-string-', dir=ROOT/'.tools'))
    report = {'before': before, 'profile': cross.invoke.types.PROFILE, 'passed': False,
        'native_evaluations': 0, 'model_evaluations': 0, 'state_assertions_evaluated': 0,
        'runner_mode': 'SL', 'numeric_cap_seconds': 120, 'case': CASES[args.group], 'jobs': 1}
    print(out, flush=True)
    try:
        original = sources.CASES[CASES[args.group]]
        source = out/'source.php'; source.write_bytes(original)
        sources.prepare(out, source)
        eval_checks = integer.prepare_eval(out, 'weak-getter' if args.group in ('reference-kept', 'reference-format') else args.group)
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
