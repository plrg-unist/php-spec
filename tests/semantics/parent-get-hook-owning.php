<?php
class ParentGetPayload108 {
    public function __destruct() { echo 'V|'; }
}
class ParentGetParent108 {
    public object $value {
        get {
            global $child;
            echo 'P|';
            $child = null;
            return new ParentGetPayload108();
        }
    }
    public function __destruct() { echo 'D|'; }
}
class ParentGetChild108 extends ParentGetParent108 {
    public object $value {
        get {
            echo 'C|';
            $copy = parent::$value::get();
            echo 'A|';
            return $copy;
        }
    }
}
class ParentGetGrand108 extends ParentGetChild108 {}
$child = new ParentGetGrand108();
$result = 42;
echo 'O:';
$result = $child->value;
echo 'M|';
unset($result);
echo 'E|';
