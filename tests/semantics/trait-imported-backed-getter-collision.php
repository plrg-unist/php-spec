<?php
trait ImportedBackedCollisionTrait63 {
    public int $value = 100 {
        get {
            echo 'GET:', self::class, '/', static::class, '/', __METHOD__, '|';
            return $this->value + $this->answer();
        }
    }
}
class ImportedBackedCollisionConsumer63 {
    use ImportedBackedCollisionTrait63;
    public int $value = 100;
    private function answer(): int { return 13; }
}
