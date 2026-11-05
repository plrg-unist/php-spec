<?php
function t() { echo 'T'; }
register_tick_function('t');
declare(ticks=1) {
    switch (defined('PHP_VERSION')) { case true: echo 'A'; }
    echo 'Z';
}
