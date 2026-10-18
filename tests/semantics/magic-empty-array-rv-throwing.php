<?php
class EmptyPayload89 {
    public function __destruct() {
        global $child;
        echo 'V|';
        $child = null;
        echo 'v|';
        throw new Exception('array-rv-stop');
    }
}
class MagicObjectParent89 {
    private int $value = 1;
    public function __isset(string $name): bool {
        echo 'I|';
        return true;
    }
    public function __get($name) {
        echo 'G|';
        return [new EmptyPayload89()];
    }
    public function __destruct() { echo 'D|'; }
}
class MagicObjectChild89 extends MagicObjectParent89 {}
$child = new MagicObjectChild89();
echo 'X:';
try { echo empty($child->value) ? 'T' : 'F', '|'; }
catch (Exception $caught) { echo 'C|'; }
echo 'E|';
