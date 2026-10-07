<?php
error_reporting(0);
class SmallChild309 implements ArrayAccess {
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
class SmallOuter309 implements ArrayAccess {
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
$rhs309 = 11;
$alias309 =& $rhs309;
$new309 = 31;
$child309 = new SmallChild309;
$weak309 = WeakReference::create($child309);
$outer309 = new SmallOuter309;
$r309 = ($outer309[include 'Array'][] = $rhs309);
echo 'R:', $r309, ':', $saved309, ':', $rhs309, ':', $alias309, ':', ($weak309->get() === null ? 0 : 1), ':', (isset($outer309) ? 1 : 0), ':', (isset($child309) ? 1 : 0), ';';
