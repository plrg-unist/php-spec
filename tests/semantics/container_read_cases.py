"""Original R-container and scalar-offset warning discriminators."""
CASES = [
    ('missing-base-definition-does-not-refetch-array', b"""<?php
error_reporting(0);
set_error_handler(function($n,$m){if($m==='Undefined variable $base282'){echo "B;";$GLOBALS['base282']=[0=>17];}else{echo "O:",$m==='Trying to access array offset on null'?1:0,";";}return false;},2);
$r282=$base282[0];
restore_error_handler();echo "R:",$r282===null?1:0,":",$base282[0],";";
""", b'B;O:1;R:1:17;'),
    ('scalar-offset-types-ignore-key-conversions-with-false-fallback', b"""<?php
error_reporting(0);$null282=null;$false282=false;$int282=13;$float282=1.5;$key282=[];
set_error_handler(function($n,$m){echo $m==='Trying to access array offset on null'?"N;":($m==='Trying to access array offset on false'?"F;":($m==='Trying to access array offset on int'?"I;":($m==='Trying to access array offset on float'?"D;":"WRONG;")));return false;},2|8192);
$n282=$null282[1.5];$f282=$false282[null];$i282=$int282[$key282];$d282=$float282[0];
restore_error_handler();echo "R:",($n282===null&&$f282===null&&$i282===null&&$d282===null)?1:0,";";
""", b'N;F;I;D;R:1;'),
    ('nested-missing-base-retains-null-for-both-fetches', b"""<?php
error_reporting(0);$round282=0;
set_error_handler(function($n,$m){$GLOBALS['round282']++;if($m==='Undefined variable $base282'){echo "B;";$GLOBALS['base282']=[[17]];}else{echo "O:",$m==='Trying to access array offset on null'?1:0,";";}return false;},2);
$r282=$base282[0][0];
restore_error_handler();echo "R:",$r282===null?1:0,":",$base282[0][0],":",$round282,";";
""", b'B;O:1;O:1;R:1:17:3;'),
    ('nested-scalar-row-is-dereferenced-before-key-warning', b"""<?php
error_reporting(0);$cell282=9;$a282=[&$cell282];$held282=$a282;
set_error_handler(function($n,$m){if($m==='Undefined variable $key282'){echo "K;";$GLOBALS['cell282']=false;$GLOBALS['a282']=[[''=>13]];$GLOBALS['key282']=0;}else{echo "O:",$m==='Trying to access array offset on int'?1:0,";";}return false;},2);
$r282=$a282[0][$key282];
restore_error_handler();echo "R:",$r282===null?1:0,":",$cell282===false?1:0,":",$held282[0]===false?1:0,":",$a282[0][''],";";
""", b'K;O:1;R:1:1:1:13;'),
    ('computed-scalar-base-is-owned-value-before-key-warning', b"""<?php
error_reporting(0);$other282=9;
function scalar282(){echo "S;";return 13;}
set_error_handler(function($n,$m){if($m==='Undefined variable $key282'){echo "K;";$GLOBALS['key282']=0;$GLOBALS['other282']='ab';}else{echo "O:",$m==='Trying to access array offset on int'?1:0,";";}return false;},2);
$r282=scalar282()[$key282];
restore_error_handler();echo "R:",$r282===null?1:0,":",$other282,";";
""", b'S;K;O:1;R:1:ab;'),
    ('quiet-missing-bases-skip-base-and-offset-key-conversions', b"""<?php
error_reporting(0);
set_error_handler(function($n,$m){echo "WRONG;";return false;},2|8192);
$i282=isset($missingI282[null]);$e282=empty($missingE282[1.5]);$c282=$missingC282[[]]??17;
restore_error_handler();echo "Q:",$i282?1:0,":",$e282?1:0,":",$c282,":",isset($missingI282)?1:0,":",isset($missingE282)?1:0,":",isset($missingC282)?1:0,";";
""", b'Q:0:1:17:0:0:0;'),
]

# A genuine evaluated key operand keeps its real reference cell during Warning.
CASES.append(('scalar-offset-retains-real-key-temporary-through-handler', b"""<?php
error_reporting(0);$cell282=9;$held282=&$cell282;$scalar282=13;
set_error_handler(function($n,$m){echo "O:",$m==='Trying to access array offset on int'?1:0,";";unset($GLOBALS['cell282'],$GLOBALS['held282']);return false;},2);
$r282=$scalar282[[&$cell282]];
restore_error_handler();echo "R:",$r282===null?1:0,":",isset($cell282)?1:0,":",isset($held282)?1:0,";";
""", b'O:1;R:1:0:0;'))
