<?php
trait PrivateOverlapGetterTrait69 {
    public int $value = 100 {
        get => $this->value + $this->answer(__METHOD__);
    }
}
class PrivateOverlapGetterBase69 {
    private int $value = 7;
    public int $marker = 700;
    public function parentRead(): int {
        echo 'PARENT:', self::class, '/', static::class, '|';
        return $this->value;
    }
}
class PrivateOverlapGetterConsumer69 extends PrivateOverlapGetterBase69 {
    use PrivateOverlapGetterTrait69;
    private function answer(string $method): int {
        echo 'ANSWER:', self::class, '/', static::class, '/', $method, '|';
        return 13;
    }
}
class PrivateOverlapGetterGrand69 extends PrivateOverlapGetterConsumer69 {
    private function answer(string $method): int { return 900; }
}
$privateKey = "\0PrivateOverlapGetterBase69\0value";
$consumer = new PrivateOverlapGetterConsumer69();
$grand = new PrivateOverlapGetterGrand69();
$raw = (array) $consumer;
echo 'C:', $raw['value'], '/', ($raw[$privateKey] ?? 'ABSENT'), '/', $raw['marker'], '|';
$raw = (array) $grand;
echo 'G:', $raw['value'], '/', ($raw[$privateKey] ?? 'ABSENT'), '/', $raw['marker'], '|';
echo $consumer->value, '|';
echo $grand->value, '|';
echo $consumer->parentRead(), '|';
echo $grand->parentRead(), '|';
$grand->value = 300;
$raw = (array) $grand;
echo 'G:', $raw['value'], '/', ($raw[$privateKey] ?? 'ABSENT'), '/', $raw['marker'], '|';
echo $grand->value, '|';
echo $grand->parentRead(), '|';
