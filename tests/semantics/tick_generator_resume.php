<?php
$count = 0;
function tick() {
    global $count;
    echo 'T', ++$count, ';';
}
function values() {
    declare(ticks=1) {
        echo 'A;';
        yield 1;
        echo 'B;';
        yield from [2, 3];
        echo 'C;';
    }
}
register_tick_function('tick');
$generator = values();
echo 'S;';
foreach ($generator as $value) {
    echo $value, ';';
}
unregister_tick_function('tick');
echo 'Z', $count, ';';
