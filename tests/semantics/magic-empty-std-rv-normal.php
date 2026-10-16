<?php
class EmptyPayload88 {
    public function __destruct() {
        global $child;
        echo 'V|';
        $child = null;
        echo 'v|';
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
echo 'N:', empty($child->value) ? 'T' : 'F', '|';
echo 'E|';
