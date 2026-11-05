<?php
class GC34IncomingLeaf {}
$target = new stdClass;
$key = WeakReference::create($target);
$first = new WeakMap;
$second = new WeakMap;
$valueFirst = new GC34IncomingLeaf;
$valueSecond = new GC34IncomingLeaf;
$second[$key] = $valueSecond;
$first[$key] = $valueFirst;
unset($valueFirst, $valueSecond);
echo 'B|', count($first), '|', count($second), '|';
unset($key);
echo 'A|', count($first), '|', count($second), '|';
