<?php
class GcFakeMethodReached09 {
    public const Closure CACHED = self::value(...);
    public static function value(): int { return 7; }
    public function bound(): int { return 11; }
}
gc_disable();
echo 'Z|', gc_collect_cycles(), '|';
$method = GcFakeMethodReached09::value(...);
$pair = [GcFakeMethodReached09::class, 'value'];
$array = $pair(...);
$name = 'GcFakeMethodReached09::value';
$string = $name(...);
$constant = GcFakeMethodReached09::CACHED;
$from = Closure::fromCallable([GcFakeMethodReached09::class, 'value']);
$object = new GcFakeMethodReached09;
$bound = $object->bound(...);
$copyMethod = $method;
$copyArray = $array;
$copyString = $string;
$copyConstant = $constant;
$copyFrom = $from;
$copyBound = $bound;
gc_collect_cycles();
unset($copyMethod, $copyArray, $copyString, $copyConstant, $copyFrom, $copyBound);
gc_enabled();
echo $method(), $array(), $string(), $constant(), $from(), '|', $bound(), '|END';
