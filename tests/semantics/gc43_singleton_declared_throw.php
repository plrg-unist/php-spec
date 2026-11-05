<?php
class GC43Value {
    public $first = null;
    public $scalar = null;
    public $last = null;
}
class GC43FirstChild {
    public function __destruct() {
        global $mapWatch, $valueWatch, $lastWatch, $keyWatch;
        echo 'F|', (int) ($mapWatch->get() !== null), '|',
             (int) ($valueWatch->get() === null), '|',
             (int) ($lastWatch->get() !== null), '|',
             (int) ($keyWatch->get() !== null), '|';
        throw new Exception('singleton-43');
    }
}
class GC43LastChild {
    public function __destruct() {
        global $mapWatch, $valueWatch, $firstWatch, $keyWatch;
        echo 'L|', (int) ($mapWatch->get() !== null), '|',
             (int) ($valueWatch->get() === null), '|',
             (int) ($firstWatch->get() === null), '|',
             (int) ($keyWatch->get() !== null), '|';
    }
}
$map = new WeakMap;
$key = new stdClass;
$value = new GC43Value;
$map[$key] = $value;
$value->last = new GC43LastChild;
$value->first = new GC43FirstChild;
$value->scalar = 'Q';
$mapWatch = WeakReference::create($map);
$valueWatch = WeakReference::create($value);
$firstWatch = WeakReference::create($value->first);
$lastWatch = WeakReference::create($value->last);
$keyWatch = WeakReference::create($key);
echo 'B|', $value->scalar, '|';
unset($value);
try { unset($map); echo 'AFTER|'; }
catch (Throwable $error) { echo 'T|', $error->getMessage(), '|'; }
echo 'A|', (int) ($mapWatch->get() === null), '|',
     (int) ($valueWatch->get() === null), '|',
     (int) ($firstWatch->get() === null), '|',
     (int) ($lastWatch->get() === null), '|',
     (int) ($keyWatch->get() !== null), '|';
