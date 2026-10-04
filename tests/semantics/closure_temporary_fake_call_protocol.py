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
                                                         'S_done.ERRORHANDLER.CALLBACK = eps']}}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--match', default='')
    args = parser.parse_args()
    selected = {name: case for name, case in CASES.items() if args.match in name}
    assert selected
    helper = Path(__file__).with_suffix('.watsup')
    protocol.MODULES.append(helper)
    protocol.run(selected, extra_inputs=(Path(__file__), helper))
