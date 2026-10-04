#!/usr/bin/env python3
"""Check delayed static-reference selection, sole-cell ownership and retirement."""
import argparse,tempfile
from pathlib import Path
import deferred_static_default_protocol as protocol

protocol.SOURCES = {'selected-cold-reference': '''<?php
class A { public static int $p = E_STRICT; }
class C { public static int $p = 40; }
class B { public static int $q = 4; }
function h($l, $m, $f, $n) {
    echo "H:";
    restore_error_handler();
    $GLOBALS["escaped"] =& $GLOBALS["which"]::$p;
    $GLOBALS["escaped"] = 9;
    $GLOBALS["replacement"] = 6;
    B::$q =& $GLOBALS["replacement"];
    $GLOBALS["which"] = "C";
    return true;
}
$which = "A";
$name = "p";
set_error_handler("h");
$which::${$name} =& B::$q;
echo A::$p, ":", B::$q, ":", $escaped, ":";
A::$p = 11;
try { $escaped = "bad"; echo "free:"; } catch (TypeError $e) { echo "typed:"; }
echo A::$p, ":", B::$q, ":", $escaped, ":", C::$p;
'''}
protocol.PREFIX += '''
dec $cold_static_test_output(pevent*) : ptbytes
def $cold_static_test_output(eps) = eps
def $cold_static_test_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $cold_static_test_output(pevent*)
dec $cold_static_test_stage(pstate, nat) : bool
def $cold_static_test_stage(S, 0) = true
  -- if S.FRAMES = eps
  -- if S.TODO = (PROPERTY_REF_BIND (BASE_CLASS_STATIC_PENDING poperand_class poperand_name) n_cell z) :: ptask_tail*
def $cold_static_test_stage(S, 1) = true
  -- if S.FRAMES = eps
  -- if S.TODO = (STATIC_DEFAULT_BIND pstaticdefaultcontext) :: ptask_tail*
  -- if $class_static_at(S.CLASSSTATICS, pstaticdefaultcontext.DECL) = (pclassstatic)
  -- if pclassstatic.STATE = PROP_VALUE (ALIAS n_cell)
def $cold_static_test_stage(S, 2) = true
  -- if S.FRAMES = eps
  -- if S.TODO = (PROPERTY_REF_BIND (BASE_CLASS_STATIC porigin ptbytes) n_cell z) :: ptask_tail*
def $cold_static_test_stage(S, n) = false -- otherwise
dec $cold_static_test_seek(pstate, nat, nat) : pstate
def $cold_static_test_seek(S, n, n_limit) = S
  -- if $cold_static_test_stage(S, n)
def $cold_static_test_seek(S, n, n_limit) = $cold_static_test_seek($static_default_test_resume(S_next), n, n_rest)
  -- if ~$cold_static_test_stage(S, n)
  -- if $(n_limit > 0)
  -- if S.COMPLETION = NORMAL
  -- if ~S.COMPILESTOP
  -- if n_rest = $(n_limit - 1)
  -- if S_next = $drive_steps(S, 1)
'''
protocol.CHECKS = {'selected-cold-reference': [
 'S = $cold_static_test_seek(S_initial[.COMPLETION = NORMAL], 0, 500)',
 'S.TODO = (PROPERTY_REF_BIND (BASE_CLASS_STATIC_PENDING poperand_class poperand_name) n_rhs z) :: ptask_tail*',
 'S.ORIGIN = (porigin_assignment)',
 '$class_named(S.CLASSNAMES, $ptascii("a")) = (porigin_a)',
 '$class_named(S.CLASSNAMES, $ptascii("b")) = (porigin_b)',
 '$class_named(S.CLASSNAMES, $ptascii("c")) = (porigin_c)',
 '$class_at(S.CLASSES, porigin_a) = (pclassdesc_a)',
 '$class_at(S.CLASSES, porigin_b) = (pclassdesc_b)',
 'pclassdesc_a.PROPERTIES = [ppropertydesc_a]',
 'pclassdesc_b.PROPERTIES = [ppropertydesc_b]',
 'porigin_p = ppropertydesc_a.ORIGIN',
 'porigin_q = ppropertydesc_b.ORIGIN',
 'S.STORE[n_rhs] = DEFINED (PINT 4)',
 '$class_static_at(S.CLASSSTATICS, porigin_q) = ({DECL porigin_q, STATE PROP_VALUE (ALIAS n_rhs)})',
 '~$class_constant_table_done(S, porigin_a)',
 'S_queue = $static_default_test_resume($drive_steps(S, 1))',
 'S_queue.TODO = (STATIC_DEFAULT_UPDATE porigin_p z) :: (CLASS_CONST_TABLE_UPDATE porigin_a z) :: (CLASS_CONST_SELECTED pstaticselection ptbytes z) :: (ORIGIN_RETURN (porigin_assignment)) :: (PROPERTY_REF_BIND (BASE_CLASS_STATIC porigin_a ptbytes) n_rhs z) :: ptask_tail*',
 'pstaticselection = {SITE porigin_target, ROOT porigin_a, SCOPE eps, CALLED eps}',
 'S_queue.ORIGIN = (porigin_target)',
 '$origin_child((porigin_assignment), [PCFIELD 0]) = (porigin_target)',
 'ptbytes = $ptascii("p")',
 '$class_static_selection_valid(S_queue, pstaticselection)',
 '$call_tasks_valid(S_queue, S_queue.TODO)',
 '$class_constant_state_valid(S_queue)',
 '$class_statics_valid(S_queue)',
 '$proprefs_valid(S_queue)',
 'ptask_wrong_class* = [STATIC_DEFAULT_UPDATE porigin_p z, CLASS_CONST_TABLE_UPDATE porigin_a z, CLASS_CONST_SELECTED pstaticselection ptbytes z, ORIGIN_RETURN (porigin_assignment), PROPERTY_REF_BIND (BASE_CLASS_STATIC porigin_c ptbytes) n_rhs z] ++ ptask_tail*',
 '~$call_tasks_valid(S_queue[.TODO = ptask_wrong_class*], ptask_wrong_class*)',
 'ptask_wrong_name* = [STATIC_DEFAULT_UPDATE porigin_p z, CLASS_CONST_TABLE_UPDATE porigin_a z, CLASS_CONST_SELECTED pstaticselection ptbytes z, ORIGIN_RETURN (porigin_assignment), PROPERTY_REF_BIND (BASE_CLASS_STATIC porigin_a $ptascii("q")) n_rhs z] ++ ptask_tail*',
 '~$call_tasks_valid(S_queue[.TODO = ptask_wrong_name*], ptask_wrong_name*)',
 'ptask_wrong_origin* = [STATIC_DEFAULT_UPDATE porigin_p z, CLASS_CONST_TABLE_UPDATE porigin_a z, CLASS_CONST_SELECTED pstaticselection ptbytes z, ORIGIN_RETURN (porigin_target), PROPERTY_REF_BIND (BASE_CLASS_STATIC porigin_a ptbytes) n_rhs z] ++ ptask_tail*',
 '~$call_tasks_valid(S_queue[.TODO = ptask_wrong_origin*], ptask_wrong_origin*)',
 '~$class_static_selection_valid(S_queue, pstaticselection[.SCOPE = (porigin_a)])',
 '~$class_static_selection_valid(S_queue, pstaticselection[.CALLED = (porigin_c)])',
 'S_outer = $cold_static_test_seek(S_queue, 1, 1600)',
 'S_outer.TODO = (STATIC_DEFAULT_BIND pstaticdefaultcontext) :: ptask_outer_tail*',
 '$class_static_selection_at(S_outer.TODO) = (pstaticselection)',
 '$class_static_at(S_outer.CLASSSTATICS, porigin_p) = ({DECL porigin_p, STATE PROP_VALUE (ALIAS n_escaped)})',
 'S_outer.STORE[n_escaped] = DEFINED (PINT 9)',
 '$class_static_at(S_outer.CLASSSTATICS, porigin_q) = ({DECL porigin_q, STATE PROP_VALUE (ALIAS n_replacement)})',
 'S_outer.STORE[n_replacement] = DEFINED (PINT 6)',
 'n_replacement =/= n_rhs',
 'S_outer.STORE[n_rhs] = DEFINED (PINT 4)',
 '$heap_owners($heap_graph(S_outer), HCELL n_rhs) = 1',
 '(HCELL n_rhs) <- $tasks_nodes(S_outer.TODO)',
 '~$propref_source_present(S_outer.PROPREFS, n_rhs, CLASS_PROP_SOURCE porigin_q)',
 '$static_default_bind_valid(S_outer, pstaticdefaultcontext)',
 'n_event = |S_outer.CLASSCONSTANTHISTORY|',
 'S_retired = $static_default_test_resume($drive_steps(S_outer, 1))',
 'n_prefix = |S_retired.DECLARATIONS|',
 'S_retired.CLASSCONSTANTHISTORY = S_outer.CLASSCONSTANTHISTORY ++ [CCSTATICRETIRESELECT porigin_p pstaticselection n_prefix n_escaped]',
 '$class_static_at(S_retired.CLASSSTATICS, porigin_p) = ({DECL porigin_p, STATE PROP_VALUE (DIRECT (PINT 2048))})',
 '$propref_source_valid(S_retired, n_escaped, RETIRED_CLASS_PROP_SOURCE porigin_p n_event)',
 '~$propref_source_valid(S_retired, n_rhs, RETIRED_CLASS_PROP_SOURCE porigin_p n_event)',
 '~$class_constant_history_valid(S_retired[.CLASSCONSTANTHISTORY = S_outer.CLASSCONSTANTHISTORY ++ [CCSTATICRETIRESELECT porigin_p (pstaticselection[.ROOT = porigin_c]) n_prefix n_escaped]])',
 r'$class_constant_state_valid(S_retired) /\ $class_statics_valid(S_retired) /\ $proprefs_valid(S_retired)',
 'S_bind = $cold_static_test_seek(S_retired, 2, 100)',
 'S_bind.TODO = (PROPERTY_REF_BIND (BASE_CLASS_STATIC porigin_a ptbytes) n_rhs z) :: ptask_tail*',
 'S_bind.ORIGIN = (porigin_assignment)',
 'S_bind.BASE = BASE_CLASS_STATIC porigin_a ptbytes',
 '$call_tasks_valid(S_bind, S_bind.TODO)',
 '~$call_tasks_valid(S_bind[.BASE = BASE_VALUE (KNOWN PNULL)], S_bind.TODO)',
 '~$call_tasks_valid(S_bind[.TODO = (PROPERTY_REF_BIND (BASE_CLASS_STATIC porigin_c ptbytes) n_rhs z) :: ptask_tail*], (PROPERTY_REF_BIND (BASE_CLASS_STATIC porigin_c ptbytes) n_rhs z) :: ptask_tail*)',
 '~$call_tasks_valid(S_bind[.TODO = (PROPERTY_REF_BIND (BASE_CLASS_STATIC porigin_a $ptascii("q")) n_rhs z) :: ptask_tail*], (PROPERTY_REF_BIND (BASE_CLASS_STATIC porigin_a $ptascii("q")) n_rhs z) :: ptask_tail*)',
 '$class_constant_static_reference_ready(S_bind, porigin_a, ptbytes, z)',
 '$heap_owners($heap_graph(S_bind), HCELL n_rhs) = 1',
 'S_bound = $static_default_test_resume($drive_steps(S_bind, 1))',
 '$class_static_at(S_bound.CLASSSTATICS, porigin_p) = ({DECL porigin_p, STATE PROP_VALUE (ALIAS n_rhs)})',
 'S_bound.STORE[n_rhs] = DEFINED (PINT 4)',
 '$propref_source_present(S_bound.PROPREFS, n_rhs, CLASS_PROP_SOURCE porigin_p)',
 'S_done = $drive_steps(S_bound, 800)',
 r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
 '$cold_static_test_output(S_done.EVENTS) = $ptascii("H:4:6:9:typed:11:6:9:40")',
 'S_done.STORE[n_rhs] = DEFINED (PINT 11)',
 'S_done.STORE[n_replacement] = DEFINED (PINT 6)',
 'S_done.STORE[n_escaped] = DEFINED (PINT 9)',
 r'$class_constant_state_valid(S_done) /\ $class_statics_valid(S_done) /\ $proprefs_valid(S_done)',
 'S_dead = $prune_allocations(S_done[.ENV = eps][.GLOBALTABLE = eps][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)])',
 '~((HCELL n_escaped) <- S_dead.ALLOCATIONS)',
 '$propref_at(S_dead.PROPREFS, n_escaped) = eps',
 '(HCELL n_rhs) <- S_dead.ALLOCATIONS',
 'S_dead.CLASSCONSTANTHISTORY = S_done.CLASSCONSTANTHISTORY',
 r'$class_constant_history_valid(S_dead) /\ $class_statics_valid(S_dead) /\ $proprefs_valid(S_dead)'
]}

if __name__ == '__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--prepare');args=parser.parse_args()
 if args.prepare:protocol.prepare(Path(args.prepare));print(args.prepare)
 else:protocol.run(Path(tempfile.mkdtemp(prefix='cold-static-reference-',dir=protocol.ROOT/'.tools'))/'run')
