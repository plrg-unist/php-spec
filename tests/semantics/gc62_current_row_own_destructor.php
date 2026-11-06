<?php
class GC62Incoming {}
class GC62Value {
    public function __destruct() {
        global $map62, $loopKey62, $result62, $throw62,
               $mapWatch62, $keyWatch62, $oldWatch62, $incomingWatch62;
        echo 'D|', (int) ($oldWatch62->get() === $this), '|';
        $seen62 = $map62[$loopKey62];
        echo 'C|', (int) ($mapWatch62->get() === $map62), '|',
             (int) ($keyWatch62->get() === $loopKey62), '|',
             (int) ($seen62 === $incomingWatch62->get()), '|',
             (int) ($result62 === 77), '|';
        if ($throw62) { throw new Exception('fresh-62'); }
    }
}
$throw62 = false;
$map62 = new WeakMap;
$key62 = new stdClass;
$otherKey62 = new stdClass;
$old62 = new GC62Value;
$incoming62 = new GC62Incoming;
$other62 = new GC62Incoming;
$map62[$key62] = $old62;
$map62[$otherKey62] = $other62;
$mapWatch62 = WeakReference::create($map62);
$keyWatch62 = WeakReference::create($key62);
$oldWatch62 = WeakReference::create($old62);
$incomingWatch62 = WeakReference::create($incoming62);
unset($old62);
$result62 = 77;
$continued62 = 0;
echo 'B|';
try {
    foreach ($map62 as $loopKey62 => $loopValue62) {
        $loopValue62 = 0;
        $result62 = $map62[$loopKey62] = $incoming62;
        $continued62 = 1;
        echo 'A|', (int) ($result62 === $incoming62), '|';
        break;
    }
} catch (Exception $error62) {
    $trace62 = $error62->getTrace();
    echo 'T|', $error62->getMessage(), '|', $error62->getLine(), '|',
         $trace62[0]['function'], '|', $trace62[0]['line'], '|',
         (int) ($result62 === 77), '|', $continued62, '|';
}
echo 'R|', (int) ($result62 === 77), '|',
     (int) ($result62 === $incoming62), '|', $continued62, '|',
     (int) ($loopValue62 === 0), '|',
     (int) ($map62[$key62] === $incoming62), '|',
     (int) ($oldWatch62->get() === null), '|';
unset($map62);
echo 'M|', (int) ($mapWatch62->get() === null), '|',
     (int) ($incomingWatch62->get() === $incoming62), '|';
unset($result62, $incoming62);
echo 'V|', (int) ($incomingWatch62->get() === null), '|';
unset($key62, $otherKey62, $loopKey62, $other62);
echo 'K|', (int) ($keyWatch62->get() === null), '|';
