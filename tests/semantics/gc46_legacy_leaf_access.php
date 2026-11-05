<?php
class Value141 {}
$map = new WeakMap;
$a = new stdClass;
$b = new stdClass;
$x = new Value141;
$y = new Value141;
$map[$a] = $x;
$map[$b] = $y;
$wa = WeakReference::create($a);
$wb = WeakReference::create($b);
$wx = WeakReference::create($x);
$wy = WeakReference::create($y);
$wm = WeakReference::create($map);
unset($x, $y);
echo "P:", (int)isset($map[$a]), (int)isset($map[$b]), ";R:", (int)(($wx->get() instanceof Value141) && ($wx->get() === $map[$a])), (int)(($wy->get() instanceof Value141) && ($wy->get() === $map[$b])), ";D:", (int)($map[$a] !== $map[$b]), ";";
unset($a);
echo "A:", (int)($wa->get() === null), ";X:", (int)($wx->get() === null), ";B:", (int)(($wb->get() instanceof stdClass) && ($wb->get() === $b)), ";Y:", (int)(($wy->get() instanceof Value141) && ($wy->get() === $map[$b])), ";P:", (int)isset($map[$b]), ";";
unset($b);
echo "B:", (int)($wb->get() === null), ";Y:", (int)($wy->get() === null), ";M:", (int)($wm->get() instanceof WeakMap), ";E;";
