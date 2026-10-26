<?php
function warn126($severity, $message, $file, $line) { echo 'bad-warning|'; return true; }
class PrivateOwner126 {
    private int $ghost = 0;
    public function clear() { $receiver = $this; unset($receiver->ghost); }
    public static function readOwned() {
        return privateFactory126()->ghost; // READ126
    }
    public function __get($name) { echo 'G|'; return '7'; }
    public function __destruct() { echo 'D|'; }
}
function privateFactory126() {
    $receiver = new PrivateOwner126();
    $receiver->clear();
    return $receiver;
}
set_error_handler('warn126');
echo 'V:';
$result = PrivateOwner126::readOwned();
echo $result === 7 ? 'int7|' : 'bad|';
unset($result);
restore_error_handler();
echo 'E|';
