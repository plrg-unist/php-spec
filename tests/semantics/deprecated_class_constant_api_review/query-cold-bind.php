<?php
\define('SEED_QUERY213', 7);
class QueryAPI213 {
    #[\Deprecated]
    public const VALUE = SEED_QUERY213;
}
class AliasQueryAPI213 extends QueryAPI213 {}
class OtherQueryAPI213 {
    public const VALUE = 9;
}
function noticeQueryAPI213($level, $message, $file, $line) {
    echo 'H|';
    unset($GLOBALS['query213']);
    $GLOBALS['query213'] = 'OtherQueryAPI213::VALUE';
    echo 'W|';
    return true;
}
$prefix213 = 'AliasQueryAPI213';
$query213 = $prefix213 . '::VALUE';
unset($prefix213);
set_error_handler('noticeQueryAPI213');
echo \constant($query213), '|';
echo 'R|';
$query213 = 'AliasQueryAPI213::VALUE';
echo \constant($query213), '|';
restore_error_handler();
unset($query213);
echo 'Z|';
