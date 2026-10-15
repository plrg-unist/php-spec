<?php
class VirtualSetParent77 {
    public int $stored = 10;
    public int $value {
        set {
            echo 'SET:', self::class, '/', static::class, '/', __METHOD__, '/', $value, '|';
            $this->stored = $value + $this->offset();
        }
    }
    private function offset(): int { return 13; }
}
class VirtualSetChild77 extends VirtualSetParent77 {
    private function offset(): int { return 900; }
}
$child = new VirtualSetChild77();
$raw = (array) $child;
echo 'I:', ($raw === ['stored' => 10] ? 'ONLY' : 'OTHER'), '/', $raw['value'] ?? 'ABSENT', '/', $raw['stored'], '|';
$result = ($child->value = 20);
$raw = (array) $child;
echo 'R:', $result, '/', ($raw === ['stored' => 33] ? 'ONLY' : 'OTHER'), '/', $raw['value'] ?? 'ABSENT', '/', $raw['stored'], '/', $child->stored, '|';
try {
    $read = $child->value;
    echo 'VALUE:', $read, '|';
} catch (Error $error) {
    echo 'READ:', $error->getMessage(), '|';
}
try {
    $child->value = [1];
} catch (TypeError $error) {
    echo 'TYPE:', $error->getMessage(), '|';
}
$raw = (array) $child;
echo 'F:', ($raw === ['stored' => 33] ? 'ONLY' : 'OTHER'), '/', $raw['value'] ?? 'ABSENT', '/', $raw['stored'], '/', $child->stored, '|';
