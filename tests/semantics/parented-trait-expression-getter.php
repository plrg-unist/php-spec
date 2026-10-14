<?php
trait ParentedTraitExpressionGetterTrait67 {
    public int $value = 100 {
        get => $this->value + $this->answer(__METHOD__);
    }
}
class ParentedTraitExpressionGetterBase67 {
    public int $marker = 700;
    private function answer(string $method): int { return 7; }
    public function parentRead(): int {
        echo 'PARENT:', self::class, '/', static::class, '|';
        return $this->value;
    }
}
class ParentedTraitExpressionGetterConsumer67 extends ParentedTraitExpressionGetterBase67 {
    use ParentedTraitExpressionGetterTrait67;
    private function answer(string $method): int {
        echo 'ANSWER:', self::class, '/', static::class, '/', $method, '|';
        return 13;
    }
}
class ParentedTraitExpressionGetterGrand67 extends ParentedTraitExpressionGetterConsumer67 {
    private function answer(string $method): int { return 900; }
}
$consumer = new ParentedTraitExpressionGetterConsumer67();
$grand = new ParentedTraitExpressionGetterGrand67();
$raw = (array) $consumer;
echo $raw === ['marker' => 700, 'value' => 100] ? 'C100/700|' : 'CBAD|';
$raw = (array) $grand;
echo $raw === ['marker' => 700, 'value' => 100] ? 'G100/700|' : 'GBAD|';
echo $consumer->value, '|';
echo $grand->value, '|';
echo $consumer->parentRead(), '|';
echo $grand->parentRead(), '|';
$grand->value = 300;
$raw = (array) $grand;
echo $raw === ['marker' => 700, 'value' => 300] ? 'G300/700|' : 'GBAD|';
echo $grand->value, '|';
echo $grand->parentRead(), '|';
