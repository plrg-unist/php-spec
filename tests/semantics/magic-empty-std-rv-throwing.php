<?php
class EmptyPayload88 {
    public function __destruct() {
        global $child;
        echo 'V|';
        $child = null;
        echo 'v|';
        throw new Exception('std-rv-stop');
    }
}
class MagicObjectParent88 {
    private int $value = 1;
    public function __isset(string $name): bool {
        echo 'I|';
        return true;
    }
    public function __get($name) {
        echo 'G|';
        $box = new stdClass();
        $box->payload = new EmptyPayload88();
        return $box;
    }
    public function __destruct() { echo 'D|'; }
}
class MagicObjectChild88 extends MagicObjectParent88 {}
$child = new MagicObjectChild88();
echo 'X:';
try { echo empty($child->value) ? 'T' : 'F', '|'; }
catch (Exception $caught) { echo 'C|'; }
echo 'E|';
