<?php
#[Deprecated]
const X = [];
class Static209 {
    public static function take($value = X) {
        echo 'B|', ($value === [] ? 'E|' : 'BAD|');
    }
    public function __destruct() { echo 'D|'; }
}
function notice209($level, $message, $file, $line) {
    echo 'H|';
    $GLOBALS['selector209'] = null;
    echo 'W|';
    return true;
}
$selector209 = new Static209;
set_error_handler('notice209');
$selector209::take();
echo 'R|';
Static209::take();
restore_error_handler();
echo 'Z|';
