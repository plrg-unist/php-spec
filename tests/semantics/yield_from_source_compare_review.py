#!/usr/bin/env python3
"""Genuine yield-from mutable-source self comparison and recursive owner checks."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import fiber_state_review as review

CATALOG = Path(__file__).with_name('yield_from_source_compare_cases.json')
INPUT_BYTES = {path: path.read_bytes() for path in (Path(__file__), Path(review.__file__), CATALOG)}
SOURCES = {row['id']: row['source'] for row in json.loads(INPUT_BYTES[CATALOG])}
ADMISSION = ['S.YIELDRETAINED = eps', '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
POST = ['S_one.YIELDRETAINED = eps', '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))']
ONE = ['S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
       'S_one = S_one_budget[.COMPLETION = NORMAL]']
ZERO = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S']
HEADER = ['n_original = pyieldfromaggregate.AGGREGATE',
          'n_parent = pyieldfromaggregate.PARENT',
          'pyieldfromaggregate.OBJECT = n_original',
          'pyieldfromaggregate.CURRENT = KNOWN PNULL',
          'S.OBJECTS[n_parent] = GENERATOR pgenerator_parent',
          'pgenerator_parent.PHASE = GENERATOR_RUNNING',
          'pgenerator_parent.DELEGATE = eps',
          '$yield_from_receipt_valid(S, $yield_from_aggregate_receipt(S, pyieldfromaggregate))']
KEEPER = ['S_global = $global_table_view(S)',
          '$lookup(S_global.ENV, $ptascii("keeper")) = (n_keeper)',
          'S.STORE[n_keeper] = DEFINED (POBJECT n_original)']
CV = ['pyieldfromaggregate.INPUT = VARIABLE ($ptascii("slot")) z',
      '$lookup(S.ENV, $ptascii("slot")) = (n_input)',
      'n_input <- S.REFCELLS']
FIRST = ['pyieldfromaggregate.ACQUIRED = eps',
         'S.STORE[n_input] = DEFINED (POBJECT n_payload)',
         'n_payload =/= n_original',
         '~$generator_from_aggregate(S, POBJECT n_payload)',
         '$yield_from_aggregate_self_object(S, pyieldfromaggregate) = (n_payload)',
         '~$yield_from_aggregate_input_stable(S, pyieldfromaggregate)',
         '$yield_from_aggregate_mutable_input(pyieldfromaggregate.INPUT)']
RECURSE = [
    'S_one.TODO = (CALL_ARGS pcalltarget eps 0 eps (pyieldfromaggregate.SITE) '
    'pyieldfromaggregate.LINE) :: (YIELD_FROM_AGGREGATE pyieldfromaggregate_next "getIterator") :: ptask_tail*',
    'pcalltarget = AGGREGATE_METHOD_TARGET n_original porigin_get',
    '$fiber_traversal_method_selected(S_one, n_original, porigin_get, "getIterator")',
    '$target_nodes(pcalltarget) = eps',
    'pyieldfromaggregate_next = pyieldfromaggregate[.ACQUIRED = [n_original]]',
    '$yield_from_aggregate_acquisition_valid(S_one, pyieldfromaggregate_next)',
    '~$fiber_traversal_acquisition_valid(S_one, n_original, [n_original])',
    '$heap_owners($heap_graph(S_one), HOBJECT n_original) = 2',
    'S_one.STORE[n_input] = S.STORE[n_input]',
    'S_one.ITERATORS = S.ITERATORS', 'S_one.NEXTITER = S.NEXTITER',
]
GETTER = ('S.TODO = (YIELD_FROM_AGGREGATE pyieldfromaggregate "getIterator") :: '
          'ptask_tail* -- if S.RESULT = KNOWN (POBJECT n_return)')
DEEP = (GETTER + ' -- if pyieldfromaggregate.ACQUIRED = [pyieldfromaggregate.AGGREGATE]')
DEEP_HEADER = [*HEADER, 'pyieldfromaggregate.ACQUIRED = [n_original]',
               '$yield_from_aggregate_acquisition_valid(S, pyieldfromaggregate)',
               '$yield_from_aggregate_self_object(S, pyieldfromaggregate) = (n_original)',
               'S.DESTRUCTION.CALLED = [n_first]',
               '~((HOBJECT n_first) <- S.ALLOCATIONS)',
               '$heap_owners($heap_graph(S), HOBJECT n_first) = 0']
PARK = ('S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_main* '
        '-- if pconfigcall.KIND = INTRINSIC_FIBER_RESUME '
        '-- if pconfigcall.OWNER = (n_fiber) '
        '-- if $fiber_at(S, n_fiber) = (pfiber) '
        '-- if pfiber.VM = (pfibervm) '
        '-- if pfibervm.FRAMES = pframe_getter :: pframe_resumers* '
        '-- if pframe_getter.TODO = '
        '(YIELD_FROM_AGGREGATE pyieldfromaggregate "getIterator") :: ptask_parent*')
PARK_VIEW = [
    'n_original = pyieldfromaggregate.AGGREGATE',
    'pyieldfromaggregate.OBJECT = n_original',
    'pyieldfromaggregate.ACQUIRED = [n_original]',
    'pyieldfromaggregate.CURRENT = KNOWN PNULL',
    'pyieldfromaggregate.INPUT = VARIABLE ($ptascii("slot")) 33',
    'pyieldfromaggregate.LINE = 33',
    'pfibervm.CURRENT = (pcallcontext_get)',
    'pcallcontext_get.TARGET = AGGREGATE_METHOD_TARGET n_original porigin_get',
    'S_view = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)]'
    '[.FIBERCALLERS = eps][.COMPLETION = NORMAL]',
    'S_scope = $constant_frame_scope(S_view, pframe_getter, pframe_resumers*)',
    '$lookup(S_scope.ENV, $ptascii("slot")) = (n_input)',
    'n_input <- S.REFCELLS',
    'S.STORE[n_input] = DEFINED (POBJECT n_payload)',
    'n_payload =/= n_original',
    'S.DESTRUCTION.CALLED = [n_first]',
    '~((HOBJECT n_first) <- S.ALLOCATIONS)',
    '$yield_from_aggregate_self_object(S_scope, pyieldfromaggregate) = (n_original)',
    '$yield_from_aggregate_acquisition_valid(S_scope, pyieldfromaggregate)',
    '$yield_from_aggregate_frame(S_view, pcallcontext_get, pframe_getter)',
    'n_parent = pyieldfromaggregate.PARENT',
    '$generator_saved_fiber_ids(S) = [n_parent]',
    '$fiber_generator_transfer(S_view)',
    'S_view.YIELDRETAINED = eps',
]

CASES = {
    'yield-from-cv-self-comparison-permits-first-kept-original-repeat': {
        'source': SOURCES['yield-from-source-compare-kept-receiver-repeat-rechange'], 'stage': GETTER,
        'checks': [
            *HEADER, *KEEPER, *CV, 'z = 31', 'pyieldfromaggregate.LINE = z',
            *FIRST, 'n_return = n_original',
            '$heap_owners($heap_graph(S), HOBJECT n_original) = 2',
            '$task_nodes(YIELD_FROM_AGGREGATE pyieldfromaggregate "getIterator") = eps',
            'S.EVENTS = [OUTPUT $ptascii("G0|")]', *ADMISSION, *ONE, *RECURSE,
            '$task_nodes(YIELD_FROM_AGGREGATE pyieldfromaggregate_next "getIterator") = [HOBJECT n_original]',
            *POST,
        ],
    },
    'yield-from-reference-self-comparison-permits-first-kept-original-repeat': {
        'source': SOURCES['yield-from-source-compare-reference-repeat-rechange'], 'stage': GETTER,
        'checks': [
            *HEADER, *KEEPER, 'pyieldfromaggregate.LINE = 32',
            'pyieldfromaggregate.INPUT = REFERENCE n_input', 'n_input <- S.REFCELLS',
            *FIRST, 'n_return = n_original',
            '$heap_owners($heap_graph(S), HCELL n_input) = 3',
            '$heap_owners($heap_graph(S), HOBJECT n_original) = 2',
            '$task_nodes(YIELD_FROM_AGGREGATE pyieldfromaggregate "getIterator") = [HCELL n_input]',
            'S.EVENTS = [OUTPUT $ptascii("R|"), OUTPUT $ptascii("G0|")]',
            *ADMISSION, *ONE, *RECURSE,
            '$task_nodes(YIELD_FROM_AGGREGATE pyieldfromaggregate_next "getIterator") = [HOBJECT n_original, HCELL n_input]',
            '$heap_owners($heap_graph(S_one), HCELL n_input) = 3', *POST,
        ],
    },
    'yield-from-deeper-acquisition-uses-owned-layer-after-earlier-payload-retirement': {
        'source': SOURCES['yield-from-source-compare-kept-receiver-repeat-rechange'], 'stage': DEEP,
        'checks': [
            *DEEP_HEADER, *KEEPER, *CV, 'z = 31', 'pyieldfromaggregate.LINE = z',
            'S.STORE[n_input] = DEFINED (POBJECT n_payload)', 'n_payload =/= n_original',
            'n_return = n_data', '$useriter_instance(S, n_data)',
            '$task_nodes(YIELD_FROM_AGGREGATE pyieldfromaggregate "getIterator") = [HOBJECT n_original]',
            '$heap_owners($heap_graph(S), HOBJECT n_original) = 2',
            'S.EVENTS = [OUTPUT $ptascii("G0|"), OUTPUT $ptascii("G1|"), OUTPUT $ptascii("Q|")]',
            *ADMISSION, *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(YIELD_FROM_AGGREGATE pyieldfromaggregate_data "acquired") :: ptask_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_original)]',
            'pdestructionrelease.CALLER = S.CURRENT', 'pdestructionrelease.ORIGIN = S.ORIGIN',
            'pyieldfromaggregate_data = pyieldfromaggregate[.OBJECT = n_data][.ACQUIRED = eps]',
            '$task_nodes(YIELD_FROM_AGGREGATE pyieldfromaggregate_data "acquired") = [HOBJECT n_data]',
            '$heap_owners($heap_graph(S_one), HOBJECT n_data) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_original) = 2',
            'S_one.STORE[n_input] = S.STORE[n_input]',
            'S_one.ITERATORS = S.ITERATORS', 'S_one.NEXTITER = S.NEXTITER',
            '$destructor_release_valid(S_one, pdestructionrelease)', *POST,
        ],
    },
    'yield-from-repeated-reference-releases-cell-before-data-rewind': {
        'source': SOURCES['yield-from-source-compare-reference-repeat-rechange'],
        'stage': 'S.TODO = (YIELD_FROM_AGGREGATE pyieldfromaggregate "acquired") :: ptask_tail*',
        'checks': [
            'n_original = pyieldfromaggregate.AGGREGATE', *KEEPER,
            'n_parent = pyieldfromaggregate.PARENT',
            'S.OBJECTS[n_parent] = GENERATOR pgenerator_parent',
            'pgenerator_parent.PHASE = GENERATOR_RUNNING', 'pgenerator_parent.DELEGATE = eps',
            '$yield_from_receipt_valid(S, $yield_from_aggregate_receipt(S, pyieldfromaggregate))',
            'pyieldfromaggregate.LINE = 32', 'pyieldfromaggregate.ACQUIRED = eps',
            'pyieldfromaggregate.CURRENT = KNOWN PNULL',
            'pyieldfromaggregate.INPUT = REFERENCE n_input', 'n_input <- S.REFCELLS',
            'S.STORE[n_input] = DEFINED (POBJECT n_payload)', 'n_payload =/= n_original',
            'n_data = pyieldfromaggregate.OBJECT', '$useriter_instance(S, n_data)',
            '$task_nodes(YIELD_FROM_AGGREGATE pyieldfromaggregate "acquired") = [HOBJECT n_data, HCELL n_input]',
            '$heap_owners($heap_graph(S), HCELL n_input) = 3',
            '$heap_owners($heap_graph(S), HOBJECT n_original) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_data) = 1',
            'S.EVENTS = [OUTPUT $ptascii("R|"), OUTPUT $ptascii("G0|"), OUTPUT $ptascii("G1|"), OUTPUT $ptascii("Q|")]',
            'S.YIELDRETAINED = eps', *ADMISSION, *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(YIELD_FROM_AGGREGATE pyieldfromaggregate_ready "ready") :: ptask_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HCELL n_input)]',
            'pdestructionrelease.CALLER = S.CURRENT', 'pdestructionrelease.ORIGIN = S.ORIGIN',
            'pyieldfromaggregate_ready = pyieldfromaggregate[.INPUT = KNOWN PNULL]',
            '$task_nodes(YIELD_FROM_AGGREGATE pyieldfromaggregate_ready "ready") = [HOBJECT n_data]',
            'S_one.STORE[n_input] = S.STORE[n_input]',
            '$heap_owners($heap_graph(S_one), HOBJECT n_data) = 1',
            'S_one.YIELDRETAINED = eps',
            '$destructor_release_valid(S_one, pdestructionrelease)', *POST,
        ],
    },
    'yield-from-live-reference-source-equality-rejects-returned-aggregate': {
        'source': SOURCES['yield-from-source-compare-reference-self-rejection'], 'stage': GETTER,
        'checks': [
            *HEADER, *KEEPER, 'pyieldfromaggregate.ACQUIRED = eps', 'pyieldfromaggregate.LINE = 26',
            'pyieldfromaggregate.INPUT = REFERENCE n_input', 'n_input <- S.REFCELLS',
            'S.STORE[n_input] = DEFINED (POBJECT n_return)', 'n_return =/= n_original',
            '$generator_from_aggregate(S, POBJECT n_return)',
            '$yield_from_aggregate_self_object(S, pyieldfromaggregate) = (n_return)',
            '~$yield_from_aggregate_input_stable(S, pyieldfromaggregate)',
            '$heap_owners($heap_graph(S), HCELL n_input) = 3',
            '$heap_owners($heap_graph(S), HOBJECT n_original) = 1',
            'S.EVENTS = [OUTPUT $ptascii("R|"), OUTPUT $ptascii("G|")]',
            *ADMISSION, *ONE,
            'S_one.TODO = (THROW_SEARCH n_error) :: '
            '(YIELD_FROM_AGGREGATE pyieldfromaggregate_error "getIterator-error") :: ptask_tail*',
            'pyieldfromaggregate_error = pyieldfromaggregate[.CURRENT = KNOWN (POBJECT n_return)]',
            '$task_nodes(YIELD_FROM_AGGREGATE pyieldfromaggregate_error "getIterator-error") = [HOBJECT n_return, HCELL n_input]',
            'S_one.OBJECTS[n_error] = THROWABLE pthrowable', 'pthrowable.KIND = "Exception"',
            '$throwable_field(S_one, n_error, "line") = PINT 26',
            '$string_bytes($throwable_field(S_one, n_error, "message")) = '
            '($ptascii("Objects returned by YieldFromCompareRejectOuter20::getIterator() must be traversable or implement interface Iterator"))',
            'S_one.STORE[n_input] = S.STORE[n_input]',
            '$heap_owners($heap_graph(S_one), HOBJECT n_original) = 1', *POST,
        ],
    },
    'yield-from-immutable-temporary-compares-its-own-input-despite-global-rebind': {
        'source': SOURCES['yield-from-source-compare-immutable-original-self-rejection'], 'stage': GETTER,
        'checks': [
            *HEADER, *KEEPER, 'pyieldfromaggregate.ACQUIRED = eps', 'pyieldfromaggregate.LINE = 19',
            'pyieldfromaggregate.INPUT = KNOWN (POBJECT n_original)', 'n_return = n_original',
            '$lookup(S.ENV, $ptascii("slot")) = (n_input)',
            'S.STORE[n_input] = DEFINED (POBJECT n_payload)', 'n_payload =/= n_original',
            '$yield_from_aggregate_self_object(S, pyieldfromaggregate) = (n_original)',
            '~$yield_from_aggregate_mutable_input(pyieldfromaggregate.INPUT)',
            '$task_nodes(YIELD_FROM_AGGREGATE pyieldfromaggregate "getIterator") = [HOBJECT n_original]',
            '$heap_owners($heap_graph(S), HOBJECT n_original) = 3',
            'S.EVENTS = [OUTPUT $ptascii("R|"), OUTPUT $ptascii("G|")]', *ADMISSION, *ONE,
            'S_one.TODO = (THROW_SEARCH n_error) :: '
            '(YIELD_FROM_AGGREGATE pyieldfromaggregate_error "getIterator-error") :: ptask_tail*',
            'pyieldfromaggregate_error = pyieldfromaggregate[.CURRENT = KNOWN (POBJECT n_original)]',
            '$task_nodes(YIELD_FROM_AGGREGATE pyieldfromaggregate_error "getIterator-error") = [HOBJECT n_original, HOBJECT n_original]',
            '$throwable_field(S_one, n_error, "line") = PINT 19',
            '$string_bytes($throwable_field(S_one, n_error, "message")) = '
            '($ptascii("Objects returned by YieldFromCompareImmutableAggregate20::getIterator() must be traversable or implement interface Iterator"))',
            '$heap_owners($heap_graph(S_one), HOBJECT n_original) = 3', *POST,
        ],
    },
    'yield-from-immutable-source-cannot-forge-a-first-repeated-layer': {
        'source': SOURCES['yield-from-source-compare-immutable-original-self-rejection'], 'stage': GETTER,
        'checks': [
            *HEADER, 'pyieldfromaggregate.ACQUIRED = eps',
            'pyieldfromaggregate.INPUT = KNOWN (POBJECT n_original)', 'n_return = n_original',
            '$yield_from_aggregate_acquisition_valid(S, pyieldfromaggregate)', *ADMISSION,
            'pyieldfromaggregate_bad = pyieldfromaggregate[.ACQUIRED = [n_original]]',
            'S_bad = S[.TODO = (YIELD_FROM_AGGREGATE pyieldfromaggregate_bad "getIterator") :: ptask_tail*]',
            '$task_nodes(YIELD_FROM_AGGREGATE pyieldfromaggregate_bad "getIterator") = [HOBJECT n_original, HOBJECT n_original]',
            '$heap_valid($heap_graph(S_bad))',
            '~$yield_from_aggregate_acquisition_valid(S_bad, pyieldfromaggregate_bad)',
            '~$yield_from_aggregate_valid(S_bad, pyieldfromaggregate_bad, "getIterator")',
            '~$call_descriptors_valid(S_bad)',
        ],
    },
    'yield-from-mutable-source-cannot-forge-a-deeper-adjacent-repeat': {
        'source': SOURCES['yield-from-source-compare-kept-receiver-repeat-rechange'], 'stage': DEEP,
        'checks': [
            *DEEP_HEADER, *CV, 'z = 31', '$useriter_instance(S, n_return)', *ADMISSION,
            'pyieldfromaggregate_bad = pyieldfromaggregate[.ACQUIRED = [n_original, n_original]]',
            'S_bad = S[.TODO = (YIELD_FROM_AGGREGATE pyieldfromaggregate_bad "getIterator") :: ptask_tail*]',
            '$heap_owners($heap_graph(S_bad), HOBJECT n_original) = 3',
            '$heap_valid($heap_graph(S_bad))',
            '~$yield_from_aggregate_acquisition_valid(S_bad, pyieldfromaggregate_bad)',
            '~$yield_from_aggregate_valid(S_bad, pyieldfromaggregate_bad, "getIterator")',
            '~$call_descriptors_valid(S_bad)',
        ],
    },
    'yield-from-distinct-acquired-layer-retires-before-generator-startup': {
        'source': SOURCES['yield-from-source-compare-distinct-aggregate-generator'],
        'stage': GETTER + ' -- if S.OBJECTS[n_return] = GENERATOR pgenerator_data',
        'checks': [
            'n_original = pyieldfromaggregate.AGGREGATE', *KEEPER, *CV, 'z = 22',
            'pyieldfromaggregate.LINE = z', 'pyieldfromaggregate.ACQUIRED = [n_inner]',
            'pyieldfromaggregate.OBJECT = n_inner', 'n_inner =/= n_original',
            'pyieldfromaggregate.CURRENT = KNOWN PNULL',
            '$yield_from_receipt_valid(S, $yield_from_aggregate_receipt(S, pyieldfromaggregate))',
            '$yield_from_aggregate_self_object(S, pyieldfromaggregate) = (n_inner)',
            '$yield_from_aggregate_acquisition_valid(S, pyieldfromaggregate)',
            'pgenerator_data.PHASE = GENERATOR_FRESH', 'pgenerator_data.VALUE = eps',
            'S.EVENTS = [OUTPUT $ptascii("G|"), OUTPUT $ptascii("N|")]', *ADMISSION, *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(YIELD_FROM_AGGREGATE pyieldfromaggregate_data "acquired") :: ptask_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_inner)]',
            'pyieldfromaggregate_data = pyieldfromaggregate[.OBJECT = n_return][.ACQUIRED = eps]',
            'S_one.OBJECTS[n_return] = GENERATOR pgenerator_data',
            '$task_nodes(YIELD_FROM_AGGREGATE pyieldfromaggregate_data "acquired") = [HOBJECT n_return]',
            '$heap_owners($heap_graph(S_one), HOBJECT n_return) = 1',
            'S_one.ITERATORS = S.ITERATORS', 'S_one.NEXTITER = S.NEXTITER',
            '$destructor_release_valid(S_one, pdestructionrelease)', *POST,
        ],
    },
    'yield-from-repeated-parked-getter-keeps-raw-layer-and-borrows-current-receiver': {
        'source': SOURCES['yield-from-source-compare-repeated-getter-parks'], 'stage': PARK,
        'checks': [
            *PARK_VIEW, *KEEPER,
            '$target_nodes(pcallcontext_get.TARGET) = eps',
            '$call_context_roots(pfibervm.CURRENT) = eps',
            '$task_nodes(YIELD_FROM_AGGREGATE pyieldfromaggregate "getIterator") = [HOBJECT n_original]',
            '$heap_owners($heap_graph(S), HOBJECT n_original) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_first) = 0',
            '$fiber_vm_valid(S, pfibervm, (n_fiber), eps)', *ADMISSION, *ZERO,
        ],
    },
    'yield-from-repeated-parked-frame-rejects-duplicate-real-acquisition-marker': {
        'source': SOURCES['yield-from-source-compare-repeated-getter-parks'], 'stage': PARK,
        'checks': [
            *PARK_VIEW, '$fiber_vm_valid(S, pfibervm, (n_fiber), eps)', *ADMISSION,
            'pframe_bad = pframe_getter[.TODO = (YIELD_FROM_AGGREGATE pyieldfromaggregate "getIterator") :: '
            '(YIELD_FROM_AGGREGATE pyieldfromaggregate "getIterator") :: ptask_parent*]',
            'pfibervm_bad = pfibervm[.FRAMES = pframe_bad :: pframe_resumers*]',
            'S_bad = S[.OBJECTS[n_fiber] = FIBER pfiber[.VM = (pfibervm_bad)]]',
            'S_view_bad = $fiber_vm_restore(S_bad, pfibervm_bad)[.ACTIVEFIBER = (n_fiber)]'
            '[.FIBERCALLERS = eps][.COMPLETION = NORMAL]',
            'S_scope_bad = $constant_frame_scope(S_view_bad, pframe_bad, pframe_resumers*)',
            '$yield_from_aggregate_count(pframe_bad.TODO, pyieldfromaggregate.SITE) = 2',
            '$heap_owners($heap_graph(S_bad), HOBJECT n_original) = 3',
            '$heap_valid($heap_graph(S_bad))',
            '~$yield_from_aggregate_valid(S_scope_bad, pyieldfromaggregate, "getIterator")',
            '~$yield_from_aggregate_frame(S_view_bad, pcallcontext_get, pframe_bad)',
            '~$fiber_vm_valid(S_bad, pfibervm_bad, (n_fiber), eps)',
            '~$call_descriptors_valid(S_bad)',
        ],
    },
    'yield-from-repeated-getter-throw-releases-layer-with-original-exception': {
        'source': SOURCES['yield-from-source-compare-repeated-getter-throws'],
        'stage': ('S.TODO = (THROW_SEARCH n_error) :: '
                  '(YIELD_FROM_AGGREGATE pyieldfromaggregate "getIterator") :: ptask_tail*'),
        'checks': [
            *DEEP_HEADER, *KEEPER, *CV, 'z = 22', 'pyieldfromaggregate.LINE = z',
            '$lookup(S.ENV, $ptascii("failure")) = (n_failure)',
            'S.STORE[n_failure] = DEFINED (POBJECT n_error)',
            '$heap_owners($heap_graph(S), HOBJECT n_error) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_original) = 2',
            'S.EVENTS = [OUTPUT $ptascii("G0|"), OUTPUT $ptascii("G1|"), OUTPUT $ptascii("Q|")]',
            *ADMISSION, *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (THROW_SEARCH n_error) :: ptask_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_original)]',
            'pdestructionrelease.CALLER = S.CURRENT',
            'pdestructionrelease.ORIGIN = (pyieldfromaggregate.SITE)',
            '$destructor_release_valid(S_one, pdestructionrelease)',
            'S_one.EVENTS = S.EVENTS',
            '$heap_owners($heap_graph(S_one), HOBJECT n_error) = 2',
            '$heap_owners($heap_graph(S_one), HOBJECT n_original) = 2', *POST,
        ],
    },
    'yield-from-live-cv-source-equality-now-rejects-the-affected-original-control': {
        'source': SOURCES['yield-from-rebound-returned-aggregate-self-control'], 'stage': GETTER,
        'checks': [
            *HEADER, *KEEPER, *CV, 'pyieldfromaggregate.ACQUIRED = eps', 'z = 26',
            'pyieldfromaggregate.LINE = z', 'S.STORE[n_input] = DEFINED (POBJECT n_return)',
            'n_return =/= n_original', '$generator_from_aggregate(S, POBJECT n_return)',
            '~$yield_from_aggregate_input_stable(S, pyieldfromaggregate)',
            '~$yield_from_aggregate_no_self_check(S, S.RESULT)',
            '$yield_from_aggregate_self_object(S, pyieldfromaggregate) = (n_return)',
            '$yield_from_aggregate_valid(S, pyieldfromaggregate, "getIterator")',
            'S.EVENTS = [OUTPUT $ptascii("G|")]', *ADMISSION, *ONE,
            'S_one.TODO = (THROW_SEARCH n_error) :: '
            '(YIELD_FROM_AGGREGATE pyieldfromaggregate_error "getIterator-error") :: ptask_tail*',
            'pyieldfromaggregate_error = pyieldfromaggregate[.CURRENT = KNOWN (POBJECT n_return)]',
            '$task_nodes(YIELD_FROM_AGGREGATE pyieldfromaggregate_error "getIterator-error") = [HOBJECT n_return]',
            'S_one.OBJECTS[n_error] = THROWABLE pthrowable', 'pthrowable.KIND = "Exception"',
            '$throwable_field(S_one, n_error, "line") = PINT 26',
            '$string_bytes($throwable_field(S_one, n_error, "message")) = '
            '($ptascii("Objects returned by ReboundControlAggregate20::getIterator() must be traversable or implement interface Iterator"))',
            'S_one.EVENTS = S.EVENTS', *POST,
        ],
    },
    'yield-from-nonobject-source-with-aggregate-return-keeps-named-refusal': {
        'source': SOURCES['yield-from-source-compare-nonobject-original-control'], 'stage': GETTER,
        'checks': [
            *HEADER, *KEEPER, *CV, 'pyieldfromaggregate.ACQUIRED = eps', 'z = 26',
            'pyieldfromaggregate.LINE = z', 'S.STORE[n_input] = DEFINED PNULL',
            'n_return =/= n_original', '$generator_from_aggregate(S, POBJECT n_return)',
            '~$yield_from_aggregate_input_stable(S, pyieldfromaggregate)',
            '~$yield_from_aggregate_no_self_check(S, S.RESULT)',
            '$yield_from_aggregate_self_object(S, pyieldfromaggregate) = eps',
            'S.EVENTS = [OUTPUT $ptascii("G|")]', *ADMISSION, *ONE,
            'S_one.TODO = [ERROR_UNWIND (UNSUPPORTED "yield from IteratorAggregate changed original operand")]',
            'S_one.EVENTS = S.EVENTS',
        ],
    },
}

CASES.update({
    'yield-from-deeper-self-comparison-rejects-owned-original-again': {
        'source': SOURCES['yield-from-source-compare-deeper-self-rejection'],
        'stage': 'S.TODO = (YIELD_FROM_AGGREGATE pyieldfromaggregate "getIterator") :: ptask_tail* -- if S.RESULT = KNOWN (POBJECT n_return) -- if pyieldfromaggregate.ACQUIRED = [pyieldfromaggregate.AGGREGATE] -- if n_return = pyieldfromaggregate.AGGREGATE',
        'checks': ['n_original = pyieldfromaggregate.AGGREGATE',
         'pyieldfromaggregate.OBJECT = n_original',
         'pyieldfromaggregate.CURRENT = KNOWN PNULL',
              '$yield_from_receipt_valid(S, $yield_from_aggregate_receipt(S, pyieldfromaggregate))',
         'S_global = $global_table_view(S)',
         '$lookup(S_global.ENV, $ptascii("keeper")) = (n_keeper)',
         'S.STORE[n_keeper] = DEFINED (POBJECT n_original)',
         'pyieldfromaggregate.INPUT = VARIABLE ($ptascii("slot")) z',
         '$lookup(S.ENV, $ptascii("slot")) = (n_input)',
         'n_input <- S.REFCELLS',
         'z = 29',
         'pyieldfromaggregate.LINE = z',
         'pyieldfromaggregate.ACQUIRED = [n_original]',
         'n_return = n_original',
         'S.STORE[n_input] = DEFINED (POBJECT n_payload)',
         'n_payload =/= n_original',
         '$yield_from_aggregate_self_object(S, pyieldfromaggregate) = (n_original)',
         '$yield_from_aggregate_acquisition_valid(S, pyieldfromaggregate)',
         '$task_nodes(YIELD_FROM_AGGREGATE pyieldfromaggregate "getIterator") = [HOBJECT n_original]',
         '$heap_owners($heap_graph(S), HOBJECT n_original) = 3',
         'S.EVENTS = [OUTPUT $ptascii("G0|"), OUTPUT $ptascii("G1|")]',
         'S.YIELDRETAINED = eps',
         '$call_descriptors_valid(S)',
         '$heap_valid($heap_graph(S))',
         'S_one_budget = $drive_steps(S, 1)',
         'S_one_budget.COMPLETION = BUDGET',
         'S_one = S_one_budget[.COMPLETION = NORMAL]',
         'S_one.TODO = (THROW_SEARCH n_error) :: (YIELD_FROM_AGGREGATE pyieldfromaggregate_error "getIterator-error") '
         ':: ptask_tail*',
         'pyieldfromaggregate_error = pyieldfromaggregate[.CURRENT = KNOWN (POBJECT n_original)]',
         '$task_nodes(YIELD_FROM_AGGREGATE pyieldfromaggregate_error "getIterator-error") = [HOBJECT n_original, '
         'HOBJECT n_original]',
         'S_one.OBJECTS[n_error] = THROWABLE pthrowable',
         'pthrowable.KIND = "Exception"',
         '$throwable_field(S_one, n_error, "line") = PINT 29',
         '$string_bytes($throwable_field(S_one, n_error, "message")) = ($ptascii("Objects returned by '
         'YieldFromCompareDeepRejectAggregate20::getIterator() must be traversable or implement interface '
         'Iterator"))',
         '$heap_owners($heap_graph(S_one), HOBJECT n_original) = 3',
         'S_one.EVENTS = S.EVENTS',
         'S_one.YIELDRETAINED = eps',
         '$call_descriptors_valid(S_one)',
         '$heap_valid($heap_graph(S_one))'],
    },
    'yield-from-deeper-self-error-retires-both-raw-original-occurrences': {
        'source': SOURCES['yield-from-source-compare-deeper-self-rejection'],
        'stage': 'S.TODO = (THROW_SEARCH n_error) :: (YIELD_FROM_AGGREGATE pyieldfromaggregate "getIterator-error") :: ptask_tail*',
        'checks': ['n_original = pyieldfromaggregate.AGGREGATE',
         'pyieldfromaggregate.OBJECT = n_original',
              '$yield_from_receipt_valid(S, $yield_from_aggregate_receipt(S, pyieldfromaggregate))',
         'S_global = $global_table_view(S)',
         '$lookup(S_global.ENV, $ptascii("keeper")) = (n_keeper)',
         'S.STORE[n_keeper] = DEFINED (POBJECT n_original)',
         'pyieldfromaggregate.INPUT = VARIABLE ($ptascii("slot")) z',
         '$lookup(S.ENV, $ptascii("slot")) = (n_input)',
         'n_input <- S.REFCELLS',
         'z = 29',
         'pyieldfromaggregate.LINE = z',
         'pyieldfromaggregate.ACQUIRED = [n_original]',
         'pyieldfromaggregate.CURRENT = KNOWN (POBJECT n_original)',
         '$yield_from_aggregate_acquisition_valid(S, pyieldfromaggregate)',
         '$task_nodes(YIELD_FROM_AGGREGATE pyieldfromaggregate "getIterator-error") = [HOBJECT n_original, HOBJECT '
         'n_original]',
         '$heap_owners($heap_graph(S), HOBJECT n_original) = 3',
         '$throwable_field(S, n_error, "line") = PINT 29',
         'S.EVENTS = [OUTPUT $ptascii("G0|"), OUTPUT $ptascii("G1|")]',
         'S.YIELDRETAINED = eps',
         '$call_descriptors_valid(S)',
         '$heap_valid($heap_graph(S))',
         'S_one_budget = $drive_steps(S, 1)',
         'S_one_budget.COMPLETION = BUDGET',
         'S_one = S_one_budget[.COMPLETION = NORMAL]',
         'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (THROW_SEARCH n_error) :: ptask_tail*',
         'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_original), DESTRUCTION_VALUE (HOBJECT '
         'n_original)]',
         'pdestructionrelease.CALLER = S.CURRENT',
         'pdestructionrelease.ORIGIN = (pyieldfromaggregate.SITE)',
         '$destructor_release_valid(S_one, pdestructionrelease)',
         '$heap_owners($heap_graph(S_one), HOBJECT n_original) = 3',
         'S_one.EVENTS = S.EVENTS',
         'S_one.YIELDRETAINED = eps',
         '$call_descriptors_valid(S_one)',
         '$heap_valid($heap_graph(S_one))'],
    },
})

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
            'yield-from source comparison review inputs changed during run'
        if not passed:
            break
    raise SystemExit(0 if passed else 1)
