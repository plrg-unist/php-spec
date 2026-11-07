<?php
class GC80ChildAuthor {
    public function __destruct() { echo 'D|'; }
}
$a = [new GC80ChildAuthor, 17];
echo 'B|';
$view = $a;
$before = gc_collect_cycles();
echo 'Q|', $before, '|';
$a[0] = 23;
echo 'W|', $a[0], '|', $view[1], '|';
unset($a);
echo 'K|';
unset($view);
echo 'V|';
$collected = gc_collect_cycles();
echo 'G|', $collected, '|';
register_shutdown_function(function () { echo 'S|'; });
echo 'E|';
