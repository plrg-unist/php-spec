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
$token = [];
$token['leaf'] = $leaf;
$token['self'] = $token;
$collector = static function () use ($token) {
    echo $token['leaf'] === $token['self']['leaf'] && !isset($token['self']['self']) ? 'T|' : 'BAD|';
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

    $leafCopy = $token['self']['leaf'];
    echo 'P|', gc_collect_cycles(), '|';
    $copy = $token;
    unset($copy);
    $innerCopy = $token['self'];
    unset($innerCopy);
    unset($leafCopy);
    unset($drop);
    echo gc_collect_cycles(), '|';
    echo $wh->get() !== null && $wd->get() === null ? 'split|' : 'BAD|';
    echo gc_collect_cycles(), '|';
    unset($held);
    echo gc_collect_cycles(), '|';
    echo $wh->get() === null && $wd->get() === null ? 'dead|' : 'BAD|';
    echo gc_collect_cycles(), '|', ($token['leaf'] === $token['self']['leaf'] && !isset($token['self']['self']) ? 'live|' : 'BAD|'), 'END';
};
unset($leaf, $token);
$collector();
echo $weakLeaf->get() !== null ? '|leaf-live' : '|BAD';
unset($collector);
echo $weakLeaf->get() === null ? '|leaf-dead' : '|BAD';
