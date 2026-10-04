#!/usr/bin/env python3
"""Source-derived global const entry, transfer, registration and owner guards."""
import argparse,base64,hashlib,json,os,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tests/semantics'))
import static_types as types
from recorded_worker import Worker
import deferred_static_default_protocol as base
ENV=base.ENV
SOURCES={'global-constant-timing-fallback': '<?php\n'
                                    'namespace {\n'
                                    "    function selected() { return 'global'; }\n"
                                    '}\n'
                                    'namespace GlobalConstantNamespace {\n'
                                    "    try { $before = F; } catch (\\Error $e) { echo 'U:'; }\n"
                                    '    const F = selected(...);\n'
                                    "    const VALUES = [F, static function () { return 'real'; "
                                    '}];\n'
                                    '    $f = F;\n'
                                    '    $values = VALUES;\n'
                                    '    if (true) {\n'
                                    "        function selected() { return 'late'; }\n"
                                    '    }\n'
                                    "    echo $f(), ':', $values[0](), ':', selected(), ':',\n"
                                    "        (F === $f ? '1' : '0'), ':', $values[1]();\n"
                                    '    unset($f, $values);\n'
                                    '    $again = F;\n'
                                    "    echo ';', $again();\n"
                                    '}\n',
 'global-constant-inherited-include': '<?php\n'
                                      'class GlobalScopeA {\n'
                                      "    private const TOKEN = 'secret';\n"
                                      '    private static function read() {\n'
                                      "        return self::class . '/' . get_called_class() . ':' "
                                      '. self::TOKEN;\n'
                                      '    }\n'
                                      '    public function load() {\n'
                                      '        include __DIR__ . '
                                      "'/global-constant-inherited-scope.inc.php';\n"
                                      '    }\n'
                                      '}\n'
                                      'class GlobalScopeD extends GlobalScopeA {}\n'
                                      '$receiver = new GlobalScopeD;\n'
                                      '$receiver->load();\n'
                                      '$real = INCLUDED_REAL;\n'
                                      '$method = INCLUDED_METHOD;\n'
                                      'unset($receiver);\n'
                                      "echo $real(), ';', $method();\n",
 'global-constant-partial-retry': '<?php\n'
                                  'try {\n'
                                  '    include __DIR__ . '
                                  "'/global-constant-partial-retry.inc.php';\n"
                                  '} catch (Error $e) {\n'
                                  "    echo 'F:';\n"
                                  '}\n'
                                  '$first = FIRST;\n'
                                  'if (true) {\n'
                                  "    function missing() { return 'ok'; }\n"
                                  '}\n'
                                  'set_error_handler(static function ($severity, $message) {\n'
                                  "    echo 'D:';\n"
                                  '    return true;\n'
                                  '});\n'
                                  "include __DIR__ . '/global-constant-partial-retry.inc.php';\n"
                                  'restore_error_handler();\n'
                                  '$again = FIRST;\n'
                                  '$second = SECOND;\n'
                                  "echo ($first === $again ? '1' : '0'), ':', $second();\n",
 'global-constant-reentry': '<?php\n'
                            '$depth = 0;\n'
                            '$inner = null;\n'
                            'set_error_handler(static function ($severity, $message) use (&$depth, '
                            '&$inner) {\n'
                            "    echo $severity, ':';\n"
                            '    if ($severity === E_DEPRECATED && $depth === 0) {\n'
                            '        $depth = 1;\n'
                            '        try { $before = REENTRANT_VALUE; } catch (Error $e) { echo '
                            "'U:'; }\n"
                            "        include __DIR__ . '/global-constant-reentry.inc.php';\n"
                            '        $inner = REENTRANT_VALUE[0];\n'
                            '    }\n'
                            '    return true;\n'
                            '});\n'
                            "include __DIR__ . '/global-constant-reentry.inc.php';\n"
                            'restore_error_handler();\n'
                            '$installed = REENTRANT_VALUE[0];\n'
                            "echo ($inner === $installed ? '1' : '0'), ':', REENTRANT_VALUE[1];\n",
 'global-constant-throw-retry': '<?php\n'
                                'set_error_handler(static function ($severity, $message) {\n'
                                "    echo $severity, ':';\n"
                                "    throw new Error('stop');\n"
                                '});\n'
                                'try {\n'
                                "    include __DIR__ . '/global-constant-throw-retry.inc.php';\n"
                                '} catch (Error $e) {\n'
                                "    echo 'F:';\n"
                                '}\n'
                                "try { $before = THROW_VALUE; } catch (Error $e) { echo 'U:'; }\n"
                                'restore_error_handler();\n'
                                'set_error_handler(static function ($severity, $message) {\n'
                                "    echo $severity, ':';\n"
                                '    return true;\n'
                                '});\n'
                                "include __DIR__ . '/global-constant-throw-retry.inc.php';\n"
                                'restore_error_handler();\n'
                                '$values = THROW_VALUE;\n'
                                '$clone = clone $values[0];\n'
                                'unset($values);\n'
                                "echo $clone(), ':', THROW_VALUE[1];\n",
 'global-constant-raw-trait-notice': '<?php\n'
                                     'trait GlobalRawTrait {\n'
                                     "    public static function m() { return 'trait'; }\n"
                                     '}\n'
                                     'set_error_handler(static function ($severity) {\n'
                                     "    echo $severity, ':';\n"
                                     "    throw new Error('stop');\n"
                                     '});\n'
                                     'try {\n'
                                     "    eval('const RAW_TRAIT_F = GlobalRawTrait::m(...);');\n"
                                     '} catch (Error $e) {\n'
                                     "    echo 'F:';\n"
                                     '}\n'
                                     'try {\n'
                                     '    $missing = RAW_TRAIT_F;\n'
                                     '} catch (Error $e) {\n'
                                     "    echo 'U:';\n"
                                     '}\n'
                                     'set_error_handler(static function ($severity) {\n'
                                     "    echo $severity, ':';\n"
                                     '    return true;\n'
                                     '});\n'
                                     "eval('const RAW_TRAIT_F = GlobalRawTrait::m(...);');\n"
                                     '$f = RAW_TRAIT_F;\n'
                                     '$clone = clone $f;\n'
                                     'unset($f, $missing, $e);\n'
                                     'echo $clone();\n',
 'global-constant-duplicate-alias-shadow': '<?php\n'
                                           'namespace {\n'
                                           "    const SEED = static function () { return 'global'; "
                                           '};\n'
                                           '}\n'
                                           'namespace GlobalAliasScope {\n'
                                           '    const DUP = SEED;\n'
                                           '    set_error_handler(static function ($severity) {\n'
                                           "        echo $severity, ':';\n"
                                           "        eval('namespace GlobalAliasScope; const SEED = "
                                           'static function () { return "late"; };\');\n'
                                           '        return true;\n'
                                           '    });\n'
                                           "    eval('namespace GlobalAliasScope; const DUP = "
                                           '[SEED, static function () { return "discarded"; '
                                           "}];');\n"
                                           '    $original = DUP;\n'
                                           '    $late = SEED;\n'
                                           "    echo $original(), ':', $late(), ':', DUP === "
                                           "\\SEED ? '1' : '0', ';';\n"
                                           '}\n'
                                           'namespace GlobalAliasThrowScope {\n'
                                           '    const DUP = SEED;\n'
                                           '    set_error_handler(static function ($severity) {\n'
                                           "        echo $severity, ':';\n"
                                           "        eval('namespace GlobalAliasThrowScope; const "
                                           'SEED = static function () { return "late"; };\');\n'
                                           "        throw new \\Error('stop');\n"
                                           '    });\n'
                                           '    try {\n'
                                           "        eval('namespace GlobalAliasThrowScope; const "
                                           'DUP = [SEED, static function () { return "discarded"; '
                                           "}];');\n"
                                           '    } catch (\\Error $e) {\n'
                                           "        echo 'F:';\n"
                                           '    }\n'
                                           '    $original = DUP;\n'
                                           '    $late = SEED;\n'
                                           "    echo $original(), ':', $late(), ':', DUP === "
                                           "\\SEED ? '1' : '0';\n"
                                           '}\n'}
FILES={'global-constant-inherited-include': ('global-constant-inherited-scope.inc.php',
                                       '<?php\n'
                                       'const INCLUDED_REAL = static function () {\n'
                                       "    return self::class . '/' . get_called_class() . ':' . "
                                       'self::TOKEN;\n'
                                       '};\n'
                                       'const INCLUDED_METHOD = self::read(...);\n'),
 'global-constant-partial-retry': ('global-constant-partial-retry.inc.php',
                                   '<?php\n'
                                   "const FIRST = static function () { return 'first'; }, SECOND = "
                                   'missing(...);\n'),
 'global-constant-reentry': ('global-constant-reentry.inc.php',
                             '<?php\n'
                             "const REENTRANT_VALUE = [static function () { return 'ok'; }, "
                             'E_STRICT + 0];\n'),
 'global-constant-throw-retry': ('global-constant-throw-retry.inc.php',
                                 '<?php\n'
                                 "const THROW_VALUE = [static function () { return 'ok'; }, "
                                 'E_STRICT + 0];\n')}
EVALS={'global-constant-raw-trait-notice': ['const RAW_TRAIT_F = GlobalRawTrait::m(...);'],
 'global-constant-duplicate-alias-shadow': ['namespace GlobalAliasScope; const SEED = static '
                                            'function () { return "late"; };',
                                            'namespace GlobalAliasScope; const DUP = [SEED, static '
                                            'function () { return "discarded"; }];',
                                            'namespace GlobalAliasThrowScope; const SEED = static '
                                            'function () { return "late"; };',
                                            'namespace GlobalAliasThrowScope; const DUP = [SEED, '
                                            'static function () { return "discarded"; }];']}

PREFIX=r'''
dec $global_test_resume(pstate) : pstate
def $global_test_resume(S) = S[.COMPLETION = NORMAL] -- if S.COMPLETION = BUDGET
def $global_test_resume(S) = S -- otherwise
dec $global_test_service(pstate) : pstate
dec $global_test_next(pstate) : pstate
def $global_test_next(S) = $global_test_service($global_test_resume($drive_steps(S, 1)))
  -- if S.COMPLETION = NORMAL
def $global_test_next(S) = $global_test_service(S)
  -- if S.COMPLETION = SOURCE_PENDING
dec $global_test_output_piece(pevent) : ptbytes
def $global_test_output_piece(OUTPUT ptbytes) = ptbytes
def $global_test_output_piece(pevent) = eps -- otherwise
dec $global_test_output(pevent*) : ptbytes
def $global_test_output(eps) = eps
def $global_test_output(pevent :: pevent_tail*) = $global_test_output_piece(pevent) ++ $global_test_output(pevent_tail*)
dec $global_test_name(pstate, porigin, ptbytes) : bool
def $global_test_name(S, porigin_decl, ptbytes) = true
  -- if $constant_declaration(S, porigin_decl) = ((preqbytes, z))
  -- if $user_constant_key(preqbytes) = ptbytes
def $global_test_name(S, porigin_decl, ptbytes) = false -- otherwise
dec $global_test_stage(pstate, ptbytes, nat) : bool
def $global_test_stage(S, ptbytes, 0) = true
  -- if S.ORIGIN = (porigin_decl)
  -- if S.TODO = (CONSTANT_INIT expression) :: ptask_tail*
  -- if $global_test_name(S, porigin_decl, ptbytes)
def $global_test_stage(S, ptbytes, 1) = true
  -- if S.TODO = (CONSTANT_BIND porigin_decl) :: ptask_tail*
  -- if $global_test_name(S, porigin_decl, ptbytes)
def $global_test_stage(S, ptbytes, 2) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = GLOBAL_CONSTANT_DUPLICATE porigin_decl pvalue pvalueclass n_constants z
  -- if $global_test_name(S, porigin_decl, ptbytes)
def $global_test_stage(S, ptbytes, 3) = true
  -- if S.TODO = (GLOBAL_CONSTANT_DUPLICATE porigin_decl pvalue pvalueclass n_constants z) :: ptask_tail*
  -- if $global_test_name(S, porigin_decl, ptbytes)
def $global_test_stage(S, ptbytes, 4) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = GLOBAL_CONSTANT_METHOD_RESUME porigin_site porigin_method porigin_called n_prefix
  -- if S.CONSTCONTEXT = (pconstantcontext)
  -- if $global_test_name(S, pconstantcontext.ORIGIN, ptbytes)
def $global_test_stage(S, ptbytes, 5) = true
  -- if S.TODO = (GLOBAL_CONSTANT_METHOD_RESUME porigin_site porigin_method porigin_called n_prefix) :: ptask_tail*
  -- if S.CONSTCONTEXT = (pconstantcontext)
  -- if $global_test_name(S, pconstantcontext.ORIGIN, ptbytes)
def $global_test_stage(S, ptbytes, 6) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = DEPRECATED_CONSTANT_RESULT pdeprecatedconstant
  -- if S.CONSTCONTEXT = (pconstantcontext)
  -- if $global_test_name(S, pconstantcontext.ORIGIN, ptbytes)
def $global_test_stage(S, ptbytes, 7) = ($global_test_output(S.EVENTS) = ptbytes)
def $global_test_stage(S, ptbytes, 8) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = CLOSURE_TARGET n_object
  -- if $constant_callable_record(S.CONSTANTCLOSURES, n_object) = (pconstantclosure)
  -- if $global_test_name(S, pconstantclosure.DECL, ptbytes)
def $global_test_stage(S, ptbytes, n_stage) = false -- otherwise
dec $global_test_find(pstate, ptbytes, nat, nat) : pstate
def $global_test_find(S, ptbytes, n_stage, n_limit) = S
  -- if $global_test_stage(S, ptbytes, n_stage)
def $global_test_find(S, ptbytes, n_stage, n_limit) = $global_test_find(S_next, ptbytes, n_stage, n_rest)
  -- if ~$global_test_stage(S, ptbytes, n_stage)
  -- if $(n_limit > 0)
  -- if (S.COMPLETION = NORMAL \/ S.COMPLETION = SOURCE_PENDING) /\ ~S.COMPILESTOP
  -- if n_rest = $(n_limit - 1)
  -- if S_next = $global_test_next(S)
dec $global_test_finish(pstate, nat) : pstate
def $global_test_finish(S, n_limit) = S
  -- if S.COMPLETION = NORMAL /\ S.TODO = eps
def $global_test_finish(S, n_limit) = $global_test_finish(S_next, n_rest)
  -- if ~(S.COMPLETION = NORMAL /\ S.TODO = eps)
  -- if $(n_limit > 0)
  -- if (S.COMPLETION = NORMAL \/ S.COMPLETION = SOURCE_PENDING) /\ ~S.COMPILESTOP
  -- if n_rest = $(n_limit - 1)
  -- if S_next = $global_test_next(S)
dec $global_test_entry_prefix(pdeclaration*, nat, nat) : nat?
def $global_test_entry_prefix(eps, n_unit, n_count) = eps
def $global_test_entry_prefix(pdeclaration :: pdeclaration_tail*, n_unit, n_count) = (n_count)
  -- if $declaration_enter_item(pdeclaration, n_unit)
def $global_test_entry_prefix(pdeclaration :: pdeclaration_tail*, n_unit, n_count) = $global_test_entry_prefix(pdeclaration_tail*, n_unit, $(n_count + 1))
  -- if ~$declaration_enter_item(pdeclaration, n_unit)
'''

def premises(text):
    return [line.strip() for line in text.splitlines() if line.strip()]

CHECKS={}
CHECKS['global-constant-timing-fallback']=premises(r'''
ptbytes_f = $user_constant_key($ptascii("GlobalConstantNamespace") ++ [92] ++ $ptascii("F"))
ptbytes_values = $user_constant_key($ptascii("GlobalConstantNamespace") ++ [92] ++ $ptascii("VALUES"))
S_init = $global_test_find(S_initial[.COMPLETION = NORMAL], ptbytes_f, 0, 600)
S_init.TODO = (CONSTANT_INIT expression) :: ptask_init*
$constant_initializer_valid(S_init, expression)
~$constant_initializer_valid(S_init, NScalarInt (INTEGER 999) eps)
~$call_task_valid(S_init, CONSTANT_INIT (NScalarInt (INTEGER 999) eps))
S_f = $global_test_find(S_init, ptbytes_f, 1, 600)
S_f.TODO = (CONSTANT_BIND porigin_f) :: ptask_f*
S_f.RESULT = KNOWN (POBJECT n_f)
$constant_callable_record(S_f.CONSTANTCLOSURES, n_f) = (pconstantclosure_f)
pconstantclosure_f.DECL = porigin_f
$global_constant_callable_context(S_f, pconstantclosure_f.SITE) = ((porigin_decl, porigin_scope?))
porigin_decl = porigin_f
porigin_scope? = eps
$constant_context_valid(S_f)
$global_constant_callable_header(S_f, pconstantclosure_f)
~$global_constant_callable_active(S_f[.DECLARATIONS = eps], pconstantclosure_f.SITE)
~$global_constant_callable_active(S_f[.TODO = ptask_f*], pconstantclosure_f.SITE)
~$global_constant_callable_active(S_f[.CONSTCONTEXT = eps], pconstantclosure_f.SITE)
$closure_scope_at(S_f.CLOSURESCOPES, n_f) = eps
S_values = $global_test_find(S_f, ptbytes_values, 1, 700)
S_values.TODO = (CONSTANT_BIND porigin_values) :: ptask_values*
S_values.RESULT = KNOWN (PARRAY n_values)
S_values.ARRAYS[n_values].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_f)), ENTRY (KINT 1) (DIRECT (POBJECT n_real))]
$constant_callable_record(S_values.CONSTANTCLOSURES, n_real) = (pconstantclosure_real)
pconstantclosure_real.DECL = porigin_values
pvalueclass_values = $constant_received_class(S_values, porigin_values)
$constant_value_class_valid(S_values, PARRAY n_values, pvalueclass_values)
$global_constant_transfer_valid(S_values, porigin_values, pvalueclass_values, S_values.USERCONSTANTS)
~$global_constant_transfer_valid(S_values, porigin_f, pvalueclass_values, S_values.USERCONSTANTS)
S_foreign = S_values[.ARRAYS = $array_replace(S_values.ARRAYS, n_values, S_values.ARRAYS[n_values][.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_real)), ENTRY (KINT 1) (DIRECT (POBJECT n_real))]])]
~$constant_value_class_valid(S_foreign, PARRAY n_values, pvalueclass_values)
$global_constant_transfer_valid(S_foreign, porigin_values, pvalueclass_values, S_foreign.USERCONSTANTS)
S_rejected = $global_test_next(S_foreign)
S_rejected.COMPLETION = UNSUPPORTED "global constant object transfer"
~$global_constant_callable_header(S_values, pconstantclosure_f[.DECL = porigin_values])
~$constant_callable_record_valid(S_values, pconstantclosure_f[.SITE = pconstantclosure_real.SITE])
S_done = $global_test_finish(S_values, 2400)
S_done.COMPLETION = NORMAL /\ S_done.TODO = eps
$global_test_output(S_done.EVENTS) = $ptascii("U:global:global:late:1:real;global")
$user_constants_valid(S_done, S_done.USERCONSTANTS)
$constant_callable_records_valid(S_done, S_done.CONSTANTCLOSURES)
S_done.CONSTANTCLOSURES = S_values.CONSTANTCLOSURES
$user_constant_at(S_done.USERCONSTANTS, ptbytes_f) = (puserconstant_f)
puserconstant_f.VALUE = POBJECT n_f
S_roots = $prune_allocations(S_done[.ENV = eps][.GLOBALTABLE = eps][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)])
(HOBJECT n_f) <- S_roots.ALLOCATIONS
(HOBJECT n_real) <- S_roots.ALLOCATIONS
(HARRAY n_values) <- S_roots.ALLOCATIONS
S_roots.USERCONSTANTS = S_done.USERCONSTANTS
$user_constants_valid(S_roots, S_roots.USERCONSTANTS)
$constant_callable_records_valid(S_roots, S_roots.CONSTANTCLOSURES)
''')
CHECKS['global-constant-inherited-include']=premises(r'''
S_real = $global_test_find(S_initial[.COMPLETION = NORMAL], $ptascii("INCLUDED_REAL"), 1, 1200)
S_real.TODO = (CONSTANT_BIND porigin_real) :: ptask_real*
S_real.RESULT = KNOWN (POBJECT n_real)
$class_named(S_real.CLASSNAMES, $ptascii("globalscopea")) = (porigin_a)
$class_named(S_real.CLASSNAMES, $ptascii("globalscoped")) = (porigin_d)
S_real.CURRENT = (pcallcontext)
pcallcontext.LEXICAL_CLASS = (porigin_a)
pcallcontext.CALLED_CLASS = (porigin_d)
pcallcontext.RECEIVER = (n_receiver)
$constant_callable_record(S_real.CONSTANTCLOSURES, n_real) = (pconstantclosure_real)
pconstantclosure_real.DECL = porigin_real
porigin_real = PORIGIN n_unit pcpath_real
$global_constant_scope(S_real, n_unit) = (true, porigin_scope?)
porigin_scope? = (porigin_a)
$global_constant_callable_context(S_real, pconstantclosure_real.SITE) = ((porigin_decl, porigin_entry?))
porigin_decl = porigin_real
porigin_entry? = (porigin_a)
$closure_scope_at(S_real.CLOSURESCOPES, n_real) = (pclosurescope_real)
pclosurescope_real.LEXICAL = porigin_a /\ pclosurescope_real.CALLED = porigin_a
pclosurescope_real.RECEIVER = eps /\ pclosurescope_real.CREATION = eps
$closure_scope_row_valid(S_real, pclosurescope_real)
~$global_constant_callable_active(S_real[.DECLARATIONS = eps], pconstantclosure_real.SITE)
~$global_constant_callable_header(S_real[.FILEBINDINGS = eps], pconstantclosure_real)
~$global_constant_real_scope_valid(S_real, pconstantclosure_real.SITE, pclosurescope_real[.CALLED = porigin_d])
~$global_constant_real_scope_valid(S_real, pconstantclosure_real.SITE, pclosurescope_real[.RECEIVER = (n_receiver)])
~$global_constant_real_scope_valid(S_real, pconstantclosure_real.SITE, pclosurescope_real[.LEXICAL = porigin_d][.CALLED = porigin_d])
S_method = $global_test_find(S_real, $ptascii("INCLUDED_METHOD"), 1, 500)
S_method.RESULT = KNOWN (POBJECT n_method)
$constant_callable_record(S_method.CONSTANTCLOSURES, n_method) = (pconstantclosure_method)
$object_body(S_method.OBJECTS[n_method]) = METHODCLOSURE porigin_function pconstantclosure_method.SITE porigin_a eps
$class_method_origin(S_method.CLASSES, porigin_function) = (pmethoddesc)
$closure_scope_at(S_method.CLOSURESCOPES, n_method) = (pclosurescope_method)
pclosurescope_method.LEXICAL = porigin_a /\ pclosurescope_method.CALLED = porigin_a
pclosurescope_method.RECEIVER = eps /\ pclosurescope_method.CREATION = eps
$global_constant_method_live(S_method, pmethoddesc, pconstantclosure_method.SITE, porigin_a, pclosurescope_method)
$closure_scope_row_valid(S_method, pclosurescope_method)
~$global_constant_method_live(S_method, pmethoddesc, pconstantclosure_method.SITE, porigin_d, pclosurescope_method[.CALLED = porigin_d])
~$global_constant_method_live(S_method[.CONSTANTCLOSURES = eps], pmethoddesc, pconstantclosure_method.SITE, porigin_a, pclosurescope_method)
~$global_constant_method_live(S_method[.OBJECTS = $object_set(S_method.OBJECTS, n_method, METHODCLOSURE porigin_function pconstantclosure_method.SITE porigin_a eps)], pmethoddesc, pconstantclosure_method.SITE, porigin_a, pclosurescope_method)
S_current = $global_test_find(S_method, $ptascii("INCLUDED_METHOD"), 8, 1700)
$call_current_valid(S_current)
S_current.CURRENT = (pcallcontext_method)
pcallcontext_method.LEXICAL_CLASS = (porigin_a)
pcallcontext_method.CALLED_CLASS = (porigin_a)
pcallcontext_method.RECEIVER = eps
S_done = $global_test_finish(S_current, 1800)
S_done.COMPLETION = NORMAL /\ S_done.TODO = eps
$global_test_output(S_done.EVENTS) = $ptascii("GlobalScopeA/GlobalScopeA:secret;GlobalScopeA/GlobalScopeA:secret")
S_clone = $clone_object(S_done, n_real)
S_clone.RESULT = KNOWN (POBJECT n_clone)
$constant_callable_record(S_clone.CONSTANTCLOSURES, n_clone) = eps
$closure_scope_at(S_clone.CLOSURESCOPES, n_clone) = (pclosurescope_clone)
$global_constant_real_scope_valid(S_clone, pconstantclosure_real.SITE, pclosurescope_clone)
$closure_scope_row_valid(S_clone, pclosurescope_clone)
~$global_constant_real_scope_valid(S_clone[.CONSTANTCLOSURES = eps], pconstantclosure_real.SITE, pclosurescope_clone)
S_clone_roots = $prune_allocations(S_clone[.ENV = eps][.GLOBALTABLE = eps][.BASE = BASE_VALUE (KNOWN PNULL)])
(HOBJECT n_clone) <- S_clone_roots.ALLOCATIONS
(HOBJECT n_real) <- S_clone_roots.ALLOCATIONS
(HOBJECT n_method) <- S_clone_roots.ALLOCATIONS
~((HOBJECT n_receiver) <- S_clone_roots.ALLOCATIONS)
S_roots = $prune_allocations(S_clone_roots[.RESULT = KNOWN PNULL])
~((HOBJECT n_clone) <- S_roots.ALLOCATIONS)
(HOBJECT n_real) <- S_roots.ALLOCATIONS
(HOBJECT n_method) <- S_roots.ALLOCATIONS
$constant_callable_records_valid(S_roots, S_roots.CONSTANTCLOSURES)
$user_constants_valid(S_roots, S_roots.USERCONSTANTS)
''')
CHECKS['global-constant-partial-retry']=premises(r'''
S_failed = $global_test_find(S_initial[.COMPLETION = NORMAL], $ptascii("F:"), 7, 1500)
$user_constant_at(S_failed.USERCONSTANTS, $ptascii("FIRST")) = (puserconstant_first)
puserconstant_first.VALUE = POBJECT n_first
$constant_callable_record(S_failed.CONSTANTCLOSURES, n_first) = (pconstantclosure_first)
$user_constant_at(S_failed.USERCONSTANTS, $ptascii("SECOND")) = eps
$user_constants_valid(S_failed, S_failed.USERCONSTANTS)
$constant_callable_record_valid(S_failed, pconstantclosure_first)
S_warning = $global_test_find(S_failed, $ptascii("FIRST"), 2, 1600)
S_warning.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warning*
perrorcall.RESUME = GLOBAL_CONSTANT_DUPLICATE porigin_duplicate (POBJECT n_duplicate) pvalueclass_duplicate n_constants z
porigin_duplicate =/= puserconstant_first.ORIGIN
n_duplicate =/= n_first
$constant_callable_record(S_warning.CONSTANTCLOSURES, n_duplicate) = (pconstantclosure_duplicate)
pconstantclosure_duplicate.DECL = porigin_duplicate
$global_constant_duplicate_valid(S_warning, porigin_duplicate, POBJECT n_duplicate, pvalueclass_duplicate, n_constants, z)
$error_call_valid(S_warning, perrorcall)
$task_nodes(perrorcall.RESUME) = [HOBJECT n_duplicate]
$user_constant_at(S_warning.USERCONSTANTS, $ptascii("FIRST")) = (puserconstant_first)
S_held = $prune_allocations(S_warning)
(HOBJECT n_duplicate) <- S_held.ALLOCATIONS
(HOBJECT n_first) <- S_held.ALLOCATIONS
~$global_constant_duplicate_valid(S_warning, porigin_duplicate, POBJECT n_duplicate, pvalueclass_duplicate, 0, z)
~$global_constant_duplicate_valid(S_warning, porigin_duplicate, POBJECT n_first, pvalueclass_duplicate, n_constants, z)
~$global_constant_duplicate_valid(S_warning, puserconstant_first.ORIGIN, POBJECT n_duplicate, pvalueclass_duplicate, n_constants, z)
S_resumed = $global_test_find(S_warning, $ptascii("FIRST"), 3, 1600)
$user_constant_at(S_resumed.USERCONSTANTS, $ptascii("FIRST")) = (puserconstant_first)
S_done = $global_test_finish(S_resumed, 2400)
S_done.COMPLETION = NORMAL /\ S_done.TODO = eps
$global_test_output(S_done.EVENTS) = $ptascii("F:D:1:ok")
$user_constant_at(S_done.USERCONSTANTS, $ptascii("FIRST")) = (puserconstant_first)
$user_constant_at(S_done.USERCONSTANTS, $ptascii("SECOND")) = (puserconstant_second)
puserconstant_second.VALUE = POBJECT n_second
n_second =/= n_first /\ n_second =/= n_duplicate
$constant_callable_record(S_done.CONSTANTCLOSURES, n_first) = (pconstantclosure_first)
S_roots = $prune_allocations(S_done[.ENV = eps][.GLOBALTABLE = eps][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)])
(HOBJECT n_first) <- S_roots.ALLOCATIONS
(HOBJECT n_second) <- S_roots.ALLOCATIONS
~((HOBJECT n_duplicate) <- S_roots.ALLOCATIONS)
$constant_callable_record_valid(S_roots, pconstantclosure_duplicate)
$user_constants_valid(S_roots, S_roots.USERCONSTANTS)
''')
CHECKS['global-constant-reentry']=premises(r'''
S_warning = $global_test_find(S_initial[.COMPLETION = NORMAL], $ptascii("REENTRANT_VALUE"), 6, 1400)
S_warning.CONSTANTCLOSURES = [pconstantclosure_outer]
n_outer = pconstantclosure_outer.OBJECT
$user_constant_at(S_warning.USERCONSTANTS, $ptascii("REENTRANT_VALUE")) = eps
$constant_context_valid(S_warning)
S_pending_roots = $prune_allocations(S_warning)
(HOBJECT n_outer) <- S_pending_roots.ALLOCATIONS
S_duplicate = $global_test_find(S_warning, $ptascii("REENTRANT_VALUE"), 2, 2600)
S_duplicate.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_duplicate*
perrorcall.RESUME = GLOBAL_CONSTANT_DUPLICATE porigin_outer (PARRAY n_candidate) pvalueclass_candidate n_constants z
porigin_outer = pconstantclosure_outer.DECL
$user_constant_at(S_duplicate.USERCONSTANTS, $ptascii("REENTRANT_VALUE")) = (puserconstant_inner)
puserconstant_inner.VALUE = PARRAY n_inner_array
S_duplicate.ARRAYS[n_inner_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_inner)), ENTRY (KINT 1) (DIRECT (PINT 2048))]
S_duplicate.ARRAYS[n_candidate].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_outer)), ENTRY (KINT 1) (DIRECT (PINT 2048))]
n_inner =/= n_outer /\ n_inner_array =/= n_candidate
puserconstant_inner.ORIGIN =/= porigin_outer
$global_test_output(S_duplicate.EVENTS) = $ptascii("8192:U:")
$global_constant_duplicate_valid(S_duplicate, porigin_outer, PARRAY n_candidate, pvalueclass_candidate, n_constants, z)
$error_call_valid(S_duplicate, perrorcall)
$task_nodes(perrorcall.RESUME) = [HARRAY n_candidate]
~$global_constant_duplicate_valid(S_duplicate, porigin_outer, PARRAY n_inner_array, pvalueclass_candidate, n_constants, z)
~$global_constant_duplicate_valid(S_duplicate, porigin_outer, PARRAY n_candidate, pvalueclass_candidate, 0, z)
~$error_call_valid(S_duplicate, perrorcall[.LINE = $(z + 1)])
S_held = $prune_allocations(S_duplicate)
(HARRAY n_candidate) <- S_held.ALLOCATIONS
(HOBJECT n_outer) <- S_held.ALLOCATIONS
(HARRAY n_inner_array) <- S_held.ALLOCATIONS
(HOBJECT n_inner) <- S_held.ALLOCATIONS
S_done = $global_test_finish(S_duplicate, 2800)
S_done.COMPLETION = NORMAL /\ S_done.TODO = eps
$global_test_output(S_done.EVENTS) = $ptascii("8192:U:2:1:2048")
$user_constant_at(S_done.USERCONSTANTS, $ptascii("REENTRANT_VALUE")) = (puserconstant_inner)
S_roots = $prune_allocations(S_done[.ENV = eps][.GLOBALTABLE = eps][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)])
~((HARRAY n_candidate) <- S_roots.ALLOCATIONS)
~((HOBJECT n_outer) <- S_roots.ALLOCATIONS)
(HARRAY n_inner_array) <- S_roots.ALLOCATIONS
(HOBJECT n_inner) <- S_roots.ALLOCATIONS
$constant_callable_record_valid(S_roots, pconstantclosure_outer)
$constant_callable_records_valid(S_roots, S_roots.CONSTANTCLOSURES)
$user_constants_valid(S_roots, S_roots.USERCONSTANTS)
''')
CHECKS['global-constant-throw-retry']=premises(r'''
S_warning = $global_test_find(S_initial[.COMPLETION = NORMAL], $ptascii("THROW_VALUE"), 6, 1400)
S_warning.CONSTANTCLOSURES = [pconstantclosure_failed]
n_failed = pconstantclosure_failed.OBJECT
$user_constant_at(S_warning.USERCONSTANTS, $ptascii("THROW_VALUE")) = eps
$constant_context_valid(S_warning)
S_caught = $global_test_find(S_warning, $ptascii("8192:F:"), 7, 2000)
$user_constant_at(S_caught.USERCONSTANTS, $ptascii("THROW_VALUE")) = eps
S_dead_failed = $prune_allocations(S_caught)
~((HOBJECT n_failed) <- S_dead_failed.ALLOCATIONS)
$constant_callable_record_valid(S_dead_failed, pconstantclosure_failed)
S_done = $global_test_finish(S_caught, 3600)
S_done.COMPLETION = NORMAL /\ S_done.TODO = eps
$global_test_output(S_done.EVENTS) = $ptascii("8192:F:U:8192:ok:2048")
$user_constant_at(S_done.USERCONSTANTS, $ptascii("THROW_VALUE")) = (puserconstant_success)
puserconstant_success.VALUE = PARRAY n_array
S_done.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_success)), ENTRY (KINT 1) (DIRECT (PINT 2048))]
n_success =/= n_failed
$lookup(S_done.ENV, $ptascii("clone")) = (n_cell_clone)
S_done.STORE[n_cell_clone] = DEFINED (POBJECT n_clone)
$constant_callable_record(S_done.CONSTANTCLOSURES, n_clone) = eps
$object_body(S_done.OBJECTS[n_clone]) = $object_body(S_done.OBJECTS[n_success])
S_roots = $prune_allocations(S_done[.ENV = eps][.GLOBALTABLE = eps][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)])
~((HOBJECT n_failed) <- S_roots.ALLOCATIONS)
~((HOBJECT n_clone) <- S_roots.ALLOCATIONS)
(HOBJECT n_success) <- S_roots.ALLOCATIONS
(HARRAY n_array) <- S_roots.ALLOCATIONS
$constant_callable_record_valid(S_roots, pconstantclosure_failed)
$user_constants_valid(S_roots, S_roots.USERCONSTANTS)
''')
CHECKS['global-constant-raw-trait-notice']=premises(r'''
S_warning = $global_test_find(S_initial[.COMPLETION = NORMAL], $ptascii("RAW_TRAIT_F"), 4, 1600)
S_warning.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warning*
perrorcall.RESUME = GLOBAL_CONSTANT_METHOD_RESUME porigin_site porigin_method porigin_called n_prefix
S_warning.CONSTANTCLOSURES = eps
$user_constant_at(S_warning.USERCONSTANTS, $ptascii("RAW_TRAIT_F")) = eps
S_warning.CONSTCONTEXT = (pconstantcontext)
$global_constant_method_resume_valid(S_warning, porigin_site, porigin_method, porigin_called, n_prefix)
$error_call_valid(S_warning, perrorcall)
$task_nodes(perrorcall.RESUME) = eps
$constant_context_valid(S_warning)
$class_method_origin(S_warning.CLASSES, porigin_method) = (pmethoddesc)
$global_constant_method_trait(S_warning, pmethoddesc)
porigin_site = PORIGIN n_unit pcpath_site
$global_test_entry_prefix(S_warning.DECLARATIONS, n_unit, 0) = (n_before_entry)
$constant_callable_published(S_warning.DECLARATIONS[0:n_before_entry], porigin_called)
~$declaration_entered(S_warning.DECLARATIONS[0:n_before_entry], n_unit)
~$global_constant_method_resume_valid(S_warning, porigin_site, porigin_method, porigin_called, n_before_entry)
~$global_constant_method_resume_valid(S_warning, porigin_site, porigin_method, porigin_called, $(n_prefix + 1))
~$global_constant_method_resume_valid(S_warning, pconstantcontext.ORIGIN, porigin_method, porigin_called, n_prefix)
~$global_constant_method_resume_valid(S_warning, porigin_site, pconstantcontext.ORIGIN, porigin_called, n_prefix)
~$global_constant_method_resume_valid(S_warning, porigin_site, porigin_method, pconstantcontext.ORIGIN, n_prefix)
~$global_constant_method_resume_valid(S_warning[.CONSTCONTEXT = eps], porigin_site, porigin_method, porigin_called, n_prefix)
~$error_call_valid(S_warning, perrorcall[.LEVEL = 2])
~$error_call_valid(S_warning, perrorcall[.LINE = $(perrorcall.LINE + 1)])
~$error_call_valid(S_warning, perrorcall[.SITE = pconstantcontext.ORIGIN])
~$error_call_valid(S_warning, perrorcall[.RESUME = GLOBAL_CONSTANT_METHOD_RESUME porigin_site porigin_method porigin_called n_before_entry])
S_caught = $global_test_find(S_warning, $ptascii("8192:F:"), 7, 2000)
$user_constant_at(S_caught.USERCONSTANTS, $ptascii("RAW_TRAIT_F")) = eps
S_caught.CONSTANTCLOSURES = eps
S_resume = $global_test_find(S_caught, $ptascii("RAW_TRAIT_F"), 5, 2600)
S_resume.TODO = (GLOBAL_CONSTANT_METHOD_RESUME porigin_site_retry porigin_method porigin_called n_prefix_retry) :: ptask_resume*
porigin_site_retry =/= porigin_site
S_resume.CONSTANTCLOSURES = eps
$global_constant_method_resume_valid(S_resume, porigin_site_retry, porigin_method, porigin_called, n_prefix_retry)
n_created = |S_resume.OBJECTS|
S_created = $global_test_next(S_resume)
S_created.RESULT = KNOWN (POBJECT n_created)
$constant_callable_record(S_created.CONSTANTCLOSURES, n_created) = (pconstantclosure_created)
pconstantclosure_created.SITE = porigin_site_retry
pconstantclosure_created.PREFIX = |S_created.DECLARATIONS|
$constant_callable_record_valid(S_created, pconstantclosure_created)
$object_body(S_created.OBJECTS[n_created]) = METHODCLOSURE porigin_method porigin_site_retry porigin_called eps
S_done = $global_test_finish(S_created, 2800)
S_done.COMPLETION = NORMAL /\ S_done.TODO = eps
$global_test_output(S_done.EVENTS) = $ptascii("8192:F:U:8192:trait")
$user_constant_at(S_done.USERCONSTANTS, $ptascii("RAW_TRAIT_F")) = (puserconstant)
puserconstant.VALUE = POBJECT n_created
$lookup(S_done.ENV, $ptascii("clone")) = (n_cell_clone)
S_done.STORE[n_cell_clone] = DEFINED (POBJECT n_clone)
$closure_scope_at(S_done.CLOSURESCOPES, n_clone) = (pclosurescope_clone)
$constant_callable_record(S_done.CONSTANTCLOSURES, n_clone) = eps
$global_constant_method_live(S_done, pmethoddesc, porigin_site_retry, porigin_called, pclosurescope_clone)
$closure_scope_row_valid(S_done, pclosurescope_clone)
S_roots = $prune_allocations(S_done[.ENV = eps][.GLOBALTABLE = eps][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)])
(HOBJECT n_created) <- S_roots.ALLOCATIONS
~((HOBJECT n_clone) <- S_roots.ALLOCATIONS)
$user_constants_valid(S_roots, S_roots.USERCONSTANTS)
$constant_callable_records_valid(S_roots, S_roots.CONSTANTCLOSURES)
''')
CHECKS['global-constant-duplicate-alias-shadow']=premises(r'''
ptbytes_dup = $user_constant_key($ptascii("GlobalAliasScope") ++ [92] ++ $ptascii("DUP"))
ptbytes_seed = $user_constant_key($ptascii("GlobalAliasScope") ++ [92] ++ $ptascii("SEED"))
S_warning = $global_test_find(S_initial[.COMPLETION = NORMAL], ptbytes_dup, 2, 2200)
S_warning.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warning*
perrorcall.RESUME = GLOBAL_CONSTANT_DUPLICATE porigin_decl (PARRAY n_candidate) pvalueclass_candidate n_constants z
$user_constant_at(S_warning.USERCONSTANTS, ptbytes_dup) = (puserconstant_original)
$user_constant_at(S_warning.USERCONSTANTS, ptbytes_seed) = eps
$global_constant_duplicate_valid(S_warning, porigin_decl, PARRAY n_candidate, pvalueclass_candidate, n_constants, z)
$error_call_valid(S_warning, perrorcall)
S_warning.ARRAYS[n_candidate].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_original)), ENTRY (KINT 1) (DIRECT (POBJECT n_discarded))]
puserconstant_original.VALUE = POBJECT n_original
$constant_callable_record(S_warning.CONSTANTCLOSURES, n_discarded) = (pconstantclosure_discarded)
pconstantclosure_discarded.DECL = porigin_decl
$task_nodes(perrorcall.RESUME) = [HARRAY n_candidate]
S_resumed = $global_test_find(S_warning, ptbytes_dup, 3, 2400)
S_resumed.TODO = (GLOBAL_CONSTANT_DUPLICATE porigin_decl (PARRAY n_candidate) pvalueclass_candidate n_constants z) :: ptask_resume*
$(n_constants < |S_resumed.USERCONSTANTS|)
$user_constant_at(S_resumed.USERCONSTANTS, ptbytes_seed) = (puserconstant_late)
puserconstant_late.VALUE = POBJECT n_late
n_late =/= n_original
$user_constant_at(S_resumed.USERCONSTANTS, ptbytes_dup) = (puserconstant_original)
$global_constant_transfer_valid(S_resumed, porigin_decl, pvalueclass_candidate, S_resumed.USERCONSTANTS[0:n_constants])
~$global_constant_transfer_valid(S_resumed, porigin_decl, pvalueclass_candidate, S_resumed.USERCONSTANTS)
$global_constant_duplicate_valid(S_resumed, porigin_decl, PARRAY n_candidate, pvalueclass_candidate, n_constants, z)
~$global_constant_duplicate_valid(S_resumed, porigin_decl, PARRAY n_candidate, pvalueclass_candidate, |S_resumed.USERCONSTANTS|, z)
~$global_constant_duplicate_valid(S_resumed, porigin_decl, PARRAY n_candidate, pvalueclass_candidate, 0, z)
~$global_constant_duplicate_valid(S_resumed, porigin_decl, PARRAY n_candidate, pvalueclass_candidate, $(|S_resumed.USERCONSTANTS| + 1), z)
S_held = $prune_allocations(S_resumed)
(HARRAY n_candidate) <- S_held.ALLOCATIONS
(HOBJECT n_discarded) <- S_held.ALLOCATIONS
(HOBJECT n_original) <- S_held.ALLOCATIONS
S_done = $global_test_finish(S_resumed, 5400)
S_done.COMPLETION = NORMAL /\ S_done.TODO = eps
$global_test_output(S_done.EVENTS) = $ptascii("2:global:late:1;2:F:global:late:1")
$user_constant_at(S_done.USERCONSTANTS, ptbytes_dup) = (puserconstant_original)
ptbytes_throw_dup = $user_constant_key($ptascii("GlobalAliasThrowScope") ++ [92] ++ $ptascii("DUP"))
$user_constant_at(S_done.USERCONSTANTS, ptbytes_throw_dup) = (puserconstant_throw)
puserconstant_throw.VALUE = POBJECT n_original
$user_constants_valid(S_done, S_done.USERCONSTANTS)
$constant_callable_records_valid(S_done, S_done.CONSTANTCLOSURES)
S_roots = $prune_allocations(S_done[.ENV = eps][.GLOBALTABLE = eps][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)])
~((HARRAY n_candidate) <- S_roots.ALLOCATIONS)
~((HOBJECT n_discarded) <- S_roots.ALLOCATIONS)
(HOBJECT n_original) <- S_roots.ALLOCATIONS
(HOBJECT n_late) <- S_roots.ALLOCATIONS
$constant_callable_record_valid(S_roots, pconstantclosure_discarded)
S_roots.USERCONSTANTS = S_done.USERCONSTANTS
$user_constants_valid(S_roots, S_roots.USERCONSTANTS)
''')

def seq(value):
    return '('+str(list(value))+')'

def service(child,child_fixture,evals):
    clauses=[]
    if child is not None:
        path=seq(bytes(child));data=seq(child.read_bytes())
        clauses.append('''def $global_test_service(S) = $file_open_resume(S, FILE_OPENED n_nonce pfilecontext.CALLER pfilecontext.REQUESTED CHILD_PATH CHILD_PATH CHILD_BYTES)
  -- if S.COMPLETION = SOURCE_PENDING
  -- if S.TODO = (FILE_RESOLVE_AWAIT n_nonce) :: ptask_tail*
  -- if S.FILECONTEXTS = pfilecontext :: pfilecontext_tail*
  -- if pfilecontext.NONCE = n_nonce
  -- if pfilecontext.REQUESTED = CHILD_PATH
def $global_test_service(S) = $file_parse_resume(S, SOURCE_ACCEPT n_unit CHILD_BYTES CHILD_PROGRAM)
  -- if S.COMPLETION = SOURCE_PENDING
  -- if S.TODO = (FILE_PARSE_AWAIT n_nonce) :: ptask_tail*
  -- if S.FILECONTEXTS = pfilecontext :: pfilecontext_tail*
  -- if pfilecontext.NONCE = n_nonce
  -- if pfilecontext.UNIT = (n_unit)
  -- if pfilecontext.BYTES = (CHILD_BYTES)
'''.replace('CHILD_PATH',path).replace('CHILD_BYTES',data).replace('CHILD_PROGRAM',child_fixture))
    for data,fixture in evals:
        clauses.append('''def $global_test_service(S) = $eval_resume(S, SOURCE_ACCEPT n_unit pevalcontext.BYTES EVAL_PROGRAM)
  -- if S.COMPLETION = SOURCE_PENDING
  -- if S.TODO = (EVAL_AWAIT n_unit) :: ptask_tail*
  -- if $eval_context_at(S.EVALCONTEXTS, n_unit) = (pevalcontext)
  -- if pevalcontext.BYTES = EVAL_BYTES
'''.replace('EVAL_PROGRAM',fixture).replace('EVAL_BYTES',seq(data)))
    clauses.append('def $global_test_service(S) = S'+(' -- otherwise' if clauses else '')+'\n')
    return ''.join(clauses)

def prepare(out):
    out=Path(out).resolve();out.mkdir(parents=True,exist_ok=False)
    types.ENV=ENV
    frontend=adapter=None
    records=[]
    def worker(command,name):
        result=Worker(command,out/name)
        (out/name/'launch.json').write_text(json.dumps({'supplied_argv':command,'supplied_cwd':os.getcwd(),'supplied_environment':ENV,'popen_args':result.p.args,'pid':result.p.pid},indent=2)+'\n')
        return result
    def checked(source,stem,mode='file'):
        data=source.encode()
        request={'op':'parse','source':base64.b64encode(data).decode()}
        if mode=='eval':
            request.update(op='parse-eval',id='1',mode='eval',profile='cli-raw-85')
        parsed=frontend.request(request);assert parsed['accepted'],parsed
        result=adapter.request({'op':'check','ast':parsed['ast'],'fixture':True});assert result['ok'],result
        (out/(stem+'.checked.json')).write_text(json.dumps(result,indent=2)+'\n')
        return result['fixture']
    try:
        frontend=worker([str(types.PHP),'-n',*types.FLAGS,'-d','extension='+str(ROOT/'.tools/php-file.so'),str(ROOT/'frontend/worker.php')],'frontend')
        adapter=worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)],'adapter')
        for name,source in SOURCES.items():
            path=out/(name+'.php');path.write_bytes(source.encode())
            main_fixture=checked(source,name)
            child=child_fixture=None
            companions=[]
            if name in FILES:
                filename,body=FILES[name]
                child=out/filename;child.write_bytes(body.encode())
                child_fixture=checked(body,child.stem)
                companions.append({'path':str(child),'sha256':base.sha(child)})
            evals=[(body.encode(),checked(body,name+'-eval-'+str(index),'eval')) for index,body in enumerate(EVALS.get(name,[]))]
            initial='$php_file_run('+main_fixture+', 0, '+seq(bytes(path))+', '+seq(bytes(ROOT))+')' if child else '$php_run('+main_fixture+', 0, '+json.dumps(base64.b64encode(bytes(path)).decode())+')'
            conditions=['S_initial = '+initial,*CHECKS[name]]
            fixture=out/(name+'.watsup')
            fixture.write_text(PREFIX+service(child,child_fixture,evals)+'\ndec $main() : bool\ndef $main() = true\n'+''.join('  -- if '+condition+'\n' for condition in conditions))
            records.append({'id':name,'source':str(path),'source_sha256':base.sha(path),'fixture':str(fixture),'fixture_sha256':base.sha(fixture),'main_predicates':len(conditions),'files':companions})
    finally:
        try:
            if frontend:frontend.close()
        finally:
            if adapter:adapter.close()
    (out/'prepared.json').write_text(json.dumps({'scope':'Checked original-source preparation only; global const numeric bodies unrun.','root':str(ROOT),'records':records},indent=2)+'\n')
    return records

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--prepare-only');parser.add_argument('--output')
    arguments=parser.parse_args()
    out=Path(arguments.prepare_only or arguments.output or str(Path(tempfile.mkdtemp(prefix='global-constant-callable-',dir=ROOT/'.tools'))/'prepared'))
    if arguments.prepare_only:
        prepare(out)
    else:
        protocol_before=base.sha(Path(__file__))
        original=base.prepare
        try:
            base.prepare=prepare;base.run(out)
        finally:
            base.prepare=original
        report=json.loads((out/'report.json').read_text())
        report.update(protocol=str(Path(__file__)),protocol_sha256=protocol_before,protocol_unchanged=protocol_before==base.sha(Path(__file__)))
        if not report['protocol_unchanged']:report['result']='failed'
        (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
        assert report['protocol_unchanged'],'protocol changed'
    print(out)

if __name__=='__main__':
    main()
