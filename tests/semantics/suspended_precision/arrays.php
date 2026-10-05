<?php
$escaped = null;
set_error_handler(function () {
    global $escaped, $allocated;
    $escaped = beforeArray();
    $allocated = [9];
    echo 'H:', $escaped[0], '|';
    ini_set('precision', '1tail');
    return true;
});
ini_set('precision', '3tail');
eval(<<<'PHP'
function beforeArray() { return [(12.3456789 + 0) . 'L', [1]]; }
function arrayNotice($x) { return "${x}"; }
function afterArray() { return [(12.3456789 + 0) . 'L', [2]]; }
$after = afterArray();
echo 'B:', beforeArray()[0], '|A:', $after[0], '|';
PHP);
$escaped[1][0] = 7;
echo 'K:', $escaped[0], ':', $escaped[1][0], '|B:', beforeArray()[1][0], '|D:', $allocated[0], '|END';
