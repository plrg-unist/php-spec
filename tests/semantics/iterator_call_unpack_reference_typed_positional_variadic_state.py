#!/usr/bin/env python3
"""Reach typed property-reference tails before warnings, receives and body writes."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('iterator_call_unpack_reference_typed_positional_variadic_cases.json')
INPUTS = [Path(__file__), CATALOG, Path(review.__file__)]
SOURCES = {row['id'].removeprefix('iterator-call-unpack-reference-typed-positional-variadic-'): row['source']
           for row in json.loads(CATALOG.read_bytes())}
ADMISSION = ['$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
POST = ['$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))']
ZERO = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S']
ONE = ['S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
       'S_one = S_one_budget[.COMPLETION = NORMAL]']
CLASS_A = ('[(PTBRANCH ([(PTCLASS $ptascii("TypedRestA44"))])), '
           '(PTBRANCH ([PTBUILTIN "null"]))]')
CLASS_B = ('[(PTBRANCH ([(PTCLASS $ptascii("TypedRestB44"))])), '
           '(PTBRANCH ([PTBUILTIN "null"]))]')
ARRAY = '[(PTBRANCH ([PTBUILTIN "array"])), (PTBRANCH ([PTBUILTIN "null"]))]'
SECOND = [
    'n_data = piteratorunpack.OBJECT', 'n_cursor = piteratorunpack.ITERATOR',
    'piteratorunpack.CURRENT = REFERENCE n_raw',
    'piteratorunpack.INPUT = KNOWN (POBJECT n_data)',
    'piteratorunpack.CALL.SENT.NAMED = eps',
    'piteratorunpack.CALL.SENT.SLOTS = [NAMED_SENT (REFERENCE n_prior)]',
    'piteratorunpack.KEY = KNOWN (PINT 1)', '~piteratorunpack.NAMED',
    'S.STORE[n_prior] = DEFINED (PARRAY n_earlier)',
    'S.ARRAYS[n_earlier].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_child))]',
    '$object_name(S, n_child) = $ptascii("TypedRestA44")',
    'n_prior <- S.REFCELLS', 'n_prior =/= n_raw',
    'S.STORE[n_raw] = DEFINED (POBJECT n_current)',
    '$object_name(S, n_current) = $ptascii("TypedRestB44")',
    'n_raw <- S.REFCELLS',
    '$objectprops_record_at(S.OBJECTPROPS, n_data) = (pobjectprops)',
    '$property_slot_at(pobjectprops.SLOTS, $ptascii("earlier")) = (ppropertyslot_earlier)',
    'ppropertyslot_earlier.STATE = PROP_VALUE (ALIAS n_source)',
    'n_source =/= n_prior', 'n_source =/= n_raw',
    'S.STORE[n_source] = DEFINED (PARRAY n_earlier)',
    '$property_slot_at(pobjectprops.SLOTS, $ptascii("current")) = (ppropertyslot_current)',
    'ppropertyslot_current.STATE = PROP_VALUE (ALIAS n_raw)',
    '$node_children(S, HOBJECT n_data) = [HCELL n_source, HCELL n_raw]',
    '$node_children(S, HCELL n_prior) = [HARRAY n_earlier]',
    '$node_children(S, HARRAY n_earlier) = [HOBJECT n_child]',
    '$heap_owners($heap_graph(S), HCELL n_prior) = 1',
    '$heap_owners($heap_graph(S), HCELL n_raw) = 2',
    '$heap_owners($heap_graph(S), HARRAY n_earlier) = 2',
    '$heap_owners($heap_graph(S), HOBJECT n_child) = 1',
    '$heap_owners($heap_graph(S), HOBJECT n_data) = 2',
]

CASES = {
    'typed-initial-tail-captures-detached-owner-before-warning': {
        'source': SOURCES['class-entry-only-private-writes'],
        'stage': ('S.TODO = (ITERATOR_UNPACK piteratorunpack "send") :: ptask_tail* '
                  '-- if piteratorunpack.CALL.SENT = {SLOTS eps, NAMED eps}'),
        'checks': [
            'n_data = piteratorunpack.OBJECT', 'piteratorunpack.CURRENT = REFERENCE n_raw',
            'piteratorunpack.KEY = KNOWN (PINT 0)', '~piteratorunpack.NAMED',
            'piteratorunpack.HOLD = KNOWN PNULL', 'piteratorunpack.SNAPSHOT = eps',
            'S.STORE[n_raw] = DEFINED (POBJECT n_payload)', 'n_raw <- S.REFCELLS',
            '$object_name(S, n_payload) = $ptascii("TypedRestA44")',
            '$objectprops_record_at(S.OBJECTPROPS, n_data) = (pobjectprops)',
            '$property_slot_at(pobjectprops.SLOTS, $ptascii("earlier")) = (ppropertyslot)',
            'ppropertyslot.STATE = PROP_VALUE (ALIAS n_raw)',
            '$heap_owners($heap_graph(S), HCELL n_raw) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_payload) = 1',
            '$target_function(S, piteratorunpack.CALL.FUNCTION) = (pfunction)',
            'pfunction.SIGNATURE.PARAMETERS = [psparam]',
            '$call_fixed_parameters(pfunction.SIGNATURE.PARAMETERS) = eps',
            'psparam.VARIADIC', 'psparam.BYREF', 'psparam.TYPE = ' + CLASS_A,
            '$iterator_unpack_named_target(S, piteratorunpack) = NAMED_POSITION 0',
            '$iterator_unpack_reference_allowed(S, piteratorunpack)',
            '$iterator_unpack_warning_hold(S, piteratorunpack) = (KNOWN (POBJECT n_payload))',
            *ADMISSION,
            '~$iterator_unpack_reference_allowed(S, piteratorunpack[.NAMED = true])',
            'piteratorunpack_named = piteratorunpack[.KEY = KNOWN (PSTRING $ptascii("rest"))]',
            '~$iterator_unpack_reference_allowed(S, piteratorunpack_named)',
            'pfunction_reversed = pfunction[.SIGNATURE.PARAMETERS = [psparam[.TYPE = '
            '[(PTBRANCH ([PTBUILTIN "null"])), (PTBRANCH ([(PTCLASS $ptascii("TypedRestA44"))]))]]]]',
            '~$iterator_unpack_reference_allowed(S[.FUNCTIONS = [pfunction_reversed]], piteratorunpack)',
            'pfunction_nonnullable = pfunction[.SIGNATURE.PARAMETERS = [psparam[.TYPE = '
            '[(PTBRANCH ([(PTCLASS $ptascii("TypedRestA44"))]))]]]]',
            '~$iterator_unpack_reference_allowed(S[.FUNCTIONS = [pfunction_nonnullable]], piteratorunpack)',
            'pfunction_value = pfunction[.SIGNATURE.PARAMETERS = [psparam[.BYREF = false]]]',
            '~$iterator_unpack_reference_allowed(S[.FUNCTIONS = [pfunction_value]], piteratorunpack)',
            *ZERO, *ONE,
            'S_one.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
            'perrorcall.RESUME = ITERATOR_UNPACK piteratorunpack_held "byref"',
            'piteratorunpack_held = piteratorunpack[.HOLD = KNOWN (POBJECT n_payload)]'
            '[.SNAPSHOT = (POBJECT n_payload)]',
            'perrorcall.LEVEL = 2', 'perrorcall.LINE = 26',
            'perrorcall.MESSAGE = $ptascii("Cannot pass by-reference argument 1 of '
            'typedRestTarget44() by unpacking a Traversable, passing by-value instead")',
            '$error_call_valid(S_one, perrorcall)',
            '$heap_owners($heap_graph(S_one), HOBJECT n_payload) = 2',
            'S_one.STORE = S.STORE', 'S_one.EVENTS = S.EVENTS', *POST,
        ],
    },
    'typed-array-rest-body-overwrites-preserve-source-alias': {
        'source': SOURCES['array-entry-cow-and-private-overwrites'],
        'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.NAME = $ptascii("typedRestTarget44") '
                  '-- if S.TODO = (EMIT z_emit) :: ptask_tail* -- if S.RESULT = KNOWN pvalue_text '
                  '-- if $string_bytes(pvalue_text) = ($ptascii("R|"))'),
        'checks': [
            'pcallcontext.ARGC = 2', 'pcallcontext.HOLES = eps',
            'pcallcontext.NAMED = eps', 'pcallcontext.LINE = 26',
            'pcallcontext.EXTRA = [REFERENCE n_left, REFERENCE n_right]',
            '$receiving_function(S, pcallcontext.FUNCTION) = (pfunction)',
            'pfunction.SIGNATURE.PARAMETERS = [psparam]',
            'psparam.BYREF', 'psparam.VARIADIC', 'psparam.TYPE = ' + ARRAY,
            '$lookup(S.ENV, $ptascii("rest")) = (n_rest_cell)',
            'S.STORE[n_rest_cell] = DEFINED (PARRAY n_rest)',
            'S.ARRAYS[n_rest].ITEMS = [ENTRY (KINT 0) (ALIAS n_left), ENTRY (KINT 1) (ALIAS n_right)]',
            'S.ARRAYS[n_rest].NEXT = 2',
            'n_left =/= n_right', 'n_left <- S.REFCELLS', 'n_right <- S.REFCELLS',
            'S.STORE[n_left] = DEFINED (PINT 17)', 'S.STORE[n_right] = DEFINED (PINT 23)',
            '~$typed_reference_cell_source(S, n_left)', '~$typed_reference_cell_source(S, n_right)',
            '$parameter_backing_at(S.PARAMETERBACKINGS, n_left) = eps',
            '$parameter_backing_at(S.PARAMETERBACKINGS, n_right) = eps',
            '$variadic_conversion(S, psparam, REFERENCE n_left) = TYPEREJECT',
            '$variadic_conversion(S, psparam, REFERENCE n_right) = TYPEREJECT',
            'S_global = $global_table_view(S)',
            '$lookup(S_global.ENV, $ptascii("alias")) = (n_raw)',
            'n_raw =/= n_left', 'n_raw =/= n_right', 'n_raw <- S.REFCELLS',
            'S.STORE[n_raw] = DEFINED (PARRAY n_source)',
            'S.ARRAYS[n_source].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_child))]',
            '$object_name(S, n_child) = $ptascii("TypedRestB44")',
            '$node_children(S, HARRAY n_rest) = [HCELL n_left, HCELL n_right]',
            '$node_children(S, HCELL n_left) = eps', '$node_children(S, HCELL n_right) = eps',
            '$heap_owners($heap_graph(S), HCELL n_left) = 2',
            '$heap_owners($heap_graph(S), HCELL n_right) = 2',
            '$heap_owners($heap_graph(S), HCELL n_raw) = 1',
            '$heap_owners($heap_graph(S), HARRAY n_rest) = 1',
            '$heap_owners($heap_graph(S), HARRAY n_source) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_child) = 1',
            'S.DESTRUCTION.CALLED = [n_data, n_earlier]',
            '$object_name(S, n_data) = $ptascii("TypedRestIterator44")',
            '$object_name(S, n_earlier) = $ptascii("TypedRestA44")',
            '$heap_owners($heap_graph(S), HOBJECT n_data) = 0',
            '$heap_owners($heap_graph(S), HOBJECT n_earlier) = 0',
            *ADMISSION, *ZERO, *ONE,
            'S_one.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("R|")]',
            'S_one.STORE = S.STORE', 'S_one.ARRAYS = S.ARRAYS', *POST,
            'S_two_budget = $drive_steps(S_one, 1)', '$drive(S, 2) = S_two_budget',
        ],
    },
    'partial-array-rest-rejection-captures-dereferenced-trace': {
        'source': SOURCES['array-partial-receive-trace'],
        'stage': ('S.TODO = [VARIADIC_RECEIVE porigin 1] -- if S.CURRENT = (pcallcontext) '
                  '-- if pcallcontext.NAME = $ptascii("typedRestTarget44")'),
        'checks': [
            'pcallcontext.FUNCTION = porigin', 'pcallcontext.ARGC = 2',
            'pcallcontext.HOLES = eps', 'pcallcontext.NAMED = eps',
            'pcallcontext.LINE = 26', 'pcallcontext.CALLSITE = (porigin_call)',
            'pcallcontext.EXTRA = [REFERENCE n_left, REFERENCE n_right]',
            '$receiving_function(S, porigin) = (pfunction)',
            'pfunction.SIGNATURE.PARAMETERS = [psparam]',
            'psparam.BYREF', 'psparam.VARIADIC', 'psparam.TYPE = ' + ARRAY,
            '$default_parameter_line(S, porigin, 0) = 16',
            '$lookup(S.ENV, $ptascii("rest")) = (n_rest_cell)',
            'S.STORE[n_rest_cell] = DEFINED (PARRAY n_rest)',
            'S.ARRAYS[n_rest].ITEMS = [ENTRY (KINT 0) (ALIAS n_left)]',
            'S.ARRAYS[n_rest].NEXT = 1',
            'n_left =/= n_right', 'n_left <- S.REFCELLS', 'n_right <- S.REFCELLS',
            'S.STORE[n_left] = DEFINED (PARRAY n_earlier)',
            'S.ARRAYS[n_earlier].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_child))]',
            '$object_name(S, n_child) = $ptascii("TypedRestA44")',
            'S.STORE[n_right] = DEFINED (POBJECT n_current)',
            '$object_name(S, n_current) = $ptascii("TypedRestB44")',
            '~$typed_reference_cell_source(S, n_left)', '~$typed_reference_cell_source(S, n_right)',
            '$variadic_conversion(S, psparam, REFERENCE n_left) = TYPEVALUE (PARRAY n_earlier)',
            '$variadic_conversion(S, psparam, REFERENCE n_right) = TYPEREJECT',
            '~$variadic_string_candidate(S)', '~$api_variadic_candidate(S)',
            '$node_children(S, HARRAY n_rest) = [HCELL n_left]',
            '$heap_owners($heap_graph(S), HCELL n_left) = 2',
            '$heap_owners($heap_graph(S), HCELL n_right) = 1',
            '$heap_owners($heap_graph(S), HARRAY n_earlier) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_child) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_current) = 1',
            'S.DESTRUCTION.CALLED = [n_data]',
            '$object_name(S, n_data) = $ptascii("TypedRestIterator44")',
            '$heap_owners($heap_graph(S), HOBJECT n_data) = 0',
            '$call_task_valid(S, VARIADIC_RECEIVE porigin 1)', *ADMISSION, *ZERO, *ONE,
            'S_one.TODO = (THROW_SEARCH n_error) :: ptask_after*',
            'S_one.OBJECTS[n_error] = THROWABLE pthrowable', 'pthrowable.KIND = "TypeError"',
            '$throwable_field(S_one, n_error, "line") = PINT 16',
            '$throwable_field(S_one, n_error, "code") = PINT 0',
            '$string_bytes($throwable_field(S_one, n_error, "message")) = '
            '($ptascii("typedRestTarget44(): Argument #2 must be of type ?array, TypedRestB44 given, called in ") '
            '++ $call_sourcefile(S.FILES, porigin_call) ++ $ptascii(" on line 26"))',
            '$throwable_field(S_one, n_error, "trace") = PARRAY n_trace',
            '$entry_lookup(S_one.ARRAYS[n_trace].ITEMS, KINT 0) = (DIRECT (PARRAY n_frame))',
            '$entry_lookup(S_one.ARRAYS[n_frame].ITEMS, KSTRING $ptascii("function")) = '
            '(DIRECT (PSTRING $ptascii("typedRestTarget44")))',
            '$entry_lookup(S_one.ARRAYS[n_frame].ITEMS, KSTRING $ptascii("line")) = (DIRECT (PINT 26))',
            '$entry_lookup(S_one.ARRAYS[n_frame].ITEMS, KSTRING $ptascii("args")) = (DIRECT (PARRAY n_args))',
            'S_one.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_earlier)), '
            'ENTRY (KINT 1) (DIRECT (POBJECT n_current))]',
            '$node_children(S_one, HARRAY n_args) = [HARRAY n_earlier, HOBJECT n_current]',
            '$trace_graph_valid(S_one, n_trace)',
            'S_one.ARRAYS[n_rest] = S.ARRAYS[n_rest]',
            '$heap_owners($heap_graph(S_one), HCELL n_left) = 2',
            '$heap_owners($heap_graph(S_one), HCELL n_right) = 1',
            '$heap_owners($heap_graph(S_one), HARRAY n_earlier) = 2',
            '$heap_owners($heap_graph(S_one), HOBJECT n_child) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_current) = 2',
            'S_one.STORE = S.STORE', 'S_one.CURRENT = S.CURRENT',
            'S_one.EVENTS = S.EVENTS', *POST,
            'S_two_budget = $drive_steps(S_one, 1)', '$drive(S, 2) = S_two_budget',
        ],
    },
    'second-typed-tail-warning-precedes-first-wrong-type-receive': {
        'source': SOURCES['second-warning-throw-precedes-first-receive-rejection'],
        'stage': ('S.TODO = (ITERATOR_UNPACK piteratorunpack "send") :: ptask_tail* '
                  '-- if piteratorunpack.CALL.SENT.SLOTS = [NAMED_SENT (REFERENCE n_prior)]'),
        'checks': [
            *SECOND, 'piteratorunpack.HOLD = KNOWN PNULL', 'piteratorunpack.SNAPSHOT = eps',
            '$heap_owners($heap_graph(S), HOBJECT n_current) = 1',
            '$target_function(S, piteratorunpack.CALL.FUNCTION) = (pfunction)',
            'pfunction.SIGNATURE.PARAMETERS = [psparam]',
            'psparam.BYREF', 'psparam.VARIADIC', 'psparam.TYPE = ' + CLASS_B,
            '$typed_conversion_at(S, psparam.TYPE, PARRAY n_earlier, false) = TYPEREJECT',
            '$typed_conversion_at(S, psparam.TYPE, POBJECT n_current, false) = TYPEVALUE (POBJECT n_current)',
            '$iterator_unpack_reference_allowed(S, piteratorunpack)',
            '$iterator_unpack_warning_hold(S, piteratorunpack) = (KNOWN (POBJECT n_current))',
            *ADMISSION, *ZERO, *ONE,
            'S_one.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
            'perrorcall.RESUME = ITERATOR_UNPACK piteratorunpack_held "byref"',
            'piteratorunpack_held = piteratorunpack[.HOLD = KNOWN (POBJECT n_current)]'
            '[.SNAPSHOT = (POBJECT n_current)]',
            'perrorcall.LEVEL = 2', 'perrorcall.LINE = 26',
            'perrorcall.MESSAGE = $ptascii("Cannot pass by-reference argument 2 of '
            'typedRestTarget44() by unpacking a Traversable, passing by-value instead")',
            '$error_call_valid(S_one, perrorcall)',
            '$heap_owners($heap_graph(S_one), HOBJECT n_current) = 2',
            '$heap_owners($heap_graph(S_one), HARRAY n_earlier) = 2',
            '$heap_owners($heap_graph(S_one), HOBJECT n_child) = 1',
            'S_one.STORE = S.STORE', 'S_one.EVENTS = S.EVENTS', *POST,
        ],
    },
    'parked-typed-tail-injection-precedes-first-wrong-type-receive': {
        'source': SOURCES['parked-second-warning-precedes-first-receive-rejection'],
        'stage': ('S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_main* '
                  '-- if pconfigcall.KIND = INTRINSIC_FIBER_THROW '
                  '-- if pconfigcall.OWNER = (n_fiber) '
                  '-- if $fiber_at(S, n_fiber) = (pfiber) -- if pfiber.VM = (pfibervm) '
                  '-- if pfibervm.FRAMES = [pframe_unpack, pframe_base] '
                  '-- if pframe_unpack.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_unpack* '
                  '-- if perrorcall.RESUME = ITERATOR_UNPACK piteratorunpack "byref" '
                  '-- if piteratorunpack.CALL.SENT.SLOTS = [NAMED_SENT (REFERENCE n_prior)]'),
        'checks': [
            *SECOND,
            'piteratorunpack.HOLD = KNOWN (POBJECT n_current)',
            'piteratorunpack.SNAPSHOT = (POBJECT n_current)',
            '$iterator_unpack_hold_valid(piteratorunpack, "byref")',
            '$heap_owners($heap_graph(S), HOBJECT n_current) = 2',
            '$lookup(S.ENV, $ptascii("marker")) = (n_marker)',
            'S.STORE[n_marker] = DEFINED (PINT 17)',
            'pconfigcall.SENT = [NAMED_SENT (KNOWN (POBJECT n_error))]',
            '$throwable_live(S, n_error)', '$throwable_field(S, n_error, "code") = PINT 51',
            'S.ACTIVEFIBER = eps', 'S.FIBERCALLERS = eps',
            'pfiber.STATUS = FIBER_SUSPENDED',
            'S_view = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)]'
            '[.FIBERCALLERS = eps][.COMPLETION = NORMAL]',
            'S_scope = $constant_frame_scope(S_view, pframe_unpack, [pframe_base])',
            '$target_function(S_scope, piteratorunpack.CALL.FUNCTION) = (pfunction)',
            'pfunction.SIGNATURE.PARAMETERS = [psparam]',
            'psparam.BYREF', 'psparam.VARIADIC', 'psparam.TYPE = ' + CLASS_B,
            '$typed_conversion_at(S_scope, psparam.TYPE, PARRAY n_earlier, false) = TYPEREJECT',
            '$typed_conversion_at(S_scope, psparam.TYPE, POBJECT n_current, false) = TYPEVALUE (POBJECT n_current)',
            '$iterator_unpack_reference_allowed(S_scope, piteratorunpack)',
            '$iterator_unpack_result_valid(S_scope, piteratorunpack, "byref")',
            '$iterator_unpack_hold_live(S_scope, piteratorunpack, "byref")',
            '$error_entered_call_valid(S_scope, perrorcall)',
            '$useriter_frames_ids(pfibervm.FRAMES) = [n_cursor]',
            '$fiber_vm_valid(S, pfibervm, (n_fiber), eps)', 'perrorcall.LINE = 28',
            *ADMISSION, *ZERO,
            'piteratorunpack_missing = piteratorunpack[.HOLD = KNOWN PNULL][.SNAPSHOT = eps]',
            'perrorcall_bad = perrorcall[.RESUME = ITERATOR_UNPACK piteratorunpack_missing "byref"]',
            'pframe_bad = pframe_unpack[.TODO = (ERROR_HANDLER_RESULT perrorcall_bad) :: ptask_unpack*]',
            'pfibervm_bad = pfibervm[.FRAMES = [pframe_bad, pframe_base]]',
            'S_bad = $fiber_put(S, n_fiber, pfiber[.VM = (pfibervm_bad)])',
            '~$fiber_vm_valid(S_bad, pfibervm_bad, (n_fiber), eps)',
            '~$call_descriptors_valid(S_bad)', *ONE,
            'S_one.ACTIVEFIBER = (n_fiber)',
            '$fiber_at(S_one, n_fiber) = (pfiber_running)',
            'pfiber_running.STATUS = FIBER_RUNNING', 'pfiber_running.VM = eps',
            'S_one.FIBERCALLERS = [pfibercaller]', 'pfibercaller.PREVIOUS = eps',
            'pfibercaller.API.KIND = (INTRINSIC_FIBER_THROW)',
            'S_one.TODO = (THROW_SEARCH n_error) :: ptask_throw*',
            'S_one.STORE = S.STORE', 'S_one.ARRAYS = S.ARRAYS',
            'S_one.STORE[n_marker] = DEFINED (PINT 17)', 'S_one.EVENTS = S.EVENTS',
            '$heap_owners($heap_graph(S_one), HCELL n_prior) = 1',
            '$heap_owners($heap_graph(S_one), HARRAY n_earlier) = 2',
            '$heap_owners($heap_graph(S_one), HOBJECT n_child) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_current) = 2', *POST,
            'S_two_budget = $drive_steps(S_one, 1)', '$drive(S, 2) = S_two_budget',
        ],
    },
}


def run(selected):
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=review.ROOT, text=True).strip()
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    before = {str(path): digest(path) for path in INPUTS}
    review.CASES = CASES
    original = review.recorded
    raw = None
    process_caps = {}

    def recorded(command, directory, stem, environment, cap):
        nonlocal raw
        raw = directory.parent
        if directory.name == 'parked-typed-tail-injection-precedes-first-wrong-type-receive':
            cap = 180
        process_caps[directory.name] = cap
        return original(command, directory, stem, environment, cap)

    review.recorded = recorded
    try:
        passed = review.run(selected)
    finally:
        review.recorded = original
    stable = before == {str(path): digest(path) for path in INPUTS}
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'],
                                                     cwd=review.ROOT, text=True).strip()
    path = raw / 'report.json'
    report = json.loads(path.read_bytes())
    report['budgets']['process_seconds'] = max(process_caps.values())
    report.update(author_inputs=before, author_inputs_stable=stable,
                  case_process_seconds=process_caps, head_stable=head_stable,
                  passed=passed and stable and head_stable)
    path.write_text(json.dumps(report, indent=2) + '\n')
    return passed and stable and head_stable


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    raise SystemExit(0 if run(parser.parse_args().case) else 1)
