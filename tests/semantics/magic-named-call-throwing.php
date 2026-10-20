<?php
class MagicNamedPayload114 {
    public function __destruct() { global $rhs, $error; echo 'V|'; $rhs = 99; throw $error; }
}
class MagicNamedOwner114 {
    public function __call(string $name, array $arguments) {
        global $child, $rhs;
        echo 'C|';
        $child = null;
        foreach ($arguments as $key => $value) { echo $key, '|'; }
        unset($key, $value);
        $cached = $rhs;
        unset($arguments);
        echo 'A|';
        return $cached;
    }
    public function __destruct() { echo 'D|'; }
}
echo 'X:';
$error = new Exception('chosen');
$rhs = 7;
$result = 42;
$child = new MagicNamedOwner114();
try {
    $result = $child->MiSs(second: new MagicNamedPayload114(), first: 7);
    echo 'R|';
} catch (Exception $caught) {
    if ($caught === $error) { echo 'C|'; }
    echo $result, '/', $rhs, '|';
} finally { echo 'F|'; }
echo 'E|';
