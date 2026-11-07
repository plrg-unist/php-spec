<?php
namespace Ns219Private;
class Base219 {
    #[\Deprecated] private const SECRET = 7;
    #[\Deprecated] public const OPEN = 11;
    public static function get() { return self::SECRET; }
}
class Child219 extends Base219 {
    public static function bad() { return parent::SECRET; }
}
function notice219($level, $message) {
    echo 'H|';
    try { echo Base219::SECRET, '|BAD|'; }
    catch (\Error $error) { echo 'I|', $error->getMessage(), '|'; }
    return true;
}
\set_error_handler('Ns219Private\\notice219');
try { echo Base219::SECRET, '|BAD|'; }
catch (\Error $error) { echo 'C|', $error->getMessage(), '|'; }
echo 'V|', Base219::get(), '|';
try { echo Child219::bad(), '|BAD|'; }
catch (\Error $error) { echo 'K|', $error->getMessage(), '|'; }
try { echo Base219::SECRET, '|BAD|'; }
catch (\Error $error) { echo 'W|', $error->getMessage(), '|'; }
echo 'R|', Base219::get(), '|Z|';
