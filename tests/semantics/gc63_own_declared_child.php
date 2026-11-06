<?php
class GC63Incoming {}
class GC63Child {
    public function __destruct() {
        global $map63, $loopKey63, $result63,
               $mapWatch63, $keyWatch63, $oldWatch63, $incomingWatch63;
        $seenChild63 = $map63[$loopKey63];
        echo 'C|', (int) ($oldWatch63->get() === null), '|',
             (int) ($mapWatch63->get() === $map63), '|',
             (int) ($keyWatch63->get() === $loopKey63), '|',
             (int) ($seenChild63 === $incomingWatch63->get()), '|',
             (int) ($result63 === 77), '|';
    }
}
class GC63Value {
    public $before = 17;
    public $child = null;
    public $after = 23;
    public function __destruct() {
        global $map63, $loopKey63, $result63, $throw63,
               $mapWatch63, $keyWatch63, $oldWatch63, $incomingWatch63;
        echo 'O|', (int) ($oldWatch63->get() === $this), '|',
             (int) ($this->before === 17), '|', (int) ($this->after === 23), '|';
        $seenOwn63 = $map63[$loopKey63];
        echo 'V|', (int) ($mapWatch63->get() === $map63), '|',
             (int) ($keyWatch63->get() === $loopKey63), '|',
             (int) ($seenOwn63 === $incomingWatch63->get()), '|',
             (int) ($result63 === 77), '|';
        if ($throw63) { throw new Exception('fresh-63'); }
    }
}
$throw63 = false;
$map63 = new WeakMap;
$key63 = new stdClass;
$otherKey63 = new stdClass;
$old63 = new GC63Value;
$child63 = new GC63Child;
$old63->child = $child63;
$incoming63 = new GC63Incoming;
$other63 = new GC63Incoming;
$map63[$key63] = $old63;
$map63[$otherKey63] = $other63;
$mapWatch63 = WeakReference::create($map63);
$keyWatch63 = WeakReference::create($key63);
$oldWatch63 = WeakReference::create($old63);
$childWatch63 = WeakReference::create($child63);
$incomingWatch63 = WeakReference::create($incoming63);
unset($old63, $child63);
$result63 = 77;
$continued63 = 0;
echo 'B|';
try {
    foreach ($map63 as $loopKey63 => $loopValue63) {
        $loopValue63 = 0;
        $result63 = $map63[$loopKey63] = $incoming63;
        $continued63 = 1;
        echo 'A|', (int) ($result63 === $incoming63), '|';
        break;
    }
} catch (Exception $error63) {
    $trace63 = $error63->getTrace();
    echo 'T|', $error63->getMessage(), '|', $error63->getLine(), '|',
         $trace63[0]['function'], '|', $trace63[0]['line'], '|',
         (int) ($result63 === 77), '|', $continued63, '|';
}
echo 'R|', (int) ($result63 === 77), '|',
     (int) ($result63 === $incoming63), '|', $continued63, '|',
     (int) ($loopValue63 === 0), '|',
     (int) ($map63[$key63] === $incoming63), '|',
     (int) ($oldWatch63->get() === null), '|',
     (int) ($childWatch63->get() === null), '|';
unset($map63);
echo 'M|', (int) ($mapWatch63->get() === null), '|',
     (int) ($incomingWatch63->get() === $incoming63), '|';
unset($result63, $incoming63);
echo 'V|', (int) ($incomingWatch63->get() === null), '|';
unset($key63, $otherKey63, $loopKey63, $other63);
echo 'K|', (int) ($keyWatch63->get() === null), '|';
