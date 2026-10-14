<?php
class BackedSetParent71 {
    public int $value = 10 {
        set {
            echo 'SET:', self::class, '/', static::class, '/', __METHOD__, '/', $value, '|';
            $this->value = $value + $this->offset();
        }
    }
    private function offset(): int { return 13; }
}
class BackedSetChild71 extends BackedSetParent71 {
    private function offset(): int { return 900; }
}
$child = new BackedSetChild71();
$raw = (array) $child;
echo 'I:', $raw['value'], '/', $child->value, '|';
$result = ($child->value = 20);
$raw = (array) $child;
echo 'R:', $result, '/', $raw['value'], '/', $child->value, '|';
try {
    $child->value = [1];
} catch (TypeError $error) {
    echo 'TYPE:', $error->getMessage(), '|';
}
$raw = (array) $child;
echo 'F:', $raw['value'], '/', $child->value, '|';
