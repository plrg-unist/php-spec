<?php
error_reporting(0);
class OwnerGlobalCurrent269{
public static int $value=9;
private static function handle($n,$m,$f,$l){echo "H:",self::class,"/",static::class,":",$l,";";$GLOBALS['lost269']=&self::$value;unset($GLOBALS['name269']);return false;}
public static function run(int &$arg){
$name269='lost269';$GLOBALS['name269']=&$name269;
set_error_handler(self::handle(...),2);
$r=++$GLOBALS[$name269];
restore_error_handler();$arg=17;
echo "R:",$r,":",$GLOBALS['lost269'],":",func_get_arg(0),":",isset($GLOBALS['name269'])?1:0,";";
}
}
class ChildGlobalCurrent269 extends OwnerGlobalCurrent269{public static function handle($n,$m,$f,$l){echo "WRONG;";}}
ChildGlobalCurrent269::run(OwnerGlobalCurrent269::$value);
echo "V:",OwnerGlobalCurrent269::$value,";";
