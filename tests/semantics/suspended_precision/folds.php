<?php
set_error_handler(function () {
    echo 'H:', ini_get('precision'), '|';
    ini_set('precision', '1tail');
    return true;
});
ini_set('precision', '3tail');
eval(<<<'PHP'
$suffix = 'X';
$before = (12.3456789 + 0) . 'L';
function foldNotice($x) { return "${x}"; }
$after = (12.3456789 + 0) . 'L';
$mixed = 12.3456789 . $suffix;
$parser = 12.3456789 . 'L';
echo 'B:', $before, '|A:', $after, '|M:', $mixed, '|P:', $parser, '|';
PHP);
echo 'R:', ini_get('precision'), '|END';
