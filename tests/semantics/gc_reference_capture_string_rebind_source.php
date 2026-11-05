<?php
gc_disable();
#[AllowDynamicProperties]
class GcReferenceCaptureRoot29 {
    public $head;
    public $tail;
    public $name;
    public function __destruct() { echo $this->name, '|'; }
}
#[AllowDynamicProperties]
class GcReferenceCaptureProxy29 {}
$prefix = 'head';
$v = $prefix . '-tail';
$collector = static function () use (&$v) {
    $v .= '-inside';
    echo $v === 'head-tail-inside' ? 'T|' : 'BAD|';
    $held = new GcReferenceCaptureRoot29;
    $held->name = 'H';
    $heldProxy = new GcReferenceCaptureProxy29;
    $heldProxy->back = $held;
    $heldTable = (array) $heldProxy;
    $held->head = $heldTable;
    $held->tail = $heldProxy;
    $held->extra = 7;
    $wh = WeakReference::create($held);
    unset($heldProxy, $heldTable);

    $drop = new GcReferenceCaptureRoot29;
    $drop->name = 'D';
    $dropProxy = new GcReferenceCaptureProxy29;
    $dropProxy->back = $drop;
    $dropTable = (array) $dropProxy;
    $drop->head = $dropTable;
    $drop->tail = $dropProxy;
    $drop->extra = 8;
    $wd = WeakReference::create($drop);
    unset($dropProxy, $dropTable);

    echo 'P|', gc_collect_cycles(), '|';
    $copy =& $v;
    unset($copy);
    unset($drop);
    echo gc_collect_cycles(), '|';
    echo $wh->get() !== null && $wd->get() === null ? 'split|' : 'BAD|';
    echo gc_collect_cycles(), '|';
    unset($held);
    echo gc_collect_cycles(), '|';
    echo $wh->get() === null && $wd->get() === null ? 'dead|' : 'BAD|';
    echo gc_collect_cycles(), '|', ($v === 'head-tail-inside' ? 'live|' : 'BAD|'), 'END';
};
unset($v);
$v = 'new-global';
$collector();
echo $v === 'new-global' ? '|new-kept' : '|BAD';
$weakCollector = WeakReference::create($collector);
unset($collector);
echo $weakCollector->get() === null ? '|closure-dead' : '|BAD';
