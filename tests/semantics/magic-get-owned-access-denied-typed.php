<?php
function warn126($severity, $message, $file, $line) { echo 'bad-warning|'; return true; }
class DeniedOwner126 {
    private int $ghost;
    public function __get($name) { echo 'G|'; return 'ok'; }
    public function __destruct() { echo 'D|'; }
}
function deniedFactory126() { return new DeniedOwner126(); }
set_error_handler('warn126');
echo 'X:';
$result = deniedFactory126()->ghost; // READ126
echo $result === 'ok' ? 'rawok|' : 'bad|';
unset($result);
restore_error_handler();
echo 'E|';
