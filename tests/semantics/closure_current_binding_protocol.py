#!/usr/bin/env python3
"""Current identity, copied binding history, receiver owners and warning unwind."""
from pathlib import Path
import argparse

import closure_call_protocol as protocol

CASES = {'bound-private-method-shared-statics-retired-source': {'source': '<?php\n'
                                                                  'class FakeOwner253 {\n'
                                                                  '    public int $id;\n'
                                                                  '    public function '
                                                                  '__construct(int $id) { '
                                                                  '$this->id = $id; }\n'
                                                                  '    private function tick() {\n'
                                                                  '        static $n = 0;\n'
                                                                  "        echo self::class, ':', "
                                                                  "get_called_class(), ':', "
                                                                  "$this->id, ':', ++$n, '|';\n"
                                                                  '    }\n'
                                                                  '    public function capture() { '
                                                                  'return '
                                                                  'Closure::fromCallable([$this, '
                                                                  "'tick']); }\n"
                                                                  '}\n'
                                                                  'class FakeChild253 extends '
                                                                  'FakeOwner253 {}\n'
                                                                  '$original = new '
                                                                  'FakeOwner253(1);\n'
                                                                  '$cap = $original->capture();\n'
                                                                  '$new = new FakeChild253(2);\n'
                                                                  '$bound = $cap->bindTo($new);\n'
                                                                  '$same = Closure::bind($cap, '
                                                                  '$new, FakeOwner253::class);\n'
                                                                  '$copy = clone $bound;\n'
                                                                  'echo ($same == $bound ? 1 : 0), '
                                                                  "':', ($same === $bound ? 1 : "
                                                                  "0), ':', ($copy == $bound ? 1 : "
                                                                  "0), '|';\n"
                                                                  '$cap();\n'
                                                                  'unset($original, $cap, $new);\n'
                                                                  '$bound();\n'
                                                                  '$same();\n'
                                                                  '$copy();\n'
                                                                  'unset($bound,$same,$copy);\n',
                                                        'stage': 'S.TODO = (ARGINFO_INVOKE '
                                                                 'pargcall) :: ptask_tail* -- if '
                                                                 'pargcall.KIND = '
                                                                 'INTRINSIC_GET_CALLED_CLASS -- if '
                                                                 'S.CURRENT = (pcallcontext) -- if '
                                                                 'pcallcontext.TARGET = '
                                                                 'CLOSURE_TARGET n_bound -- if '
                                                                 'S.OBJECTS[n_bound] = '
                                                                 'BOUNDFAKECLOSURE pboundfake',
                                                        'checks': ['$bound_fake_valid(S, n_bound)',
                                                                   'pboundfake.SOURCE = n_source',
                                                                   '~((HOBJECT n_source) <- '
                                                                   'S.ALLOCATIONS)',
                                                                   'S.OBJECTS[n_source] = '
                                                                   'FROMCALLABLECLOSURE '
                                                                   'pfrommethod',
                                                                   'pfrommethod.CLASS.RECEIVER = '
                                                                   '(n_old)',
                                                                   '~((HOBJECT n_old) <- '
                                                                   'S.ALLOCATIONS)',
                                                                   'pboundfake.RECEIVER = '
                                                                   '(n_receiver)',
                                                                   'pboundfake.SCOPE = BIND_CLASS '
                                                                   'porigin_owner',
                                                                   'pboundfake.CALLED = BIND_CLASS '
                                                                   'porigin_child',
                                                                   'S.OBJECTS[n_receiver] = '
                                                                   'INSTANCE porigin_child',
                                                                   'pcallcontext.INSTANCE = '
                                                                   '(n_bound)',
                                                                   'pcallcontext.LEXICAL_CLASS = '
                                                                   '(porigin_owner)',
                                                                   'pcallcontext.CALLED_CLASS = '
                                                                   '(porigin_child)',
                                                                   'pcallcontext.RECEIVER = '
                                                                   '(n_receiver)',
                                                                   '$class_method_origin(S.CLASSES, '
                                                                   'pcallcontext.FUNCTION) = '
                                                                   '(pmethoddesc)',
                                                                   'pmethoddesc.VISIBILITY = '
                                                                   'PROPERTY_PRIVATE',
                                                                   'pmethoddesc.NAME = '
                                                                   '$ptascii("tick")',
                                                                   '$closure_current_object(S) = '
                                                                   'eps',
                                                                   '$node_children(S, HOBJECT '
                                                                   'n_bound) = [HOBJECT '
                                                                   'n_receiver]',
                                                                   '~(HOBJECT n_source <- '
                                                                   '$node_children(S, HOBJECT '
                                                                   'n_bound))',
                                                                   '~(HOBJECT n_old <- '
                                                                   '$node_children(S, HOBJECT '
                                                                   'n_bound))',
                                                                   '$call_descriptors_valid(S)',
                                                                   '$closure_state_valid(S)',
                                                                   '$heap_valid($heap_graph(S))',
                                                                   '~$bound_fake_valid(S[.OBJECTS[n_bound] '
                                                                   '= BOUNDFAKECLOSURE '
                                                                   'pboundfake[.RECEIVER = '
                                                                   '(n_old)]], n_bound)',
                                                                   '~$bound_fake_valid(S[.OBJECTS[n_bound] '
                                                                   '= BOUNDFAKECLOSURE '
                                                                   'pboundfake[.SCOPE = '
                                                                   'BIND_UNSCOPED]], n_bound)',
                                                                   '~$call_current_valid(S[.CURRENT '
                                                                   '= (pcallcontext[.LEXICAL_CLASS '
                                                                   '= (porigin_child)])])',
                                                                   '~$call_current_valid(S[.CURRENT '
                                                                   '= (pcallcontext[.INSTANCE = '
                                                                   '(n_source)])])',
                                                                   'S_budget = $drive(S, 0)',
                                                                   'S_budget.COMPLETION = BUDGET',
                                                                   '$call_descriptors_valid(S_budget)',
                                                                   '$closure_state_valid(S_budget)',
                                                                   '$heap_valid($heap_graph(S_budget))',
                                                                   'S_done = '
                                                                   '$drive(S_budget[.COMPLETION = '
                                                                   'NORMAL], 3000)',
                                                                   'S_done.COMPLETION = NORMAL',
                                                                   'S_done.CURRENT = eps /\\ '
                                                                   'S_done.FRAMES = eps',
                                                                   '$call_descriptors_valid(S_done)',
                                                                   '$closure_state_valid(S_done)',
                                                                   '$heap_valid($heap_graph(S_done))',
                                                                   '$current_binding_outputs(S_done.EVENTS) '
                                                                   '= '
                                                                   '$ptascii("1:0:1|FakeOwner253:FakeOwner253:1:1|FakeOwner253:FakeChild253:2:2|FakeOwner253:FakeChild253:2:3|FakeOwner253:FakeChild253:2:4|")',
                                                                   '~((HOBJECT n_bound) <- '
                                                                   'S_done.ALLOCATIONS)',
                                                                   '~((HOBJECT n_receiver) <- '
                                                                   'S_done.ALLOCATIONS)',
                                                                   '~((HOBJECT n_old) <- '
                                                                   'S_done.ALLOCATIONS)']},
 'bound-getter-new-receiver-old-chain-retired': {'source': '<?php $old=new '
                                                           "Exception('old');$source=$old->getMessage(...);$new=new "
                                                           "Exception('new');$bound=$source->bindTo($new);$copy=clone "
                                                           '$bound;unset($old,$source,$new);echo '
                                                           "$bound(),':',$copy(),'|';unset($bound,$copy);",
                                                 'stage': 'S.TODO = (GETTER_INVOKE pgettercall) :: '
                                                          'ptask_tail* -- if pgettercall.CAPTURE = '
                                                          '(n_bound) -- if S.OBJECTS[n_bound] = '
                                                          'BOUNDFAKECLOSURE pboundfake',
                                                 'checks': ['pboundfake.SOURCE = n_source',
                                                            'S.OBJECTS[n_source] = GETTERCLOSURE '
                                                            'n_old GET_MESSAGE text_base '
                                                            'porigin_getter',
                                                            '~((HOBJECT n_source) <- '
                                                            'S.ALLOCATIONS)',
                                                            '~((HOBJECT n_old) <- S.ALLOCATIONS)',
                                                            'pboundfake.RECEIVER = (n_receiver)',
                                                            'pgettercall.RECEIVER = n_receiver',
                                                            'pboundfake.SCOPE = BIND_INTERNAL '
                                                            '$ptascii("Exception")',
                                                            'pboundfake.CALLED = BIND_INTERNAL '
                                                            '$ptascii("Exception")',
                                                            '$bound_fake_getter(S, n_bound) = '
                                                            '((n_receiver, GET_MESSAGE, '
                                                            'text_base))',
                                                            '$getter_call_valid(S, pgettercall)',
                                                            '$closure_callable(S, n_bound)',
                                                            '$node_children(S, HOBJECT n_bound) = '
                                                            '[HOBJECT n_receiver]',
                                                            '~(HOBJECT n_source <- '
                                                            '$task_nodes(GETTER_INVOKE '
                                                            'pgettercall))',
                                                            'HOBJECT n_bound <- '
                                                            '$task_nodes(GETTER_INVOKE '
                                                            'pgettercall)',
                                                            '$call_descriptors_valid(S)',
                                                            '$closure_state_valid(S)',
                                                            '$heap_valid($heap_graph(S))',
                                                            '~$getter_call_valid(S, '
                                                            'pgettercall[.METHOD = GET_CODE])',
                                                            '~$getter_call_valid(S, '
                                                            'pgettercall[.RECEIVER = n_old])',
                                                            '~$bound_fake_valid(S[.OBJECTS[n_bound] '
                                                            '= BOUNDFAKECLOSURE '
                                                            'pboundfake[.RECEIVER = eps]], '
                                                            'n_bound)',
                                                            'S_budget = $drive(S, 0)',
                                                            'S_budget.COMPLETION = BUDGET',
                                                            '$call_descriptors_valid(S_budget)',
                                                            '$closure_state_valid(S_budget)',
                                                            '$heap_valid($heap_graph(S_budget))',
                                                            'S_done = $drive(S_budget[.COMPLETION '
                                                            '= NORMAL], 3000)',
                                                            'S_done.COMPLETION = NORMAL',
                                                            'S_done.CURRENT = eps /\\ '
                                                            'S_done.FRAMES = eps',
                                                            '$call_descriptors_valid(S_done)',
                                                            '$closure_state_valid(S_done)',
                                                            '$heap_valid($heap_graph(S_done))',
                                                            '$current_binding_outputs(S_done.EVENTS) '
                                                            '= $ptascii("new:new|")',
                                                            '~((HOBJECT n_bound) <- '
                                                            'S_done.ALLOCATIONS)',
                                                            '~((HOBJECT n_receiver) <- '
                                                            'S_done.ALLOCATIONS)']},
 'bound-free-intrinsic-no-bound-receiver': {'source': '<?php class FreeHostState253{} '
                                                      '$source=get_class(...);$bound=$source->bindTo(new '
                                                      'FreeHostState253());$copy=clone '
                                                      '$bound;unset($source);echo $bound(new '
                                                      "FreeHostState253()),'|';unset($bound,$copy);",
                                            'stage': 'S.TODO = (GETCLASS_INVOKE pgetclasscall) :: '
                                                     'ptask_tail* -- if pgetclasscall.OWNER = '
                                                     '(n_bound) -- if S.OBJECTS[n_bound] = '
                                                     'BOUNDFAKECLOSURE pboundfake',
                                            'checks': ['pboundfake.SOURCE = n_source',
                                                       'S.OBJECTS[n_source] = INTRINSICCLOSURE '
                                                       'INTRINSIC_GET_CLASS',
                                                       '~((HOBJECT n_source) <- S.ALLOCATIONS)',
                                                       'pboundfake.SCOPE = BIND_UNSCOPED',
                                                       'pboundfake.CALLED = BIND_CLASS '
                                                       'porigin_host',
                                                       'pboundfake.RECEIVER = eps',
                                                       '$node_children(S, HOBJECT n_bound) = eps',
                                                       '$named_slot_at(pgetclasscall.SENT, 0) = '
                                                       'NAMED_SENT (KNOWN (POBJECT n_argument))',
                                                       'S.OBJECTS[n_argument] = INSTANCE '
                                                       'porigin_host',
                                                       'HOBJECT n_bound <- '
                                                       '$task_nodes(GETCLASS_INVOKE pgetclasscall)',
                                                       'HOBJECT n_argument <- '
                                                       '$task_nodes(GETCLASS_INVOKE pgetclasscall)',
                                                       '$closure_callable(S, n_bound)',
                                                       '$call_descriptors_valid(S)',
                                                       '$closure_state_valid(S)',
                                                       '$heap_valid($heap_graph(S))',
                                                       '~$bound_fake_receiver_valid(S, '
                                                       'pboundfake[.RECEIVER = (n_argument)])',
                                                       '~$bound_fake_valid(S[.OBJECTS[n_bound] = '
                                                       'BOUNDFAKECLOSURE pboundfake[.RECEIVER = '
                                                       '(n_argument)]], n_bound)',
                                                       '~$bound_fake_valid(S[.OBJECTS[n_bound] = '
                                                       'BOUNDFAKECLOSURE pboundfake[.SCOPE = '
                                                       'BIND_CLASS porigin_host]], n_bound)',
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
                                                       '$current_binding_outputs(S_done.EVENTS) = '
                                                       '$ptascii("FreeHostState253|")',
                                                       '~((HOBJECT n_bound) <- S_done.ALLOCATIONS)',
                                                       '~((HOBJECT n_argument) <- '
                                                       'S_done.ALLOCATIONS)']},
 'internal-child-clone-real-statics-parent-retired': {'source': '<?php\n'
                                                                'function dummyChildMaker253() {\n'
                                                                '    return function () {\n'
                                                                '        static $n = 0;\n'
                                                                "        return self::class . ':' "
                                                                ". get_called_class() . ':' . "
                                                                "get_class($this) . ':' . ++$n;\n"
                                                                '    };\n'
                                                                '}\n'
                                                                'class DummyChildHost253 {}\n'
                                                                '$fake = dummyChildMaker253(...);\n'
                                                                '$bound = $fake->bindTo(new '
                                                                'DummyChildHost253());\n'
                                                                '$child = $bound();\n'
                                                                '$child();\n'
                                                                '$copy = clone $child;\n'
                                                                'unset($fake, $bound);\n'
                                                                "echo $child(), '|', $copy(), "
                                                                "'|';\n"
                                                                'unset($child,$copy);\n',
                                                      'stage': 'S.TODO = (ARGINFO_INVOKE pargcall) '
                                                               ':: ptask_tail* -- if pargcall.KIND '
                                                               '= INTRINSIC_GET_CALLED_CLASS -- if '
                                                               'S.CURRENT = (pcallcontext) -- if '
                                                               'pcallcontext.TARGET = '
                                                               'CLOSURE_TARGET n_child -- if '
                                                               'S.OBJECTS[n_child] = '
                                                               'INTERNALSCOPECLOSURE '
                                                               'pinternalclosurescope pobject -- '
                                                               'if ~pinternalclosurescope.BOUND -- '
                                                               'if ~((HOBJECT '
                                                               'pinternalclosurescope.SOURCE) <- '
                                                               'S.ALLOCATIONS)',
                                                      'checks': ['pinternalclosurescope.SOURCE = '
                                                                 'n_parent',
                                                                 'S.OBJECTS[n_parent] = '
                                                                 'BOUNDFAKECLOSURE pboundfake',
                                                                 'pinternalclosurescope.LEXICAL = '
                                                                 'BIND_INTERNAL '
                                                                 '$ptascii("Closure")',
                                                                 'pinternalclosurescope.CALLED = '
                                                                 'pboundfake.CALLED',
                                                                 'pinternalclosurescope.RECEIVER = '
                                                                 'pboundfake.RECEIVER',
                                                                 'pinternalclosurescope.RECEIVER = '
                                                                 '(n_receiver)',
                                                                 'pboundfake.SOURCE = n_named',
                                                                 '~((HOBJECT n_named) <- '
                                                                 'S.ALLOCATIONS)',
                                                                 '$heap_owners($heap_graph(S), '
                                                                 'HOBJECT n_parent) = 0',
                                                                 '$closure_scope_at(S.CLOSURESCOPES, '
                                                                 'n_parent) = eps',
                                                                 '$closure_scope_at(S.CLOSURESCOPES, '
                                                                 'n_child) = eps',
                                                                 '$closure_binding_at(S.CLOSUREBINDINGS, '
                                                                 'n_child) = eps',
                                                                 '$closure_current_object(S) = '
                                                                 '(n_child)',
                                                                 '$internal_closure_scope_valid(S, '
                                                                 'n_child)',
                                                                 'pcallcontext.INSTANCE = '
                                                                 '(n_child)',
                                                                 'pcallcontext.LEXICAL_CLASS = eps',
                                                                 'pcallcontext.RECEIVER = '
                                                                 '(n_receiver)',
                                                                 '$object_body(S.OBJECTS[n_child]) '
                                                                 '= REALCLOSURE porigin_child '
                                                                 'pitem* pstaticcell*',
                                                                 '$node_children(S, HOBJECT '
                                                                 'n_child) = '
                                                                 '$closure_items_nodes(pitem*) ++ '
                                                                 '$static_roots(pstaticcell*) ++ '
                                                                 '[HOBJECT n_receiver]',
                                                                 'S.GLOBALTABLE = '
                                                                 '(psymboltable_global)',
                                                                 '$lookup(psymboltable_global.ENV, '
                                                                 '$ptascii("copy")) = '
                                                                 '(n_copy_cell)',
                                                                 'S.STORE[n_copy_cell] = DEFINED '
                                                                 '(POBJECT n_copy)',
                                                                 'S.OBJECTS[n_copy] = '
                                                                 'INTERNALSCOPECLOSURE '
                                                                 'pinternalclosurescope '
                                                                 '(REALCLOSURE porigin_child '
                                                                 'pitem_copy* pstaticcell_copy*)',
                                                                 'pstaticcell_copy* =/= '
                                                                 'pstaticcell*',
                                                                 '$($heap_owners($heap_graph(S), '
                                                                 'HOBJECT n_receiver) >= 2)',
                                                                 '$call_descriptors_valid(S)',
                                                                 '$closure_state_valid(S)',
                                                                 '$heap_valid($heap_graph(S))',
                                                                 '~$internal_closure_scope_valid(S[.OBJECTS[n_child] '
                                                                 '= INTERNALSCOPECLOSURE '
                                                                 'pinternalclosurescope[.BOUND = '
                                                                 'true] pobject], n_child)',
                                                                 '~$internal_closure_scope_valid(S[.OBJECTS[n_child] '
                                                                 '= INTERNALSCOPECLOSURE '
                                                                 'pinternalclosurescope[.SOURCE = '
                                                                 'n_child] pobject], n_child)',
                                                                 '~$internal_closure_scope_valid(S[.OBJECTS[n_child] '
                                                                 '= INTERNALSCOPECLOSURE '
                                                                 'pinternalclosurescope[.LEXICAL = '
                                                                 'BIND_UNSCOPED] pobject], '
                                                                 'n_child)',
                                                                 '~$internal_closure_scope_valid(S[.OBJECTS[n_child] '
                                                                 '= INTERNALSCOPECLOSURE '
                                                                 'pinternalclosurescope[.CALLED = '
                                                                 'BIND_INTERNAL '
                                                                 '$ptascii("Closure")] pobject], '
                                                                 'n_child)',
                                                                 '~$internal_closure_scope_valid(S[.OBJECTS[n_child] '
                                                                 '= INTERNALSCOPECLOSURE '
                                                                 'pinternalclosurescope[.RECEIVER '
                                                                 '= eps] pobject], n_child)',
                                                                 'S_budget = $drive(S, 0)',
                                                                 'S_budget.COMPLETION = BUDGET',
                                                                 '$call_descriptors_valid(S_budget)',
                                                                 '$closure_state_valid(S_budget)',
                                                                 '$heap_valid($heap_graph(S_budget))',
                                                                 'S_done = '
                                                                 '$drive(S_budget[.COMPLETION = '
                                                                 'NORMAL], 3000)',
                                                                 'S_done.COMPLETION = NORMAL',
                                                                 'S_done.CURRENT = eps /\\ '
                                                                 'S_done.FRAMES = eps',
                                                                 '$call_descriptors_valid(S_done)',
                                                                 '$closure_state_valid(S_done)',
                                                                 '$heap_valid($heap_graph(S_done))',
                                                                 '$current_binding_outputs(S_done.EVENTS) '
                                                                 '= '
                                                                 '$ptascii("Closure:DummyChildHost253:DummyChildHost253:2|Closure:DummyChildHost253:DummyChildHost253:2|")',
                                                                 '~((HOBJECT n_child) <- '
                                                                 'S_done.ALLOCATIONS)',
                                                                 '~((HOBJECT n_copy) <- '
                                                                 'S_done.ALLOCATIONS)',
                                                                 '~((HOBJECT n_receiver) <- '
                                                                 'S_done.ALLOCATIONS)']},
 'fake-warning-throw-finally-selected-owner-unwind': {'source': '<?php\n'
                                                                'class ThrowOwner253 { public '
                                                                'function method() {} }\n'
                                                                'class ThrowOther253 {}\n'
                                                                '$original = new ThrowOwner253();\n'
                                                                '$cap = $original->method(...);\n'
                                                                'unset($original);\n'
                                                                'set_error_handler(function '
                                                                '($errno, $message) use (&$cap) {\n'
                                                                '    try {\n'
                                                                "        echo 'W:', $message, "
                                                                "'|';\n"
                                                                '        $cap = 99;\n'
                                                                "        throw new Exception('bind "
                                                                "stop');\n"
                                                                '    } finally {\n'
                                                                "        echo 'F:', $cap, '|';\n"
                                                                '    }\n'
                                                                '});\n'
                                                                'try { $cap->bindTo(new '
                                                                'ThrowOther253()); } catch '
                                                                "(Exception $e) { echo 'E:', "
                                                                "$e->getMessage(), ':', $cap, '|'; "
                                                                '}\n'
                                                                'restore_error_handler();\n'
                                                                'unset($e);\n',
                                                      'stage': 'S.TODO = (THROW_SEARCH n_throw) :: '
                                                               'ptask_tail* -- if S.CURRENT = '
                                                               '(pcallcontext) -- if S.FRAMES = '
                                                               'pframe_global :: pframe_tail* -- '
                                                               'if pframe_global.TODO = '
                                                               '(ERROR_HANDLER_RESULT perrorcall) '
                                                               ':: ptask_saved* -- if '
                                                               'perrorcall.RESUME = '
                                                               'FAKE_BIND_WARNING pbindwarning -- '
                                                               'if '
                                                               '$current_binding_outputs(S.EVENTS) '
                                                               '= $ptascii("W:Cannot bind method '
                                                               'ThrowOwner253::method() to object '
                                                               'of class ThrowOther253, this will '
                                                               'be an error in PHP 9|F:99|")',
                                                      'checks': ['pbindwarning.CALL.KIND = '
                                                                 'INTRINSIC_CLOSURE_BINDTO',
                                                                 'pbindwarning.CALL.OWNER = '
                                                                 '(n_source)',
                                                                 '$object_body(S.OBJECTS[n_source]) '
                                                                 '= METHODCLOSURE porigin_method '
                                                                 'porigin_called porigin_capture '
                                                                 'pmethodcapture?',
                                                                 '(HOBJECT n_source) <- '
                                                                 'S.ALLOCATIONS',
                                                                 '$target_receiver(S, '
                                                                 'CLOSURE_TARGET n_source) = '
                                                                 '(n_old)',
                                                                 '(HOBJECT n_old) <- S.ALLOCATIONS',
                                                                 '$named_slot_at(pbindwarning.CALL.SENT, '
                                                                 '0) = NAMED_SENT (KNOWN (POBJECT '
                                                                 'n_other))',
                                                                 'HOBJECT n_source <- '
                                                                 '$task_nodes(FAKE_BIND_WARNING '
                                                                 'pbindwarning)',
                                                                 'HOBJECT n_other <- '
                                                                 '$task_nodes(FAKE_BIND_WARNING '
                                                                 'pbindwarning)',
                                                                 'S.ERRORHANDLER.CALLBACK = eps',
                                                                 'S.GLOBALTABLE = '
                                                                 '(psymboltable_global)',
                                                                 '$lookup(psymboltable_global.ENV, '
                                                                 '$ptascii("cap")) = (n_cap)',
                                                                 'S.STORE[n_cap] = DEFINED (PINT '
                                                                 '99)',
                                                                 'S_emitter = '
                                                                 '$constant_frame_scope(S, '
                                                                 'pframe_global, pframe_tail*)',
                                                                 '$error_call_valid(S_emitter, '
                                                                 'perrorcall)',
                                                                 '$call_task_valid(S_emitter, '
                                                                 'FAKE_BIND_WARNING pbindwarning)',
                                                                 '$error_context_valid(S, '
                                                                 'pcallcontext)',
                                                                 '$call_descriptors_valid(S)',
                                                                 '$closure_state_valid(S)',
                                                                 '$heap_valid($heap_graph(S))',
                                                                 '~$error_call_valid(S_emitter, '
                                                                 'perrorcall[.MESSAGE = '
                                                                 '$ptascii("wrong")])',
                                                                 '~$error_call_valid(S_emitter, '
                                                                 'perrorcall[.LINE = '
                                                                 '$(perrorcall.LINE + 1)])',
                                                                 '~$call_task_valid(S_emitter, '
                                                                 'FAKE_BIND_WARNING '
                                                                 'pbindwarning[.MESSAGE = '
                                                                 '$ptascii("wrong")])',
                                                                 '~$call_task_valid(S_emitter, '
                                                                 'FAKE_BIND_WARNING '
                                                                 'pbindwarning[.CALL.OWNER = '
                                                                 '(n_other)])',
                                                                 'S_budget = $drive(S, 0)',
                                                                 'S_budget.COMPLETION = BUDGET',
                                                                 '$call_descriptors_valid(S_budget)',
                                                                 '$closure_state_valid(S_budget)',
                                                                 '$heap_valid($heap_graph(S_budget))',
                                                                 'S_done = '
                                                                 '$drive(S_budget[.COMPLETION = '
                                                                 'NORMAL], 3000)',
                                                                 'S_done.COMPLETION = NORMAL',
                                                                 'S_done.CURRENT = eps /\\ '
                                                                 'S_done.FRAMES = eps',
                                                                 '$call_descriptors_valid(S_done)',
                                                                 '$closure_state_valid(S_done)',
                                                                 '$heap_valid($heap_graph(S_done))',
                                                                 'S_done.ERRORHANDLER.CALLBACK = '
                                                                 'eps',
                                                                 'S_done.ERRORHANDLERS = eps',
                                                                 '$current_binding_outputs(S_done.EVENTS) '
                                                                 '= $ptascii("W:Cannot bind method '
                                                                 'ThrowOwner253::method() to '
                                                                 'object of class ThrowOther253, '
                                                                 'this will be an error in PHP '
                                                                 '9|F:99|E:bind stop:99|")',
                                                                 '~((HOBJECT n_source) <- '
                                                                 'S_done.ALLOCATIONS)',
                                                                 '~((HOBJECT n_old) <- '
                                                                 'S_done.ALLOCATIONS)',
                                                                 '~((HOBJECT n_other) <- '
                                                                 'S_done.ALLOCATIONS)',
                                                                 '~((HOBJECT n_throw) <- '
                                                                 'S_done.ALLOCATIONS)']},
 'current-cloned-bound-real-identity-and-owners': {'source': '<?php class CurrentOwnerState253 {} '
                                                             '$other=function(){}; '
                                                             '$real=function() use ($other) { '
                                                             'return $other->getCurrent(); }; '
                                                             '$bound=$real->bindTo(new '
                                                             'CurrentOwnerState253()); $copy=clone '
                                                             '$bound; unset($other,$real,$bound); '
                                                             'echo $copy()===$copy ? "OK" : "BAD"; '
                                                             'unset($copy);',
                                                   'stage': 'S.TODO = (CONFIG_INVOKE pconfigcall) '
                                                            ':: ptask_tail* -- if pconfigcall.KIND '
                                                            '= INTRINSIC_CLOSURE_CURRENT -- if '
                                                            'S.CURRENT = (pcallcontext) -- if '
                                                            'pcallcontext.TARGET = CLOSURE_TARGET '
                                                            'n_current',
                                                   'checks': ['pconfigcall.OWNER = (n_other)',
                                                              'n_current =/= n_other',
                                                              'pcallcontext.INSTANCE = (n_current)',
                                                              '$closure_current_object(S) = '
                                                              '(n_current)',
                                                              '$config_invoke_valid(S, '
                                                              'pconfigcall)',
                                                              '$internal_closure_row(S, n_current) '
                                                              '= (pinternalclosurescope)',
                                                              'pinternalclosurescope.BOUND',
                                                              'pinternalclosurescope.SOURCE = '
                                                              'n_source',
                                                              'pinternalclosurescope.LEXICAL = '
                                                              'BIND_INTERNAL ($ptascii("Closure"))',
                                                              '$closure_binding_at(S.CLOSUREBINDINGS, '
                                                              'n_current) = eps',
                                                              '$closure_scope_at(S.CLOSURESCOPES, '
                                                              'n_current) = eps',
                                                              '~((HOBJECT n_source) <- '
                                                              'S.ALLOCATIONS)',
                                                              '$object_body(S.OBJECTS[n_current]) '
                                                              '= REALCLOSURE porigin pitem* '
                                                              'pstaticcell*',
                                                              '$object_body(S.OBJECTS[n_source]) = '
                                                              'REALCLOSURE porigin pitem_source* '
                                                              'pstaticcell_source*',
                                                              'pcallcontext.RECEIVER = '
                                                              '(n_receiver)',
                                                              'pinternalclosurescope.RECEIVER = '
                                                              '(n_receiver)',
                                                              'S.OBJECTS[n_receiver] = INSTANCE '
                                                              'porigin_host',
                                                              'pinternalclosurescope.CALLED = '
                                                              'BIND_CLASS porigin_host',
                                                              '$internal_closure_scope_valid(S, '
                                                              'n_current)',
                                                              '~(HOBJECT n_source <- '
                                                              '$node_children(S, HOBJECT '
                                                              'n_current))',
                                                              'HOBJECT n_receiver <- '
                                                              '$node_children(S, HOBJECT '
                                                              'n_current)',
                                                              '~$closure_callable(S[.OBJECTS[n_current] '
                                                              '= INTERNALSCOPECLOSURE '
                                                              'pinternalclosurescope[.LEXICAL = '
                                                              'BIND_INTERNAL '
                                                              '($ptascii("stdClass"))] '
                                                              '(REALCLOSURE porigin pitem* '
                                                              'pstaticcell*)], n_current)',
                                                              '~$closure_callable(S[.OBJECTS[n_current] '
                                                              '= INTERNALSCOPECLOSURE '
                                                              'pinternalclosurescope[.BOUND = '
                                                              'false] (REALCLOSURE porigin pitem* '
                                                              'pstaticcell*)], n_current)',
                                                              '~$closure_callable(S[.OBJECTS[n_current] '
                                                              '= INTERNALSCOPECLOSURE '
                                                              'pinternalclosurescope[.CALLSITE = '
                                                              '(pconfigcall.SITE)] (REALCLOSURE '
                                                              'porigin pitem* pstaticcell*)], '
                                                              'n_current)',
                                                              '~$closure_callable(S[.OBJECTS[n_current] '
                                                              '= INTERNALSCOPECLOSURE '
                                                              'pinternalclosurescope[.CALLED = '
                                                              'BIND_UNSCOPED] (REALCLOSURE porigin '
                                                              'pitem* pstaticcell*)], n_current)',
                                                              '~(HOBJECT n_other <- '
                                                              '$task_nodes(CONFIG_INVOKE '
                                                              'pconfigcall))',
                                                              'HOBJECT n_current <- '
                                                              '$target_nodes(pcallcontext.TARGET)',
                                                              '~(HOBJECT n_source <- '
                                                              '$target_nodes(pcallcontext.TARGET))',
                                                              '$call_descriptors_valid(S)',
                                                              '$closure_state_valid(S)',
                                                              '$heap_valid($heap_graph(S))',
                                                              '~$closure_callable(S[.OBJECTS[n_other] '
                                                              '= INTRINSICCLOSURE '
                                                              'INTRINSIC_CLOSURE_CURRENT], '
                                                              'n_other)',
                                                              '~$closure_live_object_valid(S[.OBJECTS[n_other] '
                                                              '= INTRINSICCLOSURE '
                                                              'INTRINSIC_CLOSURE_CURRENT], '
                                                              'n_other)',
                                                              '~$call_current_valid(S[.CURRENT = '
                                                              '(pcallcontext[.INSTANCE = '
                                                              '(n_other)])])',
                                                              '~$config_selected_valid(S, '
                                                              'pconfigcall[.OWNER = eps])',
                                                              '~$call_task_valid(S, CONFIG_INVOKE '
                                                              'pconfigcall[.LINE = '
                                                              '$(pconfigcall.LINE + 100)])',
                                                              'S_after = $drive_steps(S, '
                                                              '1)[.COMPLETION = NORMAL]',
                                                              'S_after.RESULT = KNOWN (POBJECT '
                                                              'n_current)',
                                                              'S_after.OBJECTS = S.OBJECTS',
                                                              'S_after.CLOSURESCOPES = '
                                                              'S.CLOSURESCOPES',
                                                              'S_after.CLOSUREBINDINGS = '
                                                              'S.CLOSUREBINDINGS',
                                                              'S_after.ALLOCATIONS = S.ALLOCATIONS',
                                                              '$heap_owners($heap_graph(S_after), '
                                                              'HOBJECT n_current) = '
                                                              '$($heap_owners($heap_graph(S), '
                                                              'HOBJECT n_current) + 1)',
                                                              '$call_descriptors_valid(S_after)',
                                                              '$closure_state_valid(S_after)',
                                                              '$heap_valid($heap_graph(S_after))',
                                                              'S_budget = $drive(S_after, 0)',
                                                              'S_budget.COMPLETION = BUDGET',
                                                              '$call_descriptors_valid(S_budget)',
                                                              '$closure_state_valid(S_budget)',
                                                              '$heap_valid($heap_graph(S_budget))',
                                                              'S_done = '
                                                              '$drive(S_budget[.COMPLETION = '
                                                              'NORMAL], 3000)',
                                                              'S_done.COMPLETION = NORMAL',
                                                              'S_done.CURRENT = eps /\\ '
                                                              'S_done.FRAMES = eps',
                                                              'S_done.EVENTS = [OUTPUT '
                                                              '($ptascii("OK"))]',
                                                              '~((HOBJECT n_current) <- '
                                                              'S_done.ALLOCATIONS)',
                                                              '~((HOBJECT n_other) <- '
                                                              'S_done.ALLOCATIONS)',
                                                              '~((HOBJECT n_receiver) <- '
                                                              'S_done.ALLOCATIONS)',
                                                              '$call_descriptors_valid(S_done)',
                                                              '$closure_state_valid(S_done)',
                                                              '$heap_valid($heap_graph(S_done))']},
 'bound-fake-dummy-internal-scope-retired-chain': {'source': '<?php\n'
                                                             'function dummyClosureReceiver253() '
                                                             '{\n'
                                                             '    static $n = 0;\n'
                                                             "    echo get_class($this), ':', "
                                                             "get_called_class(), ':', ++$n, '|';\n"
                                                             '    try { Closure::getCurrent(); } '
                                                             "catch (Error $e) { echo 'C:', "
                                                             "$e->getMessage(), '|'; }\n"
                                                             '}\n'
                                                             'class DummyFirstHost253 {}\n'
                                                             '$source = '
                                                             'dummyClosureReceiver253(...);\n'
                                                             '$bound = $source->bindTo(new '
                                                             'DummyFirstHost253());\n'
                                                             '$other = function () {};\n'
                                                             '$again = $bound->bindTo($other);\n'
                                                             '$copy = clone $again;\n'
                                                             'unset($source, $bound, $other);\n'
                                                             '$again();\n'
                                                             '$copy();\n'
                                                             'unset($again, $copy);\n',
                                                   'stage': 'S.TODO = (ARGINFO_INVOKE pargcall) :: '
                                                            'ptask_tail* -- if pargcall.KIND = '
                                                            'INTRINSIC_GET_CALLED_CLASS -- if '
                                                            'S.CURRENT = (pcallcontext) -- if '
                                                            'pcallcontext.TARGET = CLOSURE_TARGET '
                                                            'n_current -- if S.OBJECTS[n_current] '
                                                            '= BOUNDFAKECLOSURE pboundfake',
                                                   'checks': ['pboundfake.SCOPE = BIND_INTERNAL '
                                                              '$ptascii("Closure")',
                                                              'pboundfake.CALLED = BIND_INTERNAL '
                                                              '$ptascii("Closure")',
                                                              'pboundfake.RECEIVER = (n_receiver)',
                                                              'S.OBJECTS[n_receiver] = REALCLOSURE '
                                                              'porigin_receiver pitem_receiver* '
                                                              'pstaticcell_receiver*',
                                                              'pboundfake.SOURCE = n_first',
                                                              'S.OBJECTS[n_first] = '
                                                              'BOUNDFAKECLOSURE pboundfake_first',
                                                              '~((HOBJECT n_first) <- '
                                                              'S.ALLOCATIONS)',
                                                              'pboundfake_first.RECEIVER = '
                                                              '(n_old_host)',
                                                              'S.OBJECTS[n_old_host] = INSTANCE '
                                                              'porigin_old_host',
                                                              '~((HOBJECT n_old_host) <- '
                                                              'S.ALLOCATIONS)',
                                                              'pboundfake_first.SOURCE = n_named',
                                                              'S.OBJECTS[n_named] = NAMEDCLOSURE '
                                                              'porigin_function',
                                                              '~((HOBJECT n_named) <- '
                                                              'S.ALLOCATIONS)',
                                                              'pcallcontext.FUNCTION = '
                                                              'porigin_function',
                                                              'pcallcontext.INSTANCE = (n_current)',
                                                              'pcallcontext.RECEIVER = '
                                                              '(n_receiver)',
                                                              '$bound_fake_internal_scope(S) = '
                                                              '($ptascii("Closure"))',
                                                              '$bound_fake_internal_called(S) = '
                                                              '($ptascii("Closure"))',
                                                              '$closure_current_object(S) = eps',
                                                              '$closure_callable(S, n_current)',
                                                              '$closure_live_object_valid(S, '
                                                              'n_current)',
                                                              '$node_children(S, HOBJECT '
                                                              'n_current) = [HOBJECT n_receiver]',
                                                              '$target_nodes(CLOSURE_TARGET '
                                                              'n_current) = [HOBJECT n_current]',
                                                              'S.FRAMES = pframe_global :: '
                                                              'pframe_tail*',
                                                              'pframe_global.CONTEXT = eps /\\ '
                                                              'pframe_global.LOCALS = eps',
                                                              'S.GLOBALTABLE = '
                                                              '(psymboltable_global)',
                                                              '$lookup(psymboltable_global.ENV, '
                                                              '$ptascii("copy")) = (n_copy_cell)',
                                                              'S.STORE[n_copy_cell] = DEFINED '
                                                              '(POBJECT n_copy)',
                                                              'S.OBJECTS[n_copy] = '
                                                              'BOUNDFAKECLOSURE pboundfake',
                                                              'n_copy =/= n_current',
                                                              '$node_children(S, HOBJECT n_copy) = '
                                                              '[HOBJECT n_receiver]',
                                                              '$($heap_owners($heap_graph(S), '
                                                              'HOBJECT n_receiver) >= 2)',
                                                              '$call_descriptors_valid(S)',
                                                              '$closure_state_valid(S)',
                                                              '$heap_valid($heap_graph(S))',
                                                              'pclosurescope_forged = {OBJECT '
                                                              'n_named, LEXICAL porigin_old_host, '
                                                              'CALLED porigin_old_host, RECEIVER '
                                                              '(n_old_host), CREATION eps}',
                                                              '~$fake_bind_source_valid(S, '
                                                              'pboundfake_first[.ORIGINAL = '
                                                              '(pclosurescope_forged)])',
                                                              '~$closure_callable(S[.OBJECTS[n_current] '
                                                              '= BOUNDFAKECLOSURE '
                                                              'pboundfake[.SOURCE = n_receiver]], '
                                                              'n_current)',
                                                              '~$closure_callable(S[.OBJECTS[n_current] '
                                                              '= BOUNDFAKECLOSURE '
                                                              'pboundfake[.SCOPE = '
                                                              'BIND_UNSCOPED]], n_current)',
                                                              '~$closure_callable(S[.OBJECTS[n_current] '
                                                              '= BOUNDFAKECLOSURE '
                                                              'pboundfake[.CALLED = '
                                                              'BIND_UNSCOPED]], n_current)',
                                                              '~$closure_callable(S[.OBJECTS[n_current] '
                                                              '= BOUNDFAKECLOSURE '
                                                              'pboundfake[.RECEIVER = '
                                                              '(n_old_host)]], n_current)',
                                                              '~$call_current_valid(S[.CURRENT = '
                                                              '(pcallcontext[.INSTANCE = '
                                                              '(n_copy)])])',
                                                              '~$call_current_valid(S[.CURRENT = '
                                                              '(pcallcontext[.RECEIVER = eps])])',
                                                              'S_budget = $drive(S, 0)',
                                                              'S_budget.COMPLETION = BUDGET',
                                                              '$call_descriptors_valid(S_budget)',
                                                              '$closure_state_valid(S_budget)',
                                                              '$heap_valid($heap_graph(S_budget))',
                                                              'S_done = '
                                                              '$drive(S_budget[.COMPLETION = '
                                                              'NORMAL], 3000)',
                                                              'S_done.COMPLETION = NORMAL',
                                                              'S_done.CURRENT = eps /\\ '
                                                              'S_done.FRAMES = eps',
                                                              '$current_binding_outputs(S_done.EVENTS) '
                                                              '= '
                                                              '$ptascii("Closure:Closure:1|C:Current '
                                                              'function is not a '
                                                              'closure|Closure:Closure:2|C:Current '
                                                              'function is not a closure|")',
                                                              '~((HOBJECT n_current) <- '
                                                              'S_done.ALLOCATIONS)',
                                                              '~((HOBJECT n_copy) <- '
                                                              'S_done.ALLOCATIONS)',
                                                              '~((HOBJECT n_receiver) <- '
                                                              'S_done.ALLOCATIONS)',
                                                              '$call_descriptors_valid(S_done)',
                                                              '$closure_state_valid(S_done)',
                                                              '$heap_valid($heap_graph(S_done))']},
 'current-static-api-historical-receiver-retires-during-send-warning': {'source': '<?php\n'
                                                                                  '$payload = new '
                                                                                  'stdClass();\n'
                                                                                  '$other = '
                                                                                  'function () use '
                                                                                  '($payload) {};\n'
                                                                                  'unset($payload);\n'
                                                                                  'set_error_handler(function '
                                                                                  '($level, '
                                                                                  '$message) use '
                                                                                  '(&$other) {\n'
                                                                                  '    $other = '
                                                                                  'null;\n'
                                                                                  '    $current = '
                                                                                  'Closure::getCurrent();\n'
                                                                                  '    echo '
                                                                                  '$current '
                                                                                  'instanceof '
                                                                                  "Closure ? 'H|' "
                                                                                  ": 'BAD|';\n"
                                                                                  '    return '
                                                                                  'true;\n'
                                                                                  '});\n'
                                                                                  'try { '
                                                                                  '$other->getCurrent($missing); '
                                                                                  '} catch '
                                                                                  '(ArgumentCountError '
                                                                                  '$e) { echo '
                                                                                  "'A|'; }\n"
                                                                                  'restore_error_handler();\n'
                                                                                  'unset($e, '
                                                                                  '$other);\n',
                                                                        'stage': 'S.TODO = '
                                                                                 '(CONFIG_INVOKE '
                                                                                 'pconfigcall_here) '
                                                                                 ':: ptask_tail* '
                                                                                 '-- if '
                                                                                 'pconfigcall_here.KIND '
                                                                                 '= '
                                                                                 'INTRINSIC_CLOSURE_CURRENT '
                                                                                 '-- if '
                                                                                 'pconfigcall_here.OWNER '
                                                                                 '= eps -- if '
                                                                                 'S.CURRENT = '
                                                                                 '(pcallcontext_handler) '
                                                                                 '-- if '
                                                                                 'pcallcontext_handler.TARGET '
                                                                                 '= CLOSURE_TARGET '
                                                                                 'n_handler -- if '
                                                                                 'S.FRAMES = '
                                                                                 'pframe_parent :: '
                                                                                 'pframe_tail* -- '
                                                                                 'if '
                                                                                 'pframe_parent.TODO '
                                                                                 '= '
                                                                                 '(ERROR_HANDLER_RESULT '
                                                                                 'perrorcall) :: '
                                                                                 'ptask_parent* -- '
                                                                                 'if '
                                                                                 'perrorcall.RESUME '
                                                                                 '= '
                                                                                 'ERROR_READ_RESULT '
                                                                                 'perrorread -- if '
                                                                                 'perrorread.TASK '
                                                                                 '= CONFIG_SEND '
                                                                                 'pconfigcall_outer '
                                                                                 '-- if '
                                                                                 'pconfigcall_outer.KIND '
                                                                                 '= '
                                                                                 'INTRINSIC_CLOSURE_CURRENT',
                                                                        'checks': ['pconfigcall_outer.OWNER '
                                                                                   '= (n_old)',
                                                                                   '$object_body(S.OBJECTS[n_old]) '
                                                                                   '= REALCLOSURE '
                                                                                   'porigin_old '
                                                                                   '([DIRECT '
                                                                                   '(POBJECT '
                                                                                   'n_payload)]) '
                                                                                   'pstaticcell_old*',
                                                                                   '~((HOBJECT '
                                                                                   'n_old) <- '
                                                                                   'S.ALLOCATIONS)',
                                                                                   'S.OBJECTS[n_payload] '
                                                                                   '= STDINSTANCE',
                                                                                   '~((HOBJECT '
                                                                                   'n_payload) <- '
                                                                                   'S.ALLOCATIONS)',
                                                                                   '$heap_owners($heap_graph(S), '
                                                                                   'HOBJECT n_old) '
                                                                                   '= 0',
                                                                                   '$heap_owners($heap_graph(S), '
                                                                                   'HOBJECT '
                                                                                   'n_payload) = 0',
                                                                                   '~(HOBJECT '
                                                                                   'n_old <- '
                                                                                   '$task_nodes(CONFIG_SEND '
                                                                                   'pconfigcall_outer))',
                                                                                   '~(HOBJECT '
                                                                                   'n_old <- '
                                                                                   '$task_nodes(ERROR_READ_RESULT '
                                                                                   'perrorread))',
                                                                                   '~(HOBJECT '
                                                                                   'n_old <- '
                                                                                   '$task_nodes(ERROR_HANDLER_RESULT '
                                                                                   'perrorcall))',
                                                                                   '$lookup(S.ENV, '
                                                                                   '$ptascii("other")) '
                                                                                   '= '
                                                                                   '(n_other_cell)',
                                                                                   'S.STORE[n_other_cell] '
                                                                                   '= DEFINED '
                                                                                   'PNULL',
                                                                                   '(HCELL '
                                                                                   'n_other_cell) '
                                                                                   '<- '
                                                                                   'S.ALLOCATIONS',
                                                                                   'pcallcontext_handler.INSTANCE '
                                                                                   '= (n_handler)',
                                                                                   '$closure_current_object(S) '
                                                                                   '= (n_handler)',
                                                                                   '$config_invoke_valid(S, '
                                                                                   'pconfigcall_here)',
                                                                                   'S_parent = '
                                                                                   '$constant_frame_scope(S, '
                                                                                   'pframe_parent, '
                                                                                   'pframe_tail*)',
                                                                                   '$config_selected_valid(S_parent, '
                                                                                   'pconfigcall_outer)',
                                                                                   '$error_read_valid(S_parent, '
                                                                                   'perrorread)',
                                                                                   '$error_entered_call_valid(S_parent, '
                                                                                   'perrorcall)',
                                                                                   '$call_descriptors_valid(S)',
                                                                                   '$closure_state_valid(S)',
                                                                                   '$heap_valid($heap_graph(S))',
                                                                                   '~$call_task_valid(S_parent, '
                                                                                   'CONFIG_SEND '
                                                                                   'pconfigcall_outer[.LINE '
                                                                                   '= '
                                                                                   '$(pconfigcall_outer.LINE '
                                                                                   '+ 100)])',
                                                                                   'n_invalid = '
                                                                                   '|S.OBJECTS|',
                                                                                   '~$config_selected_valid(S_parent, '
                                                                                   'pconfigcall_outer[.OWNER '
                                                                                   '= '
                                                                                   '(n_invalid)])',
                                                                                   '~$config_selected_valid(S_parent, '
                                                                                   'pconfigcall_outer[.OWNER '
                                                                                   '= '
                                                                                   '(n_payload)])',
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
                                                                                   '$current_binding_outputs(S_done.EVENTS) '
                                                                                   '= '
                                                                                   '$ptascii("H|A|")',
                                                                                   '~((HOBJECT '
                                                                                   'n_handler) <- '
                                                                                   'S_done.ALLOCATIONS)',
                                                                                   '~((HCELL '
                                                                                   'n_other_cell) '
                                                                                   '<- '
                                                                                   'S_done.ALLOCATIONS)',
                                                                                   '$call_descriptors_valid(S_done)',
                                                                                   '$closure_state_valid(S_done)',
                                                                                   '$heap_valid($heap_graph(S_done))']},
 'computed-real-binding-child-retired-creator-current': {'source': '<?php\n'
                                                                   'class RealComputedHost253 {}\n'
                                                                   '$maker = function () {\n'
                                                                   '    return function () {\n'
                                                                   "        echo self::class, ':', "
                                                                   "static::class, ':', "
                                                                   "get_class($this), '|';\n"
                                                                   '        return '
                                                                   'Closure::getCurrent();\n'
                                                                   '    };\n'
                                                                   '};\n'
                                                                   "$method = 'BiNdTo';\n"
                                                                   '$bound = $maker->$method(new '
                                                                   'RealComputedHost253(), '
                                                                   'RealComputedHost253::class);\n'
                                                                   '$child = $bound();\n'
                                                                   'unset($maker, $bound, '
                                                                   '$method);\n'
                                                                   '$current = $child();\n'
                                                                   'echo $current === $child ? '
                                                                   "'OK' : 'BAD';\n"
                                                                   'unset($child, $current);\n',
                                                         'stage': 'S.TODO = (CONFIG_INVOKE '
                                                                  'pconfigcall) :: ptask_tail* -- '
                                                                  'if pconfigcall.KIND = '
                                                                  'INTRINSIC_CLOSURE_CURRENT -- if '
                                                                  'S.CURRENT = (pcallcontext) -- '
                                                                  'if pcallcontext.TARGET = '
                                                                  'CLOSURE_TARGET n_child -- if '
                                                                  '$closure_scope_at(S.CLOSURESCOPES, '
                                                                  'n_child) = (pclosurescope) -- '
                                                                  'if pclosurescope.CREATION = '
                                                                  '(pclosurecreation) -- if '
                                                                  'pclosurecreation.EVIDENCE = '
                                                                  '(pclosurecreator) -- if '
                                                                  'pclosurecreator.SCOPE = '
                                                                  'CLOSURE_BINDING pclosurebinding',
                                                         'checks': ['pconfigcall.OWNER = eps',
                                                                    '$closure_current_object(S) = '
                                                                    '(n_child)',
                                                                    'pcallcontext.INSTANCE = '
                                                                    '(n_child)',
                                                                    '$object_body(S.OBJECTS[n_child]) '
                                                                    '= REALCLOSURE porigin_child '
                                                                    'eps eps',
                                                                    'pclosurebinding.OBJECT = '
                                                                    'n_parent',
                                                                    '$(n_parent < n_child)',
                                                                    '~((HOBJECT n_parent) <- '
                                                                    'S.ALLOCATIONS)',
                                                                    '$closure_binding_at(S.CLOSUREBINDINGS, '
                                                                    'n_parent) = eps',
                                                                    'pclosurebinding.SOURCE = '
                                                                    'n_original',
                                                                    '~((HOBJECT n_original) <- '
                                                                    'S.ALLOCATIONS)',
                                                                    'pclosurecreation.FUNCTION = '
                                                                    'porigin_parent',
                                                                    '$object_body(S.OBJECTS[n_parent]) '
                                                                    '= REALCLOSURE porigin_parent '
                                                                    'eps eps',
                                                                    '$object_body(S.OBJECTS[n_original]) '
                                                                    '= REALCLOSURE porigin_parent '
                                                                    'eps eps',
                                                                    'pclosurescope.RECEIVER = '
                                                                    '(n_receiver)',
                                                                    'pclosurebinding.RECEIVER = '
                                                                    '(n_receiver)',
                                                                    'S.OBJECTS[n_receiver] = '
                                                                    'INSTANCE porigin_host',
                                                                    'pclosurescope.LEXICAL = '
                                                                    'porigin_host',
                                                                    'pclosurescope.CALLED = '
                                                                    'porigin_host',
                                                                    '$class_at(S.CLASSES, '
                                                                    'porigin_host) = (pclassdesc)',
                                                                    'pclassdesc.NAME = '
                                                                    '$ptascii("RealComputedHost253")',
                                                                    'pcallcontext.RECEIVER = '
                                                                    '(n_receiver)',
                                                                    '$closure_evidence_valid(S, '
                                                                    'CLOSURE_BINDING '
                                                                    'pclosurebinding)',
                                                                    '$closure_creator_valid(S, '
                                                                    'porigin_child, pclosurescope, '
                                                                    'pclosurecreation, '
                                                                    'pclosurecreator)',
                                                                    '$closure_scope_row_valid(S, '
                                                                    'pclosurescope)',
                                                                    '$node_children(S, HOBJECT '
                                                                    'n_child) = [HOBJECT '
                                                                    'n_receiver]',
                                                                    '~(HOBJECT n_parent <- '
                                                                    '$node_children(S, HOBJECT '
                                                                    'n_child))',
                                                                    '~(HOBJECT n_original <- '
                                                                    '$node_children(S, HOBJECT '
                                                                    'n_child))',
                                                                    '$call_descriptors_valid(S)',
                                                                    '$closure_state_valid(S)',
                                                                    '$heap_valid($heap_graph(S))',
                                                                    '~$closure_evidence_valid(S, '
                                                                    'CLOSURE_BINDING '
                                                                    'pclosurebinding[.SITE = '
                                                                    'pconfigcall.SITE])',
                                                                    '~$closure_evidence_valid(S, '
                                                                    'CLOSURE_BINDING '
                                                                    'pclosurebinding[.SOURCE = '
                                                                    'n_child])',
                                                                    '~$closure_creator_valid(S, '
                                                                    'porigin_child, '
                                                                    'pclosurescope[.RECEIVER = '
                                                                    'eps], pclosurecreation, '
                                                                    'pclosurecreator)',
                                                                    '~$call_current_valid(S[.CURRENT '
                                                                    '= (pcallcontext[.INSTANCE = '
                                                                    '(n_parent)])])',
                                                                    'S_after = $drive_steps(S, '
                                                                    '1)[.COMPLETION = NORMAL]',
                                                                    'S_after.RESULT = KNOWN '
                                                                    '(POBJECT n_child)',
                                                                    'S_after.OBJECTS = S.OBJECTS',
                                                                    'S_after.CLOSURESCOPES = '
                                                                    'S.CLOSURESCOPES',
                                                                    'S_after.CLOSUREBINDINGS = '
                                                                    'S.CLOSUREBINDINGS',
                                                                    'S_after.ALLOCATIONS = '
                                                                    'S.ALLOCATIONS',
                                                                    '$heap_owners($heap_graph(S_after), '
                                                                    'HOBJECT n_child) = '
                                                                    '$($heap_owners($heap_graph(S), '
                                                                    'HOBJECT n_child) + 1)',
                                                                    '$call_descriptors_valid(S_after)',
                                                                    '$closure_state_valid(S_after)',
                                                                    '$heap_valid($heap_graph(S_after))',
                                                                    'S_budget = $drive(S_after, 0)',
                                                                    'S_budget.COMPLETION = BUDGET',
                                                                    '$call_descriptors_valid(S_budget)',
                                                                    '$closure_state_valid(S_budget)',
                                                                    '$heap_valid($heap_graph(S_budget))',
                                                                    'S_done = '
                                                                    '$drive(S_budget[.COMPLETION = '
                                                                    'NORMAL], 3000)',
                                                                    'S_done.COMPLETION = NORMAL',
                                                                    'S_done.CURRENT = eps /\\ '
                                                                    'S_done.FRAMES = eps',
                                                                    '$current_binding_outputs(S_done.EVENTS) '
                                                                    '= '
                                                                    '$ptascii("RealComputedHost253:RealComputedHost253:RealComputedHost253|OK")',
                                                                    '~((HOBJECT n_child) <- '
                                                                    'S_done.ALLOCATIONS)',
                                                                    '~((HOBJECT n_receiver) <- '
                                                                    'S_done.ALLOCATIONS)',
                                                                    '$call_descriptors_valid(S_done)',
                                                                    '$closure_state_valid(S_done)',
                                                                    '$heap_valid($heap_graph(S_done))']}}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--match', default='')
    args = parser.parse_args()
    protocol.MODULES.append(Path(__file__).with_suffix('.watsup'))
    selected = {name: case for name, case in CASES.items() if args.match in name}
    assert selected, 'no current/binding state selected'
    protocol.run(selected, extra_inputs=(Path(__file__),))
