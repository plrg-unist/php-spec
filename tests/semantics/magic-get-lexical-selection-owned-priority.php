<?php
function warn125($severity, $message, $file, $line) { echo 'bad-warning|'; return true; }
class OwnedParent125 {
    private int $ghost = 0;
    public function clearParent() { $receiver = $this; unset($receiver->ghost); }
    public static function readOwned() {
        return factory125()->ghost; // READ125
    }
    public function __destruct() { echo 'D|'; }
}
class OwnedChild125 extends OwnedParent125 {
    public string $ghost = 'hidden';
    public function __get($name) { echo 'G|'; return '7'; }
}
function factory125() {
    $receiver = new OwnedChild125();
    $receiver->clearParent();
    return $receiver;
}
set_error_handler('warn125');
echo 'F:';
$inside = OwnedParent125::readOwned();
echo $inside === 7 ? 'int7|' : 'bad-inside|';
$child = new OwnedChild125();
echo $child->ghost === 'hidden' ? 'public|' : 'bad-public|';
unset($child, $inside);
restore_error_handler();
echo 'E|';
