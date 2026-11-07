<?php
class GC82ChildPeer {
    public function __destruct() { echo 'D|'; }
}
echo 'B|';
$slot = 17;
$a = [&$slot, 17, &$slot, new GC82ChildPeer];
$view = $a;
$before = gc_collect_cycles();
echo 'Q|', $before, '|';
$ref =& $a[0];
echo 'A|';
$ref = 23;
echo 'W|', $slot, '|', $a[0], '|', $a[2], '|', $view[0], '|', $view[2], '|';
unset($ref);
echo 'R|';
unset($a);
echo 'K|';
unset($view);
echo 'V|', $slot, '|';
unset($slot);
echo 'F|';
$collected = gc_collect_cycles();
echo 'G|', $collected, '|';
register_shutdown_function(function () { echo 'S|'; });
echo 'E|';
