<?php
gc_disable();
#[AllowDynamicProperties]
class GcBufferedArrayChildRoot19 {
    public $head;
    public $tail;
    public $name;
    public function __destruct() { echo $this->name, '|'; }
}
#[AllowDynamicProperties]
class GcBufferedArrayChildProxy19 {}
$leaf = new stdClass;
$leaf2 = $leaf;
$weakLeaf = WeakReference::create($leaf);
$token = [];
$token[0] = $leaf;
$token[1] = $leaf2;
$collector = static function () use ($token) {
    echo $token[0] === $token[1] ? 'T|' : 'BAD|';
    $held = new GcBufferedArrayChildRoot19;
    $held->name = 'H';
    $heldProxy = new GcBufferedArrayChildProxy19;
    $heldProxy->back = $held;
    $heldTable = (array) $heldProxy;
    $held->head = $heldTable;
    $held->tail = $heldProxy;
    $held->extra = 7;
    $wh = WeakReference::create($held);
    unset($heldProxy, $heldTable);

    $drop = new GcBufferedArrayChildRoot19;
    $drop->name = 'D';
    $dropProxy = new GcBufferedArrayChildProxy19;
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
    unset($leafCopy);
    unset($drop);
    echo gc_collect_cycles(), '|';
    echo $wh->get() !== null && $wd->get() === null ? 'split|' : 'BAD|';
    echo gc_collect_cycles(), '|';
    unset($held);
    echo gc_collect_cycles(), '|';
    echo $wh->get() === null && $wd->get() === null ? 'dead|' : 'BAD|';
    echo gc_collect_cycles(), '|', ($token[0] !== null && $token[1] !== null ? 'live|' : 'BAD|'), 'END';
};
unset($leaf, $leaf2, $token);
$collector();
echo $weakLeaf->get() !== null ? '|leaf-live' : '|BAD';
unset($collector);
echo $weakLeaf->get() === null ? '|leaf-dead' : '|BAD';
