#!/usr/bin/env python3
"""Authentic callable receive owners and warning/conversion resumption."""
from pathlib import Path

import closure_call_protocol as protocol

CASES = {'failed-lookup-lossy-int-keeps-pre-warning-result': {'source': '<?php\n'
                                                                'class ReceiveLossyFallback248 {\n'
                                                                '    public static function '
                                                                "take(callable|int &...$items) { echo 'B:', "
                                                                "$items[0], '|'; }\n"
                                                                '}\n'
                                                                "$input = 'self::xx';\n"
                                                                '$hits = 0;\n'
                                                                'set_error_handler(function ($level, '
                                                                '$message) use (&$input, &$hits) {\n'
                                                                '    $hits++;\n'
                                                                "    echo 'D:', $message, '|';\n"
                                                                "    if ($hits === 1) { $input = '123456.5'; "
                                                                '}\n'
                                                                '    else { $input = 99; }\n'
                                                                '    return true;\n'
                                                                '});\n'
                                                                'ReceiveLossyFallback248::take($input);\n'
                                                                "echo 'A:', $input, ':', $hits, '|';\n"
                                                                'restore_error_handler();\n',
                                                      'stage': 'S.CURRENT = (pcallcontext_handler) -- if '
                                                               'S.FRAMES = pframe_receive :: pframe_tail* -- '
                                                               'if pframe_receive.TODO = '
                                                               '[ERROR_HANDLER_RESULT perrorcall] -- if '
                                                               'perrorcall.RESUME = CALLABLE_SCALAR_RESULT '
                                                               '(VARIADIC_RECEIVE porigin_receive '
                                                               'n_argument) (REFERENCE n_input) (PSTRING '
                                                               'ptbytes_input) i -- if S.STORE[n_input] = '
                                                               'DEFINED (PINT 99)',
                                                      'checks': ['pframe_receive.LOCALS = '
                                                                 '(psymboltable_receive)',
                                                                 'S_receive = $api_saved_frame_scope(S, '
                                                                 'pframe_receive, pframe_tail*)',
                                                                 'S_receive.ENV = psymboltable_receive.ENV',
                                                                 'S_receive.FRAMES = pframe_tail*',
                                                                 '$api_pending_task(perrorcall.RESUME)',
                                                                 '$api_pending_tasks(pframe_receive.TODO)',
                                                                 '$error_context_call(S, '
                                                                 'pcallcontext_handler) = (perrorcall)',
                                                                 '$error_call_valid(S_receive, perrorcall)',
                                                                 'perrorcall.CALLBACK = POBJECT n_handler',
                                                                 'S.ERRORHANDLER.CALLBACK = eps',
                                                                 'n_argument = 0',
                                                                 'ptbytes_input = $ptascii("123456.5")',
                                                                 'i = 123456',
                                                                 'S_receive.CURRENT = (pcallcontext)',
                                                                 'pcallcontext.FUNCTION = porigin_receive',
                                                                 'pcallcontext.ARGC = 1 /\\ '
                                                                 'pcallcontext.NAMED = eps /\\ '
                                                                 'pcallcontext.HOLES = eps',
                                                                 'pcallcontext.EXTRA = [REFERENCE n_input]',
                                                                 'S.STORE[n_input] = DEFINED (PINT 99)',
                                                                 '(HCELL n_input) <- S.ALLOCATIONS /\\ '
                                                                 'n_input <- S.REFCELLS',
                                                                 '$function_at($all_functions(S), '
                                                                 'porigin_receive) = (pfunction)',
                                                                 'pfunction.SIGNATURE.PARAMETERS[0].BYREF '
                                                                 '/\\ '
                                                                 'pfunction.SIGNATURE.PARAMETERS[0].VARIADIC',
                                                                 '$lookup(S_receive.ENV, $ptascii("items")) '
                                                                 '= (n_collector)',
                                                                 'S.STORE[n_collector] = DEFINED (PARRAY '
                                                                 'n_collected)',
                                                                 'S.ARRAYS[n_collected].ITEMS = eps',
                                                                 'ptask_result = CALLABLE_SCALAR_RESULT '
                                                                 '(VARIADIC_RECEIVE porigin_receive '
                                                                 'n_argument) (REFERENCE n_input) (PSTRING '
                                                                 'ptbytes_input) i',
                                                                 '$task_nodes(ptask_result) = [HCELL '
                                                                 'n_input]',
                                                                 '$call_task_valid(S_receive, ptask_result)',
                                                                 '$api_fallback_conversion(S_receive, '
                                                                 'VARIADIC_RECEIVE porigin_receive '
                                                                 'n_argument) = TYPEREJECT',
                                                                 '$call_descriptors_valid(S)',
                                                                 '$class_state_valid(S)',
                                                                 '$closure_state_valid(S)',
                                                                 '$heap_valid($heap_graph(S))',
                                                                 '~$call_task_valid(S_receive, '
                                                                 'CALLABLE_SCALAR_RESULT (VARIADIC_RECEIVE '
                                                                 'porigin_receive 1) (REFERENCE n_input) '
                                                                 '(PSTRING ptbytes_input) i)',
                                                                 'n_bad_cell = |S.STORE|',
                                                                 '~$call_task_valid(S_receive, '
                                                                 'CALLABLE_SCALAR_RESULT (VARIADIC_RECEIVE '
                                                                 'porigin_receive 0) (REFERENCE n_bad_cell) '
                                                                 '(PSTRING ptbytes_input) i)',
                                                                 '~$call_task_valid(S_receive, '
                                                                 'CALLABLE_SCALAR_RESULT (VARIADIC_RECEIVE '
                                                                 'porigin_receive 0) (KNOWN (PSTRING '
                                                                 'ptbytes_input)) (PSTRING ptbytes_input) i)',
                                                                 '~$call_task_valid(S_receive, '
                                                                 'CALLABLE_SCALAR_RESULT (VARIADIC_RECEIVE '
                                                                 'porigin_receive 0) (REFERENCE n_input) '
                                                                 '(PSTRING ptbytes_input) $(i + 1))',
                                                                 '~$call_task_valid(S_receive, '
                                                                 'CALLABLE_SCALAR_RESULT (VARIADIC_RECEIVE '
                                                                 'porigin_receive 0) (REFERENCE n_input) '
                                                                 '(PSTRING $ptascii("123457.5")) i)',
                                                                 '~$call_task_valid(S_receive, '
                                                                 'CALLABLE_SCALAR_RESULT '
                                                                 '(NAMED_VARIADIC_RECEIVE porigin_receive 0) '
                                                                 '(REFERENCE n_input) (PSTRING '
                                                                 'ptbytes_input) i)',
                                                                 '~$call_task_valid(S_receive, '
                                                                 'CALLABLE_SCALAR_RESULT (TYPE_RECEIVE '
                                                                 'porigin_receive 0) (REFERENCE n_input) '
                                                                 '(PSTRING ptbytes_input) i)',
                                                                 'S_budget = $drive(S, 0)',
                                                                 'S_budget.COMPLETION = BUDGET',
                                                                 '$call_descriptors_valid(S_budget)',
                                                                 '$heap_valid($heap_graph(S_budget))',
                                                                 'S_done = $drive(S_budget[.COMPLETION = '
                                                                 'NORMAL], 3000)',
                                                                 'S_done.COMPLETION = NORMAL',
                                                                 '$capture_outputs(S_done.EVENTS) = '
                                                                 '$ptascii("D:Use of \\"self\\" in callables '
                                                                 'is deprecated|D:Implicit conversion from '
                                                                 'float-string \\"123456.5\\" to int loses '
                                                                 'precision|B:123456|A:123456:2|")',
                                                                 'S_done.STORE[n_input] = DEFINED (PINT '
                                                                 '123456)',
                                                                 '~((HOBJECT n_handler) <- '
                                                                 'S_done.ALLOCATIONS)',
                                                                 'S_done.CURRENT = eps /\\ S_done.FRAMES = '
                                                                 'eps',
                                                                 'S_done.ERRORHANDLER.CALLBACK = eps /\\ '
                                                                 'S_done.ERRORHANDLERS = eps',
                                                                 '~((HARRAY n_collected) <- '
                                                                 'S_done.ALLOCATIONS)',
                                                                 '$heap_owners($heap_graph(S_done), HARRAY '
                                                                 'n_collected) = 0',
                                                                 '$call_descriptors_valid(S_done)',
                                                                 '$class_state_valid(S_done)',
                                                                 '$closure_state_valid(S_done)',
                                                                 '$heap_valid($heap_graph(S_done))']},
 'failed-lookup-forces-dual-object-string-conversion': {'source': '<?php\n'
                                                                  'class ReceiveDualStringable248 {\n'
                                                                  '    public function __invoke() { echo '
                                                                  "'INVOKE|'; }\n"
                                                                  '    public function __toString(): string '
                                                                  "{ echo 'T|'; return 'converted'; }\n"
                                                                  '}\n'
                                                                  'class ReceiveDualFallback248 {\n'
                                                                  '    public static function '
                                                                  'take(callable|string &...$items) {\n'
                                                                  "        echo 'B:', $items[0] === "
                                                                  "'converted' ? 'string' : 'other', '|';\n"
                                                                  '    }\n'
                                                                  '}\n'
                                                                  "$method = 'missing';\n"
                                                                  "$input = ['self', &$method];\n"
                                                                  'set_error_handler(function ($level, '
                                                                  '$message) use (&$input) {\n'
                                                                  "    echo 'D|'; $input = new "
                                                                  'ReceiveDualStringable248; return true;\n'
                                                                  '});\n'
                                                                  'ReceiveDualFallback248::take($input);\n'
                                                                  "echo 'A:', $input, '|';\n"
                                                                  'restore_error_handler();\n',
                                                        'stage': 'S.CURRENT = (pcallcontext_string) -- if '
                                                                 'pcallcontext_string.TARGET = METHOD_TARGET '
                                                                 'n_converter porigin_string -- if S.FRAMES '
                                                                 '= pframe_receive :: pframe_tail* -- if '
                                                                 'pframe_receive.TODO = [STRINGIFY_RESULT '
                                                                 'n_converter porigin_site z, '
                                                                 'CALLABLE_STRING_RESULT (VARIADIC_RECEIVE '
                                                                 'porigin_receive n_argument) (REFERENCE '
                                                                 'n_input) n_converter n_parameter z]',
                                                        'checks': ['n_argument = 0 /\\ n_parameter = 0',
                                                                   'pcallcontext_string.RECEIVER = '
                                                                   '(n_converter)',
                                                                   'pframe_receive.CONTEXT = '
                                                                   '(pcallcontext_receive)',
                                                                   'pcallcontext_receive.FUNCTION = '
                                                                   'porigin_receive',
                                                                   'pcallcontext_receive.EXTRA = [REFERENCE '
                                                                   'n_input]',
                                                                   'pframe_receive.LOCALS = '
                                                                   '(psymboltable_receive)',
                                                                   'S_receive = $set_active_table(S[.CURRENT '
                                                                   '= pframe_receive.CONTEXT][.ORIGIN = '
                                                                   'pframe_receive.ORIGIN][.TODO = '
                                                                   'pframe_receive.TODO][.FRAMES = '
                                                                   'pframe_tail*], psymboltable_receive)',
                                                                   'S.STORE[n_input] = DEFINED (POBJECT '
                                                                   'n_converter)',
                                                                   '(HOBJECT n_converter) <- S.ALLOCATIONS',
                                                                   'S.OBJECTS[n_converter] = INSTANCE '
                                                                   'porigin_converter',
                                                                   '$class_at(S.CLASSES, porigin_converter) '
                                                                   '= (pclassdesc_converter)',
                                                                   'pclassdesc_converter.NAME = '
                                                                   '$ptascii("ReceiveDualStringable248")',
                                                                   '$typed_callable(S_receive, POBJECT '
                                                                   'n_converter) = (true)',
                                                                   '$user_string_coercion(S_receive, '
                                                                   '$api_fallback_parameter(S_receive, '
                                                                   'VARIADIC_RECEIVE porigin_receive '
                                                                   '0).TYPE, POBJECT n_converter, false) = '
                                                                   'false',
                                                                   'ptask_result = CALLABLE_STRING_RESULT '
                                                                   '(VARIADIC_RECEIVE porigin_receive '
                                                                   'n_argument) (REFERENCE n_input) '
                                                                   'n_converter n_parameter z',
                                                                   '$task_nodes(ptask_result) = [HCELL '
                                                                   'n_input, HOBJECT n_converter]',
                                                                   '$call_task_valid(S_receive, '
                                                                   'ptask_result)',
                                                                   '$receive_string_scope_valid(S, '
                                                                   'ptask_result)',
                                                                   '$stringify_source(S, porigin_site, z, '
                                                                   'ptask_result)',
                                                                   '$lookup(S_receive.ENV, '
                                                                   '$ptascii("items")) = (n_collector)',
                                                                   'S.STORE[n_collector] = DEFINED (PARRAY '
                                                                   'n_collected)',
                                                                   'S.ARRAYS[n_collected].ITEMS = eps',
                                                                   '$call_descriptors_valid(S)',
                                                                   '$class_state_valid(S)',
                                                                   '$closure_state_valid(S)',
                                                                   '$heap_valid($heap_graph(S))',
                                                                   '~$call_task_valid(S_receive, '
                                                                   'CALLABLE_STRING_RESULT (VARIADIC_RECEIVE '
                                                                   'porigin_receive 1) (REFERENCE n_input) '
                                                                   'n_converter n_parameter z)',
                                                                   'n_bad_cell = |S.STORE|',
                                                                   '~$call_task_valid(S_receive, '
                                                                   'CALLABLE_STRING_RESULT (VARIADIC_RECEIVE '
                                                                   'porigin_receive 0) (REFERENCE '
                                                                   'n_bad_cell) n_converter n_parameter z)',
                                                                   'n_bad_object = |S.OBJECTS|',
                                                                   '~$call_task_valid(S_receive, '
                                                                   'CALLABLE_STRING_RESULT (VARIADIC_RECEIVE '
                                                                   'porigin_receive 0) (REFERENCE n_input) '
                                                                   'n_bad_object n_parameter z)',
                                                                   '~$call_task_valid(S_receive, '
                                                                   'CALLABLE_STRING_RESULT (VARIADIC_RECEIVE '
                                                                   'porigin_receive 0) (REFERENCE n_input) '
                                                                   'n_converter 1 z)',
                                                                   '~$call_task_valid(S_receive, '
                                                                   'CALLABLE_STRING_RESULT (VARIADIC_RECEIVE '
                                                                   'porigin_receive 0) (REFERENCE n_input) '
                                                                   'n_converter n_parameter $(z + 100))',
                                                                   '~$call_task_valid(S_receive, '
                                                                   'CALLABLE_STRING_RESULT (TYPE_RECEIVE '
                                                                   'porigin_receive 0) (REFERENCE n_input) '
                                                                   'n_converter n_parameter z)',
                                                                   '~$call_task_valid(S_receive, '
                                                                   'CALLABLE_STRING_RESULT DISCARD '
                                                                   '(REFERENCE n_input) n_converter '
                                                                   'n_parameter z)',
                                                                   'S_budget = $drive(S, 0)',
                                                                   'S_budget.COMPLETION = BUDGET',
                                                                   '$call_descriptors_valid(S_budget)',
                                                                   '$heap_valid($heap_graph(S_budget))',
                                                                   'S_done = $drive(S_budget[.COMPLETION = '
                                                                   'NORMAL], 3000)',
                                                                   'S_done.COMPLETION = NORMAL',
                                                                   '$capture_outputs(S_done.EVENTS) = '
                                                                   '$ptascii("D|T|B:string|A:converted|")',
                                                                   'S_done.STORE[n_input] = DEFINED (PSTRING '
                                                                   '$ptascii("converted"))',
                                                                   'S_done.CURRENT = eps /\\ S_done.FRAMES = '
                                                                   'eps',
                                                                   'S_done.ERRORHANDLER.CALLBACK = eps /\\ '
                                                                   'S_done.ERRORHANDLERS = eps',
                                                                   '~((HARRAY n_collected) <- '
                                                                   'S_done.ALLOCATIONS)',
                                                                   '$heap_owners($heap_graph(S_done), HARRAY '
                                                                   'n_collected) = 0',
                                                                   '~((HOBJECT n_converter) <- '
                                                                   'S_done.ALLOCATIONS)',
                                                                   '$heap_owners($heap_graph(S_done), '
                                                                   'HOBJECT n_converter) = 0',
                                                                   '$call_descriptors_valid(S_done)',
                                                                   '$class_state_valid(S_done)',
                                                                   '$closure_state_valid(S_done)',
                                                                   '$heap_valid($heap_graph(S_done))']},
 'default-warning-keeps-receiving-scope-and-formal-owner': {'source': '<?php\n'
                                                                      'class ReceiveConstantOwner248 { '
                                                                      "public const CB = ['self', 'only']; "
                                                                      '}\n'
                                                                      'class ReceivePermission248 {\n'
                                                                      '    private static function only() '
                                                                      '{}\n'
                                                                      '    public static function '
                                                                      'take(callable $cb = '
                                                                      'ReceiveConstantOwner248::CB, int $tag '
                                                                      '= 0) {\n'
                                                                      "        echo 'B:', self::class, ':', "
                                                                      "static::class, ':', $tag, '|';\n"
                                                                      '    }\n'
                                                                      '}\n'
                                                                      'class ReceivePermissionChild248 '
                                                                      'extends ReceivePermission248 {}\n'
                                                                      'class ReceiveForeignCaller248 {\n'
                                                                      '    public static function go() {\n'
                                                                      '        '
                                                                      'ReceivePermissionChild248::take();\n'
                                                                      '        '
                                                                      'ReceivePermissionChild248::take(tag: '
                                                                      '3);\n'
                                                                      '    }\n'
                                                                      '}\n'
                                                                      'set_error_handler(function ($level, '
                                                                      "$message) { echo 'D|'; return true; "
                                                                      '});\n'
                                                                      'ReceiveForeignCaller248::go();\n'
                                                                      'restore_error_handler();\n',
                                                            'stage': 'S.CURRENT = (pcallcontext_handler) -- '
                                                                     'if pcallcontext_handler.TARGET = '
                                                                     'CLOSURE_TARGET n_handler -- if '
                                                                     'S.FRAMES = pframe_receive :: '
                                                                     'pframe_tail* -- if pframe_receive.TODO '
                                                                     '= (ERROR_HANDLER_RESULT perrorcall) :: '
                                                                     'ptask_receive* -- if perrorcall.RESUME '
                                                                     '= API_CALLABLE_RESULT papiquery 0 -- '
                                                                     'if papiquery.SOURCE = '
                                                                     'CALLABLE_DEFAULT_RECEIVE '
                                                                     'porigin_receive n_parameter',
                                                            'checks': ['n_parameter = 0',
                                                                       'pframe_receive.CONTEXT = '
                                                                       '(pcallcontext_receive)',
                                                                       'pcallcontext_receive.FUNCTION = '
                                                                       'porigin_receive',
                                                                       'pcallcontext_receive.ARGC = 0 /\\ '
                                                                       'pcallcontext_receive.HOLES = eps',
                                                                       'pframe_receive.LOCALS = '
                                                                       '(psymboltable_receive)',
                                                                       'pframe_receive.CONSTCONTEXT = eps',
                                                                       '$lookup(psymboltable_receive.ENV, '
                                                                       '$ptascii("cb")) = (n_formal)',
                                                                       '$lookup(S.ENV, $ptascii("cb")) = eps',
                                                                       'S.STORE[n_formal] = DEFINED '
                                                                       'papiquery.VALUE',
                                                                       '(HCELL n_formal) <- S.ALLOCATIONS',
                                                                       'papiquery.VALUE = PARRAY n_raw',
                                                                       'papiquery.INPUT = PSTRING '
                                                                       '$ptascii("self")',
                                                                       'papiquery.METHOD = DIRECT (PSTRING '
                                                                       '$ptascii("only"))',
                                                                       'papiquery.SCOPE = '
                                                                       'pcallcontext_receive.LEXICAL_CLASS',
                                                                       'papiquery.CALLED = '
                                                                       'pcallcontext_receive.CALLED_CLASS',
                                                                       'papiquery.THIS = eps /\\ '
                                                                       'pcallcontext_receive.RECEIVER = eps',
                                                                       'pcallcontext_handler.LEXICAL_CLASS = '
                                                                       'eps',
                                                                       '$class_at(S.CLASSES, '
                                                                       'papiquery.CLASS.REQUESTED) = '
                                                                       '(pclassdesc_receive)',
                                                                       'pclassdesc_receive.NAME = '
                                                                       '$ptascii("ReceivePermission248")',
                                                                       'papiquery.CALLED = (porigin_called)',
                                                                       '$class_at(S.CLASSES, porigin_called) '
                                                                       '= (pclassdesc_called)',
                                                                       'pclassdesc_called.NAME = '
                                                                       '$ptascii("ReceivePermissionChild248")',
                                                                       '$class_named(S.CLASSNAMES, '
                                                                       '$ptlc($ptascii("ReceiveConstantOwner248"))) '
                                                                       '= (porigin_constant)',
                                                                       '(porigin_constant) =/= '
                                                                       'papiquery.SCOPE',
                                                                       '(HARRAY n_raw) <- S.ALLOCATIONS',
                                                                       '$($heap_owners($heap_graph(S), '
                                                                       'HARRAY n_raw) >= 2)',
                                                                       '$task_nodes(API_CALLABLE_RESULT '
                                                                       'papiquery 0) = eps',
                                                                       'S_receive = '
                                                                       '$api_saved_frame_scope(S, '
                                                                       'pframe_receive, pframe_tail*)',
                                                                       'S_receive.CURRENT = '
                                                                       '(pcallcontext_receive)',
                                                                       'S_receive.ENV = '
                                                                       'psymboltable_receive.ENV',
                                                                       'S_receive.FRAMES = pframe_tail*',
                                                                       '$api_query_valid(S_receive, '
                                                                       'papiquery, 0)',
                                                                       '$error_entered_call_valid(S_receive, '
                                                                       'perrorcall)',
                                                                       '~$api_query_valid(S, papiquery, 0)',
                                                                       '~$api_query_valid(S_receive, '
                                                                       'papiquery[.SOURCE = TYPE_RECEIVE '
                                                                       'porigin_receive 0], 0)',
                                                                       '~$api_query_valid(S_receive, '
                                                                       'papiquery[.SOURCE = '
                                                                       'CALLABLE_DEFAULT_RECEIVE '
                                                                       'porigin_receive 1], 0)',
                                                                       '~$api_query_valid(S_receive, '
                                                                       'papiquery[.SCOPE = '
                                                                       '(porigin_constant)], 0)',
                                                                       '~$api_query_valid(S_receive, '
                                                                       'papiquery[.CALLED = '
                                                                       'papiquery.SCOPE], 0)',
                                                                       '~$api_query_valid(S_receive, '
                                                                       'papiquery[.LINE = $(papiquery.LINE + '
                                                                       '100)], 0)',
                                                                       '~$api_query_valid(S_receive, '
                                                                       'papiquery, 1)',
                                                                       'S_bad = S[.FRAMES = '
                                                                       'pframe_receive[.CONTEXT = '
                                                                       '(pcallcontext_receive[.LEXICAL_CLASS '
                                                                       '= (porigin_constant)])] :: '
                                                                       'pframe_tail*]',
                                                                       '~$call_descriptors_valid(S_bad)',
                                                                       '$call_descriptors_valid(S)',
                                                                       '$class_state_valid(S)',
                                                                       '$closure_state_valid(S)',
                                                                       '$heap_valid($heap_graph(S))',
                                                                       'S_budget = $drive(S, 0)',
                                                                       'S_budget.COMPLETION = BUDGET',
                                                                       '$call_descriptors_valid(S_budget)',
                                                                       '$heap_valid($heap_graph(S_budget))',
                                                                       'S_done = $drive(S_budget[.COMPLETION '
                                                                       '= NORMAL], 3000)',
                                                                       'S_done.COMPLETION = NORMAL',
                                                                       '$capture_outputs(S_done.EVENTS) = '
                                                                       '$ptascii("D|B:ReceivePermission248:ReceivePermissionChild248:0|D|B:ReceivePermission248:ReceivePermissionChild248:3|")',
                                                                       'S_done.CURRENT = eps /\\ '
                                                                       'S_done.FRAMES = eps',
                                                                       'S_done.ERRORHANDLER.CALLBACK = eps '
                                                                       '/\\ S_done.ERRORHANDLERS = eps',
                                                                       '~((HCELL n_formal) <- '
                                                                       'S_done.ALLOCATIONS)',
                                                                       '~((HOBJECT n_handler) <- '
                                                                       'S_done.ALLOCATIONS)',
                                                                       '(HARRAY n_raw) <- S_done.ALLOCATIONS',
                                                                       '$call_descriptors_valid(S_done)',
                                                                       '$class_state_valid(S_done)',
                                                                       '$closure_state_valid(S_done)',
                                                                       '$heap_valid($heap_graph(S_done))']},
 'variadic-replaced-reference-keeps-borrowed-method-after-array-retirement': {'source': '<?php\n'
                                                                                        'class '
                                                                                        'ReceiveRetired248 '
                                                                                        '{\n'
                                                                                        '    private static '
                                                                                        'function ok() {}\n'
                                                                                        '    public static '
                                                                                        'function '
                                                                                        'take(callable '
                                                                                        '&...$items) { echo '
                                                                                        "'B:', $items[0], "
                                                                                        "'|'; }\n"
                                                                                        '}\n'
                                                                                        "$method = 'ok';\n"
                                                                                        "$input = ['self', "
                                                                                        '&$method];\n'
                                                                                        'set_error_handler(function '
                                                                                        '($level, $message) '
                                                                                        'use (&$input) {\n'
                                                                                        "    echo 'D|'; "
                                                                                        '$input = 7; return '
                                                                                        'true;\n'
                                                                                        '});\n'
                                                                                        'ReceiveRetired248::take($input);\n'
                                                                                        "echo 'A:', $input, "
                                                                                        "':', $method, '|';\n"
                                                                                        'restore_error_handler();\n',
                                                                              'stage': 'S.TODO = '
                                                                                       '(API_CALLABLE_RESULT '
                                                                                       'papiquery 0) :: '
                                                                                       'ptask_tail* -- if '
                                                                                       'papiquery.SOURCE = '
                                                                                       'VARIADIC_RECEIVE '
                                                                                       'porigin_receive '
                                                                                       'n_argument',
                                                                              'checks': ['S.CURRENT = '
                                                                                         '(pcallcontext)',
                                                                                         'pcallcontext.FUNCTION '
                                                                                         '= porigin_receive',
                                                                                         'pcallcontext.ARGC '
                                                                                         '= 1 /\\ '
                                                                                         'pcallcontext.NAMED '
                                                                                         '= eps',
                                                                                         'n_argument = 0',
                                                                                         '$function_at($all_functions(S), '
                                                                                         'porigin_receive) = '
                                                                                         '(pfunction)',
                                                                                         '$call_fixed_parameters(pfunction.SIGNATURE.PARAMETERS) '
                                                                                         '= eps',
                                                                                         'pfunction.SIGNATURE.PARAMETERS[0].VARIADIC',
                                                                                         'pfunction.SIGNATURE.PARAMETERS[0].BYREF',
                                                                                         'pcallcontext.EXTRA '
                                                                                         '= [REFERENCE '
                                                                                         'n_input]',
                                                                                         'S.STORE[n_input] = '
                                                                                         'DEFINED (PINT 7)',
                                                                                         '(HCELL n_input) <- '
                                                                                         'S.ALLOCATIONS /\\ '
                                                                                         'n_input <- '
                                                                                         'S.REFCELLS',
                                                                                         'papiquery.VALUE = '
                                                                                         'PARRAY n_raw',
                                                                                         'papiquery.INPUT = '
                                                                                         'PSTRING '
                                                                                         '$ptascii("self")',
                                                                                         'papiquery.METHOD = '
                                                                                         'ALIAS n_method',
                                                                                         'papiquery.ORIGINAL '
                                                                                         '= $ptascii("ok")',
                                                                                         'papiquery.PREFIX = '
                                                                                         '0 /\\ '
                                                                                         'papiquery.WIDTH = '
                                                                                         '0 /\\ '
                                                                                         'papiquery.OUTER = '
                                                                                         'eps',
                                                                                         'S.STORE[n_method] '
                                                                                         '= DEFINED (PSTRING '
                                                                                         '$ptascii("ok"))',
                                                                                         '(HCELL n_method) '
                                                                                         '<- S.ALLOCATIONS '
                                                                                         '/\\ n_method <- '
                                                                                         'S.REFCELLS',
                                                                                         '$entry_lookup(S.ARRAYS[n_raw].ITEMS, '
                                                                                         'KINT 1) = (ALIAS '
                                                                                         'n_method)',
                                                                                         '~((HARRAY n_raw) '
                                                                                         '<- S.ALLOCATIONS)',
                                                                                         '$heap_owners($heap_graph(S), '
                                                                                         'HARRAY n_raw) = 0',
                                                                                         '$task_nodes(API_CALLABLE_RESULT '
                                                                                         'papiquery 0) = eps',
                                                                                         'papiquery.SCOPE = '
                                                                                         'pcallcontext.LEXICAL_CLASS',
                                                                                         'papiquery.CALLED = '
                                                                                         'pcallcontext.CALLED_CLASS',
                                                                                         'papiquery.THIS = '
                                                                                         'eps /\\ '
                                                                                         'pcallcontext.RECEIVER '
                                                                                         '= eps',
                                                                                         '$class_at(S.CLASSES, '
                                                                                         'papiquery.CLASS.REQUESTED) '
                                                                                         '= (pclassdesc)',
                                                                                         'pclassdesc.NAME = '
                                                                                         '$ptascii("ReceiveRetired248")',
                                                                                         '$lookup(S.ENV, '
                                                                                         '$ptascii("items")) '
                                                                                         '= (n_collector)',
                                                                                         'S.STORE[n_collector] '
                                                                                         '= DEFINED (PARRAY '
                                                                                         'n_collected)',
                                                                                         'S.ARRAYS[n_collected].ITEMS '
                                                                                         '= eps',
                                                                                         '(HARRAY '
                                                                                         'n_collected) <- '
                                                                                         'S.ALLOCATIONS',
                                                                                         '$api_query_valid(S, '
                                                                                         'papiquery, 0)',
                                                                                         '$call_descriptors_valid(S)',
                                                                                         '$class_state_valid(S)',
                                                                                         '$closure_state_valid(S)',
                                                                                         '$heap_valid($heap_graph(S))',
                                                                                         '~$api_query_valid(S, '
                                                                                         'papiquery[.SOURCE '
                                                                                         '= VARIADIC_RECEIVE '
                                                                                         'porigin_receive '
                                                                                         '1], 0)',
                                                                                         '~$api_query_valid(S, '
                                                                                         'papiquery[.SOURCE '
                                                                                         '= '
                                                                                         'NAMED_VARIADIC_RECEIVE '
                                                                                         'porigin_receive '
                                                                                         '0], 0)',
                                                                                         '~$api_query_valid(S, '
                                                                                         'papiquery[.SOURCE '
                                                                                         '= TYPE_RECEIVE '
                                                                                         'porigin_receive '
                                                                                         '0], 0)',
                                                                                         '~$api_query_valid(S, '
                                                                                         'papiquery[.METHOD '
                                                                                         '= DIRECT (PSTRING '
                                                                                         '$ptascii("ok"))], '
                                                                                         '0)',
                                                                                         'n_bad_cell = '
                                                                                         '|S.STORE|',
                                                                                         '~$api_query_valid(S, '
                                                                                         'papiquery[.METHOD '
                                                                                         '= ALIAS '
                                                                                         'n_bad_cell], 0)',
                                                                                         'n_bad_array = '
                                                                                         '|S.ARRAYS|',
                                                                                         '~$api_query_valid(S, '
                                                                                         'papiquery[.VALUE = '
                                                                                         'PARRAY '
                                                                                         'n_bad_array], 0)',
                                                                                         '~$api_query_valid(S[.ARRAYS[n_raw].ITEMS '
                                                                                         '= eps], papiquery, '
                                                                                         '0)',
                                                                                         '~$api_query_valid(S, '
                                                                                         'papiquery[.SCOPE = '
                                                                                         'eps], 0)',
                                                                                         '~$api_query_valid(S, '
                                                                                         'papiquery[.LINE = '
                                                                                         '$(papiquery.LINE + '
                                                                                         '100)], 0)',
                                                                                         '~$api_query_valid(S, '
                                                                                         'papiquery, 1)',
                                                                                         'S_budget = '
                                                                                         '$drive(S, 0)',
                                                                                         'S_budget.COMPLETION '
                                                                                         '= BUDGET',
                                                                                         '$call_descriptors_valid(S_budget)',
                                                                                         '$heap_valid($heap_graph(S_budget))',
                                                                                         'S_done = '
                                                                                         '$drive(S_budget[.COMPLETION '
                                                                                         '= NORMAL], 3000)',
                                                                                         'S_done.COMPLETION '
                                                                                         '= NORMAL',
                                                                                         '$capture_outputs(S_done.EVENTS) '
                                                                                         '= '
                                                                                         '$ptascii("D|B:7|A:7:ok|")',
                                                                                         'S_done.CURRENT = '
                                                                                         'eps /\\ '
                                                                                         'S_done.FRAMES = '
                                                                                         'eps',
                                                                                         'S_done.ERRORHANDLER.CALLBACK '
                                                                                         '= eps /\\ '
                                                                                         'S_done.ERRORHANDLERS '
                                                                                         '= eps',
                                                                                         '~((HARRAY n_raw) '
                                                                                         '<- '
                                                                                         'S_done.ALLOCATIONS)',
                                                                                         '~((HARRAY '
                                                                                         'n_collected) <- '
                                                                                         'S_done.ALLOCATIONS)',
                                                                                         '$heap_owners($heap_graph(S_done), '
                                                                                         'HARRAY n_raw) = 0',
                                                                                         '$heap_owners($heap_graph(S_done), '
                                                                                         'HARRAY '
                                                                                         'n_collected) = 0',
                                                                                         'S_done.STORE[n_input] '
                                                                                         '= DEFINED (PINT 7)',
                                                                                         'S_done.STORE[n_method] '
                                                                                         '= DEFINED (PSTRING '
                                                                                         '$ptascii("ok"))',
                                                                                         '$call_descriptors_valid(S_done)',
                                                                                         '$class_state_valid(S_done)',
                                                                                         '$closure_state_valid(S_done)',
                                                                                         '$heap_valid($heap_graph(S_done))']},
 'second-lossy-warning-throw-keeps-frozen-result-uncommitted': {'source': '<?php\n'
                                                                          'class ReceiveLossyThrow248 {\n'
                                                                          '    public static function '
                                                                          'take(callable|int &...$items) { '
                                                                          "echo 'BODY|'; }\n"
                                                                          '}\n'
                                                                          "$input = 'self::xx';\n"
                                                                          '$hits = 0;\n'
                                                                          'set_error_handler(function '
                                                                          '($level, $message) use (&$input, '
                                                                          '&$hits) {\n'
                                                                          '    $hits++;\n'
                                                                          "    echo 'D:', $message, '|';\n"
                                                                          '    if ($hits === 1) { $input = '
                                                                          "'123456.5'; }\n"
                                                                          '    else {\n'
                                                                          '        try { throw new '
                                                                          "Exception('loss'); }\n"
                                                                          "        finally { echo 'F|'; "
                                                                          '$input = 77; }\n'
                                                                          '    }\n'
                                                                          '    return true;\n'
                                                                          '});\n'
                                                                          'try { '
                                                                          'ReceiveLossyThrow248::take($input); '
                                                                          '}\n'
                                                                          'catch (Exception $error) { echo '
                                                                          "'C:', $error->getMessage(), '|'; "
                                                                          '}\n'
                                                                          "echo 'A:', $input, ':', $hits, "
                                                                          "'|';\n"
                                                                          'restore_error_handler();\n',
                                                                'stage': 'S.TODO = (THROW_SEARCH n_error) :: '
                                                                         'ptask_handler* -- if S.CURRENT = '
                                                                         '(pcallcontext_handler) -- if '
                                                                         'pcallcontext_handler.TARGET = '
                                                                         'CLOSURE_TARGET n_handler -- if '
                                                                         'S.FRAMES = pframe_receive :: '
                                                                         'pframe_tail* -- if '
                                                                         'pframe_receive.TODO = '
                                                                         '(ERROR_HANDLER_RESULT perrorcall) '
                                                                         ':: ptask_receive* -- if '
                                                                         'perrorcall.RESUME = '
                                                                         'CALLABLE_SCALAR_RESULT '
                                                                         '(VARIADIC_RECEIVE porigin_receive '
                                                                         'n_argument) (REFERENCE n_input) '
                                                                         '(PSTRING ptbytes_input) i -- if '
                                                                         'S.STORE[n_input] = DEFINED (PINT '
                                                                         '77)',
                                                                'checks': ['n_argument = 0 /\\ i = 123456',
                                                                           'ptbytes_input = '
                                                                           '$ptascii("123456.5")',
                                                                           'pframe_receive.CONTEXT = '
                                                                           '(pcallcontext_receive)',
                                                                           'pcallcontext_receive.FUNCTION = '
                                                                           'porigin_receive',
                                                                           'pcallcontext_receive.EXTRA = '
                                                                           '[REFERENCE n_input]',
                                                                           'pframe_receive.LOCALS = '
                                                                           '(psymboltable_receive)',
                                                                           'S_receive = '
                                                                           '$api_saved_frame_scope(S, '
                                                                           'pframe_receive, pframe_tail*)',
                                                                           'S_receive.CURRENT = '
                                                                           '(pcallcontext_receive)',
                                                                           'S_receive.ENV = '
                                                                           'psymboltable_receive.ENV',
                                                                           'S_receive.FRAMES = pframe_tail*',
                                                                           'ptask_result = perrorcall.RESUME',
                                                                           '$api_pending_task(ptask_result)',
                                                                           '$call_task_valid(S_receive, '
                                                                           'ptask_result)',
                                                                           '$error_call_valid(S_receive, '
                                                                           'perrorcall)',
                                                                           '$error_entered_call_valid(S_receive, '
                                                                           'perrorcall)',
                                                                           '~$call_task_valid(S, '
                                                                           'ptask_result)',
                                                                           'perrorcall.LEVEL = 8192',
                                                                           'S.ERRORHANDLER.CALLBACK = eps',
                                                                           '(HCELL n_input) <- S.ALLOCATIONS '
                                                                           '/\\ n_input <- S.REFCELLS',
                                                                           '$task_nodes(ptask_result) = '
                                                                           '[HCELL n_input]',
                                                                           '$lookup(S_receive.ENV, '
                                                                           '$ptascii("items")) = '
                                                                           '(n_collector)',
                                                                           'S.STORE[n_collector] = DEFINED '
                                                                           '(PARRAY n_collected)',
                                                                           'S.ARRAYS[n_collected].ITEMS = '
                                                                           'eps',
                                                                           '(HARRAY n_collected) <- '
                                                                           'S.ALLOCATIONS',
                                                                           '$call_descriptors_valid(S)',
                                                                           '$class_state_valid(S)',
                                                                           '$closure_state_valid(S)',
                                                                           '$heap_valid($heap_graph(S))',
                                                                           'S_done = $drive(S, 3000)',
                                                                           'S_done.COMPLETION = NORMAL',
                                                                           '$capture_outputs(S_done.EVENTS) '
                                                                           '= $ptascii("D:Use of \\"self\\" '
                                                                           'in callables is '
                                                                           'deprecated|D:Implicit conversion '
                                                                           'from float-string \\"123456.5\\" '
                                                                           'to int loses '
                                                                           'precision|F|C:loss|A:77:2|")',
                                                                           'S_done.STORE[n_input] = DEFINED '
                                                                           '(PINT 77)',
                                                                           'S_done.CURRENT = eps /\\ '
                                                                           'S_done.FRAMES = eps',
                                                                           'S_done.ERRORHANDLER.CALLBACK = '
                                                                           'eps /\\ S_done.ERRORHANDLERS = '
                                                                           'eps',
                                                                           '~((HARRAY n_collected) <- '
                                                                           'S_done.ALLOCATIONS)',
                                                                           '$heap_owners($heap_graph(S_done), '
                                                                           'HARRAY n_collected) = 0',
                                                                           '~((HOBJECT n_handler) <- '
                                                                           'S_done.ALLOCATIONS)',
                                                                           '$heap_owners($heap_graph(S_done), '
                                                                           'HOBJECT n_handler) = 0',
                                                                           '$call_descriptors_valid(S_done)',
                                                                           '$class_state_valid(S_done)',
                                                                           '$closure_state_valid(S_done)',
                                                                           '$heap_valid($heap_graph(S_done))']}}

if __name__ == '__main__':
    protocol.MODULES.append(Path(__file__).with_name('from_callable_protocol.watsup'))
    protocol.run(CASES, extra_inputs=(Path(__file__),))
