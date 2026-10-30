<?php
function gcFakeFunction09(): int { return 5; }
class GcFakeProducer09 {
    public const Closure CACHED = self::staticValue(...);
    public static function staticValue(): int { return 7; }
    public function boundValue(): int { return 11; }
}
function gcFakeProbe09(string $name, Closure $closure): void {
    $copy = $closure;
    gc_collect_cycles();
    unset($copy);
    echo $name, '=', gc_status()['roots'], '|';
}
gc_disable();
echo 'Z|', gc_collect_cycles(), '|';
$named = gcFakeFunction09(...);
gcFakeProbe09('named', $named);
$namedClone = clone $named;
gcFakeProbe09('namedClone', $namedClone);
$namedFrom = Closure::fromCallable('gcFakeFunction09');
gcFakeProbe09('namedFrom', $namedFrom);
$intrinsic = gc_enabled(...);
gcFakeProbe09('intrinsic', $intrinsic);
$intrinsicFrom = Closure::fromCallable('gc_enabled');
gcFakeProbe09('intrinsicFrom', $intrinsicFrom);
$intrinsicClone = clone $intrinsic;
gcFakeProbe09('intrinsicClone', $intrinsicClone);
$direct = GcFakeProducer09::staticValue(...);
gcFakeProbe09('method', $direct);
$arraySource = [GcFakeProducer09::class, 'staticValue'];
$array = $arraySource(...);
gcFakeProbe09('array', $array);
$stringSource = 'GcFakeProducer09::staticValue';
$string = $stringSource(...);
gcFakeProbe09('string', $string);
$constant = GcFakeProducer09::CACHED;
gcFakeProbe09('constant', $constant);
$fromArray = Closure::fromCallable([GcFakeProducer09::class, 'staticValue']);
gcFakeProbe09('fromArray', $fromArray);
$fromString = Closure::fromCallable('GcFakeProducer09::staticValue');
gcFakeProbe09('fromString', $fromString);
$factory = Closure::fromCallable(...);
gcFakeProbe09('factory', $factory);
$factoryClone = clone $factory;
gcFakeProbe09('factoryClone', $factoryClone);
$identity = Closure::fromCallable($named);
echo 'identity=', (int)($identity === $named), '|';
$boundCopy = $named->bindTo(null);
gcFakeProbe09('boundCopy', $boundCopy);
$object = new GcFakeProducer09;
$bound = $object->boundValue(...);
gcFakeProbe09('bound', $bound);
$boundFrom = Closure::fromCallable([$object, 'boundValue']);
gcFakeProbe09('boundFrom', $boundFrom);
$real = static function (): int { return 13; };
gcFakeProbe09('real', $real);
echo 'calls=', $named(), $direct(), $bound(), $real(), '|END';
