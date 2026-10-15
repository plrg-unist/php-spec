<?php
trait ImportedPairedHookTrait76 {
    public int $value = 10 {
        get {
            echo 'GET:', self::class, '/', static::class, '/', __METHOD__, '/', __TRAIT__, '|';
            $this->value = $this->value;
            return $this->value + $this->offset();
        }
        set {
            echo 'SET:', self::class, '/', static::class, '/', __METHOD__, '/', __TRAIT__, '/', $value, '/', $this->value, '|';
            $this->value = $value + $this->offset();
        }
    }
}
class ImportedPairedHookConsumer76 {
    use ImportedPairedHookTrait76;
    private function offset(): int { return 13; }
}
class ImportedPairedHookGrand76 extends ImportedPairedHookConsumer76 {
    private function offset(): int { return 900; }
}
$grand = new ImportedPairedHookGrand76();
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
