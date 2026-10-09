#!/usr/bin/env python3
"""Source-reached foreach NaN warnings, raw results and iterator owners."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import fiber_state_review as review

CATALOG = Path(__file__).with_name('foreach_valid_nan_cases.json')
INPUT_BYTES = {path: path.read_bytes() for path in (Path(__file__), Path(review.__file__), CATALOG)}
SOURCES = {row['id']: row['source'] for row in json.loads(INPUT_BYTES[CATALOG])}
ADMISSION = ['$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
POST = ['$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))']
ONE = ['S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
       'S_one = S_one_budget[.COMPLETION = NORMAL]']
ZERO = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S']
INITIAL = ['n_original = pforeachaggregate.AGGREGATE',
           'n_data = pforeachaggregate.OBJECT',
           'pforeachaggregate.INPUT = KNOWN (POBJECT n_original)',
           'pforeachaggregate.ACQUIRED = eps',
           'pforeachaggregate.ITERATOR = (n_cursor)',
           '$foreach_aggregate_site(S, pforeachaggregate.STATEMENT, '
           'pforeachaggregate.SITE, pforeachaggregate.LINE)']
RESUME = 'S.TODO = (FOREACH_AGGREGATE pforeachaggregate "valid-nan") :: ptask_tail*'
INVOKE = ('S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail* '
          '-- if perrorcall.RESUME = FOREACH_AGGREGATE pforeachaggregate "valid-nan"')
LATER = ('S.TODO = (USERITER_RESULT n_cursor n_data statement porigin_site z '
         '"valid-nan" poperand) :: ptask_tail*')
PARK = ('S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_main* '
        '-- if pconfigcall.KIND = INTRINSIC_FIBER_RESUME '
        '-- if pconfigcall.OWNER = (n_parent) '
        '-- if $fiber_at(S, n_parent) = (pfiber_parent) '
        '-- if pfiber_parent.VM = (pfibervm) '
        '-- if pfibervm.FRAMES = [pframe_warning, pframe_base] '
        '-- if pframe_warning.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_warning* '
        '-- if perrorcall.RESUME = FOREACH_AGGREGATE pforeachaggregate "valid-nan"')
PARK_VIEW = ['n_original = pforeachaggregate.AGGREGATE',
             'n_data = pforeachaggregate.OBJECT',
             'pforeachaggregate.ITERATOR = (n_cursor)',
             'pforeachaggregate.CURRENT = REFERENCE n_valid',
             'S_view = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_parent)]'
             '[.FIBERCALLERS = eps][.COMPLETION = NORMAL]',
             'S_scope = $constant_frame_scope(S_view, pframe_warning, [pframe_base])',
             '$error_call_valid(S_scope, perrorcall)']


CASES = {
    'initial-warning-dispatch-keeps-original-reference-and-both-owners': {
        'source': SOURCES['foreach-initial-nan-reference-handler'],
        'stage': ('S.TODO = (FOREACH_AGGREGATE pforeachaggregate "valid") :: ptask_tail* '
                  '-- if S.RESULT = REFERENCE n_valid'),
        'checks': [
            *INITIAL, 'pforeachaggregate.LINE = 23',
            'S.STORE[n_valid] = DEFINED (PFLOAT n_bits)',
            '$generator_from_nan(PFLOAT n_bits)',
            '$foreach_aggregate_result_valid(S, pforeachaggregate, "valid")',
            *ADMISSION, *ONE,
            'S_one.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
            'perrorcall.RESUME = FOREACH_AGGREGATE '
            'pforeachaggregate[.CURRENT = REFERENCE n_valid] "valid-nan"',
            'perrorcall.SITE = pforeachaggregate.SITE', 'perrorcall.LINE = 23',
            'perrorcall.LEVEL = 2',
            'perrorcall.MESSAGE = $ptascii("unexpected NAN value was coerced to bool")',
            'perrorcall.EVENT = DIAGNOSTIC "Warning" perrorcall.MESSAGE 23',
            '$error_call_valid(S_one, perrorcall)',
            '$foreach_aggregate_count(S_one.TODO, pforeachaggregate.SITE) = 1',
            '$useriter_task_ids(ERROR_HANDLER_INVOKE perrorcall) = [n_cursor]',
            '$error_task_iterator(ERROR_HANDLER_INVOKE perrorcall) = [n_cursor]',
            '$heap_count(HCELL n_valid, $task_nodes(perrorcall.RESUME)) = 1',
            '$heap_count(HOBJECT n_data, $task_nodes(perrorcall.RESUME)) = 1',
            '$heap_count(HOBJECT n_original, $task_nodes(perrorcall.RESUME)) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_data) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_original) = 1', *POST,
        ],
    },
    'initial-reference-handler-rereads-zero-before-empty-input-release': {
        'source': SOURCES['foreach-initial-nan-reference-handler'],
        'stage': RESUME,
        'checks': [
            *INITIAL, 'pforeachaggregate.LINE = 23',
            'pforeachaggregate.CURRENT = REFERENCE n_valid',
            'S.STORE[n_valid] = DEFINED (PFLOAT 0)',
            '$lookup(S.ENV, $ptascii("condition")) = (n_valid)',
            '$generator_from_valid_decision(S, pforeachaggregate.CURRENT) = (false)',
            '$foreach_aggregate_result_valid(S, pforeachaggregate, "valid-nan")',
            *ADMISSION, *ZERO, *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: '
            '(FOREACH_AGGREGATE pforeachaggregate_next "empty") :: ptask_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HCELL n_valid)]',
            'pdestructionrelease.CALLER = S.CURRENT',
            'pdestructionrelease.ORIGIN = (pforeachaggregate.SITE)',
            'pdestructionoperation.SOURCE = FOREACH_AGGREGATE pforeachaggregate "valid-nan"',
            'pdestructionoperation.CALLER = S.CURRENT',
            'pdestructionoperation.ORIGIN = (pforeachaggregate.SITE)',
            '$destructor_release_valid(S_one, pdestructionrelease)',
            '$destructor_operation_valid(S_one, pdestructionoperation)',
            '$heap_count(HCELL n_valid, $tasks_nodes(S_one.TODO)) = 1',
            'pforeachaggregate_next = pforeachaggregate[.CURRENT = KNOWN PNULL]',
            '$task_nodes(FOREACH_AGGREGATE pforeachaggregate_next "empty") = '
            '[HOBJECT n_data, HOBJECT n_original]',
            'S_one.RESULT = KNOWN PNULL', *POST,
        ],
    },
    'initial-copied-nan-survives-global-write-and-clears-before-current': {
        'source': SOURCES['foreach-initial-nan-value-handler'],
        'stage': RESUME,
        'checks': [
            *INITIAL, 'pforeachaggregate.LINE = 23',
            'pforeachaggregate.CURRENT = KNOWN (PFLOAT n_bits)',
            '$generator_from_nan(PFLOAT n_bits)',
            '$lookup(S.ENV, $ptascii("condition")) = (n_condition)',
            'S.STORE[n_condition] = DEFINED (PFLOAT 0)',
            '$generator_from_valid_decision(S, pforeachaggregate.CURRENT) = (true)',
            *ADMISSION, *ONE,
            'S_one.TODO = (FOREACH_AGGREGATE pforeachaggregate_next "ready") :: ptask_tail*',
            'pforeachaggregate_next = pforeachaggregate[.CURRENT = KNOWN PNULL]',
            '$task_nodes(FOREACH_AGGREGATE pforeachaggregate_next "ready") = '
            '[HOBJECT n_data, HOBJECT n_original]', *POST,
            'pforeachaggregate_bad = pforeachaggregate[.CURRENT = KNOWN (PFLOAT 0)]',
            'S_bad = S[.TODO = (FOREACH_AGGREGATE pforeachaggregate_bad "valid-nan") :: ptask_tail*]',
            '$heap_graph(S_bad) = $heap_graph(S)',
            '~$foreach_aggregate_result_valid(S_bad, pforeachaggregate_bad, "valid-nan")',
            '~$call_descriptors_valid(S_bad)',
        ],
    },
    'later-warning-dispatch-retains-raw-reference-and-one-cursor': {
        'source': SOURCES['foreach-later-nan-reference-handler'],
        'stage': ('S.TODO = (USERITER_RESULT n_cursor n_data statement porigin_site z '
                  '"valid" poperand) :: ptask_tail* -- if S.RESULT = REFERENCE n_valid '
                  '-- if S.STORE[n_valid] = DEFINED (PFLOAT n_bits) '
                  '-- if $generator_from_nan(PFLOAT n_bits)'),
        'checks': [
            'z = 19', 'poperand = KNOWN PNULL',
            '$useriter_result_valid(S, n_cursor, n_data, statement, porigin_site, z, "valid", poperand)',
            *ADMISSION, *ONE,
            'S_one.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
            'perrorcall.RESUME = USERITER_RESULT n_cursor n_data statement '
            'porigin_site z "valid-nan" (REFERENCE n_valid)',
            'perrorcall.LINE = 19', 'perrorcall.LEVEL = 2',
            'perrorcall.EVENT = DIAGNOSTIC "Warning" '
            '($ptascii("unexpected NAN value was coerced to bool")) 19',
            '$error_call_valid(S_one, perrorcall)',
            '$foreach_aggregate_count(S_one.TODO, porigin_site) = 0',
            '$useriter_task_ids(ERROR_HANDLER_INVOKE perrorcall) = [n_cursor]',
            '$heap_count(HCELL n_valid, $task_nodes(perrorcall.RESUME)) = 1',
            '$heap_count(HOBJECT n_data, $task_nodes(perrorcall.RESUME)) = 1', *POST,
        ],
    },
    'later-reference-false-removes-cursor-and-orders-raw-before-data': {
        'source': SOURCES['foreach-later-nan-reference-handler'],
        'stage': LATER,
        'checks': [
            'z = 19', 'poperand = REFERENCE n_valid',
            'S.STORE[n_valid] = DEFINED (PFLOAT 0)',
            '$lookup(S.ENV, $ptascii("condition")) = (n_valid)',
            '$generator_from_valid_decision(S, poperand) = (false)',
            '$useriter_result_valid(S, n_cursor, n_data, statement, porigin_site, z, "valid-nan", poperand)',
            *ADMISSION, *ONE,
            '$iterator_lookup(S_one.ITERATORS, n_cursor) = eps',
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HCELL n_valid), '
            'DESTRUCTION_VALUE (HOBJECT n_data)]',
            'pdestructionrelease.ORIGIN = (porigin_site)',
            '$destructor_release_valid(S_one, pdestructionrelease)',
            'S_one.RESULT = KNOWN PNULL', *POST,
        ],
    },
    'later-copied-nan-enters-real-current-without-input-owner': {
        'source': SOURCES['foreach-aggregate-later-valid-nan-required'],
        'stage': LATER,
        'checks': [
            'z = 21', 'poperand = KNOWN (PFLOAT n_bits)',
            '$generator_from_nan(PFLOAT n_bits)',
            '$generator_from_valid_decision(S, poperand) = (true)',
            '$foreach_aggregate_count(S.TODO, porigin_site) = 0',
            '$task_nodes(USERITER_RESULT n_cursor n_data statement '
            'porigin_site z "valid-nan" poperand) = [HOBJECT n_data]',
            *ADMISSION, *ONE,
            'S_one.TODO = (CALL_ARGS (METHOD_TARGET n_data porigin_current) eps 0 eps '
            '(porigin_site) z) :: (USERITER_RESULT n_cursor n_data statement '
            'porigin_site z "current" (KNOWN PNULL)) :: ptask_tail*',
            '$useriter_pending(S_one, METHOD_TARGET n_data porigin_current, porigin_site)',
            'S_one.RESULT = KNOWN PNULL', *POST,
        ],
    },
    'initial-warning-rejects-coherent-foreign-severity': {
        'source': SOURCES['foreach-initial-nan-reference-handler'],
        'stage': INVOKE,
        'checks': [
            '$error_call_valid(S, perrorcall)', *ADMISSION,
            'perrorcall_bad = perrorcall[.LEVEL = 8][.EVENT = '
            'DIAGNOSTIC "Notice" perrorcall.MESSAGE perrorcall.LINE]',
            'S_bad = S[.TODO = (ERROR_HANDLER_INVOKE perrorcall_bad) :: ptask_tail*]',
            '$heap_graph(S_bad) = $heap_graph(S)',
            '~$error_call_valid(S_bad, perrorcall_bad)',
            '~$call_task_valid(S_bad, ERROR_HANDLER_INVOKE perrorcall_bad)',
            '~$call_descriptors_valid(S_bad)',
        ],
    },
    'initial-warning-rejects-coordinated-line-and-resume-forgery': {
        'source': SOURCES['foreach-initial-nan-reference-handler'],
        'stage': INVOKE,
        'checks': [
            'pforeachaggregate.LINE = 23', '$error_call_valid(S, perrorcall)', *ADMISSION,
            'pforeachaggregate_bad = pforeachaggregate[.LINE = 24]',
            'perrorcall_bad = perrorcall[.LINE = 24][.EVENT = '
            'DIAGNOSTIC "Warning" perrorcall.MESSAGE 24][.RESUME = '
            'FOREACH_AGGREGATE pforeachaggregate_bad "valid-nan"]',
            'S_bad = S[.TODO = (ERROR_HANDLER_INVOKE perrorcall_bad) :: ptask_tail*]',
            '$heap_graph(S_bad) = $heap_graph(S)',
            '~$foreach_aggregate_result_valid(S_bad, pforeachaggregate_bad, "valid-nan")',
            '~$error_call_valid(S_bad, perrorcall_bad)',
            '~$call_descriptors_valid(S_bad)',
        ],
    },
    'initial-operational-clean-keeps-raw-data-input-and-one-cursor': {
        'source': SOURCES['foreach-initial-nan-handler-parks'],
        'stage': ('S.TODO = (ERROR_HANDLER_CLEAN perrorcall) :: ptask_tail* '
                  '-- if perrorcall.RESUME = FOREACH_AGGREGATE pforeachaggregate "valid-nan"'),
        'checks': [
            *INITIAL, '$destructor_operational(S)', 'pforeachaggregate.LINE = 25',
            'pforeachaggregate.CURRENT = REFERENCE n_valid',
            'S.STORE[n_valid] = DEFINED (PFLOAT 0)',
            '$error_cleanup_valid(S, perrorcall)',
            '$foreach_aggregate_count(S.TODO, pforeachaggregate.SITE) = 1',
            '$useriter_task_ids(ERROR_HANDLER_CLEAN perrorcall) = [n_cursor]',
            '$error_task_iterator(ERROR_HANDLER_CLEAN perrorcall) = [n_cursor]',
            '$heap_count(HCELL n_valid, $task_nodes(ERROR_HANDLER_CLEAN perrorcall)) = 1',
            '$heap_count(HOBJECT n_data, $task_nodes(ERROR_HANDLER_CLEAN perrorcall)) = 1',
            '$heap_count(HOBJECT n_original, $task_nodes(ERROR_HANDLER_CLEAN perrorcall)) = 1',
            *ADMISSION, *ONE,
            'S_one.TODO = (FOREACH_AGGREGATE pforeachaggregate "valid-nan") :: ptask_tail*',
            '$foreach_aggregate_result_valid(S_one, pforeachaggregate, "valid-nan")', *POST,
        ],
    },
    'later-operational-clean-keeps-reference-data-and-one-cursor': {
        'source': SOURCES['foreach-later-nan-reference-handler'],
        'stage': ('S.TODO = (ERROR_HANDLER_CLEAN perrorcall) :: ptask_tail* '
                  '-- if perrorcall.RESUME = USERITER_RESULT n_cursor n_data '
                  'statement porigin_site z "valid-nan" poperand'),
        'checks': [
            '$destructor_operational(S)', 'z = 19', 'poperand = REFERENCE n_valid',
            'S.STORE[n_valid] = DEFINED (PFLOAT 0)',
            '$error_cleanup_valid(S, perrorcall)',
            '$useriter_task_ids(ERROR_HANDLER_CLEAN perrorcall) = [n_cursor]',
            '$error_task_iterator(ERROR_HANDLER_CLEAN perrorcall) = [n_cursor]',
            '$heap_count(HCELL n_valid, $task_nodes(ERROR_HANDLER_CLEAN perrorcall)) = 1',
            '$heap_count(HOBJECT n_data, $task_nodes(ERROR_HANDLER_CLEAN perrorcall)) = 1',
            *ADMISSION, *ONE,
            'S_one.TODO = (USERITER_RESULT n_cursor n_data statement porigin_site z '
            '"valid-nan" poperand) :: ptask_tail*', *POST,
        ],
    },
    'parked-handler-retains-real-reference-data-input-and-cursor': {
        'source': SOURCES['foreach-initial-nan-handler-parks'],
        'stage': PARK,
        'checks': [
            *PARK_VIEW, 'S.ACTIVEFIBER = eps', 'S.FIBERCALLERS = eps',
            'pfiber_parent.STATUS = FIBER_SUSPENDED', 'pforeachaggregate.LINE = 25',
            'pforeachaggregate.INPUT = KNOWN (POBJECT n_original)',
            'S.STORE[n_valid] = DEFINED (PFLOAT n_bits)', '$generator_from_nan(PFLOAT n_bits)',
            'pfibervm.CURRENT = (pcallcontext_handler)',
            'pcallcontext_handler.LINE = 25', 'pcallcontext_handler.CALLSITE = (pforeachaggregate.SITE)',
            '$useriter_frames_ids(pfibervm.FRAMES) = [n_cursor]',
            '$heap_count(HCELL n_valid, $task_nodes(perrorcall.RESUME)) = 1',
            '$heap_count(HOBJECT n_data, $task_nodes(perrorcall.RESUME)) = 1',
            '$heap_count(HOBJECT n_original, $task_nodes(perrorcall.RESUME)) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_data) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_original) = 1',
            '$fiber_vm_valid(S, pfibervm, (n_parent), eps)', *ADMISSION, *ZERO,
        ],
    },
    'parked-handler-rejects-coordinated-real-frame-line-forgery': {
        'source': SOURCES['foreach-initial-nan-handler-parks'],
        'stage': PARK,
        'checks': [
            *PARK_VIEW, 'pfibervm.CURRENT = (pcallcontext_handler)', *ADMISSION,
            'pforeachaggregate_bad = pforeachaggregate[.LINE = 26]',
            'perrorcall_bad = perrorcall[.LINE = 26][.EVENT = '
            'DIAGNOSTIC "Warning" perrorcall.MESSAGE 26][.RESUME = '
            'FOREACH_AGGREGATE pforeachaggregate_bad "valid-nan"]',
            'pframe_bad = pframe_warning[.TODO = '
            '(ERROR_HANDLER_RESULT perrorcall_bad) :: ptask_warning*]',
            'pfibervm_bad = pfibervm[.CURRENT = (pcallcontext_handler[.LINE = 26])]'
            '[.FRAMES = [pframe_bad, pframe_base]]',
            'S_bad = S[.OBJECTS[n_parent] = FIBER pfiber_parent[.VM = (pfibervm_bad)]]',
            '$heap_graph(S_bad) = $heap_graph(S)',
            'S_scope_bad = S_scope[.TODO = pframe_bad.TODO]',
            '~$error_call_valid(S_scope_bad, perrorcall_bad)',
            '~$fiber_vm_valid(S_bad, pfibervm_bad, (n_parent), eps)',
            '~$call_descriptors_valid(S_bad)',
        ],
    },
    'parked-handler-rejects-duplicate-marker-and-cursor-in-real-frame': {
        'source': SOURCES['foreach-initial-nan-handler-parks'],
        'stage': PARK,
        'checks': [
            *PARK_VIEW, *ADMISSION,
            'pframe_duplicate = pframe_warning[.TODO = (ERROR_HANDLER_RESULT perrorcall) :: '
            '(ERROR_HANDLER_RESULT perrorcall) :: ptask_warning*]',
            'pfibervm_duplicate = pfibervm[.FRAMES = [pframe_duplicate, pframe_base]]',
            'S_duplicate = S[.OBJECTS[n_parent] = '
            'FIBER pfiber_parent[.VM = (pfibervm_duplicate)]]',
            '$foreach_aggregate_count(pframe_duplicate.TODO, pforeachaggregate.SITE) = 2',
            '$useriter_tasks_ids(pframe_duplicate.TODO) = [n_cursor, n_cursor]',
            'S_scope_duplicate = S_scope[.TODO = pframe_duplicate.TODO]',
            '~$error_call_valid(S_scope_duplicate, perrorcall)',
            '$heap_valid($heap_graph(S_duplicate))',
            '$heap_owners($heap_graph(S_duplicate), HOBJECT n_data) = '
            '$($heap_owners($heap_graph(S), HOBJECT n_data) + 1)',
            '$heap_owners($heap_graph(S_duplicate), HOBJECT n_original) = '
            '$($heap_owners($heap_graph(S), HOBJECT n_original) + 1)',
            '~$fiber_vm_valid(S_duplicate, pfibervm_duplicate, (n_parent), eps)',
            '~$call_descriptors_valid(S_duplicate)',
        ],
    },
    'initial-thrown-handler-discards-cursor-and-retains-raw-data-input': {
        'source': SOURCES['foreach-initial-nan-handler-throws'],
        'stage': ('S.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall) :: '
                  'ptask_tail* -- if S.CURRENT = eps -- if perrorcall.RESUME = '
                  'FOREACH_AGGREGATE pforeachaggregate "valid-nan"'),
        'checks': [
            *INITIAL, 'pforeachaggregate.LINE = 22',
            'pforeachaggregate.CURRENT = REFERENCE n_valid',
            '$lookup(S.ENV, $ptascii("failure")) = (n_failure)',
            'S.STORE[n_failure] = DEFINED (POBJECT n_error)',
            '$error_call_valid(S, perrorcall)', *ADMISSION, *ONE,
            '$iterator_lookup(S_one.ITERATORS, n_cursor) = eps',
            '$heap_count(HCELL n_valid, $tasks_nodes(S_one.TODO)) = 1',
            '$heap_count(HOBJECT n_data, $tasks_nodes(S_one.TODO)) = 1',
            '$heap_count(HOBJECT n_original, $tasks_nodes(S_one.TODO)) = 1', *POST,
        ],
    },
    'initial-thrown-handler-reaches-ordered-raw-data-input-release': {
        'source': SOURCES['foreach-initial-nan-handler-throws'],
        'stage': ('S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
                  '(THROW_SEARCH n_error) :: ptask_tail* -- if pdestructionrelease.JOBS = '
                  '[DESTRUCTION_VALUE (HCELL n_valid), DESTRUCTION_VALUE (HOBJECT n_data), '
                  'DESTRUCTION_VALUE (HOBJECT n_original)]'),
        'checks': [
            '$lookup(S.ENV, $ptascii("failure")) = (n_failure)',
            'S.STORE[n_failure] = DEFINED (POBJECT n_error)',
            'pdestructionrelease.CALLER = eps',
            'pdestructionrelease.ORIGIN = (porigin_site)',
            '$origin_node(S.SOURCES, porigin_site) = (statement)',
            '$foreach_aggregate_site(S, statement, porigin_site, 22)',
            'S.ITERATORS = eps', '$destructor_release_valid(S, pdestructionrelease)',
            '~(n_data <- S.DESTRUCTION.CALLED)', '~(n_original <- S.DESTRUCTION.CALLED)',
            '$heap_count(HOBJECT n_data, $tasks_nodes(S.TODO)) = 1',
            '$heap_count(HOBJECT n_original, $tasks_nodes(S.TODO)) = 1', *ADMISSION,
        ],
    },
    'later-thrown-handler-discards-cursor-and-retains-raw-and-data': {
        'source': SOURCES['foreach-later-nan-handler-throws'],
        'stage': ('S.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall) :: '
                  'ptask_tail* -- if S.CURRENT = eps -- if perrorcall.RESUME = USERITER_RESULT '
                  'n_cursor n_data statement porigin_site z "valid-nan" poperand'),
        'checks': [
            'z = 19', 'poperand = REFERENCE n_valid',
            '$lookup(S.ENV, $ptascii("failure")) = (n_failure)',
            'S.STORE[n_failure] = DEFINED (POBJECT n_error)',
            '$error_call_valid(S, perrorcall)', *ADMISSION, *ONE,
            '$iterator_lookup(S_one.ITERATORS, n_cursor) = eps',
            '$heap_count(HCELL n_valid, $tasks_nodes(S_one.TODO)) = 1',
            '$heap_count(HOBJECT n_data, $tasks_nodes(S_one.TODO)) = 1', *POST,
        ],
    },
    'later-thrown-handler-reaches-ordered-raw-and-data-release': {
        'source': SOURCES['foreach-later-nan-handler-throws'],
        'stage': ('S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
                  '(THROW_SEARCH n_error) :: ptask_tail* -- if pdestructionrelease.JOBS = '
                  '[DESTRUCTION_VALUE (HCELL n_valid), DESTRUCTION_VALUE (HOBJECT n_data)]'),
        'checks': [
            '$lookup(S.ENV, $ptascii("failure")) = (n_failure)',
            'S.STORE[n_failure] = DEFINED (POBJECT n_error)',
            'pdestructionrelease.CALLER = eps',
            'pdestructionrelease.ORIGIN = (porigin_site)',
            '$origin_node(S.SOURCES, porigin_site) = (statement)',
            '$useriter_site(S, statement, porigin_site, 19)',
            'S.ITERATORS = eps', '$destructor_release_valid(S, pdestructionrelease)',
            '~(n_data <- S.DESTRUCTION.CALLED)',
            '$heap_count(HCELL n_valid, $tasks_nodes(S.TODO)) = 1',
            '$heap_count(HOBJECT n_data, $tasks_nodes(S.TODO)) = 1', *ADMISSION,
        ],
    },
    'default-warning-resumes-directly-with-copied-nan-and-both-owners': {
        'source': SOURCES['foreach-initial-nan-default-warning'],
        'stage': RESUME,
        'checks': [
            *INITIAL, 'pforeachaggregate.LINE = 16', 'S.ERRORHANDLER.CALLBACK = eps',
            'pforeachaggregate.CURRENT = KNOWN (PFLOAT n_bits)',
            '$generator_from_nan(PFLOAT n_bits)',
            '$generator_from_valid_decision(S, pforeachaggregate.CURRENT) = (true)',
            '$foreach_aggregate_count(S.TODO, pforeachaggregate.SITE) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_data) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_original) = 1',
            *ADMISSION, *ONE,
            'S_one.TODO = (FOREACH_AGGREGATE pforeachaggregate_next "ready") :: ptask_tail*',
            'pforeachaggregate_next = pforeachaggregate[.CURRENT = KNOWN PNULL]', *POST,
        ],
    },
}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=CASES)
    args = parser.parse_args()
    review.ROOT = ROOT
    review.CASES = CASES
    passed = True
    for name in args.case or list(CASES):
        passed = review.run([name])
        assert all(path.read_bytes() == data for path, data in INPUT_BYTES.items()), \
            'foreach valid NaN review inputs changed during run'
        if not passed:
            break
    raise SystemExit(0 if passed else 1)
