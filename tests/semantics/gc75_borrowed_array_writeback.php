<?php
class GC75ChildAuthor {
    public function __destruct() { echo 'D|'; }
}
$a = [17, new GC75ChildAuthor];
echo 'B|';
$ref =& $a[0];
echo 'A|';
$ref = 23;
echo 'R|', $a[0], '|';
$a[1] = 29;
echo 'W|', $a[1], '|';
$a = $a;
echo 'C|';
unset($ref, $a);
echo 'U|';
$collected = gc_collect_cycles();
echo 'G|', $collected, '|';
register_shutdown_function(function () { echo 'S|'; });
echo 'E|';
