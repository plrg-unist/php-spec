<?php
class MagicNamedPayload114 {
    public function __destruct() { global $rhs; echo 'V|'; $rhs = 99; }
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
echo 'O:';
$rhs = 7;
$child = new MagicNamedOwner114();
$result = $child->MiSs(second: new MagicNamedPayload114(), first: 7);
echo 'R|', $result, '/', $rhs, '|';
echo 'E|';
