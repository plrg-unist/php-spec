#!/usr/bin/env python3
"""Check borrowed parameter identities, scope, read prefixes and array redirects."""
import argparse,json,tempfile
from pathlib import Path
import global_constant_callable_protocol as global_protocol

base=global_protocol.base
ROOT=base.ROOT
premises=global_protocol.premises

SOURCES={'parameter-borrowed-global': '<?php\n'
                              'const ParameterGlobalDonor = static function () { static $n = 0; return '
                              '++$n; };\n'
                              'function takeGlobalDonor($f = ParameterGlobalDonor) { return $f; }\n'
                              'function namedGlobalDonor($f = ParameterGlobalDonor, $tail = 7) {\n'
                              "    echo $f === ParameterGlobalDonor ? 'same:' : 'wrong:';\n"
                              '    echo $tail;\n'
                              '}\n'
                              'function skipMissingDonor($f = MissingParameterDonor) { return $f; }\n'
                              "function typedGlobalDonor(int $f = ParameterGlobalDonor) { echo 'body'; "
                              '}\n'
                              '$a = takeGlobalDonor();\n'
                              '$b = takeGlobalDonor();\n'
                              "echo $a === $b ? 'same:' : 'fresh:';\n"
                              "echo $a(), ':', $b(), '|';\n"
                              'namedGlobalDonor(tail: 9);\n'
                              "echo '|', skipMissingDonor(4), '|';\n"
                              "try { typedGlobalDonor(); } catch (TypeError $e) { echo 'type'; }\n",
 'parameter-borrowed-class-scope': '<?php\n'
                                   'class ParameterDonorBase {\n'
                                   "    private const TOKEN = 'base';\n"
                                   '    public const SEED = static function () { return [self::class, '
                                   'static::class, self::TOKEN]; };\n'
                                   '    public static function take($f = self::SEED) { return $f; }\n'
                                   '    public static function maker() { return static function ($f = '
                                   'self::SEED) { return $f; }; }\n'
                                   '}\n'
                                   'class ParameterDonorChild extends ParameterDonorBase {}\n'
                                   'class ParameterDonorOther {\n'
                                   "    private const TOKEN = 'other';\n"
                                   '    public const SEED = static function () { return [self::class, '
                                   'static::class, self::TOKEN]; };\n'
                                   '}\n'
                                   '$a = ParameterDonorChild::take();\n'
                                   '$b = ParameterDonorBase::take();\n'
                                   "echo $a === $b ? 'same:' : 'fresh:';\n"
                                   '$r = $a();\n'
                                   "echo $r[0], ':', $r[1], ':', $r[2], '|';\n"
                                   '$maker = ParameterDonorBase::maker();\n'
                                   '$rebound = Closure::bind($maker, null, '
                                   'ParameterDonorOther::class);\n'
                                   '$c = $rebound();\n'
                                   "echo $c === ParameterDonorOther::SEED ? 'same:' : 'wrong:';\n"
                                   '$clone = clone $c;\n'
                                   'unset($maker, $rebound, $c);\n'
                                   '$r = $clone();\n'
                                   "echo $r[0], ':', $r[1], ':', $r[2];\n",
 'parameter-mixed-array': '<?php\n'
                          "function parameterArrayNamed() { return 'named'; }\n"
                          'const ParameterArrayDonor = static function () { static $n = 0; return ++$n; '
                          '};\n'
                          'const ParameterArrayPayload = [ParameterArrayDonor, '
                          'parameterArrayNamed(...)];\n'
                          'function takeMixedArray($a = [\n'
                          "    'fresh' => static function () { static $n = 0; return ++$n; },\n"
                          "    'borrowed' => ParameterArrayDonor,\n"
                          "    'nested' => [ParameterArrayPayload],\n"
                          ']) { return $a; }\n'
                          '$x = takeMixedArray();\n'
                          '$y = takeMixedArray();\n'
                          "echo $x['fresh'] !== $y['fresh'] ? 'fresh:' : 'same:';\n"
                          "echo $x['borrowed'] === $y['borrowed'] ? 'same:' : 'wrong:';\n"
                          "echo $x['nested'][0][1] === ParameterArrayPayload[1] ? 'same:' : 'wrong:';\n"
                          "$x['nested'][0][0] = $x['fresh'];\n"
                          "echo $y['nested'][0][0] === ParameterArrayDonor ? 'cow:' : 'changed:';\n"
                          "$a = $x['fresh'];\n"
                          "$b = $y['fresh'];\n"
                          "$c = $x['borrowed'];\n"
                          "$d = $y['borrowed'];\n"
                          "$e = $y['nested'][0][1];\n"
                          "echo $a(), ':', $a(), ':', $b(), ':', $c(), ':', $d(), ':', $e();\n",
 'parameter-compiled-redirect': '<?php\n'
                                "function parameterRedirectNamed() { return 'donor'; }\n"
                                'const ParameterRedirectDonor = parameterRedirectNamed(...);\n'
                                'function takeTrueRedirect($f = true ? static function () { return '
                                "'fresh'; } : MissingRedirectDonor) { return $f; }\n"
                                'function takeFalseRedirect($f = false ? static function () { return '
                                "'unused'; } : ParameterRedirectDonor) { return $f; }\n"
                                '$a = takeTrueRedirect();\n'
                                '$b = takeTrueRedirect();\n'
                                '$c = takeFalseRedirect();\n'
                                '$d = takeFalseRedirect();\n'
                                "echo $a !== $b ? 'fresh:' : 'same:';\n"
                                "echo $c === $d ? 'same:' : 'fresh:';\n"
                                "echo $a(), ':', $c();\n",
 'parameter-namespace-between-receives': '<?php\n'
                                         'namespace {\n'
                                         '    const ParameterNamespaceSeed = static function () { '
                                         "return 'global'; };\n"
                                         '}\n'
                                         'namespace ParameterNamespace {\n'
                                         '    function take($f = ParameterNamespaceSeed) { return $f; '
                                         '}\n'
                                         '    $a = take();\n'
                                         '    const ParameterNamespaceSeed = static function () { '
                                         "return 'local'; };\n"
                                         '    $b = take();\n'
                                         "    echo $a === \\ParameterNamespaceSeed ? 'old:' : "
                                         "'wrong:';\n"
                                         "    echo $b === ParameterNamespaceSeed ? 'new:' : 'wrong:';\n"
                                         "    echo $a(), ':', $b();\n"
                                         '}\n',
 'parameter-namespace-warning-prefix': '<?php\n'
                                       'namespace {\n'
                                       '    const ParameterNoticeSeed = static function () { return '
                                       "'global'; };\n"
                                       '    trait ParameterNoticeTrait { public static function '
                                       "target() { return 'trait'; } }\n"
                                       '}\n'
                                       'namespace ParameterNotice {\n'
                                       '    function take($a = [ParameterNoticeSeed, '
                                       '\\ParameterNoticeTrait::target(...), ParameterNoticeSeed]) { '
                                       'return $a; }\n'
                                       '    $seen = 0;\n'
                                       '    set_error_handler(function ($n, $m) use (&$seen) {\n'
                                       '        ++$seen;\n'
                                       "        echo 'H|';\n"
                                       "        eval('namespace ParameterNotice; const "
                                       'ParameterNoticeSeed = static function () { return "local"; '
                                       "};');\n"
                                       '        return true;\n'
                                       '    });\n'
                                       '    $a = take();\n'
                                       '    $b = take();\n'
                                       "    echo $a[0] === \\ParameterNoticeSeed ? 'old:' : 'wrong:';\n"
                                       "    echo $a[2] === ParameterNoticeSeed ? 'new:' : 'wrong:';\n"
                                       "    echo $b[0] === ParameterNoticeSeed ? 'local:' : 'wrong:';\n"
                                       "    echo $a[1] !== $b[1] ? 'fresh:' : 'same:';\n"
                                       "    echo $seen, ':';\n"
                                       '    $old = $a[0];\n'
                                       '    $new = $a[2];\n'
                                       "    echo $old(), ':', $new();\n"
                                       '}\n',
 'parameter-namespace-warning-retry': '<?php\n'
                                      'namespace {\n'
                                      '    const ParameterRetrySeed = static function () { return '
                                      "'global'; };\n"
                                      '    trait ParameterRetryTrait { public static function target() '
                                      "{ return 'trait'; } }\n"
                                      '}\n'
                                      'namespace ParameterRetry {\n'
                                      '    function take($a = [ParameterRetrySeed, '
                                      '\\ParameterRetryTrait::target(...), ParameterRetrySeed]) { '
                                      'return $a; }\n'
                                      '    $seen = 0;\n'
                                      '    set_error_handler(function ($n, $m) use (&$seen) {\n'
                                      '        ++$seen;\n'
                                      "        echo 'H', $seen, '|';\n"
                                      '        if ($seen === 1) {\n'
                                      "            eval('namespace ParameterRetry; const "
                                      'ParameterRetrySeed = static function () { return "local"; '
                                      "};');\n"
                                      "            throw new \\Exception('stop');\n"
                                      '        }\n'
                                      '        return true;\n'
                                      '    });\n'
                                      '    try { take(); } catch (\\Exception $e) { echo '
                                      "$e->getMessage(), '|'; }\n"
                                      '    $a = take();\n'
                                      '    $first = $a[0];\n'
                                      '    $last = $a[2];\n'
                                      "    echo $first(), ':', $last(), ':', $seen;\n"
                                      '}\n',
 'parameter-borrowed-emitter-scope': '<?php\n'
                                     'class ParameterDonorEmitter {\n'
                                     "    private const TOKEN = 'emitter';\n"
                                     '    public static function create() {\n'
                                     "        eval('const ParameterEmittedDonor = static function () { "
                                     "return self::TOKEN; };');\n"
                                     '    }\n'
                                     '}\n'
                                     'ParameterDonorEmitter::create();\n'
                                     'function takeEmittedDonor($f = ParameterEmittedDonor) { return '
                                     '$f; }\n'
                                     '$a = takeEmittedDonor();\n'
                                     '$b = takeEmittedDonor();\n'
                                     "echo $a === $b ? 'same:' : 'fresh:';\n"
                                     '$clone = clone $a;\n'
                                     'unset($a, $b);\n'
                                     'echo $clone();\n',
 'parameter-borrowed-private-method': '<?php\n'
                                      'class ParameterPrivateMethodDonor {\n'
                                      '    private static function target() { return [self::class, '
                                      'static::class]; }\n'
                                      '    public const PUBLIC_SEED = self::target(...);\n'
                                      '    private const PRIVATE_SEED = self::target(...);\n'
                                      '    public static function take($f = self::PRIVATE_SEED) { '
                                      'return $f; }\n'
                                      '}\n'
                                      'class ParameterPrivateMethodChild extends '
                                      'ParameterPrivateMethodDonor {}\n'
                                      'function takePublicMethod($f = '
                                      'ParameterPrivateMethodDonor::PUBLIC_SEED) { return $f; }\n'
                                      'function takeDeniedMethod($f = '
                                      'ParameterPrivateMethodDonor::PRIVATE_SEED) { return $f; }\n'
                                      '$a = takePublicMethod();\n'
                                      '$b = takePublicMethod();\n'
                                      "echo $a === $b ? 'same:' : 'fresh:';\n"
                                      '$copy = clone $a;\n'
                                      'unset($a, $b);\n'
                                      '$r = $copy();\n'
                                      "echo $r[0], ':', $r[1], '|';\n"
                                      '$c = ParameterPrivateMethodChild::take();\n'
                                      '$d = ParameterPrivateMethodDonor::take();\n'
                                      "echo $c === $d ? 'same:' : 'fresh:';\n"
                                      '$r = $c();\n'
                                      "echo $r[0], ':', $r[1], '|';\n"
                                      "echo takeDeniedMethod($copy) === $copy ? 'supplied|' : "
                                      "'wrong|';\n"
                                      'try { takeDeniedMethod(); } catch (Error $e) { echo '
                                      '$e->getMessage(); }\n'}
SOURCES['parameter-object-context-warning']=r'''<?php
namespace {
    const ParameterNoticeSeed = static function () { return 'global'; };
    class ParameterNoticeObject {}
    const ParameterNoticeObjectSeed = new ParameterNoticeObject;
    trait ParameterNoticeTrait { public static function target() { return 'trait'; } }
}
namespace ParameterNotice {
    function take($a = [\ParameterNoticeObjectSeed, ParameterNoticeSeed, \ParameterNoticeTrait::target(...), ParameterNoticeSeed]) { return $a; }
    $seen = 0;
    set_error_handler(function ($n, $m) use (&$seen) {
        ++$seen;
        echo 'H|';
        eval('namespace ParameterNotice; const ParameterNoticeSeed = static function () { return "local"; };');
        return true;
    });
    $a = take();
    $b = take();
    echo $a[0] === \ParameterNoticeObjectSeed ? 'object:' : 'wrong:';
    echo $a[1] === \ParameterNoticeSeed ? 'old:' : 'wrong:';
    echo $a[3] === ParameterNoticeSeed ? 'new:' : 'wrong:';
    echo $b[1] === ParameterNoticeSeed ? 'local:' : 'wrong:';
    echo $a[2] !== $b[2] ? 'fresh:' : 'same:';
    echo $seen, ':';
    $old = $a[1];
    $new = $a[3];
    echo $old(), ':', $new();
}
'''
SOURCES['parameter-quiet-object-context']=r'''<?php
class ParameterQuietObject {}
const ParameterQuietObjectSeed = new ParameterQuietObject;
const ParameterQuietClosureSeed = static function () { return 'global'; };
function takeQuietObjectContext($a = [ParameterQuietObjectSeed, ParameterQuietClosureSeed]) { return $a; }
$a = takeQuietObjectContext();
echo $a[0] === ParameterQuietObjectSeed ? 'object:' : 'wrong:';
echo $a[1] === ParameterQuietClosureSeed ? 'same:' : 'wrong:';
$f = $a[1];
echo $f();
'''
SOURCES['parameter-trailing-real-warning']=r'''<?php
namespace {
    const ParameterNoticeSeed = static function () { return 'global'; };
    trait ParameterNoticeTrait { public static function target() { return 'trait'; } }
}
namespace ParameterNotice {
    function take($a = [ParameterNoticeSeed, \ParameterNoticeTrait::target(...), ParameterNoticeSeed, static function () { return 'after'; }]) { return $a; }
    $seen = 0;
    set_error_handler(function ($n, $m) use (&$seen) {
        ++$seen;
        echo 'H|';
        eval('namespace ParameterNotice; const ParameterNoticeSeed = static function () { return "local"; };');
        return true;
    });
    $a = take();
    $b = take();
    echo $a[0] === \ParameterNoticeSeed ? 'old:' : 'wrong:';
    echo $a[2] === ParameterNoticeSeed ? 'new:' : 'wrong:';
    echo $b[0] === ParameterNoticeSeed ? 'local:' : 'wrong:';
    echo $a[1] !== $b[1] ? 'fresh:' : 'same:';
    echo $seen, ':';
    $old = $a[0];
    $new = $a[2];
    echo $old(), ':', $new();
}
'''
SOURCES['parameter-deprecated-shadow']=r'''<?php
namespace {
    const ParameterDeprecatedSeed = static function () { return 'global'; };
}
namespace ParameterDeprecated {
    function take($a = [ParameterDeprecatedSeed, E_STRICT, ParameterDeprecatedSeed]) { return $a; }
    set_error_handler(function ($n, $m) {
        echo 'H|';
        eval('namespace ParameterDeprecated; const ParameterDeprecatedSeed = static function () { return "local"; }; const E_STRICT = 2048;');
        return true;
    });
    $a = take();
    echo $a[0] === \ParameterDeprecatedSeed ? 'old:' : 'wrong:';
    echo $a[2] === ParameterDeprecatedSeed ? 'new:' : 'wrong:';
    echo $a[1], ':';
    $old = $a[0];
    $new = $a[2];
    echo $old(), ':', $new();
}
'''
SOURCES['parameter-bool-null-values']=r'''<?php
const ParameterBooleanNullSeed = static function () { return 'donor'; };
function takeBooleanNullKeys($a = [false => ParameterBooleanNullSeed, '' => [true, false, null], true => static function () { return 'fresh'; }]) { return $a; }
$a = takeBooleanNullKeys();
$b = takeBooleanNullKeys();
echo $a[0] === ParameterBooleanNullSeed ? 'same:' : 'wrong:';
echo $a[''] === [true, false, null] ? 'values:' : 'wrong:';
echo $a[1] !== $b[1] ? 'fresh:' : 'same:';
$f = $a[0];
$g = $a[1];
echo $f(), ':', $g();
'''
OUTPUTS={'parameter-borrowed-global': 'same:1:2|same:9|4|type',
 'parameter-borrowed-class-scope': 'same:ParameterDonorBase:ParameterDonorBase:base|same:ParameterDonorOther:ParameterDonorOther:other',
 'parameter-mixed-array': 'fresh:same:same:cow:1:2:1:1:2:named',
 'parameter-compiled-redirect': 'fresh:same:fresh:donor',
 'parameter-namespace-between-receives': 'old:new:global:local',
 'parameter-namespace-warning-prefix': 'H|old:new:local:fresh:1:global:local',
 'parameter-namespace-warning-retry': 'H1|stop|H2|local:local:2',
 'parameter-borrowed-emitter-scope': 'same:emitter',
 'parameter-borrowed-private-method': 'same:ParameterPrivateMethodDonor:ParameterPrivateMethodDonor|same:ParameterPrivateMethodDonor:ParameterPrivateMethodDonor|supplied|Cannot '
                                      'access private constant '
                                      'ParameterPrivateMethodDonor::PRIVATE_SEED'}
OUTPUTS['parameter-object-context-warning']='H|object:old:new:local:fresh:1:global:local'
OUTPUTS['parameter-quiet-object-context']='object:same:global'
OUTPUTS['parameter-trailing-real-warning']='H|old:new:local:fresh:1:global:local'
OUTPUTS['parameter-deprecated-shadow']='H|old:new:2048:global:local'
OUTPUTS['parameter-bool-null-values']='same:values:fresh:donor:fresh'
FILES={}
EVALS={
    'parameter-namespace-warning-prefix': ['namespace ParameterNotice; const ParameterNoticeSeed = static function () { return "local"; };'],
    'parameter-namespace-warning-retry': ['namespace ParameterRetry; const ParameterRetrySeed = static function () { return "local"; };'],
    'parameter-borrowed-emitter-scope': ['const ParameterEmittedDonor = static function () { return self::TOKEN; };'],
}

EVALS['parameter-object-context-warning']=EVALS['parameter-namespace-warning-prefix']

EVALS['parameter-trailing-real-warning']=EVALS['parameter-namespace-warning-prefix']
EVALS['parameter-deprecated-shadow']=['namespace ParameterDeprecated; const ParameterDeprecatedSeed = static function () { return "local"; }; const E_STRICT = 2048;']

PREFIX=global_protocol.PREFIX+r'''
dec $donor_test_parameter_frame(pstate, pframe) : bool
dec $donor_test_saved_parameter(pstate, pframe*) : (pframe, pframe*)?
dec $donor_test_function(pstate, ptbytes) : bool
def $donor_test_function(S, ptbytes_name) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $function_at($all_functions(S), pcallcontext.FUNCTION) = (pfunction)
  -- if pfunction.NAME = ptbytes_name
def $donor_test_function(S, ptbytes_name) = false -- otherwise
dec $donor_test_stage(pstate, ptbytes, nat) : bool
def $donor_test_stage(S, ptbytes_name, 0) = true
  -- if $donor_test_function(S, ptbytes_name)
  -- if S.TODO = (DEFAULT_BIND porigin_function n_index) :: ptask_tail*
def $donor_test_stage(S, ptbytes_name, 1) = true
  -- if $donor_test_function(S, ptbytes_name)
  -- if S.TODO = (NAMED_DEFAULT_BIND porigin_function n_index) :: ptask_tail*
def $donor_test_stage(S, ptbytes_name, 2) = true
  -- if $donor_test_function(S, ptbytes_name)
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = PARAMETER_CONSTANT_METHOD_RESUME porigin_site porigin_function porigin_called n_prefix
def $donor_test_stage(S, ptbytes_name, 3) = true
  -- if $donor_test_function(S, ptbytes_name)
  -- if S.TODO = (PARAMETER_CONSTANT_METHOD_RESUME porigin_site porigin_function porigin_called n_prefix) :: ptask_tail*
def $donor_test_stage(S, ptbytes_name, 4) = true
  -- if |S.USERCONSTANTS| = 2
  -- if $donor_test_saved_parameter(S, S.FRAMES) = ((pframe, pframe_tail*))
def $donor_test_stage(S, ptbytes_name, n_stage) = false -- otherwise
dec $donor_test_seek(pstate, ptbytes, nat, nat) : pstate
def $donor_test_seek(S, ptbytes_name, n_stage, n_limit) = S
  -- if $donor_test_stage(S, ptbytes_name, n_stage)
def $donor_test_seek(S, ptbytes_name, n_stage, n_limit) = $donor_test_seek($global_test_next(S), ptbytes_name, n_stage, n_rest)
  -- if ~$donor_test_stage(S, ptbytes_name, n_stage)
  -- if $(n_limit > 0)
  -- if (S.COMPLETION = NORMAL \/ S.COMPLETION = SOURCE_PENDING) /\ ~S.COMPILESTOP
  -- if n_rest = $(n_limit - 1)
def $donor_test_parameter_frame(S, pframe) = true
  -- if pframe.CONSTCONTEXT = (pconstantcontext)
  -- if $origin_node(S.SOURCES, pconstantcontext.ORIGIN) = (NParam phpType14 phpType24 phpType18 phpType4_ref phpType4_var phpType10 expression phpType37 metadata)
def $donor_test_parameter_frame(S, pframe) = false -- otherwise
def $donor_test_saved_parameter(S, pframe :: pframe_tail*) = ((pframe, pframe_tail*))
  -- if $donor_test_parameter_frame(S, pframe)
def $donor_test_saved_parameter(S, pframe :: pframe_tail*) = $donor_test_saved_parameter(S, pframe_tail*)
  -- if ~$donor_test_parameter_frame(S, pframe)
def $donor_test_saved_parameter(S, eps) = eps
dec $donor_test_step(pstate) : pstate
def $donor_test_step(S) = S_next
  -- if S.COMPLETION = NORMAL
  -- PhpStep: S ~> S_next
'''

CHECKS={}
CHECKS['parameter-borrowed-global']=premises(r'''
S = $donor_test_seek(S_initial[.COMPLETION = NORMAL], $ptascii("takeGlobalDonor"), 0, 1800)
S.TODO = (DEFAULT_BIND porigin_function 0) :: ptask_tail*
$function_at($all_functions(S), porigin_function) = (pfunction)
$default_at(pfunction.DEFAULTS, 0) = (pdefault)
S.RESULT = KNOWN (POBJECT n_donor)
$user_constant_at(S.USERCONSTANTS, $ptascii("ParameterGlobalDonor")) = (puserconstant)
puserconstant.VALUE = POBJECT n_donor
S.CONSTCONTEXT = (pconstantcontext)
$constant_fact_at(pconstantcontext.FACTS, pdefault.ORIGIN) = (pconstantfact)
pconstantfact.CLASS = puserconstant.CLASS /\ pconstantfact.VALUE = eps
pconstantfact.LOOKUP = (pconstantlookup)
pconstantlookup.ORIGIN = pconstantcontext.ORIGIN /\ pconstantlookup.SITE = pdefault.ORIGIN
pconstantlookup.DECL = puserconstant.ORIGIN /\ pconstantlookup.PREFIX = |S.USERCONSTANTS|
S.PARAMETERCLOSURES = eps /\ S.DEFAULTCACHE = eps
$global_constant_lookup_valid(S, pconstantcontext.ORIGIN, pconstantfact, S.USERCONSTANTS)
$parameter_default_transfer_valid(S, pfunction, 0, POBJECT n_donor, pconstantfact.CLASS)
$default_context_valid(S, pconstantcontext) /\ $call_descriptors_valid(S)
~$global_constant_fact_lookup_valid(S, pconstantcontext.ORIGIN, pconstantfact[.LOOKUP = eps])
~$global_constant_lookup_valid(S, pconstantcontext.ORIGIN, pconstantfact[.LOOKUP = (pconstantlookup[.PREFIX = 0])], S.USERCONSTANTS)
~$global_constant_lookup_valid(S, pconstantcontext.ORIGIN, pconstantfact[.LOOKUP = (pconstantlookup[.DECL = pdefault.ORIGIN])], S.USERCONSTANTS)
~$global_constant_lookup_valid(S, pconstantcontext.ORIGIN, pconstantfact[.LOOKUP = (pconstantlookup[.SITE = pconstantcontext.ORIGIN])], S.USERCONSTANTS)
S_erased = S[.CONSTCONTEXT = (pconstantcontext[.FACTS = [pconstantfact[.LOOKUP = eps]]])]
~$default_context_valid(S_erased, pconstantcontext[.FACTS = [pconstantfact[.LOOKUP = eps]]])
~$parameter_default_transfer_valid(S_erased, pfunction, 0, POBJECT n_donor, pconstantfact.CLASS)
S_again = $donor_test_seek($global_test_next(S), $ptascii("takeGlobalDonor"), 0, 1800)
S_again.RESULT = KNOWN (POBJECT n_donor)
S_again.PARAMETERCLOSURES = eps /\ S_again.DEFAULTCACHE = eps
S_named = $donor_test_seek(S_again, $ptascii("namedGlobalDonor"), 1, 2400)
S_named.RESULT = KNOWN (POBJECT n_donor)
S_named.TODO = (NAMED_DEFAULT_BIND porigin_named 0) :: ptask_named*
$call_descriptors_valid(S_named)
S_bad = $donor_test_seek(S_named, $ptascii("typedGlobalDonor"), 0, 2400)
S_bad.RESULT = KNOWN (POBJECT n_donor)
$call_descriptors_valid(S_bad)
S_done = $global_test_finish(S_bad, 3600)
S_done.COMPLETION = NORMAL /\ S_done.TODO = eps
$global_test_output(S_done.EVENTS) = $ptascii("same:1:2|same:9|4|type")
S_done.PARAMETERCLOSURES = eps /\ S_done.DEFAULTCACHE = eps
$($heap_owners($heap_graph(S_done), HOBJECT n_donor) > 0)
S_roots = $prune_allocations(S_done[.ENV = eps][.GLOBALTABLE = eps][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)])
(HOBJECT n_donor) <- S_roots.ALLOCATIONS
$heap_owners($heap_graph(S_roots), HOBJECT n_donor) = 1
$user_constants_valid(S_roots, S_roots.USERCONSTANTS)
''')
CHECKS['parameter-borrowed-class-scope']=premises(r'''
S = $donor_test_seek(S_initial[.COMPLETION = NORMAL], $ptascii("ParameterDonorBase::take"), 0, 1800)
S.TODO = (DEFAULT_BIND porigin_function 0) :: ptask_tail*
$function_at($all_functions(S), porigin_function) = (pfunction)
$default_at(pfunction.DEFAULTS, 0) = (pdefault)
S.CURRENT = (pcallcontext)
S.RESULT = KNOWN (POBJECT n_donor)
$global_constant_class_alias(S, pdefault.ORIGIN, pcallcontext.LEXICAL_CLASS) = (pclassconstantdesc)
$constant_callable_alias_class(S, pclassconstantdesc) = (pvalueclass)
$constant_callable_alias_flow(S, pclassconstantdesc, pvalueclass, |S.DECLARATIONS|, eps)
$default_cache_at(S.CLASSCONSTANTCACHE, pclassconstantdesc.ORIGIN) = (pdefaultcache)
pdefaultcache.VALUE = POBJECT n_donor /\ pdefaultcache.CLASS = pvalueclass
$closure_scope_at(S.CLOSURESCOPES, n_donor) = (pclosurescope)
pclosurescope.LEXICAL = pclassconstantdesc.OWNER /\ pclosurescope.CALLED = pclassconstantdesc.OWNER
pclosurescope.RECEIVER = eps
$parameter_default_transfer_valid(S, pfunction, 0, POBJECT n_donor, pvalueclass)
$call_descriptors_valid(S)
~$constant_callable_alias_flow(S[.CLASSCONSTANTCACHE = eps], pclassconstantdesc, pvalueclass, |S.DECLARATIONS|, eps)
S.PARAMETERCLOSURES = eps /\ S.DEFAULTCACHE = eps
S_again = $donor_test_seek($global_test_next(S), $ptascii("ParameterDonorBase::take"), 0, 1600)
S_again.RESULT = KNOWN (POBJECT n_donor)
S_done = $global_test_finish(S_again, 5000)
S_done.COMPLETION = NORMAL /\ S_done.TODO = eps
$global_test_output(S_done.EVENTS) = $ptascii("same:ParameterDonorBase:ParameterDonorBase:base|same:ParameterDonorOther:ParameterDonorOther:other")
S_done.PARAMETERCLOSURES = eps /\ S_done.DEFAULTCACHE = eps
$lookup(S_done.ENV, $ptascii("clone")) = (n_cell_clone)
S_done.STORE[n_cell_clone] = DEFINED (POBJECT n_clone)
$constant_callable_record(S_done.CONSTANTCLOSURES, n_clone) = eps
$closure_scope_at(S_done.CLOSURESCOPES, n_clone) = (pclosurescope_clone)
$class_at(S_done.CLASSES, pclosurescope_clone.LEXICAL) = (pclassdesc_other)
pclassdesc_other.NAME = $ptascii("ParameterDonorOther")
pclosurescope_clone.CALLED = pclosurescope_clone.LEXICAL /\ pclosurescope_clone.RECEIVER = eps
$closure_scope_row_valid(S_done, pclosurescope_clone)
~$closure_scope_row_valid(S_done, pclosurescope_clone[.LEXICAL = pclassconstantdesc.OWNER])
$heap_owners($heap_graph(S_done), HOBJECT n_clone) = 1
''')
CHECKS['parameter-mixed-array']=premises(r'''
S = $donor_test_seek(S_initial[.COMPLETION = NORMAL], $ptascii("takeMixedArray"), 0, 2000)
S.TODO = (DEFAULT_BIND porigin_function 0) :: ptask_tail*
$function_at($all_functions(S), porigin_function) = (pfunction)
$default_at(pfunction.DEFAULTS, 0) = (pdefault)
S.RESULT = KNOWN (PARRAY n_first)
S.CONSTCONTEXT = (pconstantcontext)
$constant_fact_at(pconstantcontext.FACTS, pdefault.ORIGIN) = (pconstantfact)
$constant_value_class_valid(S, PARRAY n_first, pconstantfact.CLASS)
S.ARRAYS[n_first].ITEMS = [ENTRY (KSTRING ptbytes_fresh) (DIRECT (POBJECT n_fresh)), ENTRY (KSTRING ptbytes_borrowed) (DIRECT (POBJECT n_donor)), ENTRY (KSTRING ptbytes_nested) (DIRECT (PARRAY n_nested))]
ptbytes_fresh = $ptascii("fresh") /\ ptbytes_borrowed = $ptascii("borrowed") /\ ptbytes_nested = $ptascii("nested")
S.ARRAYS[n_nested].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_payload))]
$user_constant_at(S.USERCONSTANTS, $ptascii("ParameterArrayDonor")) = (puserconstant)
puserconstant.VALUE = POBJECT n_donor
$user_constant_at(S.USERCONSTANTS, $ptascii("ParameterArrayPayload")) = (puserconstant_payload)
puserconstant_payload.VALUE = PARRAY n_payload
$parameter_callable_record(S.PARAMETERCLOSURES, n_fresh) = (pparameterclosure)
$parameter_callable_record(S.PARAMETERCLOSURES, n_donor) = eps
$parameter_default_transfer_valid(S, pfunction, 0, PARRAY n_first, pconstantfact.CLASS)
$call_descriptors_valid(S)
S_wrong = S[.ARRAYS[n_first].ITEMS = [ENTRY (KSTRING ptbytes_fresh) (DIRECT (POBJECT n_donor)), ENTRY (KSTRING ptbytes_borrowed) (DIRECT (POBJECT n_donor)), ENTRY (KSTRING ptbytes_nested) (DIRECT (PARRAY n_nested))]]
~$parameter_default_transfer_valid(S_wrong, pfunction, 0, PARRAY n_first, pconstantfact.CLASS)
S_again = $donor_test_seek($global_test_next(S), $ptascii("takeMixedArray"), 0, 2200)
S_again.RESULT = KNOWN (PARRAY n_second)
n_first =/= n_second
S_again.ARRAYS[n_second].ITEMS = [ENTRY (KSTRING ptbytes_fresh) (DIRECT (POBJECT n_fresh_second)), ENTRY (KSTRING ptbytes_borrowed) (DIRECT (POBJECT n_donor)), ENTRY (KSTRING ptbytes_nested) (DIRECT (PARRAY n_nested_second))]
n_fresh =/= n_fresh_second /\ n_nested =/= n_nested_second
S_again.ARRAYS[n_nested_second].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_payload))]
S_again.DEFAULTCACHE = eps
S_done = $global_test_finish(S_again, 5000)
S_done.COMPLETION = NORMAL /\ S_done.TODO = eps
$global_test_output(S_done.EVENTS) = $ptascii("fresh:same:same:cow:1:2:1:1:2:named")
$user_constant_at(S_done.USERCONSTANTS, $ptascii("ParameterArrayPayload")) = (puserconstant_payload)
$lookup(S_done.ENV, $ptascii("x")) = (n_cell_x)
S_done.STORE[n_cell_x] = DEFINED (PARRAY n_changed)
S_done.ARRAYS[n_changed].ITEMS = [ENTRY (KSTRING ptbytes_fresh) (DIRECT (POBJECT n_fresh)), ENTRY (KSTRING ptbytes_borrowed) (DIRECT (POBJECT n_donor)), ENTRY (KSTRING ptbytes_nested) (DIRECT (PARRAY n_changed_nested))]
S_done.ARRAYS[n_changed_nested].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_changed_payload))]
n_changed_payload =/= n_payload
S_done.ARRAYS[n_changed_payload].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_fresh)), ENTRY (KINT 1) (DIRECT (POBJECT n_named))]
S_done.ARRAYS[n_payload].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_donor)), ENTRY (KINT 1) (DIRECT (POBJECT n_named))]
$lookup(S_done.ENV, $ptascii("y")) = (n_cell_y)
S_done.STORE[n_cell_y] = DEFINED (PARRAY n_final_y)
S_done.ARRAYS[n_final_y].ITEMS = [ENTRY (KSTRING ptbytes_fresh) (DIRECT (POBJECT n_fresh_second)), ENTRY (KSTRING ptbytes_borrowed) (DIRECT (POBJECT n_donor)), ENTRY (KSTRING ptbytes_nested) (DIRECT (PARRAY n_final_y_nested))]
S_done.ARRAYS[n_final_y_nested].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_payload))]
S_done.DEFAULTCACHE = eps
$user_constants_valid(S_done, S_done.USERCONSTANTS)
''')
CHECKS['parameter-compiled-redirect']=premises(r'''
S = $donor_test_seek(S_initial[.COMPLETION = NORMAL], $ptascii("takeTrueRedirect"), 0, 1800)
S.TODO = (DEFAULT_BIND porigin_function 0) :: ptask_tail*
$function_at($all_functions(S), porigin_function) = (pfunction)
$default_at(pfunction.DEFAULTS, 0) = (pdefault)
$compiled_redirect(S, pdefault.ORIGIN) = ((porigin_selected, expression_selected, false, z))
S.RESULT = KNOWN (POBJECT n_fresh)
$parameter_callable_record(S.PARAMETERCLOSURES, n_fresh) = (pparameterclosure)
$constant_callable_record(S.CONSTANTCLOSURES, n_fresh) = (pconstantclosure)
pconstantclosure.SITE = porigin_selected
$parameter_default_transfer_valid(S, pfunction, 0, POBJECT n_fresh, PVCLOSURE n_fresh porigin_selected)
$call_descriptors_valid(S)
S.CONSTCONTEXT = (pconstantcontext_true)
$origin_node(S.SOURCES, pdefault.ORIGIN) = (NExprTernary expression_condition phpType5 expression_false metadata_ternary)
$constant_ternary_branches_valid(S, pdefault.ORIGIN, phpType5)
$constant_fact_at(pconstantcontext_true.FACTS, porigin_selected) = (pconstantfact_selected)
porigin_pruned = $constant_child(pdefault.ORIGIN, [PCFIELD 2])
pconstantfact_pruned = pconstantfact_selected[.ORIGIN = porigin_pruned][.VALUE = (PINT 0)][.CLASS = PVSCALAR][.LOOKUP = eps]
S_pruned = S[.CONSTCONTEXT = (pconstantcontext_true[.FACTS = pconstantcontext_true.FACTS ++ [pconstantfact_pruned]])]
~$constant_ternary_branches_valid(S_pruned, pdefault.ORIGIN, phpType5)
~$default_context_valid(S_pruned, pconstantcontext_true[.FACTS = pconstantcontext_true.FACTS ++ [pconstantfact_pruned]])
~$parameter_default_transfer_valid(S_pruned, pfunction, 0, POBJECT n_fresh, PVCLOSURE n_fresh porigin_selected)
S.CODE = [pcode]
pdefault.ORIGIN = PORIGIN n_unit pcpath_default
S_wrong = S[.CODE = [pcode[.REDIRECTS = (CODEREDIRECT pcpath_default (pcpath_default ++ [PCFIELD 2]) false) :: pcode.REDIRECTS]]]
~$constant_ternary_branches_valid(S_wrong, pdefault.ORIGIN, phpType5)
~$parameter_default_transfer_valid(S_wrong, pfunction, 0, POBJECT n_fresh, PVCLOSURE n_fresh porigin_selected)
S_no_redirect = S[.CODE = [pcode[.REDIRECTS = eps]]]
~$constant_ternary_branches_valid(S_no_redirect, pdefault.ORIGIN, phpType5)
~$parameter_default_transfer_valid(S_no_redirect, pfunction, 0, POBJECT n_fresh, PVCLOSURE n_fresh porigin_selected)
S_again = $donor_test_seek($global_test_next(S), $ptascii("takeTrueRedirect"), 0, 1800)
S_again.RESULT = KNOWN (POBJECT n_fresh_again)
n_fresh =/= n_fresh_again
S_borrowed = $donor_test_seek(S_again, $ptascii("takeFalseRedirect"), 0, 2200)
S_borrowed.TODO = (DEFAULT_BIND porigin_borrowed 0) :: ptask_borrowed*
$function_at($all_functions(S_borrowed), porigin_borrowed) = (pfunction_borrowed)
$default_at(pfunction_borrowed.DEFAULTS, 0) = (pdefault_borrowed)
$compiled_redirect(S_borrowed, pdefault_borrowed.ORIGIN) = ((porigin_alias, expression_alias, false, z_alias))
$user_constant_at(S_borrowed.USERCONSTANTS, $ptascii("ParameterRedirectDonor")) = (puserconstant)
S_borrowed.RESULT = KNOWN puserconstant.VALUE
S_borrowed.CONSTCONTEXT = (pconstantcontext)
$constant_fact_at(pconstantcontext.FACTS, porigin_alias) = (pconstantfact)
pconstantfact.LOOKUP = (pconstantlookup)
pconstantfact.CLASS = puserconstant.CLASS
$global_constant_lookup_valid(S_borrowed, pconstantcontext.ORIGIN, pconstantfact, S_borrowed.USERCONSTANTS)
$call_descriptors_valid(S_borrowed)
porigin_alias = PORIGIN n_unit pcpath_alias
S_transplanted = S[.CODE = [pcode[.REDIRECTS = (CODEREDIRECT pcpath_default pcpath_alias false) :: pcode.REDIRECTS]]]
~$constant_ternary_branches_valid(S_transplanted, pdefault.ORIGIN, phpType5)
~$parameter_default_transfer_valid(S_transplanted, pfunction, 0, POBJECT n_fresh, PVCLOSURE n_fresh porigin_selected)
S_done = $global_test_finish(S_borrowed, 4200)
S_done.COMPLETION = NORMAL /\ S_done.TODO = eps
$global_test_output(S_done.EVENTS) = $ptascii("fresh:same:fresh:donor")
|S_done.PARAMETERCLOSURES| = 2
S_done.DEFAULTCACHE = eps
''')
CHECKS['parameter-namespace-between-receives']=premises(r'''
ptbytes_function = $ptascii("ParameterNamespace") ++ [92] ++ $ptascii("take")
ptbytes_local = $ptascii("ParameterNamespace") ++ [92] ++ $ptascii("ParameterNamespaceSeed")
S = $donor_test_seek(S_initial[.COMPLETION = NORMAL], ptbytes_function, 0, 1600)
S.RESULT = KNOWN (POBJECT n_old)
$user_constant_at(S.USERCONSTANTS, $ptascii("ParameterNamespaceSeed")) = (puserconstant_old)
puserconstant_old.VALUE = POBJECT n_old
$user_constant_at(S.USERCONSTANTS, $user_constant_key(ptbytes_local)) = eps
S.CONSTCONTEXT = (pconstantcontext)
pconstantcontext.FACTS = [pconstantfact]
pconstantfact.LOOKUP = (pconstantlookup)
pconstantlookup.PREFIX = 1 /\ pconstantlookup.DECL = puserconstant_old.ORIGIN
$global_constant_lookup_valid(S, pconstantcontext.ORIGIN, pconstantfact, S.USERCONSTANTS)
$call_descriptors_valid(S)
S_late = $donor_test_seek($global_test_next(S), ptbytes_function, 0, 1800)
S_late.RESULT = KNOWN (POBJECT n_new)
n_old =/= n_new
$user_constant_at(S_late.USERCONSTANTS, $user_constant_key(ptbytes_local)) = (puserconstant_new)
puserconstant_new.VALUE = POBJECT n_new
S_late.CONSTCONTEXT = (pconstantcontext_late)
pconstantcontext_late.FACTS = [pconstantfact_late]
pconstantfact_late.ORIGIN = pconstantfact.ORIGIN
pconstantfact_late.LOOKUP = (pconstantlookup_late)
pconstantlookup_late.PREFIX = 2 /\ pconstantlookup_late.DECL = puserconstant_new.ORIGIN
$global_constant_lookup_valid(S_late, pconstantcontext_late.ORIGIN, pconstantfact_late, S_late.USERCONSTANTS)
S_late.TODO = (DEFAULT_BIND porigin_function 0) :: ptask_late*
$function_at($all_functions(S_late), porigin_function) = (pfunction)
$parameter_callable_quiet_source(S_late, pconstantfact_late.ORIGIN, eps)
S_rewind = S_late[.RESULT = KNOWN (POBJECT n_old)][.CONSTCONTEXT = (pconstantcontext_late[.FACTS = [pconstantfact_late[.CLASS = puserconstant_old.CLASS][.LOOKUP = (pconstantlookup_late[.PREFIX = 1][.DECL = puserconstant_old.ORIGIN])]]])]
$constant_value_class_valid(S_rewind, POBJECT n_old, puserconstant_old.CLASS)
$heap_valid($heap_graph(S_rewind))
~$parameter_default_transfer_valid(S_rewind, pfunction, 0, POBJECT n_old, puserconstant_old.CLASS)
$global_constant_lookup_valid(S_late, pconstantcontext_late.ORIGIN, pconstantfact_late[.CLASS = puserconstant_old.CLASS][.LOOKUP = (pconstantlookup_late[.PREFIX = 1][.DECL = puserconstant_old.ORIGIN])], S_late.USERCONSTANTS)
S_done = $global_test_finish(S_late, 3600)
S_done.COMPLETION = NORMAL /\ S_done.TODO = eps
$global_test_output(S_done.EVENTS) = $ptascii("old:new:global:local")
S_done.PARAMETERCLOSURES = eps /\ S_done.DEFAULTCACHE = eps
''')
CHECKS['parameter-namespace-warning-prefix']=premises(r'''
ptbytes_function = $ptascii("ParameterNotice") ++ [92] ++ $ptascii("take")
ptbytes_local = $ptascii("ParameterNotice") ++ [92] ++ $ptascii("ParameterNoticeSeed")
S_warning = $donor_test_seek(S_initial[.COMPLETION = NORMAL], ptbytes_function, 2, 2000)
S_warning.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warning*
S_warning.CONSTCONTEXT = (pconstantcontext_early)
S_warning.PARAMETERCLOSURES = eps
$user_constant_at(S_warning.USERCONSTANTS, $user_constant_key(ptbytes_local)) = eps
pconstantcontext_early.FACTS = [pconstantfact_early]
pconstantfact_early.LOOKUP = (pconstantlookup_early)
pconstantlookup_early.PREFIX = 1
$global_constant_lookup_valid(S_warning, pconstantcontext_early.ORIGIN, pconstantfact_early, S_warning.USERCONSTANTS)
$error_call_valid(S_warning, perrorcall) /\ $call_descriptors_valid(S_warning)
S_saved = $donor_test_seek(S_warning, ptbytes_function, 4, 2400)
$donor_test_saved_parameter(S_saved, S_saved.FRAMES) = ((pframe, pframe_tail*))
pframe.CONSTCONTEXT = (pconstantcontext_early)
S_outer = $constant_frame_scope(S_saved, pframe, pframe_tail*)
$user_constant_at(S_saved.USERCONSTANTS, $user_constant_key(ptbytes_local)) = (puserconstant_local)
$global_constant_lookup_valid(S_outer, pconstantcontext_early.ORIGIN, pconstantfact_early, S_saved.USERCONSTANTS)
$default_context_valid(S_outer, pconstantcontext_early)
$call_descriptors_valid(S_saved)
S_resume = $donor_test_seek(S_saved, ptbytes_function, 3, 2000)
$global_test_output(S_resume.EVENTS) = $ptascii("H|")
S_resume.PARAMETERCLOSURES = eps
$call_descriptors_valid(S_resume)
S = $donor_test_seek(S_resume, ptbytes_function, 0, 2200)
S.TODO = (DEFAULT_BIND porigin_function 0) :: ptask_tail*
$function_at($all_functions(S), porigin_function) = (pfunction)
$default_at(pfunction.DEFAULTS, 0) = (pdefault)
S.RESULT = KNOWN (PARRAY n_array)
S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_old)), ENTRY (KINT 1) (DIRECT (POBJECT n_method)), ENTRY (KINT 2) (DIRECT (POBJECT n_local))]
$user_constant_at(S.USERCONSTANTS, $ptascii("ParameterNoticeSeed")) = (puserconstant_old)
puserconstant_old.VALUE = POBJECT n_old /\ puserconstant_local.VALUE = POBJECT n_local
n_old =/= n_local
S.CONSTCONTEXT = (pconstantcontext)
$constant_fact_at(pconstantcontext.FACTS, pconstantfact_early.ORIGIN) = (pconstantfact_early)
porigin_late = $constant_child(pdefault.ORIGIN, [PCFIELD 0, PCINDEX 2, PCFIELD 1])
$constant_fact_at(pconstantcontext.FACTS, porigin_late) = (pconstantfact_late)
pconstantfact_late.LOOKUP = (pconstantlookup_late)
pconstantlookup_late.PREFIX = 2 /\ pconstantlookup_late.DECL = puserconstant_local.ORIGIN
pconstantlookup_early.SITE =/= pconstantlookup_late.SITE
$constant_fact_at(pconstantcontext.FACTS, pdefault.ORIGIN) = (pconstantfact_root)
pconstantfact_root.CLASS = PVARRAY b ([(KINT 0, puserconstant_old.CLASS), (KINT 1, pvalueclass_method), (KINT 2, puserconstant_local.CLASS)])
$global_constant_lookup_valid(S, pconstantcontext.ORIGIN, pconstantfact_early, S.USERCONSTANTS)
$global_constant_lookup_valid(S, pconstantcontext.ORIGIN, pconstantfact_late, S.USERCONSTANTS)
~$parameter_callable_quiet_source(S, pdefault.ORIGIN, eps)
$parameter_callable_quiet_facts(pconstantcontext.FACTS)
$parameter_callable_quiet_key_value((PBOOL false))
~$parameter_callable_quiet_key_value((PNULL))
~$parameter_callable_quiet_key_value((PFLOAT 0))
~$parameter_callable_quiet_class(PVARRAY false ([(KINT 0, PVARRAY false ([(KINT 0, PVINSTANCE n_old puserconstant_old.ORIGIN)]))]))
~$parameter_callable_quiet_class(PVARRAY false ([(KINT 0, PVARRAY false ([(KINT 0, PVOBJECT)]))]))
~$parameter_default_transfer_valid(S, pfunction, 0, PARRAY n_array, pconstantfact_root.CLASS)
$call_descriptors_valid(S)
pconstantfact_rewind = pconstantfact_late[.CLASS = puserconstant_old.CLASS][.LOOKUP = (pconstantlookup_late[.PREFIX = 1][.DECL = puserconstant_old.ORIGIN])]
pconstantfact_rewind.ORIGIN = porigin_late
$global_constant_alias(S, S.USERCONSTANTS[0:1], porigin_late) = (puserconstant_old)
$constant_fact_value_valid(pconstantfact_rewind)
pvalueclass_rewind = PVARRAY b ([(KINT 0, puserconstant_old.CLASS), (KINT 1, pvalueclass_method), (KINT 2, puserconstant_old.CLASS)])
pconstantcontext_rewind = pconstantcontext[.FACTS = $constant_fact_put($constant_fact_put(pconstantcontext.FACTS, pconstantfact_rewind), pconstantfact_root[.CLASS = pvalueclass_rewind])]
S_rewind = S[.CONSTCONTEXT = (pconstantcontext_rewind)][.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_old)), ENTRY (KINT 1) (DIRECT (POBJECT n_method)), ENTRY (KINT 2) (DIRECT (POBJECT n_old))]]
$constant_value_class_valid(S_rewind, PARRAY n_array, pvalueclass_rewind)
$heap_valid($heap_graph(S_rewind))
$global_constant_lookup_valid(S_rewind, pconstantcontext.ORIGIN, pconstantfact_rewind, S.USERCONSTANTS)
$default_context_valid(S_rewind, pconstantcontext_rewind)
~$parameter_default_transfer_valid(S_rewind, pfunction, 0, PARRAY n_array, pvalueclass_rewind)
pconstantfact_forward = pconstantfact_early[.CLASS = puserconstant_local.CLASS][.LOOKUP = (pconstantlookup_early[.PREFIX = 2][.DECL = puserconstant_local.ORIGIN])]
pvalueclass_forward = PVARRAY b ([(KINT 0, puserconstant_local.CLASS), (KINT 1, pvalueclass_method), (KINT 2, puserconstant_local.CLASS)])
pconstantcontext_forward = pconstantcontext[.FACTS = $constant_fact_put($constant_fact_put(pconstantcontext.FACTS, pconstantfact_forward), pconstantfact_root[.CLASS = pvalueclass_forward])]
S_forward = S[.CONSTCONTEXT = (pconstantcontext_forward)][.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_local)), ENTRY (KINT 1) (DIRECT (POBJECT n_method)), ENTRY (KINT 2) (DIRECT (POBJECT n_local))]]
$constant_value_class_valid(S_forward, PARRAY n_array, pvalueclass_forward)
$heap_valid($heap_graph(S_forward))
$global_constant_lookup_valid(S_forward, pconstantcontext.ORIGIN, pconstantfact_forward, S.USERCONSTANTS)
~$parameter_callable_quiet_source(S_forward, pdefault.ORIGIN, eps)
~$parameter_default_transfer_valid(S_forward, pfunction, 0, PARRAY n_array, pvalueclass_forward)
S.COMPLETION = NORMAL
S_transfer = $donor_test_step(S)
S_transfer.COMPLETION = UNSUPPORTED "uncertified parameter callable default transfer"
S_stop = $drive_steps(S_transfer, 40)
S_stop.COMPLETION = UNSUPPORTED "uncertified parameter callable default transfer"
$global_test_output(S_stop.EVENTS) = $ptascii("H|")
S_stop.DEFAULTCACHE = eps
''')
CHECKS['parameter-namespace-warning-retry']=premises(r'''
ptbytes_function = $ptascii("ParameterRetry") ++ [92] ++ $ptascii("take")
ptbytes_local = $ptascii("ParameterRetry") ++ [92] ++ $ptascii("ParameterRetrySeed")
S_first = $donor_test_seek(S_initial[.COMPLETION = NORMAL], ptbytes_function, 2, 2200)
S_first.PARAMETERCLOSURES = eps
S_first.CONSTCONTEXT = (pconstantcontext_first)
pconstantcontext_first.FACTS = [pconstantfact_first]
pconstantfact_first.LOOKUP = (pconstantlookup_first)
pconstantlookup_first.PREFIX = 1
$call_descriptors_valid(S_first)
S_retry = $donor_test_seek($global_test_next(S_first), ptbytes_function, 2, 4200)
$global_test_output(S_retry.EVENTS) = $ptascii("H1|stop|")
S_retry.PARAMETERCLOSURES = eps
S_retry.CONSTCONTEXT = (pconstantcontext_retry)
pconstantcontext_retry.FACTS = [pconstantfact_retry]
pconstantfact_retry.LOOKUP = (pconstantlookup_retry)
pconstantlookup_retry.PREFIX = 2
$user_constant_at(S_retry.USERCONSTANTS, $user_constant_key(ptbytes_local)) = (puserconstant_local)
pconstantlookup_retry.DECL = puserconstant_local.ORIGIN
pconstantfact_retry.CLASS = puserconstant_local.CLASS
$global_constant_lookup_valid(S_retry, pconstantcontext_retry.ORIGIN, pconstantfact_retry, S_retry.USERCONSTANTS)
$call_descriptors_valid(S_retry)
S = $donor_test_seek($global_test_next(S_retry), ptbytes_function, 0, 3000)
S.RESULT = KNOWN (PARRAY n_array)
puserconstant_local.VALUE = POBJECT n_local
S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_local)), ENTRY (KINT 1) (DIRECT (POBJECT n_method)), ENTRY (KINT 2) (DIRECT (POBJECT n_local))]
|S.PARAMETERCLOSURES| = 1
$call_descriptors_valid(S)
S_retry.TODO = (ERROR_HANDLER_INVOKE perrorcall_retry) :: ptask_retry*
S.CONSTCONTEXT = (pconstantcontext_complete)
$constant_expression_root(S, pconstantcontext_complete.ORIGIN) = (porigin_initializer)
~$parameter_callable_quiet_source(S, porigin_initializer, eps)
S.COMPLETION = NORMAL
S_transfer = $donor_test_step(S)
S_transfer.COMPLETION = UNSUPPORTED "uncertified parameter callable default transfer"
S_stop = $drive_steps(S_transfer, 40)
S_stop.COMPLETION = UNSUPPORTED "uncertified parameter callable default transfer"
$global_test_output(S_stop.EVENTS) = $ptascii("H1|stop|H2|")
S_stop.DEFAULTCACHE = eps
''')
CHECKS['parameter-borrowed-emitter-scope']=premises(r'''
S = $donor_test_seek(S_initial[.COMPLETION = NORMAL], $ptascii("takeEmittedDonor"), 0, 2400)
S.RESULT = KNOWN (POBJECT n_donor)
$user_constant_at(S.USERCONSTANTS, $ptascii("ParameterEmittedDonor")) = (puserconstant)
puserconstant.VALUE = POBJECT n_donor
$constant_callable_record(S.CONSTANTCLOSURES, n_donor) = (pconstantclosure)
$closure_scope_at(S.CLOSURESCOPES, n_donor) = (pclosurescope)
$class_at(S.CLASSES, pclosurescope.LEXICAL) = (pclassdesc)
pclassdesc.NAME = $ptascii("ParameterDonorEmitter")
pclosurescope.CALLED = pclosurescope.LEXICAL /\ pclosurescope.RECEIVER = eps
$global_constant_real_scope_valid(S, pconstantclosure.SITE, pclosurescope)
S.CURRENT = (pcallcontext)
pcallcontext.LEXICAL_CLASS = eps /\ pcallcontext.CALLED_CLASS = eps
S.PARAMETERCLOSURES = eps /\ S.DEFAULTCACHE = eps
$call_descriptors_valid(S)
S_done = $global_test_finish(S, 4500)
S_done.COMPLETION = NORMAL /\ S_done.TODO = eps
$global_test_output(S_done.EVENTS) = $ptascii("same:emitter")
$lookup(S_done.ENV, $ptascii("clone")) = (n_cell_clone)
S_done.STORE[n_cell_clone] = DEFINED (POBJECT n_clone)
$constant_callable_record(S_done.CONSTANTCLOSURES, n_clone) = eps
$closure_scope_at(S_done.CLOSURESCOPES, n_clone) = (pclosurescope_clone)
pclosurescope_clone.LEXICAL = pclosurescope.LEXICAL /\ pclosurescope_clone.CALLED = pclosurescope.CALLED
$global_constant_real_scope_valid(S_done, pconstantclosure.SITE, pclosurescope_clone)
~$global_constant_real_scope_valid(S_done, pconstantclosure.SITE, pclosurescope_clone[.CALLED = pconstantclosure.SITE])
S_roots = $prune_allocations(S_done[.ENV = eps][.GLOBALTABLE = eps][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)])
~((HOBJECT n_clone) <- S_roots.ALLOCATIONS) /\ (HOBJECT n_donor) <- S_roots.ALLOCATIONS
$heap_owners($heap_graph(S_roots), HOBJECT n_donor) = 1
$user_constants_valid(S_roots, S_roots.USERCONSTANTS)
''')
CHECKS['parameter-borrowed-private-method']=premises(r'''
S = $donor_test_seek(S_initial[.COMPLETION = NORMAL], $ptascii("takePublicMethod"), 0, 2000)
S.TODO = (DEFAULT_BIND porigin_function 0) :: ptask_tail*
$function_at($all_functions(S), porigin_function) = (pfunction)
$default_at(pfunction.DEFAULTS, 0) = (pdefault)
S.RESULT = KNOWN (POBJECT n_public)
$global_constant_class_alias(S, pdefault.ORIGIN, eps) = (pclassconstantdesc_public)
$constant_callable_alias_class(S, pclassconstantdesc_public) = (pvalueclass_public)
$constant_callable_alias_flow(S, pclassconstantdesc_public, pvalueclass_public, |S.DECLARATIONS|, eps)
$closure_scope_at(S.CLOSURESCOPES, n_public) = (pclosurescope_public)
pclosurescope_public.LEXICAL = pclassconstantdesc_public.OWNER /\ pclosurescope_public.CALLED = pclassconstantdesc_public.OWNER
$closure_scope_row_valid(S, pclosurescope_public)
S.PARAMETERCLOSURES = eps /\ S.DEFAULTCACHE = eps
$call_descriptors_valid(S)
S_again = $donor_test_seek($global_test_next(S), $ptascii("takePublicMethod"), 0, 1800)
S_again.RESULT = KNOWN (POBJECT n_public)
S_private = $donor_test_seek(S_again, $ptascii("ParameterPrivateMethodDonor::take"), 0, 2800)
S_private.TODO = (DEFAULT_BIND porigin_private 0) :: ptask_private*
$function_at($all_functions(S_private), porigin_private) = (pfunction_private)
$default_at(pfunction_private.DEFAULTS, 0) = (pdefault_private)
S_private.CURRENT = (pcallcontext_private)
S_private.RESULT = KNOWN (POBJECT n_private)
n_private =/= n_public
$global_constant_class_alias(S_private, pdefault_private.ORIGIN, pcallcontext_private.LEXICAL_CLASS) = (pclassconstantdesc_private)
pclassconstantdesc_private.VISIBILITY = PROPERTY_PRIVATE
$global_constant_class_alias(S_private, pdefault_private.ORIGIN, eps) = eps
$constant_callable_alias_class(S_private, pclassconstantdesc_private) = (pvalueclass_private)
$parameter_default_transfer_valid(S_private, pfunction_private, 0, POBJECT n_private, pvalueclass_private)
$closure_scope_at(S_private.CLOSURESCOPES, n_private) = (pclosurescope_private)
pclosurescope_private.LEXICAL = pclassconstantdesc_private.OWNER /\ pclosurescope_private.CALLED = pclassconstantdesc_private.OWNER
$call_descriptors_valid(S_private)
S_done = $global_test_finish(S_private, 5500)
S_done.COMPLETION = NORMAL /\ S_done.TODO = eps
$global_test_output(S_done.EVENTS) = $ptascii("same:ParameterPrivateMethodDonor:ParameterPrivateMethodDonor|same:ParameterPrivateMethodDonor:ParameterPrivateMethodDonor|supplied|Cannot access private constant ParameterPrivateMethodDonor::PRIVATE_SEED")
S_done.PARAMETERCLOSURES = eps /\ S_done.DEFAULTCACHE = eps
$lookup(S_done.ENV, $ptascii("copy")) = (n_cell_clone)
S_done.STORE[n_cell_clone] = DEFINED (POBJECT n_clone)
$constant_callable_record(S_done.CONSTANTCLOSURES, n_clone) = eps
$closure_scope_at(S_done.CLOSURESCOPES, n_clone) = (pclosurescope_clone)
pclosurescope_clone.LEXICAL = pclassconstantdesc_public.OWNER /\ pclosurescope_clone.CALLED = pclassconstantdesc_public.OWNER
$closure_scope_row_valid(S_done, pclosurescope_clone)
~$closure_scope_row_valid(S_done, pclosurescope_clone[.LEXICAL = pdefault.ORIGIN])
''')

CHECKS['parameter-object-context-warning']=premises(r'''
ptbytes_function = $ptascii("ParameterNotice") ++ [92] ++ $ptascii("take")
S = $donor_test_seek(S_initial[.COMPLETION = NORMAL], ptbytes_function, 0, 3000)
S.TODO = (DEFAULT_BIND porigin_function 0) :: ptask_tail*
$function_at($all_functions(S), porigin_function) = (pfunction)
$default_at(pfunction.DEFAULTS, 0) = (pdefault)
S.CURRENT = (pcallcontext)
S.CONSTCONTEXT = (pconstantcontext)
S.RESULT = KNOWN (PARRAY n_array)
S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_instance)), ENTRY (KINT 1) (DIRECT (POBJECT n_old)), ENTRY (KINT 2) (DIRECT (POBJECT n_method)), ENTRY (KINT 3) (DIRECT (POBJECT n_local))]
$user_constant_at(S.USERCONSTANTS, $ptascii("ParameterNoticeObjectSeed")) = (puserconstant_object)
puserconstant_object.VALUE = POBJECT n_instance
puserconstant_object.CLASS = PVINSTANCE n_instance porigin_object
$user_constant_at(S.USERCONSTANTS, $ptascii("ParameterNoticeSeed")) = (puserconstant_old)
puserconstant_old.VALUE = POBJECT n_old
$user_constant_at(S.USERCONSTANTS, $user_constant_key($ptascii("ParameterNotice") ++ [92] ++ $ptascii("ParameterNoticeSeed"))) = (puserconstant_local)
puserconstant_local.VALUE = POBJECT n_local /\ n_old =/= n_local
porigin_late = $constant_child(pdefault.ORIGIN, [PCFIELD 0, PCINDEX 3, PCFIELD 1])
$constant_fact_at(pconstantcontext.FACTS, porigin_late) = (pconstantfact_late)
pconstantfact_late.LOOKUP = (pconstantlookup_late)
pconstantlookup_late.PREFIX = 3 /\ pconstantlookup_late.DECL = puserconstant_local.ORIGIN
$constant_fact_at(pconstantcontext.FACTS, pdefault.ORIGIN) = (pconstantfact_root)
pconstantfact_root.CLASS = PVARRAY b ([(KINT 0, puserconstant_object.CLASS), (KINT 1, puserconstant_old.CLASS), (KINT 2, pvalueclass_method), (KINT 3, puserconstant_local.CLASS)])
$constant_value_class_valid(S, PARRAY n_array, pconstantfact_root.CLASS)
$heap_valid($heap_graph(S))
$parameter_callable_quiet_class(puserconstant_local.CLASS)
~$parameter_callable_quiet_class(pconstantfact_root.CLASS)
~$parameter_callable_quiet_facts(pconstantcontext.FACTS)
~$parameter_callable_flow(S, pfunction, 0, porigin_late, pcallcontext.LEXICAL_CLASS, puserconstant_local.CLASS, eps)
~$parameter_default_transfer_valid(S, pfunction, 0, PARRAY n_array, pconstantfact_root.CLASS)
pconstantfact_rewind = pconstantfact_late[.CLASS = puserconstant_old.CLASS][.LOOKUP = (pconstantlookup_late[.PREFIX = 2][.DECL = puserconstant_old.ORIGIN])]
pvalueclass_rewind = PVARRAY b ([(KINT 0, puserconstant_object.CLASS), (KINT 1, puserconstant_old.CLASS), (KINT 2, pvalueclass_method), (KINT 3, puserconstant_old.CLASS)])
pconstantcontext_rewind = pconstantcontext[.FACTS = $constant_fact_put($constant_fact_put(pconstantcontext.FACTS, pconstantfact_rewind), pconstantfact_root[.CLASS = pvalueclass_rewind])]
S_rewind = S[.CONSTCONTEXT = (pconstantcontext_rewind)][.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_instance)), ENTRY (KINT 1) (DIRECT (POBJECT n_old)), ENTRY (KINT 2) (DIRECT (POBJECT n_method)), ENTRY (KINT 3) (DIRECT (POBJECT n_old))]]
$constant_value_class_valid(S_rewind, PARRAY n_array, pvalueclass_rewind)
$heap_valid($heap_graph(S_rewind))
~$parameter_callable_flow(S_rewind, pfunction, 0, porigin_late, pcallcontext.LEXICAL_CLASS, puserconstant_old.CLASS, eps)
~$parameter_default_transfer_valid(S_rewind, pfunction, 0, PARRAY n_array, pvalueclass_rewind)
S.COMPLETION = NORMAL
S_transfer = $donor_test_step(S)
S_transfer.COMPLETION = UNSUPPORTED "uncertified parameter callable default transfer"
S_stop = $drive_steps(S_transfer, 40)
S_stop.COMPLETION = UNSUPPORTED "uncertified parameter callable default transfer"
$global_test_output(S_stop.EVENTS) = $ptascii("H|")
S_stop.DEFAULTCACHE = eps
''')

CHECKS['parameter-quiet-object-context']=premises(r'''
S = $donor_test_seek(S_initial[.COMPLETION = NORMAL], $ptascii("takeQuietObjectContext"), 0, 2200)
S.TODO = (DEFAULT_BIND porigin_function 0) :: ptask_tail*
$function_at($all_functions(S), porigin_function) = (pfunction)
$default_at(pfunction.DEFAULTS, 0) = (pdefault)
S.CURRENT = (pcallcontext)
S.CONSTCONTEXT = (pconstantcontext)
S.RESULT = KNOWN (PARRAY n_array)
S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_instance)), ENTRY (KINT 1) (DIRECT (POBJECT n_donor))]
$user_constant_at(S.USERCONSTANTS, $ptascii("ParameterQuietObjectSeed")) = (puserconstant_object)
puserconstant_object.VALUE = POBJECT n_instance
puserconstant_object.CLASS = PVINSTANCE n_instance porigin_instance
$user_constant_at(S.USERCONSTANTS, $ptascii("ParameterQuietClosureSeed")) = (puserconstant_donor)
puserconstant_donor.VALUE = POBJECT n_donor
porigin_alias = $constant_child(pdefault.ORIGIN, [PCFIELD 0, PCINDEX 1, PCFIELD 1])
$constant_fact_at(pconstantcontext.FACTS, porigin_alias) = (pconstantfact_alias)
pconstantfact_alias.LOOKUP = (pconstantlookup)
pconstantlookup.PREFIX = |S.USERCONSTANTS|
$global_constant_lookup_valid(S, pconstantcontext.ORIGIN, pconstantfact_alias, S.USERCONSTANTS)
$constant_fact_at(pconstantcontext.FACTS, pdefault.ORIGIN) = (pconstantfact_root)
pconstantfact_root.CLASS = PVARRAY b ([(KINT 0, puserconstant_object.CLASS), (KINT 1, puserconstant_donor.CLASS)])
$constant_value_class_valid(S, PARRAY n_array, pconstantfact_root.CLASS)
$heap_valid($heap_graph(S))
$parameter_callable_quiet_source(S, pdefault.ORIGIN, eps)
$parameter_callable_quiet_class(puserconstant_donor.CLASS)
~$parameter_callable_quiet_class(pconstantfact_root.CLASS)
~$parameter_callable_quiet_facts(pconstantcontext.FACTS)
~$parameter_callable_flow(S, pfunction, 0, porigin_alias, pcallcontext.LEXICAL_CLASS, puserconstant_donor.CLASS, eps)
~$parameter_default_transfer_valid(S, pfunction, 0, PARRAY n_array, pconstantfact_root.CLASS)
S.COMPLETION = NORMAL
S_transfer = $donor_test_step(S)
S_transfer.COMPLETION = UNSUPPORTED "uncertified parameter callable default transfer"
S_stop = $drive_steps(S_transfer, 40)
S_stop.COMPLETION = UNSUPPORTED "uncertified parameter callable default transfer"
$global_test_output(S_stop.EVENTS) = eps
S_stop.PARAMETERCLOSURES = eps /\ S_stop.DEFAULTCACHE = eps
''')

CHECKS['parameter-trailing-real-warning']=premises(r'''
ptbytes_function = $ptascii("ParameterNotice") ++ [92] ++ $ptascii("take")
ptbytes_local = $ptascii("ParameterNotice") ++ [92] ++ $ptascii("ParameterNoticeSeed")
S_warning = $donor_test_seek(S_initial[.COMPLETION = NORMAL], ptbytes_function, 2, 2000)
S_warning.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warning*
S_warning.CONSTCONTEXT = (pconstantcontext_early)
S_warning.PARAMETERCLOSURES = eps
$user_constant_at(S_warning.USERCONSTANTS, $user_constant_key(ptbytes_local)) = eps
pconstantcontext_early.FACTS = [pconstantfact_early]
pconstantfact_early.LOOKUP = (pconstantlookup_early)
pconstantlookup_early.PREFIX = 1
$global_constant_lookup_valid(S_warning, pconstantcontext_early.ORIGIN, pconstantfact_early, S_warning.USERCONSTANTS)
$error_call_valid(S_warning, perrorcall) /\ $call_descriptors_valid(S_warning)
S_saved = $donor_test_seek(S_warning, ptbytes_function, 4, 2400)
$donor_test_saved_parameter(S_saved, S_saved.FRAMES) = ((pframe, pframe_tail*))
pframe.CONSTCONTEXT = (pconstantcontext_early)
S_outer = $constant_frame_scope(S_saved, pframe, pframe_tail*)
$user_constant_at(S_saved.USERCONSTANTS, $user_constant_key(ptbytes_local)) = (puserconstant_local)
$global_constant_lookup_valid(S_outer, pconstantcontext_early.ORIGIN, pconstantfact_early, S_saved.USERCONSTANTS)
$default_context_valid(S_outer, pconstantcontext_early)
$call_descriptors_valid(S_saved)
S_resume = $donor_test_seek(S_saved, ptbytes_function, 3, 2000)
$global_test_output(S_resume.EVENTS) = $ptascii("H|")
S_resume.PARAMETERCLOSURES = eps
$call_descriptors_valid(S_resume)
S = $donor_test_seek(S_resume, ptbytes_function, 0, 2200)
S.TODO = (DEFAULT_BIND porigin_function 0) :: ptask_tail*
$function_at($all_functions(S), porigin_function) = (pfunction)
$default_at(pfunction.DEFAULTS, 0) = (pdefault)
S.RESULT = KNOWN (PARRAY n_array)
S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_old)), ENTRY (KINT 1) (DIRECT (POBJECT n_method)), ENTRY (KINT 2) (DIRECT (POBJECT n_local)), ENTRY (KINT 3) (DIRECT (POBJECT n_after))]
$user_constant_at(S.USERCONSTANTS, $ptascii("ParameterNoticeSeed")) = (puserconstant_old)
puserconstant_old.VALUE = POBJECT n_old /\ puserconstant_local.VALUE = POBJECT n_local
n_old =/= n_local
S.CONSTCONTEXT = (pconstantcontext)
$constant_fact_at(pconstantcontext.FACTS, pconstantfact_early.ORIGIN) = (pconstantfact_early)
porigin_late = $constant_child(pdefault.ORIGIN, [PCFIELD 0, PCINDEX 2, PCFIELD 1])
$constant_fact_at(pconstantcontext.FACTS, porigin_late) = (pconstantfact_late)
pconstantfact_late.LOOKUP = (pconstantlookup_late)
pconstantlookup_late.PREFIX = 2 /\ pconstantlookup_late.DECL = puserconstant_local.ORIGIN
pconstantlookup_early.SITE =/= pconstantlookup_late.SITE
porigin_after = $constant_child(pdefault.ORIGIN, [PCFIELD 0, PCINDEX 3, PCFIELD 1])
$parameter_callable_quiet_source(S, porigin_after, eps)
$constant_fact_at(pconstantcontext.FACTS, pdefault.ORIGIN) = (pconstantfact_root)
pconstantfact_root.CLASS = PVARRAY b ([(KINT 0, puserconstant_old.CLASS), (KINT 1, pvalueclass_method), (KINT 2, puserconstant_local.CLASS), (KINT 3, PVCLOSURE n_after porigin_after)])
$global_constant_lookup_valid(S, pconstantcontext.ORIGIN, pconstantfact_early, S.USERCONSTANTS)
$global_constant_lookup_valid(S, pconstantcontext.ORIGIN, pconstantfact_late, S.USERCONSTANTS)
~$parameter_callable_quiet_source(S, pdefault.ORIGIN, eps)
$parameter_callable_quiet_facts(pconstantcontext.FACTS)
$parameter_callable_quiet_key_value((PBOOL false))
~$parameter_callable_quiet_key_value((PNULL))
~$parameter_callable_quiet_key_value((PFLOAT 0))
~$parameter_callable_quiet_class(PVARRAY false ([(KINT 0, PVARRAY false ([(KINT 0, PVINSTANCE n_old puserconstant_old.ORIGIN)]))]))
~$parameter_callable_quiet_class(PVARRAY false ([(KINT 0, PVARRAY false ([(KINT 0, PVOBJECT)]))]))
~$parameter_default_transfer_valid(S, pfunction, 0, PARRAY n_array, pconstantfact_root.CLASS)
$call_descriptors_valid(S)
pconstantfact_rewind = pconstantfact_late[.CLASS = puserconstant_old.CLASS][.LOOKUP = (pconstantlookup_late[.PREFIX = 1][.DECL = puserconstant_old.ORIGIN])]
pconstantfact_rewind.ORIGIN = porigin_late
$global_constant_alias(S, S.USERCONSTANTS[0:1], porigin_late) = (puserconstant_old)
$constant_fact_value_valid(pconstantfact_rewind)
pvalueclass_rewind = PVARRAY b ([(KINT 0, puserconstant_old.CLASS), (KINT 1, pvalueclass_method), (KINT 2, puserconstant_old.CLASS), (KINT 3, PVCLOSURE n_after porigin_after)])
pconstantcontext_rewind = pconstantcontext[.FACTS = $constant_fact_put($constant_fact_put(pconstantcontext.FACTS, pconstantfact_rewind), pconstantfact_root[.CLASS = pvalueclass_rewind])]
S_rewind = S[.CONSTCONTEXT = (pconstantcontext_rewind)][.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_old)), ENTRY (KINT 1) (DIRECT (POBJECT n_method)), ENTRY (KINT 2) (DIRECT (POBJECT n_old)), ENTRY (KINT 3) (DIRECT (POBJECT n_after))]]
$constant_value_class_valid(S_rewind, PARRAY n_array, pvalueclass_rewind)
$heap_valid($heap_graph(S_rewind))
$global_constant_lookup_valid(S_rewind, pconstantcontext.ORIGIN, pconstantfact_rewind, S.USERCONSTANTS)
$default_context_valid(S_rewind, pconstantcontext_rewind)
~$parameter_default_transfer_valid(S_rewind, pfunction, 0, PARRAY n_array, pvalueclass_rewind)
pconstantfact_forward = pconstantfact_early[.CLASS = puserconstant_local.CLASS][.LOOKUP = (pconstantlookup_early[.PREFIX = 2][.DECL = puserconstant_local.ORIGIN])]
pvalueclass_forward = PVARRAY b ([(KINT 0, puserconstant_local.CLASS), (KINT 1, pvalueclass_method), (KINT 2, puserconstant_local.CLASS), (KINT 3, PVCLOSURE n_after porigin_after)])
pconstantcontext_forward = pconstantcontext[.FACTS = $constant_fact_put($constant_fact_put(pconstantcontext.FACTS, pconstantfact_forward), pconstantfact_root[.CLASS = pvalueclass_forward])]
S_forward = S[.CONSTCONTEXT = (pconstantcontext_forward)][.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_local)), ENTRY (KINT 1) (DIRECT (POBJECT n_method)), ENTRY (KINT 2) (DIRECT (POBJECT n_local)), ENTRY (KINT 3) (DIRECT (POBJECT n_after))]]
$constant_value_class_valid(S_forward, PARRAY n_array, pvalueclass_forward)
$heap_valid($heap_graph(S_forward))
$global_constant_lookup_valid(S_forward, pconstantcontext.ORIGIN, pconstantfact_forward, S.USERCONSTANTS)
~$parameter_callable_quiet_source(S_forward, pdefault.ORIGIN, eps)
~$parameter_default_transfer_valid(S_forward, pfunction, 0, PARRAY n_array, pvalueclass_forward)
S.COMPLETION = NORMAL
S_transfer = $donor_test_step(S)
S_transfer.COMPLETION = UNSUPPORTED "uncertified parameter callable default transfer"
S_stop = $drive_steps(S_transfer, 40)
S_stop.COMPLETION = UNSUPPORTED "uncertified parameter callable default transfer"
$global_test_output(S_stop.EVENTS) = $ptascii("H|")
S_stop.DEFAULTCACHE = eps
''')

CHECKS['parameter-deprecated-shadow']=premises(r'''
ptbytes_function = $ptascii("ParameterDeprecated") ++ [92] ++ $ptascii("take")
S = $donor_test_seek(S_initial[.COMPLETION = NORMAL], ptbytes_function, 0, 2600)
S.TODO = (DEFAULT_BIND porigin_function 0) :: ptask_tail*
$function_at($all_functions(S), porigin_function) = (pfunction)
$default_at(pfunction.DEFAULTS, 0) = (pdefault)
S.CONSTCONTEXT = (pconstantcontext)
S.RESULT = KNOWN (PARRAY n_array)
S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_old)), ENTRY (KINT 1) (DIRECT (PINT 2048)), ENTRY (KINT 2) (DIRECT (POBJECT n_local))]
$user_constant_at(S.USERCONSTANTS, $ptascii("ParameterDeprecatedSeed")) = (puserconstant_old)
puserconstant_old.VALUE = POBJECT n_old
$user_constant_at(S.USERCONSTANTS, $user_constant_key($ptascii("ParameterDeprecated") ++ [92] ++ $ptascii("ParameterDeprecatedSeed"))) = (puserconstant_local)
puserconstant_local.VALUE = POBJECT n_local /\ n_old =/= n_local
porigin_notice = $constant_child(pdefault.ORIGIN, [PCFIELD 0, PCINDEX 1, PCFIELD 1])
$global_constant_alias(S, S.USERCONSTANTS, porigin_notice) = (puserconstant_scalar)
puserconstant_scalar.VALUE = PINT 2048 /\ puserconstant_scalar.CLASS = PVSCALAR
$deprecated_constant_source(S, porigin_notice, |S.USERCONSTANTS|) = eps
$deprecated_constant_source(S, porigin_notice, 0) = (z_notice)
~$parameter_callable_quiet_source(S, porigin_notice, eps)
~$parameter_callable_quiet_source(S, pdefault.ORIGIN, eps)
$parameter_callable_quiet_facts(pconstantcontext.FACTS)
porigin_early = $constant_child(pdefault.ORIGIN, [PCFIELD 0, PCINDEX 0, PCFIELD 1])
$constant_fact_at(pconstantcontext.FACTS, porigin_early) = (pconstantfact_early)
pconstantfact_early.LOOKUP = (pconstantlookup_early)
pconstantlookup_early.PREFIX = 1 /\ pconstantlookup_early.DECL = puserconstant_old.ORIGIN
$constant_fact_at(pconstantcontext.FACTS, pdefault.ORIGIN) = (pconstantfact_root)
pconstantfact_root.CLASS = PVARRAY b ([(KINT 0, puserconstant_old.CLASS), (KINT 1, PVSCALAR), (KINT 2, puserconstant_local.CLASS)])
pconstantfact_forward = pconstantfact_early[.CLASS = puserconstant_local.CLASS][.LOOKUP = (pconstantlookup_early[.PREFIX = 3][.DECL = puserconstant_local.ORIGIN])]
pvalueclass_forward = PVARRAY b ([(KINT 0, puserconstant_local.CLASS), (KINT 1, PVSCALAR), (KINT 2, puserconstant_local.CLASS)])
pconstantcontext_forward = pconstantcontext[.FACTS = $constant_fact_put($constant_fact_put(pconstantcontext.FACTS, pconstantfact_forward), pconstantfact_root[.CLASS = pvalueclass_forward])]
S_forward = S[.CONSTCONTEXT = (pconstantcontext_forward)][.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_local)), ENTRY (KINT 1) (DIRECT (PINT 2048)), ENTRY (KINT 2) (DIRECT (POBJECT n_local))]]
$constant_value_class_valid(S_forward, PARRAY n_array, pvalueclass_forward)
$heap_valid($heap_graph(S_forward))
$global_constant_lookup_valid(S_forward, pconstantcontext.ORIGIN, pconstantfact_forward, S.USERCONSTANTS)
~$parameter_callable_quiet_source(S_forward, pdefault.ORIGIN, eps)
~$parameter_default_transfer_valid(S_forward, pfunction, 0, PARRAY n_array, pvalueclass_forward)
~$parameter_default_transfer_valid(S, pfunction, 0, PARRAY n_array, pconstantfact_root.CLASS)
S.COMPLETION = NORMAL
S_transfer = $donor_test_step(S)
S_transfer.COMPLETION = UNSUPPORTED "uncertified parameter callable default transfer"
S_stop = $drive_steps(S_transfer, 40)
S_stop.COMPLETION = UNSUPPORTED "uncertified parameter callable default transfer"
$global_test_output(S_stop.EVENTS) = $ptascii("H|")
''')

CHECKS['parameter-bool-null-values']=premises(r'''
S = $donor_test_seek(S_initial[.COMPLETION = NORMAL], $ptascii("takeBooleanNullKeys"), 0, 2500)
S.TODO = (DEFAULT_BIND porigin_function 0) :: ptask_tail*
$function_at($all_functions(S), porigin_function) = (pfunction)
$default_at(pfunction.DEFAULTS, 0) = (pdefault)
S.CONSTCONTEXT = (pconstantcontext)
S.RESULT = KNOWN (PARRAY n_array)
$constant_fact_at(pconstantcontext.FACTS, pdefault.ORIGIN) = (pconstantfact_root)
$constant_value_class_valid(S, PARRAY n_array, pconstantfact_root.CLASS)
$parameter_callable_quiet_source(S, pdefault.ORIGIN, eps)
$parameter_callable_quiet_facts(pconstantcontext.FACTS)
$parameter_callable_quiet_key_value((PBOOL false))
$parameter_callable_quiet_key_value((PBOOL true))
~$parameter_callable_quiet_key_value((PNULL))
$parameter_default_transfer_valid(S, pfunction, 0, PARRAY n_array, pconstantfact_root.CLASS)
$call_descriptors_valid(S)
S_again = $donor_test_seek($global_test_next(S), $ptascii("takeBooleanNullKeys"), 0, 2500)
$call_descriptors_valid(S_again)
S_done = $global_test_finish(S_again, 4800)
S_done.COMPLETION = NORMAL /\ S_done.TODO = eps
$global_test_output(S_done.EVENTS) = $ptascii("same:values:fresh:donor:fresh")
|S_done.PARAMETERCLOSURES| = 2
S_done.DEFAULTCACHE = eps
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
    out=Path(arguments.prepare_only or arguments.output or str(Path(tempfile.mkdtemp(prefix='parameter-callable-alias-',dir=ROOT/'.tools'))/'prepared'))
    if arguments.prepare_only:
        prepare(out)
    else:
        watched=[Path(__file__),Path(global_protocol.__file__)]
        before={str(p):base.sha(p) for p in watched}
        superseded={'parameter-namespace-warning-prefix','parameter-namespace-warning-retry',
                    'parameter-trailing-real-warning','parameter-deprecated-shadow'}
        original=base.prepare;original_flags=base.RUNNER_FLAGS
        try:
            base.prepare=lambda path:[row for row in prepare(path) if row['id'] not in superseded]
            base.RUNNER_FLAGS={name:['--sl'] for name in (
                'parameter-borrowed-private-method','parameter-object-context-warning',
                'parameter-quiet-object-context','parameter-bool-null-values')}
            base.run(out)
        finally:
            base.prepare=original;base.RUNNER_FLAGS=original_flags
        report=json.loads((out/'report.json').read_text())
        report.update(protocol_inputs=before,protocols_unchanged=before=={str(p):base.sha(p) for p in watched})
        report.update(superseded_causality_cases=sorted(superseded),
                      replacement_protocol='tests/semantics/parameter_alias_causality_protocol.py')
        if not report['protocols_unchanged']:report['result']='failed'
        (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
        assert report['protocols_unchanged'],'protocol changed'
    print(out)

if __name__=='__main__':main()
