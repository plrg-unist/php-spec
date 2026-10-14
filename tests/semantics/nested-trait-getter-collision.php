<?php
trait NestedConflictGetterInner70 {
    public int $value = 100 {
        get => $this->value + $this->answer(__METHOD__, __TRAIT__);
    }
}
trait NestedConflictGetterOuter70 {
    use NestedConflictGetterInner70;
    public int $value = 100;
}
class NestedConflictGetterConsumer70 {
    use NestedConflictGetterOuter70;
    private function answer(string $method, string $trait): int {
        echo 'ANSWER:', self::class, '/', static::class, '/', $method, '/', $trait, '|';
        return 13;
    }
}
class NestedConflictGetterGrand70 extends NestedConflictGetterConsumer70 {
    private function answer(string $method, string $trait): int { return 900; }
}
$consumer = new NestedConflictGetterConsumer70();
$grand = new NestedConflictGetterGrand70();
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
