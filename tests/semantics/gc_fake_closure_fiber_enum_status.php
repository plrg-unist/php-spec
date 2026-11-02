<?php
enum GcFakeEnum09 { case One; }
function gcFakeFiberProbe09(string $name, Closure $closure): void {
    $copy = $closure;
    gc_collect_cycles();
    unset($copy);
    echo $name, '=', gc_status()['roots'], '|';
}
gc_disable();
echo 'Z|', gc_collect_cycles(), '|';
$enum = GcFakeEnum09::cases(...);
gcFakeFiberProbe09('enum', $enum);
$enumClone = clone $enum;
gcFakeFiberProbe09('enumClone', $enumClone);
$fiber = new Fiber(static function (): int { return 17; });
$weak = WeakReference::create($fiber);
$static = Fiber::getCurrent(...);
gcFakeFiberProbe09('fiberStatic', $static);
$objectStatic = $fiber->getCurrent(...);
gcFakeFiberProbe09('fiberObjectStatic', $objectStatic);
$arrayStatic = [Fiber::class, 'getCurrent'](...);
gcFakeFiberProbe09('fiberArrayStatic', $arrayStatic);
$arrayObjectStatic = [$fiber, 'getCurrent'](...);
gcFakeFiberProbe09('fiberArrayObjectStatic', $arrayObjectStatic);
$fromStatic = Closure::fromCallable([Fiber::class, 'getCurrent']);
gcFakeFiberProbe09('fiberFromStatic', $fromStatic);
$fromObjectStatic = Closure::fromCallable([$fiber, 'getCurrent']);
gcFakeFiberProbe09('fiberFromObjectStatic', $fromObjectStatic);
$fromString = Closure::fromCallable('Fiber::getCurrent');
gcFakeFiberProbe09('fiberFromString', $fromString);
$bound = $fiber->isStarted(...);
gcFakeFiberProbe09('fiberBound', $bound);
$fromBound = Closure::fromCallable([$fiber, 'isStarted']);
gcFakeFiberProbe09('fiberFromBound', $fromBound);
$staticClone = clone $static;
gcFakeFiberProbe09('fiberStaticClone', $staticClone);
unset($fiber);
echo 'weak=', (int)($weak->get() !== null), '|';
echo 'calls=', count($enum()), (int)($static() === null), (int)($bound() === false), '|END';
