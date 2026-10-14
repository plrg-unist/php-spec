<?php
class PairedHookParent72 {
    public int $value = 10 {
        get {
            echo 'GET:', self::class, '/', static::class, '/', __METHOD__, '|';
            $this->value = $this->value;
            return $this->value + $this->offset();
        }
        set {
            echo 'SET:', self::class, '/', static::class, '/', __METHOD__, '/', $value, '/', $this->value, '|';
            $this->value = $value + $this->offset();
        }
    }
    private function offset(): int { return 13; }
}
class PairedHookChild72 extends PairedHookParent72 {
    private function offset(): int { return 900; }
}
$child = new PairedHookChild72();
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
