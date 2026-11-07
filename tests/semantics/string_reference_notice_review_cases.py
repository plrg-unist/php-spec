"""Interned snapshots and real prior cells at ordinary reference-SEND Notices."""

CASES = {
    'named-interned-prior-cell': b'''<?php
function h($n,$m,$file,$line){$GLOBALS['head']='seen';$GLOBALS['head'] =& $GLOBALS['replacement'];unset($GLOBALS['hold']);$GLOBALS['source']='new';echo 'H;';return true;}
function make(){echo 'P;';return $GLOBALS['source'];}
function &take(&$kept,&...$rest){$kept.='-h';$rest['tail'].='-f';echo 'F:',$kept,':',$rest['tail'],';';return $rest['tail'];}
$head='head';$hold=&$head;$replacement='root';$source='seed';set_error_handler('h',8);
$r =& take(kept:$head,tail:make());$r.='-r';echo 'R:',$r,':',$head,':',$replacement,':',isset($hold)===false,':',$source,';';
''',
    'positional-interned-false-line': b'''<?php
function h($n,$m,$file,$line){$GLOBALS['source']='new';echo 'H:',$line,';';return false;}
function make(){echo 'P;';return $GLOBALS['source'];}
function later(){echo 'T;';return 9;}
function &take(&$value,$other){$value.='-f';echo 'F:',$value,':',$other,';';return $value;}
$source='seed';set_error_handler('h',8);
$r =& take(
    make(),
    later()
);
$r.='-r';echo 'R:',$r,':',$source,';';
''',
}

BOUNDARY_CONTROLS = {
    'request-string-pending-control': b'''<?php
function h($n,$m,$file,$line){echo 'H;';return true;}
function make(){echo 'P;';return $GLOBALS['source'].$GLOBALS['suffix'];}
function &take(&$value){echo 'F:',$value,';';return $value;}
$source='seed';$suffix='-dyn';set_error_handler('h',8);
$r =& take(value:make());$r.='-r';echo 'R:',$r,';';
''',
}

if __name__ == '__main__':
    from pathlib import Path
    import function_scope
    raise SystemExit(0 if function_scope.main(CASES,
        'string-reference-notice-review', Path(__file__), publish=False,
        model_seconds=120) else 1)
