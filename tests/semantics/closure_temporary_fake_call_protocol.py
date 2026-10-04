#!/usr/bin/env python3
"""Temporary fake Closure calls, frozen warnings and receiver ownership."""
from pathlib import Path
import argparse
import closure_call_protocol as protocol

CASES = {'finite-getter-temporary-held-owners': {'source': '<?php\n'
                                                   "$old = new Exception('one');\n"
                                                   '$source = $old->getMessage(...);\n'
                                                   'unset($old);\n'
                                                   "$new = new Exception('two');\n"
                                                   'echo $source->call((function () use (&$source, '
                                                   '&$new) {\n'
                                                   '    $held = $new;\n'
                                                   '    $source = null;\n'
                                                   '    $new = null;\n'
                                                   '    return $held;\n'
                                                   "})()), '|', (int)($source === null), ':', "
                                                   "(int)($new === null), '|';\n",
                                         'stage': 'S.TODO = (CLOSURE_CALL_GETTER_RESULT '
                                                  'pclosurecall) :: ptask_tail* -- if '
                                                  'pclosurecall.RECEIVER = (n_new)',
                                         'checks': ['pclosurecall.SOURCE = n_source',
                                                    'S.OBJECTS[n_source] = GETTERCLOSURE n_old '
                                                    'GET_MESSAGE "Exception" porigin_capture',
                                                    'S.OBJECTS[n_old] = THROWABLE pthrowable_old',
                                                    'S.OBJECTS[n_new] = THROWABLE pthrowable_new',
                                                    'n_new =/= n_old',
                                                    '$closure_call_source(S, n_source)',
                                                    '$closure_call_warning(S, n_source, n_new) = '
                                                    'eps',
                                                    '$target_function(S, CLOSURE_TARGET n_source) '
                                                    '= eps',
                                                    'S.RESULT = KNOWN (PSTRING ($ptascii("two")))',
                                                    'pclosurecall.FIRST = (POBJECT n_new)',
                                                    'pclosurecall.RAW = eps /\\ pclosurecall.ERROR '
                                                    '= eps',
                                                    '$call_task_valid(S, '
                                                    'CLOSURE_CALL_GETTER_RESULT pclosurecall)',
                                                    '$getter_capture_live(S, n_source)',
                                                    '(HOBJECT n_source) <- S.ALLOCATIONS',
                                                    '(HOBJECT n_old) <- S.ALLOCATIONS',
                                                    '(HOBJECT n_new) <- S.ALLOCATIONS',
                                                    'HOBJECT n_source <- '
                                                    '$task_nodes(CLOSURE_CALL_GETTER_RESULT '
                                                    'pclosurecall)',
                                                    'HOBJECT n_new <- '
                                                    '$task_nodes(CLOSURE_CALL_GETTER_RESULT '
                                                    'pclosurecall)',
                                                    'HOBJECT n_old <- $node_children(S, HOBJECT '
                                                    'n_source)',
                                                    '~(HOBJECT n_new <- $node_children(S, HOBJECT '
                                                    'n_source))',
                                                    '$lookup(S.ENV, $ptascii("source")) = '
                                                    '(n_source_cell)',
                                                    'S.STORE[n_source_cell] = DEFINED PNULL',
                                                    '$lookup(S.ENV, $ptascii("new")) = '
                                                    '(n_new_cell)',
                                                    'S.STORE[n_new_cell] = DEFINED PNULL',
                                                    '~$call_selected_valid(S, CLOSURE_CALL_TARGET '
                                                    'n_source n_new, (pclosurecall.SITE))',
                                                    '~$call_task_valid(S, '
                                                    'CLOSURE_CALL_GETTER_RESULT '
                                                    'pclosurecall[.SOURCE = n_new])',
                                                    '~$call_task_valid(S, '
                                                    'CLOSURE_CALL_GETTER_RESULT pclosurecall[.LINE '
                                                    '= $(pclosurecall.LINE + 1)])',
                                                    '~$call_task_valid(S, '
                                                    'CLOSURE_CALL_GETTER_RESULT '
                                                    'pclosurecall[.INDEX = $(pclosurecall.INDEX + '
                                                    '1)])',
                                                    '~$call_task_valid(S, '
                                                    'CLOSURE_CALL_GETTER_RESULT '
                                                    'pclosurecall[.FIRST = (POBJECT n_old)])',
                                                    '~$call_task_valid(S, '
                                                    'CLOSURE_CALL_GETTER_RESULT pclosurecall[.RAW '
                                                    '= [(KINT 1, KNOWN PNULL)]])',
                                                    '~$call_task_valid(S[.ALLOCATIONS = '
                                                    '$temporary_call_without(S.ALLOCATIONS, '
                                                    'HOBJECT n_source)], '
                                                    'CLOSURE_CALL_GETTER_RESULT pclosurecall)',
                                                    '~$call_task_valid(S[.ALLOCATIONS = '
                                                    '$temporary_call_without(S.ALLOCATIONS, '
                                                    'HOBJECT n_new)], CLOSURE_CALL_GETTER_RESULT '
                                                    'pclosurecall)',
                                                    '$call_descriptors_valid(S)',
                                                    '$closure_state_valid(S)',
                                                    '$heap_valid($heap_graph(S))',
                                                    'S_budget = $drive(S, 0)',
                                                    'S_budget.COMPLETION = BUDGET',
                                                    '$call_descriptors_valid(S_budget)',
                                                    '$closure_state_valid(S_budget)',
                                                    '$heap_valid($heap_graph(S_budget))',
                                                    'S_done = $drive(S_budget[.COMPLETION = '
                                                    'NORMAL], 3000)',
                                                    'S_done.COMPLETION = NORMAL',
                                                    'S_done.CURRENT = eps /\\ S_done.FRAMES = eps',
                                                    '$call_descriptors_valid(S_done)',
                                                    '$closure_state_valid(S_done)',
                                                    '$heap_valid($heap_graph(S_done))',
                                                    '$temporary_call_outputs(S_done.EVENTS) = '
                                                    '$ptascii("two|1:1|")',
                                                    '~((HOBJECT n_source) <- S_done.ALLOCATIONS)',
                                                    '~((HOBJECT n_old) <- S_done.ALLOCATIONS)',
                                                    '~((HOBJECT n_new) <- S_done.ALLOCATIONS)']},
 'binding-warning-finally-throw-retirement': {'source': '<?php\n'
                                                        'error_reporting(0);\n'
                                                        'class CallWarnOwner268 {\n'
                                                        "    public function run() { echo 'BODY|'; "
                                                        '}\n'
                                                        '    public function capture() { return '
                                                        '$this->run(...); }\n'
                                                        '}\n'
                                                        'function stopCall268() {\n'
                                                        '    global $source, $receiver;\n'
                                                        '    $source = null;\n'
                                                        '    $receiver = null;\n'
                                                        "    echo 'W|';\n"
                                                        "    try { throw new Exception('stop'); }\n"
                                                        "    finally { echo 'F|'; }\n"
                                                        '}\n'
                                                        '$source = (new '
                                                        'CallWarnOwner268)->capture();\n'
                                                        '$receiver = new stdClass;\n'
                                                        "set_error_handler('stopCall268');\n"
                                                        'try { $source->call($receiver); }\n'
                                                        'catch (Exception $e) { echo '
                                                        "get_class($e), ':', $e->getMessage(), "
                                                        "'|'; }\n"
                                                        'restore_error_handler();\n'
                                                        'unset($e);\n'
                                                        "echo (int)($source === null), ':', "
                                                        "(int)($receiver === null), '|';\n",
                                              'stage': 'S.TODO = (THROW_SEARCH n_error) :: '
                                                       'ptask_tail* -- if '
                                                       '$temporary_call_outputs(S.EVENTS) = '
                                                       '$ptascii("W|F|") -- if S.CURRENT = '
                                                       '(pcallcontext) -- if pcallcontext.NAME = '
                                                       '$ptascii("stopCall268") -- if S.FRAMES = '
                                                       'pframe :: pframe_tail* -- if pframe.TODO = '
                                                       '(ERROR_HANDLER_RESULT perrorcall) :: '
                                                       'ptask_saved* -- if perrorcall.RESUME = '
                                                       'CLOSURE_CALL_WARNING pclosurecall ptbytes',
                                              'checks': ['pclosurecall.SOURCE = n_source',
                                                         'pclosurecall.RECEIVER = (n_new)',
                                                         '$object_body(S.OBJECTS[n_source]) = '
                                                         'METHODCLOSURE porigin_method '
                                                         'porigin_capture porigin_requested '
                                                         'pmethodcapture?',
                                                         '$target_receiver(S, CLOSURE_TARGET '
                                                         'n_source) = (n_old)',
                                                         'S.OBJECTS[n_old] = INSTANCE '
                                                         'porigin_class',
                                                         'S.OBJECTS[n_new] = STDINSTANCE',
                                                         'ptbytes = $ptascii("Cannot bind method '
                                                         'CallWarnOwner268::run() to object of '
                                                         'class stdClass, this will be an error in '
                                                         'PHP 9")',
                                                         'S.GLOBALTABLE = (psymboltable_global)',
                                                         '$lookup(psymboltable_global.ENV, '
                                                         '$ptascii("source")) = (n_source_cell)',
                                                         'S.STORE[n_source_cell] = DEFINED PNULL',
                                                         '$lookup(psymboltable_global.ENV, '
                                                         '$ptascii("receiver")) = '
                                                         '(n_receiver_cell)',
                                                         'S.STORE[n_receiver_cell] = DEFINED PNULL',
                                                         'S_emitter = '
                                                         '$api_saved_frame_scope($constant_frame_scope(S, '
                                                         'pframe, pframe_tail*), pframe, '
                                                         'pframe_tail*)',
                                                         '$call_task_valid(S_emitter, '
                                                         'CLOSURE_CALL_WARNING pclosurecall '
                                                         'ptbytes)',
                                                         '$error_call_valid(S_emitter, perrorcall)',
                                                         '$closure_call_warning(S_emitter, '
                                                         'n_source, n_new) = (ptbytes)',
                                                         '~$call_selected_valid(S_emitter, '
                                                         'CLOSURE_CALL_TARGET n_source n_new, '
                                                         '(pclosurecall.SITE))',
                                                         'S.ERRORHANDLER.CALLBACK = eps',
                                                         '(HOBJECT n_source) <- S.ALLOCATIONS',
                                                         '(HOBJECT n_old) <- S.ALLOCATIONS',
                                                         '(HOBJECT n_new) <- S.ALLOCATIONS',
                                                         'HOBJECT n_source <- '
                                                         '$task_nodes(CLOSURE_CALL_WARNING '
                                                         'pclosurecall ptbytes)',
                                                         'HOBJECT n_new <- '
                                                         '$task_nodes(CLOSURE_CALL_WARNING '
                                                         'pclosurecall ptbytes)',
                                                         'HOBJECT n_old <- $node_children(S, '
                                                         'HOBJECT n_source)',
                                                         '~$call_task_valid(S_emitter, '
                                                         'CLOSURE_CALL_WARNING pclosurecall '
                                                         '($ptascii("bad")))',
                                                         '~$call_task_valid(S_emitter, '
                                                         'CLOSURE_CALL_WARNING '
                                                         'pclosurecall[.SOURCE = n_old] ptbytes)',
                                                         '~$call_task_valid(S_emitter, '
                                                         'CLOSURE_CALL_WARNING '
                                                         'pclosurecall[.RECEIVER = (n_old)] '
                                                         'ptbytes)',
                                                         '~$call_task_valid(S_emitter, '
                                                         'CLOSURE_CALL_WARNING pclosurecall[.LINE '
                                                         '= $(pclosurecall.LINE + 1)] ptbytes)',
                                                         '~$error_call_valid(S_emitter, '
                                                         'perrorcall[.MESSAGE = $ptascii("bad")])',
                                                         '~$error_call_valid(S_emitter, '
                                                         'perrorcall[.LEVEL = 8192])',
                                                         '$call_descriptors_valid(S)',
                                                         '$closure_state_valid(S)',
                                                         '$heap_valid($heap_graph(S))',
                                                         'S_budget = $drive(S, 0)',
                                                         'S_budget.COMPLETION = BUDGET',
                                                         '$call_descriptors_valid(S_budget)',
                                                         '$closure_state_valid(S_budget)',
                                                         '$heap_valid($heap_graph(S_budget))',
                                                         'S_done = $drive(S_budget[.COMPLETION = '
                                                         'NORMAL], 3000)',
                                                         'S_done.COMPLETION = NORMAL',
                                                         'S_done.CURRENT = eps /\\ S_done.FRAMES = '
                                                         'eps',
                                                         '$call_descriptors_valid(S_done)',
                                                         '$closure_state_valid(S_done)',
                                                         '$heap_valid($heap_graph(S_done))',
                                                         '$temporary_call_outputs(S_done.EVENTS) = '
                                                         '$ptascii("W|F|Exception:stop|1:1|")',
                                                         '~((HOBJECT n_source) <- '
                                                         'S_done.ALLOCATIONS)',
                                                         '~((HOBJECT n_old) <- S_done.ALLOCATIONS)',
                                                         '~((HOBJECT n_new) <- S_done.ALLOCATIONS)',
                                                         '~((HOBJECT n_error) <- '
                                                         'S_done.ALLOCATIONS)',
                                                         'S_done.ERRORHANDLER.CALLBACK = eps']},
 'temporary-private-method-keeps-selected-source-and-statics': {'source': '<?php\n'
                                                                          'declare(strict_types=1);\n'
                                                                          'class '
                                                                          'FakePrivateCallHost268 '
                                                                          '{\n'
                                                                          '    public int $id;\n'
                                                                          '    public function '
                                                                          '__construct($id) { '
                                                                          '$this->id = $id; }\n'
                                                                          '    private function '
                                                                          'run(int $value = 3) {\n'
                                                                          '        static $n = 0;\n'
                                                                          '        echo '
                                                                          "self::class, '/', "
                                                                          "static::class, ':', "
                                                                          "$this->id, ':', ++$n, "
                                                                          "':', $value, '|';\n"
                                                                          '        if ($n === 1) '
                                                                          '{\n'
                                                                          '            try { '
                                                                          'Closure::getCurrent(); '
                                                                          '}\n'
                                                                          '            catch '
                                                                          "(Error $e) { echo 'E:', "
                                                                          "$e->getMessage(), '|'; "
                                                                          '}\n'
                                                                          '        }\n'
                                                                          '        return $value;\n'
                                                                          '    }\n'
                                                                          '    public function '
                                                                          'capture() { return '
                                                                          '$this->run(...); }\n'
                                                                          '}\n'
                                                                          '$original = new '
                                                                          'FakePrivateCallHost268(1);\n'
                                                                          '$receiver = new '
                                                                          'FakePrivateCallHost268(2);\n'
                                                                          '$source = '
                                                                          '$original->capture();\n'
                                                                          '$copy = clone $source;\n'
                                                                          'echo '
                                                                          '$source->call($receiver, '
                                                                          "'4'), '|';\n"
                                                                          'echo '
                                                                          '$copy->call($receiver), '
                                                                          "'|';\n"
                                                                          "echo $source(), '|';\n"
                                                                          'unset($original, '
                                                                          '$receiver, $source, '
                                                                          '$copy);\n',
                                                                'stage': 'S.CURRENT = '
                                                                         '(pcallcontext) -- if '
                                                                         'pcallcontext.TARGET = '
                                                                         'CLOSURE_CALL_TARGET '
                                                                         'n_source n_receiver -- '
                                                                         'if S.TODO = '
                                                                         '(CONFIG_INVOKE '
                                                                         'pconfigcall) :: '
                                                                         'ptask_tail* -- if '
                                                                         'pconfigcall.KIND = '
                                                                         'INTRINSIC_CLOSURE_CURRENT',
                                                                'checks': ['$object_body(S.OBJECTS[n_source]) '
                                                                           '= METHODCLOSURE '
                                                                           'porigin_method '
                                                                           'porigin_capture '
                                                                           'porigin_requested '
                                                                           'pmethodcapture?',
                                                                           '$class_method_origin(S.CLASSES, '
                                                                           'porigin_method) = '
                                                                           '(pmethoddesc)',
                                                                           'pmethoddesc.NAME = '
                                                                           '$ptascii("run")',
                                                                           'pmethoddesc.VISIBILITY '
                                                                           '= PROPERTY_PRIVATE',
                                                                           '~pmethoddesc.STATIC',
                                                                           '$target_function(S, '
                                                                           'CLOSURE_CALL_TARGET '
                                                                           'n_source n_receiver) = '
                                                                           '(pmethoddesc.FUNCTION)',
                                                                           'pcallcontext.FUNCTION '
                                                                           '= porigin_method',
                                                                           'pcallcontext.INSTANCE '
                                                                           '= (n_source)',
                                                                           'pcallcontext.RECEIVER '
                                                                           '= (n_receiver)',
                                                                           'pcallcontext.LEXICAL_CLASS '
                                                                           '= (pmethoddesc.OWNER)',
                                                                           'pcallcontext.CALLED_CLASS '
                                                                           '= '
                                                                           'pcallcontext.LEXICAL_CLASS',
                                                                           'S.OBJECTS[n_receiver] '
                                                                           '= INSTANCE '
                                                                           'pmethoddesc.OWNER',
                                                                           '$closure_scope_at(S.CLOSURESCOPES, '
                                                                           'n_source) = '
                                                                           '(pclosurescope_source)',
                                                                           'pclosurescope_source.LEXICAL '
                                                                           '= pmethoddesc.OWNER',
                                                                           'pclosurescope_source.CALLED '
                                                                           '= pmethoddesc.OWNER',
                                                                           'pclosurescope_source.RECEIVER '
                                                                           '= (n_original)',
                                                                           'n_original =/= '
                                                                           'n_receiver',
                                                                           '$target_receiver(S, '
                                                                           'CLOSURE_TARGET '
                                                                           'n_source) = '
                                                                           '(n_original)',
                                                                           '$node_children(S, '
                                                                           'HOBJECT n_source) = '
                                                                           '[HOBJECT n_original]',
                                                                           '$target_nodes(CLOSURE_CALL_TARGET '
                                                                           'n_source n_receiver) = '
                                                                           '[HOBJECT n_source, '
                                                                           'HOBJECT n_receiver]',
                                                                           '$closure_call_warning(S, '
                                                                           'n_source, n_receiver) '
                                                                           '= eps',
                                                                           '$closure_current_object(S) '
                                                                           '= eps',
                                                                           '~$closure_current_temporary(S)',
                                                                           '$lookup(S.ENV, '
                                                                           '$ptascii("value")) = '
                                                                           '(n_value)',
                                                                           'S.STORE[n_value] = '
                                                                           'DEFINED (PINT 4)',
                                                                           '$lookup(S.ENV, '
                                                                           '$ptascii("n")) = '
                                                                           '(n_static)',
                                                                           'S.STORE[n_static] = '
                                                                           'DEFINED (PINT 1)',
                                                                           '$fake_call_has_static(S.STATICS, '
                                                                           'n_static)',
                                                                           'S.GLOBALTABLE = '
                                                                           '(psymboltable_global)',
                                                                           '$lookup(psymboltable_global.ENV, '
                                                                           '$ptascii("copy")) = '
                                                                           '(n_copy_cell)',
                                                                           'S.STORE[n_copy_cell] = '
                                                                           'DEFINED (POBJECT '
                                                                           'n_copy)',
                                                                           '$target_function(S, '
                                                                           'CLOSURE_TARGET n_copy) '
                                                                           '= '
                                                                           '(pmethoddesc.FUNCTION)',
                                                                           '$node_children(S, '
                                                                           'HOBJECT n_copy) = '
                                                                           '[HOBJECT n_original]',
                                                                           '$($heap_owners($heap_graph(S), '
                                                                           'HOBJECT n_original) >= '
                                                                           '2)',
                                                                           '(HOBJECT n_source) <- '
                                                                           'S.ALLOCATIONS',
                                                                           '(HOBJECT n_receiver) '
                                                                           '<- S.ALLOCATIONS',
                                                                           '$call_current_valid(S)',
                                                                           '$call_descriptors_valid(S)',
                                                                           '$class_state_valid(S)',
                                                                           '$closure_state_valid(S)',
                                                                           '$heap_valid($heap_graph(S))',
                                                                           '~$call_current_valid(S[.CURRENT '
                                                                           '= '
                                                                           '(pcallcontext[.TARGET '
                                                                           '= CLOSURE_TARGET '
                                                                           'n_source])])',
                                                                           '~$call_current_valid(S[.CURRENT '
                                                                           '= '
                                                                           '(pcallcontext[.RECEIVER '
                                                                           '= (n_original)])])',
                                                                           '~$call_current_valid(S[.CURRENT '
                                                                           '= '
                                                                           '(pcallcontext[.INSTANCE '
                                                                           '= (n_receiver)])])',
                                                                           '~$call_current_valid(S[.CURRENT '
                                                                           '= '
                                                                           '(pcallcontext[.FUNCTION '
                                                                           '= '
                                                                           'pmethoddesc.OWNER])])',
                                                                           '~$call_current_valid(S[.CURRENT '
                                                                           '= '
                                                                           '(pcallcontext[.LEXICAL_CLASS '
                                                                           '= eps])])',
                                                                           '~$call_current_valid(S[.CURRENT '
                                                                           '= '
                                                                           '(pcallcontext[.CALLED_CLASS '
                                                                           '= eps])])',
                                                                           '~$call_current_valid(S[.CURRENT '
                                                                           '= '
                                                                           '(pcallcontext[.WRAPPER '
                                                                           '= eps])])',
                                                                           'S_budget = $drive(S, '
                                                                           '0)',
                                                                           'S_budget.COMPLETION = '
                                                                           'BUDGET',
                                                                           '$call_descriptors_valid(S_budget)',
                                                                           '$closure_state_valid(S_budget)',
                                                                           '$heap_valid($heap_graph(S_budget))',
                                                                           'S_done = '
                                                                           '$drive(S_budget[.COMPLETION '
                                                                           '= NORMAL], 3000)',
                                                                           'S_done.COMPLETION = '
                                                                           'NORMAL',
                                                                           'S_done.CURRENT = eps '
                                                                           '/\\ S_done.FRAMES = '
                                                                           'eps',
                                                                           '$fake_call_outputs(S_done.EVENTS) '
                                                                           '= '
                                                                           '$ptascii("FakePrivateCallHost268/FakePrivateCallHost268:2:1:4|E:Current '
                                                                           'function is not a '
                                                                           'closure|4|FakePrivateCallHost268/FakePrivateCallHost268:2:2:3|3|FakePrivateCallHost268/FakePrivateCallHost268:1:3:3|3|")',
                                                                           '~((HOBJECT n_source) '
                                                                           '<- S_done.ALLOCATIONS)',
                                                                           '~((HOBJECT n_copy) <- '
                                                                           'S_done.ALLOCATIONS)',
                                                                           '~((HOBJECT n_original) '
                                                                           '<- S_done.ALLOCATIONS)',
                                                                           '~((HOBJECT n_receiver) '
                                                                           '<- S_done.ALLOCATIONS)',
                                                                           '$call_descriptors_valid(S_done)',
                                                                           '$closure_state_valid(S_done)',
                                                                           '$heap_valid($heap_graph(S_done))']},
 'temporary-dummy-call-child-keeps-new-receiver-after-maker-retirement': {'source': '<?php\n'
                                                                                    'function '
                                                                                    'fake_dummy_maker268() '
                                                                                    '{\n'
                                                                                    '    echo '
                                                                                    "'P:', "
                                                                                    'get_class($this), '
                                                                                    "'|';\n"
                                                                                    '    return '
                                                                                    'function () '
                                                                                    '{\n'
                                                                                    '        echo '
                                                                                    'self::class, '
                                                                                    "'/', "
                                                                                    'static::class, '
                                                                                    "'/', "
                                                                                    'get_class($this), '
                                                                                    "'|';\n"
                                                                                    '        '
                                                                                    'return '
                                                                                    'Closure::getCurrent();\n'
                                                                                    '    };\n'
                                                                                    '}\n'
                                                                                    '$originalReceiver '
                                                                                    '= function () '
                                                                                    '{ return 1; '
                                                                                    '};\n'
                                                                                    '$nextReceiver '
                                                                                    '= static '
                                                                                    'function () { '
                                                                                    'return 2; };\n'
                                                                                    '$source = '
                                                                                    'fake_dummy_maker268(...);\n'
                                                                                    '$bound = '
                                                                                    '$source->bindTo($originalReceiver, '
                                                                                    'null);\n'
                                                                                    '$child = '
                                                                                    '$bound->call($nextReceiver);\n'
                                                                                    'unset($source, '
                                                                                    '$bound, '
                                                                                    '$originalReceiver, '
                                                                                    '$nextReceiver);\n'
                                                                                    'echo '
                                                                                    '(int)($child() '
                                                                                    '=== $child), '
                                                                                    "'|';\n"
                                                                                    'unset($child);\n',
                                                                          'stage': 'S.CURRENT = '
                                                                                   '(pcallcontext) '
                                                                                   '-- if '
                                                                                   'pcallcontext.TARGET '
                                                                                   '= '
                                                                                   'CLOSURE_TARGET '
                                                                                   'n_child -- if '
                                                                                   'S.OBJECTS[n_child] '
                                                                                   '= '
                                                                                   'INTERNALCALLCLOSURE '
                                                                                   'pinternalclosurescope '
                                                                                   '(REALCLOSURE '
                                                                                   'porigin_child '
                                                                                   'pitem* '
                                                                                   'pstaticcell*) '
                                                                                   '-- if S.TODO = '
                                                                                   '(CONFIG_INVOKE '
                                                                                   'pconfigcall) '
                                                                                   ':: ptask_tail* '
                                                                                   '-- if '
                                                                                   'pconfigcall.KIND '
                                                                                   '= '
                                                                                   'INTRINSIC_CLOSURE_CURRENT',
                                                                          'checks': ['~pinternalclosurescope.BOUND',
                                                                                     'pinternalclosurescope.LEXICAL '
                                                                                     '= '
                                                                                     'BIND_INTERNAL '
                                                                                     '($ptascii("Closure"))',
                                                                                     'pinternalclosurescope.CALLED '
                                                                                     '= '
                                                                                     'pinternalclosurescope.LEXICAL',
                                                                                     'pinternalclosurescope.RECEIVER '
                                                                                     '= '
                                                                                     '(n_receiver)',
                                                                                     'n_parent = '
                                                                                     'pinternalclosurescope.SOURCE',
                                                                                     '$(n_parent < '
                                                                                     'n_child)',
                                                                                     'S.OBJECTS[n_parent] '
                                                                                     '= '
                                                                                     'BOUNDFAKECLOSURE '
                                                                                     'pboundfake',
                                                                                     'S.OBJECTS[pboundfake.SOURCE] '
                                                                                     '= '
                                                                                     'NAMEDCLOSURE '
                                                                                     'porigin_function',
                                                                                     'pinternalclosurescope.FUNCTION '
                                                                                     '= '
                                                                                     'porigin_function',
                                                                                     'pboundfake.SCOPE '
                                                                                     '= '
                                                                                     'pinternalclosurescope.LEXICAL',
                                                                                     'pboundfake.RECEIVER '
                                                                                     '= '
                                                                                     '(n_original_receiver)',
                                                                                     'n_original_receiver '
                                                                                     '=/= '
                                                                                     'n_receiver',
                                                                                     '$internal_creator_body(S, '
                                                                                     'n_parent) = '
                                                                                     '(porigin_function)',
                                                                                     '$internal_closure_history_valid(S, '
                                                                                     'n_child)',
                                                                                     '$internal_closure_scope_valid(S, '
                                                                                     'n_child)',
                                                                                     '$internal_closure_row(S, '
                                                                                     'n_child) = '
                                                                                     '(pinternalclosurescope)',
                                                                                     'pinternalclosurescope.CALLSITE '
                                                                                     '= '
                                                                                     '(porigin_site)',
                                                                                     '$closure_call_args_at(S, '
                                                                                     'porigin_site) '
                                                                                     '= phpType7*',
                                                                                     '$function_at(S.CLOSURETEMPLATES, '
                                                                                     'porigin_child) '
                                                                                     '= '
                                                                                     '(pfunction_child)',
                                                                                     '~$closure_static(S, '
                                                                                     'pfunction_child)',
                                                                                     'pitem* = eps '
                                                                                     '/\\ '
                                                                                     'pstaticcell* '
                                                                                     '= eps',
                                                                                     '$node_children(S, '
                                                                                     'HOBJECT '
                                                                                     'n_child) = '
                                                                                     '[HOBJECT '
                                                                                     'n_receiver]',
                                                                                     '~(HOBJECT '
                                                                                     'n_parent <- '
                                                                                     '$node_children(S, '
                                                                                     'HOBJECT '
                                                                                     'n_child))',
                                                                                     '~(HOBJECT '
                                                                                     'pboundfake.SOURCE '
                                                                                     '<- '
                                                                                     '$node_children(S, '
                                                                                     'HOBJECT '
                                                                                     'n_child))',
                                                                                     '~(HOBJECT '
                                                                                     'n_original_receiver '
                                                                                     '<- '
                                                                                     '$node_children(S, '
                                                                                     'HOBJECT '
                                                                                     'n_child))',
                                                                                     '~((HOBJECT '
                                                                                     'n_parent) <- '
                                                                                     'S.ALLOCATIONS)',
                                                                                     '~((HOBJECT '
                                                                                     'pboundfake.SOURCE) '
                                                                                     '<- '
                                                                                     'S.ALLOCATIONS)',
                                                                                     '~((HOBJECT '
                                                                                     'n_original_receiver) '
                                                                                     '<- '
                                                                                     'S.ALLOCATIONS)',
                                                                                     '$heap_owners($heap_graph(S), '
                                                                                     'HOBJECT '
                                                                                     'n_parent) = '
                                                                                     '0',
                                                                                     '$heap_owners($heap_graph(S), '
                                                                                     'HOBJECT '
                                                                                     'n_original_receiver) '
                                                                                     '= 0',
                                                                                     '(HOBJECT '
                                                                                     'n_receiver) '
                                                                                     '<- '
                                                                                     'S.ALLOCATIONS',
                                                                                     '$($heap_owners($heap_graph(S), '
                                                                                     'HOBJECT '
                                                                                     'n_receiver) '
                                                                                     '>= 2)',
                                                                                     'pcallcontext.FUNCTION '
                                                                                     '= '
                                                                                     'porigin_child',
                                                                                     'pcallcontext.INSTANCE '
                                                                                     '= (n_child)',
                                                                                     'pcallcontext.RECEIVER '
                                                                                     '= '
                                                                                     '(n_receiver)',
                                                                                     'pcallcontext.LEXICAL_CLASS '
                                                                                     '= eps /\\ '
                                                                                     'pcallcontext.CALLED_CLASS '
                                                                                     '= eps',
                                                                                     '$internal_closure_current_scopes(S) '
                                                                                     '= '
                                                                                     '((pbindscope_lexical, '
                                                                                     'pbindscope_called, '
                                                                                     'n_bound?)) '
                                                                                     '-- if '
                                                                                     'pbindscope_lexical '
                                                                                     '= '
                                                                                     'pinternalclosurescope.LEXICAL '
                                                                                     '/\\ '
                                                                                     'pbindscope_called '
                                                                                     '= '
                                                                                     'pinternalclosurescope.CALLED '
                                                                                     '/\\ n_bound? '
                                                                                     '= '
                                                                                     '(n_receiver)',
                                                                                     '$closure_current_object(S) '
                                                                                     '= (n_child)',
                                                                                     '~$closure_current_temporary(S)',
                                                                                     '$bound_fake_internal_scope(S) '
                                                                                     '= '
                                                                                     '($ptascii("Closure"))',
                                                                                     '$bound_fake_internal_called(S) '
                                                                                     '= '
                                                                                     '($ptascii("Closure"))',
                                                                                     '$call_descriptors_valid(S)',
                                                                                     '$closure_state_valid(S)',
                                                                                     '$heap_valid($heap_graph(S))',
                                                                                     '~$internal_closure_history_valid(S[.OBJECTS '
                                                                                     '= '
                                                                                     '$object_set(S.OBJECTS, '
                                                                                     'n_child, '
                                                                                     'INTERNALCALLCLOSURE '
                                                                                     'pinternalclosurescope[.SOURCE '
                                                                                     '= n_child] '
                                                                                     '(REALCLOSURE '
                                                                                     'porigin_child '
                                                                                     'pitem* '
                                                                                     'pstaticcell*))], '
                                                                                     'n_child)',
                                                                                     '~$internal_closure_history_valid(S[.OBJECTS '
                                                                                     '= '
                                                                                     '$object_set(S.OBJECTS, '
                                                                                     'n_child, '
                                                                                     'INTERNALCALLCLOSURE '
                                                                                     'pinternalclosurescope[.FUNCTION '
                                                                                     '= '
                                                                                     'porigin_child] '
                                                                                     '(REALCLOSURE '
                                                                                     'porigin_child '
                                                                                     'pitem* '
                                                                                     'pstaticcell*))], '
                                                                                     'n_child)',
                                                                                     '~$internal_closure_history_valid(S[.OBJECTS '
                                                                                     '= '
                                                                                     '$object_set(S.OBJECTS, '
                                                                                     'n_child, '
                                                                                     'INTERNALCALLCLOSURE '
                                                                                     'pinternalclosurescope[.CALLSITE '
                                                                                     '= eps] '
                                                                                     '(REALCLOSURE '
                                                                                     'porigin_child '
                                                                                     'pitem* '
                                                                                     'pstaticcell*))], '
                                                                                     'n_child)',
                                                                                     '~$internal_closure_history_valid(S[.OBJECTS '
                                                                                     '= '
                                                                                     '$object_set(S.OBJECTS, '
                                                                                     'n_child, '
                                                                                     'INTERNALCALLCLOSURE '
                                                                                     'pinternalclosurescope[.BOUND '
                                                                                     '= true] '
                                                                                     '(REALCLOSURE '
                                                                                     'porigin_child '
                                                                                     'pitem* '
                                                                                     'pstaticcell*))], '
                                                                                     'n_child)',
                                                                                     '~$internal_closure_history_valid(S[.OBJECTS '
                                                                                     '= '
                                                                                     '$object_set(S.OBJECTS, '
                                                                                     'n_child, '
                                                                                     'INTERNALCALLCLOSURE '
                                                                                     'pinternalclosurescope[.LEXICAL '
                                                                                     '= '
                                                                                     'BIND_UNSCOPED] '
                                                                                     '(REALCLOSURE '
                                                                                     'porigin_child '
                                                                                     'pitem* '
                                                                                     'pstaticcell*))], '
                                                                                     'n_child)',
                                                                                     '~$internal_closure_history_valid(S[.OBJECTS '
                                                                                     '= '
                                                                                     '$object_set(S.OBJECTS, '
                                                                                     'n_child, '
                                                                                     'INTERNALCALLCLOSURE '
                                                                                     'pinternalclosurescope[.CALLED '
                                                                                     '= '
                                                                                     'BIND_UNSCOPED] '
                                                                                     '(REALCLOSURE '
                                                                                     'porigin_child '
                                                                                     'pitem* '
                                                                                     'pstaticcell*))], '
                                                                                     'n_child)',
                                                                                     '~$internal_closure_history_valid(S[.OBJECTS '
                                                                                     '= '
                                                                                     '$object_set(S.OBJECTS, '
                                                                                     'n_child, '
                                                                                     'INTERNALCALLCLOSURE '
                                                                                     'pinternalclosurescope[.RECEIVER '
                                                                                     '= eps] '
                                                                                     '(REALCLOSURE '
                                                                                     'porigin_child '
                                                                                     'pitem* '
                                                                                     'pstaticcell*))], '
                                                                                     'n_child)',
                                                                                     '~$internal_closure_history_valid(S[.OBJECTS '
                                                                                     '= '
                                                                                     '$object_set(S.OBJECTS, '
                                                                                     'n_child, '
                                                                                     'INTERNALCALLCLOSURE '
                                                                                     'pinternalclosurescope[.RECEIVER '
                                                                                     '= '
                                                                                     '(|S.OBJECTS|)] '
                                                                                     '(REALCLOSURE '
                                                                                     'porigin_child '
                                                                                     'pitem* '
                                                                                     'pstaticcell*))], '
                                                                                     'n_child)',
                                                                                     '~$internal_closure_scope_valid(S[.OBJECTS '
                                                                                     '= '
                                                                                     '$object_set(S.OBJECTS, '
                                                                                     'n_receiver, '
                                                                                     'STDINSTANCE)], '
                                                                                     'n_child)',
                                                                                     '~$call_current_valid(S[.CURRENT '
                                                                                     '= '
                                                                                     '(pcallcontext[.RECEIVER '
                                                                                     '= eps])])',
                                                                                     'S_budget = '
                                                                                     '$drive(S, 0)',
                                                                                     'S_budget.COMPLETION '
                                                                                     '= BUDGET',
                                                                                     '$call_descriptors_valid(S_budget)',
                                                                                     '$closure_state_valid(S_budget)',
                                                                                     '$heap_valid($heap_graph(S_budget))',
                                                                                     'S_done = '
                                                                                     '$drive(S_budget[.COMPLETION '
                                                                                     '= NORMAL], '
                                                                                     '3000)',
                                                                                     'S_done.COMPLETION '
                                                                                     '= NORMAL',
                                                                                     'S_done.CURRENT '
                                                                                     '= eps /\\ '
                                                                                     'S_done.FRAMES '
                                                                                     '= eps',
                                                                                     '$fake_call_outputs(S_done.EVENTS) '
                                                                                     '= '
                                                                                     '$ptascii("P:Closure|Closure/Closure/Closure|1|")',
                                                                                     '~((HOBJECT '
                                                                                     'n_child) <- '
                                                                                     'S_done.ALLOCATIONS)',
                                                                                     '~((HOBJECT '
                                                                                     'n_receiver) '
                                                                                     '<- '
                                                                                     'S_done.ALLOCATIONS)',
                                                                                     '$call_descriptors_valid(S_done)',
                                                                                     '$closure_state_valid(S_done)',
                                                                                     '$heap_valid($heap_graph(S_done))']},
 'temporary-reference-warning-freezes-value-before-handler-allocation': {'source': '<?php\n'
                                                                                   'class '
                                                                                   'FakeReferenceHost268 '
                                                                                   '{\n'
                                                                                   '    public '
                                                                                   'function '
                                                                                   'run(&$value) { '
                                                                                   "echo 'B:', "
                                                                                   "++$value, '|'; "
                                                                                   'return $value; '
                                                                                   '}\n'
                                                                                   '}\n'
                                                                                   '$original = '
                                                                                   'new '
                                                                                   'FakeReferenceHost268;\n'
                                                                                   '$receiver = '
                                                                                   'new '
                                                                                   'FakeReferenceHost268;\n'
                                                                                   '$source = '
                                                                                   '$original->run(...);\n'
                                                                                   '$value = 5;\n'
                                                                                   'set_error_handler(function '
                                                                                   '($n, $message) '
                                                                                   'use (&$value) '
                                                                                   '{\n'
                                                                                   "    echo 'W:', "
                                                                                   '$message, '
                                                                                   "'|';\n"
                                                                                   '    $value = '
                                                                                   '9;\n'
                                                                                   '    return '
                                                                                   'true;\n'
                                                                                   '});\n'
                                                                                   '$result = '
                                                                                   '$source->call($receiver, '
                                                                                   '$value);\n'
                                                                                   "echo 'R:', "
                                                                                   "$value, ':', "
                                                                                   "$result, '|';\n"
                                                                                   'restore_error_handler();\n'
                                                                                   'unset($original, '
                                                                                   '$receiver, '
                                                                                   '$source, '
                                                                                   '$value, '
                                                                                   '$result);\n',
                                                                         'stage': 'S.CURRENT = '
                                                                                  '(pcallcontext) '
                                                                                  '-- if '
                                                                                  'pcallcontext.TARGET '
                                                                                  '= '
                                                                                  'CLOSURE_TARGET '
                                                                                  'n_handler -- if '
                                                                                  'S.FRAMES = '
                                                                                  'pframe :: '
                                                                                  'pframe_tail* -- '
                                                                                  'if pframe.TODO '
                                                                                  '= '
                                                                                  '(ERROR_HANDLER_RESULT '
                                                                                  'perrorcall) :: '
                                                                                  'ptask_saved* -- '
                                                                                  'if '
                                                                                  'perrorcall.RESUME '
                                                                                  '= '
                                                                                  'CLOSURE_CALL_REFERENCE '
                                                                                  'pclosurecall n '
                                                                                  'pnamedargs '
                                                                                  'n_base -- if '
                                                                                  'S.GLOBALTABLE = '
                                                                                  '(psymboltable_global) '
                                                                                  '-- if '
                                                                                  '$lookup(psymboltable_global.ENV, '
                                                                                  '$ptascii("value")) '
                                                                                  '= (n_value) -- '
                                                                                  'if '
                                                                                  'S.STORE[n_value] '
                                                                                  '= DEFINED (PINT '
                                                                                  '9)',
                                                                         'checks': ['n = 0',
                                                                                    'pnamedargs = '
                                                                                    '{SLOTS eps, '
                                                                                    'NAMED eps}',
                                                                                    'pclosurecall.RAW '
                                                                                    '= [(KINT 1, '
                                                                                    'KNOWN (PINT '
                                                                                    '5))]',
                                                                                    'pclosurecall.SENT.SLOTS '
                                                                                    '= [NAMED_SENT '
                                                                                    '(KNOWN (PINT '
                                                                                    '5))]',
                                                                                    'pclosurecall.ERROR '
                                                                                    '= eps',
                                                                                    'pclosurecall.RECEIVER '
                                                                                    '= '
                                                                                    '(n_receiver)',
                                                                                    'n_source = '
                                                                                    'pclosurecall.SOURCE',
                                                                                    '$closure_call_real(S, '
                                                                                    'n_source) = '
                                                                                    'false',
                                                                                    '$target_function(S, '
                                                                                    'CLOSURE_CALL_TARGET '
                                                                                    'n_source '
                                                                                    'n_receiver) = '
                                                                                    '(pfunction)',
                                                                                    '$closure_call_reference_formal(pfunction.SIGNATURE.PARAMETERS)',
                                                                                    '$closure_call_warning(S, '
                                                                                    'n_source, '
                                                                                    'n_receiver) = '
                                                                                    'eps',
                                                                                    '$(n_base < '
                                                                                    '|S.STORE|)',
                                                                                    'perrorcall.MESSAGE '
                                                                                    '= '
                                                                                    '$ptascii("FakeReferenceHost268::run(): '
                                                                                    'Argument #1 '
                                                                                    '($value) must '
                                                                                    'be passed by '
                                                                                    'reference, '
                                                                                    'value given")',
                                                                                    'perrorcall.MESSAGE '
                                                                                    '= '
                                                                                    '$closure_call_reference_message(S, '
                                                                                    'pclosurecall, '
                                                                                    'n)',
                                                                                    'perrorcall.LEVEL '
                                                                                    '= 2',
                                                                                    'perrorcall.LINE '
                                                                                    '= '
                                                                                    'pclosurecall.LINE',
                                                                                    '(HOBJECT '
                                                                                    'n_source) <- '
                                                                                    'S.ALLOCATIONS',
                                                                                    '(HOBJECT '
                                                                                    'n_receiver) '
                                                                                    '<- '
                                                                                    'S.ALLOCATIONS',
                                                                                    '(HOBJECT '
                                                                                    'n_handler) <- '
                                                                                    'S.ALLOCATIONS',
                                                                                    'HOBJECT '
                                                                                    'n_source <- '
                                                                                    '$task_nodes(perrorcall.RESUME)',
                                                                                    'HOBJECT '
                                                                                    'n_receiver <- '
                                                                                    '$task_nodes(perrorcall.RESUME)',
                                                                                    '~(HCELL '
                                                                                    'n_value <- '
                                                                                    '$task_nodes(perrorcall.RESUME))',
                                                                                    '~(HCELL '
                                                                                    'n_base <- '
                                                                                    '$task_nodes(perrorcall.RESUME))',
                                                                                    'S_emitter = '
                                                                                    '$api_saved_frame_scope($constant_frame_scope(S, '
                                                                                    'pframe, '
                                                                                    'pframe_tail*), '
                                                                                    'pframe, '
                                                                                    'pframe_tail*)',
                                                                                    '$call_task_valid(S_emitter, '
                                                                                    'perrorcall.RESUME)',
                                                                                    '$error_call_valid(S_emitter, '
                                                                                    'perrorcall)',
                                                                                    '$call_descriptors_valid(S)',
                                                                                    '$closure_state_valid(S)',
                                                                                    '$heap_valid($heap_graph(S))',
                                                                                    '~$call_task_valid(S_emitter, '
                                                                                    'CLOSURE_CALL_REFERENCE '
                                                                                    'pclosurecall '
                                                                                    'n pnamedargs '
                                                                                    '$(|S.STORE| + '
                                                                                    '1))',
                                                                                    '~$call_task_valid(S_emitter, '
                                                                                    'CLOSURE_CALL_REFERENCE '
                                                                                    'pclosurecall '
                                                                                    '$(n + 1) '
                                                                                    'pnamedargs '
                                                                                    'n_base)',
                                                                                    '~$call_task_valid(S_emitter, '
                                                                                    'CLOSURE_CALL_REFERENCE '
                                                                                    'pclosurecall '
                                                                                    'n '
                                                                                    'pnamedargs[.SLOTS '
                                                                                    '= [NAMED_SENT '
                                                                                    '(REFERENCE '
                                                                                    'n_value)]] '
                                                                                    'n_base)',
                                                                                    '~$call_task_valid(S_emitter, '
                                                                                    'CLOSURE_CALL_REFERENCE '
                                                                                    'pclosurecall[.LINE '
                                                                                    '= '
                                                                                    '$(pclosurecall.LINE '
                                                                                    '+ 1)] n '
                                                                                    'pnamedargs '
                                                                                    'n_base)',
                                                                                    '~$call_task_valid(S_emitter, '
                                                                                    'CLOSURE_CALL_REFERENCE '
                                                                                    'pclosurecall[.SOURCE '
                                                                                    '= n_receiver] '
                                                                                    'n pnamedargs '
                                                                                    'n_base)',
                                                                                    '~$call_task_valid(S_emitter, '
                                                                                    'CLOSURE_CALL_REFERENCE '
                                                                                    'pclosurecall[.RAW '
                                                                                    '= [(KINT 1, '
                                                                                    'KNOWN (PINT '
                                                                                    '9))]] n '
                                                                                    'pnamedargs '
                                                                                    'n_base)',
                                                                                    '~$call_task_valid(S_emitter, '
                                                                                    'CLOSURE_CALL_REFERENCE '
                                                                                    'pclosurecall[.RAW '
                                                                                    '= [(KINT 1, '
                                                                                    'REFERENCE '
                                                                                    'n_value)]] n '
                                                                                    'pnamedargs '
                                                                                    'n_base)',
                                                                                    '~$error_call_valid(S_emitter, '
                                                                                    'perrorcall[.MESSAGE '
                                                                                    '= '
                                                                                    '$ptascii("forged")])',
                                                                                    '~$error_call_valid(S_emitter, '
                                                                                    'perrorcall[.LEVEL '
                                                                                    '= 8192])',
                                                                                    'S_prepared = '
                                                                                    '$fake_call_seek_prepared(S, '
                                                                                    '200)[.COMPLETION '
                                                                                    '= NORMAL]',
                                                                                    'S_prepared.TODO '
                                                                                    '= '
                                                                                    '(CLOSURE_CALL_FORWARD '
                                                                                    'pclosurecall '
                                                                                    '1 '
                                                                                    'pnamedargs_prepared '
                                                                                    'n_base) :: '
                                                                                    'ptask_prepared*',
                                                                                    'pnamedargs_prepared.SLOTS '
                                                                                    '= [NAMED_SENT '
                                                                                    '(REFERENCE '
                                                                                    'n_fresh)]',
                                                                                    'pnamedargs_prepared.NAMED '
                                                                                    '= eps',
                                                                                    '$(n_fresh > '
                                                                                    'n_base)',
                                                                                    'n_fresh =/= '
                                                                                    'n_value',
                                                                                    'S_prepared.STORE[n_fresh] '
                                                                                    '= DEFINED '
                                                                                    '(PINT 5)',
                                                                                    'S_prepared.STORE[n_value] '
                                                                                    '= DEFINED '
                                                                                    '(PINT 9)',
                                                                                    'n_fresh <- '
                                                                                    'S_prepared.REFCELLS',
                                                                                    '(HCELL '
                                                                                    'n_fresh) <- '
                                                                                    'S_prepared.ALLOCATIONS',
                                                                                    'HCELL n_fresh '
                                                                                    '<- '
                                                                                    '$task_nodes(CLOSURE_CALL_FORWARD '
                                                                                    'pclosurecall '
                                                                                    '1 '
                                                                                    'pnamedargs_prepared '
                                                                                    'n_base)',
                                                                                    '$call_task_valid(S_prepared, '
                                                                                    'CLOSURE_CALL_FORWARD '
                                                                                    'pclosurecall '
                                                                                    '1 '
                                                                                    'pnamedargs_prepared '
                                                                                    'n_base)',
                                                                                    '~$call_task_valid(S_prepared, '
                                                                                    'CLOSURE_CALL_FORWARD '
                                                                                    'pclosurecall '
                                                                                    '1 '
                                                                                    'pnamedargs_prepared[.SLOTS '
                                                                                    '= [NAMED_SENT '
                                                                                    '(REFERENCE '
                                                                                    'n_value)]] '
                                                                                    'n_base)',
                                                                                    '$call_descriptors_valid(S_prepared)',
                                                                                    '$closure_state_valid(S_prepared)',
                                                                                    '$heap_valid($heap_graph(S_prepared))',
                                                                                    'S_budget = '
                                                                                    '$drive(S_prepared, '
                                                                                    '0)',
                                                                                    'S_budget.COMPLETION '
                                                                                    '= BUDGET',
                                                                                    '$call_descriptors_valid(S_budget)',
                                                                                    '$closure_state_valid(S_budget)',
                                                                                    '$heap_valid($heap_graph(S_budget))',
                                                                                    'S_done = '
                                                                                    '$drive(S_budget[.COMPLETION '
                                                                                    '= NORMAL], '
                                                                                    '3000)',
                                                                                    'S_done.COMPLETION '
                                                                                    '= NORMAL',
                                                                                    'S_done.CURRENT '
                                                                                    '= eps /\\ '
                                                                                    'S_done.FRAMES '
                                                                                    '= eps',
                                                                                    '$fake_call_outputs(S_done.EVENTS) '
                                                                                    '= '
                                                                                    '$ptascii("W:FakeReferenceHost268::run(): '
                                                                                    'Argument #1 '
                                                                                    '($value) must '
                                                                                    'be passed by '
                                                                                    'reference, '
                                                                                    'value '
                                                                                    'given|B:6|R:9:6|")',
                                                                                    '~((HCELL '
                                                                                    'n_fresh) <- '
                                                                                    'S_done.ALLOCATIONS)',
                                                                                    '~((HOBJECT '
                                                                                    'n_source) <- '
                                                                                    'S_done.ALLOCATIONS)',
                                                                                    '~((HOBJECT '
                                                                                    'n_receiver) '
                                                                                    '<- '
                                                                                    'S_done.ALLOCATIONS)',
                                                                                    '~((HOBJECT '
                                                                                    'n_handler) <- '
                                                                                    'S_done.ALLOCATIONS)',
                                                                                    '$call_descriptors_valid(S_done)',
                                                                                    '$closure_state_valid(S_done)',
                                                                                    '$heap_valid($heap_graph(S_done))']}}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--match', default='')
    args = parser.parse_args()
    selected = {name: case for name, case in CASES.items() if args.match in name}
    assert selected
    helper = Path(__file__).with_suffix('.watsup')
    protocol.MODULES.append(helper)
    protocol.run(selected, extra_inputs=(Path(__file__), helper))
