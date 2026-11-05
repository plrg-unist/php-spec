<?php
gc_disable();
#[AllowDynamicProperties]
class GcNestedArrayCaptureRoot28 {
    public $head;
    public $tail;
    public $name;
    public function __destruct() { echo $this->name, '|'; }
}
#[AllowDynamicProperties]
class GcNestedArrayCaptureProxy28 {}
$leaf = new stdClass;
$weakLeaf = WeakReference::create($leaf);
$inner = [];
$inner[0] = $leaf;
$inner[1] = $leaf;
$token = [];
$token['left'] = $inner;
$token['right'] = $inner;
$second = [];
$second['deep'] = $token;
$collector = static function () use ($second, $inner, $leaf) {
    echo $second['deep']['left'][0] === $leaf && $second['deep']['right'][1] === $leaf && $inner[0] === $inner[1] ? 'T|' : 'BAD|';
    $held = new GcNestedArrayCaptureRoot28;
    $held->name = 'H';
    $heldProxy = new GcNestedArrayCaptureProxy28;
    $heldProxy->back = $held;
    $heldTable = (array) $heldProxy;
    $held->head = $heldTable;
    $held->tail = $heldProxy;
    $held->extra = 7;
    $wh = WeakReference::create($held);
    unset($heldProxy, $heldTable);

    $drop = new GcNestedArrayCaptureRoot28;
    $drop->name = 'D';
    $dropProxy = new GcNestedArrayCaptureProxy28;
    $dropProxy->back = $drop;
    $dropTable = (array) $dropProxy;
    $drop->head = $dropTable;
    $drop->tail = $dropProxy;
    $drop->extra = 8;
    $wd = WeakReference::create($drop);
    unset($dropProxy, $dropTable);

    $leafCopy = $inner[0];
    echo 'P|', gc_collect_cycles(), '|';
    $copy = $second;
    unset($copy);
    $parentCopy = $second['deep'];
    unset($parentCopy);
    $innerCopy = $inner;
    unset($innerCopy);
    unset($leafCopy);
    unset($drop);
    echo gc_collect_cycles(), '|';
    echo $wh->get() !== null && $wd->get() === null ? 'split|' : 'BAD|';
    echo gc_collect_cycles(), '|';
    unset($held);
    echo gc_collect_cycles(), '|';
    echo $wh->get() === null && $wd->get() === null ? 'dead|' : 'BAD|';
    echo gc_collect_cycles(), '|', ($second['deep']['left'][0] === $leaf && $second['deep']['right'][1] === $leaf && $inner[0] === $inner[1] ? 'live|' : 'BAD|'), 'END';
};
unset($leaf, $inner, $token, $second);
$collector();
echo $weakLeaf->get() !== null ? '|leaf-live' : '|BAD';
unset($collector);
echo $weakLeaf->get() === null ? '|leaf-dead' : '|BAD';
