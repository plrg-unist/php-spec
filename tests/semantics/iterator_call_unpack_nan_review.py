#!/usr/bin/env python3
"""Reached Iterator-unpack NaN warning ownership and continuation checks."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import fiber_state_review as review

CATALOG = Path(__file__).with_name('iterator_call_unpack_nan_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
SOURCES = {r['id']: r['source'] for r in json.loads(INPUT_BYTES[CATALOG])}
ADMISSION = ['$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
POST = ['$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))']
ZERO = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S']
ONE = ['S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
       'S_one = S_one_budget[.COMPLETION = NORMAL]']
HEADER = ['n_data = piteratorunpack.OBJECT', 'n_cursor = piteratorunpack.ITERATOR',
          '$useriter_cursor_valid(S, n_cursor, n_data)',
          'S.ORIGIN = $unpack_origin(S, piteratorunpack.CALL)',
          '$useriter_tasks_ids(S.TODO) = [n_cursor]',
          'piteratorunpack.INPUT = KNOWN (POBJECT n_data)',
          'piteratorunpack.KEY = KNOWN PNULL',
          '$heap_owners($heap_graph(S), HOBJECT n_data) = 2']
RAW = ['piteratorunpack.CURRENT = REFERENCE n_condition',
       '$heap_count(HCELL n_condition, $tasks_nodes(S.TODO)) = 1',
       '$heap_owners($heap_graph(S), HCELL n_condition) = 2']
NAN = 'S.TODO = (ITERATOR_UNPACK piteratorunpack "valid-nan") :: ptask_tail*'
SENT = ['piteratorunpack.NAMED',
        'piteratorunpack.CALL.SENT.SLOTS = [NAMED_SENT (KNOWN (POBJECT n_sent))]',
        'piteratorunpack.CALL.SENT.NAMED = eps', 'n_sent =/= n_data',
        '$heap_owners($heap_graph(S), HOBJECT n_sent) = 1',
        '$heap_count(HOBJECT n_sent, $tasks_nodes(S.TODO)) = 1',
        '~(n_sent <- S.DESTRUCTION.CALLED)']
RETIRED = ['S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
           '(ITERATOR_UNPACK piteratorunpack_next text_next) :: ptask_tail*',
           'piteratorunpack_next = piteratorunpack[.CURRENT = KNOWN PNULL]',
           'S_one.STORE[n_condition] = S.STORE[n_condition]',
           'S_one.EVENTS = S.EVENTS',
           '$heap_count(HCELL n_condition, $task_nodes(ITERATOR_UNPACK '
           'piteratorunpack_next text_next)) = 0',
           '$heap_owners($heap_graph(S_one), HOBJECT n_data) = 2',
           '$destructor_release_valid(S_one, pdestructionrelease)']

CASES = {
    'raw-reference-warning-dispatch-keeps-one-cell-and-authentic-line': {
        'source': SOURCES['iterator-call-unpack-nan-initial-reference-zero'],
        'stage': ('S.TODO = (ITERATOR_UNPACK piteratorunpack "valid") :: ptask_tail* '
                  '-- if S.RESULT = REFERENCE n_condition'),
        'checks': [
            *HEADER, 'piteratorunpack.CURRENT = KNOWN PNULL',
            'S.STORE[n_condition] = DEFINED (PFLOAT n_bits)',
            '$fparts_nan($float_decode(n_bits))',
            '$heap_owners($heap_graph(S), HCELL n_condition) = 2',
            'piteratorunpack.CALL.SENT.SLOTS = eps', *ADMISSION, *ZERO, *ONE,
            'S_one.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
            'perrorcall.RESUME = ITERATOR_UNPACK piteratorunpack_nan "valid-nan"',
            'piteratorunpack_nan = piteratorunpack[.CURRENT = REFERENCE n_condition]',
            'perrorcall.LEVEL = 2', 'perrorcall.LINE = 23',
            'perrorcall.MESSAGE = $ptascii("unexpected NAN value was coerced to bool")',
            'perrorcall.EVENT = DIAGNOSTIC "Warning" perrorcall.MESSAGE 23',
            '$error_call_valid(S_one, perrorcall)',
            '$useriter_task_ids(ERROR_HANDLER_INVOKE perrorcall) = [n_cursor]',
            '$heap_count(HCELL n_condition, $task_nodes(ERROR_HANDLER_INVOKE perrorcall)) = 1',
            '$heap_owners($heap_graph(S_one), HCELL n_condition) = 2',
            'S_one.RESULT = KNOWN PNULL', 'S_one.EVENTS = S.EVENTS',
            'perrorcall_bad = perrorcall[.LINE = 24]'
            '[.EVENT = DIAGNOSTIC "Warning" perrorcall.MESSAGE 24]',
            'S_bad = S_one[.TODO = (ERROR_HANDLER_INVOKE perrorcall_bad) :: ptask_tail*]',
            '$heap_graph(S_bad) = $heap_graph(S_one)',
            '~$error_call_valid(S_bad, perrorcall_bad)', '~$call_descriptors_valid(S_bad)',
            'perrorcall_level = perrorcall[.LEVEL = 512]',
            'S_level = S_one[.TODO = (ERROR_HANDLER_INVOKE perrorcall_level) :: ptask_tail*]',
            '$heap_graph(S_level) = $heap_graph(S_one)',
            '~$call_descriptors_valid(S_level)', *POST,
        ],
    },
    'warning-clean-retains-cell-and-one-real-cursor': {
        'source': SOURCES['iterator-call-unpack-nan-initial-reference-zero'],
        'stage': ('S.TODO = (ERROR_HANDLER_CLEAN perrorcall) :: ptask_tail* '
                  '-- if perrorcall.RESUME = ITERATOR_UNPACK piteratorunpack "valid-nan"'),
        'checks': [
            *HEADER, *RAW, 'S.STORE[n_condition] = DEFINED (PFLOAT 0)',
            '$error_cleanup_valid(S, perrorcall)',
            '$useriter_task_ids(ERROR_HANDLER_CLEAN perrorcall) = [n_cursor]',
            '$error_task_iterator(ERROR_HANDLER_CLEAN perrorcall) = [n_cursor]',
            *ADMISSION, *ONE, 'S_one.TODO = perrorcall.RESUME :: ptask_tail*',
            '$useriter_tasks_ids(S_one.TODO) = [n_cursor]',
            '$heap_owners($heap_graph(S_one), HCELL n_condition) = 2', *POST,
        ],
    },
    'live-reference-zero-retires-before-empty-teardown': {
        'source': SOURCES['iterator-call-unpack-nan-initial-reference-zero'],
        'stage': NAN,
        'checks': [
            *HEADER, *RAW, 'S.STORE[n_condition] = DEFINED (PFLOAT 0)',
            'piteratorunpack.CALL.SENT.SLOTS = eps', *ADMISSION, *ZERO, *ONE,
            *RETIRED, 'text_next = "finish"',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HCELL n_condition)]', *POST,
        ],
    },
    'copied-nan-survives-source-zero-and-enters-current': {
        'source': SOURCES['iterator-call-unpack-nan-initial-copied-zero'],
        'stage': NAN,
        'checks': [
            *HEADER, 'piteratorunpack.CURRENT = KNOWN (PFLOAT n_bits)',
            '$fparts_nan($float_decode(n_bits))',
            '$lookup(S.ENV, $ptascii("condition")) = (n_condition)',
            'S.STORE[n_condition] = DEFINED (PFLOAT 0)',
            '$heap_count(HCELL n_condition, $tasks_nodes(S.TODO)) = 0',
            *ADMISSION, *ONE, *RETIRED, 'text_next = "current-start"',
            'pdestructionrelease.JOBS = eps', *POST,
        ],
    },
    'integer-minimum-reread-uses-signed-zero-bits': {
        'source': SOURCES['iterator-call-unpack-nan-initial-reference-intmin'],
        'stage': NAN,
        'checks': [
            *HEADER, *RAW,
            'S.STORE[n_condition] = DEFINED (PINT $(-9223372036854775808))',
            '$truth(S, PINT $(-9223372036854775808))',
            'piteratorunpack.CALL.SENT.SLOTS = eps', *ADMISSION, *ONE,
            *RETIRED, 'text_next = "finish"',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HCELL n_condition)]', *POST,
        ],
    },
    'live-reference-one-enters-current-after-raw-cell-release': {
        'source': SOURCES['iterator-call-unpack-nan-initial-reference-one'],
        'stage': NAN,
        'checks': [
            *HEADER, *RAW, 'S.STORE[n_condition] = DEFINED (PFLOAT 4607182418800017408)',
            *ADMISSION, *ONE, *RETIRED, 'text_next = "current-start"',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HCELL n_condition)]', *POST,
        ],
    },
    'later-named-false-keeps-the-already-sent-object': {
        'source': SOURCES['iterator-call-unpack-nan-later-named-reference-zero'],
        'stage': NAN,
        'checks': [
            *HEADER, *RAW, *SENT, 'S.STORE[n_condition] = DEFINED (PFLOAT 0)',
            *ADMISSION, *ONE, *RETIRED, 'text_next = "finish"',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HCELL n_condition)]',
            '$heap_owners($heap_graph(S_one), HOBJECT n_sent) = 1', *POST,
        ],
    },
    'later-finish-retires-data-and-input-before-target-entry': {
        'source': SOURCES['iterator-call-unpack-nan-later-named-reference-zero'],
        'stage': 'S.TODO = (ITERATOR_UNPACK piteratorunpack "finish") :: ptask_tail*',
        'checks': [
            *HEADER, *SENT, 'piteratorunpack.CURRENT = KNOWN PNULL',
            *ADMISSION, *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(UNPACK_ARGS punpackcall_next) :: ptask_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_data), '
            'DESTRUCTION_VALUE (HOBJECT n_data)]',
            'punpackcall_next.SENT = piteratorunpack.CALL.SENT',
            '$iterator_lookup(S_one.ITERATORS, n_cursor) = eps',
            '$heap_owners($heap_graph(S_one), HOBJECT n_sent) = 1',
            '$heap_count(HOBJECT n_sent, $task_nodes(UNPACK_ARGS punpackcall_next)) = 1',
            'S_one.EVENTS = S.EVENTS',
            '$destructor_release_valid(S_one, pdestructionrelease)', *POST,
        ],
    },
    'thrown-later-warning-queues-raw-data-input-then-sent': {
        'source': SOURCES['iterator-call-unpack-nan-later-named-reference-throw'],
        'stage': ('S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
                  '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail* '
                  '-- if pdestructionoperation.SOURCE = ITERATOR_UNPACK piteratorunpack "valid-nan" '
                  '-- if pdestructionoperation.PENDING = (n_error) '
                  '-- if piteratorunpack.CURRENT = REFERENCE n_condition '
                  '-- if piteratorunpack.CALL.SENT.SLOTS = [NAMED_SENT (KNOWN (POBJECT n_sent))] '
                  '-- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HCELL n_condition), '
                  'DESTRUCTION_VALUE (HOBJECT piteratorunpack.OBJECT), '
                  'DESTRUCTION_VALUE (HOBJECT piteratorunpack.OBJECT), '
                  'DESTRUCTION_VALUE (HOBJECT n_sent)]'),
        'checks': [
            'n_data = piteratorunpack.OBJECT', 'piteratorunpack.NAMED',
            'S.ITERATORS = eps', 'S.CURRENT = eps',
            '$heap_count(HCELL n_condition, $tasks_nodes(S.TODO)) = 1',
            '$heap_owners($heap_graph(S), HCELL n_condition) = 2',
            '$heap_count(HOBJECT n_data, $tasks_nodes(S.TODO)) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_sent) = 1',
            '~(n_sent <- S.DESTRUCTION.CALLED)',
            '$throwable_field(S, n_error, "code") = PINT 41',
            '$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = [HOBJECT n_error]',
            '$useriter_task_ids(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = eps',
            '$eager_operation_source_valid(S, pdestructionoperation)',
            '$destructor_operation_valid(S, pdestructionoperation)',
            '$destructor_release_valid(S, pdestructionrelease)', *ADMISSION, *ZERO,
        ],
    },
    'retired-data-source-receipt-keeps-pending-sent-cleanup-authentic': {
        'source': SOURCES['iterator-call-unpack-nan-later-named-reference-throw'],
        'stage': ('S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
                  '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail* '
                  '-- if pdestructionoperation.SOURCE = ITERATOR_UNPACK piteratorunpack "valid-nan" '
                  '-- if pdestructionoperation.PENDING = (n_error) '
                  '-- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_sent)]'),
        'checks': [
            'n_data = piteratorunpack.OBJECT',
            '~((HOBJECT n_data) <- S.ALLOCATIONS)',
            '$heap_owners($heap_graph(S), HOBJECT n_data) = 0',
            'n_data <- S.DESTRUCTION.CALLED',
            '$heap_owners($heap_graph(S), HOBJECT n_sent) = 1',
            '~(n_sent <- S.DESTRUCTION.CALLED)',
            '$throwable_field(S, n_error, "code") = PINT 41',
            '$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = [HOBJECT n_error]',
            '$eager_operation_source_valid(S, pdestructionoperation)',
            '$destructor_operation_valid(S, pdestructionoperation)',
            '$destructor_release_valid(S, pdestructionrelease)', *ADMISSION,
        ],
    },
    'parked-handler-keeps-raw-reference-cursor-and-data': {
        'source': SOURCES['iterator-call-unpack-nan-fiber-reference-zero'],
        'stage': ('S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_main* '
                  '-- if pconfigcall.KIND = INTRINSIC_FIBER_RESUME '
                  '-- if pconfigcall.OWNER = (n_fiber) '
                  '-- if $fiber_at(S, n_fiber) = (pfiber) '
                  '-- if pfiber.VM = (pfibervm) '
                  '-- if pfibervm.FRAMES = [pframe_unpack, pframe_base] '
                  '-- if pframe_unpack.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_unpack* '
                  '-- if perrorcall.RESUME = ITERATOR_UNPACK piteratorunpack "valid-nan"'),
        'checks': [
            'n_data = piteratorunpack.OBJECT', 'n_cursor = piteratorunpack.ITERATOR',
            'piteratorunpack.CURRENT = REFERENCE n_condition',
            'S.STORE[n_condition] = DEFINED (PFLOAT 0)',
            'S.ACTIVEFIBER = eps', 'S.FIBERCALLERS = eps',
            'pfiber.STATUS = FIBER_SUSPENDED',
            'pfibervm.CURRENT = (pcallcontext_saved)',
            'S_view = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)]'
            '[.FIBERCALLERS = eps][.COMPLETION = NORMAL]',
            'S_scope = $constant_frame_scope(S_view, pframe_unpack, [pframe_base])',
            '$useriter_frames_ids(pfibervm.FRAMES) = [n_cursor]',
            '$heap_owners($heap_graph(S), HOBJECT n_data) = 2',
            '$lookup(S.ENV, $ptascii("condition")) = (n_condition)',
            '$lookup(pfibervm.TABLE.ENV, $ptascii("condition")) = (n_condition)',
            '$heap_count(HCELL n_condition, $environment_nodes(S.ENV)) = 1',
            '$heap_count(HCELL n_condition, $environment_nodes(pfibervm.TABLE.ENV)) = 1',
            '$heap_owners($heap_graph(S), HCELL n_condition) = 3',
            '$heap_count(HCELL n_condition, $task_nodes(perrorcall.RESUME)) = 1',
            '$fiber_vm_valid(S, pfibervm, (n_fiber), eps)',
            '$error_context_valid(S_view, pcallcontext_saved)',
            '$error_entered_call_valid(S_scope, perrorcall)',
            'pcallcontext_saved.LINE = 24', 'perrorcall.LINE = 24',
            '$iterator_unpack_result_valid(S_scope, piteratorunpack, "valid-nan")',
            *ADMISSION, *ZERO, 'S_zero.OBJECTS[n_fiber] = FIBER pfiber',
            'piteratorunpack_bad = piteratorunpack[.CALL = piteratorunpack.CALL[.LINE = 25]]',
            'perrorcall_bad = perrorcall[.LINE = 25]'
            '[.EVENT = DIAGNOSTIC "Warning" perrorcall.MESSAGE 25]'
            '[.RESUME = ITERATOR_UNPACK piteratorunpack_bad "valid-nan"]',
            'pframe_bad = pframe_unpack[.TODO = (ERROR_HANDLER_RESULT perrorcall_bad) :: ptask_unpack*]',
            'pfibervm_bad = pfibervm[.CURRENT = (pcallcontext_saved[.LINE = 25])]'
            '[.FRAMES = [pframe_bad, pframe_base]]',
            'S_bad = $fiber_put(S, n_fiber, pfiber[.VM = (pfibervm_bad)])',
            '$heap_graph(S_bad) = $heap_graph(S)',
            '~$fiber_vm_valid(S_bad, pfibervm_bad, (n_fiber), eps)',
            '~$call_descriptors_valid(S_bad)',
            'pframe_duplicate = pframe_unpack[.TODO = (ERROR_HANDLER_RESULT perrorcall) :: '
            '(ERROR_HANDLER_RESULT perrorcall) :: ptask_unpack*]',
            'pfibervm_duplicate = pfibervm[.FRAMES = [pframe_duplicate, pframe_base]]',
            'S_duplicate = $fiber_put(S, n_fiber, pfiber[.VM = (pfibervm_duplicate)])',
            '$useriter_frames_ids(pfibervm_duplicate.FRAMES) = [n_cursor, n_cursor]',
            '$heap_valid($heap_graph(S_duplicate))',
            '$heap_owners($heap_graph(S_duplicate), HOBJECT n_data) = 4',
            '$heap_owners($heap_graph(S_duplicate), HCELL n_condition) = 4',
            '~$fiber_vm_valid(S_duplicate, pfibervm_duplicate, (n_fiber), eps)',
            '~$call_descriptors_valid(S_duplicate)',
        ],
    },
    'raw-bool-change-stops-as-unsupported-after-real-handler': {
        'source': SOURCES['iterator-call-unpack-nan-raw-bool-change-control'],
        'stage': NAN,
        'checks': [
            *HEADER, *RAW, 'S.STORE[n_condition] = DEFINED (PBOOL false)',
            *ADMISSION, 'S_one = $drive_steps(S, 1)',
            'S_one.COMPLETION = UNSUPPORTED "Iterator unpack valid NaN raw payload type change"',
            'S_one.TODO = eps', 'S_one.STORE[n_condition] = S.STORE[n_condition]',
            'S_one.EVENTS = S.EVENTS',
        ],
    },
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    assert not args.case or set(args.case) <= CASES.keys(), 'unknown Iterator NaN review case'
    review.ROOT = ROOT
    review.CASES = CASES
    passed = review.run(args.case)
    assert all(p.read_bytes() == data for p, data in INPUT_BYTES.items()), \
        'Iterator NaN review inputs changed during run'
    raise SystemExit(0 if passed else 1)
