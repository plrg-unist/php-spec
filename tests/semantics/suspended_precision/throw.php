<?php
set_error_handler(function () {
    echo 'H:', ini_get('precision'), '|';
    ini_set('precision', '1tail');
    throw new Exception('stop');
});
ini_set('precision', '3tail');
try {
    eval(<<<'PHP'
function throwFirst($x) { return "${x}"; }
function throwFold() { return (12.3456789 + 0) . 'L'; }
function throwSecond($x) { return "${x}"; }
class ThrowPublished { const MARK = 'C'; }
echo 'BODY|';
PHP);
} catch (Exception $error) { echo 'E:', $error->getMessage(), '|'; }
echo 'F:', throwFold(), '|C:', ThrowPublished::MARK, '|R:', ini_get('precision'), '|END';
