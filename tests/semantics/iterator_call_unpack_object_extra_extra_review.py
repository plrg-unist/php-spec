#!/usr/bin/env python3
"""Reached copied-object warnings after an earlier private extra-name cell."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import fiber_state_review as review

CATALOG = Path(__file__).with_name('iterator_call_unpack_object_extra_extra_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
SOURCES = {r['id']: r['source'] for r in json.loads(INPUT_BYTES[CATALOG])}
ADMISSION = ['$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
POST = ['$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))']
ZERO = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S']
ONE = ['S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
       'S_one = S_one_budget[.COMPLETION = NORMAL]']
PRIOR = '{SLOTS eps, NAMED ([($ptascii("zeta"), REFERENCE n_private_earlier)])}'
SENT = '{SLOTS eps, NAMED ([($ptascii("zeta"), REFERENCE n_private_earlier), '
SENT += '($ptascii("alpha"), REFERENCE n_private_current)])}'
BASE = ['n_data = piteratorunpack.OBJECT', 'n_cursor = piteratorunpack.ITERATOR',
        'piteratorunpack.CURRENT = KNOWN (POBJECT n_current)',
        'piteratorunpack.INPUT = KNOWN (POBJECT n_data)',
        'piteratorunpack.CALL.SENT = ' + PRIOR,
        'S.STORE[n_private_earlier] = DEFINED (POBJECT n_earlier)',
        'n_earlier =/= n_current', 'n_earlier =/= n_data', 'n_current =/= n_data',
        'piteratorunpack.KEY = KNOWN pvalue_key',
        '$fiber_traversal_key(pvalue_key) = (KSTRING ($ptascii("alpha")))',
        'piteratorunpack.NAMED',
        '$iterator_unpack_named_target(S, piteratorunpack) = NAMED_EXTRA ($ptascii("alpha"))']
SOURCES_NULL = ['$lookup(S.ENV, $ptascii("earlier")) = (n_source_earlier)',
                '$lookup(S.ENV, $ptascii("current")) = (n_source_current)',
                'S.STORE[n_source_earlier] = DEFINED PNULL',
                'S.STORE[n_source_current] = DEFINED PNULL',
                'n_private_earlier =/= n_source_earlier',
                'n_private_earlier =/= n_source_current']
HELD = ['piteratorunpack.HOLD = piteratorunpack.CURRENT',
        '$iterator_unpack_hold_valid(piteratorunpack, "byref")',
        '$iterator_unpack_hold_allowed(S, piteratorunpack, "byref")',
        '$heap_owners($heap_graph(S), HCELL n_private_earlier) = 1',
        '$heap_owners($heap_graph(S), HOBJECT n_earlier) = 1',
        '$heap_owners($heap_graph(S), HOBJECT n_current) = 2']
ACTIVE = ['$useriter_cursor_valid(S, n_cursor, n_data)',
          'S.ORIGIN = $unpack_origin(S, piteratorunpack.CALL)',
          '$useriter_tasks_ids(S.TODO) = [n_cursor]']
ABORT_STAGE = ('S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
               '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail* '
               '-- if pdestructionoperation.PENDING = (n_error) '
               '-- if pdestructionoperation.SOURCE = ITERATOR_UNPACK piteratorunpack "byref"')
ABORT_METADATA = [
    'S_scope = S[.CURRENT = pdestructionoperation.CALLER]'
    '[.ORIGIN = pdestructionoperation.ORIGIN]'
    '[.CONSTCONTEXT = pdestructionoperation.CONSTCONTEXT]',
    '$iterator_unpack_hold_allowed(S_scope, piteratorunpack, "byref")',
    '$eager_operation_source_valid(S, pdestructionoperation)',
    '$destructor_operation_valid(S, pdestructionoperation)',
    '$destructor_release_valid(S, pdestructionrelease)',
    '$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = [HOBJECT n_error]',
    '$throwable_live(S, n_error)', '$throwable_field(S, n_error, "code") = PINT 51',
]
def source(ending):
    return SOURCES['iterator-call-unpack-object-extra-extra-' + ending]


def abort_checks():
    return [*BASE, *HELD, *ABORT_METADATA,
            '$iterator_lookup(S.ITERATORS, n_cursor) = eps',
            '$heap_owners($heap_graph(S), HOBJECT n_data) = 2',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_current), '
            'DESTRUCTION_VALUE (HOBJECT n_data), DESTRUCTION_VALUE (HOBJECT n_data), '
            'DESTRUCTION_VALUE (HCELL n_private_earlier), DESTRUCTION_VALUE (HOBJECT n_current)]',
            '$iterator_unpack_discard_nodes(S_scope, piteratorunpack) = '
            '[HOBJECT n_current, HOBJECT n_data, HOBJECT n_data, '
            'HCELL n_private_earlier, HOBJECT n_current]', *ADMISSION, *ZERO]


CASES = {
    'second-extra-warning-holds-current-beside-earlier-private-cell': {
        'source': source('normal'),
        'stage': ('S.TODO = (ITERATOR_UNPACK piteratorunpack "send") :: ptask_tail* '
                  '-- if piteratorunpack.CALL.SENT.NAMED = '
                  '[($ptascii("zeta"), REFERENCE n_private_earlier)]'),
        'checks': [
            *BASE, *ACTIVE, 'piteratorunpack.HOLD = KNOWN PNULL',
            '$lookup(S.ENV, $ptascii("earlier")) = (n_source_earlier)',
            '$lookup(S.ENV, $ptascii("current")) = (n_source_current)',
            'S.STORE[n_source_earlier] = DEFINED PNULL',
            'S.STORE[n_source_current] = DEFINED (POBJECT n_current)',
            'n_private_earlier =/= n_source_earlier',
            'n_private_earlier =/= n_source_current',
            '$heap_owners($heap_graph(S), HCELL n_private_earlier) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_earlier) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_current) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_data) = 2',
            '$iterator_unpack_warning_hold(S, piteratorunpack) = (piteratorunpack.CURRENT)',
            *ADMISSION, *ZERO, *ONE,
            'S_one.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
            'perrorcall.RESUME = ITERATOR_UNPACK piteratorunpack_held "byref"',
            'piteratorunpack_held = piteratorunpack[.HOLD = piteratorunpack.CURRENT]',
            'perrorcall.LEVEL = 2', 'perrorcall.LINE = 29',
            'perrorcall.MESSAGE = $ptascii("Cannot pass by-reference argument 1 of '
            'ExtraExtraTarget24() by unpacking a Traversable, passing by-value instead")',
            '$error_call_valid(S_one, perrorcall)',
            '$heap_owners($heap_graph(S_one), HOBJECT n_current) = 3',
            '$heap_owners($heap_graph(S_one), HCELL n_private_earlier) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_earlier) = 1',
            'S_one.STORE = S.STORE', 'S_one.EVENTS = S.EVENTS', *POST,
        ],
    },
    'second-extra-resume-appends-distinct-private-cell-and-retires-raw': {
        'source': source('normal'),
        'stage': ('S.TODO = (ITERATOR_UNPACK piteratorunpack "byref") :: ptask_tail* '
                  '-- if piteratorunpack.CALL.SENT.NAMED = '
                  '[($ptascii("zeta"), REFERENCE n_private_earlier)]'),
        'checks': [
            *BASE, *ACTIVE, *SOURCES_NULL, *HELD, *ADMISSION, *ZERO,
            'n_private_current = |S.STORE|', *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(ITERATOR_UNPACK piteratorunpack_next "next-start") :: ptask_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_current)]',
            'piteratorunpack_next.CURRENT = KNOWN PNULL',
            'piteratorunpack_next.KEY = KNOWN PNULL',
            'piteratorunpack_next.HOLD = KNOWN PNULL',
            'piteratorunpack_next.CALL.SENT = ' + SENT,
            'S_one.STORE[n_private_current] = DEFINED (POBJECT n_current)',
            'n_private_current <- S_one.REFCELLS',
            'n_private_current =/= n_private_earlier',
            'n_private_current =/= n_source_earlier',
            'n_private_current =/= n_source_current',
            '$heap_owners($heap_graph(S_one), HCELL n_private_current) = 1',
            '$heap_owners($heap_graph(S_one), HCELL n_private_earlier) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_current) = 2',
            '$heap_owners($heap_graph(S_one), HOBJECT n_earlier) = 1', *POST,
            'S_two_budget = $drive_steps(S_one, 1)', 'S_two_budget.COMPLETION = BUDGET',
            'S_two = S_two_budget[.COMPLETION = NORMAL]',
            '$heap_owners($heap_graph(S_two), HOBJECT n_current) = 1',
            '$heap_owners($heap_graph(S_two), HOBJECT n_earlier) = 1',
            'S_two.EVENTS = S.EVENTS', '$call_descriptors_valid(S_two)',
            '$heap_valid($heap_graph(S_two))',
            'piteratorunpack_bad = piteratorunpack[.CALL = piteratorunpack.CALL[.SENT = '
            '{SLOTS eps, NAMED ([($ptascii("alpha"), REFERENCE n_private_earlier)])}]]',
            'S_bad = S[.TODO = (ITERATOR_UNPACK piteratorunpack_bad "byref") :: ptask_tail*]',
            '$heap_graph(S_bad) = $heap_graph(S)',
            '$iterator_unpack_hold_valid(piteratorunpack_bad, "byref")',
            '~$iterator_unpack_hold_allowed(S, piteratorunpack_bad, "byref")',
            '~$call_descriptors_valid(S_bad)',
        ],
    },
    'second-extra-throw-orders-cache-data-input-earlier-cell-current-hold': {
        'source': source('second-warning-throw'), 'stage': ABORT_STAGE,
        'checks': [*abort_checks(), *SOURCES_NULL, *ONE,
                   '$heap_owners($heap_graph(S_one), HOBJECT n_current) = 1',
                   '$heap_owners($heap_graph(S_one), HCELL n_private_earlier) = 1',
                   '$heap_owners($heap_graph(S_one), HOBJECT n_earlier) = 1',
                   'S_one.EVENTS = S.EVENTS', *POST],
    },
    'retired-extra-receipt-keeps-dead-cell-documentary-and-rejects-occupied-key': {
        'source': source('second-warning-throw'),
        'stage': (ABORT_STAGE + ' -- if pdestructionrelease.JOBS = eps '
                  '-- if piteratorunpack.CURRENT = KNOWN (POBJECT n_current) '
                  '-- if piteratorunpack.CALL.SENT = ' + PRIOR + ' '
                  '-- if S.STORE[n_private_earlier] = DEFINED (POBJECT n_earlier) '
                  '-- if n_current <- S.DESTRUCTION.CALLED '
                  '-- if n_earlier <- S.DESTRUCTION.CALLED'),
        'checks': [
            *BASE, 'piteratorunpack.HOLD = piteratorunpack.CURRENT',
            '$heap_owners($heap_graph(S), HCELL n_private_earlier) = 0',
            '$heap_owners($heap_graph(S), HOBJECT n_earlier) = 0',
            '$heap_owners($heap_graph(S), HOBJECT n_current) = 0',
            '~((HCELL n_private_earlier) <- S.ALLOCATIONS)',
            '~((HOBJECT n_earlier) <- S.ALLOCATIONS)',
            '~((HOBJECT n_current) <- S.ALLOCATIONS)',
            *ABORT_METADATA, *ADMISSION, *ZERO,
            'S.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail*',
            'piteratorunpack_bad = piteratorunpack[.CALL = piteratorunpack.CALL[.SENT = '
            '{SLOTS eps, NAMED ([($ptascii("alpha"), REFERENCE n_private_earlier)])}]]',
            'pdestructionoperation_bad = pdestructionoperation[.SOURCE = '
            'ITERATOR_UNPACK piteratorunpack_bad "byref"]',
            'S_bad = S[.DESTRUCTION.OPERATIONS = pdestructionoperation_bad :: '
            'pdestructionoperation_tail*][.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation_bad) :: ptask_tail*]',
            '$heap_graph(S_bad) = $heap_graph(S)',
            '$iterator_unpack_hold_valid(piteratorunpack_bad, "byref")',
            '~$iterator_unpack_hold_allowed(S_scope, piteratorunpack_bad, "byref")',
            '~$eager_operation_source_valid(S_bad, pdestructionoperation_bad)',
            '~$destructor_operation_valid(S_bad, pdestructionoperation_bad)',
            '~$call_descriptors_valid(S_bad)',
        ],
    },
}

CASES['parked-second-extra-keeps-private-cell-and-rejects-occupied-or-duplicate-resume'] = {
    'source': source('parked-throw'),
    'stage': ('S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_main* '
              '-- if pconfigcall.KIND = INTRINSIC_FIBER_THROW '
              '-- if pconfigcall.OWNER = (n_fiber) '
              '-- if $fiber_at(S, n_fiber) = (pfiber) -- if pfiber.VM = (pfibervm) '
              '-- if pfibervm.FRAMES = [pframe_unpack, pframe_base] '
              '-- if pframe_unpack.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_unpack* '
              '-- if perrorcall.RESUME = ITERATOR_UNPACK piteratorunpack "byref"'),
    'checks': [
        *BASE, 'piteratorunpack.HOLD = piteratorunpack.CURRENT',
        '$heap_owners($heap_graph(S), HCELL n_private_earlier) = 1',
        '$heap_owners($heap_graph(S), HOBJECT n_earlier) = 1',
        '$heap_owners($heap_graph(S), HOBJECT n_current) = 2',
        '$heap_owners($heap_graph(S), HOBJECT n_data) = 2',
        '$lookup(S.ENV, $ptascii("earlier")) = (n_source_earlier)',
        '$lookup(S.ENV, $ptascii("current")) = (n_source_current)',
        '$lookup(pfibervm.TABLE.ENV, $ptascii("earlier")) = (n_source_earlier)',
        '$lookup(pfibervm.TABLE.ENV, $ptascii("current")) = (n_source_current)',
        'S.STORE[n_source_earlier] = DEFINED (PINT 17)',
        'S.STORE[n_source_current] = DEFINED (PINT 19)',
        '$heap_owners($heap_graph(S), HCELL n_source_earlier) = 2',
        '$heap_owners($heap_graph(S), HCELL n_source_current) = 2',
        'S_view = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)]'
        '[.FIBERCALLERS = eps][.COMPLETION = NORMAL]',
        'S_scope = $constant_frame_scope(S_view, pframe_unpack, [pframe_base])',
        '$iterator_unpack_result_valid(S_scope, piteratorunpack, "byref")',
        '$error_entered_call_valid(S_scope, perrorcall)',
        '$fiber_vm_valid(S, pfibervm, (n_fiber), eps)', 'perrorcall.LINE = 31',
        *ADMISSION, *ZERO,
        'piteratorunpack_bad = piteratorunpack[.CALL = piteratorunpack.CALL[.SENT = '
        '{SLOTS eps, NAMED ([($ptascii("alpha"), REFERENCE n_private_earlier)])}]]',
        'perrorcall_bad = perrorcall[.RESUME = ITERATOR_UNPACK piteratorunpack_bad "byref"]',
        'pframe_bad = pframe_unpack[.TODO = (ERROR_HANDLER_RESULT perrorcall_bad) :: ptask_unpack*]',
        'pfibervm_bad = pfibervm[.FRAMES = [pframe_bad, pframe_base]]',
        'S_bad = $fiber_put(S, n_fiber, pfiber[.VM = (pfibervm_bad)])',
        '$heap_graph(S_bad) = $heap_graph(S)',
        '~$iterator_unpack_hold_allowed(S_scope, piteratorunpack_bad, "byref")',
        '~$fiber_vm_valid(S_bad, pfibervm_bad, (n_fiber), eps)',
        '~$call_descriptors_valid(S_bad)',
        'pframe_duplicate = pframe_unpack[.TODO = (ERROR_HANDLER_RESULT perrorcall) :: '
        '(ERROR_HANDLER_RESULT perrorcall) :: ptask_unpack*]',
        'pfibervm_duplicate = pfibervm[.FRAMES = [pframe_duplicate, pframe_base]]',
        'S_duplicate = $fiber_put(S, n_fiber, pfiber[.VM = (pfibervm_duplicate)])',
        '$heap_valid($heap_graph(S_duplicate))',
        '$heap_owners($heap_graph(S_duplicate), HCELL n_private_earlier) = 2',
        '$heap_owners($heap_graph(S_duplicate), HOBJECT n_earlier) = 1',
        '$heap_owners($heap_graph(S_duplicate), HOBJECT n_current) = 4',
        '$heap_owners($heap_graph(S_duplicate), HOBJECT n_data) = 4',
        '~$fiber_vm_valid(S_duplicate, pfibervm_duplicate, (n_fiber), eps)',
        '~$call_descriptors_valid(S_duplicate)',
    ],
}
CASES['injected-second-extra-throw-retires-earlier-private-cell-before-current'] = {
    'source': source('parked-throw'), 'stage': ABORT_STAGE,
    'checks': [*abort_checks(), 'S.ACTIVEFIBER = (n_fiber)',
               '$unpack_line(S, piteratorunpack.CALL) = 31'],
}

REST = ['pcallcontext.NAMED = [($ptascii("zeta"), REFERENCE n_private_earlier), '
        '($ptascii("alpha"), REFERENCE n_private_current)]',
        'S.STORE[n_private_earlier] = DEFINED (POBJECT n_earlier)',
        'S.STORE[n_private_current] = DEFINED (POBJECT n_current)',
        'n_private_earlier =/= n_private_current', 'n_earlier =/= n_current',
        '$lookup(S.ENV, $ptascii("rest")) = (n_rest)',
        'S.STORE[n_rest] = DEFINED (PARRAY n_rest_array)',
        '$heap_owners($heap_graph(S), HCELL n_private_earlier) = 1',
        '$heap_owners($heap_graph(S), HCELL n_private_current) = 1']
CASES['both-extra-private-cells-collect-direct-items-in-insertion-order'] = {
    'source': source('normal'),
    'stage': ('S.TODO = [NAMED_VARIADIC_RECEIVE porigin 2] '
              '-- if S.CURRENT = (pcallcontext) '
              '-- if pcallcontext.NAME = $ptascii("ExtraExtraTarget24")'),
    'checks': [
        '$receiving_function(S, porigin) = (pfunction)',
        'pfunction.ORIGIN = pcallcontext.FUNCTION', 'pcallcontext.TARGET = porigin',
        'pcallcontext.EXTRA = eps', *REST,
        'S.ARRAYS[n_rest_array].ITEMS = '
        '[ENTRY (KSTRING ($ptascii("zeta"))) (DIRECT (POBJECT n_earlier)), '
        'ENTRY (KSTRING ($ptascii("alpha"))) (DIRECT (POBJECT n_current))]',
        '$heap_owners($heap_graph(S), HARRAY n_rest_array) = 1',
        '$heap_owners($heap_graph(S), HOBJECT n_earlier) = 2',
        '$heap_owners($heap_graph(S), HOBJECT n_current) = 2',
        '$named_variadic_private(S, pfunction, 0, REFERENCE n_private_earlier, POBJECT n_earlier)',
        '$named_variadic_private(S, pfunction, 1, REFERENCE n_private_current, POBJECT n_current)',
        '$call_task_valid(S, NAMED_VARIADIC_RECEIVE porigin 2)', *ADMISSION, *ZERO, *ONE,
        'S_one.TODO = $function_tasks(S_one, pfunction)',
        'S_one.STORE = S.STORE', 'S_one.ARRAYS = S.ARRAYS',
        'S_one.CURRENT = S.CURRENT', 'S_one.EVENTS = S.EVENTS', *POST,
    ],
}
CASES['body-clears-current-rest-item-with-both-original-cells-retained'] = {
    'source': source('normal'),
    'stage': ('S.CURRENT = (pcallcontext) '
              '-- if pcallcontext.NAME = $ptascii("ExtraExtraTarget24") '
              '-- if S.TODO = (EMIT z_emit) :: ptask_tail* '
              '-- if S.RESULT = KNOWN pvalue_text '
              '-- if $string_bytes(pvalue_text) = ($ptascii("F|"))'),
    'checks': [
        *REST, 'S.ARRAYS[n_rest_array].ITEMS = '
        '[ENTRY (KSTRING ($ptascii("zeta"))) (DIRECT (POBJECT n_earlier)), '
        'ENTRY (KSTRING ($ptascii("alpha"))) (DIRECT PNULL)]',
        '$heap_owners($heap_graph(S), HOBJECT n_earlier) = 2',
        '$heap_owners($heap_graph(S), HOBJECT n_current) = 1',
        '~(n_earlier <- S.DESTRUCTION.CALLED)', '~(n_current <- S.DESTRUCTION.CALLED)',
        *ADMISSION, *ZERO, *ONE,
        'S_one.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("F|")]',
        'S_one.STORE = S.STORE', 'S_one.CURRENT = S.CURRENT', *POST,
        'S_done = $drive(S, 4000)', 'S_done.COMPLETION = NORMAL',
        'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("F|"), '
        'OUTPUT $ptascii("A|"), OUTPUT $ptascii("B|"), OUTPUT $ptascii("E")]',
        'n_earlier <- S_done.DESTRUCTION.CALLED', 'n_current <- S_done.DESTRUCTION.CALLED',
        '$heap_owners($heap_graph(S_done), HCELL n_private_earlier) = 0',
        '$heap_owners($heap_graph(S_done), HCELL n_private_current) = 0',
        '$heap_owners($heap_graph(S_done), HOBJECT n_earlier) = 0',
        '$heap_owners($heap_graph(S_done), HOBJECT n_current) = 0',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ],
}


def run(selected):
    review.CASES = CASES
    passed = review.run(selected)
    assert INPUT_BYTES == {p: p.read_bytes() for p in INPUT_BYTES}, 'extra-extra review inputs changed'
    return passed


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if run(args.case) else 1)
