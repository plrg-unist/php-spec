#!/usr/bin/env python3
"""Source-reached NaN valid() ownership, warning authority and unwind checks."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import fiber_state_review as review

CATALOG = Path(__file__).with_name('fiber_start_nan_cases.json')
SOURCE_BYTES = CATALOG.read_bytes()
SOURCES = {row['id']: row['source'] for row in json.loads(SOURCE_BYTES)}
ADMISSION = ['$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
ZERO = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S']
ONE = ['S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
       'S_one = S_one_budget[.COMPLETION = NORMAL]']
HEADER = ['pfiberstart = pfibertraversal.START', 'n_pack = pfibertraversal.OBJECT',
          'S.OBJECTS[pfiberstart.OBJECT] = FIBER pfiber_target',
          'pfiber_target.STATUS = FIBER_INIT',
          'pfibertraversal.SENT = {SLOTS eps, NAMED eps}',
          'pfibertraversal.ITEMS = eps']
RESUME = 'S.TODO = (FIBER_TRAVERSE_RESULT pfibertraversal "valid-nan") :: ptask_tail*'
PARK = ('S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_main* '
        '-- if pconfigcall.KIND = INTRINSIC_FIBER_RESUME '
        '-- if pconfigcall.OWNER = (n_parent) '
        '-- if $fiber_at(S, n_parent) = (pfiber_parent) '
        '-- if pfiber_parent.VM = (pfibervm) '
        '-- if pfibervm.FRAMES = [pframe_unpack, pframe_base] '
        '-- if pframe_unpack.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_unpack* '
        '-- if perrorcall.RESUME = FIBER_TRAVERSE_RESULT pfibertraversal "valid-nan"')
PARK_VIEW = ['S_view = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_parent)]'
             '[.FIBERCALLERS = eps][.COMPLETION = NORMAL]',
             'S_scope = $constant_frame_scope(S_view, pframe_unpack, [pframe_base])',
             '$error_call_valid(S_scope, perrorcall)']


def parked_mutation(expression):
    return [
        f'perrorcall_bad = {expression}',
        'pframe_bad = pframe_unpack[.TODO = '
        '(ERROR_HANDLER_RESULT perrorcall_bad) :: ptask_unpack*]',
        'pfibervm_bad = pfibervm[.FRAMES = [pframe_bad, pframe_base]]',
        'S_bad = S[.OBJECTS[n_parent] = FIBER pfiber_parent[.VM = (pfibervm_bad)]]',
        '$heap_graph(S_bad) = $heap_graph(S)',
        'S_scope_bad = S_scope[.TODO = pframe_bad.TODO]',
        '~$error_call_valid(S_scope_bad, perrorcall_bad)',
        '~$call_task_valid(S_scope_bad, ERROR_HANDLER_RESULT perrorcall_bad)',
        '~$fiber_vm_valid(S_bad, pfibervm_bad, (n_parent), eps)',
        '~$call_descriptors_valid(S_bad)',
    ]


CASES = {
    'nan-reference-handler-rereads-float-zero': {
        'source': SOURCES['iterator-valid-nan-reference-handler'],
        'stage': RESUME,
        'checks': [
            *HEADER, 'pfibertraversal.LINE = 23',
            'pfibertraversal.CURRENT = REFERENCE n_valid',
            'S.STORE[n_valid] = DEFINED (PFLOAT 0)',
            '$objectprops_at(S.OBJECTPROPS, n_pack) = (ppropertyslot*)',
            '$property_slot_at(ppropertyslot*, $ptascii("more")) = (ppropertyslot_more)',
            'ppropertyslot_more.STATE = PROP_VALUE (ALIAS n_valid)',
            '$fiber_traversal_result_valid(S, pfibertraversal, "valid-nan")',
            '$generator_from_valid_decision(S, pfibertraversal.CURRENT) = (false)',
            '$heap_count(HCELL n_valid, $task_nodes('
            'FIBER_TRAVERSE_RESULT pfibertraversal "valid-nan")) = 1',
            *ADMISSION, *ZERO, *ONE,
            'S_one.TODO = (FIBER_ARGS pfiberstart_next) :: ptask_tail*',
            'pfiberstart_next.INDEX = $(pfiberstart.INDEX + 1)',
            'pfiberstart_next.SENT = pfibertraversal.SENT',
            'pfiberstart_next.PACKS = [FIBER_TRAVERSABLE_PACK ptraversablepack]',
            'ptraversablepack.OBJECT = n_pack', 'ptraversablepack.ITEMS = eps',
            'S_one.RESULT = KNOWN PNULL',
            '$call_task_valid(S_one, FIBER_ARGS pfiberstart_next)',
        ],
    },
    'nan-value-handler-keeps-copied-nan-and-clears-raw-before-current': {
        'source': SOURCES['iterator-valid-nan-value-handler'],
        'stage': RESUME,
        'checks': [
            *HEADER, 'pfibertraversal.LINE = 23',
            'pfibertraversal.CURRENT = KNOWN (PFLOAT n_bits)',
            '$generator_from_nan(PFLOAT n_bits)',
            '$objectprops_at(S.OBJECTPROPS, n_pack) = (ppropertyslot*)',
            '$property_slot_at(ppropertyslot*, $ptascii("more")) = (ppropertyslot_more)',
            'ppropertyslot_more.STATE = PROP_VALUE (DIRECT (PFLOAT 0))',
            '$generator_from_valid_decision(S, pfibertraversal.CURRENT) = (true)',
            '$fiber_traversal_result_valid(S, pfibertraversal, "valid-nan")',
            *ADMISSION, *ONE,
            'S_one.TODO = (CALL_ARGS (METHOD_TARGET n_pack porigin_current) '
            'eps 0 eps (pfiberstart.SITE) 23) :: '
            '(FIBER_TRAVERSE_RESULT pfibertraversal_next "current") :: ptask_tail*',
            'pfibertraversal_next = pfibertraversal[.CURRENT = KNOWN PNULL]',
            '$fiber_traversal_pending(S_one, METHOD_TARGET n_pack porigin_current, pfiberstart.SITE)',
            'pfibertraversal_bad = pfibertraversal[.CURRENT = KNOWN (PFLOAT 0)]',
            'S_bad = S[.TODO = (FIBER_TRAVERSE_RESULT pfibertraversal_bad "valid-nan") :: ptask_tail*]',
            '$heap_graph(S_bad) = $heap_graph(S)',
            '~$fiber_traversal_result_valid(S_bad, pfibertraversal_bad, "valid-nan")',
            '~$call_descriptors_valid(S_bad)',
        ],
    },
    'nan-warning-invoke-authenticates-level-line-event': {
        'source': SOURCES['iterator-valid-nan-reference-handler'],
        'stage': ('S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail* '
                  '-- if perrorcall.RESUME = '
                  'FIBER_TRAVERSE_RESULT pfibertraversal "valid-nan"'),
        'checks': [
            *HEADER, 'perrorcall.SITE = pfiberstart.SITE',
            'perrorcall.LEVEL = 2', 'perrorcall.LINE = 23',
            'perrorcall.MESSAGE = $ptascii("unexpected NAN value was coerced to bool")',
            'perrorcall.EVENT = DIAGNOSTIC "Warning" perrorcall.MESSAGE 23',
            '$fiber_start_unpack_count(S.TODO, pfibertraversal.CAPTURE, pfiberstart.SITE) = 1',
            '$fiber_start_unpack_project(S.TODO, pfibertraversal.CAPTURE, '
            'pfiberstart, pfiberstart) = (FIBER_ARGS pfiberstart) :: ptask_tail*',
            '$error_call_valid(S, perrorcall)', *ADMISSION,
            'perrorcall_level = perrorcall[.LEVEL = 512]',
            'S_level = S[.TODO = (ERROR_HANDLER_INVOKE perrorcall_level) :: ptask_tail*]',
            '$heap_graph(S_level) = $heap_graph(S)',
            '~$error_call_valid(S_level, perrorcall_level)',
            '~$call_task_valid(S_level, ERROR_HANDLER_INVOKE perrorcall_level)',
            '~$call_descriptors_valid(S_level)',
            'perrorcall_line = perrorcall[.LINE = 24][.EVENT = '
            'DIAGNOSTIC "Warning" perrorcall.MESSAGE 24]',
            'S_line = S[.TODO = (ERROR_HANDLER_INVOKE perrorcall_line) :: ptask_tail*]',
            '$heap_graph(S_line) = $heap_graph(S)',
            '~$error_call_valid(S_line, perrorcall_line)',
            'perrorcall_event = perrorcall[.EVENT = DIAGNOSTIC "Notice" perrorcall.MESSAGE 23]',
            'S_event = S[.TODO = (ERROR_HANDLER_INVOKE perrorcall_event) :: ptask_tail*]',
            '$heap_graph(S_event) = $heap_graph(S)',
            '~$error_call_valid(S_event, perrorcall_event)',
        ],
    },
    'nan-parked-handler-keeps-reference-and-iterator-data-after-cv-null': {
        'source': SOURCES['iterator-valid-nan-reference-handler-parks'],
        'stage': PARK,
        'checks': [
            *HEADER, 'S.ACTIVEFIBER = eps', 'S.FIBERCALLERS = eps',
            'pfiber_parent.STATUS = FIBER_SUSPENDED',
            'pfibervm.TODO = (FIBER_CONTINUE pfiberapi) :: ptask_handler*',
            'pfiberapi.KIND = (INTRINSIC_FIBER_SUSPEND)',
            'pfiberapi.SENT = (PSTRING ($ptascii("pause")))',
            'pfibertraversal.LINE = 26',
            'pfibertraversal.INPUT = VARIABLE ($ptascii("pack")) z_input',
            '$operand_nodes(pfibertraversal.INPUT) = eps',
            'pfibertraversal.CURRENT = REFERENCE n_valid',
            'S.STORE[n_valid] = DEFINED (PFLOAT 0)',
            'psymboltable_global = $fiber_globals(S)',
            '$lookup(psymboltable_global.ENV, $ptascii("pack")) = (n_pack_cell)',
            'S.STORE[n_pack_cell] = DEFINED PNULL',
            '$lookup(psymboltable_global.ENV, $ptascii("more")) = (n_valid)',
            '$heap_count(HCELL n_valid, $task_nodes(perrorcall.RESUME)) = 1',
            '$heap_count(HOBJECT n_pack, $task_nodes(perrorcall.RESUME)) = 1',
            '(HOBJECT n_pack) <- S.ALLOCATIONS', '(HCELL n_valid) <- S.ALLOCATIONS',
            *PARK_VIEW, *ADMISSION, *ZERO,
        ],
    },
    'nan-parked-warning-rejects-changed-line-on-same-heap': {
        'source': SOURCES['iterator-valid-nan-reference-handler-parks'],
        'stage': PARK,
        'checks': [*PARK_VIEW, *ADMISSION, *parked_mutation(
            'perrorcall[.LINE = $(perrorcall.LINE + 1)][.EVENT = '
            'DIAGNOSTIC "Warning" perrorcall.MESSAGE $(perrorcall.LINE + 1)]')],
    },
    'nan-parked-warning-rejects-duplicate-start-in-real-frame': {
        'source': SOURCES['iterator-valid-nan-reference-handler-parks'],
        'stage': PARK,
        'checks': [
            *PARK_VIEW, *ADMISSION,
            'pframe_duplicate = pframe_unpack[.TODO = '
            '(ERROR_HANDLER_RESULT perrorcall) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_unpack*]',
            'pfibervm_duplicate = pfibervm[.FRAMES = [pframe_duplicate, pframe_base]]',
            'S_duplicate = S[.OBJECTS[n_parent] = '
            'FIBER pfiber_parent[.VM = (pfibervm_duplicate)]]',
            '$fiber_start_unpack_count(pframe_duplicate.TODO, pfibertraversal.CAPTURE, '
            'pfibertraversal.START.SITE) = 2',
            'S_scope_duplicate = S_scope[.TODO = pframe_duplicate.TODO]',
            '~$error_call_valid(S_scope_duplicate, perrorcall)',
            '$heap_valid($heap_graph(S_duplicate))',
            '$heap_owners($heap_graph(S_duplicate), HOBJECT pfibertraversal.OBJECT) = '
            '$($heap_owners($heap_graph(S), HOBJECT pfibertraversal.OBJECT) + 1)',
            '~$fiber_vm_valid(S_duplicate, pfibervm_duplicate, (n_parent), eps)',
            '~$call_descriptors_valid(S_duplicate)',
        ],
    },
    'nan-operational-handler-clean-keeps-one-start-and-raw-reference': {
        'source': SOURCES['iterator-valid-nan-reference-handler-parks'],
        'stage': ('S.TODO = (ERROR_HANDLER_CLEAN perrorcall) :: ptask_tail* '
                  '-- if perrorcall.RESUME = '
                  'FIBER_TRAVERSE_RESULT pfibertraversal "valid-nan"'),
        'checks': [
            *HEADER, '$destructor_operational(S)', 'pfibertraversal.LINE = 26',
            'pfibertraversal.CURRENT = REFERENCE n_valid',
            'S.STORE[n_valid] = DEFINED (PFLOAT 0)',
            '$error_call_valid(S, perrorcall)', '$error_cleanup_valid(S, perrorcall)',
            '$fiber_start_unpack_count(S.TODO, pfibertraversal.CAPTURE, pfiberstart.SITE) = 1',
            '$fiber_start_unpack_project(S.TODO, pfibertraversal.CAPTURE, '
            'pfiberstart, pfiberstart) = (FIBER_ARGS pfiberstart) :: ptask_tail*',
            '$heap_count(HCELL n_valid, $task_nodes(ERROR_HANDLER_CLEAN perrorcall)) = 1',
            *ADMISSION, *ONE,
            'S_one.TODO = (FIBER_TRAVERSE_RESULT pfibertraversal "valid-nan") :: ptask_tail*',
            '$fiber_traversal_result_valid(S_one, pfibertraversal, "valid-nan")',
        ],
    },
    'nan-thrown-handler-releases-raw-result-data-temp-before-direct-capture': {
        'source': SOURCES['iterator-valid-nan-reference-handler-throws'],
        'stage': ('S.TODO = (THROW_SEARCH n_error) :: '
                  '(ERROR_HANDLER_RESULT perrorcall) :: ptask_tail* '
                  '-- if S.CURRENT = eps '
                  '-- if perrorcall.RESUME = '
                  'FIBER_TRAVERSE_RESULT pfibertraversal "valid-nan"'),
        'checks': [
            *HEADER, 'S.FRAMES = eps', '$destructor_operational(S)',
            'pfibertraversal.LINE = 22', 'pfibertraversal.CAPTURE = (n_capture)',
            '~$exit_method_site(S, pfiberstart.SITE)',
            'pfibertraversal.INPUT = KNOWN (POBJECT n_pack)',
            'pfibertraversal.CURRENT = REFERENCE n_valid',
            '$lookup(S.ENV, $ptascii("original")) = (n_original)',
            'S.STORE[n_original] = DEFINED (POBJECT n_error)',
            '$error_call_valid(S, perrorcall)', *ADMISSION, *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_handler) :: '
            '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation_handler) :: '
            '(DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(THROW_SEARCH n_error) :: ptask_tail*',
            'pdestructionrelease_handler.JOBS = $destruction_values($error_selected_roots(perrorcall.TARGET))',
            'pdestructionoperation_handler.SOURCE = THROW_SEARCH n_error',
            'S_one.DESTRUCTION.RELEASES = [pdestructionrelease_handler, pdestructionrelease]',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HCELL n_valid), '
            'DESTRUCTION_VALUE (HOBJECT n_pack), DESTRUCTION_VALUE (HOBJECT n_pack)]',
            'pdestructionrelease.CALLER = eps',
            'pdestructionrelease.ORIGIN = (pfiberstart.SITE)',
            'S_one.OBJECTS[pfiberstart.OBJECT] = FIBER pfiber_target',
            '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
        ],
    },
}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=CASES)
    args = parser.parse_args()
    review.ROOT = ROOT
    review.CASES = CASES
    review.__file__ = str(Path(__file__).resolve())
    passed = review.run(args.case or list(CASES))
    assert CATALOG.read_bytes() == SOURCE_BYTES, 'NaN START originals changed during run'
    raise SystemExit(0 if passed else 1)
