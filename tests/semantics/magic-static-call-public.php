<?php
class MagicStaticParent100 {
    public static function __callStatic(string $name, array $arguments) {
        throw new Exception('magic-static-must-not-run');
    }
    public static function direct($incoming) {
        echo 'B|', $incoming, '|', __CLASS__, '|', static::class, '|b|';
        return 17;
    }
}
class MagicStaticChild100 extends MagicStaticParent100 {}
$answer = 42;
echo 'B:';
$answer = MagicStaticChild100::direct(7);
echo 'R|', $answer, '|E|';
