"""Ordinary null cast/copy/SEND producers and direct ASSIGN exception timing."""
CASES = [
    ('cast-array-through-callback-created-alias', b'''<?php
error_reporting(0);
$other213=9;
set_error_handler(function($level,$message,$file,$line) {
    $GLOBALS['missing213'] =& $GLOBALS['other213'];
    echo "H",func_num_args(),";";
    return true;
},2);
$missing213=(array)$missing213; echo $missing213===[] && $other213===[]?"A;":"BAD;";
restore_error_handler();
''', b'H4;A;', 'normal'),
    ('cast-bool-through-callback-created-alias', b'''<?php
error_reporting(0);
$other213=9;
set_error_handler(function($level,$message,$file,$line) {
    $GLOBALS['missing213'] =& $GLOBALS['other213'];
    echo "H",func_num_args(),";";
    return true;
},2);
$missing213=(bool)$missing213; echo $missing213===false && $other213===false?"B;":"BAD;";
restore_error_handler();
''', b'H4;B;', 'normal'),
    ('cast-int-through-callback-created-alias', b'''<?php
error_reporting(0);
$other213=9;
set_error_handler(function($level,$message,$file,$line) {
    $GLOBALS['missing213'] =& $GLOBALS['other213'];
    echo "H",func_num_args(),";";
    return true;
},2);
$missing213=(int)$missing213; echo $missing213===0 && $other213===0?"I;":"BAD;";
restore_error_handler();
''', b'H4;I;', 'normal'),
    ('cast-float-through-callback-created-alias', b'''<?php
error_reporting(0);
$other213=9;
set_error_handler(function($level,$message,$file,$line) {
    $GLOBALS['missing213'] =& $GLOBALS['other213'];
    echo "H",func_num_args(),";";
    return true;
},2);
$missing213=(float)$missing213; echo $missing213===0.0 && $other213===0.0?"D;":"BAD;";
restore_error_handler();
''', b'H4;D;', 'normal'),
    ('cast-string-through-callback-created-alias', b'''<?php
error_reporting(0);
$other213=9;
set_error_handler(function($level,$message,$file,$line) {
    $GLOBALS['missing213'] =& $GLOBALS['other213'];
    echo "H",func_num_args(),";";
    return true;
},2);
$missing213=(string)$missing213; echo $missing213==='' && $other213===''?"S;":"BAD;";
restore_error_handler();
''', b'H4;S;', 'normal'),
    ('cast-object-through-callback-created-alias', b'''<?php
error_reporting(0);
$other213=9;
set_error_handler(function($level,$message,$file,$line) {
    $GLOBALS['missing213'] =& $GLOBALS['other213'];
    echo "H",func_num_args(),";";
    return true;
},2);
$missing213=(object)$missing213; echo $missing213 instanceof stdClass && $missing213===$other213?"O;":"BAD;";
restore_error_handler();
''', b'H4;O;', 'normal'),
    ('selected-copy-folded-true-null', b'''<?php
error_reporting(0);
$right213=8;
set_error_handler(function($level,$message,$file,$line) {
    $GLOBALS['left213']=9;
    echo "H",func_num_args(),";";
    return true;
},2);
$copy213=true ? $left213 : $right213; echo $copy213===null?"N:":"BAD:",$left213,";";
restore_error_handler();
''', b'H4;N:9;', 'normal'),
    ('selected-copy-folded-false-null', b'''<?php
error_reporting(0);
$right213=8;
set_error_handler(function($level,$message,$file,$line) {
    $GLOBALS['left213']=9;
    echo "H",func_num_args(),";";
    return true;
},2);
$copy213=false ? $right213 : $left213; echo $copy213===null?"N:":"BAD:",$left213,";";
restore_error_handler();
''', b'H4;N:9;', 'normal'),
    ('selected-copy-runtime-true-null', b'''<?php
error_reporting(0);
$right213=8;
set_error_handler(function($level,$message,$file,$line) {
    $GLOBALS['left213']=9;
    echo "H",func_num_args(),";";
    return true;
},2);
$condition213=true;
$copy213=$condition213 ? $left213 : $right213; echo $copy213===null?"N:":"BAD:",$left213,";";
restore_error_handler();
''', b'H4;N:9;', 'normal'),
    ('selected-copy-coalesce-null', b'''<?php
error_reporting(0);
$right213=8;
set_error_handler(function($level,$message,$file,$line) {
    $GLOBALS['left213']=9;
    echo "H",func_num_args(),";";
    return true;
},2);
$copy213=null ?? $left213; echo $copy213===null?"N:":"BAD:",$left213,";";
restore_error_handler();
''', b'H4;N:9;', 'normal'),
    ('selected-copy-shorthand-null', b'''<?php
error_reporting(0);
$right213=8;
set_error_handler(function($level,$message,$file,$line) {
    $GLOBALS['left213']=9;
    echo "H",func_num_args(),";";
    return true;
},2);
$copy213=false ?: $left213; echo $copy213===null?"N:":"BAD:",$left213,";";
restore_error_handler();
''', b'H4;N:9;', 'normal'),
    ('selected-copy-throw-preserves-destination', b'''<?php
error_reporting(0);
$right213=8;
$copy213='old';
$throw213=function($level,$message,$file,$line) {
    $GLOBALS['left213']=9;
    $GLOBALS['copy213']='handler';
    echo "T",func_num_args(),";";
    throw new Error('copy');
};
set_error_handler($throw213,2);
try {$copy213=true ? $left213 : $right213;} catch(Error $e) {
    echo "C:",$copy213,":",$left213,":",get_error_handler()===$throw213?1:0,";";
}
restore_error_handler();
''', b'T4;C:handler:9:1;', 'normal'),
    ('positional-send-retains-closure-and-array', b'''<?php
error_reporting(0);
$seed213=[]; $seed213[]=1;
$callee213=function($snapshot,$value) {
    echo "S",func_num_args(),":",$snapshot[0],":",isset($snapshot[1])?"BAD":"C",":",$value===null?"N":"BAD",";";
};
set_error_handler(function($level,$message,$file,$line) {
    $GLOBALS['missing213']=9;
    $GLOBALS['seed213'][]=2;
    $GLOBALS['callee213']=null;
    echo "H",func_num_args(),";";
    return true;
},2);
$callee213($seed213,$missing213);
echo $seed213[1],":",$missing213,":",$callee213===null?1:0,";";
restore_error_handler();
''', b'H4;S2:1:C:N;2:9:1;', 'normal'),
    ('named-send-holes-and-extra-value', b'''<?php
error_reporting(0);
function sink213($first=3,$second=4,...$extra) {
    echo $first,":",$second===null?"N":$second,":",isset($extra['third'])?"BAD":(isset($extra[0])?"BAD":"V"),";";
    if ($extra!==[]) echo $extra['third']===null?"N;":"BAD;";
}
set_error_handler(function($level,$message,$file,$line) {
    $GLOBALS['missing213']=9;
    echo "H",func_num_args(),";";
    return true;
},2);
sink213(second:$missing213);
unset($missing213);
sink213(third:$missing213,second:7,first:1);
echo $missing213,";";
restore_error_handler();
''', b'H4;3:N:V;H4;1:7:V;N;9;', 'normal'),
    ('explicit-send-after-unpack-and-throw', b'''<?php
error_reporting(0);
function sink213($first,$second) {echo "S",func_num_args(),":",$first,":",$second===null?"N":"BAD",";";}
set_error_handler(function($level,$message,$file,$line) {
    $GLOBALS['missing213']=9; echo "H",func_num_args(),";"; return true;
},2);
sink213(...[7],second:$missing213);
restore_error_handler(); unset($missing213);
$throw213=function($level,$message,$file,$line) {
    $GLOBALS['missing213']=9; echo "T",func_num_args(),";"; throw new Error('send');
};
set_error_handler($throw213,2);
try {sink213(...[7],second:$missing213);} catch(Error $e) {
    echo "C:",$missing213,":",get_error_handler()===$throw213?1:0,";";
}
restore_error_handler();
''', b'H4;S2:7:N;T4;C:9:1;', 'normal'),
    ('named-slot-errors-before-cv-warning', b'''<?php
error_reporting(0); $hits213=0;
function sink213($first) {echo "BAD;";}
set_error_handler(function($level,$message,$file,$line) {$GLOBALS['hits213']=$GLOBALS['hits213']+1; return true;},2);
try {sink213(other:$missing213);} catch(Error $e) {echo $e->getMessage()==='Unknown named parameter $other'?"U;":"BAD;";}
try {sink213(first:1,first:$missing213);} catch(Error $e) {echo $e->getMessage()==='Named parameter $first overwrites previous argument'?"D;":"BAD;";}
echo $hits213,":",isset($missing213)?1:0,";";
restore_error_handler();
''', b'U;D;0:0;', 'normal'),
    ('direct-assign-null-through-alias-on-throw', b'''<?php
error_reporting(0); $alias213='old'; $destination213 =& $alias213;
$throw213=function($level,$message,$file,$line) {
    $GLOBALS['missing213']=9; $GLOBALS['destination213']='handler';
    echo "T",func_num_args(),";"; throw new Error('assign');
};
set_error_handler($throw213,2);
try {$destination213=$missing213;} catch(Error $e) {
    echo $destination213===null?"N":"BAD",":",$alias213===null?"N":"BAD",":",$missing213,":",get_error_handler()===$throw213?1:0,";";
}
restore_error_handler();
''', b'T4;N:N:9:1;', 'normal'),
    ('direct-assign-nullable-typed-alias-on-throw', b'''<?php
error_reporting(0);
class Slot213 {public static ?int $value=3;}
$destination213 =& Slot213::$value;
$throw213=function($level,$message,$file,$line) {
    $GLOBALS['missing213']=9; $GLOBALS['destination213']=7;
    echo "T",func_num_args(),";"; throw new Error('assign');
};
set_error_handler($throw213,2);
try {$destination213=$missing213;} catch(Error $e) {
    echo Slot213::$value===null?"N":"BAD",":",$destination213===null?"N":"BAD",":",get_error_handler()===$throw213?1:0,";";
}
restore_error_handler();
''', b'T4;N:N:1;', 'normal'),
    ('strict-handler-receive-still-writes-null', b'''<?php
declare(strict_types=1);
error_reporting(0);
function handler213(string $level,$message,$file,$line) {echo "BAD;";}
set_error_handler('handler213',2); $destination213='old';
try {$destination213=$missing213;} catch(TypeError $e) {
    echo $destination213===null?"N":"BAD",":",isset($missing213)?1:0,":",get_error_handler()==='handler213'?1:0,";";
}
restore_error_handler();
''', b'N:0:1;', 'normal'),
    ('byref-creation-and-mask-miss', b'''<?php
error_reporting(0); $hits213=0;
function sink213(&$value) {echo $value===null?"N;":"BAD;"; $value=5;}
set_error_handler(function($level,$message,$file,$line) {$GLOBALS['hits213']=$GLOBALS['hits213']+1; return true;},2);
sink213($missing213); echo $missing213,":",$hits213,";";
restore_error_handler(); unset($missing213);
set_error_handler(function($level,$message,$file,$line) {echo "BAD;"; return true;},512);
$value213=(int)$missing213; echo $value213,";";
unset($missing213); $value213=true?$missing213:1; echo $value213===null?"N;":"BAD;";
restore_error_handler();
''', b'N;5:0;0;N;', 'normal'),
    ('rejected-constrained-assign-throw-pending', b'''<?php
error_reporting(0);
class Slot213 {public static int $value=3;}
$destination213 =& Slot213::$value;
$throw213=function($level,$message,$file,$line) {
    $GLOBALS['destination213']=7;
    echo "T",func_num_args(),";"; throw new Error('handler');
};
set_error_handler($throw213,2);
try {$destination213=$missing213;} catch(TypeError $e) {
    echo "C:",Slot213::$value,":",$e->getPrevious() instanceof Error?1:0,":",get_error_handler()===$throw213?1:0,";";
}
restore_error_handler();
''', b'T4;C:7:1:1;', 'unsupported'),
    ('earlier-cast-control-now-admitted', b'''<?php
error_reporting(0);
set_error_handler(function() { echo 'H'; }, 2);
$r = (bool) $missing_cast209;
echo ($r ? 'BAD' : 'F');
restore_error_handler();
''', b'HF', 'normal'),
]
