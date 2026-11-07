<?php
class GC83ChildPeer {
    public function __destruct() { echo 'D|'; }
}
echo 'B|';
$a = [new GC83ChildPeer];
$first =& $a[0];
$second =& $a[0];
$before = gc_collect_cycles();
echo 'Q|', $before, '|';
$third =& $a[0];
echo 'R|';
$beforeRebind = gc_collect_cycles();
echo 'T|', $beforeRebind, '|';
$third =& $a[0];
echo 'A|';
$beforeUnset = gc_collect_cycles();
echo 'C|', $beforeUnset, '|';
unset($third);
echo 'U|';
$first = 23;
echo 'W|', $a[0], '|', $second, '|';
unset($first, $second, $a);
echo 'F|';
register_shutdown_function(function () { echo 'S|'; });
echo 'E|';
