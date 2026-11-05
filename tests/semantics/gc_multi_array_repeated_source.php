<?php
gc_disable();
#[AllowDynamicProperties]
class GcMultipleArrayCaptureRoot27 {
    public $head;
    public $tail;
    public $name;
    public function __destruct() { echo $this->name, '|'; }
}
#[AllowDynamicProperties]
class GcMultipleArrayCaptureProxy27 {}
$leaf = new stdClass;
$weakLeaf = WeakReference::create($leaf);
$token = [];
$token[0] = $leaf;
$token[1] = $leaf;
$second = $token;
$seed = 11;
$collector = static function () use ($token, $seed, $second) {
    echo $token === $second && $token[0] === $token[1] && $seed === 11 ? 'T|' : 'BAD|';
    $held = new GcMultipleArrayCaptureRoot27;
    $held->name = 'H';
    $heldProxy = new GcMultipleArrayCaptureProxy27;
    $heldProxy->back = $held;
    $heldTable = (array) $heldProxy;
    $held->head = $heldTable;
    $held->tail = $heldProxy;
    $held->extra = 7;
    $wh = WeakReference::create($held);
    unset($heldProxy, $heldTable);

    $drop = new GcMultipleArrayCaptureRoot27;
    $drop->name = 'D';
    $dropProxy = new GcMultipleArrayCaptureProxy27;
    $dropProxy->back = $drop;
    $dropTable = (array) $dropProxy;
    $drop->head = $dropTable;
    $drop->tail = $dropProxy;
    $drop->extra = 8;
    $wd = WeakReference::create($drop);
    unset($dropProxy, $dropTable);

    $leafCopy = $token[0];
    echo 'P|', gc_collect_cycles(), '|';
    $copy = $token;
    unset($copy);
    $secondCopy = $second;
    unset($secondCopy);
    unset($leafCopy);
    unset($drop);
    echo gc_collect_cycles(), '|';
    echo $wh->get() !== null && $wd->get() === null ? 'split|' : 'BAD|';
    echo gc_collect_cycles(), '|';
    unset($held);
    echo gc_collect_cycles(), '|';
    echo $wh->get() === null && $wd->get() === null ? 'dead|' : 'BAD|';
    echo gc_collect_cycles(), '|', ($token[0] === $second[1] && $seed === 11 ? 'live|' : 'BAD|'), 'END';
};
unset($leaf, $token, $second);
$collector();
echo $weakLeaf->get() !== null ? '|leaf-live' : '|BAD';
unset($collector);
echo $weakLeaf->get() === null ? '|leaf-dead' : '|BAD';
