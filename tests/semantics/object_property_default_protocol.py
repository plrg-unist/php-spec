#!/usr/bin/env python3
"""Check object-bearing property template identity, copy snapshots and cleanup."""
import argparse,tempfile
from pathlib import Path
import deferred_static_default_protocol as protocol

protocol.SOURCES = {'instance-closure-cold-late': '<?php\n'
                               'class A {\n'
                               '    private const X = 7;\n'
                               '    public Closure $f = static function () {\n'
                               '        static $n = 0;\n'
                               '        return self::X + $n++;\n'
                               '    };\n'
                               '}\n'
                               'class B extends A {}\n'
                               '$a = new A;\n'
                               '$a2 = new A;\n'
                               '$b = new B;\n'
                               'if (true) { class C extends A {} }\n'
                               '$c = new C;\n'
                               '$copy = clone $a;\n'
                               "echo (int) ($a->f === $a2->f), ':', (int) ($a->f === "
                               "$b->f), ':', (int) ($a->f === $c->f), ':', (int) ($a->f "
                               "=== $copy->f), ':';\n"
                               "echo ($a->f)(), ':', ($a2->f)(), ':', ($b->f)(), ':', "
                               "($c->f)(), ':';\n"
                               '$kept = $copy->f;\n'
                               'unset($a, $a2, $b, $c, $copy);\n'
                               'echo $kept();\n',
 'instance-closure-late-reentry': '<?php\n'
                                  'class A {\n'
                                  '    public Closure $f = [static function () { static $n '
                                  '= 0; return ++$n; }, E_STRICT][0];\n'
                                  '}\n'
                                  '$slots = [];\n'
                                  'set_error_handler(static function ($level) use '
                                  '(&$slots) {\n'
                                  "    echo 'H:';\n"
                                  '    error_reporting(0);\n'
                                  '    $inner = new A;\n'
                                  '    if (true) { class B extends A {} }\n'
                                  "    $slots['inner'] = $inner;\n"
                                  "    $slots['child'] = new B;\n"
                                  '    error_reporting(30719);\n'
                                  '    return true;\n'
                                  '});\n'
                                  '$a = new A;\n'
                                  '$freshA = new A;\n'
                                  '$freshB = new B;\n'
                                  "echo (int) ($a->f === $slots['inner']->f), ':', (int) "
                                  "($a->f === $freshA->f), ':', (int) ($slots['child']->f "
                                  "=== $freshB->f), ':';\n"
                                  "echo ($slots['inner']->f)(), ':', "
                                  "($slots['child']->f)(), ':', ($a->f)(), ':', "
                                  '($freshB->f)();\n'
                                  'unset($a, $freshA, $freshB, $slots);\n',
 'static-closure-throw-retain': '<?php\n'
                                'class A {\n'
                                '    public static Closure $f = [static function () { '
                                'return 7; }, E_STRICT][0];\n'
                                '}\n'
                                '$slots = [];\n'
                                'set_error_handler(static function ($level) use (&$slots) '
                                '{\n'
                                "    echo 'H:';\n"
                                '    error_reporting(0);\n'
                                "    $slots['r'] =& A::$f;\n"
                                '    error_reporting(30719);\n'
                                "    throw new Exception('stop');\n"
                                '});\n'
                                'try { $f = A::$f; }\n'
                                "catch (Exception $e) { echo 'T:'; }\n"
                                '$warm = A::$f;\n'
                                "echo (int) ($warm === $slots['r']), ':', ($slots['r'])(), "
                                "':', $warm();\n",
 'partial-closure-fcc-retry': '<?php\n'
                              'class A {\n'
                              '    public Closure $f = static function () { static $n = 0; '
                              'return ++$n; };\n'
                              '    public Closure $g = late(...);\n'
                              '}\n'
                              'try { $failed = new A; }\n'
                              "catch (Error $e) { echo 'F:'; }\n"
                              'if (true) { function late() { return 7; } }\n'
                              '$a = new A;\n'
                              '$b = new A;\n'
                              "echo (int) ($a->f === $b->f), ':', ($a->f)(), ':', "
                              "($b->f)(), ':', ($a->g)();\n"}

protocol.PREFIX = r'''
dec $object_default_test_resume(pstate) : pstate
def $object_default_test_resume(S) = S[.COMPLETION = NORMAL] -- if S.COMPLETION = BUDGET
def $object_default_test_resume(S) = S -- otherwise
dec $object_default_test_output(pevent*) : ptbytes
def $object_default_test_output(eps) = eps
def $object_default_test_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $object_default_test_output(pevent*)
dec $object_default_test_receipts(pconstantclosure*, porigin) : pconstantclosure*
def $object_default_test_receipts(eps, porigin) = eps
def $object_default_test_receipts(pconstantclosure :: pconstantclosure_tail*, porigin) = pconstantclosure :: $object_default_test_receipts(pconstantclosure_tail*, porigin)
  -- if pconstantclosure.DECL = porigin
def $object_default_test_receipts(pconstantclosure :: pconstantclosure_tail*, porigin) = $object_default_test_receipts(pconstantclosure_tail*, porigin)
  -- if pconstantclosure.DECL =/= porigin
dec $object_default_test_stage(pstate, nat) : bool
def $object_default_test_stage(S, 0) = true
  -- if $instance_default_context_at(S.TODO) = (porigin_b)
  -- if $class_named(S.CLASSNAMES, $ptascii("b")) = (porigin_b)
  -- if $static_default_context_at(S.TODO) = (pstaticdefaultcontext)
  -- if S.TODO = (EVAL expression) :: ptask_tail*
  -- if S.ORIGIN = (porigin_site)
  -- if $constant_callable_context(S, porigin_site) = ((pstaticdefaultcontext.DECL, porigin_a))
  -- if porigin_a =/= porigin_b
def $object_default_test_stage(S, 1) = true
  -- if $class_named(S.CLASSNAMES, $ptascii("a")) = (porigin_a)
  -- if $class_named(S.CLASSNAMES, $ptascii("b")) = (porigin_b)
  -- if S.TODO = (INSTANCE_DEFAULT_BIND porigin_a pstaticdefaultcontext) :: ptask_tail*
  -- if $instance_default_at(S.INSTANCEDEFAULTS, porigin_a, pstaticdefaultcontext.DECL) = (pinstancetemplate)
  -- if pinstancetemplate.STATE = INSTANCE_OBJECT_VALUE (POBJECT n_inner) pvalueclass pinstanceobjectcertificate
  -- if S.RESULT = KNOWN (POBJECT n_outer)
  -- if n_inner =/= n_outer
def $object_default_test_stage(S, 2) = true
  -- if $static_default_context_at(S.TODO) = (pstaticdefaultcontext)
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = DEPRECATED_CONSTANT_RESULT pdeprecatedconstant
  -- if S.ORIGIN = (pdeprecatedconstant.SITE)
  -- if $origin_node(S.SOURCES, pdeprecatedconstant.SITE) = (NExprConstFetch (NName (BYTES text) metadata_name) metadata)
  -- if $ptlc($base64(text)) = $ptascii("e_strict")
  -- if $class_static_at(S.CLASSSTATICS, pstaticdefaultcontext.DECL) = (pclassstatic)
  -- if $static_default_pending(pclassstatic.STATE)
  -- if $object_default_test_receipts(S.CONSTANTCLOSURES, pstaticdefaultcontext.DECL) = [pconstantclosure]
def $object_default_test_stage(S, 3) = true
  -- if $class_named(S.CLASSNAMES, $ptascii("a")) = (porigin_a)
  -- if $class_at(S.CLASSES, porigin_a) = (pclassdesc)
  -- if pclassdesc.PROPERTIES = [ppropertydesc_f, ppropertydesc_g]
  -- if ppropertydesc_g.ORIGIN = porigin_g
  -- if $instance_default_context_at(S.TODO) = (porigin_a)
  -- if $static_default_context_at(S.TODO) = (pstaticdefaultcontext)
  -- if pstaticdefaultcontext.DECL = porigin_g
  -- if S.TODO = (EVAL (NExprFuncCall phpType19 phpType6 metadata)) :: ptask_tail*
  -- if S.ORIGIN = (porigin_site)
  -- if $constant_callable_context(S, porigin_site) = ((porigin_g, porigin_a))
  -- if $constant_callable_function(S, porigin_site, |S.DECLARATIONS|) = eps
def $object_default_test_stage(S, 4) = true
  -- if $object_default_test_output(S.EVENTS) = $ptascii("F:")
  -- if S.CONSTCONTEXT = eps
  -- if $class_named(S.CLASSNAMES, $ptascii("a")) = (porigin_a)
  -- if $class_at(S.CLASSES, porigin_a) = (pclassdesc)
  -- if pclassdesc.PROPERTIES = [ppropertydesc_f, ppropertydesc_g]
  -- if ppropertydesc_g.ORIGIN = porigin_g
  -- if $instance_default_pending(S, porigin_a, porigin_g)
def $object_default_test_stage(S, n) = false -- otherwise
dec $object_default_test_seek(pstate, nat, nat) : pstate
def $object_default_test_seek(S, n_stage, n_limit) = S -- if $object_default_test_stage(S, n_stage)
def $object_default_test_seek(S, n_stage, n_limit) = $object_default_test_seek($object_default_test_resume(S_next), n_stage, n_rest)
  -- if ~$object_default_test_stage(S, n_stage)
  -- if $(n_limit > 0)
  -- if S.COMPLETION = NORMAL
  -- if ~S.COMPILESTOP
  -- if n_rest = $(n_limit - 1)
  -- if S_next = $drive_steps(S, 1)
'''

protocol.CHECKS = {'instance-closure-cold-late': ['S = $object_default_test_seek(S_initial[.COMPLETION = NORMAL], 0, '
                                '2500)',
                                '$class_named(S.CLASSNAMES, $ptascii("a")) = (porigin_a)',
                                '$class_named(S.CLASSNAMES, $ptascii("b")) = (porigin_b)',
                                '$class_at(S.CLASSES, porigin_a) = (pclassdesc_a)',
                                '$class_at(S.CLASSES, porigin_b) = (pclassdesc_b)',
                                'pclassdesc_a.PROPERTIES = [ppropertydesc]',
                                'ppropertydesc.ORIGIN = porigin_decl',
                                'ppropertydesc.DEFAULT = PROP_DEFERRED porigin_initializer',
                                'pclassdesc_b.PROPERTIES = eps',
                                'S.ORIGIN = (porigin_site)',
                                '$static_default_context_at(S.TODO) = (pstaticdefaultcontext)',
                                'pstaticdefaultcontext.DECL = porigin_decl',
                                'pstaticdefaultcontext.ROOT = porigin_b',
                                '$instance_default_context_at(S.TODO) = (porigin_b)',
                                '$static_default_scope(S) = (porigin_a)',
                                '$constant_callable_context(S, porigin_site) = ((porigin_decl, '
                                'porigin_a))',
                                '$property_callable_context_valid(S, ppropertydesc, '
                                'pstaticdefaultcontext)',
                                '~$property_callable_context_valid(S, ppropertydesc, '
                                'pstaticdefaultcontext[.ROOT = porigin_a])',
                                '$constant_callable_context(S[.CONSTCONTEXT = eps], porigin_site) = '
                                'eps',
                                '$constant_callable_context(S[.CONSTCONTEXT = ({ORIGIN porigin_b, LINE '
                                'pstaticdefaultcontext.LINE, FACTS eps})], porigin_site) = eps',
                                '$call_tasks_valid(S, S.TODO)',
                                '$class_constant_state_valid(S)',
                                'S_done = $drive_steps(S, 6000)',
                                'S_done.COMPLETION = NORMAL',
                                'S_done.TODO = eps',
                                '$object_default_test_output(S_done.EVENTS) = '
                                '$ptascii("1:0:1:1:7:8:7:9:10")',
                                '$class_named(S_done.CLASSNAMES, $ptascii("c")) = (porigin_c)',
                                '$instance_default_at(S_done.INSTANCEDEFAULTS, porigin_a, '
                                'porigin_decl) = (pinstancetemplate_a)',
                                '$instance_default_at(S_done.INSTANCEDEFAULTS, porigin_b, '
                                'porigin_decl) = (pinstancetemplate_b)',
                                '$instance_default_at(S_done.INSTANCEDEFAULTS, porigin_c, '
                                'porigin_decl) = (pinstancetemplate_c)',
                                'pinstancetemplate_a.STATE = INSTANCE_OBJECT_VALUE (POBJECT n_a) '
                                'pvalueclass_a pinstanceobjectcertificate_a',
                                'pinstancetemplate_b.STATE = INSTANCE_OBJECT_VALUE (POBJECT n_b) '
                                'pvalueclass_b pinstanceobjectcertificate_b',
                                'pinstancetemplate_c.STATE = INSTANCE_OBJECT_VALUE (POBJECT n_a) '
                                'pvalueclass_a pinstanceobjectcertificate_c',
                                'n_a =/= n_b',
                                'pvalueclass_a = PVCLOSURE n_a porigin_site',
                                'pvalueclass_b = PVCLOSURE n_b porigin_site',
                                '$instance_object_certificate_valid(S_done, '
                                'pinstanceobjectcertificate_a, porigin_a, porigin_decl, pvalueclass_a)',
                                '$instance_object_certificate_valid(S_done, '
                                'pinstanceobjectcertificate_b, porigin_b, porigin_decl, pvalueclass_b)',
                                '$instance_object_certificate_valid(S_done, '
                                'pinstanceobjectcertificate_c, porigin_c, porigin_decl, pvalueclass_a)',
                                '~$instance_object_certificate_valid(S_done, '
                                'pinstanceobjectcertificate_a, porigin_a, porigin_b, pvalueclass_a)',
                                '~$instance_object_certificate_valid(S_done, '
                                'pinstanceobjectcertificate_a, porigin_b, porigin_decl, pvalueclass_a)',
                                '~$instance_object_certificate_valid(S_done, '
                                'pinstanceobjectcertificate_a, porigin_a, porigin_decl, pvalueclass_b)',
                                '~$instance_default_state_valid(S_done[.INSTANCEDEFAULTS = '
                                '$instance_default_set(S_done.INSTANCEDEFAULTS, porigin_a, '
                                'porigin_decl, INSTANCE_OBJECT_VALUE (POBJECT n_b) pvalueclass_b '
                                'pinstanceobjectcertificate_a)])',
                                '~$instance_default_state_valid(S_done[.INSTANCEDEFAULTS = '
                                '$instance_default_set(S_done.INSTANCEDEFAULTS, porigin_a, '
                                'porigin_decl, pinstancetemplate_b.STATE)])',
                                '~$instance_default_state_valid(S_done[.INSTANCEDEFAULTS = '
                                '$instance_default_set(S_done.INSTANCEDEFAULTS, porigin_a, '
                                'porigin_decl, INSTANCE_VALUE (POBJECT n_a) pvalueclass_a)])',
                                '$instance_default_link_prefix(S_done.CLASSCONSTANTHISTORY, porigin_b, '
                                'eps) = (pclassconstantevent_before_b*)',
                                'S_done.CLASSCONSTANTHISTORY[|pclassconstantevent_before_b*|] = CCLINK '
                                'porigin_b n_link_b',
                                '~$instance_object_certificate_valid(S_done, INSTANCE_OBJECT_COPY '
                                'porigin_b n_link_b pinstanceobjectcertificate_a, porigin_b, '
                                'porigin_decl, pvalueclass_a)',
                                '$constant_callable_records_valid(S_done, S_done.CONSTANTCLOSURES)',
                                '$instance_default_state_valid(S_done)',
                                '$property_state_valid(S_done)',
                                'S_clone = $clone_object(S_done, n_a)',
                                'S_clone.RESULT = KNOWN (POBJECT n_clone)',
                                '$constant_callable_record(S_clone.CONSTANTCLOSURES, n_clone) = eps',
                                'S_clone.OBJECTS[n_clone] = REALCLOSURE porigin_site pitem_clone* '
                                'pstaticcell_clone*',
                                '$closure_scope_at(S_clone.CLOSURESCOPES, n_clone) = '
                                '(pclosurescope_clone)',
                                'pclosurescope_clone.LEXICAL = porigin_a',
                                'pclosurescope_clone.CALLED = porigin_a',
                                '$closure_scope_row_valid(S_clone, pclosurescope_clone)',
                                '~$closure_scope_row_valid(S_clone, pclosurescope_clone[.LEXICAL = '
                                'porigin_b][.CALLED = porigin_b])',
                                'S_dead = $prune_allocations(S_clone[.ENV = eps][.GLOBALTABLE = '
                                'eps][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)])',
                                '~((HOBJECT n_clone) <- S_dead.ALLOCATIONS)',
                                '(HOBJECT n_a) <- S_dead.ALLOCATIONS',
                                '(HOBJECT n_b) <- S_dead.ALLOCATIONS',
                                '$instance_default_roots(S_dead.INSTANCEDEFAULTS) = [HOBJECT n_a, '
                                'HOBJECT n_b, HOBJECT n_a]',
                                '$heap_owners($heap_graph(S_dead), HOBJECT n_a) = 2',
                                '$heap_owners($heap_graph(S_dead), HOBJECT n_b) = 1',
                                'S_dead.CONSTANTCLOSURES = S_done.CONSTANTCLOSURES',
                                '$constant_callable_records_valid(S_dead, S_dead.CONSTANTCLOSURES)',
                                '$instance_default_state_valid(S_dead)',
                                '$class_constant_history_valid(S_dead)',
                                '$property_state_valid(S_dead)'],
 'instance-closure-late-reentry': ['S = $object_default_test_seek(S_initial[.COMPLETION = NORMAL], 1, '
                                   '5000)',
                                   '$class_named(S.CLASSNAMES, $ptascii("a")) = (porigin_a)',
                                   '$class_named(S.CLASSNAMES, $ptascii("b")) = (porigin_b)',
                                   'S.TODO = (INSTANCE_DEFAULT_BIND porigin_a pstaticdefaultcontext) '
                                   ':: ptask_tail*',
                                   'porigin_decl = pstaticdefaultcontext.DECL',
                                   '$property_default_active_desc(S, porigin_decl) = (ppropertydesc)',
                                   'ppropertydesc.DEFAULT = PROP_DEFERRED porigin_initializer',
                                   '$instance_default_at(S.INSTANCEDEFAULTS, porigin_a, porigin_decl) '
                                   '= (pinstancetemplate_a)',
                                   '$instance_default_at(S.INSTANCEDEFAULTS, porigin_b, porigin_decl) '
                                   '= (pinstancetemplate_b)',
                                   'pinstancetemplate_a.STATE = INSTANCE_OBJECT_VALUE (POBJECT '
                                   'n_inner) pvalueclass_inner pinstanceobjectcertificate_inner',
                                   'pinstancetemplate_b.STATE = INSTANCE_OBJECT_VALUE (POBJECT '
                                   'n_inner) pvalueclass_inner pinstanceobjectcertificate_child',
                                   'S.RESULT = KNOWN (POBJECT n_outer)',
                                   'n_inner =/= n_outer',
                                   'pvalueclass_inner = PVCLOSURE n_inner porigin_site',
                                   '$constant_callable_record(S.CONSTANTCLOSURES, n_outer) = '
                                   '(pconstantclosure_outer)',
                                   'pconstantclosure_outer.DECL = porigin_decl',
                                   'pconstantclosure_outer.SITE = porigin_site',
                                   '$property_callable_projection(S, porigin_initializer) = '
                                   '(porigin_site)',
                                   '$property_default_transfer_valid(S, ppropertydesc, PVCLOSURE '
                                   'n_outer porigin_site)',
                                   '~$property_default_transfer_valid(S, ppropertydesc, PVCLOSURE '
                                   'n_outer porigin_initializer)',
                                   '$instance_default_link_prefix(S.CLASSCONSTANTHISTORY, porigin_b, '
                                   'eps) = (pclassconstantevent_before*)',
                                   'S.CLASSCONSTANTHISTORY[|pclassconstantevent_before*|] = CCLINK '
                                   'porigin_b n_link',
                                   'pinstanceobjectcertificate_child = INSTANCE_OBJECT_COPY porigin_b '
                                   'n_link pinstanceobjectcertificate_inner',
                                   '$instance_object_certificate_valid(S, '
                                   'pinstanceobjectcertificate_inner, porigin_a, porigin_decl, '
                                   'pvalueclass_inner)',
                                   '$instance_object_certificate_valid(S, '
                                   'pinstanceobjectcertificate_child, porigin_b, porigin_decl, '
                                   'pvalueclass_inner)',
                                   '~$instance_object_certificate_valid(S, INSTANCE_OBJECT_COPY '
                                   'porigin_b $(n_link + 1) pinstanceobjectcertificate_inner, '
                                   'porigin_b, porigin_decl, pvalueclass_inner)',
                                   '~$instance_object_certificate_valid(S, INSTANCE_OBJECT_COPY '
                                   'porigin_a n_link pinstanceobjectcertificate_inner, porigin_b, '
                                   'porigin_decl, pvalueclass_inner)',
                                   '~$instance_default_fill_present(S.CLASSCONSTANTHISTORY, porigin_b, '
                                   'porigin_decl)',
                                   '$instance_default_record(S, porigin_a, pstaticdefaultcontext) = '
                                   'eps',
                                   '$instance_default_bind_valid(S, porigin_a, pstaticdefaultcontext)',
                                   '$instance_default_state_valid(S)',
                                   '$call_tasks_valid(S, S.TODO)',
                                   '$class_constant_state_valid(S)',
                                   '$constant_callable_records_valid(S, S.CONSTANTCLOSURES)',
                                   'S_bound = $object_default_test_resume($drive_steps(S, 1))',
                                   '$instance_default_at(S_bound.INSTANCEDEFAULTS, porigin_a, '
                                   'porigin_decl) = (pinstancetemplate_outer)',
                                   'pinstancetemplate_outer.STATE = INSTANCE_OBJECT_VALUE (POBJECT '
                                   'n_outer) pvalueclass_outer pinstanceobjectcertificate_outer',
                                   'pvalueclass_outer = PVCLOSURE n_outer porigin_site',
                                   '$instance_default_at(S_bound.INSTANCEDEFAULTS, porigin_b, '
                                   'porigin_decl) = (pinstancetemplate_b)',
                                   'S_bound.CLASSCONSTANTHISTORY = S.CLASSCONSTANTHISTORY',
                                   '$instance_object_certificate_valid(S_bound, '
                                   'pinstanceobjectcertificate_outer, porigin_a, porigin_decl, '
                                   'pvalueclass_outer)',
                                   '$instance_object_certificate_valid(S_bound, '
                                   'pinstanceobjectcertificate_child, porigin_b, porigin_decl, '
                                   'pvalueclass_inner)',
                                   '~$instance_object_certificate_valid(S_bound, INSTANCE_OBJECT_COPY '
                                   'porigin_b n_link pinstanceobjectcertificate_outer, porigin_b, '
                                   'porigin_decl, pvalueclass_outer)',
                                   '~$instance_default_state_valid(S_bound[.INSTANCEDEFAULTS = '
                                   '$instance_default_set(S_bound.INSTANCEDEFAULTS, porigin_b, '
                                   'porigin_decl, INSTANCE_OBJECT_VALUE (POBJECT n_outer) '
                                   'pvalueclass_outer pinstanceobjectcertificate_child)])',
                                   '$instance_default_state_valid(S_bound)',
                                   '$constant_callable_records_valid(S_bound, '
                                   'S_bound.CONSTANTCLOSURES)',
                                   'S_done = $drive_steps(S_bound, 4000)',
                                   'S_done.COMPLETION = NORMAL',
                                   'S_done.TODO = eps',
                                   '$object_default_test_output(S_done.EVENTS) = '
                                   '$ptascii("H:0:1:1:1:2:1:3")',
                                   'S_dead = $prune_allocations(S_done[.ENV = eps][.GLOBALTABLE = '
                                   'eps][.ERRORHANDLER.CALLBACK = eps][.ERRORHANDLERS = eps][.RESULT = '
                                   'KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)])',
                                   '$instance_default_roots(S_dead.INSTANCEDEFAULTS) = [HOBJECT '
                                   'n_outer, HOBJECT n_inner]',
                                   '$heap_owners($heap_graph(S_dead), HOBJECT n_outer) = 1',
                                   '$heap_owners($heap_graph(S_dead), HOBJECT n_inner) = 1',
                                   'S_dead.CONSTANTCLOSURES = S_done.CONSTANTCLOSURES',
                                   '$constant_callable_records_valid(S_dead, S_dead.CONSTANTCLOSURES)',
                                   '$instance_object_certificate_valid(S_dead, '
                                   'pinstanceobjectcertificate_child, porigin_b, porigin_decl, '
                                   'pvalueclass_inner)',
                                   '$instance_default_state_valid(S_dead)',
                                   '$class_constant_history_valid(S_dead)',
                                   '$property_state_valid(S_dead)'],
 'static-closure-throw-retain': ['S = $object_default_test_seek(S_initial[.COMPLETION = NORMAL], 2, '
                                 '2200)',
                                 '$class_named(S.CLASSNAMES, $ptascii("a")) = (porigin_a)',
                                 '$class_at(S.CLASSES, porigin_a) = (pclassdesc)',
                                 'pclassdesc.PROPERTIES = [ppropertydesc]',
                                 'ppropertydesc.ORIGIN = porigin_decl',
                                 'ppropertydesc.DEFAULT = PROP_DEFERRED porigin_initializer',
                                 '$object_default_test_receipts(S.CONSTANTCLOSURES, porigin_decl) = '
                                 '[pconstantclosure_outer]',
                                 'n_outer = pconstantclosure_outer.OBJECT',
                                 'porigin_site = pconstantclosure_outer.SITE',
                                 '$static_default_context_at(S.TODO) = (pstaticdefaultcontext)',
                                 'pstaticdefaultcontext.DECL = porigin_decl',
                                 '$static_default_scope(S) = (porigin_a)',
                                 '$constant_callable_record_valid(S, pconstantclosure_outer)',
                                 '~$constant_callable_record_valid(S, pconstantclosure_outer[.DECL = '
                                 'porigin_a])',
                                 '~$constant_callable_record_valid(S, pconstantclosure_outer[.SITE = '
                                 'porigin_initializer])',
                                 '~$constant_callable_record_valid(S, pconstantclosure_outer[.PREFIX = '
                                 '0])',
                                 '$constant_callable_value_valid(S, n_outer, porigin_site)',
                                 '$property_callable_projection(S, porigin_initializer) = '
                                 '(porigin_site)',
                                 '$constant_callable_flow(S, porigin_initializer, porigin_a, PVCLOSURE '
                                 'n_outer porigin_site, |S.DECLARATIONS|, eps)',
                                 '$call_tasks_valid(S, S.TODO)',
                                 '$class_constant_state_valid(S)',
                                 'S_done = $drive_steps(S, 5000)',
                                 'S_done.COMPLETION = NORMAL',
                                 'S_done.TODO = eps',
                                 '$object_default_test_output(S_done.EVENTS) = $ptascii("H:T:1:7:7")',
                                 '$class_static_at(S_done.CLASSSTATICS, porigin_decl) = (pclassstatic)',
                                 'pclassstatic.STATE = PROP_VALUE (ALIAS n_cell)',
                                 'S_done.STORE[n_cell] = DEFINED (POBJECT n_inner)',
                                 'n_inner =/= n_outer',
                                 '$object_default_test_receipts(S_done.CONSTANTCLOSURES, porigin_decl) '
                                 '= [pconstantclosure_outer, pconstantclosure_inner]',
                                 'pconstantclosure_inner.OBJECT = n_inner',
                                 'pconstantclosure_inner.SITE = porigin_site',
                                 'S_done.INSTANCEDEFAULTS = eps',
                                 '~((HOBJECT n_outer) <- S_done.ALLOCATIONS)',
                                 '$constant_callable_identity_valid(S_done, n_outer, porigin_site)',
                                 '~$constant_callable_value_valid(S_done, n_outer, porigin_site)',
                                 '$constant_callable_record_valid(S_done, pconstantclosure_outer)',
                                 '$constant_callable_records_valid(S_done, S_done.CONSTANTCLOSURES)',
                                 '$propref_source_valid(S_done, n_cell, CLASS_PROP_SOURCE '
                                 'porigin_decl)',
                                 '$static_default_fills(S_done.CLASSCONSTANTHISTORY) = [porigin_decl]',
                                 '$class_constant_table_done(S_done, porigin_a)',
                                 '$class_statics_valid(S_done)',
                                 '$proprefs_valid(S_done)',
                                 'S_dead = $prune_allocations(S_done[.ENV = eps][.GLOBALTABLE = '
                                 'eps][.ERRORHANDLER.CALLBACK = eps][.ERRORHANDLERS = eps][.RESULT = '
                                 'KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)])',
                                 '~((HOBJECT n_outer) <- S_dead.ALLOCATIONS)',
                                 '(HOBJECT n_inner) <- S_dead.ALLOCATIONS',
                                 '(HCELL n_cell) <- S_dead.ALLOCATIONS',
                                 '$heap_owners($heap_graph(S_dead), HOBJECT n_inner) = 1',
                                 'S_dead.CONSTANTCLOSURES = S_done.CONSTANTCLOSURES',
                                 '$constant_callable_records_valid(S_dead, S_dead.CONSTANTCLOSURES)',
                                 '$constant_callable_flow(S_dead, porigin_initializer, porigin_a, '
                                 'PVCLOSURE n_outer porigin_site, |S_dead.DECLARATIONS|, eps)',
                                 '~$constant_value_class_valid(S_dead, POBJECT n_outer, PVCLOSURE '
                                 'n_outer porigin_site)',
                                 '$class_statics_valid(S_dead)',
                                 '$proprefs_valid(S_dead)',
                                 '$property_state_valid(S_dead)',
                                 '$class_constant_history_valid(S_dead)'],
 'partial-closure-fcc-retry': ['S = $object_default_test_seek(S_initial[.COMPLETION = NORMAL], 3, '
                               '2000)',
                               '$class_named(S.CLASSNAMES, $ptascii("a")) = (porigin_a)',
                               '$class_at(S.CLASSES, porigin_a) = (pclassdesc)',
                               'pclassdesc.PROPERTIES = [ppropertydesc_f, ppropertydesc_g]',
                               'ppropertydesc_f.ORIGIN = porigin_f',
                               'ppropertydesc_g.ORIGIN = porigin_g',
                               '$instance_default_at(S.INSTANCEDEFAULTS, porigin_a, porigin_f) = '
                               '(pinstancetemplate_f)',
                               'pinstancetemplate_f.STATE = INSTANCE_OBJECT_VALUE (POBJECT n_f) '
                               'pvalueclass_f pinstanceobjectcertificate_f',
                               '$instance_default_pending(S, porigin_a, porigin_g)',
                               '$object_default_test_receipts(S.CONSTANTCLOSURES, porigin_f) = '
                               '[pconstantclosure_f]',
                               '$object_default_test_receipts(S.CONSTANTCLOSURES, porigin_g) = eps',
                               'pconstantclosure_f.OBJECT = n_f',
                               '$instance_object_certificate_valid(S, pinstanceobjectcertificate_f, '
                               'porigin_a, porigin_f, pvalueclass_f)',
                               '$call_tasks_valid(S, S.TODO)',
                               '$class_constant_state_valid(S)',
                               'S_failed = $object_default_test_seek(S, 4, 1600)',
                               '$instance_default_at(S_failed.INSTANCEDEFAULTS, porigin_a, porigin_f) '
                               '= (pinstancetemplate_f)',
                               '$instance_default_pending(S_failed, porigin_a, porigin_g)',
                               '$object_default_test_receipts(S_failed.CONSTANTCLOSURES, porigin_g) = '
                               'eps',
                               '~$class_constant_table_done(S_failed, porigin_a)',
                               '$heap_owners($heap_graph(S_failed), HOBJECT n_f) = 1',
                               '$instance_default_state_valid(S_failed)',
                               '$constant_callable_records_valid(S_failed, S_failed.CONSTANTCLOSURES)',
                               'S_done = $drive_steps(S_failed, 3500)',
                               'S_done.COMPLETION = NORMAL',
                               'S_done.TODO = eps',
                               '$object_default_test_output(S_done.EVENTS) = $ptascii("F:1:1:2:7")',
                               '$instance_default_at(S_done.INSTANCEDEFAULTS, porigin_a, porigin_f) = '
                               '(pinstancetemplate_f)',
                               '$instance_default_at(S_done.INSTANCEDEFAULTS, porigin_a, porigin_g) = '
                               '(pinstancetemplate_g)',
                               'pinstancetemplate_g.STATE = INSTANCE_OBJECT_VALUE (POBJECT n_g) '
                               'pvalueclass_g pinstanceobjectcertificate_g',
                               '$object_default_test_receipts(S_done.CONSTANTCLOSURES, porigin_f) = '
                               '[pconstantclosure_f]',
                               '$object_default_test_receipts(S_done.CONSTANTCLOSURES, porigin_g) = '
                               '[pconstantclosure_g]',
                               'pconstantclosure_g.OBJECT = n_g',
                               '$(pconstantclosure_f.PREFIX < pconstantclosure_g.PREFIX)',
                               '$instance_object_certificate_valid(S_done, '
                               'pinstanceobjectcertificate_f, porigin_a, porigin_f, pvalueclass_f)',
                               '$instance_object_certificate_valid(S_done, '
                               'pinstanceobjectcertificate_g, porigin_a, porigin_g, pvalueclass_g)',
                               '~$property_default_transfer_valid(S_done, ppropertydesc_f, '
                               'pvalueclass_g)',
                               '~$constant_callable_record_valid(S_done, pconstantclosure_f[.DECL = '
                               'porigin_g])',
                               '~$instance_default_state_valid(S_done[.INSTANCEDEFAULTS = '
                               '$instance_default_set(S_done.INSTANCEDEFAULTS, porigin_a, porigin_f, '
                               'pinstancetemplate_g.STATE)])',
                               'S_done.CLASSCONSTANTHISTORY = [CCLINK porigin_a n_link, CCINSTANCE '
                               'porigin_a porigin_f porigin_a porigin_first eps n_first, CCINSTANCE '
                               'porigin_a porigin_g porigin_a porigin_retry eps n_retry, CCUPDATE '
                               'porigin_a porigin_a porigin_retry n_done]',
                               '$class_constant_table_done(S_done, porigin_a)',
                               '$instance_default_state_valid(S_done)',
                               '$constant_callable_records_valid(S_done, S_done.CONSTANTCLOSURES)',
                               '$class_constant_history_valid(S_done)',
                               '$property_state_valid(S_done)']}

protocol.SOURCES['nested-class-property-closures'] = (
 '<?php\n'
 '$make = static function () {\n'
 '    class C {\n'
 '        private const X = 3;\n'
 "        public Closure $f = static function () { return self::X . ':' . get_called_class(); };\n"
 '        public static Closure $g = static function () { return self::X + 1; };\n'
 '    }\n'
 '};\n'
 '$make();\n'
 'unset($make);\n'
 '$c = new C;\n'
 '$copy = clone ($c->f);\n'
 "echo ($c->f)(), ':', (C::$g)(), ':', $copy();\n"
)

protocol.CHECKS['nested-class-property-closures'] = ['S = $drive_steps(S_initial[.COMPLETION = NORMAL], 3500)',
 'S.COMPLETION = NORMAL',
 'S.TODO = eps',
 '$object_default_test_output(S.EVENTS) = $ptascii("3:C:4:3:C")',
 '$class_named(S.CLASSNAMES, $ptascii("c")) = (porigin_c)',
 '$class_at(S.CLASSES, porigin_c) = (pclassdesc_c)',
 'pclassdesc_c.PROPERTIES = [ppropertydesc_f, ppropertydesc_g]',
 'ppropertydesc_f.ORIGIN = porigin_f',
 'ppropertydesc_g.ORIGIN = porigin_g',
 '$instance_default_at(S.INSTANCEDEFAULTS, porigin_c, porigin_f) = (pinstancetemplate_f)',
 'pinstancetemplate_f.STATE = INSTANCE_OBJECT_VALUE (POBJECT n_f) (PVCLOSURE n_f '
 'porigin_site_f) pinstanceobjectcertificate_f',
 '$class_static_at(S.CLASSSTATICS, porigin_g) = (pclassstatic_g)',
 'pclassstatic_g.STATE = PROP_VALUE (DIRECT (POBJECT n_g))',
 '$constant_callable_record(S.CONSTANTCLOSURES, n_g) = (pconstantclosure_g)',
 'pconstantclosure_g.SITE = porigin_site_g',
 '$closure_scope_at(S.CLOSURESCOPES, n_f) = (pclosurescope_f)',
 '$closure_scope_at(S.CLOSURESCOPES, n_g) = (pclosurescope_g)',
 '$closure_nested_creation(S, porigin_site_f)',
 '$closure_nested_creation(S, porigin_site_g)',
 'pclosurescope_f.CREATION = eps /\\ pclosurescope_g.CREATION = eps',
 '$property_callable_scope_valid(S, porigin_site_f, pclosurescope_f)',
 '$property_callable_scope_valid(S, porigin_site_g, pclosurescope_g)',
 '$closure_scope_creation_valid(S, porigin_site_f, pclosurescope_f)',
 '$closure_scope_creation_valid(S, porigin_site_g, pclosurescope_g)',
 '$closure_scope_row_valid(S, pclosurescope_f)',
 '$closure_scope_row_valid(S, pclosurescope_g)',
 'S.OBJECTS[0] = REALCLOSURE porigin_maker pitem_maker* pstaticcell_maker*',
 '~((HOBJECT 0) <- S.ALLOCATIONS)',
 '~$property_callable_scope_valid(S, porigin_maker, pclosurescope_f)',
 '~$closure_scope_creation_valid(S, porigin_site_f, pclosurescope_f[.CREATION = ({FUNCTION '
 'porigin_maker, CALLSITE eps, RECEIVER false, EVIDENCE eps})])',
 'S_clone = $clone_object(S, n_f)',
 'S_clone.RESULT = KNOWN (POBJECT n_clone)',
 '$constant_callable_record(S_clone.CONSTANTCLOSURES, n_clone) = eps',
 '$closure_scope_at(S_clone.CLOSURESCOPES, n_clone) = (pclosurescope_clone)',
 'pclosurescope_clone.CREATION = eps',
 '$closure_scope_row_valid(S_clone, pclosurescope_clone)',
 'S_dead = $prune_allocations(S_clone[.ENV = eps][.GLOBALTABLE = eps][.RESULT = KNOWN '
 'PNULL][.BASE = BASE_VALUE (KNOWN PNULL)])',
 '~((HOBJECT n_clone) <- S_dead.ALLOCATIONS)',
 '$heap_owners($heap_graph(S_dead), HOBJECT n_f) = 1',
 '$heap_owners($heap_graph(S_dead), HOBJECT n_g) = 1',
 '$instance_default_state_valid(S_dead)',
 '$constant_callable_records_valid(S_dead, S_dead.CONSTANTCLOSURES)',
 '$property_state_valid(S_dead)']

protocol.SOURCES['private-named-fcc'] = (
 '<?php\n'
 'function named() { static $n = 0; return ++$n; }\n'
 'class P {\n'
 '    private const X = 5;\n'
 "    private static function secret() { return self::X . '/' . get_called_class(); }\n"
 '    public Closure $f = self::secret(...);\n'
 '    public static Closure $s = self::secret(...);\n'
 '    public Closure $n = named(...);\n'
 '}\n'
 'class Q extends P {}\n'
 '$p = new P;\n'
 '$q = new Q;\n'
 "echo ($p->f)(), ':', ($q->f)(), ':', (P::$s)(), ':', (int) ($p->f === $q->f), ':', ($p->n)(), ':', ($q->n)();\n"
)
protocol.CHECKS['private-named-fcc'] = [
 'S = $drive_steps(S_initial[.COMPLETION = NORMAL], 3500)',
 'S.COMPLETION = NORMAL',
 'S.TODO = eps',
 '$object_default_test_output(S.EVENTS) = $ptascii("5/P:5/P:5/P:0:1:2")',
 '$class_named(S.CLASSNAMES, $ptascii("p")) = (porigin_p)',
 '$class_named(S.CLASSNAMES, $ptascii("q")) = (porigin_q)',
 '$class_at(S.CLASSES, porigin_p) = (pclassdesc_p)',
 'pclassdesc_p.PROPERTIES = [ppropertydesc_f, ppropertydesc_s, ppropertydesc_n]',
 'ppropertydesc_f.ORIGIN = porigin_f',
 'ppropertydesc_s.ORIGIN = porigin_s',
 'ppropertydesc_n.ORIGIN = porigin_n',
 'ppropertydesc_f.DEFAULT = PROP_DEFERRED porigin_site_f',
 'ppropertydesc_n.DEFAULT = PROP_DEFERRED porigin_site_n',
 '$instance_default_at(S.INSTANCEDEFAULTS, porigin_p, porigin_f) = (pinstancetemplate_f)',
 'pinstancetemplate_f.STATE = INSTANCE_OBJECT_VALUE (POBJECT n_f) (PVCLOSURE n_f porigin_site_f) pinstanceobjectcertificate_f',
 '$constant_callable_record(S.CONSTANTCLOSURES, n_f) = (pconstantclosure_f)',
 '$property_callable_receipt_owner(S, pconstantclosure_f) = (porigin_p)',
 '$constant_callable_method(S, porigin_site_f, porigin_p, pconstantclosure_f.PREFIX) = ((pmethoddesc, porigin_p))',
 'S.OBJECTS[n_f] = CONSTANTCLOSURE porigin_site_f (METHODCLOSURE pmethoddesc.FUNCTION.ORIGIN porigin_site_f porigin_p eps)',
 '$closure_scope_at(S.CLOSURESCOPES, n_f) = (pclosurescope_f)',
 '$property_callable_method_owner(S, pmethoddesc, porigin_site_f, porigin_p, pclosurescope_f) = (porigin_p)',
 '$closure_scope_row_valid(S, pclosurescope_f)',
 '$constant_callable_record_valid(S, pconstantclosure_f)',
 '$property_callable_method_receipt_owner(S, pconstantclosure_f[.DECL = porigin_s], pmethoddesc, porigin_site_f, porigin_p) = eps',
 '$property_callable_method_receipt_owner(S, pconstantclosure_f[.DECL = porigin_n], pmethoddesc, porigin_site_f, porigin_p) = eps',
 '$property_callable_method_receipt_owner(S, pconstantclosure_f[.SITE = porigin_site_n], pmethoddesc, porigin_site_f, porigin_p) = eps',
 '$property_callable_method_receipt_owner(S, pconstantclosure_f[.PREFIX = 0], pmethoddesc, porigin_site_f, porigin_p) = eps',
 '~$closure_scope_row_valid(S[.CONSTANTCLOSURES = eps], pclosurescope_f)',
 '~$closure_scope_row_valid(S[.ALLOCATIONS = eps], pclosurescope_f)',
 '~$closure_scope_row_valid(S[.OBJECTS = $object_set(S.OBJECTS, n_f, METHODCLOSURE pmethoddesc.FUNCTION.ORIGIN porigin_site_f porigin_p eps)], pclosurescope_f)',
 '~$closure_scope_row_valid(S, pclosurescope_f[.CALLED = porigin_q])',
 '~$closure_scope_row_valid(S, pclosurescope_f[.LEXICAL = porigin_q])',
 'S_requested = S[.OBJECTS = $object_set(S.OBJECTS, n_f, CONSTANTCLOSURE porigin_site_f (METHODCLOSURE pmethoddesc.FUNCTION.ORIGIN porigin_site_f porigin_q eps))]',
 '~$closure_scope_row_valid(S_requested, pclosurescope_f[.CALLED = porigin_q])',
 'S_clone = $clone_object(S, n_f)',
 'S_clone.RESULT = KNOWN (POBJECT n_clone)',
 '$(n_f < n_clone)',
 'S_clone.OBJECTS[n_clone] = METHODCLOSURE pmethoddesc.FUNCTION.ORIGIN porigin_site_f porigin_p eps',
 '$constant_callable_record(S_clone.CONSTANTCLOSURES, n_clone) = eps',
 '$closure_scope_at(S_clone.CLOSURESCOPES, n_clone) = (pclosurescope_clone)',
 '$closure_scope_row_valid(S_clone, pclosurescope_clone)',
 '$property_callable_method_owner(S_clone, pmethoddesc, porigin_site_f, porigin_p, pclosurescope_clone) = (porigin_p)',
 '$property_callable_clone_receipt_owner(S_clone, [pconstantclosure_f], pmethoddesc, porigin_site_f, porigin_p, n_f) = eps',
 '~$closure_scope_row_valid(S_clone[.CONSTANTCLOSURES = eps], pclosurescope_clone)',
 'S_dead = $prune_allocations(S_clone[.INSTANCEDEFAULTS = eps][.CLASSSTATICS = eps][.ENV = eps][.GLOBALTABLE = eps][.BASE = BASE_VALUE (KNOWN PNULL)])',
 '~((HOBJECT n_f) <- S_dead.ALLOCATIONS)',
 '$closure_scope_at(S_dead.CLOSURESCOPES, n_f) = eps',
 '(HOBJECT n_clone) <- S_dead.ALLOCATIONS',
 '$constant_callable_record(S_dead.CONSTANTCLOSURES, n_f) = (pconstantclosure_f)',
 '$property_callable_method_receipt_owner(S_dead, pconstantclosure_f, pmethoddesc, porigin_site_f, porigin_p) = (porigin_p)',
 '$closure_scope_row_valid(S_dead, pclosurescope_clone)',
 '$heap_owners($heap_graph(S_dead), HOBJECT n_f) = 0',
 '$heap_owners($heap_graph(S_dead), HOBJECT n_clone) = 1'
]

protocol.PREFIX += r'''
dec $object_default_cache_replace(pconstantclosure*, nat, pconstantclosure) : pconstantclosure*
def $object_default_cache_replace(eps, n_target, pconstantclosure_new) = eps
def $object_default_cache_replace(pconstantclosure :: pconstantclosure_tail*, n_target, pconstantclosure_new) = pconstantclosure_new :: pconstantclosure_tail*
  -- if pconstantclosure.OBJECT = n_target
def $object_default_cache_replace(pconstantclosure :: pconstantclosure_tail*, n_target, pconstantclosure_new) = pconstantclosure :: $object_default_cache_replace(pconstantclosure_tail*, n_target, pconstantclosure_new)
  -- if pconstantclosure.OBJECT =/= n_target
def $object_default_test_stage(S, 5) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = CLOSURE_TARGET n
  -- if pcallcontext.LEXICAL_CLASS = (porigin_lexical)
  -- if pcallcontext.CALLED_CLASS = (porigin_called)
  -- if porigin_lexical =/= porigin_called
  -- if $object_body(S.OBJECTS[n]) = METHODCLOSURE pcallcontext.FUNCTION porigin_site porigin_called eps
'''

protocol.SOURCES['trait-property-fcc-cache-publication'] = ('<?php\n'
 'namespace {\n'
 "    function selected() { return 'global'; }\n"
 '}\n'
 'namespace N {\n'
 '    trait Maker {\n'
 "        private static function reveal() { return self::class . '/' . "
 'get_called_class(); }\n'
 '        public \\Closure $f = self::reveal(...);\n'
 '        public static \\Closure $s = self::reveal(...);\n'
 '        public \\Closure $n = selected(...);\n'
 '    }\n'
 '    class HostA { use Maker; }\n'
 '    $a = new HostA;\n'
 "    echo ($a->f)(), ':', (HostA::$s)(), ':', ($a->n)(), ';';\n"
 "    HostA::$s = static function() { return 'replacement'; };\n"
 '    if (true) {\n'
 "        function selected() { return 'late'; }\n"
 '        class HostB { use Maker; }\n'
 '    }\n'
 '    $b = new HostB;\n'
 "    echo ($b->f)(), ':', (HostB::$s)(), ':', ($b->n)(), ':', selected();\n"
 '}\n')

protocol.CHECKS['trait-property-fcc-cache-publication'] = ['S = $object_default_test_seek(S_initial[.COMPLETION = NORMAL], 5, 7000)',
 'S.CURRENT = (pcallcontext)',
 'pcallcontext.LEXICAL_CLASS = (porigin_a)',
 'pcallcontext.CALLED_CLASS = (porigin_b)',
 'porigin_a =/= porigin_b',
 '$class_at(S.CLASSES, porigin_a) = (pclassdesc_a)',
 '$class_at(S.CLASSES, porigin_b) = (pclassdesc_b)',
 'pclassdesc_a.PROPERTIES = [ppropertydesc_af, ppropertydesc_as, ppropertydesc_an]',
 'pclassdesc_b.PROPERTIES = [ppropertydesc_bf, ppropertydesc_bs, ppropertydesc_bn]',
 'ppropertydesc_af.ORIGIN = porigin_af',
 'ppropertydesc_as.ORIGIN = porigin_as',
 'ppropertydesc_an.ORIGIN = porigin_an',
 'ppropertydesc_bf.ORIGIN = porigin_bf',
 'ppropertydesc_bs.ORIGIN = porigin_bs',
 'ppropertydesc_bn.ORIGIN = porigin_bn',
 'ppropertydesc_af.DEFAULT = PROP_DEFERRED porigin_site_f',
 'ppropertydesc_bf.DEFAULT = PROP_DEFERRED porigin_site_f',
 'ppropertydesc_as.DEFAULT = PROP_DEFERRED porigin_site_s',
 'ppropertydesc_bs.DEFAULT = PROP_DEFERRED porigin_site_s',
 'ppropertydesc_an.DEFAULT = PROP_DEFERRED porigin_site_n',
 'ppropertydesc_bn.DEFAULT = PROP_DEFERRED porigin_site_n',
 '$constant_callable_first(S.CONSTANTCLOSURES, porigin_site_f) = (pconstantclosure_af)',
 '$constant_callable_first(S.CONSTANTCLOSURES, porigin_site_s) = (pconstantclosure_as)',
 '$constant_callable_first(S.CONSTANTCLOSURES, porigin_site_n) = (pconstantclosure_an)',
 '$instance_default_at(S.INSTANCEDEFAULTS, porigin_b, porigin_bf) = (pinstancetemplate_bf)',
 'pinstancetemplate_bf.STATE = INSTANCE_OBJECT_VALUE (POBJECT n_bf) (PVCLOSURE n_bf '
 'porigin_site_f) pinstanceobjectcertificate_bf',
 '$instance_default_at(S.INSTANCEDEFAULTS, porigin_b, porigin_bn) = (pinstancetemplate_bn)',
 'pinstancetemplate_bn.STATE = INSTANCE_OBJECT_VALUE (POBJECT n_bn) (PVCLOSURE n_bn '
 'porigin_site_n) pinstanceobjectcertificate_bn',
 '$constant_callable_record(S.CONSTANTCLOSURES, n_bf) = (pconstantclosure_bf)',
 '$constant_callable_record(S.CONSTANTCLOSURES, n_bn) = (pconstantclosure_bn)',
 'pconstantclosure_af.DECL = porigin_af',
 'pconstantclosure_as.DECL = porigin_as',
 'pconstantclosure_an.DECL = porigin_an',
 'pconstantclosure_bf.DECL = porigin_bf',
 'pconstantclosure_bn.DECL = porigin_bn',
 '$(pconstantclosure_af.PREFIX < pconstantclosure_bf.PREFIX)',
 '$(pconstantclosure_an.PREFIX < pconstantclosure_bn.PREFIX)',
 '$property_callable_receipt_owner(S, pconstantclosure_af) = (porigin_a)',
 '$property_callable_receipt_owner(S, pconstantclosure_bf) = (porigin_b)',
 '$property_callable_cached_method(S, porigin_site_f) = (pmethoddesc_a)',
 '$constant_callable_method_fresh(S, porigin_site_f, porigin_b, pconstantclosure_bf.PREFIX) = '
 '((pmethoddesc_b, porigin_b))',
 'pmethoddesc_a.FUNCTION.ORIGIN =/= pmethoddesc_b.FUNCTION.ORIGIN',
 'pmethoddesc_a.OWNER = porigin_a',
 'pmethoddesc_b.OWNER = porigin_b',
 '~$method_accessible(S, pmethoddesc_a, (porigin_b))',
 '~$class_origin_matches(S, porigin_b, pclassdesc_a.NAME, |S.CLASSES|)',
 '$constant_callable_method(S, porigin_site_f, porigin_b, pconstantclosure_bf.PREFIX) = '
 '((pmethoddesc_a, porigin_b))',
 '$constant_callable_method(S, porigin_site_f, porigin_b, 0) = eps',
 '$closure_scope_at(S.CLOSURESCOPES, n_bf) = (pclosurescope_bf)',
 'pclosurescope_bf.LEXICAL = porigin_a /\\ pclosurescope_bf.CALLED = porigin_b',
 '$property_callable_method_owner(S, pmethoddesc_a, porigin_site_f, porigin_b, '
 'pclosurescope_bf) = (porigin_b)',
 '$closure_scope_row_valid(S, pclosurescope_bf)',
 '$call_current_valid(S)',
 '$constant_callable_record_valid(S, pconstantclosure_bf)',
 '$property_callable_method_receipt_owner(S, pconstantclosure_bf[.DECL = porigin_af], '
 'pmethoddesc_a, porigin_site_f, porigin_b) = eps',
 '$property_callable_method_receipt_owner(S, pconstantclosure_bf[.PREFIX = '
 'pconstantclosure_af.PREFIX], pmethoddesc_a, porigin_site_f, porigin_b) = eps',
 '~$closure_scope_row_valid(S, pclosurescope_bf[.LEXICAL = porigin_b])',
 '~$closure_scope_row_valid(S, pclosurescope_bf[.CALLED = porigin_a])',
 'S_wrong_method = S[.OBJECTS = $object_set(S.OBJECTS, n_bf, CONSTANTCLOSURE porigin_site_f '
 '(METHODCLOSURE pmethoddesc_b.FUNCTION.ORIGIN porigin_site_f porigin_b eps))]',
 '~$closure_scope_row_valid(S_wrong_method, pclosurescope_bf[.LEXICAL = porigin_b])',
 'S_wrong_first = S[.OBJECTS = $object_set(S.OBJECTS, pconstantclosure_af.OBJECT, '
 'CONSTANTCLOSURE porigin_site_f (METHODCLOSURE pmethoddesc_b.FUNCTION.ORIGIN porigin_site_f '
 'porigin_a eps))]',
 '$property_callable_cached_method(S_wrong_first, porigin_site_f) = eps',
 '~$closure_scope_row_valid(S_wrong_first, pclosurescope_bf)',
 'S_wrong_prefix = S[.CONSTANTCLOSURES = $object_default_cache_replace(S.CONSTANTCLOSURES, '
 'pconstantclosure_af.OBJECT, pconstantclosure_af[.PREFIX = 0])]',
 '$property_callable_cached_method(S_wrong_prefix, porigin_site_f) = eps',
 'S_wrong_decl = S[.CONSTANTCLOSURES = $object_default_cache_replace(S.CONSTANTCLOSURES, '
 'pconstantclosure_af.OBJECT, pconstantclosure_af[.DECL = porigin_bf])]',
 '$property_callable_cached_method(S_wrong_decl, porigin_site_f) = eps',
 '~$property_default_transfer_valid(S, ppropertydesc_af, PVCLOSURE n_bf porigin_site_f)',
 '$property_default_transfer_valid(S, ppropertydesc_bf, PVCLOSURE n_bf porigin_site_f)',
 '~((HOBJECT pconstantclosure_as.OBJECT) <- S.ALLOCATIONS)',
 '$property_callable_cached_method(S, porigin_site_s) = (pmethoddesc_a)',
 '$property_callable_cached_function(S, porigin_site_n) = (pfunction_global)',
 '$constant_callable_function_fresh(S, porigin_site_n, pconstantclosure_bn.PREFIX) = '
 '(pfunction_late)',
 'pfunction_global.ORIGIN =/= pfunction_late.ORIGIN',
 '$constant_callable_function(S, porigin_site_n, pconstantclosure_bn.PREFIX) = '
 '(pfunction_global)',
 '$constant_callable_function(S, porigin_site_n, 0) = eps',
 'S_done = $drive_steps(S, 4500)',
 'S_done.COMPLETION = NORMAL',
 'S_done.TODO = eps',
 '$object_default_test_output(S_done.EVENTS) = '
 '$ptascii("N\\\\HostA/N\\\\HostA:N\\\\HostA/N\\\\HostA:global;N\\\\HostA/N\\\\HostB:N\\\\HostA/N\\\\HostB:global:late")',
 '$constant_callable_records_valid(S_done, S_done.CONSTANTCLOSURES)',
 '$instance_default_state_valid(S_done)',
 'S_clone = $clone_object(S_done, n_bf)',
 'S_clone.RESULT = KNOWN (POBJECT n_clone)',
 '$closure_scope_at(S_clone.CLOSURESCOPES, n_clone) = (pclosurescope_clone)',
 '$closure_scope_row_valid(S_clone, pclosurescope_clone)',
 'S_dead = $prune_allocations(S_clone[.INSTANCEDEFAULTS = eps][.CLASSSTATICS = eps][.ENV = '
 'eps][.GLOBALTABLE = eps][.BASE = BASE_VALUE (KNOWN PNULL)])',
 '~((HOBJECT pconstantclosure_af.OBJECT) <- S_dead.ALLOCATIONS)',
 '~((HOBJECT pconstantclosure_as.OBJECT) <- S_dead.ALLOCATIONS)',
 '$closure_scope_at(S_dead.CLOSURESCOPES, pconstantclosure_af.OBJECT) = eps',
 '$property_callable_cached_method(S_dead, porigin_site_f) = (pmethoddesc_a)',
 '$property_callable_cached_method(S_dead, porigin_site_s) = (pmethoddesc_a)',
 '$property_callable_cached_function(S_dead, porigin_site_n) = (pfunction_global)',
 '$closure_scope_row_valid(S_dead, pclosurescope_clone)',
 '$constant_callable_records_valid(S_dead, S_dead.CONSTANTCLOSURES)',
 '$heap_owners($heap_graph(S_dead), HOBJECT pconstantclosure_af.OBJECT) = 0',
 '$heap_owners($heap_graph(S_dead), HOBJECT n_clone) = 1']

if __name__ == '__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--prepare');args=parser.parse_args()
 if args.prepare:protocol.prepare(Path(args.prepare));print(args.prepare)
 else:protocol.run(Path(tempfile.mkdtemp(prefix='object-property-default-',dir=protocol.ROOT/'.tools'))/'run')
