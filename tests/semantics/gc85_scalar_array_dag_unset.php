<?php
echo 'B|';
$seed = 17;
$leaf = [$seed];
$inner = [$leaf];
$a = [$inner, $inner];
$view = $a;
unset($inner, $leaf, $seed);
echo 'Q|', gc_collect_cycles(), '|';
unset($a[0]);
echo 'W|', isset($a[0]) ? 1 : 0, '|', $a[1][0][0], '|', $view[0][0][0], '|';
echo 'R|', gc_collect_cycles(), '|';
unset($a[1]);
echo 'U|', isset($a[1]) ? 1 : 0, '|', $view[1][0][0], '|';
unset($a);
echo 'K|';
unset($view);
echo 'V|G|', gc_collect_cycles(), '|E|';
