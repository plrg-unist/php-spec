<?php
function warn124($severity, $message, $file, $line) { echo 'bad-warning|'; return true; }
class ShadowParent124 {
    private int $ghost = 0;
    public function clearParent() { $receiver = $this; unset($receiver->ghost); }
    public function readParent() {
        return $this->ghost; // READ124
    }
    public function __destruct() { echo 'D|'; }
}
class ShadowChild124 extends ShadowParent124 {
    private string $ghost = 'hidden';
    public function readChild() { $receiver = $this; return $receiver->ghost; }
    public function __get($name) { echo 'G|'; return '7'; }
}
set_error_handler('warn124');
$child = new ShadowChild124();
$child->clearParent();
$other = new ShadowChild124();
$other->clearParent();
echo 'S:';
$inside = $child->readParent();
echo $inside === 7 ? 'int7|' : 'bad-inside|';
echo $child->readChild(), '|';
$outside = $child->ghost;
echo $outside === '7' ? 'raw7|' : 'bad-outside|';
unset($child, $other, $inside, $outside);
restore_error_handler();
echo 'E|';
