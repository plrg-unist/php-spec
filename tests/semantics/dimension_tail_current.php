<?php
error_reporting(0);
class TailCellCurrent255 {public static int $value=9;}
class OwnerTailCurrent255 {
    private static function handle($level,$message,$file,$line) {echo "H:",__CLASS__,"/",get_called_class(),":",$line,";";$GLOBALS['heldCurrent255']=$GLOBALS['aCurrent255'];unset($GLOBALS['aliasCurrent255'],$GLOBALS['keyCurrent255']);return false;}
    public static function run(&$arg) {
        global $aCurrent255,$keyCurrent255;
        set_error_handler([static::class,'handle'],8192);
        $result=($aCurrent255[$keyCurrent255][]=['p'=>&$arg]);
        restore_error_handler();$arg=17;
        echo "R:",$result['p'],":",isset($aCurrent255[1][1])?1:0,":",isset($GLOBALS['heldCurrent255'][1][1])?1:0,":",func_get_arg(0),";";
    }
}
class ChildTailCurrent255 extends OwnerTailCurrent255 {public static function handle($level,$message,$file,$line) {echo "WRONG;";return true;}}
$seedCurrent255=5;$aCurrent255=[1=>[$seedCurrent255]];$keyCurrent255=1.5;$aliasCurrent255=&TailCellCurrent255::$value;
ChildTailCurrent255::run($aliasCurrent255);echo "V:",TailCellCurrent255::$value,";";
