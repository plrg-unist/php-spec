<?php
trait NestedGetterInner70 {
    public int $value = 100 {
        get => $this->value + $this->answer(__METHOD__, __TRAIT__);
    }
}
trait NestedGetterOuter70 {
    use NestedGetterInner70;
}
class NestedGetterConsumer70 {
    use NestedGetterOuter70;
    private function answer(string $method, string $trait): int {
        echo 'ANSWER:', self::class, '/', static::class, '/', $method, '/', $trait, '|';
        return 13;
    }
}
class NestedGetterGrand70 extends NestedGetterConsumer70 {
    private function answer(string $method, string $trait): int { return 900; }
}
$consumer = new NestedGetterConsumer70();
$grand = new NestedGetterGrand70();
$raw = (array) $consumer;
echo 'C:', $raw['value'], '|';
$raw = (array) $grand;
echo 'G:', $raw['value'], '|';
echo $consumer->value, '|';
echo $grand->value, '|';
$grand->value = 300;
$raw = (array) $grand;
echo 'G:', $raw['value'], '|';
echo $grand->value, '|';
