<?php
class GC48Value { public $child = null; }
class GC48Leaf {}
function makeFailure48() { return new Exception('replace-48'); }
class GC48Child {
    public function __destruct() {
        global $map, $key, $incoming, $result, $mapWatch, $keyWatch,
               $oldWatch, $incomingWatch, $failure, $fresh;
        echo 'C|', (int) ($mapWatch->get() === $map), '|',
             (int) ($keyWatch->get() === $key), '|',
             (int) ($oldWatch->get() === null), '|',
             (int) ($map[$key] === $incomingWatch->get()), '|',
             (int) ($result === 77), '|';
        $incoming = 'changed-48';
        if ($fresh) { throw new Exception('fresh-48'); }
        throw $failure;
    }
}
$fresh = false;
$failure = makeFailure48();
$map = new WeakMap;
$key = new stdClass;
$old = new GC48Value;
$child = new GC48Child;
$old->child = $child;
$incoming = new GC48Leaf;
$map[$key] = $old;
$mapWatch = WeakReference::create($map);
$keyWatch = WeakReference::create($key);
$oldWatch = WeakReference::create($old);
$childWatch = WeakReference::create($child);
$incomingWatch = WeakReference::create($incoming);
unset($old, $child);
$result = 77;
$continued = 0;
echo 'B|';
try {
    $result = $map[$key] = $incoming;
    $continued = 1;
} catch (Exception $e) {
    $trace = $e->getTrace();
    echo 'T|', (int) ($e === $failure), '|', $e->getMessage(), '|',
         $trace[0]['function'], '|', $result, '|', $continued, '|',
         (int) ($incoming === 'changed-48'), '|',
         (int) ($map[$key] === $incomingWatch->get()), '|',
         (int) ($oldWatch->get() === null), '|',
         (int) ($childWatch->get() === null), '|';
}
unset($map);
echo 'A|', (int) ($mapWatch->get() === null), '|',
     (int) ($incomingWatch->get() === null), '|',
     (int) ($keyWatch->get() === $key), '|';
