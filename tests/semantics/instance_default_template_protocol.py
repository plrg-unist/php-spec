#!/usr/bin/env python3
"""Check class-owned instance templates, link copies, strict fills and reentry."""
import argparse,tempfile
from pathlib import Path
import deferred_static_default_protocol as protocol

protocol.SOURCES = {'private-shadow-phase-order': '<?php\n'
                               'class A {\n'
                               '    const K=E_STRICT+0;\n'
                               '    private int $p=E_STRICT+1;\n'
                               '    public static int $q=E_STRICT+2;\n'
                               '    public function base(){ return $this->p; }\n'
                               '}\n'
                               'class B extends A {\n'
                               '    private int $p=E_STRICT+3;\n'
                               '    public static int $r=E_STRICT+4;\n'
                               '    public function own(){ return $this->p; }\n'
                               '}\n'
                               'set_error_handler(function($level,$message,$file,$line){ echo '
                               "$line,':'; return true; });\n"
                               '$b=new B;\n'
                               "echo A::K,':',$b->base(),':',$b->own(),':',A::$q,':',B::$r;\n"
                               'restore_error_handler();\n',
 'partial-parent-link-retry': '<?php\n'
                              'class A {\n'
                              '    public array $a=[E_STRICT+N];\n'
                              '    public int $b=E_STRICT+LATE;\n'
                              '    public static int $c=E_STRICT;\n'
                              '}\n'
                              'const N=7;\n'
                              'set_error_handler(function($level,$message,$file,$line){ echo '
                              "$line,':'; return true; });\n"
                              "try { new A; } catch(Error $e) { echo 'F:'; }\n"
                              'if(true) { class B extends A {} }\n'
                              'const LATE=9;\n'
                              '$b=new B;\n'
                              "echo $b->a[0],':',$b->b,':',A::$c;\n"
                              'restore_error_handler();\n',
 'late-child-before-parent-replacement': '<?php\n'
                                         'class A { public array $a=[E_STRICT]; }\n'
                                         '$child=null;\n'
                                         'set_error_handler(function() use(&$child){\n'
                                         "    echo 'H:';\n"
                                         '    error_reporting(0);\n'
                                         '    $inner=new A;\n'
                                         '    if(true) { class B extends A {} }\n'
                                         '    $child=new B;\n'
                                         '    error_reporting(30719);\n'
                                         '    return true;\n'
                                         '});\n'
                                         '$outer=new A;\n'
                                         'restore_error_handler();\n'
                                         '$outer->a[0]=1;\n'
                                         '$child->a[0]=2;\n'
                                         '$a=new A;\n'
                                         '$b=new B;\n'
                                         'echo '
                                         "$outer->a[0],':',$child->a[0],':',$a->a[0],':',$b->a[0];\n"
                                         'unset($outer,$child,$a,$b);\n'}

protocol.PREFIX = r'''
dec $instance_template_test_resume(pstate) : pstate
def $instance_template_test_resume(S) = S[.COMPLETION = NORMAL] -- if S.COMPLETION = BUDGET
def $instance_template_test_resume(S) = S -- otherwise
dec $instance_template_test_output(pevent*) : ptbytes
def $instance_template_test_output(eps) = eps
def $instance_template_test_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $instance_template_test_output(pevent*)
dec $instance_template_test_objects(pstate, pnode*, porigin) : nat*
dec $instance_template_test_object(pstate, pnode, porigin) : bool
def $instance_template_test_object(S, HOBJECT n, porigin) = (S.OBJECTS[n] = INSTANCE porigin)
def $instance_template_test_object(S, pnode, porigin) = false -- otherwise
def $instance_template_test_objects(S, eps, porigin) = eps
def $instance_template_test_objects(S, (HOBJECT n) :: pnode*, porigin) = n :: $instance_template_test_objects(S, pnode*, porigin)
  -- if S.OBJECTS[n] = INSTANCE porigin
def $instance_template_test_objects(S, pnode :: pnode_tail*, porigin) = $instance_template_test_objects(S, pnode_tail*, porigin)
  -- if ~$instance_template_test_object(S, pnode, porigin)
dec $instance_template_test_fill_event(pclassconstantevent) : bool
def $instance_template_test_fill_event(CCINSTANCE porigin_class porigin_decl porigin_root porigin_trigger pstaticselection? n) = true
def $instance_template_test_fill_event(pclassconstantevent) = false -- otherwise
dec $instance_template_test_fills(pclassconstantevent*) : (porigin, porigin)*
def $instance_template_test_fills(eps) = eps
def $instance_template_test_fills((CCINSTANCE porigin_class porigin_decl porigin_root porigin_trigger pstaticselection? n) :: pclassconstantevent*) = (porigin_class, porigin_decl) :: $instance_template_test_fills(pclassconstantevent*)
def $instance_template_test_fills(pclassconstantevent :: pclassconstantevent_tail*) = $instance_template_test_fills(pclassconstantevent_tail*)
  -- if ~$instance_template_test_fill_event(pclassconstantevent)
dec $instance_template_test_stage(pstate, nat) : bool
def $instance_template_test_stage(S, 0) = true
  -- if S.TODO = (INSTANCE_DEFAULT_UPDATE porigin_a porigin_p z) :: ptask_tail*
  -- if $class_named(S.CLASSNAMES, $ptascii("a")) = (porigin_a)
  -- if $class_named(S.CLASSNAMES, $ptascii("b")) = (porigin_b)
def $instance_template_test_stage(S, 1) = true
  -- if S.TODO = (INSTANCE_DEFAULT_BIND porigin_b pstaticdefaultcontext) :: ptask_tail*
  -- if $class_named(S.CLASSNAMES, $ptascii("b")) = (porigin_b)
  -- if $property_declaring_class(S.CLASSES, pstaticdefaultcontext.DECL) = (porigin_a)
  -- if porigin_a =/= porigin_b
def $instance_template_test_stage(S, 2) = true
  -- if $class_named(S.CLASSNAMES, $ptascii("a")) = (porigin_a)
  -- if $class_named(S.CLASSNAMES, $ptascii("b")) = (porigin_b)
  -- if $class_at(S.CLASSES, porigin_a) = (pclassdesc)
  -- if pclassdesc.PROPERTIES = [ppropertydesc_a, ppropertydesc_b, ppropertydesc_c]
  -- if ppropertydesc_b.ORIGIN = porigin_decl
  -- if $instance_default_pending(S, porigin_a, porigin_decl)
  -- if $instance_default_pending(S, porigin_b, porigin_decl)
def $instance_template_test_stage(S, 3) = true
  -- if S.TODO = (INSTANCE_DEFAULT_BIND porigin_a pstaticdefaultcontext) :: ptask_tail*
  -- if $class_named(S.CLASSNAMES, $ptascii("a")) = (porigin_a)
  -- if $class_named(S.CLASSNAMES, $ptascii("b")) = (porigin_b)
  -- if $instance_default_at(S.INSTANCEDEFAULTS, porigin_a, pstaticdefaultcontext.DECL) = (pinstancetemplate)
  -- if pinstancetemplate.STATE = INSTANCE_VALUE (PARRAY n_inner) pvalueclass
  -- if S.RESULT = KNOWN (PARRAY n_outer)
  -- if n_inner =/= n_outer
def $instance_template_test_stage(S, 4) = true
  -- if S.TODO = (INSTANCE_DEFAULT_BIND porigin_a pstaticdefaultcontext) :: ptask_tail*
  -- if $class_named(S.CLASSNAMES, $ptascii("a")) = (porigin_a)
  -- if $class_named(S.CLASSNAMES, $ptascii("b")) = (porigin_b)
  -- if $instance_default_pending(S, porigin_a, pstaticdefaultcontext.DECL)
def $instance_template_test_stage(S, n) = false -- otherwise
dec $instance_template_test_seek(pstate, nat, nat) : pstate
def $instance_template_test_seek(S, n_stage, n_limit) = S -- if $instance_template_test_stage(S, n_stage)
def $instance_template_test_seek(S, n_stage, n_limit) = $instance_template_test_seek($instance_template_test_resume(S_next), n_stage, n_rest)
  -- if ~$instance_template_test_stage(S, n_stage)
  -- if $(n_limit > 0)
  -- if S.COMPLETION = NORMAL
  -- if ~S.COMPILESTOP
  -- if n_rest = $(n_limit - 1)
  -- if S_next = $drive_steps(S, 1)
'''
protocol.CHECKS = {'private-shadow-phase-order': [
 'S_queue = $instance_template_test_seek(S_initial[.COMPLETION = NORMAL], 0, 1800)',
 '$class_named(S_queue.CLASSNAMES, $ptascii("a")) = (porigin_a)',
 '$class_named(S_queue.CLASSNAMES, $ptascii("b")) = (porigin_b)',
 '$class_at(S_queue.CLASSES, porigin_a) = (pclassdesc_a)',
 '$class_at(S_queue.CLASSES, porigin_b) = (pclassdesc_b)',
 'pclassdesc_a.PROPERTIES = [ppropertydesc_ap, ppropertydesc_aq]',
 'pclassdesc_b.PROPERTIES = [ppropertydesc_bp, ppropertydesc_br]',
 'ppropertydesc_ap.ORIGIN = porigin_ap',
 'ppropertydesc_bp.ORIGIN = porigin_bp',
 'ppropertydesc_aq.ORIGIN = porigin_aq',
 'ppropertydesc_br.ORIGIN = porigin_br',
 'S_queue.TODO = (INSTANCE_DEFAULT_UPDATE porigin_a porigin_ap z) :: (STATIC_DEFAULT_UPDATE porigin_aq z) :: (CLASS_CONST_TABLE_UPDATE porigin_a z) :: (INSTANCE_DEFAULT_UPDATE porigin_b porigin_ap z) :: (INSTANCE_DEFAULT_UPDATE porigin_b porigin_bp z) :: (STATIC_DEFAULT_UPDATE porigin_br z) :: (CLASS_CONST_TABLE_UPDATE porigin_b z) :: ptask_queue_tail*',
 '$property_layout(S_queue, porigin_b, |S_queue.CLASSES|) = [ppropertydesc_ap, ppropertydesc_bp]',
 '$instance_default_order(S_queue, porigin_b, |S_queue.CLASSES|) = [(porigin_a, porigin_ap), (porigin_b, porigin_ap), (porigin_b, porigin_bp)]',
 '$instance_default_sequence(S_queue, porigin_b, [(porigin_a, porigin_ap), (porigin_b, porigin_ap), (porigin_b, porigin_bp)])',
 '~$instance_default_sequence(S_queue, porigin_b, [(porigin_a, porigin_ap), (porigin_b, porigin_bp)])',
 '~$instance_default_sequence(S_queue, porigin_b, [(porigin_b, porigin_ap), (porigin_a, porigin_ap), (porigin_b, porigin_bp)])',
 '$call_tasks_valid(S_queue, S_queue.TODO)',
 '$instance_default_state_valid(S_queue)',
 '$class_constant_state_valid(S_queue)',
 '$property_state_valid(S_queue)',
 '$instance_template_test_objects(S_queue, S_queue.ALLOCATIONS, porigin_a) = eps',
 '$instance_template_test_objects(S_queue, S_queue.ALLOCATIONS, porigin_b) = eps',
 '~$property_default_phases([STATIC_DEFAULT_UPDATE porigin_aq z, INSTANCE_DEFAULT_UPDATE porigin_a porigin_ap z], 0)',
 '~$property_default_phases([INSTANCE_DEFAULT_UPDATE porigin_a porigin_ap z, CLASS_CONST_UPDATE porigin_a z], 0)',
 'S_active = $instance_template_test_seek(S_queue, 4, 900)',
 'S_active.TODO = (INSTANCE_DEFAULT_BIND porigin_a pstaticdefaultcontext_a) :: ptask_active_tail*',
 'pstaticdefaultcontext_a.DECL = porigin_ap',
 '$instance_default_busy(S_active, porigin_a, porigin_ap)',
 '~$instance_default_busy(S_active, porigin_b, porigin_ap)',
 '$instance_default_unfinished(S_active, [(porigin_a, porigin_ap), (porigin_b, porigin_ap), (porigin_b, porigin_bp)]) = [(porigin_b, porigin_ap), (porigin_b, porigin_bp)]',
 '$instance_default_sequence(S_active, porigin_b, [(porigin_b, porigin_ap), (porigin_b, porigin_bp)])',
 '~$instance_default_sequence(S_active, porigin_b, [(porigin_b, porigin_bp)])',
 '$call_tasks_valid(S_active, S_active.TODO)',
 '$class_constant_state_valid(S_active)',
 'S = $instance_template_test_seek(S_active, 1, 1200)',
 'S.TODO = (INSTANCE_DEFAULT_BIND porigin_b pstaticdefaultcontext) :: ptask_tail*',
 'pstaticdefaultcontext.DECL = porigin_ap',
 'pstaticdefaultcontext.ROOT = porigin_b',
 '$static_default_scope(S) = (porigin_a)',
 '$instance_default_at(S.INSTANCEDEFAULTS, porigin_a, porigin_ap) = (pinstancetemplate_a)',
 'pinstancetemplate_a.STATE = INSTANCE_VALUE (PINT 2049) PVSCALAR',
 '$instance_default_pending(S, porigin_b, porigin_ap)',
 '$instance_default_filled_at(S, porigin_a, porigin_ap, S.CLASSCONSTANTHISTORY, |S.CLASSES|)',
 '~$instance_default_filled_at(S, porigin_b, porigin_ap, S.CLASSCONSTANTHISTORY, |S.CLASSES|)',
 '$instance_default_bind_valid(S, porigin_b, pstaticdefaultcontext)',
 '~$instance_default_bind_valid(S, porigin_a, pstaticdefaultcontext)',
 '~$instance_default_bind_valid(S, porigin_b, pstaticdefaultcontext[.DECL = porigin_bp])',
 '~$instance_default_bind_valid(S, porigin_b, pstaticdefaultcontext[.ROOT = porigin_a])',
 '~$instance_default_bind_valid(S, porigin_b, pstaticdefaultcontext[.LINE = $(pstaticdefaultcontext.LINE + 1)])',
 '$call_tasks_valid(S, S.TODO)',
 '$class_constant_state_valid(S)',
 '$instance_template_test_objects(S, S.ALLOCATIONS, porigin_b) = eps',
 'S_done = $drive_steps(S, 1800)',
 r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
 '$instance_template_test_fills(S_done.CLASSCONSTANTHISTORY) = [(porigin_a, porigin_ap), (porigin_b, porigin_ap), (porigin_b, porigin_bp)]',
 '$instance_default_at(S_done.INSTANCEDEFAULTS, porigin_b, porigin_ap) = (pinstancetemplate_ba)',
 '$instance_default_at(S_done.INSTANCEDEFAULTS, porigin_b, porigin_bp) = (pinstancetemplate_bb)',
 'pinstancetemplate_ba.STATE = INSTANCE_VALUE (PINT 2049) PVSCALAR',
 'pinstancetemplate_bb.STATE = INSTANCE_VALUE (PINT 2051) PVSCALAR',
 '$class_constant_table_done(S_done, porigin_a)',
 '$class_constant_table_done(S_done, porigin_b)',
 '$instance_default_state_valid(S_done)',
 '$class_constant_history_valid(S_done)',
 '$property_state_valid(S_done)',
 '$instance_template_test_output(S_done.EVENTS) = $ptascii("3:4:5:4:9:10:2048:2049:2051:2050:2052")'
], 'partial-parent-link-retry': [
 'S = $instance_template_test_seek(S_initial[.COMPLETION = NORMAL], 2, 2000)',
 '$class_named(S.CLASSNAMES, $ptascii("a")) = (porigin_a)',
 '$class_named(S.CLASSNAMES, $ptascii("b")) = (porigin_b)',
 '$class_at(S.CLASSES, porigin_a) = (pclassdesc)',
 'pclassdesc.PROPERTIES = [ppropertydesc_a, ppropertydesc_b, ppropertydesc_c]',
 'ppropertydesc_a.ORIGIN = porigin_da',
 'ppropertydesc_b.ORIGIN = porigin_db',
 'ppropertydesc_a.DEFAULT = PROP_DEFERRED porigin_ia',
 'ppropertydesc_b.DEFAULT = PROP_DEFERRED porigin_ib',
 '$instance_default_at(S.INSTANCEDEFAULTS, porigin_a, porigin_da) = (pinstancetemplate_aa)',
 '$instance_default_at(S.INSTANCEDEFAULTS, porigin_b, porigin_da) = (pinstancetemplate_ba)',
 'pinstancetemplate_aa.STATE = INSTANCE_VALUE (PARRAY n_shared) pvalueclass',
 'pinstancetemplate_ba.STATE = pinstancetemplate_aa.STATE',
 '$instance_default_at(S.INSTANCEDEFAULTS, porigin_a, porigin_db) = (pinstancetemplate_ab)',
 '$instance_default_at(S.INSTANCEDEFAULTS, porigin_b, porigin_db) = (pinstancetemplate_bb)',
 'pinstancetemplate_ab.STATE = INSTANCE_PENDING porigin_ib',
 'pinstancetemplate_bb.STATE = pinstancetemplate_ab.STATE',
 '$instance_default_link_prefix(S.CLASSCONSTANTHISTORY, porigin_b, eps) = (pclassconstantevent_before*)',
 '$instance_default_filled_at(S, porigin_a, porigin_da, pclassconstantevent_before*, |S.CLASSES|)',
 '$instance_default_filled_at(S, porigin_b, porigin_da, S.CLASSCONSTANTHISTORY, |S.CLASSES|)',
 '~$instance_default_fill_present(S.CLASSCONSTANTHISTORY, porigin_b, porigin_da)',
 '~$instance_default_filled_at(S, porigin_b, porigin_db, S.CLASSCONSTANTHISTORY, |S.CLASSES|)',
 '~$class_constant_table_done(S, porigin_a)',
 '~$class_constant_table_done(S, porigin_b)',
 '$instance_default_state_valid(S)',
 '$class_constant_history_valid(S)',
 '$instance_template_test_objects(S, S.ALLOCATIONS, porigin_a) = eps',
 '$instance_template_test_objects(S, S.ALLOCATIONS, porigin_b) = eps',
 'S_forged = S[.INSTANCEDEFAULTS = $instance_default_set(S.INSTANCEDEFAULTS, porigin_b, porigin_db, INSTANCE_VALUE (PINT 2057) PVSCALAR)]',
 '~$instance_default_state_valid(S_forged)',
 'S_missing = S[.INSTANCEDEFAULTS = $instance_default_set(S.INSTANCEDEFAULTS, porigin_b, porigin_da, INSTANCE_PENDING porigin_ia)]',
 '~$instance_default_state_valid(S_missing)',
 'S_done = $drive_steps(S, 1800)',
 r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
 '$instance_template_test_fills(S_done.CLASSCONSTANTHISTORY) = [(porigin_a, porigin_da), (porigin_a, porigin_db), (porigin_b, porigin_db)]',
 '$instance_default_at(S_done.INSTANCEDEFAULTS, porigin_b, porigin_da) = (pinstancetemplate_ba)',
 '$instance_default_at(S_done.INSTANCEDEFAULTS, porigin_a, porigin_db) = (pinstancetemplate_ab[.STATE = INSTANCE_VALUE (PINT 2057) PVSCALAR])',
 '$instance_default_at(S_done.INSTANCEDEFAULTS, porigin_b, porigin_db) = (pinstancetemplate_bb[.STATE = INSTANCE_VALUE (PINT 2057) PVSCALAR])',
 '$class_constant_table_done(S_done, porigin_a)',
 '$class_constant_table_done(S_done, porigin_b)',
 '$property_state_valid(S_done)',
 '$class_constant_history_valid(S_done)',
 '$instance_template_test_output(S_done.EVENTS) = $ptascii("3:4:F:4:12:4:2055:2057:2048")',
 'S_dead = $prune_allocations(S_done[.ENV = eps][.GLOBALTABLE = eps][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)])',
 '$instance_template_test_objects(S_dead, S_dead.ALLOCATIONS, porigin_a) = eps',
 '$instance_template_test_objects(S_dead, S_dead.ALLOCATIONS, porigin_b) = eps',
 '(HARRAY n_shared) <- S_dead.ALLOCATIONS',
 '$heap_owners($heap_graph(S_dead), HARRAY n_shared) = 2',
 'S_dead.CLASSCONSTANTHISTORY = S_done.CLASSCONSTANTHISTORY',
 '$property_state_valid(S_dead)',
 '$class_constant_history_valid(S_dead)'
], 'late-child-before-parent-replacement': [
 'S = $instance_template_test_seek(S_initial[.COMPLETION = NORMAL], 3, 2400)',
 '$class_named(S.CLASSNAMES, $ptascii("a")) = (porigin_a)',
 '$class_named(S.CLASSNAMES, $ptascii("b")) = (porigin_b)',
 'S.TODO = (INSTANCE_DEFAULT_BIND porigin_a pstaticdefaultcontext) :: ptask_tail*',
 'porigin_decl = pstaticdefaultcontext.DECL',
 '$instance_default_at(S.INSTANCEDEFAULTS, porigin_a, porigin_decl) = (pinstancetemplate_a)',
 '$instance_default_at(S.INSTANCEDEFAULTS, porigin_b, porigin_decl) = (pinstancetemplate_b)',
 'pinstancetemplate_a.STATE = INSTANCE_VALUE (PARRAY n_inner) pvalueclass_inner',
 'pinstancetemplate_b.STATE = pinstancetemplate_a.STATE',
 'S.RESULT = KNOWN (PARRAY n_outer)',
 'n_inner =/= n_outer',
 '$instance_default_link_prefix(S.CLASSCONSTANTHISTORY, porigin_b, eps) = (pclassconstantevent_before*)',
 '$instance_default_filled_at(S, porigin_a, porigin_decl, pclassconstantevent_before*, |S.CLASSES|)',
 '$instance_default_filled_at(S, porigin_b, porigin_decl, S.CLASSCONSTANTHISTORY, |S.CLASSES|)',
 '~$instance_default_fill_present(S.CLASSCONSTANTHISTORY, porigin_b, porigin_decl)',
 '$instance_template_test_fills(S.CLASSCONSTANTHISTORY) = [(porigin_a, porigin_decl)]',
 '$class_constant_table_done(S, porigin_a)',
 '$class_constant_table_done(S, porigin_b)',
 '$instance_default_bind_valid(S, porigin_a, pstaticdefaultcontext)',
 '$instance_default_record(S, porigin_a, pstaticdefaultcontext) = eps',
 '~$instance_default_bind_valid(S, porigin_b, pstaticdefaultcontext)',
 '~$instance_default_bind_valid(S, porigin_a, pstaticdefaultcontext[.DECL = porigin_a])',
 '~$instance_default_bind_valid(S, porigin_a, pstaticdefaultcontext[.ROOT = porigin_b])',
 '$call_tasks_valid(S, S.TODO)',
 '$class_constant_state_valid(S)',
 '$property_state_valid(S)',
 '(HARRAY n_inner) <- $instance_default_roots(S.INSTANCEDEFAULTS)',
 '(HARRAY n_outer) <- $machine_roots(S)',
 'S_bound = $instance_template_test_resume($drive_steps(S, 1))',
 '$instance_default_at(S_bound.INSTANCEDEFAULTS, porigin_a, porigin_decl) = (pinstancetemplate_a_new)',
 'pinstancetemplate_a_new.STATE = INSTANCE_VALUE (PARRAY n_outer) pvalueclass_outer',
 '$instance_default_at(S_bound.INSTANCEDEFAULTS, porigin_b, porigin_decl) = (pinstancetemplate_b)',
 'S_bound.CLASSCONSTANTHISTORY = S.CLASSCONSTANTHISTORY',
 '$instance_template_test_fills(S_bound.CLASSCONSTANTHISTORY) = [(porigin_a, porigin_decl)]',
 '$instance_default_state_valid(S_bound)',
 '$class_constant_history_valid(S_bound)',
 'S_done = $drive_steps(S_bound, 2000)',
 r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
 '$instance_template_test_output(S_done.EVENTS) = $ptascii("H:1:2:2048:2048")',
 '$instance_template_test_objects(S_done, S_done.ALLOCATIONS, porigin_a) = eps',
 '$instance_template_test_objects(S_done, S_done.ALLOCATIONS, porigin_b) = eps',
 'S_dead = $prune_allocations(S_done[.ENV = eps][.GLOBALTABLE = eps][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)])',
 '$instance_default_at(S_dead.INSTANCEDEFAULTS, porigin_a, porigin_decl) = (pinstancetemplate_a_new)',
 '$instance_default_at(S_dead.INSTANCEDEFAULTS, porigin_b, porigin_decl) = (pinstancetemplate_b)',
 '(HARRAY n_inner) <- S_dead.ALLOCATIONS',
 '(HARRAY n_outer) <- S_dead.ALLOCATIONS',
 '$heap_owners($heap_graph(S_dead), HARRAY n_inner) = 1',
 '$heap_owners($heap_graph(S_dead), HARRAY n_outer) = 1',
 '$instance_default_roots(S_dead.INSTANCEDEFAULTS) = [HARRAY n_outer, HARRAY n_inner]',
 'S_dead.CLASSCONSTANTHISTORY = S_bound.CLASSCONSTANTHISTORY',
 '$property_state_valid(S_dead)',
 '$class_constant_history_valid(S_dead)'
]}

if __name__ == '__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--prepare');args=parser.parse_args()
 if args.prepare:protocol.prepare(Path(args.prepare));print(args.prepare)
 else:protocol.run(Path(tempfile.mkdtemp(prefix='instance-default-template-',dir=protocol.ROOT/'.tools'))/'run')
