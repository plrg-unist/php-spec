<?php
function tick() { echo 'T'; }
register_tick_function('tick');
try {
    declare(ticks=1) {
        switch (match (0) {}) {
            default: echo 'BAD';
        }
    }
} catch (UnhandledMatchError $error) {
    echo 'U';
}
unregister_tick_function('tick');
echo 'Z';
