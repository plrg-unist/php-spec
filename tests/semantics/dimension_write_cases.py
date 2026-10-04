"""Writable key conversion, real cells and acquisition priority originals."""

CASES = [
    ('undefined-key-reference-keeps-empty-key-after-two-notices', b'''<?php
error_reporting(0);$seed242=5;$a242=[''=>$seed242];
function defineKey242($level,$message,$file,$line) {
    if($level===2) {$GLOBALS['key242']='changed';echo "U;";} else {echo "D;";}
    return true;
}
set_error_handler('defineKey242',8194);$ref242=&$a242[$key242];$ref242=17;
echo "R:",$a242[''],":",$key242,":",$ref242,";";restore_error_handler();
''', b'U;D;R:17:changed:17;', 'normal'),
    ('null-key-reference-separates-before-conversion', b'''<?php
error_reporting(0);$seed242=5;$a242=[''=>$seed242];$old242=$a242;$key242=null;
function nullKey242($level,$message,$file,$line) {$GLOBALS['key242']='changed';echo "D;";return true;}
set_error_handler('nullKey242',8192);$ref242=&$a242[$key242];$ref242=17;
echo "R:",$a242[''],":",$old242[''],":",$key242,":",$ref242,";";restore_error_handler();
''', b'D;R:17:5:changed:17;', 'normal'),
    ('float-key-reference-keeps-live-shared-element-cell', b'''<?php
error_reporting(0);$cell242=5;$a242=[1=>&$cell242];$old242=$a242;$key242=1.5;
function floatKey242($level,$message,$file,$line) {$GLOBALS['cell242']=17;$GLOBALS['key242']=7.5;echo "D;";return false;}
set_error_handler('floatKey242',8192);$ref242=&$a242[$key242];$before242=$ref242;$ref242=19;
echo "R:",$before242,":",$a242[1],":",$old242[1],":",$cell242,":",$key242,";";restore_error_handler();
''', b'D;R:17:19:19:19:7.5;', 'normal'),
    ('nan-key-reference-keeps-protection-and-real-cell-through-tail', b'''<?php
error_reporting(0);$cell242=5;$a242=[&$cell242];$old242=$a242;$key242=NAN;
function nanWrite242($level,$message,$file,$line) {
    if($level===2) {$GLOBALS['cell242']=17;$GLOBALS['key242']=7.5;echo "W;";return false;}
    $GLOBALS['cell242']=19;echo "D;";return true;
}
set_error_handler('nanWrite242',8194);$ref242=&$a242[$key242];$before242=$ref242;$ref242=23;
echo "R:",$before242,":",$a242[0],":",$old242[0],":",$cell242,":",$key242,";";restore_error_handler();
''', b'W;D;R:19:23:23:23:7.5;', 'normal'),
    ('nan-first-notice-throw-keeps-old-typed-destination-binding', b'''<?php
error_reporting(0);$seed242=5;$a242=[0=>$seed242];$key242=NAN;
class NanDestination242 {public static int $value=9;}$destination242=&NanDestination242::$value;
$older242=new Error('older');$pending242=new Error('handler',0,$older242);
function throwNanWrite242($level,$message,$file,$line) {
    if($level===2) {echo "W;";unset($GLOBALS['a242'],$GLOBALS['key242'],$GLOBALS['older242']);throw $GLOBALS['pending242'];}
    echo "D;";return true;
}
set_error_handler('throwNanWrite242',8194);
try {$destination242=&$a242[$key242];} catch(Error $e) {
    echo "C:",$destination242,":",$e===$pending242?1:0,":";unset($pending242);$destination242=19;
    echo NanDestination242::$value,":",$e->getMessage(),":",$e->getPrevious()->getMessage(),";";
}
restore_error_handler();
''', b'W;C:9:1:19:handler:older;', 'normal'),
]
