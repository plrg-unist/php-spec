<?php
set_error_handler(function () {
    echo 'H:', ini_get('precision'), '|';
    ini_set('precision', '1tail');
    eval("echo 'N:', (12.3456789 + 0) . 'L', '|';");
    ini_set('precision', '2tail');
    return true;
});
ini_set('precision', '3tail');
eval(<<<'PHP'
function nestedNotice($x) { return "${x}"; }
$after = (12.3456789 + 0) . 'L';
$parser = 12.3456789 . 'L';
echo 'A:', $after, '|P:', $parser, '|';
PHP);
echo 'R:', ini_get('precision'), '|END';
