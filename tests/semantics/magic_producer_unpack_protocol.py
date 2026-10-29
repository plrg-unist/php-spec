#!/usr/bin/env python3
"""Reached array/Generator magic send, ownership and retired-caller checks."""
import argparse
import json
from pathlib import Path
import fiber_state_review as review
import magic_iterator_unpack_protocol as iterator


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
VALID = ['$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
ONE = ['S_zero = $drive_steps(S, 0)', 'S_zero.COMPLETION = BUDGET',
       'S_zero.TODO = S.TODO', 'S_one_budget = $drive_steps(S, 1)',
       'S_one_budget.COMPLETION = BUDGET',
       '$drive_steps(S_zero[.COMPLETION = NORMAL], 1) = S_one_budget',
       'S_one = S_one_budget[.COMPLETION = NORMAL]']
POST = ['$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))']


def source(name):
    return (HERE / ('magic_producer_unpack_' + name + '.php')).read_text()


CASES = {
    'array-reference-leaf-copies-without-separation': {
        'source': source('array_copy_named'),
        'stage': 'S.TODO = (UNPACK_NEXT punpackcall poperand 0 false) :: ptask_tail* '
                 '-- if punpackcall.FUNCTION = MAGIC_METHOD_SEND_TARGET pmagicmethodcall '
                 '-- if punpackcall.INDEX = 0',
        'checks': [
            'poperand = KNOWN (PARRAY n_array)',
            'S.ARRAYS[n_array].ITEMS = [ENTRY (KSTRING ($ptascii("arguments"))) (ALIAS n_value)]',
            '$lookup(S.ENV, $ptascii("value")) = (n_value)',
            '$lookup(S.ENV, $ptascii("alias")) = (n_value)',
            'n_value <- S.REFCELLS', 'S.STORE[n_value] = DEFINED (PINT 7)',
            '$heap_owners($heap_graph(S), HARRAY n_array) = 3',
            '$heap_owners($heap_graph(S), HCELL n_value) = 3',
            '$target_function(S, punpackcall.FUNCTION) = eps',
            '$unpack_send_target(S, punpackcall.FUNCTION, KSTRING ($ptascii("arguments")), 0) = NAMED_EXTRA ($ptascii("arguments"))',
            '~$unpack_send_reference(S, punpackcall.FUNCTION, NAMED_EXTRA ($ptascii("arguments")))',
            '$unpack_next_valid(S, punpackcall, poperand, 0, false)',
            '~$unpack_next_valid(S, punpackcall, poperand, 0, true)',
            '~$unpack_next_valid(S, punpackcall, poperand, 2, true)',
            *VALID, *ONE,
            'S_one.TODO = (UNPACK_NEXT punpackcall_sent poperand 1 true) :: ptask_tail*',
            'punpackcall_sent.SENT.SLOTS = eps',
            'punpackcall_sent.SENT.NAMED = [($ptascii("arguments"), KNOWN (PINT 7))]',
            'S_one.ARRAYS = S.ARRAYS', 'S_one.STORE = S.STORE',
            '$unpack_next_valid(S_one, punpackcall_sent, poperand, 1, true)',
            '~$unpack_next_valid(S_one, punpackcall_sent[.SENT = {SLOTS eps, NAMED eps}], poperand, 1, true)',
            *POST,
        ],
    },
    'returned-reference-retains-its-container-owner': {
        'source': source('array_reference_input'),
        'stage': 'S.TODO = (UNPACK_NEXT punpackcall (REFERENCE n_input) 0 false) :: ptask_tail* '
                 '-- if punpackcall.FUNCTION = MAGIC_METHOD_SEND_TARGET pmagicmethodcall '
                 '-- if punpackcall.INDEX = 0',
        'checks': [
            '$lookup(S.ENV, $ptascii("pack")) = (n_input)',
            'n_input <- S.REFCELLS', 'S.STORE[n_input] = DEFINED (PARRAY n_array)',
            '$unpack_array(S, REFERENCE n_input) = n_array',
            '$unpack_writable(S, punpackcall)',
            '$heap_count(HCELL n_input, $task_nodes(UNPACK_NEXT punpackcall (REFERENCE n_input) 0 false)) = 1',
            '$heap_count(HARRAY n_array, $task_nodes(UNPACK_NEXT punpackcall (REFERENCE n_input) 0 false)) = 0',
            '$unpack_send_target(S, punpackcall.FUNCTION, KINT 0, 0) = NAMED_POSITION 0',
            '~$unpack_send_reference(S, punpackcall.FUNCTION, NAMED_POSITION 0)',
            '$unpack_next_valid(S, punpackcall, REFERENCE n_input, 0, false)',
            '~$unpack_next_valid(S, punpackcall[.CALLSITE = eps], REFERENCE n_input, 0, false)',
            *VALID, *ONE,
            'S_one.TODO = (UNPACK_NEXT punpackcall_sent (REFERENCE n_input) 1 false) :: ptask_tail*',
            'punpackcall_sent.SENT.SLOTS = [NAMED_SENT (KNOWN (PINT 7))]',
            'punpackcall_sent.SENT.NAMED = eps',
            'S_one.ARRAYS = S.ARRAYS', 'S_one.STORE = S.STORE',
            *POST,
        ],
    },
    'generator-reference-cache-sends-a-value': {
        'source': source('generator_copy_named'),
        'stage': 'S.TODO = (GENERATOR_UNPACK pgeneratorunpack "ready") :: ptask_tail* '
                 '-- if pgeneratorunpack.CALL.FUNCTION = MAGIC_METHOD_SEND_TARGET pmagicmethodcall '
                 '-- if pgeneratorunpack.COUNT = 0',
        'checks': [
            'S.OBJECTS[pgeneratorunpack.OBJECT] = GENERATOR pgenerator',
            'pgenerator.PHASE = GENERATOR_PAUSED',
            'pgenerator.REFCELL = (n_value)', 'pgenerator.VALUE = eps',
            '$lookup(S.ENV, $ptascii("value")) = (n_value)',
            'n_value <- S.REFCELLS', 'S.STORE[n_value] = DEFINED (PINT 7)',
            '$generator_cached_value(S, pgeneratorunpack.OBJECT, false) = PINT 7',
            '$fiber_traversal_key($generator_cached_value(S, pgeneratorunpack.OBJECT, true)) = (KSTRING ($ptascii("arguments")))',
            '$target_function(S, pgeneratorunpack.CALL.FUNCTION) = eps',
            '$unpack_send_target(S, pgeneratorunpack.CALL.FUNCTION, KSTRING ($ptascii("arguments")), 0) = NAMED_EXTRA ($ptascii("arguments"))',
            '~$unpack_send_reference(S, pgeneratorunpack.CALL.FUNCTION, NAMED_EXTRA ($ptascii("arguments")))',
            '$generator_unpack_valid(S, pgeneratorunpack, "ready")',
            '~$generator_unpack_valid(S, pgeneratorunpack[.COUNT = 1], "ready")',
            '~$generator_unpack_valid(S, pgeneratorunpack[.CALL = pgeneratorunpack.CALL[.LINE = 0]], "ready")',
            *VALID, *ONE,
            'S_one.TODO = (GENERATOR_UNPACK pgeneratorunpack_sent "next") :: ptask_tail*',
            'pgeneratorunpack_sent.COUNT = 1', 'pgeneratorunpack_sent.NAMED',
            'pgeneratorunpack_sent.CALL.SENT.SLOTS = eps',
            'pgeneratorunpack_sent.CALL.SENT.NAMED = [($ptascii("arguments"), KNOWN (PINT 7))]',
            'S_one.OBJECTS[pgeneratorunpack.OBJECT] = GENERATOR pgenerator',
            '$generator_unpack_valid(S_one, pgeneratorunpack_sent, "next")',
            *POST,
        ],
    },
    'mixed-producers-share-one-final-send-sequence': {
        'source': source('mixed_static'),
        'stage': 'S.TODO = (UNPACK_ARGS punpackcall) :: ptask_tail* '
                 '-- if punpackcall.FUNCTION = MAGIC_STATIC_METHOD_SEND_TARGET pmagicstaticmethodcall '
                 '-- if punpackcall.ARGUMENTS = eps',
        'checks': [
            'punpackcall.INDEX = 4',
            'punpackcall.SENT.SLOTS = [NAMED_SENT (KNOWN (PINT 7)), NAMED_SENT (KNOWN (PINT 8)), NAMED_SENT (KNOWN (PINT 10))]',
            'punpackcall.SENT.NAMED = [($ptascii("arguments"), KNOWN (PINT 9))]',
            '$target_function(S, punpackcall.FUNCTION) = eps',
            '$unpack_before_valid(S, punpackcall, 0)',
            '~$magic_unpack_sends(S, punpackcall.FUNCTION, punpackcall.SENT[.SLOTS = [NAMED_HOLE]])',
            '~$magic_unpack_sends(S, punpackcall.FUNCTION, punpackcall.SENT[.NAMED = punpackcall.SENT.NAMED ++ punpackcall.SENT.NAMED])',
            *VALID, *ONE,
            'S_one.TODO = (CALL_ARGS pcalltarget_final eps 2 poperand_pair* porigin_site? z) :: (MAGIC_UNPACK_RESULT pcalltarget_final) :: ptask_tail*',
            'pcalltarget_final = MAGIC_UNPACK_TARGET punpackcall.FUNCTION n_arguments (n_named) punpackcall.SENT',
            'n_arguments = $(n_named + 1)',
            'S_one.ARRAYS[n_arguments].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 7)), ENTRY (KINT 1) (DIRECT (PINT 8)), ENTRY (KINT 2) (DIRECT (PINT 10)), ENTRY (KSTRING ($ptascii("arguments"))) (DIRECT (PINT 9))]',
            'S_one.ARRAYS[n_named].ITEMS = [ENTRY (KSTRING ($ptascii("arguments"))) (DIRECT (PINT 9))]',
            '$heap_owners($heap_graph(S_one), HARRAY n_arguments) = 1',
            '$heap_owners($heap_graph(S_one), HARRAY n_named) = 1',
            '$magic_unpack_pending(S_one, pcalltarget_final)',
            *POST,
        ],
    },
    'temporary-generator-abort-authenticates-retired-selection': {
        'source': source('generator_invalid_temporary'),
        'stage': 'S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail* '
                 '-- if pdestructionoperation.SOURCE = GENERATOR_UNPACK pgeneratorunpack "ready" '
                 '-- if pgeneratorunpack.CALL.FUNCTION = MAGIC_METHOD_SEND_TARGET pmagicmethodcall '
                 '-- if ~((HOBJECT pmagicmethodcall.OBJECT) <- S.ALLOCATIONS)',
        'checks': [
            'pdestructionoperation <- S.DESTRUCTION.OPERATIONS',
            'pdestructionoperation.PENDING = (n_error)', '$throwable_live(S, n_error)',
            'pgeneratorunpack.INPUT = KNOWN (POBJECT pgeneratorunpack.OBJECT)',
            '~((HOBJECT pgeneratorunpack.OBJECT) <- S.ALLOCATIONS)',
            'S_scope = S[.CURRENT = pdestructionoperation.CALLER][.ORIGIN = pdestructionoperation.ORIGIN][.CONSTCONTEXT = pdestructionoperation.CONSTCONTEXT]',
            '$magic_unpack_caller_history(S_scope, pgeneratorunpack.CALL.FUNCTION)',
            '$iterator_unpack_abort_plain(S_scope, pgeneratorunpack.CALL)',
            '~$iterator_unpack_abort_plain(S_scope, pgeneratorunpack.CALL[.FUNCTION = MAGIC_METHOD_SEND_TARGET pmagicmethodcall[.OWNER = $(pmagicmethodcall.OWNER + 1)]])',
            '~$iterator_unpack_abort_plain(S_scope, pgeneratorunpack.CALL[.FUNCTION = MAGIC_METHOD_SEND_TARGET pmagicmethodcall[.METHOD = pmagicmethodcall.SITE]])',
            '$generator_unpack_abort_input(S_scope, pgeneratorunpack)',
            '$eager_operation_source_valid(S, pdestructionoperation)',
            '~$eager_operation_source_valid(S, pdestructionoperation[.SOURCE = GENERATOR_UNPACK pgeneratorunpack[.CALL = pgeneratorunpack.CALL[.LINE = 0]] "ready"])',
            *VALID, *ONE, *POST,
        ],
    },
    'retained-generator-abort-keeps-its-unsent-cache': {
        'source': source('generator_invalid_retained'),
        'stage': 'S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail* '
                 '-- if pdestructionoperation.SOURCE = GENERATOR_UNPACK pgeneratorunpack "ready" '
                 '-- if pgeneratorunpack.CALL.FUNCTION = MAGIC_METHOD_SEND_TARGET pmagicmethodcall '
                 '-- if ~((HOBJECT pmagicmethodcall.OBJECT) <- S.ALLOCATIONS)',
        'checks': [
            'pdestructionoperation <- S.DESTRUCTION.OPERATIONS',
            'pdestructionoperation.PENDING = (n_error)', '$throwable_live(S, n_error)',
            'pgeneratorunpack.INPUT = VARIABLE ptbytes_input z_input',
            '(HOBJECT pgeneratorunpack.OBJECT) <- S.ALLOCATIONS',
            'S.OBJECTS[pgeneratorunpack.OBJECT] = GENERATOR pgenerator',
            'pgenerator.PHASE = GENERATOR_PAUSED',
            'pgenerator.VALUE = (POBJECT n_payload)', '(HOBJECT n_payload) <- S.ALLOCATIONS',
            '$heap_owners($heap_graph(S), HOBJECT n_payload) = 1',
            '~(pgeneratorunpack.OBJECT <- S.DESTRUCTION.CALLED)',
            'S_scope = S[.CURRENT = pdestructionoperation.CALLER][.ORIGIN = pdestructionoperation.ORIGIN][.CONSTCONTEXT = pdestructionoperation.CONSTCONTEXT]',
            '$iterator_unpack_abort_plain(S_scope, pgeneratorunpack.CALL)',
            '$generator_unpack_abort_input(S_scope, pgeneratorunpack)',
            '$eager_operation_source_valid(S, pdestructionoperation)',
            *VALID, *ONE, *POST,
        ],
    },
    'empty-producers-still-pack-the-real-handler-pair': {
        'source': source('empty'),
        'stage': 'S.TODO = (UNPACK_ARGS punpackcall) :: ptask_tail* '
                 '-- if punpackcall.FUNCTION = MAGIC_METHOD_SEND_TARGET pmagicmethodcall '
                 '-- if punpackcall.ARGUMENTS = eps',
        'checks': [
            'punpackcall.INDEX = 2', 'punpackcall.SENT = {SLOTS eps, NAMED eps}',
            '$unpack_before_valid(S, punpackcall, 0)',
            *VALID, *ONE,
            'S_one.TODO = (CALL_ARGS pcalltarget_final eps 2 poperand_pair* porigin_site? z) :: (MAGIC_UNPACK_RESULT pcalltarget_final) :: ptask_tail*',
            'pcalltarget_final = MAGIC_UNPACK_TARGET punpackcall.FUNCTION n_arguments eps punpackcall.SENT',
            'S_one.ARRAYS[n_arguments] = $array_empty()',
            '$heap_owners($heap_graph(S_one), HARRAY n_arguments) = 1',
            '$magic_unpack_pending(S_one, pcalltarget_final)',
            *POST,
        ],
    },
}
CASES['generator-handler-keeps-original-named-buffer'] = {
    **iterator.CASES['handler-unset-retains-original-named-buffer'],
    'source': source('generator_handler_throw'),
}
CASES['iterator-shared-destination-control'] = iterator.CASES['copied-current-key-then-zero-formal-send']
CASES['ordinary-reference-demand-keeps-real-formals'] = {
    'source': json.loads((HERE / 'call_unpack_cases.json').read_text())['unpack-reference-cv-array-cow'],
    'stage': 'S.TODO = (UNPACK_NEXT punpackcall poperand 0 false) :: ptask_tail* '
             '-- if $target_function(S, punpackcall.FUNCTION) = (pfunction) '
             '-- if punpackcall.FUNCTION = pfunction.ORIGIN',
    'checks': [
        '~$magic_unpack_collecting(punpackcall.FUNCTION)',
        '$unpack_send_target(S, punpackcall.FUNCTION, KINT 0, 0) = NAMED_POSITION 0',
        '$unpack_send_reference(S, punpackcall.FUNCTION, NAMED_POSITION 0)',
        'poperand = KNOWN (PARRAY n_array)',
        '$lookup(S.ENV, $ptascii("a")) = (n_a)', 'S.STORE[n_a] = DEFINED (PARRAY n_array)',
        '$lookup(S.ENV, $ptascii("b")) = (n_b)', 'S.STORE[n_b] = DEFINED (PARRAY n_old)',
        'n_array =/= n_old', 'S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 1))]',
        '$heap_owners($heap_graph(S), HARRAY n_array) = 2',
        '$unpack_next_valid(S, punpackcall, poperand, 0, false)',
        *VALID, *ONE,
        'S_one.TODO = (UNPACK_NEXT punpackcall_sent poperand 1 false) :: ptask_tail*',
        'punpackcall_sent.SENT.SLOTS = [NAMED_SENT (REFERENCE n_value)]',
        'S_one.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (ALIAS n_value)]',
        'S_one.STORE[n_value] = DEFINED (PINT 1)',
        '$heap_owners($heap_graph(S_one), HCELL n_value) = 2',
        'S_one.ARRAYS[n_old] = S.ARRAYS[n_old]',
        *POST,
    ],
}
CASES['second-reference-yield-authenticates-interned-key'] = {
    'source': source('generator_copy_named'),
    'stage': 'S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail* '
             '-- if pdestructionoperation.SOURCE = GENERATOR_YIELD_DONE porigin poperand_key? '
             '-- if pdestructionoperation.VALUE = VARIABLE n_name* z '
             '-- if n_name* = $ptascii("tail")',
    'checks': [
        'pdestructionoperation <- S.DESTRUCTION.OPERATIONS',
        'pdestructionoperation.PENDING = eps',
        'poperand_key? = (KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("tail"))))',
        '$origin_child((porigin), [PCFIELD 0]) = (porigin_key)',
        '$compiled_read(S, porigin_key) = (PSTRING ($ptascii("tail")))',
        '$compiled_string_value(S, porigin_key, PSTRING ($ptascii("tail"))) = PSTRING_CARRIER INTERNED_STRING ($ptascii("tail"))',
        '$generator_reference_payload_valid(S, (porigin_key), PSTRING_CARRIER INTERNED_STRING ($ptascii("tail")))',
        '~$generator_reference_payload_valid(S, (porigin_key), PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("tail")))',
        '~$generator_reference_payload_valid(S, (porigin_key), PSTRING_CARRIER INTERNED_STRING ($ptascii("different")))',
        '$generator_yield_delayed_value_valid(S, pdestructionoperation)',
        '~$generator_yield_delayed_value_valid(S, pdestructionoperation[.VALUE = VARIABLE ($ptascii("value")) z])',
        '$eager_operation_value_valid(S, pdestructionoperation)',
        '$destructor_operation_valid(S, pdestructionoperation)',
        '$lookup(S.ENV, $ptascii("tail")) = (n_tail)',
        'S.STORE[n_tail] = DEFINED (PINT 8)',
        'ptask_tail* = (GENERATOR_YIELD_STORE porigin poperand_key?) :: ptask_after*',
        '$generator_state_valid(S)',
        *VALID, *ONE,
        'S_one.TODO = ptask_tail*',
        'S_one.RESULT = VARIABLE n_name* z',
        'S_one.STORE[n_tail] = DEFINED (PINT 8)',
        '$generator_state_valid(S_one)',
        *POST,
    ],
}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    assert not args.case or set(args.case) <= CASES.keys()
    review.ROOT = ROOT
    review.CASES = CASES
    for name in args.case or list(CASES):
        assert review.run([name])
