"""Direct global fetch warnings and genuine request-table ownership witnesses."""

# ID, original source, predicted stdout, status, explicit request facts required.
CASES = [
    ('computed-name-is-captured-before-handler-rebind', b'''<?php
error_reporting(0);$key226='missing226';$other226=7;$hits226=0;
function handler226($level,$message,$file,$line) {
    $GLOBALS['key226']='other226';
    $GLOBALS['missing226'] =& $GLOBALS['other226'];
    $GLOBALS['hits226']=$GLOBALS['hits226']+1;
    echo "H:",$message==='Undefined global variable $missing226'?1:0,":",$file===__FILE__?1:0,":",$line===10?1:0,";";
    return true;
}
set_error_handler('handler226',2);$result226=$GLOBALS[$key226];
echo "R:",$result226===null?1:0,":",$missing226,":",$key226,":",$hits226,";";
restore_error_handler();
''', b'H:1:1:1;R:1:7:other226:1;', 'normal', False),
    ('returned-handler-null-rejects-live-typed-destination', b'''<?php
error_reporting(0);
class Returned226 {public static int $slot=9;}
$dst226 =& Returned226::$slot;
function returned226($level,$message,$file,$line) {
    $GLOBALS['missing226']=13;echo "H;";return true;
}
set_error_handler('returned226',2);
try {$dst226=$GLOBALS['missing226'];echo "BAD;";} catch(TypeError $e) {
    echo "C:",$dst226,":",$missing226,":",$e->getPrevious()===null?1:0,";";
}
restore_error_handler();
''', b'H;C:9:13:1;', 'normal', False),
    ('global-fetch-precedes-duplicate-named-slot-error', b'''<?php
error_reporting(0);$hits226=0;
function named226($value) {echo "BAD;";}
function namedHandler226($level,$message,$file,$line) {
    $GLOBALS['hits226']=$GLOBALS['hits226']+1;
    $GLOBALS['missing226']=17;echo "H;";return true;
}
set_error_handler('namedHandler226',2);$target226='named226';
try {$target226(value:1,value:$GLOBALS['missing226']);} catch(Error $e) {
    echo "N:",$e->getMessage()==='Named parameter $value overwrites previous argument'?1:0,":",$hits226,":",$missing226,";";
}
restore_error_handler();
''', b'H;N:1:1:17;', 'normal', False),
    ('false-fallback-and-missing-coalesce-have-distinct-demand', b'''<?php
error_reporting(0);$hits226=0;
function false226($level,$message,$file,$line) {
    $GLOBALS['hits226']=$GLOBALS['hits226']+1;
    $GLOBALS['missing226']=19;echo "H;";return false;
}
set_error_handler('false226',2);
$quiet226=$GLOBALS['quiet226']??23;
$read226=(array)$GLOBALS['missing226'];
echo "F:",$quiet226,":",count($read226),":",$missing226,":",$hits226,";";
restore_error_handler();
''', b'H;F:23:0:19:1;', 'normal', False),
    ('global-reference-bind-survives-snapshot-free-call', b'''<?php
error_reporting(0);$hits226=0;
function bind226(&$first,&$second) {$first=29;echo "B:",$second,";";}
function quietHandler226($level,$message,$file,$line) {$GLOBALS['hits226']=$GLOBALS['hits226']+1;return true;}
set_error_handler('quietHandler226',2);
bind226(second:$GLOBALS['fresh226'],first:$GLOBALS['fresh226']);
$alias226 =& $GLOBALS['fresh226'];unset($fresh226);$alias226=31;
echo "A:",$alias226,":",$GLOBALS['fresh226']??'gone',":",$hits226,";";
restore_error_handler();
''', b'B:29;A:31:gone:0;', 'normal', False),
    ('throw-skips-assignment-and-retires-selected-caller', b'''<?php
error_reporting(0);$destination226=37;$older226=new Error('older');
$pending226=new Error('handler',0,$older226);
function throw226($level,$message,$file,$line) {
    $GLOBALS['missing226']=41;
    unset($GLOBALS['pending226'],$GLOBALS['older226']);
    throw $GLOBALS['held226'];
}
$held226=$pending226;set_error_handler('throw226',2);
try {$destination226=$GLOBALS['missing226'];} catch(Error $caught226) {
    unset($held226);
    echo "T:",$destination226,":",$missing226,":",$caught226->getMessage(),":",$caught226->getPrevious()->getMessage(),";";
}
restore_error_handler();
''', b'T:37:41:handler:older;', 'normal', False),
    ('snapshot-numeric-keys-cow-and-retained-reference-cell', b'''<?php
${'12'}=2;${'012'}=3;$n226=[4];$r226=&${'12'};
$single226=5;$alias226=&$single226;unset($alias226);
$snapshot226=$GLOBALS;$copy226=$snapshot226;
${'12'}=7;$n226[0]=8;
$snapshot226[12]=9;$snapshot226['012']=10;$snapshot226['n226'][0]=11;$snapshot226['single226']=13;
echo "S:",${'12'},":",${'012'},":",$copy226[12],":",$copy226['012'],":",$n226[0],":",$snapshot226['n226'][0],":",$copy226['n226'][0],":",$single226,":",$copy226['single226'],";";
unset($r226,${'12'},$snapshot226);
$copy226[12]=17;echo "L:",$copy226[12],":",$copy226['single226'],";";
''', b'S:9:3:9:3:8:11:4:5:5;L:17:5;', 'normal', True),
    ('handler-full-table-snapshot-retains-owners-through-rebind', b'''<?php
error_reporting(0);$root226=2;$alias226=&$root226;$array226=[3];
if(false){$undefined226=1;}
function snapshotHandler226($level,$message,$file,$line) {
    $local226=5;$GLOBALS['created226']=7;
    $GLOBALS['table226']=$GLOBALS;
    $GLOBALS['root226']=11;$GLOBALS['array226'][0]=13;
    unset($GLOBALS['root226'],$GLOBALS['alias226']);
    $GLOBALS['root226']=17;return true;
}
set_error_handler('snapshotHandler226',2);
$result226=$GLOBALS['missing226'];
echo "H:",$result226===null?1:0,":",$table226['root226'],":",$root226,":",$table226['array226'][0],":",$array226[0],":",$table226['created226'],":",$table226['local226']??'L',":",$table226['undefined226']??'U',":",$table226['result226']??'R',";";
$table226['alias226']=19;echo "C:",$table226['root226'],":",$root226,";";
restore_error_handler();
''', b'H:1:11:17:3:13:7:L:U:R;C:19:17;', 'normal', True),
]
