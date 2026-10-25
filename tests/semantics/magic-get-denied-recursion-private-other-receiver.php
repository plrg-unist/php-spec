<?php
class OtherParent122 {
    public function __get($name) {
        global $first, $other;
        echo 'G|';
        if ($this === $first) {
            $receiver = $other;
            return $receiver->ghost; // READ122
        }
        return 9;
    }
}
class OtherChild122 extends OtherParent122 { private int $ghost = 0; }
$first = new OtherChild122();
$other = new OtherChild122();
echo 'O:';
$value = $first->ghost;
echo 'A|', $value, '|';
unset($first, $other, $value);
echo 'E|';
