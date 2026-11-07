<?php
class GC82ChildAuthor {
    public function __destruct() { echo 'D|'; }
}
$slot = 17;
$a = [&$slot, new GC82ChildAuthor];
unset($slot);
$view = $a;
echo 'B|';
$before = gc_collect_cycles(); echo 'Q|', $before, '|';
$ref =& $a[0];
$ref = 23;
echo 'W|', $view[0], '|', $a[0], '|', $ref, '|';
unset($a); echo 'K|';
unset($ref); echo 'R|';
unset($view); echo 'V|';
$collected = gc_collect_cycles(); echo 'G|', $collected, '|';
register_shutdown_function(function () { echo 'S|'; });
echo 'E|';
