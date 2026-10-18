<?php
class Private103 {
    private function __construct() { echo "B|"; }
    public static function make() { return new self; }
    public function __destruct() {
        global $rhs, $throws, $error;
        echo "D|";
        $rhs = 99;
        if ($throws) { throw $error; }
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
function argument103() { echo "A|"; return 7; }
echo "H|";
$error = new Exception("supplied");
$rhs = 7;
$throws = true;
$original = Private103::make();
$held = $original;
$answer = 42;
try { $answer = new (choose103())(argument103()); }
catch (Error $caught) { echo "E|"; }
echo "F|";
try { $held = null; }
catch (Throwable $caught) {
    echo $caught === $error ? "C|" : "W|";
    echo $caught->getPrevious() === null ? "P|" : "Q|";
}
echo $answer, "|", $rhs, "|Z|";
