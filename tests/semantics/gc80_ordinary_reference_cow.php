<?php
class GC80ChildPeer {
    public function __destruct() { echo 'D|'; }
}
echo 'B|';
$a = [17, new GC80ChildPeer];
$view = $a;
$before = gc_collect_cycles();
echo 'Q|', $before, '|';
$ref =& $a[0];
$ref = 23;
echo 'W|', $view[0], '|', $a[0], '|';
unset($ref, $a);
echo 'K|';
unset($view);
echo 'V|';
$collected = gc_collect_cycles();
echo 'G|', $collected, '|';
register_shutdown_function(function () { echo 'S|'; });
echo 'E|';
