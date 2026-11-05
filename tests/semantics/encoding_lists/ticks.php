<?php
declare(encoding=123, ticks=1);
function counter() { echo "T|"; }
register_tick_function('counter');
echo "A|";
unregister_tick_function('counter');
echo "Z|";
