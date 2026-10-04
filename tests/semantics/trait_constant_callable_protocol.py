#!/usr/bin/env python3
"""Check shared trait-constant targets, declaring scope, retry and cache owners."""
import argparse,tempfile
from pathlib import Path
import deferred_static_default_protocol as protocol

# The repeated private-default constructor path exceeds the bounded AL run.
# Keep the exact source-derived assertions in the production SL evaluator.
protocol.RUNNER_FLAGS={'trait-constant-method-partial-created-child':['--sl']}

protocol.SOURCES = {'trait-constant-named-fcc-late-import': '<?php\n'
                                         'namespace {\n'
                                         "    function selected() { return 'global'; }\n"
                                         '}\n'
                                         'namespace ConstNames {\n'
                                         '    trait ConstantNamedFactory {\n'
                                         '        public const \\Closure F = '
                                         'selected(...);\n'
                                         '    }\n'
                                         '    class NamedA { use ConstantNamedFactory; }\n'
                                         '    $first = NamedA::F;\n'
                                         "    echo $first(), ':', (int)($first === "
                                         "NamedA::F), ';';\n"
                                         '    if (true) {\n'
                                         "        function selected() { return 'late'; }\n"
                                         '        class NamedB { use ConstantNamedFactory; '
                                         '}\n'
                                         '    }\n'
                                         '    $second = NamedB::F;\n'
                                         '    $copy = clone $second;\n'
                                         "    echo $second(), ':', $copy(), ':', "
                                         "selected(), ':', (int)($first === $second);\n"
                                         '}\n',
 'trait-constant-real-closure-late-import': '<?php\n'
                                            'trait ConstantClosureFactory {\n'
                                            "    private const TOKEN = 'secret';\n"
                                            '    public const \\Closure F = static '
                                            'function () {\n'
                                            "        return self::class . '/' . "
                                            "get_called_class() . ':' . self::TOKEN;\n"
                                            '    };\n'
                                            '}\n'
                                            'class ClosureA { use ConstantClosureFactory; '
                                            '}\n'
                                            '$first = ClosureA::F;\n'
                                            "echo $first(), ':', (int)($first === "
                                            "ClosureA::F), ';';\n"
                                            'if (true) { class ClosureB { use '
                                            'ConstantClosureFactory; } }\n'
                                            '$second = ClosureB::F;\n'
                                            '$copy = clone $second;\n'
                                            'unset($first);\n'
                                            "echo $second(), ':', $copy(), ':', "
                                            '(int)($second === ClosureB::F);\n',
 'trait-constant-method-partial-created-child': '<?php\n'
                                                'trait ConstantChildFactory {\n'
                                                '    private static function maker() {\n'
                                                '        return function ($value = new '
                                                'self) {\n'
                                                "            return self::class . '/' . "
                                                "get_called_class() . '/' . "
                                                '$value::class;\n'
                                                '        };\n'
                                                '    }\n'
                                                '    public const array F = '
                                                '[self::maker(...), ConstantLate::X];\n'
                                                '}\n'
                                                'class ConstantChildA {\n'
                                                '    use ConstantChildFactory;\n'
                                                '    private function __construct() { echo '
                                                "'A:'; }\n"
                                                '}\n'
                                                'try {\n'
                                                '    $first = ConstantChildA::F;\n'
                                                '} catch (Error $e) {\n'
                                                "    echo 'F:';\n"
                                                '}\n'
                                                'if (true) {\n'
                                                '    class ConstantLate { public const X = '
                                                '7; }\n'
                                                '    class ConstantChildB { use '
                                                'ConstantChildFactory; }\n'
                                                '}\n'
                                                '$values = ConstantChildB::F;\n'
                                                '$maker = $values[0];\n'
                                                '$child = $maker();\n'
                                                '$makerClone = clone $maker;\n'
                                                '$secondChild = $makerClone();\n'
                                                '$childClone = clone $child;\n'
                                                'unset($values, $maker, $makerClone, '
                                                '$child);\n'
                                                "echo $secondChild(), ';', $childClone(), "
                                                "';';\n"
                                                '$retry = ConstantChildA::F;\n'
                                                '$retryChild = $retry[0]();\n'
                                                "echo $retryChild(), ':', $retry[1];\n"}

protocol.PREFIX = r'''
dec $trait_callable_test_resume(pstate) : pstate
def $trait_callable_test_resume(S) = S[.COMPLETION = NORMAL] -- if S.COMPLETION = BUDGET
def $trait_callable_test_resume(S) = S -- otherwise
dec $trait_callable_test_output(pevent*) : ptbytes
def $trait_callable_test_output(eps) = eps
def $trait_callable_test_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $trait_callable_test_output(pevent*)
dec $trait_callable_test_stage(pstate, nat) : bool
def $trait_callable_test_stage(S, 0) = true
  -- if $trait_callable_test_output(S.EVENTS) = $ptascii("F:")
  -- if $class_named(S.CLASSNAMES, $ptascii("constantlate")) = eps
def $trait_callable_test_stage(S, 1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = CLOSURE_TARGET n_maker
  -- if $(n_maker < |S.OBJECTS|)
  -- if S.OBJECTS[n_maker] = CONSTANTCLOSURE porigin_site (METHODCLOSURE porigin_method porigin_site porigin_called eps)
  -- if pcallcontext.LEXICAL_CLASS =/= pcallcontext.CALLED_CLASS
  -- if S.TODO = (CLOSURE_CAPTURE n_child 0) :: ptask_tail*
def $trait_callable_test_stage(S, 2) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = CLOSURE_TARGET n_maker
  -- if $(n_maker < |S.OBJECTS|)
  -- if S.OBJECTS[n_maker] = METHODCLOSURE porigin_method porigin_site porigin_called eps
  -- if pcallcontext.LEXICAL_CLASS =/= pcallcontext.CALLED_CLASS
  -- if S.TODO = (CLOSURE_CAPTURE n_child 0) :: ptask_tail*
def $trait_callable_test_stage(S, n_stage) = false -- otherwise
dec $trait_callable_test_seek(pstate, nat, nat) : pstate
def $trait_callable_test_seek(S, n_stage, n_limit) = S
  -- if $trait_callable_test_stage(S, n_stage)
def $trait_callable_test_seek(S, n_stage, n_limit) = $trait_callable_test_seek($trait_callable_test_resume(S_next), n_stage, n_rest)
  -- if ~$trait_callable_test_stage(S, n_stage)
  -- if $(n_limit > 0)
  -- if S.COMPLETION = NORMAL
  -- if ~S.COMPILESTOP
  -- if n_rest = $(n_limit - 1)
  -- if S_next = $drive_steps(S, 1)
'''

def premises(text):return text.strip().splitlines()

protocol.CHECKS = {'trait-constant-named-fcc-late-import': premises(r'''
S = $drive_steps(S_initial[.COMPLETION = NORMAL], 6000)
S.COMPLETION = NORMAL /\ S.TODO = eps
$trait_callable_test_output(S.EVENTS) = $ptascii("global:1;global:global:late:0")
$class_named(S.CLASSNAMES, $ptascii("constnames\\nameda")) = (porigin_a)
$class_named(S.CLASSNAMES, $ptascii("constnames\\namedb")) = (porigin_b)
$class_constant_lookup(S, porigin_a, $ptascii("F"), |S.CLASSES|) = (pclassconstantdesc_a)
$class_constant_lookup(S, porigin_b, $ptascii("F"), |S.CLASSES|) = (pclassconstantdesc_b)
pclassconstantdesc_a.ORIGIN = TRAIT_MEMBER_ORIGIN porigin_a porigin_member
pclassconstantdesc_b.ORIGIN = TRAIT_MEMBER_ORIGIN porigin_b porigin_member
$default_cache_at(S.CLASSCONSTANTCACHE, pclassconstantdesc_a.ORIGIN) = (pdefaultcache_a)
$default_cache_at(S.CLASSCONSTANTCACHE, pclassconstantdesc_b.ORIGIN) = (pdefaultcache_b)
pdefaultcache_a.VALUE = POBJECT n_a
pdefaultcache_b.VALUE = POBJECT n_b
n_a =/= n_b
$constant_callable_record(S.CONSTANTCLOSURES, n_a) = (pconstantclosure_a)
$constant_callable_record(S.CONSTANTCLOSURES, n_b) = (pconstantclosure_b)
pconstantclosure_a.SITE = porigin_site
pconstantclosure_b.SITE = porigin_site
pconstantclosure_a.DECL = pclassconstantdesc_a.ORIGIN
pconstantclosure_b.DECL = pclassconstantdesc_b.ORIGIN
$(pconstantclosure_a.PREFIX < pconstantclosure_b.PREFIX)
$constant_callable_first(S.CONSTANTCLOSURES, porigin_site) = (pconstantclosure_a)
$constant_callable_function_fresh(S, porigin_site, pconstantclosure_a.PREFIX) = (pfunction_global)
$constant_callable_function_fresh(S, porigin_site, pconstantclosure_b.PREFIX) = (pfunction_late)
pfunction_global.ORIGIN =/= pfunction_late.ORIGIN
S.OBJECTS[n_a] = CONSTANTCLOSURE porigin_site (NAMEDCLOSURE pfunction_global.ORIGIN)
S.OBJECTS[n_b] = CONSTANTCLOSURE porigin_site (NAMEDCLOSURE pfunction_global.ORIGIN)
$class_constant_callable_cached_function(S, porigin_site) = (pfunction_global)
$constant_callable_function(S, porigin_site, pconstantclosure_b.PREFIX) = (pfunction_global)
$class_constant_callable_receipt_owner(S, pconstantclosure_b) = (porigin_b)
$constant_callable_records_valid(S, S.CONSTANTCLOSURES)
$class_constant_caches_valid(S, S.CLASSCONSTANTCACHE)
S_foreign = S[.CONSTANTCLOSURES = [pconstantclosure_a, pconstantclosure_b[.DECL = pclassconstantdesc_a.ORIGIN]]]
$constant_callable_record_valid(S_foreign, pconstantclosure_b[.DECL = pclassconstantdesc_a.ORIGIN])
~$class_constant_caches_valid(S_foreign, S_foreign.CLASSCONSTANTCACHE)
~$constant_callable_record_valid(S, pconstantclosure_b[.PREFIX = pconstantclosure_a.PREFIX])
n_future = $(|S.DECLARATIONS| + 1)
$class_constant_callable_receipt_owner(S, pconstantclosure_b[.PREFIX = n_future]) = eps
~$constant_callable_cache_valid(S, pclassconstantdesc_b, pdefaultcache_a.CLASS, pconstantclosure_b.PREFIX)
S_wrong_target = S[.OBJECTS = $object_set(S.OBJECTS, n_a, CONSTANTCLOSURE porigin_site (NAMEDCLOSURE pfunction_late.ORIGIN))]
$class_constant_callable_cached_function(S_wrong_target, porigin_site) = eps
~$constant_callable_record_valid(S_wrong_target, pconstantclosure_a)
$class_constant_callable_cached_function(S[.CONSTANTCLOSURES = eps], porigin_site) = eps
$class_constant_callable_cached_function(S[.CONSTANTCLOSURES = [pconstantclosure_b]], porigin_site) = eps
~$constant_callable_record_valid(S[.CONSTANTCLOSURES = [pconstantclosure_b]], pconstantclosure_b)
$lookup(S.ENV, $ptascii("copy")) = (n_cell_copy)
S.STORE[n_cell_copy] = DEFINED (POBJECT n_copy)
S.OBJECTS[n_copy] = NAMEDCLOSURE pfunction_global.ORIGIN
$constant_callable_record(S.CONSTANTCLOSURES, n_copy) = eps
S_cache = $prune_allocations(S[.ENV = eps][.GLOBALTABLE = eps][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)])
HOBJECT n_a <- S_cache.ALLOCATIONS
HOBJECT n_b <- S_cache.ALLOCATIONS
~((HOBJECT n_copy) <- S_cache.ALLOCATIONS)
$heap_owners($heap_graph(S_cache), HOBJECT n_a) = 1
$heap_owners($heap_graph(S_cache), HOBJECT n_b) = 1
$constant_callable_records_valid(S_cache, S_cache.CONSTANTCLOSURES)
$class_constant_caches_valid(S_cache, S_cache.CLASSCONSTANTCACHE)
'''),
'trait-constant-real-closure-late-import': premises(r'''
S = $drive_steps(S_initial[.COMPLETION = NORMAL], 6000)
S.COMPLETION = NORMAL /\ S.TODO = eps
$trait_callable_test_output(S.EVENTS) = $ptascii("ClosureA/ClosureA:secret:1;ClosureB/ClosureB:secret:ClosureB/ClosureB:secret:1")
$class_named(S.CLASSNAMES, $ptascii("closurea")) = (porigin_a)
$class_named(S.CLASSNAMES, $ptascii("closureb")) = (porigin_b)
$class_constant_lookup(S, porigin_a, $ptascii("F"), |S.CLASSES|) = (pclassconstantdesc_a)
$class_constant_lookup(S, porigin_b, $ptascii("F"), |S.CLASSES|) = (pclassconstantdesc_b)
pclassconstantdesc_a.ORIGIN = TRAIT_MEMBER_ORIGIN porigin_a porigin_member
pclassconstantdesc_b.ORIGIN = TRAIT_MEMBER_ORIGIN porigin_b porigin_member
$default_cache_at(S.CLASSCONSTANTCACHE, pclassconstantdesc_a.ORIGIN) = (pdefaultcache_a)
$default_cache_at(S.CLASSCONSTANTCACHE, pclassconstantdesc_b.ORIGIN) = (pdefaultcache_b)
pdefaultcache_a.VALUE = POBJECT n_a
pdefaultcache_b.VALUE = POBJECT n_b
n_a =/= n_b
$constant_callable_record(S.CONSTANTCLOSURES, n_a) = (pconstantclosure_a)
$constant_callable_record(S.CONSTANTCLOSURES, n_b) = (pconstantclosure_b)
pconstantclosure_a.SITE = porigin_site
pconstantclosure_b.SITE = porigin_site
$closure_scope_at(S.CLOSURESCOPES, n_a) = (pclosurescope_a)
$closure_scope_at(S.CLOSURESCOPES, n_b) = (pclosurescope_b)
pclosurescope_a.LEXICAL = porigin_a /\ pclosurescope_a.CALLED = porigin_a
pclosurescope_b.LEXICAL = porigin_b /\ pclosurescope_b.CALLED = porigin_b
pclosurescope_a.RECEIVER = eps /\ pclosurescope_a.CREATION = eps
pclosurescope_b.RECEIVER = eps /\ pclosurescope_b.CREATION = eps
$class_constant_closure_scope_valid(S, porigin_site, pclosurescope_a)
$class_constant_closure_scope_valid(S, porigin_site, pclosurescope_b)
$closure_scope_rows_valid(S, S.CLOSURESCOPES)
$constant_callable_records_valid(S, S.CONSTANTCLOSURES)
~$class_constant_closure_scope_valid(S, porigin_site, pclosurescope_b[.LEXICAL = porigin_a][.CALLED = porigin_a])
~$closure_scope_row_valid(S, pclosurescope_b[.LEXICAL = porigin_a][.CALLED = porigin_a])
~$class_constant_closure_scope_valid(S, porigin_site, pclosurescope_b[.CALLED = porigin_a])
~$class_constant_closure_scope_valid(S, porigin_site, pclosurescope_b[.RECEIVER = (n_a)])
~$class_constant_closure_receipt(S, pconstantclosure_b[.DECL = pclassconstantdesc_a.ORIGIN], porigin_site, porigin_b)
~$constant_callable_record_valid(S, pconstantclosure_b[.DECL = pclassconstantdesc_a.ORIGIN])
~$constant_callable_cache_valid(S, pclassconstantdesc_b, pdefaultcache_a.CLASS, pconstantclosure_b.PREFIX)
$lookup(S.ENV, $ptascii("copy")) = (n_cell_copy)
S.STORE[n_cell_copy] = DEFINED (POBJECT n_copy)
S.OBJECTS[n_copy] = REALCLOSURE porigin_site eps eps
$constant_callable_record(S.CONSTANTCLOSURES, n_copy) = eps
$closure_scope_at(S.CLOSURESCOPES, n_copy) = (pclosurescope_copy)
pclosurescope_copy.LEXICAL = porigin_b /\ pclosurescope_copy.CALLED = porigin_b
$class_constant_closure_scope_valid(S, porigin_site, pclosurescope_copy)
$closure_scope_row_valid(S, pclosurescope_copy)
~$class_constant_closure_scope_valid(S[.CONSTANTCLOSURES = eps], porigin_site, pclosurescope_copy)
~$class_constant_closure_scope_valid(S[.CONSTANTCLOSURES = [pconstantclosure_b[.OBJECT = n_copy]]], porigin_site, pclosurescope_copy)
S_cache = $prune_allocations(S[.ENV = eps][.GLOBALTABLE = eps][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)])
HOBJECT n_a <- S_cache.ALLOCATIONS
HOBJECT n_b <- S_cache.ALLOCATIONS
~((HOBJECT n_copy) <- S_cache.ALLOCATIONS)
$heap_owners($heap_graph(S_cache), HOBJECT n_a) = 1
$heap_owners($heap_graph(S_cache), HOBJECT n_b) = 1
$class_constant_caches_valid(S_cache, S_cache.CLASSCONSTANTCACHE)
$constant_callable_records_valid(S_cache, S_cache.CONSTANTCLOSURES)
'''),
'trait-constant-method-partial-created-child': premises(r'''
S_failed = $trait_callable_test_seek(S_initial[.COMPLETION = NORMAL], 0, 6000)
$class_named(S_failed.CLASSNAMES, $ptascii("constantchilda")) = (porigin_a)
$class_constant_lookup(S_failed, porigin_a, $ptascii("F"), |S_failed.CLASSES|) = (pclassconstantdesc_a)
$default_cache_at(S_failed.CLASSCONSTANTCACHE, pclassconstantdesc_a.ORIGIN) = eps
S_failed.CONSTANTCLOSURES = [pconstantclosure_first]
pconstantclosure_first.OBJECT = n_first
pconstantclosure_first.SITE = porigin_site
pconstantclosure_first.DECL = pclassconstantdesc_a.ORIGIN
~((HOBJECT n_first) <- S_failed.ALLOCATIONS)
$closure_scope_at(S_failed.CLOSURESCOPES, n_first) = eps
$class_constant_callable_receipt_owner(S_failed, pconstantclosure_first) = (porigin_a)
$class_constant_callable_cached_method(S_failed, porigin_site) = (pmethoddesc_a)
S_failed.OBJECTS[n_first] = CONSTANTCLOSURE porigin_site (METHODCLOSURE pmethoddesc_a.FUNCTION.ORIGIN porigin_site porigin_a eps)
$constant_callable_record_valid(S_failed, pconstantclosure_first)
$heap_owners($heap_graph(S_failed), HOBJECT n_first) = 0
S = $trait_callable_test_seek(S_failed, 1, 6000)
S.CURRENT = (pcallcontext)
pcallcontext.TARGET = CLOSURE_TARGET n_maker
pcallcontext.LEXICAL_CLASS = (porigin_a)
pcallcontext.CALLED_CLASS = (porigin_b)
porigin_a =/= porigin_b
S.TODO = (CLOSURE_CAPTURE n_child 0) :: ptask_tail*
$class_constant_lookup(S, porigin_b, $ptascii("F"), |S.CLASSES|) = (pclassconstantdesc_b)
pclassconstantdesc_b.ORIGIN = TRAIT_MEMBER_ORIGIN porigin_b porigin_member
pclassconstantdesc_a.ORIGIN = TRAIT_MEMBER_ORIGIN porigin_a porigin_member
$default_cache_at(S.CLASSCONSTANTCACHE, pclassconstantdesc_a.ORIGIN) = eps
$default_cache_at(S.CLASSCONSTANTCACHE, pclassconstantdesc_b.ORIGIN) = (pdefaultcache_b)
pdefaultcache_b.CLASS = PVARRAY b ([(KINT 0, PVCLOSURE n_maker porigin_site), (KINT 1, PVSCALAR)])
$constant_callable_record(S.CONSTANTCLOSURES, n_maker) = (pconstantclosure_b)
pconstantclosure_b.DECL = pclassconstantdesc_b.ORIGIN
$(pconstantclosure_first.PREFIX < pconstantclosure_b.PREFIX)
$constant_callable_method_fresh(S, porigin_site, porigin_b, pconstantclosure_b.PREFIX) = ((pmethoddesc_b, porigin_b))
pmethoddesc_a.FUNCTION.ORIGIN =/= pmethoddesc_b.FUNCTION.ORIGIN
$constant_callable_method(S, porigin_site, porigin_b, pconstantclosure_b.PREFIX) = ((pmethoddesc_a, porigin_b))
~$method_accessible(S, pmethoddesc_a, (porigin_b))
$constant_callable_method_access(S, porigin_site, porigin_b, pmethoddesc_a)
$closure_scope_at(S.CLOSURESCOPES, n_maker) = (pclosurescope_maker)
$class_constant_callable_method_receipt_owner(S, pconstantclosure_b, pmethoddesc_a, porigin_site, porigin_b) = (porigin_b)
$class_constant_callable_method_owner(S, pmethoddesc_a, porigin_site, porigin_b, pclosurescope_maker) = (porigin_b)
$closure_scope_row_valid(S, pclosurescope_maker)
$call_current_valid(S)
$closure_scope_at(S.CLOSURESCOPES, n_child) = (pclosurescope_child)
$object_body(S.OBJECTS[n_child]) = REALCLOSURE porigin_child pitem* eps
pclosurescope_child.CREATION = (pclosurecreation)
pclosurecreation.EVIDENCE = (pclosurecreator)
pclosurecreator.SCOPE = CLOSURE_SCOPE pclosurescope_maker
pclosurecreation.FUNCTION = pmethoddesc_a.FUNCTION.ORIGIN
$trait_imported_origin(pclosurecreation.FUNCTION)
$origin_source(pclosurecreation.FUNCTION) =/= pclosurecreation.FUNCTION
pclosurescope_child.LEXICAL = porigin_a /\ pclosurescope_child.CALLED = porigin_b
pclosurescope_child.RECEIVER = eps /\ ~pclosurecreation.RECEIVER
$class_constant_method_child_valid(S, porigin_child, pclosurescope_child)
$closure_scope_classes_valid(S, porigin_child, pclosurescope_child)
$closure_scope_creation_valid(S, porigin_child, pclosurescope_child)
$closure_scope_row_valid(S, pclosurescope_child)
$class_constant_callable_method_history_owner(S, pmethoddesc_a, porigin_site, porigin_b, pclosurescope_maker[.LEXICAL = porigin_b]) = eps
$class_constant_callable_method_history_owner(S, pmethoddesc_a, porigin_site, porigin_b, pclosurescope_maker[.CALLED = porigin_a]) = eps
$class_constant_callable_method_receipt_owner(S, pconstantclosure_b[.DECL = pclassconstantdesc_a.ORIGIN], pmethoddesc_a, porigin_site, porigin_b) = eps
$class_constant_callable_method_receipt_owner(S, pconstantclosure_b[.PREFIX = pconstantclosure_first.PREFIX], pmethoddesc_a, porigin_site, porigin_b) = eps
$class_constant_callable_cached_method(S[.CONSTANTCLOSURES = eps], porigin_site) = eps
$class_constant_callable_cached_method(S[.CONSTANTCLOSURES = [pconstantclosure_b]], porigin_site) = eps
~$class_constant_method_scope_valid(S[.CONSTANTCLOSURES = [pconstantclosure_b]], pclosurescope_maker)
S_wrong_target = S[.OBJECTS = $object_set(S.OBJECTS, n_first, CONSTANTCLOSURE porigin_site (METHODCLOSURE pmethoddesc_b.FUNCTION.ORIGIN porigin_site porigin_a eps))]
$class_constant_callable_cached_method(S_wrong_target, porigin_site) = eps
~$class_constant_method_scope_valid(S_wrong_target, pclosurescope_maker)
S_wrong_body = S[.OBJECTS = $object_set(S.OBJECTS, n_maker, CONSTANTCLOSURE porigin_site (METHODCLOSURE pmethoddesc_b.FUNCTION.ORIGIN porigin_site porigin_b eps))]
~$class_constant_method_scope_valid(S_wrong_body, pclosurescope_maker)
$class_constant_callable_method_owner(S[.OBJECTS = $object_set(S.OBJECTS, n_maker, METHODCLOSURE pmethoddesc_a.FUNCTION.ORIGIN porigin_site porigin_b eps)], pmethoddesc_a, porigin_site, porigin_b, pclosurescope_maker) = eps
~$closure_creator_valid(S, porigin_child, pclosurescope_child, pclosurecreation[.FUNCTION = pmethoddesc_b.FUNCTION.ORIGIN], pclosurecreator)
~$closure_creator_valid(S, porigin_child, pclosurescope_child, pclosurecreation[.FUNCTION = $origin_source(pclosurecreation.FUNCTION)], pclosurecreator)
~$closure_creator_valid(S, porigin_child, pclosurescope_child, pclosurecreation[.CALLSITE = (porigin_child)], pclosurecreator)
~$class_constant_method_child_valid(S, porigin_child, pclosurescope_child[.CREATION = eps])
S_clone = $trait_callable_test_seek(S, 2, 6000)
S_clone.CURRENT = (pcallcontext_clone)
pcallcontext_clone.TARGET = CLOSURE_TARGET n_maker_clone
S_clone.OBJECTS[n_maker_clone] = METHODCLOSURE pmethoddesc_a.FUNCTION.ORIGIN porigin_site porigin_b eps
$constant_callable_record(S_clone.CONSTANTCLOSURES, n_maker_clone) = eps
$closure_scope_at(S_clone.CLOSURESCOPES, n_maker_clone) = (pclosurescope_maker_clone)
$class_constant_method_scope_valid(S_clone, pclosurescope_maker_clone)
$class_constant_callable_method_owner(S_clone, pmethoddesc_a, porigin_site, porigin_b, pclosurescope_maker_clone) = (porigin_b)
$class_constant_callable_method_history_owner(S_clone[.CONSTANTCLOSURES = [pconstantclosure_first]], pmethoddesc_a, porigin_site, porigin_b, pclosurescope_maker_clone) = eps
S_done = $drive_steps(S_clone, 6000)
S_done.COMPLETION = NORMAL /\ S_done.TODO = eps
$trait_callable_test_output(S_done.EVENTS) = $ptascii("F:A:ConstantChildA/ConstantChildB/ConstantChildA;A:ConstantChildA/ConstantChildB/ConstantChildA;A:ConstantChildA/ConstantChildA/ConstantChildA:7")
$default_cache_at(S_done.CLASSCONSTANTCACHE, pclassconstantdesc_a.ORIGIN) = (pdefaultcache_a)
pdefaultcache_a.CLASS = PVARRAY b_a ([(KINT 0, PVCLOSURE n_a porigin_site), (KINT 1, PVSCALAR)])
n_a =/= n_first /\ n_a =/= n_maker
$constant_callable_record(S_done.CONSTANTCLOSURES, n_a) = (pconstantclosure_a)
pconstantclosure_a.DECL = pclassconstantdesc_a.ORIGIN
$class_constant_callable_method_receipt_owner(S_done, pconstantclosure_a, pmethoddesc_a, porigin_site, porigin_a) = (porigin_a)
$class_constant_caches_valid(S_done, S_done.CLASSCONSTANTCACHE)
$constant_callable_records_valid(S_done, S_done.CONSTANTCLOSURES)
~((HOBJECT n_first) <- S_done.ALLOCATIONS)
~((HOBJECT n_maker_clone) <- S_done.ALLOCATIONS)
$closure_scope_at(S_done.CLOSURESCOPES, n_maker_clone) = eps
$class_constant_callable_method_owner(S_done, pmethoddesc_a, porigin_site, porigin_b, pclosurescope_maker_clone) = eps
$class_constant_method_scope_valid(S_done, pclosurescope_maker_clone)
$closure_evidence_valid(S_done, CLOSURE_SCOPE pclosurescope_maker_clone)
$heap_owners($heap_graph(S_done), HOBJECT n_first) = 0
$heap_owners($heap_graph(S_done), HOBJECT n_maker_clone) = 0
$lookup(S_done.ENV, $ptascii("childClone")) = (n_cell_child_clone)
S_done.STORE[n_cell_child_clone] = DEFINED (POBJECT n_child_clone)
$closure_scope_at(S_done.CLOSURESCOPES, n_child_clone) = (pclosurescope_child_clone)
$class_constant_method_child_valid(S_done, porigin_child, pclosurescope_child_clone)
$lookup(S_done.ENV, $ptascii("retryChild")) = (n_cell_retry_child)
S_done.STORE[n_cell_retry_child] = DEFINED (POBJECT n_retry_child)
$closure_scope_at(S_done.CLOSURESCOPES, n_retry_child) = (pclosurescope_retry_child)
$closure_scope_original_classes(S_done, porigin_child, pclosurescope_retry_child)
$class_constant_method_child_valid(S_done, porigin_child, pclosurescope_retry_child)
$closure_scope_rows_valid(S_done, S_done.CLOSURESCOPES)
S_cache = $prune_allocations(S_done[.ENV = eps][.GLOBALTABLE = eps][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)])
HOBJECT n_a <- S_cache.ALLOCATIONS
HOBJECT n_maker <- S_cache.ALLOCATIONS
~((HOBJECT n_child_clone) <- S_cache.ALLOCATIONS)
~((HOBJECT n_retry_child) <- S_cache.ALLOCATIONS)
$heap_owners($heap_graph(S_cache), HOBJECT n_first) = 0
$heap_owners($heap_graph(S_cache), HOBJECT n_maker_clone) = 0
$heap_owners($heap_graph(S_cache), HOBJECT n_a) = 1
$heap_owners($heap_graph(S_cache), HOBJECT n_maker) = 1
$class_constant_caches_valid(S_cache, S_cache.CLASSCONSTANTCACHE)
$class_constant_method_scope_valid(S_cache, pclosurescope_maker_clone)
''')}

if __name__ == '__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--prepare');args=parser.parse_args()
 if args.prepare:protocol.prepare(Path(args.prepare));print(args.prepare)
 else:protocol.run(Path(tempfile.mkdtemp(prefix='trait-constant-callables-',dir=protocol.ROOT/'.tools'))/'run')
