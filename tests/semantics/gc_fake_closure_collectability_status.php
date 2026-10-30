<?php
class GcFakeClosure09 {
    public static function staticValue(): int { return 5; }
    public function boundValue(): int { return 7; }
}
gc_disable();
echo 'Z|', gc_collect_cycles(), '|', gc_status()['roots'], '|';
$static = GcFakeClosure09::staticValue(...);
$staticCopy = $static;
gc_collect_cycles();
unset($staticCopy);
echo gc_status()['roots'], '|';
$object = new GcFakeClosure09;
$weak = WeakReference::create($object);
$bound = $object->boundValue(...);
$boundCopy = $bound;
echo gc_collect_cycles(), '|', gc_status()['roots'], '|';
unset($boundCopy);
echo gc_status()['roots'], '|';
$real = static function (): int { return 3; };
$realCopy = $real;
gc_collect_cycles();
unset($realCopy);
echo gc_status()['roots'], '|';
echo ($weak->get() === $object ? 'alive' : 'BAD'), '|';
echo $static(), '|', $bound(), '|', $real(), '|END';
