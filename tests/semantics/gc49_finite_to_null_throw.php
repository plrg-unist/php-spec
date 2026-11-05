<?php
class GC49OldValue { public $child = null; }
function makeFailure49() { return new Exception('mixed-49'); }
class GC49ThrowChild {
    public function __destruct() {
        global $map, $key, $incoming, $oldWatch, $nextWatch, $result, $failure;
        echo 'C|', (int) ($oldWatch->get() === null), '|',
             (int) ($map[$key] === null), '|',
             (int) !isset($map[$key]), '|',
             (int) empty($map[$key]), '|',
             (int) (($map[$key] ?? 'null-slot') === 'null-slot'), '|',
             (int) ($nextWatch->get() !== null), '|',
             (int) ($result === 77), '|';
        $incoming = 'changed-49';
        throw $failure;
    }
}
class GC49NextChild { public function __destruct() { echo 'Z|'; } }
$failure = makeFailure49();
$map = new WeakMap;
$key = new stdClass;
$nextKey = new stdClass;
$old = new GC49OldValue;
$child = new GC49ThrowChild;
$old->child = $child;
$next = new GC49OldValue;
$next->child = new GC49NextChild;
$map[$key] = $old;
$map[$nextKey] = $next;
$oldWatch = WeakReference::create($old);
$childWatch = WeakReference::create($child);
$nextWatch = WeakReference::create($next);
unset($old, $child, $next);
$incoming = null;
$result = 77;
$continued = 0;
echo 'B|';
try {
    $result = $map[$key] = $incoming;
    $continued = 1;
} catch (Exception $e) {
    $trace = $e->getTrace();
    echo 'T|', (int) ($e === $failure), '|', $trace[0]['function'], '|',
         $result, '|', $continued, '|',
         (int) ($incoming === 'changed-49'), '|',
         (int) ($childWatch->get() === null), '|',
         (int) ($nextWatch->get() !== null), '|';
}
unset($map);
echo 'A|', (int) ($nextWatch->get() === null), '|';
