<?php
function t() { echo 'T'; }
register_tick_function('t');
declare(ticks=1) {
    switch (defined('PHP_VERSION') + 1) { case 2: echo 'A'; }
    echo 'Z';
}
