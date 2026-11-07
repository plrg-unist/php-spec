<?php
class GC81ChildPeer {
    public function __destruct() { echo 'D|'; }
}
echo 'B|';
$slot = 17;
$a = [&$slot, 17, &$slot, new GC81ChildPeer];
$view = $a;
$before = gc_collect_cycles();
echo 'Q|', $before, '|';
$a[0] = 23;
echo 'W|', $slot, '|', $a[0], '|', $a[2], '|', $view[0], '|', $view[2], '|';
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
