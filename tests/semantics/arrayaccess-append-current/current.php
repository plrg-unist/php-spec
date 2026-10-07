<?php
error_reporting(0);
class CompositionOwner304 {
 protected static function who304(): string { return 'O'; }
 private function warning304($n,$m) {
  if ($n===2) {
   echo 'W:',self::who304(),':',static::who304(),';';
   $GLOBALS['nameCell304']=7;
   unset($GLOBALS['keyArray304'],$GLOBALS['nameCell304'],$GLOBALS['maker304']);
  } else {
   echo 'N;';
   $GLOBALS['old304'] =& $GLOBALS['new304'];
   $GLOBALS['rhs304']=17;
   unset($GLOBALS['o304']);
  }
  return true;
 }
 public function callback304(): Closure { return $this->warning304(...); }
}
class CompositionChild304 extends CompositionOwner304 {
 protected static function who304(): string { return 'C'; }
}
class CompositionAccess304 implements ArrayAccess {
 public function offsetExists(mixed $offset): bool { return false; }
 public function offsetGet(mixed $offset): mixed {
  echo 'G:',$offset,';';
  return $GLOBALS['data304'];
 }
 public function offsetSet(mixed $offset,mixed $value): void { echo 'WRONGSET;'; }
 public function offsetUnset(mixed $offset): void { echo 'WRONGUNSET;'; }
}
$old304=['old'=>5]; $keep304=&$old304; $new304=['new'=>7];
$data304=['ref'=>&$old304]; $rhs304=11;
$nameCell304=3; $keyArray304=[1,&$nameCell304];
$maker304=new CompositionChild304;
set_error_handler($maker304->callback304());
$o304=new CompositionAccess304;
$r304=($o304[include $keyArray304]['ref'][]+=$rhs304);
restore_error_handler();
echo 'R:',$r304,':',$data304['ref'][0],':',$keep304[0],':',$old304['new'],':',$rhs304,':',(int)isset($o304),':',(int)isset($maker304),';';
