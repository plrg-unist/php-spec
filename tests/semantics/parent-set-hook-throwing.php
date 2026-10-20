<?php
class ParentSetParent109 {
    private int $secret = 41;
    public int $value {
        set {
            global $error;
            echo 'P|';
            $this->secret = $value;
            throw $error;
        }
    }
    public function __destruct() { echo 'D', $this->secret, '|'; }
}
class ParentSetChild109 extends ParentSetParent109 {
    public int $value {
        set { echo 'C|'; parent::$value::set(mutate109()); echo 'A|'; }
    }
}
class ParentSetGrand109 extends ParentSetChild109 {}
function mutate109() { global $child, $rhs; echo 'M|'; $child = null; $rhs = 99; return 7; }
$error = new Exception('supplied');
$rhs = 7;
$child = new ParentSetGrand109();
$result = 42;
echo 'X:B|';
try { $result = ($child->value = 20); }
catch (Exception $caught) { if ($caught === $error) { echo 'C|'; } }
echo $result, '|', $rhs, '|E|';
