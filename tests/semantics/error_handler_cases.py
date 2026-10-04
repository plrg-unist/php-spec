"""Ordinary source error-handler behavior; expected bytes are authored facts."""

CASES = [
    ('registration-stack', b'''<?php
function eh13a($n,$m,$f,$l) {} function eh13b($n,$m,$f,$l) {}
echo set_error_handler('eh13a') === null;
echo set_error_handler('eh13b',512) === 'eh13a';
echo get_error_handler() === 'eh13b';
echo restore_error_handler(); echo get_error_handler() === 'eh13a';
echo set_error_handler(null) === 'eh13a'; echo get_error_handler() === null;
restore_error_handler(); echo get_error_handler() === 'eh13a';
restore_error_handler(); echo get_error_handler() === null;
echo restore_error_handler(); echo get_error_handler() === null;
''', b'11111111111', 'normal'),
    ('mask-reporting-and-silence', b'''<?php
error_reporting(0);
set_error_handler(function($n,$m,$f,$l){echo 'H',$n,';';return false;},512);
echo trigger_error('match',512); trigger_error('miss',1024);
@trigger_error('silent',512); restore_error_handler();
''', b'H512;1H512;', 'normal'),
    ('zero-and-null-are-handled', b'''<?php
set_error_handler(function($n,$m,$f,$l){echo 'Z';return 0;});
echo trigger_error('zero',512);
set_error_handler(function($n,$m,$f,$l){echo 'N';});
echo trigger_error('null',1024); restore_error_handler(); restore_error_handler();
''', b'Z1N1', 'normal'),
    ('replacement-nested-and-throw', b'''<?php
class Handler13 {public function __invoke($n,$m,$f,$l) {
 echo 'A',func_num_args(),':',get_error_handler() === null;
 set_error_handler(function($n,$m,$f,$l){echo 'B',func_num_args(),':',$n,';';return 0;},512);
 trigger_error('nested',512); throw new Exception('end');
}}
$handler=new Handler13;set_error_handler($handler,512);unset($handler);
try {trigger_error('outer',512);}catch(Throwable $e){echo 'C';}
echo get_error_handler() instanceof Closure; trigger_error('later',512);
restore_error_handler();restore_error_handler();echo get_error_handler() === null;
''', b'A4:1B4:512;C1B4:512;1', 'normal'),
    ('callback-finally-before-caller-catch', b'''<?php
function eh13throw($n,$m,$f,$l){try{echo 'T';throw new Error('x');}
finally{echo get_error_handler() === null ? 'F' : 'bad';}}
set_error_handler('eh13throw',512);
try{trigger_error('x',512);}catch(Throwable $e){echo get_error_handler() === 'eh13throw' ? 'C' : 'bad';}
finally{echo get_error_handler() === 'eh13throw' ? 'M' : 'bad';}
restore_error_handler();
''', b'TFCM', 'normal'),
    ('undefined-assignment-null-snapshot', b'''<?php
set_error_handler(function($n,$m,$f,$l){global $missing13;$missing13=9;echo 'H';});
$out=$missing13; echo $out === null ? 'N' : 'bad';echo ':',$missing13;
restore_error_handler();
''', b'HN:9', 'normal'),
    ('missing-left-before-live-right', b'''<?php
set_error_handler(function($n,$m,$f,$l){global $missing13,$right13;$missing13=9;$right13=5;echo 'H';});
echo $missing13+$right13;echo ':',$missing13,':',$right13;restore_error_handler();
''', b'H5:9:5', 'normal'),
    ('known-left-before-missing-right', b'''<?php
set_error_handler(function($n,$m,$f,$l){global $missing13;$missing13=9;echo 'H';});
echo 7+$missing13;echo ':',$missing13;restore_error_handler();
''', b'H7:9', 'normal'),
    ('reporting-null-and-signed32', b'''<?php
echo error_reporting() === 30719;echo ':',error_reporting(null);
echo ':',error_reporting(4294967295);echo ':',error_reporting();
echo ':',error_reporting(-2147483649);echo ':',error_reporting();
''', b'1:30719:30719:-1:-1:2147483647', 'normal'),
    ('api-errors-named-and-unpacked', b'''<?php
try{trigger_error('bad',2);}catch(ValueError $e){echo 'V';}
try{set_error_handler(17);}catch(TypeError $e){echo 'C';}
try{restore_error_handler(1);}catch(ArgumentCountError $e){echo 'R';}
try{trigger_error(error_level:512);}catch(ArgumentCountError $e){echo 'M';}
function eh13named($n,$m,$f,$l){echo $n,':',$m,':',func_num_args();}
set_error_handler(callback:'eh13named',error_levels:512);
user_error(...['message'=>'ok','error_level'=>512]);restore_error_handler();
''', b'VCRM512:ok:4', 'normal'),
    ('user-fatal-deprecation-throw-priority', b'''<?php
error_reporting(0);
set_error_handler(function($n,$m,$f,$l){echo $n;throw new Exception('deprecated');},8192);
try{trigger_error('fatal',256);echo 'bad';}catch(Exception $e){echo 'D';}
restore_error_handler();
''', b'8192D', 'normal'),
    ('user-fatal-handled', b'''<?php
set_error_handler(function($n,$m,$f,$l){echo $n,';';});
echo trigger_error('fatal',256);restore_error_handler();
''', b'8192;256;1', 'normal'),
    ('user-fatal-masked-default', b'''<?php
error_reporting(0);echo 'before';
trigger_error('fatal',256);echo 'bad';
''', b'before', 'php_error'),
    ('user-fatal-displayed-default', b'''<?php
error_reporting(256);echo 'before';
trigger_error('fatal',256);echo 'bad';
''', b'before', 'php_error'),
    ('weak-message-raw-level-uncaught-trace', b'''<?php
function eh13trace($n,$m,$f,$l){throw new Exception('raised');}
set_error_handler('eh13trace',512);
trigger_error(123,'512');
''', b'', 'php_error'),
    ('temporary-reference-and-omitted-default', b'''<?php
function eh13ref(&$n,$m,$f,$l,$extra=7){$n=999;echo func_num_args(),':',$extra;}
error_reporting(0);set_error_handler('eh13ref',512);trigger_error('x',512);restore_error_handler();
''', b'4:7', 'normal'),
    ('required-fifth-argument-error', b'''<?php
function eh13five($n,$m,$f,$l,$required) {echo 'bad';}
set_error_handler('eh13five',512);
try{trigger_error('x',512);}catch(ArgumentCountError $e){echo $e->getMessage();}
restore_error_handler();
''', b'Too few arguments to function eh13five(), 4 passed and exactly 5 expected', 'normal'),
    ('direct-callback-type-error-message', b'''<?php
function eh13int($n,int $m,$f,$l) {echo 'bad';}
set_error_handler('eh13int',512);
try{trigger_error('nonnumeric',512);}catch(TypeError $e){echo $e->getMessage();}
restore_error_handler();
''', b'eh13int(): Argument #2 ($m) must be of type int, string given', 'normal'),
    ('converted-message-before-level-errors', b'''<?php
try{trigger_error(123,2);}catch(ValueError $e){$t=$e->getTrace();echo $t[0]['args'][0] === '123' ? 'V' : 'bad';}
try{trigger_error(123,'bad');}catch(TypeError $e){$t=$e->getTrace();echo $t[0]['args'][0] === '123' ? 'T' : 'bad';}
''', b'VT', 'normal'),
    ('ordinary-warning-before-type-error', b'''<?php
try{'2tail'+'bad';}catch(TypeError $e){echo 'T';}
''', b'T', 'normal'),
    ('pending-warning-cannot-be-overwritten', b'''<?php
set_error_handler(function($n,$m,$f,$l){echo 'H';});
try{'2tail'+'bad';}catch(TypeError $e){echo 'T';}
restore_error_handler();
''', b'HT', 'unsupported'),
    ('user-fatal-false-callback-trace', b'''<?php
error_reporting(256);$arg=[];$arg[]=1;
function eh13cause(&$v){trigger_error(123,'256');}
function eh13fataltrace($n,$m,$f,$l){global $arg;$arg[0]=9;return false;}
set_error_handler('eh13fataltrace',256);
eh13cause($arg);
''', b'', 'php_error'),
    ('user-fatal-nested-warning-clears-trace', b'''<?php
error_reporting(256);
function eh13fatalclear($n,$m,$f,$l){trigger_error('nested',512);return false;}
set_error_handler('eh13fatalclear',256);
trigger_error('outer',256);
''', b'', 'php_error'),
    ('nonfatal-fallback-retains-inner-fatal-trace', b'''<?php
error_reporting(512);
function eh13innerfatal($n,$m,$f,$l){return null;}
function eh13outerwarning($n,$m,$f,$l){set_error_handler('eh13innerfatal',256);trigger_error('inner',256);return false;}
set_error_handler('eh13outerwarning',512);
trigger_error('outer',512);
''', b'', 'normal'),

]

from reporting_cases import CASES as REPORTING_CASES, FILE_MODE as REPORTING_FILE_MODE
CASES.extend(case for case in REPORTING_CASES if case[0] not in REPORTING_FILE_MODE)
