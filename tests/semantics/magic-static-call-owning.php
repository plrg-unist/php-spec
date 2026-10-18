<?php
class MagicStaticPayload100 {
    public function __destruct() {
        global $value;
        echo 'P|';
        $value = 99;
        echo 'p|';
    }
}
class MagicStaticParent100 {
    public static function __callStatic(string $name, array $arguments) {
        global $value;
        echo 'M|', $name, '|', __CLASS__, '|', static::class, '|';
        if (isset($arguments[0])) { echo 'A|'; }
        echo 'm|';
        return $value;
    }
}
class MagicStaticChild100 extends MagicStaticParent100 {}
$value = 7;
$answer = 42;
echo 'O:';
$answer = MagicStaticChild100::MiSsInG(new MagicStaticPayload100());
echo 'R|', $answer, '|', $value, '|E|';
