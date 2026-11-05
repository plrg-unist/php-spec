<?php
class GC40PeerLeaf {}
class GC40PeerValue { public $child = null; }
class GC40PeerChild {
    public function __destruct() {
        echo 'C|',
            (int) ($GLOBALS['mapWatch']->get() !== null), '|',
            (int) ($GLOBALS['leafWatch']->get() === null), '|',
            (int) ($GLOBALS['fieldWatch']->get() === null), '|',
            (int) ($GLOBALS['firstKeyWatch']->get() !== null), '|',
            (int) ($GLOBALS['secondKeyWatch']->get() !== null), '|';
        throw new Exception('reverse-40');
    }
}
$map = new WeakMap;
$mapWatch = WeakReference::create($map);
$firstKey = new stdClass;
$secondKey = new stdClass;
$firstKeyWatch = WeakReference::create($firstKey);
$secondKeyWatch = WeakReference::create($secondKey);
$leaf = new GC40PeerLeaf;
$field = new GC40PeerValue;
$map[$firstKey] = $leaf;
$map[$secondKey] = $field;
$leafWatch = WeakReference::create($leaf);
$fieldWatch = WeakReference::create($field);
$field->child = new GC40PeerChild;
unset($leaf, $field);
echo 'B|';
try { unset($map); echo 'AFTER|'; }
catch (Throwable $error) { echo 'T|', $error->getMessage(), '|'; }
echo 'A|',
    (int) ($mapWatch->get() === null), '|',
    (int) ($leafWatch->get() === null), '|',
    (int) ($fieldWatch->get() === null), '|',
    (int) ($firstKeyWatch->get() !== null), '|',
    (int) ($secondKeyWatch->get() !== null), '|';
