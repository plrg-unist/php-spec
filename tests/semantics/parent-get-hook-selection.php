<?php
class ParentGetParent108 {
    private int $secret = 41;
    public int $value {
        get {
            global $child;
            echo 'P|', __CLASS__, '|', static::class, '|';
            $child = null;
            return $this->secret;
        }
    }
    public function __destruct() { global $rhs; echo 'D|'; $rhs = 99; }
}
class ParentGetChild108 extends ParentGetParent108 {
    private int $secret = 99;
    public int $value {
        get {
            echo 'C|';
            $copy = parent::$value::get();
            echo 'A|';
            return $copy;
        }
    }
}
class ParentGetGrand108 extends ParentGetChild108 {}
$rhs = 7;
$child = new ParentGetGrand108();
$result = 42;
echo 'N:';
$result = $child->value;
echo $result, '|', $rhs, '|E|';
