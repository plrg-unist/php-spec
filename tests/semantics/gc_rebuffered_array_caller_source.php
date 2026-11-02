<?php
gc_disable();
#[AllowDynamicProperties]
class GcBufferedArrayRoot17 {
    public $head;
    public $tail;
    public $name;
    public function __destruct() { echo $this->name, '|'; }
}
#[AllowDynamicProperties]
class GcBufferedArrayProxy17 {}
$token = [];
$token[0] = 11;
$collector = static function () use ($token) {
    echo $token[0] === 11 ? 'T|' : 'BAD|';
    $held = new GcBufferedArrayRoot17;
    $held->name = 'H';
    $heldProxy = new GcBufferedArrayProxy17;
    $heldProxy->back = $held;
    $heldTable = (array) $heldProxy;
    $held->head = $heldTable;
    $held->tail = $heldProxy;
    $held->extra = 7;
    $wh = WeakReference::create($held);
    unset($heldProxy, $heldTable);

    $drop = new GcBufferedArrayRoot17;
    $drop->name = 'D';
    $dropProxy = new GcBufferedArrayProxy17;
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
    echo gc_collect_cycles(), '|END';
};
unset($token);
$collector();
