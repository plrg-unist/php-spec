<?php
class ProtectedSetterParent79 {
    public protected(set) int $value = 10 {
        set {
            echo 'SET:', self::class, '/', static::class, '/', __METHOD__, '/', $value, '|';
            $this->value = $value + $this->offset();
        }
    }
    private function offset(): int { return 13; }
}
class ProtectedSetterChild79 extends ProtectedSetterParent79 {
    private function offset(): int { return 900; }
    public function write($input) {
        return $this->value = $input;
    }
}
$child = new ProtectedSetterChild79();
$raw = (array) $child;
echo 'I:', $raw['value'], '/', $child->value, '|';
$result = $child->write(20);
$raw = (array) $child;
echo 'R:', $result, '/', $raw['value'], '/', $child->value, '|';
try {
    $child->value = [1];
} catch (Error $error) {
    echo 'DENY:', $error->getMessage(), '|';
}
try {
    $child->write([1]);
} catch (TypeError $error) {
    echo 'TYPE:', $error->getMessage(), '|';
}
$raw = (array) $child;
echo 'F:', $raw['value'], '/', $child->value, '|';
