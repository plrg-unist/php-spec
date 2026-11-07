"""Independent positional reference-SEND owners and emitted-line controls."""

CASES = {
    'positional-prior-sent-cell-outlives-handler-rebinding': b'''<?php
function h($n,$m,$file,$line){echo 'H;';$GLOBALS['x'] =& $GLOBALS['replacement'];unset($GLOBALS['keep']);return true;}
function make(){echo 'P;';return 7;}
function &take(&$kept,&$warn){$kept+=1;$warn+=2;echo 'F:',$kept,':',$warn,';';return $kept;}
$x=3;$keep=&$x;$replacement=40;set_error_handler('h',8);
$v =& take($x,make());
$v=11;echo 'R:',$v,':',$x,':',$replacement,':',isset($keep)===false,';';
''',
    'positional-false-handler-keeps-emitted-send-line': b'''<?php
function h($n,$m,$file,$line){echo 'H:',$line,';';return false;}
function make(){echo 'P;';return 7;}
function later(){echo 'T;';return 9;}
function &take(&$x,$y){echo 'F:',$x,':',$y,';';return $x;}
set_error_handler('h',8);
$v =& take(
    make(),
    later()
);
$v=20;echo 'R:',$v,';';
''',
}

SOURCE_KIND_CONTROLS = {
    'positional-reference-producer-skips-notice': b'''<?php
function h($n,$m,$file,$line){echo 'BAD-H;';return true;}
function &make(){global $x;echo 'P;';return $x;}
function &take(&$slot){$slot+=1;return $slot;}
$x=3;$old=&$x;set_error_handler('h',8);
$v =& take(make());$v=20;echo 'R:',$x,':',$old,':',$v,';';
''',
    'positional-tmp-errors-before-notice': b'''<?php
function h($n,$m,$file,$line){echo 'BAD-H;';return true;}
function &take(&$slot){echo 'BAD-F;';return $slot;}
$v=55;set_error_handler('h',8);
try{$v =& take(7);}catch(Error $e){echo 'C:',$e->getMessage(),':',$v===55,';';}
''',
}

if __name__ == '__main__':
    from pathlib import Path
    import function_scope
    raise SystemExit(0 if function_scope.main(CASES | SOURCE_KIND_CONTROLS,
        'positional-reference-notice-review', Path(__file__), publish=False,
        model_seconds=120) else 1)
