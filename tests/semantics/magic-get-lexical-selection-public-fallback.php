<?php
function warn125($severity, $message, $file, $line) { echo 'bad-warning|'; return true; }
class FallbackParent125 {
    public function clear() { $receiver = $this; unset($receiver->ghost); }
    public function readParent() {
        $receiver = $this;
        return $receiver->ghost; // READ125
    }
    public function __destruct() { echo 'D|'; }
}
class FallbackChild125 extends FallbackParent125 {
    public string $ghost = 'hidden';
    public function __get($name) { echo 'G|'; return 7; }
}
set_error_handler('warn125');
$child = new FallbackChild125();
$child->clear();
echo 'P:';
$result = $child->readParent();
echo $result === '7' ? 'string7|' : 'bad|';
unset($child, $result);
restore_error_handler();
echo 'E|';
