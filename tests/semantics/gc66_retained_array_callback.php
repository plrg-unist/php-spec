<?php
class ArrayLeaf66 {}
class ArrayChild66 {
    public function __destruct() {
        global $map66, $loopKey66, $oldWatch66, $result66;
        $seen66 = $map66[$loopKey66];
        echo 'C|', $oldWatch66->get() === null, '|', $seen66[0] === 29,
            '|', $result66 === 77, '|';
        unset($seen66);
    }
}
class ArrayRoot66 {
    public $child;
    public function __destruct() {
        global $map66, $loopKey66, $oldWatch66, $result66, $throw66;
        echo 'O|', $oldWatch66->get() === $this, '|';
        $seen66 = $map66[$loopKey66];
        echo 'U|', $seen66[0] === 29, '|', $result66 === 77, '|';
        unset($seen66);
        if ($throw66) {
            throw new Exception('array-own-66');
        }
    }
}
$throw66 = false;
$key66 = new stdClass;
$spareKey66 = new stdClass;
$leaf66 = new ArrayLeaf66;
$leafWatch66 = WeakReference::create($leaf66);
$inner66 = [$leaf66, 17];
$incoming66 = [29, $inner66];
unset($inner66, $leaf66);
$child66 = new ArrayChild66;
$old66 = new ArrayRoot66;
$old66->child = $child66;
$oldWatch66 = WeakReference::create($old66);
$spare66 = new ArrayLeaf66;
$map66 = new WeakMap;
$map66[$key66] = $old66;
$map66[$spareKey66] = $spare66;
$mapWatch66 = WeakReference::create($map66);
unset($child66, $old66);
$result66 = 77;
$continued66 = 0;
echo 'S|';
try {
    foreach ($map66 as $loopKey66 => $loopValue66) {
        $loopValue66 = 0;
        $result66 = $map66[$loopKey66] = $incoming66;
        $continued66 = 1;
        break;
    }
} catch (Exception $caught66) {
    echo 'T|', $caught66->getMessage(), '|', $caught66->getLine(), '|';
}
echo 'A|', $continued66, '|', $result66 === 77, '|',
    $oldWatch66->get() === null, '|', $leafWatch66->get() !== null, '|';
unset($loopValue66, $loopKey66, $map66);
echo 'M|', $mapWatch66->get() === null, '|', $leafWatch66->get() !== null, '|';
unset($incoming66);
echo 'R|', $leafWatch66->get() === null, '|';
unset($result66);
echo 'Z|', $leafWatch66->get() === null, '|';
unset($spare66, $key66, $spareKey66);
