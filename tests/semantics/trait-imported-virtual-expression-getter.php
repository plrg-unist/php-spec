<?php
trait ImportedVirtualExpressionGetterTrait66 {
    public int $value {
        get => $this->answer(__METHOD__);
    }
}
class ImportedVirtualExpressionGetterConsumer66 {
    use ImportedVirtualExpressionGetterTrait66;
    private function answer(string $method): int {
        echo 'ANSWER:', self::class, '/', static::class, '/', $method, '|';
        return 13;
    }
}
class ImportedVirtualExpressionGetterGrand66 extends ImportedVirtualExpressionGetterConsumer66 {
    private function answer(string $method): int { return 900; }
}
$consumer = new ImportedVirtualExpressionGetterConsumer66();
$grand = new ImportedVirtualExpressionGetterGrand66();
$raw = (array) $consumer;
echo $raw === [] ? 'CEMPTY|' : ($raw === ['value' => null] ? 'CNULL|' : 'CBAD|');
$raw = (array) $grand;
echo $raw === [] ? 'GEMPTY|' : ($raw === ['value' => null] ? 'GNULL|' : 'GBAD|');
echo $consumer->value, '|';
echo $grand->value, '|';
try {
    $grand->value = 300;
    echo 'WRITE|';
} catch (Error $error) {
    echo 'ERR:', $error->getMessage(), '|';
}
$raw = (array) $grand;
echo $raw === [] ? 'GEMPTY|' : ($raw === ['value' => null] ? 'GNULL|' : 'GBAD|');
echo $grand->value, '|';
