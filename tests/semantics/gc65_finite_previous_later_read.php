<?php
class GC65Incoming {}
class GC65First {
    public function __destruct() {
        global $oldWatch65;
        echo 'B|', (int) ($oldWatch65->get() === null), '|';
        throw new Exception('b65');
    }
}
class GC65Second {
    public function __destruct() {
        global $map65, $loopKey65, $result65, $oldWatch65, $incomingWatch65;
        $seen65 = $map65[$loopKey65];
        echo 'C|', (int) ($oldWatch65->get() === null), '|',
             (int) ($seen65 === $incomingWatch65->get()), '|',
             (int) ($result65 === 77), '|';
        throw new Exception('c65');
    }
}
class GC65Later {
    public function __destruct() {
        global $map65, $loopKey65, $result65, $oldWatch65, $incomingWatch65;
        $seen65 = $map65[$loopKey65];
        echo 'D|', (int) ($oldWatch65->get() === null), '|',
             (int) ($seen65 === $incomingWatch65->get()), '|',
             (int) ($result65 === 77), '|';
    }
}
class GC65Value {
    public $before = 17;
    public $first = null;
    public $second = null;
    public $later = null;
    public $after = 23;
    public function __destruct() {
        global $map65, $loopKey65, $oldWatch65;
        echo 'O|', (int) ($oldWatch65->get() === $this), '|';
        throw new Exception('a65');
    }
}
$map65 = new WeakMap;
$key65 = new stdClass;
$otherKey65 = new stdClass;
$old65 = new GC65Value;
$first65 = new GC65First;
$second65 = new GC65Second;
$later65 = new GC65Later;
$old65->first = $first65;
$old65->second = $second65;
$old65->later = $later65;
$incoming65 = new GC65Incoming;
$other65 = new GC65Incoming;
$map65[$key65] = $old65;
$map65[$otherKey65] = $other65;
$oldWatch65 = WeakReference::create($old65);
$firstWatch65 = WeakReference::create($first65);
$secondWatch65 = WeakReference::create($second65);
$laterWatch65 = WeakReference::create($later65);
$incomingWatch65 = WeakReference::create($incoming65);
$mapWatch65 = WeakReference::create($map65);
$keyWatch65 = WeakReference::create($key65);
unset($old65, $first65, $second65, $later65);
$result65 = 77;
$continued65 = 0;
echo 'S|';
try {
    foreach ($map65 as $loopKey65 => $loopValue65) {
        $loopValue65 = 0;
        $result65 = $map65[$loopKey65] = $incoming65;
        $continued65 = 1;
        echo 'BAD|';
    }
} catch (Exception $error65) {
    $previous65 = $error65->getPrevious();
    $earliest65 = $previous65->getPrevious();
    echo 'T|', $error65->getMessage(), '|', $error65->getLine(), '|',
         $previous65->getMessage(), '|', $previous65->getLine(), '|',
         $earliest65->getMessage(), '|', $earliest65->getLine(), '|',
         (int) ($earliest65->getPrevious() === null), '|',
         (int) ($result65 === 77), '|', $continued65, '|';
}
echo 'R|', (int) ($map65[$key65] === $incoming65), '|',
     (int) ($oldWatch65->get() === null), '|',
     (int) ($firstWatch65->get() === null), '|',
     (int) ($secondWatch65->get() === null), '|',
     (int) ($laterWatch65->get() === null), '|';
unset($error65, $previous65, $earliest65);
unset($map65);
echo 'M|', (int) ($mapWatch65->get() === null), '|',
     (int) ($incomingWatch65->get() === $incoming65), '|';
unset($incoming65);
echo 'V|', (int) ($incomingWatch65->get() === null), '|';
unset($key65, $otherKey65, $loopKey65, $other65);
echo 'K|', (int) ($keyWatch65->get() === null), '|';
