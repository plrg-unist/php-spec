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
        global $child;
        echo 'M|', $name, '|', $this->tag, '|';
        if (isset($arguments[0])) { echo 'A|'; }
        $child = null;
        echo 'm|';
        return 7;
    }
    public function __destruct() { echo 'D|'; }
}
class MagicCallChild99 extends MagicCallParent99 {}
$child = new MagicCallChild99();
$answer = 42;
echo 'O:';
$answer = $child->MiSsInG(new MagicCallPayload99());
echo 'R|', $answer, '|';
$child = null;
echo 'E|';
