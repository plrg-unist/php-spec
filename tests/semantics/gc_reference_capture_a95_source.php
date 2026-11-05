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
function &values95() { global $v; echo "Y;"; yield 0 => $v; echo "N:",$v,";"; }
function sink95(&$x) { echo "S:",$x,";"; $x=33; echo "R:",$x,";"; }
function warning95($level,$message) { global $old; unset($GLOBALS['v']); $GLOBALS['v'] =& $GLOBALS['other']; $old=22; echo "H:",$GLOBALS['v'],":",$old,";"; return true; }
$v=11;
$old =& $v;
$other=44;
set_error_handler('warning95');
$collector = static function () use (&$v) {
    echo 'B;';
    $g = values95();
    sink95(...$g);
    echo 'V:',$GLOBALS['v'],':',$v,':',$GLOBALS['other'],';';
    unset($g);
    restore_error_handler();
    unset($GLOBALS['old']);
    echo $v === 22 && $GLOBALS['v'] === 44 ? 'T|' : 'BAD|';
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
    echo gc_collect_cycles(), '|', ($v === 22 && $GLOBALS['v'] === 44 ? 'live|' : 'BAD|'), 'END';
};
$collector();
echo $v === 44 && $other === 44 ? '|new-kept' : '|BAD';
$weakCollector = WeakReference::create($collector);
unset($collector);
echo $weakCollector->get() === null ? '|closure-dead' : '|BAD';
