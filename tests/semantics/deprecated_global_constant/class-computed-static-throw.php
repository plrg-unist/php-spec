<?php
namespace {
class Drop195 { function __destruct() { echo 'D|'; throw new \Exception('old'); } }
#[Deprecated] const X = [];
function notice195() {
    echo 'H|'; define('Ns195\\X', 9);
    $copy = \Ns195\Cache195::VALUE; $copy[0](); $copy = null;
    return true;
}
}
namespace Ns195 {
class Cache195 { const VALUE = [static function () { static $held = new \Drop195(); echo 'F|'; }, X]; }
set_error_handler('notice195');
try { echo Cache195::VALUE[1] === [] ? 'E|' : 'BAD|'; } catch (\Exception $error) { echo 'K|'; }
echo Cache195::VALUE[1] === [] ? 'E|' : 'BAD|';
}
