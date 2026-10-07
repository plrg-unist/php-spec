<?php
error_reporting(0);
class CompositionCell292 { public static int $value=13; }
class CompositionOwner292 {
 protected static function who292(): string { return 'O'; }
 private function warning292($n,$m) {
  echo 'W:',self::who292(),':',static::who292(),';';
  $GLOBALS['nameCell292']=7;
  unset($GLOBALS['keyArray292'],$GLOBALS['nameCell292'],$GLOBALS['maker292']);
  return true;
 }
 public function callback292(): Closure { return $this->warning292(...); }
}
class CompositionChild292 extends CompositionOwner292 {
 protected static function who292(): string { return 'C'; }
}
class CompositionAccess292 implements ArrayAccess {
 public function offsetExists(mixed $offset): bool { return false; }
 public function offsetGet(mixed $offset): mixed {
  echo 'G:',$offset,';';
  $GLOBALS['rhs292'] =& $GLOBALS['replacement292'];
  $GLOBALS['old292']=19;
  unset($GLOBALS['o292']);
  return 5;
 }
 public function offsetSet(mixed $offset,mixed $value): void {
  echo 'S:',$offset,':',$value,';';
  $GLOBALS['saved292']=$value;
  $GLOBALS['old292']=23;
 }
 public function offsetUnset(mixed $offset): void {}
}
$old292=&CompositionCell292::$value;
$rhs292=&$old292;$replacement292=17;
$nameCell292=3;$keyArray292=[1,&$nameCell292];
$maker292=new CompositionChild292;
set_error_handler($maker292->callback292());
$o292=new CompositionAccess292;
$r292=($o292[include $keyArray292]+=$rhs292);
restore_error_handler();
echo 'R:',$r292,':',$saved292,':',$rhs292,':',CompositionCell292::$value,':',(int)isset($o292),':',(int)isset($maker292),';';
