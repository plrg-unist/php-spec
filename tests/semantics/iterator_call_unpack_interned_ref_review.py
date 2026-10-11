#!/usr/bin/env python3
"""Reached interned-reference warning rereads, owners and payload boundaries."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import fiber_state_review as review

CATALOG = Path(__file__).with_name('iterator_call_unpack_interned_ref_cases.json')
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
          '$heap_owners($heap_graph(S), HOBJECT n_data) = 2',
          'piteratorunpack.CALL.SENT.SLOTS = eps',
          'piteratorunpack.CALL.SENT.NAMED = eps',
          '$lookup(S.ENV, $ptascii("source")) = (n_source)',
          'piteratorunpack.CURRENT = REFERENCE n_source',
          '$operand_nodes(piteratorunpack.CURRENT) = [HCELL n_source]',
          '$heap_owners($heap_graph(S), HCELL n_source) = 2']
HANDLER = ['pvalue_current = PSTRING_CARRIER INTERNED_STRING ($ptascii("handler"))',
           'S.STORE[n_source] = DEFINED pvalue_current',
           '$string_carrier_valid(S, pvalue_current)']
FRESH = ['S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
         '(ITERATOR_UNPACK piteratorunpack_next "next-start") :: ptask_tail*',
         'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HCELL n_source)]',
         'piteratorunpack_next.CURRENT = KNOWN PNULL',
         'piteratorunpack_next.KEY = KNOWN PNULL',
         'S_one.STORE[n_private] = DEFINED pvalue_current',
         'n_private <- S_one.REFCELLS', 'n_private =/= n_source',
         'S_one.STORE[n_source] = S.STORE[n_source]',
         'S_one.STRINGDATA = S.STRINGDATA',
         '$heap_owners($heap_graph(S_one), HCELL n_private) = 1',
         '$heap_count(HCELL n_private, $tasks_nodes(S_one.TODO)) = 1',
         '$heap_owners($heap_graph(S_one), HCELL n_source) = 2',
         '$heap_owners($heap_graph(S_one), HOBJECT n_data) = 2',
         '$destructor_release_valid(S_one, pdestructionrelease)']
BYREF = 'S.TODO = (ITERATOR_UNPACK piteratorunpack "byref") :: ptask_tail*'
MESSAGE = ('$ptascii("Cannot pass by-reference argument 1 of StringTarget21() '
           'by unpacking a Traversable, passing by-value instead")')

CASES = {
    'live-interned-handler-reread-creates-private-positional-cell': {
        'source': SOURCES['iterator-call-unpack-interned-ref-key-handler-literals'],
        'stage': BYREF,
        'checks': [
            *HEADER, *HANDLER, 'piteratorunpack.KEY = KNOWN (PINT 0)',
            '$unpack_line(S, piteratorunpack.CALL) = 21',
            'n_private = |S.STORE|', *ADMISSION, *ZERO, *ONE, *FRESH,
            'piteratorunpack_next.CALL.SENT.SLOTS = [NAMED_SENT (REFERENCE n_private)]',
            'piteratorunpack_next.CALL.SENT.NAMED = eps',
            '~piteratorunpack_next.NAMED', *POST,
        ],
    },
    'live-interned-named-variadic-reread-creates-private-extra-cell': {
        'source': SOURCES['iterator-call-unpack-interned-ref-named-variadic'],
        'stage': BYREF,
        'checks': [
            *HEADER, *HANDLER, 'piteratorunpack.KEY = KNOWN pvalue_key',
            '$fiber_traversal_key(pvalue_key) = (KSTRING ($ptascii("named")))',
            '$iterator_unpack_named_target(S, piteratorunpack) = NAMED_EXTRA ($ptascii("named"))',
            '$iterator_unpack_warning_message(S, piteratorunpack) = ' + MESSAGE,
            'n_private = |S.STORE|', *ADMISSION, *ONE, *FRESH,
            'piteratorunpack_next.CALL.SENT.SLOTS = eps',
            'piteratorunpack_next.CALL.SENT.NAMED = [($ptascii("named"), REFERENCE n_private)]',
            'piteratorunpack_next.NAMED', *POST,
        ],
    },
    'parked-live-interned-cell-keeps-three-owners-and-source-authority': {
        'source': SOURCES['iterator-call-unpack-interned-ref-fiber-resume'],
        'stage': ('S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_main* '
                  '-- if pconfigcall.KIND = INTRINSIC_FIBER_RESUME '
                  '-- if pconfigcall.OWNER = (n_fiber) '
                  '-- if $fiber_at(S, n_fiber) = (pfiber) -- if pfiber.VM = (pfibervm) '
                  '-- if pfibervm.FRAMES = [pframe_unpack, pframe_base] '
                  '-- if pframe_unpack.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_unpack* '
                  '-- if perrorcall.RESUME = ITERATOR_UNPACK piteratorunpack "byref"'),
        'checks': [
            'n_data = piteratorunpack.OBJECT', 'n_cursor = piteratorunpack.ITERATOR',
            'piteratorunpack.CURRENT = REFERENCE n_source',
            'piteratorunpack.INPUT = KNOWN (POBJECT n_data)',
            'piteratorunpack.CALL.SENT.SLOTS = eps',
            '$lookup(S.ENV, $ptascii("source")) = (n_source)',
            '$lookup(pfibervm.TABLE.ENV, $ptascii("source")) = (n_source)',
            'S.STORE[n_source] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("main")))',
            '$heap_count(HCELL n_source, $environment_nodes(S.ENV)) = 1',
            '$heap_count(HCELL n_source, $environment_nodes(pfibervm.TABLE.ENV)) = 1',
            '$heap_count(HCELL n_source, $task_nodes(perrorcall.RESUME)) = 1',
            '$heap_owners($heap_graph(S), HCELL n_source) = 3',
            '$heap_owners($heap_graph(S), HOBJECT n_data) = 2',
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
            'pframe_duplicate = pframe_unpack[.TODO = (ERROR_HANDLER_RESULT perrorcall) :: '
            '(ERROR_HANDLER_RESULT perrorcall) :: ptask_unpack*]',
            'pfibervm_duplicate = pfibervm[.FRAMES = [pframe_duplicate, pframe_base]]',
            'S_duplicate = $fiber_put(S, n_fiber, pfiber[.VM = (pfibervm_duplicate)])',
            '$useriter_frames_ids(pfibervm_duplicate.FRAMES) = [n_cursor, n_cursor]',
            '$heap_valid($heap_graph(S_duplicate))',
            '$heap_owners($heap_graph(S_duplicate), HOBJECT n_data) = 4',
            '$heap_owners($heap_graph(S_duplicate), HCELL n_source) = 4',
            '~$fiber_vm_valid(S_duplicate, pfibervm_duplicate, (n_fiber), eps)',
            '~$call_descriptors_valid(S_duplicate)',
        ],
    },
    'thrown-live-interned-warning-retires-raw-cell-before-data-and-input': {
        'source': SOURCES['iterator-call-unpack-interned-ref-fiber-throw'],
        'stage': ('S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
                  '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail* '
                  '-- if pdestructionoperation.PENDING = (n_error) '
                  '-- if pdestructionoperation.SOURCE = ITERATOR_UNPACK piteratorunpack "byref"'),
        'checks': [
            'n_data = piteratorunpack.OBJECT', 'n_cursor = piteratorunpack.ITERATOR',
            'piteratorunpack.CURRENT = REFERENCE n_source',
            'S.STORE[n_source] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("main")))',
            'piteratorunpack.INPUT = KNOWN (POBJECT n_data)',
            'piteratorunpack.CALL.SENT.SLOTS = eps', 'piteratorunpack.CALL.SENT.NAMED = eps',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HCELL n_source), '
            'DESTRUCTION_VALUE (HOBJECT n_data), DESTRUCTION_VALUE (HOBJECT n_data)]',
            '$iterator_lookup(S.ITERATORS, n_cursor) = eps',
            '$heap_count(HCELL n_source, $tasks_nodes(S.TODO)) = 1',
            '$heap_owners($heap_graph(S), HCELL n_source) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_data) = 2',
            '~(n_data <- S.DESTRUCTION.CALLED)',
            'pdestructionoperation.CALLER = S.CURRENT',
            'pdestructionoperation.ORIGIN = piteratorunpack.CALL.CALLSITE',
            '$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = [HOBJECT n_error]',
            '$useriter_task_ids(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = eps',
            '$throwable_live(S, n_error)', '$throwable_field(S, n_error, "code") = PINT 51',
            '$eager_operation_source_valid(S, pdestructionoperation)',
            '$destructor_operation_valid(S, pdestructionoperation)',
            '$destructor_release_valid(S, pdestructionrelease)', *ADMISSION, *ZERO,
        ],
    },
    'live-request-string-remains-unsupported-before-warning': {
        'source': SOURCES['iterator-call-unpack-interned-ref-request-reference-control'],
        'stage': 'S.TODO = (ITERATOR_UNPACK piteratorunpack "send") :: ptask_tail*',
        'checks': [
            *HEADER, 'S.STORE[n_source] = DEFINED pvalue_current',
            'pvalue_current = PSTRING_CARRIER (REQUEST_STRING n_string) ($ptascii("old3"))',
            '$string_carrier_valid(S, pvalue_current)', *ADMISSION, *ZERO,
            'S_one = $drive_steps(S, 1)',
            'S_one.COMPLETION = UNSUPPORTED "Iterator unpack by-reference raw payload"',
            'S_one.TODO = eps', 'S_one.STORE = S.STORE', 'S_one.REFCELLS = S.REFCELLS',
            'S_one.EVENTS = S.EVENTS',
        ],
    },
    'post-handler-request-and-plain-string-tags-stop-before-fresh-cell': {
        'source': SOURCES['iterator-call-unpack-interned-ref-key-handler-literals'],
        'stage': BYREF,
        'checks': [
            *HEADER, *HANDLER, *ADMISSION,
            'S_alloc = $string_request(S, $ptascii("handler"))',
            'S_alloc.RESULT = KNOWN pvalue_request', '$string_carrier_valid(S_alloc, pvalue_request)',
            'S_bad = S_alloc[.STORE[n_source] = DEFINED pvalue_request][.RESULT = KNOWN PNULL]',
            '$heap_graph(S_bad) = $heap_graph(S)',
            '$iterator_unpack_result_valid(S_bad, piteratorunpack, "byref")',
            '$call_descriptors_valid(S_bad)', 'S_bad_one = $drive_steps(S_bad, 1)',
            'S_bad_one.COMPLETION = UNSUPPORTED "Iterator unpack by-reference raw payload"',
            'S_bad_one.TODO = eps', 'S_bad_one.STORE = S_bad.STORE',
            'S_bad_one.REFCELLS = S.REFCELLS', 'S_bad_one.EVENTS = S.EVENTS',
            'S_plain = S[.STORE[n_source] = DEFINED (PSTRING ($ptascii("handler")))]',
            '$heap_graph(S_plain) = $heap_graph(S)', '$call_descriptors_valid(S_plain)',
            'S_plain_one = $drive_steps(S_plain, 1)',
            'S_plain_one.COMPLETION = UNSUPPORTED "Iterator unpack by-reference raw payload"',
            'S_plain_one.TODO = eps', 'S_plain_one.STORE = S_plain.STORE',
            'S_plain_one.REFCELLS = S.REFCELLS', 'S_plain_one.EVENTS = S.EVENTS',
        ],
    },
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    assert not args.case or set(args.case) <= CASES.keys(), 'unknown Iterator interned reference review case'
    review.ROOT = ROOT
    review.CASES = CASES
    passed = review.run(args.case)
    assert all(p.read_bytes() == data for p, data in INPUT_BYTES.items()), \
        'Iterator interned reference review inputs changed during run'
    raise SystemExit(0 if passed else 1)
