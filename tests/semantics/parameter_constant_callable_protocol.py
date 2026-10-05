#!/usr/bin/env python3
"""Check parameter callable receive scope, cached targets and nonowning history."""
import argparse,json,tempfile
from pathlib import Path
import global_constant_callable_protocol as global_protocol

base=global_protocol.base
ROOT=base.ROOT
premises=global_protocol.premises

SOURCES={'parameter-rebound-scope': '<?php\n'
                            'class ParameterBoundA {\n'
                            "    private const TOKEN = 'A';\n"
                            "    private static function token() { return self::TOKEN . ':' . "
                            'get_called_class(); }\n'
                            '    public static function maker() {\n'
                            '        return function ($r = static function () { return self::TOKEN '
                            ". ':' . get_called_class(); }, $m = self::token(...)) { echo "
                            "get_called_class(), ':'; return [$r, $m]; };\n"
                            '    }\n'
                            '}\n'
                            'class ParameterBoundB {\n'
                            "    private const TOKEN = 'B';\n"
                            "    private static function token() { return self::TOKEN . ':' . "
                            'get_called_class(); }\n'
                            '}\n'
                            'class ParameterReceiverC {}\n'
                            '$maker = ParameterBoundA::maker(); $a = $maker();\n'
                            '$receiver = new ParameterReceiverC(); $bound = '
                            '$maker->bindTo($receiver, ParameterBoundB::class);\n'
                            'unset($maker, $receiver);\n'
                            '$b = $bound(); unset($bound);\n'
                            "echo ($a[0] === $b[0] ? 'same' : 'fresh'), ':', $a[0](), ':', "
                            "$b[0](), ';';\n"
                            "echo ($a[1] === $b[1] ? 'same' : 'fresh'), ':', $a[1](), ':', "
                            "$b[1](), ';';\n",
 'parameter-trait-import-cache': '<?php\n'
                                 'trait ParameterDefaultTrait {\n'
                                 "    private static function token() { return self::NAME . ':' . "
                                 'get_called_class(); }\n'
                                 '    public static function take($m = self::token(...), $r = '
                                 "static function () { return self::NAME . ':' . "
                                 'get_called_class(); }) { return [$m, $r]; }\n'
                                 '}\n'
                                 'class ParameterHostA { use ParameterDefaultTrait; private const '
                                 "NAME = 'A'; }\n"
                                 "$a = ParameterHostA::take(); echo $a[0](), ':', $a[1](), ';'; "
                                 'unset($a);\n'
                                 "eval('class ParameterHostB { use ParameterDefaultTrait; private "
                                 'const NAME = "B"; }\');\n'
                                 "$b = ParameterHostB::take(); echo $b[0](), ':', $b[1](), ';';\n"
                                 "$clone = clone $b[0]; unset($b); echo $clone(), ';';\n",
 'parameter-trait-notice-reentry': '<?php\n'
                                   'trait ParameterNoticeTrait { public static function hit() { '
                                   'return 7; } }\n'
                                   'function parameterAcquire($f = ParameterNoticeTrait::hit(...)) '
                                   "{ echo 'B:'; return $f; }\n"
                                   '$count = 0;\n'
                                   'set_error_handler(static function ($level, $message, $file, '
                                   '$line) use (&$count) {\n'
                                   "    $count++; echo 'W', $count, ':', $line, ':';\n"
                                   "    if ($count === 1) { throw new Exception('stop'); }\n"
                                   "    if ($count === 2) { $GLOBALS['parameter_inner'] = "
                                   "parameterAcquire(); echo 'I:'; }\n"
                                   '    return true;\n'
                                   '});\n'
                                   "try { parameterAcquire(); } catch (Exception $e) { echo 'F:'; "
                                   '}\n'
                                   '$outer = parameterAcquire(); $later = parameterAcquire();\n'
                                   'restore_error_handler();\n'
                                   "echo ($outer === $later ? 'same' : 'fresh'), ':', $outer(), "
                                   "':', $GLOBALS['parameter_inner'](), ':', $later();\n",
 'parameter-partial-retry': '<?php\n'
                            'function parameterPair($a = static function () { return 11; }, $b = '
                            "parameterLate(...)) { echo 'B:'; return [$a, $b]; }\n"
                            "try { parameterPair(); } catch (Error $e) { echo 'F:'; }\n"
                            "eval('function parameterLate() { return 13; }');\n"
                            '$x = parameterPair(); $y = parameterPair();\n'
                            "echo ($x[0] === $y[0] ? 'same' : 'fresh'), ':', ($x[1] === $y[1] ? "
                            "'same' : 'fresh'), ':', $x[0](), ':', $x[1]();\n",
 'parameter-named-receive-type-failure': '<?php\n'
                                         'function parameterNamed(Closure $f = static function () '
                                         "{ return 3; }, int $sent = 0) { echo 'N', $sent, ':'; "
                                         'return $f; }\n'
                                         '$a = parameterNamed(sent: 4); $b = parameterNamed(sent: '
                                         '5);\n'
                                         '$supplied = static function () { return 9; };\n'
                                         '$c = parameterNamed(f: $supplied, sent: 6);\n'
                                         "echo ($a === $b ? 'same' : 'fresh'), ':', $a(), ':', "
                                         "$b(), ':', ($c === $supplied ? 'supplied' : 'bad');\n"
                                         'function parameterBad(int $f = static function () { '
                                         "return 1; }) { echo ';BODY'; }\n"
                                         'try { parameterBad(); } catch (TypeError $e) { echo '
                                         "';T'; }\n",
 'parameter-global-source-receiver': '<?php\n'
                                     '$maker = static function ($f = static function () { static '
                                     '$n = 0; return ++$n; }) { return $f; };\n'
                                     '$makerClone = clone $maker;\n'
                                     '$a = $maker(); $b = $makerClone(); unset($maker, '
                                     '$makerClone);\n'
                                     "echo ($a === $b ? 'same' : 'fresh'), ':', $a(), ':', $b();\n"
                                     "$clone = clone $a; unset($a); echo ':', $clone(), ':', "
                                     '$b();\n'}
SOURCES.update({'parameter-global-rebound-retired-maker': '<?php\n'
                                           'class ParameterGlobalBoundOwner {}\n'
                                           '$maker = static function ($f = static function () { '
                                           'return get_called_class(); }) { return $f; };\n'
                                           '$unscoped = $maker();\n'
                                           '$bound = $maker->bindTo(null, '
                                           'ParameterGlobalBoundOwner::class);\n'
                                           '$scoped = $bound();\n'
                                           'unset($maker, $bound);\n'
                                           "echo ($unscoped === $scoped ? 'same' : 'fresh'), ':', "
                                           '$scoped();\n',
 'parameter-unscoped-fcc-forms': '<?php\n'
                                 'function parameterUnscopedNamedFcc($v) { return $v + 1; }\n'
                                 'class ParameterUnscopedMethodOwner {\n'
                                 '    public static function pick() { return get_called_class(); '
                                 '}\n'
                                 '}\n'
                                 '$maker = static function ($f = parameterUnscopedNamedFcc(...), '
                                 '$g = ParameterUnscopedMethodOwner::pick(...)) { return [$f, $g]; '
                                 '};\n'
                                 '$first = $maker();\n'
                                 '$second = $maker();\n'
                                 '$clone = clone $first[1];\n'
                                 "echo ($first[0] === $second[0] ? 'same' : 'fresh'), ':', "
                                 "($first[1] === $second[1] ? 'same' : 'fresh'), ':';\n"
                                 'unset($maker, $first);\n'
                                 "echo $second[0](4), ':', $second[1](), ':', $clone();\n"})
FILES={}
EVALS={
    "parameter-trait-import-cache": ['class ParameterHostB { use ParameterDefaultTrait; private const NAME = "B"; }'],
    "parameter-partial-retry": ['function parameterLate() { return 13; }'],
}

PREFIX=global_protocol.PREFIX+r'''
dec $parameter_test_index(pstate, nat) : bool
def $parameter_test_index(S, n_index) = true
  -- if S.TODO = (DEFAULT_BIND porigin_function n_index) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.FUNCTION = porigin_function
  -- if S.RESULT = KNOWN (POBJECT n_object)
  -- if $parameter_callable_record(S.PARAMETERCLOSURES, n_object) = (pparameterclosure)
def $parameter_test_index(S, n_index) = false -- otherwise
dec $parameter_test_function(pstate, ptbytes) : bool
def $parameter_test_function(S, ptbytes_name) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $function_at($all_functions(S), pcallcontext.FUNCTION) = (pfunction)
  -- if pfunction.NAME = ptbytes_name
def $parameter_test_function(S, ptbytes_name) = false -- otherwise
dec $parameter_test_scope(pstate, ptbytes) : bool
def $parameter_test_scope(S, ptbytes_name) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.LEXICAL_CLASS = (porigin_scope)
  -- if $class_at(S.CLASSES, porigin_scope) = (pclassdesc)
  -- if pclassdesc.NAME = ptbytes_name
def $parameter_test_scope(S, ptbytes_name) = false -- otherwise
dec $parameter_test_warning(pstate) : bool
def $parameter_test_warning(S) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = PARAMETER_CONSTANT_METHOD_RESUME porigin_site porigin_function porigin_called n_prefix
def $parameter_test_warning(S) = false -- otherwise
dec $parameter_test_saved(pstate) : bool
def $parameter_test_saved(S) = true
  -- if S.CURRENT = (pcallcontext_handler)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.CONTEXT = (pcallcontext_receive)
  -- if pcallcontext_receive.NAME = $ptascii("parameterAcquire")
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = PARAMETER_CONSTANT_METHOD_RESUME porigin_site porigin_function porigin_called n_prefix
def $parameter_test_saved(S) = false -- otherwise
dec $parameter_test_stage(pstate, nat) : bool
def $parameter_test_stage(S, 0) = ($parameter_test_index(S, 0) /\ $parameter_test_scope(S, $ptascii("ParameterBoundA")))
def $parameter_test_stage(S, 1) = ($parameter_test_index(S, 1) /\ $parameter_test_scope(S, $ptascii("ParameterBoundA")))
def $parameter_test_stage(S, 2) = ($parameter_test_index(S, 0) /\ $parameter_test_scope(S, $ptascii("ParameterBoundB")))
def $parameter_test_stage(S, 3) = ($parameter_test_index(S, 1) /\ $parameter_test_scope(S, $ptascii("ParameterBoundB")))
def $parameter_test_stage(S, 4) = ($parameter_test_index(S, 0) /\ $parameter_test_scope(S, $ptascii("ParameterHostA")))
def $parameter_test_stage(S, 5) = ($parameter_test_index(S, 0) /\ $parameter_test_scope(S, $ptascii("ParameterHostB")))
def $parameter_test_stage(S, 6) = ($parameter_test_warning(S) /\ S.PARAMETERCLOSURES = eps)
def $parameter_test_stage(S, 7) = ($parameter_test_saved(S) /\ $global_test_output(S.EVENTS) = $ptascii("W1:3:"))
def $parameter_test_stage(S, 8) = ($parameter_test_warning(S) /\ $global_test_output(S.EVENTS) = $ptascii("W1:3:F:"))
def $parameter_test_stage(S, 9) = ($parameter_test_saved(S) /\ $global_test_output(S.EVENTS) = $ptascii("W1:3:F:W2:3:"))
def $parameter_test_stage(S, 10) = true
  -- if S.TODO = (PARAMETER_CONSTANT_METHOD_RESUME porigin_site porigin_function porigin_called n_prefix) :: ptask_tail*
  -- if $global_test_output(S.EVENTS) = $ptascii("W1:3:F:W2:3:B:I:")
  -- if |S.PARAMETERCLOSURES| = 1
def $parameter_test_stage(S, 11) = ($parameter_test_index(S, 0) /\ $parameter_test_function(S, $ptascii("parameterPair")) /\ S.EVENTS = eps)
def $parameter_test_stage(S, 12) = ($parameter_test_index(S, 0) /\ $parameter_test_function(S, $ptascii("parameterPair")) /\ $global_test_output(S.EVENTS) = $ptascii("F:"))
def $parameter_test_stage(S, 13) = true
  -- if S.TODO = (NAMED_DEFAULT_BIND porigin_function 0) :: ptask_tail*
  -- if $parameter_test_function(S, $ptascii("parameterNamed"))
  -- if S.RESULT = KNOWN (POBJECT n_object)
def $parameter_test_stage(S, 14) = ($parameter_test_index(S, 0) /\ $parameter_test_function(S, $ptascii("parameterBad")))
def $parameter_test_stage(S, 15) = true
  -- if $parameter_test_index(S, 0)
  -- if |S.PARAMETERCLOSURES| = 1
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.LEXICAL_CLASS = eps
  -- if pcallcontext.TARGET = CLOSURE_TARGET n_source
def $parameter_test_stage(S, 16) = true
  -- if $parameter_test_index(S, 0)
  -- if |S.PARAMETERCLOSURES| = 2
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.LEXICAL_CLASS = eps
  -- if pcallcontext.TARGET = CLOSURE_TARGET n_source
def $parameter_test_stage(S, 17) = ($parameter_test_index(S, 0) /\ $parameter_test_scope(S, $ptascii("ParameterGlobalBoundOwner")))
def $parameter_test_stage(S, 18) = true
  -- if $parameter_test_index(S, 1)
  -- if |S.PARAMETERCLOSURES| = 2
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.LEXICAL_CLASS = eps
  -- if pcallcontext.TARGET = CLOSURE_TARGET n_source
def $parameter_test_stage(S, n_stage) = false -- otherwise
dec $parameter_test_seek(pstate, nat, nat) : pstate
def $parameter_test_seek(S, n_stage, n_limit) = S
  -- if $parameter_test_stage(S, n_stage)
def $parameter_test_seek(S, n_stage, n_limit) = $parameter_test_seek($global_test_next(S), n_stage, n_rest)
  -- if ~$parameter_test_stage(S, n_stage)
  -- if $(n_limit > 0)
  -- if (S.COMPLETION = NORMAL \/ S.COMPLETION = SOURCE_PENDING) /\ ~S.COMPILESTOP
  -- if n_rest = $(n_limit - 1)
dec $parameter_test_without_constant(pconstantclosure*, nat) : pconstantclosure*
def $parameter_test_without_constant(eps, n_object) = eps
def $parameter_test_without_constant(pconstantclosure :: pconstantclosure_tail*, n_object) = $parameter_test_without_constant(pconstantclosure_tail*, n_object)
  -- if pconstantclosure.OBJECT = n_object
def $parameter_test_without_constant(pconstantclosure :: pconstantclosure_tail*, n_object) = pconstantclosure :: $parameter_test_without_constant(pconstantclosure_tail*, n_object)
  -- if pconstantclosure.OBJECT =/= n_object
dec $parameter_test_function_event(pdeclaration, porigin) : bool
def $parameter_test_function_event(PDEFUNCTION n_unit porigin_function, porigin_function) = true
def $parameter_test_function_event(PDRFUNCTION porigin_function pdeclcause, porigin_function) = true
def $parameter_test_function_event(pdeclaration, porigin_function) = false -- otherwise
dec $parameter_test_function_prefix(pdeclaration*, porigin, nat) : nat?
def $parameter_test_function_prefix(eps, porigin_function, n_count) = eps
def $parameter_test_function_prefix(pdeclaration :: pdeclaration_tail*, porigin_function, n_count) = (n_count)
  -- if $parameter_test_function_event(pdeclaration, porigin_function)
def $parameter_test_function_prefix(pdeclaration :: pdeclaration_tail*, porigin_function, n_count) = $parameter_test_function_prefix(pdeclaration_tail*, porigin_function, $(n_count + 1))
  -- if ~$parameter_test_function_event(pdeclaration, porigin_function)
'''
CHECKS={}
CHECKS['parameter-rebound-scope']=premises(r'''
S_a = $parameter_test_seek(S_initial[.COMPLETION = NORMAL], 0, 1800)
S_a.RESULT = KNOWN (POBJECT n_real_a)
$constant_callable_record(S_a.CONSTANTCLOSURES, n_real_a) = (pconstantclosure_real_a)
$parameter_callable_header(S_a, pconstantclosure_real_a) = (pparameterclosure_real_a)
pparameterclosure_real_a.SCOPE = (porigin_a)
S_m = $parameter_test_seek(S_a, 1, 1000)
S_m.RESULT = KNOWN (POBJECT n_method_a)
$constant_callable_record(S_m.CONSTANTCLOSURES, n_method_a) = (pconstantclosure_method_a)
$object_body(S_m.OBJECTS[n_method_a]) = METHODCLOSURE porigin_method pconstantclosure_method_a.SITE porigin_a eps
S = $parameter_test_seek(S_m, 2, 1800)
S.TODO = [DEFAULT_BIND porigin_function 0]
S.RESULT = KNOWN (POBJECT n_real_b)
S.CURRENT = (pcallcontext)
pcallcontext.FUNCTION = porigin_function
pcallcontext.TARGET = CLOSURE_TARGET n_bound
pcallcontext.LEXICAL_CLASS = (porigin_b)
pcallcontext.CALLED_CLASS = (porigin_c)
pcallcontext.RECEIVER = (n_receiver)
porigin_a =/= porigin_b /\ porigin_b =/= porigin_c
$function_at(S.CLOSURETEMPLATES, porigin_function) = (pfunction)
$constant_callable_record(S.CONSTANTCLOSURES, n_real_b) = (pconstantclosure_real_b)
$parameter_callable_header(S, pconstantclosure_real_b) = (pparameterclosure_real_b)
pparameterclosure_real_b.FUNCTION = porigin_function /\ pparameterclosure_real_b.INDEX = 0
pparameterclosure_real_b.SCOPE = (porigin_b)
pparameterclosure_real_b.EVIDENCE = (PARAMETER_SCOPE pclosureevidence)
pclosureevidence = CLOSURE_BINDING pclosurebinding
pclosurebinding.OBJECT = n_bound /\ pclosurebinding.RECEIVER = (n_receiver)
$closure_evidence_valid(S, pclosureevidence)
$closure_scope_at(S.CLOSURESCOPES, n_real_b) = (pclosurescope_real_b)
pclosurescope_real_b.LEXICAL = porigin_b /\ pclosurescope_real_b.CALLED = porigin_b
pclosurescope_real_b.RECEIVER = eps /\ pclosurescope_real_b.CREATION = eps
$parameter_callable_real_scope_valid(S, pconstantclosure_real_b.SITE, pclosurescope_real_b)
$parameter_default_transfer_valid(S, pfunction, 0, POBJECT n_real_b, PVCLOSURE n_real_b pconstantclosure_real_b.SITE)
~$parameter_default_transfer_valid(S, pfunction, 1, POBJECT n_real_b, PVCLOSURE n_real_b pconstantclosure_real_b.SITE)
~$parameter_default_transfer_valid(S[.RESULT = KNOWN (POBJECT n_real_a)], pfunction, 0, POBJECT n_real_b, PVCLOSURE n_real_b pconstantclosure_real_b.SITE)
~$parameter_callable_scope_valid(S, pparameterclosure_real_b[.SCOPE = (porigin_a)], pfunction)
~$parameter_callable_scope_valid(S, pparameterclosure_real_b[.EVIDENCE = eps], pfunction)
~$parameter_callable_scope_valid(S, pparameterclosure_real_b[.EVIDENCE = (PARAMETER_SCOPE (CLOSURE_BINDING pclosurebinding[.OBJECT = n_real_b]))], pfunction)
$parameter_callable_header(S, pconstantclosure_real_b[.DECL = pconstantclosure_method_a.DECL]) = eps
$parameter_callable_header(S, pconstantclosure_real_b[.SITE = pconstantclosure_method_a.SITE]) = eps
$parameter_callable_header(S, pconstantclosure_real_b[.PREFIX = 0]) = eps
~$parameter_callable_real_scope_valid(S, pconstantclosure_real_b.SITE, pclosurescope_real_b[.CALLED = porigin_c])
$call_current_valid(S) /\ $call_tasks_valid(S, S.TODO)
$call_descriptors_valid(S)
S_b = $parameter_test_seek(S, 3, 1000)
S_b.RESULT = KNOWN (POBJECT n_method_b)
$constant_callable_record(S_b.CONSTANTCLOSURES, n_method_b) = (pconstantclosure_method_b)
$parameter_callable_header(S_b, pconstantclosure_method_b) = (pparameterclosure_method_b)
pparameterclosure_method_b.SCOPE = (porigin_b) /\ pparameterclosure_method_b.INDEX = 1
$object_body(S_b.OBJECTS[n_method_b]) = METHODCLOSURE porigin_method pconstantclosure_method_b.SITE porigin_b eps
$parameter_callable_cached_method(S_b, pconstantclosure_method_b.SITE) = (pmethoddesc)
pmethoddesc.OWNER = porigin_a
$closure_scope_at(S_b.CLOSURESCOPES, n_method_b) = (pclosurescope_method_b)
pclosurescope_method_b.LEXICAL = porigin_a /\ pclosurescope_method_b.CALLED = porigin_b
$parameter_callable_method_live(S_b, pmethoddesc, pconstantclosure_method_b.SITE, porigin_b, pclosurescope_method_b)
$closure_scope_row_valid(S_b, pclosurescope_method_b)
~$parameter_callable_method_live(S_b, pmethoddesc, pconstantclosure_method_b.SITE, porigin_b, pclosurescope_method_b[.CALLED = porigin_a])
S_done = $global_test_finish(S_b, 6500)
$global_test_output(S_done.EVENTS) = $ptascii("ParameterBoundA:ParameterReceiverC:fresh:A:ParameterBoundA:B:ParameterBoundB;fresh:A:ParameterBoundA:A:ParameterBoundB;")
$parameter_callable_records_valid(S_done, S_done.PARAMETERCLOSURES)
~((HOBJECT n_bound) <- S_done.ALLOCATIONS)
~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)
~((HOBJECT pclosurebinding.SOURCE) <- S_done.ALLOCATIONS)
$parameter_callable_header(S_done, pconstantclosure_real_b) = (pparameterclosure_real_b)
$closure_evidence_valid(S_done, pclosureevidence)
$heap_owners($heap_graph(S_done), HOBJECT n_bound) = 0
$heap_owners($heap_graph(S_done), HOBJECT n_receiver) = 0
$parameter_callable_method_live(S_done, pmethoddesc, pconstantclosure_method_b.SITE, porigin_b, pclosurescope_method_b)
S_roots = $prune_allocations(S_done[.ENV = eps][.GLOBALTABLE = eps][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)])
~((HOBJECT n_real_b) <- S_roots.ALLOCATIONS)
~((HOBJECT n_method_b) <- S_roots.ALLOCATIONS)
$parameter_callable_records_valid(S_roots, S_roots.PARAMETERCLOSURES)
''')
CHECKS['parameter-trait-import-cache']=premises(r'''
S_a = $parameter_test_seek(S_initial[.COMPLETION = NORMAL], 4, 1800)
S_a.RESULT = KNOWN (POBJECT n_method_a)
$constant_callable_record(S_a.CONSTANTCLOSURES, n_method_a) = (pconstantclosure_a)
$parameter_callable_header(S_a, pconstantclosure_a) = (pparameterclosure_a)
pparameterclosure_a.SCOPE = (porigin_a)
$function_at($all_functions(S_a), pparameterclosure_a.FUNCTION) = (pfunction_a)
$trait_imported_origin(pfunction_a.ORIGIN)
S = $parameter_test_seek(S_a, 5, 4200)
S.TODO = [DEFAULT_BIND porigin_function_b 0]
S.RESULT = KNOWN (POBJECT n_method_b)
$constant_callable_record(S.CONSTANTCLOSURES, n_method_b) = (pconstantclosure_b)
$parameter_callable_header(S, pconstantclosure_b) = (pparameterclosure_b)
pparameterclosure_b.SCOPE = (porigin_b)
pparameterclosure_b.FUNCTION = porigin_function_b
$function_at($all_functions(S), porigin_function_b) = (pfunction_b)
$trait_imported_origin(pfunction_b.ORIGIN)
pfunction_a.ORIGIN =/= pfunction_b.ORIGIN
$origin_source(pfunction_a.ORIGIN) = $origin_source(pfunction_b.ORIGIN)
pconstantclosure_a.SITE = pconstantclosure_b.SITE
pconstantclosure_a.DECL = pconstantclosure_b.DECL
$(pconstantclosure_a.PREFIX < pconstantclosure_b.PREFIX)
$constant_callable_first(S.CONSTANTCLOSURES, pconstantclosure_b.SITE) = (pconstantclosure_a)
$parameter_callable_cached_method(S, pconstantclosure_b.SITE) = (pmethoddesc_a)
pmethoddesc_a.OWNER = porigin_a
$object_body(S.OBJECTS[n_method_b]) = METHODCLOSURE pmethoddesc_a.FUNCTION.ORIGIN pconstantclosure_b.SITE porigin_b eps
$closure_scope_at(S.CLOSURESCOPES, n_method_b) = (pclosurescope_b)
pclosurescope_b.LEXICAL = porigin_a /\ pclosurescope_b.CALLED = porigin_b
$parameter_callable_method_live(S, pmethoddesc_a, pconstantclosure_b.SITE, porigin_b, pclosurescope_b)
$closure_scope_row_valid(S, pclosurescope_b)
$parameter_callable_scope_valid(S, pparameterclosure_b, pfunction_b)
~$parameter_callable_scope_valid(S, pparameterclosure_b[.SCOPE = (porigin_a)], pfunction_b)
S_wrong_import = S[.PARAMETERCLOSURES = [pparameterclosure_b[.FUNCTION = pfunction_a.ORIGIN]]]
$parameter_callable_header(S_wrong_import, pconstantclosure_b) = eps
$parameter_callable_header(S, pconstantclosure_b[.PREFIX = pconstantclosure_a.PREFIX]) = eps
$parameter_callable_header(S, pconstantclosure_b[.DECL = pfunction_b.ORIGIN]) = eps
$parameter_callable_header(S, pconstantclosure_b[.SITE = pfunction_b.ORIGIN]) = eps
~$parameter_callable_method_live(S, pmethoddesc_a, pconstantclosure_b.SITE, porigin_b, pclosurescope_b[.LEXICAL = porigin_b])
~$parameter_callable_method_live(S, pmethoddesc_a, pconstantclosure_b.SITE, porigin_b, pclosurescope_b[.CALLED = porigin_a])
S_missing_first = S[.CONSTANTCLOSURES = $parameter_test_without_constant(S.CONSTANTCLOSURES, n_method_a)]
$parameter_callable_record(S_missing_first.PARAMETERCLOSURES, n_method_b) = (pparameterclosure_b)
$constant_callable_record(S_missing_first.CONSTANTCLOSURES, n_method_b) = (pconstantclosure_b)
$parameter_callable_cached_method(S_missing_first, pconstantclosure_b.SITE) = eps
~$parameter_callable_method_live(S_missing_first, pmethoddesc_a, pconstantclosure_b.SITE, porigin_b, pclosurescope_b)
~((HOBJECT n_method_a) <- S.ALLOCATIONS)
$heap_owners($heap_graph(S), HOBJECT n_method_a) = 0
$constant_callable_record_valid(S, pconstantclosure_a)
$call_current_valid(S) /\ $call_tasks_valid(S, S.TODO)
$call_descriptors_valid(S)
S_done = $global_test_finish(S, 5000)
$global_test_output(S_done.EVENTS) = $ptascii("A:ParameterHostA:A:ParameterHostA;A:ParameterHostB:B:ParameterHostB;A:ParameterHostB;")
$lookup(S_done.ENV, $ptascii("clone")) = (n_cell_clone)
S_done.STORE[n_cell_clone] = DEFINED (POBJECT n_clone)
S_done.OBJECTS[n_clone] = METHODCLOSURE pmethoddesc_a.FUNCTION.ORIGIN pconstantclosure_b.SITE porigin_b eps
$constant_callable_record(S_done.CONSTANTCLOSURES, n_clone) = eps
$parameter_callable_record(S_done.PARAMETERCLOSURES, n_clone) = eps
$closure_scope_at(S_done.CLOSURESCOPES, n_clone) = (pclosurescope_clone)
$parameter_callable_method_live(S_done, pmethoddesc_a, pconstantclosure_b.SITE, porigin_b, pclosurescope_clone)
$closure_scope_row_valid(S_done, pclosurescope_clone)
~((HOBJECT n_method_b) <- S_done.ALLOCATIONS)
$constant_callable_record_valid(S_done, pconstantclosure_b)
$parameter_callable_records_valid(S_done, S_done.PARAMETERCLOSURES)
~$parameter_callable_method_live(S_done[.CONSTANTCLOSURES = eps], pmethoddesc_a, pconstantclosure_b.SITE, porigin_b, pclosurescope_clone)
$heap_owners($heap_graph(S_done), HOBJECT n_clone) = 1
S_roots = $prune_allocations(S_done[.ENV = eps][.GLOBALTABLE = eps][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)])
~((HOBJECT n_clone) <- S_roots.ALLOCATIONS)
$parameter_callable_records_valid(S_roots, S_roots.PARAMETERCLOSURES)
''')
CHECKS['parameter-trait-notice-reentry']=premises(r'''
S = $parameter_test_seek(S_initial[.COMPLETION = NORMAL], 6, 2000)
S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warning*
perrorcall.RESUME = PARAMETER_CONSTANT_METHOD_RESUME porigin_site porigin_method porigin_called n_prefix
perrorcall.SITE = porigin_site /\ perrorcall.LEVEL = 8192 /\ perrorcall.LINE = 3
S.CURRENT = (pcallcontext_receive)
$function_at(S.FUNCTIONS, pcallcontext_receive.FUNCTION) = (pfunction_receive)
$default_at(pfunction_receive.DEFAULTS, 0) = (pdefault)
S.CONSTCONTEXT = (pconstantcontext)
pconstantcontext.ORIGIN = $default_parameter_origin(S, pfunction_receive.ORIGIN, 0)
$parameter_callable_context(S, porigin_site) = (pparameterclosure_pending)
pparameterclosure_pending.FUNCTION = pfunction_receive.ORIGIN /\ pparameterclosure_pending.INDEX = 0
pparameterclosure_pending.SCOPE = eps /\ pparameterclosure_pending.EVIDENCE = eps
$parameter_callable_method_resume_valid(S, porigin_site, porigin_method, porigin_called, n_prefix)
$error_call_valid(S, perrorcall)
$call_task_valid(S, ERROR_HANDLER_INVOKE perrorcall)
$call_descriptors_valid(S)
S.CONSTANTCLOSURES = eps /\ S.PARAMETERCLOSURES = eps
$task_nodes(perrorcall.RESUME) = eps
$parameter_test_function_prefix(S.DECLARATIONS, pfunction_receive.ORIGIN, 0) = (n_before_function)
$declaration_entered(S.DECLARATIONS[0:n_before_function], pfunction_receive.CODE.UNIT)
~$parameter_callable_function_published(S, pfunction_receive, n_before_function)
~$parameter_callable_method_resume_valid(S, porigin_site, porigin_method, porigin_called, n_before_function)
~$parameter_callable_method_resume_valid(S, pconstantcontext.ORIGIN, porigin_method, porigin_called, n_prefix)
~$parameter_callable_method_resume_valid(S, porigin_site, pfunction_receive.ORIGIN, porigin_called, n_prefix)
~$parameter_callable_method_resume_valid(S, porigin_site, porigin_method, pfunction_receive.ORIGIN, n_prefix)
~$parameter_callable_method_resume_valid(S, porigin_site, porigin_method, porigin_called, $(|S.DECLARATIONS| + 1))
~$error_call_valid(S, perrorcall[.LINE = 4])
~$error_call_valid(S, perrorcall[.RESUME = PARAMETER_CONSTANT_METHOD_RESUME porigin_site porigin_method porigin_called n_before_function])
S_handler = $parameter_test_seek(S, 7, 2200)
S_handler.CURRENT = (pcallcontext_handler)
S_handler.FRAMES = pframe :: pframe_tail*
pframe.CONTEXT = (pcallcontext_receive)
pframe.CONSTCONTEXT = (pconstantcontext)
pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_saved) :: ptask_saved*
perrorcall_saved.RESUME = perrorcall.RESUME
perrorcall_saved.TARGET = (pcallcontext_handler.TARGET)
$call_current_valid(S_handler)
$call_saved_context_valid(S_handler, pframe)
$call_frames_valid(S_handler, S_handler.FRAMES)
$call_descriptors_valid(S_handler)
S_owner = $constant_frame_scope(S_handler, pframe, pframe_tail*)
S_owner.CURRENT = (pcallcontext_receive) /\ S_owner.CONSTCONTEXT = (pconstantcontext)
S_owner.TODO = pframe.TODO
$parameter_callable_context(S_owner, porigin_site) = (pparameterclosure_owner)
pparameterclosure_owner.FUNCTION = pfunction_receive.ORIGIN /\ pparameterclosure_owner.INDEX = 0
$parameter_callable_method_resume_valid(S_owner, porigin_site, porigin_method, porigin_called, n_prefix)
$error_call_valid(S_owner, perrorcall_saved)
$call_task_valid(S_owner, ERROR_HANDLER_RESULT perrorcall_saved)
~$call_frames_valid(S_handler, pframe[.CONTEXT = (pcallcontext_receive[.FUNCTION = porigin_method])] :: pframe_tail*)
~$call_frames_valid(S_handler, pframe[.CONSTCONTEXT = (pconstantcontext[.ORIGIN = porigin_site])] :: pframe_tail*)
~$call_frames_valid(S_handler, pframe[.TODO = (ERROR_HANDLER_RESULT perrorcall_saved[.RESUME = PARAMETER_CONSTANT_METHOD_RESUME porigin_site porigin_method porigin_called n_before_function]) :: ptask_saved*] :: pframe_tail*)
S_caught = $global_test_find(S_handler, $ptascii("W1:3:F:"), 7, 2200)
S_caught.CONSTANTCLOSURES = eps /\ S_caught.PARAMETERCLOSURES = eps
S_caught.CONSTCONTEXT = eps
S_again = $parameter_test_seek(S_caught, 8, 1500)
S_again.TODO = (ERROR_HANDLER_INVOKE perrorcall_again) :: ptask_again*
perrorcall_again.RESUME = perrorcall.RESUME
S_second = $parameter_test_seek(S_again, 9, 1800)
$call_frames_valid(S_second, S_second.FRAMES)
$call_descriptors_valid(S_second)
S_resume = $parameter_test_seek(S_second, 10, 3500)
S_resume.TODO = (PARAMETER_CONSTANT_METHOD_RESUME porigin_site porigin_method porigin_called n_prefix) :: ptask_resume*
S_resume.PARAMETERCLOSURES = [pparameterclosure_inner]
$constant_callable_record(S_resume.CONSTANTCLOSURES, pparameterclosure_inner.OBJECT) = (pconstantclosure_inner)
$parameter_callable_header(S_resume, pconstantclosure_inner) = (pparameterclosure_inner)
$parameter_callable_cached_method(S_resume, porigin_site) = (pmethoddesc)
pmethoddesc.FUNCTION.ORIGIN = porigin_method
$parameter_callable_method_resume_valid(S_resume, porigin_site, porigin_method, porigin_called, n_prefix)
n_outer = |S_resume.OBJECTS|
S_outer = $global_test_next(S_resume)
S_outer.RESULT = KNOWN (POBJECT n_outer)
$parameter_callable_record(S_outer.PARAMETERCLOSURES, n_outer) = (pparameterclosure_outer)
$constant_callable_record(S_outer.CONSTANTCLOSURES, n_outer) = (pconstantclosure_outer)
$(pparameterclosure_inner.OBJECT < n_outer)
pconstantclosure_outer.PREFIX = |S_outer.DECLARATIONS|
$constant_callable_record_valid(S_outer, pconstantclosure_outer)
S_done = $global_test_finish(S_outer, 4800)
$global_test_output(S_done.EVENTS) = $ptascii("W1:3:F:W2:3:B:I:B:B:fresh:7:7:7")
|S_done.PARAMETERCLOSURES| = 3
S_done.DEFAULTCACHE = eps
$parameter_callable_records_valid(S_done, S_done.PARAMETERCLOSURES)
(HOBJECT pparameterclosure_inner.OBJECT) <- S_done.ALLOCATIONS
(HOBJECT n_outer) <- S_done.ALLOCATIONS
S_roots = $prune_allocations(S_done[.ENV = eps][.GLOBALTABLE = eps][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)])
~((HOBJECT n_outer) <- S_roots.ALLOCATIONS)
~((HOBJECT pparameterclosure_inner.OBJECT) <- S_roots.ALLOCATIONS)
$parameter_callable_records_valid(S_roots, S_roots.PARAMETERCLOSURES)
''')
CHECKS['parameter-partial-retry']=premises(r'''
S = $parameter_test_seek(S_initial[.COMPLETION = NORMAL], 11, 1500)
S.TODO = [DEFAULT_BIND porigin_function 0]
S.RESULT = KNOWN (POBJECT n_first)
$function_at(S.FUNCTIONS, porigin_function) = (pfunction)
$constant_callable_record(S.CONSTANTCLOSURES, n_first) = (pconstantclosure_first)
$parameter_callable_header(S, pconstantclosure_first) = (pparameterclosure_first)
pparameterclosure_first.FUNCTION = porigin_function /\ pparameterclosure_first.INDEX = 0
pparameterclosure_first.SCOPE = eps /\ pparameterclosure_first.EVIDENCE = eps
$default_at(pfunction.DEFAULTS, 0) = (pdefault_a)
$default_at(pfunction.DEFAULTS, 1) = (pdefault_b)
$parameter_default_transfer_valid(S, pfunction, 0, POBJECT n_first, PVCLOSURE n_first pconstantclosure_first.SITE)
~$parameter_default_transfer_valid(S, pfunction, 1, POBJECT n_first, PVCLOSURE n_first pconstantclosure_first.SITE)
$parameter_callable_header(S, pconstantclosure_first[.DECL = $default_parameter_origin(S, porigin_function, 1)]) = eps
$call_descriptors_valid(S)
S_caught = $global_test_find(S, $ptascii("F:"), 7, 1800)
S_caught.CONSTCONTEXT = eps /\ S_caught.DEFAULTCACHE = eps
S_caught.PARAMETERCLOSURES = [pparameterclosure_first]
~((HOBJECT n_first) <- S_caught.ALLOCATIONS)
$heap_owners($heap_graph(S_caught), HOBJECT n_first) = 0
$parameter_callable_header(S_caught, pconstantclosure_first) = (pparameterclosure_first)
$constant_callable_record_valid(S_caught, pconstantclosure_first)
S_retry = $parameter_test_seek(S_caught, 12, 2500)
S_retry.RESULT = KNOWN (POBJECT n_retry)
n_first =/= n_retry
$constant_callable_record(S_retry.CONSTANTCLOSURES, n_retry) = (pconstantclosure_retry)
$parameter_callable_header(S_retry, pconstantclosure_retry) = (pparameterclosure_retry)
pparameterclosure_retry.FUNCTION = porigin_function /\ pparameterclosure_retry.INDEX = 0
pconstantclosure_retry.SITE = pconstantclosure_first.SITE
$(pconstantclosure_first.PREFIX < pconstantclosure_retry.PREFIX)
$parameter_default_transfer_valid(S_retry, pfunction, 0, POBJECT n_retry, PVCLOSURE n_retry pconstantclosure_retry.SITE)
~$parameter_default_transfer_valid(S_retry[.RESULT = KNOWN (POBJECT n_first)], pfunction, 0, POBJECT n_first, PVCLOSURE n_first pconstantclosure_first.SITE)
~$parameter_default_transfer_valid(S_retry, pfunction, 1, POBJECT n_retry, PVCLOSURE n_retry pconstantclosure_retry.SITE)
$call_descriptors_valid(S_retry)
S_done = $global_test_finish(S_retry, 4500)
$global_test_output(S_done.EVENTS) = $ptascii("F:B:B:fresh:fresh:11:13")
|S_done.PARAMETERCLOSURES| = 5
S_done.DEFAULTCACHE = eps /\ S_done.CONSTCONTEXT = eps
$lookup(S_done.ENV, $ptascii("x")) = (n_cell_x)
$lookup(S_done.ENV, $ptascii("y")) = (n_cell_y)
S_done.STORE[n_cell_x] = DEFINED (PARRAY n_x)
S_done.STORE[n_cell_y] = DEFINED (PARRAY n_y)
S_done.ARRAYS[n_x].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_xa)), ENTRY (KINT 1) (DIRECT (POBJECT n_xb))]
S_done.ARRAYS[n_y].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_ya)), ENTRY (KINT 1) (DIRECT (POBJECT n_yb))]
n_xa = n_retry /\ n_xa =/= n_ya /\ n_xb =/= n_yb
$constant_callable_record(S_done.CONSTANTCLOSURES, n_xb) = (pconstantclosure_xb)
$parameter_callable_header(S_done, pconstantclosure_xb) = (pparameterclosure_xb)
pparameterclosure_xb.INDEX = 1 /\ pparameterclosure_xb.FUNCTION = porigin_function
$object_body(S_done.OBJECTS[n_xb]) = NAMEDCLOSURE porigin_late
$function_at(S_done.FUNCTIONS, porigin_late) = (pfunction_late)
pfunction_late.NAME = $ptascii("parameterLate")
$constant_callable_records_valid(S_done, S_done.CONSTANTCLOSURES)
$parameter_callable_records_valid(S_done, S_done.PARAMETERCLOSURES)
S_roots = $prune_allocations(S_done[.ENV = eps][.GLOBALTABLE = eps][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)])
~((HOBJECT n_retry) <- S_roots.ALLOCATIONS)
~((HOBJECT n_xb) <- S_roots.ALLOCATIONS)
$parameter_callable_records_valid(S_roots, S_roots.PARAMETERCLOSURES)
''')
CHECKS['parameter-named-receive-type-failure']=premises(r'''
S = $parameter_test_seek(S_initial[.COMPLETION = NORMAL], 13, 1600)
S.TODO = [NAMED_DEFAULT_BIND porigin_function 0]
S.CURRENT = (pcallcontext)
pcallcontext.FUNCTION = porigin_function
$function_at(S.FUNCTIONS, porigin_function) = (pfunction)
S.RESULT = KNOWN (POBJECT n_first)
$constant_callable_record(S.CONSTANTCLOSURES, n_first) = (pconstantclosure_first)
$parameter_callable_header(S, pconstantclosure_first) = (pparameterclosure_first)
pparameterclosure_first.FUNCTION = porigin_function /\ pparameterclosure_first.INDEX = 0
pparameterclosure_first.SCOPE = eps /\ pparameterclosure_first.EVIDENCE = eps
$parameter_callable_real_unscoped(S, n_first)
$parameter_default_transfer_valid(S, pfunction, 0, POBJECT n_first, PVCLOSURE n_first pconstantclosure_first.SITE)
$call_task_valid(S, NAMED_DEFAULT_BIND porigin_function 0)
$call_descriptors_valid(S)
$parameter_test_function_prefix(S.DECLARATIONS, porigin_function, 0) = (n_before_function)
$declaration_entered(S.DECLARATIONS[0:n_before_function], pfunction.CODE.UNIT)
$parameter_callable_header(S, pconstantclosure_first[.PREFIX = n_before_function]) = eps
~$parameter_callable_scope_valid(S, pparameterclosure_first[.SCOPE = (porigin_function)], pfunction)
S_wrong_index = S[.PARAMETERCLOSURES = [pparameterclosure_first[.INDEX = 1]]]
$parameter_callable_header(S_wrong_index, pconstantclosure_first) = eps
~$parameter_default_transfer_valid(S[.RESULT = KNOWN PNULL], pfunction, 0, POBJECT n_first, PVCLOSURE n_first pconstantclosure_first.SITE)
~$parameter_default_transfer_valid(S, pfunction, 1, POBJECT n_first, PVCLOSURE n_first pconstantclosure_first.SITE)
S_bad = $parameter_test_seek(S, 14, 3800)
S_bad.TODO = [DEFAULT_BIND porigin_bad_function 0]
S_bad.RESULT = KNOWN (POBJECT n_bad)
$function_at(S_bad.FUNCTIONS, porigin_bad_function) = (pfunction_bad)
$constant_callable_record(S_bad.CONSTANTCLOSURES, n_bad) = (pconstantclosure_bad)
$parameter_callable_header(S_bad, pconstantclosure_bad) = (pparameterclosure_bad)
pparameterclosure_bad.FUNCTION = porigin_bad_function /\ pparameterclosure_bad.INDEX = 0
$constant_callable_record_valid(S_bad, pconstantclosure_bad)
$parameter_default_transfer_valid(S_bad, pfunction_bad, 0, POBJECT n_bad, PVCLOSURE n_bad pconstantclosure_bad.SITE)
$default_at(pfunction_bad.DEFAULTS, 0) = (pdefault_bad)
$default_cache_at(S_bad.DEFAULTCACHE, pdefault_bad.ORIGIN) = eps
$call_descriptors_valid(S_bad)
S_done = $global_test_finish(S_bad, 3500)
$global_test_output(S_done.EVENTS) = $ptascii("N4:N5:N6:fresh:3:3:supplied;T")
|S_done.PARAMETERCLOSURES| = 3
S_done.DEFAULTCACHE = eps /\ S_done.CONSTCONTEXT = eps
$lookup(S_done.ENV, $ptascii("a")) = (n_cell_a)
$lookup(S_done.ENV, $ptascii("b")) = (n_cell_b)
$lookup(S_done.ENV, $ptascii("c")) = (n_cell_c)
$lookup(S_done.ENV, $ptascii("supplied")) = (n_cell_supplied)
S_done.STORE[n_cell_a] = DEFINED (POBJECT n_first)
S_done.STORE[n_cell_b] = DEFINED (POBJECT n_second)
S_done.STORE[n_cell_c] = DEFINED (POBJECT n_supplied)
S_done.STORE[n_cell_supplied] = DEFINED (POBJECT n_supplied)
n_first =/= n_second /\ n_first =/= n_supplied
$constant_callable_record(S_done.CONSTANTCLOSURES, n_supplied) = eps
$parameter_callable_record(S_done.PARAMETERCLOSURES, n_supplied) = eps
$parameter_callable_records_valid(S_done, S_done.PARAMETERCLOSURES)
$constant_callable_record_valid(S_done, pconstantclosure_bad)
S_roots = $prune_allocations(S_done[.ENV = eps][.GLOBALTABLE = eps][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)])
~((HOBJECT n_bad) <- S_roots.ALLOCATIONS)
~((HOBJECT n_first) <- S_roots.ALLOCATIONS)
~((HOBJECT n_second) <- S_roots.ALLOCATIONS)
$parameter_callable_records_valid(S_roots, S_roots.PARAMETERCLOSURES)
''')
CHECKS['parameter-global-source-receiver']=premises(r'''
S = $parameter_test_seek(S_initial[.COMPLETION = NORMAL], 15, 1800)
S.CURRENT = (pcallcontext)
pcallcontext.TARGET = CLOSURE_TARGET n_maker
pcallcontext.LEXICAL_CLASS = eps /\ pcallcontext.CALLED_CLASS = eps /\ pcallcontext.RECEIVER = eps
$function_at(S.CLOSURETEMPLATES, pcallcontext.FUNCTION) = (pfunction)
S.RESULT = KNOWN (POBJECT n_first)
$constant_callable_record(S.CONSTANTCLOSURES, n_first) = (pconstantclosure_first)
$parameter_callable_header(S, pconstantclosure_first) = (pparameterclosure_first)
pparameterclosure_first.EVIDENCE = (PARAMETER_SOURCE n_maker)
pparameterclosure_first.SCOPE = eps /\ pparameterclosure_first.INDEX = 0
S.OBJECTS[n_first] = CONSTANTCLOSURE pconstantclosure_first.SITE (PARAMETERSOURCECLOSURE n_maker (REALCLOSURE pconstantclosure_first.SITE eps eps))
$object_body(S.OBJECTS[n_maker]) = REALCLOSURE pfunction.ORIGIN pitem_maker* pstaticcell_maker*
$parameter_callable_current_evidence(S, pfunction) = (PARAMETER_SOURCE n_maker)
$parameter_callable_scope_valid(S, pparameterclosure_first, pfunction)
$parameter_callable_real_unscoped(S, n_first)
$parameter_default_transfer_valid(S, pfunction, 0, POBJECT n_first, PVCLOSURE n_first pconstantclosure_first.SITE)
~$parameter_callable_scope_valid(S, pparameterclosure_first[.EVIDENCE = eps], pfunction)
~$parameter_callable_scope_valid(S, pparameterclosure_first[.EVIDENCE = (PARAMETER_SOURCE n_first)], pfunction)
~$parameter_callable_scope_valid(S, pparameterclosure_first[.EVIDENCE = (PARAMETER_SOURCE $(|S.OBJECTS| + 1))], pfunction)
~$parameter_callable_scope_valid(S, pparameterclosure_first[.SCOPE = (pfunction.ORIGIN)], pfunction)
~$parameter_callable_scope_valid(S[.OBJECTS = $object_set(S.OBJECTS, n_maker, REALCLOSURE pconstantclosure_first.SITE pitem_maker* pstaticcell_maker*)], pparameterclosure_first, pfunction)
$call_descriptors_valid(S)
S_second = $parameter_test_seek(S, 16, 1800)
S_second.CURRENT = (pcallcontext_second)
pcallcontext_second.TARGET = CLOSURE_TARGET n_maker_clone
n_maker =/= n_maker_clone
$object_body(S_second.OBJECTS[n_maker_clone]) = REALCLOSURE pfunction.ORIGIN pitem_clone* pstaticcell_clone*
S_second.RESULT = KNOWN (POBJECT n_second)
n_first =/= n_second
$constant_callable_record(S_second.CONSTANTCLOSURES, n_second) = (pconstantclosure_second)
$parameter_callable_header(S_second, pconstantclosure_second) = (pparameterclosure_second)
pparameterclosure_second.EVIDENCE = (PARAMETER_SOURCE n_maker_clone)
$parameter_callable_scope_valid(S_second, pparameterclosure_second, pfunction)
$parameter_callable_current_evidence(S_second, pfunction) = (PARAMETER_SOURCE n_maker_clone)
$call_descriptors_valid(S_second)
S_done = $global_test_finish(S_second, 4500)
$global_test_output(S_done.EVENTS) = $ptascii("fresh:1:1:2:2")
S_done.DEFAULTCACHE = eps
~((HOBJECT n_maker) <- S_done.ALLOCATIONS)
~((HOBJECT n_maker_clone) <- S_done.ALLOCATIONS)
~((HOBJECT n_first) <- S_done.ALLOCATIONS)
$parameter_callable_header(S_done, pconstantclosure_first) = (pparameterclosure_first)
$parameter_callable_header(S_done, pconstantclosure_second) = (pparameterclosure_second)
$parameter_callable_records_valid(S_done, S_done.PARAMETERCLOSURES)
$lookup(S_done.ENV, $ptascii("clone")) = (n_cell_clone)
S_done.STORE[n_cell_clone] = DEFINED (POBJECT n_clone)
$object_body(S_done.OBJECTS[n_clone]) = REALCLOSURE pconstantclosure_first.SITE eps pstaticcell_child*
$constant_callable_record(S_done.CONSTANTCLOSURES, n_clone) = eps
$parameter_callable_record(S_done.PARAMETERCLOSURES, n_clone) = eps
$parameter_callable_real_unscoped(S_done, n_clone)
$closure_scope_at(S_done.CLOSURESCOPES, n_clone) = eps
$closure_binding_at(S_done.CLOSUREBINDINGS, n_clone) = eps
~$internal_closure_object(S_done, n_clone)
~$parameter_callable_real_unscoped(S_done[.CONSTANTCLOSURES = eps], n_clone)
S_done.OBJECTS[n_second] = CONSTANTCLOSURE pconstantclosure_second.SITE (PARAMETERSOURCECLOSURE n_maker_clone (REALCLOSURE pconstantclosure_second.SITE eps pstaticcell_second*))
S_same_index = S_done[.OBJECTS[n_second] = $object_body(S_done.OBJECTS[n_second])]
S_same_index.OBJECTS[n_second] = REALCLOSURE pconstantclosure_second.SITE eps pstaticcell_second*
~$parameter_callable_real_unscoped(S_same_index, n_second)
$heap_owners($heap_graph(S_done), HOBJECT n_maker) = 0
$heap_owners($heap_graph(S_done), HOBJECT n_maker_clone) = 0
$heap_owners($heap_graph(S_done), HOBJECT n_clone) = 1
S_roots = $prune_allocations(S_done[.ENV = eps][.GLOBALTABLE = eps][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)])
~((HOBJECT n_clone) <- S_roots.ALLOCATIONS)
~((HOBJECT n_second) <- S_roots.ALLOCATIONS)
$parameter_callable_records_valid(S_roots, S_roots.PARAMETERCLOSURES)
''')

CHECKS['parameter-global-rebound-retired-maker']=premises(r'''
S = $parameter_test_seek(S_initial[.COMPLETION = NORMAL], 15, 1800)
S.CURRENT = (pcallcontext)
pcallcontext.TARGET = CLOSURE_TARGET n_maker
$function_at(S.CLOSURETEMPLATES, pcallcontext.FUNCTION) = (pfunction)
S.RESULT = KNOWN (POBJECT n_unscoped)
$constant_callable_record(S.CONSTANTCLOSURES, n_unscoped) = (pconstantclosure_unscoped)
$parameter_callable_header(S, pconstantclosure_unscoped) = (pparameterclosure_unscoped)
pparameterclosure_unscoped.EVIDENCE = (PARAMETER_SOURCE n_maker)
S.OBJECTS[n_unscoped] = CONSTANTCLOSURE pconstantclosure_unscoped.SITE (PARAMETERSOURCECLOSURE n_maker (REALCLOSURE pconstantclosure_unscoped.SITE eps eps))
$parameter_callable_scope_valid(S, pparameterclosure_unscoped, pfunction)
$parameter_callable_real_unscoped(S, n_unscoped)
$call_descriptors_valid(S)
S_erased = S[.OBJECTS[n_unscoped] = CONSTANTCLOSURE pconstantclosure_unscoped.SITE ($object_body(S.OBJECTS[n_unscoped]))]
$parameter_callable_header(S_erased, pconstantclosure_unscoped) = eps
~$parameter_callable_birth(S_erased, pconstantclosure_unscoped, pparameterclosure_unscoped)
~$parameter_callable_scope_valid(S_erased, pparameterclosure_unscoped, pfunction)
~$parameter_callable_real_unscoped(S_erased, n_unscoped)
S_wrong = S[.OBJECTS[n_unscoped] = CONSTANTCLOSURE pconstantclosure_unscoped.SITE (PARAMETERSOURCECLOSURE n_unscoped ($object_body(S.OBJECTS[n_unscoped])))]
$parameter_callable_header(S_wrong, pconstantclosure_unscoped) = eps
S_bound = $parameter_test_seek(S, 17, 1800)
S_bound.CURRENT = (pcallcontext_bound)
pcallcontext_bound.TARGET = CLOSURE_TARGET n_bound
S_bound.RESULT = KNOWN (POBJECT n_scoped)
$constant_callable_record(S_bound.CONSTANTCLOSURES, n_scoped) = (pconstantclosure_scoped)
$parameter_callable_header(S_bound, pconstantclosure_scoped) = (pparameterclosure_scoped)
pparameterclosure_scoped.EVIDENCE = (PARAMETER_SCOPE pclosureevidence)
$closure_evidence_object(pclosureevidence) = n_bound
pparameterclosure_scoped.SCOPE = (porigin_owner)
$closure_scope_at(S_bound.CLOSURESCOPES, n_scoped) = (pclosurescope)
pclosurescope.LEXICAL = porigin_owner /\ pclosurescope.CALLED = porigin_owner /\ pclosurescope.RECEIVER = eps
$parameter_callable_real_scope_valid(S_bound, pconstantclosure_scoped.SITE, pclosurescope)
$call_descriptors_valid(S_bound)
S_done = $global_test_finish(S_bound, 4500)
$global_test_output(S_done.EVENTS) = $ptascii("fresh:ParameterGlobalBoundOwner")
S_done.DEFAULTCACHE = eps
~((HOBJECT n_maker) <- S_done.ALLOCATIONS) /\ ~((HOBJECT n_bound) <- S_done.ALLOCATIONS)
$closure_binding_at(S_done.CLOSUREBINDINGS, n_bound) = eps
$closure_scope_at(S_done.CLOSURESCOPES, n_bound) = eps
$object_body(S_done.OBJECTS[n_bound]) = REALCLOSURE pfunction.ORIGIN pitem* pstaticcell*
$parameter_callable_records_valid(S_done, S_done.PARAMETERCLOSURES)
pparameterclosure_forged = pparameterclosure_scoped[.SCOPE = eps][.EVIDENCE = (PARAMETER_SOURCE n_bound)]
S_forged = S_done[.PARAMETERCLOSURES = [pparameterclosure_unscoped, pparameterclosure_forged]][.CLOSURESCOPES = eps]
~$parameter_callable_scope_valid(S_forged, pparameterclosure_forged, pfunction)
$parameter_callable_header(S_forged, pconstantclosure_scoped) = eps
~$parameter_callable_birth(S_forged, pconstantclosure_scoped, pparameterclosure_forged)
~$parameter_callable_real_unscoped(S_forged, n_scoped)
$heap_owners($heap_graph(S_done), HOBJECT n_maker) = 0 /\ $heap_owners($heap_graph(S_done), HOBJECT n_bound) = 0
$heap_owners($heap_graph(S_done), HOBJECT n_unscoped) = 1 /\ $heap_owners($heap_graph(S_done), HOBJECT n_scoped) = 1
S_roots = $prune_allocations(S_done[.ENV = eps][.GLOBALTABLE = eps][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)])
~((HOBJECT n_unscoped) <- S_roots.ALLOCATIONS) /\ ~((HOBJECT n_scoped) <- S_roots.ALLOCATIONS)
$parameter_callable_records_valid(S_roots, S_roots.PARAMETERCLOSURES)
''')
CHECKS['parameter-unscoped-fcc-forms']=premises(r'''
S = $parameter_test_seek(S_initial[.COMPLETION = NORMAL], 15, 1800)
S.CURRENT = (pcallcontext)
pcallcontext.TARGET = CLOSURE_TARGET n_maker
S.RESULT = KNOWN (POBJECT n_named)
$constant_callable_record(S.CONSTANTCLOSURES, n_named) = (pconstantclosure_named)
$parameter_callable_header(S, pconstantclosure_named) = (pparameterclosure_named)
pparameterclosure_named.EVIDENCE = (PARAMETER_SOURCE n_maker)
S.OBJECTS[n_named] = CONSTANTCLOSURE pconstantclosure_named.SITE (PARAMETERSOURCECLOSURE n_maker (NAMEDCLOSURE porigin_named))
$constant_callable_function(S, pconstantclosure_named.SITE, pconstantclosure_named.PREFIX) = (pfunction_named)
pfunction_named.ORIGIN = porigin_named
$parameter_callable_birth(S, pconstantclosure_named, pparameterclosure_named)
$call_descriptors_valid(S)
S_method = $parameter_test_seek(S, 18, 1800)
S_method.RESULT = KNOWN (POBJECT n_method)
$constant_callable_record(S_method.CONSTANTCLOSURES, n_method) = (pconstantclosure_method)
$parameter_callable_header(S_method, pconstantclosure_method) = (pparameterclosure_method)
pparameterclosure_method.EVIDENCE = (PARAMETER_SOURCE n_maker)
S_method.OBJECTS[n_method] = CONSTANTCLOSURE pconstantclosure_method.SITE (PARAMETERSOURCECLOSURE n_maker (METHODCLOSURE porigin_method pconstantclosure_method.SITE porigin_called eps))
$class_method_origin(S_method.CLASSES, porigin_method) = (pmethoddesc)
$closure_scope_at(S_method.CLOSURESCOPES, n_method) = (pclosurescope_method)
$parameter_callable_method_live(S_method, pmethoddesc, pconstantclosure_method.SITE, porigin_called, pclosurescope_method)
$parameter_callable_birth(S_method, pconstantclosure_method, pparameterclosure_method)
$call_descriptors_valid(S_method)
S_done = $global_test_finish(S_method, 4500)
$global_test_output(S_done.EVENTS) = $ptascii("fresh:fresh:5:ParameterUnscopedMethodOwner:ParameterUnscopedMethodOwner")
|S_done.PARAMETERCLOSURES| = 4 /\ |S_done.CONSTANTCLOSURES| = 4
S_done.DEFAULTCACHE = eps
~((HOBJECT n_maker) <- S_done.ALLOCATIONS) /\ ~((HOBJECT n_named) <- S_done.ALLOCATIONS) /\ ~((HOBJECT n_method) <- S_done.ALLOCATIONS)
$parameter_callable_records_valid(S_done, S_done.PARAMETERCLOSURES)
$parameter_callable_cached_function(S_done, pconstantclosure_named.SITE) = (pfunction_named)
$parameter_callable_cached_method(S_done, pconstantclosure_method.SITE) = (pmethoddesc)
$lookup(S_done.ENV, $ptascii("clone")) = (n_cell_clone)
S_done.STORE[n_cell_clone] = DEFINED (POBJECT n_clone)
S_done.OBJECTS[n_clone] = METHODCLOSURE porigin_method pconstantclosure_method.SITE porigin_called eps
$constant_callable_record(S_done.CONSTANTCLOSURES, n_clone) = eps /\ $parameter_callable_record(S_done.PARAMETERCLOSURES, n_clone) = eps
$closure_scope_at(S_done.CLOSURESCOPES, n_clone) = (pclosurescope_clone)
$parameter_callable_method_live(S_done, pmethoddesc, pconstantclosure_method.SITE, porigin_called, pclosurescope_clone)
~$parameter_callable_method_live(S_done[.CONSTANTCLOSURES = eps], pmethoddesc, pconstantclosure_method.SITE, porigin_called, pclosurescope_clone)
$heap_owners($heap_graph(S_done), HOBJECT n_maker) = 0
$heap_owners($heap_graph(S_done), HOBJECT n_clone) = 1
S_roots = $prune_allocations(S_done[.ENV = eps][.GLOBALTABLE = eps][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)])
~((HOBJECT n_clone) <- S_roots.ALLOCATIONS)
$parameter_callable_records_valid(S_roots, S_roots.PARAMETERCLOSURES)
''')

def prepare(out):
    names=('SOURCES','FILES','EVALS','PREFIX','CHECKS')
    saved={name:getattr(global_protocol,name) for name in names}
    try:
        for name in names:setattr(global_protocol,name,globals()[name])
        return global_protocol.prepare(out)
    finally:
        for name,value in saved.items():setattr(global_protocol,name,value)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--prepare-only');parser.add_argument('--output')
    arguments=parser.parse_args()
    out=Path(arguments.prepare_only or arguments.output or str(Path(tempfile.mkdtemp(prefix='parameter-constant-callable-',dir=ROOT/'.tools'))/'prepared'))
    if arguments.prepare_only:
        prepare(out)
    else:
        watched=[Path(__file__),Path(global_protocol.__file__)]
        before={str(p):base.sha(p) for p in watched}
        original=base.prepare;original_flags=base.RUNNER_FLAGS
        try:
            base.prepare=prepare;base.RUNNER_FLAGS={'parameter-rebound-scope':['--sl']};base.run(out)
        finally:
            base.prepare=original;base.RUNNER_FLAGS=original_flags
        report=json.loads((out/'report.json').read_text())
        report.update(protocol_inputs=before,protocols_unchanged=before=={str(p):base.sha(p) for p in watched})
        if not report['protocols_unchanged']:report['result']='failed'
        (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
        assert report['protocols_unchanged'],'protocol changed'
    print(out)

if __name__=='__main__':main()
