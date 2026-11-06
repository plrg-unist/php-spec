<?php
#[Deprecated] const X = [];
class Local201 {
    function __destruct() {
        echo 'L|';
        $GLOBALS['member'] = 'other';
    }
}
function notice201() {
    echo 'H|';
    $GLOBALS['receiver'] = null;
    $local = new Local201;
    return true;
}
class Box201 {
    function run($value = X) {
        echo 'M|', ($value === [] ? 'E|' : 'BAD|');
    }
    function other() { echo 'BAD|'; }
    function __destruct() { echo 'D|'; }
}
$receiver = new Box201;
$member = 'run';
set_error_handler('notice201');
$receiver->$member();
echo 'R|';
echo $receiver === null ? 'G|' : 'BAD|';
echo $member === 'other' ? 'N|' : 'BAD|';
$next = new Box201;
$otherName = 'RUN';
$next->$otherName();
$next = null;
echo 'Z|';
