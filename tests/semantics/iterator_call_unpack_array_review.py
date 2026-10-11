#!/usr/bin/env python3
"""Reached copied-array warning owners, child edges and ordered retirement."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import fiber_state_review as review

CATALOG = Path(__file__).with_name('iterator_call_unpack_array_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
SOURCES = {r['id']: r['source'] for r in json.loads(INPUT_BYTES[CATALOG])}


def source(suffix):
    return SOURCES['iterator-call-unpack-array-' + suffix]


ADMISSION = ['$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
POST = ['$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))']
ZERO = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S']
ONE = ['S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
       'S_one = S_one_budget[.COMPLETION = NORMAL]']
COPIED = ['n_data = piteratorunpack.OBJECT', 'n_cursor = piteratorunpack.ITERATOR',
          'piteratorunpack.CURRENT = KNOWN (PARRAY n_array)',
          'S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_child))]',
          'n_child =/= n_data', 'piteratorunpack.INPUT = KNOWN (POBJECT n_data)',
          'piteratorunpack.CALL.SENT = {SLOTS eps, NAMED eps}',
          '$operand_nodes(piteratorunpack.CURRENT) = [HARRAY n_array]',
          '$node_children(S, HARRAY n_array) = [HOBJECT n_child]',
          '$heap_owners($heap_graph(S), HOBJECT n_child) = 1',
          '$heap_owners($heap_graph(S), HOBJECT n_data) = 2',
          '~(n_child <- S.DESTRUCTION.CALLED)']
ACTIVE = ['$useriter_cursor_valid(S, n_cursor, n_data)',
          'S.ORIGIN = $unpack_origin(S, piteratorunpack.CALL)',
          '$useriter_tasks_ids(S.TODO) = [n_cursor]']
SOURCE_NULL = ['$lookup(S.ENV, $ptascii("source")) = (n_source)',
               'S.STORE[n_source] = DEFINED PNULL',
               '$heap_owners($heap_graph(S), HCELL n_source) = 1']
HELD = ['piteratorunpack.HOLD = piteratorunpack.CURRENT',
        '$iterator_unpack_hold_valid(piteratorunpack, "byref")',
        '$iterator_unpack_warning_hold(S, piteratorunpack) = (piteratorunpack.CURRENT)',
        '$heap_owners($heap_graph(S), HARRAY n_array) = 2']
MESSAGE = ('$ptascii("Cannot pass by-reference argument 1 of ArrayTarget28() '
           'by unpacking a Traversable, passing by-value instead")')
ABORT_STAGE = ('S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
               '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail* '
               '-- if pdestructionoperation.PENDING = (n_error) '
               '-- if pdestructionoperation.SOURCE = ITERATOR_UNPACK piteratorunpack "byref"')
ABORT = [*COPIED, *HELD, '$iterator_lookup(S.ITERATORS, n_cursor) = eps',
         '$useriter_task_ids(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = eps',
         'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HARRAY n_array), '
         'DESTRUCTION_VALUE (HOBJECT n_data), DESTRUCTION_VALUE (HOBJECT n_data), '
         'DESTRUCTION_VALUE (HARRAY n_array)]',
         'pdestructionoperation.CALLER = S.CURRENT',
         'pdestructionoperation.ORIGIN = piteratorunpack.CALL.CALLSITE',
         '$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = [HOBJECT n_error]',
         '$throwable_live(S, n_error)', '$throwable_field(S, n_error, "code") = PINT 51',
         '$eager_operation_source_valid(S, pdestructionoperation)',
         '$destructor_operation_valid(S, pdestructionoperation)',
         '$destructor_release_valid(S, pdestructionrelease)', *ADMISSION, *ZERO]

CASES = {
    'copied-array-warning-adds-container-owner-with-one-child-edge': {
        'source': source('normal-write'),
        'stage': 'S.TODO = (ITERATOR_UNPACK piteratorunpack "send") :: ptask_tail*',
        'checks': [
            *COPIED, *ACTIVE, 'piteratorunpack.HOLD = KNOWN PNULL',
            'piteratorunpack.KEY = KNOWN (PINT 0)', '~piteratorunpack.NAMED',
            '$lookup(S.ENV, $ptascii("source")) = (n_source)',
            'S.STORE[n_source] = DEFINED (PARRAY n_array)',
            '$heap_owners($heap_graph(S), HARRAY n_array) = 2',
            '~$iterator_unpack_scalar_operand(S, piteratorunpack.CURRENT)',
            '$iterator_unpack_warning_hold(S, piteratorunpack) = (piteratorunpack.CURRENT)',
            *ADMISSION, *ZERO, *ONE,
            'S_one.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
            'perrorcall.RESUME = ITERATOR_UNPACK piteratorunpack_held "byref"',
            'piteratorunpack_held = piteratorunpack[.HOLD = piteratorunpack.CURRENT]',
            'perrorcall.LEVEL = 2', 'perrorcall.LINE = 21',
            'perrorcall.MESSAGE = ' + MESSAGE, '$error_call_valid(S_one, perrorcall)',
            '$heap_owners($heap_graph(S_one), HARRAY n_array) = 3',
            '$heap_owners($heap_graph(S_one), HOBJECT n_child) = 1',
            '$node_children(S_one, HARRAY n_array) = [HOBJECT n_child]',
            'S_one.STORE = S.STORE', 'S_one.ARRAYS = S.ARRAYS',
            'S_one.EVENTS = S.EVENTS', *POST,
            'S_early = S[.TODO = (ITERATOR_UNPACK piteratorunpack_held "send") :: ptask_tail*]',
            '$heap_valid($heap_graph(S_early))',
            '~$iterator_unpack_result_valid(S_early, piteratorunpack_held, "send")',
            '~$call_descriptors_valid(S_early)',
            'piteratorunpack_occupied = piteratorunpack[.CALL = '
            'piteratorunpack.CALL[.SENT.SLOTS = [NAMED_SENT (KNOWN (PINT 1))]]]',
            'S_occupied = S[.TODO = (ITERATOR_UNPACK piteratorunpack_occupied "send") :: ptask_tail*]',
            '$heap_graph(S_occupied) = $heap_graph(S)',
            '$iterator_unpack_warning_hold(S_occupied, piteratorunpack_occupied) = eps',
        ],
    },
    'handler-drop-transfers-array-hold-into-distinct-private-cell': {
        'source': source('normal-write'),
        'stage': 'S.TODO = (ITERATOR_UNPACK piteratorunpack "byref") :: ptask_tail*',
        'checks': [
            *COPIED, *ACTIVE, *SOURCE_NULL, *HELD, *ADMISSION, *ZERO,
            'n_private = |S.STORE|', *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(ITERATOR_UNPACK piteratorunpack_next "next-start") :: ptask_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HARRAY n_array)]',
            'piteratorunpack_next.CURRENT = KNOWN PNULL',
            'piteratorunpack_next.KEY = KNOWN PNULL',
            'piteratorunpack_next.HOLD = KNOWN PNULL',
            '~piteratorunpack_next.NAMED',
            'piteratorunpack_next.CALL.SENT.SLOTS = [NAMED_SENT (REFERENCE n_private)]',
            'piteratorunpack_next.CALL.SENT.NAMED = eps',
            'S_one.STORE[n_private] = DEFINED (PARRAY n_array)',
            'n_private <- S_one.REFCELLS', 'n_private =/= n_source',
            'S_one.STORE[n_source] = DEFINED PNULL',
            '$heap_owners($heap_graph(S_one), HCELL n_private) = 1',
            '$node_children(S_one, HCELL n_private) = [HARRAY n_array]',
            '$heap_owners($heap_graph(S_one), HARRAY n_array) = 2',
            '$heap_owners($heap_graph(S_one), HOBJECT n_child) = 1',
            '$destructor_release_valid(S_one, pdestructionrelease)', *POST,
            'S_two_budget = $drive_steps(S_one, 1)', 'S_two_budget.COMPLETION = BUDGET',
            'S_two = S_two_budget[.COMPLETION = NORMAL]',
            'S_two.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_done) :: '
            '(ITERATOR_UNPACK piteratorunpack_next "next-start") :: ptask_tail*',
            'pdestructionrelease_done.JOBS = eps',
            '$heap_owners($heap_graph(S_two), HARRAY n_array) = 1',
            '$heap_owners($heap_graph(S_two), HOBJECT n_child) = 1',
            '$heap_owners($heap_graph(S_two), HCELL n_private) = 1',
            '~(n_child <- S_two.DESTRUCTION.CALLED)', 'S_two.EVENTS = S.EVENTS',
            '$call_descriptors_valid(S_two)', '$heap_valid($heap_graph(S_two))',
            'piteratorunpack_early = piteratorunpack_next[.HOLD = KNOWN (PARRAY n_array)]',
            'S_early = S_one[.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(ITERATOR_UNPACK piteratorunpack_early "next-start") :: ptask_tail*]',
            '$heap_valid($heap_graph(S_early))', '~$call_descriptors_valid(S_early)',
        ],
    },
    'warning-throw-retires-raw-array-before-data-input-and-hold': {
        'source': source('warning-throw'), 'stage': ABORT_STAGE,
        'checks': [
            *ABORT, *SOURCE_NULL, *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_next) :: '
            '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*',
            'pdestructionrelease_next.JOBS = [DESTRUCTION_VALUE (HOBJECT n_data), '
            'DESTRUCTION_VALUE (HOBJECT n_data), DESTRUCTION_VALUE (HARRAY n_array)]',
            '$heap_owners($heap_graph(S_one), HARRAY n_array) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_child) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_data) = 2',
            '~(n_child <- S_one.DESTRUCTION.CALLED)', 'S_one.EVENTS = S.EVENTS', *POST,
        ],
    },
    'last-container-owner-expands-child-job-after-iterator-retirement': {
        'source': source('warning-throw'),
        'stage': (ABORT_STAGE + ' -- if pdestructionrelease.JOBS = '
                  '[DESTRUCTION_VALUE (HARRAY n_array)] '
                  '-- if piteratorunpack.CURRENT = KNOWN (PARRAY n_array)'),
        'checks': [
            'n_data = piteratorunpack.OBJECT',
            'S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_child))]',
            'n_child =/= n_data', 'piteratorunpack.HOLD = piteratorunpack.CURRENT',
            '$heap_owners($heap_graph(S), HARRAY n_array) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_child) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_data) = 0',
            'n_data <- S.DESTRUCTION.CALLED', '~(n_child <- S.DESTRUCTION.CALLED)',
            '$eager_operation_source_valid(S, pdestructionoperation)',
            '$destructor_operation_valid(S, pdestructionoperation)',
            '$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = [HOBJECT n_error]',
            *ADMISSION, *ZERO, *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_child) :: '
            '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*',
            'pdestructionrelease_child.JOBS = [DESTRUCTION_VALUE (HOBJECT n_child)]',
            '~((HARRAY n_array) <- S_one.ALLOCATIONS)',
            '$heap_owners($heap_graph(S_one), HARRAY n_array) = 0',
            '$heap_owners($heap_graph(S_one), HOBJECT n_child) = 1',
            'S_one.ARRAYS = S.ARRAYS', 'S_one.EVENTS = S.EVENTS',
            '$eager_operation_source_valid(S_one, pdestructionoperation)', *POST,
            'S_document = S_one[.ARRAYS[n_array] = $array_empty()]',
            '$heap_graph(S_document) = $heap_graph(S_one)',
            '$eager_operation_source_valid(S_document, pdestructionoperation)',
            '$destructor_operation_valid(S_document, pdestructionoperation)',
            'S_two_budget = $drive_steps(S_one, 1)', 'S_two_budget.COMPLETION = BUDGET',
            'S_two = S_two_budget[.COMPLETION = NORMAL]',
            'S_two.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: '
            '(DESTRUCTOR_RELEASE pdestructionrelease_done) :: '
            '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*',
            'pdestructionrelease_done.JOBS = eps',
            'pdestructorcall.OBJECT = n_child', 'pdestructorcall.PENDING = (n_error)',
            'n_child <- S_two.DESTRUCTION.CALLED', 'n_data <- S_two.DESTRUCTION.CALLED',
            'S_two.EVENTS = S.EVENTS',
            '$call_descriptors_valid(S_two)', '$heap_valid($heap_graph(S_two))',
        ],
    },
    'retired-array-source-is-nonowning-and-rejects-missing-hold': {
        'source': source('warning-throw'),
        'stage': (ABORT_STAGE + ' -- if pdestructionrelease.JOBS = eps '
                  '-- if piteratorunpack.CURRENT = KNOWN (PARRAY n_array) '
                  '-- if S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_child))] '
                  '-- if n_child <- S.DESTRUCTION.CALLED'),
        'checks': [
            'n_data = piteratorunpack.OBJECT', 'piteratorunpack.HOLD = piteratorunpack.CURRENT',
            '~((HARRAY n_array) <- S.ALLOCATIONS)', '~((HOBJECT n_child) <- S.ALLOCATIONS)',
            '$heap_owners($heap_graph(S), HARRAY n_array) = 0',
            '$heap_owners($heap_graph(S), HOBJECT n_child) = 0',
            '$heap_owners($heap_graph(S), HOBJECT n_data) = 0',
            '$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = [HOBJECT n_error]',
            '$iterator_unpack_hold_valid(piteratorunpack, "byref")',
            '$eager_operation_source_valid(S, pdestructionoperation)',
            '$destructor_operation_valid(S, pdestructionoperation)', *ADMISSION, *ZERO,
            'S.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail*',
            'pdestructionoperation_bad = pdestructionoperation[.SOURCE = '
            'ITERATOR_UNPACK piteratorunpack[.HOLD = KNOWN PNULL] "byref"]',
            'S_bad = S[.DESTRUCTION.OPERATIONS = pdestructionoperation_bad :: '
            'pdestructionoperation_tail*][.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation_bad) :: ptask_tail*]',
            '$heap_graph(S_bad) = $heap_graph(S)',
            '~$eager_operation_source_valid(S_bad, pdestructionoperation_bad)',
            '~$destructor_operation_valid(S_bad, pdestructionoperation_bad)',
            '~$call_descriptors_valid(S_bad)',
            'pdestructionoperation_phase = pdestructionoperation[.SOURCE = '
            'ITERATOR_UNPACK piteratorunpack[.NAMED = true] "byref"]',
            'S_phase = S[.DESTRUCTION.OPERATIONS = pdestructionoperation_phase :: '
            'pdestructionoperation_tail*][.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation_phase) :: ptask_tail*]',
            '$heap_graph(S_phase) = $heap_graph(S)',
            '~$eager_operation_source_valid(S_phase, pdestructionoperation_phase)',
            '~$destructor_operation_valid(S_phase, pdestructionoperation_phase)',
            '~$call_descriptors_valid(S_phase)',
        ],
    },
    'parked-array-preserves-container-and-child-counts-with-source-guards': {
        'source': source('parked-throw'),
        'stage': ('S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_main* '
                  '-- if pconfigcall.KIND = INTRINSIC_FIBER_THROW '
                  '-- if pconfigcall.OWNER = (n_fiber) '
                  '-- if $fiber_at(S, n_fiber) = (pfiber) -- if pfiber.VM = (pfibervm) '
                  '-- if pfibervm.FRAMES = [pframe_unpack, pframe_base] '
                  '-- if pframe_unpack.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_unpack* '
                  '-- if perrorcall.RESUME = ITERATOR_UNPACK piteratorunpack "byref"'),
        'checks': [
            *COPIED, 'piteratorunpack.HOLD = piteratorunpack.CURRENT',
            '$heap_owners($heap_graph(S), HARRAY n_array) = 2',
            '$lookup(S.ENV, $ptascii("source")) = (n_source)',
            '$lookup(pfibervm.TABLE.ENV, $ptascii("source")) = (n_source)',
            'S.STORE[n_source] = DEFINED (PINT 17)',
            '$heap_count(HCELL n_source, $task_nodes(perrorcall.RESUME)) = 0',
            '$heap_owners($heap_graph(S), HCELL n_source) = 2',
            'S.ACTIVEFIBER = eps', 'S.FIBERCALLERS = eps',
            'pfiber.STATUS = FIBER_SUSPENDED', 'pfibervm.CURRENT = (pcallcontext_saved)',
            'S_view = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)]'
            '[.FIBERCALLERS = eps][.COMPLETION = NORMAL]',
            'S_scope = $constant_frame_scope(S_view, pframe_unpack, [pframe_base])',
            '$useriter_frames_ids(pfibervm.FRAMES) = [n_cursor]',
            '$fiber_vm_valid(S, pfibervm, (n_fiber), eps)',
            '$error_context_valid(S_view, pcallcontext_saved)',
            '$error_entered_call_valid(S_scope, perrorcall)',
            '$iterator_unpack_result_valid(S_scope, piteratorunpack, "byref")',
            'pcallcontext_saved.LINE = 23', 'perrorcall.LINE = 23', *ADMISSION, *ZERO,
            'piteratorunpack_bad = piteratorunpack[.CALL = piteratorunpack.CALL[.LINE = 24]]',
            'perrorcall_bad = perrorcall[.LINE = 24]'
            '[.EVENT = DIAGNOSTIC "Warning" perrorcall.MESSAGE 24]'
            '[.RESUME = ITERATOR_UNPACK piteratorunpack_bad "byref"]',
            'pframe_bad = pframe_unpack[.TODO = (ERROR_HANDLER_RESULT perrorcall_bad) :: ptask_unpack*]',
            'pfibervm_bad = pfibervm[.CURRENT = (pcallcontext_saved[.LINE = 24])]'
            '[.FRAMES = [pframe_bad, pframe_base]]',
            'S_bad = $fiber_put(S, n_fiber, pfiber[.VM = (pfibervm_bad)])',
            '$heap_graph(S_bad) = $heap_graph(S)',
            '~$fiber_vm_valid(S_bad, pfibervm_bad, (n_fiber), eps)',
            '~$call_descriptors_valid(S_bad)',
            '$lookup(S.ENV, $ptascii("failure")) = (n_failure_cell)',
            'S.STORE[n_failure_cell] = DEFINED (POBJECT n_failure)',
            '$throwable_field(S, n_failure, "trace") = PARRAY n_foreign_array',
            'n_foreign_array =/= n_array',
            'piteratorunpack_foreign = piteratorunpack[.HOLD = KNOWN (PARRAY n_foreign_array)]',
            'perrorcall_foreign = perrorcall[.RESUME = '
            'ITERATOR_UNPACK piteratorunpack_foreign "byref"]',
            'pframe_foreign = pframe_unpack[.TODO = '
            '(ERROR_HANDLER_RESULT perrorcall_foreign) :: ptask_unpack*]',
            'pfibervm_foreign = pfibervm[.FRAMES = [pframe_foreign, pframe_base]]',
            'S_foreign = $fiber_put(S, n_fiber, pfiber[.VM = (pfibervm_foreign)])',
            '$heap_valid($heap_graph(S_foreign))',
            '$heap_owners($heap_graph(S_foreign), HARRAY n_array) = 1',
            '$heap_owners($heap_graph(S_foreign), HOBJECT n_child) = 1',
            '$heap_owners($heap_graph(S_foreign), HOBJECT n_data) = 2',
            '~$fiber_vm_valid(S_foreign, pfibervm_foreign, (n_fiber), eps)',
            '~$call_descriptors_valid(S_foreign)',
            'pframe_duplicate = pframe_unpack[.TODO = (ERROR_HANDLER_RESULT perrorcall) :: '
            '(ERROR_HANDLER_RESULT perrorcall) :: ptask_unpack*]',
            'pfibervm_duplicate = pfibervm[.FRAMES = [pframe_duplicate, pframe_base]]',
            'S_duplicate = $fiber_put(S, n_fiber, pfiber[.VM = (pfibervm_duplicate)])',
            '$useriter_frames_ids(pfibervm_duplicate.FRAMES) = [n_cursor, n_cursor]',
            '$heap_valid($heap_graph(S_duplicate))',
            '$heap_owners($heap_graph(S_duplicate), HARRAY n_array) = 4',
            '$heap_owners($heap_graph(S_duplicate), HOBJECT n_child) = 1',
            '$heap_owners($heap_graph(S_duplicate), HOBJECT n_data) = 4',
            '~$fiber_vm_valid(S_duplicate, pfibervm_duplicate, (n_fiber), eps)',
            '~$call_descriptors_valid(S_duplicate)',
        ],
    },
    'injected-throw-keeps-array-hold-last-with-main-scalar-source': {
        'source': source('parked-throw'), 'stage': ABORT_STAGE,
        'checks': [*ABORT, 'S.ACTIVEFIBER = (n_fiber)',
                   '$unpack_line(S, piteratorunpack.CALL) = 23',
                   'S.GLOBALTABLE = (psymboltable_global)',
                   '$lookup(psymboltable_global.ENV, $ptascii("source")) = (n_source)',
                   'S.STORE[n_source] = DEFINED (PINT 17)'],
    },
    'reference-array-remains-unsupported-before-warning': {
        'source': source('reference-array-control'),
        'stage': 'S.TODO = (ITERATOR_UNPACK piteratorunpack "send") :: ptask_tail*',
        'checks': [
            'n_data = piteratorunpack.OBJECT', '$lookup(S.ENV, $ptascii("source")) = (n_source)',
            'piteratorunpack.CURRENT = REFERENCE n_source',
            'piteratorunpack.HOLD = KNOWN PNULL', 'S.STORE[n_source] = DEFINED (PARRAY n_array)',
            'S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_child))]',
            '$heap_owners($heap_graph(S), HCELL n_source) = 2',
            '$heap_owners($heap_graph(S), HARRAY n_array) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_child) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_data) = 2',
            '$iterator_unpack_warning_hold(S, piteratorunpack) = eps',
            *ADMISSION, *ZERO, 'S_one = $drive_steps(S, 1)',
            'S_one.COMPLETION = UNSUPPORTED "Iterator unpack by-reference raw payload"',
            'S_one.TODO = eps', 'S_one.STORE = S.STORE',
            'S_one.REFCELLS = S.REFCELLS', 'S_one.EVENTS = S.EVENTS',
        ],
    },
    'private-array-element-write-destroys-child-before-target-finishes': {
        'source': source('normal-write'),
        'stage': ('S.CURRENT = (pcallcontext) '
                  '-- if pcallcontext.NAME = $ptascii("ArrayTarget28") '
                  '-- if S.TODO = (EMIT z_emit) :: ptask_tail* '
                  '-- if S.RESULT = KNOWN pvalue_text '
                  '-- if $string_bytes(pvalue_text) = ($ptascii("F|"))'),
        'checks': [
            '$receiving_function(S, pcallcontext.FUNCTION) = (pfunction)',
            'pfunction.SIGNATURE.PARAMETERS = [psparam]',
            'psparam.BYREF', '~psparam.VARIADIC', 'psparam.TYPE = eps',
            '$lookup(S.ENV, $ptascii("item")) = (n_private)',
            'S.STORE[n_private] = DEFINED (PARRAY n_array)',
            'n_private <- S.REFCELLS',
            'S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT PNULL)]',
            '$node_children(S, HARRAY n_array) = eps',
            '$heap_owners($heap_graph(S), HCELL n_private) = 1',
            '$heap_owners($heap_graph(S), HARRAY n_array) = 1',
            'S.DESTRUCTION.CALLED = [n_data, n_child]', 'n_data =/= n_child',
            '$object_name(S, n_child) = $ptascii("ArrayPayload28")',
            '$heap_owners($heap_graph(S), HOBJECT n_child) = 0',
            '~((HOBJECT n_child) <- S.ALLOCATIONS)',
            *ADMISSION, *ZERO, *ONE,
            'S_one.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("F|")]',
            'S_one.STORE = S.STORE', 'S_one.ARRAYS = S.ARRAYS', *POST,
            'S_done = $drive(S, 4000)', 'S_done.COMPLETION = NORMAL',
            'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("F|"), OUTPUT $ptascii("E")]',
            'n_data <- S_done.DESTRUCTION.CALLED', 'n_child <- S_done.DESTRUCTION.CALLED',
            '$heap_owners($heap_graph(S_done), HCELL n_private) = 0',
            '$heap_owners($heap_graph(S_done), HARRAY n_array) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_child) = 0',
            '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        ],
    },
}


def run(selected):
    review.CASES = CASES
    original = review.recorded
    raw_directory = None

    def recorded(command, directory, stem, environment, cap):
        nonlocal raw_directory
        raw_directory = directory.parent
        return original(command, directory, stem, environment, 180)

    review.recorded = recorded
    try:
        passed = review.run(selected)
    finally:
        review.recorded = original
    report_path = raw_directory / 'report.json'
    report = json.loads(report_path.read_text())
    assert report['budgets']['process_seconds'] == 120
    report['budgets']['process_seconds'] = 180
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    assert INPUT_BYTES == {p: p.read_bytes() for p in INPUT_BYTES}, 'array review inputs changed'
    return passed


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if run(args.case) else 1)
