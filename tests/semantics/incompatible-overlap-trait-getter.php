<?php
trait IncompatibleOverlapGetterTrait68 {
    public int $value = 100 {
        get => $this->value + $this->answer(__METHOD__);
    }
}
class IncompatibleOverlapGetterBase68 {
    public string $value = 'base';
    public int $marker = 700;
    private function answer(string $method): int { return 7; }
    public function parentRead(): int {
        echo 'PARENT:', self::class, '/', static::class, '|';
        return $this->value;
    }
}
class IncompatibleOverlapGetterConsumer68 extends IncompatibleOverlapGetterBase68 {
    use IncompatibleOverlapGetterTrait68;
    private function answer(string $method): int {
        echo 'ANSWER:', self::class, '/', static::class, '/', $method, '|';
        return 13;
    }
}
class IncompatibleOverlapGetterGrand68 extends IncompatibleOverlapGetterConsumer68 {
    private function answer(string $method): int { return 900; }
}
$consumer = new IncompatibleOverlapGetterConsumer68();
$grand = new IncompatibleOverlapGetterGrand68();
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
