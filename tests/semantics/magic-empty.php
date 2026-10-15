<?php
class MagicEmptyParent83 {
    private int $skip = 11;
    private int $zero = 22;
    private int $full = 33;
    public int $ready = 0;
    public int $pending;
    public function __isset(string $name): bool {
        echo 'I:', $name, '/', self::class, '/', static::class, '/', __METHOD__, '|';
        return $name !== 'skip' && isset($this->zero);
    }
    public function __get($name) {
        echo 'G:', $name, '/', self::class, '/', static::class, '/', __METHOD__, '|';
        return $name === 'zero' ? 0 : $this->answer();
    }
    private function answer(): int { return 13; }
}
class MagicEmptyChild83 extends MagicEmptyParent83 {
    private function answer(): int { return 900; }
}
$child = new MagicEmptyChild83();
echo 'P:', empty($child->ready) ? 'T' : 'F', '/', empty($child->pending) ? 'T' : 'F', '|';
echo 'S:', empty($child->skip) ? 'T' : 'F', '|';
echo 'Z:', empty($child->zero) ? 'T' : 'F', '|';
echo 'F:', empty($child->full) ? 'T' : 'F', '|';
$raw = (array) $child;
echo 'R:', $raw === ["\0MagicEmptyParent83\0skip" => 11, "\0MagicEmptyParent83\0zero" => 22, "\0MagicEmptyParent83\0full" => 33, 'ready' => 0] ? 'ONLY' : 'BAD', '|';
