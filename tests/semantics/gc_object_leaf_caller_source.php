<?php
gc_disable();
#[AllowDynamicProperties]
class GcLeafRoot13 {
    public $head;
    public $tail;
    public $name;
    public function __destruct() { echo $this->name, '|'; }
}
#[AllowDynamicProperties]
class GcLeafProxy13 {}
$token = new stdClass;
$collector = static function () use ($token) {
    echo $token !== null ? 'T|' : 'BAD|';
    $held = new GcLeafRoot13;
    $held->name = 'H';
    $heldProxy = new GcLeafProxy13;
    $heldProxy->back = $held;
    $heldTable = (array) $heldProxy;
    $held->head = $heldTable;
    $held->tail = $heldProxy;
    $held->extra = 7;
    $wh = WeakReference::create($held);
    unset($heldProxy, $heldTable);

    $drop = new GcLeafRoot13;
    $drop->name = 'D';
    $dropProxy = new GcLeafProxy13;
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
