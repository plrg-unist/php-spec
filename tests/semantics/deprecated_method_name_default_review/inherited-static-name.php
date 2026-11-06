<?php
#[Deprecated] const X = [];
function notice201() {
    echo 'H|';
    $GLOBALS['member'] = 'other';
    return true;
}
class Base201 {
    static function run($value = X) {
        echo static::class, '|', ($value === [] ? 'E|' : 'BAD|');
    }
    static function other() { echo 'BAD|'; }
}
class Child201 extends Base201 {}
class Other201 extends Base201 {}
$member = 'rUn';
set_error_handler('notice201');
Child201::$member();
echo $member === 'other' ? 'N|' : 'BAD|';
$member = 'RUN';
Other201::$member();
$member = 'run';
Base201::$member();
