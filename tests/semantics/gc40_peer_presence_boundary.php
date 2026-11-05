<?php
class GC40PresenceValue { public $child = null; }
class GC40PresenceLeaf {}
class GC40PresenceChild {
    public function __destruct() {
        global $mapWatch, $firstWatch, $secondWatch, $firstKeyWatch, $secondKeyWatch, $firstKey;
        echo 'P|', (int) isset($mapWatch->get()[$firstKey]), '|';
        echo 'C|', (int) ($mapWatch->get() !== null), '|',
             (int) ($firstWatch->get() === null), '|',
             (int) ($secondWatch->get() !== null), '|',
             (int) ($firstKeyWatch->get() !== null), '|',
             (int) ($secondKeyWatch->get() !== null), '|';
    }
}
$map = new WeakMap;
$firstKey = new stdClass;
$secondKey = new stdClass;
$first = new GC40PresenceValue;
$second = new GC40PresenceLeaf;
$map[$firstKey] = $first;
$map[$secondKey] = $second;
$first->child = new GC40PresenceChild;
$mapWatch = WeakReference::create($map);
$firstWatch = WeakReference::create($first);
$secondWatch = WeakReference::create($second);
$firstKeyWatch = WeakReference::create($firstKey);
$secondKeyWatch = WeakReference::create($secondKey);
unset($first, $second);
echo 'B|';
unset($map);
echo 'A|', (int) ($mapWatch->get() === null), '|',
     (int) ($firstWatch->get() === null), '|',
     (int) ($secondWatch->get() === null), '|',
     (int) ($firstKeyWatch->get() !== null), '|',
     (int) ($secondKeyWatch->get() !== null), '|';
