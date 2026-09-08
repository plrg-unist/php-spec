<?php
gc_disable();
$x = 1;
$a = [&$x];
$dead = [&$x];
$dead["self"] =& $dead;
unset($x, $dead);
echo gc_collect_cycles(), ":";
$b = $a;
$b[] = 0;
$b[0] = 9;
echo $a[0], $b[0];
