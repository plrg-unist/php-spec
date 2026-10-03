<?php
error_reporting(0);
class BorrowStringOwner13 {
    public static function read(&$left){return $left===$missing;}
}
class BorrowStringChild13 extends BorrowStringOwner13 {}
$x=null;$a=&$x;$y=9;
function borrowStringWarning13($n,$m,$f,$l){
    $GLOBALS['a'] =& $GLOBALS['y'];
    echo func_num_args(),';';
}
set_error_handler('borrowStringWarning13',2);
$call='BorrowStringChild13::read';
echo($call(left:$a)?1:0),':',$a,':',($x===null?1:0);
restore_error_handler();
