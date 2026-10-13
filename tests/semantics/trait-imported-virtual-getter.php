<?php
trait ImportedVirtualGetterTrait64 {
    public int $value {
        get {
            echo 'GET:', self::class, '/', static::class, '/', __METHOD__, '|';
            return $this->answer();
        }
    }
}
class ImportedVirtualGetterConsumer64 {
    use ImportedVirtualGetterTrait64;
    private function answer(): int { return 13; }
}
class ImportedVirtualGetterGrand64 extends ImportedVirtualGetterConsumer64 {
    private function answer(): int { return 900; }
}
$consumer = new ImportedVirtualGetterConsumer64();
$grand = new ImportedVirtualGetterGrand64();
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
