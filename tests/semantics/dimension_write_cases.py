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
    ('constant-null-compound-abort-skips-delayed-rhs-cv-demand', b'''<?php
error_reporting(0);$seed242=5;$a242=[''=>$seed242];
function abortConstant242($level,$message,$file,$line) {$GLOBALS['held242']=$GLOBALS['a242'];echo $level===8192?"D;":"U;";return true;}
set_error_handler('abortConstant242',8194);$result242=($a242[null]+=$missingRhs242);
echo "R:",$result242===null?1:0,":",$a242[''],":",$held242[''],":",isset($missingRhs242)?1:0,";";restore_error_handler();
''', b'D;R:1:5:5:0;', 'normal'),
    ('dormant-handler-preserves-defined-global-rw-route', b'''<?php
error_reporting(0);$counter242=5;
function dormantGlobal242($level,$message,$file,$line) {echo "H;";return true;}
set_error_handler('dormantGlobal242',8194);$first242=++$GLOBALS['counter242'];$second242=($GLOBALS['counter242']+=7);
echo "G:",$first242,":",$second242,":",$counter242,";";restore_error_handler();
''', b'G:6:13:13;', 'normal'),
    ('dormant-handler-preserves-nested-string-terminal-consumers', b'''<?php
error_reporting(0);$seed242='ab';$a242=['row'=>$seed242];
function dormantString242($level,$message,$file,$line) {echo "H;";return true;}
set_error_handler('dormantString242',8194);$result242=($a242['row'][0]='z');
echo "S:",$result242,":",$a242['row'],";";
try {$ref242=&$a242['row'][0];} catch(Error $e) {echo "F:",$e->getMessage(),";";}
try {$a242['row'][0]+=1;} catch(Error $e) {echo "C:",$e->getMessage(),";";}
try {++$a242['row'][0];} catch(Error $e) {echo "I:",$e->getMessage(),";";}
restore_error_handler();
''', b'S:z:zb;F:Cannot create references to/from string offsets;C:Cannot use assign-op operators with string offsets;I:Cannot increment/decrement string offsets;', 'normal'),
    ('named-reference-retains-selected-callable-and-earlier-array', b'''<?php
error_reporting(0);$seed242=5;$earlier242=[&$seed242];$start242=7;$a242=[1=>$start242];$key242=1.5;
function namedTarget242($earlier,&$ref) {echo "C:",$earlier[0],":",$ref,";";$ref=19;}
$callee242=namedTarget242(...);
function keepNamed242($level,$message,$file,$line) {
    $GLOBALS['seed242']=17;$GLOBALS['key242']=7.5;unset($GLOBALS['callee242'],$GLOBALS['earlier242'],$GLOBALS['seed242']);echo "D;";return false;
}
set_error_handler('keepNamed242',8192);$callee242(earlier:$earlier242,ref:$a242[$key242]);restore_error_handler();
echo "R:",$a242[1],":",$key242,":",isset($callee242)?1:0,":",isset($earlier242)?1:0,":",isset($seed242)?1:0,";";
''', b'D;C:17:7;R:19:7.5:0:0:0;', 'normal'),
]
