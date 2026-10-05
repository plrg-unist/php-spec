<?php
set_error_handler(function () {
    echo 'H:', ini_get('precision'), '|';
    ini_set('precision', '1tail');
    return true;
});
ini_set('precision', '3tail');
eval(<<<'PHP'
$value = 'X';
$mixed = 12.3456789 . "${value}";
$parser = 12.3456789 . 'L';
echo 'M:', $mixed, '|P:', $parser, '|';
PHP);
echo 'END';
