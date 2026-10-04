#!/usr/bin/env python3
"""Called-class stopping frames, selected builtin owners and handler restoration."""
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('called_class_cases.json')
SOURCES = {row['id']: row['source'] for row in json.loads(CATALOGUE.read_text())['cases']}
VALID = ['$call_current_valid(S)', '$call_frames_valid(S, S.FRAMES)',
         '$call_descriptors_valid(S)', '$class_state_valid(S)', '$heap_valid($heap_graph(S))']
FINISH = ['S_done = $drive(S, 5000)', 'S_done.COMPLETION = NORMAL',
          'S_done.TODO = eps', 'S_done.CURRENT = eps', 'S_done.FRAMES = eps',
          '$call_descriptors_valid(S_done)', '$class_state_valid(S_done)',
          '$heap_valid($heap_graph(S_done))']
STAGE = ('S.TODO = (ARGINFO_INVOKE pargcall) :: ptask_tail* '
         '-- if pargcall.KIND = INTRINSIC_GET_CALLED_CLASS')

CASES = {
    'plain-function-stops-before-saved-method': {
        'source': SOURCES['plain-function-stops-saved-method'],
        'stage': STAGE,
        'checks': [
            'S.CURRENT = (pcallcontext)',
            'pcallcontext.CALLED_CLASS = eps',
            'pcallcontext.LEXICAL_CLASS = eps',
            'pcallcontext.RECEIVER = eps',
            'S.FRAMES = pframe :: pframe_tail*',
            'pframe.CONTEXT = (pcallcontext_caller)',
            'pcallcontext_caller.CALLED_CLASS = (porigin_child)',
            'pcallcontext_caller.LEXICAL_CLASS = (porigin_owner)',
            'porigin_child =/= porigin_owner',
            '$calledclass_name(S, pargcall) = eps',
            '$calledclass_special(S, pargcall)',
            '$call_task_valid(S, ARGINFO_INVOKE pargcall)',
            *VALID,
            '~$call_current_valid(S[.CURRENT = (pcallcontext[.CALLED_CLASS = (porigin_child)])])',
            '~$call_task_valid(S, ARGINFO_INVOKE pargcall[.KIND = INTRINSIC_FUNC_NUM_ARGS])',
            '~$call_task_valid(S, ARGINFO_INVOKE pargcall[.LINE = $(pargcall.LINE + 1)])',
            '~$call_task_valid(S, ARGINFO_INVOKE pargcall[.SITE = pcallcontext_caller.FUNCTION])',
            'PhpStep: S ~> S_one',
            'S_one.COMPLETION = THROWING n_error',
            '$throwable_field(S_one, n_error, "message") = PSTRING ($ptascii("get_called_class() must be called from within a class"))',
            '$throwable_field(S_one, n_error, "trace") = PARRAY n_trace',
            'S_one.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_plain)), ENTRY (KINT 1) (DIRECT (PARRAY n_method))]',
            '$trace_array_field(S_one, n_plain, $ptascii("function")) = PSTRING ($ptascii("plain"))',
            '$trace_array_field(S_one, n_method, $ptascii("class")) = PSTRING ($ptascii("A"))',
            '$trace_graph_valid(S_one, n_trace)',
        ],
    },
    'captured-static-closure-keeps-retired-called-class': {
        'source': SOURCES['retired-maker-static-closure'],
        'stage': STAGE,
        'checks': [
            'S.CURRENT = (pcallcontext)',
            'pcallcontext.TARGET = CLOSURE_TARGET n_closure',
            'pcallcontext.RECEIVER = eps',
            'pcallcontext.LEXICAL_CLASS = (porigin_owner)',
            'pcallcontext.CALLED_CLASS = (porigin_child)',
            'porigin_child =/= porigin_owner',
            '$class_at(S.CLASSES, porigin_child) = (pclassdesc)',
            'pclassdesc.NAME = $ptascii("B")',
            '$calledclass_name(S, pargcall) = ($ptascii("B"))',
            '$target_called_class(S, pcallcontext.TARGET) = (porigin_child)',
            '$call_task_valid(S, ARGINFO_INVOKE pargcall)',
            *VALID,
            '~$call_current_valid(S[.CURRENT = (pcallcontext[.CALLED_CLASS = (porigin_owner)])])',
            *FINISH,
        ],
    },
    'wrapper-receiver-survives-null-and-retires': {
        'source': SOURCES['builtin-fcc-wrapper-mutation'],
        'stage': STAGE + ' -- if pargcall.OWNER = (n_owner)',
        'checks': [
            'S.OBJECTS[n_owner] = INTRINSICCLOSURE INTRINSIC_GET_CALLED_CLASS',
            '(HOBJECT n_owner) <- S.ALLOCATIONS',
            'HOBJECT n_owner <- $task_nodes(ARGINFO_INVOKE pargcall)',
            '$lookup(S.ENV, $ptascii("f")) = (n_f)',
            'S.STORE[n_f] = DEFINED PNULL',
            'pargcall.SENT = eps',
            'pargcall.INDEX = 1',
            'S.CURRENT = (pcallcontext)',
            'pcallcontext.CALLED_CLASS = (porigin_child)',
            '$class_at(S.CLASSES, porigin_child) = (pclassdesc)',
            'pclassdesc.NAME = $ptascii("B")',
            '$arginfo_method_receiver(S, pargcall)',
            '$calledclass_name(S, pargcall) = ($ptascii("Closure"))',
            '~$calledclass_special(S, pargcall)',
            '$call_task_valid(S, ARGINFO_INVOKE pargcall)',
            *VALID,
            '~$call_task_valid(S, ARGINFO_INVOKE pargcall[.OWNER = eps])',
            '~$call_task_valid(S, ARGINFO_INVOKE pargcall[.KIND = INTRINSIC_FUNC_NUM_ARGS])',
            *FINISH,
            '~((HOBJECT n_owner) <- S_done.ALLOCATIONS)',
        ],
    },
    'dynamic-name-certificate-survives-mutation': {
        'source': SOURCES['dynamic-selected-name-survives-argument'],
        'stage': STAGE,
        'checks': [
            'pargcall.SELECTION = (n_nonce)',
            'pargcall.OWNER = eps',
            'pargcall.SENT = [NAMED_SENT (KNOWN (PINT 1))]',
            'S.SELECTEDCALLS[n_nonce] = pselectedcall',
            'pselectedcall.KIND = INTRINSIC_GET_CALLED_CLASS',
            'pselectedcall.ORIGINAL = $ptascii("get_called_class")',
            '$lookup(S.ENV, $ptascii("f")) = (n_f)',
            'S.STORE[n_f] = DEFINED (PSTRING $ptascii("get_class"))',
            '$arginfo_selected_valid(S, pargcall)',
            '$call_task_valid(S, ARGINFO_INVOKE pargcall)',
            '~$calledclass_special(S, pargcall)',
            *VALID,
            '~$call_task_valid(S, ARGINFO_INVOKE pargcall[.SELECTION = eps])',
            '~$call_task_valid(S, ARGINFO_INVOKE pargcall[.KIND = INTRINSIC_GET_CLASS])',
            'PhpStep: S ~> S_one',
            'S_one.COMPLETION = THROWING n_error',
            '$throwable_field(S_one, n_error, "message") = PSTRING ($ptascii("get_called_class() expects exactly 0 arguments, 1 given"))',
            '$throwable_field(S_one, n_error, "trace") = PARRAY n_trace',
            'S_one.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_builtin))]',
            '$trace_array_field(S_one, n_builtin, $ptascii("function")) = PSTRING ($ptascii("get_called_class"))',
            '$trace_array_field(S_one, n_builtin, $ptascii("args")) = PARRAY n_args',
            'S_one.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 1))]',
            '$trace_graph_valid(S_one, n_trace)',
        ],
    },
    'handler-current-class-and-real-saved-emitter': {
        'source': SOURCES['handler-static-scope-and-emitter-restore'],
        'stage': STAGE + ' -- if S.CURRENT = (pcallcontext) '
                 '-- if pcallcontext.TARGET = HANDLER_METHOD_TARGET true porigin ptbytes pcalltarget',
        'checks': [
            'S.CURRENT = (pcallcontext)',
            'pcallcontext.CALLED_CLASS = (porigin_handler)',
            '$class_at(S.CLASSES, porigin_handler) = (pclassdesc_handler)',
            'pclassdesc_handler.NAME = $ptascii("H")',
            'S.FRAMES = pframe :: pframe_tail*',
            'pframe.CONTEXT = (pcallcontext_emitter)',
            'pcallcontext_emitter.CALLED_CLASS = (porigin_emitter)',
            '$class_at(S.CLASSES, porigin_emitter) = (pclassdesc_emitter)',
            'pclassdesc_emitter.NAME = $ptascii("B")',
            'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_saved*',
            '$error_context_valid(S, pcallcontext)',
            '$calledclass_name(S, pargcall) = ($ptascii("H"))',
            '$call_task_valid(S, ARGINFO_INVOKE pargcall)',
            *VALID,
            '~$call_current_valid(S[.CURRENT = (pcallcontext[.CALLED_CLASS = (porigin_emitter)])])',
            '~$call_frames_valid(S, pframe[.CONTEXT = (pcallcontext_emitter[.CALLED_CLASS = (porigin_handler)])] :: pframe_tail*)',
            *FINISH,
            'S_done.ERRORHANDLER.CALLBACK = eps',
            'S_done.ERRORHANDLERS = eps',
        ],
    },
}


if __name__ == '__main__':
    protocol.run(CASES, (Path(__file__), CATALOGUE))
