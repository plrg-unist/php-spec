"""Reporting INI bytes, live masks and core error constants."""

CASES = [
    ('reporting-core-error-constants', br'''<?php
namespace Diagnostic;
echo E_ERROR,',',E_WARNING,',',E_PARSE,',',E_NOTICE,',',E_CORE_ERROR,',',E_CORE_WARNING,',',E_COMPILE_ERROR,',',E_COMPILE_WARNING,',',E_USER_ERROR,',',E_USER_WARNING,',',E_USER_NOTICE,',',E_RECOVERABLE_ERROR,',',E_DEPRECATED,',',E_USER_DEPRECATED,',',E_ALL;
''', b'1,2,4,8,16,32,64,128,256,512,1024,4096,8192,16384,30719', 'normal'),
    ('reporting-constant-shadow-and-case', br'''<?php
namespace Diagnostic;
const E_WARNING=7;
echo E_WARNING,'/',\E_WARNING,'/';
try {echo \e_warning;}catch(\Error $e){echo $e->getMessage()==='Undefined constant "e_warning"'?'C':'X';}
''', b'7/2/C', 'normal'),
    ('reporting-raw-get-set-restore', br'''<?php
echo ini_get('error_reporting'),'|';
echo ini_set(value:" \t+512junk\0tail",option:'error_reporting'),'|';
echo error_reporting(),'|',ini_get('error_reporting'),'|';
echo error_reporting(512),'|',ini_get('error_reporting'),'|';
echo ini_restore('error_reporting')===null?'N':'X';
echo error_reporting(),'|',ini_get('error_reporting');
''', b'30719|30719|512| \t+512junk\0tail|512| \t+512junk\0tail|N30719|30719', 'normal'),
    ('reporting-empty-null-and-nul-values', br'''<?php
echo ini_set('error_reporting',"\0tail"),'|',error_reporting(),'|',ini_get('error_reporting'),'|';
echo ini_set('error_reporting',null),'|',error_reporting(),'|',ini_get('error_reporting'),'|';
echo ini_set('error_reporting','2.5suffix'),'|',error_reporting(),'|',ini_get('error_reporting');
''', b'30719|0|\0tail|\0tail|0|||2|2.5suffix', 'normal'),
    ('reporting-signed64-overflow-prefix', br'''<?php
ini_set('error_reporting','9223372036854775808');
echo error_reporting(),'|',ini_get('error_reporting'),'|';
ini_set('error_reporting','-9223372036854775809');
echo error_reporting(),'|',ini_get('error_reporting');
''', b'-1|9223372036854775808|0|-9223372036854775809', 'normal'),
    ('reporting-strict-direct-and-owned-parse', br'''<?php
declare(strict_types=1);
try {error_reporting('2');}catch(TypeError $e){echo $e->getMessage()==='error_reporting(): Argument #1 ($error_level) must be of type ?int, string given'?'D':'X';}
$f=error_reporting(...);
try {$f(error_level:'2');}catch(TypeError $e){echo 'C';}
echo '|',$f->__invoke(error_level:'2'),'|',error_reporting(),'|',ini_get('error_reporting');
echo '|',$f->__invoke(error_level:null),'|',ini_get('error_reporting');
''', b'DC|30719|2|2|2|2', 'normal'),
    ('reporting-option-callback-late-old-and-frame', br'''<?php
class ReportOption {
    function __toString():string {
        echo 'C',func_num_args(),func_get_args()===[]?'Z':'X';
        ini_set('error_reporting',"2\0inner");
        return 'error_reporting';
    }
}
function setReport($first,$second) {
    $saved=func_get_args();
    echo func_num_args(),':',$saved[0],':',$saved[1],'|';
    $old=ini_set(value:"512\0outer",option:new ReportOption);
    echo $old,'|',error_reporting(),'|',ini_get('error_reporting');
    echo func_num_args()===2&&func_get_args()===$saved?'S':'X';
}
setReport(second:'B',first:'A');
''', b'2:A:B|C0Z2\0inner|512|512\0outerS', 'normal'),
    ('reporting-option-miss-and-value-priority', br'''<?php
class ReportMiss {
    function __toString():string {
        echo 'C';
        ini_set('error_reporting',"2\0inner");
        return "error_reporting\0missing";
    }
}
echo ini_get('ERROR_REPORTING')===false?'F':'X';
try {ini_set(value:[],option:new ReportMiss);}catch(TypeError $e){echo $e->getMessage()==='ini_set(): Argument #2 ($value) must be of type string|int|float|bool|null'?'T':'X';}
echo '|',error_reporting(),'|',ini_get('error_reporting');
''', b'FCT|2|2\0inner', 'normal'),
    ('reporting-silence-restores-modified-entry', br'''<?php
function reportProbe() {
    echo error_reporting(),':',ini_get('error_reporting');
    ini_restore('error_reporting');
    echo ':',error_reporting(),':',ini_get('error_reporting');
}
@reportProbe();
echo '|',error_reporting(),':',ini_get('error_reporting');
''', b'4437:30719:30719:30719|30719:30719', 'normal'),
    ('reporting-handler-false-live-mask-routing', br'''<?php
ini_set('error_reporting',"0\0off");
set_error_handler(function($level,$message,$file,$line){echo 'H',func_num_args();ini_set('error_reporting',"512\0on");return false;},E_USER_WARNING);
echo trigger_error('report-visible',E_USER_WARNING)?'T':'F';
restore_error_handler();
echo '|',error_reporting(),'|',ini_get('error_reporting');
''', b'H4T|512|512\0on', 'normal'),
]

FILE_MODE = {
    'reporting-option-callback-late-old-and-frame',
    'reporting-option-miss-and-value-priority',
}
STDERR = {
    'reporting-handler-false-live-mask-routing':
        b'Warning: report-visible in {file} on line 4\n',
}


# Exact independent literals from the reviewed source input.
CASES += [
    ('independent-reporting-raw-signed32-owned-strict', b'<?php\ndeclare(strict_types=1);\nini_set(\'error_reporting\', "0008tail\\0raw");\necho error_reporting(), \':\', ini_get(\'error_reporting\'), \'|\';\necho error_reporting(E_NOTICE), \':\', ini_get(\'error_reporting\'), \'|\';\necho error_reporting(4294967304), \':\', error_reporting(), \':\', ini_get(\'error_reporting\'), \'|\';\ntry { error_reporting(error_level: \'8\'); }\ncatch (TypeError $e) {\n    echo $e->getMessage() === \'error_reporting(): Argument #1 ($error_level) must be of type ?int, string given\' ? \'T\' : \'X\';\n}\n$owned = error_reporting(...);\necho \':\', $owned->__invoke(\'512\'), \':\', error_reporting(), \':\', ini_get(\'error_reporting\');\nini_restore(\'error_reporting\');\necho \':\', error_reporting(), \':\', ini_get(\'error_reporting\');\n', b'8:0008tail\x00raw|8:0008tail\x00raw|8:8:4294967304|T:8:512:512:30719:30719', 'normal'),
    ('independent-reporting-silence-restore-handler-live', b'<?php\nini_restore(\'error_reporting\');\nfunction reportingDuringSilence() {\n    echo error_reporting(), \':\', ini_get(\'error_reporting\'), \'|\';\n    ini_restore(\'error_reporting\');\n    echo error_reporting(), \':\', ini_get(\'error_reporting\'), \'|\';\n}\n@reportingDuringSilence();\necho error_reporting(), \':\', ini_get(\'error_reporting\'), \'|\';\nset_error_handler(function ($level, $message, $file, $line) {\n    echo \'H\', func_num_args(), \':\', error_reporting(), \':\', ini_get(\'error_reporting\'), \'|\';\n    ini_set(\'error_reporting\', "0\\0handled");\n    return false;\n}, E_USER_NOTICE);\n@trigger_error(\'quiet\', E_USER_NOTICE);\necho error_reporting(), \':\', ini_get(\'error_reporting\'), \'|\';\nrestore_error_handler();\nini_restore(\'error_reporting\');\necho error_reporting(), \':\', ini_get(\'error_reporting\');\n', b'4437:30719|30719:30719|30719:30719|H4:4437:30719|30719:0\x00handled|30719:30719', 'normal'),
]
