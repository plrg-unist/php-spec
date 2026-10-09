#!/usr/bin/env python3
"""Genuine foreach mutable-source self comparison and recursive owner checks."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import fiber_state_review as review

CATALOG = Path(__file__).with_name('foreach_source_compare_cases.json')
INPUT_BYTES = {path: path.read_bytes() for path in (Path(__file__), Path(review.__file__), CATALOG)}
SOURCES = {row['id']: row['source'] for row in json.loads(INPUT_BYTES[CATALOG])}
ADMISSION = ['$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
POST = ['$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))']
ONE = ['S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
       'S_one = S_one_budget[.COMPLETION = NORMAL]']
ZERO = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S']
HEADER = ['n_original = pforeachaggregate.AGGREGATE',
          'pforeachaggregate.OBJECT = n_original',
          'pforeachaggregate.CURRENT = KNOWN PNULL',
          'pforeachaggregate.ITERATOR = eps',
          '$foreach_aggregate_site(S, pforeachaggregate.STATEMENT, '
          'pforeachaggregate.SITE, pforeachaggregate.LINE)']
KEEPER = ['S_global = $global_table_view(S)',
          '$lookup(S_global.ENV, $ptascii("keeper")) = (n_keeper)',
          'S.STORE[n_keeper] = DEFINED (POBJECT n_original)']
CV = ['pforeachaggregate.INPUT = VARIABLE ($ptascii("slot")) z',
      '$lookup(S.ENV, $ptascii("slot")) = (n_input)',
      'n_input <- S.REFCELLS']
FIRST = ['pforeachaggregate.ACQUIRED = eps',
         'S.STORE[n_input] = DEFINED (POBJECT n_payload)',
         'n_payload =/= n_original',
         '~$generator_from_aggregate(S, POBJECT n_payload)',
         '$foreach_aggregate_self_object(S, pforeachaggregate) = (n_payload)',
         '~$foreach_aggregate_input_stable(S, pforeachaggregate)',
         '$foreach_aggregate_mutable_input(pforeachaggregate.INPUT)']
RECURSE = [
    'S_one.TODO = (CALL_ARGS pcalltarget eps 0 eps (pforeachaggregate.SITE) '
    'pforeachaggregate.LINE) :: (FOREACH_AGGREGATE pforeachaggregate_next "getIterator") :: ptask_tail*',
    'pcalltarget = AGGREGATE_METHOD_TARGET n_original porigin_get',
    '$fiber_traversal_method_selected(S_one, n_original, porigin_get, "getIterator")',
    '$target_nodes(pcalltarget) = eps',
    'pforeachaggregate_next = pforeachaggregate[.ACQUIRED = [n_original]]',
    '$foreach_aggregate_acquisition_valid(S_one, pforeachaggregate_next)',
    '~$fiber_traversal_acquisition_valid(S_one, n_original, [n_original])',
    '$heap_owners($heap_graph(S_one), HOBJECT n_original) = 2',
    'S_one.STORE[n_input] = S.STORE[n_input]',
    'S_one.ITERATORS = S.ITERATORS', 'S_one.NEXTITER = S.NEXTITER',
]
GETTER = ('S.TODO = (FOREACH_AGGREGATE pforeachaggregate "getIterator") :: '
          'ptask_tail* -- if S.RESULT = KNOWN (POBJECT n_return)')
DEEP = (GETTER + ' -- if pforeachaggregate.ACQUIRED = [pforeachaggregate.AGGREGATE]')
DEEP_HEADER = [*HEADER, 'pforeachaggregate.ACQUIRED = [n_original]',
               '$foreach_aggregate_acquisition_valid(S, pforeachaggregate)',
               '$foreach_aggregate_self_object(S, pforeachaggregate) = (n_original)',
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
        '(FOREACH_AGGREGATE pforeachaggregate "getIterator") :: ptask_parent*')
PARK_VIEW = [
    'n_original = pforeachaggregate.AGGREGATE',
    'pforeachaggregate.OBJECT = n_original',
    'pforeachaggregate.ACQUIRED = [n_original]',
    'pforeachaggregate.CURRENT = KNOWN PNULL',
    'pforeachaggregate.ITERATOR = eps',
    'pforeachaggregate.INPUT = VARIABLE ($ptascii("slot")) 33',
    'pforeachaggregate.LINE = 33',
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
    '$foreach_aggregate_self_object(S_scope, pforeachaggregate) = (n_original)',
    '$foreach_aggregate_acquisition_valid(S_scope, pforeachaggregate)',
    '$foreach_aggregate_frame(S_view, pcallcontext_get, pframe_getter)',
]

CASES = {
    'foreach-cv-self-comparison-permits-first-kept-original-repeat': {
        'source': SOURCES['foreach-source-compare-kept-receiver-repeat-rechange'], 'stage': GETTER,
        'checks': [
            *HEADER, *KEEPER, *CV, 'z = 31', 'pforeachaggregate.LINE = z',
            *FIRST, 'n_return = n_original',
            '$heap_owners($heap_graph(S), HOBJECT n_original) = 2',
            '$task_nodes(FOREACH_AGGREGATE pforeachaggregate "getIterator") = eps',
            'S.EVENTS = [OUTPUT $ptascii("G0|")]', *ADMISSION, *ONE, *RECURSE,
            '$task_nodes(FOREACH_AGGREGATE pforeachaggregate_next "getIterator") = [HOBJECT n_original]',
            *POST,
        ],
    },
    'foreach-reference-self-comparison-permits-first-kept-original-repeat': {
        'source': SOURCES['foreach-source-compare-reference-repeat-rechange'], 'stage': GETTER,
        'checks': [
            *HEADER, *KEEPER, 'pforeachaggregate.LINE = 32',
            'pforeachaggregate.INPUT = REFERENCE n_input', 'n_input <- S.REFCELLS',
            *FIRST, 'n_return = n_original',
            '$heap_owners($heap_graph(S), HCELL n_input) = 3',
            '$heap_owners($heap_graph(S), HOBJECT n_original) = 2',
            '$task_nodes(FOREACH_AGGREGATE pforeachaggregate "getIterator") = [HCELL n_input]',
            'S.EVENTS = [OUTPUT $ptascii("R|"), OUTPUT $ptascii("G0|")]',
            *ADMISSION, *ONE, *RECURSE,
            '$task_nodes(FOREACH_AGGREGATE pforeachaggregate_next "getIterator") = [HOBJECT n_original, HCELL n_input]',
            '$heap_owners($heap_graph(S_one), HCELL n_input) = 3', *POST,
        ],
    },
    'foreach-deeper-acquisition-uses-owned-layer-after-earlier-payload-retirement': {
        'source': SOURCES['foreach-source-compare-kept-receiver-repeat-rechange'], 'stage': DEEP,
        'checks': [
            *DEEP_HEADER, *KEEPER, *CV, 'z = 31', 'pforeachaggregate.LINE = z',
            'S.STORE[n_input] = DEFINED (POBJECT n_payload)', 'n_payload =/= n_original',
            'n_return = n_data', '$useriter_instance(S, n_data)',
            '$task_nodes(FOREACH_AGGREGATE pforeachaggregate "getIterator") = [HOBJECT n_original]',
            '$heap_owners($heap_graph(S), HOBJECT n_original) = 2',
            'S.EVENTS = [OUTPUT $ptascii("G0|"), OUTPUT $ptascii("G1|"), OUTPUT $ptascii("Q|")]',
            *ADMISSION, *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(FOREACH_AGGREGATE pforeachaggregate_data "acquired") :: ptask_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_original)]',
            'pdestructionrelease.CALLER = S.CURRENT', 'pdestructionrelease.ORIGIN = S.ORIGIN',
            'pforeachaggregate_data = pforeachaggregate[.OBJECT = n_data][.ACQUIRED = eps]',
            '$task_nodes(FOREACH_AGGREGATE pforeachaggregate_data "acquired") = [HOBJECT n_data]',
            '$heap_owners($heap_graph(S_one), HOBJECT n_data) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_original) = 2',
            'S_one.STORE[n_input] = S.STORE[n_input]',
            'S_one.ITERATORS = S.ITERATORS', 'S_one.NEXTITER = S.NEXTITER',
            '$destructor_release_valid(S_one, pdestructionrelease)', *POST,
        ],
    },
    'foreach-repeated-reference-retains-input-through-first-valid-then-releases-cell': {
        'source': SOURCES['foreach-source-compare-reference-repeat-rechange'],
        'stage': 'S.TODO = (FOREACH_AGGREGATE pforeachaggregate "ready") :: ptask_tail*',
        'checks': [
            'n_original = pforeachaggregate.AGGREGATE', *KEEPER,
            'pforeachaggregate.LINE = 32', 'pforeachaggregate.ACQUIRED = eps',
            'pforeachaggregate.CURRENT = KNOWN PNULL',
            'pforeachaggregate.INPUT = REFERENCE n_input', 'n_input <- S.REFCELLS',
            'S.STORE[n_input] = DEFINED (POBJECT n_payload)', 'n_payload =/= n_original',
            'n_data = pforeachaggregate.OBJECT', '$useriter_instance(S, n_data)',
            'pforeachaggregate.ITERATOR = (n_cursor)',
            '$iterator_lookup(S.ITERATORS, n_cursor) = (OBJECTITER n_cursor n_data 0 false)',
            '$task_nodes(FOREACH_AGGREGATE pforeachaggregate "ready") = [HOBJECT n_data, HCELL n_input]',
            '$heap_owners($heap_graph(S), HCELL n_input) = 3',
            '$heap_owners($heap_graph(S), HOBJECT n_original) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_data) = 1',
            'S.EVENTS = [OUTPUT $ptascii("R|"), OUTPUT $ptascii("G0|"), OUTPUT $ptascii("G1|"), '
            'OUTPUT $ptascii("Q|"), OUTPUT $ptascii("W|"), OUTPUT $ptascii("V|")]',
            *ADMISSION, *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(FOREACH_AGGREGATE pforeachaggregate_current "current") :: ptask_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HCELL n_input)]',
            'pdestructionrelease.CALLER = S.CURRENT', 'pdestructionrelease.ORIGIN = S.ORIGIN',
            'pforeachaggregate_current = pforeachaggregate[.INPUT = KNOWN PNULL]',
            '$task_nodes(FOREACH_AGGREGATE pforeachaggregate_current "current") = [HOBJECT n_data]',
            'S_one.STORE[n_input] = S.STORE[n_input]',
            '$heap_owners($heap_graph(S_one), HOBJECT n_data) = 1',
            '$destructor_release_valid(S_one, pdestructionrelease)', *POST,
        ],
    },
    'foreach-live-reference-source-equality-rejects-returned-aggregate': {
        'source': SOURCES['foreach-source-compare-reference-self-rejection'], 'stage': GETTER,
        'checks': [
            *HEADER, *KEEPER, 'pforeachaggregate.ACQUIRED = eps', 'pforeachaggregate.LINE = 26',
            'pforeachaggregate.INPUT = REFERENCE n_input', 'n_input <- S.REFCELLS',
            'S.STORE[n_input] = DEFINED (POBJECT n_return)', 'n_return =/= n_original',
            '$generator_from_aggregate(S, POBJECT n_return)',
            '$foreach_aggregate_self_object(S, pforeachaggregate) = (n_return)',
            '~$foreach_aggregate_input_stable(S, pforeachaggregate)',
            '$heap_owners($heap_graph(S), HCELL n_input) = 3',
            '$heap_owners($heap_graph(S), HOBJECT n_original) = 1',
            'S.EVENTS = [OUTPUT $ptascii("R|"), OUTPUT $ptascii("G|")]',
            *ADMISSION, *ONE,
            'S_one.TODO = (THROW_SEARCH n_error) :: '
            '(FOREACH_AGGREGATE pforeachaggregate_error "getIterator-error") :: ptask_tail*',
            'pforeachaggregate_error = pforeachaggregate[.CURRENT = KNOWN (POBJECT n_return)]',
            '$task_nodes(FOREACH_AGGREGATE pforeachaggregate_error "getIterator-error") = [HOBJECT n_return, HCELL n_input]',
            'S_one.OBJECTS[n_error] = THROWABLE pthrowable', 'pthrowable.KIND = "Exception"',
            '$throwable_field(S_one, n_error, "line") = PINT 26',
            '$string_bytes($throwable_field(S_one, n_error, "message")) = '
            '($ptascii("Objects returned by ForeachCompareRejectOuter20::getIterator() must be traversable or implement interface Iterator"))',
            'S_one.STORE[n_input] = S.STORE[n_input]',
            '$heap_owners($heap_graph(S_one), HOBJECT n_original) = 1', *POST,
        ],
    },
    'foreach-immutable-temporary-compares-its-own-input-despite-global-rebind': {
        'source': SOURCES['foreach-source-compare-immutable-original-self-rejection'], 'stage': GETTER,
        'checks': [
            *HEADER, *KEEPER, 'pforeachaggregate.ACQUIRED = eps', 'pforeachaggregate.LINE = 19',
            'pforeachaggregate.INPUT = KNOWN (POBJECT n_original)', 'n_return = n_original',
            '$lookup(S.ENV, $ptascii("slot")) = (n_input)',
            'S.STORE[n_input] = DEFINED (POBJECT n_payload)', 'n_payload =/= n_original',
            '$foreach_aggregate_self_object(S, pforeachaggregate) = (n_original)',
            '~$foreach_aggregate_mutable_input(pforeachaggregate.INPUT)',
            '$task_nodes(FOREACH_AGGREGATE pforeachaggregate "getIterator") = [HOBJECT n_original]',
            '$heap_owners($heap_graph(S), HOBJECT n_original) = 3',
            'S.EVENTS = [OUTPUT $ptascii("R|"), OUTPUT $ptascii("G|")]', *ADMISSION, *ONE,
            'S_one.TODO = (THROW_SEARCH n_error) :: '
            '(FOREACH_AGGREGATE pforeachaggregate_error "getIterator-error") :: ptask_tail*',
            'pforeachaggregate_error = pforeachaggregate[.CURRENT = KNOWN (POBJECT n_original)]',
            '$task_nodes(FOREACH_AGGREGATE pforeachaggregate_error "getIterator-error") = [HOBJECT n_original, HOBJECT n_original]',
            '$throwable_field(S_one, n_error, "line") = PINT 19',
            '$string_bytes($throwable_field(S_one, n_error, "message")) = '
            '($ptascii("Objects returned by ForeachCompareImmutableAggregate20::getIterator() must be traversable or implement interface Iterator"))',
            '$heap_owners($heap_graph(S_one), HOBJECT n_original) = 3', *POST,
        ],
    },
    'foreach-immutable-source-cannot-forge-a-first-repeated-layer': {
        'source': SOURCES['foreach-source-compare-immutable-original-self-rejection'], 'stage': GETTER,
        'checks': [
            *HEADER, 'pforeachaggregate.ACQUIRED = eps',
            'pforeachaggregate.INPUT = KNOWN (POBJECT n_original)', 'n_return = n_original',
            '$foreach_aggregate_acquisition_valid(S, pforeachaggregate)', *ADMISSION,
            'pforeachaggregate_bad = pforeachaggregate[.ACQUIRED = [n_original]]',
            'S_bad = S[.TODO = (FOREACH_AGGREGATE pforeachaggregate_bad "getIterator") :: ptask_tail*]',
            '$task_nodes(FOREACH_AGGREGATE pforeachaggregate_bad "getIterator") = [HOBJECT n_original, HOBJECT n_original]',
            '$heap_valid($heap_graph(S_bad))',
            '~$foreach_aggregate_acquisition_valid(S_bad, pforeachaggregate_bad)',
            '~$foreach_aggregate_valid(S_bad, pforeachaggregate_bad, "getIterator")',
            '~$call_descriptors_valid(S_bad)',
        ],
    },
    'foreach-mutable-source-cannot-forge-a-deeper-adjacent-repeat': {
        'source': SOURCES['foreach-source-compare-kept-receiver-repeat-rechange'], 'stage': DEEP,
        'checks': [
            *DEEP_HEADER, *CV, 'z = 31', '$useriter_instance(S, n_return)', *ADMISSION,
            'pforeachaggregate_bad = pforeachaggregate[.ACQUIRED = [n_original, n_original]]',
            'S_bad = S[.TODO = (FOREACH_AGGREGATE pforeachaggregate_bad "getIterator") :: ptask_tail*]',
            '$heap_owners($heap_graph(S_bad), HOBJECT n_original) = 3',
            '$heap_valid($heap_graph(S_bad))',
            '~$foreach_aggregate_acquisition_valid(S_bad, pforeachaggregate_bad)',
            '~$foreach_aggregate_valid(S_bad, pforeachaggregate_bad, "getIterator")',
            '~$call_descriptors_valid(S_bad)',
        ],
    },
    'foreach-distinct-acquired-layer-retires-before-generator-startup': {
        'source': SOURCES['foreach-source-compare-distinct-aggregate-generator'],
        'stage': GETTER + ' -- if S.OBJECTS[n_return] = GENERATOR pgenerator_data',
        'checks': [
            'n_original = pforeachaggregate.AGGREGATE', *KEEPER, *CV, 'z = 22',
            'pforeachaggregate.LINE = z', 'pforeachaggregate.ACQUIRED = [n_inner]',
            'pforeachaggregate.OBJECT = n_inner', 'n_inner =/= n_original',
            'pforeachaggregate.CURRENT = KNOWN PNULL', 'pforeachaggregate.ITERATOR = eps',
            '$foreach_aggregate_self_object(S, pforeachaggregate) = (n_inner)',
            '$foreach_aggregate_acquisition_valid(S, pforeachaggregate)',
            'pgenerator_data.PHASE = GENERATOR_FRESH', 'pgenerator_data.VALUE = eps',
            'S.EVENTS = [OUTPUT $ptascii("G|"), OUTPUT $ptascii("N|")]', *ADMISSION, *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(FOREACH_AGGREGATE pforeachaggregate_data "acquired") :: ptask_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_inner)]',
            'pforeachaggregate_data = pforeachaggregate[.OBJECT = n_return][.ACQUIRED = eps]',
            'S_one.OBJECTS[n_return] = GENERATOR pgenerator_data',
            '$task_nodes(FOREACH_AGGREGATE pforeachaggregate_data "acquired") = [HOBJECT n_return]',
            '$heap_owners($heap_graph(S_one), HOBJECT n_return) = 1',
            'S_one.ITERATORS = S.ITERATORS', 'S_one.NEXTITER = S.NEXTITER',
            '$destructor_release_valid(S_one, pdestructionrelease)', *POST,
        ],
    },
    'foreach-repeated-parked-getter-keeps-raw-layer-and-borrows-current-receiver': {
        'source': SOURCES['foreach-source-compare-repeated-getter-parks'], 'stage': PARK,
        'checks': [
            *PARK_VIEW, *KEEPER,
            '$target_nodes(pcallcontext_get.TARGET) = eps',
            '$call_context_roots(pfibervm.CURRENT) = eps',
            '$task_nodes(FOREACH_AGGREGATE pforeachaggregate "getIterator") = [HOBJECT n_original]',
            '$heap_owners($heap_graph(S), HOBJECT n_original) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_first) = 0',
            '$fiber_vm_valid(S, pfibervm, (n_fiber), eps)', *ADMISSION, *ZERO,
        ],
    },
    'foreach-repeated-parked-frame-rejects-duplicate-real-acquisition-marker': {
        'source': SOURCES['foreach-source-compare-repeated-getter-parks'], 'stage': PARK,
        'checks': [
            *PARK_VIEW, '$fiber_vm_valid(S, pfibervm, (n_fiber), eps)', *ADMISSION,
            'pframe_bad = pframe_getter[.TODO = (FOREACH_AGGREGATE pforeachaggregate "getIterator") :: '
            '(FOREACH_AGGREGATE pforeachaggregate "getIterator") :: ptask_parent*]',
            'pfibervm_bad = pfibervm[.FRAMES = pframe_bad :: pframe_resumers*]',
            'S_bad = S[.OBJECTS[n_fiber] = FIBER pfiber[.VM = (pfibervm_bad)]]',
            'S_view_bad = $fiber_vm_restore(S_bad, pfibervm_bad)[.ACTIVEFIBER = (n_fiber)]'
            '[.FIBERCALLERS = eps][.COMPLETION = NORMAL]',
            'S_scope_bad = $constant_frame_scope(S_view_bad, pframe_bad, pframe_resumers*)',
            '$foreach_aggregate_count(pframe_bad.TODO, pforeachaggregate.SITE) = 2',
            '$heap_owners($heap_graph(S_bad), HOBJECT n_original) = 3',
            '$heap_valid($heap_graph(S_bad))',
            '~$foreach_aggregate_valid(S_scope_bad, pforeachaggregate, "getIterator")',
            '~$foreach_aggregate_frame(S_view_bad, pcallcontext_get, pframe_bad)',
            '~$fiber_vm_valid(S_bad, pfibervm_bad, (n_fiber), eps)',
            '~$call_descriptors_valid(S_bad)',
        ],
    },
    'foreach-repeated-getter-throw-releases-layer-with-original-exception': {
        'source': SOURCES['foreach-source-compare-repeated-getter-throws'],
        'stage': ('S.TODO = (THROW_SEARCH n_error) :: '
                  '(FOREACH_AGGREGATE pforeachaggregate "getIterator") :: ptask_tail*'),
        'checks': [
            *DEEP_HEADER, *KEEPER, *CV, 'z = 22', 'pforeachaggregate.LINE = z',
            '$lookup(S.ENV, $ptascii("failure")) = (n_failure)',
            'S.STORE[n_failure] = DEFINED (POBJECT n_error)',
            '$heap_owners($heap_graph(S), HOBJECT n_error) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_original) = 2',
            'S.EVENTS = [OUTPUT $ptascii("G0|"), OUTPUT $ptascii("G1|"), OUTPUT $ptascii("Q|")]',
            *ADMISSION, *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (THROW_SEARCH n_error) :: ptask_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_original)]',
            'pdestructionrelease.CALLER = S.CURRENT',
            'pdestructionrelease.ORIGIN = (pforeachaggregate.SITE)',
            '$destructor_release_valid(S_one, pdestructionrelease)',
            'S_one.EVENTS = S.EVENTS',
            '$heap_owners($heap_graph(S_one), HOBJECT n_error) = 2',
            '$heap_owners($heap_graph(S_one), HOBJECT n_original) = 2', *POST,
        ],
    },
    'foreach-live-cv-source-equality-now-rejects-the-affected-original-control': {
        'source': SOURCES['foreach-rebound-returned-aggregate-self-control'], 'stage': GETTER,
        'checks': [
            *HEADER, *KEEPER, *CV, 'pforeachaggregate.ACQUIRED = eps', 'z = 26',
            'pforeachaggregate.LINE = z', 'S.STORE[n_input] = DEFINED (POBJECT n_return)',
            'n_return =/= n_original', '$generator_from_aggregate(S, POBJECT n_return)',
            '~$foreach_aggregate_input_stable(S, pforeachaggregate)',
            '~$foreach_aggregate_no_self_check(S, S.RESULT)',
            '$foreach_aggregate_self_object(S, pforeachaggregate) = (n_return)',
            '$foreach_aggregate_valid(S, pforeachaggregate, "getIterator")',
            'S.EVENTS = [OUTPUT $ptascii("G|")]', *ADMISSION, *ONE,
            'S_one.TODO = (THROW_SEARCH n_error) :: '
            '(FOREACH_AGGREGATE pforeachaggregate_error "getIterator-error") :: ptask_tail*',
            'pforeachaggregate_error = pforeachaggregate[.CURRENT = KNOWN (POBJECT n_return)]',
            '$task_nodes(FOREACH_AGGREGATE pforeachaggregate_error "getIterator-error") = [HOBJECT n_return]',
            'S_one.OBJECTS[n_error] = THROWABLE pthrowable', 'pthrowable.KIND = "Exception"',
            '$throwable_field(S_one, n_error, "line") = PINT 26',
            '$string_bytes($throwable_field(S_one, n_error, "message")) = '
            '($ptascii("Objects returned by ForeachReboundControlAggregate20::getIterator() must be traversable or implement interface Iterator"))',
            'S_one.EVENTS = S.EVENTS', *POST,
        ],
    },
    'foreach-nonobject-source-with-aggregate-return-keeps-named-refusal': {
        'source': SOURCES['foreach-source-compare-nonobject-original-control'], 'stage': GETTER,
        'checks': [
            *HEADER, *KEEPER, *CV, 'pforeachaggregate.ACQUIRED = eps', 'z = 26',
            'pforeachaggregate.LINE = z', 'S.STORE[n_input] = DEFINED PNULL',
            'n_return =/= n_original', '$generator_from_aggregate(S, POBJECT n_return)',
            '~$foreach_aggregate_input_stable(S, pforeachaggregate)',
            '~$foreach_aggregate_no_self_check(S, S.RESULT)',
            '$foreach_aggregate_self_object(S, pforeachaggregate) = eps',
            'S.EVENTS = [OUTPUT $ptascii("G|")]', *ADMISSION, *ONE,
            'S_one.TODO = [ERROR_UNWIND (UNSUPPORTED "foreach IteratorAggregate changed original operand")]',
            'S_one.EVENTS = S.EVENTS',
        ],
    },
}

CASES.update({
    'foreach-deeper-self-comparison-rejects-owned-original-again': {
        'source': SOURCES['foreach-source-compare-deeper-self-rejection'],
        'stage': 'S.TODO = (FOREACH_AGGREGATE pforeachaggregate "getIterator") :: ptask_tail* -- if S.RESULT = KNOWN (POBJECT n_return) -- if pforeachaggregate.ACQUIRED = [pforeachaggregate.AGGREGATE] -- if n_return = pforeachaggregate.AGGREGATE',
        'checks': ['n_original = pforeachaggregate.AGGREGATE',
         'pforeachaggregate.OBJECT = n_original',
         'pforeachaggregate.CURRENT = KNOWN PNULL',
         'pforeachaggregate.ITERATOR = eps',
         '$foreach_aggregate_site(S, pforeachaggregate.STATEMENT, pforeachaggregate.SITE, pforeachaggregate.LINE)',
         'S_global = $global_table_view(S)',
         '$lookup(S_global.ENV, $ptascii("keeper")) = (n_keeper)',
         'S.STORE[n_keeper] = DEFINED (POBJECT n_original)',
         'pforeachaggregate.INPUT = VARIABLE ($ptascii("slot")) z',
         '$lookup(S.ENV, $ptascii("slot")) = (n_input)',
         'n_input <- S.REFCELLS',
         'z = 29',
         'pforeachaggregate.LINE = z',
         'pforeachaggregate.ACQUIRED = [n_original]',
         'n_return = n_original',
         'S.STORE[n_input] = DEFINED (POBJECT n_payload)',
         'n_payload =/= n_original',
         '$foreach_aggregate_self_object(S, pforeachaggregate) = (n_original)',
         '$foreach_aggregate_acquisition_valid(S, pforeachaggregate)',
         '$task_nodes(FOREACH_AGGREGATE pforeachaggregate "getIterator") = [HOBJECT n_original]',
         '$heap_owners($heap_graph(S), HOBJECT n_original) = 3',
         'S.EVENTS = [OUTPUT $ptascii("G0|"), OUTPUT $ptascii("G1|")]',
         '$call_descriptors_valid(S)',
         '$heap_valid($heap_graph(S))',
         'S_one_budget = $drive_steps(S, 1)',
         'S_one_budget.COMPLETION = BUDGET',
         'S_one = S_one_budget[.COMPLETION = NORMAL]',
         'S_one.TODO = (THROW_SEARCH n_error) :: (FOREACH_AGGREGATE pforeachaggregate_error "getIterator-error") '
         ':: ptask_tail*',
         'pforeachaggregate_error = pforeachaggregate[.CURRENT = KNOWN (POBJECT n_original)]',
         '$task_nodes(FOREACH_AGGREGATE pforeachaggregate_error "getIterator-error") = [HOBJECT n_original, '
         'HOBJECT n_original]',
         'S_one.OBJECTS[n_error] = THROWABLE pthrowable',
         'pthrowable.KIND = "Exception"',
         '$throwable_field(S_one, n_error, "line") = PINT 29',
         '$string_bytes($throwable_field(S_one, n_error, "message")) = ($ptascii("Objects returned by '
         'ForeachCompareDeepRejectAggregate20::getIterator() must be traversable or implement interface '
         'Iterator"))',
         '$heap_owners($heap_graph(S_one), HOBJECT n_original) = 3',
         'S_one.EVENTS = S.EVENTS',
         '$call_descriptors_valid(S_one)',
         '$heap_valid($heap_graph(S_one))'],
    },
    'foreach-deeper-self-error-retires-both-raw-original-occurrences': {
        'source': SOURCES['foreach-source-compare-deeper-self-rejection'],
        'stage': 'S.TODO = (THROW_SEARCH n_error) :: (FOREACH_AGGREGATE pforeachaggregate "getIterator-error") :: ptask_tail*',
        'checks': ['n_original = pforeachaggregate.AGGREGATE',
         'pforeachaggregate.OBJECT = n_original',
         'pforeachaggregate.ITERATOR = eps',
         '$foreach_aggregate_site(S, pforeachaggregate.STATEMENT, pforeachaggregate.SITE, pforeachaggregate.LINE)',
         'S_global = $global_table_view(S)',
         '$lookup(S_global.ENV, $ptascii("keeper")) = (n_keeper)',
         'S.STORE[n_keeper] = DEFINED (POBJECT n_original)',
         'pforeachaggregate.INPUT = VARIABLE ($ptascii("slot")) z',
         '$lookup(S.ENV, $ptascii("slot")) = (n_input)',
         'n_input <- S.REFCELLS',
         'z = 29',
         'pforeachaggregate.LINE = z',
         'pforeachaggregate.ACQUIRED = [n_original]',
         'pforeachaggregate.CURRENT = KNOWN (POBJECT n_original)',
         '$foreach_aggregate_acquisition_valid(S, pforeachaggregate)',
         '$task_nodes(FOREACH_AGGREGATE pforeachaggregate "getIterator-error") = [HOBJECT n_original, HOBJECT '
         'n_original]',
         '$heap_owners($heap_graph(S), HOBJECT n_original) = 3',
         '$throwable_field(S, n_error, "line") = PINT 29',
         'S.EVENTS = [OUTPUT $ptascii("G0|"), OUTPUT $ptascii("G1|")]',
         '$call_descriptors_valid(S)',
         '$heap_valid($heap_graph(S))',
         'S_one_budget = $drive_steps(S, 1)',
         'S_one_budget.COMPLETION = BUDGET',
         'S_one = S_one_budget[.COMPLETION = NORMAL]',
         'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (THROW_SEARCH n_error) :: ptask_tail*',
         'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_original), DESTRUCTION_VALUE (HOBJECT '
         'n_original)]',
         'pdestructionrelease.CALLER = S.CURRENT',
         'pdestructionrelease.ORIGIN = (pforeachaggregate.SITE)',
         '$destructor_release_valid(S_one, pdestructionrelease)',
         '$heap_owners($heap_graph(S_one), HOBJECT n_original) = 3',
         'S_one.EVENTS = S.EVENTS',
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
            'foreach source comparison review inputs changed during run'
        if not passed:
            break
    raise SystemExit(0 if passed else 1)
