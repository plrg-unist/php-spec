<?php
class ScopedPayload107 {
    public function __destruct() {
        global $rhs, $error;
        echo 'P|';
        throw $error;
    }
}
class ScopedParent107 {
    public function __call(string $name, array $arguments) {
        global $child, $rhs;
        echo 'I|', $name, '|';
        $child = null;
        return $rhs;
    }
    public static function __callStatic(string $name, array $arguments) {
        echo 'S|';
        return -1;
    }
    public function run() {
        echo 'B|';
        $value = self::MiSsInG(new ScopedPayload107());
        echo 'A|';
        return $value;
    }
    public function __destruct() { echo 'D|'; }
}
class ScopedChild107 extends ScopedParent107 {}
$error = new Exception('supplied');
$rhs = 7;
$child = new ScopedChild107();
$result = 42;
echo 'X:';
try {
    $result = $child->run();
} catch (Exception $caught) {
    echo $caught === $error ? 'C' : '!', '|';
}
echo $result, '|E|';
