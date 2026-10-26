<?php
function warn123($severity, $message, $file, $line) { echo 'bad-warning|'; return true; }
class PopulateParent123 {
    protected $ghost = 0;
    public function clearProtected() { $receiver = $this; unset($receiver->ghost); }
    public function writeProtected($value) { $receiver = $this; $receiver->ghost = $value; }
    public function readProtected() {
        $receiver = $this;
        return $receiver->ghost; // READ123
    }
    public function __destruct() { echo 'D|'; }
}
class PopulateChild123 extends PopulateParent123 {
    public function __get($name) { echo 'G|'; $this->writeProtected(99); return 'ok'; }
}
set_error_handler('warn123');
$child = new PopulateChild123();
$child->clearProtected();
echo 'T:';
$first = $child->readProtected();
echo $first === 'ok' ? 'ok|' : 'bad-first|';
echo $child->readProtected(), '|';
unset($child, $first);
restore_error_handler();
echo 'E|';
