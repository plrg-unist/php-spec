<?php
class ClosurePayload96 {
    public function __destruct() {
        global $child, $weak;
        echo 'V|';
        echo $weak->get() === null ? 'K' : 'k', '|';
        $child = null;
        echo 'v|';
    }
}
class MagicClosureParent96 {
    private int $value = 1;
    public function __isset(string $name): bool {
        echo 'I|';
        return true;
    }
    public function __get($name) {
        global $weak, $alias;
        echo 'G|';
        $payload =& $alias;
        $payload = new ClosurePayload96();
        $closure = static function () use (&$payload) {};
        $weak = WeakReference::create($closure);
        return $closure;
    }
    public function __destruct() { echo 'D|'; }
}
class MagicClosureChild96 extends MagicClosureParent96 {}
$held = null;
$alias = null;
$weak = null;
$child = new MagicClosureChild96();
echo 'A:';
echo empty($child->value) ? 'T' : 'F', '|';
echo $weak->get() === null ? 'Z' : 'L', '|';
$held = null;
$alias = null;
$weak = null;
echo 'E|';
