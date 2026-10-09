#!/usr/bin/env python3
"""Source-reached acquired Iterator NaN warnings and generic-mode ownership."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import fiber_state_review as review

CATALOG = Path(__file__).with_name('yield_from_valid_nan_cases.json')
INPUT_BYTES = {path: path.read_bytes() for path in (Path(__file__), Path(review.__file__), CATALOG)}
SOURCES = {row['id']: row['source'] for row in json.loads(INPUT_BYTES[CATALOG])}
ADMISSION = ['$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
POST = ['$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))']
ONE = ['S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
       'S_one = S_one_budget[.COMPLETION = NORMAL]']
ZERO = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S']
HEADER = ['S.OBJECTS[n_parent] = GENERATOR pgenerator_parent',
          'pgenerator_parent.PHASE = GENERATOR_RUNNING',
          'pgenerator_parent.DELEGATE = (pgeneratorfrom)',
          'pgeneratorfrom.ACQUISITION = (pyieldfromreceipt)',
          'pgeneratorfrom.SITE = pyieldfromreceipt.SITE',
          'pgeneratorfrom.INPUT = (POBJECT n_data)',
          '$useriter_instance(S, n_data)',
          'n_original = pyieldfromreceipt.AGGREGATE',
          'n_original <- S.DESTRUCTION.CALLED',
          '$heap_owners($heap_graph(S), HOBJECT n_original) = 0',
          '$heap_owners($heap_graph(S), HOBJECT n_data) = 1',
          'S.YIELDRETAINED = eps',
          '$yield_from_receipt_valid(S, pyieldfromreceipt)']
RESUME = ('S.TODO = (YIELD_FROM_ITERATOR_VALID n_parent pyieldfromreceipt poperand) :: '
          'ptask_tail*')
INVOKE = ('S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail* '
          '-- if perrorcall.RESUME = YIELD_FROM_ITERATOR_VALID '
          'n_parent pyieldfromreceipt poperand')
RAW_VALID = ('S.TODO = (GENERATOR_FROM_CALLBACK n_parent porigin "valid") :: ptask_tail* '
             '-- if S.OBJECTS[n_parent] = GENERATOR pgenerator_parent '
             '-- if pgenerator_parent.DELEGATE = (pgeneratorfrom) '
             '-- if pgeneratorfrom.ACQUISITION = (pyieldfromreceipt)')
PARK = ('S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_main* '
        '-- if pconfigcall.KIND = INTRINSIC_FIBER_RESUME '
        '-- if pconfigcall.OWNER = (n_fiber) '
        '-- if $fiber_at(S, n_fiber) = (pfiber) '
        '-- if pfiber.VM = (pfibervm) '
        '-- if pfibervm.FRAMES = pframe_handler :: pframe_tail* '
        '-- if pframe_handler.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_handler* '
        '-- if perrorcall.RESUME = YIELD_FROM_ITERATOR_VALID '
        'n_parent pyieldfromreceipt poperand')
PARK_VIEW = ['S_view = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)]'
             '[.FIBERCALLERS = eps][.COMPLETION = NORMAL]',
             'S_scope = $api_saved_frame_scope('
             '$constant_frame_scope(S_view, pframe_handler, pframe_tail*), '
             'pframe_handler, pframe_tail*)',
             'pfibervm.CURRENT = (pcallcontext_handler)',
             'pframe_handler.CONTEXT = (pcallcontext_parent)',
             'pcallcontext_parent.FUNCTION = pyieldfromreceipt.FUNCTION',
             'poperand = REFERENCE n_valid',
             'S.OBJECTS[n_parent] = GENERATOR pgenerator_parent',
             'pgenerator_parent.DELEGATE = (pgeneratorfrom)',
             'pgeneratorfrom.ACQUISITION = (pyieldfromreceipt)',
             'pgeneratorfrom.INPUT = (POBJECT n_data)',
             'pyieldfromreceipt.LINE = 26']
THROWN = ('S.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall) :: '
          'ptask_tail* -- if perrorcall.RESUME = YIELD_FROM_ITERATOR_VALID '
          'n_parent pyieldfromreceipt poperand -- if S.CURRENT = (pcallcontext_parent) '
          '-- if pcallcontext_parent.FUNCTION = pyieldfromreceipt.FUNCTION')
RELEASED = ('S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(THROW_SEARCH n_error) :: ptask_tail* -- if pdestructionrelease.JOBS = '
            '[DESTRUCTION_VALUE (HCELL n_valid), DESTRUCTION_VALUE (HOBJECT n_data)]')


CASES = {
    'initial-dispatch-keeps-raw-reference-receipt-and-one-data-owner': {
        'source': SOURCES['yield-from-acquired-initial-nan-reference'],
        'stage': RAW_VALID + ' -- if S.RESULT = REFERENCE n_valid',
        'checks': [
            *HEADER, 'pgeneratorfrom.POSITION = 0', 'pyieldfromreceipt.LINE = 23',
            'S.STORE[n_valid] = DEFINED (PFLOAT n_bits)', '$generator_from_nan(PFLOAT n_bits)',
            'S.EVENTS = [OUTPUT $ptascii("G|"), OUTPUT $ptascii("A|"), '
            'OUTPUT $ptascii("W|"), OUTPUT $ptascii("V|")]', *ADMISSION, *ONE,
            'S_one.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
            'perrorcall.RESUME = YIELD_FROM_ITERATOR_VALID '
            'n_parent pyieldfromreceipt (REFERENCE n_valid)',
            'perrorcall.SITE = pyieldfromreceipt.SITE', 'perrorcall.LINE = 23',
            'perrorcall.LEVEL = 2',
            'perrorcall.MESSAGE = $ptascii("unexpected NAN value was coerced to bool")',
            'perrorcall.EVENT = DIAGNOSTIC "Warning" perrorcall.MESSAGE 23',
            '$error_call_valid(S_one, perrorcall)',
            '$generator_from_claims(S_one.TODO) = [n_parent]',
            '$task_nodes(perrorcall.RESUME) = [HCELL n_valid]',
            '$heap_owners($heap_graph(S_one), HOBJECT n_data) = 1',
            'S_one.RESULT = KNOWN PNULL', *POST,
        ],
    },
    'default-warning-keeps-copied-nan-and-real-operand-line': {
        'source': SOURCES['yield-from-acquired-initial-nan-default-warning'],
        'stage': RAW_VALID + ' -- if S.RESULT = KNOWN (PFLOAT n_bits) '
        '-- if $generator_from_nan(PFLOAT n_bits)',
        'checks': [
            *HEADER, 'pyieldfromreceipt.LINE = 17', 'S.ERRORHANDLER.CALLBACK = eps',
            *ADMISSION, *ONE,
            'S_one.TODO = (YIELD_FROM_ITERATOR_VALID n_parent pyieldfromreceipt '
            '(KNOWN (PFLOAT n_bits))) :: ptask_tail*',
            'S_one.EVENTS = S.EVENTS ++ [DIAGNOSTIC "Warning" '
            '($ptascii("unexpected NAN value was coerced to bool")) 17]',
            '$generator_from_claims(S_one.TODO) = [n_parent]',
            '$task_nodes(YIELD_FROM_ITERATOR_VALID n_parent pyieldfromreceipt '
            '(KNOWN (PFLOAT n_bits))) = eps', *POST,
        ],
    },
    'initial-reference-zero-retires-raw-before-data-at-natural-end': {
        'source': SOURCES['yield-from-acquired-initial-nan-reference'],
        'stage': RESUME,
        'checks': [
            *HEADER, 'pyieldfromreceipt.LINE = 23', 'pgeneratorfrom.POSITION = 0',
            'poperand = REFERENCE n_valid', 'S.STORE[n_valid] = DEFINED (PFLOAT 0)',
            '$generator_from_valid_decision(S, poperand) = (false)',
            '$yield_from_iterator_valid_task(S, n_parent, pyieldfromreceipt, poperand)',
            *ADMISSION, *ZERO, *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HCELL n_valid), '
            'DESTRUCTION_VALUE (HOBJECT n_data)]',
            'pdestructionrelease.CALLER = S.CURRENT',
            'pdestructionrelease.ORIGIN = (pyieldfromreceipt.SITE)',
            'S_one.OBJECTS[n_parent] = GENERATOR pgenerator_parent'
            '[.DELEGATE = (pgeneratorfrom[.INPUT = eps])]',
            'S_one.RESULT = KNOWN PNULL', 'S_one.BASE = BASE_VALUE (KNOWN PNULL)',
            'S_one.YIELDRETAINED = eps',
            '$destructor_release_valid(S_one, pdestructionrelease)', *POST,
        ],
    },
    'initial-copied-nan-enters-current-after-handler-writes-zero': {
        'source': SOURCES['yield-from-acquired-initial-nan-value'],
        'stage': RESUME,
        'checks': [
            *HEADER, 'pyieldfromreceipt.LINE = 23', 'pgeneratorfrom.POSITION = 0',
            'poperand = KNOWN (PFLOAT n_bits)', '$generator_from_nan(PFLOAT n_bits)',
            'S.GLOBALTABLE = (psymboltable_global)',
            '$lookup(psymboltable_global.ENV, $ptascii("condition")) = (n_condition)',
            'S.STORE[n_condition] = DEFINED (PFLOAT 0)',
            '$generator_from_valid_decision(S, poperand) = (true)', *ADMISSION, *ONE,
            'S_one.TODO = (CALL_ARGS pcalltarget eps 0 eps (pyieldfromreceipt.SITE) 23) :: '
            '(GENERATOR_FROM_CALLBACK n_parent pyieldfromreceipt.SITE "current") :: ptask_tail*',
            '$generator_from_pending(S_one, pcalltarget, pyieldfromreceipt.SITE)',
            '$generator_from_claims(S_one.TODO) = [n_parent]',
            'S_one.RESULT = KNOWN PNULL', 'S_one.BASE = BASE_VALUE (KNOWN PNULL)', *POST,
        ],
    },
    'later-reference-zero-retires-raw-data-without-request-retention': {
        'source': SOURCES['yield-from-acquired-later-nan-reference'],
        'stage': RESUME,
        'checks': [
            *HEADER, 'pyieldfromreceipt.LINE = 24', 'pgeneratorfrom.POSITION = 1',
            'poperand = REFERENCE n_valid', 'S.STORE[n_valid] = DEFINED (PFLOAT 0)',
            '$generator_from_valid_decision(S, poperand) = (false)', *ADMISSION, *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HCELL n_valid), '
            'DESTRUCTION_VALUE (HOBJECT n_data)]',
            'S_one.OBJECTS[n_parent] = GENERATOR pgenerator_parent'
            '[.DELEGATE = (pgeneratorfrom[.INPUT = eps])]',
            'S_one.YIELDRETAINED = eps',
            '$destructor_release_valid(S_one, pdestructionrelease)', *POST,
        ],
    },
    'later-copied-nan-retains-generic-mode-before-second-current': {
        'source': SOURCES['yield-from-acquired-later-nan-value'],
        'stage': RESUME,
        'checks': [
            *HEADER, 'pyieldfromreceipt.LINE = 24', 'pgeneratorfrom.POSITION = 1',
            'poperand = KNOWN (PFLOAT n_bits)', '$generator_from_nan(PFLOAT n_bits)',
            '$generator_from_valid_decision(S, poperand) = (true)', *ADMISSION, *ONE,
            'S_one.TODO = (CALL_ARGS pcalltarget eps 0 eps (pyieldfromreceipt.SITE) 24) :: '
            '(GENERATOR_FROM_CALLBACK n_parent pyieldfromreceipt.SITE "current") :: ptask_tail*',
            '$generator_from_pending(S_one, pcalltarget, pyieldfromreceipt.SITE)',
            'S_one.OBJECTS[n_parent] = GENERATOR pgenerator_parent',
            'S_one.RESULT = KNOWN PNULL', *POST,
        ],
    },
    'reference-one-retires-numeric-raw-before-authentic-current-call': {
        'source': SOURCES['yield-from-acquired-initial-nan-reference-true'],
        'stage': RESUME,
        'checks': [
            *HEADER, 'pyieldfromreceipt.LINE = 23', 'pgeneratorfrom.POSITION = 0',
            'poperand = REFERENCE n_valid',
            'S.STORE[n_valid] = DEFINED (PFLOAT 4607182418800017408)',
            '$generator_from_valid_decision(S, poperand) = (true)',
            '$eager_explicit_task(YIELD_FROM_ITERATOR_VALID n_parent pyieldfromreceipt poperand)',
            *ADMISSION, *ONE,
            'S_one.TODO = (CALL_ARGS pcalltarget eps 0 eps (pyieldfromreceipt.SITE) 23) :: '
            '(GENERATOR_FROM_CALLBACK n_parent pyieldfromreceipt.SITE "current") :: ptask_tail*',
            '$generator_from_pending(S_one, pcalltarget, pyieldfromreceipt.SITE)',
            '$heap_count(HCELL n_valid, $tasks_nodes(S_one.TODO)) = 0',
            '$generator_from_claims(S_one.TODO) = [n_parent]',
            '$target_nodes(pcalltarget) = [HOBJECT n_data]',
            '$heap_count(HOBJECT n_data, $tasks_nodes(S_one.TODO)) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_data) = 2', *POST,
        ],
    },
    'operational-clean-keeps-one-parent-and-original-raw-reference': {
        'source': SOURCES['yield-from-acquired-initial-nan-reference'],
        'stage': ('S.TODO = (ERROR_HANDLER_CLEAN perrorcall) :: ptask_tail* '
                  '-- if perrorcall.RESUME = YIELD_FROM_ITERATOR_VALID '
                  'n_parent pyieldfromreceipt poperand'),
        'checks': [
            *HEADER, '$destructor_operational(S)', 'poperand = REFERENCE n_valid',
            'S.STORE[n_valid] = DEFINED (PFLOAT 0)',
            '$error_cleanup_valid(S, perrorcall)',
            '$generator_from_claim(ERROR_HANDLER_CLEAN perrorcall) = [n_parent]',
            '$generator_internal_task(ERROR_HANDLER_CLEAN perrorcall)',
            '$heap_count(HCELL n_valid, $task_nodes(ERROR_HANDLER_CLEAN perrorcall)) = 1',
            *ADMISSION, *ONE,
            'S_one.TODO = perrorcall.RESUME :: ptask_tail*',
            '$generator_from_claims(S_one.TODO) = [n_parent]', *POST,
        ],
    },
    'warning-rejects-coherent-wrong-severity': {
        'source': SOURCES['yield-from-acquired-initial-nan-reference'],
        'stage': INVOKE,
        'checks': [
            '$error_call_valid(S, perrorcall)', *ADMISSION,
            'perrorcall_bad = perrorcall[.LEVEL = 512]',
            'S_bad = S[.TODO = (ERROR_HANDLER_INVOKE perrorcall_bad) :: ptask_tail*]',
            '$heap_graph(S_bad) = $heap_graph(S)', '~$error_call_valid(S_bad, perrorcall_bad)',
            '~$call_descriptors_valid(S_bad)',
        ],
    },
    'warning-rejects-coordinated-receipt-and-packet-line-forgery': {
        'source': SOURCES['yield-from-acquired-initial-nan-reference'],
        'stage': INVOKE,
        'checks': [
            *HEADER, '$error_call_valid(S, perrorcall)', *ADMISSION,
            'pyieldfromreceipt_bad = pyieldfromreceipt[.LINE = 24]',
            'perrorcall_bad = perrorcall[.LINE = 24][.EVENT = DIAGNOSTIC "Warning" '
            'perrorcall.MESSAGE 24][.RESUME = YIELD_FROM_ITERATOR_VALID '
            'n_parent pyieldfromreceipt_bad poperand]',
            'S_bad = S[.TODO = (ERROR_HANDLER_INVOKE perrorcall_bad) :: ptask_tail*]'
            '[.OBJECTS[n_parent] = GENERATOR pgenerator_parent'
            '[.DELEGATE = (pgeneratorfrom[.ACQUISITION = (pyieldfromreceipt_bad)])]]',
            '$heap_graph(S_bad) = $heap_graph(S)',
            '~$yield_from_receipt_valid(S_bad, pyieldfromreceipt_bad)',
            '~$error_call_valid(S_bad, perrorcall_bad)', '~$call_descriptors_valid(S_bad)',
        ],
    },
    'acquired-mode-rejects-substitution-of-old-direct-warning-marker': {
        'source': SOURCES['yield-from-acquired-initial-nan-reference'],
        'stage': RESUME,
        'checks': [
            '$yield_from_iterator_valid_task(S, n_parent, pyieldfromreceipt, poperand)',
            *ADMISSION,
            'ptask_bad = GENERATOR_FROM_VALID n_parent pyieldfromreceipt.SITE poperand',
            'S_bad = S[.TODO = ptask_bad :: ptask_tail*]',
            '$heap_graph(S_bad) = $heap_graph(S)',
            '~$generator_from_valid_task(S_bad, n_parent, pyieldfromreceipt.SITE, poperand)',
            '~$call_task_valid(S_bad, ptask_bad)', '~$call_descriptors_valid(S_bad)',
        ],
    },
    'warning-receipt-rejects-cleared-delegate-acquisition-mode': {
        'source': SOURCES['yield-from-acquired-initial-nan-reference'],
        'stage': RESUME,
        'checks': [
            *HEADER, '$yield_from_iterator_valid_task(S, n_parent, pyieldfromreceipt, poperand)',
            *ADMISSION,
            'S_bad = S[.OBJECTS[n_parent] = GENERATOR pgenerator_parent'
            '[.DELEGATE = (pgeneratorfrom[.ACQUISITION = eps])]]',
            '$heap_graph(S_bad) = $heap_graph(S)',
            '~$yield_from_iterator_valid_task(S_bad, n_parent, pyieldfromreceipt, poperand)',
            '~$call_descriptors_valid(S_bad)',
        ],
    },
    'parked-handler-keeps-raw-data-and-unique-real-parent-operation': {
        'source': SOURCES['yield-from-acquired-nan-handler-parks'],
        'stage': PARK,
        'checks': [
            *PARK_VIEW, 'S.ACTIVEFIBER = eps', 'S.FIBERCALLERS = eps',
            'pfiber.STATUS = FIBER_SUSPENDED',
            'S.STORE[n_valid] = DEFINED (PFLOAT n_bits)', '$generator_from_nan(PFLOAT n_bits)',
            'pcallcontext_handler.LINE = 26',
            'pcallcontext_handler.CALLSITE = (pyieldfromreceipt.SITE)',
            '$error_context_valid(S_view, pcallcontext_handler)',
            '$error_entered_call_valid(S_scope, perrorcall)',
            '$yield_from_iterator_warning_transfer(S_view)',
            '$generator_saved_ids(pfibervm.FRAMES) = [n_parent]',
            '$generator_from_saved_claims(pfibervm.FRAMES) = [n_parent]',
            '$yield_from_iterator_warning_vm_claims(S, pfibervm) = [n_parent]',
            '$generator_from_saved_fiber_claims(S) = [n_parent]',
            '$generator_saved_fiber_ids(S) = [n_parent]',
            '$generator_from_saved_fiber_claims(S_view) = eps',
            '$task_nodes(perrorcall.RESUME) = [HCELL n_valid]',
            '$heap_owners($heap_graph(S), HOBJECT n_data) = 1',
            '$fiber_vm_valid(S, pfibervm, (n_fiber), eps)', *ADMISSION,
        ],
    },
    'parked-warning-zero-budget-preserves-exact-saved-vm': {
        'source': SOURCES['yield-from-acquired-nan-handler-parks'],
        'stage': PARK,
        'checks': [
            '$fiber_vm_valid(S, pfibervm, (n_fiber), eps)', *ADMISSION, *ZERO,
            'S_zero.OBJECTS[n_fiber] = FIBER pfiber',
        ],
    },
    'parked-warning-rejects-coherent-shifted-receipt-and-handler-line': {
        'source': SOURCES['yield-from-acquired-nan-handler-parks'],
        'stage': PARK,
        'checks': [
            *PARK_VIEW, '$yield_from_iterator_warning_transfer(S_view)', *ADMISSION,
            'pyieldfromreceipt_bad = pyieldfromreceipt[.LINE = 25]',
            'perrorcall_bad = perrorcall[.LINE = 25][.EVENT = DIAGNOSTIC "Warning" '
            'perrorcall.MESSAGE 25][.RESUME = YIELD_FROM_ITERATOR_VALID '
            'n_parent pyieldfromreceipt_bad poperand]',
            'pframe_bad = pframe_handler[.TODO = '
            '(ERROR_HANDLER_RESULT perrorcall_bad) :: ptask_handler*]',
            'pfibervm_bad = pfibervm[.CURRENT = (pcallcontext_handler[.LINE = 25])]'
            '[.FRAMES = pframe_bad :: pframe_tail*]',
            'S_bad = S[.OBJECTS[n_fiber] = FIBER pfiber[.VM = (pfibervm_bad)]]'
            '[.OBJECTS[n_parent] = GENERATOR pgenerator_parent'
            '[.DELEGATE = (pgeneratorfrom[.ACQUISITION = (pyieldfromreceipt_bad)])]]',
            '$heap_graph(S_bad) = $heap_graph(S)',
            'S_view_bad = $fiber_vm_restore(S_bad, pfibervm_bad)'
            '[.ACTIVEFIBER = (n_fiber)][.FIBERCALLERS = eps][.COMPLETION = NORMAL]',
            '~$yield_from_iterator_warning_transfer(S_view_bad)',
            '~$fiber_vm_valid(S_bad, pfibervm_bad, (n_fiber), eps)',
            '~$call_descriptors_valid(S_bad)',
        ],
    },
    'parked-warning-rejects-duplicate-wrapper-and-parent-claim': {
        'source': SOURCES['yield-from-acquired-nan-handler-parks'],
        'stage': PARK,
        'checks': [
            *PARK_VIEW, *ADMISSION,
            'pframe_duplicate = pframe_handler[.TODO = (ERROR_HANDLER_RESULT perrorcall) :: '
            '(ERROR_HANDLER_RESULT perrorcall) :: ptask_handler*]',
            'pfibervm_duplicate = pfibervm[.FRAMES = pframe_duplicate :: pframe_tail*]',
            'S_duplicate = S[.OBJECTS[n_fiber] = FIBER pfiber[.VM = (pfibervm_duplicate)]]',
            '$generator_from_claims(pframe_duplicate.TODO) = [n_parent, n_parent]',
            '$generator_saved_ids(pfibervm_duplicate.FRAMES) = [n_parent]',
            '$heap_valid($heap_graph(S_duplicate))',
            '$heap_owners($heap_graph(S_duplicate), HOBJECT n_data) = 1',
            '$heap_owners($heap_graph(S_duplicate), HCELL n_valid) = '
            '$($heap_owners($heap_graph(S), HCELL n_valid) + 1)',
            'S_view_duplicate = $fiber_vm_restore(S_duplicate, pfibervm_duplicate)'
            '[.ACTIVEFIBER = (n_fiber)][.FIBERCALLERS = eps][.COMPLETION = NORMAL]',
            '~$yield_from_iterator_warning_transfer(S_view_duplicate)',
            '~$fiber_vm_valid(S_duplicate, pfibervm_duplicate, (n_fiber), eps)',
            '~$generator_from_state_valid(S_duplicate)',
            '~$call_descriptors_valid(S_duplicate)',
        ],
    },
    'initial-handler-throw-drops-delegate-and-keeps-ordered-raw-data-owners': {
        'source': SOURCES['yield-from-acquired-initial-nan-handler-throws'],
        'stage': THROWN,
        'checks': [
            *HEADER, 'pyieldfromreceipt.LINE = 24', 'poperand = REFERENCE n_valid',
            '$lookup(S.ENV, $ptascii("failure")) = (n_failure)',
            'S.STORE[n_failure] = DEFINED (POBJECT n_error)',
            '$error_call_valid(S, perrorcall)', *ADMISSION, *ONE,
            'S_one.OBJECTS[n_parent] = GENERATOR pgenerator_parent'
            '[.DELEGATE = (pgeneratorfrom[.INPUT = eps])]',
            '$heap_count(HCELL n_valid, $tasks_nodes(S_one.TODO)) = 1',
            '$heap_count(HOBJECT n_data, $tasks_nodes(S_one.TODO)) = 1',
            'S_one.YIELDRETAINED = eps', *POST,
        ],
    },
    'later-handler-throw-drops-data-before-catch-and-finally': {
        'source': SOURCES['yield-from-acquired-later-nan-handler-throws'],
        'stage': THROWN,
        'checks': [
            *HEADER, 'pyieldfromreceipt.LINE = 25', 'pgeneratorfrom.POSITION = 1',
            'poperand = REFERENCE n_valid',
            '$lookup(S.ENV, $ptascii("failure")) = (n_failure)',
            'S.STORE[n_failure] = DEFINED (POBJECT n_error)',
            '$error_call_valid(S, perrorcall)', *ADMISSION, *ONE,
            'S_one.OBJECTS[n_parent] = GENERATOR pgenerator_parent'
            '[.DELEGATE = (pgeneratorfrom[.INPUT = eps])]',
            '$heap_count(HCELL n_valid, $tasks_nodes(S_one.TODO)) = 1',
            '$heap_count(HOBJECT n_data, $tasks_nodes(S_one.TODO)) = 1',
            'S_one.YIELDRETAINED = eps', *POST,
        ],
    },
    'initial-error-reaches-real-raw-before-data-release-without-retention': {
        'source': SOURCES['yield-from-acquired-initial-nan-handler-throws'],
        'stage': RELEASED,
        'checks': [
            '$lookup(S.ENV, $ptascii("failure")) = (n_failure)',
            'S.STORE[n_failure] = DEFINED (POBJECT n_error)',
            'pdestructionrelease.CALLER = S.CURRENT',
            'pdestructionrelease.ORIGIN = (porigin_site)',
            '$generator_from_site(S, porigin_site)', '$generator_from_line(S, porigin_site) = 24',
            '~(n_data <- S.DESTRUCTION.CALLED)',
            '$destructor_release_valid(S, pdestructionrelease)',
            '$heap_count(HCELL n_valid, $tasks_nodes(S.TODO)) = 1',
            '$heap_count(HOBJECT n_data, $tasks_nodes(S.TODO)) = 1',
            'S.YIELDRETAINED = eps', *ADMISSION,
        ],
    },
    'later-error-reaches-real-raw-before-data-release-without-retention': {
        'source': SOURCES['yield-from-acquired-later-nan-handler-throws'],
        'stage': RELEASED,
        'checks': [
            '$lookup(S.ENV, $ptascii("failure")) = (n_failure)',
            'S.STORE[n_failure] = DEFINED (POBJECT n_error)',
            'pdestructionrelease.CALLER = S.CURRENT',
            'pdestructionrelease.ORIGIN = (porigin_site)',
            '$generator_from_site(S, porigin_site)', '$generator_from_line(S, porigin_site) = 25',
            '~(n_data <- S.DESTRUCTION.CALLED)',
            '$destructor_release_valid(S, pdestructionrelease)',
            '$heap_count(HCELL n_valid, $tasks_nodes(S.TODO)) = 1',
            '$heap_count(HOBJECT n_data, $tasks_nodes(S.TODO)) = 1',
            'S.YIELDRETAINED = eps', *ADMISSION,
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
            'yield-from valid NaN review inputs changed during run'
        if not passed:
            break
    raise SystemExit(0 if passed else 1)
