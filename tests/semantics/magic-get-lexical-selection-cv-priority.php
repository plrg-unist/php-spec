<?php
function warn125($severity, $message, $file, $line) { echo 'bad-warning|'; return true; }
class ShadowParent125 {
    private int $ghost = 0;
    public function clearParent() { $receiver = $this; unset($receiver->ghost); }
    public function readParent() {
        $receiver = $this;
        return $receiver->ghost; // READ125
    }
    public function __destruct() { echo 'D|'; }
}
class ShadowChild125 extends ShadowParent125 {
    public string $ghost = 'hidden';
    public function readChild() { $receiver = $this; return $receiver->ghost; }
    public function __get($name) { echo 'G|'; return '7'; }
}
set_error_handler('warn125');
$child = new ShadowChild125();
$child->clearParent();
echo 'C:';
$inside = $child->readParent();
echo $inside === 7 ? 'int7|' : 'bad-inside|';
echo $child->readChild(), '|';
$outside = $child->ghost;
echo $outside === 'hidden' ? 'public|' : 'bad-outside|';
unset($child, $inside, $outside);
restore_error_handler();
echo 'E|';
