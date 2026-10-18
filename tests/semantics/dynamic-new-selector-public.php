<?php
class Public103 {
    public int $mark = 0;
    public function __construct($number = 0) {
        global $made;
        $made++;
        $this->mark = $number;
        echo "C", $number, "|";
    }
    public function __destruct() {
        global $rhs;
        echo "D", $this->mark, "|";
        if ($this->mark === 0) { $rhs = 99; }
        echo "d|";
    }
}
function choose103() {
    global $original;
    $value = $original;
    $original = null;
    echo "S|";
    return $value;
}
function argument103() { global $rhs; echo "A|"; return $rhs; }
echo "P|";
$rhs = 7;
$made = 0;
$original = new Public103;
$answer = new (choose103())(argument103());
echo $answer->mark, "|", $made, "|";
$answer = null;
echo "Z|";
