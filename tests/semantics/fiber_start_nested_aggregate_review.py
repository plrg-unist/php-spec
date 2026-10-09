#!/usr/bin/env python3
"""Source-reached nested Aggregate owners, callback authority and retirement."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import fiber_state_review as review

CATALOG = Path(__file__).with_name('fiber_start_nested_aggregate_cases.json')
INPUT_BYTES = {path: path.read_bytes() for path in (Path(__file__), CATALOG)}
SOURCES = {row['id']: row['source'] for row in json.loads(INPUT_BYTES[CATALOG])}
ADMISSION = ['$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
ONE = ['S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
       'S_one = S_one_budget[.COMPLETION = NORMAL]']
HEADER = ['pfiberstart = pfibertraversal.START',
          'pfibertraversal.AGGREGATE = (n_original)',
          'S.OBJECTS[pfiberstart.OBJECT] = FIBER pfiber_target',
          'pfiber_target.STATUS = FIBER_INIT']
DEEP_PENDING = ('S.TODO = (CALL_ARGS pcalltarget eps 0 eps (porigin) z) :: '
                '(FIBER_TRAVERSE_RESULT pfibertraversal "getIterator") :: ptask_tail* '
                '-- if pfibertraversal.ACQUIRED = [n_middle, n_leaf]')
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
THROWING_DESTRUCTOR = (
    'S.TODO = (THROW_SEARCH n_error) :: (DESTRUCTOR_RESULT pdestructorcall) :: '
    '(DESTRUCTOR_RELEASE pdestructionrelease) :: '
    '(FIBER_TRAVERSE_RESULT pfibertraversal "acquired") :: ptask_tail* '
    '-- if S.CURRENT = eps')
PENDING_YIELD = (
    'S.TODO = (GENERATOR_YIELD_STORE porigin_yield poperand_key?) :: ptask_body* '
    '-- if S.RESULT = KNOWN (PINT 7) -- if S.FRAMES = [pframe] '
    '-- if pframe.TODO = (GENERATOR_RESUME pgeneratorop) :: '
    '(FIBER_TRAVERSE_GENERATOR pfibertraversal "rewind-error") :: ptask_saved*')
PENDING_EVENTS = ('[OUTPUT $ptascii("O|"), OUTPUT $ptascii("M|"), '
                  'OUTPUT $ptascii("N|"), OUTPUT $ptascii("n|"), '
                  'OUTPUT $ptascii("m|"), OUTPUT $ptascii("Y|")]')


def deep_stack_negative(replacement):
    return {
        'source': SOURCES['nested-fresh-iterator-owner-order'], 'stage': DEEP_PENDING,
        'checks': [
            'pfibertraversal.OBJECT = n_leaf',
            '$fiber_traversal_pending(S, pcalltarget, porigin)', *ADMISSION,
            'pfibertraversal_bad = pfibertraversal[.ACQUIRED = ' + replacement + ']',
            'S_bad = S[.TODO = (CALL_ARGS pcalltarget eps 0 eps (porigin) z) :: '
            '(FIBER_TRAVERSE_RESULT pfibertraversal_bad "getIterator") :: ptask_tail*]',
            '$heap_valid($heap_graph(S_bad))',
            '~$fiber_traversal_result_valid(S_bad, pfibertraversal_bad, "getIterator")',
            '~$fiber_traversal_pending(S_bad, pcalltarget, porigin)',
            '~$call_descriptors_valid(S_bad)',
        ],
    }


CASES = {
    'nested-deep-getter-borrows-receiver-and-owns-each-raw-layer': {
        'source': SOURCES['nested-fresh-iterator-owner-order'], 'stage': DEEP_PENDING,
        'checks': [
            *HEADER, 'porigin = pfiberstart.SITE', 'z = 25',
            'pfibertraversal.LINE = z', 'pfibertraversal.OBJECT = n_leaf',
            'pfibertraversal.INPUT = KNOWN (POBJECT n_original)',
            'pfibertraversal.CURRENT = KNOWN PNULL', 'pfibertraversal.ITEMS = eps',
            'pcalltarget = AGGREGATE_METHOD_TARGET n_leaf porigin_get',
            '$target_nodes(pcalltarget) = eps',
            '$fiber_traversal_pending(S, pcalltarget, porigin)',
            '$fiber_traversal_nodes(pfibertraversal, false) = '
            '[HOBJECT n_leaf, HOBJECT n_middle, HOBJECT n_original]',
            '$heap_owners($heap_graph(S), HOBJECT n_leaf) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_middle) = 1',
            *ADMISSION, *ONE,
            'S_one.CURRENT = (pcallcontext_get)',
            'pcallcontext_get.LINE = 25', 'pcallcontext_get.CALLSITE = (porigin)',
            'pcallcontext_get.TARGET = pcalltarget',
            '$heap_count(HOBJECT n_leaf, $call_context_roots(S_one.CURRENT)) = 0',
            '$heap_count(HOBJECT n_leaf, $destructor_context_nodes(S_one.CURRENT)) = 0',
            'S_one.FRAMES = pframe_unpack :: pframe_tail*',
            '$fiber_traversal_frame(S_one, pcallcontext_get, pframe_unpack, pframe_tail*)',
        ],
    },
    'nested-deep-getter-zero-budget-preserves-raw-stack': {
        'source': SOURCES['nested-fresh-iterator-owner-order'], 'stage': DEEP_PENDING,
        'checks': [
            '$heap_valid($heap_graph(S))',
            'S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
            'S_zero[.COMPLETION = NORMAL] = S',
        ],
    },
    'nested-getter-rejects-reversed-current-layer': deep_stack_negative('[n_leaf, n_middle]'),
    'nested-getter-rejects-adjacent-self-layer': deep_stack_negative('[n_middle, n_middle, n_leaf]'),
    'nested-repeated-ancestor-keeps-two-independent-retval-owners': {
        'source': SOURCES['nested-finite-repeated-ancestor'],
        'stage': ('S.TODO = (CALL_ARGS pcalltarget eps 0 eps (porigin) z) :: '
                  '(FIBER_TRAVERSE_RESULT pfibertraversal "getIterator") :: ptask_tail* '
                  '-- if pfibertraversal.ACQUIRED = [n_middle, n_original, n_middle]'),
        'checks': [
            *HEADER, 'pfibertraversal.OBJECT = n_middle', 'pfibertraversal.LINE = 34',
            'n_middle =/= n_original',
            'pcalltarget = AGGREGATE_METHOD_TARGET n_middle porigin_get',
            '$target_nodes(pcalltarget) = eps',
            '$fiber_traversal_acquisition_valid(S, n_original, pfibertraversal.ACQUIRED)',
            '$fiber_traversal_pending(S, pcalltarget, porigin)',
            '$heap_count(HOBJECT n_middle, $fiber_traversal_nodes(pfibertraversal, false)) = 2',
            '$heap_count(HOBJECT n_original, $fiber_traversal_nodes(pfibertraversal, false)) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_middle) = 3',
            '$heap_owners($heap_graph(S), HOBJECT n_original) = 2', *ADMISSION,
        ],
    },
    'nested-terminal-iterator-protects-data-during-inside-out-release': {
        'source': SOURCES['nested-fresh-iterator-owner-order'],
        'stage': ('S.TODO = (FIBER_TRAVERSE_RESULT pfibertraversal "getIterator") :: '
                  'ptask_tail* -- if pfibertraversal.ACQUIRED = [n_middle, n_leaf] '
                  '-- if S.RESULT = KNOWN (POBJECT n_iterator)'),
        'checks': [
            *HEADER, 'pfibertraversal.OBJECT = n_leaf',
            '$useriter_instance(S, n_iterator)',
            '$fiber_traversal_result_valid(S, pfibertraversal, "getIterator")',
            '$heap_count(HOBJECT n_iterator, $task_nodes('
            'FIBER_TRAVERSE_RESULT pfibertraversal "getIterator")) = 0',
            *ADMISSION, *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(FIBER_TRAVERSE_RESULT pfibertraversal_acquired "acquired") :: ptask_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_leaf), '
            'DESTRUCTION_VALUE (HOBJECT n_middle)]',
            'pdestructionrelease.ORIGIN = (pfiberstart.SITE)',
            'pfibertraversal_acquired = pfibertraversal[.OBJECT = n_iterator][.ACQUIRED = eps]',
            '$fiber_traversal_nodes(pfibertraversal_acquired, true) = '
            '[HOBJECT n_iterator, HOBJECT n_original]',
            '$destructor_release_valid(S_one, pdestructionrelease)',
            '$call_task_valid(S_one, FIBER_TRAVERSE_RESULT pfibertraversal_acquired "acquired")',
            '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
        ],
    },
    'nested-generator-method-promotes-current-layer-only': {
        'source': SOURCES['nested-generator-method-receiver-owner'],
        'stage': ('S.TODO = (GENERATOR_CREATE porigin_get) :: ptask_body* '
                  '-- if S.CURRENT = (pcallcontext_borrowed) '
                  '-- if S.FRAMES = [pframe_unpack] -- if pframe_unpack.TODO = '
                  '(FIBER_TRAVERSE_RESULT pfibertraversal "getIterator") :: ptask_unpack*'),
        'checks': [
            *HEADER, 'pfibertraversal.ACQUIRED = [n_inner]',
            'pfibertraversal.OBJECT = n_inner', 'n_inner =/= n_original',
            'pcallcontext_borrowed.TARGET = AGGREGATE_METHOD_TARGET n_inner porigin_get',
            '$heap_count(HOBJECT n_inner, $call_context_roots(S.CURRENT)) = 0',
            '$generator_creation_supported(S, pcallcontext_borrowed)',
            '$generator_create_valid(S, porigin_get)', *ADMISSION, *ONE,
            'S_one.RESULT = KNOWN (POBJECT n_generator)',
            'S_one.OBJECTS[n_generator] = GENERATOR pgenerator',
            'pgenerator.FRAME = (pframe_generator)',
            'pframe_generator.CONTEXT = (pcallcontext_owned)',
            'pcallcontext_owned.TARGET = AGGREGATE_GENERATOR_TARGET n_inner porigin_get '
            'pfiberstart.INDEX pfibertraversal.SITE pfibertraversal.LINE',
            'pcallcontext_owned[.TARGET = pcallcontext_borrowed.TARGET] = pcallcontext_borrowed',
            '$heap_count(HOBJECT n_inner, $call_context_roots(pframe_generator.CONTEXT)) = 1',
            '$heap_count(HOBJECT n_original, $call_context_roots(pframe_generator.CONTEXT)) = 0',
            '$heap_owners($heap_graph(S_one), HOBJECT n_inner) = 2',
            '$generator_frame_valid(S_one, pgenerator, pframe_generator)',
            '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
        ],
    },
    'nested-plain-generator-enters-after-layer-retirement': {
        'source': SOURCES['nested-plain-generator-owner-order'],
        'stage': ('S.TODO = (GENERATOR_YIELD_STORE porigin_yield poperand_key?) :: '
                  'ptask_body* -- if S.RESULT = KNOWN (PINT 7) '
                  '-- if S.FRAMES = [pframe] -- if pframe.TODO = '
                  '(GENERATOR_RESUME pgeneratorop) :: '
                  '(FIBER_TRAVERSE_GENERATOR pfibertraversal "rewind") :: ptask_saved*'),
        'checks': [
            *HEADER, 'pfibertraversal.ACQUIRED = eps',
            'n_generator = pfibertraversal.OBJECT',
            'pfibertraversal.INPUT = KNOWN (POBJECT n_original)',
            'pgeneratorop.OBJECT = n_generator', 'pgeneratorop.STARTPACK',
            'pgeneratorop.LINE = 15',
            '$fiber_traversal_generator_valid(S, pgeneratorop)',
            '$heap_count(HOBJECT n_generator, $task_nodes(GENERATOR_RESUME pgeneratorop)) = 1',
            '$heap_count(HOBJECT n_generator, $task_nodes('
            'FIBER_TRAVERSE_GENERATOR pfibertraversal "rewind")) = 0',
            'S.EVENTS = [OUTPUT $ptascii("O|"), OUTPUT $ptascii("N|"), '
            'OUTPUT $ptascii("n|"), OUTPUT $ptascii("Y|")]', *ADMISSION,
        ],
    },
    'nested-parked-getter-retains-raw-owner-with-borrowed-context': {
        'source': SOURCES['nested-get-iterator-parks'], 'stage': PARK,
        'checks': [
            *HEADER, 'pfibertraversal.ACQUIRED = [n_inner]',
            'pfibertraversal.OBJECT = n_inner', 'pfibertraversal.LINE = 29',
            'pfibertraversal.INPUT = KNOWN (POBJECT n_original)',
            'pfiber_parent.STATUS = FIBER_SUSPENDED',
            '$fiber_traversal_nodes(pfibertraversal, false) = [HOBJECT n_inner, HOBJECT n_original]',
            *PARK_VIEW,
            'pcallcontext_get.TARGET = AGGREGATE_METHOD_TARGET n_inner porigin_get',
            'pcallcontext_get.CALLSITE = (pfiberstart.SITE)',
            'pcallcontext_get.LINE = 29',
            '$heap_count(HOBJECT n_inner, $call_context_roots(pfibervm.CURRENT)) = 0',
            '$heap_count(HOBJECT n_inner, $destructor_context_nodes(pfibervm.CURRENT)) = 0',
            '$heap_owners($heap_graph(S), HOBJECT n_inner) = 1',
            '$fiber_traversal_result_valid(S_scope, pfibertraversal, "getIterator")',
            *ADMISSION,
            'S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
            'S_zero[.COMPLETION = NORMAL] = S',
        ],
    },
    'nested-parked-getter-rejects-shifted-unpack-line': {
        'source': SOURCES['nested-get-iterator-parks'], 'stage': PARK,
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
            '~$fiber_vm_valid(S_bad, pfibervm_bad, (n_parent), eps)',
            '~$call_descriptors_valid(S_bad)',
        ],
    },
    'nested-parked-getter-rejects-duplicate-start-continuation': {
        'source': SOURCES['nested-get-iterator-parks'], 'stage': PARK,
        'checks': [
            *PARK_VIEW, *ADMISSION,
            'pframe_bad = pframe_unpack[.TODO = '
            '(FIBER_TRAVERSE_RESULT pfibertraversal "getIterator") :: '
            '(FIBER_TRAVERSE_RESULT pfibertraversal "getIterator") :: ptask_unpack*]',
            'pfibervm_bad = pfibervm[.FRAMES = [pframe_bad, pframe_base]]',
            'S_bad = S[.OBJECTS[n_parent] = FIBER pfiber_parent[.VM = (pfibervm_bad)]]',
            '$fiber_start_unpack_count(pframe_bad.TODO, pfibertraversal.CAPTURE, '
            'pfibertraversal.START.SITE) = 2',
            'S_scope_bad = S_scope[.TODO = pframe_bad.TODO]',
            '~$fiber_traversal_result_valid(S_scope_bad, pfibertraversal, "getIterator")',
            '$heap_valid($heap_graph(S_bad))',
            '~$fiber_vm_valid(S_bad, pfibervm_bad, (n_parent), eps)',
            '~$call_descriptors_valid(S_bad)',
        ],
    },
    'nested-raw-reference-error-keeps-reference-and-layer-until-unwind': {
        'source': SOURCES['nested-reference-return-rejected'],
        'stage': ('S.TODO = (FIBER_TRAVERSE_RESULT pfibertraversal "getIterator") :: '
                  'ptask_tail* -- if S.RESULT = REFERENCE n_return '
                  '-- if pfibertraversal.ACQUIRED = [n_inner]'),
        'checks': [
            *HEADER, 'pfibertraversal.OBJECT = n_inner',
            'S.STORE[n_return] = DEFINED (POBJECT n_iterator)',
            '$useriter_instance(S, n_iterator)',
            '$fiber_traversal_result_valid(S, pfibertraversal, "getIterator")',
            *ADMISSION, *ONE,
            'S_one.TODO = (THROW_SEARCH n_error) :: '
            '(FIBER_TRAVERSE_RESULT pfibertraversal_error "getIterator-error") :: ptask_tail*',
            'pfibertraversal_error = pfibertraversal[.CURRENT = REFERENCE n_return]',
            '$fiber_traversal_nodes(pfibertraversal_error, false) = '
            '[HCELL n_return, HOBJECT n_inner, HOBJECT n_original]',
            '$fiber_traversal_result_valid(S_one, pfibertraversal_error, "getIterator-error")',
            '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
        ],
    },
    'nested-getter-throw-retires-layer-before-original-and-keeps-direct-capture': {
        'source': SOURCES['nested-get-iterator-throws-direct-fcc'],
        'stage': ('S.TODO = (THROW_SEARCH n_error) :: '
                  '(FIBER_TRAVERSE_RESULT pfibertraversal "getIterator") :: ptask_tail* '
                  '-- if S.CURRENT = eps -- if pfibertraversal.ACQUIRED = [n_inner]'),
        'checks': [
            *HEADER, 'pfibertraversal.OBJECT = n_inner',
            'pfibertraversal.CAPTURE = (n_capture)',
            '~$exit_method_site(S, pfiberstart.SITE)',
            'pfibertraversal.CURRENT = KNOWN PNULL',
            'pfibertraversal.INPUT = KNOWN (POBJECT n_original)',
            '$fiber_traversal_nodes(pfibertraversal, false) = [HOBJECT n_inner, HOBJECT n_original]',
            *ADMISSION, *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(THROW_SEARCH n_error) :: ptask_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_inner), '
            'DESTRUCTION_VALUE (HOBJECT n_original)]',
            'pdestructionrelease.ORIGIN = (pfiberstart.SITE)',
            '$destructor_release_valid(S_one, pdestructionrelease)',
            '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
        ],
    },
    'nested-destructor-throw-transfers-pending-owner-before-remaining-layer': {
        'source': SOURCES['nested-intermediate-destructor-throws'],
        'stage': THROWING_DESTRUCTOR,
        'checks': [
            *HEADER, 'pfibertraversal.ACQUIRED = eps',
            'pfibertraversal.OBJECT = n_iterator', '$useriter_instance(S, n_iterator)',
            'pdestructorcall.RELEASE = (pdestructionrelease_before)',
            'pdestructionrelease_before.JOBS = '
            '[DESTRUCTION_VALUE (HOBJECT pdestructorcall.OBJECT), '
            'DESTRUCTION_VALUE (HOBJECT n_middle)]',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_middle)]',
            'pdestructorcall.PENDING = eps',
            '$destructor_result_valid(S, pdestructorcall)', *ADMISSION, *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_inner) :: '
            '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: '
            '(DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(FIBER_TRAVERSE_RESULT pfibertraversal_error "acquired-error") :: ptask_tail*',
            'pdestructionrelease_inner = pdestructionrelease[.JOBS = '
            '[DESTRUCTION_VALUE (HOBJECT pdestructorcall.OBJECT)]]',
            'pdestructionoperation.SOURCE = THROW_SEARCH n_error',
            'pdestructionoperation.PENDING = eps',
            'pdestructionoperation.CALLER = pdestructorcall.CALLER',
            'pdestructionoperation.ORIGIN = pdestructorcall.ORIGIN',
            '$destructor_operation_valid(S_one, pdestructionoperation)',
            'pfibertraversal_error = pfibertraversal[.CURRENT = KNOWN (POBJECT n_error)]',
            '$destructor_tail_pending((DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(FIBER_TRAVERSE_RESULT pfibertraversal_error "acquired-error") :: ptask_tail*) = '
            '(n_error)',
            '$heap_count(HOBJECT n_error, $tasks_nodes(S_one.TODO)) = 1',
            '$heap_count(HOBJECT n_iterator, $tasks_nodes(S_one.TODO)) = 1',
            '$heap_count(HOBJECT n_original, $tasks_nodes(S_one.TODO)) = 1',
            '$heap_count(HOBJECT n_middle, $tasks_nodes(S_one.TODO)) = 1',
            '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
        ],
    },
    'nested-destructor-pending-hook-rejects-foreign-release-snapshot': {
        'source': SOURCES['nested-intermediate-destructor-throws'],
        'stage': THROWING_DESTRUCTOR,
        'checks': [
            'S.DESTRUCTION.CALLS = pdestructorcall :: pdestructorcall_tail*',
            'pdestructorcall.RELEASE = (pdestructionrelease_before)',
            '$destructor_result_valid(S, pdestructorcall)', *ADMISSION,
            'S_clean = S[.TODO = (THROW_SEARCH n_error) :: '
            '(DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(FIBER_TRAVERSE_RESULT pfibertraversal "acquired") :: ptask_tail*]'
            '[.DESTRUCTION.CALLS = pdestructorcall_tail*]',
            'S_resume = $destructor_resume_pending(S_clean, pdestructorcall)',
            'S_resume.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(FIBER_TRAVERSE_RESULT pfibertraversal_error "acquired-error") :: ptask_tail*',
            'pfibertraversal_error = pfibertraversal[.CURRENT = KNOWN (POBJECT n_error)]',
            'pdestructorcall_bad = pdestructorcall[.RELEASE = '
            '(pdestructionrelease_before[.ORIGIN = eps])]',
            'S_bad = S[.TODO = (THROW_SEARCH n_error) :: '
            '(DESTRUCTOR_RESULT pdestructorcall_bad) :: '
            '(DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(FIBER_TRAVERSE_RESULT pfibertraversal "acquired") :: ptask_tail*]'
            '[.DESTRUCTION.CALLS = pdestructorcall_bad :: pdestructorcall_tail*]',
            '$heap_graph(S_bad) = $heap_graph(S)',
            '~$destructor_result_valid(S_bad, pdestructorcall_bad)',
            '~$call_descriptors_valid(S_bad)',
            '$destructor_resume_pending(S_clean, pdestructorcall_bad) = S_clean',
        ],
    },
    'nested-pending-retirement-finishes-before-data-and-original-unwind': {
        'source': SOURCES['nested-intermediate-destructor-throws'],
        'stage': ('S.TODO = (FIBER_TRAVERSE_RESULT pfibertraversal "acquired-error") :: '
                  'ptask_tail* -- if pfibertraversal.CURRENT = KNOWN (POBJECT n_error)'),
        'checks': [
            *HEADER, 'pfibertraversal.ACQUIRED = eps',
            'pfibertraversal.CAPTURE = eps', 'pfibertraversal.SENT.SLOTS = eps',
            'pfibertraversal.SENT.NAMED = eps',
            'n_iterator = pfibertraversal.OBJECT', '$useriter_instance(S, n_iterator)',
            'S.EVENTS = [OUTPUT $ptascii("O|"), OUTPUT $ptascii("M|"), '
            'OUTPUT $ptascii("N|"), OUTPUT $ptascii("n|"), OUTPUT $ptascii("m|")]',
            '$fiber_traversal_result_valid(S, pfibertraversal, "acquired-error")',
            '$fiber_traversal_nodes(pfibertraversal, true) = '
            '[HOBJECT n_error, HOBJECT n_iterator, HOBJECT n_original]',
            *ADMISSION, *ONE,
            'S_one.TODO = (THROW_SEARCH n_error) :: '
            '(FIBER_TRAVERSE_RESULT pfibertraversal_clean "acquired") :: ptask_tail*',
            'pfibertraversal_clean = pfibertraversal[.CURRENT = KNOWN PNULL]',
            'S_two_budget = $drive_steps(S_one, 1)', 'S_two_budget.COMPLETION = BUDGET',
            'S_two = S_two_budget[.COMPLETION = NORMAL]',
            'S_two.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(THROW_SEARCH n_error) :: ptask_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_iterator), '
            'DESTRUCTION_VALUE (HOBJECT n_original), '
            'DESTRUCTION_VALUE (HOBJECT pfiberstart.OBJECT)]',
            '$destructor_release_valid(S_two, pdestructionrelease)',
            '$call_descriptors_valid(S_two)', '$heap_valid($heap_graph(S_two))',
        ],
    },
    'nested-pending-generator-runs-real-body-with-exception-in-resumer': {
        'source': SOURCES['nested-intermediate-destructor-throws-generator'],
        'stage': PENDING_YIELD,
        'checks': [
            *HEADER, 'pfibertraversal.CURRENT = KNOWN (POBJECT n_error)',
            'pfibertraversal.ACQUIRED = eps', 'pfibertraversal.LINE = 21',
            'n_generator = pfibertraversal.OBJECT',
            'S.OBJECTS[n_generator] = GENERATOR pgenerator',
            'pgenerator.PHASE = GENERATOR_RUNNING', 'pgenerator.FRAME = eps',
            'pgeneratorop.NAME = "rewind"', 'pgeneratorop.STARTPACK',
            'pgeneratorop.LINE = 21', 'pgeneratorop.SITE = pfiberstart.SITE',
            '$throwable_live(S, n_error)',
            '$fiber_traversal_pending_body(S, n_generator)',
            '$fiber_traversal_generator_valid(S, pgeneratorop)',
            '$heap_count(HOBJECT n_error, $task_nodes('
            'FIBER_TRAVERSE_GENERATOR pfibertraversal "rewind-error")) = 1',
            '$heap_count(HOBJECT n_error, $tasks_nodes(S.TODO)) = 0',
            '$heap_count(HOBJECT n_error, $call_context_roots(S.CURRENT)) = 0',
            '$heap_count(HOBJECT n_generator, $task_nodes(GENERATOR_RESUME pgeneratorop)) = 1',
            '$heap_count(HOBJECT n_generator, $task_nodes('
            'FIBER_TRAVERSE_GENERATOR pfibertraversal "rewind-error")) = 0',
            'S.EVENTS = ' + PENDING_EVENTS, *ADMISSION,
        ],
    },
    'nested-pending-generator-rejects-nonthrowable-resumer-owner': {
        'source': SOURCES['nested-intermediate-destructor-throws-generator'],
        'stage': PENDING_YIELD,
        'checks': [
            'pfibertraversal.AGGREGATE = (n_original)',
            '$fiber_traversal_generator_valid(S, pgeneratorop)', *ADMISSION,
            'pfibertraversal_bad = pfibertraversal[.CURRENT = KNOWN (POBJECT n_original)]',
            'pframe_bad = pframe[.TODO = (GENERATOR_RESUME pgeneratorop) :: '
            '(FIBER_TRAVERSE_GENERATOR pfibertraversal_bad "rewind-error") :: ptask_saved*]',
            'S_bad = S[.FRAMES = [pframe_bad]]',
            '$heap_valid($heap_graph(S_bad))',
            '~$fiber_traversal_generator_valid(S_bad, pgeneratorop)',
            '~$call_descriptors_valid(S_bad)',
        ],
    },
    'nested-pending-generator-closes-paused-empty-frame-without-finally': {
        'source': SOURCES['nested-intermediate-destructor-throws-generator'],
        'stage': ('S.TODO = (GENERATOR_RESUME pgeneratorop) :: '
                  '(FIBER_TRAVERSE_GENERATOR pfibertraversal "rewind-error") :: ptask_tail* '
                  '-- if S.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator '
                  '-- if pgenerator.PHASE = GENERATOR_PAUSED '
                  '-- if pgenerator.FRAME = (pframe_generator)'),
        'checks': [
            *HEADER, 'pfibertraversal.CURRENT = KNOWN (POBJECT n_error)',
            'pgenerator.VALUE = (PINT 7)', 'pgenerator.KEY = (PINT 0)',
            'pgenerator.RETURN = eps',
            '$generator_close_frame_nodes(S, pframe_generator) = eps',
            '$fiber_traversal_generator_valid(S, pgeneratorop)',
            'S.EVENTS = ' + PENDING_EVENTS, *ADMISSION, *ONE,
            'S_one.TODO = (THROW_SEARCH n_error) :: '
            '(FIBER_TRAVERSE_RESULT pfibertraversal_clean "acquired") :: ptask_tail*',
            'pfibertraversal_clean = pfibertraversal[.CURRENT = KNOWN PNULL]',
            'S_one.OBJECTS[pgeneratorop.OBJECT] = '
            'GENERATOR pgenerator[.FRAME = eps][.PHASE = GENERATOR_CLOSED]',
            '$heap_count(HOBJECT n_error, $task_nodes(THROW_SEARCH n_error)) = 1',
            '$heap_count(HOBJECT n_error, $task_nodes('
            'FIBER_TRAVERSE_RESULT pfibertraversal_clean "acquired")) = 0',
            'S_one.EVENTS = S.EVENTS',
            '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
        ],
    },
    'nested-pending-closed-generator-retires-data-before-original': {
        'source': SOURCES['nested-intermediate-destructor-throws-generator'],
        'stage': ('S.TODO = (THROW_SEARCH n_error) :: '
                  '(FIBER_TRAVERSE_RESULT pfibertraversal "acquired") :: ptask_tail* '
                  '-- if S.OBJECTS[pfibertraversal.OBJECT] = GENERATOR pgenerator '
                  '-- if pgenerator.PHASE = GENERATOR_CLOSED'),
        'checks': [
            *HEADER, 'n_generator = pfibertraversal.OBJECT',
            'pfibertraversal.CURRENT = KNOWN PNULL', 'pfibertraversal.ACQUIRED = eps',
            'pfibertraversal.CAPTURE = eps', 'pfibertraversal.SENT.SLOTS = eps',
            'pfibertraversal.SENT.NAMED = eps',
            'pgenerator.FRAME = eps', 'pgenerator.VALUE = (PINT 7)',
            'pgenerator.KEY = (PINT 0)', 'pgenerator.RETURN = eps',
            'S.EVENTS = ' + PENDING_EVENTS, *ADMISSION, *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(THROW_SEARCH n_error) :: ptask_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_generator), '
            'DESTRUCTION_VALUE (HOBJECT n_original), '
            'DESTRUCTION_VALUE (HOBJECT pfiberstart.OBJECT)]',
            'pdestructionrelease.ORIGIN = (pfiberstart.SITE)',
            '$destructor_release_valid(S_one, pdestructionrelease)',
            'S_one.EVENTS = S.EVENTS',
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
    passed = review.run(args.case or list(CASES))
    assert all(path.read_bytes() == original for path, original in INPUT_BYTES.items()), \
        'Nested Aggregate runner or originals changed during run'
    raise SystemExit(0 if passed else 1)
