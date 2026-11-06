<?php
#[Deprecated]
const X = [];
class Source207 {
    public static function take($value = X) {
        echo 'B|', ($value === [] ? 'E|' : 'BAD|');
    }
    public function __destruct() { echo 'D|'; }
}
function notice207($level, $message, $file, $line) {
    echo 'H|';
    $GLOBALS['callback207'] = null;
    echo 'W|';
    return true;
}
$callback207 = [new Source207, 'take'];
set_error_handler('notice207');
$callback207();
echo 'R|';
Source207::take();
restore_error_handler();
echo 'Z|';
