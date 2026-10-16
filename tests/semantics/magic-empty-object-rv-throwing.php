<?php
class EmptyPayload87 {
    public function __destruct() {
        global $child;
        echo 'V|';
        $child = null;
        echo 'v|';
        throw new Exception('rv-stop');
    }
}
class MagicObjectParent87 {
    private int $value = 1;
    public function __isset(string $name): bool {
        echo 'I|';
        return true;
    }
    public function __get($name) {
        echo 'G|';
        return new EmptyPayload87();
    }
    public function __destruct() { echo 'D|'; }
}
class MagicObjectChild87 extends MagicObjectParent87 {}
$child = new MagicObjectChild87();
echo 'X:';
try { echo empty($child->value) ? 'T' : 'F', '|'; }
catch (Exception $caught) { echo 'C|'; }
echo 'E|';
