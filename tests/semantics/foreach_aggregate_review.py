#!/usr/bin/env python3
"""Real foreach Aggregate callback authority, owners and ordered retirement."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import fiber_state_review as review

CATALOG = Path(__file__).with_name('foreach_aggregate_cases.json')
INPUT_BYTES = {path: path.read_bytes() for path in (Path(__file__), CATALOG)}
SOURCES = {row['id']: row['source'] for row in json.loads(INPUT_BYTES[CATALOG])}
ADMISSION = ['$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
POST = ['$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))']
ONE = ['S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
       'S_one = S_one_budget[.COMPLETION = NORMAL]']
ZERO = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S']
HEADER = ['n_original = pforeachaggregate.AGGREGATE',
          '$foreach_aggregate_site(S, pforeachaggregate.STATEMENT, '
          'pforeachaggregate.SITE, pforeachaggregate.LINE)']
DEEP_PENDING = ('S.TODO = (CALL_ARGS pcalltarget eps 0 eps (porigin) z) :: '
                '(FOREACH_AGGREGATE pforeachaggregate "getIterator") :: ptask_tail* '
                '-- if pforeachaggregate.ACQUIRED = [n_middle, n_inner]')
PARK = ('S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_main* '
        '-- if pconfigcall.KIND = INTRINSIC_FIBER_RESUME '
        '-- if pconfigcall.OWNER = (n_parent) '
        '-- if $fiber_at(S, n_parent) = (pfiber_parent) '
        '-- if pfiber_parent.VM = (pfibervm) '
        '-- if pfibervm.FRAMES = [pframe_foreach, pframe_base] '
        '-- if pframe_foreach.TODO = '
        '(FOREACH_AGGREGATE pforeachaggregate "getIterator") :: ptask_foreach*')
PARK_VIEW = ['S_view = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_parent)]'
             '[.FIBERCALLERS = eps][.COMPLETION = NORMAL]',
             'pfibervm.CURRENT = (pcallcontext_get)',
             'S_scope = $constant_frame_scope(S_view, pframe_foreach, [pframe_base])',
             '$foreach_aggregate_frame(S_view, pcallcontext_get, pframe_foreach)']
LAYER_THROW = ('S.TODO = (THROW_SEARCH n_error) :: '
               '(DESTRUCTOR_RESULT pdestructorcall) :: '
               '(DESTRUCTOR_RELEASE pdestructionrelease) :: '
               '(FOREACH_AGGREGATE pforeachaggregate "acquired") :: ptask_tail* '
               '-- if S.CURRENT = eps')
CLOSE_PARK = ('S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_main* '
              '-- if pconfigcall.KIND = INTRINSIC_FIBER_RESUME '
              '-- if pconfigcall.OWNER = (n_parent) '
              '-- if $fiber_at(S, n_parent) = (pfiber_parent) '
              '-- if pfiber_parent.VM = (pfibervm) '
              '-- if pfibervm.FRAMES = [pframe_close, pframe_base] '
              '-- if pframe_close.TODO = (GENERATOR_CLOSE_DONE pgenclose) :: ptask_saved*')
CLOSE_VIEW = ['S_view = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_parent)]'
              '[.FIBERCALLERS = eps][.COMPLETION = NORMAL]',
              'pfibervm.CURRENT = (pcallcontext_close)',
              'pcallcontext_close.TARGET = FOREACH_AGGREGATE_GENERATOR_TARGET '
              'n_original porigin_get porigin_foreach z',
              'pgenclose.CONTEXT = pcallcontext_close',
              'S.OBJECTS[pgenclose.OBJECT] = GENERATOR pgenerator',
              'pgenerator.PHASE = GENERATOR_RUNNING']

CASES = {
    'foreach-deep-getter-borrows-receiver-and-owns-raw-layers': {
        'source': SOURCES['foreach-aggregate-nested-temporary-break'],
        'stage': DEEP_PENDING,
        'checks': [
            *HEADER, 'pforeachaggregate.SITE = porigin', 'z = 22',
            'pforeachaggregate.LINE = z', 'pforeachaggregate.OBJECT = n_inner',
            'pforeachaggregate.INPUT = KNOWN (POBJECT n_original)',
            'pforeachaggregate.CURRENT = KNOWN PNULL', 'pforeachaggregate.ITERATOR = eps',
            'pcalltarget = AGGREGATE_METHOD_TARGET n_inner porigin_get',
            '$target_nodes(pcalltarget) = eps',
            '$foreach_aggregate_pending_site(S, porigin)',
            '$task_nodes(FOREACH_AGGREGATE pforeachaggregate "getIterator") = '
            '[HOBJECT n_inner, HOBJECT n_middle, HOBJECT n_original]',
            '$heap_owners($heap_graph(S), HOBJECT n_inner) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_middle) = 1',
            *ADMISSION, *ONE,
            'S_one.CURRENT = (pcallcontext_get)',
            'pcallcontext_get.TARGET = pcalltarget', 'pcallcontext_get.LINE = 22',
            'pcallcontext_get.CALLSITE = (porigin)',
            '$heap_count(HOBJECT n_inner, $call_context_roots(S_one.CURRENT)) = 0',
            '$heap_count(HOBJECT n_inner, $destructor_context_nodes(S_one.CURRENT)) = 0',
            'S_one.FRAMES = pframe_foreach :: pframe_tail*',
            '$foreach_aggregate_frame(S_one, pcallcontext_get, pframe_foreach)', *POST,
        ],
    },
    'foreach-getter-rejects-owning-target': {
        'source': SOURCES['foreach-aggregate-nested-temporary-break'],
        'stage': DEEP_PENDING,
        'checks': [
            'pcalltarget = AGGREGATE_METHOD_TARGET n_inner porigin_get',
            '$foreach_aggregate_pending_site(S, porigin)', *ADMISSION,
            'pcalltarget_owned = METHOD_TARGET n_inner porigin_get',
            'S_bad = S[.TODO = (CALL_ARGS pcalltarget_owned eps 0 eps (porigin) z) :: '
            '(FOREACH_AGGREGATE pforeachaggregate "getIterator") :: ptask_tail*]',
            '$heap_valid($heap_graph(S_bad))',
            '$heap_owners($heap_graph(S_bad), HOBJECT n_inner) = '
            '$($heap_owners($heap_graph(S), HOBJECT n_inner) + 1)',
            '~$foreach_aggregate_pending_site(S_bad, porigin)',
            '~$call_task_valid(S_bad, CALL_ARGS pcalltarget_owned eps 0 eps (porigin) z)',
            '~$call_descriptors_valid(S_bad)',
        ],
    },
    'foreach-getter-rejects-foreign-line-and-preserves-zero-budget': {
        'source': SOURCES['foreach-aggregate-nested-temporary-break'],
        'stage': DEEP_PENDING,
        'checks': [
            '$foreach_aggregate_pending_site(S, porigin)', *ADMISSION, *ZERO,
            'pforeachaggregate_bad = pforeachaggregate[.LINE = $(z + 1)]',
            'S_bad = S[.TODO = (CALL_ARGS pcalltarget eps 0 eps (porigin) $(z + 1)) :: '
            '(FOREACH_AGGREGATE pforeachaggregate_bad "getIterator") :: ptask_tail*]',
            '$heap_graph(S_bad) = $heap_graph(S)',
            '~$foreach_aggregate_result_valid(S_bad, pforeachaggregate_bad, "getIterator")',
            '~$foreach_aggregate_pending_site(S_bad, porigin)',
            '~$call_descriptors_valid(S_bad)',
        ],
    },
    'foreach-terminal-acquisition-protects-data-before-layer-retirement': {
        'source': SOURCES['foreach-aggregate-nested-temporary-break'],
        'stage': ('S.TODO = (FOREACH_AGGREGATE pforeachaggregate "getIterator") :: '
                  'ptask_tail* -- if pforeachaggregate.ACQUIRED = [n_middle, n_inner] '
                  '-- if S.RESULT = KNOWN (POBJECT n_data)'),
        'checks': [
            *HEADER, '$useriter_instance(S, n_data)',
            'pforeachaggregate.INPUT = KNOWN (POBJECT n_original)',
            'pforeachaggregate.ITERATOR = eps',
            '$task_nodes(FOREACH_AGGREGATE pforeachaggregate "getIterator") = '
            '[HOBJECT n_inner, HOBJECT n_middle, HOBJECT n_original]',
            *ADMISSION, *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(FOREACH_AGGREGATE pforeachaggregate_data "acquired") :: ptask_tail*',
            'pforeachaggregate_data = pforeachaggregate[.OBJECT = n_data][.ACQUIRED = eps]',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_inner), '
            'DESTRUCTION_VALUE (HOBJECT n_middle)]',
            'pdestructionrelease.ORIGIN = (pforeachaggregate.SITE)',
            '$task_nodes(FOREACH_AGGREGATE pforeachaggregate_data "acquired") = '
            '[HOBJECT n_data, HOBJECT n_original]',
            '$heap_owners($heap_graph(S_one), HOBJECT n_data) = 1',
            'S_one.ITERATORS = S.ITERATORS', 'S_one.NEXTITER = S.NEXTITER',
            '$destructor_release_valid(S_one, pdestructionrelease)', *POST,
        ],
    },
    'foreach-first-valid-retires-input-before-current': {
        'source': SOURCES['foreach-aggregate-nested-temporary-break'],
        'stage': ('S.TODO = (FOREACH_AGGREGATE pforeachaggregate "ready") :: ptask_tail*'),
        'checks': [
            *HEADER, 'n_data = pforeachaggregate.OBJECT',
            'pforeachaggregate.INPUT = KNOWN (POBJECT n_original)',
            'pforeachaggregate.ACQUIRED = eps', 'pforeachaggregate.ITERATOR = (n_cursor)',
            '$iterator_lookup(S.ITERATORS, n_cursor) = (OBJECTITER n_cursor n_data 0 false)',
            '$task_nodes(FOREACH_AGGREGATE pforeachaggregate "ready") = '
            '[HOBJECT n_data, HOBJECT n_original]',
            'S.EVENTS = [OUTPUT $ptascii("O|"), OUTPUT $ptascii("M|"), '
            'OUTPUT $ptascii("N|"), OUTPUT $ptascii("n|"), OUTPUT $ptascii("m|"), '
            'OUTPUT $ptascii("W|"), OUTPUT $ptascii("V|")]',
            *ADMISSION, *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(FOREACH_AGGREGATE pforeachaggregate_current "current") :: ptask_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_original)]',
            'pforeachaggregate_current = pforeachaggregate[.INPUT = KNOWN PNULL]',
            '$task_nodes(FOREACH_AGGREGATE pforeachaggregate_current "current") = [HOBJECT n_data]',
            'S_one.ITERATORS = S.ITERATORS', *POST,
        ],
    },
    'foreach-empty-valid-retires-input-before-data': {
        'source': SOURCES['foreach-aggregate-empty-iterator'],
        'stage': ('S.TODO = (FOREACH_AGGREGATE pforeachaggregate "empty") :: ptask_tail*'),
        'checks': [
            *HEADER, 'n_data = pforeachaggregate.OBJECT',
            'pforeachaggregate.INPUT = KNOWN (POBJECT n_original)',
            'pforeachaggregate.ITERATOR = (n_cursor)',
            'S.EVENTS = [OUTPUT $ptascii("G|"), OUTPUT $ptascii("W|"), OUTPUT $ptascii("V|")]',
            *ADMISSION, *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(FOREACH_AGGREGATE pforeachaggregate_finish "finish") :: ptask_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_original)]',
            'pforeachaggregate_finish = pforeachaggregate[.INPUT = KNOWN PNULL]',
            '$task_nodes(FOREACH_AGGREGATE pforeachaggregate_finish "finish") = [HOBJECT n_data]',
            '$heap_count(HOBJECT n_data, $tasks_nodes(S_one.TODO)) = 1', *POST,
            'S_done = $drive(S_one, 4000)', *review.DONE,
            'S_done.EVENTS = [OUTPUT $ptascii("G|"), OUTPUT $ptascii("W|"), '
            'OUTPUT $ptascii("V|"), OUTPUT $ptascii("A|"), OUTPUT $ptascii("I|"), '
            'OUTPUT $ptascii("E")]',
        ],
    },
    'foreach-valid-raw-retval-destructor-precedes-input-release': {
        'source': SOURCES['foreach-aggregate-valid-retval-retirement'],
        'stage': ('S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
                  '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: '
                  '(FOREACH_AGGREGATE pforeachaggregate "ready") :: ptask_tail* '
                  '-- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_retval)]'),
        'checks': [
            *HEADER, 'n_data = pforeachaggregate.OBJECT',
            'pforeachaggregate.INPUT = KNOWN (POBJECT n_original)',
            'pdestructionoperation.SOURCE = FOREACH_AGGREGATE pforeachaggregate "valid"',
            '$destructor_operation_valid(S, pdestructionoperation)',
            '$destructor_release_valid(S, pdestructionrelease)',
            '$task_nodes(FOREACH_AGGREGATE pforeachaggregate "ready") = '
            '[HOBJECT n_data, HOBJECT n_original]',
            '$heap_count(HOBJECT n_retval, $tasks_nodes(S.TODO)) = 1',
            '$heap_count(HOBJECT n_data, $tasks_nodes(S.TODO)) = 1',
            '$heap_count(HOBJECT n_original, $tasks_nodes(S.TODO)) = 1',
            '~(n_retval <- S.DESTRUCTION.CALLED)', '~(n_original <- S.DESTRUCTION.CALLED)',
            'S.EVENTS = [OUTPUT $ptascii("G|"), OUTPUT $ptascii("W|"), OUTPUT $ptascii("V|")]',
            *ADMISSION,
        ],
    },
    'foreach-valid-retval-throw-keeps-data-and-input-for-unwind': {
        'source': SOURCES['foreach-aggregate-valid-retval-destructor-throws'],
        'stage': ('S.TODO = (THROW_SEARCH n_error) :: (DESTRUCTOR_RESULT pdestructorcall) :: '
                  '(DESTRUCTOR_RELEASE pdestructionrelease) :: '
                  '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: '
                  '(FOREACH_AGGREGATE pforeachaggregate "ready") :: ptask_tail* '
                  '-- if S.CURRENT = eps'),
        'checks': [
            *HEADER, 'n_data = pforeachaggregate.OBJECT',
            'pforeachaggregate.INPUT = KNOWN (POBJECT n_original)',
            'pdestructorcall.OPERATION = (pdestructionoperation)',
            'pdestructionoperation.SOURCE = FOREACH_AGGREGATE pforeachaggregate "valid"',
            '$destructor_result_valid(S, pdestructorcall)',
            '$task_nodes(FOREACH_AGGREGATE pforeachaggregate "ready") = '
            '[HOBJECT n_data, HOBJECT n_original]',
            '$lookup(S.ENV, $ptascii("failure")) = (n_failure)',
            'S.STORE[n_failure] = DEFINED (POBJECT n_error)',
            '~(n_data <- S.DESTRUCTION.CALLED)', '~(n_original <- S.DESTRUCTION.CALLED)',
            'S.EVENTS = [OUTPUT $ptascii("G|"), OUTPUT $ptascii("W|"), '
            'OUTPUT $ptascii("V|"), OUTPUT $ptascii("R|")]',
            *ADMISSION,
            'S_done = $drive(S, 4000)', *review.DONE,
            'S_done.EVENTS = [OUTPUT $ptascii("G|"), OUTPUT $ptascii("W|"), '
            'OUTPUT $ptascii("V|"), OUTPUT $ptascii("R|"), OUTPUT $ptascii("I|"), '
            'OUTPUT $ptascii("A|"), OUTPUT $ptascii("1"), OUTPUT $ptascii("|")]',
        ],
    },
    'foreach-generator-method-promotes-only-copied-receiver': {
        'source': SOURCES['foreach-aggregate-generator-method-break'],
        'stage': ('S.TODO = (GENERATOR_CREATE porigin_get) :: ptask_body* '
                  '-- if S.CURRENT = (pcallcontext_borrowed) '
                  '-- if S.FRAMES = [pframe_foreach] -- if pframe_foreach.TODO = '
                  '(FOREACH_AGGREGATE pforeachaggregate "getIterator") :: ptask_tail*'),
        'checks': [
            *HEADER, 'pforeachaggregate.LINE = 10',
            'pcallcontext_borrowed.TARGET = AGGREGATE_METHOD_TARGET n_original porigin_get',
            '$heap_count(HOBJECT n_original, $call_context_roots(S.CURRENT)) = 0',
            '$generator_create_valid(S, porigin_get)', *ADMISSION, *ONE,
            'S_one.TODO = (FOREACH_AGGREGATE pforeachaggregate "getIterator") :: ptask_tail*',
            'S_one.RESULT = KNOWN (POBJECT n_generator)',
            'S_one.OBJECTS[n_generator] = GENERATOR pgenerator',
            'pgenerator.PHASE = GENERATOR_FRESH', 'pgenerator.FRAME = (pframe_generator)',
            'pframe_generator.CONTEXT = (pcallcontext_owned)',
            'pcallcontext_owned.TARGET = FOREACH_AGGREGATE_GENERATOR_TARGET n_original '
            'porigin_get pforeachaggregate.SITE 10',
            'pcallcontext_owned[.TARGET = pcallcontext_borrowed.TARGET] = pcallcontext_borrowed',
            '$heap_count(HOBJECT n_original, $call_context_roots(pframe_generator.CONTEXT)) = 1',
            '$heap_count(HOBJECT n_original, $node_children(S_one, HOBJECT n_generator)) = 1',
            '$generator_frame_valid(S_one, pgenerator, pframe_generator)', *POST,
        ],
    },
    'foreach-generator-rejects-shifted-receipt-and-context-line': {
        'source': SOURCES['foreach-aggregate-generator-method-break'],
        'stage': ('S.TODO = (FOREACH_AGGREGATE pforeachaggregate "getIterator") :: '
                  'ptask_tail* -- if S.RESULT = KNOWN (POBJECT n_generator) '
                  '-- if S.OBJECTS[n_generator] = GENERATOR pgenerator '
                  '-- if pgenerator.FRAME = (pframe_generator) '
                  '-- if pframe_generator.CONTEXT = (pcallcontext_owned)'),
        'checks': [
            'pcallcontext_owned.TARGET = FOREACH_AGGREGATE_GENERATOR_TARGET '
            'n_original porigin_get porigin z',
            '$foreach_aggregate_generator_context(S, pcallcontext_owned)', *ADMISSION,
            'pcallcontext_bad = pcallcontext_owned[.LINE = $(z + 1)][.TARGET = '
            'FOREACH_AGGREGATE_GENERATOR_TARGET n_original porigin_get porigin $(z + 1)]',
            'pframe_bad = pframe_generator[.CONTEXT = (pcallcontext_bad)]',
            'S_bad = S[.OBJECTS[n_generator] = GENERATOR pgenerator[.FRAME = (pframe_bad)]]',
            '$heap_graph(S_bad) = $heap_graph(S)',
            '~$foreach_aggregate_generator_context(S_bad, pcallcontext_bad)',
            '~$generator_frame_valid(S_bad, pgenerator[.FRAME = (pframe_bad)], pframe_bad)',
            '~$call_descriptors_valid(S_bad)',
        ],
    },
    'foreach-main-break-releases-generator-at-user-statement-boundary': {
        'source': SOURCES['foreach-aggregate-generator-method-break'],
        'stage': ('S.TODO = (STMT (NStmtBreak ABSENT metadata)) :: '
                  '(ORIGIN_RETURN (porigin_foreach)) :: '
                  '(GENERATOR_NEXT pgeneratorop) :: ptask_tail* '
                  '-- if S.CURRENT = eps -- if S.FRAMES = eps'),
        'checks': [
            'n_generator = pgeneratorop.OBJECT', 'pgeneratorop.SITE = porigin_foreach',
            'pgeneratorop.LINE = 10', 'pgeneratorop.LOOP = (pgeneratorloop)',
            'n_cursor = pgeneratorloop.ITERATOR',
            'S.OBJECTS[n_generator] = GENERATOR pgenerator',
            'pgenerator.PHASE = GENERATOR_PAUSED', 'pgenerator.FRAME = (pframe_generator)',
            'pframe_generator.CONTEXT = (pcallcontext_owned)',
            'pcallcontext_owned.TARGET = FOREACH_AGGREGATE_GENERATOR_TARGET '
            'n_original porigin_get porigin_foreach 10',
            '$heap_owners($heap_graph(S), HOBJECT n_generator) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_original) = 1',
            '$heap_count(HOBJECT n_original, $tasks_nodes(S.TODO)) = 0',
            *ADMISSION, *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_generator)]',
            'pdestructionrelease.USER', 'pdestructionrelease.ORIGIN = (porigin_foreach)',
            'pdestructionoperation.SOURCE = STMT (NStmtBreak ABSENT metadata)',
            'pdestructionoperation.COMPLETION = NORMAL',
            'S_one.ORIGIN = (porigin_foreach)',
            '$eager_source_origin(S_one, S_one.ORIGIN)',
            '~$eager_source_origin(S_one, (porigin_get))',
            '$destructor_operation_valid(S_one, pdestructionoperation)',
            '$iterator_lookup(S_one.ITERATORS, n_cursor) = eps',
            '$heap_count(HOBJECT n_original, $node_children(S_one, HOBJECT n_generator)) = 1',
            '$destructor_release_valid(S_one, pdestructionrelease)', *POST,
        ],
    },
    'foreach-parked-generator-close-keeps-real-receipt-and-receiver-owner': {
        'source': SOURCES['foreach-aggregate-generator-finally-parks'], 'stage': CLOSE_PARK,
        'checks': [
            *CLOSE_VIEW, 'z = 15',
            'pcallcontext_close.CALLSITE = (porigin_foreach)',
            'pcallcontext_close.LINE = z', 'pgenclose.FRAME = eps',
            'pgenerator.FRAME = eps', 'pgenclose.PENDING = eps',
            '$generator_close_saved(S_view, S_view.CURRENT, S_view.FRAMES) = (pgenclose)',
            '$foreach_aggregate_generator_context(S_view, pcallcontext_close)',
            '$fiber_generator_transfer(S_view)',
            '$generator_resume_ids(pfibervm.TODO) = eps',
            '$generator_saved_ids(pfibervm.FRAMES) = [pgenclose.OBJECT]',
            '$generator_saved_fiber_ids(S) = [pgenclose.OBJECT]',
            '$generator_saved_fiber_ids(S_view) = eps',
            '$generator_owners_valid(S)', '$generator_owners_valid(S_view)',
            '$heap_owners($heap_graph(S), HOBJECT pgenclose.OBJECT) = 1',
            '$heap_count(HOBJECT n_original, $call_context_roots(pfibervm.CURRENT)) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_original) = 1',
            '~(n_original <- S.DESTRUCTION.CALLED)',
            '$fiber_vm_valid(S, pfibervm, (n_parent), eps)', *ADMISSION,
        ],
    },
    'foreach-parked-generator-close-rejects-shifted-receipt': {
        'source': SOURCES['foreach-aggregate-generator-finally-parks'], 'stage': CLOSE_PARK,
        'checks': [
            *CLOSE_VIEW, *ADMISSION,
            'pcallcontext_bad = pcallcontext_close[.LINE = $(z + 1)][.TARGET = '
            'FOREACH_AGGREGATE_GENERATOR_TARGET n_original porigin_get porigin_foreach $(z + 1)]',
            'pframe_bad = pframe_close[.TODO = '
            '(GENERATOR_CLOSE_DONE pgenclose[.CONTEXT = pcallcontext_bad]) :: ptask_saved*]',
            'pfibervm_bad = pfibervm[.CURRENT = (pcallcontext_bad)]'
            '[.FRAMES = [pframe_bad, pframe_base]]',
            'S_bad = S[.OBJECTS[n_parent] = FIBER pfiber_parent[.VM = (pfibervm_bad)]]',
            '$heap_graph(S_bad) = $heap_graph(S)',
            'S_view_bad = $fiber_vm_restore(S_bad, pfibervm_bad)[.ACTIVEFIBER = (n_parent)]'
            '[.FIBERCALLERS = eps][.COMPLETION = NORMAL]',
            '~$foreach_aggregate_generator_context(S_view_bad, pcallcontext_bad)',
            '~$fiber_generator_transfer(S_view_bad)',
            '~$fiber_vm_valid(S_bad, pfibervm_bad, (n_parent), eps)',
            '~$call_descriptors_valid(S_bad)',
        ],
    },
    'foreach-parked-generator-close-rejects-duplicate-real-claim': {
        'source': SOURCES['foreach-aggregate-generator-finally-parks'], 'stage': CLOSE_PARK,
        'checks': [
            *CLOSE_VIEW, *ADMISSION,
            '$generator_saved_fiber_ids(S) = [pgenclose.OBJECT]',
            '$heap_owners($heap_graph(S), HOBJECT pgenclose.OBJECT) = 1',
            'pframe_bad = pframe_close[.TODO = (GENERATOR_CLOSE_DONE pgenclose) :: '
            '(GENERATOR_CLOSE_DONE pgenclose) :: ptask_saved*]',
            'pfibervm_bad = pfibervm[.FRAMES = [pframe_bad, pframe_base]]',
            'S_bad = S[.OBJECTS[n_parent] = FIBER pfiber_parent[.VM = (pfibervm_bad)]]',
            '$heap_valid($heap_graph(S_bad))',
            '$heap_owners($heap_graph(S_bad), HOBJECT pgenclose.OBJECT) = 2',
            '$heap_owners($heap_graph(S_bad), HOBJECT n_original) = 1',
            'S_view_bad = $fiber_vm_restore(S_bad, pfibervm_bad)[.ACTIVEFIBER = (n_parent)]'
            '[.FIBERCALLERS = eps][.COMPLETION = NORMAL]',
            '$generator_saved_ids(S_view_bad.FRAMES) = '
            '[pgenclose.OBJECT, pgenclose.OBJECT]',
            '~$fiber_generator_transfer(S_view_bad)',
            '~$fiber_vm_valid(S_bad, pfibervm_bad, (n_parent), eps)',
            '~$generator_owners_valid(S_bad)', '~$call_descriptors_valid(S_bad)',
        ],
    },
    'foreach-parked-getter-keeps-real-raw-owner-and-borrowed-frame': {
        'source': SOURCES['foreach-aggregate-deep-getter-parks'], 'stage': PARK,
        'checks': [
            *HEADER, 'pforeachaggregate.LINE = 26',
            'pforeachaggregate.ACQUIRED = [n_inner]', 'pforeachaggregate.OBJECT = n_inner',
            'pforeachaggregate.INPUT = KNOWN (POBJECT n_original)',
            'pforeachaggregate.ITERATOR = eps', *PARK_VIEW,
            'pcallcontext_get.TARGET = AGGREGATE_METHOD_TARGET n_inner porigin_get',
            'pcallcontext_get.LINE = 26',
            '$call_context_roots(pfibervm.CURRENT) = eps',
            '$task_nodes(FOREACH_AGGREGATE pforeachaggregate "getIterator") = '
            '[HOBJECT n_inner, HOBJECT n_original]',
            '$heap_owners($heap_graph(S), HOBJECT n_inner) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_original) = 1',
            '$foreach_aggregate_result_valid(S_scope, pforeachaggregate, "getIterator")',
            '$fiber_vm_valid(S, pfibervm, (n_parent), eps)', *ADMISSION,
        ],
    },
    'foreach-parked-getter-rejects-shifted-real-frame-line': {
        'source': SOURCES['foreach-aggregate-deep-getter-parks'], 'stage': PARK,
        'checks': [
            *PARK_VIEW, *ADMISSION,
            'pforeachaggregate_bad = pforeachaggregate[.LINE = $(pforeachaggregate.LINE + 1)]',
            'pframe_bad = pframe_foreach[.TODO = '
            '(FOREACH_AGGREGATE pforeachaggregate_bad "getIterator") :: ptask_foreach*]',
            'pfibervm_bad = pfibervm[.FRAMES = [pframe_bad, pframe_base]]',
            'S_bad = S[.OBJECTS[n_parent] = FIBER pfiber_parent[.VM = (pfibervm_bad)]]',
            '$heap_graph(S_bad) = $heap_graph(S)',
            'S_scope_bad = S_scope[.TODO = pframe_bad.TODO]',
            '~$foreach_aggregate_result_valid(S_scope_bad, pforeachaggregate_bad, "getIterator")',
            '~$fiber_vm_valid(S_bad, pfibervm_bad, (n_parent), eps)',
            '~$call_descriptors_valid(S_bad)',
        ],
    },
    'foreach-parked-getter-zero-budget-preserves-saved-owners': {
        'source': SOURCES['foreach-aggregate-deep-getter-parks'], 'stage': PARK,
        'checks': [*ADMISSION, *ZERO],
    },
    'foreach-parked-getter-rejects-duplicate-real-continuation': {
        'source': SOURCES['foreach-aggregate-deep-getter-parks'], 'stage': PARK,
        'checks': [
            *PARK_VIEW, *ADMISSION,
            'pforeachaggregate.ACQUIRED = [n_inner]',
            'pforeachaggregate.INPUT = KNOWN (POBJECT n_original)',
            'pframe_duplicate = pframe_foreach[.TODO = '
            '(FOREACH_AGGREGATE pforeachaggregate "getIterator") :: '
            '(FOREACH_AGGREGATE pforeachaggregate "getIterator") :: ptask_foreach*]',
            'pfibervm_duplicate = pfibervm[.FRAMES = [pframe_duplicate, pframe_base]]',
            'S_duplicate = S[.OBJECTS[n_parent] = FIBER '
            'pfiber_parent[.VM = (pfibervm_duplicate)]]',
            '$foreach_aggregate_count(pframe_duplicate.TODO, pforeachaggregate.SITE) = 2',
            'S_scope_duplicate = S_scope[.TODO = pframe_duplicate.TODO]',
            '~$foreach_aggregate_result_valid(S_scope_duplicate, pforeachaggregate, "getIterator")',
            '$heap_valid($heap_graph(S_duplicate))',
            '$heap_owners($heap_graph(S_duplicate), HOBJECT n_inner) = '
            '$($heap_owners($heap_graph(S), HOBJECT n_inner) + 1)',
            '$heap_owners($heap_graph(S_duplicate), HOBJECT n_original) = '
            '$($heap_owners($heap_graph(S), HOBJECT n_original) + 1)',
            '~$fiber_vm_valid(S_duplicate, pfibervm_duplicate, (n_parent), eps)',
            '~$call_descriptors_valid(S_duplicate)',
        ],
    },
    'foreach-original-reference-operand-keeps-raw-cell-owner': {
        'source': SOURCES['foreach-aggregate-reference-original-operand'],
        'stage': ('S.TODO = (CALL_ARGS pcalltarget eps 0 eps (porigin) z) :: '
                  '(FOREACH_AGGREGATE pforeachaggregate "getIterator") :: ptask_tail*'),
        'checks': [
            *HEADER, 'z = 19', 'pforeachaggregate.INPUT = REFERENCE n_input',
            'S.STORE[n_input] = DEFINED (POBJECT n_original)',
            'pcalltarget = AGGREGATE_METHOD_TARGET n_original porigin_get',
            '$target_nodes(pcalltarget) = eps',
            '$task_nodes(FOREACH_AGGREGATE pforeachaggregate "getIterator") = [HCELL n_input]',
            '$heap_count(HCELL n_input, $tasks_nodes(S.TODO)) = 1',
            '$heap_count(HOBJECT n_original, $tasks_nodes(S.TODO)) = 0',
            '$foreach_aggregate_input_stable(S, pforeachaggregate)', *ADMISSION, *ONE,
            'S_one.CURRENT = (pcallcontext_get)',
            '$heap_count(HOBJECT n_original, $call_context_roots(S_one.CURRENT)) = 0', *POST,
        ],
    },
    'foreach-byref-generator-cv-remains-borrowed-before-acquisition': {
        'source': SOURCES['foreach-aggregate-by-reference-generator'],
        'stage': ('S.TODO = (CALL_ARGS pcalltarget eps 0 eps (porigin) z) :: '
                  '(FOREACH_AGGREGATE pforeachaggregate "getIterator") :: ptask_tail*'),
        'checks': [
            *HEADER, 'z = 13', '$foreach_aggregate_reference(pforeachaggregate.STATEMENT)',
            'pforeachaggregate.INPUT = VARIABLE ($ptascii("aggregate")) 13',
            '$lookup(S.ENV, $ptascii("aggregate")) = (n_cell)',
            'S.STORE[n_cell] = DEFINED (POBJECT n_original)', '~(n_cell <- S.REFCELLS)',
            '$task_nodes(FOREACH_AGGREGATE pforeachaggregate "getIterator") = eps',
            '$heap_owners($heap_graph(S), HOBJECT n_original) = 1',
            '$foreach_aggregate_input_stable(S, pforeachaggregate)', *ADMISSION, *ONE,
            'S_one.CURRENT = (pcallcontext_get)',
            '$heap_count(HOBJECT n_original, $call_context_roots(S_one.CURRENT)) = 0', *POST,
        ],
    },
    'foreach-raw-reference-getter-result-is-rejected-and-owned-until-unwind': {
        'source': SOURCES['foreach-aggregate-raw-reference-return-rejected'],
        'stage': ('S.TODO = (FOREACH_AGGREGATE pforeachaggregate "getIterator") :: '
                  'ptask_tail* -- if S.RESULT = REFERENCE n_return'),
        'checks': [
            *HEADER, 'pforeachaggregate.INPUT = KNOWN (POBJECT n_original)',
            'S.STORE[n_return] = DEFINED (POBJECT n_data)', '$useriter_instance(S, n_data)',
            '$task_nodes(FOREACH_AGGREGATE pforeachaggregate "getIterator") = [HOBJECT n_original]',
            *ADMISSION, *ONE,
            'S_one.TODO = (THROW_SEARCH n_error) :: '
            '(FOREACH_AGGREGATE pforeachaggregate_error "getIterator-error") :: ptask_tail*',
            'pforeachaggregate_error = pforeachaggregate[.CURRENT = REFERENCE n_return]',
            '$task_nodes(FOREACH_AGGREGATE pforeachaggregate_error "getIterator-error") = '
            '[HCELL n_return, HOBJECT n_original]',
            '$foreach_aggregate_result_valid(S_one, pforeachaggregate_error, "getIterator-error")',
            '$heap_count(HOBJECT n_data, $tasks_nodes(S_one.TODO)) = 0', *POST,
        ],
    },
    'foreach-pending-layer-error-prevents-generator-startup': {
        'source': SOURCES['foreach-aggregate-layer-destructor-throws-generator'],
        'stage': ('S.TODO = (FOREACH_AGGREGATE pforeachaggregate "acquired-error") :: '
                  'ptask_tail* -- if pforeachaggregate.CURRENT = KNOWN (POBJECT n_error)'),
        'checks': [
            *HEADER, 'n_generator = pforeachaggregate.OBJECT',
            'pforeachaggregate.INPUT = KNOWN (POBJECT n_original)',
            'pforeachaggregate.ITERATOR = eps', 'pforeachaggregate.ACQUIRED = eps',
            'S.OBJECTS[n_generator] = GENERATOR pgenerator',
            'pgenerator.PHASE = GENERATOR_FRESH', 'pgenerator.FRAME = (pframe_generator)',
            'S.EVENTS = [OUTPUT $ptascii("O|"), OUTPUT $ptascii("M|"), '
            'OUTPUT $ptascii("N|"), OUTPUT $ptascii("n|"), OUTPUT $ptascii("m|")]',
            '$task_nodes(FOREACH_AGGREGATE pforeachaggregate "acquired-error") = '
            '[HOBJECT n_error, HOBJECT n_generator, HOBJECT n_original]',
            *ADMISSION, *ONE,
            'S_one.TODO = (THROW_SEARCH n_error) :: '
            '(FOREACH_AGGREGATE pforeachaggregate_clean "acquired") :: ptask_tail*',
            'pforeachaggregate_clean = pforeachaggregate[.CURRENT = KNOWN PNULL]',
            'S_one.OBJECTS[n_generator] = GENERATOR pgenerator',
            'S_one.ITERATORS = S.ITERATORS', *POST,
            'S_done = $drive(S_one, 4000)', *review.DONE,
            'S_done.EVENTS = [OUTPUT $ptascii("O|"), OUTPUT $ptascii("M|"), '
            'OUTPUT $ptascii("N|"), OUTPUT $ptascii("n|"), OUTPUT $ptascii("m|"), '
            'OUTPUT $ptascii("A|"), OUTPUT $ptascii("1"), OUTPUT $ptascii("|")]',
        ],
    },
    'foreach-pending-layer-hook-rejects-foreign-release-snapshot': {
        'source': SOURCES['foreach-aggregate-layer-destructor-throws-generator'],
        'stage': LAYER_THROW,
        'checks': [
            'S.DESTRUCTION.CALLS = pdestructorcall :: pdestructorcall_tail*',
            'pdestructorcall.RELEASE = (pdestructionrelease_before)',
            '$destructor_result_valid(S, pdestructorcall)', *ADMISSION,
            'S_clean = S[.TODO = (THROW_SEARCH n_error) :: '
            '(DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(FOREACH_AGGREGATE pforeachaggregate "acquired") :: ptask_tail*]'
            '[.DESTRUCTION.CALLS = pdestructorcall_tail*]',
            'S_resume = $destructor_resume_pending(S_clean, pdestructorcall)',
            'S_resume.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(FOREACH_AGGREGATE pforeachaggregate_error "acquired-error") :: ptask_tail*',
            'pforeachaggregate_error = pforeachaggregate[.CURRENT = KNOWN (POBJECT n_error)]',
            'pdestructorcall_bad = pdestructorcall[.RELEASE = '
            '(pdestructionrelease_before[.ORIGIN = eps])]',
            'S_bad = S[.TODO = (THROW_SEARCH n_error) :: '
            '(DESTRUCTOR_RESULT pdestructorcall_bad) :: '
            '(DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(FOREACH_AGGREGATE pforeachaggregate "acquired") :: ptask_tail*]'
            '[.DESTRUCTION.CALLS = pdestructorcall_bad :: pdestructorcall_tail*]',
            '$heap_graph(S_bad) = $heap_graph(S)',
            '~$destructor_result_valid(S_bad, pdestructorcall_bad)',
            '~$call_descriptors_valid(S_bad)',
            '$destructor_resume_pending(S_clean, pdestructorcall_bad) = S_clean',
        ],
    },
    'foreach-initial-generator-body-has-one-data-owner-in-real-operation': {
        'source': SOURCES['foreach-aggregate-plain-generator'],
        'stage': ('S.TODO = (GENERATOR_YIELD_STORE porigin_yield poperand_key?) :: '
                  'ptask_body* -- if S.RESULT = KNOWN (PINT 7) '
                  '-- if S.FRAMES = [pframe_resumer] -- if pframe_resumer.TODO = '
                  '(GENERATOR_RESUME pgeneratorop) :: '
                  '(FOREACH_AGGREGATE pforeachaggregate "generator") :: ptask_tail*'),
        'checks': [
            *HEADER, 'n_generator = pforeachaggregate.OBJECT',
            'pforeachaggregate.INPUT = KNOWN (POBJECT n_original)',
            'pforeachaggregate.ITERATOR = (n_cursor)',
            'pgeneratorop.OBJECT = n_generator', 'pgeneratorop.NAME = "rewind"',
            '~pgeneratorop.STARTPACK',
            'pgeneratorop.LOOP = ({ITERATOR n_cursor, STATEMENT pforeachaggregate.STATEMENT})',
            'S.OBJECTS[n_generator] = GENERATOR pgenerator',
            'pgenerator.PHASE = GENERATOR_RUNNING',
            '$task_nodes(FOREACH_AGGREGATE pforeachaggregate "generator") = [HOBJECT n_original]',
            '$heap_count(HOBJECT n_generator, $task_nodes(GENERATOR_RESUME pgeneratorop)) = 1',
            '$heap_count(HOBJECT n_generator, $frames_roots(S.FRAMES)) = 1',
            '$heap_count(HOBJECT n_original, $frames_roots(S.FRAMES)) = 1',
            'S.EVENTS = [OUTPUT $ptascii("G|"), OUTPUT $ptascii("Y|")]', *ADMISSION,
        ],
    },
    'foreach-generator-startup-throw-transfers-data-and-retires-cursor': {
        'source': SOURCES['foreach-aggregate-generator-body-throws'],
        'stage': ('S.TODO = (THROW_SEARCH n_error) :: (GENERATOR_RESUME pgeneratorop) :: '
                  '(FOREACH_AGGREGATE pforeachaggregate "generator") :: ptask_tail*'),
        'checks': [
            *HEADER, 'n_generator = pforeachaggregate.OBJECT',
            'pforeachaggregate.INPUT = KNOWN (POBJECT n_original)',
            'pforeachaggregate.ITERATOR = (n_cursor)',
            '$iterator_lookup(S.ITERATORS, n_cursor) = (GENERATORITER n_cursor n_generator)',
            'S.OBJECTS[n_generator] = GENERATOR pgenerator',
            'pgenerator.PHASE = GENERATOR_CLOSED',
            '$task_nodes(FOREACH_AGGREGATE pforeachaggregate "generator") = [HOBJECT n_original]',
            '$heap_count(HOBJECT n_generator, $tasks_nodes(S.TODO)) = 1',
            '$foreach_aggregate_result_valid(S, pforeachaggregate, "generator")', *ADMISSION, *ONE,
            'S_one.TODO = (THROW_SEARCH n_error) :: '
            '(FOREACH_AGGREGATE pforeachaggregate_acquired "acquired") :: ptask_tail*',
            'pforeachaggregate_acquired = pforeachaggregate[.ITERATOR = eps]',
            '$iterator_lookup(S_one.ITERATORS, n_cursor) = eps',
            '$task_nodes(FOREACH_AGGREGATE pforeachaggregate_acquired "acquired") = '
            '[HOBJECT n_generator, HOBJECT n_original]',
            '$heap_count(HOBJECT n_generator, $tasks_nodes(S_one.TODO)) = 1', *POST,
        ],
    },
    'foreach-input-destructor-throw-keeps-data-before-body': {
        'source': SOURCES['foreach-aggregate-input-destructor-throws'],
        'stage': ('S.TODO = (THROW_SEARCH n_error) :: (DESTRUCTOR_RESULT pdestructorcall) :: '
                  '(DESTRUCTOR_RELEASE pdestructionrelease) :: '
                  '(FOREACH_AGGREGATE pforeachaggregate "current") :: ptask_tail* '
                  '-- if S.CURRENT = eps'),
        'checks': [
            *HEADER, 'pdestructorcall.OBJECT = n_original',
            'pforeachaggregate.INPUT = KNOWN PNULL', 'n_data = pforeachaggregate.OBJECT',
            '$useriter_instance(S, n_data)',
            '$task_nodes(FOREACH_AGGREGATE pforeachaggregate "current") = [HOBJECT n_data]',
            '$destructor_result_valid(S, pdestructorcall)',
            '~(n_data <- S.DESTRUCTION.CALLED)',
            '$lookup(S.ENV, $ptascii("failure")) = (n_failure)',
            'S.STORE[n_failure] = DEFINED (POBJECT n_error)',
            'S.EVENTS = [OUTPUT $ptascii("G|"), OUTPUT $ptascii("W|"), '
            'OUTPUT $ptascii("V|"), OUTPUT $ptascii("A|")]', *ADMISSION,
        ],
    },
}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=CASES)
    args = parser.parse_args()
    review.ROOT = ROOT
    review.CASES = CASES
    passed = review.run(args.case)
    assert INPUT_BYTES == {path: path.read_bytes() for path in INPUT_BYTES}
    raise SystemExit(0 if passed else 1)
