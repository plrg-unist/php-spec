<?php
enum GcFakeFiberEnumReached09 { case One; }
gc_disable();
echo 'Z|', gc_collect_cycles(), '|';
$enum = GcFakeFiberEnumReached09::cases(...);
$fiber = new Fiber(static function (): int { return 17; });
$weak = WeakReference::create($fiber);
$static = Fiber::getCurrent(...);
$objectStatic = $fiber->getCurrent(...);
$pair = [$fiber, 'getCurrent'];
$arrayStatic = $pair(...);
$fromStatic = Closure::fromCallable([$fiber, 'getCurrent']);
$bound = $fiber->isStarted(...);
$clone = clone $static;
$copyEnum = $enum;
$copyStatic = $static;
$copyObjectStatic = $objectStatic;
$copyArrayStatic = $arrayStatic;
$copyFromStatic = $fromStatic;
$copyBound = $bound;
$copyClone = $clone;
gc_collect_cycles();
unset($copyEnum, $copyStatic, $copyObjectStatic, $copyArrayStatic, $copyFromStatic, $copyBound, $copyClone);
gc_enabled();
unset($fiber, $pair);
$cases = $enum();
echo (int)($cases[0] === GcFakeFiberEnumReached09::One), '|', (int)($static() === null), (int)($clone() === null), (int)($bound() === false), '|', (int)($weak->get() !== null), '|END';
