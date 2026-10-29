<?php
$failure = new Exception("producer");
class ComputedEarlyReceiver123 {
    public function __destruct() { echo "D|receiver|"; }
    public function __invoke($item) { echo "BAD|"; }
}
function computedEarlyInput123() { global $failure; echo "P|"; throw $failure; }
try { (new ComputedEarlyReceiver123())(...computedEarlyInput123()); }
catch (Throwable $error) { echo "E|", (int)($error === $failure), "|"; }
echo "A|";
