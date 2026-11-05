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
$otherLeaf = new stdClass;
$weakLeaf = WeakReference::create($leaf);
$weakOther = WeakReference::create($otherLeaf);
$token = [];
$token[0] = $leaf;
$token[1] = $leaf;
$second = [];
$second['shared'] = $leaf;
$second['own'] = $otherLeaf;
$collector = static function () use ($token, $leaf, $second, $otherLeaf) {
    echo $token[0] === $token[1] && $token[0] === $leaf && $second['shared'] === $leaf && $second['own'] === $otherLeaf ? 'T|' : 'BAD|';
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
    $otherCopy = $second['own'];
    echo 'P|', gc_collect_cycles(), '|';
    $copy = $token;
    unset($copy);
    $secondCopy = $second;
    unset($secondCopy);
    unset($leafCopy);
    unset($otherCopy);
    unset($drop);
    echo gc_collect_cycles(), '|';
    echo $wh->get() !== null && $wd->get() === null ? 'split|' : 'BAD|';
    echo gc_collect_cycles(), '|';
    unset($held);
    echo gc_collect_cycles(), '|';
    echo $wh->get() === null && $wd->get() === null ? 'dead|' : 'BAD|';
    echo gc_collect_cycles(), '|', ($token[0] === $leaf && $second['shared'] === $leaf && $second['own'] === $otherLeaf ? 'live|' : 'BAD|'), 'END';
};
unset($leaf, $otherLeaf, $token, $second);
$collector();
echo $weakLeaf->get() !== null && $weakOther->get() !== null ? '|leaf-live' : '|BAD';
unset($collector);
echo $weakLeaf->get() === null && $weakOther->get() === null ? '|leaf-dead' : '|BAD';
