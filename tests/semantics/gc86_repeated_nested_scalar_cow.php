<?php
$seed = 17;
$leaf = [$seed];
$inner = [$seed, $leaf];
$a = [$inner, $inner];
$view = $a;
unset($inner, $leaf, $seed);
echo 'B|Q|', gc_collect_cycles(), '|';
$a[0][0] = 23;
echo 'W|', $a[0][0], '|', $a[1][0], '|', $view[0][0], '|';
echo 'R|', gc_collect_cycles(), '|';
$a[1] = 29;
echo 'U|', $a[1], '|', $view[1][0], '|';
unset($a);
echo 'K|';
unset($view);
echo 'V|G|', gc_collect_cycles(), '|E|';
