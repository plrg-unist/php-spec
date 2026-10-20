<?php
class ScopedParent107 {
    public function __call(string $name, array $arguments) {
        echo 'I|', $name, '|', $arguments[0], '|', $arguments[1], '|', __CLASS__, '|', static::class, '|';
        return 7;
    }
    public static function __callStatic(string $name, array $arguments) {
        echo 'S|';
        return -1;
    }
    public function run($first) {
        echo 'B|';
        $value = self::MiSsInG($first, mutate107());
        echo 'A|';
        return $value;
    }
    public function __destruct() { echo 'D|'; }
}
class ScopedChild107 extends ScopedParent107 {}
function mutate107() {
    global $child, $rhs;
    echo 'M|';
    $rhs = 99;
    $child = null;
    return 2;
}
$rhs = 7;
$child = new ScopedChild107();
$result = 42;
echo 'N:';
$result = $child->run($rhs);
echo $result, '|', $rhs, '|E|';
