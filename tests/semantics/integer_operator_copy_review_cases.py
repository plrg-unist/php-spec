"""Independent original: two owning operands alias one live reference cell."""

CASES = {
    'refcall-both-shared-review': b'''<?php
function &lhs() { return $GLOBALS['x']; }
function &rhs() { return $GLOBALS['x']; }
function h($n,$m,$f,$l) {
    echo "H:",$n,";";
    $GLOBALS['calls']=$GLOBALS['calls']+1;
    $GLOBALS['x']=&$GLOBALS['replacement'];
    $GLOBALS['old']=$GLOBALS['calls']===1 ? 3.75 : 7.75;
    return true;
}
$x=5.75; $old=&$x; $replacement=8; $calls=0;
set_error_handler('h');
$v=lhs() % rhs();
echo "V:",$v,":",$calls,":",$old,":",$x;
''',
}
