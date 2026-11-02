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
$token = [];
$token[0] = $leaf;
$collector = static function () use ($token) {
    echo 'T|';
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

    echo 'P|', gc_collect_cycles(), '|';
    $copy = $token;
    unset($copy);
    unset($drop);
    echo gc_collect_cycles(), '|';
    echo $wh->get() !== null && $wd->get() === null ? 'split|' : 'BAD|';
    echo gc_collect_cycles(), '|';
    unset($held);
    echo gc_collect_cycles(), '|';
    echo $wh->get() === null && $wd->get() === null ? 'dead|' : 'BAD|';
    echo gc_collect_cycles(), '|', ($token[0] !== null ? 'live|' : 'BAD|'), 'END';
};
$collector();
