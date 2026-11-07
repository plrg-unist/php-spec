"""Independent plain-CV owners and emitted-line controls for reference SEND."""

CASES = {
    'prior-sent-cell-outlives-handler-rebinding': b'''<?php
function h($n,$m,$file,$line){echo 'H;';$GLOBALS['x'] =& $GLOBALS['replacement'];unset($GLOBALS['keep']);return true;}
function make(){echo 'P;';return 7;}
function &take(&$kept,&$warn){$kept+=1;$warn+=2;echo 'F:',$kept,':',$warn,';';return $kept;}
$x=3;$keep=&$x;$replacement=40;set_error_handler('h',8);
$v =& take(kept:$x,warn:make());
$v=11;echo 'R:',$v,':',$x,':',$replacement,':',isset($keep)===false,';';
''',
    'false-handler-keeps-emitted-send-line': b'''<?php
function h($n,$m,$file,$line){echo 'H:',$line,';';return false;}
function make(){echo 'P;';return 7;}
function later(){echo 'T;';return 9;}
function &take(&$x,$y){echo 'F:',$x,':',$y,';';return $x;}
set_error_handler('h',8);
$v =& take(
    x: make(),
    y: later()
);
$v=20;echo 'R:',$v,';';
''',
}
