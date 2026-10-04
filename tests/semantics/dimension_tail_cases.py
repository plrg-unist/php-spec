"""Original nested-unset/append witnesses for source and reached-state checks."""

CASES = [
    ('nested-unset-null-keeps-selected-parent-after-callback-cow', b'''<?php
error_reporting(0);$seed255=5;$a255=[''=>[1=>$seed255]];$key255=null;
function copyUnsetParent255($level,$message,$file,$line) {$GLOBALS['copy255']=$GLOBALS['a255'];$GLOBALS['a255']['']=[1=>17];$GLOBALS['key255']='changed';echo "D;";return false;}
set_error_handler('copyUnsetParent255',8192);unset($a255[$key255][1]);restore_error_handler();
echo "R:",$a255[''][1],":",isset($copy255[''][1])?1:0,":",$seed255,":",$key255,";";
''', b'D;R:17:0:5:changed;', 'normal'),
    ('nested-unset-final-copy-deletes-both-selected-rows-keeps-old-real-cell', b'''<?php
error_reporting(0);$cell255=5;$a255=['row'=>[1=>&$cell255]];$old255=$a255;$key255=1.5;
function copyUnsetChild255($level,$message,$file,$line) {$GLOBALS['child255']=$GLOBALS['a255']['row'];$GLOBALS['cell255']=17;echo "D;";return true;}
set_error_handler('copyUnsetChild255',8192);unset($a255['row'][$key255]);restore_error_handler();
echo "R:",isset($a255['row'][1])?1:0,":",isset($child255[1])?1:0,":",$old255['row'][1],":",$cell255,";";
''', b'D;R:0:0:17:17;', 'normal'),
    ('append-demands-mutated-rhs-cv-after-captured-float-key', b'''<?php
error_reporting(0);$seed255=5;$row255=[$seed255];$a255=[1=>&$row255];$key255=1.5;$rhs255=7;
function liveAppendRhs255($level,$message,$file,$line) {$GLOBALS['rhs255']=17;$GLOBALS['key255']=7.5;echo "D;";return true;}
set_error_handler('liveAppendRhs255',8192);$result255=($a255[$key255][]=$rhs255);restore_error_handler();
echo "R:",$result255,":",$a255[1][1],":",$row255[1],":",$key255,";";
''', b'D;R:17:17:17:7.5;', 'normal'),
    ('append-nan-tail-keeps-moved-parent-and-real-row', b'''<?php
error_reporting(0);$seed255=5;$row255=[$seed255];$a255=[0=>&$row255];$key255=NAN;
function moveAppendParent255($level,$message,$file,$line) {echo $level===2?"W;":"D;";if($level===2) {$GLOBALS['held255']=$GLOBALS['a255'];unset($GLOBALS['a255']);$GLOBALS['key255']=7.5;}return false;}
set_error_handler('moveAppendParent255',8194);$result255=($a255[$key255][]=17);restore_error_handler();
echo "R:",$result255,":",$held255[0][1],":",$row255[1],":",isset($a255)?1:0,":",$key255,";";
''', b'W;D;R:17:17:17:0:7.5;', 'normal'),
    ('append-conversion-throw-follows-rhs-keeps-typed-destination-chain', b'''<?php
error_reporting(0);class AppendDestination255 {public static int $value=9;}$destination255=&AppendDestination255::$value;
$seed255=5;$a255=[1=>[$seed255]];$key255=1.5;$older255=new Error('older');$pending255=new Error('handler',0,$older255);
function throwAppendKey255($level,$message,$file,$line) {echo "D;";$GLOBALS['held255']=$GLOBALS['a255'];unset($GLOBALS['a255'],$GLOBALS['key255'],$GLOBALS['older255']);throw $GLOBALS['pending255'];}
function computedAppendRhs255() {echo "S;";return 17;}
set_error_handler('throwAppendKey255',8192);
try {$destination255=($a255[$key255][]=computedAppendRhs255());} catch(Error $e) {$same255=$e===$pending255;unset($pending255);echo "C:",$same255?1:0,":",$destination255,":",$e->getMessage(),":",$e->getPrevious()->getMessage(),";";}
restore_error_handler();echo "V:",AppendDestination255::$value,";";
''', b'S;D;C:1:9:handler:older;V:9;', 'normal'),
]
