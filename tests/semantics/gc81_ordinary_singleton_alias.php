<?php
class GC81ChildAuthor {
    public function __destruct() { echo 'D|'; }
}
$slot = 17;
$a = [&$slot, new GC81ChildAuthor];
echo 'B|';
unset($slot);
$view = $a;
$before = gc_collect_cycles();
echo 'Q|', $before, '|';
$a[0] = 23;
echo 'W|', $view[0], '|', $a[0], '|';
unset($a);
echo 'K|';
unset($view);
echo 'V|';
$collected = gc_collect_cycles();
echo 'G|', $collected, '|';
register_shutdown_function(function () { echo 'S|'; });
echo 'E|';
