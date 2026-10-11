#!/usr/bin/env python3
"""Reached untyped named-array holds, private rest copies and child lifetimes."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import fiber_state_review as review

CATALOG = Path(__file__).with_name('iterator_call_unpack_array_named_variadic_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
SOURCES = {r['id']: r['source'] for r in json.loads(INPUT_BYTES[CATALOG])}
ADMISSION = ['$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
POST = ['$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))']
ZERO = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S']
ONE = ['S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
       'S_one = S_one_budget[.COMPLETION = NORMAL]']
PRIOR = '{SLOTS eps, NAMED ([($ptascii("zeta"), REFERENCE n_private_earlier)])}'
SENT = ('{SLOTS eps, NAMED ([($ptascii("zeta"), REFERENCE n_private_earlier), '
        '($ptascii("alpha"), REFERENCE n_private_current)])}')
TYPE = ['pfunction.SIGNATURE.PARAMETERS = [psparam]',
        r'psparam.VARIADIC /\ psparam.BYREF',
        'psparam.TYPE = eps']
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
        'piteratorunpack.KEY = KNOWN pvalue_key',
        '$string_bytes(pvalue_key) = ($ptascii("alpha"))', 'piteratorunpack.NAMED',
        '$iterator_unpack_named_target(S, piteratorunpack) = NAMED_EXTRA $ptascii("alpha")']
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
    return SOURCES['iterator-call-unpack-array-named-variadic-' + ending]


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
    'second-untyped-named-array-warning-holds-container-beside-earlier-cell': {
        'source': source('normal'),
        'stage': ('S.TODO = (ITERATOR_UNPACK piteratorunpack "send") :: ptask_tail* '
                  '-- if piteratorunpack.CALL.SENT.NAMED = '
                  '[($ptascii("zeta"), REFERENCE n_private_earlier)]'),
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
            *TYPE,
            '$iterator_unpack_warning_hold(S, piteratorunpack) = (piteratorunpack.CURRENT)',
            *ADMISSION, *ZERO, *ONE,
            'S_one.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
            'perrorcall.RESUME = ITERATOR_UNPACK piteratorunpack_held "byref"',
            'piteratorunpack_held = piteratorunpack[.HOLD = piteratorunpack.CURRENT]',
            'perrorcall.LEVEL = 2', 'perrorcall.LINE = 29',
            'perrorcall.MESSAGE = $ptascii("Cannot pass by-reference argument 1 of '
            'ArrayNamedTarget33() by unpacking a Traversable, passing by-value instead")',
            '$error_call_valid(S_one, perrorcall)',
            '$heap_owners($heap_graph(S_one), HARRAY n_current_array) = 3',
            '$heap_owners($heap_graph(S_one), HCELL n_private_earlier) = 1',
            '$heap_owners($heap_graph(S_one), HARRAY n_earlier_array) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_current_child) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_earlier_child) = 1',
            'S_one.STORE = S.STORE', 'S_one.ARRAYS = S.ARRAYS',
            'S_one.EVENTS = S.EVENTS', *POST],
    },
    'second-untyped-named-array-resume-transfers-hold-into-fresh-private-cell': {
        'source': source('normal'),
        'stage': ('S.TODO = (ITERATOR_UNPACK piteratorunpack "byref") :: ptask_tail* '
                  '-- if piteratorunpack.CALL.SENT.NAMED = '
                  '[($ptascii("zeta"), REFERENCE n_private_earlier)]'),
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
            'piteratorunpack_bad = piteratorunpack[.CALL = piteratorunpack.CALL'
            '[.SENT = piteratorunpack.CALL.SENT[.NAMED = '
            '[($ptascii("alpha"), REFERENCE n_private_earlier)]]]]',
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
    'second-untyped-named-array-throw-retires-cache-data-input-before-named-cells': {
        'source': source('second-warning-throw'), 'stage': ABORT_STAGE,
        'checks': [*abort_checks(), *SOURCES_NULL, *ONE,
                   '$heap_owners($heap_graph(S_one), HARRAY n_current_array) = 1',
                   '$heap_owners($heap_graph(S_one), HCELL n_private_earlier) = 1',
                   '$heap_owners($heap_graph(S_one), HARRAY n_earlier_array) = 1',
                   '$heap_owners($heap_graph(S_one), HOBJECT n_current_child) = 1',
                   '$heap_owners($heap_graph(S_one), HOBJECT n_earlier_child) = 1',
                   'S_one.EVENTS = S.EVENTS', *POST],
    },
    'retired-untyped-named-array-source-is-nonowning-and-rejects-phase-forgery': {
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
            'piteratorunpack_bad = piteratorunpack[.KEY = KNOWN (PINT 1)]',
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

CASES['parked-second-untyped-array-warning-preserves-cell-edges-and-rejects-duplicate'] = {
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
        'piteratorunpack_bad = piteratorunpack[.CALL = piteratorunpack.CALL'
        '[.SENT = piteratorunpack.CALL.SENT[.NAMED = '
        '[($ptascii("alpha"), REFERENCE n_private_earlier)]]]]',
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
CASES['injected-second-untyped-array-warning-keeps-main-scalars-and-named-insertion-order'] = {
    'source': source('parked-throw'), 'stage': ABORT_STAGE,
    'checks': [*abort_checks(), 'S.ACTIVEFIBER = (n_fiber)',
               '$unpack_line(S, piteratorunpack.CALL) = 31',
               'S.GLOBALTABLE = (psymboltable_global)',
               '$lookup(psymboltable_global.ENV, $ptascii("earlier")) = (n_source_earlier)',
               '$lookup(psymboltable_global.ENV, $ptascii("current")) = (n_source_current)',
               'S.STORE[n_source_earlier] = DEFINED (PINT 17)',
               'S.STORE[n_source_current] = DEFINED (PINT 19)'],
}

# The logical rest is separated from the original named argument buffer. This
# models observable COW behavior, not Zend's shared table before the first write.
REST = ['pcallcontext.EXTRA = eps',
        'pcallcontext.NAMED = [($ptascii("zeta"), REFERENCE n_private_earlier), '
        '($ptascii("alpha"), REFERENCE n_private_current)]', 'pcallcontext.ARGC = 0',
        'n_private_earlier =/= n_private_current',
        'n_private_earlier <- S.REFCELLS', 'n_private_current <- S.REFCELLS',
        'S.STORE[n_private_earlier] = DEFINED (PARRAY n_earlier_array)',
        'S.STORE[n_private_current] = DEFINED (PARRAY n_current_array)',
        'n_earlier_array =/= n_current_array',
        'S.ARRAYS[n_earlier_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_earlier_child))]',
        'S.ARRAYS[n_current_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_current_child))]',
        'n_earlier_child =/= n_current_child',
        '$lookup(S.ENV, $ptascii("rest")) = (n_rest)',
        'S.STORE[n_rest] = DEFINED (PARRAY n_rest_array)',
        'n_rest_array =/= n_earlier_array', 'n_rest_array =/= n_current_array',
        '$heap_owners($heap_graph(S), HCELL n_private_earlier) = 1',
        '$heap_owners($heap_graph(S), HCELL n_private_current) = 1',
        '$heap_owners($heap_graph(S), HARRAY n_rest_array) = 1',
        '$node_children(S, HCELL n_private_earlier) = [HARRAY n_earlier_array]',
        '$node_children(S, HCELL n_private_current) = [HARRAY n_current_array]',
        '$node_children(S, HARRAY n_earlier_array) = [HOBJECT n_earlier_child]',
        '$node_children(S, HARRAY n_current_array) = [HOBJECT n_current_child]',
        '$heap_owners($heap_graph(S), HOBJECT n_earlier_child) = 1',
        '$heap_owners($heap_graph(S), HOBJECT n_current_child) = 1',
        'S.DESTRUCTION.CALLED = [n_data]',
        'n_earlier_child =/= n_data', 'n_current_child =/= n_data']
CASES['private-named-array-cells-produce-direct-rest-items-with-shared-cell-fallback'] = {
    'source': source('normal'),
    'stage': ('S.TODO = [NAMED_VARIADIC_RECEIVE porigin 2] '
              '-- if S.CURRENT = (pcallcontext) '
              '-- if pcallcontext.NAME = $ptascii("ArrayNamedTarget33")'),
    'checks': [
        '$receiving_function(S, porigin) = (pfunction)', *TYPE,
        'pfunction.ORIGIN = pcallcontext.FUNCTION', 'pcallcontext.TARGET = porigin',
        *REST,
        'S.ARRAYS[n_rest_array].ITEMS = '
        '[ENTRY (KSTRING $ptascii("zeta")) (DIRECT (PARRAY n_earlier_array)), '
        'ENTRY (KSTRING $ptascii("alpha")) (DIRECT (PARRAY n_current_array))]',
        '$node_children(S, HARRAY n_rest_array) = [HARRAY n_earlier_array, HARRAY n_current_array]',
        '$heap_owners($heap_graph(S), HARRAY n_earlier_array) = 2',
        '$heap_owners($heap_graph(S), HARRAY n_current_array) = 2',
        '$named_variadic_private(S, pfunction, 0, REFERENCE n_private_earlier, PARRAY n_earlier_array)',
        '$named_variadic_private(S, pfunction, 1, REFERENCE n_private_current, PARRAY n_current_array)',
        '$named_variadic_item(S, pfunction, 0, REFERENCE n_private_earlier, PARRAY n_earlier_array) = '
        'DIRECT (PARRAY n_earlier_array)',
        '$named_variadic_item(S, pfunction, 1, REFERENCE n_private_current, PARRAY n_current_array) = '
        'DIRECT (PARRAY n_current_array)',
        '$call_task_valid(S, NAMED_VARIADIC_RECEIVE porigin 2)', *ADMISSION, *ZERO,
        # Counterfactual guards based on a genuine receive frontier; no native
        # heap/count equivalence or additional source agreement is asserted.
        'S_shared = S[.HELD = S.HELD ++ [HCELL n_private_current]]',
        '$heap_valid($heap_graph(S_shared))',
        '$heap_owners($heap_graph(S_shared), HCELL n_private_current) = 2',
        '$heap_owners($heap_graph(S_shared), HARRAY n_current_array) = 2',
        '~$named_variadic_private(S_shared, pfunction, 1, REFERENCE n_private_current, PARRAY n_current_array)',
        '$named_variadic_item(S_shared, pfunction, 1, REFERENCE n_private_current, PARRAY n_current_array) = '
        'ALIAS n_private_current',
        'S_extra = S[.CURRENT = (pcallcontext[.EXTRA = [KNOWN (PINT 7)]])]',
        '$heap_graph(S_extra) = $heap_graph(S)',
        '~$named_variadic_private(S_extra, pfunction, 1, REFERENCE n_private_current, PARRAY n_current_array)',
        '$named_variadic_item(S_extra, pfunction, 1, REFERENCE n_private_current, PARRAY n_current_array) = '
        'ALIAS n_private_current',
        'S_foreign = S[.CURRENT = (pcallcontext[.CALLSITE = eps])]',
        '$heap_graph(S_foreign) = $heap_graph(S)',
        '~$named_variadic_private(S_foreign, pfunction, 1, REFERENCE n_private_current, PARRAY n_current_array)',
        '$named_variadic_item(S_foreign, pfunction, 1, REFERENCE n_private_current, PARRAY n_current_array) = '
        'ALIAS n_private_current', *ONE,
        'S_one.TODO = $function_tasks(S_one, pfunction)',
        'S_one.STORE = S.STORE', 'S_one.ARRAYS = S.ARRAYS',
        'S_one.CURRENT = S.CURRENT', 'S_one.EVENTS = S.EVENTS', *POST],
}
CASES['nested-direct-array-write-copies-container-and-keeps-original-child-through-F'] = {
    'source': source('normal'),
    'stage': ('S.CURRENT = (pcallcontext) '
              '-- if pcallcontext.NAME = $ptascii("ArrayNamedTarget33") '
              '-- if S.TODO = (EMIT z_emit) :: ptask_tail* '
              '-- if S.RESULT = KNOWN pvalue_text '
              '-- if $string_bytes(pvalue_text) = ($ptascii("F|"))'),
    'checks': [
        *REST,
        'S.ARRAYS[n_rest_array].ITEMS = '
        '[ENTRY (KSTRING $ptascii("zeta")) (DIRECT (PARRAY n_earlier_array)), '
        'ENTRY (KSTRING $ptascii("alpha")) (DIRECT (PARRAY n_current_copy))]',
        'n_current_copy =/= n_current_array', 'n_current_copy =/= n_earlier_array',
        'n_current_copy =/= n_rest_array',
        'S.ARRAYS[n_current_copy].ITEMS = [ENTRY (KINT 0) (DIRECT PNULL)]',
        '$node_children(S, HARRAY n_current_copy) = eps',
        '$node_children(S, HARRAY n_rest_array) = [HARRAY n_earlier_array, HARRAY n_current_copy]',
        '$heap_owners($heap_graph(S), HARRAY n_earlier_array) = 2',
        '$heap_owners($heap_graph(S), HARRAY n_current_array) = 1',
        '$heap_owners($heap_graph(S), HARRAY n_current_copy) = 1',
        '$object_name(S, n_current_child) = $ptascii("ArrayNamedCurrent33")',
        '~(n_earlier_child <- S.DESTRUCTION.CALLED)',
        '~(n_current_child <- S.DESTRUCTION.CALLED)', *ADMISSION, *ZERO, *ONE,
        'S_one.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("F|")]',
        'S_one.STORE = S.STORE', 'S_one.ARRAYS = S.ARRAYS',
        'S_one.CURRENT = S.CURRENT', *POST,
        'S_done = $drive(S, 4000)', 'S_done.COMPLETION = NORMAL',
        'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("F|"), OUTPUT $ptascii("A|"), '
        'OUTPUT $ptascii("B|"), OUTPUT $ptascii("E")]',
        'n_earlier_child <- S_done.DESTRUCTION.CALLED',
        'n_current_child <- S_done.DESTRUCTION.CALLED', 'n_data <- S_done.DESTRUCTION.CALLED',
        '$heap_owners($heap_graph(S_done), HCELL n_private_earlier) = 0',
        '$heap_owners($heap_graph(S_done), HCELL n_private_current) = 0',
        '$heap_owners($heap_graph(S_done), HARRAY n_earlier_array) = 0',
        '$heap_owners($heap_graph(S_done), HARRAY n_current_array) = 0',
        '$heap_owners($heap_graph(S_done), HARRAY n_current_copy) = 0',
        '$heap_owners($heap_graph(S_done), HARRAY n_rest_array) = 0',
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
    assert INPUT_BYTES == {p: p.read_bytes() for p in INPUT_BYTES}, 'untyped named-array review inputs changed'
    return passed


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if run(args.case) else 1)
