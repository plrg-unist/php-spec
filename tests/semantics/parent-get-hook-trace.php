<?php
class ParentGetParent108 {
    public object $value {
        get {
            global $child;
            $child = null;
            return new Exception('trace');
        }
    }
}
class ParentGetChild108 extends ParentGetParent108 {
    public object $value {
        get { return parent::$value::get(); }
    }
}
class ParentGetGrand108 extends ParentGetChild108 {}
$child = new ParentGetGrand108();
$error = $child->value;
$trace = $error->getTrace();
echo $trace[0]['function'], '|', $trace[0]['class'] ?? 'none', '|', $trace[0]['type'] ?? 'none', '|';
