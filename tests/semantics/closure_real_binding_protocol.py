#!/usr/bin/env python3
"""REAL binding warnings, compiled flags and null-unbinding owners."""
from pathlib import Path
import argparse
import closure_call_protocol as protocol

CASES = {'real-uses-this-warning-live-owner': {'source': '<?php\n'
                                                 'class RealUsesHost264 {\n'
                                                 '    public function dead() {\n'
                                                 '        return function () { if (false) { echo $this; '
                                                 '} return 7; };\n'
                                                 '    }\n'
                                                 '    public function probe() {\n'
                                                 '        return function () { return isset($this); };\n'
                                                 '    }\n'
                                                 '}\n'
                                                 'set_error_handler(function ($n, $message) { echo '
                                                 "'W:', $message, '|'; return true; });\n"
                                                 '$host = new RealUsesHost264;\n'
                                                 '$dead = $host->dead();\n'
                                                 '$probe = $host->probe();\n'
                                                 '$a = $dead->bindTo(null);\n'
                                                 '$b = $probe->bindTo(null);\n'
                                                 "echo (int)($a === null), ':', (int)($b === null), "
                                                 "':', $dead(), ':', (int)$probe(), '|';\n"
                                                 'restore_error_handler();\n'
                                                 'unset($host, $dead, $probe, $a, $b);\n',
                                       'stage': 'S.CURRENT = (pcallcontext) -- if pcallcontext.TARGET = '
                                                'CLOSURE_TARGET n_handler -- if S.FRAMES = pframe :: '
                                                'pframe_tail* -- if pframe.TODO = (ERROR_HANDLER_RESULT '
                                                'perrorcall) :: ptask_saved* -- if perrorcall.RESUME = '
                                                'FAKE_BIND_WARNING pbindwarning -- if '
                                                'pbindwarning.CALL.OWNER = (n_source) -- if '
                                                'S.GLOBALTABLE = (psymboltable_global) -- if '
                                                '$lookup(psymboltable_global.ENV, $ptascii("dead")) = '
                                                '(n_cell_source) -- if S.STORE[n_cell_source] = DEFINED '
                                                '(POBJECT n_source)',
                                       'checks': ['pbindwarning.CALL.KIND = INTRINSIC_CLOSURE_BINDTO',
                                                  'pbindwarning.CALL.SENT = [NAMED_SENT (KNOWN PNULL)]',
                                                  '$object_body(S.OBJECTS[n_source]) = REALCLOSURE '
                                                  'porigin pitem* pstaticcell*',
                                                  '$function_at(S.CLOSURETEMPLATES, porigin) = '
                                                  '(pfunction)',
                                                  '$real_closure_uses_this(S, pfunction)',
                                                  '~$closure_static(S, pfunction)',
                                                  '$target_receiver(S, CLOSURE_TARGET n_source) = '
                                                  '(n_host)',
                                                  '$closure_scope_at(S.CLOSURESCOPES, n_source) = '
                                                  '(pclosurescope)',
                                                  'pbindwarning.SCOPE = BIND_SCOPE (BIND_CLASS '
                                                  'pclosurescope.LEXICAL)',
                                                  'pbindwarning.MESSAGE = $ptascii("Cannot unbind $this '
                                                  'of closure using $this, this will be an error in PHP '
                                                  '9")',
                                                  '(HOBJECT n_source) <- S.ALLOCATIONS',
                                                  '(HOBJECT n_host) <- S.ALLOCATIONS',
                                                  '(HOBJECT n_handler) <- S.ALLOCATIONS',
                                                  'HOBJECT n_source <- $task_nodes(FAKE_BIND_WARNING '
                                                  'pbindwarning)',
                                                  '~(HOBJECT n_host <- $task_nodes(FAKE_BIND_WARNING '
                                                  'pbindwarning))',
                                                  'HOBJECT n_host <- $node_children(S, HOBJECT '
                                                  'n_source)',
                                                  '~(HOBJECT n_source <- $node_children(S, HOBJECT '
                                                  'n_handler))',
                                                  '$lookup(psymboltable_global.ENV, $ptascii("probe")) '
                                                  '= (n_cell_probe)',
                                                  'S.STORE[n_cell_probe] = DEFINED (POBJECT n_probe)',
                                                  '$object_body(S.OBJECTS[n_probe]) = REALCLOSURE '
                                                  'porigin_probe pitem_probe* pstaticcell_probe*',
                                                  '$function_at(S.CLOSURETEMPLATES, porigin_probe) = '
                                                  '(pfunction_probe)',
                                                  '$real_closure_uses_this(S, pfunction_probe)',
                                                  '~$real_closure_uses_this(S, pfunction[.CODE = '
                                                  'pfunction.CODE[.EXPRESSIONS = eps]])',
                                                  'S_emitter = $constant_frame_scope(S, pframe, '
                                                  'pframe_tail*)',
                                                  '$fake_bind_warning_valid(S_emitter, pbindwarning)',
                                                  '$error_call_valid(S_emitter, perrorcall)',
                                                  '$call_task_valid(S_emitter, FAKE_BIND_WARNING '
                                                  'pbindwarning)',
                                                  '~$fake_bind_warning_valid(S_emitter, '
                                                  'pbindwarning[.MESSAGE = $ptascii("Cannot bind an '
                                                  'instance to a static closure, this will be an error '
                                                  'in PHP 9")])',
                                                  '~$fake_bind_warning_valid(S_emitter, '
                                                  'pbindwarning[.SCOPE = BIND_SCOPE BIND_UNSCOPED])',
                                                  '~$call_task_valid(S_emitter, FAKE_BIND_WARNING '
                                                  'pbindwarning[.CALL.LINE = $(pbindwarning.CALL.LINE + '
                                                  '1)])',
                                                  '~$call_task_valid(S_emitter, FAKE_BIND_WARNING '
                                                  'pbindwarning[.CALL.OWNER = (n_handler)])',
                                                  '$call_descriptors_valid(S)',
                                                  '$closure_state_valid(S)',
                                                  '$heap_valid($heap_graph(S))',
                                                  'S_budget = $drive(S, 0)',
                                                  'S_budget.COMPLETION = BUDGET',
                                                  '$call_descriptors_valid(S_budget)',
                                                  '$closure_state_valid(S_budget)',
                                                  '$heap_valid($heap_graph(S_budget))',
                                                  'S_done = $drive(S_budget[.COMPLETION = NORMAL], '
                                                  '3000)',
                                                  'S_done.COMPLETION = NORMAL',
                                                  'S_done.CURRENT = eps /\\ S_done.FRAMES = eps',
                                                  '$call_descriptors_valid(S_done)',
                                                  '$closure_state_valid(S_done)',
                                                  '$heap_valid($heap_graph(S_done))',
                                                  '$real_binding_outputs(S_done.EVENTS) = '
                                                  '$ptascii("W:Cannot unbind $this of closure using '
                                                  '$this, this will be an error in PHP 9|W:Cannot '
                                                  'unbind $this of closure using $this, this will be an '
                                                  'error in PHP 9|1:1:7:1|")',
                                                  '~((HOBJECT n_source) <- S_done.ALLOCATIONS)',
                                                  '~((HOBJECT n_probe) <- S_done.ALLOCATIONS)',
                                                  '~((HOBJECT n_host) <- S_done.ALLOCATIONS)',
                                                  '~((HOBJECT n_handler) <- S_done.ALLOCATIONS)']},
 'real-unbind-private-alias-statics-retired-source': {'source': '<?php\n'
                                                                'class RealAliasOwner264 {\n'
                                                                '    private static function '
                                                                "secret($value) { echo 'P:', $value, "
                                                                "'|'; }\n"
                                                                '    public function make(&$value) {\n'
                                                                '        return function () use '
                                                                '(&$value) {\n'
                                                                '            static $n = 0;\n'
                                                                '            self::secret($value);\n'
                                                                "            echo self::class, ':', "
                                                                "static::class, ':', ++$n, '|';\n"
                                                                '            return '
                                                                'Closure::getCurrent();\n'
                                                                '        };\n'
                                                                '    }\n'
                                                                '}\n'
                                                                'class RealAliasChild264 extends '
                                                                'RealAliasOwner264 {}\n'
                                                                '$value = 1;\n'
                                                                '$host = new RealAliasChild264;\n'
                                                                '$source = $host->make($value);\n'
                                                                'echo (int)($source() === $source), '
                                                                "'|';\n"
                                                                '$unbound = Closure::bind($source, '
                                                                'null);\n'
                                                                '$copy = clone $unbound;\n'
                                                                'unset($host, $source);\n'
                                                                '$value = 6;\n'
                                                                'echo (int)($unbound() === $unbound), '
                                                                "'|';\n"
                                                                "echo (int)($copy() === $copy), '|';\n"
                                                                'echo (int)($unbound() === $unbound), '
                                                                "'|';\n"
                                                                'unset($unbound, $copy, $value);\n',
                                                      'stage': 'S.TODO = (CONFIG_INVOKE pconfigcall) :: '
                                                               'ptask_tail* -- if pconfigcall.KIND = '
                                                               'INTRINSIC_CLOSURE_CURRENT -- if '
                                                               'S.CURRENT = (pcallcontext) -- if '
                                                               'pcallcontext.TARGET = CLOSURE_TARGET '
                                                               'n_bound -- if '
                                                               '$closure_binding_at(S.CLOSUREBINDINGS, '
                                                               'n_bound) = (pclosurebinding)',
                                                      'checks': ['S.GLOBALTABLE = (psymboltable_global)',
                                                                 'pclosurebinding.SOURCE = n_source',
                                                                 '$object_body(S.OBJECTS[n_bound]) = '
                                                                 'REALCLOSURE porigin pitem* '
                                                                 'pstaticcell_bound_all*',
                                                                 '$function_at(S.CLOSURETEMPLATES, '
                                                                 'porigin) = (pfunction)',
                                                                 '~$real_closure_uses_this(S, '
                                                                 'pfunction)',
                                                                 '~$closure_static(S, pfunction)',
                                                                 '~((HOBJECT n_source) <- '
                                                                 'S.ALLOCATIONS)',
                                                                 '$closure_scope_at(S.CLOSURESCOPES, '
                                                                 'n_source) = eps',
                                                                 '$closure_binding_at(S.CLOSUREBINDINGS, '
                                                                 'n_source) = eps',
                                                                 'S.OBJECTS[0] = INSTANCE porigin_child',
                                                                 'n_host = 0',
                                                                 '~((HOBJECT n_host) <- S.ALLOCATIONS)',
                                                                 'pclosurebinding.RECEIVER = eps',
                                                                 'pclosurebinding.LEXICAL = '
                                                                 '(porigin_owner)',
                                                                 'pclosurebinding.CALLED = '
                                                                 '(porigin_owner)',
                                                                 '$class_at(S.CLASSES, porigin_owner) = '
                                                                 '(pclassdesc)',
                                                                 'pclassdesc.NAME = '
                                                                 '$ptascii("RealAliasOwner264")',
                                                                 '$target_receiver(S, CLOSURE_TARGET '
                                                                 'n_bound) = eps',
                                                                 'pcallcontext.INSTANCE = (n_bound)',
                                                                 'pcallcontext.RECEIVER = eps',
                                                                 'pcallcontext.LEXICAL_CLASS = '
                                                                 '(porigin_owner)',
                                                                 'pcallcontext.CALLED_CLASS = '
                                                                 '(porigin_owner)',
                                                                 'pitem* = [ALIAS n_cell]',
                                                                 'S.STORE[n_cell] = DEFINED (PINT 6)',
                                                                 'pstaticcell_bound_all* = '
                                                                 '[pstaticcell_bound]',
                                                                 'S.STORE[pstaticcell_bound.CELL] = '
                                                                 'DEFINED (PINT 2)',
                                                                 '$lookup(psymboltable_global.ENV, '
                                                                 '$ptascii("copy")) = (n_cell_copy)',
                                                                 'S.STORE[n_cell_copy] = DEFINED '
                                                                 '(POBJECT n_copy)',
                                                                 '$object_body(S.OBJECTS[n_copy]) = '
                                                                 'REALCLOSURE porigin pitem_copy* '
                                                                 'pstaticcell_copy_all*',
                                                                 'pitem_copy* = [ALIAS n_cell]',
                                                                 'pstaticcell_copy_all* = '
                                                                 '[pstaticcell_copy]',
                                                                 'pstaticcell_copy.CELL =/= '
                                                                 'pstaticcell_bound.CELL',
                                                                 'S.STORE[pstaticcell_copy.CELL] = '
                                                                 'DEFINED (PINT 1)',
                                                                 'HCELL n_cell <- $node_children(S, '
                                                                 'HOBJECT n_bound)',
                                                                 'HCELL n_cell <- $node_children(S, '
                                                                 'HOBJECT n_copy)',
                                                                 '~(HOBJECT n_source <- '
                                                                 '$node_children(S, HOBJECT n_bound))',
                                                                 '~(HOBJECT n_host <- $node_children(S, '
                                                                 'HOBJECT n_bound))',
                                                                 '$closure_binding_source_valid(S, '
                                                                 'pclosurebinding)',
                                                                 '$closure_current_object(S) = '
                                                                 '(n_bound)',
                                                                 '~$closure_binding_source_valid(S, '
                                                                 'pclosurebinding[.SOURCE = n_bound])',
                                                                 '~$closure_binding_source_valid(S, '
                                                                 'pclosurebinding[.CALLED = '
                                                                 '(porigin_child)])',
                                                                 '~$closure_binding_source_valid(S, '
                                                                 'pclosurebinding[.RECEIVER = '
                                                                 '(n_host)])',
                                                                 '~$call_current_valid(S[.CURRENT = '
                                                                 '(pcallcontext[.CALLED_CLASS = '
                                                                 '(porigin_child)])])',
                                                                 '$call_descriptors_valid(S)',
                                                                 '$closure_state_valid(S)',
                                                                 '$heap_valid($heap_graph(S))',
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
                                                                 '$real_binding_outputs(S_done.EVENTS) '
                                                                 '= '
                                                                 '$ptascii("P:1|RealAliasOwner264:RealAliasChild264:1|1|P:6|RealAliasOwner264:RealAliasOwner264:2|1|P:6|RealAliasOwner264:RealAliasOwner264:2|1|P:6|RealAliasOwner264:RealAliasOwner264:3|1|")',
                                                                 '~((HOBJECT n_bound) <- '
                                                                 'S_done.ALLOCATIONS)',
                                                                 '~((HOBJECT n_copy) <- '
                                                                 'S_done.ALLOCATIONS)',
                                                                 '~((HCELL n_cell) <- '
                                                                 'S_done.ALLOCATIONS)',
                                                                 '~((HCELL pstaticcell_bound.CELL) <- '
                                                                 'S_done.ALLOCATIONS)',
                                                                 '~((HCELL pstaticcell_copy.CELL) <- '
                                                                 'S_done.ALLOCATIONS)']},
 'real-static-warning-keeps-selected-inputs-after-replacement': {'source': '<?php\n'
                                                                           'class RealSnapshotHost264 '
                                                                           '{}\n'
                                                                           '$source = static function '
                                                                           '() { return 1; };\n'
                                                                           '$receiver = new '
                                                                           'RealSnapshotHost264;\n'
                                                                           '$scope = '
                                                                           'RealSnapshotHost264::class;\n'
                                                                           '$class = Closure::class;\n'
                                                                           "$method = 'BiNd';\n"
                                                                           'set_error_handler(function '
                                                                           '($n, $message) use '
                                                                           '(&$source, &$receiver, '
                                                                           '&$scope) {\n'
                                                                           "    echo 'W:', $message, "
                                                                           "'|';\n"
                                                                           '    $source = function () { '
                                                                           'return 7; };\n'
                                                                           '    $receiver = null;\n'
                                                                           '    $scope = null;\n'
                                                                           '    $current = '
                                                                           'Closure::getCurrent();\n'
                                                                           '    echo (int)($current '
                                                                           "instanceof Closure), '|';\n"
                                                                           '    return true;\n'
                                                                           '});\n'
                                                                           '$result = '
                                                                           '$class::$method(newScope: '
                                                                           '$scope, newThis: $receiver, '
                                                                           'closure: $source);\n'
                                                                           'echo (int)($result === '
                                                                           "null), ':', $source(), ':', "
                                                                           '(int)($receiver === null), '
                                                                           "':', (int)($scope === "
                                                                           "null), '|';\n"
                                                                           'restore_error_handler();\n'
                                                                           'unset($source, $receiver, '
                                                                           '$scope, $class, $method, '
                                                                           '$result);\n',
                                                                 'stage': 'S.TODO = (CONFIG_INVOKE '
                                                                          'pconfigcall_here) :: '
                                                                          'ptask_tail* -- if '
                                                                          'pconfigcall_here.KIND = '
                                                                          'INTRINSIC_CLOSURE_CURRENT -- '
                                                                          'if S.CURRENT = '
                                                                          '(pcallcontext_handler) -- if '
                                                                          'pcallcontext_handler.TARGET '
                                                                          '= CLOSURE_TARGET n_handler '
                                                                          '-- if S.FRAMES = '
                                                                          'pframe_parent :: '
                                                                          'pframe_tail* -- if '
                                                                          'pframe_parent.TODO = '
                                                                          '(ERROR_HANDLER_RESULT '
                                                                          'perrorcall) :: ptask_parent* '
                                                                          '-- if perrorcall.RESUME = '
                                                                          'FAKE_BIND_WARNING '
                                                                          'pbindwarning -- if '
                                                                          'pbindwarning.CALL.KIND = '
                                                                          'INTRINSIC_CLOSURE_BIND',
                                                                 'checks': ['S_parent = '
                                                                            '$constant_frame_scope(S, '
                                                                            'pframe_parent, '
                                                                            'pframe_tail*)',
                                                                            '$fake_bind_source(pbindwarning.CALL) '
                                                                            '= (n_old)',
                                                                            '$fake_bind_this(pbindwarning.CALL) '
                                                                            '= (n_receiver)',
                                                                            'pbindwarning.SCOPE = '
                                                                            'BIND_SCOPE (BIND_CLASS '
                                                                            'porigin_host)',
                                                                            'pbindwarning.MESSAGE = '
                                                                            '$ptascii("Cannot bind an '
                                                                            'instance to a static '
                                                                            'closure, this will be an '
                                                                            'error in PHP 9")',
                                                                            '$object_body(S.OBJECTS[n_old]) '
                                                                            '= REALCLOSURE porigin_old '
                                                                            'eps eps',
                                                                            '$function_at(S.CLOSURETEMPLATES, '
                                                                            'porigin_old) = '
                                                                            '(pfunction_old)',
                                                                            '$closure_static(S, '
                                                                            'pfunction_old)',
                                                                            '~$real_closure_uses_this(S, '
                                                                            'pfunction_old)',
                                                                            'S.OBJECTS[n_receiver] = '
                                                                            'INSTANCE porigin_host',
                                                                            '(HOBJECT n_old) <- '
                                                                            'S.ALLOCATIONS',
                                                                            '(HOBJECT n_receiver) <- '
                                                                            'S.ALLOCATIONS',
                                                                            'HOBJECT n_old <- '
                                                                            '$task_nodes(FAKE_BIND_WARNING '
                                                                            'pbindwarning)',
                                                                            'HOBJECT n_receiver <- '
                                                                            '$task_nodes(FAKE_BIND_WARNING '
                                                                            'pbindwarning)',
                                                                            'HOBJECT n_old <- '
                                                                            '$task_nodes(ERROR_HANDLER_RESULT '
                                                                            'perrorcall)',
                                                                            'HOBJECT n_receiver <- '
                                                                            '$task_nodes(ERROR_HANDLER_RESULT '
                                                                            'perrorcall)',
                                                                            '$($heap_owners($heap_graph(S), '
                                                                            'HOBJECT n_old) >= 1)',
                                                                            '$($heap_owners($heap_graph(S), '
                                                                            'HOBJECT n_receiver) >= 1)',
                                                                            '$lookup(S.ENV, '
                                                                            '$ptascii("source")) = '
                                                                            '(n_source_cell)',
                                                                            'S.STORE[n_source_cell] = '
                                                                            'DEFINED (POBJECT n_new)',
                                                                            'n_new =/= n_old',
                                                                            '$lookup(S.ENV, '
                                                                            '$ptascii("receiver")) = '
                                                                            '(n_receiver_cell)',
                                                                            'S.STORE[n_receiver_cell] = '
                                                                            'DEFINED PNULL',
                                                                            '$lookup(S.ENV, '
                                                                            '$ptascii("scope")) = '
                                                                            '(n_scope_cell)',
                                                                            'S.STORE[n_scope_cell] = '
                                                                            'DEFINED PNULL',
                                                                            '$closure_current_object(S) '
                                                                            '= (n_handler)',
                                                                            'pcallcontext_handler.INSTANCE '
                                                                            '= (n_handler)',
                                                                            'pcallcontext_handler.RECEIVER '
                                                                            '= eps',
                                                                            '$config_invoke_valid(S, '
                                                                            'pconfigcall_here)',
                                                                            '$call_task_valid(S_parent, '
                                                                            'FAKE_BIND_WARNING '
                                                                            'pbindwarning)',
                                                                            '$fake_bind_warning_valid(S_parent, '
                                                                            'pbindwarning)',
                                                                            '$error_entered_call_valid(S_parent, '
                                                                            'perrorcall)',
                                                                            '$call_descriptors_valid(S)',
                                                                            '$closure_state_valid(S)',
                                                                            '$heap_valid($heap_graph(S))',
                                                                            '~$fake_bind_warning_valid(S_parent, '
                                                                            'pbindwarning[.MESSAGE = '
                                                                            '$ptascii("Cannot unbind '
                                                                            '$this of closure using '
                                                                            '$this, this will be an '
                                                                            'error in PHP 9")])',
                                                                            '~$fake_bind_warning_valid(S_parent, '
                                                                            'pbindwarning[.SCOPE = '
                                                                            'BIND_SCOPE BIND_UNSCOPED])',
                                                                            '~$call_task_valid(S_parent, '
                                                                            'FAKE_BIND_WARNING '
                                                                            'pbindwarning[.CALL = '
                                                                            'pbindwarning.CALL[.SITE = '
                                                                            'pconfigcall_here.SITE]])',
                                                                            '~$fake_bind_warning_valid(S_parent[.OBJECTS[n_old] '
                                                                            '= '
                                                                            '$object_body(S.OBJECTS[n_new])], '
                                                                            'pbindwarning)',
                                                                            '~$call_current_valid(S[.CURRENT '
                                                                            '= '
                                                                            '(pcallcontext_handler[.RECEIVER '
                                                                            '= (n_receiver)])])',
                                                                            '$closure_scope_at(S_parent.CLOSURESCOPES, '
                                                                            'n_new) = eps',
                                                                            'pclosurebinding_bad = '
                                                                            '{OBJECT n_new, SITE '
                                                                            'pbindwarning.CALL.SITE, '
                                                                            'SOURCE n_old, LEXICAL '
                                                                            '(porigin_host), CALLED '
                                                                            '(porigin_host), RECEIVER '
                                                                            '(n_receiver)}',
                                                                            'S_bad = '
                                                                            'S_parent[.OBJECTS[n_new] = '
                                                                            'REALCLOSURE porigin_old '
                                                                            'eps eps][.CLOSUREBINDINGS '
                                                                            '= S_parent.CLOSUREBINDINGS '
                                                                            '++ [pclosurebinding_bad]]',
                                                                            '$binding_scope_valid(S_bad, '
                                                                            'pclosurebinding_bad)',
                                                                            '~$closure_binding_source_valid(S_bad, '
                                                                            'pclosurebinding_bad)',
                                                                            'S_after = $drive_steps(S, '
                                                                            '1)[.COMPLETION = NORMAL]',
                                                                            'S_after.RESULT = KNOWN '
                                                                            '(POBJECT n_handler)',
                                                                            'S_after.OBJECTS = '
                                                                            'S.OBJECTS',
                                                                            'S_after.ALLOCATIONS = '
                                                                            'S.ALLOCATIONS',
                                                                            '$heap_owners($heap_graph(S_after), '
                                                                            'HOBJECT n_handler) = '
                                                                            '$($heap_owners($heap_graph(S), '
                                                                            'HOBJECT n_handler) + 1)',
                                                                            '$call_descriptors_valid(S_after)',
                                                                            '$closure_state_valid(S_after)',
                                                                            '$heap_valid($heap_graph(S_after))',
                                                                            'S_budget = $drive(S, 0)',
                                                                            'S_budget.COMPLETION = '
                                                                            'BUDGET',
                                                                            '$call_descriptors_valid(S_budget)',
                                                                            '$closure_state_valid(S_budget)',
                                                                            '$heap_valid($heap_graph(S_budget))',
                                                                            'S_done = '
                                                                            '$drive(S_budget[.COMPLETION '
                                                                            '= NORMAL], 3000)',
                                                                            'S_done.COMPLETION = NORMAL',
                                                                            'S_done.CURRENT = eps /\\ '
                                                                            'S_done.FRAMES = eps',
                                                                            '$real_binding_outputs(S_done.EVENTS) '
                                                                            '= $ptascii("W:Cannot bind '
                                                                            'an instance to a static '
                                                                            'closure, this will be an '
                                                                            'error in PHP '
                                                                            '9|1|1:7:1:1|")',
                                                                            'S_done.OBJECTS = S.OBJECTS',
                                                                            '~((HOBJECT n_old) <- '
                                                                            'S_done.ALLOCATIONS)',
                                                                            '~((HOBJECT n_receiver) <- '
                                                                            'S_done.ALLOCATIONS)',
                                                                            '~((HOBJECT n_new) <- '
                                                                            'S_done.ALLOCATIONS)',
                                                                            '~((HOBJECT n_handler) <- '
                                                                            'S_done.ALLOCATIONS)',
                                                                            '$call_descriptors_valid(S_done)',
                                                                            '$closure_state_valid(S_done)',
                                                                            '$heap_valid($heap_graph(S_done))']},
 'real-internal-unbind-retires-parent-and-copies-statics': {'source': '<?php\n'
                                                                      'class InternalRealUnbindHost264 '
                                                                      '{}\n'
                                                                      'set_error_handler(function ($n, '
                                                                      "$message) { echo 'W:', $message, "
                                                                      "'|'; return true; });\n"
                                                                      '$source = function () {\n'
                                                                      '    static $n = 0;\n'
                                                                      "    echo self::class, ':', "
                                                                      "static::class, ':', ++$n, '|';\n"
                                                                      '    return '
                                                                      'Closure::getCurrent();\n'
                                                                      '};\n'
                                                                      '$host = new '
                                                                      'InternalRealUnbindHost264;\n'
                                                                      '$bound = '
                                                                      '$source->bindTo($host);\n'
                                                                      'echo (int)($bound() === $bound), '
                                                                      "'|';\n"
                                                                      '$unbound = '
                                                                      '$bound->bindTo(null);\n'
                                                                      '$same = $bound->bindTo(null, '
                                                                      'Closure::class);\n'
                                                                      '$bad = $unbound->bindTo(null, '
                                                                      'Exception::class);\n'
                                                                      'unset($source, $bound, $host);\n'
                                                                      'echo (int)($unbound() === '
                                                                      "$unbound), '|';\n"
                                                                      'echo (int)($same() === $same), '
                                                                      "'|';\n"
                                                                      "echo (int)($bad === null), '|';\n"
                                                                      'restore_error_handler();\n'
                                                                      'unset($unbound, $same, $bad);\n',
                                                            'stage': 'S.TODO = (CONFIG_INVOKE '
                                                                     'pconfigcall) :: ptask_tail* -- if '
                                                                     'pconfigcall.KIND = '
                                                                     'INTRINSIC_CLOSURE_CURRENT -- if '
                                                                     'S.CURRENT = (pcallcontext) -- if '
                                                                     'pcallcontext.TARGET = '
                                                                     'CLOSURE_TARGET n_current -- if '
                                                                     '$internal_closure_row(S, '
                                                                     'n_current) = '
                                                                     '(pinternalclosurescope) -- if '
                                                                     'pinternalclosurescope.BOUND -- if '
                                                                     'pinternalclosurescope.RECEIVER = '
                                                                     'eps -- if ~((HOBJECT '
                                                                     'pinternalclosurescope.SOURCE) <- '
                                                                     'S.ALLOCATIONS)',
                                                            'checks': ['pcallcontext.INSTANCE = '
                                                                       '(n_current)',
                                                                       'pcallcontext.RECEIVER = eps',
                                                                       'pcallcontext.LEXICAL_CLASS = '
                                                                       'eps',
                                                                       'pcallcontext.CALLED_CLASS = eps',
                                                                       'pinternalclosurescope.LEXICAL = '
                                                                       'BIND_INTERNAL '
                                                                       '($ptascii("Closure"))',
                                                                       'pinternalclosurescope.CALLED = '
                                                                       'BIND_INTERNAL '
                                                                       '($ptascii("Closure"))',
                                                                       'pinternalclosurescope.SOURCE = '
                                                                       'n_parent',
                                                                       'S.OBJECTS[n_parent] = '
                                                                       'INTERNALSCOPECLOSURE '
                                                                       'pinternalclosurescope_parent '
                                                                       '(REALCLOSURE porigin eps '
                                                                       '([pstaticcell_parent]))',
                                                                       'pinternalclosurescope_parent.RECEIVER '
                                                                       '= (n_old_receiver)',
                                                                       'S.OBJECTS[n_old_receiver] = '
                                                                       'INSTANCE porigin_host',
                                                                       '~((HOBJECT n_old_receiver) <- '
                                                                       'S.ALLOCATIONS)',
                                                                       'pinternalclosurescope_parent.SOURCE '
                                                                       '= n_original',
                                                                       '~((HOBJECT n_original) <- '
                                                                       'S.ALLOCATIONS)',
                                                                       '$object_body(S.OBJECTS[n_current]) '
                                                                       '= REALCLOSURE porigin eps '
                                                                       '([pstaticcell_current])',
                                                                       '$function_at(S.CLOSURETEMPLATES, '
                                                                       'porigin) = (pfunction)',
                                                                       '~$real_closure_uses_this(S, '
                                                                       'pfunction)',
                                                                       '$lookup(S.ENV, $ptascii("n")) = '
                                                                       '(pstaticcell_current.CELL)',
                                                                       'S.STORE[pstaticcell_current.CELL] '
                                                                       '= DEFINED (PINT 2)',
                                                                       '(HCELL '
                                                                       'pstaticcell_current.CELL) <- '
                                                                       'S.ALLOCATIONS',
                                                                       '~((HCELL '
                                                                       'pstaticcell_parent.CELL) <- '
                                                                       'S.ALLOCATIONS)',
                                                                       'pstaticcell_parent.CELL =/= '
                                                                       'pstaticcell_current.CELL',
                                                                       'S.GLOBALTABLE = '
                                                                       '(psymboltable_global)',
                                                                       '$lookup(psymboltable_global.ENV, '
                                                                       '$ptascii("same")) = '
                                                                       '(n_same_cell)',
                                                                       'S.STORE[n_same_cell] = DEFINED '
                                                                       '(POBJECT n_same)',
                                                                       '$object_body(S.OBJECTS[n_same]) '
                                                                       '= REALCLOSURE porigin eps '
                                                                       '([pstaticcell_same])',
                                                                       'pstaticcell_same.CELL =/= '
                                                                       'pstaticcell_current.CELL',
                                                                       'S.STORE[pstaticcell_same.CELL] '
                                                                       '= DEFINED (PINT 1)',
                                                                       '$node_children(S, HOBJECT '
                                                                       'n_current) = [HCELL '
                                                                       'pstaticcell_current.CELL]',
                                                                       '~(HOBJECT n_parent <- '
                                                                       '$node_children(S, HOBJECT '
                                                                       'n_current))',
                                                                       '~(HOBJECT n_old_receiver <- '
                                                                       '$node_children(S, HOBJECT '
                                                                       'n_current))',
                                                                       '$target_nodes(pcallcontext.TARGET) '
                                                                       '= [HOBJECT n_current]',
                                                                       '$internal_closure_scope_valid(S, '
                                                                       'n_current)',
                                                                       '$closure_current_object(S) = '
                                                                       '(n_current)',
                                                                       '$call_descriptors_valid(S)',
                                                                       '$closure_state_valid(S)',
                                                                       '$heap_valid($heap_graph(S))',
                                                                       '~$closure_callable(S[.OBJECTS[n_current] '
                                                                       '= INTERNALSCOPECLOSURE '
                                                                       'pinternalclosurescope[.CALLED = '
                                                                       'BIND_UNSCOPED] (REALCLOSURE '
                                                                       'porigin eps '
                                                                       '([pstaticcell_current]))], '
                                                                       'n_current)',
                                                                       '~$closure_callable(S[.OBJECTS[n_current] '
                                                                       '= INTERNALSCOPECLOSURE '
                                                                       'pinternalclosurescope[.RECEIVER '
                                                                       '= (n_old_receiver)] '
                                                                       '(REALCLOSURE porigin eps '
                                                                       '([pstaticcell_current]))], '
                                                                       'n_current)',
                                                                       '~$closure_callable(S[.OBJECTS[n_current] '
                                                                       '= INTERNALSCOPECLOSURE '
                                                                       'pinternalclosurescope[.CALLSITE '
                                                                       '= (pconfigcall.SITE)] '
                                                                       '(REALCLOSURE porigin eps '
                                                                       '([pstaticcell_current]))], '
                                                                       'n_current)',
                                                                       '~$closure_callable(S[.OBJECTS[n_current] '
                                                                       '= INTERNALSCOPECLOSURE '
                                                                       'pinternalclosurescope[.SOURCE = '
                                                                       'n_current] (REALCLOSURE porigin '
                                                                       'eps ([pstaticcell_current]))], '
                                                                       'n_current)',
                                                                       '~$call_current_valid(S[.CURRENT '
                                                                       '= (pcallcontext[.RECEIVER = '
                                                                       '(n_old_receiver)])])',
                                                                       'S_after = $drive_steps(S, '
                                                                       '1)[.COMPLETION = NORMAL]',
                                                                       'S_after.RESULT = KNOWN (POBJECT '
                                                                       'n_current)',
                                                                       'S_after.OBJECTS = S.OBJECTS',
                                                                       'S_after.ALLOCATIONS = '
                                                                       'S.ALLOCATIONS',
                                                                       '$heap_owners($heap_graph(S_after), '
                                                                       'HOBJECT n_current) = '
                                                                       '$($heap_owners($heap_graph(S), '
                                                                       'HOBJECT n_current) + 1)',
                                                                       '$call_descriptors_valid(S_after)',
                                                                       '$closure_state_valid(S_after)',
                                                                       '$heap_valid($heap_graph(S_after))',
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
                                                                       '$real_binding_outputs(S_done.EVENTS) '
                                                                       '= '
                                                                       '$ptascii("Closure:InternalRealUnbindHost264:1|1|W:Cannot '
                                                                       'bind closure to scope of '
                                                                       'internal class Exception, this '
                                                                       'will be an error in PHP '
                                                                       '9|Closure:Closure:2|1|Closure:Closure:2|1|1|")',
                                                                       '~((HOBJECT n_current) <- '
                                                                       'S_done.ALLOCATIONS)',
                                                                       '~((HOBJECT n_same) <- '
                                                                       'S_done.ALLOCATIONS)',
                                                                       '~((HCELL '
                                                                       'pstaticcell_current.CELL) <- '
                                                                       'S_done.ALLOCATIONS)',
                                                                       '~((HCELL pstaticcell_same.CELL) '
                                                                       '<- S_done.ALLOCATIONS)',
                                                                       '$call_descriptors_valid(S_done)',
                                                                       '$closure_state_valid(S_done)',
                                                                       '$heap_valid($heap_graph(S_done))']},
 'real-uses-this-no-old-receiver-valid-unbound-frame': {'source': '<?php\n'
                                                                  'class RealRetiredUsesHost264 {}\n'
                                                                  'set_error_handler(function ($n, '
                                                                  "$message) { echo 'W:', $message, "
                                                                  "'|'; return true; });\n"
                                                                  '$source = function () { return '
                                                                  'isset($this); };\n'
                                                                  '$empty = $source->bindTo(null, '
                                                                  'null);\n'
                                                                  'unset($source);\n'
                                                                  "echo (int)$empty(), '|';\n"
                                                                  '$host = new RealRetiredUsesHost264;\n'
                                                                  '$bound = $empty->bindTo($host, '
                                                                  'null);\n'
                                                                  "echo (int)$bound(), '|';\n"
                                                                  '$failed = $bound->bindTo(null);\n'
                                                                  "echo (int)($failed === null), '|';\n"
                                                                  'restore_error_handler();\n'
                                                                  'unset($empty, $host, $bound, '
                                                                  '$failed);\n',
                                                        'stage': 'S.TODO = (EVAL (NExprIsset phpType25 '
                                                                 'metadata)) :: ptask_tail* -- if '
                                                                 'S.CURRENT = (pcallcontext) -- if '
                                                                 'pcallcontext.TARGET = CLOSURE_TARGET '
                                                                 'n_current -- if '
                                                                 '$closure_binding_at(S.CLOSUREBINDINGS, '
                                                                 'n_current) = (pclosurebinding) -- if '
                                                                 'pclosurebinding.RECEIVER = eps -- if '
                                                                 '~((HOBJECT pclosurebinding.SOURCE) <- '
                                                                 'S.ALLOCATIONS)',
                                                        'checks': ['pcallcontext.INSTANCE = (n_current)',
                                                                   'pcallcontext.RECEIVER = eps',
                                                                   'pcallcontext.LEXICAL_CLASS = eps',
                                                                   'pcallcontext.CALLED_CLASS = eps',
                                                                   'pclosurebinding.LEXICAL = eps',
                                                                   'pclosurebinding.CALLED = eps',
                                                                   'pclosurebinding.SOURCE = n_original',
                                                                   '$object_body(S.OBJECTS[n_current]) '
                                                                   '= REALCLOSURE porigin eps eps',
                                                                   '$object_body(S.OBJECTS[n_original]) '
                                                                   '= REALCLOSURE porigin eps eps',
                                                                   '$function_at(S.CLOSURETEMPLATES, '
                                                                   'porigin) = (pfunction)',
                                                                   '$real_closure_uses_this(S, '
                                                                   'pfunction)',
                                                                   '~$real_bind_receiver_warning(S, '
                                                                   'n_current, eps)',
                                                                   '$real_bind_warning_message(S, '
                                                                   'n_current, eps, BIND_UNSCOPED) = '
                                                                   'eps',
                                                                   '$closure_binding_source_valid(S, '
                                                                   'pclosurebinding)',
                                                                   '$closure_callable(S, n_current)',
                                                                   '$closure_scope_at(S.CLOSURESCOPES, '
                                                                   'n_current) = eps',
                                                                   '~$internal_closure_object(S, '
                                                                   'n_current)',
                                                                   '$node_children(S, HOBJECT '
                                                                   'n_current) = eps',
                                                                   '$target_nodes(pcallcontext.TARGET) '
                                                                   '= [HOBJECT n_current]',
                                                                   '~(HOBJECT n_original <- '
                                                                   '$node_children(S, HOBJECT '
                                                                   'n_current))',
                                                                   '$heap_owners($heap_graph(S), '
                                                                   'HOBJECT n_original) = 0',
                                                                   '$call_descriptors_valid(S)',
                                                                   '$closure_state_valid(S)',
                                                                   '$heap_valid($heap_graph(S))',
                                                                   '~$call_current_valid(S[.CURRENT = '
                                                                   '(pcallcontext[.INSTANCE = '
                                                                   '(n_original)])])',
                                                                   '~$closure_binding_source_valid(S, '
                                                                   'pclosurebinding[.SOURCE = '
                                                                   'n_current])',
                                                                   '~$closure_binding_source_valid(S, '
                                                                   'pclosurebinding[.SITE = porigin])',
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
                                                                   '$real_binding_outputs(S_done.EVENTS) '
                                                                   '= $ptascii("0|1|W:Cannot unbind '
                                                                   '$this of closure using $this, this '
                                                                   'will be an error in PHP 9|1|")',
                                                                   '~((HOBJECT n_current) <- '
                                                                   'S_done.ALLOCATIONS)',
                                                                   '~((HOBJECT n_original) <- '
                                                                   'S_done.ALLOCATIONS)',
                                                                   '$call_descriptors_valid(S_done)',
                                                                   '$closure_state_valid(S_done)',
                                                                   '$heap_valid($heap_graph(S_done))']}}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--match", default="")
    args = parser.parse_args()
    protocol.MODULES.append(Path(__file__).with_suffix(".watsup"))
    selected = {n: c for n, c in CASES.items() if args.match in n}
    assert selected
    protocol.run(selected, extra_inputs=(Path(__file__),))
