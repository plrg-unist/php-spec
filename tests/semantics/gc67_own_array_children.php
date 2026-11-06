<?php
class ArrayReplacement67 {}
class ArrayFirst67 {
    public function __destruct() {
        global $map67, $loopKey67, $oldWatch67, $expected67, $result67;
        $seen67 = $map67[$loopKey67];
        echo 'F|', $oldWatch67->get() === null, '|', $seen67 === $expected67,
            '|', $result67 === 77, '|';
    }
}
class ArraySecond67 {
    public function __destruct() {
        global $map67, $loopKey67, $oldWatch67, $expected67, $result67;
        $seen67 = $map67[$loopKey67];
        echo 'S|', $oldWatch67->get() === null, '|', $seen67 === $expected67,
            '|', $result67 === 77, '|';
    }
}
class ArrayTail67 {
    public function __destruct() {
        global $map67, $loopKey67, $oldWatch67, $expected67, $result67;
        $seen67 = $map67[$loopKey67];
        echo 'L|', $oldWatch67->get() === null, '|', $seen67 === $expected67,
            '|', $result67 === 77, '|';
    }
}
class ArrayOwner67 {
    public $box;
    public $tail;
    public function __destruct() {
        global $map67, $loopKey67, $oldWatch67, $expected67, $result67, $throw67;
        echo 'O|', $oldWatch67->get() === $this, '|';
        $seen67 = $map67[$loopKey67];
        echo 'U|', $seen67 === $expected67, '|', $result67 === 77, '|';
        if ($throw67) {
            throw new Exception('own-array-67');
        }
    }
}
$throw67 = false;
$key67 = new stdClass;
$spareKey67 = new stdClass;
$incoming67 = new ArrayReplacement67;
$expected67 = $incoming67;
$first67 = new ArrayFirst67;
$second67 = new ArraySecond67;
$tail67 = new ArrayTail67;
$firstWatch67 = WeakReference::create($first67);
$secondWatch67 = WeakReference::create($second67);
$tailWatch67 = WeakReference::create($tail67);
$old67 = new ArrayOwner67;
$oldWatch67 = WeakReference::create($old67);
$box67 = [17, $first67, 23, $second67, 29];
$old67->box = $box67;
$old67->tail = $tail67;
unset($box67, $first67, $second67, $tail67);
$spare67 = new ArrayReplacement67;
$map67 = new WeakMap;
$map67[$key67] = $old67;
$map67[$spareKey67] = $spare67;
$mapWatch67 = WeakReference::create($map67);
unset($old67);
$result67 = 77;
$continued67 = 0;
echo 'B|';
try {
    foreach ($map67 as $loopKey67 => $loopValue67) {
        $loopValue67 = 0;
        $result67 = $map67[$loopKey67] = $incoming67;
        $continued67 = 1;
        break;
    }
} catch (Exception $caught67) {
    echo 'T|', $caught67->getMessage(), '|', $caught67->getLine(), '|';
}
echo 'A|', $continued67, '|', $result67 === 77, '|',
    $oldWatch67->get() === null, '|', $firstWatch67->get() === null, '|',
    $secondWatch67->get() === null, '|', $tailWatch67->get() === null, '|';
unset($loopValue67, $loopKey67, $map67);
echo 'M|', $mapWatch67->get() === null, '|';
unset($expected67, $incoming67, $result67, $spare67, $key67, $spareKey67);
