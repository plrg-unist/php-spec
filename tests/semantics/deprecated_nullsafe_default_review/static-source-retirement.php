<?php
#[Deprecated]
const X = [];
class Static208 {
    public static function take($value = X) {
        echo 'B|', ($value === [] ? 'E|' : 'BAD|');
    }
    public function __destruct() { echo 'D|'; }
}
function notice208($level, $message, $file, $line) {
    echo 'H|';
    $GLOBALS['receiver208'] = null;
    echo 'W|';
    return true;
}
$receiver208 = new Static208;
set_error_handler('notice208');
$receiver208?->take();
echo 'R|';
Static208::take();
restore_error_handler();
echo 'Z|';
