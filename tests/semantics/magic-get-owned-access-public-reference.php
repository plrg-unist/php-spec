<?php
function warn126($severity, $message, $file, $line) { echo 'bad-warning|'; return true; }
class PublicOwner126 {
    public int $ghost = 0;
    public function clear() { $receiver = $this; unset($receiver->ghost); }
    public function &__get($name) { global $slot; echo 'G|'; return $slot; }
    public function __destruct() { global $slot; $slot = 9; echo 'D|'; }
}
function publicFactory126() {
    $receiver = new PublicOwner126();
    $receiver->clear();
    return $receiver;
}
set_error_handler('warn126');
$slot = 7;
echo 'R:';
$result = publicFactory126()->ghost; // READ126
echo $result, '|', $slot, '|';
unset($result, $slot);
restore_error_handler();
echo 'E|';
