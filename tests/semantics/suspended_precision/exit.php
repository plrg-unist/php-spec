<?php
register_shutdown_function(function () {
    ini_restore('precision');
    echo 'Q:', ini_get('precision'), ':', ExitPublished::VALUE, '|';
});
set_error_handler(function () {
    echo 'H:', ini_get('precision'), '|';
    ini_set('precision', '1tail');
    exit(0);
});
ini_set('precision', '3tail');
eval(<<<'PHP'
function exitNotice($x) { return "${x}"; }
class ExitPublished { const VALUE = (12.3456789 + 0) . 'L'; }
echo 'BODY|';
PHP);
echo 'CALLER|';
