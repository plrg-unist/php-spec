<?php
class ParentSetParent109 {
    private int $secret = 41;
    public int $value {
        set {
            echo 'P|', __CLASS__, '|', static::class, '|';
            $this->secret = $value;
            echo $this->secret, '|';
        }
    }
    public function __destruct() { echo 'D', $this->secret, '|'; }
}
class ParentSetChild109 extends ParentSetParent109 {
    private int $secret = 99;
    public int $value {
        set {
            echo 'C|';
            $inner = parent::$value::set(mutate109());
            if ($inner === null) { echo 'Z|'; }
            echo $this->secret, '|', $value, '|A|';
        }
    }
}
class ParentSetGrand109 extends ParentSetChild109 {}
function mutate109() { global $child, $rhs; echo 'M|'; $child = null; $rhs = 99; return 7; }
$rhs = 7;
$child = new ParentSetGrand109();
$result = 42;
echo 'N:B|';
$result = ($child->value = 20);
echo $result, '|', $rhs, '|E|';
