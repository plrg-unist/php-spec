<?php
function gcFakeNamedReached09(): int { return 5; }
gc_disable();
echo 'Z|', gc_collect_cycles(), '|';
$named = gcFakeNamedReached09(...);
$namedFrom = Closure::fromCallable('gcFakeNamedReached09');
$intrinsic = gc_enabled(...);
$intrinsicFrom = Closure::fromCallable('gc_enabled');
$factory = Closure::fromCallable(...);
$clone = clone $intrinsic;
$boundCopy = $named->bindTo(null);
$identity = Closure::fromCallable($named);
$real = static function (): int { return 3; };
$copyNamed = $named;
$copyNamedFrom = $namedFrom;
$copyIntrinsic = $intrinsic;
$copyIntrinsicFrom = $intrinsicFrom;
$copyFactory = $factory;
$copyClone = $clone;
$copyBound = $boundCopy;
$copyReal = $real;
gc_collect_cycles();
unset($copyNamed, $copyNamedFrom, $copyIntrinsic, $copyIntrinsicFrom, $copyFactory, $copyClone, $copyBound, $copyReal);
gc_enabled();
echo (int)($identity === $named), '|', $named(), '|', $namedFrom(), '|', $real(), '|END';
