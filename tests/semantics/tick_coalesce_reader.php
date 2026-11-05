<?php
function t() { echo 'T'; }
register_tick_function('t');
set_error_handler(static function ($n, $m) { echo 'H'; return true; });
$values = [];
declare(ticks=0) {
    $values[(static function () { declare(ticks=2); echo 'K'; return 'k'; })()] ??= (static function () { declare(ticks=3); echo 'R'; return 9; })();
    echo $values['k'];
    echo 'Z';
    echo 'W';
}
