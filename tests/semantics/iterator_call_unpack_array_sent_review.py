#!/usr/bin/env python3
"""Reached array holds after fixed sends and mapped child destruction."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import fiber_state_review as review

CATALOG = Path(__file__).with_name('iterator_call_unpack_array_sent_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
SOURCES = {r['id']: r['source'] for r in json.loads(INPUT_BYTES[CATALOG])}
ADMISSION = ['$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
POST = ['$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))']
ZERO = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S']
ONE = ['S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
       'S_one = S_one_budget[.COMPLETION = NORMAL]']
EARLIER = 'NAMED_SENT (KNOWN (PARRAY n_earlier_array))'
SLOTS = {'positional': '[' + EARLIER + ']',
         'reversed-named': '[NAMED_HOLE, ' + EARLIER + ']'}
FIRST = {'positional': 'earlier', 'reversed-named': 'current'}
SECOND = {'positional': 'current', 'reversed-named': 'earlier'}
BASE = ['n_data = piteratorunpack.OBJECT', 'n_cursor = piteratorunpack.ITERATOR',
        'piteratorunpack.CURRENT = KNOWN (PARRAY n_current_array)',
        'piteratorunpack.INPUT = KNOWN (POBJECT n_data)',
        '$named_slots_roots(piteratorunpack.CALL.SENT.SLOTS) = [HARRAY n_earlier_array]',
        'piteratorunpack.CALL.SENT.NAMED = eps', 'n_current_array =/= n_earlier_array',
        'S.ARRAYS[n_earlier_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_earlier_child))]',
        'S.ARRAYS[n_current_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_current_child))]',
        'n_earlier_child =/= n_current_child', 'n_earlier_child =/= n_data',
        'n_current_child =/= n_data']
CHILDREN = ['$node_children(S, HARRAY n_earlier_array) = [HOBJECT n_earlier_child]',
            '$node_children(S, HARRAY n_current_array) = [HOBJECT n_current_child]',
            '$heap_owners($heap_graph(S), HOBJECT n_earlier_child) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_current_child) = 1',
            '~(n_earlier_child <- S.DESTRUCTION.CALLED)',
            '~(n_current_child <- S.DESTRUCTION.CALLED)']
NULL_SOURCES = ['$lookup(S.ENV, $ptascii("earlier")) = (n_cell_earlier)',
                '$lookup(S.ENV, $ptascii("current")) = (n_cell_current)',
                'n_cell_earlier =/= n_cell_current',
                'S.STORE[n_cell_earlier] = DEFINED PNULL',
                'S.STORE[n_cell_current] = DEFINED PNULL']
HELD = ['piteratorunpack.HOLD = piteratorunpack.CURRENT',
        '$iterator_unpack_hold_valid(piteratorunpack, "byref")',
        '$heap_owners($heap_graph(S), HARRAY n_current_array) = 2',
        '$heap_owners($heap_graph(S), HARRAY n_earlier_array) = 1']
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
    '$throwable_live(S, n_error)', '$throwable_field(S, n_error, "code") = PINT 51']


def source(mode, ending):
    return SOURCES['iterator-call-unpack-array-sent-' + mode + '-' + ending]


def array_job(which):
    return 'DESTRUCTION_VALUE (HARRAY n_' + which + '_array)'


def child_job(which):
    return 'DESTRUCTION_VALUE (HOBJECT n_' + which + '_child)'


def slots(mode):
    result = ['piteratorunpack.CALL.SENT.SLOTS = ' + SLOTS[mode]]
    if mode == 'positional':
        result += ['piteratorunpack.KEY = KNOWN (PINT 1)', '~piteratorunpack.NAMED',
                   '$iterator_unpack_named_target(S, piteratorunpack) = NAMED_POSITION 1']
    else:
        result += ['piteratorunpack.KEY = KNOWN pvalue_key',
                   '$fiber_traversal_key(pvalue_key) = (KSTRING ($ptascii("first")))',
                   'piteratorunpack.NAMED',
                   '$iterator_unpack_named_target(S, piteratorunpack) = NAMED_POSITION 0']
    return result


def abort(mode):
    ordered = [array_job('current'), 'DESTRUCTION_VALUE (HOBJECT n_data)',
               'DESTRUCTION_VALUE (HOBJECT n_data)',
               array_job(FIRST[mode]), array_job(SECOND[mode])]
    return [*BASE, *slots(mode), *HELD, *CHILDREN, *ABORT_METADATA,
            '$iterator_lookup(S.ITERATORS, n_cursor) = eps',
            '$heap_owners($heap_graph(S), HOBJECT n_data) = 2',
            'pdestructionrelease.JOBS = [' + ', '.join(ordered) + ']',
            '$iterator_unpack_discard_nodes(S_scope, piteratorunpack) = '
            '[HARRAY n_current_array, HOBJECT n_data, HOBJECT n_data, '
            'HARRAY n_' + FIRST[mode] + '_array, HARRAY n_' + SECOND[mode] + '_array]',
            *ADMISSION, *ZERO]


CASES = {
    'later-array-warning-adds-container-owner-with-child-edge-once': {
        'source': source('positional', 'normal'),
        'stage': ('S.TODO = (ITERATOR_UNPACK piteratorunpack "send") :: ptask_tail* '
                  '-- if piteratorunpack.CALL.SENT.SLOTS =/= eps'),
        'checks': [
            *BASE, *slots('positional'), *ACTIVE, *CHILDREN,
            'piteratorunpack.HOLD = KNOWN PNULL',
            '$lookup(S.ENV, $ptascii("earlier")) = (n_cell_earlier)',
            '$lookup(S.ENV, $ptascii("current")) = (n_cell_current)',
            'S.STORE[n_cell_earlier] = DEFINED (PARRAY n_earlier_array)',
            'S.STORE[n_cell_current] = DEFINED (PARRAY n_current_array)',
            '$heap_owners($heap_graph(S), HARRAY n_earlier_array) = 2',
            '$heap_owners($heap_graph(S), HARRAY n_current_array) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_data) = 2',
            '$iterator_unpack_warning_hold(S, piteratorunpack) = (piteratorunpack.CURRENT)',
            *ADMISSION, *ZERO, *ONE,
            'S_one.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
            'perrorcall.RESUME = ITERATOR_UNPACK piteratorunpack_held "byref"',
            'piteratorunpack_held = piteratorunpack[.HOLD = piteratorunpack.CURRENT]',
            'perrorcall.LEVEL = 2', 'perrorcall.LINE = 24',
            'perrorcall.MESSAGE = $ptascii("Cannot pass by-reference argument 2 of '
            'ArraySentTarget29() by unpacking a Traversable, passing by-value instead")',
            '$error_call_valid(S_one, perrorcall)',
            '$heap_owners($heap_graph(S_one), HARRAY n_current_array) = 3',
            '$heap_owners($heap_graph(S_one), HARRAY n_earlier_array) = 2',
            '$heap_owners($heap_graph(S_one), HOBJECT n_earlier_child) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_current_child) = 1',
            'S_one.STORE = S.STORE', 'S_one.ARRAYS = S.ARRAYS',
            'S_one.EVENTS = S.EVENTS', *POST,
        ],
    },
}

for mode in SLOTS:
    fresh = 'NAMED_SENT (REFERENCE n_private)'
    sent = '[' + ', '.join([EARLIER, fresh] if mode == 'positional' else [fresh, EARLIER]) + ']'
    CASES[mode + '-resume-transfers-array-hold-into-vacant-fixed-cell'] = {
        'source': source(mode, 'normal'),
        'stage': 'S.TODO = (ITERATOR_UNPACK piteratorunpack "byref") :: ptask_tail*',
        'checks': [
            *BASE, *slots(mode), *ACTIVE, *NULL_SOURCES, *HELD, *CHILDREN,
            '$iterator_unpack_hold_allowed(S, piteratorunpack, "byref")',
            '$heap_owners($heap_graph(S), HOBJECT n_data) = 2', *ADMISSION, *ZERO,
            'n_private = |S.STORE|', *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(ITERATOR_UNPACK piteratorunpack_next "next-start") :: ptask_tail*',
            'pdestructionrelease.JOBS = [' + array_job('current') + ']',
            'piteratorunpack_next.CURRENT = KNOWN PNULL',
            'piteratorunpack_next.KEY = KNOWN PNULL',
            'piteratorunpack_next.HOLD = KNOWN PNULL',
            'piteratorunpack_next.NAMED = ' + ('false' if mode == 'positional' else 'true'),
            'piteratorunpack_next.CALL.SENT.SLOTS = ' + sent,
            'piteratorunpack_next.CALL.SENT.NAMED = eps',
            'S_one.STORE[n_private] = DEFINED (PARRAY n_current_array)',
            'n_private <- S_one.REFCELLS', 'n_private =/= n_cell_current',
            'n_private =/= n_cell_earlier',
            '$heap_owners($heap_graph(S_one), HCELL n_private) = 1',
            '$node_children(S_one, HCELL n_private) = [HARRAY n_current_array]',
            '$heap_owners($heap_graph(S_one), HARRAY n_current_array) = 2',
            '$heap_owners($heap_graph(S_one), HARRAY n_earlier_array) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_current_child) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_earlier_child) = 1',
            'S_one.STORE[n_cell_current] = DEFINED PNULL', *POST,
            'S_two_budget = $drive_steps(S_one, 1)', 'S_two_budget.COMPLETION = BUDGET',
            'S_two = S_two_budget[.COMPLETION = NORMAL]',
            'S_two.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_done) :: '
            '(ITERATOR_UNPACK piteratorunpack_next "next-start") :: ptask_tail*',
            'pdestructionrelease_done.JOBS = eps',
            '$heap_owners($heap_graph(S_two), HARRAY n_current_array) = 1',
            '$heap_owners($heap_graph(S_two), HARRAY n_earlier_array) = 1',
            '$heap_owners($heap_graph(S_two), HOBJECT n_current_child) = 1',
            '$heap_owners($heap_graph(S_two), HOBJECT n_earlier_child) = 1',
            'S_two.EVENTS = S.EVENTS',
            '$call_descriptors_valid(S_two)', '$heap_valid($heap_graph(S_two))',
        ],
    }
    CASES[mode + '-throw-maps-array-hold-after-raw-data-and-input'] = {
        'source': source(mode, 'throw'), 'stage': ABORT_STAGE,
        'checks': [*abort(mode), *NULL_SOURCES, *ONE,
                   '$heap_owners($heap_graph(S_one), HARRAY n_current_array) = 1',
                   '$heap_owners($heap_graph(S_one), HARRAY n_earlier_array) = 1',
                   '$heap_owners($heap_graph(S_one), HOBJECT n_current_child) = 1',
                   '$heap_owners($heap_graph(S_one), HOBJECT n_earlier_child) = 1',
                   '$heap_owners($heap_graph(S_one), HOBJECT n_data) = 2',
                   'S_one.EVENTS = S.EVENTS', *POST],
    }
    first, second = FIRST[mode], SECOND[mode]
    CASES[mode + '-first-container-expands-child-in-fixed-slot-order'] = {
        'source': source(mode, 'throw'),
        'stage': (ABORT_STAGE + ' -- if piteratorunpack.CURRENT = KNOWN (PARRAY n_current_array) '
                  '-- if piteratorunpack.CALL.SENT.SLOTS = ' + SLOTS[mode] +
                  ' -- if pdestructionrelease.JOBS = [' + array_job(first) + ', ' + array_job(second) + ']'),
        'checks': [
            *BASE, *slots(mode), 'piteratorunpack.HOLD = piteratorunpack.CURRENT',
            *CHILDREN, *ABORT_METADATA, '$heap_owners($heap_graph(S), HOBJECT n_data) = 0',
            'n_data <- S.DESTRUCTION.CALLED',
            '$heap_owners($heap_graph(S), HARRAY n_earlier_array) = 1',
            '$heap_owners($heap_graph(S), HARRAY n_current_array) = 1',
            *ADMISSION, *ZERO, *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_next) :: '
            '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*',
            'pdestructionrelease_next.JOBS = [' + child_job(first) + ', ' + array_job(second) + ']',
            '~((HARRAY n_' + first + '_array) <- S_one.ALLOCATIONS)',
            '$heap_owners($heap_graph(S_one), HARRAY n_' + first + '_array) = 0',
            '$heap_owners($heap_graph(S_one), HOBJECT n_' + first + '_child) = 1',
            '$heap_owners($heap_graph(S_one), HARRAY n_' + second + '_array) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_' + second + '_child) = 1',
            'S_one.ARRAYS = S.ARRAYS', 'S_one.EVENTS = S.EVENTS',
            '$eager_operation_source_valid(S_one, pdestructionoperation)', *POST,
            'S_two_budget = $drive_steps(S_one, 1)', 'S_two_budget.COMPLETION = BUDGET',
            'S_two = S_two_budget[.COMPLETION = NORMAL]',
            'S_two.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: '
            '(DESTRUCTOR_RELEASE pdestructionrelease_after) :: '
            '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*',
            'pdestructorcall.OBJECT = n_' + first + '_child',
            'pdestructorcall.PENDING = (n_error)',
            'pdestructionrelease_after.JOBS = [' + array_job(second) + ']',
            'n_' + first + '_child <- S_two.DESTRUCTION.CALLED',
            '~(n_' + second + '_child <- S_two.DESTRUCTION.CALLED)',
            'S_two.EVENTS = S.EVENTS',
            '$call_descriptors_valid(S_two)', '$heap_valid($heap_graph(S_two))',
        ],
    }

CASES['retired-array-receipt-is-nonowning-and-rejects-phase-forgery'] = {
    'source': source('positional', 'throw'),
    'stage': (ABORT_STAGE + ' -- if pdestructionrelease.JOBS = eps '
              '-- if piteratorunpack.CURRENT = KNOWN (PARRAY n_current_array) '
              '-- if piteratorunpack.CALL.SENT.SLOTS = ' + SLOTS['positional']),
    'checks': [
        *BASE, *slots('positional'), 'piteratorunpack.HOLD = piteratorunpack.CURRENT',
        '$heap_owners($heap_graph(S), HARRAY n_current_array) = 0',
        '$heap_owners($heap_graph(S), HARRAY n_earlier_array) = 0',
        '~((HARRAY n_current_array) <- S.ALLOCATIONS)',
        '~((HARRAY n_earlier_array) <- S.ALLOCATIONS)',
        '$heap_owners($heap_graph(S), HOBJECT n_current_child) = 0',
        '$heap_owners($heap_graph(S), HOBJECT n_earlier_child) = 0',
        'n_current_child <- S.DESTRUCTION.CALLED',
        'n_earlier_child <- S.DESTRUCTION.CALLED',
        *ABORT_METADATA, *ADMISSION, *ZERO,
        'S_document = S[.ARRAYS[n_current_array] = $array_empty()]'
        '[.ARRAYS[n_earlier_array] = $array_empty()]',
        '$heap_graph(S_document) = $heap_graph(S)',
        '$eager_operation_source_valid(S_document, pdestructionoperation)',
        '$call_descriptors_valid(S_document)',
        'S.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail*',
        'piteratorunpack_bad = piteratorunpack[.NAMED = true]',
        'pdestructionoperation_bad = pdestructionoperation[.SOURCE = '
        'ITERATOR_UNPACK piteratorunpack_bad "byref"]',
        'S_bad = S[.DESTRUCTION.OPERATIONS = pdestructionoperation_bad :: '
        'pdestructionoperation_tail*][.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
        '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation_bad) :: ptask_tail*]',
        '$heap_graph(S_bad) = $heap_graph(S)',
        '~$iterator_unpack_hold_allowed(S_scope, piteratorunpack_bad, "byref")',
        '~$eager_operation_source_valid(S_bad, pdestructionoperation_bad)',
        '~$call_descriptors_valid(S_bad)',
    ],
}
CASES['parked-named-array-sends-preserve-child-edges-and-vacant-slot'] = {
    'source': source('reversed-named', 'parked-throw'),
    'stage': ('S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_main* '
              '-- if pconfigcall.KIND = INTRINSIC_FIBER_THROW '
              '-- if pconfigcall.OWNER = (n_fiber) '
              '-- if $fiber_at(S, n_fiber) = (pfiber) -- if pfiber.VM = (pfibervm) '
              '-- if pfibervm.FRAMES = [pframe_unpack, pframe_base] '
              '-- if pframe_unpack.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_unpack* '
              '-- if perrorcall.RESUME = ITERATOR_UNPACK piteratorunpack "byref"'),
    'checks': [
        *BASE, *slots('reversed-named'), *HELD, *CHILDREN,
        '$heap_owners($heap_graph(S), HOBJECT n_data) = 2',
        '$lookup(S.ENV, $ptascii("earlier")) = (n_cell_earlier)',
        '$lookup(S.ENV, $ptascii("current")) = (n_cell_current)',
        '$lookup(pfibervm.TABLE.ENV, $ptascii("earlier")) = (n_cell_earlier)',
        '$lookup(pfibervm.TABLE.ENV, $ptascii("current")) = (n_cell_current)',
        'S.STORE[n_cell_earlier] = DEFINED (PINT 17)',
        'S.STORE[n_cell_current] = DEFINED (PINT 19)',
        '$heap_owners($heap_graph(S), HCELL n_cell_earlier) = 2',
        '$heap_owners($heap_graph(S), HCELL n_cell_current) = 2',
        'S_view = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)]'
        '[.FIBERCALLERS = eps][.COMPLETION = NORMAL]',
        'S_scope = $constant_frame_scope(S_view, pframe_unpack, [pframe_base])',
        '$iterator_unpack_result_valid(S_scope, piteratorunpack, "byref")',
        '$iterator_unpack_hold_allowed(S_scope, piteratorunpack, "byref")',
        '$error_entered_call_valid(S_scope, perrorcall)',
        '$useriter_frames_ids(pfibervm.FRAMES) = [n_cursor]',
        '$fiber_vm_valid(S, pfibervm, (n_fiber), eps)',
        'pfibervm.CURRENT = (pcallcontext_saved)',
        'pcallcontext_saved.LINE = 26', 'perrorcall.LINE = 26', *ADMISSION, *ZERO,
        'piteratorunpack_bad = piteratorunpack[.CALL = '
        'piteratorunpack.CALL[.SENT.SLOTS = ([' + EARLIER + ', NAMED_HOLE])]]',
        'perrorcall_bad = perrorcall[.RESUME = ITERATOR_UNPACK piteratorunpack_bad "byref"]',
        'pframe_bad = pframe_unpack[.TODO = (ERROR_HANDLER_RESULT perrorcall_bad) :: ptask_unpack*]',
        'pfibervm_bad = pfibervm[.FRAMES = [pframe_bad, pframe_base]]',
        'S_bad = $fiber_put(S, n_fiber, pfiber[.VM = (pfibervm_bad)])',
        '$heap_graph(S_bad) = $heap_graph(S)',
        '~$iterator_unpack_hold_allowed(S_scope, piteratorunpack_bad, "byref")',
        '~$fiber_vm_valid(S_bad, pfibervm_bad, (n_fiber), eps)',
        '~$call_descriptors_valid(S_bad)',
        'piteratorunpack_line = piteratorunpack[.CALL = piteratorunpack.CALL[.LINE = 27]]',
        'perrorcall_line = perrorcall[.LINE = 27]'
        '[.EVENT = DIAGNOSTIC "Warning" perrorcall.MESSAGE 27]'
        '[.RESUME = ITERATOR_UNPACK piteratorunpack_line "byref"]',
        'pframe_line = pframe_unpack[.TODO = (ERROR_HANDLER_RESULT perrorcall_line) :: ptask_unpack*]',
        'pfibervm_line = pfibervm[.CURRENT = (pcallcontext_saved[.LINE = 27])]'
        '[.FRAMES = [pframe_line, pframe_base]]',
        'S_line = $fiber_put(S, n_fiber, pfiber[.VM = (pfibervm_line)])',
        '$heap_graph(S_line) = $heap_graph(S)',
        '~$fiber_vm_valid(S_line, pfibervm_line, (n_fiber), eps)',
        '~$call_descriptors_valid(S_line)',
        'pframe_duplicate = pframe_unpack[.TODO = (ERROR_HANDLER_RESULT perrorcall) :: '
        '(ERROR_HANDLER_RESULT perrorcall) :: ptask_unpack*]',
        'pfibervm_duplicate = pfibervm[.FRAMES = [pframe_duplicate, pframe_base]]',
        'S_duplicate = $fiber_put(S, n_fiber, pfiber[.VM = (pfibervm_duplicate)])',
        '$heap_valid($heap_graph(S_duplicate))',
        '$heap_owners($heap_graph(S_duplicate), HARRAY n_earlier_array) = 2',
        '$heap_owners($heap_graph(S_duplicate), HARRAY n_current_array) = 4',
        '$heap_owners($heap_graph(S_duplicate), HOBJECT n_earlier_child) = 1',
        '$heap_owners($heap_graph(S_duplicate), HOBJECT n_current_child) = 1',
        '$heap_owners($heap_graph(S_duplicate), HOBJECT n_data) = 4',
        '~$fiber_vm_valid(S_duplicate, pfibervm_duplicate, (n_fiber), eps)',
        '~$call_descriptors_valid(S_duplicate)',
    ],
}
CASES['injected-named-array-throw-keeps-main-scalars-and-mapped-order'] = {
    'source': source('reversed-named', 'parked-throw'), 'stage': ABORT_STAGE,
    'checks': [*abort('reversed-named'), 'S.ACTIVEFIBER = (n_fiber)',
               '$unpack_line(S, piteratorunpack.CALL) = 26',
               'S.GLOBALTABLE = (psymboltable_global)',
               '$lookup(psymboltable_global.ENV, $ptascii("earlier")) = (n_cell_earlier)',
               '$lookup(psymboltable_global.ENV, $ptascii("current")) = (n_cell_current)',
               'S.STORE[n_cell_earlier] = DEFINED (PINT 17)',
               'S.STORE[n_cell_current] = DEFINED (PINT 19)'],
}
CASES['private-current-array-write-destroys-child-before-earlier-body-owner'] = {
    'source': source('positional', 'normal'),
    'stage': ('S.CURRENT = (pcallcontext) '
              '-- if pcallcontext.NAME = $ptascii("ArraySentTarget29") '
              '-- if S.TODO = (EMIT z_emit) :: ptask_tail* '
              '-- if S.RESULT = KNOWN pvalue_text '
              '-- if $string_bytes(pvalue_text) = ($ptascii("F|"))'),
    'checks': [
        '$lookup(S.ENV, $ptascii("first")) = (n_cell_earlier)',
        '$lookup(S.ENV, $ptascii("second")) = (n_private)',
        'n_cell_earlier =/= n_private',
        'S.STORE[n_cell_earlier] = DEFINED (PARRAY n_earlier_array)',
        'S.STORE[n_private] = DEFINED (PARRAY n_current_array)',
        'n_private <- S.REFCELLS', 'n_current_array =/= n_earlier_array',
        'S.ARRAYS[n_current_array].ITEMS = [ENTRY (KINT 0) (DIRECT PNULL)]',
        'S.ARRAYS[n_earlier_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_earlier_child))]',
        '$node_children(S, HARRAY n_current_array) = eps',
        '$heap_owners($heap_graph(S), HCELL n_private) = 1',
        '$heap_owners($heap_graph(S), HARRAY n_current_array) = 1',
        '$heap_owners($heap_graph(S), HARRAY n_earlier_array) = 1',
        '$heap_owners($heap_graph(S), HOBJECT n_earlier_child) = 1',
        'S.DESTRUCTION.CALLED = [n_data, n_current_child]',
        'n_data =/= n_current_child', 'n_earlier_child =/= n_current_child',
        '$object_name(S, n_current_child) = $ptascii("ArraySentCurrent29")',
        '~(n_earlier_child <- S.DESTRUCTION.CALLED)',
        '$heap_owners($heap_graph(S), HOBJECT n_current_child) = 0',
        '~((HOBJECT n_current_child) <- S.ALLOCATIONS)',
        *ADMISSION, *ZERO, *ONE,
        'S_one.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("F|")]',
        'S_one.STORE = S.STORE', 'S_one.ARRAYS = S.ARRAYS', *POST,
        'S_done = $drive(S, 4000)', 'S_done.COMPLETION = NORMAL',
        'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("F|"), OUTPUT $ptascii("A|"), OUTPUT $ptascii("E")]',
        'n_data <- S_done.DESTRUCTION.CALLED',
        'n_current_child <- S_done.DESTRUCTION.CALLED',
        'n_earlier_child <- S_done.DESTRUCTION.CALLED',
        '$heap_owners($heap_graph(S_done), HARRAY n_current_array) = 0',
        '$heap_owners($heap_graph(S_done), HARRAY n_earlier_array) = 0',
        '$heap_owners($heap_graph(S_done), HOBJECT n_current_child) = 0',
        '$heap_owners($heap_graph(S_done), HOBJECT n_earlier_child) = 0',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ],
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
    assert INPUT_BYTES == {p: p.read_bytes() for p in INPUT_BYTES}, 'array sent review inputs changed'
    return passed


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if run(args.case) else 1)
