<?php
error_reporting(0);
class OwnerWriteCurrent242 {
    public static int $slot=9;
    private static function keyWarning($level,$message,$file,$line) {echo "H:",get_called_class(),":",func_num_args(),":",$line,";";$GLOBALS['held242']=$GLOBALS['a242'];return false;}
    public static function run(&$slot) {
        $a242=[1=>&$slot];$GLOBALS['a242']=&$a242;$key242=1.5;
        set_error_handler(self::keyWarning(...),8192);
        $ref242=&$a242[$key242];$wasNull242=$ref242===null;$ref242=17;
        restore_error_handler();echo "R:",$wasNull242?1:0,":",$slot,":",func_get_arg(0),":",$a242[1],":",$GLOBALS['held242'][1],":",$ref242,";";
    }
}
class ChildWriteCurrent242 extends OwnerWriteCurrent242 {public static function keyWarning($level,$message,$file,$line) {echo "WRONG;";return true;}}
$alias242=&OwnerWriteCurrent242::$slot;ChildWriteCurrent242::run($alias242);echo "V:",$alias242,";";
