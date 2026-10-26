<?php
function warn126($severity, $message, $file, $line) { echo 'bad-warning|'; return true; }
class PopulateParent126 {
    protected $ghost = 0;
    public function clear() { $receiver = $this; unset($receiver->ghost); }
    public static function readOwned() {
        return protectedFactory126()->ghost; // READ126
    }
    public function __destruct() { echo 'D', $this->ghost, '|'; }
}
class PopulateChild126 extends PopulateParent126 {
    public function __get($name) {
        echo 'G|';
        $receiver = $this;
        $receiver->ghost = 99;
        echo 'g|';
        return 'ok';
    }
}
function protectedFactory126() {
    $receiver = new PopulateChild126();
    $receiver->clear();
    return $receiver;
}
set_error_handler('warn126');
echo 'P:';
$result = PopulateParent126::readOwned();
echo $result === 'ok' ? 'ok|' : 'bad|';
unset($result);
restore_error_handler();
echo 'E|';
