<?php
trait ImportedExplicitNarrowSetTrait75 {
    public int $value = 10 {
        set(string $incoming) {
            echo 'SET:', self::class, '/', static::class, '/', __METHOD__, '/', __TRAIT__, '/', $incoming, '|';
            $this->value = (int) $incoming + $this->offset();
        }
    }
}
class ImportedExplicitNarrowSetConsumer75 {
    use ImportedExplicitNarrowSetTrait75;
    private function offset(): int { return 13; }
}
class ImportedExplicitNarrowSetGrand75 extends ImportedExplicitNarrowSetConsumer75 {
    private function offset(): int { return 900; }
}
$grand = new ImportedExplicitNarrowSetGrand75();
$raw = (array) $grand;
echo 'I:', $raw['value'], '/', $grand->value, '|';
$result = ($grand->value = '20');
$raw = (array) $grand;
echo 'R:', ($result === '20' ? 'STRING' : 'OTHER'), '/', $result, '/', $raw['value'], '/', $grand->value, '|';
try {
    $grand->value = [1];
} catch (TypeError $error) {
    echo 'TYPE:', $error->getMessage(), '|';
}
$raw = (array) $grand;
echo 'F:', $raw['value'], '/', $grand->value, '|';
