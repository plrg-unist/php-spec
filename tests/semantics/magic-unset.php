<?php
class MagicUnsetParent81 {
    private int $hidden = 10;
    public int $seen = 0;
    public function __unset(string $name): void {
        echo 'U:', $name, '/', self::class, '/', static::class, '/', __METHOD__, '|';
        unset($this->hidden);
        $this->seen = $this->offset();
    }
    private function offset(): int { return 13; }
}
class MagicUnsetChild81 extends MagicUnsetParent81 {
    private function offset(): int { return 900; }
}
$child = new MagicUnsetChild81();
$raw = (array) $child;
echo 'I:', $raw["\0MagicUnsetParent81\0hidden"], '/', $raw['seen'], '|';
unset($child->seen);
$raw = (array) $child;
echo 'P:', $raw === ["\0MagicUnsetParent81\0hidden" => 10] ? 'ONLY' : 'BAD', '|';
unset($child->hidden);
$raw = (array) $child;
echo 'F:', $raw === ['seen' => 13] ? 'ONLY' : 'BAD', '/', $child->seen, '|';
