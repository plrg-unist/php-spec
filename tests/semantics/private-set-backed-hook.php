<?php
class PrivateSetterParent80 {
    public private(set) int $value = 10 {
        set {
            echo 'SET:', self::class, '/', static::class, '/', __METHOD__, '/', $value, '|';
            $this->value = $value + $this->offset();
        }
    }
    private function offset(): int { return 13; }
    public function write($input) {
        return $this->value = $input;
    }
}
class PrivateSetterChild80 extends PrivateSetterParent80 {
    private function offset(): int { return 900; }
    public function denied($input) {
        return $this->value = $input;
    }
}
$child = new PrivateSetterChild80();
$raw = (array) $child;
echo 'I:', $raw['value'], '/', $child->value, '|';
$result = $child->write(20);
$raw = (array) $child;
echo 'R:', $result, '/', $raw['value'], '/', $child->value, '|';
try {
    $child->denied([1]);
} catch (Error $error) {
    echo 'CHILD:', $error->getMessage(), '|';
}
try {
    $child->value = [1];
} catch (Error $error) {
    echo 'GLOBAL:', $error->getMessage(), '|';
}
try {
    $child->write([1]);
} catch (TypeError $error) {
    echo 'TYPE:', $error->getMessage(), '|';
}
$raw = (array) $child;
echo 'F:', $raw['value'], '/', $child->value, '|';
