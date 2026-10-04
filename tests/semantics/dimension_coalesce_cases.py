"""Native predictions for nested CV-array coalesce assignment."""
CASES = [
    ('missing-prefix-key-kept-table-latches-null-and-deprecates', b'''<?php
error_reporting(0);
$seed=5;$a=[''=>[1=>$seed],1=>[1=>13]];$held=$a;
function rhs262(){echo "S;";return 37;}
set_error_handler(function($n,$m){if($n===2){echo "U;";$GLOBALS['missing']=1;$GLOBALS['a'][''][1]=17;}else{echo "D;";}return false;},30719);
$r=($a[$missing][1]??=rhs262());restore_error_handler();
echo "R:",$r,":",$a[''][1],":",$a[1][1],":",$missing,";";
''', b'U;D;R:5:17:13:1;'),
    ('missing-prefix-key-latches-null-before-deprecation', b'''<?php
error_reporting(0);
$seed=5;$a=[''=>[1=>$seed],1=>[1=>13]];
function rhs262(){echo "S;";return 37;}
set_error_handler(function($n,$m){if($n===2){echo "U;";$GLOBALS['missing']=1;$GLOBALS['a'][''][1]=17;}else{echo "D;";}return false;},30719);
$r=($a[$missing][1]??=rhs262());restore_error_handler();
echo "R:",$r,":",$a[''][1],":",$a[1][1],":",$missing,";";
''', b'U;D;R:17:17:13:1;'),
    ('nan-prefix-ordered-tail-retains-moved-parent-and-real-cell', b'''<?php
error_reporting(0);
class NaNCell262{public static int $value=5;}
$cell=&NaNCell262::$value;$a=[0=>[1=>&$cell]];$key=NAN;
function rhs262(){echo "S;";return 37;}
set_error_handler(function($n,$m){if($n===2){echo "W;";$GLOBALS['held']=$GLOBALS['a'];NaNCell262::$value=17;unset($GLOBALS['a'],$GLOBALS['cell'],$GLOBALS['key']);}else{echo "D;";}return false;},30719);
$r=($a[$key][1]??=rhs262());restore_error_handler();
echo "R:",$r,":",$held[0][1],":",isset($a)?1:0,":",isset($cell)?1:0,";V:",NaNCell262::$value,";";
''', b'W;D;R:17:17:0:0;V:17;'),
    ('multiline-prefix-and-final-memoized-write-lines', b'''<?php
error_reporting(0);
$seed=null;$a=[1=>[1=>$seed]];$outer=1.5;$inner=1.5;
function key262(){echo "K;";return $GLOBALS['outer'];}
function rhs262(){echo "S;";return 17;}
set_error_handler(function($n,$m,$f,$l){echo "D:",$l,";";return false;},8192);
$r=($a[
    key262()
    +0.0
][
    $inner
]??=rhs262());restore_error_handler();
echo "R:",$r,":",$a[1][1],";";
''', b'K;D:9;D:11;S;D:7;D:10;R:17:17;'),
    ('computed-array-rhs-retains-real-cell-through-prefix-abort', b'''<?php
error_reporting(0);
class RHSCell262{public static int $value=5;}
$seed=null;$a=[1=>[1=>$seed]];$key=1.5;$hits=0;$cell=&RHSCell262::$value;
set_error_handler(function($n,$m){$GLOBALS['hits']++;echo "D;";if($GLOBALS['hits']===2){$GLOBALS['held']=$GLOBALS['a'];unset($GLOBALS['cell'],$GLOBALS['key']);}return false;},8192);
$r=($a[$key][1]??=[&$cell]);restore_error_handler();
echo "R:",$r[0],":",$a[1][1]===null?1:0,":",$held[1][1]===null?1:0,":",isset($cell)?1:0,";";
$r[0]=17;echo "V:",RHSCell262::$value,";";
''', b'D;D;R:5:1:1:0;V:17;'),
    ('late-keyed-rhs-throw-writes-precreated-entry-before-unwind', b'''<?php
error_reporting(0);
class Destination262{public static int $value=9;}
$seed=5;$a=[1=>[1=>$seed]];$keep=&$a;$key=1.5;
$older=new Error('older');$err=new Error('handler',0,$older);$original=$err;
set_error_handler(function($n,$m){if($n===2){echo "U:",$GLOBALS['keep'][1]===[1=>5,2=>null]?1:0,";";$GLOBALS['a'][1][2]=31;$GLOBALS['missing']=37;$e=$GLOBALS['err'];unset($GLOBALS['err'],$GLOBALS['older']);throw $e;}echo "D;";return false;},30719);
try{Destination262::$value=($a[$key][2]??=$missing);}catch(Error $e){echo "C:",$e===$original?1:0,":",Destination262::$value,":",$keep[1][2]===null?1:0,":",$missing,":",$e->getMessage(),":",$e->getPrevious()->getMessage(),";";}
restore_error_handler();echo "V:",Destination262::$value,";";
''', b'D;D;U:1;C:1:9:1:37:handler:older;V:9;'),
]
