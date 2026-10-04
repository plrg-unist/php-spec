"""Original GLOBALS read-write name, lookup and delayed-consumer witnesses."""
CASES = [
('array-name-keeps-selected-live-cell-and-delayed-rhs', b'''<?php
error_reporting(0);
class NameCell269{public static int $value=5;}
$GLOBALS['Array']=&NameCell269::$value;$key269=[5];$rhs269=7;
set_error_handler(function($n,$m){echo "C;";NameCell269::$value=13;$GLOBALS['rhs269']=17;$GLOBALS['key269']='chosen269';return false;},2);
$r=($GLOBALS[$key269]+=$rhs269);restore_error_handler();
echo "R:",$r,":",$GLOBALS['Array'],":",NameCell269::$value,":",$rhs269,":",$key269,";";
''', b'C;R:30:30:30:17:chosen269;'),
('missing-name-cv-rereads-caller-after-warning-for-rw', b'''<?php
error_reporting(0);
$GLOBALS['chosen269']=9;
set_error_handler(function($n,$m){echo "U;";$GLOBALS['key269']='chosen269';return false;},2);
$r=($GLOBALS[$key269]+=4);restore_error_handler();
echo "R:",$r,":",$GLOBALS['chosen269'],":",$key269,":",isset($GLOBALS[''])?1:0,";";
''', b'U;R:13:13:chosen269:0;'),
('multiline-array-name-before-missing-global-and-delayed-rhs', b'''<?php
error_reporting(0);
$key269=[5];$rhs269=7;$stage269=0;
set_error_handler(function($n,$m,$f,$l){$GLOBALS['stage269']++;echo $GLOBALS['stage269']===1?"C:":"G:",$l,";";if($GLOBALS['stage269']===1){$GLOBALS['key269']='chosen269';$GLOBALS['rhs269']=17;}else{$GLOBALS['Array']=37;}return false;},2);
$r=($GLOBALS[
    $key269
] += $rhs269);restore_error_handler();
echo "R:",$r,":",$GLOBALS['Array'],":",$rhs269,":",$key269,":",$stage269,";";
''', b'C:6;G:6;R:17:17:17:chosen269:2;'),
('eager-rhs-throw-precedes-global-array-name-conversion', b'''<?php
error_reporting(0);
class RhsCell269{public static int $value=9;public static int $dest=9;}
$cell269=&RhsCell269::$value;$older269=new Error('older');$error269=new Error('rhs',0,$older269);$original269=$error269;
function rhs269(){echo "S;";RhsCell269::$value=17;throw $GLOBALS['error269'];}
set_error_handler(function($n,$m){echo "WRONG;";return false;},2);
try{RhsCell269::$dest=($GLOBALS[[&$cell269]]+=rhs269());}catch(Error $e){echo "C:",$e===$original269?1:0,":",$e->getMessage(),":",$e->getPrevious()->getMessage(),";";}
restore_error_handler();echo "V:",$cell269,":",RhsCell269::$value,":",RhsCell269::$dest,";";
''', b'S;C:1:rhs:older;V:17:17:9;'),
('nested-global-rw-copy-abort-keeps-shared-typed-cell', b'''<?php
error_reporting(0);
class CopyCell269{public static int $value=9;}
$cell269=&CopyCell269::$value;$GLOBALS['box269']=[1=>&$cell269];$key269=1.5;
set_error_handler(function($n,$m){echo "H:",$n,";";$GLOBALS['held269']=$GLOBALS['box269'];CopyCell269::$value=17;$GLOBALS['key269']=7.5;return false;},8194);
$r=++$GLOBALS['box269'][$key269];restore_error_handler();
echo "R:",$r,":",$GLOBALS['box269'][1],":",$GLOBALS['held269'][1],":",CopyCell269::$value,":",$key269,";";
''', b'H:8192;R:1:17:17:17:7.5;'),
]
