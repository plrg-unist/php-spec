<?php
class GcFakeClosureReached09 {
    public static function staticValue(): int { return 5; }
    public function boundValue(): int { return 7; }
}
gc_disable();
echo 'Z|', gc_collect_cycles(), '|';
$static = GcFakeClosureReached09::staticValue(...);
$staticCopy = $static;
gc_collect_cycles();
unset($staticCopy);
gc_enabled();
$object = new GcFakeClosureReached09;
$weak = WeakReference::create($object);
$bound = $object->boundValue(...);
$boundCopy = $bound;
gc_collect_cycles();
unset($boundCopy);
gc_enabled();
$clone = clone $static;
$cloneCopy = $clone;
gc_collect_cycles();
unset($cloneCopy);
gc_enabled();
$real = static function (): int { return 3; };
$realCopy = $real;
gc_collect_cycles();
unset($realCopy);
gc_enabled();
echo ($weak->get() === $object ? 'alive' : 'BAD'), '|';
echo $static(), '|', $bound(), '|', $clone(), '|', $real(), '|END';
