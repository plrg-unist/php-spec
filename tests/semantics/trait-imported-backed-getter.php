<?php
trait ImportedBackedGetterTrait63 {
    public int $value = 100 {
        get {
            echo 'GET:', self::class, '/', static::class, '/', __METHOD__, '|';
            return $this->value + $this->answer();
        }
    }
}
class ImportedBackedGetterConsumer63 {
    use ImportedBackedGetterTrait63;
    private function answer(): int { return 13; }
    public function consumerRead(): int {
        echo 'READ:', self::class, '/', static::class, '|';
        return $this->value;
    }
}
class ImportedBackedGetterGrand63 extends ImportedBackedGetterConsumer63 {
    private function answer(): int { return 900; }
}
$consumer = new ImportedBackedGetterConsumer63();
$grand = new ImportedBackedGetterGrand63();
$raw = (array) $consumer;
echo 'C', $raw['value'], '|';
$raw = (array) $grand;
echo 'G', $raw['value'], '|';
echo $consumer->value, '|';
echo $grand->value, '|';
echo $grand->consumerRead(), '|';
$grand->value = 300;
$raw = (array) $grand;
echo 'G', $raw['value'], '|';
echo $grand->value, '|';
