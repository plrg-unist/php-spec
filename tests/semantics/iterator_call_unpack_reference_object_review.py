#!/usr/bin/env python3
"""Reached Iterator property references, detached payloads and fresh arguments."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import fiber_state_review as review

CATALOG = Path(__file__).with_name('iterator_call_unpack_reference_object_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
SOURCES = {r['id']: r['source'] for r in json.loads(INPUT_BYTES[CATALOG])}
ADMISSION = ['$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
POST = ['$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))']
ZERO = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S']
ONE = ['S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
       'S_one = S_one_budget[.COMPLETION = NORMAL]']
RAW = ['n_data = piteratorunpack.OBJECT', 'n_cursor = piteratorunpack.ITERATOR',
       'piteratorunpack.CURRENT = REFERENCE n_raw',
       'piteratorunpack.INPUT = KNOWN (POBJECT n_data)',
       'piteratorunpack.CALL.SENT = {SLOTS eps, NAMED eps}',
       'piteratorunpack.KEY = KNOWN (PINT 0)', '~piteratorunpack.NAMED',
       '$operand_nodes(piteratorunpack.CURRENT) = [HCELL n_raw]']
LIVE = ['S.STORE[n_raw] = DEFINED (POBJECT n_payload)', 'n_payload =/= n_data',
        'n_raw <- S.REFCELLS',
        '$objectprops_record_at(S.OBJECTPROPS, n_data) = (pobjectprops)',
        '$property_slot_at(pobjectprops.SLOTS, $ptascii("payload")) = (ppropertyslot)',
        'ppropertyslot.STATE = PROP_VALUE (ALIAS n_raw)',
        '$node_children(S, HOBJECT n_data) = [HCELL n_raw]',
        '$node_children(S, HCELL n_raw) = [HOBJECT n_payload]']
HELD = ['piteratorunpack.SNAPSHOT = (POBJECT n_payload)',
        'piteratorunpack.HOLD = KNOWN (POBJECT n_payload)',
        '$iterator_unpack_hold_valid(piteratorunpack, "byref")',
        '$heap_owners($heap_graph(S), HOBJECT n_payload) = 2',
        '$heap_owners($heap_graph(S), HCELL n_raw) = 2',
        '$heap_owners($heap_graph(S), HOBJECT n_data) = 2',
        '$iterator_unpack_nodes(piteratorunpack) = '
        '[HCELL n_raw, HOBJECT n_data, HOBJECT n_data, HOBJECT n_payload]']
ACTIVE = ['$useriter_cursor_valid(S, n_cursor, n_data)',
          'S.ORIGIN = $unpack_origin(S, piteratorunpack.CALL)',
          '$useriter_tasks_ids(S.TODO) = [n_cursor]']
FRESH = ['S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
         '(ITERATOR_UNPACK piteratorunpack_next "next-start") :: ptask_tail*',
         'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HCELL n_raw)]',
         'piteratorunpack_next.CURRENT = KNOWN PNULL',
         'piteratorunpack_next.KEY = KNOWN PNULL',
         'piteratorunpack_next.HOLD = KNOWN PNULL',
         'piteratorunpack_next.SNAPSHOT = eps', '~piteratorunpack_next.NAMED',
         'piteratorunpack_next.CALL.SENT.SLOTS = [NAMED_SENT (REFERENCE n_private)]',
         'piteratorunpack_next.CALL.SENT.NAMED = eps',
         'n_private =/= n_raw', 'n_private <- S_one.REFCELLS',
         'S_one.STORE[n_raw] = DEFINED (POBJECT n_payload)',
         'S_one.STORE[n_private] = DEFINED (POBJECT n_payload)',
         '$heap_owners($heap_graph(S_one), HCELL n_raw) = 2',
         '$heap_owners($heap_graph(S_one), HCELL n_private) = 1',
         '$heap_owners($heap_graph(S_one), HOBJECT n_payload) = 2',
         '$heap_owners($heap_graph(S_one), HOBJECT n_data) = 2',
         '$node_children(S_one, HCELL n_private) = [HOBJECT n_payload]',
         '~(n_payload <- S_one.DESTRUCTION.CALLED)',
         '$destructor_release_valid(S_one, pdestructionrelease)', *POST]
ABORT_STAGE = ('S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
               '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail* '
               '-- if pdestructionoperation.PENDING = (n_error) '
               '-- if pdestructionoperation.SOURCE = ITERATOR_UNPACK piteratorunpack "byref"')
PARKED_STAGE = ('S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_main* '
                '-- if pconfigcall.KIND = INTRINSIC_FIBER_RESUME '
                '-- if pconfigcall.OWNER = (n_fiber) '
                '-- if $fiber_at(S, n_fiber) = (pfiber) '
                '-- if pfiber.VM = (pfibervm) '
                '-- if pfibervm.FRAMES = [pframe_unpack, pframe_base] '
                '-- if pframe_unpack.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_unpack* '
                '-- if perrorcall.RESUME = ITERATOR_UNPACK piteratorunpack "byref"')
BODY_STAGE = ('S.CURRENT = (pcallcontext) '
              '-- if pcallcontext.NAME = $ptascii("ReferenceTarget34") '
              '-- if S.TODO = (EMIT z_emit) :: ptask_tail* '
              '-- if S.RESULT = KNOWN pvalue_text '
              '-- if $string_bytes(pvalue_text) = ($ptascii("F|"))')
MESSAGE = ('$ptascii("Cannot pass by-reference argument 1 of ReferenceTarget34() '
           'by unpacking a Traversable, passing by-value instead")')


def source(ending):
    return SOURCES['iterator-call-unpack-reference-object-' + ending]


def abort_checks():
    return [*RAW, *LIVE, *HELD,
            '$iterator_lookup(S.ITERATORS, n_cursor) = eps',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HCELL n_raw), '
            'DESTRUCTION_VALUE (HOBJECT n_data), DESTRUCTION_VALUE (HOBJECT n_data), '
            'DESTRUCTION_VALUE (HOBJECT n_payload)]',
            'S_scope = S[.CURRENT = pdestructionoperation.CALLER]'
            '[.ORIGIN = pdestructionoperation.ORIGIN]'
            '[.CONSTCONTEXT = pdestructionoperation.CONSTCONTEXT]',
            '$iterator_unpack_reference_allowed(S_scope, piteratorunpack)',
            '$iterator_unpack_hold_allowed(S_scope, piteratorunpack, "byref")',
            '$iterator_unpack_discard_nodes(S_scope, piteratorunpack) = '
            '[HCELL n_raw, HOBJECT n_data, HOBJECT n_data, HOBJECT n_payload]',
            '$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = [HOBJECT n_error]',
            '$throwable_live(S, n_error)', '$throwable_field(S, n_error, "code") = PINT 51',
            '$eager_operation_source_valid(S, pdestructionoperation)',
            '$destructor_operation_valid(S, pdestructionoperation)',
            '$destructor_release_valid(S, pdestructionrelease)', *ADMISSION, *ZERO]


CASES = {
    'property-reference-warning-adds-payload-owner-with-nonowning-snapshot': {
        'source': source('normal'),
        'stage': 'S.TODO = (ITERATOR_UNPACK piteratorunpack "send") :: ptask_tail*',
        'checks': [
            *RAW, *LIVE, *ACTIVE, 'piteratorunpack.HOLD = KNOWN PNULL',
            'piteratorunpack.SNAPSHOT = eps',
            '$heap_owners($heap_graph(S), HCELL n_raw) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_payload) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_data) = 2',
            '~$iterator_unpack_scalar_operand(S, piteratorunpack.CURRENT)',
            '$iterator_unpack_reference_allowed(S, piteratorunpack)',
            '$iterator_unpack_reference_object(S, piteratorunpack) = (POBJECT n_payload)',
            '$iterator_unpack_warning_hold(S, piteratorunpack) = (KNOWN (POBJECT n_payload))',
            *ADMISSION, *ZERO, *ONE,
            'S_one.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
            'perrorcall.RESUME = ITERATOR_UNPACK piteratorunpack_held "byref"',
            'piteratorunpack_held = piteratorunpack[.HOLD = KNOWN (POBJECT n_payload)]'
            '[.SNAPSHOT = (POBJECT n_payload)]',
            'perrorcall.LEVEL = 2', 'perrorcall.LINE = 21',
            'perrorcall.MESSAGE = ' + MESSAGE,
            '$error_call_valid(S_one, perrorcall)',
            '$heap_owners($heap_graph(S_one), HCELL n_raw) = 2',
            '$heap_owners($heap_graph(S_one), HOBJECT n_payload) = 2',
            '$heap_owners($heap_graph(S_one), HOBJECT n_data) = 2',
            'S_one.STORE = S.STORE', 'S_one.EVENTS = S.EVENTS', *POST,
            'S_early = S[.TODO = (ITERATOR_UNPACK piteratorunpack_held "send") :: ptask_tail*]',
            '$heap_valid($heap_graph(S_early))',
            '$heap_owners($heap_graph(S_early), HOBJECT n_payload) = 2',
            '~$iterator_unpack_hold_valid(piteratorunpack_held, "send")',
            '~$call_descriptors_valid(S_early)',
        ],
    },
    'stable-property-reference-transfers-hold-to-distinct-fresh-cell': {
        'source': source('normal'),
        'stage': 'S.TODO = (ITERATOR_UNPACK piteratorunpack "byref") :: ptask_tail*',
        'checks': [
            *RAW, *LIVE, *HELD, *ACTIVE,
            '$iterator_unpack_hold_live(S, piteratorunpack, "byref")',
            '$iterator_unpack_reference_allowed(S, piteratorunpack)',
            *ADMISSION, *ZERO,
            'piteratorunpack_missing = piteratorunpack[.HOLD = KNOWN PNULL][.SNAPSHOT = eps]',
            'S_missing = S[.TODO = (ITERATOR_UNPACK piteratorunpack_missing "byref") :: ptask_tail*]',
            '$heap_valid($heap_graph(S_missing))',
            '$heap_owners($heap_graph(S_missing), HOBJECT n_payload) = 1',
            '~$iterator_unpack_hold_live(S_missing, piteratorunpack_missing, "byref")',
            '~$call_descriptors_valid(S_missing)',
            'piteratorunpack_foreign = piteratorunpack[.HOLD = KNOWN (POBJECT n_data)]',
            'S_foreign = S[.TODO = (ITERATOR_UNPACK piteratorunpack_foreign "byref") :: ptask_tail*]',
            '$heap_valid($heap_graph(S_foreign))',
            '$heap_owners($heap_graph(S_foreign), HOBJECT n_payload) = 1',
            '$heap_owners($heap_graph(S_foreign), HOBJECT n_data) = 3',
            '~$iterator_unpack_hold_valid(piteratorunpack_foreign, "byref")',
            '~$call_descriptors_valid(S_foreign)',
            # No native live refcounted replacement probe is executed. This
            # counterfactual keeps the graph valid and must fail admission.
            'S_changed = S[.STORE[n_raw] = DEFINED (POBJECT n_data)]',
            '$heap_valid($heap_graph(S_changed))',
            '$heap_owners($heap_graph(S_changed), HOBJECT n_payload) = 1',
            '~$iterator_unpack_hold_live(S_changed, piteratorunpack, "byref")',
            '~$call_descriptors_valid(S_changed)',
            *ONE, *FRESH,
            'S_after_budget = $drive_steps(S_one, 1)',
            'S_after = S_after_budget[.COMPLETION = NORMAL]',
            'S_after.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_empty) :: '
            '(ITERATOR_UNPACK piteratorunpack_next "next-start") :: ptask_tail*',
            'pdestructionrelease_empty = pdestructionrelease[.JOBS = eps]',
            '$heap_owners($heap_graph(S_after), HCELL n_raw) = 1',
            '$heap_owners($heap_graph(S_after), HOBJECT n_payload) = 2',
            'S_after.STORE = S_one.STORE', 'S_after.EVENTS = S.EVENTS',
            '$call_descriptors_valid(S_after)', '$heap_valid($heap_graph(S_after))',
            'S_ready_budget = $drive_steps(S_after, 1)',
            'S_ready = S_ready_budget[.COMPLETION = NORMAL]',
            'S_ready.TODO = (ITERATOR_UNPACK piteratorunpack_next "next-start") :: ptask_tail*',
        ],
    },
    'global-alias-survives-clearing-the-fresh-callee-cell': {
        'source': source('separate-alias'), 'stage': BODY_STAGE,
        'checks': [
            '$lookup(S.ENV, $ptascii("item")) = (n_private)',
            'S.STORE[n_private] = DEFINED PNULL', 'n_private <- S.REFCELLS',
            'S.GLOBALTABLE = (psymboltable_global)',
            '$lookup(psymboltable_global.ENV, $ptascii("alias")) = (n_raw)',
            'n_private =/= n_raw', 'n_raw <- S.REFCELLS',
            'S.STORE[n_raw] = DEFINED (POBJECT n_payload)',
            '$node_children(S, HCELL n_raw) = [HOBJECT n_payload]',
            '$heap_owners($heap_graph(S), HCELL n_raw) = 1',
            '$heap_owners($heap_graph(S), HCELL n_private) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_payload) = 1',
            'S.DESTRUCTION.CALLED = [n_data]', 'n_data =/= n_payload',
            '$object_name(S, n_data) = $ptascii("ReferenceIterator34")',
            '$heap_owners($heap_graph(S), HOBJECT n_data) = 0',
            '~(n_payload <- S.DESTRUCTION.CALLED)', *ADMISSION, *ZERO, *ONE,
            'S_one.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("F|")]',
            'S_one.STORE = S.STORE', *POST,
            'S_done = $drive(S, 4000)', 'S_done.COMPLETION = NORMAL',
            'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("F|"), OUTPUT $ptascii("HELD|"), '
            'OUTPUT $ptascii("O|"), OUTPUT $ptascii("E")]',
            'n_payload <- S_done.DESTRUCTION.CALLED',
            '$heap_owners($heap_graph(S_done), HCELL n_raw) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_payload) = 0',
            '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        ],
    },
    'warning-throw-retires-raw-cell-before-data-input-and-detached-object': {
        'source': source('warning-throw'), 'stage': ABORT_STAGE,
        'checks': [*abort_checks(), *ONE,
                   'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_next) :: '
                   '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*',
                   'pdestructionrelease_next.JOBS = [DESTRUCTION_VALUE (HOBJECT n_data), '
                   'DESTRUCTION_VALUE (HOBJECT n_data), DESTRUCTION_VALUE (HOBJECT n_payload)]',
                   '$heap_owners($heap_graph(S_one), HCELL n_raw) = 1',
                   '$heap_owners($heap_graph(S_one), HOBJECT n_payload) = 2',
                   'S_one.EVENTS = S.EVENTS', *POST],
    },
    'retired-source-authentication-does-not-read-dead-reference-contents': {
        'source': source('warning-throw'),
        'stage': (ABORT_STAGE + ' -- if piteratorunpack.SNAPSHOT = (POBJECT n_payload) '
                  '-- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_payload)]'),
        'checks': [
            *RAW, 'piteratorunpack.HOLD = KNOWN (POBJECT n_payload)',
            '$iterator_unpack_hold_valid(piteratorunpack, "byref")',
            '$heap_owners($heap_graph(S), HCELL n_raw) = 0',
            '$heap_owners($heap_graph(S), HOBJECT n_data) = 0',
            '$heap_owners($heap_graph(S), HOBJECT n_payload) = 1',
            'n_raw <- S.REFCELLS', '~((HCELL n_raw) <- S.ALLOCATIONS)',
            '$objectprops_record_at(S.OBJECTPROPS, n_data) = eps',
            'n_data <- S.DESTRUCTION.CALLED', '~(n_payload <- S.DESTRUCTION.CALLED)',
            '$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = [HOBJECT n_error]',
            '$eager_operation_source_valid(S, pdestructionoperation)',
            *ADMISSION, *ZERO,
            'S_erased = S[.STORE[n_raw] = UNDEFINED]',
            '$heap_graph(S_erased) = $heap_graph(S)',
            '$eager_operation_source_valid(S_erased, pdestructionoperation)',
            '$destructor_operation_valid(S_erased, pdestructionoperation)',
            '$call_descriptors_valid(S_erased)',
            'piteratorunpack_bad = piteratorunpack[.SNAPSHOT = (POBJECT n_data)]',
            'pdestructionoperation_bad = pdestructionoperation[.SOURCE = '
            'ITERATOR_UNPACK piteratorunpack_bad "byref"]',
            'S_bad = S[.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation_bad) :: ptask_tail*]',
            '$heap_graph(S_bad) = $heap_graph(S)',
            '~$eager_operation_source_valid(S_bad, pdestructionoperation_bad)',
            '~$call_descriptors_valid(S_bad)',
        ],
    },
    'parked-reference-warning-keeps-cell-and-payload-owners-distinct': {
        'source': source('parked-resume'), 'stage': PARKED_STAGE,
        'checks': [
            *RAW, *LIVE, *HELD,
            '$lookup(S.ENV, $ptascii("marker")) = (n_marker)',
            '$lookup(pfibervm.TABLE.ENV, $ptascii("marker")) = eps',
            'S.STORE[n_marker] = DEFINED (PINT 17)',
            '$heap_count(HCELL n_marker, $task_nodes(perrorcall.RESUME)) = 0',
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
            'pcallcontext_saved.LINE = 24', 'perrorcall.LINE = 24', *ADMISSION, *ZERO,
            'piteratorunpack_bad = piteratorunpack[.CALL = piteratorunpack.CALL[.LINE = 25]]',
            'perrorcall_bad = perrorcall[.LINE = 25]'
            '[.EVENT = DIAGNOSTIC "Warning" perrorcall.MESSAGE 25]'
            '[.RESUME = ITERATOR_UNPACK piteratorunpack_bad "byref"]',
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
            '$heap_owners($heap_graph(S_duplicate), HCELL n_raw) = 3',
            '$heap_owners($heap_graph(S_duplicate), HOBJECT n_payload) = 3',
            '$heap_owners($heap_graph(S_duplicate), HOBJECT n_data) = 4',
            '~$fiber_vm_valid(S_duplicate, pfibervm_duplicate, (n_fiber), eps)',
            '~$call_descriptors_valid(S_duplicate)',
        ],
    },
    'resumed-reference-warning-transfers-the-same-payload-to-a-fresh-cell': {
        'source': source('parked-resume'),
        'stage': 'S.TODO = (ITERATOR_UNPACK piteratorunpack "byref") :: ptask_tail*',
        'checks': [*RAW, *LIVE, *HELD, *ACTIVE,
                   'S.ACTIVEFIBER = (n_fiber)', 'S.GLOBALTABLE = (psymboltable_global)',
                   '$lookup(psymboltable_global.ENV, $ptascii("marker")) = (n_marker)',
                   'S.STORE[n_marker] = DEFINED (PINT 17)',
                   '$unpack_line(S, piteratorunpack.CALL) = 24',
                   *ADMISSION, *ZERO, *ONE, *FRESH],
    },
    'injected-reference-warning-retires-iterator-before-held-object': {
        'source': source('parked-throw'), 'stage': ABORT_STAGE,
        'checks': [*abort_checks(), 'S.ACTIVEFIBER = (n_fiber)',
                   'S.GLOBALTABLE = (psymboltable_global)',
                   '$lookup(psymboltable_global.ENV, $ptascii("marker")) = (n_marker)',
                   'S.STORE[n_marker] = DEFINED (PINT 17)',
                   '$lookup(psymboltable_global.ENV, $ptascii("failure")) = (n_failure)',
                   'S.STORE[n_failure] = DEFINED (POBJECT n_error)',
                   '$unpack_line(S, piteratorunpack.CALL) = 24'],
    },
    'fresh-argument-clearing-destroys-unaliased-object-before-F': {
        'source': source('normal'), 'stage': BODY_STAGE,
        'checks': [
            '$lookup(S.ENV, $ptascii("item")) = (n_private)',
            'S.STORE[n_private] = DEFINED PNULL', 'n_private <- S.REFCELLS',
            '$heap_owners($heap_graph(S), HCELL n_private) = 1',
            'S.DESTRUCTION.CALLED = [n_data, n_payload]', 'n_data =/= n_payload',
            '$object_name(S, n_data) = $ptascii("ReferenceIterator34")',
            '$object_name(S, n_payload) = $ptascii("ReferencePayload34")',
            '$heap_owners($heap_graph(S), HOBJECT n_data) = 0',
            '$heap_owners($heap_graph(S), HOBJECT n_payload) = 0',
            '~((HOBJECT n_payload) <- S.ALLOCATIONS)', *ADMISSION, *ZERO, *ONE,
            'S_one.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("F|")]',
            'S_one.STORE = S.STORE', *POST,
            'S_done = $drive(S, 4000)', 'S_done.COMPLETION = NORMAL',
            'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("F|"), OUTPUT $ptascii("E")]',
            'n_data <- S_done.DESTRUCTION.CALLED', 'n_payload <- S_done.DESTRUCTION.CALLED',
            '$heap_owners($heap_graph(S_done), HCELL n_private) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_payload) = 0',
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
    assert INPUT_BYTES == {p: p.read_bytes() for p in INPUT_BYTES}, 'reference-object review inputs changed'
    return passed


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if run(args.case) else 1)
