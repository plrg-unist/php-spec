<?php
gc_disable();
#[AllowDynamicProperties]
class GcReferenceCaptureCowRoot29 {
    public $head;
    public $tail;
    public $name;
    public function __destruct() { echo $this->name, '|'; }
}
#[AllowDynamicProperties]
class GcReferenceCaptureCowProxy29 {}
$leaf = new stdClass;
$weakLeaf = WeakReference::create($leaf);
$inner = [];
$inner['leaf'] = $leaf;
$inner['a'] = 0;
$inner['x'] = 0;
$token = [];
$token[0] = $inner;
$token[1] = $inner;
$other = $token;
$same = $token;
$alias =& $same;
$collector = static function () use (&$token, &$other, &$same, &$alias) {
    $token[0]['a'] = 17;
    $same[0]['x'] = 23;
    echo $token[0]['leaf'] === $other[1]['leaf']
        && $same[0]['leaf'] === $alias[1]['leaf']
        && $token[0]['a'] === 17 && $token[0]['x'] === 0
        && $other[0]['a'] === 0 && $other[0]['x'] === 0
        && $same[0]['a'] === 0 && $same[0]['x'] === 23
        && $alias[0]['x'] === 23 ? 'T|' : 'BAD|';
    $held = new GcReferenceCaptureCowRoot29;
    $held->name = 'H';
    $heldProxy = new GcReferenceCaptureCowProxy29;
    $heldProxy->back = $held;
    $heldTable = (array) $heldProxy;
    $held->head = $heldTable;
    $held->tail = $heldProxy;
    $held->extra = 7;
    $wh = WeakReference::create($held);
    unset($heldProxy, $heldTable);

    $drop = new GcReferenceCaptureCowRoot29;
    $drop->name = 'D';
    $dropProxy = new GcReferenceCaptureCowProxy29;
    $dropProxy->back = $drop;
    $dropTable = (array) $dropProxy;
    $drop->head = $dropTable;
    $drop->tail = $dropProxy;
    $drop->extra = 8;
    $wd = WeakReference::create($drop);
    unset($dropProxy, $dropTable);

    $leafCopy = $other[0]['leaf'];
    echo 'P|', gc_collect_cycles(), '|';
    $copy =& $token;
    unset($copy);
    $otherCopy =& $other;
    unset($otherCopy);
    $sameCopy =& $alias;
    unset($sameCopy);
    $innerCopy = $token[0];
    unset($innerCopy);
    $olderCopy = $other[0];
    unset($olderCopy);
    $sameInnerCopy = $same[0];
    unset($sameInnerCopy);
    unset($leafCopy);
    unset($drop);
    echo gc_collect_cycles(), '|';
    echo $wh->get() !== null && $wd->get() === null ? 'split|' : 'BAD|';
    echo gc_collect_cycles(), '|';
    unset($held);
    echo gc_collect_cycles(), '|';
    echo $wh->get() === null && $wd->get() === null ? 'dead|' : 'BAD|';
    echo gc_collect_cycles(), '|', ($token[0]['a'] === 17
        && $other[0]['a'] === 0 && $same[0]['x'] === 23
        && $alias[0]['x'] === 23 ? 'live|' : 'BAD|');
    echo 'END';
};
unset($leaf, $inner, $token, $other, $same, $alias);
$collector();
echo $weakLeaf->get() !== null ? '|leaf-live' : '|BAD';
unset($collector);
echo $weakLeaf->get() === null ? '|leaf-dead' : '|BAD';
