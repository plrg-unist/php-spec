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
        global $error;
        echo 'M|', $name, '|', __CLASS__, '|', static::class, '|';
        if (isset($arguments[0])) { echo 'A|'; }
        echo 'm|';
        throw $error;
    }
}
class MagicStaticChild100 extends MagicStaticParent100 {}
$error = new Exception('magic-static-stop');
$value = 7;
$answer = 42;
echo 'X:';
try { $answer = MagicStaticChild100::MiSsInG(new MagicStaticPayload100()); }
catch (Exception $caught) {
    echo 'C|', $answer, '|';
    if ($caught === $error) { echo 'T|'; } else { echo 'F|'; }
}
echo $value, '|E|';
