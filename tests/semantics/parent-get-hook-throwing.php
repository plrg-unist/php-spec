<?php
class ParentGetParent108 {
    public int $value {
        get {
            global $child, $error;
            echo 'P|';
            $child = null;
            throw $error;
        }
    }
    public function __destruct() { echo 'D|'; }
}
class ParentGetChild108 extends ParentGetParent108 {
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
$error = new Exception('supplied');
$child = new ParentGetGrand108();
$result = 42;
echo 'X:';
try { $result = $child->value; }
catch (Exception $caught) { echo $caught === $error ? 'C' : '!', '|'; }
echo $result, '|E|';
