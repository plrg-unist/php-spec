<?php
class MagicCallPayload99 {
    public function __destruct() {
        global $child;
        echo 'P|';
        if ($child === null) { echo 'K|'; } else { echo 'Q|'; }
        echo 'p|';
    }
}
class MagicCallParent99 {
    private int $tag = 41;
    public function __call(string $name, array $arguments) {
        global $child, $error;
        echo 'M|', $name, '|', $this->tag, '|';
        if (isset($arguments[0])) { echo 'A|'; }
        $child = null;
        echo 'm|';
        throw $error;
    }
    public function __destruct() { echo 'D|'; }
}
class MagicCallChild99 extends MagicCallParent99 {}
$error = new Exception('magic-call-stop');
$child = new MagicCallChild99();
$answer = 42;
echo 'X:';
try { $answer = $child->MiSsInG(new MagicCallPayload99()); }
catch (Exception $caught) {
    echo 'C|', $answer, '|';
    if ($caught === $error) { echo 'T|'; } else { echo 'F|'; }
}
$child = null;
echo 'E|';
