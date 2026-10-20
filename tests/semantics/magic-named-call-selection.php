<?php
class MagicNamedParent114 {
    public function __call(string $name, array $arguments) {
        echo 'C|', $name, '|', __CLASS__, '|', static::class, '|';
        foreach ($arguments as $key => $value) { echo $key, ':', $value, '|'; }
        unset($key, $value);
        echo 'c|';
        return $arguments[0];
    }
    public function __destruct() { echo 'D|'; }
}
class MagicNamedChild114 extends MagicNamedParent114 {}
function mutate114() {
    global $first, $child;
    echo 'M|';
    $first = 99;
    $child = null;
    return 2;
}
echo 'N:';
$first = 7;
$child = new MagicNamedChild114();
$result = $child->MiSs($first, name: mutate114());
echo 'A|', $result, '/', $first, '|';
echo 'E|';
