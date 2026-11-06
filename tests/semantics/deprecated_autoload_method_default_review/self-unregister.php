<?php
#[Deprecated]
const X = [];

class Loader204 {
    public function load($name, $value = X) {
        echo "B|";
        if ($value === []) { echo "E|"; }
        class Wanted204 {}
    }
    public function __destruct() { echo "D|"; }
}
function warning204($number, $message, $file, $line) {
    echo "H|";
    spl_autoload_unregister([$GLOBALS['loader204'], 'load']);
    $GLOBALS['loader204'] = null;
    echo "W|";
    return true;
}
set_error_handler('warning204');
$GLOBALS['loader204'] = new Loader204;
spl_autoload_register([$GLOBALS['loader204'], 'load']);
new Wanted204;
echo "Z|";
