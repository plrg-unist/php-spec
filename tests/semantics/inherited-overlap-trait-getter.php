<?php
trait InheritedOverlapGetterTrait68 {
    public int $value = 100 {
        get => $this->value + $this->answer(__METHOD__);
    }
}
class InheritedOverlapGetterBase68 {
    public int $value = 10;
    public int $marker = 700;
    private function answer(string $method): int { return 7; }
    public function parentRead(): int {
        echo 'PARENT:', self::class, '/', static::class, '|';
        return $this->value;
    }
}
class InheritedOverlapGetterConsumer68 extends InheritedOverlapGetterBase68 {
    use InheritedOverlapGetterTrait68;
    private function answer(string $method): int {
        echo 'ANSWER:', self::class, '/', static::class, '/', $method, '|';
        return 13;
    }
}
class InheritedOverlapGetterGrand68 extends InheritedOverlapGetterConsumer68 {
    private function answer(string $method): int { return 900; }
}
$consumer = new InheritedOverlapGetterConsumer68();
$grand = new InheritedOverlapGetterGrand68();
$raw = (array) $consumer;
echo 'C:', $raw['value'], '/', $raw['marker'], '|';
$raw = (array) $grand;
echo 'G:', $raw['value'], '/', $raw['marker'], '|';
echo $consumer->value, '|';
echo $grand->value, '|';
echo $consumer->parentRead(), '|';
echo $grand->parentRead(), '|';
$grand->value = 300;
$raw = (array) $grand;
echo 'G:', $raw['value'], '/', $raw['marker'], '|';
echo $grand->value, '|';
echo $grand->parentRead(), '|';
