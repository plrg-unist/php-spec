<?php
class MagicStaticParent100 {
    public static function __callStatic(string $name, array $arguments) {
        echo 'M|', $name, '|', __CLASS__, '|', static::class, '|', $arguments[0], '|', $arguments[1], '|m|';
        return $arguments[0];
    }
}
class MagicStaticChild100 extends MagicStaticParent100 {}
function mutateStaticCall100() {
    global $rhs;
    $rhs = 99;
    echo 'A|';
    return 2;
}
$rhs = 7;
$answer = 42;
echo 'N:';
$answer = MagicStaticChild100::MiSsInG($rhs, mutateStaticCall100());
echo 'R|', $answer, '|', $rhs, '|E|';
