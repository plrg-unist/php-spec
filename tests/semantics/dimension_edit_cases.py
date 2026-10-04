"""Original sources for coalesce-assignment and unset key continuations."""

CASES = [
    ('unset-float-separates-before-copy-and-keeps-selected-key', b'''<?php
error_reporting(0);$seed249=5;$a249=[1=>$seed249];$old249=$a249;$key249=1.5;
function copyUnset249($level,$message,$file,$line) {$GLOBALS['held249']=$GLOBALS['a249'];$GLOBALS['key249']=7.5;echo "D;";return false;}
set_error_handler('copyUnset249',8192);unset($a249[$key249]);
echo "R:",isset($a249[1])?1:0,":",isset($held249[1])?1:0,":",$old249[1],":",$key249,";";restore_error_handler();
''', b'D;R:0:0:5:7.5;', 'normal'),
    ('unset-undefined-key-keeps-empty-key-without-null-notice', b'''<?php
error_reporting(0);$seed249=5;$a249=[''=>$seed249];$hits249=0;
function missingUnset249($level,$message,$file,$line) {$GLOBALS['hits249']++;if($level===2) {echo "U;";$GLOBALS['held249']=$GLOBALS['a249'];$GLOBALS['key249']='changed';} else {echo "D;";}return true;}
set_error_handler('missingUnset249',8194);unset($a249[$key249]);
echo "R:",isset($a249[''])?1:0,":",isset($held249[''])?1:0,":",$key249,":",$hits249,";";restore_error_handler();
''', b'U;R:0:0:changed:1;', 'normal'),
    ('unset-nan-tail-retains-table-through-moved-keeper', b'''<?php
error_reporting(0);$seed249=5;$a249=[0=>$seed249,7=>11];$key249=NAN;
function nanUnset249($level,$message,$file,$line) {if($level===2) {echo "W;";$GLOBALS['held249']=$GLOBALS['a249'];unset($GLOBALS['a249']);$GLOBALS['key249']=7.5;} else {echo "D;";}return true;}
set_error_handler('nanUnset249',8194);unset($a249[$key249]);
echo "R:",isset($a249)?1:0,":",isset($held249[0])?1:0,":",$held249[7],":",$key249,";";restore_error_handler();
''', b'W;D;R:0:0:11:7.5;', 'normal'),
    ('coalesce-null-quiet-capture-precedes-rhs-and-write-copy-abort', b'''<?php
error_reporting(0);$seed249=null;$a249=[''=>$seed249];$hits249=0;
function copiedCoalesce249($level,$message,$file,$line) {$GLOBALS['hits249']++;echo "D",$GLOBALS['hits249'],";";if($GLOBALS['hits249']===1) {$GLOBALS['held249']=$GLOBALS['a249'];$GLOBALS['a249']['']=13;} else {$GLOBALS['later249']=$GLOBALS['a249'];}return true;}
function rhsCoalesce249() {echo "S;";return 7;}
set_error_handler('copiedCoalesce249',8192);$result249=($a249[null]??=rhsCoalesce249());
echo "R:",$result249===null?1:0,":",$a249[''],":",$held249['']===null?1:0,":",$later249[''],";";restore_error_handler();
''', b'D1;S;D2;R:1:13:1:13;', 'normal'),
    ('coalesce-present-shared-cell-skips-rhs-after-key-callback', b'''<?php
error_reporting(0);$seed249=5;$a249=[1=>&$seed249];$key249=1.5;
function presentCoalesce249($level,$message,$file,$line) {echo "D;";$GLOBALS['held249']=$GLOBALS['a249'];$GLOBALS['seed249']=17;$GLOBALS['a249']=[7=>31];$GLOBALS['key249']=7.5;return true;}
function wrongRhs249() {echo "WRONG;";return 7;}
set_error_handler('presentCoalesce249',8192);$result249=($a249[$key249]??=wrongRhs249());
echo "R:",$result249,":",$held249[1],":",$a249[7],":",$key249,";";restore_error_handler();
''', b'D;R:17:17:31:7.5;', 'normal'),
]
