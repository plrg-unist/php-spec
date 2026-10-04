#!/usr/bin/env python3
"""Independent source-frame, callback and retained-owner checks for called class."""
from pathlib import Path

import closure_call_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
STAGE = ('S.TODO = (ARGINFO_INVOKE pargcall) :: ptask_tail* '
         '-- if pargcall.KIND = INTRINSIC_GET_CALLED_CLASS')
VALID = [
    '$call_task_valid(S, ARGINFO_INVOKE pargcall)',
    '$call_current_valid(S)',
    '$call_frames_valid(S, S.FRAMES)',
    '$call_descriptors_valid(S)',
    '$closure_state_valid(S)',
    '$heap_valid($heap_graph(S))',
    '~$call_task_valid(S, ARGINFO_INVOKE pargcall[.LINE = 999])',
    '~$call_task_valid(S, ARGINFO_INVOKE pargcall[.SITE = PORIGIN 999 eps])',
    '~$call_task_valid(S, ARGINFO_INVOKE pargcall[.KIND = INTRINSIC_EXIT])',
]
FINISH = [
    'S_done = $drive(S, 2000)',
    'S_done.COMPLETION = NORMAL',
    'S_done.TODO = eps',
    'S_done.FRAMES = eps',
    'S_done.CURRENT = eps',
    'S_done.TRACE = eps',
    '$heap_valid($heap_graph(S_done))',
    'S_done = $drive(S_initial[.COMPLETION = NORMAL], 2000)',
]

CASES = {
    'instance-declaring-and-called-classes': {
        'source': '<?php class A{function show(){echo get_called_class();}}'
                  'class B extends A{}(new B)->show();',
        'stage': STAGE,
        'checks': [
            *VALID,
            'S.CURRENT = (pcallcontext)',
            'pcallcontext.LEXICAL_CLASS = (porigin_owner)',
            'pcallcontext.CALLED_CLASS = (porigin_called)',
            'porigin_owner =/= porigin_called',
            '$class_at(S.CLASSES, porigin_owner) = (pclassdesc_owner)',
            'pclassdesc_owner.NAME = $ptascii("A")',
            '$class_at(S.CLASSES, porigin_called) = (pclassdesc_called)',
            'pclassdesc_called.NAME = $ptascii("B")',
            'pcallcontext.RECEIVER = (n_receiver)',
            'S.OBJECTS[n_receiver] = INSTANCE porigin_called',
            '$calledclass_name(S, pargcall) = ($ptascii("B"))',
            '~$call_current_valid(S[.CURRENT = (pcallcontext[.CALLED_CLASS = (porigin_owner)])])',
            '~$call_current_valid(S[.CURRENT = (pcallcontext[.RECEIVER = (999)])])',
            '~$call_current_valid(S[.CURRENT = (pcallcontext[.LEXICAL_CLASS = (porigin_called)])])',
            '~$call_descriptors_valid(S[.CURRENT = (pcallcontext[.CALLED_CLASS = (porigin_owner)])])',
            'S_bad = $drive(S[.CURRENT = (pcallcontext[.CALLED_CLASS = (porigin_owner)])], 20)',
            'S_bad.COMPLETION = UNSUPPORTED text',
            *FINISH,
        ],
    },
    'static-inherited-class-without-receiver': {
        'source': '<?php class A{static function show(){echo get_called_class();}}'
                  'class B extends A{}B::show();',
        'stage': STAGE,
        'checks': [
            *VALID,
            'S.CURRENT = (pcallcontext)',
            'pcallcontext.RECEIVER = eps',
            'pcallcontext.LEXICAL_CLASS = (porigin_owner)',
            'pcallcontext.CALLED_CLASS = (porigin_called)',
            'porigin_owner =/= porigin_called',
            '$calledclass_name(S, pargcall) = ($ptascii("B"))',
            '$calledclass_special(S, pargcall)',
            '~$call_current_valid(S[.CURRENT = (pcallcontext[.CALLED_CLASS = eps])])',
            '~$call_current_valid(S[.CURRENT = (pcallcontext[.CALLED_CLASS = (porigin_owner)])])',
            '~$call_task_valid(S, ARGINFO_INVOKE pargcall[.SELECTION = (999)])',
            *FINISH,
        ],
    },
    'ordinary-function-stops-saved-method': {
        'source': '<?php function plain(){try{get_called_class();}catch(Error $e){echo "E";}}'
                  'class A{static function go(){plain();}}class B extends A{}B::go();',
        'stage': STAGE,
        'checks': [
            *VALID,
            'S.CURRENT = (pcallcontext)',
            'pcallcontext.NAME = $ptascii("plain")',
            'pcallcontext.CALLED_CLASS = eps',
            'pcallcontext.LEXICAL_CLASS = eps',
            'S.FRAMES = pframe :: pframe_tail*',
            'pframe.CONTEXT = (pcallcontext_saved)',
            'pcallcontext_saved.CALLED_CLASS = (porigin_called)',
            '$class_at(S.CLASSES, porigin_called) = (pclassdesc)',
            'pclassdesc.NAME = $ptascii("B")',
            '$calledclass_name(S, pargcall) = eps',
            '$call_saved_context_valid(S, pframe)',
            '~$call_current_valid(S[.CURRENT = (pcallcontext[.CALLED_CLASS = (porigin_called)])])',
            '~$call_saved_context_valid(S, pframe[.CONTEXT = (pcallcontext_saved[.CALLED_CLASS = eps])])',
            *FINISH,
        ],
    },
    'builtin-wrapper-global-owner': {
        'source': '<?php $f=get_called_class(...);echo $f->__invoke();',
        'stage': STAGE,
        'checks': [
            *VALID,
            'S.CURRENT = eps',
            'S.FRAMES = eps',
            'pargcall.OWNER = (n_owner)',
            'n_owner = 0',
            'pargcall.SELECTION = eps',
            'S.OBJECTS[n_owner] = INTRINSICCLOSURE INTRINSIC_GET_CALLED_CLASS',
            '(HOBJECT n_owner) <- $task_nodes(ARGINFO_INVOKE pargcall)',
            '$arginfo_method_receiver(S, pargcall)',
            '$calledclass_name(S, pargcall) = ($ptascii("Closure"))',
            '~$calledclass_special(S, pargcall)',
            '~$call_task_valid(S, ARGINFO_INVOKE pargcall[.OWNER = eps])',
            '~$call_task_valid(S, ARGINFO_INVOKE pargcall[.OWNER = (999)])',
            '~$call_task_valid(S[.OBJECTS = [INTRINSICCLOSURE INTRINSIC_EXIT]], ARGINFO_INVOKE pargcall)',
            *FINISH,
        ],
    },
    'builtin-wrapper-retains-overwritten-owner': {
        'source': '<?php function zap(&$f){$f=null;echo "Z";return [];}'
                  'class A{static function go(){ $f=get_called_class(...);'
                  'echo $f->__invoke(...zap($f));echo $f===null?"N":"F";'
                  'echo get_called_class();}}class B extends A{}B::go();',
        'stage': STAGE + ' -- if pargcall.OWNER = (n_owner)',
        'checks': [
            *VALID,
            '$lookup(S.ENV, $ptascii("f")) = (n_cell)',
            'S.STORE[n_cell] = DEFINED PNULL',
            '(HOBJECT n_owner) <- S.ALLOCATIONS',
            '(HOBJECT n_owner) <- $task_nodes(ARGINFO_INVOKE pargcall)',
            '$($heap_owners($heap_graph(S), HOBJECT n_owner) > 0)',
            '$calledclass_name(S, pargcall) = ($ptascii("Closure"))',
            *FINISH,
            '~((HOBJECT n_owner) <- S_done.ALLOCATIONS)',
        ],
    },
    'rebound-receiver-differs-from-lexical-class': {
        'source': '<?php class A{}class B{}$f=function(){echo get_called_class();};'
                  '$g=$f->bindTo(new B,A::class);$g();',
        'stage': STAGE,
        'checks': [
            *VALID,
            'S.CURRENT = (pcallcontext)',
            'pcallcontext.TARGET = CLOSURE_TARGET n_closure',
            '$closure_binding_at(S.CLOSUREBINDINGS, n_closure) = (pclosurebinding)',
            'pclosurebinding.LEXICAL = (porigin_lexical)',
            'pclosurebinding.CALLED = (porigin_called)',
            'porigin_lexical =/= porigin_called',
            'pcallcontext.CALLED_CLASS = (porigin_called)',
            'pcallcontext.LEXICAL_CLASS = (porigin_lexical)',
            'pclosurebinding.RECEIVER = (n_receiver)',
            'S.OBJECTS[n_receiver] = INSTANCE porigin_called',
            '$calledclass_name(S, pargcall) = ($ptascii("B"))',
            '~$binding_scope_valid(S, pclosurebinding[.CALLED = (porigin_lexical)])',
            '~$call_current_valid(S[.CURRENT = (pcallcontext[.CALLED_CLASS = (porigin_lexical)])])',
            *FINISH,
        ],
    },
    'method-handler-and-emitter-have-distinct-called-class': {
        'source': '<?php class A{static function h($a,$b,$c,$d){echo get_called_class();return true;}'
                  'static function go(){echo $miss;echo get_called_class();}}'
                  'class B extends A{}class C extends A{}set_error_handler(["B","h"]);'
                  'C::go();restore_error_handler();',
        'stage': STAGE + ' -- if S.CURRENT = (pcallcontext) -- if pcallcontext.ARGC = 4',
        'checks': [
            *VALID,
            '$error_context_valid(S, pcallcontext)',
            'pcallcontext.CALLED_CLASS = (porigin_handler)',
            'S.FRAMES = pframe :: pframe_tail*',
            'pframe.CONTEXT = (pcallcontext_saved)',
            'pcallcontext_saved.CALLED_CLASS = (porigin_emitter)',
            'porigin_handler =/= porigin_emitter',
            '$calledclass_name(S, pargcall) = ($ptascii("B"))',
            '$call_saved_context_valid(S, pframe)',
            '~$call_current_valid(S[.CURRENT = (pcallcontext[.CALLED_CLASS = (porigin_emitter)])])',
            '~$call_saved_context_valid(S, pframe[.CONTEXT = (pcallcontext_saved[.CALLED_CLASS = (porigin_handler)])])',
            'S_bad = $drive(S[.FRAMES = pframe[.CONTEXT = (pcallcontext_saved[.CALLED_CLASS = (porigin_handler)])] :: pframe_tail*], 20)',
            'S_bad.COMPLETION = UNSUPPORTED text',
            *FINISH,
        ],
    },
    'nested-function-authenticates-saved-handler-and-emitter': {
        'source': '<?php function nested(){try{echo get_called_class();}catch(Error $e){echo "E";}}'
                  'class A{static function h($a,$b,$c,$d){nested();echo get_called_class();return true;}'
                  'static function go(){echo $miss;echo get_called_class();}}'
                  'class B extends A{}class C extends A{}set_error_handler(["B","h"]);'
                  'C::go();restore_error_handler();',
        'stage': STAGE + ' -- if S.CURRENT = (pcallcontext) '
                 '-- if pcallcontext.NAME = $ptascii("nested")',
        'checks': [
            *VALID,
            'pcallcontext.CALLED_CLASS = eps',
            '$calledclass_name(S, pargcall) = eps',
            'S.FRAMES = pframe_handler :: pframe_emitter :: pframe_tail*',
            'pframe_handler.CONTEXT = (pcallcontext_handler)',
            'pcallcontext_handler.ARGC = 4',
            'pcallcontext_handler.CALLED_CLASS = (porigin_handler)',
            'pframe_emitter.CONTEXT = (pcallcontext_emitter)',
            'pcallcontext_emitter.CALLED_CLASS = (porigin_emitter)',
            'porigin_handler =/= porigin_emitter',
            '$error_context_valid(S, pcallcontext_handler)',
            '$call_saved_context_valid(S, pframe_handler)',
            '$call_saved_context_valid(S, pframe_emitter)',
            '~$call_saved_context_valid(S, pframe_handler[.CONTEXT = (pcallcontext_handler[.CALLED_CLASS = (porigin_emitter)])])',
            '~$call_saved_context_valid(S, pframe_handler[.CONTEXT = (pcallcontext_handler[.ARGC = 0])])',
            '~$call_current_valid(S[.CURRENT = (pcallcontext[.CALLED_CLASS = (porigin_handler)])])',
            *FINISH,
        ],
    },
    'dynamic-selected-receipt-retains-source-name': {
        'source': '<?php class A{static function go(){$f="GeT_CaLlEd_ClAsS";echo $f();}}'
                  'class B extends A{}B::go();',
        'stage': STAGE,
        'checks': [
            *VALID,
            'pargcall.SELECTION = (n_nonce)',
            'S.SELECTEDCALLS[n_nonce] = pselectedcall',
            'pselectedcall.KIND = INTRINSIC_GET_CALLED_CLASS',
            '$selected_entry_source_valid(S, pselectedcall)',
            '$calledclass_name(S, pargcall) = ($ptascii("B"))',
            '~$calledclass_special(S, pargcall)',
            '~$arginfo_selected_valid(S, pargcall[.SELECTION = (999)])',
            '~$selected_entry_source_valid(S, pselectedcall[.KIND = INTRINSIC_FUNC_NUM_ARGS])',
            '~$selected_entry_source_valid(S, pselectedcall[.ORIGINAL = $ptascii("get_class")])',
            *FINISH,
        ],
    },
    'static-closure-keeps-retired-maker-called-class': {
        'source': '<?php class A{static function make(){return static function(){echo get_called_class();};}}'
                  'class B extends A{}$f=B::make();$f();',
        'stage': STAGE,
        'checks': [
            *VALID,
            'S.CURRENT = (pcallcontext)',
            'pcallcontext.TARGET = CLOSURE_TARGET n_closure',
            '$closure_scope_at(S.CLOSURESCOPES, n_closure) = (pclosurescope)',
            'pclosurescope.LEXICAL = porigin_owner',
            'pclosurescope.CALLED = porigin_called',
            'porigin_owner =/= porigin_called',
            'pclosurescope.RECEIVER = eps',
            '$closure_scope_row_valid(S, pclosurescope)',
            'pcallcontext.CALLED_CLASS = (porigin_called)',
            '$calledclass_name(S, pargcall) = ($ptascii("B"))',
            '~$closure_scope_row_valid(S, pclosurescope[.CALLED = porigin_owner])',
            '~$call_current_valid(S[.CURRENT = (pcallcontext[.CALLED_CLASS = (porigin_owner)])])',
            *FINISH,
        ],
    },
}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__),))
