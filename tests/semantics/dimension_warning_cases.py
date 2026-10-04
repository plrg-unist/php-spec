"""Selected key/base ordering, quiet demand and genuine temporary ownership."""

# ID, original source, predicted stdout, status.
CASES = [
    ('global-array-name-conversion-keeps-selected-name', b'''<?php
error_reporting(0);$cell233=3;$key233=[&$cell233];$copy233=$key233;$Array=5;$other233=7;
function nameHandler233($level,$message,$file,$line) {
    $GLOBALS['key233']='other233';$GLOBALS['Array']=17;$GLOBALS['cell233']=19;
    echo "A:",$message==='Array to string conversion'?1:0,":",$file===__FILE__?1:0,":",$line===8?1:0,";";
    return true;
}
set_error_handler('nameHandler233',2);$result233=$GLOBALS[$key233];
echo "R:",$result233,":",$key233,":",$copy233[0],";";restore_error_handler();
''', b'A:1:1:1;R:17:other233:19;', 'normal'),
    ('array-null-conversion-retains-shared-old-table', b'''<?php
error_reporting(0);$seed233=5;$a233=[''=>$seed233];$saved233=$a233;$key233=null;
function nullHandler233($level,$message,$file,$line) {
    $GLOBALS['a233']['']=17;$GLOBALS['key233']='changed';
    echo "D:",$level===8192?1:0,";";return true;
}
set_error_handler('nullHandler233',8192);$result233=$a233[$key233];
echo "R:",$result233,":",$a233[''],":",$saved233[''],":",$key233,";";restore_error_handler();
''', b'D:1;R:5:17:5:changed;', 'normal'),
    ('array-null-conversion-releases-sole-protection', b'''<?php
error_reporting(0);$seed233=5;$a233=[''=>$seed233];$key233=null;
function soleHandler233($level,$message,$file,$line) {
    $GLOBALS['a233']['']=17;echo "D;";return true;
}
set_error_handler('soleHandler233',8192);$result233=$a233[$key233];
echo "R:",$result233===null?1:0,":",$a233[''],";";restore_error_handler();
''', b'D;R:1:17;', 'normal'),
    ('isset-undefined-key-has-no-first-protection', b'''<?php
error_reporting(0);$seed233=5;$a233=[''=>$seed233];
function issetHandler233($level,$message,$file,$line) {
    if($level===2) {$GLOBALS['a233']['']=17;$GLOBALS['missingKey233']='changed';echo "U;";}
    else {echo "D;";}
    return true;
}
set_error_handler('issetHandler233',8194);$result233=isset($a233[$missingKey233]);
echo "I:",$result233?1:0,":",$a233[''],":",$missingKey233,";";restore_error_handler();
''', b'U;D;I:1:17:changed;', 'normal'),
    ('nested-key-cast-retains-original-null', b'''<?php
error_reporting(0);${''}=17;$chosen233=19;
function castKey233($level,$message,$file,$line) {
    $GLOBALS['missingCast233']='chosen233';echo "U;";return false;
}
set_error_handler('castKey233',2);$result233=$GLOBALS[(string)$missingCast233];
echo "C:",$result233,":",$missingCast233,";";restore_error_handler();
''', b'U;C:17:chosen233;', 'normal'),
    ('global-conversion-throw-releases-real-key-temporary', b'''<?php
error_reporting(0);$cell233=23;$retained233=&$cell233;$destination233=9;
$older233=new Error('older');$pending233=new Error('handler',0,$older233);
function keyFactory233(&$cell) {return [&$cell];}
function throwKey233($level,$message,$file,$line) {
    unset($GLOBALS['cell233'],$GLOBALS['older233']);$GLOBALS['retained233']=37;
    throw $GLOBALS['pending233'];
}
set_error_handler('throwKey233',2);
try {$destination233=$GLOBALS[keyFactory233($cell233)];} catch(Error $e) {
    unset($pending233);
    echo "T:",$destination233,":",$retained233,":",$e->getMessage(),":",$e->getPrevious()->getMessage(),";";
}
restore_error_handler();
''', b'T:9:37:handler:older;', 'normal'),
    ('constant-null-conversion-then-missing-keeps-captured-null', b'''<?php
error_reporting(0);$seed233=5;$a233=['live'=>$seed233];$keep233=$a233;
function missingAfterCast233($level,$message,$file,$line) {
    if($level===8192) {$GLOBALS['a233']['']=17;echo "D;";}
    else {$GLOBALS['keep233']['']=31;echo "U:",$message==='Undefined array key ""'?1:0,";";}
    return true;
}
set_error_handler('missingAfterCast233',8194);$result233=$a233[null];
echo "R:",$result233===null?1:0,":",$a233[''],":",$keep233[''],";";restore_error_handler();
''', b'D;U:1;R:1:17:31;', 'normal'),
    # Exact independent native originals; only their new model checks are run.
    ('nan-conversion-keeps-protection-across-both-notices', b'''<?php
error_reporting(0);$seed233=5;$a233=[0=>$seed233];$key233=NAN;
function nanKey233($level,$message,$file,$line) {
    if($level===2) {$GLOBALS['a233'][0]=17;$GLOBALS['key233']=7.5;echo "W:",$message==='The float NAN is not representable as an int, cast occurred'?1:0,":",$line===7?1:0,";";return false;}
    $GLOBALS['a233'][0]=23;echo "D:",$message==='Implicit conversion from float NAN to int loses precision'?1:0,":",$line===7?1:0,";";return true;
}
set_error_handler('nanKey233',8194);$read233=$a233[$key233];
echo "R:",$read233===null?1:0,":",$a233[0],":",$key233,";";restore_error_handler();
''', b'W:1:1;D:1:1;R:1:23:7.5;', 'normal'),
    ('nan-first-notice-throw-preserves-priority-and-destination', b'''<?php
error_reporting(0);$seed233=5;$a233=[0=>$seed233];$key233=NAN;
class NanDestination233 {public static int $value=9;}$destination233=&NanDestination233::$value;
$older233=new Error('older');$pending233=new Error('handler',0,$older233);
function throwNan233($level,$message,$file,$line) {
    if($level===2) {echo "W;";unset($GLOBALS['a233'],$GLOBALS['key233'],$GLOBALS['older233']);throw $GLOBALS['pending233'];}
    echo "D;";return true;
}
set_error_handler('throwNan233',8194);
try {$destination233=$a233[$key233];} catch(Error $e) {
    echo "C:",$destination233,":",$e===$pending233?1:0,":";unset($pending233);
    echo $e->getMessage(),":",$e->getPrevious()->getMessage(),";";
}
restore_error_handler();
''', b'W;C:9:1:handler:older;', 'normal'),
]
