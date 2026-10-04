#!/usr/bin/env python3
"""Check constant-created Closure birth, transfer, scope, retry and cache roots."""
import argparse,base64,hashlib,json,os,signal,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tests/semantics'))
import static_types as types
from recorded_worker import Worker
from method_runtime import owned_members
ENV={'PATH':'/usr/bin:/bin','LC_ALL':'C','TZ':'UTC','PYTHONDONTWRITEBYTECODE':'1','GIT_OPTIONAL_LOCKS':'0'}
SOURCES = {'birth-clone-statics': '<?php\n'
                        'class A { const Closure F=static function() { static $n=0; echo ++$n; }; }\n'
                        'class B extends A {}\n'
                        '$f=A::F; $g=B::F;\n'
                        '$f(); $g();\n'
                        '$h=clone $f;\n'
                        '$h(); $f(); $h(); $g();\n',
 'alias-array-flow': '<?php\n'
                     'class A {\n'
                     '    const F = static function() { echo "A"; };\n'
                     '    const array X = [static function() { echo "B"; }, static function() { echo '
                     '"C"; }];\n'
                     '}\n'
                     'class B extends A {\n'
                     '    const G = parent::F;\n'
                     '    const array Y = [parent::F, self::G];\n'
                     '}\n'
                     '$f=A::F; $g=B::G; $x=A::X; $y=B::Y;\n'
                     'echo ($f === $g && $y[0] === $f && $y[1] === $f) ? "same:" : "bad:";\n'
                     'echo ($x[0] !== $x[1]) ? "distinct:" : "bad:";\n'
                     '$x[0]=$x[1];\n'
                     '($x[0])(); echo ":";\n'
                     '(A::X[0])(); (A::X[1])(); $g();\n',
 'fixed-retry-prefix': '<?php\n'
                       'namespace { function f() { echo "G"; } }\n'
                       'namespace N {\n'
                       'class A { const array X=[f(...),LATE]; }\n'
                       'try { $v=A::X; } catch (\\Error $e) { echo "retry:"; }\n'
                       'if (true) { function f() { echo "L"; } }\n'
                       'const LATE=1;\n'
                       '$v=A::X; $w=A::X;\n'
                       'echo $v[1], ":";\n'
                       '($v[0])(); ($w[0])(); echo ":";\n'
                       '$fresh=f(...); $fresh();\n'
                       '}\n',
 'method-owner-called': '<?php\n'
                        'class A { public static function f() { return self::class . ":" . '
                        'static::class; } }\n'
                        'class B extends A { const Closure F=B::f(...); }\n'
                        'class C extends B {}\n'
                        '$f=C::F; $g=B::F; $h=clone $f;\n'
                        'echo ($f === $g) ? "same:" : "bad:";\n'
                        'echo $f(), ":", $h();\n',
 'literal-class-owner': ('<?php\n'
 'namespace {\n'
 'class A { public static function f() { return self::class . ":" . static::class; } }\n'
 'class B extends A {}\n'
 '}\n'
 'namespace N {\n'
 'class A { public static function f() { return "wrong"; } }\n'
 'class B extends A {}\n'
 "class C { const \\Closure F=('B')::f(...); const \\Closure G=('\\B')::f(...); }\n"
 'class D extends C {}\n'
 '$f=C::F; $g=D::F; $h=clone $f; $q=C::G;\n'
 'echo ($f === $g) ? "same:" : "bad:";\n'
 'echo $f(), ":", $h(), ":", $q();\n'
 '}\n')}
PREFIX = ('dec $constant_callable_test_cache_set(pdefaultcache*, porigin, pdefaultcache) : pdefaultcache*\n'
 'def $constant_callable_test_cache_set(eps, porigin, pdefaultcache_new) = eps\n'
 'def $constant_callable_test_cache_set(pdefaultcache :: pdefaultcache_tail*, porigin, '
 'pdefaultcache_new) = pdefaultcache_new :: pdefaultcache_tail*\n'
 '  -- if pdefaultcache.ORIGIN = porigin\n'
 'def $constant_callable_test_cache_set(pdefaultcache :: pdefaultcache_tail*, porigin, '
 'pdefaultcache_new) = pdefaultcache :: $constant_callable_test_cache_set(pdefaultcache_tail*, porigin, '
 'pdefaultcache_new)\n'
 '  -- if pdefaultcache.ORIGIN =/= porigin\n'
 'dec $constant_callable_test_plain(pobject*, nat) : pobject*\n'
 'def $constant_callable_test_plain(pobject :: pobject_tail*, 0) = $object_body(pobject) :: '
 'pobject_tail*\n'
 'def $constant_callable_test_plain(pobject :: pobject_tail*, n) = pobject :: '
 '$constant_callable_test_plain(pobject_tail*, $nabs($(n - 1)))\n'
 '  -- if $(n > 0)\n')
CHECKS = {'birth-clone-statics': ['S = $drive_steps(S_initial[.COMPLETION = NORMAL], 1600)',
                         'S.COMPLETION = NORMAL',
                         'S.TODO = eps',
                         '$class_constant_state_valid(S)',
                         '$constant_callable_records_valid(S, S.CONSTANTCLOSURES)',
                         '$class_named(S.CLASSNAMES, $ptascii("a")) = (porigin_a)',
                         '$class_named(S.CLASSNAMES, $ptascii("b")) = (porigin_b)',
                         '$class_constant_lookup(S, porigin_a, $ptascii("F"), |S.CLASSES|) = '
                         '(pclassconstantdesc)',
                         '$default_cache_at(S.CLASSCONSTANTCACHE, pclassconstantdesc.ORIGIN) = '
                         '(pdefaultcache)',
                         'pdefaultcache.VALUE = POBJECT n_original',
                         'pdefaultcache.CLASS = PVCLOSURE n_original porigin_site',
                         '$constant_callable_record(S.CONSTANTCLOSURES, n_original) = '
                         '(pconstantclosure)',
                         'S.OBJECTS[n_original] = CONSTANTCLOSURE porigin_site (REALCLOSURE '
                         'porigin_site eps ([pstaticcell]))',
                         'S.STORE[pstaticcell.CELL] = DEFINED (PINT 4)',
                         'HCELL pstaticcell.CELL <- $node_children(S, HOBJECT n_original)',
                         '$closure_scope_at(S.CLOSURESCOPES, n_original) = (pclosurescope)',
                         'pclosurescope.LEXICAL = porigin_a /\\ pclosurescope.CALLED = porigin_a',
                         'S_global = $global_table_view(S)',
                         '$lookup(S_global.ENV, $ptascii("h")) = (n_cell)',
                         'S.STORE[n_cell] = DEFINED (POBJECT n_clone)',
                         'S.OBJECTS[n_clone] = REALCLOSURE porigin_site eps ([pstaticcell_clone])',
                         'n_clone =/= n_original /\\ pstaticcell_clone.CELL =/= pstaticcell.CELL',
                         'S.STORE[pstaticcell_clone.CELL] = DEFINED (PINT 4)',
                         '$closure_callable(S, n_original) /\\ $closure_callable(S, n_clone)',
                         '~$constant_callable_record_valid(S, pconstantclosure[.OBJECT = n_clone])',
                         'S_forged = S[.CLASSCONSTANTCACHE = '
                         '$constant_callable_test_cache_set(S.CLASSCONSTANTCACHE, '
                         'pclassconstantdesc.ORIGIN, pdefaultcache[.VALUE = POBJECT n_clone][.CLASS = '
                         'PVCLOSURE n_clone porigin_site])][.CONSTANTCLOSURES = S.CONSTANTCLOSURES ++ '
                         '[pconstantclosure[.OBJECT = n_clone]]]',
                         'S_forged.OBJECTS = S.OBJECTS',
                         '~$class_constant_caches_valid(S_forged, S_forged.CLASSCONSTANTCACHE)',
                         '~$constant_callable_records_valid(S_forged, S_forged.CONSTANTCLOSURES)',
                         '~$constant_callable_record_valid(S, pconstantclosure[.SITE = PORIGIN 999 '
                         'eps])',
                         '~$constant_callable_record_valid(S, pconstantclosure[.DECL = porigin_b])',
                         'S_wrong_scope = S[.CLOSURESCOPES = [pclosurescope[.LEXICAL = porigin_b]]]',
                         '~$constant_callable_record_valid(S_wrong_scope, pconstantclosure)',
                         'S_wrong_called = S[.CLOSURESCOPES = [pclosurescope[.CALLED = porigin_b]]]',
                         '~$constant_callable_record_valid(S_wrong_called, pconstantclosure)',
                         'S_wrong_receiver = S[.CLOSURESCOPES = [pclosurescope[.RECEIVER = (n_clone)]]]',
                         '~$constant_callable_record_valid(S_wrong_receiver, pconstantclosure)',
                         'S_cache_only = $prune_allocations(S[.ENV = eps][.GLOBALTABLE = eps][.RESULT = '
                         'KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)])',
                         'HOBJECT n_original <- S_cache_only.ALLOCATIONS',
                         'HCELL pstaticcell.CELL <- S_cache_only.ALLOCATIONS',
                         '$constant_callable_record_valid(S_cache_only, pconstantclosure)',
                         '~$constant_callable_records_valid(S[.CONSTANTCLOSURES = eps], eps)',
                         'S_plain = S[.OBJECTS = $constant_callable_test_plain(S.OBJECTS, n_original)]',
                         'S_plain.OBJECTS[n_original] = REALCLOSURE porigin_site eps ([pstaticcell])',
                         '~$constant_callable_record_valid(S_plain, pconstantclosure)',
                         '~$constant_callable_records_valid(S_plain, S_plain.CONSTANTCLOSURES)',
                         'S_pruned = $prune_allocations(S[.ENV = eps][.GLOBALTABLE = '
                         'eps][.CLASSCONSTANTCACHE = eps][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE '
                         '(KNOWN PNULL)])',
                         '~(HOBJECT n_original <- S_pruned.ALLOCATIONS)',
                         'S_pruned.CONSTANTCLOSURES = S.CONSTANTCLOSURES',
                         '$constant_callable_record_valid(S_pruned, pconstantclosure)',
                         '~$constant_callable_value_valid(S_pruned, n_original, porigin_site)',
                         '~$constant_callable_records_valid(S[.OBJECTS = $object_set(S.OBJECTS, '
                         'n_original, CONSTANTCLOSURE porigin_site (CONSTANTCLOSURE porigin_site '
                         '(REALCLOSURE porigin_site eps ([pstaticcell]))))], S.CONSTANTCLOSURES)',
                         '~$constant_callable_records_valid(S[.OBJECTS = $object_set(S.OBJECTS, '
                         'n_original, CONSTANTCLOSURE porigin_site STDINSTANCE)], S.CONSTANTCLOSURES)'],
 'alias-array-flow': ['S = $drive_steps(S_initial[.COMPLETION = NORMAL], 1600)',
                      'S.COMPLETION = NORMAL',
                      'S.TODO = eps',
                      '$class_constant_state_valid(S)',
                      '$constant_callable_records_valid(S, S.CONSTANTCLOSURES)',
                      '$class_named(S.CLASSNAMES, $ptascii("a")) = (porigin_a)',
                      '$class_named(S.CLASSNAMES, $ptascii("b")) = (porigin_b)',
                      '$class_constant_lookup(S, porigin_a, $ptascii("F"), |S.CLASSES|) = '
                      '(pclassconstantdesc_f)',
                      '$class_constant_lookup(S, porigin_a, $ptascii("X"), |S.CLASSES|) = '
                      '(pclassconstantdesc_x)',
                      '$class_constant_lookup(S, porigin_b, $ptascii("G"), |S.CLASSES|) = '
                      '(pclassconstantdesc_g)',
                      '$class_constant_lookup(S, porigin_b, $ptascii("Y"), |S.CLASSES|) = '
                      '(pclassconstantdesc_y)',
                      'pclassconstantdesc_f.TYPE = eps /\\ pclassconstantdesc_g.TYPE = eps',
                      '$default_cache_at(S.CLASSCONSTANTCACHE, pclassconstantdesc_f.ORIGIN) = '
                      '(pdefaultcache_f)',
                      '$default_cache_at(S.CLASSCONSTANTCACHE, pclassconstantdesc_g.ORIGIN) = '
                      '(pdefaultcache_g)',
                      'pdefaultcache_f.VALUE = pdefaultcache_g.VALUE /\\ pdefaultcache_f.CLASS = '
                      'pdefaultcache_g.CLASS',
                      '$default_cache_at(S.CLASSCONSTANTCACHE, pclassconstantdesc_x.ORIGIN) = '
                      '(pdefaultcache_x)',
                      '$default_cache_at(S.CLASSCONSTANTCACHE, pclassconstantdesc_y.ORIGIN) = '
                      '(pdefaultcache_y)',
                      'pdefaultcache_x.VALUE = PARRAY n_x',
                      'pdefaultcache_x.CLASS = PVARRAY b ([(KINT 0, PVCLOSURE n_first porigin_first), '
                      '(KINT 1, PVCLOSURE n_second porigin_second)])',
                      'n_first =/= n_second /\\ porigin_first =/= porigin_second',
                      'S.ARRAYS[n_x].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_first)), ENTRY (KINT 1) '
                      '(DIRECT (POBJECT n_second))]',
                      '$constant_callable_cache_prefix(S.CLASSCONSTANTHISTORY, '
                      'pclassconstantdesc_f.ORIGIN) = (n_prefix_f)',
                      '$constant_callable_cache_prefix(S.CLASSCONSTANTHISTORY, '
                      'pclassconstantdesc_g.ORIGIN) = (n_prefix_g)',
                      '$constant_callable_cache_prefix(S.CLASSCONSTANTHISTORY, '
                      'pclassconstantdesc_x.ORIGIN) = (n_prefix_x)',
                      '$constant_callable_cache_prefix(S.CLASSCONSTANTHISTORY, '
                      'pclassconstantdesc_y.ORIGIN) = (n_prefix_y)',
                      '$constant_callable_cache_valid(S, pclassconstantdesc_y, pdefaultcache_y.CLASS, '
                      'n_prefix_y)',
                      '$constant_callable_foldable(PVARRAY b ([(KINT 0, PVSCALAR), (KINT 1, '
                      'PVSCALAR)]))',
                      '~$constant_callable_foldable(pdefaultcache_x.CLASS)',
                      '~$constant_callable_foldable(pdefaultcache_f.CLASS)',
                      '~$constant_callable_cache_valid(S, pclassconstantdesc_f, PVSCALAR, n_prefix_f)',
                      'pdefaultcache_f_erased = pdefaultcache_f[.VALUE = PINT 1][.CLASS = PVSCALAR]',
                      'pdefaultcache_g_erased = pdefaultcache_g[.VALUE = PINT 1][.CLASS = PVSCALAR]',
                      'S_erased = S[.CLASSCONSTANTCACHE = '
                      '$constant_callable_test_cache_set($constant_callable_test_cache_set(S.CLASSCONSTANTCACHE, '
                      'pclassconstantdesc_f.ORIGIN, pdefaultcache_f_erased), '
                      'pclassconstantdesc_g.ORIGIN, pdefaultcache_g_erased)]',
                      '$class_constant_runtime_type(S_erased, pclassconstantdesc_f.TYPE, PINT 1)',
                      '$constant_value_class_valid(S_erased, PINT 1, PVSCALAR)',
                      '~$constant_callable_cache_valid(S_erased, pclassconstantdesc_g, PVSCALAR, '
                      'n_prefix_g)',
                      '~$class_constant_caches_valid(S_erased, S_erased.CLASSCONSTANTCACHE)',
                      'pvalueclass_swapped = PVARRAY b ([(KINT 0, PVCLOSURE n_second porigin_second), '
                      '(KINT 1, PVCLOSURE n_first porigin_first)])',
                      'S_swapped = S[.ARRAYS = $array_replace(S.ARRAYS, n_x, S.ARRAYS[n_x][.ITEMS = '
                      '[ENTRY (KINT 0) (DIRECT (POBJECT n_second)), ENTRY (KINT 1) (DIRECT (POBJECT '
                      'n_first))]])][.CLASSCONSTANTCACHE = '
                      '$constant_callable_test_cache_set(S.CLASSCONSTANTCACHE, '
                      'pclassconstantdesc_x.ORIGIN, pdefaultcache_x[.CLASS = pvalueclass_swapped])]',
                      '$constant_value_class_valid(S_swapped, PARRAY n_x, pvalueclass_swapped)',
                      '~$constant_callable_cache_valid(S_swapped, pclassconstantdesc_x, '
                      'pvalueclass_swapped, n_prefix_x)',
                      'pvalueclass_erased = PVARRAY b ([(KINT 0, PVSCALAR), (KINT 1, PVSCALAR)])',
                      'S_array_erased = S[.ARRAYS = $array_replace(S.ARRAYS, n_x, S.ARRAYS[n_x][.ITEMS '
                      '= [ENTRY (KINT 0) (DIRECT (PINT 1)), ENTRY (KINT 1) (DIRECT (PINT '
                      '2))]])][.CLASSCONSTANTCACHE = '
                      '$constant_callable_test_cache_set(S.CLASSCONSTANTCACHE, '
                      'pclassconstantdesc_x.ORIGIN, pdefaultcache_x[.CLASS = pvalueclass_erased])]',
                      '$constant_value_class_valid(S_array_erased, PARRAY n_x, pvalueclass_erased)',
                      '$class_constant_runtime_type(S_array_erased, pclassconstantdesc_x.TYPE, PARRAY '
                      'n_x)',
                      '~$constant_callable_cache_valid(S_array_erased, pclassconstantdesc_x, '
                      'pvalueclass_erased, n_prefix_x)',
                      '~$class_constant_caches_valid(S_array_erased, '
                      'S_array_erased.CLASSCONSTANTCACHE)'],
 'fixed-retry-prefix': ['S = $drive_steps(S_initial[.COMPLETION = NORMAL], 1600)',
                        'S.COMPLETION = NORMAL',
                        'S.TODO = eps',
                        '$class_constant_state_valid(S)',
                        '$constant_callable_records_valid(S, S.CONSTANTCLOSURES)',
                        '$class_named(S.CLASSNAMES, $ptascii("n\\\\a")) = (porigin_a)',
                        '$class_constant_lookup(S, porigin_a, $ptascii("X"), |S.CLASSES|) = '
                        '(pclassconstantdesc)',
                        '$default_cache_at(S.CLASSCONSTANTCACHE, pclassconstantdesc.ORIGIN) = '
                        '(pdefaultcache)',
                        'pdefaultcache.CLASS = PVARRAY b ([(KINT 0, PVCLOSURE n_original porigin_site), '
                        '(KINT 1, PVSCALAR)])',
                        '$constant_callable_first(S.CONSTANTCLOSURES, porigin_site) = '
                        '(pconstantclosure_first)',
                        '$constant_callable_record(S.CONSTANTCLOSURES, n_original) = (pconstantclosure)',
                        'pconstantclosure_first.OBJECT =/= n_original',
                        '~(HOBJECT pconstantclosure_first.OBJECT <- S.ALLOCATIONS)',
                        'pconstantclosure.PREFIX = pconstantclosure_first.PREFIX',
                        '$constant_callable_record_valid(S, pconstantclosure_first)',
                        '$constant_callable_function(S, porigin_site, pconstantclosure.PREFIX) = '
                        '(pfunction_early)',
                        'n_late = |S.DECLARATIONS|',
                        '$constant_callable_function(S, porigin_site, n_late) = (pfunction_late)',
                        'pfunction_early.ORIGIN =/= pfunction_late.ORIGIN',
                        'S.OBJECTS[n_original] = CONSTANTCLOSURE porigin_site (NAMEDCLOSURE '
                        'pfunction_early.ORIGIN)',
                        'S_forged = S[.OBJECTS = $object_set(S.OBJECTS, n_original, CONSTANTCLOSURE '
                        'porigin_site (NAMEDCLOSURE pfunction_late.ORIGIN))][.CONSTANTCLOSURES = '
                        '[pconstantclosure_first, pconstantclosure[.PREFIX = n_late]]]',
                        '~$constant_callable_record_valid(S_forged, pconstantclosure[.PREFIX = n_late])',
                        '~$constant_callable_records_valid(S_forged, S_forged.CONSTANTCLOSURES)',
                        '$constant_callable_cache_prefix(S.CLASSCONSTANTHISTORY, '
                        'pclassconstantdesc.ORIGIN) = (n_cache)',
                        '~$constant_callable_cache_valid(S, pclassconstantdesc, pdefaultcache.CLASS, '
                        '$nabs($(pconstantclosure.PREFIX - 1)))',
                        'S_pruned = $prune_allocations(S[.ENV = eps][.GLOBALTABLE = '
                        'eps][.CLASSCONSTANTCACHE = eps][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE '
                        '(KNOWN PNULL)])',
                        'S_pruned.CONSTANTCLOSURES = S.CONSTANTCLOSURES',
                        '~(HOBJECT n_original <- S_pruned.ALLOCATIONS)',
                        '$constant_callable_record_valid(S_pruned, pconstantclosure_first)',
                        '$constant_callable_record_valid(S_pruned, pconstantclosure)'],
 'method-owner-called': ['S = $drive_steps(S_initial[.COMPLETION = NORMAL], 1600)',
                         'S.COMPLETION = NORMAL',
                         'S.TODO = eps',
                         '$class_constant_state_valid(S)',
                         '$constant_callable_records_valid(S, S.CONSTANTCLOSURES)',
                         '$class_named(S.CLASSNAMES, $ptascii("a")) = (porigin_a)',
                         '$class_named(S.CLASSNAMES, $ptascii("b")) = (porigin_b)',
                         '$class_constant_lookup(S, porigin_b, $ptascii("F"), |S.CLASSES|) = '
                         '(pclassconstantdesc)',
                         '$default_cache_at(S.CLASSCONSTANTCACHE, pclassconstantdesc.ORIGIN) = '
                         '(pdefaultcache)',
                         'pdefaultcache.CLASS = PVCLOSURE n_original porigin_site',
                         '$constant_callable_record(S.CONSTANTCLOSURES, n_original) = '
                         '(pconstantclosure)',
                         'S.OBJECTS[n_original] = CONSTANTCLOSURE porigin_site (METHODCLOSURE '
                         'porigin_method porigin_site porigin_b eps)',
                         '$class_method_origin(S.CLASSES, porigin_method) = (pmethoddesc)',
                         'pmethoddesc.OWNER = porigin_a',
                         '$closure_scope_at(S.CLOSURESCOPES, n_original) = (pclosurescope)',
                         'pclosurescope.LEXICAL = porigin_a /\\ pclosurescope.CALLED = porigin_b',
                         '~$constant_callable_record_valid(S[.CLOSURESCOPES = [pclosurescope[.LEXICAL = '
                         'porigin_b]]], pconstantclosure)',
                         '~$constant_callable_record_valid(S[.CLOSURESCOPES = [pclosurescope[.CALLED = '
                         'porigin_a]]], pconstantclosure)',
                         '~$constant_callable_record_valid(S[.CLOSURESCOPES = [pclosurescope[.RECEIVER '
                         '= (n_original)]]], pconstantclosure)',
                         'S_global = $global_table_view(S)',
                         '$lookup(S_global.ENV, $ptascii("h")) = (n_cell)',
                         'S.STORE[n_cell] = DEFINED (POBJECT n_clone)',
                         'S.OBJECTS[n_clone] = METHODCLOSURE porigin_method porigin_site porigin_b eps',
                         '$closure_callable(S, n_clone)',
                         '~$constant_callable_record_valid(S, pconstantclosure[.OBJECT = n_clone])'],
 'literal-class-owner': ['S = $drive_steps(S_initial[.COMPLETION = NORMAL], 1600)',
 'S.COMPLETION = NORMAL',
 'S.TODO = eps',
 '$class_constant_state_valid(S)',
 '$constant_callable_records_valid(S, S.CONSTANTCLOSURES)',
 '$class_named(S.CLASSNAMES, $ptascii("a")) = (porigin_a)',
 '$class_named(S.CLASSNAMES, $ptascii("b")) = (porigin_b)',
 '$class_named(S.CLASSNAMES, $ptascii("n") ++ [92] ++ $ptascii("c")) = (porigin_c)',
 '$class_constant_lookup(S, porigin_c, $ptascii("F"), |S.CLASSES|) = (pclassconstantdesc)',
 '$default_cache_at(S.CLASSCONSTANTCACHE, pclassconstantdesc.ORIGIN) = (pdefaultcache)',
 'pdefaultcache.CLASS = PVCLOSURE n_original porigin_site',
 '$constant_callable_record(S.CONSTANTCLOSURES, n_original) = (pconstantclosure)',
 'S.OBJECTS[n_original] = CONSTANTCLOSURE porigin_site (METHODCLOSURE porigin_method porigin_site '
 'porigin_b eps)',
 '$class_method_origin(S.CLASSES, porigin_method) = (pmethoddesc)',
 'pmethoddesc.OWNER = porigin_a',
 '$closure_scope_at(S.CLOSURESCOPES, n_original) = (pclosurescope)',
 'pclosurescope.LEXICAL = porigin_a /\\ pclosurescope.CALLED = porigin_b',
 '~$constant_callable_record_valid(S[.CLOSURESCOPES = [pclosurescope[.LEXICAL = porigin_b]]], '
 'pconstantclosure)',
 '~$constant_callable_record_valid(S[.CLOSURESCOPES = [pclosurescope[.CALLED = porigin_a]]], '
 'pconstantclosure)',
 '~$constant_callable_record_valid(S[.CLOSURESCOPES = [pclosurescope[.RECEIVER = (n_original)]]], '
 'pconstantclosure)',
 'S_global = $global_table_view(S)',
 '$lookup(S_global.ENV, $ptascii("h")) = (n_cell)',
 'S.STORE[n_cell] = DEFINED (POBJECT n_clone)',
 'S.OBJECTS[n_clone] = METHODCLOSURE porigin_method porigin_site porigin_b eps',
 '$closure_callable(S, n_clone)',
 '~$constant_callable_record_valid(S, pconstantclosure[.OBJECT = n_clone])',
 'S.EVENTS = [(OUTPUT $ptascii("same:")), (OUTPUT $ptascii("A:B")), (OUTPUT $ptascii(":")), '
 '(OUTPUT $ptascii("A:B")), (OUTPUT $ptascii(":")), (OUTPUT $ptascii("A:B"))]',
 '$class_named(S.CLASSNAMES, $ptascii("n") ++ [92] ++ $ptascii("b")) = (porigin_shadow)',
 '$effective_method(S, porigin_shadow, $ptascii("f"), |S.CLASSES|) = (pmethoddesc_shadow)',
 'S_shadow = S[.OBJECTS = $object_set(S.OBJECTS, n_original, CONSTANTCLOSURE porigin_site '
 '(METHODCLOSURE pmethoddesc_shadow.FUNCTION.ORIGIN porigin_site porigin_shadow '
 'eps))][.CLOSURESCOPES = [pclosurescope[.LEXICAL = pmethoddesc_shadow.OWNER][.CALLED = '
 'porigin_shadow]]]',
 '~$constant_callable_record_valid(S_shadow, pconstantclosure)',
 '$origin_node(S.SOURCES, porigin_site) = (NExprStaticCall phpType19 phpType20 phpType6 metadata)',
 '$constant_callable_literal_class(phpType19) = ($ptascii("B"))',
 '$constant_callable_class_name(S, porigin_site, porigin_c, phpType19) = ($ptascii("B"))',
 '$class_constant_lookup(S, porigin_c, $ptascii("G"), |S.CLASSES|) = (pclassconstantdesc_g)',
 '$default_cache_at(S.CLASSCONSTANTCACHE, pclassconstantdesc_g.ORIGIN) = (pdefaultcache_g)',
 'pdefaultcache_g.CLASS = PVCLOSURE n_g porigin_site_g',
 'n_g =/= n_original',
 '$origin_node(S.SOURCES, porigin_site_g) = (NExprStaticCall phpType19_g phpType20_g phpType6_g '
 'metadata_g)',
 '$constant_callable_literal_class(phpType19_g) = ($ptascii("B"))',
 '$constant_callable_class_name(S, porigin_site_g, porigin_c, phpType19_g) = ($ptascii("B"))',
 '$constant_callable_record(S.CONSTANTCLOSURES, n_g) = (pconstantclosure_g)',
 '$constant_callable_record_valid(S, pconstantclosure_g)']}

SOURCES.update({'folded-spelling': '<?php\n'
                    'namespace N;\n'
                    'use Vendor\\MiXeD as Alias;\n'
                    'use Vendor\\Pkg as Pkg;\n'
                    'class CaseClass {}\n'
                    'const X = [Alias::class, aLiAs::CLASS, pkg\\Thing::class, '
                    'namespace\\Local::class, \\Root\\Missing::class, missing::class, '
                    'cAsEcLaSs::class];\n'
                    'echo X[0], "|", X[1], "|", X[2], "|", X[3], "|", X[4], "|", X[5], '
                    '"|", X[6];\n',
 'contextual-default': '<?php\n'
                       'class A { const Closure F = static function($x = self::class) { '
                       'echo $x; }; }\n'
                       'class B extends A {}\n'
                       '$f = A::F;\n'
                       '$f();\n'
                       '$g = $f->bindTo(null, B::class);\n'
                       '$g();\n'
                       '$f();\n'
                       'echo (A::F === $f) ? ":same" : ":bad";\n'})

PREFIX += '\ndec $classname_test_constant_replace(pconstant*, pcpath, pvalue) : pconstant*\ndef $classname_test_constant_replace(eps, pcpath, pvalue) = eps\ndef $classname_test_constant_replace((PCONSTANT pcpath pvalue_old) :: pconstant*, pcpath, pvalue) = (PCONSTANT pcpath pvalue) :: pconstant*\ndef $classname_test_constant_replace((PCONSTANT pcpath_old pvalue_old) :: pconstant_tail*, pcpath, pvalue) = (PCONSTANT pcpath_old pvalue_old) :: $classname_test_constant_replace(pconstant_tail*, pcpath, pvalue)\n  -- if pcpath_old =/= pcpath\n'

CHECKS.update({'folded-spelling': ['S = $drive_steps(S_initial[.COMPLETION = NORMAL], 1200)',
                     'S.COMPLETION = NORMAL /\\ S.TODO = eps',
                     '$declaration_history_valid(S)',
                     '$source_unit(S.SOURCES, 0) = (pcunit)',
                     'P = $declaration_compiler_state($eval_source_ppstate(S, pcunit))',
                     'P.COMPLETION = PPCNORMAL',
                     '$compilation_image_valid(S, pcunit, P)',
                     '$user_constant_at(S.USERCONSTANTS, $ptascii("n") ++ [92] ++ $ptascii("X")) = '
                     '(puserconstant)',
                     '$constant_expression_root(S, puserconstant.ORIGIN) = (PORIGIN 0 pcpath_root)',
                     '$pool_value(S.POOLS, PORIGIN 0 pcpath_root) = (PARRAY n_array)',
                     'pcpath_leaf = pcpath_root ++ [PCFIELD 0, PCINDEX 0, PCFIELD 1]',
                     '$origin_node(S.SOURCES, PORIGIN 0 pcpath_leaf) = (NExprClassConstFetch phpType19 '
                     'phpType20 metadata)',
                     '$pfclassname_member(phpType20)',
                     '$pool_value(S.POOLS, PORIGIN 0 pcpath_leaf) = (PSTRING ($ptascii("Vendor") ++ [92] '
                     '++ $ptascii("MiXeD")))',
                     '$pool_class(S.POOLS, PORIGIN 0 pcpath_leaf) = (PVSTRING true)',
                     'S.POOLS = [ppool]',
                     'ppool_bad = ppool[.CONSTANTS = $classname_test_constant_replace(ppool.CONSTANTS, '
                     'pcpath_leaf, PSTRING ($ptascii("vendor") ++ [92] ++ $ptascii("mixed")))]',
                     'S_bad = S[.POOLS = [ppool_bad]][.ARRAYS = $array_replace(S.ARRAYS, n_array, '
                     '$array_insert(S.ARRAYS[n_array], KINT 0, DIRECT (PSTRING ($ptascii("vendor") ++ [92] '
                     '++ $ptascii("mixed")))))]',
                     'S_bad.SOURCES = S.SOURCES /\\ S_bad.CODE = S.CODE /\\ S_bad.CLASSES = S.CLASSES',
                     '$pool_value(S_bad.POOLS, PORIGIN 0 pcpath_leaf) = (PSTRING ($ptascii("vendor") ++ '
                     '[92] ++ $ptascii("mixed")))',
                     '$pool_class(S_bad.POOLS, PORIGIN 0 pcpath_leaf) = (PVSTRING true)',
                     '$constant_pool_values_valid(S_bad, ppool_bad.CONSTANTS, ppool_bad.CONSTANTS)',
                     '~$compilation_image_valid(S_bad, pcunit, P)',
                     '~$declaration_history_valid(S_bad)'],
 'contextual-default': ['S = $drive_steps(S_initial[.COMPLETION = NORMAL], 1200)',
                        'S.COMPLETION = NORMAL /\\ S.TODO = eps',
                        'S.EVENTS = [OUTPUT $ptascii("A"), OUTPUT $ptascii("B"), OUTPUT $ptascii("A"), '
                        'OUTPUT $ptascii(":same")]',
                        '$class_constant_state_valid(S)',
                        '$closure_state_valid(S)',
                        '$call_descriptors_valid(S)',
                        'S.CLOSURETEMPLATES = [pfunction]',
                        'pfunction.DEFAULTS = [pdefault]',
                        'pdefault.KIND = PDDEFERRED',
                        '$compiled_read(S, pdefault.ORIGIN) = eps',
                        '$default_scope_dependent(S, pdefault.ORIGIN)',
                        'S.DEFAULTCACHE = eps',
                        '$default_cache_value(S, pdefault.ORIGIN, PSTRING $ptascii("A"), PVSTRING true) = '
                        'S',
                        '$class_named(S.CLASSNAMES, $ptascii("a")) = (porigin_a)',
                        '$class_named(S.CLASSNAMES, $ptascii("b")) = (porigin_b)',
                        'S_global = $global_table_view(S)',
                        '$lookup(S_global.ENV, $ptascii("f")) = (n_f_cell)',
                        '$lookup(S_global.ENV, $ptascii("g")) = (n_g_cell)',
                        'S.STORE[n_f_cell] = DEFINED (POBJECT n_f)',
                        'S.STORE[n_g_cell] = DEFINED (POBJECT n_g)',
                        'n_f =/= n_g',
                        '$closure_scope_at(S.CLOSURESCOPES, n_f) = (pclosurescope_f)',
                        '$closure_binding_at(S.CLOSUREBINDINGS, n_g) = (pclosurebinding_g)',
                        'pclosurescope_f.LEXICAL = porigin_a /\\ pclosurebinding_g.LEXICAL = (porigin_b)',
                        '$class_constant_lookup(S, porigin_a, $ptascii("F"), |S.CLASSES|) = '
                        '(pclassconstantdesc)',
                        '$default_cache_at(S.CLASSCONSTANTCACHE, pclassconstantdesc.ORIGIN) = '
                        '(pdefaultcache_constant)',
                        'pdefaultcache_constant.VALUE = POBJECT n_f',
                        'pdefaultcache_bad = {ORIGIN pdefault.ORIGIN, VALUE PSTRING $ptascii("A"), CLASS '
                        'PVSTRING true}',
                        '$default_cacheable(pdefaultcache_bad.CLASS)',
                        '$constant_value_class_valid(S, pdefaultcache_bad.VALUE, pdefaultcache_bad.CLASS)',
                        'S_bad = S[.DEFAULTCACHE = [pdefaultcache_bad]]',
                        'S_bad.CLOSURETEMPLATES = S.CLOSURETEMPLATES /\\ S_bad.CLOSURESCOPES = '
                        'S.CLOSURESCOPES',
                        '~$default_caches_valid(S_bad, S_bad.DEFAULTCACHE)',
                        '~$call_descriptors_valid(S_bad)',
                        'S.CLOSURESCOPES = [pclosurescope_f] /\\ S.CLOSUREBINDINGS = [pclosurebinding_g]',
                        'S_wrong_scope = S[.CLOSUREBINDINGS = [pclosurebinding_g[.LEXICAL = (porigin_a)]]]',
                        '~$closure_state_valid(S_wrong_scope)']})

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def prepare(out):
 out=Path(out).resolve();out.mkdir(parents=True,exist_ok=False)
 types.ENV=ENV
 frontend=adapter=None
 records=[]
 def worker(command,name):
  w=Worker(command,out/name)
  (out/name/'launch.json').write_text(json.dumps({'supplied_argv':command,'supplied_cwd':os.getcwd(),'supplied_environment':ENV,'popen_args':w.p.args,'pid':w.p.pid},indent=2)+'\n')
  return w
 try:
  frontend=worker([str(types.PHP),'-n',*types.FLAGS,'-d','extension='+str(ROOT/'.tools/php-file.so'),str(ROOT/'frontend/worker.php')],'frontend')
  adapter=worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)],'adapter')
  for case,source in SOURCES.items():
   path=out/(case+'.php');path.write_bytes(source.encode())
   parsed=frontend.request({'op':'parse','source':base64.b64encode(path.read_bytes()).decode()});assert parsed['accepted'],parsed
   checked=adapter.request({'op':'check','ast':parsed['ast'],'fixture':True});assert checked['ok'],checked
   (out/(case+'.checked.json')).write_text(json.dumps(checked,indent=2)+'\n')
   conditions=['S_initial = $php_run('+checked['fixture']+', 0, '+json.dumps(base64.b64encode(bytes(path)).decode())+')',*CHECKS[case]]
   fixture=out/(case+'.watsup');fixture.write_text(PREFIX+'\ndec $main() : bool\ndef $main() = true\n'+''.join('  -- if '+c+'\n' for c in conditions))
   records.append({'id':case,'source':str(path),'source_sha256':sha(path),'fixture':str(fixture),'fixture_sha256':sha(fixture),'main_predicates':len(conditions)})
 finally:
  try:
   if frontend:frontend.close()
  finally:
   if adapter:adapter.close()
 (out/'prepared.json').write_text(json.dumps({'scope':'Pure checked source/fixture preparation only; numeric state programs UNRUN.','root':str(ROOT),'records':records},indent=2)+'\n')
 print(out)
 return records

def run():
 interrupted=None;cleaning=False
 def terminate(signum,frame):
  nonlocal interrupted
  interrupted=signum
  if not cleaning:raise RuntimeError('interrupted by signal '+str(signum))
 previous_term=signal.signal(signal.SIGTERM,terminate)
 modules=[ROOT/name for name in json.loads((ROOT/'spec/semantics/modules.json').read_text())]
 runner=ROOT/'tests/semantics/_build/default/numeric_runner.exe'
 fingerprint=types.syntax_validation.implementation_fingerprint()
 watched=[*modules,runner,types.PHP,ROOT/'_build/default/adapter/main.exe',
  ROOT/'spec/semantics/modules.json',Path(__file__),ROOT/'tests/semantics/recorded_worker.py',
  ROOT/'tests/semantics/method_runtime.py',ROOT/'frontend/worker.php',ROOT/'.tools/php-file.so']
 before={str(p.relative_to(ROOT)):sha(p) for p in watched}
 def stable():
  return fingerprint==types.syntax_validation.implementation_fingerprint() and all(sha(ROOT/name)==digest for name,digest in before.items())
 out=Path(tempfile.mkdtemp(prefix='constant-callable-protocol-',dir=ROOT/'.tools'))
 records=[];fixtures=[];failure=None
 try:
  fixtures=prepare(out/'fixtures')
  for row in fixtures:
   assert stable(),'class-constant inputs changed before case'
   assert sha(row['source'])==row['source_sha256'] and sha(row['fixture'])==row['fixture_sha256'],'prepared input changed'
   raw=out/row['id'];raw.mkdir()
   command=[str(runner),*map(str,modules),row['fixture']]
   facts={'supplied_argv':command,'supplied_cwd':str(ROOT),'supplied_environment':ENV,
    'host_timeout_seconds':120,'observed_exit':None,'cleanup_exit':None,'status':'prepared'}
   def save():
    (raw/'command.json').write_text(json.dumps(facts,indent=2)+'\n')
   save();process=None
   with (raw/'stdout').open('wb') as stdout,(raw/'stderr').open('wb') as stderr:
    try:
     process=subprocess.Popen(command,cwd=ROOT,env=ENV,stdout=stdout,stderr=stderr,start_new_session=True)
     facts.update(popen_args=process.args,pid=process.pid,owned_pgid=process.pid,status='running');save()
     facts['observed_exit']=process.wait(timeout=120)
    except subprocess.TimeoutExpired:
     facts['timeout_expired']=True
    finally:
     cleaning=True
     if process is not None:
      try:os.killpg(process.pid,signal.SIGKILL)
      except ProcessLookupError:pass
      try:facts['cleanup_exit']=process.wait(timeout=5)
      except subprocess.TimeoutExpired:facts['cleanup_timeout']=True
      facts['owned_group_after']=owned_members(process.pid)
     facts.update(status='closed',interrupted_by=interrupted);save();cleaning=False
   unchanged=stable() and sha(row['source'])==row['source_sha256'] and sha(row['fixture'])==row['fixture_sha256']
   passed=(facts['observed_exit']==0 and facts['cleanup_exit']==0 and facts.get('owned_group_after')==[]
    and (raw/'stdout').read_bytes()==b'true\n' and not (raw/'stderr').read_bytes() and unchanged)
   records.append({**row,'result':'pass' if passed else 'fail','command_record':str(raw/'command.json'),
    'stdout_sha256':sha(raw/'stdout'),'stderr_sha256':sha(raw/'stderr'),'inputs_stable':unchanged})
   print(row['id'],records[-1]['result'],row['main_predicates'],flush=True)
   if not passed:break
 except BaseException as error:
  failure={'type':type(error).__name__,'message':str(error)}
 passed=interrupted is None and failure is None and len(records)==len(SOURCES) and all(r['result']=='pass' for r in records)
 report={'result':'pass' if passed else 'fail','fingerprint':fingerprint,'direct_inputs':before,
  'scope':'Source-derived finite state predicates; native agreement is separate.',
  'completed_cases':len(records),'selected_cases':len(SOURCES),'conditional_unrun':list(SOURCES)[len(records):],
  'records':records,'error':failure,'interrupted_by':interrupted,'raw':str(out)}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(out,report['result'],flush=True)
 signal.signal(signal.SIGTERM,previous_term)
 return passed

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--prepare-only',type=Path);args=parser.parse_args()
 if args.prepare_only:prepare(args.prepare_only)
 else:raise SystemExit(0 if run() else 1)
