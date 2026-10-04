#!/usr/bin/env python3
"""Finite-context source comparisons for include_path mutation."""
import base64
import errno
import hashlib
import json
import locale
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PROFILE = ROOT / 'tests/semantics/profile.json'
locale.setlocale(locale.LC_ALL, 'C')
CASES = {
    'pipe-config-set-empty': b'<?php\nclass PipeEmptyResult {\n    function __toString():string {\n        echo \'C\';\n        ini_set(\'include_path\',"inner\\0tail");\n        return \'\';\n    }\n}\necho (new PipeEmptyResult |> set_include_path(...))===false?\'F\':\'X\',\'|\',get_include_path();\n',
    'pipe-config-getter-exact': b'<?php\nclass PipeGetter {\n    function __toString():string {\n        echo \'C\',func_num_args(),func_get_args()===[]?\'Z\':\'X\';\n        ini_set(\'include_path\',"inner\\0tail");\n        return \'include_path\';\n    }\n}\necho new PipeGetter |> ini_get(...);\necho \'|\',get_include_path();\n',
    'pipe-config-restore-dynamic': b'<?php\nclass PipeRestore {\n    function __toString():string {\n        global $left;\n        echo \'C\',func_num_args(),func_get_args()===[]?\'Z\':\'X\',$left===null?\'N\':\'X\';\n        ini_set(\'include_path\',"inner\\0tail");\n        return \'include_path\';\n    }\n}\nfunction chooseRestoreTarget() {\n    global $left;\n    $left=null;\n    echo \'R\';\n    return \'ini_restore\';\n}\n$left=new PipeRestore;\n$result =\n    $left\n    |>\n    chooseRestoreTarget();\necho $result===null?\'N\':\'X\',\'|\',get_include_path();\n',
    'pipe-config-getter-nul-miss': b'<?php\nclass PipeMiss {\n    function __toString():string {\n        echo \'C\';\n        ini_set(\'include_path\',"inner\\0tail");\n        return "include_path\\0suffix";\n    }\n}\n$get=ini_get(...);\necho (new PipeMiss |> $get)===false?\'F\':\'X\',\'|\',get_include_path();\n',
    'pipe-config-set-leading-nul': b'<?php\nclass PipeEmpty {\n    function __toString():string {\n        echo \'C\';\n        ini_set(\'include_path\',"inner\\0tail");\n        return "\\0after";\n    }\n}\n$set=set_include_path(...);\ntry {new PipeEmpty |> $set;} catch(ValueError $e) {\n    echo $e->getMessage()===\'set_include_path(): Argument #1 ($include_path) must not contain any null bytes\'?\'V\':\'X\';\n}\necho \'|\',get_include_path();\n',
    'pipe-config-throw-keeps-raw': b'<?php\nclass PipeThrow {\n    function __toString():string {\n        echo \'C\';\n        ini_set(\'include_path\',"throw\\0tail");\n        throw new Exception(\'boom\');\n    }\n}\ntry {new PipeThrow |> ini_get(...);} catch(Exception $e) {echo $e->getMessage()===\'boom\'?\'T\':\'X\';}\necho \'|\',get_include_path();\n',
    'pipe-config-ini-set-arity': b"<?php\nclass PipeArity {\n    function __toString():string {echo 'BAD';return 'include_path';}\n}\ntry {new PipeArity |> ini_set(...);} catch(ArgumentCountError $e) {\n    echo $e->getMessage()==='ini_set() expects exactly 2 arguments, 1 given'?'A':'X';\n}\necho '|',get_include_path();\n",
    'pipe-config-optimized-strict-refusal': b'<?php\ndeclare(strict_types=1);\nini_set(\'include_path\', "before\\0tail");\nclass PipeStrictValue {\n    public function __toString(): string { echo \'BAD\'; return \'after\'; }\n}\n$value = new PipeStrictValue;\ntry {\n    $value |> set_include_path(...);\n    echo \'BAD\';\n} catch (TypeError $e) {\n    echo $e->getMessage() === \'set_include_path(): Argument #1 ($include_path) must be of type string, PipeStrictValue given\' ? \'R\' : \'X\';\n}\necho \'|\', get_include_path();\n',
    'independent-config-pipe-owned-strict-refusal': b'<?php\ndeclare(strict_types=1);\nini_set(\'include_path\', "before\\0tail");\nclass PipeStrictValue {\n    public function __toString(): string { echo \'BAD\'; return \'after\'; }\n}\n$value = new PipeStrictValue;\n$target = set_include_path(...);\ntry {\n    $value |> $target;\n    echo \'BAD\';\n} catch (TypeError $e) {\n    echo $e->getMessage() === \'set_include_path(): Argument #1 ($include_path) must be of type string, PipeStrictValue given\' ? \'R\' : \'X\';\n}\necho \'|\', get_include_path();\n',
    'independent-config-pipe-owned-held-left': b'<?php\nini_set(\'include_path\', "before\\0tail");\nclass PipeHeldValue {\n    public function __toString(): string {\n        global $left;\n        echo \'C\', func_num_args(), func_get_args() === [] ? \'Z\' : \'X\', $left === null ? \'N\' : \'X\';\n        ini_set(\'include_path\', "inner\\0tail");\n        return \'after\';\n    }\n}\nfunction choosePipeTarget() {\n    global $left;\n    $left = null;\n    echo \'R\';\n    return set_include_path(...);\n}\n$left = new PipeHeldValue;\n$old = $left |> choosePipeTarget();\necho $old, \'|\', get_include_path();\n',
    'ini-readback-null-handler-owned-restore-throw': b'<?php\ndeclare(strict_types=1);\nini_set(\'include_path\', "before\\0tail");\nfunction ReadbackThrow(string $level, $message, $file, $line): void {\n    $args = func_get_args();\n    echo \'H\', func_num_args();\n    echo $level === \'8192\' && $args[0] === \'8192\'\n        && $message === \'ini_restore(): Passing null to parameter #1 ($option) of type string is deprecated\'\n        ? \'W\' : \'X\';\n    ini_set(\'include_path\', "throw\\0tail");\n    throw new Exception(\'stop\');\n}\nfunction ReadbackCaller($first, $second): void {\n    $saved = func_get_args();\n    echo func_num_args(), \':\', $saved[0], \':\', $saved[1], \'|\';\n    $restore = ini_restore(...);\n    try {\n        $restore->__invoke(option: null);\n        echo \'BAD\';\n    } catch (Exception $e) {\n        echo $e->getMessage() === \'stop\' ? \'T\' : \'X\';\n        $trace = $e->getTrace();\n        echo $trace[1][\'function\'] === \'ini_restore\' && $trace[1][\'args\'][0] === null ? \'I\' : \'X\';\n    }\n    echo func_num_args() === 2 && func_get_args() === $saved ? \'S\' : \'X\';\n    echo \'|\', get_include_path();\n}\nset_error_handler(\'ReadbackThrow\', 8192);\nReadbackCaller(second: \'B\', first: \'A\');\necho \'|\', get_error_handler() === \'ReadbackThrow\' ? \'R\' : \'X\';\nrestore_error_handler();\n',
    'ini-readback-null-handler-live-raw': b'<?php\nini_set(\'include_path\',"before\\0tail");\nfunction nullReadHandler($level,$message,$file,$line){\n    echo \'H\',func_num_args();\n    echo $level===8192&&$message===\'ini_get(): Passing null to parameter #1 ($option) of type string is deprecated\'&&$file===__FILE__?\'D\':\'X\';\n    echo get_error_handler()===null?\'Z\':\'X\';\n    echo get_include_path();\n    ini_set(\'include_path\',"handled\\0tail");\n    return 0;\n}\nfunction readRaw($first,$second){\n    $saved=func_get_args();\n    echo func_num_args(),\':\',$saved[0],\':\',$saved[1],\'|\';\n    set_error_handler(\'nullReadHandler\',8192);\n    $result=ini_get(option:null);\n    echo $result===false?\'F\':\'X\';\n    echo func_num_args()===2&&func_get_args()===$saved?\'S\':\'X\';\n    echo \'|\',get_include_path();\n    restore_error_handler();\n    echo get_error_handler()===null?\'R\':\'X\';\n}\nreadRaw(second:\'B\',first:\'A\');\n',
    'ini-readback-null-handler-owned-restore-fallback': b'<?php\ndeclare(strict_types=1);\nini_set(\'include_path\',"before\\0tail");\nfunction restoreNullHandler($level,$message,$file,$line){\n    echo \'H\',func_num_args();\n    echo $level===8192&&$message===\'ini_restore(): Passing null to parameter #1 ($option) of type string is deprecated\'&&$file===__FILE__?\'D\':\'X\';\n    ini_set(\'include_path\',"restored\\0tail");\n    return false;\n}\n$f=ini_restore(...);\nset_error_handler(\'restoreNullHandler\',8192);\necho @$f->__invoke(option:null)===null?\'N\':\'X\';\necho \'|\',get_include_path();\nrestore_error_handler();\necho get_error_handler()===null?\'R\':\'X\';\n',
    'set-restore': b"<?php echo include 'one.php'; echo set_include_path('__SUB__'); echo include 'one.php'; ini_restore('include_path'); echo include 'one.php';",
    'ini-set': b"<?php echo ini_set('include_path','__SUB__'); echo include 'one.php';",
    'ini-case': b"<?php echo ini_set('INCLUDE_PATH','__SUB__')?'Y':'N'; echo include 'one.php';",
    'named-error': b"<?php function a(){echo 'A';return 'sub';} function b(){echo 'B';return 7;} try{set_include_path(include_path:a(),bad:b());}catch(Error $e){echo '|',$e->getMessage(),'|';} echo include 'one.php';",
    'first-class': b"<?php $f=set_include_path(...); echo $f('__SUB__'); echo include 'one.php';",
    'dynamic-restore': b"<?php set_include_path('sub'); $f='ini_restore'; $f('include_path'); echo set_include_path('z');",
    'dynamic-ini-set': b"<?php $f='ini_set'; echo $f(option:'include_path',value:'sub');",
    'dynamic-mutated-callee': b'<?php $f="set_include_path"; function mutate(){global $f; $f="ini_restore"; return "sub";} echo $f(mutate()),"|",set_include_path("end");',
    'dynamic-ref-finally': b"<?php function &r($tmp):string{$x='sub';try{if($tmp)return 'sub';return $x;}finally{echo 'R';}} function arg(){global $f;r(false);r(true);$f='ini_restore';return 'sub';} $f='set_include_path'; echo $f(arg()),'|',set_include_path('end');",
    'dynamic-caught-reentry': b'<?php function g($x){$f="set_include_path"; return $f($x ? throw new Exception("boom") : "sub");} try{g(true);}catch(Throwable $e){} echo g(false);',
    'dynamic-pipe': b'<?php $f="set_include_path"; echo "sub" |> $f;',
    'fixed-pipe': b'<?php echo "sub" |> set_include_path(...);',
    'dynamic-chdir': b"<?php $f='chdir'; $f('__SUB__'); echo include 'one.php';",
    'named': b"<?php echo ini_set(value:'__SUB__',option:'include_path'); echo include 'one.php';",
    'unpack': b"<?php echo set_include_path(...['include_path'=>'__SUB__']); echo include 'one.php';",
    'empty': b"<?php echo set_include_path('')?'Y':'N'; echo include 'one.php';",
    'null': b"<?php echo set_include_path(null)?'Y':'N'; echo include 'one.php';",
    'ini-false': b"<?php echo ini_set('include_path',false)?'Y':'N'; echo include 'one.php';",
    'ini-null': b"<?php echo ini_set('include_path',null)?'Y':'N'; echo include 'one.php';",
    'strict-ini-int': b"<?php declare(strict_types=1); echo ini_set('include_path',123);",
    'strict-set-int': b"<?php declare(strict_types=1); try{set_include_path(123);}catch(TypeError $e){echo $e->getMessage();} echo include 'one.php';",
    'set-nul': b"<?php try{set_include_path(\"a\\0b\");}catch(ValueError $e){echo $e->getMessage();} echo include 'one.php';",
    'chdir-success': b"<?php echo include 'one.php'; echo chdir('__SUB__')?'T':'F'; echo include 'one.php';",
    'chdir-relative': b"<?php echo include 'one.php'; echo chdir('sub')?'T':'F'; echo include 'one.php';",
    'chdir-function': b"<?php function f(){return chdir('__SUB__');} echo include 'one.php'; f(); echo include 'one.php';",
    'chdir-once': b"<?php echo include_once 'one.php'; chdir('__SUB__'); echo include_once 'one.php';",
    'chdir-failure': b"<?php echo chdir('missing')?'T':'F'; echo include 'one.php';",
    'chdir-empty': b"<?php echo chdir('')?'T':'F'; echo include 'one.php';",
    'chdir-nul': b"<?php try{chdir(\"a\\0b\");}catch(ValueError $e){echo $e->getMessage();} echo include 'one.php';",
    'chdir-null': b"<?php echo chdir(null)?'T':'F'; echo include 'one.php';",
    'chdir-weak-int': b"<?php echo chdir(123)?'T':'F'; echo include 'one.php';",
    'chdir-strict-int': b"<?php declare(strict_types=1); try{chdir(123);}catch(TypeError $e){echo $e->getMessage();} echo include 'one.php';",
    'chdir-named': b"<?php chdir(directory:'__SUB__'); echo include 'one.php';",
    'chdir-unpack': b"<?php chdir(...['directory'=>'__SUB__']); echo include 'one.php';",
    'chdir-first-class': b"<?php $f=chdir(...); $f('__SUB__'); echo include 'one.php';",
    'included-function-chdir': b"<?php include 'mutate.php'; echo include 'one.php';",
    'chdir-stringable-weak': b"<?php class O { function __toString(): string { echo 'S'; return '__SUB__'; } } echo chdir(new O)?'T':'F'; echo include 'one.php';",
    'chdir-stringable-throw-lines': b'<?php\nclass O { function __toString(): string { throw new Exception("X"); } }\nchdir(\n  new O\n);\n',
    'chdir-stringable-nul': b'<?php class O { function __toString(): string { echo "S"; return "a\\0b"; } } try { chdir(new O); } catch (ValueError $e) { echo "V"; } echo include "one.php";',
    'chdir-stringable-nul-uncaught': b'<?php class O { function __toString(): string { return "a\\0b"; } } chdir(new O);',
    'chdir-stringable-invoke-nul': b'<?php class O { function __toString(): string { return "a\\0b"; } } $f=chdir(...); $f->__invoke(new O);',
    'chdir-stringable-invoke-throw': b'<?php class O { function __toString(): string { throw new Exception("X"); } } $f=chdir(...); $f->__invoke(new O);',
    'chdir-stringable-invoke-nested-throw': b'<?php class O { function __toString(): string { $this->g(); return "sub"; } function g(): void { throw new Exception("X"); } } $f=chdir(...); $f->__invoke(new O);',
    'chdir-stringable-inherited-invoke-throw': b'<?php class P {function __toString():string {throw new Exception("X");}} class O extends P {} $f=chdir(...); $f->__invoke(new O);',
    'chdir-stringable-inherited-case-invoke-throw': b'<?php class P {function __ToStRiNg():string {throw new Exception("X");}} class O extends P {} $f=chdir(...); $f->__invoke(new O);',
    'chdir-stringable-strict': b'<?php declare(strict_types=1); class O { function __toString(): string { echo "S"; return "sub"; } } try { chdir(new O); } catch (TypeError $e) { echo "T"; } echo include "one.php";',
    'chdir-object-nonstringable': b'<?php class O {} try { chdir(new O); } catch (TypeError $e) { echo "T"; } echo include "one.php";',
    'chdir-stringable-dynamic': b"<?php class O { function __toString(): string { echo 'S'; return '__SUB__'; } } $f='chdir'; echo $f(new O)?'T':'F'; echo include 'one.php';",
    'chdir-stringable-first-class': b"<?php class O { function __toString(): string { echo 'S'; return '__SUB__'; } } $f=chdir(...); echo $f(new O)?'T':'F'; echo include 'one.php';",
    'chdir-stringable-nested-throw': b'<?php class O { function __toString(): string { $this->g(); return "sub"; } function g(): void { throw new Exception("X"); } } chdir(new O);',
    'chdir-stringable-mutate-cwd': b"<?php class O { function __toString(): string { chdir('__SUB__'); return '..'; } } echo chdir(new O)?'T':'F'; echo include 'one.php';",
    'chdir-stringable-nested-conversion': b"<?php class P { function __toString():string { echo 'P'; return '__SUB__'; } } class O { function __toString():string { echo 'O'; $g='chdir'; $g(new P); return '..'; } } $f='chdir'; echo $f(new O)?'T':'F'; echo include 'one.php';",
    'chdir-stringable-named': b"<?php class O { function __toString():string { echo 'S'; return '__SUB__'; } } echo chdir(directory:new O)?'T':'F'; echo include 'one.php';",
    'chdir-stringable-named-selection': b"<?php class O { function __toString():string { echo 'S'; return '__SUB__'; } } function swap($v){global $f; echo 'A'; $f='ini_restore'; return new O;} $f='chdir'; echo $f(directory:swap($f))?'T':'F'; echo include 'one.php'; echo '|',$f;",
    'chdir-stringable-named-first-class': b"<?php class O { function __toString():string { echo 'S'; return '__SUB__'; } } $f=chdir(...); echo $f(directory:new O)?'T':'F'; echo include 'one.php';",
    'chdir-stringable-named-invoke': b"<?php class O { function __toString():string { echo 'S'; return '__SUB__'; } } $f=chdir(...); echo $f->__invoke(directory:new O)?'T':'F'; echo include 'one.php';",
    'chdir-stringable-named-mutate-cwd': b"<?php class O { function __toString():string { echo 'S'; chdir('__SUB__'); return '..'; } } echo chdir(directory:new O)?'T':'F'; echo include 'one.php';",
    'chdir-stringable-named-nul': b'<?php class O { function __toString():string { echo "S"; return "a\\0b"; } } chdir(directory:new O);',
    'chdir-stringable-named-invoke-nul': b'<?php class O { function __toString():string { echo "S"; return "a\\0b"; } } $f=chdir(...); $f->__invoke(directory:new O);',
    'chdir-stringable-named-inherited-case-throw': b'<?php class P { function __ToStRiNg():string { throw new Exception("X"); } } class O extends P {} $f=chdir(...); $f->__invoke(directory:new O);',
    'chdir-stringable-named-strict': b'<?php declare(strict_types=1); class O { function __toString():string { echo "S"; return "sub"; } } chdir(directory:new O);',
    'chdir-stringable-named-strict-first-class': b'<?php declare(strict_types=1); class O { function __toString():string { echo "S"; return "sub"; } } $f=chdir(...); $f(directory:new O);',
    'chdir-stringable-named-strict-invoke': b'<?php declare(strict_types=1); class O { function __toString():string { echo "S"; return "a\\0b"; } } $f=chdir(...); $f->__invoke(directory:new O);',
    'chdir-object-named-nonstringable': b'<?php class O {} chdir(directory:new O);',
    'chdir-object-named-unknown': b'<?php class O { function __toString():string { echo "T"; return "sub"; } } function a(){echo "A"; return new O;} $f=chdir(...); $f->__invoke(bad:a());',
    'chdir-object-named-case': b'<?php class O { function __toString():string { echo "T"; return "sub"; } } function a(){echo "A"; return new O;} chdir(Directory:a());',
    'chdir-object-named-duplicate': b'<?php class O { function __toString():string { echo "T"; return "sub"; } } function a($s){echo $s; return new O;} chdir(a("A"),directory:a("B"));',
    'chdir-object-named-count': b'<?php class O { function __toString():string { echo "T"; return "sub"; } } function a($s){echo $s; return new O;} chdir(a("A"),a("B"));',
    'chdir-object-named-invoke-count': b'<?php class O { function __toString():string { echo "T"; return "sub"; } } function a($s){echo $s; return new O;} $f=chdir(...); $f->__invoke(a("A"),a("B"));',
    'chdir-stringable-unpack-positional': b"<?php class O { function __toString():string { echo 'S'; return '__SUB__'; } } echo chdir(...[new O])?'T':'F'; echo include 'one.php';",
    'chdir-stringable-unpack-selection': b"<?php class O { function __toString():string { echo 'S'; return '__SUB__'; } } function swap(){global $f; echo 'A'; $f='ini_restore'; return ['directory'=>new O];} $f='chdir'; echo $f(...swap())?'T':'F'; echo include 'one.php'; echo '|',$f;",
    'chdir-stringable-unpack-ordinary-before-empty': b"<?php class O { function __toString():string { echo 'S'; return '__SUB__'; } } echo chdir(new O,...[])?'T':'F'; echo include 'one.php';",
    'chdir-stringable-unpack-ordinary-after-empty': b"<?php class O { function __toString():string { echo 'S'; return '__SUB__'; } } echo chdir(...[],directory:new O)?'T':'F'; echo include 'one.php';",
    'chdir-stringable-unpack-first-class-empty': b"<?php class O { function __toString():string { echo 'S'; return '__SUB__'; } } $f=chdir(...); echo $f(...[],...['directory'=>new O],...[])?'T':'F'; echo include 'one.php';",
    'chdir-stringable-unpack-invoke': b"<?php class O { function __toString():string { echo 'S'; return '__SUB__'; } } $f=chdir(...); echo $f->__invoke(...['directory'=>new O])?'T':'F'; echo include 'one.php';",
    'chdir-stringable-unpack-capture-retired': b"<?php class O {function __toString():string {global $x,$a; echo ($x==='changed' && $a===[])?'E':'N'; echo 'T'; throw new Exception('X');}} $x=new O; $a=['directory'=>&$x]; function later(){global $x,$a; echo 'A'; $x='changed'; $a=[]; return [];} $f=chdir(...); $f->__invoke(...$a,...later());",
    'chdir-stringable-unpack-mutate-cwd': b"<?php class O { function __toString():string { echo 'S'; chdir('__SUB__'); return '..'; } } echo chdir(...['directory'=>new O])?'T':'F'; echo include 'one.php';",
    'chdir-stringable-unpack-nul': b'<?php class O { function __toString():string { echo "S"; return "a\\0b"; } } chdir(...[new O]);',
    'chdir-stringable-unpack-invoke-nul': b'<?php class O { function __toString():string { echo "S"; return "a\\0b"; } } $f=chdir(...); $f->__invoke(...["directory"=>new O]);',
    'chdir-stringable-unpack-inherited-case-throw': b'<?php class P { function __ToStRiNg():string { throw new Exception("X"); } } class O extends P {} $f=chdir(...); $f->__invoke(...[],...["directory"=>new O],...[]);',
    'chdir-stringable-unpack-strict': b'<?php declare(strict_types=1); class O { function __toString():string { echo "S"; return "sub"; } } chdir(...[new O]);',
    'chdir-stringable-unpack-strict-first-class': b'<?php declare(strict_types=1); class O { function __toString():string { echo "S"; return "sub"; } } $f=chdir(...); $f(...["directory"=>new O]);',
    'chdir-stringable-unpack-strict-invoke': b'<?php declare(strict_types=1); class O { function __toString():string { echo "S"; return "a\\0b"; } } $f=chdir(...); $f->__invoke(...["directory"=>new O]);',
    'chdir-object-unpack-unknown': b'<?php class O { function __toString():string { echo "T"; return "sub"; } } function a(){echo "A"; return new O;} $f=chdir(...); $f->__invoke(...["bad"=>a()]);',
    'chdir-object-unpack-duplicate': b'<?php class O { function __toString():string { echo "T"; return "sub"; } } function a($s){echo $s; return new O;} chdir(...[a("A")],...["directory"=>a("B")]);',
    'chdir-object-unpack-array-order': b'<?php class O { function __toString():string { echo "T"; return "sub"; } } function a($s){echo $s; return new O;} function later(){echo "L"; return [];} chdir(...["directory"=>a("A"),a("B")],...later());',
    'chdir-object-unpack-pack-order': b'<?php class O { function __toString():string { echo "T"; return "sub"; } } function a($s){echo $s; return new O;} $f=chdir(...); $f->__invoke(...["directory"=>a("A")],...[a("B")]);',
    'chdir-object-unpack-empty-count': b'<?php $f=chdir(...); $f->__invoke(...[],...[]);',
    'chdir-object-unpack-positional-count': b'<?php class O { function __toString():string { echo "T"; return "sub"; } } function a($s){echo $s; return new O;} chdir(...[a("A"),a("B")]);',
    'set-unpack-retained': b"<?php echo set_include_path(...['include_path'=>'__SUB__']); echo include 'one.php';",
    'ini-set-unpack-retained': b"<?php echo ini_set(...['value'=>'__SUB__'],...['option'=>'include_path']); echo include 'one.php';",
    'ini-restore-unpack-retained': b"<?php set_include_path('__SUB__'); ini_restore(...['option'=>'include_path']); echo include 'one.php';",
    'set-stringable-direct': b"<?php class O { function __toString():string { echo 'S'; return '__SUB__'; } } echo set_include_path(new O); echo include 'one.php';",
    'set-stringable-first-class': b"<?php class O { function __toString():string { echo 'S'; return '__SUB__'; } } $f=set_include_path(...); echo $f(new O); echo include 'one.php';",
    'set-stringable-named-invoke': b"<?php class O { function __toString():string { echo 'S'; return '__SUB__'; } } $f=set_include_path(...); echo $f->__invoke(include_path:new O); echo include 'one.php';",
    'set-stringable-selection': b"<?php class O { function __toString():string { echo 'S'; return '__SUB__'; } } function swap($v){global $f; echo 'A'; $f='ini_restore'; return new O;} $f='set_include_path'; echo $f(include_path:swap($f)); echo include 'one.php'; echo '|',$f;",
    'set-stringable-mutate-ini': b"<?php class O {function __toString():string {echo set_include_path('inner'); return 'outer';}} echo set_include_path(new O); echo '|'; echo set_include_path('.:');",
    'set-stringable-empty': b"<?php class O {function __toString():string {echo set_include_path('inner'); return '';}} echo set_include_path(new O)?'T':'F'; echo set_include_path('.:');",
    'set-stringable-unpack-capture-retired': b"<?php class O {function __toString():string {global $x,$a; echo ($x==='changed' && $a===[])?'E':'N'; echo 'T'; return 'outer';}} $x=new O; $a=['include_path'=>&$x]; function later(){global $x,$a; echo 'A'; $x='changed'; $a=[]; return [];} $f=set_include_path(...); echo $f->__invoke(...$a,...later()); echo '|',set_include_path('end');",
    'set-stringable-ordinary-after-empty': b"<?php class O { function __toString():string { echo 'S'; return '__SUB__'; } } echo set_include_path(...[],include_path:new O); echo include 'one.php';",
    'set-stringable-nested-chdir': b"<?php class P {function __toString():string {echo 'P';return '__SUB__';}} class O {function __toString():string {echo chdir(new P)?'T':'F';return '.:';}} echo set_include_path(new O); echo include 'one.php';",
    'set-stringable-caught-throw': b"<?php class O {function __toString():string {set_include_path('inner');throw new Exception('X');}} try{set_include_path(new O);}catch(Exception $e){echo set_include_path('end');}",
    'set-stringable-nul': b'<?php class O {function __toString():string {echo "S";return "a\\0b";}} set_include_path(new O);',
    'set-stringable-invoke-nul': b'<?php class O {function __toString():string {echo "S";return "a\\0b";}} $f=set_include_path(...);$f->__invoke(include_path:new O);',
    'set-stringable-mutated-nul': b'<?php class O {function __toString():string {set_include_path("inner");return "a\\0b";}} try{set_include_path(new O);}catch(ValueError $e){echo set_include_path(".:");}',
    'set-stringable-inherited-case-throw': b'<?php class P {function __ToStRiNg():string {throw new Exception("X");}} class O extends P {} $f=set_include_path(...);$f->__invoke(...[],...["include_path"=>new O],...[]);',
    'set-stringable-strict': b'<?php declare(strict_types=1);class O {function __toString():string {echo "T";return "outer";}} set_include_path(include_path:new O);',
    'set-stringable-strict-first-class': b'<?php declare(strict_types=1);class O {function __toString():string {echo "T";return "outer";}} $f=set_include_path(...);$f(...[new O]);',
    'set-stringable-strict-invoke': b"<?php declare(strict_types=1);class O {function __toString():string {echo 'T';return 'outer';}} $f=set_include_path(...);echo $f->__invoke(include_path:new O);",
    'set-object-nonstringable': b'<?php class O {} set_include_path(new O);',
    'set-object-named-unknown': b"<?php class O {function __toString():string {echo 'T';return 'outer';}} function a(){echo 'A';return new O;} $f=set_include_path(...);$f->__invoke(directory:a());",
    'set-object-unpack-duplicate': b"<?php class O {function __toString():string {echo 'T';return 'outer';}} function a($s){echo $s;return new O;} set_include_path(...[a('A')],...['include_path'=>a('B')]);",
    'set-object-unpack-count': b"<?php class O {function __toString():string {echo 'T';return 'outer';}} function a($s){echo $s;return new O;} $f=set_include_path(...);$f->__invoke(...[a('A'),a('B')]);",
    'ini-set-object-value': b"<?php class O {function __toString():string {echo 'T';return 'outer';}} ini_set('include_path',new O);",
    'ini-set-object-value-strict': b"<?php declare(strict_types=1);class O {function __toString():string {echo 'T';return 'outer';}} ini_set('include_path',new O);",
    'ini-set-object-value-invoke-named': b"<?php class O {function __toString():string {echo 'T';return 'outer';}} $f=ini_set(...);$f->__invoke(value:new O,option:'include_path');",

    'ini-prefix-scalar-set-old': b'<?php ini_set(\'include_path\',"a\\0b");echo set_include_path(\'end\');',
    'ini-prefix-stringable-set-old': b'<?php class O {function __toString():string {echo \'T\';return \'end\';}} ini_set(\'include_path\',"a\\0b");echo set_include_path(new O);',
    'ini-prefix-stringable-set-live-old': b'<?php class O {function __toString():string {ini_set(\'include_path\',"inner\\0tail");return \'end\';}} ini_set(\'include_path\',"before\\0tail");echo set_include_path(new O);',
    'ini-prefix-ini-old-full': b'<?php echo ini_set(\'include_path\',"a\\0b"),\'|\',ini_set(\'include_path\',\'end\');',
    'ini-prefix-leading-nul': b'<?php set_include_path(\'inner\');echo ini_set(\'include_path\',"\\0tail")?\'Y\':\'F\';echo \'|\',set_include_path(\'end\');',
    'ini-prefix-empty': b"<?php set_include_path('inner');echo ini_set('include_path','')?'Y':'F';echo '|',set_include_path('end');",
    'ini-prefix-null': b"<?php set_include_path('inner');echo ini_set('include_path',null)?'Y':'F';echo '|',set_include_path('end');",
    'ini-prefix-leading-nul-preserves-raw': b'<?php ini_set(\'include_path\',"a\\0b");echo ini_set(\'include_path\',"\\0tail")?\'Y\':\'F\';echo \'|\',ini_set(\'include_path\',\'end\');',
    'ini-prefix-callback-leading-nul': b'<?php class O {function __toString():string {echo ini_set(\'include_path\',"\\0tail")?\'Y\':\'F\';return \'end\';}} ini_set(\'include_path\',"a\\0b");echo set_include_path(new O);',
    'ini-prefix-interior-nul-include': b'<?php ini_set(\'include_path\',"__SUB__\\0suffix");echo include \'one.php\';',
    'ini-prefix-interior-nul-missing-require': b'<?php ini_set(\'include_path\',"__SUB__\\0suffix");require \'missing-prefix.php\';',
    'ini-prefix-invoke-bare-old-full': b'<?php class I {function __invoke($value){return ini_set(\'include_path\',$value);}} $o=new I;$o(value:"a\\0b");echo $o(value:\'end\');',
    'ini-prefix-invoke-capture-leading-raw': b'<?php class I {function __invoke($value){return ini_set(\'include_path\',$value);}} $o=new I;$f=$o(...);$o=0;$f("a\\0b");echo $f(value:"\\0bad")?\'Y\':\'F\';echo \'|\',set_include_path(\'end\');',
    'ini-prefix-invoke-typed-callable': b'<?php class I {function __invoke($value){return ini_set(\'include_path\',$value);}} function feed(callable $f,string $value){return $f($value);} $o=new I;feed($o,"a\\0b");echo feed($o,\'end\');',
    'ini-prefix-invoke-set-live-old': b'<?php class I {function __invoke(){ini_set(\'include_path\',"inner\\0tail");}} class O {function __toString():string {(new I)();return \'end\';}} ini_set(\'include_path\',"before\\0tail");echo set_include_path(new O);',
    'ini-prefix-invoke-frame-include': b'<?php class I {function __invoke(){ini_set(\'include_path\',"__SUB__\\0suffix");echo include \'one.php\';}} (new I)();',

    'restore-stringable-direct': b"<?php class O {function __toString():string {echo 'T';return 'include_path';}} set_include_path('before');ini_restore(new O);echo '|',set_include_path('end');",
    'restore-stringable-first-class': b"<?php class O {function __toString():string {echo 'T';return 'include_path';}} set_include_path('before');$f=ini_restore(...);$f(new O);echo '|',set_include_path('end');",
    'restore-stringable-named': b"<?php class O {function __toString():string {echo 'T';return 'include_path';}} set_include_path('before');ini_restore(option:new O);echo '|',set_include_path('end');",
    'restore-stringable-named-invoke': b"<?php class O {function __toString():string {echo 'T';return 'include_path';}} set_include_path('before');$f=ini_restore(...);$f->__invoke(option:new O);echo '|',set_include_path('end');",
    'restore-stringable-selection': b"<?php class O {function __toString():string {echo 'T';return 'include_path';}} function a(){global $f;$f='set_include_path';return new O;} set_include_path('before');$f='ini_restore';$f(option:a());echo '|',set_include_path('end');",
    'restore-stringable-mutate-ini': b"<?php class O {function __toString():string {echo 'T';set_include_path('inner');return 'include_path';}} ini_restore(new O);echo '|',set_include_path('end');",
    'restore-stringable-case': b"<?php class O {function __toString():string {echo 'T';set_include_path('inner');return 'INCLUDE_PATH';}} ini_restore(new O);echo '|',set_include_path('end');",
    'restore-stringable-empty': b"<?php class O {function __toString():string {echo 'T';set_include_path('inner');return '';}} ini_restore(new O);echo '|',set_include_path('end');",
    'restore-stringable-nul': b'<?php class O {function __toString():string {echo \'T\';set_include_path(\'inner\');return "include_path\\0suffix";}} $f=ini_restore(...);$f->__invoke(option:new O);echo \'|\',set_include_path(\'end\');',
    'restore-stringable-unpack-capture-retired': b"<?php class O {function __toString():string {global $x,$a;echo ($x==='changed' && $a===[])?'E':'N';echo 'T';return 'include_path';}} $x=new O;$a=['option'=>&$x];function later(){global $x,$a;echo 'A';$x='changed';$a=[];return [];} set_include_path('before');$f=ini_restore(...);$f->__invoke(...$a,...later());echo '|',set_include_path('end');",
    'restore-stringable-ordinary-after-empty': b"<?php class O {function __toString():string {echo 'T';return 'include_path';}} set_include_path('before');ini_restore(...[],option:new O);echo '|',set_include_path('end');",
    'restore-stringable-ordinary-before-empty': b"<?php class O {function __toString():string {echo 'T';return 'include_path';}} set_include_path('before');ini_restore(new O,...[]);echo '|',set_include_path('end');",
    'restore-stringable-nested-chdir': b"<?php class P {function __toString():string {echo 'P';return '__SUB__';}} class O {function __toString():string {echo chdir(new P)?'T':'F';return 'include_path';}} set_include_path('before');ini_restore(new O);echo include 'one.php';",
    'restore-stringable-inherited-case-throw': b'<?php\nclass P {\n    function __ToStRiNg():string {\n        throw new Exception("X");\n    }\n}\nclass O extends P {}\n$f=ini_restore(...);\n$f->__invoke(\n    ...[],\n    ...["option"=>new O],\n    ...[]\n);\n',
    'restore-stringable-strict': b"<?php declare(strict_types=1);class O {function __toString():string {echo 'T';return 'include_path';}} ini_restore(option:new O);",
    'restore-stringable-strict-first-class': b"<?php declare(strict_types=1);class O {function __toString():string {echo 'T';return 'include_path';}} $f=ini_restore(...);$f(option:new O);",
    'restore-stringable-strict-invoke': b"<?php declare(strict_types=1);class O {function __toString():string {echo 'T';return 'include_path';}} set_include_path('before');$f=ini_restore(...);$f->__invoke(option:new O);echo '|',set_include_path('end');",
    'restore-object-nonstringable': b'<?php class O {} ini_restore(new O);',
    'restore-object-named-unknown': b"<?php class O {function __toString():string {echo 'T';return 'include_path';}} function a(){echo 'A';return new O;} $f=ini_restore(...);$f->__invoke(directory:a());",
    'restore-object-unpack-duplicate': b"<?php class O {function __toString():string {echo 'T';return 'include_path';}} function a($s){echo $s;return new O;} ini_restore(...[a('A')],...['option'=>a('B')]);",
    'restore-object-unpack-count': b"<?php class O {function __toString():string {echo 'T';return 'include_path';}} function a($s){echo $s;return new O;} $f=ini_restore(...);$f->__invoke(...[a('A'),a('B')]);",
    'restore-scalar-empty-nul': b'<?php set_include_path(\'inner\');ini_restore(\'\');ini_restore("include_path\\0suffix");echo set_include_path(\'end\');',
    'restore-stringable-invalid-return-caught': b"<?php class O {function __toString():string {set_include_path('inner');return [];}} try{ini_restore(new O);}catch(TypeError $e){echo 'C|',set_include_path('end');}",
    'restore-object-unpack-empty-count': b'<?php ini_restore(...[]);',
    'restore-prefix-public-invoke-exact': b'<?php class I {function __invoke($option){return ini_restore(option:$option);}} class O {function __toString():string {ini_set(\'include_path\',"inner\\0tail");return \'include_path\';}} $i=new I;echo $i(new O)===null?\'N\':\'F\';echo \'|\',ini_set(\'include_path\',\'end\');',
    'restore-prefix-inherited-capture-miss': b'<?php class P {function __invoke($option){return ini_restore(option:$option);}} class I extends P {} class O {function __toString():string {ini_set(\'include_path\',"inner\\0tail");return "include_path\\0suffix";}} $i=new I;$f=$i(...);$i=0;echo $f(new O)===null?\'N\':\'F\';echo \'|\',ini_set(\'include_path\',\'end\');',
    'restore-prefix-leading-nul-name': b'<?php ini_set(\'include_path\',"a\\0b");ini_restore("\\0include_path");echo ini_set(\'include_path\',\'end\'),\'|\',set_include_path(\'last\');',
    'restore-prefix-owned-weak-nul-name': b'<?php declare(strict_types=1);class O {function __toString():string {echo \'T\';ini_set(\'include_path\',"inner\\0tail");return "include_path\\0suffix";}} $f=ini_restore(...);echo $f->__invoke(option:new O)===null?\'N\':\'F\';echo \'|\',ini_set(\'include_path\',\'end\');',
    'restore-callable-string-name-miss': b'<?php class RestoreDualMiss{public function __invoke(){$r=ini_restore($this);echo $r===null?"N":"X";echo ini_set("include_path","after");}public function __toString():string{echo "C";ini_set("include_path","inner\\0suffix");return "include_path\\0suffix";}}function acceptRestore(callable|string $value){$value();}acceptRestore(value:new RestoreDualMiss);',
    'independent-restore-callable-strict-owned-exact': b'<?php declare(strict_types=1); class IndependentRestoreCallable{function __invoke(){$restore=ini_restore(...);$result=$restore->__invoke(option:$this);echo $result===null?"N":"X";echo ini_set("include_path","after");}function __toString():string{echo "C";ini_set("include_path","inner\\0suffix");return "include_path";}}function independent_restore_accept(string|callable $value){$value();}independent_restore_accept(...["value"=>new IndependentRestoreCallable]);',
    'restore-argument-frame-name-miss': b'<?php class RestoreArgumentMiss{function __invoke($first,$second){$before=func_get_args();echo func_num_args(),":",$before[0],":",$before[1],"|";$result=ini_restore($this);echo $result===null?"N":"X";$after=func_get_args();echo func_num_args(),$after===$before?"S":"X","|";echo ini_set("include_path","after");}function __toString():string{echo "C",func_num_args(),func_get_args()===[]?"Z":"X";ini_set("include_path","inner\\0tail");return "include_path\\0suffix";}}function acceptRestoreArguments(callable|string $sink){$sink(second:"B",first:"A");}acceptRestoreArguments(sink:new RestoreArgumentMiss);',
    'independent-restore-argument-frame-owned-exact': b'<?php declare(strict_types=1); class IndependentRestoreArgumentExact{function __invoke($first,$second){$before=func_get_args();echo func_num_args(),":",$before[0],":",$before[1],"|";$restore=ini_restore(...);$result=$restore->__invoke(option:$this);echo $result===null?"N":"X";$after=func_get_args();echo func_num_args(),$after===$before?"S":"X","|";echo ini_set("include_path","after");}function __toString():string{echo "C",func_num_args(),func_get_args()===[]?"Z":"X";ini_set("include_path","inner\\0tail");return "include_path";}}function independent_restore_arguments(string|callable $sink){$sink(...["second"=>"B","first"=>"A"]);}independent_restore_arguments(...["sink"=>new IndependentRestoreArgumentExact]);',
    'ini-option-direct': b"<?php class O {function __toString():string {echo 'T';return 'include_path';}} echo ini_set(new O,'__SUB__');echo include 'one.php';",
    'ini-option-first-class': b"<?php class O {function __toString():string {echo 'T';return 'include_path';}} $f=ini_set(...);echo $f(new O,'__SUB__');echo include 'one.php';",
    'ini-option-reversed-named': b"<?php class O {function __toString():string {echo 'T';echo set_include_path('inner');return 'include_path';}} function a(){echo 'A';return 'outer';} echo ini_set(value:a(),option:new O),'|',set_include_path('end');",
    'ini-option-named-invoke': b"<?php class O {function __toString():string {echo 'T';return 'include_path';}} $f=ini_set(...);echo $f->__invoke(value:'__SUB__',option:new O);echo include 'one.php';",
    'ini-option-selection': b"<?php class O {function __toString():string {echo 'T';return 'include_path';}} function a(){global $f;echo 'A';$f='ini_restore';return new O;} $f='ini_set';echo $f(value:'__SUB__',option:a());echo include 'one.php';echo '|',$f;",
    'ini-option-captured-value': b"<?php class O {function __toString():string {global $v;$v='changed';echo set_include_path('inner');return 'include_path';}} $v='outer';echo ini_set(value:$v,option:new O),'|',$v,'|',set_include_path('end');",
    'ini-option-case': b"<?php class O {function __toString():string {set_include_path('inner');echo 'T';return 'INCLUDE_PATH';}} echo ini_set(new O,'outer')?'Y':'F';echo '|',set_include_path('end');",
    'ini-option-empty': b"<?php class O {function __toString():string {set_include_path('inner');echo 'T';return '';}} echo ini_set(new O,'outer')?'Y':'F';echo '|',set_include_path('end');",
    'ini-option-nul': b'<?php class O {function __toString():string {set_include_path(\'inner\');echo \'T\';return "include_path\\0suffix";}} echo ini_set(new O,\'outer\')?\'Y\':\'F\';echo \'|\',set_include_path(\'end\');',
    'ini-option-null-value': b"<?php class O {function __toString():string {set_include_path('inner');echo 'T';return 'include_path';}} echo ini_set(new O,null)?'Y':'F';echo '|',set_include_path('end');",
    'ini-option-leading-nul-value': b'<?php class O {function __toString():string {set_include_path(\'inner\');echo \'T\';return \'include_path\';}} echo ini_set(new O,"\\0later")?\'Y\':\'F\';echo \'|\',set_include_path(\'end\');',
    'ini-option-interior-nul-value': b'<?php class O {function __toString():string {echo \'T\';return \'include_path\';}} echo ini_set(new O,"a\\0b"),\'|\',ini_set(\'include_path\',\'end\');',
    'ini-option-scalar-set-old-prefix': b'<?php class O {function __toString():string {return \'include_path\';}} ini_set(new O,"a\\0b");echo set_include_path(\'end\');',
    'ini-option-stringable-set-old-prefix': b'<?php class O {function __toString():string {return \'include_path\';}} class P {function __toString():string {echo \'P\';return \'end\';}} ini_set(new O,"a\\0b");echo set_include_path(new P);',
    'ini-option-interior-nul-include': b'<?php class O {function __toString():string {echo \'T\';return \'include_path\';}} ini_set(new O,"__SUB__\\0ignored");echo include \'one.php\';',
    'ini-option-interior-nul-missing-require': b'<?php class O {function __toString():string {echo \'T\';return \'include_path\';}} ini_set(new O,"__SUB__\\0ignored");require \'missing-ini.php\';',
    'ini-option-strict-direct': b"<?php declare(strict_types=1);class O {function __toString():string {echo 'T';return 'include_path';}} ini_set(new O,'outer');",
    'ini-option-strict-first-class': b"<?php declare(strict_types=1);class O {function __toString():string {echo 'T';return 'include_path';}} $f=ini_set(...);$f(new O,'outer');",
    'ini-option-strict-invoke': b"<?php declare(strict_types=1);class O {function __toString():string {echo 'T';return 'include_path';}} $f=ini_set(...);echo $f->__invoke(value:'outer',option:new O);",
    'ini-option-inherited-throw': b"<?php\nclass P {\n function __ToStRiNg():string {\n  throw new Exception('X');\n }\n}\nclass O extends P {}\n$f=ini_set(...);\n$f->__invoke(\n value:'outer',\n option:new O\n);",
    'ini-option-nonstringable': b"<?php class O {} ini_set(new O,'outer');",
    'ini-option-object-value-error': b"<?php class O {function __toString():string {echo 'T';return 'include_path';}} class V {function __toString():string {echo 'V';return 'bad';}} ini_set(new O,new V);",
    'ini-option-array-value-invoke-error': b'<?php class O {function __toString():string {echo \'T\';return "include_path\\0suffix";}} $f=ini_set(...);$f->__invoke(value:[],option:new O);',
    'ini-option-scalar-array-invoke-error': b"<?php $f=ini_set(...);$f->__invoke(value:[],option:'');",
    'ini-option-unpack-capture-retired': b"<?php class O {function __toString():string {global $x,$v,$a;echo ($x==='changed' && $v==='changed' && $a===[])?'E':'N';echo 'T';return 'include_path';}} $x=new O;$v='outer';$a=['value'=>&$v,'option'=>&$x];function later(){global $x,$v,$a;echo 'A';$x='changed';$v='changed';$a=[];return [];} $f=ini_set(...);echo $f->__invoke(...$a,...later()),'|',set_include_path('end');",
    'ini-option-ordinary-after-empty': b"<?php class O {function __toString():string {echo 'T';return 'include_path';}} echo ini_set(...[],value:'outer',option:new O),'|',set_include_path('end');",
    'ini-option-ordinary-before-empty': b"<?php class O {function __toString():string {echo 'T';return 'include_path';}} echo ini_set(new O,'outer',...[]),'|',set_include_path('end');",
    'ini-option-unknown-before-callback': b"<?php class O {function __toString():string {echo 'T';return 'include_path';}} function a(){echo 'A';return new O;} ini_set(value:'outer',bad:a());",
    'ini-option-duplicate-before-callback': b"<?php class O {function __toString():string {echo 'T';return 'include_path';}} ini_set(...['option'=>new O],...['option'=>new O,'value'=>'outer']);",
    'ini-option-count-before-callback': b"<?php class O {function __toString():string {echo 'T';return 'include_path';}} ini_set(new O,'outer',new O);",
    'ini-option-invalid-return-caught': b"<?php class O {function __toString():string {set_include_path('inner');return [];} } try{ini_set(new O,'outer');}catch(TypeError $e){echo 'C|',set_include_path('end');}",
    'ini-option-nested-chdir': b"<?php class P {function __toString():string {echo 'P';return '__SUB__';}} class O {function __toString():string {echo chdir(new P)?'T':'F';return 'include_path';}} echo ini_set(new O,'.:');echo include 'one.php';",
    'ini-option-inherited-nested-throw': b"<?php\nclass P {\n function __ToStRiNg():string {$this->g();return 'include_path';}\n function g():void {throw new Exception('X');}\n}\nclass O extends P {}\n$f=ini_set(...);\n$f->__invoke(value:'outer',option:new O);\n",

    'ini-option-argument-frame-value-priority': b'<?php class IniArgumentPriority{function __invoke($first,$second){$before=func_get_args();echo func_num_args(),":",$before[0],":",$before[1],"|";try{ini_set(value:[],option:$this);}catch(TypeError $e){echo "E";}$after=func_get_args();echo func_num_args(),$after===$before?"S":"X","|";echo ini_set("include_path","after");}function __toString():string{echo "C",func_num_args(),func_get_args()===[]?"Z":"X";ini_set("include_path","inner\\0tail");return "include_path\\0missing";}}(new IniArgumentPriority)(second:"B",first:"A");',

    'ini-option-scalar-weak-misses': b'<?php ini_set("include_path","before\\0tail");echo ini_set(value:"outer",option:false)===false?"F":"X";echo ini_set(option:true,value:12)===false?"F":"X";echo ini_set(option:12,value:1.5)===false?"F":"X";echo ini_set(option:1.5,value:true)===false?"F":"X";echo "|",ini_set("include_path","after");',
    'ini-option-null-weak-suppressed': b'<?php ini_set("include_path","before\\0tail");echo @ini_set(option:null,value:12)===false?"F":"X";echo "|",ini_set("include_path","after");',
    'ini-option-null-owned-weak-suppressed': b'<?php declare(strict_types=1);ini_set("include_path","before\\0tail");$f=ini_set(...);echo @$f->__invoke(option:null,value:12)===false?"F":"X";echo "|",ini_set("include_path","after");',
    'ini-option-scalar-strict-priority': b'<?php declare(strict_types=1);try{ini_set(value:[],option:false);}catch(TypeError $e){echo $e->getMessage()===\'ini_set(): Argument #1 ($option) must be of type string, false given\'?"1":"X";}try{ini_set(value:[],option:12);}catch(TypeError $e){echo $e->getMessage()===\'ini_set(): Argument #1 ($option) must be of type string, int given\'?"1":"X";}try{ini_set(value:[],option:1.5);}catch(TypeError $e){echo $e->getMessage()===\'ini_set(): Argument #1 ($option) must be of type string, float given\'?"1":"X";}',
    'ini-option-scalar-weak-value-priority': b'<?php try{ini_set(value:[],option:false);}catch(TypeError $e){echo $e->getMessage()===\'ini_set(): Argument #2 ($value) must be of type string|int|float|bool|null\'?"2":"X";}',
    'ini-option-array-priority': b'<?php try{ini_set(value:[],option:[]);}catch(TypeError $e){echo $e->getMessage()===\'ini_set(): Argument #1 ($option) must be of type string, array given\'?"1":"X";}',
    'ini-option-null-strict-priority': b'<?php declare(strict_types=1);try{ini_set(value:[],option:null);}catch(TypeError $e){echo $e->getMessage()===\'ini_set(): Argument #1 ($option) must be of type string, null given\'?"1":"X";}',
    'ini-option-scalar-owned-value-priority': b'<?php declare(strict_types=1);$f=ini_set(...);try{$f->__invoke(value:[],option:false);}catch(TypeError $e){echo $e->getMessage()===\'ini_set(): Argument #2 ($value) must be of type string|int|float|bool|null\'?"2":"X";}',

    'ini-option-null-weak-diagnostic-priority': b'<?php ini_set("include_path","before\\0tail");try{ini_set(value:[],option:null);}catch(TypeError $e){echo $e->getMessage()===\'ini_set(): Argument #2 ($value) must be of type string|int|float|bool|null\'?"2":"X";}echo "|",ini_set("include_path","after");',

    'ini-property-nul-option-array-priority': b'<?php class IniProperty{public static string $p="old";}class IniPropertyOption{function __toString():string{echo "O",func_num_args(),func_get_args()===[]?"Z":"X";ini_set("include_path","inner\\0tail");return "include_path\\0missing";}}class IniPropertyValue{function __toString():string{echo "P",func_num_args(),func_get_args()===[]?"Z":"X";try{ini_set(value:[],option:new IniPropertyOption);}catch(TypeError $e){echo "E";}return "s\\0typed";}}function ini_property($value){$before=func_get_args();echo func_num_args();IniProperty::$p=$value;echo func_num_args(),func_get_args()===$before?"S":"X";}ini_property(new IniPropertyValue);echo "|",ini_set("include_path","after"),"|",IniProperty::$p;',
    'ini-option-captured-unpack-array-priority': b'<?php class IniCapturedArrayOption{function __toString():string{global $pack;$pack=[];echo "C";ini_set("include_path","inner\\0tail");return "include_path\\0missing";}}$pack=["value"=>[],"option"=>new IniCapturedArrayOption];try{ini_set(...$pack);}catch(TypeError $e){echo "E";}echo $pack===[]?"R":"X";echo ini_set("include_path","after");',
    'independent-ini-property-owned-late-raw': b'<?php class IndependentIniProperty{public static string $p="old";}class IndependentIniOption{function __toString():string{echo "O",func_num_args(),func_get_args()===[]?"Z":"X";ini_set("include_path","inner\\0tail");return "include_path";}}class IndependentIniValue{function __toString():string{echo "P",func_num_args(),func_get_args()===[]?"Z":"X";$f=ini_set(...);echo $f->__invoke(value:"outer",option:new IndependentIniOption);return "s\\0typed";}}function independent_ini_property($value){echo func_num_args();IndependentIniProperty::$p=$value;echo func_num_args();}independent_ini_property(new IndependentIniValue);echo "|",ini_set("include_path","end"),"|",IndependentIniProperty::$p;',
    'ini-readback-default': b"<?php echo get_include_path(),'|',ini_get(option:'include_path');",
    'ini-readback-raw-set-prefix': b'<?php ini_set(\'include_path\',"a\\0b");echo get_include_path(),\'|\',ini_get(\'include_path\'),\'|\',set_include_path(\'next\'),\'|\',get_include_path();',
    'ini-readback-restore-exact-and-miss': b'<?php ini_set(\'include_path\',"before\\0tail");echo ini_restore("include_path\\0missing")===null?\'N\':\'X\',get_include_path(),\'|\';echo ini_restore(\'include_path\')===null?\'N\':\'X\',ini_get(\'include_path\');',
    'ini-readback-leading-nul-preserves-raw': b'<?php ini_set(\'include_path\',"a\\0b");echo ini_set(\'include_path\',"\\0no")===false?\'F\':\'X\',\'|\',get_include_path(),\'|\',ini_get(\'include_path\');',
    'ini-readback-full-name-misses': b'<?php ini_set(\'include_path\',"a\\0b");echo ini_get(\'\')===false?\'F\':\'X\',ini_get(\'INCLUDE_PATH\')===false?\'F\':\'X\',ini_get("include_path\\0suffix")===false?\'F\':\'X\',\'|\',get_include_path();',
    'ini-readback-selected-before-argument': b'<?php function arg(){global $f;$f=\'ini_restore\';echo \'A\';return \'include_path\';}ini_set(\'include_path\',"before\\0tail");$f=\'ini_get\';echo $f(option:arg()),\'|\',get_include_path();',
    'ini-readback-captured-retired-unpack': b'<?php declare(strict_types=1);class O{function __toString():string{global $a,$x;echo ($a===[] && $x===0)?\'R\':\'X\';echo \'C\';ini_set(\'include_path\',"inner\\0tail");return \'include_path\';}}$x=new O;$a=[\'option\'=>&$x];function later(){global $a,$x;$a=[];$x=0;echo \'A\';return [];}$f=ini_get(...);echo $f->__invoke(...$a,...later()),\'|\',get_include_path();',
    'ini-readback-owned-zero-arity': b'<?php declare(strict_types=1);ini_set(\'include_path\',"a\\0b");$g=get_include_path(...);echo $g->__invoke(),\'|\',$g();',
    'ini-readback-stringable-live-raw': b'<?php class O{function __toString():string{echo \'C\';ini_set(\'include_path\',"inner\\0tail");return \'include_path\';}}ini_set(\'include_path\',"before\\0tail");echo ini_get(option:new O),\'|\',get_include_path();',
    'ini-readback-strict-stringable-refusal': b'<?php declare(strict_types=1);class O{function __toString():string{echo \'X\';ini_set(\'include_path\',\'wrong\');return \'include_path\';}}ini_set(\'include_path\',"before\\0tail");try{ini_get(new O);}catch(TypeError $e){echo $e->getMessage()===\'ini_get(): Argument #1 ($option) must be of type string, O given\'?\'T\':\'X\';}echo \'|\',get_include_path();',
    'ini-readback-weak-primitive-options': b'<?php ini_set(\'include_path\',"before\\0tail");foreach([false,true,7,1.5] as $x){echo ini_get($x)===false?\'F\':\'X\';echo ini_restore($x)===null?\'N\':\'X\';}echo \'|\',get_include_path();',
    'ini-readback-strict-primitive-get': b'<?php declare(strict_types=1);ini_set(\'include_path\',"before\\0tail");try{ini_get(false);}catch(TypeError $e){echo $e->getMessage()===\'ini_get(): Argument #1 ($option) must be of type string, false given\'?\'F\':\'X\';}try{ini_get(null);}catch(TypeError $e){echo $e->getMessage()===\'ini_get(): Argument #1 ($option) must be of type string, null given\'?\'N\':\'X\';}try{ini_get(7);}catch(TypeError $e){echo $e->getMessage()===\'ini_get(): Argument #1 ($option) must be of type string, int given\'?\'I\':\'X\';}echo \'|\',get_include_path();',
    'ini-readback-strict-primitive-restore': b'<?php declare(strict_types=1);ini_set(\'include_path\',"before\\0tail");try{ini_restore(false);}catch(TypeError $e){echo $e->getMessage()===\'ini_restore(): Argument #1 ($option) must be of type string, false given\'?\'F\':\'X\';}try{ini_restore(null);}catch(TypeError $e){echo $e->getMessage()===\'ini_restore(): Argument #1 ($option) must be of type string, null given\'?\'N\':\'X\';}try{ini_restore(7);}catch(TypeError $e){echo $e->getMessage()===\'ini_restore(): Argument #1 ($option) must be of type string, int given\'?\'I\':\'X\';}echo \'|\',get_include_path();',
    'ini-readback-null-get-diagnostic': b'<?php ini_set(\'include_path\',"before\\0tail");echo ini_get(null)===false?\'F\':\'X\',\'|\',get_include_path();',
    'ini-readback-null-restore-diagnostic': b'<?php ini_set(\'include_path\',"before\\0tail");echo ini_restore(null)===null?\'N\':\'X\',\'|\',get_include_path();',
    'ini-readback-zero-arity-side-effect': b"<?php class O{function __toString():string{echo 'BAD';return 'include_path';}}function arg(){echo 'A';return new O;}try{get_include_path(arg());}catch(ArgumentCountError $e){echo $e->getMessage()==='get_include_path() expects exactly 0 arguments, 1 given'?'C':'X';}echo '|',get_include_path();",
    'ini-readback-get-arity-side-effects': b"<?php class O{function __toString():string{echo 'BAD';return 'include_path';}}function arg($s){echo $s;return new O;}try{ini_get();}catch(ArgumentCountError $e){echo $e->getMessage()==='ini_get() expects exactly 1 argument, 0 given'?'Z':'X';}try{ini_get(arg('A'),arg('B'));}catch(ArgumentCountError $e){echo $e->getMessage()==='ini_get() expects exactly 1 argument, 2 given'?'E':'X';}echo '|',get_include_path();",
    'ini-readback-named-binding-errors': b"<?php function arg(){echo 'A';return 'include_path';}try{ini_get(bad:arg());}catch(Error $e){echo $e->getMessage()==='Unknown named parameter $bad'?'U':'X';}try{ini_get(...['option'=>'include_path'],option:arg());}catch(Error $e){echo $e->getMessage()==='Named parameter $option overwrites previous argument'?'D':'X';}echo '|',get_include_path();",
    'ini-readback-caller-argument-frame': b'<?php class O{function __toString():string{echo \'C\',func_num_args(),func_get_args()===[]?\'Z\':\'X\';ini_set(\'include_path\',"inner\\0tail");return \'include_path\';}}class I{function __invoke($a,$b){echo func_num_args(),\':\',$a,\':\',$b,\'|\';echo ini_get(new O);echo func_num_args(),func_get_args()===[$a,$b]?\'S\':\'X\';}}(new I)(b:\'B\',a:\'A\');',
    'ini-readback-callback-throw-keeps-raw': b'<?php class O{function __toString():string{echo \'C\';ini_set(\'include_path\',"inner\\0tail");throw new Exception(\'stop\');}}ini_set(\'include_path\',\'before\');try{ini_get(new O);}catch(Exception $e){echo $e->getMessage()===\'stop\'?\'T\':\'X\';}echo \'|\',get_include_path();',
    'ini-readback-array-and-object-refusal': b'<?php class O{}ini_set(\'include_path\',"before\\0tail");try{ini_get([]);}catch(TypeError $e){echo $e->getMessage()===\'ini_get(): Argument #1 ($option) must be of type string, array given\'?\'A\':\'X\';}try{ini_get(new O);}catch(TypeError $e){echo $e->getMessage()===\'ini_get(): Argument #1 ($option) must be of type string, O given\'?\'O\':\'X\';}echo \'|\',get_include_path();',
    'ini-readback-first-class-named': b'<?php ini_set(\'include_path\',"a\\0b");$g=ini_get(...);echo $g(option:\'include_path\'),\'|\',$g->__invoke(option:\'include_path\'),\'|\',get_include_path();',
    'ini-readback-array-inherited-raw': b'<?php ini_set(\'include_path\',"before\\0tail");class Option{public function __toString():string{echo \'C\',func_num_args(),func_get_args()===[]?\'Z\':\'X\';ini_set(\'include_path\',"inner\\0tail");return \'include_path\';}}class Owner{public function read($first,$second):void{echo __CLASS__,\'/\',static::class,\'|\';$saved=func_get_args();echo func_num_args(),\':\',$saved[0],\':\',$saved[1],\'|\';echo ini_get(option:new Option);echo func_num_args()===2&&func_get_args()===$saved?\'S\':\'X\';echo \'|\',get_include_path();}}class Child extends Owner{}$callable=[new Child,\'read\'];$callable(second:\'B\',first:\'A\');',
    'ini-readback-independent-ini-getter-callback-full-raw': b'<?php ini_set("include_path","before\\0tail");class IndependentIniRead{function __toString():string{echo "C",func_num_args(),func_get_args()===[]?"Z":"X";ini_set("include_path","inner\\0suffix");return "include_path";}}echo get_include_path(),"|",ini_get(option:new IndependentIniRead),"|",get_include_path();',
    'ini-readback-independent-ini-getter-owned-nul-name': b'<?php declare(strict_types=1);class IndependentIniReadMiss{function __toString():string{echo "C",func_num_args(),func_get_args()===[]?"Z":"X";ini_set("include_path","inner\\0suffix");return "include_path\\0missing";}}$f=ini_get(...);$result=$f->__invoke(option:new IndependentIniReadMiss);echo $result===false?"F":"X";echo "|",get_include_path();',
    'ini-readback-independent-restore-primitive-owned-priority': b'<?php declare(strict_types=1);ini_set("include_path","before\\0tail");try{ini_restore(option:false);}catch(TypeError $e){echo "T";}$f=ini_restore(...);echo @$f->__invoke(option:null)===null?"N":"X";echo @$f->__invoke(option:false)===null?"B":"X";echo "|",get_include_path();',
    'ini-readback-independent-ini-readback-array-capture-owned': b'<?php\ndeclare(strict_types=1);\nini_set(\'include_path\', "before\\0tail");\nclass Option {\n    public function __toString(): string {\n        echo \'C\', func_num_args();\n        echo func_get_args() === [] ? \'Z\' : \'X\';\n        ini_set(\'include_path\', "inner\\0suffix");\n        return \'include_path\';\n    }\n}\nclass Owner {\n    public function run($first, $second): void {\n        echo __CLASS__, \'/\', static::class, \'|\';\n        $saved = func_get_args();\n        echo func_num_args(), \':\', $saved[0], \':\', $saved[1], \'|\';\n        $read = ini_get(...);\n        echo $read->__invoke(option: new Option);\n        echo func_num_args() === 2 && func_get_args() === $saved ? \'S\' : \'X\';\n        $restore = ini_restore(...);\n        echo $restore->__invoke(option: false) === null ? \'|N\' : \'|X\';\n        echo get_include_path();\n    }\n}\nclass Child extends Owner {}\n$cb = [new Child, \'run\'];\n$f = $cb(...);\n$g = clone $f;\n$cb[0] = 0;\nunset($f, $cb);\n$g(...[\'second\' => \'B\', \'first\' => \'A\']);\n',
    'pipe-config-warning-normal-held-left': b'<?php\nerror_reporting(0);\nini_set(\'include_path\', "before\\0tail");\nclass PipeWarningSet {\n    function __toString(): string {\n        global $left;\n        echo \'C\', func_num_args(), func_get_args() === [] ? \'Z\' : \'X\', $left === null ? \'N\' : \'X\';\n        $x = null;\n        $a =& $x;\n        set_error_handler(function($severity, $message, $file, $line) use (&$x) {\n            echo \'H\', func_num_args();\n            $x = 9;\n            ini_set(\'include_path\', "inner\\0tail");\n            return 0;\n        }, 2);\n        $result = $a === $missing;\n        echo $result ? \'1\' : \'0\', func_num_args() === 0 && func_get_args() === [] ? \'S\' : \'X\';\n        restore_error_handler();\n        return \'after\';\n    }\n}\nfunction chooseWarningSetter() {\n    global $left;\n    $left = null;\n    echo \'R\';\n    return set_include_path(...);\n}\n$left = new PipeWarningSet;\n$old = $left |> chooseWarningSetter();\necho \'|\', $old, \'|\', get_include_path();\n',
    'independent-config-pipe-warning-throw-held-left': b'<?php\nerror_reporting(0);\nini_set(\'include_path\', "before\\0tail");\nclass PipeWarningThrow {\n    function __toString(): string {\n        global $left;\n        echo \'C\', func_num_args(), func_get_args() === [] ? \'Z\' : \'X\', $left === null ? \'N\' : \'X\';\n        $x = null;\n        $a =& $x;\n        set_error_handler(function($severity, $message, $file, $line) use (&$x) {\n            echo \'H\', func_num_args();\n            $x = 9;\n            ini_set(\'include_path\', "throw\\0tail");\n            throw new Error(\'warning\');\n        }, 2);\n        $result = $a === $missing;\n        echo \'BAD\';\n        return \'include_path\';\n    }\n}\nfunction chooseWarningRestore() {\n    global $left;\n    $left = null;\n    echo \'R\';\n    return ini_restore(...);\n}\n$left = new PipeWarningThrow;\ntry {\n    $left |> chooseWarningRestore();\n} catch (Error $e) {\n    echo \'T\';\n}\nrestore_error_handler();\necho \'|\', get_include_path();\n',
    'pipe-config-chdir-dynamic-live-cwd': b'<?php\nini_set(\'include_path\', ".:\\0tail");\nclass PipeDirectoryDynamic {\n    function __toString(): string {\n        global $left;\n        echo \'C\', func_num_args(), func_get_args() === [] ? \'Z\' : \'X\', $left === null ? \'N\' : \'X\';\n        chdir(\'sub\');\n        return \'..\';\n    }\n}\nfunction chooseDirectoryName() {\n    global $left;\n    $left = null;\n    echo \'R\';\n    return \'chdir\';\n}\n$left = new PipeDirectoryDynamic;\n$result =\n    $left\n    |>\n    chooseDirectoryName();\necho $result ? \'T\' : \'F\';\ninclude \'one.php\';\necho \'|\', get_include_path();\n',
    'pipe-config-chdir-nul-refusal': b'<?php\nini_set(\'include_path\', ".:\\0tail");\nclass PipeDirectoryNul {\n    function __toString(): string {\n        echo \'C\';\n        chdir(\'sub\');\n        ini_set(\'include_path\', ".:\\0changed");\n        return "\\0invalid";\n    }\n}\ntry {\n    new PipeDirectoryNul |> chdir(...);\n} catch (ValueError $e) {\n    echo $e->getMessage() === \'chdir(): Argument #1 ($directory) must not contain any null bytes\' ? \'V\' : \'X\';\n}\ninclude \'one.php\';\necho \'|\', get_include_path();\n',
    'pipe-config-chdir-provider-false': b'<?php\nini_set(\'include_path\', ".:\\0tail");\nclass PipeDirectoryMissing {\n    function __toString(): string {\n        echo \'C\';\n        chdir(\'sub\');\n        return \'missing\';\n    }\n}\n$result = @(new PipeDirectoryMissing |> chdir(...));\necho $result === false ? \'F\' : \'X\';\ninclude \'one.php\';\necho \'|\', get_include_path();\n',
    'pipe-config-chdir-strict-refusal': b'<?php\ndeclare(strict_types=1);\nini_set(\'include_path\', ".:\\0tail");\nclass PipeDirectoryStrict {\n    function __toString(): string {\n        echo \'BAD\';\n        chdir(\'sub\');\n        return \'..\';\n    }\n}\ntry {\n    new PipeDirectoryStrict |> chdir(...);\n} catch (TypeError $e) {\n    echo $e->getMessage() === \'chdir(): Argument #1 ($directory) must be of type string, PipeDirectoryStrict given\' ? \'R\' : \'X\';\n}\ninclude \'one.php\';\necho \'|\', get_include_path();\n',
    'pipe-config-chdir-throw-keeps-cwd': b'<?php\nini_set(\'include_path\', ".:\\0tail");\nclass PipeDirectoryThrow {\n    function __toString(): string {\n        echo \'C\';\n        chdir(\'sub\');\n        ini_set(\'include_path\', ".:\\0throw");\n        throw new Exception(\'directory\');\n    }\n}\ntry {\n    new PipeDirectoryThrow |> chdir(...);\n} catch (Exception $e) {\n    echo $e->getMessage() === \'directory\' ? \'T\' : \'X\';\n}\ninclude \'one.php\';\necho \'|\', get_include_path();\n',
    'independent-config-pipe-chdir-held-cwd': b'<?php\nini_set(\'include_path\', ".:\\0tail");\nclass PipeDirectoryHeld {\n    function __toString(): string {\n        global $left;\n        echo \'C\', func_num_args(), func_get_args() === [] ? \'Z\' : \'X\', $left === null ? \'N\' : \'X\';\n        chdir(\'sub\');\n        return \'..\';\n    }\n}\nfunction chooseDirectoryTarget() {\n    global $left;\n    $left = null;\n    echo \'R\';\n    return chdir(...);\n}\n$left = new PipeDirectoryHeld;\n$result = $left |> chooseDirectoryTarget();\necho $result ? \'T\' : \'F\';\ninclude \'one.php\';\necho \'|\', get_include_path();\n',
    'chdir-warning-normal-held-cwd': b'<?php\nini_set(\'include_path\', ".:\\0before");\nclass DirectoryWarningNormal {\n    function __toString(): string {\n        global $left;\n        echo \'C\', func_num_args(), func_get_args() === [] ? \'Z\' : \'X\', $left === null ? \'N\' : \'X\';\n        chdir(\'sub\');\n        return \'missing\';\n    }\n}\nfunction chooseWarningDirectory() {\n    global $left;\n    $left = null;\n    echo \'R\';\n    return chdir(...);\n}\nfunction normalDirectoryCaller($first, $second) {\n    global $left;\n    $saved = func_get_args();\n    echo func_num_args(), \':\', $saved[0], \':\', $saved[1], \'|\';\n    set_error_handler(function($level, $message, $file, $line) {\n        echo \'H\', func_num_args(), $level === 2 && $message === \'chdir(): No such file or directory (errno 2)\' && $file === __FILE__ && $line > 0 ? \'W\' : \'X\';\n        chdir(\'..\');\n        ini_set(\'include_path\', ".:\\0normal");\n        return 0;\n    }, 2);\n    $left = new DirectoryWarningNormal;\n    $result =\n        $left\n        |>\n        chooseWarningDirectory();\n    echo $result === false ? \'F\' : \'X\';\n    echo func_num_args() === 2 && func_get_args() === $saved ? \'S\' : \'X\';\n    restore_error_handler();\n}\nnormalDirectoryCaller(second:\'B\', first:\'A\');\ninclude \'one.php\';\necho \'|\', get_include_path();\n',
    'chdir-warning-false-fallback': b'<?php\nini_set(\'include_path\', ".:\\0before");\nfunction fallbackDirectoryCaller($first, $second) {\n    $saved = func_get_args();\n    echo func_num_args(), \':\', $saved[0], \':\', $saved[1], \'|\';\n    set_error_handler(function($level, $message, $file, $line) {\n        echo \'H\', func_num_args(), $level === 2 && $message === \'chdir(): No such file or directory (errno 2)\' && $file === __FILE__ && $line > 0 ? \'W\' : \'X\';\n        chdir(\'sub\');\n        ini_set(\'include_path\', ".:\\0fallback");\n        return false;\n    }, 2);\n    $result = chdir(\'missing\');\n    echo $result === false ? \'F\' : \'X\';\n    echo func_num_args() === 2 && func_get_args() === $saved ? \'S\' : \'X\';\n    restore_error_handler();\n}\nfallbackDirectoryCaller(second:\'B\', first:\'A\');\ninclude \'one.php\';\necho \'|\', get_include_path();\n',
    'independent-chdir-warning-owned-throw': b'<?php\ndeclare(strict_types=1);\nini_set(\'include_path\', ".:\\0before");\nfunction directoryWarning(string $level, $message, $file, $line) {\n    $args = func_get_args();\n    echo \'H\', func_num_args(), $level === \'2\' ? \'W\' : \'X\';\n    echo $args === [$level, $message, $file, $line]\n        && $message === \'chdir(): No such file or directory (errno 2)\'\n        && $file === __FILE__ && $line > 0 ? \'Z\' : \'X\';\n    chdir(\'..\');\n    ini_set(\'include_path\', ".:\\0throw");\n    throw new Exception(\'directory-handler\');\n}\nclass DirectoryWarningOperand {\n    function __toString(): string {\n        global $left;\n        echo \'C\', func_num_args(), func_get_args() === [] ? \'Z\' : \'X\', $left === null ? \'N\' : \'X\';\n        chdir(\'sub\');\n        return \'missing\';\n    }\n}\nfunction runFailedDirectory($left) {\n    $before = func_get_args();\n    echo \'P\', func_num_args();\n    $internal = chdir(...);\n    try {\n        $internal->__invoke($left);\n        echo \'BAD\';\n    } catch (Exception $e) {\n        $trace = $e->getTrace();\n        echo $e->getMessage() === \'directory-handler\' ? \'T\' : \'X\';\n        echo $trace[1][\'function\'] === \'chdir\' && $trace[1][\'args\'] === [\'missing\'] ? \'A\' : \'X\';\n        echo $trace[2][\'class\'] === \'Closure\' && $trace[2][\'function\'] === \'__invoke\'\n            && $trace[2][\'args\'] === [$left] ? \'O\' : \'X\';\n    }\n    echo func_num_args(), $before === func_get_args() ? \'S\' : \'X\';\n}\nfunction chooseFailedDirectoryTarget() {\n    global $left;\n    $left = null;\n    echo \'R\';\n    return runFailedDirectory(...);\n}\nset_error_handler(\'directoryWarning\');\n$left = new DirectoryWarningOperand;\n$left |> chooseFailedDirectoryTarget();\ninclude \'one.php\';\necho \'|\', get_include_path();\n',
    'chdir-warning-normal-minimal': b'<?php\nini_set(\'include_path\', ".:\\0before");\nclass DirectoryWarningMinimal {\n    function __toString(): string {\n        global $left;\n        echo $left === null ? \'R\' : \'X\';\n        chdir(\'sub\');\n        return \'missing\';\n    }\n}\nfunction chooseMinimalDirectory() {\n    global $left;\n    $left = null;\n    return chdir(...);\n}\nfunction minimalDirectoryCaller($first, $second) {\n    global $left;\n    $saved = func_get_args();\n    set_error_handler(function($level, $message, $file, $line) {\n        echo \'H\';\n        chdir(\'..\');\n        ini_set(\'include_path\', ".:\\0normal");\n        return 0;\n    }, 2);\n    $left = new DirectoryWarningMinimal;\n    $result =\n        $left\n        |>\n        chooseMinimalDirectory();\n    echo $result === false ? \'F\' : \'X\';\n    echo func_num_args() === 2 && func_get_args() === $saved ? \'S\' : \'X\';\n    restore_error_handler();\n}\nminimalDirectoryCaller(second:\'B\', first:\'A\');\ninclude \'one.php\';\necho \'|\', get_include_path();\n',
    'chdir-warning-method-array-normal': b'<?php\nini_set(\'include_path\', ".:\\0before");\nclass DirectoryHandlerOwner {\n    static function warning(string $level, $message, $file, $line) {\n        echo \'H\', __CLASS__ === \'DirectoryHandlerOwner\' ? \'O\' : \'X\';\n        echo static::class === \'DirectoryHandlerChild\' ? \'C\' : \'X\';\n        echo func_num_args(), $level === \'2\' ? \'W\' : \'X\';\n        chdir(\'sub\');\n        ini_set(\'include_path\', ".:\\0method");\n        return 0;\n    }\n}\nclass DirectoryHandlerChild extends DirectoryHandlerOwner {}\nclass DirectoryHandlerOperand {\n    function __toString(): string {\n        global $left;\n        echo \'C\', func_num_args(), func_get_args() === [] ? \'Z\' : \'X\';\n        echo $left === null ? \'N\' : \'X\';\n        return \'missing\';\n    }\n}\nfunction chooseMethodDirectory() {\n    global $left;\n    $left = null;\n    echo \'R\';\n    return chdir(...);\n}\nfunction methodDirectoryCaller($first, $second) {\n    global $left;\n    $saved = func_get_args();\n    set_error_handler([new DirectoryHandlerChild, \'warning\'], 2);\n    $left = new DirectoryHandlerOperand;\n    $result =\n        $left\n        |>\n        chooseMethodDirectory();\n    echo $result === false ? \'F\' : \'X\';\n    echo func_num_args() === 2 && func_get_args() === $saved ? \'S\' : \'X\';\n    restore_error_handler();\n}\nmethodDirectoryCaller(second: \'B\', first: \'A\');\ninclude \'one.php\';\necho \'|\', get_include_path();\n',
    'independent-chdir-warning-string-handler-throw': b'<?php\ndeclare(strict_types=1);\nini_set(\'include_path\', ".:\\0before");\nclass WarningOwner {\n    public static function warning(string $level, $message, $file, $line) {\n        echo \'H\', func_num_args(), $level === \'2\' ? \'W\' : \'X\';\n        echo __CLASS__ === \'WarningOwner\' && static::class === \'WarningChild\' ? \'K\' : \'X\';\n        chdir(\'..\');\n        ini_set(\'include_path\', ".:\\0throw");\n        throw new Exception(\'directory-handler\');\n    }\n}\nclass WarningChild extends WarningOwner {}\nclass DirectoryWarningOperand {\n    function __toString(): string {\n        global $left;\n        echo \'C\', func_num_args(), $left === null ? \'N\' : \'X\';\n        chdir(\'sub\');\n        return \'missing\';\n    }\n}\nfunction runFailedDirectory($left) {\n    $before = func_get_args();\n    $internal = chdir(...);\n    try { $internal->__invoke($left); echo \'BAD\'; }\n    catch (Exception $e) {\n        $trace = $e->getTrace();\n        echo $e->getMessage() === \'directory-handler\' ? \'T\' : \'X\';\n        echo $trace[1][\'function\'] === \'chdir\' && $trace[1][\'args\'] === [\'missing\'] ? \'A\' : \'X\';\n        echo $trace[2][\'class\'] === \'Closure\' && $trace[2][\'function\'] === \'__invoke\'\n            && $trace[2][\'args\'] === [$left] ? \'O\' : \'X\';\n    }\n    echo func_num_args(), $before === func_get_args() ? \'S\' : \'X\';\n}\nfunction chooseFailedDirectoryTarget() {\n    global $left;\n    $left = null;\n    echo \'R\';\n    return runFailedDirectory(...);\n}\nset_error_handler(\'WarningChild::warning\');\n$left = new DirectoryWarningOperand;\n$left\n    |>\n    chooseFailedDirectoryTarget();\ninclude \'one.php\';\necho \'|\', get_include_path();\n',
    'independent-chdir-warning-string-handler-throw-result': b'<?php\ndeclare(strict_types=1);\nini_set(\'include_path\', ".:\\0before");\nclass WarningOwner {\n    public static function warning(string $level, $message, $file, $line) {\n        echo \'H\', func_num_args(), $level === \'2\' ? \'W\' : \'X\';\n        echo __CLASS__ === \'WarningOwner\' && static::class === \'WarningChild\' ? \'K\' : \'X\';\n        chdir(\'..\');\n        ini_set(\'include_path\', ".:\\0throw");\n        throw new Exception(\'directory-handler\');\n    }\n}\nclass WarningChild extends WarningOwner {}\nclass DirectoryWarningOperand {\n    function __toString(): string {\n        global $left;\n        echo \'C\', func_num_args(), $left === null ? \'N\' : \'X\';\n        chdir(\'sub\');\n        return \'missing\';\n    }\n}\nfunction runFailedDirectory($left) {\n    $before = func_get_args();\n    $internal = chdir(...);\n    try { $internal->__invoke($left); echo \'BAD\'; }\n    catch (Exception $e) {\n        echo func_num_args(), $before === func_get_args() ? \'S\' : \'X\';\n        return [$e, $left];\n    }\n}\nfunction chooseFailedDirectoryTarget() {\n    global $left;\n    $left = null;\n    echo \'R\';\n    return runFailedDirectory(...);\n}\nset_error_handler(\'WarningChild::warning\');\n$left = new DirectoryWarningOperand;\n$pair =\n    $left\n    |>\n    chooseFailedDirectoryTarget();\n$e = $pair[0];\n$original = $pair[1];\n$trace = $e->getTrace();\necho $e->getMessage() === \'directory-handler\' ? \'T\' : \'X\';\necho $trace[1][\'function\'] === \'chdir\' && $trace[1][\'args\'] === [\'missing\'] ? \'A\' : \'X\';\necho $trace[2][\'class\'] === \'Closure\' && $trace[2][\'function\'] === \'__invoke\'\n    && $trace[2][\'args\'] === [$original] ? \'O\' : \'X\';\ninclude \'one.php\';\necho \'|\', get_include_path();\n',
}


def b64(data):
    return base64.b64encode(data).decode()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def vendor_identity():
    tree = subprocess.check_output(['git', 'rev-parse', 'HEAD:vendor/php-parser-source'],
                                   cwd=ROOT, text=True).strip()
    dirty = subprocess.check_output(['git', 'status', '--porcelain',
                                     '--untracked-files=all', '--', 'vendor/php-parser-source'],
                                    cwd=ROOT, text=True)
    assert not dirty, 'vendored parser changed during campaign'
    return tree


def main():
    out = Path(tempfile.mkdtemp(prefix='include-mutable-', dir=ROOT / '.tools'))
    print(out, flush=True)
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    watched = [*modules, ROOT / 'spec/semantics/modules.json', ROOT / 'bin/php-semantics',
               ROOT / '_build/default/adapter/main.exe', ROOT / 'frontend/worker.php',
               ROOT / 'frontend/FileLexer.php', ROOT / 'frontend/EvalLexer.php',
               ROOT / 'frontend/autoload.php', ROOT / 'frontend/encoding-literal.php',
               ROOT / 'frontend/target.php', ROOT / 'frontend/SourcePrinter.php',
               ROOT / 'frontend/encoding.php', ROOT / 'frontend/wire.php',
               ROOT / 'spec/schema.json', ROOT / 'spec/php.watsup', ROOT / 'adapter/main.ml',
               ROOT / 'frontend/wire.py', ROOT / '.tools/php/bin/php',
               ROOT / '.tools/php-file.so', PROFILE, Path(__file__)]
    before = {str(path.relative_to(ROOT)): digest(path) for path in watched}
    vendor_before = vendor_identity()
    profile = json.loads(PROFILE.read_text())
    flags = [piece for key, value in profile.items() for piece in ('-d', key + '=' + value)]
    environment = {**os.environ, 'LC_ALL': 'C'}
    default_cwd = os.fsencode(ROOT.resolve())
    records = []
    for name, template in CASES.items():
        directory = out / name
        directory.mkdir()
        pipe_chdir = name.startswith(('pipe-config-chdir-', 'chdir-warning-')) or name in ('independent-config-pipe-chdir-held-cwd', 'independent-chdir-warning-owned-throw', 'independent-chdir-warning-string-handler-throw', 'independent-chdir-warning-string-handler-throw-result')
        cwd = os.fsencode(directory.resolve()) if name == 'chdir-relative' or pipe_chdir else default_cwd
        sub = directory / 'sub'
        sub.mkdir()
        main_path = directory / 'main.php'
        local = directory / 'one.php'
        alternate = sub / 'one.php'
        local.write_bytes(b'<?php return 8;')
        alternate.write_bytes(b'<?php return 7;')
        if pipe_chdir:
            local.write_bytes(b"<?php echo 'M';")
            alternate.write_bytes(b"<?php echo 'Q';")
        sub_bytes = os.fsencode(sub.resolve())
        source = template.replace(b'__SUB__', sub_bytes)
        main_path.write_bytes(source)
        main_bytes = os.fsencode(main_path.resolve())
        mutate = directory / 'mutate.php'
        if name == 'included-function-chdir':
            mutate.write_bytes(b"<?php function f(){return chdir('__SUB__');} f();".replace(b'__SUB__', sub_bytes))
        entries = []
        for cwd_key, include_path, target in [(cwd, b'.:', local), (cwd, sub_bytes, alternate),
                                               (sub_bytes, b'.:', alternate)]:
            opened = os.fsencode(target.resolve())
            entries.append({'caller': b64(main_bytes), 'requested': b64(b'one.php'),
                            'cwd': b64(cwd_key), 'include_path': b64(include_path),
                            'status': 'opened', 'resolved': b64(opened),
                            'opened': b64(opened), 'source': b64(target.read_bytes())})
        if name in ('chdir-stringable-mutate-cwd', 'chdir-stringable-nested-conversion', 'chdir-stringable-named-mutate-cwd', 'chdir-stringable-unpack-mutate-cwd'):
            case_cwd = os.fsencode(directory.resolve())
            opened = os.fsencode(local.resolve())
            entries.append({'caller': b64(main_bytes), 'requested': b64(b'one.php'),
                            'cwd': b64(case_cwd), 'include_path': b64(b'.:'),
                            'status': 'opened', 'resolved': b64(opened),
                            'opened': b64(opened), 'source': b64(local.read_bytes())})
        if name == 'included-function-chdir':
            mutate_bytes = os.fsencode(mutate.resolve())
            entries.append({'caller': b64(main_bytes), 'requested': b64(b'mutate.php'),
                            'cwd': b64(cwd), 'include_path': b64(b'.:'), 'status': 'opened',
                            'resolved': b64(mutate_bytes), 'opened': b64(mutate_bytes),
                            'source': b64(mutate.read_bytes())})
        missing_error = os.strerror(errno.ENOENT).encode()
        if name == 'ini-prefix-interior-nul-missing-require':
            entries.append({'caller': b64(main_bytes), 'requested': b64(b'missing-prefix.php'),
                            'cwd': b64(cwd), 'include_path': b64(sub_bytes),
                            'status': 'missing', 'stream_error': b64(missing_error)})
        if name == 'ini-option-interior-nul-missing-require':
            entries.append({'caller': b64(main_bytes), 'requested': b64(b'missing-ini.php'),
                            'cwd': b64(cwd), 'include_path': b64(sub_bytes),
                            'status': 'missing', 'stream_error': b64(missing_error)})
        chdir_entries = [
            {'cwd': b64(cwd), 'requested': b64(sub_bytes), 'status': 'success',
             'next_cwd': b64(sub_bytes)},
            {'cwd': b64(cwd), 'requested': b64(b'missing'), 'status': 'failure',
             'stream_error': b64(missing_error), 'errno': errno.ENOENT},
            {'cwd': b64(cwd), 'requested': b64(b''), 'status': 'failure',
             'stream_error': b64(missing_error), 'errno': errno.ENOENT},
            {'cwd': b64(cwd), 'requested': b64(b'123'), 'status': 'failure',
             'stream_error': b64(missing_error), 'errno': errno.ENOENT},
        ]
        if name == 'chdir-relative':
            chdir_entries.append({'cwd': b64(cwd), 'requested': b64(b'sub'),
                                  'status': 'success', 'next_cwd': b64(sub_bytes)})
        if name in ('chdir-stringable-mutate-cwd', 'chdir-stringable-nested-conversion', 'chdir-stringable-named-mutate-cwd', 'chdir-stringable-unpack-mutate-cwd'):
            chdir_entries.append({'cwd': b64(sub_bytes), 'requested': b64(b'..'),
                                  'status': 'success',
                                  'next_cwd': b64(os.fsencode(directory.resolve()))})
        if pipe_chdir:
            chdir_entries += [
                {'cwd': b64(cwd), 'requested': b64(b'sub'), 'status': 'success', 'next_cwd': b64(sub_bytes)},
                {'cwd': b64(sub_bytes), 'requested': b64(b'..'), 'status': 'success', 'next_cwd': b64(cwd)},
                {'cwd': b64(sub_bytes), 'requested': b64(b'missing'), 'status': 'failure',
                 'stream_error': b64(missing_error), 'errno': errno.ENOENT},
            ]
        snapshot = {'version': 2, 'main': b64(main_bytes), 'cwd': b64(cwd),
                    'include_path': b64(b'.:'), 'entries': entries,
                    'chdir_entries': chdir_entries}
        snapshot_path = directory / 'snapshot.json'
        snapshot_path.write_text(json.dumps(snapshot, sort_keys=True) + '\n')
        model_command = [str(ROOT / 'bin/php-semantics'), str(main_path),
                         '--file-snapshot', str(snapshot_path), '--steps', '100000', '--timeout', '60']
        native_command = [str(ROOT / '.tools/php/bin/php'), '-n', *flags, '-d', 'include_path=.:', str(main_path)]
        process_cwd = directory if name == 'chdir-relative' or pipe_chdir else ROOT
        # Two directory pauses plus include replay measured 150s; each request keeps its 60s cap.
        model_producer_timeout = (240 if name.startswith(('chdir-warning-', 'independent-chdir-warning-'))
                                  else 180 if name == 'chdir-stringable-nested-conversion' else 90)
        model = subprocess.run(model_command, cwd=process_cwd, env=environment, capture_output=True, timeout=model_producer_timeout)
        native = subprocess.run(native_command, cwd=process_cwd, env=environment, capture_output=True, timeout=30)
        for label, result in [('model', model), ('native', native)]:
            (directory / (label + '.stdout')).write_bytes(result.stdout)
            (directory / (label + '.stderr')).write_bytes(result.stderr)
        try:
            outcome = json.loads(model.stdout)
            matching = (base64.b64decode(outcome.get('stdout', '')) == native.stdout
                        and base64.b64decode(outcome.get('stderr', '')) == native.stderr
                        and outcome.get('exit_status') == native.returncode
                        and outcome.get('status') in {'normal', 'php_error', 'static_rejection'})
        except (ValueError, KeyError):
            outcome = {}
            matching = False
        records.append({'case': name, 'result': 'pass' if matching else 'fail',
                        'source_sha256': digest(main_path), 'snapshot_sha256': digest(snapshot_path),
                        'local_sha256': digest(local), 'alternate_sha256': digest(alternate),
                        'mutate_sha256': digest(mutate) if mutate.exists() else None,
                        'model_command': model_command, 'native_command': native_command,
                        'model_producer_timeout': model_producer_timeout,
                        'process_cwd': str(process_cwd.resolve()),
                        'model_process_exit': model.returncode, 'native_exit': native.returncode,
                        'model_status': outcome.get('status'),
                        'model_stdout_sha256': digest(directory / 'model.stdout'),
                        'model_stderr_sha256': digest(directory / 'model.stderr'),
                        'native_stdout_sha256': digest(directory / 'native.stdout'),
                        'native_stderr_sha256': digest(directory / 'native.stderr')})
        print(name, records[-1]['result'], outcome.get('status'), flush=True)
    after = {str(path.relative_to(ROOT)): digest(path) for path in watched}
    vendor_after = vendor_identity()
    report = {'inputs': before, 'input_changes': [key for key in before if before[key] != after[key]],
              'vendor_tree': vendor_before,
              'chdir_fact_basis': 'Created finite subdirectory canonicalized with Path.resolve; ENOENT number and C-locale strerror from errno.ENOENT/os.strerror, checked against pinned native raw outputs',
              'profile': profile, 'environment': {'LC_ALL': 'C', 'cwd': str(ROOT.resolve())},
              'cases': records, 'passed': all(row['result'] == 'pass' for row in records)}
    (out / 'report.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    assert report['passed'] and not report['input_changes'] and vendor_before == vendor_after


if __name__ == '__main__':
    main()
