<?php
class ChildCurrent18 implements ArrayAccess {
    public function offsetExists(mixed $k): bool { return false; }
    public function offsetGet(mixed $k): mixed { return null; }
    public function offsetSet(mixed $k, mixed $v): void {
        echo 'S:', ($k === null ? 1 : 0), ':', $v, ';';
        $sent18 = Fiber::suspend('parked');
        echo 'Q:', $sent18, ':', $v, ';';
        $GLOBALS['rhs18'] =& $GLOBALS['new18'];
        unset($GLOBALS['g18']);
    }
    public function offsetUnset(mixed $k): void {}
    public function __destruct() { echo 'C;'; }
}
class OuterCurrent18 implements ArrayAccess {
    public function offsetExists(mixed $k): bool { return false; }
    public function offsetGet(mixed $k): mixed { echo 'G;'; return new ChildCurrent18; }
    public function offsetSet(mixed $k, mixed $v): void { echo 'WRONGOUTERSET;'; }
    public function offsetUnset(mixed $k): void {}
}
function finalizeCurrent18() {
    try { yield 1; }
    finally { echo 'F;'; $GLOBALS['alias18'] = 25; }
}
$g18 = finalizeCurrent18();
$g18->current();
$rhs18 = 11;
$alias18 =& $rhs18;
$new18 = 31;
$root18 = new OuterCurrent18;
$f18 = new Fiber(function () use ($root18, &$rhs18) {
    $read18 = ($root18['root'][] = $rhs18);
    echo 'R:', $read18, ';';
});
$parked18 = $f18->start();
echo 'A:', $parked18, ';';
unset($root18);
$alias18 = 23;
$f18->resume('resumed');
echo 'E:', $alias18, ':', $rhs18, ':', ($f18->isTerminated() ? 1 : 0), ';';
