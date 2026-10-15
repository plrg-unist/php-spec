<?php
class MagicIssetParent82 {
    private int $hidden = 10;
    private int $other = 0;
    public int $ready = 0;
    public int $pending;
    public function __isset(string $name): bool {
        echo 'I:', $name, '/', self::class, '/', static::class, '/', __METHOD__, '|';
        return $name === 'hidden' && isset($this->hidden) && $this->answer();
    }
    private function answer(): bool { return true; }
}
class MagicIssetChild82 extends MagicIssetParent82 {
    private function answer(): bool { return false; }
}
$child = new MagicIssetChild82();
echo 'P:', isset($child->ready) ? 'T' : 'F', '/', isset($child->pending) ? 'T' : 'F', '|';
echo 'H:', isset($child->hidden) ? 'T' : 'F', '|';
echo 'O:', isset($child->other, $child->hidden) ? 'T' : 'F', '|';
$raw = (array) $child;
echo 'F:', $raw === ["\0MagicIssetParent82\0hidden" => 10, "\0MagicIssetParent82\0other" => 0, 'ready' => 0] ? 'ONLY' : 'BAD', '|';
