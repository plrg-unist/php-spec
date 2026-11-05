<?php
class GC34OwnReuse {
    public function __destruct() {
        global $mapWatch;
        $old = $mapWatch->get();
        echo 'OWN1|', (int) ($old !== null), '|';
        $again = WeakReference::create($old);
        echo (int) ($again === $mapWatch), '|';
    }
}
class GC34OwnLaterReuse {
    public function __destruct() { echo 'OWN2|'; }
}
class GC34IncomingReuse {
    public function __destruct() { echo 'IN|'; }
}
$map = new WeakMap;
$mapWatch = WeakReference::create($map);
$first = new stdClass;
$second = new stdClass;
$outer = new WeakMap;
$map[$first] = new GC34OwnReuse;
$map[$second] = new GC34OwnLaterReuse;
$outer[$map] = new GC34IncomingReuse;
echo 'B|';
unset($map);
echo 'A|', (int) ($mapWatch->get() === null), '|';
