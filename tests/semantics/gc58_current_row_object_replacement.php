<?php
class GC58Value { public $child = null; }
class GC58OldChild {
    public function __destruct() {
        global $mapWatch58, $keyWatch58, $oldWatch58, $newWatch58;
        echo 'O|', (int) ($mapWatch58->get() === null), '|',
             (int) ($keyWatch58->get() === null), '|',
             (int) ($oldWatch58->get() === null), '|',
             (int) ($newWatch58->get() === null), '|';
    }
}
class GC58NewChild {
    public function __destruct() {
        global $mapWatch58, $keyWatch58, $oldWatch58, $newWatch58;
        echo 'N|', (int) ($mapWatch58->get() === null), '|',
             (int) ($keyWatch58->get() === null), '|',
             (int) ($oldWatch58->get() !== null), '|',
             (int) ($newWatch58->get() === null), '|';
    }
}
$map = new WeakMap;
$key = new stdClass;
$scalarKey = new stdClass;
$old = new GC58Value;
$old->child = new GC58OldChild;
$new = new GC58Value;
$new->child = new GC58NewChild;
$mapWatch58 = WeakReference::create($map);
$keyWatch58 = WeakReference::create($key);
$map[$key] = $old;
$map[$scalarKey] = 17;
$used = 31;
echo 'B|';
foreach ($map as $loopKey => $loopValue) {
    $used = $map[$loopKey] = $new;
    echo 'P|', (int) ($loopValue === $old), '|',
         (int) ($used === $new), '|',
         (int) ($map[$loopKey] === $new), '|',
         (int) ($loopValue !== $used), '|';
    $oldWatch58 = WeakReference::create($old);
    $newWatch58 = WeakReference::create($new);
    unset($old, $new);
    break;
}
echo 'E|', (int) ($oldWatch58->get() === $loopValue), '|',
     (int) ($newWatch58->get() === $used), '|',
     (int) ($map[$key] === $used), '|';
unset($map);
echo 'M|', (int) ($mapWatch58->get() === null), '|',
     (int) ($oldWatch58->get() === $loopValue), '|',
     (int) ($newWatch58->get() === $used), '|';
unset($key, $scalarKey, $loopKey);
echo 'K|', (int) ($keyWatch58->get() === null), '|';
unset($used);
echo 'U|', (int) ($oldWatch58->get() === $loopValue), '|',
     (int) ($newWatch58->get() === null), '|';
unset($loopValue);
echo 'F|', (int) ($oldWatch58->get() === null), '|',
     (int) ($newWatch58->get() === null), '|';
