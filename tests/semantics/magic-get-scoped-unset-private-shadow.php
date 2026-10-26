<?php
function warn123($severity, $message, $file, $line) { echo 'bad-warning|'; return true; }
class ShadowParent123 {
    private int $ghost = 0;
    public function clearParent() { $receiver = $this; unset($receiver->ghost); }
    public function readParent() {
        $receiver = $this;
        return $receiver->ghost; // READ123
    }
    public function __destruct() { echo 'D|'; }
}
class ShadowChild123 extends ShadowParent123 {
    private string $ghost = 'hidden';
    public function readChild() { $receiver = $this; return $receiver->ghost; }
    public function __get($name) { echo 'G|'; return '7'; }
}
set_error_handler('warn123');
$child = new ShadowChild123();
$child->clearParent();
echo 'S:';
$inside = $child->readParent();
echo $inside === 7 ? 'int7|' : 'bad-inside|';
echo $child->readChild(), '|';
$outside = $child->ghost;
echo $outside === '7' ? 'raw7|' : 'bad-outside|';
unset($child, $inside, $outside);
restore_error_handler();
echo 'E|';
