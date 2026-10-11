#!/usr/bin/env python3
"""Reached copied-object holds after fixed sends and ordered failed slots."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import fiber_state_review as review

CATALOG = Path(__file__).with_name('iterator_call_unpack_object_sent_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
SOURCES = {r['id']: r['source'] for r in json.loads(INPUT_BYTES[CATALOG])}
ADMISSION = ['$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
POST = ['$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))']
ZERO = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S']
ONE = ['S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
       'S_one = S_one_budget[.COMPLETION = NORMAL]']
EARLIER = 'NAMED_SENT (KNOWN (POBJECT n_earlier))'
SLOTS = {'positional': '[' + EARLIER + ']',
         'reversed-named': '[NAMED_HOLE, ' + EARLIER + ']'}
FIRST = {'positional': 'n_earlier', 'reversed-named': 'n_current'}
SECOND = {'positional': 'n_current', 'reversed-named': 'n_earlier'}
BASE = ['n_data = piteratorunpack.OBJECT', 'n_cursor = piteratorunpack.ITERATOR',
        'piteratorunpack.CURRENT = KNOWN (POBJECT n_current)',
        'piteratorunpack.INPUT = KNOWN (POBJECT n_data)',
        '$named_slots_roots(piteratorunpack.CALL.SENT.SLOTS) = [HOBJECT n_earlier]',
        'n_current =/= n_earlier', 'n_current =/= n_data', 'n_earlier =/= n_data',
        'piteratorunpack.CALL.SENT.NAMED = eps']
NULL_SOURCES = ['$lookup(S.ENV, $ptascii("earlier")) = (n_cell_earlier)',
                '$lookup(S.ENV, $ptascii("current")) = (n_cell_current)',
                'n_cell_earlier =/= n_cell_current',
                'S.STORE[n_cell_earlier] = DEFINED PNULL',
                'S.STORE[n_cell_current] = DEFINED PNULL']
HELD = ['piteratorunpack.HOLD = piteratorunpack.CURRENT',
        '$iterator_unpack_hold_valid(piteratorunpack, "byref")',
        '$iterator_unpack_hold_allowed(S, piteratorunpack, "byref")',
        '$iterator_unpack_warning_hold(S, piteratorunpack) = (piteratorunpack.HOLD)',
        '$heap_owners($heap_graph(S), HOBJECT n_current) = 2',
        '$heap_owners($heap_graph(S), HOBJECT n_earlier) = 1']
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


def source(mode, ending):
    return SOURCES['iterator-call-unpack-object-sent-' + mode + '-' + ending]


def job(n):
    return 'DESTRUCTION_VALUE (HOBJECT ' + n + ')'


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
    ordered = [job('n_current'), job('n_data'), job('n_data'),
               job(FIRST[mode]), job(SECOND[mode])]
    return [*BASE, *slots(mode), *HELD, *ABORT_METADATA,
            '$iterator_lookup(S.ITERATORS, n_cursor) = eps',
            '$heap_owners($heap_graph(S), HOBJECT n_data) = 2',
            'pdestructionrelease.JOBS = [' + ', '.join(ordered) + ']',
            '$iterator_unpack_discard_nodes(S_scope, piteratorunpack) = '
            '[HOBJECT n_current, HOBJECT n_data, HOBJECT n_data, '
            'HOBJECT ' + FIRST[mode] + ', HOBJECT ' + SECOND[mode] + ']',
            *ADMISSION, *ZERO]


CASES = {
    'later-positional-warning-adds-one-hold-without-reordering-earlier-send': {
        'source': source('positional', 'normal'),
        'stage': ('S.TODO = (ITERATOR_UNPACK piteratorunpack "send") :: ptask_tail* '
                  '-- if piteratorunpack.CALL.SENT.SLOTS =/= eps'),
        'checks': [
            *BASE, *slots('positional'), *ACTIVE, 'piteratorunpack.HOLD = KNOWN PNULL',
            '$lookup(S.ENV, $ptascii("earlier")) = (n_cell_earlier)',
            '$lookup(S.ENV, $ptascii("current")) = (n_cell_current)',
            'S.STORE[n_cell_earlier] = DEFINED (POBJECT n_earlier)',
            'S.STORE[n_cell_current] = DEFINED (POBJECT n_current)',
            '$heap_owners($heap_graph(S), HOBJECT n_earlier) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_current) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_data) = 2',
            '$iterator_unpack_warning_hold(S, piteratorunpack) = (piteratorunpack.CURRENT)',
            *ADMISSION, *ZERO, *ONE,
            'S_one.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
            'perrorcall.RESUME = ITERATOR_UNPACK piteratorunpack_held "byref"',
            'piteratorunpack_held = piteratorunpack[.HOLD = piteratorunpack.CURRENT]',
            'perrorcall.LEVEL = 2', 'perrorcall.LINE = 24',
            'perrorcall.MESSAGE = $ptascii("Cannot pass by-reference argument 2 of '
            'OrderedSentTarget23() by unpacking a Traversable, passing by-value instead")',
            '$error_call_valid(S_one, perrorcall)',
            '$heap_owners($heap_graph(S_one), HOBJECT n_current) = 3',
            '$heap_owners($heap_graph(S_one), HOBJECT n_earlier) = 2',
            'S_one.STORE = S.STORE', 'S_one.EVENTS = S.EVENTS', *POST,
        ],
    },
}

for mode in SLOTS:
    fresh = 'NAMED_SENT (REFERENCE n_private)'
    sent = '[' + ', '.join([EARLIER, fresh] if mode == 'positional' else [fresh, EARLIER]) + ']'
    CASES[mode + '-resume-transfers-hold-to-vacant-fixed-cell'] = {
        'source': source(mode, 'normal'),
        'stage': 'S.TODO = (ITERATOR_UNPACK piteratorunpack "byref") :: ptask_tail*',
        'checks': [
            *BASE, *slots(mode), *ACTIVE, *NULL_SOURCES, *HELD,
            '$heap_owners($heap_graph(S), HOBJECT n_data) = 2', *ADMISSION, *ZERO,
            'n_private = |S.STORE|', *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(ITERATOR_UNPACK piteratorunpack_next "next-start") :: ptask_tail*',
            'pdestructionrelease.JOBS = [' + job('n_current') + ']',
            'piteratorunpack_next.CURRENT = KNOWN PNULL',
            'piteratorunpack_next.KEY = KNOWN PNULL',
            'piteratorunpack_next.HOLD = KNOWN PNULL',
            'piteratorunpack_next.CALL.SENT.SLOTS = ' + sent,
            'piteratorunpack_next.CALL.SENT.NAMED = eps',
            'S_one.STORE[n_private] = DEFINED (POBJECT n_current)',
            'n_private <- S_one.REFCELLS', 'n_private =/= n_cell_current',
            'n_private =/= n_cell_earlier',
            '$heap_owners($heap_graph(S_one), HCELL n_private) = 1',
            '$node_children(S_one, HCELL n_private) = [HOBJECT n_current]',
            '$heap_owners($heap_graph(S_one), HOBJECT n_current) = 2',
            '$heap_owners($heap_graph(S_one), HOBJECT n_earlier) = 1',
            'S_one.STORE[n_cell_current] = DEFINED PNULL', *POST,
            'S_two_budget = $drive_steps(S_one, 1)', 'S_two_budget.COMPLETION = BUDGET',
            'S_two = S_two_budget[.COMPLETION = NORMAL]',
            'S_two.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_done) :: '
            '(ITERATOR_UNPACK piteratorunpack_next "next-start") :: ptask_tail*',
            'pdestructionrelease_done.JOBS = eps',
            '$heap_owners($heap_graph(S_two), HOBJECT n_current) = 1',
            '$heap_owners($heap_graph(S_two), HOBJECT n_earlier) = 1',
            'S_two.EVENTS = S.EVENTS',
            '$call_descriptors_valid(S_two)', '$heap_valid($heap_graph(S_two))',
        ],
    }
    CASES[mode + '-throw-installs-failed-hold-in-parameter-order'] = {
        'source': source(mode, 'throw'), 'stage': ABORT_STAGE,
        'checks': [*abort(mode), *NULL_SOURCES, *ONE,
                   '$heap_owners($heap_graph(S_one), HOBJECT n_current) = 1',
                   '$heap_owners($heap_graph(S_one), HOBJECT n_earlier) = 1',
                   '$heap_owners($heap_graph(S_one), HOBJECT n_data) = 2',
                   'S_one.EVENTS = S.EVENTS', *POST],
    }
    CASES[mode + '-first-argument-destructor-follows-fixed-slot-order'] = {
        'source': source(mode, 'throw'),
        'stage': (ABORT_STAGE + ' -- if piteratorunpack.CURRENT = KNOWN (POBJECT n_current) '
                  '-- if piteratorunpack.CALL.SENT.SLOTS = ' + SLOTS[mode] +
                  ' -- if pdestructionrelease.JOBS = [' + job(FIRST[mode]) + ', ' + job(SECOND[mode]) + ']'),
        'checks': [
            *BASE, *slots(mode), 'piteratorunpack.HOLD = piteratorunpack.CURRENT',
            *ABORT_METADATA, '$heap_owners($heap_graph(S), HOBJECT n_data) = 0',
            'n_data <- S.DESTRUCTION.CALLED',
            '$heap_owners($heap_graph(S), HOBJECT n_earlier) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_current) = 1',
            '~(n_earlier <- S.DESTRUCTION.CALLED)', '~(n_current <- S.DESTRUCTION.CALLED)',
            *ADMISSION, *ZERO, *ONE,
            'S_one.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: '
            '(DESTRUCTOR_RELEASE pdestructionrelease_next) :: '
            '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*',
            'pdestructorcall.OBJECT = ' + FIRST[mode],
            'pdestructorcall.PENDING = (n_error)',
            'pdestructionrelease_next.JOBS = [' + job(SECOND[mode]) + ']',
            FIRST[mode] + ' <- S_one.DESTRUCTION.CALLED',
            '~(' + SECOND[mode] + ' <- S_one.DESTRUCTION.CALLED)',
            'S_one.EVENTS = S.EVENTS', *POST,
        ],
    }

CASES['retired-positional-receipt-is-nonowning-and-rejects-named-flag-forgery'] = {
    'source': source('positional', 'throw'),
    'stage': (ABORT_STAGE + ' -- if pdestructionrelease.JOBS = eps '
              '-- if piteratorunpack.CURRENT = KNOWN (POBJECT n_current) '
              '-- if piteratorunpack.CALL.SENT.SLOTS = ' + SLOTS['positional'] +
              ' -- if n_current <- S.DESTRUCTION.CALLED -- if n_earlier <- S.DESTRUCTION.CALLED'),
    'checks': [
        *BASE, *slots('positional'), 'piteratorunpack.HOLD = piteratorunpack.CURRENT',
        '$heap_owners($heap_graph(S), HOBJECT n_current) = 0',
        '$heap_owners($heap_graph(S), HOBJECT n_earlier) = 0',
        '~((HOBJECT n_current) <- S.ALLOCATIONS)',
        '~((HOBJECT n_earlier) <- S.ALLOCATIONS)',
        *ABORT_METADATA, *ADMISSION, *ZERO,
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
        '~$destructor_operation_valid(S_bad, pdestructionoperation_bad)',
        '~$call_descriptors_valid(S_bad)',
    ],
}
CASES['parked-named-sends-keep-exact-owners-and-vacant-target-authority'] = {
    'source': source('reversed-named', 'parked-throw'),
    'stage': ('S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_main* '
              '-- if pconfigcall.KIND = INTRINSIC_FIBER_THROW '
              '-- if pconfigcall.OWNER = (n_fiber) '
              '-- if $fiber_at(S, n_fiber) = (pfiber) -- if pfiber.VM = (pfibervm) '
              '-- if pfibervm.FRAMES = [pframe_unpack, pframe_base] '
              '-- if pframe_unpack.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_unpack* '
              '-- if perrorcall.RESUME = ITERATOR_UNPACK piteratorunpack "byref"'),
    'checks': [
        *BASE, *slots('reversed-named'), 'piteratorunpack.HOLD = piteratorunpack.CURRENT',
        '$heap_owners($heap_graph(S), HOBJECT n_earlier) = 1',
        '$heap_owners($heap_graph(S), HOBJECT n_current) = 2',
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
        'perrorcall.LINE = 26', *ADMISSION, *ZERO,
        'piteratorunpack_bad = piteratorunpack[.CALL = '
        'piteratorunpack.CALL[.SENT.SLOTS = [' + EARLIER + ', NAMED_HOLE]]]',
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
        '$heap_owners($heap_graph(S_duplicate), HOBJECT n_earlier) = 2',
        '$heap_owners($heap_graph(S_duplicate), HOBJECT n_current) = 4',
        '$heap_owners($heap_graph(S_duplicate), HOBJECT n_data) = 4',
        '~$fiber_vm_valid(S_duplicate, pfibervm_duplicate, (n_fiber), eps)',
        '~$call_descriptors_valid(S_duplicate)',
    ],
}
CASES['injected-named-fiber-throw-maps-current-before-earlier-slot'] = {
    'source': source('reversed-named', 'parked-throw'), 'stage': ABORT_STAGE,
    'checks': [*abort('reversed-named'), 'S.ACTIVEFIBER = (n_fiber)',
               '$unpack_line(S, piteratorunpack.CALL) = 26'],
}


def run(selected):
    review.CASES = CASES
    passed = review.run(selected)
    assert INPUT_BYTES == {p: p.read_bytes() for p in INPUT_BYTES}, 'sent review inputs changed'
    return passed


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if run(args.case) else 1)
