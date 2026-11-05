<?php
class GC34IncomingLeaf {}
$target = new stdClass;
$key = WeakReference::create($target);
$first = new WeakMap;
$second = new WeakMap;
$valueFirst = new GC34IncomingLeaf;
$valueSecond = new GC34IncomingLeaf;
$watchFirst = WeakReference::create($valueFirst);
$watchSecond = WeakReference::create($valueSecond);
$second[$key] = $valueSecond;
$first[$key] = $valueFirst;
unset($valueFirst, $valueSecond);
echo 'B|', (int) ($watchFirst->get() !== null), '|', (int) ($watchSecond->get() !== null), '|';
unset($key);
echo 'A|', (int) ($watchFirst->get() === null), '|', (int) ($watchSecond->get() === null), '|';
