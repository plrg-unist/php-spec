<?php
error_reporting(0);
class OwnerCurrentCoalesce262{
public static int $value=9;
private static function handle($n,$m,$f,$l){echo "H:",self::class,"/",static::class,":",$l,";";$GLOBALS['base262']=[0=>[1=>13]];self::$value=17;return false;}
public static function run(int &$arg){
$a=[0=>[1=>&$arg]];$key=1.5;$GLOBALS['base262']=&$a;
set_error_handler(self::handle(...),8192);
$r=($a[0][$key]??=37);
restore_error_handler();unset($GLOBALS['base262']);
echo "R:",$r,":",$a[0][1],":",func_get_arg(0),";";
}
}
class ChildCurrentCoalesce262 extends OwnerCurrentCoalesce262{public static function handle($n,$m,$f,$l){echo "WRONG;";}}
ChildCurrentCoalesce262::run(OwnerCurrentCoalesce262::$value);
echo "V:",OwnerCurrentCoalesce262::$value,";";
