<?php
class MagicCallParent99 {
    private int $tag = 41;
    public function __call(string $name, array $arguments) {
        echo 'M|', $name, '|', $this->tag, '|', $arguments[0], '|', $arguments[1], '|m|';
        return $arguments[0];
    }
    public function __destruct() { echo 'D|'; }
}
class MagicCallChild99 extends MagicCallParent99 {}
function mutateCall99() {
    global $child, $rhs;
    $child = null;
    $rhs = 99;
    echo 'A|';
    return 2;
}
$rhs = 7;
$child = new MagicCallChild99();
$answer = 42;
echo 'N:';
$answer = $child->MiSsInG($rhs, mutateCall99());
echo 'R|', $answer, '|', $rhs, '|';
$child = null;
echo 'E|';
