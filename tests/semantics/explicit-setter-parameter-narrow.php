<?php
class NarrowSetParent73 {
    public int $value = 10 {
        set(string $incoming) {
            echo 'SET:', self::class, '/', static::class, '/', __METHOD__, '/', $incoming, '|';
            $this->value = (int) $incoming + $this->offset();
        }
    }
    private function offset(): int { return 13; }
}
class NarrowSetChild73 extends NarrowSetParent73 {
    private function offset(): int { return 900; }
}
$child = new NarrowSetChild73();
$raw = (array) $child;
echo 'I:', $raw['value'], '/', $child->value, '|';
$result = ($child->value = '20');
$raw = (array) $child;
echo 'R:', ($result === '20' ? 'STRING' : 'OTHER'), '/', $result, '/', $raw['value'], '/', $child->value, '|';
try {
    $child->value = [1];
} catch (TypeError $error) {
    echo 'TYPE:', $error->getMessage(), '|';
}
$raw = (array) $child;
echo 'F:', $raw['value'], '/', $child->value, '|';
