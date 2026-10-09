#!/usr/bin/env python3
"""Source-reached Aggregate acquisition, owners and callback authority checks."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import fiber_state_review as review

CATALOG = Path(__file__).with_name('fiber_start_aggregate_cases.json')
SOURCE_BYTES = CATALOG.read_bytes()
SOURCES = {row['id']: row['source'] for row in json.loads(SOURCE_BYTES)}
ADMISSION = ['$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
ZERO = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S']
ONE = ['S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
       'S_one = S_one_budget[.COMPLETION = NORMAL]']
HEADER = ['pfiberstart = pfibertraversal.START',
          'pfibertraversal.AGGREGATE = (n_aggregate)',
          'S.OBJECTS[pfiberstart.OBJECT] = FIBER pfiber_target',
          'pfiber_target.STATUS = FIBER_INIT']
PARK = ('S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_main* '
        '-- if pconfigcall.KIND = INTRINSIC_FIBER_RESUME '
        '-- if pconfigcall.OWNER = (n_parent) '
        '-- if $fiber_at(S, n_parent) = (pfiber_parent) '
        '-- if pfiber_parent.VM = (pfibervm) '
        '-- if pfibervm.FRAMES = [pframe_unpack, pframe_base] '
        '-- if pframe_unpack.TODO = '
        '(FIBER_TRAVERSE_RESULT pfibertraversal "getIterator") :: ptask_unpack*')
PARK_VIEW = ['S_view = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_parent)]'
             '[.FIBERCALLERS = eps][.COMPLETION = NORMAL]',
             'pfibervm.CURRENT = (pcallcontext_get)',
             'S_scope = $constant_frame_scope(S_view, pframe_unpack, [pframe_base])',
             '$fiber_traversal_frame(S_view, pcallcontext_get, pframe_unpack, [pframe_base])']
GENERATOR_RESULT = ('S.TODO = (FIBER_TRAVERSE_RESULT pfibertraversal "getIterator") :: '
                    'ptask_tail* -- if S.RESULT = KNOWN (POBJECT n_generator) '
                    '-- if S.OBJECTS[n_generator] = GENERATOR pgenerator '
                    '-- if pgenerator.PHASE = GENERATOR_FRESH '
                    '-- if pgenerator.FRAME = (pframe_generator) '
                    '-- if pframe_generator.CONTEXT = (pcallcontext_owned)')


def generator_receipt_forgery(target, shifted_line=False):
    return {
        'source': SOURCES['author-fiber-start-iterator-aggregate-acquisition'],
        'stage': GENERATOR_RESULT,
        'checks': [
            'pcallcontext_owned.TARGET = AGGREGATE_GENERATOR_TARGET '
            'n_aggregate porigin_get n_index porigin_arg z',
            'pcallcontext_owned.CALLSITE = (porigin_call)',
            'S_scope = $generator_frame_scope(S, pframe_generator)',
            '$fiber_traversal_generator_context(S_scope, pcallcontext_owned)',
            '$generator_frame_valid(S, pgenerator, pframe_generator)', *ADMISSION,
            'pcallcontext_bad = pcallcontext_owned[.TARGET = ' + target + ']' +
            ('[.LINE = $(z + 1)]' if shifted_line else ''),
            'pframe_bad = pframe_generator[.CONTEXT = (pcallcontext_bad)]',
            'pgenerator_bad = pgenerator[.FRAME = (pframe_bad)]',
            'S_bad = S[.OBJECTS[n_generator] = GENERATOR pgenerator_bad]',
            '$heap_graph(S_bad) = $heap_graph(S)',
            'S_scope_bad = $generator_frame_scope(S_bad, pframe_bad)',
            '~$fiber_traversal_generator_context(S_scope_bad, pcallcontext_bad)',
            '~$generator_frame_valid(S_bad, pgenerator_bad, pframe_bad)',
            '~$call_descriptors_valid(S_bad)',
        ],
    }


CASES = {
    'aggregate-pending-get-iterator-has-input-without-data-owner': {
        'source': SOURCES['aggregate-fresh-iterator-owner-order'],
        'stage': ('S.TODO = (CALL_ARGS pcalltarget eps 0 eps (porigin) z) :: '
                  '(FIBER_TRAVERSE_RESULT pfibertraversal "getIterator") :: ptask_tail*'),
        'checks': [
            *HEADER, 'porigin = pfiberstart.SITE', 'z = 23',
            'pfibertraversal.LINE = z', 'pfibertraversal.OBJECT = n_aggregate',
            'pfibertraversal.INPUT = KNOWN (POBJECT n_aggregate)',
            'pfibertraversal.CURRENT = KNOWN PNULL', 'pfibertraversal.ITEMS = eps',
            'pcalltarget = AGGREGATE_METHOD_TARGET n_aggregate porigin_get',
            '$target_nodes(pcalltarget) = eps',
            '$fiber_traversal_method_selected(S, n_aggregate, porigin_get, "getIterator")',
            '$fiber_traversal_pending(S, pcalltarget, porigin)',
            '$heap_count(HOBJECT n_aggregate, $task_nodes('
            'FIBER_TRAVERSE_RESULT pfibertraversal "getIterator")) = 1',
            '$fiber_traversal_nodes(pfibertraversal, false) = [HOBJECT n_aggregate]',
            *ADMISSION, *ZERO, *ONE,
            'S_one.CURRENT = (pcallcontext_get)',
            'pcallcontext_get.LINE = 23', 'pcallcontext_get.CALLSITE = (porigin)',
            'pcallcontext_get.TARGET = pcalltarget',
            '$heap_count(HOBJECT n_aggregate, $call_context_roots(S_one.CURRENT)) = 0',
            '$heap_count(HOBJECT n_aggregate, $destructor_context_nodes(S_one.CURRENT)) = 0',
            'S_one.FRAMES = pframe_unpack :: pframe_tail*',
            '$fiber_traversal_frame(S_one, pcallcontext_get, pframe_unpack, pframe_tail*)',
        ],
    },
    'aggregate-acquired-iterator-keeps-original-input-and-distinct-data': {
        'source': SOURCES['aggregate-fresh-iterator-owner-order'],
        'stage': ('S.TODO = (FIBER_TRAVERSE_RESULT pfibertraversal "getIterator") :: '
                  'ptask_tail* -- if S.RESULT = KNOWN (POBJECT n_inner)'),
        'checks': [
            *HEADER, 'pfibertraversal.OBJECT = n_aggregate',
            'pfibertraversal.INPUT = KNOWN (POBJECT n_aggregate)',
            'n_inner =/= n_aggregate', '$useriter_instance(S, n_inner)',
            '$fiber_traversal_result_valid(S, pfibertraversal, "getIterator")',
            '$heap_count(HOBJECT n_inner, $task_nodes('
            'FIBER_TRAVERSE_RESULT pfibertraversal "getIterator")) = 0',
            *ADMISSION, *ONE,
            'S_one.TODO = (CALL_ARGS (METHOD_TARGET n_inner porigin_rewind) '
            'eps 0 eps (pfiberstart.SITE) 23) :: '
            '(FIBER_TRAVERSE_RESULT pfibertraversal_inner "rewind") :: ptask_tail*',
            'pfibertraversal_inner = pfibertraversal[.OBJECT = n_inner]',
            '$fiber_traversal_pending(S_one, METHOD_TARGET n_inner porigin_rewind, pfiberstart.SITE)',
            '$heap_count(HOBJECT n_inner, $task_nodes('
            'FIBER_TRAVERSE_RESULT pfibertraversal_inner "rewind")) = 1',
            '$heap_count(HOBJECT n_aggregate, $task_nodes('
            'FIBER_TRAVERSE_RESULT pfibertraversal_inner "rewind")) = 1',
            'S_one.RESULT = KNOWN PNULL', '$call_descriptors_valid(S_one)',
        ],
    },
    'aggregate-get-iterator-rejects-owning-method-target': {
        'source': SOURCES['aggregate-fresh-iterator-owner-order'],
        'stage': ('S.TODO = (CALL_ARGS pcalltarget eps 0 eps (porigin) z) :: '
                  '(FIBER_TRAVERSE_RESULT pfibertraversal "getIterator") :: ptask_tail*'),
        'checks': [
            *HEADER, 'pcalltarget = AGGREGATE_METHOD_TARGET n_aggregate porigin_get',
            '$fiber_traversal_pending(S, pcalltarget, porigin)', *ADMISSION,
            'pcalltarget_owned = METHOD_TARGET n_aggregate porigin_get',
            'S_owned = S[.TODO = (CALL_ARGS pcalltarget_owned eps 0 eps (porigin) z) :: '
            '(FIBER_TRAVERSE_RESULT pfibertraversal "getIterator") :: ptask_tail*]',
            '$heap_valid($heap_graph(S_owned))',
            '$heap_owners($heap_graph(S_owned), HOBJECT n_aggregate) = '
            '$($heap_owners($heap_graph(S), HOBJECT n_aggregate) + 1)',
            '~$fiber_traversal_pending(S_owned, pcalltarget_owned, porigin)',
            '~$call_task_valid(S_owned, CALL_ARGS pcalltarget_owned eps 0 eps (porigin) z)',
            '~$call_descriptors_valid(S_owned)',
        ],
    },
    'aggregate-success-retires-inner-data-before-temporary-input': {
        'source': SOURCES['aggregate-fresh-iterator-owner-order'],
        'stage': ('S.TODO = (FIBER_TRAVERSE_RESULT pfibertraversal "valid") :: '
                  'ptask_tail* -- if S.RESULT = KNOWN (PBOOL false)'),
        'checks': [
            *HEADER, 'n_inner = pfibertraversal.OBJECT', 'n_inner =/= n_aggregate',
            'pfibertraversal.INPUT = KNOWN (POBJECT n_aggregate)',
            'pfibertraversal.CURRENT = KNOWN PNULL',
            'pfibertraversal.ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 7))]',
            '$destructor_operational(S)',
            '$fiber_traversal_result_valid(S, pfibertraversal, "valid")',
            *ADMISSION, *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(FIBER_ARGS pfiberstart_next) :: ptask_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_inner), '
            'DESTRUCTION_VALUE (HOBJECT n_aggregate)]',
            'pdestructionrelease.ORIGIN = (pfiberstart.SITE)',
            'S_one.DESTRUCTION.RELEASES = [pdestructionrelease]',
            'pfiberstart_next.PACKS = [FIBER_TRAVERSABLE_PACK ptraversablepack]',
            'ptraversablepack.OBJECT = n_inner',
            'ptraversablepack.ITEMS = pfibertraversal.ITEMS',
            '$heap_count(HOBJECT n_inner, $task_nodes(FIBER_ARGS pfiberstart_next)) = 0',
            '$heap_count(HOBJECT n_aggregate, $task_nodes(FIBER_ARGS pfiberstart_next)) = 0',
            '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
        ],
    },
    'aggregate-generator-data-owner-is-native-operation-only': {
        'source': SOURCES['aggregate-generator-acquisition'],
        'stage': ('S.TODO = (GENERATOR_YIELD_STORE porigin_yield poperand_key?) :: '
                  'ptask_body* -- if S.RESULT = KNOWN (PINT 7) '
                  '-- if S.FRAMES = [pframe] -- if pframe.TODO = '
                  '(GENERATOR_RESUME pgeneratorop) :: '
                  '(FIBER_TRAVERSE_GENERATOR pfibertraversal "rewind") :: ptask_saved*'),
        'checks': [
            *HEADER, 'n_generator = pfibertraversal.OBJECT',
            'n_generator =/= n_aggregate', 'pfibertraversal.LINE = 22',
            'pfibertraversal.INPUT = KNOWN (POBJECT n_aggregate)',
            'pfibertraversal.CURRENT = KNOWN PNULL',
            'pgeneratorop.OBJECT = n_generator', 'pgeneratorop.STARTPACK',
            'pgeneratorop.NAME = "rewind"', 'pgeneratorop.SITE = pfiberstart.SITE',
            'pgeneratorop.LINE = 22', 'pgeneratorop.LOOP = eps',
            'S.OBJECTS[n_generator] = GENERATOR pgenerator',
            'pgenerator.PHASE = GENERATOR_RUNNING',
            '$fiber_traversal_generator_valid(S, pgeneratorop)',
            '$heap_count(HOBJECT n_generator, $task_nodes(GENERATOR_RESUME pgeneratorop)) = 1',
            '$heap_count(HOBJECT n_generator, $task_nodes('
            'FIBER_TRAVERSE_GENERATOR pfibertraversal "rewind")) = 0',
            '$heap_count(HOBJECT n_aggregate, $task_nodes('
            'FIBER_TRAVERSE_GENERATOR pfibertraversal "rewind")) = 1',
            *ADMISSION,
        ],
    },
    'aggregate-generator-method-promotes-only-copied-receiver-owner': {
        'source': SOURCES['author-fiber-start-iterator-aggregate-acquisition'],
        'stage': ('S.TODO = (GENERATOR_CREATE porigin_get) :: ptask_body* '
                  '-- if S.CURRENT = (pcallcontext_borrowed) '
                  '-- if S.FRAMES = [pframe_unpack] -- if pframe_unpack.TODO = '
                  '(FIBER_TRAVERSE_RESULT pfibertraversal "getIterator") :: ptask_unpack*'),
        'checks': [
            *HEADER, 'pfibertraversal.OBJECT = n_aggregate',
            'pcallcontext_borrowed.TARGET = AGGREGATE_METHOD_TARGET n_aggregate porigin_get',
            '$heap_count(HOBJECT n_aggregate, $call_context_roots(S.CURRENT)) = 0',
            '$generator_creation_supported(S, pcallcontext_borrowed)',
            '$generator_create_valid(S, porigin_get)', *ADMISSION, *ONE,
            'S_one.TODO = (FIBER_TRAVERSE_RESULT pfibertraversal "getIterator") :: ptask_unpack*',
            'S_one.RESULT = KNOWN (POBJECT n_generator)',
            'S_one.OBJECTS[n_generator] = GENERATOR pgenerator',
            'pgenerator.PHASE = GENERATOR_FRESH', 'pgenerator.FRAME = (pframe_generator)',
            'pframe_generator.CONTEXT = (pcallcontext_owned)',
            'pcallcontext_owned.TARGET = AGGREGATE_GENERATOR_TARGET n_aggregate porigin_get '
            'pfiberstart.INDEX pfibertraversal.SITE pfibertraversal.LINE',
            'pcallcontext_owned[.TARGET = pcallcontext_borrowed.TARGET] = pcallcontext_borrowed',
            'pcallcontext_owned.TARGET =/= pcallcontext_borrowed.TARGET',
            '$heap_count(HOBJECT n_aggregate, $call_context_roots(pframe_generator.CONTEXT)) = 1',
            '$heap_count(HOBJECT n_aggregate, $destructor_context_nodes(pframe_generator.CONTEXT)) = 1',
            '$heap_count(HOBJECT n_aggregate, $node_children(S_one, HOBJECT n_generator)) = 1',
            '$generator_frame_valid(S_one, pgenerator, pframe_generator)',
            '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
        ],
    },
    'aggregate-generator-rejects-shifted-receipt-and-context-line': generator_receipt_forgery(
        'AGGREGATE_GENERATOR_TARGET n_aggregate porigin_get n_index porigin_arg $(z + 1)',
        shifted_line=True),
    'aggregate-generator-rejects-wrong-original-unpack-index': generator_receipt_forgery(
        'AGGREGATE_GENERATOR_TARGET n_aggregate porigin_get $(n_index + 1) porigin_arg z'),
    'aggregate-parked-get-iterator-keeps-real-frame-without-data-root': {
        'source': SOURCES['aggregate-get-iterator-parks'], 'stage': PARK,
        'checks': [
            *HEADER, 'S.ACTIVEFIBER = eps', 'S.FIBERCALLERS = eps',
            'pfiber_parent.STATUS = FIBER_SUSPENDED',
            'pfibertraversal.OBJECT = n_aggregate', 'pfibertraversal.LINE = 31',
            'pfibertraversal.INPUT = VARIABLE ($ptascii("aggregate")) z_input',
            '$operand_nodes(pfibertraversal.INPUT) = eps',
            'pfibertraversal.CURRENT = KNOWN PNULL', 'pfibertraversal.ITEMS = eps',
            'psymboltable_global = $fiber_globals(S)',
            '$lookup(psymboltable_global.ENV, $ptascii("aggregate")) = (n_operand_cell)',
            'S.STORE[n_operand_cell] = DEFINED PNULL',
            '$lookup(psymboltable_global.ENV, $ptascii("keep")) = (n_keeper_cell)',
            'S.STORE[n_keeper_cell] = DEFINED (POBJECT n_aggregate)',
            '$heap_count(HOBJECT n_aggregate, $task_nodes('
            'FIBER_TRAVERSE_RESULT pfibertraversal "getIterator")) = 0',
            '(HOBJECT n_aggregate) <- S.ALLOCATIONS',
            *PARK_VIEW, 'pcallcontext_get.LINE = 31',
            'pcallcontext_get.CALLSITE = (pfiberstart.SITE)',
            'pcallcontext_get.TARGET = AGGREGATE_METHOD_TARGET n_aggregate porigin_get',
            '$heap_count(HOBJECT n_aggregate, $call_context_roots(pfibervm.CURRENT)) = 0',
            '$heap_count(HOBJECT n_aggregate, $destructor_context_nodes(pfibervm.CURRENT)) = 0',
            '$heap_owners($heap_graph(S), HOBJECT n_aggregate) = 1',
            '$fiber_traversal_result_valid(S_scope, pfibertraversal, "getIterator")',
            *ADMISSION, *ZERO,
        ],
    },
    'aggregate-parked-get-iterator-rejects-shifted-unpack-line': {
        'source': SOURCES['aggregate-get-iterator-parks'], 'stage': PARK,
        'checks': [
            *PARK_VIEW, *ADMISSION,
            'pfibertraversal_bad = pfibertraversal[.LINE = $(pfibertraversal.LINE + 1)]',
            'pframe_bad = pframe_unpack[.TODO = '
            '(FIBER_TRAVERSE_RESULT pfibertraversal_bad "getIterator") :: ptask_unpack*]',
            'pfibervm_bad = pfibervm[.FRAMES = [pframe_bad, pframe_base]]',
            'S_bad = S[.OBJECTS[n_parent] = FIBER pfiber_parent[.VM = (pfibervm_bad)]]',
            '$heap_graph(S_bad) = $heap_graph(S)',
            'S_scope_bad = S_scope[.TODO = pframe_bad.TODO]',
            '~$fiber_traversal_result_valid(S_scope_bad, pfibertraversal_bad, "getIterator")',
            '~$call_task_valid(S_scope_bad, FIBER_TRAVERSE_RESULT pfibertraversal_bad "getIterator")',
            '~$fiber_vm_valid(S_bad, pfibervm_bad, (n_parent), eps)',
            '~$call_descriptors_valid(S_bad)',
        ],
    },
    'aggregate-parked-get-iterator-rejects-duplicate-start': {
        'source': SOURCES['aggregate-get-iterator-parks'], 'stage': PARK,
        'checks': [
            *PARK_VIEW, *ADMISSION,
            'pframe_duplicate = pframe_unpack[.TODO = '
            '(FIBER_TRAVERSE_RESULT pfibertraversal "getIterator") :: '
            '(FIBER_TRAVERSE_RESULT pfibertraversal "getIterator") :: ptask_unpack*]',
            'pfibervm_duplicate = pfibervm[.FRAMES = [pframe_duplicate, pframe_base]]',
            'S_duplicate = S[.OBJECTS[n_parent] = FIBER pfiber_parent[.VM = (pfibervm_duplicate)]]',
            '$fiber_start_unpack_count(pframe_duplicate.TODO, pfibertraversal.CAPTURE, '
            'pfibertraversal.START.SITE) = 2',
            'S_scope_duplicate = S_scope[.TODO = pframe_duplicate.TODO]',
            '~$fiber_traversal_result_valid(S_scope_duplicate, pfibertraversal, "getIterator")',
            '$heap_valid($heap_graph(S_duplicate))',
            '$heap_owners($heap_graph(S_duplicate), HOBJECT pfibertraversal.START.OBJECT) = '
            '$($heap_owners($heap_graph(S), HOBJECT pfibertraversal.START.OBJECT) + 1)',
            '~$fiber_vm_valid(S_duplicate, pfibervm_duplicate, (n_parent), eps)',
            '~$call_descriptors_valid(S_duplicate)',
        ],
    },
    'aggregate-raw-reference-result-is-rejected-and-retained-for-unwind': {
        'source': SOURCES['safe-aggregate-reference-iterator-acquisition'],
        'stage': ('S.TODO = (FIBER_TRAVERSE_RESULT pfibertraversal "getIterator") :: '
                  'ptask_tail* -- if S.RESULT = REFERENCE n_return'),
        'checks': [
            *HEADER, 'pfibertraversal.OBJECT = n_aggregate',
            'S.STORE[n_return] = DEFINED (POBJECT n_inner)', '$useriter_instance(S, n_inner)',
            'pfibertraversal.CURRENT = KNOWN PNULL',
            '$fiber_traversal_result_valid(S, pfibertraversal, "getIterator")',
            '$heap_count(HOBJECT n_inner, $task_nodes('
            'FIBER_TRAVERSE_RESULT pfibertraversal "getIterator")) = 0',
            *ADMISSION, *ONE,
            'S_one.TODO = (THROW_SEARCH n_error) :: '
            '(FIBER_TRAVERSE_RESULT pfibertraversal_error "getIterator-error") :: ptask_tail*',
            'pfibertraversal_error = pfibertraversal[.CURRENT = REFERENCE n_return]',
            '$heap_count(HCELL n_return, $task_nodes('
            'FIBER_TRAVERSE_RESULT pfibertraversal_error "getIterator-error")) = 1',
            '$heap_count(HOBJECT n_aggregate, $task_nodes('
            'FIBER_TRAVERSE_RESULT pfibertraversal_error "getIterator-error")) = 0',
            '$fiber_traversal_result_valid(S_one, pfibertraversal_error, "getIterator-error")',
            '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
        ],
    },
    'aggregate-retired-original-identity-adds-no-owner-after-acquisition': {
        'source': SOURCES['aggregate-borrowed-cv-retired-keeper'],
        'stage': ('S.TODO = (CALL_ARGS pcalltarget eps 0 eps (porigin) z) :: '
                  '(FIBER_TRAVERSE_RESULT pfibertraversal "valid") :: ptask_tail*'),
        'checks': [
            *HEADER, 'n_inner = pfibertraversal.OBJECT', 'n_inner =/= n_aggregate',
            'pfibertraversal.INPUT = VARIABLE ($ptascii("aggregate")) z_input',
            '~((HOBJECT n_aggregate) <- S.ALLOCATIONS)',
            '$heap_owners($heap_graph(S), HOBJECT n_aggregate) = 0',
            '$fiber_traversal_identity(S, pfibertraversal)',
            '$heap_count(HOBJECT n_aggregate, $task_nodes('
            'FIBER_TRAVERSE_RESULT pfibertraversal "valid")) = 0',
            '$heap_count(HOBJECT n_inner, $task_nodes('
            'FIBER_TRAVERSE_RESULT pfibertraversal "valid")) = 1',
            '$fiber_traversal_pending(S, pcalltarget, porigin)', *ADMISSION,
            'pfibertraversal_bad = pfibertraversal[.AGGREGATE = (n_inner)]',
            'S_bad = S[.TODO = (CALL_ARGS pcalltarget eps 0 eps (porigin) z) :: '
            '(FIBER_TRAVERSE_RESULT pfibertraversal_bad "valid") :: ptask_tail*]',
            '$heap_graph(S_bad) = $heap_graph(S)',
            '~$fiber_traversal_identity(S_bad, pfibertraversal_bad)',
            '~$call_descriptors_valid(S_bad)',
        ],
    },
    'aggregate-get-iterator-throw-releases-only-input-before-direct-capture': {
        'source': SOURCES['aggregate-get-iterator-throws-direct-fcc'],
        'stage': ('S.TODO = (THROW_SEARCH n_error) :: '
                  '(FIBER_TRAVERSE_RESULT pfibertraversal "getIterator") :: '
                  'ptask_tail* -- if S.CURRENT = eps'),
        'checks': [
            *HEADER, 'pfibertraversal.OBJECT = n_aggregate',
            'pfibertraversal.CAPTURE = (n_capture)',
            '~$exit_method_site(S, pfiberstart.SITE)',
            'pfibertraversal.INPUT = KNOWN (POBJECT n_aggregate)',
            'pfibertraversal.CURRENT = KNOWN PNULL', 'pfibertraversal.ITEMS = eps',
            'pfibertraversal.SENT = {SLOTS eps, NAMED eps}',
            '$lookup(S.ENV, $ptascii("original")) = (n_original)',
            'S.STORE[n_original] = DEFINED (POBJECT n_error)',
            '$heap_count(HOBJECT n_aggregate, $task_nodes('
            'FIBER_TRAVERSE_RESULT pfibertraversal "getIterator")) = 1',
            '$fiber_traversal_result_valid(S, pfibertraversal, "getIterator")',
            *ADMISSION, *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(THROW_SEARCH n_error) :: ptask_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_aggregate)]',
            'pdestructionrelease.ORIGIN = (pfiberstart.SITE)',
            'S_one.DESTRUCTION.RELEASES = [pdestructionrelease]',
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
    assert CATALOG.read_bytes() == SOURCE_BYTES, 'Aggregate originals changed during run'
    raise SystemExit(0 if passed else 1)
