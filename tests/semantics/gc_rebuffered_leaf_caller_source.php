<?php
gc_disable();
#[AllowDynamicProperties]
class GcRebufferedRoot15 {
    public $head;
    public $tail;
    public $name;
    public function __destruct() { echo $this->name, '|'; }
}
#[AllowDynamicProperties]
class GcRebufferedProxy15 {}
$token = new stdClass;
$collector = static function () use ($token) {
    echo $token !== null ? 'T|' : 'BAD|';
    $held = new GcRebufferedRoot15;
    $held->name = 'H';
    $heldProxy = new GcRebufferedProxy15;
    $heldProxy->back = $held;
    $heldTable = (array) $heldProxy;
    $held->head = $heldTable;
    $held->tail = $heldProxy;
    $held->extra = 7;
    $wh = WeakReference::create($held);
    unset($heldProxy, $heldTable);

    $drop = new GcRebufferedRoot15;
    $drop->name = 'D';
    $dropProxy = new GcRebufferedProxy15;
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
