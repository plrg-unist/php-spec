"""Missing CV reference sends and rejected ASSIGN exception priority."""
from warning_consumer_cases import CASES as CONSUMERS

CASES = [
    ('positional-reference-shares-created-null', b'''<?php
error_reporting(0); $hits220=0;
function pair220(&$first,&$second) {
    echo func_num_args(),":",$first===null?"N":"BAD",":",$second===null?"N":"BAD",";";
    $first=3; echo $second===3?"1:":"BAD:"; $second=5; echo $first,";";
}
set_error_handler(function($level,$message,$file,$line) {$GLOBALS['hits220']=$GLOBALS['hits220']+1; return true;},2);
pair220($missing220,$missing220);
echo $missing220,":",$hits220,";";
restore_error_handler();
''', b'2:N:N;1:5;5:0;', 'normal'),
    ('named-reference-shares-created-null', b'''<?php
error_reporting(0); $hits220=0;
function namedPair220(&$first,&$second) {
    echo func_num_args(),":",$first===null?"N":"BAD",":",$second===null?"N":"BAD",";";
    $second=4; echo $first===4?"1:":"BAD:"; $first=6; echo $second,";";
}
set_error_handler(function($level,$message,$file,$line) {$GLOBALS['hits220']=$GLOBALS['hits220']+1; return true;},2);
$target220='namedPair220';
$target220(second:$missing220,first:$missing220);
echo $missing220,":",$hits220,";";
restore_error_handler();
''', b'2:N:N;1:6;6:0;', 'normal'),
    ('unknown-name-before-reference-creation', b'''<?php
error_reporting(0); $hits220=0;
function reject220(&$value) {echo "BAD;";}
set_error_handler(function($level,$message,$file,$line) {$GLOBALS['hits220']=$GLOBALS['hits220']+1; echo "H",func_num_args(),";"; return true;},2);
try {reject220(other:$missing220);} catch(Error $e) {
    echo $e->getMessage()==='Unknown named parameter $other'?"U:":"BAD:",$hits220,";";
}
echo $missing220; echo $hits220,";";
restore_error_handler();
''', b'U:0;H4;1;', 'normal'),
    ('duplicate-name-before-reference-creation', b'''<?php
error_reporting(0); $hits220=0; $first220=8;
function reject220(&$value) {echo "BAD;";}
set_error_handler(function($level,$message,$file,$line) {$GLOBALS['hits220']=$GLOBALS['hits220']+1; echo "H",func_num_args(),";"; return true;},2);
try {reject220($first220,value:$missing220);} catch(Error $e) {
    echo $e->getMessage()==='Named parameter $value overwrites previous argument'?"D:":"BAD:",$first220,":",$hits220,";";
}
echo $missing220; echo $hits220,";";
restore_error_handler();
''', b'D:8:0;H4;1;', 'normal'),
    ('later-reference-fetch-uses-defined-cv-and-selected-target', b'''<?php
error_reporting(0);
function sink220($prior,&$value) {
    echo "S",func_num_args(),":",$prior===null?"N":"BAD",":",$value,";"; $value=5;
}
function other220($prior,$value) {echo "BAD;";}
$target220='sink220';
$handler220=function($level,$message,$file,$line) {
    $GLOBALS['target220']='other220'; $GLOBALS['reference220']=7;
    echo "H",func_num_args(),";"; return true;
};
set_error_handler($handler220,2);
$target220($missing220,$reference220);
echo $reference220,":",$target220==='other220'?"other":"BAD",":",get_error_handler()===$handler220?1:0,";";
restore_error_handler();
''', b'H4;S2:N:7;5:other:1;', 'normal'),
    ('returned-handler-attaches-rejecting-destination', b'''<?php
error_reporting(0);
class Attach220 {public static int $slot=7;}
$destination220=1;
$handler220=function($level,$message,$file,$line) {
    $GLOBALS['destination220'] =& Attach220::$slot; $GLOBALS['missing220']=9;
    echo "H",func_num_args(),";"; return true;
};
set_error_handler($handler220,2);
try {$destination220=$missing220; echo "BAD;";} catch(TypeError $e) {
    echo "C:",$destination220,":",$missing220,":",$e->getPrevious()===null?"N":"BAD",":",get_error_handler()===$handler220?1:0,";";
}
restore_error_handler();
''', b'H4;C:7:9:N:1;', 'normal'),
    ('rejected-write-replaces-error-and-retains-previous-chain', b'''<?php
error_reporting(0);
class Chain220 {public static int $slot=7;}
$destination220 =& Chain220::$slot;
$seed220=new Error('seed'); $pending220=new Error('handler',0,$seed220);
$handler220=function($level,$message,$file,$line) use($pending220) {
    $GLOBALS['missing220']=9;
    echo "H",func_num_args(),";"; throw $pending220;
};
set_error_handler($handler220,2);
try {
    $destination220 =
        $missing220;
    echo "BAD;";
} catch(TypeError $e) {
    echo "C:",$destination220,":",$missing220,":",$e->getPrevious()===$pending220?1:0,":",$e->getPrevious()->getPrevious()===$seed220?1:0,":",get_error_handler()===$handler220?1:0,";";
    $pending220=null; echo $e->getPrevious()->getMessage(),":",$e->getPrevious()->getPrevious()->getMessage(),";";
}
restore_error_handler();
''', b'H4;C:7:9:1:1:1;handler:seed;', 'normal'),
    ('strict-handler-rejection-precedes-constrained-write-error', b'''<?php
declare(strict_types=1);
error_reporting(0);
class Strict220 {public static int $slot=7;}
$destination220 =& Strict220::$slot;
function handler220(string $level,$message,$file,$line) {echo "BAD;";}
set_error_handler('handler220',2);
try {$destination220=$missing220; echo "BAD;";} catch(TypeError $e) {
    echo "C:",$destination220,":",$e->getPrevious() instanceof TypeError?1:0,":",$e->getPrevious()->getPrevious()===null?1:0,":",get_error_handler()==='handler220'?1:0,";";
}
restore_error_handler();
''', b'C:7:1:1:1;', 'normal'),
]

# This exact predecessor source was an Unsupported control. Only its changed
# constrained-write behavior is selected here; the other consumer rows stay put.
predecessor = next(c for c in CONSUMERS if c[0] == 'rejected-constrained-assign-throw-pending')
CASES.append(('constrained-rejection-now-chains-handler-error', predecessor[1], predecessor[2], 'normal'))
