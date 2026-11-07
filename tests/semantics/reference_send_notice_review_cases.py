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

DUPLICATE_CONTROLS = {
    'fixed-duplicate-precedes-reference-notice': b'''<?php
function h($n,$m,$file,$line){echo 'BAD-H;';return true;}
function make(){echo 'P;';return 7;}
function &take(&$x){echo 'BAD-F;';return $x;}
$x=3;$r=55;set_error_handler('h',8);
try{$r =& take(x:$x,x:make());}catch(Error $e){echo 'C:',$e->getMessage(),':',$r===55,':',$x,';';}
''',
    'variadic-duplicate-precedes-reference-notice': b'''<?php
function h($n,$m,$file,$line){echo 'BAD-H;';return true;}
function make(){echo 'P;';return 7;}
function &take(&...$tail){echo 'BAD-F;';return $tail['a'];}
$x=3;$r=55;set_error_handler('h',8);
try{$r =& take(a:$x,a:make());}catch(Error $e){echo 'C:',$e->getMessage(),':',$r===55,':',$x,';';}
''',
}

if __name__ == '__main__':
    from pathlib import Path
    import function_scope
    raise SystemExit(0 if function_scope.main(CASES | DUPLICATE_CONTROLS,
        'named-reference-send-notice-review', Path(__file__), publish=False,
        model_seconds=120) else 1)
