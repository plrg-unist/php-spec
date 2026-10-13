<?php
trait ImportedExpressionGetterTrait65 {
    public int $value = 100 {
        get => $this->value + $this->answer(__METHOD__);
    }
}
class ImportedExpressionGetterConsumer65 {
    use ImportedExpressionGetterTrait65;
    private function answer(string $method): int {
        echo 'ANSWER:', self::class, '/', static::class, '/', $method, '|';
        return 13;
    }
}
class ImportedExpressionGetterGrand65 extends ImportedExpressionGetterConsumer65 {
    private function answer(string $method): int { return 900; }
}
$consumer = new ImportedExpressionGetterConsumer65();
$grand = new ImportedExpressionGetterGrand65();
$raw = (array) $consumer;
echo $raw === ['value' => 100] ? 'C100|' : 'CBAD|';
$raw = (array) $grand;
echo $raw === ['value' => 100] ? 'G100|' : 'GBAD|';
echo $consumer->value, '|';
echo $grand->value, '|';
$grand->value = 300;
$raw = (array) $grand;
echo $raw === ['value' => 300] ? 'G300|' : 'GBAD|';
echo $grand->value, '|';
