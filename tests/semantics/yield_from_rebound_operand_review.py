#!/usr/bin/env python3
"""Source-reached yield-from acquisition after a protected operand is rebound."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import fiber_state_review as review

CATALOG = Path(__file__).with_name('yield_from_rebound_operand_cases.json')
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
          'pyieldfromaggregate.ACQUIRED = eps',
          'pyieldfromaggregate.CURRENT = KNOWN PNULL',
          'S.OBJECTS[n_parent] = GENERATOR pgenerator_parent',
          'pgenerator_parent.PHASE = GENERATOR_RUNNING',
          'pgenerator_parent.DELEGATE = eps',
          '$yield_from_receipt_valid(S, $yield_from_aggregate_receipt(S, pyieldfromaggregate))']
KEEPER = ['S_global = $global_table_view(S)',
          '$lookup(S_global.ENV, $ptascii("keeper")) = (n_keeper)',
          'S.STORE[n_keeper] = DEFINED (POBJECT n_original)',
          '$heap_owners($heap_graph(S), HOBJECT n_original) = 1',
          '~(n_original <- S.DESTRUCTION.CALLED)']
CV = ['pyieldfromaggregate.INPUT = VARIABLE ($ptascii("slot")) z',
      '$lookup(S.ENV, $ptascii("slot")) = (n_input)',
      'n_input <- S.REFCELLS']
TERMINAL = ('S.TODO = (YIELD_FROM_AGGREGATE pyieldfromaggregate "getIterator") :: '
            'ptask_tail* -- if S.RESULT = KNOWN (POBJECT n_data)')
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
             'pyieldfromaggregate.OBJECT = n_original',
             'pyieldfromaggregate.ACQUIRED = eps',
             'pyieldfromaggregate.INPUT = VARIABLE ($ptascii("slot")) 25',
             'pyieldfromaggregate.LINE = 25',
             'pfibervm.CURRENT = (pcallcontext_get)',
             'pcallcontext_get.TARGET = AGGREGATE_METHOD_TARGET n_original porigin_get',
             'S_view = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)]'
             '[.FIBERCALLERS = eps][.COMPLETION = NORMAL]',
             'S_scope = $constant_frame_scope(S_view, pframe_getter, pframe_resumers*)',
             '$lookup(S_scope.ENV, $ptascii("slot")) = (n_input)',
             'S.STORE[n_input] = DEFINED (POBJECT n_payload)',
             'n_payload =/= n_original',
             '~$generator_from_aggregate(S, POBJECT n_payload)',
             '~$yield_from_aggregate_input_stable(S_scope, pyieldfromaggregate)']

CASES = {
    'rebound-cv-terminal-iterator-preserves-original-keeper-and-data-transfer': {
        'source': SOURCES['yield-from-rebound-cv-object-iterator'], 'stage': TERMINAL,
        'checks': [
            *HEADER, *KEEPER, *CV, 'z = 23',
            'pyieldfromaggregate.OBJECT = n_original',
            'S.STORE[n_input] = DEFINED (POBJECT n_payload)',
            'n_payload =/= n_original', '~$generator_from_aggregate(S, POBJECT n_payload)',
            '$useriter_instance(S, n_data)',
            '~$yield_from_aggregate_input_stable(S, pyieldfromaggregate)',
            '$yield_from_aggregate_no_self_check(S, S.RESULT)',
            '$task_nodes(YIELD_FROM_AGGREGATE pyieldfromaggregate "getIterator") = eps',
            'S.EVENTS = [OUTPUT $ptascii("G|")]', *ADMISSION, *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(YIELD_FROM_AGGREGATE pyieldfromaggregate_data "acquired") :: ptask_tail*',
            'pdestructionrelease.JOBS = eps',
            'pdestructionrelease.CALLER = S.CURRENT', 'pdestructionrelease.ORIGIN = S.ORIGIN',
            'pyieldfromaggregate_data = pyieldfromaggregate[.OBJECT = n_data]',
            '$task_nodes(YIELD_FROM_AGGREGATE pyieldfromaggregate_data "acquired") = [HOBJECT n_data]',
            '$heap_owners($heap_graph(S_one), HOBJECT n_data) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_original) = 1',
            'S_one.STORE[n_input] = S.STORE[n_input]', 'S_one.YIELDRETAINED = eps',
            '$destructor_release_valid(S_one, pdestructionrelease)', *POST,
        ],
    },
    'rebound-null-cv-acquires-fresh-generator-before-startup': {
        'source': SOURCES['yield-from-rebound-cv-null-generator'], 'stage': TERMINAL,
        'checks': [
            *HEADER, *KEEPER, *CV, 'z = 18',
            'S.STORE[n_input] = DEFINED PNULL',
            'S.OBJECTS[n_data] = GENERATOR pgenerator_data',
            'pgenerator_data.PHASE = GENERATOR_FRESH', 'pgenerator_data.VALUE = eps',
            '~$yield_from_aggregate_input_stable(S, pyieldfromaggregate)',
            '$yield_from_aggregate_no_self_check(S, S.RESULT)',
            'S.EVENTS = [OUTPUT $ptascii("G|")]', *ADMISSION, *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(YIELD_FROM_AGGREGATE pyieldfromaggregate_data "acquired") :: ptask_tail*',
            'pdestructionrelease.JOBS = eps',
            'pyieldfromaggregate_data = pyieldfromaggregate[.OBJECT = n_data]',
            'S_one.OBJECTS[n_data] = GENERATOR pgenerator_data',
            '$heap_owners($heap_graph(S_one), HOBJECT n_data) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_original) = 1',
            'S_one.STORE[n_input] = DEFINED PNULL', 'S_one.YIELDRETAINED = eps',
            '$destructor_release_valid(S_one, pdestructionrelease)', *POST,
        ],
    },
    'rebound-reference-input-retires-one-cell-owner-before-rewind': {
        'source': SOURCES['yield-from-rebound-reference-object-iterator'],
        'stage': 'S.TODO = (YIELD_FROM_AGGREGATE pyieldfromaggregate "acquired") :: ptask_tail*',
        'checks': [
            *HEADER, *KEEPER, 'pyieldfromaggregate.LINE = 28',
            'pyieldfromaggregate.INPUT = REFERENCE n_input', 'n_input <- S.REFCELLS',
            'S.STORE[n_input] = DEFINED (POBJECT n_payload)',
            'n_payload =/= n_original', '~$generator_from_aggregate(S, POBJECT n_payload)',
            '~$yield_from_aggregate_input_stable(S, pyieldfromaggregate)',
            'n_data = pyieldfromaggregate.OBJECT', '$useriter_instance(S, n_data)',
            '$task_nodes(YIELD_FROM_AGGREGATE pyieldfromaggregate "acquired") = '
            '[HOBJECT n_data, HCELL n_input]',
            '$heap_count(HCELL n_input, $task_nodes(YIELD_FROM_AGGREGATE pyieldfromaggregate "acquired")) = 1',
            '$heap_owners($heap_graph(S), HCELL n_input) = 3',
            '$heap_owners($heap_graph(S), HOBJECT n_payload) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_data) = 1',
            'S.EVENTS = [OUTPUT $ptascii("R|"), OUTPUT $ptascii("G|")]',
            *ADMISSION, *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(YIELD_FROM_AGGREGATE pyieldfromaggregate_ready "ready") :: ptask_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HCELL n_input)]',
            'pyieldfromaggregate_ready = pyieldfromaggregate[.INPUT = KNOWN PNULL]',
            '$task_nodes(YIELD_FROM_AGGREGATE pyieldfromaggregate_ready "ready") = [HOBJECT n_data]',
            'S_one.STORE[n_input] = S.STORE[n_input]',
            '$heap_owners($heap_graph(S_one), HOBJECT n_payload) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_original) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_data) = 1',
            'S_one.YIELDRETAINED = eps',
            '$destructor_release_valid(S_one, pdestructionrelease)', *POST,
        ],
    },
    'terminal-result-permission-does-not-admit-cleared-original-input': {
        'source': SOURCES['yield-from-rebound-cv-object-iterator'], 'stage': TERMINAL,
        'checks': [
            *HEADER, *CV, '$yield_from_aggregate_no_self_check(S, S.RESULT)',
            '$yield_from_aggregate_valid(S, pyieldfromaggregate, "getIterator")', *ADMISSION,
            'pyieldfromaggregate_bad = pyieldfromaggregate[.INPUT = KNOWN PNULL]',
            'S_bad = S[.TODO = (YIELD_FROM_AGGREGATE pyieldfromaggregate_bad "getIterator") :: ptask_tail*]',
            '$heap_graph(S_bad) = $heap_graph(S)',
            '$yield_from_aggregate_no_self_check(S_bad, S_bad.RESULT)',
            '~$yield_from_aggregate_input(S_bad, pyieldfromaggregate_bad, "getIterator")',
            '~$yield_from_aggregate_valid(S_bad, pyieldfromaggregate_bad, "getIterator")',
            '~$call_descriptors_valid(S_bad)',
        ],
    },
    'parked-rebound-getter-keeps-only-independent-original-receiver-owner': {
        'source': SOURCES['yield-from-rebound-getter-parks'], 'stage': PARK,
        'checks': [
            *PARK_VIEW, *KEEPER,
            '$target_nodes(pcallcontext_get.TARGET) = eps',
            '$call_context_roots(pfibervm.CURRENT) = eps',
            '$task_nodes(YIELD_FROM_AGGREGATE pyieldfromaggregate "getIterator") = eps',
            '$yield_from_aggregate_frame(S_view, pcallcontext_get, pframe_getter)',
            '$yield_from_aggregate_valid(S_scope, pyieldfromaggregate, "getIterator")',
            '$generator_saved_ids(pfibervm.FRAMES) = [n_parent]',
            '$generator_saved_fiber_ids(S) = [n_parent]',
            '$fiber_generator_transfer(S_view)',
            '$fiber_vm_valid(S, pfibervm, (n_fiber), eps)', *ADMISSION,
        ],
    },
    'parked-rebound-operand-zero-budget-keeps-real-saved-vm': {
        'source': SOURCES['yield-from-rebound-getter-parks'], 'stage': PARK,
        'checks': [
            *PARK_VIEW, '$yield_from_aggregate_frame(S_view, pcallcontext_get, pframe_getter)',
            '$fiber_vm_valid(S, pfibervm, (n_fiber), eps)', *ADMISSION, *ZERO,
        ],
    },
    'rebound-getter-throw-discards-acquisition-with-original-exception': {
        'source': SOURCES['yield-from-rebound-getter-throws'],
        'stage': ('S.TODO = (THROW_SEARCH n_error) :: '
                  '(YIELD_FROM_AGGREGATE pyieldfromaggregate "getIterator") :: ptask_tail*'),
        'checks': [
            *HEADER, *KEEPER, *CV, 'z = 13', 'S.STORE[n_input] = DEFINED PNULL',
            '$lookup(S_global.ENV, $ptascii("failure")) = (n_failure)',
            'S.STORE[n_failure] = DEFINED (POBJECT n_error)',
            '$string_bytes($throwable_field(S, n_error, "message")) = ($ptascii("rebound-getter"))',
            '~$yield_from_aggregate_input_stable(S, pyieldfromaggregate)',
            '$yield_from_aggregate_valid(S, pyieldfromaggregate, "getIterator")',
            'S.YIELDRETAINED = eps', *ADMISSION, *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(THROW_SEARCH n_error) :: ptask_tail*',
            'pdestructionrelease.JOBS = eps',
            'S_one.STORE[n_input] = DEFINED PNULL',
            'S_one.STORE[n_failure] = DEFINED (POBJECT n_error)',
            '$heap_owners($heap_graph(S_one), HOBJECT n_original) = 1',
            'S_one.YIELDRETAINED = eps',
            '$destructor_release_valid(S_one, pdestructionrelease)', *POST,
        ],
    },
    'rebound-source-raw-reference-rejection-keeps-cell-and-fixed-class-error': {
        'source': SOURCES['yield-from-rebound-getter-reference-rejected'],
        'stage': ('S.TODO = (YIELD_FROM_AGGREGATE pyieldfromaggregate "getIterator") :: '
                  'ptask_tail* -- if S.RESULT = REFERENCE n_return'),
        'checks': [
            *HEADER, *KEEPER, *CV, 'z = 22', 'S.STORE[n_input] = DEFINED (PBOOL false)',
            'S.STORE[n_return] = DEFINED (POBJECT n_data)', '$useriter_instance(S, n_data)',
            '~$yield_from_aggregate_input_stable(S, pyieldfromaggregate)',
            '$yield_from_aggregate_no_self_check(S, S.RESULT)',
            '$yield_from_aggregate_valid(S, pyieldfromaggregate, "getIterator")',
            *ADMISSION, *ONE,
            'S_one.TODO = (THROW_SEARCH n_error) :: '
            '(YIELD_FROM_AGGREGATE pyieldfromaggregate_error "getIterator-error") :: ptask_tail*',
            'pyieldfromaggregate_error = pyieldfromaggregate[.CURRENT = REFERENCE n_return]',
            '$task_nodes(YIELD_FROM_AGGREGATE pyieldfromaggregate_error "getIterator-error") = [HCELL n_return]',
            'S_one.OBJECTS[n_error] = THROWABLE pthrowable', 'pthrowable.KIND = "Exception"',
            '$throwable_field(S_one, n_error, "line") = PINT 22',
            '$throwable_field(S_one, n_error, "message") = PSTRING '
            '$ptascii("Objects returned by ReboundRawAggregate20::getIterator() must be traversable or implement interface Iterator")',
            'S_one.STORE[n_input] = DEFINED (PBOOL false)',
            '$heap_owners($heap_graph(S_one), HOBJECT n_original) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_data) = 1',
            'S_one.YIELDRETAINED = eps', *POST,
        ],
    },
    'yield-from-live-cv-source-equality-now-rejects-the-affected-original-control': {
        'source': SOURCES['yield-from-rebound-returned-aggregate-self-control'],
        'stage': 'S.TODO = (YIELD_FROM_AGGREGATE pyieldfromaggregate "getIterator") :: ptask_tail* -- if S.RESULT = KNOWN (POBJECT n_return)',
        'checks': ['n_original = pyieldfromaggregate.AGGREGATE',
         'n_parent = pyieldfromaggregate.PARENT',
         'pyieldfromaggregate.OBJECT = n_original',
         'pyieldfromaggregate.CURRENT = KNOWN PNULL',
         'S.OBJECTS[n_parent] = GENERATOR pgenerator_parent',
         'pgenerator_parent.PHASE = GENERATOR_RUNNING',
         'pgenerator_parent.DELEGATE = eps',
         '$yield_from_receipt_valid(S, $yield_from_aggregate_receipt(S, pyieldfromaggregate))',
         'S_global = $global_table_view(S)',
         '$lookup(S_global.ENV, $ptascii("keeper")) = (n_keeper)',
         'S.STORE[n_keeper] = DEFINED (POBJECT n_original)',
         'pyieldfromaggregate.INPUT = VARIABLE ($ptascii("slot")) z',
         '$lookup(S.ENV, $ptascii("slot")) = (n_input)',
         'n_input <- S.REFCELLS',
         'pyieldfromaggregate.ACQUIRED = eps',
         'z = 26',
         'pyieldfromaggregate.LINE = z',
         'S.STORE[n_input] = DEFINED (POBJECT n_return)',
         'n_return =/= n_original',
         '$generator_from_aggregate(S, POBJECT n_return)',
         '~$yield_from_aggregate_input_stable(S, pyieldfromaggregate)',
         '~$yield_from_aggregate_no_self_check(S, S.RESULT)',
         '$yield_from_aggregate_self_object(S, pyieldfromaggregate) = (n_return)',
         '$yield_from_aggregate_valid(S, pyieldfromaggregate, "getIterator")',
         'S.EVENTS = [OUTPUT $ptascii("G|")]',
         'S.YIELDRETAINED = eps',
         '$call_descriptors_valid(S)',
         '$heap_valid($heap_graph(S))',
         'S_one_budget = $drive_steps(S, 1)',
         'S_one_budget.COMPLETION = BUDGET',
         'S_one = S_one_budget[.COMPLETION = NORMAL]',
         'S_one.TODO = (THROW_SEARCH n_error) :: (YIELD_FROM_AGGREGATE pyieldfromaggregate_error '
         '"getIterator-error") :: ptask_tail*',
         'pyieldfromaggregate_error = pyieldfromaggregate[.CURRENT = KNOWN (POBJECT n_return)]',
         '$task_nodes(YIELD_FROM_AGGREGATE pyieldfromaggregate_error "getIterator-error") = [HOBJECT n_return]',
         'S_one.OBJECTS[n_error] = THROWABLE pthrowable',
         'pthrowable.KIND = "Exception"',
         '$throwable_field(S_one, n_error, "line") = PINT 26',
         '$string_bytes($throwable_field(S_one, n_error, "message")) = ($ptascii("Objects returned by '
         'ReboundControlAggregate20::getIterator() must be traversable or implement interface Iterator"))',
         'S_one.EVENTS = S.EVENTS',
         'S_one.YIELDRETAINED = eps',
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
            'yield-from rebound operand review inputs changed during run'
        if not passed:
            break
    raise SystemExit(0 if passed else 1)
