<?php
error_reporting(0);
class OwnerContainerCurrent276{
 public static int $value=9;
 private static function handle($n,$m,$file,$line){echo "H:",self::class,"/",get_called_class(),":",$line,";";unset($GLOBALS['source276']);$GLOBALS['key276']=2;return false;}
 public static function run(int &$arg){
  global $key276;
  $a276=false;$GLOBALS['source276']=[1=>&$arg];$key276=1;set_error_handler(self::handle(...),8192);
  $a276[$key276]=&$GLOBALS['source276'][1];
  restore_error_handler();$arg=17;
  echo "R:",$a276[2],":",func_get_arg(0),":",isset($GLOBALS['source276'])?1:0,";";
 }
}
class ChildContainerCurrent276 extends OwnerContainerCurrent276{public static function handle($n,$m){echo "WRONG;";return false;}}
ChildContainerCurrent276::run(OwnerContainerCurrent276::$value);
echo "V:",OwnerContainerCurrent276::$value,";";
