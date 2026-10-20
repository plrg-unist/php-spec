<?php
class ParentSetParent109 {
    private int $secret = 41;
    public int $value {
        set { echo 'P|'; $this->secret = $value; }
    }
    public function __destruct() { echo 'D', $this->secret, '|'; }
}
class ParentSetChild109 extends ParentSetParent109 {
    public int $value {
        set { echo 'C|'; parent::$value::set(mutate109()); echo 'A|'; }
    }
}
class ParentSetGrand109 extends ParentSetChild109 {}
function mutate109() { global $child, $rhs; echo 'M|'; $child = null; $rhs = 99; return ['bad']; }
$rhs = 7;
$child = new ParentSetGrand109();
$result = 42;
echo 'T:B|';
try { $result = ($child->value = 20); }
catch (TypeError $caught) {
    echo 'C|';
    $trace = $caught->getTrace();
    $frame = $trace[0];
    echo $frame['function'], '|', $frame['class'] ?? 'none', '|', $frame['type'] ?? 'none', '|';
}
echo $result, '|', $rhs, '|E|';
