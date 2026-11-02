<?php
gc_disable();
#[AllowDynamicProperties]
class GcBufferedRoot14 {
    public $head;
    public $tail;
    public $name;
    public function __destruct() { echo $this->name, '|'; }
}
#[AllowDynamicProperties]
class GcBufferedProxy14 {}
$token = new stdClass;
$collector = static function () use ($token) {
    echo $token !== null ? 'T|' : 'BAD|';
    $held = new GcBufferedRoot14;
    $held->name = 'H';
    $heldProxy = new GcBufferedProxy14;
    $heldProxy->back = $held;
    $heldTable = (array) $heldProxy;
    $held->head = $heldTable;
    $held->tail = $heldProxy;
    $held->extra = 7;
    $wh = WeakReference::create($held);
    unset($heldProxy, $heldTable);

    $drop = new GcBufferedRoot14;
    $drop->name = 'D';
    $dropProxy = new GcBufferedProxy14;
    $dropProxy->back = $drop;
    $dropTable = (array) $dropProxy;
    $drop->head = $dropTable;
    $drop->tail = $dropProxy;
    $drop->extra = 8;
    $wd = WeakReference::create($drop);
    unset($dropProxy, $dropTable);

    echo 'P|', gc_collect_cycles(), '|';
    unset($drop);
    echo gc_collect_cycles(), '|';
    echo $wh->get() !== null && $wd->get() === null ? 'split|' : 'BAD|';
    echo gc_collect_cycles(), '|';
    unset($held);
    echo gc_collect_cycles(), '|';
    echo $wh->get() === null && $wd->get() === null ? 'dead|' : 'BAD|';
    echo gc_collect_cycles(), '|END';
};
unset($token);
$collector();
