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
$otherLeaf = new stdClass;
$weakLeaf = WeakReference::create($leaf);
$weakOther = WeakReference::create($otherLeaf);
$inner = [];
$inner['leaf'] = $leaf;
$token = [];
$token[0] = $inner;
$token[1] = $inner;
$collector = static function () use ($token, $otherLeaf) {
    $token[0]['tag'] = 17;
    echo $token[0]['leaf'] === $token[1]['leaf'] && $token[0]['tag'] === 17 && !isset($token[1]['tag']) && $otherLeaf !== $token[0]['leaf'] ? 'T|' : 'BAD|';
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

    $leafCopy = $token[1]['leaf'];
    echo 'P|', gc_collect_cycles(), '|';
    $copy = $token;
    unset($copy);
    $innerCopy = $token[0];
    unset($innerCopy);
    $olderCopy = $token[1];
    unset($olderCopy);
    unset($leafCopy);
    unset($drop);
    echo gc_collect_cycles(), '|';
    echo $wh->get() !== null && $wd->get() === null ? 'split|' : 'BAD|';
    echo gc_collect_cycles(), '|';
    unset($held);
    echo gc_collect_cycles(), '|';
    echo $wh->get() === null && $wd->get() === null ? 'dead|' : 'BAD|';
    echo gc_collect_cycles(), '|', ($token[0]['leaf'] === $token[1]['leaf'] && $token[0]['tag'] === 17 && !isset($token[1]['tag']) && $otherLeaf !== $token[0]['leaf'] ? 'live|' : 'BAD|'), 'END';
};
unset($leaf, $otherLeaf, $inner, $token);
$collector();
echo $weakLeaf->get() !== null && $weakOther->get() !== null ? '|leaf-live' : '|BAD';
unset($collector);
echo $weakLeaf->get() === null && $weakOther->get() === null ? '|leaf-dead' : '|BAD';
