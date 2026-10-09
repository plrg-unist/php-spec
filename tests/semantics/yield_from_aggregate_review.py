#!/usr/bin/env python3
"""Source-reached Aggregate yield-from acquisition, data and receipt ownership."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import fiber_state_review as review

CATALOG = Path(__file__).with_name('yield_from_aggregate_cases.json')
INPUT_BYTES = {path: path.read_bytes() for path in (Path(__file__), Path(review.__file__), CATALOG)}
SOURCES = {row['id']: row['source'] for row in json.loads(INPUT_BYTES[CATALOG])}
ADMISSION = ['$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
POST = ['$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))']
ONE = ['S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
       'S_one = S_one_budget[.COMPLETION = NORMAL]']
ZERO = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S']
HEADER = ['n_original = pyieldfromaggregate.AGGREGATE',
          'n_parent = pyieldfromaggregate.PARENT',
          'S.OBJECTS[n_parent] = GENERATOR pgenerator_parent',
          'pgenerator_parent.PHASE = GENERATOR_RUNNING',
          'pgenerator_parent.DELEGATE = eps',
          'pyieldfromreceipt = $yield_from_aggregate_receipt(S, pyieldfromaggregate)',
          '$yield_from_receipt_valid(S, pyieldfromreceipt)']
PENDING = ('S.TODO = (CALL_ARGS pcalltarget eps 0 eps (porigin) z) :: '
           '(YIELD_FROM_AGGREGATE pyieldfromaggregate "getIterator") :: ptask_tail* '
           '-- if pyieldfromaggregate.ACQUIRED = eps')
CREATION = ('S.TODO = (GENERATOR_CREATE porigin_get) :: ptask_body* '
            '-- if S.CURRENT = (pcallcontext_borrowed) '
            '-- if S.FRAMES = pframe_getter :: pframe_resumers* '
            '-- if pframe_getter.TODO = '
            '(YIELD_FROM_AGGREGATE pyieldfromaggregate "getIterator") :: ptask_tail*')
BODY = ('S.TODO = (GENERATOR_YIELD_STORE porigin_yield poperand_key?) :: ptask_body* '
        '-- if S.RESULT = KNOWN (PINT 7) '
        '-- if S.FRAMES = pframe_data :: pframe_resumers* '
        '-- if pframe_data.TODO = (GENERATOR_RESUME pgeneratorop) :: '
        '(YIELD_FROM_ITERATOR_RESULT n_parent pyieldfromreceipt n_data) :: ptask_parent*')
PARK = ('S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_main* '
        '-- if pconfigcall.KIND = INTRINSIC_FIBER_RESUME '
        '-- if pconfigcall.OWNER = (n_fiber) '
        '-- if $fiber_at(S, n_fiber) = (pfiber) '
        '-- if pfiber.VM = (pfibervm) '
        '-- if pfibervm.FRAMES = pframe_getter :: pframe_resumers* '
        '-- if pframe_getter.TODO = '
        '(YIELD_FROM_AGGREGATE pyieldfromaggregate "getIterator") :: ptask_parent*')
PARK_VIEW = ['n_original = pyieldfromaggregate.AGGREGATE',
             'n_parent = pyieldfromaggregate.PARENT',
             'pyieldfromaggregate.ACQUIRED = [n_inner]',
             'pyieldfromaggregate.OBJECT = n_inner',
             'pyieldfromaggregate.INPUT = KNOWN (POBJECT n_original)',
             'pyieldfromaggregate.LINE = 25',
             'pfibervm.CURRENT = (pcallcontext_get)',
             'pcallcontext_get.TARGET = AGGREGATE_METHOD_TARGET n_inner porigin_get',
             'S_view = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)]'
             '[.FIBERCALLERS = eps][.COMPLETION = NORMAL]',
             'S_scope = $constant_frame_scope(S_view, pframe_getter, pframe_resumers*)',
             '$yield_from_aggregate_frame(S_view, pcallcontext_get, pframe_getter)']
LAYER_THROW = ('S.TODO = (THROW_SEARCH n_error) :: '
               '(DESTRUCTOR_RESULT pdestructorcall) :: '
               '(DESTRUCTOR_RELEASE pdestructionrelease) :: '
               '(YIELD_FROM_AGGREGATE pyieldfromaggregate "acquired") :: ptask_tail*')
RETAINED = ('S.TODO = (THROW_SEARCH n_error) :: ptask_tail* '
            '-- if S.YIELDRETAINED = [pyieldfromretained]')


CASES = {
    'stable-global-cv-reference-cell-borrows-original-with-live-identity': {
        'source': SOURCES['yield-from-aggregate-stable-iterator'],
        'stage': PENDING,
        'checks': [
            *HEADER, 'z = 21',
            'pyieldfromaggregate.INPUT = VARIABLE ($ptascii("aggregate")) 21',
            '$lookup(S.ENV, $ptascii("aggregate")) = (n_input)',
            'n_input <- S.REFCELLS',
            'S.STORE[n_input] = DEFINED (POBJECT n_original)',
            '$yield_from_aggregate_input_stable(S, pyieldfromaggregate)',
            '$task_nodes(YIELD_FROM_AGGREGATE pyieldfromaggregate "getIterator") = eps',
            '$target_nodes(pcalltarget) = eps',
            '$yield_from_aggregate_pending_site(S, porigin)', *ADMISSION, *ZERO,
        ],
    },
    'pending-getter-borrows-receiver-and-enters-real-source-frame': {
        'source': SOURCES['yield-from-aggregate-nested-owner-order'],
        'stage': PENDING,
        'checks': [
            *HEADER, 'z = 24', 'pyieldfromaggregate.SITE = porigin',
            'pyieldfromaggregate.LINE = z',
            'pyieldfromaggregate.INPUT = KNOWN (POBJECT n_original)',
            'pcalltarget = AGGREGATE_METHOD_TARGET n_original porigin_get',
            '$target_nodes(pcalltarget) = eps',
            '$task_nodes(YIELD_FROM_AGGREGATE pyieldfromaggregate "getIterator") = '
            '[HOBJECT n_original]',
            '$yield_from_aggregate_pending_site(S, porigin)', *ADMISSION, *ONE,
            'S_one.CURRENT = (pcallcontext_get)',
            'pcallcontext_get.TARGET = pcalltarget',
            'pcallcontext_get.LINE = 24', 'pcallcontext_get.ARGC = 0',
            '$call_context_roots(S_one.CURRENT) = eps',
            'S_one.FRAMES = pframe_getter :: pframe_resumers*',
            '$yield_from_aggregate_frame(S_one, pcallcontext_get, pframe_getter)', *POST,
        ],
    },
    'pending-getter-rejects-coordinated-source-line-forgery': {
        'source': SOURCES['yield-from-aggregate-nested-owner-order'],
        'stage': PENDING,
        'checks': [
            '$yield_from_aggregate_pending_site(S, porigin)', *ADMISSION,
            'pyieldfromaggregate_bad = pyieldfromaggregate[.LINE = $(z + 1)]',
            'S_bad = S[.TODO = (CALL_ARGS pcalltarget eps 0 eps (porigin) $(z + 1)) :: '
            '(YIELD_FROM_AGGREGATE pyieldfromaggregate_bad "getIterator") :: ptask_tail*]',
            '$heap_graph(S_bad) = $heap_graph(S)',
            '~$yield_from_aggregate_valid(S_bad, pyieldfromaggregate_bad, "getIterator")',
            '~$yield_from_aggregate_pending_site(S_bad, porigin)',
            '~$call_descriptors_valid(S_bad)',
        ],
    },
    'terminal-transfer-retires-returned-layers-inside-out-and-protects-data': {
        'source': SOURCES['yield-from-aggregate-nested-owner-order'],
        'stage': ('S.TODO = (YIELD_FROM_AGGREGATE pyieldfromaggregate "getIterator") :: '
                  'ptask_tail* -- if pyieldfromaggregate.ACQUIRED = [n_middle, n_inner] '
                  '-- if S.RESULT = KNOWN (POBJECT n_data)'),
        'checks': [
            *HEADER, 'pyieldfromaggregate.OBJECT = n_inner',
            '$useriter_instance(S, n_data)',
            'pyieldfromaggregate.INPUT = KNOWN (POBJECT n_original)',
            '$yield_from_aggregate_valid(S, pyieldfromaggregate, "getIterator")',
            *ADMISSION, *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(YIELD_FROM_AGGREGATE pyieldfromaggregate_data "acquired") :: ptask_tail*',
            'pyieldfromaggregate_data = pyieldfromaggregate[.OBJECT = n_data][.ACQUIRED = eps]',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_inner), '
            'DESTRUCTION_VALUE (HOBJECT n_middle)]',
            '$destructor_release_valid(S_one, pdestructionrelease)',
            '$task_nodes(YIELD_FROM_AGGREGATE pyieldfromaggregate_data "acquired") = '
            '[HOBJECT n_data, HOBJECT n_original]',
            '$heap_owners($heap_graph(S_one), HOBJECT n_data) = 1',
            'S_one.RESULT = KNOWN PNULL', *POST,
        ],
    },
    'original-input-retires-before-first-rewind': {
        'source': SOURCES['yield-from-aggregate-nested-owner-order'],
        'stage': 'S.TODO = (YIELD_FROM_AGGREGATE pyieldfromaggregate "acquired") :: ptask_tail*',
        'checks': [
            *HEADER, 'n_data = pyieldfromaggregate.OBJECT',
            'pyieldfromaggregate.INPUT = KNOWN (POBJECT n_original)',
            'pyieldfromaggregate.ACQUIRED = eps',
            'S.EVENTS = [OUTPUT $ptascii("O|"), OUTPUT $ptascii("M|"), '
            'OUTPUT $ptascii("N|"), OUTPUT $ptascii("n|"), OUTPUT $ptascii("m|")]',
            *ADMISSION, *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(YIELD_FROM_AGGREGATE pyieldfromaggregate_ready "ready") :: ptask_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_original)]',
            'pyieldfromaggregate_ready = pyieldfromaggregate[.INPUT = KNOWN PNULL]',
            '$task_nodes(YIELD_FROM_AGGREGATE pyieldfromaggregate_ready "ready") = '
            '[HOBJECT n_data]',
            '$destructor_release_valid(S_one, pdestructionrelease)',
            '$heap_owners($heap_graph(S_one), HOBJECT n_data) = 1', *POST,
        ],
    },
    'generic-generator-body-has-one-data-owner-and-real-borrowed-resumer': {
        'source': SOURCES['yield-from-aggregate-generator-iterator-return-send'],
        'stage': BODY,
        'checks': [
            'pgeneratorop.BORROWED', '~pgeneratorop.STARTPACK',
            'pgeneratorop.OBJECT = n_data', 'pgeneratorop.NAME = "rewind"',
            'pgeneratorop.SITE = pyieldfromreceipt.SITE', 'pgeneratorop.LINE = 15',
            'pgeneratorop.ARGUMENTS = eps', 'pgeneratorop.LOOP = eps',
            '$task_nodes(GENERATOR_RESUME pgeneratorop) = eps',
            'S.OBJECTS[n_parent] = GENERATOR pgenerator_parent',
            'pgenerator_parent.DELEGATE = (pgeneratorfrom)',
            'pgeneratorfrom.ACQUISITION = (pyieldfromreceipt)',
            'pgeneratorfrom.INPUT = (POBJECT n_data)',
            '$generator_from_nodes(pgenerator_parent.DELEGATE) = [HOBJECT n_data]',
            '$yield_from_iterator_operation_valid(S, pgeneratorop)',
            '$generator_operation_valid(S, pgeneratorop)',
            '$generator_saved_ids(S.FRAMES) = [n_data, n_parent]',
            '$heap_owners($heap_graph(S), HOBJECT n_data) = 1',
            'S.YIELDRETAINED = eps', *ADMISSION,
        ],
    },
    'generic-generator-rejects-cleared-acquisition-with-authentic-result-receipt': {
        'source': SOURCES['yield-from-aggregate-generator-iterator-return-send'],
        'stage': BODY,
        'checks': [
            '$yield_from_iterator_operation_valid(S, pgeneratorop)', *ADMISSION,
            'S.OBJECTS[n_parent] = GENERATOR pgenerator_parent',
            'pgenerator_parent.DELEGATE = (pgeneratorfrom)',
            'S_bad = S[.OBJECTS[n_parent] = GENERATOR '
            'pgenerator_parent[.DELEGATE = (pgeneratorfrom[.ACQUISITION = eps])]]',
            '$heap_graph(S_bad) = $heap_graph(S)',
            '~$yield_from_iterator_result_valid(S_bad, n_parent, pyieldfromreceipt, n_data)',
            '~$generator_operation_valid(S_bad, pgeneratorop)',
            '~$call_descriptors_valid(S_bad)',
        ],
    },
    'ordinary-generator-call-cannot-forge-borrowed-native-operation': {
        'source': SOURCES['yield-from-aggregate-generator-iterator-return-send'],
        'stage': PENDING + ' -- if S.FRAMES = [pframe_resumer] '
                 '-- if pframe_resumer.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask_main*',
        'checks': [
            '~pgeneratorop.BORROWED', '~pgeneratorop.STARTPACK',
            'pgeneratorop.NAME = "current"',
            '$generator_operation_valid(S, pgeneratorop)', *ADMISSION,
            'pgeneratorop_bad = pgeneratorop[.BORROWED = true]',
            'pframe_bad = pframe_resumer[.TODO = '
            '(GENERATOR_RESUME pgeneratorop_bad) :: ptask_main*]',
            'S_bad = S[.FRAMES = [pframe_bad]]',
            '$heap_valid($heap_graph(S_bad))',
            '~$generator_operation_valid(S_bad, pgeneratorop_bad)',
            '~$call_descriptors_valid(S_bad)',
        ],
    },
    'generator-getter-promotes-only-its-copied-frame-to-owned-receiver': {
        'source': SOURCES['yield-from-aggregate-generator-getter-receiver'],
        'stage': CREATION,
        'checks': [
            *HEADER, 'pyieldfromaggregate.LINE = 10',
            'pcallcontext_borrowed.TARGET = AGGREGATE_METHOD_TARGET n_original porigin_get',
            '$call_context_roots(S.CURRENT) = eps',
            '$generator_create_valid(S, porigin_get)', *ADMISSION, *ONE,
            'S_one.TODO = (YIELD_FROM_AGGREGATE pyieldfromaggregate "getIterator") :: ptask_tail*',
            'S_one.RESULT = KNOWN (POBJECT n_data)',
            'S_one.OBJECTS[n_data] = GENERATOR pgenerator_data',
            'pgenerator_data.PHASE = GENERATOR_FRESH',
            'pgenerator_data.FRAME = (pframe_data)',
            'pframe_data.CONTEXT = (pcallcontext_owned)',
            'pcallcontext_owned.TARGET = YIELD_FROM_AGGREGATE_GENERATOR_TARGET '
            'n_original porigin_get n_parent pyieldfromaggregate.SITE 10',
            'pcallcontext_owned[.TARGET = pcallcontext_borrowed.TARGET] = pcallcontext_borrowed',
            '$heap_count(HOBJECT n_original, $call_context_roots(pframe_data.CONTEXT)) = 1',
            '$heap_count(HOBJECT n_original, $node_children(S_one, HOBJECT n_data)) = 1',
            '$generator_frame_valid(S_one, pgenerator_data, pframe_data)', *POST,
        ],
    },
    'generator-getter-rejects-coordinated-retained-receipt-and-line-forgery': {
        'source': SOURCES['yield-from-aggregate-generator-getter-receiver'],
        'stage': ('S.TODO = (YIELD_FROM_AGGREGATE pyieldfromaggregate "getIterator") :: '
                  'ptask_tail* -- if S.RESULT = KNOWN (POBJECT n_data) '
                  '-- if S.OBJECTS[n_data] = GENERATOR pgenerator_data '
                  '-- if pgenerator_data.FRAME = (pframe_data) '
                  '-- if pframe_data.CONTEXT = (pcallcontext_owned)'),
        'checks': [
            'pcallcontext_owned.TARGET = YIELD_FROM_AGGREGATE_GENERATOR_TARGET '
            'n_original porigin_get n_parent porigin z',
            '$yield_from_aggregate_generator_context(S, pcallcontext_owned)', *ADMISSION,
            'pcallcontext_bad = pcallcontext_owned[.LINE = $(z + 1)][.TARGET = '
            'YIELD_FROM_AGGREGATE_GENERATOR_TARGET '
            'n_original porigin_get n_parent porigin $(z + 1)]',
            'pframe_bad = pframe_data[.CONTEXT = (pcallcontext_bad)]',
            'S_bad = S[.OBJECTS[n_data] = GENERATOR '
            'pgenerator_data[.FRAME = (pframe_bad)]]',
            '$heap_graph(S_bad) = $heap_graph(S)',
            '~$yield_from_aggregate_generator_context(S_bad, pcallcontext_bad)',
            '~$generator_frame_valid(S_bad, pgenerator_data[.FRAME = (pframe_bad)], pframe_bad)',
            '~$call_descriptors_valid(S_bad)',
        ],
    },
    'generic-generator-cache-retains-raw-reference-across-global-write': {
        'source': SOURCES['yield-from-aggregate-generator-reference-cache'],
        'stage': ('S.TODO = (GENERATOR_ARGS pgeneratorop phpType7* poperand*) :: ptask_tail* '
                  '-- if pgeneratorop.NAME = "current" '
                  '-- if $lookup(S.ENV, $ptascii("value")) = (n_value) '
                  '-- if S.STORE[n_value] = DEFINED (PINT 9)'),
        'checks': [
            'n_parent = pgeneratorop.OBJECT',
            'S.OBJECTS[n_parent] = GENERATOR pgenerator_parent',
            'pgenerator_parent.PHASE = GENERATOR_DELEGATING',
            'pgenerator_parent.DELEGATE = (pgeneratorfrom)',
            'pgeneratorfrom.ACQUISITION = (pyieldfromreceipt)',
            'pgeneratorfrom.CURRENT = (REFERENCE n_value)',
            'pgeneratorfrom.INPUT = (POBJECT n_data)',
            '$generator_from_shared(S, pgenerator_parent.DELEGATE) = false',
            '$generator_from_raw(S, n_parent, $(|S.OBJECTS| + 1)) = (REFERENCE n_value)',
            '$generator_cached_value(S, n_parent, false) = PINT 9',
            '$heap_count(HCELL n_value, $generator_from_nodes(pgenerator_parent.DELEGATE)) = 1',
            'pgenerator_parent.FRAME = (pframe_parent)',
            'pframe_parent.TODO = (YIELD_FROM_ITERATOR_NEXT n_parent pyieldfromreceipt) :: ptask_body*',
            '$call_task_valid($generator_frame_scope(S, pframe_parent), '
            'YIELD_FROM_ITERATOR_NEXT n_parent pyieldfromreceipt)', *ADMISSION,
        ],
    },
    'finite-repeated-ancestor-keeps-each-returned-owner-occurrence': {
        'source': SOURCES['yield-from-aggregate-repeated-ancestor'],
        'stage': ('S.TODO = (YIELD_FROM_AGGREGATE pyieldfromaggregate "getIterator") :: '
                  'ptask_tail* -- if pyieldfromaggregate.ACQUIRED = [n_middle, n_original] '
                  '-- if pyieldfromaggregate.AGGREGATE = n_original '
                  '-- if S.RESULT = KNOWN (POBJECT n_data)'),
        'checks': [
            *HEADER, 'pyieldfromaggregate.OBJECT = n_original',
            'n_middle =/= n_original', '$useriter_instance(S, n_data)',
            'pyieldfromaggregate.INPUT = VARIABLE n_name* z',
            '$fiber_traversal_acquisition_valid(S, n_original, [n_middle, n_original])',
            '$fiber_traversal_acquisition_nodes([n_middle, n_original]) = '
            '[HOBJECT n_original, HOBJECT n_middle]',
            '$task_nodes(YIELD_FROM_AGGREGATE pyieldfromaggregate "getIterator") = '
            '[HOBJECT n_original, HOBJECT n_middle]',
            '$heap_owners($heap_graph(S), HOBJECT n_original) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_middle) = 2', *ADMISSION,
        ],
    },
    'parked-deeper-getter-retains-input-layer-and-exact-parent-resumer': {
        'source': SOURCES['yield-from-aggregate-deeper-getter-parks'], 'stage': PARK,
        'checks': [
            *PARK_VIEW,
            '$call_context_roots(pfibervm.CURRENT) = eps',
            '$task_nodes(YIELD_FROM_AGGREGATE pyieldfromaggregate "getIterator") = '
            '[HOBJECT n_inner, HOBJECT n_original]',
            '$heap_owners($heap_graph(S), HOBJECT n_inner) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_original) = 1',
            '$yield_from_aggregate_valid(S_scope, pyieldfromaggregate, "getIterator")',
            '$generator_saved_ids(pfibervm.FRAMES) = [n_parent]',
            '$generator_saved_fiber_ids(S) = [n_parent]',
            '$fiber_generator_transfer(S_view)',
            '$generator_saved_fiber_ids(S_view) = eps',
            '$fiber_vm_valid(S, pfibervm, (n_fiber), eps)', *ADMISSION, *ZERO,
        ],
    },
    'parked-deeper-getter-rejects-shifted-real-source-frame': {
        'source': SOURCES['yield-from-aggregate-deeper-getter-parks'], 'stage': PARK,
        'checks': [
            *PARK_VIEW, *ADMISSION,
            'pyieldfromaggregate_bad = pyieldfromaggregate[.LINE = 26]',
            'pcallcontext_bad = pcallcontext_get[.LINE = 26]',
            'pframe_bad = pframe_getter[.TODO = '
            '(YIELD_FROM_AGGREGATE pyieldfromaggregate_bad "getIterator") :: ptask_parent*]',
            'pfibervm_bad = pfibervm[.CURRENT = (pcallcontext_bad)]'
            '[.FRAMES = pframe_bad :: pframe_resumers*]',
            'S_bad = S[.OBJECTS[n_fiber] = FIBER pfiber[.VM = (pfibervm_bad)]]',
            '$heap_graph(S_bad) = $heap_graph(S)',
            'S_view_bad = $fiber_vm_restore(S_bad, pfibervm_bad)[.ACTIVEFIBER = (n_fiber)]'
            '[.FIBERCALLERS = eps][.COMPLETION = NORMAL]',
            '~$fiber_generator_transfer(S_view_bad)',
            '~$fiber_vm_valid(S_bad, pfibervm_bad, (n_fiber), eps)',
            '~$call_descriptors_valid(S_bad)',
        ],
    },
    'parked-deeper-getter-rejects-duplicate-authentic-acquisition-owner': {
        'source': SOURCES['yield-from-aggregate-deeper-getter-parks'], 'stage': PARK,
        'checks': [
            *PARK_VIEW, *ADMISSION,
            'pframe_duplicate = pframe_getter[.TODO = '
            '(YIELD_FROM_AGGREGATE pyieldfromaggregate "getIterator") :: '
            '(YIELD_FROM_AGGREGATE pyieldfromaggregate "getIterator") :: ptask_parent*]',
            'pfibervm_duplicate = pfibervm[.FRAMES = pframe_duplicate :: pframe_resumers*]',
            'S_duplicate = S[.OBJECTS[n_fiber] = FIBER pfiber[.VM = (pfibervm_duplicate)]]',
            '$yield_from_aggregate_count(pframe_duplicate.TODO, pyieldfromaggregate.SITE) = 2',
            '$heap_valid($heap_graph(S_duplicate))',
            '$heap_owners($heap_graph(S_duplicate), HOBJECT n_inner) = 2',
            '$heap_owners($heap_graph(S_duplicate), HOBJECT n_original) = 2',
            '~$yield_from_aggregate_valid(S_scope[.TODO = pframe_duplicate.TODO], '
            'pyieldfromaggregate, "getIterator")',
            '~$fiber_vm_valid(S_duplicate, pfibervm_duplicate, (n_fiber), eps)',
            '~$call_descriptors_valid(S_duplicate)',
        ],
    },
    'raw-reference-rejection-keeps-return-cell-through-authenticated-error-step': {
        'source': SOURCES['yield-from-aggregate-raw-reference-rejected'],
        'stage': ('S.TODO = (YIELD_FROM_AGGREGATE pyieldfromaggregate "getIterator") :: '
                  'ptask_tail* -- if S.RESULT = REFERENCE n_return'),
        'checks': [
            *HEADER, 'pyieldfromaggregate.LINE = 20',
            'S.STORE[n_return] = DEFINED (POBJECT n_data)', '$useriter_instance(S, n_data)',
            'pyieldfromaggregate.INPUT = KNOWN (POBJECT n_original)',
            '$yield_from_aggregate_valid(S, pyieldfromaggregate, "getIterator")',
            *ADMISSION, *ONE,
            'S_one.TODO = (THROW_SEARCH n_error) :: '
            '(YIELD_FROM_AGGREGATE pyieldfromaggregate_error "getIterator-error") :: ptask_tail*',
            'pyieldfromaggregate_error = pyieldfromaggregate[.CURRENT = REFERENCE n_return]',
            '$task_nodes(YIELD_FROM_AGGREGATE pyieldfromaggregate_error "getIterator-error") = '
            '[HCELL n_return, HOBJECT n_original]',
            'S_one.OBJECTS[n_error] = THROWABLE pthrowable', 'pthrowable.KIND = "Exception"',
            '$throwable_field(S_one, n_error, "line") = PINT 20',
            'S_one.YIELDRETAINED = eps', *POST,
        ],
    },
    'already-closed-generator-rejection-constructs-no-retained-iterator': {
        'source': SOURCES['yield-from-aggregate-already-closed-generator'],
        'stage': ('S.TODO = (YIELD_FROM_AGGREGATE pyieldfromaggregate "getIterator") :: '
                  'ptask_tail* -- if S.RESULT = KNOWN (POBJECT n_data)'),
        'checks': [
            *HEADER, 'S.OBJECTS[n_data] = GENERATOR pgenerator_data',
            'pgenerator_data.PHASE = GENERATOR_CLOSED', 'pgenerator_data.RETURN = (PINT 23)',
            *ADMISSION, *ONE,
            'S_one.TODO = (THROW_SEARCH n_error) :: '
            '(YIELD_FROM_AGGREGATE pyieldfromaggregate_error "getIterator-error") :: ptask_tail*',
            'pyieldfromaggregate_error = pyieldfromaggregate[.CURRENT = KNOWN (POBJECT n_data)]',
            'S_one.OBJECTS[n_error] = THROWABLE pthrowable', 'pthrowable.KIND = "Exception"',
            '$throwable_field(S_one, n_error, "message") = '
            'PSTRING $ptascii("Cannot traverse an already closed generator")',
            'S_one.YIELDRETAINED = eps', *POST,
        ],
    },
    'pending-layer-hook-authenticates-real-release-snapshot': {
        'source': SOURCES['yield-from-aggregate-layer-destructor-throws'], 'stage': LAYER_THROW,
        'checks': [
            *HEADER, 'S.DESTRUCTION.CALLS = pdestructorcall :: pdestructorcall_tail*',
            'pdestructorcall.RELEASE = (pdestructionrelease_before)',
            '$destructor_result_valid(S, pdestructorcall)', *ADMISSION,
            'S_clean = S[.TODO = (THROW_SEARCH n_error) :: '
            '(DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(YIELD_FROM_AGGREGATE pyieldfromaggregate "acquired") :: ptask_tail*]'
            '[.DESTRUCTION.CALLS = pdestructorcall_tail*]',
            'S_resume = $destructor_resume_pending(S_clean, pdestructorcall)',
            'S_resume.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(YIELD_FROM_AGGREGATE pyieldfromaggregate_error "acquired-error") :: ptask_tail*',
            'pyieldfromaggregate_error = pyieldfromaggregate[.CURRENT = KNOWN (POBJECT n_error)]',
            '$heap_count(HOBJECT n_error, $tasks_nodes(S_resume.TODO)) = 1',
            'pdestructorcall_bad = pdestructorcall[.RELEASE = '
            '(pdestructionrelease_before[.ORIGIN = eps])]',
            '$destructor_resume_pending(S_clean, pdestructorcall_bad) = S_clean',
        ],
    },
    'constructed-iterator-pending-error-appends-one-request-data-owner': {
        'source': SOURCES['yield-from-aggregate-layer-destructor-throws'],
        'stage': ('S.TODO = (YIELD_FROM_AGGREGATE pyieldfromaggregate "ready-error") :: '
                  'ptask_tail* -- if pyieldfromaggregate.CURRENT = KNOWN (POBJECT n_error)'),
        'checks': [
            *HEADER, 'n_data = pyieldfromaggregate.OBJECT', '$useriter_instance(S, n_data)',
            'pyieldfromaggregate.INPUT = KNOWN PNULL', 'pyieldfromaggregate.ACQUIRED = eps',
            'S.YIELDRETAINED = eps',
            'S.EVENTS = [OUTPUT $ptascii("O|"), OUTPUT $ptascii("M|"), '
            'OUTPUT $ptascii("N|"), OUTPUT $ptascii("n|"), '
            'OUTPUT $ptascii("m|"), OUTPUT $ptascii("A|")]',
            '$task_nodes(YIELD_FROM_AGGREGATE pyieldfromaggregate "ready-error") = '
            '[HOBJECT n_error, HOBJECT n_data]', *ADMISSION, *ONE,
            'S_one.TODO = (THROW_SEARCH n_error) :: ptask_tail*',
            'S_one.YIELDRETAINED = [{PARENT n_parent, DATA n_data, '
            'RECEIPT pyieldfromreceipt, INDEX 0}]',
            '$yield_from_retained_nodes(S_one.YIELDRETAINED) = [HOBJECT n_data]',
            '$heap_owners($heap_graph(S_one), HOBJECT n_data) = 1',
            '~(n_data <- S_one.DESTRUCTION.CALLED)',
            'S_one.OBJECTS[n_parent] = GENERATOR pgenerator_parent', *POST,
        ],
    },
    'retained-iterator-rejects-duplicate-authentic-occurrence-index': {
        'source': SOURCES['yield-from-aggregate-layer-destructor-throws'], 'stage': RETAINED,
        'checks': [
            '$yield_from_retained_valid(S, S.YIELDRETAINED)', *ADMISSION,
            'pyieldfromretained.INDEX = 0',
            'S_bad = S[.YIELDRETAINED = [pyieldfromretained, pyieldfromretained]]',
            '$heap_valid($heap_graph(S_bad))',
            '$heap_owners($heap_graph(S_bad), HOBJECT pyieldfromretained.DATA) = '
            '$($heap_owners($heap_graph(S), HOBJECT pyieldfromretained.DATA) + 1)',
            '~$yield_from_retained_valid(S_bad, S_bad.YIELDRETAINED)',
            '~$call_descriptors_valid(S_bad)',
        ],
    },
    'retained-iterator-rejects-shifted-source-receipt-with-identical-heap': {
        'source': SOURCES['yield-from-aggregate-layer-destructor-throws'], 'stage': RETAINED,
        'checks': [
            '$yield_from_retained_valid(S, S.YIELDRETAINED)', *ADMISSION,
            'pyieldfromreceipt = pyieldfromretained.RECEIPT', 'pyieldfromreceipt.LINE = 25',
            'pyieldfromretained_bad = pyieldfromretained[.RECEIPT = '
            'pyieldfromreceipt[.LINE = 26]]',
            'S_bad = S[.YIELDRETAINED = [pyieldfromretained_bad]]',
            '$heap_graph(S_bad) = $heap_graph(S)',
            '~$yield_from_retained_valid(S_bad, S_bad.YIELDRETAINED)',
            '~$call_descriptors_valid(S_bad)',
        ],
    },
    'input-destructor-error-retains-fresh-generator-without-starting-body': {
        'source': SOURCES['yield-from-aggregate-input-destructor-throws-generator'], 'stage': RETAINED,
        'checks': [
            'n_data = pyieldfromretained.DATA',
            'S.OBJECTS[n_data] = GENERATOR pgenerator_data',
            'pgenerator_data.PHASE = GENERATOR_FRESH', 'pgenerator_data.FRAME = (pframe_data)',
            'pgenerator_data.VALUE = eps', 'pgenerator_data.RETURN = eps',
            'S.EVENTS = [OUTPUT $ptascii("G|"), OUTPUT $ptascii("A|")]',
            '$yield_from_retained_nodes(S.YIELDRETAINED) = [HOBJECT n_data]',
            '$heap_owners($heap_graph(S), HOBJECT n_data) = 1',
            '$generator_resume_ids(S.TODO) = eps',
            '$generator_saved_ids(S.FRAMES) = [pyieldfromretained.PARENT]', *ADMISSION,
        ],
    },
    'rewind-error-releases-data-before-catch-and-never-enters-retained-list': {
        'source': SOURCES['yield-from-aggregate-rewind-throws'],
        'stage': ('S.TODO = (THROW_SEARCH n_error) :: '
                  '(GENERATOR_FROM_CALLBACK n_parent porigin "rewind") :: ptask_tail* '
                  '-- if S.OBJECTS[n_parent] = GENERATOR pgenerator_parent '
                  '-- if pgenerator_parent.DELEGATE = (pgeneratorfrom)'),
        'checks': [
            'pgeneratorfrom.ACQUISITION = (pyieldfromreceipt)',
            'pgeneratorfrom.INPUT = (POBJECT n_data)', '$useriter_instance(S, n_data)',
            'pyieldfromreceipt.LINE = 17', 'S.YIELDRETAINED = eps',
            '$generator_from_callback_valid(S, n_parent, porigin, "rewind")',
            'S.EVENTS = [OUTPUT $ptascii("G|"), OUTPUT $ptascii("A|"), OUTPUT $ptascii("W|")]',
            *ADMISSION, *ONE,
            'S_one.OBJECTS[n_parent] = GENERATOR pgenerator_parent_next',
            'pgenerator_parent_next.DELEGATE = (pgeneratorfrom_next)',
            'pgeneratorfrom_next.INPUT = eps', 'pgeneratorfrom_next.CURRENT = eps',
            'S_one.YIELDRETAINED = eps',
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_data)]',
            'pdestructionoperation.SOURCE = THROW_SEARCH n_error',
            'pdestructionoperation.PENDING = (n_error)',
            'pdestructionoperation.CALLER = S_one.CURRENT',
            'pdestructionoperation.ORIGIN = S_one.ORIGIN',
            '$heap_count(HOBJECT n_error, $task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation)) = 1',
            '$destructor_release_valid(S_one, pdestructionrelease)',
            '$destructor_operation_valid(S_one, pdestructionoperation)', *POST,
        ],
    },
    'reference-original-input-is-one-owning-cell-with-borrowed-getter': {
        'source': SOURCES['yield-from-aggregate-reference-original-operand'],
        'stage': PENDING,
        'checks': [
            *HEADER, 'z = 25', 'pyieldfromaggregate.LINE = 25',
            'pyieldfromaggregate.SITE = porigin',
            'pyieldfromaggregate.INPUT = REFERENCE n_input',
            'n_input <- S.REFCELLS',
            'S.STORE[n_input] = DEFINED (POBJECT n_original)',
            '$yield_from_aggregate_input_stable(S, pyieldfromaggregate)',
            'pcalltarget = AGGREGATE_METHOD_TARGET n_original porigin_get',
            '$target_nodes(pcalltarget) = eps',
            '$task_nodes(YIELD_FROM_AGGREGATE pyieldfromaggregate "getIterator") = [HCELL n_input]',
            '$heap_owners($heap_graph(S), HCELL n_input) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_original) = 1',
            'S.EVENTS = [OUTPUT $ptascii("R|")]',
            'S.YIELDRETAINED = eps', *ADMISSION, *ZERO,
        ],
    },
    'reference-original-input-release-keeps-cell-payload-and-protected-data': {
        'source': SOURCES['yield-from-aggregate-reference-original-operand'],
        'stage': 'S.TODO = (YIELD_FROM_AGGREGATE pyieldfromaggregate "acquired") :: ptask_tail*',
        'checks': [
            *HEADER, 'pyieldfromaggregate.LINE = 25',
            'pyieldfromaggregate.INPUT = REFERENCE n_input',
            'n_input <- S.REFCELLS',
            'S.STORE[n_input] = DEFINED (POBJECT n_original)',
            'n_data = pyieldfromaggregate.OBJECT',
            '$useriter_instance(S, n_data)',
            'pyieldfromaggregate.ACQUIRED = eps',
            'pyieldfromaggregate.CURRENT = KNOWN PNULL',
            '$task_nodes(YIELD_FROM_AGGREGATE pyieldfromaggregate "acquired") = '
            '[HOBJECT n_data, HCELL n_input]',
            '$heap_owners($heap_graph(S), HCELL n_input) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_data) = 2',
            'S.EVENTS = [OUTPUT $ptascii("R|"), OUTPUT $ptascii("G|")]',
            'S.YIELDRETAINED = eps', *ADMISSION, *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(YIELD_FROM_AGGREGATE pyieldfromaggregate_ready "ready") :: ptask_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HCELL n_input)]',
            'pyieldfromaggregate_ready = pyieldfromaggregate[.INPUT = KNOWN PNULL]',
            '$task_nodes(YIELD_FROM_AGGREGATE pyieldfromaggregate_ready "ready") = [HOBJECT n_data]',
            'S_one.STORE[n_input] = DEFINED (POBJECT n_original)',
            'n_input <- S_one.REFCELLS',
            '$heap_count(HCELL n_input, $task_nodes(DESTRUCTOR_RELEASE pdestructionrelease)) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_data) = 2',
            '$heap_owners($heap_graph(S_one), HOBJECT n_original) = 1',
            'S_one.YIELDRETAINED = eps',
            '$destructor_release_valid(S_one, pdestructionrelease)', *POST,
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
            'yield-from Aggregate review inputs changed during run'
        if not passed:
            break
    raise SystemExit(0 if passed else 1)
