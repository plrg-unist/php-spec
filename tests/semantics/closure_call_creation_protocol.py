#!/usr/bin/env python3
"""Check temporary Closure scope, nested receiver ownership and retirement."""
import argparse,tempfile
from pathlib import Path
import deferred_static_default_protocol as protocol

protocol.SOURCES = {'global-escaping-child': '''<?php
class A { private int $v=7; private static int $p=5; }
$maker=function(){
    return function(){
        echo get_called_class(),':',$this->v,':',self::$p;
    };
};
$receiver=new A;
$child=$maker->call($receiver);
unset($maker,$receiver);
$child();
unset($child);
''', 'callback-resume-throw': '''<?php
class B { private static int $p=7; }
$child=null;
$maker=function(){
    global $child;
    echo $missing;
    $child=static function(){
        echo self::$p,':',get_called_class(),':';
        $r=&self::$p;
        $r=9;
        echo $r;
    };
    throw new Exception('x');
};
$receiver=new B;
set_error_handler(function(){
    echo 'H:';
    unset($GLOBALS['maker'],$GLOBALS['receiver']);
    return true;
});
try { $maker->call($receiver); } catch(Exception $e) { echo 'E:'; }
restore_error_handler();
$child();
unset($child);
'''}
protocol.PREFIX = '''
dec $closure_call_test_resume(pstate) : pstate
def $closure_call_test_resume(S) = S[.COMPLETION = NORMAL] -- if S.COMPLETION = BUDGET
def $closure_call_test_resume(S) = S -- otherwise
dec $closure_call_test_output(pevent*) : ptbytes
def $closure_call_test_output(eps) = eps
def $closure_call_test_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $closure_call_test_output(pevent*)
dec $closure_call_test_stage(pstate, bool) : bool
def $closure_call_test_stage(S, b_static) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $context_target(pcallcontext) = CLOSURE_CALL_TARGET n_source n_receiver
  -- if S.TODO = (CLOSURE_CAPTURE n_child 0) :: ptask_tail*
  -- if $object_body(S.OBJECTS[n_child]) = REALCLOSURE porigin_child pitem* pstaticcell*
  -- if $function_at(S.CLOSURETEMPLATES, porigin_child) = (pfunction)
  -- if $closure_static(S, pfunction) = b_static
def $closure_call_test_stage(S, b_static) = false -- otherwise
dec $closure_call_test_seek(pstate, bool, nat) : pstate
def $closure_call_test_seek(S, b_static, n_limit) = S -- if $closure_call_test_stage(S, b_static)
def $closure_call_test_seek(S, b_static, n_limit) = $closure_call_test_seek($closure_call_test_resume(S_next), b_static, n_rest)
  -- if ~$closure_call_test_stage(S, b_static)
  -- if $(n_limit > 0)
  -- if S.COMPLETION = NORMAL
  -- if ~S.COMPILESTOP
  -- if n_rest = $(n_limit - 1)
  -- if S_next = $drive_steps(S, 1)
'''
COMMON = [
 'S.CURRENT = (pcallcontext)',
 '$context_target(pcallcontext) = CLOSURE_CALL_TARGET n_source n_receiver',
 '$call_current_valid(S)',
 'pcallcontext.CALLSITE = (porigin_site)',
 'S.TODO = (CLOSURE_CAPTURE n_child 0) :: ptask_tail*',
 '$object_body(S.OBJECTS[n_child]) = REALCLOSURE porigin_child pitem* pstaticcell*',
 '$closure_scope_at(S.CLOSURESCOPES, n_child) = (pclosurescope)',
 'pclosurescope.CREATION = (pclosurecreation)',
 'pclosurecreation.EVIDENCE = (pclosurecreator)',
 'pclosurecreator.SCOPE = CLOSURE_CALL porigin_site n_source n_receiver porigin_class',
 'S.OBJECTS[n_receiver] = INSTANCE porigin_class',
 'pcallcontext.LEXICAL_CLASS = (porigin_class)',
 'pcallcontext.CALLED_CLASS = (porigin_class)',
 'pclosurecreator.CALLSITE = (porigin_site)',
 'pclosurecreation.CALLSITE = (porigin_site)',
 'pclosurecreation.FUNCTION = pcallcontext.FUNCTION',
 '$closure_evidence_body(S, n_source) = (pcallcontext.FUNCTION)',
 '$(n_source < n_child)',
 '$(n_receiver < n_child)',
 '$closure_creator_current(S) = (pclosurecreator)',
 '$closure_evidence_current(S) = (pclosurecreator.SCOPE)',
 '$closure_evidence_valid(S, pclosurecreator.SCOPE)',
 '$closure_scope_creation_valid(S, porigin_child, pclosurescope)',
 '$closure_scope_row_valid(S, pclosurescope)',
 '$closure_capture_valid(S, n_child, 0)',
 '$closure_evidence_current(S[.CURRENT = (pcallcontext[.RECEIVER = eps])]) = eps',
 '$closure_evidence_current(S[.CURRENT = (pcallcontext[.LEXICAL_CLASS = (porigin_child)])]) = eps',
 '$closure_evidence_current(S[.CURRENT = (pcallcontext[.CALLED_CLASS = (porigin_child)])]) = eps',
 '$closure_evidence_current(S[.CURRENT = (pcallcontext[.CALLSITE = eps])]) = eps',
 '~$closure_evidence_valid(S, CLOSURE_CALL porigin_child n_source n_receiver porigin_class)',
 '~$closure_evidence_valid(S, CLOSURE_CALL porigin_site n_receiver n_receiver porigin_class)',
 '~$closure_evidence_valid(S, CLOSURE_CALL porigin_site n_source n_source porigin_class)',
 '~$closure_evidence_valid(S, CLOSURE_CALL porigin_site n_source n_receiver porigin_child)',
 'n_objects = |S.OBJECTS|',
 '~$closure_evidence_valid(S, CLOSURE_CALL porigin_site n_objects n_receiver porigin_class)',
 '~$closure_evidence_valid(S, CLOSURE_CALL porigin_site n_source n_objects porigin_class)',
 '~$closure_scope_row_valid(S, pclosurescope[.CREATION = eps])',
 '~$closure_scope_row_valid(S, pclosurescope[.CREATION = (pclosurecreation[.EVIDENCE = eps])])',
 '~$closure_scope_row_valid(S, pclosurescope[.CREATION = (pclosurecreation[.FUNCTION = porigin_child])])',
 'pclosurecreator_site = pclosurecreator[.CALLSITE = (porigin_child)]',
 'pclosurecreation_site = pclosurecreation[.CALLSITE = (porigin_child)][.EVIDENCE = (pclosurecreator_site)]',
 '~$closure_scope_row_valid(S, pclosurescope[.CREATION = (pclosurecreation_site)])',
 'pclosurecreator_null = pclosurecreator[.CALLSITE = eps]',
 'pclosurecreation_null = pclosurecreation[.CALLSITE = eps][.EVIDENCE = (pclosurecreator_null)]',
 '~$closure_scope_row_valid(S, pclosurescope[.CREATION = (pclosurecreation_null)])',
 'pclosurecreator_self = pclosurecreator[.SCOPE = CLOSURE_CALL porigin_site n_child n_receiver porigin_class]',
 '~$closure_scope_row_valid(S, pclosurescope[.CREATION = (pclosurecreation[.EVIDENCE = (pclosurecreator_self)])])',
 '$closure_evidence_valid(S, CLOSURE_SCOPE pclosurescope)',
 '$closure_scope_complete(S, S.ALLOCATIONS)'
]
RETIRE = [
 'S_done = $drive_steps(S, 1400)',
 r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
 '~((HOBJECT n_source) <- S_done.ALLOCATIONS)',
 '~((HOBJECT n_child) <- S_done.ALLOCATIONS)',
 '$closure_scope_at(S_done.CLOSURESCOPES, n_source) = eps',
 '$closure_scope_at(S_done.CLOSURESCOPES, n_child) = eps',
 '$closure_evidence_valid(S_done, pclosurecreator.SCOPE)',
 '$closure_evidence_valid(S_done, CLOSURE_SCOPE pclosurescope)',
 '$closure_scope_creation_valid(S_done, porigin_child, pclosurescope)',
 '$closure_state_valid(S_done)',
 '$class_constant_history_valid(S_done)',
 'S_dead = $prune_allocations(S_done[.ENV = eps][.GLOBALTABLE = eps][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)])',
 '~((HOBJECT n_source) <- S_dead.ALLOCATIONS)',
 '~((HOBJECT n_receiver) <- S_dead.ALLOCATIONS)',
 '~((HOBJECT n_child) <- S_dead.ALLOCATIONS)',
 '$closure_evidence_valid(S_dead, pclosurecreator.SCOPE)',
 '$closure_evidence_valid(S_dead, CLOSURE_SCOPE pclosurescope)',
 '$closure_scope_creation_valid(S_dead, porigin_child, pclosurescope)',
 '$closure_state_valid(S_dead)'
]
protocol.CHECKS = {'global-escaping-child': [
 'S = $closure_call_test_seek(S_initial[.COMPLETION = NORMAL], false, 900)',
 *COMMON,
 'pclosurescope.RECEIVER = (n_receiver)',
 'pclosurecreation.RECEIVER',
 '$closure_source_class(S, porigin_child) = eps',
 '~$closure_scope_row_valid(S, pclosurescope[.RECEIVER = eps])',
 '~$closure_scope_row_valid(S, pclosurescope[.RECEIVER = (n_source)])',
 *RETIRE,
 '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
 '$closure_call_test_output(S_done.EVENTS) = $ptascii("A:7:5")'
], 'callback-resume-throw': [
 'S = $closure_call_test_seek(S_initial[.COMPLETION = NORMAL], true, 1100)',
 *COMMON,
 'pclosurescope.RECEIVER = eps',
 '~pclosurecreation.RECEIVER',
 '$closure_call_test_output(S.EVENTS) = $ptascii("H:")',
 '(HOBJECT n_source) <- $call_context_roots(S.CURRENT)',
 '(HOBJECT n_receiver) <- $call_context_roots(S.CURRENT)',
 '$heap_owners($heap_graph(S), HOBJECT n_source) = 1',
 '~$closure_scope_row_valid(S, pclosurescope[.RECEIVER = (n_receiver)])',
 '~$closure_evidence_valid(S, CLOSURE_CALL porigin_site n_child n_receiver porigin_class)',
 *RETIRE,
 '(HOBJECT n_receiver) <- S_done.ALLOCATIONS',
 '$heap_owners($heap_graph(S_done), HOBJECT n_receiver) = 1',
 '$closure_call_test_output(S_done.EVENTS) = $ptascii("H:E:7:B:9")'
]}

protocol.SOURCES['own-class-static-child'] = '''<?php
class A {
    public static function make(){
        return function(){
            return static function(){
                echo get_called_class(),':',self::class;
            };
        };
    }
}
$maker=A::make();
$child=$maker->call(new A);
unset($maker);
$child();
unset($child);
'''
protocol.CHECKS['own-class-static-child'] = [
 'S = $closure_call_test_seek(S_initial[.COMPLETION = NORMAL], true, 900)',
 'S.CURRENT = (pcallcontext)',
 '$context_target(pcallcontext) = CLOSURE_CALL_TARGET n_source n_receiver',
 '$call_current_valid(S)',
 'pcallcontext.CALLSITE = (porigin_site)',
 'S.TODO = (CLOSURE_CAPTURE n_child 0) :: ptask_tail*',
 '$object_body(S.OBJECTS[n_child]) = REALCLOSURE porigin_child pitem* pstaticcell*',
 '$closure_scope_at(S.CLOSURESCOPES, n_child) = (pclosurescope)',
 'pclosurescope.CREATION = (pclosurecreation)',
 'pclosurecreation.EVIDENCE = (pclosurecreator)',
 'pclosurecreator.SCOPE = CLOSURE_CALL porigin_site n_source n_receiver porigin_class',
 '$class_named(S.CLASSNAMES, $ptascii("a")) = (porigin_class)',
 '$closure_source_class(S, porigin_child) = (porigin_class)',
 'pclosurescope.LEXICAL = porigin_class',
 'pclosurescope.CALLED = porigin_class',
 'pclosurescope.RECEIVER = eps',
 '~pclosurecreation.RECEIVER',
 '$closure_scope_original_classes(S, porigin_child, pclosurescope)',
 '$closure_creator_valid(S, porigin_child, pclosurescope, pclosurecreation, pclosurecreator)',
 '$closure_scope_classes_valid(S, porigin_child, pclosurescope)',
 '$closure_receiver_forbidden(S, porigin_child)',
 '$closure_scope_receiver_free(S, porigin_child, pclosurescope)',
 '$closure_scope_row_valid(S, pclosurescope)',
 '$closure_capture_valid(S, n_child, 0)',
 '$closure_evidence_valid(S, CLOSURE_SCOPE pclosurescope)',
 'S_done = $drive_steps(S, 700)',
 r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
 '$closure_call_test_output(S_done.EVENTS) = $ptascii("A:A")',
 '~((HOBJECT n_source) <- S_done.ALLOCATIONS)',
 '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
 '~((HOBJECT n_child) <- S_done.ALLOCATIONS)',
 '$closure_evidence_valid(S_done, pclosurecreator.SCOPE)',
 '$closure_evidence_valid(S_done, CLOSURE_SCOPE pclosurescope)',
 '$closure_state_valid(S_done)'
]

if __name__ == '__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--prepare');args=parser.parse_args()
 if args.prepare:protocol.prepare(Path(args.prepare));print(args.prepare)
 else:protocol.run(Path(tempfile.mkdtemp(prefix='closure-call-creation-',dir=protocol.ROOT/'.tools'))/'run')
