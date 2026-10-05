#!/usr/bin/env python3
"""Independent source-reached Fiber continuation, ownership and admission checks."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

from exception_handler_review import recorded
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
SOURCES = {row['id']: row['source'] for row in json.loads(
    Path(__file__).with_name('fiber_review_cases.json').read_text())}
VALID = ['$call_current_valid(S)', '$call_frames_valid(S, S.FRAMES)',
         '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
DONE = ['S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
        'S_done.FRAMES = eps', 'S_done.CURRENT = eps', 'S_done.HELD = eps',
        'S_done.ACTIVEFIBER = eps', 'S_done.FIBERCALLERS = eps',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))']
PAUSE = ['S_paused = $drive(S, 0)', 'S_paused.COMPLETION = BUDGET',
         'S_paused.TODO = S.TODO', 'S_paused.FIBERCALLERS = S.FIBERCALLERS',
         'S_paused.OBJECTS = S.OBJECTS', 'S_paused.ALLOCATIONS = S.ALLOCATIONS',
         'S_done = $drive(S, 4000)',
         '$drive(S_paused[.COMPLETION = NORMAL], 4000) = S_done']

CASES = {
    'start-frame-original-buffer': {
        'source': '<?php $f=new Fiber(function(){echo func_num_args();return 7;});$f->start([3],4);echo $f->getReturn();',
        'stage': 'S.TODO = (ARGINFO_INVOKE pargcall) :: ptask_tail* -- if S.CURRENT = (pcallcontext) -- if $fiber_context_kind(S, pcallcontext)',
        'checks': [
            'S.ACTIVEFIBER = (n)', 'S.OBJECTS[n] = FIBER pfiber',
            'S.FIBERCALLERS = [pfibercaller]', 'pfibercaller.OBJECT = n',
            'pfibercaller.PREVIOUS = eps', 'pfibercaller.VM.GLOBAL',
            'pfibercaller.VM.TABLE = $empty_table()',
            'pfibercaller.API.KIND = eps',
            'pfibercaller.API.START = (pnamedargs_start)',
            'pnamedargs_start.SLOTS = [NAMED_SENT (KNOWN (PARRAY n_arg)), NAMED_SENT (KNOWN (PINT 4))]',
            'pnamedargs_start.NAMED = eps',
            'pcallcontext.ARGC = 2', 'pcallcontext.EXTRA = [KNOWN (PARRAY n_arg), KNOWN (PINT 4)]',
            'pcallcontext.WRAPPER = eps', 'pcallcontext.HOLES = eps',
            '$heap_owners($heap_graph(S), HARRAY n_arg) = 3',
            '$heap_count(HARRAY n_arg, $pools_nodes(S.POOLS)) = 1',
            '$heap_count(HARRAY n_arg, $fiber_api_nodes(pfibercaller.API)) = 1',
            '$heap_count(HARRAY n_arg, $call_context_roots(S.CURRENT)) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n) = 2',
            '$task_nodes(FIBER_FINISH n) = eps',
            '$task_nodes(FIBER_WAIT pfibercaller.API) = eps',
            '$fiber_context_valid(S, pcallcontext)',
            '~$fiber_context_valid(S, pcallcontext[.ARGC = 1])',
            '~$fiber_context_valid(S, pcallcontext[.EXTRA = eps])',
            '~$fiber_context_valid(S, pcallcontext[.LINE = 0])',
            '~$fiber_cache_valid(S, n, pfiber[.READY = false])',
            '~$fiber_callers_valid(S, (n), [pfibercaller[.PREVIOUS = (n)]], eps)',
            '~$fiber_callers_valid(S, (n), [pfibercaller[.API = pfibercaller.API[.SEQUENCE = S.FIBERSEQ]]], eps)',
            *VALID, *PAUSE, *DONE,
        ],
    },
    'parked-helper-stack-without-self-owner': {
        'source': SOURCES['review-fiber-helper-call-suspension'],
        'stage': 'S.ACTIVEFIBER = eps -- if $lookup(S.ENV, $ptascii("f")) = (n_cell) -- if S.STORE[n_cell] = DEFINED (POBJECT n) -- if S.OBJECTS[n] = FIBER pfiber -- if pfiber.STATUS = FIBER_SUSPENDED',
        'checks': [
            'S.FIBERCALLERS = eps', 'pfiber.VM = (pfibervm)',
            '~pfibervm.GLOBAL', 'pfibervm.CURRENT = (pcallcontext)',
            'pfibervm.FRAMES = [pframe_callback, pframe_base]',
            'pfibervm.TODO = (FIBER_CONTINUE pfiberapi) :: ptask_saved*',
            'pfiberapi.OBJECT = n', 'pfiberapi.SENT = (PINT 4)',
            'pfiberapi.SEQUENCE = pfiber.SEQUENCE',
            '$task_nodes(FIBER_CONTINUE pfiberapi) = eps',
            '~((HOBJECT n) <- $node_children(S, HOBJECT n))',
            '$fiber_vm_valid(S, pfibervm, (n), eps)',
            '~$fiber_vm_valid(S, pfibervm[.GLOBAL = true], (n), eps)',
            '~$fiber_record_valid(S, n, pfiber[.SEQUENCE = S.FIBERSEQ])',
            '~$fiber_record_valid(S, n, pfiber[.VM = (pfibervm[.TODO = ptask_saved*])])',
            'S_view = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n)]',
            '$fiber_continue_valid(S_view, pfiberapi)',
            '~$fiber_continue_valid(S_view, pfiberapi[.OBJECT = |S.OBJECTS|])',
            '~$fiber_continue_valid(S_view, pfiberapi[.KIND = (INTRINSIC_FIBER_RESUME)])',
            *VALID, *PAUSE, *DONE,
        ],
    },
    'nested-waiting-caller-chain': {
        'source': SOURCES['review-fiber-nested-running-current'],
        'stage': 'S.FIBERCALLERS = [pfibercaller_inner, pfibercaller_outer] -- if S.CURRENT = (pcallcontext) -- if $fiber_context_kind(S, pcallcontext)',
        'checks': [
            'S.ACTIVEFIBER = (n_inner)', 'pfibercaller_inner.OBJECT = n_inner',
            'pfibercaller_inner.PREVIOUS = (n_outer)',
            'pfibercaller_outer.OBJECT = n_outer', 'pfibercaller_outer.PREVIOUS = eps',
            '~pfibercaller_inner.VM.GLOBAL', 'pfibercaller_outer.VM.GLOBAL',
            'S.OBJECTS[n_outer] = FIBER pfiber_outer',
            'S.OBJECTS[n_inner] = FIBER pfiber_inner',
            'pfiber_outer.STATUS = FIBER_RUNNING', 'pfiber_inner.STATUS = FIBER_RUNNING',
            'pfiber_outer.VM = eps', 'pfiber_inner.VM = eps',
            'S.TODO = [NAMED_PREFLIGHT pcallcontext.FUNCTION 0]',
            '$call_task_valid(S, NAMED_PREFLIGHT pcallcontext.FUNCTION 0)',
            '~$call_task_valid(S[.ORIGIN = eps], NAMED_PREFLIGHT pcallcontext.FUNCTION 0)',
            '~$call_task_valid(S[.ACTIVEFIBER = eps], NAMED_PREFLIGHT pcallcontext.FUNCTION 0)',
            '~$call_task_valid(S[.CURRENT = (pcallcontext[.LINE = 0])], NAMED_PREFLIGHT pcallcontext.FUNCTION 0)',
            '~$call_task_valid(S[.TODO = [NAMED_PREFLIGHT pcallcontext.FUNCTION 1]], NAMED_PREFLIGHT pcallcontext.FUNCTION 1)',
            '$getclass_live_object(S, n_inner)', '$getclass_live_object(S, n_outer)',
            '~$getclass_live_object(S[.ALLOCATIONS = eps], n_inner)',
            '~$getclass_live_object(S, |S.OBJECTS|)',
            'pfibercaller_inner.VM.TODO = (FIBER_WAIT pfibercaller_inner.API) :: ptask_waiting*',
            '$fiber_callers_valid(S, (n_inner), S.FIBERCALLERS, eps)',
            '~$fiber_callers_valid(S, (n_inner), [pfibercaller_inner[.PREVIOUS = eps], pfibercaller_outer], eps)',
            '~$fiber_callers_valid(S, (n_inner), [pfibercaller_inner[.PREVIOUS = (n_inner)], pfibercaller_outer], eps)',
            '~$fiber_callers_valid(S, (n_outer), S.FIBERCALLERS, eps)',
            '$call_descriptors_local_valid(S)', '$fiber_state_valid(S)',
            *VALID, *PAUSE, *DONE,
        ],
    },
    'resume-frame-owns-sent-array': {
        'source': SOURCES['review-fiber-resume-buffer-keeps-reference-shared'],
        'stage': 'S.TODO = (FIBER_CONTINUE pfiberapi) :: ptask_tail* -- if S.RESULT = KNOWN (PARRAY n_arg)',
        'checks': [
            'S.ACTIVEFIBER = (n)', 'S.OBJECTS[n] = FIBER pfiber',
            'pfiber.STATUS = FIBER_RUNNING', 'pfiber.VM = eps',
            'S.FIBERCALLERS = [pfibercaller]',
            'pfibercaller.API.KIND = (INTRINSIC_FIBER_RESUME)',
            'pfibercaller.API.SENT = (PARRAY n_arg)',
            'pfiberapi.KIND = (INTRINSIC_FIBER_SUSPEND)', 'pfiberapi.SENT = eps',
            '$(pfiberapi.SEQUENCE < pfibercaller.API.SEQUENCE)',
            '$fiber_api_nodes(pfibercaller.API) = [HOBJECT n, HARRAY n_arg]',
            '$task_nodes(FIBER_CONTINUE pfiberapi) = eps',
            '$heap_owners($heap_graph(S), HARRAY n_arg) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n) = 2',
            '~$fiber_continue_valid(S, pfiberapi[.SEQUENCE = pfiber.SEQUENCE])',
            '~$fiber_continue_valid(S, pfiberapi[.SENT = (PNULL)])',
            *VALID, *PAUSE, *DONE,
            'S_done.EVENTS = [OUTPUT $ptascii("9"), OUTPUT $ptascii("/"), OUTPUT $ptascii("9"), OUTPUT $ptascii("|"), OUTPUT $ptascii("6")]',
        ],
    },
    'frozen-private-selection-after-maker-return': {
        'source': SOURCES['review-fiber-private-callback-cached-permission'],
        'stage': 'S.TODO = (FIBER_ARGS pfiberstart) :: ptask_tail* -- if S.CURRENT = eps',
        'checks': [
            'n = pfiberstart.OBJECT', 'S.OBJECTS[n] = FIBER pfiber',
            'pfiber.STATUS = FIBER_INIT', 'pfiber.READY',
            'pfiber.CALL = (pconfigcall)', 'pfiber.PRODUCER = (pshutdownproducer)',
            'pfiber.CAPTURE = (pmethodcapture)',
            'S.FRAMES = eps', 'S.ACTIVEFIBER = eps', 'S.FIBERCALLERS = eps',
            '$fiber_cache_valid(S, n, pfiber)',
            '~$fiber_cache_valid(S, n, pfiber[.TARGET = eps])',
            '~$fiber_cache_valid(S, n, pfiber[.CALL = (pconfigcall[.OWNER = (|S.OBJECTS|)])])',
            '~$fiber_cache_valid(S, n, pfiber[.CALL = (pconfigcall[.SENT = eps])])',
            '~$fiber_cache_valid(S, n, pfiber[.RAW = PNULL])',
            *VALID, *PAUSE, *DONE,
        ],
    },
    'uncaught-callback-crosses-root-once': {
        'source': SOURCES['review-fiber-callback-trace-includes-start-buffer'],
        'stage': 'S.TODO = [THROW_SEARCH n_throwable, FIBER_FINISH n]',
        'checks': [
            'S.ACTIVEFIBER = (n)', 'S.CURRENT = eps', 'S.FRAMES = eps',
            'S.OBJECTS[n] = FIBER pfiber', 'pfiber.STATUS = FIBER_RUNNING',
            'S.FIBERCALLERS = [pfibercaller]',
            'pfibercaller.API.START = (pnamedargs_start)',
            'pnamedargs_start.SLOTS = [NAMED_SENT (KNOWN (PSTRING $ptascii("held")))]',
            'pnamedargs_start.NAMED = eps',
            '$throwable_member(S, n_throwable)',
            '$call_task_valid(S, FIBER_FINISH n)',
            '~$call_task_valid(S, FIBER_FINISH (|S.OBJECTS|))',
            *VALID, *PAUSE, *DONE,
            'S_done.OBJECTS[n] = FIBER pfiber_done',
            'pfiber_done.STATUS = FIBER_TERMINATED', 'pfiber_done.FAILED',
            'pfiber_done.RAW = PNULL', 'pfiber_done.CALL = eps',
            'pfiber_done.TARGET = eps', 'pfiber_done.ENTRY = eps', 'pfiber_done.VM = eps',
        ],
    },
    'interleaved-transfer-stamps-are-distinct': {
        'source': SOURCES['review-fiber-interleaved-foreach-cursors'],
        'stage': 'S.ACTIVEFIBER = eps -- if $lookup(S.ENV, $ptascii("a")) = (n_cell_a) -- if S.STORE[n_cell_a] = DEFINED (POBJECT n_a) -- if S.OBJECTS[n_a] = FIBER pfiber_a -- if pfiber_a.STATUS = FIBER_SUSPENDED -- if $lookup(S.ENV, $ptascii("b")) = (n_cell_b) -- if S.STORE[n_cell_b] = DEFINED (POBJECT n_b) -- if S.OBJECTS[n_b] = FIBER pfiber_b -- if pfiber_b.STATUS = FIBER_SUSPENDED',
        'checks': [
            'S.FIBERCALLERS = eps', 'n_a =/= n_b',
            'pfiber_a.SEQUENCE =/= pfiber_b.SEQUENCE',
            'pfiber_a.VM = (pfibervm_a)',
            'pfibervm_a.TODO = (FIBER_CONTINUE pfiberapi_a) :: ptask_saved*',
            'pfiberapi_a.SEQUENCE = pfiber_a.SEQUENCE',
            '$fiber_record_valid(S, n_a, pfiber_a)',
            '$fiber_record_valid(S, n_b, pfiber_b)',
            'S_bad = $fiber_put(S, n_a, pfiber_a[.SEQUENCE = pfiber_b.SEQUENCE][.VM = (pfibervm_a[.TODO = (FIBER_CONTINUE pfiberapi_a[.SEQUENCE = pfiber_b.SEQUENCE]) :: ptask_saved*])])',
            '~$fiber_state_valid(S_bad)', '~$call_descriptors_valid(S_bad)',
            *VALID, *PAUSE, *DONE,
        ],
    },
    'dynamic-new-certificate-survives-marker-retirement': {
        'source': SOURCES['review-fiber-dynamic-new-cache-survives-class-variable-write'],
        'stage': 'S.TODO = (FIBER_ARGS pfiberstart) :: ptask_tail* -- if S.CURRENT = eps',
        'checks': [
            'n = pfiberstart.OBJECT', 'S.OBJECTS[n] = FIBER pfiber',
            'pfiber.STATUS = FIBER_INIT', 'pfiber.READY',
            'pfiber.BIRTH = (pdynamicnew)',
            'pdynamicnew.CLASS = $ptascii("Fiber")',
            'pdynamicnew.SOURCE = PSTRING $ptascii("Fiber")',
            '$lookup(S.ENV, $ptascii("class")) = (n_class)',
            'S.STORE[n_class] = DEFINED (PSTRING $ptascii("stdClass"))',
            'S.ACTIVEFIBER = eps', 'S.FIBERCALLERS = eps', 'S.FRAMES = eps',
            '$dynamic_new_find(S, S.TODO, pdynamicnew.SITE) = eps',
            '$fiber_cache_valid(S, n, pfiber)',
            '~$fiber_cache_valid(S, n, pfiber[.BIRTH = eps])',
            '~$fiber_cache_valid(S, n, pfiber[.BIRTH = (pdynamicnew[.CLASS = $ptascii("stdClass")])])',
            '~$fiber_cache_valid(S, n, pfiber[.BIRTH = (pdynamicnew[.SOURCE = PSTRING $ptascii("Exception")])])',
            '~$fiber_cache_valid(S, n, pfiber[.BIRTH = (pdynamicnew[.SITE = pfiberstart.SITE])])',
            '~$fiber_cache_valid(S, n, pfiber[.BIRTH = (pdynamicnew[.LINE = $(pdynamicnew.LINE + 1)])])',
            *VALID, *PAUSE, *DONE,
            'S_done.EVENTS = [OUTPUT $ptascii("A"), OUTPUT $ptascii("s"), OUTPUT $ptascii("|"), OUTPUT eps, OUTPUT $ptascii("|"), OUTPUT $ptascii("7")]',
            'S_done.OBJECTS[n] = FIBER pfiber_done',
            'pfiber_done.BIRTH = eps',
        ],
    },
}


# Complementary author checks; independent cases above retain their own cuts.
CASES.update({'author-resumed-mask-and-shared-ini': {'source': '<?php\n'
                                                  'error_reporting(123);\n'
                                                  '$f = new Fiber(function () {\n'
                                                  "    echo 'I', error_reporting(), '/', "
                                                  "ini_get('error_reporting'), '|';\n"
                                                  '    error_reporting(456);\n'
                                                  '    Fiber::suspend();\n'
                                                  "    echo 'R', error_reporting(), '/', "
                                                  "ini_get('error_reporting'), '|';\n"
                                                  '    return 9;\n'
                                                  '});\n'
                                                  '$f->start();\n'
                                                  "echo 'O', error_reporting(), '/', "
                                                  "ini_get('error_reporting'), '|';\n"
                                                  'error_reporting(789);\n'
                                                  '$f->resume();\n'
                                                  "echo 'F', error_reporting(), '/', "
                                                  "ini_get('error_reporting');\n",
                                        'stage': 'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
                                                 '-- if pconfigcall.KIND = INTRINSIC_ERROR_REPORTING -- '
                                                 'if pconfigcall.SENT = eps -- if S.REPORTING = 456 -- '
                                                 'if S.REPORTINGINI = $ptascii("789")',
                                        'checks': ['S.ACTIVEFIBER = (n)',
                                                   'S.OBJECTS[n] = FIBER pfiber',
                                                   'pfiber.STATUS = FIBER_RUNNING',
                                                   'pfiber.VM = eps',
                                                   'S.CURRENT = (pcallcontext)',
                                                   '$fiber_context_valid(S, pcallcontext)',
                                                   'S.FIBERCALLERS = [pfibercaller]',
                                                   'pfibercaller.OBJECT = n',
                                                   'pfibercaller.API.KIND = (INTRINSIC_FIBER_RESUME)',
                                                   'pfibercaller.API.SENT = eps',
                                                   'pfibercaller.API.SEQUENCE = pfiber.SEQUENCE',
                                                   'pfibercaller.VM.GLOBAL',
                                                   'pfibercaller.VM.TABLE = $empty_table()',
                                                   'pfibercaller.VM.REPORTING = 789',
                                                   'pfibercaller.VM.SILENCES = eps',
                                                   'S.SILENCES = eps',
                                                   'S.REPORTINGMODIFIED',
                                                   'pfibervm_current = $fiber_vm(S)',
                                                   'pfibervm_current.REPORTING = 456',
                                                   'pfibervm_current.SILENCES = eps',
                                                   'S_caller = $fiber_vm_restore(S, pfibercaller.VM)',
                                                   'S_caller.REPORTING = 789',
                                                   'S_caller.REPORTINGINI = $ptascii("789")',
                                                   'S_caller.REPORTINGMODIFIED = S.REPORTINGMODIFIED',
                                                   'S_changed = $fiber_vm_restore(S[.REPORTINGINI = '
                                                   '$ptascii("321")], pfibercaller.VM)',
                                                   'S_changed.REPORTING = 789',
                                                   'S_changed.REPORTINGINI = $ptascii("321")',
                                                   '$config_invoke_valid(S, pconfigcall)',
                                                   '~$config_invoke_valid(S, pconfigcall[.LINE = '
                                                   '$(pconfigcall.LINE + 1)])',
                                                   '~$fiber_context_valid(S, pcallcontext[.LINE = 0])',
                                                   '$call_current_valid(S)',
                                                   '$call_frames_valid(S, S.FRAMES)',
                                                   '$call_descriptors_valid(S)',
                                                   '$heap_valid($heap_graph(S))',
                                                   'S_paused = $drive(S, 0)',
                                                   'S_paused.COMPLETION = BUDGET',
                                                   'S_paused.REPORTING = S.REPORTING',
                                                   'S_paused.REPORTINGINI = S.REPORTINGINI',
                                                   'S_paused.ERRORHANDLER = S.ERRORHANDLER',
                                                   'S_paused.ERRORHANDLERS = S.ERRORHANDLERS',
                                                   'S_paused.FIBERCALLERS = S.FIBERCALLERS',
                                                   'S_paused.OBJECTS = S.OBJECTS',
                                                   'S_paused.ALLOCATIONS = S.ALLOCATIONS',
                                                   'S_paused.FIBERSEQ = S.FIBERSEQ',
                                                   'S_done = $drive(S, 4000)',
                                                   '$drive(S_paused[.COMPLETION = NORMAL], 4000) = '
                                                   'S_done',
                                                   'S_done.COMPLETION = NORMAL',
                                                   'S_done.TODO = eps',
                                                   'S_done.FRAMES = eps',
                                                   'S_done.CURRENT = eps',
                                                   'S_done.HELD = eps',
                                                   'S_done.ACTIVEFIBER = eps',
                                                   'S_done.FIBERCALLERS = eps',
                                                   '$call_descriptors_valid(S_done)',
                                                   '$heap_valid($heap_graph(S_done))',
                                                   'S_done.REPORTING = 789',
                                                   'S_done.REPORTINGINI = $ptascii("789")',
                                                   'S_done.OBJECTS[n] = FIBER pfiber_done',
                                                   'pfiber_done.STATUS = FIBER_TERMINATED',
                                                   'pfiber_done.VALUE = PINT 9',
                                                   'pfiber_done.VM = eps',
                                                   'pfiber_done.CALL = eps']},
 'author-parked-handler-keeps-live-replacement': {'source': '<?php\n'
                                                            'function '
                                                            'fiber_review_first_handler281($level, '
                                                            '$message) {\n'
                                                            "    echo 'H1|';\n"
                                                            "    Fiber::suspend('wait');\n"
                                                            "    echo 'R1|';\n"
                                                            '    return true;\n'
                                                            '}\n'
                                                            'function '
                                                            'fiber_review_second_handler281($level, '
                                                            "$message) { echo 'H2|'; return true; }\n"
                                                            "set_error_handler('fiber_review_first_handler281');\n"
                                                            '$f = new Fiber(function () { echo $inside; '
                                                            'return 3; });\n'
                                                            "echo $f->start(), '|';\n"
                                                            'echo '
                                                            "(int)(set_error_handler('fiber_review_second_handler281') "
                                                            "=== null), '|';\n"
                                                            '$f->resume();\n'
                                                            'echo $outside;\n'
                                                            'restore_error_handler();\n'
                                                            'restore_error_handler();\n'
                                                            'echo $f->getReturn();\n',
                                                  'stage': 'S.TODO = (CONFIG_INVOKE pconfigcall) :: '
                                                           'ptask_tail* -- if pconfigcall.KIND = '
                                                           'INTRINSIC_FIBER_RESUME -- if '
                                                           'pconfigcall.OWNER = (n) -- if S.OBJECTS[n] '
                                                           '= FIBER pfiber -- if pfiber.STATUS = '
                                                           'FIBER_SUSPENDED',
                                                  'checks': ['S.ACTIVEFIBER = eps',
                                                             'S.FIBERCALLERS = eps',
                                                             'S.CURRENT = eps',
                                                             'S.FRAMES = eps',
                                                             'S.ERRORHANDLER.CALLBACK = (PSTRING '
                                                             '$ptascii("fiber_review_second_handler281"))',
                                                             'S.ERRORHANDLERS = '
                                                             '[perrorhandler_disabled, '
                                                             'perrorhandler_initial]',
                                                             'perrorhandler_disabled.CALLBACK = eps',
                                                             'perrorhandler_initial.CALLBACK = eps',
                                                             'pfiber.VM = (pfibervm)',
                                                             '~pfibervm.GLOBAL',
                                                             'pfibervm.CURRENT = (pcallcontext_handler)',
                                                             'pfibervm.FRAMES = [pframe_callback, '
                                                             'pframe_base]',
                                                             'pframe_callback.TODO = '
                                                             '(ERROR_HANDLER_RESULT perrorcall) :: '
                                                             'ptask_callback*',
                                                             'perrorcall.CALLBACK = PSTRING '
                                                             '$ptascii("fiber_review_first_handler281")',
                                                             'perrorcall.RESUME = ERROR_READ_RESULT '
                                                             'perrorread',
                                                             'perrorread.NAME = $ptascii("inside")',
                                                             'pfibervm.TODO = (FIBER_CONTINUE '
                                                             'pfiberapi) :: ptask_handler*',
                                                             'pfiberapi.SENT = (PSTRING '
                                                             '$ptascii("wait"))',
                                                             'pfiberapi.OBJECT = n',
                                                             'pfiberapi.SEQUENCE = pfiber.SEQUENCE',
                                                             'pfiber.RAW = POBJECT n_callback',
                                                             '$heap_owners($heap_graph(S), HOBJECT '
                                                             'n_callback) = 2',
                                                             '$heap_owners($heap_graph(S), HOBJECT n) = '
                                                             '2',
                                                             '~((HOBJECT n) <- $node_children(S, '
                                                             'HOBJECT n))',
                                                             '$fiber_vm_valid(S, pfibervm, (n), eps)',
                                                             'S_view = $fiber_vm_restore(S, '
                                                             'pfibervm)[.ACTIVEFIBER = (n)]',
                                                             'S_view.ERRORHANDLER = S.ERRORHANDLER',
                                                             'S_view.ERRORHANDLERS = S.ERRORHANDLERS',
                                                             '$error_context_valid(S_view, '
                                                             'pcallcontext_handler)',
                                                             '~$error_context_valid(S_view, '
                                                             'pcallcontext_handler[.ARGC = 2])',
                                                             '~$error_context_valid(S_view, '
                                                             'pcallcontext_handler[.LINE = 0])',
                                                             '$fiber_continue_valid(S_view, pfiberapi)',
                                                             '~$fiber_continue_valid(S_view, '
                                                             'pfiberapi[.OBJECT = |S.OBJECTS|])',
                                                             '$call_current_valid(S)',
                                                             '$call_frames_valid(S, S.FRAMES)',
                                                             '$call_descriptors_valid(S)',
                                                             '$heap_valid($heap_graph(S))',
                                                             'S_paused = $drive(S, 0)',
                                                             'S_paused.COMPLETION = BUDGET',
                                                             'S_paused.REPORTING = S.REPORTING',
                                                             'S_paused.REPORTINGINI = S.REPORTINGINI',
                                                             'S_paused.ERRORHANDLER = S.ERRORHANDLER',
                                                             'S_paused.ERRORHANDLERS = S.ERRORHANDLERS',
                                                             'S_paused.FIBERCALLERS = S.FIBERCALLERS',
                                                             'S_paused.OBJECTS = S.OBJECTS',
                                                             'S_paused.ALLOCATIONS = S.ALLOCATIONS',
                                                             'S_paused.FIBERSEQ = S.FIBERSEQ',
                                                             'S_done = $drive(S, 4000)',
                                                             '$drive(S_paused[.COMPLETION = NORMAL], '
                                                             '4000) = S_done',
                                                             'S_done.COMPLETION = NORMAL',
                                                             'S_done.TODO = eps',
                                                             'S_done.FRAMES = eps',
                                                             'S_done.CURRENT = eps',
                                                             'S_done.HELD = eps',
                                                             'S_done.ACTIVEFIBER = eps',
                                                             'S_done.FIBERCALLERS = eps',
                                                             '$call_descriptors_valid(S_done)',
                                                             '$heap_valid($heap_graph(S_done))',
                                                             'S_done.ERRORHANDLER.CALLBACK = eps',
                                                             'S_done.ERRORHANDLERS = eps',
                                                             'S_done.OBJECTS[n] = FIBER pfiber_done',
                                                             'pfiber_done.STATUS = FIBER_TERMINATED',
                                                             'pfiber_done.VALUE = PINT 3',
                                                             '$heap_owners($heap_graph(S_done), HOBJECT '
                                                             'n_callback) = 0',
                                                             '~((HOBJECT n_callback) <- '
                                                             'S_done.ALLOCATIONS)']}})


# Independent guards for deferred defaults and callback entry errors.
CASES.update({
    'deferred-named-default-uses-mapped-start-buffer': {
        'source': SOURCES['review-fiber-const-named-holes-defaults-and-entry-errors'],
        'stage': 'S.TODO = [NAMED_DEFAULT_BIND porigin 0] -- if S.CURRENT = (pcallcontext) -- if $fiber_context_kind(S, pcallcontext)',
        'checks': [
            'S.ACTIVEFIBER = (n)',
            'S.OBJECTS[n] = FIBER pfiber',
            'pfiber.STATUS = FIBER_RUNNING',
            'pfiber.VM = eps',
            'pfiber.ENTRY = (pnamedargs_entry)',
            'pnamedargs_entry.SLOTS = [NAMED_HOLE, NAMED_HOLE, NAMED_SENT (KNOWN (PSTRING $ptascii("Z")))]',
            'pnamedargs_entry.NAMED = eps',
            'S.FIBERCALLERS = [pfibercaller]',
            'pfibercaller.OBJECT = n',
            'pfibercaller.API.START = (pnamedargs_start)',
            'pnamedargs_start.SLOTS = eps',
            'pnamedargs_start.NAMED = [($ptascii("c"), KNOWN (PSTRING $ptascii("Z")))]',
            '$fiber_api_valid(S, pfibercaller.API)',
            '~$fiber_api_valid(S, pfibercaller.API[.START = (pnamedargs_start[.NAMED = [($ptascii("C"), KNOWN (PSTRING $ptascii("Z")))]])])',
            '~$fiber_api_valid(S, pfibercaller.API[.START = (pnamedargs_start[.NAMED = eps])])',
            'pcallcontext.FUNCTION = porigin',
            'pcallcontext.ARGC = 3',
            'pcallcontext.PARAMS = [$ptascii("a"), $ptascii("b"), $ptascii("c")]',
            'pcallcontext.HOLES = [0, 1]',
            'pcallcontext.EXTRA = eps',
            'pcallcontext.NAMED = eps',
            'pcallcontext.WRAPPER = eps',
            'pcallcontext.CALLSITE = eps',
            'pcallcontext.LINE = $(-1)',
            '~$named_defined(S, $ptascii("a"))',
            '~$named_defined(S, $ptascii("b"))',
            '$lookup(S.ENV, $ptascii("c")) = (n_c)',
            'S.STORE[n_c] = DEFINED (PSTRING $ptascii("Z"))',
            '$target_function(S, pcallcontext.TARGET) = (pfunction)',
            '$default_at(pfunction.DEFAULTS, 0) = (pdefault)',
            'pdefault.KIND = PDDEFERRED',
            '$default_cache_at(S.DEFAULTCACHE, pdefault.ORIGIN) = eps',
            'S.RESULT = KNOWN (PSTRING $ptascii("A"))',
            'S.CONSTCONTEXT =/= eps',
            'S.ORIGIN = ($default_parameter_origin(S, porigin, 0))',
            '$named_call_shape(S, pcallcontext.TARGET, eps) = pnamedargs_entry',
            '$named_preflight_stage(S, porigin, 0)',
            '~$named_preflight_stage(S, porigin, 4)',
            '$named_bind_valid(S, porigin, 0)',
            '$call_task_valid(S, NAMED_DEFAULT_BIND porigin 0)',
            '~$call_task_valid(S[.ORIGIN = eps], NAMED_DEFAULT_BIND porigin 0)',
            '~$call_task_valid(S[.ACTIVEFIBER = eps], NAMED_DEFAULT_BIND porigin 0)',
            '~$call_task_valid(S[.CURRENT = (pcallcontext[.LINE = 0])], NAMED_DEFAULT_BIND porigin 0)',
            '~$fiber_context_valid(S, pcallcontext[.HOLES = eps])',
            '~$fiber_context_valid(S, pcallcontext[.ARGC = 2])',
            '$fiber_api_nodes(pfibercaller.API) = [HOBJECT n]',
            '$heap_owners($heap_graph(S), HOBJECT n) = 2',
            '$task_nodes(FIBER_FINISH n) = eps',
            *VALID,
            *PAUSE,
            *DONE,
            'S_done.OBJECTS[n] = FIBER pfiber_done',
            'pfiber_done.STATUS = FIBER_TERMINATED',
            '~pfiber_done.FAILED',
            'pfiber_done.VALUE = PINT 7',
            'pfiber_done.RAW = PNULL',
            'pfiber_done.CALL = eps',
            'pfiber_done.TARGET = eps',
            'pfiber_done.ENTRY = eps',
            'pfiber_done.VM = eps',
            '$lookup(S_done.ENV, $ptascii("missing")) = (n_missing_cell)',
            'S_done.STORE[n_missing_cell] = DEFINED (POBJECT n_missing)',
            'S_done.OBJECTS[n_missing] = FIBER pfiber_missing',
            'pfiber_missing.STATUS = FIBER_TERMINATED',
            'pfiber_missing.FAILED',
            'pfiber_missing.VALUE = PNULL',
            'pfiber_missing.CALL = eps',
            '$lookup(S_done.ENV, $ptascii("duplicate")) = (n_duplicate_cell)',
            'S_done.STORE[n_duplicate_cell] = DEFINED (POBJECT n_duplicate)',
            'S_done.OBJECTS[n_duplicate] = FIBER pfiber_duplicate',
            'pfiber_duplicate.STATUS = FIBER_TERMINATED',
            'pfiber_duplicate.FAILED',
            'pfiber_duplicate.VALUE = PNULL',
            'pfiber_duplicate.CALL = eps',
        ],
    },
    'entry-name-error-retains-caller-provenance': {
        'source': SOURCES['review-fiber-entry-name-error-caller-provenance'],
        'stage': 'S.TODO = [FIBER_ENTER n pnamedargs, FIBER_FINISH n]',
        'checks': [
            'S.ACTIVEFIBER = (n)',
            'S.CURRENT = eps',
            'S.FRAMES = eps',
            'S.EVENTS = eps',
            'S.OBJECTS[n] = FIBER pfiber',
            'pfiber.STATUS = FIBER_RUNNING',
            'pfiber.ENTRY = (pnamedargs)',
            'pnamedargs.SLOTS = eps',
            'pnamedargs.NAMED = [($ptascii("missing"), KNOWN (PINT 1))]',
            'S.FIBERCALLERS = [pfibercaller]',
            'pfibercaller.OBJECT = n',
            'pfibercaller.API.KIND = eps',
            'pfibercaller.API.START = (pnamedargs)',
            'pfibercaller.API.LINE = 4',
            '$fiber_api_valid(S, pfibercaller.API)',
            '~$fiber_api_valid(S, pfibercaller.API[.START = (pnamedargs[.NAMED = [($ptascii("Missing"), KNOWN (PINT 1))]])])',
            '~$fiber_api_valid(S, pfibercaller.API[.START = (pnamedargs[.NAMED = eps])])',
            '$fiber_enter_valid(S, n, pnamedargs)',
            '~$fiber_enter_valid(S[.ACTIVEFIBER = eps], n, pnamedargs)',
            '~$fiber_enter_valid(S, n, pnamedargs[.NAMED = eps])',
            '~$call_descriptors_valid(S[.FIBERCALLERS = [pfibercaller[.API = pfibercaller.API[.LINE = 0]]]])',
            '~$call_descriptors_valid(S[.FIBERCALLERS = [pfibercaller[.API = pfibercaller.API[.KIND = (INTRINSIC_FIBER_RESUME)]]]])',
            '$task_nodes(FIBER_ENTER n pnamedargs) = eps',
            '$task_nodes(FIBER_FINISH n) = eps',
            '$fiber_api_nodes(pfibercaller.API) = [HOBJECT n]',
            '$heap_owners($heap_graph(S), HOBJECT n) = 2',
            *VALID,
            'S_error_reached = $drive_steps(S, 1)',
            'S_error_reached.COMPLETION = BUDGET',
            'S_error = S_error_reached[.COMPLETION = NORMAL]',
            'S_error.TODO = [THROW_SEARCH n_error, FIBER_FINISH n]',
            'S_error.CURRENT = eps',
            'S_error.FRAMES = eps',
            'S_error.FIBERCALLERS = S.FIBERCALLERS',
            'S_error.OBJECTS[n_error] = THROWABLE pthrowable',
            'pthrowable.KIND = "Error"',
            'pthrowable.ORIGIN = (pfibercaller.API.SITE)',
            'pthrowable.FILEORIGIN = (pfibercaller.API.SITE)',
            '$throwable_field(S_error, n_error, "line") = PINT 4',
            '$throwable_field(S_error, n_error, "file") = PSTRING $call_sourcefile(S.FILES, pfibercaller.API.SITE)',
            '$throwable_field(S_error, n_error, "message") = PSTRING $ptascii("Unknown named parameter $missing")',
            '$heap_owners($heap_graph(S_error), HOBJECT n_error) = 1',
            '$call_descriptors_valid(S_error)',
            '$heap_valid($heap_graph(S_error))',
            *PAUSE,
            '$drive(S_error, 4000) = S_done',
            *DONE,
            'S_done.OBJECTS[n] = FIBER pfiber_done',
            'pfiber_done.STATUS = FIBER_TERMINATED',
            'pfiber_done.FAILED',
            'pfiber_done.CALL = eps',
            'pfiber_done.RAW = PNULL',
        ],
    },
})


# Actual-parent Generator ownership stays on the active machine.
CASES.update({
    'separate-running-generator-keeps-parked-fiber-admission': {
        'source': SOURCES['review-fiber-separate-generator-running-with-parked-fiber'],
        'stage': 'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* -- if pconfigcall.KIND = INTRINSIC_FIBER_SUSPENDED -- if pconfigcall.OWNER = (n_fiber) -- if S.CURRENT = (pcallcontext) -- if $generator_context_operation(S, pcallcontext) = (pgeneratorop)',
        'checks': [
            'S.ACTIVEFIBER = eps', 'S.FIBERCALLERS = eps',
            'S.OBJECTS[n_fiber] = FIBER pfiber',
            'pfiber.STATUS = FIBER_SUSPENDED', 'pfiber.VM = (pfibervm)',
            'pfibervm.CURRENT = (pcallcontext_fiber)',
            'pfibervm.FRAMES = [pframe_base]',
            'pframe_base.TODO = [FIBER_FINISH n_fiber]',
            'pfibervm.TODO = (FIBER_CONTINUE pfiberapi) :: ptask_saved*',
            'pfiberapi.OBJECT = n_fiber', 'pfiberapi.SENT = (PSTRING $ptascii("S"))',
            'pfiberapi.SEQUENCE = pfiber.SEQUENCE',
            'n_generator = pgeneratorop.OBJECT', 'n_generator =/= n_fiber',
            'pgeneratorop.NAME = "current"', 'pgeneratorop.LOOP = eps',
            'S.OBJECTS[n_generator] = GENERATOR pgenerator',
            'pgenerator.PHASE = GENERATOR_RUNNING', 'pgenerator.FRAME = eps',
            'pgenerator.CLOSURE = eps', 'pgenerator.FUNCTION = pcallcontext.FUNCTION',
            'S.FRAMES = [pframe_main]',
            'pframe_main.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask_main*',
            'pframe_main.LOCALS = eps', 'pframe_main.CONTEXT = eps',
            '$generator_active(S)', '$generator_resume_ids(S.TODO) = eps',
            '$generator_saved_ids(S.FRAMES) = [n_generator]',
            '$generator_state_valid(S)', '$fiber_state_valid(S)',
            '~$fiber_transfer_domain(S)',
            '$config_nodes(pconfigcall) = [HOBJECT n_fiber]',
            '$heap_owners($heap_graph(S), HOBJECT n_fiber) = 3',
            '$heap_owners($heap_graph(S), HOBJECT n_generator) = 2',
            '~((HOBJECT n_fiber) <- $fiber_vm_nodes(pfibervm))',
            '$task_nodes(FIBER_CONTINUE pfiberapi) = eps',
            '$task_nodes(GENERATOR_RESUME pgeneratorop) = [HOBJECT n_generator]',
            'S_view = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)][.FIBERCALLERS = eps][.COMPLETION = NORMAL]',
            '$generator_objects_valid(S_view, S_view.ALLOCATIONS)',
            '~$generator_owners_valid(S_view)', '~$generator_state_valid(S_view)',
            '$call_descriptors_local_valid(S_view)',
            '$fiber_vm_valid(S, pfibervm, (n_fiber), eps)',
            '~$generator_owners_valid(S[.FRAMES = eps])',
            '~$call_descriptors_valid(S[.FRAMES = eps])',
            '~$generator_owners_valid(S[.FRAMES = [pframe_main, pframe_main]])',
            'pfibervm_current_forged = pfibervm[.TODO = (GENERATOR_RESUME pgeneratorop) :: pfibervm.TODO]',
            '$generator_flat_tasks(pfibervm_current_forged.TODO)',
            '$generator_resume_ids(pfibervm_current_forged.TODO) = [n_generator]',
            '~$fiber_vm_valid(S, pfibervm_current_forged, (n_fiber), eps)',
            'pfibervm_frame_forged = pfibervm[.FRAMES = [pframe_base[.TODO = (GENERATOR_RESUME pgeneratorop) :: pframe_base.TODO]]]',
            '$generator_flat_frames(pfibervm_frame_forged.FRAMES)',
            '$generator_saved_ids(pfibervm_frame_forged.FRAMES) = [n_generator]',
            '~$fiber_vm_valid(S, pfibervm_frame_forged, (n_fiber), eps)',
            '~$fiber_record_valid(S, n_fiber, pfiber[.VM = (pfibervm_frame_forged)])',
            '~$call_descriptors_valid($fiber_put(S, n_fiber, pfiber[.VM = (pfibervm_frame_forged)]))',
            'pfibervm_nested_forged = pfibervm[.TODO = (AT pfiberapi.SITE (GENERATOR_RESUME pgeneratorop)) :: pfibervm.TODO]',
            '$generator_resume_ids(pfibervm_nested_forged.TODO) = eps',
            '~$generator_flat_tasks(pfibervm_nested_forged.TODO)',
            '~$fiber_vm_valid(S, pfibervm_nested_forged, (n_fiber), eps)',
            'pfibervm_nested_frame_forged = pfibervm[.FRAMES = [pframe_base[.TODO = (AT pfiberapi.SITE (GENERATOR_RESUME pgeneratorop)) :: pframe_base.TODO]]]',
            '$generator_saved_ids(pfibervm_nested_frame_forged.FRAMES) = eps',
            '~$generator_flat_frames(pfibervm_nested_frame_forged.FRAMES)',
            '~$fiber_vm_valid(S, pfibervm_nested_frame_forged, (n_fiber), eps)',
            *VALID, *PAUSE, *DONE,
            'S_done.OBJECTS[n_fiber] = FIBER pfiber_done',
            'pfiber_done.STATUS = FIBER_TERMINATED', '~pfiber_done.FAILED',
            'pfiber_done.VALUE = PINT 9', 'pfiber_done.VM = eps',
            'pfiber_done.RAW = PNULL', 'pfiber_done.TARGET = eps',
            'S_done.OBJECTS[n_generator] = GENERATOR pgenerator_done',
            'pgenerator_done.PHASE = GENERATOR_PAUSED',
            'pgenerator_done.VALUE = (PINT 5)', 'pgenerator_done.RETURN = eps',
            'S_done.EVENTS = [OUTPUT $ptascii("S"), OUTPUT $ptascii("|"), OUTPUT $ptascii("1"), OUTPUT $ptascii("|"), OUTPUT $ptascii("5"), OUTPUT $ptascii("|"), OUTPUT $ptascii("R|"), OUTPUT $ptascii("9"), OUTPUT $ptascii("|")]',
        ],
    },
})


def run(selected):
    assert not selected or set(selected) <= CASES.keys(), 'unknown Fiber state case'
    cases = {key: value for key, value in CASES.items() if not selected or key in selected}
    out = Path(tempfile.mkdtemp(prefix='fiber-state-review-', dir=ROOT / '.tools'))
    environment = dict(os.environ, LC_ALL='C', TZ='UTC')
    environment.pop('PHP_SPEC_SCRIPT_ENCODING', None)
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    identity_paths = [ROOT / name for name in ('.tools/php/bin/php', '.tools/php-file.so',
        '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe')]
    identities = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in identity_paths}
    changed = subprocess.check_output(['git', 'diff', '--name-only', 'ae0aa479eb5369c879c3b42c358a12aae0ec6c9f'], cwd=ROOT, text=True).splitlines()
    changed += subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard', 'spec/semantics'], cwd=ROOT, text=True).splitlines()
    watched = [Path(__file__), Path(__file__).with_name('fiber_review_cases.json'), ROOT / 'spec/semantics/modules.json']
    watched += [ROOT / name for name in changed if name.endswith('.watsup')]
    inputs = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
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
        try:
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted'], name
        finally:
            frontend.close()
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
        try:
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'], name
        finally:
            adapter.close()
        fixture = directory / 'test.watsup'
        fixture.write_text(
            'dec $stage(pstate) : bool\ndef $stage(S) = true -- if ' + case['stage'] + '\n'
            'def $stage(S) = false -- otherwise\ndec $seek(pstate, nat) : pstate\n'
            'def $seek(S, n) = S -- if $stage(S)\n'
            'def $seek(S, n) = $seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1))) '
            '-- if ~$stage(S) -- if $(n > 0) -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
            'def $seek(S, n) = S -- if S.COMPLETION =/= NORMAL /\\ S.COMPLETION =/= BUDGET\n'
            'dec $main() : bool\ndef $main() = true\n'
            '  -- if S_initial = $php_run(' + checked['fixture'] + ', 0, '
            + json.dumps(base64.b64encode(str(source).encode()).decode()) + ')\n'
            '  -- if S_reached = $seek(S_initial[.COMPLETION = NORMAL], 4000)\n'
            '  -- if S_reached.COMPLETION = NORMAL \\/ S_reached.COMPLETION = BUDGET\n'
            '  -- if S = S_reached[.COMPLETION = NORMAL]\n'
            '  -- if ' + case['stage'] + '\n'
            + ''.join('  -- if ' + clause + '\n' for clause in case['checks']))
        process = recorded([ROOT / 'tests/semantics/_build/default/numeric_runner.exe',
                            '--sl', *modules, fixture], directory, 'model', environment, 120)
        passed = (not process['timeout'] and process['exit'] == 0 and
                  (directory / 'model.stdout').read_bytes() == b'true\n' and
                  not (directory / 'model.stderr').read_bytes())
        records.append({'id': name, 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                        'assertions': len(case['checks']) + 5, 'process': process, 'passed': passed})
        print(name, passed, flush=True)
        if not passed:
            print((directory / 'model.stderr').read_text()[-2500:], flush=True)
    assert inputs == {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}, 'Fiber review inputs changed during run'
    report = {'revision': revision, 'selection': list(cases), 'records': records,
              'identities': identities, 'inputs': inputs,
              'compiler': {'spectec_source_commit': 'da36ac3c434cd291940293a63da64544307730a3', 'ocaml_switch': '5.1.0', 'semantic_mode': 'SL'},
              'runtime': {'source_commit': '34308a6666b2d489c509541ea9befea9e2b42348', 'version': '8.5.10', 'sapi': 'cli', 'int_size': 8, 'zts': False},
              'environment': {'LC_ALL': 'C', 'TZ': 'UTC', 'PHP_SPEC_SCRIPT_ENCODING_removed': True},
              'budgets': {'seek_steps': 4000, 'finish_steps': 4000, 'process_seconds': 120},
              'raw': str(out), 'passed': all(row['passed'] for row in records)}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return report['passed']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if run(args.case) else 1)
