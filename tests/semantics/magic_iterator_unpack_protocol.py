#!/usr/bin/env python3
"""Source-reached magic trampoline sends, buffers and abrupt retirement."""
import argparse
from pathlib import Path
import fiber_state_review as review


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
    return (HERE / ('magic_iterator_unpack_' + name + '.php')).read_text()


CASES = {
    'copied-current-key-then-zero-formal-send': {
        'source': source('copy_named'),
        'stage': 'S.TODO = (ITERATOR_UNPACK piteratorunpack "send") :: ptask_tail* '
                 '-- if piteratorunpack.CALL.FUNCTION = MAGIC_METHOD_SEND_TARGET pmagicmethodcall',
        'checks': [
            'piteratorunpack.CURRENT = KNOWN (PINT 7)',
            'piteratorunpack.KEY = KNOWN pvalue_key',
            '$fiber_traversal_key(pvalue_key) = (KSTRING ($ptascii("arguments")))',
            '$lookup(S.ENV, $ptascii("value")) = (n_value)',
            'S.STORE[n_value] = DEFINED (PINT 9)',
            '$lookup(S.ENV, $ptascii("receiver")) = (n_receiver_cv)',
            'S.STORE[n_receiver_cv] = DEFINED PNULL',
            '$heap_owners($heap_graph(S), HOBJECT pmagicmethodcall.OBJECT) = 1',
            '$target_function(S, piteratorunpack.CALL.FUNCTION) = eps',
            '$iterator_unpack_named_target(S, piteratorunpack) = NAMED_EXTRA ($ptascii("arguments"))',
            '$iterator_unpack_result_valid(S, piteratorunpack, "send")',
            '~$magic_unpack_descriptor(S, MAGIC_METHOD_SEND_TARGET pmagicmethodcall[.METHOD = pmagicmethodcall.SITE])',
            '~$magic_unpack_descriptor(S, MAGIC_METHOD_SEND_TARGET pmagicmethodcall[.SITE = pmagicmethodcall.METHOD])',
            '~$unpack_pending_valid(S[.ORIGIN = piteratorunpack.CALL.CALLSITE], piteratorunpack.CALL[.INDEX = 1], 1)',
            *VALID, *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (ITERATOR_UNPACK piteratorunpack_sent "next-start") :: ptask_tail*',
            'pdestructionrelease.JOBS = eps',
            'S_release = $drive_steps(S_one, 1)',
            'S_release.COMPLETION = BUDGET',
            'S_release.TODO = (ITERATOR_UNPACK piteratorunpack_sent "next-start") :: ptask_tail*',
            '$call_descriptors_valid(S_release[.COMPLETION = NORMAL])',
            '$heap_valid($heap_graph(S_release[.COMPLETION = NORMAL]))',
            'piteratorunpack_sent.CALL.SENT.SLOTS = eps',
            'piteratorunpack_sent.CALL.SENT.NAMED = [($ptascii("arguments"), KNOWN (PINT 7))]',
            'piteratorunpack_sent.CURRENT = KNOWN PNULL',
            'piteratorunpack_sent.NAMED',
            'S_one.STORE[n_value] = DEFINED (PINT 9)',
            *POST,
        ],
    },
    'reference-prefix-is-an-earlier-snapshot': {
        'source': source('prefix_reference'),
        'stage': 'S.TODO = (ITERATOR_UNPACK piteratorunpack "send") :: ptask_tail* '
                 '-- if piteratorunpack.CALL.FUNCTION = MAGIC_METHOD_SEND_TARGET pmagicmethodcall',
        'checks': [
            'piteratorunpack.CALL.INDEX = 1',
            'piteratorunpack.CALL.SENT.SLOTS = [NAMED_SENT (KNOWN (PINT 7))]',
            'piteratorunpack.CALL.SENT.NAMED = eps',
            '$lookup(S.ENV, $ptascii("prefix")) = (n_prefix)',
            '$lookup(S.ENV, $ptascii("alias")) = (n_prefix)',
            'n_prefix <- S.REFCELLS',
            'S.STORE[n_prefix] = DEFINED (PINT 9)',
            'piteratorunpack.CURRENT = KNOWN (PINT 8)',
            '$iterator_unpack_named_target(S, piteratorunpack) = NAMED_POSITION 1',
            '~$magic_unpack_sends(S, piteratorunpack.CALL.FUNCTION, {SLOTS ([(NAMED_SENT (REFERENCE n_prefix))]), NAMED eps})',
            *VALID, *ONE,
            'S_one.TODO = (ITERATOR_UNPACK piteratorunpack_sent "next-start") :: ptask_tail*',
            'piteratorunpack_sent.CALL.SENT.SLOTS = [NAMED_SENT (KNOWN (PINT 7)), NAMED_SENT (KNOWN (PINT 8))]',
            'S_one.STORE[n_prefix] = DEFINED (PINT 9)',
            *POST,
        ],
    },
    'cross-container-positional-before-named-pack': {
        'source': source('static_cross'),
        'stage': 'S.TODO = (UNPACK_ARGS punpackcall) :: ptask_tail* '
                 '-- if punpackcall.FUNCTION = MAGIC_STATIC_METHOD_SEND_TARGET pmagicstaticmethodcall '
                 '-- if punpackcall.ARGUMENTS = eps',
        'checks': [
            'punpackcall.INDEX = 2',
            'punpackcall.SENT.SLOTS = [NAMED_SENT (KNOWN (PINT 8))]',
            'punpackcall.SENT.NAMED = [($ptascii("arguments"), KNOWN (PINT 7))]',
            '$target_function(S, punpackcall.FUNCTION) = eps',
            '$unpack_before_valid(S, punpackcall, 0)',
            '~$magic_unpack_sends(S, punpackcall.FUNCTION, punpackcall.SENT[.SLOTS = [NAMED_HOLE]])',
            '~$magic_unpack_sends(S, punpackcall.FUNCTION, punpackcall.SENT[.NAMED = punpackcall.SENT.NAMED ++ punpackcall.SENT.NAMED])',
            *VALID, *ONE,
            'S_one.TODO = (CALL_ARGS pcalltarget_final eps 2 poperand_pair* porigin_site? z) :: (MAGIC_UNPACK_RESULT pcalltarget_final) :: ptask_tail*',
            'pcalltarget_final = MAGIC_UNPACK_TARGET punpackcall.FUNCTION n_arguments (n_named) punpackcall.SENT',
            'n_arguments = $(n_named + 1)',
            'S_one.ARRAYS[n_arguments].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 8)), ENTRY (KSTRING ($ptascii("arguments"))) (DIRECT (PINT 7))]',
            'S_one.ARRAYS[n_named].ITEMS = [ENTRY (KSTRING ($ptascii("arguments"))) (DIRECT (PINT 7))]',
            '$heap_owners($heap_graph(S_one), HARRAY n_arguments) = 1',
            '$heap_owners($heap_graph(S_one), HARRAY n_named) = 1',
            '$magic_unpack_pending(S_one, pcalltarget_final)',
            '$target_function(S_one, pcalltarget_final) = (pfunction_handler)',
            'pfunction_handler.ORIGIN = pmagicstaticmethodcall.METHOD',
            *POST,
        ],
    },
    'empty-expansion-still-enters-two-formal-handler': {
        'source': source('empty'),
        'stage': 'S.TODO = (UNPACK_ARGS punpackcall) :: ptask_tail* '
                 '-- if punpackcall.FUNCTION = MAGIC_METHOD_SEND_TARGET pmagicmethodcall '
                 '-- if punpackcall.ARGUMENTS = eps',
        'checks': [
            'punpackcall.INDEX = 1',
            'punpackcall.SENT = {SLOTS eps, NAMED eps}',
            '$unpack_before_valid(S, punpackcall, 0)',
            *VALID, *ONE,
            'S_one.TODO = (CALL_ARGS pcalltarget_final eps 2 poperand_pair* porigin_site? z) :: (MAGIC_UNPACK_RESULT pcalltarget_final) :: ptask_tail*',
            'pcalltarget_final = MAGIC_UNPACK_TARGET punpackcall.FUNCTION n_arguments eps punpackcall.SENT',
            'S_one.ARRAYS[n_arguments] = $array_empty()',
            '$heap_owners($heap_graph(S_one), HARRAY n_arguments) = 1',
            '$magic_unpack_pending(S_one, pcalltarget_final)',
            '~$magic_unpack_history(S_one, MAGIC_UNPACK_TARGET punpackcall.FUNCTION n_arguments (n_arguments) punpackcall.SENT)',
            *POST,
        ],
    },
    'invalid-key-retired-selected-receiver-receipt': {
        'source': source('invalid'),
        'stage': 'S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail* '
                 '-- if pdestructionoperation.SOURCE = ITERATOR_UNPACK piteratorunpack "error" '
                 '-- if piteratorunpack.CALL.FUNCTION = MAGIC_METHOD_SEND_TARGET pmagicmethodcall '
                 '-- if ~((HOBJECT pmagicmethodcall.OBJECT) <- S.ALLOCATIONS)',
        'checks': [
            'pdestructionoperation <- S.DESTRUCTION.OPERATIONS',
            'pdestructionoperation.PENDING = (n_error)',
            '$throwable_live(S, n_error)',
            'piteratorunpack.CURRENT = KNOWN (POBJECT n_current)',
            '~((HOBJECT n_current) <- S.ALLOCATIONS)',
            '~((HOBJECT piteratorunpack.OBJECT) <- S.ALLOCATIONS)',
            'piteratorunpack.INPUT = KNOWN (POBJECT piteratorunpack.OBJECT)',
            'S_scope = S[.CURRENT = pdestructionoperation.CALLER][.ORIGIN = pdestructionoperation.ORIGIN][.CONSTCONTEXT = pdestructionoperation.CONSTCONTEXT]',
            '$iterator_unpack_abort_plain(S_scope, piteratorunpack.CALL)',
            '$iterator_unpack_abort_selected(S_scope, piteratorunpack)',
            '~$iterator_unpack_abort_plain(S_scope, piteratorunpack.CALL[.FUNCTION = MAGIC_METHOD_SEND_TARGET pmagicmethodcall[.OWNER = $(pmagicmethodcall.OWNER + 1)]])',
            '~$iterator_unpack_abort_plain(S_scope, piteratorunpack.CALL[.FUNCTION = MAGIC_METHOD_SEND_TARGET pmagicmethodcall[.METHOD = pmagicmethodcall.SITE]])',
            '~$iterator_unpack_abort_plain(S_scope, piteratorunpack.CALL[.CALLSITE = eps])',
            '$eager_operation_source_valid(S, pdestructionoperation)',
            *VALID, *ONE, *POST,
        ],
    },
    'handler-unset-retains-original-named-buffer': {
        'source': source('handler_throw'),
        'stage': 'S.CURRENT = (pcallcontext) '
                 '-- if pcallcontext.TARGET = MAGIC_UNPACK_TARGET (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) n_arguments (n_named) pnamedargs '
                 '-- if ~$named_defined(S, $ptascii("arguments")) '
                 '-- if (OUTPUT ($ptascii("U|"))) <- S.EVENTS',
        'checks': [
            'pcallcontext.ARGC = 2',
            '|pmagicmethodcall.ARGUMENTS| = 1',
            'pnamedargs.SLOTS = eps',
            'pnamedargs.NAMED = [($ptascii("arguments"), KNOWN (POBJECT n_payload))]',
            'n_arguments = n_named',
            'S.ARRAYS[n_named].ITEMS = [ENTRY (KSTRING ($ptascii("arguments"))) (DIRECT (POBJECT n_payload))]',
            '$heap_owners($heap_graph(S), HARRAY n_named) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_payload) = 1',
            '$heap_owners($heap_graph(S), HOBJECT pmagicmethodcall.OBJECT) = 1',
            '$call_receiver_roots(pcallcontext) = eps',
            '$target_nodes(pcallcontext.TARGET) = eps',
            '$magic_unpack_history(S, pcallcontext.TARGET)',
            '$magic_unpack_buffer(S, pcallcontext.TARGET)',
            '~$magic_unpack_buffer(S[.ARRAYS[n_named] = $array_empty()], pcallcontext.TARGET)',
            '~$magic_unpack_entered(S, (pcallcontext[.ARGC = 1]), S.FRAMES, pcallcontext.TARGET)',
            '$magic_unpack_entered(S, S.CURRENT, S.FRAMES, pcallcontext.TARGET)',
            *VALID, *ONE, *POST,
        ],
    },
    'normal-marker-retired-buffer-and-receiver-receipt': {
        'source': source('copy_named'),
        'stage': 'S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail* '
                 '-- if pdestructionoperation.SOURCE = MAGIC_UNPACK_RESULT pcalltarget_final '
                 '-- if pcalltarget_final = MAGIC_UNPACK_TARGET (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) n_arguments (n_named) pnamedargs '
                 '-- if ~((HOBJECT pmagicmethodcall.OBJECT) <- S.ALLOCATIONS)',
        'checks': [
            'pdestructionoperation <- S.DESTRUCTION.OPERATIONS',
            'pdestructionoperation.PENDING = eps',
            'pdestructionoperation.COMPLETION = NORMAL',
            'pnamedargs.NAMED = [($ptascii("arguments"), KNOWN (PINT 7))]',
            'n_arguments = n_named',
            '~((HARRAY n_named) <- S.ALLOCATIONS)',
            '$task_nodes(MAGIC_UNPACK_RESULT pcalltarget_final) = [HARRAY n_named, HOBJECT pmagicmethodcall.OBJECT]',
            '$magic_unpack_history(S, pcalltarget_final)',
            '~$magic_unpack_buffer(S, pcalltarget_final)',
            '$magic_unpack_retired_source(S, pdestructionoperation, pcalltarget_final)',
            '~$magic_unpack_retired_source(S, pdestructionoperation, MAGIC_UNPACK_TARGET (MAGIC_METHOD_SEND_TARGET pmagicmethodcall[.OWNER = $(pmagicmethodcall.OWNER + 1)]) n_arguments (n_named) pnamedargs)',
            '~$magic_unpack_retired_source(S, pdestructionoperation, MAGIC_UNPACK_TARGET (MAGIC_METHOD_SEND_TARGET pmagicmethodcall[.METHOD = pmagicmethodcall.SITE]) n_arguments (n_named) pnamedargs)',
            '~$magic_unpack_retired_source(S[.TODO = [DESTRUCTOR_OPERATION_EXIT pdestructionoperation]], pdestructionoperation, pcalltarget_final)',
            '$eager_operation_source_guard(S, pdestructionoperation)',
            '$eager_operation_source_valid(S, pdestructionoperation)',
            *VALID, *ONE, *POST,
        ],
    },
    'throwing-handler-retired-buffer-and-supplied-pending': {
        'source': source('handler_throw'),
        'stage': 'S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail* '
                 '-- if pdestructionoperation.SOURCE = MAGIC_UNPACK_RESULT pcalltarget_final '
                 '-- if pcalltarget_final = MAGIC_UNPACK_TARGET (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) n_arguments (n_named) pnamedargs '
                 '-- if ~((HOBJECT pmagicmethodcall.OBJECT) <- S.ALLOCATIONS)',
        'checks': [
            'pdestructionoperation <- S.DESTRUCTION.OPERATIONS',
            'pdestructionoperation.PENDING = (n_failure)',
            '$lookup(S.ENV, $ptascii("failure")) = (n_failure_cv)',
            'S.STORE[n_failure_cv] = DEFINED (POBJECT n_failure)',
            '$throwable_live(S, n_failure)',
            'pnamedargs.NAMED = [($ptascii("arguments"), KNOWN (POBJECT n_payload))]',
            '~((HARRAY n_named) <- S.ALLOCATIONS)',
            '~((HOBJECT n_payload) <- S.ALLOCATIONS)',
            '$lookup(S.ENV, $ptascii("answer")) = (n_answer)',
            'S.STORE[n_answer] = DEFINED (PINT 42)',
            '$magic_unpack_history(S, pcalltarget_final)',
            '~$magic_unpack_buffer(S, pcalltarget_final)',
            '$magic_unpack_retired_source(S, pdestructionoperation, pcalltarget_final)',
            '~$magic_unpack_retired_source(S, pdestructionoperation, MAGIC_UNPACK_TARGET (MAGIC_METHOD_SEND_TARGET pmagicmethodcall[.OWNER = $(pmagicmethodcall.OWNER + 1)]) n_arguments (n_named) pnamedargs)',
            '$eager_operation_source_valid(S, pdestructionoperation)',
            *VALID, *ONE, *POST,
        ],
    },
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
