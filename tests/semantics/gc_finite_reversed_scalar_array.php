<?php
gc_disable();
#[AllowDynamicProperties]
class GcArrayRoot16 {
    public $head;
    public $tail;
    public $name;
    public function __destruct() { echo $this->name, '|'; }
}
#[AllowDynamicProperties]
class GcArrayProxy16 {}
$seed = 11;
$token = [];
$token[0] = 11;
$collector = static function () use ($token, $seed) {
    echo 'C|', $seed, '|';
    echo $token[0] === 11 ? 'T|' : 'BAD|';
    $held = new GcArrayRoot16;
    $held->name = 'H';
    $heldProxy = new GcArrayProxy16;
    $heldProxy->back = $held;
    $heldTable = (array) $heldProxy;
    $held->head = $heldTable;
    $held->tail = $heldProxy;
    $held->extra = 7;
    $wh = WeakReference::create($held);
    unset($heldProxy, $heldTable);

    $drop = new GcArrayRoot16;
    $drop->name = 'D';
    $dropProxy = new GcArrayProxy16;
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
$collector();
