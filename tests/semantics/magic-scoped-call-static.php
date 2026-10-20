<?php
class ScopedParent107 {
    public function __call(string $name, array $arguments) {
        echo 'I|';
        return -1;
    }
    public static function __callStatic(string $name, array $arguments) {
        echo 'S|', $name, '|', $arguments[0], '|', __CLASS__, '|', static::class, '|';
        return 9;
    }
}
class ScopedChild107 extends ScopedParent107 {}
echo 'C:';
$result = ScopedChild107::MiSsInG(7);
echo $result, '|E|';
