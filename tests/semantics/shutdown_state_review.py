#!/usr/bin/env python3
"""Independent source-reached shutdown cache, C-call and ownership checks."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

from shutdown_review import recorded
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
SOURCES = {row['id']: row['source'] for row in json.loads(
    Path(__file__).with_name('shutdown_review_cases.json').read_text())}
VALID = ['$call_current_valid(S)', '$call_frames_valid(S, S.FRAMES)',
         '$call_descriptors_valid(S)', '$class_state_valid(S)',
         '$heap_valid($heap_graph(S))']
DONE = ['S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.CURRENT = eps',
        'S_done.HELD = eps', 'S_done.CONSTCONTEXT = eps',
        'S_done.SHUTDOWN.PHASE = SHUTDOWN_DONE', 'S_done.SHUTDOWN.SENT = eps',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))']
CURRENT = ['S.CURRENT = (pcallcontext)', 'S.FRAMES = [pframe]',
           'pframe.TODO = [SHUTDOWN_RESULT n_index poperand*]',
           'pframe.CONTEXT = eps', 'pframe.LOCALS = eps',
           'pframe.ORIGIN = eps', 'pframe.CONSTCONTEXT = eps',
           'pcallcontext.CALLSITE = eps', 'pcallcontext.LINE = $(-1)',
           'pcallcontext.WRAPPER = eps', 'pcallcontext.HOLES = eps',
           'pshutdownentry = S.SHUTDOWN.ENTRIES[n_index]',
           'pcallcontext.TARGET = pshutdownentry.TARGET',
           '$shutdown_context_valid(S, pcallcontext)']

CASES = {
    'retired-imported-trait-maker': {
        'source': '<?php declare(strict_types=1);trait T{static function reg(){register_shutdown_function([self::class,"h"]);}private static function h(Exception $e=new Exception(self::N)){echo $e->getMessage(),":",get_called_class(),":",func_num_args(),";";}}class C{use T;private const N="kept";}class D{use T;private const N="other";}C::reg();exit(7);',
        'stage': 'S.TODO = [SHUTDOWN_SEND 0 0 eps]',
        'checks': [
            'S.CURRENT = eps', 'S.FRAMES = eps', 'S.CONSTCONTEXT = eps',
            'S.SHUTDOWN.COMPLETION = EXITED 7',
            'pshutdownentry = S.SHUTDOWN.ENTRIES[0]',
            'pshutdownentry.CAPTURE = (pmethodcapture)',
            'pshutdownentry.CALL.SENT = [NAMED_SENT (KNOWN (PARRAY n_raw))]',
            'pshutdownentry.ARGS = eps',
            '~((HARRAY n_raw) <- S.ALLOCATIONS)',
            '$shutdown_roots(S.SHUTDOWN.ENTRIES) = eps',
            '$class_named(S.CLASSNAMES, $ptascii("c")) = (porigin_class)',
            '$class_named(S.CLASSNAMES, $ptascii("d")) = (porigin_other)',
            '$effective_method(S, porigin_class, $ptascii("reg"), |S.CLASSES|) = (pmethoddesc)',
            '$effective_method(S, porigin_class, $ptascii("h"), |S.CLASSES|) = (pmethoddesc_handler)',
            '$effective_method(S, porigin_other, $ptascii("reg"), |S.CLASSES|) = (pmethoddesc_other)',
            'pmethodcapture.FUNCTION = pmethoddesc.FUNCTION.ORIGIN',
            'pmethodcapture.LEXICAL_CLASS = (porigin_class)',
            'pmethodcapture.CALLED_CLASS = (porigin_class)',
            'pmethodcapture.CALLSITE = (porigin_call)',
            '$trait_imported_origin(pmethodcapture.FUNCTION)',
            'pshutdownentry.CALL.SITE = PORIGIN n_unit pcpath',
            '$goto_source_owner($all_functions(S), n_unit, pcpath) = (pfunction_physical)',
            '$trait_source_same(pfunction_physical, pmethoddesc.FUNCTION)',
            '$trait_capture_invocation(S, pmethoddesc.FUNCTION, pmethodcapture, porigin_call)',
            '$shutdown_capture_valid(S, pshutdownentry.CALL.SITE, (pmethodcapture))',
            '~$shutdown_capture_valid(S, pshutdownentry.CALL.SITE, (pmethodcapture[.FUNCTION = pmethoddesc_other.FUNCTION.ORIGIN]))',
            '~$shutdown_capture_valid(S, pshutdownentry.CALL.SITE, (pmethodcapture[.FUNCTION = pmethoddesc_other.FUNCTION.ORIGIN][.LEXICAL_CLASS = (porigin_other)][.CALLED_CLASS = (porigin_other)]))',
            '~$shutdown_capture_valid(S, pshutdownentry.CALL.SITE, (pmethodcapture[.FUNCTION = pmethoddesc_handler.FUNCTION.ORIGIN]))',
            '~$shutdown_capture_valid(S, pshutdownentry.CALL.SITE, (pmethodcapture[.LEXICAL_CLASS = (porigin_other)]))',
            '~$shutdown_capture_valid(S, pshutdownentry.CALL.SITE, (pmethodcapture[.CALLED_CLASS = (porigin_other)]))',
            '~$shutdown_capture_valid(S, pshutdownentry.CALL.SITE, (pmethodcapture[.CALLSITE = (pshutdownentry.CALL.SITE)]))',
            '~$shutdown_registration_valid(S, pshutdownentry.CALL[.SITE = porigin_call])',
            '$shutdown_entry_valid(S, pshutdownentry)',
            '~$shutdown_entry_valid(S, pshutdownentry[.CAPTURE = (pmethodcapture[.CALLED_CLASS = (porigin_other)])])',
            '$call_task_valid(S, SHUTDOWN_SEND 0 0 eps)',
            *VALID, 'S_paused = $drive(S, 0)', 'S_paused.COMPLETION = BUDGET',
            'S_paused.SHUTDOWN = S.SHUTDOWN', 'S_paused.ALLOCATIONS = S.ALLOCATIONS',
            'S_done = $drive(S, 1500)', 'S_done.COMPLETION = EXITED 7', *DONE,
            '$drive(S_paused[.COMPLETION = NORMAL], 1500) = S_done',
            'S_done.EVENTS = [OUTPUT $ptascii("kept"), OUTPUT $ptascii(":"), OUTPUT $ptascii("C"), OUTPUT $ptascii(":"), OUTPUT $ptascii("0"), OUTPUT $ptascii(";")]',
            '~((HOBJECT 0) <- S_done.ALLOCATIONS)',
        ],
    },
    'cached-private-reference-selection': {
        'source': '<?php class C{static function reg(){ $m="a";$raw=["C",&$m];'
                  'register_shutdown_function($raw,[$m]);$m="b";}'
                  'private static function a($v){}private static function b($v){}}C::reg();',
        'stage': 'S.TODO = [SHUTDOWN_SEND 0 0 eps]',
        'checks': [
            'pshutdownentry = S.SHUTDOWN.ENTRIES[0]',
            'S.CURRENT = eps', 'S.FRAMES = eps', 'S.CONSTCONTEXT = eps',
            'pshutdownentry.CALL.SENT = [NAMED_SENT (KNOWN (PARRAY n_raw)), NAMED_SENT (KNOWN (PARRAY n_arg))]',
            'pshutdownentry.ARGS = [PARRAY n_arg]',
            'pshutdownentry.RAW = (parray)',
            'parray.ITEMS = [ENTRY (KINT 0) (DIRECT (PSTRING $ptascii("C"))), ENTRY (KINT 1) (DIRECT (PSTRING $ptascii("a")))]',
            '~((HARRAY n_raw) <- S.ALLOCATIONS)',
            '$heap_owners($heap_graph(S), HARRAY n_arg) = 1',
            '$shutdown_entry_valid(S, pshutdownentry)',
            'pshutdownentry.TARGET = HANDLER_METHOD_TARGET b_class porigin_requested ptbytes (SCOPE_METHOD_TARGET pcalltarget pcallableaccess)',
            'pcallableaccess.SCOPE = (porigin_requested)',
            '$effective_method(S, porigin_requested, $ptascii("b"), |S.CLASSES|) = (pmethoddesc)',
            '$scope_handler_base(S, porigin_requested, pmethoddesc, eps, b_class) = (pcalltarget_other)',
            '~$shutdown_entry_valid(S, pshutdownentry[.TARGET = HANDLER_METHOD_TARGET b_class porigin_requested $ptascii("b") (SCOPE_METHOD_TARGET pcalltarget_other pcallableaccess)])',
            '~$shutdown_entry_valid(S, pshutdownentry[.RAW = ($array_empty())])',
            '~$shutdown_entry_valid(S, pshutdownentry[.ARGS = [PNULL]])',
            '~$shutdown_entry_valid(S, pshutdownentry[.CALL.KIND = INTRINSIC_SET_EXCEPTION_HANDLER])',
            '$call_task_valid(S, SHUTDOWN_SEND 0 0 eps)',
            '~$call_task_valid(S, SHUTDOWN_SEND 1 0 eps)',
            '~$shutdown_state_valid(S[.SHUTDOWN.INDEX = $(|S.SHUTDOWN.ENTRIES| + 1)])',
            *VALID, 'S_paused = $drive(S, 0)', 'S_paused.COMPLETION = BUDGET',
            'S_paused.SHUTDOWN = S.SHUTDOWN', 'S_paused.ALLOCATIONS = S.ALLOCATIONS',
            'S_done = $drive(S, 1500)', 'S_done.COMPLETION = NORMAL', *DONE,
            '$drive(S_paused[.COMPLETION = NORMAL], 1500) = S_done',
            '$heap_owners($heap_graph(S_done), HARRAY n_arg) = 1',
        ],
    },
    'retired-api-and-static-selector': {
        'source': '<?php class C{static function h($v){}}function make(){'
                  '$r=register_shutdown_function(...);$raw=[new C,"h"];'
                  '$r($raw,new stdClass());}make();',
        'stage': 'S.TODO = [SHUTDOWN_SEND 0 0 eps]',
        'checks': [
            'pshutdownentry = S.SHUTDOWN.ENTRIES[0]',
            'pshutdownentry.CALL.OWNER = (n_api)',
            'pshutdownentry.CALL.SENT = [NAMED_SENT (KNOWN (PARRAY n_raw)), NAMED_SENT (KNOWN (POBJECT n_arg))]',
            'pshutdownentry.RAW = (parray)',
            'parray.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_selector)), ENTRY (KINT 1) (DIRECT (PSTRING $ptascii("h")))]',
            '~((HOBJECT n_api) <- S.ALLOCATIONS)',
            '~((HOBJECT n_selector) <- S.ALLOCATIONS)',
            '~((HARRAY n_raw) <- S.ALLOCATIONS)',
            '$target_nodes(pshutdownentry.TARGET) = eps',
            '$shutdown_roots(S.SHUTDOWN.ENTRIES) = [HOBJECT n_arg]',
            '$heap_owners($heap_graph(S), HOBJECT n_arg) = 1',
            '$shutdown_registration_valid(S, pshutdownentry.CALL)',
            '~$shutdown_registration_valid(S, pshutdownentry.CALL[.OWNER = (n_arg)])',
            '~$shutdown_registration_valid(S, pshutdownentry.CALL[.OWNER = (|S.OBJECTS|)])',
            '$shutdown_entry_valid(S, pshutdownentry)',
            *VALID, 'S_done = $drive(S, 1500)', 'S_done.COMPLETION = NORMAL', *DONE,
            '$heap_owners($heap_graph(S_done), HOBJECT n_arg) = 1',
        ],
    },
    'zero-formals-original-extra': {
        'source': SOURCES['zero-formals-extra'],
        'stage': 'S.TODO = (ARGINFO_INVOKE pargcall) :: ptask_tail* -- if S.CURRENT = (pcallcontext) -- if $shutdown_context_kind(S, pcallcontext)',
        'checks': [
            *CURRENT, 'pcallcontext.ARGC = 2',
            'pcallcontext.EXTRA = [KNOWN (PSTRING $ptascii("first")), KNOWN (PSTRING $ptascii("second"))]',
            '~$shutdown_context_valid(S, pcallcontext[.EXTRA = [KNOWN PNULL, KNOWN PNULL]])',
            '~$shutdown_context_valid(S, pcallcontext[.ARGC = 0])',
            '~$shutdown_context_valid(S, pcallcontext[.HOLES = [0]])',
            '~$shutdown_context_valid(S, pcallcontext[.WRAPPER = ({SLOTS eps, NAMED eps})])',
            '~$shutdown_context_valid(S, pcallcontext[.CALLSITE = (pcallcontext.FUNCTION)])',
            '~$shutdown_context_valid(S, pcallcontext[.LINE = 0])',
            '~$shutdown_context_valid(S[.FRAMES = eps], pcallcontext)',
            '~$shutdown_context_valid(S[.FRAMES = [pframe[.CONSTCONTEXT = ({ORIGIN pcallcontext.FUNCTION, LINE 1, FACTS eps})]]], pcallcontext)',
            *VALID, 'S_done = $drive(S, 1500)', 'S_done.COMPLETION = NORMAL', *DONE,
        ],
    },
    'saved-private-callback-scope': {
        'source': SOURCES['saved-private-callback-scope'],
        'stage': 'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* -- if pconfigcall.KIND = INTRINSIC_REGISTER_SHUTDOWN_FUNCTION -- if S.CURRENT = (pcallcontext) -- if ~$shutdown_context_kind(S, pcallcontext) -- if S.FRAMES = [pframe_saved, pframe_global] -- if pframe_global.TODO = [SHUTDOWN_RESULT n_index poperand*]',
        'checks': [
            'S.CURRENT = (pcallcontext)',
            'S.FRAMES = [pframe_saved, pframe_global]',
            'pframe_saved.CONTEXT = (pcallcontext_handler)',
            'pframe_global.TODO = [SHUTDOWN_RESULT n_index poperand*]',
            'pcallcontext.LEXICAL_CLASS = eps',
            'pcallcontext_handler.LEXICAL_CLASS = (porigin_class)',
            '$shutdown_context_valid(S, pcallcontext_handler)',
            '~$shutdown_context_valid(S, pcallcontext)',
            '$call_saved_context_valid(S, pframe_saved)',
            '~$shutdown_context_valid(S, pcallcontext_handler[.ARGC = 1])',
            '~$shutdown_context_valid(S, pcallcontext_handler[.HOLES = [0]])',
            '~$shutdown_context_valid(S[.FRAMES = [pframe_saved, pframe_global[.CONTEXT = (pcallcontext)]]], pcallcontext_handler)',
            '~$shutdown_context_valid(S[.FRAMES = [pframe_saved, pframe_global[.TODO = eps]]], pcallcontext_handler)',
            '~$shutdown_context_valid(S[.FRAMES = [pframe_saved, pframe_global[.CONSTCONTEXT = ({ORIGIN pcallcontext_handler.FUNCTION, LINE 1, FACTS eps})]]], pcallcontext_handler)',
            '$error_handler_resolution(S, PSTRING $ptascii("C::secret")) = HANDLERINVALID ptbytes_reason',
            *VALID, 'S_done = $drive(S, 2000)', 'S_done.COMPLETION = NORMAL', *DONE,
            'S_done.SHUTDOWN.INDEX = 2',
        ],
    },
    'warning-throw-resumes-selected': {
        'source': SOURCES['warning-handled-throw'],
        'stage': 'S.TODO = [SHUTDOWN_REFERENCE 0 0 eps]',
        'checks': [
            'pshutdownentry = S.SHUTDOWN.ENTRIES[0]',
            'pshutdownentry.ARGS = [PSTRING $ptascii("value")]',
            'S.CURRENT = eps', 'S.FRAMES = eps', 'S.CONSTCONTEXT = eps',
            '$target_function(S, pshutdownentry.TARGET) = (pfunction)',
            'S.ORIGIN = (pfunction.ORIGIN)',
            'S.EXCEPTIONHANDLER = (PSTRING $ptascii("h"))',
            '$call_task_valid(S, SHUTDOWN_REFERENCE 0 0 eps)',
            '~$call_task_valid(S, SHUTDOWN_REFERENCE 1 0 eps)',
            '~$call_task_valid(S[.ORIGIN = eps], SHUTDOWN_REFERENCE 0 0 eps)',
            '~$call_task_valid(S[.CONSTCONTEXT = ({ORIGIN pfunction.ORIGIN, LINE 1, FACTS eps})], SHUTDOWN_REFERENCE 0 0 eps)',
            *VALID, 'S_done = $drive(S, 1500)', 'S_done.COMPLETION = NORMAL', *DONE,
            'S_done.SHUTDOWN.INDEX = 2',
        ],
    },
    'retired-reference-send-cell': {
        'source': '<?php class C{}function a(&$v){$v=null;}function b(){}$x="other";$other=&$x;'
                  'register_shutdown_function("a",new C);register_shutdown_function("b");',
        'stage': 'S.TODO = [SHUTDOWN_RESULT 0 poperand*]',
        'checks': [
            'S.TODO = [SHUTDOWN_RESULT 0 ([REFERENCE n_cell])]',
            'S.CURRENT = eps', 'S.FRAMES = eps',
            'pshutdownentry = S.SHUTDOWN.ENTRIES[0]',
            'pshutdownentry.ARGS = [POBJECT n_arg]',
            'S.STORE[n_cell] = DEFINED PNULL',
            'n_cell <- S.REFCELLS', '~((HCELL n_cell) <- S.ALLOCATIONS)',
            '$lookup(S.ENV, $ptascii("other")) = (n_other)',
            'n_other <- S.REFCELLS', 'n_other =/= n_cell',
            '$task_nodes(SHUTDOWN_RESULT 0 ([REFERENCE n_cell])) = eps',
            '$heap_owners($heap_graph(S), HOBJECT n_arg) = 1',
            '$shutdown_result_valid(S, 0, [REFERENCE n_cell])',
            '~$shutdown_result_valid(S, 0, [KNOWN (POBJECT n_arg)])',
            '~$shutdown_result_valid(S, 0, [REFERENCE n_other])',
            '~$shutdown_result_valid(S, 0, [REFERENCE $(|S.STORE|)])',
            *VALID, 'S_paused = $drive(S, 0)', 'S_paused.COMPLETION = BUDGET',
            'S_paused.ALLOCATIONS = S.ALLOCATIONS',
            'S_done = $drive(S, 1500)', 'S_done.COMPLETION = NORMAL', *DONE,
            '$drive(S_paused[.COMPLETION = NORMAL], 1500) = S_done',
            '$heap_owners($heap_graph(S_done), HOBJECT n_arg) = 1',
        ],
    },
    'ignored-reference-return': {
        'source': SOURCES['reference-return-ignored'],
        'stage': 'S.TODO = [SHUTDOWN_RESULT 0 eps]',
        'checks': [
            'S.CURRENT = eps', 'S.FRAMES = eps',
            'S.RESULT = REFERENCE n_cell',
            'S.STORE[n_cell] = DEFINED (PSTRING $ptascii("value"))',
            '$heap_owners($heap_graph(S), HCELL n_cell) = 1',
            '$call_reference_operand_valid(S, S.RESULT)',
            '$shutdown_result_valid(S, 0, eps)',
            *VALID, 'S_done = $drive(S, 1500)', 'S_done.COMPLETION = NORMAL', *DONE,
            'S_done.RESULT = KNOWN PNULL', '~((HCELL n_cell) <- S_done.ALLOCATIONS)',
        ],
    },
    'append-from-exception-handler': {
        'source': SOURCES['append-in-exception-handler'],
        'stage': 'S.TODO = [SHUTDOWN_RESULT 0 eps]',
        'checks': [
            'S.CURRENT = eps', 'S.FRAMES = eps', 'S.ORIGIN = eps',
            'S.SHUTDOWN.PHASE = SHUTDOWN_RUNNING',
            'S.SHUTDOWN.INDEX = 0', '|S.SHUTDOWN.ENTRIES| = 3',
            'S.SHUTDOWN.COMPLETION = NORMAL',
            'S.EXCEPTIONHANDLER = (PSTRING $ptascii("h"))',
            '$shutdown_result_valid(S, 0, eps)',
            '~$shutdown_result_valid(S, 1, eps)',
            *VALID, 'S_done = $drive(S, 1500)', 'S_done.COMPLETION = NORMAL', *DONE,
            'S_done.SHUTDOWN.INDEX = 3',
            '|S_done.SHUTDOWN.ENTRIES| = 3',
            'S_done.EVENTS = [OUTPUT $ptascii("A;"), OUTPUT $ptascii("H;"), OUTPUT $ptascii("B;"), OUTPUT $ptascii("C;")]',
        ],
    },
    'frozen-fatal-survives-reporting-write': {
        'source': SOURCES['status-fatal-before-reporting-change'],
        'stage': 'S.TODO = [SHUTDOWN_RESULT 0 eps]',
        'checks': [
            'S.CURRENT = eps', 'S.FRAMES = eps', 'S.REPORTING = 0',
            'S.SHUTDOWN.COMPLETION = REQUESTFATAL $ptascii("Error") $ptascii("main fatal") 2',
            'ptbytes_file = $call_sourcefile(S.FILES, PORIGIN 0 eps)',
            'ptbytes_stderr = $ptascii("Fatal error: main fatal in ") ++ ptbytes_file ++ $ptascii(" on line 2") ++ [10] ++ $ptascii("Stack trace:") ++ [10] ++ $ptascii("#0 ") ++ ptbytes_file ++ $ptascii("(2): trigger_error(\'main fatal\', 256)") ++ [10] ++ $ptascii("#1 {main}") ++ [10]',
            'S.EVENTS = [DIAGNOSTIC "Deprecated" $error_user_deprecation() 2, STDERR ptbytes_stderr, OUTPUT $ptascii("A;")]',
            '~$shutdown_state_valid(S[.SHUTDOWN.PHASE = SHUTDOWN_PENDING])',
            *VALID, 'S_done = $drive(S, 1500)',
            'S_done.COMPLETION = S.SHUTDOWN.COMPLETION', *DONE,
            'S_done.EVENTS = S.EVENTS',
        ],
    },
    'compiler-fatal-queue-history': {
        'source': SOURCES['compile-stop-dynamic-compiler-fatal'],
        'eval': 'class B{public function __wakeup():int{}}',
        'stage': 'S.TODO = [SHUTDOWN_ENTER 0 eps]',
        'checks': [
            'S.COMPLETION = NORMAL', '~S.COMPILESTOP',
            'S.SHUTDOWN.PHASE = SHUTDOWN_RUNNING',
            'pshutdownentry = S.SHUTDOWN.ENTRIES[0]',
            'S.SHUTDOWN.COMPLETION = REQUESTFATAL $ptascii("CompileError") $ptascii("B::__wakeup(): Return type must be void when declared") 1',
            '$declaration_history_valid(S)',
            '$call_task_valid(S, SHUTDOWN_ENTER 0 eps)',
            '~$declaration_history_valid(S[.SHUTDOWN.PHASE = SHUTDOWN_PENDING])',
            '~$declaration_history_valid(S[.SHUTDOWN.COMPLETION = NORMAL])',
            '~$declaration_history_valid(S[.SHUTDOWN.ENTRIES = [pshutdownentry[.ARGS = [PNULL]]]])',
            *VALID, 'S_paused = $drive(S, 0)', 'S_paused.COMPLETION = BUDGET',
            'S_paused.SHUTDOWN = S.SHUTDOWN', 'S_done = $drive(S, 1500)',
            'S_done.COMPLETION = S.SHUTDOWN.COMPLETION', *DONE,
            '$declaration_history_valid(S_done)',
            '$drive(S_paused[.COMPLETION = NORMAL], 1500) = S_done',
        ],
    },
    'compiler-fatal-mask-frozen-before-callback': {
        'source': SOURCES['compile-fatal-mask-before-callback'],
        'eval': 'class B{public function __wakeup():int{}}',
        'stage': 'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* -- if pconfigcall.KIND = INTRINSIC_ERROR_REPORTING -- if S.CURRENT = (pcallcontext) -- if $shutdown_context_kind(S, pcallcontext)',
        'checks': [
            *CURRENT, 'S.REPORTING = 0', 'S.EVENTS = eps',
            'S.SHUTDOWN.COMPLETION = REQUESTFATAL $ptascii("CompileError") $ptascii("B::__wakeup(): Return type must be void when declared") 1',
            '$declaration_history_valid(S)',
            '~$declaration_history_valid(S[.SHUTDOWN.COMPLETION = NORMAL])',
            *VALID, 'S_paused = $drive(S, 0)', 'S_paused.COMPLETION = BUDGET',
            'S_paused.EVENTS = eps', 'S_paused.SHUTDOWN = S.SHUTDOWN',
            'S_done = $drive(S, 1500)',
            'S_done.REPORTING = 30719',
            'S_done.COMPLETION = S.SHUTDOWN.COMPLETION', *DONE,
            'S_done.EVENTS = [OUTPUT $ptascii("S;"), DIAGNOSTIC "Warning" $ptascii("later") 1]',
            '$declaration_history_valid(S_done)',
            '$drive(S_paused[.COMPLETION = NORMAL], 1500) = S_done',
        ],
    },
    'compound-error-callback-internal-diagnostic': {
        'source': '<?php class A{static function w($n,$m,$f,$l){echo "W:",$n,":",$f,":",$l,";";return true;}}class B extends A{}class E extends Exception{function __construct(){$this->message=[];}}function s(){echo "S;";}set_error_handler(["B","A::w"]);register_shutdown_function("s");throw new E;',
        'stage': 'S.TODO = [API_CALLABLE_RESULT papiquery 1] -- if papiquery.SOURCE = ERROR_HANDLER_INVOKE perrorcall -- if perrorcall.RESUME = SHUTDOWN_RENDER pshutdownrender',
        'checks': [
            'S.TODO = [API_CALLABLE_RESULT papiquery 1]',
            'papiquery.SOURCE = ERROR_HANDLER_INVOKE perrorcall',
            'papiquery.LINE = 0', 'perrorcall.RESUME = SHUTDOWN_RENDER pshutdownrender',
            'perrorcall.LINE = 0', 'perrorcall.LEVEL = 2',
            'perrorcall.EVENT = DIAGNOSTIC_INTERNAL "Warning" $ptascii("Array to string conversion") 0',
            'S.CURRENT = eps', 'S.FRAMES = eps', 'S.CONSTCONTEXT = eps',
            '$error_call_valid(S, perrorcall)',
            '$call_task_valid(S, API_CALLABLE_RESULT papiquery 1)',
            '$api_warning_message(S, papiquery, 1) = (ptbytes)',
            '$api_warning_event(S, papiquery, ptbytes) = DIAGNOSTIC_INTERNAL "Deprecated" ptbytes 0',
            'S.EVENTS = [DIAGNOSTIC "Deprecated" ptbytes 1, DIAGNOSTIC_INTERNAL "Deprecated" ptbytes 0]',
            '$heap_owners($heap_graph(S), HOBJECT pshutdownrender.ROOT) = 1',
            '~$call_task_valid(S, API_CALLABLE_RESULT (papiquery[.SOURCE = ERROR_HANDLER_INVOKE (perrorcall[.LINE = 1])]) 1)',
            '~$call_task_valid(S[.CONSTCONTEXT = ({ORIGIN perrorcall.SITE, LINE 1, FACTS eps})], API_CALLABLE_RESULT papiquery 1)',
            '$api_warning_event(S, papiquery[.LINE = 1], ptbytes) = DIAGNOSTIC "Deprecated" ptbytes 1',
            '$api_warning_event(S[.CONSTCONTEXT = ({ORIGIN perrorcall.SITE, LINE 1, FACTS eps})], papiquery, ptbytes) = DIAGNOSTIC "Deprecated" ptbytes 0',
            *VALID, 'S_paused = $drive(S, 0)', 'S_paused.COMPLETION = BUDGET',
            'S_paused.SHUTDOWN = S.SHUTDOWN', 'S_paused.ALLOCATIONS = S.ALLOCATIONS',
            'S_done = $drive(S, 1500)',
            'S_done.COMPLETION = REQUESTFATAL $ptascii("E") $ptascii("Array") 1', *DONE,
            '~((HOBJECT pshutdownrender.ROOT) <- S_done.ALLOCATIONS)',
            '$drive(S_paused[.COMPLETION = NORMAL], 1500) = S_done',
        ],
    },
    'exception-variadic-saved-received-view': {
        'source': SOURCES['exception-variadic-saved-local-write'],
        'stage': 'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* -- if pconfigcall.KIND = INTRINSIC_ERROR_REPORTING -- if S.CURRENT = (pcallcontext) -- if S.FRAMES = [pframe_saved, pframe_global] -- if pframe_global.TODO = (EXCEPTION_HANDLER_RESULT pexceptioncall) :: ptask_global*',
        'checks': [
            'S.CURRENT = (pcallcontext)',
            'S.FRAMES = [pframe_saved, pframe_global]',
            'pframe_saved.CONTEXT = (pcallcontext_handler)',
            'pframe_global.TODO = (EXCEPTION_HANDLER_RESULT pexceptioncall) :: ptask_global*',
            'pframe_global.CONTEXT = eps', 'pframe_global.LOCALS = eps',
            'pframe_global.ORIGIN = eps', 'pframe_global.CONSTCONTEXT = eps',
            'pcallcontext_handler.CALLSITE = eps',
            'pcallcontext_handler.LINE = $(-1)', 'pcallcontext_handler.ARGC = 1',
            'pcallcontext_handler.EXTRA = [KNOWN (PSTRING $ptascii("text"))]',
            'pexceptioncall.SENT = (KNOWN (POBJECT pexceptioncall.OBJECT))',
            '$exception_context_call(S, pcallcontext_handler) = (pexceptioncall)',
            '$exception_context_valid(S, pcallcontext_handler)',
            '$call_saved_context_valid(S, pframe_saved)',
            '~$exception_context_valid(S, pcallcontext)',
            '$heap_owners($heap_graph(S), HOBJECT pexceptioncall.OBJECT) = 1',
            '~$exception_context_valid(S, pcallcontext_handler[.EXTRA = [KNOWN (POBJECT pexceptioncall.OBJECT)]])',
            '~$exception_context_valid(S, pcallcontext_handler[.EXTRA = [KNOWN PNULL]])',
            '~$exception_context_valid(S, pcallcontext_handler[.ARGC = 0])',
            '~$exception_context_valid(S, pcallcontext_handler[.CALLSITE = (pcallcontext_handler.FUNCTION)])',
            '~$exception_context_valid(S, pcallcontext_handler[.LINE = 0])',
            '~$exception_context_valid(S, pcallcontext_handler[.HOLES = [0]])',
            '~$exception_context_valid(S[.FRAMES = [pframe_saved, pframe_global[.CONTEXT = (pcallcontext)]]], pcallcontext_handler)',
            '~$exception_context_valid(S[.FRAMES = [pframe_saved, pframe_global[.CONSTCONTEXT = ({ORIGIN pcallcontext_handler.FUNCTION, LINE 1, FACTS eps})]]], pcallcontext_handler)',
            *VALID, 'S_paused = $drive(S, 0)', 'S_paused.COMPLETION = BUDGET',
            'S_paused.FRAMES = S.FRAMES', 'S_paused.ALLOCATIONS = S.ALLOCATIONS',
            'S_done = $drive(S, 1500)', 'S_done.COMPLETION = NORMAL', *DONE,
            '~((HOBJECT pexceptioncall.OBJECT) <- S_done.ALLOCATIONS)',
            '$drive(S_paused[.COMPLETION = NORMAL], 1500) = S_done',
        ],
    },
    'converted-variadic-original-owners': {
        'source': SOURCES['receive-variadic-stringable-indexed'],
        'stage': 'S.TODO = [VARIADIC_STRING_RESULT pvariadicstring] -- if pvariadicstring.ELEMENT = 1',
        'checks': [
            *CURRENT,
            'S.TODO = [VARIADIC_STRING_RESULT pvariadicstring]',
            'pvariadicstring.ELEMENT = 1',
            'pshutdownentry.ARGS = [POBJECT n_first, POBJECT n_second]',
            'S.SHUTDOWN.SENT = [KNOWN (POBJECT n_first), KNOWN (POBJECT n_second)]',
            'pcallcontext.EXTRA = [KNOWN (PSTRING $ptascii("v")), KNOWN (POBJECT n_second)]',
            'S.SHUTDOWN.RECEIVED = pcallcontext.EXTRA',
            'S.RESULT = KNOWN (PSTRING $ptascii("v"))',
            '$heap_owners($heap_graph(S), HOBJECT n_first) = 1',
            '~$shutdown_context_valid(S, pcallcontext[.EXTRA = [KNOWN PNULL, KNOWN (POBJECT n_second)]])',
            '~$shutdown_context_valid(S[.SHUTDOWN.RECEIVED = eps], pcallcontext)',
            '~$receive_string_scope_valid(S, VARIADIC_STRING_RESULT pvariadicstring[.ELEMENT = 0])',
            '$variadic_context_coerced(S, 0, KNOWN (PSTRING $ptascii("v"))) = S',
            '$variadic_context_coerced(S, 1, KNOWN (PSTRING $ptascii("forged"))) = S',
            *VALID,
            'PhpStep: S ~> S_next',
            'S_next.CURRENT = (pcallcontext_next)',
            'pcallcontext_next.EXTRA = [KNOWN (PSTRING $ptascii("v")), KNOWN (PSTRING $ptascii("v"))]',
            'S_next.SHUTDOWN.RECEIVED = pcallcontext_next.EXTRA',
            'S_next.SHUTDOWN.SENT = S.SHUTDOWN.SENT',
            'S_next.SHUTDOWN.ENTRIES = S.SHUTDOWN.ENTRIES',
            '$shutdown_context_valid(S_next, pcallcontext_next)',
            '$heap_owners($heap_graph(S_next), HOBJECT n_first) = 1',
            '$heap_owners($heap_graph(S_next), HOBJECT n_second) = 1',
            'S_paused = $drive(S, 0)', 'S_paused.COMPLETION = BUDGET',
            'S_paused.SHUTDOWN = S.SHUTDOWN', 'S_done = $drive(S, 1500)',
            'S_done.COMPLETION = NORMAL', *DONE,
            'S_done.SHUTDOWN.RECEIVED = eps',
            '$drive(S_paused[.COMPLETION = NORMAL], 1500) = S_done',
            '$heap_owners($heap_graph(S_done), HOBJECT n_first) = 1',
            '$heap_owners($heap_graph(S_done), HOBJECT n_second) = 1',
        ],
    },
}

def run(selected):
    assert not selected or set(selected) <= CASES.keys(), 'unknown state case'
    cases = {name: case for name, case in CASES.items() if not selected or name in selected}
    out = Path(tempfile.mkdtemp(prefix='shutdown-state-review-', dir=ROOT / '.tools'))
    environment = dict(os.environ, LC_ALL='C', TZ='UTC')
    environment.pop('PHP_SPEC_SCRIPT_ENCODING', None)
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip()
    records = []
    print(out, flush=True)
    for name, case in cases.items():
        directory = out / name
        directory.mkdir()
        source = directory / 'source.php'
        source.write_text(case['source'])
        frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                           'extension=' + str(ROOT / '.tools/php-file.so'),
                           str(ROOT / 'frontend/worker.php')], directory / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
        try:
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted'], name
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'], name
            reply = None
            if 'eval' in case:
                child = case['eval'].encode()
                parsed_child = frontend.request({'op': 'parse-eval', 'id': '1', 'mode': 'eval',
                    'profile': 'cli-raw-85', 'source': base64.b64encode(child).decode()})
                assert parsed_child['accepted'], name
                checked_child = adapter.request({'op': 'check', 'ast': parsed_child['ast'], 'fixture': True})
                assert checked_child['ok'], name
                reply = '(SOURCE_ACCEPT 1 (' + str(list(child)) + ') ' + checked_child['fixture'] + ')'
        finally:
            frontend.close()
            adapter.close()
        fixture = directory / 'test.watsup'
        fixture.write_text(
            'dec $stage(pstate) : bool\ndef $stage(S) = true -- if ' + case['stage'] + '\n'
            'def $stage(S) = false -- otherwise\ndec $seek(pstate, nat) : pstate\n'
            + ('dec $seek_step(pstate) : pstate\n'
               'def $seek_step(S) = $drive_steps(S[.COMPLETION = NORMAL], 1) -- if S.COMPLETION = BUDGET\n'
               'def $seek_step(S) = $drive_steps(S, 1) -- if S.COMPLETION =/= BUDGET\n' if reply else '')
            +
            'def $seek(S, n) = S -- if $stage(S)\n'
            'def $seek(S, n) = $seek(' + ('$seek_step(S)' if reply else '$drive_steps(S[.COMPLETION = NORMAL], 1)')
            + ', $nabs($(n - 1))) -- if ~$stage(S) -- if $(n > 0) '
            '-- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET'
            + (' \\/ $shutdown_ready(S)' if reply else '') + '\n'
            + ('def $seek(S, n) = $seek($eval_resume(S, ' + reply + '), $nabs($(n - 1))) '
               '-- if S.COMPLETION = SOURCE_PENDING -- if $(n > 0) -- if $eval_response_valid(S, ' + reply + ')\n'
               if reply else '')
            + 'def $seek(S, n) = S -- if S.COMPLETION =/= NORMAL /\\ S.COMPLETION =/= BUDGET'
            + (' /\\ S.COMPLETION =/= SOURCE_PENDING /\\ ~$shutdown_ready(S)' if reply else '') + '\n'
            'dec $main() : bool\ndef $main() = true\n'
            '  -- if S_initial = $php_run(' + checked['fixture'] + ', 0, '
            + json.dumps(base64.b64encode(str(source).encode()).decode()) + ')\n'
            '  -- if S = $seek(S_initial[.COMPLETION = NORMAL], 2000)[.COMPLETION = NORMAL]\n'
            '  -- if ' + case['stage'] + '\n'
            + ''.join('  -- ' + ('' if clause.startswith('PhpStep:') else 'if ') + clause + '\n'
                      for clause in case['checks']))
        process = recorded([ROOT / 'tests/semantics/_build/default/numeric_runner.exe',
                            *modules, fixture], directory, 'model', environment, 120)
        passed = not process['timeout'] and process['exit'] == 0 and (
            directory / 'model.stdout').read_bytes() == b'true\n' and not (
            directory / 'model.stderr').read_bytes()
        records.append({'id': name, 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                        'assertions': len(case['checks']) + 3, 'process': process, 'passed': passed})
        print(name, passed, flush=True)
        if not passed:
            print((directory / 'model.stderr').read_text()[-2500:], flush=True)
            break
    report = {'revision': revision, 'selection': list(cases), 'records': records,
              'environment': {'LC_ALL': 'C', 'TZ': 'UTC', 'PHP_SPEC_SCRIPT_ENCODING_removed': True},
              'passed': len(records) == len(cases) and all(row['passed'] for row in records)}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return report['passed']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if run(args.case) else 1)
