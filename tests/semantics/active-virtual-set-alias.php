<?php
class VirtualAliasParent78 {
    public int $stored = 10;
    public int $value {
        set {
            echo 'SET:', self::class, '/', static::class, '/', __METHOD__, '/', $value, '|';
            $alias = $this;
            $alias->value = $value;
            $this->stored = $value + 13;
            echo 'AFTER|';
        }
    }
}
class VirtualAliasChild78 extends VirtualAliasParent78 {}
$child = new VirtualAliasChild78();
$raw = (array) $child;
echo 'I:', ($raw === ['stored' => 10] ? 'ONLY' : 'OTHER'), '/', $raw['value'] ?? 'ABSENT', '/', $child->stored, '|';
$result = 7;
try {
    $result = ($child->value = 20);
    echo 'RESULT:', $result, '|';
} catch (Error $error) {
    echo 'ERROR:', $error->getMessage(), '|';
}
$raw = (array) $child;
echo 'F:', ($raw === ['stored' => 10] ? 'ONLY' : 'OTHER'), '/', $raw['value'] ?? 'ABSENT', '/', $child->stored, '/', $result, '|';
