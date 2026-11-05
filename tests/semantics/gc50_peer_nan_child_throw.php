<?php
class GC50PeerValue { public $child = null; }
function makeFloatFailure50() { return new Exception('float-50'); }
class GC50PeerThrowChild {
    public function __destruct() {
        global $map, $key, $oldWatch, $nextWatch, $result, $failure;
        echo 'C|', (int) ($oldWatch->get() === null), '|',
             (int) ($map[$key] !== $map[$key]), '|',
             (int) isset($map[$key]), '|',
             (int) ($nextWatch->get() !== null), '|',
             (int) ($result === 77), '|';
        $wasEmpty = empty($map[$key]);
        echo 'E|', (int) $wasEmpty, '|',
             (int) ($map[$key] === PHP_INT_MIN), '|';
        throw $failure;
    }
}
class GC50PeerNextChild { public function __destruct() { echo 'Z|'; } }
function replaceFloatSlot50($level, $message) {
    global $map, $key;
    echo 'H|', (int) ($level === 2), '|',
         (int) ($message === 'unexpected NAN value was coerced to bool'), '|',
         (int) ($map[$key] !== $map[$key]), '|';
    $map[$key] = PHP_INT_MIN;
    echo 'I|', (int) !empty($map[$key]), '|';
    return true;
}
$failure = makeFloatFailure50();
$map = new WeakMap;
$key = new stdClass;
$nextKey = new stdClass;
$old = new GC50PeerValue;
$child = new GC50PeerThrowChild;
$old->child = $child;
$next = new GC50PeerValue;
$next->child = new GC50PeerNextChild;
$map[$key] = $old;
$map[$nextKey] = $next;
$oldWatch = WeakReference::create($old);
$childWatch = WeakReference::create($child);
$nextWatch = WeakReference::create($next);
unset($old, $child, $next);
$incoming = NAN;
$result = 77;
$after = 0;
set_error_handler('replaceFloatSlot50');
echo 'B|';
try {
    $result = $map[$key] = $incoming;
    $after = 1;
} catch (Exception $e) {
    $trace = $e->getTrace();
    echo 'T|', (int) ($e === $failure), '|', $trace[0]['function'], '|',
         $result, '|', $after, '|',
         (int) ($childWatch->get() === null), '|',
         (int) ($nextWatch->get() !== null), '|',
         (int) ($map[$key] === PHP_INT_MIN), '|';
}
unset($map);
echo 'A|', (int) ($nextWatch->get() === null), '|';
