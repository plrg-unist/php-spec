<?php
namespace Ns222Select;
class Base222 {
    #[\Deprecated]
    public const A = 7, B = 9;
}
class Child222 extends Base222 {}
function notice222($level, $message) {
    echo $message, '|', $level, '|';
    if ($GLOBALS['inside222']) {
        $GLOBALS['inside222'] = false;
        $inside = 'A';
        echo 'I|', Child222::{$inside}, '|';
    }
    $GLOBALS['member222'] = 'B';
    return true;
}
\set_error_handler('Ns222Select\\notice222');
$inside222 = true;
$member222 = 'A';
echo Child222::{$member222}, '|';
echo Child222::{$member222}, '|';
echo Base222::A, '|Z|';
