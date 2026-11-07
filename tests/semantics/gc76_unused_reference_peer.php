<?php
class GC76PeerChild {
    public function __destruct() { echo 'D|'; }
}
$a = [new GC76PeerChild, 17];
echo 'B|';
$ref =& $a[0];
echo 'R|';
unset($ref);
echo 'U|';
$a[0] = 23;
echo 'W|', $a[0], '|';
unset($a);
$collected = gc_collect_cycles();
echo 'G|', $collected, '|';
register_shutdown_function(function () { echo 'S|'; });
echo 'E|';
