<?php
#[Deprecated]
const X = [];

class RejectLoader204 {
    public function load($name, int $value = X) { echo "BAD|"; }
    public function __destruct() { echo "D|"; }
}
function notice204($number, $message, $file, $line) {
    echo "H|";
    return true;
}
set_error_handler('notice204');
$GLOBALS['loader204'] = new RejectLoader204;
spl_autoload_register([$GLOBALS['loader204'], 'load']);
try { new MissingType204; } catch (TypeError $error) { echo "T|"; }
try { spl_autoload_call('MissingType204'); } catch (TypeError $error) { echo "T|"; }
unset($error);
spl_autoload_unregister([$GLOBALS['loader204'], 'load']);
$GLOBALS['loader204'] = null;
echo "Z|";
