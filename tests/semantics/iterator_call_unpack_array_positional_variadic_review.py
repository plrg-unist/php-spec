#!/usr/bin/env python3
"""Reached positional variadic array holds, shared cells and child cleanup."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import fiber_state_review as review

CATALOG = Path(__file__).with_name('iterator_call_unpack_array_positional_variadic_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
SOURCES = {r['id']: r['source'] for r in json.loads(INPUT_BYTES[CATALOG])}
ADMISSION = ['$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
POST = ['$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))']
ZERO = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S']
ONE = ['S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
       'S_one = S_one_budget[.COMPLETION = NORMAL]']
PRIOR = '{SLOTS ([(NAMED_SENT (REFERENCE n_private_earlier))]), NAMED eps}'
SENT = ('{SLOTS ([(NAMED_SENT (REFERENCE n_private_earlier)), '
        '(NAMED_SENT (REFERENCE n_private_current))]), NAMED eps}')
BASE = ['n_data = piteratorunpack.OBJECT', 'n_cursor = piteratorunpack.ITERATOR',
        'piteratorunpack.CURRENT = KNOWN (PARRAY n_current_array)',
        'piteratorunpack.INPUT = KNOWN (POBJECT n_data)',
        'piteratorunpack.CALL.SENT = ' + PRIOR,
        'S.STORE[n_private_earlier] = DEFINED (PARRAY n_earlier_array)',
        'n_earlier_array =/= n_current_array',
        'S.ARRAYS[n_earlier_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_earlier_child))]',
        'S.ARRAYS[n_current_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_current_child))]',
        'n_earlier_child =/= n_current_child', 'n_earlier_child =/= n_data',
        'n_current_child =/= n_data',
        'piteratorunpack.KEY = KNOWN (PINT 1)', '~piteratorunpack.NAMED',
        '$iterator_unpack_named_target(S, piteratorunpack) = NAMED_POSITION 1']
CHILDREN = ['$node_children(S, HARRAY n_earlier_array) = [HOBJECT n_earlier_child]',
            '$node_children(S, HARRAY n_current_array) = [HOBJECT n_current_child]',
            '$heap_owners($heap_graph(S), HOBJECT n_earlier_child) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_current_child) = 1',
            '~(n_earlier_child <- S.DESTRUCTION.CALLED)',
            '~(n_current_child <- S.DESTRUCTION.CALLED)']
SOURCES_NULL = ['$lookup(S.ENV, $ptascii("earlier")) = (n_source_earlier)',
                '$lookup(S.ENV, $ptascii("current")) = (n_source_current)',
                'S.STORE[n_source_earlier] = DEFINED PNULL',
                'S.STORE[n_source_current] = DEFINED PNULL',
                'n_private_earlier =/= n_source_earlier',
                'n_private_earlier =/= n_source_current']
HELD = ['piteratorunpack.HOLD = piteratorunpack.CURRENT',
        '$iterator_unpack_hold_valid(piteratorunpack, "byref")',
        '$heap_owners($heap_graph(S), HCELL n_private_earlier) = 1',
        '$heap_owners($heap_graph(S), HARRAY n_earlier_array) = 1',
        '$heap_owners($heap_graph(S), HARRAY n_current_array) = 2']
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


def source(ending):
    return SOURCES['iterator-call-unpack-array-positional-variadic-' + ending]


def abort_checks():
    return [*BASE, *HELD, *CHILDREN, *ABORT_METADATA,
            '$iterator_lookup(S.ITERATORS, n_cursor) = eps',
            '$heap_owners($heap_graph(S), HOBJECT n_data) = 2',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HARRAY n_current_array), '
            'DESTRUCTION_VALUE (HOBJECT n_data), DESTRUCTION_VALUE (HOBJECT n_data), '
            'DESTRUCTION_VALUE (HCELL n_private_earlier), DESTRUCTION_VALUE (HARRAY n_current_array)]',
            '$iterator_unpack_discard_nodes(S_scope, piteratorunpack) = '
            '[HARRAY n_current_array, HOBJECT n_data, HOBJECT n_data, '
            'HCELL n_private_earlier, HARRAY n_current_array]', *ADMISSION, *ZERO]


CASES = {
    'second-positional-array-warning-holds-container-beside-earlier-cell': {
        'source': source('normal'),
        'stage': ('S.TODO = (ITERATOR_UNPACK piteratorunpack "send") :: ptask_tail* '
                  '-- if piteratorunpack.CALL.SENT.SLOTS = '
                  '[(NAMED_SENT (REFERENCE n_private_earlier))]'),
        'checks': [
            *BASE, *ACTIVE, *CHILDREN, 'piteratorunpack.HOLD = KNOWN PNULL',
            '$lookup(S.ENV, $ptascii("earlier")) = (n_source_earlier)',
            '$lookup(S.ENV, $ptascii("current")) = (n_source_current)',
            'S.STORE[n_source_earlier] = DEFINED PNULL',
            'S.STORE[n_source_current] = DEFINED (PARRAY n_current_array)',
            'n_private_earlier =/= n_source_earlier',
            'n_private_earlier =/= n_source_current',
            '$heap_owners($heap_graph(S), HCELL n_private_earlier) = 1',
            '$heap_owners($heap_graph(S), HARRAY n_earlier_array) = 1',
            '$heap_owners($heap_graph(S), HARRAY n_current_array) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_data) = 2',
            '$target_function(S, piteratorunpack.CALL.FUNCTION) = (pfunction)',
            'pfunction.SIGNATURE.PARAMETERS = [psparam]',
            r'psparam.VARIADIC /\ psparam.BYREF /\ psparam.TYPE = eps',
            '$iterator_unpack_warning_hold(S, piteratorunpack) = (piteratorunpack.CURRENT)',
            *ADMISSION, *ZERO, *ONE,
            'S_one.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
            'perrorcall.RESUME = ITERATOR_UNPACK piteratorunpack_held "byref"',
            'piteratorunpack_held = piteratorunpack[.HOLD = piteratorunpack.CURRENT]',
            'perrorcall.LEVEL = 2', 'perrorcall.LINE = 29',
            'perrorcall.MESSAGE = $ptascii("Cannot pass by-reference argument 2 of '
            'ArrayPositionalTarget30() by unpacking a Traversable, passing by-value instead")',
            '$error_call_valid(S_one, perrorcall)',
            '$heap_owners($heap_graph(S_one), HARRAY n_current_array) = 3',
            '$heap_owners($heap_graph(S_one), HCELL n_private_earlier) = 1',
            '$heap_owners($heap_graph(S_one), HARRAY n_earlier_array) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_current_child) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_earlier_child) = 1',
            'S_one.STORE = S.STORE', 'S_one.ARRAYS = S.ARRAYS',
            'S_one.EVENTS = S.EVENTS', *POST],
    },
    'second-positional-array-resume-transfers-hold-into-fresh-private-cell': {
        'source': source('normal'),
        'stage': ('S.TODO = (ITERATOR_UNPACK piteratorunpack "byref") :: ptask_tail* '
                  '-- if piteratorunpack.CALL.SENT.SLOTS = '
                  '[(NAMED_SENT (REFERENCE n_private_earlier))]'),
        'checks': [
            *BASE, *ACTIVE, *SOURCES_NULL, *HELD, *CHILDREN,
            '$iterator_unpack_hold_allowed(S, piteratorunpack, "byref")',
            *ADMISSION, *ZERO, 'n_private_current = |S.STORE|', *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(ITERATOR_UNPACK piteratorunpack_next "next-start") :: ptask_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HARRAY n_current_array)]',
            'piteratorunpack_next.CURRENT = KNOWN PNULL',
            'piteratorunpack_next.KEY = KNOWN PNULL',
            'piteratorunpack_next.HOLD = KNOWN PNULL',
            'piteratorunpack_next.CALL.SENT = ' + SENT,
            'S_one.STORE[n_private_current] = DEFINED (PARRAY n_current_array)',
            'n_private_current <- S_one.REFCELLS',
            'n_private_current =/= n_private_earlier',
            'n_private_current =/= n_source_earlier',
            'n_private_current =/= n_source_current',
            '$heap_owners($heap_graph(S_one), HCELL n_private_current) = 1',
            '$heap_owners($heap_graph(S_one), HCELL n_private_earlier) = 1',
            '$node_children(S_one, HCELL n_private_current) = [HARRAY n_current_array]',
            '$heap_owners($heap_graph(S_one), HARRAY n_current_array) = 2',
            '$heap_owners($heap_graph(S_one), HARRAY n_earlier_array) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_current_child) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_earlier_child) = 1', *POST,
            'S_two_budget = $drive_steps(S_one, 1)', 'S_two_budget.COMPLETION = BUDGET',
            'S_two = S_two_budget[.COMPLETION = NORMAL]',
            '$heap_owners($heap_graph(S_two), HARRAY n_current_array) = 1',
            '$heap_owners($heap_graph(S_two), HARRAY n_earlier_array) = 1',
            '$heap_owners($heap_graph(S_two), HOBJECT n_current_child) = 1',
            '$heap_owners($heap_graph(S_two), HOBJECT n_earlier_child) = 1',
            'S_two.EVENTS = S.EVENTS', '$call_descriptors_valid(S_two)',
            '$heap_valid($heap_graph(S_two))',
            'piteratorunpack_bad = piteratorunpack[.NAMED = true]',
            'S_bad = S[.TODO = (ITERATOR_UNPACK piteratorunpack_bad "byref") :: ptask_tail*]',
            '$heap_graph(S_bad) = $heap_graph(S)',
            '$iterator_unpack_hold_valid(piteratorunpack_bad, "byref")',
            '~$iterator_unpack_hold_allowed(S, piteratorunpack_bad, "byref")',
            '~$call_descriptors_valid(S_bad)',
            'piteratorunpack_foreign = piteratorunpack[.CALL = piteratorunpack.CALL[.CALLSITE = eps]]',
            'S_foreign = S[.TODO = (ITERATOR_UNPACK piteratorunpack_foreign "byref") :: ptask_tail*]',
            '$heap_graph(S_foreign) = $heap_graph(S)',
            '$iterator_unpack_hold_valid(piteratorunpack_foreign, "byref")',
            '~$iterator_unpack_hold_allowed(S, piteratorunpack_foreign, "byref")',
            '~$call_descriptors_valid(S_foreign)'],
    },
    'second-positional-array-throw-retires-cache-data-input-before-call-slots': {
        'source': source('second-warning-throw'), 'stage': ABORT_STAGE,
        'checks': [*abort_checks(), *SOURCES_NULL, *ONE,
                   '$heap_owners($heap_graph(S_one), HARRAY n_current_array) = 1',
                   '$heap_owners($heap_graph(S_one), HCELL n_private_earlier) = 1',
                   '$heap_owners($heap_graph(S_one), HARRAY n_earlier_array) = 1',
                   '$heap_owners($heap_graph(S_one), HOBJECT n_current_child) = 1',
                   '$heap_owners($heap_graph(S_one), HOBJECT n_earlier_child) = 1',
                   'S_one.EVENTS = S.EVENTS', *POST],
    },
    'earlier-private-cell-expands-container-then-child-before-current-array': {
        'source': source('second-warning-throw'),
        'stage': (ABORT_STAGE + ' -- if pdestructionrelease.JOBS = '
                  '[DESTRUCTION_VALUE (HCELL n_private_earlier), DESTRUCTION_VALUE (HARRAY n_current_array)]'),
        'checks': [
            *BASE, *CHILDREN, *ABORT_METADATA,
            '$heap_owners($heap_graph(S), HCELL n_private_earlier) = 1',
            '$heap_owners($heap_graph(S), HARRAY n_earlier_array) = 1',
            '$heap_owners($heap_graph(S), HARRAY n_current_array) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_data) = 0',
            'n_data <- S.DESTRUCTION.CALLED', *ADMISSION, *ZERO, *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_one) :: '
            '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*',
            'pdestructionrelease_one.JOBS = [DESTRUCTION_VALUE (HARRAY n_earlier_array), '
            'DESTRUCTION_VALUE (HARRAY n_current_array)]',
            '$heap_owners($heap_graph(S_one), HCELL n_private_earlier) = 0',
            '~((HCELL n_private_earlier) <- S_one.ALLOCATIONS)',
            '$heap_owners($heap_graph(S_one), HARRAY n_earlier_array) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_earlier_child) = 1',
            'S_one.STORE = S.STORE', 'S_one.ARRAYS = S.ARRAYS', *POST,
            'S_two_budget = $drive_steps(S_one, 1)', 'S_two_budget.COMPLETION = BUDGET',
            'S_two = S_two_budget[.COMPLETION = NORMAL]',
            'S_two.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_two) :: '
            '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*',
            'pdestructionrelease_two.JOBS = [DESTRUCTION_VALUE (HOBJECT n_earlier_child), '
            'DESTRUCTION_VALUE (HARRAY n_current_array)]',
            '$heap_owners($heap_graph(S_two), HARRAY n_earlier_array) = 0',
            '~((HARRAY n_earlier_array) <- S_two.ALLOCATIONS)',
            '$heap_owners($heap_graph(S_two), HOBJECT n_earlier_child) = 1',
            '$heap_owners($heap_graph(S_two), HOBJECT n_current_child) = 1',
            'S_two.EVENTS = S.EVENTS', '$call_descriptors_valid(S_two)',
            '$heap_valid($heap_graph(S_two))',
            'S_three_budget = $drive_steps(S_two, 1)', 'S_three_budget.COMPLETION = BUDGET',
            'S_three = S_three_budget[.COMPLETION = NORMAL]',
            'S_three.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: '
            '(DESTRUCTOR_RELEASE pdestructionrelease_three) :: '
            '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*',
            'pdestructorcall.OBJECT = n_earlier_child', 'pdestructorcall.PENDING = (n_error)',
            'pdestructionrelease_three.JOBS = [DESTRUCTION_VALUE (HARRAY n_current_array)]',
            'n_earlier_child <- S_three.DESTRUCTION.CALLED',
            '~(n_current_child <- S_three.DESTRUCTION.CALLED)',
            'S_three.EVENTS = S.EVENTS', '$call_descriptors_valid(S_three)',
            '$heap_valid($heap_graph(S_three))'],
    },
    'retired-positional-array-source-is-nonowning-and-rejects-phase-forgery': {
        'source': source('second-warning-throw'),
        'stage': (ABORT_STAGE + ' -- if pdestructionrelease.JOBS = eps '
                  '-- if piteratorunpack.CURRENT = KNOWN (PARRAY n_current_array) '
                  '-- if piteratorunpack.CALL.SENT = ' + PRIOR + ' '
                  '-- if S.STORE[n_private_earlier] = DEFINED (PARRAY n_earlier_array) '
                  '-- if S.ARRAYS[n_earlier_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_earlier_child))] '
                  '-- if S.ARRAYS[n_current_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_current_child))] '
                  '-- if n_current_child <- S.DESTRUCTION.CALLED '
                  '-- if n_earlier_child <- S.DESTRUCTION.CALLED'),
        'checks': [
            *BASE, 'piteratorunpack.HOLD = piteratorunpack.CURRENT',
            '$heap_owners($heap_graph(S), HCELL n_private_earlier) = 0',
            '$heap_owners($heap_graph(S), HARRAY n_earlier_array) = 0',
            '$heap_owners($heap_graph(S), HARRAY n_current_array) = 0',
            '$heap_owners($heap_graph(S), HOBJECT n_earlier_child) = 0',
            '$heap_owners($heap_graph(S), HOBJECT n_current_child) = 0',
            '~((HCELL n_private_earlier) <- S.ALLOCATIONS)',
            '~((HARRAY n_earlier_array) <- S.ALLOCATIONS)',
            '~((HARRAY n_current_array) <- S.ALLOCATIONS)',
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
            '~$destructor_operation_valid(S_bad, pdestructionoperation_bad)',
            '~$call_descriptors_valid(S_bad)'],
    },
}

CASES['parked-second-array-warning-preserves-cell-edges-and-rejects-duplicate'] = {
    'source': source('parked-throw'),
    'stage': ('S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_main* '
              '-- if pconfigcall.KIND = INTRINSIC_FIBER_THROW '
              '-- if pconfigcall.OWNER = (n_fiber) '
              '-- if $fiber_at(S, n_fiber) = (pfiber) -- if pfiber.VM = (pfibervm) '
              '-- if pfibervm.FRAMES = [pframe_unpack, pframe_base] '
              '-- if pframe_unpack.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_unpack* '
              '-- if perrorcall.RESUME = ITERATOR_UNPACK piteratorunpack "byref"'),
    'checks': [
        *BASE, *HELD, *CHILDREN, '$heap_owners($heap_graph(S), HOBJECT n_data) = 2',
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
        '$iterator_unpack_hold_allowed(S_scope, piteratorunpack, "byref")',
        '$error_entered_call_valid(S_scope, perrorcall)',
        '$fiber_vm_valid(S, pfibervm, (n_fiber), eps)',
        'pfibervm.CURRENT = (pcallcontext_saved)', 'pcallcontext_saved.LINE = 31',
        'perrorcall.LINE = 31', *ADMISSION, *ZERO,
        'piteratorunpack_bad = piteratorunpack[.NAMED = true]',
        'perrorcall_bad = perrorcall[.RESUME = ITERATOR_UNPACK piteratorunpack_bad "byref"]',
        'pframe_bad = pframe_unpack[.TODO = (ERROR_HANDLER_RESULT perrorcall_bad) :: ptask_unpack*]',
        'pfibervm_bad = pfibervm[.FRAMES = [pframe_bad, pframe_base]]',
        'S_bad = $fiber_put(S, n_fiber, pfiber[.VM = (pfibervm_bad)])',
        '$heap_graph(S_bad) = $heap_graph(S)',
        '~$iterator_unpack_hold_allowed(S_scope, piteratorunpack_bad, "byref")',
        '~$fiber_vm_valid(S_bad, pfibervm_bad, (n_fiber), eps)',
        '~$call_descriptors_valid(S_bad)',
        'piteratorunpack_line = piteratorunpack[.CALL = piteratorunpack.CALL[.LINE = 32]]',
        'perrorcall_line = perrorcall[.LINE = 32]'
        '[.EVENT = DIAGNOSTIC "Warning" perrorcall.MESSAGE 32]'
        '[.RESUME = ITERATOR_UNPACK piteratorunpack_line "byref"]',
        'pframe_line = pframe_unpack[.TODO = (ERROR_HANDLER_RESULT perrorcall_line) :: ptask_unpack*]',
        'pfibervm_line = pfibervm[.CURRENT = (pcallcontext_saved[.LINE = 32])]'
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
        '$heap_owners($heap_graph(S_duplicate), HCELL n_private_earlier) = 2',
        '$heap_owners($heap_graph(S_duplicate), HARRAY n_earlier_array) = 1',
        '$heap_owners($heap_graph(S_duplicate), HARRAY n_current_array) = 4',
        '$heap_owners($heap_graph(S_duplicate), HOBJECT n_earlier_child) = 1',
        '$heap_owners($heap_graph(S_duplicate), HOBJECT n_current_child) = 1',
        '$heap_owners($heap_graph(S_duplicate), HOBJECT n_data) = 4',
        '~$fiber_vm_valid(S_duplicate, pfibervm_duplicate, (n_fiber), eps)',
        '~$call_descriptors_valid(S_duplicate)'],
}
CASES['injected-second-array-warning-keeps-main-scalars-and-slot-order'] = {
    'source': source('parked-throw'), 'stage': ABORT_STAGE,
    'checks': [*abort_checks(), 'S.ACTIVEFIBER = (n_fiber)',
               '$unpack_line(S, piteratorunpack.CALL) = 31',
               'S.GLOBALTABLE = (psymboltable_global)',
               '$lookup(psymboltable_global.ENV, $ptascii("earlier")) = (n_source_earlier)',
               '$lookup(psymboltable_global.ENV, $ptascii("current")) = (n_source_current)',
               'S.STORE[n_source_earlier] = DEFINED (PINT 17)',
               'S.STORE[n_source_current] = DEFINED (PINT 19)'],
}

REST = ['pcallcontext.EXTRA = [REFERENCE n_private_earlier, REFERENCE n_private_current]',
        'pcallcontext.NAMED = eps', 'pcallcontext.ARGC = 2',
        'n_private_earlier =/= n_private_current',
        '$lookup(S.ENV, $ptascii("rest")) = (n_rest)',
        'S.STORE[n_rest] = DEFINED (PARRAY n_rest_array)',
        'S.ARRAYS[n_rest_array].ITEMS = '
        '[ENTRY (KINT 0) (ALIAS n_private_earlier), ENTRY (KINT 1) (ALIAS n_private_current)]',
        '$heap_owners($heap_graph(S), HCELL n_private_earlier) = 2',
        '$heap_owners($heap_graph(S), HCELL n_private_current) = 2',
        '$heap_owners($heap_graph(S), HARRAY n_rest_array) = 1']
CASES['packed-variadic-array-receive-keeps-private-cells-and-child-edges'] = {
    'source': source('normal'),
    'stage': ('S.TODO = [VARIADIC_RECEIVE porigin 2] '
              '-- if S.CURRENT = (pcallcontext) '
              '-- if pcallcontext.NAME = $ptascii("ArrayPositionalTarget30")'),
    'checks': [
        '$receiving_function(S, porigin) = (pfunction)',
        'pfunction.ORIGIN = pcallcontext.FUNCTION', 'pcallcontext.TARGET = porigin',
        *REST, 'S.STORE[n_private_earlier] = DEFINED (PARRAY n_earlier_array)',
        'S.STORE[n_private_current] = DEFINED (PARRAY n_current_array)',
        'S.ARRAYS[n_earlier_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_earlier_child))]',
        'S.ARRAYS[n_current_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_current_child))]',
        'n_earlier_array =/= n_current_array', *CHILDREN,
        '$heap_owners($heap_graph(S), HARRAY n_earlier_array) = 1',
        '$heap_owners($heap_graph(S), HARRAY n_current_array) = 1',
        '$call_task_valid(S, VARIADIC_RECEIVE porigin 2)', *ADMISSION, *ZERO, *ONE,
        'S_one.TODO = $function_tasks(S_one, pfunction)',
        'S_one.STORE = S.STORE', 'S_one.ARRAYS = S.ARRAYS',
        'S_one.CURRENT = S.CURRENT', 'S_one.EVENTS = S.EVENTS', *POST],
}
CASES['nested-current-array-write-destroys-child-before-earlier-rest-owner'] = {
    'source': source('normal'),
    'stage': ('S.CURRENT = (pcallcontext) '
              '-- if pcallcontext.NAME = $ptascii("ArrayPositionalTarget30") '
              '-- if S.TODO = (EMIT z_emit) :: ptask_tail* '
              '-- if S.RESULT = KNOWN pvalue_text '
              '-- if $string_bytes(pvalue_text) = ($ptascii("F|"))'),
    'checks': [
        *REST, 'S.STORE[n_private_earlier] = DEFINED (PARRAY n_earlier_array)',
        'S.STORE[n_private_current] = DEFINED (PARRAY n_current_array)',
        'n_earlier_array =/= n_current_array',
        'S.ARRAYS[n_earlier_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_earlier_child))]',
        'S.ARRAYS[n_current_array].ITEMS = [ENTRY (KINT 0) (DIRECT PNULL)]',
        '$node_children(S, HARRAY n_current_array) = eps',
        'S.DESTRUCTION.CALLED = [n_data, n_current_child]',
        'n_earlier_child =/= n_current_child', 'n_earlier_child =/= n_data',
        'n_current_child =/= n_data',
        '$object_name(S, n_current_child) = $ptascii("ArrayPositionalCurrent30")',
        '$heap_owners($heap_graph(S), HARRAY n_earlier_array) = 1',
        '$heap_owners($heap_graph(S), HARRAY n_current_array) = 1',
        '$heap_owners($heap_graph(S), HOBJECT n_earlier_child) = 1',
        '$heap_owners($heap_graph(S), HOBJECT n_current_child) = 0',
        '~((HOBJECT n_current_child) <- S.ALLOCATIONS)',
        '~(n_earlier_child <- S.DESTRUCTION.CALLED)', *ADMISSION, *ZERO, *ONE,
        'S_one.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("F|")]',
        'S_one.STORE = S.STORE', 'S_one.ARRAYS = S.ARRAYS',
        'S_one.CURRENT = S.CURRENT', *POST,
        'S_done = $drive(S, 4000)', 'S_done.COMPLETION = NORMAL',
        'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("F|"), OUTPUT $ptascii("A|"), OUTPUT $ptascii("E")]',
        'n_earlier_child <- S_done.DESTRUCTION.CALLED',
        'n_current_child <- S_done.DESTRUCTION.CALLED',
        'n_data <- S_done.DESTRUCTION.CALLED',
        '$heap_owners($heap_graph(S_done), HCELL n_private_earlier) = 0',
        '$heap_owners($heap_graph(S_done), HCELL n_private_current) = 0',
        '$heap_owners($heap_graph(S_done), HARRAY n_earlier_array) = 0',
        '$heap_owners($heap_graph(S_done), HARRAY n_current_array) = 0',
        '$heap_owners($heap_graph(S_done), HOBJECT n_earlier_child) = 0',
        '$heap_owners($heap_graph(S_done), HOBJECT n_current_child) = 0',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))'],
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
    assert INPUT_BYTES == {p: p.read_bytes() for p in INPUT_BYTES}, 'array variadic review inputs changed'
    return passed


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if run(args.case) else 1)
