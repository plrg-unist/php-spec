<?php
class GC64Incoming {}
class GC64ThrowChild {
    public function __destruct() {
        global $map64, $loopKey64, $result64, $oldWatch64, $incomingWatch64;
        $seen64 = $map64[$loopKey64];
        echo 'C|', (int) ($oldWatch64->get() === null), '|',
             (int) ($seen64 === $incomingWatch64->get()), '|',
             (int) ($result64 === 77), '|';
        throw new Exception('child-64');
    }
}
class GC64TailChild {
    public function __destruct() {
        global $map64, $loopKey64, $result64, $oldWatch64, $incomingWatch64;
        $seen64 = $map64[$loopKey64];
        echo 'L|', (int) ($oldWatch64->get() === null), '|',
             (int) ($seen64 === $incomingWatch64->get()), '|',
             (int) ($result64 === 77), '|';
    }
}
class GC64Value {
    public $before = 17;
    public $first = null;
    public $tail = null;
    public $after = 23;
    public function __destruct() {
        global $map64, $loopKey64, $result64, $oldWatch64, $incomingWatch64;
        echo 'O|', (int) ($oldWatch64->get() === $this), '|';
        $seen64 = $map64[$loopKey64];
        echo 'V|', (int) ($seen64 === $incomingWatch64->get()), '|',
             (int) ($result64 === 77), '|';
        throw new Exception('own-64');
    }
}
$map64 = new WeakMap;
$key64 = new stdClass;
$otherKey64 = new stdClass;
$old64 = new GC64Value;
$first64 = new GC64ThrowChild;
$tail64 = new GC64TailChild;
$old64->first = $first64;
$old64->tail = $tail64;
$incoming64 = new GC64Incoming;
$other64 = new GC64Incoming;
$map64[$key64] = $old64;
$map64[$otherKey64] = $other64;
$mapWatch64 = WeakReference::create($map64);
$keyWatch64 = WeakReference::create($key64);
$oldWatch64 = WeakReference::create($old64);
$firstWatch64 = WeakReference::create($first64);
$tailWatch64 = WeakReference::create($tail64);
$incomingWatch64 = WeakReference::create($incoming64);
unset($old64, $first64, $tail64);
$result64 = 77;
$continued64 = 0;
echo 'B|';
try {
    foreach ($map64 as $loopKey64 => $loopValue64) {
        $loopValue64 = 0;
        $result64 = $map64[$loopKey64] = $incoming64;
        $continued64 = 1;
    }
} catch (Exception $error64) {
    $previous64 = $error64->getPrevious();
    $trace64 = $error64->getTrace();
    $previousTrace64 = $previous64->getTrace();
    echo 'T|', $error64->getMessage(), '|', $error64->getLine(), '|',
         $trace64[0]['function'], '|', $trace64[0]['line'], '|',
         $previous64->getMessage(), '|', $previous64->getLine(), '|',
         $previousTrace64[0]['function'], '|', $previousTrace64[0]['line'], '|',
         (int) ($previous64->getPrevious() === null), '|',
         (int) ($result64 === 77), '|', $continued64, '|';
}
echo 'R|', (int) ($map64[$key64] === $incoming64), '|',
     (int) ($oldWatch64->get() === null), '|',
     (int) ($firstWatch64->get() === null), '|',
     (int) ($tailWatch64->get() === null), '|';
unset($map64);
echo 'M|', (int) ($mapWatch64->get() === null), '|',
     (int) ($incomingWatch64->get() === $incoming64), '|';
unset($incoming64);
echo 'V|', (int) ($incomingWatch64->get() === null), '|';
unset($key64, $otherKey64, $loopKey64, $other64);
echo 'K|', (int) ($keyWatch64->get() === null), '|';
