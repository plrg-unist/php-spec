<?php
class GcFakeClosureClone09 {
    public static function value(): int { return 5; }
}
gc_disable();
echo 'Z|', gc_collect_cycles(), '|';
$original = GcFakeClosureClone09::value(...);
$originalCopy = $original;
gc_collect_cycles();
unset($originalCopy);
echo gc_status()['roots'], '|';
$clone = clone $original;
$cloneCopy = $clone;
gc_collect_cycles();
unset($cloneCopy);
echo gc_status()['roots'], '|', $original(), '|', $clone(), '|END';
