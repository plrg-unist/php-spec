<?php
function warn126($severity, $message, $file, $line) { echo 'bad-warning|'; return true; }
class InitialOwner126 {
    private int $ghost;
    public static function readOwned() {
        return initialFactory126()->ghost; // READ126
    }
    public function __get($name) { echo 'bad-G|'; return 7; }
    public function __destruct() { echo 'D|'; }
}
function initialFactory126() { return new InitialOwner126(); }
set_error_handler('warn126');
$result = 42;
echo 'I:';
try { $result = InitialOwner126::readOwned(); echo 'bad|'; }
catch (Error $caught) {
    echo $caught->getMessage() === 'Typed property InitialOwner126::$ghost must not be accessed before initialization' ? 'initial|' : 'bad-message|';
    echo $caught->getLine() === 6 ? 'line|' : 'bad-line|';
    echo $caught->getFile() === __FILE__ ? 'file|' : 'bad-file|';
    echo $result, '|';
}
unset($result, $caught);
restore_error_handler();
echo 'E|';
