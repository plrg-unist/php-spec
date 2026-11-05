<?php
class GC34OwnRecreate {
    public function __destruct() {
        global $mapWatch;
        $old = $mapWatch->get();
        unset($GLOBALS['mapWatch']);
        $GLOBALS['newMapWatch'] = WeakReference::create($old);
        echo 'OWN1|', (int) ($GLOBALS['newMapWatch']->get() === $old), '|';
    }
}
class GC34OwnRecreateLater {
    public function __destruct() { echo 'OWN2|'; }
}
class GC34IncomingRecreate {
    public function __destruct() {
        echo 'IN|', (int) ($GLOBALS['newMapWatch']->get() !== null), '|';
    }
}
$map = new WeakMap;
$mapWatch = WeakReference::create($map);
$first = new stdClass;
$second = new stdClass;
$outer = new WeakMap;
$map[$first] = new GC34OwnRecreate;
$map[$second] = new GC34OwnRecreateLater;
$outer[$map] = new GC34IncomingRecreate;
echo 'B|';
unset($map);
echo 'A|', (int) ($GLOBALS['newMapWatch']->get() === null), '|';
