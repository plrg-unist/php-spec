#!/usr/bin/env python3
"""Reached copied-object warning holds, private cells and ordered retirement."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import fiber_state_review as review

CATALOG = Path(__file__).with_name('iterator_call_unpack_object_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
SOURCES = {r['id']: r['source'] for r in json.loads(INPUT_BYTES[CATALOG])}
ADMISSION = ['$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
POST = ['$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))']
ZERO = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S']
ONE = ['S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
       'S_one = S_one_budget[.COMPLETION = NORMAL]']
COPIED = ['n_data = piteratorunpack.OBJECT', 'n_cursor = piteratorunpack.ITERATOR',
          'piteratorunpack.CURRENT = KNOWN (POBJECT n_payload)', 'n_payload =/= n_data',
          'piteratorunpack.INPUT = KNOWN (POBJECT n_data)',
          'piteratorunpack.CALL.SENT = {SLOTS eps, NAMED eps}',
          '$operand_nodes(piteratorunpack.CURRENT) = [HOBJECT n_payload]',
          '$heap_owners($heap_graph(S), HOBJECT n_data) = 2',
          '~(n_payload <- S.DESTRUCTION.CALLED)']
ACTIVE = ['$useriter_cursor_valid(S, n_cursor, n_data)',
          'S.ORIGIN = $unpack_origin(S, piteratorunpack.CALL)',
          '$useriter_tasks_ids(S.TODO) = [n_cursor]']
SOURCE_NULL = ['$lookup(S.ENV, $ptascii("source")) = (n_source)',
               'S.STORE[n_source] = DEFINED PNULL',
               '$heap_owners($heap_graph(S), HCELL n_source) = 1']
HELD = ['piteratorunpack.HOLD = piteratorunpack.CURRENT',
        '$iterator_unpack_hold_valid(piteratorunpack, "byref")',
        '$iterator_unpack_warning_hold(S, piteratorunpack) = (piteratorunpack.CURRENT)',
        '$heap_owners($heap_graph(S), HOBJECT n_payload) = 2']
FRESH = ['S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
         '(ITERATOR_UNPACK piteratorunpack_next "next-start") :: ptask_tail*',
         'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_payload)]',
         'piteratorunpack_next.CURRENT = KNOWN PNULL',
         'piteratorunpack_next.KEY = KNOWN PNULL',
         'piteratorunpack_next.HOLD = KNOWN PNULL',
         'piteratorunpack_next.CALL.SENT.SLOTS = [NAMED_SENT (REFERENCE n_private)]',
         'piteratorunpack_next.CALL.SENT.NAMED = eps',
         'S_one.STORE[n_private] = DEFINED (POBJECT n_payload)',
         'n_private <- S_one.REFCELLS', 'n_private =/= n_source',
         'S_one.STORE[n_source] = DEFINED PNULL',
         '$heap_owners($heap_graph(S_one), HCELL n_private) = 1',
         '$heap_count(HCELL n_private, $tasks_nodes(S_one.TODO)) = 1',
         '$node_children(S_one, HCELL n_private) = [HOBJECT n_payload]',
         '$heap_owners($heap_graph(S_one), HOBJECT n_payload) = 2',
         '$heap_owners($heap_graph(S_one), HOBJECT n_data) = 2',
         '~(n_payload <- S_one.DESTRUCTION.CALLED)',
         '$destructor_release_valid(S_one, pdestructionrelease)', *POST]
ABORT_STAGE = ('S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
               '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail* '
               '-- if pdestructionoperation.PENDING = (n_error) '
               '-- if pdestructionoperation.SOURCE = ITERATOR_UNPACK piteratorunpack "byref"')
ABORT = [*COPIED, *HELD,
         '$iterator_lookup(S.ITERATORS, n_cursor) = eps',
         '$useriter_task_ids(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = eps',
         'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_payload), '
         'DESTRUCTION_VALUE (HOBJECT n_data), DESTRUCTION_VALUE (HOBJECT n_data), '
         'DESTRUCTION_VALUE (HOBJECT n_payload)]',
         'pdestructionoperation.CALLER = S.CURRENT',
         'pdestructionoperation.ORIGIN = piteratorunpack.CALL.CALLSITE',
         '$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = [HOBJECT n_error]',
         '$throwable_live(S, n_error)', '$throwable_field(S, n_error, "code") = PINT 51',
         '$eager_operation_source_valid(S, pdestructionoperation)',
         '$destructor_operation_valid(S, pdestructionoperation)',
         '$destructor_release_valid(S, pdestructionrelease)', *ADMISSION, *ZERO]
MESSAGE = ('$ptascii("Cannot pass by-reference argument 1 of HoldTarget22() '
           'by unpacking a Traversable, passing by-value instead")')

CASES = {
    'copied-object-warning-adds-one-detached-owner-before-handler': {
        'source': SOURCES['iterator-call-unpack-object-copied-positional-drop'],
        'stage': 'S.TODO = (ITERATOR_UNPACK piteratorunpack "send") :: ptask_tail*',
        'checks': [
            *COPIED, *ACTIVE, 'piteratorunpack.HOLD = KNOWN PNULL',
            'piteratorunpack.KEY = KNOWN (PINT 0)',
            '$lookup(S.ENV, $ptascii("source")) = (n_source)',
            'S.STORE[n_source] = DEFINED (POBJECT n_payload)',
            '$heap_owners($heap_graph(S), HOBJECT n_payload) = 2',
            '~$iterator_unpack_scalar_operand(S, piteratorunpack.CURRENT)',
            '$iterator_unpack_warning_hold(S, piteratorunpack) = (piteratorunpack.CURRENT)',
            *ADMISSION, *ZERO, *ONE,
            'S_one.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
            'perrorcall.RESUME = ITERATOR_UNPACK piteratorunpack_held "byref"',
            'piteratorunpack_held = piteratorunpack[.HOLD = piteratorunpack.CURRENT]',
            'perrorcall.LEVEL = 2', 'perrorcall.LINE = 21',
            'perrorcall.MESSAGE = ' + MESSAGE,
            '$error_call_valid(S_one, perrorcall)',
            '$heap_owners($heap_graph(S_one), HOBJECT n_payload) = 3',
            '$heap_owners($heap_graph(S_one), HOBJECT n_data) = 2',
            'S_one.STORE = S.STORE', 'S_one.EVENTS = S.EVENTS', *POST,
            'S_early = S[.TODO = (ITERATOR_UNPACK piteratorunpack_held "send") :: ptask_tail*]',
            '$heap_valid($heap_graph(S_early))',
            '$heap_owners($heap_graph(S_early), HOBJECT n_payload) = 3',
            '~$iterator_unpack_result_valid(S_early, piteratorunpack_held, "send")',
            '~$call_descriptors_valid(S_early)',
            'piteratorunpack_later = piteratorunpack[.CALL = '
            'piteratorunpack.CALL[.SENT.SLOTS = [NAMED_SENT (KNOWN (PINT 1))]]]',
            '$iterator_unpack_warning_hold(S, piteratorunpack_later) = eps',
            '$iterator_unpack_warning_hold(S, piteratorunpack_later[.CURRENT = KNOWN (PINT 1)]) '
            '= (KNOWN PNULL)',
        ],
    },
    'handler-source-drop-transfers-hold-to-distinct-private-cell': {
        'source': SOURCES['iterator-call-unpack-object-copied-positional-drop'],
        'stage': 'S.TODO = (ITERATOR_UNPACK piteratorunpack "byref") :: ptask_tail*',
        'checks': [
            *COPIED, *ACTIVE, *SOURCE_NULL, *HELD, *ADMISSION, *ZERO,
            'n_private = |S.STORE|', *ONE, *FRESH, '~piteratorunpack_next.NAMED',
            'S_two_budget = $drive_steps(S_one, 1)', 'S_two_budget.COMPLETION = BUDGET',
            'S_two = S_two_budget[.COMPLETION = NORMAL]',
            'S_two.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_done) :: '
            '(ITERATOR_UNPACK piteratorunpack_next "next-start") :: ptask_tail*',
            'pdestructionrelease_done.JOBS = eps',
            '$heap_owners($heap_graph(S_two), HOBJECT n_payload) = 1',
            '$heap_owners($heap_graph(S_two), HCELL n_private) = 1',
            '~(n_payload <- S_two.DESTRUCTION.CALLED)', 'S_two.EVENTS = S.EVENTS',
            '$call_descriptors_valid(S_two)', '$heap_valid($heap_graph(S_two))',
            'piteratorunpack_early = piteratorunpack_next[.HOLD = KNOWN (POBJECT n_payload)]',
            'S_early = S_one[.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(ITERATOR_UNPACK piteratorunpack_early "next-start") :: ptask_tail*]',
            '$heap_valid($heap_graph(S_early))',
            '~$call_descriptors_valid(S_early)',
        ],
    },
    'named-object-warning-transfers-one-hold-into-fixed-private-slot': {
        'source': SOURCES['iterator-call-unpack-object-copied-named-drop'],
        'stage': 'S.TODO = (ITERATOR_UNPACK piteratorunpack "byref") :: ptask_tail*',
        'checks': [
            *COPIED, *ACTIVE, *SOURCE_NULL, *HELD,
            'piteratorunpack.KEY = KNOWN pvalue_key',
            '$fiber_traversal_key(pvalue_key) = (KSTRING ($ptascii("item")))',
            '$iterator_unpack_named_target(S, piteratorunpack) = NAMED_POSITION 0',
            '$iterator_unpack_warning_message(S, piteratorunpack) = ' + MESSAGE,
            *ADMISSION, 'n_private = |S.STORE|', *ONE, *FRESH,
            'piteratorunpack_next.NAMED',
        ],
    },
    'parked-copied-object-hold-preserves-owners-and-source-authority': {
        'source': SOURCES['iterator-call-unpack-object-copied-fiber-resume'],
        'stage': ('S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_main* '
                  '-- if pconfigcall.KIND = INTRINSIC_FIBER_RESUME '
                  '-- if pconfigcall.OWNER = (n_fiber) '
                  '-- if $fiber_at(S, n_fiber) = (pfiber) -- if pfiber.VM = (pfibervm) '
                  '-- if pfibervm.FRAMES = [pframe_unpack, pframe_base] '
                  '-- if pframe_unpack.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_unpack* '
                  '-- if perrorcall.RESUME = ITERATOR_UNPACK piteratorunpack "byref"'),
        'checks': [
            *COPIED, *HELD, '$lookup(S.ENV, $ptascii("source")) = (n_source)',
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
            'piteratorunpack_foreign = piteratorunpack[.HOLD = KNOWN (POBJECT n_data)]',
            'perrorcall_foreign = perrorcall[.RESUME = '
            'ITERATOR_UNPACK piteratorunpack_foreign "byref"]',
            'pframe_foreign = pframe_unpack[.TODO = '
            '(ERROR_HANDLER_RESULT perrorcall_foreign) :: ptask_unpack*]',
            'pfibervm_foreign = pfibervm[.FRAMES = [pframe_foreign, pframe_base]]',
            'S_foreign = $fiber_put(S, n_fiber, pfiber[.VM = (pfibervm_foreign)])',
            '$heap_valid($heap_graph(S_foreign))',
            '$heap_owners($heap_graph(S_foreign), HOBJECT n_payload) = 1',
            '$heap_owners($heap_graph(S_foreign), HOBJECT n_data) = 3',
            '~$fiber_vm_valid(S_foreign, pfibervm_foreign, (n_fiber), eps)',
            '~$call_descriptors_valid(S_foreign)',
            'pframe_duplicate = pframe_unpack[.TODO = (ERROR_HANDLER_RESULT perrorcall) :: '
            '(ERROR_HANDLER_RESULT perrorcall) :: ptask_unpack*]',
            'pfibervm_duplicate = pfibervm[.FRAMES = [pframe_duplicate, pframe_base]]',
            'S_duplicate = $fiber_put(S, n_fiber, pfiber[.VM = (pfibervm_duplicate)])',
            '$useriter_frames_ids(pfibervm_duplicate.FRAMES) = [n_cursor, n_cursor]',
            '$heap_valid($heap_graph(S_duplicate))',
            '$heap_owners($heap_graph(S_duplicate), HOBJECT n_payload) = 4',
            '$heap_owners($heap_graph(S_duplicate), HOBJECT n_data) = 4',
            '$heap_owners($heap_graph(S_duplicate), HCELL n_source) = 2',
            '~$fiber_vm_valid(S_duplicate, pfibervm_duplicate, (n_fiber), eps)',
            '~$call_descriptors_valid(S_duplicate)',
        ],
    },
    'thrown-object-warning-retires-raw-before-data-input-and-hold': {
        'source': SOURCES['iterator-call-unpack-object-copied-positional-throw'],
        'stage': ABORT_STAGE,
        'checks': [
            *ABORT, *SOURCE_NULL, *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_next) :: '
            '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*',
            'pdestructionrelease_next.JOBS = [DESTRUCTION_VALUE (HOBJECT n_data), '
            'DESTRUCTION_VALUE (HOBJECT n_data), DESTRUCTION_VALUE (HOBJECT n_payload)]',
            '$heap_owners($heap_graph(S_one), HOBJECT n_payload) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_data) = 2',
            '~(n_payload <- S_one.DESTRUCTION.CALLED)', 'S_one.EVENTS = S.EVENTS', *POST,
        ],
    },
    'last-object-hold-enters-destructor-after-iterator-retirement': {
        'source': SOURCES['iterator-call-unpack-object-copied-positional-throw'],
        'stage': (ABORT_STAGE + ' -- if pdestructionrelease.JOBS = '
                  '[DESTRUCTION_VALUE (HOBJECT n_payload)] '
                  '-- if piteratorunpack.CURRENT = KNOWN (POBJECT n_payload)'),
        'checks': [
            'n_data = piteratorunpack.OBJECT', 'n_payload =/= n_data',
            'piteratorunpack.HOLD = piteratorunpack.CURRENT',
            '$heap_owners($heap_graph(S), HOBJECT n_payload) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_data) = 0',
            'n_data <- S.DESTRUCTION.CALLED', '~(n_payload <- S.DESTRUCTION.CALLED)',
            '$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = [HOBJECT n_error]',
            '$eager_operation_source_valid(S, pdestructionoperation)',
            '$destructor_operation_valid(S, pdestructionoperation)',
            '$throwable_field(S, n_error, "code") = PINT 51', *ADMISSION, *ZERO, *ONE,
            'S_one.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: '
            '(DESTRUCTOR_RELEASE pdestructionrelease_done) :: '
            '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*',
            'pdestructionrelease_done.JOBS = eps',
            'pdestructorcall.OBJECT = n_payload', 'pdestructorcall.PENDING = (n_error)',
            'n_payload <- S_one.DESTRUCTION.CALLED', 'n_data <- S_one.DESTRUCTION.CALLED',
            'S_one.EVENTS = S.EVENTS', *POST,
        ],
    },
    'retired-object-source-receipt-is-nonowning-and-rejects-missing-hold': {
        'source': SOURCES['iterator-call-unpack-object-copied-positional-throw'],
        'stage': (ABORT_STAGE + ' -- if pdestructionrelease.JOBS = eps '
                  '-- if piteratorunpack.CURRENT = KNOWN (POBJECT n_payload) '
                  '-- if n_payload <- S.DESTRUCTION.CALLED'),
        'checks': [
            'n_data = piteratorunpack.OBJECT',
            'piteratorunpack.HOLD = piteratorunpack.CURRENT',
            '~((HOBJECT n_payload) <- S.ALLOCATIONS)',
            '$heap_owners($heap_graph(S), HOBJECT n_payload) = 0',
            '$heap_owners($heap_graph(S), HOBJECT n_data) = 0',
            '$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = [HOBJECT n_error]',
            '$iterator_unpack_hold_valid(piteratorunpack, "byref")',
            '$eager_operation_source_valid(S, pdestructionoperation)',
            '$destructor_operation_valid(S, pdestructionoperation)',
            '$throwable_live(S, n_error)', *ADMISSION, *ZERO,
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
        ],
    },
    'injected-fiber-throw-keeps-detached-object-last-in-abort-jobs': {
        'source': SOURCES['iterator-call-unpack-object-copied-fiber-throw'],
        'stage': ABORT_STAGE,
        'checks': [*ABORT, 'S.ACTIVEFIBER = (n_fiber)',
                   '$unpack_line(S, piteratorunpack.CALL) = 23'],
    },
    'live-reference-object-remains-unsupported-before-warning': {
        'source': SOURCES['iterator-call-unpack-object-reference-object-control'],
        'stage': 'S.TODO = (ITERATOR_UNPACK piteratorunpack "send") :: ptask_tail*',
        'checks': [
            'n_data = piteratorunpack.OBJECT', 'n_cursor = piteratorunpack.ITERATOR',
            '$lookup(S.ENV, $ptascii("source")) = (n_source)',
            'piteratorunpack.CURRENT = REFERENCE n_source',
            'piteratorunpack.HOLD = KNOWN PNULL',
            'S.STORE[n_source] = DEFINED (POBJECT n_payload)',
            '$heap_owners($heap_graph(S), HCELL n_source) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_payload) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_data) = 2',
            '$iterator_unpack_warning_hold(S, piteratorunpack) = eps',
            *ADMISSION, *ZERO, 'S_one = $drive_steps(S, 1)',
            'S_one.COMPLETION = UNSUPPORTED "Iterator unpack by-reference raw payload"',
            'S_one.TODO = eps', 'S_one.STORE = S.STORE',
            'S_one.REFCELLS = S.REFCELLS', 'S_one.EVENTS = S.EVENTS',
        ],
    },
}


def run(selected):
    review.CASES = CASES
    passed = review.run(selected)
    assert INPUT_BYTES == {p: p.read_bytes() for p in INPUT_BYTES}, 'object review inputs changed'
    return passed


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if run(args.case) else 1)
