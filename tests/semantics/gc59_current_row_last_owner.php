<?php
class GC59Value { public $child = null; }
class GC59Incoming {}
class GC59Child {
    public function __destruct() {
        global $map59, $loopKey59, $result59, $throw59,
               $mapWatch59, $keyWatch59, $oldWatch59, $incomingWatch59;
        $seen59 = $map59[$loopKey59];
        echo 'C|', (int) ($mapWatch59->get() === $map59), '|',
             (int) ($keyWatch59->get() === $loopKey59), '|',
             (int) ($oldWatch59->get() === null), '|',
             (int) ($seen59 === $incomingWatch59->get()), '|',
             (int) ($result59 === 77), '|';
        if ($throw59) { throw new Exception('fresh-59'); }
    }
}
$throw59 = false;
$map59 = new WeakMap;
$key59 = new stdClass;
$scalarKey59 = new stdClass;
$old59 = new GC59Value;
$child59 = new GC59Child;
$old59->child = $child59;
$incoming59 = new GC59Incoming;
$map59[$key59] = $old59;
$map59[$scalarKey59] = 17;
$mapWatch59 = WeakReference::create($map59);
$keyWatch59 = WeakReference::create($key59);
$oldWatch59 = WeakReference::create($old59);
$childWatch59 = WeakReference::create($child59);
$incomingWatch59 = WeakReference::create($incoming59);
unset($old59, $child59);
$result59 = 77;
$continued59 = 0;
echo 'B|';
try {
    foreach ($map59 as $loopKey59 => $loopValue59) {
        $loopValue59 = 0;
        $result59 = $map59[$loopKey59] = $incoming59;
        $continued59 = 1;
        echo 'A|', (int) ($result59 === $incoming59), '|';
        break;
    }
} catch (Exception $error59) {
    $trace59 = $error59->getTrace();
    echo 'T|', $error59->getMessage(), '|', $trace59[0]['function'], '|',
         (int) ($result59 === 77), '|', $continued59, '|';
}
echo 'R|', (int) ($result59 === 77), '|',
     (int) ($result59 === $incoming59), '|', $continued59, '|',
     (int) ($loopValue59 === 0), '|',
     (int) ($map59[$key59] === $incoming59), '|',
     (int) ($oldWatch59->get() === null), '|',
     (int) ($childWatch59->get() === null), '|';
unset($map59);
echo 'M|', (int) ($mapWatch59->get() === null), '|',
     (int) ($incomingWatch59->get() === $incoming59), '|';
unset($result59, $incoming59);
echo 'V|', (int) ($incomingWatch59->get() === null), '|';
unset($key59, $scalarKey59, $loopKey59);
echo 'K|', (int) ($keyWatch59->get() === null), '|';
