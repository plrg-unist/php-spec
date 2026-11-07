<?php
class GC83ChildAuthor {
    public function __destruct() { echo 'D|'; }
}
$a = [new GC83ChildAuthor];
$first =& $a[0];
echo 'B|';
$before = gc_collect_cycles(); echo 'Q|', $before, '|';
$second =& $a[0]; echo 'R|';
$cleared = gc_collect_cycles(); echo 'C|', $cleared, '|';
unset($second); echo 'U|';
$first = 23; echo 'W|', $a[0], '|', $first, '|';
unset($first); unset($a); echo 'F|';
register_shutdown_function(function () { echo 'S|'; });
echo 'E|';
