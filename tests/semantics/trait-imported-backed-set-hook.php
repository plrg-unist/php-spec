<?php
trait ImportedSetTrait74 {
    public int $value = 10 {
        set {
            echo 'SET:', self::class, '/', static::class, '/', __METHOD__, '/', __TRAIT__, '/', $value, '|';
            $this->value = $value + $this->offset();
        }
    }
}
class ImportedSetConsumer74 {
    use ImportedSetTrait74;
    private function offset(): int { return 13; }
}
class ImportedSetGrand74 extends ImportedSetConsumer74 {
    private function offset(): int { return 900; }
}
$grand = new ImportedSetGrand74();
$raw = (array) $grand;
echo 'I:', $raw['value'], '/', $grand->value, '|';
$result = ($grand->value = 20);
$raw = (array) $grand;
echo 'R:', $result, '/', $raw['value'], '/', $grand->value, '|';
try {
    $grand->value = [1];
} catch (TypeError $error) {
    echo 'TYPE:', $error->getMessage(), '|';
}
$raw = (array) $grand;
echo 'F:', $raw['value'], '/', $grand->value, '|';
