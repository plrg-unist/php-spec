#!/usr/bin/env python3
"""Check borrowed Closure scope, nested creation and selected static ownership."""
import argparse,tempfile
from pathlib import Path
import deferred_static_default_protocol as protocol

protocol.SOURCES = {'bound-reentry': '''<?php
class A { public static int $p = E_STRICT; }
class B { public static int $q = 4; }
class R {}
$inner = function () { $GLOBALS["escaped"] =& self::$p; $GLOBALS["escaped"] = 9; };
$outer = function () { self::$p =& B::$q; };
$inner = $inner->bindTo(new R(), A::class);
$outer = $outer->bindTo(new R(), A::class);
function h($l, $m, $f, $n) {
    echo "H:";
    restore_error_handler();
    $GLOBALS["inner"]();
    $GLOBALS["replacement"] = 6;
    B::$q =& $GLOBALS["replacement"];
    unset($GLOBALS["inner"], $GLOBALS["outer"]);
    return true;
}
set_error_handler("h");
$outer();
echo A::$p, ":", B::$q, ":", $escaped, ":";
A::$p = 11;
try { $escaped = "bad"; echo "free:"; } catch (TypeError $e) { echo "typed:"; }
echo A::$p, ":", B::$q, ":", $escaped;
''', 'handler-nested': '''<?php
class A { public static int $p = N; }
class R {}
$f = function ($l, $m, $f, $n) {
    echo get_called_class(), ":";
    $GLOBALS["getter"] = function &() { return self::$p; };
    return true;
};
$g = $f->bindTo(new R(), A::class);
unset($f);
set_error_handler($g);
unset($g);
const N = 5;
echo $missing;
restore_error_handler();
$r =& $getter(); echo $r, ":";
unset($getter);
$r = 8; echo A::$p;
''', 'terminal-nested': '''<?php
class A { public static int $p = N; }
class R {}
$f = function ($e) {
    echo get_called_class(), ":";
    restore_exception_handler();
    $g = function &() { return self::$p; };
    $r =& $g(); echo $r, ":";
    unset($g);
    $r = 8; echo A::$p;
};
$h = $f->bindTo(new R(), A::class);
unset($f);
set_exception_handler($h);
unset($h);
const N = 5;
throw new Exception("stop");
'''}
protocol.PREFIX += '''
dec $cold_closure_test_output(pevent*) : ptbytes
def $cold_closure_test_output(eps) = eps
def $cold_closure_test_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $cold_closure_test_output(pevent*)
dec $cold_closure_test_stage(pstate, nat) : bool
def $cold_closure_test_stage(S, 0) = true
  -- if S.TODO = (PROPERTY_REF_BIND (BASE_CLASS_STATIC_PENDING poperand_class poperand_name) n_cell z) :: ptask_tail*
def $cold_closure_test_stage(S, 1) = true
  -- if S.TODO = (STATIC_DEFAULT_BIND pstaticdefaultcontext) :: ptask_tail*
  -- if $class_static_at(S.CLASSSTATICS, pstaticdefaultcontext.DECL) = (pclassstatic)
  -- if pclassstatic.STATE = PROP_VALUE (ALIAS n_cell)
def $cold_closure_test_stage(S, 2) = true
  -- if S.TODO = (CLOSURE_CAPTURE n 0) :: ptask_tail*
  -- if $closure_scope_at(S.CLOSURESCOPES, n) = (pclosurescope)
  -- if pclosurescope.CREATION = (pclosurecreation)
  -- if pclosurecreation.EVIDENCE = (pclosurecreator)
def $cold_closure_test_stage(S, 3) = true
  -- if S.TODO = (STATIC_DEFAULT_UPDATE porigin_p z) :: ptask_tail*
  -- if $class_static_selection_at(S.TODO) = (pstaticselection)
  -- if pstaticselection.CLOSURE = (CLOSURE_SCOPE pclosurescope)
def $cold_closure_test_stage(S, n) = false -- otherwise
dec $cold_closure_test_seek(pstate, nat, nat) : pstate
def $cold_closure_test_seek(S, n, n_limit) = S
  -- if $cold_closure_test_stage(S, n)
def $cold_closure_test_seek(S, n, n_limit) = $cold_closure_test_seek($static_default_test_resume(S_next), n, n_rest)
  -- if ~$cold_closure_test_stage(S, n)
  -- if $(n_limit > 0)
  -- if S.COMPLETION = NORMAL
  -- if ~S.COMPILESTOP
  -- if n_rest = $(n_limit - 1)
  -- if S_next = $drive_steps(S, 1)
'''
protocol.CHECKS = {'bound-reentry': [
 'S = $cold_closure_test_seek(S_initial[.COMPLETION = NORMAL], 0, 900)',
 'S.TODO = (PROPERTY_REF_BIND (BASE_CLASS_STATIC_PENDING poperand_class poperand_name) n_rhs z) :: ptask_tail*',
 'S.CURRENT = (pcallcontext)',
 '$context_target(pcallcontext) = CLOSURE_TARGET n_outer',
 '$call_current_valid(S)',
 '$class_named(S.CLASSNAMES, $ptascii("a")) = (porigin_a)',
 '$class_named(S.CLASSNAMES, $ptascii("b")) = (porigin_b)',
 '$class_named(S.CLASSNAMES, $ptascii("r")) = (porigin_r)',
 '$closure_binding_at(S.CLOSUREBINDINGS, n_outer) = (pclosurebinding)',
 'pclosurebinding.LEXICAL = (porigin_a)',
 'pclosurebinding.CALLED = (porigin_r)',
 'pclosurebinding.RECEIVER = (n_receiver)',
 'S.OBJECTS[n_receiver] = INSTANCE porigin_r',
 'n_source = pclosurebinding.SOURCE',
 '$object_body(S.OBJECTS[n_source]) = REALCLOSURE pcallcontext.FUNCTION pitem_source* pstaticcell_source*',
 '~$class_constant_parent_chain(S, porigin_r, porigin_a, |S.CLASSES|)',
 '$closure_evidence_current(S) = (CLOSURE_BINDING pclosurebinding)',
 '$closure_evidence_valid(S, CLOSURE_BINDING pclosurebinding)',
 '$closure_evidence_current(S[.CURRENT = (pcallcontext[.RECEIVER = eps])]) = eps',
 'S_queue = $static_default_test_resume($drive_steps(S, 1))',
 'S_queue.TODO = (STATIC_DEFAULT_UPDATE porigin_p z) :: (CLASS_CONST_TABLE_UPDATE porigin_a z) :: (CLASS_CONST_SELECTED pstaticselection ptbytes z) :: ptask_queue_tail*',
 'pstaticselection.CLOSURE = (CLOSURE_BINDING pclosurebinding)',
 'pstaticselection.ROOT = porigin_a',
 'pstaticselection.SCOPE = (porigin_a)',
 'pstaticselection.CALLED = (porigin_r)',
 '$class_static_selection_valid(S_queue, pstaticselection)',
 '$class_constant_state_valid(S_queue)',
 '$call_tasks_valid(S_queue, S_queue.TODO)',
 '~$class_static_selection_valid(S_queue, pstaticselection[.CLOSURE = eps])',
 '~$class_static_selection_valid(S_queue, pstaticselection[.ROOT = porigin_b])',
 '~$class_static_selection_valid(S_queue, pstaticselection[.SCOPE = (porigin_b)])',
 '~$class_static_selection_valid(S_queue, pstaticselection[.CALLED = (porigin_a)])',
 '~$closure_evidence_valid(S_queue, CLOSURE_BINDING (pclosurebinding[.OBJECT = n_receiver]))',
 '~$closure_evidence_valid(S_queue, CLOSURE_BINDING (pclosurebinding[.SOURCE = n_outer]))',
 '~$closure_evidence_valid(S_queue, CLOSURE_BINDING (pclosurebinding[.SITE = pstaticselection.SITE]))',
 '~$closure_evidence_valid(S_queue, CLOSURE_BINDING (pclosurebinding[.LEXICAL = (porigin_b)]))',
 '~$closure_evidence_valid(S_queue, CLOSURE_BINDING (pclosurebinding[.CALLED = (porigin_a)]))',
 '~$closure_evidence_valid(S_queue, CLOSURE_BINDING (pclosurebinding[.RECEIVER = (n_source)]))',
 'S_outer = $cold_closure_test_seek(S_queue, 1, 1800)',
 '$class_static_at(S_outer.CLASSSTATICS, porigin_p) = ({DECL porigin_p, STATE PROP_VALUE (ALIAS n_escaped)})',
 'S_outer.STORE[n_escaped] = DEFINED (PINT 9)',
 'S_outer.STORE[n_rhs] = DEFINED (PINT 4)',
 '$heap_owners($heap_graph(S_outer), HCELL n_rhs) = 1',
 '(HCELL n_rhs) <- $tasks_nodes(S_outer.TODO)',
 '$class_static_selection_at(S_outer.TODO) = (pstaticselection)',
 'n_event = |S_outer.CLASSCONSTANTHISTORY|',
 'S_retired = $static_default_test_resume($drive_steps(S_outer, 1))',
 'n_prefix = |S_retired.DECLARATIONS|',
 'S_retired.CLASSCONSTANTHISTORY = S_outer.CLASSCONSTANTHISTORY ++ [CCSTATICRETIRESELECT porigin_p pstaticselection n_prefix n_escaped]',
 '$propref_source_valid(S_retired, n_escaped, RETIRED_CLASS_PROP_SOURCE porigin_p n_event)',
 '$class_constant_state_valid(S_retired)',
 '$class_statics_valid(S_retired)',
 '$proprefs_valid(S_retired)',
 'S_done = $drive_steps(S_retired, 1100)',
 r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
 '$cold_closure_test_output(S_done.EVENTS) = $ptascii("H:4:6:9:typed:11:6:9")',
 'S_dead = $prune_allocations(S_done[.ENV = eps][.GLOBALTABLE = eps][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)])',
 '~((HOBJECT n_outer) <- S_dead.ALLOCATIONS)',
 '~((HOBJECT n_source) <- S_dead.ALLOCATIONS)',
 '~((HOBJECT n_receiver) <- S_dead.ALLOCATIONS)',
 '$closure_binding_at(S_dead.CLOSUREBINDINGS, n_outer) = eps',
 '$closure_evidence_valid(S_dead, CLOSURE_BINDING pclosurebinding)',
 '$class_static_selection_valid(S_dead, pstaticselection)',
 'S_dead.CLASSCONSTANTHISTORY = S_done.CLASSCONSTANTHISTORY',
 '$class_constant_history_valid(S_dead)',
 '$class_statics_valid(S_dead)',
 '$proprefs_valid(S_dead)',
 '$closure_state_valid(S_dead)'
], 'handler-nested': [
 'S = $cold_closure_test_seek(S_initial[.COMPLETION = NORMAL], 2, 1000)',
 'S.TODO = (CLOSURE_CAPTURE n_inner 0) :: ptask_tail*',
 'S.CURRENT = (pcallcontext)',
 '$call_current_valid(S)',
 '$error_context_valid(S, pcallcontext)',
 '$object_body(S.OBJECTS[n_inner]) = REALCLOSURE porigin_inner pitem* pstaticcell*',
 '$closure_scope_at(S.CLOSURESCOPES, n_inner) = (pclosurescope)',
 'pclosurescope.CREATION = (pclosurecreation)',
 'pclosurecreation.EVIDENCE = (pclosurecreator)',
 'pclosurecreator.SCOPE = CLOSURE_BINDING pclosurebinding',
 'pclosurecreator.CALLSITE = pcallcontext.CALLSITE',
 '$closure_evidence_current(S) = (CLOSURE_BINDING pclosurebinding)',
 'n_creator = pclosurebinding.OBJECT',
 'pclosurecreation.FUNCTION = pcallcontext.FUNCTION',
 'pclosurecreation.CALLSITE = (porigin_emission)',
 'pcallcontext.CALLSITE = (porigin_emission)',
 '$origin_node(S.SOURCES, porigin_emission) = (NExprVariable (BYTES text_missing) metadata_missing)',
 '~$method_capture_invocation_valid(S, {FUNCTION pclosurecreation.FUNCTION, CALLSITE (porigin_emission), LEXICAL_CLASS (pclosurescope.LEXICAL), CALLED_CLASS (pclosurescope.CALLED)}, porigin_emission)',
 '$closure_source_class(S, porigin_inner) = eps',
 '$closure_scope_row_valid(S, pclosurescope)',
 '$closure_scope_creation_valid(S, porigin_inner, pclosurescope)',
 '$closure_evidence_valid(S, CLOSURE_SCOPE pclosurescope)',
 '~$closure_scope_row_valid(S, pclosurescope[.CREATION = eps])',
 '~$closure_scope_row_valid(S, pclosurescope[.LEXICAL = pclosurescope.CALLED])',
 '~$closure_scope_row_valid(S, pclosurescope[.CALLED = pclosurescope.LEXICAL])',
 '~$closure_scope_row_valid(S, pclosurescope[.CREATION = (pclosurecreation[.EVIDENCE = eps])])',
 '~$closure_scope_row_valid(S, pclosurescope[.CREATION = (pclosurecreation[.FUNCTION = porigin_inner])])',
 '~$closure_scope_row_valid(S, pclosurescope[.CREATION = (pclosurecreation[.CALLSITE = (porigin_inner)])])',
 'porigin_absent = PORIGIN |S.SOURCES| eps',
 'pclosurecreator_absent = pclosurecreator[.CALLSITE = (porigin_absent)]',
 'pclosurecreation_absent = pclosurecreation[.CALLSITE = (porigin_absent)][.EVIDENCE = (pclosurecreator_absent)]',
 '~$closure_scope_row_valid(S, pclosurescope[.CREATION = (pclosurecreation_absent)])',
 '~$closure_scope_row_valid(S, pclosurescope[.CREATION = (pclosurecreation[.EVIDENCE = (pclosurecreator[.SCOPE = CLOSURE_BINDING (pclosurebinding[.OBJECT = n_inner])])])])',
 '~$closure_scope_row_valid(S, pclosurescope[.CREATION = (pclosurecreation[.EVIDENCE = (pclosurecreator[.SCOPE = CLOSURE_BINDING (pclosurebinding[.SITE = porigin_inner])])])])',
 '$closure_scope_complete(S, S.ALLOCATIONS)',
 'S_queue = $cold_closure_test_seek(S, 3, 800)',
 '$class_static_selection_at(S_queue.TODO) = (pstaticselection)',
 'pstaticselection.CLOSURE = (CLOSURE_SCOPE pclosurescope)',
 '$class_static_selection_valid(S_queue, pstaticselection)',
 '$closure_scope_row_valid(S_queue, pclosurescope)',
 '$closure_binding_at(S_queue.CLOSUREBINDINGS, n_creator) = eps',
 '~((HOBJECT n_creator) <- S_queue.ALLOCATIONS)',
 '$closure_evidence_valid(S_queue, CLOSURE_BINDING pclosurebinding)',
 'S_done = $drive_steps(S_queue, 700)',
 r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
 '$cold_closure_test_output(S_done.EVENTS) = $ptascii("R:5:8")',
 'S_dead = $prune_allocations(S_done[.ENV = eps][.GLOBALTABLE = eps][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)])',
 '~((HOBJECT n_inner) <- S_dead.ALLOCATIONS)',
 '~((HOBJECT n_creator) <- S_dead.ALLOCATIONS)',
 '$closure_scope_at(S_dead.CLOSURESCOPES, n_inner) = eps',
 '$closure_evidence_valid(S_dead, CLOSURE_SCOPE pclosurescope)',
 '$class_static_selection_valid(S_dead, pstaticselection)',
 '$class_constant_history_valid(S_dead)',
 '$class_statics_valid(S_dead)',
 '$proprefs_valid(S_dead)',
 '$closure_state_valid(S_dead)'
], 'terminal-nested': [
 'S = $cold_closure_test_seek(S_initial[.COMPLETION = NORMAL], 2, 900)',
 'S.TODO = (CLOSURE_CAPTURE n_inner 0) :: ptask_tail*',
 'S.CURRENT = (pcallcontext)',
 '$call_current_valid(S)',
 '$exception_context_valid(S, pcallcontext)',
 'pcallcontext.CALLSITE = eps',
 '$object_body(S.OBJECTS[n_inner]) = REALCLOSURE porigin_inner pitem* pstaticcell*',
 '$closure_scope_at(S.CLOSURESCOPES, n_inner) = (pclosurescope)',
 'pclosurescope.CREATION = (pclosurecreation)',
 'pclosurecreation.CALLSITE = eps',
 'pclosurecreation.EVIDENCE = (pclosurecreator)',
 'pclosurecreator.CALLSITE = eps',
 'pclosurecreator.SCOPE = CLOSURE_BINDING pclosurebinding',
 '$closure_creator_current(S) = (pclosurecreator)',
 '$closure_scope_creation_valid(S, porigin_inner, pclosurescope)',
 '$closure_scope_row_valid(S, pclosurescope)',
 '~$closure_scope_row_valid(S, pclosurescope[.CREATION = (pclosurecreation[.CALLSITE = (porigin_inner)])])',
 '~$closure_scope_row_valid(S, pclosurescope[.CREATION = (pclosurecreation[.EVIDENCE = eps])])',
 'S_queue = $cold_closure_test_seek(S, 3, 450)',
 '$class_static_selection_at(S_queue.TODO) = (pstaticselection)',
 'pstaticselection.CLOSURE = (CLOSURE_SCOPE pclosurescope)',
 '$class_static_selection_valid(S_queue, pstaticselection)',
 '$class_constant_state_valid(S_queue)',
 'S_done = $drive_steps(S_queue, 700)',
 r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
 '$cold_closure_test_output(S_done.EVENTS) = $ptascii("R:5:8")',
 'S_dead = $prune_allocations(S_done[.ENV = eps][.GLOBALTABLE = eps][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)])',
 '~((HOBJECT n_inner) <- S_dead.ALLOCATIONS)',
 '$closure_evidence_valid(S_dead, CLOSURE_SCOPE pclosurescope)',
 '$class_static_selection_valid(S_dead, pstaticselection)',
 '$class_constant_history_valid(S_dead)',
 '$class_statics_valid(S_dead)',
 '$proprefs_valid(S_dead)',
 '$closure_state_valid(S_dead)'
]}

if __name__ == '__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--prepare');args=parser.parse_args()
 if args.prepare:protocol.prepare(Path(args.prepare));print(args.prepare)
 else:protocol.run(Path(tempfile.mkdtemp(prefix='cold-closure-static-',dir=protocol.ROOT/'.tools'))/'run')
