<?php
$seed = 17;
$inner = [$seed];
$a = [$inner, 29];
$view = $a;
unset($inner, $seed);
echo 'B|Q|', gc_collect_cycles(), '|';
$a[0][0] = 23;
echo 'W|', $a[0][0], '|', $view[0][0], '|', $view[1], '|';
unset($a);
echo 'K|';
unset($view);
echo 'V|G|', gc_collect_cycles(), '|E|';
