"""Original initial-CV container and array-reference-write discriminators."""
CASES = [
    ('undefined-w-initializes-before-key-u-and-latches-empty', b"""<?php
error_reporting(0);
set_error_handler(function($n,$m){if($n===2){echo "U:",isset($GLOBALS['a276'])?1:0,";";$GLOBALS['key276']=5;}else{echo "D;";}return false;},2|8192);
$r276=&$a276[$key276];
restore_error_handler();$before276=$r276===null;$r276=17;
echo "R:",$before276?1:0,":",$a276[''],":",$key276,":",isset($a276[5])?1:0,";";
""", b'U:1;D;R:1:17:5:0;'),
    ('undefined-rw-replaces-returning-handler-array', b"""<?php
error_reporting(0);$round276=0;$seed276=9;
set_error_handler(function($n,$m){$GLOBALS['round276']++;if($GLOBALS['round276']===1){echo "U;";$GLOBALS['a276']=[1=>$GLOBALS['seed276']];$GLOBALS['held276']=$GLOBALS['a276'];}else{echo "M;";}return false;},2);
$r276=++$a276[1];
restore_error_handler();echo "R:",$r276,":",$a276[1],":",$held276[1],":",$round276,";";
""", b'U;M;R:1:1:9:2;'),
    ('null-final-assign-rhs-before-key-and-quiet-no-init', b"""<?php
error_reporting(0);$a276=null;$null276=null;$other276=null;$key276=1.5;
function rhs276(){echo "S;";return 7;}
set_error_handler(function($n,$m){echo "D:",isset($GLOBALS['a276'])?1:0,";";$GLOBALS['key276']=7.5;return false;},8192);
$q276=isset($null276[1.5]);$v276=$other276[1.5]??17;
$r276=($a276[$key276]=rhs276());
restore_error_handler();echo "R:",$r276,":",$a276[1],":",$key276,":",isset($a276[7])?1:0,";Q:",$q276?1:0,":",$v276,":",($null276===null&&$other276===null)?1:0,";";
""", b'S;D:1;R:7:7:7.5:0;Q:0:17:1;'),
    ('false-fetch-reads-live-key-after-base-warning', b"""<?php
error_reporting(0);$a276=false;$key276=1.5;$round276=0;
set_error_handler(function($n,$m){$GLOBALS['round276']++;if($m[0]==='A'){echo "F:",isset($GLOBALS['a276'])?1:0,";";$GLOBALS['key276']=2.5;}else{echo "D;";$GLOBALS['key276']=7.5;}return false;},8192);
$r276=&$a276[$key276];
restore_error_handler();$before276=$r276===null;$r276=19;echo "R:",$before276?1:0,":",$a276[2],":",$key276,":",isset($a276[1])?1:0,":",$round276,";";
""", b'F:1;D;R:1:19:7.5:0:2;'),
    ('typed-array-false-wrapper-fetch-and-final-warning', b"""<?php
error_reporting(0);
class ArrayHolder276{public static array|false $value=false;}
$a276=&ArrayHolder276::$value;$alias276=&$a276;
set_error_handler(function($n,$m){echo "F;";return false;},8192);
$r276=&$a276[0];$r276=17;echo "T:",ArrayHolder276::$value[0],":",$alias276[0],":",$r276,";";
$a276=false;$a276[0]=19;
restore_error_handler();echo "R:",ArrayHolder276::$value[0],":",$alias276[0],":",$r276,";";
""", b'T:17:17:17;F;R:19:19:17;'),
    ('false-fetch-before-ordered-nan-key-notices', b"""<?php
error_reporting(0);$a276=false;$key276=NAN;
set_error_handler(function($n,$m){if($n===2){echo "W;";$GLOBALS['key276']=7.5;}elseif($m[0]==='A'){echo "F;";}else{echo "D;";}return false;},2|8192);
$r276=&$a276[$key276];
restore_error_handler();$before276=$r276===null;$r276=19;echo "R:",$before276?1:0,":",$a276[0],":",$key276,";";
""", b'F;W;D;R:1:19:7.5;'),
    ('reference-target-key-before-delayed-source-cv', b"""<?php
error_reporting(0);$a276=null;$source276=9;$alias276=&$source276;$key276=1.5;
set_error_handler(function($n,$m){echo "D;";unset($GLOBALS['source276']);$GLOBALS['source276']=17;$GLOBALS['key276']=7.5;return false;},8192);
$a276[$key276]=&$source276;
restore_error_handler();echo "R:",$source276,":",$alias276,":",$a276[1],":",$key276,";";$source276=19;echo "V:",$a276[1],":",$alias276,":",isset($a276[7])?1:0,";";
""", b'D;R:17:9:17:7.5;V:19:9:0;'),
]
