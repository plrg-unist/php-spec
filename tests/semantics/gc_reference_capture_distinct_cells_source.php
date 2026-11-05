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
$leaf = new stdClass;
$weakLeaf = WeakReference::create($leaf);
$token = [];
$token[0] = $leaf;
$token[1] = $leaf;
$other = $token;
$collector = static function () use (&$token, &$other) {
    echo $token[0] === $other[1] ? 'T|' : 'BAD|';
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

    $leafCopy = $token[0];
    echo 'P|', gc_collect_cycles(), '|';
    $copy =& $token;
    unset($copy);
    $otherCopy =& $other;
    unset($otherCopy);
    unset($leafCopy);
    unset($drop);
    echo gc_collect_cycles(), '|';
    echo $wh->get() !== null && $wd->get() === null ? 'split|' : 'BAD|';
    echo gc_collect_cycles(), '|';
    unset($held);
    echo gc_collect_cycles(), '|';
    echo $wh->get() === null && $wd->get() === null ? 'dead|' : 'BAD|';
    echo gc_collect_cycles(), '|', ($token[0] === $other[1] ? 'live|' : 'BAD|');
    $other = null;
    echo $token[0] !== null ? 'kept|' : 'BAD|';
    echo 'END';
};
unset($leaf, $token, $other);
$collector();
echo $weakLeaf->get() !== null ? '|leaf-live' : '|BAD';
unset($collector);
echo $weakLeaf->get() === null ? '|leaf-dead' : '|BAD';
