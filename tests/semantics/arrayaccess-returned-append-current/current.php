<?php
error_reporting(0);
class CompositionCell309 { public static int $value = 11; }
class CompositionOwner309 {
 protected static function who309(): string { return 'O'; }
 private function warning309($level, $message) {
  echo 'W:', self::who309(), ':', static::who309(), ';';
  $GLOBALS['nameCell309'] = 7;
  unset($GLOBALS['keyArray309'], $GLOBALS['nameCell309'], $GLOBALS['maker309']);
  return true;
 }
 public function callback309(): Closure { return $this->warning309(...); }
}
class CompositionOwnerChild309 extends CompositionOwner309 {
 protected static function who309(): string { return 'C'; }
}
class CompositionChild309 implements ArrayAccess {
 public function offsetExists(mixed $offset): bool { echo 'WRONGEXISTS;'; return false; }
 public function offsetGet(mixed $offset): mixed { echo 'WRONGGET;'; return null; }
 public function offsetSet(mixed $offset, mixed $value): void {
  echo 'S:', ($offset === null ? 'N' : 'K'), ':', $value, ':', ($GLOBALS['weak309']->get() === $this ? 1 : 0), ';';
  $GLOBALS['saved309'] = $value;
  $GLOBALS['rhs309'] =& $GLOBALS['new309'];
  $GLOBALS['alias309'] = 25;
 }
 public function offsetUnset(mixed $offset): void { echo 'WRONGUNSET;'; }
 public function __destruct() { echo 'CD;'; $GLOBALS['alias309'] = 29; }
}
class CompositionOuter309 implements ArrayAccess {
 public function offsetExists(mixed $offset): bool { echo 'WRONGEXISTS;'; return false; }
 public function offsetGet(mixed $offset): mixed {
  echo 'G:', $offset, ';';
  $held309 = $GLOBALS['child309'];
  $GLOBALS['rhs309'] = 17;
  unset($GLOBALS['outer309'], $GLOBALS['child309']);
  return $held309;
 }
 public function offsetSet(mixed $offset, mixed $value): void { echo 'WRONGOUTERSET;'; }
 public function offsetUnset(mixed $offset): void { echo 'WRONGUNSET;'; }
 public function __destruct() { echo 'OD;'; }
}
$alias309 =& CompositionCell309::$value;
$rhs309 =& $alias309;
$new309 = 31;
$nameCell309 = 3;
$keyArray309 = [1, &$nameCell309];
$maker309 = new CompositionOwnerChild309;
set_error_handler($maker309->callback309());
$child309 = new CompositionChild309;
$weak309 = WeakReference::create($child309);
$outer309 = new CompositionOuter309;
$r309 = ($outer309[include $keyArray309][] = $rhs309);
restore_error_handler();
echo 'R:', $r309, ':', $saved309, ':', $rhs309, ':', CompositionCell309::$value, ':', ($weak309->get() === null ? 0 : 1), ':', (isset($outer309) ? 1 : 0), ':', (isset($child309) ? 1 : 0), ':', (isset($maker309) ? 1 : 0), ';';
