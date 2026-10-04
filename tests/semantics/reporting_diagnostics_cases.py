"""Runtime deprecated constants and lossy reporting ZPP diagnostics."""

CASES = [
    ('estrict-runtime-repeat-dead-branch', br'''<?php
if (false) {echo E_STRICT;}
set_error_handler(function($level,$message,$file,$line){echo 'H',func_num_args(),$level===E_DEPRECATED&&$message==='Constant E_STRICT is deprecated since 8.4, the error level was removed'?'M':'X';return 0;},E_DEPRECATED);
echo E_STRICT,':',E_STRICT;
restore_error_handler();
''', b'H4M2048:H4M2048', 'normal'),
    ('estrict-namespace-shadow-runtime-initializer', br'''<?php
namespace Diagnostic;
const E_STRICT=17;
set_error_handler(function($level,$message){echo 'H';return 0;},E_DEPRECATED);
echo E_STRICT,':';
const SAVED=\E_STRICT;
echo SAVED,':';
try {echo \e_strict;}catch(\Error $e){echo $e->getMessage()==='Undefined constant "e_strict"'?'C':'X';}
restore_error_handler();
''', b'17:H2048:C', 'normal'),
    ('estrict-visible-default', br'''<?php
echo E_STRICT;
''', b'2048', 'normal'),
    ('estrict-deferred-default-and-class-cache', br'''<?php
set_error_handler(function($level,$message){echo 'H';return 0;},E_DEPRECATED);
function strictDefault($value=E_STRICT){echo 'D';return $value;}
class StrictHolder {const VALUE=E_STRICT;}
echo 'A',strictDefault(),'|',strictDefault(),'|',StrictHolder::VALUE,'|',StrictHolder::VALUE;
restore_error_handler();
''', b'AHD2048|D2048|H2048|2048', 'normal'),
    ('estrict-suppressed-default', br'''<?php
$value=@E_STRICT;
echo $value,':',error_reporting(),':',ini_get('error_reporting');
''', b'2048:30719:30719', 'normal'),
    ('estrict-handler-false-live-mask', br'''<?php
ini_set('error_reporting',"0\0before");
set_error_handler(function($level,$message){echo 'H';ini_set('error_reporting',"8192\0visible");return false;},E_DEPRECATED);
echo E_STRICT;
restore_error_handler();
echo ':',error_reporting(),':',ini_get('error_reporting');
''', b'H2048:8192:8192\0visible', 'normal'),
    ('reporting-lossy-float-visible', br'''<?php
echo error_reporting(3.5),':',error_reporting(),':',ini_get('error_reporting');
''', b'30719:3:3', 'normal'),
    ('reporting-lossy-suppression-and-integral', br'''<?php
echo @error_reporting(3.5),':',error_reporting(),':',ini_get('error_reporting'),'|';
echo error_reporting(3.0),':',error_reporting(),'|';
try {error_reporting(INF);}catch(TypeError $e){echo 'I';}
try {error_reporting(NAN);}catch(TypeError $e){echo 'N';}
try {error_reporting("3.5\0bad");}catch(TypeError $e){echo 'Z';}
echo ':',error_reporting(),':',ini_get('error_reporting');
''', b'4437:3:3|3:3|INZ:3:3', 'normal'),
    ('reporting-lossy-handler-postconversion-old', br'''<?php
set_error_handler(function(string $level,$message,$file,$line){echo 'H',func_num_args(),$level==='8192'?'W':'X';ini_set('error_reporting',"512\0handler");return 0;},E_DEPRECATED);
echo error_reporting(error_level:'3.5'),':',error_reporting(),':',ini_get('error_reporting');
restore_error_handler();
''', b'H4W512:3:3', 'normal'),
    ('reporting-lossy-handler-false-mask-zero', br'''<?php
set_error_handler(function($level,$message){echo 'H';ini_set('error_reporting',"0\0quiet");return false;},E_DEPRECATED);
echo error_reporting(-3.5),':',error_reporting(),':',ini_get('error_reporting');
restore_error_handler();
''', b'H0:-3:-3', 'normal'),
    ('reporting-lossy-owned-handler-throw-original-trace', br'''<?php
declare(strict_types=1);
set_error_handler(function(string $level,$message){echo $level==='8192'?'W':'X';ini_set('error_reporting',"512\0throw");throw new Exception('stop');},E_DEPRECATED);
$value=7;$owned=error_reporting(...);
try {$value=$owned->__invoke('3.5');}catch(Exception $e){
    $trace=$e->getTrace();$internal=$trace[1];$wrapper=$trace[2];
    echo $internal['function']==='error_reporting'&&$internal['args']===['3.5']?'I':'X';
    echo $wrapper['function']==='__invoke'&&$wrapper['args']===['3.5']?'O':'X';
}
restore_error_handler();
echo $value,':',error_reporting(),':',ini_get('error_reporting');
''', b'WIO7:512:512\0throw', 'normal'),
]

STDERR = {
    'estrict-visible-default':
        b'Deprecated: Constant E_STRICT is deprecated since 8.4, the error level was removed in {file} on line 2\n',
    'estrict-handler-false-live-mask':
        b'Deprecated: Constant E_STRICT is deprecated since 8.4, the error level was removed in {file} on line 4\n',
    'reporting-lossy-float-visible':
        b'Deprecated: Implicit conversion from float 3.5 to int loses precision in {file} on line 2\n',
}
