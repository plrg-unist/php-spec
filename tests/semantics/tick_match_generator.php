<?php
function tick() { echo 'T'; }
declare(ticks=0) {
    function values() {
        yield match (0) {
            0 => 'V',
            default => (static function () { declare(ticks=1); return 'X'; })(),
        };
        echo 'G';
    }
}
register_tick_function('tick');
$generator = values();
echo 'I';
echo $generator->current(), '|';
$generator->next();
unregister_tick_function('tick');
echo 'Z';
