<?php
class GC40PeerFirstThrowValue { public $child = null; }
class GC40PeerFirstThrowLeaf {}
class GC40PeerFirstThrowChild {
    public function __destruct() {
        global $mapWatch, $firstWatch, $secondWatch, $firstKeyWatch, $secondKeyWatch;
        echo 'C|', (int) ($mapWatch->get() !== null), '|',
             (int) ($firstWatch->get() === null), '|',
             (int) ($secondWatch->get() !== null), '|',
             (int) ($firstKeyWatch->get() !== null), '|',
             (int) ($secondKeyWatch->get() !== null), '|';
        throw new Exception('first-40');
    }
}
$map = new WeakMap;
$firstKey = new stdClass;
$secondKey = new stdClass;
$first = new GC40PeerFirstThrowValue;
$second = new GC40PeerFirstThrowLeaf;
$map[$firstKey] = $first;
$map[$secondKey] = $second;
$first->child = new GC40PeerFirstThrowChild;
$mapWatch = WeakReference::create($map);
$firstWatch = WeakReference::create($first);
$secondWatch = WeakReference::create($second);
$firstKeyWatch = WeakReference::create($firstKey);
$secondKeyWatch = WeakReference::create($secondKey);
unset($first, $second);
echo 'B|';
try { unset($map); echo 'AFTER|'; }
catch (Throwable $error) { echo 'T|', $error->getMessage(), '|'; }
echo 'A|', (int) ($mapWatch->get() === null), '|',
     (int) ($firstWatch->get() === null), '|',
     (int) ($secondWatch->get() === null), '|',
     (int) ($firstKeyWatch->get() !== null), '|',
     (int) ($secondKeyWatch->get() !== null), '|';
