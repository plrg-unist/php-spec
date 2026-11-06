<?php
#[Deprecated]
const X = [];
class Typed208 {
    public function reject(int $value = X) { echo 'BAD|'; }
    public function __destruct() { echo 'D|'; }
}
function notice208($level, $message, $file, $line) {
    echo 'H|';
    return true;
}
$receiver208 = new Typed208;
set_error_handler('notice208');
try { $receiver208?->reject(); }
catch (TypeError $error) { echo 'T|'; }
try { $receiver208?->reject(); }
catch (TypeError $error) { echo 'T|'; }
restore_error_handler();
unset($error, $receiver208);
echo 'Z|';
