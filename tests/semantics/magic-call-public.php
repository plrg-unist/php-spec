<?php
class MagicCallParent99 {
    public function __call(string $name, array $arguments) {
        throw new Exception('magic-must-not-run');
    }
    public function direct($incoming) {
        global $child;
        echo 'B|', $incoming, '|';
        $child = null;
        echo 'b|';
        return 17;
    }
    public function __destruct() { echo 'D|'; }
}
class MagicCallChild99 extends MagicCallParent99 {}
$child = new MagicCallChild99();
$answer = 42;
echo 'B:';
$answer = $child->direct(7);
echo 'R|', $answer, '|';
$child = null;
echo 'E|';
