<?php
error_reporting(0);
class OwnerReadCurrent282 {
    public static int $value=9;
    private static function handle($n,$m,$f,$l) { echo 'H:',self::class,'/',get_called_class(),':',$l,';'; $GLOBALS['alias282']=17; unset($GLOBALS['alias282']); return true; }
    public static function run(int &$arg) {
        $GLOBALS['alias282']=&$arg; $a=13;
        set_error_handler(self::handle(...),2);
        $r=$a[[&$arg]];
        restore_error_handler();
        echo 'R:',$arg,':',func_get_arg(0),':',(int)($r===null),';';
    }
}
class ChildReadCurrent282 extends OwnerReadCurrent282 { public static function handle($n,$m,$f,$l) { echo 'WRONG;'; return true; } }
ChildReadCurrent282::run(OwnerReadCurrent282::$value);
echo 'V:',OwnerReadCurrent282::$value,';';
