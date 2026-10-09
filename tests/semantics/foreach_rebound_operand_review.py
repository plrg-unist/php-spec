#!/usr/bin/env python3
"""Genuine foreach acquisition after a protected source operand is rebound."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import fiber_state_review as review

CATALOG = Path(__file__).with_name('foreach_rebound_operand_cases.json')
INPUT_BYTES = {path: path.read_bytes() for path in (Path(__file__), Path(review.__file__), CATALOG)}
SOURCES = {row['id']: row['source'] for row in json.loads(INPUT_BYTES[CATALOG])}
ADMISSION = ['$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
POST = ['$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))']
ONE = ['S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
       'S_one = S_one_budget[.COMPLETION = NORMAL]']
ZERO = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S']
HEADER = ['n_original = pforeachaggregate.AGGREGATE',
          'pforeachaggregate.ACQUIRED = eps',
          'pforeachaggregate.CURRENT = KNOWN PNULL',
          '$foreach_aggregate_site(S, pforeachaggregate.STATEMENT, '
          'pforeachaggregate.SITE, pforeachaggregate.LINE)']
KEEPER = ['S_global = $global_table_view(S)',
          '$lookup(S_global.ENV, $ptascii("keeper")) = (n_keeper)',
          'S.STORE[n_keeper] = DEFINED (POBJECT n_original)',
          '$heap_owners($heap_graph(S), HOBJECT n_original) = 1',
          '~(n_original <- S.DESTRUCTION.CALLED)']
CV = ['pforeachaggregate.INPUT = VARIABLE ($ptascii("slot")) z',
      '$lookup(S.ENV, $ptascii("slot")) = (n_input)',
      'n_input <- S.REFCELLS']
TERMINAL = ('S.TODO = (FOREACH_AGGREGATE pforeachaggregate "getIterator") :: '
            'ptask_tail* -- if S.RESULT = KNOWN (POBJECT n_data)')
PARK = ('S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_main* '
        '-- if pconfigcall.KIND = INTRINSIC_FIBER_RESUME '
        '-- if pconfigcall.OWNER = (n_fiber) '
        '-- if $fiber_at(S, n_fiber) = (pfiber) '
        '-- if pfiber.VM = (pfibervm) '
        '-- if pfibervm.FRAMES = pframe_getter :: pframe_resumers* '
        '-- if pframe_getter.TODO = '
        '(FOREACH_AGGREGATE pforeachaggregate "getIterator") :: ptask_parent*')
PARK_VIEW = ['n_original = pforeachaggregate.AGGREGATE',
             'pforeachaggregate.OBJECT = n_original',
             'pforeachaggregate.ACQUIRED = eps',
             'pforeachaggregate.INPUT = VARIABLE ($ptascii("slot")) 25',
             'pforeachaggregate.LINE = 25',
             'pforeachaggregate.CURRENT = KNOWN PNULL',
             'pforeachaggregate.ITERATOR = eps',
             'pfibervm.CURRENT = (pcallcontext_get)',
             'pcallcontext_get.TARGET = AGGREGATE_METHOD_TARGET n_original porigin_get',
             'S_view = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)]'
             '[.FIBERCALLERS = eps][.COMPLETION = NORMAL]',
             'S_scope = $constant_frame_scope(S_view, pframe_getter, pframe_resumers*)',
             '$lookup(S_scope.ENV, $ptascii("slot")) = (n_input)',
             'n_input <- S.REFCELLS',
             'S.STORE[n_input] = DEFINED (POBJECT n_payload)',
             'n_payload =/= n_original',
             '~$generator_from_aggregate(S, POBJECT n_payload)',
             '~$foreach_aggregate_input_stable(S_scope, pforeachaggregate)']

CASES = {
    'foreach-rebound-cv-terminal-iterator-protects-data-and-original-keeper': {
        'source': SOURCES['foreach-rebound-cv-object-iterator'], 'stage': TERMINAL,
        'checks': [
            *HEADER, *KEEPER, *CV, 'z = 23', 'pforeachaggregate.LINE = z',
            'pforeachaggregate.OBJECT = n_original', 'pforeachaggregate.ITERATOR = eps',
            'S.STORE[n_input] = DEFINED (POBJECT n_payload)',
            'n_payload =/= n_original', '~$generator_from_aggregate(S, POBJECT n_payload)',
            '$useriter_instance(S, n_data)',
            '~$foreach_aggregate_input_stable(S, pforeachaggregate)',
            '$foreach_aggregate_no_self_check(S, S.RESULT)',
            '$task_nodes(FOREACH_AGGREGATE pforeachaggregate "getIterator") = eps',
            'S.EVENTS = [OUTPUT $ptascii("G|")]', *ADMISSION, *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(FOREACH_AGGREGATE pforeachaggregate_data "acquired") :: ptask_tail*',
            'pdestructionrelease.JOBS = eps',
            'pdestructionrelease.CALLER = S.CURRENT', 'pdestructionrelease.ORIGIN = S.ORIGIN',
            'pforeachaggregate_data = pforeachaggregate[.OBJECT = n_data]',
            '$task_nodes(FOREACH_AGGREGATE pforeachaggregate_data "acquired") = [HOBJECT n_data]',
            '$heap_owners($heap_graph(S_one), HOBJECT n_data) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_original) = 1',
            'S_one.STORE[n_input] = S.STORE[n_input]',
            'S_one.ITERATORS = S.ITERATORS', 'S_one.NEXTITER = S.NEXTITER',
            '$destructor_release_valid(S_one, pdestructionrelease)', *POST,
        ],
    },
    'foreach-rebound-null-cv-acquires-generator-before-first-resume': {
        'source': SOURCES['foreach-rebound-cv-null-generator'], 'stage': TERMINAL,
        'checks': [
            *HEADER, *KEEPER, *CV, 'z = 22', 'pforeachaggregate.LINE = z',
            'pforeachaggregate.OBJECT = n_original', 'pforeachaggregate.ITERATOR = eps',
            'S.STORE[n_input] = DEFINED PNULL',
            'S.OBJECTS[n_data] = GENERATOR pgenerator_data',
            'pgenerator_data.PHASE = GENERATOR_FRESH', 'pgenerator_data.VALUE = eps',
            '~$foreach_aggregate_input_stable(S, pforeachaggregate)',
            '$foreach_aggregate_no_self_check(S, S.RESULT)',
            'S.EVENTS = [OUTPUT $ptascii("G|")]', *ADMISSION, *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(FOREACH_AGGREGATE pforeachaggregate_data "acquired") :: ptask_tail*',
            'pdestructionrelease.JOBS = eps',
            'pforeachaggregate_data = pforeachaggregate[.OBJECT = n_data]',
            'S_one.OBJECTS[n_data] = GENERATOR pgenerator_data',
            '$heap_owners($heap_graph(S_one), HOBJECT n_data) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_original) = 1',
            'S_one.STORE[n_input] = DEFINED PNULL',
            'S_one.ITERATORS = S.ITERATORS', 'S_one.NEXTITER = S.NEXTITER',
            '$destructor_release_valid(S_one, pdestructionrelease)', *POST,
        ],
    },
    'foreach-rebound-reference-input-survives-first-valid-then-retires-before-current': {
        'source': SOURCES['foreach-rebound-reference-object-iterator'],
        'stage': 'S.TODO = (FOREACH_AGGREGATE pforeachaggregate "ready") :: ptask_tail*',
        'checks': [
            *HEADER, *KEEPER, 'pforeachaggregate.LINE = 28',
            'pforeachaggregate.INPUT = REFERENCE n_input', 'n_input <- S.REFCELLS',
            'S.STORE[n_input] = DEFINED (POBJECT n_payload)',
            'n_payload =/= n_original', '~$generator_from_aggregate(S, POBJECT n_payload)',
            '~$foreach_aggregate_input_stable(S, pforeachaggregate)',
            'n_data = pforeachaggregate.OBJECT', '$useriter_instance(S, n_data)',
            'pforeachaggregate.ITERATOR = (n_cursor)',
            '$iterator_lookup(S.ITERATORS, n_cursor) = (OBJECTITER n_cursor n_data 0 false)',
            '$task_nodes(FOREACH_AGGREGATE pforeachaggregate "ready") = [HOBJECT n_data, HCELL n_input]',
            '$heap_count(HCELL n_input, $task_nodes(FOREACH_AGGREGATE pforeachaggregate "ready")) = 1',
            '$heap_owners($heap_graph(S), HCELL n_input) = 3',
            '$heap_owners($heap_graph(S), HOBJECT n_payload) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_data) = 1',
            'S.EVENTS = [OUTPUT $ptascii("R|"), OUTPUT $ptascii("G|"), '
            'OUTPUT $ptascii("W|"), OUTPUT $ptascii("V|")]',
            *ADMISSION, *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(FOREACH_AGGREGATE pforeachaggregate_current "current") :: ptask_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HCELL n_input)]',
            'pdestructionrelease.CALLER = S.CURRENT', 'pdestructionrelease.ORIGIN = S.ORIGIN',
            'pforeachaggregate_current = pforeachaggregate[.INPUT = KNOWN PNULL]',
            '$task_nodes(FOREACH_AGGREGATE pforeachaggregate_current "current") = [HOBJECT n_data]',
            'S_one.STORE[n_input] = S.STORE[n_input]',
            '$heap_owners($heap_graph(S_one), HOBJECT n_payload) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_original) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_data) = 1',
            'S_one.ITERATORS = S.ITERATORS',
            '$destructor_release_valid(S_one, pdestructionrelease)', *POST,
        ],
    },
    'foreach-terminal-result-permission-rejects-cleared-original-input': {
        'source': SOURCES['foreach-rebound-cv-object-iterator'], 'stage': TERMINAL,
        'checks': [
            *HEADER, *CV, '$foreach_aggregate_no_self_check(S, S.RESULT)',
            '$foreach_aggregate_valid(S, pforeachaggregate, "getIterator")', *ADMISSION,
            'pforeachaggregate_bad = pforeachaggregate[.INPUT = KNOWN PNULL]',
            'S_bad = S[.TODO = (FOREACH_AGGREGATE pforeachaggregate_bad "getIterator") :: ptask_tail*]',
            '$heap_graph(S_bad) = $heap_graph(S)',
            '$foreach_aggregate_no_self_check(S_bad, S_bad.RESULT)',
            '~$foreach_aggregate_input(S_bad, pforeachaggregate_bad, "getIterator")',
            '~$foreach_aggregate_valid(S_bad, pforeachaggregate_bad, "getIterator")',
            '~$call_descriptors_valid(S_bad)',
        ],
    },
    'foreach-parked-rebound-getter-borrows-receiver-and-preserves-keeper': {
        'source': SOURCES['foreach-rebound-getter-parks'], 'stage': PARK,
        'checks': [
            *PARK_VIEW, *KEEPER,
            '$target_nodes(pcallcontext_get.TARGET) = eps',
            '$call_context_roots(pfibervm.CURRENT) = eps',
            '$task_nodes(FOREACH_AGGREGATE pforeachaggregate "getIterator") = eps',
            '$foreach_aggregate_frame(S_view, pcallcontext_get, pframe_getter)',
            '$foreach_aggregate_valid(S_scope, pforeachaggregate, "getIterator")',
            '$generator_saved_ids(pfibervm.FRAMES) = eps',
            '$fiber_generator_transfer(S_view)',
            '$fiber_vm_valid(S, pfibervm, (n_fiber), eps)', *ADMISSION,
        ],
    },
    'foreach-parked-rebound-zero-budget-keeps-real-saved-vm': {
        'source': SOURCES['foreach-rebound-getter-parks'], 'stage': PARK,
        'checks': [
            *PARK_VIEW, '$foreach_aggregate_frame(S_view, pcallcontext_get, pframe_getter)',
            '$fiber_vm_valid(S, pfibervm, (n_fiber), eps)', *ADMISSION, *ZERO,
        ],
    },
    'foreach-rebound-getter-throw-discards-acquisition-with-same-exception': {
        'source': SOURCES['foreach-rebound-getter-throws'],
        'stage': ('S.TODO = (THROW_SEARCH n_error) :: '
                  '(FOREACH_AGGREGATE pforeachaggregate "getIterator") :: ptask_tail*'),
        'checks': [
            *HEADER, *KEEPER, *CV, 'z = 14', 'pforeachaggregate.ITERATOR = eps',
            'S.STORE[n_input] = DEFINED PNULL',
            '$lookup(S_global.ENV, $ptascii("failure")) = (n_failure)',
            'S.STORE[n_failure] = DEFINED (POBJECT n_error)',
            '$string_bytes($throwable_field(S, n_error, "message")) = ($ptascii("foreach-rebound-getter"))',
            '~$foreach_aggregate_input_stable(S, pforeachaggregate)',
            '$foreach_aggregate_valid(S, pforeachaggregate, "getIterator")',
            *ADMISSION, *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(THROW_SEARCH n_error) :: ptask_tail*',
            'pdestructionrelease.JOBS = eps',
            'S_one.STORE[n_input] = DEFINED PNULL',
            'S_one.STORE[n_failure] = DEFINED (POBJECT n_error)',
            '$heap_owners($heap_graph(S_one), HOBJECT n_original) = 1',
            '$destructor_release_valid(S_one, pdestructionrelease)', *POST,
        ],
    },
    'foreach-rebound-raw-reference-rejection-keeps-cell-and-fixed-class-error': {
        'source': SOURCES['foreach-rebound-getter-reference-rejected'],
        'stage': ('S.TODO = (FOREACH_AGGREGATE pforeachaggregate "getIterator") :: '
                  'ptask_tail* -- if S.RESULT = REFERENCE n_return'),
        'checks': [
            *HEADER, *KEEPER, *CV, 'z = 22', 'pforeachaggregate.ITERATOR = eps',
            'S.STORE[n_input] = DEFINED (PBOOL false)',
            'S.STORE[n_return] = DEFINED (POBJECT n_data)', '$useriter_instance(S, n_data)',
            '~$foreach_aggregate_input_stable(S, pforeachaggregate)',
            '$foreach_aggregate_no_self_check(S, S.RESULT)',
            '$foreach_aggregate_valid(S, pforeachaggregate, "getIterator")',
            *ADMISSION, *ONE,
            'S_one.TODO = (THROW_SEARCH n_error) :: '
            '(FOREACH_AGGREGATE pforeachaggregate_error "getIterator-error") :: ptask_tail*',
            'pforeachaggregate_error = pforeachaggregate[.CURRENT = REFERENCE n_return]',
            '$task_nodes(FOREACH_AGGREGATE pforeachaggregate_error "getIterator-error") = [HCELL n_return]',
            'S_one.OBJECTS[n_error] = THROWABLE pthrowable', 'pthrowable.KIND = "Exception"',
            '$throwable_field(S_one, n_error, "line") = PINT 22',
            '$string_bytes($throwable_field(S_one, n_error, "message")) = '
            '($ptascii("Objects returned by ForeachReboundRawAggregate20::getIterator() must be traversable or implement interface Iterator"))',
            'S_one.STORE[n_input] = DEFINED (PBOOL false)',
            '$heap_owners($heap_graph(S_one), HOBJECT n_original) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_data) = 1', *POST,
        ],
    },
    'foreach-live-cv-source-equality-now-rejects-the-affected-original-control': {
        'source': SOURCES['foreach-rebound-returned-aggregate-self-control'],
        'stage': 'S.TODO = (FOREACH_AGGREGATE pforeachaggregate "getIterator") :: ptask_tail* -- if S.RESULT = KNOWN (POBJECT n_return)',
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
         'pforeachaggregate.ACQUIRED = eps',
         'z = 26',
         'pforeachaggregate.LINE = z',
         'S.STORE[n_input] = DEFINED (POBJECT n_return)',
         'n_return =/= n_original',
         '$generator_from_aggregate(S, POBJECT n_return)',
         '~$foreach_aggregate_input_stable(S, pforeachaggregate)',
         '~$foreach_aggregate_no_self_check(S, S.RESULT)',
         '$foreach_aggregate_self_object(S, pforeachaggregate) = (n_return)',
         '$foreach_aggregate_valid(S, pforeachaggregate, "getIterator")',
         'S.EVENTS = [OUTPUT $ptascii("G|")]',
         '$call_descriptors_valid(S)',
         '$heap_valid($heap_graph(S))',
         'S_one_budget = $drive_steps(S, 1)',
         'S_one_budget.COMPLETION = BUDGET',
         'S_one = S_one_budget[.COMPLETION = NORMAL]',
         'S_one.TODO = (THROW_SEARCH n_error) :: (FOREACH_AGGREGATE pforeachaggregate_error "getIterator-error") '
         ':: ptask_tail*',
         'pforeachaggregate_error = pforeachaggregate[.CURRENT = KNOWN (POBJECT n_return)]',
         '$task_nodes(FOREACH_AGGREGATE pforeachaggregate_error "getIterator-error") = [HOBJECT n_return]',
         'S_one.OBJECTS[n_error] = THROWABLE pthrowable',
         'pthrowable.KIND = "Exception"',
         '$throwable_field(S_one, n_error, "line") = PINT 26',
         '$string_bytes($throwable_field(S_one, n_error, "message")) = ($ptascii("Objects returned by '
         'ForeachReboundControlAggregate20::getIterator() must be traversable or implement interface Iterator"))',
         'S_one.EVENTS = S.EVENTS',
         '$call_descriptors_valid(S_one)',
         '$heap_valid($heap_graph(S_one))'],
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
            'foreach rebound operand review inputs changed during run'
        if not passed:
            break
    raise SystemExit(0 if passed else 1)
