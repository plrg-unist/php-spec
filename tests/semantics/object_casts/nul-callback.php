<?php
$object = (object)["\0bad" => 'first', 'tail' => 'old'];
set_error_handler(function($level, $message, $file, $line) use (&$object) {
    echo 'H:', $level, ':', $message, ':', $line, '|';
    $object->tail = 'changed';
    $object->late = 'added';
    return true;
});
foreach ($object as $key => $value) {
    echo ($key === "\0bad" ? 'nul' : $key), ':', $value, '|';
}
restore_error_handler();
echo $object->tail, ':', $object->late, '|END';
